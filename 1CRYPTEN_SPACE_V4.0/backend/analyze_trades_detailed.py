import asyncio
import os
import sys
import json
from collections import Counter, defaultdict
from datetime import datetime

# Adiciona o diretório atual ao path para importar os serviços
sys.path.append(os.getcwd())
from services.sovereign_service import sovereign_service

async def analyze_trades_detailed():
    await sovereign_service.initialize()
    # Pega os últimos 300 trades para uma base estatística melhor
    trades = await sovereign_service.get_trade_history(limit=300)
    
    if not trades:
        print("Nenhum trade encontrado no histórico.")
        return

    total_pnl = 0
    wins = 0
    losses = 0
    
    patterns = defaultdict(lambda: {"pnl": 0, "wins": 0, "total": 0, "scores": [], "reasons": Counter()})
    symbols = defaultdict(lambda: {"pnl": 0, "wins": 0, "total": 0})
    sides = defaultdict(lambda: {"pnl": 0, "wins": 0, "total": 0})
    
    # Análise de Score
    score_success = {"high": {"wins": 0, "total": 0}, "mid": {"wins": 0, "total": 0}, "low": {"wins": 0, "total": 0}}

    for t in trades:
        pnl = float(t.get('realized_pnl', t.get('pnl', 0)))
        roi = float(t.get('pnl_percent', t.get('roi', 0)))
        pattern = t.get('pattern', 'UNKNOWN')
        symbol = t.get('symbol', 'UNKNOWN')
        side = t.get('side', 'UNKNOWN')
        score = float(t.get('score', 0))
        
        total_pnl += pnl
        if pnl > 0:
            wins += 1
        else:
            losses += 1
            
        # Stats por Padrão
        patterns[pattern]["pnl"] += pnl
        patterns[pattern]["total"] += 1
        patterns[pattern]["scores"].append(score)
        patterns[pattern]["reasons"][t.get('close_reason', 'UNKNOWN')] += 1
        if pnl > 0:
            patterns[pattern]["wins"] += 1
            
        # Stats por Símbolo
        symbols[symbol]["pnl"] += pnl
        symbols[symbol]["total"] += 1
        if pnl > 0:
            symbols[symbol]["wins"] += 1
            
        # Stats por Lado
        sides[side]["pnl"] += pnl
        sides[side]["total"] += 1
        if pnl > 0:
            sides[side]["wins"] += 1
            
        # Stats por Score
        if score >= 80:
            score_success["high"]["total"] += 1
            if pnl > 0: score_success["high"]["wins"] += 1
        elif score >= 60:
            score_success["mid"]["total"] += 1
            if pnl > 0: score_success["mid"]["wins"] += 1
        else:
            score_success["low"]["total"] += 1
            if pnl > 0: score_success["low"]["wins"] += 1

    # Formatação dos resultados
    summary = {
        "global": {
            "total_trades": len(trades),
            "wins": wins,
            "losses": losses,
            "win_rate": f"{(wins/len(trades)*100):.2f}%",
            "total_pnl": f"${total_pnl:.2f}"
        },
        "patterns": {},
        "top_symbols": {},
        "side_performance": {},
        "score_correlation": {}
    }

    for p, data in patterns.items():
        wr = (data["wins"]/data["total"]*100) if data["total"] > 0 else 0
        avg_score = sum(data["scores"])/len(data["scores"]) if data["scores"] else 0
        summary["patterns"][p] = {
            "total": data["total"],
            "win_rate": f"{wr:.2f}%",
            "total_pnl": f"${data['pnl']:.2f}",
            "avg_score": f"{avg_score:.1f}",
            "reasons": dict(data["reasons"])
        }
        
    for s, data in sorted(symbols.items(), key=lambda x: x[1]["pnl"], reverse=True)[:10]:
        wr = (data["wins"]/data["total"]*100) if data["total"] > 0 else 0
        summary["top_symbols"][s] = {
            "total": data["total"],
            "win_rate": f"{wr:.2f}%",
            "total_pnl": f"${data['pnl']:.2f}"
        }
        
    for side, data in sides.items():
        wr = (data["wins"]/data["total"]*100) if data["total"] > 0 else 0
        summary["side_performance"][side] = {
            "win_rate": f"{wr:.2f}%",
            "total_pnl": f"${data['pnl']:.2f}"
        }
        
    for cat, data in score_success.items():
        wr = (data["wins"]/data["total"]*100) if data["total"] > 0 else 0
        summary["score_correlation"][cat] = {
            "total": data["total"],
            "win_rate": f"{wr:.2f}%"
        }

    # Salva em arquivo para análise persistente
    with open('trade_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)
    
    print(json.dumps(summary, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(analyze_trades_detailed())
