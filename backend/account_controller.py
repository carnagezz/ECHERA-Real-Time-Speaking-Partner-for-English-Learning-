from __future__ import annotations
from typing import Dict, Any
from database import Database
from auth_service import AuthService

class AccountController:
    def __init__(self, database: Database, authService: AuthService):
        self.database = database
        self.authService = authService

    def register(self, email: str, password: str, nickname: str):
        self.validateInput({"email": email, "password": password, "nickname": nickname})
        
        if self.database.checkEmailExists(email):
            raise ValueError("Email already registered")
        
        pwdHash = self.authService.hashPassword(password)
        userId = self.database.saveUser(email, pwdHash, nickname)
        return {"userId": userId}

    def login(self, email: str, password: str):
        self.validateInput({"email": email, "password": password})
        
        if not self.authService.authenticate(email, password):
            raise ValueError("Invalid email or password")
        
        user = self.database.findUserByEmail(email)
        session = self.authService.createSession(user.userId)
        return {"userId": user.userId, "sessionId": session.sessionId}

    def logout(self, sessionId: str):
        if sessionId:
            self.authService.endSession(sessionId)
        return {"ok": True}

    def updateProfile(self, userId: str, data: Dict[str, Any]):
        updateData = {}
        
        if "nickname" in data and data["nickname"]:
            self.validateInput({"nickname": data["nickname"]})
            updateData["nickname"] = data["nickname"]
        
        if "password" in data and data["password"]:
            self.validateInput({"password": data["password"]})
            updateData["passwordHash"] = self.authService.hashPassword(data["password"])
        
        if updateData:
            self.database.updateUser(userId, updateData)
        
        return {"ok": True}

    def validateInput(self, data: Dict[str, Any]):
        if "email" in data:
            email = (data.get("email") or "").strip()
            if not email or "@" not in email or "." not in email.split("@")[-1]:
                raise ValueError("Invalid email format")
        
        if "password" in data:
            pw = data.get("password") or ""
            if len(pw) < 8:  
                raise ValueError("Password must be at least 8 characters")
        
        if "nickname" in data:
            nick = (data.get("nickname") or "").strip()
            if len(nick) < 2:
                raise ValueError("Nickname must be at least 2 characters")
        
        return True
