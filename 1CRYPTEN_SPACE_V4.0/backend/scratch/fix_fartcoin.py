import asyncio
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from services.sovereign_service import sovereign_service
from services.database_service import database_service
from services.bybit_rest import bybit_rest_service
from sqlalchemy import text

async def main():
    await database_service.init_db()
    await bybit_rest_service._load_paper_state()
    await sovereign_service.initialize()
    
    # Check slots for FARTCOIN or empty genesis
    fartcoin_slot = None
    for slot in sovereign_service.slots_cache:
        if slot.get("symbol") and "FARTCOIN" in slot.get("symbol"):
            fartcoin_slot = slot
            break

    fartcoin_pos = next((p for p in bybit_rest_service.paper_positions if p.get("symbol") and "FARTCOIN" in p.get("symbol")), None)
    
    if fartcoin_pos and fartcoin_slot:
        print(f"✅ REAL FARTCOIN FOUND IN PAPER MODE: {fartcoin_pos.get('symbol')}")
        order_id = fartcoin_pos.get("order_id")
        if not order_id:
            order_id = f"PAPER-FART-{int(time.time())}"
        genesis_id = f"SWG-{order_id}-FART"
        
        fartcoin_pos["order_id"] = order_id
        fartcoin_pos["genesis_id"] = genesis_id
        await bybit_rest_service._save_paper_state()
        
        await sovereign_service.update_slot(fartcoin_slot["id"], {
            "order_id": order_id,
            "genesis_id": genesis_id
        })
        print(f"✅ Slot {fartcoin_slot['id']} updated with Genesis ID: {genesis_id}")
    elif fartcoin_slot:
        print("👻 GHOST FARTCOIN. Clearing slot...")
        # Limpar o slot na força bruta se for fantasma
        await sovereign_service.update_slot(fartcoin_slot["id"], {
            "symbol": None,
            "status_risco": "LIVRE",
            "pnl_percent": 0,
            "pnl_usd": 0,
            "entry_price": 0,
            "current_stop": 0,
            "target_price": 0,
            "qty": 0,
            "side": None,
            "order_id": None,
            "genesis_id": None,
            "pensamento": "🔄 GHOST_PURGE MANUAL"
        })
        print(f"✅ Slot {fartcoin_slot['id']} cleared.")
    else:
        print("FARTCOIN not found in slots.")
        
    print("🧹 Cleaning vault history...")
    async with database_service.AsyncSessionLocal() as session:
        # Pega todos os registros de Recovery (nossos testes ou ghosts de falha de fechamento antigo)
        result = await session.execute(text("DELETE FROM trade_history WHERE genesis_id LIKE 'RECOVERY-%' OR (pnl = 0 AND reasoning_report IS NULL)"))
        await session.commit()
        print(f"✅ {result.rowcount} ghost trades deleted from history.")

if __name__ == "__main__":
    asyncio.run(main())
