"""Mandatory offline reference for the Griffiths April 2017 temporal evidence.

Frozen source reports enter newly generated production SQL through the bounded
SQLite compatibility adapter, then real post-fetch, map, Inspector and temporal
recipe calculations. Reviewed expectations are read only after calculation.
This is not native ClickHouse-engine or geographic-distance validation.
"""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import socket

import matplotlib.dates as matplotlib_dates
import numpy as np
import pandas as pd
import pytest
import requests

from reference_sql import execute_generated_sql

from config import BAND_MAP
from core.analysis_context import AnalysisContext
from core.analysis_plan import AnalysisPlan, DECODE_FILTER_LEGACY
from core.analysis_runner import (
    apply_post_fetch_filters, build_analysis_batches, should_retry_without_decode_filter,
)
from core.map_data import build_map_data_result
from core.math_utils import locator_to_latlon
from core.presentation_context import PresentationContext
from i18n import T
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.config_io import apply_config_state_values
from frozen_reference_adapter import validate_frozen_reference_document, frozen_context_projection
from ui.inspector.evidence_data import (
    _build_compare_unit_rows,
    _compare_joint_evidence_points,
    _retain_thresholded_compare_outcomes,
)
from ui.inspector.view_models import build_compare_inspector_view_model
from ui.plots.evidence_figures import (
    _compare_temporal_profile_values,
    _recipe_uses_authoritative_temporal_iqr,
    _segment_temporal_evidence_export_recipe,
)


REFERENCE_DIRECTORY = (
    Path(__file__).parent / "reference_fixtures" / "griffiths_fig3_temporal_v1"
)
FIG6_REFERENCE_DIRECTORY = REFERENCE_DIRECTORY.parent / "griffiths_fig6_diurnal_v1"
FIG6_PAPER_DIRECTORY = REFERENCE_DIRECTORY.parent / "griffiths_fig6_paper_v1"
FIG3_PAPER_DIRECTORY = REFERENCE_DIRECTORY.parent / "griffiths_fig3_paper_v1"
FIG3_PAPER_FEATURE_IDS = (
    "early_april_concentration", "mid_april_concentration",
    "late_april_concentration", "mid_april_negative_tail",
)
FIG3_PAPER_MEAN_IDS = (
    "isolated_april_06", "isolated_april_13", "isolated_april_15",
    "first_half_daily_mean_minimum", "first_half_daily_mean_maximum",
)
REQUIRED_REFERENCE_FILES = {
    "analysis_context.json", "capture_provenance.json", "demo.config",
    "expected_24h.csv", "expected_3h.csv", "expected_utc_hour.csv",
    "expected_density_24h.csv", "expected_density_3h.csv",
    "expected_density_utc_hour.csv", "expected_paired_rows.parquet",
    "expected_summary.json", "input_sql_rows.parquet", "query_legacy.sql",
    "README.md", "source_rows.parquet", "source_rows_query.sql",
    "verification.json",
}
FIG6_REQUIRED_REFERENCE_FILES = REQUIRED_REFERENCE_FILES | {
    "expected_1h.csv", "expected_6h.csv",
    "expected_density_1h.csv", "expected_density_6h.csv",
    "expected_paired_rows_22000km.parquet", "expected_utc_hour_22000km.csv",
    "expected_density_utc_hour_22000km.csv",
}


def _read_reference_json(filename, reference_directory=REFERENCE_DIRECTORY):
    return json.loads((reference_directory / filename).read_text(encoding="utf-8"))


def _verify_reference_manifest(reference_directory, required_files):
    """Missing, truncated or accidentally edited reference files must fail."""
    manifest_path = reference_directory / "manifest.json"
    assert manifest_path.is_file(), f"Mandatory reference fixture missing: {manifest_path}"
    manifest = _read_reference_json("manifest.json", reference_directory)
    assert manifest["schema_version"] == 1
    paths = [record["path"] for record in manifest["files"]]
    assert len(paths) == len(set(paths)), "Duplicate reference manifest paths"
    assert required_files.issubset(paths)
    for record in manifest["files"]:
        artifact_path = (reference_directory / record["path"]).resolve()
        assert artifact_path.is_relative_to(reference_directory.resolve())
        assert artifact_path.is_file(), f"Mandatory reference file missing: {artifact_path}"
        contents = artifact_path.read_bytes()
        assert len(contents) == record["bytes"], f"Reference size changed: {record['path']}"
        assert hashlib.sha256(contents).hexdigest() == record["sha256"], (
            f"Reference content changed: {record['path']}"
        )
    return manifest


@pytest.fixture(scope="module")
def verified_reference_manifest():
    return _verify_reference_manifest(REFERENCE_DIRECTORY, REQUIRED_REFERENCE_FILES)


@pytest.fixture(scope="module")
def fig6_verified_reference_manifest():
    return _verify_reference_manifest(FIG6_REFERENCE_DIRECTORY, FIG6_REQUIRED_REFERENCE_FILES)


@dataclass(frozen=True)
class TemporalReferenceRun:
    configuration: dict
    context: AnalysisContext
    analysis: AnalysisPlan
    input_row_count: int
    processed_rows: pd.DataFrame
    station_rows: pd.DataFrame
    comparison_units: pd.DataFrame
    paired_points: pd.DataFrame
    temporal_recipes: dict
    reference_directory: Path
    source_row_count: int
    strict_row_count: int
    sql_rows: pd.DataFrame


def _reject_network_access(*args, **kwargs):
    pytest.fail("The frozen temporal reference must not access the network")


def _build_temporal_recipe(paired_points, configuration, time_bin, time_bin_options=("24h", "3h"), *, reference_snr_correction_db):
    """Use the actual export recipe without invoking its figure renderer."""
    return _segment_temporal_evidence_export_recipe(
        paired_points[["plot_time", "metric"]],
        "Griffiths April 2017 temporal reference", time_bin, "Joint spots",
        reference_snr_correction_db=reference_snr_correction_db,
        analysis_start_t=configuration["start_utc"],
        analysis_end_t=configuration["end_utc"],
        chronological_title="Chronological Delta SNR ({time_bin})",
        chronological_x_label="UTC", chronological_unavailable_text="No evidence",
        metric_axis_label="Delta SNR (dB)", folded_title="UTC hour",
        folded_x_label="UTC hour", folded_date_annotation="{utc_date_count} dates",
        density_label="Relative Joint spot density", folded_unavailable_text="No evidence",
        median_focus_axis_label="Delta SNR (dB)", median_label="Median",
        bin_median_label="Bin median", bin_iqr_label="Bin IQR",
        time_bin_options=time_bin_options,
    )


