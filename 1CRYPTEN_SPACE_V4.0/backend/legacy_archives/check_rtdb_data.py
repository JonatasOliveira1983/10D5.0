import firebase_admin
from firebase_admin import credentials, db
import os
import json

def check_rtdb_radar():
    cert_path = "serviceAccountKey.json"
    if not os.path.exists(cert_path):
        cert_path = "1CRYPTEN_SPACE_V4.0/backend/serviceAccountKey.json"
    if not os.path.exists(cert_path):
        cert_path = "backend/serviceAccountKey.json"
        
    if not firebase_admin._apps:
        cred = credentials.Certificate(cert_path)
        database_url = "https://projeto-teste-firestore-3b00e-default-rtdb.europe-west1.firebasedatabase.app"
        firebase_admin.initialize_app(cred, {'databaseURL': database_url})

    ref = db.reference("radar_pulse")
    data = ref.get()
    
    print("=== RTDB: radar_pulse Keys ===")
    if data:
        print(list(data.keys()))
        if "market_context" in data:
            print("market_context ENCONTRADO!")
            print(json.dumps(data["market_context"], indent=2))
        else:
            print("market_context NÃO encontrado nas chaves.")
    else:
        print("Node 'radar_pulse' está vazio ou não existe.")

if __name__ == "__main__":
    check_rtdb_radar()
