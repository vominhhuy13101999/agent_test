"""
Multi-Agent Orchestrator - Main orchestration layer for coordinating all agents
"""
from typing import Dict, Any, Optional, List
import asyncio

from .coordinator_agent import CoordinatorAgent, AgentType, coordinator_agent
from .specialist_agents import AgentRegistry, agent_registry


class MultiAgentOrchestrator:
    """
    Main orchestrator that manages the complete multi-agent workflow:
    1. Coordinator analyzes query and determines routing
    2. Specialist agents process in sequence or pipeline
    3. Results are combined and returned
    """
    
    def __init__(self):
        self.coordinator = coordinator_agent
        self.agent_registry = agent_registry
        self.session_context: Dict[str, Any] = {}
    
    async def initialize(self):
        """Initialize all agents in the system"""
        print("🚀 Initializing Multi-Agent System...")
        
        # Initialize coordinator agent
        await self.coordinator._initialize_agent()
        print("✅ Coordinator Agent initialized")
        
        # Initialize specialist agents
        await self.agent_registry._initialize_agents()
        print("✅ Specialist Agents initialized")
        
        print("🎯 Multi-Agent System ready!")
    
    async def process_query(self, 
                          query: str, 
                          session_id: str = "default",
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a query through the complete multi-agent system
        
        Args:
            query: User's query
            session_id: Session identifier for context persistence
            context: Additional context (documents, previous results, etc.)
            
        Returns:
            Complete response with routing decisions and results
        """
        print(f"🔍 Processing query: '{query[:100]}...'")
        
        # Get or create session context
        session_context = self._get_session_context(session_id)
        if context:
            session_context.update(context)
        
        try:
            # Step 1: Coordinator analyzes query and determines routing
            routing_decision = await self.coordinator.route_query(query, session_context)
            print(f"🎯 Routing decision: {routing_decision['agent_type']} - {routing_decision['reasoning']}")
            
            # Step 2: Process with appropriate specialist agent(s)
            if routing_decision.get("pipeline"):
                # Pipeline processing for document workflows
                result = await self._process_pipeline(
                    routing_decision["pipeline"], 
                    query, 
                    session_context
                )
            else:
                # Single agent processing
                result = await self._process_single_agent(
                    routing_decision["agent_type"],
                    query,
                    session_context
                )
            
            # Step 3: Update session context and return results
            self._update_session_context(session_id, routing_decision, result)
            
            return {
                "query": query,
                "routing_decision": routing_decision,
                "result": result,
                "session_id": session_id,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Error in multi-agent processing: {e}")
            return {
                "query": query,
                "error": str(e),
                "session_id": session_id,
                "status": "error"
            }
    
    async def _process_single_agent(self, 
                                  agent_type: AgentType, 
                                  query: str, 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Process query with a single specialist agent"""
        agent_type_str = agent_type.value if isinstance(agent_type, AgentType) else str(agent_type)
        
        print(f"🤖 Processing with single agent: {agent_type_str}")
        
        result = await self.agent_registry.process_with_agent(
            agent_type_str, 
            query, 
            context
        )
        
        return result
    
    async def _process_pipeline(self, 
                              pipeline: List[AgentType], 
                              query: str, 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Process query through a pipeline of specialist agents"""
        pipeline_str = [agent.value if isinstance(agent, AgentType) else str(agent) for agent in pipeline]
        
        print(f"🔄 Processing pipeline: {' → '.join(pipeline_str)}")
        
        result = await self.agent_registry.process_pipeline(
            pipeline_str, 
            query, 
            context
        )
        
        return result
    
    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get context for a specific session"""
        if session_id not in self.session_context:
            self.session_context[session_id] = {
                "session_id": session_id,
                "history": [],
                "documents_uploaded": False,
                "previous_agent": None
            }
        
        return self.session_context[session_id].copy()
    
    def _update_session_context(self, 
                              session_id: str, 
                              routing_decision: Dict[str, Any], 
                              result: Dict[str, Any]):
        """Update session context with latest interaction"""
        if session_id not in self.session_context:
            self.session_context[session_id] = {}
        
        # Add to history
        interaction = {
            "timestamp": asyncio.get_event_loop().time(),
            "routing_decision": routing_decision,
            "result": result
        }
        
        if "history" not in self.session_context[session_id]:
            self.session_context[session_id]["history"] = []
        
        self.session_context[session_id]["history"].append(interaction)
        
        # Update previous agent
        if isinstance(routing_decision.get("agent_type"), AgentType):
            self.session_context[session_id]["previous_agent"] = routing_decision["agent_type"].value
        else:
            self.session_context[session_id]["previous_agent"] = str(routing_decision.get("agent_type"))
    
    def add_documents_to_session(self, session_id: str, document_info: Dict[str, Any]):
        """Add document information to session context"""
        session_context = self._get_session_context(session_id)
        session_context["documents_uploaded"] = True
        session_context["document_info"] = document_info
        self.session_context[session_id] = session_context
        
        print(f"📄 Documents added to session {session_id}")
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get interaction history for a session"""
        session_context = self._get_session_context(session_id)
        return session_context.get("history", [])
    
    def clear_session(self, session_id: str):
        """Clear session context"""
        if session_id in self.session_context:
            del self.session_context[session_id]
            print(f"🧹 Session {session_id} cleared")
    
    async def get_available_agents(self) -> Dict[str, str]:
        """Get information about available agents"""
        return {
            "coordinator": "Analyzes queries and routes to appropriate specialists",
            "general_knowledge": "Handles mathematical problems and general knowledge questions",
            "document_comparison": "Compares documents and analyzes differences",
            "question_generator": "Creates targeted questions from document content",
            "information_extractor": "Extracts specific information from documents",
            "comparison_analyst": "Provides structured analysis and comparison of data"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health status of all agents"""
        health_status = {
            "coordinator": "healthy",
            "specialist_agents": {},
            "overall_status": "healthy"
        }
        
        # Check coordinator
        try:
            if self.coordinator.agent:
                health_status["coordinator"] = "healthy"
            else:
                health_status["coordinator"] = "not_initialized"
        except Exception as e:
            health_status["coordinator"] = f"error: {str(e)}"
        
        # Check specialist agents
        for agent_type in ["general_knowledge", "document_comparison", "question_generator", 
                          "information_extractor", "comparison_analyst"]:
            try:
                agent = self.agent_registry.get_agent(agent_type)
                if agent and agent.agent:
                    health_status["specialist_agents"][agent_type] = "healthy"
                else:
                    health_status["specialist_agents"][agent_type] = "not_initialized"
            except Exception as e:
                health_status["specialist_agents"][agent_type] = f"error: {str(e)}"
        
        # Determine overall status
        if any("error" in status for status in health_status["specialist_agents"].values()):
            health_status["overall_status"] = "degraded"
        elif health_status["coordinator"] != "healthy":
            health_status["overall_status"] = "degraded"
        
        return health_status


# Singleton instance
orchestrator = MultiAgentOrchestrator()