def _prepare_reference_run(reference_directory, time_bins, *, max_peer_distance_km=None, source_rows=None):
    """Replay source reports through production SQL and evidence preparation.

    Neither captured SQL-result snapshots nor expected paired rows are read.
    ``source_rows`` permits controlled input perturbations for sensitivity tests.
    """
    with pytest.MonkeyPatch.context() as network_guard:
        network_guard.setattr(requests.sessions.Session, "request", _reject_network_access)
        network_guard.setattr(socket, "create_connection", _reject_network_access)
        network_guard.setattr(socket.socket, "connect", _reject_network_access)
        network_guard.setattr(socket.socket, "connect_ex", _reject_network_access)
        configuration = validate_frozen_reference_document(_read_reference_json("demo.config", reference_directory))
        if max_peer_distance_km is not None:
            configuration["max_peer_distance_km"] = max_peer_distance_km
        session_values = {"lang": "en"}
        apply_config_state_values(configuration, session_values)
        session_values["run_mode"] = configuration["analysis_direction"].upper()
        context = build_analysis_context_from_session_state(session_values)
        center_latitude, center_longitude = locator_to_latlon(context.qth)
        presentation_context = PresentationContext(solar_label="All", labels=T["en"])
        analyses = build_analysis_batches(
            context, configuration["start_utc"], configuration["end_utc"],
            center_latitude, center_longitude,
            f"AND band = '{BAND_MAP[context.band]}'",
            presentation_context=presentation_context,
        )
        assert len(analyses) == 1
        source_rows = pd.read_parquet(reference_directory / "source_rows.parquet") if source_rows is None else source_rows
        analysis = analyses[0]
        strict_rows = execute_generated_sql(analysis.query, source_rows)
        if should_retry_without_decode_filter(strict_rows, analysis):
            analysis = analysis.for_legacy_query()
            input_rows = execute_generated_sql(analysis.query, source_rows)
        else:
            input_rows = strict_rows
        input_row_count = len(input_rows)
        sql_rows = input_rows.copy()
        processed_rows, warning_message = apply_post_fetch_filters(
            input_rows, analysis, context, center_latitude, center_longitude, T["en"],
        )
        assert warning_message is None
        map_preparation = build_map_data_result(
            processed_rows, analysis_id=analysis.id, is_compare=analysis.is_compare,
             analysis_kind=analysis.analysis_kind,
            center_latitude=center_latitude, center_longitude=center_longitude,
            min_spots=context.min_joint_spots_per_station,
            min_opportunities=context.min_confirmed_opportunities_per_peer,
            base_min_stations=context.min_joint_stations_per_map_segment,



        )
        assert map_preparation.diagnostic is None
        assert map_preparation.map_data is not None
        station_rows = map_preparation.map_data.station_rows
        inspector_model = build_compare_inspector_view_model(
            station_rows, analysis_id=analysis.id,
            analysis_context=context, presentation_context=presentation_context,
        )
        comparison_units = _build_compare_unit_rows(
            processed_rows, station_rows,
            paired_identity_df=inspector_model.build_evidence_identities(),
        )
        comparison_units = _retain_thresholded_compare_outcomes(comparison_units, station_rows)
        paired_points = _compare_joint_evidence_points(
            comparison_units, require_paired_eligible=True,
        )
        temporal_recipes = {
            time_bin: _build_temporal_recipe(
                paired_points, configuration, time_bin, time_bins,
                reference_snr_correction_db=context.reference_snr_correction_db,
            )
            for time_bin in time_bins
        }
    return TemporalReferenceRun(
        configuration, context, analysis, input_row_count, processed_rows,
        station_rows, comparison_units, paired_points, temporal_recipes, reference_directory,
        len(source_rows), len(strict_rows), sql_rows,
    )


@pytest.fixture(scope="module")
def fig3_reference_run(verified_reference_manifest):
    return _prepare_reference_run(REFERENCE_DIRECTORY, ("24h", "3h"))


@pytest.fixture(scope="module")
def fig6_reference_run(fig6_verified_reference_manifest):
    return _prepare_reference_run(FIG6_REFERENCE_DIRECTORY, ("24h", "3h", "1h", "6h"))


@pytest.fixture(scope="module", params=["fig3_reference_run", "fig6_reference_run"], ids=["fig3", "fig6"])
def reference_run(request):
    return request.getfixturevalue(request.param)


def test_reference_files_are_complete_and_intact(verified_reference_manifest):
    assert verified_reference_manifest["fixture_id"] == "griffiths_squibb_fig3_temporal_2017_04"


def test_reference_configuration_and_processed_population(reference_run):
    expected = _read_reference_json("expected_summary.json", reference_run.reference_directory)
    assert reference_run.context.to_dict() == frozen_context_projection(_read_reference_json("analysis_context.json", reference_run.reference_directory))
    assert reference_run.analysis.decode_filter_mode == DECODE_FILTER_LEGACY
    assert reference_run.configuration["start_utc"] == pd.Timestamp(expected["start_utc"])
    assert reference_run.configuration["end_utc"] == pd.Timestamp(expected["end_utc_exclusive"])
    pipeline = expected["pipeline"]
    assert reference_run.input_row_count == pipeline["input_sql_rows"]
    assert len(reference_run.processed_rows) == pipeline["processed_rows"]
    assert len(reference_run.station_rows) == pipeline["station_rows"]
    assert reference_run.comparison_units["outcome"].value_counts().to_dict() == pipeline["outcomes"]
    assert reference_run.comparison_units["paired_eligible"].groupby(
        [reference_run.comparison_units["peer_sign"], reference_run.comparison_units["peer_grid"]],
        observed=True,
    ).any().sum() == expected["global"]["paired_peer_identities"]


def _canonical_paired_rows(reference_run):
    """Project freshly computed paired evidence without reading any oracle."""
    identity_keys = ["evidence_utc", "peer_sign", "peer_grid"]
    actual = reference_run.paired_points.rename(columns={
        "plot_time": "evidence_utc", "station": "peer_sign", "grid": "peer_grid",
        "metric": "delta_snr_db",
    })[identity_keys + ["delta_snr_db"]].merge(
        reference_run.comparison_units[identity_keys + ["target_snr_db", "reference_snr_db"]],
        on=identity_keys, how="left", validate="one_to_one",
    )
    actual["time_slot"] = actual["evidence_utc"].dt.as_unit("ns").astype("int64") // 120_000_000_000
    return actual


def _assert_paired_rows_match_reference(reference_run, filename="expected_paired_rows.parquet"):
    actual = _canonical_paired_rows(reference_run)
    expected = pd.read_parquet(reference_run.reference_directory / filename)
    sort_keys = ["time_slot", "peer_sign", "peer_grid"]
    pd.testing.assert_frame_equal(
        actual[expected.columns].sort_values(sort_keys).reset_index(drop=True),
        expected.sort_values(sort_keys).reset_index(drop=True),
        check_dtype=False, check_exact=True,
    )
    return actual


def test_all_paired_rows_match_the_reviewed_reference(reference_run):
    actual = _assert_paired_rows_match_reference(reference_run)
    summary = _read_reference_json("expected_summary.json", reference_run.reference_directory)["global"]
    assert len(actual) == summary["joint_spots"]
    assert actual["delta_snr_db"].median() == summary["median_delta_snr_db"]
    assert actual["delta_snr_db"].mean() == pytest.approx(summary["mean_delta_snr_db"], abs=1e-12, rel=0)
    for recipe in reference_run.temporal_recipes.values():
        assert recipe["utc_date_count"] == summary["days"]
        assert recipe["median_focus"]["median_db"] == summary["median_delta_snr_db"]


def test_source_sql_replay_preserves_frozen_aggregation(reference_run):
    """The SQL-result capture is an assertion target, never a pipeline input."""
    expected = pd.read_parquet(reference_run.reference_directory / "input_sql_rows.parquet")
    columns = ["time_slot", "peer_sign", "peer_grid", "snr_u_norm", "snr_r_norm", "has_u", "has_r", "best_ref_sign"]
    keys = ["time_slot", "peer_sign", "peer_grid"]
    # CSV ingestion of the original ClickHouse capture converted empty absent-
    # reference strings to NA; SQLite returns the aggregate's empty string.
    expected["best_ref_sign"] = expected.best_ref_sign.fillna("")
    pd.testing.assert_frame_equal(
        reference_run.sql_rows[columns].sort_values(keys).reset_index(drop=True),
        expected[columns].sort_values(keys).reset_index(drop=True),
        check_dtype=False, check_exact=True,
    )
    assert reference_run.source_row_count > reference_run.input_row_count
    assert reference_run.strict_row_count == 0
    assert reference_run.analysis.decode_filter_mode == DECODE_FILTER_LEGACY


def test_source_replay_is_independent_of_expected_and_sql_capture_reads(monkeypatch):
    """Forbid all non-source parquet inputs while the scientific path executes."""
    read_parquet = pd.read_parquet
    observed_reads = []

    def read_source_only(path, *args, **kwargs):
        path = Path(path)
        assert path.name == "source_rows.parquet", f"Replay read a derived fixture: {path}"
        observed_reads.append(path.name)
        return read_parquet(path, *args, **kwargs)

    monkeypatch.setattr(pd, "read_parquet", read_source_only)
    replay = _prepare_reference_run(FIG6_REFERENCE_DIRECTORY, ("12h",))
    projected = _canonical_paired_rows(replay)
    assert observed_reads == ["source_rows.parquet"]
    assert len(projected) == len(replay.paired_points) > 0
    assert replay.temporal_recipes["12h"]["prepared_profiles"]["chronological"]["12h"]


