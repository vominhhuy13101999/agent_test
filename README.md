# Demo with Google Agent Development Kit (ADK)

## Setup environment

Use `UV` as Package Manager 

To install `UV`, following the instruction on official website [link](https://docs.astral.sh/uv/getting-started/installation/)

At project folder, run `uv sync` to install all necessary packages for project

**Setup Agent API Key for project**

Steps: 
1. Get API Key from [Google AI Studio](https://aistudio.google.com)
2. Create file `.env` in folder `multi_tool_agent` with following content
    ```.env
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    GOOGLE_API_KEY=<API_KEY>
    ```
3. Replace `<API_KEY>` with yours in file `.env`

## Run Project 

At project folder, run command `uv run main.py` to run an Agent program

### Use self-hosted model

Use model `qwen 3 - 1.7B`, which is suitable for local testing 

- Test with `Ollama`
```
ollama run qwen3:1.7B
```

