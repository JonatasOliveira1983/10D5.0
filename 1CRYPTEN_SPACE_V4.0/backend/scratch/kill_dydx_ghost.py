import asyncio
import os
import sys

# Adicionar o path do projeto para importar os serviços
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

from services.firebase_service import firebase_service

async def kill_dydx_ghost():
    print("[GHOST-BUSTER] Exterminador de Fantasmas V1.0 - Iniciando...")
    await firebase_service.initialize()
    
    # 1. Buscar no Firestore
    print("Busca cirúrgica na coleção 'moonbags'...")
    moonbags = await firebase_service.get_moonbags()
    
    dydx_ghosts = [m for m in moonbags if "DYDX" in m.get("symbol", "").upper()]
    
    if not dydx_ghosts:
        print("✅ Nenhum fantasma de DYDX encontrado no Firestore.")
    else:
        for ghost in dydx_ghosts:
            gid = ghost.get("id")
            gsym = ghost.get("symbol")
            print(f"DELETANDO: {gsym} (ID: {gid}). Removendo...")
            await firebase_service.remove_moonbag(gid, reason="PURGE_V110.128.1")
            print(f"OK: Fantasma {gid} purgado com sucesso.")

    print("\nOPERACAO CONCLUIDA. Radar operando em modo limpo.")

if __name__ == "__main__":
    asyncio.run(kill_dydx_ghost())