def test_source_snr_perturbation_changes_computed_pairs_and_temporal_grid(fig6_reference_run):
    """A changed measurement must propagate to plotted evidence and fail its oracle."""
    before = _canonical_paired_rows(fig6_reference_run)
    witness = before.sort_values(["evidence_utc", "peer_sign", "peer_grid"]).iloc[0]
    source = pd.read_parquet(FIG6_REFERENCE_DIRECTORY / "source_rows.parquet")
    selected = (
        source.rx_sign.eq("G3ZIL") & source.time.eq(witness.evidence_utc)
        & source.tx_sign.eq(witness.peer_sign) & source.tx_loc.eq(witness.peer_grid)
    )
    assert selected.any()
    source.loc[selected, "snr"] += 3
    changed_run = _prepare_reference_run(FIG6_REFERENCE_DIRECTORY, ("24h", "3h", "1h", "6h"), source_rows=source)
    after = _canonical_paired_rows(changed_run)
    keys = ["evidence_utc", "peer_sign", "peer_grid"]
    comparison = before[keys + ["delta_snr_db"]].merge(after[keys + ["delta_snr_db"]], on=keys,
                                                       validate="one_to_one", suffixes=("_before", "_after"))
    difference = comparison.delta_snr_db_after - comparison.delta_snr_db_before
    assert len(comparison) == len(before) == len(after)
    assert difference.ne(0).sum() == 1 and difference[difference.ne(0)].iloc[0] == 3
    old = fig6_reference_run.temporal_recipes["1h"]["prepared_profiles"]["folded"]["count_grid"]
    new = changed_run.temporal_recipes["1h"]["prepared_profiles"]["folded"]["count_grid"]
    assert not np.array_equal(old, new)
    with pytest.raises(AssertionError):
        _assert_paired_rows_match_reference(changed_run)


def test_figure3_hourly_density_uses_production_counts_and_preserves_12h_view(fig3_reference_run, monkeypatch):
    from scripts.internal import build_griffiths_figure3_comparisons as builder

    pairs = _canonical_paired_rows(fig3_reference_run)

    def reject_derived_inputs(*args, **kwargs):
        pytest.fail("Density presentation must use the supplied production pairs")

    with monkeypatch.context() as guard:
        guard.setattr(pd, "read_parquet", reject_derived_inputs)
        guard.setattr(pd, "read_csv", reject_derived_inputs)
        recipe = builder.temporal_recipe(
            pairs, reference_snr_correction_db=fig3_reference_run.context.reference_snr_correction_db,
        )
        density = builder.prepare_density_reconstruction(pairs, recipe)
    hourly, _, edges, _ = _compare_temporal_profile_values(recipe["prepared_profiles"]["chronological"]["1h"])
    half_daily, _, _, _ = _compare_temporal_profile_values(recipe["prepared_profiles"]["chronological"]["12h"])
    np.testing.assert_array_equal(density["counts"], hourly)
    assert hourly.shape[1] == 720 and hourly.sum() == len(pairs) == 57767
    np.testing.assert_allclose(np.diff(edges), 1 / 24, rtol=0, atol=5e-12)
    np.testing.assert_array_equal(np.diff(density["y_edges_db"]), 1)
    np.testing.assert_array_equal(hourly.reshape(hourly.shape[0], 60, 12).sum(axis=2), half_daily)
    np.testing.assert_array_equal(np.ma.getmaskarray(density["relative_density"]), hourly == 0)
    np.testing.assert_allclose(density["relative_density"].compressed(), 100 * hourly[hourly > 0] / hourly.max())
    assert len(density["native_days"]) == len(density["native_delta_snr_db"]) == len(pairs)
    np.testing.assert_array_equal(density["native_delta_snr_db"], pairs.delta_snr_db)
    np.testing.assert_allclose(density["native_days"],
                               (pairs.evidence_utc - builder.START).dt.total_seconds() / 86400,
                               rtol=0, atol=5e-12)


def test_figure3_density_artists_preserve_global_scale_and_all_native_coordinates():
    from scripts.internal import build_griffiths_figure3_comparisons as builder
    from core.matplotlib_runtime import dispose_agg_figure, matplotlib_operation_lock

    # Three first-hour observations occupy cell 0; the exact +0.5 dB
    # boundary belongs to cell 1 under the temporal half-open policy.
    # The next hour has two in that cell and a separate half-dB tie, while
    # the last observation remains in the grid beyond B's displayed y range.
    pairs = pd.DataFrame({
        "evidence_utc": pd.to_datetime([
            "2017-04-01T00:00Z", "2017-04-01T00:00Z", "2017-04-01T00:00Z", "2017-04-01T00:58Z",
            "2017-04-01T01:00Z", "2017-04-01T01:02Z", "2017-04-01T01:04Z", "2017-04-30T23:58Z",
        ], utc=True),
        "delta_snr_db": [0, 0, 0, .5, -.5, 0, 1.5, 35],
    })
    density = builder.prepare_density_reconstruction(
        pairs, builder.temporal_recipe(pairs, reference_snr_correction_db=0.0),
    )
    assert density["counts"].sum() == 8
    np.testing.assert_array_equal(density["counts"][0, :2], [3, 2])
    np.testing.assert_allclose(density["relative_density"][0, :2], [100, 200 / 3])
    assert density["counts"][1, 0] == 1
    assert density["counts"][2, 1] == density["counts"][35, -1] == 1
    expected_offsets = np.column_stack([
        (pairs.evidence_utc - builder.START).dt.total_seconds() / 86400,
        pairs.delta_snr_db,
    ])
    with matplotlib_operation_lock():
        figure, axis = builder.plt.subplots()
        try:
            mesh, markers = builder.draw_density_reconstruction(axis, density)
            assert mesh.cmap.name == "gray_r" and mesh.norm.vmin == 0 and mesh.norm.vmax == 100
            np.testing.assert_allclose(mesh.cmap(mesh.norm([0, 50, 100]))[:, :3],
                                       [[1, 1, 1], [.5, .5, .5], [0, 0, 0]], atol=1 / 255)
            np.testing.assert_array_equal(mesh.get_array().filled(-1), density["relative_density"].filled(-1))
            np.testing.assert_array_equal(mesh.get_coordinates()[0, :, 0], density["time_edges_days"])
            np.testing.assert_array_equal(mesh.get_coordinates()[:, 0, 1], density["y_edges_db"])
            np.testing.assert_allclose(markers.get_offsets(), expected_offsets, rtol=0, atol=5e-12)
            assert len(markers.get_offsets()) == 8  # includes the three coincident pairs
            assert markers.get_gid() == "figure3-all-native-pairs"
            assert np.all(markers.get_sizes() > 2.5) and markers.get_alpha() > .2
            np.testing.assert_array_equal(markers.get_facecolors()[:, :3], 0)
            assert axis.get_yscale() == "linear"
        finally:
            dispose_agg_figure(figure)


