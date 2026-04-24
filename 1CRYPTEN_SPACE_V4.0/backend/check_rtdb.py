import asyncio
import os
import sys

# Adicionar o diretório base ao sys.path para importar serviços
sys.path.append(os.getcwd())

async def check():
    from services.firebase_service import firebase_service
    if not firebase_service.is_active:
        await firebase_service.initialize()
        
    print(f"Firebase Active: {firebase_service.is_active}")
    
    print("Checking RTDB vault_status...")
    try:
        def _get_val(path):
            return firebase_service.rtdb.child(path).get()
        
        vault_status = await asyncio.to_thread(_get_val, "vault_status")
        print(f"Vault Status: {vault_status}")

        print("Checking RTDB slots...")
        slots = await asyncio.to_thread(_get_val, "slots")
        print(f"Slots: {slots}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
