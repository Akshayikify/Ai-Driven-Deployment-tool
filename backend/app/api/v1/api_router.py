from fastapi import APIRouter
from app.api.v1.endpoints import tasks

api_router = APIRouter()

api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

@api_router.get("/health")
async def health_check():
    return {"status": "API v1 is healthy"}