def _assert_temporal_profile_matches_reference(reference_run, profile_name, filename_suffix=""):
    profiles = reference_run.temporal_recipes["24h"]["prepared_profiles"]
    profile = profiles["folded"] if profile_name == "utc_hour" else profiles["chronological"][profile_name]
    counts, summary, edges, centers = _compare_temporal_profile_values(profile)
    expected = pd.read_csv(reference_run.reference_directory / f"expected_{profile_name}{filename_suffix}.csv")
    for actual_column, expected_column in (
        ("count", "joint_spots"), ("median", "median_delta_snr_db"),
        ("q1", "q1_delta_snr_db"), ("q3", "q3_delta_snr_db"),
    ):
        np.testing.assert_array_equal(summary[actual_column], expected[expected_column])
    expected_density = pd.read_csv(reference_run.reference_directory / f"expected_density_{profile_name}{filename_suffix}.csv")
    expected_counts = expected_density.pivot(
        index="delta_snr_bin_db", columns="bin_index", values="joint_spots",
    )
    np.testing.assert_array_equal(counts, expected_counts.to_numpy())
    np.testing.assert_array_equal(
        profiles["y_edges"],
        np.arange(expected_counts.index.min() - 0.5, expected_counts.index.max() + 1.5),
    )
    assert int(counts.sum()) == int(expected["joint_spots"].sum())
    if profile_name == "utc_hour":
        np.testing.assert_array_equal(expected["utc_hour"], np.arange(24))
        np.testing.assert_array_equal(edges, np.arange(25))
        np.testing.assert_array_equal(centers, np.arange(24) + 0.5)
    else:
        lower_bounds = pd.DatetimeIndex(pd.to_datetime(expected["bin_start_utc"], utc=True))
        upper_bounds = pd.DatetimeIndex(pd.to_datetime(expected["bin_end_utc"], utc=True))
        assert pd.DatetimeIndex(matplotlib_dates.num2date(edges[:-1], tz="UTC")).equals(lower_bounds)
        assert pd.DatetimeIndex(matplotlib_dates.num2date(edges[1:], tz="UTC")).equals(upper_bounds)
        assert pd.DatetimeIndex(matplotlib_dates.num2date(centers, tz="UTC")).equals(
            lower_bounds + (upper_bounds - lower_bounds) / 2
        )


@pytest.mark.parametrize("profile_name", ["24h", "3h", "utc_hour"])
def test_temporal_profiles_match_the_reviewed_reference(reference_run, profile_name):
    _assert_temporal_profile_matches_reference(reference_run, profile_name)


def test_chronological_selection_preserves_folded_evidence(reference_run):
    daily = reference_run.temporal_recipes["24h"]
    assert daily["time_bin"] == "24h"
    for time_bin, recipe in reference_run.temporal_recipes.items():
        assert recipe["time_bin"] == time_bin
        for field in ("count_grid", "median", "count", "q1", "q3", "x_edges", "x_centers"):
            np.testing.assert_array_equal(
                daily["prepared_profiles"]["folded"][field],
                recipe["prepared_profiles"]["folded"][field],
            )


def test_sparse_three_hour_bin_retains_statistics_without_iqr_support(fig3_reference_run):
    recipe = fig3_reference_run.temporal_recipes["3h"]
    assert recipe["iqr_min_count"] == 5
    assert _recipe_uses_authoritative_temporal_iqr(recipe)
    _, summary, _, _ = _compare_temporal_profile_values(
        recipe["prepared_profiles"]["chronological"]["3h"]
    )
    expected = pd.read_csv(REFERENCE_DIRECTORY / "expected_3h.csv")
    sparse_bins = expected[(expected["joint_spots"] > 0) & (expected["joint_spots"] < 5)]
    assert len(sparse_bins) == 1
    sparse_bin = sparse_bins.iloc[0]
    bin_index = int(sparse_bin["bin_index"])
    assert summary.loc[bin_index, "count"] == sparse_bin["joint_spots"]
    assert summary.loc[bin_index, "count"] < recipe["iqr_min_count"]
    assert summary.loc[bin_index, ["median", "q1", "q3"]].notna().all()


def test_fig6_reference_files_are_complete_and_intact(fig6_verified_reference_manifest):
    assert fig6_verified_reference_manifest["fixture_id"] == "griffiths_squibb_fig6_diurnal_2017_04_05_07"


@pytest.mark.parametrize("profile_name", ["1h", "6h"])
def test_fig6_hourly_and_six_hour_profiles_match_reference(fig6_reference_run, profile_name):
    _assert_temporal_profile_matches_reference(fig6_reference_run, profile_name)


def test_fig6_folded_reversal_matches_reviewed_day_night_anchors(fig6_reference_run):
    """Reviewed demo anchors, not exact medians digitized from paper contours."""
    recipe = fig6_reference_run.temporal_recipes["1h"]
    _, summary, _, _ = _compare_temporal_profile_values(recipe["prepared_profiles"]["folded"])
    assert recipe["utc_date_count"] == 3
    assert recipe["median_focus"]["median_db"] == 5
    assert summary["count"].sum() == 6459
    np.testing.assert_array_equal(summary["median"].iloc[1:5], [-2, -3, -2, -1])
    np.testing.assert_array_equal(summary["median"].iloc[5:7], [2, 3])
    assert summary["median"].iloc[7:21].between(5, 8).all()
    # The paper describes an approximate daytime average. This exact mean is
    # independently calculated from our frozen pairs for that stated interval.
    points = fig6_reference_run.paired_points
    utc_minutes = points["plot_time"].dt.hour * 60 + points["plot_time"].dt.minute
    daytime = points.loc[(utc_minutes >= 5 * 60) & (utc_minutes < 21 * 60 + 30), "metric"]
    assert len(daytime) == 5568
    assert daytime.mean() == pytest.approx(5.765086206896552, abs=1e-12, rel=0)


def test_fig6_partial_final_hour_preserves_selected_window(fig6_reference_run):
    recipe = fig6_reference_run.temporal_recipes["1h"]
    _, summary, edges, centers = _compare_temporal_profile_values(
        recipe["prepared_profiles"]["chronological"]["1h"]
    )
    assert len(summary) == 72
    assert pd.Timestamp(matplotlib_dates.num2date(edges[-2], tz="UTC")) == pd.Timestamp("2017-04-07T23:00Z")
    assert pd.Timestamp(matplotlib_dates.num2date(edges[-1], tz="UTC")) == pd.Timestamp("2017-04-07T23:45Z")
    assert pd.Timestamp(matplotlib_dates.num2date(centers[-1], tz="UTC")) == pd.Timestamp("2017-04-07T23:22:30Z")
    assert summary.iloc[-1][["count", "median", "q1", "q3"]].tolist() == [13, 0, -3, 2]


def test_fig6_wider_range_retains_hourly_medians(fig6_reference_run):
    wider_run = _prepare_reference_run(
        FIG6_REFERENCE_DIRECTORY, ("24h", "1h"), max_peer_distance_km=22000,
    )
    assert wider_run.context.max_peer_distance_km == 22000
    wider_pairs = _assert_paired_rows_match_reference(wider_run, "expected_paired_rows_22000km.parquet")
    assert len(wider_pairs) == 6474
    _assert_temporal_profile_matches_reference(wider_run, "utc_hour", "_22000km")
    regular_folded = fig6_reference_run.temporal_recipes["1h"]["prepared_profiles"]["folded"]
    wider_folded = wider_run.temporal_recipes["1h"]["prepared_profiles"]["folded"]
    np.testing.assert_array_equal(wider_folded["median"], regular_folded["median"])
    assert sum(wider_folded["count"]) - sum(regular_folded["count"]) == 15


@pytest.fixture(scope="module")
def fig6_paper_reference():
    """External expected features contain no WSPRadar-derived SNR values."""
    manifest = _verify_reference_manifest(FIG6_PAPER_DIRECTORY, {
        "paper_features.json", "paper_figure6.png", "comparison_policy.json",
        "independent_image_review.json", "paper_points.json", "README.md",
    })
    assert manifest["fixture_id"] == "griffiths_squibb_fig6_paper_density_features"
    annotations = _read_reference_json("paper_features.json", FIG6_PAPER_DIRECTORY)
    policy = _read_reference_json("comparison_policy.json", FIG6_PAPER_DIRECTORY)
    # Policy edits must not silently leave declared bandwidths untested or
    # introduce allowances that the fixed comparison does not implement.
    assert policy["smoothing"]["sigma_time_hours"] == [0.75, 1.0, 1.25]
    assert policy["smoothing"]["sigma_snr_db"] == [0.75, 1.0, 1.25]
    assert policy["branch_match"]["time_bin_half_width_allowance"] is True
    assert policy["branch_match"]["snr_bin_half_width_allowance"] is True
    assert policy["branch_match"]["unknown_author_smoother_extra_tolerance"] == 0
    return annotations, policy


