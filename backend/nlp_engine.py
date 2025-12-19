from __future__ import annotations
from typing import List
import spacy
from models import Scores

class NLPEngine:
    def __init__(self, apiEndpoint: str):
        self.apiEndpoint = apiEndpoint
        try:
            self._nlp = spacy.load("en_core_web_sm")
        except Exception:
            self._nlp = None

    def analyzeText(self, text: str) -> Scores:
        return Scores(
            fluency=self.calculateFluency(text),
            wordChoice=self.calculateWordChoice(text),
            grammar=self.calculateGrammar(text),
        )

    def calculateFluency(self, text: str) -> int:
        t = (text or "").strip()
        if not t or not self._nlp:
            return 0
        
        doc = self._nlp(t)
        
        sentences = list(doc.sents)
        if not sentences:
            return 0
        
        score = 50 
        
        if len(sentences) > 1:
            score += min(15, len(sentences) * 5)
        
        conjunctions = [token for token in doc if token.pos_ == "CCONJ" or token.pos_ == "SCONJ"]
        score += min(15, len(conjunctions) * 5)
        
        pos_patterns = set()
        for sent in sentences:
            pattern = tuple(token.pos_ for token in sent)
            pos_patterns.add(pattern)
        
        if len(pos_patterns) > 1:
            score += 10
        
        adverbs = [token for token in doc if token.pos_ == "ADV"]
        score += min(10, len(adverbs) * 3)
        
        return max(0, min(100, score))

    def calculateWordChoice(self, text: str) -> int:
        t = (text or "").strip()
        if not t or not self._nlp:
            return 0
        
        doc = self._nlp(t)
        
        if len(doc) == 0:
            return 0
        
        score = 40  
        
        lemmas = [token.lemma_.lower() for token in doc if token.is_alpha]
        if lemmas:
            diversity = len(set(lemmas)) / len(lemmas)
            score += int(20 * diversity)
        
        adjectives = [token for token in doc if token.pos_ == "ADJ"]
        score += min(15, len(adjectives) * 5)
        
        adverbs = [token for token in doc if token.pos_ == "ADV"]
        score += min(10, len(adverbs) * 4)
        
        entities = list(doc.ents)
        score += min(15, len(entities) * 8)
        
        return max(0, min(100, score))

    def calculateGrammar(self, text: str) -> int:
        t = (text or "").strip()
        if not t or not self._nlp:
            return 0
        
        doc = self._nlp(t)
        
        score = 100 
        
        sentences = list(doc.sents)
        for sent in sentences:
            first_token = sent[0]
            if first_token.text and first_token.text[0].islower():
                score -= 10
        
        for sent in sentences:
            last_token = sent[-1]
            if last_token.text not in [".", "!", "?"]:
                score -= 8
        
        has_subject = any(token.dep_ in ["nsubj", "nsubjpass"] for token in doc)
        has_verb = any(token.pos_ == "VERB" for token in doc)
        
        if not has_subject:
            score -= 15
        if not has_verb:
            score -= 15
        
        orphaned = sum(1 for token in doc if token.dep_ == "dep")
        score -= min(20, orphaned * 5)
        
        determiners = [token for token in doc if token.pos_ == "DET"]
        nouns = [token for token in doc if token.pos_ in ["NOUN", "PROPN"]]
        
        if nouns and not determiners:
            score -= 5
        
        return max(0, min(100, score))

    def generateScores(self) -> Scores:
        return Scores(0, 0, 0)

    def generateTips(self, text: str, scores: Scores) -> List[str]:
        if not text or not self._nlp:
            return ["Keep practicing your English skills!"]
        
        doc = self._nlp(text)
        tips = []
        
        if scores.grammar < 70:
            sentences = list(doc.sents)
            
            for sent in sentences:
                if sent[0].text and sent[0].text[0].islower():
                    tips.append("Remember to capitalize the first letter of sentences.")
                    break
            
            for sent in sentences:
                if sent[-1].text not in [".", "!", "?"]:
                    tips.append("End your sentences with proper punctuation (. ! ?).")
                    break
            
            has_subject = any(token.dep_ in ["nsubj", "nsubjpass"] for token in doc)
            has_verb = any(token.pos_ == "VERB" for token in doc)
            
            if not has_subject or not has_verb:
                tips.append("Make sure your sentences have both a subject and a verb.")
        elif scores.grammar >= 90:
            tips.append("Excellent grammar! Your sentence structure is very clear.")
        elif scores.grammar >= 70:
            tips.append("Good grammar! Just minor improvements needed.")
        
        if scores.wordChoice < 60:
            adjectives = [token for token in doc if token.pos_ == "ADJ"]
            adverbs = [token for token in doc if token.pos_ == "ADV"]
            
            if len(adjectives) == 0:
                tips.append("Try using adjectives to describe nouns (e.g., 'beautiful day', 'fast car').")
            
            if len(adverbs) == 0:
                tips.append("Use adverbs to modify verbs (e.g., 'speak clearly', 'run quickly').")
            
            lemmas = [token.lemma_.lower() for token in doc if token.is_alpha]
            if lemmas and len(set(lemmas)) / len(lemmas) < 0.7:
                tips.append("Try to use a wider variety of words instead of repeating the same ones.")
        elif scores.wordChoice >= 80:
            tips.append("Great vocabulary! Your word choice is sophisticated and varied.")
        elif scores.wordChoice >= 60:
            tips.append("Good word choice! Consider using more descriptive words.")
        
        if scores.fluency < 60:
            sentences = list(doc.sents)
            
            if len(sentences) <= 1:
                tips.append("Try expressing your thoughts in multiple sentences for better flow.")
            
            conjunctions = [token for token in doc if token.pos_ in ["CCONJ", "SCONJ"]]
            if len(conjunctions) == 0:
                tips.append("Connect your ideas using words like 'and', 'but', 'because', or 'however'.")
            
            adverbs = [token for token in doc if token.pos_ == "ADV"]
            if len(adverbs) == 0:
                tips.append("Add adverbs to make your expression more nuanced and fluent.")
        elif scores.fluency >= 80:
            tips.append("Excellent fluency! Your expression flows very naturally.")
        elif scores.fluency >= 60:
            tips.append("Good fluency! Your sentences connect well.")
        
        if not tips:
            avg_score = (scores.grammar + scores.wordChoice + scores.fluency) / 3
            if avg_score >= 85:
                tips.append("Outstanding! Your English skills are excellent across all areas.")
            elif avg_score >= 70:
                tips.append("Well done! You're communicating effectively in English.")
            else:
                tips.append("Keep practicing! You're making progress.")
        
        return tips[:3]  