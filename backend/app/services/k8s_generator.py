import os
import re
from typing import Dict, Any, Optional
import yaml
from loguru import logger
from pydantic import BaseModel

class KubernetesConfig(BaseModel):
    """
    Input model for Kubernetes manifest generation.
    """
    repo_name: str
    ghcr_image: str
    container_port: Optional[int] = None
    replicas: Optional[int] = None

def detect_container_port(framework: Optional[str] = None) -> int:
    """
    Detects the container port based on the framework or project type.

    Rules:
    - FastAPI -> 8000
    - Flask -> 5000
    - Express -> 3000
    - React (Static) -> 80
    - Spring Boot -> 8080
    - Django -> 8000
    - Laravel -> 8000
    - PHP Apache -> 80
    - If unknown -> 8080
    """
    if not framework:
        return 8080

    fw = framework.strip().lower()
    if "fastapi" in fw:
        return 8000
    elif "flask" in fw:
        return 5000
    elif "express" in fw:
        return 3000
    elif "react" in fw or "static" in fw:
        return 80
    elif "spring boot" in fw or "springboot" in fw:
        return 8080
    elif "django" in fw:
        return 8000
    elif "laravel" in fw:
        return 8000
    elif "php apache" in fw or "php-apache" in fw or "php" in fw:
        return 80
    else:
        return 8080

def recommend_replicas(project_type: Optional[str] = None) -> int:
    """
    Recommends replica count based on project type.

    Rules:
    - Small project -> 1 replica
    - REST API -> 2 replicas
    - Microservice -> 3 replicas
    - Default: 2 replicas
    """
    if not project_type:
        return 2

    pt = project_type.strip().lower()
    if "small" in pt:
        return 1
    elif "rest api" in pt or "api" in pt:
        return 2
    elif "microservice" in pt:
        return 3
    else:
        return 2

def generate_deployment_yaml(repo_name: str, ghcr_image: str, container_port: int, replicas: int = 2, pull_secret_name: Optional[str] = None, image_pull_policy: str = "Always") -> str:
    """
    Generates a Kubernetes deployment manifest dynamically using PyYAML.
    If pull_secret_name is provided, imagePullSecrets is added to the pod spec
    so Minikube can pull private images from GHCR.
    If image_pull_policy is 'IfNotPresent', Kubernetes uses a pre-loaded image
    (loaded via `minikube image load`) without contacting the registry.
    """
    pod_spec: dict = {
        "containers": [
            {
                "name": repo_name,
                "image": ghcr_image,
                "imagePullPolicy": image_pull_policy,
                "ports": [
                    {
                        "containerPort": container_port
                    }
                ]
            }
        ]
    }

    # Inject imagePullSecrets when a registry credential secret is available
    if pull_secret_name:
        pod_spec["imagePullSecrets"] = [{"name": pull_secret_name}]

    deployment_dict = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": repo_name
        },
        "spec": {
            "replicas": replicas,
            "selector": {
                "matchLabels": {
                    "app": repo_name
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": repo_name
                    }
                },
                "spec": pod_spec
            }
        }
    }
    return yaml.dump(deployment_dict, sort_keys=False, default_flow_style=False)

def generate_service_yaml(repo_name: str, container_port: int) -> str:
    """
    Generates a Kubernetes service manifest dynamically using PyYAML.
    """
    service_dict = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": f"{repo_name}-service"
        },
        "spec": {
            "selector": {
                "app": repo_name
            },
            "ports": [
                {
                    "port": 80,
                    "targetPort": container_port
                }
            ],
            "type": "NodePort"
        }
    }
    return yaml.dump(service_dict, sort_keys=False, default_flow_style=False)

