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
from ui.config_io import apply_config_state_values
from frozen_reference_adapter import validate_frozen_reference_document, frozen_context_projection, frozen_document_projection
from ui.inspector.evidence_data import (
    _build_compare_unit_rows, _compare_joint_evidence_points,
    _retain_thresholded_compare_outcomes,
)
from ui.inspector.view_models import build_compare_inspector_view_model
from ui.plots.evidence_figures import (
    _compare_temporal_profile_values, _selected_evidence_export_recipe,
    _temporal_metric_summary, _relative_density_values,
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
        "expected_density_12h_correction_aware_v1.csv", "temporal_density_revision_v1.json",
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
    configuration = validate_frozen_reference_document(_read_json("demo.config"))
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
         analysis_kind=analysis.analysis_kind,
        center_latitude=latitude, center_longitude=longitude,
        min_spots=context.min_joint_spots_per_station,
        min_opportunities=context.min_confirmed_opportunities_per_peer,
        base_min_stations=context.min_joint_stations_per_map_segment,



    )
    assert preparation.diagnostic is None and preparation.map_data is not None
    stations = preparation.map_data.station_rows
    inspector = build_compare_inspector_view_model(
        stations, analysis_id=analysis.id,
        analysis_context=context, presentation_context=presentation,
    )
    units = _build_compare_unit_rows(
        processed, stations,
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
        points, "Vanhamel Figure 6: M7AEO (IO82)", "12h",
        reference_snr_correction_db=context.reference_snr_correction_db,
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
    assert installed["settings"] == frozen_document_projection(frozen)["settings"]
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
    density_rows = _read_csv("expected_density_12h_correction_aware_v1.csv")
    density = density_rows.pivot(index="metric_bin_id", columns="bin_index", values="joint_spots")
    np.testing.assert_array_equal(counts, density.to_numpy())
    np.testing.assert_array_equal(counts.sum(axis=0), expected.joint_spots)
    cells = density_rows.drop_duplicates("metric_bin_id").sort_values("metric_bin_id")
    independent_edges = np.append(cells.cell_lower_db, cells.cell_upper_db.iloc[-1])
    np.testing.assert_allclose(profiles["y_edges"], independent_edges, rtol=0, atol=2e-15)
    np.testing.assert_array_equal(profiles["metric_bin_ids"], density.index)
    legacy_density = _read_csv("expected_density_12h.csv").pivot(index="delta_snr_bin_db", columns="bin_index", values="joint_spots")
    np.testing.assert_array_equal(counts, legacy_density.to_numpy())
    np.testing.assert_allclose(independent_edges, np.arange(-7.5, 10.5) + .4, rtol=0, atol=2e-15)
    assert counts.sum() == 1441
    # The extreme tails are retained in their own bins, not clipped to the IQR.
    assert density.index.min() == -5 and density.index.max() == 11
    assert counts[0].sum() > 0 and counts[-1].sum() > 0
    occupied = np.flatnonzero(counts[:, 0])
    np.testing.assert_allclose([independent_edges[occupied[0]], independent_edges[occupied[-1] + 1]], [-4.1, 1.9], rtol=0, atol=1e-15)


def test_correction_translates_grid_and_statistics_once_without_changing_population(reference_run):
    """Replay frozen raw reports at zero and +1.6 dB through production SQL/preparation."""
    zero = _calculate_run(reference_run.source_rows, reference_correction_db=0.0)
    assert len(zero.points) == len(reference_run.points) == 1441
    np.testing.assert_array_equal(_utc_nanoseconds(zero.points.plot_time), _utc_nanoseconds(reference_run.points.plot_time))
    np.testing.assert_allclose(reference_run.points.metric, zero.points.metric - 1.6, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(reference_run.units.target_snr_db, zero.units.target_snr_db)
    np.testing.assert_allclose(reference_run.units.reference_snr_db, zero.units.reference_snr_db + 1.6, rtol=0, atol=1e-12, equal_nan=True)
    corrected_profiles = reference_run.temporal["prepared_profiles"]
    zero_profiles = zero.temporal["prepared_profiles"]
    np.testing.assert_array_equal(corrected_profiles["metric_bin_ids"], zero_profiles["metric_bin_ids"])
    np.testing.assert_array_equal(corrected_profiles["y_edges"], np.asarray(zero_profiles["y_edges"]) - 1.6)
    for zero_profile, corrected_profile in (
        (zero_profiles["chronological"]["12h"], corrected_profiles["chronological"]["12h"]),
        (zero_profiles["folded"], corrected_profiles["folded"]),
    ):
        zero_counts, zero_summary, zero_edges, zero_centers = _compare_temporal_profile_values(zero_profile)
        counts, summary, time_edges, time_centers = _compare_temporal_profile_values(corrected_profile)
        np.testing.assert_array_equal(counts, zero_counts)
        np.testing.assert_array_equal(time_edges, zero_edges)
        np.testing.assert_array_equal(time_centers, zero_centers)
        for column in ("median", "q1", "q3"):
            np.testing.assert_allclose(summary[column], zero_summary[column] - 1.6, rtol=0, atol=1e-12, equal_nan=True)
        corrected_density = _relative_density_values(counts)
        zero_density = _relative_density_values(zero_counts)
        np.testing.assert_array_equal(corrected_density.data, zero_density.data)
        np.testing.assert_array_equal(np.ma.getmaskarray(corrected_density), np.ma.getmaskarray(zero_density))
    _assert_exact_trace(reference_run.points)
    _paper_landmark_values(reference_run.points)


def test_density_only_revision_reproduces_from_raw_reports_without_changing_legacy_oracles(tmp_path):
    """Keep the independent density revision reproducible and scientific sources frozen."""
    from scripts.internal import build_vanhamel_temporal_density_reference as calculator

    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in REFERENCE_DIRECTORY.glob("expected_*")}
    frozen_metadata_bytes = (REFERENCE_DIRECTORY / "temporal_density_revision_v1.json").read_bytes()
    calculator.calculate_density_reference(REFERENCE_DIRECTORY, tmp_path)
    filename = "expected_density_12h_correction_aware_v1.csv"
    assert (tmp_path / filename).read_bytes() == (REFERENCE_DIRECTORY / filename).read_bytes()
    generated_metadata = json.loads((tmp_path / "temporal_density_revision_v1.json").read_text(encoding="utf-8"))
    frozen_metadata = json.loads(frozen_metadata_bytes)
    # Script relocation changes only current-generation provenance. Preserve the
    # original artifact's path/hash and compare every scientific field exactly.
    assert generated_metadata.pop("calculator_path") == "scripts/internal/build_vanhamel_temporal_density_reference.py"
    assert generated_metadata.pop("calculator_sha256") == hashlib.sha256(Path(calculator.__file__).read_bytes()).hexdigest()
    assert frozen_metadata.pop("calculator_path") == "scripts/build_vanhamel_temporal_density_reference.py"
    assert len(frozen_metadata.pop("calculator_sha256")) == 64
    assert generated_metadata == frozen_metadata
    assert (REFERENCE_DIRECTORY / "temporal_density_revision_v1.json").read_bytes() == frozen_metadata_bytes
    assert before == {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in REFERENCE_DIRECTORY.glob("expected_*")}


def test_comparison_preparation_uses_production_values_without_reading_expectations(reference_run, monkeypatch):
    from scripts.internal import build_vanhamel_rotation_comparison as comparison

    changed = SimpleNamespace(**vars(reference_run))
    changed.points = reference_run.points.copy()
    changed.units = reference_run.units.copy()
    changed.points["metric"] += 2
    changed.units["target_snr_db"] += 2
    changed.units["metric"] += 2

    def reject_expected_reads(*args, **kwargs):
        pytest.fail("Presentation preparation must not read frozen expected CSVs")

    with monkeypatch.context() as guard:
        guard.setattr(comparison.pd, "read_csv", reject_expected_reads)
        original = comparison.prepare_reconstruction(reference_run)
        mutated = comparison.prepare_reconstruction(changed)
        original_mapping = comparison.prepare_reception_bin_mapping(original)
        changed_mapping = comparison.prepare_reception_bin_mapping(mutated)
    np.testing.assert_allclose(mutated.points.metric, original.points.metric + 2, rtol=0, atol=1e-12)
    np.testing.assert_allclose(mutated.target_trace, original.target_trace + 2, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(mutated.reference_trace, original.reference_trace)
    np.testing.assert_array_equal(mutated.reception_indexes, original.reception_indexes)
    np.testing.assert_array_equal(changed_mapping.reception_edges, original_mapping.reception_edges)
    np.testing.assert_array_equal(changed_mapping.count_grid, original_mapping.count_grid)
    np.testing.assert_allclose(changed_mapping.y_edges, original_mapping.y_edges + 2, rtol=0, atol=1e-12)
    original_summary = _compare_temporal_profile_values(original.temporal_recipe["prepared_profiles"]["chronological"]["12h"])[1]
    changed_summary = _compare_temporal_profile_values(mutated.temporal_recipe["prepared_profiles"]["chronological"]["12h"])[1]
    for column in ("median", "q1", "q3"):
        np.testing.assert_allclose(changed_summary[column], original_summary[column] + 2, rtol=0, atol=1e-12, equal_nan=True)
    # The oracle still rejects a scientific drift; it does not supply the
    # reconstructed trace or overwrite production values to hide the change.
    comparison.assert_reference_reconstruction(original)
    with pytest.raises(AssertionError):
        comparison.assert_reference_reconstruction(mutated)


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


def test_reception_mapping_retains_time_membership_gaps_and_final_partial_bin(reference_run):
    """Preserve exact UTC membership, zero-width gaps and the clipped final bin."""
    from scripts.internal.build_vanhamel_rotation_comparison import prepare_reconstruction, prepare_reception_bin_mapping

    reconstruction = prepare_reconstruction(reference_run)
    mapping = prepare_reception_bin_mapping(reconstruction)
    assert len(mapping.records) == 28
    assert mapping.pair_counts.sum() == 1441
    assert [r["bin_id"] for r in mapping.records if not r["pair_count"]] == [2, 18, 26]
    assert [r["bin_id"] for r in mapping.records if r["first_reception"] is None] == [2, 18, 26]
    np.testing.assert_array_equal(np.flatnonzero(np.diff(mapping.reception_edges) == 0) + 1, [2, 18, 26])
    assert mapping.reception_edges[0] == 0.5
    assert mapping.reception_edges[-1] == 1441.5

    for bin_id, first, last, count in ((1, 1, 99, 99), (13, 660, 755, 96), (14, 756, 759, 4), (15, 760, 849, 90), (16, 850, 850, 1), (28, 1437, 1441, 5)):
        actual = mapping.records[bin_id - 1]
        assert (actual["first_reception"], actual["last_reception"], actual["pair_count"]) == (first, last, count)
        assert np.all(mapping.point_bin_indexes[first - 1:last] == bin_id - 1)

    assert mapping.edge_times[0] == pd.Timestamp("2021-05-01T17:15:00Z")
    assert mapping.edge_times[-1] == pd.Timestamp("2021-05-15T07:00:00Z")
    assert mapping.edge_times[-1] - mapping.edge_times[-2] == pd.Timedelta(hours=1, minutes=45)


def test_bridge_retains_native_density_values_masks_colours_and_vertical_cells(reference_run):
    """Change only reception geometry while retaining native density rendering."""
    from matplotlib.collections import QuadMesh
    from core.matplotlib_runtime import dispose_agg_figure
    from scripts.internal.build_vanhamel_rotation_comparison import (prepare_reconstruction, prepare_reception_bin_mapping, draw_reception_density_bridge)
    from ui.plots.evidence_figures import render_selected_evidence_export_figure
    from ui.results_export import _style_figure_for_paper

    reconstruction = prepare_reconstruction(reference_run)
    mapping = prepare_reception_bin_mapping(reconstruction)
    figure = render_selected_evidence_export_figure(reconstruction.temporal_recipe)
    try:
        _style_figure_for_paper(figure)
        native_axis = next(a for a in figure.axes if a.get_gid() == "compare-temporal-chronological-axis")
        native = next(c for c in native_axis.collections if isinstance(c, QuadMesh))
        bridge_axis = figure.add_axes([0.1, 0.1, 0.8, 0.2])
        bridge = draw_reception_density_bridge(bridge_axis, native, mapping)
        np.testing.assert_array_equal(bridge.get_array().data, native.get_array().data)
        np.testing.assert_array_equal(np.ma.getmaskarray(bridge.get_array()), np.ma.getmaskarray(native.get_array()))
        assert bridge.norm is native.norm
        assert bridge.get_cmap() is native.get_cmap()
        np.testing.assert_array_equal(bridge.to_rgba(bridge.get_array()), native.to_rgba(native.get_array()))
        np.testing.assert_array_equal(bridge.get_coordinates()[:, 0, 1], native.get_coordinates()[:, 0, 1])
        np.testing.assert_array_equal(bridge.get_coordinates()[0, :, 0], mapping.reception_edges)
    finally:
        dispose_agg_figure(figure)
