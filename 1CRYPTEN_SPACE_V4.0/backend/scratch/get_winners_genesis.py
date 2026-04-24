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
    
    docs = db.collection("trade_history").limit(100).stream()
    res = {"EIGENUSDT": None, "AAVEUSDT": None, "SOLUSDT": None}
    
    for doc in docs:
        d = doc.to_dict()
        sym = d.get("symbol")
        if sym in res and res[sym] is None:
            res[sym] = d
    
    with open("winners_out_utf8.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, default=str)

if __name__ == "__main__":
    main()
