# AutoDeployment Tool - Intelligent AI-Driven Deployment Platform

[![Frontend: React](https://img.shields.io/badge/Frontend-React%2018-blue?logo=react)](https://reactjs.org/)
[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Auth: Clerk](https://img.shields.io/badge/Auth-Clerk-6C47FF?logo=clerk)](https://clerk.com/)
[![Database: MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248?logo=mongodb)](https://www.mongodb.com/)

**AutoDeploy.ai** is a state-of-the-art, AI-powered SaaS platform that automates the entire DevOps lifecycle. From the moment you provide a GitHub URL, our intelligent agents analyze your code, generate production-ready Docker configurations, and orchestrate CI/CD pipelines—all without you writing a single line of YAML.

---

## ✨ Key Features

- **Deep AI Analysis**: Automatically detects frameworks (React, Flask, Express, etc.) and analyzes project structure with high-confidence heuristics.
- **Zero-Config Dockerization**: Generates optimized `Dockerfile` and `docker-compose.yml` assets tailored to your application's unique requirements.
- **Automated CI/CD Pipelines**: Injects fully-functional GitHub Actions workflows into your repository to handle testing, linting, and building.
- **Live Monitoring**: Real-time streaming of GitHub Actions logs and deployment status directly into your dashboard via Server-Sent Events (SSE).
- **LLM Fallback Engine**: If your language isn't natively supported, our integrated AI (Gemini/GPT) dynamically generates bespoke configurations for any stack (Rust, Go, Java, etc.).
- **Enterprise-Grade Security**: Secure OAuth token management via Clerk, ensuring your GitHub credentials never touch the client-side.
- **Interactive Dashboard**: A sleek, professional management console for tracking deployments, analytics, and infrastructure health.

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: [React 18](https://reactjs.org/) with [Vite](https://vitejs.dev/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Animations**: [Framer Motion](https://www.framer.com/motion/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Auth**: [Clerk](https://clerk.com/)

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Database**: [MongoDB Atlas](https://www.mongodb.com/atlas)
- **AI Integration**: Google Gemini API / OpenRouter
- **Process Management**: Uvicorn

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB Atlas Account
- Clerk Account (for Authentication)
- GitHub Personal Access Token (with `repo` scope)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (required for Minikube)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) v1.38.1+
- [kubectl](https://kubernetes.io/docs/tasks/tools/) (latest stable)

---

## 🐳 Docker & Minikube Setup (Local Kubernetes)

AutoDeploy.ai uses Minikube to deploy your containerized applications locally. Follow these steps carefully to set up a stable environment.

### Step 1: Verify Docker Desktop is Running

Open **Docker Desktop** and confirm the engine is running. Then verify in terminal:

```bash
docker ps
```

Look for a container named `minikube` (if Minikube was previously started). If Docker is running without errors, proceed to the next step.

---

### Step 2: Delete Any Corrupted Minikube Cluster

If you have an existing broken or outdated cluster, wipe it first:

```bash
minikube delete --all
```

Wait until all resources are fully deleted before continuing.

---

### Step 3: Upgrade Minikube

Open **PowerShell as Administrator** and run:

```powershell
winget upgrade Kubernetes.minikube
```

Verify the installed version:

```bash
minikube version
```

> ✅ **Recommended:** `v1.38.1` or higher

---

### Step 4: Upgrade kubectl

```powershell
winget upgrade Kubernetes.kubectl
```

Verify:

```bash
kubectl version --client
```

---

### Step 5: Restart Docker Desktop Completely

Do this properly — don't just close the window:

1. **Quit Docker Desktop** → system tray → *Quit Docker Desktop*
2. **Wait 20 seconds**
3. **Open Docker Desktop**
4. Wait until it shows: **Engine running**

---

### Step 6: Start Minikube with a Stable Kubernetes Version

```bash
minikube start --driver=docker --kubernetes-version=v1.31.0
```

> ⚠️ Use `v1.31.0` — it is mature and stable. Avoid using `latest` as it may pull untested versions.

---

### Step 7: Troubleshoot Registry Connection Issues

If you see errors like `Failing to connect to https://registry.k8s.io/`, your DNS may be the problem.

**Diagnose first:**

```bash
nslookup registry.k8s.io
```

You should receive an IP address. If it **times out**, change your DNS settings:

| Setting | Option A (Google) | Option B (Cloudflare) |
|---|---|---|
| **Preferred DNS** | `8.8.8.8` | `1.1.1.1` |
| **Alternate DNS** | `8.8.4.4` | `1.0.0.1` |

**On Windows:**
1. Open **Control Panel → Network & Internet → Network Connections**
2. Right-click your active adapter → **Properties**
3. Select **Internet Protocol Version 4 (TCP/IPv4)** → **Properties**
4. Enter the DNS values above and click **OK**

Then retry:

```bash
minikube start --driver=docker --kubernetes-version=v1.31.0
```

---

### Step 8: Verify Minikube is Healthy

After a successful start, confirm all components are running:

```bash
minikube status
```

Expected output:

```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

---

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Akshayikify/Ai-Driven-Deployment-tool.git
   cd Ai-Driven-Deployment-tool
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
   Create a `.env` file in the `backend/` directory:
   ```env
   MONGODB_URI=your_mongodb_uri
   CLERK_SECRET_KEY=your_clerk_secret_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```
   Create a `.env.local` file in the `frontend/` directory:
   ```env
   VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
   ```

4. **Run the Application**
   - **Start Backend**: `cd backend && uvicorn app.main:app --reload`
   - **Start Frontend**: `cd frontend && npm run dev`

---

## 📁 Project Structure

```text
Ai-Driven-Deployment-tool/
├── frontend/             # React Application
│   ├── client/           # Source code (Components, Pages, Hooks)
│   └── public/           # Static assets
├── backend/              # FastAPI Application
│   ├── app/
│   │   ├── api/          # RESTful endpoints
│   │   ├── services/     # Analysis, AI, and GitHub logic
│   │   └── models/       # Database schemas
│   └── requirements.txt  # Python dependencies
└── README.md             # You are here!
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

Project Link: [https://github.com/Akshayikify/Ai-Driven-Deployment-tool](https://github.com/Akshayikify/Ai-Driven-Deployment-tool)
