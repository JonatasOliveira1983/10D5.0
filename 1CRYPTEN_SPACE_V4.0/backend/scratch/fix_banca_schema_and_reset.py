
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def update_schema():
    db_url = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"
    engine = create_async_engine(db_url)
    try:
        async with engine.begin() as conn:
            print("Updating banca_status schema...")
            # Mudar tipo da coluna ID para String para aceitar 'status'
            await conn.execute(text("ALTER TABLE banca_status ALTER COLUMN id TYPE VARCHAR(50)"))
            
            # Adicionar colunas faltantes se não existirem
            await conn.execute(text("ALTER TABLE banca_status ADD COLUMN IF NOT EXISTS lucro_total_acumulado FLOAT DEFAULT 0.0"))
            await conn.execute(text("ALTER TABLE banca_status ADD COLUMN IF NOT EXISTS lucro_ciclo FLOAT DEFAULT 0.0"))
            await conn.execute(text("ALTER TABLE banca_status ADD COLUMN IF NOT EXISTS vault_total FLOAT DEFAULT 0.0"))
            await conn.execute(text("ALTER TABLE banca_status ADD COLUMN IF NOT EXISTS leverage FLOAT DEFAULT 50.0"))
            await conn.execute(text("ALTER TABLE banca_status ADD COLUMN IF NOT EXISTS saldo_real_bybit FLOAT DEFAULT 0.0"))
            await conn.execute(text("ALTER TABLE banca_status ADD COLUMN IF NOT EXISTS configured_balance FLOAT DEFAULT 100.0"))
            
            # Limpeza das tabelas de trade para não poluir o cálculo
            await conn.execute(text("TRUNCATE TABLE trade_history RESTART IDENTITY CASCADE"))
            await conn.execute(text("TRUNCATE TABLE order_genesis RESTART IDENTITY CASCADE"))
            
            # Reset da banca
            await conn.execute(text("DELETE FROM banca_status"))
            await conn.execute(text("""
                INSERT INTO banca_status (id, saldo_total, lucro_total_acumulado, slots_disponiveis, leverage, configured_balance, status)
                VALUES ('status', 100.0, 0.0, 4, 50.0, 100.0, 'READY')
            """))
            print("✅ Schema updated and Banca reset to $100.00!")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(update_schema())
