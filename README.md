# Multi-Agent Document Analysis Platform with RAG-Enhanced Knowledge System

## Project Overview

This project is a **comprehensive multi-agent AI platform** that implements a sophisticated **Coordinator Agent** with specialized document analysis agents through **unified MCP (Model Control Protocol) integration**. Built with Google's Agent Development Kit (ADK), it demonstrates advanced multi-agent coordination where a Coordinator Agent analyzes queries and routes them to appropriate specialist agents, with document processing flowing through intelligent pipelines.

## Architecture Philosophy

The platform follows a **Coordinator-Specialist Agent Architecture** with:

1. **Coordinator Agent**: AI-powered coordinator that analyzes queries and routes to appropriate specialists
2. **Sequential Processing**: Coordinator → Specialist Agent → Response  
3. **Pipeline Processing**: Within specialists, documents flow through Extract → Analyze → Compare pipelines
4. **Unified MCP Integration**: Single server providing both mathematical tools and RAG document analysis
5. **API-First Design**: RESTful API as primary interface with Gradio web UI for rich interactions

## 🤖 Multi-Agent Architecture

### Core Agent System

#### **Coordinator Agent** 🎯
- **AI-Powered Routing**: Analyzes query content and determines optimal specialist agent
- **Intelligent Decision Making**: Uses both rule-based and AI-based routing strategies
- **Pipeline Orchestration**: Determines multi-step processing workflows for complex queries
- **Context Awareness**: Considers session history and available documents for routing

#### **General Knowledge Agent** 🧠
- **Mathematical Problem Solving**: Equation solving, calculations, step-by-step explanations
- **General Knowledge**: Science, technology, history, arts, culture, finance, health, law
- **Calculator Tools**: Advanced mathematical computation via MCP integration
- **Knowledge Base Access**: Comprehensive domain expertise (RAG)

#### **Document Specialist Agents** 📄

**Document Comparison Specialist**:
- Analyzes and compares PDF documents with structured difference analysis
- Provides side-by-side comparisons with highlighted changes
- Supports multi-document comparison workflows

**Question Generator**:
- Creates targeted questions based on document content
- Generates questions for different difficulty levels and purposes
- Adapts questioning style to document type (legal, technical, financial)

**Information Extractor**:
- Extracts specific information and data from documents
- Identifies entities, facts, figures, and key data points  
- Provides structured data extraction with source citations

**Comparison Analyst**:
- Provides structured document comparisons and trend analysis
- Generates analytical reports with data visualization concepts
- Performs risk assessment and impact analysis

### 🔧 Unified MCP Integration

**Single MCP Server Architecture** (Port 17324):
```
MCP Server (127.0.0.1:17324/mcp-server/sse)
├── Mathematical Tools
│   ├── Calculator functions
│   ├── Equation solvers  
│   ├── Statistical operations
│   └── Mathematical constants
└── Document Tools
    ├── Semantic search

```

**Filtered Tool Access**:
- **Knowledge Agent**: `["calculator", "math_solver", "semantic_search"]`
- **Document Agents**: `[]`
- **Shared Tools**: `[]` - accessible by both agent types

### 📄 Document Processing Pipeline

**Pipeline Flow for Document comparision Queries**:
```
Document Query (for comparision only) → Coordinator Agent → Pipeline Determination
                                  ↓
Information Extractor → Document Specialist → Comparison Analyst
                     ↓                     ↓                    ↓
              Extract Data         Analyze Content      Generate Report
```
**Pipeline Flow for Document retrieval Queries**:
```
Document Query (for retrieval only) → Coordinator Agent → general knowledge agent (use with RAG funtionality)
                                  
```
**Universal Document Support**:
- PDFs, DOCX, TXT, and other formats using Docling
- Intelligent text extraction with error handling
- Multi-document simultaneous processing
- Context-aware analysis with document type detection

## 🌐 Interface Architecture

### **Primary API** (FastAPI)
- RESTful endpoints for all agent capabilities
- Automatic routing through Coordinator Agent
- Session management across multiple agents
- Tool management and MCP coordination

### **Gradio Web UI**
- Rich document upload and analysis interface
- Real-time chat with multi-agent coordination
- Visual pipeline progress indicators
- Multi-document comparison workflows

### **CLI Interface**  
- Development and testing interface
- Agent inspection and health monitoring
- Direct multi-agent system interaction
- Debugging and development workflows

## Agent Coordination Flow

