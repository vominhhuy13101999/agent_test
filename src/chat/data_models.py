from pydantic import BaseModel

class MessageRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

class MessageResponse(BaseModel):
    response: str