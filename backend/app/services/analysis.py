import os
import json
from loguru import logger
from typing import Dict, Any

class AnalysisEngine:
    def analyze_directory(self, workspace_path: str) -> Dict[str, Any]:
        """
        Analyzes the directory to detect language and framework.
        """
        logger.info(f"Analyzing workspace: {workspace_path}")
        findings = {
            "language": "Unknown",
            "framework": "Unknown",
            "detected_files": [],
            "dependencies": []
        }

        file_list = []
        for root, dirs, files in os.walk(workspace_path):
            # Only look at top 2 levels for framework signals to keep it snappy
            depth = root[len(workspace_path):].count(os.sep)
            if depth > 2: continue
            for f in files:
                file_list.append(f)

        # 1. Check for Node.js
        if "package.json" in file_list:
            findings["language"] = "JavaScript/TypeScript"
            findings["detected_files"].append("package.json")
            try:
                pkg_path = os.path.join(workspace_path, "package.json")
                with open(pkg_path, "r") as f:
                    pkg_data = json.load(f)
                    deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                    findings["dependencies"] = list(deps.keys())
                    
                    if "next" in deps: findings["framework"] = "Next.js"
                    elif "react" in deps: findings["framework"] = "React"
                    elif "vite" in deps: findings["framework"] = "Vite"
                    elif "express" in deps: findings["framework"] = "Express"
                    else: findings["framework"] = "Node.js (Generic)"
            except Exception as e:
                logger.error(f"Error parsing package.json: {e}")

        # 2. Check for Python
        elif "requirements.txt" in file_list or "pyproject.toml" in file_list or "setup.py" in file_list:
            findings["language"] = "Python"
            if "requirements.txt" in file_list:
                findings["detected_files"].append("requirements.txt")
                with open(os.path.join(workspace_path, "requirements.txt"), "r") as f:
                    deps = f.read().lower()
                    if "fastapi" in deps: findings["framework"] = "FastAPI"
                    elif "django" in deps: findings["framework"] = "Django"
                    elif "flask" in deps: findings["framework"] = "Flask"
                    else: findings["framework"] = "Python (Generic)"
            elif "pyproject.toml" in file_list:
                findings["detected_files"].append("pyproject.toml")
                findings["framework"] = "Python (Poetry/Modern)"
            else:
                findings["detected_files"].append("setup.py")
                findings["framework"] = "Python (Setuptools)"

        # 3. Check for Go
        elif "go.mod" in file_list:
            findings["language"] = "Go"
            findings["detected_files"].append("go.mod")
            findings["framework"] = "Go (Modules)"

        # 4. Final Fallback / Signals
        if "Dockerfile" in file_list:
            findings["detected_files"].append("Dockerfile")
            if findings["framework"] == "Unknown":
                findings["framework"] = "Existing Container"

        logger.info(f"Analysis complete: {findings['language']} / {findings['framework']}")
        return findings

analysis_engine = AnalysisEngine()
