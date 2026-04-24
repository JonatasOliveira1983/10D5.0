import requests
import json

try:
    response = requests.get("http://localhost:8085/api/slots")
    if response.status_code == 200:
        slots = response.json()
        print(json.dumps(slots, indent=2))
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Exception: {e}")
