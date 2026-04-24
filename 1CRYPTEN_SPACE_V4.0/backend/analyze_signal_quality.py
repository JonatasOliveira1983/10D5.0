import asyncio
import os
import sys
from datetime import datetime
import json

sys.path.append(os.getcwd())
try:
    from services.sovereign_service import sovereign_service
except Exception as e:
    print(f"Error importing sovereign_service: {e}")
    sys.exit(1)

async def analyze():
    print("Initialize Firebase...")
    await sovereign_service.initialize()
    if not sovereign_service.is_active:
        print("❌ Firebase not active. Check credentials.")
        return

    print("Fetching trade history...")
    # Get last 100 trades for a meaningful analysis
    docs = sovereign_service.db.collection("trade_history").order_by("timestamp", direction="DESCENDING").limit(100).stream()
    
    stats = {
        "total": 0,
        "wins": 0,
        "losses": 0,
        "total_pnl": 0,
        "patterns": {},
        "layers": {},
        "reasons": {}
    }
    
    trades = []
    for doc in docs:
        data = doc.to_dict()
        stats["total"] += 1
        
        pnl = data.get('pnl', data.get('realized_pnl', 0))
        roi = data.get('pnl_percent', data.get('roi', 0))
        pattern = data.get('pattern', 'UNKNOWN')
        layer = data.get('layer', 'UNKNOWN')
        reason = data.get('close_reason', 'UNKNOWN')
        
        stats["total_pnl"] += pnl
        if pnl > 0:
            stats["wins"] += 1
        else:
            stats["losses"] += 1
            
        # Pattern analysis
        if pattern not in stats["patterns"]:
            stats["patterns"][pattern] = {"wins": 0, "losses": 0, "total_pnl": 0, "count": 0}
        stats["patterns"][pattern]["count"] += 1
        stats["patterns"][pattern]["total_pnl"] += pnl
        if pnl > 0: stats["patterns"][pattern]["wins"] += 1
        else: stats["patterns"][pattern]["losses"] += 1
        
        # Layer analysis
        if layer not in stats["layers"]:
            stats["layers"][layer] = {"wins": 0, "losses": 0, "count": 0}
        stats["layers"][layer]["count"] += 1
        if pnl > 0: stats["layers"][layer]["wins"] += 1
        else: stats["layers"][layer]["losses"] += 1

    # Format output
    print("\n=== SIGNAL QUALITY ANALYSIS ===")
    print(f"Total Trades: {stats['total']}")
    print(f"Win Rate: {(stats['wins']/stats['total']*100 if stats['total']>0 else 0):.1f}%")
    print(f"Total PnL: ${stats['total_pnl']:.2f}")
    
    print("\n--- PERFORMANCE BY PATTERN ---")
    for p, p_data in sorted(stats["patterns"].items(), key=lambda x: x[1]['total_pnl'], reverse=True):
        wr = (p_data['wins']/p_data['count']*100 if p_data['count']>0 else 0)
        print(f"[{p:20}] WR: {wr:5.1f}% | PnL: ${p_data['total_pnl']:7.2f} | Count: {p_data['count']}")

    print("\n--- PERFORMANCE BY LAYER ---")
    for l, l_data in stats["layers"].items():
        wr = (l_data['wins']/l_data['count']*100 if l_data['count']>0 else 0)
        print(f"[{l:20}] WR: {wr:5.1f}% | Count: {l_data['count']}")

if __name__ == "__main__":
    asyncio.run(analyze())
