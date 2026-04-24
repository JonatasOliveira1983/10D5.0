import asyncio
import os
import sys

# Adicionar o diretório base ao sys.path para importar serviços
sys.path.append(os.getcwd())

async def check():
    from services.sovereign_service import sovereign_service
    if not sovereign_service.is_active:
        await sovereign_service.initialize()
        
    print(f"Firebase Active: {sovereign_service.is_active}")
    
    print("Checking RTDB vault_status...")
    try:
        def _get_val(path):
            return sovereign_service.rtdb.child(path).get()
        
        vault_status = await asyncio.to_thread(_get_val, "vault_status")
        print(f"Vault Status: {vault_status}")

        print("Checking RTDB slots...")
        slots = await asyncio.to_thread(_get_val, "slots")
        print(f"Slots: {slots}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
