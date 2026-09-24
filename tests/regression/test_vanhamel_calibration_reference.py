"""Paper-anchored RX calibration and independently calculated archive reference.

The paper supplies the rounded 1.2 dB average and seven-day calibration design,
not exact dates or individual reports. Frozen archive expectations come from a
separate standard-library calculation. Actual production SQL executes over raw
rows through the bounded SQLite adapter before production evidence preparation.
"""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import socket
from types import SimpleNamespace

import matplotlib.dates as matplotlib_dates
import numpy as np
import pandas as pd
import pytest
import requests

from reference_sql import execute_generated_sql

from config import BAND_MAP
from core.analysis_runner import apply_post_fetch_filters, build_analysis_batches
from core.compare_engine import compare_footer_counts
from core.map_data import build_map_data_result
from core.math_utils import locator_to_latlon
from core.presentation_context import PresentationContext
from i18n import T
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.config_io import apply_config_state_values, validate_config_document
from ui.inspector.evidence_data import (
    _build_compare_unit_rows, _compare_joint_evidence_points,
    _retain_thresholded_compare_outcomes,
)
from ui.inspector.view_models import build_compare_inspector_view_model
from ui.plots.evidence_figures import (
    _compare_temporal_profile_values, _segment_figure_export_recipe,
    _segment_temporal_evidence_export_recipe,
)


REFERENCE_DIRECTORY = Path(__file__).parent / "reference_fixtures" / "vanhamel_rx_calibration_v1"
KEY_COLUMNS = ["time_slot", "peer_sign", "peer_grid"]


def _read_json(filename):
    return json.loads((REFERENCE_DIRECTORY / filename).read_text(encoding="utf-8"))


def _reject_network(*args, **kwargs):
    pytest.fail("The Vanhamel reference is mandatory and entirely offline")


@pytest.fixture(scope="module", autouse=True)
def verified_reference_files():
    manifest = _read_json("manifest.json")
    assert manifest["schema_version"] == 1
    paths = [record["path"] for record in manifest["files"]]
    assert len(paths) == len(set(paths))
    assert {
        "README.md", "demo.config", "source_rows.csv", "source_rows.parquet", "capture_provenance.json",
        "paper_features.json", "expected_sql_rows.csv", "expected_retained_rows.csv",
        "expected_paired_rows.csv", "expected_station_rows.csv",
        "expected_histogram_1db.csv", "expected_24h.csv", "expected_density_24h.csv",
        "expected_summary.json",
    }.issubset(paths)
    for record in manifest["files"]:
        path = (REFERENCE_DIRECTORY / record["path"]).resolve()
        assert path.is_relative_to(REFERENCE_DIRECTORY.resolve())
        contents = path.read_bytes()
        assert len(contents) == record["bytes"], record["path"]
        assert hashlib.sha256(contents).hexdigest() == record["sha256"], record["path"]
    with pytest.MonkeyPatch.context() as guard:
        guard.setattr(requests.sessions.Session, "request", _reject_network)
        guard.setattr(socket, "create_connection", _reject_network)
        guard.setattr(socket.socket, "connect", _reject_network)
        guard.setattr(socket.socket, "connect_ex", _reject_network)
        yield


