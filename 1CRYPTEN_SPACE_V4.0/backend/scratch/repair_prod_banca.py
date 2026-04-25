
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def repair_and_reset():
    db_url = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"
    engine = create_async_engine(db_url)
    try:
        async with engine.begin() as conn:
            print("Force updating schema...")
            # Garantir colunas
            cols = [
                ("lucro_total_acumulado", "FLOAT DEFAULT 0.0"),
                ("lucro_ciclo", "FLOAT DEFAULT 0.0"),
                ("vault_total", "FLOAT DEFAULT 0.0"),
                ("leverage", "FLOAT DEFAULT 50.0"),
                ("saldo_real_bybit", "FLOAT DEFAULT 0.0"),
                ("configured_balance", "FLOAT DEFAULT 100.0"),
                ("risco_real_percent", "FLOAT DEFAULT 0.0"),
                ("slots_disponiveis", "INTEGER DEFAULT 4"),
                ("status", "VARCHAR(50) DEFAULT 'READY'"),
                ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            ]
            for col_name, col_type in cols:
                try:
                    await conn.execute(text(f"ALTER TABLE banca_status ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                except Exception as e:
                    print(f"Skipping {col_name}: {e}")

            # Mudar tipo da coluna ID para String para aceitar 'status' e '1'
            try:
                await conn.execute(text("ALTER TABLE banca_status ALTER COLUMN id TYPE VARCHAR(50)"))
            except Exception as e:
                print(f"ID Type Alteration: {e}")
            
            # Limpar lixo
            await conn.execute(text("TRUNCATE TABLE trade_history RESTART IDENTITY CASCADE"))
            await conn.execute(text("TRUNCATE TABLE order_genesis RESTART IDENTITY CASCADE"))
            await conn.execute(text("DELETE FROM banca_status"))
            
            # Inserir ID 1 (que o backend usa) e ID 'status' (para compatibilidade legada)
            await conn.execute(text("""
                INSERT INTO banca_status (id, saldo_total, lucro_total_acumulado, slots_disponiveis, leverage, configured_balance, status)
                VALUES ('1', 100.0, 0.0, 4, 50.0, 100.0, 'ONLINE')
            """))
            await conn.execute(text("""
                INSERT INTO banca_status (id, saldo_total, lucro_total_acumulado, slots_disponiveis, leverage, configured_balance, status)
                VALUES ('status', 100.0, 0.0, 4, 50.0, 100.0, 'ONLINE')
            """))
            print("✅ Production Postgres Repaired and Reset to $100.00!")
            
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(repair_and_reset())
