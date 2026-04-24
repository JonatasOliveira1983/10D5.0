import sqlite3
import pandas as pd
from datetime import datetime

def analyze_recent_movements_optimized(db_path, hours=6):
    conn = sqlite3.connect(db_path)
    
    # Get the latest timestamp
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(open_time) FROM klines")
    last_ts = cursor.fetchone()[0]
    
    if not last_ts:
        print("No klines found.")
        conn.close()
        return
    
    start_ts = last_ts - (hours * 3600 * 1000)
    
    print(f"Analyzing from {datetime.fromtimestamp(start_ts/1000)} to {datetime.fromtimestamp(last_ts/1000)}")
    
    query = """
    WITH SymbolBounds AS (
        SELECT 
            symbol, 
            MIN(open_time) as start_time, 
            MAX(open_time) as end_time,
            MAX(high) as max_high,
            MIN(low) as min_low
        FROM klines 
        WHERE open_time >= ? 
        GROUP BY symbol
    )
    SELECT 
        b.symbol,
        k_start.open as start_price,
        k_end.close as end_price,
        b.max_high,
        b.min_low
    FROM SymbolBounds b
    JOIN klines k_start ON b.symbol = k_start.symbol AND b.start_time = k_start.open_time
    JOIN klines k_end ON b.symbol = k_end.symbol AND b.end_time = k_end.open_time
    """
    
    df = pd.read_sql_query(query, conn, params=(start_ts,))
    conn.close()
    
    if df.empty:
        print("No movements found in this period.")
        return

    df['change_pct'] = ((df['end_price'] - df['start_price']) / df['start_price']) * 100
    df['max_gain_pct'] = ((df['max_high'] - df['start_price']) / df['start_price']) * 100
    df['max_drawdown_pct'] = ((df['min_low'] - df['start_price']) / df['start_price']) * -100
    
    interesting_coins = df[(df['max_gain_pct'] >= 2.0) & (df['max_gain_pct'] <= 15.0)].sort_values('max_gain_pct', ascending=False)
    
    print("\nCoins with 2% to 15% evolution during this period:")
    print(interesting_coins[['symbol', 'start_price', 'end_price', 'max_gain_pct', 'change_pct', 'max_drawdown_pct']].to_string(index=False))
    
    btc = df[df['symbol'] == 'BTCUSDT']
    if not btc.empty:
        print("\nBTC Movement Context:")
        print(btc[['symbol', 'start_price', 'end_price', 'max_gain_pct', 'change_pct', 'max_drawdown_pct']].to_string(index=False))

if __name__ == "__main__":
    db_path = "backtest_data.db"
    analyze_recent_movements_optimized(db_path)
