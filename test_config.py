import json
from pathlib import Path

import pytest

from config import load_config


@pytest.fixture
def minimal_config_file(tmp_path):
    config = {
        "auth": {
            "client_secrets_path": "client_secret.json",
            "token_store_path": ".token_cache.json",
        },
        "gsc": {
            "site_url": "sc-domain:config.example.com",
        },
        "query": {
            "dimensions": ["query", "page"],
            "type": "web",
            "row_limit": 1000,
            "page_filter": "https://config.example.com/initial-filter/",
            "query_filter": "bloques de concreto",
        },
        "output": {
            "csv_path": "export.csv",
        },
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return str(path)


@pytest.fixture
def config_without_site_url(tmp_path):
    config = {
        "auth": {
            "client_secrets_path": "client_secret.json",
            "token_store_path": ".token_cache.json",
        },
        "gsc": {},
        "query": {
            "dimensions": ["query", "page"],
            "type": "web",
            "row_limit": 1000,
        },
        "output": {
            "csv_path": "export.csv",
        },
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return str(path)


@pytest.fixture
def config_without_csv_path(tmp_path):
    config = {
        "auth": {
            "client_secrets_path": "client_secret.json",
            "token_store_path": ".token_cache.json",
        },
        "gsc": {
            "site_url": "sc-domain:config.example.com",
        },
        "query": {
            "dimensions": ["query", "page"],
            "type": "web",
            "row_limit": 1000,
        },
        "output": {},
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return str(path)


class TestSiteUrlEnvironmentOverride:
    def test_env_overrides_site_url(self, minimal_config_file, monkeypatch):
        monkeypatch.setenv("GSC_SITE_URL", "sc-domain:env.example.com")
        config = load_config(minimal_config_file)
        assert config.site_url == "sc-domain:env.example.com"

    def test_absence_of_gsc_site_url_uses_config_json(self, minimal_config_file, monkeypatch):
        monkeypatch.delenv("GSC_SITE_URL", raising=False)
        config = load_config(minimal_config_file)
        assert config.site_url == "sc-domain:config.example.com"

    def test_empty_gsc_site_url_triggers_validation_failure(self, minimal_config_file, monkeypatch):
        monkeypatch.setenv("GSC_SITE_URL", "")
        with pytest.raises(ValueError, match="Missing required configuration fields"):
            load_config(minimal_config_file)

    def test_env_with_valid_url_and_site_url_missing_in_json(self, config_without_site_url, monkeypatch):
        monkeypatch.setenv("GSC_SITE_URL", "sc-domain:env.example.com")
        config = load_config(config_without_site_url)
        assert config.site_url == "sc-domain:env.example.com"

    def test_no_env_and_site_url_missing_in_json_raises(self, config_without_site_url, monkeypatch):
        monkeypatch.delenv("GSC_SITE_URL", raising=False)
        with pytest.raises(ValueError, match="Missing required configuration fields"):
            load_config(config_without_site_url)


class TestPageFilterEnvironmentOverride:
    def test_env_overrides_page_filter(self, minimal_config_file, monkeypatch):
        monkeypatch.setenv("GSC_PAGE_FILTER", "https://env.example.com/page/")
        config = load_config(minimal_config_file)
        assert config.page_filter == "https://env.example.com/page/"

    def test_absence_of_gsc_page_filter_uses_config_json(self, minimal_config_file, monkeypatch):
        monkeypatch.delenv("GSC_PAGE_FILTER", raising=False)
        config = load_config(minimal_config_file)
        assert config.page_filter == "https://config.example.com/initial-filter/"

    def test_empty_gsc_page_filter_produces_none(self, minimal_config_file, monkeypatch):
        monkeypatch.setenv("GSC_PAGE_FILTER", "")
        config = load_config(minimal_config_file)
        assert config.page_filter is None


class TestQueryFilterEnvironmentOverride:
    def test_env_overrides_query_filter(self, minimal_config_file, monkeypatch):
        monkeypatch.setenv("GSC_QUERY_FILTER", "ladrillos rojos")
        config = load_config(minimal_config_file)
        assert config.query_filter == "ladrillos rojos"

    def test_absence_of_gsc_query_filter_uses_config_json(self, minimal_config_file, monkeypatch):
        monkeypatch.delenv("GSC_QUERY_FILTER", raising=False)
        config = load_config(minimal_config_file)
        assert config.query_filter == "bloques de concreto"

    def test_empty_gsc_query_filter_produces_none(self, minimal_config_file, monkeypatch):
        monkeypatch.setenv("GSC_QUERY_FILTER", "")
        config = load_config(minimal_config_file)
        assert config.query_filter is None


class TestCsvPathDefault:
    def test_default_csv_path_when_omitted(self, config_without_csv_path, monkeypatch):
        monkeypatch.delenv("GSC_SITE_URL", raising=False)
        config = load_config(config_without_csv_path)
        assert config.csv_path == "csv/export.csv"

    def test_explicit_csv_path_overrides_default(self, minimal_config_file, monkeypatch):
        monkeypatch.delenv("GSC_SITE_URL", raising=False)
        config = load_config(minimal_config_file)
        assert config.csv_path == "export.csv"
