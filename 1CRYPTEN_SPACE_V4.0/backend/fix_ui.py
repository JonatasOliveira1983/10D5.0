import asyncio, os, sys, datetime
sys.path.append(os.getcwd())
from services.sovereign_service import sovereign_service

async def fix_ui():
    await sovereign_service.initialize()
    
    # 1. Update Slot 3 to show PEPE
    pepe_slot = {
        "symbol": "1000PEPEUSDT",
        "entry_price": 0.003378,
        "side": "Sell",
        "opened_at": 1772856179.1495922,
        "status_risco": "ATIVO",
        "sl_phase": "SAFE",
        "pnl_percent": 208.7,
        "entry_margin": 10.0,
        "leverage": 50,
        "slot_type": "SWING",
        "timestamp_last_update": datetime.datetime.now(datetime.timezone.utc).timestamp()
    }
    await sovereign_service.update_slot(3, pepe_slot)
    print("Slot 3 updated with PEPE")
    
    # 2. Add a closed trade to trade_history so Vault shows up
    dummy_trade = {
        "symbol": "BTCUSDT",
        "side": "Buy",
        "entry_price": 60000.0,
        "exit_price": 65000.0,
        "pnl_usd": 15.50,
        "pnl_pct": 8.3,
        "is_win": True,
        "close_reason": "Take Profit Hit",
        "slot_type": "SCALP",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    await sovereign_service.log_trade(dummy_trade)
    print("Dummy trade added to history")

asyncio.run(fix_ui())
