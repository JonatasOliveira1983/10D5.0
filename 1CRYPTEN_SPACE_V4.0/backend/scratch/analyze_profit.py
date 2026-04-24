import sqlite3
import os
from datetime import datetime

db_path = "backtest_data.db"

def analyze():
    if not os.path.exists(db_path):
        return "DB not found"
        
    conn = sqlite3.connect(db_path)
    # Get last 12 hours
    res = conn.execute("SELECT MAX(start_time) FROM klines").fetchone()
    if not res or not res[0]:
        return "No data in DB"
    last_ts = res[0]
    start_ts = last_ts - (12 * 3600 * 1000)
    
    # Get all symbols with data in last 12h
    # Note: 1CRYPTEN system uses 'interval' column which can be '5m', '1h', etc.
    # We'll use '1h' if '15m' or '5m' is not available.
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT interval FROM klines")
    intervals = [r[0] for r in cur.fetchall()]
    
    target_interval = '15m' if '15m' in intervals else ('5m' if '5m' in intervals else '1h')
    
    query = """
        SELECT symbol, MIN(start_time) as first_ts, MAX(start_time) as last_ts,
               MIN(low) as min_low, MAX(high) as max_high
        FROM klines 
        WHERE start_time >= ? AND interval = ?
        GROUP BY symbol
    """
    cur.execute(query, (start_ts, target_interval))
    symbols_data = cur.fetchall()
    
    results = []
    for row in symbols_data:
        symbol, first_ts, last_ts_sym, min_low, max_high = row
        
        # Get start/end prices
        start_price = conn.execute("SELECT open FROM klines WHERE symbol=? AND interval=? AND start_time=?", (symbol, target_interval, first_ts)).fetchone()[0]
        end_price = conn.execute("SELECT close FROM klines WHERE symbol=? AND interval=? AND start_time=?", (symbol, target_interval, last_ts_sym)).fetchone()[0]
        
        move_to_high = ((max_high - start_price) / start_price) * 100
        net_change = ((end_price - start_price) / start_price) * 100
        drawdown = ((min_low - start_price) / start_price) * 100
        
        if 2.0 <= move_to_high <= 15.0:
            results.append({
                "symbol": symbol,
                "max_gain": round(move_to_high, 2),
                "net_gain": round(net_change, 2),
                "max_dd": round(drawdown, 2)
            })
            
    results.sort(key=lambda x: x['max_gain'], reverse=True)
    
    print(f"--- ANALISE DE OPORTUNIDADES (Ultimas 12h) ---")
    print(f"Periodo: {datetime.fromtimestamp(start_ts/1000)} - {datetime.fromtimestamp(last_ts/1000)}")
    print(f"Intervalo usado: {target_interval}")
    print(f"{'SYMBOL':<15} | {'MAX GAIN':<10} | {'NET GAIN':<10} | {'MAX DD':<10}")
    print("-" * 55)
    for r in results[:20]:
        print(f"{r['symbol']:<15} | {r['max_gain']:>8}% | {r['net_gain']:>8}% | {r['max_dd']:>8}%")
    
    # Check BTC
    btc = [r for r in results if r['symbol'] == 'BTCUSDT']
    if btc:
        b = btc[0]
        print("\nCONTEXTO BTC:")
        print(f"BTCUSDT: Max Gain: {b['max_gain']}% | Net: {b['net_gain']}% | Max DD: {b['max_dd']}%")
    else:
        # Get BTC even if not in range
        cur.execute("SELECT MIN(start_time), MAX(start_time), MIN(low), MAX(high) FROM klines WHERE symbol='BTCUSDT' AND start_time >= ? AND interval=?", (start_ts, target_interval))
        btc_row = cur.fetchone()
        if btc_row and btc_row[0]:
            f_ts, l_ts, m_low, m_high = btc_row
            s_p = conn.execute("SELECT open FROM klines WHERE symbol='BTCUSDT' AND interval=? AND start_time=?", (target_interval, f_ts)).fetchone()[0]
            e_p = conn.execute("SELECT close FROM klines WHERE symbol='BTCUSDT' AND interval=? AND start_time=?", (target_interval, l_ts)).fetchone()[0]
            m_g = round(((m_high - s_p) / s_p) * 100, 2)
            n_c = round(((e_p - s_p) / s_p) * 100, 2)
            m_d = round(((m_low - s_p) / s_p) * 100, 2)
            print("\nCONTEXTO BTC:")
            print(f"BTCUSDT: Max Gain: {m_g}% | Net: {n_c}% | Max DD: {m_d}%")

    conn.close()

if __name__ == "__main__":
    analyze()
