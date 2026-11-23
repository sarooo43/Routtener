# Cleanup inventory — Phase 1

OBSERVED: Base `origin/main` was `275d6191bd67c044dc6c9e71123daf0de2c0a767`; no files are proposed for deletion. This is a decision report, not a deletion authorization. The current branch is for the report only.

## Scope and method

- OBSERVED: `git ls-files` listed 339 tracked files; `git ls-files --others --exclude-standard` listed no untracked, non-ignored files before this report was created.
- The 76-row table is a **conservative superset** of the files outside the expressly protected prefixes/names. It also includes protected or apparently needed entries to make the boundary visible; these are KEEP, never deletion candidates. The other 263 tracked files are protected by the named roots, tests, explicit names, or related requirements.
- `docs/audit/` is OWNER DECIDES as requested even when referenced. OWNER DECIDES is not permission to delete: inbound references and protected/linked docs must still be preserved unless the owner resolves the dependency without violating the protected scope.
- The seven `doc/*.txt` files are historical, potentially overlapping planning documents, not proved disposable; manuals, architecture and testing evidence are retained. The one-byte `docs/image` has no known purpose, so OWNER DECIDES rather than guessing it is generated. `frontend/public/icons.svg` has no literal filename hit but Vite can copy public assets to the staged frontend build: KEEP. Archived cloud deployment docs are excluded from this inventory because `docs/deploy/` is frozen; the referenced Worker and config are KEEP.
- Filename search results below are **possible** references, not necessarily semantic inbound links: fixed-string matching can hit an unrelated basename or path prefix. Absence of a literal match does not prove absence of dynamic references. No DELETE verdict depends on a negative search.

Commands run (the `$path` form was run per listed file; basename searches were omitted for generic names including `README.md`, `image`, `.gitignore`, `.dockerignore`, `package.json`, `package-lock.json`, and `requirements.txt`):

```sh
git ls-files
git ls-files --others --exclude-standard
git grep -Il -F -e "$path" -e "${path##*/}" -- .
git grep -Il -F -e "$path" -- .
git log -1 --format="%h %cs" -- "$path"
git grep -n -E 'docs/image([^[:alnum:]_./-]|$)' -- .
python /tmp/check-relative-links.py
```

OBSERVED: The exact `docs/image` path search returned no hits; `docs/images/` is a different directory. The basename `image` is too generic to establish an inbound reference. Full last-modifying commit hashes can be resolved from the abbreviated hashes below.

## Inventory by directory

