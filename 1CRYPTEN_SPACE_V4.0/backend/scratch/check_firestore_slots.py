import asyncio
from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service

async def check():
    print("Checking Firestore Active Slots...")
    slots = await firebase_service.get_active_slots(force_refresh=True)
    for s in slots:
        print(f"Slot {s.get('id')}: {s.get('symbol')} | Status: {s.get('status')} | Genesis: {s.get('genesis_id')}")
    
    print("\nChecking Paper Positions...")
    for p in bybit_rest_service.paper_positions:
        print(f"Paper: {p.get('symbol')} | Side: {p.get('side')} | PnL: {p.get('unrealised_pnl')}")

if __name__ == "__main__":
    asyncio.run(check())
