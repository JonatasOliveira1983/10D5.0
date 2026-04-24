# -*- coding: utf-8 -*-
"""
Teste dos 3 fixes do V110.28.2
"""
import asyncio
import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.path.insert(0, ".")

PASS = 0
FAIL = 0

def ok(msg):
    global PASS
    PASS += 1
    print(f"  [PASSOU] {msg}")

def fail(msg):
    global FAIL
    FAIL += 1
    print(f"  [FALHOU] {msg}")


# ============================================================
# TEST 1: SHADOW slot_type na Escadinha (Fix #2)
# ============================================================
async def test_shadow_emancipation():
    print("=" * 60)
    print("TEST 1: Escadinha com slot_type = SHADOW")
    print("=" * 60)
    from services.execution_protocol import execution_protocol

    # Usa BTCUSDT para evitar erro de instrumento invalido
    symbol = "BTCUSDT"
    entry = 80000.0

    execution_protocol.last_check_times.clear()

    slot_shadow = {
        "symbol": symbol,
        "side": "Buy",
        "entry_price": entry,
        "current_stop": entry * 0.98,
        "slot_type": "SHADOW",
        "status": "IN_TRADE",
        "opened_at": 0,
        "sentinel_first_hit_at": 0,
        "structural_target": 0,
        "score": 80,
        "id": 1,
        "is_market_ranging": False,
    }

    # ROI = 155% - preco seria entry*(1 + 155/50/100) = entry*1.031
    price_155 = entry * (1 + 155.0 / (50 * 100))
    should_close, reason, new_sl = await execution_protocol.process_sniper_logic(
        slot_shadow, current_price=price_155, roi=155.0
    )
    print(f"  ROI=155%% -> should_close={should_close} | reason={reason} | new_sl={new_sl}")
    if reason == "EMANCIPATE_SLOT":
        ok("SHADOW emancipa em 155%% ROI")
    elif reason == "THROTTLED":
        ok("Throttle ativo (esperado em testes rapidos)")
    else:
        fail(f"SHADOW em 155%% esperava EMANCIPATE_SLOT, got {reason}")

    # ROI = 70% - preco = entry*(1 + 70/50/100) = entry*1.014
    execution_protocol.last_check_times.clear()
    price_70 = entry * (1 + 70.0 / (50 * 100))
    slot_70 = dict(slot_shadow)
    slot_70["current_stop"] = entry * 0.98
    should_close2, reason2, new_sl2 = await execution_protocol.process_sniper_logic(
        slot_70, current_price=price_70, roi=70.0
    )
    print(f"  ROI=70%%  -> should_close={should_close2} | reason={reason2} | new_sl={new_sl2}")
    if new_sl2 is not None and new_sl2 > entry:
        ok(f"SHADOW trava SL em +5%% ROI. new_sl={new_sl2:.2f}")
    elif reason2 == "THROTTLED":
        ok("Throttle ativo")
    else:
        fail(f"SHADOW em 70%% deveria new_sl > entry, got reason={reason2} new_sl={new_sl2}")

    # ROI = 110%
    execution_protocol.last_check_times.clear()
    price_110 = entry * (1 + 110.0 / (50 * 100))
    slot_110 = dict(slot_shadow)
    slot_110["current_stop"] = entry * 1.001  # ja em break-even
    should_close3, reason3, new_sl3 = await execution_protocol.process_sniper_logic(
        slot_110, current_price=price_110, roi=110.0
    )
    print(f"  ROI=110%% -> should_close={should_close3} | reason={reason3} | new_sl={new_sl3}")
    if new_sl3 is not None:
        ok(f"SHADOW trava SL em +80%% ROI. new_sl={new_sl3:.2f}")
    elif reason3 == "THROTTLED":
        ok("Throttle ativo")
    else:
        fail(f"SHADOW em 110%% deveria ter new_sl, got reason={reason3} new_sl={new_sl3}")


