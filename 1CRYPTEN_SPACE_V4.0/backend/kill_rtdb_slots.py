import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service

async def kill_rtdb_slots():
    await firebase_service.initialize()
    print("Conectado. Deletando banca_status/slots e live_slots no RTDB...")
    try:
        await asyncio.to_thread(firebase_service.rtdb.child("banca_status").child("slots").set, None)
        print("banca_status/slots deletado do RTDB com sucesso.")
    except Exception as e:
        print(f"Erro ao deletar banca_status/slots: {e}")
        
    try:
        await asyncio.to_thread(firebase_service.rtdb.child("live_slots").set, None)
        print("live_slots deletado do RTDB com sucesso.")
    except Exception as e:
        print(f"Erro ao deletar live_slots: {e}")

    try:
        # Also let's push the clean array to RTDB slot sync logic manually if needed
        empty_slot = {
            "symbol": None, "entry_price": 0, "current_stop": 0, "entry_margin": 0,
            "status_risco": "IDLE", "side": None, "pnl_percent": 0, "target_price": 0,
            "qty": 0, "slot_type": None, "pattern": None, "pensamento": ""
        }
        slots_data = {str(i): {**empty_slot, "id": i} for i in range(1, 5)}
        await asyncio.to_thread(firebase_service.rtdb.child("banca_status").child("slots").set, slots_data)
        await asyncio.to_thread(firebase_service.rtdb.child("live_slots").set, slots_data)
        print("Slots RTDB recriados zerados.")
    except Exception as e:
        print(f"Erro reseting: {e}")

if __name__ == "__main__":
    asyncio.run(kill_rtdb_slots())
