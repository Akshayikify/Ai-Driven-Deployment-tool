from fastapi import APIRouter
from app.api.v1.endpoints import tasks, analyze, logs, chat

api_router = APIRouter()

api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

@api_router.get("/health")
async def health_check():
    return {"status": "API v1 is healthy"}
