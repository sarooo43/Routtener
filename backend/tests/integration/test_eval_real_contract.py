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
def real_gateway(tmp_path, request):
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
    if getattr(request, 'param', None) == 'auth':
        env['REQUIRE_API_KEY'] = 'true'
    with (tmp_path / 'server.log').open('w+') as log:
        proc = subprocess.Popen([sys.executable, '-c', preamble], cwd=ROOT / 'backend', env=env, stdout=log, stderr=subprocess.STDOUT)
        base = f'http://127.0.0.1:{port}'
        ProviderStub.gateway_process = proc
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


def _owner(base, providers=("groq", "deepseek")):
    with httpx.Client(base_url=base, timeout=20) as client:
        r = client.post('/api/v1/keys/generate', json={'label': 'contract test'})
        assert r.status_code == 201
        key = r.json()['api_key']
        assert isinstance(key, str) and key.startswith('rk_')
        headers = {'X-API-Key': key}
        for provider, fake in [('groq', 'gsk_FAKE000000000000'), ('deepseek', 'sk-FAKE000000000000'), ('gemini', 'AIzaFAKE0000000000000000000000')]:
            if provider not in providers:
                continue
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
        status = client.get('/api/v1/admin/chaos/status')
        assert status.status_code == 200 and isinstance(status.json()['active_chaos'], list)
        probe = client.post('/api/v1/provider-test/groq', headers=headers)
        assert probe.status_code == 200
        assert isinstance(probe.json()['key_valid'], bool)
        assert isinstance(probe.json()['verdict'], str)
        assert probe.json()['error'] is None or isinstance(probe.json()['error'], str)
        ProviderStub.failures = {'deepseek'}
        failed_probe = client.post('/api/v1/provider-test/deepseek', headers=headers)
        assert failed_probe.status_code == 200
        assert failed_probe.json()['key_valid'] is False
        assert isinstance(failed_probe.json()['verdict'], str)
        assert isinstance(failed_probe.json()['error'], str)
        assert 'stub rejected key' in failed_probe.json()['error']
        ProviderStub.failures = set()
        bad = client.post('/api/v1/admin/chaos/inject', json={'provider_name': 'nonexistent', 'duration_seconds': 10})
        assert bad.status_code == 400 and isinstance(bad.json()['detail'], str)
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


def test_one_detected_provider_is_still_checked_before_fatal(real_gateway):
    base, env = real_gateway
    key = _owner(base, ('groq',))
    run_env = dict(env, ROUTTENER_EVAL_API_KEY=key)
    result = subprocess.run([sys.executable, str(ROOT / 'evals' / 'run_resilience_eval.py'), '--live', '--yes-spend-quota', '--base-url', base, '--n', '1'], cwd=ROOT, env=run_env, capture_output=True, text=True, timeout=90)
    assert result.returncode != 0
    assert 'Provider check groq: PASS' in result.stdout
    assert 'FATAL: fewer than 2 provider checks passed' in result.stderr
    assert key not in result.stdout + result.stderr


def test_live_results_label_with_actual_upstream_failure_and_fallback(real_gateway, tmp_path):
    base, env = real_gateway
    key = _owner(base, ('groq', 'deepseek', 'gemini'))
    ProviderStub.failures = {'gemini'}
    copy = tmp_path / 'copy'
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', 'data', 'dist', '*.db', '.env'))
    run_env = dict(env, ROUTTENER_EVAL_API_KEY=key, PYTHONPATH=str(copy / 'backend'))
    result = subprocess.run([sys.executable, str(copy / 'evals' / 'run_resilience_eval.py'), '--live', '--yes-spend-quota', '--base-url', base, '--n', '1', '--json'], cwd=copy, env=run_env, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout[result.stdout.index('{\n  "eval": "resilience"'):])
    assert payload['scenarios'][0]['router']['successes'] == 1
    assert sum(name == 'deepseek' for name, _ in ProviderStub.calls) >= 2
    assert sum(name == 'gemini' for name, _ in ProviderStub.calls) >= 2
    assert 'chain entries (may include skipped providers)' in (copy / 'docs' / 'eval-results.md').read_text()
    assert key not in result.stdout + result.stderr


