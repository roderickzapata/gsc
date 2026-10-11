import csv
import os
import subprocess
import sys
from pathlib import Path

import pytest

from compare import compare_csvs


CSV_HEADER = ["query", "page", "clicks", "impressions", "ctr", "position"]


def _write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _read_output(path: Path) -> tuple[list[str], list[list[str]]]:
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    return header, rows


class TestCompareCsvsValidation:
    def test_site_a_missing_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(b, [])
        with pytest.raises(FileNotFoundError, match="Site A CSV not found"):
            compare_csvs(a, b, tmp_path / "out.csv")

    def test_site_b_missing_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        with pytest.raises(FileNotFoundError, match="Site B CSV not found"):
            compare_csvs(a, b, tmp_path / "out.csv")

    def test_output_matches_site_a_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        with pytest.raises(ValueError, match="must not coincide with site_a_path"):
            compare_csvs(a, b, a)

    def test_output_matches_site_b_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        with pytest.raises(ValueError, match="must not coincide with site_b_path"):
            compare_csvs(a, b, b)

    def test_output_with_relative_path_to_site_a_raises(self, tmp_path, monkeypatch):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="must not coincide with site_a_path"):
            compare_csvs(Path("a.csv"), b, Path("./a.csv"))

    def test_output_with_dot_segments_to_site_b_raises(self, tmp_path):
        a = tmp_path / "subdir" / ".." / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        indirect = tmp_path / "subdir" / ".." / "b.csv"
        with pytest.raises(ValueError, match="must not coincide with site_b_path"):
            compare_csvs(a, b, indirect)

    def test_output_with_absolute_path_to_site_a_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        with pytest.raises(ValueError, match="must not coincide with site_a_path"):
            compare_csvs(a, b, a.resolve())

    def test_output_symlink_to_site_a_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        link = tmp_path / "link.csv"
        try:
            os.symlink(a, link)
        except (OSError, NotImplementedError) as exc:
            pytest.skip(f"symlinks not supported in this environment: {exc}")
        with pytest.raises(ValueError, match="must not coincide with site_a_path"):
            compare_csvs(a, b, link)

    def test_output_symlink_to_site_b_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        link = tmp_path / "link.csv"
        try:
            os.symlink(b, link)
        except (OSError, NotImplementedError) as exc:
            pytest.skip(f"symlinks not supported in this environment: {exc}")
        with pytest.raises(ValueError, match="must not coincide with site_b_path"):
            compare_csvs(a, b, link)

    def test_label_a_empty_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        with pytest.raises(ValueError, match="non-empty"):
            compare_csvs(a, b, tmp_path / "out.csv", label_a="")

    def test_label_b_empty_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        with pytest.raises(ValueError, match="non-empty"):
            compare_csvs(a, b, tmp_path / "out.csv", label_b="")

    def test_labels_equal_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        with pytest.raises(ValueError, match="must be different"):
            compare_csvs(a, b, tmp_path / "out.csv", label_a="x", label_b="x")


