from loguru import logger
import os
from typing import Dict, Any, Optional
import inspect

from .docker_templates.python_template import PythonDockerTemplate
from .docker_templates.node_template import NodeDockerTemplate
from .docker_templates.php_template import PHPDockerTemplate
from .docker_templates.llm_template import LLMDockerTemplate

class FileGenerator:
    def __init__(self):
        self.strategies = {
            "Python": PythonDockerTemplate(),
            "JavaScript/TypeScript": NodeDockerTemplate(),
            "PHP": PHPDockerTemplate()
        }

    async def generate_deployment_files(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates all necessary deployment files (Dockerfile, .dockerignore) based on analysis findings.
        """
        success = True
        
        # 1. Generate Dockerfile
        df_success = await self.generate_dockerfile(workspace_path, findings)
        
        # 2. Generate .dockerignore
        di_success = self.generate_dockerignore(workspace_path, findings)
        
        # 3. Generate CI/CD workflow
        ci_success = self.generate_cicd_workflow(workspace_path, findings)
        
        # 4. Generate .env.example if env vars were detected
        env_success = self.generate_env_file(workspace_path, findings)
        
        return df_success and di_success and ci_success

    async def generate_dockerfile(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates a recommended Dockerfile using the appropriate template strategy.
        """
        dockerfile_path = os.path.join(workspace_path, "Dockerfile")
        
        if os.path.exists(dockerfile_path):
            logger.info("Dockerfile already exists. Skipping generation.")
            return False

        lang = findings.get("language")
        strategy = self.strategies.get(lang)

        if not strategy:
            logger.info(f"No specific Docker template found for language: {lang}. Falling back to LLM generation.")
            strategy = LLMDockerTemplate()

        if inspect.iscoroutinefunction(strategy.generate_dockerfile):
            content = await strategy.generate_dockerfile(findings)
        else:
            content = strategy.generate_dockerfile(findings)
        
        if content:
            try:
                with open(dockerfile_path, "w") as f:
                    f.write(content)
                logger.info(f"Generated Dockerfile at {dockerfile_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to generate Dockerfile: {e}")
        
        return False

    def generate_dockerignore(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates a .dockerignore file.
        """
        ignore_path = os.path.join(workspace_path, ".dockerignore")
        if os.path.exists(ignore_path):
            return False

        lang = findings.get("language")
        strategy = self.strategies.get(lang)

        # Fallback to base ignore if no specific strategy
        from .docker_templates.base import DockerTemplate
        content = strategy.generate_dockerignore(findings) if strategy else ".git\nnode_modules\n__pycache__\n"

        try:
            with open(ignore_path, "w") as f:
                f.write(content)
            logger.info(f"Generated .dockerignore at {ignore_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate .dockerignore: {e}")
            return False

    def generate_cicd_workflow(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates a GitHub Actions CI/CD workflow based on project.
        """
        github_dir = os.path.join(workspace_path, ".github", "workflows")
        os.makedirs(github_dir, exist_ok=True)
        workflow_path = os.path.join(github_dir, "deploy.yml")

        if os.path.exists(workflow_path):
            return False

        content = """name: Auto-Deployment CI/CD

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t app:latest .
"""
        try:
            with open(workflow_path, "w") as f:
                f.write(content)
            logger.info(f"Generated CI/CD workflow at {workflow_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate CI/CD workflow: {e}")
            return False

    def generate_env_file(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates an environment template if env variables were found.
        """
        env_vars = findings.get("env_vars", [])
        if not env_vars:
            return False

        env_path = os.path.join(workspace_path, ".env.example")
        if os.path.exists(env_path):
            return False

        try:
            with open(env_path, "w") as f:
                for var in env_vars:
                    f.write(f"{var}=your_value_here\n")
            logger.info(f"Generated .env.example at {env_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate .env.example: {e}")
            return False

file_generator = FileGenerator()
