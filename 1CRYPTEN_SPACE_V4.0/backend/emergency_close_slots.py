"""
Emergency Close All Active Positions + Limpar Slots Firebase
Almirante use: python emergency_close_slots.py
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.bybit_rest import bybit_rest_service
from services.sovereign_service import sovereign_service
from config import settings

async def emergency_close():
    print(f"\n[EMERGENCY CLOSE] - Modo: {settings.BYBIT_EXECUTION_MODE}")
    print("=" * 50)
    
    await sovereign_service.initialize()
    await bybit_rest_service.initialize()

    # 1. Busca posicoes abertas na Bybit (Real ou Paper)
    try:
        positions = await bybit_rest_service.get_active_positions()
        print(f"\n[INFO] Posicoes encontradas na Bybit: {len(positions)}")
        
        if not positions:
            print("[OK] Nenhuma posicao aberta na corretora.")
        
        for pos in positions:
            sym = pos.get("symbol", "")
            side = pos.get("side", "")
            size = float(pos.get("size", 0) or 0)
            pnl = float(pos.get("unrealisedPnl", 0) or 0)
            
            if size <= 0:
                continue
                
            print(f"\n[CLOSE] {sym} | {side} | Size: {size} | PnL: ${pnl:.2f}")
            
            close_side = "Sell" if side == "Buy" else "Buy"
            
            try:
                result = bybit_rest_service.session.place_order(
                    category="linear",
                    symbol=sym.replace(".P", ""),
                    side=close_side,
                    orderType="Market",
                    qty=str(size),
                    reduceOnly=True,
                    timeInForce="IOC"
                )
                ret_code = result.get("retCode", -1)
                if ret_code == 0:
                    print(f"   [OK] {sym} fechado com sucesso!")
                else:
                    print(f"   [ERRO] {sym}: {result.get('retMsg', 'unknown')}")
            except Exception as e:
                print(f"   [EXCECAO] {sym}: {e}")
    
    except Exception as e:
        print(f"[ERRO] ao buscar posicoes: {e}")

    # 2. Limpa todos os slots no Firebase
    print("\n[FIREBASE] Limpando slots...")
    empty_slot = {
        "symbol": None, "entry_price": 0, "current_stop": 0,
        "entry_margin": 0, "status_risco": "IDLE", "side": None,
        "pnl_percent": 0, "target_price": 0, "qty": 0,
        "slot_type": None, "pattern": None, "pensamento": "",
        "opened_at": None, "fleet_intel": None
    }
    for i in range(1, 5):
        try:
            await sovereign_service.update_slot(i, empty_slot)
            print(f"   [OK] Slot {i} -> IDLE")
        except Exception as e:
            print(f"   [ERRO] Slot {i}: {e}")

    print("\n[DONE] Expurgo de emergencia finalizado!")
    print("   Slots livres para Shadow Strikes ou quando o BTC acordar.")

if __name__ == "__main__":
    asyncio.run(emergency_close())
