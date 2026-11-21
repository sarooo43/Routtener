"""Provider contracts over real sockets; no live provider credentials."""
import json
import hashlib
import sqlite3
import os
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[3]
ORPHEUS = 'canopylabs/orpheus-v1-english'
TERMS_MESSAGE = ('The model `canopylabs/orpheus-v1-english` requires terms acceptance. '
                 'Please have the org admin accept the terms at '
                 'https://console.groq.com/playground?model=canopylabs%2Forpheus-v1-english')


@pytest.fixture
def gateway(tmp_path, request):
    state = {'models': ['aaa-chat', 'zzz-chat', ORPHEUS, 'whisper-large-v3', 'text-embedding-3'],
             'fail': set(), 'attempts': [], 'message_only': False, 'generic': False}
    class Stub(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def send(self, data, status=200):
            body = json.dumps(data).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self):
            self.send({'object': 'list', 'data': [{'id': m, 'object': 'model', 'active': True, 'owned_by': 'stub'} for m in state['models']]})
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            model = body['model']
            state['attempts'].append(model)
            if model in state['fail'] and state['generic']:
                self.send({'error': {'message': 'Request rejected by policy; token=gsk_FAKE000000000000'}}, 400)
            elif model in state['fail']:
                err = {'message': TERMS_MESSAGE, 'type': 'invalid_request_error'}
                if not state['message_only']:
                    err['code'] = 'model_terms_required'
                self.send({'error': err}, 400)
            else:
                self.send({'choices': [{'message': {'content': 'ok'}}], 'usage': {'total_tokens': 2}})
    server = ThreadingHTTPServer(('127.0.0.1', 0), Stub)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = dict(os.environ, DATABASE_URL=f'sqlite+aiosqlite:///{tmp_path}/db',
               ROUTTENER_DATA_DIR=str(tmp_path), REDIS_URL='', REQUIRE_API_KEY='false',
               ALLOWED_HOSTS='*', DEMO_MODE_ENABLED='false', PYTHONPATH=str(ROOT / 'backend'))
    for name in ('GROQ_API_KEY', 'GROQ_MODEL', 'DEEPSEEK_API_KEY', 'GEMINI_API_KEY'):
        env.pop(name, None)
    if getattr(request, 'param', None) == 'orpheus':
        env['GROQ_MODEL'] = ORPHEUS
    code = ("from dataclasses import replace;import app.providers.model_registry as m;"
            f"m.PROVIDER_SPECS['groq']=replace(m.PROVIDER_SPECS['groq'],base_url='http://127.0.0.1:{server.server_port}');"
            f"import uvicorn;uvicorn.run('app.main:app',host='127.0.0.1',port={port},log_level='critical')")
    process = subprocess.Popen([sys.executable, '-c', code], cwd=ROOT / 'backend', env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f'http://127.0.0.1:{port}'
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                if httpx.get(base + '/health', timeout=.5).status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(.1)
        else:
            raise AssertionError('gateway did not start')
        with httpx.Client(base_url=base, timeout=30) as client:
            key = client.post('/api/v1/keys/generate', json={'label': 'local'}).json()['api_key']
            client.headers['X-API-Key'] = key
            assert client.put('/api/v1/provider-keys/groq', json={'api_key': 'gsk_FAKE000000000000'}).status_code == 200
            if getattr(request, 'param', None) == 'stale':
                process.terminate()
                process.wait(timeout=10)
                process = subprocess.Popen([sys.executable, '-c', code], cwd=ROOT / 'backend', env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                for _ in range(200):
                    try:
                        if httpx.get(base + '/health', timeout=.5).status_code == 200:
                            break
                    except httpx.HTTPError:
                        time.sleep(.1)
                else:
                    raise AssertionError('gateway did not restart')
                fingerprint = hashlib.sha256(b'gsk_FAKE000000000000').hexdigest()[:16]
                with sqlite3.connect(tmp_path / 'db') as db:
                    db.execute('INSERT OR REPLACE INTO discovered_models (provider, key_fingerprint, models_json, fetched_at) VALUES (?, ?, ?, ?)',
                               ('groq', fingerprint, json.dumps([ORPHEUS, 'aaa-chat']), time.time()))
            yield client, state
    finally:
        process.terminate()
        process.wait(timeout=10)
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_non_chat_models_excluded_from_explorer_and_pin(gateway):
    client, state = gateway
    response = client.get('/api/v1/provider-keys/groq/models')
    assert response.status_code == 200
    ids = {m['id'] for m in response.json()['models']}
    assert {'aaa-chat', 'zzz-chat'} <= ids
    assert not {ORPHEUS, 'whisper-large-v3', 'text-embedding-3'} & ids
    assert client.put('/api/v1/provider-keys/groq/model', json={'model_id': ORPHEUS}).status_code == 422


@pytest.mark.parametrize('message_only', [False, True])
def test_terms_400_walks_and_preserves_first_failure(gateway, message_only):
    client, state = gateway
    state['fail'] = {'aaa-chat'}
    state['message_only'] = message_only
    response = client.post('/api/v1/route', json={'prompt': 'hello', 'task_type': 'qa'})
    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True and body['model_used'] == 'groq'
    assert state['attempts'] == ['aaa-chat', 'zzz-chat']
    assert 'model_terms_required' in body['error']
    assert 'accept terms' in body['error'].lower()
    assert 'bug in how' not in body['error']


def test_dashboard_test_shows_terms_error(gateway):
    client, state = gateway
    state['fail'] = {'aaa-chat', 'zzz-chat'}
    response = client.post('/api/v1/provider-test/groq')
    assert response.status_code == 200
    data = response.json()
    assert data['key_valid'] is False
    assert 'model_terms_required' in data['error']
    assert 'accept terms' in data['error'].lower()
    assert 'bug in how' not in data['error']


@pytest.mark.parametrize('gateway', ['orpheus'], indirect=True)
def test_existing_operator_override_orpheus_reports_and_walks(gateway):
    client, state = gateway
    state['fail'] = {ORPHEUS}
    response = client.post('/api/v1/route', json={'prompt': 'hello', 'task_type': 'qa'})
    body = response.json()
    assert body['success'] is True and body['model_used'] == 'groq'
    assert state['attempts'] == [ORPHEUS, 'aaa-chat']
    assert body['error'].startswith('model_terms_required:')
    assert ORPHEUS in body['error']


def test_generic_400_is_neutral_and_redacted(gateway):
    client, state = gateway
    state['fail'] = {'aaa-chat'}
    state['generic'] = True
    response = client.post('/api/v1/route', json={'prompt': 'hello', 'task_type': 'qa'})
    body = response.json()
    assert body['success'] is False
    assert 'rejected the request (HTTP 400)' in body['error']
    assert 'Request rejected by policy' in body['error']
    assert 'bug in how' not in body['error']
    assert 'gsk_FAKE000000000000' not in body['error']


@pytest.mark.parametrize('gateway', ['stale'], indirect=True)
def test_old_persisted_catalog_cannot_expose_filtered_model(gateway):
    client, state = gateway
    response = client.get('/api/v1/provider-keys/groq/models')
    assert response.status_code == 200
    ids = [model['id'] for model in response.json()['models']]
    assert ids == ['aaa-chat']
