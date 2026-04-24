import asyncio
import os
import firebase_admin
from firebase_admin import credentials, firestore

async def main():
    cred_path = "c:\\Users\\spcom\\Desktop\\10D-3.0\\1CRYPTEN_SPACE_V4.0\\backend\\serviceAccountKey.json"
    if not os.path.getsize(cred_path) > 0:
        print("Empty key")
        return
        
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    print("=== SEARCHING FOR GALA AND TRX TRADES ===")
    # Search in trade_history
    docs = db.collection("trade_history").where("symbol", "in", ["GALAUSDT", "TRXUSDT", "GALAUSDT.P", "TRXUSDT.P"]).stream()
    
    found = False
    for doc in docs:
        found = True
        d = doc.to_dict()
        print(f"ID: {doc.id}")
        for k, v in d.items():
            print(f"  {k}: {v}")
        print("-" * 20)
        
    if not found:
        print("No specific trades found in trade_history for GALA or TRX.")

    print("\n=== SEARCHING IN JOURNEY SIGNALS ===")
    docs = db.collection("journey_signals").where("symbol", "in", ["GALAUSDT", "TRXUSDT", "GALAUSDT.P", "TRXUSDT.P"]).limit(10).stream()
    for doc in docs:
        d = doc.to_dict()
        print(f"SIGNAL ID: {doc.id} | Symbol: {d.get('symbol')} | Outcome: {d.get('outcome')}")

if __name__ == "__main__":
    asyncio.run(main())
