import asyncio
import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"

async def main():
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print("🧹 Conectando ao Banco de Dados...")
    async with AsyncSessionLocal() as session:
        # 1. Limpar FARTCOIN fantasma dos slots
        print("Verificando se o FARTCOIN é um fantasma no banco...")
        # Procurar o slot com FARTCOIN
        res = await session.execute(text("SELECT id, symbol FROM slots WHERE symbol LIKE '%FARTCOIN%'"))
        fart_slot = res.fetchone()
        
        if fart_slot:
            print(f"👻 Encontrado slot {fart_slot.id} com FARTCOIN. Resetando atômicamente...")
            await session.execute(text("""
                UPDATE slots 
                SET symbol = NULL, status_risco = 'LIVRE', pnl_percent = 0, pnl_usd = 0, 
                    entry_price = 0, current_stop = 0, target_price = 0, qty = 0, side = NULL,
                    order_id = NULL, genesis_id = NULL, timestamp_last_update = extract(epoch from now()),
                    pensamento = '🔄 PURGADO: Ordem fantasma removida'
                WHERE id = :slot_id
            """), {"slot_id": fart_slot.id})
            
            # Limpar moonbags também
            await session.execute(text("DELETE FROM moonbags WHERE symbol LIKE '%FARTCOIN%'"))
            
        # 2. Limpar Histórico Fantasma da Vault
        print("Limpando histórico de trades vazios/fantasmas na Vault...")
        result = await session.execute(text("DELETE FROM trade_history WHERE genesis_id LIKE 'RECOVERY-%' OR pnl = 0"))
        
        await session.commit()
        print(f"✅ {result.rowcount} trades fantasmas (RECOVERY/PNL $0) deletados do histórico.")
        
    print("🧹 Limpando posição residual na memória do PAPER...")
    paper_file = os.path.join(os.path.dirname(__file__), "..", "data", "paper_positions.json")
    if os.path.exists(paper_file):
        try:
            with open(paper_file, "r") as f:
                positions = json.load(f)
            
            new_positions = [p for p in positions if "FARTCOIN" not in p.get("symbol", "")]
            if len(new_positions) != len(positions):
                with open(paper_file, "w") as f:
                    json.dump(new_positions, f, indent=4)
                print("✅ Posição residual removida do arquivo paper_positions.json.")
        except Exception as e:
            print(f"Erro ao limpar json: {e}")

    print("🎉 Limpeza concluída. O Captain agora tem 1 slot a mais liberado e o Vault está impecável.")

if __name__ == "__main__":
    asyncio.run(main())
