from __future__ import annotations
from typing import List, Dict, Any
from database import Database
from models import Scores

class ProfileController:
    def __init__(self, database: Database):
        self.database = database

    def getStatistics(self, userId: str):
        scores = self.database.getAllScores(userId)
        
        msgs = self.database.getAllUserMessages(userId)
        
        convCount = self.database.getConversationCount(userId)
        
        info = self.database.getAccountInfo(userId)
        
        return {
            "avgFluency": self.calculateAverageFluency(scores),
            "avgWordChoice": self.calculateAverageWordChoice(scores),
            "avgGrammar": self.calculateAverageGrammar(scores),
            "messageCount": len(msgs),
            "conversationCount": convCount,
            "accountInfo": info
        }

    def calculateAverageFluency(self, scores: List[Scores]) -> float:
        if not scores:
            return 0.0
        return round(sum(s.fluency for s in scores) / len(scores), 1)

    def calculateAverageWordChoice(self, scores: List[Scores]) -> float:
        if not scores:
            return 0.0
        return round(sum(s.wordChoice for s in scores) / len(scores), 1)

    def calculateAverageGrammar(self, scores: List[Scores]) -> float:
        if not scores:
            return 0.0
        return round(sum(s.grammar for s in scores) / len(scores), 1)


