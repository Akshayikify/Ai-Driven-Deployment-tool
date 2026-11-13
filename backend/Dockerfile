# =============================================================================
# AutoDeploy.ai Backend — Production Dockerfile
# Base  : python:3.11-slim  (Debian Bookworm slim; ~130 MB compressed)
# Entry : app.main:app  (FastAPI / Uvicorn)
# Port  : 8000 (configurable via PORT env var)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1 – dependency builder
#   Installs Python packages into /install so the final image stays lean.
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /install

# System build deps only: gcc + libffi for cryptography (python-jose/passlib)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        libssl-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer-cache efficiency
COPY requirements.txt .

# Install into a prefix directory so we can COPY just the site-packages
RUN pip install --upgrade pip \
    && pip install --prefix=/install/pkg --no-cache-dir -r requirements.txt


# -----------------------------------------------------------------------------
# Stage 2 – runtime image
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Metadata
LABEL org.opencontainers.image.title="autodeploy-backend" \
      org.opencontainers.image.description="AutoDeploy.ai FastAPI backend" \
      org.opencontainers.image.source="https://github.com/Akshayikify/Ai-Driven-Deployment-tool"

# Runtime system deps:
#   git  — GitPython shells out to the git binary at runtime
#   curl — optional healthcheck helper
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install/pkg /usr/local

# Create non-root user for security
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --home /home/appuser appuser

WORKDIR /app

# Copy application source (excluding everything in .dockerignore)
COPY app/ ./app/

# Create the temp workspace and k8s generation directories.
# GitPython clones repos and k8s files are generated here; must be writable by appuser.
RUN mkdir -p /tmp/auto_deploy_workspaces /tmp/auto_deploy_k8s \
    && chown -R appuser:appgroup /tmp/auto_deploy_workspaces /tmp/auto_deploy_k8s \
    && chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# ── Environment variable NAMES (values supplied at runtime via --env-file) ───
# MONGO_URI               — MongoDB Atlas connection string (required)
# MONGO_DB_NAME           — Database name (default: ai_deployment_tool)
# GOOGLE_API_KEY          — Google Gemini API key
# GEMINI_MODEL            — Gemini model name (default: gemini-flash-latest)
# OPENROUTER_API_KEY      — OpenRouter API key
# OPENROUTER_MODEL        — OpenRouter model name (default: google/gemini-2.5-flash)
# GROQ_API_KEY            — Groq API key (optional; primary if set)
# CLERK_SECRET_KEY        — Clerk secret key (fetches GitHub OAuth tokens)
# CORS_ORIGINS            — Comma-separated allowed origins
# JWT_SECRET_KEY          — JWT signing key (replace default before production)
# ADMIN_USERNAME          — Admin username  (default: admin)
# ADMIN_PASSWORD          — Admin password  (change before production)
# DEBUG                   — false in production
# PORT                    — Uvicorn port (default: 8000)
# TEMP_WORKSPACES_DIR     — Override clone workspace dir (default: /tmp/auto_deploy_workspaces)
# TEMP_K8S_DIR            — Override k8s manifests dir (default: /tmp/auto_deploy_k8s)

ENV PORT=8000 \
    TEMP_WORKSPACES_DIR=/tmp/auto_deploy_workspaces \
    TEMP_K8S_DIR=/tmp/auto_deploy_k8s \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Healthcheck — hits the /health endpoint every 30 s
# start-period is set to 30s to allow Python module loading and MongoDB ping lifespan check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Production startup — no --reload, workers scaled to 1 for K3s pod-per-replica
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1 --log-level info"]

