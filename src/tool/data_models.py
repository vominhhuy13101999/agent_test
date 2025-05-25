from typing import List

from pydantic import BaseModel

class ToolResponse(BaseModel):
    tools: List[str]

class StatusResponse(BaseModel):
    status: str
    timestamp: str
