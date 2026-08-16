# AGENTS.md — GSC Export

## Quick start

```bash
python download.py --last 7
```

First run opens browser for OAuth. Token cached to `.token_cache.json`.

## Run tests

```bash
pytest
```

Single test file: `pytest test_config.py`
Single test: `pytest test_config.py::TestSiteUrlEnvironmentOverride::test_env_overrides_site_url`

## Key behavioral facts

- **`--last N` includes today** — `--last 7` = last 7 days including today.
- **CSV filename comes from `site_url` domain**, not `config.json`'s `csv_path`. `sc-domain:nicaladrillos.com` → `nicaladrillos.com.csv`.
- **Empty env var (`GSC_PAGE_FILTER=""`) = no filter** (null), different from unset env var.
- **Env vars override `config.json`**: `GSC_SITE_URL`, `GSC_PAGE_FILTER`, `GSC_QUERY_FILTER`.

## Architecture

- **`download.py`** is the only module that imports all others.
- Modules communicate exclusively via domain models (`Config`, `ExecutionRequest`, `SearchResult`).
- `ARCHITECTURE.md` contains binding ADR decisions. Changes to module interfaces, domain models, or cross-module flow require ADR documentation first.

## Project-specific quirks

- `test_auth.py` is a **manual auth test script** (run directly), not a pytest test.
- `run_local.sh` contains real credentials — never commit it.
- No lint/typecheck tools are configured in this repo.
- `.gitignore` excludes `config.json`, `client_secret*.json`, `.token_cache.json`, and all `*.csv`.

## Useful commands

```bash
# Install
pip install -r requirements.txt

# Dev install (entry point)
pip install -e .

# Manual auth test
python test_auth.py
```
