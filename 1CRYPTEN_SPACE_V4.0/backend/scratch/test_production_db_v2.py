
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_conn(user, password, host, port, dbname):
    db_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
    print(f"Testando: {user}@{host}:{port}/{dbname}")
    
    engine = create_async_engine(db_url)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"SUCCESS: {result.scalar()}")
            return True
    except Exception as e:
        print(f"FAILED: {str(e)[:100]}")
        return False
    finally:
        await engine.dispose()

async def main():
    token = "5dee6975-be12-4a3a-ac53-6dc851c0bf13"
    host = "centerbeam.proxy.rlwy.net"
    port = 54059
    
    combinations = [
        ("postgres", token, host, port, "railway"),
        ("postgres", token, host, port, "postgres"),
        ("railway", token, host, port, "railway"),
        ("railway", token, host, port, "postgres"),
    ]
    
    for user, pwd, h, p, db in combinations:
        if await test_conn(user, pwd, h, p, db):
            print(f"\n--- ENCONTRADO! ---")
            print(f"URL: postgresql+asyncpg://{user}:{pwd}@{h}:{p}/{db}")
            break

if __name__ == "__main__":
    asyncio.run(main())
