"""Regression contracts for the optional Delta-SNR episode report UI."""

import inspect
import json
from hashlib import sha256
from types import SimpleNamespace

import pandas as pd
import pytest

from core.analysis_context import AnalysisContext, COMPARISON_REFERENCE_STATION
from i18n import T
from ui.components import segment_inspector
from ui.inspector.outlier_candidates import (
    DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
    DELTA_SNR_OUTLIER_DETECTOR_VERSION,
    DeltaSnrOutlierCandidate,
    DeltaSnrOutlierModel,
    DeltaSnrOutlierReportEntry,
    OutlierStationIdentity,
)
from ui.inspector.outlier_report import (
    build_delta_snr_outlier_report_view_model,
)


EPISODE_START = pd.Timestamp("2021-06-01T18:38:00Z")


def _candidate(
    callsign,
    locator,
    anomaly_db,
    *,
    event_kind="short_burst",
    start_utc=EPISODE_START,
    observed_span_minutes=8.0,
    paired_unit_count=3,
    agreeing_unit_count=None,
    peak_anomaly_db=None,
    direction="W",
    target_values=(-10.0, -12.0, 2.0),
    reference_values=(-15.2, -12.0, -3.2),
    path_effective_cadence_minutes=2.0,
    maximum_episode_gap_minutes=6.0,
    diagnostic_neighborhood_minutes=15.0,
    nearby_joint_unit_count=None,
    nearby_target_only_unit_count=0,
    nearby_reference_only_unit_count=0,
    decode_edge_warning_reason=None,
):
    """Build one native paired-unit path episode with positive half-open bounds."""
    agreeing_unit_count = (
        paired_unit_count
        if agreeing_unit_count is None
        else agreeing_unit_count
    )
    peak_anomaly_db = (
        float(anomaly_db)
        if peak_anomaly_db is None
        else float(peak_anomaly_db)
    )
    nearby_joint_unit_count = (
        paired_unit_count
        if nearby_joint_unit_count is None
        else nearby_joint_unit_count
    )
    station_baseline_db = 0.3
    last_observed_utc = start_utc + pd.Timedelta(
        minutes=observed_span_minutes
    )
    return DeltaSnrOutlierCandidate(
        station_identity=OutlierStationIdentity(callsign, locator),
        direction_sector=direction,
        event_kind=event_kind,
        start_utc=start_utc,
        end_utc=last_observed_utc + pd.Timedelta(nanoseconds=1),
        representative_utc=last_observed_utc,
        representative_delta_snr_db=station_baseline_db + peak_anomaly_db,
        episode_median_delta_snr_db=station_baseline_db + anomaly_db,
        station_baseline_db=station_baseline_db,
        pre_baseline_db=0.2,
        post_baseline_db=0.4,
        median_anomaly_db=float(anomaly_db),
        peak_anomaly_db=peak_anomaly_db,
        mad_db=0.4,
        robust_spread_db=0.5,
        robust_spread_method="mad",
        robust_z=0.6745 * float(anomaly_db) / 0.5,
        pre_flank_cell_count=5,
        post_flank_cell_count=6,
        paired_unit_count=paired_unit_count,
        agreeing_paired_unit_count=agreeing_unit_count,
        paired_unit_sign_agreement_fraction=(
            agreeing_unit_count / paired_unit_count
        ),
        observed_span_minutes=float(observed_span_minutes),
        largest_gap_minutes=(
            0.0
            if paired_unit_count == 1
            else float(observed_span_minutes) / (paired_unit_count - 1)
        ),
        target_median_snr_db=target_values[0],
        target_baseline_db=target_values[1],
        target_anomaly_db=target_values[2],
        reference_median_snr_db=reference_values[0],
        reference_baseline_db=reference_values[1],
        reference_anomaly_db=reference_values[2],
        path_effective_cadence_minutes=path_effective_cadence_minutes,
        maximum_episode_gap_minutes=maximum_episode_gap_minutes,
        diagnostic_neighborhood_minutes=diagnostic_neighborhood_minutes,
        nearby_joint_unit_count=nearby_joint_unit_count,
        nearby_target_only_unit_count=nearby_target_only_unit_count,
        nearby_reference_only_unit_count=nearby_reference_only_unit_count,
        decode_edge_warning=decode_edge_warning_reason is not None,
        decode_edge_warning_reason=decode_edge_warning_reason,
    )


def _impulse(callsign="A1AAA", locator="AA00", **kwargs):
    """Build a one-unit spot impulse at one exact native timestamp."""
    return _candidate(
        callsign,
        locator,
        kwargs.pop("anomaly_db", 5.5),
        event_kind="spot_impulse",
        observed_span_minutes=0.0,
        paired_unit_count=1,
        **kwargs,
    )


