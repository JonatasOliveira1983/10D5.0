import asyncio
import os
import json
from datetime import datetime, timezone
import logging

# Ensure we can import services
import sys
project_root = os.getcwd()
backend_path = os.path.join(project_root, "1CRYPTEN_SPACE_V4.0", "backend")
sys.path.append(backend_path)

# Mocking settings to avoid loading real config if needed, but better use real one
from services.firebase_service import FirebaseService

async def analyze_recent_trades():
    print("LOG: Inicializando Firebase Service...")
    fs = FirebaseService()
    await fs.initialize()
    
    if not fs.is_active or not fs.db:
        print("ERROR: Nao foi possivel conectar ao Firebase. Verifique as credenciais.")
        return

    print("LOG: Buscando historico de trades...")
    try:
        def _get_history():
            docs = (fs.db.collection("trade_history")
                    .order_by("timestamp", direction="DESCENDING")
                    .limit(10)
                    .stream())
            return [{**d.to_dict(), "id": d.id} for d in docs]
        
        trades = await asyncio.to_thread(_get_history)
    except Exception as e:
        print(f"ERROR: Erro ao buscar historico: {str(e)}")
        return

    if not trades:
        print("INFO: Nenhum trade encontrado no 'trade_history'. Verificando 'system_logs' para motivos de fechamento...")
        # Check logs if trades are empty (maybe they weren't logged yet?)
        try:
            def _get_logs():
                docs = (fs.db.collection("system_logs")
                        .order_by("timestamp", direction="DESCENDING")
                        .limit(30)
                        .stream())
                return [d.to_dict() for d in docs]
            logs = await asyncio.to_thread(_get_logs)
            for l in logs:
                msg = l.get("message", "")
                if "CLOSE" in msg.upper() or "FECHADO" in msg.upper() or "PROMOTED" in msg.upper():
                    print(f"LOG EVENT: {l.get('agent')} | {l.get('timestamp')} | {msg}")
        except Exception as le:
            print(f"ERROR: Erro ao buscar logs: {str(le)}")
        return

    print(f"INFO: Analisando os ultimos {len(trades)} trades:\n")
    
    for t in trades:
        symbol = t.get("symbol", "N/A")
        side = t.get("side", "N/A")
        pnl = t.get("pnl", 0)
        roi = t.get("pnl_percent", 0)
        timestamp = t.get("timestamp", "N/A")
        exit_type = t.get("exit_type", "N/A")
        pensamento = t.get("pensamento", "N/A")
        intel = t.get("fleet_intel", {})
        
        print(f"--- {symbol} ({side}) ---")
        print(f"ID: {t['id']}")
        print(f"Data: {timestamp}")
        print(f"PnL: ${pnl} ({roi}%)")
        print(f"Exit Type: {exit_type}")
        print(f"Pensamento/Relatorio: {pensamento}")
        
        if intel:
            print(f"Sinal Intel: {json.dumps({k: v for k, v in intel.items() if k in ['sentiment', 'unified_score', 'trap_risk', 'bias']}, indent=2)}")
        
        # Interpret exit type if UNKNOWN
        if roi >= 70:
            print(">>> ANALISE: Fechamento por TAKE PROFIT (Alvo atingido).")
        elif roi <= -30:
            print(">>> ANALISE: Fechamento por STOP LOSS (Protecao de capital).")
        elif exit_type == "MOONBAG_EMANCIPATION" or "Emancipado" in pensamento:
            print(">>> ANALISE: EMANCIPACAO - Ordem promovida para Moonbag (em andamento livre).")
        elif "Trailing" in pensamento or "TS" in str(exit_type):
            print(">>> ANALISE: TRAILING STOP - Lucro protegido apos reversao de fluxo.")
        elif "Reaper" in pensamento or "REAPER" in str(exit_type):
            print(">>> ANALISE: REAPER CONTROL - Fechamento forcado por risco excessivo ou erro.")
        else:
            print(">>> ANALISE: Fechamento por condicao de mercado (Possivel reversao de tendencia).")
        
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(analyze_recent_trades())
