
import firebase_admin
from firebase_admin import credentials, db
import time
import os

def inject_sync_test():
    cred_path = "serviceAccountKey.json"
    if not os.path.exists(cred_path):
        print(f"Erro: {cred_path} não encontrado.")
        return

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app'
        })

    # Slot 1: Trade que 'ainda' está no slot tático
    slot_ref = db.reference('live_slots/1')
    slot_data = {
        "id": 1,
        "symbol": "BTCUSDT",
        "side": "Buy",
        "entry_price": 65000,
        "current_stop": 64500,
        "status_risco": "PROTECTED",
        "pnl_percent": 2.5,
        "timestamp_last_update": time.time()
    }
    slot_ref.set(slot_data)
    print("[OK] Injetado BTCUSDT no Slot 1")

    # Moonbag Vault: A mesma trade já promovida
    moon_ref = db.reference('moonbag_vault/BTCUSDT_TEST')
    moon_data = {
        "id": "BTCUSDT_TEST",
        "symbol": "BTCUSDT",
        "side": "Buy",
        "entry_price": 65000,
        "current_stop": 66000,
        "status": "EMANCIPATED",
        "pnl_percent": 15.0,
        "timestamp_last_update": time.time()
    }
    moon_ref.set(moon_data)
    print("[OK] Injetada BTCUSDT no Moonbag Vault")
    print("[INFO] Agora a UI deve filtrar o Slot 1 e mostrar apenas a Moonbag!")

if __name__ == "__main__":
    inject_sync_test()