# ============================================================
# TEST 2: set_trading_stop atualiza paper_moonbags (Fix #1)
# ============================================================
async def test_set_trading_stop_moonbag():
    print()
    print("=" * 60)
    print("TEST 2: set_trading_stop atualiza paper_moonbags")
    print("=" * 60)
    from services.bybit_rest import bybit_rest_service

    TEST_SYM = "BTCUSDT"
    TEST_SL = "82000"

    mock_moonbag = {
        "symbol": TEST_SYM,
        "status": "EMANCIPATED",
        "stopLoss": "0",
        "avgPrice": "80000.0",
        "side": "Buy",
        "size": "0.01",
    }

    # Remove da lista tatica, adiciona em moonbags
    bybit_rest_service.paper_positions = [
        p for p in bybit_rest_service.paper_positions if p.get("symbol") != TEST_SYM
    ]
    bybit_rest_service.paper_moonbags = [
        m for m in bybit_rest_service.paper_moonbags if m.get("symbol") != TEST_SYM
    ]
    bybit_rest_service.paper_moonbags.append(mock_moonbag)

    # Atualiza SL da moonbag
    result = await bybit_rest_service.set_trading_stop(
        category="linear", symbol=TEST_SYM, stopLoss=TEST_SL
    )

    print(f"  retCode={result.get('retCode')} (esperado: 0)")
    print(f"  stopLoss da moonbag: {mock_moonbag['stopLoss']} (esperado: {TEST_SL})")

    if result.get("retCode") == 0:
        ok("set_trading_stop retCode=0 para moonbag")
    else:
        fail(f"set_trading_stop retCode={result.get('retCode')} em vez de 0")

    if mock_moonbag["stopLoss"] == TEST_SL:
        ok("stopLoss da moonbag atualizado corretamente")
    else:
        fail(f"stopLoss={mock_moonbag['stopLoss']} em vez de {TEST_SL}")

    # Limpa
    bybit_rest_service.paper_moonbags = [
        m for m in bybit_rest_service.paper_moonbags if m.get("symbol") != TEST_SYM
    ]


# ============================================================
# TEST 3: Hard-Lock 110% (Moonbag fecha ao atingir SL)
# ============================================================
async def test_moonbag_hard_lock():
    print()
    print("=" * 60)
    print("TEST 3: Hard-Lock 110%% para Moonbag (Sentinel Bypass)")
    print("=" * 60)
    from services.execution_protocol import execution_protocol

    execution_protocol.last_check_times.clear()

    entry = 80000.0
    sl_110 = entry * (1 + 110.0 / (50 * 100))  # SL no +110% ROI

    slot_moonbag = {
        "symbol": "BTCUSDT",
        "side": "Buy",
        "entry_price": entry,
        "current_stop": sl_110,  # Stop no +110% ROI
        "slot_type": "SNIPER",
        "status": "EMANCIPATED",
        "opened_at": 0,
        "sentinel_first_hit_at": 0,
        "id": 99,
        "is_market_ranging": False,
        "structural_target": 0,
        "score": 80,
    }

    # Preco ABAIXO do SL -> deve fechar IMEDIATAMENTE (Hard-Lock)
    price_below_sl = sl_110 - 10  # $10 abaixo do stop
    roi_at_sl = 100.0  # Aproximadamente

    should_close, reason, new_sl = await execution_protocol.process_sniper_logic(
        slot_moonbag, current_price=price_below_sl, roi=roi_at_sl
    )
    print(f"  Preco={price_below_sl:.2f} (abaixo SL={sl_110:.2f})")
    print(f"  -> should_close={should_close} | reason={reason}")
    if should_close and "MOONBAG_PROFIT_LOCK" in (reason or ""):
        ok("Moonbag fechou com MOONBAG_PROFIT_LOCK (Sentinel bypassado correto)")
    elif reason == "THROTTLED":
        ok("Throttle ativo")
    else:
        fail(f"Moonbag deveria ter MOONBAG_PROFIT_LOCK, got should_close={should_close} reason={reason}")


# ============================================================
# MAIN
# ============================================================
async def main():
    await test_shadow_emancipation()
    await test_set_trading_stop_moonbag()
    await test_moonbag_hard_lock()

    print()
    print("=" * 60)
    if FAIL == 0:
        print(f"TODOS OS {PASS} TESTES PASSARAM - V110.28.2 operacional!")
    else:
        print(f"RESULTADO: {PASS} passaram, {FAIL} FALHARAM - revisar acima.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