### 1. **Query Analysis and Routing**
```
User Query → Coordinator Agent → Content Analysis → Agent Selection
                              ↓
Rule-based Quick Route ← AI-powered Analysis → Pipeline Determination
```

### 2. **Sequential Processing**
```
Coordinator Decision → Specialist Agent → Processing → Response
```

### 3. **Pipeline Processing** (Document comparision Workflows)
```
Complex Document Query → Information Extractor → Document Specialist → Comparison Analyst
                                            ↓                      ↓                    ↓
                                    Extract Content    Analyze/Compare Content    Generate Report
```
### 4. **Pipeline Processing 2** (Document retrieval Workflows)
```
Complex Document Query → general knowledge agent -> use rag -> response
```



## Installation and Setup

### Prerequisites
- Python 3.12+
- UV package manager ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))

### Quick Start

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd agent_test
   uv sync
   ```

2. **Configure Environment**
   
   Create `src/core/.env`:
   ```env
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=<your-google-ai-studio-key>
   MCP_SERVER_URL=http://127.0.0.1:17324/mcp-server/sse
   AGENT_MODEL=gemini-2.5-flash-preview-05-20
   USE_RAG=TRUE
   RAG_SIMILARITY_THRESHOLD=0.7
   MAX_CONTEXT_LENGTH=4000
   ```

3. **Start Unified MCP Server**
   ```bash
   # Start the unified MCP server on port 17324
   # This provides both mathematical and document analysis tools
   ```

## Usage

### **Primary: API Integration**

#### Start Multi-Agent API Server
```bash
# Start the FastAPI server with multi-agent coordination
python src/server.py
# Available at: http://localhost:8756
```

#### **Core API Endpoints**

**Multi-Agent Chat**:
```bash
POST /agent/chat
{
  "user_id": "user123",
  "session_id": "session456", 
  "message": "Compare the financial terms in these two contracts",
  "use_rag": true
}

# Response includes routing information:
{
  "response": "Analysis results...",
  "routing": "document_comparison",
  "pipeline": ["information_extractor", "document_comparison", "comparison_analyst"]
}
```

**Agent Management**:
```bash
GET /tools/tools          # List all available tools from unified MCP server
POST /tools/update-toolset # Refresh MCP server connection and tool discovery
```

### **Web UI: Gradio Interface**

#### Launch Multi-Agent Document Analysis UI
```bash
# Start Gradio interface with multi-agent coordination
uv run gradio_app.py
# Available at: http://localhost:7860

# Features:
# - Multi-agent query processing with pipeline visualization
# - Document upload with automatic routing to document specialists
# - Real-time agent coordination display
# - Pipeline progress tracking
```

### **Development: Multi-Agent CLI**
```bash
# Start CLI with full multi-agent system
uv run main.py

# Multi-Agent Commands:
# - 'exit': Quit application
# - 'check': Show all agents and their health status
# - 'agents': List specialist agents and their capabilities
# - 'health': Detailed system health check
# - Any query: Process through Coordinator Agent with routing display
```

## Multi-Agent Workflow Examples

### 1. **Mathematical Problem** (Knowledge Agent)
```bash
Query: "Solve the quadratic equation x^2 - 5x + 6 = 0"

Coordinator Analysis:
- Detects mathematical equation pattern
- Routes to: General Knowledge Agent
- Pipeline: None (single agent processing)

Result: Step-by-step solution with explanations
```

### 2. **Document Comparison** (Pipeline Processing)
```bash
Query: "Compare the liability clauses in these two contracts"

Coordinator Analysis:
- Detects comparison + documents context
- Routes to: Document Comparison Specialist  
- Pipeline: Information Extractor → Document Comparison → Comparison Analyst

Workflow:
1. Information Extractor: Locates liability clauses in both documents
2. Document Comparison: Analyzes differences between clauses
3. Comparison Analyst: Generates structured comparison report
```

### 3. **Question Generation** (Document Pipeline)
```bash
Query: "Generate study questions from this technical manual"

Coordinator Analysis:
- Detects question generation request + document
- Routes to: Question Generator
- Pipeline: Information Extractor → Question Generator

Workflow:
1. Information Extractor: Analyzes manual content and structure
2. Question Generator: Creates targeted questions by topic and difficulty
```

### 4. **Cross-Domain Analysis** (Hybrid Processing)
```bash
Query: "Explain the mathematical models in this research paper and calculate example values"

