
import asyncio
import os
import sys

sys.path.append(os.getcwd())
from services.firebase_service import firebase_service

async def check():
    await firebase_service.initialize()
    if not firebase_service.rtdb:
        print("RTDB not connected")
        return
        
    vault = firebase_service.rtdb.child("vault_status").get()
    print(f"RTDB vault_status: {vault}")
    
    banca = firebase_service.rtdb.child("banca_status").get()
    print(f"RTDB banca_status: {banca}")

if __name__ == "__main__":
    asyncio.run(check())
