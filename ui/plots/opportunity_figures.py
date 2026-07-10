"""Opportunity evidence figures for WSPRadar."""

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.dates as mdates
import streamlit as st

from config import APP_VERSION
from core.matplotlib_runtime import create_agg_figure, synchronized_matplotlib
from core.opportunity_engine import (
    opportunity_rate_scale_max,
    SUCCESS_RATE_BOUNDS,
    SUCCESS_RATE_COLORS,
    SUCCESS_RATE_TICK_LABELS,
)
from core.solar_path import (
    ILLUMINATION_CLASSES,
    ILLUMINATION_DAYLIGHT,
    ILLUMINATION_DISPLAY_LABELS,
    ILLUMINATION_GREYLINE_MIXED,
    ILLUMINATION_NIGHT,
)
from i18n import T, absolute_terms
from ui.plots.evidence_figures import (
    SEGMENT_FIGURE_FOOTER_Y,
    _draw_stacked_vertical_metric_histogram,
    _style_evidence_axis,
    _time_agg_minutes,
)

ILLUMINATION_TARGET_COLORS = {
    ILLUMINATION_NIGHT: "#0b5d1e",
    ILLUMINATION_GREYLINE_MIXED: "#39ff14",
    ILLUMINATION_DAYLIGHT: "#a8ff8a",
}
ILLUMINATION_COUNTER_COLORS = {
    ILLUMINATION_NIGHT: "#4a4a4a",
    ILLUMINATION_GREYLINE_MIXED: "#858585",
    ILLUMINATION_DAYLIGHT: "#c8c8c8",
}

def _opportunity_time_bin(rows, analysis_start_t=None, analysis_end_t=None):
    """Choose a readable fixed UTC bin for opportunity-rate evidence."""
    if analysis_start_t is not None and analysis_end_t is not None:
        span = _as_utc_timestamp(analysis_end_t) - _as_utc_timestamp(analysis_start_t)
    else:
        if rows.empty:
            return "3h"
        times = pd.to_datetime(rows["cycle_time"], errors="coerce", utc=True).dropna()
        if times.empty:
            return "3h"
        span = times.max() - times.min()
    if span <= pd.Timedelta(days=1):
        return "1h"
    if span <= pd.Timedelta(days=7):
        return "3h"
    return "12h"

def _as_utc_timestamp(value):
    """Normalize a datetime-like value to a timezone-aware UTC Timestamp."""
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")

