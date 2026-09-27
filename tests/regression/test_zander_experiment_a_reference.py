"""External Figure 4 evidence and independent raw-report TX A/B regression.

The generated SQL is executed over frozen rows in SQLite with a deliberately
small ClickHouse-function adapter. This exercises the actual SELECT, predicates,
UNION, grouping and aggregation, but does not validate the ClickHouse engine.
The resulting rows enter the real post-fetch, map, Inspector and histogram path.
"""

import hashlib
import json
from pathlib import Path
import socket
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import requests

from reference_sql import execute_generated_sql as _execute_generated_sql

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
from ui.matplotlib_renderer import dispose_matplotlib_figure
from ui.plots.evidence_figures import (
    _segment_figure_export_recipe, _vertical_metric_histogram_recipe,
    render_segment_insight_export_figure,
)


REFERENCE_DIRECTORY = Path(__file__).parent / "reference_fixtures" / "zander_experiment_a_v1"
PAPER_DIRECTORY = REFERENCE_DIRECTORY.parent / "zander_fig4_paper_v1"
KEY_COLUMNS = ["time_slot", "peer_sign", "peer_grid"]
SQL_SCIENTIFIC_COLUMNS = KEY_COLUMNS + [
    "peer_lat", "peer_lon", "snr_u_norm", "snr_r_norm", "has_u", "has_r",
]


def _read_json(directory, name):
    return json.loads((directory / name).read_text(encoding="utf-8"))


def _verify_manifest(directory, required_files):
    manifest = _read_json(directory, "manifest.json")
    assert manifest["schema_version"] == 1
    paths = [record["path"] for record in manifest["files"]]
    assert len(paths) == len(set(paths))
    assert required_files.issubset(paths)
    for record in manifest["files"]:
        path = (directory / record["path"]).resolve()
        assert path.is_relative_to(directory.resolve())
        contents = path.read_bytes()
        assert len(contents) == record["bytes"], record["path"]
        assert hashlib.sha256(contents).hexdigest() == record["sha256"], record["path"]


def _reject_network(*args, **kwargs):
    pytest.fail("The Zander reference is mandatory and entirely offline")


@pytest.fixture(scope="module", autouse=True)
def verified_reference_files():
    _verify_manifest(REFERENCE_DIRECTORY, {
        "README.md", "demo.config", "analysis_context.json", "source_rows.csv",
        "source_rows.parquet", "source_rows_query.sql", "capture_provenance.json",
        "captured_query_strict.sql", "captured_sql_output.csv",
        "expected_sql_rows.csv", "expected_retained_rows.csv",
        "expected_paired_rows.csv", "expected_station_rows.csv",
        "expected_histogram_1db.csv", "expected_summary.json",
    })
    _verify_manifest(PAPER_DIRECTORY, {
        "README.md", "paper_features.json", "paper_figure4.png",
        "extraction_provenance.md", "comparison_policy.json", "frozen_inputs.json",
    })
    with pytest.MonkeyPatch.context() as guard:
        guard.setattr(requests.sessions.Session, "request", _reject_network)
        guard.setattr(socket, "create_connection", _reject_network)
        guard.setattr(socket.socket, "connect", _reject_network)
        guard.setattr(socket.socket, "connect_ex", _reject_network)
        yield


def _assert_scientific_rows(actual, expected):
    columns = list(expected.columns)
    pd.testing.assert_frame_equal(
        actual[columns].sort_values(KEY_COLUMNS).reset_index(drop=True),
        expected.sort_values(KEY_COLUMNS).reset_index(drop=True),
        check_dtype=False, check_exact=False, rtol=0, atol=1e-12,
    )


def _calculate_run(source_rows, configuration_document=None):
    """Replay actual production processing without reading expected results.

    The review-figure builder uses this same bounded offline entry point so
    scientific changes affect its plotted values before the oracle checks run.
    """
    if configuration_document is None:
        configuration_document = _read_json(REFERENCE_DIRECTORY, "demo.config")
    configuration = validate_config_document(configuration_document)
    session_values = {"lang": "en"}
    apply_config_state_values(configuration, session_values)
    session_values["run_mode"] = configuration["analysis_direction"].upper()
    context = build_analysis_context_from_session_state(session_values)
    latitude, longitude = locator_to_latlon(context.qth)
    presentation = PresentationContext(solar_label="All", labels=T["en"])
    analyses = build_analysis_batches(
        context, configuration["start_utc"], configuration["end_utc"], latitude, longitude,
        f"AND band = '{BAND_MAP[context.band]}'", presentation_context=presentation,
    )
    assert len(analyses) == 1
    analysis = analyses[0]
    sql_rows = _execute_generated_sql(analysis.query, source_rows)
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
        title="Zander Experiment A", selected_segment="Full Range | All Directions",
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
    return SimpleNamespace(
        configuration=configuration, context=context, analysis=analysis,
        source_rows=source_rows, sql_rows=sql_rows, processed=processed,
        stations=stations, units=units, points=points, recipe=recipe,
    )


