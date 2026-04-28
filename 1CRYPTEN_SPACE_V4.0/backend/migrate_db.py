import asyncio
import os
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Carrega as variáveis do .env (Força override se já existir no ambiente)
load_dotenv(override=True)

# Adiciona o diretório atual ao path
sys.path.append(os.getcwd())

async def migrate():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL nao encontrada. Abortando migracao.")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"Conectando ao banco de dados para migracao...")
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
        ("unified_confidence", "INTEGER DEFAULT 50"),
        ("timestamp_last_update", "FLOAT DEFAULT 0.0"),
        ("is_ranging_sniper", "BOOLEAN DEFAULT FALSE"),
        ("v42_tag", "VARCHAR DEFAULT 'STANDARD'"),
        ("move_room_pct", "FLOAT DEFAULT 0.0"),
        ("is_reverse_sniper", "BOOLEAN DEFAULT FALSE"),
        ("rescue_activated", "BOOLEAN DEFAULT FALSE"),
        ("rescue_resolved", "BOOLEAN DEFAULT FALSE"),
        ("is_shadow_strike", "BOOLEAN DEFAULT FALSE"),
        ("is_spring_strike", "BOOLEAN DEFAULT FALSE"),
        ("score", "INTEGER DEFAULT 0")
    ]

    for col_name, col_type in slots_migrations:
        try:
            print(f"Tentando adicionar {col_name} a tabela slots...")
            async with engine.connect() as conn:
                await conn.execute(text(f"ALTER TABLE slots ADD COLUMN {col_name} {col_type}"))
                await conn.commit()
            print(f"Coluna {col_name} adicionada com sucesso.")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"Coluna {col_name} ja existe. Pulando.")
            else:
                print(f"Erro ao adicionar {col_name}: {e}")

    print("Migracao concluida!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