def _assign_fixed_time_bins(rows, start_t, end_t, bin_minutes):
    """Assign rows to contiguous bins anchored at the analysis start time."""
    start = _as_utc_timestamp(start_t)
    end = _as_utc_timestamp(end_t)
    delta = pd.Timedelta(minutes=int(bin_minutes))
    if end <= start:
        return rows.iloc[0:0].copy(), pd.DatetimeIndex([])

    bin_count = int(np.ceil((end - start) / delta))
    time_bins = pd.DatetimeIndex(
        [start + (index * delta) for index in range(bin_count)]
    )
    work = rows.copy()
    work["cycle_time"] = pd.to_datetime(work["cycle_time"], errors="coerce", utc=True)
    work = work[
        work["cycle_time"].notna() &
        work["cycle_time"].ge(start) &
        work["cycle_time"].lt(end)
    ].copy()
    if work.empty:
        work["time_bin"] = pd.Series(dtype="datetime64[ns, UTC]")
        return work, time_bins

    bin_index = ((work["cycle_time"] - start) // delta).astype(int)
    work["time_bin"] = start + (bin_index * delta)
    return work, time_bins

def _opportunity_segment_recipe(
    title,
    selected_segment,
    peer_df,
    rows,
    analysis_start_t,
    analysis_end_t,
    terminology,
):
    """Build compact Target/Elsewhere success-rate plot inputs for UI and lazy export."""
    time_bin = _opportunity_time_bin(rows, analysis_start_t, analysis_end_t)
    bin_minutes = _time_agg_minutes(time_bin)
    work = rows.merge(
        peer_df[["peer_sign", "peer_grid", "dist_label", "eligible"]],
        on=["peer_sign", "peer_grid"],
        how="inner",
    )
    work = work[work["eligible"]].copy()
    work, time_bins = _assign_fixed_time_bins(
        work,
        analysis_start_t,
        analysis_end_t,
        bin_minutes,
    )

    range_labels = sorted(
        peer_df["dist_label"].dropna().unique().tolist(),
        key=lambda value: int(str(value).strip("[]km").split("-")[0]),
    )
    station_rate_grid = np.full((len(range_labels), len(time_bins)), np.nan, dtype=float)
    overall_rate_grid = np.full((len(range_labels), len(time_bins)), np.nan, dtype=float)

    if range_labels and len(time_bins):
        station_bins = (
            work.groupby(
                ["dist_label", "time_bin", "peer_sign", "peer_grid"],
                dropna=False,
            )
            .agg(hits=("hit", "sum"), misses=("miss", "sum"))
            .reset_index()
        )
        station_bins["trials"] = station_bins["hits"] + station_bins["misses"]
        station_bins = station_bins[station_bins["trials"] > 0]
        station_bins["rate_pct"] = (
            100.0 * station_bins["hits"] / station_bins["trials"]
        )
        cells = (
            station_bins.groupby(["dist_label", "time_bin"], dropna=False)
            .agg(
                station_rate_pct=("rate_pct", "mean"),
                hits=("hits", "sum"),
                misses=("misses", "sum"),
            )
            .reset_index()
        )
        cells["overall_rate_pct"] = np.where(
            (cells["hits"] + cells["misses"]) > 0,
            100.0 * cells["hits"] / (cells["hits"] + cells["misses"]),
            np.nan,
        )
        range_index = {label: index for index, label in enumerate(range_labels)}
        time_index = {pd.Timestamp(value): index for index, value in enumerate(time_bins)}
        for row in cells.itertuples(index=False):
            y = range_index.get(row.dist_label)
            x = time_index.get(pd.Timestamp(row.time_bin))
            if y is None or x is None:
                continue
            station_rate_grid[y, x] = float(row.station_rate_pct)
            overall_rate_grid[y, x] = float(row.overall_rate_pct)

    return {
        "kind": "opportunity",
        "title": title,
        "absolute_mode": terminology.get("mode", "RX"),
        "terminology": dict(terminology),
        "selected_segment": selected_segment,
        "time_bin": time_bin,
        "station_trials": peer_df["opportunities"].to_numpy(dtype=float, copy=True),
        "station_hits": peer_df["hits"].to_numpy(dtype=float, copy=True),
        "station_rates": peer_df["rate_pct"].to_numpy(dtype=float, copy=True),
        "minimum_trials": int(st.session_state.get("val_min_opportunities", 5)),
        "range_labels": list(range_labels),
        "time_ns": time_bins.to_numpy(dtype="datetime64[ns]").astype(np.int64, copy=True),
        "station_rate_grid": station_rate_grid,
        "overall_rate_grid": overall_rate_grid,
    }

def _draw_opportunity_heatmap(
    ax,
    grid,
    range_labels,
    time_values,
    title,
    cbar_label,
    cmap,
    vmin=None,
    vmax=None,
    norm=None,
    cbar_ticks=None,
    cbar_ticklabels=None,
    show_y_labels=True,
    show_colorbar=True,
    empty_message="No Target/Elsewhere evidence",
):
    ax.set_facecolor("black")
    ax.tick_params(colors="white", labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#444444")
    ax.set_title(title, color="white", fontweight="bold", fontsize=12, pad=9)
    if grid.size == 0 or not range_labels or len(time_values) == 0:
        ax.text(0.5, 0.5, empty_message, color="#cccccc", ha="center", va="center", transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        return None

    masked = np.ma.masked_invalid(np.asarray(grid, dtype=float))
    image_kwargs = {
        "origin": "lower",
        "aspect": "auto",
        "interpolation": "nearest",
        "cmap": cmap,
    }
    if norm is not None:
        image_kwargs["norm"] = norm
    else:
        image_kwargs["vmin"] = vmin
        image_kwargs["vmax"] = vmax
    image = ax.imshow(masked, **image_kwargs)
    if show_y_labels:
        distance_boundaries = []
        for label in range_labels:
            try:
                upper_km = int(str(label).strip("[]km").split("-")[1])
                distance_boundaries.append(f"{upper_km} km")
            except (IndexError, TypeError, ValueError):
                distance_boundaries.append(str(label))
        ax.set_yticks(np.arange(len(range_labels), dtype=float) + 0.5)
        ax.set_yticklabels(distance_boundaries, color="white", fontsize=9)
        for boundary in np.arange(len(range_labels), dtype=float) + 0.5:
            ax.axhline(boundary, color="#777777", linewidth=0.8, alpha=0.30)
    else:
        ax.tick_params(axis="y", left=False, labelleft=False)
    tick_indices = _opportunity_time_tick_indices(time_values)
    ax.set_xticks(tick_indices)
    ax.set_xticklabels(
        [pd.Timestamp(time_values[index]).strftime("%d-%b\n%H:%M") for index in tick_indices],
        color="white",
        fontsize=9,
    )
    if show_colorbar:
        cbar = ax.figure.colorbar(
            image,
            ax=ax,
            pad=0.015,
            fraction=0.04,
            ticks=cbar_ticks,
            spacing="uniform",
        )
        if cbar_ticklabels is not None:
            cbar.ax.set_yticklabels(cbar_ticklabels)
        cbar.set_label(cbar_label, color="white", fontsize=9)
        cbar.ax.tick_params(colors="white", labelsize=9)
    return image

def _opportunity_time_tick_indices(time_values):
    """Return clock-stable, equidistant time ticks anchored at analysis start."""
    time_index = pd.DatetimeIndex(time_values)
    bin_count = len(time_index)
    if bin_count <= 8:
        return np.arange(bin_count, dtype=int)

    bin_delta = time_index[1] - time_index[0]
    bin_minutes = max(1, int(round(bin_delta / pd.Timedelta(minutes=1))))
    interval_minutes = (
        60,
        120,
        180,
        240,
        360,
        480,
        720,
        1440,
        2880,
        4320,
        5760,
        7200,
        10080,
    )
    candidates = []
    for interval in interval_minutes:
        if interval < bin_minutes or interval % bin_minutes:
            continue
        stride = interval // bin_minutes
        label_count = ((bin_count - 1) // stride) + 1
        if 6 <= label_count <= 10:
            range_penalty = 0
        else:
            range_penalty = min(abs(label_count - 6), abs(label_count - 10))
        candidates.append((range_penalty, abs(label_count - 8), stride))

    if candidates:
        stride = min(candidates)[2]
    else:
        stride = max(1, int(np.ceil((bin_count - 1) / 7)))
    return np.arange(0, bin_count, stride, dtype=int)

@synchronized_matplotlib
def _render_opportunity_segment_figure(recipe):
    terms = recipe.get("terminology") or absolute_terms(
        T.get(st.session_state.get("lang", "en"), T["en"]),
        recipe.get("absolute_mode", "RX"),
    )
    fig = create_agg_figure(figsize=(13, 7.2), facecolor="black")
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.12, top=0.84, hspace=0.42, wspace=0.10)
    fig.suptitle(
        f"\n{recipe.get('title', '')} - {recipe.get('selected_segment', '')}",
        color="white",
        fontweight="bold",
        fontsize=16,
        y=0.98,
    )
    fig.text(0.98, 0.035, f"WSPRadar.org {APP_VERSION}", color="#888888", ha="right", fontsize=10)
    gs = fig.add_gridspec(2, 2, height_ratios=[0.82, 1.18])
    ax_rates = fig.add_subplot(gs[0, :])
    ax_rate_time = fig.add_subplot(gs[1, 0])
    ax_opp_time = fig.add_subplot(gs[1, 1], sharey=ax_rate_time)

    _style_evidence_axis(ax_rates)
    ax_rates.tick_params(colors="white", labelsize=10)

    trials = np.asarray(recipe.get("station_trials", []), dtype=float)
    hits = np.asarray(recipe.get("station_hits", []), dtype=float)
    rates = np.asarray(recipe.get("station_rates", []), dtype=float)
    valid = (
        np.isfinite(trials) &
        np.isfinite(hits) &
        np.isfinite(rates) &
        (trials > 0) &
        (hits > 0)
    )
    trials = trials[valid]
    hits = hits[valid]
    rates = rates[valid]
    if len(rates):
        ax_rates.scatter(
            trials,
            rates,
            c="#39ff14",
            s=18,
            alpha=0.80,
            edgecolors="none",
            label="Station with Target evidence",
        )
        ax_rates.axvline(
            float(recipe.get("minimum_trials", 5)),
            color="#ffffff",
            linestyle="dashed",
            linewidth=1,
            alpha=0.8,
            label=f"{terms['pair']} threshold {int(recipe.get('minimum_trials', 5))}",
        )
        ax_rates.set_xscale("log", base=2)
        minimum_tick = max(1, int(2 ** np.floor(np.log2(np.nanmin(trials)))))
        maximum_tick = max(minimum_tick, int(2 ** np.ceil(np.log2(np.nanmax(trials)))))
        evidence_ticks = []
        tick_value = minimum_tick
        while tick_value <= maximum_tick:
            evidence_ticks.append(tick_value)
            tick_value *= 2
        if len(evidence_ticks) > 8:
            evidence_ticks = [
                evidence_ticks[index]
                for index in np.unique(
                    np.linspace(0, len(evidence_ticks) - 1, 8).astype(int)
                )
            ]
        ax_rates.set_xticks(evidence_ticks)
        ax_rates.xaxis.set_major_formatter(
            mpl.ticker.FuncFormatter(lambda value, _position: f"{int(value):d}")
        )
        ax_rates.xaxis.set_minor_locator(mpl.ticker.NullLocator())
        ax_rates.set_ylim(0, 100)
        ax_rates.legend(
            loc="upper right",
            facecolor="#111111",
            edgecolor="#444444",
            labelcolor="white",
            fontsize=8,
        )
    else:
        ax_rates.text(0.5, 0.5, "No station has Target evidence", color="#cccccc", ha="center", va="center", transform=ax_rates.transAxes)
    ax_rates.set_title("Station Success Rate by Evidence Count", color="white", fontweight="bold", fontsize=12, pad=9)
    ax_rates.set_xlabel(f"Evidence Count (Target + {terms['counter']})", color="white", fontsize=10)
    ax_rates.set_ylabel("Success Rate (%)", color="white", fontsize=10)

    time_values = pd.to_datetime(
        np.asarray(recipe.get("time_ns", []), dtype=np.int64),
        unit="ns",
        utc=True,
    ).tz_convert(None)
    success_cmap = mpl.colors.ListedColormap(list(SUCCESS_RATE_COLORS))
    success_bounds = np.asarray(SUCCESS_RATE_BOUNDS, dtype=float)
    success_norm = mpl.colors.BoundaryNorm(
        success_bounds,
        success_cmap.N,
        clip=True,
    )
    success_ticklabels = list(SUCCESS_RATE_TICK_LABELS)
    station_image = _draw_opportunity_heatmap(
        ax_rate_time,
        np.asarray(recipe.get("station_rate_grid", []), dtype=float),
        recipe.get("range_labels", []),
        time_values,
        f"Average Station Success Rate ({recipe.get('time_bin', '3h')})",
        f"Average Target / (Target + {terms['counter']})",
        success_cmap,
        norm=success_norm,
        cbar_ticks=success_bounds,
        cbar_ticklabels=success_ticklabels,
        show_colorbar=False,
        empty_message=terms["empty_evidence"],
    )
    observation_image = _draw_opportunity_heatmap(
        ax_opp_time,
        np.asarray(recipe.get("overall_rate_grid", []), dtype=float),
        recipe.get("range_labels", []),
        time_values,
        f"Observation-Level Success Rate ({recipe.get('time_bin', '3h')})",
        f"Total Target / (Target + {terms['counter']})",
        success_cmap,
        norm=success_norm,
        cbar_ticks=success_bounds,
        cbar_ticklabels=success_ticklabels,
        show_y_labels=False,
        show_colorbar=False,
        empty_message=terms["empty_evidence"],
    )
    shared_image = station_image if station_image is not None else observation_image
    if shared_image is not None:
        cbar = fig.colorbar(
            shared_image,
            ax=[ax_rate_time, ax_opp_time],
            pad=0.015,
            fraction=0.025,
            ticks=success_bounds,
            spacing="uniform",
        )
        cbar.ax.set_yticklabels(success_ticklabels)
        cbar.set_label(
            f"Success Rate: {terms['formula_spaced']}",
            color="white",
            fontsize=9,
        )
        cbar.ax.tick_params(colors="white", labelsize=9)
    return fig

def _opportunity_selected_recipe(
    rows,
    title,
    time_bin,
    analysis_start_t,
    analysis_end_t,
    terminology,
):
    bin_minutes = _time_agg_minutes(time_bin)
    work, time_bins = _assign_fixed_time_bins(
        rows,
        analysis_start_t,
        analysis_end_t,
        bin_minutes,
    )
    if "path_illumination" not in work.columns:
        work["path_illumination"] = ILLUMINATION_GREYLINE_MIXED
    work["path_illumination"] = pd.Categorical(
        work["path_illumination"].astype(str),
        categories=ILLUMINATION_CLASSES,
        ordered=True,
    )

    bins = (
        work.groupby("time_bin", dropna=False)
        .agg(
            hits=("hit", "sum"),
            misses=("miss", "sum"),
        )
        .reindex(time_bins, fill_value=0)
        .rename_axis("time_bin")
        .reset_index()
    )
    bins["confirmed"] = bins["hits"] + bins["misses"]
    bins["rate_pct"] = np.where(
        bins["confirmed"] > 0,
        100.0 * bins["hits"] / bins["confirmed"],
        np.nan,
    )

    def count_by_illumination(value_column):
        grouped = (
            work.groupby(["time_bin", "path_illumination"], observed=False)[value_column]
            .sum()
            .unstack(fill_value=0)
            .reindex(index=time_bins, columns=ILLUMINATION_CLASSES, fill_value=0)
        )
        return {
            illumination: grouped[illumination].to_numpy(dtype=float, copy=True)
            for illumination in ILLUMINATION_CLASSES
        }

    hit_rows = work[work["hit"] > 0].copy()
    successful_snr_by_illumination = {}
    for illumination in ILLUMINATION_CLASSES:
        successful_snr_by_illumination[illumination] = pd.to_numeric(
            hit_rows.loc[hit_rows["path_illumination"].astype(str) == illumination, "target_snr"],
            errors="coerce",
        ).dropna().to_numpy(dtype=float, copy=True)

    return {
        "kind": "opportunity",
        "title": title,
        "absolute_mode": terminology.get("mode", "RX"),
        "terminology": dict(terminology),
        "time_bin": time_bin,
        "time_ns": pd.to_datetime(bins["time_bin"], utc=True).dt.tz_convert(None).to_numpy(dtype="datetime64[ns]").astype(np.int64, copy=True),
        "rate_pct": bins["rate_pct"].to_numpy(dtype=float, copy=True),
        "hits": bins["hits"].to_numpy(dtype=float, copy=True),
        "misses": bins["misses"].to_numpy(dtype=float, copy=True),
        "target_by_illumination": count_by_illumination("hit"),
        "counter_by_illumination": count_by_illumination("miss"),
        "successful_snr": pd.to_numeric(
            hit_rows["target_snr"],
            errors="coerce",
        ).dropna().to_numpy(dtype=float, copy=True),
        "successful_snr_by_illumination": successful_snr_by_illumination,
    }

@synchronized_matplotlib
def _render_opportunity_selected_figure(recipe):
    terms = recipe.get("terminology") or absolute_terms(
        T.get(st.session_state.get("lang", "en"), T["en"]),
        recipe.get("absolute_mode", "RX"),
    )
    fig = create_agg_figure(figsize=(13, 5.8), facecolor="black")
    fig.subplots_adjust(left=0.07, right=0.95, bottom=0.15, top=0.76, wspace=0.32)
    fig.suptitle(recipe.get("title", ""), color="white", fontweight="bold", fontsize=14, y=0.955)
    fig.text(0.98, SEGMENT_FIGURE_FOOTER_Y, f"WSPRadar.org {APP_VERSION}", color="#888888", ha="right", fontsize=10)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0])
    ax_time = fig.add_subplot(gs[0, 0])
    ax_snr = fig.add_subplot(gs[0, 1])
    for ax in [ax_time, ax_snr]:
        _style_evidence_axis(ax)

    target_legend_handles = [
        mpl.patches.Patch(
            facecolor=ILLUMINATION_TARGET_COLORS[illumination],
            edgecolor="#111111",
            label=f"Target {ILLUMINATION_DISPLAY_LABELS[illumination]}",
        )
        for illumination in ILLUMINATION_CLASSES
    ]
    counter_legend_handles = [
        mpl.patches.Patch(
            facecolor=ILLUMINATION_COUNTER_COLORS[illumination],
            edgecolor="#111111",
            label=f"{terms['counter']} {ILLUMINATION_DISPLAY_LABELS[illumination]}",
        )
        for illumination in ILLUMINATION_CLASSES
    ]
    fig.legend(
        handles=target_legend_handles + counter_legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.50, 0.895),
        ncol=6,
        facecolor="#111111",
        edgecolor="#444444",
        labelcolor="white",
        fontsize=8,
        framealpha=0.85,
        handlelength=1.2,
        columnspacing=0.9,
        handletextpad=0.4,
    )
    times = pd.to_datetime(np.asarray(recipe.get("time_ns", []), dtype=np.int64), unit="ns", utc=True).tz_convert(None)
    rates = np.asarray(recipe.get("rate_pct", []), dtype=float)
    hits = np.asarray(recipe.get("hits", []), dtype=float)
    misses = np.asarray(recipe.get("misses", []), dtype=float)
    x_values = np.arange(len(times), dtype=float)
    if len(x_values):
        ax_time.plot(
            x_values,
            rates,
            color="#c8f4ff",
            marker="o",
            markersize=3,
            linewidth=1.2,
            label="Success Rate",
        )
        ax_time.set_ylim(0, opportunity_rate_scale_max(rates))
        ax_time.set_ylabel("Success Rate (%)", color="white")
        time_tick_indices = _opportunity_time_tick_indices(times)
        ax_time.set_xticks(x_values[time_tick_indices])
        ax_time.set_xticklabels(
            [
                pd.Timestamp(times[index]).strftime("%d-%b\n%H:%M")
                for index in time_tick_indices
            ],
            color="white",
            fontsize=9,
        )
        ax_evidence = ax_time.twinx()
        ax_evidence.set_facecolor("black")
        ax_evidence.patch.set_alpha(0)
        width = 0.72
        target_by_illumination = recipe.get("target_by_illumination") or {
            ILLUMINATION_GREYLINE_MIXED: hits,
        }
        counter_by_illumination = recipe.get("counter_by_illumination") or {
            ILLUMINATION_GREYLINE_MIXED: misses,
        }
        stack_bottom = np.zeros_like(x_values, dtype=float)
        for illumination in ILLUMINATION_CLASSES:
            values = np.asarray(
                target_by_illumination.get(illumination, np.zeros_like(x_values)),
                dtype=float,
            )
            if not np.any(values > 0):
                continue
            ax_evidence.bar(
                x_values,
                values,
                bottom=stack_bottom,
                width=width,
                color=ILLUMINATION_TARGET_COLORS[illumination],
                alpha=0.72,
                edgecolor="#111111",
                linewidth=0.35,
            )
            stack_bottom += values
        for illumination in ILLUMINATION_CLASSES:
            values = np.asarray(
                counter_by_illumination.get(illumination, np.zeros_like(x_values)),
                dtype=float,
            )
            if not np.any(values > 0):
                continue
            ax_evidence.bar(
                x_values,
                values,
                bottom=stack_bottom,
                width=width,
                color=ILLUMINATION_COUNTER_COLORS[illumination],
                alpha=0.58,
                edgecolor="#111111",
                linewidth=0.35,
            )
            stack_bottom += values
        ax_evidence.set_ylabel(terms["count_axis_label"], color="#bbbbbb")
        ax_evidence.tick_params(colors="#bbbbbb", labelsize=8)
        ax_evidence.yaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
        ax_evidence.yaxis.set_major_formatter(
            mpl.ticker.FuncFormatter(lambda value, _position: f"{int(value):d}")
        )
        for spine in ax_evidence.spines.values():
            spine.set_color("#444444")
        ax_time.set_zorder(ax_evidence.get_zorder() + 1)
        ax_time.patch.set_visible(False)
        ax_time.set_xlim(-0.5, len(x_values) - 0.5)
        rate_handles, rate_labels = ax_time.get_legend_handles_labels()
        ax_time.legend(
            rate_handles,
            rate_labels,
            loc="upper right",
            facecolor="#111111",
            edgecolor="#444444",
            labelcolor="white",
            fontsize=8,
        )
    else:
        ax_time.text(0.5, 0.5, "No time evidence", color="#cccccc", ha="center", va="center", transform=ax_time.transAxes)
    ax_time.set_title(f"Station Success Rate + Evidence over Time ({recipe.get('time_bin', '3h')})", color="white", fontweight="bold", pad=8)
    ax_time.set_xlabel("Date/Time (UTC)", color="white")

    snr = np.asarray(recipe.get("successful_snr", []), dtype=float)
    if len(snr):
        snr_by_illumination = recipe.get("successful_snr_by_illumination") or {
            ILLUMINATION_GREYLINE_MIXED: snr,
        }
        _draw_stacked_vertical_metric_histogram(
            ax_snr,
            snr_by_illumination,
            ILLUMINATION_TARGET_COLORS,
        )
        ax_snr.set_xlabel("Target normalized SNR (dB @ 1 W)", color="white")
    else:
        ax_snr.text(0.5, 0.5, "No Target SNR evidence", color="#cccccc", ha="center", va="center", transform=ax_snr.transAxes)
    ax_snr.set_title("Target SNR", color="white", fontweight="bold", pad=8)
    return fig