Coordinator Analysis:
- Detects hybrid mathematical + document query
- Routes to: use RAG (first) → General Knowledge Agent (second)

Workflow:
1. use RAG: Extracts mathematical models from paper
2. General Knowledge Agent: Explains models and performs calculations
3. Combined response with document citations and calculations
```

## Configuration

### **Multi-Agent System Configuration**
```python
# src/core/config.py
AGENT_TOOLS = {
    "knowledge_agent": ["calculator", "math_solver", "semantic_search"],
    "document_agent": [],
    "shared_tools": []
}

# Agent routing configuration
QUICK_ROUTE_PATTERNS = {
    "mathematical": [r'\d+\s*[\+\-\*\/\^]\s*\d+', r'solve.*equation'],
    "comparison": ["compare", "difference", "contrast", "versus"],
    "extraction": ["extract", "find", "get information"]
}
```

### **Coordinator Agent Prompts**
```python
COORDINATOR_PROMPT = """
You are an intelligent coordinator that analyzes queries and routes to specialists:
- GENERAL_KNOWLEDGE: Mathematical problems, science, general questions
- DOCUMENT_COMPARISON: Comparing documents, analyzing differences  
- QUESTION_GENERATOR: Creating questions from document content
- INFORMATION_EXTRACTOR: Extracting specific data from documents
- COMPARISON_ANALYST: Structured analysis and comparison
"""
```

### **Pipeline Definitions**
```python
AGENT_PIPELINES = {
    "document_comparison": [
        "information_extractor", 
        "document_comparison", 
        "comparison_analyst"
    ],
    "question_generator": [
        "information_extractor", 
        "question_generator"
    ]
}
```

## Dependencies

### **Core Multi-Agent System** (Required)
```toml
# Agent Development Kit and MCP
google-adk = ">=0.4.0"

# API Framework  
fastapi = ">=0.115.12"
uvicorn = ">=0.34.2"
chainlit = ">=2.5.5"

# LLM Integration
litellm = ">=1.70.0"

# Document Processing (Required for full functionality)
docling = ">=2.15.1"
pdfplumber = ">=0.11.6"
python-docx = ">=1.1.2"
docx2txt = ">=0.9"

# NLP and Text Processing (Required for RAG)
fuzzywuzzy = ">=0.18.0"
spacy = ">=3.8.4"
transformers = ">=4.51.3"

# Web UI (Required for Gradio interface)
gradio = ">=5.33.0"

# Utilities
python-dotenv = ">=1.0.0"
```

## Development and Extension

### **Adding New Specialist Agents**
```python
# 1. Create new specialist agent
class NewSpecialistAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__("new_specialist")
    
    def get_instruction(self) -> str:
        return "Specialized instruction for new agent type"

# 2. Add to Coordinator routing logic
AGENT_ROUTING_RULES = {
    "new_domain_query": "new_specialist"
}

# 3. Register in AgentRegistry
def _initialize_agents(self):
    self.agents["new_specialist"] = NewSpecialistAgent()
```

### **Extending Pipeline Processing**
```python
# Define new pipeline for complex workflows
NEW_PIPELINE = [
    "information_extractor",
    "new_specialist", 
    "comparison_analyst"
]

# Add to Coordinator pipeline determination
def get_pipeline_for_agent(self, agent_type, query, context):
    if "new_workflow" in query.lower():
        return NEW_PIPELINE
```

### **MCP Tool Integration**
```python
# Add new tools to unified MCP server
NEW_TOOLS = ["domain_analyzer", "specialized_processor"]

# Update agent tool access
AGENT_TOOLS["new_specialist"] = ["semantic_search", "domain_analyzer"]
```

## Troubleshooting

### **Multi-Agent System Issues**
```bash
# Check system health
GET /health  # API endpoint
# or
> health    # CLI command

# Check agent coordination
GET /tools/tools  # Verify all agents have access to tools
> agents          # CLI - List all agents and capabilities
```

### **Coordinator Routing Issues**
```bash
# Debug routing decisions
> check     # CLI - Show routing decision for last query

# Test specific agent routing
POST /agent/chat {"message": "test query", "debug_routing": true}
```

### **Pipeline Processing Issues**
```bash
# Monitor pipeline execution
> health    # Check individual agent health
# Look for pipeline execution logs in API/CLI output

