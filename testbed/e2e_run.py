"""End-to-end run of the real pipeline on the testbed apps.

For each app: create/seed a GitHub repo, then call the tool's own
`analyze_repo_task` (clone -> analyze -> generate -> push -> monitor the
GitHub Actions run for the pushed commit -> deploy to Minikube -> HTTP check).
Stubbed: the Clerk token lookup (uses `gh auth token`), MongoDB writes, and the
AI fallback, so each app gets one deterministic first attempt.

Usage: python testbed/e2e_run.py --owner theakashainapur [--visibility public|private]
                                 [--apps a,b,c] [--deploy-concurrency 2]
Results: testbed/e2e-results/<app>.json and testbed/e2e-results/summary.md
"""
import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import httpx

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(REPO, "testbed", "apps")
OUT_DIR = os.path.join(REPO, "testbed", "e2e-results")
sys.path.insert(0, os.path.join(REPO, "backend"))
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
for k in ("GROQ_API_KEY", "OPENROUTER_API_KEY", "GOOGLE_API_KEY"):
    os.environ[k] = ""

GH = r"C:\Program Files\GitHub CLI\gh.exe" if os.name == "nt" else "gh"
TERMINAL = {"success", "failed"}
CREATE_LOCK = asyncio.Lock()


def sh(cmd, cwd=None, check=True, timeout=180):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=env, stdin=subprocess.DEVNULL, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {r.stderr.strip()[:300]}")
    return r


def gh_token():
    return sh([GH, "auth", "token"]).stdout.strip()


def ensure_repo(owner, name, visibility, token):
    """Creates the repo if missing and seeds main with the app files (no generated files)."""
    full = f"{owner}/{name}"
    exists = sh([GH, "repo", "view", full], check=False).returncode == 0
    if not exists:
        # New accounts hit "too many repositories" when creating several at once:
        # back off and retry instead of failing the app.
        for attempt in range(8):
            r = sh([GH, "repo", "create", full, f"--{visibility}", "--description", "Deployment testbed sample app"], check=False)
            if r.returncode == 0:
                break
            if "too many repositories" not in r.stderr:
                raise RuntimeError(f"gh repo create failed: {r.stderr.strip()[:300]}")
            time.sleep(90)
        else:
            raise RuntimeError("gh repo create kept hitting the repository creation rate limit")
        time.sleep(20)
    remote = f"https://x-access-token:{token}@github.com/{full}.git"
    tmp = tempfile.mkdtemp(prefix="tb_seed_")
    try:
        app_dir = os.path.join(APPS_DIR, name[len("tb-"):])
        shutil.copytree(app_dir, tmp, dirs_exist_ok=True, ignore=shutil.ignore_patterns("expect.json"))
        sh(["git", "init", "-q", "-b", "main"], cwd=tmp)
        sh(["git", "add", "-A"], cwd=tmp)
        sh(["git", "-c", "user.name=testbed", "-c", "user.email=testbed@example.com", "commit", "-q", "-m", "Seed sample app"], cwd=tmp)
        sh(["git", "remote", "add", "origin", remote], cwd=tmp)
        pushed = sh(["git", "push", "-q", "-u", "origin", "main"], cwd=tmp, check=False)
        # A rejected push means the repo already has history from an earlier run; keep it.
        if pushed.returncode != 0 and "rejected" not in pushed.stderr and "fetch first" not in pushed.stderr:
            raise RuntimeError("seed push failed: " + pushed.stderr.replace(token, "***")[:300])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return full


