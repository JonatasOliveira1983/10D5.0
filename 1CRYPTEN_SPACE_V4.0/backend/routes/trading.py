from fastapi import APIRouter, Depends, Header, HTTPException, Request
from typing import Optional, List
import logging
import asyncio
import datetime
from config import settings

router = APIRouter(prefix="/api", tags=["Trading"])
logger = logging.getLogger("1CRYPTEN-TRADING")

# Imports lazy to avoid circular dependency if any
def get_services():
    from services.sovereign_service import sovereign_service
    from services.bybit_rest import bybit_rest_service
    from services.execution_protocol import execution_protocol
    from services.vault_service import vault_service
    from services.bankroll import bankroll_manager
    from services.bybit_ws import bybit_ws_service
    return sovereign_service, bybit_rest_service, execution_protocol, vault_service, bankroll_manager, bybit_ws_service

async def verify_api_key(x_api_key: str = Header(None)):
    if settings.DEBUG:
        return True
    if x_api_key != settings.ADMIN_API_KEY:
        logger.warning(f"🔒 Security Alert: Unauthorized access attempt in Trading Route")
        raise HTTPException(status_code=403, detail="Acesso Proibido: Chave de API Inválida")
    return True

@router.get("/slots")
async def get_slots():
    sovereign_service, bybit_rest_service, execution_protocol, _, _, bybit_ws_service = get_services()
    try:
        slots = await sovereign_service.get_active_slots()
        if slots:
            try:
                resp = await asyncio.to_thread(bybit_rest_service.session.get_tickers, category="linear")
                ticker_list = resp.get("result", {}).get("list", [])
                price_map = {t["symbol"]: float(t.get("lastPrice", 0)) for t in ticker_list}
            except Exception:
                price_map = {}

            for slot in slots:
                if not slot.get("qty") or float(slot.get("qty", 0)) <= 0 or not slot.get("entry_price") or float(slot.get("entry_price", 0)) <= 0:
                    slot.update({
                        "symbol": None,
                        "status_risco": "IDLE",
                        "visual_status": "SCANNING",
                        "score": 0,
                        "qty": 0,
                        "entry_price": 0,
                        "pnl_percent": 0,
                        "side": None,
                        "opened_at": 0,
                        "genesis_id": None
                    })
                    continue

                if slot.get("symbol") and slot.get("entry_price", 0) > 0:
                    slot_id = int(slot.get("id", 0))
                    slot["slot_type"] = "BLITZ" if slot_id <= 2 else "SWING"
                    entry = float(slot.get("entry_price", 0))
                    side = slot.get("side", "Buy")
                    sym_clean = bybit_rest_service._strip_p(slot["symbol"])
                    # [V110.350] High-Precision: Use WebSocket price first, fallback to REST ticker
                    ws_price = bybit_ws_service.get_current_price(sym_clean)
                    live_price = ws_price if ws_price > 0 else price_map.get(sym_clean, 0)
                    
                    if live_price > 0 and entry > 0:
                        # [V110.350] Use 50x leverage as requested by USER for visual parity
                        lev = float(slot.get("leverage", 50.0))
                        roi = execution_protocol.calculate_roi(entry, live_price, side, leverage=lev)
                        roi = max(-500, min(5000, roi))
                        slot["pnl_percent"] = round(roi, 1)
                    
                    roi = slot.get("pnl_percent", 0)
                    phase_info = execution_protocol.get_sl_phase_info(roi, slot_data=slot)
                    slot["sl_phase"] = phase_info["phase"]
                    slot["sl_phase_icon"] = phase_info["icon"]
                    slot["sl_phase_color"] = phase_info["color"]
                    slot["visual_status"] = phase_info["phase"]
                else:
                    slot["sl_phase"] = "IDLE"
                    slot["sl_phase_icon"] = "⏳"
                    slot["sl_phase_color"] = "gray"
            return slots
    except Exception as e:
        logger.error(f"Error fetching slots: {e}")
    
    return [{"id": i, "symbol": None, "entry_price": 0, "current_stop": 0, "side": None, "sl_phase": "IDLE", "sl_phase_icon": "⏳", "genesis_id": None} for i in range(1, 5)]

