import sqlite3
import json
import os

db_path = "backtest_data.db"
output_path = "scratch/db_dump.json"

def dump_info():
    if not os.path.exists(db_path):
        return {"error": "DB not found"}
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get last 5 klines
    cursor.execute("SELECT * FROM klines ORDER BY start_time DESC LIMIT 5")
    last_klines = cursor.fetchall()
    
    # Get count
    cursor.execute("SELECT COUNT(*) FROM klines")
    count = cursor.fetchone()[0]
    
    # Get intervals
    cursor.execute("SELECT DISTINCT interval FROM klines")
    intervals = [r[0] for r in cursor.fetchall()]
    
    # Get latest 10 symbols with max gain > 2% in last 12 hours
    cursor.execute("SELECT MAX(start_time) FROM klines")
    last_ts = cursor.fetchone()[0]
    start_ts = last_ts - (12 * 3600 * 1000)
    
    cursor.execute("""
        SELECT symbol, MAX(high) as h, MIN(low) as l, MIN(open) as o, MAX(close) as c
        FROM klines 
        WHERE start_time >= ? AND interval = '15m'
        GROUP BY symbol
    """, (start_ts,))
    
    potential = []
    for row in cursor.fetchall():
        symbol, high, low, open_p, close_p = row
        gain = ((high - open_p) / open_p) * 100
        if 2.0 <= gain <= 10.0:
            potential.append({
                "symbol": symbol,
                "gain": round(gain, 2),
                "net": round(((close_p - open_p) / open_p) * 100, 2)
            })
            
    potential.sort(key=lambda x: x['gain'], reverse=True)
    
    conn.close()
    return {
        "count": count,
        "intervals": intervals,
        "last_klines": last_klines,
        "potential": potential[:20]
    }

if __name__ == "__main__":
    if not os.path.exists("scratch"):
        os.makedirs("scratch")
    info = dump_info()
    with open(output_path, "w") as f:
        json.dump(info, f, indent=2)
