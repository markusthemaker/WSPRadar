"""Regression coverage for exact-distance and temporal Success evidence."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import to_hex

from core.opportunity_engine import opportunity_utc_from_time_slot
from core.presentation_context import PresentationContext
from i18n import T
from ui.components.segment_inspector import (
    _opportunity_export_station_rows,
    _selected_success_context_line,
    _selected_success_temporal_figure_title,
    _success_figure_labels,
    _success_temporal_figure_title,
)
from ui.inspector.view_models import build_opportunity_inspector_view_model
from ui.matplotlib_renderer import dispose_matplotlib_figure
from ui.plots.evidence_figures import (
    _segment_temporal_evidence_export_recipe,
    render_segment_temporal_evidence_export_figure,
    render_segment_temporal_snr_export_figure,
)
from ui.plots.opportunity_figures import (
    SUCCESS_DISTANCE_BINNING_VERSION,
    SUCCESS_MINIMUM_SNR_BASELINE_OBSERVATIONS,
    SUCCESS_SNR_REPRESENTATION_ACTUAL,
    SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE,
    SUCCESS_SNR_BASELINE_VERSION,
    SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE,
    SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
    SUCCESS_TEMPORAL_TIME_BINS,
    _aggregate_success_distance_profile,
    _assign_success_distance_bins,
    _format_ham_compact_count,
    _opportunity_segment_recipe,
    _opportunity_temporal_recipe,
    _prepare_success_snr_anomalies,
    _render_opportunity_segment_figure,
    _success_distance_panel_title,
    _success_distance_bin_definition,
    _success_distance_bin_width_km,
    _success_relative_density_grid,
    _success_temporal_rate_axis_max,
)


def _time_slot(timestamp_utc: str) -> int:
    """Return the canonical integer 120-second WSPR slot for one UTC instant."""
    timestamp = pd.Timestamp(timestamp_utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    else:
        timestamp = timestamp.tz_convert("UTC")
    return int(timestamp.timestamp() // 120)


def _peer(
    peer_sign: str,
    distance_km: float,
    *,
    hits: int,
    misses: int,
    successful_snr_median: float = np.nan,
    eligible: bool = True,
) -> dict[str, object]:
    """Return one map-station row with exact Success evidence and geometry."""
    opportunities = hits + misses
    coarse_lower_km = float(np.floor(distance_km / 2500.0) * 2500.0)
    coarse_upper_km = coarse_lower_km + 2500.0
    return {
        "peer_sign": peer_sign,
        "peer_grid": f"{peer_sign[:2]:0<2}00",
        "dist_label": (
            f"[{int(coarse_lower_km)}-{int(coarse_upper_km)}km]"
        ),
        "r_min": coarse_lower_km,
        "r_max": coarse_upper_km,
        "calc_dist": float(distance_km),
        "calc_azimuth": 0.0,
        "eligible": bool(eligible),
        "hits": int(hits),
        "misses": int(misses),
        "opportunities": int(opportunities),
        "rate_pct": (
            100.0 * hits / opportunities
            if opportunities
            else np.nan
        ),
        "successful_snr_median": successful_snr_median,
    }


def _summary_peer_rows() -> pd.DataFrame:
    """Return qualifying peers with unequal evidence depth and one ineligible peer."""
    return pd.DataFrame(
        [
            _peer("A", 900.0, hits=0, misses=5),
            _peer("B", 1800.0, hits=1, misses=1, successful_snr_median=-18.0),
            _peer("C", 3200.0, hits=4, misses=0, successful_snr_median=-12.0),
            _peer("D", 4400.0, hits=1, misses=3, successful_snr_median=-16.0),
            _peer("E", 7200.0, hits=0, misses=0, eligible=False),
        ]
    )


def _summary_evidence_rows() -> pd.DataFrame:
    """Return row-level outcomes matching the scoped summary aggregates."""
    records = []
    for peer in _summary_peer_rows().itertuples(index=False):
        for _ in range(int(peer.hits)):
            records.append(
                {
                    "peer_sign": peer.peer_sign,
                    "peer_grid": peer.peer_grid,
                    "hit": 1,
                    "miss": 0,
                }
            )
        for _ in range(int(peer.misses)):
            records.append(
                {
                    "peer_sign": peer.peer_sign,
                    "peer_grid": peer.peer_grid,
                    "hit": 0,
                    "miss": 1,
                }
            )
    return pd.DataFrame.from_records(records)


def _temporal_peer_rows() -> pd.DataFrame:
    """Return three qualifying stations and one excluded station."""
    return pd.DataFrame(
        [
            _peer("A", 100.0, hits=4, misses=1, successful_snr_median=-5.0),
            _peer("B", 200.0, hits=3, misses=0, successful_snr_median=0.0),
            _peer("C", 300.0, hits=2, misses=2, successful_snr_median=0.0),
            _peer(
                "D",
                400.0,
                hits=1,
                misses=0,
                successful_snr_median=100.0,
                eligible=False,
            ),
        ]
    )


def _temporal_evidence_rows() -> pd.DataFrame:
    """Return two confirmed UTC dates plus excluded and Target-only audit rows."""
    records: list[dict[str, object]] = []

    def add(
        peer_sign: str,
        timestamp_utc: str,
        *,
        hit: int = 0,
        miss: int = 0,
        target_snr: float = np.nan,
    ) -> None:
        peer_grid = _temporal_peer_rows().set_index("peer_sign").loc[
            peer_sign,
            "peer_grid",
        ]
        records.append(
            {
                "time_slot": _time_slot(timestamp_utc),
                "peer_sign": peer_sign,
                "peer_grid": peer_grid,
                "hit": hit,
                "miss": miss,
                "target_snr": target_snr,
            }
        )

    # A: four successful values, baseline -5 dB. Its two values in each
    # date/hour must collapse to one station-bin or station-date-hour median.
    add("A", "2026-07-10T00:00:00Z", hit=1, target_snr=-20.0)
    add("A", "2026-07-10T00:10:00Z", hit=1, target_snr=-10.0)
    add("A", "2026-07-10T01:00:00Z", miss=1)
    add("A", "2026-07-11T00:00:00Z", hit=1, target_snr=0.0)
    add("A", "2026-07-11T00:10:00Z", hit=1, target_snr=10.0)

    # B: three successful values, baseline 0 dB. Its first-hour median anomaly
    # equals A's first-hour median so density normalization has a 2:1 cell ratio.
    add("B", "2026-07-10T00:20:00Z", hit=1, target_snr=-20.0)
    add("B", "2026-07-10T00:30:00Z", hit=1, target_snr=0.0)
    add("B", "2026-07-10T01:10:00Z", hit=1, target_snr=20.0)

    # C has only two successful SNR observations. It remains in Success Rate
    # and support but is excluded only from the station-centered SNR layers.
    add("C", "2026-07-10T00:40:00Z", hit=1, target_snr=-5.0)
    add("C", "2026-07-11T00:40:00Z", hit=1, target_snr=5.0)
    add("C", "2026-07-10T02:00:00Z", miss=1)
    add("C", "2026-07-11T02:00:00Z", miss=1)

    # D is not a qualifying station and must not enter any segment layer.
    add("D", "2026-07-10T00:50:00Z", hit=1, target_snr=100.0)

    # This audit-only row must not create a third represented evidence date.
    add("A", "2026-07-12T02:00:00Z", target_snr=-3.0)
    return pd.DataFrame.from_records(records)


def _selected_actual_snr_evidence_rows() -> pd.DataFrame:
    """Return one selected path with unequal report depth across two UTC dates."""
    peer_grid = _peer("SEL", 1173.0, hits=4, misses=3)["peer_grid"]
    records = []

    def add(
        timestamp_utc: str,
        *,
        hit: int = 0,
        miss: int = 0,
        target_snr: float = np.nan,
    ) -> None:
        """Append one retained selected-station opportunity row."""
        records.append(
            {
                "time_slot": _time_slot(timestamp_utc),
                "peer_sign": "SEL",
                "peer_grid": peer_grid,
                "hit": hit,
                "miss": miss,
                "target_snr": target_snr,
            }
        )

    # Date 1 contributes three raw SNR observations to one chronological bin.
    # Its date-hour median is -30 dB, while its raw-observation median is also
    # -30 dB and the second occupied density cell proves the rows were not
    # collapsed to one station-bin value.
    add("2026-07-10T00:00:00Z", hit=1, target_snr=-30.0)
    add("2026-07-10T00:10:00Z", hit=1, target_snr=-30.0)
    add("2026-07-10T00:20:00Z", hit=1, target_snr=0.0)
    add("2026-07-10T00:30:00Z", miss=1)
    add("2026-07-10T01:00:00Z", miss=1)

    # Date 2 contributes only one successful report at hour 00. Equal-date
    # folding must therefore summarize [-30, +10] rather than the four raw rows.
    add("2026-07-11T00:00:00Z", hit=1, target_snr=10.0)
    add("2026-07-11T00:30:00Z", miss=1)
    return pd.DataFrame.from_records(records)


def _station_vote_contract_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return complete-run peers and rows exercising every station-vote case."""
    peers = pd.DataFrame(
        [
            _peer("ALLSUCCESS", 100.0, hits=5, misses=0),
            _peer("ALLCOUNTER", 200.0, hits=0, misses=5),
            _peer("MIXED", 300.0, hits=2, misses=3),
            _peer("PROLIFIC", 400.0, hits=5, misses=15),
            _peer("SPARSE", 500.0, hits=5, misses=0),
            _peer("NOBIN", 600.0, hits=5, misses=0),
            _peer(
                "INELIGIBLE",
                700.0,
                hits=20,
                misses=0,
                eligible=False,
            ),
        ]
    )
    peer_grids = peers.set_index("peer_sign")["peer_grid"].to_dict()
    records: list[dict[str, object]] = []

    def add_outcomes(
        peer_sign: str,
        start_utc: str,
        *,
        hits: int,
        misses: int,
    ) -> None:
        """Append distinct two-minute opportunity rows for one station."""
        start = pd.Timestamp(start_utc)
        outcomes = ([1] * int(hits)) + ([0] * int(misses))
        for index, is_hit in enumerate(outcomes):
            records.append(
                {
                    "time_slot": _time_slot(
                        str(start + pd.Timedelta(minutes=2 * index))
                    ),
                    "peer_sign": peer_sign,
                    "peer_grid": peer_grids[peer_sign],
                    "hit": int(is_hit),
                    "miss": int(not is_hit),
                    "target_snr": np.nan,
                }
            )

    # The first hour contains an all-success, all-counter, mixed, prolific,
    # and sparse station. NOBIN has no opportunity there. SPARSE nevertheless
    # qualifies over the complete run and must not be requalified per bin.
    add_outcomes("ALLSUCCESS", "2026-07-10T00:00:00Z", hits=2, misses=0)
    add_outcomes("ALLCOUNTER", "2026-07-10T00:00:00Z", hits=0, misses=2)
    add_outcomes("MIXED", "2026-07-10T00:00:00Z", hits=1, misses=3)
    add_outcomes("PROLIFIC", "2026-07-10T00:00:00Z", hits=5, misses=15)
    add_outcomes("SPARSE", "2026-07-10T00:00:00Z", hits=1, misses=0)
    add_outcomes("INELIGIBLE", "2026-07-10T00:00:00Z", hits=10, misses=0)

    add_outcomes("ALLSUCCESS", "2026-07-10T01:00:00Z", hits=3, misses=0)
    add_outcomes("ALLCOUNTER", "2026-07-10T01:00:00Z", hits=0, misses=3)
    add_outcomes("MIXED", "2026-07-10T01:00:00Z", hits=1, misses=0)
    add_outcomes("SPARSE", "2026-07-10T01:00:00Z", hits=4, misses=0)
    add_outcomes("NOBIN", "2026-07-10T01:00:00Z", hits=5, misses=0)
    add_outcomes("INELIGIBLE", "2026-07-10T01:00:00Z", hits=10, misses=0)
    return peers, pd.DataFrame.from_records(records)


def _presentation(language: str = "en") -> PresentationContext:
    """Return one presentation context without changing scientific inputs."""
    return PresentationContext(
        language=language,
        labels=T[language],
        theme="dark",
        solar_label="All" if language == "en" else "Alle",
    )


def _figure_labels(
    language: str = "en",
    analysis_id: str = "RX_ABS",
) -> dict[str, str]:
    """Return the public component-to-recipe localization contract."""
    return _success_figure_labels(T[language], analysis_id)


def _temporal_recipe_for_test(
    language: str = "en",
    analysis_id: str = "RX_ABS",
    *,
    rows: pd.DataFrame | None = None,
    start_t: str = "2026-07-10T00:00:00Z",
    end_t: str = "2026-07-13T00:00:00Z",
) -> dict[str, object]:
    """Build one complete localized Success temporal recipe."""
    evidence_title = _success_temporal_figure_title(
        "G3ZIL",
        analysis_id,
        T[language],
        figure_kind="evidence",
    )
    snr_title = _success_temporal_figure_title(
        "G3ZIL",
        analysis_id,
        T[language],
        figure_kind="snr",
    )
    return _opportunity_temporal_recipe(
        evidence_title,
        "Full Range | All Directions",
        _temporal_peer_rows(),
        _temporal_evidence_rows() if rows is None else rows,
        pd.Timestamp(start_t),
        pd.Timestamp(end_t),
        _presentation(language).absolute_terms(
            "TX" if analysis_id.startswith("TX") else "RX"
        ),
        figure_labels=_figure_labels(language, analysis_id),
        snr_title=snr_title,
    )


def _selected_actual_snr_recipe_for_test(
    rows: pd.DataFrame | None = None,
) -> dict[str, object]:
    """Build a schema-7 temporal recipe for one exact selected station."""
    selected_rows = (
        _selected_actual_snr_evidence_rows()
        if rows is None
        else rows.copy()
    )
    successful_count = int(
        pd.to_numeric(selected_rows["hit"], errors="coerce").fillna(0).sum()
    )
    counter_count = int(
        pd.to_numeric(selected_rows["miss"], errors="coerce").fillna(0).sum()
    )
    successful_snr = pd.to_numeric(
        selected_rows.loc[
            pd.to_numeric(
                selected_rows["hit"],
                errors="coerce",
            ).fillna(0)
            > 0,
            "target_snr",
        ],
        errors="coerce",
    ).dropna()
    selected_peer = _peer(
        "SEL",
        1173.0,
        hits=successful_count,
        misses=counter_count,
        successful_snr_median=(
            float(successful_snr.median())
            if not successful_snr.empty
            else np.nan
        ),
    )
    selected_peer["calc_azimuth"] = 91.0
    selected_peer["dir_name"] = "E"
    return _opportunity_temporal_recipe(
        "RX Success Selected Station Temporal Evidence: SEL (SE00)",
        "",
        pd.DataFrame([selected_peer]),
        selected_rows,
        pd.Timestamp("2026-07-10T00:00:00Z"),
        pd.Timestamp("2026-07-12T00:00:00Z"),
        _presentation().absolute_terms("RX"),
        figure_labels=_figure_labels(),
        snr_title="RX Success Selected Station SNR Evidence: SEL (SE00)",
        population_mode=SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION,
        snr_representation=SUCCESS_SNR_REPRESENTATION_ACTUAL,
    )


