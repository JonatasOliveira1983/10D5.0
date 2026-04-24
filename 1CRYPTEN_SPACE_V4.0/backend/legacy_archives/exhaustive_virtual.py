import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def exhaustive_virtual_search():
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
    
    # Busca 2000 records no Python
    print("Searching 2000 records across all indices for VIRTUAL...")
    docs = db.collection("trade_history").limit(2000).stream()
    
    found = []
    for doc in docs:
        data = doc.to_dict()
        if 'VIRTUAL' in str(data.get('symbol', '')).upper():
            found.append(data)
            
    if found:
        print(f"Found {len(found)} records!")
        print(json.dumps(found, indent=2))
    else:
        print("Still nothing. Checking journey_signals similarly...")
        docs_j = db.collection("journey_signals").limit(1000).stream()
        for doc in docs_j:
            data = doc.to_dict()
            if 'VIRTUAL' in str(data.get('symbol', '')).upper():
                found.append(data)
        if found:
            print(f"Found {len(found)} records in journey_signals!")
            print(json.dumps(found, indent=2))
        else:
            print("Totally missing from typical collections.")

if __name__ == "__main__":
    exhaustive_virtual_search()
