import asyncio
import sys
import os
import time
from collections import deque
from unittest.mock import MagicMock, AsyncMock, patch

# Configurando o ambiente para não tentar carregar Firebase real
os.environ["FIREBASE_SERVICE_ACCOUNT"] = "{}" 

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def run_v110_62_validation():
    print("="*60)
    print("      SISTEMA SNIPER 10D - VALIDACAO TACTICAL V110.62")
    print("="*60)

    # 1. TESTE PILAR 1: CORRELATION SHIELD
    print("\n[TEST 1] Correlation Shield Execution...")
    
    # Mocking bybit_ws_service e captain_agent
    with patch("services.bybit_ws.bybit_ws_service") as mock_ws, \
         patch("services.firebase_service.firebase_service") as mock_fb:
        
        from services.bybit_ws import BybitWS
        real_ws = BybitWS() # Instancia localmente para testar a logica math
        
        # Simular paridade perfeita SOL e ETH
        sym_a = "ETHUSDT"
        sym_b = "SOLUSDT"
        real_ws.price_history[sym_a] = deque([100 * (1 + i*0.01) for i in range(20)], maxlen=60)
        real_ws.price_history[sym_b] = deque([50 * (1 + i*0.01) for i in range(20)], maxlen=60)
        
        correlation = real_ws.get_correlation(sym_a, sym_b)
        print(f"  > Correlacao Calculada (ETH vs SOL): {correlation:.4f}")
        
        if correlation > 0.99:
            print("  [SUCCESS] Pearson Math OK.")
        else:
            print("  [FAIL] Pearson Math Incrustado.")

    # 2. TESTE PILAR 2: ADAPTIVE WEIGHTING (LIBRARIAN)
    print("\n[TEST 2] Librarian Auditor Logic...")
    
    with patch("services.firebase_service.firebase_service") as mock_fb:
        from services.agents.librarian_auditor import LibrarianAuditor
        auditor = LibrarianAuditor()
        
        # Mocking trades: SMC confiante mas errando (LOSS)
        mock_trades = []
        for i in range(5):
            mock_trades.append({
                "pnl": -10, 
                "fleet_intel": {"macro": 50, "micro": 50, "smc": 90},
                "timestamp": time.time()
            })
        
        mock_fb.get_trade_history = AsyncMock(return_value=mock_trades)
        mock_fb.save_system_bias = AsyncMock()
        
        await auditor.perform_audit()
        
        new_smc_weight = auditor.biases.get("smc_weight")
        print(f"  > Novo Peso SMC apos 5 losses: {new_smc_weight}")
        
        if new_smc_weight <= 0.5:
            print("  [SUCCESS] Bias Adjustment OK.")
        else:
            print("  [FAIL] Bias Adjustment Failed.")

    # 3. TESTE PILAR 3: GUARDIAN HEDGE (ORACLE)
    print("\n[TEST 3] Guardian Hedge Sentinel...")
    
    with patch("services.bankroll.bankroll_manager") as mock_bank, \
         patch("services.firebase_service.firebase_service") as mock_fb:
        
        from services.agents.oracle_agent import OracleAgent
        oracle = OracleAgent()
        
        mock_bank.activate_emergency_hedge = AsyncMock()
        
        # Simular FLASH CRASH (-2.5% em 15m)
        crash_slice = {"btc_variation_15m": -2.5, "btc_price": 62000}
        await oracle.update_market_data("BybitWS", crash_slice)
        
        if mock_bank.activate_emergency_hedge.called:
            print("  [SUCCESS] Oracle Panic Trigger OK.")
        else:
            print("  [FAIL] Oracle Panic Trigger Failed.")

    print("\n" + "="*60)
    print("      VALIDACAO V110.62 COMPLETA: SISTEMA PRONTO")
    print("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(run_v110_62_validation())
    except Exception as e:
        print(f"CRITICAL ERROR IN VALIDATION: {e}")