### (root)

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `.dockerignore` | Docker build exclusions | `backend/.dockerignore`, `backend/tests/integration/test_packaging.py`, `frontend/.dockerignore` | 9e85368 2026-11-10 | KEEP |
| `.gitignore` | Git ignore rules | `backend/.dockerignore`, `backend/app/local.py`, `backend/tests/test_evals.py`, `docs/audit/FINAL-REPORT.md`, `docs/deploy/HUGGINGFACE_AND_MANAGED.md`, `frontend/.dockerignore` | e3f55f7 2026-11-19 | KEEP |
| `.gitleaks.toml` | secret-scan configuration | `backend/tests/integration/test_repository_hygiene.py`, `backend/tests/unit/test_check_secrets.py` | e3f55f7 2026-11-19 | KEEP |
| `.npmrc` | npm configuration | No exact path/name match | fdba71a 2026-11-01 | KEEP |
| `.pre-commit-config.yaml` | pre-commit hooks | `backend/tests/integration/test_repository_hygiene.py` | 944278f 2026-11-10 | KEEP |
| `AGENTS.md.txt` | legacy agent project instructions | `backend/tests/integration/test_legacy_doc_branding.py`, `docs/audit/name-inventory.md` | 5d5276c 2026-11-22 | KEEP |
| `CODE_OF_CONDUCT.md` | community code of conduct | `README.md`, `backend/tests/integration/test_repository_hygiene.py` | 944278f 2026-11-10 | KEEP |
| `CONTRIBUTING.md` | contributor guide | `README.md`, `backend/tests/integration/test_legacy_doc_branding.py`, `backend/tests/integration/test_repository_hygiene.py`, `docs/audit/name-inventory.md` | d7d2884 2026-11-22 | KEEP |
| `Caddyfile` | legacy Caddy proxy configuration | `docs/deploy/README.md` | 0379997 2026-11-18 | KEEP |
| `SECURITY.md` | security threat model and reporting guide | `.github/ISSUE_TEMPLATE/feature_request.md`, `CONTRIBUTING.md`, `README.md`, `backend/tests/integration/test_repository_hygiene.py` | e3f55f7 2026-11-19 | KEEP |
### backend

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `backend/.coveragerc` | coverage settings | `docs/verification.md` | 0379997 2026-11-18 | KEEP |
| `backend/.dockerignore` | backend Docker build exclusions | No exact path/name match | 2ecdada 2026-10-25 | KEEP |
| `backend/Dockerfile` | backend container build | `backend/.dockerignore`, `backend/tests/integration/test_packaging.py`, `docker-compose.yml`, `docs/deploy/HF_BUILD_TROUBLESHOOTING.md`, `frontend/.dockerignore` | 0379997 2026-11-18 | KEEP |
| `backend/README.md` | backend usage guide | `backend/tests/test_hf_requirements.py` | 0379997 2026-11-18 | KEEP |
| `backend/hf_app.py` | Hugging Face entrypoint | `backend/.env.example`, `backend/README.md`, `backend/app/config.py`, `backend/app/env_compat.py`, `backend/tests/test_deploy_scripts.py`, `backend/tests/test_hf_app.py`, `docs/audit/fake-audit.md`, `docs/deploy/HF_BUILD_TROUBLESHOOTING.md`, `docs/deploy/HUGGINGFACE_AND_MANAGED.md`, `docs/deploy/VERIFICATION.md`, `docs/testing.md`, `docs/verification.md`, `scripts/deploy_hf.ps1`, `scripts/deploy_hf.sh` | 0379997 2026-11-18 | KEEP |
| `backend/pytest.ini` | backend test configuration | `.github/workflows/ci.yml`, `docs/testing.md`, `docs/verification.md` | 35898f9 2026-11-15 | KEEP |
| `backend/requirements-dev.txt` | backend development dependencies | `.github/workflows/ci.yml`, `backend/app/db/url.py`, `backend/requirements.txt`, `backend/scripts/check_providers.py`, `backend/tests/integration/test_legacy_doc_branding.py`, `docs/audit/name-inventory.md`, `docs/deploy/HUGGINGFACE_AND_MANAGED.md`, `docs/deploy/VERIFICATION.md`, `docs/testing.md`, `scripts/deploy_hf.ps1`, `scripts/deploy_hf.sh` | 10e39de 2026-11-22 | KEEP |
| `backend/requirements-ml.txt` | optional ML dependencies | `README.md`, `backend/.env.example`, `backend/README.md`, `backend/app/core/ml_classifier.py`, `backend/scripts/train_router_model.py`, `backend/tests/test_hf_requirements.py`, `docs/deploy/HF_BUILD_TROUBLESHOOTING.md`, `docs/deploy/HUGGINGFACE_AND_MANAGED.md`, `docs/verification.md` | 6568fc1 2026-10-31 | KEEP |
| `backend/requirements.txt` | backend runtime dependencies | `.github/workflows/release.yml`, `backend/Dockerfile`, `docs/architecture.md`, `docs/audit/FINAL-REPORT.md`, `docs/deploy/HF_BUILD_TROUBLESHOOTING.md`, `docs/deploy/HUGGINGFACE_AND_MANAGED.md`, `run.py` | e3f55f7 2026-11-19 | KEEP |
### backend/scripts

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `backend/scripts/check_providers.py` | provider connectivity diagnostics | `README.md`, `backend/tests/unit/test_check_providers_script.py` | 35898f9 2026-11-15 | KEEP |
| `backend/scripts/check_secrets.py` | credential scanning tool | `.github/workflows/ci.yml`, `.gitleaks.toml`, `.pre-commit-config.yaml`, `CONTRIBUTING.md`, `README.md`, `backend/README.md`, `backend/tests/unit/test_check_secrets.py`, `docs/testing.md`, `docs/verification.md` | 0379997 2026-11-18 | KEEP |
| `backend/scripts/collect_training_data.py` | training-data collection script | `backend/.env.example`, `backend/app/core/judge.py`, `backend/requirements-ml.txt`, `backend/scripts/train_router_model.py`, `docs/architecture.md` | 6568fc1 2026-10-31 | KEEP |
| `backend/scripts/demo_server.py` | local demo server script | No exact path/name match | 0f62cc2 2026-11-01 | KEEP |
| `backend/scripts/smoke_openai_sdk.py` | OpenAI SDK smoke test helper | `backend/requirements-dev.txt` | e3f55f7 2026-11-19 | KEEP |
| `backend/scripts/train_router_model.py` | optional ML training script | `backend/.env.example`, `backend/app/config.py`, `backend/app/core/ml_classifier.py`, `backend/requirements-ml.txt` | 6568fc1 2026-10-31 | KEEP |
### benchmark

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `benchmark/README.md` | benchmark instructions | `README.md`, `backend/tests/integration/test_repository_hygiene.py`, `benchmark/run_benchmark.py` | 0379997 2026-11-18 | KEEP |
| `benchmark/generate_report.py` | benchmark report generator | `backend/tests/integration/test_legacy_doc_branding.py`, `backend/tests/test_benchmark.py`, `benchmark/README.md`, `docs/audit/name-inventory.md`, `docs/deploy/VERIFICATION.md` | e3f55f7 2026-11-19 | KEEP |
| `benchmark/requirements.txt` | benchmark dependencies | No exact path/name match | 3add715 2026-10-31 | KEEP |
### benchmark/results

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `benchmark/results/README.md` | generated-results directory instructions | No exact path/name match | 0379997 2026-11-18 | KEEP |
### benchmark

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `benchmark/run_benchmark.py` | benchmark runner | `CHANGELOG.md`, `README.md`, `backend/tests/integration/test_live_eval_subprocess.py`, `backend/tests/integration/test_live_script_contract.py`, `backend/tests/integration/test_repository_hygiene.py`, `backend/tests/test_benchmark.py`, `benchmark/README.md`, `benchmark/generate_report.py`, `benchmark/results/README.md`, `docs/audit/eval-response-fields.md`, `docs/audit/name-inventory.md`, `docs/deploy/VERIFICATION.md` | 7ff89da 2026-11-20 | KEEP |
| `benchmark/test_prompts.json` | benchmark prompt fixture | `backend/scripts/collect_training_data.py`, `benchmark/README.md`, `benchmark/run_benchmark.py` | 0379997 2026-11-18 | KEEP |
### cloudflare

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `cloudflare/worker.js` | archived Worker entrypoint | `cloudflare/config.test.js`, `cloudflare/worker.test.js`, `docs/deploy/CLOUDFLARE.md`, `docs/deploy/README.md`, `wrangler.jsonc` | 0b2666d 2026-11-08 | KEEP |
### doc

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `doc/Architecture.md.txt` | legacy architecture design notes | No exact path/name match | 2ecdada 2026-10-25 | KEEP |
| `doc/Design.md.txt` | legacy UI design notes | No exact path/name match | 2ecdada 2026-10-25 | KEEP |
| `doc/README.md.txt` | legacy product/readme guide | `backend/tests/integration/test_legacy_doc_branding.py`, `docs/audit/name-inventory.md` | 5d5276c 2026-11-22 | KEEP |
| `doc/TechStack.md.txt` | legacy technology stack notes | No exact path/name match | 2ecdada 2026-10-25 | KEEP |
| `doc/Testing.doc.txt` | legacy testing scenarios | No exact path/name match | 2ecdada 2026-10-25 | KEEP |
| `doc/prd.md.txt` | legacy product requirements | `backend/tests/integration/test_legacy_doc_branding.py`, `docs/audit/name-inventory.md` | 5d5276c 2026-11-22 | KEEP |
| `doc/trd.md.txt` | legacy technical requirements | No exact path/name match | 2ecdada 2026-10-25 | KEEP |
### (root)

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `docker-compose.yml` | container composition config | `.env.example`, `CHANGELOG.md`, `backend/README.md`, `backend/tests/integration/test_packaging.py`, `doc/README.md.txt`, `docs/deploy/README.md` | 0379997 2026-11-18 | KEEP |
### docs/assets

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `docs/assets/README.md` | demo recording instructions | `README.md`, `backend/tests/integration/test_repository_hygiene.py` | 944278f 2026-11-10 | KEEP |
### docs/audit

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `docs/audit/FINAL-REPORT.md` | historical pre-release audit report | `docs/audit/name-inventory.md` | 07b0599 2026-11-21 | OWNER DECIDES |
| `docs/audit/coverage-tracer-anomaly.md` | coverage measurement investigation | `docs/audit/FINAL-REPORT.md` | 07b0599 2026-11-21 | OWNER DECIDES |
| `docs/audit/eval-response-fields.md` | eval response-field audit | No exact path/name match | 204624e 2026-11-22 | OWNER DECIDES |
| `docs/audit/fake-audit.md` | test-double audit | `docs/audit/FINAL-REPORT.md` | 07b0599 2026-11-21 | OWNER DECIDES |
| `docs/audit/name-inventory.md` | project name inventory | `backend/tests/integration/test_legacy_doc_branding.py` | b765e0a 2026-11-22 | OWNER DECIDES |
### docs

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `docs/field-reality.md` | provider behavior and limitations guide | `README.md`, `docs/testing.md` | 0379997 2026-11-18 | KEEP |
| `docs/image` | one-byte newline-only file; purpose unknown | No exact path hit; `docs/images/` substring hits are different paths | 9850dea 2026-11-18 | OWNER DECIDES |
| `docs/mock-provider-investigation.md` | mock provider troubleshooting evidence | No exact path/name match | 35898f9 2026-11-15 | KEEP |
| `docs/verification.md` | historical verification audit | `docs/audit/name-inventory.md` | fd4f36e 2026-11-19 | KEEP |
### examples/webhook

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `examples/webhook/README.md` | webhook usage guide | `docs/audit/name-inventory.md` | 0379997 2026-11-18 | KEEP |
| `examples/webhook/call_routellm.mjs` | Node webhook example | `docs/audit/name-inventory.md`, `examples/webhook/README.md` | 0379997 2026-11-18 | KEEP |
| `examples/webhook/call_routellm.sh` | shell webhook example | `docs/audit/name-inventory.md`, `examples/webhook/README.md` | 0379997 2026-11-18 | KEEP |
| `examples/webhook/receiver.py` | webhook receiver example | `docs/audit/name-inventory.md`, `docs/deploy/HTTPS_AND_WEBHOOKS.md`, `examples/webhook/README.md` | 0379997 2026-11-18 | KEEP |
### frontend

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `frontend/.dockerignore` | frontend Docker build exclusions | No exact path/name match | 2ecdada 2026-10-25 | KEEP |
| `frontend/.gitignore` | frontend ignore rules | No exact path/name match | 2ecdada 2026-10-25 | KEEP |
| `frontend/.oxlintrc.json` | frontend lint configuration | `frontend/README.md` | 2ecdada 2026-10-25 | KEEP |
| `frontend/Dockerfile` | frontend container build | `backend/.dockerignore`, `backend/tests/integration/test_packaging.py`, `docker-compose.yml`, `docs/deploy/HF_BUILD_TROUBLESHOOTING.md`, `frontend/.dockerignore` | 0f62cc2 2026-11-01 | KEEP |
| `frontend/README.md` | frontend setup guide | No exact path/name match | 2ecdada 2026-10-25 | KEEP |
| `frontend/index.html` | frontend application entry HTML | `.github/workflows/release.yml`, `backend/app/frontend.py`, `backend/tests/integration/test_frontend_serving.py`, `backend/tests/test_run_launcher.py`, `frontend/nginx.conf`, `frontend/tailwind.config.js`, `run.py` | 0379997 2026-11-18 | KEEP |
| `frontend/nginx.conf` | frontend container server config | `frontend/Dockerfile` | 0f62cc2 2026-11-01 | KEEP |
| `frontend/package-lock.json` | frontend dependency lockfile | `.github/workflows/ci.yml`, `backend/Dockerfile` | 2ecdada 2026-10-25 | KEEP |
| `frontend/package.json` | frontend dependency and script manifest | `.github/workflows/ci.yml`, `CHANGELOG.md`, `backend/Dockerfile`, `backend/tests/test_run_launcher.py`, `docs/architecture.md` | 8190760 2026-11-21 | KEEP |
| `frontend/postcss.config.js` | PostCSS build config | `run.py` | 2ecdada 2026-10-25 | KEEP |
### frontend/public

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `frontend/public/favicon.svg` | frontend favicon | `backend/app/frontend.py`, `backend/tests/integration/test_frontend_serving.py`, `frontend/index.html` | 2ecdada 2026-10-25 | KEEP |
| `frontend/public/icons.svg` | frontend public SVG icon sprite | No exact path/name match | 2ecdada 2026-10-25 | KEEP |
### frontend

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `frontend/tailwind.config.js` | Tailwind build config | `run.py` | 0f62cc2 2026-11-01 | KEEP |
| `frontend/tsconfig.app.json` | app TypeScript config | `frontend/tsconfig.json` | 2ecdada 2026-10-25 | KEEP |
| `frontend/tsconfig.json` | root TypeScript config | No exact path/name match | 2ecdada 2026-10-25 | KEEP |
| `frontend/tsconfig.node.json` | Node TypeScript config | `frontend/tsconfig.json` | 2ecdada 2026-10-25 | KEEP |
| `frontend/vite.config.ts` | Vite build and test config | `frontend/.env.example`, `frontend/src/config.ts`, `frontend/tsconfig.node.json`, `run.py` | 0379997 2026-11-18 | KEEP |
### (root)

