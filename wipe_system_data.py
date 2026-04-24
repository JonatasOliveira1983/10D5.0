import firebase_admin
from firebase_admin import credentials, firestore, db
import os
import json

def wipe_data():
    print("Starting system data wipe...")
    
    # Tentativa de carregar credenciais
    cert_path = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
    if not os.path.exists(cert_path):
        print("Error: Credentials not found at:", cert_path)
        return

    try:
        cred = credentials.Certificate(cert_path)
        # Database URL explicita do .env para garantir conexão
        database_url = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"
        
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })
        
        firestore_db = firestore.client()
        rtdb = db.reference()

        print("--- FIRESTORE ---")
        
        # 1. Limpar Sinais (journey_signals)
        print("Deleting signals from 'journey_signals'...")
        signals_ref = firestore_db.collection("journey_signals")
        docs = signals_ref.stream()
        count = 0
        for doc in docs:
            doc.reference.delete()
            count += 1
        print(f"Success: {count} signals deleted.")

        # 2. Resetar Slots (slots_ativos)
        print("Resetting slots in 'slots_ativos'...")
        reset_data = {
            "symbol": None,
            "side": None,
            "entry_price": 0,
            "current_stop": 0,
            "target_price": None,
            "status_risco": "LIVRE",
            "pnl_percent": 0,
            "slot_type": None,
            "pensamento": "Reset Manual: Limpeza de Sistema",
            "visual_status": "IDLE"
        }
        for i in range(1, 5):
            firestore_db.collection("slots_ativos").document(str(i)).set(reset_data)
        print("Success: Slots 1-4 reset in Firestore.")

        print("\n--- REALTIME DATABASE ---")
        
        # 3. Limpar RTDB Nodes
        nodes_to_clear = ["radar_pulse", "live_slots", "market_radar", "system_state", "vault_status"]
        for node in nodes_to_clear:
            print(f"Cleaning node '{node}'...")
            rtdb.child(node).delete()
        
        # 4. Repopular slots básicos no RTDB para o frontend não bugar
        print("Initializing basic slots in RTDB...")
        rtdb_slots = {str(i): reset_data for i in range(1, 5)}
        rtdb.child("live_slots").set(rtdb_slots)
        
        print("\nCLEANUP COMPLETED SUCCESSFULLY!")
        print("O sistema agora está em estado virgem. Reinicie o Capitão para começar do zero.")

    except Exception as e:
        print(f"❌ Erro crítico durante a limpeza: {e}")

if __name__ == "__main__":
    wipe_data()
