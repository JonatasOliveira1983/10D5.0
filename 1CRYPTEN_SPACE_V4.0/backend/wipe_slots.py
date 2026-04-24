import asyncio
import logging
from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service

async def reset_paper_slots():
    print("🚀 Resetting Firebase Slots for PAPER recovery...")
    slots = await firebase_service.get_active_slots()
    for slot in slots:
        slot_id = slot.get("id")
        symbol = slot.get("symbol")
        if symbol and symbol != "SCANNING":
            print(f"🧹 Clearing slot {slot_id} ({symbol})...")
            await firebase_service.hard_reset_slot(slot_id, "PAPER_RECOVERY_WIPE", 0.0)
    # 2. Local JSON Wipe
    import json
    import os
    json_path = "paper_storage.json"
    clean_state = {"positions": [], "balance": 1000.0, "history": []}
    with open(json_path, 'w') as f:
        json.dump(clean_state, f, indent=2)
    print(f"💾 Clean state written to {json_path}")
    
    print("✅ All systems cleared.")

if __name__ == "__main__":
    asyncio.run(reset_paper_slots())
