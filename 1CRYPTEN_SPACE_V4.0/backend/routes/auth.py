from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from services.auth_service import auth_service

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    if auth_service.verify_password(request.password):
        token = auth_service.create_session()
        return {"status": "SUCCESS", "token": token}
    else:
        raise HTTPException(status_code=401, detail="Senha incorreta")

@router.get("/verify")
async def verify(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")
    
    token = authorization.split(" ")[1]
    if auth_service.is_token_valid(token):
        return {"status": "VALID"}
    else:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

@router.post("/logout")
async def logout(authorization: str = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        auth_service.revoke_session(token)
    return {"status": "SUCCESS"}
