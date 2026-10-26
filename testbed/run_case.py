"""Runs the analyzer and file generator on one testbed app.

Usage: python testbed/run_case.py <app_dir> <workspace_dir> <result_json>

The app is copied into <workspace_dir>, analysed, and the deployment files
are generated there, exactly as the pipeline does after cloning. The CI
workflow then builds the generated Dockerfile and probes the container.
AI providers are disabled so results are deterministic.
"""
import asyncio
import json
import os
import re
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "backend"))
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("GROQ_API_KEY", "")
os.environ.setdefault("OPENROUTER_API_KEY", "")
os.environ.setdefault("GOOGLE_API_KEY", "")


def run_case(app_dir, workspace):
    from app.services.analysis import analysis_engine
    from app.services.generator import file_generator
    from app.services import ai_service as ai_mod
    ai_mod.ai_service.providers = []

    expect = {}
    exp_path = os.path.join(app_dir, "expect.json")
    if os.path.exists(exp_path):
        with open(exp_path) as f:
            expect = json.load(f)

    if os.path.exists(workspace):
        shutil.rmtree(workspace)
    shutil.copytree(app_dir, workspace, ignore=shutil.ignore_patterns("expect.json"))

    findings = analysis_engine.analyze_directory(workspace)
    asyncio.run(file_generator.generate_deployment_files(workspace, findings))

    dockerfile = os.path.join(workspace, "Dockerfile")
    expose = None
    if os.path.exists(dockerfile):
        with open(dockerfile) as f:
            m = re.search(r"(?im)^\s*EXPOSE\s+(\d+)", f.read())
            if m:
                expose = int(m.group(1))

    detected = {
        "language": findings.get("language"),
        "framework": findings.get("framework"),
        "services": len(findings.get("services", [])),
    }
    checks = {
        "language": detected["language"] == expect.get("language"),
        "framework": detected["framework"] == expect.get("framework"),
        "services": detected["services"] == expect.get("services", 1),
        "dockerfile": os.path.exists(dockerfile),
        "workflow": os.path.exists(os.path.join(workspace, ".github", "workflows", "deploy.yml")),
    }
    return {
        "app": os.path.basename(os.path.normpath(app_dir)),
        "expected": expect,
        "detected": detected,
        "expose": expose,
        "path": expect.get("path", "/"),
        "checks": checks,
        "detect_ok": all(checks.values()),
    }


if __name__ == "__main__":
    app_dir, workspace, out = sys.argv[1:4]
    result = run_case(app_dir, workspace)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
