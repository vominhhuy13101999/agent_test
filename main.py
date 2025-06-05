import datetime
from src.agent_manager import MCPAgentManager
from src.error_handler import ErrorHandler

async def main():
    """Enhanced main function with better error handling and modular design."""
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
                  

if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv("multi_tool_agent/.env")
    
    # Run the main application
    asyncio.run(main())