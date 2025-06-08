import json
from typing import Dict, List, Optional, Tuple, Any
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

from .config import AppConfig, MCPConfig, AgentPrompts, DocumentType, Role

class AgentManager:
    """Manages all AI agents and their interactions."""
    
    def __init__(self):
        self.coordinator_agent: Optional[LlmAgent] = None
        self.general_agent: Optional[LlmAgent] = None
        self.question_generator_agent: Optional[LlmAgent] = None
        self.information_extractor_agent: Optional[LlmAgent] = None
        self.comparison_agent: Optional[LlmAgent] = None
        self.runner: Optional[Runner] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize all agents and runner."""
        if self._initialized:
            return
        
        self.coordinator_agent = await self._create_coordinator_agent()
        self.general_agent = await self._create_general_agent()
        self.question_generator_agent = await self._create_question_generator_agent()
        self.information_extractor_agent = await self._create_information_extractor_agent()
        self.comparison_agent = await self._create_comparison_agent()
        
        session_service = InMemorySessionService()
        self.runner = Runner(
            app_name=AppConfig.APP_NAME,
            agent=self.coordinator_agent,
            session_service=session_service,
        )
        session_service.create_session(
            app_name=AppConfig.APP_NAME,
            user_id=AppConfig.USER_ID,
            session_id=AppConfig.SESSION_ID
        )
        
        self._initialized = True
    
    async def _create_coordinator_agent(self) -> LlmAgent:
        """Create the coordinator agent."""
        general_agent = LlmAgent(
            name="general_assistant",
            model=AppConfig.MODEL_NAME,
            description="Helpful AI assistant for general questions and tasks"
        )
        
        pdf_comparison_agent = LlmAgent(
            name="pdf_comparison_specialist", 
            model=AppConfig.MODEL_NAME,
            description="Specialist for comparing PDF documents"
        )
        
        return LlmAgent(
            name="coordinator",
            model=AppConfig.MODEL_NAME,
            description=AgentPrompts.COORDINATOR,
            sub_agents=[general_agent, pdf_comparison_agent]
        )
    
    async def _create_general_agent(self) -> LlmAgent:
        """Create the general knowledge agent."""
        return LlmAgent(
            name="general_assistant",
            model=AppConfig.MODEL_NAME,
            description=AgentPrompts.GENERAL
        )
    
    async def _create_question_generator_agent(self) -> LlmAgent:
        """Create the question generator agent."""
        return LlmAgent(
            name="question_generator",
            model=AppConfig.MODEL_NAME,
            description=AgentPrompts.QUESTION_GENERATOR
        )
    
    async def _create_information_extractor_agent(self) -> LlmAgent:
        """Create the information extractor agent."""
        return LlmAgent(
            name="information_extractor",
            model=AppConfig.MODEL_NAME,
            description=AgentPrompts.INFORMATION_EXTRACTOR
        )
    
    async def _create_comparison_agent(self) -> LlmAgent:
        """Create the comparison agent."""
        return LlmAgent(
            name="comparison_analyst",
            model=AppConfig.MODEL_NAME,
            description=AgentPrompts.COMPARISON
        )
    
    async def run_agent(self, agent: LlmAgent, prompt: str) -> str:
        """Run a specific agent with a prompt."""
        await self.initialize()
        
        original_agent = self.runner.agent
        self.runner.agent = agent
        
        try:
            events = [
                e async for e in self.runner.run_async(
                    user_id=AppConfig.USER_ID,
                    session_id=AppConfig.SESSION_ID,
                    new_message=types.Content(
                        role=Role.USER, 
                        parts=[types.Part(text=prompt)]
                    ),
                )
            ]
            return events[-1].content.parts[0].text if events else "(no response)"
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                return "Rate limit exceeded. Please try again in a moment."
            return f"Error: {e}"
        finally:
            self.runner.agent = original_agent
    
    async def parse_json_response(self, response: str) -> Dict:
        """Safely parse JSON response from agent."""
        try:
            # Try to find JSON in the response
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end != -1:
                    json_str = response[start:end].strip()
                    return json.loads(json_str)
            
            # Try to find plain JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
                
        except Exception:
            pass
        
        return {}
    
    def get_fallback_questions(self, prompt: str, pdf_contents: List[Tuple[str, str]]) -> List[str]:
        """Get fallback questions based on document content."""
        # Check document type based on keywords
        all_text = prompt.lower() + " " + " ".join([content.lower() for _, content in pdf_contents])
        
        if any(word in all_text for word in ['lease', 'rent', 'tenant', 'landlord']):
            return DocumentType.FALLBACK_QUESTIONS['lease']
        elif any(word in all_text for word in ['contract', 'agreement', 'terms', 'conditions']):
            return DocumentType.FALLBACK_QUESTIONS['contract']
        elif any(word in all_text for word in ['policy', 'procedure', 'guidelines', 'rules']):
            return DocumentType.FALLBACK_QUESTIONS['policy']
        else:
            return DocumentType.FALLBACK_QUESTIONS['generic']

class MCPAgentManager:
    """Manages MCP-based agents for simple use cases."""
    
    def __init__(self):
        self.agent = None
        self.runner = None
        self.exit_stack = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize MCP agent."""
        if self._initialized:
            return
        
        try:
            remote_tools, self.exit_stack = await MCPToolset.from_server(
                connection_params=SseServerParams(url=MCPConfig.SERVER_URL)
            )
            
            from google.adk.agents import Agent
            self.agent = Agent(
                name="calculator_agent",
                model="gemini-2.0-flash",
                description="A mathematician agent and general knowledge agent",
                instruction=(
                    "You are a mathematician and general knowledge agent. "
                    "You can find roots of equations, or solve high school math problems. "
                    "You can use the tools to help you with your tasks."
                ),
                tools=remote_tools
            )
            
            session_service = InMemorySessionService()
            self.runner = Runner(
                app_name="Math APP",
                agent=self.agent,
                session_service=session_service
            )
            
            if not session_service.get_session(
                app_name="Math APP",
                user_id="anhld",
                session_id="anhld-session-01"
            ):
                session_service.create_session(
                    app_name="Math APP",
                    user_id="anhld", 
                    session_id="anhld-session-01"
                )
            
            self._initialized = True
            
        except Exception as e:
            print(f"Failed to initialize MCP agent: {e}")
            raise
    
    async def run(self, prompt: str) -> str:
        """Run the MCP agent with a prompt."""
        await self.initialize()
        
        try:
            events = [
                event async for event in self.runner.run_async(
                    user_id="anhld",
                    session_id="anhld-session-01",
                    new_message=types.Content(
                        role="user",
                        parts=[types.Part(text=prompt)]
                    )
                )
            ]
            
            if events:
                return events[-1].content.parts[0].text
            return "(no response)"
            
        except Exception as e:
            return f"Error: {e}"
    
    async def cleanup(self):
        """Clean up resources."""
        if self.exit_stack:
            await self.exit_stack.aclose()
    
    async def update_toolset(self):
        """Update the toolset from MCP server."""
        if self.exit_stack:
            await self.exit_stack.aclose()
        
        new_tools, self.exit_stack = await MCPToolset.from_server(
            connection_params=SseServerParams(url=MCPConfig.SERVER_URL)
        )
        
        if self.agent:
            self.agent.tools = new_tools