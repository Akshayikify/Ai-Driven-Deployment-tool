import os
import json
from loguru import logger
from typing import Dict, Any

class AnalysisEngine:
    def analyze_directory(self, workspace_path: str) -> Dict[str, Any]:
        """
        Deeply analyzes the directory to detect language, framework, and entry points.
        Supports Monorepos by detecting multiple services.
        """
        logger.info(f"Performing deep analysis on: {workspace_path}")
        
        file_index = {
            "all_files": [],
            "by_name": {},  # name -> list of full paths
            "by_extension": {} # .ext -> list of full paths
        }

        # 1. Recursive Indexing
        for root, dirs, files in os.walk(workspace_path):
            # Prune directories to ignore for better performance and to avoid indexing noise
            dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "venv", "__pycache__", "aienv", ".venv", "dist", "build", "target"]]
            
            rel_root = os.path.relpath(root, workspace_path)
            if rel_root == ".":
                rel_root = ""
                
            for f in files:
                # Standardize separators for cross-platform consistency
                full_rel_path = os.path.join(rel_root, f).replace("\\", "/")
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
            "services": [],
            "databases": [],
            "architecture": "Standard",
            "file_index": file_index
        }

        # 2. Identify Potential Service Roots
        roots = self._identify_service_roots(file_index)
        
        for root_path in roots:
            service_findings = self._analyze_service(workspace_path, root_path, file_index)
            if service_findings["language"] != "Unknown":
                findings["services"].append(service_findings)

        # 3. Detect Architecture
        if len(findings["services"]) > 1:
            findings["architecture"] = "Monorepo"
        elif not findings["services"]:
            # Fallback for very simple projects that didn't match service roots
            fallback = self._create_empty_findings("")
            self._apply_detections(fallback, workspace_path, file_index, "")
            if fallback["language"] != "Unknown":
                findings["services"].append(fallback)

        # 4. Detect Databases
        findings["databases"] = self._detect_databases(findings)

        # 5. Backward Compatibility (Populate top-level fields from primary service)
        if findings["services"]:
            primary = findings["services"][0]
            # If there's a root-level service, use it as primary
            for s in findings["services"]:
                if s["path"] == "" or s["path"] == ".":
                    primary = s
                    break
            
            findings.update({
                "language": primary["language"],
                "framework": primary["framework"],
                "confidence": primary["confidence"],
                "entry_point": primary["entry_point"],
                "detected_files": primary["detected_files"],
                "dependencies": primary["dependencies"]
            })
        else:
            findings.update({
                "language": "Unknown",
                "framework": "Unknown",
                "confidence": 0.0,
                "entry_point": None,
                "detected_files": [],
                "dependencies": []
            })
        
        # 6. Predict Deployment Time
        findings["estimated_duration"] = self._predict_deployment_time(findings)

        logger.info(f"Deep analysis complete. Detected {len(findings['services'])} services and {len(findings['databases'])} databases. Estimated deployment: {findings['estimated_duration']}")
        return findings

    def _predict_deployment_time(self, findings: Dict[str, Any]) -> str:
        """
        AI estimation of how long the deployment will take in seconds based on project complexity.
        """
        total_seconds = 45 # Baseline for cloning & analysis
        
        # 1. Framework Base Times (Seconds)
        base_times = {
            "Java": 240,
            "Maven / Spring Boot": 300,
            "JavaScript/TypeScript": 120,
            "Next.js": 180,
            "React": 150,
            "Python": 90,
            "FastAPI": 100,
            "Django": 150,
            "PHP": 80,
            "Go": 60,
            "Unknown": 120
        }
        
        # 2. Add complexity for each service
        for service in findings.get("services", []):
            lang = service.get("language", "Unknown")
            framework = service.get("framework", "Unknown")
            
            # Use framework time if specifically known, else language, else generic
            service_base = base_times.get(framework, base_times.get(lang, 120))
            
            # Add multiplier for dependency count
            dep_count = len(service.get("dependencies", []))
            dep_penalty = min(dep_count * 2, 60) # Up to 1 min extra for many deps
            
            total_seconds += service_base + dep_penalty
            
        # 3. Add penalty for databases (infrastructure setup)
        total_seconds += len(findings.get("databases", [])) * 40
        
        # 4. Multi-service coordination penalty
        if len(findings.get("services", [])) > 1:
            total_seconds += 30 
            
        # Format as M:SS
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        if minutes == 0:
            return f"{seconds}s"
        return f"{minutes}m {seconds}s"

    def _identify_service_roots(self, file_index: dict) -> list:
        """Finds directories that likely represent the root of a service."""
        core_manifests = ["package.json", "requirements.txt", "pyproject.toml", "go.mod", "pom.xml", "composer.json", "Gemfile", "Dockerfile"]
        # Also look for common entry point signals if manifest is missing
        entry_signals = ["app.py", "main.py", "server.js", "index.js", "main.go", "sentiment_api.py"]
        
        roots = set()
        for signal in core_manifests + entry_signals:
            if signal in file_index["by_name"]:
                for rel_path in file_index["by_name"][signal]:
                    root = os.path.dirname(rel_path)
                    # For root level, use empty string
                    if root == "." or root == "":
                        roots.add("")
                    else:
                        roots.add(root)
        
        # Prune nested roots: if 'root/sub' and 'root' are both present, 
        # keep only the top-most root unless 'root' is empty.
        # Exception: don't prune if it's a known monorepo structure.
        sorted_roots = sorted(list(roots), key=len)
        pruned_roots = []
        for r in sorted_roots:
            is_nested = False
            for parent in pruned_roots:
                if parent != "" and r.startswith(parent + "/"):
                    is_nested = True
                    break
            if not is_nested:
                pruned_roots.append(r)
        
        return pruned_roots


    def _analyze_service(self, workspace_path: str, service_rel_path: str, file_index: dict) -> dict:
        """Analyzes a specific sub-directory as a potential service."""
        findings = self._create_empty_findings(service_rel_path)
        self._apply_detections(findings, workspace_path, file_index, service_rel_path)
        return findings

    def _create_empty_findings(self, path: str) -> dict:
        return {
            "name": os.path.basename(path) if path else "root",
            "path": path,
            "language": "Unknown",
            "framework": "Unknown",
            "entry_point": None,
            "confidence": 0.0,
            "detected_files": [],
            "dependencies": []
        }

    def _apply_detections(self, findings: dict, workspace_path: str, file_index: dict, service_path: str):
        """Runs all detection methods on a specific directory."""
        self._detect_node(findings, workspace_path, file_index, service_path)
        self._detect_python(findings, workspace_path, file_index, service_path)
        self._detect_go(findings, workspace_path, file_index, service_path)
        self._detect_php(findings, workspace_path, file_index, service_path)
        self._detect_ruby(findings, workspace_path, file_index, service_path)
        self._detect_swift(findings, workspace_path, file_index, service_path)
        self._detect_java(findings, workspace_path, file_index, service_path)
        self._detect_html(findings, workspace_path, file_index, service_path)

        # Check for existing Dockerfile in this specific dir
        dockerfile_name = "Dockerfile"
        if service_path:
            dockerfile_path = f"{service_path}/{dockerfile_name}"
        else:
            dockerfile_path = dockerfile_name
            
        if dockerfile_path in file_index["all_files"]:
            findings["detected_files"].append(dockerfile_name)
            if findings["framework"] == "Unknown":
                findings["framework"] = "Existing Container"
                findings["confidence"] = max(findings["confidence"], 0.5)

    def _detect_databases(self, findings: dict) -> list:
        """Identifies database requirements based on dependencies and files."""
        databases = set()
        
        # 1. Dependency-based detection
        for service in findings.get("services", []):
            deps = " ".join(service.get("dependencies", [])).lower()
            
            # PostgreSQL
            if any(k in deps for k in ["postgres", "psycopg2", "pg", "sequelize", "typeorm", "postgresql"]):
                databases.add("PostgreSQL")
            
            # MongoDB
            if any(k in deps for k in ["mongodb", "pymongo", "mongoose", "motor", "mongodb-driver", "spring-boot-starter-data-mongodb"]):
                databases.add("MongoDB")
            
            # Redis
            if any(k in deps for k in ["redis", "ioredis", "spring-boot-starter-data-redis"]):
                databases.add("Redis")
            
            # MySQL
            if any(k in deps for k in ["mysql", "mysqlclient", "mariadb", "mysql2", "mysql-connector"]):
                databases.add("MySQL")
            
            # SQLite
            if "sqlite" in deps:
                databases.add("SQLite")
                
            # H2 (Common in Java)
            if "h2" in deps:
                databases.add("H2 (Memory DB)")


        # 2. File-based detection (e.g., .sql files, config files)
        file_index = findings.get("file_index", {})
        if ".sql" in file_index.get("by_extension", {}):
            # If no DB detected yet, assume Postgres or MySQL as default for SQL files
            if not databases:
                databases.add("PostgreSQL")

        return sorted(list(databases))

    def _detect_node(self, findings: dict, workspace_path: str, file_index: dict, service_path: str):
        pkg_json = "package.json"
        rel_pkg_path = f"{service_path}/{pkg_json}" if service_path else pkg_json
        
        if rel_pkg_path in file_index["all_files"]:
            findings["language"] = "JavaScript/TypeScript"
            findings["detected_files"].append(pkg_json)
            findings["confidence"] += 0.4
            
            # Detect entry points
            node_entries = ["server.js", "index.js", "app.js", "main.js", "index.ts", "server.ts"]
            for entry in node_entries:
                entry_path = f"{service_path}/{entry}" if service_path else entry
                if entry_path in file_index["all_files"]:
                    findings["entry_point"] = entry_path
                    findings["confidence"] += 0.2
                    break

            try:
                full_pkg_path = os.path.join(workspace_path, rel_pkg_path)
                with open(full_pkg_path, "r") as f:
                    pkg_data = json.load(f)
                    deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                    findings["dependencies"] = list(deps.keys())
                    
                    if "next" in deps: findings["framework"] = "Next.js"
                    elif "react" in deps: findings["framework"] = "React"
                    elif "vue" in deps: findings["framework"] = "Vue"
                    elif "express" in deps: findings["framework"] = "Express"
                    elif "nest" in deps: findings["framework"] = "NestJS"
                    elif "@fastify/core" in deps or "fastify" in deps: findings["framework"] = "Fastify"
                    else: findings["framework"] = "Node.js (Generic)"
                    
                    if findings["framework"] != "Unknown":
                        findings["confidence"] += 0.3
            except Exception as e:
                logger.error(f"Error parsing package.json at {rel_pkg_path}: {e}")

    def _detect_python(self, findings: dict, workspace_path: str, file_index: dict, service_path: str):
        python_signals = ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile", "poetry.lock", "manage.py"]
        
        detected_signals = []
        for sig in python_signals:
            sig_path = f"{service_path}/{sig}" if service_path else sig
            if sig_path in file_index["all_files"]:
                detected_signals.append(sig)
        
        if detected_signals:
            findings["language"] = "Python"
            findings["detected_files"].extend(detected_signals)
            findings["confidence"] += 0.4
            
            # Detect entry points
            py_entries = ["app.py", "main.py", "wsgi.py", "asgi.py", "manage.py"]
            for entry in py_entries:
                entry_path = f"{service_path}/{entry}" if service_path else entry
                if entry_path in file_index["all_files"]:
                    findings["entry_point"] = entry_path
                    findings["confidence"] += 0.2
                    break
            
            # Framework Specifics & Dependency Parsing
            if "manage.py" in detected_signals:
                findings["framework"] = "Django"
                findings["confidence"] += 0.3
            
            # Read requirements.txt if present to populate dependencies
            if "requirements.txt" in detected_signals:
                try:
                    rel_req_path = f"{service_path}/requirements.txt" if service_path else "requirements.txt"
                    req_path = os.path.join(workspace_path, rel_req_path)
                    with open(req_path, "r") as f:
                        lines = f.readlines()
                        # Simple parsing of requirements.txt
                        deps = []
                        for line in lines:
                            line = line.strip().lower()
                            if line and not line.startswith("#"):
                                # Handle version specifiers (FastAPI==0.68.0 -> fastapi)
                                for sep in ["==", ">=", "<=", "~=", ">", "<"]:
                                    if sep in line:
                                        line = line.split(sep)[0].strip()
                                        break
                                deps.append(line)
                        findings["dependencies"] = deps
                        
                        # Detect framework from deps
                        if "fastapi" in deps: findings["framework"] = "FastAPI"
                        elif "flask" in deps: findings["framework"] = "Flask"
                        elif "django" in deps: findings["framework"] = "Django"
                        
                        if findings["framework"] != "Unknown":
                            findings["confidence"] += 0.3
                except Exception as e:
                    logger.error(f"Error parsing requirements.txt at {service_path}: {e}")

            if findings["framework"] == "Unknown":
                if "poetry.lock" in detected_signals or "pyproject.toml" in detected_signals:
                    findings["framework"] = "Python (Modern/Poetry)"
                else:
                    findings["framework"] = "Python (Generic)"


    def _detect_go(self, findings: dict, workspace_path: str, file_index: dict, service_path: str):
        go_mod = "go.mod"
        rel_go_mod = f"{service_path}/{go_mod}" if service_path else go_mod
        
        if rel_go_mod in file_index["all_files"]:
            findings["language"] = "Go"
            findings["detected_files"].append(go_mod)
            findings["framework"] = "Go (Modules)"
            findings["confidence"] += 0.6
            
            main_go = f"{service_path}/main.go" if service_path else "main.go"
            if main_go in file_index["all_files"]:
                findings["entry_point"] = main_go
                findings["confidence"] += 0.2

    def _detect_php(self, findings: dict, workspace_path: str, file_index: dict, service_path: str):
        composer_json = "composer.json"
        rel_composer = f"{service_path}/{composer_json}" if service_path else composer_json
        
        has_php_files = any(f.endswith(".php") and (not service_path or f.startswith(service_path)) for f in file_index["all_files"])
        
        if rel_composer in file_index["all_files"] or has_php_files:
            findings["language"] = "PHP"
            findings["confidence"] = max(findings["confidence"], 0.6)
            
            if rel_composer in file_index["all_files"]:
                findings["detected_files"].append(composer_json)
                findings["framework"] = "PHP (Composer)"
            
            php_entries = ["index.php", "server.php", "app.php"]
            for entry in php_entries:
                entry_path = f"{service_path}/{entry}" if service_path else entry
                if entry_path in file_index["all_files"]:
                    findings["entry_point"] = entry_path
                    findings["confidence"] += 0.2
                    break

    def _detect_ruby(self, findings: dict, workspace_path: str, file_index: dict, service_path: str):
        gemfile = "Gemfile"
        rel_gemfile = f"{service_path}/{gemfile}" if service_path else gemfile
        has_ruby_files = any(f.endswith(".rb") and (not service_path or f.startswith(service_path)) for f in file_index["all_files"])

        if rel_gemfile in file_index["all_files"] or has_ruby_files:
            findings["language"] = "Ruby"
            findings["confidence"] = max(findings["confidence"], 0.6)
            
            if rel_gemfile in file_index["all_files"]:
                findings["detected_files"].append(gemfile)
                findings["framework"] = "Ruby (Bundler)"
            
            config_ru = f"{service_path}/config.ru" if service_path else "config.ru"
            if config_ru in file_index["all_files"]:
                findings["entry_point"] = config_ru

    def _detect_swift(self, findings: dict, workspace_path: str, file_index: dict, service_path: str):
        pkg_swift = "Package.swift"
        rel_pkg_swift = f"{service_path}/{pkg_swift}" if service_path else pkg_swift
        has_swift_files = any(f.endswith(".swift") and (not service_path or f.startswith(service_path)) for f in file_index["all_files"])

        if rel_pkg_swift in file_index["all_files"] or has_swift_files:
            findings["language"] = "Swift"
            findings["confidence"] = max(findings["confidence"], 0.6)
            
            if rel_pkg_swift in file_index["all_files"]:
                findings["detected_files"].append(pkg_swift)
                findings["framework"] = "Swift (Server-side)"

    def _detect_html(self, findings: dict, workspace_path: str, file_index: dict, service_path: str):
        # Only detect as HTML if no other major language was found
        has_html_files = any(f.endswith(".html") and (not service_path or f.startswith(service_path)) for f in file_index["all_files"])
        
        if findings["language"] == "Unknown" and has_html_files:
            findings["language"] = "HTML/Static"
            findings["framework"] = "Static Website"
            findings["confidence"] = 0.5
            
            index_html = f"{service_path}/index.html" if service_path else "index.html"
            if index_html in file_index["all_files"]:
                findings["entry_point"] = index_html
                findings["confidence"] += 0.2

    def _detect_java(self, findings: dict, workspace_path: str, file_index: dict, service_path: str):
        java_signals = ["pom.xml", "build.gradle", "settings.gradle", "mvnw", "gradlew"]
        
        detected_signals = []
        for sig in java_signals:
            sig_path = f"{service_path}/{sig}" if service_path else sig
            if sig_path in file_index["all_files"]:
                detected_signals.append(sig)
        
        if detected_signals:
            findings["language"] = "Java"
            findings["detected_files"].extend(detected_signals)
            findings["confidence"] = max(findings["confidence"], 0.6)
            
            # 1. Framework & Dependency Detection
            if "pom.xml" in detected_signals:
                findings["framework"] = "Maven / Spring Boot"
                findings["confidence"] += 0.2
                try:
                    pom_rel_path = f"{service_path}/pom.xml" if service_path else "pom.xml"
                    pom_path = os.path.join(workspace_path, pom_rel_path)
                    with open(pom_path, "r", encoding="utf-8") as f:
                        content = f.read().lower()
                        # Very simple artifactId detection
                        import re
                        deps = re.findall(r"<artifactid>([^<]+)</artifactid>", content)
                        findings["dependencies"] = list(set(deps))
                except: pass

            elif "build.gradle" in detected_signals:
                findings["framework"] = "Gradle"
                findings["confidence"] += 0.2
                try:
                    gradle_rel_path = f"{service_path}/build.gradle" if service_path else "build.gradle"
                    gradle_path = os.path.join(workspace_path, gradle_rel_path)
                    with open(gradle_path, "r", encoding="utf-8") as f:
                        content = f.read().lower()
                        # Simple regex for compile/implementation dependencies
                        deps = re.findall(r"['\"]([^'\"]+:[^'\"]+:[^'\"]+)['\"]", content)
                        # Fallback for simpler declarations
                        deps += re.findall(r"implementation\s+['\"]([^'\"]+)['\"]", content)
                        findings["dependencies"] = list(set(deps))
                except: pass
            
            # 2. Advanced DB detection via properties/yml
            config_files = ["application.properties", "application.yml", "application.yaml"]
            for cfg in config_files:
                cfg_path = f"{service_path}/src/main/resources/{cfg}" if service_path else f"src/main/resources/{cfg}"
                if cfg_path in file_index["all_files"]:
                    try:
                        p = os.path.join(workspace_path, cfg_path)
                        with open(p, "r", encoding="utf-8") as f:
                            c = f.read().lower()
                            if "jdbc:postgresql" in c: findings["dependencies"].append("postgresql-driver")
                            if "jdbc:mysql" in c: findings["dependencies"].append("mysql-driver")
                            if "mongodb://" in c: findings["dependencies"].append("mongodb-driver")
                    except: pass

            # 3. Find probable entry points
            if "Application.java" in file_index["by_name"]:
                for path in file_index["by_name"]["Application.java"]:
                    if not service_path or path.startswith(service_path):
                        findings["entry_point"] = path
                        findings["confidence"] += 0.1
                        break



analysis_engine = AnalysisEngine()
