import requests
import json

try:
    r = requests.get("http://localhost:8085/api/radar/pulse")
    data = r.json()
    with open("pulse_debug.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Pulse data saved to pulse_debug.json")
    print(f"Keys in pulse: {list(data.keys())}")
    if "market_context" in data:
        print(f"Market context keys: {list(data['market_context'].keys())}")
    else:
        print("CRITICAL: market_context MISSING from pulse data!")
except Exception as e:
    print(f"Error: {e}")
