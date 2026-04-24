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
    
    print("=== ALL TRADES IN HISTORY ===")
    docs = db.collection("trade_history").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    
    total_calculated_pnl = 0
    for doc in docs:
        d = doc.to_dict()
        pnl = d.get('pnl', 0)
        symbol = d.get('symbol', 'N/A')
        ts = d.get('timestamp', 'N/A')
        print(f"[{ts}] {symbol} | PnL: {pnl}")
        total_calculated_pnl += pnl
        
    print(f"\nTotal Calculated PnL from history: {total_calculated_pnl}")

    print("\n=== VAULT MANAGEMENT DETAILS ===")
    vault_docs = db.collection("vault_management").stream()
    for doc in vault_docs:
        print(f"Doc: {doc.id}")
        d = doc.to_dict()
        for k, v in d.items():
            print(f"  {k}: {v}")

if __name__ == "__main__":
    asyncio.run(main())
