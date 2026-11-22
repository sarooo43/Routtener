"""Exercise the generic edge explanation in a real subprocess over HTTP."""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[3]


def test_generic_bad_request_explanation_over_real_socket():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    code = '''from fastapi import FastAPI
from app.core.error_messages import explain
import uvicorn
app = FastAPI()
@app.get('/')
def explain_error():
    return {'error': explain('unexpected_error: HTTP 400 upstream policy declined', 'deepseek')}
uvicorn.run(app, host='127.0.0.1', port=PORT, log_level='critical')
'''.replace('PORT', str(port))
    process = subprocess.Popen([sys.executable, '-c', code], cwd=ROOT / 'backend',
                               env=dict(os.environ, PYTHONPATH=str(ROOT / 'backend')),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                response = httpx.get(f'http://127.0.0.1:{port}/', timeout=1)
                break
            except httpx.HTTPError:
                time.sleep(.1)
        else:
            raise AssertionError('explanation server did not start')
        assert response.status_code == 200
        assert response.json()['error'] == 'bad_request: deepseek rejected the request (unexpected_error: HTTP 400 upstream policy declined).'
    finally:
        process.terminate()
        process.wait(timeout=10)
