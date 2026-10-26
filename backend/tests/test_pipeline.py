"""Unit checks for the pipeline fixes that don't need Docker, GitHub or Minikube."""
import asyncio
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "testbed"))
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")

import yaml  # noqa: E402

from app.services.k8s_generator import generate_deployment_yaml  # noqa: E402
from app.services.minikube_deployment_manager import verify_http  # noqa: E402


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(404 if self.path == "/missing" else 503 if self.path == "/down" else 200)
        self.end_headers()

    def log_message(self, *args):
        pass


def _serve():
    srv = HTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def test_verify_http_accepts_app_that_answers():
    srv = _serve()
    ok, detail = asyncio.run(verify_http(f"http://127.0.0.1:{srv.server_port}/", attempts=2, delay=0.1))
    assert ok, detail


def test_verify_http_accepts_404_but_rejects_5xx_and_closed_port():
    srv = _serve()
    base = f"http://127.0.0.1:{srv.server_port}"
    assert asyncio.run(verify_http(base + "/missing", attempts=1, delay=0))[0]
    assert not asyncio.run(verify_http(base + "/down", attempts=2, delay=0.05))[0]
    srv.shutdown()
    srv.server_close()
    assert not asyncio.run(verify_http(base + "/", attempts=2, delay=0.05))[0]


def test_deployment_has_readiness_probe_port_env_and_one_replica():
    doc = yaml.safe_load(generate_deployment_yaml("demo", "ghcr.io/o/demo:latest", 3000))
    container = doc["spec"]["template"]["spec"]["containers"][0]
    assert doc["spec"]["replicas"] == 1
    assert container["readinessProbe"]["tcpSocket"]["port"] == 3000
    assert {"name": "PORT", "value": "3000"} in container["env"]


def test_task_secrets_not_persisted(monkeypatch):
    from app.db import mongodb

    captured = {}

    class _Col:
        async def find_one(self, *a, **k):
            return None

        async def update_one(self, flt, ops, upsert=False):
            captured.update(ops["$set"])

    class _Db:
        deployments = _Col()

    store = mongodb.MongoDB() if hasattr(mongodb, "MongoDB") else mongodb.db
    store.db = _Db()
    asyncio.run(store.store_deployment_data({"id": "t1", "repo_url": "https://github.com/o/r", "_github_token": "secret", "status": "failed"}))
    assert "_github_token" not in captured
    assert captured["status"] == "failed"
