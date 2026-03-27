from loguru import logger
import os
from typing import Dict, Any, Optional
import inspect

from .docker_templates.python_template import PythonDockerTemplate
from .docker_templates.node_template import NodeDockerTemplate
from .docker_templates.php_template import PHPDockerTemplate
from .docker_templates.java_template import JavaDockerTemplate
from .docker_templates.llm_template import LLMDockerTemplate

class FileGenerator:
    def __init__(self):
        self.strategies = {
            "Python": PythonDockerTemplate(),
            "JavaScript/TypeScript": NodeDockerTemplate(),
            "PHP": PHPDockerTemplate(),
            "Java": JavaDockerTemplate()
        }

    def _get_strategy(self, findings: Dict[str, Any]):
        lang = findings.get("language")
        return self.strategies.get(lang, LLMDockerTemplate())

    async def generate_deployment_files(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates all necessary deployment files (Dockerfile, .dockerignore) based on analysis findings.
        Supports multi-service monorepos and database detection.
        """
        success = True
        services = findings.get("services", [])
        
        # 1. Generate Dockerfiles for each service
        for service in services:
            service_rel_path = service.get("path", "")
            service_abs_path = os.path.join(workspace_path, service_rel_path)
            
            # Ensure service directory exists
            if not os.path.exists(service_abs_path):
                os.makedirs(service_abs_path, exist_ok=True)
                
            df_s = await self.generate_dockerfile(service_abs_path, service)
            di_s = self.generate_dockerignore(service_abs_path, service)
            success = success and (df_s or os.path.exists(os.path.join(service_abs_path, "Dockerfile")))

        # 2. Generate Docker Compose if multi-service or database detected
        if len(services) > 1 or findings.get("databases"):
            compose_s = await self.generate_docker_compose(workspace_path, findings)
            success = success and compose_s

        # 3. Generate CI/CD workflow (at workspace root)
        ci_s = self.generate_cicd_workflow(workspace_path, findings)
        
        # 4. Generate .env.example (at workspace root)
        env_s = self.generate_env_file(workspace_path, findings)
        
        return success

    async def generate_dockerfile(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates a recommended Dockerfile using the appropriate template strategy.
        'findings' here refers to a specific service's findings.
        """
        dockerfile_path = os.path.join(workspace_path, "Dockerfile")
        
        if os.path.exists(dockerfile_path):
            logger.info(f"Dockerfile already exists at {dockerfile_path}. Skipping generation.")
            return False

        strategy = self._get_strategy(findings)

        if inspect.iscoroutinefunction(strategy.generate_dockerfile):
            content = await strategy.generate_dockerfile(findings)
        else:
            content = strategy.generate_dockerfile(findings)
        
        if content:
            try:
                with open(dockerfile_path, "w") as f:
                    f.write(content)
                logger.info(f"Generated Dockerfile at {dockerfile_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to generate Dockerfile at {dockerfile_path}: {e}")
        
        return False

    async def generate_docker_compose(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates a docker-compose.yml file representing all services and databases.
        """
        compose_path = os.path.join(workspace_path, "docker-compose.yml")
        if os.path.exists(compose_path):
            logger.info("docker-compose.yml already exists. Skipping.")
            return False

        services_config = {}
        networks = {"app-network": {"driver": "bridge"}}
        volumes = {}

        # 1. Add Application Services
        for index, service in enumerate(findings.get("services", [])):
            name = service.get("name", f"service-{index}")
            path = service.get("path", ".")
            
            # Simple Port Mapping Heuristic
            # Backend usually 8000 (Python/Go/FastAPI), Java usually 8080, Frontend 3000 (React/Next)
            is_frontend = any(kw in (name.lower() or "") for kw in ["frontend", "client", "web"])
            is_frontend = is_frontend or service.get("framework") in ["React", "Next.js", "Vue"]
            is_java = service.get("language") == "Java"
            
            if is_frontend:
                internal_port = "3000"
                external_port = str(3000 + index)
            elif is_java:
                internal_port = "8080"
                external_port = str(8080 + index)
            else:
                internal_port = "8000"
                external_port = str(8000 + index)


            services_config[name] = {
                "build": {
                    "context": ".",
                    "dockerfile": os.path.join(path, "Dockerfile").replace("\\", "/")
                },
                "ports": [f"{external_port}:{internal_port}"],
                "networks": ["app-network"],
                "restart": "unless-stopped"
            }

            # Inject database dependency if detected
            if findings.get("databases"):
                services_config[name]["depends_on"] = [db.lower().replace("/", "-") for db in findings["databases"]]

        # 2. Add Database Services
        for db in findings.get("databases", []):
            db_id = db.lower().replace("/", "-")
            if db == "PostgreSQL":
                services_config[db_id] = {
                    "image": "postgres:15-alpine",
                    "environment": {
                        "POSTGRES_USER": "admin",
                        "POSTGRES_PASSWORD": "password123",
                        "POSTGRES_DB": "app_db"
                    },
                    "networks": ["app-network"],
                    "volumes": [f"{db_id}-data:/var/lib/postgresql/data"]
                }
                volumes[f"{db_id}-data"] = None
            elif db == "MongoDB":
                services_config[db_id] = {
                    "image": "mongo:latest",
                    "networks": ["app-network"],
                    "volumes": [f"{db_id}-data:/data/db"]
                }
                volumes[f"{db_id}-data"] = None
            elif db == "Redis" or db == "Redis":
                 services_config[db_id] = {
                    "image": "redis:alpine",
                    "networks": ["app-network"]
                }
            elif db == "MySQL":
                services_config[db_id] = {
                    "image": "mysql:8",
                    "environment": {
                        "MYSQL_ROOT_PASSWORD": "rootpassword",
                        "MYSQL_DATABASE": "app_db",
                        "MYSQL_USER": "admin",
                        "MYSQL_PASSWORD": "password123"
                    },
                    "networks": ["app-network"],
                    "volumes": [f"{db_id}-data:/var/lib/mysql"]
                }
                volumes[f"{db_id}-data"] = None

        import yaml
        compose_data = {
            "version": "3.8",
            "services": services_config,
            "networks": networks
        }
        if volumes:
            compose_data["volumes"] = volumes

        try:
            with open(compose_path, "w") as f:
                yaml.dump(compose_data, f, sort_keys=False, default_flow_style=False)
            logger.info(f"Generated docker-compose.yml at {compose_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate docker-compose.yml: {e}")
            return False

    def generate_dockerignore(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates a .dockerignore file.
        'findings' refers to a specific service.
        """
        ignore_path = os.path.join(workspace_path, ".dockerignore")
        if os.path.exists(ignore_path):
            return False

        strategy = self._get_strategy(findings)
        content = strategy.generate_dockerignore(findings)

        try:
            with open(ignore_path, "w") as f:
                f.write(content)
            logger.info(f"Generated .dockerignore at {ignore_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate .dockerignore at {ignore_path}: {e}")
            return False

    def generate_cicd_workflow(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates a GitHub Actions CI/CD workflow based on project detected language using the template strategy.
        'findings' can be global or root service.
        """
        github_dir = os.path.join(workspace_path, ".github", "workflows")
        os.makedirs(github_dir, exist_ok=True)
        workflow_path = os.path.join(github_dir, "deploy.yml")

        if os.path.exists(workflow_path):
            return False

        # In multi-service context, findings might be global. Take first service for workflow template.
        primary_findings = findings
        if findings.get("services"):
            primary_findings = findings["services"][0]

        strategy = self._get_strategy(primary_findings)
        content = strategy.generate_cicd_workflow(primary_findings)

        try:
            with open(workflow_path, "w") as f:
                f.write(content)
            logger.info(f"Generated CI/CD workflow at {workflow_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate CI/CD workflow at {workflow_path}: {e}")
            return False

    def generate_env_file(self, workspace_path: str, findings: Dict[str, Any]) -> bool:
        """
        Generates an environment template if env variables were found.
        Collects from all services.
        """
        env_vars = set(findings.get("env_vars", []))
        for s in findings.get("services", []):
            for v in s.get("env_vars", []):
                env_vars.add(v)
                
        if not env_vars:
            # If databases detected, add common env vars
            if findings.get("databases"):
                env_vars.update(["DATABASE_URL", "DB_HOST", "DB_USER", "DB_PASS"])
            else:
                return False

        env_path = os.path.join(workspace_path, ".env.example")
        if os.path.exists(env_path):
            return False

        try:
            with open(env_path, "w") as f:
                for var in sorted(list(env_vars)):
                    f.write(f"{var}=your_value_here\n")
            logger.info(f"Generated .env.example at {env_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate .env.example at {env_path}: {e}")
            return False


file_generator = FileGenerator()
