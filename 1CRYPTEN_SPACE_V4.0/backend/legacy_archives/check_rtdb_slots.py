
import firebase_admin
from firebase_admin import credentials, db
import json
import os

def check_live_slots():
    try:
        cred_path = "serviceAccountKey.json"
        
        if not os.path.exists(cred_path):
            print(f"Erro: {cred_path} não encontrado.")
            return

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app'
            })

        ref = db.reference('live_slots')
        slots = ref.get()
        
        print(f"--- LIVE SLOTS NO RTDB ---")
        if slots:
            # slots can be a list or a dict
            if isinstance(slots, list):
                for i, s in enumerate(slots):
                    if s:
                        print(f"Slot {i}: {s.get('symbol')} | Status: {s.get('status_risco')} | Side: {s.get('side')}")
            else:
                for k, s in slots.items():
                    print(f"Slot {k}: {s.get('symbol')} | Status: {s.get('status_risco')} | Side: {s.get('side')}")
        else:
            print("Nenhum slot encontrado no RTDB.")

    except Exception as e:
        print(f"Erro ao acessar RTDB: {e}")

if __name__ == "__main__":
    check_live_slots()
