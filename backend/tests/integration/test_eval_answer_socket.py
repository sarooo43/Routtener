"""Eval answer probes over uvicorn and socket upstreams; response shapes from memory, not verified live."""
import os
import subprocess
import sys

import httpx
import pytest

from tests.integration.test_eval_real_contract import ROOT, ProviderStub, _owner, real_gateway  # noqa: F401


@pytest.fixture
def upstream(monkeypatch):
    state = {'mode': 'normal', 'calls': []}
    def post(handler):
        import json
        body = json.loads(handler.rfile.read(int(handler.headers['Content-Length'])))
        name = handler.path.split('/')[1]
        state['calls'].append((name, body))
        mode = state['mode']
        if name == 'groq' and mode in ('groq_empty', 'budget'):
            empty = mode == 'groq_empty' or body.get('max_tokens', 0) < 256
            handler._send({'choices': [{'message': {'content': '' if empty else 'ok', 'reasoning': 'not an answer'}, 'finish_reason': 'length' if empty else 'stop'}], 'usage': {'completion_tokens': 1, 'total_tokens': 2}})
        elif name == 'gemini' and mode == 'gemini_empty':
            handler._send({'candidates': [{'content': {'role': 'model'}, 'finishReason': 'MAX_TOKENS'}], 'usageMetadata': {'candidatesTokenCount': 1, 'totalTokenCount': 2}})
        elif name == 'gemini':
            handler._send({'candidates': [{'content': {'parts': [{'text': 'ok'}]}, 'finishReason': 'STOP'}], 'usageMetadata': {'candidatesTokenCount': 1, 'totalTokenCount': 2}})
        else:
            handler._send({'choices': [{'message': {'content': 'ok'}, 'finish_reason': 'stop'}], 'usage': {'completion_tokens': 1, 'total_tokens': 2}})
    monkeypatch.setattr(ProviderStub, 'do_POST', post)
    return state


def check(base, env, key, provider):
    code = '''import asyncio,os,httpx
from evals.run_resilience_eval import check_provider_answers
async def go():
 async with httpx.AsyncClient(base_url=os.environ['BASE']) as c:
  await check_provider_answers(c, os.environ['KEY'], [os.environ['PROVIDER'], 'deepseek'])
asyncio.run(go())
'''
    runenv = dict(env, BASE=base, KEY=key, PROVIDER=provider,
                  PYTHONPATH=os.pathsep.join((str(ROOT), str(ROOT / 'backend'))))
    result = subprocess.run([sys.executable, '-c', code], cwd=ROOT, env=runenv, capture_output=True, text=True, timeout=60)
    output = result.stdout + result.stderr
    for secret in (key, 'gsk_FAKE000000000000', 'sk-FAKE000000000000', 'AIzaFAKE0000000000000000000000'):
        assert secret not in output
    return result.returncode, output


@pytest.mark.parametrize('provider,mode', [('groq','groq_empty'), ('gemini','gemini_empty'), ('groq','normal'), ('gemini','normal')])
def test_provider_check_socket_cases(real_gateway, upstream, provider, mode):
    base, env = real_gateway
    key = _owner(base, ('groq', 'gemini', 'deepseek'))
    upstream['mode'] = mode
    code, output = check(base, env, key, provider)
    print(f'CASE {provider} {mode}\n{output}', end='')
    assert code == (1 if mode != 'normal' else 0)
    assert f"Provider check {provider}: {'FAIL' if mode != 'normal' else 'PASS'}" in output
    call = next(body for name, body in upstream['calls'] if name == provider)
    if provider == 'groq':
        assert call['max_tokens'] == 256
        assert call['messages'][0]['content'] == 'ping'
    else:
        assert call['generationConfig']['maxOutputTokens'] == 256
        assert call['contents'][0]['parts'][0]['text'] == 'ping'
    if mode != 'normal':
        model = 'llama-3.1-8b-instant' if provider == 'groq' else 'gemini-2.0-flash'
        finish = 'LENGTH' if provider == 'groq' else 'MAX_TOKENS'
        assert f'model={model} empty_response: reply_length=0 finish_reason={finish} completion_tokens=1' in output
        assert 'not an answer' not in output


def test_answer_check_budget_allows_reasoning_then_text(real_gateway, upstream):
    base, env = real_gateway
    key = _owner(base, ('groq', 'deepseek'))
    upstream['mode'] = 'budget'
    code, output = check(base, env, key, 'groq')
    assert code == 0 and 'Provider check groq: PASS' in output
    assert next(body for name, body in upstream['calls'] if name == 'groq')['max_tokens'] == 256


@pytest.mark.parametrize('provider,mode', [('groq', 'groq_empty'), ('gemini', 'gemini_empty'), ('groq', 'normal'), ('gemini', 'normal')])
def test_dashboard_and_check_agree_on_same_reply(real_gateway, upstream, provider, mode):
    base, env = real_gateway
    key = _owner(base, ('groq', 'gemini', 'deepseek'))
    upstream['mode'] = mode
    with httpx.Client(base_url=base, timeout=30) as client:
        result = client.post('/api/v1/provider-test/' + provider, headers={'X-API-Key': key})
    assert result.status_code == 200
    body = result.json()
    assert body['key_valid'] is (mode == 'normal')
    assert key not in result.text
    for secret in ('gsk_FAKE000000000000', 'sk-FAKE000000000000', 'AIzaFAKE0000000000000000000000'):
        assert secret not in result.text
    code, output = check(base, env, key, provider)
    assert (f'Provider check {provider}: PASS' in output) == body['key_valid']
    assert code == (0 if body['key_valid'] else 1)
