import os
from typing import Optional, Dict, List


class Config:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:17324/mcp-server/sse")
        self.agent_model = os.getenv("AGENT_MODEL", "gemini-2.5-flash-preview-05-20")
        self.use_vertex_ai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "FALSE").upper() == "TRUE"
        
        # Unified MCP server configuration
        self.unified_mcp_server = True  # Single server for both math and document tools
        
        # Agent tool access configuration
        self.agent_tools = {
            "knowledge_agent": ["calculator", "math_solver", "general_search", "semantic_search"],
            "document_agent": ["semantic_search", "doc_processor", "rag_retrieval", "document_comparison"],
            "shared_tools": ["semantic_search"]  # Tools both agents can use
        }
        
        # RAG configuration
        self.use_rag = os.getenv("USE_RAG", "TRUE").upper() == "TRUE"
        self.rag_similarity_threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.7"))
        self.max_context_length = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))
        self.max_retrieved_documents = int(os.getenv("MAX_RETRIEVED_DOCUMENTS", "5"))
        
    @property
    def is_configured(self) -> bool:
        return self.google_api_key is not None
        
    def get_mcp_server_url(self) -> str:
        return self.mcp_server_url
        
    def get_agent_model(self) -> str:
        return self.agent_model
        
    def get_agent_tools(self, agent_type: str) -> List[str]:
        """Get available tools for a specific agent type."""
        return self.agent_tools.get(agent_type, [])
        
    def get_shared_tools(self) -> List[str]:
        """Get tools that can be used by both agents."""
        return self.agent_tools.get("shared_tools", [])


# Agent prompt configurations
class AgentPrompts:
    KNOWLEDGE_AGENT = """
    You are a mathematical and general knowledge expert. You can find roots of equations, solve high school math problems, 
    and provide comprehensive knowledge across science, technology, history, arts, culture, finance, health, law, and everyday topics.
    
    Use calculator tools for mathematical problems. When appropriate, collaborate with document analysis capabilities 
    for context-enhanced responses.
    
    Style: Use clear, concise language. Show step-by-step logic for calculations and provide reasoning when helpful.
    """
    
    DOCUMENT_AGENT = """
    You are a document analysis specialist. When asked to compare, analyze, or extract from documents, IMMEDIATELY proceed with the task without asking for clarification.
    
    For document comparison: Automatically perform comprehensive comparison including textual differences, structural changes, formatting variations, and content analysis.
    For information extraction: Immediately extract relevant information with source citations.
    For analysis: Provide detailed analysis with evidence and citations.
    
    Use semantic search and RAG for document-based queries. Process PDFs, DOCX, TXT and other formats.
    Always provide source attribution and evidence. Use document processing tools for all tasks.
    
    DO NOT ask users for additional criteria or specifications - proceed with comprehensive analysis immediately.
    """


config = Config()