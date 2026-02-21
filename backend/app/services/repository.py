import os
import shutil
import stat
from git import Repo
from loguru import logger
from typing import Optional

class RepositoryService:
    def __init__(self, base_temp_dir: str = "app/temp/workspaces"):
        self.base_temp_dir = base_temp_dir
        if not os.path.exists(self.base_temp_dir):
            os.makedirs(self.base_temp_dir)
            logger.info(f"Created base temporary directory: {self.base_temp_dir}")

    def _rmtree(self, path: str):
        """
        Internal helper to handle read-only files on Windows during deletion.
        """
        def on_rm_error(func, path, exc_info):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        if os.path.exists(path):
            try:
                # onerror is for compatibility, onexc is 3.12+
                shutil.rmtree(path, onerror=on_rm_error)
            except Exception as e:
                logger.error(f"Failed to delete {path}: {e}")

    def clone_repository(self, repo_url: str, branch: str = "main", token: Optional[str] = None) -> Optional[str]:
        """
        Clones a GitHub repository to a temporary workspace.
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

            Repo.clone_from(clone_url, target_dir, branch=branch)
            logger.info(f"Successfully cloned {repo_url}")
            return target_dir
        except Exception as e:
            logger.error(f"Failed to clone repository {repo_url}: {e}")
            return None

    def push_changes(self, workspace_path: str, commit_message: str = "Add generated deployment files"):
        """
        Commits and pushes changes in the workspace back to the remote.
        """
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
            logger.info(f"Pushing changes to remote...")
            origin.push()
            logger.info("Successfully pushed changes to GitHub.")
            return True
        except Exception as e:
            logger.error(f"Failed to push changes: {e}")
            return False

    def cleanup_workspace(self, workspace_path: str):
        """
        Deletes the temporary workspace.
        """
        logger.info(f"Cleaning up workspace: {workspace_path}")
        self._rmtree(workspace_path)

repo_service = RepositoryService()
