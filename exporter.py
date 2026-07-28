import csv
from pathlib import Path

from models import Config, SearchResult


def export_csv(rows: list[SearchResult], config: Config) -> Path:
    path = Path(config.csv_path)
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
