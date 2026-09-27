"""Capture exact production query results once, before the offline load test.

Run this explicitly in Codespaces. Each generated strict/legacy query is fetched
sequentially from one configured provider under the production byte, row and
request limits. A completed capture is immutable and is never refreshed by the
load runner. This is load-test input, not an independent scientific reference.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace


REPOSITORY_ROOT = next(parent for parent in Path(__file__).resolve().parents
                       if (parent / "app.py").is_file() and (parent / "AGENT_README.md").is_file())
DEFAULT_CONFIGURATION = REPOSITORY_ROOT / "config/demos/00c_griffiths_squibb_performance.config"
DEFAULT_OUTPUT = REPOSITORY_ROOT / ".test/multiuser-datasets/griffiths-performance"
MANIFEST_NAME = "capture.json"
CAPTURE_KIND = "exact-production-query-capture"
MAX_ERROR_RESPONSE_CHARACTERS = 8192


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_record(path, directory):
    path = Path(path)
    return {"path": path.relative_to(directory).as_posix(), "bytes": path.stat().st_size,
            "sha256": _sha256(path)}


def _add_repository_imports():
    if str(REPOSITORY_ROOT) not in sys.path:
        sys.path.insert(0, str(REPOSITORY_ROOT))


def build_query_plan(configuration_path):
    """Return the validated configuration and exact production query variants."""
    _add_repository_imports()
    from config import BAND_MAP
    from core.analysis_runner import build_analysis_batches
    from core.math_utils import locator_to_latlon
    from core.presentation_context import PresentationContext
    from i18n import T
    from ui.analysis_context_adapter import build_analysis_context_from_session_state
    from ui.config_io import apply_config_state_values, validate_config_document

    document = json.loads(Path(configuration_path).read_text(encoding="utf-8"))
    normalized = validate_config_document(document)
    session_values = {"lang": "en"}
    apply_config_state_values(normalized, session_values)
    session_values["run_mode"] = normalized["analysis_direction"].upper()
    context = build_analysis_context_from_session_state(session_values)
    latitude, longitude = locator_to_latlon(context.qth)
    analyses = build_analysis_batches(
        context, normalized["start_utc"], normalized["end_utc"], latitude, longitude,
        f"AND band = '{BAND_MAP[context.band]}'",
        presentation_context=PresentationContext(solar_label="All", labels=T["en"]),
    )
    query_plan = []
    for analysis in analyses:
        variants = [("strict", analysis.query)]
        if analysis.legacy_query:
            variants.append(("legacy", analysis.legacy_query))
        for variant, sql_query in variants:
            query_plan.append({
                "analysis_id": analysis.id, "variant": variant,
                "sql": sql_query, "response_format": analysis.response_format,
                "analysis_contract": {
                    "analysis_kind": analysis.analysis_kind,
                    "is_sequential": analysis.is_sequential,
                    "is_local_median": analysis.is_local_median,
                },
            })
    if not query_plan:
        raise ValueError("The configuration produced no analysis queries")
    return document, normalized, query_plan


def _safe_capture_file(directory, relative_name):
    if not isinstance(relative_name, str) or not relative_name:
        raise ValueError("Capture file path must be a non-empty relative name")
    portable = PurePosixPath(relative_name)
    if (portable.is_absolute() or "\\" in relative_name
            or any(part in {".", ".."} or ":" in part for part in portable.parts)
            or portable.as_posix() != relative_name):
        raise ValueError(f"Unsafe capture file path: {relative_name!r}")
    current = directory
    for part in portable.parts:
        current = current / part
        information = current.lstat()
        if stat.S_ISLNK(information.st_mode) or getattr(information, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Capture links and reparse points are not allowed: {relative_name}")
    try:
        current.resolve().relative_to(directory.resolve())
    except ValueError as error:
        raise ValueError(f"Capture file escaped its directory: {relative_name}") from error
    if not current.is_file():
        raise ValueError(f"Capture path is not a regular file: {relative_name}")
    return current


def _verified_file(directory, record, *, maximum_bytes):
    if not isinstance(record, dict):
        raise ValueError("Capture file metadata must be an object")
    expected_bytes = record.get("bytes")
    if (type(expected_bytes) is not int or not 0 < expected_bytes <= maximum_bytes
            or not isinstance(record.get("sha256"), str) or len(record["sha256"]) != 64):
        raise ValueError("Capture file size or hash metadata is invalid")
    path = _safe_capture_file(directory, record.get("path"))
    if path.stat().st_size != expected_bytes or _sha256(path) != record["sha256"]:
        raise ValueError(f"Capture file failed size/hash validation: {record['path']}")
    return path


def _query_identity(query):
    return (query["analysis_id"], query["variant"], query["response_format"],
            hashlib.sha256(query["sql"].encode("utf-8")).hexdigest())


def _validate_query_schema(schema, query):
    """Reuse the production required-column contract without allocating rows."""
    from core.fetch_models import FetchResult
    from core.run_data_preparation import _schema_error

    schema_only_result = FetchResult(dataframe=SimpleNamespace(columns=schema.names))
    schema_error = _schema_error(schema_only_result, query["analysis_contract"])
    if schema_error is not None:
        raise ValueError(f"Capture query schema is invalid: {schema_error.error.message}")


def load_query_capture(directory, configuration_path, query_plan):
    """Validate immutable captured files against today's exact configuration/SQL."""
    _add_repository_imports()
    from config import MAX_ANALYSIS_RESULT_ROWS, WSPR_PARQUET_MAX_RESPONSE_BYTES
    import pyarrow.parquet as parquet

    directory = Path(directory).resolve()
    if not (directory / MANIFEST_NAME).exists():
        raise FileNotFoundError(f"No completed capture at {directory}; run capture.py once in Codespaces before the load test")
    manifest_path = _safe_capture_file(directory, MANIFEST_NAME)
    if manifest_path.stat().st_size > 1024 * 1024:
        raise ValueError("Capture manifest exceeds 1 MiB")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (not isinstance(manifest, dict) or manifest.get("schema_version") != 1
            or manifest.get("kind") != CAPTURE_KIND or manifest.get("status") != "complete"):
        raise ValueError("Capture manifest is unsupported or incomplete")
    configuration_file = _verified_file(directory, manifest.get("configuration"), maximum_bytes=4 * 1024 * 1024)
    if configuration_file.read_bytes() != Path(configuration_path).read_bytes():
        raise ValueError("Capture configuration differs from the current requested configuration; create a fresh capture")
    provider = manifest.get("provider")
    if (not isinstance(provider, dict) or not isinstance(provider.get("key"), str)
            or not provider["key"] or not isinstance(provider.get("url"), str)
            or not provider["url"].startswith("https://")):
        raise ValueError("Capture provider provenance is incomplete")
    captured_at = manifest.get("captured_at_utc")
    if not isinstance(captured_at, str) or datetime.fromisoformat(captured_at).utcoffset() is None:
        raise ValueError("Capture timestamp must include a timezone")
    expected = {_query_identity(query): query for query in query_plan}
    queries = manifest.get("queries")
    if not expected or len(expected) != len(query_plan) or not isinstance(queries, list):
        raise ValueError("Capture query plan is empty, duplicated or invalid")
    actual_identities = set()
    query_paths = {}
    query_result_rows = 0
    for record in queries:
        if not isinstance(record, dict):
            raise ValueError("Capture query metadata must be an object")
        identity = (record.get("analysis_id"), record.get("variant"),
                    record.get("response_format"), record.get("sql_sha256"))
        if identity not in expected or identity in actual_identities:
            raise ValueError("Capture query set differs from the current exact production query plan")
        actual_identities.add(identity)
        sql_file = _verified_file(directory, record.get("sql_file"), maximum_bytes=4 * 1024 * 1024)
        sql_query = expected[identity]["sql"]
        if sql_file.read_bytes() != sql_query.encode("utf-8") or _sha256(sql_file) != identity[3]:
            raise ValueError("Captured SQL differs from the current production query")
        result_file = _verified_file(directory, record.get("result_file"), maximum_bytes=WSPR_PARQUET_MAX_RESPONSE_BYTES)
        row_count = record.get("rows")
        if type(row_count) is not int or not 0 <= row_count <= MAX_ANALYSIS_RESULT_ROWS:
            raise ValueError("Capture result row count violates production limits")
        if parquet.read_metadata(result_file).num_rows != row_count:
            raise ValueError("Capture Parquet footer row count differs from its manifest")
        _validate_query_schema(parquet.read_schema(result_file), expected[identity])
        if identity[3] in query_paths:
            raise ValueError("Capture query SQL is duplicated")
        query_paths[identity[3]] = result_file
        query_result_rows += row_count
    if actual_identities != set(expected):
        raise ValueError("Capture is missing required strict/legacy query results")
    if query_result_rows == 0:
        raise ValueError("Every captured query result is empty; this capture cannot drive a load test")
    if manifest.get("query_result_rows") != query_result_rows:
        raise ValueError("Capture total query-result rows differs from its query records")
    return query_paths, {
        "kind": CAPTURE_KIND, "captured_at_utc": captured_at, "provider": provider,
        "configuration": manifest["configuration"], "queries": queries,
        "query_result_rows": query_result_rows, "manifest_sha256": _sha256(manifest_path),
        "source_note": "Captured production query results; not raw network reports or independent scientific expectations.",
    }