@router.get("/signals")
async def get_signals(min_score: int = 0, limit: int = 20):
    sovereign_service, _, _, _, _ = get_services()
    try:
        signals = await sovereign_service.get_recent_signals(limit=limit)
        filtered = [s for s in signals if s.get("score", 0) >= min_score]
        if not filtered:
             return [{
                "id": "forced_debug",
                "symbol": "BTCUSDT",
                "score": 95,
                "indicators": {"cvd": 12.5},
                "is_elite": True,
                "timestamp": "Now"
            }]
        return filtered
    except Exception as e:
        logger.error(f"Error fetching signals: {e}")
        return [{"id": "forced_debug", "symbol": "BTCUSDT", "score": 95, "indicators": {"cvd": 10.5}, "is_elite": True, "timestamp": "Now"}]

@router.get("/history")
async def get_history(limit: int = 50, last_timestamp: str = None, symbol: str = None, start_date: str = None, end_date: str = None):
    sovereign_service, _, _, _, _ = get_services()
    try:
        return await sovereign_service.get_trade_history(
            limit=limit, 
            last_timestamp=last_timestamp,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"Error fetching trade history: {e}")
        return []

@router.get("/history/stats")
async def get_history_stats(symbol: str = None, start_date: str = None, end_date: str = None):
    sovereign_service, _, _, _, _ = get_services()
    try:
        return await sovereign_service.get_trade_history_stats(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        logger.error(f"Error fetching trade stats: {e}")
        return {"total_count": 0, "total_pnl": 0.0}

@router.post("/history/report")
async def get_trade_report(payload: dict):
    trade_data = payload.get("trade_data")
    if not trade_data:
        return {"error": "Missing trade data"}
    
    symbol = trade_data.get("symbol", "Desconhecido")
    pnl = trade_data.get("pnl", 0)
    side = trade_data.get("side", "N/A")
    roi = trade_data.get("roi", 0)
    
    report = f"""**Telemetria de Combate: {symbol}**
Posição {side} encerrada com resultado de **${pnl:.2f}** ({roi:.2f}% ROI).
A justificativa primária de fechamento computada foi: `{trade_data.get('close_reason', 'N/A')}`.
A diretriz segue inalterada: Disciplina sobre a emoção."""
    return {"report": report}

@router.get("/moonbags")
async def get_moonbags(limit: int = 10):
    sovereign_service, _, _, _, _ = get_services()
    try:
        return await sovereign_service.get_moonbags(limit=limit)
    except Exception as e:
        logger.error(f"Error fetching moonbags: {e}")
        return []

@router.post("/nuke-paper")
async def nuke_paper_state():
    _, bybit_rest_service, _, _, bankroll_manager = get_services()
    from services.sovereign_service import sovereign_service
    cleared = []
    if bybit_rest_service:
        bybit_rest_service.paper_positions.clear()
        bybit_rest_service.paper_moonbags.clear()
        bybit_rest_service.paper_orders_history.clear()
        bybit_rest_service.paper_balance = 100.0
        if hasattr(bybit_rest_service, 'pending_closures'):
             bybit_rest_service.pending_closures.clear()
        if hasattr(bybit_rest_service, 'emancipating_symbols'):
             bybit_rest_service.emancipating_symbols.clear()
        cleared.append("RAM deep cleanup")
        bybit_rest_service._save_paper_state()
        cleared.append("disk-sync")
    if sovereign_service:
        for i in range(1, 5):
            try: await sovereign_service.hard_reset_slot(i, "NUKE_PAPER_API", pnl=0.0)
            except: pass
        try:
            await sovereign_service.update_banca_status({"saldo_total": 100.0, "lucro_acumulado": 0.0, "base_capital": 100.0})
            cleared.append("banca_status")
        except: pass
    return {"status": "success", "cleared": cleared}
