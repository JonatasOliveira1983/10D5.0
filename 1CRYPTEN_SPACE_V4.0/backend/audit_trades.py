import asyncio
import os
import sys
from datetime import datetime

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service

async def audit():
    await firebase_service.initialize()
    print("--- AUDITORIA DE TRADES RECENTES ---")
    
    # Busca os últimos trades
    docs = await asyncio.to_thread(
        firebase_service.db.collection('trade_history')
        .order_by('closed_at', direction='DESCENDING')
        .limit(10)
        .get
    )
    
    if not docs:
        print("Nenhum trade encontrado no histórico.")
        return

    for doc in docs:
        t = doc.to_dict()
        symbol = t.get("symbol", "???")
        pnl = t.get("pnl_usd", 0)
        roi = t.get("final_roi", 0)
        reason = t.get("close_reason", "unknown")
        closed = t.get("closed_at", "???")
        side = t.get("side", "???")
        
        print(f"[{closed}] {symbol} ({side}) | PnL: ${pnl:.2f} | ROI: {roi}% | Reason: {reason}")

if __name__ == "__main__":
    asyncio.run(audit())