def _require_fresh_process():
    if "core.data_engine" in sys.modules or "core.artifact_store" in sys.modules:
        raise RuntimeError("Run capture.py in a fresh Python process so the cache can be isolated before core imports")


def select_provider(providers, provider_key=None):
    """Pin one enabled configured source without changing application policy."""
    candidates = [provider for provider in providers if provider.enabled]
    if provider_key is not None:
        candidates = [provider for provider in candidates if provider.key == provider_key]
    if not candidates:
        raise ValueError(f"No enabled configured provider matches {provider_key!r}")
    return candidates[0]


def record_capture_failure(output_directory, provider, query, error):
    """Retain the bounded provider explanation that the generic HTTP code omits."""
    diagnostic = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "provider": {"key": provider.key, "url": provider.url},
        "analysis_id": query["analysis_id"], "variant": query["variant"],
        "sql": query["sql"], "sql_sha256": _query_identity(query)[3],
        "code": error.code, "message": error.message, "status_code": error.status_code,
        "failure_stage": error.failure_stage,
        "response_text": str(error.response_text or "")[:MAX_ERROR_RESPONSE_CHARACTERS],
    }
    diagnostic_path = output_directory / "capture_failure.json"
    diagnostic_path.write_text(json.dumps(diagnostic, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Capture failure details: {diagnostic_path}", file=sys.stderr, flush=True)
    if diagnostic["response_text"]:
        print(f"Provider response:\n{diagnostic['response_text']}", file=sys.stderr, flush=True)


def capture_queries(output_directory, configuration_path, *, provider_key=None):
    """Capture a fresh immutable dataset using isolated production cache files."""
    output_directory = Path(output_directory).resolve()
    configuration_path = Path(configuration_path).resolve()
    if not configuration_path.is_file():
        raise FileNotFoundError(f"Configuration not found: {configuration_path}")
    if output_directory.exists():
        raise FileExistsError(f"Capture output already exists; use a NEW --output directory: {output_directory}")
    _require_fresh_process()
    _add_repository_imports()
    import config

    provider = select_provider(config.WSPR_DATABASE_PROVIDERS, provider_key)
    output_directory.mkdir(parents=True, exist_ok=False)
    configuration_copy = output_directory / "configuration.config"
    shutil.copyfile(configuration_path, configuration_copy)
    captured_at = datetime.now(timezone.utc).isoformat()
    with TemporaryDirectory(prefix="wspradar-query-capture-") as cache_directory:
        import config
        from config import app_config

        # These configuration imports stay lightweight; core captures CACHE_DIR
        # on import, so install the temporary cache root before building queries.
        config.CACHE_DIR = cache_directory
        app_config.CACHE_DIR = cache_directory
        _document, _normalized, query_plan = build_query_plan(configuration_copy)
        from core.data_engine import fetch_wspr_data, _query_cache_path, _validate_csv_query_numeric_values
        from core.provider_dispatch import UPSTREAM_PROVIDER_DISPATCH
        from core.run_data_preparation import _schema_error
        import pyarrow.parquet as parquet

        (output_directory / "queries").mkdir()
        (output_directory / "results").mkdir()
        records = []
        with UPSTREAM_PROVIDER_DISPATCH.acquire_run(
            {provider.key: len(query_plan)}, allowed_sources={provider.key},
        ) as provider_lease:
            for index, query in enumerate(query_plan):
                print(f"Capturing {query['analysis_id']} {query['variant']} from {provider.display_name}", flush=True)
                fetched = fetch_wspr_data(
                    query["sql"], response_format=query["response_format"], is_demo=False,
                    database_provider=provider, request_permit=provider_lease,
                )
                if fetched.error is not None:
                    provider_lease.report_failure(fetched.error)
                    record_capture_failure(output_directory, provider, query, fetched.error)
                    raise RuntimeError(f"Capture failed ({fetched.error.code}): {fetched.error.message}; no retry or provider fallback was attempted")
                if fetched.database_source.value != provider.key or not fetched.database_hit:
                    raise ValueError("Fresh capture did not originate from the pinned database provider")
                schema_error = _schema_error(fetched, query["analysis_contract"])
                if fetched.dataframe is None or schema_error is not None:
                    message = schema_error.error.message if schema_error is not None else "No query frame was returned"
                    raise ValueError(f"Capture query schema is invalid: {message}")
                _validate_csv_query_numeric_values(fetched.dataframe, is_demo=False)
                cache_path = _query_cache_path(query["sql"], provider, is_demo=False)
                if not cache_path.is_file():
                    raise ValueError("The production fetch did not persist a raw query artifact; capture was not published")
                sql_path = output_directory / "queries" / f"{index:02d}-{query['variant']}.sql"
                sql_path.write_text(query["sql"], encoding="utf-8", newline="")
                result_path = output_directory / "results" / f"{index:02d}-{query['variant']}.parquet"
                shutil.copyfile(cache_path, result_path)
                rows = int(parquet.read_metadata(result_path).num_rows)
                _validate_query_schema(parquet.read_schema(result_path), query)
                records.append({
                    "analysis_id": query["analysis_id"], "variant": query["variant"],
                    "response_format": query["response_format"], "sql_sha256": _query_identity(query)[3],
                    "sql_file": _file_record(sql_path, output_directory),
                    "result_file": _file_record(result_path, output_directory), "rows": rows,
                })
                fetched.dataframe = None
                print(f"Captured {rows:,} query-result rows", flush=True)
            provider_lease.report_success()
        total_rows = sum(record["rows"] for record in records)
        if total_rows == 0:
            raise ValueError("All strict/legacy query results were empty; no completed capture was published")
        manifest = {
            "schema_version": 1, "kind": CAPTURE_KIND, "status": "complete", "captured_at_utc": captured_at,
            "provider": {"key": provider.key, "url": provider.url, "display_name": provider.display_name},
            "configuration": _file_record(configuration_copy, output_directory),
            "queries": records, "query_result_rows": total_rows,
            "source_note": "Exact production query outputs captured once for offline load testing; not independent expected scientific results.",
        }
        manifest_path = output_directory / MANIFEST_NAME
        pending_manifest_path = output_directory / f"{MANIFEST_NAME}.pending"
        with pending_manifest_path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(manifest, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        pending_manifest_path.rename(manifest_path)
    return manifest


def main(arguments=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIGURATION)
    parser.add_argument("--provider", default=None,
                        help="Pin an enabled configured provider key (e.g. wd2); default: first enabled provider.")
    options = parser.parse_args(arguments)
    try:
        manifest = capture_queries(options.output, options.config, provider_key=options.provider)
    except Exception as error:
        print(f"Capture failed: {type(error).__name__}: {error}", file=sys.stderr)
        print("Capture did not complete. Retain any partial files for diagnosis and choose a NEW --output for another attempt.", file=sys.stderr)
        return 1
    print(f"Captured {manifest['query_result_rows']:,} query-result rows: {options.output.resolve() / MANIFEST_NAME}", flush=True)
    print("The load test will read this capture offline; it will not repeat provider requests.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
