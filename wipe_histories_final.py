
import firebase_admin
from firebase_admin import credentials, firestore
import os

def wipe_all_histories():
    if not firebase_admin._apps:
        cred = credentials.Certificate("1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    collections = ["trade_history", "vault_history", "banca_history", "signals_history"]
    
    for coll_name in collections:
        print(f"Limpando coleção: {coll_name}...")
        docs = db.collection(coll_name).limit(500).get()
        deleted = 0
        for doc in docs:
            doc.reference.delete()
            deleted += 1
        print(f"Deletados {deleted} documentos de {coll_name}")

    # Também limpar os slots ativos no RTDB apenas por segurança
    from firebase_admin import db as rtdb
    try:
        # Re-init for RTDB if needed
        ref = rtdb.reference('slots_ativos')
        ref.delete()
        print("RTDB slots_ativos deletados.")
    except Exception as e:
        print(f"Erro ao limpar RTDB: {e}")

if __name__ == "__main__":
    wipe_all_histories()
