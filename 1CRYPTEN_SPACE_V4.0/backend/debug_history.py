
import asyncio
from services.firebase_service import firebase_service

async def check_history():
    await firebase_service.initialize()
    trades = await firebase_service.get_trade_history(limit=5)
    print("--- RECENT TRADES ---")
    for t in trades:
        print(f"Symbol: {t.get('symbol')} | PnL: {t.get('pnl')} | Time: {t.get('closed_at') or t.get('close_time')}")
        # print(f"Raw: {t}")
    print("---------------------")

if __name__ == "__main__":
    asyncio.run(check_history())
