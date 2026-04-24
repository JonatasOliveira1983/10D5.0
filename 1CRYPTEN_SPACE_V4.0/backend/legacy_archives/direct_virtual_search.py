import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def get_virtual_trades():
    # Use o arquivo local
    cred_path = "serviceAccountKey.json"
    if not os.path.exists(cred_path):
        print(f"Error: {cred_path} not found")
        return

    cred = credentials.Certificate(cred_path)
    # A URL está no .env, mas para o Firestore não é estritamente necessária se o JSON tiver o project_id
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass # Já inicializado

    db = firestore.client()
    
    # Busca os últimos 100 trades
    docs = db.collection("trade_history").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(100).stream()
    
    virtual_trades = []
    for doc in docs:
        data = doc.to_dict()
        if 'VIRTUAL' in str(data.get('symbol', '')):
            virtual_trades.append(data)
            
    print(json.dumps(virtual_trades, indent=2))

if __name__ == "__main__":
    get_virtual_trades()
