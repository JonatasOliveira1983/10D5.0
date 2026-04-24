# -*- coding: utf-8 -*-
"""
[V110.25.0] NUCLEAR SYSTEM RESET — Pristine state (Banca $100, empty history).
Clears Firestore & RTDB.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb_admin
import time
import json

# Define working directory safely
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

# Load configuration for RTDB URL if possible
RTDB_URL = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred, {'databaseURL': RTDB_URL})

db = firestore.client()

def delete_collection(coll_ref, batch_size=50):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    if deleted >= batch_size:
        return deleted + delete_collection(coll_ref, batch_size)
    return deleted

print("--- [V110.25.0] NUCLEAR RESET INITIATED ---")

# 1. Reset Banca Status (Firestore & RTDB)
reset_data = {
    "configured_balance": 100.0,
    "saldo_total": 100.0,
    "lucro_ciclo": 0.0,
    "lucro_total_acumulado": 0.0,
    "vault_total": 0.0,
    "risco_real_percent": 0.0,
    "slots_disponiveis": 4,
    "status": "ONLINE",
    "timestamp_last_update": time.time()
}
db.collection("banca_status").document("status").set(reset_data)
try:
    rtdb_admin.reference("banca_status").set(reset_data)
    print("[OK] Banca Metadata: Reset to $100.00 (Firestore & RTDB)")
except Exception as e:
    print(f"[WARN] RTDB Banca Reset Error: {e} (Continuing...)")

# 2. Reset Active Slots (Firestore & RTDB)
reset_slot = {
    "symbol": None, "side": None, "qty": 0, "entry_margin": 0, "opened_at": None,
    "entry_price": 0, "current_stop": 0, "status_risco": "LIVRE", "pnl_percent": 0,
    "timestamp_last_update": time.time()
}
for i in range(1, 5):
    db.collection("slots_ativos").document(str(i)).set(reset_slot)
try:
    rtdb_admin.reference("live_slots").set({str(i): reset_slot for i in range(1, 5)})
    print("[OK] Active Slots: Reset to LIVRE (Firestore & RTDB)")
except Exception as e:
    print(f"[ERROR] RTDB Slots Reset Error: {e}")

# 3. Clear History Collections (Firestore)
collections_to_wipe = ["trade_history", "banca_history", "system_logs", "journey_signals", "moonbags"]
for coll in collections_to_wipe:
    count = delete_collection(db.collection(coll))
    print(f"[OK] Collection {coll}: {count} documents deleted.")

# 4. Clear Paper State (Firestore)
db.collection("paper_state").document("current").delete()
print("[OK] Paper State Persistence: Cleared.")

# 5. Clear RTDB Vaults (RTDB)
try:
    rtdb_admin.reference("moonbag_vault").delete()
    print("[OK] RTDB Moonbag Vault: Cleared.")
except Exception as e:
    print(f"[ERROR] RTDB Vault Reset Error: {e}")

print("--- NUCLEAR RESET COMPLETE [V110.25.0] ---")
