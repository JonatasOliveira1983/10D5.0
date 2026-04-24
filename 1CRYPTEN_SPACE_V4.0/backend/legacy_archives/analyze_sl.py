import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (onde deve estar o caminho do Firebase)
load_dotenv()

# Garante que o diretório atual está no path para importar imports locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sovereign_service import sovereign_service

async def analyze():
    print("Iniciando análise do histórico de trades (Foco em Stop Loss e Slots)...")
    
    # Inicializa o serviço Firebase
    await sovereign_service.initialize()
    
    # Aguarda inicialização do Firebase
    await asyncio.sleep(2)
    
    if not sovereign_service.db:
        print("Erro: Banco de dados não conectado.")
        return

    try:
        # Busca os últimos 500 trades para ter uma amostra boa
        docs = list(sovereign_service.db.collection("trade_history").order_by("timestamp", direction="DESCENDING").limit(200).stream())
        
        scalp_trades = [] # Slots 1 e 2
        trend_trades = [] # Slots 3 e 4
        
        for doc in docs:
            data = doc.to_dict()
            slot_id = data.get("slot_id")
            
            if slot_id in [1, 2]:
                scalp_trades.append(data)
            elif slot_id in [3, 4]:
                trend_trades.append(data)
                
        def print_analysis(name, trades):
            print(f"\n--- Análise: {name} ---")
            print(f"Total de trades analisados: {len(trades)}")
            if not trades:
                return
                
            wins = [t for t in trades if t.get("pnl", 0) > 0]
            losses = [t for t in trades if t.get("pnl", 0) <= 0]
            
            print(f"Wins: {len(wins)} | Losses: {len(losses)}")
            
            phases = {}
            reasons = {}
            for t in trades:
                reason = t.get("close_reason", "UNKNOWN")
                reasons[reason] = reasons.get(reason, 0) + 1
                
                # Tenta extrair a fase do reason
                phase = "UNKNOWN"
                for p in ["MEGA_PULSE", "PROFIT_LOCK", "FLASH_SECURE", "STABILIZE", "RISK_ZERO", "SAFE", "HARD_STOP"]:
                    if p in reason.upper():
                        phase = p
                        break
                phases[phase] = phases.get(phase, 0) + 1
            
            print("Motivos de Fechamento (Close Reason):")
            for r, c in sorted(reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {r}: {c} vezes")
                
            print("Distribuição de Fases do Stop Loss:")
            for p, c in sorted(phases.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {p}: {c} vezes ({(c/len(trades))*100:.1f}%)")
                
            # ROI Médio nas perdas (para ver quão fundo o stop foi atingido)
            if losses:
                avg_loss_roi = sum(float(t.get("pnl_percent", 0)) for t in losses) / len(losses)
                print(f"ROI Médio nas Perdas (Profundidade do Stop): {avg_loss_roi:.2f}%")
            else:
                print("Nenhuma perda registrada nessa amostra.")
                
            if wins:
                avg_win_roi = sum(float(t.get("pnl_percent", 0)) for t in wins) / len(wins)
                print(f"ROI Médio nos Ganhos (Alvo alcançado): {avg_win_roi:.2f}%")
        
        print_analysis("Batalhão Rápido (SCALP) - Slots 1 e 2", scalp_trades)
        print_analysis("Batalhão Pesado (TREND) - Slots 3 e 4", trend_trades)
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(analyze())
