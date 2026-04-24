import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
paper_path = os.path.join(base_dir, "paper_storage.json")

try:
    with open(paper_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    moonbags = data.get("moonbags", [])
    seen = set()
    cleaned = []
    
    for mb in moonbags:
        sym = mb.get("symbol")
        if sym not in seen:
            seen.add(sym)
            cleaned.append(mb)
            
    data["moonbags"] = cleaned
    
    with open(paper_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    print(f"Limpou paper_storage.json: de {len(moonbags)} para {len(cleaned)} moonbags.")
except Exception as e:
    print(f"Erro: {e}")
