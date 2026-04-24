import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def search_pnl_and_analytics():
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
    
    print("--- Searching trade_history for PnL around -25% or symbol VIRTUAL ---")
    docs = db.collection("trade_history").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1000).stream()
    
    results_hist = []
    for doc in docs:
        data = doc.to_dict()
        pnl = data.get("pnl", 0)
        symbol = str(data.get("symbol", "")).upper()
        # Procura por PnL entre -30% e -20% (assumindo que pnl é decimal -0.3 a -0.2)
        # Ou se o usuário quis dizer -25 dólares, procuramos por -25.0
        is_pnl_match = False
        try:
            pnl_val = float(pnl)
            if -0.30 <= pnl_val <= -0.15 or -35 <= pnl_val <= -15:
                is_pnl_match = True
        except:
            pass
            
        if 'VIRTUAL' in symbol or is_pnl_match:
            results_hist.append(data)
            
    print(f"Found {len(results_hist)} potential matches in trade_history")
    if results_hist:
        print(json.dumps(results_hist[:10], indent=2)) # Print first 10

    print("\n--- Searching trade_analytics for VIRTUAL ---")
    docs_analytics = db.collection("trade_analytics").limit(100).stream()
    results_analytics = []
    for doc in docs_analytics:
        data = doc.to_dict()
        if 'VIRTUAL' in str(data.get('symbol', '')).upper():
            results_analytics.append(data)
    
    if results_analytics:
        print(f"Found {len(results_analytics)} matches in trade_analytics")
        print(json.dumps(results_analytics, indent=2))

if __name__ == "__main__":
    search_pnl_and_analytics()
