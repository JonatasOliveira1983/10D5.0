import asyncio
from services.firebase_service import firebase_service

async def clear_all():
    print("Iniciando limpeza profunda de slots (V110.173)...")
    # Limpa os 4 slots no Firestore e RTDB
    for i in range(1, 5):
        empty_slot = {
            "id": i,
            "symbol": "",
            "side": "",
            "entry_price": 0,
            "current_price": 0,
            "leverage": 0,
            "pnl_pct": 0,
            "pnl_cash": 0,
            "status": "LIVRE",
            "opened_at": 0,
            "genesis_id": ""
        }
        await firebase_service.update_slot(i, empty_slot)
        if firebase_service.rtdb:
            firebase_service.rtdb.child("live_slots").child(str(i)).set(empty_slot)
        print(f"Slot {i} resetado.")

if __name__ == "__main__":
    asyncio.run(clear_all())
