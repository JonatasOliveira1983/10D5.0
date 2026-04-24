
import math

def calculate_sl_logic(current_price, side, atr, is_market_ranging, is_swing_macro, adaptive_sl=0):
    # Volatility Ratio (Simulating Captain's logic)
    vol_ratio = (atr / current_price) if current_price > 0 else 0
    
    # Adaptive SL Buffer (V42.5 Logic)
    sl_buffer_pct = max(0.001, min(0.0035, vol_ratio * 0.2)) if atr > 0 else 0.001
    
    # 1. Bankroll Risk Cap (V42.5 Logic)
    if is_market_ranging:
        asset_volatility = (atr / current_price) if current_price > 0 else 0
        if asset_volatility > 0.008:
            max_risk = 0.020 
        else:
            max_risk = 0.010
    else:
        max_risk = 0.040 if is_swing_macro else 0.020

    # 2. Final SL Choice
    if adaptive_sl > 0:
        # Captain already applied the buffer in its logic
        # We simulate the Captain's output here if we were testing the Captain directly
        # But in Bankroll, we use it as is if it's within the risk cap
        final_sl = adaptive_sl
    else:
        sl_percent = min(max_risk, (atr * 1.5) / current_price) if atr > 0 else max_risk
        final_sl = current_price * (1 - sl_percent) if side == "Buy" else current_price * (1 + sl_percent)

    # V42.9 Adaptive Logic
    asset_volatility = (atr / current_price) if current_price > 0 else 0
    
    if is_market_ranging:
        # V42.9 RANGING AGGRESSIVE
        dyn_risk_zero_trigger = 30.0
        dyn_stabilize_trigger = 50.0
        dyn_flash_secure_trigger = 70.0
        dyn_profit_lock_trigger = 100.0
        
        sl_risk_zero = 10.0
        sl_stabilize = 30.0
        sl_flash_secure = 50.0
        sl_profit_lock = 80.0
    elif asset_volatility > 0.01:
        # Stage 2: Safe Triggers (Guardian V42.8)
        dyn_risk_zero_trigger = 50.0 
        dyn_stabilize_trigger = 75.0
        dyn_flash_secure_trigger = 100.0
        dyn_profit_lock_trigger = 130.0 
        
        sl_risk_zero = 10.0
        sl_stabilize = 40.0
        sl_flash_secure = 70.0
        sl_profit_lock = 100.0
    else:
        # V42.9 EXPANSIVE GROWTH (Trend)
        dyn_risk_zero_trigger = 40.0
        dyn_stabilize_trigger = 70.0
        dyn_flash_secure_trigger = 100.0
        dyn_profit_lock_trigger = 130.0
        
        sl_risk_zero = 10.0
        sl_stabilize = 40.0
        sl_flash_secure = 70.0
        sl_profit_lock = 100.0

    # V42.9 Rule of 100 & Gas Logic
    # In the real code, ROI is calculated early. Here we use a high ROI for simulation.
    roi = 100.0 if not is_market_ranging else 50.0 
    
    if roi >= 100.0:
        gas_favorable = True # Simulation assumes favorable by default for logic test
        if gas_favorable:
            # Lock 80% and activate MegaPulse
            dyn_profit_lock_trigger = 100.0
            sl_profit_lock = 80.0
        else:
            return {"action": "CLOSE_AT_100"}

    # Stage 3: Trailing Gap (MegaPulse)
    vol_gap = (atr / current_price) * 50 * 100 * 1.5 if (atr and current_price > 0) else 0
    trailing_gap = max(60.0, vol_gap)

    return {
        "max_risk_pct": max_risk * 100,
        "sl_buffer_pct": sl_buffer_pct * 100,
        "final_sl": final_sl,
        "sl_distance_pct": abs((current_price - final_sl) / current_price) * 100,
        "net_zero_trigger": 18.0,
        "net_zero_sl": 10.0,
        "risk_zero_trigger": dyn_risk_zero_trigger,
        "risk_zero_sl": sl_risk_zero,
        "flash_secure_trigger": dyn_flash_secure_trigger,
        "flash_secure_sl": sl_flash_secure,
        "mega_pulse_trigger": dyn_profit_lock_trigger,
        "mega_pulse_sl_lock": sl_profit_lock,
        "trailing_gap": trailing_gap
    }

# Test Case: TRUMPUSDT Lifecycle
print("--- TEST CASE: TRUMPUSDT V42.8 (Guardian of 26%) ---")
result = calculate_sl_logic(4.05, "Buy", 0.15, True, False)
print(f"Stage 1: Initial SL: {result['sl_distance_pct']:.2f}% (Folego)")
print(f"Safety First (V42.9): @ {result['net_zero_trigger']}% ROI -> Move SL to +{result['net_zero_sl']}% (Net-Zero)")
print(f"Stage 2 Safe-Path ({'LATERAL' if result['risk_zero_trigger'] == 30.0 else 'TREND'}):")
print(f"  @ {result['risk_zero_trigger']}% ROI -> Lock {result['risk_zero_sl']}% ROI")
print(f"  @ {result['flash_secure_trigger']}% ROI -> Lock {result['flash_secure_sl']}% ROI")
print(f"  @ {result['mega_pulse_trigger']}% ROI -> Lock {result['mega_pulse_sl_lock']}% ROI (WIN SECURED!)")
print(f"Stage 3 Expansion: MegaPulse ACTIVE @ {result['mega_pulse_trigger']}%")
print(f"Stage 3 Trailing Gap: {result['trailing_gap']:.1f}% ROI ({result['trailing_gap']/50:.2f}% Price)")

# Test Case: TRUMPUSDT + Adaptive SL (Tocaia)
# Pivot: 3.99, Buffer should be higher now
current_price = 4.05
pivot_price = 3.99
vol_ratio = 0.15 / 4.05
sl_buffer_pct = max(0.001, min(0.0035, vol_ratio * 0.2))
adaptive_sl = pivot_price * (1 - sl_buffer_pct)

print("\n--- TEST CASE: TRUMPUSDT TOCAIA (Adaptive SL) ---")
print(f"Vol Ratio: {vol_ratio*100:.2f}%")
print(f"Dynamic Buffer: {sl_buffer_pct*100:.3f}%")
print(f"Pivot: ${pivot_price:.4f} | Adaptive SL: ${adaptive_sl:.4f}")
print(f"Distance from Pivot: ${pivot_price - adaptive_sl:.4f}")

# Compare with OLD logic (Fixed 0.1%)
old_adaptive_sl = pivot_price * (1 - 0.001)
print(f"OLD Adaptive SL: ${old_adaptive_sl:.4f} (Distance: ${pivot_price - old_adaptive_sl:.4f})")
