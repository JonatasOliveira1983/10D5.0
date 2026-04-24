
import firebase_admin
from firebase_admin import credentials, firestore, db
import os

cert_path = "c:/Users/spcom/Desktop/10D-3.0/1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
cred = credentials.Certificate(cert_path)
try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app'
    })
except:
    pass

fs = firestore.client()
rtdb = db.reference()

print("=== FIRESTORE SLOTS ===")
for i in range(1, 5):
    doc = fs.collection("active_slots").document(str(i)).get()
    if doc.exists:
        data = doc.to_dict()
        symbol = data.get("symbol", "EMPTY")
        status = data.get("status", "N/A")
        print(f"Slot {i}: {symbol} | Status: {status}")
    else:
        print(f"Slot {i}: NOT FOUND")

print("\n=== RTDB SNIPER_PULSE (Signals) ===")
signals = rtdb.child("sniper_pulse").get()
if signals:
    count = len(signals)
    print(f"Total Signals: {count}")
    # Print first 2 for debug
    for k, v in list(signals.items())[:2]:
        print(f"  - {k}: {v.get('side')} {v.get('score')} {v.get('outcome')}")
else:
    print("No signals in RTDB.")
