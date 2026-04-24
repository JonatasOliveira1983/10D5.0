import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service

async def reset_slots():
    print("Iniciando limpeza dos Slots 1 a 4...")
    await firebase_service.initialize()
    
    empty_slot = {
        "symbol": None, "entry_price": 0, "current_stop": 0, "entry_margin": 0,
        "status_risco": "IDLE", "side": None, "pnl_percent": 0, "target_price": 0,
        "qty": 0, "slot_type": None, "pattern": None, "pensamento": ""
    }
    
    for i in range(1, 5):
        try:
            await firebase_service.update_slot(i, empty_slot)
            print(f" Slot {i} resetado para IDLE.")
        except Exception as e:
            print(f" Erro ao resetar slot {i}: {e}")
            
    print("Concluído! Os slots fantasmas foram limpos.")

if __name__ == "__main__":
    asyncio.run(reset_slots())
