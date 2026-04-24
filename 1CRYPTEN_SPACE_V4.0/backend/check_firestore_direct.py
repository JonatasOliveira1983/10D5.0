
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def check_firestore_slots():
    try:
        cred_path = "serviceAccountKey.json"
        
        if not os.path.exists(cred_path):
            print(f"Erro: {cred_path} não encontrado.")
            return

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        
        # Consultar Slots Ativos
        docs = db.collection("slots_ativos").stream()
        
        print(f"--- RESULTADO FIRESTORE (slots_ativos) ---")
        found = False
        for doc in docs:
            d = doc.to_dict()
            print(f"Slot {doc.id}: {d.get('symbol')} | Status: {d.get('status_risco')}")
            if d.get('symbol'):
                found = True
        
        if not found:
            print("Nenhum símbolo ativo encontrado nos slots do Firestore.")

    except Exception as e:
        print(f"Erro ao acessar Firestore: {e}")

if __name__ == "__main__":
    check_firestore_slots()
