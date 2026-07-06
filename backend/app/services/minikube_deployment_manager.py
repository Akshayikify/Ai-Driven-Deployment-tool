import asyncio
import os
import re
import json
import datetime
import subprocess
import socket
from typing import Optional, Dict, Any
from loguru import logger
import httpx

from app.db.mongodb import db
from app.services.task_manager import task_manager
from app.services.k8s_generator import generate_deployment_yaml, generate_service_yaml, save_yaml_files

import shutil

# ---------------------------------------------------------------------------
# Global registry of live port-forward tunnel processes.
# Key: service_name (str), Value: subprocess.Popen handle
# ---------------------------------------------------------------------------
_tunnel_processes: Dict[str, subprocess.Popen] = {}

def slugify(name: str) -> str:
    """Converts a name to a Kubernetes-compliant DNS-1123 subdomain name."""
    s = name.lower()
    s = re.sub(r'[^a-z0-9\-]', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')

def _find_executable(name: str) -> Optional[str]:
    """
    Finds all occurrences of an executable on PATH using shutil.which,
    and prefers paths that do NOT contain spaces (avoids Windows CreateProcess issues).
    Falls back to the first result if none are space-free.
    """
    # Collect all matches
    candidates = []
    found = shutil.which(name)
    if found:
        candidates.append(found)
    
    # Walk through PATH entries manually to find all candidates
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    seen = set(candidates)
    for d in path_dirs:
        for ext in ["", ".exe", ".EXE", ".cmd", ".CMD", ".bat", ".BAT"]:
            candidate = os.path.join(d, name + ext)
            if os.path.isfile(candidate) and candidate not in seen:
                candidates.append(candidate)
                seen.add(candidate)
    
    if not candidates:
        return None
    
    # Prefer executables whose full path contains no spaces
    for c in candidates:
        if " " not in c:
            return c
    
    # Fallback: return first found
    return candidates[0]


def _run_subprocess(command: list) -> tuple:
    """Runs a command synchronously using subprocess.run (thread-safe, Windows-compatible)."""
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
    )
    stdout = result.stdout.decode("utf-8", errors="ignore").strip()
    stderr = result.stderr.decode("utf-8", errors="ignore").strip()
    return result.returncode, stdout, stderr


async def run_command(command: list[str]) -> tuple:
    """
    Runs a command asynchronously using subprocess.run in a thread executor.
    Uses explicit executable path resolution and handles Windows paths with spaces.
    Returns (exit_code, stdout, stderr).
    """
    try:
        executable = _find_executable(command[0])
        if executable is None:
            raise RuntimeError(f"{command[0]} executable not found on PATH.")
        
        command = [executable] + command[1:]
        logger.info("Executing: {}", " ".join(command))
        
        # Use asyncio.to_thread so we don't block the event loop.
        # subprocess.run handles Windows paths-with-spaces correctly unlike
        # asyncio.create_subprocess_exec which can fail on such paths.
        return await asyncio.to_thread(_run_subprocess, command)
    except Exception as e:
        logger.error(f"Failed to execute command '{' '.join(command)}': {e}")
        return -1, "", str(e)

