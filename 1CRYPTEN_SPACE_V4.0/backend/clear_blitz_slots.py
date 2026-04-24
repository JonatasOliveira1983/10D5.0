import asyncio
from services.sovereign_service import sovereign_service
import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

async def clear_slots():
    await sovereign_service.initialize()
    
    # Limpando Slot 1 e Slot 2 (Blitz)
    print("[CLEANUP] Limpando slots 1 e 2 para novos testes...")
    await sovereign_service.free_slot(1, reason="Limpeza para Teste Mola")
    await sovereign_service.free_slot(2, reason="Limpeza para Teste Mola")
    
    # Tambem limpa do paper_storage.json para evitar que o Ghostbuster tente recuperar
    paper_path = os.path.join(backend_dir, "paper_storage.json")
    if os.path.exists(paper_path):
        import json
        with open(paper_path, 'r') as f:
            data = json.load(f)
        
        # Filtra para manter apenas posicoes que nao sejam dos slots 1 e 2
        # (Neste caso, vamos manter METUSDT que esta no slot 3)
        original_count = len(data.get("positions", []))
        data["positions"] = [p for p in data.get("positions", []) if p["symbol"] not in ["GMTUSDT", "USDEUSDT"]]
        new_count = len(data["positions"])
        
        with open(paper_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"FILE paper_storage.json atualizado: {original_count} -> {new_count} posicoes.")
        
        # Sincroniza com Firestore paper_state
        await sovereign_service.update_paper_state(data)

    print("OK Slots 1 e 2 limpos com sucesso.")

if __name__ == "__main__":
    asyncio.run(clear_slots())
