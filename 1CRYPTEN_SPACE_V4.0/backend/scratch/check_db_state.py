import asyncio
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from services.firebase_service import firebase_service

async def check_db_slots():
    print(f"Checking RTDB slots at: {settings.FIREBASE_DATABASE_URL}")
    slots = firebase_service.db.reference('slots').get()
    print("\n--- RTDB SLOTS ---")
    print(json.dumps(slots, indent=2))
    
    positions = firebase_service.db.reference('positions').get()
    print("\n--- RTDB POSITIONS ---")
    print(json.dumps(positions, indent=2))

if __name__ == "__main__":
    asyncio.run(check_db_slots())
