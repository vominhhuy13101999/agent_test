from enum import Enum

from fastapi import HTTPException
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from fastapi import APIRouter

from chat.data_models import MessageRequest, MessageResponse
from agent.agent import create_agent

router = APIRouter()

# Global variables
agent = None
exit_stack = None
runner = None
session_service = None

app_name = "Tooling Agent"

class Role(str, Enum):
    USER = "user"


@router.on_event("startup")
async def startup_event():
    global agent, exit_stack, session_service
    agent, exit_stack = await create_agent()
    session_service = InMemorySessionService()

@router.on_event("shutdown")
async def shutdown_event():
    global exit_stack
    if exit_stack:
        await exit_stack.aclose()

@router.post("/", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    global agent, runner, session_service
    
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    if runner is None:
        runner = Runner(
            app_name=app_name,
            agent=agent,
            session_service=session_service
        )
    
    # Create session if it doesn't exist
    if not runner.session_service.get_session(
        app_name=app_name,
        user_id=request.user_id,
        session_id=request.session_id
    ):
        runner.session_service.create_session(
            app_name=app_name,
            user_id=request.user_id,
            session_id=request.session_id
        )
    
    # Run the agent
    events = [
        event
        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=request.session_id,
            new_message=types.Content(
                role=Role.USER,
                parts=[types.Part(text=request.message)]
            )
        )
    ]
    
    # Get the final response
    response_text = ""
    for event in events:
        if event.is_final_response():
            response_text = event.content.parts[0].text
    
    return MessageResponse(response=response_text)