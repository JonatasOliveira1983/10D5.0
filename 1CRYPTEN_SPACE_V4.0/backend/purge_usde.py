import asyncio
from services.firebase_service import firebase_service
import os
import sys
import json

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

async def purge_usde():
    await firebase_service.initialize()
    
    # 1. Limpa o Slot 2 no Firestore/RTDB
    print("[PURGE] Removendo USDEUSDT do Slot 2...")
    await firebase_service.free_slot(2, reason="REMOVIDO: Ativo Sem Volatilidade (Stablecoin)")
    
    # 2. Atualiza o paper_storage.json
    paper_path = os.path.join(backend_dir, "paper_storage.json")
    if os.path.exists(paper_path):
        with open(paper_path, 'r') as f:
            data = json.load(f)
        
        original_count = len(data.get("positions", []))
        data["positions"] = [p for p in data.get("positions", []) if p["symbol"] != "USDEUSDT"]
        new_count = len(data["positions"])
        
        with open(paper_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"FILE paper_storage.json atualizado: {original_count} -> {new_count} posicoes.")
        
        # 3. Sincroniza com Firestore paper_state
        await firebase_service.update_paper_state(data)

    print("OK USDEUSDT purgado com sucesso.")

if __name__ == "__main__":
    asyncio.run(purge_usde())
