import asyncio
import aiohttp

async def get_elite_pairs():
    url = "https://api.bybit.com/v5/market/instruments-info?category=linear&limit=1000"
    candidates = {}
    async with aiohttp.ClientSession() as session:
        cursor = ""
        while True:
            params = {"category": "linear", "limit": 1000}
            if cursor: params["cursor"] = cursor
            async with session.get(url, params=params) as response:
                data = await response.json()
                instr_list = data.get("result", {}).get("list", [])
                for info in instr_list:
                    symbol = info.get("symbol")
                    if not symbol or not symbol.endswith("USDT"): continue
                    max_lev = float(info.get("leverageFilter", {}).get("maxLeverage", 0))
                    if max_lev == 50.0:
                        candidates[symbol] = info
                cursor = data.get("result", {}).get("nextPageCursor")
                if not cursor: break
    
    print(f"Total 50x pairs: {len(candidates)}")
    for sym in ['SPXUSDT', 'JASMYUSDT', 'TIAUSDT']:
        if sym in candidates:
            print(f"{sym} is IN the 50x list.")
        else:
            print(f"{sym} is NOT in the 50x list.")

asyncio.run(get_elite_pairs())
