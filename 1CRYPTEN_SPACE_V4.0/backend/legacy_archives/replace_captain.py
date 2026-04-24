import os

target_path = r"c:\Users\spcom\Desktop\10D-3.0\1CRYPTEN_SPACE_V4.0\backend\services\agents\captain.py"
with open(target_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add active_tocaias to __init__
old_init = "self.trade_outcomes = {}  # {symbol: [list of 'W' or 'L']}"
new_init = "self.trade_outcomes = {}  # {symbol: [list of 'W' or 'L']}\n        self.active_tocaias = set()  # [V36.4] CONCURRENT TOCAIA TRACKER"
content = content.replace(old_init, new_init)

# 2. Extract boundaries
start_marker = "    async def monitor_signals(self):"
end_marker = "    async def monitor_active_positions_loop(self):"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Could not find boundaries!")
    exit(1)

new_methods = '''    async def monitor_signals(self):
        """
        [V36.4] CONCURRENT SNIPER MONITOR:
        Picks the best signals and manages concurrent trades.
        """
        self.is_running = True
        await sovereign_service.log_event("SNIPER", "Sniper System V36.4 CONCURRENT ONLINE. Tocaias assíncronas ativadas.", "SUCCESS")
        
        while self.is_running:
            try:
                # 0. Global Authorization Check
                from services.vault_service import vault_service
                from services.bybit_rest import bybit_rest_service
                allowed, reason = await vault_service.is_trading_allowed()
                if not allowed:
                    if not hasattr(self, "_last_block_log") or (time.time() - self._last_block_log) > 300:
                        logger.info(f"⏸️ SNIPER PAUSED: {reason}")
                        self._last_block_log = time.time()
                    await asyncio.sleep(5)
                    continue

                # Check available slots
                slots = await sovereign_service.get_active_slots()
                if bybit_rest_service.execution_mode == "PAPER":
                    occupied_count = len(bybit_rest_service.paper_positions)
                else:
                    occupied_count = sum(1 for s in slots if s.get("symbol"))
                
                free_slots = 4 - occupied_count
                
                if free_slots <= 0 or len(self.active_tocaias) >= free_slots:
                    if not hasattr(self, "_last_slot_fail_log") or (time.time() - self._last_slot_fail_log) > 60:
                        logger.info(f"🚫 SNIPER: Limite atingido. (Livres: {free_slots}, Tocaias Ativas: {len(self.active_tocaias)})")
                        self._last_slot_fail_log = time.time()
                    await asyncio.sleep(1)
                    continue

                from services.signal_generator import signal_generator
                while not hasattr(signal_generator, "signal_queue") or signal_generator.signal_queue is None:
                    await asyncio.sleep(1)
                
                try:
                    best_signal = await asyncio.wait_for(signal_generator.signal_queue.get(), timeout=10.0)
                except asyncio.TimeoutError:
                    continue
                    
                symbol = best_signal.get("symbol")
                if not symbol or symbol in self.active_tocaias:
                    continue
                    
                self.active_tocaias.add(symbol)
                logger.info(f"🎯 [V36.4] START TOCAIA: {symbol} ({len(self.active_tocaias)}/{free_slots} ativas)")
                asyncio.create_task(self._process_single_signal(best_signal))
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in Captain monitor loop: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(5)

    async def _process_single_signal(self, best_signal: dict):
        """[V36.4] Trabalhador Assíncrono para o Pullback Hunter e Needle Flip."""
        symbol = best_signal["symbol"]
        score = best_signal["score"]
        
        try:
            signal_layer = best_signal.get("layer", "MOMENTUM")
            strategy = "SWING"
            
            from services.signal_generator import signal_generator
            try:
                regime_data = await signal_generator.detect_market_regime(symbol)
                market_regime = regime_data.get('regime', 'TRANSITION')
            except Exception:
                market_regime = "TRANSITION"
                
            if signal_layer == "MOMENTUM":
                is_decorrelation = best_signal.get("indicators", {}).get("decorrelation_play", False)
                if is_decorrelation:
                    signal_layer = "SNIPER"
                    logger.info(f"🎯 [V31.0] DECORRELATION promovido: {symbol} ({score})")
                else:
                    allow_momentum = False
                    if market_regime == "RANGING" and score >= 85:
                        allow_momentum = True
                    from config import settings
                    if settings.BYBIT_EXECUTION_MODE == "PAPER" and score >= 80:
                        allow_momentum = True
                    if not allow_momentum:
                        logger.info(f"⏭️ {symbol} rejeitado: SCORE={score} em LAYER={signal_layer}")
                        await sovereign_service.update_signal_outcome(best_signal["id"], "MOMENTUM_BLOCKED")
                        return

            side = best_signal.get("side", "Buy")
            
            if market_regime == "RANGING":
                logger.info(f"🔄 [V33.0] REVERSE SNIPER SUSPENSO: Seguindo direção original {side} para {symbol}.")

            in_cooldown, remaining = await self.is_symbol_in_cooldown(symbol)
            if in_cooldown:
                if score >= 95:
                    logger.info(f"⚡ V12.5 ELITE BYPASS: {symbol} ignoring cooldown")
                else:
                    logger.info(f"⏱️ {symbol} no cooldown. Abortando.")
                    await sovereign_service.update_signal_outcome(best_signal["id"], "COOLDOWN_SKIP")
                    return

            consensus = await self._get_fleet_consensus(best_signal)
            if not consensus["approved"]:
                reason = consensus["reason"]
                logger.info(f"🚫 [FLEET] {symbol} REJEITADO: {reason}")
                await sovereign_service.update_signal_outcome(best_signal["id"], f"FLEET_REJECTED: {reason}")
                return
            
            fleet_intel = consensus["intel"]
            
            is_mean_rev = best_signal.get("is_mean_reversion", False)
            trap_exploited = best_signal.get("trap_exploited", False)
            
            if is_mean_rev or trap_exploited:
                logger.info(f"⚡ [OMNICHANNEL] {symbol} BYPASS PULLBACK HUNTER.")
                best_signal["indicators"]["pattern"] = "OMNICHANNEL"
                price_check = {"confirmed": True, "rejection_type": None, "adaptive_sl": 0, "max_drawdown_pct": 0}
            else:
                price_check = await self._validate_price_structure(symbol, side, signal_data=best_signal)
                if price_check["confirmed"]:
                    best_signal["indicators"]["pattern"] = "TOCAIA"
                
            if not price_check["confirmed"]:
                rejection = price_check.get("rejection_type", "UNKNOWN")
                logger.info(f"⏭️ [PULLBACK HUNTER] {symbol} REJEITADO: {rejection}")
                await sovereign_service.update_signal_outcome(best_signal["id"], f"FAKE_MOVE_{rejection}")
                return
                
            await sovereign_service.update_signal_outcome(best_signal["id"], "PRICE_STRUCTURE_OK")
            best_signal["adaptive_sl"] = price_check.get("adaptive_sl", 0)

            flip_confirmed = await self._wait_for_needle_flip(symbol, side, max_wait=10, signal_data=best_signal)
            if not flip_confirmed:
                logger.info(f"⏭️ [NEEDLE FLIP] {symbol} não confirmou exaustão CVD+Volume.")
                await sovereign_service.update_signal_outcome(best_signal["id"], "NEEDLE_FLIP_FAIL")
                return
                
            await sovereign_service.update_signal_outcome(best_signal["id"], "NEEDLE_FLIP_OK")
            logger.info(f"🎯 V36.4 PULLBACK ALVO PRONTO: {symbol}")
            await sovereign_service.update_signal_outcome(best_signal["id"], "PICKED")
            
            reasoning = best_signal.get("reasoning", "High Momentum")
            pensamento = f"V33.0 Pullback Hunter: Price Structure OK + Needle Flip OK. {reasoning} | Score: {score} | Fleet: {fleet_intel.get('sentiment', 'N/A')}"
            
            if is_mean_rev:
                pensamento = f"🧲 [REVERSÃO À MÉDIA] {symbol} MKT Direto. {reasoning} | Score: {score}"
            elif trap_exploited:
                pensamento = f"🦇 [TRAP EXPLOITATION] {symbol} Retail Hunter MKT. {reasoning} | Score: {score}"
            elif best_signal.get("is_reverse_sniper"):
                pensamento = f"🔄 REVERSE SNIPER (Fading): {pensamento}"

            norm_symbol_ac = normalize_symbol(symbol)
            sym_trades = self.daily_symbol_trades.get(norm_symbol_ac, {'count': 0, 'first_trade_at': 0})
            if time.time() - sym_trades.get('first_trade_at', 0) > 86400:
                sym_trades = {'count': 0, 'first_trade_at': time.time()}
            if sym_trades['count'] >= 3:
                logger.info(f"🚫 [ANTI-CONCENTRATION] {symbol} bloqueado (limite 3 trades/dia).")
                await sovereign_service.update_signal_outcome(best_signal["id"], "CONCENTRATION_BLOCK")
                return
                
            # VERIFICAR E TRAVAR SLOT no ÚLTIMO MILISSEGUNDO!
            slot_id = await bankroll_manager.can_open_new_slot(symbol=symbol)
            if not slot_id:
                logger.info(f"🚨 [V36.4] Tocaia finalizada para {symbol}, mas todos os slots foram roubados! Abortando.")
                await sovereign_service.update_signal_outcome(best_signal["id"], "SLOTS_FULL_LATE_REJECT")
                return
                
            order = await bankroll_manager.open_position(
                symbol=symbol,
                side=side,
                pensamento=pensamento,
                slot_type=strategy,
                signal_data=best_signal,
                target_slot_id=slot_id
            )
            
            if order:
                self.last_traded_symbol = symbol
                sym_trades['count'] += 1
                if sym_trades['first_trade_at'] == 0:
                    sym_trades['first_trade_at'] = time.time()
                self.daily_symbol_trades[norm_symbol_ac] = sym_trades
                logger.info(f"✅ SNIPER SHOT DEPLOYED: {symbol} (Slot {slot_id})")
            else:
                logger.warning(f"❌ SNIPER SHOT FAILED para {symbol}")

        except Exception as e:
            logger.error(f"Erro no processamento da Tocaia {symbol}: {e}")
        finally:
            self.active_tocaias.discard(symbol)
            logger.info(f"🏁 [TOCAIA ENCERRADA] {symbol} dispensado. (Restantes: {len(self.active_tocaias)})")

'''

new_content = content[:start_idx] + new_methods + content[end_idx:]

with open(target_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Successfully rewritten {target_path} blocks.")
