import firebase_admin
from firebase_admin import credentials, firestore
import os

def analyze_trade(symbol_search="BIOUSDT"):
    cred_path = "c:\\Users\\spcom\\Desktop\\10D REAL 4.0\\1CRYPTEN_SPACE_V4.0\\backend\\serviceAccountKey.json"
    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except:
        pass
        
    db = firestore.client()
    
    # 1. Search in trade_history (without index requirement)
    print(f"--- ANALYZING {symbol_search} ---")
    history_ref = db.collection("trade_history")
    
    # Filter only by symbol
    docs = history_ref.where("symbol", "in", [symbol_search, f"{symbol_search}.P"]).stream()
    
    trades = []
    for doc in docs:
        d = doc.to_dict()
        d['id'] = doc.id
        trades.append(d)
    
    # Sort in memory
    trades.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    for d in trades[:3]:
        print(f"\n[TRADE HISTORY] ID: {d['id']}")
        print(f"Symbol: {d.get('symbol')} | Side: {d.get('side')} | PnL: ${d.get('pnl', 0):.2f} | ROI: {d.get('roi', 0):.2f}%")
        print(f"Entry: ${d.get('entry_price')} | Exit: ${d.get('exit_price')}")
        print(f"Reason: {d.get('close_reason')}")
        print(f"Timestamp: {d.get('timestamp')}")
        print(f"Genesis ID: {d.get('genesis_id')}")

    # 2. Search in orders_genesis
    print("\n--- GENESIS DATA ---")
    genesis_ref = db.collection("orders_genesis")
    gen_docs = genesis_ref.where("symbol", "in", [symbol_search, f"{symbol_search}.P"]).stream()
    
    geneses = []
    for doc in gen_docs:
        d = doc.to_dict()
        d['id'] = doc.id
        geneses.append(d)
        
    geneses.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    for d in geneses[:3]:
        print(f"\n[GENESIS] ID: {d['id']}")
        print(f"Genesis ID: {d.get('genesis_id')}")
        signal_data = d.get('signal_data', {})
        print(f"Strategy: {signal_data.get('strategy')} | Score: {signal_data.get('score')}")
        print(f"Indicators: {signal_data.get('indicators')}")
        print(f"Librarian DNA: {d.get('librarian_dna')}")
        oracle_state = d.get('oracle_state', {})
        print(f"Oracle: ADX={oracle_state.get('btc_adx')} | Trend={oracle_state.get('btc_trend')}")

if __name__ == "__main__":
    analyze_trade("BIOUSDT")
