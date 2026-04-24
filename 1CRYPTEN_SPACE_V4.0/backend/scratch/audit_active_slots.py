
import asyncio
import os
import sys
import time

# Add backend to path
sys.path.append(os.getcwd())

from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service
from services.execution_protocol import execution_protocol

async def check_current_slots():
    await firebase_service.initialize()
    await bybit_rest_service.initialize()
    
    slots = await firebase_service.get_active_slots()
    print(f"\n--- Current Slots Analysis ({len(slots)} active) ---")
    
    for s in slots:
        symbol = s.get("symbol")
        if not symbol: continue
        
        entry = float(s.get("entry_price", 0))
        side = s.get("side", "Buy")
        
        ticker = await bybit_rest_service.get_tickers(symbol)
        ticker_list = ticker.get("result", {}).get("list", [])
        if not ticker_list:
            print(f"[{symbol}] Could not fetch price")
            continue
            
        cur_p = float(ticker_list[0].get("lastPrice", 0))
        roi = execution_protocol.calculate_roi(entry, cur_p, side)
        
        print(f"[{symbol}] Side: {side} | Entry: {entry} | Current: {cur_p} | ROI: {roi:.2f}%")
        
        # Check logic
        should_close, reason, new_sl = await execution_protocol.process_order_logic(s, cur_p)
        print(f"  > Should Close: {should_close} | Reason: {reason} | New SL: {new_sl}")

if __name__ == "__main__":
    asyncio.run(check_current_slots())