def _station_vote_recipe_for_test(
    peer_rows: pd.DataFrame,
    evidence_rows: pd.DataFrame,
) -> dict[str, object]:
    """Build a two-hour recipe for exact station-vote contract assertions."""
    return _opportunity_temporal_recipe(
        "RX Success Temporal Evidence",
        "Full Range | All Directions",
        peer_rows,
        evidence_rows,
        pd.Timestamp("2026-07-10T00:00:00Z"),
        pd.Timestamp("2026-07-10T02:00:00Z"),
        _presentation().absolute_terms("RX"),
        figure_labels=_figure_labels(),
    )


def _compare_temporal_recipe_for_test() -> dict[str, object]:
    """Build a two-date Compare recipe as the shared layout reference."""
    compare_rows = pd.DataFrame(
        {
            "plot_time": pd.to_datetime(
                [
                    "2026-07-10T00:05:00Z",
                    "2026-07-10T03:05:00Z",
                    "2026-07-11T00:05:00Z",
                ],
                utc=True,
            ),
            "metric": [-1.0, 1.0, 0.0],
        }
    )
    return _segment_temporal_evidence_export_recipe(
        compare_rows,
        "RX Compare Temporal Evidence",
        "1h",
        "Joint spot count",
    )


_SUCCESS_COMMON_FIGURE_LABELS = {
    "en": {
        "distance_x": "Distance from Target QTH (km)",
        "rate_y": "Success Rate (%)",
        "snr_y": (
            "Station-median successful Target SNR (dB @ 30 dBm)"
        ),
        "confirmed_opportunities": "Confirmed opportunities",
        "qualifying_stations": "Qualifying stations",
        "successful_snr_stations": "Stations with successful SNR",
        "station_balanced": "Station-balanced",
        "observation_level": "Observation-level",
        "median": "Median",
        "iqr": "IQR",
        "two_station_range": "Range (2 stations)",
        "evidence_chronological_title": (
            "Evidence over Time ({time_bin} bins)"
        ),
        "evidence_utc_hour_title": "Evidence by UTC Hour (1 h bins)",
        "station_support_folded_subtitle": (
            "Average contributing station presences per represented UTC date"
        ),
        "opportunity_folded_subtitle": (
            "Average confirmed opportunities per represented UTC date"
        ),
        "opportunity_y": "Opportunities",
        "opportunity_folded_y": "Opportunities",
        "rate_legend": "Success Rate",
        "time_x": "Date/Time (UTC)",
        "utc_hour_x": "UTC hour",
        "snr_density": (
            "Relative density of station-level SNR deviations"
        ),
        "station_baseline": "Each station’s run median (0 dB)",
        "bin_median_chronological": "Median across stations",
        "bin_median_folded": "Median across stations and dates",
        "selected_snr_y": "Normalized Target SNR (dB @ 30 dBm)",
        "snr_anomaly_unavailable": (
            "Successful-SNR anomaly unavailable — requires at least 3 "
            "successful Target SNR observations per station."
        ),
        "temporal_unavailable": (
            "UTC-hour pattern unavailable — requires evidence from at "
            "least 2 UTC dates."
        ),
        "utc_dates_folded": "{count} UTC dates folded",
    },
    "de": {
        "distance_x": "Entfernung vom Target-QTH (km)",
        "rate_y": "Success Rate (%)",
        "snr_y": (
            "Stationsmedian des erfolgreichen Target-SNR (dB @ 30 dBm)"
        ),
        "confirmed_opportunities": "Bestätigte Gelegenheiten",
        "qualifying_stations": "Qualifizierende Stationen",
        "successful_snr_stations": "Stationen mit erfolgreichem SNR",
        "station_balanced": "Stationsgleichgewichtet",
        "observation_level": "Beobachtungsebene",
        "median": "Median",
        "iqr": "IQR",
        "two_station_range": "Spanne (2 Stationen)",
        "evidence_chronological_title": (
            "Evidenz im Zeitverlauf ({time_bin}-Bins)"
        ),
        "evidence_utc_hour_title": (
            "Evidenz nach UTC-Stunde (1-h-Bins)"
        ),
        "station_support_folded_subtitle": (
            "Durchschnittliche Stationspräsenzen pro "
            "berücksichtigtem UTC-Tag"
        ),
        "opportunity_folded_subtitle": (
            "Durchschnittliche bestätigte Gelegenheiten pro "
            "berücksichtigtem UTC-Tag"
        ),
        "opportunity_y": "Gelegenheiten",
        "opportunity_folded_y": "Gelegenheiten",
        "rate_legend": "Success Rate",
        "time_x": "Datum/Uhrzeit (UTC)",
        "utc_hour_x": "UTC-Stunde",
        "snr_density": (
            "Relative Dichte stationsbezogener SNR-Abweichungen"
        ),
        "station_baseline": "Laufmedian jeder Station (0 dB)",
        "bin_median_chronological": "Median über Stationen",
        "bin_median_folded": "Median über Stationen und Tage",
        "selected_snr_y": "Normiertes Target-SNR (dB @ 30 dBm)",
        "snr_anomaly_unavailable": (
            "SNR-Anomalie nicht verfügbar — erfordert mindestens 3 "
            "erfolgreiche Target-SNR-Beobachtungen je Station."
        ),
        "temporal_unavailable": (
            "UTC-Stundenmuster nicht verfügbar — erfordert Evidenz aus "
            "mindestens 2 UTC-Tagen."
        ),
        "utc_dates_folded": "{count} UTC-Tage zusammengeführt",
    },
}


_SUCCESS_DIRECTION_FIGURE_LABELS = {
    ("en", "RX_ABS"): {
        "reach_title": (
            "TX Stations Heard by Target at Least Once by Distance"
        ),
        "reach_y": (
            "Qualifying TX stations heard by Target at least once (%)"
        ),
        "consistency_title": "RX Success Rate by TX-Station Distance",
        "snr_distance_title": (
            "Successful Target SNR by TX-Station Distance"
        ),
        "target_stations": "Heard by Target",
        "target_evidence": "Heard by Target",
        "counter_evidence": "Heard by others only",
        "snr_chronological_title": (
            "Successful RX SNR Deviation over Time"
        ),
        "snr_chronological_subtitle": (
            "Each TX station centered on its run median · {time_bin} bins"
        ),
        "snr_utc_hour_title": (
            "Successful RX SNR Deviation by UTC Hour"
        ),
        "snr_utc_hour_subtitle": (
            "Each TX station centered on its run median · 1 h bins"
        ),
        "snr_anomaly_y": (
            "Deviation from each TX station’s run median (dB)"
        ),
        "station_vote_y": "TX Stations",
        "station_support_folded_y": "TX Stations",
        "evidence_title": "RX Success Temporal Evidence: Target {callsign}",
        "snr_title": (
            "RX Success Temporal SNR Evidence: Target {callsign}"
        ),
    },
    ("en", "TX_ABS"): {
        "reach_title": (
            "RX Stations Hearing the Target at Least Once by Distance"
        ),
        "reach_y": (
            "Qualifying RX stations that heard Target at least once (%)"
        ),
        "consistency_title": "TX Success Rate by RX-Station Distance",
        "snr_distance_title": (
            "Successful Target SNR by RX-Station Distance"
        ),
        "target_stations": "Target heard",
        "target_evidence": "Target heard",
        "counter_evidence": "Other signals heard only",
        "snr_chronological_title": (
            "Successful TX SNR Deviation over Time"
        ),
        "snr_chronological_subtitle": (
            "Each RX station centered on its run median · {time_bin} bins"
        ),
        "snr_utc_hour_title": (
            "Successful TX SNR Deviation by UTC Hour"
        ),
        "snr_utc_hour_subtitle": (
            "Each RX station centered on its run median · 1 h bins"
        ),
        "snr_anomaly_y": (
            "Deviation from each RX station’s run median (dB)"
        ),
        "station_vote_y": "RX Stations",
        "station_support_folded_y": "RX Stations",
        "evidence_title": "TX Success Temporal Evidence: Target {callsign}",
        "snr_title": (
            "TX Success Temporal SNR Evidence: Target {callsign}"
        ),
    },
    ("de", "RX_ABS"): {
        "reach_title": (
            "Vom Target mindestens einmal gehörte TX-Stationen "
            "nach Entfernung"
        ),
        "reach_y": (
            "Qualifizierende TX-Stationen, vom Target mindestens "
            "einmal gehört (%)"
        ),
        "consistency_title": (
            "RX Success Rate nach Entfernung der TX-Station"
        ),
        "snr_distance_title": (
            "Erfolgreiches Target-SNR nach Entfernung der TX-Station"
        ),
        "target_stations": "Vom Target gehört",
        "target_evidence": "Vom Target gehört",
        "counter_evidence": "Nur von anderen gehört",
        "snr_chronological_title": (
            "Abweichung des erfolgreichen RX-SNR im Zeitverlauf"
        ),
        "snr_chronological_subtitle": (
            "Jede TX-Station auf ihren Laufmedian zentriert · {time_bin}-Bins"
        ),
        "snr_utc_hour_title": (
            "Abweichung des erfolgreichen RX-SNR nach UTC-Stunde"
        ),
        "snr_utc_hour_subtitle": (
            "Jede TX-Station auf ihren Laufmedian zentriert · 1-h-Bins"
        ),
        "snr_anomaly_y": (
            "Abweichung vom Laufmedian jeder TX-Station (dB)"
        ),
        "station_vote_y": "TX-Stationen",
        "station_support_folded_y": "TX-Stationen",
        "evidence_title": (
            "RX Success — Zeitliche Evidenz: Target {callsign}"
        ),
        "snr_title": (
            "RX Success — Zeitliche SNR-Evidenz: Target {callsign}"
        ),
    },
    ("de", "TX_ABS"): {
        "reach_title": (
            "RX-Stationen, die das Target mindestens einmal hörten, "
            "nach Entfernung"
        ),
        "reach_y": (
            "Qualifizierende RX-Stationen, die das Target mindestens "
            "einmal hörten (%)"
        ),
        "consistency_title": (
            "TX Success Rate nach Entfernung der RX-Station"
        ),
        "snr_distance_title": (
            "Erfolgreiches Target-SNR nach Entfernung der RX-Station"
        ),
        "target_stations": "Target gehört",
        "target_evidence": "Target gehört",
        "counter_evidence": "Nur andere Signale gehört",
        "snr_chronological_title": (
            "Abweichung des erfolgreichen TX-SNR im Zeitverlauf"
        ),
        "snr_chronological_subtitle": (
            "Jede RX-Station auf ihren Laufmedian zentriert · {time_bin}-Bins"
        ),
        "snr_utc_hour_title": (
            "Abweichung des erfolgreichen TX-SNR nach UTC-Stunde"
        ),
        "snr_utc_hour_subtitle": (
            "Jede RX-Station auf ihren Laufmedian zentriert · 1-h-Bins"
        ),
        "snr_anomaly_y": (
            "Abweichung vom Laufmedian jeder RX-Station (dB)"
        ),
        "station_vote_y": "RX-Stationen",
        "station_support_folded_y": "RX-Stationen",
        "evidence_title": (
            "TX Success — Zeitliche Evidenz: Target {callsign}"
        ),
        "snr_title": (
            "TX Success — Zeitliche SNR-Evidenz: Target {callsign}"
        ),
    },
}


def _artist_gids(figure) -> set[str]:
    """Return every non-empty Matplotlib gid attached below the figure axes."""
    return {
        str(gid)
        for axis in figure.axes
        for artist in axis.get_children()
        if (gid := artist.get_gid())
    }


def _axis_by_gid(figure, gid: str):
    """Return the unique figure axis carrying the requested regression gid."""
    matching_axes = [axis for axis in figure.axes if axis.get_gid() == gid]
    assert len(matching_axes) == 1
    return matching_axes[0]


def _panel_subtitle(axis):
    """Return the unique Success temporal subtitle artist below one title."""
    matching_artists = [
        text
        for text in axis.texts
        if text.get_gid() == "success-temporal-panel-subtitle"
    ]
    assert len(matching_artists) == 1
    return matching_artists[0]


def _figure_text_by_gid(figure, gid: str):
    """Return the unique figure-level text carrying one regression gid."""
    matching_artists = [
        text for text in figure.texts if text.get_gid() == gid
    ]
    assert len(matching_artists) == 1
    return matching_artists[0]


@pytest.mark.parametrize(
    ("distance_scope_intervals", "expected_width_km"),
    [
        (((0.0, 1250.0),), 125.0),
        (((0.0, np.nextafter(1250.0, np.inf)),), 250.0),
        (((0.0, 3000.0),), 250.0),
        (((0.0, np.nextafter(3000.0, np.inf)),), 500.0),
        (((2500.0, 8500.0),), 500.0),
        (((0.0, np.nextafter(6000.0, np.inf)),), 1000.0),
        (((0.0, 22000.0),), 1000.0),
    ],
)
def test_success_distance_width_rules_are_deterministic(
    distance_scope_intervals,
    expected_width_km,
):
    """Select 125/250/500/1,000 km widths only from the chosen distance span."""
    assert (
        _success_distance_bin_width_km(distance_scope_intervals)
        == expected_width_km
    )


def test_success_distance_grid_is_zero_anchored_and_localized():
    """Anchor every edge to a width multiple from zero and localize separators."""
    definition = _success_distance_bin_definition(
        ((2500.0, 5000.0),),
        thousands_separator=".",
    )

    assert definition["version"] == SUCCESS_DISTANCE_BINNING_VERSION
    assert definition["width_km"] == 250.0
    assert definition["edges_km"][0] == 2500.0
    assert definition["edges_km"][-1] == 5000.0
    np.testing.assert_allclose(
        np.mod(definition["edges_km"], definition["width_km"]),
        0.0,
    )
    assert definition["labels"][0] == "2.500\u20132.750 km"
    assert definition["labels"][-1] == "4.750\u20135.000 km"


def test_success_distance_assignment_is_half_open_and_closes_only_final_bound():
    """Use exact values at internal edges and admit the final scope boundary once."""
    definition = _success_distance_bin_definition(((0.0, 250.0),))
    distances = np.asarray(
        [
            0.0,
            np.nextafter(125.0, -np.inf),
            125.0,
            np.nextafter(125.0, np.inf),
            np.nextafter(250.0, -np.inf),
            250.0,
            np.nextafter(250.0, np.inf),
            -0.1,
            np.nan,
        ]
    )

    np.testing.assert_array_equal(
        _assign_success_distance_bins(distances, definition),
        [0, 0, 1, 1, 1, 1, -1, -1, -1],
    )


