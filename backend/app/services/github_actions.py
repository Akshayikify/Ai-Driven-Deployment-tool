import asyncio
import httpx
from loguru import logger
from typing import Optional

class GitHubActionsService:
    def __init__(self):
        self.api_base = "https://api.github.com"

    async def _get_latest_workflow_run(self, owner: str, repo: str, token: str) -> Optional[dict]:
        """Fetches the latest workflow run for a repository."""
        url = f"{self.api_base}/repos/{owner}/{repo}/actions/runs"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                runs = data.get("workflow_runs", [])
                if runs:
                    return runs[0]  # Get the most recent run
            except Exception as e:
                logger.error(f"Failed to fetch workflow runs for {owner}/{repo}: {e}")
        return None

    async def _get_job_steps(self, jobs_url: str, token: str) -> list:
        """Fetches all jobs and their steps for a specific workflow run."""
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(jobs_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get("jobs", [])
            except Exception as e:
                logger.error(f"Failed to fetch jobs at {jobs_url}: {e}")
        return []

    async def _get_job_logs(self, owner: str, repo: str, job_id: int, token: str) -> Optional[str]:
        """Downloads the raw logs for a specific job."""
        url = f"{self.api_base}/repos/{owner}/{repo}/actions/jobs/{job_id}/logs"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # GitHub redirects the log download, so we need follow_redirects=True
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"Failed to download logs for job {job_id}: {e}")
        return None

    async def apply_auto_fix(self, owner: str, repo: str, token: str, actions: list) -> bool:
        """Applies an auto-fix payload to the repository using the GitHub API."""
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        
        async with httpx.AsyncClient() as client:
            for action_item in actions:
                path = action_item.get("path")
                content = action_item.get("content")
                
                if not path or not content:
                    continue
                    
                import base64
                encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
                
                # Check if file exists to get its SHA (required for updating files)
                file_url = f"{self.api_base}/repos/{owner}/{repo}/contents/{path}"
                file_sha = None
                
                try:
                    resp = await client.get(file_url, headers=headers)
                    if resp.status_code == 200:
                        file_sha = resp.json().get("sha")
                except Exception:
                    pass # File might not exist, which is fine for create
                
                payload = {
                    "message": f"Auto-Fix applied by AI Agent: {path}",
                    "content": encoded_content,
                }
                
                if file_sha:
                    payload["sha"] = file_sha
                    
                try:
                    put_resp = await client.put(file_url, headers=headers, json=payload)
                    put_resp.raise_for_status()
                    logger.info(f"[AI Agent] Successfully pushed fix for {path}")
                except Exception as e:
                    logger.error(f"[AI Agent] Failed to push fix for {path}: {e}")
                    return False
        return True

    async def monitor_workflow(self, repo_url: str, token: str, task_id: Optional[str] = None):
        """
        Monitors a newly triggered GitHub Actions workflow and logs the progress natively.
        Also updates the TaskManager if task_id is provideed.
        """
        from app.services.task_manager import task_manager
        
        # 1. Parse Owner and Repo from URL
        clean_url = repo_url.replace(".git", "")
        parts = clean_url.split("/")
        if len(parts) < 2:
            logger.error(f"Could not parse repository owner and name from URL: {repo_url}")
            if task_id:
                task_manager.update_task(task_id, "failed", message="Invalid repository URL")
            return
            
        owner = parts[-2]
        repo = parts[-1]

        logger.info(f"🚀 Initializing GitHub Actions Monitor for {owner}/{repo}...")
        if task_id:
            task_manager.update_task(task_id, "building", message="Initializing GitHub Actions monitor...")
        
        # Give GitHub a few seconds to register the fresh push
        await asyncio.sleep(5)
        
        run = await self._get_latest_workflow_run(owner, repo, token)
        if not run:
            logger.warning("Could not find a recent GitHub Actions workflow run.")
            if task_id:
                task_manager.update_task(task_id, "failed", message="Could not find a recent GitHub Actions workflow run.")
            return
            
        run_id = run["id"]
        run_name = run.get("name", "CI/CD Pipeline")
        jobs_url = run["jobs_url"]
        commit_sha = run.get("head_sha", "N/A")[:7]
        
        logger.info(f"[GitHub Actions] ⏳ Pipeline Discovered: {run_name} (ID: {run_id})")
        if task_id:
            task_manager.update_task(task_id, "building", message=f"Pipeline Discovered: {run_name}", commit=commit_sha)
        
        # Track seen steps to avoid duplicate logging
        seen_steps = set()
        
        while True:
            run_status = await self._get_latest_workflow_run(owner, repo, token)
            if not run_status or run_status["id"] != run_id: 
                break

            status = run_status.get("status")
            conclusion = run_status.get("conclusion")

            # Fetch live jobs and steps
            jobs = await self._get_job_steps(jobs_url, token)
            
            for job in jobs:
                job_name = job.get("name")
                for step in job.get("steps", []):
                    step_name = step.get("name").lower()
                    step_status = step.get("status")
                    step_conclusion = step.get("conclusion")
                    
                    # Create a unique ID for the step state
                    step_id_key = f"{job_name}-{step_name}-{step_status}-{step_conclusion}"
                    
                    if step_id_key not in seen_steps:
                        seen_steps.add(step_id_key)
                        
                        if step_status == "in_progress":
                            logger.info(f"[GitHub Actions] 🔄 Running: {step_name}")
                            if task_id:
                                # Try to distinguish between build and deploy
                                if any(word in step_name for word in ["deploy", "push", "publish"]):
                                    task_manager.update_task(task_id, "deploying", message=f"GitHub Actions: {step_name}")
                                else:
                                    task_manager.update_task(task_id, "building", message=f"GitHub Actions: {step_name}")
                        elif step_status == "completed":
                            if step_conclusion == "success":
                                logger.info(f"[GitHub Actions] ✅ Success: {step_name}")
                            elif step_conclusion in ["failure", "cancelled"]:
                                logger.error(f"[GitHub Actions] ❌ Failed: {step_name}")
                            elif step_conclusion == "skipped":
                                logger.warning(f"[GitHub Actions] ⏭️ Skipped: {step_name}")

            # If the entire workflow is done, report and exit
            if status == "completed":
                if conclusion == "success":
                    logger.info(f"🎉 Pipeline Complete! Your application is officially deployed and stored in GHCR!")
                    if task_id:
                        task_manager.update_task(task_id, "completed")
                else:
                    logger.error(f"🚨 Pipeline terminated with conclusion: {conclusion}. Please check your GitHub Actions tab.")
                    if task_id:
                        task_manager.update_task(task_id, "failed", message=f"Pipeline failed with conclusion: {conclusion}")
                    
                    # AI Auto-Fixing Trigger
                    logger.info(f"[AI Agent] 🧠 Downloading crash logs for analysis...")
                    
                    failed_job = None
                    for job in jobs:
                        if job.get("conclusion") in ["failure", "timed_out", "cancelled"]:
                            failed_job = job
                            break
                    
                    if failed_job:
                        job_id = failed_job.get("id")
                        raw_logs = await self._get_job_logs(owner, repo, job_id, token)
                        if raw_logs:
                            from app.services.ai_service import ai_service
                            workflow_path = run.get("path")
                            diagnosis_json = await ai_service.analyze_build_failure(raw_logs, repo_url, workflow_path)
                            if diagnosis_json:
                                logger.info(f"[AUTO_FIX_PAYLOAD] {diagnosis_json}")
                
                if conclusion == "success":
                    logger.info(f"🔗 View Full Logs: https://github.com/{owner}/{repo}/actions/runs/{run_id}")
                break
                
            await asyncio.sleep(4)

github_actions_service = GitHubActionsService()
