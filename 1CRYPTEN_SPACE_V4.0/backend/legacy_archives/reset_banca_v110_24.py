# -*- coding: utf-8 -*-
"""
[V110.24.0] Targeted Banca Reset — Reseta apenas os numbers da banca para $100.
NÃO apaga slots ativos nem histórico de vault.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import firebase_admin
from firebase_admin import credentials, firestore
import time

KEY_PATH = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

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
print("[V110.24.0] Banca resetada para $100.00 com sucesso!")
print("   configured_balance: $100.00")
print("   saldo_total: $100.00")
print("   lucro_acumulado: $0.00")