def _report_entry(
    *candidates,
    episode_index=0,
    event_kind=None,
    coherence_scope="path_specific",
    contributing_station_count=8,
    evaluable_station_count=6,
    segment_median_signed_anomaly_db=1.2,
    segment_positive_station_count=3,
    segment_negative_station_count=2,
    segment_neutral_station_count=1,
    sector_summaries=(),
):
    """Build one same-sign contemporaneous detector report entry."""
    anomaly_values = [candidate.median_anomaly_db for candidate in candidates]
    positive_count = sum(value > 0.0 for value in anomaly_values)
    negative_count = sum(value < 0.0 for value in anomaly_values)
    sign_agreement = (
        "positive"
        if negative_count == 0
        else "negative"
        if positive_count == 0
        else "mixed"
    )
    segment_sign_agreement = (
        "mixed"
        if segment_positive_station_count and segment_negative_station_count
        else "positive"
        if segment_positive_station_count
        else "negative"
        if segment_negative_station_count
        else "neutral"
    )
    event_kinds = tuple(
        dict.fromkeys(candidate.event_kind for candidate in candidates)
    )
    maximum_candidate = max(
        candidates,
        key=lambda candidate: abs(candidate.peak_anomaly_db),
    )
    return DeltaSnrOutlierReportEntry(
        episode_index=episode_index,
        start_utc=min(candidate.start_utc for candidate in candidates),
        end_utc=max(candidate.end_utc for candidate in candidates),
        event_kind=(
            event_kind
            or (event_kinds[0] if len(event_kinds) == 1 else "mixed_duration")
        ),
        coherence_scope=coherence_scope,
        contributing_station_count=contributing_station_count,
        evaluable_station_count=evaluable_station_count,
        candidates=tuple(candidates),
        median_signed_anomaly_db=float(pd.Series(anomaly_values).median()),
        maximum_absolute_anomaly_db=abs(maximum_candidate.peak_anomaly_db),
        maximum_anomaly_db=maximum_candidate.peak_anomaly_db,
        sign_agreement=sign_agreement,
        agreeing_count=max(positive_count, negative_count),
        segment_median_signed_anomaly_db=segment_median_signed_anomaly_db,
        segment_sign_agreement=segment_sign_agreement,
        segment_agreeing_count=max(
            segment_positive_station_count,
            segment_negative_station_count,
        ),
        segment_positive_station_count=segment_positive_station_count,
        segment_negative_station_count=segment_negative_station_count,
        segment_neutral_station_count=segment_neutral_station_count,
        direction_sectors=tuple(
            dict.fromkeys(
                candidate.direction_sector
                for candidate in candidates
                if candidate.direction_sector is not None
            )
        ),
        sector_summaries=tuple(sector_summaries),
        station_identities=tuple(
            dict.fromkeys(
                candidate.station_identity for candidate in candidates
            )
        ),
    )


def _empty_model(*, populated=0, assessed=0, abstained=0, cadence=2.0):
    """Return one enabled active-scope model with no candidate episodes."""
    return DeltaSnrOutlierModel(
        detector_version=DELTA_SNR_OUTLIER_DETECTOR_VERSION,
        detection_resolution=DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
        paired_unit_cadence_minutes=cadence,
        analysis_start_utc=EPISODE_START,
        analysis_end_utc=EPISODE_START + pd.Timedelta(days=2),
        populated_station_cycle_count=populated,
        evaluable_station_cycle_count=assessed,
        abstained_station_cycle_count=abstained,
        candidates=(),
        report_entries=(),
        candidate_signature="empty-signature",
    )


def _episode_report_model():
    """Build one impulse card and one multi-path short-burst card."""
    impulse = _impulse(direction=None)
    burst_start = pd.Timestamp("2021-06-03T03:38:00Z")
    first_burst = _candidate(
        "B2BBB",
        "BB11",
        -4.5,
        start_utc=burst_start,
        peak_anomaly_db=-6.0,
        direction="SW",
    )
    second_burst = _candidate(
        "C3CCC",
        "CC22",
        -4.0,
        start_utc=burst_start + pd.Timedelta(minutes=2),
        peak_anomaly_db=-5.5,
        direction="WSW",
    )
    first_entry = _report_entry(impulse)
    second_entry = _report_entry(
        first_burst,
        second_burst,
        episode_index=1,
        coherence_scope="directionally_coherent",
        contributing_station_count=7,
        evaluable_station_count=5,
        segment_median_signed_anomaly_db=-2.0,
        segment_positive_station_count=0,
        segment_negative_station_count=5,
        segment_neutral_station_count=0,
    )
    return DeltaSnrOutlierModel(
        detector_version=DELTA_SNR_OUTLIER_DETECTOR_VERSION,
        detection_resolution=DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
        paired_unit_cadence_minutes=2.0,
        analysis_start_utc=first_entry.start_utc,
        analysis_end_utc=second_entry.end_utc,
        populated_station_cycle_count=24,
        evaluable_station_cycle_count=18,
        abstained_station_cycle_count=6,
        candidates=(impulse, first_burst, second_burst),
        report_entries=(first_entry, second_entry),
        candidate_signature="episode-card-signature",
    )


