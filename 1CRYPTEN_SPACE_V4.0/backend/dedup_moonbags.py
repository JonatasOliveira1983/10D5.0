import asyncio
import os
import sys

# Garante que acha as dependências
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

from config import settings
from services.firebase_service import firebase_service

async def main():
    await firebase_service.initialize()
    print("🧹 Iniciando limpeza de Moonbags duplicadas...")
    
    # Busca todas as moonbags
    moonbags = await firebase_service.get_moonbags(limit=100)
    seen_symbols = set()
    to_delete = []
    
    # Ordena por promovido_at (para manter o mais antigo ou mais recente)
    moonbags.sort(key=lambda x: x.get("promoted_at", 0), reverse=True)
    
    for mb in moonbags:
        symbol = mb.get("symbol")
        uid = mb.get("id")
        
        if symbol in seen_symbols:
            to_delete.append((uid, symbol))
        else:
            seen_symbols.add(symbol)
            
    print(f"🗑️ Encontradas {len(to_delete)} duplicatas para remover.")
    
    for uid, sym in to_delete:
        print(f"Removendo cópia de {sym} (ID: {uid})...")
        await firebase_service.remove_moonbag(uid, reason="Deduplication")
        
    print("✅ Limpeza concluída!")

if __name__ == "__main__":
    asyncio.run(main())
