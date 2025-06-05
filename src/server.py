from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chat.route import router as chat_router

# Initialize FastAPI app
app = FastAPI(
    title="Agent API",
    description="API for interacting with the agent",
    version="0.1.0"
)

app.include_router(chat_router, prefix="/chat", tags=["chat"])

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000)