def _comparison_units_for_model(model):
    """Build the detector-declared Joint rows for every candidate episode."""
    return pd.DataFrame(
        [
            {
                "peer_sign": candidate.station_identity.callsign,
                "peer_grid": candidate.station_identity.locator,
                "evidence_utc": (
                    candidate.start_utc
                    + pd.Timedelta(
                        minutes=(
                            0.0
                            if candidate.paired_unit_count == 1
                            else candidate.observed_span_minutes
                            * unit_index
                            / (candidate.paired_unit_count - 1)
                        )
                    )
                ),
                "outcome": "joint",
                "paired_eligible": True,
                "target_snr_db": candidate.target_median_snr_db,
                "reference_snr_db": candidate.reference_median_snr_db,
                "metric": candidate.episode_median_delta_snr_db,
            }
            for candidate in model.candidates
            for unit_index in range(candidate.paired_unit_count)
        ]
    )


def _report_view_model(model, comparison_units=None):
    """Build the pure compact report view model used by rendering tests."""
    if comparison_units is None:
        comparison_units = _comparison_units_for_model(model)
    return build_delta_snr_outlier_report_view_model(
        model,
        comparison_units,
    )


def _model_for_entries(*entries):
    """Build one enabled detector model from exact report entries."""
    candidates = tuple(
        candidate
        for entry in entries
        for candidate in entry.candidates
    )
    return DeltaSnrOutlierModel(
        detector_version=DELTA_SNR_OUTLIER_DETECTOR_VERSION,
        detection_resolution=DELTA_SNR_OUTLIER_DETECTION_RESOLUTION,
        paired_unit_cadence_minutes=2.0,
        analysis_start_utc=min(entry.start_utc for entry in entries),
        analysis_end_utc=max(entry.end_utc for entry in entries),
        populated_station_cycle_count=max(1, len(candidates)),
        evaluable_station_cycle_count=max(1, len(candidates)),
        abstained_station_cycle_count=0,
        candidates=candidates,
        report_entries=tuple(entries),
        candidate_signature="report-view-model-signature",
    )


def test_utc_display_hides_positive_half_open_sentinel():
    """Show an impulse once and multi-unit bounds as first-to-last observed."""
    impulse_entry = _report_entry(_impulse())
    burst_entry = _report_entry(_candidate("B2BBB", "BB11", 4.0))

    assert segment_inspector._format_outlier_utc_range(
        impulse_entry,
        T["en"],
    ) == "01-Jun 18:38 UTC"
    assert segment_inspector._format_outlier_utc_range(
        impulse_entry,
        T["de"],
    ) == "01.06. 18:38 UTC"
    assert segment_inspector._format_outlier_utc_range(
        burst_entry,
        T["en"],
    ) == "01-Jun 18:38–18:46 UTC"


def test_multiple_spot_impulses_in_one_card_render_an_observed_range():
    """Do not collapse contemporaneous impulses on different paths to one time."""
    entry = _report_entry(
        _impulse(),
        _impulse(
            "B2BBB",
            "BB11",
            start_utc=EPISODE_START + pd.Timedelta(minutes=4),
        ),
        coherence_scope="multiple_paths",
    )

    assert entry.event_kind == "spot_impulse"
    assert segment_inspector._format_outlier_utc_range(entry, T["en"]) == (
        "01-Jun 18:38–18:42 UTC"
    )


def test_default_path_summary_is_compact_and_duration_aware():
    """Keep identity-adjacent duration and residual facts self-describing."""
    impulse = _impulse()
    burst = _candidate(
        "B2BBB",
        "BB11",
        -4.5,
        peak_anomaly_db=-6.0,
        agreeing_unit_count=2,
    )
    impulse_model = _model_for_entries(_report_entry(impulse))
    burst_model = _model_for_entries(_report_entry(burst))

    impulse_text = segment_inspector._format_outlier_candidate_facts(
        impulse,
        _report_view_model(impulse_model).cards[0],
        T["en"],
        False,
    )
    burst_text = segment_inspector._format_outlier_candidate_facts(
        burst,
        _report_view_model(burst_model).cards[0],
        T["en"],
        True,
    )

    assert impulse_text == (
        "1 Joint Spot · first-to-last span 0 min · median interval — · "
        "largest gap —\n\n- **Expected local ΔSNR:** +0.3 dB\n"
        "- **Observed median ΔSNR:** +5.8 dB\n"
        "- **Largest single-cycle departure:** +5.5 dB"
    )
    assert burst_text == (
        "3 complete Scheduled Pairs · first-to-last span 8 min · median "
        "interval 4 min · largest gap 4 min\n\n"
        "- **Expected local ΔSNR:** +0.3 dB\n"
        "- **Observed median ΔSNR:** −4.2 dB\n"
        "- **Largest single-cycle departure:** −6.0 dB"
    )


