import time

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.events import Event, EventActions
from google.adk.models import LlmRequest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


def simple_before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
):
    agent_name = callback_context.agent_name
    print(f"[Callback] Before model call for agent  {agent_name}")
    
    if callback_context.state["disable_tool"]:
        for tool in llm_request.config.tools:
            tool.function_declarations = [declaration for declaration in tool.function_declarations if declaration.name != "get_revenue"]

    # print(".tools_dict:", llm_request.tools_dict)
    # print(".config.tools:", llm_request.config.tools)  
    print('#' * 50)


def get_agent(disable_tool: bool = False) -> Agent:
    model = "gemini-2.5-flash-preview-05-20"
    # - Gemini hosted by Google
    
    # model_name = "qwen3:1.7B"
    # model = LiteLlm(model=f"ollama_chat/{model_name}")
    
    async def get_company_name(stock_symbol: str) -> str:
        """A tool to get company name from stock symbol."""
        mapping = {
            "AAPL": "Apple Inc.",
            "GOOGL": "Alphabet Inc.",
            "MSFT": "Microsoft Corporation",
            "AMZN": "Amazon.com, Inc.",
            "TSLA": "Tesla, Inc."
        }
        return mapping.get(stock_symbol.upper(), "Unknown Company")

    async def get_revenue(company_name: str) -> float:
        """A tool to get revenue from company name."""
        mapping = {
            "Apple Inc.": 365.82,
            "Alphabet Inc.": 282.83,
            "Microsoft Corporation": 211.91,
            "Amazon.com, Inc.": 469.82,
            "Tesla, Inc.": 81.46
        }
        return str(mapping.get(company_name, 0.0))
    
    agent = Agent(
        name="financial_agent",
        model=model, # Self-hosted model 
        description="An agent can answer questions in documents",
        instruction=(
            "You are a financial agent that can answer questions about companies and their revenues. "
        ),
        tools=[get_company_name] + ([] if disable_tool else [get_revenue]),
        before_model_callback=simple_before_model_callback,
    )
    
    return agent

def get_runner(agent: Agent, app_name: str, session_service: InMemorySessionService) -> Runner:
    """Creates a Runner instance with the given agent and session service."""
    return Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service
    )

async def main():
    app_name = "Financial APP"
    agent = get_agent()
    session_service = InMemorySessionService()
    
    user_id = "user123"
    user_session_id = "user123_session1"

    message = "What is the revenue of stock AAPL?"

    turn_index = 0
    while True:
        event_actions = EventActions(state_delta={"disable_tool": turn_index % 2 == 0})
        update_state_event = Event(
            author="system",
            actions=event_actions,
            timestamp=time.time()
        )
        
        agent = get_agent(disable_tool=False)
        
        runner = get_runner(
            agent=agent,
            app_name=app_name,
            session_service=session_service
        )
        
        current_session = await runner.session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=user_session_id
        )
        if not current_session:
            current_session = await runner.session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=user_session_id
            )
        
        await runner.session_service.append_event(current_session, update_state_event)
            
        print(f"User ID: {user_id}, Session ID: {current_session.id}")
        async for event in runner.run_async(
            user_id=user_id,
            session_id=current_session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=message)]
            )
        ):
            # print(event)
            if event.is_final_response():
                response_text = event.content.parts[0].text
                print('*' * 50)
                print(f"Final Response: {response_text}")
                
            print('=' * 50)
        
        command = input("Enter a new message (or 'exit' to quit): ")
        if command.lower() == 'exit':
            break
        
        turn_index += 1
        

    

if __name__ == "__main__":
    import asyncio
    
    from dotenv import load_dotenv
    
    load_dotenv(".env")

    asyncio.run(main())