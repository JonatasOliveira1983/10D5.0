
import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb
import os
import json

def absolute_nuke():
    # 1. Initialize Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate("1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app/'
        })
    
    db = firestore.client()
    
    # 2. Wipe Firestore Collections
    collections = ["trade_history", "vault_history", "banca_history", "signals_history", "slots_ativos", "banca_status", "logs", "moonbags"]
    
    for coll_name in collections:
        print(f"Limpanfo Firestore: {coll_name}...")
        docs = db.collection(coll_name).list_documents()
        deleted = 0
        for doc in docs:
            doc.delete()
            deleted += 1
        print(f"Deletados {deleted} de {coll_name}")

    # 3. Wipe RTDB
    try:
        print("Limpando RTDB globalmente...")
        rtdb.reference('/').delete()
        print("RTDB 100% LIMPO.")
    except Exception as e:
        print(f"Erro RTDB: {e}")

    import time
    # 5. Initialize Slots (1-4)
    print("Inicializando 4 Slots Ativos...")
    for i in range(1, 5):
        empty_slot = {
            "id": i,
            "symbol": None,
            "side": None,
            "qty": 0,
            "entry_price": 0,
            "current_stop": 0,
            "status_risco": "LIVRE",
            "pnl_percent": 0,
            "timestamp_last_update": time.time()
        }
        db.collection("slots_ativos").document(str(i)).set(empty_slot)
    
    # 6. Reset Banca Status specifically
    banca_data = {
        "saldo_total": 100.0,
        "configured_balance": 100.0,
        "lucro_total_acumulado": 0.0,
        "lucro_ciclo": 0.0,
        "vault_total": 0.0,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4,
        "status": "ONLINE",
        "timestamp_last_update": time.time()
    }
    db.collection("banca_status").document("status").set(banca_data)
    db.collection("banca_status").document("global").set(banca_data) # Legacy support
    
    # RTDB Sync for UI immediate update
    try:
        rtdb.reference('banca_status').set(banca_data)
        print("Banca Status resetado para $100.00 em Firestore e RTDB")
    except:
        pass

if __name__ == "__main__":
    absolute_nuke()
