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

    async def validate_active_flow(self):
        """Heuristic check on currently active slots."""
        slots = await sovereign_service.get_active_slots()
        for s in slots:
            if s.get("symbol") and not s.get("genesis_id"):
                logger.warning(f"⚠️ FlowSentinel: Slot {s['id']} ({s['symbol']}) is active but lacks a Genesis ID!")

# Singleton
flow_sentinel = FlowSentinel()
