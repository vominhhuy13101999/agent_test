import datetime

from fastapi import APIRouter, HTTPException
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

from src.tool.data_models import ToolResponse, StatusResponse

router = APIRouter()

@router.get("/tools", response_model=ToolResponse)
async def get_tools():
    global agent
    
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    tool_names = [tool._get_declaration().name for tool in agent.tools]
    return ToolResponse(tools=tool_names)

@router.post("/update-toolset", response_model=StatusResponse)
async def update_toolset():
    global agent, exit_stack
    
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    # Close existing exit stack
    await exit_stack.aclose()
    
    # Get new tools
    new_tools, new_exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://127.0.0.1:17234/sse"
        )
    )
    
    # Update agent tools
    agent.tools = new_tools
    exit_stack = new_exit_stack
    
    timestamp = datetime.datetime.now().isoformat()
    return StatusResponse(status="Toolset updated successfully", timestamp=timestamp)
