import asyncio
import os
import sys
import io

# Force UTF-8 on Windows for emoji printing
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.signal_generator import signal_generator

async def test_decorrelation_logic():
    print("=" * 70)
    print("🎯 Test V31.0: Decorrelation Hunter Logic")
    print("=" * 70)
    
    # Mock bybit_ws_service attributes
    from services.bybit_ws import bybit_ws_service
    
    # Store originals
    original_get_klines = None
    try:
        from services.bybit_rest import bybit_rest_service
        original_get_klines = bybit_rest_service.get_klines
    except:
        pass
    
    original_btc_var = bybit_ws_service.btc_variation_1h
    original_get_cvd = bybit_ws_service.get_cvd_score
    original_get_price = bybit_ws_service.get_current_price
    
    # ═══════════════════════════════════════════════════
    # TEST 1: BTC Lateral + Alt se desgrudando + LS Extremo
    # Deve retornar is_decorrelated = True
    # ═══════════════════════════════════════════════════
    print("\n[TEST 1] BTC Lateral + Alt Decorrelada + Sardinhada posicionada")
    
    bybit_ws_service.btc_variation_1h = 0.1  # BTC quase parado
    
    def mock_cvd_1(symbol):
        if "BTC" in symbol:
            return 50000  # BTC CVD neutro
        return 80000  # Alt CVD forte positivo
    
    def mock_price_1(symbol):
        if "BTC" in symbol:
            return 95000
        return 1.50  # Alt price
    
    async def mock_klines_1(symbol="", interval="", limit=2):
        if "BTC" not in symbol:
            # Simula alt que subiu 0.8% na última hora
            return [
                [0, "1.50", "1.51", "1.48", "1.50", 0],  # candle atual
                [0, "1.48", "1.49", "1.47", "1.488", 0],  # candle anterior (close=1.488)
            ]
        return [[0, "95000", "95100", "94900", "95000", 0], [0, "94950", "95050", "94850", "94950", 0]]
    
    bybit_ws_service.get_cvd_score = mock_cvd_1
    bybit_ws_service.get_current_price = mock_price_1
    if original_get_klines:
        bybit_rest_service.get_klines = mock_klines_1
    
    result1 = await signal_generator.detect_btc_decorrelation(
        symbol="XRPUSDT",
        alt_cvd=80000,
        alt_ls_ratio=1.8,  # Varejo MUITO comprado → sardinhada
        alt_oi=50000
    )
    
    print(f"  is_decorrelated: {result1.get('is_decorrelated')}")
    print(f"  direction: {result1.get('direction')}")
    print(f"  confidence: {result1.get('confidence')}")
    print(f"  signals: {result1.get('signals', [])}")
    print(f"  reason: {result1.get('reason')}")
    
    assert result1['is_decorrelated'] == True, f"❌ FALHOU: Esperava decorrelation=True, got {result1['is_decorrelated']}"
    assert result1['direction'] == "Short", f"❌ FALHOU: Esperava direction=Short (contra sardinhada Long), got {result1['direction']}"
    print("  ✅ PASSED")
    
    # ═══════════════════════════════════════════════════
    # TEST 2: BTC movendo forte → NÃO deve decorrelacionar
    # ═══════════════════════════════════════════════════
    print("\n[TEST 2] BTC movendo forte → Decorrelation bloqueada")
    
    bybit_ws_service.btc_variation_1h = 1.5  # BTC movendo forte
    
    def mock_cvd_2(symbol):
        if "BTC" in symbol:
            return 2000000  # BTC CVD forte
        return 80000
    
    bybit_ws_service.get_cvd_score = mock_cvd_2
    
    result2 = await signal_generator.detect_btc_decorrelation(
        symbol="XRPUSDT",
        alt_cvd=80000,
        alt_ls_ratio=1.8,
        alt_oi=50000
    )
    
    print(f"  is_decorrelated: {result2.get('is_decorrelated')}")
    print(f"  reason: {result2.get('reason')}")
    
    assert result2['is_decorrelated'] == False, f"❌ FALHOU: Esperava decorrelation=False quando BTC forte, got {result2['is_decorrelated']}"
    assert result2.get('reason') == 'btc_not_lateral', f"❌ FALHOU: Razão esperada 'btc_not_lateral', got {result2.get('reason')}"
    print("  ✅ PASSED")
    
    # ═══════════════════════════════════════════════════
    # TEST 3: BTC Lateral + Alt parada → NÃO deve decorrelacionar
    # ═══════════════════════════════════════════════════
    print("\n[TEST 3] BTC Lateral + Alt parada → Sem decorrelation")
    
    bybit_ws_service.btc_variation_1h = 0.1  # BTC lateral
    
    def mock_cvd_3(symbol):
        if "BTC" in symbol:
            return 100000  # Neutro
        return 2000  # Alt CVD fraco
    
    def mock_price_3(symbol):
        if "BTC" in symbol:
            return 95000
        return 1.489  # Praticamente igual ao close anterior
    
    bybit_ws_service.get_cvd_score = mock_cvd_3
    bybit_ws_service.get_current_price = mock_price_3
    
    result3 = await signal_generator.detect_btc_decorrelation(
        symbol="XRPUSDT",
        alt_cvd=2000,
        alt_ls_ratio=1.0,  # LS ratio neutro
        alt_oi=0
    )
    
    print(f"  is_decorrelated: {result3.get('is_decorrelated')}")
    print(f"  reason: {result3.get('reason')}")
    
    assert result3['is_decorrelated'] == False, f"❌ FALHOU: Esperava False para alt parada"
    print("  ✅ PASSED")
    
    # ═══════════════════════════════════════════════════
    # TEST 4: Bear Trap — Varejo vendido + Alt subindo sozinha
    # ═══════════════════════════════════════════════════
    print("\n[TEST 4] Bear Trap — Varejo vendido + Alt subindo (BTC lateral)")
    
    bybit_ws_service.btc_variation_1h = 0.05  # BTC super lateral
    
    def mock_cvd_4(symbol):
        if "BTC" in symbol:
            return 30000  # BTC neutro
        return 60000  # Alt CVD positivo forte
    
    def mock_price_4(symbol):
        if "BTC" in symbol:
            return 95000
        return 1.50  # Alt subiu
    
    bybit_ws_service.get_cvd_score = mock_cvd_4
    bybit_ws_service.get_current_price = mock_price_4
    
    result4 = await signal_generator.detect_btc_decorrelation(
        symbol="XRPUSDT",
        alt_cvd=60000,
        alt_ls_ratio=0.6,  # Varejo MUITO vendido → bear trap
        alt_oi=30000
    )
    
    print(f"  is_decorrelated: {result4.get('is_decorrelated')}")
    print(f"  direction: {result4.get('direction')}")
    print(f"  confidence: {result4.get('confidence')}")
    print(f"  signals: {result4.get('signals', [])}")
    
    assert result4['is_decorrelated'] == True, f"❌ FALHOU: Esperava decorrelation=True para Bear Trap"
    assert result4['direction'] == "Long", f"❌ FALHOU: Esperava Long (contra sardinhada Short), got {result4['direction']}"
    print("  ✅ PASSED")
    # ═══════════════════════════════════════════════════
    # TEST 5: Anticorrelation — BTC cai, Alt sobe
    # ═══════════════════════════════════════════════════
    print("\n[TEST 5] Anticorrelation — BTC cai forte, Alt sobe forte")
    
    bybit_ws_service.btc_variation_1h = -1.2  # BTC caindo forte
    
    def mock_cvd_5(symbol):
        if "BTC" in symbol:
            return -800000  # BTC CVD negativo forte
        return 70000  # Alt CVD positivo forte
    
    def mock_price_5(symbol):
        if "BTC" in symbol:
            return 93000
        return 1.50
    
    async def mock_klines_5(symbol="", interval="", limit=2):
        if "BTC" not in symbol:
            # alt subiu 1%
            return [
                [0, "1.50", "1.51", "1.48", "1.50", 0],
                [0, "1.485", "1.49", "1.47", "1.485", 0],
            ]
        return [[0, "93000", "95100", "93000", "93000", 0], [0, "95000", "95050", "94850", "95000", 0]]
        
    bybit_ws_service.get_cvd_score = mock_cvd_5
    bybit_ws_service.get_current_price = mock_price_5
    if original_get_klines:
        bybit_rest_service.get_klines = mock_klines_5
        
    result5 = await signal_generator.detect_btc_decorrelation(
        symbol="XRPUSDT",
        alt_cvd=70000,
        alt_ls_ratio=1.6,  # Varejo comprado (vai ser liquidado se cair, mas a alt tá subindo!)
        alt_oi=40000
    )
    
    print(f"  is_decorrelated: {result5.get('is_decorrelated')}")
    print(f"  direction: {result5.get('direction')}")
    print(f"  confidence: {result5.get('confidence')}")
    print(f"  signals: {result5.get('signals', [])}")
    
    assert result5['is_decorrelated'] == True, f"❌ FALHOU: Esperava decorrelation=True no modo Anticorrelation"
    print("  ✅ PASSED")
    
    # ═══════════════════════════════════════════════════
    # RESTORE ORIGINALS
    # ═══════════════════════════════════════════════════
    bybit_ws_service.btc_variation_1h = original_btc_var
    bybit_ws_service.get_cvd_score = original_get_cvd
    bybit_ws_service.get_current_price = original_get_price
    if original_get_klines:
        bybit_rest_service.get_klines = original_get_klines
    
    print("\n" + "=" * 70)
    print("🎯 ALL 5 TESTS PASSED ✅")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_decorrelation_logic())
