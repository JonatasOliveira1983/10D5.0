import asyncio
import json
import sys
import os

# Adiciona o diretório atual ao path para importar os serviços
sys.path.append(os.getcwd())

from services.sovereign_service import sovereign_service

async def analyze_virtual_trades():
    await sovereign_service.initialize()
    # Pega os últimos 200 trades para garantir que encontramos os de VIRTUALUSDT
    trades = await sovereign_service.get_trade_history(limit=200)
    
    virtual_trades = [t for t in trades if 'VIRTUAL' in str(t.get('symbol', ''))]
    
    # Ordenar por timestamp (mais recente primeiro)
    virtual_trades.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    print(json.dumps(virtual_trades, indent=2))

if __name__ == "__main__":
    asyncio.run(analyze_virtual_trades())
