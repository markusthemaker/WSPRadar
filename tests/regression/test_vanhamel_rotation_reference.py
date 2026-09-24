"""Vanhamel Figure 6 paper anchors and independently calculated raw reference.

The raster supplies seven approximate landmarks, not exact sample medians.
Frozen standard-library expectations protect production SQL, paired components,
reception slices, and the actual Selected Station Evidence temporal recipe.
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
    _compare_temporal_profile_values, _selected_evidence_export_recipe,
    _temporal_metric_summary,
)


REFERENCE_DIRECTORY = Path(__file__).parent / "reference_fixtures" / "vanhamel_fig6_rotation_v1"
REPOSITORY_DIRECTORY = Path(__file__).resolve().parents[2]
KEY_COLUMNS = ["time_slot", "peer_sign", "peer_grid"]


def _read_json(filename):
    return json.loads((REFERENCE_DIRECTORY / filename).read_text(encoding="utf-8"))


def _read_csv(filename):
    return pd.read_csv(REFERENCE_DIRECTORY / filename, float_precision="round_trip")


def _reject_network(*args, **kwargs):
    pytest.fail("The Figure 6 reference is mandatory and entirely offline")


@pytest.fixture(scope="module", autouse=True)
def verified_reference_files():
    manifest = _read_json("manifest.json")
    assert manifest["schema_version"] == 1
    paths = [record["path"] for record in manifest["files"]]
    assert len(paths) == len(set(paths))
    assert {
        "README.md", "demo.config", "source_rows.csv", "source_rows.parquet",
        "capture_provenance.json", "paper_features.json", "figure6_overlay_1p6.png",
        "expected_sql_rows.csv", "expected_retained_rows.csv", "expected_paired_rows.csv",
        "expected_reception_slices_20.csv", "expected_12h.csv",
        "expected_density_12h.csv", "expected_halves.csv", "expected_summary.json",
    }.issubset(paths)
    for record in manifest["files"]:
        path = (REFERENCE_DIRECTORY / record["path"]).resolve()
        assert path.is_relative_to(REFERENCE_DIRECTORY.resolve())
        contents = path.read_bytes()
        assert len(contents) == record["bytes"], record["path"]
        assert hashlib.sha256(contents).hexdigest() == record["sha256"], record["path"]
    assert (REFERENCE_DIRECTORY / "figure6_overlay_1p6.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    with pytest.MonkeyPatch.context() as guard:
        guard.setattr(requests.sessions.Session, "request", _reject_network)
        guard.setattr(socket, "create_connection", _reject_network)
        guard.setattr(socket.socket, "connect", _reject_network)
        guard.setattr(socket.socket, "connect_ex", _reject_network)
        yield


def _calculate_run(source_rows, *, reference_correction_db=None):
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
    selection = _read_json("demo.config")["settings"]["results_view"]["benchmark"]["selected_stations"]
    assert len(selection) == 1
    selected = selection[0]
    units = units[
        units.peer_sign.eq(selected["callsign"]) & units.peer_grid.eq(selected["locator"])
    ].sort_values("evidence_utc").reset_index(drop=True)
    points = _compare_joint_evidence_points(units, require_paired_eligible=True)
    points = points.sort_values("plot_time").reset_index(drop=True)
    temporal = _selected_evidence_export_recipe(
        points, "Vanhamel Figure 6: M7AEO (IO82)", "12h", False,
        analysis_start_t=configuration["start_utc"], analysis_end_t=configuration["end_utc"],
        count_label="Joint spots", chronological_title="Delta SNR ({time_bin})",
        chronological_x_label="UTC", chronological_unavailable_text="No evidence",
        metric_axis_label="Delta SNR (dB)", folded_title="UTC hour",
        folded_x_label="UTC hour", folded_date_annotation="{utc_date_count} dates",
        density_label="Relative Joint spot density", folded_unavailable_text="No evidence",
        median_focus_axis_label="Delta SNR (dB)", median_label="Median",
        bin_median_label="Bin median", bin_iqr_label="Bin IQR", time_bin_options=("12h",),
    )
    return SimpleNamespace(
        configuration=configuration, context=context, source_rows=source_rows,
        sql_rows=sql_rows, processed=processed, units=units, points=points, temporal=temporal,
    )


@pytest.fixture(scope="module")
def reference_run(verified_reference_files):
    return _calculate_run(_read_csv("source_rows.csv"))


def _assert_scientific_rows(actual, expected):
    pd.testing.assert_frame_equal(
        actual[list(expected.columns)].sort_values(KEY_COLUMNS).reset_index(drop=True),
        expected.sort_values(KEY_COLUMNS).reset_index(drop=True),
        check_dtype=False, check_exact=False, rtol=0, atol=1e-12,
    )


def _assert_exact_trace(points):
    expected = _read_csv("expected_paired_rows.csv")
    assert len(points) == len(expected) == 1441
    np.testing.assert_array_equal(
        _utc_nanoseconds(points.plot_time),
        _utc_nanoseconds(expected.evidence_utc),
    )
    np.testing.assert_allclose(points.metric, expected.delta_snr_db, rtol=0, atol=1e-12)


def _utc_nanoseconds(timestamps):
    # Pandas can retain seconds or microseconds depending on the input path.
    return pd.to_datetime(timestamps, utc=True).to_numpy(dtype="datetime64[ns]").astype(np.int64)


def _paper_landmark_values(points):
    paper = _read_json("paper_features.json")
    policy = paper["landmark_readout_policy"]
    index_tolerance = policy["index_tolerance_receptions"]
    amplitudes = []
    for landmark in paper["black_trace_landmarks"]:
        center = landmark["reception_index_approx"]
        # The position allowance was fixed from the raster before archive comparison.
        nearby = points.iloc[max(0, center - index_tolerance - 1):center + index_tolerance]
        assert not nearby.empty
        amplitude = nearby.metric.min() if landmark["delta_snr_db_approx"] < 0 else nearby.metric.max()
        assert abs(amplitude - landmark["delta_snr_db_approx"]) <= policy["amplitude_tolerance_db"] + 1e-12, landmark["name"]
        amplitudes.append(amplitude)
    return amplitudes


def _assert_group_statistics(points, group_indexes, expected):
    grouped = points.metric.groupby(group_indexes)
    actual = _temporal_metric_summary(grouped, pd.RangeIndex(len(expected)))
    for actual_column, expected_column in (
        ("count", "joint_spots"), ("median", "median_delta_snr_db"),
        ("q1", "q1_delta_snr_db"), ("q3", "q3_delta_snr_db"),
    ):
        np.testing.assert_allclose(actual[actual_column], expected[expected_column], rtol=0, atol=1e-12)
    for aggregation in ("mean", "min", "max"):
        np.testing.assert_allclose(
            grouped.agg(aggregation), expected[f"{aggregation}_delta_snr_db"], rtol=0, atol=1e-12,
        )


def test_installed_demo_pins_reconciled_correction_and_selected_path(reference_run):
    installed = json.loads((REPOSITORY_DIRECTORY / "config/demos/02_vanhamel_rx_ab.config").read_text(encoding="utf-8"))
    frozen = _read_json("demo.config")
    assert installed["settings"] == frozen["settings"]
    assert reference_run.context.reference_snr_correction_db == 1.6
    assert frozen["settings"]["results_view"]["benchmark"]["station_evidence_time_bin"] == "12h"
    assert set(reference_run.points.station) == {"M7AEO"}
    assert set(reference_run.points.grid) == {"IO82"}
    assert reference_run.temporal["kind"] == "selected_benchmark_temporal"
    assert reference_run.temporal["selected_identity_count"] == 1


def test_actual_sql_and_post_fetch_reproduce_independent_source_groups(reference_run):
    assert len(reference_run.source_rows) == 12545
    assert len(reference_run.sql_rows) == 7166
    assert len(reference_run.processed) == 7139
    _assert_scientific_rows(reference_run.sql_rows, _read_csv("expected_sql_rows.csv"))
    _assert_scientific_rows(reference_run.processed, _read_csv("expected_retained_rows.csv"))


def test_every_paired_component_and_cycle_matches_raw_reference(reference_run):
    _assert_exact_trace(reference_run.points)
    expected = _read_csv("expected_paired_rows.csv")
    paired = reference_run.units[reference_run.units.metric.notna()].reset_index(drop=True)
    assert len(paired) == len(expected)
    for column in ("target_snr_db", "reference_snr_db"):
        np.testing.assert_allclose(paired[column], expected[column], rtol=0, atol=1e-12)
    source = reference_run.source_rows.set_index("id")
    for side, callsign in (("target", "ON4AWM0"), ("reference", "ON4AWM1")):
        ids = expected[f"{side}_report_ids"].astype(str)
        assert not ids.str.contains(";").any()
        reports = source.loc[ids.astype("int64")].reset_index()
        assert reports.rx_sign.eq(callsign).all()
        assert reports.tx_sign.eq("M7AEO").all() and reports.tx_loc.str.upper().eq("IO82").all()
        np.testing.assert_array_equal(reports.snr, expected[f"{side}_report_snr_db"])
        np.testing.assert_array_equal(reports.power, expected[f"{side}_report_power_dbm"])
        np.testing.assert_array_equal(
            _utc_nanoseconds(reports.time) // 120_000_000_000,
            expected.time_slot,
        )


def test_seven_independent_paper_landmarks_and_extreme_span(reference_run):
    amplitudes = _paper_landmark_values(reference_run.points)
    # Independently read largest positive 9.3 minus deepest negative -6.5.
    assert amplitudes[2] - amplitudes[4] == pytest.approx(15.8, abs=0.8)
    paper = _read_json("paper_features.json")
    assert paper["published_labels_and_caption"]["rotation_measurement_point"] == 750
    assert paper["landmark_readout_policy"]["index_tolerance_receptions"] == 5
    assert paper["landmark_readout_policy"]["amplitude_tolerance_db"] == 0.4


def test_twenty_reception_slices_preserve_medians_iqr_and_extremes(reference_run):
    expected = _read_csv("expected_reception_slices_20.csv")
    points = reference_run.points
    groups = np.arange(len(points)) * 20 // len(points)
    assert len(expected) == 20 and expected.joint_spots.sum() == 1441
    _assert_group_statistics(points, groups, expected)
    for group_index, rows in points.groupby(groups):
        assert rows.index.min() + 1 == expected.iloc[group_index].first_reception_index
        assert rows.index.max() + 1 == expected.iloc[group_index].last_reception_index


def test_selected_station_chart_12h_counts_quartiles_and_density(reference_run):
    profiles = reference_run.temporal["prepared_profiles"]
    counts, summary, edges, centers = _compare_temporal_profile_values(profiles["chronological"]["12h"])
    expected = _read_csv("expected_12h.csv")
    assert len(summary) == len(expected) == 28
    # Empty bins have no summary observations (NaN), and zero density counts.
    np.testing.assert_array_equal(summary["count"].fillna(0), expected.joint_spots)
    assert summary.loc[expected.joint_spots.eq(0)].isna().all().all()
    for column in ("median", "q1", "q3"):
        np.testing.assert_allclose(summary[column], expected[f"{column}_delta_snr_db"], rtol=0, atol=1e-12, equal_nan=True)
    starts = pd.DatetimeIndex(pd.to_datetime(expected.bin_start_utc, utc=True))
    ends = pd.DatetimeIndex(pd.to_datetime(expected.bin_end_utc, utc=True))
    assert pd.DatetimeIndex(matplotlib_dates.num2date(edges[:-1], tz="UTC")).equals(starts)
    assert pd.DatetimeIndex(matplotlib_dates.num2date(edges[1:], tz="UTC")).equals(ends)
    assert pd.DatetimeIndex(matplotlib_dates.num2date(centers, tz="UTC")).equals(starts + (ends - starts) / 2)
    density = _read_csv("expected_density_12h.csv").pivot(index="delta_snr_bin_db", columns="bin_index", values="joint_spots")
    np.testing.assert_array_equal(counts, density.to_numpy())
    np.testing.assert_array_equal(counts.sum(axis=0), expected.joint_spots)
    np.testing.assert_array_equal(profiles["y_edges"], np.arange(density.index.min() - .5, density.index.max() + 1.5))
    assert counts.sum() == 1441
    # The extreme tails are retained in their own bins, not clipped to the IQR.
    assert density.index.min() == -7 and density.index.max() == 9
    assert counts[0].sum() > 0 and counts[-1].sum() > 0


@pytest.mark.parametrize("split_kind", ["elapsed_time", "reception_750"])
def test_before_after_summaries_use_paired_observations(reference_run, split_kind):
    expected = _read_csv("expected_halves.csv")
    expected = expected[expected.split_kind.eq(split_kind)].reset_index(drop=True)
    points = reference_run.points
    if split_kind == "elapsed_time":
        start = pd.Timestamp(reference_run.configuration["start_utc"])
        end = pd.Timestamp(reference_run.configuration["end_utc"])
        groups = points.plot_time.ge(start + (end - start) / 2).astype(int)
    else:
        groups = (np.arange(len(points)) >= 750).astype(int)
    _assert_group_statistics(points, groups, expected)
    assert expected.iloc[1].median_delta_snr_db - expected.iloc[0].median_delta_snr_db == pytest.approx(3)


@pytest.mark.parametrize("mutation", ["reverse_subtraction", "clip_extremes", "shift_reception_order"])
def test_paper_anchors_reject_wrong_sign_clipping_and_misalignment(reference_run, mutation):
    changed = reference_run.points.copy()
    if mutation == "reverse_subtraction":
        changed["metric"] = -changed.metric
    elif mutation == "clip_extremes":
        changed["metric"] = changed.metric.clip(-4, 7)
    else:
        changed["metric"] = np.roll(changed.metric.to_numpy(), 20)
    with pytest.raises(AssertionError):
        _paper_landmark_values(changed)


@pytest.mark.parametrize("wrong_correction", [1.2, 1.5])
def test_exact_trace_rejects_correction_drift_even_inside_paper_tolerance(reference_run, wrong_correction):
    changed = _calculate_run(reference_run.source_rows, reference_correction_db=wrong_correction)
    with pytest.raises(AssertionError):
        _assert_exact_trace(changed.points)
    if wrong_correction == 1.2:
        with pytest.raises(AssertionError):
            _paper_landmark_values(changed.points)
    else:
        # A 0.1 dB shift can fit a raster's tolerance; exact frozen values detect it.
        _paper_landmark_values(changed.points)
