import asyncio
from services.firebase_service import firebase_service
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run():
    await firebase_service.initialize()
    if not firebase_service.db:
        print("Erro db")
        return
    
    trades_ref = firebase_service.db.collection('trade_history')
    
    print("\n--- Recent Trades (Last 10) ---")
    query = trades_ref.order_by('timestamp', direction='DESCENDING').limit(10)
    docs = await asyncio.to_thread(lambda: list(query.stream()))
    
    for doc in docs:
        d = doc.to_dict()
        print(f"ID: {doc.id} | TS: {d.get('timestamp')} | Symbol: {d.get('symbol')} | PnL: {d.get('pnl')} | Reason: {d.get('close_reason')}")

if __name__ == "__main__":
    asyncio.run(run())
