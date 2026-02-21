from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from app.services.log_streamer import log_streamer
import asyncio

router = APIRouter()

@router.get("/stream")
async def stream_logs():
    """
    SSE endpoint to stream backend logs to the frontend.
    """
    async def log_generator():
        async for log in log_streamer.subscribe():
            # If the client disconnects, the subscribe generator will be closed
            yield {
                "data": log
            }

    return EventSourceResponse(log_generator())
