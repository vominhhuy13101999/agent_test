import datetime
from enum import Enum

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

from src.agent.agent import get_agent


class Role(str, Enum):
    USER = "user"


async def main():
    agent = await get_agent()
    
    runner = None
    
    while True:
        user_input = input("Enter command (or 'exit' to quit): ")
        user_input = user_input.strip()
        
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'check':
            print(f"Available tools: {[tool._get_declaration().name for tool in agent.tools[0].get_tools()]}")
        elif user_input.lower() == 'update_toolset':
            print("Updating toolset...")
            
            new_toolset = MCPToolset(
                connection_params=SseServerParams(
                    url="http://127.0.0.1:17324/mcp-server/sse"
                )
            )
            
            agent.tools = [new_toolset]
            print(f"Toolset updated at {datetime.datetime.now()}")
        else:
            if runner is None:
                session_service = InMemorySessionService()
                
                runner = Runner(
                    app_name="Agent CLI",
                    agent=agent,
                    session_service=session_service
                )
                
                if not await runner.session_service.get_session(
                    app_name="Agent CLI",
                    user_id="cli_user",
                    session_id="cli_session"
                ):
                    await runner.session_service.create_session(
                        app_name="Agent CLI",
                        user_id="cli_user", 
                        session_id="cli_session"
                    )
                else:
                    print("Session already exists.")
            
            events = [
                event
                async for event in runner.run_async(
                    user_id="cli_user",
                    session_id="cli_session",
                    new_message=types.Content(
                        role=Role.USER,
                        parts=[types.Part(text=user_input)]
                    )
                )
            ]
            
            for event in events:
                if event.is_final_response():
                    print(f"Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv("src/core/.env")
    
    asyncio.run(main())