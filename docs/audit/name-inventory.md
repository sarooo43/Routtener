# Name inventory

Scope: UI strings, README, docs, CLI output. Not a complete audit.

OBSERVED: This conservative source search includes non-visible identifiers as well as visible text; it excludes test files. The ten previously unresolved entries are classified below; the wider search is not a complete audit. Historical evidence outside CHANGELOG is retained rather than rewritten. Protected `docs/deploy/` is included for reference and was not edited.

| Source:line | Mark | Reason |
|---|---|---|
| `CHANGELOG.md:8` | INTENTIONAL | rename history or compatibility |
| `CHANGELOG.md:9` | INTENTIONAL | rename history or compatibility |
| `CHANGELOG.md:32` | INTENTIONAL | rename history or compatibility |
| `CHANGELOG.md:58` | INTENTIONAL | rename history or compatibility |
| `CHANGELOG.md:62` | INTENTIONAL | rename history or compatibility |
| `CHANGELOG.md:65` | INTENTIONAL | rename history or compatibility |
| `CHANGELOG.md:71` | INTENTIONAL | rename history or compatibility |
| `CHANGELOG.md:72` | INTENTIONAL | rename history or compatibility |
| `CHANGELOG.md:109` | INTENTIONAL | rename history or compatibility |
| `CHANGELOG.md:135` | INTENTIONAL | rename history or compatibility |
| `CONTRIBUTING.md:10` | INTENTIONAL | rename history and upstream disambiguation |
| `CONTRIBUTING.md:11` | INTENTIONAL | rename history and upstream disambiguation |
| `CONTRIBUTING.md:64` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `README.md:14` | INTENTIONAL | rename history and upstream disambiguation |
| `README.md:16` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `README.md:18` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `README.md:19` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `README.md:20` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `README.md:241` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `README.md:263` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `README.md:374` | INTENTIONAL | rename history and upstream disambiguation |
| `README.md:409` | keep | Example PostgreSQL database name; not project branding. |
| `README.md:581` | INTENTIONAL | rename history and upstream disambiguation |
| `backend/app/api/openai_compat_routes.py:35` | INTENTIONAL | rename history and upstream disambiguation |
| `backend/app/api/openai_compat_routes.py:37` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/api/openai_compat_routes.py:115` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/api/openai_compat_routes.py:126` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/api/openai_compat_routes.py:138` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/api/openai_compat_routes.py:139` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/api/openai_compat_routes.py:256` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/api/openai_compat_routes.py:263` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/config.py:13` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/config.py:53` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/config.py:56` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/config.py:59` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/config.py:98` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/config.py:143` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/config.py:145` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/config.py:165` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/config.py:173` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/db/session.py:68` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/db/session.py:90` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/db/session.py:91` | keep | Example PostgreSQL database name in diagnostic guidance. |
| `backend/app/env_compat.py:3` | INTENTIONAL | rename history and upstream disambiguation |
| `backend/app/env_compat.py:4` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/env_compat.py:10` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/env_compat.py:11` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/env_compat.py:27` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/env_compat.py:34` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/identity.py:4` | INTENTIONAL | rename history and upstream disambiguation |
| `backend/app/identity.py:5` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/identity.py:8` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/identity.py:12` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/identity.py:13` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/identity.py:29` | INTENTIONAL | rename history and upstream disambiguation |
| `backend/app/local.py:23` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/local.py:29` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/local.py:50` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/local.py:53` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/local.py:63` | keep | Existing per-user data-directory identifier; changing it breaks compatibility. |
| `backend/app/local.py:104` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/local.py:111` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/main.py:9` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/providers/model_registry.py:1039` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/providers/model_registry.py:1045` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/runtime.py:11` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/runtime.py:14` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `backend/app/runtime.py:33` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `benchmark/generate_report.py:4` | not-visible | Internal module docstring describing result keys. |
| `benchmark/generate_report.py:59` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `benchmark/generate_report.py:84` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `benchmark/generate_report.py:109` | not-visible | Internal result dictionary key. |
| `benchmark/generate_report.py:111` | not-visible | Internal result dictionary key. |
| `benchmark/generate_report.py:216` | not-visible | Internal plotting dataset keys. |
| `benchmark/run_benchmark.py:18` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `benchmark/run_benchmark.py:398` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `docs/architecture.md:152` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `docs/audit/FINAL-REPORT.md:3` | INTENTIONAL | historical audit evidence or protected identifier |
| `docs/audit/FINAL-REPORT.md:164` | INTENTIONAL | historical audit evidence or protected identifier |
| `docs/audit/FINAL-REPORT.md:173` | INTENTIONAL | historical audit evidence or protected identifier |
| `docs/deploy/CLOUDFLARE.md:1` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:3` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:11` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:168` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:179` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:184` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:185` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:200` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:211` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:221` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:228` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:251` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:255` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:256` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:264` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:265` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:286` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:304` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:325` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/CLOUDFLARE.md:326` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:15` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:19` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:52` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:64` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:96` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:112` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:129` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:130` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:131` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:144` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:152` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:153` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:166` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:195` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:200` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/DEPLOY_WALKTHROUGH.md:208` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:3` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:8` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:19` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:38` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:70` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:73` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:86` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:91` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:100` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:105` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:117` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:121` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:126` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:134` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:149` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:150` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:163` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:167` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:168` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HTTPS_AND_WEBHOOKS.md:183` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:1` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:9` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:11` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:31` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:46` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:66` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:67` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:70` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:72` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:75` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:115` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:122` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:124` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:125` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:189` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:221` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:224` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/HUGGINGFACE_AND_MANAGED.md:231` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/README.md:10` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/README.md:17` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:1` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:56` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:135` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:141` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:151` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:152` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:169` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:173` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:176` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:177` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:183` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:204` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:217` | INTENTIONAL | protected archived deploy file |
| `docs/deploy/VERIFICATION.md:228` | INTENTIONAL | protected archived deploy file |
| `docs/running-the-live-eval.md:76` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `docs/testing.md:60` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `docs/verification.md:99` | INTENTIONAL | historical audit evidence or protected identifier |
| `docs/verification.md:118` | INTENTIONAL | historical audit evidence or protected identifier |
| `docs/verification.md:237` | INTENTIONAL | historical audit evidence or protected identifier |
| `docs/verification.md:249` | INTENTIONAL | historical audit evidence or protected identifier |
| `docs/verification.md:370` | INTENTIONAL | historical audit evidence or protected identifier |
| `docs/verification.md:392` | INTENTIONAL | historical audit evidence or protected identifier |
| `docs/verification.md:396` | INTENTIONAL | historical audit evidence or protected identifier |
| `docs/verification.md:420` | INTENTIONAL | historical audit evidence or protected identifier |
| `evals/harness.py:357` | not-visible | Source comment about secret redaction. |
| `evals/run_resilience_eval.py:80` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `evals/run_resilience_eval.py:84` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `evals/run_resilience_eval.py:90` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/README.md:7` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/README.md:8` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/README.md:11` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/call_routellm.mjs:3` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/call_routellm.mjs:4` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/call_routellm.mjs:5` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/call_routellm.mjs:7` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/call_routellm.sh:4` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/call_routellm.sh:7` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/call_routellm.sh:8` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/receiver.py:5` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/receiver.py:6` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/receiver.py:41` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/receiver.py:42` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `examples/webhook/receiver.py:44` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/api/client.ts:100` | not-visible | TypeScript source comment, not UI text. |
| `frontend/src/api/client.ts:108` | not-visible | TypeScript source comment, not UI text. |
| `frontend/src/api/keyStorage.ts:19` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/api/keyStorage.ts:20` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/api/keyStorage.ts:21` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/api/onboarding.ts:12` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/api/onboarding.ts:13` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/api/onboarding.ts:14` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/api/workerDetail.ts:5` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/appInfo.ts:4` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/appInfo.ts:5` | INTENTIONAL | rename history and upstream disambiguation |
| `frontend/src/appInfo.ts:8` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/appInfo.ts:9` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/appInfo.ts:18` | INTENTIONAL | rename history and upstream disambiguation |
| `frontend/src/buildInfo.ts:4` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/buildInfo.ts:9` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/buildInfo.ts:12` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/buildInfo.ts:13` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ErrorState.tsx:51` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/Layout.tsx:9` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:109` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:128` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:189` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:214` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:233` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:255` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:287` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:322` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:370` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:382` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:399` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:411` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:423` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:444` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/ModelExplorerPanel.tsx:461` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/components/NoProviderKeyBanner.tsx:7` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/config.ts:13` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `frontend/src/pages/ProviderKeys.tsx:462` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `run.py:49` | INTENTIONAL | compatibility name, protected identifier or source reference |
| `run.py:599` | INTENTIONAL | compatibility name, protected identifier or source reference |

OBSERVED: STALE occurrences corrected in this branch: legacy planning document titles and prose (`AGENTS.md.txt`, `doc/prd.md.txt`, `doc/README.md.txt`), the checkout command in `CONTRIBUTING.md`, and the header in `backend/requirements-dev.txt`. Real-subprocess tests and mutations cover these changes.
