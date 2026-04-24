import asyncio
from services.sovereign_service import sovereign_service
import os
import sys
import json

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

async def purge_btc():
    await sovereign_service.initialize()
    
    # 1. Encontrar em qual slot o BTCUSDT esta e limpar
    slots = await sovereign_service.get_active_slots(force_refresh=True)
    slot_id_to_clear = None
    for s in slots:
        if s.get("symbol") == "BTCUSDT":
            slot_id_to_clear = s.get("id")
            break
            
    if slot_id_to_clear:
        print(f"[PURGE] Removendo BTCUSDT do Slot {slot_id_to_clear}...")
        await sovereign_service.free_slot(slot_id_to_clear, reason="REMOVIDO: Blue Chip Blocklist V110.168")
    else:
        print("[PURGE] BTCUSDT nao encontrado em nenhum slot do RTDB.")
    
    # 2. Atualiza o paper_storage.json
    paper_path = os.path.join(backend_dir, "paper_storage.json")
    if os.path.exists(paper_path):
        with open(paper_path, 'r') as f:
            data = json.load(f)
        
        original_count = len(data.get("positions", []))
        data["positions"] = [p for p in data.get("positions", []) if p["symbol"] != "BTCUSDT"]
        new_count = len(data["positions"])
        
        with open(paper_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"FILE paper_storage.json atualizado: {original_count} -> {new_count} posicoes.")
        
        # 3. Sincroniza com Firestore paper_state
        await sovereign_service.update_paper_state(data)

    print("OK BTCUSDT purgado com sucesso.")

if __name__ == "__main__":
    asyncio.run(purge_btc())
