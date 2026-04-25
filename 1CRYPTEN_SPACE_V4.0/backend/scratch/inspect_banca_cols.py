
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def inspect_columns():
    db_url = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"
    engine = create_async_engine(db_url)
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'banca_status'"))
            cols = res.fetchall()
            print(f"Columns: {[c[0] for c in cols]}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(inspect_columns())