def test_success_distance_assignment_uses_unrounded_calculated_distance():
    """Do not move a 124.6 km station into the next bin by display rounding."""
    peers = pd.DataFrame(
        [
            _peer("A", 124.6, hits=1, misses=0, successful_snr_median=-10.0),
            _peer("B", 125.4, hits=1, misses=0, successful_snr_median=-20.0),
        ]
    )

    _definition, profile = _aggregate_success_distance_profile(
        peers,
        ((0.0, 250.0),),
    )

    np.testing.assert_array_equal(
        profile["qualifying_station_count"],
        [1, 1],
    )
    np.testing.assert_allclose(
        profile["successful_snr_median_db"],
        [-10.0, -20.0],
    )


def test_success_distance_grid_depends_on_intervals_not_direction_population():
    """Changing only direction changes values, never the shared distance edges."""
    north_peers = pd.DataFrame(
        [_peer("N", 20.0, hits=1, misses=0, successful_snr_median=-10.0)]
    )
    south_peers = pd.DataFrame(
        [_peer("S", 340.0, hits=0, misses=4)]
    )
    intervals = ((0.0, 375.0),)
    rx_terms = _presentation().absolute_terms("RX")

    north = _opportunity_segment_recipe(
        "RX Success Evidence",
        "North",
        north_peers,
        pd.DataFrame(),
        None,
        None,
        rx_terms,
        figure_labels=_figure_labels(),
        distance_scope_intervals=intervals,
    )
    south = _opportunity_segment_recipe(
        "RX Success Evidence",
        "South",
        south_peers,
        pd.DataFrame(),
        None,
        None,
        rx_terms,
        figure_labels=_figure_labels(),
        distance_scope_intervals=intervals,
    )

    np.testing.assert_array_equal(
        north["distance_edges_km"],
        south["distance_edges_km"],
    )
    np.testing.assert_array_equal(
        north["distance_centers_km"],
        south["distance_centers_km"],
    )
    assert north["distance_labels"] == south["distance_labels"]
    assert not np.array_equal(
        north["distance_qualifying_station_counts"],
        south["distance_qualifying_station_counts"],
    )


def test_disjoint_distance_scope_preserves_gaps_and_missing_metrics():
    """Inactive and unsupported bins remain visible as missing, never as zero rates."""
    peers = pd.DataFrame(
        [
            _peer("A", 100.0, hits=1, misses=1, successful_snr_median=-10.0),
            # This well-populated row lies in the unselected gap and must vanish.
            _peer("G", 3500.0, hits=100, misses=0, successful_snr_median=20.0),
            _peer("B", 5100.0, hits=0, misses=4),
        ]
    )

    definition, profile = _aggregate_success_distance_profile(
        peers,
        ((0.0, 2500.0), (5000.0, 10000.0)),
    )
    active_mask = np.asarray(definition["active_mask"], dtype=bool)
    gap_indexes = np.flatnonzero(~active_mask)

    assert len(gap_indexes) >= 1
    assert np.all(
        (definition["centers_km"][gap_indexes] > 2500.0)
        & (definition["centers_km"][gap_indexes] < 5000.0)
    )
    for metric_column in (
        "peer_reach_pct",
        "station_balanced_rate_pct",
        "observation_level_rate_pct",
        "successful_snr_median_db",
    ):
        assert profile.loc[gap_indexes, metric_column].isna().all()
    for count_column in (
        "qualifying_station_count",
        "target_station_count",
        "confirmed_opportunity_count",
        "target_count",
        "counter_count",
        "successful_snr_station_count",
    ):
        assert (profile.loc[gap_indexes, count_column] == 0).all()

    # At least one selected but unsupported bin is also missing evidence.
    empty_active = active_mask & profile["qualifying_station_count"].eq(0).to_numpy()
    assert empty_active.any()
    assert profile.loc[empty_active, "peer_reach_pct"].isna().all()
    assert profile.loc[empty_active, "station_balanced_rate_pct"].isna().all()
    assert profile.loc[empty_active, "observation_level_rate_pct"].isna().all()


def test_success_distance_formulas_and_support_reconcile():
    """Compute reach, both rate weightings, and all support from qualifying peers."""
    peers = pd.DataFrame(
        [
            _peer("A", 10.0, hits=0, misses=4),
            _peer("B", 20.0, hits=1, misses=1, successful_snr_median=-20.0),
            _peer("C", 30.0, hits=3, misses=1, successful_snr_median=-10.0),
            _peer("D", 140.0, hits=2, misses=8, successful_snr_median=-15.0),
            _peer(
                "E",
                160.0,
                hits=100,
                misses=0,
                successful_snr_median=0.0,
                eligible=False,
            ),
        ]
    )

    _definition, profile = _aggregate_success_distance_profile(
        peers,
        ((0.0, 375.0),),
    )

    first = profile.iloc[0]
    assert first["qualifying_station_count"] == 3
    assert first["target_station_count"] == 2
    assert first["peer_reach_pct"] == pytest.approx(200.0 / 3.0)
    assert first["station_balanced_rate_pct"] == pytest.approx(
        (0.0 + 50.0 + 75.0) / 3.0
    )
    assert first["observation_level_rate_pct"] == pytest.approx(40.0)
    assert first["confirmed_opportunity_count"] == 10
    assert first["target_count"] == 4
    assert first["counter_count"] == 6
    assert first["successful_snr_station_count"] == 2

    second = profile.iloc[1]
    assert second["qualifying_station_count"] == 1
    assert second["target_station_count"] == 1
    assert second["peer_reach_pct"] == pytest.approx(100.0)
    assert second["station_balanced_rate_pct"] == pytest.approx(20.0)
    assert second["observation_level_rate_pct"] == pytest.approx(20.0)
    assert second["confirmed_opportunity_count"] == 10
    assert second["target_count"] == 2
    assert second["counter_count"] == 8
    assert second["successful_snr_station_count"] == 1

    assert int(profile["qualifying_station_count"].sum()) == 4
    assert int(profile["target_station_count"].sum()) == 3
    assert int(profile["confirmed_opportunity_count"].sum()) == 20
    assert int(profile["target_count"].sum()) == 6
    assert int(profile["counter_count"].sum()) == 14
    assert int(profile["successful_snr_station_count"].sum()) == 3


def test_successful_snr_distance_handles_zero_one_two_and_three_stations():
    """Show no interval, a two-station range, then an IQR without report weighting."""
    peers = pd.DataFrame(
        [
            _peer("Z", 10.0, hits=0, misses=2),
            _peer("A", 130.0, hits=1, misses=0, successful_snr_median=-20.0),
            _peer("B", 260.0, hits=50, misses=0, successful_snr_median=-30.0),
            _peer("C", 270.0, hits=1, misses=0, successful_snr_median=-10.0),
            _peer("D", 380.0, hits=1, misses=0, successful_snr_median=-30.0),
            _peer("E", 390.0, hits=1, misses=0, successful_snr_median=-20.0),
            _peer("F", 400.0, hits=1, misses=0, successful_snr_median=-10.0),
        ]
    )

    _definition, profile = _aggregate_success_distance_profile(
        peers,
        ((0.0, 500.0),),
    )

    np.testing.assert_array_equal(
        profile["successful_snr_station_count"],
        [0, 1, 2, 3],
    )
    assert profile["successful_snr_interval_kind"].tolist() == [
        "none",
        "none",
        "range",
        "iqr",
    ]
    assert np.isnan(profile.loc[0, "successful_snr_median_db"])
    assert np.isnan(profile.loc[0, "successful_snr_interval_lower_db"])
    assert profile.loc[1, "successful_snr_median_db"] == -20.0
    assert np.isnan(profile.loc[1, "successful_snr_interval_lower_db"])
    assert profile.loc[2, "successful_snr_median_db"] == -20.0
    assert profile.loc[2, "successful_snr_interval_lower_db"] == -30.0
    assert profile.loc[2, "successful_snr_interval_upper_db"] == -10.0
    assert profile.loc[3, "successful_snr_median_db"] == -20.0
    assert profile.loc[3, "successful_snr_interval_lower_db"] == -25.0
    assert profile.loc[3, "successful_snr_interval_upper_db"] == -15.0


@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("analysis_id", ["RX_ABS", "TX_ABS"])
def test_success_summary_retains_metrics_and_displays_compact_directional_terms(
    language,
    analysis_id,
):
    """Keep both weighting metrics while displaying the requested compact rows."""
    summary = build_opportunity_inspector_view_model(
        _summary_peer_rows(),
        _summary_evidence_rows(),
        analysis_id=analysis_id,
        minimum_confirmed=2,
        presentation_context=_presentation(language),
    )

    assert summary.confirmed_station_count == 4
    assert summary.zero_target_station_count == 1
    assert summary.confirmed_opportunity_count == 15
    assert summary.target_count == 6
    assert summary.counter_count == 9
    assert summary.station_balanced_rate_pct == pytest.approx(43.75)
    assert summary.observation_level_rate_pct == pytest.approx(40.0)
    assert summary.weighting_gap_percentage_points == pytest.approx(-3.75)
    assert summary.median_opportunities_per_station == pytest.approx(4.0)
    assert len(summary.summary_lines) == 2
    outcomes = _SUCCESS_DIRECTION_FIGURE_LABELS[
        (language, analysis_id)
    ]
    station_heading = "Stations" if language == "en" else "Stationen"
    opportunity_heading = (
        "Opportunities" if language == "en" else "Gelegenheiten"
    )
    assert summary.summary_lines == [
        (
            f"{station_heading}: {outcomes['target_evidence']} 3 · "
            f"{outcomes['counter_evidence']} 1 · Success Rate 43.8%"
        ),
        (
            f"{opportunity_heading}: {outcomes['target_evidence']} 6 · "
            f"{outcomes['counter_evidence']} 9 · Success Rate 40.0%"
        ),
    ]
    for line in summary.summary_lines:
        assert "Elsewhere" not in line
        assert "Other Signals" not in line


def test_visible_success_station_filter_maps_back_to_canonical_export_rows():
    """Keep display-only columns out of the compatibility station CSV."""
    display = pd.DataFrame(
        {
            "TX-Station": ["B"],
            "Locator": ["B000"],
            "Vom Target gehört": [1],
            "Nur von anderen gehört": [1],
            "Bestätigte Gelegenheiten": [2],
        }
    )
    canonical = pd.DataFrame(
        {
            "TX Station": ["A", "B"],
            "Locator": ["A000", "B000"],
            "Target (T)": [0, 1],
            "Elsewhere (E)": [5, 1],
            "T/(T+E) (%)": [0.0, 50.0],
        }
    )
    source = canonical.copy(deep=True)

    selected = _opportunity_export_station_rows(
        display,
        canonical,
        display_station_column="TX-Station",
        display_locator_column="Locator",
        export_station_column="TX Station",
        export_locator_column="Locator",
    )

    pd.testing.assert_frame_equal(canonical, source)
    assert list(selected.columns) == list(canonical.columns)
    assert selected.to_dict("records") == [
        {
            "TX Station": "B",
            "Locator": "B000",
            "Target (T)": 1,
            "Elsewhere (E)": 1,
            "T/(T+E) (%)": 50.0,
        }
    ]


@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("analysis_id", ["RX_ABS", "TX_ABS"])
def test_success_figure_labels_are_exact_and_direction_specific(
    language,
    analysis_id,
):
    """Keep every Success figure label bilingual and direction-aware."""
    labels = _figure_labels(language, analysis_id)
    expected = {
        **_SUCCESS_COMMON_FIGURE_LABELS[language],
        **_SUCCESS_DIRECTION_FIGURE_LABELS[(language, analysis_id)],
    }

    for key, expected_text in expected.items():
        if key not in {"evidence_title", "snr_title"}:
            assert labels[key] == expected_text
    for figure_kind in ("evidence", "snr"):
        assert _success_temporal_figure_title(
            "g3zil",
            analysis_id,
            T[language],
            figure_kind=figure_kind,
        ) == expected[f"{figure_kind}_title"].format(callsign="G3ZIL")
    for outcome_key in (
        "target_stations",
        "target_evidence",
        "counter_evidence",
    ):
        assert labels[outcome_key] not in {
            "Target",
            "Elsewhere",
            "Other Signals",
        }
    for title in (
        labels["reach_title"],
        labels["consistency_title"],
        labels["snr_distance_title"],
    ):
        rendered_title = _success_distance_panel_title(title)
        assert "\n" in rendered_title
        assert rendered_title.replace("\n", " ") == title


def test_success_temporal_figure_title_rejects_unknown_figure_kind():
    """Require callers to select the SNR or evidence title explicitly."""
    with pytest.raises(
        ValueError,
        match="must be 'snr' or 'evidence'",
    ):
        _success_temporal_figure_title(
            "G3ZIL",
            "RX_ABS",
            T["en"],
            figure_kind="unknown",
        )


def test_success_temporal_baselines_require_three_successful_snr_observations():
    """Exclude a two-value station only from anomaly rows, not Success evidence."""
    rows = _temporal_evidence_rows()
    qualifying = rows[rows["peer_sign"].isin(["A", "B", "C"])].copy()
    qualifying = qualifying[(qualifying["hit"] + qualifying["miss"]) > 0]
    qualifying["evidence_utc"] = opportunity_utc_from_time_slot(
        qualifying["time_slot"]
    )

    anomalies, baselines = _prepare_success_snr_anomalies(qualifying)

    assert SUCCESS_MINIMUM_SNR_BASELINE_OBSERVATIONS == 3
    assert set(baselines["peer_sign"]) == {"A", "B"}
    assert baselines.set_index("peer_sign").loc[
        "A",
        "station_baseline_snr_db",
    ] == pytest.approx(-5.0)
    assert baselines.set_index("peer_sign").loc[
        "B",
        "station_baseline_snr_db",
    ] == pytest.approx(0.0)
    assert "C" not in set(anomalies["peer_sign"])
    np.testing.assert_allclose(
        sorted(anomalies.loc[anomalies["peer_sign"] == "A", "snr_anomaly_db"]),
        [-15.0, -5.0, 5.0, 15.0],
    )


def test_success_relative_density_normalizes_each_panel_to_its_maximum():
    """Represent a 2:1 occupied-cell count ratio as 100% and 50%."""
    grid = _success_relative_density_grid(
        [0, 0, 1],
        [0.1, 0.2, 0.1],
        x_count=3,
        anomaly_centers_db=np.asarray([-1.0, 0.0, 1.0]),
    )

    assert grid[1, 0] == pytest.approx(100.0)
    assert grid[1, 1] == pytest.approx(50.0)
    assert np.isnan(grid[1, 2])
    finite = grid[np.isfinite(grid)]
    assert finite.min() >= 0.0
    assert finite.max() == pytest.approx(100.0)


