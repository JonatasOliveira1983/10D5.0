import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb
import os
from datetime import datetime, timezone

BANKROLL = 100.0
LEVERAGE = 50

cert = "serviceAccountKey.json"
rtdb_url = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"

if not firebase_admin._apps:
    firebase_admin.initialize_app(credentials.Certificate(cert), {"databaseURL": rtdb_url})

fdb = firestore.client()
now = datetime.now(timezone.utc)

def wipe_collection(coll_name):
    print(f"Limpeza de {coll_name} (Firestore)...", flush=True)
    count = 0
    while True:
        docs = list(fdb.collection(coll_name).limit(500).stream())
        if not docs: break
        batch = fdb.batch()
        for d in docs: batch.delete(d.reference)
        batch.commit()
        count += len(docs)
    print(f" -> Removidos {count} de {coll_name}")

print("--- EXTERMINACAO FINAL V110.137 ---")

# 1. Firestore
wipe_collection("trade_history")
wipe_collection("moonbags")
wipe_collection("orders_genesis")

# 2. RTDB
print("Limpando RTDB completo...", flush=True)
rtdb.reference("trade_history").delete()
rtdb.reference("moonbag_vault").delete()
rtdb.reference("radar_pulse").delete()
rtdb.reference("system_pulse").delete()
rtdb.reference("live_slots").delete()
rtdb.reference("orders_genesis").delete()
rtdb.reference("system_logs").delete()

# 3. Restaura Banca
print("Restaurando Banca de Dados...", flush=True)
banca = {
    "id": "status", "configured_balance": BANKROLL, "saldo_real_bybit": 0.0,
    "saldo_total": BANKROLL, "risco_real_percent": 0.0, "slots_disponiveis": 4, 
    "lucro_total_acumulado": 0.0, "lucro_ciclo": 0.0, "vault_total": 0.0,
    "leverage": LEVERAGE, "status": "ONLINE", "timestamp_last_update": now.timestamp()
}
fdb.collection("banca_status").document("status").set(banca)
fdb.collection("banca_status").document("global").set(banca)
rtdb.reference("banca_status").set(banca)

fdb.collection("vault_management").document("current_cycle").set({
    "cycle_number": 1, "mega_cycle_number": 1, "vault_total": 0.0,
    "cycle_bankroll": BANKROLL, "min_score_threshold": 60, "sniper_mode_active": True
})
rtdb.reference("vault_status").set({
    "cycle_number": 1, "mega_cycle_number": 1, "vault_total": 0.0,
    "sniper_mode_active": True
})

# 4. Restaura Slots Limpos
print("Restaurando Slots...", flush=True)

for i in range(1, 5):
    slot_limpo = {
        "id": i, "symbol": None, "side": None, "entry_price": 0, "current_stop": 0, 
        "target_price": 0, "status_risco": "LIVRE", "pnl_percent": 0, 
        "qty": 0, "leverage": LEVERAGE, "timestamp_last_update": now.timestamp()
    }
    fdb.collection("slots_ativos").document(str(i)).set(slot_limpo)
    rtdb.reference("live_slots").child(str(i)).set(slot_limpo)

print("TUDO LIMPO. BEM-VINDO A V110.137!")
