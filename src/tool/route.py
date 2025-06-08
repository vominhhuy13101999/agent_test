import datetime

from fastapi import APIRouter, HTTPException
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

from .data_models import ToolResponse, StatusResponse
from ..agent.agent import get_agent

router = APIRouter()

@router.get("/tools", response_model=ToolResponse)
async def get_tools():
    try:
        agent = await get_agent()
        
        if not agent.tools:
            return ToolResponse(tools=[])
            
        tool_names = []
        for toolset in agent.tools:
            if hasattr(toolset, 'get_tools'):
                tools = await toolset.get_tools()
                tool_names.extend([tool._get_declaration().name for tool in tools])
        
        return ToolResponse(tools=tool_names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tools: {str(e)}")

@router.post("/update-toolset", response_model=StatusResponse)
async def update_toolset():
    try:
        agent = await get_agent()
        
        # Create new toolset
        new_toolset = MCPToolset(
            connection_params=SseServerParams(
                url="http://127.0.0.1:17324/mcp-server/sse"
            )
        )
        
        # Update agent tools
        agent.tools = [new_toolset]
        
        timestamp = datetime.datetime.now().isoformat()
        return StatusResponse(status="Toolset updated successfully", timestamp=timestamp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating toolset: {str(e)}")
