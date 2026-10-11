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
        query_filter=None,
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

    def test_body_without_query_filter(self, mock_credentials, base_config):
        request = ExecutionRequest(
            start_date="2026-01-01",
            end_date="2026-01-07",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=1000,
            page_filter=None,
            query_filter=None,
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

    def test_body_with_query_filter(self, mock_credentials, base_config):
        request = ExecutionRequest(
            start_date="2026-01-01",
            end_date="2026-01-07",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=1000,
            page_filter=None,
            query_filter="teja de barro",
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
        assert filter_obj["dimension"] == "query"
        assert filter_obj["operator"] == "equals"
        assert filter_obj["expression"] == "teja de barro"

    def test_body_with_query_filter_and_page_filter(self, mock_credentials, base_config):
        page_url = "https://www.nicaladrillos.com/catalogo/teja/"
        request = ExecutionRequest(
            start_date="2026-01-01",
            end_date="2026-01-07",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=1000,
            page_filter=page_url,
            query_filter="teja de barro",
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
        assert len(filters) == 2

        filter_by_page = next(f for f in filters if f["dimension"] == "page")
        filter_by_query = next(f for f in filters if f["dimension"] == "query")

        assert filter_by_page["dimension"] == "page"
        assert filter_by_page["operator"] == "equals"
        assert filter_by_page["expression"] == page_url

        assert filter_by_query["dimension"] == "query"
        assert filter_by_query["operator"] == "equals"
        assert filter_by_query["expression"] == "teja de barro"

    def test_body_with_empty_string_query_filter(self, mock_credentials, base_config):
        request = ExecutionRequest(
            start_date="2026-01-01",
            end_date="2026-01-07",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=1000,
            page_filter=None,
            query_filter="",
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


class TestPagination:
    def test_single_page_results(self, mock_credentials, base_config):
        request = ExecutionRequest(
            start_date="2026-01-01",
            end_date="2026-01-07",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=1000,
        )

        mock_service = MagicMock()
        mock_response = {
            "rows": [
                {
                    "keys": ["ladrillo cuarteron", "https://example.com/cuarteron/"],
                    "clicks": 10,
                    "impressions": 100,
                    "ctr": 0.1,
                    "position": 1.0,
                }
            ]
        }
        mock_service.searchanalytics().query.return_value.execute.return_value = (
            mock_response
        )

        with patch("search_console.build", return_value=mock_service):
            result = download_search_analytics(mock_credentials, base_config, request)

        assert len(result) == 1
        assert result[0].query == "ladrillo cuarteron"
        assert result[0].clicks == 10
        assert mock_service.searchanalytics().query.call_count == 1

    def test_multiple_pages(self, mock_credentials, base_config):
        request = ExecutionRequest(
            start_date="2026-01-01",
            end_date="2026-01-07",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=2,
        )

        mock_service = MagicMock()
        page1_rows = [
            {
                "keys": ["query a", "https://example.com/page1/"],
                "clicks": 10,
                "impressions": 100,
                "ctr": 0.1,
                "position": 1.0,
            },
            {
                "keys": ["query b", "https://example.com/page2/"],
                "clicks": 20,
                "impressions": 200,
                "ctr": 0.1,
                "position": 2.0,
            },
        ]
        page2_rows = [
            {
                "keys": ["query c", "https://example.com/page3/"],
                "clicks": 30,
                "impressions": 300,
                "ctr": 0.1,
                "position": 3.0,
            },
        ]
        mock_service.searchanalytics().query.return_value.execute.side_effect = [
            {"rows": page1_rows},
            {"rows": page2_rows},
        ]

        with patch("search_console.build", return_value=mock_service):
            result = download_search_analytics(mock_credentials, base_config, request)

        assert len(result) == 3
        assert result[0].query == "query a"
        assert result[1].query == "query b"
        assert result[2].query == "query c"
        assert mock_service.searchanalytics().query.call_count == 2

        call_bodies = [
            call.kwargs["body"]
            for call in mock_service.searchanalytics().query.call_args_list
        ]
        assert call_bodies[0]["startRow"] == 0
        assert call_bodies[1]["startRow"] == 2

    def test_empty_response(self, mock_credentials, base_config):
        request = ExecutionRequest(
            start_date="2026-01-01",
            end_date="2026-01-07",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=1000,
        )

        mock_service = MagicMock()
        mock_service.searchanalytics().query.return_value.execute.return_value = {
            "rows": []
        }

        with patch("search_console.build", return_value=mock_service):
            result = download_search_analytics(mock_credentials, base_config, request)

        assert len(result) == 0
        assert mock_service.searchanalytics().query.call_count == 1

    def test_last_page_less_than_row_limit(self, mock_credentials, base_config):
        request = ExecutionRequest(
            start_date="2026-01-01",
            end_date="2026-01-07",
            dimensions=["query", "page"],
            query_type="web",
            row_limit=100,
        )

        mock_service = MagicMock()
        page1_rows = [
            {
                "keys": [f"query {i}", f"https://example.com/page{i}/"],
                "clicks": i,
                "impressions": i * 10,
                "ctr": 0.1,
                "position": 1.0,
            }
            for i in range(1, 101)
        ]
        page2_rows = [
            {
                "keys": [f"query {i}", f"https://example.com/page{i}/"],
                "clicks": i,
                "impressions": i * 10,
                "ctr": 0.1,
                "position": 1.0,
            }
            for i in range(101, 151)
        ]
        mock_service.searchanalytics().query.return_value.execute.side_effect = [
            {"rows": page1_rows},
            {"rows": page2_rows},
        ]

        with patch("search_console.build", return_value=mock_service):
            result = download_search_analytics(mock_credentials, base_config, request)

        assert len(result) == 150
        assert mock_service.searchanalytics().query.call_count == 2
