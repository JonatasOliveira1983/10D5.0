import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.abspath('.'))

async def main():
    print("🚀 Iniciando limpeza de slots BTC duplicados...")
    try:
        from services.sovereign_service import sovereign_service
        from services.bybit_rest import bybit_rest_service
        
        await sovereign_service.initialize()
        await bybit_rest_service.initialize()
        
        # 1. Limpar RTDB/Firestore Slots 3 e 4
        print("🔍 Verificando slots 1-4 no RTDB e Firestore...")
        
        for i in range(1, 5):
            # Forçamos a limpeza se for BTC ou se quisermos garantir que o RTDB reflita o Firestore
            # Mas o foco do usuário é 3 e 4 com BTC duplicado.
            
            # Limpeza Direta no RTDB (Onde o problema foi visto)
            if sovereign_service.rtdb:
                print(f"📡 Verificando RTDB Slot {i}...")
                rtdb_slot = await asyncio.to_thread(sovereign_service.rtdb.child("live_slots").child(str(i)).get)
                if rtdb_slot:
                    sym = rtdb_slot.get('symbol', '')
                    if sym and ('BTC' in sym.upper()):
                        print(f"🧹 Limpando BTC do RTDB Slot {i} ({sym})...")
                        await asyncio.to_thread(sovereign_service.rtdb.child("live_slots").child(str(i)).set, {
                            "symbol": None, "status_risco": "LIVRE", "pnl_percent": 0
                        })
                else:
                    print(f"ℹ️ RTDB Slot {i} está vazio.")

            # Limpeza no Firestore (Persistence)
            print(f"🔥 Verificando Firestore Slot {i}...")
            # Forçamos o reset nos slots 3 e 4 de qualquer jeito para garantir
            if i in [3, 4]:
                await sovereign_service.update_slot(i, {
                    "symbol": None, 
                    "entry_price": 0, 
                    "current_stop": 0, 
                    "entry_margin": 0,
                    "status_risco": "LIVRE", 
                    "side": None, 
                    "pnl_percent": 0, 
                    "sl_phase": "IDLE"
                })
                print(f"✅ Slot {i} resetado no Firestore/RTDB via update_slot.")

        # 2. Limpar paper_positions na memória/disco se houver BTC
        print("📂 Verificando paper_storage.json...")
        if bybit_rest_service.execution_mode == "PAPER":
            initial_count = len(bybit_rest_service.paper_positions)
            bybit_rest_service.paper_positions = [
                p for p in bybit_rest_service.paper_positions 
                if p.get('symbol') not in ['BTCUSDT', 'BTCUSDT.P']
            ]
            if len(bybit_rest_service.paper_positions) < initial_count:
                print(f"🧹 Removidas {initial_count - len(bybit_rest_service.paper_positions)} posições de BTC do Paper State.")
                bybit_rest_service._save_paper_state()
                print("✅ paper_storage.json atualizado!")
            else:
                print("ℹ️ Nenhuma posição de BTC encontrada no Paper State.")

        print("\n✨ Limpeza concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a limpeza: {e}")

if __name__ == "__main__":
    asyncio.run(main())
