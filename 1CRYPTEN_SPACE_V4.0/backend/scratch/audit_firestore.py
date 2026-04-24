import firebase_admin
from firebase_admin import credentials, firestore
import os

def audit_firestore():
    cred_path = "c:\\Users\\spcom\\Desktop\\10D REAL 4.0\\1CRYPTEN_SPACE_V4.0\\backend\\serviceAccountKey.json"
    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except:
        pass
        
    db = firestore.client()
    docs = db.collection("slots_ativos").stream()
    print("--- FIRESTORE AUDIT: slots_ativos ---")
    for doc in docs:
        d = doc.to_dict()
        print(f"Slot {doc.id}: {d.get('symbol')} | Genesis ID: {d.get('genesis_id')} | Order ID: {d.get('order_id')}")

if __name__ == "__main__":
    audit_firestore()
