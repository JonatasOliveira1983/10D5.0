import asyncio
import aiohttp
import time

async def get_klines(symbol):
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=120&limit=50"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            klines = data.get("result", {}).get("list", [])
            candles = klines[::-1]
            closes = [float(c[4]) for c in candles]
            sma8 = sum(closes[-8:]) / 8 if len(closes) >= 8 else sum(closes) / len(closes)
            sma21 = sum(closes[-21:]) / 21 if len(closes) >= 21 else sum(closes) / len(closes)
            if sma8 > sma21: trend = 'BULLISH_ARMED'
            elif sma8 < sma21: trend = 'BEARISH_ARMED'
            else: trend = 'NEUTRAL'
            print(f"{symbol}: SMA8={sma8:.4f}, SMA21={sma21:.4f} -> {trend}")

async def main():
    await get_klines('SPXUSDT')
    await get_klines('JASMYUSDT')
    await get_klines('TIAUSDT')

asyncio.run(main())
