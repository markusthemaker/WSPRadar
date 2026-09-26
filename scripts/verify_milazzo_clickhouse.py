"""Occasional read-only ClickHouse comparison against the approved Milazzo fixture.

Run explicitly before completing a major development effort, especially after
SQL/provider changes. This script is deliberately outside routine pytest runs.
It validates the frozen offline scientific reference first, then sends exactly
one request for each requested strict/fallback Performance/Benchmark query to
one configured provider. There are no retries, cache reads, or fixture updates.
The default checks both analyses; --analysis can isolate either provider scope.

Examples (from the repository root)::

    .venv\\Scripts\\python.exe scripts/verify_milazzo_clickhouse.py --dry-run
    .venv\\Scripts\\python.exe scripts/verify_milazzo_clickhouse.py --provider wspr_live
    .venv\\Scripts\\python.exe scripts/verify_milazzo_clickhouse.py --provider wspr_live --analysis benchmark

Live differences can indicate changed source data, provider behavior, or SQL
semantics. They fail the check and require investigation; the script never
silently replaces the human-approved reference. A dry run is not a live pass.
The optional check validates this frozen population, not all ClickHouse SQL.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import time

import pandas as pd
import pyarrow.parquet as parquet
import requests


REPOSITORY = Path(__file__).resolve().parents[1]
REGRESSION_DIRECTORY = REPOSITORY / "tests" / "regression"
FIXTURE_DIRECTORY = REGRESSION_DIRECTORY / "reference_fixtures" / "milazzo_human_review_v2"
MAXIMUM_ERROR_BODY_BYTES = 8 * 1024
sys.path.insert(0, str(REPOSITORY))
sys.path.insert(0, str(REGRESSION_DIRECTORY))

from config.app_config import (  # noqa: E402
    MAX_ANALYSIS_RESULT_ROWS,
    WSPR_CSV_MAX_RESPONSE_BYTES,
    WSPR_DATABASE_PROVIDERS,
    WSPR_HTTP_CONNECT_TIMEOUT_SEC,
    WSPR_HTTP_READ_TIMEOUT_SEC,
    WSPR_PARQUET_MAX_RESPONSE_BYTES,
)


class ProviderQueryError(RuntimeError):
    """Retain bounded HTTP diagnostics without retrying the failed query."""

    def __init__(self, metadata):
        self.metadata = metadata
        details = metadata["error_body"] or "[empty error body]"
        if metadata["error_body_limit_reached"]:
            details += "\n[error body capture limit reached]"
        super().__init__(f"Provider returned HTTP {metadata['http_status']}; no retry was attempted. {details}")


def capture_http_error(response, *, deadline, started_at):
    """Retain at most 8 KiB of a failed response within the existing deadline."""
    captured = bytearray()
    metadata = {"http_status": response.status_code, "error_body_deadline_reached": False}
    chunks = response.iter_content(chunk_size=1024)
    try:
        while len(captured) < MAXIMUM_ERROR_BODY_BYTES:
            if time.monotonic() > deadline:
                metadata["error_body_deadline_reached"] = True
                break
            try:
                chunk = next(chunks)
            except StopIteration:
                break
            captured.extend(chunk[:MAXIMUM_ERROR_BODY_BYTES - len(captured)])
    except requests.RequestException as error:
        metadata["error_body_read_error"] = f"{type(error).__name__}: {error}"
    metadata.update(
        error_body=bytes(captured).decode(response.encoding or "utf-8", errors="replace"),
        error_body_bytes=len(captured),
        error_body_limit_reached=len(captured) == MAXIMUM_ERROR_BODY_BYTES,
        elapsed_seconds=round(time.monotonic() - started_at, 3),
    )
    return metadata


def sha256_file(path):
    """Hash one local provenance input without interpreting its contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_query_rows(actual, expected):
    """Compare every output row/column without hiding missing identities.

    Peer coordinates originate as Float32 in the archive. CSV emits their
    shortest decimal form; converting those two columns back to Float32 avoids
    inventing a Float64 discrepancy from transport formatting. All scientific
    counts, flags and SNR columns retain their values; non-coordinate numerical
    comparisons allow only 1e-12 absolute representation noise.
    """
    if set(actual.columns) != set(expected.columns):
        raise AssertionError(
            f"SQL result columns differ: actual={list(actual.columns)!r}; "
            f"expected={list(expected.columns)!r}"
        )
    key_columns = ["time_slot", "peer_sign", "peer_grid"]
    if not set(key_columns).issubset(expected.columns):
        raise AssertionError("Milazzo SQL output is missing its peer-cycle identity")
    canonical_frames = []
    for frame in (actual, expected):
        canonical = frame[list(expected.columns)].copy()
        for column in ("peer_lat", "peer_lon"):
            if column in canonical:
                canonical[column] = pd.to_numeric(canonical[column], errors="raise").astype("float32")
        canonical_frames.append(canonical.sort_values(key_columns).reset_index(drop=True))
    pd.testing.assert_frame_equal(
        *canonical_frames, check_dtype=False, check_exact=False, rtol=0, atol=1e-12,
    )


