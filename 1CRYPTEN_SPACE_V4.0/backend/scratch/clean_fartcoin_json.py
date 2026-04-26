import json
import os

paper_file = os.path.join(os.path.dirname(__file__), "..", "services", "paper_positions.v110.json")
try:
    if os.path.exists(paper_file):
        with open(paper_file, "r") as f:
            data = json.load(f)
            
        pos = data.get("positions", [])
        moon = data.get("moonbags", [])
        
        new_pos = [p for p in pos if "FARTCOIN" not in p.get("symbol", "")]
        new_moon = [p for p in moon if "FARTCOIN" not in p.get("symbol", "")]
        
        data["positions"] = new_pos
        data["moonbags"] = new_moon
        
        with open(paper_file, "w") as f:
            json.dump(data, f, indent=4)
        print("FARTCOIN removido do JSON.")
except Exception as e:
    print(f"Erro JSON: {e}")
