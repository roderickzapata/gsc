import json
import os
from pathlib import Path

from models import Config


REQUIRED_FIELDS = [
    "auth.client_secrets_path",
    "gsc.site_url",
    "output.csv_path",
]


def load_config(config_path: str = "config.json") -> Config:
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}") from e

    auth = data.get("auth", {})
    gsc = data.get("gsc", {})
    query = data.get("query", {})
    output = data.get("output", {})

    env_site_url = os.getenv("GSC_SITE_URL")
    if env_site_url is not None:
        if env_site_url == "":
            site_url = ""
        else:
            site_url = env_site_url
    else:
        site_url = gsc.get("site_url", "")

    env_page_filter = os.getenv("GSC_PAGE_FILTER")
    if env_page_filter is not None:
        if env_page_filter == "":
            page_filter = None
        else:
            page_filter = env_page_filter
    else:
        page_filter = query.get("page_filter")

    _validate_required_fields(auth, output, site_url)

    return Config(
        client_secrets_path=auth.get("client_secrets_path", ""),
        token_store_path=auth.get("token_store_path", ".token_cache.json"),
        site_url=site_url,
        dimensions=query.get("dimensions", ["query", "page"]),
        query_type=query.get("type", "web"),
        row_limit=query.get("row_limit", 1000),
        csv_path=output.get("csv_path", "export.csv"),
        page_filter=page_filter,
    )


def _validate_required_fields(auth: dict, output: dict, site_url: str) -> None:
    missing = []
    if not auth.get("client_secrets_path"):
        missing.append("auth.client_secrets_path")
    if not site_url:
        missing.append("gsc.site_url")
    if not output.get("csv_path"):
        missing.append("output.csv_path")

    if missing:
        raise ValueError(f"Missing required configuration fields: {', '.join(missing)}")
