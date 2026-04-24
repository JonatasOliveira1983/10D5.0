import asyncio
import os
import json
import logging
import sys

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sovereign_service import sovereign_service
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResetSystem")

async def reset_paper_storage():
    storage_file = "paper_storage.json"
    logger.info(f"📁 Resetting {storage_file}...")
    data = {
        "positions": [],
        "balance": 100.0,
        "history": []
    }
    with open(storage_file, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info("✅ paper_storage.json reset to $100.0 and no positions.")

async def reset_firestore():
    logger.info("🔥 Connecting to Firestore...")
    await sovereign_service.initialize()
    if not sovereign_service.is_active:
        logger.error("❌ Failed to connect to Firebase.")
        return

    # 1. Reset Banca Status
    logger.info("📊 Resetting banca_status/status...")
    banca_data = {
        "configured_balance": 100.0,
        "saldo_total": 100.0,
        "saldo_real_bybit": 0.0,
        "lucro_total_acumulado": 0.0,
        "lucro_ciclo": 0.0,
        "vault_total": 0.0,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4
    }
    await sovereign_service.update_banca_status(banca_data)

    # 2. Clear Trade History
    logger.info("📜 Clearing trade_history...")
    docs = sovereign_service.db.collection("trade_history").stream()
    count = 0
    batch = sovereign_service.db.batch()
    for doc in docs:
        batch.delete(doc.reference)
        count += 1
        if count % 400 == 0:
            batch.commit()
            batch = sovereign_service.db.batch()
    batch.commit()
    logger.info(f"✅ Cleared {count} trades from history.")
    
    # 2.1 Reset Vault Cycle
    logger.info("🏆 Resetting vault_management/current_cycle...")
    vault_doc = sovereign_service.db.collection("vault_management").document("current_cycle")
    # Using the default cycle structure from VaultService
    default_vault = {
        "sniper_wins": 0,
        "cycle_number": 1,
        "cycle_profit": 0.0,
        "cycle_losses": 0.0,
        "started_at": "2026-03-20T00:00:00Z",
        "in_admiral_rest": False,
        "rest_until": None,
        "vault_total": 0.0,
        "cautious_mode": False,
        "min_score_threshold": 75,
        "total_trades_cycle": 0,
        "cycle_gains_count": 0,
        "cycle_losses_count": 0,
        "accumulated_vault": 0.0,
        "sniper_mode_active": True,
        "used_symbols_in_cycle": [],
        "cycle_start_bankroll": 100.0,
        "next_entry_value": 10.0,
        "mega_cycle_wins": 0,
        "mega_cycle_total": 0,
        "mega_cycle_number": 1,
        "mega_cycle_profit": 0.0,
        "order_ids_processed": []
    }
    vault_doc.set(default_vault)
    logger.info("✅ Vault cycle reset.")

    # 3. Clear Slots
    logger.info("🎰 Resetting active slots (1-4)...")
    for i in range(1, 5):
        await sovereign_service.free_slot(i, reason="RESET SISTEMA V56 - CLEAN SLATE")
    
    # 4. Clear Logs & Signals (Optional but requested "limpar histórico")
    logger.info("🧹 Clearing system_logs and journey_signals...")
    for col in ["system_logs", "journey_signals", "banca_history"]:
        docs = sovereign_service.db.collection(col).stream()
        count = 0
        batch = sovereign_service.db.batch()
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = sovereign_service.db.batch()
        batch.commit()
        logger.info(f"✅ Cleared {count} docs from {col}.")

    # 5. Reset RTDB nodes
    if sovereign_service.rtdb:
        logger.info("🛰️ Resetting Realtime DB nodes...")
        sovereign_service.rtdb.child("live_slots").delete()
        sovereign_service.rtdb.child("vault_status").set({
            "cycle_profit": 0,
            "vault_total": 0,
            "updated_at": 0
        })
        logger.info("✅ RTDB reset.")

async def main():
    logger.info("🚀 STARTING GLOBAL SYSTEM RESET (PAPER MODE)...")
    await reset_paper_storage()
    await reset_firestore()
    logger.info("🏁 RESET COMPLETE! The system is now 100% clean and ready for V56.0.")

if __name__ == "__main__":
    asyncio.run(main())
