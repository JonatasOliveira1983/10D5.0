import asyncio
import os
import sys
import json
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service
from config import settings

async def uber_reset_v80():
    print("--- UBER RESET V80: INICIANDO LIMPEZA TOTAL ---")
    
    # 0. Initialize Firebase
    await firebase_service.initialize()
    if not firebase_service.db:
        print("Erro: Falha ao inicializar banco de dados Firebase.")
        return
    paper_file = "paper_storage.json"
    initial_data = {
        "positions": [],
        "balance": 100.0,
        "history": []
    }
    with open(paper_file, 'w') as f:
        json.dump(initial_data, f, indent=2)
    print("OK: paper_storage.json resetado para $100.00")
    
    # 2. Clear Firestore Collections
    collections_to_clear = ['trades', 'vault_cycle', 'moonbags', 'logs']
    for coll in collections_to_clear:
        docs = await asyncio.to_thread(firebase_service.db.collection(coll).get)
        batch = firebase_service.db.batch()
        count = 0
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
            if count >= 400: # Batch limit
                await asyncio.to_thread(batch.commit)
                batch = firebase_service.db.batch()
                count = 0
        await asyncio.to_thread(batch.commit)
        print(f"OK: Colecao '{coll}' limpa no Firestore.")

    # 3. Reset Slots
    for i in range(1, 5):
        await firebase_service.hard_reset_slot(i, reason="Uber Reset V80")
    print("OK: Todos os slots resetados.")

    # 4. Reset Global Bankroll & System State
    await firebase_service.update_system_state(
        "SCANNING", 
        0, 
        "Banca Restaurada para $100.00 (V80.6)", 
        protocol="Sniper V15.1"
    )
    
    # Update Bankroll in RTDB/Firestore
    await asyncio.to_thread(
        firebase_service.db.collection('system').document('bankroll').set,
        {
            "total_balance": 100.0,
            "available_balance": 100.0,
            "updated_at": time.time()
        }
    )
    print("OK: Banca global resetada no Firestore/RTDB.")

    print("\n--- RESET CONCLUÍDO COM SUCESSO! ---")

if __name__ == "__main__":
    asyncio.run(uber_reset_v80())
