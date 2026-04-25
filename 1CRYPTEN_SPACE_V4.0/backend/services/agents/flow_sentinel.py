import logging
import asyncio
import time
from typing import Dict, Any, List
from services.sovereign_service import sovereign_service
from services.database_service import database_service
from services.agents.aios_adapter import AIOSAgent

logger = logging.getLogger("FlowSentinel")

class FlowSentinel(AIOSAgent):
    """
    V110.210: Flow Integrity Agent.
    Monitors the lifecycle of a trade from Signal -> Slot -> TradeHistory.
    Ensures zero data loss and validates Genesis ID consistency.
    """
    def __init__(self):
        super().__init__(
            agent_id="agent-flow-sentinel",
            role="integrity_guardian",
            capabilities=["flow_validation", "archival_audit", "self_healing"]
        )
        self.is_running = False
        self.audit_interval = 60 # Check every minute
        self.pending_slots = {} # slot_id -> {symbol, genesis_id, timestamp}

    async def start(self):
        self.is_running = True
        logger.info("🛡️ FlowSentinel ONLINE: Safeguarding trade lifecycle integrity.")
        asyncio.create_task(self.run_loop())

    async def stop(self):
        self.is_running = False
        logger.info("🛡️ FlowSentinel OFFLINE.")

    async def run_loop(self):
        while self.is_running:
            try:
                await self.perform_integrity_audit()
                await self.perform_self_healing() # [V110.230] Continuous Sync Guard
            except Exception as e:
                logger.error(f"FlowSentinel Audit Error: {e}")
            await asyncio.sleep(self.audit_interval)

    async def notify_reset(self, slot_id: int, symbol: str, genesis_id: str, pnl: float):
        """Called by SovereignService when a slot is cleared."""
        logger.info(f"📥 FlowSentinel: Notified of reset for {symbol} (Slot {slot_id}). Tracking archival...")
        self.pending_slots[slot_id] = {
            "symbol": symbol,
            "genesis_id": genesis_id,
            "pnl": pnl,
            "timestamp": time.time()
        }

    async def perform_integrity_audit(self):
        """Validates that all recently cleared slots have corresponding history entries."""
        if not self.pending_slots:
            return

        logger.info(f"🔍 FlowSentinel: Auditing {len(self.pending_slots)} pending archivals...")
        
        # 1. Fetch recent history
        history = await database_service.get_trade_history(limit=20)
        history_genesis_ids = {t.get("genesis_id") for t in history if t.get("genesis_id")}
        
        resolved_ids = []
        for slot_id, data in self.pending_slots.items():
            gen_id = data["genesis_id"]
            symbol = data["symbol"]
            
            # Check if it exists in history
            if gen_id in history_genesis_ids:
                logger.info(f"✅ FlowSentinel: Archival confirmed for {symbol} ({gen_id}).")
                resolved_ids.append(slot_id)
            else:
                # If it's been pending for more than 5 minutes and not in history, we have a problem
                age = time.time() - data["timestamp"]
                if age > 300:
                    logger.critical(f"🚨 FlowSentinel: INTEGRITY BREACH! {symbol} ({gen_id}) cleared but NOT found in History after 5min.")
                    await sovereign_service.log_event("INTEGRITY", f"MIA Trade: {symbol} ({gen_id}) missing from history.", "CRITICAL")
                    # TODO: Self-healing from emergency_trades.json or exchange recovery
                else:
                    logger.warning(f"⏳ FlowSentinel: Archival pending for {symbol} ({gen_id}). Age: {int(age)}s")

        # Cleanup resolved
        for s_id in resolved_ids:
            del self.pending_slots[s_id]

    async def perform_self_healing(self):
        """
        [V110.230] SELF-HEALING: Compara a memória (cache) com o banco de dados.
        Se houver divergência, o banco manda na memória e o WebSocket atualiza a UI.
        """
        try:
            db_slots = await database_service.get_active_slots()
            if not db_slots: return
            
            mem_slots = sovereign_service.slots_cache
            divergence = False
            
            for db_s in db_slots:
                slot_id = db_s.get("id")
                # Encontra o slot correspondente na memória
                mem_s = next((s for s in mem_slots if s["id"] == slot_id), None)
                
                if mem_s:
                    # Compara o símbolo (o indicador mais básico de ocupação)
                    if mem_s.get("symbol") != db_s.get("symbol"):
                        logger.warning(f"🔧 FlowSentinel: DIVERGENCE DETECTED on Slot {slot_id}! Memory: {mem_s.get('symbol')} vs DB: {db_s.get('symbol')}")
                        divergence = True
                        break
            
            if divergence:
                logger.info("🛠️ FlowSentinel: Executing Self-Healing Sync...")
                await sovereign_service.initialize() # Recarrega do banco
                from services.websocket_service import websocket_service
                await websocket_service.emit_slots(sovereign_service.slots_cache)
                logger.info("✅ FlowSentinel: System state healed and broadcasted.")
                
        except Exception as e:
            logger.error(f"FlowSentinel Self-Healing Error: {e}")

    async def on_message(self, message: Any):
        """Implementação obrigatória da classe abstrata AIOSAgent."""
        pass

# Singleton
flow_sentinel = FlowSentinel()
