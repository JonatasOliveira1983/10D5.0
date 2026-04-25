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
    entry_margin = Column(Float, default=0.0)
    current_stop = Column(Float, default=0.0)
    initial_stop = Column(Float, default=0.0)
    target_price = Column(Float, default=0.0)
    liq_price = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    status_risco = Column(String, default="LIVRE")
    slot_type = Column(String, nullable=True) # [V110.137] BLITZ_30M ou SWING
    strategy = Column(String, nullable=True)
    pattern = Column(String, nullable=True)
    leverage = Column(Float, default=50.0)
    order_id = Column(String, nullable=True)
    genesis_id = Column(String, nullable=True)
    symbol_adx = Column(Float, default=0.0)
    market_regime = Column(String, nullable=True)
    unified_confidence = Column(Integer, default=50)
    fleet_intel = Column(JSON, nullable=True)
    pensamento = Column(String, nullable=True)
    timestamp_last_intel = Column(Float, default=0.0)
    sentinel_first_hit_at = Column(Float, default=0.0)
    timestamp_last_update = Column(Float, default=0.0)
    opened_at = Column(Float, default=0.0) # Timestamp float para paridade
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

class VaultCycle(Base):
    __tablename__ = "vault_cycles"
    id = Column(Integer, primary_key=True) # Always 1 for current cycle
    sniper_wins = Column(Integer, default=0)
    cycle_number = Column(Integer, default=1)
    cycle_profit = Column(Float, default=0.0)
    cycle_losses = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)
    in_admiral_rest = Column(Boolean, default=False)
    rest_until = Column(DateTime, nullable=True)
    vault_total = Column(Float, default=0.0)
    cautious_mode = Column(Boolean, default=False)
    min_score_threshold = Column(Integer, default=75)
    total_trades_cycle = Column(Integer, default=0)
    cycle_gains_count = Column(Integer, default=0)
    cycle_losses_count = Column(Integer, default=0)
    accumulated_vault = Column(Float, default=0.0)
    sniper_mode_active = Column(Boolean, default=True)
    used_symbols_in_cycle = Column(JSON, default=list)
    cycle_start_bankroll = Column(Float, default=0.0)
    next_entry_value = Column(Float, default=0.0)
    mega_cycle_wins = Column(Integer, default=0)
    mega_cycle_total = Column(Integer, default=0)
    mega_cycle_number = Column(Integer, default=1)
    mega_cycle_profit = Column(Float, default=0.0)
    order_ids_processed = Column(JSON, default=list)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OrderGenesis(Base):
    __tablename__ = "order_genesis"
    order_id = Column(String, primary_key=True) # Linked to Bybit OrderId
    genesis_id = Column(String, index=True)
    symbol = Column(String)
    side = Column(String)
    strategy = Column(String)
    data = Column(JSON) # Full intelligence payload
    timestamp = Column(DateTime, default=datetime.utcnow)

