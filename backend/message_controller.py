from __future__ import annotations
from database import Database
from ai_service import AIService
from nlp_engine import NLPEngine

class MessageController:
    def __init__(self, database: Database, aiService: AIService, mlEngine: NLPEngine):
        self.database = database
        self.aiService = aiService
        self.mlEngine = mlEngine
        self._activeConversationId = ""
        self._activeUserId = ""
        self._lastText = ""

    def _setActive(self, conversationId: str, userId: str):
        self._activeConversationId = conversationId
        self._activeUserId = userId

    def sendMessage(self, text: str):
        return self.processMessage(text)

    def receiveMessage(self, text: str):
        self._lastText = text
        return {"ok": True}

    def cancelInput(self):
        self._lastText = ""
        return {"ok": True}

    def validateMessage(self, text: str):
        t = (text or "").strip()
        if not t:
            raise ValueError("Cannot send empty message")
        if len(t) > 2000:
            raise ValueError("Message too long (max 2000 characters)")
        return True

    def prepareContext(self):
        if not self._activeConversationId:
            return []
        return self.database.getLastMessages(self._activeConversationId, 6)

    def retry(self):
        if not self._lastText:
            raise ValueError("Nothing to retry")
        return self.processMessage(self._lastText)

    def processMessage(self, text: str):
        if not self._activeConversationId:
            raise ValueError("No active conversation")
        
        if self.database.checkMessageLimit(self._activeConversationId) >= 100:
            raise ValueError("This conversation has reached the maximum of 100 message exchanges. Please start a new conversation to continue.")

        self.validateMessage(text)
        
        userMessageId = self.database.saveMessage(self._activeConversationId, text)

        context = self.prepareContext()
        
        aiText = self.aiService.generateResponse(text, context)
        self.database.saveMessage(self._activeConversationId, aiText)

        sc = self.mlEngine.analyzeText(text)
        
        tips = self.mlEngine.generateTips(text, sc)

        self.database.saveScores(userMessageId, sc)
        self.database.saveTips(userMessageId, tips)
        
        self.receiveMessage(text)

        return {
            "aiText": aiText,
            "scores": {
                "fluency": sc.fluency,
                "wordChoice": sc.wordChoice,
                "grammar": sc.grammar
            },
            "tips": tips
        }