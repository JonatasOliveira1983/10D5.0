
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def audit_db():
    db_url = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"
    engine = create_async_engine(db_url)
    try:
        async with engine.connect() as conn:
            # 1. Check Trades
            res = await conn.execute(text("SELECT COUNT(*) FROM trade_history"))
            count = res.scalar()
            print(f"Trade History Count: {count}")
            
            # 2. Check Banca
            res = await conn.execute(text("SELECT * FROM banca_status"))
            rows = res.fetchall()
            print(f"Banca Status Rows: {len(rows)}")
            for r in rows:
                print(f"Row: {r}")
                
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(audit_db())
