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

    async def monitor_workflow(self, repo_url: str, token: str):
        """
        Monitors a newly triggered GitHub Actions workflow and logs the progress natively.
        """
        # 1. Parse Owner and Repo from URL
        # e.g., https://github.com/Akshayikify/SDC-Registration-Web-app.git
        clean_url = repo_url.replace(".git", "")
        parts = clean_url.split("/")
        if len(parts) < 2:
            logger.error(f"Could not parse repository owner and name from URL: {repo_url}")
            return
            
        owner = parts[-2]
        repo = parts[-1]

        logger.info(f"🚀 Initializing GitHub Actions Monitor for {owner}/{repo}...")
        
        # Give GitHub a few seconds to register the fresh push
        await asyncio.sleep(5)
        
        run = await self._get_latest_workflow_run(owner, repo, token)
        if not run:
            logger.warning("Could not find a recent GitHub Actions workflow run.")
            return
            
        run_id = run["id"]
        run_name = run.get("name", "CI/CD Pipeline")
        jobs_url = run["jobs_url"]
        
        logger.info(f"[GitHub Actions] ⏳ Pipeline Discovered: {run_name} (ID: {run_id})")
        
        # Track seen steps to avoid duplicate logging
        seen_steps = set()
        
        while True:
            run_status = await self._get_latest_workflow_run(owner, repo, token)
            # If we lost it, abort gracefully
            if not run_status or run_status["id"] != run_id: 
                break

            status = run_status.get("status")
            conclusion = run_status.get("conclusion")

            # Fetch live jobs and steps
            jobs = await self._get_job_steps(jobs_url, token)
            
            for job in jobs:
                job_name = job.get("name")
                for step in job.get("steps", []):
                    step_name = step.get("name")
                    step_status = step.get("status")
                    step_conclusion = step.get("conclusion")
                    
                    # Create a unique ID for the step state
                    step_id = f"{job_name}-{step_name}-{step_status}-{step_conclusion}"
                    
                    if step_id not in seen_steps:
                        seen_steps.add(step_id)
                        
                        if step_status == "in_progress":
                            logger.info(f"[GitHub Actions] 🔄 Running: {step_name}")
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
                else:
                    logger.error(f"🚨 Pipeline terminated with conclusion: {conclusion}. Please check your GitHub Actions tab.")
                
                # Link to the actions tab natively
                logger.info(f"🔗 View Full Logs: https://github.com/{owner}/{repo}/actions/runs/{run_id}")
                break
                
            # Poll every 4 seconds
            await asyncio.sleep(4)

github_actions_service = GitHubActionsService()
