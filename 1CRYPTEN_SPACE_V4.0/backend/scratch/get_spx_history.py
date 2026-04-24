import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def main():
    cred_path = r"c:\Users\spcom\Desktop\10D-3.0 - Qwen\1CRYPTEN_SPACE_V4.0\backend\serviceAccountKey.json"
    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass

    db = firestore.client()
    
    print("--- SPXUSDT LATEST TRADE HISTORY ---")
    docs = db.collection("trade_history").limit(50).stream()
    for doc in docs:
        d = doc.to_dict()
        if d.get("symbol") == "SPXUSDT":
            print(json.dumps(d, indent=2, default=str))

if __name__ == "__main__":
    main()
