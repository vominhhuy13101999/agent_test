import datetime

from typing import Dict, Any

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

async def create_agent():
    """Gets tools from MCP Server"""
    
    remote_tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://127.0.0.1:17234/sse"
        )
    )

    for index, tool in enumerate(remote_tools):
        print(f"Tool {index}: {tool}")

    agent = Agent(
        name="calculator_agent",
        model="gemini-2.0-flash", # Self-hosted model
        description="A mathematician agent",
        instruction=(
            "You are a mathematician agent. You can find roots of equations, or solve high school math problems. You can use the tools to help you with your tasks. "
            "Please provide the result of the calculation."
        ),
        tools=remote_tools
    )
    
    return agent, exit_stack

root_agent = create_agent()