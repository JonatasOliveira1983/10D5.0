import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def find_virtual_in_history():
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
    
    # Busca por símbolo que contenha VIRTUAL
    # Como o Firestore não suporta 'contains' nativamente em strings indexadas dessa forma sem um índice complexo,
    # vamos buscar os últimos 500 registros e filtrar no Python.
    docs = db.collection("trade_history").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(500).stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        if 'VIRTUAL' in str(data.get('symbol', '')).upper():
            results.append(data)
            
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    find_virtual_in_history()
