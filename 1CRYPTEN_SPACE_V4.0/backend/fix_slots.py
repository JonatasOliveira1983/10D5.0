import asyncio
import sys
import os

sys.path.append(os.path.abspath('c:/Users/spcom/Desktop/10D-3.0/1CRYPTEN_SPACE_V4.0/backend'))

async def main():
    print("Iniciando realocação de slots...")
    try:
        from services.firebase_service import firebase_service
        slots = await firebase_service.get_active_slots()
        
        pepe_slot_data = None
        
        # Encontra o PEPE e guarda os dados originais
        for slot in slots:
            if slot.get('symbol') == '1000PEPEUSDT':
                pepe_slot_data = slot.copy()
                break
                
        if pepe_slot_data:
            print("PEPE encontrado. Movendo para Slot 1...")
            # Atualiza Slot 1 com PEPE
            await firebase_service.update_slot(1, {
                "symbol": "1000PEPEUSDT", 
                "entry_price": pepe_slot_data.get('entry_price', 0), 
                "current_stop": pepe_slot_data.get('current_stop', 0), 
                "entry_margin": pepe_slot_data.get('entry_margin', 0),
                "status_risco": pepe_slot_data.get('status_risco', 'RECOVERED'), 
                "side": pepe_slot_data.get('side', 'Buy'), 
                "pnl_percent": pepe_slot_data.get('pnl_percent', 0), 
                "sl_phase": pepe_slot_data.get('sl_phase', 'IDLE')
            })
            print("Slot 1 atualizado com PEPE!")
            
            # Limpa os slots 2, 3 e 4
            for i in range(2, 5):
                await firebase_service.update_slot(i, {
                    "symbol": None, "entry_price": 0, "current_stop": 0, "entry_margin": 0,
                    "status_risco": "LIVRE", "side": None, "pnl_percent": 0, "sl_phase": "IDLE"
                })
            print("Slots 2, 3 e 4 limpos!")
        else:
            print("PEPE não encontrado nos slots!")
            
    except Exception as e:
        print("Erro:", e)

if __name__ == "__main__":
    asyncio.run(main())
