
import asyncio
from services.firebase_service import firebase_service
import json

async def check_slots():
    print("Iniciando consulta ao Firebase (Active Slots)...")
    if not firebase_service.is_active:
        print("Firebase não está ativo!")
        return

    slots = await firebase_service.get_active_slots()
    print("Slots Ativos no Firebase:")
    print(json.dumps(slots, indent=2))

if __name__ == "__main__":
    asyncio.run(check_slots())
