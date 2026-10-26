from .base import DockerTemplate
from typing import Dict, Any


class StaticDockerTemplate(DockerTemplate):
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        """Serves a plain HTML/CSS/JS site with nginx."""
        return "\n".join([
            "FROM nginx:alpine",
            "COPY . /usr/share/nginx/html",
            "EXPOSE 80",
            "",
        ])

    def generate_dockerignore(self, findings: Dict[str, Any]) -> str:
        return ".git\n.github\nDockerfile\n.dockerignore\n"
