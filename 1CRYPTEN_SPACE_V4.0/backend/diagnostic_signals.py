import asyncio
import json
from services.firebase_service import firebase_service
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run():
    await firebase_service.initialize()
    if not firebase_service.db:
        print("Erro db")
        return
    
    signals_ref = firebase_service.db.collection('journey_signals')
    
    print("\n--- Fetching last 50 signals ---")
    query = signals_ref.order_by('timestamp', direction='DESCENDING').limit(50)
    docs = await asyncio.to_thread(lambda: list(query.stream()))
    
    print(f"Found {len(docs)} signals total.")
    
    for doc in docs:
        d = doc.to_dict()
        sym = d.get('symbol', '').upper()
        outcome = d.get('outcome')
        print(f"ID: {doc.id} | Sym: {sym} | Outcome: {outcome} | Score: {d.get('score')}")

if __name__ == "__main__":
    asyncio.run(run())
