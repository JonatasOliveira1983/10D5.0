import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def analyze_recent_movements(db_path, hours=6):
    conn = sqlite3.connect(db_path)
    
    # Get the latest timestamp in the database
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(open_time) FROM klines")
    last_ts = cursor.fetchone()[0]
    
    if not last_ts:
        print("No klines found.")
        return
    
    # Calculate starting timestamp (e.g., 6 hours ago from the last record)
    # open_time is usually in milliseconds
    start_ts = last_ts - (hours * 3600 * 1000)
    
    print(f"Analyzing from {datetime.fromtimestamp(start_ts/1000)} to {datetime.fromtimestamp(last_ts/1000)}")
    
    # Get all klines in this period
    query = f"SELECT symbol, open_time, open, high, low, close FROM klines WHERE open_time >= {start_ts}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("DataFrame is empty.")
        return

    results = []
    symbols = df['symbol'].unique()
    
    for symbol in symbols:
        symbol_df = df[df['symbol'] == symbol].sort_values('open_time')
        if len(symbol_df) < 2:
            continue
            
        start_price = symbol_df.iloc[0]['open']
        end_price = symbol_df.iloc[-1]['close']
        max_price = symbol_df['high'].max()
        min_price = symbol_df['low'].min()
        
        change_pct = ((end_price - start_price) / start_price) * 100
        max_gain_pct = ((max_price - start_price) / start_price) * 100
        max_drawdown_pct = ((min_price - start_price) / start_price) * -100
        
        results.append({
            'symbol': symbol,
            'start_price': start_price,
            'end_price': end_price,
            'change_pct': change_pct,
            'max_gain_pct': max_gain_pct,
            'max_drawdown_pct': max_drawdown_pct
        })
    
    results_df = pd.DataFrame(results)
    
    # Filter for coins with max_gain between 2% and 10%
    interesting_coins = results_df[(results_df['max_gain_pct'] >= 2.0) & (results_df['max_gain_pct'] <= 10.0)].sort_values('max_gain_pct', ascending=False)
    
    print("\nCoins with 2% to 10% evolution during this period:")
    print(interesting_coins.to_string(index=False))
    
    # Also find BTC movement for context
    btc = results_df[results_df['symbol'] == 'BTCUSDT']
    if not btc.empty:
        print("\nBTC Movement Context:")
        print(btc.to_string(index=False))

if __name__ == "__main__":
    db_path = "backtest_data.db"
    analyze_recent_movements(db_path)
