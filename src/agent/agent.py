import datetime
import types
from typing import Dict, Any, Optional
from copy import copy

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

from core.config import config


def simple_before_model_modifier(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    agent_name = callback_context.agent_name
    print(f"[Callback] Before model call for agent {agent_name}")

    cloned_tools_dict = copy(llm_request.tools_dict)
    llm_request.tools_dict = cloned_tools_dict
    
    if not callback_context.state.get("use_rag", False):
        llm_request.tools_dict.pop("semantic_search", None)
        llm_request.tools_dict.pop("keyword_search", None)

    tools_using_instruction = callback_context.state.get("tools_using_instruction", "")
    if tools_using_instruction:
        original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
        if original_instruction.parts:
            original_text = original_instruction.parts[0].text
            updated_text = original_text.format(tools_using_instruction=tools_using_instruction)
            llm_request.config.system_instruction = types.Content(
                role="system",
                parts=[types.Part(text=updated_text)]
            )


_agent = None


async def get_agent() -> Agent:
    global _agent
    if _agent is None:
        _agent = await create_agent()
    return _agent


async def create_agent() -> Agent:
    """Creates agent with tools from MCP Server"""
    if not config.is_configured:
        raise ValueError("Configuration incomplete. Please check environment variables.")
    
    remote_tools = MCPToolset(
        connection_params=SseServerParams(
            url=config.get_mcp_server_url()
        )
    )

    try:
        tools = await remote_tools.get_tools()
        print(f"Loaded {len(tools)} tools from MCP server")
        for index, tool in enumerate(tools):
            print(f"Tool {index}: {tool._get_declaration().name}")
    except Exception as e:
        print(f"Warning: Could not load tools from MCP server: {e}")
    
    model = config.get_agent_model()
    
    agent = Agent(
        name="document_agent",
        model=model,
        description="An AI agent that can answer questions and perform tasks using available tools",
        instruction=(
            "You are a helpful AI agent that can answer questions and perform tasks using the tools available to you. "
            "When tools are available, use them appropriately to provide accurate and helpful responses. "
            "{tools_using_instruction}"
        ),
        tools=[remote_tools],
        before_model_callback=simple_before_model_modifier
    )
    
    return agent
