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

    def generate_cicd_workflow(self, findings: Dict[str, Any]) -> str:
        """Generates a Node.js-specific CI/CD pipeline with NPM tests and GHCR publishing."""
        return """name: Node.js CI/CD Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci || npm install

      - name: Run Linter (if configured)
        run: npm run lint --if-present

      - name: Run Tests (if configured)
        run: npm test --if-present

  build-and-push:
    needs: test
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
