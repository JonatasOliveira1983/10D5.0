import asyncio
import os
import sys
import time

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sovereign_service import sovereign_service

async def deep_clean():
    print("STARTING DEEP CLEAN (V84.4)...")
    await sovereign_service.initialize()
    
    # 1. Firestore Collections
    colls = ['trade_history', 'trades', 'vault_cycle', 'vault_management', 'moonbags', 'logs', 'system_logs', 'system_events', 'banca_status']
    
    for coll_name in colls:
        print(f"Cleaning Firestore: {coll_name}...")
        docs = await asyncio.to_thread(sovereign_service.db.collection(coll_name).get)
        batch = sovereign_service.db.batch()
        count = 0
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
            if count >= 400:
                await asyncio.to_thread(batch.commit)
                batch = sovereign_service.db.batch()
                count = 0
        await asyncio.to_thread(batch.commit)
        print(f"OK: {coll_name} cleared.")

    # 2. Reset to $100.00
    status_doc = {
        "configured_balance": 100.0,
        "saldo_total": 100.0,
        "saldo_real_bybit": 0.0,
        "lucro_total_acumulado": 0.0,
        "lucro_ciclo": 0.0,
        "vault_total": 0.0,
        "trade_count": 0,
        "updated_at": time.time()
    }
    await asyncio.to_thread(sovereign_service.db.collection('banca_status').document('status').set, status_doc)
    print("OK: Bankroll set to $100.00")

    # 3. RTDB Wipe Out
    if sovereign_service.rtdb:
        print("Cleaning RTDB...")
        targets = ["banca_status", "system/bankroll", "vault", "active_slots", "signals", "radar"]
        for target in targets:
            await asyncio.to_thread(sovereign_service.rtdb.child(target).remove)
        
        await asyncio.to_thread(sovereign_service.rtdb.child("banca_status").set, status_doc)
        await asyncio.to_thread(sovereign_service.rtdb.child("system/bankroll").set, status_doc)
        print("OK: RTDB Purified.")

    print("\nPURGE COMPLETE! REBIRTH READY.")

if __name__ == "__main__":
    asyncio.run(deep_clean())
