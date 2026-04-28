# -*- coding: utf-8 -*-
import logging
import asyncio
import time
from typing import Dict, Any, List
from services.agents.aios_adapter import AIOSAgent
from services.backtest.engine import backtest_engine
from services.backtest import data_extractor
from services.bybit_ws import bybit_ws_service
from services.google_calendar_service import google_calendar_service
from services.agents.quartermaster import quartermaster_agent # [V110.135]
from services.sovereign_service import sovereign_service
from services.kernel.dispatcher import kernel
from services.agents.market_data import get_sector
from services.agents.vision_agent import vision_agent # [V1.0]
from config import settings

logger = logging.getLogger("LibrarianAgent")

def normalize_symbol(symbol: str) -> str:
    """Limpa sufixos .P e PERP para compatibilidade REST/Firebase."""
    if not symbol: return symbol
    # Remove sufixos comuns (WebSocket .P e PERP)
    clean = symbol.upper().replace(".P", "").replace("PERP", "").split(":")[0]
    # Garante sufixo USDT para API de Klines se necessário
    if not (clean.endswith("USDT") or clean.endswith("USDC")):
        clean = f"{clean}USDT"
    return clean

class LibrarianAgent(AIOSAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent-librarian-specialist",
            role="librarian",
            capabilities=["historical_analysis", "batch_backtesting", "ranking", "sector_strategy"]
        )
        self.is_running = False
        self.study_interval = 7200  # 2 horas
        self.last_study_time = 0
        self.rankings = []
        self.live_rankings = {} # V110.100: Para feedback imediato via REST
        self.sector_insights = {}
        self.asset_dna = {} # V2.0: Período de DNA persistente
        self.negative_patterns = {} # V2.0: ML Feedback Loop
        self.consecutive_losses = {} # [V110.128] Super Quarantine Tracker
        self.spring_elite_list = [] # [V110.165] Top 20 Mola Elite Pairs
        # [V4.0] MATRIZ DE ESPECIALISTA: DNA Sniper para 40 pares principais.
        self.SPECIALIST_MATRIX = {
            "AVAXUSDT": {"respiro": 25, "rf_delay": 1.4, "beta": 1.5, "profile": "EXTREME"},
            "NEARUSDT": {"respiro": 22, "rf_delay": 1.3, "beta": 1.3, "profile": "VOLATILE"},
            "APTUSDT":  {"respiro": 25, "rf_delay": 1.4, "beta": 1.6, "profile": "EXTREME"},
            "SUIUSDT":  {"respiro": 25, "rf_delay": 1.4, "beta": 1.6, "profile": "EXTREME"},
            "OPUSDT":   {"respiro": 22, "rf_delay": 1.3, "beta": 1.4, "profile": "VOLATILE"},
            "ARBUSDT":  {"respiro": 20, "rf_delay": 1.2, "beta": 1.3, "profile": "VOLATILE"},
            "RENDERUSDT":{"respiro": 25, "rf_delay": 1.5, "beta": 1.7, "profile": "EXTREME"},
            "FETUSDT":  {"respiro": 25, "rf_delay": 1.5, "beta": 1.7, "profile": "EXTREME"},
            "INJUSDT":  {"respiro": 22, "rf_delay": 1.3, "beta": 1.4, "profile": "VOLATILE"},
            "TIAUSDT":  {"respiro": 25, "rf_delay": 1.4, "beta": 1.5, "profile": "EXTREME"},
            "LINKUSDT": {"respiro": 15, "rf_delay": 1.0, "beta": 1.0, "profile": "STABLE"},
            "DOTUSDT":  {"respiro": 12, "rf_delay": 1.0, "beta": 0.9, "profile": "STABLE"},
            "ADAUSDT":  {"respiro": 10, "rf_delay": 1.0, "beta": 0.8, "profile": "STABLE"},
            "POLUSDT":  {"respiro": 15, "rf_delay": 1.1, "beta": 1.1, "profile": "STABLE"},
            "ATOMUSDT": {"respiro": 15, "rf_delay": 1.0, "beta": 1.0, "profile": "STABLE"},
            "LTCUSDT":  {"respiro": 10, "rf_delay": 1.0, "beta": 0.7, "profile": "STABLE"},
            "BCHUSDT":  {"respiro": 18, "rf_delay": 1.2, "beta": 1.2, "profile": "VOLATILE"},
            "XLMUSDT":  {"respiro": 10, "rf_delay": 1.0, "beta": 0.7, "profile": "STABLE"},
            "XRPUSDT":  {"respiro": 10, "rf_delay": 1.0, "beta": 0.6, "profile": "STABLE"},
            "TRXUSDT":  {"respiro": 8,  "rf_delay": 1.0, "beta": 0.4, "profile": "STABLE"},
            "ALGOUSDT": {"respiro": 10, "rf_delay": 1.0, "beta": 0.8, "profile": "STABLE"},
            "ETCUSDT":  {"respiro": 12, "rf_delay": 1.1, "beta": 1.0, "profile": "STABLE"},
            "FILUSDT":  {"respiro": 18, "rf_delay": 1.2, "beta": 1.2, "profile": "VOLATILE"},
            "STXUSDT":  {"respiro": 22, "rf_delay": 1.3, "beta": 1.4, "profile": "VOLATILE"},
            "ICPUSDT":  {"respiro": 20, "rf_delay": 1.2, "beta": 1.3, "profile": "VOLATILE"},
            "HBARUSDT": {"respiro": 15, "rf_delay": 1.1, "beta": 1.0, "profile": "STABLE"},
            "KASUSDT":  {"respiro": 25, "rf_delay": 1.4, "beta": 1.5, "profile": "EXTREME"},
            "LDOUSDT":  {"respiro": 20, "rf_delay": 1.2, "beta": 1.3, "profile": "VOLATILE"},
            "AAVEUSDT": {"respiro": 18, "rf_delay": 1.2, "beta": 1.1, "profile": "VOLATILE"},
            "RUNEUSDT": {"respiro": 25, "rf_delay": 1.4, "beta": 1.6, "profile": "EXTREME"},
            "GRTUSDT":  {"respiro": 20, "rf_delay": 1.2, "beta": 1.3, "profile": "VOLATILE"},
            "EGLDUSDT": {"respiro": 15, "rf_delay": 1.1, "beta": 1.0, "profile": "STABLE"},
            "SANDUSDT": {"respiro": 18, "rf_delay": 1.2, "beta": 1.2, "profile": "VOLATILE"},
            "MANAUSDT": {"respiro": 18, "rf_delay": 1.2, "beta": 1.2, "profile": "VOLATILE"},
            "THETAUSDT":{"respiro": 15, "rf_delay": 1.1, "beta": 1.1, "profile": "STABLE"},
            "VETUSDT":  {"respiro": 12, "rf_delay": 1.0, "beta": 0.9, "profile": "STABLE"},
            "EOSUSDT":  {"respiro": 10, "rf_delay": 1.0, "beta": 0.8, "profile": "STABLE"},
            "CHZUSDT":  {"respiro": 15, "rf_delay": 1.1, "beta": 1.1, "profile": "STABLE"},
            "FTMUSDT":  {"respiro": 22, "rf_delay": 1.3, "beta": 1.4, "profile": "VOLATILE"},
            "UNIUSDT":  {"respiro": 15, "rf_delay": 1.1, "beta": 1.1, "profile": "STABLE"},
        }
        self.memecoin_blacklist = ["PEPE", "DOGE", "SHIB", "FLOKI", "BONK", "WIF", "MYRO", "1000SATS", "ORDI", "MEME", "TURBO", "PEOPLE"]

    def is_specialist_asset(self, symbol: str) -> bool:
        """Verifica se o ativo pertence à Matriz de Especialistas (DNA Sniper)."""
        norm_symbol = symbol.replace(".P", "").upper()
        return norm_symbol in self.SPECIALIST_MATRIX

    def get_specialist_symbols(self, suffix: str = ".P") -> list:
        """Retorna a lista de símbolos da Matriz com o sufixo desejado."""
        return [f"{s}{suffix}" for s in self.SPECIALIST_MATRIX.keys()]

    def detect_fvg(self, df) -> List[Dict[str, Any]]:
        """[SMC] Detecta Fair Value Gaps no DataFrame."""
        fvgs = []
        if len(df) < 3: return fvgs
        
        for i in range(1, len(df) - 1):
            # Bullish FVG: Low(i+1) > High(i-1)
            if df['low'].iloc[i+1] > df['high'].iloc[i-1]:
                fvgs.append({
                    "type": "BULLISH",
                    "top": df['low'].iloc[i+1],
                    "bottom": df['high'].iloc[i-1],
                    "index": i,
                    "timestamp": df.index[i]
                })
            # Bearish FVG: High(i+1) < Low(i-1)
            elif df['high'].iloc[i+1] < df['low'].iloc[i-1]:
                fvgs.append({
                    "type": "BEARISH",
                    "top": df['low'].iloc[i-1],
                    "bottom": df['high'].iloc[i+1],
                    "index": i,
                    "timestamp": df.index[i]
                })
        return fvgs

    def detect_order_blocks(self, df) -> List[Dict[str, Any]]:
        """[SMC] Detecta Order Blocks baseados em quebra de estrutura e volume."""
        obs = []
        if len(df) < 5: return obs
        
        for i in range(2, len(df) - 2):
            # Bullish OB: Última vela de baixa antes de um forte movimento de alta que supera a máxima anterior
            if df['close'].iloc[i] < df['open'].iloc[i]: # Vela de baixa
                strong_move = df['close'].iloc[i+1] > df['high'].iloc[i] and df['close'].iloc[i+2] > df['close'].iloc[i+1]
                if strong_move:
                    obs.append({
                        "type": "BULLISH",
                        "top": df['high'].iloc[i],
                        "bottom": df['low'].iloc[i],
                        "timestamp": df.index[i]
                    })
            
            # Bearish OB: Última vela de alta antes de um forte movimento de baixa
            elif df['close'].iloc[i] > df['open'].iloc[i]: # Vela de alta
                strong_move = df['close'].iloc[i+1] < df['low'].iloc[i] and df['close'].iloc[i+2] < df['close'].iloc[i+1]
                if strong_move:
                    obs.append({
                        "type": "BEARISH",
                        "top": df['high'].iloc[i],
                        "bottom": df['low'].iloc[i],
                        "timestamp": df.index[i]
                    })
        return obs

    async def on_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        msg_type = message.get("type")
        if msg_type == "START_STUDY":
            asyncio.create_task(self.perform_full_market_study())
            return {"status": "started"}
        elif msg_type == "START_VISUAL_SCAN":
            asyncio.create_task(self.perform_global_visual_scan())
            return {"status": "started_visual_scan"}
        elif msg_type == "GET_RANKINGS":
            return {"status": "success", "rankings": self.rankings}
        return {"status": "error", "message": f"Unknown command: {msg_type}"}

    async def perform_global_visual_scan(self):
        """[V1.0] SCAN VISUAL GLOBAL: Solicita prints de todas as 40 moedas da Matriz."""
        logger.info("👁️ [LIBRARIAN] Iniciando Scan Visual Global das 40 moedas da Matriz...")
        
        await sovereign_service.log_event(
            agent="Librarian",
            message="Iniciando Scan Visual Global das 40 moedas da Matriz para análise de contexto.",
            payload={"action": "GLOBAL_VISUAL_SCAN_START", "count": len(self.SPECIALIST_MATRIX)}
        )

        symbols = list(self.SPECIALIST_MATRIX.keys())
        total = len(symbols)
        
        for i, symbol in enumerate(symbols):
            try:
                # Progress update to UI
                if sovereign_service.rtdb:
                    try:
                        await asyncio.to_thread(
                            sovereign_service.rtdb.child("librarian_intelligence").update,
                            {
                                "status": "VISUAL_SCAN", 
                                "current_symbol": symbol,
                                "progress": round(((i+1)/total)*100, 1),
                                "updated_at": int(time.time() * 1000)
                            }
                        )
                    except: pass

                logger.info(f"👁️ [LIBRARIAN] Scan {i+1}/{total}: {symbol}")
                # Solicita ao Visão uma análise silenciosa de contexto
                # O Visão 5.0 já usará o novo motor anotado automaticamente
                await vision_agent.analyze_market_context(symbol)
                
                # Pequeno delay para não sobrecarregar a API Vision/Screenshot
                await asyncio.sleep(1.5) 
            except Exception as e:
                logger.error(f"Erro no scan visual de {symbol}: {e}")

        await sovereign_service.log_event(
            agent="Librarian",
            message="Scan Visual Global Concluído. Contexto visual mapeado para a Frota Elite.",
            payload={"action": "GLOBAL_VISUAL_SCAN_END"}
        )
        
        if sovereign_service.rtdb:
            try:
                await asyncio.to_thread(
                    sovereign_service.rtdb.child("librarian_intelligence").update,
                    {"status": "COMPLETED", "updated_at": int(time.time() * 1000)}
                )
            except: pass

    async def get_visual_data(self, symbol: str, interval: str = "1h", limit: int = 200) -> Dict[str, Any]:
        """[V5.0] Prepara dados OHLCV + SMC para o Renderer."""
        symbol = normalize_symbol(symbol)
        try:
            # 1. Pegar dados do banco local (Klines)
            conn = data_extractor.get_db_connection()
            # Pega as últimas 'limit' velas para ter histórico das médias
            import pandas as pd
            df = pd.read_sql_query(
                "SELECT start_time, open, high, low, close, volume FROM klines WHERE symbol = ? AND interval = ? ORDER BY start_time DESC LIMIT ?",
                conn, params=(symbol, interval, limit)
            )
            conn.close()
            
            # Fallback: Se o banco local estiver vazio, buscar via API (Bybit)
            if df.empty:
                logger.info(f"DB local vazio para {symbol} ({interval}). Buscando via REST API...")
                from services.bybit_rest_service import bybit_rest_service
                klines = await bybit_rest_service.get_klines(symbol, interval, limit=limit)
                if klines:
                    # Converter klines da Bybit para DataFrame compatível
                    df = pd.DataFrame(klines, columns=['start_time', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
                    df['start_time'] = pd.to_datetime(df['start_time'].astype(float), unit='ms')
                    df = df[['start_time', 'open', 'high', 'low', 'close', 'volume']]
                    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric)
                else:
                    return {}
            
            df = df.sort_values('start_time')
            if not df.index.name == 'start_time':
                df.set_index('start_time', inplace=True)
            
            # 2. Detectar SMC
            obs = self.detect_order_blocks(df)
            fvgs = self.detect_fvg(df)
            
            # 3. [V5.6] Detectar Padrão 1-2-3 (Historical Scan)
            # Usamos o SignalGenerator para consistência (Local import to avoid circular dependency)
            from services.signal_generator import signal_generator
            patterns_123 = await signal_generator.detect_123_pattern(symbol, interval=interval, limit=limit, find_all=True)
            
            return {
                "df": df,
                "obs": obs,
                "fvgs": fvgs,
                "patterns_123": patterns_123 # Retorna lista de todos os padrões encontrados
            }
        except Exception as e:
            logger.error(f"Erro ao preparar dados visuais para {symbol}: {e}")
            return {}

    async def run_loop(self):
        """Loop principal do Bibliotecário."""
        self.is_running = True
        logger.info("📚 Librarian Agent V2.0 (Strategic): ONLINE.")
        
        # V110.100: Initial Stagger - Wait 30s to allow API server to breathe on boot
        await asyncio.sleep(30)
        
        while self.is_running:
            now = time.time()
            if now - self.last_study_time >= self.study_interval:
                await self.perform_post_mortem_feedback() # V2.0: Primeiro aprende, depois estuda
                await self.perform_full_market_study()
                self.last_study_time = now
            
            await asyncio.sleep(60)

    async def get_asset_dna(self, symbol: str) -> Dict[str, Any]:
        """Retorna o perfil de DNA processado para o Capitão."""
        symbol = normalize_symbol(symbol)
        clean_name = symbol.replace("USDT", "")
        
        # 1. Filtro de Segurança: Memecoins (Quarentena)
        if clean_name in self.memecoin_blacklist:
            return {
                "status": "REJECTED",
                "reason": "QUARENTENA_MEMECOIN",
                "nectar_seal": "💀 BLACKLIST",
                "advice": "Moeda em quarentena de segurança. Não operar até robustez confirmada."
            }

        # 2. [V110.128] Super Quarentena: Bloqueio por perdas consecutivas
        loss_count = self.consecutive_losses.get(symbol, 0)
        if loss_count >= 2:
            # Verifica se a última perda ainda está dentro da janela de respiro (4 horas)
            pattern = self.negative_patterns.get(symbol)
            if pattern and (time.time() - pattern["timestamp"] < 14400): # 4 horas
                return {
                    "status": "REJECTED",
                    "reason": "SUPER_QUARANTINE",
                    "nectar_seal": "🚨 QUARENTENA",
                    "advice": f"Ativo bloqueado por {loss_count} perdas consecutivas. Aguardando estabilização (4h)."
                }
            else:
                # Reset se passou o tempo
                self.consecutive_losses[symbol] = 0

        # 3. Verifica Padrões Negativos (Feedback Loop)
        if symbol in self.negative_patterns:
            pattern = self.negative_patterns[symbol]
            if time.time() - pattern["timestamp"] < 259200: # 72 horas
                return {
                    "status": "HIGH_RISK",
                    "reason": "NEGATIVE_PATTERN_RECURRENCE",
                    "nectar_seal": "⚠️ MONITOR",
                    "advice": f"Evitar entradas agressivas. Motivo: {pattern['reason']}. Aguardar Ambush profundo."
                }

        # 4. Retorna DNA Padrão se não tiver estudo recente
        dna = self.asset_dna.get(symbol, {
            "volatility_class": "MEDIUM",
            "nectar_seal": "🛡️ VANGUARD",
            "ambush_buffer": 0.0016, 
            "is_trap_prone": False,
            "is_spring_moment": False,
            "respiro_roi_buffer": 10.0,
            "rf_trigger_delay": 1.0
        })
        
        # 5. [V4.0] SOBREPOSIÇÃO DE ESPECIALISTA: Injeta parâmetros da Matriz de 40 Pares
        if symbol in self.SPECIALIST_MATRIX:
            matrix = self.SPECIALIST_MATRIX[symbol]
            dna["respiro_roi_buffer"] = matrix["respiro"]
            dna["rf_trigger_delay"] = matrix["rf_delay"]
            dna["beta_correlation"] = matrix["beta"]
            dna["specialist_profile"] = matrix["profile"]
            
            # Sincroniza classes de volatilidade com a matriz
            if matrix["profile"] == "EXTREME":
                dna["volatility_class"] = "EXTREME"
                dna["ambush_buffer"] = max(dna.get("ambush_buffer", 0), 0.0040)
            elif matrix["profile"] == "VOLATILE":
                dna["volatility_class"] = "VOLATILE"
                dna["ambush_buffer"] = max(dna.get("ambush_buffer", 0), 0.0025)
            else:
                dna["volatility_class"] = "STABLE"
                dna["ambush_buffer"] = min(dna.get("ambush_buffer", 0.0016), 0.0012)
        
        return dna

    async def perform_post_mortem_feedback(self):
        """[V2.0] ML Feedback Loop: Analisa perdas recentes para identificar armadilhas."""
        logger.info("🧠 [LIBRARIAN ML] Iniciando análise post-mortem das últimas 72h...")
        try:
            # Pega histórico do Vault
            history = await sovereign_service.get_vault_history(limit=50)
            if not history: return

            # [V110.128] Ordena por timestamp desc para conferência de sequencialidade
            history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

            now = time.time()
            recent_losses = [h for h in history if h.get("pnl_net", 0) < 0 and (now - h.get("timestamp", 0)) < 259200]
            
            # [V110.128] Rastreamento de perdas consecutivas por ativo
            temp_counts = {}
            for h in history:
                sym = normalize_symbol(h.get("symbol"))
                pnl = h.get("pnl_net", 0)
                if sym not in temp_counts:
                    temp_counts[sym] = {"losses": 0, "active": True}
                
                if temp_counts[sym]["active"]:
                    if pnl < 0:
                        temp_counts[sym]["losses"] += 1
                    else:
                        temp_counts[sym]["active"] = False # Quebrou a sequência com um WIN
            
            self.consecutive_losses = {s: d["losses"] for s, d in temp_counts.items()}

            for loss in recent_losses:
                symbol = loss.get("symbol")
                reason = loss.get("close_reason", "STOP_LOSS")
                
                # Se perdemos por SL ou Trap Detectada, registramos o padrão
                if "SL" in reason or "TRAP" in reason:
                    self.negative_patterns[symbol] = {
                        "reason": reason,
                        "timestamp": loss.get("timestamp", now),
                        "side": loss.get("side")
                    }
                    logger.warning(f"📝 [LIBRARIAN ML] Padrão negativo registrado para {symbol}: {reason} (Consecutives: {self.consecutive_losses.get(symbol, 0)})")
        except Exception as e:
            logger.error(f"Erro no ML Feedback Loop: {e}")

    async def perform_full_market_study(self):
        """Realiza o estudo estratégico apenas dos pares monitorados (Frota)."""
        logger.info("📖 [LIBRARIAN V2] Iniciando estudo de inteligência da frota...")
        
        try:
            # [V2.2] Sinaliza início imediato para o Frontend
            if sovereign_service.rtdb:
                try:
                    await asyncio.to_thread(
                        sovereign_service.rtdb.child("librarian_intelligence").update,
                        {"status": "STUDYING", "updated_at": int(time.time() * 1000)}
                    )
                except: pass
        except: pass

        try:
            data_extractor.init_db()
            
            # Pega a frota do WebSocket (Ativos reais do Radar)
            monitored = list(bybit_ws_service.active_symbols) if bybit_ws_service and bybit_ws_service.active_symbols else []
            
            if not monitored:
                # Fallback 1: Tenta pegar do histórico do banco local
                monitored = data_extractor.get_monitored_from_db()
            
            if not monitored:
                # Fallback 2: Produção/Cold-Boot. Pega a lista de Elite (alavancagem >= 50x)
                logger.info("📡 [LIBRARIAN] Cold-boot detectado. Buscando Eligible Elite Pairs...")
                eligible = data_extractor.get_eligible_pairs()
                monitored = [p[0] for p in eligible] if eligible else []
            
            if not monitored:
                logger.warning("⚠️ [LIBRARIAN] Nenhum ativo encontrado para estudo (WebSocket/DB/Bybit Vazio).")
                return

            all_results = []
            sector_agg = {} 
            total_ghost_insights = 0
            total_assets = len(monitored)
            processed_count = 0

            for symbol_raw in monitored:
                # NORMALIZAÇÃO SNIPER: Garante compatibilidade REST e RTDB
                symbol = normalize_symbol(symbol_raw)
                
                if symbol in settings.ASSET_BLOCKLIST:
                    continue

                processed_count += 1
                progress = round((processed_count / total_assets) * 100, 1)
                
                logger.info(f"🧐 [LIBRARIAN] [{progress}%] Analisando {symbol} (Origem: {symbol_raw})...")
                
                # [V2.2] Telemetria de Pulso para a UI
                if sovereign_service.rtdb:
                    try:
                        await asyncio.to_thread(
                            sovereign_service.rtdb.child("librarian_intelligence").update,
                            {
                                "status": "STUDYING", 
                                "current_symbol": symbol,
                                "progress": progress,
                                "processed_count": processed_count,
                                "total_assets": total_assets,
                                "ghost_count_session": total_ghost_insights,
                                "updated_at": int(time.time() * 1000)
                            }
                        )
                    except: pass
                
                sector = get_sector(symbol)
                
                # Baixar apenas o GAP de dados que falta
                last_ts = data_extractor.get_last_timestamp(symbol, "1h")
                # V2.1: Aumento de histórico para 1500 velas (cerca de 62 dias) para amostragem mais precisa
                download_limit = 1500 if last_ts == 0 else 100
                data_extractor.download_klines(symbol, "1h", limit=download_limit, start_time=last_ts)
                
                try:
                    res = backtest_engine.simulate(
                        symbol=symbol,
                        interval="1h",
                        initial_balance=100.0,
                        toggles={"lateral_guillotine": True, "sentinel": True}
                    )
                    
                    if "error" not in res:
                        win_rate_val = float(res.get("win_rate", "0%").replace("%", ""))
                        max_dd = float(res.get("max_drawdown", "0%").replace("%", ""))

                        # V110.100: O Bússola do Capitão - Análise HTF e Quality Seal
                        last_ts_4h = data_extractor.get_last_timestamp(symbol, "4h")
                        data_extractor.download_klines(symbol, "4h", limit=200 if last_ts_4h == 0 else 50, start_time=last_ts_4h)
                        
                        conn = data_extractor.get_db_connection()
                        c = conn.cursor()
                        c.execute("SELECT close FROM klines WHERE symbol = ? AND interval = ? ORDER BY start_time DESC LIMIT 20", (symbol, "4h"))
                        klines_4h = [row[0] for row in c.fetchall()]
                        conn.close()
                        klines_4h.reverse()
                        
                        trend_4h = "NEUTRAL"
                        if len(klines_4h) >= 20:
                            sma20 = sum(klines_4h[-20:]) / 20
                            current = klines_4h[-1]
                            trend_4h = "UP" if current > sma20 else "DOWN"

                        seal = "Vanguard 🛡️"
                        reason = f"Mediano. Retorno tático razoável, H4 {trend_4h}."

                        if win_rate_val >= 65 and max_dd <= 20 and trend_4h == "UP":
                            seal = "SpecOps 🎖️"
                            reason = f"Ativo Seguro. {win_rate_val}% Win-rate e H4 Macro Altista."
                        elif win_rate_val < 48 or max_dd >= 22: # [V110.149] Rigor aumentado (Win < 48% ou DD > 22%)
                            seal = "Quarentena 💀"
                            reason = f"Perigoso. Altos Riscos ({max_dd}% DD) ou Win-rate insuficiente."

                        # [V110.134] ASSET DNA UPGRADE: Wick Intensity & Retest Propensity
                        # Analisamos a estrutura das velas para identificar ativos "traiçoeiros"
                        conn = data_extractor.get_db_connection()
                        c = conn.cursor()
                        c.execute("SELECT high, low, open, close FROM klines WHERE symbol = ? AND interval = ? ORDER BY start_time DESC LIMIT 100", (symbol, "1h"))
                        recent_klines = c.fetchall()
                        conn.close()

                        # [V110.165] SPRING POTENTIAL AUDIT
                        spring_audit = await self._calculate_spring_potential(symbol)
                        
                        wick_intensities = []
                        for h, l, o, cl in recent_klines:
                            intensity = quartermaster_agent.calculate_wick_intensity(h, l, o, cl)
                            wick_intensities.append(intensity)
                            
                        avg_wick = sum(wick_intensities) / len(wick_intensities) if wick_intensities else 0.0
                        
                        # [V110.149] Retest Propensity: Análise simplificada de pavios de rejeição
                        # Reduzido de 2.5 para 2.2 para capturar comportamento traiçoeiro mais cedo.
                        is_retest_heavy = avg_wick > 2.2 
                        
                        vol_val = float(res.get("avg_candle_volatility", "0.5%").replace("%", ""))
                        
                        vol_class = "STABLE"
                        ambush_buffer = 0.0012 # 0.12%
                        respiro_roi = 10.0      # [V4.0] 10% ROI buffer default
                        rf_delay = 1.0          # [V4.0] RF trigger delay default

                        if vol_val > 1.5:
                            vol_class = "EXTREME"
                            ambush_buffer = 0.0045 # 0.45% (Ambush Profundo)
                            respiro_roi = 25.0      # [V4.0] 25% ROI for wicky assets
                        elif vol_val > 0.8:
                            vol_class = "VOLATILE"
                            ambush_buffer = 0.0025 # 0.25%
                            respiro_roi = 15.0      # [V4.0] 15% ROI for volatile assets
                        
                        # [V4.0] RF Delay for Retest Heavy assets
                        if is_retest_heavy:
                            rf_delay = 1.5 # Wait for 1.5x target before moving SL to RF
                        
                        # [V2.1] Nectar Seal logic (Auditoria de Elite restrita por amostragem)
                        trades_count = res.get("trades_count", 0)
                        nectar_seal = "🛡️ VANGUARD"
                        if win_rate_val >= 70 and trend_4h == "UP" and trades_count >= 10:
                            nectar_seal = "🍯 ELITE NECTAR"
                        elif seal == "Quarentena 💀":
                            if settings.BYBIT_EXECUTION_MODE == "PAPER":
                                nectar_seal = "🛡️ VANGUARD (TRAP-WARNING)"
                            else:
                                nectar_seal = "💀 TRAP ZONE"

                        # [V110.152] MOMENTO MOLA: Detecção de Compressão de Volatilidade
                        # Compara o desvio padrão de curto prazo (20 barras) com o de longo prazo (100 barras)
                        # para identificar "molas" prontas para explodir.
                        compression_score = 1.0
                        if len(recent_klines) >= 100:
                            short_closes = [float(k[3]) for k in recent_klines[:20]]
                            long_closes = [float(k[3]) for k in recent_klines[:100]]
                            
                            import math
                            def get_std_dev(data):
                                if not data: return 0
                                mean = sum(data) / len(data)
                                variance = sum((x - mean) ** 2 for x in data) / len(data)
                                return math.sqrt(variance)
                            
                            std_short = get_std_dev(short_closes)
                            std_long = get_std_dev(long_closes)
                            
                            if std_long > 0:
                                compression_score = std_short / std_long
                        
                        # [V110.152] Critério de Mola: Volatilidade < 40% da média histórica
                        is_spring_moment = compression_score < 0.4

                        dna_entry = {
                            "volatility_class": vol_class,
                            "nectar_seal": nectar_seal,
                            "ambush_buffer": ambush_buffer,
                            "ambush_multiplier": round(ambush_buffer * 1000, 1), # V2.1: UI Display Factor
                            "is_trap_prone": vol_val > 1.0 or is_retest_heavy, # [V110.149] Sensibilidade aumentada de 1.2 para 1.0
                            "is_retest_heavy": is_retest_heavy,
                            "is_spring_moment": is_spring_moment,
                            "compression_score": round(compression_score, 3),
                            "wick_intensity": avg_wick,
                            "wick_multiplier": round(avg_wick, 2),
                            "respiro_roi_buffer": respiro_roi, # [V4.0] Specialist Respiro
                            "rf_trigger_delay": rf_delay,       # [V4.0] Specialist RF Delay
                            "trend_4h": trend_4h,
                            "last_update": time.time()
                        }
                        self.asset_dna[symbol] = dna_entry

                        result_entry = {
                            "symbol": symbol,
                            "sector": sector,
                            "win_rate": win_rate_val,
                            "quality_seal": seal,
                            "nectar_seal": nectar_seal, 
                            "seal": f"{nectar_seal} | {seal}", # V2.1: Unified seal for UI consumption
                            "dna": dna_entry, 
                            "spring_audit": spring_audit, # [V110.165]
                            "reason": reason,
                            "trend_4h": trend_4h,
                            "total_pnl": res.get("total_pnl", 0),
                            "pnl_avg": res.get("pnl_avg", 0), # V2.1: Matches UI expectation
                            "trades_count": res.get("trades_count", 0),
                            "max_drawdown": max_dd,
                            "volatility": res.get("avg_candle_volatility", "0%"),
                            "opportunity_legs": res.get("opportunity_legs", []),
                            "ghost_insights": res.get("ghost_insights", []), # V110.40: Momentum explosion insights
                            "updated_at": time.time()
                        }
                        
                        total_ghost_insights += len(result_entry["ghost_insights"])
                        
                        # [V1.0] AGENTE VISÃO: Contexto Visual (Apenas se for Elite ou SpecOps para otimizar)
                        if "ELITE" in nectar_seal or "SpecOps" in seal:
                            logger.info(f"👁️ [LIBRARIAN-VISION] Solicitando contexto visual para {symbol}...")
                            vision_ctx = await vision_agent.analyze_market_context(symbol)
                            dna_entry["visual_context"] = vision_ctx.get("visual_context", "NEUTRAL")
                            result_entry["visual_thoughts"] = vision_ctx.get("visual_context")

                        all_results.append(result_entry)
                        
                        # Agregação por Setor
                        if sector not in sector_agg:
                            sector_agg[sector] = {"pnl": 0, "win_rate_sum": 0, "count": 0, "symbols": []}
                        
                        sector_agg[sector]["pnl"] += res.get("total_pnl", 0)
                        sector_agg[sector]["win_rate_sum"] += win_rate_val
                        sector_agg[sector]["count"] += 1
                        sector_agg[sector]["symbols"].append(symbol)

                        # LIVE FEEDBACK: Atualiza o RTDB e o cache interno para visibilidade imediata
                        self.live_rankings[symbol] = result_entry
                        
                        if sovereign_service.rtdb:
                            try:
                                await asyncio.to_thread(
                                    sovereign_service.rtdb.child("librarian_intelligence").update,
                                    {
                                        f"top_rankings/{symbol}": result_entry,
                                        "last_study": time.time(),
                                        "updated_at": int(time.time() * 1000),
                                        "status": "STUDYING"
                                    }
                                )
                            except Exception as e:
                                logger.warning(f"⚠️ [LIBRARIAN] Falha ao atualizar RTDB (Partial): {e}")

                except Exception as e:
                    logger.error(f"Erro ao estudar {symbol}: {e}")
                
                await asyncio.sleep(0.01)

            # [V110.63.4] Blindagem de Tipo: Garante que win_rate e pnl sejam comparáveis (evita str vs int)
            def safe_sort_key(x):
                try:
                    wr = float(x.get('win_rate', 0))
                    pnl = float(x.get('total_pnl', 0))
                    return (wr, pnl)
                except:
                    return (0.0, 0.0)

            all_results.sort(key=safe_sort_key, reverse=True)
            self.rankings = all_results[:25]

            # [V110.165] SPRING ELITE RANKING
            # Filtra os 20 melhores ativos para a estratégia de Mola
            spring_rankings = []
            for res in all_results:
                if res.get("spring_audit") and res["spring_audit"]["score"] > 0:
                    spring_rankings.append({
                        "symbol": res["symbol"],
                        "score": res["spring_audit"]["score"],
                        "win_rate": res["spring_audit"]["win_rate"],
                        "avg_roi": res["spring_audit"]["avg_roi"]
                    })
            
            spring_rankings.sort(key=lambda x: x["score"], reverse=True)
            self.spring_elite_list = [r["symbol"] for r in spring_rankings[:40]]
            
            logger.info(f"🚀 [SPRING-ELITE] Top 40: {', '.join(self.spring_elite_list)}")

            # Calcular médias setoriais
            sector_final = {}
            if sector_agg:
                for sec, data in sector_agg.items():
                    sector_final[sec] = {
                        "avg_pnl": round(data["pnl"] / data["count"], 2),
                        "avg_win_rate": round(data["win_rate_sum"] / data["count"], 1),
                        "active_pairs": data["count"],
                        "top_pairs": data["symbols"][:5]
                    }
            
            self.sector_insights = sector_final

            # Sincronização Cloud Final
            if sovereign_service.is_active:
                # [V110.151] Sovereign Check: Only use Cloud DB if available
                if sovereign_service.db:
                    for rank in self.rankings:
                        await asyncio.to_thread(
                            sovereign_service.db.collection("fleet_intelligence")
                            .document("librarian")
                            .collection("rankings")
                            .document(rank["symbol"])
                            .set, rank
                        )
                    
                    # Insights de Setor
                    await asyncio.to_thread(
                        sovereign_service.db.collection("fleet_intelligence")
                        .document("librarian")
                        .collection("sector_insights")
                        .document("latest")
                        .set, {"sectors": sector_final, "updated_at": time.time()}
                    )

                # RTDB (Overview)
                if sovereign_service.rtdb:
                    try:
                        await asyncio.to_thread(
                            sovereign_service.rtdb.child("librarian_intelligence").update, 
                            {
                                "top_rankings": {r["symbol"]: r for r in all_results},
                                "spring_elite": self.spring_elite_list,
                                "sector_analysis": sector_final,
                                "last_study": time.time(),
                                "updated_at": int(time.time() * 1000),
                                "status": "COMPLETED"
                            }
                        )
                        logger.info("✅ [LIBRARIAN] RTDB Full Sync SUCCESS.")
                    except Exception as e:
                        logger.error(f"❌ [LIBRARIAN] RTDB Full Sync FAILED: {e}")

            logger.info(f"✅ [LIBRARIAN V2] Estudo Concluído. {len(all_results)} ativos, {len(sector_final)} setores.")

            # [V110.118] MISSED OPPORTUNITIES TRACKER
            # Identifica ativos com ELITE NECTAR que tiveram movimentos de 2%-10%
            # enquanto o sistema estava bloqueado pela Guilhotina Lateral.
            # Esses dados são publicados na UI para auditoria e refinamento da estratégia.
            try:
                missed_opps = []
                for result in all_results:
                    sym = result.get("symbol")
                    seal = result.get("nectar_seal", "")
                    is_elite = "ELITE" in seal or "NECTAR" in seal
                    if not is_elite:
                        continue

                    ghost_insights = result.get("ghost_insights", [])
                    for ghost in ghost_insights:
                        potential_roi = ghost.get("potential", 0)  # ROI% em alavancagem
                        # Converte para % de movimento real: potential_roi / leverage (50x)
                        move_pct = potential_roi / 50.0
                        if 2.0 <= move_pct <= 10.0:
                            missed_opps.append({
                                "symbol": sym,
                                "seal": seal,
                                "move_pct": round(move_pct, 2),
                                "potential_roi_pct": round(potential_roi, 1),
                                "side": ghost.get("side", "LONG"),
                                "reason": ghost.get("reason", "MOMENTUM"),
                                "timestamp": ghost.get("time", 0),
                                "price": ghost.get("price", 0)
                            })

                if missed_opps:
                    missed_opps.sort(key=lambda x: x["move_pct"], reverse=True)
                    top_missed = missed_opps[:10]  # Máximo 10 para a UI
                    logger.warning(
                        f"📊 [V110.118 MISSED-OPP] {len(missed_opps)} oportunidades 2%-10% perdidas! "
                        f"Top: {top_missed[0]['symbol']} ({top_missed[0]['move_pct']:.1f}%)"
                    )
                    if sovereign_service.rtdb:
                        try:
                            await asyncio.to_thread(
                                sovereign_service.rtdb.child("librarian_intelligence").update,
                                {
                                    "missed_opportunities": top_missed,
                                    "missed_opportunities_count": len(missed_opps),
                                    "missed_opportunities_updated_at": int(time.time() * 1000)
                                }
                            )
                            logger.info(f"✅ [LIBRARIAN] Missed Opportunities sincronizadas no RTDB: {len(top_missed)} itens.")
                        except Exception as rtdb_err:
                            logger.warning(f"⚠️ [LIBRARIAN] Falha ao sincronizar Missed Opportunities: {rtdb_err}")
            except Exception as mo_err:
                logger.error(f"Erro no Missed Opportunities Tracker: {mo_err}")

        except Exception as e:
            logger.error(f"Falha crítica no estudo do Bibliotecário: {e}")
        finally:
            # [V110.100] SAFETY SHIELD: Garante que o Oráculo nunca fique travado em 'STUDYING'
            if sovereign_service.rtdb:
                try:
                    current_data = await asyncio.to_thread(sovereign_service.rtdb.child("librarian_intelligence").get)
                    if current_data and current_data.get("status") == "STUDYING":
                        # Se ainda está em STUDYING e chegamos aqui, algo interrompeu ou finalizou sem atualizar.
                        # Forçamos COMPLETED apenas se já tivermos rankings, senão IDLE para resetar a UI.
                        final_status = "COMPLETED" if self.rankings else "IDLE"
                        await asyncio.to_thread(
                            sovereign_service.rtdb.child("librarian_intelligence").update,
                            {"status": final_status, "updated_at": int(time.time() * 1000)}
                        )
                        logger.info(f"🛡️ [LIBRARIAN GUARD] Status resetado para {final_status} via Safety Shield.")
                except: pass

    async def _calculate_spring_potential(self, symbol: str) -> Dict[str, Any]:
        """
        [V110.165] MOLA AUDIT: Analisa o potencial de explosão pós-compressão.
        """
        try:
            # 1. Busca dados M30 (histórico de 15 dias aprox = 720 candles)
            last_ts = data_extractor.get_last_timestamp(symbol, "30")
            data_extractor.download_klines(symbol, "30", limit=720 if last_ts == 0 else 100, start_time=last_ts)
            
            conn = data_extractor.get_db_connection()
            c = conn.cursor()
            c.execute("SELECT close FROM klines WHERE symbol = ? AND interval = ? ORDER BY start_time DESC LIMIT 720", (symbol, "30"))
            closes_raw = [row[0] for row in c.fetchall()]
            conn.close()
            closes = list(reversed(closes_raw))
            
            if len(closes) < 120:
                return {"score": 0, "win_rate": 0, "avg_roi": 0}

            # 2. Identifica eventos de Mola
            spring_events = []
            import math
            def get_std_dev(data):
                if not data: return 0
                mean = sum(data) / len(data)
                variance = sum((x - mean) ** 2 for x in data) / len(data)
                return math.sqrt(variance)

            for i in range(100, len(closes) - 11):
                short = closes[i-20:i]
                long = closes[i-100:i]
                std_short = get_std_dev(short)
                std_long = get_std_dev(long)
                
                if std_long > 0 and (std_short / std_long < 0.4):
                    entry_price = closes[i]
                    max_future = max(closes[i+1:i+11])
                    min_future = min(closes[i+1:i+11])
                    
                    roi_long = (max_future - entry_price) / entry_price * 100 * 50
                    roi_short = (entry_price - min_future) / entry_price * 100 * 50
                    
                    best_roi = max(roi_long, roi_short)
                    spring_events.append(best_roi)

            if not spring_events:
                return {"score": 0, "win_rate": 0, "avg_roi": 0}

            # 3. Calcula métricas
            wins = [r for r in spring_events if r >= 100.0]
            win_rate = (len(wins) / len(spring_events)) * 100
            avg_roi = sum(spring_events) / len(spring_events)
            
            score = (win_rate * avg_roi) / 100
            
            return {
                "score": round(score, 2),
                "win_rate": round(win_rate, 1),
                "avg_roi": round(avg_roi, 1),
                "events_count": len(spring_events)
            }
        except Exception as e:
            logger.error(f"Error in spring audit for {symbol}: {e}")
            return {"score": 0, "win_rate": 0, "avg_roi": 0}

librarian_agent = LibrarianAgent()
