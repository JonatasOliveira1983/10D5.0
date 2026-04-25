import asyncio
import os
import sys
import time

# Adicionar o diretório atual ao path
sys.path.append(os.getcwd())

from services.database_service import database_service

async def inject_trades():
    print("Iniciando injecao de recuperacao de trades...")
    
    # 1. Definir os trades do usuário
    trades = [
        {
            "id": 1,
            "symbol": "WLFIUSDT",
            "side": "Buy",
            "entry_price": 0.075410,
            "current_stop": 0.072771,
            "initial_stop": 0.072771,
            "target_price": 0.077672,
            "leverage": 50,
            "qty": 6676.8, # (10.07 * 50) / 0.075410
            "genesis_id": "BLZ-PAPER-WLFIUSDT-123-WLFI",
            "slot_type": "BLITZ_30M",
            "status_risco": "NORMAL",
            "opened_at": time.time() - 3600
        },
        {
            "id": 2,
            "symbol": "ENAUSDT",
            "side": "Buy",
            "entry_price": 0.108250,
            "current_stop": 0.107167,
            "initial_stop": 0.107167,
            "target_price": 0.111497,
            "leverage": 10,
            "qty": 930.25, # (10.07 * 10) / 0.108250
            "genesis_id": "BLZ-PAPER-ENAUSDT-123-ENAU",
            "slot_type": "BLITZ_30M",
            "status_risco": "NORMAL",
            "opened_at": time.time() - 1800
        },
        {
            "id": 3,
            "symbol": "STRKUSDT",
            "side": "Sell",
            "entry_price": 0.040570,
            "current_stop": 0.041438,
            "initial_stop": 0.041438,
            "target_price": 0.039353,
            "leverage": 10,
            "qty": 2482.1, # (10.07 * 10) / 0.040570
            "genesis_id": "SWG-PAPER-STRKUSDT-123-STRK",
            "slot_type": "SWING",
            "status_risco": "NORMAL",
            "opened_at": time.time() - 7200
        },
        {
            "id": 4,
            "symbol": "XPLUSDT",
            "side": "Sell",
            "entry_price": 0.098810,
            "current_stop": 0.100480,
            "initial_stop": 0.100480,
            "target_price": 0.095846,
            "leverage": 10,
            "qty": 1019.1, # (10.07 * 10) / 0.098810
            "genesis_id": "SWG-PAPER-XPLUSDT-123-XPLU",
            "slot_type": "SWING",
            "status_risco": "NORMAL",
            "opened_at": time.time() - 5400
        }
    ]

    # 2. Injetar na tabela slots
    for t in trades:
        print(f"Injecting {t['symbol']} into Slot {t['id']}...")
        await database_service.update_slot(t['id'], t)

    # 3. Injetar no estado do motor Paper (BybitREST persistence)
    paper_positions = []
    for t in trades:
        paper_positions.append({
            "symbol": t["symbol"],
            "side": t["side"],
            "size": str(t["qty"]),
            "avgPrice": str(t["entry_price"]),
            "leverage": str(t["leverage"]),
            "stopLoss": str(t["current_stop"]),
            "takeProfit": str(t["target_price"]),
            "opened_at": t["opened_at"],
            "genesis_id": t["genesis_id"],
            "is_paper": True
        })
    
    paper_state = {
        "positions": paper_positions,
        "moonbags": [],
        "balance": 100.73, # Do print do usuário
        "history": []
    }
    
    await database_service.update_system_state("paper_engine_state", paper_state)
    print("Injecao concluida com sucesso!")

if __name__ == "__main__":
    asyncio.run(inject_trades())
