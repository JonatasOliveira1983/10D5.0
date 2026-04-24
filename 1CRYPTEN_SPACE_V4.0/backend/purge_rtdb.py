import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sovereign_service import sovereign_service

async def purge_rtdb():
    print("INICIANDO EXPURGO RTDB (V80.9)...")
    await sovereign_service.initialize()
    
    # Paths to clear in RTDB
    paths = [
        'history',
        'logs',
        'system/bankroll',
        'system/pnl_history',
        'orders/closed'
    ]
    
    for path in paths:
        try:
            print(f"Limpando path RTDB: {path}")
            # Correct attribute is .rtdb
            await asyncio.to_thread(sovereign_service.rtdb.child(path).delete)
            print(f"OK: Path {path} limpo.")
        except Exception as e:
            print(f"Erro ao limpar {path}: {e}")

    # Set Initial Bankroll in RTDB
    initial_bankroll = {
        "total_balance": 100.0,
        "available_balance": 100.0,
        "accumulated_pnl": 0.0,
        "trade_count": 0,
        "last_update": 0
    }
    await asyncio.to_thread(sovereign_service.rtdb.child('system/bankroll').set, initial_bankroll)
    print("OK: Banca RTDB resetada para $100.00")

if __name__ == "__main__":
    asyncio.run(purge_rtdb())
