import json
import os

pepe_pos = {
  "symbol": "1000PEPEUSDT",
  "side": "Sell",
  "size": 148000,
  "avgPrice": 0.003378,
  "leverage": 50,
  "entryMargin": 10.0,
  "openedAt": 1772856179.1495922,
  "stopLoss": 0.00344556,
  "takeProfit": 0.00327666,
  "status_risco": "ATIVO",
  "slot_type": "SWING",
  "pnl_percent": 0.0
}

data = {"positions": [pepe_pos], "balance": 100.0, "history": []}

try:
    with open('paper_storage.json', 'r') as f:
        existing = json.load(f)
        if isinstance(existing.get("positions"), list):
            existing["positions"] = [p for p in existing["positions"] if p.get("symbol") != "1000PEPEUSDT"]
            existing["positions"].append(pepe_pos)
            data = existing
except Exception:
    pass

with open('paper_storage.json', 'w') as f:
    json.dump(data, f, indent=2)

print("1000PEPEUSDT Adopted Successfully")
