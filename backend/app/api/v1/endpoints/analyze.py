from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from app.services.repository import repo_service
from app.services.analysis import analysis_engine
from app.services.generator import file_generator
from app.core.config import settings
from loguru import logger
import uuid
import httpx

from app.services.task_manager import task_manager

from app.services.ai_service import ai_service

router = APIRouter()

class AnalyzeRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    user_id: Optional[str] = None

async def fetch_github_token(user_id: str) -> Optional[str]:
    """Fetches the GitHub OAuth token for a user from Clerk."""
    if not settings.CLERK_SECRET_KEY:
        logger.warning("CLERK_SECRET_KEY is not set. Cannot fetch token.")
        return None
        
    url = f"https://api.clerk.dev/v1/users/{user_id}/oauth_access_tokens/oauth_github"
    headers = {
        "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            tokens = response.json()
            if tokens and len(tokens) > 0:
                return tokens[0].get("token")
        except Exception as e:
            logger.error(f"Failed to fetch GitHub token from Clerk for {user_id}: {e}")
            
    return None

async def analyze_repo_task(task_id: str, repo_url: str, branch: str, user_id: Optional[str] = None):
    """
    Background task to clone, analyze, and generate files for a repo.
    """
    logger.info(f"Starting analysis task {task_id} for {repo_url}")
    
    github_token = None
    if user_id:
        task_manager.update_task(task_id, "authenticating", message="Fetching GitHub token securely...")
        github_token = await fetch_github_token(user_id)
        if not github_token:
            logger.warning(f"Task {task_id}: Could not fetch GitHub token for user {user_id}. Proceeding without auth.")
    
    task_manager.update_task(task_id, "cloning")
    
    # 1. Clone
    workspace = repo_service.clone_repository(repo_url, branch, token=github_token)
    if not workspace:
        logger.error(f"Task {task_id}: Cloning failed.")
        task_manager.update_task(task_id, "failed", message="Cloning failed.")
        return

    # 2. Analyze
    task_manager.update_task(task_id, "analyzing")
    findings = analysis_engine.analyze_directory(workspace)
    
    # AI Refinement if confidence is low
    if findings.get("confidence", 0) < 0.7:
        logger.info(f"Task {task_id}: Low confidence ({findings.get('confidence')}). Requesting AI refinement...")
        findings = await ai_service.refine_analysis(findings)
    
    # 3. Generate Deployment Files
    task_manager.update_task(task_id, "generating")
    file_generator.generate_deployment_files(workspace, findings)

    # 4. Push changes if token provided
    if github_token:
        task_manager.update_task(task_id, "pushing")
        logger.info(f"Task {task_id}: Attempting to push changes...")
        repo_service.push_changes(workspace)

    # 5. Cleanup
    repo_service.cleanup_workspace(workspace)
    
    task_manager.update_task(task_id, "completed")
    logger.info(f"Task {task_id}: Analysis and generation complete.")

@router.post("/analyze")
async def start_analysis(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    logger.info(f"Received analysis request for {request.repo_url}. Assigned ID: {task_id}")
    
    # Initialize task status
    task_manager.update_task(task_id, "initialized")
    
    background_tasks.add_task(analyze_repo_task, task_id, request.repo_url, request.branch, request.user_id)
    
    return {
        "status": "queued",
        "task_id": task_id,
        "message": f"Analysis for {request.repo_url} has been started in the background."
    }

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    status = task_manager.get_task(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status
