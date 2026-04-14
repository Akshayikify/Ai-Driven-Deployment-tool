from .base import DockerTemplate
from typing import Dict, Any
import os

class RustDockerTemplate(DockerTemplate):
    def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        """
        Generates a high-performance multi-stage Dockerfile for Rust projects.
        Uses cargo-chef for dependency caching if possible, or standard build patterns.
        """
        name = findings.get("name", "app")
        
        return f"""# Stage 1: Planning
FROM lukemathwalker/cargo-chef:latest-rust-1.75-bookworm AS planner
WORKDIR /app
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

# Stage 2: Caching
FROM lukemathwalker/cargo-chef:latest-rust-1.75-bookworm AS cacher
WORKDIR /app
COPY --from=planner /app/recipe.json recipe.json
RUN cargo chef cook --release --recipe-path recipe.json

# Stage 3: Builder
FROM rust:1.75-bookworm AS builder
WORKDIR /app
COPY . .
# Copy dependencies from cacher
COPY --from=cacher /app/target target
COPY --from=cacher /usr/local/cargo /usr/local/cargo
RUN cargo build --release

# Stage 4: Runtime
FROM debian:bookworm-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/{name} ./{name}

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

ENV APP_NAME={name}
CMD ["./{name}"]
"""

    def generate_dockerignore(self, findings: Dict[str, Any]) -> str:
        return """
target/
**/*.rs.bk
.git
.github
Dockerfile
.dockerignore
"""

    def generate_cicd_workflow(self, findings: Dict[str, Any]) -> str:
        """Generates a Rust-optimized CI/CD pipeline."""
        workdir = findings.get("path", ".")
        clean_workdir = workdir.strip("./")
        
        return f"""name: Rust CI/CD Pipeline

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

      - name: Set up Rust
        uses: actions-rs/toolchain@v1
        with:
          profile: minimal
          toolchain: stable
          override: true

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{{{ runner.os }}}}-cargo-${{{{ hashFiles('**/Cargo.lock') }}}}

      - name: Run tests
        working-directory: ./{clean_workdir}
        run: cargo test --verbose

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