| Path | What it is | References found | Last commit and date | Verdict |
|---|---|---|---|---|
| `package-lock.json` | root dependency lockfile | `.github/workflows/ci.yml`, `backend/Dockerfile`, `docs/deploy/CLOUDFLARE.md`, `frontend/Dockerfile`, `run.py` | 8190760 2026-11-21 | KEEP |
| `package.json` | root dependency and script manifest | `.github/workflows/ci.yml`, `CHANGELOG.md`, `backend/Dockerfile`, `backend/tests/test_run_launcher.py`, `cloudflare/config.test.js`, `docs/architecture.md`, `docs/deploy/CLOUDFLARE.md`, `frontend/Dockerfile`, `run.py` | 0379997 2026-11-18 | KEEP |
| `start.ps1` | Windows launcher | `.github/workflows/release.yml`, `CHANGELOG.md`, `README.md`, `backend/tests/integration/test_packaging.py`, `docs/audit/FINAL-REPORT.md` | 0379997 2026-11-18 | KEEP |
| `start.sh` | shell launcher | `.github/workflows/release.yml`, `CHANGELOG.md`, `README.md`, `backend/tests/integration/test_packaging.py`, `docs/audit/FINAL-REPORT.md` | 0379997 2026-11-18 | KEEP |
| `wrangler.jsonc` | Cloudflare Worker config | `cloudflare/config.test.js`, `docs/deploy/CLOUDFLARE.md`, `docs/deploy/DEPLOY_WALKTHROUGH.md`, `docs/deploy/HUGGINGFACE_AND_MANAGED.md`, `docs/deploy/README.md`, `docs/deploy/VERIFICATION.md`, `package.json` | 0b2666d 2026-11-08 | KEEP |

