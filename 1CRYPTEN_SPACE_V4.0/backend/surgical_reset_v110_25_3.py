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

print("--- [V110.25.3] TOTAL PURGE & PRISTINE RESET ---")

# 1. Clear Banca Status (Hard Reset)
clean_banca = {
    "id": "status",
    "configured_balance": 100.0,
    "saldo_total": 100.0,
    "saldo_real_bybit": 0.0,
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

# 2. Reset Active Slots (Ensure all LIVRE)
clean_slot = {
    "symbol": None, "side": None, "qty": 0, "entry_margin": 0, "opened_at": None,
    "entry_price": 0, "current_stop": 0, "status_risco": "LIVRE", "pnl_percent": 0,
    "timestamp_last_update": time.time()
}
for i in range(1, 5):
    db.collection("slots_ativos").document(str(i)).set(clean_slot)
rtdb_admin.reference("live_slots").set({str(i): clean_slot for i in range(1, 5)})
print("[OK] Slots Reset.")

# 3. Clear History Thoroughly
colls = ["trade_history", "banca_history", "system_logs", "journey_signals", "moonbags"]
for c in colls:
    deleted = 0
    docs = db.collection(c).limit(500).stream()
    for d in docs:
        d.reference.delete()
        deleted += 1
    print(f"[OK] Collection {c}: {deleted} docs deleted.")

# 4. Clear RTDB Pulse, Vault and Status
rtdb_admin.reference("vault").set(None)
rtdb_admin.reference("vault_status").set(None)
rtdb_admin.reference("moonbag_vault").set(None)
rtdb_admin.reference("paper_state").set(None)
print("[OK] RTDB History/State wiped.")

print("--- FINAL PRISTINE RESET COMPLETE ---")
