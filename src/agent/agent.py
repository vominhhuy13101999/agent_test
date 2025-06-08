import datetime
import types

from typing import Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

def simple_before_model_modifier(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    agent_name = callback_context.agent_name
    print(f"[Callback] Before model call for agent  {agent_name}")

    from pprint import pprint
    
    from copy import copy
    
    # print("Contents".center(50, '='))
    # pprint(llm_request.contents)
    
    print("Tool Dict".center(50, '='))
    pprint(llm_request.tools_dict)
    
    cloned_tools_dict = copy(llm_request.tools_dict)
    llm_request.tools_dict = cloned_tools_dict
    
    if not callback_context.state["use_rag"]:
        llm_request.tools_dict.pop("semantic_search", None)
        llm_request.tools_dict.pop("keyword_search", None)

    original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
    print("Original Instruction".center(50, '='))
    print(original_instruction)

    # last_user_message = ""
    # if llm_request.contents and llm_request.contents[-1].role == 'user':
    #     if llm_request.contents[-1].parts:
    #         last_user_message = llm_request.contents[-1].parts[0].text
    # print(f"[Callback] Inspecting last user message: '{last_user_message}'")

_agent = None

async def get_agent() -> Agent:
    global _agent
    if _agent is None:
        _agent = await create_agent()
    return _agent

async def create_agent():
    """Gets tools from MCP Server"""
    remote_tools = MCPToolset(
        connection_params=SseServerParams(
            url="http://127.0.0.1:17324/mcp-server/sse"
        )
    )

    for index, tool in enumerate(await remote_tools.get_tools()):
        print(f"Tool {index}: {tool._get_declaration().name}")
    
    model = "gemini-2.5-flash-preview-05-20"
    # - Gemini hosted by Google
    
    # model_name = "qwen3:1.7B"
    # model = LiteLlm(model=f"ollama_chat/{model_name}")
    
    agent = Agent(
        name="tool_agent",
        model=model, # Self-hosted model 
        description="An agent can answer questions in documents",
        instruction=(
            "You are a helpful agent that can answer questions based on the provided documents. "
            "You can use tools to retrieve information from the documents. "
            "{tools_using_instruction}"
        ),
        tools=[remote_tools],
        before_model_callback=simple_before_model_modifier
    )
    
    return agent
