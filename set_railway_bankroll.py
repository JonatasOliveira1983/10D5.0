# 1CRYPTEN_SPACE_V4.0 - V110.175 Capital Injection Script
import asyncio
import os
import sys

# Adicionar o caminho do backend para os imports funcionarem
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

from services.database_service import database_service

async def inject_capital(amount: float):
    print(f"💰 Injecting ${amount:.2f} into Railway Postgres...")
    
    # Inicializa o banco de dados
    await database_service.initialize()
    
    # Prepara os dados da banca
    banca_data = {
        "saldo_total": amount,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4,
        "status": "OPERATIONAL"
    }
    
    # Atualiza no Postgres
    await database_service.update_banca_status(banca_data)
    
    # Verifica o resultado
    check = await database_service.get_banca_status()
    print(f"✅ Balance Updated! Current Balance: ${check.get('saldo_total'):.2f}")

if __name__ == "__main__":
    # Valor desejado: $100.00
    asyncio.run(inject_capital(100.0))