def _paper_feature_bounds(feature, annotations, policy, *, include_allowances=True):
    axes = annotations["axes"]
    pixels = feature["pixel_box"]
    hours_per_pixel = 24 / (axes["x_one_day_px"] - axes["x_zero_day_px"])
    db_per_pixel = 40 / (axes["y_negative_15_db_px"] - axes["y_positive_25_db_px"])
    hour_lower = (pixels["x_min"] - axes["x_zero_day_px"]) * hours_per_pixel
    hour_upper = (pixels["x_max"] - axes["x_zero_day_px"]) * hours_per_pixel
    snr_lower = 25 - (pixels["y_max"] - axes["y_positive_25_db_px"]) * db_per_pixel
    snr_upper = 25 - (pixels["y_min"] - axes["y_positive_25_db_px"]) * db_per_pixel
    if include_allowances:
        pixel_bound = policy["branch_match"]["digitization_bound_px"]
        hour_allowance = pixel_bound * hours_per_pixel + 0.5
        snr_allowance = pixel_bound * db_per_pixel + 0.5
        hour_lower -= hour_allowance
        hour_upper += hour_allowance
        snr_lower -= snr_allowance
        snr_upper += snr_allowance
    return hour_lower, hour_upper, snr_lower, snr_upper


def _smooth_folded_density(counts, sigma_time_hours, sigma_snr_db):
    """Declared comparison estimator, not the paper's undocumented smoother.

    The caller establishes a 1-hour by 1-dB grid. Counts retain their pooled
    weighting. Time wraps at midnight; SNR uses zero padding without rescaling
    the tails. No application density, median or expected CSV defines a kernel.
    """
    def kernel(sigma):
        offsets = np.arange(-int(np.ceil(3 * sigma)), int(np.ceil(3 * sigma)) + 1)
        weights = np.exp(-0.5 * (offsets / sigma) ** 2)
        return offsets, weights / weights.sum()

    time_offsets, time_weights = kernel(sigma_time_hours)
    smoothed_time = sum(
        weight * np.roll(counts, int(offset), axis=1)
        for offset, weight in zip(time_offsets, time_weights)
    )
    snr_offsets, snr_weights = kernel(sigma_snr_db)
    padding = int(snr_offsets[-1])
    padded = np.pad(smoothed_time, ((padding, padding), (0, 0)))
    return sum(
        weight * padded[padding + offset:padding + offset + len(counts)]
        for offset, weight in zip(snr_offsets, snr_weights)
    )


def _vertical_density_modes(density, hours, snr_centers):
    """Enumerate modes across the full SNR axis before looking at paper boxes."""
    modes = []
    for hour_index, hour in enumerate(hours):
        column = density[:, hour_index]
        row = 1
        while row < len(column) - 1:
            last = row
            while last + 1 < len(column) and column[last + 1] == column[row]:
                last += 1
            if (
                last < len(column) - 1 and last - row <= 1
                and column[row] > column[row - 1]
                and column[last] > column[last + 1]
            ):
                modes.append({
                    "utc_hour": float(hour),
                    "delta_snr_db": float((snr_centers[row] + snr_centers[last]) / 2),
                    "density": float(column[row]),
                })
            row = last + 1
    return modes


def _mode_inside_feature(mode, bounds):
    hour_lower, hour_upper, snr_lower, snr_upper = bounds
    return (
        hour_lower <= mode["utc_hour"] <= hour_upper
        and snr_lower <= mode["delta_snr_db"] <= snr_upper
    )


def _compare_density_with_paper(reference_run, annotations, policy, sigma_time_hours, sigma_snr_db):
    profiles = reference_run.temporal_recipes["1h"]["prepared_profiles"]
    counts, _, hour_edges, hours = _compare_temporal_profile_values(profiles["folded"])
    snr_edges = np.asarray(profiles["y_edges"])
    np.testing.assert_array_equal(hour_edges, np.arange(25))
    np.testing.assert_array_equal(hours, np.arange(24) + 0.5)
    np.testing.assert_array_equal(np.diff(snr_edges), np.ones(len(snr_edges) - 1))
    snr_centers = (snr_edges[:-1] + snr_edges[1:]) / 2
    density = _smooth_folded_density(counts, sigma_time_hours, sigma_snr_db)
    modes = _vertical_density_modes(density, hours, snr_centers)
    comparisons = []
    for feature in annotations["features"]:
        bounds = _paper_feature_bounds(feature, annotations, policy)
        hour_start, hour_end = feature["paper_time_window_utc_hours"]
        candidates = [mode for mode in modes if hour_start <= mode["utc_hour"] < hour_end]
        matches = [mode for mode in candidates if _mode_inside_feature(mode, bounds)]
        comparisons.append({
            "feature_id": feature["id"], "bounds": bounds,
            "all_modes_in_time_window": candidates, "matching_modes": matches,
        })
    maximum_rows, maximum_columns = np.where(density == density.max())
    global_maxima = [
        {"utc_hour": float(hours[column]), "delta_snr_db": float(snr_centers[row])}
        for row, column in zip(maximum_rows, maximum_columns)
    ]
    return comparisons, global_maxima


@pytest.mark.parametrize("sigma_time_hours", [0.75, 1.0, 1.25])
@pytest.mark.parametrize("sigma_snr_db", [0.75, 1.0, 1.25])
def test_fig6_density_features_match_external_paper(
    fig6_reference_run, fig6_paper_reference, sigma_time_hours, sigma_snr_db,
):
    annotations, policy = fig6_paper_reference
    assert sigma_time_hours in policy["smoothing"]["sigma_time_hours"]
    assert sigma_snr_db in policy["smoothing"]["sigma_snr_db"]
    comparisons, global_maxima = _compare_density_with_paper(
        fig6_reference_run, annotations, policy, sigma_time_hours, sigma_snr_db,
    )
    for comparison in comparisons:
        assert comparison["matching_modes"], (
            f"Paper density feature absent at bandwidth {sigma_time_hours}h/{sigma_snr_db}dB: "
            f"{comparison}. Keep the external bounds fixed and investigate the mismatch."
        )
    strongest_feature = next(
        feature for feature in annotations["features"]
        if feature["id"] == policy["strongest_density_match"]["feature_id"]
    )
    strongest_bounds = _paper_feature_bounds(strongest_feature, annotations, policy)
    assert global_maxima and all(_mode_inside_feature(mode, strongest_bounds) for mode in global_maxima), (
        f"Strongest reconstructed density {global_maxima} lies outside paper region {strongest_bounds}"
    )


def test_fig6_density_time_ordering_matches_paper_text(fig6_reference_run, fig6_paper_reference):
    _, policy = fig6_paper_reference
    folded = fig6_reference_run.temporal_recipes["1h"]["prepared_profiles"]["folded"]
    counts, _, _, hours = _compare_temporal_profile_values(folded)
    totals = {}
    for period in ("morning", "midday", "evening"):
        start_hour, end_hour = policy["density_ordering"][f"{period}_utc_hours"]
        assert end_hour - start_hour == 3
        totals[period] = int(counts[:, (hours >= start_hour) & (hours < end_hour)].sum())
    assert totals["morning"] > totals["midday"], totals
    assert totals["evening"] > totals["midday"], totals


