
import asyncio
import os
import sys

# Adiciona o diretório atual ao path para importar os serviços
sys.path.append(os.getcwd())

from services.firebase_service import firebase_service
from services.execution_protocol import execution_protocol

async def verify():
    print("--- Diagnostic: Missão Elite Count ---")
    await firebase_service.initialize()
    
    # Busca TODOS os trades sem limite
    docs = firebase_service.db.collection("trade_history").get()
    all_trades = [d.to_dict() for d in docs]
    
    print(f"Total trades found in Firestore: {len(all_trades)}")
    
    elites = 0
    scanned = 0
    errors = []
    
    valid_slots = ["SNIPER", "SWING", "SURF", "TREND", "SCALP"]
    skipped_by_slot = 0
    skipped_by_roi = 0
    
    for t in all_trades:
        scanned += 1
        st = t.get("slot_type")
        if st not in valid_slots:
            skipped_by_slot += 1
            continue
            
        roi_raw = t.get("pnl_percent")
        # ... logic to get roi_val ...
        try:
            roi_val = 0.0
            if roi_raw is not None:
                if isinstance(roi_raw, (int, float)):
                    roi_val = float(roi_raw)
                elif isinstance(roi_raw, str):
                    roi_val = float(roi_raw.replace('%', '').strip())
            else:
                entry = t.get("entry_price", 0)
                exit = t.get("exit_price", 0)
                if entry and exit:
                    roi_val = execution_protocol.calculate_roi(entry, exit, t.get("side", "Buy"))
            
            if roi_val >= 80.0:
                elites += 1
            else:
                skipped_by_roi += 1
        except:
            pass

    print(f"\n--- Analysis ---")
    print(f"Total Scanned: {scanned}")
    print(f"Skipped (Invalid Slot Type): {skipped_by_slot}")
    print(f"Skipped (ROI < 80%): {skipped_by_roi}")
    print(f"Elite Wins Found: {elites}")
    print(f"Errors found: {len(errors)}")
    if errors:
        for err in errors[:5]:
            print(f"  - {err}")

    # Verifica o documento current_cycle
    vault_doc = firebase_service.db.collection("vault_management").document("current_cycle").get()
    if vault_doc.exists:
        vdata = vault_doc.to_dict()
        print(f"\nVault Status (Firestore):")
        print(f"  mega_cycle_wins: {vdata.get('mega_cycle_wins')}")
        print(f"  total_trades_cycle: {vdata.get('total_trades_cycle')}")
    
if __name__ == "__main__":
    asyncio.run(verify())
