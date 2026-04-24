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
    slots = await firebase_service.get_active_slots()
    
    with open("slots_dump.json", "w", encoding="utf-8") as f:
        json.dump(slots, f, indent=2, ensure_ascii=False)
    print("Slots salvos em slots_dump.json")

if __name__ == "__main__":
    asyncio.run(run())
