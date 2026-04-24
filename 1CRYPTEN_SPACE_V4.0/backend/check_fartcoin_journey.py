import asyncio
import os
import sys

sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))
from services.sovereign_service import sovereign_service

async def check():
    await sovereign_service.initialize()
    if not sovereign_service.db:
        print("Firebase Offline")
        return
        
    print("--- JOURNEY SIGNALS (FARTCOIN) ---")
    docs = sovereign_service.db.collection("journey_signals").where("symbol", "==", "FARTCOINUSDT").get()
    if not docs:
        docs = sovereign_service.db.collection("journey_signals").where("symbol", "==", "FARTCOIN").get()
        
    if not docs:
        print("Nenhum registro de FARTCOIN em journey_signals.")
    for d in docs:
        data = d.to_dict()
        print(f"ID: {d.id} | TS: {data.get('timestamp')} | Final Result: {data.get('final_result')} | Intel: {data.get('intel', {}).get('reason')}")

if __name__ == "__main__":
    asyncio.run(check())