async def detect_expose_port(owner: str, repo: str, token: Optional[str] = None) -> int:
    """
    Attempts to fetch the Dockerfile from GitHub and parse the EXPOSE port.
    If it fails, searches MongoDB for the task's language configuration, and defaults to 8000.
    """
    # 1. Fetch from GitHub
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/Dockerfile"
    headers = {"Accept": "application/vnd.github.raw"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                content = resp.text
                match = re.search(r'(?i)^\s*EXPOSE\s+(\d+)', content, re.MULTILINE)
                if match:
                    port = int(match.group(1))
                    logger.info(f"Detected EXPOSE port {port} from GitHub Dockerfile.")
                    return port
    except Exception as e:
        logger.warning(f"Could not fetch or parse Dockerfile from GitHub for port detection: {e}")
        
    # 2. Fetch from MongoDB previous task language
    try:
        task = await db.db.deployments.find_one(
            {"repo_url": {"$regex": f"/{repo}(\\.git)?$", "$options": "i"}},
            sort=[("created_at", -1)]
        )
        if task and "language" in task:
            lang = task["language"]
            if lang == "Java":
                return 8080
            elif lang == "Go":
                return 8080
            elif lang == "PHP":
                return 80
            elif lang in ["JavaScript/TypeScript", "Node.js"]:
                return 3000
    except Exception as db_err:
        logger.warning(f"Database lookup for port detection failed: {db_err}")
        
    # Default fallback
    return 8000

async def delete_previous_deployment(repo_name_slug: str):
    """Deletes existing deployment and service for the repository name."""
    logger.info(f"Cleaning up previous Kubernetes deployment resources for {repo_name_slug}...")
    await run_command(["kubectl", "delete", "deployment", repo_name_slug, "--ignore-not-found=true"])
    await run_command(["kubectl", "delete", "service", f"{repo_name_slug}-service", "--ignore-not-found=true"])


GHCR_SECRET_NAME = "ghcr-pull-secret"

async def ensure_ghcr_pull_secret(token: str) -> bool:
    """
    Creates (or updates) a Kubernetes `docker-registry` secret so that Minikube
    can pull private images from ghcr.io using the user's GitHub OAuth token.

    Uses `kubectl create secret docker-registry` (the dedicated registry credential
    command) instead of `--from-literal` with raw JSON, which is fragile on Windows
    due to shell quoting of special characters in the JSON value.

    Returns True on success, False on failure.
    """
    import base64
    import json as _json
    import tempfile

    logger.info("Creating/updating GHCR image pull secret in Kubernetes cluster...")

    # Delete any existing secret first (ignore errors if not found)
    await run_command(
        ["kubectl", "delete", "secret", GHCR_SECRET_NAME, "--ignore-not-found=true"]
    )

    # Primary approach: use the dedicated docker-registry secret type.
    # kubectl handles all JSON formatting internally — no quoting issues on Windows.
    code, stdout, stderr = await run_command([
        "kubectl", "create", "secret", "docker-registry", GHCR_SECRET_NAME,
        "--docker-server=ghcr.io",
        "--docker-username=oauth2",
        f"--docker-password={token}",
        "--docker-email=ci@localhost",
    ])

    if code == 0:
        logger.info(f"GHCR pull secret '{GHCR_SECRET_NAME}' created successfully (docker-registry method).")
        return True

    # Fallback: write the dockerconfigjson to a temp file and use --from-file.
    # This avoids any command-line quoting issues entirely.
    logger.warning(f"docker-registry method failed ({stderr}), trying --from-file fallback...")
    try:
        auth_str = base64.b64encode(f"oauth2:{token}".encode()).decode()
        docker_config = {
            "auths": {
                "ghcr.io": {
                    "username": "oauth2",
                    "password": token,
                    "auth": auth_str,
                }
            }
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            _json.dump(docker_config, tmp)
            tmp_path = tmp.name

        code2, _, stderr2 = await run_command([
            "kubectl", "create", "secret", "generic", GHCR_SECRET_NAME,
            f"--from-file=.dockerconfigjson={tmp_path}",
            "--type=kubernetes.io/dockerconfigjson",
        ])

        # Clean up temp file
        try:
            os.remove(tmp_path)
        except OSError:
            pass

        if code2 == 0:
            logger.info(f"GHCR pull secret '{GHCR_SECRET_NAME}' created successfully (--from-file fallback).")
            return True

        logger.error(f"Both methods failed to create GHCR pull secret. Last error: {stderr2}")
        return False

    except Exception as exc:
        logger.error(f"Exception while creating GHCR pull secret via fallback: {exc}")
        return False


async def _get_current_rs_hash(repo_name_slug: str) -> Optional[str]:
    """
    Returns the pod-template-hash of the ReplicaSet currently owned by the
    named Deployment, or None if it cannot be determined.
    """
    code, stdout, _ = await run_command(
        ["kubectl", "get", "replicasets", "-l", f"app={repo_name_slug}", "-o", "json"]
    )
    if code != 0 or not stdout:
        return None
    try:
        data = json.loads(stdout)
        # Find the RS whose ownerReference is our deployment AND which has desired replicas > 0
        for rs in data.get("items", []):
            desired = rs.get("spec", {}).get("replicas", 0)
            owners = rs.get("metadata", {}).get("ownerReferences", [])
            is_owned_by_deployment = any(
                o.get("kind") == "Deployment" and o.get("name") == repo_name_slug
                for o in owners
            )
            if is_owned_by_deployment and desired > 0:
                labels = rs.get("metadata", {}).get("labels", {})
                return labels.get("pod-template-hash")
    except Exception:
        pass
    return None


async def wait_for_pods(repo_name_slug: str, timeout: int = 300) -> Dict[str, Any]:
    """
    Health check loop that polls kubectl get pods.
    Only watches pods owned by the *current* deployment's ReplicaSet so that
    stale pods from previous (failed) deployments don't cause a false failure.
    Waits until the pod status is 'Running' and handles crash/pull errors.
    """
    start_time = datetime.datetime.now()
    logger.info(f"Starting health check loop for {repo_name_slug} (timeout={timeout}s)...")

    # Resolve the current ReplicaSet's pod-template-hash so we only watch
    # pods belonging to the newly applied deployment — not stale leftover pods.
    current_rs_hash: Optional[str] = None
    for _ in range(5):          # up to 5 attempts with a short back-off
        current_rs_hash = await _get_current_rs_hash(repo_name_slug)
        if current_rs_hash:
            logger.info(f"Resolved current RS hash for {repo_name_slug}: {current_rs_hash}")
            break
        await asyncio.sleep(2)

    if not current_rs_hash:
        logger.warning(
            f"Could not resolve RS hash for {repo_name_slug} — will watch ALL pods "
            f"(may include stale pods from previous deployments)."
        )

    # Track consecutive image-pull failures before declaring them fatal.
    # A single occurrence can be transient (the runtime is still trying).
    pull_error_streak: Dict[str, int] = {}
    PULL_ERROR_THRESHOLD = 3   # fail only after N consecutive polls showing the same error

    while (datetime.datetime.now() - start_time).total_seconds() < timeout:
        # Build label selector: prefer the RS-specific hash so we skip stale pods
        if current_rs_hash:
            label_selector = f"app={repo_name_slug},pod-template-hash={current_rs_hash}"
        else:
            label_selector = f"app={repo_name_slug}"

        code, stdout, stderr = await run_command(
            ["kubectl", "get", "pods", "-l", label_selector, "-o", "json"]
        )
        if code != 0 or not stdout:
            await asyncio.sleep(2)
            continue

        try:
            data = json.loads(stdout)
            items = data.get("items", [])
            if not items:
                await asyncio.sleep(2)
                continue

            for pod in items:
                pod_name = pod["metadata"]["name"]
                status_phase = pod.get("status", {}).get("phase", "Unknown")

                logger.info(f"Pod {pod_name} status: {status_phase}")

                # Inspect container statuses for waiting reasons
                container_statuses = pod.get("status", {}).get("containerStatuses") or []
                for cs in container_statuses:
                    state = cs.get("state", {})
                    waiting = state.get("waiting", {})
                    if waiting:
                        reason = waiting.get("reason", "")
                        logger.warning(f"Pod {pod_name} container state waiting reason: {reason}")

                        if reason in ["CrashLoopBackOff", "ImagePullBackOff", "ErrImagePull", "CreateContainerConfigError"]:
                            # Only fail after consecutive occurrences — transient on first pull attempt
                            pull_error_streak[pod_name] = pull_error_streak.get(pod_name, 0) + 1
                            if pull_error_streak[pod_name] >= PULL_ERROR_THRESHOLD:
                                # --- Fetch crash logs BEFORE returning ---
                                crash_logs = ""
                                if reason == "CrashLoopBackOff":
                                    logger.info(f"[Crash Diagnostics] Fetching crash logs for pod {pod_name}...")
                                    # Try --previous first (logs from the last crashed container)
                                    log_code, log_out, _ = await run_command(
                                        ["kubectl", "logs", pod_name, "--previous", "--tail=80"]
                                    )
                                    if log_code != 0 or not log_out:
                                        # Fallback: current container logs (may still have useful output)
                                        log_code, log_out, _ = await run_command(
                                            ["kubectl", "logs", pod_name, "--tail=80"]
                                        )
                                    crash_logs = log_out.strip() if log_out else "(no logs available)"
                                    logger.error(
                                        f"[Crash Diagnostics] 🔴 Pod {pod_name} crash logs:\n"
                                        f"{'='*60}\n{crash_logs}\n{'='*60}"
                                    )

                                error_detail = f"Pod container failed to start: {reason}"
                                if crash_logs:
                                    error_detail += f"\n\nCrash Logs:\n{crash_logs}"

                                return {
                                    "status": "failed",
                                    "pod_name": pod_name,
                                    "deployment_status": reason,
                                    "error": error_detail,
                                    "crash_logs": crash_logs,
                                }
                        else:
                            pull_error_streak.pop(pod_name, None)

                if status_phase == "Running":
                    # Ensure the container is actually ready
                    if container_statuses and container_statuses[0].get("ready"):
                        return {
                            "status": "success",
                            "pod_name": pod_name,
                            "deployment_status": "Running",
                        }
                elif status_phase == "Failed":
                    return {
                        "status": "failed",
                        "pod_name": pod_name,
                        "deployment_status": status_phase,
                        "error": f"Pod entered failure state: {status_phase}",
                    }

        except Exception as e:
            logger.error(f"Error parsing pod JSON output: {e}")

        await asyncio.sleep(3)

    return {
        "status": "timeout",
        "pod_name": "N/A",
        "deployment_status": "Timeout",
        "error": "Pod failed to reach running status within 300 seconds",
    }


def _find_free_port() -> int:
    """Finds a free local TCP port by binding to port 0 and releasing it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def _kill_tunnel(service_name: str):
    """Terminates any existing port-forward tunnel for the given service."""
    proc = _tunnel_processes.pop(service_name, None)
    if proc and proc.poll() is None:
        try:
            proc.terminate()
            proc.wait(timeout=5)
            logger.info(f"Terminated existing tunnel for {service_name}.")
        except Exception as e:
            logger.warning(f"Could not cleanly terminate tunnel for {service_name}: {e}")


async def get_application_url(repo_name_slug: str) -> Optional[str]:
    """
    Creates a persistent `kubectl port-forward` tunnel to the Minikube service
    and returns a stable `http://127.0.0.1:<port>` URL.

    Unlike `minikube service --url` (which exits immediately on the Docker driver
    and kills the tunnel), `kubectl port-forward` runs as a long-lived background
    process — keeping the URL alive for as long as the backend server is running.
    """
    service_name = f"{repo_name_slug}-service"
    logger.info(f"Setting up persistent port-forward tunnel for service: {service_name}...")

    # Resolve kubectl executable path
    kubectl = _find_executable("kubectl")
    if not kubectl:
        logger.error("kubectl not found — cannot set up port-forward tunnel.")
        return None

    # --- Determine the NodePort exposed by the service ---
    code, svc_json, _ = await run_command(
        ["kubectl", "get", "service", service_name, "-o", "json"]
    )
    if code != 0 or not svc_json:
        logger.error(f"Could not fetch service JSON for {service_name}.")
        return None

    try:
        svc_data = json.loads(svc_json)
        ports = svc_data.get("spec", {}).get("ports", [])
        if not ports:
            logger.error(f"No ports defined on service {service_name}.")
            return None
        target_port = ports[0].get("port", 80)   # use the service's cluster port
    except Exception as e:
        logger.error(f"Failed to parse service JSON: {e}")
        return None

    # --- Kill any previous tunnel for this service ---
    _kill_tunnel(service_name)

    # --- Pick a free local port and start the tunnel ---
    local_port = _find_free_port()
    cmd = [kubectl, "port-forward",
           f"service/{service_name}",
           f"{local_port}:{target_port}",
           "--address=127.0.0.1"]

    logger.info(f"Starting kubectl port-forward: {' '.join(cmd)}")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _tunnel_processes[service_name] = proc
    except Exception as e:
        logger.error(f"Failed to start port-forward process: {e}")
        return None

    # --- Wait briefly for the tunnel to become ready ---
    deadline = asyncio.get_event_loop().time() + 15   # up to 15 s
    url = f"http://127.0.0.1:{local_port}"
    while asyncio.get_event_loop().time() < deadline:
        # Check if the process died early
        if proc.poll() is not None:
            stderr_out = proc.stderr.read().decode("utf-8", errors="ignore") if proc.stderr else ""
            logger.error(f"port-forward process exited unexpectedly: {stderr_out}")
            return None
        # Try connecting to the tunnel
        try:
            with socket.create_connection(("127.0.0.1", local_port), timeout=1):
                logger.info(f"Tunnel is live at {url}")
                return url
        except (ConnectionRefusedError, OSError):
            pass
        await asyncio.sleep(0.5)

    # Timeout — kill the process and give up
    logger.error(f"Timed out waiting for port-forward tunnel to become ready on port {local_port}.")
    _kill_tunnel(service_name)
    return None

async def deploy_to_minikube(task_id: str, repo_name: str, ghcr_image: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Main deployment orchestrator workflow.
    """
    logger.info(f"Starting Minikube deployment workflow for task {task_id}...")
    
    # Check if kubectl is available
    try:
        k_code, _, _ = await run_command(["kubectl", "version", "--client"])
        if k_code != 0:
            raise RuntimeError("kubectl returned a non-zero exit code")
    except Exception as err:
        err_msg = f"kubectl is unavailable on this system: {err}"
        logger.error(err_msg)
        task_manager.update_task(task_id, "failed", message=err_msg)
        return {"deployment_status": "failed", "error": err_msg}
        
    # Check if minikube is running and healthy
    try:
        m_code, m_status, _ = await run_command(["minikube", "status"])
        status = m_status.lower()
        if (
            "host: running" not in status or
            "kubelet: running" not in status or
            "apiserver: running" not in status
        ):
            raise Exception("Minikube is not healthy or running.")
    except Exception as err:
        err_msg = f"Minikube cluster is not running or healthy: {err}"
        logger.error(err_msg)
        task_manager.update_task(task_id, "failed", message=err_msg)
        return {"deployment_status": "failed", "error": err_msg}

    repo_name_slug = slugify(repo_name)
    
    # 0. Update state
    task_manager.update_task(task_id, "deploying_to_minikube")
    
    # Detect port
    # Extract owner and repo from image URL if possible
    # e.g., ghcr.io/owner/repo:latest
    owner = "Unknown"
    repo = repo_name
    match = re.search(r'ghcr\.io/([^/]+)/([^:]+)', ghcr_image)
    if match:
        owner = match.group(1)
        repo = match.group(2).split("/")[-1] # Handle nested service paths
        
    port = await detect_expose_port(owner, repo, token)
    
    try:
        # Delete previous deployment
        await delete_previous_deployment(repo_name_slug)

        # 0a. Ensure GHCR pull secret exists so Minikube can pull private images
        pull_secret_name = None
        if token:
            secret_ok = await ensure_ghcr_pull_secret(token)
            if secret_ok:
                pull_secret_name = GHCR_SECRET_NAME
            else:
                logger.warning("Could not create GHCR pull secret — image pull may fail if the registry is private.")
        else:
            logger.warning("No GitHub token available — skipping GHCR pull secret creation. Image pull may fail for private registries.")

        # 0b. Pre-load image into Minikube via host Docker daemon.
        # The host Docker Desktop may have GHCR credentials (from `docker login ghcr.io`)
        # while Minikube's internal runtime does not. By pulling on the host and loading
        # directly into Minikube, we sidestep GHCR auth inside Minikube entirely.
        image_pull_policy = "Always"   # default: pull from registry
        image_loaded = False

        logger.info(f"Attempting to pre-load {ghcr_image} into Minikube via host Docker...")
        # Step 1: pull on host using Docker
        pull_code, _, pull_err = await run_command(["docker", "pull", ghcr_image])
        if pull_code == 0:
            # Step 2: load into Minikube
            load_code, _, load_err = await run_command(["minikube", "image", "load", ghcr_image])
            if load_code == 0:
                image_loaded = True
                image_pull_policy = "IfNotPresent"   # use the pre-loaded image
                logger.info(f"Image {ghcr_image} pre-loaded into Minikube successfully. Using IfNotPresent pull policy.")
            else:
                logger.warning(f"minikube image load failed ({load_err}), will rely on imagePullSecret instead.")
        else:
            logger.warning(f"docker pull failed on host ({pull_err}), will rely on imagePullSecret inside Minikube.")

        # 1. Generate manifests
        task_manager.update_task(task_id, "creating_deployment")
        deployment_content = generate_deployment_yaml(
            repo_name_slug, ghcr_image, port,
            pull_secret_name=pull_secret_name,
            image_pull_policy=image_pull_policy,
        )
        
        task_manager.update_task(task_id, "creating_service")
        service_content = generate_service_yaml(repo_name_slug, port)
        
        # Save manifests
        temp_dir = os.path.abspath(os.path.join(os.getcwd(), "app", "temp", "k8s", repo_name_slug))
        paths = save_yaml_files(repo_name_slug, deployment_content, service_content, temp_dir)
        
        # 2. Apply manifests
        logger.info(f"Applying deployment manifest to Minikube...")
        dep_code, _, dep_err = await run_command(["kubectl", "apply", "-f", paths["deployment_path"]])
        if dep_code != 0:
            raise Exception(f"Failed to apply deployment manifest: {dep_err}")
            
        logger.info(f"Applying service manifest to Minikube...")
        svc_code, _, svc_err = await run_command(["kubectl", "apply", "-f", paths["service_path"]])
        if svc_code != 0:
            raise Exception(f"Failed to apply service manifest: {svc_err}")

            
        # 3. Wait for pods to be Running
        task_manager.update_task(task_id, "waiting_for_pods")
        status_res = await wait_for_pods(repo_name_slug, timeout=300)
        
        if status_res["status"] != "success":
            raise Exception(status_res.get("error", "Failed waiting for pods"))
            
        pod_name = status_res["pod_name"]
        
        # 4. Retrieve application URL
        app_url = await get_application_url(repo_name_slug)
        if not app_url:
            raise Exception("Failed to retrieve service NodePort URL from Minikube")
            
        # 5. Store deployment metadata in MongoDB
        logger.info("Storing Minikube deployment metadata in MongoDB...")
        meta_doc = {
            "task_id": task_id,
            "repo_name": repo_name,
            "ghcr_image": ghcr_image,
            "pod_name": pod_name,
            "deployment_status": "Running",
            "deployment_url": app_url,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        await db.db.deployments.update_one(
            {"task_id": task_id},
            {"$set": meta_doc},
            upsert=True
        )
        
        # 6. Update task in manager to complete
        task_manager.update_task(task_id, "application_live", deployment_url=app_url)
        logger.info(f"Minikube deployment completed successfully! App Live: {app_url}")
        
        return {
            "deployment_status": "success",
            "pod_name": pod_name,
            "application_url": app_url
        }
        
    except Exception as err:
        logger.error(f"Minikube deployment failed: {err}")
        task_manager.update_task(task_id, "failed", message=str(err))
        return {
            "deployment_status": "failed",
            "error": str(err)
        }

async def deploy_to_minikube_bg(task_id: str, repo_name: str, ghcr_image: str, token: Optional[str] = None):
    """Background wrapper task to deploy without blocking."""
    await deploy_to_minikube(task_id, repo_name, ghcr_image, token)

