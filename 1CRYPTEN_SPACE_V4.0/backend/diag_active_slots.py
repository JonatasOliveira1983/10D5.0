# -*- coding: utf-8 -*-
"""
Diagnostico completo das 4 posicoes ativas e simulacao da Escadinha
"""
import asyncio
import sys
sys.path.insert(0, ".")

SYMBOLS = ["WUSDT", "XRPUSDT", "DOTUSDT", "LINKUSDT"]
ENTRIES = {
    "WUSDT":    0.0137,
    "XRPUSDT":  1.34,
    "DOTUSDT":  1.28,
    "LINKUSDT": 9.01,
}
LEVERAGE = 50

def calc_sl_from_roi(entry, roi_pct, side="buy"):
    offset = roi_pct / (LEVERAGE * 100)
    if side == "buy":
        return entry * (1 + offset)
    return entry * (1 - offset)

def calc_roi(entry, price, side="buy"):
    if side == "buy":
        return ((price - entry) / entry) * LEVERAGE * 100
    return ((entry - price) / entry) * LEVERAGE * 100


async def main():
    from services.sovereign_service import sovereign_service
    from services.bybit_rest import bybit_rest_service
    from services.execution_protocol import execution_protocol

    # ---- FIREBASE SLOTS ----
    print("=" * 65)
    print("SLOTS NO FIREBASE")
    print("=" * 65)
    slots = await sovereign_service.get_active_slots()
    slot_map = {}
    for s in slots:
        raw_sym = (s.get("symbol") or "").replace(".P", "")
        if raw_sym in SYMBOLS:
            slot_map[raw_sym] = s
            cstop = s.get("current_stop", "N/A")
            print(f"  {raw_sym}:")
            print(f"    id={s.get('id')}  slot_type={s.get('slot_type')}  status={s.get('status')}")
            print(f"    entry_price={s.get('entry_price')}  current_stop={cstop}")
            print(f"    score={s.get('score')}  structural_target={s.get('structural_target')}")
            print()

    if not slot_map:
        print("  NENHUM SLOT ENCONTRADO no Firebase para os simbolos informados!")
        print()

    # ---- PAPER POSITIONS EM MEMORIA ----
    print("=" * 65)
    print("POSICOES NA MEMORIA (paper_positions + paper_moonbags)")
    print("=" * 65)
    all_paper = bybit_rest_service.paper_positions + bybit_rest_service.paper_moonbags
    mem_map = {}
    for p in all_paper:
        sym = (p.get("symbol") or "").replace(".P", "")
        if sym in SYMBOLS:
            mem_map[sym] = p
            print(f"  {sym}:")
            print(f"    avgPrice={p.get('avgPrice')}  stopLoss={p.get('stopLoss')}  status={p.get('status')}")
            print(f"    side={p.get('side')}  size={p.get('size')}  opened_at={p.get('opened_at')}")
            print(f"    slot_id={p.get('slot_id')}")
            print()

    if not mem_map:
        print("  NENHUMA POSICAO NA MEMORIA para esses simbolos!")
        print()

    # ---- SIMULACAO ESCADINHA ----
    print("=" * 65)
    print("SIMULACAO ESCADINHA DE ELITE PARA CADA SLOT")
    print("=" * 65)
    for sym in SYMBOLS:
        entry = ENTRIES[sym]
        slot = slot_map.get(sym, {})
        mem = mem_map.get(sym, {})
        slot_type = slot.get("slot_type") or mem.get("slot_type") or "SNIPER"
        current_stop = float(slot.get("current_stop") or mem.get("stopLoss") or 0)
        status = slot.get("status") or mem.get("status") or "N/A"

        in_escadinha = slot_type in ["TREND", "SWING", "SNIPER", "SCALP", "SHADOW"]
        is_monitored = sym in mem_map or sym in slot_map

        p70   = calc_sl_from_roi(entry, 70.0)    # preco para 70% ROI
        p110  = calc_sl_from_roi(entry, 110.0)   # preco para 110% ROI
        p150  = calc_sl_from_roi(entry, 150.0)   # preco para 150% ROI (emancipa)
        sl5   = calc_sl_from_roi(entry, 5.0)     # SL apos 70%
        sl80  = calc_sl_from_roi(entry, 80.0)    # SL apos 110%
        sl110 = calc_sl_from_roi(entry, 110.0)   # SL apos emancipacao

        print(f"  {sym}  (entry={entry}, slot_type={slot_type}, status={status})")
        print(f"    Monitorado na memoria: {'SIM' if is_monitored else 'NAO - PROBLEMA!'}")
        print(f"    Escadinha ativa:       {'SIM' if in_escadinha else 'NAO - slot_type nao suportado!'}")
        print(f"    current_stop atual:    {current_stop}")
        print()
        print(f"    [DEGRAU 1]  ROI 70%   -> preco = {p70:.6f}  => SL sobe para {sl5:.6f}  (+5% ROI - Risk Zero)")
        print(f"    [DEGRAU 2]  ROI 110%  -> preco = {p110:.6f}  => SL sobe para {sl80:.6f}  (+80% ROI - Profit Lock)")
        print(f"    [DEGRAU 3]  ROI 150%  -> preco = {p150:.6f}  => EMANCIPA, SL trava em {sl110:.6f}  (+110% ROI - Moonbag)")
        print(f"    [HARD-LOCK] Moonbag toca SL={sl110:.6f}  => Fecha atomico sem Sentinel")
        print()

    # ---- VERIFICACAO AO VIVO (test rapi do process_order_logic) ----
    print("=" * 65)
    print("TESTE AO VIVO: process_order_logic com ROI simulado de 155%")
    print("=" * 65)

    for sym in SYMBOLS:
        entry = ENTRIES[sym]
        slot_fb = slot_map.get(sym, {})
        mem = mem_map.get(sym, {})
        slot_type = slot_fb.get("slot_type") or "SNIPER"
        current_stop_val = float(slot_fb.get("current_stop") or mem.get("stopLoss") or entry * 0.98)
        price_155 = calc_sl_from_roi(entry, 155.0)

        slot_data = {
            "symbol": sym,
            "side": "Buy",
            "entry_price": entry,
            "current_stop": current_stop_val,
            "slot_type": slot_type,
            "status": slot_fb.get("status") or "IN_TRADE",
            "opened_at": 0,
            "sentinel_first_hit_at": 0,
            "structural_target": float(slot_fb.get("structural_target") or 0),
            "score": slot_fb.get("score") or 80,
            "id": slot_fb.get("id") or 0,
            "is_market_ranging": False,
        }

        execution_protocol.last_check_times.pop(sym, None)

        try:
            should_close, reason, new_sl = await execution_protocol.process_sniper_logic(
                slot_data, current_price=price_155, roi=155.0
            )
            print(f"  {sym} @ ROI=155%: should_close={should_close} | reason={reason} | new_sl={new_sl}")
        except Exception as e:
            print(f"  {sym}: ERRO -> {e}")

    print()
    print("=" * 65)
    print("DIAGNOSTICO CONCLUIDO")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
