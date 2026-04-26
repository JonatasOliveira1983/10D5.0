import logging
import asyncio
import time

logger = logging.getLogger("AmbushAgent")

class AmbushAgent:
    """
    [V110.118] O Espião da Tocaia Refinada.
    Substitui a lógica matemática cega por entradas baseadas em:
    1. Retração Fibonacci (0.382 para tendências fortes, 0.5 para voláteis)
    2. Validação Exaustiva (CVD flow e RSI) no momento do toque.
    """
    def __init__(self):
        self.max_wait_seconds = 1800 # 30 min timeout para esfriar a Fibo 1H

    async def execute_ambush(self, symbol: str, side: str, signal_data: dict) -> dict:
        """
        Observa o mercado e decide o momento exato de executar o sinal na Tocaia.
        Retornos possíveis:
        - {"action": "TRIGGER", "reason": "...", "price": float}
        - {"action": "ABORT", "reason": "...", "price": float}
        - {"action": "TIMEOUT", "reason": "..."}
        """
        from services.signal_generator import signal_generator
        from services.bybit_ws import bybit_ws_service
        from services.redis_service import redis_service
        from services.agents.librarian import librarian_agent

        try:
            # 1. Calculando Zona de Retração Fibo
            # [V110.170] TF Adaptativo: Se for Blitz, usa 30m para maior precisão de bote rápido.
            is_blitz = signal_data.get("is_blitz") or signal_data.get("timeframe") == "30"
            tf_fibo = "30" if is_blitz else "60"
            
            fib = await signal_generator.get_fibonacci_levels(symbol, tf_fibo, 48)
            if not fib or "levels" not in fib:
                logger.warning(f"🥷 [AMBUSH-FAIL] Impossível calcular Fibonacci {tf_fibo} para {symbol}.")
                return {"action": "ABORT", "reason": "FAIL_FIBO_CALC"}

            lib_dna = await librarian_agent.get_asset_dna(symbol)
            vol_class = lib_dna.get("volatility_class", "TRENDING")

            fibo_levels = fib["levels"]
            
            # Dinâmica de agressividade conforme DNA do ativo
            if vol_class in ["EXTREME", "VOLATILE"]:
                ambush_target = fibo_levels.get("0.5", 0)
                zone_name = "Golden Zone (0.5)"
            else:
                ambush_target = fibo_levels.get("0.382", 0)
                zone_name = "Shallow Dip (0.382)"
            
            if ambush_target == 0:
                return {"action": "ABORT", "reason": "INVALID_FIBO_TARGET"}

            side_norm = side.lower()
            start_time = time.time()
            
            logger.info(f"🥷 [AMBUSH-WAIT] {symbol} {side} engatado. Volatilidade: {vol_class}. Alvo Tocaia: {ambush_target:.6f} {zone_name}.")

            is_retest_heavy = lib_dna.get("is_retest_heavy", False)
            sweep_detected = False
            
            while (time.time() - start_time) < self.max_wait_seconds:
                current_price = bybit_ws_service.get_current_price(symbol)
                if not current_price:
                    await asyncio.sleep(2)
                    continue

                # [V110.134] LOGICA SWEEP (SPRING HUNTER): 
                # Se o ativo é Retest Heavy, esperamos furar o alvo e VOLTAR (reclaim).
                if is_retest_heavy:
                    if not sweep_detected:
                        # Detecta se furou o alvo (fingimento)
                        if (side_norm == "buy" and current_price < ambush_target * 0.998) or \
                           (side_norm == "sell" and current_price > ambush_target * 1.002):
                            sweep_detected = True
                            logger.info(f"🦇 [SWEEP-DETECTED] {symbol} furou a Fibo. Aguardando Reclaim da estrutura...")
                        
                    # Se já detectou o sweep, aguarda a volta sólida
                    if sweep_detected:
                        reclaim_trigger = False
                        if side_norm == "buy" and current_price >= ambush_target:
                            reclaim_trigger = True
                        elif side_norm == "sell" and current_price <= ambush_target:
                            reclaim_trigger = True
                            
                        if reclaim_trigger:
                            # Validação final com CVD no Reclaim
                            cvd = await redis_service.get_cvd(symbol)
                            logger.info(f"🚀 [AMBUSH-RECLAIM] {symbol} recuperou o nível ({current_price:.6f})! Bote Wyckoff disparado. CVD: {cvd}")
                            return {"action": "TRIGGER", "reason": "WYCKOFF_RECLAIM", "price": current_price}
                
                # Lógica padrão de toque (para ativos Direct Pulse)
                else:
                    # [V110.151] Micro-Tocaia Tolerance (0.1% for Direct Pulse)
                    # Para evitar perder o bote se o preço chegar muito perto mas não tocar.
                    tolerance = ambush_target * 0.0010 if not is_retest_heavy else 0
                    
                    zone_reached = False
                    if side_norm == "buy":
                        if current_price <= (ambush_target + tolerance):
                            zone_reached = True
                    else: # sell
                        if current_price >= (ambush_target - tolerance):
                            zone_reached = True

                    if zone_reached:
                        # [V4.0] PACIÊNCIA DO SNIPER: Espera uma pequena 'absorção' ou rejeição no 1m
                        # Isso evita entrar "na frente do trem" e garante a violinada.
                        absorption = await self._check_entry_absorption(symbol, side_norm, current_price)
                        if not absorption["ready"]:
                            await asyncio.sleep(1)
                            continue

                        # 2. Avaliação de Exaustão (CVD) e Momento (RSI)
                        cvd = await redis_service.get_cvd(symbol)
                        rsi = bybit_ws_service.rsi_cache.get(symbol, 50.0)
                        
                        logger.info(f"🥷 [AMBUSH-ZONE] {symbol} detectou {absorption['reason']} ({current_price:.6f}). Flow -> CVD: {cvd}, RSI: {rsi:.1f}")

                        if side_norm == "buy":
                            if cvd < -150000:
                                logger.warning(f"🛑 [AMBUSH-ABORT] Faca caindo! {symbol} violou suporte com CVD Extremo ({cvd:.0f}). Abortando emboscada Long.")
                                return {"action": "ABORT", "reason": "CRITICAL_DUMP", "price": current_price}
                            
                            logger.info(f"🚀 [AMBUSH-TRIGGER] Absorção e Violinada confirmadas em {symbol}! Executando Bote Long.")
                            return {"action": "TRIGGER", "reason": f"DIP_ABSORBED_{absorption['reason']}", "price": current_price}
                            
                        else:
                            if cvd > 150000:
                                logger.warning(f"🛑 [AMBUSH-ABORT] Foguete subindo! {symbol} violou teto com CVD Extremo ({cvd:.0f}). Abortando emboscada Short.")
                                return {"action": "ABORT", "reason": "CRITICAL_PUMP", "price": current_price}

                            logger.info(f"🚀 [AMBUSH-TRIGGER] Rejeição e Violinada confirmadas em {symbol}! Executando Bote Short.")
                            return {"action": "TRIGGER", "reason": f"RALLY_ABSORBED_{absorption['reason']}", "price": current_price}

                    # [V110.150] BREAKOUT DETECTION (MODO STRIKE EMERGÊNCIAL)
                    # Se o preço não lambeu a fibo mas está rompendo o topo/fundo local com CVD explosivo
                    cvd_live = await redis_service.get_cvd(symbol)
                    if (side_norm == "buy" and cvd_live > 180000) or \
                       (side_norm == "sell" and cvd_live < -180000):
                        logger.info(f"⚡ [AMBUSH-BREAKOUT] {symbol} detectou explosão de CVD ({cvd_live:.0f}) sem recuo. Ativando Strike de Rompimento!")
                        return {"action": "TRIGGER", "reason": "VOLUME_BREAKOUT", "price": current_price}


                await asyncio.sleep(1)

            logger.warning(f"⏳ [AMBUSH-TIMEOUT] 30m esgotados para {symbol}. Fibo {ambush_target:.6f} não lamber.")
            return {"action": "TIMEOUT", "reason": "TIME_EXPIRED"}

        except Exception as e:
            logger.error(f"❌ [AMBUSH-ERROR] Falha na tocaia de {symbol}: {e}")
            return {"action": "ABORT", "reason": "SYSTEM_ERROR"}

    async def _check_entry_absorption(self, symbol: str, side: str, current_price: float) -> dict:
        """
        [V4.0] PACIÊNCIA DO SNIPER: Valida se houve uma 'violinada' e rejeição.
        Analisa as últimas velas de 1m para confirmar pavio e exaustão.
        """
        from services.bybit_ws import bybit_ws_service
        
        klines = bybit_ws_service.get_klines(symbol, "1")
        if not klines or len(klines) < 2:
            return {"ready": True, "reason": "NO_DATA_BYPASS"} # Fallback se não tiver dados
        
        last_k = klines[-1] # Vela atual (em formação)
        
        # Lógica de Absorção (Vela 1m com pavio significativo ou reversão)
        high = float(last_k.get('high', 0))
        low = float(last_k.get('low', 0))
        open_p = float(last_k.get('open', 0))
        close_p = float(last_k.get('close', 0))
        
        if side == "buy":
            # Rejeição de Fundo: Preço furou a zona mas está fechando acima da abertura ou com pavio inferior longo
            lower_wick = min(open_p, close_p) - low
            body = abs(close_p - open_p)
            # Se pavio inferior > 1.2x corpo, ou se já está revertendo (close > open)
            if lower_wick > body * 1.2 or close_p > open_p:
                return {"ready": True, "reason": "ABSORPTION_LONG"}
        else:
            # Rejeição de Topo: Pavio superior longo ou fechamento negativo
            upper_wick = high - max(open_p, close_p)
            body = abs(close_p - open_p)
            if upper_wick > body * 1.2 or close_p < open_p:
                return {"ready": True, "reason": "ABSORPTION_SHORT"}
                
        return {"ready": False}

ambush_agent = AmbushAgent()
