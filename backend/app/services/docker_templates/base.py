from abc import ABC, abstractmethod
from typing import Dict, Any

class DockerTemplate(ABC):
    @abstractmethod
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        """Generates the Dockerfile content."""
        pass

    def generate_dockerignore(self, findings: Dict[str, Any]) -> str:
        """Generates the .dockerignore content."""
        return (
            ".git\n"
            "__pycache__\n"
            "node_modules\n"
            ".env\n"
            "*.pyc\n"
            ".pytest_cache\n"
            "dist\n"
            "build\n"
        )
