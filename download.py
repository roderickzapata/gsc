import argparse
from datetime import date, timedelta

from config import load_config
from auth import authenticate
from search_console import download_search_analytics
from exporter import export_csv
from models import ExecutionRequest


def main() -> None:
    args = _parse_args()

    config = load_config()

    credentials = authenticate(config)

    start_date, end_date = _calculate_date_range(args.last)

    request = ExecutionRequest(
        start_date=start_date,
        end_date=end_date,
        dimensions=config.dimensions,
        query_type=config.query_type,
        row_limit=config.row_limit,
    )

    rows = download_search_analytics(credentials, config, request)

    csv_path = export_csv(rows, config)

    print(f"Exportacion completada: {len(rows)} filas exportadas a {csv_path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--last", type=int, required=True)
    args = parser.parse_args()
    if args.last < 1:
        raise ValueError("--last must be a positive integer (>= 1)")
    return args


def _calculate_date_range(last: int) -> tuple[str, str]:
    end_date = date.today()
    start_date = end_date - timedelta(days=last - 1)
    return start_date.isoformat(), end_date.isoformat()


if __name__ == "__main__":
    main()
