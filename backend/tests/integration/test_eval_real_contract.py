"""Script response contracts and live evaluation over uvicorn and local upstreams."""
import json
import os
import shutil
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


class ProviderStub(BaseHTTPRequestHandler):
    failures = set()
    terms_first = False
    calls = []

    def log_message(self, *args):
        pass

    def _send(self, body, status=200):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        name = self.path.split('/')[1]
        model = {'groq': 'llama-3.1-8b-instant', 'deepseek': 'deepseek-chat', 'gemini': 'gemini-2.0-flash'}[name]
        models = ['alpha-chat', 'zeta-chat'] if name == 'groq' and self.terms_first else [model]
        self._send({'models': [{'name': 'models/' + model, 'supportedGenerationMethods': ['generateContent']}]} if name == 'gemini' else {'data': [{'id': m} for m in models]})

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', '0'))))
        name = self.path.split('/')[1]
        self.calls.append((name, data.get('model')))
        if name in self.failures:
            self._send({'error': {'message': 'stub rejected key'}}, status=401)
            return
        if name == 'groq' and self.terms_first and data.get('model') == 'alpha-chat':
            self._send({'error': {'code': 'model_terms_required', 'message': 'terms acceptance required'}}, status=400)
            return
        self._send({'candidates': [{'content': {'parts': [{'text': 'local stub'}]}}], 'usageMetadata': {'totalTokenCount': 2}} if name == 'gemini' else {'choices': [{'message': {'content': 'local stub'}}], 'usage': {'total_tokens': 2}})


@pytest.fixture
def real_gateway(tmp_path):
    ProviderStub.failures = set()
    ProviderStub.terms_first = False
    ProviderStub.calls = []
    stub = ThreadingHTTPServer(('127.0.0.1', 0), ProviderStub)
    thread = threading.Thread(target=stub.serve_forever, daemon=True)
    thread.start()
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    preamble = (
        'from dataclasses import replace;import app.providers.model_registry as m;'
        + ''.join(f"m.PROVIDER_SPECS['{p}']=replace(m.PROVIDER_SPECS['{p}'],base_url='http://127.0.0.1:{stub.server_port}/{p}');" for p in ('groq', 'deepseek', 'gemini'))
        + f"import uvicorn;uvicorn.run('app.main:app',host='127.0.0.1',port={port},log_level='critical')"
    )
    env = dict(os.environ, DATABASE_URL=f"sqlite+aiosqlite:///{tmp_path / 'test.db'}",
               ROUTTENER_DATA_DIR=str(tmp_path / 'data'), REDIS_URL='', REQUIRE_API_KEY='false',
               CHAOS_MODE_ENABLED='true', DEMO_MODE_ENABLED='false', ALLOWED_HOSTS='*',
               PYTHONPATH=str(ROOT / 'backend'))
    for name in ('ROUTTENER_EVAL_API_KEY', 'ROUTELLM_EVAL_API_KEY', 'GROQ_API_KEY', 'DEEPSEEK_API_KEY', 'GEMINI_API_KEY'):
        env.pop(name, None)
    with (tmp_path / 'server.log').open('w+') as log:
        proc = subprocess.Popen([sys.executable, '-c', preamble], cwd=ROOT / 'backend', env=env, stdout=log, stderr=subprocess.STDOUT)
        base = f'http://127.0.0.1:{port}'
        try:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    raise AssertionError('gateway exited during startup')
                try:
                    if httpx.get(base + '/health', timeout=1).status_code == 200:
                        break
                except httpx.HTTPError:
                    time.sleep(.1)
            else:
                raise AssertionError('gateway did not become ready')
            yield base, env
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            stub.shutdown()
            stub.server_close()
            thread.join(timeout=2)


def _owner(base):
    with httpx.Client(base_url=base, timeout=20) as client:
        r = client.post('/api/v1/keys/generate', json={'label': 'contract test'})
        assert r.status_code == 201
        key = r.json()['api_key']
        headers = {'X-API-Key': key}
        for provider, fake in [('groq', 'gsk_FAKE000000000000'), ('deepseek', 'sk-FAKE000000000000')]:
            assert client.put('/api/v1/provider-keys/' + provider, headers=headers, json={'api_key': fake}).status_code == 200
        return key


def test_script_fields_exist_on_real_gateway(real_gateway):
    base, _ = real_gateway
    key = _owner(base)
    headers = {'X-API-Key': key}
    with httpx.Client(base_url=base, timeout=30) as client:
        health = client.get('/api/v1/health').json()
        assert isinstance(health['components'], dict)
        assert isinstance(health['components']['database'], str)
        assert isinstance(health['components']['redis'], str)
        providers = client.get('/api/v1/provider-keys', headers=headers).json()
        assert all(isinstance(row['provider_name'], str) and isinstance(row['configured'], bool) for row in providers)
        assert client.get('/api/v1/admin/chaos/status').status_code == 200
        inject = client.post('/api/v1/admin/chaos/inject', json={'provider_name': 'groq', 'duration_seconds': 10})
        assert inject.status_code == 200
        assert isinstance(inject.json()['provider_name'], str)
        assert isinstance(inject.json()['expires_in_seconds'], int)
        route = client.post('/api/v1/route', headers=headers, json={'prompt': 'hello', 'task_type': 'qa'})
        assert route.status_code == 200
        body = route.json()
        assert isinstance(body['success'], bool)
        assert isinstance(body['latency_ms'], (int, float)) and body['latency_ms'] > 0
        assert isinstance(body['tokens_used'], int)
        assert body['model_used'] is None or isinstance(body['model_used'], str)
        assert body['error'] is None or isinstance(body['error'], str)
        assert isinstance(body['fallback_chain_attempted'], list)
        assert all(isinstance(row['provider_name'], str) for row in body['fallback_chain_attempted'])
        logs = client.get('/api/v1/logs', headers=headers).json()
        assert isinstance(logs['logs'], list)
        assert isinstance(logs['total'], int)
        assert client.post('/api/v1/admin/chaos/clear', json={'provider_name': 'groq'}).status_code == 200


