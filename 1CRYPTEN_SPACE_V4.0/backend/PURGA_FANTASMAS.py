import asyncio
import os
import sys
import logging
import time

# Adiciona o diretório atual ao sys.path para importar os serviços
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from services.firebase_service import firebase_service
from services.bybit_rest import bybit_rest_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PURGA_FANTASMAS")

async def run_purge():
    logger.info("🚀 [PURGA] Iniciando Protocolo de Limpeza Profunda (Moonbag Vault)...")
    
    # 1. Inicializar Conexões
    await firebase_service.initialize()
    if not firebase_service.is_active:
        logger.error("❌ Falha ao conectar ao Firebase. Abortando.")
        return

    # Garantir que estamos em modo REAL para a limpeza de produção
    if settings.BYBIT_EXECUTION_MODE != "REAL":
        logger.warning(f"⚠️ O modo de execução está definido como {settings.BYBIT_EXECUTION_MODE}. A purga só deve ser feita no modo REAL para limpar a produção.")
        confirm = input("Deseja continuar mesmo assim no modo PAPER? (s/n): ")
        if confirm.lower() != 's':
            return

    # 2. Buscar dados da Bybit
    logger.info("📡 Buscando posições ativas na Bybit...")
    real_positions = await bybit_rest_service.get_active_positions()
    active_symbols = {p['symbol'].replace('.P', '').upper() for p in real_positions}
    logger.info(f"✅ {len(active_symbols)} posições encontradas na corretora: {active_symbols}")

    # 3. Buscar Moonbags do Firestore
    logger.info("🌖 Buscando Moonbags no Vault do Firebase...")
    moonbags = await firebase_service.get_moonbags()
    logger.info(f"✅ {len(moonbags)} Moonbags encontradas no banco de dados.")

    purged_count = 0
    
    # 4. Auditoria e Limpeza
    for moon in moonbags:
        moon_id = moon.get("id")
        symbol = moon.get("symbol", "UNKNOWN").replace('.P', '').upper()
        entry_price = float(moon.get("entry_price", 0))
        
        is_orphan = symbol not in active_symbols
        is_corrupted = entry_price <= 0
        
        # [V110.125] CRITICAL: PnL absurda detectada
        # ROI irreal é um sinal claro de dado corrompido ou órfão que não foi limpo
        reason = ""
        if is_orphan: reason = "ÓRFÃ (Não existe na Bybit)"
        elif is_corrupted: reason = "CORROMPIDA (Entry Price <= 0)"
        
        if is_orphan or is_corrupted:
            logger.warning(f"🧹 [PURGA] Removendo {symbol} (ID: {moon_id}) | Motivo: {reason}")
            try:
                await firebase_service.remove_moonbag(moon_id, reason=f"PURGE_{reason.split()[0]}")
                purged_count += 1
            except Exception as e:
                logger.error(f"❌ Erro ao remover moonbag {moon_id}: {e}")

    logger.info(f"🏁 [PURGA] Concluída. Total de fantasmas limpos: {purged_count}")
    
    # Snapshot final da banca para garantir que a UI atualize
    try:
        balance = await bybit_rest_service.get_wallet_balance()
        await firebase_service.update_bankroll(balance)
        logger.info(f"💰 Banca atualizada: ${balance:.2f}")
    except Exception as e:
        logger.error(f"Erro ao atualizar banca final: {e}")

if __name__ == "__main__":
    asyncio.run(run_purge())
