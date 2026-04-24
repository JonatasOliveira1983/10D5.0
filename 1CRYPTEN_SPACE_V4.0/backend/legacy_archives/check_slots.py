
import asyncio
from services.sovereign_service import sovereign_service
import json

async def check_slots():
    print("Iniciando consulta ao Firebase (Active Slots)...")
    if not sovereign_service.is_active:
        print("Firebase não está ativo!")
        return

    slots = await sovereign_service.get_active_slots()
    print("Slots Ativos no Firebase:")
    print(json.dumps(slots, indent=2))

if __name__ == "__main__":
    asyncio.run(check_slots())
