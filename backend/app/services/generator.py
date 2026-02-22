from loguru import logger
import os
from typing import Dict, Any, Optional
from .docker_templates.python_template import PythonDockerTemplate
from .docker_templates.node_template import NodeDockerTemplate

class FileGenerator:
    def __init__(self):
        self.strategies = {
            "Python": PythonDockerTemplate(),
            "JavaScript/TypeScript": NodeDockerTemplate()
        }

    def generate_deployment_files(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates all necessary deployment files (Dockerfile, .dockerignore) based on analysis findings.
        """
        success = True
        
        # 1. Generate Dockerfile
        df_success = self.generate_dockerfile(workspace_path, findings)
        
        # 2. Generate .dockerignore
        di_success = self.generate_dockerignore(workspace_path, findings)
        
        return df_success and di_success

    def generate_dockerfile(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
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
            logger.warning(f"No Docker template found for language: {lang}")
            return False

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

file_generator = FileGenerator()
