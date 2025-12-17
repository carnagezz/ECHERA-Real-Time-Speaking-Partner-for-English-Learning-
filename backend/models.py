from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class User:
    userId: str
    email: str
    passwordHash: str
    nickname: str
    selectedVoice: str
    createdAt: datetime

    def getUserId(self) -> str:
        return self.userId

    def getEmail(self) -> str:
        return self.email

    def getNickname(self) -> str:
        return self.nickname

    def setNickname(self, nickname: str):
        self.nickname = nickname

    def setPasswordHash(self, hash: str):
        self.passwordHash = hash


@dataclass
class Session:
    sessionId: str
    userId: str
    createdAt: datetime
    expiresAt: datetime
    invalidatedAt: Optional[datetime] = None

    def isValid(self) -> bool:
        """Check if session is still valid"""
        if self.invalidatedAt is not None:
            return False
        return datetime.utcnow() < self.expiresAt.replace(tzinfo=None)

    def invalidate(self):
        """Invalidate session"""
        self.invalidatedAt = datetime.utcnow()


@dataclass
class Conversation:
    conversationId: str
    userId: str
    title: str
    messageCount: int
    createdAt: datetime

    def getConversationId(self) -> str:
        return self.conversationId

    def getTitle(self) -> str:
        return self.title

    def setTitle(self, title: str):
        self.title = title

    def incrementMessageCount(self):
        self.messageCount += 1


@dataclass
class Message:
    messageId: str
    conversationId: str
    content: str
    senderId: str  # 'user' or 'ai'
    timestamp: datetime

    def getMessageId(self) -> str:
        return self.messageId

    def getContent(self) -> str:
        return self.content

    def getSender(self) -> str:
        return self.senderId


@dataclass
class Scores:
    fluency: int
    wordChoice: int
    grammar: int

    def getFluency(self) -> int:
        return self.fluency

    def getWordChoice(self) -> int:
        return self.wordChoice

    def getGrammar(self) -> int:
        return self.grammar


@dataclass
class Feedback:
    feedbackId: str
    messageId: str
    fluencyScore: int
    wordChoiceScore: int
    grammarScore: int
    feedbackTips: List[str]

    def getScores(self) -> Dict[str, Any]:
        return {
            "fluency": self.fluencyScore,
            "wordChoice": self.wordChoiceScore,
            "grammar": self.grammarScore,
        }

    def getFeedbackTips(self) -> List[str]:
        return list(self.feedbackTips)
