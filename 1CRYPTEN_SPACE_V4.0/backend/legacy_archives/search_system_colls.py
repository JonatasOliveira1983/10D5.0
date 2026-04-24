import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def search_system_and_consciousness():
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
    
    collections = ["admiral_consciousness", "system_logs", "vault_status"]
    
    for coll_name in collections:
        print(f"--- Searching {coll_name} for VIRTUAL ---")
        docs = db.collection(coll_name).limit(100).stream()
        found = False
        for doc in docs:
            data = doc.to_dict()
            if 'VIRTUAL' in str(data).upper():
                print(f"Match in {coll_name}: {doc.id}")
                print(json.dumps(data, indent=2))
                found = True
        if not found:
            print(f"No match in {coll_name}")

if __name__ == "__main__":
    search_system_and_consciousness()
