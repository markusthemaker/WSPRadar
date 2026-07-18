"""
Analysis Runner Module.
Handles the construction of complex ClickHouse SQL queries from canonical run context,
and provides data-filtering utilities (Solar) before plotting.
"""

from contextlib import nullcontext
import pandas as pd
import numpy as np
from config import (
    BAND_MAP,
    MAX_DYNAMIC_RADIUS_KM,
)
from core.analysis_context import (
    COMPARISON_HARDWARE_AB,
    COMPARISON_LOCAL_NEIGHBORHOOD,
    COMPARISON_NONE,
    COMPARISON_REFERENCE_STATION,
    LOCAL_BENCHMARK_MEDIAN,
    SELF_TEST_RX,
    SELF_TEST_TX,
    solar_path_state,
)
from core.input_validation import is_valid_callsign
from core.math_utils import get_solar_state
from core.opportunity_engine import (
    ABSOLUTE_METHOD_VERSION,
    build_absolute_opportunity_query,
    opportunity_utc_from_time_slot,
    prepare_opportunity_rows,
)
from core.snr_utils import round_snr_like_columns
from core.tx_ab_schedule import (
    assign_tx_ab_pair_columns,
    tx_ab_schedule_sql,
    validate_tx_ab_schedule,
)


DECODE_FILTER_STRICT = "strict_code_1"
DECODE_FILTER_LEGACY = "legacy_no_code"
DECODE_CODE_PREDICATE = "code = 1"


class AnalysisConfigError(ValueError):
    """Raised when canonical run context cannot produce a valid analysis batch."""


def _timed_span(timing_collector, label, detail=""):
    """Return a timing context when profiling is active."""
    if timing_collector is None:
        return nullcontext()
    return timing_collector.span(label, detail=detail)


def _build_station_weighted_local_median_query(
    *,
    target_snr_expr,
    reference_snr_expr,
    target_sql,
    reference_sql,
    peer_sign_column,
    peer_grid_column,
    peer_lat_column,
    peer_lon_column,
    local_sign_column,
    local_grid_column,
    local_lat_column,
    local_lon_column,
    center_latitude,
    center_longitude,
):
    """Return Local Median SQL with one median contributor per local station/cycle/path."""
    reference_distance_expr = (
        f"geoDistance({center_longitude}, {center_latitude}, {local_lon_column}, {local_lat_column})"
    )
    return (
        "SELECT time_slot, peer_sign, peer_grid, "
        "any(peer_lat) AS peer_lat, any(peer_lon) AS peer_lon, "
        "maxIf(station_snr_norm, is_me = 1) AS snr_u_norm, "
        "quantileExactInclusiveIf(0.5)(station_snr_norm, is_me = 0) AS snr_r_norm, "
        "sumIf(raw_row_count, is_me = 1) AS has_u, countIf(is_me = 0) AS has_r, "
        "concat(toString(countIf(is_me = 0)), ' stations') AS best_ref_sign, "
        "quantileExactInclusiveIf(0.5)(local_dist, is_me = 0) AS best_ref_dist, "
        "groupArrayIf(tuple(local_sign, local_grid, local_dist, station_snr_norm), is_me = 0) AS ref_detail_rows "
        "FROM ("
        f"SELECT floor(toUnixTimestamp(time)/120) AS time_slot, {peer_sign_column} AS peer_sign, "
        f"{peer_grid_column} AS peer_grid, any({peer_lat_column}) AS peer_lat, "
        f"any({peer_lon_column}) AS peer_lon, {local_sign_column} AS local_sign, "
        f"{local_grid_column} AS local_grid, 0.0 AS local_dist, max({target_snr_expr}) AS station_snr_norm, "
        "count() AS raw_row_count, 1 AS is_me "
        f"FROM wspr.rx WHERE {target_sql} AND {peer_lat_column} != 0 "
        "GROUP BY time_slot, peer_sign, peer_grid, local_sign, local_grid "
        "UNION ALL "
        f"SELECT floor(toUnixTimestamp(time)/120) AS time_slot, {peer_sign_column} AS peer_sign, "
        f"{peer_grid_column} AS peer_grid, any({peer_lat_column}) AS peer_lat, "
        f"any({peer_lon_column}) AS peer_lon, {local_sign_column} AS local_sign, "
        f"{local_grid_column} AS local_grid, quantileExactInclusive(0.5)({reference_distance_expr}) AS local_dist, "
        f"quantileExactInclusive(0.5)({reference_snr_expr}) AS station_snr_norm, "
        "count() AS raw_row_count, 0 AS is_me "
        f"FROM wspr.rx WHERE {reference_sql} AND {peer_lat_column} != 0 "
        "GROUP BY time_slot, peer_sign, peer_grid, local_sign, local_grid"
        ") GROUP BY time_slot, peer_sign, peer_grid FORMAT CSVWithNames"
    )