@pytest.mark.parametrize(
    ("count", "expected_text"),
    [
        (0, "0"),
        (7.25, "7.25"),
        (850, "850"),
        (6_400, "6k4"),
        (12_500, "12k5"),
        (100_000, "100k"),
        (6_800_000, "6M8"),
        (25_000_000, "25M"),
        (-6_400, "-6k4"),
        (np.nan, ""),
    ],
)
def test_success_temporal_count_formatter_uses_ham_compact_notation(
    count,
    expected_text,
):
    """Format count-axis ticks compactly without losing useful scale detail."""
    assert _format_ham_compact_count(count) == expected_text


@pytest.mark.parametrize(
    ("rate_series", "expected_upper_limit"),
    [
        (([],), 10.0),
        (([np.nan, -1.0],), 10.0),
        (([8.0],), 10.0),
        (([8.34],), 20.0),
        (([20.0],), 25.0),
        (([42.0],), 60.0),
        (([60.0],), 75.0),
        (([75.0],), 100.0),
        (([100.0], [20.0, 30.0]), 100.0),
    ],
)
def test_success_temporal_rate_ceiling_adds_rounded_shared_headroom(
    rate_series,
    expected_upper_limit,
):
    """Round 20% rate headroom to the established common axis ceilings."""
    assert _success_temporal_rate_axis_max(*rate_series) == expected_upper_limit


def _assert_temporal_stack_equivalence(profile: dict[str, object]) -> None:
    """Prove both stacked shares reproduce the retained rate diagnostics."""
    required_arrays = {
        "station_success_votes",
        "station_counter_votes",
        "opportunity_success_counts",
        "opportunity_counter_counts",
        "station_balanced_rate_pct",
        "observation_level_rate_pct",
        "target_counts",
        "counter_counts",
        "station_counts",
    }
    assert required_arrays.issubset(profile)

    station_success = np.asarray(profile["station_success_votes"], dtype=float)
    station_counter = np.asarray(profile["station_counter_votes"], dtype=float)
    opportunity_success = np.asarray(
        profile["opportunity_success_counts"],
        dtype=float,
    )
    opportunity_counter = np.asarray(
        profile["opportunity_counter_counts"],
        dtype=float,
    )
    old_station_rates = np.asarray(
        profile["station_balanced_rate_pct"],
        dtype=float,
    )
    old_observation_rates = np.asarray(
        profile["observation_level_rate_pct"],
        dtype=float,
    )
    old_success_counts = np.asarray(profile["target_counts"], dtype=float)
    old_counter_counts = np.asarray(profile["counter_counts"], dtype=float)
    old_station_counts = np.asarray(profile["station_counts"], dtype=float)

    assert len(
        {
            len(station_success),
            len(station_counter),
            len(opportunity_success),
            len(opportunity_counter),
            len(old_station_rates),
            len(old_observation_rates),
            len(old_success_counts),
            len(old_counter_counts),
            len(old_station_counts),
        }
    ) == 1
    np.testing.assert_allclose(opportunity_success, old_success_counts)
    np.testing.assert_allclose(opportunity_counter, old_counter_counts)

    station_totals = station_success + station_counter
    station_has_evidence = old_station_counts > 0
    np.testing.assert_allclose(
        station_totals[station_has_evidence],
        old_station_counts[station_has_evidence],
        rtol=0.0,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        100.0
        * station_success[station_has_evidence]
        / station_totals[station_has_evidence],
        old_station_rates[station_has_evidence],
        rtol=0.0,
        atol=1e-12,
    )
    assert np.isnan(old_station_rates[~station_has_evidence]).all()

    opportunity_totals = opportunity_success + opportunity_counter
    opportunity_has_evidence = opportunity_totals > 0
    np.testing.assert_allclose(
        opportunity_totals,
        old_success_counts + old_counter_counts,
    )
    np.testing.assert_allclose(
        100.0
        * opportunity_success[opportunity_has_evidence]
        / opportunity_totals[opportunity_has_evidence],
        old_observation_rates[opportunity_has_evidence],
        rtol=0.0,
        atol=1e-12,
    )
    assert np.isnan(old_observation_rates[~opportunity_has_evidence]).all()


def _assert_folded_station_support_equivalence(
    profile: dict[str, object],
) -> None:
    """Prove corrected folded support preserves the pooled station rate."""
    required_arrays = {
        "station_date_hour_presence_counts",
        "represented_utc_date_counts",
        "station_average_support_per_utc_date",
        "station_success_support_per_utc_date",
        "station_counter_support_per_utc_date",
        "station_balanced_rate_pct",
    }
    assert required_arrays.issubset(profile)

    station_date_hour_presence = np.asarray(
        profile["station_date_hour_presence_counts"],
        dtype=float,
    )
    represented_dates = np.asarray(
        profile["represented_utc_date_counts"],
        dtype=float,
    )
    average_support = np.asarray(
        profile["station_average_support_per_utc_date"],
        dtype=float,
    )
    success_support = np.asarray(
        profile["station_success_support_per_utc_date"],
        dtype=float,
    )
    counter_support = np.asarray(
        profile["station_counter_support_per_utc_date"],
        dtype=float,
    )
    pooled_station_rates = np.asarray(
        profile["station_balanced_rate_pct"],
        dtype=float,
    )

    expected_average_support = np.zeros_like(average_support)
    np.divide(
        station_date_hour_presence,
        represented_dates,
        out=expected_average_support,
        where=represented_dates > 0.0,
    )
    np.testing.assert_allclose(
        average_support,
        expected_average_support,
        rtol=0.0,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        success_support + counter_support,
        average_support,
        rtol=0.0,
        atol=1e-12,
    )
    has_support = average_support > 0.0
    np.testing.assert_allclose(
        100.0 * success_support[has_support] / average_support[has_support],
        pooled_station_rates[has_support],
        rtol=0.0,
        atol=1e-12,
    )
    assert np.isnan(pooled_station_rates[~has_support]).all()


def test_success_temporal_recipe_balances_station_bin_and_station_date_hour():
    """Preserve raw rates/counts and add folded per-date display stacks."""
    recipe = _opportunity_temporal_recipe(
        "RX Success Temporal Evidence",
        "Full Range | All Directions",
        _temporal_peer_rows(),
        _temporal_evidence_rows(),
        pd.Timestamp("2026-07-10T00:00:00Z"),
        pd.Timestamp("2026-07-13T00:00:00Z"),
        _presentation().absolute_terms("RX"),
        figure_labels=_figure_labels(),
    )

    assert recipe["schema_version"] == 7
    assert (
        recipe["population_mode"]
        == SUCCESS_TEMPORAL_POPULATION_ACTIVE_SCOPE
    )
    assert (
        recipe["snr_representation"]
        == SUCCESS_SNR_REPRESENTATION_STATION_RELATIVE
    )
    assert recipe["snr_baseline_version"] == SUCCESS_SNR_BASELINE_VERSION
    assert recipe["folded_opportunity_normalization"] == (
        "sum-outcomes-per-represented-utc-date-v1"
    )
    assert recipe["folded_station_support_policy"] == (
        "station-date-hour-presence-per-represented-utc-date-"
        "partitioned-by-pooled-station-rate-v1"
    )
    assert recipe["minimum_snr_baseline_observations"] == 3
    assert recipe["snr_baseline_station_count"] == 2
    assert recipe["time_bin_options"] == list(SUCCESS_TEMPORAL_TIME_BINS)
    assert recipe["utc_date_count"] == 2

    for profile in recipe["chronological_profiles"].values():
        _assert_temporal_stack_equivalence(profile)
        assert int(np.sum(profile["target_counts"])) == 9
        assert int(np.sum(profile["counter_counts"])) == 3
        finite_station_rates = np.asarray(
            profile["station_balanced_rate_pct"],
            dtype=float,
        )
        finite_station_rates = finite_station_rates[
            np.isfinite(finite_station_rates)
        ]
        assert np.all(
            (0.0 <= finite_station_rates)
            & (finite_station_rates <= 100.0)
        )

    chronological = recipe["chronological_profiles"]["1h"]
    # A and B each contribute one station median in the first bin despite two
    # successful reports apiece; C remains in rate/support but not SNR.
    assert chronological["snr_station_value_counts"][0] == 2
    assert chronological["snr_station_balanced_median_db"][0] == -10.0
    assert chronological["station_counts"][0] == 3
    assert chronological["target_counts"][0] == 5
    assert chronological["counter_counts"][0] == 0
    assert chronological["station_success_votes"][0] == pytest.approx(3.0)
    assert chronological["station_counter_votes"][0] == pytest.approx(0.0)
    assert chronological["opportunity_success_counts"][0] == 5
    assert chronological["opportunity_counter_counts"][0] == 0
    assert np.nanmax(chronological["snr_density_pct"]) == pytest.approx(100.0)
    assert 50.0 in chronological["snr_density_pct"][
        np.isfinite(chronological["snr_density_pct"])
    ]

    folded = recipe["folded_profile"]
    _assert_temporal_stack_equivalence(folded)
    _assert_folded_station_support_equivalence(folded)
    # UTC hour 00 receives A/date-10, A/date-11 and B/date-10: three values.
    assert folded["snr_station_value_counts"][0] == 3
    assert folded["snr_station_balanced_median_db"][0] == -10.0
    assert folded["station_counts"][0] == 3
    assert folded["utc_date_counts"][0] == 2
    np.testing.assert_array_equal(
        folded["represented_utc_date_counts"],
        np.full(24, 2, dtype=np.int64),
    )
    assert int(np.sum(folded["target_counts"])) == 9
    assert int(np.sum(folded["counter_counts"])) == 3
    np.testing.assert_allclose(
        folded["station_success_votes"][:3],
        [3.0, 1.0, 0.0],
    )
    np.testing.assert_allclose(
        folded["station_counter_votes"][:3],
        [0.0, 1.0, 1.0],
    )
    np.testing.assert_array_equal(
        folded["opportunity_success_counts"][:3],
        [8, 1, 0],
    )
    np.testing.assert_array_equal(
        folded["opportunity_counter_counts"][:3],
        [0, 1, 2],
    )
    np.testing.assert_array_equal(
        folded["station_date_hour_presence_counts"][:3],
        [5, 2, 2],
    )
    np.testing.assert_allclose(
        folded["station_average_support_per_utc_date"][:3],
        [2.5, 1.0, 1.0],
    )
    np.testing.assert_allclose(
        folded["station_success_support_per_utc_date"][:3],
        [2.5, 0.5, 0.0],
    )
    np.testing.assert_allclose(
        folded["station_counter_support_per_utc_date"][:3],
        [0.0, 0.5, 1.0],
    )
    np.testing.assert_allclose(
        folded["opportunity_success_counts_per_utc_date"][:3],
        [4.0, 0.5, 0.0],
    )
    np.testing.assert_allclose(
        folded["opportunity_counter_counts_per_utc_date"][:3],
        [0.0, 0.5, 1.0],
    )
    np.testing.assert_allclose(
        folded["station_balanced_rate_pct"][:3],
        [100.0, 50.0, 0.0],
    )
    np.testing.assert_allclose(
        folded["observation_level_rate_pct"][:3],
        [100.0, 50.0, 0.0],
    )
    chronological_station_totals = (
        np.asarray(chronological["station_success_votes"], dtype=float)
        + np.asarray(chronological["station_counter_votes"], dtype=float)
    )
    chronological_opportunity_totals = (
        np.asarray(chronological["opportunity_success_counts"], dtype=float)
        + np.asarray(chronological["opportunity_counter_counts"], dtype=float)
    )
    represented_date_offsets = (0, 24)
    np.testing.assert_allclose(
        (
            np.asarray(
                folded["station_success_support_per_utc_date"],
                dtype=float,
            )
            + np.asarray(
                folded["station_counter_support_per_utc_date"],
                dtype=float,
            )
        ),
        np.mean(
            [
                chronological_station_totals[offset : offset + 24]
                for offset in represented_date_offsets
            ],
            axis=0,
        ),
        rtol=0.0,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        (
            np.asarray(
                folded["opportunity_success_counts_per_utc_date"],
                dtype=float,
            )
            + np.asarray(
                folded["opportunity_counter_counts_per_utc_date"],
                dtype=float,
            )
        ),
        np.mean(
            [
                chronological_opportunity_totals[offset : offset + 24]
                for offset in represented_date_offsets
            ],
            axis=0,
        ),
        rtol=0.0,
        atol=1e-12,
    )
    assert np.nanmax(folded["snr_density_pct"]) == pytest.approx(100.0)
    assert 50.0 in folded["snr_density_pct"][
        np.isfinite(folded["snr_density_pct"])
    ]


def test_selected_success_actual_snr_uses_raw_rows_and_date_hour_medians():
    """Keep raw chronology but give each represented date one folded SNR value."""
    recipe = _selected_actual_snr_recipe_for_test()

    assert recipe["schema_version"] == 7
    assert (
        recipe["population_mode"]
        == SUCCESS_TEMPORAL_POPULATION_SELECTED_STATION
    )
    assert recipe["snr_representation"] == SUCCESS_SNR_REPRESENTATION_ACTUAL
    assert recipe["snr_baseline_version"] is None
    assert recipe["minimum_snr_baseline_observations"] is None
    assert recipe["snr_baseline_station_count"] == 0
    assert recipe["utc_date_count"] == 2

    chronological = recipe["chronological_profiles"]["1h"]
    folded = recipe["folded_profile"]
    actual_snr_edges_db = np.asarray(
        chronological["snr_value_edges_db"],
        dtype=float,
    )
    assert actual_snr_edges_db[0] < -30.0
    assert actual_snr_edges_db[-1] > 10.0
    for profile in (
        *recipe["chronological_profiles"].values(),
        folded,
    ):
        np.testing.assert_array_equal(
            profile["snr_value_edges_db"],
            actual_snr_edges_db,
        )
        assert "snr_anomaly_edges_db" not in profile

    assert chronological["snr_value_counts"][0] == 3
    assert chronological["snr_value_counts"][24] == 1
    assert chronological["snr_median_db"][0] == pytest.approx(-30.0)
    assert chronological["snr_median_db"][24] == pytest.approx(10.0)

    def density_value(profile, snr_db: float, x_index: int) -> float:
        """Return one actual-SNR density cell selected by its explicit edges."""
        edges = np.asarray(profile["snr_value_edges_db"], dtype=float)
        snr_index = int(np.searchsorted(edges, snr_db, side="right") - 1)
        return float(profile["snr_density_pct"][snr_index, x_index])

    # The 0 dB observation remains a second occupied cell in date 1's
    # chronological bin. A station-bin reduction would have removed it.
    assert density_value(chronological, -30.0, 0) == pytest.approx(100.0)
    assert density_value(chronological, 0.0, 0) == pytest.approx(50.0)
    assert density_value(chronological, 10.0, 24) == pytest.approx(50.0)

    # Folding first reduces date 1 to -30 dB and date 2 to +10 dB. Those two
    # equally weighted date-hour medians produce -10 dB, not the raw-row
    # population median of -30 dB.
    assert folded["snr_value_counts"][0] == 2
    assert folded["snr_median_db"][0] == pytest.approx(-10.0)
    assert density_value(folded, -30.0, 0) == pytest.approx(100.0)
    assert density_value(folded, 10.0, 0) == pytest.approx(100.0)
    assert np.isnan(density_value(folded, 0.0, 0))

    # With one exact station, station-balanced and observation-level rates are
    # the same scientific series for every chronological bin and folded hour.
    for profile in (
        *recipe["chronological_profiles"].values(),
        folded,
    ):
        np.testing.assert_allclose(
            profile["station_balanced_rate_pct"],
            profile["observation_level_rate_pct"],
            rtol=0.0,
            atol=1e-12,
            equal_nan=True,
        )
    assert chronological["station_balanced_rate_pct"][0] == pytest.approx(
        75.0
    )
    assert chronological["observation_level_rate_pct"][24] == pytest.approx(
        50.0
    )
    assert folded["station_balanced_rate_pct"][0] == pytest.approx(
        100.0 * 4.0 / 6.0
    )
    np.testing.assert_allclose(
        (
            np.asarray(
                chronological["station_success_votes"],
                dtype=float,
            )
            + np.asarray(
                chronological["station_counter_votes"],
                dtype=float,
            )
        )[
            np.asarray(chronological["station_counts"], dtype=np.int64) > 0
        ],
        1.0,
    )
    assert folded["station_average_support_per_utc_date"][0] == pytest.approx(
        1.0
    )
    assert (
        folded["opportunity_success_counts_per_utc_date"][0]
        == pytest.approx(2.0)
    )
    assert (
        folded["opportunity_counter_counts_per_utc_date"][0]
        == pytest.approx(1.0)
    )

    selected_summary = recipe["selected_station_summary"]
    assert selected_summary["peer_sign"] == "SEL"
    assert selected_summary["peer_grid"] == "SE00"
    assert selected_summary["confirmed_opportunities"] == 7
    assert selected_summary["successful_snr_median_db"] == pytest.approx(
        -15.0
    )


