import asyncio
import os
import sys

# Adiciona o diretório atual ao sys.path para importar services
sys.path.append(os.getcwd())

from services.sovereign_service import sovereign_service

async def main():
    slots = await sovereign_service.get_active_slots()
    for s in slots:
        symbol = s.get('symbol', 'LIVRE')
        current_stop = s.get('current_stop', 0)
        initial_stop = s.get('initial_stop', 'N/A')
        print(f"Slot {s['id']} | {symbol} | Current: {current_stop} | Initial: {initial_stop}")

if __name__ == "__main__":
    asyncio.run(main())
