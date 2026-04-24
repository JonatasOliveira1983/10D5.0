import os
import sys
import json
import firebase_admin
from firebase_admin import credentials, firestore

def main():
    cred_path = r"c:\Users\spcom\Desktop\10D REAL 4.0\1CRYPTEN_SPACE_V4.0\backend\serviceAccountKey.json"
    if not os.path.exists(cred_path):
        print(f"Error: {cred_path} not found")
        return

    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass

    db = firestore.client()
    
    print("--- LATEST TRADE HISTORY (Top 5) ---")
    try:
        history_docs = db.collection("trade_history").order_by("closed_at", direction=firestore.Query.DESCENDING).limit(5).stream()
        for doc in history_docs:
            print(json.dumps(doc.to_dict(), indent=2, default=str))
    except Exception as e:
        print(f"Error reading trade_history: {e}")

    print("\n--- LATEST ORDERS GENESIS (Top 5) ---")
    try:
        # Tenta ordenar por opened_at, se der erro de index tenta sem orderBy
        genesis_docs = db.collection("orders_genesis").order_by("opened_at", direction=firestore.Query.DESCENDING).limit(5).stream()
        found = False
        for doc in genesis_docs:
            found = True
            print(json.dumps(doc.to_dict(), indent=2, default=str))
        if not found:
            print("No genesis docs found.")
    except Exception as e:
        print(f"Error reading orders_genesis with orderBy. Trying without... | Error: {e}")
        try:
            genesis_docs = db.collection("orders_genesis").limit(5).stream()
            for doc in genesis_docs:
                print(json.dumps(doc.to_dict(), indent=2, default=str))
        except Exception as e2:
            print(f"Error fallback: {e2}")

if __name__ == "__main__":
    main()
