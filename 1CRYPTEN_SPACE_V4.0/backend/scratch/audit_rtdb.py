import firebase_admin
from firebase_admin import credentials, db
import os

def audit_rtdb():
    cred_path = "c:\\Users\\spcom\\Desktop\\10D REAL 4.0\\1CRYPTEN_SPACE_V4.0\\backend\\serviceAccountKey.json"
    cred = credentials.Certificate(cred_path)
    # Get DB URL from config
    db_url = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"
    
    try:
        firebase_admin.initialize_app(cred, {'databaseURL': db_url})
    except:
        pass
        
    ref = db.reference("live_slots")
    slots = ref.get()
    print("--- RTDB AUDIT: live_slots ---")
    if slots:
        if isinstance(slots, list):
            for i, s in enumerate(slots):
                if s:
                    print(f"Slot {i}: {s.get('symbol')} | Genesis ID: {s.get('genesis_id')} | Order ID: {s.get('order_id')}")
        else:
            for k, v in slots.items():
                print(f"Slot {k}: {v.get('symbol')} | Genesis ID: {v.get('genesis_id')} | Order ID: {v.get('order_id')}")
    else:
        print("No slots found in RTDB.")

if __name__ == "__main__":
    audit_rtdb()