# Test individual pipeline steps
# Route directly to specific agents for debugging
```

## Advanced Features

### **Intelligent Session Management**
- **Cross-Agent Context**: Session context shared across all specialist agents
- **Pipeline State**: Maintains state throughout multi-step document processing
- **History Tracking**: Complete interaction history with routing decisions

### **Dynamic Agent Coordination**
- **Load Balancing**: Automatic distribution of work across available agents
- **Failure Recovery**: Automatic fallback when specialist agents are unavailable
- **Performance Monitoring**: Real-time monitoring of agent response times

### **Enhanced Document Processing**
- **Multi-Modal Analysis**: Support for images, charts, and tables in documents
- **Batch Processing**: Efficient handling of multiple document workflows
- **Version Comparison**: Track changes across document versions

## Future Enhancements

### **Planned Multi-Agent Extensions**
- **Research Agent**: Academic paper analysis with citation networks
- **Financial Agent**: Advanced financial modeling and analysis with market data
- **Legal Agent**: Contract analysis with legal precedent integration
- **Technical Agent**: Code analysis and technical documentation processing

### **Advanced Coordination Features**
- **Parallel Processing**: Multiple agents working simultaneously on complex queries
- **Agent Learning**: Coordinators learning from routing decisions and outcomes
- **Dynamic Pipeline Generation**: AI-powered pipeline creation for novel workflows

### **Enterprise Integration**
- **Workflow Automation**: Integration with business process management systems
- **Advanced Analytics**: Deep insights into multi-agent coordination patterns
- **Scalability**: Distributed multi-agent processing across cloud infrastructure

This multi-agent platform provides a sophisticated foundation for intelligent document analysis and knowledge processing, with the Coordinator Agent ensuring optimal routing and the specialist agents delivering targeted expertise through intelligent pipeline processing.

---

# Git Merge Strategy & Code Integration Plan

## Current Merge Situation Analysis

### Branch Context
- **Current Branch**: `test_h_v1`
- **Target Branch**: `main`
- **Merge Type**: Feature integration with architectural changes

### Conflicted Files Status
1. **main.py** - ✅ Ready (no conflicts detected)
2. **pyproject.toml** - ✅ Ready (no conflicts detected)
3. **multi_tool_agent/agent.py** - 🗑️ Deleted (needs removal from index)
4. **uv.lock** - ⚠️ Merge conflict pending

### New Architecture Files (Added)
- `src/agent/` - New agent architecture
- `src/chat/` - Chat management system
- `src/core/` - Core configuration and utilities
- `src/services/` - Service layer implementations
- `src/tool/` - Tool management system
- `src/agents/` - Untracked specialist agents directory

## Merge Strategy & Functionality Design

### 1. **Architecture Migration Strategy**

#### From: Legacy Multi-Tool Agent
```
multi_tool_agent/
├── __init__.py (DELETED)
├── agent.py (DELETED - conflicts resolved)
└── .env (legacy config)
```

#### To: Modern Modular Architecture
```
src/
├── agent/          # Core agent implementations
├── chat/           # Chat interface and controllers
├── core/           # Configuration and utilities
├── services/       # Business logic services
├── tool/           # Tool management and MCP integration
├── agents/         # Specialist agent implementations
└── server.py       # FastAPI server entry point
```

### 2. **Functionality Preservation & Enhancement**

#### Core Functionality Mapping
| Legacy Component | New Component | Enhancement |
|------------------|---------------|-------------|
| `multi_tool_agent/agent.py` | `src/agent/agent.py` | Modular design with better separation |
| Single agent system | Multi-agent orchestrator | Coordinator + Specialist architecture |
| Basic MCP tools | Filtered tool access | Role-based tool permissions |
| Simple CLI | Enhanced interfaces | API + Web UI + CLI |

#### Key Functionality Preserved
- ✅ **MCP Integration**: Unified server communication maintained  
- ✅ **Tool Access**: Calculator, semantic search, math solver tools
- ✅ **Environment Configuration**: `.env` loading and validation
- ✅ **Session Management**: User/session tracking capabilities
- ✅ **Error Handling**: Comprehensive error management system

#### New Functionality Added
- 🆕 **Multi-Agent Coordination**: Intelligent query routing
- 🆕 **Document Processing Pipelines**: Sequential specialist processing
- 🆕 **RESTful API**: FastAPI server with comprehensive endpoints
- 🆕 **Web Interface**: Gradio-based document analysis UI
- 🆕 **Enhanced CLI**: Multi-agent system monitoring and control

### 3. **Merge Resolution Plan**

#### Phase 1: Clean Up Legacy Components
```bash
# Remove deleted files from git index
git rm multi_tool_agent/__init__.py
git rm multi_tool_agent/agent.py

