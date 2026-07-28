from googleapiclient.discovery import build

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from models import Config, ExecutionRequest, SearchResult


def download_search_analytics(
    credentials: Credentials,
    config: Config,
    request: ExecutionRequest,
) -> list[SearchResult]:
    if credentials.expired:
        credentials.refresh(Request())

    service = build("searchconsole", "v1", credentials=credentials)

    body = {
        "startDate": request.start_date,
        "endDate": request.end_date,
        "dimensions": request.dimensions,
        "type": request.query_type,
        "rowLimit": request.row_limit,
    }

    response = service.searchanalytics().query(
        siteUrl=config.site_url,
        body=body,
    ).execute()

    rows = response.get("rows", [])
    return [_row_to_search_result(row) for row in rows]


def _row_to_search_result(row: dict) -> SearchResult:
    keys = row["keys"]
    if len(keys) != 2:
        raise ValueError(
            f"Expected row.keys to contain exactly 2 elements (query, page), "
            f"got {len(keys)}: {keys}"
        )
    return SearchResult(
        query=keys[0],
        page=keys[1],
        clicks=row["clicks"],
        impressions=row["impressions"],
        ctr=row["ctr"],
        position=row["position"],
    )