def _build_tx_comparison_query(
    *,
    is_sequential,
    target_snr_expr,
    reference_snr_expr,
    target_sql,
    reference_sql,
    target_schedule_sql,
    reference_schedule_sql,
    local_reference_snr_sql,
    local_reference_sign_sql,
    local_reference_dist_sql,
    local_reference_detail_sql,
    center_latitude,
    center_longitude,
    station_weighted_reference_median=False,
):
    """Return the TX comparison SQL without performing any data access."""
    if is_sequential:
        return (
            "SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, "
            f"rx_lon AS peer_lon, snr, power, {target_snr_expr} AS stat_val, 1 AS is_me "
            f"FROM wspr.rx WHERE {target_sql} {target_schedule_sql} AND rx_lat != 0 "
            "UNION ALL "
            "SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, "
            f"rx_lon AS peer_lon, snr, power, {reference_snr_expr} AS stat_val, 0 AS is_me "
            f"FROM wspr.rx WHERE {reference_sql} {reference_schedule_sql} AND rx_lat != 0 "
            "FORMAT CSVWithNames"
        )

    if station_weighted_reference_median:
        return _build_station_weighted_local_median_query(
            target_snr_expr=target_snr_expr,
            reference_snr_expr=reference_snr_expr,
            target_sql=target_sql,
            reference_sql=reference_sql,
            peer_sign_column="rx_sign",
            peer_grid_column="rx_loc",
            peer_lat_column="rx_lat",
            peer_lon_column="rx_lon",
            local_sign_column="tx_sign",
            local_grid_column="tx_loc",
            local_lat_column="tx_lat",
            local_lon_column="tx_lon",
            center_latitude=center_latitude,
            center_longitude=center_longitude,
        )

    return (
        "SELECT floor(toUnixTimestamp(time)/120) AS time_slot, peer_sign, peer_grid, "
        "any(peer_lat) AS peer_lat, any(peer_lon) AS peer_lon, "
        f"maxIf(snr - power + 30, is_me = 1) AS snr_u_norm, {local_reference_snr_sql} AS snr_r_norm, "
        f"countIf(is_me = 1) AS has_u, countIf(is_me = 0) AS has_r, {local_reference_sign_sql} AS best_ref_sign, "
        f"{local_reference_dist_sql} AS best_ref_dist{local_reference_detail_sql} "
        "FROM ("
        "SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, "
        "rx_lon AS peer_lon, tx_sign AS local_sign, tx_loc AS local_grid, 0.0 AS local_dist, "
        f"snr, power, 1 AS is_me FROM wspr.rx WHERE {target_sql} AND rx_lat != 0 "
        "UNION ALL "
        "SELECT time, rx_sign AS peer_sign, rx_loc AS peer_grid, rx_lat AS peer_lat, "
        "rx_lon AS peer_lon, tx_sign AS local_sign, tx_loc AS local_grid, "
        f"geoDistance({center_longitude}, {center_latitude}, tx_lon, tx_lat) AS local_dist, "
        f"snr, power, 0 AS is_me FROM wspr.rx WHERE {reference_sql} AND rx_lat != 0"
        ") GROUP BY time_slot, peer_sign, peer_grid FORMAT CSVWithNames"
    )