def test_report_view_model_keeps_only_qualifying_episode_joint_rows():
    """Keep Joint rows in the candidate window and hide diagnostic outcomes."""
    candidate = _candidate(
        "A1AAA",
        "AA00",
        5.0,
        direction="E",
        nearby_target_only_unit_count=1,
        nearby_reference_only_unit_count=1,
        decode_edge_warning_reason="reference_missing_near_positive_episode",
    )
    entry = _report_entry(
        candidate,
        contributing_station_count=1,
        evaluable_station_count=1,
        segment_positive_station_count=1,
        segment_negative_station_count=0,
        segment_neutral_station_count=0,
    )
    model = _model_for_entries(entry)
    comparison_units = pd.DataFrame(
        [
            ("A1AAA", "AA00", "2021-06-01T18:30:00Z", "target_only", -20.0, None, None),
            ("A1AAA", "AA00", "2021-06-01T18:34:00Z", "joint", -13.0, -16.0, 3.0),
            ("A1AAA", "AA00", "2021-06-01T18:38:00Z", "joint", -10.0, -14.3, 4.3),
            ("A1AAA", "AA00", "2021-06-01T18:42:00Z", "joint", -9.0, -14.3, 5.3),
            ("A1AAA", "AA00", "2021-06-01T18:46:00Z", "joint", -8.0, -14.3, 6.3),
            ("A1AAA", "AA00", "2021-06-01T18:50:00Z", "reference_only", None, -18.0, None),
            ("B2BBB", "BB11", "2021-06-01T18:40:00Z", "target_only", -7.0, None, None),
        ],
        columns=(
            "peer_sign",
            "peer_grid",
            "evidence_utc",
            "outcome",
            "target_snr_db",
            "reference_snr_db",
            "metric",
        ),
    )
    comparison_units["paired_eligible"] = True

    report_view_model = _report_view_model(model, comparison_units)
    rows = report_view_model.cards[0].evidence_rows

    assert [row.evidence_utc.strftime("%H:%M") for row in rows] == [
        "18:38",
        "18:42",
        "18:46",
    ]
    assert all(not hasattr(row, "outcome") for row in rows)
    assert rows[1].local_baseline_db == pytest.approx(0.3)
    assert rows[1].residual_db == pytest.approx(5.0)
    assert rows[1].target_snr_db == pytest.approx(-9.0)
    assert rows[1].reference_snr_db == pytest.approx(-14.3)
    assert candidate.nearby_target_only_unit_count == 1
    assert candidate.nearby_reference_only_unit_count == 1
    assert candidate.decode_edge_warning is True


def test_cycle_evidence_table_uses_joint_only_columns_in_scientific_order():
    """Expose only the six approved Joint-evidence interpretation columns."""
    candidate = _candidate("A1AAA", "AA00", 5.0, direction="E")
    entry = _report_entry(
        candidate,
        contributing_station_count=1,
        evaluable_station_count=1,
        segment_positive_station_count=1,
        segment_negative_station_count=0,
        segment_neutral_station_count=0,
    )
    model = _model_for_entries(entry)
    comparison_units = pd.DataFrame(
        [
            {
                "peer_sign": "A1AAA",
                "peer_grid": "AA00",
                "evidence_utc": EPISODE_START,
                "outcome": "joint",
                "paired_eligible": True,
                "target_snr_db": -10.0,
                "reference_snr_db": -15.3,
                "metric": 5.3,
            },
            {
                "peer_sign": "A1AAA",
                "peer_grid": "AA00",
                "evidence_utc": EPISODE_START - pd.Timedelta(minutes=2),
                "outcome": "target_only",
                "paired_eligible": True,
                "target_snr_db": -20.0,
                "reference_snr_db": None,
                "metric": None,
            },
        ]
    )
    card = _report_view_model(model, comparison_units).cards[0]

    table = segment_inspector._build_outlier_cycle_evidence_table(
        card,
        T["en"],
    )

    assert list(table.columns) == [
        "UTC",
        "Path",
        "Direction",
        "Local baseline (dB)",
        "ΔSNR (dB)",
        "Residual (dB)",
    ]
    assert len(table) == 1
    assert table.iloc[0].to_dict() == {
        T["en"]["col_outlier_evidence_utc"]: "2021-06-01 18:38 UTC",
        T["en"]["col_outlier_evidence_path"]: "A1AAA (AA00)",
        T["en"]["col_outlier_evidence_direction"]: "E",
        T["en"]["col_outlier_evidence_local_baseline"]: "+0.3",
        T["en"]["col_outlier_evidence_delta_snr"]: "+5.3",
        T["en"]["col_outlier_evidence_residual"]: "+5.0",
    }


def test_single_path_selection_replaces_existing_station_insights_selection():
    """A path action selects exactly its callsign and locator identity."""
    station_identity = OutlierStationIdentity("A1AAA", "AA00")
    session_state = {
        segment_inspector.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY: [
            {"callsign": "Z9ZZZ", "locator": "ZZ99"},
            {"callsign": "Y8YYY", "locator": "YY88"},
        ],
        segment_inspector.RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY: 2,
    }

    selected = segment_inspector._select_outlier_path(
        station_identity,
        session_state,
        analysis_id="RX_COMP",
        run_id=9,
        scope_token="active",
    )

    assert selected == [{"callsign": "A1AAA", "locator": "AA00"}]
    assert session_state[
        segment_inspector.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY
    ] == selected
    assert session_state[
        segment_inspector.RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY
    ] == 3


