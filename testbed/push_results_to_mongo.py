"""Upserts the end-to-end testbed results into the `deployments` collection.

Records match the pipeline's own schema and are tagged source="testbed",
user_id="testbed" so they can be filtered out of (or into) analytics.
Run from the repo root: backend/venv/Scripts/python testbed/push_results_to_mongo.py
"""
import asyncio
import glob
import json
import os
import sys
import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "backend"))
os.chdir(os.path.join(REPO, "backend"))  # settings read backend/.env

from app.db.mongodb import db  # noqa: E402


def fmt(seconds):
    seconds = int(seconds or 0)
    return f"{seconds}s" if seconds < 60 else f"{seconds // 60}m {seconds % 60}s"


def to_doc(r):
    now = datetime.datetime.now().isoformat()
    ci = r.get("ci_runs") or []
    repo = r["repo"]
    name = repo.split("/")[-1]
    url = f"https://github.com/{repo}"
    return {
        "id": f"e2e-{r['app']}",
        "user_id": "testbed",
        "source": "testbed",
        "environment": "testbed",
        "repo_url": url,
        "normalized_repo_url": url.lower(),
        "repo_name": name,
        "status": r["status"],
        "current_message": r.get("message") or "",
        "language": r.get("language"),
        "commit": r.get("commit") or "N/A",
        "duration": fmt(r.get("seconds")),
        "deployment_url": r.get("deployment_url"),
        "pod_name": r.get("pod_name"),
        "ghcr_image": f"ghcr.io/{repo.lower()}:latest",
        "http_status": r.get("http_status"),
        "ci_runs": ci,
        "created_at": now,
        "updated_at": now,
    }


async def main():
    await db.connect_to_mongo()
    col = db.db.deployments
    docs = []
    for p in sorted(glob.glob(os.path.join(REPO, "testbed", "e2e-results", "*.json"))):
        r = json.load(open(p, encoding="utf-8"))
        if "app" in r and "repo" in r:
            docs.append(to_doc(r))
    for d in docs:
        existing = await col.find_one({"id": d["id"]}, {"created_at": 1})
        if existing and existing.get("created_at"):
            d["created_at"] = existing["created_at"]
        await col.update_one({"id": d["id"]}, {"$set": d}, upsert=True)
    n = await col.count_documents({"source": "testbed"})
    print(f"upserted {len(docs)} records; testbed records now in collection: {n}")


asyncio.run(main())
