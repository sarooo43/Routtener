# Eval and benchmark response-field audit

OBSERVED: HTTP consumers are `run_resilience_eval.py`, `run_benchmark.py`,
and their shared `harness.py`. Other eval result dictionaries are local objects,
not backend HTTP responses. `test_script_fields_exist_on_real_gateway` exercises
the shapes below with a real uvicorn gateway and local upstream, including
both a successful and a failed dashboard provider check.

| Consumer file:line | Backend response field | Definition file:line | Type |
|---|---|---|---|
| evals/run_resilience_eval.py:423 | provider-keys[].provider_name | backend/app/api/provider_keys_routes.py:73 | string |
| evals/run_resilience_eval.py:423 | provider-keys[].configured | backend/app/api/provider_keys_routes.py:74 | boolean |
| evals/run_resilience_eval.py:440; benchmark/run_benchmark.py:310 | keys/generate.api_key | backend/app/api/keys_routes.py:33 | string |
| evals/run_resilience_eval.py:516 | provider-test.key_valid | backend/app/api/provider_test_routes.py:90 | boolean |
| evals/run_resilience_eval.py:520 | provider-test.error | backend/app/api/provider_test_routes.py:94 | string or null |
| evals/run_resilience_eval.py:520 | provider-test.verdict | backend/app/api/provider_test_routes.py:88 | string |
| evals/run_resilience_eval.py:574; benchmark/run_benchmark.py:237,242 | route.success | backend/app/api/routes.py:168 | boolean |
| evals/run_resilience_eval.py:575 | route.latency_ms | backend/app/api/routes.py:173 | number |
| evals/run_resilience_eval.py:576 | route.fallback_chain_attempted | backend/app/api/routes.py:172 | list of attempt objects |
| evals/run_resilience_eval.py:581 | route.fallback_chain_attempted[].provider_name | backend/app/api/routes.py:158 | string |
| evals/run_resilience_eval.py:578; benchmark/run_benchmark.py:233 | route.model_used | backend/app/api/routes.py:170 | string or null, provider name |
| benchmark/run_benchmark.py:232 | route.tokens_used | backend/app/api/routes.py:174 | integer |
| benchmark/run_benchmark.py:242 | route.error | backend/app/api/routes.py:176 | string or null |
| benchmark/run_benchmark.py:157 | health.components | backend/app/api/routes.py:81–87,138 | string-to-string object |
| benchmark/run_benchmark.py:183 | chaos/inject.provider_name | backend/app/api/chaos_routes.py:67 | string |
| benchmark/run_benchmark.py:184–186 | chaos/inject.expires_in_seconds | backend/app/api/chaos_routes.py:68 | integer |
| evals/harness.py:393–399 | HTTP status and raw body, including error `detail` | backend/app/api/chaos_routes.py:83 (example) | integer status; response text; detail string for this example |

OBSERVED: the live eval uses the chaos-status HTTP status, not its JSON
fields; chaos clear is likewise status-only. No production script under
`evals/` or `benchmark/` reads `/api/v1/logs`; the contract test additionally
checks its `total` and `logs` fields (`backend/app/api/routes.py:228–230`).
The benchmark's `_safe_json` displays a whole error body rather than reading
individual fields. Its latency metric is client-side wall time, not the route
response's `latency_ms`.
