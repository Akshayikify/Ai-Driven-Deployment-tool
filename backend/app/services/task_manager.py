from typing import Dict, Any, Optional
import datetime
from loguru import logger

class TaskManager:
    def __init__(self):
        # In-memory store for now. In production, use Redis or Database.
        self.tasks: Dict[str, Any] = {}
        # Alias map: old_task_id -> new_task_id when a repo is re-tested
        self.task_aliases: Dict[str, str] = {}

    def update_task(self, task_id: str, status: str, message: str = "", user_id: Optional[str] = None, **kwargs):
        """
        Updates the status of a specific task.
        Status options: 'cloning', 'analyzing', 'generating', 'pushing', 'building', 'deploying', 'completed', 'failed'
        """
        if task_id not in self.tasks:
            repo_url = kwargs.get("repo_url", "Unknown")
            
            # If re-testing an existing repo, clean up any previous in-memory task for that repo
            if repo_url and repo_url != "Unknown":
                from app.db.mongodb import normalize_repo_url
                clean_target = normalize_repo_url(repo_url).lower()
                if clean_target:
                    stale_ids = [
                        tid for tid, t in self.tasks.items()
                        if normalize_repo_url(t.get("repo_url")).lower() == clean_target and tid != task_id
                    ]
                    for stale_id in stale_ids:
                        self.task_aliases[stale_id] = task_id
                        self.tasks.pop(stale_id, None)

            self.tasks[task_id] = {
                "id": task_id,
                "user_id": user_id,
                "created_at": datetime.datetime.now().isoformat(),
                "start_time": datetime.datetime.now(),
                "repo_url": repo_url,
                "environment": kwargs.get("environment", "production"),
                "commit": kwargs.get("commit", "N/A"),
                "duration": kwargs.get("duration", "-"),
                "steps": [
                    {"id": "upload",   "title": "Code Uploaded",  "description": "Project files successfully uploaded to the platform", "status": "completed", "timestamp": "Just now"},
                    {"id": "analyze",  "title": "AI Analysis",    "description": "Analyzing project structure and dependencies", "status": "pending"},
                    {"id": "security", "title": "Security Scan",  "description": "Scanning for hardcoded secrets and API keys", "status": "pending"},
                    {"id": "build",    "title": "Build Process",  "description": "Building application for deployment", "status": "pending"},
                    {"id": "minikube_deploy", "title": "Deploying To Minikube", "description": "Preparing Kubernetes manifests", "status": "pending"},
                    {"id": "minikube_deployment", "title": "Creating Deployment", "description": "Applying deployment manifest to cluster", "status": "pending"},
                    {"id": "minikube_service", "title": "Creating Service", "description": "Applying service manifest to cluster", "status": "pending"},
                    {"id": "minikube_pods", "title": "Waiting For Pods", "description": "Waiting for pods to be in Running state", "status": "pending"},
                    {"id": "minikube_live", "title": "Application Live", "description": "Deployment is live on local Minikube cluster", "status": "pending"},
                ],
                "current_message": "Task initialized",
                "status": "pending"
            }
        
        task = self.tasks[task_id]
        
        # If user_id was provided later, update it (though it should be provided at creation)
        if user_id:
            task["user_id"] = user_id
            
        # Update extra fields if provided
        for key, value in kwargs.items():
            task[key] = value

        if status == "cloning":
            self._update_step(task, "analyze", "active")
            task["current_message"] = "Cloning repository..."
            task["status"] = "running"
        elif status == "analyzing":
            self._update_step(task, "analyze", "active")
            task["current_message"] = "Analyzing project structure..."
            task["status"] = "running"
        elif status == "security_scanning":
            self._update_step(task, "analyze", "completed")
            self._update_step(task, "security", "active")
            task["current_message"] = "🔍 Scanning for hardcoded secrets and API keys..."
            task["status"] = "running"
        elif status == "security_failed":
            # Security alerts are treated as warnings only — they do NOT mark the
            # deployment as failed and are NOT persisted to MongoDB.
            # The frontend still sees the findings for display purposes.
            self._update_step(task, "security", "failed")
            task["current_message"] = f"⚠️ Security findings detected (not stored): {message}"
            task["status"] = "security_warning"  # distinct non-failed status
            # Store the security report dict on the task for the frontend to display
            if "security_report" in kwargs:
                task["security_report"] = kwargs["security_report"]
            # Calculate duration
            if "start_time" in task:
                diff = datetime.datetime.now() - task["start_time"]
                seconds = int(diff.total_seconds())
                task["duration"] = f"{seconds}s" if seconds < 60 else f"{seconds // 60}m {seconds % 60}s"
        elif status == "awaiting_push_confirmation":
            # Pipeline has generated files but paused — waiting for the user to
            # explicitly approve or cancel the GitHub push after reviewing findings.
            self._update_step(task, "security", "failed")   # amber warning icon on Security step
            self._update_step(task, "build", "pending")     # downstream steps remain pending
            task["current_message"] = (
                "⏸️ Security findings detected. Awaiting your confirmation to push to GitHub."
            )
            task["status"] = "awaiting_push_confirmation"
            if "security_report" in kwargs:
                task["security_report"] = kwargs["security_report"]
        elif status == "generating":
            self._update_step(task, "security", "completed")
            self._update_step(task, "build", "active")
            task["current_message"] = "Generating deployment files..."
            task["status"] = "running"
        elif status == "pushing":
            self._update_step(task, "build", "active")
            task["current_message"] = "Pushing changes to GitHub..."
            task["status"] = "running"
        elif status == "building":
            self._update_step(task, "analyze", "completed")
            self._update_step(task, "build", "active")
            task["current_message"] = "GitHub Actions Pipeline: Building..."
            task["status"] = "running"
        elif status == "deploying":
            self._update_step(task, "build", "completed")
            self._update_step(task, "minikube_deploy", "active")
            task["current_message"] = "GitHub Actions Pipeline: Deploying..."
            task["status"] = "running"
        elif status == "deploying_to_minikube":
            self._update_step(task, "build", "completed")
            self._update_step(task, "minikube_deploy", "active")
            task["current_message"] = "Deploying to Minikube..."
            task["status"] = "running"
        elif status == "creating_deployment":
            self._update_step(task, "minikube_deploy", "completed")
            self._update_step(task, "minikube_deployment", "active")
            task["current_message"] = "Creating Kubernetes Deployment..."
            task["status"] = "running"
        elif status == "creating_service":
            self._update_step(task, "minikube_deployment", "completed")
            self._update_step(task, "minikube_service", "active")
            task["current_message"] = "Creating Kubernetes Service..."
            task["status"] = "running"
        elif status == "waiting_for_pods":
            self._update_step(task, "minikube_service", "completed")
            self._update_step(task, "minikube_pods", "active")
            task["current_message"] = "Waiting for pods to be in Running state..."
            task["status"] = "running"
        elif status == "application_live":
            self._update_step(task, "minikube_pods", "completed")
            self._update_step(task, "minikube_live", "completed")
            task["current_message"] = "Application Live!"
            task["status"] = "success"
            
            # Calculate duration
            if "start_time" in task:
                diff = datetime.datetime.now() - task["start_time"]
                seconds = int(diff.total_seconds())
                if seconds < 60:
                    task["duration"] = f"{seconds}s"
                else:
                    task["duration"] = f"{seconds // 60}m {seconds % 60}s"
        elif status == "ready_to_deploy":
            self._update_step(task, "upload", "completed")
            self._update_step(task, "analyze", "completed")
            self._update_step(task, "security", "completed")
            self._update_step(task, "build", "pending")
            task["current_message"] = message or "AI analysis complete and deployment files generated."
            task["status"] = "ready_to_deploy"
            if "start_time" in task:
                diff = datetime.datetime.now() - task["start_time"]
                seconds = int(diff.total_seconds())
                task["duration"] = f"{seconds}s" if seconds < 60 else f"{seconds // 60}m {seconds % 60}s"
        elif status == "completed":
            self._update_step(task, "analyze", "completed")
            self._update_step(task, "build", "completed")
            self._update_step(task, "minikube_deploy", "completed")
            self._update_step(task, "minikube_deployment", "completed")
            self._update_step(task, "minikube_service", "completed")
            self._update_step(task, "minikube_pods", "completed")
            self._update_step(task, "minikube_live", "completed")
            task["current_message"] = "Deployment complete!"
            task["status"] = "success"
            
            # Calculate duration
            if "start_time" in task:
                diff = datetime.datetime.now() - task["start_time"]
                seconds = int(diff.total_seconds())
                if seconds < 60:
                    task["duration"] = f"{seconds}s"
                else:
                    task["duration"] = f"{seconds // 60}m {seconds % 60}s"
        elif status == "failed":
            task["current_message"] = f"Error: {message}"
            task["status"] = "failed"
            # Calculate duration even on failure
            if "start_time" in task:
                diff = datetime.datetime.now() - task["start_time"]
                seconds = int(diff.total_seconds())
                if seconds < 60:
                    task["duration"] = f"{seconds}s"
                else:
                    task["duration"] = f"{seconds // 60}m {seconds % 60}s"
            
            # Mark current active steps as pending or failed
            for step in task["steps"]:
                if step["status"] == "active":
                    step["status"] = "pending"
            
        task["updated_at"] = datetime.datetime.now().isoformat()
        logger.debug(f"Task {task_id} updated to {status}")
        
        # Async sync to MongoDB for analytics and history.
        # Skip storage if the task is in an advisory / pre-deployment state.
        import asyncio
        from app.db.mongodb import db
        _skip_statuses = {"security_warning", "awaiting_push_confirmation", "ready_to_deploy"}
        if task.get("status") in _skip_statuses:
            logger.debug(
                f"Task {task_id}: Skipping MongoDB sync — status is '{task.get('status')}' "
                f"(transient/advisory state, not stored)."
            )
        else:
            try:
                # Pass a snapshot copy to avoid in-flight mutation race conditions
                asyncio.create_task(db.store_deployment_data(task.copy()))
            except Exception as e:
                logger.warning(f"Failed to trigger MongoDB sync for task {task_id}: {e}")

    def _update_step(self, task: dict, step_id: str, status: str):
        for step in task["steps"]:
            if step["id"] == step_id:
                # Don't downgrade status (e.g., from completed to active)
                if status == "active" and step["status"] == "completed":
                    return
                step["status"] = status
                if status in ("completed", "failed"):
                    step["timestamp"] = datetime.datetime.now().strftime("%H:%M:%S")
                break

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        if task_id in self.tasks:
            return self.tasks[task_id]
        # Fallback to alias if an older task was superseded by a re-test
        aliased_id = self.task_aliases.get(task_id)
        if aliased_id and aliased_id in self.tasks:
            return self.tasks[aliased_id]
        return None

    def list_tasks(self, user_id: Optional[str] = None) -> list:
        from app.db.mongodb import normalize_repo_url
        all_tasks = list(self.tasks.values())
        if user_id:
            all_tasks = [t for t in all_tasks if t.get("user_id") == user_id]

        # Deduplicate by normalized repo_url so only the latest run for each repo is returned
        seen_repos = set()
        deduped = []
        for t in sorted(all_tasks, key=lambda x: str(x.get("updated_at") or x.get("created_at") or ""), reverse=True):
            r_url = normalize_repo_url(t.get("repo_url")).lower()
            if r_url:
                if r_url in seen_repos:
                    continue
                seen_repos.add(r_url)
            deduped.append(t)
        return deduped

task_manager = TaskManager()
