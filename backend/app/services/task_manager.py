from typing import Dict, Any, Optional
import datetime
from loguru import logger

class TaskManager:
    def __init__(self):
        # In-memory store for now. In production, use Redis or Database.
        self.tasks: Dict[str, Any] = {}

    def update_task(self, task_id: str, status: str, message: str = "", **kwargs):
        """
        Updates the status of a specific task.
        Status options: 'cloning', 'analyzing', 'generating', 'pushing', 'building', 'deploying', 'completed', 'failed'
        """
        if task_id not in self.tasks:
            self.tasks[task_id] = {
                "id": task_id,
                "created_at": datetime.datetime.now().isoformat(),
                "start_time": datetime.datetime.now(),
                "repo_url": kwargs.get("repo_url", "Unknown"),
                "environment": kwargs.get("environment", "production"),
                "commit": kwargs.get("commit", "N/A"),
                "duration": kwargs.get("duration", "-"),
                "steps": [
                    {"id": "upload", "title": "Code Uploaded", "description": "Project files successfully uploaded to the platform", "status": "completed", "timestamp": "Just now"},
                    {"id": "analyze", "title": "AI Analysis", "description": "Analyzing project structure and dependencies", "status": "pending"},
                    {"id": "build", "title": "Build Process", "description": "Building application for deployment", "status": "pending"},
                    {"id": "deploy", "title": "Deployment", "description": "Deploying to production environment", "status": "pending"},
                    {"id": "monitor", "title": "Monitoring", "description": "Setting up monitoring and alerts", "status": "pending"},
                ],
                "current_message": "Task initialized",
                "status": "pending"
            }
        
        task = self.tasks[task_id]
        
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
        elif status == "generating":
            self._update_step(task, "analyze", "active")
            task["current_message"] = "Generating deployment files..."
            task["status"] = "running"
        elif status == "pushing":
            self._update_step(task, "analyze", "active")
            task["current_message"] = "Pushing changes to GitHub..."
            task["status"] = "running"
        elif status == "building":
            self._update_step(task, "analyze", "completed")
            self._update_step(task, "build", "active")
            task["current_message"] = "GitHub Actions Pipeline: Building..."
            task["status"] = "running"
        elif status == "deploying":
            self._update_step(task, "build", "completed")
            self._update_step(task, "deploy", "active")
            task["current_message"] = "GitHub Actions Pipeline: Deploying..."
            task["status"] = "running"
        elif status == "completed":
            self._update_step(task, "analyze", "completed")
            self._update_step(task, "build", "completed")
            self._update_step(task, "deploy", "completed")
            self._update_step(task, "monitor", "completed")
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
        
        # Async sync to MongoDB for analytics and history
        import asyncio
        from app.db.mongodb import db
        try:
            # We use try/except and create_task to not block the main logic 
            # and handle cases where DB might not be connected yet
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
                if status == "completed":
                    step["timestamp"] = datetime.datetime.now().strftime("%H:%M:%S")
                break

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.tasks.get(task_id)

    def list_tasks(self) -> list:
        return sorted(self.tasks.values(), key=lambda x: x.get("created_at", ""), reverse=True)

task_manager = TaskManager()
