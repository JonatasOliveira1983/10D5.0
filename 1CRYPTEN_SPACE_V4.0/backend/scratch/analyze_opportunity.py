import sqlite3
import pandas as pd
from datetime import datetime

def analyze_opportunities(db_path):
    conn = sqlite3.connect(db_path)
    
    # Get last timestamp in DB
    last_ts = conn.execute("SELECT MAX(start_time) FROM klines").fetchone()[0]
    if not last_ts:
        print("No data found in klines.")
        return
        
    # Analyze last 12 hours
    start_ts = last_ts - (12 * 3600 * 1000)
    
    print(f"Analysis Period: {datetime.fromtimestamp(start_ts/1000)} to {datetime.fromtimestamp(last_ts/1000)}")
    
    # Query all coins with 15m or 1h data (prefer smaller interval if available)
    # Let's check which intervals we have first
    intervals = [r[0] for r in conn.execute("SELECT DISTINCT interval FROM klines").fetchall()]
    print(f"Found intervals: {intervals}")
    
    target_interval = '15m' if '15m' in intervals else ('5m' if '5m' in intervals else '1h')
    print(f"Using interval: {target_interval}")
    
    query = f"""
    SELECT symbol, start_time, open, high, low, close 
    FROM klines 
    WHERE start_time >= {start_ts} AND interval = '{target_interval}'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("No klines found for this period/interval.")
        return
        
    results = []
    symbols = df['symbol'].unique()
    
    for symbol in symbols:
        sdf = df[df['symbol'] == symbol].sort_values('start_time')
        if len(sdf) < 2: continue
        
        entry_price = sdf.iloc[0]['open']
        final_price = sdf.iloc[-1]['close']
        max_high = sdf['high'].max()
        min_low = sdf['low'].min()
        
        # Max gain from start to any point in the 12h
        max_gain = ((max_high - entry_price) / entry_price) * 100
        # Final gain
        net_gain = ((final_price - entry_price) / entry_price) * 100
        # Max drawdown
        max_dd = ((min_low - entry_price) / entry_price) * 100
        
        results.append({
            'symbol': symbol,
            'max_gain': max_gain,
            'net_gain': net_gain,
            'max_dd': max_dd
        })
        
    res_df = pd.DataFrame(results)
    
    # Filter for 2% to 10% max gain
    opportunities = res_df[(res_df['max_gain'] >= 2.0) & (res_df['max_gain'] <= 10.0)].sort_values('max_gain', ascending=False)
    
    print("\nPotential Opportunities (2% - 10% gain):")
    print(opportunities.head(20).to_string(index=False))
    
    # Analyze if they would be profitable with 50x leverage and 1% SL
    # actually let's just show the raw data first.
    
    btc = res_df[res_df['symbol'] == 'BTCUSDT']
    if not btc.empty:
        print("\nBTC Performance:")
        print(btc.to_string(index=False))

if __name__ == "__main__":
    db_path = "backtest_data.db"
    analyze_opportunities(db_path)
