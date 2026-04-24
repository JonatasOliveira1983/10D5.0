
import asyncio
from services.sovereign_service import sovereign_service

async def check_history():
    await sovereign_service.initialize()
    trades = await sovereign_service.get_trade_history(limit=5)
    print("--- RECENT TRADES ---")
    for t in trades:
        print(f"Symbol: {t.get('symbol')} | PnL: {t.get('pnl')} | Time: {t.get('closed_at') or t.get('close_time')}")
        # print(f"Raw: {t}")
    print("---------------------")

if __name__ == "__main__":
    asyncio.run(check_history())
