"""
Coordinator Agent - Routes requests between specialized agents based on query analysis
"""
import re
from typing import Dict, Any, Optional, List
from enum import Enum

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from core.config import config, AgentPrompts


class AgentType(str, Enum):
    """Available specialist agents for routing"""
    GENERAL_KNOWLEDGE = "general_knowledge"
    DOCUMENT_COMPARISON = "document_comparison"
    QUESTION_GENERATOR = "question_generator"
    INFORMATION_EXTRACTOR = "information_extractor"
    COMPARISON_ANALYST = "comparison_analyst"


class CoordinatorAgent:
    """
    AI-powered coordinator that analyzes queries and routes to appropriate specialist agents
    """
    
    def __init__(self):
        self.agent = None
        self.mcp_toolset = None
        self._initialize_agent()
        
    async def _initialize_agent(self):
        """Initialize the coordinator agent with routing capabilities"""
        self.mcp_toolset = MCPToolset(
            connection_params=SseServerParams(url=config.get_mcp_server_url())
        )
        
        # Coordinator gets minimal tools - mainly for analysis
        coordinator_tools = ["general_search"] if "general_search" in config.get_shared_tools() else []
        
        self.agent = Agent(
            name="coordinator_agent",
            model=config.get_agent_model(),
            description="Intelligent coordinator that analyzes queries and routes to specialist agents",
            instruction=self._get_coordinator_prompt(),
            tools=[self.mcp_toolset] if coordinator_tools else []
        )
    
    def _get_coordinator_prompt(self) -> str:
        """Get the coordinator agent's routing prompt"""
        return """
        You are an intelligent coordinator agent responsible for analyzing user queries and determining 
        which specialist agent should handle the request. You do NOT answer the query directly - your 
        job is to analyze and route.
        
        Available Specialist Agents:
        1. GENERAL_KNOWLEDGE: Mathematical problems, science, history, general questions
        2. DOCUMENT_COMPARISON: Comparing documents, analyzing differences between files
        3. QUESTION_GENERATOR: Creating questions from document content
        4. INFORMATION_EXTRACTOR: Extracting specific data from documents  
        5. COMPARISON_ANALYST: Structured analysis and comparison of document data
        
        Routing Guidelines:
        - Mathematical queries (equations, calculations) → GENERAL_KNOWLEDGE
        - General knowledge questions → GENERAL_KNOWLEDGE
        - "Compare documents/contracts/files" → DOCUMENT_COMPARISON
        - "Generate questions from..." → QUESTION_GENERATOR
        - "Extract information/data from..." → INFORMATION_EXTRACTOR
        - "Analyze differences/similarities" → COMPARISON_ANALYST
        - Document upload + analysis → Start with INFORMATION_EXTRACTOR
        
        Response Format:
        ROUTE_TO: [agent_type]
        REASONING: [brief explanation of why this agent was chosen]
        PIPELINE: [if document processing, list the sequence of agents needed]
        """
    
    async def route_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze query and determine routing
        
        Args:
            query: User's query text
            context: Additional context (documents, session info, etc.)
            
        Returns:
            Dict with routing decision and reasoning
        """
        # Prepare context for coordinator
        analysis_context = self._prepare_routing_context(query, context)
        
        # Use rule-based pre-filtering for obvious cases
        quick_route = self._quick_route_analysis(query, context)
        if quick_route:
            return quick_route
            
        # For complex cases, use AI coordinator agent
        try:
            if self.agent:
                # Get routing decision from AI coordinator
                routing_response = await self._get_ai_routing_decision(query, analysis_context)
                return self._parse_routing_response(routing_response)
            else:
                # Fallback to rule-based routing
                return self._fallback_routing(query, context)
                
        except Exception as e:
            print(f"Coordinator agent error: {e}")
            return self._fallback_routing(query, context)
    
    def _prepare_routing_context(self, query: str, context: Dict[str, Any] = None) -> str:
        """Prepare context information for routing decision"""
        context_info = []
        
        if context:
            if context.get("documents_uploaded"):
                context_info.append("Documents have been uploaded to the session")
            if context.get("previous_agent"):
                context_info.append(f"Previous interaction was with: {context['previous_agent']}")
            if context.get("session_history"):
                context_info.append("This is part of an ongoing conversation")
        
        context_str = "\n".join(context_info) if context_info else "No additional context"
        
        return f"""
        Query: "{query}"
        Context: {context_str}
        
        Determine which specialist agent should handle this query.
        """
    
    def _quick_route_analysis(self, query: str, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Fast rule-based routing for obvious cases"""
        query_lower = query.lower()
        
        # Mathematical expressions and calculations
        math_patterns = [r'\d+\s*[\+\-\*\/\^]\s*\d+', r'solve.*equation', r'calculate', r'x\s*=', r'derivative', r'integral']
        if any(re.search(pattern, query_lower) for pattern in math_patterns):
            return {
                "agent_type": AgentType.GENERAL_KNOWLEDGE,
                "reasoning": "Mathematical calculation or equation detected",
                "pipeline": [],
                "confidence": "high"
            }
        
        # Document comparison keywords
        comparison_keywords = ["compare", "difference", "contrast", "versus", "vs", "between"]
        if any(keyword in query_lower for keyword in comparison_keywords) and context and (context.get("documents_uploaded") or context.get("has_documents")):
            return {
                "agent_type": AgentType.DOCUMENT_COMPARISON,
                "reasoning": "Document comparison request detected",
                "pipeline": [AgentType.INFORMATION_EXTRACTOR, AgentType.DOCUMENT_COMPARISON, AgentType.COMPARISON_ANALYST],
                "confidence": "high"
            }
        
        # Question generation
        if "generate question" in query_lower or "create question" in query_lower:
            return {
                "agent_type": AgentType.QUESTION_GENERATOR,
                "reasoning": "Question generation request detected",
                "pipeline": [AgentType.INFORMATION_EXTRACTOR, AgentType.QUESTION_GENERATOR],
                "confidence": "high"
            }
        
        # Information extraction
        extract_keywords = ["extract", "find", "get information", "what is", "tell me about"]
        if any(keyword in query_lower for keyword in extract_keywords) and context and (context.get("documents_uploaded") or context.get("has_documents")):
            return {
                "agent_type": AgentType.INFORMATION_EXTRACTOR,
                "reasoning": "Information extraction from documents detected",
                "pipeline": [AgentType.INFORMATION_EXTRACTOR],
                "confidence": "high"
            }
        
        return None
    
    async def _get_ai_routing_decision(self, query: str, context: str) -> str:
        """Get routing decision from AI coordinator agent"""
        if not self.agent:
            raise Exception("Coordinator agent not initialized")
        
        # This would use the ADK agent to analyze the query
        # For now, return a structured response format
        routing_prompt = f"{context}\n\nProvide routing decision in the specified format."
        
        # Note: This would need to be implemented with actual ADK agent interaction
        # For now, we'll use the fallback routing
        return "ROUTE_TO: GENERAL_KNOWLEDGE\nREASONING: Fallback routing\nPIPELINE: []"
    
    def _parse_routing_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI coordinator's response into routing decision"""
        lines = response.strip().split('\n')
        result = {
            "agent_type": AgentType.GENERAL_KNOWLEDGE,
            "reasoning": "Default routing",
            "pipeline": [],
            "confidence": "medium"
        }
        
        for line in lines:
            if line.startswith("ROUTE_TO:"):
                agent_type = line.split(":", 1)[1].strip().lower()
                if agent_type in [e.value for e in AgentType]:
                    result["agent_type"] = AgentType(agent_type)
            elif line.startswith("REASONING:"):
                result["reasoning"] = line.split(":", 1)[1].strip()
            elif line.startswith("PIPELINE:"):
                pipeline_str = line.split(":", 1)[1].strip()
                # Parse pipeline if provided
                if pipeline_str and pipeline_str != "[]":
                    # Simple parsing for now
                    result["pipeline"] = []
        
        return result
    
    def _fallback_routing(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fallback routing when AI coordinator is unavailable"""
        query_lower = query.lower()
        
        # Simple keyword-based routing
        if context and context.get("documents_uploaded"):
            if any(word in query_lower for word in ["compare", "contrast", "difference"]):
                return {
                    "agent_type": AgentType.DOCUMENT_COMPARISON,
                    "reasoning": "Fallback: Document comparison keywords detected",
                    "pipeline": [AgentType.INFORMATION_EXTRACTOR, AgentType.DOCUMENT_COMPARISON],
                    "confidence": "medium"
                }
            else:
                return {
                    "agent_type": AgentType.INFORMATION_EXTRACTOR,
                    "reasoning": "Fallback: Documents available, defaulting to extraction",
                    "pipeline": [AgentType.INFORMATION_EXTRACTOR],
                    "confidence": "medium"
                }
        else:
            return {
                "agent_type": AgentType.GENERAL_KNOWLEDGE,
                "reasoning": "Fallback: No documents, defaulting to general knowledge",
                "pipeline": [],
                "confidence": "low"
            }
    
    def get_pipeline_for_agent(self, agent_type: AgentType, query: str, context: Dict[str, Any] = None) -> List[AgentType]:
        """
        Determine the processing pipeline for a given agent type
        """
        pipelines = {
            AgentType.GENERAL_KNOWLEDGE: [],
            AgentType.DOCUMENT_COMPARISON: [
                AgentType.INFORMATION_EXTRACTOR,
                AgentType.DOCUMENT_COMPARISON,
                AgentType.COMPARISON_ANALYST
            ],
            AgentType.QUESTION_GENERATOR: [
                AgentType.INFORMATION_EXTRACTOR,
                AgentType.QUESTION_GENERATOR
            ],
            AgentType.INFORMATION_EXTRACTOR: [
                AgentType.INFORMATION_EXTRACTOR
            ],
            AgentType.COMPARISON_ANALYST: [
                AgentType.INFORMATION_EXTRACTOR,
                AgentType.COMPARISON_ANALYST
            ]
        }
        
        return pipelines.get(agent_type, [])


# Singleton instance
coordinator_agent = CoordinatorAgent()