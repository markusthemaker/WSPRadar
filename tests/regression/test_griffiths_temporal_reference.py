"""Mandatory offline reference for the Griffiths April 2017 temporal evidence.

Frozen SQL-result rows enter the real post-fetch, map, Inspector and temporal
recipe calculations. Reviewed expectations are read only after calculation;
neither database SQL execution nor figure rendering is claimed by these tests.
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

from config import BAND_MAP
from core.analysis_context import AnalysisContext
from core.analysis_plan import AnalysisPlan, DECODE_FILTER_LEGACY
from core.analysis_runner import apply_post_fetch_filters, build_analysis_batches
from core.map_data import build_map_data_result
from core.math_utils import locator_to_latlon
from core.presentation_context import PresentationContext
from i18n import T
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.config_io import apply_config_state_values, validate_config_document
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


def _reject_network_access(*args, **kwargs):
    pytest.fail("The frozen temporal reference must not access the network")


def _build_temporal_recipe(paired_points, configuration, time_bin, time_bin_options=("24h", "3h")):
    """Use the actual export recipe without invoking its figure renderer."""
    return _segment_temporal_evidence_export_recipe(
        paired_points[["plot_time", "metric"]],
        "Griffiths April 2017 temporal reference", time_bin, "Joint spots",
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


def _prepare_reference_run(reference_directory, time_bins, *, max_peer_distance_km=None):
    """Calculate once from input rows; expected outputs never enter this path."""
    with pytest.MonkeyPatch.context() as network_guard:
        network_guard.setattr(requests.sessions.Session, "request", _reject_network_access)
        network_guard.setattr(socket, "create_connection", _reject_network_access)
        network_guard.setattr(socket.socket, "connect", _reject_network_access)
        network_guard.setattr(socket.socket, "connect_ex", _reject_network_access)
        configuration = validate_config_document(_read_reference_json("demo.config", reference_directory))
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
        # This fixture starts at the captured legacy SQL-result boundary. It
        # does not pretend to exercise HTTP retries or database aggregation.
        analysis = analyses[0].for_legacy_query()
        input_rows = pd.read_parquet(reference_directory / "input_sql_rows.parquet")
        input_row_count = len(input_rows)
        processed_rows, warning_message = apply_post_fetch_filters(
            input_rows, analysis, context, center_latitude, center_longitude, T["en"],
        )
        assert warning_message is None
        map_preparation = build_map_data_result(
            processed_rows, analysis_id=analysis.id, is_compare=analysis.is_compare,
            is_sequential=analysis.is_sequential, analysis_kind=analysis.analysis_kind,
            center_latitude=center_latitude, center_longitude=center_longitude,
            min_spots=context.min_joint_spots_per_station,
            min_opportunities=context.min_confirmed_opportunities_per_peer,
            base_min_stations=context.min_joint_stations_per_map_segment,
            tx_ab_repeat_interval_minutes=context.tx_ab_repeat_interval_minutes,
            tx_ab_target_start_minute=context.tx_ab_target_start_minute,
            tx_ab_reference_start_minute=context.tx_ab_reference_start_minute,
        )
        assert map_preparation.diagnostic is None
        assert map_preparation.map_data is not None
        station_rows = map_preparation.map_data.station_rows
        inspector_model = build_compare_inspector_view_model(
            station_rows, analysis_id=analysis.id, is_sequential=analysis.is_sequential,
            analysis_context=context, presentation_context=presentation_context,
        )
        comparison_units = _build_compare_unit_rows(
            processed_rows, station_rows, analysis.is_sequential,
            paired_identity_df=inspector_model.build_evidence_identities(),
        )
        comparison_units = _retain_thresholded_compare_outcomes(comparison_units, station_rows)
        paired_points = _compare_joint_evidence_points(
            comparison_units, require_paired_eligible=True,
        )
        temporal_recipes = {
            time_bin: _build_temporal_recipe(paired_points, configuration, time_bin, time_bins)
            for time_bin in time_bins
        }
    return TemporalReferenceRun(
        configuration, context, analysis, input_row_count, processed_rows,
        station_rows, comparison_units, paired_points, temporal_recipes, reference_directory,
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
    assert reference_run.context.to_dict() == _read_reference_json("analysis_context.json", reference_run.reference_directory)
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


def _assert_paired_rows_match_reference(reference_run, filename="expected_paired_rows.parquet"):
    expected = pd.read_parquet(reference_run.reference_directory / filename)
    identity_keys = ["evidence_utc", "peer_sign", "peer_grid"]
    actual = reference_run.paired_points.rename(columns={
        "plot_time": "evidence_utc", "station": "peer_sign", "grid": "peer_grid",
        "metric": "delta_snr_db",
    })[identity_keys + ["delta_snr_db"]].merge(
        reference_run.comparison_units[identity_keys + ["target_snr_db", "reference_snr_db"]],
        on=identity_keys, how="left", validate="one_to_one",
    )
    actual["time_slot"] = actual["evidence_utc"].dt.as_unit("ns").astype("int64") // 120_000_000_000
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


@pytest.mark.parametrize("point_id", ["isolated_negative_1", "isolated_positive_1", "isolated_negative_2"])
def test_fig6_isolated_paper_points_have_matching_native_pairs(
    fig6_reference_run, fig6_paper_reference, point_id,
):
    """Folded point witnesses have no author-supplied date or station identity."""
    source = _read_reference_json("paper_points.json", FIG6_PAPER_DIRECTORY)
    assert {point["id"] for point in source["points"]} == {
        "isolated_negative_1", "isolated_positive_1", "isolated_negative_2",
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
