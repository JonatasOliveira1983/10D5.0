import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

r = requests.get('http://localhost:8085/api/radar/librarian', timeout=10).json()
rankings = r.get('rankings', [])

print(f"Total rankings: {len(rankings)}")
print()

for item in rankings[:5]:
    symbol = item.get('symbol', '?')
    has_dna = 'dna' in item and item['dna'] is not None
    has_nectar = 'nectar_seal' in item and item['nectar_seal'] is not None
    
    print(f"{symbol}:")
    print(f"  win_rate: {item.get('win_rate')}")
    print(f"  quality_seal: {item.get('quality_seal', 'N/A')}")
    print(f"  nectar_seal: {item.get('nectar_seal', 'NOT PRESENT')}")
    print(f"  has_dna: {has_dna}")
    if has_dna:
        print(f"  dna: {json.dumps(item['dna'], indent=4)}")
    print(f"  keys: {sorted(item.keys())}")
    print()
