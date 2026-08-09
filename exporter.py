import csv
from pathlib import Path

from models import Config, SearchResult


def _domain_from_site_url(site_url: str) -> str:
    prefix = "sc-domain:"
    if not site_url.startswith(prefix):
        raise ValueError(f"site_url must start with '{prefix}', got: {site_url!r}")
    domain = site_url[len(prefix):]
    if not domain:
        raise ValueError("site_url domain cannot be empty")
    if "/" in domain or "\\" in domain:
        raise ValueError(f"site_url domain cannot contain path separators: {domain!r}")
    return domain


def export_csv(rows: list[SearchResult], config: Config) -> Path:
    domain = _domain_from_site_url(config.site_url)
    base_dir = Path(config.csv_path).parent
    csv_filename = f"{domain}.csv"
    path = base_dir / csv_filename
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["query", "page", "clicks", "impressions", "ctr", "position"])
        for row in rows:
            writer.writerow([
                row.query,
                row.page,
                row.clicks,
                row.impressions,
                row.ctr,
                row.position,
            ])

    return path
