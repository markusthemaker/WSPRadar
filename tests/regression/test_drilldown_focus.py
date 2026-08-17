from dataclasses import FrozenInstanceError

import pandas as pd
import pytest

from ui.inspector.drilldown_focus import (
    DRILLDOWN_OUTLIER_FOCUS_OPTION,
    DrilldownFocusWindow,
    available_manual_zoom_options,
    default_focus_center_utc,
    drilldown_outlier_candidate_context_for_scope,
    filter_station_rows_to_focus_window,
    focus_center_utc,
    manual_zoom_center_bounds,
    parse_drilldown_outlier_candidate_context,
    resolve_centered_zoom_window,
    resolve_outlier_focus_window,
)


def _utc_nanoseconds(value: object) -> int:
    return int(pd.Timestamp(value).value)


def _candidate_context_mapping(
    representative_utc: object = "2026-01-01T12:00:00.123456789Z",
) -> dict[str, object]:
    representative = pd.Timestamp(representative_utc)
    return {
        "schema_version": 1,
        "analysis_id": "RX_COMP",
        "run_id": 7,
        "scope_token": "rall_dall",
        "callsign": "a1aaa",
        "locator": "aa00",
        "request_token": "candidate-1",
        "representative_utc_ns": int(representative.value),
        "representative_delta_snr_db": 10.0,
        "event_start_utc_ns": int(
            (representative - pd.Timedelta(minutes=2)).value
        ),
        "event_end_utc_ns": int(
            (representative + pd.Timedelta(nanoseconds=1)).value
        ),
        "baseline_anchor_start_utc_ns": int(
            (representative - pd.Timedelta(minutes=10)).value
        ),
        "baseline_anchor_end_utc_ns": int(
            (representative + pd.Timedelta(minutes=10)).value
        ),
        "episode_guard_minutes": 10.0,
        "pre_flank_start_utc_ns": int(
            (representative - pd.Timedelta(hours=7)).value
        ),
        "pre_flank_end_utc_ns": int(
            (representative - pd.Timedelta(minutes=20)).value
        ),
        "post_flank_start_utc_ns": int(
            (representative + pd.Timedelta(minutes=20)).value
        ),
        "post_flank_end_utc_ns": int(
            (representative + pd.Timedelta(hours=7)).value
        ),
        "local_baseline_db": 2.0,
        "pre_baseline_db": 1.8,
        "post_baseline_db": 2.2,
        "robust_spread_db": 1.0,
        "robust_spread_method": "mad",
        "robust_z": 5.4,
        "minimum_robust_z": 3.0,
        "minimum_departure_db": 6.0,
        "detector_version": "native-residual-episode-v7",
        "candidate_signature": "candidate-signature",
    }


def test_manual_zoom_options_require_the_complete_duration():
    assert available_manual_zoom_options(
        "2026-01-01T00:00:00Z",
        "2026-01-01T05:59:59Z",
    ) == ("off", "1h", "3h")
    assert available_manual_zoom_options(
        "2026-01-01T00:00:00Z",
        "2026-01-02T00:00:00Z",
    ) == ("off", "1h", "3h", "6h", "12h", "24h")


def test_centered_zoom_clamps_at_both_edges_without_shortening():
    upper_focus = resolve_centered_zoom_window(
        "2026-01-01T00:00:00Z",
        "2026-01-02T00:00:00Z",
        "6h",
        "2026-01-01T23:00:00Z",
    )
    assert upper_focus.start_utc == pd.Timestamp("2026-01-01T18:00:00Z")
    assert upper_focus.end_utc == pd.Timestamp("2026-01-02T00:00:00Z")
    assert upper_focus.duration == pd.Timedelta(hours=6)
    assert focus_center_utc(upper_focus) == pd.Timestamp(
        "2026-01-01T21:00:00Z"
    )

    lower_focus = resolve_centered_zoom_window(
        "2026-01-01T00:00:00Z",
        "2026-01-02T00:00:00Z",
        "6h",
        "2025-12-31T20:00:00Z",
    )
    assert lower_focus.start_utc == pd.Timestamp("2026-01-01T00:00:00Z")
    assert lower_focus.end_utc == pd.Timestamp("2026-01-01T06:00:00Z")
    assert lower_focus.duration == pd.Timedelta(hours=6)


