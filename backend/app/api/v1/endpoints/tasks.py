from fastapi import APIRouter, BackgroundTasks
from app.background.tasks import dummy_background_task

router = APIRouter()

@router.post("/test-task")
async def trigger_background_task(background_tasks: BackgroundTasks, task_name: str = "Test Task"):
    background_tasks.add_task(dummy_background_task, task_name)
    return {"message": f"Task '{task_name}' has been queued in the background."}
