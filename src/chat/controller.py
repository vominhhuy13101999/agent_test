from typing import Dict, List, Optional, Any
from fastapi import HTTPException, Depends, APIRouter
from pydantic import BaseModel

# Import necessary services/models
from ..services.session_service import SessionService
from ..agent.agent import Agent


class ChatMessage(BaseModel):
    content: str
    role: str = "user"
    metadata: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    message: str
    session_id: str
    metadata: Dict[str, Any] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Dict[str, Any] = {}


class ChatController:
    def __init__(self, session_service: SessionService):
        self.session_service = session_service
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Configure API routes for chat functionality"""
        self.router.post("/chat", response_model=ChatResponse)(self.handle_message)
        self.router.get("/sessions/{session_id}")(self.get_session)
        self.router.delete("/sessions/{session_id}")(self.end_session)

    async def handle_message(self, request: ChatRequest) -> ChatResponse:
        """Process an incoming chat message"""
        try:
            # Get or create a session
            if request.session_id:
                session = self.session_service.get_session(request.session_id)
                if not session:
                    raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")
            else:
                session = self.session_service.create_session(context=request.context)
            
            # Create message object
            message = ChatMessage(content=request.message)
            
            # Get agent for this session
            agent = session.get_agent()
            if not agent:
                agent = Agent(session_id=session.id)
                session.set_agent(agent)
            
            # Process the message with the agent
            response = agent.process_message(message, session.context)
            
            # Update session with new context
            session.update_history(message, response)
            self.session_service.update_session(session)
            
            return ChatResponse(
                message=response.content,
                session_id=session.id,
                metadata=response.metadata
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

    async def get_session(self, session_id: str):
        """Retrieve a specific chat session"""
        session = self.session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        return session.to_dict()

    async def end_session(self, session_id: str):
        """End a chat session"""
        try:
            self.session_service.delete_session(session_id)
            return {"message": f"Session {session_id} terminated successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error ending session: {str(e)}")
