import asyncio
import sys
import os
import time

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.agents.librarian_auditor import LibrarianAuditor
from services.sovereign_service import sovereign_service

async def test_auditor_logic():
    print("📚 Iniciando Teste do Adaptive Weighting (Pilar 2)...")
    
    auditor = LibrarianAuditor()
    
    # 1. Simular histórico de trades onde SMC errou 5 vezes seguidas
    mock_trades = []
    for i in range(5):
        mock_trades.append({
            "symbol": f"TEST{i}USDT",
            "pnl": -10.0, # LOSS
            "fleet_intel": {
                "macro": 50,
                "micro": 50,
                "smc": 95 # SMC estava confiante e errou
            },
            "timestamp": time.time() - (i * 3600)
        })
        
    # 2. Simular histórico onde WHALE acertou 5 vezes seguidas
    for i in range(5, 10):
        mock_trades.append({
            "symbol": f"TEST{i}USDT",
            "pnl": 15.0, # WIN
            "fleet_intel": {
                "macro": 50,
                "micro": 95, # Whale estava confiante e acertou
                "smc": 50
            },
            "timestamp": time.time() - (i * 3600)
        })

    # Mockando a busca de histórico no Firebase
    async def mock_get_trade_history(limit=50):
        print(f"🔍 [MOCK] Retornando {len(mock_trades)} trades simulados.")
        return mock_trades
    
    sovereign_service.get_trade_history = mock_get_trade_history
    
    # Mockando a gravação de biases para não sujar o Firebase Real do Almirante durante o teste local
    async def mock_save_system_bias(biases):
        print(f"💾 [MOCK] Biases salvos com sucesso: {biases}")
        # Verificação
        smc_w = biases.get("smc_weight", 1.0)
        whl_w = biases.get("micro_weight", 1.0) # No auditor usamos 'micro' para representar Whale nos dados
        
        if smc_w <= 0.8:
            print("🎯 TESTE PASSOU: Peso do SMC reduzido corretamente por má performance.")
        else:
            print(f"❌ TESTE FALHOU: Peso do SMC ({smc_w}) não foi reduzido.")
            
        if whl_w >= 1.1:
            print("🎯 TESTE PASSOU: Peso da Whale aumentado corretamente por boa performance.")
        else:
            print(f"❌ TESTE FALHOU: Peso da Whale ({whl_w}) não foi aumentado.")

    sovereign_service.save_system_bias = mock_save_system_bias

    # Executa a auditoria
    print("🚀 Executando Auditoria do Bibliotecário...")
    await auditor.perform_audit()

if __name__ == "__main__":
    asyncio.run(test_auditor_logic())
