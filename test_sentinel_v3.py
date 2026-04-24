import sys
import codecs

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import asyncio
import time
import os
from typing import Dict, Any

# Ajuste de caminhos para importar os serviços
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

from services.execution_protocol import execution_protocol

async def mock_gas_true(symbol, side):
    return True

async def mock_gas_false(symbol, side):
    return False

async def test_sentinel_v3():
    print("[TESTE SENTINEL 3.0] Iniciando validadacao tecnica...")
    
    # 1. Caso: SL Atingido com Gás Favorável (Primeiro Hit)
    slot_data = {
        "symbol": "BTCUSDT.P",
        "side": "Buy",
        "entry_price": 60000.0,
        "current_stop": 59500.0,
        "sentinel_first_hit_at": 0,
        "roi": -40.0 # Perda de ~$500 num trade de $60k a 50x
    }
    
    current_price = 59490.0 # Abaixo do SL (59500)
    
    # Mock do Gás Positivo
    original_gas_check = execution_protocol._check_gas_favorable
    execution_protocol._check_gas_favorable = mock_gas_true
    
    print("\n--- Cenário 1: Primeiro toque no SL com Gás Favorável ---")
    should_close, reason, new_val = await execution_protocol.process_sniper_logic(slot_data, current_price, slot_data["roi"])
    
    print(f"Should Close: {should_close} (Esperado: False)")
    print(f"Reason: {reason} (Esperado: SENTINEL_ACTIVATE)")
    print(f"Timestamp retornado: {new_val} (Esperado: > 0)")
    
    if not should_close and reason == "SENTINEL_ACTIVATE" and new_val > 0:
        print("✅ SUCESSO: Sentinel ativado com sucesso!")
    else:
        print("❌ FALHA: Sentinel não ativou como esperado.")

    # 2. Caso: Sob proteção, ainda com Gás Favorável
    print("\n--- Cenário 2: Sob proteção (15s passados) com Gás Favorável ---")
    execution_protocol.last_check_times[slot_data["symbol"]] = 0 # Reset Throttle
    first_hit = time.time() - 15
    slot_data["sentinel_first_hit_at"] = first_hit
    
    should_close, reason, new_val = await execution_protocol.process_sniper_logic(slot_data, current_price, slot_data["roi"])
    print(f"Should Close: {should_close} (Esperado: False)")
    print(f"Reason: {reason} (Esperado: SENTINEL_WAITING)")
    
    if not should_close and reason == "SENTINEL_WAITING":
         print("✅ SUCESSO: Sentinel mantendo a posição!")
    else:
         print("❌ FALHA: Sentinel deveria estar segurando.")

    # 3. Caso: Gás vira contra a posição
    print("\n--- Cenário 3: Gás vira contra a posição durante a carência ---")
    execution_protocol.last_check_times[slot_data["symbol"]] = 0 # Reset Throttle
    execution_protocol._check_gas_favorable = mock_gas_false
    
    should_close, reason, new_val = await execution_protocol.process_sniper_logic(slot_data, current_price, slot_data["roi"])
    print(f"Should Close: {should_close} (Esperado: True)")
    print(f"Reason: {reason} (Esperado: SNIPER_SL_...)")
    
    if should_close:
         print("✅ SUCESSO: Posição encerrada por virada de Gás!")
    else:
         print("❌ FALHA: Deveria ter fechado a posição.")

    # 4. Caso: Timeout de 60s
    print("\n--- Cenário 4: Timeout de 60 segundos esgotado ---")
    execution_protocol.last_check_times[slot_data["symbol"]] = 0 # Reset Throttle
    execution_protocol._check_gas_favorable = mock_gas_true # Gás volta a ser bom
    slot_data["sentinel_first_hit_at"] = time.time() - 61 # 61 segundos atrás
    
    should_close, reason, new_val = await execution_protocol.process_sniper_logic(slot_data, current_price, slot_data["roi"])
    print(f"Should Close: {should_close} (Esperado: True)")
    
    if should_close:
         print("✅ SUCESSO: Posição encerrada por Timeout!")
    else:
         print("❌ FALHA: Deveria ter fechado por tempo.")

    # Restaurar mock
    execution_protocol._check_gas_favorable = original_gas_check
    print("\n🏁 Testes finalizados.")

if __name__ == "__main__":
    asyncio.run(test_sentinel_v3())
