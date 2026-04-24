import asyncio
import os
import sys

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from services.execution_protocol import execution_protocol

async def test_sentinel():
    print("--- Testando Logica Sentinel (TREND vs SWING) ---")
    
    # Mock slot data
    # V34.0 changed all slots to SWING. We fixed line 302 to allow SWING.
    slot_data = {
        "id": 1,
        "symbol": "BTCUSDT.P",
        "side": "Buy",
        "entry_price": 50000.0,
        "current_stop": 48000.0, # This is a -200% ROI stop at 50x (4% price drop)
        "slot_type": "SWING",
        "score": 96,
        "sentinel_retests": 0
    }
    
    # Calculate ROI for a 48000 price (when entry is 50000)
    # ROI = (current - entry) / entry * leverage * 100
    # If price is 48000: (48000 - 50000) / 50000 * 50 * 100 = -2 / 50 * 5000 = -4 * 50 = -200%
    
    current_price = 48000.0
    roi = -20.0 # Just a test ROI, not mathematically linked to 50x for this simple mock
    
    print(f"Testando slot tipo: {slot_data['slot_type']} | ROI: {roi}% | Preco: {current_price}")
    
    # We want to see if it triggers the bypass check. 
    # Since we can't easily mock the 'check_shadow_sentinel_retest' return value without deep monkeypatching,
    # we'll just check if the code REACHES that part and doesn't crash.
    
    try:
        # We call process_sniper_logic. 
        # In 'SAFE' phase (ROI < trigger_risk_zero), if price <= current_stop, it checks bypass.
        should_close, reason, new_stop = await execution_protocol.process_sniper_logic(
            slot_data, current_price, roi
        )
        
        print(f"Resultado: should_close={should_close}, reason={reason}")
        
        # If the fix worked, the reason should start with 'SENTINEL_' or 'STOP_LOSS' 
        # instead of just returning False, None, None (which happens if it doesn't even hit the SL check).
        
        if reason and "SENTINEL" in reason:
            print("--- SUCESSO: O Sentinel foi consultado para o slot SWING!")
        elif reason == "STOP_LOSS_ATINGIDO":
            print("--- SUCESSO: O Sentinel foi consultado (e negou o bypass), resultando em Stop Loss.")
        else:
            print("--- AVISO: A logica de Sentinel nao foi alcancada. Verifique os thresholds de ROI/Preco no teste.")
            
    except Exception as e:
        print(f"--- ERRO no teste: {e}")

if __name__ == "__main__":
    asyncio.run(test_sentinel())
