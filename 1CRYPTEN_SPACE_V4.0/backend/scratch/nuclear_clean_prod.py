
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os

async def nuclear_clean():
    db_url = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"
    engine = create_async_engine(db_url)
    
    async with engine.begin() as conn:
        print("Starting Nuclear Clean...")
        
        # 1. Truncate Tables
        await conn.execute(text("TRUNCATE TABLE trade_history RESTART IDENTITY CASCADE"))
        await conn.execute(text("TRUNCATE TABLE order_genesis RESTART IDENTITY CASCADE"))
        await conn.execute(text("TRUNCATE TABLE banca_status RESTART IDENTITY CASCADE"))
        
        # 2. Insert Clean Banca Status
        await conn.execute(text("""
            INSERT INTO banca_status (id, saldo_total, lucro_total_acumulado, slots_disponiveis, leverage, risco_real_percent, saldo_real_bybit, configured_balance)
            VALUES ('status', 100.00, 0.00, 4, 50.0, 0.0, 0.0, 100.00)
        """))
        
        print("✅ Nuclear Clean Completed! All history purged.")

if __name__ == "__main__":
    asyncio.run(nuclear_clean())
