import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service

async def final_clean():
    print("Iniciando limpeza final de slots para teste V80.6...")
    try:
        # Reset all 4 slots in Firestore
        for i in range(1, 5):
            await firebase_service.hard_reset_slot(i, reason="Reset Final para V80.6")
            print(f"Slot {i} resetado.")
        
        # Clear System Message
        await firebase_service.update_system_state("SCANNING", 0, "Pronto para teste V80.6", protocol="Sniper V15.1")
        print("Estado do sistema resetado para SCANNING.")
        
    except Exception as e:
        print(f"Erro na limpeza: {e}")

if __name__ == "__main__":
    asyncio.run(final_clean())
