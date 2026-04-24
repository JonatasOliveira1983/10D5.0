
import firebase_admin
from firebase_admin import credentials, db
import json
import os

def check_all_rtdb():
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

        ref = db.reference('/')
        all_data = ref.get()
        
        print(f"--- ESTRUTURA RTDB ---")
        if all_data:
            for key in all_data.keys():
                print(f"Node: {key}")
                if key == "live_slots":
                    print(json.dumps(all_data[key], indent=2))
                if key == "tocaias":
                     print(f"  Contém {len(all_data[key]) if all_data[key] else 0} itens")
        else:
            print("RTDB vazio.")

    except Exception as e:
        print(f"Erro ao acessar RTDB: {e}")

if __name__ == "__main__":
    check_all_rtdb()
