import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def search_journey_signals():
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
    
    print("--- Searching journey_signals for VIRTUAL ---")
    docs = db.collection("journey_signals").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(100).stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        if 'VIRTUAL' in str(data.get('symbol', '')).upper():
            results.append(data)
            
    if results:
        print(f"Found {len(results)} matches in journey_signals")
        print(json.dumps(results, indent=2))
    else:
        print("No matches in journey_signals")

if __name__ == "__main__":
    search_journey_signals()
