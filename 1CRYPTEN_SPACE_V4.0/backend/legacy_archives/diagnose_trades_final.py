import asyncio
import os
import json
from datetime import datetime, timezone
import logging

# Ensure we can import services
import sys
project_root = os.getcwd()
# Assuming we run from backend
backend_path = project_root 
sys.path.append(backend_path)

from firebase_admin import credentials, firestore, initialize_app, get_app, delete_app

async def analyze_recent_trades():
    print("LOG: Inicializando Firebase via Admin SDK diretamente...")
    cred_path = os.path.join(backend_path, "serviceAccountKey.json")
    
    if not os.path.exists(cred_path):
        print(f"ERROR: Arquivo de credenciais nao encontrado em {cred_path}")
        return

    try:
        try:
            delete_app(get_app())
        except: pass
        
        cred = credentials.Certificate(cred_path)
        initialize_app(cred)
        db = firestore.client()
        print("✅ Conectado ao Firestore.")
    except Exception as e:
        print(f"ERROR: Falha na conexao: {e}")
        return

    print("LOG: Buscando historico de trades...")
    try:
        def _get_history():
            docs = (db.collection("trade_history")
                    .order_by("timestamp", direction="DESCENDING")
                    .limit(10)
                    .stream())
            return [{**d.to_dict(), "id": d.id} for d in docs]
        
        trades = await asyncio.to_thread(_get_history)
    except Exception as e:
        print(f"ERROR: Erro ao buscar historico: {str(e)}")
        return

    if not trades:
        print("INFO: Nenhum trade encontrado no 'trade_history'. Verificando logs...")
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
        print(f"PnL: ${pnl} ({roi}%) | Exit: {exit_type}")
        print(f"Relatorio: {pensamento}")
        
        if intel:
            print(f"Score: {intel.get('unified_score', 'N/A')} | Sentiment: {intel.get('sentiment', 'N/A')} | Trap: {intel.get('trap_risk', 'N/A')}")
        
        # Analyze why it closed
        if roi >= 75:
            print(">>> ANALISE: Fechamento por TAKE PROFIT (Alvo atingido).")
        elif roi <= -25:
            print(">>> ANALISE: Fechamento por STOP LOSS (Protecao de capital).")
        elif "Emancipado" in pensamento:
            print(">>> ANALISE: EMANCIPACAO - Ordem promovida para Moonbag (em andamento livre).")
        elif "Trailing" in pensamento or "TS" in str(exit_type):
            print(">>> ANALISE: TRAILING STOP - Lucro protegido apos recuo do preco.")
        elif "Reaper" in pensamento:
            print(">>> ANALISE: Fechamento por Seguranca (Reaper) - Condicao de risco detectada.")
        else:
            print(">>> ANALISE: Fechamento por Fluxo/Exaustao detectada pelo Sentinela.")
        
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(analyze_recent_trades())
