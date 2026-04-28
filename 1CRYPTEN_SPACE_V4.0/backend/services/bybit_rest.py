# -*- coding: utf-8 -*-
import asyncio
import logging
import time
import json
import os
from datetime import datetime, timezone
from services.time_utils import get_br_iso_str
from typing import List, Dict, Any
from pybit.unified_trading import HTTP
from config import settings
from services.resilience import with_circuit_breaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BybitREST")

class BybitREST:
    def __init__(self):
        self._session = None
        self.category = settings.BYBIT_CATEGORY
        self.time_offset = 0
        self.is_initialized = False
        
        # Paper Trading State
        self.execution_mode = settings.BYBIT_EXECUTION_MODE # "REAL" or "PAPER"
        self.paper_balance = settings.BYBIT_SIMULATED_BALANCE
        self.paper_positions = [] # List of dicts matching Bybit schema
        self.paper_moonbags = [] # [V110.0] List of emancipated trades in Paper Mode
        self.paper_orders_history = [] 
        self._paper_engine_task = None
        self._instrument_cache = {} # Cache for tickSize and stepSize
        self.last_balance = 0.0 # V5.2.4.6: Cache for non-blocking health checks
        # [V96.5] Path fix for Paper Mode persistence
        base_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(base_dir) # One level up from services/
        self.PAPER_STORAGE_FILE = os.path.join(backend_dir, "paper_storage.json")
        self._last_paper_load_time = 0
        
        # V5.3.4: Closure Idempotency Shield
        self.pending_closures = set()
        # V5.4.0: Distributed Lock via RedisService
        from services.redis_service import redis_service
        self.redis = redis_service
        
        # [V43.0] Position Mode Cache (Hedge vs One-Way)
        self._position_mode_cache = {} # { symbol: mode_int }
        self.emancipating_symbols = set() # { symbol }
        self._http_semaphore = asyncio.Semaphore(10)
        self._paper_save_lock = asyncio.Lock() # [V110.23.2] Concurrency Shield for Paper Persistence
        self.is_ready = False # [V110.25.0] Ready flag for sync loop
        
        # [V43.2] Cache for Elite Pairs to prevent API saturation
        self._elite_cache = []
        self._elite_cache_time = 0
        self._elite_cache_ttl = 900 # 15 minutes

    async def _load_paper_state(self):
        """[V110.23.5] Global Loader - loads paper positions and balance from Firestore. Resilient to Cloud Run restarts."""
        if self.execution_mode != "PAPER": return
        try:
            from services.sovereign_service import sovereign_service
            data = await sovereign_service.get_paper_state()
            
            if data:
                self.paper_positions = [p for p in data.get("positions", []) if "FARTCOIN" not in p.get("symbol", "")]
                self.paper_moonbags = [p for p in data.get("moonbags", []) if "FARTCOIN" not in p.get("symbol", "")]
                self.paper_balance = data.get("balance", settings.BYBIT_SIMULATED_BALANCE)
                self.paper_orders_history = data.get("history", [])
                self._last_paper_load_time = time.time()
                # Apenas loga se houver algo ativo para reduzir ruído
                if self.paper_positions or self.paper_moonbags:
                    logger.info(f"📂 [PAPER] State Synced: {len(self.paper_positions)} Pos | {len(self.paper_moonbags)} Moons | ${self.paper_balance:.2f}")

                # [V110.28.5] Auto-Healing: Sincronia ativa com o Vault Real (Firestore)
                # Garante que se uma Moonbag existe no Vault mas não na RAM, ela seja adotada.
                if hasattr(sovereign_service, "get_all_moonbags"):
                    vault_moons = await sovereign_service.get_all_moonbags()
                    if vault_moons:
                        ram_symbols = {m.get("symbol") for m in self.paper_moonbags}
                        for v_moon in vault_moons:
                            symbol = v_moon.get("symbol")
                            if symbol and symbol not in ram_symbols:
                                logger.warning(f"🚑 [AUTO-ADOPT] Ordem órfã detectada no Vault: {symbol}. Adotando para o motor.")
                                # Adaptar schema Firestore para schema RAM do BybitREST
                                pos_obj = {
                                    "symbol": symbol,
                                    "side": v_moon.get("side", "Buy"),
                                    "size": str(v_moon.get("qty", 0)),
                                    "avgPrice": str(v_moon.get("entry_price", 0)),
                                    "leverage": str(v_moon.get("leverage", 50)),
                                    "status": "EMANCIPATED",
                                    "stopLoss": str(v_moon.get("current_stop", 0)),
                                    "takeProfit": "0",
                                    "is_paper": True,
                                    "entry_margin": (float(v_moon.get("qty", 10)) * float(v_moon.get("entry_price", 0))) / float(v_moon.get("leverage", 50)),
                                    "opened_at": v_moon.get("opened_at", time.time())
                                }
                                self.paper_moonbags.append(pos_obj)
                
                # [V110.61] AMNESIA-GUARD: Auto-Recovery de Slots Tativos (PAPER)
                # Se existem ordens nos slots ativos do Firestore que NÃO estão na memória local,
                # nós as restauramos para evitar a purga prematura pelo Ghostbuster.
                try:
                    firestore_slots = await sovereign_service.get_active_slots(force_refresh=True)
                    if firestore_slots:
                        local_symbols = {p.get("symbol") for p in self.paper_positions}
                        for f_slot in firestore_slots:
                            symbol = f_slot.get("symbol")
                            if symbol and "FARTCOIN" in symbol:
                                continue # FARTCOIN is dead, never recover it
                            if symbol and symbol not in local_symbols:
                                logger.warning(f"🚑 [V110.61 AMNESIA-GUARD] Recuperando ordem órfã do Firestore: {symbol}")
                                # Reconstuir objeto de posição Paper compatível com Bybit v5 Schema Fake
                                recovered_pos = {
                                    "symbol": symbol,
                                    "side": f_slot.get("side", "Buy"),
                                    "size": str(f_slot.get("qty", 0)),
                                    "avgPrice": str(f_slot.get("entry_price", 0)),
                                    "leverage": str(f_slot.get("leverage", 50)),
                                    "status": "RECOVERED",
                                    "stopLoss": str(f_slot.get("current_stop", 0)),
                                    "takeProfit": str(f_slot.get("target_price", 0)),
                                    "opened_at": f_slot.get("opened_at", time.time()),
                                    "is_paper": True,
                                    "entry_margin": f_slot.get("entry_margin", 0)
                                }
                                self.paper_positions.append(recovered_pos)
                except Exception as recovery_error:
                    logger.error(f"⚠️ [V110.61] Falha no Amnesia-Guard: {recovery_error}")

            else:
                # Silencioso se estiver vazio para não poluir o Cloud Run
                self.paper_balance = settings.BYBIT_SIMULATED_BALANCE
                self._last_paper_load_time = time.time()
        except Exception as e:
            logger.error(f"❌ [PAPER] Failed to load global state: {e}")

    async def _save_paper_state(self):
        """[V110.23.5] Saves paper positions and balance to Firestore for global persistence."""
        if self.execution_mode != "PAPER": return
        async with self._paper_save_lock:
            try:
                from services.sovereign_service import sovereign_service
                data = {
                    "positions": self.paper_positions,
                    "moonbags": self.paper_moonbags,
                    "balance": self.paper_balance,
                    "history": self.paper_orders_history[-50:] # Keep last 50 only
                }
                await sovereign_service.update_paper_state(data)
                # logger.debug("💾 [V110.23.5 PAPER] Global State saved to Firestore.")
            except Exception as e:
                logger.error(f"❌ [PAPER] Failed to save global state: {e}")

    def normalize_symbol(self, symbol: str) -> str:
        """
        [V6.0] Robust Mapping: Standardizes symbols for Bybit V5 API.
        Strips .P suffix, ensures upper case, and prevents common mapping errors.
        """
        if not symbol: return ""
        norm = symbol.strip().upper()
        if norm.endswith(".P"):
            norm = norm[:-2]
        
        # Security Guard: Ensure it ends with USDT (or USDC)
        if not (norm.endswith("USDT") or norm.endswith("USDC")):
            # Fallback: if it's just 'BTC', return 'BTCUSDT'
            if norm: norm = f"{norm}USDT"
            
        return norm

    def _strip_p(self, symbol: str) -> str:
        """Standardizes symbols for Bybit API calls."""
        return self.normalize_symbol(symbol)

    async def initialize(self):
        """Inicialização assíncrona do motor Paper."""
        try:
            # [V110.29.0] Factory Reset Protocol: Se ativado, limpa tudo no boot
            if getattr(settings, "FACTORY_RESET_V110", False):
                logger.warning("☣️ [FACTORY-RESET] Iniciando purgação atômica (V110.29.0)...")
                self.paper_moonbags = []
                self.paper_positions = []
                self.paper_balance = settings.BYBIT_SIMULATED_BALANCE
                if os.path.exists(self.PAPER_STORAGE_FILE):
                    os.remove(self.PAPER_STORAGE_FILE)
                    logger.warning(f"🗑️ [FACTORY-RESET] Arquivo de estado deletado: {self.PAPER_STORAGE_FILE}")
                
                # Sincroniza limpo com RTDB/Firestore imediatamente
                from services.sovereign_service import sovereign_service
                await self._save_paper_state()
                if hasattr(sovereign_service, "update_bankroll"):
                    await sovereign_service.update_bankroll(self.paper_balance)
                logger.warning(f"✅ [FACTORY-RESET] Sistema purificado e balanceado em ${self.paper_balance:.2f}.")
                return # Pula o carregamento de estado normal
        except Exception as e:
            logger.error(f"❌ [FACTORY-RESET] Falha crítica na purgação: {e}")

        if self.is_initialized:
            return

        # [V110.175] AUTO-PAPER SHIELD: Se não houver chaves, força modo PAPER para evitar travamento
        if not settings.BYBIT_API_KEY or "sua_chave" in settings.BYBIT_API_KEY.lower():
            logger.warning("⚠️ [AUTO-PAPER] Chaves de API ausentes. Forçando modo PAPER para execução simulada.")
            self.execution_mode = "PAPER"
        
        # Create a temporary session to fetch server time
        temp_session = HTTP(testnet=settings.BYBIT_TESTNET)
        try:
            local_start = int(time.time() * 1000)
            server_time_resp = await asyncio.to_thread(temp_session.get_server_time)
            local_end = int(time.time() * 1000)
            
            # Compensation for RTT (Round Trip Time)
            rtt = local_end - local_start
            server_time = int(server_time_resp.get("result", {}).get("timeSecond", 0)) * 1000
            if server_time == 0: 
                server_time = int(int(server_time_resp.get("result", {}).get("timeNano", 0)) / 1000000)
            
            if server_time > 0:
                # server_time is likely at (local_start + rtt/2)
                self.time_offset = server_time - (local_start + rtt // 2)
                logger.info(f"Bybit Time Sync (RTT Comp): Offset detected as {self.time_offset}ms. RTT: {rtt}ms. Applying patch...")
                
                # Monkeypatch pybit's internal helper to use synced time
                import pybit._helpers as pybit_helpers
                _orig_time = time.time
                def synced_timestamp():
                    # Intentionally add a small buffer (500ms) to avoid 'too far in past' vs 'too far in future' race
                    return int((_orig_time() + (self.time_offset / 1000.0)) * 1000)
                
                pybit_helpers.generate_timestamp = synced_timestamp
                logger.info("Bybit Time Patch applied successfully.")
            
            # [V110.23.5] PAPER STATE RECOVERY: Ensure state is loaded from Firestore BEFORE sync loop
            if self.execution_mode == "PAPER":
                logger.info("📂 [V110.23.5] PAPER ENGINE: Loading persistent state from Firestore...")
                await self._load_paper_state()

        except Exception as e:
            logger.error(f"Failed to sync time with Bybit: {e}")

        # Create the actual session
        self._session = HTTP(
            testnet=settings.BYBIT_TESTNET,
            api_key=settings.BYBIT_API_KEY.strip() if settings.BYBIT_API_KEY else None,
            api_secret=settings.BYBIT_API_SECRET.strip() if settings.BYBIT_API_SECRET else None,
            recv_window=30000,
        )
        self.is_initialized = True
        logger.info("BybitREST: Session initialized.")
        
        # [V53.6] Load Paper State on startup (Global Firestore Sync)
        if self.execution_mode == "PAPER":
            await self._load_paper_state()
            
        self.is_ready = True
        logger.info("BybitREST: Session and state initialized.")


    @property
    def session(self):
        """Returns the Bybit HTTP session. Ensure initialize() was called before use for best results."""
        if self._session is None:
            # Fallback for synchronous calls, though initialize() is preferred
            self._session = HTTP(
                testnet=settings.BYBIT_TESTNET,
                api_key=settings.BYBIT_API_KEY.strip() if settings.BYBIT_API_KEY else None,
                api_secret=settings.BYBIT_API_SECRET.strip() if settings.BYBIT_API_SECRET else None,
                recv_window=30000,
            )
        return self._session
    async def get_elite_focus_pairs(self):
        """
        [V5.6] ESTRATÉGIA DE FOCO 20: 
        Retorna os Top 20 pares de Elite + qualquer par que tenha uma Moonbag ativa.
        Isso garante processamento ultra-rápido e foco total no capital investido.
        """
        try:
            # 1. Obter Top 20 do Bibliotecário (ou fallback de volume)
            from services.agents.librarian import librarian_agent
            elite_base = []
            if librarian_agent.rankings:
                elite_base = [r["symbol"] for r in librarian_agent.rankings[:20]]
                logger.info(f"🏆 [ELITE-FOCUS] {len(elite_base)} pares de Elite (Top 20) detectados.")
            else:
                # Fallback: Top 20 por volume
                all_candidates = await self.get_elite_50x_pairs()
                elite_base = all_candidates[:20]
                logger.info(f"📡 [ELITE-COLD] Usando fallback de volume para Top 20.")

            # 2. Obter símbolos de Moonbags ativas (Swing Trades)
            # No modo PAPER, pegamos da memória. No REAL, pegamos do Vault/Bybit.
            active_moon_symbols = set()
            if self.execution_mode == "PAPER":
                active_moon_symbols = {p["symbol"] for p in self.paper_moonbags}
            else:
                # Em modo REAL, as posições com status de EMANCIPATED ou tags específicas no Vault
                # Por simplicidade e segurança, pegamos todos os pares com posição aberta que não estão no elite_base
                active_positions = await self.get_active_positions()
                active_moon_symbols = {p["symbol"] for p in active_positions}

            # 3. União dos conjuntos para evitar duplicatas
            final_set = set(elite_base) | active_moon_symbols
            final_list = list(final_set)
            
            logger.info(f"🎯 [SNIPER-RADAR] Monitorando {len(final_list)} ativos (Top 20 + {len(active_moon_symbols - set(elite_base))} Moonbags extras).")
            return final_list
            
        except Exception as e:
            logger.error(f"Erro ao obter pares de Elite Dinâmicos: {e}")
            return ["BTCUSDT.P", "ETHUSDT.P", "SOLUSDT.P"]

    async def get_elite_50x_pairs(self):
        """
        🚀 REFINAMENTO ESTRATÉGICO V6.0: Escaneia pares com alavancagem >= 50x.
        [V110.173] Reduzido para Top 40 para maximizar foco e precisão.
        """
        now = time.time()
        if self._elite_cache and (now - self._elite_cache_time < self._elite_cache_ttl):
            return self._elite_cache

        try:
            logger.info("BybitREST: Fetching Elite 50x Instruments (Sniper Strategy)...")
            candidates = {}
            cursor = ""
            while True:
                params = {"category": "linear", "limit": 1000}
                if cursor: params["cursor"] = cursor
                instr_resp = await asyncio.to_thread(self.session.get_instruments_info, **params)
                instr_list = instr_resp.get("result", {}).get("list", [])
                for info in instr_list:
                    symbol = info.get("symbol")
                    if not symbol or not symbol.endswith("USDT"): continue
                    if symbol in settings.ASSET_BLOCKLIST: continue
                    max_lev = float(info.get("leverageFilter", {}).get("maxLeverage", 0))
                    if max_lev >= 50.0:
                        candidates[symbol] = info
                cursor = instr_resp.get("result", {}).get("nextPageCursor")
                if not cursor: break
            
            tickers_resp = await asyncio.to_thread(self.session.get_tickers, category="linear")
            ticker_list = tickers_resp.get("result", {}).get("list", [])
            final_candidates = []
            for t in ticker_list:
                sym = t.get("symbol")
                if sym in candidates:
                    turnover = float(t.get("turnover24h", 0))
                    final_candidates.append({"symbol": sym, "turnover": turnover})
            
            final_candidates.sort(key=lambda x: x["turnover"], reverse=True)
            # [V110.173] Foco reduzido de 100 para 40 pares para precisão extrema
            # [V4.2] Radar Blindage will handle the final filtering, but we keep this as a sane fallback.
            final_symbols = [f"{x['symbol']}.P" for x in final_candidates][:40]
            
            logger.info(f"BybitREST: Mass Sniper Elite Scan Successful. Monitoring Top {len(final_symbols)} pairs.")
            self._elite_cache = final_symbols
            self._elite_cache_time = now
            return final_symbols
        except Exception as e:
            logger.error(f"Error in Elite 50x scan: {e}")
            return []

    def get_top_200_usdt_pairs(self):
        """Deprecated: Use get_elite_50x_pairs for Sniper Protocol."""
        return self.get_elite_50x_pairs()

    @with_circuit_breaker(breaker_name="bybit_rest_public", fallback_return=0.0)
    async def get_wallet_balance(self):
        """Fetches the total equity from the Bybit account (UNIFIED or CONTRACT)."""
        # logger.info(f"[DEBUG] get_wallet_balance called. Mode: {self.execution_mode}")
        if self.execution_mode == "PAPER":
             # Calculate unrealized PNL from active paper positions to show dynamic equity
             unrealized_pnl = 0.0
             # Note: Accurate unrealized PNL requires fetching current prices. 
             # For performance, we might just return static balance + realized, 
             # OR realistically we should update it.
             # Ideally bankroll manager handles this via slots PNL, but here we return raw wallet balance.
             return self.paper_balance

        async with self._http_semaphore:
            try:
                # Try UNIFIED first
                logger.info("Fetching balance (UNIFIED)...")
                try:
                    # V5.2.4.3: Added 10s timeout
                    response = await asyncio.wait_for(asyncio.to_thread(self.session.get_wallet_balance, accountType="UNIFIED"), timeout=10.0)
                    result = response.get("result", {}).get("list", [{}])[0]
                    equity = float(result.get("totalEquity", 0))
                    logger.info(f"UNIFIED Equity: {equity}")
                    self.last_balance = equity # V5.2.4.6: Update cache
                    if equity > 0: return equity
                except Exception as ue: 
                    logger.warning(f"UNIFIED balance fetch failed: {ue}")
                
                # Try CONTRACT if UNIFIED fails or is 0
                logger.info("Fetching balance (CONTRACT)...")
                # V5.2.4.3: Added 10s timeout
                response = await asyncio.wait_for(asyncio.to_thread(self.session.get_wallet_balance, accountType="CONTRACT"), timeout=10.0)
                result = response.get("result", {}).get("list", [{}])[0]
                coins = result.get("coin", [])
                usdt_coin = next((c for c in coins if c.get("coin") == "USDT"), {})
                equity = float(usdt_coin.get("equity", 0))
                logger.info(f"CONTRACT Equity: {equity}")
                self.last_balance = equity # V5.2.4.6: Update cache
                return equity
            except Exception as e:
                logger.error(f"Error fetching wallet balance: {e}")
                return self.last_balance # V5.2.4.6: Return cached on error

    @with_circuit_breaker(breaker_name="bybit_rest_private", fallback_return=[])
    async def get_active_positions(self, symbol: str = None):
        """Fetches currently open linear positions (Real or Simulated)."""
        if self.execution_mode == "PAPER":
            combined = self.paper_positions + self.paper_moonbags
            if symbol:
                norm_symbol = self._strip_p(symbol).upper()
                return [p for p in combined if p["symbol"].upper() == norm_symbol]
            return combined


        async with self._http_semaphore:
            try:
                params = {"category": self.category, "settleCoin": "USDT"}
                if symbol: params["symbol"] = symbol
                
                # V5.2.4.3: Added 10s timeout
                response = await asyncio.wait_for(asyncio.to_thread(self.session.get_positions, **params), timeout=10.0)
                pos_list = response.get("result", {}).get("list", [])
                # Filter for positions with size > 0
                active = [p for p in pos_list if float(p.get("size", 0)) > 0]
                return active
            except Exception as e:
                logger.error(f"Error fetching positions: {e}")
                return []

    @with_circuit_breaker(breaker_name="bybit_rest_public", fallback_return={"retCode": -1, "result": {"list": []}})
    async def get_tickers(self, symbol: str = None):
        """
        Fetches ticker data with [V6.0] Exact Match Protection.
        If a symbol is provided, only that exact symbol's data is returned.
        [V12.7] Added 2s cache for global fetches to avoid bandwidth blocks.
        """
        async with self._http_semaphore:
            try:
                # Check Cache for global scan
                if symbol is None:
                    now = time.time()
                    if hasattr(self, "_global_ticker_cache") and (now - self._global_ticker_cache_time < 2.0):
                        return self._global_ticker_cache
                
                api_symbol = self.normalize_symbol(symbol)
                # [V6.1.1] HOTFIX (AttributeError): Removed non-existent is_scanning_phase check.
                # Strictly blocking None to prevent heavy API load UNLESS it's the 2s window.
                # if symbol is None:
                #    logger.warning("[PERFORMANCE] get_tickers called with None symbol! BLOCKED to save bandwidth.")
                #    return {"retCode": 0, "result": {"list": []}}
    
                params = {"category": self.category}
                if api_symbol: 
                    params["symbol"] = api_symbol
                else:
                    # [V6.1] Optimization: If symbol is None, checking if we really want ALL tickers.
                    # [V12.7] We only allow this every 2 seconds.
                    logger.info("[PERFORMANCE] get_tickers: Refreshing global market data (2s Cache).")
                
                # V5.2.4.3: Added 5s timeout -> Increased to 10s for stability
                response = await asyncio.wait_for(asyncio.to_thread(self.session.get_tickers, **params), timeout=10.0)
                
                # Update Cache if global
                if symbol is None:
                    self._global_ticker_cache = response
                    self._global_ticker_cache_time = time.time()
    
                # [V6.0] Robust Mapping verification
                if api_symbol:
                    ticker_list = response.get("result", {}).get("list", [])
                    
                    # Check 1: Did we get anything?
                    if not ticker_list:
                        logger.warning(f"⚠️ [BYBIT] No ticker found for exactly {api_symbol}")
                        return response
                    
                    # Check 2: Exact Match Verification
                    # Bybit can return the whole list if symbol is slightly off or if they change API behavior
                    actual_symbol = ticker_list[0].get("symbol")
                    if actual_symbol != api_symbol:
                        logger.error(f"🚨 [TICKER COLLISION] Requested {api_symbol} but Bybit returned {actual_symbol}!")
                        # Invalidate list to prevent bankroll.py from using wrong price
                        response["result"]["list"] = [] 
                    elif len(ticker_list) > 1:
                        logger.warning(f"⚠️ [TICKER AMBIGUITY] Multiple results for {api_symbol}. Filtering for exact match.")
                        response["result"]["list"] = [t for t in ticker_list if t.get("symbol") == api_symbol]
                
                return response
            except Exception as e:
                logger.error(f"Error fetching tickers for {symbol}: {e}")
                return {}

    @with_circuit_breaker(breaker_name="bybit_rest_public", fallback_return={})
    async def get_instrument_info(self, symbol: str):
        """Fetches precision and lot size filtering for a symbol with local caching."""
        async with self._http_semaphore:
            try:
                api_symbol = self._strip_p(symbol)
                if api_symbol in self._instrument_cache:
                    return self._instrument_cache[api_symbol]
    
                # V5.2.4.3: Added 5s timeout
                response = await asyncio.wait_for(asyncio.to_thread(self.session.get_instruments_info, category="linear", symbol=api_symbol), timeout=5.0)
                info = response.get("result", {}).get("list", [{}])[0]
                
                if info:
                    self._instrument_cache[api_symbol] = info
                
                return info
            except Exception as e:
                logger.error(f"Error fetching instrument info for {symbol}: {e}")
                return {}

    async def round_price(self, symbol: str, price: float) -> float:
        """
        Rounds the price to the nearest tickSize allowed by Bybit.
        Essential for avoiding 10001 errors and ensuring 'Maker' precision.
        """
        return await self.format_precision(symbol, price)

    async def format_precision(self, symbol: str, price: float) -> float:
        """
        [V5.2.5] Precision Engine: Normaliza preços baseado no tickSize real da Bybit.
        """
        if price <= 0: return price
        
        info = await self.get_instrument_info(symbol)
        tick_size_str = info.get("priceFilter", {}).get("tickSize")
        
        if not tick_size_str:
            return price # Fallback
            
        from decimal import Decimal, ROUND_HALF_UP
        tick_size = Decimal(tick_size_str)
        price_dec = Decimal(str(price))
        
        # Formula: round(price / tickSize) * tickSize
        rounded = (price_dec / tick_size).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * tick_size
        
        # Normalize to remove trailing zeros and convert back to float
        return float(rounded.normalize())

    async def round_qty(self, symbol: str, qty: float) -> float:
        """
        [V53.0] Precisão de Quantidade: Normaliza quantidades baseado no qtyStep da Bybit.
        """
        if qty <= 0: return qty
        
        info = await self.get_instrument_info(symbol)
        qty_step_str = info.get("lotSizeFilter", {}).get("qtyStep")
        
        if not qty_step_str:
            return qty
            
        from decimal import Decimal, ROUND_HALF_UP
        qty_step = Decimal(qty_step_str)
        qty_dec = Decimal(str(qty))
        
        rounded = (qty_dec / qty_step).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * qty_step
        return float(rounded.normalize())



    @with_circuit_breaker(breaker_name="bybit_rest_private", fallback_return={"retCode": -1, "retMsg": "Circuit Breaker Active"})
    async def set_leverage(self, symbol: str, leverage: int = 50):
        """
        🚀 V12.0: Ajusta a alavancagem para o símbolo antes de abrir a ordem.
        Garante que a margem calculada corresponda à alavancagem real na Bybit.
        """
        api_symbol = self._strip_p(symbol)
        
        if self.execution_mode == "PAPER":
            logger.info(f"[PAPER] Setting leverage for {api_symbol} to {leverage}x")
            # Update leverage in existing paper position if it exists
            pos = next((p for p in self.paper_positions if p["symbol"] == api_symbol), None)
            if pos:
                pos["leverage"] = str(leverage)
                await self._save_paper_state()
            return {"retCode": 0, "result": {}}

        try:
            # Use synchronize thread for pybit call
            response = await asyncio.to_thread(self.session.set_leverage,
                category=self.category,
                symbol=api_symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            
            # Note: Bybit returns 110043 if leverage is already set to the same value
            if response.get("retCode") == 110043:
                logger.debug(f"Leverage for {symbol} already at {leverage}x.")
                return response
                
            logger.info(f"Leverage set for {symbol} to {leverage}x: {response}")
            return response
        except Exception as e:
            # Common error: "leverage not modified" or similar, we log but don't block
            logger.warning(f"Failed to set leverage for {symbol}: {e}")
            return {"retCode": -1, "retMsg": str(e)}

    @with_circuit_breaker(breaker_name="bybit_rest_private", fallback_return=None)
    async def place_atomic_order(self, symbol: str, side: str, qty: float, sl_price: float, tp_price: float = None, slot_id: int = 0, leverage: float = 50, **kwargs):
        """
        Sends a Market Order with Stop Loss in the same request.
        """
        api_symbol = self._strip_p(symbol)
        if self.execution_mode == "PAPER":
            logger.info(f"[PAPER] Simulating Atomic Order: {side} {qty} {symbol} @ MARKET")
            # 1. Get current price for entry simulation
            try:
                # Need to fetch real price to simulate entry
                ticker = await asyncio.to_thread(self.session.get_tickers, category="linear", symbol=api_symbol)
                last_price = float(ticker.get("result", {}).get("list", [{}])[0].get("lastPrice", 0))
                
                if last_price == 0:
                    raise Exception("Could not fetch price for paper execution")

                # [V110.65] AMBUSH ENTRY: Usa zona de lambida para entrada mais precisa
                # Se o sinal tem um ambush_price calculado e o preço já está na zona, 
                # entramos no ambush price (melhor entry = mais espaço pro Moonbag)
                ambush_price = kwargs.get("ambush_price", 0)
                if ambush_price > 0:
                    side_norm = side.lower()
                    # Verifica se o preço atual já alcançou ou ultrapassou a zona de lambida
                    is_in_ambush_zone = (side_norm == "buy" and last_price <= ambush_price) or \
                                        (side_norm == "sell" and last_price >= ambush_price)
                    if is_in_ambush_zone:
                        logger.info(f"🎯 [V110.65 AMBUSH] {symbol} Entrada na Zona de Lambida: ${ambush_price:.6f} (Market: ${last_price:.6f})")
                        last_price = ambush_price  # Simula entry no ambush price
                    else:
                        # Preço não chegou na zona, mas como é Paper e queremos testar,
                        # aceitamos entry no mercado com log de aviso
                        logger.info(f"📍 [V110.65 AMBUSH] {symbol} Market entry ${last_price:.6f} (Ambush zone: ${ambush_price:.6f} não alcançada)")


                # [V110.256] UNIFIED GENESIS: genesis_id ÚNICO é gerado SOMENTE no bankroll.py
                # após receber o orderId desta resposta. Não geramos aqui para evitar duplicata.
                # O paper_position NÃO carrega genesis_id — ele será injetado via update_slot().
                
                # orderId único baseado em timestamp para garantir unicidade por ordem
                paper_order_id = f"PAPER-{api_symbol}-{int(time.time() * 1000)}"
                
                # 2. Create Position Object (Mocking Bybit Schema)
                new_position = {
                    "symbol": api_symbol, # Normalized
                    "side": side,
                    "size": str(qty),
                    "avgPrice": str(last_price),
                    "leverage": str(leverage),
                    "stopLoss": str(sl_price),
                    "takeProfit": str(tp_price) if tp_price else "",
                    "entry_margin": str((qty * last_price) / leverage),
                    "createdTime": str(int(time.time() * 1000)),
                    "opened_at": time.time(), # [V84.1] Absolute start
                    "maestria_guard_active": False, # [V84.1] Start clean
                    "slot_id": slot_id, # [V96.9] Track slot for history registration
                    "order_id": paper_order_id  # [V110.256] Ancora real com o orderId único
                    # genesis_id NÃO é definido aqui — bankroll.py define após receber o orderId
                }
                
                # Check if position already exists (Hedge mode not supported in paper simple impl, assuming One-Way)
                existing = next((p for p in self.paper_positions if p["symbol"] == api_symbol), None)
                if existing:
                    logger.warning(f"[PAPER] Overwriting existing position for {api_symbol} (Simpler than averaging).")
                    self.paper_positions.remove(existing)
                
                self.paper_positions.append(new_position)
                logger.info(f"[PAPER] Position Created: {api_symbol} Entry={last_price} | OrderId={paper_order_id}")
                await self._save_paper_state()
                
                # [V110.256] Retorna o orderId único — bankroll.py usará ele para gerar genesis_id
                return {
                    "retCode": 0,
                    "result": {"orderId": paper_order_id, "orderLinkId": paper_order_id}
                }

            except Exception as e:
                logger.error(f"[PAPER] Failed to place simulated order: {e}")
                return None

        try:
            # [V5.2.5] Precision Engine: Normalizar preços antes do envio
            sl_final = await self.format_precision(symbol, sl_price)
            tp_final = await self.format_precision(symbol, tp_price) if tp_price else None

            # [V43.0] Hedge Mode support for order entry
            positionIdx = 0
            if self.execution_mode == "REAL":
                # Detect mode if not cached
                if api_symbol not in self._position_mode_cache:
                    try:
                        resp = await asyncio.to_thread(self.session.get_position_infos, category=self.category, symbol=api_symbol)
                        pos_list = resp.get("result", {}).get("list", [])
                        if pos_list:
                            # If we get multiple positions for one symbol, it's Hedge Mode
                            if len(pos_list) > 1:
                                self._position_mode_cache[api_symbol] = "HEDGE"
                            else:
                                self._position_mode_cache[api_symbol] = "ONE_WAY"
                    except Exception as pe:
                        logger.warning(f"Could not detect position mode for {symbol}: {pe}")
                
                mode = self._position_mode_cache.get(api_symbol, "ONE_WAY")
                if mode == "HEDGE":
                    positionIdx = 1 if side == "Buy" else 2
                else:
                    positionIdx = 0

            order_params = {
                "category": self.category,
                "symbol": api_symbol,
                "side": side,
                "orderType": "Market",
                "qty": str(qty),
                "stopLoss": str(sl_final) if sl_final > 0 else None,
                "tpTriggerBy": "LastPrice",
                "slTriggerBy": "LastPrice",
                "tpslMode": "Full",
                "positionIdx": positionIdx
            }
            if tp_final:
                order_params["takeProfit"] = str(tp_final)

            response = await asyncio.to_thread(self.session.place_order, **order_params)
            logger.info(f"Atomic order placed for {symbol} (idx:{positionIdx}): {response}")
            return response
        except Exception as e:
            logger.error(f"Failed to place atomic order for {symbol}: {e}")
            return None

    @with_circuit_breaker(breaker_name="bybit_rest_private", fallback_return=False, is_critical=True)
    async def close_position(self, symbol: str, side: str, qty: float, reason: str = "MANUAL_CLOSE", is_partial: bool = False) -> bool:
        """
        [V110.118] Closes (fully or partially) a position at market price.
        
        Args:
            symbol: Trading pair (e.g. 'SOLUSDT')
            side: Position side ('Buy' or 'Sell')
            qty: Quantity to close (partial if < full size)
            reason: Close reason for audit trail
            is_partial: If True, keeps the remaining position open (Moonbag stays alive)
        
        V5.3.4: Added closure_lock and pending_closures for target/SL coordination.
        Returns True if closure was executed, False if already closed/pending.
        """
        norm_symbol = self._strip_p(symbol).upper()
        
        # [V110.118] Partial closes use a lighter lock (prefix 'partial:') to allow
        # multiple harvests of the same symbol over time without blocking full closes.
        lock_key = f"partial:{norm_symbol}" if is_partial else f"close:{norm_symbol}"
        lock_acquired = await self.redis.acquire_lock(lock_key, lock_timeout=15)
        if not lock_acquired:
            logger.info(f"🛡️ [REDIS LOCK] {norm_symbol} {'partial harvest' if is_partial else 'closure'} already in progress. Skipping.")
            return False

        try:
            if not is_partial and norm_symbol in self.pending_closures:
                logger.info(f"🛡️ [BYBIT] {norm_symbol} already has a local pending closure. Skipping.")
                return False
            
            # [V5.3.4] Add to pending_closures immediately to prevent sync flapping
            if not is_partial:
                self.pending_closures.add(norm_symbol)
            
            if self.execution_mode == "PAPER":
                logger.info(f"[PAPER] {'Partial harvest' if is_partial else 'Closing'} position {norm_symbol} | qty={qty} | Reason: {reason}")
                # Find position in tactical or moonbags
                pos = next((p for p in self.paper_positions if self.normalize_symbol(p["symbol"]) == norm_symbol), None)
                if not pos:
                    pos = next((p for p in self.paper_moonbags if self.normalize_symbol(p["symbol"]) == norm_symbol), None)
                if pos:
                    try:
                        from services.execution_protocol import execution_protocol
                        api_symbol = self._strip_p(symbol)
                        
                        entry_price = float(pos["avgPrice"])
                        size = float(pos["size"])
                        leverage = float(pos.get("leverage", 50))
                        side_pos = pos["side"]
                        stop_price = float(pos.get("stopLoss", 0))
                        
                        # [V110.118] Determinar qty real a fechar
                        close_qty = min(float(qty) if qty > 0 else size, size)  # Nunca fechar mais que o size total
                        remaining_qty = size - close_qty
                        # Re-avaliar is_partial pela qty real (proteção dupla)
                        is_partial_real = is_partial and remaining_qty > 0.000001
                        
                        reason_upper = (reason or "").upper()
                        is_sl_trigger = any(kw in reason_upper for kw in ["SL", "STOP", "RISK_ZERO", "SAFE", "STABILIZE", "FLASH", "MEGA", "PROFIT"])
                        
                        if is_sl_trigger and stop_price > 0:
                            exit_price = stop_price
                            logger.info(f"[PAPER] SL-triggered exit: using stop price ${exit_price:.6f} as exit (not market)")
                        else:
                            # Safely fetch current price
                            try:
                                # [V110.125 FIX] Tenta pegar o preço do WebSocket (LKG) primeiro pois é mais rápido e confiável que o Ticker REST em picos
                                from services.bybit_ws import bybit_ws_service
                                ws_price = bybit_ws_service.get_current_price(symbol)
                                
                                if ws_price and ws_price > 0:
                                    exit_price = ws_price
                                    logger.info(f"[PAPER] Using WS price for closure: ${exit_price:.6f}")
                                else:
                                    ticker = await asyncio.to_thread(self.session.get_tickers, category="linear", symbol=api_symbol)
                                    ticker_list = ticker.get("result", {}).get("list", [])
                                    if ticker_list and float(ticker_list[0].get("lastPrice", 0)) > 0:
                                        exit_price = float(ticker_list[0].get("lastPrice", 0))
                                    else:
                                        # [V110.125 HARDEN] Se tudo falhar mas for um SL, usa o stop_price. 
                                        # Senão, usa o entry_price como último recurso (com aviso crítico).
                                        if stop_price > 0:
                                            exit_price = stop_price
                                            logger.warning(f"[PAPER] Critical Price Failure. Falling back to Stop Price: ${exit_price:.6f}")
                                        else:
                                            exit_price = entry_price 
                                            logger.error(f"[PAPER-CRITICAL] Global Price Failure. Falling back to ENTRY: ${exit_price:.6f} (PnL Zeroed)")
                            except Exception as price_err:
                                logger.warning(f"[PAPER] Failed to fetch exit price: {price_err}. Fallback: {'Stop Price' if stop_price > 0 else 'Entry Price'}")
                                exit_price = stop_price if stop_price > 0 else entry_price

                        # Calcular PnL da quantidade fechada
                        final_pnl = execution_protocol.calculate_pnl(entry_price, exit_price, close_qty, side_pos)
                        harvest_roi = execution_protocol.calculate_roi(entry_price, exit_price, side_pos, leverage=leverage)
                        
                        self.paper_balance += final_pnl
                        self.paper_orders_history.append({
                            "symbol": symbol,
                            "side": side_pos,
                            "positionValue": close_qty * entry_price, 
                            "unrealisedPnl": 0,
                            "createdTime": pos.get("createdTime") or str(int(time.time() * 1000)),
                            "avgEntryPrice": str(entry_price),
                            "avgExitPrice": str(exit_price),
                            "closedPnl": str(final_pnl),
                            "leverage": str(leverage),
                            "qty": str(close_qty),
                            "is_partial": is_partial_real,
                            "updatedTime": str(int(time.time() * 1000))
                        })
                        
                        # [V110.65] ATOMIC CLOSURE PROTOCOL
                        try:
                            from services.bankroll import bankroll_manager
                            slot_id = pos.get("slot_id", 0)
                            
                            # [V110.256] Capture intelligence BEFORE clearing slot or removing from memory
                            # genesis_id é puxado do slot_state (bankroll.py é a fonte canônica do ID)
                            fleet_intel = {}
                            unified_confidence = 50
                            pensamento = ""
                            canonical_genesis_id = pos.get("order_id")  # fallback inicial
                            canonical_order_id = pos.get("order_id", f"{norm_symbol}_{int(time.time())}")

                            if slot_id > 0:
                                from services.sovereign_service import sovereign_service
                                slot_state = await sovereign_service.get_slot(slot_id)
                                if slot_state:
                                    fleet_intel = slot_state.get("fleet_intel", {}) or {}
                                    unified_confidence = slot_state.get("unified_confidence", 50)
                                    pensamento = slot_state.get("pensamento", "")
                                    # [V110.256] genesis_id canônico vem do slot (definido pelo bankroll)
                                    slot_genesis = slot_state.get("genesis_id")
                                    slot_order_id = slot_state.get("order_id")
                                    if slot_genesis:
                                        canonical_genesis_id = slot_genesis
                                    if slot_order_id:
                                        canonical_order_id = slot_order_id

                            # Fallback de emergência se genesis ainda for None
                            if not canonical_genesis_id:
                                strategy_prefix = "BLZ" if slot_id in [1, 2] else "SWG"
                                canonical_genesis_id = f"{strategy_prefix}-RECOVERY-{norm_symbol[:4]}-{int(time.time())}"
                                logger.warning(f"⚠️ [GENESIS-RECOVERY] {symbol}: genesis_id ausente. Fallback: {canonical_genesis_id}")

                            harvest_label = "HARVEST" if is_partial_real else "FULL_CLOSE"
                            trade_report = (
                                f"--- PAPER EXECUTION V110.256 ({'PARTIAL HARVEST' if is_partial_real else 'FULL CLOSE'}) ---\n"
                                f"Symbol: {symbol} | Side: {side_pos}\n"
                                f"Entry: ${entry_price:.6f} | Exit: ${exit_price:.6f}\n"
                                f"Qty Fechada: {close_qty:.6f} | Qty Restante: {remaining_qty:.6f}\n"
                                f"PNL: ${final_pnl:.2f} | ROI: {harvest_roi:.1f}% | Reason: {reason}\n"
                                f"Genesis: {canonical_genesis_id}\n"
                                f"{'🌾 MOONBAG SOBREVIVE com residual!' if is_partial_real else '🛑 Posição totalmente fechada.'}"
                            )

                            trade_data = {
                                "symbol": symbol,
                                "side": side_pos,
                                "entry_price": entry_price,
                                "exit_price": exit_price,
                                "qty": close_qty,  # [V110.118] qty da COLHEITA, não do total
                                "order_id": canonical_order_id,  # [V110.256] order_id canônico
                                "genesis_id": canonical_genesis_id,  # [V110.256] ID único e consistente
                                "pnl": final_pnl,
                                "slot_id": slot_id,
                                "slot_type": "MOONBAG" if is_partial_real else "SNIPER",
                                "close_reason": reason,
                                "final_roi": harvest_roi,
                                "closed_at": get_br_iso_str(),
                                "opened_at": pos.get("opened_at", 0),
                                "reasoning_report": trade_report,
                                "fleet_intel": fleet_intel,
                                "unified_confidence": unified_confidence,
                                "pensamento": pensamento,
                                "entry_margin": round(close_qty * entry_price / leverage, 2),
                                "leverage": leverage,
                                "is_partial": is_partial_real,
                                "pnl_percent": round(harvest_roi, 2)
                            }

                            # Registrar no histórico
                            await bankroll_manager.register_sniper_trade(trade_data)
                            
                            if is_partial_real:
                                # [V110.118] PARCIAL: Moonbag sobrevive — NÃO limpar slot
                                # Apenas atualizar a quantidade e margem restantes na memória
                                pos["size"] = str(remaining_qty)
                                pos["entry_margin"] = str(round(remaining_qty * entry_price / leverage, 2))
                                logger.info(
                                    f"🌾 [PAPER-HARVEST] {symbol} | Colhido {close_qty:.6f} ({(close_qty/size)*100:.1f}%) "
                                    f"| Restante: {remaining_qty:.6f} | PNL Parcial: ${final_pnl:.2f} | ROI: {harvest_roi:.1f}%"
                                )
                                # Atualizar Firebase do Moonbag (se aplicável) sem resetar o slot
                                if slot_id > 0:
                                    from services.sovereign_service import sovereign_service
                                    # Se é um moonbag (emancipado), atualizar o registro do vault
                                    moonbags_state = await sovereign_service.get_moonbags()
                                    t_moon = next((m for m in moonbags_state if self._strip_p(m.get("symbol", "")) == norm_symbol), None)
                                    if t_moon:
                                        await sovereign_service.update_moonbag(t_moon["id"], {
                                            "qty": remaining_qty,
                                            "entry_margin": round(remaining_qty * entry_price / leverage, 2),
                                            "harvest_pnl_accumulated": round(
                                                float(t_moon.get("harvest_pnl_accumulated", 0)) + final_pnl, 2
                                            ),
                                            "last_harvest_at": int(time.time()),
                                            "last_harvest_roi": round(harvest_roi, 1),
                                            "pensamento": f"🌾 Colheita de {harvest_roi:.0f}% ROI realizada | Residual: {remaining_qty:.6f}"
                                        })
                                        logger.info(f"✅ [PAPER-HARVEST] Firebase Moonbag atualizado para {symbol}.")
                            else:
                                # FECHAMENTO TOTAL: remover de memória e limpar slot
                                if pos in self.paper_positions:
                                    self.paper_positions.remove(pos)
                                elif pos in self.paper_moonbags:
                                    self.paper_moonbags.remove(pos)
                                logger.info(f"🛑 [PAPER-CLOSE] Full Close: {symbol} removido das posições.")

                                if slot_id > 0:
                                    from services.sovereign_service import sovereign_service
                                    await sovereign_service.hard_reset_slot(slot_id, reason=f"PAPER_CLOSE_ATOMIC_{reason}", pnl=final_pnl, trade_data=trade_data)
                                    logger.info(f"🧹 [PAPER-SYNC] Slot {slot_id} resetado com audit log.")

                        except Exception as atomic_err:
                            logger.error(f"❌ [PAPER-ATOMIC-FAIL] Critical failure during {'harvest' if is_partial_real else 'closure'} for {symbol}: {atomic_err}")
                            raise atomic_err

                        # Cleanup pending after a small delay to let other loops sync
                        asyncio.create_task(self._cleanup_pending_closure(norm_symbol))
                        return True


                    except Exception as e:
                        logger.error(f"[PAPER] Error during position closure: {e}")
                        if pos in self.paper_positions:
                            self.paper_positions.remove(pos)
                        self.pending_closures.discard(norm_symbol)
                        return False
                return False

            # REAL MODE
            try:
                api_symbol = self._strip_p(symbol)
                close_side = "Sell" if side == "Buy" else "Buy"
                response = await asyncio.to_thread(self.session.place_order,
                    category=self.category,
                    symbol=api_symbol,
                    side=close_side,
                    orderType="Market",
                    qty=str(qty),
                    reduceOnly=True
                )
                # Cleanup pending
                asyncio.create_task(self._cleanup_pending_closure(norm_symbol))
                return True
            except Exception as e:
                logger.error(f"Error closing position for {symbol}: {e}")
                self.pending_closures.discard(norm_symbol)
                return False
        finally:
            # Release Redis Lock
            await self.redis.release_lock(f"close:{norm_symbol}")

    async def _cleanup_pending_closure(self, symbol: str, delay: int = 15):
        """V5.3.4: Helper to clear pending closure flag after a delay."""
        await asyncio.sleep(delay)
        self.pending_closures.discard(symbol)

    async def get_closed_pnl(self, symbol: str, limit: int = 5):
        """
        [V43.2] Fetches final PnL for closed trades.
        Increased default limit to 5 to avoid missing rapid-fire trades during sync.
        """
        if self.execution_mode == "PAPER":
            # Filter history by symbol
            relevant = [h for h in self.paper_orders_history if h["symbol"] == symbol]
            # Return last N
            return relevant[-limit:] if relevant else []

        async with self._http_semaphore:
            try:
                api_symbol = self._strip_p(symbol)
                # [V43.2] V5 Bybit API: Fetching closed PnL with higher limit
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.session.get_closed_pnl, 
                        category=self.category, 
                        symbol=api_symbol, 
                        limit=limit
                    ), 
                    timeout=10.0
                )
                
                result_list = response.get("result", {}).get("list", [])
                if not result_list:
                    # [V43.2] Traceability: Log when no history is found despite sync trigger
                    logger.debug(f"🔍 [BYBIT-REST] No closed PnL found for {symbol} in last {limit} trades.")
                return result_list
            except Exception as e:
                logger.error(f"Error fetching closed PnL for {symbol}: {e}")
                return []

    async def get_public_trade_history(self, symbol: str, limit: int = 50):
        """
        [V16.0] REST Fallback for CVD calculation.
        Fetches recent public trades via HTTP when WebSocket is unstable.
        """
        async with self._http_semaphore:
            try:
                api_symbol = self._strip_p(symbol)
                resp = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.session.get_public_trade_history,
                        category=self.category,
                        symbol=api_symbol,
                        limit=limit
                    ),
                    timeout=5.0
                )
                return resp.get("result", {}).get("list", [])
            except Exception as e:
                logger.warning(f"Error fetching public trades for {symbol}: {e}")
                return []

    async def get_orderbook(self, symbol: str, limit: int = 50) -> dict:
        """[V12.0] Fetches L2 orderbook for localized depth analysis."""
        try:
            norm_symbol = self.normalize_symbol(symbol)
            resp = await asyncio.to_thread(self._session.get_orderbook, category="linear", symbol=norm_symbol, limit=limit)
            return resp.get("result", {})
        except Exception as e:
            logger.error(f"Error fetching orderbook for {symbol}: {e}")
            return {}

    async def get_klines(self, symbol: str, interval: str = "60", limit: int = 20, kline_type: str = "mark"):
        """
        Fetches historical klines. 
        Use kline_type='mark' for Mark Price (no volume, safer for triggers)
        Use kline_type='last' for Last Price (includes volume, better for UI)
        """
        async with self._http_semaphore:
            try:
                # [V110.12.11] ENSURE NO .P SUFFIX for Market Data
                api_symbol = self._strip_p(symbol).replace(".P", "")
                
                method = self.session.get_mark_price_kline if kline_type == "mark" else self.session.get_kline
                
                # V5.2.4.3: Added 5s timeout
                response = await asyncio.wait_for(asyncio.to_thread(method,
                    category=self.category,
                    symbol=api_symbol,
                    interval=interval,
                    limit=limit
                ), timeout=5.0)
                return response.get("result", {}).get("list", [])
            except Exception as e:
                logger.error(f"Error fetching klines for {symbol} ({kline_type}): {e}")
                return []

    async def get_open_interest(self, symbol: str, interval: str = "1h") -> float:
        """
        [V15.5] Fetches the current Open Interest for a symbol.
        Used to detect 'Gas' (liquidity inflows) during accumulation box exits.
        """
        async with self._http_semaphore:
            try:
                # [V110.12.11] ENSURE NO .P SUFFIX for Market Data
                api_symbol = self._strip_p(symbol).replace(".P", "")
                # V5 endpoint: get_open_interest
                response = await asyncio.wait_for(asyncio.to_thread(
                    self.session.get_open_interest,
                    category=self.category,
                    symbol=api_symbol,
                    intervalTime=interval,
                    limit=1
                ), timeout=5.0)
                
                oi_list = response.get("result", {}).get("list", [])
                if oi_list:
                    return float(oi_list[0].get("openInterest", 0))
                return 0.0
            except Exception as e:
                logger.error(f"Error fetching Open Interest for {symbol}: {e}")
                return 0.0

    async def get_open_interest_history(self, symbol: str, interval: str = "5min", limit: int = 5) -> List[Dict[str, Any]]:
        """
        [V46.0] Fetches historical Open Interest data.
        Returns a list of OI records: [{"openInterest": "...", "timestamp": "..."}]
        """
        async with self._http_semaphore:
            try:
                api_symbol = self._strip_p(symbol)
                response = await asyncio.wait_for(asyncio.to_thread(
                    self.session.get_open_interest,
                    category=self.category,
                    symbol=api_symbol,
                    intervalTime=interval,
                    limit=limit
                ), timeout=5.0)
                
                return response.get("result", {}).get("list", [])
            except Exception as e:
                logger.error(f"Error fetching OI history for {symbol}: {e}")
                return []

    async def get_account_ratio(self, symbol: str, period: str = "5min") -> float:
        """
        [V15.5] Fetches the Long/Short Account Ratio for a symbol.
        Used to detect retail positioning (high ratio = retail over-bought).
        """
        async with self._http_semaphore:
            try:
                # [V110.12.11] ENSURE NO .P SUFFIX for Market Data
                api_symbol = self._strip_p(symbol).replace(".P", "")
                # V5 endpoint: get_long_short_ratio
                response = await asyncio.wait_for(asyncio.to_thread(
                    self.session.get_long_short_ratio,
                    category=self.category,
                    symbol=api_symbol,
                    period=period,
                    limit=1
                ), timeout=5.0)
                
                ratio_list = response.get("result", {}).get("list", [])
                if ratio_list:
                    # Returns the ratio (e.g., 1.5 means 1.5 accounts long for every 1 short)
                    return float(ratio_list[0].get("buySellRatio", 1.0))
                return 1.0
            except Exception as e:
                logger.error(f"Error fetching Account Ratio for {symbol}: {e}")
                return 1.0

    # [V25.1] Funding Rate Cache
    _funding_cache: dict = {}  # { symbol: { rate, timestamp } }
    
    async def get_funding_rate(self, symbol: str) -> float:
        """
        [V25.1] Fetches the current funding rate for a symbol.
        Positive rate = longs pay shorts (bearish pressure).
        Negative rate = shorts pay longs (squeeze potential for longs).
        Returns rate as decimal (e.g., 0.0001 = 0.01%).
        Cached for 60s to avoid excessive API calls.
        """
        async with self._http_semaphore:
            try:
                api_symbol = self._strip_p(symbol)
                
                # Check cache (60s TTL)
                cached = self._funding_cache.get(api_symbol)
                if cached and (time.time() - cached.get("ts", 0)) < 60:
                    return cached["rate"]
                
                response = await asyncio.wait_for(asyncio.to_thread(
                    self.session.get_tickers,
                    category=self.category,
                    symbol=api_symbol
                ), timeout=5.0)
                
                ticker = response.get("result", {}).get("list", [{}])[0]
                rate = float(ticker.get("fundingRate", 0))
                
                # Cache result
                self._funding_cache[api_symbol] = {"rate": rate, "ts": time.time()}
                
                return rate
            except Exception as e:
                logger.warning(f"Error fetching funding rate for {symbol}: {e}")
                return 0.0
    
    async def set_trading_stop(self, category: str, symbol: str, stopLoss: str, slTriggerBy: str = None, tpslMode: str = None, positionIdx: int = None, side: str = None):
        """
        Sets the stop loss for a position.
        [V43.0] Hedge Mode Support: Automatically resolves positionIdx based on side if not provided.
        """
        if self.execution_mode == "PAPER":
            api_symbol = self._strip_p(symbol)
            logger.info(f"[PAPER] Updating Stop Loss for {api_symbol} to {stopLoss}")
            # [V110.28.2 FIX] Busca em paper_positions E paper_moonbags (garante Hard-Lock 110%)
            pos = next((p for p in self.paper_positions if p["symbol"] == api_symbol), None)
            if not pos:
                pos = next((p for p in self.paper_moonbags if p["symbol"] == api_symbol), None)
            if pos:
                pos["stopLoss"] = str(stopLoss)
                await self._save_paper_state()
                logger.info(f"[PAPER] Stop Loss de {api_symbol} atualizado para {stopLoss} com sucesso.")
                return {"retCode": 0, "result": {}}
            else:
                logger.warning(f"[PAPER] Position {api_symbol} não encontrada em positions nem moonbags.")
                return {"retCode": 10001, "retMsg": f"Position {api_symbol} not found in Paper Trading"}

        try:
            api_symbol = self._strip_p(symbol)
            
            # [V43.0] Hedge Mode Auto-Resolution
            if positionIdx is None:
                if side:
                    # In Hedge Mode: 1=Buy, 2=Sell. In One-Way: 0.
                    # We default to 0 but if we have a side, we can't be sure of the mode without an API call.
                    # Optimization: Fetch one position to see its structure.
                    active_pos = await self.get_active_positions(symbol=api_symbol)
                    if active_pos:
                        positionIdx = active_pos[0].get("positionIdx", 0)
                    else:
                        positionIdx = 0 
                else:
                    positionIdx = 0

            params = {
                "category": category,
                "symbol": api_symbol,
                "stopLoss": stopLoss,
                "positionIdx": positionIdx
            }
            if slTriggerBy: params["slTriggerBy"] = slTriggerBy
            if tpslMode: params["tpslMode"] = tpslMode
            
            response = await asyncio.to_thread(self.session.set_trading_stop, **params)
            logger.info(f"set_trading_stop response for {symbol} (idx:{positionIdx}): {response}")
            return response
        except Exception as e:
            logger.error(f"Error setting SL for {symbol}: {e}")
            return {"retCode": -1, "retMsg": str(e)}

    async def run_real_execution_loop(self):
        """
        [V110.0] Smart SL Engine for REAL Mode.
        Monitors both Tactical Slots and Moonbag Vault.
        """
        if self.execution_mode != "REAL":
            return

        from services.execution_protocol import execution_protocol
        from services.sovereign_service import sovereign_service

        logger.info("🚀 [V110.0] REAL Execution Engine (Tactical + Vault) ACTIVATING...")

        while True:
            try:
                # 1. Get active slots AND moonbags from Firebase
                slots = await sovereign_service.get_active_slots()
                moonbags = await sovereign_service.get_moonbags()
                
                active_tactical = [s for s in slots if s.get("symbol") and s.get("entry_price", 0) > 0]
                active_positions = active_tactical + moonbags
                
                if not active_positions:
                    await asyncio.sleep(5)
                    continue
                # 2. Batch fetch tickers & positions
                resp = await asyncio.to_thread(self.session.get_tickers, category="linear")
                ticker_list = resp.get("result", {}).get("list", [])
                price_map = {t["symbol"]: float(t.get("lastPrice", 0)) for t in ticker_list}

                # [V110.125] Position Verification: Fetch real positions once per loop for cross-check
                real_positions = await self.get_active_positions()
                active_real_symbols = {p['symbol'].replace('.P', '').upper() for p in real_positions}

                # 3. Process each position
                for slot in active_positions:
                    try:
                        symbol = self._strip_p(slot["symbol"])
                        current_price = price_map.get(symbol, 0)
                        if current_price <= 0: continue

                        is_moonbag = slot.get("status") == "EMANCIPATED"
                        moon_uuid = slot.get("id") if is_moonbag else None

                        # [V110.125] GHOST MOONBAG GUARD: Se é moonbag e não existe na Bybit, ignore ou purgue
                        if is_moonbag and symbol not in active_real_symbols:
                            opened_at = slot.get("opened_at", 0)
                            if (time.time() - opened_at) > 300: # 5 min grace period
                                logger.warning(f"🌙 [GHOST-PURGE] Moonbag {symbol} não encontrada na Bybit. Removendo do Vault.")
                                await sovereign_service.remove_moonbag(moon_uuid, reason="GHOST_SYCH_BYBIT")
                                continue

                        slot_data = {
                            "symbol": symbol,
                            "side": slot.get("side", "Buy"),
                            "entry_price": float(slot.get("entry_price", 0)),
                            "current_stop": float(slot.get("current_stop", 0)),
                            "target_price": float(slot.get("target_price", 0)),
                            "structural_target": float(slot.get("structural_target", 0)),
                            "slot_type": slot.get("slot_type", "TREND"),
                            "slot_id": slot.get("id"),
                            "status": slot.get("status"),
                            "sentinel_retests": slot.get("sentinel_retests", 0),
                            "partial_tp_hit": slot.get("partial_tp_hit", False),
                            "move_room_pct": slot.get("move_room_pct", 2.0),
                            "opened_at": slot.get("opened_at", 0),
                            "maestria_guard_active": slot.get("maestria_guard_active", False),
                            "sentinel_first_hit_at": slot.get("sentinel_first_hit_at", 0),
                        }

                        # [V110.125] ROI INTEGRITY GUARD
                        if slot_data["entry_price"] <= 0:
                            logger.error(f"❌ [DATA-CORRUPT] {symbol} com entry_price zero. Pulando processamento.")
                            continue

                        # 4. Execute Logic
                        should_close, reason, new_sl = await execution_protocol.process_order_logic(slot_data, current_price)

                        # [SENTINEL 3.0] Ativação da Paciência Diplomática
                        if reason == "SENTINEL_ACTIVATE":
                            upd = {"sentinel_first_hit_at": new_sl} 
                            if is_moonbag: await sovereign_service.update_moonbag(moon_uuid, upd)
                            else: await sovereign_service.update_slot(slot["id"], upd)
                            continue

                        # [V110.6] EMANCIPATION TRIGGER (Real Mode)
                        if reason == "EMANCIPATE_SLOT" and not is_moonbag:
                            if symbol in self.emancipating_symbols:
                                logger.info(f"🛡️ [V110.4] {symbol} já está em processo de emancipação. Aguardando...")
                                continue
                            
                            self.emancipating_symbols.add(symbol)
                            try:
                                # [V110.6] ACQUISITION LOCK: Update Exchange BEFORE liberating slot in Firebase
                                logger.info(f"🚀 [V110.6 EMANCIPATE-SYNC] Iniciando atualização na Bybit para {symbol}...")
                                
                                # 1. Limpa TakeProfit (Surf Mode)
                                tp_clear = await self.set_trading_stop(symbol, takeProfit="0")
                                
                                # 2. Define StopLoss Progressivo
                                success = True
                                rounded_sl = 0
                                if new_sl:
                                    rounded_sl = await self.round_price(symbol, new_sl)
                                    sl_result = await self.set_trading_stop(
                                        category="linear", symbol=symbol,
                                        stopLoss=str(rounded_sl), side=slot_data["side"]
                                    )
                                    if sl_result.get("retCode") != 0:
                                        ret_code = sl_result.get("retCode")
                                        ret_msg = str(sl_result.get("retMsg", "")).lower()
                                        if ret_code in (10001, 130024, 130073, 140024, 130074) or "not modified" in ret_msg or "same" in ret_msg:
                                            logger.info(f"✅ [REAL] SL de {symbol} já está posicionado em +110% (Code {ret_code}). Avançando com Emancipação.")
                                        else:
                                            logger.error(f"❌ [V110.6] Falha ao definir SL de emancipação para {symbol}: {sl_result}")
                                            success = False
                                
                                # 3. SOMENTE se a Bybit confirmar, promove no Firebase
                                if success:
                                    new_moon_uuid = await sovereign_service.promote_to_moonbag(slot.get("id"))
                                    if new_moon_uuid:
                                        logger.info(f"✅ [V110.6] {symbol} promovido para Moonbag após confirmação da Bybit.")
                                        if rounded_sl > 0:
                                            await sovereign_service.update_moonbag(new_moon_uuid, {"current_stop": rounded_sl, "timestamp_last_update": time.time()})
                                else:
                                    logger.warning(f"⚠️ [V110.6] Emancipação abortada para {symbol} devido a falha na corretora. O slot permanece tático.")
                            finally:
                                # Remove o guard após um pequeno delay para sincronização
                                asyncio.create_task(self._release_emancipation_guard(symbol))
                            continue

                        # 5a. Handle SL Update
                        if new_sl is not None and not should_close:
                            current_sl = float(slot.get("current_stop", 0))
                            side_norm = slot_data["side"].lower()
                            
                            is_improvement = (side_norm == "buy" and new_sl > current_sl) or \
                                             (side_norm == "sell" and (current_sl == 0 or new_sl < current_sl)) or \
                                             (reason == "RESCUE_MOVE_SL_BREAKEVEN")

                            if is_improvement:
                                rounded_sl = await self.round_price(symbol, new_sl)
                                result = await self.set_trading_stop(
                                    category="linear", symbol=symbol, 
                                    stopLoss=str(rounded_sl), side=slot_data["side"]
                                )
                                if result.get("retCode") == 0:
                                    upd = {"current_stop": rounded_sl, "timestamp_last_update": time.time()}
                                    if is_moonbag: await sovereign_service.update_moonbag(moon_uuid, upd)
                                    else: await sovereign_service.update_slot(slot["id"], upd)
                                    # [V110.350] Use 50x leverage for ROI consistency in logs
                                    lev_val = float(slot_data.get("leverage", 50.0))
                                    logger.info(f"🛡️ [REAL SL] {symbol} ROI: {execution_protocol.calculate_roi(slot_data['entry_price'], current_price, side_norm, leverage=lev_val):.1f}% | SL: {rounded_sl}")

                        # 5b. Status Updates Sem Fechamento (ex: MAESTRIA)
                        if reason == "MAESTRIA_GUARD_ACTIVATE" and not should_close:
                            if is_moonbag: await sovereign_service.update_moonbag(moon_uuid, {"maestria_guard_active": True})
                            else: await sovereign_service.update_slot(slot["id"], {"maestria_guard_active": True})

                        # 5b. Handle Partial Harvest or Full Closure
                        elif should_close or reason == "PARTIAL_HARVEST":
                            logger.info(f"🚜 [HARVESTER] Decision for {symbol}: {reason}")
                            try:
                                from services.bankroll import bankroll_manager
                                pos_list = await self.get_active_positions(symbol=symbol)
                                for p in pos_list:
                                    q = float(p.get("size", 0))
                                    if q <= 0: continue
                                    
                                    if reason == "PARTIAL_HARVEST":
                                        # Payload is in new_sl (which is harvest_res)
                                        harvest_res = new_sl
                                        proportion = harvest_res.get("proportion", 0.9)
                                        close_qty = await self.round_qty(symbol, q * proportion)
                                        
                                        if close_qty > 0:
                                            logger.warning(f"🌾 [REAL-HARVEST] Executing partial harvest for {symbol}: {close_qty} units ({proportion*100:.1f}%)")
                                            success = await self.close_position(symbol, p["side"], close_qty, reason=f"HARVEST_{harvest_res.get('target_level')}")
                                            if success:
                                                # Log trade manually for Real mode as it won't appear in orphan sync yet
                                                # Calculate estimated PnL for the harvest
                                                entry_p = float(p.get("avgPrice", 0))
                                                roi_val = harvest_res.get("current_roi", 0)
                                                margin_used = (close_qty * entry_p) / 50.0
                                                est_pnl = margin_used * (roi_val / 100.0)
                                                
                                                trade_data = {
                                                    "symbol": symbol,
                                                    "side": p["side"],
                                                    "entry_price": entry_p,
                                                    "exit_price": current_price,
                                                    "qty": close_qty,
                                                    "pnl": est_pnl,
                                                    "pnl_percent": roi_val,
                                                    "slot_id": slot.get("id", 0),
                                                    "slot_type": "MOONBAG",
                                                    "close_reason": f"HARVEST_{harvest_res.get('target_level')}",
                                                    "order_id": f"{symbol.replace('.P','')}_{slot.get('opened_at', int(time.time()))}_harvest"
                                                }
                                                await bankroll_manager.register_sniper_trade(trade_data)
                                                
                                                # Update moonbag record with new qty
                                                await sovereign_service.update_moonbag(moon_uuid, {
                                                    "qty": q - close_qty,
                                                    "entry_margin": ((q - close_qty) * entry_p) / 50.0,
                                                    "pensamento": f"🌾 Colheita de 500% ROI realizada em {harvest_res.get('target_level')}"
                                                })
                                    else:
                                        # Full Closure
                                        logger.warning(f"🛑 [REAL EXIT] {symbol} | Reason: {reason}")
                                        success = await self.close_position(symbol, p["side"], q, reason=reason)
                                        if success and is_moonbag:
                                            # Register trade before removing
                                            entry_p = float(p.get("avgPrice", 0))
                                            lev_val = float(p.get("leverage", 50.0))
                                            roi_val = execution_protocol.calculate_roi(entry_p, current_price, p["side"], leverage=lev_val)
                                            margin_used = (q * entry_p) / lev_val
                                            est_pnl = margin_used * (roi_val / 100.0)
                                            
                                            trade_data = {
                                                "symbol": symbol,
                                                "side": p["side"],
                                                "entry_price": entry_p,
                                                "exit_price": current_price,
                                                "qty": q,
                                                "pnl": est_pnl,
                                                "pnl_percent": roi_val,
                                                "slot_id": slot.get("id", 0),
                                                "slot_type": "MOONBAG",
                                                "close_reason": reason,
                                                "order_id": f"{symbol.replace('.P','')}_{slot.get('opened_at', int(time.time()))}"
                                            }
                                            await bankroll_manager.register_sniper_trade(trade_data)
                                            await sovereign_service.remove_moonbag(moon_uuid, reason=reason)
                                        elif success and not is_moonbag:
                                            # Slots normais são pegos pelo Position Reaper, mas vamos garantir o order_id
                                            pass
                            except Exception as ce: logger.error(f"Error handling closure/harvest for {symbol}: {ce}")


                    except Exception as se:
                        logger.error(f"Error processing {slot.get('symbol')}: {se}")

                # UI PNL Pulse
                if active_tactical:
                    pnl_summary = []
                    for s in active_tactical:
                        p_sym = self._strip_p(s["symbol"])
                        cur_p = price_map.get(p_sym, 0)
                        if cur_p > 0:
                            entry = float(s.get("entry_price", 0))
                            if entry > 0:
                                side = s.get("side", "Buy")
                                qty = float(s.get("qty") or s.get("size") or 0)
                                lev = float(s.get("leverage", 50.0))
                                # [V110.128] Standardized PnL Calculation: (ROI/100) * Margin
                                margin = float(s.get("entry_margin") or (qty * entry / lev))
                                roi = execution_protocol.calculate_roi(entry, cur_p, side, leverage=lev)
                                p_usd = (roi / 100.0) * margin
                                
                                pnl_summary.append({
                                    "symbol": s["symbol"],
                                    "roi": roi,
                                    "pnl_usd": round(p_usd, 2)
                                })
                    if pnl_summary:
                        await self.redis.publish_update("ui_updates", {"type": "PNL_PULSE", "data": pnl_summary})

            except Exception as e:
                logger.error(f"[REAL ENGINE] Loop error: {e}")

            await asyncio.sleep(3)

    async def run_paper_execution_loop(self):
        """
        [V110.0] Engine de execução blindada para modo PAPER.
        Monitors both paper_positions and paper_moonbags.
        """
        if self.execution_mode != "PAPER":
            return

        from services.bybit_ws import bybit_ws_service
        from services.execution_protocol import execution_protocol
        from services.sovereign_service import sovereign_service

        logger.info("🚀 [V110.12.12] PAPER Execution Engine (Tactical + Vault) ACTIVATING...")
        
        while True:
            try:
                # [V110.23.5] Periodically refresh state from Firestore if any other instance modified it
                # (Every 5 minutes or based on a last-update flag if we wanted to be fancy)
                if time.time() - self._last_paper_load_time > 300:
                    await self._load_paper_state()
                    # [V110.64 FIX] Removido 'continue' que causava skip do ciclo inteiro após reload

                combined_paper = self.paper_positions + self.paper_moonbags
                if not combined_paper:
                    await asyncio.sleep(2)
                    continue

                # 1. Fetch prices
                price_map = {}
                for pos in combined_paper:
                    sym = pos["symbol"]
                    ws_price = bybit_ws_service.get_current_price(sym)
                    if ws_price and ws_price > 0: price_map[sym] = ws_price
                    else:
                        ticker = await self.get_tickers(symbol=sym)
                        t_list = ticker.get("result", {}).get("list", [])
                        if t_list: price_map[sym] = float(t_list[0].get("lastPrice", 0))

                # 2. Get Firebase slots
                slots = await sovereign_service.get_active_slots()
                slots_by_symbol = {self._strip_p(s.get("symbol")): s for s in slots if s.get("symbol")}

                # 3. Process each position
                for pos in combined_paper:
                    symbol = pos.get("symbol", "UNKNOWN")
                    try:
                        current_price = price_map.get(symbol, 0)
                        if current_price <= 0: continue

                        is_moonbag = pos.get("status") == "EMANCIPATED"
                        slot = slots_by_symbol.get(symbol)
                        
                        slot_data = {
                            "symbol": symbol,
                            "side": pos.get("side", "Buy"),
                            "entry_price": float(pos.get("avgPrice", 0)),
                            "current_stop": float(pos.get("stopLoss", 0)) if pos.get("stopLoss") else 0,
                            "target_price": float(pos.get("takeProfit", 0)) if pos.get("takeProfit") else 0,
                            "slot_type": slot.get("slot_type", "SNIPER") if slot else "SNIPER",
                            "slot_id": slot.get("id") if slot else None,
                            "status": pos.get("status"),
                            "opened_at": pos.get("opened_at", 0),
                            "maestria_guard_active": pos.get("maestria_guard_active", False),
                            "sentinel_first_hit_at": slot.get("sentinel_first_hit_at", 0) if slot else 0,
                            # [V110.28.2 FIX] Campos ausentes que afetam os triggers da Escadinha
                            "structural_target": float(slot.get("structural_target", 0)) if slot else 0,
                            "score": slot.get("score", 0) if slot else 0,
                            "is_market_ranging": slot.get("is_market_ranging", False) if slot else False,
                            "id": slot.get("id", 0) if slot else 0,
                            "leverage": float(pos.get("leverage", 50.0))
                        }

                        from services.execution_protocol import execution_protocol
                        lev = float(pos.get("leverage", 50.0))
                        roi = execution_protocol.calculate_roi(slot_data["entry_price"], current_price, slot_data["side"], leverage=lev)
                        should_close, reason, new_sl = await execution_protocol.process_order_logic(slot_data, current_price)
                        # [V110.100.2] ABSOLUTE ORDER (Sem saida parcial)
                        # A ordem inteira será conduzida até a emancipação completa.

                        # [V110.118 FIX-A] SENTINEL EARLY EXIT: Deve ser interceptado ANTES
                        # do bloco genérico de new_sl para evitar que o timestamp (time.time())
                        # seja gravado como stopLoss no Firebase e na memória Paper.
                        if reason == "SENTINEL_ACTIVATE":
                            current_phase = execution_protocol.get_sl_phase(roi, scale=1.0, slot_data=slot_data)
                            upd = {
                                "sentinel_first_hit_at": new_sl,  # new_sl aqui É o timestamp — correto
                                "visual_status": current_phase,
                                "sl_phase": current_phase
                            }
                            if is_moonbag:
                                moonbags_fb = await sovereign_service.get_moonbags()
                                t_moon = next((m for m in moonbags_fb if m.get("symbol") == symbol), None)
                                if t_moon: await sovereign_service.update_moonbag(t_moon["id"], upd)
                            elif slot:
                                await sovereign_service.update_slot(slot["id"], upd)
                            continue  # EARLY EXIT: nunca chega no bloco de SL abaixo

                        # Se houve mudança de SL pela Escadinha
                        if new_sl and new_sl != slot_data["current_stop"]:
                            # [V110.118 FIX-A] SANITY GUARD: Rejeita timestamps como SL.
                            # Qualquer valor > 1 bilhão não é um preço de ativo — é um bug.
                            if isinstance(new_sl, (int, float)) and new_sl > 1_000_000_000:
                                logger.error(f"🚨 [V110.118 SL-GHOST-BLOCK] {symbol}: new_sl={new_sl:.0f} é um timestamp! Bloqueando gravação no stopLoss.")
                                new_sl = None
                            else:
                                pos["stopLoss"] = str(new_sl)
                                if slot:
                                    current_phase = execution_protocol.get_sl_phase(roi, scale=1.0, slot_data=slot_data)
                                    await sovereign_service.update_slot(slot["id"], {
                                        "current_stop": new_sl,
                                        "visual_status": current_phase,
                                        "sl_phase": current_phase
                                    })
                                await self._save_paper_state()

                                # Do not skip directly if this was an emancipation trigger!
                                if reason != "EMANCIPATE_SLOT":
                                    continue
                        # [V110.65] Sincronização periódica da fase visual (mesmo sem mudança de SL)
                        if slot and int(time.time()) % 5 == 0: # A cada ~5s
                            current_phase = execution_protocol.get_sl_phase(roi, scale=1.0, slot_data=slot_data)
                            if slot.get("visual_status") != current_phase:
                                await sovereign_service.update_slot(slot["id"], {
                                    "visual_status": current_phase,
                                    "sl_phase": current_phase
                                })

                        # [V110.6] EMANCIPATION TRIGGER (Paper Mode)
                        if reason == "EMANCIPATE_SLOT" and not is_moonbag:
                            if symbol in self.emancipating_symbols:
                                logger.info(f"🛡️ [V110.4 PAPER] {symbol} já está em processo de emancipação. Aguardando...")
                                continue

                            # [V110.28.2] PERPETUAL SURF: Mover 100% da ordem (Cheia) para o Vault.
                            # Liberar slot tático sem reduzir o tamanho da posição.
                            logger.info(f"🚀 [V110.28.2 PAPER-SYNC] Iniciando emancipação de ORDEM CHEIA para {symbol}...")
                            self.emancipating_symbols.add(symbol)
                            try:
                                # 1. Atualiza o estado local (Simulando a corretora)
                                pos["status"] = "EMANCIPATED"
                                pos["takeProfit"] = "0"
                                if new_sl: pos["stopLoss"] = str(new_sl)
                                
                                # Move para moonbags na memória
                                if pos in self.paper_positions:
                                    self.paper_positions.remove(pos)
                                if pos not in self.paper_moonbags:
                                    self.paper_moonbags.append(pos)
                                
                                await self._save_paper_state()
                                
                                # 2. Promove no Firebase (Liberação da vaga tática)
                                # Somente após o estado local estar salvo
                                moon_uuid = await sovereign_service.promote_to_moonbag(slot["id"]) if slot else None
                                if moon_uuid:
                                    pos["moon_uuid"] = moon_uuid # [V110.128.1] Persist ID for atomic closure
                                    if new_sl:
                                        await sovereign_service.update_moonbag(moon_uuid, {"current_stop": new_sl, "timestamp_last_update": time.time()})
                                    logger.info(f"[V110.6 PAPER] {symbol} promovido com sucesso no Firebase (ID: {moon_uuid}).")
                                else:
                                    # [V110.136.2 F1] EMANCIPATION RETRY GUARD
                                    # promote_to_moonbag falhou (retornou None). O slot do Firebase nao foi liberado.
                                    # Revertemos o estado em memoria para que o proximo ciclo tente novamente.
                                    logger.error(
                                        f"[V110.136.2 EMANCIPATION-FAIL] promote_to_moonbag falhou para {symbol}. "
                                        f"Revertendo estado em memoria — proximo ciclo tentara novamente."
                                    )
                                    pos["status"] = None
                                    pos["takeProfit"] = str(slot.get("target_price", "0")) if slot else "0"
                                    if pos in self.paper_moonbags:
                                        self.paper_moonbags.remove(pos)
                                    if pos not in self.paper_positions:
                                        self.paper_positions.append(pos)
                                    await self._save_paper_state()
                            finally:
                                asyncio.create_task(self._release_emancipation_guard(symbol))
                            continue

                        # 4a. Update SL
                        if new_sl is not None and not should_close:
                            current_sl = float(pos.get("stopLoss", 0)) if pos.get("stopLoss") else 0
                            side_norm = str(slot_data.get("side") or "Buy").lower()
                            is_improvement = (side_norm == "buy" and new_sl > current_sl) or \
                                             (side_norm == "sell" and (current_sl == 0 or new_sl < current_sl))
                            
                            if is_improvement:
                                pos["stopLoss"] = str(new_sl)
                                await self._save_paper_state()
                                if is_moonbag:
                                    moonbags = await sovereign_service.get_moonbags()
                                    target_moon = next((m for m in moonbags if m.get("symbol") == symbol), None)
                                    if target_moon: await sovereign_service.update_moonbag(target_moon["id"], {"current_stop": new_sl})
                                elif slot:
                                    await sovereign_service.update_slot(slot["id"], {"current_stop": new_sl})

                        # 4b. Status Updates Sem Fechamento (ex: MAESTRIA)
                        if reason == "MAESTRIA_GUARD_ACTIVATE" and not should_close:
                            pos["maestria_guard_active"] = True
                            await self._save_paper_state()
                            if slot: await sovereign_service.update_slot(slot["id"], {"maestria_guard_active": True})

                        # 4b. Close or Partial Harvest
                        elif should_close or reason == "PARTIAL_HARVEST":
                            try:
                                from services.bankroll import bankroll_manager
                                qty = float(pos.get("size", 0))
                                
                                if reason == "PARTIAL_HARVEST":
                                    harvest_res = new_sl
                                    proportion = harvest_res.get("proportion", 0.9)
                                    close_qty = qty * proportion
                                    
                                    if close_qty <= 0:
                                        logger.warning(f"⚠️ [PAPER-HARVEST] {symbol}: close_qty={close_qty} inválido. Abortando colheita.")
                                    else:
                                        logger.warning(
                                            f"🌾 [PAPER-HARVEST] {symbol} | "
                                            f"Colhendo {proportion*100:.1f}% ({close_qty:.6f}/{qty:.6f} unidades) "
                                            f"| Fase: {harvest_res.get('phase', 'COLHEITA')}"
                                        )
                                        # [V110.118] close_position com is_partial=True:
                                        # - NÃO chama hard_reset_slot (Moonbag sobrevive)
                                        # - NÃO remove da memória (apenas atualiza size)
                                        # - Registra o trade parcial no histórico
                                        # - Atualiza o Firebase do moonbag
                                        success = await self.close_position(
                                            symbol, pos.get("side"), close_qty,
                                            reason=f"HARVEST_{harvest_res.get('target_level', 'FIBO')}",
                                            is_partial=True
                                        )
                                        
                                        if success:
                                            # [V110.118] NÃO atualizar pos["size"] aqui!
                                            # close_position já fez isso internamente.
                                            # Apenas salvar o estado Paper.
                                            await self._save_paper_state()
                                            logger.info(f"✅ [PAPER-HARVEST] Colheita parcial de {symbol} executada com sucesso.")
                                        else:
                                            logger.error(f"❌ [PAPER-HARVEST] Falha ao executar colheita parcial de {symbol}.")

                                else:
                                    # Full Close
                                    logger.warning(f"🛑 [PAPER EXIT] {symbol} | Reason: {reason}")
                                    if qty > 0:
                                        await self.close_position(symbol, pos.get("side"), qty, reason=reason)
                                    
                                    await self._save_paper_state()
                                    if is_moonbag:
                                        # [V110.128.1] Use saved moon_uuid if available to avoid search failure
                                        target_id = pos.get("moon_uuid")
                                        if not target_id:
                                            moonbags = await sovereign_service.get_moonbags()
                                            target_moon = next((m for m in moonbags if m.get("symbol") == symbol), None)
                                            target_id = target_moon["id"] if target_moon else None
                                        
                                        if target_id:
                                            await sovereign_service.remove_moonbag(target_id, reason=reason)
                                        else:
                                            logger.warning(f"⚠️ [PAPER-GHOST-WARD] {symbol} (Moonbag) closed but no Firebase ID found to remove.")
                            except Exception as pe: logger.error(f"Error handling paper closure/harvest for {symbol}: {pe}")

                            # [V110.64 FIX] Removido free_slot() duplicado aqui.
                            # close_position() já faz hard_reset_slot() internamente.
                            # O duplo reset causava race conditions e slots "piscando".

                    except Exception as pos_error:
                        logger.error(f"❌ [PAPER POSITION ERROR] {symbol}: {pos_error}")
                        continue

                # UI PNL Pulse (Paper)
                if self.paper_positions:
                    # [V110.12.12] Safe ROI Calculation for UI
                    pnl_summary = []
                    for p in self.paper_positions:
                        p_sym = p.get("symbol")
                        p_price = price_map.get(p_sym, 0)
                        if p_price > 0:
                            entry = float(p.get("avgPrice", 0))
                            if entry > 0:
                                side = p.get("side", "Buy")
                                qty = float(p.get("size", 0))
                                lev = float(p.get("leverage", 50.0))
                                margin = float(p.get("entry_margin") or (qty * entry / lev))
                                roi = execution_protocol.calculate_roi(entry, p_price, side, leverage=lev)
                                # [V110.128] Standardized PnL Calculation: (ROI/100) * Margin
                                p_usd = (roi / 100.0) * margin
                                pnl_summary.append({
                                    "symbol": p_sym, 
                                    "roi": roi,
                                    "pnl_usd": round(p_usd, 2)
                                })
                    if pnl_summary:
                        await self.redis.publish_update("ui_updates", {"type": "PNL_PULSE", "data": pnl_summary})
                        # [V110.118 FIX-B] Publicar também no RTDB para que o PWA receba PnL dinâmico
                        # (o PWA assina RTDB, não Redis — sem isso o PnL fica estático)
                        if sovereign_service.rtdb:
                            try:
                                total_float_roi = sum(p["roi"] for p in pnl_summary)
                                total_float_pnl = sum(p["pnl_usd"] for p in pnl_summary)
                                await asyncio.to_thread(
                                    sovereign_service.rtdb.child("live_pnl").update,
                                    {
                                        "slots_roi": {p["symbol"]: round(p["roi"], 1) for p in pnl_summary},
                                        "slots_pnl": {p["symbol"]: round(p["pnl_usd"], 2) for p in pnl_summary},
                                        "total_float_roi": round(total_float_roi, 1),
                                        "total_float_pnl": round(total_float_pnl, 2),
                                        "active_count": len(pnl_summary),
                                        "updated_at": int(time.time() * 1000)
                                    }
                                )
                            except Exception:
                                pass  # Silencioso: não travar o loop por RTDB

            except Exception as e:
                logger.error(f"[PAPER ENGINE] Global Loop error: {e}")

            await asyncio.sleep(1)

    async def _release_emancipation_guard(self, symbol: str, delay: int = 15):
        """Libera a trava de emancipação após um delay de sincronização."""
        await asyncio.sleep(delay)
        self.emancipating_symbols.discard(symbol)

bybit_rest_service = BybitREST()

