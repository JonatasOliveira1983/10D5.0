import sys
import asyncio
sys.path.append('c:/Users/spcom/Desktop/10D-3.0/1CRYPTEN_SPACE_V4.0/backend')

from services.execution_protocol import execution_protocol
from services.bankroll import bankroll_manager

async def run_tests():
    print('--- TESTANDO EMANCIPAÇÃO (V110.2) ---')
    slot_data = {'symbol': 'DYDXUSDT', 'side': 'Sell', 'entry_price': 2.0, 'slot_type': 'SNIPER', 'status': 'ATIVO'}
    should, reason, sl = await execution_protocol.process_sniper_logic(slot_data, 1.95, 125.0)
    print(f'ROI 125.0% -> Emancipou? {reason == \"EMANCIPATE_SLOT\"} (MOTIVO: {reason})')

    should, reason, sl = await execution_protocol.process_sniper_logic(slot_data, 1.95, 170.0)
    print(f'ROI 170.0% -> Emancipou? {reason == \"EMANCIPATE_SLOT\"} (MOTIVO: {reason})')
    
    print('\n--- TESTANDO VALOR DA MARGEM FIXA (.00) ---')
    print(f'Banca  -> Margem calculada: $', await bankroll_manager._calculate_target_margin(100.0, 50.0))
    print(f'Banca .9 -> Margem calculada: $', await bankroll_manager._calculate_target_margin(39.9, 50.0))

asyncio.run(run_tests())