# Verify old directory removal
rm -rf multi_tool_agent/  # if needed
```

#### Phase 2: Resolve Lock File Conflicts
```bash
# Strategy for uv.lock:
# 1. Accept new architecture dependencies
# 2. Preserve existing working package versions
# 3. Resolve version conflicts with UV's dependency resolution
uv lock --upgrade  # after merge resolution
```

#### Phase 3: Integration Validation
```bash
# Test suite execution order:
1. Environment configuration validation
2. MCP server connectivity test  
3. Agent initialization test
4. Tool access verification
5. API endpoint functionality
6. Web UI launch verification
```

### 4. **Migration Compatibility**

#### Backward Compatibility Strategy
- **Environment Variables**: Maintained existing `.env` format with additions
- **CLI Interface**: Enhanced but maintains familiar commands
- **Tool Access**: All existing tools remain available
- **Session Management**: Existing session data structure preserved

#### Breaking Changes (Intentional)
- **Import Paths**: `multi_tool_agent.agent` → `src.agent.agent`
- **Configuration Location**: `multi_tool_agent/.env` → `src/core/.env`
- **Entry Points**: Multiple interfaces instead of single `main.py`

### 5. **Post-Merge Validation Checklist**

#### Core System Tests
- [ ] MCP server connection established
- [ ] All required environment variables loaded
- [ ] Agent initialization without errors
- [ ] Tool filtering working correctly
- [ ] Session service operational

#### Interface Tests  
- [ ] CLI multi-agent system functional
- [ ] FastAPI server starts and responds
- [ ] Gradio web UI launches successfully
- [ ] All API endpoints return valid responses

#### Integration Tests
- [ ] Coordinator routing decisions
- [ ] Pipeline processing workflows
- [ ] Document upload and analysis
- [ ] Mathematical problem solving
- [ ] RAG document retrieval

### 6. **Rollback Strategy**

#### If Merge Issues Arise
```bash
# Emergency rollback procedure:
git merge --abort  # if mid-merge
git reset --hard HEAD~1  # if merge completed but broken
git checkout main  # return to stable state

# Alternative: Create fix branch
git checkout -b fix-merge-issues
# Implement targeted fixes
# Test thoroughly before re-merging
```

#### Recovery Verification
- All original functionality restored
- No data loss in existing sessions
- MCP server connectivity maintained
- Environment configuration intact

### 7. **Success Criteria**

#### Technical Validation
- ✅ All imports resolve correctly
- ✅ No circular dependency issues  
- ✅ Environment variables load properly
- ✅ MCP tools accessible to appropriate agents
- ✅ API responses match expected schemas

#### Functional Validation  
- ✅ Mathematical queries route to knowledge agent
- ✅ Document queries route to appropriate specialists
- ✅ Pipeline processing executes in correct sequence
- ✅ Web UI handles document uploads and analysis
- ✅ CLI provides system monitoring capabilities

This merge strategy ensures a smooth transition from the legacy single-agent system to the modern multi-agent architecture while preserving all existing functionality and adding significant new capabilities.

---

# System Testing Guide

## Complete Testing Protocol

Follow these steps to thoroughly test the multi-agent system after installation or deployment.

### Prerequisites Verification

#### 1. **Environment Setup Test**
```bash
# Check Python version (>=3.12 required)
python --version

# Verify UV package manager
uv --version

# Check project dependencies
uv sync
```

#### 2. **Configuration Validation**
```bash
# Test core configuration loading
python -c "
from src.core.config import config
print('✅ Config loaded successfully')
print(f'MCP Server URL: {config.get_mcp_server_url()}')
print(f'Agent Model: {config.get_agent_model()}')
print(f'RAG Enabled: {config.get_use_rag()}')
"
```

#### 3. **Import Validation**
```bash
# Test all critical imports
python -c "
try:
    from src.agent.agent import get_agent
    from src.server import app
    from src.core.config import config
    from src.agents.multi_agent_orchestrator import orchestrator
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
"
```

### Core System Testing

#### 4. **MCP Server Connectivity Test**
```bash
# Test MCP server connection (requires MCP server running on port 17324)
python -c "
import asyncio
from src.agent.agent import get_agent

