import asyncio
from services.signal_generator import signal_generator
from services.bybit_rest import bybit_rest_service

async def audit_funnel():
    await bybit_rest_service.initialize()
    
    # Check BTC Daily
    btc_daily = await signal_generator.get_daily_macro_filter("BTCUSDT.P")
    print(f"BTC Daily Trend: {btc_daily.get('trend')}")
    
    # Try to run one iteration of Stage 1 & 2 logic manually
    from services.bybit_ws import bybit_ws_service
    # Mock active symbols if empty
    if not getattr(bybit_ws_service, 'active_symbols', []):
        resp = await asyncio.to_thread(bybit_rest_service.session.get_tickers, category="linear")
        symbols = [t['symbol'] + ".P" for t in resp.get('result', {}).get('list', [])]
        bybit_ws_service.active_symbols = symbols
    
    print(f"Total Symbols: {len(bybit_ws_service.active_symbols)}")
    
    # Trace a few assets mentioned by user
    targets = ['DOTUSDT.P', 'WLDUSDT.P', 'WIFUSDT.P']
    for t in targets:
        # Check tactical score
        tactical = await signal_generator.get_30m_tactical_analysis(t)
        print(f"Asset: {t} | Tactical Score: {tactical.get('tactical_score')} | Side: {tactical.get('side_label')}")
        
if __name__ == "__main__":
    asyncio.run(audit_funnel())
