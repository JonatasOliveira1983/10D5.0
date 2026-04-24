import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sovereign_service import sovereign_service

async def unlock_bot():
    print("Conectando ao Firebase para desbloquear o sistema (Resetando META 100)...")
    await sovereign_service.initialize()
    await sovereign_service.initialize_db()

    cycle_ref = sovereign_service.db.collection("vault_management").document("current_cycle")
    doc = cycle_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        print(f"Estado atual -> total_trades_cycle: {data.get('total_trades_cycle')}")
        
        cycle_ref.update({
            "total_trades_cycle": 0
        })
        print("✅ total_trades_cycle resetado para 0 com sucesso. O bot voltará a operar!")
    else:
        print("Documento current_cycle não encontrado.")

if __name__ == "__main__":
    asyncio.run(unlock_bot())