def test_selected_success_actual_snr_renderer_reuses_axes_without_baseline():
    """Reuse active temporal geometry while omitting anomaly-only SNR artists."""
    selected_recipe = _selected_actual_snr_recipe_for_test()
    selected_recipe["time_bin"] = "1h"
    active_recipe = _temporal_recipe_for_test()
    active_recipe["time_bin"] = "1h"
    selected_figure = render_segment_temporal_snr_export_figure(
        selected_recipe
    )
    active_figure = render_segment_temporal_snr_export_figure(active_recipe)
    try:
        assert selected_figure is not None
        assert active_figure is not None
        selected_figure.canvas.draw()
        active_figure.canvas.draw()

        selected_chronological = _axis_by_gid(
            selected_figure,
            "success-temporal-snr-chronological-axis",
        )
        selected_folded = _axis_by_gid(
            selected_figure,
            "success-temporal-snr-folded-axis",
        )
        active_chronological = _axis_by_gid(
            active_figure,
            "success-temporal-snr-chronological-axis",
        )
        active_folded = _axis_by_gid(
            active_figure,
            "success-temporal-snr-folded-axis",
        )

        np.testing.assert_allclose(
            selected_figure.get_size_inches(),
            active_figure.get_size_inches(),
        )
        assert selected_chronological.get_position().bounds == pytest.approx(
            active_chronological.get_position().bounds
        )
        assert selected_folded.get_position().bounds == pytest.approx(
            active_folded.get_position().bounds
        )
        assert selected_chronological.get_ylim() == pytest.approx(
            selected_folded.get_ylim()
        )
        assert selected_chronological.get_ylabel() == selected_recipe[
            "labels"
        ]["snr_y"]
        assert selected_folded.get_ylabel() == selected_recipe["labels"][
            "snr_y"
        ]
        assert selected_figure._suptitle.get_text() == selected_recipe[
            "snr_title"
        ]

        selected_gids = _artist_gids(selected_figure)
        assert "success-temporal-snr-density" in selected_gids
        assert "success-temporal-snr-bin-median" in selected_gids
        assert "success-temporal-snr-baseline" not in selected_gids
        for axis, expected_median_label in (
            (
                selected_chronological,
                selected_recipe["labels"]["bin_median_chronological"],
            ),
            (
                selected_folded,
                selected_recipe["labels"]["bin_median_folded"],
            ),
        ):
            assert [
                text.get_text() for text in axis.get_legend().get_texts()
            ] == [expected_median_label]
        assert any(
            axis.yaxis.label.get_text()
            == selected_recipe["labels"]["snr_density"]
            for axis in selected_figure.axes
        )
    finally:
        if selected_figure is not None:
            dispose_matplotlib_figure(selected_figure)
        if active_figure is not None:
            dispose_matplotlib_figure(active_figure)


@pytest.mark.parametrize(
    ("successful_snr_db", "has_successful_snr"),
    [
        (np.nan, False),
        (-17.0, True),
    ],
)
def test_selected_success_actual_snr_renders_absent_and_sparse_evidence(
    successful_snr_db,
    has_successful_snr,
):
    """Render zero or one successful SNR value without synthesis or fallback."""
    peer_grid = _peer("SEL", 1173.0, hits=1, misses=1)["peer_grid"]
    rows = pd.DataFrame(
        [
            {
                "time_slot": _time_slot("2026-07-10T00:00:00Z"),
                "peer_sign": "SEL",
                "peer_grid": peer_grid,
                "hit": 1,
                "miss": 0,
                "target_snr": successful_snr_db,
            },
            {
                "time_slot": _time_slot("2026-07-11T00:00:00Z"),
                "peer_sign": "SEL",
                "peer_grid": peer_grid,
                "hit": 0,
                "miss": 1,
                "target_snr": np.nan,
            },
        ]
    )
    recipe = _selected_actual_snr_recipe_for_test(rows)
    recipe["time_bin"] = "1h"
    chronological = recipe["chronological_profiles"]["1h"]
    folded = recipe["folded_profile"]

    edges = np.asarray(chronological["snr_value_edges_db"], dtype=float)
    assert np.isfinite(edges).all()
    assert np.all(np.diff(edges) > 0.0)
    assert int(np.sum(chronological["snr_value_counts"])) == int(
        has_successful_snr
    )
    assert int(np.sum(folded["snr_value_counts"])) == int(
        has_successful_snr
    )
    if has_successful_snr:
        assert np.nanmax(chronological["snr_density_pct"]) == pytest.approx(
            100.0
        )
        assert np.nanmax(folded["snr_density_pct"]) == pytest.approx(100.0)
    else:
        assert np.isnan(chronological["snr_density_pct"]).all()
        assert np.isnan(folded["snr_density_pct"]).all()
        assert np.isnan(chronological["snr_median_db"]).all()
        assert np.isnan(folded["snr_median_db"]).all()

    figure = render_segment_temporal_snr_export_figure(recipe)
    try:
        assert figure is not None
        figure.canvas.draw()
        assert "success-temporal-snr-baseline" not in _artist_gids(figure)
        unavailable_texts = [
            text.get_text()
            for axis in figure.axes
            for text in axis.texts
            if text.get_text() == recipe["labels"]["snr_unavailable"]
        ]
        assert len(unavailable_texts) == (0 if has_successful_snr else 2)
    finally:
        if figure is not None:
            dispose_matplotlib_figure(figure)


def test_success_folded_display_denominator_includes_zero_evidence_date_hours():
    """Average each UTC hour over represented dates, including empty date-hours."""
    folded = _temporal_recipe_for_test()["folded_profile"]

    # Hour 01 has evidence only on July 10, but July 11 is represented elsewhere
    # in the scoped run and therefore remains in the folded display denominator.
    assert folded["utc_date_counts"][1] == 1
    assert folded["represented_utc_date_counts"][1] == 2
    assert folded["station_success_votes"][1] == pytest.approx(1.0)
    assert folded["station_counter_votes"][1] == pytest.approx(1.0)
    assert folded["station_date_hour_presence_counts"][1] == 2
    assert folded["station_average_support_per_utc_date"][1] == pytest.approx(
        1.0
    )
    assert folded["station_success_support_per_utc_date"][1] == pytest.approx(
        0.5
    )
    assert folded["station_counter_support_per_utc_date"][1] == pytest.approx(
        0.5
    )
    assert folded["opportunity_success_counts"][1] == 1
    assert folded["opportunity_counter_counts"][1] == 1
    assert folded["opportunity_success_counts_per_utc_date"][1] == pytest.approx(
        0.5
    )
    assert folded["opportunity_counter_counts_per_utc_date"][1] == pytest.approx(
        0.5
    )
    assert folded["station_balanced_rate_pct"][1] == pytest.approx(50.0)
    assert folded["observation_level_rate_pct"][1] == pytest.approx(50.0)
    _assert_folded_station_support_equivalence(folded)


def test_success_folded_recurring_station_support_stays_one_per_utc_date():
    """Render one recurring station as one daily support unit, not one divided by days."""
    peer_rows = pd.DataFrame([_peer("A", 100.0, hits=3, misses=0)])
    evidence_rows = pd.DataFrame(
        [
            {
                "time_slot": _time_slot(f"2026-07-{day:02d}T00:00:00Z"),
                "peer_sign": "A",
                "peer_grid": "A000",
                "hit": 1,
                "miss": 0,
                "target_snr": np.nan,
            }
            for day in (10, 11, 12)
        ]
    )
    recipe = _opportunity_temporal_recipe(
        "RX Success Temporal Evidence",
        "Recurring station",
        peer_rows,
        evidence_rows,
        pd.Timestamp("2026-07-10T00:00:00Z"),
        pd.Timestamp("2026-07-13T00:00:00Z"),
        _presentation().absolute_terms("RX"),
        figure_labels=_figure_labels(),
    )
    folded = recipe["folded_profile"]

    assert folded["represented_utc_date_counts"][0] == 3
    assert folded["station_counts"][0] == 1
    assert folded["station_success_votes"][0] == pytest.approx(1.0)
    assert folded["station_counter_votes"][0] == pytest.approx(0.0)
    assert folded["station_balanced_rate_pct"][0] == pytest.approx(100.0)
    assert folded["station_date_hour_presence_counts"][0] == 3
    assert folded["station_average_support_per_utc_date"][0] == pytest.approx(
        1.0
    )
    assert folded["station_success_support_per_utc_date"][0] == pytest.approx(
        1.0
    )
    assert folded["station_counter_support_per_utc_date"][0] == pytest.approx(
        0.0
    )
    _assert_temporal_stack_equivalence(folded)
    _assert_folded_station_support_equivalence(folded)


def test_success_folded_rate_gives_one_vote_per_distinct_station_not_presence():
    """Keep date recurrence in support without multiplying station-rate weight."""
    evidence_rows = pd.DataFrame(
        [
            {
                "time_slot": _time_slot(
                    f"2026-07-{day:02d}T00:00:00Z"
                ),
                "peer_sign": "RECURRING",
                "peer_grid": "RE00",
                "hit": 1,
                "miss": 0,
                "target_snr": np.nan,
            }
            for day in range(1, 11)
        ]
        + [
            {
                "time_slot": _time_slot("2026-07-01T00:20:00Z"),
                "peer_sign": "SINGLE",
                "peer_grid": "SI00",
                "hit": 0,
                "miss": 1,
                "target_snr": np.nan,
            }
        ]
    )
    peer_rows = pd.DataFrame(
        [
            _peer("RECURRING", 100.0, hits=10, misses=0),
            _peer("SINGLE", 200.0, hits=0, misses=1),
        ]
    )
    peer_rows.loc[
        peer_rows["peer_sign"] == "RECURRING",
        "peer_grid",
    ] = "RE00"
    peer_rows.loc[
        peer_rows["peer_sign"] == "SINGLE",
        "peer_grid",
    ] = "SI00"
    recipe = _opportunity_temporal_recipe(
        "RX Success Temporal Evidence",
        "Distinct-station rate",
        peer_rows,
        evidence_rows,
        pd.Timestamp("2026-07-01T00:00:00Z"),
        pd.Timestamp("2026-07-11T00:00:00Z"),
        _presentation().absolute_terms("RX"),
        figure_labels=_figure_labels(),
    )
    folded = recipe["folded_profile"]

    assert folded["station_counts"][0] == 2
    assert folded["station_date_hour_presence_counts"][0] == 11
    assert folded["represented_utc_date_counts"][0] == 10
    assert folded["station_average_support_per_utc_date"][0] == pytest.approx(
        1.1
    )
    assert folded["station_balanced_rate_pct"][0] == pytest.approx(50.0)
    assert folded["observation_level_rate_pct"][0] == pytest.approx(
        100.0 * 10.0 / 11.0
    )
    assert folded["station_success_support_per_utc_date"][0] == pytest.approx(
        0.55
    )
    assert folded["station_counter_support_per_utc_date"][0] == pytest.approx(
        0.55
    )
    _assert_temporal_stack_equivalence(folded)
    _assert_folded_station_support_equivalence(folded)


def test_success_folded_support_uses_the_unchanged_pooled_station_rate():
    """Partition corrected daily support by the established pooled-station rate."""
    peer_rows = pd.DataFrame([_peer("A", 100.0, hits=9, misses=2)])
    records = [
        {
            "time_slot": _time_slot(
                f"2026-07-10T00:{2 * report_index:02d}:00Z"
            ),
            "peer_sign": "A",
            "peer_grid": "A000",
            "hit": int(report_index < 9),
            "miss": int(report_index == 9),
            "target_snr": np.nan,
        }
        for report_index in range(10)
    ]
    records.append(
        {
            "time_slot": _time_slot("2026-07-11T00:00:00Z"),
            "peer_sign": "A",
            "peer_grid": "A000",
            "hit": 0,
            "miss": 1,
            "target_snr": np.nan,
        }
    )
    recipe = _opportunity_temporal_recipe(
        "RX Success Temporal Evidence",
        "Pooled station rate",
        peer_rows,
        pd.DataFrame.from_records(records),
        pd.Timestamp("2026-07-10T00:00:00Z"),
        pd.Timestamp("2026-07-12T00:00:00Z"),
        _presentation().absolute_terms("RX"),
        figure_labels=_figure_labels(),
    )
    folded = recipe["folded_profile"]
    expected_pooled_rate = 100.0 * 9.0 / 11.0

    assert folded["represented_utc_date_counts"][0] == 2
    assert folded["station_counts"][0] == 1
    assert folded["station_success_votes"][0] == pytest.approx(9.0 / 11.0)
    assert folded["station_counter_votes"][0] == pytest.approx(2.0 / 11.0)
    assert folded["station_balanced_rate_pct"][0] == pytest.approx(
        expected_pooled_rate
    )
    assert folded["station_date_hour_presence_counts"][0] == 2
    assert folded["station_average_support_per_utc_date"][0] == pytest.approx(
        1.0
    )
    assert folded["station_success_support_per_utc_date"][0] == pytest.approx(
        9.0 / 11.0
    )
    assert folded["station_counter_support_per_utc_date"][0] == pytest.approx(
        2.0 / 11.0
    )
    _assert_temporal_stack_equivalence(folded)
    _assert_folded_station_support_equivalence(folded)


