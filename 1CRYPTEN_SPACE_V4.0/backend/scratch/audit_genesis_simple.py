import firebase_admin
from firebase_admin import credentials, firestore
import os

def audit_slots():
    cred_path = "c:\\Users\\spcom\\Desktop\\10D REAL 4.0\\1CRYPTEN_SPACE_V4.0\\backend\\serviceAccountKey.json"
    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except:
        pass
    db = firestore.client()
    docs = db.collection("slots_ativos").limit(4).stream()
    for doc in docs:
        print(f"SLOT {doc.id}: {doc.to_dict().keys()}")
        print(f"GENESIS_ID: {doc.to_dict().get('genesis_id')}")

if __name__ == "__main__":
    audit_slots()
