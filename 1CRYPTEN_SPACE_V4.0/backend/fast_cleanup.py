import asyncio
import os
import sys

# Define base path to ensure relative imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service

async def fast_clean():
    print("Starting fast system cleanup...")
    await firebase_service.initialize()
    
    if not firebase_service.is_active:
        print("Firebase NOT active. Check credentials.")
        return

    # 1. Clear slots
    print("Clearing 4 active slots...")
    for i in range(1, 5):
        await firebase_service.free_slot(i, "Nuclear Reset V110.30.1")
    
    # 2. Reset bankroll to 100
    print("Resetting bankroll to 100.00...")
    reset_data = {
        "configured_balance": 100.0,
        "saldo_total": 100.0,
        "lucro_ciclo": 0.0,
        "lucro_total_acumulado": 0.0,
        "vault_total": 0.0,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4,
        "status": "ONLINE"
    }
    await firebase_service.update_banca_status(reset_data)
    
    # 3. Clear History collections (limit 500 to avoid long waits)
    collections = ["trade_history", "banca_history", "system_logs", "journey_signals", "moonbags"]
    for col in collections:
        print(f"Cleaning collection: {col}...")
        docs = firebase_service.db.collection(col).limit(500).stream()
        batch = firebase_service.db.batch()
        count = 0
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
        if count > 0:
            batch.commit()
        print(f"Deleted {count} documents from {col}.")

    print("Cleanup finished successfully!")

if __name__ == "__main__":
    asyncio.run(fast_clean())
