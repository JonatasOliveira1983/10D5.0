
import asyncio
import os
import sys
import time

# Forçar encoding UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adicionar o path do backend corretamente
current_file_path = os.path.abspath(__file__)
backend_dir = os.path.dirname(os.path.dirname(current_file_path))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.database_service import database_service, Base

async def nuclear_production_reset():
    # URL de Produção fornecida pelo usuário
    prod_url = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"
    
    print(f"[PRODUCTION-RESET] Conectando ao banco de produção Railway...")
    
    # Sobrescrever a engine do database_service para apontar para produção
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    engine = create_async_engine(prod_url, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        # 1. Resetar Schema (Drop e Create)
        print("Resetando schema de produção (Drop & Create)...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        
        # 2. Resetar Banca para $100
        print("Inicializando banca de produção com $100.00...")
        from services.database_service import BancaStatus, Slot
        
        async with AsyncSessionLocal() as session:
            # Inicializa Banca
            banca = BancaStatus(id=1, saldo_total=100.0, risco_real_percent=0.0, slots_disponiveis=4, status="READY_FOR_50X_TEST")
            session.add(banca)
            
            # Inicializa Slots
            print("Inicializando slots 50x...")
            for i in range(1, 5):
                slot = Slot(
                    id=i,
                    status_risco="LIVRE",
                    slot_type="BLITZ_30M" if i <= 2 else "SWING",
                    leverage=50.0,
                    pensamento="Resetado para teste de alavancagem 50x fixa.",
                    timestamp_last_update=time.time()
                )
                session.add(slot)
            
            await session.commit()
            
        print("\n[SUCCESS] RESET DE PRODUÇÃO CONCLUÍDO COM SUCESSO!")
        print("Banca: $100.00")
        print("Alavancagem: 50x fixa configurada nos slots.")
        
    except Exception as e:
        print(f"\n[ERROR] Falha no reset de produção: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(nuclear_production_reset())
