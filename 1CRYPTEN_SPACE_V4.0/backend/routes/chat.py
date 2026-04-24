from fastapi import APIRouter, Depends, Header, HTTPException, Request
import logging
import time
import re
from config import settings

router = APIRouter(prefix="/api", tags=["Chat & IA"])
logger = logging.getLogger("1CRYPTEN-CHAT")

class SimpleRateLimiter:
    def __init__(self, requests: int, window: int):
        self.requests = requests
        self.window = window
        self.clients = {}
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        self.clients[client_ip] = [t for t in self.clients.get(client_ip, []) if now - t < self.window]
        if len(self.clients[client_ip]) < self.requests:
            self.clients[client_ip].append(now)
            return True
        return False

chat_limiter = SimpleRateLimiter(requests=10, window=60)

async def rate_limit(request: Request):
    if not chat_limiter.is_allowed(request.client.host):
        logger.warning(f"🚫 Rate Limit Triggered for IP: {request.client.host}")
        raise HTTPException(status_code=429, detail="Limite de requisições excedido.")
    return True

async def verify_api_key(x_api_key: str = Header(None)):
    if settings.DEBUG: return True
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Acesso Proibido")
    return True

def get_services():
    from services.agents.ai_service import ai_service
    from services.agents.jarvis_brain import jarvis_brain
    from services.firebase_service import firebase_service
    return ai_service, jarvis_brain, firebase_service

@router.post("/chat", dependencies=[Depends(rate_limit)])
async def chat_with_captain(payload: dict):
    ai_service, jarvis_brain, _ = get_services()
    user_msg = payload.get("message", "")
    if not user_msg: raise HTTPException(status_code=400, detail="Mensagem vazia")
    active_dims = jarvis_brain.detect_dimensions(user_msg)
    synthesis = jarvis_brain.get_synthesis_instruction(active_dims)
    response = await ai_service.generate_content(prompt=user_msg, system_instruction=synthesis)
    return {"response": response or "Interferência no sinal...", "context": {"active_dimensions": active_dims}}

@router.post("/chat/manual")
async def chat_manual(payload: dict):
    ai_service, jarvis_brain, _ = get_services()
    user_msg = payload.get("text", "")
    active_dims = jarvis_brain.detect_dimensions(user_msg)
    synthesis = jarvis_brain.get_synthesis_instruction(active_dims)
    response = await ai_service.generate_content(prompt=user_msg, system_instruction=synthesis)
    return {"response": response, "dimensions": active_dims}

@router.post("/chat/reset", dependencies=[Depends(verify_api_key)])
async def reset_chat_history():
    _, _, firebase_service = get_services()
    try:
        await firebase_service.clear_chat_history()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error resetting chat: {e}")
        return {"error": str(e)}

@router.get("/chat/status")
async def get_chat_status():
    return {"status": "online", "mode": "STABLE_NEURAL"}

@router.post("/tts", dependencies=[Depends(rate_limit)])
async def text_to_speech(payload: dict):
    text = payload.get("text", "")
    if not text: return {"error": "Nenhum texto"}
    try:
        import edge_tts
        return {"status": "success", "message": "Voz processada localmente"}
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        return {"error": str(e)}

@router.get("/tts/voices")
async def get_tts_voices():
    return {"voices": [{"id": "pt-BR-AntonioNeural", "name": "Antonio", "lang": "pt-BR", "gender": "Male"}], "default": "pt-BR-AntonioNeural"}

@router.get("/logs")
async def get_logs(limit: int = 50):
    _, _, firebase_service = get_services()
    try: return await firebase_service.get_recent_logs(limit=limit)
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return []
