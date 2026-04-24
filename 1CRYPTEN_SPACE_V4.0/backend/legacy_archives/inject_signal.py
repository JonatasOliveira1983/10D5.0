
import asyncio
from services.signal_generator import signal_generator
from services.sovereign_service import sovereign_service
import time

async def inject_test_signal():
    print("🚀 Injetando sinal de teste em memoria...")
    
    test_signal = {
        "id": f"test_{int(time.time())}",
        "symbol": "BTCUSDT",
        "side": "Buy",
        "score": 98,
        "layer": "SNIPER",
        "indicators": {
            "pattern": "ELITE_TEST",
            "atr": 100,
            "decorrelation_play": True  # Bypassa o RANGING guard
        },
        "reasoning": "Teste de migração MODO PAPER - Banca $20",
        "timestamp": time.time()
    }
    
    # Injeta na fila do SignalGenerator que o Captain monitora
    if hasattr(signal_generator, "signal_queue"):
        await signal_generator.signal_queue.put(test_signal)
        print("✅ Sinal injetado na queue com sucesso!")
    else:
        print("❌ Fila do SignalGenerator nao encontrada.")

if __name__ == "__main__":
    # Como o backend ja esta rodando em outro processo, 
    # este script precisaria rodar DENTRO do contexto do backend ou via API.
    # Vou criar um endpoint temporario no main.py para facilitar o teste.
    print("Script deve ser chamado via endpoint ou rodar no mesmo loop.")