@pytest.mark.parametrize(
    ("entry_kwargs", "message"),
    (
        (
            {
                "contributing_station_count": 1,
                "evaluable_station_count": 2,
                "segment_positive_station_count": 2,
                "segment_negative_station_count": 0,
                "segment_neutral_station_count": 0,
            },
            "flagged <= assessed <= paired evidence",
        ),
        (
            {
                "segment_positive_station_count": -1,
                "segment_negative_station_count": 6,
                "segment_neutral_station_count": 1,
            },
            "sign counts must be non-negative",
        ),
        (
            {
                "segment_positive_station_count": 3,
                "segment_negative_station_count": 2,
                "segment_neutral_station_count": 0,
            },
            "must sum to the assessed-path count",
        ),
    ),
)
def test_report_entry_rejects_invalid_episode_denominators(entry_kwargs, message):
    """Fail loudly for invalid episode-level path relationships."""
    entry = _report_entry(_impulse(), **entry_kwargs)

    with pytest.raises(ValueError, match=message):
        segment_inspector._validate_outlier_report_entry_counts(entry)


def test_episode_selection_preserves_detector_path_order():
    """Select one report entry's unique exact callsign and locator identities."""
    entry = _report_entry(
        _candidate("B2BBB", "BB11", 5.0),
        _candidate("A1AAA", "AA00", 4.0),
    )
    session_state = {
        segment_inspector.RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY: 4
    }

    selected = segment_inspector._select_outlier_episode_paths(
        entry,
        session_state,
        analysis_id="RX_COMP",
        run_id=9,
        scope_token="active",
    )

    assert selected == [
        {"callsign": "B2BBB", "locator": "BB11"},
        {"callsign": "A1AAA", "locator": "AA00"},
    ]
    assert session_state[
        segment_inspector.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY
    ] == selected
    assert session_state[
        segment_inspector.RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY
    ] == 5


