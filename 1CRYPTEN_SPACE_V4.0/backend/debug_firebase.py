import asyncio
import os
import sys

# Adicionar o diretório base ao sys.path para importar serviços
sys.path.append(os.getcwd())

async def debug():
    from services.sovereign_service import sovereign_service
    await sovereign_service.initialize()
    print(f"Active: {sovereign_service.is_active}")
    
    colls = sovereign_service.db.collections()
    coll_names = [c.id for c in colls]
    print(f"Collections: {coll_names}")
    
    for cn in coll_names[:5]: # Check first 5
        docs = sovereign_service.db.collection(cn).limit(1).stream()
        found = False
        for d in docs:
            print(f"Collection '{cn}' has at least one document.")
            found = True
            break
        if not found:
            print(f"Collection '{cn}' is empty.")

if __name__ == "__main__":
    asyncio.run(debug())
