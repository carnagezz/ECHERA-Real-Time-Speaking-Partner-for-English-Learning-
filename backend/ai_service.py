from __future__ import annotations
from typing import List
import requests
from models import Message

class AIService:
    def __init__(self, apiEndpoint: str):
        self.apiEndpoint = apiEndpoint

    def generateResponse(self, text: str, context: List[Message]) -> str:
        SYSTEM_PROMPT = (
            "You are talking with an English learner and they need your help practicing English. Make sure you respond with 2-3 sentences at max and do not use any emojis or symbols that aren't punctuation marks" \
            "Also, do not focus entirely on fixing the mistakes. Chatting and considering students' opinions are also priorities for you. Think of yourself as a friendly teacher who is students' favorite."
        )

        try: 
            msgs = []

            msgs = [{"role": "system", "content": SYSTEM_PROMPT}]

            for m in context[-6:]:
                role = "user" if m.senderId == "user" else "assistant"
                msgs.append({"role": role, "content": m.content})
            
            msgs.append({"role": "user", "content": text})
            
            payload = {
                "model": "gpt-oss:120b-cloud",
                "messages": msgs,
                "stream": False
            }
            
            r = requests.post(self.apiEndpoint, json=payload, timeout=8)
            r.raise_for_status()
            data = r.json()
            
            out = data.get("message", {}).get("content")
            if out:
                return out.strip()
            
            return "I understand. Please continue."
            
        except requests.exceptions.Timeout:
            return "I'm taking a bit longer to respond. Could you try again?"
        except requests.exceptions.ConnectionError:
            return "I couldn't reach the AI service, but I got your message."
        except Exception as e:
            print(f"AI Service Error: {str(e)}")
            return "I couldn't process that right now, but I'm here listening."

    def generateTitle(self, text: str) -> str:
        """Generate conversation title from first message using AI (FR9)"""
        t = (text or "").strip()
        if not t:
            return "New conversation"
        
        try:
            payload = {
                "model": "gpt-oss:120b-cloud",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a title generator. Given a message, create a short, concise title (maximum 4 words) that summarizes the topic. Respond with ONLY the title, nothing else."
                    },
                    {
                        "role": "user",
                        "content": f"Create a short title for this message: {t}"
                    }
                ],
                "stream": False
            }
            
            r = requests.post(self.apiEndpoint, json=payload, timeout=5)
            r.raise_for_status()
            data = r.json()
            
            title = data.get("message", {}).get("content", "").strip()
            
            title = title.strip('"').strip("'")
            
            if len(title) > 35:
                title = title[:32] + "..."
            
            return title if title else self._fallbackTitle(t)
            
        except Exception as e:
            print(f"AI Title Generation Error: {str(e)}")
            return self._fallbackTitle(t)
    
    def _fallbackTitle(self, text: str) -> str:
        """Fallback title generation if AI fails"""
        t = text.replace("\n", " ").strip()
        if len(t) > 31:
            return t[:28] + "..."
        return t

