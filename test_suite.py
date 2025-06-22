import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables from the correct location
load_dotenv("src/core/.env")
print(f"📄 Loaded environment from src/core/.env")

from src.core.config import config
from src.agents.multi_agent_orchestrator import orchestrator

async def quick_test_suite():
    print("🧪 Multi-Agent System Quick Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 6
    
    # Test 1: Configuration
    try:
        mcp_url = config.get_mcp_server_url()
        print(f"✅ Config Test: MCP URL = {mcp_url}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Config Test Failed: {e}")
    
    # Test 2: Orchestrator Initialization
    try:
        await orchestrator.initialize()
        print("✅ Orchestrator Initialization")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Orchestrator Initialization Failed: {e}")
    
    # Test 3: Health Check
    try:
        health = await orchestrator.health_check()
        print(f"✅ Health Check: {health['overall_status']}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
    
    # Test 4: Simple Query
    try:
        response = await orchestrator.process_query(
            query="What is 5 + 3?",
            session_id="quick_test",
            context={"interface": "test"}
        )
        if response["status"] == "success":
            print("✅ Simple Query Processing")
            tests_passed += 1
        else:
            print("❌ Simple Query Failed")
    except Exception as e:
        print(f"❌ Simple Query Failed: {e}")
    
    # Test 5: Agent Routing
    try:
        response = await orchestrator.process_query(
            query="Compare these documents",
            session_id="quick_test",
            context={"interface": "test"}
        )
        route = response["routing_decision"]["agent_type"]
        print(f"✅ Agent Routing: {route}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Agent Routing Failed: {e}")
    
    # Test 6: Multiple Agents
    try:
        agents = await orchestrator.get_available_agents()
        print(f"✅ Available Agents: {len(agents)} agents")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Available Agents Failed: {e}")
    
    print("=" * 50)
    print(f"Test Results: {tests_passed}/{tests_total} passed")
    
    if tests_passed == tests_total:
        print("🎉 All tests passed! System is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Check configuration and dependencies.")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test_suite())
    sys.exit(0 if success else 1)