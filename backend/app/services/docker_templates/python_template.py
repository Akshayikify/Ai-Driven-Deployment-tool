from .base import DockerTemplate
from typing import Dict, Any
import os

class PythonDockerTemplate(DockerTemplate):
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        framework = findings.get("framework", "Python (Generic)")
        entry_point = findings.get("entry_point") or "main.py"
        service_path = findings.get("path", "")
        if service_path and service_path != ".":
            service_path_clean = service_path.replace("\\", "/").rstrip("/") + "/"
            entry_point_clean = entry_point.replace("\\", "/")
            if entry_point_clean.startswith(service_path_clean):
                entry_point = entry_point_clean[len(service_path_clean):]

        detected = findings.get("detected_files", [])
        
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
            "ENV PYTHONDONTWRITEBYTECODE=1",
            "ENV PYTHONUNBUFFERED=1",
            "",
            "RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/*",
            "",
        ]

        # Conditional dependency installation — install system-wide (no --user)
        # so packages land in /usr/local/lib and are available to any user in final stage
        if "requirements.txt" in detected:
            content.append("COPY requirements.txt .")
            content.append("RUN pip install --no-cache-dir -r requirements.txt")
        elif "pyproject.toml" in detected:
            content.append("COPY pyproject.toml .")
            if "poetry.lock" in detected:
                content.append("COPY poetry.lock .")
            content.append("RUN pip install --no-cache-dir .")
        elif "Pipfile" in detected:
            content.append("COPY Pipfile* .")
            content.append("RUN pip install --no-cache-dir pipenv && pipenv install --system")

        content.extend([
            "",
            "FROM python:3.11-slim",
            "WORKDIR /app",
            "",
            "# Create a non-root user with home directory (-m flag)",
            "RUN groupadd -r appuser && useradd -r -m -g appuser appuser",
            "",
            "# Copy installed packages from builder stage (system-wide install)",
            "COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages",
            "COPY --from=builder /usr/local/bin /usr/local/bin",
            "COPY --chown=appuser:appuser . .",
            "",
            f"EXPOSE {port}",
            "",
            "USER appuser",
        ])

        if framework == "FastAPI":
            # Strip file extension for uvicorn
            module = os.path.splitext(entry_point)[0].replace("\\", ".").replace("/", ".")
            content.append(f'CMD ["uvicorn", "{module}:app", "--host", "0.0.0.0", "--port", "{port}"]')
        elif framework == "Django":
            # Use gunicorn for production; fall back to manage.py runserver if gunicorn not available
            content.append(f'CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:{port} --workers 2 $(python -c \\"import os; [print(f.replace(\\\'/\\\',\\\'.\\\')[:-3]) for f in [\\\'wsgi.py\\\'] if os.path.exists(f)]\\") 2>/dev/null || python manage.py runserver 0.0.0.0:{port}"]')
        elif framework == "Flask":
            module = os.path.splitext(entry_point)[0].replace("\\", ".").replace("/", ".")
            content.append(f'ENV FLASK_APP={module}')
            content.append(f'CMD ["flask", "run", "--host=0.0.0.0", "--port={port}"]')
        else:
            content.append(f'CMD ["python", "{entry_point}"]')

        content.append("")
        return "\n".join(content)


    def generate_cicd_workflow(self, findings: Dict[str, Any]) -> str:
        """Generates a Python-specific CI/CD pipeline with Flake8, PyTest, and GHCR publishing."""
        workdir = findings.get("path", ".")
        clean_workdir = workdir.strip("./")
        path_prefix = f"{clean_workdir}/" if clean_workdir and clean_workdir != "." else ""
        
        # Determine caching strategy based on detected files
        detected = findings.get("detected_files", [])
        cache_config = ""
        if "requirements.txt" in detected:
            cache_config = f"""          cache: "pip"
          cache-dependency-path: "{path_prefix}requirements.txt\""""
        elif "pyproject.toml" in detected:
            cache_config = f"""          cache: "pip"
          cache-dependency-path: "{path_prefix}pyproject.toml\""""
        elif "Pipfile" in detected:
            cache_config = f"""          cache: "pip"
          cache-dependency-path: "{path_prefix}Pipfile\""""

        return f"""name: Python CI/CD Pipeline

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
{cache_config}

      - name: Install dependencies
        working-directory: ./{clean_workdir}
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f pyproject.toml ]; then pip install .; fi
          pip install flake8 pytest

      - name: Lint with flake8
        working-directory: ./{clean_workdir}
        run: |
          # Stop the build if there are Python syntax errors or undefined names
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          # Exit-zero treats all errors as warnings.
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

      - name: Test with pytest
        working-directory: ./{clean_workdir}
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

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to the Container registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{{{ github.actor }}}}
          password: ${{{{ secrets.GITHUB_TOKEN }}}}

      - name: Lowercase repository name
        run: echo "IMAGE_ID=$(echo ${{{{ github.repository }}}} | tr '[:upper:]' '[:lower:]')" >> $GITHUB_ENV

      - name: Extract metadata (tags, labels) for Docker
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ghcr.io/${{{{ env.IMAGE_ID }}}}
          tags: |
            type=raw,value=latest,enable=${{{{ github.ref == 'refs/heads/main' }}}}
            type=sha,prefix=sha-,format=short

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./{clean_workdir}
          file: ./{clean_workdir}/Dockerfile
          push: ${{{{ github.event_name != 'pull_request' }}}}
          tags: ${{{{ steps.meta.outputs.tags }}}}
          labels: ${{{{ steps.meta.outputs.labels }}}}
          cache-from: type=gha
          cache-to: type=gha,mode=max
"""

    def generate_dockerignore(self, findings: Dict[str, Any]) -> str:
        return """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
venv/
ENV/
.pytest_cache/
.coverage
htmlcov/
"""
