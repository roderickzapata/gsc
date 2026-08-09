import csv
import tempfile
from pathlib import Path

import pytest

from exporter import export_csv, _domain_from_site_url
from models import Config, SearchResult


class TestDomainFromSiteUrl:
    def test_sc_domain_format(self):
        assert _domain_from_site_url("sc-domain:nicaladrillos.com") == "nicaladrillos.com"

    def test_sc_domain_with_subdomain(self):
        assert _domain_from_site_url("sc-domain:docs.example.com") == "docs.example.com"

    def test_url_format_raises(self):
        with pytest.raises(ValueError, match="must start with 'sc-domain:'"):
            _domain_from_site_url("https://www.example.com/")

    def test_sc_domain_with_path_raises(self):
        with pytest.raises(ValueError, match="cannot contain path separators"):
            _domain_from_site_url("sc-domain:example.com/path")

    def test_sc_domain_empty_raises(self):
        with pytest.raises(ValueError, match="domain cannot be empty"):
            _domain_from_site_url("sc-domain:")


class TestExportCsv:
    @pytest.fixture
    def sample_rows(self):
        return [
            SearchResult(
                query="keyword1",
                page="https://example.com/page1",
                clicks=10.0,
                impressions=100.0,
                ctr=0.1,
                position=3.5,
            ),
            SearchResult(
                query="keyword2",
                page="https://example.com/page2",
                clicks=5.0,
                impressions=50.0,
                ctr=0.1,
                position=5.0,
            ),
        ]

    @pytest.fixture
    def base_config(self):
        return Config(
            client_secrets_path="client_secret.json",
            token_store_path=".token_cache.json",
            site_url="sc-domain:nicaladrillos.com",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=1000,
            csv_path="export.csv",
        )

    def test_csv_filename_uses_domain(self, sample_rows, base_config, tmp_path):
        base_config.csv_path = str(tmp_path / "export.csv")
        result_path = export_csv(sample_rows, base_config)
        assert result_path.name == "nicaladrillos.com.csv"

    def test_csv_directory_preserved(self, sample_rows, base_config, tmp_path):
        base_config.csv_path = str(tmp_path / "subdir" / "export.csv")
        result_path = export_csv(sample_rows, base_config)
        assert result_path.parent == tmp_path / "subdir"
        assert result_path.name == "nicaladrillos.com.csv"

    def test_csv_headers(self, sample_rows, base_config, tmp_path):
        base_config.csv_path = str(tmp_path / "export.csv")
        result_path = export_csv(sample_rows, base_config)
        with open(result_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
        assert headers == ["query", "page", "clicks", "impressions", "ctr", "position"]

    def test_csv_data_rows(self, sample_rows, base_config, tmp_path):
        base_config.csv_path = str(tmp_path / "export.csv")
        result_path = export_csv(sample_rows, base_config)
        with open(result_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0][0] == "keyword1"
        assert rows[0][1] == "https://example.com/page1"
        assert rows[0][2] == "10.0"
        assert rows[1][0] == "keyword2"

    def test_domain_isolation_no_overwrite(self, sample_rows, base_config, tmp_path):
        base_config.csv_path = str(tmp_path / "export.csv")

        config_d1 = Config(
            client_secrets_path=base_config.client_secrets_path,
            token_store_path=base_config.token_store_path,
            site_url="sc-domain:dominio1.com",
            dimensions=base_config.dimensions,
            query_type=base_config.query_type,
            row_limit=base_config.row_limit,
            csv_path=base_config.csv_path,
        )
        rows_d1 = [
            SearchResult(
                query="test_query_1",
                page="https://dominio1.com/page",
                clicks=100.0,
                impressions=1000.0,
                ctr=0.1,
                position=1.0,
            ),
        ]
        path_d1 = export_csv(rows_d1, config_d1)

        config_d2 = Config(
            client_secrets_path=base_config.client_secrets_path,
            token_store_path=base_config.token_store_path,
            site_url="sc-domain:dominio2.com",
            dimensions=base_config.dimensions,
            query_type=base_config.query_type,
            row_limit=base_config.row_limit,
            csv_path=base_config.csv_path,
        )
        rows_d2 = [
            SearchResult(
                query="test_query_2",
                page="https://dominio2.com/page",
                clicks=200.0,
                impressions=2000.0,
                ctr=0.1,
                position=2.0,
            ),
        ]
        path_d2 = export_csv(rows_d2, config_d2)

        assert path_d1.name == "dominio1.com.csv"
        assert path_d2.name == "dominio2.com.csv"
        assert path_d1.exists()
        assert path_d2.exists()

        with open(path_d1, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            d1_rows = list(reader)
        assert len(d1_rows) == 1
        assert d1_rows[0][0] == "test_query_1"
        assert d1_rows[0][1] == "https://dominio1.com/page"
        assert d1_rows[0][2] == "100.0"

        with open(path_d2, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            d2_rows = list(reader)
        assert len(d2_rows) == 1
        assert d2_rows[0][0] == "test_query_2"
        assert d2_rows[0][1] == "https://dominio2.com/page"
        assert d2_rows[0][2] == "200.0"
