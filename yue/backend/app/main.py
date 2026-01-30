import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import chat, agents, mcp
from app.mcp.manager import mcp_manager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize MCP Manager
    await mcp_manager.initialize()
    yield
    # Cleanup MCP Manager
    await mcp_manager.cleanup()

app = FastAPI(title="Yue Agent Platform API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["mcp"])

@app.get("/")
async def root():
    return {"message": "Welcome to Yue Agent Platform API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
