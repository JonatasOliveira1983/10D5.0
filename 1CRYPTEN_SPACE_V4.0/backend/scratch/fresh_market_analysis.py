import urllib.request
import json
import time
from datetime import datetime

def get_klines(symbol, interval="60", limit=100):
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={interval}&limit={limit}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get("retCode") == 0:
                return data["result"]["list"]
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    return []

def analyze_opportunities():
    # symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "BNBUSDT", "LINKUSDT", "DOTUSDT", "MATICUSDT"]
    symbols = ["BTCUSDT", "SOLUSDT", "XRPUSDT", "ETHUSDT", "BIOUSDT", "HYPEUSDT", "ORDIUSDT", "PEPEUSDT", "FETUSDT", "RENDERUSDT", "SUIUSDT", "TAOUSDT"]
    
    results = []
    
    print(f"Buscando dados recentes para análise... (Tempo atual: {datetime.now()})")
    
    for symbol in symbols:
        klines = get_klines(symbol, interval="60", limit=24) # Last 24 hours
        if not klines: continue
        
        # Bybit returns newest first
        # [start_time, open, high, low, close, volume, turnover]
        candles = klines[::-1]
        start_price = float(candles[0][1])
        end_price = float(candles[-1][4])
        max_high = max(float(k[2]) for k in candles)
        min_low = min(float(k[3]) for k in candles)
        
        gain = ((max_high - start_price) / start_price) * 100
        net = ((end_price - start_price) / start_price) * 100
        dd = ((min_low - start_price) / start_price) * 100
        
        results.append({
            "symbol": symbol,
            "gain": round(gain, 2),
            "net": round(net, 2),
            "dd": round(dd, 2)
        })
        time.sleep(0.05)
        
    results.sort(key=lambda x: x['gain'], reverse=True)
    
    print("\n--- ANÁLISE DE OPORTUNIDADES (Últimas 24h) ---")
    print(f"{'MOEDA':<15} | {'MAX GAIN':<10} | {'NET GAIN':<10} | {'MAX DD':<10}")
    print("-" * 55)
    for r in results:
        print(f"{r['symbol']:<15} | {r['gain']:>8}% | {r['net']:>8}% | {r['dd']:>8}%")

if __name__ == "__main__":
    analyze_opportunities()
