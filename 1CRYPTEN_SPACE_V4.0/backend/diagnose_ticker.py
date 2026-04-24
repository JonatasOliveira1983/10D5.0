import asyncio
import os
from services.bybit_rest import bybit_rest_service

async def diagnose_ada_ticker():
    symbol = "ADAUSDT"
    print(f"🔍 Diagnosting ticker for {symbol}...")
    
    # 1. Test get_tickers (Multiple)
    tickers = await bybit_rest_service.get_tickers(symbol=symbol)
    ticker_list = tickers.get("result", {}).get("list", [])
    if ticker_list:
        print(f"✅ Found {len(ticker_list)} tickers.")
        for t in ticker_list:
            print(f"   - Symbol: {t.get('symbol')} | Last Price: {t.get('lastPrice')}")
    else:
        print("❌ No tickers found in list.")

    # 2. Test global scan to see if ADA is in there with a different price
    print("\n🔍 Checking global scan for ADA...")
    all_tickers = await bybit_rest_service.get_tickers()
    all_list = all_tickers.get("result", {}).get("list", [])
    ada_matches = [t for t in all_list if "ADA" in t.get("symbol", "")]
    for t in ada_matches:
        print(f"   - Global Match: {t.get('symbol')} | Price: {t.get('lastPrice')}")

if __name__ == "__main__":
    asyncio.run(diagnose_ada_ticker())