def test_fig6_displayed_paper_points_preserve_source_provenance(fig6_paper_reference):
    """Displayed witnesses may change without moving or deleting source evidence."""
    from PIL import Image

    source = _read_reference_json("paper_points.json", FIG6_PAPER_DIRECTORY)
    points = source["points"]
    by_id = {point["id"]: point for point in points}
    assert len(by_id) == len(points)
    assert {point_id: point["comparison_label"] for point_id, point in by_id.items()} == {
        "isolated_negative_1": "P1",
        "isolated_positive_1": "P2",
        "isolated_negative_2": None,
        "clipped_negative_1": None,
        "isolated_positive_2": "P4",
        "isolated_negative_3": "P3",
    }
    displayed = [point for point in points if point["comparison_label"] is not None]
    assert len({point["comparison_label"] for point in displayed}) == 4
    assert sum(point["delta_snr_db"] < 0 for point in displayed) == 2
    assert sum(point["delta_snr_db"] > 0 for point in displayed) == 2
    for point_id, coordinates in {
        "isolated_negative_1": (1.75675, -12.91631),
        "isolated_positive_1": (6.82108, 22.08480),
        "isolated_negative_2": (7.71238, -12.91631),
        "clipped_negative_1": (8.54958567, -14.87301587),
        "isolated_positive_2": (15.87018256, 24.07104660),
    }.items():
        point = by_id[point_id]
        assert (point["utc_hour"], point["delta_snr_db"]) == coordinates
    assert by_id["isolated_negative_3"]["source_component"]["clipped_at_plot_boundary"] is False
    tolerance = source["recommended_comparison_tolerance"]
    assert tolerance["utc_hour"] == 0.08
    assert tolerance["delta_snr_db"] == 0.21
    revision = source["display_revision"]
    image_path = FIG6_PAPER_DIRECTORY / revision["source_image"]
    assert hashlib.sha256(image_path.read_bytes()).hexdigest() == revision["source_image_sha256"]
    with Image.open(image_path) as raster:
        pixels = np.asarray(raster.convert("RGB"))
    calibration = source["axis_calibration"]
    for point in points:
        x, y = point["centroid_px"]
        hour = 24 * (x - calibration["left_x_px"]) / (
            calibration["right_x_px"] - calibration["left_x_px"]
        )
        snr = 25 - 40 * (y - calibration["top_y_px"]) / (
            calibration["bottom_y_px"] - calibration["top_y_px"]
        )
        assert point["utc_hour"] == pytest.approx(hour, abs=0.0001)
        assert point["delta_snr_db"] == pytest.approx(snr, abs=0.0001)
        if "source_component" not in point:
            continue
        component = point["source_component"]
        box = component["pixel_box"]
        crop = pixels[box["y_min"]:box["y_max"] + 1, box["x_min"]:box["x_max"] + 1]
        rows, columns = np.where((crop < 80).all(axis=2))
        assert len(rows) == component["dark_pixel_count"]
        np.testing.assert_allclose(
            [columns.mean() + box["x_min"], rows.mean() + box["y_min"]],
            point["centroid_px"], rtol=0, atol=0.000001,
        )
        if component["clipped_at_plot_boundary"]:
            axis_row = component["excluded_axis_start_y_px"]
            assert box["y_max"] + 1 == axis_row
            assert (pixels[axis_row, box["x_min"]:box["x_max"] + 1] < 80).all()


@pytest.mark.parametrize("point_id", [
    "isolated_negative_1", "isolated_positive_1", "isolated_negative_2",
    "clipped_negative_1", "isolated_positive_2", "isolated_negative_3",
])
def test_fig6_isolated_paper_points_have_matching_native_pairs(
    fig6_reference_run, fig6_paper_reference, point_id,
):
    """Folded point witnesses have no author-supplied date or station identity."""
    source = _read_reference_json("paper_points.json", FIG6_PAPER_DIRECTORY)
    assert {point["id"] for point in source["points"]} == {
        "isolated_negative_1", "isolated_positive_1", "isolated_negative_2",
        "clipped_negative_1", "isolated_positive_2", "isolated_negative_3",
    }
    point = next(point for point in source["points"] if point["id"] == point_id)
    tolerance = source["recommended_comparison_tolerance"]
    native_pairs = fig6_reference_run.paired_points
    utc_times = pd.to_datetime(native_pairs["plot_time"], utc=True)
    utc_hours = utc_times.dt.hour + utc_times.dt.minute / 60 + utc_times.dt.second / 3600
    hour_difference = ((utc_hours - point["utc_hour"] + 12) % 24 - 12).abs()
    snr_difference = (native_pairs["metric"] - point["delta_snr_db"]).abs()
    matching_pairs = native_pairs.loc[
        (hour_difference <= tolerance["utc_hour"])
        & (snr_difference <= tolerance["delta_snr_db"])
    ]
    assert not matching_pairs.empty, (
        f"No native pair matches independently digitized paper point {point} "
        f"within the fixed source-readout tolerance {tolerance}"
    )


def test_fig6_additional_report_combinations_explain_selected_paper_difference(fig6_reference_run):
    """Raw-report alternatives explain the missing tail without changing native pairs."""
    from scripts.internal.build_griffiths_fig6_comparison import additional_report_combinations

    reports = pd.read_parquet(FIG6_REFERENCE_DIRECTORY / "source_rows.parquet")
    pairs = _canonical_paired_rows(fig6_reference_run)
    additional = additional_report_combinations(reports, pairs, "G3ZIL", "G4HZX")
    assert len(additional) == 17
    assert int(additional["delta_snr_db"].between(-15, 25).sum()) == 8
    native_keys = set(zip(pairs["time_slot"], pairs["peer_sign"], pairs["peer_grid"]))
    assert set(zip(additional["time_slot"], additional["tx_sign"], additional["tx_loc"])) <= native_keys
    np.testing.assert_array_equal(
        additional["delta_snr_db"],
        additional["normalized_snr_target"] - additional["normalized_snr_reference"],
    )
    assert (
        additional["normalized_snr_target"].lt(additional["target_snr_db"])
        | additional["normalized_snr_reference"].lt(additional["reference_snr_db"])
    ).all()
    for minute, source_ids in ((26, (766002421, 766001569)), (30, (766005910, 766005260))):
        timestamp = pd.Timestamp(f"2017-04-07T18:{minute}:00Z")
        native = pairs.loc[
            pairs["evidence_utc"].eq(timestamp)
            & pairs["peer_sign"].eq("DK3RU") & pairs["peer_grid"].eq("JO31ws")
        ]
        assert native["delta_snr_db"].tolist() == [11.0]
        alternative = additional.loc[
            additional["evidence_utc"].eq(timestamp) & additional["delta_snr_db"].eq(-13)
        ]
        assert list(zip(alternative["id_target"], alternative["id_reference"])) == [source_ids]
    # Two weaker reports can yield the same Delta SNR as the retained strongest
    # pair. Provenance, not a difference in numeric coordinates, defines this overlay.
    coincident = additional.loc[
        additional["id_target"].eq(766002421) & additional["id_reference"].eq(766001526)
    ]
    assert coincident["delta_snr_db"].tolist() == [11.0]


