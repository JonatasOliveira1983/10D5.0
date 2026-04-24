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

print("--- [V110.25.1] VAULT & SLOT PURGE (PRISTINE V5) ---")

# 1. Delete all 0.0 PnL trades from history
def clear_zero_pnl():
    docs = db.collection("trade_history").stream()
    count = 0
    for doc in docs:
        d = doc.to_dict()
        if abs(float(d.get("pnl", 0))) < 0.0001:
            doc.reference.delete()
            count += 1
    print(f"[OK] {count} zero PnL trades deleted from Vault.")

clear_zero_pnl()

# 2. Reset slots to ensure no stale data remains
reset_data = {
    "symbol": None, "side": None, "qty": 0, "entry_margin": 0, "opened_at": None,
    "fleet_intel": {}, "unified_confidence": 50, "entry_price": 0, "initial_stop": 0,
    "current_stop": 0, "target_price": 0, "status_risco": "LIVRE", "pnl_percent": 0,
    "slot_type": None, "pattern": None, "pensamento": "🔄 Reset Total V5",
    "maestria_guard_active": False, "rescue_activated": False, "rescue_resolved": False,
    "sentinel_retests": 0, "partial_tp_hit": False, "timestamp_last_update": time.time()
}

for i in range(1, 5):
    db.collection("slots_ativos").document(str(i)).set(reset_data)
rtdb_admin.reference("live_slots").delete()
print("[OK] Atomic Slots Reset.")

print("--- PRISTINE CLEAN V5 COMPLETE ---")