def test_live_eval_latency_uses_real_response_and_writes_only_in_copy(real_gateway, tmp_path):
    base, env = real_gateway
    key = _owner(base)
    copy = tmp_path / 'copy'
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', 'data', 'dist', '*.db', '.env'))
    actual = ROOT / 'docs' / 'eval-results.md'
    before = actual.read_bytes() if actual.exists() else None
    run_env = dict(env, ROUTTENER_EVAL_API_KEY=key, PYTHONPATH=str(copy / 'backend'))
    result = subprocess.run([sys.executable, str(copy / 'evals' / 'run_resilience_eval.py'), '--live', '--yes-spend-quota', '--base-url', base, '--n', '2', '--json'], cwd=copy, env=run_env, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stderr
    assert key not in result.stdout + result.stderr
    marker = '{\n  "eval": "resilience"'
    payload = json.loads(result.stdout[result.stdout.index(marker):])
    assert payload['scenarios'][0]['router']['mean_latency_ms'] > 0, payload['scenarios'][0]['router']
    report = (copy / 'docs' / 'eval-results.md').read_text()
    assert 'MODE: LIVE' in report
    assert 'chain entries (may include skipped providers)' in report
    assert payload['scenarios'][0]['router']['successes'] > 0
    assert 'groq' in payload['scenarios'][0]['models_called'] and 'deepseek' in payload['scenarios'][0]['models_called']
    assert (actual.read_bytes() if actual.exists() else None) == before


@pytest.mark.parametrize('failed,expected', [(set(), 0), ({'groq'}, 1), ({'groq', 'deepseek'}, 1)])
def test_provider_checks_real_endpoint_with_stub_answers(real_gateway, tmp_path, failed, expected):
    base, env = real_gateway
    ProviderStub.failures = failed
    ProviderStub.terms_first = not failed
    key = _owner(base)
    copy = tmp_path / 'copy'
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', 'data', 'dist', '*.db', '.env'))
    actual = ROOT / 'docs' / 'eval-results.md'
    before = actual.read_bytes() if actual.exists() else None
    run_env = dict(env, ROUTTENER_EVAL_API_KEY=key, PYTHONPATH=str(copy / 'backend'))
    command = [sys.executable, str(copy / 'evals' / 'run_resilience_eval.py'), '--live', '--yes-spend-quota', '--base-url', base, '--n', '1']
    result = subprocess.run(command, cwd=copy, env=run_env, capture_output=True, text=True, timeout=90)
    assert result.returncode == expected, result.stderr
    output = result.stdout + result.stderr
    assert key not in output
    assert '2 provider check calls (each may try more than one upstream model) + 1 route calls' in output
    for provider in ('groq', 'deepseek'):
        assert f"Provider check {provider}: {'FAIL' if provider in failed else 'PASS'}" in output
    if failed:
        assert 'FATAL: fewer than 2 provider checks passed' in output
        assert 'stub rejected key' in output
    else:
        assert ('groq', 'alpha-chat') in ProviderStub.calls
        assert ('groq', 'zeta-chat') in ProviderStub.calls
    assert (actual.read_bytes() if actual.exists() else None) == before


def test_dry_run_does_not_send_provider_checks(real_gateway, tmp_path):
    base, env = real_gateway
    key = _owner(base)
    ProviderStub.calls.clear()
    run_env = dict(env, ROUTTENER_EVAL_API_KEY=key)
    result = subprocess.run([sys.executable, str(ROOT / 'evals' / 'run_resilience_eval.py'), '--live', '--dry-run', '--yes-spend-quota', '--base-url', base], cwd=ROOT, env=run_env, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stderr
    assert 'would check 2 providers' in result.stdout
    assert ProviderStub.calls == []


def test_skip_provider_check_skips_the_test_endpoint(real_gateway, tmp_path):
    base, env = real_gateway
    key = _owner(base)
    ProviderStub.failures = {'groq', 'deepseek'}
    copy = tmp_path / 'copy'
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', 'data', 'dist', '*.db', '.env'))
    run_env = dict(env, ROUTTENER_EVAL_API_KEY=key, PYTHONPATH=str(copy / 'backend'))
    result = subprocess.run([sys.executable, str(copy / 'evals' / 'run_resilience_eval.py'), '--live', '--yes-spend-quota', '--skip-provider-check', '--base-url', base, '--n', '1'], cwd=copy, env=run_env, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stderr
    assert '0 provider check calls (each may try more than one upstream model) + 1 route calls' in result.stdout
    assert 'Provider check groq:' not in result.stdout