def test_center_bounds_and_default_center_are_exact_inverses():
    earliest, latest = manual_zoom_center_bounds(
        "2026-01-01T00:00:00Z",
        "2026-01-02T00:00:00Z",
        "6h",
    )
    assert earliest == pd.Timestamp("2026-01-01T03:00:00Z")
    assert latest == pd.Timestamp("2026-01-01T21:00:00Z")
    assert default_focus_center_utc(
        "2026-01-01T00:00:00Z",
        "2026-01-02T00:00:00Z",
        "6h",
    ) == pd.Timestamp("2026-01-01T12:00:00Z")

    requested_center = pd.Timestamp("2026-01-01T13:17:22.123456789Z")
    focus = resolve_centered_zoom_window(
        "2026-01-01T00:00:00Z",
        "2026-01-02T00:00:00Z",
        "3h",
        requested_center,
    )
    assert focus_center_utc(focus) == requested_center


def test_centered_zoom_rejects_a_preset_that_does_not_fit():
    with pytest.raises(ValueError, match="does not fit"):
        resolve_centered_zoom_window(
            "2026-01-01T00:00:00Z",
            "2026-01-01T02:00:00Z",
            "3h",
            "2026-01-01T01:00:00Z",
        )


def test_candidate_context_round_trip_preserves_exact_utc_and_is_immutable():
    context = parse_drilldown_outlier_candidate_context(
        _candidate_context_mapping()
    )
    assert context.station_identity == ("A1AAA", "AA00")
    assert context.representative_utc == pd.Timestamp(
        "2026-01-01T12:00:00.123456789Z"
    )
    assert parse_drilldown_outlier_candidate_context(
        context.as_session_mapping()
    ) == context
    with pytest.raises(FrozenInstanceError):
        context.local_baseline_db = 9.0


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "message"),
    (
        ("robust_spread_db", 0.0, "robust_spread_db must be positive"),
        ("minimum_robust_z", float("nan"), "must be a finite number"),
        ("callsign", "../bad", "callsign is invalid"),
    ),
)
def test_candidate_context_rejects_invalid_scientific_fields(
    field_name,
    invalid_value,
    message,
):
    record = _candidate_context_mapping()
    record[field_name] = invalid_value
    with pytest.raises(ValueError, match=message):
        parse_drilldown_outlier_candidate_context(record)


def test_candidate_context_rejects_representative_outside_event():
    record = _candidate_context_mapping()
    record["event_end_utc_ns"] = record["representative_utc_ns"]
    with pytest.raises(ValueError, match="inside its half-open event"):
        parse_drilldown_outlier_candidate_context(record)


def test_candidate_context_is_scoped_without_being_merged_into_active_window():
    record = _candidate_context_mapping()
    context = drilldown_outlier_candidate_context_for_scope(
        record,
        analysis_id="RX_COMP",
        run_id=7,
        scope_token="rall_dall",
        selected_identity=("A1AAA", "AA00"),
        analysis_start_utc="2026-01-01T00:00:00Z",
        analysis_end_utc="2026-01-02T00:00:00Z",
    )
    assert context is not None
    manual_focus = resolve_centered_zoom_window(
        "2026-01-01T00:00:00Z",
        "2026-01-02T00:00:00Z",
        "3h",
        "2026-01-01T15:00:00Z",
    )
    assert context.representative_utc == pd.Timestamp(
        "2026-01-01T12:00:00.123456789Z"
    )
    assert manual_focus.option == "3h"
    assert drilldown_outlier_candidate_context_for_scope(
        record,
        analysis_id="RX_COMP",
        run_id=8,
        scope_token="rall_dall",
        selected_identity=("A1AAA", "AA00"),
        analysis_start_utc="2026-01-01T00:00:00Z",
        analysis_end_utc="2026-01-02T00:00:00Z",
    ) is None


