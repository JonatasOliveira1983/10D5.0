import asyncio
import os
import sys
import json

# Fix Windows console encoding for emojis
sys.stdout.reconfigure(encoding='utf-8')

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service

async def nuclear_reset():
    print("☢️  [NUCLEAR-RESET V110.171] Starting full Estado Zero...")
    
    # 1. Initialize services
    await firebase_service.initialize()
    await bybit_rest_service.initialize()
    
    # 2. Cancel all exchange orders
    print("🚫 Canceling all exchange orders...")
    try:
        await bybit_rest_service.cancel_all_orders()
    except Exception as e:
        print(f"⚠️  Failed to cancel orders: {e}")

    # 3. Clear all 4 slots in Firestore + RTDB
    print("\n🧹 Clearing all active slots...")
    for i in range(1, 5):
        await firebase_service.free_slot(i, reason="NUCLEAR_RESET_V110_171")
        print(f"   ✅ Slot {i} cleared.")
    
    # 4. Purge trade_history collection
    print("\n🗑️  Purging trade_history collection...")
    try:
        trades = await firebase_service.get_trade_history(limit=5000)
        deleted = 0
        for trade in trades:
            doc_id = trade.get("id")
            if doc_id:
                firebase_service.db.collection("trade_history").document(doc_id).delete()
                deleted += 1
        print(f"   ✅ Deleted {deleted} trade history records.")
    except Exception as e:
        print(f"   ⚠️  Error purging trade_history: {e}")

    # 5. Purge orders_genesis collection
    print("\n🗑️  Purging orders_genesis collection...")
    try:
        import asyncio as aio
        genesis_docs = await aio.to_thread(firebase_service.db.collection("orders_genesis").get)
        deleted_g = 0
        for doc in genesis_docs:
            doc.reference.delete()
            deleted_g += 1
        print(f"   ✅ Deleted {deleted_g} genesis records.")
    except Exception as e:
        print(f"   ⚠️  Error purging orders_genesis: {e}")

    # 6. Reset bankroll to $100
    print("\n💰 Resetting bankroll to $100...")
    await firebase_service.update_banca_status({
        "id": "status",
        "saldo_real_bybit": 0,
        "risco_real_percent": 0,
        "slots_disponiveis": 4,
        "lucro_total_acumulado": 0,
        "lucro_ciclo": 0,
        "vault_total": 0,
        "saldo_total": 100.0,
        "configured_balance": 100.0
    })
    print("   ✅ Bankroll reset to $100.")

    # 7. Clear Paper Storage File
    paper_path = os.path.join(backend_dir, "paper_storage.json")
    if os.path.exists(paper_path):
        print("\n📄 Clearing paper_storage.json...")
        empty_data = {"positions": [], "updated_at": 0}
        with open(paper_path, 'w') as f:
            json.dump(empty_data, f, indent=2)
        await firebase_service.update_paper_state(empty_data)
        print("   ✅ paper_storage.json cleared.")
        
    # 8. Clear RAM positions
    bybit_rest_service.paper_positions = []
    
    print("\n✅ [ESTADO ZERO COMPLETO] Sistema 100% limpo. Pronto para novo ciclo.")

if __name__ == "__main__":
    asyncio.run(nuclear_reset())

