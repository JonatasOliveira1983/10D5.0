import asyncio
import os
import sys

# Setup paths
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

from services.sovereign_service import sovereign_service

async def purge_all_slots():
    print("Iniciando Purga Nuclear de Slots no Firestore...")
    for i in range(1, 5):
        try:
            await sovereign_service.hard_reset_slot(i, reason="Nuclear Clean for V96.9 HFT")
            print(f"Slot {i} resetado com sucesso.")
        except Exception as e:
            print(f"Erro ao resetar Slot {i}: {e}")
    print("Purga completa.")

if __name__ == "__main__":
    asyncio.run(purge_all_slots())
import asyncio
import os
import sys

# Setup paths
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

from services.sovereign_service import sovereign_service

async def purge_all_slots():
    print("Iniciando Purga Nuclear de Slots no Firestore...")
    for i in range(1, 5):
        try:
            await sovereign_service.hard_reset_slot(i, reason="Nuclear Clean for V96.9 HFT")
            print(f"Slot {i} resetado com sucesso.")
        except Exception as e:
            print(f"Erro ao resetar Slot {i}: {e}")
    print("Purga completa.")

if __name__ == "__main__":
    asyncio.run(purge_all_slots())
