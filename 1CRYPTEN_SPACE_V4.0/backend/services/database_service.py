# 1CRYPTEN_SPACE_V4.0 - V110.175 Database Service (Railway/Postgres)
import os
import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, desc, select, update, delete
from config import settings

logger = logging.getLogger("DatabaseService")

Base = declarative_base()

class BancaStatus(Base):
    __tablename__ = "banca_status"
    id = Column(Integer, primary_key=True)
    saldo_total = Column(Float, default=0.0)
    risco_real_percent = Column(Float, default=0.0)
    slots_disponiveis = Column(Integer, default=4)
    status = Column(String, default="IDLE")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Slot(Base):
    __tablename__ = "slots"
    id = Column(Integer, primary_key=True) # 1, 2, 3, 4
    symbol = Column(String, nullable=True)
    side = Column(String, nullable=True)
    qty = Column(Float, default=0.0)
    entry_price = Column(Float, default=0.0)
    current_stop = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    status_risco = Column(String, default="LIVRE")
    strategy = Column(String, nullable=True)
    strategy_label = Column(String, nullable=True)
    genesis_id = Column(String, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TradeHistory(Base):
    __tablename__ = "trade_history"
    id = Column(Integer, primary_key=True)
    order_id = Column(String, index=True)
    genesis_id = Column(String, index=True)
    symbol = Column(String)
    side = Column(String)
    pnl = Column(Float)
    pnl_percent = Column(Float)
    entry_price = Column(Float)
    exit_price = Column(Float)
    strategy = Column(String)
    close_reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON) # Metadados completos (Librarian, Oracle, etc)

class Moonbag(Base):
    __tablename__ = "moonbags"
    uuid = Column(String, primary_key=True)
    symbol = Column(String)
    side = Column(String)
    qty = Column(Float)
    entry_price = Column(Float)
    current_stop = Column(Float)
    pnl_percent = Column(Float)
    promoted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DatabaseService:
    def __init__(self):
        # Em Railway, DATABASE_URL é provido automaticamente (postgres://...)
        # Precisamos converter para postgresql+asyncpg://...
        db_url = os.getenv("DATABASE_URL")
        if db_url and db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        
        # Fallback local para desenvolvimento
        if not db_url:
            db_url = "sqlite+aiosqlite:///local_sniper.db"
            logger.warning("DATABASE_URL not found. Using local SQLite.")

        self.engine = create_async_engine(db_url, echo=False)
        self.AsyncSessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.is_active = False

    async def initialize(self):
        """Inicializa as tabelas no banco de dados."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            self.is_active = True
            logger.info("✅ Database Service initialized successfully (Postgres/Railway).")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Database: {e}")

    async def get_session(self):
        return self.AsyncSessionLocal()

    # --- BANCA STATUS ---
    async def update_banca_status(self, data: dict):
        async with self.AsyncSessionLocal() as session:
            try:
                # Sempre ID 1 para banca única
                obj = await session.get(BancaStatus, 1)
                if not obj:
                    obj = BancaStatus(id=1, **data)
                    session.add(obj)
                else:
                    for key, value in data.items():
                        setattr(obj, key, value)
                await session.commit()
            except Exception as e:
                logger.error(f"Error updating banca status: {e}")

    async def get_banca_status(self):
        async with self.AsyncSessionLocal() as session:
            obj = await session.get(BancaStatus, 1)
            if obj:
                return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            return {"saldo_total": 0, "risco_real_percent": 0, "slots_disponiveis": 4, "status": "UNKNOWN"}

    # --- SLOTS ---
    async def update_slot(self, slot_id: int, data: dict):
        async with self.AsyncSessionLocal() as session:
            try:
                obj = await session.get(Slot, slot_id)
                if not obj:
                    obj = Slot(id=slot_id, **data)
                    session.add(obj)
                else:
                    for key, value in data.items():
                        if hasattr(obj, key):
                            setattr(obj, key, value)
                await session.commit()
                
                # V110.175: Emitir update via WebSocket/Redis se disponível
                from .redis_service import redis_service
                await redis_service.publish_update("live_slots", {"slot_id": slot_id, "data": data})
                
            except Exception as e:
                logger.error(f"Error updating slot {slot_id}: {e}")

    async def get_active_slots(self):
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(select(Slot).order_by(Slot.id))
            slots = result.scalars().all()
            return [{c.name: getattr(s, c.name) for c in s.__table__.columns} for s in slots]

    # --- TRADE HISTORY ---
    async def log_trade(self, trade_data: dict):
        async with self.AsyncSessionLocal() as session:
            try:
                new_trade = TradeHistory(
                    order_id=str(trade_data.get("order_id")),
                    genesis_id=trade_data.get("genesis_id"),
                    symbol=trade_data.get("symbol"),
                    side=trade_data.get("side"),
                    pnl=float(trade_data.get("pnl", 0)),
                    pnl_percent=float(trade_data.get("pnl_percent", 0)),
                    entry_price=float(trade_data.get("entry_price", 0)),
                    exit_price=float(trade_data.get("exit_price", 0)),
                    strategy=trade_data.get("strategy"),
                    close_reason=trade_data.get("close_reason"),
                    data=trade_data
                )
                session.add(new_trade)
                await session.commit()
                logger.info(f"✅ Trade logged in Postgres: {trade_data.get('symbol')}")
            except Exception as e:
                logger.error(f"Error logging trade: {e}")

    async def get_trade_history(self, limit: int = 50):
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(select(TradeHistory).order_by(desc(TradeHistory.timestamp)).limit(limit))
            trades = result.scalars().all()
            return [{c.name: getattr(t, c.name) for c in t.__table__.columns} for t in trades]

database_service = DatabaseService()
