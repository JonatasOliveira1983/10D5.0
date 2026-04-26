import os
import asyncio
import asyncpg
from dotenv import load_dotenv

async def check():
    db_url = "postgresql://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"
    conn = await asyncpg.connect(db_url)
    
    banca = await conn.fetchrow("SELECT saldo_total, status FROM banca_status WHERE id = 1")
    trades = await conn.fetchval("SELECT count(*) FROM trade_history")
    all_slots = await conn.fetch("SELECT id, symbol, status_risco FROM slots ORDER BY id")
    vault = await conn.fetchrow("SELECT mega_cycle_wins, cycle_profit FROM vault_cycles WHERE id = 1")
    
    print(f"BANCA: ${banca['saldo_total']} ({banca['status']})")
    print(f"TRADES NO HISTORICO: {trades}")
    print(f"VAULT MEGA WINS: {vault['mega_cycle_wins']}")
    print(f"VAULT CYCLE PROFIT: ${vault['cycle_profit']}")
    print("\nSLOTS:")
    for s in all_slots:
        print(f"  Slot {s['id']}: {s['symbol'] or 'LIVRE'} ({s['status_risco']})")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check())
