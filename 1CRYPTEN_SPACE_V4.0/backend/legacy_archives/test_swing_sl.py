import asyncio
from services.execution_protocol import execution_protocol

async def run_sim():
    eps = execution_protocol
    
    # Fake Entry for SCALP Short
    entry = 10.00
    side = 'Sell' # Short
    leverage = 50
    slot_data = {
        'id': 1,  # Slot 1 = SCALP
        'slot_type': 'SCALP',
        'side': side,
        'entry_price': entry,
        'current_stop': 10.07, # Initial 0.7% SL (-35% ROI)
        'structural_target': 9.85, # target at 1.5%
    }
    
    test_prices = [
        (10.07, "Drawdown (-35%)"),
        (10.00, "Breakeven"),
        (9.95, "In Profit (+25%)"),
        (9.90, "Triggering Phase 2 (+50%)"),
        (9.85, "Triggering Phase 3 (+75%)"),
        (9.82, "Triggering Guard (+90%)"),
        (9.80, "Triggering Lock (+100%)"),
        (9.70, "Deep Profit (+150%)")
    ]
    
    print(f"--- SCALP SL SIMULATION (Entry: {entry}, Short, Slot 1) ---")
    for price, label in test_prices:
        roi = eps.calculate_roi(entry, price, side)
        action, reason, new_sl = await eps.process_order_logic(slot_data, price)
        
        sl_str = f"{new_sl:.4f}" if new_sl else "No Update"
        print(f"[{label}] Price: {price:.4f} | ROI: {roi:5.1f}% -> Action: {sl_str}")

asyncio.run(run_sim())
