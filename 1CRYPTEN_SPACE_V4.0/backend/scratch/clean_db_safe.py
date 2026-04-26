import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"

async def main():
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        print("Cleaning FARTCOIN from slots...")
        await session.execute(text("""
            UPDATE slots 
            SET symbol = NULL, status_risco = 'LIVRE', pnl_percent = 0, pnl_usd = 0, 
                entry_price = 0, current_stop = 0, target_price = 0, qty = 0, side = NULL,
                order_id = NULL, genesis_id = NULL, timestamp_last_update = extract(epoch from now()),
                pensamento = 'PURGED: Ghost order removed manually'
            WHERE symbol LIKE '%FARTCOIN%'
        """))
        
        await session.execute(text("DELETE FROM moonbags WHERE symbol LIKE '%FARTCOIN%'"))
        
        print("Cleaning Vault History ghosts...")
        res = await session.execute(text("DELETE FROM trade_history WHERE genesis_id LIKE 'RECOVERY-%' OR (pnl = 0 AND reasoning_report IS NULL)"))
        print(f"Deleted {res.rowcount} ghost entries from Vault.")
        
        await session.commit()
    
    await engine.dispose()
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
