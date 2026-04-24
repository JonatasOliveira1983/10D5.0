
import asyncio
import os
import sys

# Adiciona o diretório atual ao path para importar os serviços
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

async def report():
    from services.sovereign_service import sovereign_service
    from services.bybit_rest import bybit_rest_service
    from services.execution_protocol import execution_protocol
    
    print("Iniciando Diagnóstico de VIP...")
    await sovereign_service.initialize()
    await sovereign_service.initialize_db()
    await bybit_rest_service.initialize()
    
    slots = await sovereign_service.get_active_slots()
    tickers = await asyncio.to_thread(bybit_rest_service.session.get_tickers, category="linear")
    price_map = {t["symbol"]: float(t.get("lastPrice", 0)) for t in tickers.get("result", {}).get("list", [])}
    
    print("\n--- STATUS DAS POSIÇÕES ATUAIS ---")
    active_count = 0
    for s in slots:
        symbol = s.get("symbol")
        if symbol:
            active_count += 1
            entry = float(s.get("entry_price", 0))
            side = s.get("side", "Buy")
            current = price_map.get(bybit_rest_service._strip_p(symbol), 0)
            roi = execution_protocol.calculate_roi(entry, current, side) if current > 0 and entry > 0 else 0
            sl = float(s.get("current_stop", 0))
            tp = float(s.get("target_price", 0))
            phase = execution_protocol.get_sl_phase(roi)
            
            print(f"Slot {s['id']}: {symbol} ({side})")
            print(f"  Entrada: ${entry:.6f} | Atual: ${current:.6f}")
            print(f"  ROI: {roi:+.2f}% | Fase: {phase}")
            print(f"  Stop: ${sl:.6f} | Target: ${tp:.6f}")
            print("-" * 30)
            
    balance = await bybit_rest_service.get_wallet_balance()
    print(f"\nEquity Atual na Bybit: ${balance:.2f}")
    print(f"Total de Slots Ocupados: {active_count}/4")

if __name__ == "__main__":
    asyncio.run(report())
