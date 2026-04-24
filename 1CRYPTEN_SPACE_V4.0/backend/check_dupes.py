
import asyncio
import os
import sys

# Adicionar o caminho do backend para importar os serviços
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

from services.firebase_service import FirebaseService

async def list_recent_trades():
    fs = FirebaseService()
    await fs.initialize()
    
    trades = await fs.get_trade_history(limit=50)
    print(f"Total trades fetched: {len(trades)}")
    
    seen = {}
    duplicates = []
    
    for t in trades:
        symbol = t.get("symbol")
        side = t.get("side")
        ts = t.get("timestamp")
        pnl = t.get("pnl")
        doc_id = t.get("id")
        
        # Chave simplificada para detectar duplicatas (mesmo símbolo e lado, timestamp aproximado)
        # Como o timestamp é ISO string (ex: 2026-03-21T19:33:00), vamos pegar até o minuto
        ts_minute = str(ts)[:16] 
        key = (symbol, side, ts_minute)
        
        if key in seen:
            duplicates.append((t, seen[key]))
        else:
            seen[key] = t

    if not duplicates:
        print("No duplicates found in the last 50 trades.")
    else:
        print(f"Found {len(duplicates)} potential duplicate pairs:")
        for dup, original in duplicates:
            print(f"Duplicate: {dup['symbol']} {dup['side']} at {dup['timestamp']} (ID: {dup['id']})")
            print(f"Original:  {original['symbol']} {original['side']} at {original['timestamp']} (ID: {original['id']})")
            print("-" * 20)

if __name__ == "__main__":
    asyncio.run(list_recent_trades())
