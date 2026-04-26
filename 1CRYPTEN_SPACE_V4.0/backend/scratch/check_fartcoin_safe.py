import asyncio
import sys
from sqlalchemy import text
from services.database_service import database_service

async def main():
    with open("c:/Users/spcom/Desktop/10D REAL 4.0/1CRYPTEN_SPACE_V4.0/backend/scratch/db_out.txt", "w", encoding="utf-8") as f:
        f.write("Connecting to DB...\n")
        async with database_service.AsyncSessionLocal() as session:
            f.write("--- FARTCOIN IN HISTORY ---\n")
            result = await session.execute(text("SELECT * FROM trade_history WHERE symbol = 'FARTCOINUSDT'"))
            fartcoin_rows = result.fetchall()
            f.write(f"Fartcoin rows: {len(fartcoin_rows)}\n")
            for r in fartcoin_rows:
                f.write(str(r) + "\n")
                
            f.write("\n--- VAULT CYCLE ---\n")
            result2 = await session.execute(text("SELECT sniper_wins, cycle_profit, cycle_gains_count, total_trades_cycle FROM vault_cycles"))
            f.write(str(result2.fetchall()) + "\n")

            f.write("\n--- RECENT HISTORY (Last 20) ---\n")
            result3 = await session.execute(text("SELECT symbol, pnl, exit_price FROM trade_history ORDER BY timestamp DESC LIMIT 20"))
            for r in result3.fetchall():
                f.write(f"{r[0]} | PNL: {r[1]} | Exit: {r[2]}\n")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
