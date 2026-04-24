import asyncio
import os
import sys
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.bybit_rest import bybit_rest_service

async def get_refined_elite_30():
    all_liquid_symbols = await bybit_rest_service.get_elite_50x_pairs() # This returns symbols with > 0 turnover
    
    # Current Elite 30 (for comparison)
    current_elite_30 = [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "ADAUSDT",
        "SUIUSDT", "LINKUSDT", "AVAXUSDT", "NEARUSDT", "APTUSDT", "INJUSDT",
        "RNDRUSDT", "ARBUSDT", "DOGEUSDT", "WIFUSDT", "TRUMPUSDT", "AAVEUSDT",
        "OPUSDT", "POLUSDT", "DOTUSDT", "FTMUSDT", "SEIUSDT", "TIAUSDT",
        "IMXUSDT", "FETUSDT", "TAOUSDT", "GALAUSDT", "ENAUSDT", "OMUSDT"
    ]
    
    # Get instruments info to check leverage
    response = await asyncio.to_thread(bybit_rest_service.session.get_instruments_info, category="linear")
    instruments = response.get("result", {}).get("list", [])
    
    # Map symbols to max leverage and turnover
    ticker_resp = await asyncio.to_thread(bybit_rest_service.session.get_tickers, category="linear")
    tickers = {t["symbol"]: float(t.get("turnover24h", 0)) for t in ticker_resp.get("result", {}).get("list", [])}
    
    eligible = []
    for inst in instruments:
        symbol = inst.get("symbol")
        if not symbol.endswith("USDT"): continue
        
        max_lev = float(inst.get("leverageFilter", {}).get("maxLeverage", 0))
        turnover = tickers.get(symbol, 0)
        
        if max_lev == 50.0:
            eligible.append({"symbol": symbol, "max_lev": max_lev, "turnover": turnover})
            
    # Sort eligible by turnover
    eligible.sort(key=lambda x: x["turnover"], reverse=True)
    
    top_30_50x_only = [x["symbol"] for x in eligible[:30]]
    
    print("\n--- ATUAIS NO ELITE 30 COM LEVERAGE > 50x (A SEREM REMOVIDOS) ---")
    for sym in current_elite_30:
        clean_sym = sym.replace(".P", "")
        inst = next((i for i in instruments if i["symbol"] == clean_sym), None)
        if inst:
            max_lev = float(inst.get("leverageFilter", {}).get("maxLeverage", 0))
            if max_lev > 50.0:
                print(f"{clean_sym}: {max_lev}x")

    print("\n--- SUGESTÃO: NOVO ELITE 30 (SOMENTE 50x MAX) ---")
    formatted_list = [f"{s}.P" for s in top_30_50x_only]
    print(json.dumps(formatted_list, indent=4))

if __name__ == "__main__":
    asyncio.run(get_refined_elite_30())
