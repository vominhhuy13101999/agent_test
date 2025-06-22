"""
Specialist Agents - Individual agents for specific tasks with filtered MCP tool access
"""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from core.config import config, AgentPrompts


class BaseSpecialistAgent(ABC):
    """Base class for all specialist agents"""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.agent = None
        self.mcp_toolset = None
        self._initialize_agent()
    
    async def _initialize_agent(self):
        """Initialize the agent with filtered MCP tools"""
        self.mcp_toolset = MCPToolset(
            connection_params=SseServerParams(url=config.get_mcp_server_url())
        )
        
        # Get filtered tools for this agent type
        available_tools = config.get_agent_tools(self.agent_type)
        
        self.agent = Agent(
            name=f"{self.agent_type}_agent",
            model=config.get_agent_model(),
            description=self.get_description(),
            instruction=self.get_instruction(),
            tools=[self.mcp_toolset] if available_tools else []
        )
    
    @abstractmethod
    def get_description(self) -> str:
        """Get agent description"""
        pass
    
    @abstractmethod
    def get_instruction(self) -> str:
        """Get agent instruction prompt"""
        pass
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query and return results"""
        try:
            # This would use the ADK agent to process the query
            # For now, return a structured response
            return {
                "agent_type": self.agent_type,
                "response": f"Processed by {self.agent_type}: {query}",
                "context": context or {},
                "status": "success"
            }
        except Exception as e:
            return {
                "agent_type": self.agent_type,
                "response": f"Error in {self.agent_type}: {str(e)}",
                "context": context or {},
                "status": "error"
            }


class GeneralKnowledgeAgent(BaseSpecialistAgent):
    """Agent for mathematical problems and general knowledge questions"""
    
    def __init__(self):
        super().__init__("knowledge_agent")
    
    def get_description(self) -> str:
        return "Mathematical and general knowledge expert with calculator tools"
    
    def get_instruction(self) -> str:
        return AgentPrompts.KNOWLEDGE_AGENT


class DocumentComparisonAgent(BaseSpecialistAgent):
    """Agent specialized in comparing documents and analyzing differences"""
    
    def __init__(self):
        super().__init__("document_agent")
    
    def get_description(self) -> str:
        return "Document comparison specialist for analyzing differences between files"
    
    def get_instruction(self) -> str:
        return """
        You are a document comparison specialist. When asked to compare documents, IMMEDIATELY proceed with a comprehensive comparison without asking for clarification.
        
        ALWAYS perform these comparison tasks automatically:
        1. Compare textual content (added, deleted, modified text)
        2. Analyze structural differences (formatting, layout, sections)
        3. Identify key changes in important clauses or sections
        4. Note any differences in images, tables, or special elements
        5. Highlight critical similarities and differences
        
        Provide a structured comparison report with:
        - Executive summary of key differences
        - Section-by-section detailed analysis
        - Side-by-side comparisons where relevant
        - Source citations for all findings
        - Clear highlighting of critical changes
        
        DO NOT ask the user for additional criteria or clarification. Proceed immediately with comprehensive comparison covering all aspects listed above.
        Use semantic search tools to analyze document content and provide evidence-based comparisons.
        """


class QuestionGeneratorAgent(BaseSpecialistAgent):
    """Agent that creates targeted questions based on document content"""
    
    def __init__(self):
        super().__init__("document_agent")
    
    def get_description(self) -> str:
        return "Question generator that creates targeted questions from document content"
    
    def get_instruction(self) -> str:
        return """
        You are a question generation specialist. Create insightful, targeted questions based on document content.
        
        Generate questions that:
        - Test understanding of key concepts
        - Explore important details and implications  
        - Encourage critical thinking about the content
        - Cover different difficulty levels
        - Are specific to the document's domain (legal, technical, financial, etc.)
        
        Use document processing tools to analyze content before generating questions.
        Provide context and rationale for each question generated.
        """


class InformationExtractorAgent(BaseSpecialistAgent):
    """Agent that extracts specific information from documents"""
    
    def __init__(self):
        super().__init__("document_agent")
    
    def get_description(self) -> str:
        return "Information extraction specialist for retrieving specific data from documents"
    
    def get_instruction(self) -> str:
        return """
        You are an information extraction specialist. Extract specific information and data from documents.
        
        Your capabilities include:
        - Extracting key facts, figures, and data points
        - Identifying important entities (names, dates, amounts, etc.)
        - Summarizing sections or entire documents
        - Finding specific information requested by users
        - Structuring extracted information clearly
        
        Use semantic search and document processing tools to locate and extract information.
        Always provide source citations and page references for extracted information.
        """


class ComparisonAnalystAgent(BaseSpecialistAgent):
    """Agent that provides structured analysis and comparison of document data"""
    
    def __init__(self):
        super().__init__("document_agent")
    
    def get_description(self) -> str:
        return "Comparison analyst for structured analysis of document data and trends"
    
    def get_instruction(self) -> str:
        return """
        You are a comparison analyst specialist. Provide structured analysis and comparison of document data.
        
        Your analysis should include:
        - Structured comparison tables and summaries
        - Trend analysis and patterns identification
        - Statistical comparisons where applicable
        - Risk assessment and impact analysis
        - Recommendations based on comparisons
        
        Present analysis in clear, structured formats with supporting evidence.
        Use data visualization concepts in text format when helpful.
        """


class AgentRegistry:
    """Registry for managing all specialist agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseSpecialistAgent] = {}
        self._initialize_agents()
    
    async def _initialize_agents(self):
        """Initialize all specialist agents"""
        self.agents = {
            "general_knowledge": GeneralKnowledgeAgent(),
            "document_comparison": DocumentComparisonAgent(),
            "question_generator": QuestionGeneratorAgent(),
            "information_extractor": InformationExtractorAgent(),
            "comparison_analyst": ComparisonAnalystAgent()
        }
    
    def get_agent(self, agent_type: str) -> Optional[BaseSpecialistAgent]:
        """Get a specialist agent by type"""
        return self.agents.get(agent_type)
    
    async def process_with_agent(self, agent_type: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query with a specific agent"""
        agent = self.get_agent(agent_type)
        if not agent:
            return {
                "agent_type": agent_type,
                "response": f"Agent type '{agent_type}' not found",
                "status": "error"
            }
        
        return await agent.process(query, context)
    
    async def process_pipeline(self, pipeline: List[str], query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query through a pipeline of agents"""
        results = []
        current_context = context or {}
        
        for agent_type in pipeline:
            print(f"Processing with {agent_type}...")
            
            result = await self.process_with_agent(agent_type, query, current_context)
            results.append(result)
            
            # Update context with results for next agent in pipeline
            current_context["previous_results"] = results
            current_context["last_agent_result"] = result
        
        # Combine results from pipeline
        final_response = self._combine_pipeline_results(results, query)
        
        return {
            "agent_type": "pipeline",
            "pipeline": pipeline,
            "response": final_response,
            "individual_results": results,
            "status": "success"
        }
    
    def _combine_pipeline_results(self, results: List[Dict[str, Any]], query: str) -> str:
        """Combine results from multiple agents in pipeline"""
        if not results:
            return "No results from pipeline"
        
        if len(results) == 1:
            return results[0].get("response", "No response")
        
        # For multiple results, create a structured response
        combined = f"Pipeline Analysis for: '{query}'\n\n"
        
        for i, result in enumerate(results, 1):
            agent_type = result.get("agent_type", f"Agent {i}")
            response = result.get("response", "No response")
            combined += f"{i}. {agent_type.upper()}:\n{response}\n\n"
        
        return combined


# Singleton instance
agent_registry = AgentRegistry()