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

    def generate_cicd_workflow(self, findings: Dict[str, Any]) -> str:
        """Generates the .github/workflows/deploy.yml CI/CD pipeline content."""
        return """name: Generic Docker CI/CD

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Log in to the Container registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels) for Docker
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ghcr.io/${{ github.repository }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
"""
