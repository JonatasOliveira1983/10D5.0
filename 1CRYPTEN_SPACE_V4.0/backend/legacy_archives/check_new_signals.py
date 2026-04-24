import asyncio
from services.sovereign_service import sovereign_service
import time

async def check_signals():
    await sovereign_service.initialize()
    print("Checking for recent Blitz signals in Firestore...")
    
    # Busca sinais dos últimos 5 minutos
    now_ms = int(time.time() * 1000)
    five_mins_ago = now_ms - (5 * 60 * 1000)
    
    signals_ref = sovereign_service.db.collection("journey_signals")
    query = signals_ref.where("timestamp", ">=", five_mins_ago).order_by("timestamp", direction="DESCENDING").limit(10)
    
    docs = query.stream()
    found = False
    for doc in docs:
        found = True
        s = doc.to_dict()
        print(f"Signal: {s.get('symbol')} | TF: {s.get('timeframe')} | Score: {s.get('score')} | Pattern: {s.get('indicators', {}).get('pattern')}")
        
    if not found:
        print("No recent signals found in Firestore.")

if __name__ == "__main__":
    asyncio.run(check_signals())