def benchmark_native_expected(benchmark, directory):
    """Use the historical native capture only for its auxiliary geoDistance.

    The SQLite adapter deliberately uses a spherical distance approximation;
    native ClickHouse geoDistance uses WGS-84. Their best_ref_dist values are
    not interchangeable. Every other captured column must first agree with the
    independently checked frozen-source replay, after clipping the capture to
    the exact approved time window. Only then may its distance column supply
    the native baseline. This machine capture is supplementary engine evidence,
    not a human-approved scientific oracle.
    """
    capture = pd.read_csv(
        Path(directory) / "benchmark_native_sql_capture.csv", float_precision="round_trip",
        keep_default_na=False, na_values=["\\N"],
    )
    start_slot = pd.Timestamp(benchmark.configuration["start_utc"]).timestamp() / 120
    end_slot = pd.Timestamp(benchmark.configuration["end_utc"]).timestamp() / 120
    capture = capture.loc[(capture.time_slot >= start_slot) & (capture.time_slot < end_slot)]
    auxiliary_columns = ["best_ref_dist"]
    compare_query_rows(
        capture.drop(columns=auxiliary_columns),
        benchmark.sql_rows.drop(columns=auxiliary_columns),
    )
    identity_columns = ["time_slot", "peer_sign", "peer_grid"]
    return benchmark.sql_rows.drop(columns=auxiliary_columns).merge(
        capture[[*identity_columns, *auxiliary_columns]],
        on=identity_columns, how="left", validate="one_to_one",
    )


def build_query_plan(work_directory):
    """Validate approved offline evidence before planning four live queries."""
    from milazzo_human_reference import (
        assert_performance_reference, replay_performance, verify_human_reference_files,
    )
    from test_milazzo_reference import _assert_native_units, _calculate_run

    verify_human_reference_files(FIXTURE_DIRECTORY)
    performance = replay_performance(FIXTURE_DIRECTORY, work_directory)
    assert_performance_reference(performance, FIXTURE_DIRECTORY)
    benchmark_source = pd.read_csv(
        FIXTURE_DIRECTORY / "benchmark_source.csv", float_precision="round_trip",
    )
    benchmark_document = json.loads((FIXTURE_DIRECTORY / "benchmark.config").read_text(encoding="utf-8"))
    benchmark = _calculate_run(benchmark_source, configuration_document=benchmark_document)
    expected_units = pd.read_csv(
        FIXTURE_DIRECTORY / "benchmark_expected_native_units.csv", float_precision="round_trip",
    )
    _assert_native_units(benchmark.units, expected_units)
    benchmark_fallback = benchmark_native_expected(benchmark, FIXTURE_DIRECTORY)
    queries = []
    for name, replay in (("performance", performance), ("benchmark", benchmark)):
        for variant, query, expected in (
            ("strict", replay.analysis.query, replay.strict_rows),
            ("fallback", replay.analysis.get("legacy_query"),
             benchmark_fallback if name == "benchmark" else replay.sql_rows),
        ):
            if not isinstance(query, str) or not query.strip():
                raise AssertionError(f"Missing {name} {variant} production SQL")
            queries.append((f"{name}_{variant}", query, expected))
    return queries


