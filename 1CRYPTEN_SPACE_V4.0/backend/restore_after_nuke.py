import asyncio
import json
import os
import time
import sys

# Ajusta o path para importar os serviços
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from services.bybit_rest import bybit_rest_service
from services.firebase_service import firebase_service

async def restore():
    print("[RECOVERY] Restaurando slots apos Factory Reset acidental...")
    await firebase_service.initialize()
    
    # Forçamos o reset da flag no settings antes de inicializar o BybitREST
    from config import settings
    settings.FACTORY_RESET_V110 = False
    
    await bybit_rest_service.initialize()
    
    # Ativos identificados antes do nuke
    # Slot 1: GMTUSDT (Buy)
    # Slot 2: USDEUSDT (Sell)
    # Slot 3: METUSDT (Sell)
    
    symbols = ["GMTUSDT", "USDEUSDT", "METUSDT"]
    sides = {"GMTUSDT": "Buy", "USDEUSDT": "Sell", "METUSDT": "Sell"}
    
    positions = []
    for sym in symbols:
        try:
            ticker = await asyncio.to_thread(bybit_rest_service.session.get_tickers, category="linear", symbol=sym)
            price = float(ticker['result']['list'][0]['lastPrice'])
            
            # Simula uma margem de $10 a 50x
            margin = 10.0
            leverage = 50.0
            qty = (margin * leverage) / price
            
            # Arredonda qty conforme a precisão do ativo (usando o próprio bybit_rest)
            qty = await bybit_rest_service.round_qty(sym, qty)
            
            positions.append({
                "symbol": sym,
                "side": sides[sym],
                "size": str(qty),
                "avgPrice": str(price),
                "leverage": str(int(leverage)),
                "stopLoss": "0",
                "takeProfit": "0",
                "opened_at": time.time(),
                "is_paper": True,
                "entry_margin": margin,
                "status": "RECOVERED"
            })
            print(f"OK Preparado: {sym} {sides[sym]} @ {price}")
        except Exception as e:
            print(f"ERR Erro ao buscar {sym}: {e}")
    
    data = {
        "positions": positions,
        "moonbags": [],
        "balance": 100.0,
        "history": []
    }
    
    # 1. Salva localmente
    paper_path = os.path.join(backend_dir, "paper_storage.json")
    with open(paper_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"FILE Local paper_storage.json criado com {len(positions)} posicoes.")
    
    # 2. Sincroniza com Firestore
    await firebase_service.update_paper_state(data)
    print("CLOUD Firestore paper_state sincronizado.")
    
    # 3. Força o RTDB a manter os slots (opcional, mas bom para UI)
    for i, pos in enumerate(positions, 1):
        slot_data = {
            "id": i,
            "symbol": pos["symbol"],
            "side": pos["side"],
            "entry_price": float(pos["avgPrice"]),
            "qty": float(pos["size"]),
            "leverage": 50,
            "status_risco": "ATIVO",
            "opened_at": pos["opened_at"],
            "entry_margin": pos["entry_margin"]
        }
        await firebase_service.update_slot(i, slot_data)
        print(f"SYNC Slot {i} ({pos['symbol']}) atualizado no Firebase/RTDB.")

    print("\nOK RESTAURACAO CONCLUIDA. O Ghostbuster nao deve mais remover estas ordens.")

if __name__ == "__main__":
    asyncio.run(restore())
