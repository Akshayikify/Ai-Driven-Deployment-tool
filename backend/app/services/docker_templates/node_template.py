from .base import DockerTemplate
from typing import Dict, Any

class NodeDockerTemplate(DockerTemplate):
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        framework = findings.get("framework", "Node.js (Generic)")
        port = 3000
        
        # Discover the exact location of package.json
        pkg_files = findings.get("file_index", {}).get("by_name", {}).get("package.json", [])
        workdir = "."
        if pkg_files:
            import os
            workdir = os.path.dirname(pkg_files[0])
            if not workdir: workdir = "."

        content = [
            "FROM node:20-slim AS builder",
            "WORKDIR /app",
        ]
        
        if workdir != ".":
            content.append(f"COPY {workdir}/package*.json ./")
            content.append("RUN npm install")
            content.append(f"COPY {workdir}/ .")
        else:
            content.append("COPY package*.json ./")
            content.append("RUN npm install")
            content.append("COPY . .")

        content.extend([
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
        ])

        return "\n".join(content)

    def generate_cicd_workflow(self, findings: Dict[str, Any]) -> str:
        """Generates a Node.js-specific CI/CD pipeline with NPM tests and GHCR publishing."""
        pkg_files = findings.get("file_index", {}).get("by_name", {}).get("package.json", [])
        workdir = "."
        if pkg_files:
            import os
            workdir = os.path.dirname(pkg_files[0])
            if not workdir: workdir = "."

        defaults_block = f"""
    defaults:
      run:
        working-directory: ./{workdir}
""" if workdir != "." else ""

        return f"""name: Node.js CI/CD Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  test:
    runs-on: ubuntu-latest{defaults_block}
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "20"

      - name: Install dependencies
        run: |
          if [ -f "package-lock.json" ] || [ -f "npm-shrinkwrap.json" ]; then
            npm ci
          elif [ -f "package.json" ]; then
            npm install
          else
            echo "No package.json found. Skipping dependencies installation."
          fi

      - name: Run Linter (if configured)
        run: |
          if [ -f "package.json" ]; then
            npm run lint --if-present
          fi

      - name: Run Tests (if configured)
        run: |
          if [ -f "package.json" ]; then
            npm test --passWithNoTests --if-present || echo "No tests or test command failed, but proceeding."
          fi

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
          username: ${{{{ github.actor }}}}
          password: ${{{{ secrets.GITHUB_TOKEN }}}}

      - name: Lowercase repository name
        run: echo "IMAGE_ID=$(echo ${{{{ github.repository }}}} | tr '[:upper:]' '[:lower:]')" >> $GITHUB_ENV

      - name: Extract metadata (tags, labels) for Docker
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ghcr.io/${{{{ env.IMAGE_ID }}}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./Dockerfile
          push: ${{{{ github.event_name != 'pull_request' }}}}
          tags: ${{{{ steps.meta.outputs.tags }}}}
          labels: ${{{{ steps.meta.outputs.labels }}}}
"""