def _calculate_run(source_rows, *, reference_correction_db=None):
    """Run production calculations without reading independent expectations."""
    configuration = validate_config_document(_read_json("demo.config"))
    session_values = {"lang": "en"}
    apply_config_state_values(configuration, session_values)
    session_values["run_mode"] = configuration["analysis_direction"].upper()
    context = build_analysis_context_from_session_state(session_values)
    if reference_correction_db is not None:
        context = replace(context, reference_snr_correction_db=reference_correction_db)
    latitude, longitude = locator_to_latlon(context.qth)
    presentation = PresentationContext(solar_label="All", labels=T["en"])
    analyses = build_analysis_batches(
        context, configuration["start_utc"], configuration["end_utc"], latitude, longitude,
        f"AND band = '{BAND_MAP[context.band]}'", presentation_context=presentation,
    )
    assert len(analyses) == 1
    analysis = analyses[0]
    sql_rows = execute_generated_sql(analysis.query, source_rows)
    processed, warning = apply_post_fetch_filters(
        sql_rows.copy(), analysis, context, latitude, longitude, T["en"],
    )
    assert warning is None
    preparation = build_map_data_result(
        processed, analysis_id=analysis.id, is_compare=analysis.is_compare,
        is_sequential=analysis.is_sequential, analysis_kind=analysis.analysis_kind,
        center_latitude=latitude, center_longitude=longitude,
        min_spots=context.min_joint_spots_per_station,
        min_opportunities=context.min_confirmed_opportunities_per_peer,
        base_min_stations=context.min_joint_stations_per_map_segment,
        tx_ab_repeat_interval_minutes=context.tx_ab_repeat_interval_minutes,
        tx_ab_target_start_minute=context.tx_ab_target_start_minute,
        tx_ab_reference_start_minute=context.tx_ab_reference_start_minute,
    )
    assert preparation.diagnostic is None and preparation.map_data is not None
    stations = preparation.map_data.station_rows
    inspector = build_compare_inspector_view_model(
        stations, analysis_id=analysis.id, is_sequential=analysis.is_sequential,
        analysis_context=context, presentation_context=presentation,
    )
    units = _build_compare_unit_rows(
        processed, stations, analysis.is_sequential,
        paired_identity_df=inspector.build_evidence_identities(),
    )
    units = _retain_thresholded_compare_outcomes(units, stations)
    points = _compare_joint_evidence_points(units, require_paired_eligible=True)
    outcome_counts = compare_footer_counts(stations, max_dist_km=float("inf"))
    recipe = _segment_figure_export_recipe(
        title="Vanhamel receiver-chain calibration", selected_segment="Full Range | All Directions",
        is_sequential=False, station_values=stations["stat_val"].dropna(),
        spot_values=points["metric"],
        panel_labels=["Only Target", "Joint", "Both asynchronous", "Only Reference"],
        panel_station_counts=[outcome_counts[f"stat_{name}"] for name in ("only_u", "joint", "both_async", "only_r")],
        panel_spot_counts=[outcome_counts[f"spot_{name}"] for name in ("only_u", "joint", "both_async", "only_r")],
        panel_series_labels=["Stations", "Spots"], panel_y_label="Percent of sample",
        decode_outcomes_title="Decode Outcomes", station_medians_title="Station Medians",
        paired_evidence_title="Joint-Spot Delta SNR", metric_axis_label="Delta SNR (dB)",
        median_label="Median", mean_label="Mean", no_data_label="No evidence",
    )
    temporal = _segment_temporal_evidence_export_recipe(
        points[["plot_time", "metric"]], "Vanhamel calibration", "24h", "Joint spots",
        analysis_start_t=configuration["start_utc"], analysis_end_t=configuration["end_utc"],
        chronological_title="Chronological Delta SNR ({time_bin})",
        chronological_x_label="UTC", chronological_unavailable_text="No evidence",
        metric_axis_label="Delta SNR (dB)", folded_title="UTC hour",
        folded_x_label="UTC hour", folded_date_annotation="{utc_date_count} dates",
        density_label="Relative Joint spot density", folded_unavailable_text="No evidence",
        median_focus_axis_label="Delta SNR (dB)", median_label="Median",
        bin_median_label="Bin median", bin_iqr_label="Bin IQR", time_bin_options=("24h",),
    )
    return SimpleNamespace(
        configuration=configuration, context=context, analysis=analysis,
        source_rows=source_rows, sql_rows=sql_rows, processed=processed,
        stations=stations, units=units, points=points, recipe=recipe, temporal=temporal,
    )


@pytest.fixture(scope="module")
def reference_run(verified_reference_files):
    source_rows = pd.read_csv(REFERENCE_DIRECTORY / "source_rows.csv", float_precision="round_trip")
    return _calculate_run(source_rows)


def _assert_scientific_rows(actual, expected):
    pd.testing.assert_frame_equal(
        actual[list(expected.columns)].sort_values(KEY_COLUMNS).reset_index(drop=True),
        expected.sort_values(KEY_COLUMNS).reset_index(drop=True),
        check_dtype=False, check_exact=False, rtol=0, atol=1e-12,
    )


def _assert_paper_mean(mean_db):
    policy = _read_json("paper_features.json")["comparison_policy"]
    lower, upper = policy["mean_rounding_interval_db"]
    assert lower <= mean_db < upper, (
        f"Joint-Spot mean {mean_db:.9f} dB no longer rounds to the paper's 1.2 dB; "
        "investigate selection, pairing, normalization, correction and weighting "
        "before changing the frozen baseline."
    )


