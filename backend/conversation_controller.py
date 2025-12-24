from __future__ import annotations
import uuid
from database import Database
from ai_service import AIService

class ConversationController:
    def __init__(self, database: Database, aiService: AIService, messageController=None):
        self.database = database
        self.aiService = aiService
        self.messageController = messageController

    def createConversation(self, userId: str):
        if self.database.countConversations(userId) >= 50:
            raise ValueError("You have reached the maximum of 50 conversations. Please delete old conversations to create new ones.")
        
        conversationId = self.database.saveConversation(userId, None)
        return {"conversationId": conversationId}

    def getHistory(self, userId: str):
        items = self.database.findAllConversations(userId)
        return [{
            "conversationId": c.conversationId,
            "title": c.title,
            "messageCount": c.messageCount,
            "createdAt": c.createdAt.isoformat(),
        } for c in items]

    def getDetails(self, conversationId: str):
        c = self.database.findConversation(conversationId)
        msgs = self.database.findMessages(conversationId)
        return {
            "conversationId": c.conversationId,
            "title": c.title,
            "messages": [{
                "senderId": m.senderId,
                "content": m.content,
                "timestamp": m.timestamp.isoformat()
            } for m in msgs]
        }

    def continueConversation(self, conversationId: str):
        return self.getDetails(conversationId)

    def delete(self, conversationId: str):
        self.database.deleteMessages(conversationId)
        self.database.deleteConversation(conversationId)
        return {"ok": True}

    def processFirstMessage(self, text: str):
        return self.aiService.generateTitle(text)

    def generateSessionId(self):
        return str(uuid.uuid4())