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


def test_name_inventory_classification_via_real_subprocess():
    process = subprocess.run([sys.executable, '-c',
        'import pathlib,sys;sys.stdout.write(pathlib.Path(sys.argv[1]).read_text())',
        str(ROOT / 'docs/audit/name-inventory.md')], capture_output=True, text=True, timeout=10)
    assert process.returncode == 0
    text = process.stdout
    assert 'Scope: UI strings, README, docs, CLI output. Not a complete audit.' in text
    marks = {
        'README.md:409': 'keep', 'backend/app/db/session.py:91': 'keep',
        'backend/app/local.py:63': 'keep', 'benchmark/generate_report.py:4': 'not-visible',
        'benchmark/generate_report.py:109': 'not-visible', 'benchmark/generate_report.py:111': 'not-visible',
        'benchmark/generate_report.py:216': 'not-visible', 'evals/harness.py:357': 'not-visible',
        'frontend/src/api/client.ts:100': 'not-visible', 'frontend/src/api/client.ts:108': 'not-visible',
    }
    for path, mark in marks.items():
        assert f'| `{path}` | {mark} |' in text
    assert '| REVIEW |' not in text