@pytest.fixture(scope="module")
def reference_run(verified_reference_files):
    source_rows = pd.read_csv(REFERENCE_DIRECTORY / "source_rows.csv", float_precision="round_trip")
    return _calculate_run(source_rows)


def test_demo_configuration_and_independent_sql_aggregation(reference_run):
    assert reference_run.context.to_dict() == _read_json(REFERENCE_DIRECTORY, "analysis_context.json")
    assert reference_run.analysis.decode_filter_mode == "strict_code_1"
    assert not reference_run.analysis.is_sequential
    _assert_scientific_rows(reference_run.sql_rows, pd.read_csv(REFERENCE_DIRECTORY / "expected_sql_rows.csv"))
    captured = pd.read_csv(REFERENCE_DIRECTORY / "captured_sql_output.csv")
    # ClickHouse CSV rounds Float32 coordinates for display. Recover the source
    # precision before checking the scientific projection against actual SQL.
    for column in ("peer_lat", "peer_lon"):
        captured[column] = captured[column].astype("float32").astype("float64")
    _assert_scientific_rows(reference_run.sql_rows, captured[SQL_SCIENTIFIC_COLUMNS])


def test_raw_csv_preserves_the_original_provider_reports(reference_run):
    original = pd.read_parquet(REFERENCE_DIRECTORY / "source_rows.parquet")
    csv_rows = reference_run.source_rows.copy()
    csv_rows["time"] = pd.to_datetime(csv_rows["time"], utc=True)
    pd.testing.assert_frame_equal(csv_rows, original, check_dtype=False, check_exact=True)
    summary = _read_json(REFERENCE_DIRECTORY, "expected_summary.json")
    assert len(original) == summary["source_rows"]
    assert original.code.astype(str).value_counts().to_dict() == summary["source_code_counts"]


def test_independent_selection_and_all_paired_snr_components(reference_run):
    expected = pd.read_csv(REFERENCE_DIRECTORY / "expected_paired_rows.csv")
    _assert_scientific_rows(reference_run.processed, pd.read_csv(REFERENCE_DIRECTORY / "expected_retained_rows.csv"))
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
    summary = _read_json(REFERENCE_DIRECTORY, "expected_summary.json")
    assert len(reference_run.sql_rows) == summary["sql_group_count"]
    assert len(reference_run.processed) == summary["retained_group_count"]
    assert len(reference_run.stations) == summary["retained_peer_identities"]
    assert reference_run.units.outcome.value_counts().to_dict() == summary["outcomes"]
    assert len(actual) == summary["joint_spots"]


def test_joint_histogram_and_station_medians_keep_distinct_weighting(reference_run):
    expected = pd.read_csv(REFERENCE_DIRECTORY / "expected_histogram_1db.csv")
    histogram = reference_run.recipe["spot_histogram"]
    nonempty = np.asarray(histogram["counts"]) > 0
    expected_nonempty = expected.loc[expected.joint_spots > 0]
    np.testing.assert_array_equal(np.asarray(histogram["centers"])[nonempty], expected_nonempty.delta_snr_db)
    np.testing.assert_array_equal(np.asarray(histogram["counts"])[nonempty], expected_nonempty.joint_spots)
    assert histogram["bin_width"] == 1
    summary = _read_json(REFERENCE_DIRECTORY, "expected_summary.json")
    assert histogram["value_count"] == summary["joint_spots"]
    assert histogram["mean"] == pytest.approx(summary["mean_delta_snr_db"], abs=1e-12)
    assert histogram["median"] == summary["median_delta_snr_db"]
    assert reference_run.points.metric.std(ddof=1) == pytest.approx(summary["sample_std_delta_snr_db"], abs=1e-12)
    station_histogram = reference_run.recipe["station_histogram"]
    assert station_histogram["value_count"] == summary["paired_peer_identities"]
    assert station_histogram["mean"] == pytest.approx(summary["station_median_mean_db"], abs=1e-12)
    assert not np.isclose(station_histogram["mean"], histogram["mean"])
    expected_stations = pd.read_csv(REFERENCE_DIRECTORY / "expected_station_rows.csv")
    actual_stations = reference_run.stations.loc[reference_run.stations.spot_count > 0].rename(columns={
        "spot_count": "joint_spots", "stat_val": "median_delta_snr_db",
    })
    station_columns = ["peer_sign", "peer_grid", "joint_spots", "median_delta_snr_db"]
    pd.testing.assert_frame_equal(
        actual_stations[station_columns].sort_values(station_columns[:2]).reset_index(drop=True),
        expected_stations[station_columns].sort_values(station_columns[:2]).reset_index(drop=True),
        check_dtype=False, check_exact=True,
    )


