import asyncio
import os
import sys
from datetime import datetime

sys.path.append(os.getcwd())
from services.firebase_service import firebase_service

async def main():
    await firebase_service.initialize()
    docs = firebase_service.db.collection("trade_history").order_by("closed_at", direction="DESCENDING").limit(20).stream()
    
    with open('recent_trades.txt', 'w', encoding='utf-8') as f:
        f.write("Recent Trades (Last 20):\n")
        total_pnl = 0
        wins = 0
        losses = 0
        for doc in docs:
            data = doc.to_dict()
            symbol = data.get('symbol')
            side = data.get('side')
            pnl = data.get('realized_pnl', 0)
            roi = data.get('pnl_percent', 0)
            close_reason = data.get('close_reason', 'UNKNOWN')
            pattern = data.get('pattern', 'UNKNOWN')
            score = data.get('score', 0)
            closed_at = data.get('closed_at', 0)
            
            if isinstance(closed_at, (int, float)):
                try:
                    dt = datetime.fromtimestamp(closed_at)
                    closed_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    closed_str = str(closed_at)
            else:
                closed_str = str(closed_at)
                
            total_pnl += pnl
            if pnl > 0:
                wins += 1
            else:
                losses += 1
                
            f.write(f"[{closed_str}] {symbol} {side} | PnL: ${pnl:.4f} ({roi:.2f}%) | Reason: {close_reason} | Score: {score} | Pattern: {pattern}\n")
            
        f.write(f"\nSummary: Wins: {wins}, Losses: {losses}, Total PnL: ${total_pnl:.4f}\n")

if __name__ == "__main__":
    asyncio.run(main())
