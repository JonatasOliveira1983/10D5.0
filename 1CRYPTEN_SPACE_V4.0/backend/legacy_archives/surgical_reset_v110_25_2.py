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

print("--- [V110.25.2] FINAL NUCLEAR SURGICAL RESET ---")

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

# 2. Reset Active Slots
clean_slot = {
    "symbol": None, "side": None, "qty": 0, "entry_margin": 0, "opened_at": None,
    "entry_price": 0, "current_stop": 0, "status_risco": "LIVRE", "pnl_percent": 0,
    "timestamp_last_update": time.time()
}
for i in range(1, 5):
    db.collection("slots_ativos").document(str(i)).set(clean_slot)
rtdb_admin.reference("live_slots").set({str(i): clean_slot for i in range(1, 5)})
print("[OK] Slots Reset.")

# 3. Reset Vault Metrics (Targeting BOTH 'vault' and 'vault_status')
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
rtdb_admin.reference("vault_status").set(clean_vault)
print("[OK] Vault Metrics Reset (Dual Keys).")

# 4. Final Sweep on Collections
colls = ["trade_history", "banca_history", "system_logs", "journey_signals", "moonbags"]
for c in colls:
    docs = db.collection(c).limit(200).stream()
    for d in docs: d.reference.delete()
print("[OK] Collections Sweep (Limit 200).")

# 5. RTDB Pulse and State reset
rtdb_admin.reference("moonbag_vault").delete()
rtdb_admin.reference("paper_state").delete()
print("[OK] RTDB State reset.")

print("--- FINAL RESET COMPLETE [V110.25.2] ---")
