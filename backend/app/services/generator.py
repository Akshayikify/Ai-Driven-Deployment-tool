from loguru import logger
import os

class FileGenerator:
    def generate_dockerfile(self, workspace_path: str, findings: dict) -> bool:
        """
        Generates a recommended Dockerfile based on analysis results.
        """
        dockerfile_path = os.path.join(workspace_path, "Dockerfile")
        
        if os.path.exists(dockerfile_path):
            logger.info("Dockerfile already exists. Skipping generation.")
            return False

        content = ""
        lang = findings.get("language")
        framework = findings.get("framework")

        if lang == "Python":
            content = (
                "FROM python:3.11-slim\n"
                "WORKDIR /app\n"
                "COPY requirements.txt .\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n"
                "COPY . .\n"
            )
            if framework == "FastAPI":
                content += "CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"
            else:
                content += "CMD [\"python\", \"main.py\"]\n"

        elif lang == "JavaScript/TypeScript":
            content = (
                "FROM node:20-slim\n"
                "WORKDIR /app\n"
                "COPY package*.json .\n"
                "RUN npm install\n"
                "COPY . .\n"
                "RUN npm run build\n"
                "CMD [\"npm\", \"start\"]\n"
            )

        if content:
            try:
                with open(dockerfile_path, "w") as f:
                    f.write(content)
                logger.info(f"Generated Dockerfile at {dockerfile_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to generate Dockerfile: {e}")
        
        return False

file_generator = FileGenerator()
