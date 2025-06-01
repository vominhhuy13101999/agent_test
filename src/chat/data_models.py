from pydantic import BaseModel, Field

class MessageRequest(BaseModel):
    user_id: str = Field(description="ID of the user sending the message")
    session_id: str = Field(description="ID of the session the message belongs to")
    message: str = Field(description="Content of the message being sent")
    use_rag: bool = Field(default=False, description="If True, agent will search context in Knowledge Base")

class MessageResponse(BaseModel):
    response: str