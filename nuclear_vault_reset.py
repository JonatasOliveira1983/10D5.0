import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import firebase_admin
from firebase_admin import credentials, firestore, db
import os
from datetime import datetime, timezone

BANKROLL = 100.0
LEVERAGE = 50

cert = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
rtdb_url = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"

print("RESET CIRURGICO - Banca $100 + Vault History")
print("-" * 45)

if not os.path.exists(cert):
    print("ERRO: serviceAccountKey.json nao encontrado.")
    sys.exit(1)

if not firebase_admin._apps:
    firebase_admin.initialize_app(credentials.Certificate(cert), {"databaseURL": rtdb_url})

fdb  = firestore.client()
rtdb = db.reference()
now  = datetime.now(timezone.utc)

# ── 1. LIMPA trade_history (historico da Vault UI) ──────────
print("1/4  Limpando trade_history (Vault UI)...", flush=True)
count = 0
while True:
    docs = list(fdb.collection("trade_history").limit(500).stream())
    if not docs: break
    b = fdb.batch()
    for d in docs: b.delete(d.reference)
    b.commit()
    count += len(docs)
print("     -> %d registros removidos." % count)

# ── 2. RESET banca_status -> $100 ───────────────────────────
print("2/4  banca_status -> $100...", flush=True)
banca = {
    "id": "status",
    "configured_balance": BANKROLL, "saldo_real_bybit": 0.0,
    "saldo_total": BANKROLL, "risco_real_percent": 0.0,
    "slots_disponiveis": 4, "lucro_total_acumulado": 0.0,
    "lucro_ciclo": 0.0, "vault_total": 0.0,
    "leverage": LEVERAGE, "status": "ONLINE",
    "timestamp_last_update": now.timestamp()
}
fdb.collection("banca_status").document("status").set(banca)
rtdb.child("banca_status").set(banca)
print("     -> OK  $%.2f" % BANKROLL)

# ── 3. RESET vault_management/current_cycle ─────────────────
print("3/4  vault_management/current_cycle...", flush=True)
fdb.collection("vault_management").document("current_cycle").set({
    "cycle_number": 1, "mega_cycle_number": 1,
    "mega_cycle_wins": 0, "mega_cycle_total": 0, "mega_cycle_profit": 0.0,
    "cycle_start_bankroll": BANKROLL, "cycle_bankroll": BANKROLL,
    "cycle_profit": 0.0, "cycle_losses": 0.0, "total_trades_cycle": 0,
    "cycle_gains_count": 0, "cycle_losses_count": 0, "sniper_wins": 0,
    "used_symbols_in_cycle": [], "min_score_threshold": 60,
    "sniper_mode_active": True, "in_admiral_rest": False,
    "rest_until": None, "vault_total": 0.0, "cautious_mode": False,
    "accumulated_vault": 0.0, "next_entry_value": BANKROLL * 0.10,
    "started_at": now.isoformat()
})
rtdb.child("vault_status").set({
    "cycle_number": 1, "mega_cycle_number": 1,
    "cycle_profit": 0.0, "total_trades_cycle": 0,
    "sniper_wins": 0, "vault_total": 0.0,
    "sniper_mode_active": True, "in_admiral_rest": False
})
print("     -> Ciclo #1 OK")

# ── 4. RESET slots_ativos 1-4 ────────────────────────────────
print("4/4  Slots 1-4...", flush=True)
slot_limpo = {
    "symbol": None, "side": None, "entry_price": 0,
    "current_stop": 0, "initial_stop": 0, "target_price": 0,
    "status_risco": "LIVRE", "pnl_percent": 0, "slot_type": None,
    "pensamento": "Reset Cirurgico V3.0", "entry_margin": 0,
    "qty": 0, "leverage": LEVERAGE, "score": 0,
    "fleet_intel": {}, "unified_confidence": 50,
    "timestamp_last_update": now.timestamp()
}
b2 = fdb.batch()
for i in range(1, 5):
    b2.set(fdb.collection("slots_ativos").document(str(i)), slot_limpo)
b2.commit()
for i in range(1, 5):
    rtdb.child("live_slots").child(str(i)).set(slot_limpo)
print("     -> Slots 1-4 LIVRES OK")

print("-" * 45)
print("CONCLUIDO! Banca: $%.2f | Historico: LIMPO" % BANKROLL)
