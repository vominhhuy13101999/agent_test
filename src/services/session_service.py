from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class Session:
    def __init__(self, session_id: str, user_id: str, context: Dict[str, Any] = None):
        self.id = session_id
        self.user_id = user_id
        self.context = context or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.history = []
        self.agent = None
    
    def update_history(self, message, response):
        self.history.append({
            "message": message,
            "response": response,
            "timestamp": datetime.now()
        })
        self.updated_at = datetime.now()
    
    def set_agent(self, agent):
        self.agent = agent
    
    def get_agent(self):
        return self.agent
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "history_count": len(self.history)
        }


class SessionService:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
    
    def create_session(self, user_id: str = None, session_id: str = None, context: Dict[str, Any] = None) -> Session:
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if user_id is None:
            user_id = "anonymous"
        
        session = Session(session_id, user_id, context)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)
    
    def update_session(self, session: Session):
        self.sessions[session.id] = session
    
    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(self, user_id: str = None) -> list:
        if user_id:
            return [session for session in self.sessions.values() if session.user_id == user_id]
        return list(self.sessions.values())