from fastapi import APIRouter, Depends, Header, HTTPException, Request
import logging
from config import settings

router = APIRouter(prefix="", tags=["Vault"])
logger = logging.getLogger("1CRYPTEN-VAULT")

def get_services():
    from services.vault_service import vault_service
    from services.bankroll import bankroll_manager
    return vault_service, bankroll_manager

async def verify_api_key(x_api_key: str = Header(None)):
    if settings.DEBUG:
        return True
    if x_api_key != settings.ADMIN_API_KEY:
        logger.warning(f"🔒 Security Alert: Unauthorized access attempt in Vault Route")
        raise HTTPException(status_code=403, detail="Acesso Proibido: Chave de API Inválida")
    return True

@router.get("/api/vault/status")
async def get_vault_status():
    vault_service, _ = get_services()
    try:
        status = await vault_service.get_cycle_status()
        calc = await vault_service.calculate_withdrawal_amount()
        return {**status, "recommended_withdrawal": calc.get("recommended_20pct", 0)}
    except Exception as e:
        logger.error(f"Error fetching vault status: {e}")
        return {"error": str(e)}

@router.get("/api/vault/cycle")
async def get_vault_cycle():
    vault_service, _ = get_services()
    try: return await vault_service.get_cycle_status()
    except Exception as e:
        logger.error(f"Error fetching vault cycle: {e}")
        return {"cycle_number": 1, "used_symbols_in_cycle": [], "cycle_start_bankroll": 0, "total_trades_cycle": 0}

@router.get("/api/vault/history")
async def get_vault_history(limit: int = 20):
    vault_service, _ = get_services()
    try: return await vault_service.get_withdrawal_history(limit=limit)
    except Exception as e:
        logger.error(f"Error fetching vault history: {e}")
        return []

@router.post("/api/vault/withdraw")
async def register_withdrawal(payload: dict):
    vault_service, _ = get_services()
    amount = payload.get("amount", 0)
    if amount <= 0: return {"error": "Amount must be greater than 0"}
    try:
        success = await vault_service.execute_withdrawal(float(amount))
        return {"status": "success", "amount": amount} if success else {"status": "error", "message": "Failed to register withdrawal"}
    except Exception as e:
        logger.error(f"Error registering withdrawal: {e}")
        return {"error": str(e)}

@router.post("/api/vault/new-cycle")
async def start_new_cycle():
    vault_service, _ = get_services()
    try:
        result = await vault_service.start_new_cycle()
        return {"status": "success", "cycle": result}
    except Exception as e:
        logger.error(f"Error starting new cycle: {e}")
        return {"error": str(e)}

@router.post("/panic", dependencies=[Depends(verify_api_key)])
async def panic_button():
    _, bankroll_manager = get_services()
    try: return await bankroll_manager.emergency_close_all()
    except Exception as e:
        logger.error(f"Panic button error: {e}")
        return {"status": "error", "message": str(e)}
