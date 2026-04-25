
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check_banca():
    db_url = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"
    engine = create_async_engine(db_url)
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT * FROM banca_status"))
            row = res.fetchone()
            print(f"Banca Row: {row}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_banca())
