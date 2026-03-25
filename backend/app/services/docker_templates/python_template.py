from .base import DockerTemplate
from typing import Dict, Any
import os

class PythonDockerTemplate(DockerTemplate):
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        framework = findings.get("framework", "Python (Generic)")
        entry_point = findings.get("entry_point", "main.py")
        
        # Determine port
        port = 8000
        if framework == "Django":
            port = 8000
        elif framework == "FastAPI":
            port = 8000
        elif framework == "Flask":
            port = 5000

        content = [
            "# Multi-stage build for efficiency",
            "FROM python:3.11-slim AS builder",
            "WORKDIR /app",
            "ENV PYTHONDONTWRITEBYTECODE 1",
            "ENV PYTHONUNBUFFERED 1",
            "",
            "RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev",
            "",
            "COPY requirements.txt .",
            "RUN pip install --no-cache-dir --user -r requirements.txt",
            "",
            "FROM python:3.11-slim",
            "WORKDIR /app",
            "",
            "# Create a non-root user",
            "RUN groupadd -r appuser && useradd -r -g appuser appuser",
            "",
            "COPY --from=builder /root/.local /home/appuser/.local",
            "COPY . .",
            "",
            "ENV PATH=/home/appuser/.local/bin:$PATH",
            f"EXPOSE {port}",
            "",
            "USER appuser",
        ]

        if framework == "FastAPI":
            # Strip file extension for uvicorn
            module = os.path.splitext(entry_point)[0].replace(os.path.sep, ".")
            content.append(f'CMD ["uvicorn", "{module}:app", "--host", "0.0.0.0", "--port", "{port}"]')
        elif framework == "Django":
            content.append(f'CMD ["python", "{entry_point}", "runserver", "0.0.0.0:{port}"]')
        elif framework == "Flask":
            module = os.path.splitext(entry_point)[0].replace(os.path.sep, ".")
            content.append(f'ENV FLASK_APP={module}')
            content.append(f'CMD ["flask", "run", "--host=0.0.0.0", "--port={port}"]')
        else:
            content.append(f'CMD ["python", "{entry_point}"]')

        content.append("")
        # Simple healthcheck (requires curl)
        # content.append(f"HEALTHCHECK --interval=30s --timeout=3s CMD curl --fail http://localhost:{port}/health || exit 1")

        return "\n".join(content)

    def generate_cicd_workflow(self, findings: Dict[str, Any]) -> str:
        """Generates a Python-specific CI/CD pipeline with Flake8, PyTest, and GHCR publishing."""
        return """name: Python CI/CD Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  test-and-lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          pip install flake8 pytest

      - name: Lint with flake8
        run: |
          # Stop the build if there are Python syntax errors or undefined names
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          # Exit-zero treats all errors as warnings.
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

      - name: Test with pytest
        run: |
          if [ -d tests ] || ls test_*.py 1> /dev/null 2>&1; then
            pytest
          else
            echo "No tests found. Skipping pytest."
          fi

  build-and-push:
    needs: test-and-lint
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

      - name: Lowercase repository name
        run: echo "IMAGE_ID=$(echo ${{ github.repository }} | tr '[:upper:]' '[:lower:]')" >> $GITHUB_ENV

      - name: Extract metadata (tags, labels) for Docker
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ghcr.io/${{ env.IMAGE_ID }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
"""
