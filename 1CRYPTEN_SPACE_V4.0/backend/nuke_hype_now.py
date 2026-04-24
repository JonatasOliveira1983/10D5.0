import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import settings
from services.sovereign_service import sovereign_service

async def nuke():
    print("Connecting to Firebase...")
    await sovereign_service.initialize()
    if not sovereign_service.is_active:
        print("Firebase Offline!")
        return

    print("Fetching moonbags...")
    moonbags = await sovereign_service.get_moonbags()
    
    hype_id = None
    for m in moonbags:
        if m.get("symbol") == "HYPEUSDT":
            hype_id = m.get("id")
            print(f"Found HYPEUSDT! ID: {hype_id}")
            break
            
    if hype_id:
        print(f"Nuking {hype_id} from Firebase...")
        await sovereign_service.remove_moonbag(hype_id, reason="NUCLEAR_PURGE_GHOST")
        print("Firestore Nuke Done!")
    else:
        print("HYPEUSDT not found in Firestore.")
        
    print("Checking RTDB directly...")
    if sovereign_service.rtdb:
        # Avoid hanging thread by wrapping in to_thread and timeout isn't strictly necessary but good practice
        rtdb_snaps = await asyncio.to_thread(sovereign_service.rtdb.child("moonbag_vault").get)
        if rtdb_snaps and rtdb_snaps.val():
            found = False
            for key, val in rtdb_snaps.val().items():
                if val.get("symbol") == "HYPEUSDT":
                    print(f"Found HYPEUSDT in RTDB (ID: {key}). Nuking...")
                    await asyncio.to_thread(sovereign_service.rtdb.child("moonbag_vault").child(key).delete)
                    print("RTDB Nuke Done!")
                    found = True
            if not found:
                print("HYPEUSDT not found in RTDB.")
        else:
            print("RTDB is empty.")

asyncio.run(nuke())
os._exit(0)
