import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sovereign_service import sovereign_service

async def reset_all():
    print("Conectando ao Firebase...")
    await sovereign_service.initialize()
    await sovereign_service.initialize_db()

    print("Limpando 4 slots...")
    for i in range(1, 5):
        try:
            await sovereign_service.update_slot(i, {
                "symbol": None, "entry_price": 0, "current_stop": 0, "entry_margin": 0,
                "status_risco": "LIVRE", "side": None, "pnl_percent": 0
            })
            print(f"Slot {i} resetado.")
        except Exception as e:
            print(f"Erro slot {i}: {e}")

    print("Resetando banca para $100...")
    try:
        await sovereign_service.update_banca_status({
            "saldo_total": 100.0,
            "configured_balance": 100.0,
            "lucro_total_acumulado": 0.0,
            "saldo_real_bybit": 0.0
        })
        print("Banca configurada para $100.")
    except Exception as e:
        print(f"Erro ao setar banca: {e}")

    print("Todas as operações de limpeza concluídas.")

if __name__ == "__main__":
    asyncio.run(reset_all())
