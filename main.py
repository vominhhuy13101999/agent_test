import datetime

from enum import Enum

from google.genai import types

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

from multi_tool_agent.agent import create_agent

class Role(str, Enum):
    USER = "user"

async def main():
    agent, exit_stack = await create_agent()
    
    runner = None
    
    while True:
        user_input = input("Update toolset (or 'exit' to quit): ")
        user_input = user_input.strip().lower()
        if user_input == 'exit':
            break
        elif user_input == 'check':
            print(f"Tools: {agent.tools}")
        elif user_input == 'update_toolset':
            print(f"Updating toolset ...")
            await exit_stack.aclose()
            
            new_tools, new_exit_stack = await MCPToolset.from_server(
                connection_params=SseServerParams(
                    url="http://127.0.0.1:17234/sse"
                )
            )
            print(new_tools)
            
            agent.tools = new_tools
            exit_stack = new_exit_stack
            
            print(f"Toolset updated at {datetime.datetime.now()}")
        else:
            if runner is None:
                session_service = InMemorySessionService()
                
                runner = Runner(
                    app_name="Math APP",
                    agent=agent,
                    session_service=session_service
                )
                
                if not runner.session_service.get_session(
                    app_name="Math APP",
                    user_id="anhld",
                    session_id="anhld-session-01"
                ):
                    runner.session_service.create_session(
                        app_name="Math APP",
                        user_id="anhld",
                        session_id="anhld-session-01"
                    )
                else:
                    print("Session already exists.")
            
            events = [
                event
                async for event in runner.run_async(
                    user_id="anhld",
                    session_id="anhld-session-01",
                    new_message=types.Content(
                        role=Role.USER,
                        parts=[types.Part(text=user_input)]
                    )
                )
            ]
            
            for event in events:
                print(event)
            
            # print(runner.session_service.sessions)
            # print(runner.session_service.user_state)
            # print(runner.session_service.app_state)
                  

if __name__ == "__main__":
    import asyncio
    
    from dotenv import load_dotenv
    
    load_dotenv("multi_tool_agent/.env")

    asyncio.run(main())