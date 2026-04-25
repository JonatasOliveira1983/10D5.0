import asyncio
import os
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Adiciona o diretório atual ao path
sys.path.append(os.getcwd())

async def migrate():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL não encontrada. Abortando migração.")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

    print(f"📡 Conectando ao banco de dados para migração...")
    engine = create_async_engine(db_url)

    # Lista de colunas para adicionar à tabela 'slots'
    slots_migrations = [
        ("entry_margin", "FLOAT DEFAULT 0.0"),
        ("fleet_intel", "JSON"),
        ("pensamento", "TEXT"),
        ("timestamp_last_intel", "FLOAT DEFAULT 0.0"),
        ("sentinel_first_hit_at", "FLOAT DEFAULT 0.0"),
        ("opened_at", "FLOAT DEFAULT 0.0"),
        ("symbol_adx", "FLOAT DEFAULT 0.0"),
        ("market_regime", "VARCHAR"),
        ("unified_confidence", "INTEGER DEFAULT 50")
    ]

    async with engine.begin() as conn:
        for col_name, col_type in slots_migrations:
            try:
                print(f"🛠️ Tentando adicionar {col_name} à tabela slots...")
                await conn.execute(text(f"ALTER TABLE slots ADD COLUMN {col_name} {col_type}"))
                print(f"✅ Coluna {col_name} adicionada com sucesso.")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"ℹ️ Coluna {col_name} já existe. Pulando.")
                else:
                    print(f"⚠️ Erro ao adicionar {col_name}: {e}")

    print("🏁 Migração concluída!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