## Counts

- DELETE: **0**. KEEP: **70**. OWNER DECIDES: **6** (five `docs/audit/` files and `docs/image`). Counts apply to the 76 listed rows, including conservative protected extras.

## Relative links before deletion

OBSERVED: `python /tmp/check-relative-links.py` checked README.md and all six top-level `docs/*.md` files: **19 relative links/images, 0 broken**. The temporary script is not committed. It resolves relative targets and Markdown heading fragments, checks linked-badge targets, and ignores fenced examples, HTML comments, and external URLs. It does not check external availability or nested docs outside the requested `docs/*.md` glob.

## Release and packaging

OBSERVED: `.github/workflows/release.yml` builds the frontend and stages `backend/` (excluding caches, tests, `.env`, and data), `frontend/dist`, and `run.py`, `start.sh`, `start.ps1`, `README.md`, and `LICENSE`, then zips them. It smoke-tests `/health`, `/`, and `/api/v1/catalog` after installing backend runtime requirements. Some listed KEEP files are staged or used during the build. No DELETE candidate is staged or smoke-tested because there are **no DELETE candidates**.

OBSERVED: The archive does not stage `docs/images/` or several other README-relative targets. This is a packaging limitation separate from the zero broken links in the repository; the release workflow and archive were not changed or run.

STOP: await an owner-approved list; do not delete or move anything in this phase.
