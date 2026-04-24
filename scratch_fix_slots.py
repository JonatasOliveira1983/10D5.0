import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb

cert = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
rtdb_url = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"
firebase_admin.initialize_app(credentials.Certificate(cert), {"databaseURL": rtdb_url})
fdb = firestore.client()

for i in range(1, 5):
    # Update RTDB
    rtdb.reference("live_slots").child(str(i)).update({"id": i, "slot_type": None})
    # Update Firestore
    fdb.collection("slots_ativos").document(str(i)).update({"id": i, "slot_type": None})
    print(f"Slot {i} id updated.")
