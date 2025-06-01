import datetime

from typing import Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

# def simple_before_model_modifier(
#     callback_context: CallbackContext,
#     llm_request: LlmRequest,
# ) -> Optional[LlmResponse]:
#     agent_name = callback_context.agent_name
#     print(f"[Callback] Before model call for agent  {agent_name}")

#     from pprint import pprint
#     print("Contents:")
#     pprint(llm_request.contents)

#     print("Tool Dict")
#     pprint(llm_request.tools_dict)

#     last_user_message = ""
#     if llm_request.contents and llm_request.contents[-1].role == 'user':
#         if llm_request.contents[-1].parts:
#             last_user_message = llm_request.contents[-1].parts[0].text
#     print(f"[Callback] Inspecting last user message: '{last_user_message}'")

_agent = None

def get_agent() -> Agent:
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent

def create_agent():
    """Gets tools from MCP Server"""
    remote_tools = MCPToolset(
        connection_params=SseServerParams(
            url="http://127.0.0.1:17324/sse"
        )
    )

    # for index, tool in enumerate(remote_tools):
    #     print(f"Tool {index}: {tool._get_declaration().name}")
    
    model = "gemini-2.0-flash" # - Gemini hosted by Google
    
    # model_name = "qwen3:1.7B"
    # model = LiteLlm(model=f"ollama_chat/{model_name}")
    
    agent = Agent(
        name="tool_agent",
        model=model, # Self-hosted model 
        description="A tool agent",
        instruction=(
            "You are a tool agent. You can find roots of equations, or solve high school math problems. You can use the tools to help you with your tasks. "
            "Please provide the result of the calculation."
        ),
        tools=[remote_tools]
    )
    
    return agent
