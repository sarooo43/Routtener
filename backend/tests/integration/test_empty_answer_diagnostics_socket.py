"""Socket-backed Groq reply shapes: from memory, not verified live."""
import json

import httpx
import pytest

from tests.integration.test_eval_real_contract import ProviderStub, _owner, real_gateway  # noqa: F401
from tests.integration.test_eval_answer_socket import check


@pytest.fixture
def reply_stub(monkeypatch):
    state = {'mode': '', 'models': []}

    def get(handler):
        name = handler.path.split('/')[1]
        if name == 'groq':
            handler._send({'data': [{'id': 'openai/gpt-oss-120b'}, {'id': 'openai/gpt-oss-20b'}]})
        else:
            handler._send({'data': [{'id': 'deepseek-chat'}]})

    def post(handler):
        body = json.loads(handler.rfile.read(int(handler.headers['Content-Length'])))
        name = handler.path.split('/')[1]
        if name != 'groq':
            handler._send({'choices': [{'message': {'content': 'ok'}}], 'usage': {'total_tokens': 2}})
            return
        state['models'].append(body.get('model'))
        mode = state['mode']
        usage = {'completion_tokens': 17, 'total_tokens': 20}
        if mode == 'choices':
            handler._send({'choices': [], 'usage': usage})
        else:
            content = None if mode == 'null' else ''
            if mode == 'walk' and body.get('model') == 'openai/gpt-oss-20b':
                content = 'ok'
            handler._send({'choices': [{'message': {'content': content, 'reasoning': 'private reasoning'}, 'finish_reason': 'length'}], 'usage': usage})

    monkeypatch.setattr(ProviderStub, 'do_GET', get)
    monkeypatch.setattr(ProviderStub, 'do_POST', post)
    return state


@pytest.mark.parametrize('mode', ['empty', 'null', 'choices', 'walk'])
def test_groq_empty_shapes_on_socket(real_gateway, reply_stub, mode):
    base, env = real_gateway
    key = _owner(base, ('groq', 'deepseek'))
    reply_stub['mode'] = mode
    code, output = check(base, env, key, 'groq')
    print(f'CASE {mode} models={reply_stub["models"]}\n{output}', end='')
    assert key not in output
    assert 'private reasoning' not in output
    assert code == 1
    assert reply_stub['models'] == ['openai/gpt-oss-120b']
    length = '0' if mode in ('empty', 'walk') else 'unavailable'
    finish = 'unavailable' if mode == 'choices' else 'LENGTH'
    assert (f'model=openai/gpt-oss-120b empty_response: reply_length={length} '
            f'finish_reason={finish} completion_tokens=17') in output


@pytest.mark.parametrize('real_gateway', ['legacy-empty'], indirect=True)
def test_test_endpoint_decorates_legacy_empty_response(real_gateway, reply_stub):
    base, env = real_gateway
    key = _owner(base, ('groq', 'deepseek'))
    reply_stub['mode'] = 'empty'
    response = httpx.post(base + '/api/v1/provider-test/groq', headers={'X-API-Key': key}, timeout=30)
    assert response.status_code == 200
    assert response.json()['verdict'] == 'empty_response'
    assert response.json()['error'] == ('empty_response: reply_length=unavailable '
                                       'finish_reason=unavailable completion_tokens=unavailable')
    assert key not in response.text
    code, output = check(base, env, key, 'groq')
    assert code == 1
    assert ('model=openai/gpt-oss-120b empty_response: reply_length=unavailable '
            'finish_reason=unavailable completion_tokens=unavailable') in output
    assert key not in output and 'private reasoning' not in output


def test_eval_handles_legacy_bare_empty_response_over_socket():
    import os
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class LegacyTestEndpoint(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_POST(self):
            result = ({'key_valid': False, 'error': 'empty_response: private reasoning'}
                      if '/groq' in self.path else {'key_valid': True})
            raw = json.dumps(result).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

    server = ThreadingHTTPServer(('127.0.0.1', 0), LegacyTestEndpoint)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    key = 'rk_TESTONLY00000000000000'
    try:
        code, output = check(f'http://127.0.0.1:{server.server_port}', dict(os.environ), key, 'groq')
        assert code == 1
        assert ('model=unavailable empty_response: reply_length=unavailable '
                'finish_reason=unavailable completion_tokens=unavailable') in output
        assert key not in output and 'private reasoning' not in output
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