def fetch_live_query(query, provider):
    """Make one uncached read-only request with bounded time, bytes and rows."""
    format_match = re.search(r"\bFORMAT\s+(CSVWithNames|Parquet)\s*$", query)
    if format_match is None or not re.match(r"\s*(?:SELECT|WITH)\b", query, re.IGNORECASE) or ";" in query:
        raise ValueError("Only one generated read-only SELECT/WITH query is allowed")
    if not provider.url.startswith("https://"):
        raise ValueError("The configured provider must use HTTPS")
    response_format = format_match.group(1)
    maximum_bytes = WSPR_PARQUET_MAX_RESPONSE_BYTES if response_format == "Parquet" else WSPR_CSV_MAX_RESPONSE_BYTES
    started_at = time.monotonic()
    deadline = started_at + WSPR_HTTP_CONNECT_TIMEOUT_SEC + WSPR_HTTP_READ_TIMEOUT_SEC
    with requests.Session() as session:
        # An explicit provider is the identity under review. Redirects and
        # failover would silently change that identity and are not followed.
        with session.get(
            provider.url, params={"query": query}, stream=True, allow_redirects=False,
            timeout=(WSPR_HTTP_CONNECT_TIMEOUT_SEC, WSPR_HTTP_READ_TIMEOUT_SEC),
        ) as response:
            if response.status_code != 200:
                raise ProviderQueryError(capture_http_error(
                    response, deadline=deadline, started_at=started_at,
                ))
            response_buffer = io.BytesIO()
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if time.monotonic() > deadline:
                    raise TimeoutError("Provider response exceeded the complete-request deadline")
                if response_buffer.tell() + len(chunk) > maximum_bytes:
                    raise ValueError(f"Provider response exceeds {maximum_bytes} bytes")
                response_buffer.write(chunk)
            payload_bytes = response_buffer.tell()
            response_buffer.seek(0)
            if response_format == "Parquet":
                if parquet.ParquetFile(response_buffer).metadata.num_rows > MAX_ANALYSIS_RESULT_ROWS:
                    raise ValueError("Provider result exceeds the analysis row limit")
                response_buffer.seek(0)
                frame = pd.read_parquet(response_buffer)
            else:
                # Reuse the production logical CSV record counter before
                # allocating columns, including quoted embedded line breaks.
                from core.data_engine import _bounded_csv_response_buffer

                class BufferedResponse:
                    def iter_content(self, chunk_size):
                        while chunk := response_buffer.read(chunk_size):
                            yield chunk

                bounded_csv = _bounded_csv_response_buffer(
                    BufferedResponse(), maximum_bytes, MAX_ANALYSIS_RESULT_ROWS,
                )
                frame = pd.read_csv(
                    bounded_csv, float_precision="round_trip",
                    keep_default_na=False, na_values=["\\N"],
                )
            if len(frame) > MAX_ANALYSIS_RESULT_ROWS:
                raise ValueError("Provider result exceeds the analysis row limit")
    return frame, {
        "response_bytes": payload_bytes,
        "response_sha256": hashlib.sha256(response_buffer.getvalue()).hexdigest(),
        "elapsed_seconds": round(time.monotonic() - started_at, 3),
        "http_status": 200,
    }