def _build_rx_comparison_query(
    *,
    is_sequential,
    target_snr_expr,
    reference_snr_expr,
    target_sql,
    reference_sql,
    target_schedule_sql,
    reference_schedule_sql,
    local_reference_snr_sql,
    local_reference_sign_sql,
    local_reference_dist_sql,
    local_reference_detail_sql,
    center_latitude,
    center_longitude,
    station_weighted_reference_median=False,
):
    """Return the RX comparison SQL without performing any data access."""
    if is_sequential:
        return (
            "SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, "
            f"tx_lon AS peer_lon, snr, power, {target_snr_expr} AS stat_val, 1 AS is_me "
            f"FROM wspr.rx WHERE {target_sql} {target_schedule_sql} AND tx_lat != 0 "
            "UNION ALL "
            "SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, "
            f"tx_lon AS peer_lon, snr, power, {reference_snr_expr} AS stat_val, 0 AS is_me "
            f"FROM wspr.rx WHERE {reference_sql} {reference_schedule_sql} AND tx_lat != 0 "
            "FORMAT CSVWithNames"
        )

    if station_weighted_reference_median:
        return _build_station_weighted_local_median_query(
            target_snr_expr=target_snr_expr,
            reference_snr_expr=reference_snr_expr,
            target_sql=target_sql,
            reference_sql=reference_sql,
            peer_sign_column="tx_sign",
            peer_grid_column="tx_loc",
            peer_lat_column="tx_lat",
            peer_lon_column="tx_lon",
            local_sign_column="rx_sign",
            local_grid_column="rx_loc",
            local_lat_column="rx_lat",
            local_lon_column="rx_lon",
            center_latitude=center_latitude,
            center_longitude=center_longitude,
        )

    return (
        "SELECT floor(toUnixTimestamp(time)/120) AS time_slot, peer_sign, peer_grid, "
        "any(peer_lat) AS peer_lat, any(peer_lon) AS peer_lon, "
        f"maxIf(snr - power + 30, is_me = 1) AS snr_u_norm, {local_reference_snr_sql} AS snr_r_norm, "
        f"countIf(is_me = 1) AS has_u, countIf(is_me = 0) AS has_r, {local_reference_sign_sql} AS best_ref_sign, "
        f"{local_reference_dist_sql} AS best_ref_dist{local_reference_detail_sql} "
        "FROM ("
        "SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, "
        "tx_lon AS peer_lon, rx_sign AS local_sign, rx_loc AS local_grid, 0.0 AS local_dist, "
        f"snr, power, 1 AS is_me FROM wspr.rx WHERE {target_sql} AND tx_lat != 0 "
        "UNION ALL "
        "SELECT time, tx_sign AS peer_sign, tx_loc AS peer_grid, tx_lat AS peer_lat, "
        "tx_lon AS peer_lon, rx_sign AS local_sign, rx_loc AS local_grid, "
        f"geoDistance({center_longitude}, {center_latitude}, rx_lon, rx_lat) AS local_dist, "
        f"snr, power, 0 AS is_me FROM wspr.rx WHERE {reference_sql} AND tx_lat != 0"
        ") GROUP BY time_slot, peer_sign, peer_grid FORMAT CSVWithNames"
    )


def _decode_filter_sql(require_decode_code=True):
    return f" AND {DECODE_CODE_PREDICATE}" if require_decode_code else ""


def without_decode_code_filter(query):
    """Return a legacy-compatible query variant without the strict decode code predicate."""
    cleaned = str(query or "")
    for pattern in (
        "WHERE code = 1\n  AND ",
        "WHERE code = 1\n      AND ",
        "WHERE code = 1 AND ",
    ):
        cleaned = cleaned.replace(pattern, "WHERE ")
    for pattern in (
        "\n      AND code = 1",
        "\n  AND code = 1",
        " AND code = 1",
    ):
        cleaned = cleaned.replace(pattern, "")
    return cleaned


def with_decode_fallback(analysis):
    """Attach strict/legacy decode metadata and a no-code fallback query."""
    strict_query = analysis["query"]
    legacy_query = without_decode_code_filter(strict_query)
    analysis["decode_filter_mode"] = DECODE_FILTER_STRICT
    if legacy_query != strict_query:
        analysis["legacy_query"] = legacy_query
        analysis["legacy_decode_filter_mode"] = DECODE_FILTER_LEGACY
    return analysis


