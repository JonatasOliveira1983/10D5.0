
import asyncio
import os
import sys
import time

# Forçar encoding para evitar erros de emojis no console Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adicionar o path do backend corretamente
current_file_path = os.path.abspath(__file__)
backend_dir = os.path.dirname(os.path.dirname(current_file_path))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.database_service import database_service, Base
from services.sovereign_service import sovereign_service

async def nuclear_reset():
    print("[NUCLEAR-RESET] Iniciando reset total para teste de 50x...")
    
    # 1. Inicializar serviços
    await database_service.initialize()
    
    # 2. Recriar Schema (Drop e Create) para limpar tudo e corrigir colunas faltantes
    print("Resetando schema do banco de dados (Drop & Create)...")
    async with database_service.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # 3. Resetar Banca para $100
    print("Inicializando banca com $100.00...")
    banca_data = {
        "saldo_total": 100.0,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4,
        "status": "READY_FOR_50X_TEST"
    }
    await database_service.update_banca_status(banca_data)
    
    # 4. Inicializar Slots Vazios
    print("Inicializando slots vazios...")
    for i in range(1, 5):
        slot_data = {
            "id": i,
            "status_risco": "LIVRE",
            "slot_type": "BLITZ_30M" if i <= 2 else "SWING",
            "leverage": 50.0,
            "pensamento": "Resetado para teste de alavancagem 50x fixa.",
            "timestamp_last_update": time.time()
        }
        await database_service.update_slot(i, slot_data)
    
    print("\n[SUCCESS] Reset concluído com sucesso!")
    print("Nota: Este reset foi aplicado ao banco de dados identificado pelo sistema.")
    if os.getenv("DATABASE_URL"):
        print(f"Database: {os.getenv('DATABASE_URL')}")
    else:
        print("Database: Local SQLite (local_sniper.db)")

if __name__ == "__main__":
    asyncio.run(nuclear_reset())
