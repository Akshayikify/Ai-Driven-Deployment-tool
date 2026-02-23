import os
import json
from loguru import logger
from typing import Dict, Any

class AnalysisEngine:
    def analyze_directory(self, workspace_path: str) -> Dict[str, Any]:
        """
        Deeply analyzes the directory to detect language, framework, and entry points.
        """
        logger.info(f"Performing deep analysis on: {workspace_path}")
        
        file_index = {
            "all_files": [],
            "by_name": {},  # name -> list of full paths
            "by_extension": {} # .ext -> list of full paths
        }

        # 1. Recursive Indexing
        for root, _, files in os.walk(workspace_path):
            rel_root = os.path.relpath(root, workspace_path)
            if rel_root == ".":
                rel_root = ""
                
            for f in files:
                full_rel_path = os.path.join(rel_root, f)
                file_index["all_files"].append(full_rel_path)
                
                if f not in file_index["by_name"]:
                    file_index["by_name"][f] = []
                file_index["by_name"][f].append(full_rel_path)
                
                _, ext = os.path.splitext(f)
                if ext:
                    if ext not in file_index["by_extension"]:
                        file_index["by_extension"][ext] = []
                    file_index["by_extension"][ext].append(full_rel_path)

        findings = {
            "language": "Unknown",
            "framework": "Unknown",
            "entry_point": None,
            "architecture": "Standard",
            "confidence": 0.0,
            "detected_files": [],
            "dependencies": [],
            "file_index": file_index
        }

        # 2. Language & Framework Detection logic
        self._detect_node(findings, workspace_path)
        self._detect_python(findings, workspace_path)
        self._detect_go(findings, workspace_path)
        self._detect_php(findings, workspace_path)
        self._detect_ruby(findings, workspace_path)
        self._detect_swift(findings, workspace_path)
        self._detect_html(findings, workspace_path)
        
        # 3. Detect Architecture
        if "package.json" in file_index["by_name"] and ("requirements.txt" in file_index["by_name"] or "pyproject.toml" in file_index["by_name"]):
            findings["architecture"] = "Monorepo"

        # 4. Final Fallback / Signal logic
        if "Dockerfile" in file_index["by_name"]:
            findings["detected_files"].append("Dockerfile")
            if findings["framework"] == "Unknown":
                findings["framework"] = "Existing Container"
                findings["confidence"] = max(findings["confidence"], 0.5)

        logger.info(f"Deep analysis complete: {findings['language']} / {findings['framework']} (Confidence: {findings['confidence']})")
        return findings

    def _detect_node(self, findings: dict, workspace_path: str):
        file_index = findings["file_index"]
        if "package.json" in file_index["by_name"]:
            findings["language"] = "JavaScript/TypeScript"
            findings["detected_files"].append("package.json")
            findings["confidence"] += 0.4
            
            # Detect entry points
            node_entries = ["server.js", "index.js", "app.js", "main.js"]
            for entry in node_entries:
                if entry in file_index["by_name"]:
                    findings["entry_point"] = file_index["by_name"][entry][0]
                    findings["confidence"] += 0.2
                    break

            try:
                # Use the first package.json found (usually root)
                pkg_path = os.path.join(workspace_path, file_index["by_name"]["package.json"][0])
                with open(pkg_path, "r") as f:
                    pkg_data = json.load(f)
                    deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                    findings["dependencies"] = list(deps.keys())
                    
                    if "next" in deps: findings["framework"] = "Next.js"
                    elif "react" in deps: findings["framework"] = "React"
                    elif "vue" in deps: findings["framework"] = "Vue"
                    elif "express" in deps: findings["framework"] = "Express"
                    elif "nest" in deps: findings["framework"] = "NestJS"
                    else: findings["framework"] = "Node.js (Generic)"
                    
                    if findings["framework"] != "Unknown":
                        findings["confidence"] += 0.3
            except Exception as e:
                logger.error(f"Error parsing package.json: {e}")

    def _detect_python(self, findings: dict, workspace_path: str):
        file_index = findings["file_index"]
        python_signals = ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile", "poetry.lock", "manage.py"]
        detected_signals = [s for s in python_signals if s in file_index["by_name"]]
        
        if detected_signals:
            findings["language"] = "Python"
            findings["detected_files"].extend(detected_signals)
            findings["confidence"] += 0.4
            
            # Detect entry points
            py_entries = ["app.py", "main.py", "wsgi.py", "asgi.py", "manage.py"]
            for entry in py_entries:
                if entry in file_index["by_name"]:
                    findings["entry_point"] = file_index["by_name"][entry][0]
                    findings["confidence"] += 0.2
                    break
            
            # Framework Specifics
            if "manage.py" in file_index["by_name"]:
                findings["framework"] = "Django"
                findings["confidence"] += 0.3
            elif "requirements.txt" in file_index["by_name"]:
                try:
                    req_path = os.path.join(workspace_path, file_index["by_name"]["requirements.txt"][0])
                    with open(req_path, "r") as f:
                        content = f.read().lower()
                        if "fastapi" in content: findings["framework"] = "FastAPI"
                        elif "flask" in content: findings["framework"] = "Flask"
                        elif "django" in content: findings["framework"] = "Django"
                        
                        if findings["framework"] != "Unknown":
                            findings["confidence"] += 0.3
                except: pass

            if findings["framework"] == "Unknown":
                if "poetry.lock" in file_index["by_name"] or "pyproject.toml" in file_index["by_name"]:
                    findings["framework"] = "Python (Modern/Poetry)"
                else:
                    findings["framework"] = "Python (Generic)"

    def _detect_go(self, findings: dict, workspace_path: str):
        file_index = findings["file_index"]
        if "go.mod" in file_index["by_name"]:
            findings["language"] = "Go"
            findings["detected_files"].append("go.mod")
            findings["framework"] = "Go (Modules)"
            findings["confidence"] += 0.6
            
            if "main.go" in file_index["by_name"]:
                findings["entry_point"] = file_index["by_name"]["main.go"][0]
                findings["confidence"] += 0.2

    def _detect_php(self, findings: dict, workspace_path: str):
        file_index = findings["file_index"]
        if "composer.json" in file_index["by_name"] or ".php" in file_index["by_extension"]:
            findings["language"] = "PHP"
            findings["confidence"] = max(findings["confidence"], 0.6)
            
            if "composer.json" in file_index["by_name"]:
                findings["detected_files"].append("composer.json")
                findings["framework"] = "PHP (Composer)"
            
            php_entries = ["index.php", "server.php", "app.php"]
            for entry in php_entries:
                if entry in file_index["by_name"]:
                    findings["entry_point"] = file_index["by_name"][entry][0]
                    findings["confidence"] += 0.2
                    break

    def _detect_ruby(self, findings: dict, workspace_path: str):
        file_index = findings["file_index"]
        if "Gemfile" in file_index["by_name"] or ".rb" in file_index["by_extension"]:
            findings["language"] = "Ruby"
            findings["confidence"] = max(findings["confidence"], 0.6)
            
            if "Gemfile" in file_index["by_name"]:
                findings["detected_files"].append("Gemfile")
                findings["framework"] = "Ruby (Bundler)"
            
            if "config.ru" in file_index["by_name"]:
                findings["entry_point"] = "config.ru"

    def _detect_swift(self, findings: dict, workspace_path: str):
        file_index = findings["file_index"]
        if "Package.swift" in file_index["by_name"] or ".swift" in file_index["by_extension"]:
            findings["language"] = "Swift"
            findings["confidence"] = max(findings["confidence"], 0.6)
            
            if "Package.swift" in file_index["by_name"]:
                findings["detected_files"].append("Package.swift")
                findings["framework"] = "Swift (Server-side)"

    def _detect_html(self, findings: dict, workspace_path: str):
        file_index = findings["file_index"]
        # Only detect as HTML if no other major language was found
        if findings["language"] == "Unknown" and ".html" in file_index["by_extension"]:
            findings["language"] = "HTML/Static"
            findings["framework"] = "Static Website"
            findings["confidence"] = 0.5
            
            if "index.html" in file_index["by_name"]:
                findings["entry_point"] = file_index["by_name"]["index.html"][0]
                findings["confidence"] += 0.2

        return findings

analysis_engine = AnalysisEngine()
