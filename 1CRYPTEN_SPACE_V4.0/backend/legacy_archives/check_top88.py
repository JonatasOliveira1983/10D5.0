import asyncio
from services.bybit_rest import bybit_rest_service
from services.bybit_ws import bybit_ws_service
from services.signal_generator import SignalGenerator
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    print("Initialising REST...")
    await bybit_rest_service.initialize()
    print("REST initialized.")
    pairs = await bybit_rest_service.get_elite_50x_pairs()
    print(f"Top 88 pairs length: {len(pairs)}")
    if 'SPXUSDT.P' in pairs:
        print("SPXUSDT.P is in the Top 88 pairs.")
    else:
        print("SPXUSDT.P is NOT in the Top 88 pairs!!!")
        # Find where it is
        all_tickers = bybit_rest_service.session.get_tickers(category="linear").get("result", {}).get("list", [])
        spx = next((t for t in all_tickers if t.get('symbol') == 'SPXUSDT'), None)
        if spx:
            print(f"SPXUSDT turnover is {spx.get('turnover24h')}")
        else:
            print("SPXUSDT not found in tickers.")

asyncio.run(main())
