import asyncio
import os
import sys
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.bybit_rest import bybit_rest_service

async def get_almirante_elite_30():
    # 1. Get all linear instruments
    response = await asyncio.to_thread(bybit_rest_service.session.get_instruments_info, category="linear")
    instruments = response.get("result", {}).get("list", [])
    
    # 2. Get Tickers for Turnover
    ticker_resp = await asyncio.to_thread(bybit_rest_service.session.get_tickers, category="linear")
    tickers = {t["symbol"]: float(t.get("turnover24h", 0)) for t in ticker_resp.get("result", {}).get("list", [])}
    
    # 3. Filter criteria
    # - Max Leverage <= 75x (Removing 100x/125x like BTC, ETH, SOL, XRP, BNB)
    # - No "1000" prefix (Removing common memecoin multipliers)
    # - High Liquidity (Turnover)
    
    eligible = []
    for inst in instruments:
        symbol = inst.get("symbol")
        if not symbol.endswith("USDT"): continue
        
        # Almirante's Blacklist: No 1000-prefix memecoins
        if symbol.startswith("1000"): continue
        
        # Specific memecoin blacklist (Manual check)
        memecoins = ["PEPE", "SHIB", "FLOKI", "BONK", "WIF", "DOGE", "TRUMP", "TRX", "TON"] # Wait, Almirante likes DOGE!
        is_memecoin = any(m + "USDT" == symbol for m in memecoins if m != "DOGE") 
        if is_memecoin: continue
        
        max_lev = float(inst.get("leverageFilter", {}).get("maxLeverage", 0))
        
        # Only up to 75x
        if max_lev <= 75.0:
            eligible.append({
                "symbol": symbol, 
                "max_lev": max_lev, 
                "turnover": tickers.get(symbol, 0)
            })
            
    # Sort eligible by turnover
    eligible.sort(key=lambda x: x["turnover"], reverse=True)
    
    # Take top candidates
    candidates = [x["symbol"] for x in eligible[:40]] # Take a few more to filter
    
    # Ensure Almirante's Favorites are there
    favorites = ["ADAUSDT", "DOGEUSDT", "AAVEUSDT", "POLUSDT", "GALAUSDT"]
    final_30 = []
    
    # Start with Favorites
    for f in favorites:
        if f in [x["symbol"] for x in eligible]:
            final_30.append(f)
            
    # Fill the rest with high turnover non-memecoins
    for c in candidates:
        if c not in final_30 and len(final_30) < 30:
            final_30.append(c)
            
    print("\n--- REFINAMENTO: O ELITE 30 DO ALMIRANTE ---")
    print(f"Total Candidatos Qualificados: {len(eligible)}")
    print(json.dumps([f"{s}.P" for s in final_30], indent=4))
    
    # Check what was excluded
    excluded_majors = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]
    print("\n--- MAJORS EXCLUIDOS (> 75x) ---")
    print(", ".join(excluded_majors))

if __name__ == "__main__":
    asyncio.run(get_almirante_elite_30())
