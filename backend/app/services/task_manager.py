from typing import Dict, Any, Optional
import datetime
from loguru import logger

class TaskManager:
    def __init__(self):
        # In-memory store for now. In production, use Redis or Database.
        self.tasks: Dict[str, Any] = {}

    def update_task(self, task_id: str, status: str, message: str = "", user_id: Optional[str] = None, **kwargs):
        """
        Updates the status of a specific task.
        Status options: 'cloning', 'analyzing', 'generating', 'pushing', 'building', 'deploying', 'completed', 'failed'
        """
        if task_id not in self.tasks:
            self.tasks[task_id] = {
                "id": task_id,
                "user_id": user_id,
                "created_at": datetime.datetime.now().isoformat(),
                "start_time": datetime.datetime.now(),
                "repo_url": kwargs.get("repo_url", "Unknown"),
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
        # Skip storage if the task has security warnings — those are advisory only
        # and must not pollute the deployments collection with false failures.
        import asyncio
        from app.db.mongodb import db
        _skip_statuses = {"security_warning", "awaiting_push_confirmation"}
        if task.get("status") in _skip_statuses:
            logger.debug(
                f"Task {task_id}: Skipping MongoDB sync — status is '{task.get('status')}' "
                f"(transient/advisory state, not stored)."
            )
        else:
            try:
                asyncio.create_task(db.store_deployment_data(task))
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
        return self.tasks.get(task_id)

    def list_tasks(self, user_id: Optional[str] = None) -> list:
        all_tasks = self.tasks.values()
        if user_id:
            all_tasks = [t for t in all_tasks if t.get("user_id") == user_id]
        return sorted(all_tasks, key=lambda x: x.get("created_at", ""), reverse=True)

task_manager = TaskManager()
