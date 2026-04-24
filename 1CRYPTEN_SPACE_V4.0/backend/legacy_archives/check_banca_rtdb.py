import asyncio
import json
from services.sovereign_service import sovereign_service

async def main():
    await sovereign_service.initialize()
    if not sovereign_service.is_active:
        print("Offline")
        return
        
    try:
        banca = await asyncio.to_thread(sovereign_service.rtdb.child("banca_status").get)
        print("Banca RTDB:")
        print(json.dumps(banca, indent=2) if banca else "None")
        
        banca2 = await sovereign_service.get_banca_status()
        print("\nBanca Firestore:")
        print(json.dumps(banca2, indent=2) if banca2 else "None")
        
        vault = await asyncio.to_thread(sovereign_service.rtdb.child("vault_status").get)
        print("\nVault RTDB:")
        print(json.dumps(vault, indent=2) if vault else "None")
        
    except Exception as e:
        print(f"Erro: {e}")

asyncio.run(main())
