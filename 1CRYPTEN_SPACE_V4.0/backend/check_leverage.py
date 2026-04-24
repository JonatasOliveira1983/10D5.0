import asyncio
import aiohttp

async def get_leverage(symbol):
    url = f"https://api.bybit.com/v5/market/instruments-info?category=linear&symbol={symbol}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            list_data = data.get("result", {}).get("list", [])
            if list_data:
                leverage = list_data[0].get("leverageFilter", {}).get("maxLeverage", "Unknown")
                print(f"{symbol}: MAX LEVERAGE = {leverage}x")
            else:
                print(f"{symbol}: Not found")

async def main():
    await get_leverage('SPXUSDT')
    await get_leverage('JASMYUSDT')
    await get_leverage('TIAUSDT')

asyncio.run(main())