@pytest.mark.parametrize('real_gateway', ['auth'], indirect=True)
@pytest.mark.parametrize('supplied', [False, True], ids=['minted', 'supplied'])
@pytest.mark.parametrize('event', ['success', 'fatal', 'exception', 'sigint', 'server_death', 'preflight_sigint', 'preflight_death'])
def test_exit_matrix_real_process(real_gateway, tmp_path, supplied, event):
    """Forward through a real socket while witnessing key ownership and cleanup."""
    import signal

    base, env = real_gateway
    gateway_process = ProviderStub.gateway_process
    state = {'key': None, 'deletes': 0, 'deleted': False}
    entered = threading.Event()
    release = threading.Event()
    if supplied:
        state['key'] = _owner(base, () if event == 'fatal' else ('groq', 'deepseek'))

    class Proxy(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def forward(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            if self.command == 'DELETE' and self.path == '/api/v1/keys/me':
                state['deletes'] += 1
            if ((self.path == '/api/v1/route' and event in ('sigint', 'server_death')) or
                (self.path == '/api/v1/provider-keys' and event in ('preflight_sigint', 'preflight_death'))):
                entered.set()
                release.wait(30)
            if self.path == '/api/v1/route' and event == 'exception':
                status, content = 500, b'{"detail":"local scenario failure"}'
            else:
                try:
                    response = httpx.request(self.command, base + self.path, content=body,
                                             headers={'Content-Type': 'application/json',
                                                      'X-API-Key': self.headers.get('X-API-Key', '')}, timeout=10)
                    status, content = response.status_code, response.content
                    if self.path == '/api/v1/keys/generate' and status == 201:
                        state['key'] = response.json()['api_key']
                        if event != 'fatal':
                            headers = {'X-API-Key': state['key']}
                            for provider, fake in [('groq', 'gsk_FAKE000000000000'), ('deepseek', 'sk-FAKE000000000000')]:
                                saved = httpx.put(base + '/api/v1/provider-keys/' + provider,
                                                  headers=headers, json={'api_key': fake}, timeout=20)
                                if saved.status_code != 200:
                                    raise AssertionError('test-only provider setup failed')
                    if self.command == 'DELETE' and self.path == '/api/v1/keys/me' and status == 200:
                        state['deleted'] = True
                except httpx.HTTPError:
                    status, content = 502, b'{}'
            try:
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except (BrokenPipeError, ConnectionResetError):
                pass

        do_GET = forward
        do_POST = forward
        do_DELETE = forward

    proxy = ThreadingHTTPServer(('127.0.0.1', 0), Proxy)
    thread = threading.Thread(target=proxy.serve_forever, daemon=True)
    thread.start()
    copy = tmp_path / 'copy'
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', 'data', 'dist', '*.db', '.env'))
    run_env = dict(env, PYTHONPATH=str(copy / 'backend'))
    if supplied:
        run_env['ROUTTENER_EVAL_API_KEY'] = state['key']
    else:
        run_env.pop('ROUTTENER_EVAL_API_KEY', None)
        run_env.pop('ROUTELLM_EVAL_API_KEY', None)
    bootstrap = "import runpy,signal,sys;signal.signal(signal.SIGINT,signal.default_int_handler);p=sys.argv.pop(1);runpy.run_path(p,run_name='__main__')"
    process = subprocess.Popen([sys.executable, '-c', bootstrap, str(copy / 'evals' / 'run_resilience_eval.py'),
                                '--live', '--yes-spend-quota', '--skip-provider-check', '--n', '1',
                                '--base-url', f'http://127.0.0.1:{proxy.server_port}'],
                               cwd=copy, env=run_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        if event in ('sigint', 'server_death', 'preflight_sigint', 'preflight_death'):
            assert entered.wait(30), 'eval did not reach the expected stage'
            if event in ('sigint', 'preflight_sigint'):
                process.send_signal(signal.SIGINT)
            else:
                gateway_process.terminate()
                gateway_process.wait(timeout=10)
                release.set()
        stdout, stderr = process.communicate(timeout=40)
        assert state['key'] not in stdout + stderr
        assert (process.returncode == 0) == (event == 'success')
        if supplied:
            assert state['deletes'] == 0
            if event not in ('server_death', 'preflight_death'):
                assert httpx.get(base + '/api/v1/keys/me', headers={'X-API-Key': state['key']}).status_code == 200
        elif event in ('server_death', 'preflight_death'):
            assert state['deletes'] == 1 and not state['deleted']
            assert 'could not revoke transient API key ' + state['key'][:8] in stderr
        else:
            assert state['deletes'] == 1 and state['deleted']
            assert 'API key: revoked' in stdout
            assert httpx.get(base + '/api/v1/keys/me', headers={'X-API-Key': state['key']}).status_code == 401
    finally:
        release.set()
        if process.poll() is None:
            process.kill()
            process.communicate()
        proxy.shutdown()
        proxy.server_close()
        thread.join(timeout=2)


@pytest.mark.parametrize('real_gateway', ['auth'], indirect=True)
@pytest.mark.parametrize('supplied', [False, True], ids=['minted', 'supplied'])
def test_invalid_url_does_not_mint_or_revoke(real_gateway, supplied):
    base, env = real_gateway
    key = _owner(base, ()) if supplied else None
    run_env = dict(env)
    if key:
        run_env['ROUTTENER_EVAL_API_KEY'] = key
    result = subprocess.run([sys.executable, str(ROOT / 'evals' / 'run_resilience_eval.py'),
                             '--live', '--yes-spend-quota', '--base-url', 'http://:8000'],
                            cwd=ROOT, env=run_env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 2
    assert 'FATAL: --base-url is not a valid URL' in result.stderr
    assert 'minting a throwaway key' not in result.stdout
    assert 'API key: revoked' not in result.stdout
    if key:
        assert key not in result.stdout + result.stderr
        assert httpx.get(base + '/api/v1/keys/me', headers={'X-API-Key': key}).status_code == 200
