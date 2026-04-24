
import firebase_admin
from firebase_admin import credentials, firestore

cert_path = "c:/Users/spcom/Desktop/10D-3.0/1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
cred = credentials.Certificate(cert_path)
try:
    firebase_admin.initialize_app(cred)
except:
    pass

fs = firestore.client()

print("--- INICIALIZANDO SLOTS NO FIRESTORE ---")
for i in range(1, 5):
    slot_ref = fs.collection("active_slots").document(str(i))
    slot_data = {
        "id": i,
        "symbol": None,
        "side": None,
        "status": "WAITING",
        "pnl_percent": 0.0,
        "opened_at": 0
    }
    slot_ref.set(slot_data)
    print(f"Slot {i} criado/resetado com sucesso.")

print("\n--- PRONTO ---")