def has_target_evidence(df, analysis):
    """Return True when fetched data contains target-side evidence before UI filters."""
    if df is None or df.empty:
        return False

    if analysis.get("analysis_kind") == "opportunity":
        if "target_seen" not in df.columns:
            return False
        target_seen = pd.to_numeric(df["target_seen"], errors="coerce").fillna(0)
        return bool((target_seen > 0).any())

    if "has_u" in df.columns:
        has_target = pd.to_numeric(df["has_u"], errors="coerce").fillna(0)
        return bool((has_target > 0).any())
    if "is_me" in df.columns:
        is_target = pd.to_numeric(df["is_me"], errors="coerce").fillna(0)
        return bool((is_target > 0).any())

    return True


def should_retry_without_decode_filter(df, analysis):
    """Retry only when strict code=1 produced no target-side evidence."""
    return (
        analysis.get("decode_filter_mode") == DECODE_FILTER_STRICT
        and bool(analysis.get("legacy_query"))
        and not has_target_evidence(df, analysis)
    )


def build_analysis_batches(
    analysis_context,
    start_t,
    end_t,
    lat_0,
    lon_0,
    band_filter,
    presentation_context=None,
    warn=None,
):
    """Build direction-specific Success and optional Compare execution batches.

    Success-only returns one opportunity batch. A selected benchmark returns the
    comparison batch first and the target's separate Success batch second.
    Invalid callsigns, bands, or benchmark designs raise ``AnalysisConfigError``.
    """
    labels = presentation_context.labels if presentation_context is not None else {}

    def label(key, default):
        return str(labels.get(key, default))

    callsign = analysis_context.callsign.upper().strip()

    # Defense-in-depth: validate callsign before any SQL is assembled.
    if not is_valid_callsign(callsign):
        raise AnalysisConfigError(
            f"Invalid callsign '{callsign}'. Only A-Z, 0-9, and '/' are allowed (3-15 characters)."
        )
    if analysis_context.band not in BAND_MAP:
        raise AnalysisConfigError(
            f"Invalid operating band '{analysis_context.band}'. Choose one exact WSPR band."
        )

    comp_mode = analysis_context.comparison_mode
    time_filter = f"time BETWEEN '{start_t.strftime('%Y-%m-%d %H:%M:%S')}' AND '{end_t.strftime('%Y-%m-%d %H:%M:%S')}'"
    benchmark_offset_db = round(float(analysis_context.reference_snr_correction_db), 1)
    target_snr_expr = "(snr - power + 30)"
    benchmark_snr_expr = f"(snr - power + 30 + {benchmark_offset_db:.1f})"
    decode_filter_sql = _decode_filter_sql(require_decode_code=True)
    
    # Special callsign exclusion filter.
    # Hardcoded prefixes target special balloon telemetry callsigns without exposing raw SQL fragments through free text.
    if analysis_context.exclude_special_callsigns:
        for prefix in ["Q", "0", "1"]:
            time_filter += f" AND tx_sign NOT LIKE '{prefix}%' AND rx_sign NOT LIKE '{prefix}%'"
    
    is_sequential = False
    
    # Determine Reference / Buddy Parameters
    if comp_mode == COMPARISON_NONE:
        ref_callsign = None
    elif comp_mode == COMPARISON_LOCAL_NEIGHBORHOOD:
        ref_radius_km = min(analysis_context.neighborhood_radius_km, MAX_DYNAMIC_RADIUS_KM)
    elif comp_mode == COMPARISON_REFERENCE_STATION:
        ref_callsign = analysis_context.reference_callsign.upper().strip()
        if not is_valid_callsign(ref_callsign):
            raise AnalysisConfigError(
                f"Invalid reference callsign '{ref_callsign}'. Only A-Z, 0-9, and '/' are allowed (3-15 characters)."
            )
    elif comp_mode == COMPARISON_HARDWARE_AB:
        ref_callsign = callsign  # defaults to target callsign (already validated above)
        if analysis_context.self_test_mode == SELF_TEST_TX:
            is_sequential = True
        elif analysis_context.self_test_mode == SELF_TEST_RX:
            ref_callsign = analysis_context.setup_b_callsign.upper().strip()
            if not is_valid_callsign(ref_callsign):
                raise AnalysisConfigError(
                    f"Invalid Setup B callsign '{ref_callsign}'. Only A-Z, 0-9, and '/' are allowed (3-15 characters)."
                )
    else:
        raise AnalysisConfigError(f"Unknown benchmark design '{comp_mode}'.")

    target_schedule_sql = ""
    reference_schedule_sql = ""
    if is_sequential:
        try:
            validate_tx_ab_schedule(
                analysis_context.tx_ab_repeat_interval_minutes,
                analysis_context.tx_ab_target_start_minute,
                analysis_context.tx_ab_reference_start_minute,
            )
        except ValueError as exc:
            raise AnalysisConfigError(f"Invalid TX A/B schedule: {exc}") from exc
        target_schedule_sql = "AND " + tx_ab_schedule_sql(
            analysis_context.tx_ab_repeat_interval_minutes,
            analysis_context.tx_ab_target_start_minute,
        )
        reference_schedule_sql = "AND " + tx_ab_schedule_sql(
            analysis_context.tx_ab_repeat_interval_minutes,
            analysis_context.tx_ab_reference_start_minute,
        )
        
    # Target SQL filters use one exact callsign; suffix callsigns are selected by entering that exact callsign.
    tx_target_sql = f"tx_sign = '{callsign}' {band_filter} AND {time_filter}{decode_filter_sql}"
    rx_target_sql = f"rx_sign = '{callsign}' {band_filter} AND {time_filter}{decode_filter_sql}"

    # Cycle synchronization is applied after fetching in apply_post_fetch_filters().
    # Keeping it outside SQL construction avoids query-builder data access.

    # Peer SQL Filters
    if comp_mode == COMPARISON_NONE:
        tx_peer_sql = None
        rx_peer_sql = None
        display_callsign = callsign
        comp_title = ""
    elif comp_mode == COMPARISON_LOCAL_NEIGHBORHOOD:
        ref_radius_km = min(analysis_context.neighborhood_radius_km, MAX_DYNAMIC_RADIUS_KM)
        local_benchmark = analysis_context.local_benchmark
        is_local_median = local_benchmark == LOCAL_BENCHMARK_MEDIAN
        max_rad = ref_radius_km * 1000
        
        # Prefilter with a bounding box so geoDistance is only evaluated nearby.
        lat_diff = ref_radius_km / 111.0
        lon_diff = ref_radius_km / (111.0 * max(abs(np.cos(np.radians(lat_0))), 0.01))
        
        bbox_tx = f"AND tx_lat BETWEEN {lat_0 - lat_diff} AND {lat_0 + lat_diff} AND tx_lon BETWEEN {lon_0 - lon_diff} AND {lon_0 + lon_diff}"
        bbox_rx = f"AND rx_lat BETWEEN {lat_0 - lat_diff} AND {lat_0 + lat_diff} AND rx_lon BETWEEN {lon_0 - lon_diff} AND {lon_0 + lon_diff}"
        
        tx_peer_sql = f"tx_sign != '{callsign}' {band_filter} AND {time_filter}{decode_filter_sql} {bbox_tx} AND tx_lat != 0 AND tx_lon != 0 AND geoDistance({lon_0}, {lat_0}, tx_lon, tx_lat) <= {max_rad}"
        
        rx_peer_sql = f"rx_sign != '{callsign}' {band_filter} AND {time_filter}{decode_filter_sql} {bbox_rx} AND rx_lat != 0 AND rx_lon != 0 AND geoDistance({lon_0}, {lat_0}, rx_lon, rx_lat) <= {max_rad}"
        
        if is_local_median:
            comp_title = label(
                "comp_title_local_median",
                "Local Median Neighborhood (<= {radius} km)",
            ).format(radius=ref_radius_km)
        else:
            comp_title = label(
                "comp_title_local_best",
                "Local Best Station (<= {radius} km)",
            ).format(radius=ref_radius_km)
        display_callsign = callsign
    else:
        tx_peer_sql = f"tx_sign = '{ref_callsign}' {band_filter} AND {time_filter}{decode_filter_sql}"
        rx_peer_sql = f"rx_sign = '{ref_callsign}' {band_filter} AND {time_filter}{decode_filter_sql}"
            
        if comp_mode == COMPARISON_HARDWARE_AB:
            if analysis_context.self_test_mode == SELF_TEST_RX:
                display_callsign = f"{callsign} (Setup A)"
                comp_title = f"{ref_callsign} (Setup B)"
            else:
                display_callsign = f"{callsign} (Setup A)"
                comp_title = f"{callsign} (Setup B)"
        else:
            display_callsign = callsign
            comp_title = label(
                "comp_title_ref",
                "{callsign} (Reference)",
            ).format(callsign=ref_callsign)

    # Assemble Analysis Batches
    analyses = []
    local_ref_snr_sql = f"maxIf({benchmark_snr_expr}, is_me = 0)"
    local_ref_sign_sql = f"argMaxIf(local_sign, {benchmark_snr_expr}, is_me = 0)"
    local_ref_dist_sql = f"argMaxIf(local_dist, {benchmark_snr_expr}, is_me = 0)"
    local_ref_detail_sql = ""
    station_weighted_reference_median = False
    if comp_mode == COMPARISON_LOCAL_NEIGHBORHOOD and analysis_context.local_benchmark == LOCAL_BENCHMARK_MEDIAN:
        station_weighted_reference_median = True
        local_ref_snr_sql = f"quantileExactInclusiveIf(0.5)({benchmark_snr_expr}, is_me = 0)"
        local_ref_sign_sql = "concat(toString(countIf(is_me = 0)), ' stations')"
        local_ref_dist_sql = "quantileExactInclusiveIf(0.5)(local_dist, is_me = 0)"
        local_ref_detail_sql = f", groupArrayIf(tuple(local_sign, local_grid, local_dist, {benchmark_snr_expr}), is_me = 0) AS ref_detail_rows"
    
    if analysis_context.run_mode == "TX":
        if comp_mode != COMPARISON_NONE:
            tx_comp_query = _build_tx_comparison_query(
                is_sequential=is_sequential,
                target_snr_expr=target_snr_expr,
                reference_snr_expr=benchmark_snr_expr,
                target_sql=tx_target_sql,
                reference_sql=tx_peer_sql,
                target_schedule_sql=target_schedule_sql,
                reference_schedule_sql=reference_schedule_sql,
                local_reference_snr_sql=local_ref_snr_sql,
                local_reference_sign_sql=local_ref_sign_sql,
                local_reference_dist_sql=local_ref_dist_sql,
                local_reference_detail_sql=local_ref_detail_sql,
                center_latitude=lat_0,
                center_longitude=lon_0,
                station_weighted_reference_median=station_weighted_reference_median,
            )
            analyses.append(with_decode_fallback({
                "id": "TX_COMP",
                "title": label(
                    "fig_tx_comp",
                    "TX Compare: {callsign} (Target) vs. {comp_title}",
                ).format(callsign=display_callsign, comp_title=comp_title),
                "is_compare": True,
                "is_sequential": is_sequential,
                "analysis_kind": "comparison",
                "response_format": "csv",
                "query": tx_comp_query,
                "analysis_start_utc": start_t,
                "analysis_end_utc": end_t,
            }))
        analyses.append(with_decode_fallback({
            "id": "TX_ABS",
            "title": label(
                "fig_tx_abs",
                "TX Success: Target {callsign} vs. Other Signals at Active RX Stations",
            ).format(callsign=callsign),
            "is_compare": False,
            "is_sequential": False,
            "analysis_kind": "opportunity",
            "absolute_mode": "TX",
            "absolute_method_version": ABSOLUTE_METHOD_VERSION,
            "response_format": "parquet",
            "query": build_absolute_opportunity_query(
                mode="TX",
                start_t=start_t,
                end_t=end_t,
                band_value=BAND_MAP[analysis_context.band],
                callsign=callsign,
                qth=analysis_context.qth,
                exclude_special_callsigns=analysis_context.exclude_special_callsigns,
                target_repeat_interval_minutes=(
                    analysis_context.tx_ab_repeat_interval_minutes
                    if is_sequential
                    else None
                ),
                target_start_minute_utc=(
                    analysis_context.tx_ab_target_start_minute
                    if is_sequential
                    else None
                ),
                require_decode_code=True,
            ),
        }))

    elif analysis_context.run_mode == "RX":
        if comp_mode != COMPARISON_NONE:
            rx_comp_query = _build_rx_comparison_query(
                is_sequential=is_sequential,
                target_snr_expr=target_snr_expr,
                reference_snr_expr=benchmark_snr_expr,
                target_sql=rx_target_sql,
                reference_sql=rx_peer_sql,
                target_schedule_sql=target_schedule_sql,
                reference_schedule_sql=reference_schedule_sql,
                local_reference_snr_sql=local_ref_snr_sql,
                local_reference_sign_sql=local_ref_sign_sql,
                local_reference_dist_sql=local_ref_dist_sql,
                local_reference_detail_sql=local_ref_detail_sql,
                center_latitude=lat_0,
                center_longitude=lon_0,
                station_weighted_reference_median=station_weighted_reference_median,
            )
            analyses.append(with_decode_fallback({
                "id": "RX_COMP",
                "title": label(
                    "fig_rx_comp",
                    "RX Compare: {callsign} (Target) vs. {comp_title}",
                ).format(callsign=display_callsign, comp_title=comp_title),
                "is_compare": True,
                "is_sequential": is_sequential,
                "analysis_kind": "comparison",
                "response_format": "csv",
                "query": rx_comp_query,
                "analysis_start_utc": start_t,
                "analysis_end_utc": end_t,
            }))
        analyses.append(with_decode_fallback({
            "id": "RX_ABS",
            "title": label(
                "fig_rx_abs",
                "RX Success: Target {callsign} vs. Same Signals Heard Elsewhere",
            ).format(callsign=callsign),
            "is_compare": False,
            "is_sequential": False,
            "analysis_kind": "opportunity",
            "absolute_mode": "RX",
            "absolute_method_version": ABSOLUTE_METHOD_VERSION,
            "response_format": "parquet",
            "query": build_absolute_opportunity_query(
                mode="RX",
                start_t=start_t,
                end_t=end_t,
                band_value=BAND_MAP[analysis_context.band],
                callsign=callsign,
                qth=analysis_context.qth,
                exclude_special_callsigns=analysis_context.exclude_special_callsigns,
                require_decode_code=True,
            ),
        }))

    return analyses

