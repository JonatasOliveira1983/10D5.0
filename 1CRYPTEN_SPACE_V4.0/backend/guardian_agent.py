import asyncio
import os
import sys
import time
from datetime import datetime
from services.sovereign_service import sovereign_service
from services.bybit_rest import bybit_rest_service
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | GUARDIAN - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/guardian.log") if os.path.exists("logs") else logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Guardian")

class GuardianAgent:
    def __init__(self):
        self.btc_price_history = []  # Para armazenar [timestamp, price]
        self.check_interval = 15  # a cada 15 segundos verifica
        
        # Target definitions -> Se BTC se mover X% em Y minutos
        self.macro_window_minutes = 5
        self.macro_threshold_percent = 1.0  # 1% de salto/queda em 5 minutos = TERREMOTO!
        
        self.is_running = False
        
        # Caching para não estourar rate limit da API Pública de Dominância
        self.cached_dominance = 50.0
        self.last_dominance_fetch = 0

    async def initialize(self):
        from services.redis_service import redis_service
        await redis_service.connect()
        await sovereign_service.initialize()
        await bybit_rest_service.initialize()
        logger.info("Guardian Agent Inicializado: Olhos 3D no BTC (Price, ADX, Dominância)!")

    async def get_btc_macro_state(self):
        """Monitora o BTC para TERREMOTO DE 5 MINUTOS (Dump/Pump violento)."""
        ticker = await bybit_rest_service.get_tickers("BTCUSDT")
        try:
            current_price = float(ticker.get("result", {}).get("list", [{}])[0].get("lastPrice", 0))
        except (ValueError, TypeError, IndexError):
            return "NORMAL", 0

        now = time.time()
        self.btc_price_history.append((now, current_price))
        
        cutoff = now - (self.macro_window_minutes * 60)
        self.btc_price_history = [x for x in self.btc_price_history if x[0] >= cutoff]

        if len(self.btc_price_history) >= 2:
            oldest_price = self.btc_price_history[0][1]
            variation = ((current_price - oldest_price) / oldest_price) * 100
            
            if variation >= self.macro_threshold_percent:
                return "PUMP", variation
            elif variation <= -self.macro_threshold_percent:
                return "DUMP", variation
                
        return "NORMAL", 0

    async def get_deep_macro_status(self):
        """[V110.32.1] Extrai o estado Tridimensional do BTC validado pelo ORACLE."""
        try:
            from services.agents.oracle_agent import oracle_agent
            oracle_context = oracle_agent.get_validated_context()
            
            # Se ainda estiver estabilizando ou com dados instáveis, reportamos o status
            status = oracle_context.get("status", "BOOTING")
            if status in ["STABILIZING", "STALE_DATA", "ERROR_ZERO_ADX"]:
                wait_time = oracle_context.get("remaining_wait", 0)
                logger.warning(f"🔮 [ORACLE-GUARD] Dados Instáveis ou em Estabilização! Status: {status} | Espera: {wait_time}s")
            
            return {
                "regime": oracle_context.get("regime", "TRANSITION"),
                "direction": oracle_context.get("btc_direction", "LATERAL"),
                "adx": oracle_context.get("btc_adx", 20.0),
                "dominance": oracle_context.get("dominance", self.cached_dominance),
                "oracle_status": status,
                "is_secure": status == "SECURE"
            }
        except Exception as e:
            logger.error(f"Erro ao consultar Oracle no Guardian: {e}")
            return {
                "regime": "TRANSITION",
                "direction": "LATERAL",
                "adx": 0.0,
                "dominance": self.cached_dominance,
                "oracle_status": "ERROR",
                "is_secure": False
            }

    async def purge_counter_trend(self, slots, btc_direction):
        """Mata imediatamente posições contra a maré em tendência forte do BTC."""
        for slot in slots:
            symbol = slot.get("symbol")
            if not symbol: continue
            
            side = str(slot.get("side", "")).upper() # BUY or SELL
            
            if btc_direction == "UP" and side == "SELL":
                pnl = float(slot.get("pnl_percent", 0))
                logger.critical(f"🛡️ GUARDIÃO [LIMPEZA DE TREND]: Fechando {symbol} (SHORT). Vai contra a SUBIDA brutal do BTC! (PnL atual: {pnl:.1f}%)")
                await self._kill_position(symbol, side, "GUARDIAN_ANTI_TREND_KILL_UP", slot.get("id"))
                
            elif btc_direction == "DOWN" and side == "BUY":
                pnl = float(slot.get("pnl_percent", 0))
                logger.critical(f"🛡️ GUARDIÃO [LIMPEZA DE TREND]: Fechando {symbol} (LONG). Vai contra a QUEDA brutal do BTC! (PnL atual: {pnl:.1f}%)")
                await self._kill_position(symbol, side, "GUARDIAN_ANTI_TREND_KILL_DOWN", slot.get("id"))

    async def evaluate_zombies(self, slots, tempo_limite=15, agressivo=False, btc_direction="LATERAL"):
        """
        Monitora zumbis que não saem do zero a zero e matam a agilidade.
        V66.0: Regra do Almirante - Se não bateu 12% ROI (taxas) no tempo limite, ejetar.
        """
        now = time.time()
        
        for slot in slots:
            symbol = slot.get("symbol")
            if not symbol: continue
            
            opened_at = slot.get("opened_at", slot.get("timestamp_last_update", now))
            # FIX Timestamp Bug: Converter millisegundos para segundos do runtime Bybit/Firebase
            if opened_at > 2000000000:
                opened_at = opened_at / 1000.0
                
            duration_minutes = (now - opened_at) / 60
            pnl_percent = float(slot.get("pnl_percent", 0))
            side = str(slot.get("side", "BUY")).upper()
            
            # 1. Regra de Divergência Tática (BTC sobe, Alt cai no Long) [V66.0]
            if btc_direction == "UP" and side == "BUY" and pnl_percent < -15.0 and duration_minutes > 5:
                logger.critical(f"🛡️ GUARDIÃO [DIVERGÊNCIA]: {symbol} (LONG) perdendo -15% enquanto BTC Sobe. Falha de acompanhamento! Abatendo.")
                await self._kill_position(symbol, side, "GUARDIAN_DIVERGENCE_FAIL", slot.get("id"))
                continue

            # 2. Regra Zumbi (Time-Based / Performance)
            # [V69.0] Tempos ajustados: mais paciência = menos taxas acumuladas
            current_tempo_limite = 10 if btc_direction == "LATERAL" and pnl_percent < 0 else tempo_limite
            
            if duration_minutes > current_tempo_limite:
                from services.signal_generator import signal_generator
                try:
                    dec_res = await signal_generator.detect_btc_decorrelation(symbol)
                    is_decor = dec_res.get('is_decorrelated', False)
                except Exception as e:
                    logger.error(f"Erro ao verificar descorrelação do zumbi {symbol}: {e}")
                    is_decor = False
                
                # Moedas Descorrelacionadas ganham limite triplo
                vida_util = tempo_limite * 3 if is_decor else tempo_limite
                
                if duration_minutes > vida_util:
                    # [V66.0] PERFORMANCE GUARD: Se após a vida útil não bateu 12% ROI, ejeta.
                    # Garantir os 12% ROI (~10% líquido) solicitados pelo usuário para taxas.
                    if pnl_percent < 12.0:
                        reason = "GUARDIAN_STAGNANT_ZOMBIE"
                        if is_decor: reason = "GUARDIAN_DECORRELATED_TIMEOUT"
                        
                        logger.warning(f"🏁 {reason}: {symbol} envelheceu {duration_minutes:.1f}m sem atingir 12% ROI (Atual: {pnl_percent:.2f}%). Abortando para giro!")
                        await self._kill_position(symbol, side, reason, slot.get("id"))
                    else:
                        # Se estiver lucrando bem, deixa o Sentinel (ExecutionProtocol) gerir, mas avisa.
                        logger.info(f"✨ {symbol} envelheceu {duration_minutes:.1f}m mas está lucrando {pnl_percent:.1f}%. Sentinel assume.")

    async def _kill_position(self, symbol, side, reason, slot_id=None):
        norm_symbol = symbol.replace(".P", "").upper()
        # Verificar o size real na corretora
        positions = await bybit_rest_service.get_active_positions(symbol=norm_symbol)
        if not positions:
            logger.info(f"Tentou matar {symbol}, mas ordem já não existe na base da Bybit.")
            if slot_id:
                 logger.warning(f"🛡️ GUARDIÃO [GHOST BUSTER]: Purgando fantasma {symbol} direto do Firebase Slot {slot_id}.")
                 await sovereign_service.hard_reset_slot(slot_id, reason="GUARDIAN_GHOST_PURGE")
            return

        for pos in positions:
            size = float(pos.get("size", 0))
            if size > 0:
                logger.error(f"⚔️ O GUARDIÃO ORDENOU O ABATE de {symbol} ({reason})")
                success = await bybit_rest_service.close_position(symbol, pos.get("side", side), size, reason=reason)
                if not success:
                    logger.info(f"Tentou matar {symbol}, mas ordem já não existe na base da Bybit.")
                    if slot_id:
                        logger.warning(f"🛡️ GUARDIÃO [GHOST BUSTER]: Purgando fantasma {symbol} direto do Firebase Slot {slot_id}.")
                        await sovereign_service.hard_reset_slot(slot_id, reason="GUARDIAN_GHOST_PURGE")

    async def loop(self):
        self.is_running = True
        
        # Flags para não spammar os logs se a leitura for a mesma seqüencial
        last_log_state = ""
        
        while self.is_running:
            try:
                # 1. Macro Básico de Sobrevivência (Terremoto Flash)
                macro_state, var_pct = await self.get_btc_macro_state()
                slots = await sovereign_service.get_active_slots()
                
                # Defesa 1: O Defletor de Terremoto Instantâneo (Emergency Dump/Pump 1%)
                if macro_state in ["PUMP", "DUMP"]:
                    logger.error(f"🌋 ALERTA DE TERREMOTO! BTC {macro_state} ({var_pct:.2f}% em {self.macro_window_minutes}m)")
                    contra_mare = "SELL" if macro_state == "PUMP" else "BUY"
                    for slot in slots:
                        if slot.get("symbol") and str(slot.get("side", "")).upper() == contra_mare:
                            pnl_pct = float(slot.get("pnl_percent", 0))
                            if pnl_pct <= 0.5:
                                logger.critical(f"🛡️ GUARDIÃO SALVANDO CAPITAL: Abortando {slot['symbol']} ({contra_mare}). Terremoto engolindo a direção! (PnL: {pnl_pct:.2f}%)")
                                await self._kill_position(slot["symbol"], slot["side"], "GUARDIAN_MACRO_DEFENSE", slot.get("id"))
                                
                # 2. Gestão Tridimensional do Portfólio (A "Cabeça" Estratégica)
                deep_macro = await self.get_deep_macro_status()
                
                regime = deep_macro["regime"]
                direcao = deep_macro["direction"]
                adx = deep_macro["adx"]
                dom = deep_macro["dominance"]
                
                current_log_state = f"{regime}_{direcao}_{int(adx)}_{int(dom)}"
                
                # MODO 1: TENDÊNCIA BRUTAL SUCTÓRIA (BTC TRENDING + ADX > 25 + DOMINANCE > 48%)
                if (regime == "TRENDING" or adx > 25) and direcao in ["UP", "DOWN"] and dom > 48:
                    if current_log_state != last_log_state:
                        logger.info(f"👑 [GUARDIAN TRENDING] BTC ferveu e definiu lado! (Dir: {direcao}, ADX: {adx:.1f}, Dom: {dom:.1f}%). Exterminando contramaré.")
                        last_log_state = current_log_state
                    await self.purge_counter_trend(slots, btc_direction=direcao)
                    # Adiciona a patrulha normal de zumbis para moedas a favor da tendência que estagnaram no 0 a 0
                    await self.evaluate_zombies(slots, tempo_limite=20, agressivo=False, btc_direction=direcao)
                
                # MODO 2: LATERAL (RANGING)
                elif regime == "RANGING" or direcao == "LATERAL":
                    if current_log_state != last_log_state:
                        logger.info(f"💤 [GUARDIAN RANGING] Mercado Lateral (ADX: {adx:.1f}). Modo Fast-Evolve ativo. Caçando zumbis estagnados agressivamente.")
                        last_log_state = current_log_state
                    await self.evaluate_zombies(slots, tempo_limite=12, agressivo=True, btc_direction=direcao)
                    
                # MODO 3: TRANSIÇÃO / NORMAL
                else:
                    if current_log_state != last_log_state:
                        logger.info(f"📊 [GUARDIAN TRANSITION] Mercado Estável -> ADX {adx:.1f}, Dom {dom:.1f}%. Patrulha Zumbi Padrão on.")
                        last_log_state = current_log_state
                    await self.evaluate_zombies(slots, tempo_limite=20, agressivo=False, btc_direction=direcao)

            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"Erro no loop do Guardian: {e}")
            
            await asyncio.sleep(self.check_interval)

if __name__ == "__main__":
    guardian = GuardianAgent()
    asyncio.run(guardian.initialize())
    try:
        asyncio.run(guardian.loop())
    except KeyboardInterrupt:
        logger.info("Guardian desativado manualmente.")
