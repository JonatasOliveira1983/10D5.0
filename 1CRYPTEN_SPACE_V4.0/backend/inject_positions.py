# -*- coding: utf-8 -*-
"""
Injeta as 4 posicoes diretamente no Firestore slots_ativos e no paper_state
usando o firebase_service com inicializacao correta.
"""
import asyncio, sys, time
sys.path.insert(0, ".")

import firebase_admin
from firebase_admin import credentials, firestore as fs_admin, db as rtdb_admin

# Carrega credenciais
cred = credentials.Certificate("serviceAccountKey.json")
try:
    app = firebase_admin.initialize_app(cred, {
        "databaseURL": "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"
    })
except Exception:
    app = firebase_admin.get_app()

db = fs_admin.client()
rtdb = rtdb_admin.reference("/")

import time as _time

ENTRIES = {
    "WUSDT":    {"entry": 0.0137, "stop": 0.0134, "target": 0.0150, "qty": 394.0,  "margin": 10.82, "slot": 1},
    "XRPUSDT":  {"entry": 1.34,   "stop": 1.33,   "target": 1.47,   "qty": 404.0,  "margin": 10.82, "slot": 2},
    "DOTUSDT":  {"entry": 1.28,   "stop": 1.26,   "target": 1.41,   "qty": 422.0,  "margin": 10.82, "slot": 3},
    "LINKUSDT": {"entry": 9.01,   "stop": 8.89,   "target": 9.91,   "qty": 60.0,   "margin": 10.81, "slot": 4},
}

TS = _time.time()

print("=" * 60)
print("1. ATUALIZANDO SLOTS_ATIVOS NO FIRESTORE")
print("=" * 60)

for sym, d in ENTRIES.items():
    slot_data = {
        "symbol":              sym,
        "side":                "Buy",
        "entry_price":         d["entry"],
        "current_stop":        d["stop"],
        "initial_stop":        d["stop"],
        "target_price":        d["target"],
        "structural_target":   d["target"],
        "qty":                 d["qty"],
        "entry_margin":        d["margin"],
        "leverage":            50.0,
        "slot_type":           "SNIPER",
        "status":              "IN_TRADE",
        "status_risco":        "ATIVO",
        "pnl_percent":         0,
        "score":               80,
        "unified_confidence":  80,
        "sentinel_first_hit_at": 0,
        "maestria_guard_active": False,
        "rescue_activated":    False,
        "rescue_resolved":     False,
        "sentinel_retests":    0,
        "partial_tp_hit":      False,
        "opened_at":           TS,
        "timestamp_last_update": TS,
        "fleet_intel":         {},
        "pensamento":          f"V110.28.2: Posicao reinjetada - {sym}",
        "market_regime":       "TRENDING",
        "is_ranging_sniper":   False,
    }
    slot_id = str(d["slot"])
    db.collection("slots_ativos").document(slot_id).set(slot_data, merge=True)
    rtdb.child("live_slots").child(slot_id).update(slot_data)
    print(f"  Slot {slot_id} ({sym}): entry={d['entry']} stop={d['stop']} -> Firestore + RTDB OK")

print()
print("=" * 60)
print("2. SALVANDO PAPER_STATE NO FIRESTORE")
print("=" * 60)

positions = []
for sym, d in ENTRIES.items():
    positions.append({
        "symbol":       sym,
        "side":         "Buy",
        "avgPrice":     str(d["entry"]),
        "size":         str(d["qty"]),
        "leverage":     "50",
        "stopLoss":     str(d["stop"]),
        "takeProfit":   str(d["target"]),
        "status":       "IN_TRADE",
        "is_paper":     True,
        "entry_margin": d["margin"],
        "slot_id":      d["slot"],
        "opened_at":    TS,
        "slot_type":    "SNIPER",
    })

paper_state = {
    "positions": positions,
    "moonbags":  [],
    "balance":   129.46,
    "history":   [],
    "updated_at": TS,
}
db.collection("paper_state").document("current").set(paper_state)
print(f"  paper_state salvo: {len(positions)} posicoes | balance=$129.46")

print()
print("=" * 60)
print("FEITO! Reinicie o backend para carregar as posicoes.")
print("=" * 60)
