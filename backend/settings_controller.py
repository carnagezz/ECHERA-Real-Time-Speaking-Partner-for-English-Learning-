from __future__ import annotations
from database import Database

class SettingsController:
    def __init__(self, database: Database):
        self.database = database

    def loadVoiceSettings(self, userId: str):
        voice = self.database.getVoicePreference(userId)
        return {
            "selectedVoice": voice if voice else "default"
        }

    def saveVoicePreference(self, userId: str, voiceId: str):
        self.database.updateVoiceReference(userId, voiceId)
        return {"ok": True}