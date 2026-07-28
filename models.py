from dataclasses import dataclass


@dataclass
class Config:
    client_secrets_path: str
    token_store_path: str
    site_url: str
    dimensions: list[str]
    query_type: str
    row_limit: int
    csv_path: str


@dataclass
class ExecutionRequest:
    start_date: str
    end_date: str
    dimensions: list[str]
    query_type: str
    row_limit: int


@dataclass
class SearchResult:
    query: str
    page: str
    clicks: float
    impressions: float
    ctr: float
    position: float
