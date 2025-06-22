from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chat.route import router as chat_router
from tool.route import router as tool_router

# Initialize FastAPI app
app = FastAPI(
    title="Agent API",
    description="API for interacting with the agent",
    version="0.1.0"
)

app.include_router(chat_router, prefix="/agent", tags=["agent"])
app.include_router(tool_router, prefix="/tools", tags=["tools"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Agent API is operational"}


if __name__ == "__main__":
    import uvicorn
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv("src/core/.env")
    
    uvicorn.run("src.server:app", host="0.0.0.0", port=8756, reload=True)