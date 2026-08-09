import pytest
from unittest.mock import MagicMock, patch

from search_console import download_search_analytics
from models import Config, ExecutionRequest


@pytest.fixture
def mock_credentials():
    creds = MagicMock()
    creds.expired = False
    return creds


@pytest.fixture
def base_config():
    return Config(
        client_secrets_path="client_secret.json",
        token_store_path=".token_cache.json",
        site_url="sc-domain:nicaladrillos.com",
        dimensions=["query", "page"],
        query_type="web",
        row_limit=1000,
        csv_path="export.csv",
        page_filter=None,
    )


class TestDownloadSearchAnalyticsBody:
    def test_body_without_page_filter(self, mock_credentials, base_config):
        request = ExecutionRequest(
            start_date="2026-01-01",
            end_date="2026-01-07",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=1000,
            page_filter=None,
        )

        mock_service = MagicMock()
        mock_response = {"rows": []}
        mock_service.searchanalytics().query.return_value.execute.return_value = (
            mock_response
        )

        with patch(
            "search_console.build", return_value=mock_service
        ):
            download_search_analytics(mock_credentials, base_config, request)

        mock_service.searchanalytics().query.assert_called_once()
        call_kwargs = mock_service.searchanalytics().query.call_args
        body = call_kwargs.kwargs["body"]

        assert "dimensionFilterGroups" not in body
        assert body["startDate"] == "2026-01-01"
        assert body["endDate"] == "2026-01-07"
        assert body["dimensions"] == ["query", "page"]
        assert body["type"] == "web"
        assert body["rowLimit"] == 1000

    def test_body_with_page_filter(self, mock_credentials, base_config):
        page_url = (
            "https://www.nicaladrillos.com/catalogo/teja-barro-tradicional-nicaragua/"
        )
        request = ExecutionRequest(
            start_date="2026-01-01",
            end_date="2026-01-07",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=1000,
            page_filter=page_url,
        )

        mock_service = MagicMock()
        mock_response = {"rows": []}
        mock_service.searchanalytics().query.return_value.execute.return_value = (
            mock_response
        )

        with patch(
            "search_console.build", return_value=mock_service
        ):
            download_search_analytics(mock_credentials, base_config, request)

        mock_service.searchanalytics().query.assert_called_once()
        call_kwargs = mock_service.searchanalytics().query.call_args
        body = call_kwargs.kwargs["body"]

        assert "dimensionFilterGroups" in body
        filter_groups = body["dimensionFilterGroups"]
        assert len(filter_groups) == 1

        filters = filter_groups[0]["filters"]
        assert len(filters) == 1

        filter_obj = filters[0]
        assert filter_obj["dimension"] == "page"
        assert filter_obj["operator"] == "equals"
        assert filter_obj["expression"] == page_url

    def test_body_with_page_filter_other_fields_unchanged(
        self, mock_credentials, base_config
    ):
        page_url = "https://www.example.com/test/"
        request = ExecutionRequest(
            start_date="2026-03-01",
            end_date="2026-03-15",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=5000,
            page_filter=page_url,
        )

        mock_service = MagicMock()
        mock_response = {"rows": []}
        mock_service.searchanalytics().query.return_value.execute.return_value = (
            mock_response
        )

        with patch(
            "search_console.build", return_value=mock_service
        ):
            download_search_analytics(mock_credentials, base_config, request)

        call_kwargs = mock_service.searchanalytics().query.call_args
        body = call_kwargs.kwargs["body"]

        assert body["startDate"] == "2026-03-01"
        assert body["endDate"] == "2026-03-15"
        assert body["dimensions"] == ["query", "page"]
        assert body["type"] == "web"
        assert body["rowLimit"] == 5000

    def test_body_with_empty_string_page_filter(self, mock_credentials, base_config):
        request = ExecutionRequest(
            start_date="2026-01-01",
            end_date="2026-01-07",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=1000,
            page_filter="",
        )

        mock_service = MagicMock()
        mock_response = {"rows": []}
        mock_service.searchanalytics().query.return_value.execute.return_value = (
            mock_response
        )

        with patch(
            "search_console.build", return_value=mock_service
        ):
            download_search_analytics(mock_credentials, base_config, request)

        call_kwargs = mock_service.searchanalytics().query.call_args
        body = call_kwargs.kwargs["body"]

        assert "dimensionFilterGroups" not in body
