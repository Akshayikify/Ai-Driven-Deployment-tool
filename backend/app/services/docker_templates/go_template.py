from .base import DockerTemplate
from typing import Dict, Any
import os

class GoDockerTemplate(DockerTemplate):
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        """
        Generates an optimized multi-stage Dockerfile for Go projects.
        Uses a lightweight alpine image for the final runtime.
        """
        entry_point = findings.get("entry_point", "main.go")
        # Extract binary name from project name or entry point
        name = findings.get("name", "app").lower()
        
        return f"""# Build Stage
FROM golang:1.21-alpine AS builder
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache git

# Handle modules
COPY go.mod go.sum* ./
RUN go mod download

# Build the application
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server {entry_point}

# Final Stage
FROM alpine:latest
WORKDIR /app
RUN apk add --no-cache ca-certificates tzdata

# Copy binary from builder
COPY --from=builder /app/server ./server

# Create non-root user
RUN adduser -D -g '' appuser
USER appuser

EXPOSE 8080
CMD ["./server"]
"""

    def generate_dockerignore(self, findings: Dict[str, Any]) -> str:
        return """
.git
.github
vendor/
bin/
*.exe
*.test
*.out
Dockerfile
.dockerignore
"""

    def generate_cicd_workflow(self, findings: Dict[str, Any]) -> str:
        """Generates a Go-specific CI/CD pipeline."""
        workdir = findings.get("path", ".")
        clean_workdir = workdir.strip("./")
        
        return f"""name: Go CI/CD Pipeline

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

      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
          cache: true

      - name: Run tests
        working-directory: ./{clean_workdir}
        run: go test -v ./...

  build-and-push:
    needs: test
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
