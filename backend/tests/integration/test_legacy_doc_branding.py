"""User-visible legacy planning documents, fetched from a real subprocess."""
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize('path,expected', [
    ('AGENTS.md.txt', '# Project: Routtener'),
    ('doc/prd.md.txt', 'Project Name: Routtener'),
    ('doc/README.md.txt', '# 🔀 Routtener'),
    ('CONTRIBUTING.md', 'cd Routtener'),
    ('backend/requirements-dev.txt', '# Routtener backend — development/test dependencies.'),
])
def test_legacy_docs_use_current_project_name(path, expected):
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    process = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1'],
                               cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                response = httpx.get(f'http://127.0.0.1:{port}/{path}', timeout=1)
                break
            except httpx.HTTPError:
                time.sleep(.1)
        else:
            raise AssertionError('document server failed to start')
        assert response.status_code == 200
        assert expected in response.text
    finally:
        process.terminate()
        process.wait(timeout=10)