class SystemState(Base):
    __tablename__ = "system_state"
    key = Column(String, primary_key=True)
    data = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VaultWithdrawal(Base):
    __tablename__ = "vault_withdrawals"
    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    cycle_number = Column(Integer)
    destination = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DatabaseService:
    def __init__(self):
        # Em Railway, DATABASE_URL é provido automaticamente (postgres://...)
        # Precisamos converter para postgresql+asyncpg://...
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Fallback local para desenvolvimento
        if not db_url or "sua_url_do_postgres" in db_url:
            db_url = "sqlite+aiosqlite:///local_sniper.db"
            logger.warning("DATABASE_URL not found or placeholder detected. Using local SQLite.")

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
                    data.pop("id", None) # Evitar conflito de id
                    obj = BancaStatus(id=1, **data)
                    session.add(obj)
                else:
                    for key, value in data.items():
                        if hasattr(obj, key):
                            setattr(obj, key, value)
                await session.commit()
                
                # V110.175: Broadcast imediato do saldo para o Cockpit
                try:
                    from .websocket_service import websocket_service
                    await websocket_service.broadcast({"type": "BANCA_UPDATE", "data": data})
                except Exception as ws_err:
                    logger.error(f"Erro no broadcast de banca: {ws_err}")
                    
            except Exception as e:
                logger.error(f"Error updating banca status: {e}")

    async def get_banca_status(self):
        async with self.AsyncSessionLocal() as session:
            obj = await session.get(BancaStatus, 1)
            if obj:
                return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            return {"saldo_total": 100.0, "risco_real_percent": 0, "slots_disponiveis": 4, "status": "DEFAULT_BOOT"}

    # --- SLOTS ---
    async def update_slot(self, slot_id: int, data: dict):
        async with self.AsyncSessionLocal() as session:
            try:
                obj = await session.get(Slot, slot_id)
                if not obj:
                    data.pop("id", None) # Evitar conflito de id
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
                # V110.251: Garantir que timestamps sejam naive (sem timezone) para o Postgres
                now = datetime.utcnow()
                
                # [V110.256] GENESIS GUARD: genesis_id é obrigatório — gera fallback se ausente
                genesis_id = trade_data.get("genesis_id")
                if not genesis_id:
                    sym = trade_data.get("symbol", "UNK")
                    genesis_id = f"RECOVERY-{sym[:4].upper()}-{int(now.timestamp())}"
                    logger.warning(f"⚠️ [GENESIS-GUARD] genesis_id ausente para {sym}. Usando fallback: {genesis_id}")
                
                new_trade = TradeHistory(
                    order_id=str(trade_data.get("order_id") or f"ORD-{int(now.timestamp())}"),
                    genesis_id=genesis_id,
                    symbol=trade_data.get("symbol"),
                    side=trade_data.get("side"),
                    pnl=float(trade_data.get("pnl", 0)),
                    pnl_percent=float(trade_data.get("pnl_percent", 0)),
                    entry_price=float(trade_data.get("entry_price", 0)),
                    exit_price=float(trade_data.get("exit_price", 0)),
                    strategy=trade_data.get("strategy"),
                    close_reason=trade_data.get("close_reason"),
                    data=trade_data,
                    timestamp=now.replace(tzinfo=None)
                )
                session.add(new_trade)
                await session.commit()
                logger.info(f"✅ Trade logged in Postgres: {trade_data.get('symbol')}")
            except Exception as e:
                logger.error(f"❌ DATABASE LOG FAIL for {trade_data.get('symbol')}: {e}")
                # [V110.208] BLACK BOX EMERGENCY BACKUP
                try:
                    import json
                    backup_path = "emergency_trades.json"
                    entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "error": str(e),
                        "trade_data": trade_data
                    }
                    with open(backup_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry, default=str) + "\n")
                    logger.warning(f"🛡️ [BLACK BOX] Trade backed up to emergency file: {backup_path}")
                except Exception as fatal_e:
                    logger.critical(f"🚨 ABSOLUTE PERSISTENCE FAILURE: {fatal_e}")

    async def get_trade_history(self, limit: int = 50):
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(select(TradeHistory).order_by(desc(TradeHistory.timestamp)).limit(limit))
            trades = result.scalars().all()
            return [{c.name: getattr(t, c.name) for c in t.__table__.columns} for t in trades]

    # --- VAULT ---
    async def get_vault_cycle(self):
        async with self.AsyncSessionLocal() as session:
            obj = await session.get(VaultCycle, 1)
            if obj:
                res = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
                # Ensure JSON fields are returned as lists if they were None
                if res.get("used_symbols_in_cycle") is None: res["used_symbols_in_cycle"] = []
                if res.get("order_ids_processed") is None: res["order_ids_processed"] = []
                return res
            return None

    async def update_vault_cycle(self, data: dict):
        async with self.AsyncSessionLocal() as session:
            try:
                # V110.251: Strip timezone from all datetime values in data
                for key, value in data.items():
                    if isinstance(value, datetime) and value.tzinfo is not None:
                        data[key] = value.replace(tzinfo=None)
                
                obj = await session.get(VaultCycle, 1)
                if not obj:
                    obj = VaultCycle(id=1, **data)
                    session.add(obj)
                else:
                    for key, value in data.items():
                        if hasattr(obj, key):
                            setattr(obj, key, value)
                await session.commit()
            except Exception as e:
                logger.error(f"Error updating vault cycle: {e}")

    async def add_withdrawal(self, data: dict):
        async with self.AsyncSessionLocal() as session:
            try:
                new_w = VaultWithdrawal(**data)
                session.add(new_w)
                await session.commit()
            except Exception as e:
                logger.error(f"Error adding withdrawal: {e}")

    async def get_withdrawal_history(self, limit: int = 20):
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(select(VaultWithdrawal).order_by(desc(VaultWithdrawal.timestamp)).limit(limit))
            withdrawals = result.scalars().all()
            return [{c.name: getattr(w, c.name) for c in w.__table__.columns} for w in withdrawals]

    # --- ORDER GENESIS ---
    async def register_order_genesis(self, data: dict):
        async with self.AsyncSessionLocal() as session:
            try:
                order_id = str(data.get("order_id", "loc_" + str(int(datetime.utcnow().timestamp()))))
                obj = await session.get(OrderGenesis, order_id)
                if not obj:
                    obj = OrderGenesis(
                        order_id=order_id,
                        genesis_id=data.get("genesis_id"),
                        symbol=data.get("symbol"),
                        side=data.get("side"),
                        strategy=data.get("strategy"),
                        data=data
                    )
                    session.add(obj)
                else:
                    obj.data = data
                await session.commit()
            except Exception as e:
                logger.error(f"Error registering order genesis: {e}")

    async def get_order_genesis(self, order_id: str):
        async with self.AsyncSessionLocal() as session:
            obj = await session.get(OrderGenesis, str(order_id))
            if obj:
                return obj.data
            return None

    # --- SYSTEM STATE ---
    async def update_system_state(self, key: str, data: dict):
        async with self.AsyncSessionLocal() as session:
            try:
                obj = await session.get(SystemState, key)
                if not obj:
                    obj = SystemState(key=key, data=data)
                    session.add(obj)
                else:
                    obj.data = data
                await session.commit()
            except Exception as e:
                logger.error(f"Error updating system state for {key}: {e}")

    async def get_system_state(self, key: str):
        async with self.AsyncSessionLocal() as session:
            try:
                obj = await session.get(SystemState, key)
                if obj:
                    return obj.data
                return None
            except Exception as e:
                logger.error(f"Error getting system state for {key}: {e}")
                return None

database_service = DatabaseService()
