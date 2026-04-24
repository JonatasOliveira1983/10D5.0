import os

def audit_log():
    log_path = "backend_live.log"
    if not os.path.exists(log_path):
        print("Log nao encontrado!")
        return

    print(f"--- AUDITORIA ELITE 40 (V110.173) ---")
    
    with open(log_path, "r", encoding="utf-16-le", errors="ignore") as f:
        lines = f.readlines()
        
    last_100 = lines[-200:]
    
    # 1. Fleet Size Check
    fleet_scans = [line for line in last_100 if "RADAR-PERF" in line]
    if fleet_scans:
        print(f"ULTIMA VARREDURA: {fleet_scans[-1].strip()}")
    else:
        print("ALERTA: Nenhuma varredura de Radar detectada nos ultimos 200 logs.")

    # 2. Sample Assets Check
    print("\nAMOSTRA DE ATIVOS MONITORADOS (ULTIMOS 5 MIN):")
    monitored_assets = set()
    for line in lines[-500:]:
        if "[DECOR]" in line:
            symbol = line.split("[DECOR]")[1].split(":")[0].strip()
            monitored_assets.add(symbol)
            
    if monitored_assets:
        print(f"Ativos detectados em movimento: {list(monitored_assets)[:10]}... (Total: {len(monitored_assets)})")
    else:
        print("ALERTA: Nenhum ativo detectado no log de Decorrelacao.")

    # 3. Captain Status
    captain_logs = [line for line in last_100 if "CaptainAgent" in line]
    if captain_logs:
        print(f"\nULTIMO MOVIMENTO DO CAPITAO: {captain_logs[-1].strip()}")
    else:
        print("\nCAPITAO: Em modo de espera (aguardando sinal de alta conviccao).")

    # 4. Error Check
    errors = [line for line in last_100 if "ERROR" in line or "CRITICAL" in line]
    if errors:
        print(f"\nERROS DETECTADOS: {len(errors)}")
        for e in errors[:3]:
            print(f" ! {e.strip()}")
    else:
        print("\nSISTEMA LIMPO: Nenhum erro critico nos ultimos logs.")

if __name__ == "__main__":
    audit_log()
