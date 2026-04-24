import asyncio
import os
import json
import logging
from google.cloud import firestore
from services.firebase_service import firebase_service
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResetSystem")

async def reset_all():
    print("Iniciando o EXTERMÍNIO das Collections do Firebase para limpeza total (Banca = $100)...")
    
    # 1. Reset Banca Status to exactly 100 USD (no cumulative PnL)
    print("1. Resetando Banca para 100 dólares...")
    doc_ref = firebase_service.db.collection("banca_status").document("status")
    await asyncio.to_thread(doc_ref.set, {
        "id": "status",
        "configured_balance": 100.0,
        "saldo_total": 100.0,
        "risco_real_percent": 0.0,
        "slots_disponiveis": 4,
        "lucro_total_acumulado": 0.0,
        "lucro_ciclo": 0.0,
        "lucro_hoje": 0.0,
        "lucro_semana": 0.0,
        "lucro_mes": 0.0,
        "taxa_acerto": "0%",
        "winrate_ciclo": "0%"
    }, merge=True)

    # 2. Reset Active Slots
    print("2. Esvaziando Slots Ativos...")
    for i in range(1, 5):
        await firebase_service.free_slot(i, reason="Reset Global da IA Iniciado")

    # 3. Wipe Trade History
    print("3. Limpando Histórico de Operações (trade_history)...")
    docs = await asyncio.to_thread(firebase_service.db.collection("trade_history").get)
    deleted_hist = 0
    for doc in docs:
        await asyncio.to_thread(doc.reference.delete)
        deleted_hist += 1
    print(f"Apagadas {deleted_hist} ordens do histórico.")

    # 4. Wipe Moonbags
    print("4. Limpando Vault (Moonbags)...")
    docs = await asyncio.to_thread(firebase_service.db.collection("moonbags").get)
    deleted_moon = 0
    for doc in docs:
        await asyncio.to_thread(doc.reference.delete)
        deleted_moon += 1
    print(f"Apagadas {deleted_moon} moonbags ativas.")

    # 5. Local Paper Storage
    print("5. Resetando Arquivo Local de Simulação (Paper Storage)...")
    paper_file = os.path.join(os.path.dirname(__file__), 'paper_storage.json')
    if os.path.exists(paper_file):
        with open(paper_file, 'w') as f:
            json.dump({
                "balance": 100.0,
                "positions": [],
                "history": [],
                "moonbags": []
            }, f)
        print("Arquivo paper_storage.json foi recriado com Zero posições e 100 de balance.")
    
    # 6. Sincronizar RTDB com Firebase para a UI não dar glitch
    print("6. Sincronizando Interface Gráfica (RTDB)...")
    try:
        # Remover histórico do RTDB e resetar stats
        if firebase_service.rtdb:
            await asyncio.to_thread(firebase_service.rtdb.child("trade_history").delete)
            await asyncio.to_thread(firebase_service.rtdb.child("moonbag_vault").delete)
            await firebase_service.update_vault_pulse({
                "vault_total": 0,
                "cycle_profit": 0,
                "global_profit": 0,
                "wins": 0,
                "losses": 0,
                "winrate": 0,
                "consecutive_wins": 0
            })
            print("RTDB limpo com sucesso.")
    except Exception as e:
        print(f"Erro em limpar RTDB (Não crítico): {e}")

    print("====================================")
    print("RESET COMPLETO CONCLUÍDO COM SUCESSO!")
    print("A Nuvem e os Arquivos estão zerados.")
    print("Reinicie o servidor principal.")

if __name__ == "__main__":
    asyncio.run(reset_all())