def test_rendered_right_hand_histogram_uses_joint_sample_percentages(reference_run):
    figure = render_segment_insight_export_figure(reference_run.recipe)
    assert figure is not None
    try:
        histogram = reference_run.recipe["spot_histogram"]
        rectangles = [patch for axis in figure.axes for patch in axis.patches if patch.get_gid() == "spot-metric-histogram"]
        assert len(rectangles) == len(histogram["counts"])
        np.testing.assert_allclose(
            [patch.get_height() for patch in rectangles],
            100 * np.asarray(histogram["counts"]) / histogram["value_count"], rtol=0, atol=1e-12,
        )
        np.testing.assert_allclose(
            [patch.get_x() + patch.get_width() / 2 for patch in rectangles],
            histogram["centers"], rtol=0, atol=1e-12,
        )
        assert len({id(patch.axes) for patch in rectangles}) == 1
        spot_axis = rectangles[0].axes
        station_axes = {patch.axes for axis in figure.axes for patch in axis.patches if patch.get_gid() == "station-median-histogram"}
        assert len(station_axes) == 1
        assert spot_axis.get_position().x0 > next(iter(station_axes)).get_position().x0
    finally:
        dispose_matplotlib_figure(figure)


def _paper_projection(histogram):
    """Rebin actual 1 dB counts; never fit bins or renormalize a clipped subset."""
    policy = _read_json(PAPER_DIRECTORY, "comparison_policy.json")
    edges = np.asarray(policy["nominal_edges_db"], dtype=float)
    centers = np.asarray(histogram["centers"], dtype=float)
    counts = np.asarray(histogram["counts"], dtype=int)
    assert histogram["bin_width"] == 1
    assert counts.sum() == histogram["value_count"]
    rebinned = np.histogram(centers, bins=edges, weights=counts)[0]
    assert rebinned.sum() == counts.sum(), "Evidence falls outside the paper's visible bar span"
    density = rebinned / (counts.sum() * np.diff(edges))
    return edges, rebinned, density


@pytest.mark.parametrize("statistic", ["mean_db", "sigma_db"])
def test_paper_rounded_mean_and_spread(reference_run, statistic):
    paper = _read_json(PAPER_DIRECTORY, "paper_features.json")
    interval = paper["reported_statistics"]["conditional_nearest_rounding_intervals"][statistic]
    observed = reference_run.recipe["spot_histogram"]["mean"] if statistic == "mean_db" else reference_run.points.metric.std(ddof=1)
    assert interval[0] <= observed <= interval[1], (statistic, observed, interval)


@pytest.mark.parametrize("region_index", range(9), ids=lambda value: f"visible-region-{value + 1}")
def test_paper_digitized_histogram_density(reference_run, region_index):
    paper = _read_json(PAPER_DIRECTORY, "paper_features.json")
    digitization = paper["digitization"]
    _, _, density = _paper_projection(reference_run.recipe["spot_histogram"])
    source_height = digitization["bins"][region_index]["density_per_db"]
    assert density[region_index] == pytest.approx(
        source_height, abs=digitization["density_absolute_readout_tolerance_per_db"], rel=0,
    )


