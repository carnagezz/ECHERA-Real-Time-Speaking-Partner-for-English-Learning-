from __future__ import annotations
from datetime import datetime, timedelta
import os, uuid, hashlib, hmac
from database import Database
from models import Session

class AuthService:
    def __init__(self, database: Database):
        self.database = database
        self._pepper = os.getenv("AUTH_PEPPER", "pepper")

    def authenticate(self, email: str, password: str) -> bool:
        try:
            user = self.database.findUserByEmail(email)
        except Exception:
            return False
        
        return self.validatePassword(password, user.passwordHash)

    def hashPassword(self, password: str) -> str:
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            (password + self._pepper).encode("utf-8"),
            salt,
            120_000  
        )
        return salt.hex() + "$" + dk.hex()

    def validatePassword(self, password: str, hash: str) -> bool:
        try:
            salt_hex, dk_hex = hash.split("$", 1)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(dk_hex)
            
            got = hashlib.pbkdf2_hmac(
                "sha256",
                (password + self._pepper).encode("utf-8"),
                salt,
                120_000
            )
            
            return hmac.compare_digest(got, expected)
        except Exception:
            return False

    def createSession(self, userId: str) -> Session:
        sessionId = str(uuid.uuid4())
        createdAt = datetime.utcnow()
        expiresAt = createdAt + timedelta(days=7)  
        
        self.database._saveSession(sessionId, userId, createdAt, expiresAt)
        
        return Session(
            sessionId=sessionId,
            userId=userId,
            createdAt=createdAt,
            expiresAt=expiresAt
        )

    def endSession(self, sessionId: str):
        self.database._invalidateSession(sessionId)