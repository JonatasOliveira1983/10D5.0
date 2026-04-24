
import asyncio
from services.firebase_service import firebase_service

async def cleanup_duplicates():
    print("🚀 Iniciando Limpeza de Histórico Duplicado...")
    await firebase_service.initialize()
    
    if not firebase_service.db:
        print("❌ Erro ao conectar ao Firebase.")
        return

    # 1. Buscar trades de LTCUSDT
    docs = firebase_service.db.collection("trade_history").where("symbol", "==", "LTCUSDT.P").stream()
    
    trades = []
    for d in docs:
        t = d.to_dict()
        t['doc_id'] = d.id
        trades.append(t)
    
    # Se não achar com .P, tenta sem
    if not trades:
        docs = firebase_service.db.collection("trade_history").where("symbol", "==", "LTCUSDT").stream()
        for d in docs:
            t = d.to_dict()
            t['doc_id'] = d.id
            trades.append(t)

    print(f"🔍 Encontrados {len(trades)} registros de LTCUSDT.")
    
    if len(trades) <= 1:
        print("✅ Nenhuma duplicidade óbvia encontrada (1 ou 0 registros).")
        return

    # 2. Identificar duplicatas por PnL e Fechamento (aproximado)
    # Como não tínhamos orderId antes, vamos usar PnL e close_time
    seen = {} # {(pnl, close_time): doc_id}
    to_delete = []

    for t in trades:
        pnl = t.get('pnl')
        close_time = t.get('closed_at') or t.get('close_time')
        key = (pnl, close_time)
        
        if key in seen:
            print(f"🗑️ Duplicata detectada: DOC_ID {t['doc_id']} (Igual a {seen[key]})")
            to_delete.append(t['doc_id'])
        else:
            seen[key] = t['doc_id']

    # 3. Executar deleção
    if not to_delete:
        print("✨ Nenhuma duplicata exata (PnL + Tempo) encontrada.")
    else:
        print(f"🔥 Deletando {len(to_delete)} registros duplicados...")
        for doc_id in to_delete:
            firebase_service.db.collection("trade_history").document(doc_id).delete()
            print(f"✅ Deletado: {doc_id}")
        
    print("🏁 Limpeza concluída.")

if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())