async def test_mcp():
    try:
        agent = await get_agent()
        if agent.tools and len(agent.tools) > 0:
            tools = await agent.tools[0].get_tools()
            print(f'✅ MCP Connection: {len(tools)} tools available')
            for tool in tools[:3]:  # Show first 3 tools
                print(f'  - {tool._get_declaration().name}')
        else:
            print('⚠️  No MCP tools found (server may be offline)')
    except Exception as e:
        print(f'❌ MCP Connection failed: {e}')

asyncio.run(test_mcp())
"
```

#### 5. **Multi-Agent System Health Check**
```bash
# Test multi-agent orchestrator initialization
python -c "
import asyncio
from src.agents.multi_agent_orchestrator import orchestrator

async def test_orchestrator():
    try:
        await orchestrator.initialize()
        health = await orchestrator.health_check()
        print('✅ Multi-Agent System Health:')
        print(f'  Overall Status: {health[\"overall_status\"]}')
        print(f'  Coordinator: {health[\"coordinator\"]}')
        print('  Specialist Agents:')
        for agent, status in health['specialist_agents'].items():
            print(f'    - {agent}: {status}')
    except Exception as e:
        print(f'❌ Orchestrator test failed: {e}')

asyncio.run(test_orchestrator())
"
```

### Interface Testing

#### 6. **CLI Interface Test**
```bash
# Test CLI with automated input
echo 'What is 2 + 2?
check
agents
health
exit' | python main.py

# Expected output should show:
# - Multi-agent system initialization
# - Mathematical query routing to knowledge agent
# - System health information
# - Available specialist agents list
```

#### 7. **FastAPI Server Test**
```bash
# Start server in background (Terminal 1)
python src/server.py &
SERVER_PID=$!

# Wait for server startup
sleep 5

# Test API endpoints (Terminal 2)
# Health check
curl -X GET "http://localhost:8756/health"

# Chat endpoint test
curl -X POST "http://localhost:8756/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "session_id": "test_session",
    "message": "What is the square root of 16?",
    "use_rag": false
  }'

# Tools endpoint test
curl -X GET "http://localhost:8756/tools/tools"

# Cleanup
kill $SERVER_PID
```

#### 8. **Gradio Web UI Test**
```bash
# Test web interface (requires gradio_app.py)
# This will start the UI at http://localhost:7860
python -c "
try:
    import gradio as gr
    print('✅ Gradio available')
    # Note: Full UI test requires manual interaction
    print('Run: uv run gradio_app.py to test web interface')
except ImportError:
    print('❌ Gradio not available')
"
```

### Functional Testing

#### 9. **Agent Routing Test**
```bash
# Test coordinator routing decisions
python -c "
import asyncio
from src.agents.multi_agent_orchestrator import orchestrator

async def test_routing():
    test_queries = [
        ('Solve x^2 - 4 = 0', 'GENERAL_KNOWLEDGE'),
        ('Compare these two documents', 'DOCUMENT_COMPARISON'),
        ('Extract data from this PDF', 'INFORMATION_EXTRACTOR'),
        ('Generate questions about this text', 'QUESTION_GENERATOR')
    ]
    
    await orchestrator.initialize()
    
    for query, expected_route in test_queries:
        try:
            response = await orchestrator.process_query(
                query=query,
                session_id='test_routing',
                context={'interface': 'test'}
            )
            actual_route = response['routing_decision']['agent_type']
            status = '✅' if actual_route == expected_route else '⚠️'
            print(f'{status} \"{query}\" → {actual_route} (expected: {expected_route})')
        except Exception as e:
            print(f'❌ Routing test failed for \"{query}\": {e}')

asyncio.run(test_routing())
"
```

#### 10. **Mathematical Problem Solving Test**
```bash
# Test knowledge agent with mathematical queries
python -c "
import asyncio
from src.agents.multi_agent_orchestrator import orchestrator

async def test_math():
    math_queries = [
        'What is 15 * 23?',
        'Solve the equation 2x + 5 = 13',
        'What is the derivative of x^2 + 3x?'
    ]
    
    await orchestrator.initialize()
    
    for query in math_queries:
        try:
            response = await orchestrator.process_query(
                query=query,
                session_id='test_math',
                context={'interface': 'test'}
            )
            if response['status'] == 'success':
                print(f'✅ Math Query: \"{query}\"')
                print(f'   Response: {response[\"result\"][\"response\"][:100]}...')
            else:
                print(f'❌ Math Query Failed: \"{query}\"')
        except Exception as e:
            print(f'❌ Math test failed: {e}')

