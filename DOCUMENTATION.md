# Auto-Deployment Tool: Architecture & Documentation

## 1. Project Overview
The **Auto-Deployment Tool** is an AI-driven SaaS platform that fully automates the analysis, configuration, and deployment preparation of software repositories. By simply providing a GitHub URL, the AI agent dynamically clones the repository, deeply analyzes the programming language and framework, generates optimized build environments (`Dockerfile`), continuous integration workflows (`.github/workflows/deploy.yml`), and securely pushes the configurations back to the repository using delegated OAuth access.

---

## 2. Global Architecture & Project Structure
The project structure follows a decoupled Client-Server model.

```
Ai-Driven-Deployment-tool/
├── frontend/             # React (Vite, TypeScript, TailwindCSS)
│   ├── client/           # Application Source Code
│   │   ├── components/   # UI Components (AIAgent, Timeline, LogMonitor)
│   │   ├── pages/        # Dashboard, Login, Workflow pages
│   │   └── context/      # React Providers (DeploymentContext)
│   └── tailwind.config.ts # Styling definitions
├── backend/              # Python (FastAPI, Uvicorn)
│   ├── app/
│   │   ├── api/          # RESTful Endpoints (Analyze, Chat, Logs)
│   │   ├── core/         # Settings & Environment Variables
│   │   ├── services/     # Business Logic (Analysis, Generators, AI, GitHub)
│   │   └── temp/         # Ephemeral cloning workspace 
│   ├── requirements.txt
│   └── .env              # Backend configuration
```

---

## 3. Core Features & Workflow

### 3.1 Secure OAuth Authentication (Clerk Integration)
- **Frontend Identity:** The application uses **Clerk** for robust session management. Users log in securely via GitHub OAuth.
- **Scope Delegation:** The Clerk application is configured to request the `repo` scope, ensuring the automated agent has write-access solely to edit and push deployment configurations on behalf of the user.
- **Backend Token Handshake:** When the user initiates a deploy, the frontend securely passes the `userId` to the FastAPI backend. The backend strictly communicates server-to-server with Clerk APIs using a `CLERK_SECRET_KEY` to securely retrieve the user's delegated GitHub Token, completely preventing sensitive OAuth tokens from ever hitting the browser client.

### 3.2 Deep Repository Analysis (`AnalysisEngine`)
- **Heuristics & Signatures:** When a repository is cloned ephemerally, the `analysis.py` service recursively scans the entire directory tree.
- **Framework Detection:** It identifies languages and frameworks by indexing top-level dependency files (`package.json`, `requirements.txt`, `composer.json`, `go.mod`) and deeply inspecting specific imports (e.g., `react`, `flask`, `express`).
- **Confidence Scoring:** Determines mathematical confidence (`0.0 - 1.0`) depending on the quality of signatures matched.

### 3.3 Dynamic Deployment Asset Generation (`FileGenerator`)
- Based on the `AnalysisEngine`'s results, the generator orchestrates standard deployment packages.
- **Hardcoded Templates:** Highly optimized Docker templates are instantly applied for recognized environments (`Node.js`, `Python`, `PHP`).
- **CI/CD Creation:** Generates language-specific GitHub Actions pipelines (`.github/workflows/deploy.yml`) that automatically test the code and publish built Docker images directly to the **GitHub Container Registry (GHCR)**.
- **Environment Discovery:** Automatically discovers variables injected via code parsing and generates `.env.example` boilerplates.

### 3.4 Live GitHub Actions Monitoring (`GitHubActionsService`)
- Once the CI/CD pipeline is pushed to the user's remote repository, the backend initiates an asynchronous polling service (`github_actions.py`).
- **Jobs API Integration:** It continuously polls the GitHub REST API using the user's delegated OAuth token to fetch live job step states.
- **Real-Time Log Ingestion:** As each deployment step (e.g., *Install dependencies*, *Run Tests*, *Build image*) begins, completes, or fails, the status is dynamically formatted and multiplexed natively into the frontend's Server-Sent Events (SSE) Live Log UI, keeping the user engaged without ever leaving the dashboard.

### 3.4 Generalized Language Deployment (LLM Fallback)
- **Universal Support:** If a user submits a repository written in a language outside the standardized templates (e.g., Rust, Java, C#, Ruby), the generator routes to the `LLMDockerTemplate`.
- **LLM Orchestration:** `ai_service.py` connects to Google Gemini (or OpenRouter) via backend integration. It seamlessly prompts the AI with the full recursive map of the user's project structure, dynamically requesting a bespoke, production-ready `Dockerfile` specifically engineered and optimized for that unique architectural state.

### 3.5 Assistant & Progress Tracking UI
- **AI Agent Chat:** A conversational assistant interfaced via `react-markdown` that streams real-time responses about DevOps, the deployment platform, or specific analysis diagnostics.
- **Task Manager & Timeline:** The backend exposes a background task registry. The frontend dashboard automatically polls `task_id` endpoints to visually update the Deployment Timeline (Cloning -> Analyzing -> Generating -> Pushing) simultaneously.

---

## 4. Current State & Next Steps
- **Phase 1 (UI/UX):** Complete.
- **Phase 2 (Analysis & Generation):** Complete, including LLM fallback generation.
- **Phase 3 (Clerk OAuth):** Complete, securing cross-platform secrets.
- **Phase 4 (Generalized LLM Fallback):** Complete.
- **Phase 5 (CI/CD Pipeline Automation):** Complete. The backend now writes fully customized testing, linting, and Docker building GitHub Actions pipelines that automatically push to the GitHub Container Registry.
- **Phase 6 (Live GitHub Actions Monitoring):** Complete. Real-time CI/CD step statuses are streamed directly into the dashboard logs via REST API polling.
- **Phase 7 (Container Orchestration Strategy):** Pending. Exploring options to automatically run or host the uploaded GHCR packages natively or via external providers.