def test_publication_setup_and_archive_selectors_are_distinguished(reference_run):
    setup = _read_json(PAPER_DIRECTORY, "paper_features.json")["experiment_a_setup"]
    assert int(BAND_MAP[reference_run.context.band]) == setup["band_frequency_mhz"]
    assert reference_run.context.qth == setup["transmitter_locator_prefix"]
    # Equal reported power makes normalized Target-minus-Reference equal to
    # the raw-SNR difference here. It does not establish power calibration.
    assert set(reference_run.source_rows.power) == {23}
    assert reference_run.context.reference_snr_correction_db == 0
    assert reference_run.configuration["end_utc"] - reference_run.configuration["start_utc"] == pd.Timedelta(hours=1)
    installed = json.loads((Path(__file__).parents[2] / "config/demos/03_zander_tx_buddy_experiment_a.config").read_text(encoding="utf-8"))
    frozen = _read_json(REFERENCE_DIRECTORY, "demo.config")
    installed_settings = installed["settings"]
    frozen_settings = frozen["settings"]
    for section in ("comparison_parameters", "advanced_parameters", "results_view"):
        assert installed_settings[section] == frozen_settings[section]
    installed_core = installed_settings["core_parameters"]
    frozen_core = frozen_settings["core_parameters"]
    assert {key: value for key, value in installed_core.items() if key != "time_selection"} == {
        key: value for key, value in frozen_core.items() if key != "time_selection"
    }
    assert installed_core["time_selection"] == {
        "start_utc": "2022-05-21T09:45Z", "end_utc": "2022-05-21T10:30Z",
    }
    assert frozen_core["time_selection"] == {
        "start_utc": "2022-05-21T09:30Z", "end_utc": "2022-05-21T10:30Z",
    }
    assert "09:45–10:30 UTC" in installed["profile"]["description"]["en"]


def test_installed_0945_demo_window_preserves_all_independently_checked_evidence(reference_run):
    installed = json.loads((Path(__file__).parents[2] / "config/demos/03_zander_tx_buddy_experiment_a.config").read_text(encoding="utf-8"))
    installed_run = _calculate_run(reference_run.source_rows, configuration_document=installed)
    assert installed_run.configuration["end_utc"] - installed_run.configuration["start_utc"] == pd.Timedelta(minutes=45)
    # Keep the broader captured configuration as provenance. The shortened
    # installed window must preserve every row, not merely the sample count.
    _assert_scientific_rows(installed_run.sql_rows, pd.read_csv(REFERENCE_DIRECTORY / "expected_sql_rows.csv"))
    _assert_scientific_rows(installed_run.processed, pd.read_csv(REFERENCE_DIRECTORY / "expected_retained_rows.csv"))
    for frame_name in ("sql_rows", "processed", "stations", "units", "points"):
        pd.testing.assert_frame_equal(
            getattr(installed_run, frame_name), getattr(reference_run, frame_name), check_exact=True,
        )
    expected_histogram = pd.read_csv(REFERENCE_DIRECTORY / "expected_histogram_1db.csv", float_precision="round_trip")
    histogram = installed_run.recipe["spot_histogram"]
    np.testing.assert_array_equal(histogram["centers"], expected_histogram.delta_snr_db)
    np.testing.assert_array_equal(histogram["counts"], expected_histogram.joint_spots)
    assert len(installed_run.points) == histogram["value_count"] == 166


def test_frozen_sql_oracle_detects_wrong_mode_and_power_normalization(reference_run):
    expected = pd.read_csv(REFERENCE_DIRECTORY / "expected_sql_rows.csv")
    for original, replacement in (
        ("AND code = 1", "AND code IN (1, 4)"),
        ("snr - power + 30", "snr + 30"),
    ):
        query = reference_run.analysis.query
        assert original in query
        mutated = _execute_generated_sql(query.replace(original, replacement), reference_run.source_rows)
        with pytest.raises(AssertionError):
            _assert_scientific_rows(mutated, expected)


def test_paper_oracle_rejects_sign_shift_and_aggregation_changes(reference_run):
    paper = _read_json(PAPER_DIRECTORY, "paper_features.json")["digitization"]
    expected = np.asarray([entry["density_per_db"] for entry in paper["bins"][:9]])
    tolerance = paper["density_absolute_readout_tolerance_per_db"]
    original = reference_run.recipe["spot_histogram"]
    mutations = [reference_run.recipe["station_histogram"]]
    cycle_means = reference_run.points.groupby("plot_time").metric.mean()
    mutations.append(_vertical_metric_histogram_recipe(cycle_means))
    for operation in (lambda values: -values, lambda values: values + 1):
        mutation = dict(original)
        mutation["centers"] = operation(np.asarray(original["centers"]))
        mutations.append(mutation)
    for mutation in mutations:
        try:
            _, _, density = _paper_projection(mutation)
        except AssertionError:
            continue
        assert not np.all(np.abs(density - expected) <= tolerance)


