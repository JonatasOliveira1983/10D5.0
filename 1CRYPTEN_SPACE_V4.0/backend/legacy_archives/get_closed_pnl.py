import asyncio
import os
import sys
from datetime import datetime

# Adjust path to find backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import settings
from services.bybit_rest import bybit_rest_service

async def main():
    print("Fetching closed PnL from Bybit...")
    try:
        # Get closed PnL with limit 50
        response = await asyncio.to_thread(bybit_rest_service.session.get_closed_pnl, category="linear", limit=50)
        pnl_list = response.get("result", {}).get("list", [])
        
        if not pnl_list:
            print("No closed PnL records found.")
            return

        print(f"\nFound {len(pnl_list)} recent closed positions:")
        print("-" * 120)
        for i, p in enumerate(pnl_list):
            sym = p.get("symbol")
            side = p.get("side") # Bye or Sell: closing order side
            qty = p.get("qty")
            entry = float(p.get("avgEntryPrice", 0))
            exit = float(p.get("avgExitPrice", 0))
            pnl = float(p.get("closedPnl", 0))
            created_at = int(p.get("createdTime", 0)) / 1000
            dt = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')
            
            # Position side: if closing order is Sell, position was Long
            pos_type = "LONG" if side == "Sell" else "SHORT"
            
            # ROI approx
            margin = (float(qty) * entry) / 50
            roi = (pnl / margin * 100) if margin > 0 else 0
            
            color_pnl = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
            color_roi = f"+{roi:.2f}%" if roi >= 0 else f"{roi:.2f}%"
            
            print(f"[{dt}] {sym:<12} | {pos_type:<5} | Qty: {qty:<8} | Entry: {entry:<8.5f} | Exit: {exit:<8.5f} | PnL: {color_pnl:<8} ({color_roi})")
            
        print("-" * 120)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    bybit_rest_service.execution_mode = "REAL"
    asyncio.run(main())
