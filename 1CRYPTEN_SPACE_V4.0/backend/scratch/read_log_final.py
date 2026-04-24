import sys

try:
    # Usando utf-16le e ignorando erros para garantir a leitura
    with open('backend_live.log', 'r', encoding='utf-16le', errors='ignore') as f:
        content = f.read()
        lines = content.splitlines()
        for line in lines[-50:]:
            # Filtrando caracteres não-ascii para evitar erro de print no console do VS Code
            clean_line = "".join(i for i in line if ord(i) < 128)
            print(clean_line)
except Exception as e:
    print(f"Erro: {e}")