def test_success_folded_display_denominator_clips_partial_utc_dates():
    """Count only date-hours overlapping a partial selected UTC window."""
    peer_rows = pd.DataFrame([_peer("A", 100.0, hits=3, misses=0)])
    evidence_rows = pd.DataFrame(
        [
            {
                "time_slot": _time_slot("2026-07-10T12:40:00Z"),
                "peer_sign": "A",
                "peer_grid": "A000",
                "hit": 1,
                "miss": 0,
                "target_snr": np.nan,
            },
            {
                "time_slot": _time_slot("2026-07-11T00:00:00Z"),
                "peer_sign": "A",
                "peer_grid": "A000",
                "hit": 1,
                "miss": 0,
                "target_snr": np.nan,
            },
            {
                "time_slot": _time_slot("2026-07-12T05:00:00Z"),
                "peer_sign": "A",
                "peer_grid": "A000",
                "hit": 1,
                "miss": 0,
                "target_snr": np.nan,
            },
        ]
    )
    recipe = _opportunity_temporal_recipe(
        "RX Success Temporal Evidence",
        "Partial UTC window",
        peer_rows,
        evidence_rows,
        pd.Timestamp("2026-07-10T12:30:00Z"),
        pd.Timestamp("2026-07-12T05:30:00Z"),
        _presentation().absolute_terms("RX"),
        figure_labels=_figure_labels(),
    )
    folded = recipe["folded_profile"]

    np.testing.assert_array_equal(
        folded["represented_utc_date_counts"],
        np.asarray([2] * 6 + [1] * 6 + [2] * 12, dtype=np.int64),
    )
    for utc_hour in (0, 5, 12):
        assert folded["station_success_votes"][utc_hour] == pytest.approx(1.0)
        assert folded["opportunity_success_counts"][utc_hour] == 1
        assert folded["station_date_hour_presence_counts"][utc_hour] == 1
        assert folded["station_average_support_per_utc_date"][
            utc_hour
        ] == pytest.approx(0.5)
        assert folded["station_success_support_per_utc_date"][
            utc_hour
        ] == pytest.approx(0.5)
        assert folded["station_counter_support_per_utc_date"][
            utc_hour
        ] == pytest.approx(0.0)
        assert folded["opportunity_success_counts_per_utc_date"][
            utc_hour
        ] == pytest.approx(0.5)
        assert folded["station_balanced_rate_pct"][utc_hour] == pytest.approx(
            100.0
        )
        assert folded["observation_level_rate_pct"][utc_hour] == pytest.approx(
            100.0
        )
    _assert_folded_station_support_equivalence(folded)


@pytest.mark.parametrize(
    (
        "peer_sign",
        "expected_success_vote",
        "expected_counter_vote",
        "expected_success_count",
        "expected_counter_count",
    ),
    (
        ("ALLSUCCESS", 1.0, 0.0, 2, 0),
        ("ALLCOUNTER", 0.0, 1.0, 0, 2),
        ("MIXED", 0.25, 0.75, 1, 3),
        ("PROLIFIC", 0.25, 0.75, 5, 15),
        ("SPARSE", 1.0, 0.0, 1, 0),
    ),
)
def test_success_temporal_station_vote_is_one_split_vote_per_station_bin(
    peer_sign,
    expected_success_vote,
    expected_counter_vote,
    expected_success_count,
    expected_counter_count,
):
    """Give prolific and sparse stations one split vote from their own ratio."""
    peer_rows, evidence_rows = _station_vote_contract_inputs()
    selected_peer = peer_rows[peer_rows["peer_sign"] == peer_sign].copy()
    selected_evidence = evidence_rows[
        evidence_rows["peer_sign"] == peer_sign
    ].copy()

    recipe = _station_vote_recipe_for_test(selected_peer, selected_evidence)
    first_hour = recipe["chronological_profiles"]["1h"]

    assert selected_peer.iloc[0]["opportunities"] >= 5
    assert first_hour["station_success_votes"][0] == pytest.approx(
        expected_success_vote
    )
    assert first_hour["station_counter_votes"][0] == pytest.approx(
        expected_counter_vote
    )
    assert (
        first_hour["station_success_votes"][0]
        + first_hour["station_counter_votes"][0]
    ) == pytest.approx(1.0)
    assert first_hour["opportunity_success_counts"][0] == expected_success_count
    assert first_hour["opportunity_counter_counts"][0] == expected_counter_count
    _assert_temporal_stack_equivalence(first_hour)


def test_success_temporal_votes_use_global_eligibility_without_per_bin_threshold():
    """Exclude no-evidence/ineligible peers but retain a sparse qualified vote."""
    peer_rows, evidence_rows = _station_vote_contract_inputs()
    recipe = _station_vote_recipe_for_test(peer_rows, evidence_rows)
    first_hour = recipe["chronological_profiles"]["1h"]

    # Five eligible stations contribute in this bin. NOBIN contributes no vote;
    # SPARSE contributes one despite only one in-bin opportunity; INELIGIBLE
    # contributes neither its vote nor its ten successful opportunities.
    assert first_hour["station_counts"][0] == 5
    assert first_hour["station_success_votes"][0] == pytest.approx(2.5)
    assert first_hour["station_counter_votes"][0] == pytest.approx(2.5)
    assert first_hour["opportunity_success_counts"][0] == 9
    assert first_hour["opportunity_counter_counts"][0] == 20
    assert first_hour["station_balanced_rate_pct"][0] == pytest.approx(50.0)
    assert first_hour["observation_level_rate_pct"][0] == pytest.approx(
        100.0 * 9.0 / 29.0
    )
    _assert_temporal_stack_equivalence(first_hour)

    no_bin_peer = peer_rows[peer_rows["peer_sign"] == "NOBIN"].copy()
    no_bin_rows = evidence_rows[evidence_rows["peer_sign"] == "NOBIN"].copy()
    no_bin_recipe = _station_vote_recipe_for_test(no_bin_peer, no_bin_rows)
    no_bin_first_hour = no_bin_recipe["chronological_profiles"]["1h"]
    assert no_bin_first_hour["station_counts"][0] == 0
    assert no_bin_first_hour["station_success_votes"][0] == pytest.approx(0.0)
    assert no_bin_first_hour["station_counter_votes"][0] == pytest.approx(0.0)
    assert np.isnan(no_bin_first_hour["station_balanced_rate_pct"][0])

    ineligible_peer = peer_rows[
        peer_rows["peer_sign"] == "INELIGIBLE"
    ].copy()
    ineligible_rows = evidence_rows[
        evidence_rows["peer_sign"] == "INELIGIBLE"
    ].copy()
    ineligible_recipe = _station_vote_recipe_for_test(
        ineligible_peer,
        ineligible_rows,
    )
    for profile in (
        *ineligible_recipe["chronological_profiles"].values(),
        ineligible_recipe["folded_profile"],
    ):
        assert np.sum(profile["station_success_votes"]) == pytest.approx(0.0)
        assert np.sum(profile["station_counter_votes"]) == pytest.approx(0.0)
        assert np.sum(profile["opportunity_success_counts"]) == 0
        assert np.sum(profile["opportunity_counter_counts"]) == 0
        assert np.isnan(profile["station_balanced_rate_pct"]).all()
        assert np.isnan(profile["observation_level_rate_pct"]).all()


@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("analysis_id", ["RX_ABS", "TX_ABS"])
def test_success_distance_renderer_has_localized_compare_aligned_panels(
    language,
    analysis_id,
):
    """Render exact bilingual distance panels with independent capped headroom."""
    peers = pd.DataFrame(
        [
            _peer("Z", 10.0, hits=0, misses=2),
            _peer("A", 130.0, hits=1, misses=0, successful_snr_median=-20.0),
            _peer("B", 260.0, hits=1, misses=0, successful_snr_median=-30.0),
            _peer("C", 270.0, hits=1, misses=0, successful_snr_median=-10.0),
            _peer("D", 380.0, hits=1, misses=0, successful_snr_median=-30.0),
            _peer("E", 390.0, hits=1, misses=0, successful_snr_median=-20.0),
            _peer("F", 400.0, hits=1, misses=0, successful_snr_median=-10.0),
            _peer("G", 800.0, hits=1, misses=1, successful_snr_median=-5.0),
        ]
    )
    recipe = _opportunity_segment_recipe(
        f"{analysis_id} Success Evidence",
        "Disjoint Range | All Directions",
        peers,
        pd.DataFrame(),
        None,
        None,
        _presentation(language).absolute_terms(
            "TX" if analysis_id.startswith("TX") else "RX"
        ),
        figure_labels=_figure_labels(language, analysis_id),
        distance_scope_intervals=((0.0, 500.0), (750.0, 1000.0)),
    )
    bin_count = len(recipe["distance_centers_km"])
    recipe["distance_peer_reach_pct"] = np.resize(
        np.asarray([20.0, 80.0, np.nan]),
        bin_count,
    )
    recipe["distance_station_balanced_rate_pct"] = np.resize(
        np.asarray([10.0, 50.0, np.nan]),
        bin_count,
    )
    recipe["distance_observation_level_rate_pct"] = np.resize(
        np.asarray([12.0, 40.0, np.nan]),
        bin_count,
    )

    figure = _render_opportunity_segment_figure(recipe)
    try:
        figure.canvas.draw()
        labels = recipe["labels"]
        reach_axis = next(
            axis for axis in figure.axes
            if axis.get_gid() == "success-distance-reach-axis"
        )
        consistency_axis = next(
            axis for axis in figure.axes
            if axis.get_gid() == "success-distance-consistency-axis"
        )
        snr_axis = next(
            axis for axis in figure.axes
            if axis.get_gid() == "success-distance-snr-axis"
        )
        assert len(figure.axes) == 3
        assert (
            reach_axis.get_position().x0
            < consistency_axis.get_position().x0
            < snr_axis.get_position().x0
        )
        assert all(axis.get_box_aspect() == pytest.approx(1.0) for axis in figure.axes)
        assert reach_axis.get_xlim() == pytest.approx(consistency_axis.get_xlim())
        assert reach_axis.get_xlim() == pytest.approx(snr_axis.get_xlim())
        assert reach_axis.get_ylim() == pytest.approx((0.0, 88.0))
        assert consistency_axis.get_ylim() == pytest.approx((0.0, 55.0))
        assert reach_axis.get_title().replace("\n", " ") == labels["reach_title"]
        assert (
            consistency_axis.get_title().replace("\n", " ")
            == labels["consistency_title"]
        )
        assert (
            snr_axis.get_title().replace("\n", " ")
            == labels["snr_distance_title"]
        )
        assert reach_axis.get_xlabel() == labels["distance_x"]
        assert consistency_axis.get_xlabel() == labels["distance_x"]
        assert snr_axis.get_xlabel() == labels["distance_x"]
        assert reach_axis.get_ylabel() == labels["reach_y"]
        assert consistency_axis.get_ylabel() == labels["rate_y"]
        assert snr_axis.get_ylabel() == labels["snr_y"]
        assert [
            text.get_text()
            for text in consistency_axis.get_legend().get_texts()
        ] == [
            labels["station_balanced"],
            labels["observation_level"],
        ]

        expected_gids = {
            "success-distance-peer-reach",
            "success-distance-station-balanced",
            "success-distance-observation-level",
            "success-distance-snr-median",
            "success-distance-snr-iqr",
            "success-distance-snr-two-station-range",
            "success-distance-scope-gap",
        }
        assert expected_gids.issubset(_artist_gids(figure))
        assert not {
            "success-distance-support-strip",
            "success-distance-support-count",
        }.intersection(_artist_gids(figure))

        reach_bar = next(
            patch
            for patch in reach_axis.patches
            if patch.get_gid() == "success-distance-peer-reach"
        )
        assert to_hex(reach_bar.get_facecolor()) == "#36aaf9"
        assert to_hex(reach_bar.get_edgecolor()) == "#67c4ff"
        assert reach_bar.get_alpha() == pytest.approx(0.70)
    finally:
        dispose_matplotlib_figure(figure)


