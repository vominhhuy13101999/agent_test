import time
from enum import Enum
from typing import Optional

from fastapi import HTTPException, APIRouter
from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event, EventActions

from .data_models import MessageRequest, MessageResponse
from ..agent.agent import get_agent

router = APIRouter()

# Global variables
agent: Optional[Agent] = None
runner: Optional[Runner] = None
session_service: Optional[InMemorySessionService] = None

app_name = "Tooling Agent"

class Role(str, Enum):
    USER = "user"

@router.on_event("startup")
async def startup_event():
    global agent, session_service
    agent = await get_agent()
    session_service = InMemorySessionService()

@router.post("/chat", response_model=MessageResponse)
async def send_message(
    input_data: MessageRequest
):
    global agent, runner, session_service
    
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    if runner is None:
        runner = Runner(
            agent=agent,
            app_name=app_name,
            session_service=session_service
        )

    current_session = await runner.session_service.get_session(
        app_name=app_name,
        user_id=input_data.user_id,
        session_id=input_data.session_id
    )
    if not current_session :
        current_session = await runner.session_service.create_session(
            app_name=app_name,
            user_id=input_data.user_id,
            session_id=input_data.session_id
        )

    if input_data.use_rag:
        tools_using_instruction = "Use semantic_search tool for retrieving relevant documents before answering the question."
    else:
        tools_using_instruction = "You're not allowed to use semantic_search tool for retrieving relevant documents"
        
        # tools_using_instruction = ""
    
    # print(f"Tools using instruction: {tools_using_instruction}")
    
    actions_with_update = EventActions(state_delta={
        "use_rag": input_data.use_rag,
        "tools_using_instruction": tools_using_instruction
    })
    system_event = Event(
        author="system",
        actions=actions_with_update,
        timestamp=time.time()
    )
    await runner.session_service.append_event(current_session, system_event)

    # Run the agent
    events = [
        event
        async for event in runner.run_async(
            user_id=input_data.user_id,
            session_id=input_data.session_id,
            new_message=types.Content(
                role=Role.USER,
                parts=[types.Part(text=input_data.message)]
            )
        )
    ]

    response_text = ""
    for event in events:
        print(event)
        if event.is_final_response():
            response_text = event.content.parts[0].text
    
    return MessageResponse(response=response_text)