import asyncio
import json
from config import settings
from services.bybit_rest import bybit_rest_service

async def main():
    positions = await bybit_rest_service.get_active_positions()
    for p in positions:
        sym = p.get("symbol")
        side = p.get("side")
        size = float(p.get("size", 0))
        entry = float(p.get("avgPrice", 0))
        im = float(p.get("positionIM", 0))
        sl = p.get("stopLoss", 0)
        unrealized = float(p.get("unrealisedPnl", 0))
        leverage = float(p.get("leverage", 50))
        
        real_margin = im if im > 0 else (size * entry) / leverage
        pnl_pct = (unrealized / real_margin * 100) if real_margin > 0 else 0
        print(f"[{sym} {side}] Size:{size} Entry:{entry} IM:{im} Unrealized:{unrealized} CalcMargin:{real_margin} PnlPct:{pnl_pct}%")

if __name__ == "__main__":
    asyncio.run(main())
