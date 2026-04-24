# -*- coding: utf-8 -*-
# 1CRYPTEN_SPACE_V4.0 - V110.175 Railway Sovereign Service
# Este serviço opera exclusivamente via WebSocket e Postgres local.
import asyncio
import logging
import datetime
import time
from collections import deque
from config import settings
from services.websocket_service import websocket_service
from services.database_service import database_service

logger = logging.getLogger("SovereignService")

class SovereignService: # Nome atualizado para refletir a soberania Railway
    def __init__(self):
        self.is_active = True # Railway Sovereign Mode
        self.log_buffer = deque(maxlen=100) 
        self.signal_buffer = deque(maxlen=100)
        self.slots_cache = [{"id": i, "symbol": None, "entry_price": 0, "current_stop": 0, "status_risco": "LIVRE", "pnl_percent": 0} for i in range(1, 5)]
        self.radar_pulse_cache = {"signals": [], "decisions": [], "updated_at": 0}
        self.rtdb = None # Legacy Firebase RTDB Stub
        self.db = None   # Legacy Firebase Firestore Stub

    async def initialize(self):
        logger.info("🚂 [RAILWAY-SOVEREIGN] Sovereign Service initialized. Native Stack ACTIVE.")
        return True

    def _make_json_safe(self, data):
        if isinstance(data, dict):
            return {str(k): self._make_json_safe(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_json_safe(item) for item in data]
        elif hasattr(data, 'isoformat'):
            return data.isoformat()
        return data

    async def get_banca_status(self):
        return {"saldo_total": 0, "risco_real_percent": 0, "slots_disponiveis": 4, "status": "SOVEREIGN"}

    async def update_banca_status(self, data: dict):
        try:
            asyncio.create_task(database_service.update_banca_status(data))
            await websocket_service.emit_banca_status(data)
            return data
        except Exception as e:
            logger.error(f"Error in Sovereign banca update: {e}")
            return data

    async def log_trade(self, trade_data: dict):
        try:
            asyncio.create_task(database_service.log_trade(trade_data))
        except Exception as e:
            logger.error(f"Error logging Sovereign trade: {e}")

    async def update_slot(self, slot_id: int, data: dict):
        for s in self.slots_cache:
            if s["id"] == slot_id:
                s.update(data)
                break
        try:
            asyncio.create_task(database_service.update_slot(slot_id, data))
            await websocket_service.emit_slots(self.slots_cache)
        except Exception as e:
            logger.error(f"Error in Sovereign slot update: {e}")
        return data

    async def log_signal(self, signal_data: dict):
        signal_data["id"] = f"loc_{int(time.time() * 1000)}"
        signal_data["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.signal_buffer.appendleft(signal_data)
        await websocket_service.emit_radar_pulse(list(self.signal_buffer)[:50])
        return signal_data["id"]

    async def log_event(self, agent: str, message: str, level: str = "INFO"):
        data = {"agent": agent, "message": message, "level": level, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        self.log_buffer.appendleft(data)
        await websocket_service.broadcast({"type": "SYSTEM_EVENT", "data": data})
        return data

    async def update_pulse_drag(self, btc_drag_mode: bool, btc_cvd: float, exhaustion: float, 
                                 btc_price: float = 0, btc_var_1h: float = 0,
                                 btc_adx: float = 0, decorrelation_avg: float = 0, btc_var_24h: float = 0,
                                 btc_dominance: float = 0, btc_var_15m: float = 0,
                                 btc_direction: str = 'LATERAL',
                                 oracle_context: dict = None):
        try:
            payload = {
                "btc_drag_mode": btc_drag_mode, "btc_cvd": btc_cvd, "exhaustion": exhaustion,
                "btc_price": btc_price, "btc_variation_1h": btc_var_1h, "btc_variation_24h": btc_var_24h,
                "btc_adx": btc_adx, "decorrelation_avg": decorrelation_avg, "btc_dominance": btc_dominance,
                "btc_var_15m": btc_var_15m, "btc_direction": btc_direction, "timestamp": time.time() * 1000
            }
            if oracle_context: payload.update(oracle_context)
            await websocket_service.broadcast({"type": "btc_command_center", "data": payload})
        except Exception as e:
            logger.error(f"Error in Sovereign pulse update: {e}")

    async def free_slot(self, slot_id: int, reason: str = "Released"):
        """
        [V110.203] DATA INTEGRITY PROTECTION: Archiving slot data before reset.
        Prevents trade loss during automated cleanups or system reboots.
        """
        try:
            # 1. Fetch current slot data from source of truth
            slots_list = await database_service.get_active_slots()
            slot = next((s for s in slots_list if s["id"] == slot_id), None)
            
            if slot and slot.get("symbol"):
                logger.info(f"🛡️ [V110.203] Archiving {slot['symbol']} (Slot {slot_id}) to Vault before cleanup.")
                
                # 2. Map slot data to TradeHistory format
                trade_data = {
                    "order_id": slot.get("order_id") or f"CLEANUP_{int(time.time())}",
                    "genesis_id": slot.get("genesis_id"),
                    "symbol": slot.get("symbol"),
                    "side": slot.get("side", "BUY"),
                    "pnl": float(slot.get("pnl_usd") or 0.0),
                    "pnl_percent": float(slot.get("pnl_percent") or 0.0),
                    "entry_price": float(slot.get("entry_price") or 0.0),
                    "exit_price": float(slot.get("current_price") or 0.0),
                    "strategy": slot.get("pattern", "UNKNOWN"),
                    "close_reason": reason,
                    "data": {**slot, "archived_at": time.time(), "archived_reason": reason}
                }
                
                # 3. Save to Persistent History
                await database_service.log_trade(trade_data)
                logger.info(f"✅ [V110.203] {slot['symbol']} archived successfully in TradeHistory.")
                
        except Exception as e:
            logger.error(f"❌ [V110.203] Data Integrity Failure for Slot {slot_id}: {e}")
            # We still proceed with the reset to avoid locking the slot forever,
            # but the error is logged for audit.

        # 4. Clear the slot
        await self.update_slot(slot_id, {
            "symbol": None, 
            "status_risco": "LIVRE", 
            "pnl_percent": 0, 
            "timestamp_last_update": time.time(), 
            "pensamento": f"🔄 {reason}"
        })
        return True

    async def get_radar_pulse(self):
        return self.radar_pulse_cache

    async def update_vault_pulse(self, status: dict):
        try:
            await websocket_service.broadcast({"type": "VAULT_PULSE", "data": status})
        except: pass

    # Implementation for Sovereign Mode [V110.187]
    async def register_order_genesis(self, data: dict):
        try:
            await database_service.register_order_genesis(data)
            return data.get("order_id")
        except Exception as e:
            logger.error(f"Error registering Sovereign genesis: {e}")
            return None

    async def get_order_genesis(self, order_id: str):
        try:
            return await database_service.get_order_genesis(order_id)
        except Exception as e:
            logger.error(f"Error getting Sovereign genesis: {e}")
            return None
    async def promote_to_moonbag(self, slot_id: int): return None
    async def get_moonbags(self, **kwargs): return []
    async def update_moonbag(self, uuid, data): pass
    async def remove_moonbag(self, uuid, reason): pass
    async def get_recent_signals(self, limit: int = 100): return list(self.signal_buffer)[:limit]
    async def get_recent_logs(self, limit: int = 50): return list(self.log_buffer)[:limit]
    async def update_bankroll(self, balance: float): await self.update_banca_status({"saldo_total": balance})
    async def log_banca_snapshot(self, data: dict): pass
    async def get_banca_history(self, limit: int = 50): return []
    async def get_chat_status(self): return {"is_thinking": False}
    async def get_librarian_intel(self): return {}
    async def get_radar_grid(self): return {}
    async def get_active_slots(self, **kwargs): return self.slots_cache
    async def get_trade_history(self, **kwargs): return []
    async def get_trade_history_stats(self, **kwargs): return {"total_count": 0, "total_pnl": 0.0}
    async def get_vault_history(self, limit: int = 50): return []
    async def hard_reset_slot(self, slot_id, reason, pnl=0.0): return await self.free_slot(slot_id, reason)
    async def get_doc(self, path): return {"exists": False, "data": {}}
    async def set_doc(self, path, data): return True
    async def get_collection(self, path): return []
    async def get_paper_state(self): return {}
    async def update_paper_state(self, data): return True
    async def get_all_moonbags(self): return []
    async def is_symbol_blocked(self, symbol): return False, 0
    async def register_sl_cooldown(self, symbol, duration): pass
    async def get_system_bias(self): return {}
    async def update_radar_batch(self, batch): pass
    async def update_system_state(self, *args, **kwargs): pass
    async def update_signal_outcome(self, *args, **kwargs): pass

    async def update_radar_pulse(self, signals: list, decisions: list, market_context: dict):
        """Atualiza e transmite o pulso do Radar."""
        self.radar_pulse_cache = {
            "signals": signals,
            "decisions": decisions,
            "updated_at": time.time()
        }
        await websocket_service.update_radar_pulse(signals, decisions, market_context)
        return True

# Singleton instance - O NOVO SOBERANO
sovereign_service = SovereignService()