def test_fig6_additional_report_combinations_preserve_cycle_identity_and_normalization():
    """One hand-calculated cycle excludes other full locators and neighboring cycles."""
    from scripts.internal.build_griffiths_fig6_comparison import additional_report_combinations

    timestamp = pd.Timestamp("2017-04-07T18:26:00Z")
    rows = [
        (1, 2, "G3ZIL", "JO31ws", 10, 40),
        (2, 22, "G3ZIL", "JO31ws", 5, 30),
        (3, 12, "G4HZX", "JO31ws", 2, 30),
        (4, 42, "G4HZX", "JO31ws", -5, 20),
        (5, 2, "G3ZIL", "JO31xx", -25, 30),
        (6, 12, "G4HZX", "JO31xx", -10, 30),
        (7, 122, "G3ZIL", "JO31ws", -22, 30),
        (8, 132, "G4HZX", "JO31ws", -8, 30),
    ]
    reports = pd.DataFrame([
        {
            "id": report_id, "time": timestamp + pd.Timedelta(seconds=offset),
            "rx_sign": receiver, "tx_sign": "DK3RU", "tx_loc": locator,
            "snr": snr, "power": power,
        }
        for report_id, offset, receiver, locator, snr, power in rows
    ])
    pairs = pd.DataFrame([{
        "time_slot": int(timestamp.timestamp() // 120), "evidence_utc": timestamp,
        "peer_sign": "DK3RU", "peer_grid": "JO31ws", "target_snr_db": 5.0,
        "reference_snr_db": 5.0, "delta_snr_db": 0.0,
    }])
    additional = additional_report_combinations(reports, pairs, "G3ZIL", "G4HZX")
    assert set(zip(additional["id_target"], additional["id_reference"])) == {(1, 3), (1, 4), (2, 3)}
    assert sorted(additional["delta_snr_db"].tolist()) == [-5.0, -2.0, 3.0]
    assert additional["evidence_utc"].eq(timestamp).all()
    np.testing.assert_allclose(additional["utc_hour"], 18 + 26 / 60)


@pytest.fixture(scope="module")
def fig3_paper_reference():
    """Read source-only witnesses; archive expectations never define them."""
    manifest = _verify_reference_manifest(FIG3_PAPER_DIRECTORY, {
        "paper_features.json", "paper_figure3.png", "comparison_policy.json",
        "independent_image_review.json", "paper_daily_means.json", "paper_figure4.png",
        "frozen_inputs.json", "known_discrepancies.json", "README.md",
    })
    assert manifest["fixture_id"] == "griffiths_squibb_fig3_paper_temporal_features"
    frozen = _read_reference_json("frozen_inputs.json", FIG3_PAPER_DIRECTORY)
    for filename, expected_hash in frozen["sha256"].items():
        assert hashlib.sha256((FIG3_PAPER_DIRECTORY / filename).read_bytes()).hexdigest() == expected_hash
    annotations = _read_reference_json("paper_features.json", FIG3_PAPER_DIRECTORY)
    policy = _read_reference_json("comparison_policy.json", FIG3_PAPER_DIRECTORY)
    assert policy["histogram_time_bins"] == ["3h", "24h"]
    assert policy["feature_interpretation"] == "occupied_region_witness"
    assert policy["extra_population_tolerance_db"] == 0
    assert policy["native_pixel_allowance"] == "sum_source_manual_and_axis_bounds"
    assert policy["negative_tail_strict_upper_db"] == -15
    assert [feature["id"] for feature in annotations["features"]] == list(FIG3_PAPER_FEATURE_IDS)
    assert policy["figure4_mean_anchors"] == list(FIG3_PAPER_MEAN_IDS)
    means = _read_reference_json("paper_daily_means.json", FIG3_PAPER_DIRECTORY)
    anchors = means["unambiguous_dated_daily_average_candidates"] + [
        means["date_independent_first_half_extrema"]["minimum"],
        means["date_independent_first_half_extrema"]["maximum"],
    ]
    assert [anchor["id"] for anchor in anchors] == list(FIG3_PAPER_MEAN_IDS)
    return annotations, policy


def _fig3_paper_region_bounds(feature, annotations, policy):
    """Convert a source rectangle to UTC Matplotlib days and linear dB."""
    axes = annotations["axes"]
    pixels = feature["pixel_box"]
    days_per_pixel = 30 / (axes["x_may1_px"] - axes["x_april1_px"])
    db_per_pixel = 50 / (axes["y_negative20_db_px"] - axes["y_positive30_db_px"])
    april_start = matplotlib_dates.date2num(pd.Timestamp("2017-04-01T00:00Z"))
    manual = feature["manual_box_edge_uncertainty_px"]
    axis = axes["axis_readout_uncertainty_px"]
    x_allowance = manual["x"] + axis["x"]
    y_allowance = manual["y"] + axis["y"]
    return (
        april_start + (pixels["x_min"] - x_allowance - axes["x_april1_px"]) * days_per_pixel,
        april_start + (pixels["x_max"] + x_allowance - axes["x_april1_px"]) * days_per_pixel,
        30 - (pixels["y_max"] + y_allowance - axes["y_positive30_db_px"]) * db_per_pixel,
        30 - (pixels["y_min"] - y_allowance - axes["y_positive30_db_px"]) * db_per_pixel,
    )


def _fig3_region_evidence(reference_run, annotations, policy, feature_id, time_bin):
    """Return native and plotted support without treating ink as probability."""
    feature = next(feature for feature in annotations["features"] if feature["id"] == feature_id)
    time_lower, time_upper, snr_lower, snr_upper = _fig3_paper_region_bounds(feature, annotations, policy)
    pairs = reference_run.paired_points
    times = matplotlib_dates.date2num(pd.to_datetime(pairs["plot_time"], utc=True))
    native_mask = (
        (times >= time_lower) & (times <= time_upper)
        & pairs["metric"].between(snr_lower, snr_upper)
    )
    if feature["kind"] == "negative_tail":
        native_mask &= pairs["metric"] < policy["negative_tail_strict_upper_db"]
        snr_upper = min(snr_upper, policy["negative_tail_strict_upper_db"])
    native_count = int(native_mask.sum())
    profiles = reference_run.temporal_recipes[time_bin]["prepared_profiles"]
    counts, _, time_edges, _ = _compare_temporal_profile_values(profiles["chronological"][time_bin])
    snr_edges = np.asarray(profiles["y_edges"])
    # Intersect whole cells with the source region. The native-point check
    # above prevents a neighbouring point in a coarse cell from sufficing.
    time_cells = (time_edges[:-1] <= time_upper) & (time_edges[1:] >= time_lower)
    snr_cells = (snr_edges[:-1] <= snr_upper) & (snr_edges[1:] >= snr_lower)
    histogram_count = int(counts[np.ix_(snr_cells, time_cells)].sum())
    represented_native_count = 0
    if native_count:
        time_indices = np.searchsorted(time_edges, times[native_mask], side="right") - 1
        snr_indices = np.searchsorted(snr_edges, pairs.loc[native_mask, "metric"], side="right") - 1
        assert ((time_indices >= 0) & (time_indices < counts.shape[1])).all()
        assert ((snr_indices >= 0) & (snr_indices < counts.shape[0])).all()
        witness_cells, witness_counts = np.unique(
            np.column_stack((snr_indices, time_indices)), axis=0, return_counts=True,
        )
        for (snr_index, time_index), witness_count in zip(witness_cells, witness_counts):
            if counts[snr_index, time_index] >= witness_count:
                represented_native_count += int(witness_count)
    return {
        "native_count": native_count, "histogram_count": histogram_count,
        "represented_native_count": represented_native_count,
    }


class ExternalPaperMismatch(AssertionError):
    """A source comparison differs; setup, integrity and logic errors stay fatal."""


@pytest.mark.parametrize("time_bin", ["3h", "24h"])
@pytest.mark.parametrize("feature_id", [
    *FIG3_PAPER_FEATURE_IDS[:-1],
    pytest.param(FIG3_PAPER_FEATURE_IDS[-1], marks=pytest.mark.xfail(
        strict=True, raises=ExternalPaperMismatch,
        reason="FIG3-TAIL: paper plume is compatible with duplicate-expanded pairs, not strongest-report pairing; see known_discrepancies.json",
    )),
])
def test_fig3_paper_regions_have_native_and_temporal_support(
    fig3_reference_run, fig3_paper_reference, feature_id, time_bin,
):
    """These are occupied-region witnesses, not recovered density maxima."""
    annotations, policy = fig3_paper_reference
    evidence = _fig3_region_evidence(fig3_reference_run, annotations, policy, feature_id, time_bin)
    if evidence["native_count"] == 0:
        raise ExternalPaperMismatch((feature_id, time_bin, evidence))
    assert evidence["histogram_count"] > 0, (feature_id, time_bin, evidence)
    assert evidence["represented_native_count"] == evidence["native_count"], (feature_id, time_bin, evidence)


def _fig3_daily_means(reference_run):
    """Recover pooled arithmetic means from the actual daily count grid.

    Integer dB native differences coincide with the one-dB cell centres in
    this case. Use all cells, including values beyond the paper's plot limits.
    This does not assert that the production chart displays arithmetic means.
    """
    profiles = reference_run.temporal_recipes["24h"]["prepared_profiles"]
    counts, _, time_edges, _ = _compare_temporal_profile_values(profiles["chronological"]["24h"])
    snr_edges = np.asarray(profiles["y_edges"])
    snr_centers = (snr_edges[:-1] + snr_edges[1:]) / 2
    np.testing.assert_array_equal(np.diff(snr_edges), np.ones(len(snr_centers)))
    np.testing.assert_array_equal(snr_centers, np.round(snr_centers))
    assert reference_run.paired_points["metric"].isin(snr_centers).all()
    dates = pd.DatetimeIndex(matplotlib_dates.num2date(time_edges[:-1], tz="UTC"))
    np.testing.assert_array_equal(np.diff(time_edges), np.ones(len(dates)))
    assert (counts.sum(axis=0) > 0).all()
    return pd.Series((snr_centers @ counts) / counts.sum(axis=0), index=dates)


def test_fig3_first_half_daily_mean_rises_as_described_in_paper(fig3_reference_run, fig3_paper_reference):
    """The prose anchors a trend, not monotonicity of every consecutive day."""
    _, policy = fig3_paper_reference
    means = _fig3_daily_means(fig3_reference_run)
    trend = policy["daily_mean_trend"]

    def window(bounds):
        return means.loc[(means.index >= pd.Timestamp(bounds[0])) & (means.index < pd.Timestamp(bounds[1]))]

    first_half = window(trend["whole_window_utc"])
    early = window(trend["early_window_utc"])
    late = window(trend["late_window_utc"])
    assert len(first_half) == 15 and len(early) == len(late) == 3
    slope = float(np.polyfit(np.arange(len(first_half)), first_half.to_numpy(), 1)[0])
    assert slope > 0, f"Paper describes a first-half rise; daily-mean slope is {slope} dB/day"
    assert late.mean() > early.mean(), {"early_mean_db": early.mean(), "late_mean_db": late.mean()}


@pytest.mark.parametrize("anchor_id", [
    FIG3_PAPER_MEAN_IDS[0],
    pytest.param(FIG3_PAPER_MEAN_IDS[1], marks=pytest.mark.xfail(
        strict=True, raises=ExternalPaperMismatch,
        reason="FIG3-MEAN-APR13: paper mean matches duplicate-expanded pairing, not strongest-report pairing; see known_discrepancies.json",
    )),
    *FIG3_PAPER_MEAN_IDS[2:],
])
def test_fig3_daily_means_match_external_figure4(fig3_reference_run, fig3_paper_reference, anchor_id):
    """Figure 4 supplies means; Figure 3 moisture only identifies some dates."""
    source = _read_reference_json("paper_daily_means.json", FIG3_PAPER_DIRECTORY)
    means = _fig3_daily_means(fig3_reference_run)
    _assert_fig4_mean_anchor(means, source, anchor_id)


def _assert_fig4_mean_anchor(means, source, anchor_id):
    """Compare daily arithmetic means with unchanged external marker bounds."""
    dated = source["unambiguous_dated_daily_average_candidates"]
    extrema = source["date_independent_first_half_extrema"]
    anchor = next(anchor for anchor in dated + [extrema["minimum"], extrema["maximum"]] if anchor["id"] == anchor_id)
    if "uniquely_matched_date" in anchor:
        moisture_lower, moisture_upper = anchor["moisture_interval_percent"]
        matched_dates = [
            point["date"] for point in source["figure3_first_half_moisture_points"]
            if point["moisture_interval_percent"][0] <= moisture_upper
            and point["moisture_interval_percent"][1] >= moisture_lower
        ]
        assert matched_dates == anchor["compatible_fig3_dates_by_interval_overlap"] == [anchor["uniquely_matched_date"]]
        actual_mean = means.loc[pd.Timestamp(anchor["uniquely_matched_date"], tz="UTC")]
    else:
        first_half = means.loc[(means.index >= pd.Timestamp("2017-04-01T00:00Z")) & (means.index < pd.Timestamp("2017-04-16T00:00Z"))]
        assert len(first_half) == 15
        actual_mean = first_half.min() if anchor_id == extrema["minimum"]["id"] else first_half.max()
    lower, upper = anchor["daily_average_snr_interval_db"]
    if not lower <= actual_mean <= upper:
        raise ExternalPaperMismatch(
            f"{anchor_id}: current mean {actual_mean:.9f} dB is outside paper readout "
            f"[{lower:.9f}, {upper:.9f}] dB. These bounds cover raster readout only; "
            "investigate population, daily boundaries and weighting without widening the reference."
        )


@pytest.fixture(scope="module")
def fig3_raw_pairing_variants(verified_reference_manifest):
    """Independently calculate two evidence units from frozen endpoint reports.

    The many-to-many join is an exploratory explanation of publication
    differences, not a claim to know the authors' original SQL. The maximum
    variant tests the current production duplicate policy separately.
    """
    reports = pd.read_parquet(REFERENCE_DIRECTORY / "source_rows.parquet")
    keys = ["time", "tx_sign", "tx_loc"]
    target = reports.loc[reports["rx_sign"] == "G3ZIL"]
    reference = reports.loc[reports["rx_sign"] == "G4HZX"]
    expanded = target.merge(reference, on=keys, suffixes=("_target", "_reference"))
    assert (expanded["power_target"] == expanded["power_reference"]).all()
    expanded["metric"] = expanded["snr_target"].astype(int) - expanded["snr_reference"].astype(int)
    reports["normalized_snr"] = reports["snr"].astype(int) - reports["power"].astype(int) + 30
    maxima = reports.groupby(keys + ["rx_sign"], observed=True)["normalized_snr"].max().unstack("rx_sign")
    maxima = maxima.dropna(subset=["G3ZIL", "G4HZX"])
    maximum_pairs = (maxima["G3ZIL"] - maxima["G4HZX"]).rename("metric").reset_index()
    names = {"time": "plot_time", "tx_sign": "station", "tx_loc": "grid"}
    return (
        expanded[keys + ["metric"]].rename(columns=names),
        maximum_pairs.rename(columns=names),
    )


@pytest.mark.parametrize("anchor_id", FIG3_PAPER_MEAN_IDS)
def test_fig4_means_are_reproduced_by_duplicate_expanded_source_pairs(
    fig3_raw_pairing_variants, fig3_paper_reference, anchor_id,
):
    """All five frozen paper anchors agree under the alternate evidence unit."""
    expanded, _ = fig3_raw_pairing_variants
    means = expanded.groupby(expanded["plot_time"].dt.floor("D"))["metric"].mean()
    source = _read_reference_json("paper_daily_means.json", FIG3_PAPER_DIRECTORY)
    _assert_fig4_mean_anchor(means, source, anchor_id)


def test_fig3_paper_tail_is_present_in_duplicate_expanded_source_pairs(
    fig3_raw_pairing_variants, fig3_paper_reference,
):
    """Explain the paper witness without changing production duplicate policy."""
    expanded, _ = fig3_raw_pairing_variants
    annotations, policy = fig3_paper_reference
    feature = next(feature for feature in annotations["features"] if feature["kind"] == "negative_tail")
    lower_time, upper_time, lower_snr, upper_snr = _fig3_paper_region_bounds(feature, annotations, policy)
    times = matplotlib_dates.date2num(expanded["plot_time"])
    witnesses = expanded.loc[
        (times >= lower_time) & (times <= upper_time)
        & expanded["metric"].between(lower_snr, upper_snr)
        & (expanded["metric"] < policy["negative_tail_strict_upper_db"])
    ]
    assert not witnesses.empty


def test_fig3_production_pairs_follow_independently_recomputed_maximum_report_policy(
    fig3_reference_run, fig3_raw_pairing_variants,
):
    """Check every retained pair against raw maxima, independently of baseline.

    Production determines geographic/eligibility selection; this assertion
    independently checks the SNR computation for that retained population.
    Existing exact archive tests separately guard identities and counts.
    """
    _, independent_pairs = fig3_raw_pairing_variants
    keys = ["plot_time", "station", "grid"]
    comparison = fig3_reference_run.paired_points[keys + ["metric"]].merge(
        independent_pairs, on=keys, how="left", validate="one_to_one",
        suffixes=("_production", "_independent"), indicator=True,
    )
    assert comparison["_merge"].eq("both").all()
    np.testing.assert_array_equal(comparison["metric_production"], comparison["metric_independent"])
