import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from services.firebase_service import firebase_service

async def view_moonbags():
    await firebase_service.initialize()
    moonbags = await firebase_service.get_moonbags()
    
    print("--- FIRESTORE ---")
    for m in moonbags:
        print(f"[{m.get('symbol')}] ID: {m.get('id')} - Entry: {m.get('entry_price')}")
        if m.get('symbol') == 'HYPEUSDT':
            print("Full HYPE:", m)
            
    print("--- RTDB ---")
    if firebase_service.rtdb:
        rtdb_snaps = firebase_service.rtdb.child("moonbag_vault").get()
        if rtdb_snaps and rtdb_snaps.val():
            for key, val in rtdb_snaps.val().items():
                print(f"RTDB Key: {key} -> {val.get('symbol')} | {val.get('pnl_percent')}%")
        else:
            print("Empty RTDB!")
    else:
        print("No RTDB Conn")
        
asyncio.run(view_moonbags())
os._exit(0)
