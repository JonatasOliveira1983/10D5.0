
import asyncio
from services.sovereign_service import sovereign_service

async def show_ltc():
    await sovereign_service.initialize()
    docs = sovereign_service.db.collection("trade_history").where("symbol", "==", "LTCUSDT.P").stream()
    print("--- LTCUSDT.P TRADES ---")
    for d in docs:
        t = d.to_dict()
        print(f"ID: {d.id} | PnL: {t.get('pnl')} | Time: {t.get('closed_at') or t.get('close_time')} | Side: {t.get('side')}")
    
    docs = sovereign_service.db.collection("trade_history").where("symbol", "==", "LTCUSDT").stream()
    print("--- LTCUSDT TRADES ---")
    for d in docs:
        t = d.to_dict()
        print(f"ID: {d.id} | PnL: {t.get('pnl')} | Time: {t.get('closed_at') or t.get('close_time')} | Side: {t.get('side')}")

if __name__ == "__main__":
    asyncio.run(show_ltc())
