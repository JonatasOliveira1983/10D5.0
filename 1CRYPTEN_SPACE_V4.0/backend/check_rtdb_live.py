
import asyncio
import os
import sys

sys.path.append(os.getcwd())
from services.sovereign_service import sovereign_service

async def check():
    await sovereign_service.initialize()
    if not sovereign_service.rtdb:
        print("RTDB not connected")
        return
        
    vault = sovereign_service.rtdb.child("vault_status").get()
    print(f"RTDB vault_status: {vault}")
    
    banca = sovereign_service.rtdb.child("banca_status").get()
    print(f"RTDB banca_status: {banca}")

if __name__ == "__main__":
    asyncio.run(check())
