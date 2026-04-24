import asyncio
import os
import sys

# Garante que o dir atual está no path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.firebase_service import firebase_service

async def run_audit():
    await firebase_service.initialize()
    await asyncio.sleep(2)
    
    if not firebase_service.db:
        print("Erro Firebase")
        return
        
    print("---  AUDITORIA DO VAULT (CICLO) ---")
    
    # Busca o status atual da Banca e do Ciclo    
    banca_doc = firebase_service.db.collection("banca_status").document("status").get().to_dict()
    cycle_doc = firebase_service.db.collection("vault_management").document("current_cycle").get().to_dict()
    
    print(f"\n[DADOS ATUAIS - FIREBASE]")
    print(f"Banca Configurada (Inicial): ${banca_doc.get('configured_balance', 0)}")
    print(f"Banca Total: ${banca_doc.get('saldo_total', 0)}")
    print(f"Lucro Ciclo (cycle_profit): ${cycle_doc.get('cycle_profit', 0)}")
    print(f"Banca do Ciclo (cycle_start_bankroll): ${cycle_doc.get('cycle_start_bankroll', 0)}")
    
    # Busca Histórico Real
    print(f"\n[SOMATÓRIO DO HISTÓRICO DE TRADES]")
    trades = list(firebase_service.db.collection("trade_history").stream())
    
    profit_total = sum(t.to_dict().get('pnl', 0) for t in trades)
    print(f"PnL líquido de TODOS os {len(trades)} trades da história: ${profit_total:.2f}")

    print("\nOs últimos 15 trades (pra bater com a lista):")
    sorted_trades = sorted([t.to_dict() for t in trades], key=lambda x: x.get('timestamp', ''), reverse=True)[:15]
    for t in sorted_trades:
        print(f"{t.get('symbol')} | {t.get('side')} | PnL: ${t.get('pnl', 0):.2f} | Tipo: {t.get('slot_type')} | Slot: {t.get('slot_id')} | {t.get('close_reason')}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(run_audit())
