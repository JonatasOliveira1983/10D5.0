import asyncio
from services.sovereign_service import sovereign_service
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run():
    await sovereign_service.initialize()
    if not sovereign_service.db:
        print("Erro db")
        return
    
    signals_ref = sovereign_service.db.collection('journey_signals')
    
    print("\n--- Recent LTCUSDT Signals ---")
    query_ltc = signals_ref.where('symbol', '==', 'LTCUSDT').order_by('timestamp', direction='DESCENDING').limit(5)
    docs_ltc = await asyncio.to_thread(lambda: list(query_ltc.stream()))
    for doc in docs_ltc:
        d = doc.to_dict()
        print(f"ID: {doc.id} | TS: {d.get('timestamp')} | Side: {d.get('side')} | Score: {d.get('score')} | Adaptive SL: {d.get('adaptive_sl')}")

    print("\n--- Recent BNBUSDT Signals ---")
    query_bnb = signals_ref.where('symbol', '==', 'BNBUSDT').order_by('timestamp', direction='DESCENDING').limit(5)
    docs_bnb = await asyncio.to_thread(lambda: list(query_bnb.stream()))
    for doc in docs_bnb:
        d = doc.to_dict()
        print(f"ID: {doc.id} | TS: {d.get('timestamp')} | Side: {d.get('side')} | Score: {d.get('score')} | Adaptive SL: {d.get('adaptive_sl')}")

if __name__ == "__main__":
    asyncio.run(run())
