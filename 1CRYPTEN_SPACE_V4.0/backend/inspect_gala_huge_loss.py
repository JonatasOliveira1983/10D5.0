import asyncio
import os
import firebase_admin
from firebase_admin import credentials, firestore

async def main():
    cred_path = "c:\\Users\\spcom\\Desktop\\10D-3.0\\1CRYPTEN_SPACE_V4.0\\backend\\serviceAccountKey.json"
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    print("=== SEARCHING FOR THE HUGE GALA LOSS ===")
    docs = db.collection("trade_history").where("symbol", "==", "GALAUSDT").stream()
    
    for doc in docs:
        d = doc.to_dict()
        pnl = d.get('pnl', 0)
        if abs(pnl) > 100:
            print(f"FOUND DOCUMENT: {doc.id}")
            for k, v in d.items():
                print(f"  {k}: {v}")
            print("-" * 20)

if __name__ == "__main__":
    asyncio.run(main())
