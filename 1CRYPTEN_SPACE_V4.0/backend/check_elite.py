import asyncio
from services.bybit_rest import bybit_rest_service

async def check_elite_pairs():
    await bybit_rest_service.initialize()
    pairs = await bybit_rest_service.get_elite_50x_pairs()
    print(f"--- Elite Pairs ({len(pairs)}) ---")
    
    targets = ['FARTCOINUSDT', 'LINKUSDT', 'ENAUSDT', 'OPUSDT', 'BNBUSDT', 'ETHUSDT', 'SOLUSDT', 'FILUSDT']
    for t in targets:
        match = [p for p in pairs if t in p or p in t]
        if match:
            print(f"✅ {t} is in the list as {match}")
        else:
            print(f"❌ {t} is NOT in the elite list.")

if __name__ == "__main__":
    asyncio.run(check_elite_pairs())
