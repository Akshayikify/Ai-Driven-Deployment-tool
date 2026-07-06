from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

from app.services.minikube_deployment_manager import deploy_to_minikube
from app.services.task_manager import task_manager

router = APIRouter()

class MinikubeDeployRequest(BaseModel):
    repo_url: str
    ghcr_image: str
    user_id: Optional[str] = "anonymous"

@router.post("/minikube")
async def trigger_minikube_deployment(request: MinikubeDeployRequest):
    """
    Synchronously triggers local Minikube deployment for a given GHCR image.
    This creates an in-memory task to track progress and returns the final deployment URL.
    """
    clean_url = request.repo_url.replace(".git", "")
    repo_name = clean_url.split("/")[-1]
    
    # Create a unique task ID to track this run in the TaskManager
    task_id = str(uuid.uuid4())
    task_manager.update_task(
        task_id,
        "initialized",
        repo_url=request.repo_url,
        user_id=request.user_id
    )
    
    # Run the deployment (which is async and handles command execution asynchronously)
    result = await deploy_to_minikube(task_id, repo_name, request.ghcr_image, None)
    
    if result.get("deployment_status") == "success":
        return {
            "status": "success",
            "deployment_url": result.get("application_url", "")
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Local Minikube deployment failed: {result.get('error', 'Unknown error')}"
        )
