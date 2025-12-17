from __future__ import annotations
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import psycopg2
import psycopg2.extras
from models import User, Conversation, Message, Scores

class Database:
    def __init__(self, connectionString: str):
        self.connectionString = connectionString

    @contextmanager
    def _conn(self):
        conn = psycopg2.connect(self.connectionString)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def saveUser(self, email: str, hash: str, nickname: str):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO users(email, "passwordHash", nickname) VALUES (%s,%s,%s) RETURNING "userId"',
                    (email, hash, nickname),
                )
                (userId,) = cur.fetchone()
                return str(userId)

    def findUserByEmail(self, email: str) -> User:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute('SELECT * FROM users WHERE "email"=%s', (email,))
                r = cur.fetchone()
                if not r:
                    raise ValueError("User not found")
                return User(
                    userId=str(r["userId"]),
                    email=r["email"],
                    passwordHash=r["passwordHash"],
                    nickname=r["nickname"],
                    selectedVoice=r["selectedVoice"],
                    createdAt=r["createdAt"],
                )

    def updateUser(self, userId: str, data: Dict[str, Any]):
        if not data:
            return
        
        allowed = {"email", "passwordHash", "nickname", "selectedVoice"}
        sets = []
        vals = []
        
        for k, v in data.items():
            if k in allowed and v is not None:
                sets.append(f'"{k}"=%s')
                vals.append(v)
        
        if not sets:
            return
        
        vals.append(userId)
        q = 'UPDATE users SET ' + ",".join(sets) + ' WHERE "userId"=%s'
        
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(q, tuple(vals))

    def checkEmailExists(self, email: str) -> bool:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1 FROM users WHERE LOWER("email")=LOWER(%s)', (email,))
                return cur.fetchone() is not None

    def saveConversation(self, userId: str, sessionId: str):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO conversations("userId","sessionId","title","messageCount") VALUES (%s,%s,%s,%s) RETURNING "conversationId"',
                    (userId, sessionId, "New conversation", 0),
                )
                (cid,) = cur.fetchone()
                return str(cid)

    def findConversation(self, conversationId: str) -> Conversation:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute('SELECT * FROM conversations WHERE "conversationId"=%s', (conversationId,))
                r = cur.fetchone()
                if not r:
                    raise ValueError("Conversation not found")
                return Conversation(
                    conversationId=str(r["conversationId"]),
                    userId=str(r["userId"]),
                    title=r["title"],
                    messageCount=int(r["messageCount"]),
                    createdAt=r["createdAt"],
                )

    def findAllConversations(self, userId: str) -> List[Conversation]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    'SELECT * FROM conversations WHERE "userId"=%s ORDER BY "createdAt" DESC',
                    (userId,)
                )
                rows = cur.fetchall()
                return [Conversation(
                    conversationId=str(r["conversationId"]),
                    userId=str(r["userId"]),
                    title=r["title"],
                    messageCount=int(r["messageCount"]),
                    createdAt=r["createdAt"],
                ) for r in rows]

    def updateTitle(self, conversationId: str, title: str):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE conversations SET "title"=%s WHERE "conversationId"=%s',
                    (title, conversationId)
                )

    def countConversations(self, userId: str) -> int:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT COUNT(*) FROM conversations WHERE "userId"=%s', (userId,))
                (c,) = cur.fetchone()
                return int(c)

    def saveMessage(self, conversationId: str, text: str):
        last = self._get_last_sender(conversationId)
        senderId = "user" if (last is None or last == "ai") else "ai"
        
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO messages("conversationId","content","senderId") VALUES (%s,%s,%s) RETURNING "messageId"',
                    (conversationId, text, senderId),
                )
                (mid,) = cur.fetchone()
                
                cur.execute(
                    'UPDATE conversations SET "messageCount"="messageCount"+1 WHERE "conversationId"=%s',
                    (conversationId,)
                )
                
                return str(mid)

    def deleteConversation(self, conversationId: str):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM conversations WHERE "conversationId"=%s', (conversationId,))

    def findMessages(self, conversationId: str) -> List[Message]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    'SELECT * FROM messages WHERE "conversationId"=%s ORDER BY "timestamp" ASC',
                    (conversationId,)
                )
                rows = cur.fetchall()
                return [Message(
                    messageId=str(r["messageId"]),
                    conversationId=str(r["conversationId"]),
                    content=r["content"],
                    senderId=r["senderId"],
                    timestamp=r["timestamp"],
                ) for r in rows]

    def getLastMessages(self, conversationId: str, count: int) -> List[Message]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    'SELECT * FROM messages WHERE "conversationId"=%s ORDER BY "timestamp" DESC LIMIT %s',
                    (conversationId, count)
                )
                rows = cur.fetchall()
                rows.reverse()  
                return [Message(
                    messageId=str(r["messageId"]),
                    conversationId=str(r["conversationId"]),
                    content=r["content"],
                    senderId=r["senderId"],
                    timestamp=r["timestamp"],
                ) for r in rows]

    def deleteMessages(self, conversationId: str):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM messages WHERE "conversationId"=%s', (conversationId,))
                cur.execute(
                    'UPDATE conversations SET "messageCount"=0 WHERE "conversationId"=%s',
                    (conversationId,)
                )

    def checkMessageLimit(self, conversationId: str) -> int:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT COUNT(*) FROM messages WHERE "conversationId"=%s', (conversationId,))
                (c,) = cur.fetchone()
                return int(c)

    def saveScores(self, messageId: str, scores: Scores):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''INSERT INTO feedback("messageId","fluencyScore","wordChoiceScore","grammarScore")
                       VALUES (%s,%s,%s,%s)
                       ON CONFLICT ("messageId") DO UPDATE SET
                       "fluencyScore"=EXCLUDED."fluencyScore",
                       "wordChoiceScore"=EXCLUDED."wordChoiceScore",
                       "grammarScore"=EXCLUDED."grammarScore"''',
                    (messageId, scores.fluency, scores.wordChoice, scores.grammar),
                )

    def saveTips(self, messageId: str, tips: List[str]):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE feedback SET "feedbackTips"=%s WHERE "messageId"=%s',
                    (tips, messageId)
                )

    def getAllScores(self, userId: str) -> List[Scores]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''SELECT f."fluencyScore", f."wordChoiceScore", f."grammarScore"
                       FROM feedback f
                       JOIN messages m ON m."messageId"=f."messageId"
                       JOIN conversations c ON c."conversationId"=m."conversationId"
                       WHERE c."userId"=%s AND m."senderId"='user' ''',
                    (userId,),
                )
                rows = cur.fetchall()
                return [Scores(int(r[0]), int(r[1]), int(r[2])) for r in rows]

    def getAllUserMessages(self, userId: str) -> List[Message]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    '''SELECT m.*
                       FROM messages m
                       JOIN conversations c ON c."conversationId"=m."conversationId"
                       WHERE c."userId"=%s AND m."senderId"='user'
                       ORDER BY m."timestamp" ASC''',
                    (userId,),
                )
                rows = cur.fetchall()
                return [Message(
                    messageId=str(r["messageId"]),
                    conversationId=str(r["conversationId"]),
                    content=r["content"],
                    senderId=r["senderId"],
                    timestamp=r["timestamp"],
                ) for r in rows]

    def getConversationCount(self, userId: str) -> int:
        return self.countConversations(userId)

    def getAccountInfo(self, userId: str) -> Dict[str, Any]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    'SELECT "email","nickname","selectedVoice","createdAt" FROM users WHERE "userId"=%s',
                    (userId,)
                )
                r = cur.fetchone()
                if not r:
                    return {}
                return {
                    "email": r["email"],
                    "nickname": r["nickname"],
                    "selectedVoice": r["selectedVoice"],
                    "createdAt": r["createdAt"].isoformat()
                }

    def getVoicePreference(self, userId: str) -> str:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT "selectedVoice" FROM users WHERE "userId"=%s', (userId,))
                row = cur.fetchone()
                return row[0] if row and row[0] else "default"

    def updateVoiceReference(self, userId: str, voice: str):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE users SET "selectedVoice"=%s WHERE "userId"=%s',
                    (voice, userId)
                )

    def _get_last_sender(self, conversationId: str) -> Optional[str]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT "senderId" FROM messages WHERE "conversationId"=%s ORDER BY "timestamp" DESC LIMIT 1',
                    (conversationId,)
                )
                row = cur.fetchone()
                return row[0] if row else None

    def _saveSession(self, sessionId: str, userId: str, createdAt, expiresAt):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO sessions("sessionId","userId","createdAt","expiresAt") VALUES (%s,%s,%s,%s)',
                    (sessionId, userId, createdAt, expiresAt)
                )

    def _invalidateSession(self, sessionId: str):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE sessions SET "invalidatedAt"=NOW() WHERE "sessionId"=%s',
                    (sessionId,)
                )
