import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sovereign_service import sovereign_service

async def force_firestore_purge():
    print("INICIANDO EXPURGO TOTAL FIRESTORE (V80.8)...")
    await sovereign_service.initialize()
    
    collections = ['trades', 'vault_cycle', 'moonbags', 'logs', 'system_events']
    
    for coll_name in collections:
        print(f"Limpando colecao: {coll_name}")
        docs = await asyncio.to_thread(sovereign_service.db.collection(coll_name).get)
        
        batch = sovereign_service.db.batch()
        count = 0
        deleted = 0
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
            deleted += 1
            if count >= 400:
                await asyncio.to_thread(batch.commit)
                batch = sovereign_service.db.batch()
                count = 0
        
        if count > 0:
            await asyncio.to_thread(batch.commit)
        print(f"OK: {deleted} documentos removidos de {coll_name}.")

    # Reset System Bankroll
    await asyncio.to_thread(
        sovereign_service.db.collection('system').document('bankroll').set,
        {
            "total_balance": 100.0,
            "available_balance": 100.0,
            "accumulated_pnl": 0.0,
            "trade_count": 0
        }
    )
    print("OK: Banca mestre resetada para $100.00")

if __name__ == "__main__":
    asyncio.run(force_firestore_purge())
