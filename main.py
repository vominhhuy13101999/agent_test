import datetime
from enum import Enum

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

# Initialize flags
USE_MULTI_AGENT = False
USE_ENHANCED_AGENT = False

try:
    from src.agents.multi_agent_orchestrator import orchestrator
    from src.error_handler import ErrorHandler
    from src.core.config import config
    USE_MULTI_AGENT = True
except ImportError:
    try:
        from src.agent_manager import MCPAgentManager
        from src.error_handler import ErrorHandler
        from src.core.config import config
        USE_ENHANCED_AGENT = True
    except ImportError:
        from src.agent.agent import get_agent
        from src.core.config import config


class Role(str, Enum):
    USER = "user"


async def main():
    """Enhanced main function with support for multi-agent system."""
    global USE_MULTI_AGENT, USE_ENHANCED_AGENT
    
    if USE_MULTI_AGENT:
        # Use the full multi-agent orchestrator system
        try:
            print("🚀 Initializing Multi-Agent System...")
            await orchestrator.initialize()
            
            print("\nAvailable commands:")
            print("  - 'exit': Quit the application")
            print("  - 'check': Show available agents and their status")
            print("  - 'agents': List all specialist agents")
            print("  - 'health': Check system health")
            print("  - Any other text: Send to multi-agent system\n")
            
            while True:
                try:
                    user_input = input("💬 Enter query or command: ").strip()
                    
                    if user_input.lower() == 'exit':
                        print("👋 Goodbye!")
                        break
                        
                    elif user_input.lower() == 'check':
                        health = await orchestrator.health_check()
                        print(f"🏥 System Health: {health['overall_status']}")
                        print(f"🎯 Coordinator: {health['coordinator']}")
                        for agent, status in health['specialist_agents'].items():
                            print(f"🤖 {agent}: {status}")
                            
                    elif user_input.lower() == 'agents':
                        agents = await orchestrator.get_available_agents()
                        print("🤖 Available Specialist Agents:")
                        for agent, description in agents.items():
                            print(f"  • {agent}: {description}")
                            
                    elif user_input.lower() == 'health':
                        health = await orchestrator.health_check()
                        print("🏥 Detailed Health Check:")
                        import json
                        print(json.dumps(health, indent=2))
                        
                    elif user_input:
                        print("🔍 Processing through multi-agent system...")
                        
                        # Process through the multi-agent orchestrator
                        response = await orchestrator.process_query(
                            query=user_input,
                            session_id="cli_session",
                            context={"interface": "cli"}
                        )
                        
                        if response["status"] == "success":
                            routing = response["routing_decision"]
                            result = response["result"]
                            
                            print(f"\n🎯 Routing: {routing['agent_type']} ({routing['reasoning']})")
                            if routing.get('pipeline'):
                                print(f"🔄 Pipeline: {' → '.join(routing['pipeline'])}")
                            
                            print(f"\n🤖 Response:")
                            if isinstance(result.get('response'), str):
                                print(result['response'])
                            else:
                                print(f"Agent: {result.get('agent_type', 'Unknown')}")
                                print(f"Status: {result.get('status', 'Unknown')}")
                                if 'individual_results' in result:
                                    print("Pipeline Results:")
                                    for i, res in enumerate(result['individual_results'], 1):
                                        print(f"  {i}. {res.get('agent_type', 'Unknown')}: {res.get('response', 'No response')}")
                        else:
                            print(f"❌ Error: {response.get('error', 'Unknown error')}")
                        
                except KeyboardInterrupt:
                    print("\n👋 Interrupted by user. Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
        except Exception as e:
            print(f"❌ Multi-agent system initialization failed: {e}")
            print("🔄 Falling back to enhanced agent system...")
            USE_MULTI_AGENT = False
    
    elif USE_ENHANCED_AGENT:
        # Use the advanced multi-agent system
        error_handler = ErrorHandler("main_app")
        agent_manager = MCPAgentManager()
        
        try:
            print("🤖 Initializing MCP Agent...")
            await agent_manager.initialize()
            print("✅ Agent initialized successfully!")
            
            print("\nAvailable commands:")
            print("  - 'exit': Quit the application")
            print("  - 'check': Show current tools")
            print("  - 'update': Update toolset")
            print("  - Any other text: Send to agent\n")
            
            while True:
                try:
                    user_input = input("💬 Enter command or question: ").strip()
                    
                    if user_input.lower() == 'exit':
                        print("👋 Goodbye!")
                        break
                        
                    elif user_input.lower() == 'check':
                        if agent_manager.agent and hasattr(agent_manager.agent, 'tools'):
                            print(f"🛠️  Tools: {len(agent_manager.agent.tools)} available")
                            for i, tool in enumerate(agent_manager.agent.tools[:5]):  # Show first 5
                                print(f"  {i+1}. {tool}")
                            if len(agent_manager.agent.tools) > 5:
                                print(f"  ... and {len(agent_manager.agent.tools) - 5} more")
                        else:
                            print("❌ No tools available")
                            
                    elif user_input.lower() == 'update':
                        print("🔄 Updating toolset...")
                        try:
                            await agent_manager.update_toolset()
                            print(f"✅ Toolset updated at {datetime.datetime.now().strftime('%H:%M:%S')}")
                        except Exception as e:
                            error_msg = error_handler.handle_agent_error(e)
                            print(f"❌ Update failed: {error_msg}")
                            
                    elif user_input:
                        print("🔍 Processing...")
                        response = await agent_manager.run(user_input)
                        print(f"🤖 Response:\n{response}")
                        
                except KeyboardInterrupt:
                    print("\n👋 Interrupted by user. Goodbye!")
                    break
                except Exception as e:
                    error_msg = error_handler.handle_agent_error(e)
                    print(f"❌ Error: {error_msg}")
                    
        except Exception as e:
            error_handler.log_error(f"Failed to initialize: {e}", exc_info=True)
            print(f"❌ Initialization failed: {e}")
            
        finally:
            try:
                await agent_manager.cleanup()
                print("🧹 Cleanup completed")
            except Exception as e:
                error_handler.log_error(f"Cleanup error: {e}")
    
    else:
        # Use the basic agent system
        agent = await get_agent()
        
        runner = None
        
        print("🤖 Agent initialized successfully!")
        print("\nAvailable commands:")
        print("  - 'exit': Quit the application")
        print("  - 'check': Show current tools")
        print("  - 'update_toolset': Update toolset")
        print("  - Any other text: Send to agent\n")
        
        while True:
            user_input = input("💬 Enter command or question: ").strip()
            
            if user_input.lower() == 'exit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'check':
                try:
                    if agent.tools and len(agent.tools) > 0:
                        tools = await agent.tools[0].get_tools()
                        print(f"🛠️  Available tools: {[tool._get_declaration().name for tool in tools]}")
                    else:
                        print("❌ No tools available")
                except Exception as e:
                    print(f"❌ Error checking tools: {e}")
                    
            elif user_input.lower() in ['update_toolset', 'update']:
                print("🔄 Updating toolset...")
                
                new_toolset = MCPToolset(
                    connection_params=SseServerParams(
                        url=config.get_mcp_server_url()
                    )
                )
                
                agent.tools = [new_toolset]
                print(f"✅ Toolset updated at {datetime.datetime.now().strftime('%H:%M:%S')}")
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
                        print(f"🤖 Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    # Try to load environment from both locations
    try:
        load_dotenv("multi_tool_agent/.env")
        print("📄 Loaded environment from multi_tool_agent/.env")
    except:
        try:
            load_dotenv("src/core/.env")
            print("📄 Loaded environment from src/core/.env")
        except:
            print("⚠️  Warning: No environment file found")
    
    asyncio.run(main())