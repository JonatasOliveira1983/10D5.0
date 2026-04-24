import asyncio
import os
import sys

# Adiciona o diretório atual ao sys.path para importar os serviços
sys.path.append(os.getcwd())

from services.sovereign_service import sovereign_service
from services.bybit_rest import bybit_rest_service

async def clear_all():
    print("🧹 Iniciando limpeza profunda de slots...")
    
    # 1. Obter todos os slots ativos
    slots = await sovereign_service.get_active_slots(force_refresh=True)
    
    for slot in slots:
        slot_id = slot.get("id")
        symbol = slot.get("symbol")
        if symbol:
            print(f"📦 Limpando Slot {slot_id}: {symbol}")
            await sovereign_service.hard_reset_slot(slot_id, reason="USER_REQUEST_DEEP_CLEAN")
            print(f"✅ Slot {slot_id} resetado com sucesso.")
        else:
            print(f"⚪ Slot {slot_id} já está livre.")

    print("\n🚀 Limpeza concluída. Sistema pronto para novos sinais Shadow!")

if __name__ == "__main__":
    asyncio.run(clear_all())
