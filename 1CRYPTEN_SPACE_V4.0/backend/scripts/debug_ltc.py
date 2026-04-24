
import asyncio
from services.firebase_service import firebase_service

async def show_ltc():
    await firebase_service.initialize()
    docs = firebase_service.db.collection("trade_history").where("symbol", "==", "LTCUSDT.P").stream()
    print("--- LTCUSDT.P TRADES ---")
    for d in docs:
        t = d.to_dict()
        print(f"ID: {d.id} | PnL: {t.get('pnl')} | Time: {t.get('closed_at') or t.get('close_time')} | Side: {t.get('side')}")
    
    docs = firebase_service.db.collection("trade_history").where("symbol", "==", "LTCUSDT").stream()
    print("--- LTCUSDT TRADES ---")
    for d in docs:
        t = d.to_dict()
        print(f"ID: {d.id} | PnL: {t.get('pnl')} | Time: {t.get('closed_at') or t.get('close_time')} | Side: {t.get('side')}")

if __name__ == "__main__":
    asyncio.run(show_ltc())
