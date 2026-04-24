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
    
    print("Cleaning all impossible trades in 'trade_history'...")
    # Deleted trades with PnL < -15 (impossible for $10 margin)
    history_docs = db.collection("trade_history").stream()
    for doc in history_docs:
        d = doc.to_dict()
        pnl = d.get('pnl', 0)
        if pnl < -15:
            print(f"Deleting trade {doc.id} | Symbol: {d.get('symbol')} | PnL: {pnl}")
            db.collection("trade_history").document(doc.id).delete()

    print("\n--- FINAL CLEANUP COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(main())
