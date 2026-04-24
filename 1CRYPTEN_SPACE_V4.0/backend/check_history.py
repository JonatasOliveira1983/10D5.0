import asyncio
import os
from google.cloud import firestore
from config import settings

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.FIREBASE_CREDENTIALS_PATH

async def check_last_trades():
    db = firestore.Client()
    docs = db.collection("trade_history").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
    
    print("📜 --- Last 10 Trades in Firestore ---")
    for doc in docs:
        d = doc.to_dict()
        print(f"🔹 {d.get('symbol')} | {d.get('side')} | PnL: ${d.get('pnl_usd')} | ROI: {d.get('pnl_percent')}% | Reason: {d.get('close_reason')}")
        print(f"   Entry: {d.get('entry_price')} | Exit: {d.get('exit_price')} | Qty: {d.get('qty')} | Lev: {d.get('leverage')}")
        print(f"   Time: {d.get('timestamp')}")
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(check_last_trades())
