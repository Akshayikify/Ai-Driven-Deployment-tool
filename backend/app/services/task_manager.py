from typing import Dict, Any, Optional
import datetime
from loguru import logger

class TaskManager:
    def __init__(self):
        # In-memory store for now. In production, use Redis or Database.
        self.tasks: Dict[str, Any] = {}

    def update_task(self, task_id: str, status: str, message: str = ""):
        """
        Updates the status of a specific task.
        Status options: 'cloning', 'analyzing', 'generating', 'pushing', 'completed', 'failed'
        """
        if task_id not in self.tasks:
            self.tasks[task_id] = {
                "id": task_id,
                "created_at": datetime.datetime.now().isoformat(),
                "steps": [
                    {"id": "upload", "title": "Code Uploaded", "description": "Project files successfully uploaded to the platform", "status": "completed", "timestamp": "Just now"},
                    {"id": "analyze", "title": "AI Analysis", "description": "Analyzing project structure and dependencies", "status": "pending"},
                    {"id": "build", "title": "Build Process", "description": "Building application for deployment", "status": "pending"},
                    {"id": "deploy", "title": "Deployment", "description": "Deploying to production environment", "status": "pending"},
                    {"id": "monitor", "title": "Monitoring", "description": "Setting up monitoring and alerts", "status": "pending"},
                ],
                "current_message": "Task initialized",
            }
        
        task = self.tasks[task_id]
        
        if status == "cloning":
            self._update_step(task, "analyze", "active")
            task["current_message"] = "Cloning repository..."
        elif status == "analyzing":
            self._update_step(task, "analyze", "active")
            task["current_message"] = "Analyzing project structure..."
        elif status == "generating":
            # Analysis is essentially done when we start generating
            self._update_step(task, "analyze", "active")
            task["current_message"] = "Generating deployment files..."
        elif status == "pushing":
            self._update_step(task, "analyze", "active")
            task["current_message"] = "Pushing changes to GitHub..."
        elif status == "completed":
            self._update_step(task, "analyze", "completed")
            # Build and Deploy stay pending until we implement those phases
            self._update_step(task, "build", "pending")
            self._update_step(task, "deploy", "pending")
            self._update_step(task, "monitor", "pending")
            task["current_message"] = "Analysis and generation complete."
        elif status == "failed":
            task["current_message"] = f"Error: {message}"
            # Mark active steps as pending or error if needed
            
        task["updated_at"] = datetime.datetime.now().isoformat()
        logger.debug(f"Task {task_id} updated to {status}")

    def _update_step(self, task: dict, step_id: str, status: str):
        for step in task["steps"]:
            if step["id"] == step_id:
                step["status"] = status
                if status == "completed":
                    step["timestamp"] = "Just now"
                break

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.tasks.get(task_id)

task_manager = TaskManager()