def test_marker_adapter_condenses_all_paths_but_preserves_selected_paths():
    """Use one episode marker globally and one marker per selected path."""
    model = _episode_report_model()

    all_path_recipe = segment_inspector._delta_snr_outlier_marker_recipe(
        model,
        T["en"],
    )
    selected_path_recipe = segment_inspector._delta_snr_outlier_marker_recipe(
        model,
        T["en"],
        pd.DataFrame(
            {
                "peer_sign": ["B2BBB", "C3CCC"],
                "peer_grid": ["BB11", "CC22"],
            }
        ),
    )

    assert all_path_recipe["candidate_count"] == 2
    assert {
        (marker["callsign"], marker["locator"])
        for marker in all_path_recipe["markers"]
    } == {("A1AAA", "AA00"), ("B2BBB", "BB11")}
    assert selected_path_recipe["candidate_count"] == 2
    assert {
        (marker["callsign"], marker["locator"])
        for marker in selected_path_recipe["markers"]
    } == {("B2BBB", "BB11"), ("C3CCC", "CC22")}
    expected_signature = sha256(
        json.dumps(
            all_path_recipe["markers"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    ).hexdigest()
    assert all_path_recipe["candidate_signature"] == expected_signature


def test_marker_adapter_preserves_legacy_recipe_without_report_entries():
    """Keep compatibility with marker-only cache and integration test doubles."""
    marker_payload = [
        {
            "callsign": "A1AAA",
            "locator": "AA00",
            "marker_utc_ns": int(EPISODE_START.value),
            "marker_delta_snr_db": 5.8,
            "episode_start_utc_ns": int(EPISODE_START.value),
            "episode_end_utc_ns": int(
                (EPISODE_START + pd.Timedelta(nanoseconds=1)).value
            ),
            "event_kind": "spot_impulse",
        }
    ]
    legacy_recipe = {
        "schema_version": 2,
        "detector_version": "legacy-test",
        "detection_resolution": "native-cycle",
        "candidate_count": 1,
        "candidate_signature": "legacy-signature",
        "markers": marker_payload,
    }
    legacy_model = SimpleNamespace(
        marker_recipe=lambda _station_identities: dict(legacy_recipe)
    )

    adapted_recipe = segment_inspector._delta_snr_outlier_marker_recipe(
        legacy_model,
        T["en"],
    )

    assert adapted_recipe["markers"] == marker_payload
    assert adapted_recipe["candidate_count"] == 1
    assert adapted_recipe["candidate_signature"] == "legacy-signature"
    assert adapted_recipe["legend_label"] == T["en"][
        "fig_delta_snr_outlier_candidate"
    ]


def _install_report_streamlit_fake(
    monkeypatch,
    *,
    clicked_button_indices=(),
    session_state=None,
):
    """Install a recording Streamlit boundary for episode-card tests."""
    clicked_button_indices = set(clicked_button_indices)
    render_state = SimpleNamespace(
        cards=[],
        button_calls=[],
        markdown_calls=[],
        info_calls=[],
        navigation_calls=[],
        rerun_calls=[],
        session_state={} if session_state is None else session_state,
    )

    class FakeMetricColumn:
        """Record one metric against its containing episode card."""

        def __init__(self, card):
            self.card = card

        def metric(self, label, value):
            self.card.metric_calls.append((label, value))

    class FakeExpander:
        """Record one collapsed episode-level detail table."""

        def __init__(self, label, kwargs):
            self.label = label
            self.kwargs = kwargs
            self.dataframe_calls = []

        def dataframe(self, dataframe, **kwargs):
            self.dataframe_calls.append((dataframe, kwargs))

    class FakeCard:
        """Record one native detector episode without hourly child cards."""

        def __init__(self, key, border):
            self.key = key
            self.border = border
            self.markdown_calls = []
            self.caption_calls = []
            self.column_specs = []
            self.horizontal_containers = []
            self.metric_calls = []
            self.expanders = []
            self.render_order = []

        def markdown(self, body, **_kwargs):
            self.markdown_calls.append(body)
            self.render_order.append(("markdown", body))

        def caption(self, body, **_kwargs):
            self.caption_calls.append(body)
            self.render_order.append(("caption", body))

        def columns(self, column_spec):
            self.column_specs.append(column_spec)
            return [FakeMetricColumn(self) for _width in column_spec]

        def container(self, **kwargs):
            container = FakeHorizontalContainer(self, kwargs)
            self.horizontal_containers.append(container)
            return container

        def expander(self, label, **kwargs):
            expander = FakeExpander(label, kwargs)
            self.expanders.append(expander)
            return expander

        def button(self, label, **kwargs):
            button_index = len(render_state.button_calls)
            button_call = (self, label, kwargs)
            render_state.button_calls.append(button_call)
            self.render_order.append(("button", label))
            return button_index in clicked_button_indices

    class FakeHorizontalContainer:
        """Record one path heading and its adjacent Station Insights action."""

        def __init__(self, card, kwargs):
            self.card = card
            self.kwargs = kwargs
            self.render_order = []

        def markdown(self, body, **_kwargs):
            self.card.markdown_calls.append(body)
            self.card.render_order.append(("markdown", body))
            self.render_order.append(("markdown", body))

        def button(self, label, **kwargs):
            button_index = len(render_state.button_calls)
            render_state.button_calls.append((self, label, kwargs))
            self.card.render_order.append(("button", label))
            self.render_order.append(("button", label))
            return button_index in clicked_button_indices

    def fake_container(*, border, key):
        card = FakeCard(key, border)
        render_state.cards.append(card)
        return card

    monkeypatch.setattr(
        segment_inspector,
        "st",
        SimpleNamespace(
            markdown=lambda body, **_kwargs: render_state.markdown_calls.append(
                body
            ),
            info=lambda body, **_kwargs: render_state.info_calls.append(body),
            container=fake_container,
            rerun=lambda **kwargs: render_state.rerun_calls.append(kwargs),
            session_state=render_state.session_state,
        ),
    )
    monkeypatch.setattr(
        segment_inspector,
        "request_page_navigation",
        lambda session_state, anchor_id, *, should_scroll: (
            render_state.navigation_calls.append(
                (session_state, anchor_id, should_scroll)
            )
        ),
        raising=False,
    )
    monkeypatch.setattr(
        segment_inspector,
        "render_result_guidance_popover",
        lambda *_args, **_kwargs: None,
    )
    return render_state


@pytest.mark.parametrize(
    ("is_sequential", "expander_label_key"),
    (
        (
            False,
            "exp_outlier_wspr_cycle_evidence",
        ),
        (
            True,
            "exp_outlier_scheduled_pair_evidence",
        ),
    ),
)
def test_report_renders_one_card_per_detector_entry_without_hourly_nesting(
    monkeypatch,
    is_sequential,
    expander_label_key,
):
    """Hide a redundant one-row table but retain multi-cycle evidence."""
    model = _episode_report_model()
    report_view_model = _report_view_model(model)
    render_state = _install_report_streamlit_fake(monkeypatch)

    segment_inspector._render_delta_snr_outlier_report(
        model,
        report_view_model,
        t=T["en"],
        language="en",
        analysis_id="RX_COMP",
        run_id=9,
        scope_token="active",
        is_sequential=is_sequential,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )

    assert len(render_state.cards) == len(model.report_entries) == 2
    assert all(card.border is True for card in render_state.cards)
    assert len({card.key for card in render_state.cards}) == 2
    assert [len(card.caption_calls) for card in render_state.cards] == [1, 2]
    assert "Spot impulse · 01-Jun 18:38 UTC" in (
        render_state.cards[0].markdown_calls[0]
    )
    assert "Short burst · 03-Jun 03:38–03:48 UTC" in (
        render_state.cards[1].markdown_calls[0]
    )
    for card in render_state.cards:
        assert card.column_specs == []
        assert card.metric_calls == []
    assert [len(card.expanders) for card in render_state.cards] == [0, 1]
    evidence_expander = render_state.cards[1].expanders[0]
    expected_range = segment_inspector._format_outlier_utc_range(
        model.report_entries[1],
        T["en"],
    )
    assert evidence_expander.label == T["en"][
        expander_label_key
    ].format(utc_range=expected_range)
    assert evidence_expander.kwargs["expanded"] is False
    assert evidence_expander.kwargs["icon"] == ":material/table_view:"
    assert len(evidence_expander.dataframe_calls) == 1
    evidence_table = evidence_expander.dataframe_calls[0][0]
    assert len(evidence_table) > 1
    assert list(evidence_table.columns) == [
        T["en"]["col_outlier_evidence_utc"],
        T["en"]["col_outlier_evidence_path"],
        T["en"]["col_outlier_evidence_direction"],
        T["en"]["col_outlier_evidence_local_baseline"],
        T["en"]["col_outlier_evidence_delta_snr"],
        T["en"]["col_outlier_evidence_residual"],
    ]
    assert "Outcome" not in evidence_table.columns

    first_card_markup = "\n".join(render_state.cards[0].markdown_calls)
    assert "Path 1 · A1AAA (AA00) · Not available" in first_card_markup
    second_card_markup = "\n".join(render_state.cards[1].markdown_calls)
    assert "Path 1 · B2BBB (BB11) · SW" in second_card_markup
    assert "Path 2 · C3CCC (CC22) · WSW" in second_card_markup
    expected_impulse_count = (
        "1 complete Scheduled Pair" if is_sequential else "1 Joint Spot"
    )
    assert expected_impulse_count in render_state.cards[0].caption_calls[0]
    assert "median interval —" in (
        render_state.cards[0].caption_calls[0]
    )
    assert "**Expected local ΔSNR:** +0.3 dB" in (
        render_state.cards[0].caption_calls[0]
    )
    assert render_state.cards[0].caption_calls[0].index(
        "**Expected local ΔSNR:**"
    ) < render_state.cards[0].caption_calls[0].index(
        "**Observed median ΔSNR:**"
    )
    assert "Typical departure from baseline" not in (
        render_state.cards[0].caption_calls[0]
    )
    first_path_row = render_state.cards[0].horizontal_containers[0]
    assert first_path_row.kwargs["horizontal"] is True
    assert first_path_row.kwargs["horizontal_alignment"] == "distribute"
    assert first_path_row.kwargs["vertical_alignment"] == "center"
    assert first_path_row.render_order == [
        ("markdown", "###### Path 1 · A1AAA (AA00) · Not available"),
        ("button", T["en"]["btn_outlier_show_path_in_station_insights"]),
    ]
    assert [len(card.horizontal_containers) for card in render_state.cards] == [
        1,
        2,
    ]
    assert T["en"]["txt_outlier_direction_unavailable"] in first_card_markup
    assert [call[1] for call in render_state.button_calls] == [
        T["en"]["btn_outlier_show_path_in_station_insights"],
        T["en"]["btn_outlier_show_path_in_station_insights"],
        T["en"]["btn_outlier_show_path_in_station_insights"],
        T["en"]["btn_outlier_show_all_paths_in_station_insights"],
    ]
    assert render_state.session_state == {}


def test_repeated_candidates_on_one_path_keep_labeled_timeframes(monkeypatch):
    """Do not drop or render ambiguous fact lines for a repeated path."""
    first_candidate = _candidate("A1AAA", "AA00", 5.0, direction="E")
    second_candidate = _candidate(
        "A1AAA",
        "AA00",
        4.0,
        start_utc=EPISODE_START + pd.Timedelta(minutes=12),
        observed_span_minutes=4.0,
        paired_unit_count=2,
        direction="E",
    )
    entry = _report_entry(
        first_candidate,
        second_candidate,
        contributing_station_count=1,
        evaluable_station_count=1,
        segment_positive_station_count=1,
        segment_negative_station_count=0,
        segment_neutral_station_count=0,
    )
    model = _model_for_entries(entry)
    report_view_model = _report_view_model(model)
    render_state = _install_report_streamlit_fake(monkeypatch)

    segment_inspector._render_delta_snr_outlier_report(
        model,
        report_view_model,
        t=T["en"],
        language="en",
        analysis_id="RX_COMP",
        run_id=9,
        scope_token="active",
        is_sequential=False,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )

    card = render_state.cards[0]
    card_markup = "\n".join(card.markdown_calls)
    assert card_markup.count("Path 1 · A1AAA (AA00) · E") == 1
    assert "Timeframe 01-Jun 18:38–18:46 UTC" in card_markup
    assert "Timeframe 01-Jun 18:50–18:54 UTC" in card_markup
    assert sum(
        "Observed median ΔSNR" in caption for caption in card.caption_calls
    ) == 2
    evidence_table = card.expanders[0].dataframe_calls[0][0]
    assert len(evidence_table) == 5
    assert [call[1] for call in render_state.button_calls] == [
        T["en"]["btn_outlier_show_path_in_station_insights"]
    ]


@pytest.mark.parametrize(
    ("clicked_button_index", "expected_selection"),
    (
        (1, [{"callsign": "B2BBB", "locator": "BB11"}]),
        (2, [{"callsign": "C3CCC", "locator": "CC22"}]),
        (
            3,
            [
                {"callsign": "B2BBB", "locator": "BB11"},
                {"callsign": "C3CCC", "locator": "CC22"},
            ],
        ),
    ),
)
def test_station_insights_actions_select_the_requested_paths(
    monkeypatch,
    clicked_button_index,
    expected_selection,
):
    """Wire path and all-path actions to their exact identity sets."""
    model = _episode_report_model()
    session_state = {
        segment_inspector.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY: [
            {"callsign": "Z9ZZZ", "locator": "ZZ99"}
        ],
        segment_inspector.RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY: 4,
    }
    render_state = _install_report_streamlit_fake(
        monkeypatch,
        clicked_button_indices=(clicked_button_index,),
        session_state=session_state,
    )

    segment_inspector._render_delta_snr_outlier_report(
        model,
        _report_view_model(model),
        t=T["en"],
        language="en",
        analysis_id="RX_COMP",
        run_id=9,
        scope_token="active",
        is_sequential=False,
        analysis_context=AnalysisContext(
            comparison_mode=COMPARISON_REFERENCE_STATION
        ),
    )

    assert len(render_state.button_calls) == 4
    assert session_state[
        segment_inspector.RESULTS_SELECTED_STATIONS_COMPARE_STATE_KEY
    ] == expected_selection
    assert session_state[
        segment_inspector.RESULTS_STATION_SELECTION_REVISION_COMPARE_STATE_KEY
    ] == 5
    assert session_state[
        segment_inspector.RESULTS_STATION_INSIGHTS_FOCUS_COMPARE_STATE_KEY
    ] == {
        "analysis_id": "RX_COMP",
        "run_id": 9,
        "scope_token": "active",
        "station_identities": expected_selection,
    }
    assert len(render_state.navigation_calls) == 1
    navigation_state, anchor_id, should_scroll = render_state.navigation_calls[0]
    assert navigation_state is session_state
    assert anchor_id == segment_inspector.STATION_INSIGHTS_ANCHOR_ID
    assert should_scroll is True
    assert render_state.rerun_calls == [{"scope": "app"}]


def test_enabled_empty_report_uses_native_cycle_counters(monkeypatch):
    """Distinguish no pairs, baseline abstention, and no qualifying episode."""
    render_state = _install_report_streamlit_fake(monkeypatch)

    for model in (
        _empty_model(),
        _empty_model(populated=8, assessed=0, abstained=8),
        _empty_model(populated=10, assessed=7, abstained=3),
    ):
        segment_inspector._render_delta_snr_outlier_report(
            model,
            _report_view_model(model, pd.DataFrame()),
            t=T["en"],
            language="en",
            analysis_id="RX_COMP",
            run_id=9,
            scope_token="active",
            is_sequential=False,
            analysis_context=AnalysisContext(
                comparison_mode=COMPARISON_REFERENCE_STATION
            ),
        )

    paired_evidence = T["en"]["txt_outlier_paired_evidence_joint"]
    assert render_state.info_calls == [
        T["en"]["msg_outlier_report_insufficient_paired_evidence"].format(
            paired_evidence=paired_evidence,
        ),
        T["en"]["msg_outlier_report_insufficient_local_baseline"].format(
            populated="8",
            abstained="8",
            paired_evidence=paired_evidence,
        ),
        T["en"]["msg_outlier_report_no_candidates"].format(
            assessed="7",
            abstained="3",
            populated="10",
            paired_evidence=paired_evidence,
        ),
    ]


def test_report_has_no_fixed_hour_grouping_contract():
    """Keep native report entries as the sole user-visible episode model."""
    module_source = inspect.getsource(segment_inspector)
    report_source = inspect.getsource(
        segment_inspector._render_delta_snr_outlier_report
    )

    assert "group_delta_snr_outlier_review_episodes" not in module_source
    assert "hourly_entries" not in report_source
    assert "bin_index" not in report_source
    assert "for episode_card, report_entry in zip(" in report_source


def test_report_call_is_after_temporal_evidence_and_before_station_insights():
    """Preserve the requested evidence hierarchy without a new large figure."""
    function_source = inspect.getsource(
        segment_inspector._render_segment_inspector_body
    )
    temporal_position = function_source.index(
        "segment_temporal_export = _render_segment_temporal_evidence("
    )
    report_position = function_source.index(
        "_render_delta_snr_outlier_report(",
        temporal_position,
    )
    station_insights_position = function_source.index(
        "level_three_container = st.container(",
        report_position,
    )

    assert temporal_position < report_position < station_insights_position
    assert "if is_outlier_reporting_enabled:" in function_source[
        temporal_position:report_position
    ]