def save_yaml_files(repo_name: str, deployment_content: str, service_content: str, output_dir: str) -> Dict[str, str]:
    """
    Saves the generated deployment and service yaml files to the specified output directory.
    Maintains backward compatibility with minikube_deployment_manager.py.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
    except FileNotFoundError as fnf:
        logger.error(f"Directory missing: {fnf}")
        raise FileNotFoundError("Directory missing") from fnf
    except PermissionError as pe:
        logger.error(f"Permission denied: {pe}")
        raise PermissionError("Permission denied") from pe

    dep_path = os.path.join(output_dir, "deployment.yaml")
    svc_path = os.path.join(output_dir, "service.yaml")

    try:
        with open(dep_path, "w") as f:
            f.write(deployment_content)
    except FileNotFoundError as fnf:
        logger.error(f"Directory missing when saving deployment.yaml: {fnf}")
        raise FileNotFoundError("Directory missing") from fnf
    except PermissionError as pe:
        logger.error(f"Permission denied when saving deployment.yaml: {pe}")
        raise PermissionError("Permission denied") from pe

    try:
        with open(svc_path, "w") as f:
            f.write(service_content)
    except FileNotFoundError as fnf:
        logger.error(f"Directory missing when saving service.yaml: {fnf}")
        raise FileNotFoundError("Directory missing") from fnf
    except PermissionError as pe:
        logger.error(f"Permission denied when saving service.yaml: {pe}")
        raise PermissionError("Permission denied") from pe

    return {
        "deployment_path": dep_path,
        "service_path": svc_path
    }

def generate_k8s_files(config: KubernetesConfig) -> Dict[str, Any]:
    """
    Generates deployment and service YAML manifests for a given Kubernetes config and saves them.

    Raises:
        ValueError: For missing repository name or invalid GHCR image format.
        FileNotFoundError: If the target output directory is missing and cannot be created.
        PermissionError: If there are permission issues creating the directory or writing files.
    """
    # 1. Validation
    if not config.repo_name or not config.repo_name.strip():
        logger.error("Missing repository name in config")
        raise ValueError("Missing repository name")

    if not config.ghcr_image or not isinstance(config.ghcr_image, str) or "ghcr.io/" not in config.ghcr_image:
        logger.error("Invalid GHCR image format: must contain 'ghcr.io/'")
        raise ValueError("Invalid GHCR image")

    # 2. Port and Replica Resolution
    port = config.container_port
    if not port:
        inferred = None
        repo_lower = config.repo_name.lower()
        if "fastapi" in repo_lower:
            inferred = "FastAPI"
        elif "flask" in repo_lower:
            inferred = "Flask"
        elif "express" in repo_lower:
            inferred = "Express"
        elif "react" in repo_lower:
            inferred = "React (Static)"
        elif "spring" in repo_lower or "boot" in repo_lower:
            inferred = "Spring Boot"
        elif "django" in repo_lower:
            inferred = "Django"
        elif "laravel" in repo_lower:
            inferred = "Laravel"
        elif "php" in repo_lower:
            inferred = "PHP Apache"

        port = detect_container_port(inferred)

    replicas = config.replicas
    if not replicas:
        inferred_type = None
        repo_lower = config.repo_name.lower()
        if "microservice" in repo_lower:
            inferred_type = "Microservice"
        elif "api" in repo_lower or "service" in repo_lower:
            inferred_type = "REST API"
        elif "small" in repo_lower or "demo" in repo_lower or "test" in repo_lower:
            inferred_type = "Small project"

        replicas = recommend_replicas(inferred_type)

    # 3. Generate YAML strings using Loguru logging as requested
    logger.info("Generating deployment.yaml...")
    deployment_content = generate_deployment_yaml(
        repo_name=config.repo_name,
        ghcr_image=config.ghcr_image,
        container_port=port,
        replicas=replicas
    )

    logger.info("Generating service.yaml...")
    service_content = generate_service_yaml(
        repo_name=config.repo_name,
        container_port=port
    )

    # 4. Save YAML files to target directory
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "temp", "k8s"))

    saved_paths = save_yaml_files(
        repo_name=config.repo_name,
        deployment_content=deployment_content,
        service_content=service_content,
        output_dir=output_dir
    )

    logger.info("Files saved successfully.")

    return {
        "deployment_yaml_path": saved_paths["deployment_path"],
        "service_yaml_path": saved_paths["service_path"],
        "container_port": port,
        "replicas": replicas
    }
