# AI Agent with Google ADK and MCP Integration

## Project Overview

This project implements a sophisticated AI agent system using Google's Agent Development Kit (ADK) with Model Control Protocol (MCP) integration. It provides both a command-line interface and a RESTful API for interacting with an AI agent that can access dynamic tools and perform document-based question answering.

## Code Architecture

### Core Components

#### 1. Main Entry Point (`main.py`)
- **`main()`** (`main.py:16`): Interactive CLI for direct agent interaction
- Supports commands: `exit`, `check`, `update_toolset`, and direct queries
- Manages dynamic tool updates from MCP server
- Uses `InMemorySessionService` for conversation persistence


#### 3. Advanced Agent System (`src/agent/agent.py`)
- **`create_agent()`** (`agent.py:54`): Enhanced agent with document Q&A capabilities  
- **`simple_before_model_modifier()`** (`agent.py:12`): Request preprocessing callback
- **`get_agent()`** (`agent.py:48`): Singleton agent instance manager
- Connects to MCP server at `http://127.0.0.1:17324/mcp-server/sse`
- Supports RAG (Retrieval-Augmented Generation) with semantic/keyword search

### API Layer

#### 4. FastAPI Server (`src/server.py`)
- **Main Application** (`server.py:7`): FastAPI app with CORS support
- Routes: `/agent/*` for chat functionality
- Health check endpoint at `/`
- Runs on `0.0.0.0:8756`

#### 5. Chat System (`src/chat/`)

**Route Handler** (`src/chat/route.py`):
- **`send_message()`** (`route.py:37`): Process chat messages via API
- **`startup_event()`** (`route.py:31`): Initialize agent and session service
- Supports RAG toggle for document search capabilities
- Manages user sessions and conversation state

**Data Models** (`src/chat/data_models.py`):
- **`MessageRequest`**: Input schema with user_id, session_id, message, use_rag
- **`MessageResponse`**: Output schema with agent response

**Controller** (`src/chat/controller.py`):
- **`ChatController`**: Advanced chat management class
- **`handle_message()`** (`controller.py:40`): Process messages with session management
- **`get_session()`**, **`end_session()`**: Session lifecycle management

#### 6. Tool Management (`src/tool/`)

**Tool Routes** (`src/tool/route.py`):
- **`get_tools()`** (`route.py:10`): List available agent tools
- **`update_toolset()`** (`route.py:20`): Refresh tools from MCP server

**Tool Models** (`src/tool/data_models.py`):
- **`ToolResponse`**: Schema for tool listings
- **`StatusResponse`**: Schema for operation status

### Configuration

#### 7. Project Config (`pyproject.toml`)
**Dependencies**:
- `google-adk>=0.4.0`: Google Agent Development Kit
- `chainlit>=2.5.5`: Conversational AI framework
- `fastapi>=0.115.12`: Web API framework
- `litellm>=1.70.0`: Multi-LLM integration
- `uvicorn>=0.34.2`: ASGI server

#### 8. Core Config (`src/core/config.py`)
- Configuration management class (minimal implementation)

## Key Features

### Agent Capabilities
- **Document Q&A**: RAG-enabled search through knowledge bases
- **Mathematical Problem Solving**: Specialized for equations and calculations
- **Dynamic Tool Loading**: Real-time tool updates from MCP servers
- **Session Management**: Persistent conversation contexts

### API Endpoints
- `POST /agent/chat`: Send messages to agent
- `GET /agent/tools`: List available tools  
- `POST /agent/update-toolset`: Refresh agent tools
- `GET /agent/sessions/{id}`: Retrieve session details
- `DELETE /agent/sessions/{id}`: End sessions

### Dual Interface
- **CLI Mode**: Direct terminal interaction (`main.py`)
- **API Mode**: RESTful web service (`src/server.py`)

## Setup Environment

Use `UV` as Package Manager 

To install `UV`, follow the instruction on official website [link](https://docs.astral.sh/uv/getting-started/installation/)

At project folder, run `uv sync` to install all necessary packages for project

**Setup Agent API Key for project**

Steps: 
1. Get API Key from [Google AI Studio](https://aistudio.google.com)
2. Edit the file `src/core/.env` with following content:
    ```.env
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    GOOGLE_API_KEY=<API_KEY>
    MCP_SERVER_URL=http://127.0.0.1:17324/mcp-server/sse
    AGENT_MODEL=gemini-2.5-flash-preview-05-20
    ```
3. Replace `<API_KEY>` with yours in file `.env`

## Run Project 

### CLI Mode
At project folder, run command `uv run main.py` to run an Agent program

### API Mode  
```bash
cd src && python server.py
```
or
```bash
uvicorn src.server:app --host 0.0.0.0 --port 8756
```

### Available Commands (CLI)
- **Direct Input**: Enter questions for the agent to answer
- **`check`**: Display currently available tools
- **`update_toolset`**: Refresh tools from MCP server
- **`exit`**: Quit the application

### Use Self-hosted Model

Use model `qwen 3 - 1.7B`, which is suitable for local testing 

- Test with `Ollama`
```bash
ollama run qwen3:1.7B
```

## Architecture Flow

1. **Initialization**: Load environment, create agent with MCP tools
2. **Tool Loading**: Connect to MCP server, retrieve available tools
3. **Session Management**: Create/manage conversation contexts
4. **Request Processing**: Handle user input through CLI or API
5. **RAG Integration**: Optional document search for enhanced responses
6. **Dynamic Updates**: Real-time tool refresh without restart