def main(argv=None):
    """Write an auditable result and return nonzero for failures or differences."""
    providers = {provider.key: provider for provider in WSPR_DATABASE_PROVIDERS if provider.enabled}
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", choices=tuple(providers), default=next(iter(providers)))
    parser.add_argument("--analysis", choices=("both", "performance", "benchmark"), default="both", help="Live query scope: four queries for both analyses, or two for one analysis")
    parser.add_argument("--dry-run", action="store_true", help="Validate offline references and save queries without network access")
    parser.add_argument("--output-directory", type=Path, help="New directory for report, exact SQL and expected/actual result CSV files")
    arguments = parser.parse_args(argv)
    if sys.flags.optimize:
        parser.error("Run without Python -O: the offline scientific preflight requires assertions")
    started_utc = datetime.now(timezone.utc)
    output_directory = (
        arguments.output_directory
        or REPOSITORY / "output" / f"milazzo_clickhouse_{started_utc.strftime('%Y%m%dT%H%M%S_%fZ')}"
    ).resolve()
    if output_directory.is_relative_to(REGRESSION_DIRECTORY.resolve()):
        parser.error("Output must be outside tests/regression; frozen evidence is never overwritten")
    output_directory.mkdir(parents=True, exist_ok=False)
    provider = providers[arguments.provider]
    report = {
        "started_at_utc": started_utc.isoformat(),
        "status": "incomplete",
        "provider": {"key": provider.key, "url": provider.url},
        "requested_analysis": arguments.analysis,
        "matched_requested_scope": [],
        "dry_run": arguments.dry_run,
        "fixture_directory": str(FIXTURE_DIRECTORY.relative_to(REPOSITORY)),
        "request_policy": {
            "maximum_requests": 4 if arguments.analysis == "both" else 2,
            "retries": 0, "follow_redirects": False,
            "connect_timeout_seconds": WSPR_HTTP_CONNECT_TIMEOUT_SEC,
            "read_timeout_seconds": WSPR_HTTP_READ_TIMEOUT_SEC,
            "elapsed_budget_checked_between_chunks_seconds": WSPR_HTTP_CONNECT_TIMEOUT_SEC + WSPR_HTTP_READ_TIMEOUT_SEC,
            "maximum_csv_bytes": WSPR_CSV_MAX_RESPONSE_BYTES,
            "maximum_parquet_bytes": WSPR_PARQUET_MAX_RESPONSE_BYTES,
            "maximum_result_rows": MAX_ANALYSIS_RESULT_ROWS,
            "maximum_error_body_bytes": MAXIMUM_ERROR_BODY_BYTES,
        },
        "comparison": "Complete generated SQL outputs; same columns and peer-cycle rows, dtype-insensitive, rtol=0/atol=1e-12; peer_lat/peer_lon compared at source Float32 precision",
        "benchmark_auxiliary_distance_reference": "Only best_ref_dist is supplied by the checksummed historical native SQL capture, clipped to the approved window and joined by peer-cycle identity after all other capture columns match the independently checked offline replay. It is supplementary engine evidence, not a human scientific oracle.",
        "boundary": "Live provider output versus frozen-source offline SQL projection, with offline independent scientific preflight. Differences do not distinguish source drift from SQL/provider semantics; expectations are never updated.",
        "queries": [],
    }
    exit_code = 1
    try:
        print("Checking frozen approved evidence before planning live queries...", flush=True)
        report["input_sha256"] = {
            filename: sha256_file(FIXTURE_DIRECTORY / filename)
            for filename in (
                "manifest.json", "approval.json", "reviewed_expectations.json",
                "network_source.parquet", "performance.config", "benchmark_source.csv",
                "benchmark.config", "benchmark_expected_native_units.csv",
                "benchmark_native_sql_capture.csv", "benchmark_native_capture.sql",
            )
        }
        report["code_sha256"] = {
            filename: sha256_file(REPOSITORY / filename)
            for filename in (
                "core/analysis_runner.py", "core/opportunity_engine.py",
                "tests/regression/reference_sql.py", "scripts/verify_milazzo_clickhouse.py",
            )
        }
        with TemporaryDirectory(prefix="offline_preflight_", dir=output_directory) as work_directory:
            plan = build_query_plan(Path(work_directory))
        report["offline_scientific_preflight"] = "passed"
        if arguments.analysis != "both":
            plan = [query for query in plan if query[0].startswith(arguments.analysis + "_")]
        if len(plan) != report["request_policy"]["maximum_requests"]:
            raise ValueError("The generated plan does not cover the exact requested analysis scope")
        if len(plan) > provider.request_limit:
            raise ValueError("The requested check exceeds this provider's configured request budget")
        for name, query, expected in plan:
            (output_directory / f"{name}.sql").write_text(query, encoding="utf-8")
            expected.to_csv(output_directory / f"{name}_expected.csv", index=False)
            query_report = {
                "name": name, "query_sha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
                "expected_rows": len(expected), "status": "planned",
            }
            report["queries"].append(query_report)
        for (name, query, expected), query_report in zip(plan, report["queries"], strict=True):
            if arguments.dry_run:
                continue
            print(f"Checking {name} against {provider.display_name}...", flush=True)
            query_report["status"] = "request_started"
            try:
                actual, metadata = fetch_live_query(query, provider)
            except Exception as error:
                query_report.update(status="request_failed", error_type=type(error).__name__, error=str(error))
                if isinstance(error, ProviderQueryError):
                    query_report.update(error.metadata)
                raise
            query_report.update(metadata, actual_rows=len(actual))
            actual.to_csv(output_directory / f"{name}_actual.csv", index=False)
            try:
                compare_query_rows(actual, expected)
            except AssertionError as error:
                query_report.update(status="mismatch", difference=str(error))
                print(f"MISMATCH: {name}; retained outputs for investigation.", flush=True)
            else:
                query_report["status"] = "matched"
                print(f"MATCH: {name} ({len(actual)} rows).", flush=True)
        if arguments.dry_run:
            report["status"] = "dry_run_complete_not_live_verified"
            exit_code = 0
        elif all(query["status"] == "matched" for query in report["queries"]):
            report["matched_requested_scope"] = [query["name"] for query in report["queries"]]
            report["status"] = (
                "live_outputs_match_frozen_reference" if arguments.analysis == "both"
                else "live_requested_scope_matches_frozen_reference"
            )
            exit_code = 0
        else:
            report["status"] = "mismatch_requires_investigation"
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error))
        print(f"FAILED: {type(error).__name__}: {error}", file=sys.stderr, flush=True)
    finally:
        report["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        report_path = output_directory / "report.json"
        report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(f"{report['status']}: {report_path}", flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
