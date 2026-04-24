import firebase_admin
from firebase_admin import credentials, firestore
import os

def check_genesis():
    cred_path = "c:\\Users\\spcom\\Desktop\\10D REAL 4.0\\1CRYPTEN_SPACE_V4.0\\backend\\serviceAccountKey.json"
    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except:
        pass
        
    db = firestore.client()
    docs = db.collection("orders_genesis").limit(5).stream()
    print("--- FIRESTORE AUDIT: orders_genesis (last 5) ---")
    for doc in docs:
        d = doc.to_dict()
        print(f"ID: {doc.id} | Symbol: {d.get('symbol')} | Genesis ID: {d.get('genesis_id')}")

if __name__ == "__main__":
    check_genesis()
