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
    
    import time
    
    try:
        # 1. Clone
        task_manager.update_task(task_id, "cloning")
        t0 = time.time()
        workspace = repo_service.clone_repository(repo_url, branch, token=github_token)
        t_clone = time.time() - t0
        
        if not workspace:
            logger.error(f"Task {task_id}: Cloning failed.")
            task_manager.update_task(task_id, "failed", message="Cloning failed.")
            return

        # 2. Analyze
        task_manager.update_task(task_id, "analyzing")
        t0_analyze = time.time()
        findings = analysis_engine.analyze_directory(workspace)
        t_analyze = time.time() - t0_analyze
        
        # Store estimated duration and language in task manager
        update_kwargs = {"status": "analyzing"}
        if "estimated_duration" in findings:
            update_kwargs["estimated_duration"] = findings["estimated_duration"]
        if "language" in findings:
            update_kwargs["language"] = findings["language"]
            
        task_manager.update_task(task_id, **update_kwargs)

        # AI Refinement if confidence is low
        if findings.get("confidence", 0) < 0.7:
            logger.info(f"Task {task_id}: Low confidence ({findings.get('confidence')}). Requesting AI refinement...")
            findings = await ai_service.refine_analysis(findings)
            # Update task again after refinement with potentially new language/framework
            refine_kwargs = {"status": "analyzing"}
            if "language" in findings: refine_kwargs["language"] = findings["language"]
            if "estimated_duration" in findings: refine_kwargs["estimated_duration"] = findings["estimated_duration"]
            task_manager.update_task(task_id, **refine_kwargs)
            
        # 3. Generate Deployment Files
        task_manager.update_task(task_id, "generating")
        t0_gen = time.time()
        await file_generator.generate_deployment_files(workspace, findings)
        t_generate = time.time() - t0_gen

        # 4. Push changes if token provided
        t_push = 0
        if github_token:
            task_manager.update_task(task_id, "pushing")
            logger.info(f"Task {task_id}: Attempting to push changes...")
            t0_push = time.time()
            repo_service.push_changes(workspace)
            t_push = time.time() - t0_push

        # 5. Cleanup
        repo_service.cleanup_workspace(workspace)
        
        # Log Timing Summary
        summary_msg = (
            f"⏱️ Deployment Preparation Time Summary:\n"
            f"  - Repository Cloning: {t_clone:.2f}s\n"
            f"  - Deep AI Analysis: {t_analyze:.2f}s\n"
            f"  - Asset Generation: {t_generate:.2f}s\n"
        )
        if github_token:
             summary_msg += f"  - Remote GitHub Push: {t_push:.2f}s\n"
        
        summary_msg += f"  => Total Time Saved: {(t_clone + t_analyze + t_generate + t_push):.2f}s vs Manual Deployment"
        logger.info(summary_msg)
        
        # 6. Trigger Live GitHub Actions Monitoring
        if github_token:
            # We spawn this as a background asyncio task so it doesn't block the HTTP response or Task Manager
            import asyncio
            from app.services.github_actions import github_actions_service
            asyncio.create_task(github_actions_service.monitor_workflow(repo_url, github_token, task_id=task_id))
        else:    
            update_kwargs = {"status": "completed"}
            if 'findings' in locals():
                if "language" in findings: update_kwargs["language"] = findings["language"]
                if "estimated_duration" in findings: update_kwargs["estimated_duration"] = findings["estimated_duration"]
            task_manager.update_task(task_id, **update_kwargs)
    except Exception as e:
        import traceback
        logger.error(f"Task {task_id} failed with exception: {e}")
        logger.error(traceback.format_exc())
        fail_kwargs = {"status": "failed", "message": str(e)}
        try:
            if 'findings' in locals():
                if "language" in findings: fail_kwargs["language"] = findings["language"]
                if "estimated_duration" in findings: fail_kwargs["estimated_duration"] = findings["estimated_duration"]
        except: pass
        task_manager.update_task(task_id, **fail_kwargs)
        # Ensure cleanup on failure
        try:
            if 'workspace' in locals() and workspace:
                repo_service.cleanup_workspace(workspace)
        except:
            pass

@router.post("/analyze")
async def start_analysis(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    logger.info(f"Received analysis request for {request.repo_url}. Assigned ID: {task_id}")
    
    # Initialize task status with user_id for isolation
    task_manager.update_task(task_id, "initialized", repo_url=request.repo_url, user_id=request.user_id)
    
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

@router.get("/tasks")
async def list_recent_tasks(user_id: Optional[str] = None):
    """Returns a list of all recent deployment tasks for a specific user."""
    return task_manager.list_tasks(user_id=user_id)

@router.get("/stats")
async def get_deployment_analytics(user_id: Optional[str] = None):
    """Retrieves deployment statistics from MongoDB for the analytics dashboard, isolated by user."""
    from app.db.mongodb import db
    return await db.get_deployment_stats(user_id=user_id)

class AutoFixRequest(BaseModel):
    repo_url: str
    user_id: str
    actions: list

@router.post("/auto-fix")
async def trigger_auto_fix(request: AutoFixRequest):
    """Triggers the GitHub Auto-Fix mechanism using the user's Clerk Token."""
    github_token = await fetch_github_token(request.user_id)
    if not github_token:
        raise HTTPException(status_code=401, detail="User GitHub token could not be retrieved.")

    clean_url = request.repo_url.replace(".git", "")
    parts = clean_url.split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid repository URL.")
        
    owner = parts[-2]
    repo = parts[-1]

    from app.services.github_actions import github_actions_service
    success = await github_actions_service.apply_auto_fix(owner, repo, github_token, request.actions)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to apply auto-fix to repository.")
        
    # Re-trigger monitoring for the new pipeline run triggered by the fix
    import asyncio
    asyncio.create_task(github_actions_service.monitor_workflow(request.repo_url, github_token))

    return {"status": "success", "message": "Auto-fix applied successfully. GitHub Actions will trigger a rebuild shortly."}
