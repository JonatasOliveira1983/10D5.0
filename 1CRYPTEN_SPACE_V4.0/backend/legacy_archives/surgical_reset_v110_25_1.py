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

print("--- [V110.25.1] SURGICAL UI RESET ---")

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

# 2. Reset Active Slots (Ensure all 4 are LIVRE)
clean_slot = {
    "symbol": None, "side": None, "qty": 0, "entry_margin": 0, "opened_at": None,
    "entry_price": 0, "current_stop": 0, "status_risco": "LIVRE", "pnl_percent": 0,
    "timestamp_last_update": time.time()
}
for i in range(1, 5):
    db.collection("slots_ativos").document(str(i)).set(clean_slot)
rtdb_admin.reference("live_slots").set({str(i): clean_slot for i in range(1, 5)})
print("[OK] Slots Reset.")

# 3. Reset Vault Metrics (RTDB)
clean_vault = {
    "cycle_bankroll": 100.0,
    "cycle_gains_count": 0,
    "cycle_losses": 0.0,
    "cycle_losses_count": 0,
    "cycle_number": 1,
    "cycle_profit": 0.0,
    "cycle_start_bankroll": 100.0,
    "mega_cycle_profit": 0.0,
    "mega_cycle_total": 0,
    "mega_cycle_wins": 0,
    "next_entry_value": 10.0,
    "order_ids_processed": [],
    "sniper_wins": 0,
    "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "total_trades_cycle": 0,
    "updated_at": int(time.time() * 1000),
    "used_symbols_in_cycle": [],
    "vault_total": 0.0
}
rtdb_admin.reference("vault").set(clean_vault)
print("[OK] Vault Metrics Reset.")

# 4. Wipe Moonbags (Firestore & RTDB)
try:
    rtdb_admin.reference("moonbag_vault").delete()
    # For firestore moonbags, we just delete the collection recursively (small enough hopefully)
    docs = db.collection("moonbags").stream()
    for doc in docs:
        doc.reference.delete()
    print("[OK] Moonbags wiped.")
except Exception as e:
    print(f"[WARN] Moonbag wipe error: {e}")

# 5. Clear Paper State Persistence
db.collection("paper_state").document("current").delete()
print("[OK] Paper State wiped.")

print("--- SURGICAL RESET COMPLETE ---")
