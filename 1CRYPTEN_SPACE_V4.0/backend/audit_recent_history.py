
import asyncio
import os
import sys
from datetime import datetime

sys.path.append(os.getcwd())
from services.firebase_service import firebase_service

async def audit():
    await firebase_service.initialize()
    # Pega os últimos 30 trades
    trades_ref = firebase_service.db.collection("trade_history").order_by("closed_at", direction="DESCENDING").limit(30)
    docs = trades_ref.get()
    
    print(f"{'Date':<25} | {'Symbol':<12} | Slot | Type | ROI")
    print("-" * 70)
    
    count = 0
    for doc in docs:
        t = doc.to_dict()
        closed_at = t.get("closed_at", "N/A")
        symbol = t.get("symbol", "N/A")
        slot_id = t.get("slot_id", "N/A")
        slot_type = t.get("slot_type", "N/A")
        roi = t.get("pnl_percent", 0)
        
        is_mission_trade = False
        if slot_type in ["TREND", "SURF", "SWING"] or slot_id in [3, 4]:
            is_mission_trade = True
            
        mark = " [X]" if is_mission_trade else " [ ]"
        print(f"{str(closed_at):<25} | {symbol:<12} | {slot_id:<4} | {slot_type:<5} | {roi}% {mark}")
        
        if is_mission_trade:
            count += 1
            if count == 10:
                print("--- END OF CYCLE MARKER? ---")

if __name__ == "__main__":
    asyncio.run(audit())
