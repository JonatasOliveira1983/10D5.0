import asyncio
import sys
import os

sys.path.append(os.path.abspath('c:/Users/spcom/Desktop/10D-3.0/1CRYPTEN_SPACE_V4.0/backend'))

async def main():
    print("Iniciando purga do BTCUSDT...")
    try:
        from services.sovereign_service import sovereign_service
        slots = await sovereign_service.get_active_slots()
        
        for slot in slots:
            if slot.get('symbol') == 'BTCUSDT':
                print(f"Limpando Firestore Slot {slot['id']}...")
                await sovereign_service.update_slot(slot['id'], {
                    "symbol": None, "entry_price": 0, "current_stop": 0, "entry_margin": 0,
                    "status_risco": "LIVRE", "side": None, "pnl_percent": 0, "sl_phase": "IDLE"
                })
        print("✅ BTC removido do banco de dados!")
    except Exception as e:
        print("Erro:", e)

if __name__ == "__main__":
    asyncio.run(main())
