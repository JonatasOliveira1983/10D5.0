import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

def audit_slots():
    # 1. Load credentials
    cred_path = "c:\\Users\\spcom\\Desktop\\10D REAL 4.0\\1CRYPTEN_SPACE_V4.0\\backend\\serviceAccountKey.json"
    if not os.path.exists(cred_path):
        print("Credentials not found.")
        return

    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except:
        pass
        
    db = firestore.client()
    
    print("--- AUDIT: SLOTS ATIVOS ---")
    slots = db.collection("slots_ativos").stream()
    for doc in slots:
        data = doc.to_dict()
        print(f"Slot {doc.id}: {data.get('symbol')} | Genesis ID: {data.get('genesis_id')}")

if __name__ == "__main__":
    audit_slots()
