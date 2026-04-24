# -*- coding: utf-8 -*-
import os
import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb_admin
import time
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")
RTDB_URL = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred, {'databaseURL': RTDB_URL})

db = firestore.client()

def check():
    print("--- [V110.25.5] SLOT VERIFICATION ---")
    docs = db.collection('slots_ativos').order_by('__name__').stream()
    for d in docs:
        data = d.to_dict()
        symbol = data.get("symbol")
        margin = data.get("entry_margin")
        stop = data.get("current_stop")
        side = data.get("side")
        status = data.get("status_risco")
        
        print(f"Slot {d.id}: {symbol} | {side} | Status: {status} | Margin: ${margin} | SL: {stop}")
    
    print("\nBanca Meta:")
    banca = db.collection('banca_status').document('status').get().to_dict()
    print(f"Saldo Total: ${banca.get('saldo_total')} | Lucro Ciclo: ${banca.get('lucro_ciclo')}")
    
if __name__ == "__main__":
    check()
