# -*- coding: utf-8 -*-
"""
Injeta as 4 posicoes na coleção CORRETA: system_state/paper_engine
"""
import firebase_admin
from firebase_admin import credentials, firestore as fs_admin
import time

cred = credentials.Certificate("serviceAccountKey.json")
try:
    firebase_admin.initialize_app(cred)
except Exception:
    pass

db = fs_admin.client()

TS = time.time()

POSITIONS = [
    {"symbol": "WUSDT",    "side": "Buy", "avgPrice": "0.0137", "size": "394.0",  "leverage": "50", "stopLoss": "0.0134", "takeProfit": "0.0150", "status": "IN_TRADE", "is_paper": True, "entry_margin": 10.82, "slot_id": 1, "opened_at": TS, "slot_type": "SNIPER"},
    {"symbol": "XRPUSDT",  "side": "Buy", "avgPrice": "1.34",   "size": "404.0",  "leverage": "50", "stopLoss": "1.33",   "takeProfit": "1.47",   "status": "IN_TRADE", "is_paper": True, "entry_margin": 10.82, "slot_id": 2, "opened_at": TS, "slot_type": "SNIPER"},
    {"symbol": "DOTUSDT",  "side": "Buy", "avgPrice": "1.28",   "size": "422.0",  "leverage": "50", "stopLoss": "1.26",   "takeProfit": "1.41",   "status": "IN_TRADE", "is_paper": True, "entry_margin": 10.82, "slot_id": 3, "opened_at": TS, "slot_type": "SNIPER"},
    {"symbol": "LINKUSDT", "side": "Buy", "avgPrice": "9.01",   "size": "60.0",   "leverage": "50", "stopLoss": "8.89",   "takeProfit": "9.91",   "status": "IN_TRADE", "is_paper": True, "entry_margin": 10.81, "slot_id": 4, "opened_at": TS, "slot_type": "SNIPER"},
]

state = {
    "positions": POSITIONS,
    "moonbags":  [],
    "balance":   129.46,
    "history":   [],
    "updated_at": TS,
}

db.collection("system_state").document("paper_engine").set(state, merge=True)
print("paper_engine atualizado com 4 posicoes!")
print("WUSDT | XRPUSDT | DOTUSDT | LINKUSDT")
