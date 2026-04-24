import sqlite3
import os
import sys

# Adiciona o caminho do backend para importar os serviços
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

from services.backtest.engine import backtest_engine

def debug_backtest():
    print("DEBUG: Iniciando Diagnostico Profundo V110.63.6...")
    symbol = "SOLUSDT"
    interval = "1h"
    
    try:
        results = backtest_engine.simulate(
            symbol=symbol,
            interval=interval,
            initial_balance=100.0,
            toggles={"lateral_guillotine": True, "sentinel": True}
        )
        if "error" in results:
            print(f"❌ Erro do Simulador: {results['error']}")
        else:
            print("✅ Backtest concluído com sucesso localmente!")
    except Exception as e:
        import traceback
        print(f"💥 EXPLOSÃO DETECTADA: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_backtest()
