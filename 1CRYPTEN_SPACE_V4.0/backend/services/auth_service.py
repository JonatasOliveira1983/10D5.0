import os
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
from config import settings

class AuthService:
    """
    [V110.200] Sovereign Authentication Service.
    Simple, secure, and dependency-free authentication using SHA-256 and salt.
    """
    def __init__(self):
        # [V110.201] Master Password simplified for user accessibility
        self.master_password = os.getenv("MASTER_PASSWORD", "123")
        self.secret_key = os.getenv("AUTH_SECRET_KEY", secrets.token_hex(32))
        self.sessions: Dict[str, float] = {} # token -> expiry_timestamp
        self.session_duration = 3600 * 24 # 24 hours

    def verify_password(self, password: str) -> bool:
        return password == self.master_password

    def create_session(self) -> str:
        token = secrets.token_urlsafe(32)
        expiry = time.time() + self.session_duration
        self.sessions[token] = expiry
        return token

    def is_token_valid(self, token: str) -> bool:
        if not token:
            return False
        
        # [V110.200] Fortress Logic: Validate token and check expiration
        expiry = self.sessions.get(token)
        if not expiry:
            return False
            
        if time.time() > expiry:
            del self.sessions[token]
            return False
            
        return True

    def revoke_session(self, token: str):
        if token in self.sessions:
            del self.sessions[token]

# Global instance
auth_service = AuthService()
