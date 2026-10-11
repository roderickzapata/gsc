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
- **CSV filename comes from `site_url` domain**, not `config.json`'s `csv_path`. `sc-domain:nicaladrillos.com` → `csv/nicaladrillos.com.csv` (with the default config).
- **Default output directory is `csv/`** — `output.csv_path` defaults to `csv/export.csv`, so exports land in `csv/<domain>.csv` unless the user overrides the path in `config.json`. The `csv/` directory is created automatically when missing.
- **Empty env var (`GSC_PAGE_FILTER=""`) = no filter** (null), different from unset env var.
- **Env vars override `config.json`**: `GSC_SITE_URL`, `GSC_PAGE_FILTER`, `GSC_QUERY_FILTER`.
- **Cross-site comparison requires two independent runs** — the Search Analytics API is per-property, so `download.py` cannot query two sites in one call. Run `download.py` once per site (using `GSC_SITE_URL` to switch) and feed the two CSVs into `compare.py`.
- **`compare.py` default output is `csv/comparison.csv`** — by convention, both inputs and the output live under `csv/`.

## Architecture

- **`download.py`** is the only module that imports all others.
- Modules communicate exclusively via domain models (`Config`, `ExecutionRequest`, `SearchResult`).
- `compare.py` is a standalone post-processing module: it does not import or depend on any other module of the project. Its input is two CSVs already produced by `download.py`; its output is a single aggregated comparison CSV.
- `ARCHITECTURE.md` contains binding ADR decisions. Changes to module interfaces, domain models, or cross-module flow require ADR documentation first.

## Project-specific quirks

- `test_auth.py` is a **manual auth test script** (run directly), not a pytest test.
- `run_local.sh` contains real credentials — never commit it.
- No lint/typecheck tools are configured in this repo.
- `.gitignore` excludes `config.json`, `client_secret*.json`, `.token_cache.json`, all `*.csv`, and the entire `csv/` directory (which contains the generated CSVs).
- The `csv/` directory is the only place where data files live. Do not create new top-level CSVs; route exports and comparisons through it.

## Useful commands

```bash
# Install
pip install -r requirements.txt

# Dev install (entry point)
pip install -e .

# Manual auth test
python test_auth.py

# Compare two exported CSVs (post-processing; no API access)
python compare.py --site-a csv/dominio-a.com.csv --site-b csv/dominio-b.com.csv
```
