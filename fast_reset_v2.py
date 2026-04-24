
import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb
import os
import time

def fast_reset():
    if not firebase_admin._apps:
        cred = credentials.Certificate("1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app/'
        })
    
    db = firestore.client()
    
    # 1. Reset Banca Status
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
    db.collection("banca_status").document("global").set(banca_data)
    print("✅ Banca Status resetado para $100.00")
    
    # 2. Reset Slots (1-4)
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
    print("✅ 4 Slots táticos inicializados como LIVRE")

    # 3. Wipe Trade History & Vault History (Small batch)
    for coll in ["trade_history", "vault_history", "moonbags", "system_logs", "journey_signals"]:
        print(f"Limpando coleção: {coll}...")
        docs = db.collection(coll).limit(100).stream()
        count = 0
        for doc in docs:
            doc.reference.delete()
            count += 1
        print(f"✅ Removidos {count} itens de {coll}")

    # 4. RTDB Sync
    try:
        rtdb.reference('banca_status').set(banca_data)
        rtdb.reference('live_slots').delete() # Clear RTDB slots to force refresh
        print("✅ RTDB Sincronizado")
    except Exception as e:
        print(f"⚠️ Erro RTDB: {e}")

if __name__ == "__main__":
    fast_reset()
