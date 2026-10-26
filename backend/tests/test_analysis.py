"""Detection and generation checks over the testbed sample apps."""
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "testbed"))
APPS_DIR = os.path.join(REPO, "testbed", "apps")

import run_case  # noqa: E402

APPS = sorted(d for d in os.listdir(APPS_DIR) if os.path.isdir(os.path.join(APPS_DIR, d)))


@pytest.mark.parametrize("name", APPS)
def test_detect_and_generate(name, tmp_path):
    result = run_case.run_case(os.path.join(APPS_DIR, name), str(tmp_path / "ws"))
    assert result["detect_ok"], result["checks"]
    assert result["expose"] is not None, "generated Dockerfile has no EXPOSE"
