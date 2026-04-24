import firebase_admin
from firebase_admin import credentials, firestore, db
import os

def fast_reset():
    print("Starting fast system reset...")
    cert_path = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
    if not os.path.exists(cert_path):
        print("Error: Credentials not found.")
        return

    try:
        cred = credentials.Certificate(cert_path)
        database_url = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"
        
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })
        
        firestore_db = firestore.client()
        rtdb = db.reference()

        # 1. Reset Slots in Firestore
        reset_data = {
            "symbol": None,
            "side": None,
            "entry_price": 0,
            "current_stop": 0,
            "target_price": None,
            "status_risco": "LIVRE",
            "pnl_percent": 0,
            "slot_type": None,
            "pensamento": "Fast Reset: Preparando para Teste Local",
            "visual_status": "IDLE"
        }
        for i in range(1, 5):
            firestore_db.collection("slots_ativos").document(str(i)).set(reset_data)
        print("Success: Slots 1-4 reset in Firestore.")

        # 2. Clear RTDB Nodes
        nodes_to_clear = ["radar_pulse", "live_slots", "market_radar", "system_state", "vault_status"]
        for node in nodes_to_clear:
            rtdb.child(node).delete()
        
        # 3. Initial Slots in RTDB
        rtdb_slots = {str(i): reset_data for i in range(1, 5)}
        rtdb.child("live_slots").set(rtdb_slots)
        
        # 4. Initialize Vault Status in RTDB
        rtdb.child("vault_status").set({
            "cycle_number": 1,
            "mega_cycle_number": 1,
            "mega_cycle_wins": 0,
            "cycle_start_bankroll": 100.0,
            "cycle_profit": 0.0,
            "total_trades_cycle": 0,
            "sniper_wins": 0,
            "used_symbols_in_cycle": [],
            "sniper_mode_active": True,
            "in_admiral_rest": False
        })
        print("Success: vault_status initialized with $100 bankroll.")
        
        # 5. Reset banca_status in Firestore
        banca_data = {
            "id": "status",
            "configured_balance": 100.0,
            "saldo_real_bybit": 100.0,
            "saldo_total": 100.0,
            "risco_real_percent": 0,
            "slots_disponiveis": 4,
            "lucro_total_acumulado": 0,
            "lucro_ciclo": 0,
            "vault_total": 0,
            "leverage": 50
        }
        firestore_db.collection("banca_status").document("status").set(banca_data)
        print("Success: banca_status reset with $100 and 50x leverage.")
        
        # 6. Reset vault cycle in Firestore  
        vault_cycle_data = {
            "cycle_number": 1,
            "mega_cycle_number": 1,
            "mega_cycle_wins": 0,
            "cycle_start_bankroll": 100.0,
            "cycle_profit": 0.0,
            "total_trades_cycle": 0,
            "sniper_wins": 0,
            "used_symbols_in_cycle": [],
            "min_score_threshold": 60,
            "sniper_mode_active": True,
            "in_admiral_rest": False
        }
        firestore_db.collection("vault_status").document("current_cycle").set(vault_cycle_data)
        print("Success: vault cycle in Firestore reset.")
        
        print("\nFAST RESET COMPLETED!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fast_reset()