def test_demo_pins_seven_day_reconstruction_and_zero_correction(reference_run):
    installed = json.loads((Path(__file__).parents[2] / "config/demos/01_vanhamel_rx_calibration.config").read_text(encoding="utf-8"))
    frozen = _read_json("demo.config")
    assert installed["settings"] == frozen["settings"]
    core = installed["settings"]["core_parameters"]
    assert core["time_selection"] == {
        "start_utc": "2021-02-06T06:00Z", "end_utc": "2021-02-13T06:00Z",
    }
    paper_design = _read_json("paper_features.json")["published_calibration"]
    assert reference_run.configuration["end_utc"] - reference_run.configuration["start_utc"] == pd.Timedelta(days=paper_design["first_measurement_duration_days"])
    assert reference_run.context.run_mode == "RX"
    assert reference_run.context.callsign == "ON4AWM0"
    assert reference_run.context.reference_callsign == "ON4AWM1"
    assert reference_run.context.reference_snr_correction_db == 0
    assert reference_run.context.min_joint_spots_per_station == 50
    assert reference_run.analysis.decode_filter_mode == "strict_code_1"


def test_actual_sql_and_post_fetch_rows_match_independent_source_calculation(reference_run):
    parquet_rows = pd.read_parquet(REFERENCE_DIRECTORY / "source_rows.parquet")
    csv_rows = reference_run.source_rows.copy()
    csv_rows["time"] = pd.to_datetime(csv_rows["time"], utc=True).dt.as_unit("s")
    parquet_rows["time"] = pd.to_datetime(parquet_rows["time"], utc=True).dt.as_unit("s")
    pd.testing.assert_frame_equal(csv_rows, parquet_rows, check_dtype=False, check_exact=True)
    for actual, filename in (
        (reference_run.sql_rows, "expected_sql_rows.csv"),
        (reference_run.processed, "expected_retained_rows.csv"),
    ):
        expected = pd.read_csv(REFERENCE_DIRECTORY / filename, float_precision="round_trip")
        _assert_scientific_rows(actual, expected)
    summary = _read_json("expected_summary.json")
    assert len(reference_run.sql_rows) == summary["sql_group_count"]
    assert len(reference_run.processed) == summary["retained_group_count"]
    assert reference_run.units.outcome.value_counts().to_dict() == summary["outcomes"]


def test_every_qualifying_pair_preserves_identity_cycle_and_snr_components(reference_run):
    expected = pd.read_csv(REFERENCE_DIRECTORY / "expected_paired_rows.csv")
    actual = reference_run.points.rename(columns={
        "station": "peer_sign", "grid": "peer_grid", "plot_time": "evidence_utc",
        "metric": "delta_snr_db",
    }).merge(
        reference_run.units[["evidence_utc", "peer_sign", "peer_grid", "target_snr_db", "reference_snr_db"]],
        on=["evidence_utc", "peer_sign", "peer_grid"], validate="one_to_one",
    )
    actual["time_slot"] = actual.evidence_utc.dt.as_unit("s").astype("int64") // 120
    columns = KEY_COLUMNS + ["target_snr_db", "reference_snr_db", "delta_snr_db"]
    _assert_scientific_rows(actual, expected[columns])


def test_paper_rounded_mean_and_exact_joint_histogram(reference_run):
    expected = pd.read_csv(REFERENCE_DIRECTORY / "expected_histogram_1db.csv")
    histogram = reference_run.recipe["spot_histogram"]
    populated = np.asarray(histogram["counts"]) > 0
    np.testing.assert_array_equal(np.asarray(histogram["centers"])[populated], expected.delta_snr_db)
    np.testing.assert_array_equal(np.asarray(histogram["counts"])[populated], expected.joint_spots)
    summary = _read_json("expected_summary.json")
    assert histogram["value_count"] == summary["joint_spots"]
    assert histogram["bin_width"] == 1
    assert histogram["mean"] == pytest.approx(summary["mean_delta_snr_db"], rel=0, abs=1e-12)
    assert histogram["median"] == summary["median_delta_snr_db"]
    _assert_paper_mean(histogram["mean"])
    assert f'{histogram["mean"]:.1f}' == "1.2"


