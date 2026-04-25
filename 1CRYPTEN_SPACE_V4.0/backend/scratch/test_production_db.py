
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Forçar encoding UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_conn():
    # Tentando usar o token como senha
    db_url = "postgresql+asyncpg://postgres:5dee6975-be12-4a3a-ac53-6dc851c0bf13@centerbeam.proxy.rlwy.net:54059/railway"
    print(f"Tentando conectar a: {db_url.split('@')[1]}")
    
    engine = create_async_engine(db_url)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Conexao bem-sucedida! Resultado: {result.scalar()}")
            return True
    except Exception as e:
        print(f"Falha na conexao: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_conn())