async def run_app(app, owner, visibility, token, timeout, results):
    from app.api.v1.endpoints import analyze
    from app.services.task_manager import task_manager

    name = f"tb-{app}"
    rec = {"app": app, "repo": f"{owner}/{name}", "started": time.time()}
    results[app] = rec
    try:
        async with CREATE_LOCK:
            await asyncio.to_thread(ensure_repo, owner, name, visibility, token)
        url = f"https://github.com/{owner}/{name}"
        task_id = f"e2e-{app}"
        task_manager.update_task(task_id, "initialized", repo_url=url, user_id="e2e")
        await analyze.analyze_repo_task(task_id, url, "main", "e2e")

        deadline = time.time() + timeout
        while time.time() < deadline:
            t = task_manager.get_task(task_id)
            if t and t.get("status") in TERMINAL:
                break
            await asyncio.sleep(5)
        t = task_manager.get_task(task_id) or {}
        rec["status"] = t.get("status", "timeout")
        rec["message"] = t.get("current_message")
        rec["language"] = t.get("language")
        rec["commit"] = t.get("commit")
        rec["deployment_url"] = t.get("deployment_url")
        rec["pod_name"] = t.get("pod_name")

        if rec["deployment_url"]:
            try:
                async with httpx.AsyncClient(timeout=10) as c:
                    r = await c.get(rec["deployment_url"])
                rec["http_status"] = r.status_code
                rec["http_body"] = r.text[:80]
            except Exception as e:
                rec["http_status"] = None
                rec["http_error"] = str(e)[:150]

        # CI facts straight from GitHub, independent of the tool's own status
        runs = await asyncio.to_thread(
            sh, [GH, "api", f"repos/{owner}/{name}/actions/runs?per_page=5"], None, False)
        if runs.returncode == 0:
            wr = json.loads(runs.stdout).get("workflow_runs", [])
            rec["ci_runs"] = [{"sha": w["head_sha"][:7], "conclusion": w["conclusion"], "event": w["event"]} for w in wr]
    except Exception as e:
        rec["status"] = "runner_error"
        rec["message"] = str(e)[:300]
    rec["seconds"] = round(time.time() - rec.pop("started"))
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"{app}.json"), "w") as f:
        json.dump(rec, f, indent=2)
    print(f"[{app}] {rec['status']} http={rec.get('http_status')} {rec['seconds']}s", flush=True)


def write_summary(results):
    ok = lambda v: "✅" if v else "❌"
    lines = ["| app | tool status | CI green | URL | HTTP | secs | note |", "|---|---|---|---|---|---|---|"]
    for app in sorted(results):
        r = results[app]
        ci = r.get("ci_runs") or []
        green = any(c["conclusion"] == "success" for c in ci)
        http_ok = isinstance(r.get("http_status"), int) and r["http_status"] < 500
        note = (r.get("message") or "").replace("\n", " ")[:90]
        lines.append(f"| {app} | {r.get('status')} | {ok(green)} | {ok(r.get('deployment_url'))} | {ok(http_ok)} | {r.get('seconds')} | {note} |")
    good = sum(1 for r in results.values() if r.get("status") == "success" and isinstance(r.get("http_status"), int) and r["http_status"] < 500)
    lines.append(f"\n**Fully deployed and answering HTTP: {good} / {len(results)}**")
    with open(os.path.join(OUT_DIR, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", required=True)
    ap.add_argument("--visibility", default="private", choices=["private", "public"])
    ap.add_argument("--apps", default="")
    ap.add_argument("--deploy-concurrency", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()

    token = gh_token()
    apps = [a for a in args.apps.split(",") if a] or sorted(os.listdir(APPS_DIR))

    # --- stubs: no Clerk, no MongoDB, no AI fallback ---
    from app.api.v1.endpoints import analyze
    from app.db import mongodb
    from app.services import ai_service as ai_mod
    from app.services import minikube_deployment_manager as mdm

    async def _token(_user_id):
        return token

    async def _noop(*a, **k):
        return True

    analyze.fetch_github_token = _token
    mongodb.db.store_deployment_data = _noop
    ai_mod.ai_service.providers = []

    sem = asyncio.Semaphore(args.deploy_concurrency)
    real_deploy = mdm.deploy_to_minikube_bg

    async def limited_deploy(*a, **k):
        async with sem:
            await real_deploy(*a, **k)
            # free cluster memory for the next app once its result is recorded
            await asyncio.sleep(20)
            slug = mdm.slugify(a[1])
            await mdm.run_command(["kubectl", "delete", "deployment", slug, "--ignore-not-found=true"])

    mdm.deploy_to_minikube_bg = limited_deploy

    results = {}
    await asyncio.gather(*[run_app(a, args.owner, args.visibility, token, args.timeout, results) for a in apps])
    write_summary(results)


if __name__ == "__main__":
    asyncio.run(main())