def apply_post_fetch_filters(df, analysis, analysis_context, lat_0, lon_0, t, timing_collector=None):
    """
    Applies mathematical and logical filters (Solar, Cycle-Sync, Moving Stations) 
    to the fetched dataframe before it is handed over to the plotting engine.
    """
    if analysis.get("analysis_kind") == "opportunity":
        with _timed_span(timing_collector, "opportunity prepare rows"):
            df = prepare_opportunity_rows(
                df,
                target_callsign=analysis_context.callsign,
                target_qth=analysis_context.qth,
                timing_collector=timing_collector,
                owns_input=True,
            )
        if df.empty:
            return df, t["warn_no_data"].format(title=analysis["title"])

        target_state = solar_path_state(analysis_context.solar_state)
        if target_state is not None:
            with _timed_span(timing_collector, "opportunity solar filter"):
                df["solar"] = opportunity_utc_from_time_slot(df["time_slot"]).apply(
                    lambda dt: get_solar_state(dt, lat_0, lon_0)
                )
                df = df[df["solar"] == target_state]

        if analysis_context.exclude_moving_stations and not df.empty:
            with _timed_span(timing_collector, "opportunity moving-station filter"):
                grid4 = df["peer_grid"].astype(str).str[:4]
                static_peers = (
                    df.assign(g4=grid4)
                    .groupby("peer_sign", observed=True)["g4"]
                    .nunique()
                    .loc[lambda values: values == 1]
                    .index
                )
                df = df[df["peer_sign"].isin(static_peers)]

        if df.empty:
            return df, t["warn_no_data"].format(title=analysis["title"])
        with _timed_span(timing_collector, "opportunity filtered reset"):
            return df.reset_index(drop=True), None

    if analysis.get("is_compare") and analysis.get("is_sequential"):
        with _timed_span(timing_collector, "TX A/B scheduled pair assignment"):
            df = assign_tx_ab_pair_columns(
                df,
                repeat_interval_minutes=(
                    analysis_context.tx_ab_repeat_interval_minutes
                ),
                target_start_minute_utc=(
                    analysis_context.tx_ab_target_start_minute
                ),
                reference_start_minute_utc=(
                    analysis_context.tx_ab_reference_start_minute
                ),
                start_time=analysis.get("analysis_start_utc"),
                end_time=analysis.get("analysis_end_utc"),
                exclude_boundary_pairs=True,
            )

    # 1. Solar filtering
    target_state = solar_path_state(analysis_context.solar_state)
    if target_state is not None:
        with _timed_span(timing_collector, "comparison solar filter"):
            if analysis['is_compare'] and not analysis['is_sequential']:
                df['dt_time'] = pd.to_datetime(df['time_slot'] * 120, unit='s')
            elif (
                analysis.get('is_sequential')
                and {
                    'tx_ab_pair_target_time',
                    'tx_ab_pair_reference_time',
                }.issubset(df.columns)
            ):
                target_pair_time = pd.to_datetime(
                    df['tx_ab_pair_target_time'],
                    utc=True,
                )
                reference_pair_time = pd.to_datetime(
                    df['tx_ab_pair_reference_time'],
                    utc=True,
                )
                df['dt_time'] = target_pair_time + (
                    (reference_pair_time - target_pair_time) / 2
                )
            else:
                df['dt_time'] = pd.to_datetime(df['time'])

            df['solar'] = df['dt_time'].apply(lambda dt: get_solar_state(dt, lat_0, lon_0))
            df = df[df['solar'] == target_state]

    # 2. Exclude moving stations.
    # Removes peers reporting more than one four-character grid during the selected period.
    if analysis_context.exclude_moving_stations and not df.empty and 'peer_grid' in df.columns:
        with _timed_span(timing_collector, "comparison moving-station filter"):
            # Use the first four characters so JN37 and JN37AB are treated as the same grid.
            grid4 = df['peer_grid'].astype(str).str[:4]
            # Keep only stations with exactly one unique four-character grid.
            static_peers = df.assign(g4=grid4).groupby('peer_sign', observed=True)['g4'].nunique()[lambda x: x == 1].index
            df = df[df['peer_sign'].isin(static_peers)]

    
    # 3. Vectorized cycle synchronization (RX and TX).
    # A cycle is counted only when Setup A was demonstrably active.
    # TX: the transmitter must have sent in this cycle.
    # RX: the receiver must have heard at least one station in this cycle.
    if analysis['is_compare'] and not analysis['is_sequential'] and 'has_u' in df.columns:
        with _timed_span(timing_collector, "comparison cycle synchronization"):
            active_slots = df[df['has_u'] > 0]['time_slot'].unique()
            df = df[df['time_slot'].isin(active_slots)]
    
    # Alternative cycle synchronization (strictly TX only).
    # In RX comparison, zero spots may represent a deaf antenna, so the cycle can be evidence.
    # In TX comparison, zero spots may mean no transmission, so dropping the cycle can be fairer.
    #is_tx = analysis['id'].startswith("TX")
    #if analysis['is_compare'] and not analysis['is_sequential'] and is_tx and 'has_u' in df.columns:
        #active_slots = df[df['has_u'] > 0]['time_slot'].unique()
        #df = df[df['time_slot'].isin(active_slots)]

    if df.empty:
        return df, t["warn_no_data"].format(title=analysis['title'])

    with _timed_span(timing_collector, "comparison SNR rounding"):
        df = round_snr_like_columns(df)
    return df, None
