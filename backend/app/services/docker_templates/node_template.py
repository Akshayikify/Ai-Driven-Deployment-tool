from .base import DockerTemplate
from typing import Dict, Any

class NodeDockerTemplate(DockerTemplate):
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        framework = findings.get("framework", "Node.js (Generic)")
        
        # Determine port - logic can be improved
        port = 3000
        
        content = [
            "FROM node:20-slim AS builder",
            "WORKDIR /app",
            "COPY package*.json ./",
            "RUN npm install",
            "COPY . .",
            "RUN npm run build --if-present",
            "",
            "FROM node:20-slim",
            "WORKDIR /app",
            "RUN groupadd -r appuser && useradd -r -g appuser appuser",
            "",
            "COPY --from=builder /app ./",
            "",
            f"EXPOSE {port}",
            "USER appuser",
            'CMD ["npm", "start"]'
        ]

        return "\n".join(content)
