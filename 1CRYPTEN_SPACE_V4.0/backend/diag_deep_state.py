# -*- coding: utf-8 -*-
"""
Verifica o estado real: Firebase RTDB, Firestore e paper_state.json
"""
import asyncio, sys, json, os
sys.path.insert(0, ".")

SYMBOLS = ["WUSDT", "XRPUSDT", "DOTUSDT", "LINKUSDT"]

async def main():
    from services.sovereign_service import sovereign_service
    from services.bybit_rest import bybit_rest_service

    # 1. Slots brutos no RTDB
    print("=" * 65)
    print("SLOTS BRUTOS NO RTDB (todos os slots)")
    print("=" * 65)
    try:
        raw = sovereign_service.rtdb.child("slots").get()
        if raw:
            for slot_id, data in raw.items():
                sym = data.get("symbol") if isinstance(data, dict) else "?"
                ep  = data.get("entry_price") if isinstance(data, dict) else "?"
                st  = data.get("status") if isinstance(data, dict) else "?"
                cs  = data.get("current_stop") if isinstance(data, dict) else "?"
                stype = data.get("slot_type") if isinstance(data, dict) else "?"
                print(f"  Slot {slot_id}: sym={sym} entry={ep} status={st} stop={cs} type={stype}")
        else:
            print("  RTDB slots vazio!")
    except Exception as e:
        print(f"  RTDB erro: {e}")

    # 2. paper_state.json
    print()
    print("=" * 65)
    print("PAPER_STATE.JSON (posicoes salvas em disco)")
    print("=" * 65)
    paper_paths = [
        "paper_state.json",
        ".paper_state.json",
        "paper_state_v110.json",
    ]
    found_paper = False
    for p in paper_paths:
        if os.path.exists(p):
            found_paper = True
            print(f"  Arquivo: {p}")
            with open(p, "r") as f:
                data = json.load(f)
            positions = data.get("positions", [])
            moonbags = data.get("moonbags", [])
            balance = data.get("balance", "N/A")
            print(f"  Balance: {balance}")
            print(f"  Positions ({len(positions)}):")
            for pos in positions:
                print(f"    {pos.get('symbol')}: avgPrice={pos.get('avgPrice')} stopLoss={pos.get('stopLoss')} status={pos.get('status')} size={pos.get('size')}")
            print(f"  Moonbags ({len(moonbags)}):")
            for mb in moonbags:
                print(f"    {mb.get('symbol')}: avgPrice={mb.get('avgPrice')} stopLoss={mb.get('stopLoss')} status={mb.get('status')}")
            break
    if not found_paper:
        print("  Nenhum paper_state.json encontrado!")

    # 3. Memoria viva do bybit_rest_service
    print()
    print("=" * 65)
    print("MEMORIA VIVA DO BYBIT_REST_SERVICE")
    print("=" * 65)
    print(f"  paper_balance: {bybit_rest_service.paper_balance}")
    print(f"  paper_positions ({len(bybit_rest_service.paper_positions)}):")
    for p in bybit_rest_service.paper_positions:
        print(f"    {p.get('symbol')}: avgPrice={p.get('avgPrice')} stopLoss={p.get('stopLoss')} status={p.get('status')}")
    print(f"  paper_moonbags ({len(bybit_rest_service.paper_moonbags)}):")
    for m in bybit_rest_service.paper_moonbags:
        print(f"    {m.get('symbol')}: avgPrice={m.get('avgPrice')} stopLoss={m.get('stopLoss')} status={m.get('status')}")

    # 4. Firestore slots
    print()
    print("=" * 65)
    print("FIRESTORE SLOTS (colecao sniper_slots)")
    print("=" * 65)
    try:
        fs_docs = sovereign_service.db.collection("sniper_slots").stream()
        found_fs = False
        for doc in fs_docs:
            d = doc.to_dict()
            sym = d.get("symbol")
            ep  = d.get("entry_price")
            st  = d.get("status")
            cs  = d.get("current_stop")
            stype = d.get("slot_type")
            if ep and float(ep) > 0:
                found_fs = True
                print(f"  {sym}: entry={ep} status={st} stop={cs} type={stype} id={doc.id}")
        if not found_fs:
            print("  Nenhum slot com entry_price > 0 no Firestore!")
    except Exception as e:
        print(f"  Firestore erro: {e}")

    print()
    print("=" * 65)
    print("DIAGNOSTICO CONCLUIDO")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(main())