@pytest.mark.parametrize("language", ["en", "de"])
@pytest.mark.parametrize("analysis_id", ["RX_ABS", "TX_ABS"])
def test_success_temporal_renderer_aligns_localized_directional_layers(
    language,
    analysis_id,
):
    """Render separate Compare-sized SNR and stacked-evidence figures."""
    recipe = _temporal_recipe_for_test(language, analysis_id)
    recipe["time_bin"] = "1h"

    compare_figure = render_segment_temporal_evidence_export_figure(
        _compare_temporal_recipe_for_test()
    )
    snr_figure = render_segment_temporal_snr_export_figure(recipe)
    evidence_figure = render_segment_temporal_evidence_export_figure(recipe)
    try:
        assert compare_figure is not None
        assert snr_figure is not None
        assert evidence_figure is not None
        compare_figure.canvas.draw()
        snr_figure.canvas.draw()
        evidence_figure.canvas.draw()
        labels = recipe["labels"]
        chronological_snr = _axis_by_gid(
            snr_figure,
            "success-temporal-snr-chronological-axis",
        )
        chronological_station = _axis_by_gid(
            evidence_figure,
            "success-temporal-station-chronological-axis",
        )
        chronological_opportunity = _axis_by_gid(
            evidence_figure,
            "success-temporal-opportunity-chronological-axis",
        )
        folded_snr = _axis_by_gid(
            snr_figure,
            "success-temporal-snr-folded-axis",
        )
        folded_station = _axis_by_gid(
            evidence_figure,
            "success-temporal-station-folded-axis",
        )
        folded_opportunity = _axis_by_gid(
            evidence_figure,
            "success-temporal-opportunity-folded-axis",
        )
        station_chronological_rate = _axis_by_gid(
            evidence_figure,
            "success-temporal-station-balanced-chronological-rate-axis",
        )
        opportunity_chronological_rate = _axis_by_gid(
            evidence_figure,
            "success-temporal-observation-level-chronological-rate-axis",
        )
        station_folded_rate = _axis_by_gid(
            evidence_figure,
            "success-temporal-station-balanced-folded-rate-axis",
        )
        opportunity_folded_rate = _axis_by_gid(
            evidence_figure,
            "success-temporal-observation-level-folded-rate-axis",
        )
        compare_chronological, compare_folded = compare_figure.axes[:2]
        chronological_header = _figure_text_by_gid(
            evidence_figure,
            "success-temporal-evidence-chronological-column-header",
        )
        folded_header = _figure_text_by_gid(
            evidence_figure,
            "success-temporal-evidence-folded-column-header",
        )
        assert [
            text.get_gid()
            for text in evidence_figure.texts
            if str(text.get_gid()).startswith(
                "success-temporal-evidence-"
            )
            and str(text.get_gid()).endswith("-column-header")
        ] == [
            "success-temporal-evidence-chronological-column-header",
            "success-temporal-evidence-folded-column-header",
        ]

        assert chronological_snr.get_title() == labels[
            "snr_chronological_title"
        ]
        assert folded_snr.get_title() == labels["snr_utc_hour_title"]
        for axis in (
            chronological_station,
            chronological_opportunity,
            folded_station,
            folded_opportunity,
        ):
            assert axis.get_title() == ""
        for axis in (
            chronological_station,
            chronological_opportunity,
        ):
            assert not any(
                str(text.get_gid()).endswith("-folded-subtitle")
                for text in axis.texts
            )
        folded_station_subtitle = next(
            text
            for text in folded_station.texts
            if text.get_gid() == "success-temporal-station-folded-subtitle"
        )
        folded_opportunity_subtitle = next(
            text
            for text in folded_opportunity.texts
            if (
                text.get_gid()
                == "success-temporal-opportunity-folded-subtitle"
            )
        )
        assert folded_station_subtitle.get_text() == labels[
            "station_support_folded_subtitle"
        ]
        assert folded_opportunity_subtitle.get_text() == labels[
            "opportunity_folded_subtitle"
        ]
        assert chronological_header.get_text() == labels[
            "evidence_chronological_title"
        ].format(time_bin="1 h")
        assert folded_header.get_text() == labels[
            "evidence_utc_hour_title"
        ]
        assert chronological_header.get_position()[1] == pytest.approx(
            folded_header.get_position()[1]
        )
        assert chronological_header.get_position()[0] == pytest.approx(
            (
                chronological_station.get_position().x0
                + chronological_station.get_position().x1
            )
            / 2.0
        )
        assert folded_header.get_position()[0] == pytest.approx(
            (
                folded_station.get_position().x0
                + folded_station.get_position().x1
            )
            / 2.0
        )
        expected_subtitles = {
            chronological_snr: labels[
                "snr_chronological_subtitle"
            ].format(time_bin="1 h"),
            folded_snr: labels["snr_utc_hour_subtitle"],
        }
        compare_title_by_success_axis = {
            chronological_snr: compare_chronological.title,
            folded_snr: compare_folded.title,
        }
        snr_renderer = snr_figure.canvas.get_renderer()
        suptitle_bounds = snr_figure._suptitle.get_window_extent(snr_renderer)
        for axis, expected_subtitle in expected_subtitles.items():
            subtitle = _panel_subtitle(axis)
            legend_text = axis.get_legend().get_texts()[0]
            compare_title = compare_title_by_success_axis[axis]
            assert subtitle.get_text() == expected_subtitle
            assert subtitle.get_fontsize() < axis.title.get_fontsize()
            assert subtitle.get_fontsize() == legend_text.get_fontsize()
            assert subtitle.get_fontweight() == legend_text.get_fontweight()
            assert subtitle.get_fontfamily() == legend_text.get_fontfamily()
            assert subtitle.get_fontstyle() == legend_text.get_fontstyle()
            assert axis.title.get_fontsize() == compare_title.get_fontsize()
            assert axis.title.get_fontweight() == compare_title.get_fontweight()
            assert axis.title.get_color() == compare_title.get_color()
            assert axis.title.get_fontfamily() == compare_title.get_fontfamily()
            assert (
                axis.title.get_fontsize()
                < snr_figure._suptitle.get_fontsize()
            )
            title_bounds = axis.title.get_window_extent(snr_renderer)
            subtitle_bounds = subtitle.get_window_extent(snr_renderer)
            figure_to_title_gap = suptitle_bounds.y0 - title_bounds.y1
            title_to_subtitle_gap = (
                title_bounds.y0 - subtitle_bounds.y1
            )
            assert figure_to_title_gap > title_to_subtitle_gap >= 0.0

        for header, compare_title in (
            (chronological_header, compare_chronological.title),
            (folded_header, compare_folded.title),
        ):
            assert header.get_fontsize() == compare_title.get_fontsize()
            assert header.get_fontweight() == compare_title.get_fontweight()
            assert header.get_color() == compare_title.get_color()
            assert header.get_fontfamily() == compare_title.get_fontfamily()
            assert header.get_ha() == "center"

        np.testing.assert_allclose(
            snr_figure.get_size_inches(),
            compare_figure.get_size_inches(),
        )
        np.testing.assert_allclose(
            evidence_figure.get_size_inches(),
            compare_figure.get_size_inches(),
        )
        assert len(compare_figure.axes) == 3
        assert len(snr_figure.axes) == 3
        assert len(evidence_figure.axes) == 8
        for success_axis, compare_axis in (
            (chronological_snr, compare_chronological),
            (folded_snr, compare_folded),
        ):
            assert success_axis.get_position().bounds == pytest.approx(
                compare_axis.get_position().bounds
            )
        assert chronological_snr.get_position().width > folded_snr.get_position().width
        assert chronological_snr.get_position().x0 < folded_snr.get_position().x0
        assert (
            chronological_station.get_position().y0
            > chronological_opportunity.get_position().y0
        )
        assert (
            folded_station.get_position().y0
            > folded_opportunity.get_position().y0
        )
        assert chronological_station.get_position().x0 < folded_station.get_position().x0
        assert chronological_station.get_position().width > folded_station.get_position().width
        for count_axis, rate_axis in (
            (chronological_station, station_chronological_rate),
            (chronological_opportunity, opportunity_chronological_rate),
            (folded_station, station_folded_rate),
            (folded_opportunity, opportunity_folded_rate),
        ):
            assert rate_axis.get_position().bounds == pytest.approx(
                count_axis.get_position().bounds
            )
        expected_evidence_title = (
            f"{_SUCCESS_DIRECTION_FIGURE_LABELS[(language, analysis_id)]['evidence_title'].format(callsign='G3ZIL')}"
            " — Full Range | All Directions"
        )
        expected_snr_title = (
            f"{_SUCCESS_DIRECTION_FIGURE_LABELS[(language, analysis_id)]['snr_title'].format(callsign='G3ZIL')}"
            " — Full Range | All Directions"
        )
        assert snr_figure._suptitle.get_text().strip() == expected_snr_title
        assert (
            evidence_figure._suptitle.get_text().strip()
            == expected_evidence_title
        )
        assert expected_snr_title != expected_evidence_title
        for success_suptitle in (
            snr_figure._suptitle,
            evidence_figure._suptitle,
        ):
            assert success_suptitle.get_fontsize() == (
                compare_figure._suptitle.get_fontsize()
            )
            assert success_suptitle.get_fontweight() == (
                compare_figure._suptitle.get_fontweight()
            )
            assert success_suptitle.get_color() == (
                compare_figure._suptitle.get_color()
            )
            assert success_suptitle.get_position()[1] == pytest.approx(
                compare_figure._suptitle.get_position()[1]
            )
        assert chronological_snr.get_ylabel() == labels["snr_anomaly_y"]
        assert folded_snr.get_ylabel() == labels["snr_anomaly_y"]
        assert chronological_station.get_ylabel() == labels["station_vote_y"]
        assert folded_station.get_ylabel() == labels["station_vote_y"]
        assert labels["station_support_folded_y"] == labels["station_vote_y"]
        assert chronological_opportunity.get_ylabel() == labels["opportunity_y"]
        assert folded_opportunity.get_ylabel() == labels["opportunity_y"]
        assert labels["opportunity_folded_y"] == labels["opportunity_y"]
        assert chronological_station.get_xlabel() == ""
        assert folded_station.get_xlabel() == ""
        assert chronological_opportunity.get_xlabel() == labels["time_x"]
        assert folded_opportunity.get_xlabel() == labels["utc_hour_x"]

        assert [
            text.get_text()
            for text in chronological_snr.get_legend().get_texts()
        ] == [
            labels["station_baseline"],
            labels["bin_median_chronological"],
        ]
        assert [
            text.get_text()
            for text in folded_snr.get_legend().get_texts()
        ] == [
            labels["station_baseline"],
            labels["bin_median_folded"],
        ]

        evidence_legends = [
            *evidence_figure.legends,
            *[
                legend
                for axis in evidence_figure.axes
                if (legend := axis.get_legend()) is not None
            ],
        ]
        assert len(evidence_legends) == 1
        evidence_legend_labels = [
            text.get_text() for text in evidence_legends[0].get_texts()
        ]
        assert evidence_legend_labels == [
            labels["target_evidence"],
            labels["counter_evidence"],
            labels["rate_legend"],
        ]
        assert evidence_figure.legends == evidence_legends
        assert evidence_legends[0].get_gid() == (
            "success-temporal-outcome-legend"
        )
        assert evidence_legends[0]._ncols == 3
        assert evidence_legends[0].get_bbox_to_anchor()._bbox.x0 == (
            pytest.approx(0.5)
        )
        assert evidence_legends[0].get_bbox_to_anchor()._bbox.y0 == (
            pytest.approx(0.895)
        )
        evidence_renderer = evidence_figure.canvas.get_renderer()
        evidence_suptitle_bounds = (
            evidence_figure._suptitle.get_window_extent(evidence_renderer)
        )
        evidence_legend_bounds = evidence_legends[0].get_window_extent(
            evidence_renderer
        )
        header_bounds = [
            header.get_window_extent(evidence_renderer)
            for header in (chronological_header, folded_header)
        ]
        top_axis_bounds = [
            axis.get_window_extent(evidence_renderer)
            for axis in (chronological_station, folded_station)
        ]
        folded_station_subtitle_bounds = (
            folded_station_subtitle.get_window_extent(evidence_renderer)
        )
        folded_opportunity_subtitle_bounds = (
            folded_opportunity_subtitle.get_window_extent(evidence_renderer)
        )
        assert evidence_suptitle_bounds.y0 > evidence_legend_bounds.y1
        assert evidence_legend_bounds.y0 > max(
            bounds.y1 for bounds in header_bounds
        )
        assert min(bounds.y0 for bounds in header_bounds) > max(
            bounds.y1 for bounds in top_axis_bounds
        )
        assert (
            folded_header.get_window_extent(evidence_renderer).y0
            > folded_station_subtitle_bounds.y1
            >= folded_station.get_window_extent(evidence_renderer).y1
        )
        assert folded_opportunity_subtitle_bounds.y0 == pytest.approx(
            folded_opportunity.get_window_extent(evidence_renderer).y1
        )
        assert (
            folded_station.get_window_extent(evidence_renderer).y0
            > folded_opportunity_subtitle_bounds.y1
        )
        assert labels["utc_dates_folded"].format(count=2) in {
            text.get_text() for text in folded_snr.texts
        }
        assert labels["utc_dates_folded"].format(count=2) in {
            text.get_text() for text in folded_station.texts
        }
        assert not {
            "Target",
            "Elsewhere",
            "Other Signals",
        }.intersection(evidence_legend_labels)

        for axis in (
            chronological_station,
            chronological_opportunity,
            folded_station,
            folded_opportunity,
        ):
            facecolors = {
                to_hex(patch.get_facecolor()) for patch in axis.patches
            }
            assert "#39ff14" in facecolors
            assert "#858585" in facecolors
            assert "#36aaf9" not in facecolors
            assert not axis.lines
            assert axis.yaxis.get_major_formatter()(6_400, 0) == "6k4"
        assert {
            patch.get_gid() for patch in chronological_station.patches
        } == {
            "success-temporal-station-vote-success",
            "success-temporal-station-vote-counter",
        }
        assert {
            patch.get_gid() for patch in folded_station.patches
        } == {
            "success-temporal-station-support-success",
            "success-temporal-station-support-counter",
        }

        def bar_geometry(axis, facecolor):
            """Return ordered x/width geometry for one stack color."""
            return [
                (patch.get_x(), patch.get_width())
                for patch in axis.patches
                if to_hex(patch.get_facecolor()) == facecolor
            ]

        np.testing.assert_allclose(
            bar_geometry(chronological_station, "#39ff14"),
            bar_geometry(chronological_opportunity, "#39ff14"),
        )
        np.testing.assert_allclose(
            bar_geometry(folded_station, "#39ff14"),
            bar_geometry(folded_opportunity, "#39ff14"),
        )

        def bar_heights(axis, facecolor):
            """Return ordered stacked-bar heights for one outcome color."""
            return [
                patch.get_height()
                for patch in axis.patches
                if to_hex(patch.get_facecolor()) == facecolor
            ]

        folded_profile = recipe["folded_profile"]
        np.testing.assert_allclose(
            bar_heights(folded_station, "#39ff14"),
            folded_profile["station_success_support_per_utc_date"],
        )
        np.testing.assert_allclose(
            bar_heights(folded_station, "#858585"),
            folded_profile["station_counter_support_per_utc_date"],
        )
        np.testing.assert_allclose(
            bar_heights(folded_opportunity, "#39ff14"),
            folded_profile["opportunity_success_counts_per_utc_date"],
        )
        np.testing.assert_allclose(
            bar_heights(folded_opportunity, "#858585"),
            folded_profile["opportunity_counter_counts_per_utc_date"],
        )

        chronological_profile = recipe["chronological_profiles"]["1h"]
        rate_axes = (
            (
                station_chronological_rate,
                "success-temporal-station-balanced-chronological-rate",
                chronological_profile["station_balanced_rate_pct"],
            ),
            (
                opportunity_chronological_rate,
                "success-temporal-observation-level-chronological-rate",
                chronological_profile["observation_level_rate_pct"],
            ),
            (
                station_folded_rate,
                "success-temporal-station-balanced-folded-rate",
                folded_profile["station_balanced_rate_pct"],
            ),
            (
                opportunity_folded_rate,
                "success-temporal-observation-level-folded-rate",
                folded_profile["observation_level_rate_pct"],
            ),
        )
        expected_rate_upper_limit = _success_temporal_rate_axis_max(
            *(expected_rates for _, _, expected_rates in rate_axes)
        )
        for rate_axis, expected_gid, expected_rates in rate_axes:
            assert rate_axis.get_ylabel() == labels["rate_y"]
            assert rate_axis.get_ylim() == pytest.approx(
                (0.0, expected_rate_upper_limit)
            )
            assert len(rate_axis.lines) == 1
            rate_line = rate_axis.lines[0]
            assert rate_line.get_gid() == expected_gid
            assert rate_line.get_label() == labels["rate_legend"]
            assert to_hex(rate_line.get_color()) == "#c8f4ff"
            assert rate_line.get_marker() == "o"
            assert rate_line.get_linewidth() == pytest.approx(1.2)
            np.testing.assert_allclose(
                rate_line.get_ydata(),
                expected_rates,
                equal_nan=True,
            )

        expected_snr_gids = {
            "success-temporal-snr-density",
            "success-temporal-snr-baseline",
            "success-temporal-snr-bin-median",
        }
        assert expected_snr_gids.issubset(_artist_gids(snr_figure))
        expected_rate_gids = {
            expected_gid for _, expected_gid, _ in rate_axes
        }
        assert expected_rate_gids.issubset(_artist_gids(evidence_figure))
        superseded_gids = {
            "success-temporal-station-balanced",
            "success-temporal-observation-level",
            "success-temporal-station-count",
            "success-temporal-utc-date-count",
        }
        assert not superseded_gids.intersection(_artist_gids(evidence_figure))
        assert not any(
            axis.get_gid() == "success-temporal-snr-colorbar-axis"
            for axis in evidence_figure.axes
        )
        assert any(
            axis.yaxis.label.get_text() == labels["snr_density"]
            for axis in snr_figure.axes
        )
    finally:
        if compare_figure is not None:
            dispose_matplotlib_figure(compare_figure)
        if snr_figure is not None:
            dispose_matplotlib_figure(snr_figure)
        if evidence_figure is not None:
            dispose_matplotlib_figure(evidence_figure)


