
import asyncio
import json
from services.firebase_service import firebase_service
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def find_trump_signals():
    await firebase_service.initialize()
    if not firebase_service.db:
        print("Erro db")
        return
    
    print("\n--- Searching for last 50 signals ---")
    signals_ref = firebase_service.db.collection('journey_signals')
    query = signals_ref.order_by('timestamp', direction='DESCENDING').limit(50)
    docs = await asyncio.to_thread(lambda: list(query.stream()))
    
    for doc in docs:
        d = doc.to_dict()
        if 'TRUMP' in d.get('symbol', '').upper():
            try:
                print(f"\n[SIGNAL FOUND] ID: {doc.id}")
                print(f"Data: {json.dumps(d, indent=2, ensure_ascii=False)}")
            except UnicodeEncodeError:
                print(f"\n[SIGNAL FOUND] ID: {doc.id}")
                print(str(d).encode('ascii', 'ignore').decode('ascii'))
            try:
                print(f"\n[TRADE FOUND] ID: {doc.id}")
                print(f"Symbol: {d.get('symbol')} | Side: {d.get('side')} | PnL: {d.get('pnl')}")
                print(f"Pensamento: {d.get('pensamento')}")
                print(f"Reasoning: {d.get('reasoning_report', 'N/A')}")
            except UnicodeEncodeError:
                print(f"\n[TRADE FOUND] ID: {doc.id}")
                print(f"Symbol: {d.get('symbol')} | Side: {d.get('side')} | PnL: {d.get('pnl')}")
                print(f"Pensamento: {str(d.get('pensamento')).encode('ascii', 'ignore').decode('ascii')}")
                print(f"Reasoning: {str(d.get('reasoning_report', 'N/A')).encode('ascii', 'ignore').decode('ascii')}")

if __name__ == "__main__":
    asyncio.run(find_trump_signals())
