# -*- coding: utf-8 -*-
import os
import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb_admin
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")
RTDB_URL = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred, {'databaseURL': RTDB_URL})

db = firestore.client()

print("--- [V110.25.4] TOTAL PRISTINE CLEAN V4 ---")

# 1. Reset Banca Status
clean_banca = {
    "id": "status",
    "configured_balance": 100.0,
    "saldo_total": 100.0,
    "lucro_ciclo": 0.0,
    "lucro_total_acumulado": 0.0,
    "vault_total": 0.0,
    "risco_real_percent": 0.0,
    "slots_disponiveis": 4,
    "leverage": 50,
    "status": "ONLINE",
    "timestamp_last_update": time.time()
}
db.collection("banca_status").document("status").set(clean_banca)
rtdb_admin.reference("banca_status").set(clean_banca)
print("[OK] Banca Hard Reset.")

# 2. Force Clear Slots
for i in range(1, 5):
    db.collection("slots_ativos").document(str(i)).delete()
rtdb_admin.reference("live_slots").delete()
print("[OK] Slots Deleted.")

# 3. Wipe Vault status
rtdb_admin.reference("vault").delete()
rtdb_admin.reference("vault_status").delete()

# 4. Final collection wipe
for c in ["trade_history", "journey_signals"]:
    docs = db.collection(c).limit(100).stream()
    for d in docs: d.reference.delete()

print("[OK] Total Pristine Clean V4 Complete.")
