import os
import shutil
import stat
from git import Repo
from loguru import logger
from typing import Optional

import tempfile

from urllib.parse import urlparse

class RepositoryService:
    def __init__(self, base_temp_dir: Optional[str] = None):
        if not base_temp_dir:
            base_temp_dir = os.environ.get("TEMP_WORKSPACES_DIR") or os.path.join(tempfile.gettempdir(), "auto_deploy_workspaces")
        self.base_temp_dir = os.path.abspath(base_temp_dir)
        if not os.path.exists(self.base_temp_dir):
            os.makedirs(self.base_temp_dir, exist_ok=True)
            logger.info(f"Created base temporary directory: {self.base_temp_dir}")

    def _resolve_host(self, host: str) -> Optional[str]:
        """
        Resolves hostname using Public DNS (8.8.8.8, 1.1.1.1) to avoid local ISP DNS failures.
        """
        try:
            import dns.resolver
            res = dns.resolver.Resolver()
            res.nameservers = ['8.8.8.8', '1.1.1.1']
            res.timeout = 2.0
            res.lifetime = 2.0
            answers = res.resolve(host, 'A')
            if answers:
                return str(answers[0])
        except Exception as e:
            logger.debug(f"Custom DNS resolve failed for {host}: {e}")
        try:
            import socket
            return socket.gethostbyname(host)
        except Exception as e:
            logger.debug(f"System DNS resolve failed for {host}: {e}")

        # Fallback for github.com if local DNS is completely unavailable
        if host.lower() == "github.com":
            return "20.207.73.82"
        return None

    def _rmtree(self, path: str, retries: int = 5):
        """
        Internal helper to handle read-only files on Windows during deletion.
        """
        import time
        import gc
        def on_rm_error(func, path, exc_info):
            os.chmod(path, stat.S_IWRITE)
            try:
                func(path)
            except Exception as e:
                logger.debug(f"on_rm_error failed for {path}: {e}")

        if os.path.exists(path):
            # Force garbage collection to release any dangling file handles
            gc.collect()
            
            for i in range(retries):
                try:
                    # onerror is for compatibility, onexc is 3.12+
                    shutil.rmtree(path, onerror=on_rm_error)
                    return
                except Exception as e:
                    if i < retries - 1:
                        # On Windows, sometimes handles are released slowly
                        logger.warning(f"Retry {i+1} deleting {path} due to error: {e}")
                        time.sleep(0.5 * (i + 1)) # Increasing backoff
                        gc.collect()
                    else:
                        logger.error(f"Failed to delete {path} after {retries} attempts: {e}")

    def clone_repository(self, repo_url: str, branch: str = "main", token: Optional[str] = None) -> Optional[str]:
        """
        Clones a GitHub repository to a temporary workspace with DNS fallback.
        """
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        target_dir = os.path.join(self.base_temp_dir, repo_name)

        if os.path.exists(target_dir):
            logger.info(f"Directory {target_dir} already exists. Cleaning up...")
            self._rmtree(target_dir)

        try:
            # Inject token if provided
            clone_url = repo_url
            if token:
                if "https://" in repo_url:
                    clone_url = repo_url.replace("https://", f"https://{token}@")
                logger.info(f"Cloning {repo_url} with authentication...")
            else:
                logger.info(f"Cloning {repo_url} (branch: {branch}) into {target_dir}...")

            # Extract host for DNS fallback resolution
            parsed = urlparse(repo_url)
            host = parsed.hostname or "github.com"
            resolved_ip = self._resolve_host(host)

            clone_kwargs = {"branch": branch}
            if resolved_ip:
                clone_kwargs["c"] = f"http.curloptResolve={host}:443:{resolved_ip}"
                clone_kwargs["allow_unsafe_options"] = True
                logger.info(f"Configured git clone with curloptResolve={host}:443:{resolved_ip}")

            repo = Repo.clone_from(clone_url, target_dir, **clone_kwargs)

            # Persist curloptResolve in local repo config for subsequent operations
            if resolved_ip:
                try:
                    with repo.config_writer() as cw:
                        cw.set_value("http", "curloptResolve", f"{host}:443:{resolved_ip}")
                except Exception as cw_err:
                    logger.debug(f"Failed to persist curloptResolve in local config: {cw_err}")

            repo.close()  # Close the handle immediately after cloning
            logger.info(f"Successfully cloned {repo_url}")
            return target_dir
        except Exception as e:
            logger.error(f"Failed to clone repository {repo_url}: {e}")
            return None

    def push_changes(self, workspace_path: str, commit_message: str = "Add generated deployment files"):
        """
        Commits and pushes changes in the workspace back to the remote.
        """
        repo = None
        try:
            repo = Repo(workspace_path)
            # Add all new/modified files
            repo.git.add(A=True)
            
            # Check if there are changes to commit
            if not repo.index.diff("HEAD"):
                logger.info("No changes to push.")
                return True

            repo.index.commit(commit_message)
            origin = repo.remote(name='origin')

            # Ensure curloptResolve is configured on repo if needed
            try:
                origin_url = origin.url
                host = urlparse(origin_url).hostname or "github.com"
                resolved_ip = self._resolve_host(host)
                if resolved_ip:
                    with repo.config_writer() as cw:
                        cw.set_value("http", "curloptResolve", f"{host}:443:{resolved_ip}")
            except Exception as res_err:
                logger.debug(f"Could not update curloptResolve before push: {res_err}")

            logger.info(f"Pushing changes to remote...")
            origin.push()
            logger.info("Successfully pushed changes to GitHub.")
            return True
        except Exception as e:
            logger.error(f"Failed to push changes: {e}")
            return False
        finally:
            if repo:
                repo.close()

    def cleanup_workspace(self, workspace_path: str):
        """
        Deletes the temporary workspace.
        """
        logger.info(f"Cleaning up workspace: {workspace_path}")
        self._rmtree(workspace_path)

repo_service = RepositoryService()
