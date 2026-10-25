from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from app.services.repository import repo_service
from app.services.analysis import analysis_engine
from app.services.generator import file_generator
from app.services.security_scanner import security_scanner
from app.core.config import settings
from loguru import logger
import uuid
import asyncio
import httpx

from app.services.task_manager import task_manager

from app.services.ai_service import ai_service

router = APIRouter()

class AnalyzeRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    user_id: Optional[str] = None

_USER_GITHUB_TOKEN_CACHE: Dict[str, str] = {}

async def fetch_github_token(user_id: str) -> Optional[str]:
    """Fetches the GitHub OAuth token for a user from Clerk with caching and retries."""
    if not settings.CLERK_SECRET_KEY:
        logger.warning("CLERK_SECRET_KEY is not set. Cannot fetch token.")
        return _USER_GITHUB_TOKEN_CACHE.get(user_id)
        
    url = f"https://api.clerk.com/v1/users/{user_id}/oauth_access_tokens/oauth_github"
    headers = {
        "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                tokens = response.json()
                if tokens and len(tokens) > 0:
                    token = tokens[0].get("token")
                    if token:
                        _USER_GITHUB_TOKEN_CACHE[user_id] = token
                        return token
        except Exception as e:
            if attempt < 2:
                await asyncio.sleep(0.5 * (attempt + 1))
            else:
                logger.error(f"Failed to fetch GitHub token from Clerk for {user_id} (attempt {attempt+1}/3): {e}")

    # Fallback to cached token if previously fetched for this session
    cached = _USER_GITHUB_TOKEN_CACHE.get(user_id)
    if cached:
        logger.info(f"Using cached GitHub token for {user_id}")
        return cached
            
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
            # FIX-9: Diagnose the clone failure reason so we can reclassify
            # invalid/private-repo errors as 'user_error' rather than 'failed'.
            # This prevents user input mistakes from dragging down the success rate.
            clone_error_msg = "Cloning failed."
            url_lower = repo_url.lower()
            is_likely_user_error = False

            # Check for obviously invalid URLs (no github.com domain)
            if "github.com" not in url_lower and "gitlab.com" not in url_lower and "bitbucket.org" not in url_lower:
                clone_error_msg = (
                    f"Cloning failed: '{repo_url}' does not appear to be a valid Git host URL. "
                    "Please check the repository URL and try again."
                )
                is_likely_user_error = True
            elif not github_token:
                # No token + clone failed → likely private repo
                clone_error_msg = (
                    "Cloning failed: the repository may be private or the URL is incorrect. "
                    "Connect your GitHub account to deploy private repositories."
                )
                is_likely_user_error = True

            if is_likely_user_error:
                # Mark as user_error (stored separately from failed so it doesn't
                # lower the deployment success rate in analytics).
                task_manager.update_task(
                    task_id, "failed",
                    message=clone_error_msg,
                    failure_category="user_error"
                )
            else:
                task_manager.update_task(task_id, "failed", message=clone_error_msg)
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

        # ── Step 2.5: Security Scan ──────────────────────────────────────────
        task_manager.update_task(task_id, "security_scanning")
        security_report = security_scanner.scan(workspace, findings.get("file_index", {}))

        # Attach the report to findings so it's included in any downstream data.
        findings["security_report"] = security_report.model_dump()
        # FIX-4: Only block the pipeline for CRITICAL security findings.
        # The SecurityReport schema already sets `blocked=True` only when CRITICAL
        # issues are present. HIGH/MEDIUM/LOW are advisory — attach the report and
        # let the deployment continue so the user isn't blocked unnecessarily.
        if not security_report.is_clean and security_report.blocked:
            # CRITICAL findings only — generate files first so the user sees the full picture,
            # then pause and ask for push confirmation.
            logger.warning(
                f"Task {task_id}: CRITICAL security findings — pausing pipeline. "
                f"{security_report.summary}"
            )

            # ── Step 3 (early): generate files regardless so they're ready
            task_manager.update_task(task_id, "generating")
            t0_gen = time.time()
            await file_generator.generate_deployment_files(workspace, findings)
            t_generate = time.time() - t0_gen

            # Store workspace path and github_token on the task so the
            # confirm-push endpoint can resume the pipeline later.
            task_manager.tasks[task_id]["_workspace"] = workspace
            task_manager.tasks[task_id]["_github_token"] = github_token
            task_manager.tasks[task_id]["_repo_url"] = repo_url
            task_manager.tasks[task_id]["_findings"] = {
                "language": findings.get("language"),
                "estimated_duration": findings.get("estimated_duration"),
            }

            # Pause — set status to awaiting_push_confirmation
            task_manager.update_task(
                task_id,
                "awaiting_push_confirmation",
                security_report=security_report.model_dump(),
            )
            # Background task ends here; the confirm-push endpoint resumes it.
            return

        elif not security_report.is_clean and not security_report.blocked:
            # HIGH/MEDIUM/LOW findings — attach the report as a warning but continue.
            # The frontend will display a warning banner without blocking the user.
            logger.warning(
                f"Task {task_id}: Non-critical security findings (advisory). "
                f"{security_report.summary} — pipeline continues."
            )
            task_manager.tasks[task_id]["security_report"] = security_report.model_dump()
            task_manager.tasks[task_id]["security_warning"] = True
            # Pipeline continues below — non-critical findings are advisory only.


        # ── Step 3: Generate Deployment Files (clean scan path) ─────────────
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
            update_kwargs = {
                "status": "ready_to_deploy",
                "message": "AI analysis complete and Docker/CI-CD files generated. Connect GitHub account to deploy to Minikube."
            }
            if 'findings' in locals():
                if "language" in findings: update_kwargs["language"] = findings["language"]
                if "estimated_duration" in findings: update_kwargs["estimated_duration"] = findings["estimated_duration"]
                if "security_report" in findings: update_kwargs["security_report"] = findings["security_report"]
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


async def _resume_push(task_id: str):
    """
    Resumes the deployment pipeline after the user confirms the security push.
    Called by the /confirm-push endpoint as a background task.
    """
    task = task_manager.get_task(task_id)
    if not task:
        logger.error(f"confirm-push: task {task_id} not found.")
        return

    import time
    workspace    = task.get("_workspace")
    github_token = task.get("_github_token")
    repo_url     = task.get("_repo_url", task.get("repo_url", ""))
    meta         = task.get("_findings", {})

    if not workspace:
        logger.error(f"confirm-push: no workspace stored for task {task_id}.")
        task_manager.update_task(task_id, "failed", message="Workspace not available for push.")
        return

    try:
        t_push = 0
        if github_token:
            task_manager.update_task(task_id, "pushing")
            logger.info(f"Task {task_id}: User confirmed push — pushing changes to GitHub...")
            t0_push = time.time()
            repo_service.push_changes(workspace)
            t_push = time.time() - t0_push

        repo_service.cleanup_workspace(workspace)

        if github_token:
            import asyncio
            from app.services.github_actions import github_actions_service
            asyncio.create_task(
                github_actions_service.monitor_workflow(repo_url, github_token, task_id=task_id)
            )
        else:
            update_kwargs = {
                "status": "ready_to_deploy",
                "message": "AI analysis complete and Docker/CI-CD files generated. Connect GitHub account to deploy to Minikube."
            }
            if meta.get("language"):           update_kwargs["language"] = meta["language"]
            if meta.get("estimated_duration"): update_kwargs["estimated_duration"] = meta["estimated_duration"]
            task_manager.update_task(task_id, **update_kwargs)

    except Exception as e:
        import traceback
        logger.error(f"confirm-push task {task_id} failed: {e}\n{traceback.format_exc()}")
        task_manager.update_task(task_id, "failed", message=str(e))
        try:
            if workspace:
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


@router.post("/confirm-push/{task_id}")
async def confirm_push(task_id: str, background_tasks: BackgroundTasks):
    """
    User has reviewed the security findings and approved the GitHub push.
    Resumes the paused pipeline from the awaiting_push_confirmation state.
    """
    task = task_manager.get_task(task_id)
    if not task:
        # Fallback to MongoDB if server was restarted
        from app.db.mongodb import db
        mongo_task = await db.get_deployment_by_id(task_id)
        if mongo_task and mongo_task.get("status") == "awaiting_push_confirmation":
            task_manager.tasks[task_id] = mongo_task
            task = mongo_task

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if task.get("status") != "awaiting_push_confirmation":
        raise HTTPException(
            status_code=400,
            detail=f"Task is not awaiting confirmation (current status: {task.get('status')})."
        )

    # Auto-recover workspace and token if missing from restart
    if not task.get("_workspace"):
        repo_url = task.get("_repo_url", task.get("repo_url", ""))
        if repo_url:
            repo_name = repo_url.rstrip("/").replace(".git", "").split("/")[-1]
            candidate = os.path.join(repo_service.base_temp_dir, repo_name)
            if os.path.exists(candidate):
                task["_workspace"] = candidate
    if not task.get("_github_token") and task.get("user_id"):
        task["_github_token"] = await fetch_github_token(task["user_id"])

    logger.info(f"Task {task_id}: User confirmed push despite security findings. Resuming pipeline.")
    background_tasks.add_task(_resume_push, task_id)
    return {"status": "resuming", "message": "Push confirmed. Deployment pipeline is resuming."}


@router.post("/cancel-push/{task_id}")
async def cancel_push(task_id: str):
    """
    User has reviewed the security findings and declined the GitHub push.
    Cleans up the workspace and marks the task as cancelled (not failed).
    """
    task = task_manager.get_task(task_id)
    if not task:
        from app.db.mongodb import db
        mongo_task = await db.get_deployment_by_id(task_id)
        if mongo_task and mongo_task.get("status") == "awaiting_push_confirmation":
            task_manager.tasks[task_id] = mongo_task
            task = mongo_task

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if task.get("status") != "awaiting_push_confirmation":
        raise HTTPException(
            status_code=400,
            detail=f"Task is not awaiting confirmation (current status: {task.get('status')})."
        )

    workspace = task.get("_workspace")
    if not workspace:
        repo_url = task.get("_repo_url", task.get("repo_url", ""))
        if repo_url:
            repo_name = repo_url.rstrip("/").replace(".git", "").split("/")[-1]
            candidate = os.path.join(repo_service.base_temp_dir, repo_name)
            if os.path.exists(candidate):
                workspace = candidate

    if workspace:
        try:
            repo_service.cleanup_workspace(workspace)
        except Exception as e:
            logger.warning(f"Task {task_id}: cleanup failed during cancel-push: {e}")

    # Update to a neutral 'cancelled' state — not stored in MongoDB
    task["status"] = "security_warning"
    task["current_message"] = (
        "❌ Push cancelled by user. Security findings were not resolved. "
        "Fix the issues and re-deploy to proceed."
    )
    task["_workspace"] = None
    logger.info(f"Task {task_id}: User cancelled push. Workspace cleaned up.")
    return {"status": "cancelled", "message": "Push cancelled. Workspace cleaned up."}


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    # Primary: check in-memory store (fast path, always up-to-date while server is running)
    task = task_manager.get_task(task_id)
    if task:
        return task

    # Fallback: task may have been written to MongoDB by a previous server process
    # (e.g. uvicorn hot-reload during a long-running GitHub Actions monitor).
    from app.db.mongodb import db
    mongo_task = await db.get_deployment_by_id(task_id)
    if mongo_task:
        logger.info(
            f"Status lookup: task {task_id} not in memory — serving from MongoDB fallback "
            f"(status={mongo_task.get('status')})."
        )
        return mongo_task

    raise HTTPException(status_code=404, detail="Task not found")

@router.get("/tasks")
async def list_recent_tasks(user_id: Optional[str] = None):
    """
    Returns a deduplicated list of all recent deployment tasks for a user,
    merging persistent MongoDB records with active in-memory tasks.
    """
    from app.db.mongodb import db, normalize_repo_url

    # 1. Fetch persistent deployments from MongoDB
    mongo_deployments = await db.list_deployments(user_id=user_id, limit=50)

    # 2. Fetch in-memory tasks (live active runs)
    in_memory = task_manager.list_tasks(user_id=user_id)

    # 3. Merge: key by normalized repository URL so re-tests always update the same row
    merged_map = {}
    for dep in mongo_deployments:
        key = normalize_repo_url(dep.get("repo_url")).lower() or dep.get("id")
        merged_map[key] = dep

    for task in in_memory:
        key = normalize_repo_url(task.get("repo_url")).lower() or task.get("id")
        if key in merged_map:
            # Active in-memory state overrides / enriches stored record
            merged_map[key] = {**merged_map[key], **task}
        else:
            merged_map[key] = task

    result = list(merged_map.values())
    result.sort(key=lambda x: str(x.get("updated_at") or x.get("created_at") or ""), reverse=True)
    return result

@router.get("/stats")
async def get_deployment_analytics(user_id: Optional[str] = None):
    """Retrieves deployment statistics from MongoDB for the analytics dashboard, isolated by user."""
    from app.db.mongodb import db
    return await db.get_deployment_stats(user_id=user_id)

class AutoFixRequest(BaseModel):
    repo_url: str
    user_id: str
    actions: list
    task_id: Optional[str] = None   # the original deployment task to update after auto-fix

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

    # Re-trigger monitoring for the new pipeline run, threading the original task_id
    # so the task is updated to completed/failed when the auto-fix pipeline finishes.
    import asyncio
    asyncio.create_task(
        github_actions_service.monitor_workflow(
            request.repo_url,
            github_token,
            task_id=request.task_id or None,   # None is safe — monitor still runs, just no task update
        )
    )

    return {"status": "success", "message": "Auto-fix applied successfully. GitHub Actions will trigger a rebuild shortly."}
