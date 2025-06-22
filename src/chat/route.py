import time
from enum import Enum
from typing import Optional

from fastapi import HTTPException, APIRouter
from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event, EventActions

from chat.data_models import MessageRequest, MessageResponse

# Try to import multi-agent orchestrator first, fallback to single agent
try:
    from agents.multi_agent_orchestrator import orchestrator
    USE_MULTI_AGENT = True
except ImportError:
    from agent.agent import get_agent
    USE_MULTI_AGENT = False

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
    
    if USE_MULTI_AGENT:
        # Initialize multi-agent orchestrator
        await orchestrator.initialize()
        print("🚀 Multi-Agent Orchestrator initialized for API")
    else:
        # Fallback to single agent
        agent = await get_agent()
        session_service = InMemorySessionService()

@router.post("/chat", response_model=MessageResponse)
async def send_message(
    input_data: MessageRequest
):
    global agent, runner, session_service
    
    if USE_MULTI_AGENT:
        # Use multi-agent orchestrator
        try:
            # Prepare context for multi-agent system
            context = {
                "use_rag": input_data.use_rag,
                "user_id": input_data.user_id,
                "interface": "api"
            }
            
            # Process through multi-agent orchestrator
            response = await orchestrator.process_query(
                query=input_data.message,
                session_id=input_data.session_id,
                context=context
            )
            
            if response["status"] == "success":
                result = response["result"]
                
                # Extract response text from result
                if isinstance(result.get("response"), str):
                    response_text = result["response"]
                elif "individual_results" in result:
                    # Combine pipeline results
                    response_text = result["response"]
                else:
                    response_text = f"Processed by {result.get('agent_type', 'unknown')} agent"
                
                # Add routing information to response
                routing_info = response["routing_decision"]
                if routing_info.get("pipeline"):
                    response_text += f"\n\n[Processed through pipeline: {' → '.join(routing_info['pipeline'])}]"
                
                return MessageResponse(response=response_text)
            else:
                raise HTTPException(status_code=500, detail=f"Multi-agent processing failed: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Multi-agent system error: {str(e)}")
    
    else:
        # Fallback to single agent system
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