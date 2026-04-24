import os

def audit_fast():
    log_path = "backend_live.log"
    if not os.path.exists(log_path):
        print("Log nao encontrado!")
        return

    print(f"--- AUDITORIA RELAMPAGO ELITE 40 (V110.173) ---")
    
    # Pegar as ultimas 1000 linhas de forma eficiente
    with open(log_path, "rb") as f:
        f.seek(0, os.SEEK_END)
        filesize = f.tell()
        buffer_size = min(filesize, 50000) # Ultimos 50KB
        f.seek(filesize - buffer_size)
        data = f.read().decode('utf-16-le', errors='ignore')
        lines = data.splitlines()

    # 1. Fleet Size Check
    fleet_scans = [l for l in lines if "RADAR-PERF" in l]
    if fleet_scans:
        print(f"ULTIMA VARREDURA: {fleet_scans[-1].strip()}")
    else:
        print("ALERTA: Nenhuma varredura detectada.")

    # 2. Activity Sample
    monitored = set()
    for l in lines:
        if "[DECOR]" in l:
            try:
                sym = l.split("[DECOR]")[1].split(":")[0].strip()
                monitored.add(sym)
            except: pass
    
    print(f"\nATIVIDADE: Detectados {len(monitored)} ativos em processamento.")
    if monitored:
        print(f"EXEMPLOS: {list(monitored)[:5]}")

    # 3. Decision Check
    rejections = [l for l in lines if "rejeitado" in l or "rejected" in l or "Bloqueado" in l]
    print(f"\nDECISOES RECENTES: {len(rejections)} sinais filtrados.")
    for r in rejections[-3:]:
        print(f" -> {r.strip()}")

if __name__ == "__main__":
    audit_fast()
