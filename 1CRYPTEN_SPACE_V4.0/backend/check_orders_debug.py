import asyncio
import os
import sys
from pybit.unified_trading import HTTP
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import settings

async def main():
    try:
        with open("bybit_orders_report.txt", "w", encoding="utf-8") as f:
            f.write("Buscando ultimas ordens fechadas na Bybit (Mainnet)...\n")
            session = HTTP(
                testnet=settings.BYBIT_TESTNET,
                api_key=settings.BYBIT_API_KEY,
                api_secret=settings.BYBIT_API_SECRET,
            )

            f.write("\n--- ÚLTIMAS 5 POSIÇÕES FECHADAS (CLOSED PNL) ---\n")
            pnl_response = session.get_closed_pnl(category="linear", limit=5)
            if pnl_response and pnl_response.get("retCode") == 0:
                pnl_list = pnl_response.get("result", {}).get("list", [])
                for p in pnl_list:
                    f.write(f"Symbol: {p.get('symbol')} | Side: {p.get('side')} | Qty: {p.get('qty')} | PnL: {p.get('closedPnl')} | ExecType: {p.get('execType')}\n")
                    f.write(f"  Entrada: {p.get('avgEntryPrice')} | Saida: {p.get('avgExitPrice')} | Criação: {p.get('createdTime')}\n")
            else:
                f.write(f"Erro ou vazio em Closed PnL: {pnl_response}\n")

            f.write("\n--- ÚLTIMAS 10 ORDENS (ORDER HISTORY) ---\n")
            orders_response = session.get_order_history(category="linear", limit=10)
            if orders_response and orders_response.get("retCode") == 0:
                order_list = orders_response.get("result", {}).get("list", [])
                for o in order_list:
                    f.write(f"Symbol: {o.get('symbol')} | Side: {o.get('side')} ({o.get('orderType')}) | Status: {o.get('orderStatus')} | Preço: {o.get('price')} | Qty: {o.get('qty')}\n")
                    f.write(f"  Motivo Cancel/Stop: {o.get('cancelType')} / {o.get('stopOrderType')} / {o.get('rejectReason')}\n")
                    f.write(f"  Criado/Atualizado: {o.get('createdTime')} / {o.get('updatedTime')}\n")
                    f.write("---\n")
            else:
                f.write(f"Erro ou vazio em Order History: {orders_response}\n")

    except Exception as e:
        print("Erro Exception:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
