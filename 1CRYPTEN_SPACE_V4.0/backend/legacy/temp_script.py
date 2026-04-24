import asyncio, os, sys, json
sys.path.append(os.getcwd())
from services.firebase_service import firebase_service
async def main():
    await firebase_service.initialize()
    with open('temp_diag.txt', 'w', encoding='utf-8') as f:
        f.write('--- SLOT 3 DETAILS ---\n')
        slot3 = await firebase_service.get_slot(3)
        f.write(json.dumps(slot3, indent=2, ensure_ascii=False) + '\n')
        
        f.write('\n--- TRADE HISTORY (using method) ---\n')
        hist = await firebase_service.get_trade_history(limit=5)
        for h in hist: 
            f.write(f"{h.get('symbol')} {h.get('pnl')} {h.get('closed_at')}\n")
        
        if firebase_service.rtdb:
            f.write('\n--- RTDB vault_status ---\n')
            v_status = await asyncio.to_thread(firebase_service.rtdb.child('vault_status').get)
            f.write(json.dumps(v_status, indent=2, ensure_ascii=False) + '\n')
            
            f.write('\n--- RTDB vault_history ---\n')
            v_hist = await asyncio.to_thread(firebase_service.rtdb.child('vault_history').get)
            f.write(json.dumps(v_hist, indent=2, ensure_ascii=False) + '\n')
            
            f.write('\n--- RTDB system_state ---\n')
            s_state = await asyncio.to_thread(firebase_service.rtdb.child('system_state').get)
            f.write(json.dumps(s_state, indent=2, ensure_ascii=False) + '\n')

asyncio.run(main())
