
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def get_slot_intelligence():
    try:
        cred_path = "serviceAccountKey.json"
        if not os.path.exists(cred_path):
            print(f"Erro: {cred_path} não encontrado.")
            return

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        docs = db.collection("slots_ativos").stream()
        
        print(f"--- INTELIGÊNCIA DE OPERAÇÃO ---")
        for doc in docs:
            d = doc.to_dict()
            if d.get('symbol'):
                print(f"\n[SLOT {doc.id}] {d.get('symbol')}")
                print(f"Status: {d.get('status_risco')} | Visual: {d.get('visual_status')}")
                print(f"Lado: {d.get('side')} | Entrada: {d.get('entry_price')}")
                print(f"Pensamento: {d.get('pensamento')}")
                print(f"V42 Tag: {d.get('v42_tag')}")
                print(f"Score: {d.get('score')}")

    except Exception as e:
        print(f"Erro ao acessar Firestore: {e}")

if __name__ == "__main__":
    get_slot_intelligence()
