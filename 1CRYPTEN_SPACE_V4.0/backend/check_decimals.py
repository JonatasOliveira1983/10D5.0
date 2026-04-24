import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.bybit_rest import bybit_rest_service

async def main():
    print("--- Verificando Preços na Bybit ---")
    
    symbols = ["1000PEPEUSDT", "WLDUSDT", "OPUSDT", "ONDOUSDT"]
    print("1. Buscando Tickers...")
    tickers = await bybit_rest_service.get_tickers(symbols)
    
    for symbol in symbols:
        ticker = tickers.get(symbol, {})
        print(f"Ticker {symbol}: {ticker}")
        
    print("\n2. Simulando Cálculo de Entrada Short/Long...")
    for symbol in symbols:
        price = float(tickers.get(symbol, {}).get("lastPrice", 0))
        if price == 0:
            continue
            
        print(f"\n[{symbol}] | Price: {price}")
        roi_short_1pct = execution_protocol_mock(price, price * 1.01, "Sell")
        roi_long_1pct = execution_protocol_mock(price, price * 0.99, "Buy")
        print(f"  -> Se subir 1% (Short) = ROI {roi_short_1pct:.2f}%")
        print(f"  -> Se cair 1% (Long)   = ROI {roi_long_1pct:.2f}%")

def execution_protocol_mock(entry, current, side):
    leverage = 50
    if side.lower() == "buy":
        return ((current - entry) / entry) * leverage * 100
    else:
        return ((entry - current) / entry) * leverage * 100

if __name__ == "__main__":
    asyncio.run(main())
