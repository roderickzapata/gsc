import argparse
import csv
import math
from pathlib import Path


REQUIRED_COLUMNS = ("query", "page", "clicks", "impressions", "ctr", "position")


def compare_csvs(
    site_a_path: Path,
    site_b_path: Path,
    output_path: Path,
    label_a: str = "nica",
    label_b: str = "lpc",
) -> Path:
    if not label_a or not label_b:
        raise ValueError("label_a and label_b must be non-empty strings")
    if label_a == label_b:
        raise ValueError(
            f"label_a and label_b must be different (both are {label_a!r})"
        )

    if not site_a_path.is_file():
        raise FileNotFoundError(f"Site A CSV not found: {site_a_path}")
    if not site_b_path.is_file():
        raise FileNotFoundError(f"Site B CSV not found: {site_b_path}")

    resolved_output = output_path.resolve()
    resolved_a = site_a_path.resolve()
    resolved_b = site_b_path.resolve()
    if resolved_output == resolved_a:
        raise ValueError(
            f"output_path must not coincide with site_a_path: {output_path}"
        )
    if resolved_output == resolved_b:
        raise ValueError(
            f"output_path must not coincide with site_b_path: {output_path}"
        )

    aggr_a = _read_site(site_a_path)
    aggr_b = _read_site(site_b_path)

    all_queries = sorted(set(aggr_a) | set(aggr_b))

    header = [
        "query",
        f"{label_a}_clicks",
        f"{label_a}_impressions",
        f"{label_a}_ctr",
        f"{label_a}_position",
        f"{label_b}_clicks",
        f"{label_b}_impressions",
        f"{label_b}_ctr",
        f"{label_b}_position",
        "status",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(header)
        for query in all_queries:
            a = aggr_a.get(query)
            b = aggr_b.get(query)
            if a is not None and b is not None:
                status = "shared"
            elif a is not None:
                status = f"only_{label_a}"
            else:
                status = f"only_{label_b}"
            writer.writerow(
                [
                    query,
                    _clicks(a),
                    _impressions(a),
                    _ctr(a),
                    _position(a),
                    _clicks(b),
                    _impressions(b),
                    _ctr(b),
                    _position(b),
                    status,
                ]
            )

    return output_path


def _read_site(path: Path) -> dict:
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _validate_columns(reader.fieldnames, path)
        result: dict = {}
        for row_index, row in enumerate(reader, start=2):
            try:
                query = row["query"]
                clicks = _parse_float(row["clicks"], "clicks", path, row_index, query)
                impressions = _parse_float(
                    row["impressions"], "impressions", path, row_index, query
                )
                position = _parse_float(
                    row["position"], "position", path, row_index, query
                )
            except ValueError as e:
                raise ValueError(str(e)) from e
            agg = result.setdefault(
                query,
                {
                    "clicks": 0.0,
                    "impressions": 0.0,
                    "position_numerator": 0.0,
                    "position_denominator": 0.0,
                },
            )
            agg["clicks"] += clicks
            agg["impressions"] += impressions
            agg["position_numerator"] += position * impressions
            agg["position_denominator"] += impressions
    return result


def _validate_columns(fieldnames, path: Path) -> None:
    if fieldnames is None:
        raise ValueError(f"CSV is empty (no header): {path}")
    missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
    if missing:
        raise ValueError(
            f"CSV {path} is missing required columns: {', '.join(missing)}"
        )


def _parse_float(raw: str, field: str, path: Path, row_index: int, query: str) -> float:
    if raw is None or raw == "":
        raise ValueError(
            f"Invalid numeric value in {path} at row {row_index} "
            f"(query={query!r}, field={field!r}): empty value"
        )
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid numeric value in {path} at row {row_index} "
            f"(query={query!r}, field={field!r}): got {raw!r}"
        )
    if not math.isfinite(value):
        raise ValueError(
            f"Invalid numeric value in {path} at row {row_index} "
            f"(query={query!r}, field={field!r}): got {raw!r} (non-finite)"
        )
    return value


def _clicks(agg) -> str:
    return "" if agg is None else _fmt_int(agg["clicks"])


def _impressions(agg) -> str:
    return "" if agg is None else _fmt_int(agg["impressions"])


def _ctr(agg) -> str:
    if agg is None:
        return ""
    if agg["impressions"] == 0:
        return "0.0"
    return _fmt_float(agg["clicks"] / agg["impressions"])


def _position(agg) -> str:
    if agg is None:
        return ""
    if agg["position_denominator"] == 0:
        return "0.0"
    return _fmt_float(agg["position_numerator"] / agg["position_denominator"])


def _fmt_int(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return repr(float(value))


def _fmt_float(value: float) -> str:
    return repr(float(value))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-a", type=Path, required=True)
    parser.add_argument("--site-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("csv/comparison.csv"))
    args = parser.parse_args()

    output_path = compare_csvs(
        site_a_path=args.site_a,
        site_b_path=args.site_b,
        output_path=args.output,
    )
    with open(output_path, "r", newline="", encoding="utf-8") as f:
        row_count = sum(1 for _ in f) - 1
    print(f"Comparacion completada: {row_count} filas en {output_path}")


if __name__ == "__main__":
    main()