asyncio.run(test_math())
"
```

#### 11. **Document Processing Pipeline Test**
```bash
# Test document processing capabilities
python -c "
import asyncio
from src.agents.multi_agent_orchestrator import orchestrator

async def test_documents():
    doc_queries = [
        'Compare the main themes in these documents',
        'Extract key information from this contract',
        'Generate study questions from this manual'
    ]
    
    await orchestrator.initialize()
    
    for query in doc_queries:
        try:
            response = await orchestrator.process_query(
                query=query,
                session_id='test_docs',
                context={'interface': 'test', 'has_documents': True}
            )
            routing = response['routing_decision']
            print(f'✅ Doc Query: \"{query}\"')
            print(f'   Routed to: {routing[\"agent_type\"]}')
            if routing.get('pipeline'):
                print(f'   Pipeline: {\" → \".join(routing[\"pipeline\"])}')
        except Exception as e:
            print(f'❌ Document test failed: {e}')

asyncio.run(test_documents())
"
```

### Performance Testing

#### 12. **Response Time Test**
```bash
# Test system response times
python -c "
import asyncio
import time
from src.agents.multi_agent_orchestrator import orchestrator

async def test_performance():
    await orchestrator.initialize()
    
    test_queries = [
        'What is 2 + 2?',
        'Explain quantum physics',
        'Compare document structures'
    ]
    
    for query in test_queries:
        start_time = time.time()
        try:
            response = await orchestrator.process_query(
                query=query,
                session_id='perf_test',
                context={'interface': 'test'}
            )
            end_time = time.time()
            duration = end_time - start_time
            status = '✅' if duration < 10.0 else '⚠️'
            print(f'{status} \"{query}\": {duration:.2f}s')
        except Exception as e:
            print(f'❌ Performance test failed: {e}')

asyncio.run(test_performance())
"
```

#### 13. **Memory and Resource Test**
```bash
# Test system resource usage
python -c "
import asyncio
import psutil
import os
from src.agents.multi_agent_orchestrator import orchestrator

async def test_resources():
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    await orchestrator.initialize()
    
    # Run multiple queries
    for i in range(5):
        await orchestrator.process_query(
            query=f'Test query {i+1}',
            session_id=f'resource_test_{i}',
            context={'interface': 'test'}
        )
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    print(f'Initial Memory: {initial_memory:.1f} MB')
    print(f'Final Memory: {final_memory:.1f} MB')
    print(f'Memory Increase: {memory_increase:.1f} MB')
    
    status = '✅' if memory_increase < 100 else '⚠️'
    print(f'{status} Memory usage acceptable')

asyncio.run(test_resources())
"
```

### Integration Testing

#### 14. **End-to-End Workflow Test**
```bash
# Test complete workflow from query to response
python -c "
import asyncio
from src.agents.multi_agent_orchestrator import orchestrator

async def test_e2e():
    print('🧪 Starting End-to-End Test...')
    
    # Initialize system
    await orchestrator.initialize()
    print('✅ System initialized')
    
    # Test session management
    session_id = 'e2e_test_session'
    
    # Test mathematical reasoning
    math_response = await orchestrator.process_query(
        query='If I have 10 apples and eat 3, how many do I have left?',
        session_id=session_id,
        context={'interface': 'test'}
    )
    
    if math_response['status'] == 'success':
        print('✅ Mathematical reasoning works')
    else:
        print('❌ Mathematical reasoning failed')
    
    # Test context retention
    followup_response = await orchestrator.process_query(
        query='Now if I give away 2 more, how many remain?',
        session_id=session_id,
        context={'interface': 'test'}
    )
    
    if followup_response['status'] == 'success':
        print('✅ Context retention works')
    else:
        print('❌ Context retention failed')
    
    # Test different agent routing
    doc_response = await orchestrator.process_query(
        query='Compare two documents side by side',
        session_id=session_id,
        context={'interface': 'test'}
    )
    
    if doc_response['routing_decision']['agent_type'] == 'DOCUMENT_COMPARISON':
        print('✅ Agent routing works correctly')
    else:
        print('⚠️ Agent routing may need adjustment')
    
    print('🎉 End-to-End test completed')

asyncio.run(test_e2e())
"
```

### Troubleshooting Tests

#### 15. **Error Handling Test**
```bash
# Test system error handling
python -c "
import asyncio
from src.agents.multi_agent_orchestrator import orchestrator

