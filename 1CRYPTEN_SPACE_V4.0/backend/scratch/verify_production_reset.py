
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_prod_db():
    prod_url = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"
    engine = create_async_engine(prod_url)
    
    try:
        async with engine.connect() as conn:
            # Check Banca
            banca = await conn.execute(text("SELECT * FROM banca_status"))
            b_rows = banca.fetchall()
            print(f"--- BANCA ({len(b_rows)} rows) ---")
            for r in b_rows:
                print(r)
            
            # Check Slots
            slots = await conn.execute(text("SELECT id, symbol, leverage, status_risco FROM slots ORDER BY id"))
            s_rows = slots.fetchall()
            print(f"\n--- SLOTS ({len(s_rows)} rows) ---")
            for r in s_rows:
                print(r)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

    # 3. Check Trade History
    res_trades = await conn.execute(text("SELECT count(*) FROM trade_history"))
    count_trades = res_trades.scalar()
    print(f"--- TRADE HISTORY ---")
    print(f"Count: {count_trades}")

if __name__ == "__main__":
    asyncio.run(check_prod_db())
