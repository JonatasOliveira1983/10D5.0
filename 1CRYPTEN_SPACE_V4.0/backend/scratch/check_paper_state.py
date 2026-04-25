
import asyncio
import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check_state():
    db_url = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"
    engine = create_async_engine(db_url)
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT data FROM system_state WHERE key = 'paper_engine_state'"))
            row = res.fetchone()
            if row:
                data = row[0]
                print(f"Paper State: {json.dumps(data, indent=2)}")
            else:
                print("No paper state found.")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_state())
