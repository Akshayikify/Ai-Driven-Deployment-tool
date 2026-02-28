from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger
from app.services.ai_service import ai_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    logger.info(f"Received chat message: {request.message[:50]}...")
    try:
        response_text = await ai_service.chat_with_agent(request.message)
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message.")
