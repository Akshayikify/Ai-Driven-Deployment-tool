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