class TestCompareCsvsHeaderAndShape:
    def test_default_labels_in_header(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        out = tmp_path / "out.csv"
        compare_csvs(a, b, out)
        header, _ = _read_output(out)
        assert header == [
            "query",
            "nica_clicks",
            "nica_impressions",
            "nica_ctr",
            "nica_position",
            "lpc_clicks",
            "lpc_impressions",
            "lpc_ctr",
            "lpc_position",
            "status",
        ]

    def test_custom_labels_in_header_and_status(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [{"query": "only-x", "page": "https://e.com/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 1.0}])
        _write_csv(b, [{"query": "only-y", "page": "https://e.com/", "clicks": 2, "impressions": 20, "ctr": 0.1, "position": 2.0}])
        out = tmp_path / "out.csv"
        compare_csvs(a, b, out, label_a="x", label_b="y")
        header, rows = _read_output(out)
        assert header[1:5] == ["x_clicks", "x_impressions", "x_ctr", "x_position"]
        assert header[5:9] == ["y_clicks", "y_impressions", "y_ctr", "y_position"]
        statuses = {r[0]: r[9] for r in rows}
        assert statuses == {"only-x": "only_x", "only-y": "only_y"}


class TestCompareCsvsContent:
    def test_shared_queries_with_distinct_metrics(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [
                {"query": "ladrillo", "page": "https://example.com/a/", "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 5.0},
            ],
        )
        _write_csv(
            b,
            [
                {"query": "ladrillo", "page": "https://example.com/b/", "clicks": 5, "impressions": 200, "ctr": 0.025, "position": 3.0},
            ],
        )
        out = tmp_path / "out.csv"
        result_path = compare_csvs(a, b, out)
        assert result_path == out
        header, rows = _read_output(out)
        assert len(rows) == 1
        row = rows[0]
        assert row[0] == "ladrillo"
        assert row[1:5] == ["10", "100", "0.1", "5.0"]
        assert row[5:9] == ["5", "200", str(5 / 200), "3.0"]
        assert row[9] == "shared"

    def test_only_in_a(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [{"query": "teja", "page": "https://example.com/a/", "clicks": 3, "impressions": 30, "ctr": 0.1, "position": 2.0}],
        )
        _write_csv(b, [])
        out = tmp_path / "out.csv"
        compare_csvs(a, b, out)
        _, rows = _read_output(out)
        assert len(rows) == 1
        row = rows[0]
        assert row[0] == "teja"
        assert row[1:5] == ["3", "30", "0.1", "2.0"]
        assert row[5:9] == ["", "", "", ""]
        assert row[9] == "only_nica"

    def test_only_in_b(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(
            b,
            [{"query": "cuarteron", "page": "https://example.com/b/", "clicks": 7, "impressions": 70, "ctr": 0.1, "position": 4.0}],
        )
        out = tmp_path / "out.csv"
        compare_csvs(a, b, out)
        _, rows = _read_output(out)
        assert len(rows) == 1
        row = rows[0]
        assert row[0] == "cuarteron"
        assert row[1:5] == ["", "", "", ""]
        assert row[5:9] == ["7", "70", "0.1", "4.0"]
        assert row[9] == "only_lpc"

    def test_empty_inputs_produce_header_only(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        out = tmp_path / "out.csv"
        compare_csvs(a, b, out)
        header, rows = _read_output(out)
        assert header[0] == "query"
        assert rows == []

    def test_identical_metrics(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [{"query": "x", "page": "https://example.com/a/", "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 1.0}],
        )
        _write_csv(
            b,
            [{"query": "x", "page": "https://example.com/b/", "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 1.0}],
        )
        out = tmp_path / "out.csv"
        compare_csvs(a, b, out)
        _, rows = _read_output(out)
        assert len(rows) == 1
        row = rows[0]
        assert row[1:5] == row[5:9]
        assert row[9] == "shared"

    def test_zero_impressions_no_division_error(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [{"query": "zero", "page": "https://example.com/a/", "clicks": 0, "impressions": 0, "ctr": 0, "position": 0}],
        )
        _write_csv(b, [])
        out = tmp_path / "out.csv"
        compare_csvs(a, b, out)
        _, rows = _read_output(out)
        assert len(rows) == 1
        row = rows[0]
        assert row[1:5] == ["0", "0", "0.0", "0.0"]
        assert row[9] == "only_nica"

    def test_aggregation_across_multiple_pages(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [
                {"query": "agg", "page": "https://example.com/p1/", "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 5.0},
                {"query": "agg", "page": "https://example.com/p2/", "clicks": 20, "impressions": 100, "ctr": 0.2, "position": 3.0},
            ],
        )
        _write_csv(b, [])
        out = tmp_path / "out.csv"
        compare_csvs(a, b, out)
        _, rows = _read_output(out)
        assert len(rows) == 1
        row = rows[0]
        assert row[1] == "30"
        assert row[2] == "200"
        assert row[3] == "0.15"
        assert row[4] == str((5.0 * 100 + 3.0 * 100) / 200)


class TestCompareCsvsOrdering:
    def test_alphabetical_order(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [
                {"query": "zulu", "page": "https://example.com/a/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 1.0},
                {"query": "alpha", "page": "https://example.com/a/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 1.0},
                {"query": "mike", "page": "https://example.com/a/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 1.0},
            ],
        )
        _write_csv(b, [])
        out = tmp_path / "out.csv"
        compare_csvs(a, b, out)
        _, rows = _read_output(out)
        assert [r[0] for r in rows] == ["alpha", "mike", "zulu"]

    def test_order_interleaved_across_sites(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [
                {"query": "zeta", "page": "https://example.com/a/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 1.0},
                {"query": "beta", "page": "https://example.com/a/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 1.0},
            ],
        )
        _write_csv(
            b,
            [
                {"query": "alpha", "page": "https://example.com/b/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 1.0},
                {"query": "gamma", "page": "https://example.com/b/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 1.0},
            ],
        )
        out = tmp_path / "out.csv"
        compare_csvs(a, b, out)
        _, rows = _read_output(out)
        assert [r[0] for r in rows] == ["alpha", "beta", "gamma", "zeta"]


class TestCompareCsvsIo:
    def test_output_overwrites_existing(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [{"query": "fresh", "page": "https://example.com/a/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 1.0}],
        )
        _write_csv(b, [])
        out = tmp_path / "out.csv"
        out.write_text("garbage,old,stuff\n1,2,3\n", encoding="utf-8")
        compare_csvs(a, b, out)
        header, rows = _read_output(out)
        assert header[0] == "query"
        assert [r[0] for r in rows] == ["fresh"]

    def test_creates_missing_output_directory(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        out = tmp_path / "deep" / "nested" / "out.csv"
        compare_csvs(a, b, out)
        assert out.exists()

    def test_output_path_returned(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(a, [])
        _write_csv(b, [])
        out = tmp_path / "out.csv"
        result = compare_csvs(a, b, out)
        assert result == out
        assert isinstance(result, Path)


class TestCompareCsvsInvalidInput:
    def test_missing_column_raises_value_error(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        with open(a, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["query", "page", "clicks", "impressions", "position"])
            writer.writerow(["q1", "https://e.com/", 1, 10, 1.0])
        _write_csv(b, [])
        with pytest.raises(ValueError, match="missing required columns: ctr"):
            compare_csvs(a, b, tmp_path / "out.csv")

    def test_non_numeric_clicks_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [{"query": "bad", "page": "https://e.com/", "clicks": "not-a-number", "impressions": 10, "ctr": 0.1, "position": 1.0}],
        )
        _write_csv(b, [])
        with pytest.raises(
            ValueError, match=r"field='clicks'.*got 'not-a-number'"
        ):
            compare_csvs(a, b, tmp_path / "out.csv")

    def test_non_numeric_impressions_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [{"query": "bad", "page": "https://e.com/", "clicks": 1, "impressions": "abc", "ctr": 0.1, "position": 1.0}],
        )
        _write_csv(b, [])
        with pytest.raises(
            ValueError, match=r"field='impressions'.*got 'abc'"
        ):
            compare_csvs(a, b, tmp_path / "out.csv")

    def test_non_numeric_position_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [{"query": "bad", "page": "https://e.com/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": "n/a"}],
        )
        _write_csv(b, [])
        with pytest.raises(
            ValueError, match=r"field='position'.*got 'n/a'"
        ):
            compare_csvs(a, b, tmp_path / "out.csv")

    def test_empty_numeric_value_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        with open(a, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
            writer.writerow(["bad", "https://e.com/", "1", "", "0.1", "1.0"])
        _write_csv(b, [])
        with pytest.raises(ValueError, match=r"field='impressions'.*empty value"):
            compare_csvs(a, b, tmp_path / "out.csv")

    def test_invalid_value_message_includes_row_and_query(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [
                {"query": "good", "page": "https://e.com/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 1.0},
                {"query": "broken-query", "page": "https://e.com/", "clicks": "xx", "impressions": 10, "ctr": 0.1, "position": 1.0},
            ],
        )
        _write_csv(b, [])
        with pytest.raises(ValueError) as exc_info:
            compare_csvs(a, b, tmp_path / "out.csv")
        msg = str(exc_info.value)
        assert "row 3" in msg
        assert "'broken-query'" in msg
        assert "'clicks'" in msg

    def test_nan_value_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [{"query": "bad-nan", "page": "https://e.com/", "clicks": "nan", "impressions": 10, "ctr": 0.1, "position": 1.0}],
        )
        _write_csv(b, [])
        with pytest.raises(
            ValueError, match=r"field='clicks'.*got 'nan'.*non-finite"
        ):
            compare_csvs(a, b, tmp_path / "out.csv")

    def test_inf_value_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [{"query": "bad-inf", "page": "https://e.com/", "clicks": 1, "impressions": "inf", "ctr": 0.1, "position": 1.0}],
        )
        _write_csv(b, [])
        with pytest.raises(
            ValueError, match=r"field='impressions'.*got 'inf'.*non-finite"
        ):
            compare_csvs(a, b, tmp_path / "out.csv")

    def test_negative_inf_value_raises(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [{"query": "bad-neginf", "page": "https://e.com/", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": "-inf"}],
        )
        _write_csv(b, [])
        with pytest.raises(
            ValueError, match=r"field='position'.*got '-inf'.*non-finite"
        ):
            compare_csvs(a, b, tmp_path / "out.csv")

    def test_nan_value_error_includes_file_row_query_field(self, tmp_path):
        a = tmp_path / "a.csv"
        b = tmp_path / "b.csv"
        _write_csv(
            a,
            [{"query": "broken-nan", "page": "https://e.com/", "clicks": "nan", "impressions": 10, "ctr": 0.1, "position": 1.0}],
        )
        _write_csv(b, [])
        with pytest.raises(ValueError) as exc_info:
            compare_csvs(a, b, tmp_path / "out.csv")
        msg = str(exc_info.value)
        assert str(a) in msg
        assert "row 2" in msg
        assert "'broken-nan'" in msg
        assert "'clicks'" in msg
        assert "non-finite" in msg


class TestCompareCliDefaults:
    def test_cli_default_output_is_csv_subdir(self, tmp_path, monkeypatch):
        project_root = Path(__file__).resolve().parent
        a = tmp_path / "csv" / "dominio-a.com.csv"
        b = tmp_path / "csv" / "dominio-b.com.csv"
        a.parent.mkdir(parents=True, exist_ok=True)
        _write_csv(a, [])
        _write_csv(b, [])
        result = subprocess.run(
            [
                sys.executable,
                str(project_root / "compare.py"),
                "--site-a",
                str(a),
                "--site-b",
                str(b),
            ],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(project_root),
        )
        expected = project_root / "csv" / "comparison.csv"
        assert expected.exists()
        assert "comparison.csv" in result.stdout
