# -*- coding: utf-8 -*-
import firebase_admin
from firebase_admin import credentials, firestore, db
import os
import json
import time

# --- CONFIGURAÇÃO ---
DB_URL = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"
CRED_PATH = "serviceAccountKey.json"
PAPER_STORAGE = "paper_storage.json"

def nuclear_reset():
    print("Iniciando RESET NUCLEAR V110.130 (Producao + Local)...")

    # 1. Inicializar Firebase
    if not os.path.exists(CRED_PATH):
        print(f"Erro: {CRED_PATH} nao encontrado!")
        return

    cred = credentials.Certificate(CRED_PATH)
    try:
        firebase_admin.initialize_app(cred, {
            'databaseURL': DB_URL
        })
    except ValueError:
        pass # Já inicializado

    fs = firestore.client()
    
    # --- FIRESTORE ---

    # A. Limpar Históricos e Estados (Deep Scrub)
    collections_to_wipe = [
        'vault_history', 'trade_history', 'moonbags', 'system_logs', 
        'banca_history', 'journey_signals', 'orders_genesis',
        'system_state', 'admiral_consciousness'
    ]
    
    for coll in collections_to_wipe:
        print(f"Limpando colecao Firestore: {coll}...")
        docs = fs.collection(coll).limit(500).stream()
        count = 0
        batch = fs.batch()
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
        if count > 0:
            batch.commit()
            print(f"OK: {count} documentos deletados de {coll}.")
        else:
            print(f"Colecao {coll} ja estava vazia.")

    # B. Resetar Banca Status
    print("Resetando banca para $100.00 no Firestore...")
    fs.collection('banca_status').document('status').set({
        "saldo_total": 100.0,
        "cycle_profit": 0.0,
        "lucro_total_acumulado": 0.0,
        "cycle_start_bankroll": 100.0,
        "vault_total": 0.0,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4,
        "status": "ONLINE",
        "last_update": time.time(),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        "total_trades_cycle": 0,
        "sniper_wins": 0
    })

    # C. Resetar Slots táticos
    print("Resetando slots taticos no Firestore...")
    for i in range(1, 5):
        fs.collection('slots_ativos').document(str(i)).set({
            "id": i,
            "symbol": None,
            "side": None,
            "qty": 0,
            "entry_price": 0,
            "current_stop": 0,
            "status_risco": "LIVRE",
            "pnl_percent": 0,
            "timestamp_last_update": time.time()
        })

    # --- REALTIME DATABASE ---
    print("Limpando Realtime Database...")
    try:
        ref = db.reference("/")
        
        # Resetar live_slots
        slots_reset = {}
        for i in range(1, 5):
            slots_reset[str(i)] = {
                "id": i, "symbol": None, "status_risco": "LIVRE", "pnl_percent": 0
            }
        
        ref.update({
            "live_slots": slots_reset,
            "moonbag_vault": {},
            "banca_status": {
                "saldo_total": 100.0,
                "cycle_profit": 0.0,
                "lucro_total_acumulado": 0.0,
                "cycle_start_bankroll": 100.0,
                "vault_total": 0.0,
                "risco_real_percent": 0.0,
                "last_update": time.time() * 1000,
                "total_trades_cycle": 0,
                "sniper_wins": 0
            },
            "system_pulse": {"status": "RESET", "timestamp": time.time() * 1000},
            "btc_command_center": {"btc_drag_mode": False, "btc_price": 0},
            "chat_history": {},
            "system_cooldowns": {}
        })
        print("OK: RTDB limpo e sincronizado.")
    except Exception as e:
        print(f"Erro ao limpar RTDB: {e}")

    # --- LOCAL PAPER STORAGE ---
    print("Resetando paper_storage.json local...")
    try:
        initial_state = {
            "balance": 100.0,
            "slots": {},
            "history": [],
            "last_sync": time.time()
        }
        with open(PAPER_STORAGE, 'w') as f:
            json.dump(initial_state, f, indent=4)
        print("OK: Local paper_storage.json resetado.")
    except Exception as e:
        print(f"Erro ao resetar arquivo local: {e}")

    print("\nRESET NUCLEAR V110.130 CONCLUIDO COM SUCESSO!")
    print("A UI em https://1crypten.space/ deve refletir a banca de $100 e histórico vazio agora.")

if __name__ == "__main__":
    nuclear_reset()
