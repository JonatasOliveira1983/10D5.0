import asyncio
import sys
import os
import firebase_admin
from firebase_admin import credentials, firestore

def check_sync():
    print("Initializing Firebase for quick check...")
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cred_path = os.path.join(backend_dir, "serviceAccountKey.json")
    
    if not os.path.exists(cred_path):
        print(f"Error: {cred_path} not found")
        return

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    print("\n--- ACTIVE SLOTS (Firestore) ---")
    slots = db.collection("slots_ativos").stream()
    for s in slots:
        data = s.to_dict()
        print(f"Slot {s.id}: {data.get('symbol')} | {data.get('side')} | ROI: {data.get('pnl_percent')}% | Status: {data.get('status_risco')}")

    print("\n--- MOONBAGS (Vault) ---")
    mbgs = db.collection("moonbags").stream()
    for m in mbgs:
        data = m.to_dict()
        print(f"Vault {m.id}: {data.get('symbol')} | ROI: {data.get('pnl_percent')}%")

if __name__ == "__main__":
    check_sync()