def test_station_threshold_and_station_medians_are_distinct_from_pooled_mean(reference_run):
    expected = pd.read_csv(REFERENCE_DIRECTORY / "expected_station_rows.csv")
    actual = reference_run.stations.loc[reference_run.stations.spot_count > 0].rename(columns={
        "spot_count": "joint_spots", "stat_val": "median_delta_snr_db",
    })
    columns = ["peer_sign", "peer_grid", "joint_spots", "median_delta_snr_db"]
    pd.testing.assert_frame_equal(
        actual[columns].sort_values(columns[:2]).reset_index(drop=True),
        expected[columns].sort_values(columns[:2]).reset_index(drop=True),
        check_dtype=False, check_exact=True,
    )
    station_histogram = reference_run.recipe["station_histogram"]
    assert station_histogram["value_count"] == len(expected)
    assert station_histogram["mean"] == 1.0
    assert station_histogram["mean"] != reference_run.recipe["spot_histogram"]["mean"]


def test_seven_24h_profiles_preserve_counts_medians_iqr_and_density(reference_run):
    profiles = reference_run.temporal["prepared_profiles"]
    counts, summary, edges, _ = _compare_temporal_profile_values(profiles["chronological"]["24h"])
    expected = pd.read_csv(REFERENCE_DIRECTORY / "expected_24h.csv")
    assert len(summary) == len(expected) == 7
    for actual_column, expected_column in (
        ("count", "joint_spots"), ("median", "median_delta_snr_db"),
        ("q1", "q1_delta_snr_db"), ("q3", "q3_delta_snr_db"),
    ):
        np.testing.assert_array_equal(summary[actual_column], expected[expected_column])
    assert pd.DatetimeIndex(matplotlib_dates.num2date(edges[:-1], tz="UTC")).equals(
        pd.DatetimeIndex(pd.to_datetime(expected.bin_start_utc, utc=True))
    )
    assert pd.DatetimeIndex(matplotlib_dates.num2date(edges[1:], tz="UTC")).equals(
        pd.DatetimeIndex(pd.to_datetime(expected.bin_end_utc, utc=True))
    )
    expected_density = pd.read_csv(REFERENCE_DIRECTORY / "expected_density_24h.csv").pivot(
        index="delta_snr_bin_db", columns="bin_index", values="joint_spots",
    )
    np.testing.assert_array_equal(counts, expected_density.to_numpy())
    np.testing.assert_array_equal(
        profiles["y_edges"], np.arange(expected_density.index.min() - .5, expected_density.index.max() + 1.5),
    )
    assert int(counts.sum()) == reference_run.recipe["spot_histogram"]["value_count"]


@pytest.mark.parametrize("reference_correction_db", [-0.1, -0.2])
def test_paper_guard_rejects_1_3_and_1_4_db_from_incorrect_correction(reference_run, reference_correction_db):
    # An actual calculation with an erroneous nonzero correction must fail
    # both the paper's displayed precision and the exact archive baseline.
    changed = _calculate_run(reference_run.source_rows, reference_correction_db=reference_correction_db)
    changed_mean = changed.recipe["spot_histogram"]["mean"]
    assert changed_mean == pytest.approx(reference_run.recipe["spot_histogram"]["mean"] - reference_correction_db)
    assert f"{changed_mean:.1f}" in {"1.3", "1.4"}
    with pytest.raises(AssertionError, match="no longer rounds"):
        _assert_paper_mean(changed_mean)
    with pytest.raises(AssertionError):
        _assert_scientific_rows(changed.sql_rows, pd.read_csv(REFERENCE_DIRECTORY / "expected_sql_rows.csv", float_precision="round_trip"))


def test_sql_boundary_witnesses_detect_inclusive_end_or_exclusive_start(reference_run):
    expected = pd.read_csv(REFERENCE_DIRECTORY / "expected_sql_rows.csv", float_precision="round_trip")
    query = reference_run.analysis.query
    for original, replacement in (
        ("time < '2021-02-13 06:00:00'", "time <= '2021-02-13 06:00:00'"),
        ("time >= '2021-02-06 06:00:00'", "time > '2021-02-06 06:00:00'"),
    ):
        assert original in query
        changed = execute_generated_sql(query.replace(original, replacement), reference_run.source_rows)
        with pytest.raises(AssertionError):
            _assert_scientific_rows(changed, expected)