def test_success_temporal_count_axes_scale_independently_for_six_hour_bins():
    """Keep unlike count units independent while sharing rate-axis limits."""
    recipe = _temporal_recipe_for_test()
    recipe["time_bin"] = "6h"
    figure = render_segment_temporal_evidence_export_figure(recipe)
    try:
        assert figure is not None
        figure.canvas.draw()
        station_chronological = _axis_by_gid(
            figure,
            "success-temporal-station-chronological-axis",
        )
        station_folded = _axis_by_gid(
            figure,
            "success-temporal-station-folded-axis",
        )
        opportunity_chronological = _axis_by_gid(
            figure,
            "success-temporal-opportunity-chronological-axis",
        )
        opportunity_folded = _axis_by_gid(
            figure,
            "success-temporal-opportunity-folded-axis",
        )

        for chronological_axis, folded_axis in (
            (station_chronological, station_folded),
            (opportunity_chronological, opportunity_folded),
        ):
            assert not chronological_axis.get_shared_y_axes().joined(
                chronological_axis,
                folded_axis,
            )
            assert chronological_axis.get_ylim() != pytest.approx(
                folded_axis.get_ylim()
            )
            for count in (850, 6_400, 12_500, 100_000, 6_800_000):
                assert chronological_axis.yaxis.get_major_formatter()(
                    count,
                    0,
                ) == folded_axis.yaxis.get_major_formatter()(count, 0)
            assert abs(
                len(chronological_axis.get_yticks())
                - len(folded_axis.get_yticks())
            ) <= 2

        rate_axes = [
            axis
            for axis in figure.axes
            if str(axis.get_gid()).endswith("-rate-axis")
        ]
        assert len(rate_axes) == 4
        for rate_axis in rate_axes:
            assert rate_axis.get_ylim() == pytest.approx(
                rate_axes[0].get_ylim()
            )
    finally:
        if figure is not None:
            dispose_matplotlib_figure(figure)


def test_success_temporal_export_uses_full_width_chronology_for_one_date():
    """Both one-date figures expand chronology and omit folded UTC panels."""
    rows = _temporal_evidence_rows()
    rows = rows[
        rows["time_slot"] < _time_slot("2026-07-11T00:00:00Z")
    ].copy()
    recipe = _temporal_recipe_for_test(
        rows=rows,
        end_t="2026-07-11T00:00:00Z",
    )
    recipe["time_bin"] = "1h"

    snr_figure = render_segment_temporal_snr_export_figure(recipe)
    evidence_figure = render_segment_temporal_evidence_export_figure(recipe)
    try:
        assert snr_figure is not None
        assert evidence_figure is not None
        snr_figure.canvas.draw()
        evidence_figure.canvas.draw()
        labels = recipe["labels"]
        chronological_snr = _axis_by_gid(
            snr_figure,
            "success-temporal-snr-chronological-axis",
        )
        chronological_station = _axis_by_gid(
            evidence_figure,
            "success-temporal-station-chronological-axis",
        )
        chronological_opportunity = _axis_by_gid(
            evidence_figure,
            "success-temporal-opportunity-chronological-axis",
        )
        station_rate_axis = _axis_by_gid(
            evidence_figure,
            "success-temporal-station-balanced-chronological-rate-axis",
        )
        opportunity_rate_axis = _axis_by_gid(
            evidence_figure,
            "success-temporal-observation-level-chronological-rate-axis",
        )
        chronological_header = _figure_text_by_gid(
            evidence_figure,
            "success-temporal-evidence-chronological-column-header",
        )

        assert recipe["utc_date_count"] == 1
        assert chronological_snr.get_position().width > 0.80
        assert chronological_station.get_position().width > 0.80
        assert chronological_opportunity.get_position().width > 0.80
        assert len(snr_figure.axes) == 2
        assert len(evidence_figure.axes) == 4
        assert chronological_snr.get_title() == labels[
            "snr_chronological_title"
        ]
        for axis in (
            chronological_station,
            chronological_opportunity,
        ):
            assert axis.get_title() == ""
            assert not any(
                text.get_gid() == "success-temporal-panel-subtitle"
                for text in axis.texts
            )
        assert _panel_subtitle(chronological_snr).get_text() == labels[
            "snr_chronological_subtitle"
        ].format(time_bin="1 h")
        assert chronological_header.get_text() == labels[
            "evidence_chronological_title"
        ].format(time_bin="1 h")
        assert chronological_header.get_position()[0] == pytest.approx(
            (
                chronological_station.get_position().x0
                + chronological_station.get_position().x1
            )
            / 2.0
        )
        assert not any(
            text.get_gid()
            == "success-temporal-evidence-folded-column-header"
            for text in evidence_figure.texts
        )
        for count_axis, rate_axis in (
            (chronological_station, station_rate_axis),
            (chronological_opportunity, opportunity_rate_axis),
        ):
            assert rate_axis.get_ylabel() == labels["rate_y"]
            assert rate_axis.get_ylim()[0] == pytest.approx(0.0)
            assert len(rate_axis.lines) == 1
            assert rate_axis.get_position().bounds == pytest.approx(
                count_axis.get_position().bounds
            )
            assert count_axis.get_position().x0 == pytest.approx(
                chronological_snr.get_position().x0
            )
            assert count_axis.get_position().x1 == pytest.approx(
                chronological_snr.get_position().x1
            )
        assert any(
            text.get_text() == labels["temporal_unavailable"]
            for text in chronological_snr.texts
        )
        assert not any(
            axis.get_gid() == "success-temporal-snr-folded-axis"
            for axis in snr_figure.axes
        )
        assert not any(
            axis.get_gid()
            in {
                "success-temporal-station-folded-axis",
                "success-temporal-opportunity-folded-axis",
                "success-temporal-station-balanced-folded-rate-axis",
                "success-temporal-observation-level-folded-rate-axis",
            }
            for axis in evidence_figure.axes
        )
    finally:
        if snr_figure is not None:
            dispose_matplotlib_figure(snr_figure)
        if evidence_figure is not None:
            dispose_matplotlib_figure(evidence_figure)


def test_success_temporal_lower_data_columns_match_upper_snr_axes():
    """Align lower data axes exactly while excluding the upper colorbar gutter."""
    success_recipe = _temporal_recipe_for_test()
    snr_figure = render_segment_temporal_snr_export_figure(success_recipe)
    evidence_figure = render_segment_temporal_evidence_export_figure(
        success_recipe
    )
    try:
        snr_figure.canvas.draw()
        evidence_figure.canvas.draw()
        snr_chronological = next(
            axis
            for axis in snr_figure.axes
            if axis.get_gid()
            == "success-temporal-snr-chronological-axis"
        )
        snr_folded = next(
            axis
            for axis in snr_figure.axes
            if axis.get_gid() == "success-temporal-snr-folded-axis"
        )
        snr_colorbar = _axis_by_gid(
            snr_figure,
            "success-temporal-snr-colorbar-axis",
        )
        station_chronological = next(
            axis
            for axis in evidence_figure.axes
            if axis.get_gid()
            == "success-temporal-station-chronological-axis"
        )
        station_folded = next(
            axis
            for axis in evidence_figure.axes
            if axis.get_gid()
            == "success-temporal-station-folded-axis"
        )
        opportunity_chronological = next(
            axis
            for axis in evidence_figure.axes
            if axis.get_gid()
            == "success-temporal-opportunity-chronological-axis"
        )
        opportunity_folded = next(
            axis
            for axis in evidence_figure.axes
            if axis.get_gid()
            == "success-temporal-opportunity-folded-axis"
        )
        station_chronological_rate = _axis_by_gid(
            evidence_figure,
            "success-temporal-station-balanced-chronological-rate-axis",
        )
        opportunity_chronological_rate = _axis_by_gid(
            evidence_figure,
            "success-temporal-observation-level-chronological-rate-axis",
        )
        station_folded_rate = _axis_by_gid(
            evidence_figure,
            "success-temporal-station-balanced-folded-rate-axis",
        )
        opportunity_folded_rate = _axis_by_gid(
            evidence_figure,
            "success-temporal-observation-level-folded-rate-axis",
        )

        for lower_axis in (
            station_chronological,
            opportunity_chronological,
        ):
            assert lower_axis.get_position().x0 == pytest.approx(
                snr_chronological.get_position().x0
            )
            assert lower_axis.get_position().x1 == pytest.approx(
                snr_chronological.get_position().x1
            )
        for lower_axis in (station_folded, opportunity_folded):
            assert lower_axis.get_position().x0 == pytest.approx(
                snr_folded.get_position().x0
            )
            assert lower_axis.get_position().x1 == pytest.approx(
                snr_folded.get_position().x1
            )
        assert snr_folded.get_position().x1 < snr_colorbar.get_position().x0
        assert (
            station_folded.get_position().x0
            > station_chronological.get_position().x1
        )
        for count_axis, rate_axis in (
            (station_chronological, station_chronological_rate),
            (opportunity_chronological, opportunity_chronological_rate),
            (station_folded, station_folded_rate),
            (opportunity_folded, opportunity_folded_rate),
        ):
            assert rate_axis.get_position().bounds == pytest.approx(
                count_axis.get_position().bounds
            )

        panel_heights = [
            axis.get_position().height
            for axis in (
                station_chronological,
                opportunity_chronological,
                station_folded,
                opportunity_folded,
            )
        ]
        assert panel_heights == pytest.approx([panel_heights[0]] * 4)
    finally:
        dispose_matplotlib_figure(snr_figure)
        dispose_matplotlib_figure(evidence_figure)


@pytest.mark.parametrize(
    (
        "language",
        "analysis_id",
        "expected_snr_title",
        "expected_temporal_title",
        "expected_context",
        "expected_station_instruction",
        "expected_transition",
    ),
    (
        (
            "en",
            "RX_ABS",
            "RX Success Selected Station SNR Evidence: OK1FCX (JN79)",
            "RX Success Selected Station Temporal Evidence: OK1FCX (JN79)",
            "OK1FCX (JN79) · 1,173 km · 91° E · 13,019 confirmed opportunities · Success Rate 47.6% · Median successful Target SNR −15.0 dB",
            "Contributing TX stations in the active scope. Select one row to inspect its evidence.",
            "↓ Select one station to inspect its evidence",
        ),
        (
            "de",
            "TX_ABS",
            "TX Success — SNR-Evidenz der ausgewählten Station: OK1FCX (JN79)",
            "TX Success — Zeitliche Evidenz der ausgewählten Station: OK1FCX (JN79)",
            "OK1FCX (JN79) · 1.173 km · 91° O · 13.019 bestätigte Gelegenheiten · Success Rate 47,6% · Median des erfolgreichen Target-SNR −15,0 dB",
            "Beitragende RX-Stationen im aktiven Bereich. Wähle eine Zeile, um ihre Evidenz zu untersuchen.",
            "↓ Wähle eine Station, um ihre Evidenz zu untersuchen",
        ),
    ),
)
def test_selected_success_titles_context_and_singleton_copy_are_exact(
    language,
    analysis_id,
    expected_snr_title,
    expected_temporal_title,
    expected_context,
    expected_station_instruction,
    expected_transition,
):
    """Keep approved singleton copy exact across the English and German paths."""
    translations = T[language]
    station_type = "TX" if analysis_id.startswith("RX") else "RX"
    recipe = {
        "selected_station_summary": {
            "peer_sign": "OK1FCX",
            "peer_grid": "JN79",
            "distance_km": 1173.2,
            "azimuth_degrees": 91.2,
            "direction": "E",
            "confirmed_opportunities": 13019,
            "success_rate_pct": 47.6,
            "successful_snr_median_db": -15.0,
        }
    }

    assert _selected_success_temporal_figure_title(
        "OK1FCX",
        "JN79",
        analysis_id,
        translations,
        figure_kind="snr",
    ) == expected_snr_title
    assert _selected_success_temporal_figure_title(
        "OK1FCX",
        "JN79",
        analysis_id,
        translations,
        figure_kind="evidence",
    ) == expected_temporal_title
    assert _selected_success_context_line(
        recipe,
        translations,
    ) == expected_context
    assert translations["sub_results_station_insights_success"].format(
        station_type=station_type
    ) == expected_station_instruction
    assert (
        translations["txt_results_transition_stations_success"]
        == expected_transition
    )


@pytest.mark.parametrize("language", ("en", "de"))
def test_selected_success_actual_snr_labels_retire_anomaly_wording(language):
    """Expose actual normalized SNR labels without station-centering language."""
    labels = _success_figure_labels(T[language], "RX_ABS")

    assert labels["selected_snr_y"] == T[language][
        "fig_success_selected_temporal_snr_y"
    ]
    selected_copy = " ".join(
        str(labels[key])
        for key in (
            "selected_snr_chronological_title",
            "selected_snr_chronological_subtitle",
            "selected_snr_utc_hour_title",
            "selected_snr_utc_hour_subtitle",
            "selected_snr_y",
            "selected_snr_density",
            "selected_snr_unavailable",
        )
    )
    assert "run median" not in selected_copy
    assert "Laufmedian" not in selected_copy
    assert "deviation" not in selected_copy.lower()
    assert "Abweichung" not in selected_copy


def test_selected_success_context_uses_em_dash_when_snr_is_unavailable():
    """Do not synthesize a selected-path SNR when no successful value exists."""
    context = _selected_success_context_line(
        {
            "selected_station_summary": {
                "peer_sign": "A",
                "peer_grid": "AA00",
                "distance_km": 100.0,
                "azimuth_degrees": 0.0,
                "direction": "N",
                "confirmed_opportunities": 3,
                "success_rate_pct": 0.0,
                "successful_snr_median_db": np.nan,
            }
        },
        T["en"],
    )

    assert context.endswith("Median successful Target SNR —")
