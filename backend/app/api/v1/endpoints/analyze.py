from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from app.services.repository import repo_service
from app.services.analysis import analysis_engine
from app.services.generator import file_generator
from loguru import logger
import uuid

router = APIRouter()

class AnalyzeRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    github_token: Optional[str] = None

async def analyze_repo_task(task_id: str, repo_url: str, branch: str, github_token: Optional[str] = None):
    """
    Background task to clone, analyze, and generate files for a repo.
    """
    logger.info(f"Starting analysis task {task_id} for {repo_url}")
    
    # 1. Clone
    workspace = repo_service.clone_repository(repo_url, branch, token=github_token)
    if not workspace:
        logger.error(f"Task {task_id}: Cloning failed.")
        return

    # 2. Analyze
    findings = analysis_engine.analyze_directory(workspace)
    
    # 3. Generate Dockerfile
    file_generator.generate_dockerfile(workspace, findings)

    # 4. Push changes if token provided
    if github_token:
        logger.info(f"Task {task_id}: Attempting to push changes...")
        repo_service.push_changes(workspace)

    # 5. Cleanup
    repo_service.cleanup_workspace(workspace)
    
    logger.info(f"Task {task_id}: Analysis and generation complete.")

@router.post("/analyze")
async def start_analysis(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    logger.info(f"Received analysis request for {request.repo_url}. Assigned ID: {task_id}")
    
    background_tasks.add_task(analyze_repo_task, task_id, request.repo_url, request.branch, request.github_token)
    
    return {
        "status": "queued",
        "task_id": task_id,
        "message": f"Analysis for {request.repo_url} has been started in the background."
    }
