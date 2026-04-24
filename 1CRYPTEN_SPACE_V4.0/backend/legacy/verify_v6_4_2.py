
import time

def test_cvd_threshold(atr, current_price, base_threshold):
    vol_ratio = atr / current_price if current_price > 0 else 0
    adaptive_threshold = base_threshold
    
    if vol_ratio > 0.015:
        vol_multiplier = min(2.5, 1.0 + (vol_ratio * 50))
        adaptive_threshold *= vol_multiplier
        return adaptive_threshold, vol_multiplier
    return adaptive_threshold, 1.0

def test_anchorage_sl(current_price, side, atr):
    vol_ratio = atr / current_price if current_price > 0 else 0
    sl_buffer_pct = max(0.005, min(0.012, vol_ratio * 0.5)) if atr > 0 else 0.010
    
    if side.lower() == "buy":
        anchor_sl = current_price * (1 - sl_buffer_pct)
    else:
        anchor_sl = current_price * (1 + sl_buffer_pct)
        
    return anchor_sl, sl_buffer_pct

def test_tiered_blocking(pnl, final_roi, consecutive_losses):
    block_duration = 0
    is_deep_loss = final_roi <= -80.0
    
    if is_deep_loss:
        block_duration = 86400 * 2 # 48h
    elif consecutive_losses >= 2:
        block_duration = 86400 # 24h
        
    return block_duration, is_deep_loss

def test_accelerated_protection(asset_volatility):
    if asset_volatility > 0.01:
        dyn_risk_zero = 30.0
        sl_risk_zero = 5.0
        return dyn_risk_zero, sl_risk_zero
    return 50.0, 10.0 # Standard V42.8

print("--- VERIFICATION V6.4.2 REFINEMENTS ---")

# 1. Test CVD Scaling
print("\n[1] CVD Threshold Scaling:")
t1, m1 = test_cvd_threshold(0.01, 1.0, 1000) # Vol = 1% (Low)
print(f"Low Vol (1%): Threshold={t1:.0f}, Multiplier={m1:.2f}x")
t2, m2 = test_cvd_threshold(0.04, 1.0, 1000) # Vol = 4% (High)
print(f"High Vol (4%): Threshold={t2:.0f}, Multiplier={m2:.2f}x")

# 2. Test Anchorage SL
print("\n[2] Anchorage Adaptive SL:")
sl1, buf1 = test_anchorage_sl(100.0, "Buy", 0.5) # Vol = 0.5% (Low)
print(f"Low Vol (0.5%): SL=${sl1:.4f}, Buffer={buf1*100:.2f}%")
sl2, buf2 = test_anchorage_sl(100.0, "Buy", 3.0) # Vol = 3.0% (High)
print(f"High Vol (3.0%): SL=${sl2:.4f}, Buffer={buf2*100:.2f}%")

# 3. Test Tiered Blocking
print("\n[3] Tiered Blocking Logic:")
dur1, deep1 = test_tiered_blocking(-10, -85.0, 1)
print(f"Deep Loss (-85% ROI): Blocked={dur1/3600:.0f}h, Deep={deep1}")
dur2, deep2 = test_tiered_blocking(-5, -30.0, 2)
print(f"Consecutive Losses (2x): Blocked={dur2/3600:.0f}h, Deep={deep2}")

# 4. Test Accelerated Protection
print("\n[4] Accelerated Protection Triggers:")
rz1, sl_z1 = test_accelerated_protection(0.005) # Low Vol
print(f"Low Vol (0.5%): Risk-Zero Trigger={rz1:.1f}% ROI, SL locked at {sl_z1:.1f}%")
rz2, sl_z2 = test_accelerated_protection(0.02) # High Vol
print(f"High Vol (2.0%): Risk-Zero Trigger={rz2:.1f}% ROI, SL locked at {sl_z2:.1f}%")
