from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic_ai import Agent
from app.mcp.manager import mcp_manager
import json

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    agent_id: str
    system_prompt: str | None = None

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    # Initialize MCP Manager and get tools for this agent
    tools = await mcp_manager.get_tools_for_agent(request.agent_id)
    
    # Create Pydantic AI Agent
    agent = Agent(
        "openai:gpt-4o",  # Default model, can be dynamic
        system_prompt=request.system_prompt or "You are a helpful assistant.",
        tools=tools
    )

    async def event_generator():
        async with agent.run_stream(request.message) as result:
            async for message in result.stream_text():
                # Following SSE format
                yield f"data: {json.dumps({'content': message})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
