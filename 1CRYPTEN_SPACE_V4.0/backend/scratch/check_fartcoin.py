import asyncio
import sys
import json
from datetime import datetime
from services.database_service import database_service

async def main():
    output = []
    output.append("--- SLOTS ---")
    slots = await database_service.get_active_slots()
    for s in slots:
        output.append(f"{s.get('id')} {s.get('symbol')} {s.get('genesis_id')}")

    output.append("\n--- FARTCOIN IN HISTORY ---")
    conn = await database_service._get_connection()
    try:
        if conn:
            rows = await conn.fetch("SELECT * FROM trade_history WHERE symbol = 'FARTCOINUSDT'")
            for r in rows:
                # convert dict values to string to avoid datetime serialization issue
                output.append(str(dict(r)))
            
            output.append("\n--- RECENT HISTORY (Last 20) ---")
            rows2 = await conn.fetch("SELECT symbol, pnl, exit_reason, genesis_id, closed_at FROM trade_history ORDER BY closed_at DESC LIMIT 20")
            for r in rows2:
                output.append(f"{r['symbol']} {r['pnl']} {r['exit_reason']} {r['genesis_id']} {r['closed_at']}")
                
    finally:
        if conn:
            await conn.close()
            
    with open('c:/Users/spcom/Desktop/10D REAL 4.0/1CRYPTEN_SPACE_V4.0/backend/scratch/db_out_utf8.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(main())