async def test_error_handling():
    await orchestrator.initialize()
    
    # Test with malformed queries
    error_queries = [
        '',  # Empty query
        'x' * 10000,  # Very long query
        '\\n\\r\\t',  # Special characters
    ]
    
    for i, query in enumerate(error_queries):
        try:
            response = await orchestrator.process_query(
                query=query,
                session_id=f'error_test_{i}',
                context={'interface': 'test'}
            )
            print(f'✅ Error Query {i+1}: Handled gracefully')
        except Exception as e:
            print(f'⚠️ Error Query {i+1}: {str(e)[:100]}...')

asyncio.run(test_error_handling())
"
```

#### 16. **Dependency Verification**
```bash
# Verify all required packages are properly installed
python -c "
required_packages = [
    'google.adk', 'fastapi', 'uvicorn', 'chainlit', 'litellm',
    'docling', 'docx2txt', 'pdfplumber', 'python_docx',
    'fuzzywuzzy', 'spacy', 'transformers', 'gradio'
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package.replace('-', '_').replace('.', '.'))
        print(f'✅ {package}')
    except ImportError:
        missing_packages.append(package)
        print(f'❌ {package}')

if missing_packages:
    print(f'\\n⚠️ Missing packages: {missing_packages}')
    print('Run: uv sync')
else:
    print('\\n🎉 All required packages available')
"
```

### Quick Test Suite

#### 17. **Run All Tests (Automated)**
```bash
# Save this as test_suite.py and run: python test_suite.py
cat > test_suite.py << 'EOF'
import asyncio
import sys
from src.core.config import config
from src.agents.multi_agent_orchestrator import orchestrator

async def quick_test_suite():
    print("🧪 Multi-Agent System Quick Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 6
    
    # Test 1: Configuration
    try:
        mcp_url = config.get_mcp_server_url()
        print(f"✅ Config Test: MCP URL = {mcp_url}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Config Test Failed: {e}")
    
    # Test 2: Orchestrator Initialization
    try:
        await orchestrator.initialize()
        print("✅ Orchestrator Initialization")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Orchestrator Initialization Failed: {e}")
    
    # Test 3: Health Check
    try:
        health = await orchestrator.health_check()
        print(f"✅ Health Check: {health['overall_status']}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
    
    # Test 4: Simple Query
    try:
        response = await orchestrator.process_query(
            query="What is 5 + 3?",
            session_id="quick_test",
            context={"interface": "test"}
        )
        if response["status"] == "success":
            print("✅ Simple Query Processing")
            tests_passed += 1
        else:
            print("❌ Simple Query Failed")
    except Exception as e:
        print(f"❌ Simple Query Failed: {e}")
    
    # Test 5: Agent Routing
    try:
        response = await orchestrator.process_query(
            query="Compare these documents",
            session_id="quick_test",
            context={"interface": "test"}
        )
        route = response["routing_decision"]["agent_type"]
        print(f"✅ Agent Routing: {route}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Agent Routing Failed: {e}")
    
    # Test 6: Multiple Agents
    try:
        agents = await orchestrator.get_available_agents()
        print(f"✅ Available Agents: {len(agents)} agents")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Available Agents Failed: {e}")
    
    print("=" * 50)
    print(f"Test Results: {tests_passed}/{tests_total} passed")
    
    if tests_passed == tests_total:
        print("🎉 All tests passed! System is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Check configuration and dependencies.")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test_suite())
    sys.exit(0 if success else 1)
EOF

python test_suite.py
```

### Expected Results

After running all tests, you should see:
- ✅ All imports successful
- ✅ MCP server connectivity (if server running)
- ✅ Multi-agent system initialization
- ✅ Proper agent routing decisions  
- ✅ Mathematical problem solving
- ✅ API endpoints responding
- ✅ Acceptable performance metrics
- ✅ Graceful error handling

### Troubleshooting Common Issues

**MCP Server Connection Failed:**
```bash
# Start MCP server on port 17324
# Check if server is running: curl http://127.0.0.1:17324/health
```

**Import Errors:**
```bash
# Reinstall dependencies
uv sync --reinstall
```

**Performance Issues:**
```bash
# Check system resources
htop  # or top on macOS
# Consider adjusting model settings in src/core/config.py
```

**Agent Routing Issues:**
```bash
# Check coordinator prompts in src/agents/coordinator_agent.py
# Verify routing rules in src/agents/specialist_agents.py
```

This comprehensive testing protocol ensures the multi-agent system is functioning correctly across all interfaces and capabilities.