
import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb
import os

def check_status():
    if not firebase_admin._apps:
        cred = credentials.Certificate("1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app/'
        })
    
    db = firestore.client()
    
    banca_status = db.collection("banca_status").document("status").get().to_dict()
    print(f"Banca Status (status): {banca_status}")
    
    slots = db.collection("slots_ativos").stream()
    print("Slots Ativos:")
    for slot in slots:
        print(f"Slot {slot.id}: {slot.to_dict()}")

if __name__ == "__main__":
    check_status()
