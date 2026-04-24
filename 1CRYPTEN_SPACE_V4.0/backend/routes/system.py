from fastapi import APIRouter, Depends, Header, HTTPException, Request
import logging
import datetime
import os
from config import settings

router = APIRouter(prefix="/api", tags=["System"])
logger = logging.getLogger("1CRYPTEN-SYSTEM")

def get_services():
    from services.sovereign_service import sovereign_service
    from services.bybit_rest import bybit_rest_service
    from services.vault_service import vault_service
    from services.bankroll import bankroll_manager
    from services.execution_protocol import execution_protocol
    return sovereign_service, bybit_rest_service, vault_service, bankroll_manager, execution_protocol

async def verify_api_key(x_api_key: str = Header(None)):
    if settings.DEBUG:
        return True
    if x_api_key != settings.ADMIN_API_KEY:
        logger.warning(f"🔒 Security Alert: Unauthorized access attempt in System Route")
        raise HTTPException(status_code=403, detail="Acesso Proibido: Chave de API Inválida")
    return True

@router.get("/system/reset-bankroll")
async def reset_bankroll_get():
    """Versão GET para facilidade de uso via navegador."""
    return await reset_bankroll_action(100.0)

@router.post("/system/reset-bankroll", dependencies=[Depends(verify_api_key)])
async def reset_bankroll_post(payload: dict = None):
    amount = 100.0
    if payload and "amount" in payload:
        amount = float(payload["amount"])
    return await reset_bankroll_action(amount)

async def reset_bankroll_action(amount: float):
    # Imports internos para evitar circular dependency
    from services.sovereign_service import sovereign_service
    from services.database_service import database_service
    
    # 1. Firebase (se ativo)
    try:
        await sovereign_service.update_bankroll(amount)
    except: pass
    
    # 2. Postgres
    try:
        await database_service.update_banca_status({
            "saldo_total": amount,
            "risco_real_percent": 0.0,
            "slots_disponiveis": 4,
            "status": "OPERATIONAL"
        })
    except: pass
    
    return {"status": "success", "message": f"Bankroll reset to ${amount} in all layers."}

@router.get("/test")
async def test_connectivity():
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

@router.get("/debug/test")
async def debug_test():
    from main import VERSION
    return {"status": "ok", "message": f"{VERSION} Almirante Verified"}

@router.get("/health")
async def health_check():
    sovereign_service, bybit_rest_service, _, _, _ = get_services()
    from main import VERSION, DEPLOYMENT_ID, FRONTEND_DIR
    frontend_files = []
    if os.path.exists(FRONTEND_DIR):
        try: frontend_files = os.listdir(FRONTEND_DIR)
        except: frontend_files = ["Permission Error"]
    bybit_conn = False
    balance = 0.0
    if bybit_rest_service:
        try:
            bybit_conn = True 
            balance = bybit_rest_service.last_balance
        except: pass
    return {
        "status": "online", "version": VERSION, "deployment_id": DEPLOYMENT_ID,
        "bybit_connected": bybit_conn, "balance": balance,
        "frontend_path": FRONTEND_DIR, "frontend_found": os.path.exists(FRONTEND_DIR),
        "frontend_files": frontend_files,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

@router.get("/banca/data")
async def get_banca_data():
    sovereign_service, bybit_rest_service, _, _, _ = get_services()
    from services.database_service import database_service
    try:
        # 1. Tenta buscar no Postgres (Railway Native)
        status = await database_service.get_banca_status()
        
        # 2. Se o status for UNKNOWN ou saldo zerado, tenta o Firebase como fallback
        if not status or status.get("status") == "UNKNOWN" or status.get("saldo_total", 0) == 0:
            status = await sovereign_service.get_banca_status()
            
        # 3. Se ainda assim estiver zerado, busca saldo real na Bybit (se estiver em REAL mode)
        if not status or status.get("saldo_total", 0) == 0:
            equity = await bybit_rest_service.get_wallet_balance()
            return {"saldo_total": equity, "risco_real_percent": 0.0, "slots_disponiveis": 4, "status": "LIVE_FETCH"}
            
        return status
    except Exception as e:
        logger.error(f"Error fetching banca: {e}")
    return {"saldo_total": 0.0, "risco_real_percent": 0.0, "slots_disponiveis": 4, "status": "ERROR"}

@router.post("/banca/update", dependencies=[Depends(verify_api_key)])
async def update_banca(payload: dict):
    return {"status": "blocked", "message": "Banca fixa em $100 (modo PAPER). Atualização automática via PnL."}

@router.get("/banca-history")
async def get_banca_history(limit: int = 50):
    sovereign_service, _, _, _, _ = get_services()
    try: return await sovereign_service.get_banca_history(limit=limit)
    except Exception as e:
        logger.error(f"Error in banca history endpoint: {e}")
        return []

@router.get("/stats")
async def get_stats():
    sovereign_service, _, _, _, _ = get_services()
    try: return await sovereign_service.get_banca_status()
    except Exception as e:
        logger.error(f"Error in stats endpoint: {e}")
        return {"saldo_total": 0.0, "risco_real_percent": 0.0, "win_rate": 0.0}

@router.post("/system/re-sync", dependencies=[Depends(verify_api_key)])
async def trigger_re_sync():
    _, _, vault_service, bankroll_manager, _ = get_services()
    try:
        logger.info("Manual Re-Sync Triggered via API")
        await vault_service.sync_vault_with_history()
        await bankroll_manager.update_banca_status()
        return {"status": "success", "message": "Manual synchronization complete. RTDB updated."}
    except Exception as e:
        logger.error(f"Re-sync error: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/system/sniper-toggle", dependencies=[Depends(verify_api_key)])
async def toggle_sniper(payload: dict):
    _, _, vault_service, _, _ = get_services()
    enabled = payload.get("active", True)
    success = await vault_service.set_sniper_mode(enabled)
    return {"status": "success" if success else "error"}

@router.get("/system/settings")
async def get_system_settings():
    """V110.40: Retorna as configurações críticas para o Command Center PRO."""
    from main import VERSION
    return {
        "version": VERSION,
        "execution_mode": settings.BYBIT_EXECUTION_MODE,
        "max_slots": settings.MAX_SLOTS,
        "leverage": settings.LEVERAGE,
        "risk_cap": settings.RISK_CAP_PERCENT,
        "debug_mode": settings.DEBUG,
        "testnet": settings.BYBIT_TESTNET,
        "server_time": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
