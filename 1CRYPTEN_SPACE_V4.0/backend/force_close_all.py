import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.bybit_rest import bybit_rest_service
from services.sovereign_service import sovereign_service
from config import settings

async def kill_all_positions():
    print(f"Iniciando Expurgo de Posições na Bybit... Modo: {settings.BYBIT_EXECUTION_MODE}")
    await sovereign_service.initialize()
    
    try:
        if settings.BYBIT_EXECUTION_MODE == "PAPER":
            positions = bybit_rest_service.paper_positions
            print(f"Posições em memória (Paper): {len(positions)}")
            for pos in positions.copy():
                sym = pos["symbol"]
                side = pos["side"]
                size = float(pos["size"])
                print(f"Fechando paper: {sym} {side} {size}")
                await bybit_rest_service.close_position(sym, side, size, reason="FORCE_RESET")
        else:
            # Busca da corretora Real/Testnet
            positions = await bybit_rest_service.get_open_positions()
            print(f"Posições reais na Bybit: {len(positions)}")
            for pos in positions:
                sym = pos["symbol"]
                side = pos["side"]
                size = float(pos["size"])
                print(f"Fechando real: {sym} {side} {size}")
                await bybit_rest_service.close_position(sym, side, size, reason="FORCE_RESET")
                
    except Exception as e:
        print(f"Erro ao fechar posições: {e}")

    print("Limpando slots no Firebase...")
    empty_slot = {
        "symbol": None, "entry_price": 0, "current_stop": 0, "entry_margin": 0,
        "status_risco": "IDLE", "side": None, "pnl_percent": 0, "target_price": 0,
        "qty": 0, "slot_type": None, "pattern": None, "pensamento": ""
    }
    for i in range(1, 5):
        try:
            await sovereign_service.update_slot(i, empty_slot)
            print(f"Slot {i} resetado para IDLE.")
        except Exception as e:
            print(f"Erro ao resetar slot {i}: {e}")

    print("Expurgo finalizado!")

if __name__ == "__main__":
    asyncio.run(kill_all_positions())
