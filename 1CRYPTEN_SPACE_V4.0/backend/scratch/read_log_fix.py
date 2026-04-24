import sys

try:
    with open('backend_live.log', 'r', encoding='utf-16le', errors='ignore') as f:
        lines = f.readlines()
        for line in lines[-30:]:
            print(line.strip())
except Exception as e:
    print(f"Erro ao ler log: {e}")
