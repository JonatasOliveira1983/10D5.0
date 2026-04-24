# -*- coding: utf-8 -*-
# 1CRYPTEN_SPACE_V4.0 - Nuclear Schema Reset Script
# Use este script para aplicar mudanças de schema no Postgres (Railway)
import asyncio
import os
import sys

# Adicionar o path do backend para importar os serviços
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

from services.database_service import database_service, Base, Slot, BancaStatus

async def nuclear_reset():
    print("🚀 [NUCLEAR-RESET] Iniciando reset de schema para V110.196...")
    
    # 1. Obter engine
    engine = database_service.engine
    
    async with engine.begin() as conn:
        print("💥 [DROP] Removendo tabelas antigas (slots, banca_status)...")
        # Drop tables selectively to avoid losing trade history unless necessary
        # Mas para garantir paridade total no cockpit, vamos dar drop em slots e banca
        await conn.run_sync(Base.metadata.drop_all, tables=[Slot.__table__, BancaStatus.__table__])
        
        print("🏗️ [CREATE] Criando novas tabelas com schema atualizado...")
        await conn.run_sync(Base.metadata.create_all, tables=[Slot.__table__, BancaStatus.__table__])
        
    print("✅ [SUCCESS] Schema V110.196 aplicado com sucesso!")
    print("💡 Os slots agora suportam: entry_margin, initial_stop, fleet_intel, etc.")

if __name__ == "__main__":
    asyncio.run(nuclear_reset())
