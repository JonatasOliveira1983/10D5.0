import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def main():
    cred_path = r"c:\Users\spcom\Desktop\10D-3.0 - Qwen\1CRYPTEN_SPACE_V4.0\backend\serviceAccountKey.json"
    if not os.path.exists(cred_path):
        return

    try:
        firebase_admin.initialize_app(credentials.Certificate(cred_path))
    except ValueError:
        pass

    db = firestore.client()
    result = {"trade_history": [], "orders_genesis": []}
    
    try:
        history_docs = db.collection("trade_history").order_by("closed_at", direction=firestore.Query.DESCENDING).limit(5).stream()
        for doc in history_docs:
            result["trade_history"].append(doc.to_dict())
    except Exception as e:
        pass

    try:
        genesis_docs = db.collection("orders_genesis").order_by("opened_at", direction=firestore.Query.DESCENDING).limit(5).stream()
        for doc in genesis_docs:
            result["orders_genesis"].append(doc.to_dict())
    except Exception as e:
        genesis_docs = db.collection("orders_genesis").limit(5).stream()
        for doc in genesis_docs:
            result["orders_genesis"].append(doc.to_dict())

    with open(r"c:\Users\spcom\Desktop\10D-3.0 - Qwen\1CRYPTEN_SPACE_V4.0\backend\scratch\recent_db_dump.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)

if __name__ == "__main__":
    main()
