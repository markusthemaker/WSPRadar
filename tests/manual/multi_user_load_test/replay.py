"""Prepare deterministic local query caches for the real Streamlit application.

Frozen source reports or captured exact-query responses supply the inputs.
Fixture expected results are never inputs. This measures a warm provider-cache workload: upstream
HTTP, native ClickHouse execution and database failover are outside its scope.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import threading


REPOSITORY_ROOT = next(
    directory for directory in Path(__file__).resolve().parents
    if (directory / "app.py").is_file() and (directory / "AGENT_README.md").is_file()
)
FIXTURE_ROOT = REPOSITORY_ROOT / "tests" / "regression" / "reference_fixtures"


@dataclass(frozen=True)
class ScenarioDefinition:
    id: str
    label: str
    configuration_path: Path
    source_mode: str
    source_name: str | None = None


SCENARIO_DEFINITIONS = (
    ScenarioDefinition("benchmark-large", "RX Benchmark: Griffiths April 2017",
                       FIXTURE_ROOT / "griffiths_fig3_temporal_v1" / "demo.config", "frozen_reports", "source_rows.parquet"),
    ScenarioDefinition("performance", "RX Performance: Griffiths April 2017",
                       REPOSITORY_ROOT / "config" / "demos" / "00c_griffiths_squibb_performance.config", "query_capture"),
    ScenarioDefinition("benchmark-small", "RX Benchmark: Griffiths three-day window",
                       FIXTURE_ROOT / "griffiths_fig6_diurnal_v1" / "demo.config", "frozen_reports", "source_rows.parquet"),
    ScenarioDefinition("performance-small", "TX Performance: Milazzo December 2010",
                       FIXTURE_ROOT / "milazzo_human_review_v2" / "performance.config", "frozen_reports", "network_source.parquet"),
)
DEFAULT_SCENARIOS = "benchmark-large,performance"
DEFAULT_PERFORMANCE_REPLAY = REPOSITORY_ROOT / ".test" / "multiuser-datasets" / "griffiths-performance"
_INSTALL_LOCK = threading.Lock()
_INSTALLED_DIRECTORY: Path | None = None


def _add_repository_imports() -> None:
    repository_path = str(REPOSITORY_ROOT)
    if repository_path not in sys.path:
        sys.path.insert(0, repository_path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _checked_fixture_file(directory: Path, filename: str) -> tuple[Path, dict]:
    """Validate only the requested input against its checked-in manifest."""
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    entries = {entry["path"]: entry for entry in manifest["files"]}
    if filename not in entries:
        raise ValueError(f"Fixture input is absent from its manifest: {directory.name}/{filename}")
    source_path = directory / filename
    expected = entries[filename]
    observed_hash = _sha256(source_path)
    if observed_hash != expected["sha256"] or source_path.stat().st_size != expected["bytes"]:
        raise ValueError(f"Fixture input failed integrity validation: {source_path}")
    return source_path, {
        "path": source_path.relative_to(REPOSITORY_ROOT).as_posix(),
        "sha256": observed_hash,
        "bytes": source_path.stat().st_size,
    }


def _set_cache_directory(cache_directory: Path) -> None:
    """Redirect both authoritative and compatibility imports before core imports."""
    import config
    from config import app_config

    cache_directory.mkdir(parents=True, exist_ok=True)
    config.CACHE_DIR = str(cache_directory)
    app_config.CACHE_DIR = str(cache_directory)


def prepare_streamlit_entrypoint(output_directory: str | Path) -> str:
    """Stage the bootstrap beside copied static assets, as Streamlit requires."""
    output_directory = Path(output_directory).resolve()
    runtime_directory = output_directory / "runtime"
    runtime_directory.mkdir(parents=True, exist_ok=True)
    shutil.copytree(REPOSITORY_ROOT / "static", runtime_directory / "static", dirs_exist_ok=True)
    bootstrap_path = Path(__file__).resolve().with_name("app_entry.py")
    entrypoint_path = runtime_directory / "streamlit_app.py"
    entrypoint_path.write_text(
        '"""Generated local load-test launcher; application sources remain unchanged."""\n'
        "from pathlib import Path\n"
        f"bootstrap_path = Path({str(bootstrap_path)!r})\n"
        "exec(compile(bootstrap_path.read_bytes(), str(bootstrap_path), 'exec'), "
        "{'__name__': '__main__', '__file__': str(bootstrap_path), '__package__': None})\n",
        encoding="utf-8",
    )
    return entrypoint_path.relative_to(output_directory).as_posix()


def _deny_requests_network(self, method, url, *args, **kwargs):
    """Fail closed rather than turning an unprepared query into provider traffic."""
    raise RuntimeError(
        "Offline load-test network guard rejected an HTTP request. "
        "The requested query may not be in the prepared replay cache. "
        f"Method={method}; URL={str(url).split('?')[0]}"
    )


def install_offline_runtime(output_directory: str | Path) -> dict:
    """Install the process-wide, test-only cache root and Requests guard once."""
    global _INSTALLED_DIRECTORY
    output_directory = Path(output_directory).resolve()
    _add_repository_imports()
    with _INSTALL_LOCK:
        if _INSTALLED_DIRECTORY is not None and _INSTALLED_DIRECTORY != output_directory:
            raise RuntimeError("One Streamlit process cannot mix different replay directories.")
        manifest_path = output_directory / "scenarios.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("schema_version") != 1 or manifest.get("mode") != "offline-query-cache":
            raise ValueError("Unsupported or incomplete load-test replay manifest.")
        if _INSTALLED_DIRECTORY is None:
            # Detect a bootstrap ordering mistake instead of leaving previously
            # imported core modules pointed at the ordinary application cache.
            if "core.data_engine" in sys.modules or "ui.run_controller" in sys.modules:
                raise RuntimeError("Install offline replay before importing application runtime modules.")
            _set_cache_directory(output_directory / "cache")
            import requests

            requests.sessions.Session.request = _deny_requests_network
            _INSTALLED_DIRECTORY = output_directory
        return manifest


def prepare_replay(output_directory: str | Path, *, scenarios=DEFAULT_SCENARIOS,
                   performance_replay: str | Path = DEFAULT_PERFORMANCE_REPLAY) -> dict:
    """Execute supported exact queries locally and publish reusable raw Parquet."""
    output_directory = Path(output_directory).resolve()
    output_directory.mkdir(parents=True, exist_ok=True)
    if (output_directory / "scenarios.json").exists():
        raise FileExistsError(f"Replay is already prepared; use a new output directory: {output_directory}")
    _add_repository_imports()
    _set_cache_directory(output_directory / "cache")

    import importlib.util
    import pandas as pd
    import requests

    requests.sessions.Session.request = _deny_requests_network
    from config import WSPR_DATABASE_PROVIDERS
    from core.artifact_store import ARTIFACT_STORE
    from core.data_engine import _query_cache_path, _validate_csv_query_numeric_values
    from capture import build_query_plan, load_query_capture
    from ui.url_state import build_query_from_settings, build_query_string

    adapter_path = REPOSITORY_ROOT / "tests" / "regression" / "reference_sql.py"
    adapter_spec = importlib.util.spec_from_file_location("load_test_reference_sql", adapter_path)
    if adapter_spec is None or adapter_spec.loader is None:
        raise RuntimeError("Cannot load the checked-in offline SQL adapter.")
    adapter = importlib.util.module_from_spec(adapter_spec)
    adapter_spec.loader.exec_module(adapter)
    primary_provider = WSPR_DATABASE_PROVIDERS[0]
    configurations_directory = output_directory / "configs"
    configurations_directory.mkdir(exist_ok=True)
    queries_directory = output_directory / "queries"
    queries_directory.mkdir(exist_ok=True)
    prepared_scenarios = []
    prepared_queries = {}
    definitions = {scenario.id: scenario for scenario in SCENARIO_DEFINITIONS}
    requested = scenarios.split(",")
    if not requested or len(set(requested)) != len(requested) or any(name not in definitions for name in requested):
        raise ValueError(f"Choose distinct scenarios from: {', '.join(definitions)}")

    for scenario_id in requested:
        definition = definitions[scenario_id]
        configuration_path = definition.configuration_path
        if definition.source_mode == "frozen_reports":
            configuration_path, configuration_provenance = _checked_fixture_file(configuration_path.parent, configuration_path.name)
            source_path, source_provenance = _checked_fixture_file(configuration_path.parent, definition.source_name)
            source_rows = pd.read_parquet(source_path)
        elif definition.source_mode == "query_capture":
            configuration_provenance = {
                "path": configuration_path.relative_to(REPOSITORY_ROOT).as_posix(),
                "sha256": _sha256(configuration_path), "bytes": configuration_path.stat().st_size,
            }
            source_rows = None
        else:
            raise ValueError(f"Unsupported replay source mode: {definition.source_mode}")
        document, _normalized, query_plan = build_query_plan(configuration_path)
        captured_queries = {}
        captured_row_counts = {}
        if definition.source_mode == "query_capture":
            captured_queries, source_provenance = load_query_capture(
                Path(performance_replay), configuration_path, query_plan,
            )
            captured_row_counts = {record["sql_sha256"]: record["rows"]
                                   for record in source_provenance["queries"]}
        query_row_counts = []
        for planned_query in query_plan:
            sql_query = planned_query["sql"]
            variant = planned_query["variant"]
            analysis_id = planned_query["analysis_id"]
            query_digest = hashlib.sha256(sql_query.encode("utf-8")).hexdigest()
            if definition.source_mode == "query_capture":
                # Preserve raw transport values and empty-column Arrow types;
                # copying admitted bytes avoids loading a large capture again.
                row_count = captured_row_counts[query_digest]
            else:
                query_rows = adapter.execute_generated_sql(sql_query, source_rows)
                row_count = len(query_rows)
                if planned_query["response_format"] == "csv":
                    _validate_csv_query_numeric_values(query_rows, is_demo=False)
            # Use the real path function and atomic writer. Both standard and
            # demo policies are prepared so ordinary Run and demo-style replay
            # cannot escape into an external request accidentally.
            cache_paths = []
            for is_demo in (False, True):
                cache_path = _query_cache_path(sql_query, primary_provider, is_demo=is_demo)
                if definition.source_mode == "query_capture":
                    ARTIFACT_STORE.write(cache_path, lambda temporary, source=captured_queries[query_digest]: shutil.copyfile(source, temporary))
                else:
                    ARTIFACT_STORE.write(cache_path, lambda temporary, rows=query_rows: rows.to_parquet(temporary, index=False))
                cache_paths.append(cache_path.relative_to(output_directory).as_posix())
            sql_path = queries_directory / f"{scenario_id}-{analysis_id}-{variant}.sql"
            sql_path.write_text(sql_query, encoding="utf-8")
            details = {
                "analysis_id": analysis_id, "variant": variant, "sha256": query_digest,
                "rows": row_count, "response_format": planned_query["response_format"],
                "cache_paths": cache_paths, "sql_path": sql_path.relative_to(output_directory).as_posix(),
            }
            prepared_queries[query_digest] = details
            query_row_counts.append(details)
        saved_configuration = configurations_directory / f"{scenario_id}.config"
        saved_configuration.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        prepared_scenarios.append({
            "id": scenario_id, "label": definition.label,
            "query_string": build_query_string(build_query_from_settings(document["settings"], include_run=True)),
            "config_path": saved_configuration.relative_to(output_directory).as_posix(),
            "source_mode": definition.source_mode,
            "source_rows": len(source_rows) if source_rows is not None else None,
            "query_result_rows": sum(entry["rows"] for entry in query_row_counts),
            "source_fixture": source_provenance,
            "configuration_fixture": configuration_provenance,
            "query_row_counts": query_row_counts,
            "scientific_validation_status": "Load input only; no claim of human approval or new scientific validation.",
        })
        if source_rows is not None:
            print(f"Prepared {scenario_id}: {len(source_rows):,} source rows", flush=True)
        else:
            print(f"Prepared {scenario_id}: {sum(entry['rows'] for entry in query_row_counts):,} captured query-result rows", flush=True)

    manifest = {
        "schema_version": 1, "mode": "offline-query-cache",
        "entrypoint": prepare_streamlit_entrypoint(output_directory),
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider_cache_namespace": primary_provider.key,
        "source_provenance_note": "The application's provider label identifies the replay cache namespace. Input provenance records distinguish frozen source reports from separately captured query responses; this measured run makes no provider requests.",
        "query_policy": "Exact production SQL only. Missing caches or changed scientific inputs fail closed at the Requests boundary.",
        "measurement_scope": "Real Streamlit sessions, analysis/export queues, cached fetch normalization, scientific processing, rendering, Inspector and exports; provider caches start warm.",
        "excluded_scope": ["upstream HTTP", "native ClickHouse SQL", "provider failover", "production host capacity"],
        "sql_adapter": {"path": adapter_path.relative_to(REPOSITORY_ROOT).as_posix(), "sha256": _sha256(adapter_path)},
        "scenarios": prepared_scenarios,
        "query_count": len(prepared_queries),
    }
    (output_directory / "scenarios.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", required=True, type=Path, metavar="OUTPUT_DIR")
    parser.add_argument("--scenarios", default=DEFAULT_SCENARIOS)
    parser.add_argument("--performance-replay", type=Path, default=DEFAULT_PERFORMANCE_REPLAY)
    arguments = parser.parse_args()
    manifest = prepare_replay(arguments.prepare, scenarios=arguments.scenarios,
                              performance_replay=arguments.performance_replay)
    print(f"Prepared {len(manifest['scenarios'])} offline scenarios in {arguments.prepare.resolve()}", flush=True)


if __name__ == "__main__":
    main()