def test_comparison_plot_inputs_read_raw_reports_but_never_expected_results(monkeypatch, reference_run):
    from scripts.internal import build_zander_fig4_comparison as builder

    read_csv = pd.read_csv
    opened_names = []

    def deny_expected_results(path, *args, **kwargs):
        name = Path(path).name
        opened_names.append(name)
        assert not name.startswith("expected_"), "Expected results must never supply plotted evidence"
        return read_csv(path, *args, **kwargs)

    monkeypatch.setattr(pd, "read_csv", deny_expected_results)
    comparison = builder.build_comparison_inputs()
    assert opened_names == ["source_rows.csv"]
    pd.testing.assert_frame_equal(comparison.run.points, reference_run.points)
    assert comparison.recipe is comparison.run.recipe["spot_histogram"]
    np.testing.assert_array_equal(comparison.recipe["counts"], reference_run.recipe["spot_histogram"]["counts"])
    assert comparison.counts.sum() == len(reference_run.points)


@pytest.mark.parametrize("mutation_stage", ["raw_report_snr", "production_sql_snr"])
def test_comparison_plot_values_follow_raw_and_production_mutations(monkeypatch, reference_run, mutation_stage):
    from scripts.internal import build_zander_fig4_comparison as builder

    baseline = builder.build_comparison_inputs(reference_run.source_rows.copy())
    witness = reference_run.points.loc[reference_run.points.metric.eq(-7)].iloc[0]
    slot = int(pd.Timestamp(witness.plot_time).timestamp()) // 120
    source_rows = reference_run.source_rows.copy()
    if mutation_stage == "raw_report_snr":
        selected = (
            source_rows.tx_sign.eq("SK0WE/P") & source_rows.rx_sign.eq(witness.station)
            & source_rows.rx_loc.eq(witness.grid)
            & pd.to_datetime(source_rows.time, utc=True).eq(witness.plot_time)
        )
        assert selected.sum() == 1
        source_rows.loc[selected, "snr"] += 1
    else:
        pipeline_globals = builder._calculate_run.__globals__
        execute_sql = pipeline_globals["_execute_generated_sql"]

        def alter_production_sql_snr(query, raw_rows):
            computed = execute_sql(query, raw_rows)
            selected = (
                computed.time_slot.eq(slot) & computed.peer_sign.eq(witness.station)
                & computed.peer_grid.eq(witness.grid)
            )
            assert selected.sum() == 1
            computed.loc[selected, "snr_u_norm"] += 1
            return computed

        monkeypatch.setitem(pipeline_globals, "_execute_generated_sql", alter_production_sql_snr)

    changed = builder.build_comparison_inputs(source_rows)
    assert changed.sample_count == baseline.sample_count
    assert changed.mean == pytest.approx(baseline.mean + 1 / baseline.sample_count, abs=1e-12)
    expected_differences = baseline.differences.copy()
    selected = (
        baseline.run.points.station.eq(witness.station)
        & baseline.run.points.grid.eq(witness.grid)
        & baseline.run.points.plot_time.eq(witness.plot_time)
    ).to_numpy()
    assert selected.sum() == 1
    expected_differences[selected] += 1
    np.testing.assert_array_equal(changed.differences, expected_differences)
    assert not np.array_equal(changed.recipe["counts"], baseline.recipe["counts"])
    assert not np.array_equal(changed.counts, baseline.counts)
    with pytest.raises(AssertionError):
        builder.verify_comparison_inputs_against_references(changed)


def test_comparison_expected_results_can_only_reject_computed_plot_values(monkeypatch, reference_run):
    from scripts.internal import build_zander_fig4_comparison as builder

    comparison = builder.build_comparison_inputs(reference_run.source_rows.copy())
    before = comparison.differences.copy()
    read_csv = pd.read_csv

    def corrupt_histogram_expectation(path, *args, **kwargs):
        rows = read_csv(path, *args, **kwargs)
        if Path(path).name == "expected_histogram_1db.csv":
            rows["joint_spots"] += 100
        return rows

    monkeypatch.setattr(pd, "read_csv", corrupt_histogram_expectation)
    with pytest.raises(AssertionError):
        builder.verify_comparison_inputs_against_references(comparison)
    np.testing.assert_array_equal(comparison.differences, before)
    np.testing.assert_array_equal(comparison.recipe["counts"], reference_run.recipe["spot_histogram"]["counts"])
