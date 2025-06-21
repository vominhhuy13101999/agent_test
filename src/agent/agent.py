import datetime
import types

from typing import Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.base_tool import BaseTool, ToolContext 
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

def simple_before_model_modifier(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    agent_name = callback_context.agent_name
    print(f"[Callback] Before model call for agent  {agent_name}")
    
    print(f"[Callback] The contents in LLM request: {llm_request.contents}")
    
    # if not callback_context.state["user:use_rag"]:
    #     for tool in llm_request.config.tools:
    #         tool.function_declarations = [
    #             declaration 
    #             for declaration in tool.function_declarations 
    #             if declaration.name not in ["semantic_search", "keyword_search"]
    #         ]
    
    print(
        f"[Callback] Tools after modification: {
        [
            function_declaration.name
            for tool in llm_request.config.tools
            for function_declaration in tool.function_declarations  
        ]}"
    )
        
    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == 'user':
        if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text
        
        print(f"[Callback] Inspecting last user message: '{last_user_message}'")
    
        # if callback_context.state["use_rag"]:
        #     llm_request.contents[-1].parts[0].text = f"{last_user_message} (use Semantic Search to answer this question)"

def simple_before_tool_modifier(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """Inspects/modifies tool args or skips the tool call."""
    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[Callback] Before tool call for tool '{tool_name}' in agent '{agent_name}'")
    print(f"[Callback] Original args: {args}")

    # If the tool is 'semantic_search' and country is 'BLOCK'
    if tool_name == 'semantic_search' and not tool_context.state.get("user:use_rag"):
        print("[Callback] Detected calling semantic_search tool but not enable use_rag. Skipping tool execution.")
        return {"result": "Tool execution skipped due to not enabling RAG mode"}

    print("[Callback] Proceeding with original or previously modified args.")
    return None


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
        description="An agent that can answer questions based on provided documents and use tools to retrieve information",
        instruction=(
            "You are a helpful agent that can answer questions based on the provided documents. "
            "If this value {user:use_rag} is true, force you to use tool semantic_search to retrieve information from the documents."
        ),
        tools=[remote_tools],
        before_model_callback=simple_before_model_modifier,
        before_tool_callback=simple_before_tool_modifier
    )
    
    return agent
