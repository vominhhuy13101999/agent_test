import os
from typing import Optional


class Config:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:17324/mcp-server/sse")
        self.agent_model = os.getenv("AGENT_MODEL", "gemini-2.5-flash-preview-05-20")
        self.use_vertex_ai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "FALSE").upper() == "TRUE"
        
    @property
    def is_configured(self) -> bool:
        return self.google_api_key is not None
        
    def get_mcp_server_url(self) -> str:
        return self.mcp_server_url
        
    def get_agent_model(self) -> str:
        return self.agent_model


config = Config()