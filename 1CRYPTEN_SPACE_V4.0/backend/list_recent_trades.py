import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def list_recent_trades():
    cred_path = "serviceAccountKey.json"
    if not os.path.exists(cred_path):
        print(f"Error: {cred_path} not found")
        return

    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass

    db = firestore.client()
    
    # Busca os últimos 20 trades sem filtro
    docs = db.collection("trade_history").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(20).stream()
    
    recent_trades = []
    for doc in docs:
        data = doc.to_dict()
        recent_trades.append({
            "symbol": data.get("symbol"),
            "pnl": data.get("pnl"),
            "timestamp": data.get("timestamp"),
            "close_reason": data.get("close_reason")
        })
            
    print(json.dumps(recent_trades, indent=2))

if __name__ == "__main__":
    list_recent_trades()
