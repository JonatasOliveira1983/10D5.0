import asyncio
import json
import os
from services.firebase_service import firebase_service
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def run():
    await firebase_service.initialize()
    if not firebase_service.db:
        print("Erro: DB não inicializado.")
        return
    
    signals_ref = firebase_service.db.collection('journey_signals')
    
    print("\n--- Fetching last 20 signals ---")
    query = signals_ref.order_by('timestamp', direction='DESCENDING').limit(20)
    docs = await asyncio.to_thread(lambda: list(query.stream()))
    
    print(f"Found {len(docs)} signals.")
    
    signals_data = []
    for doc in docs:
        d = doc.to_dict()
        signals_data.append(d)
        print(f"Time: {d.get('timestamp')} | Symbol: {d.get('symbol')} | Side: {d.get('side')} | Score: {d.get('score')} | Layer: {d.get('layer')}")

    with open("recent_signals_debug.json", "w", encoding="utf-8") as f:
        json.dump(signals_data, f, indent=2, ensure_ascii=False)
    
    print("\nDetalles salvos em recent_signals_debug.json")

if __name__ == "__main__":
    asyncio.run(run())
