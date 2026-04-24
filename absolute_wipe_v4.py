
import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb
import os
import time
import sys

def absolute_wipe():
    print("☢️ [NUCLEAR WIPE V4] Iniciando limpeza atômica...", flush=True)
    
    try:
        if not firebase_admin._apps:
            cred_path = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app/'
            })
        
        db = firestore.client()
        
        # 1. Reset Banca Status ($100.00)
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
        print("✅ Banca Firestore resetada para $100.00", flush=True)
        
        # 2. Reset Slots Ativos (LIVRE)
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
        print("✅ Slots Firestore inicializados como LIVRE", flush=True)

        # 3. Limpeza Profunda (Batch delete)
        collections = ["trade_history", "vault_history", "moonbags", "system_logs", "journey_signals"]
        for coll_name in collections:
            print(f"Limpando coleção: {coll_name}...", flush=True)
            docs = db.collection(coll_name).limit(500).get()
            count = 0
            for doc in docs:
                doc.reference.delete()
                count += 1
            print(f"✅ Removidos {count} documentos de '{coll_name}'", flush=True)

        # 4. Sincronização RTDB
        rtdb.reference('banca_status').set(banca_data)
        rtdb.reference('live_slots').delete()
        rtdb.reference('trade_history').delete()
        rtdb.reference('vault_history').delete()
        print("✅ RTDB Sincronizado.", flush=True)

        # 5. Local files
        for f in ["paper_storage.json", "vault_storage.json"]:
            if os.path.exists(f):
                os.remove(f)
                print(f"✅ Removido local: {f}", flush=True)

        print("\n🏁 [RESET COMPLETO]", flush=True)

    except Exception as e:
        print(f"❌ ERRO FATAL: {e}", flush=True)

if __name__ == "__main__":
    absolute_wipe()