def test_outlier_focus_is_the_exact_clipped_detector_support_window():
    context = parse_drilldown_outlier_candidate_context(
        _candidate_context_mapping()
    )
    focus = resolve_outlier_focus_window(
        "2026-01-01T06:00:00Z",
        "2026-01-01T18:00:00Z",
        context,
    )
    assert focus.start_utc == pd.Timestamp("2026-01-01T06:00:00Z")
    assert focus.end_utc == pd.Timestamp("2026-01-01T18:00:00Z")
    assert focus.option == DRILLDOWN_OUTLIER_FOCUS_OPTION
    assert focus.origin == DRILLDOWN_OUTLIER_FOCUS_OPTION


def test_stale_outlier_focus_outside_analysis_is_rejected():
    context = parse_drilldown_outlier_candidate_context(
        _candidate_context_mapping()
    )
    with pytest.raises(ValueError, match="representative UTC lies outside"):
        resolve_outlier_focus_window(
            "2026-01-03T00:00:00Z",
            "2026-01-04T00:00:00Z",
            context,
        )


def test_cycle_row_filter_uses_half_open_utc_window():
    rows = pd.DataFrame(
        {
            "time_slot": [
                _utc_nanoseconds("2026-01-01T00:00:00Z") // 120_000_000_000,
                _utc_nanoseconds("2026-01-01T00:02:00Z") // 120_000_000_000,
                _utc_nanoseconds("2026-01-01T01:00:00Z") // 120_000_000_000,
                _utc_nanoseconds("2026-01-01T01:02:00Z") // 120_000_000_000,
            ],
            "row": ["before", "start", "inside", "end"],
        }
    )
    focus = resolve_centered_zoom_window(
        "2026-01-01T00:00:00Z",
        "2026-01-01T02:00:00Z",
        "1h",
        "2026-01-01T00:32:00Z",
    )
    filtered = filter_station_rows_to_focus_window(
        rows,
        focus,
        is_sequential=False,
    )
    assert filtered["row"].tolist() == ["start", "inside"]


def test_sequential_row_filter_retains_or_excludes_complete_pairs_by_target_start():
    rows = pd.DataFrame(
        {
            "time": pd.to_datetime(
                [
                    "2026-01-01T00:00:00Z",
                    "2026-01-01T00:02:00Z",
                    "2026-01-01T00:10:00Z",
                    "2026-01-01T00:12:00Z",
                ],
                utc=True,
            ),
            "is_me": [1, 0, 1, 0],
            "side": ["target-1", "reference-1", "target-2", "reference-2"],
        }
    )
    focus = DrilldownFocusWindow(
        start_utc=pd.Timestamp("2026-01-01T00:10:00Z"),
        end_utc=pd.Timestamp("2026-01-01T00:20:00Z"),
        option="10m-test",
        origin="test",
    )
    filtered = filter_station_rows_to_focus_window(
        rows,
        focus,
        is_sequential=True,
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    )
    assert filtered["side"].tolist() == ["target-2", "reference-2"]
    assert filtered["tx_ab_pair_id"].nunique() == 1

    focus_after_pair_start = DrilldownFocusWindow(
        start_utc=pd.Timestamp("2026-01-01T00:11:00Z"),
        end_utc=pd.Timestamp("2026-01-01T00:20:00Z"),
        option="9m-test",
        origin="test",
    )
    assert filter_station_rows_to_focus_window(
        rows,
        focus_after_pair_start,
        is_sequential=True,
        tx_ab_repeat_interval_minutes=10,
        tx_ab_target_start_minute=0,
        tx_ab_reference_start_minute=2,
    ).empty
