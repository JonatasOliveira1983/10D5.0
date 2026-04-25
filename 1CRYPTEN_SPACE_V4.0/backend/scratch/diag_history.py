import asyncio
import sys
import os

# Adiciona o diretório atual ao path para importar os serviços
sys.path.append(os.getcwd())

from services.database_service import database_service

async def main():
    try:
        await database_service.initialize()
        print("--- ÚLTIMOS 10 TRADES NO HISTÓRICO ---")
        trades = await database_service.get_trade_history(limit=10)
        if not trades:
            print("Nenhum trade encontrado no histórico.")
        for t in trades:
            print(f"[{t.get('timestamp')}] {t.get('symbol')} | Motivo: {t.get('close_reason')} | PnL: {t.get('pnl_percent')}% | Genesis: {t.get('genesis_id')}")
        
        print("\n--- SLOTS ATIVOS NO BANCO ---")
        slots = await database_service.get_active_slots()
        for s in slots:
            print(f"Slot {s['id']}: {s.get('symbol') or 'LIVRE'} | {s.get('status_risco')} | {s.get('pnl_percent')}%")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())
