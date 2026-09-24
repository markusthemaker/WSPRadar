"""Paper-only extraction from the embedded raster in arXiv:2209.08989v1.

This script reads no WSPRadar data, configuration, fixtures, or outputs.
Pixel coordinates were independently read from the publication's Figure 4.
"""

from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

import numpy as np
from PIL import Image
from pypdf import PdfReader


REVIEW_DIRECTORY = Path(__file__).resolve().parent
PDF_PATH = REVIEW_DIRECTORY / "2209.08989v1.pdf"
pdf_reader = PdfReader(PDF_PATH)
figure_image = pdf_reader.pages[3].images[0].image
figure_image.save(REVIEW_DIRECTORY / "figure4_embedded.png")
pixels = np.asarray(figure_image.convert("RGB"))

# Black tick-mark pixels are unambiguous in the source raster. Axis labels were
# visually verified before entering these numerical mappings.
x_tick_pixels = np.array([133, 208, 283, 358, 433, 508])
x_tick_values_db = np.array([-15, -10, -5, 0, 5, 10])
y_tick_pixels = np.array([427, 365, 304, 242, 180, 118])
y_tick_values = np.array([0, 0.02, 0.04, 0.06, 0.08, 0.10])
x_calibration = np.polyfit(x_tick_pixels, x_tick_values_db, 1)
y_calibration = np.polyfit(y_tick_pixels, y_tick_values, 1)

# Exact solid-blue RGB in the embedded image; orange curve sometimes occludes
# a few columns, so read the most frequent top coordinate in each segment.
blue_mask = np.all(pixels == [142, 186, 217], axis=2)
left_edges_pixels = [103, 134, 166, 197, 229, 260, 292, 324, 355, 386.5]
right_edges_pixels = [134, 166, 197, 229, 260, 292, 324, 355, 386.5, 418]
top_pixels = []
for left_pixel, right_pixel in zip(left_edges_pixels, right_edges_pixels):
    column_tops = []
    for column_pixel in range(int(np.ceil(left_pixel)) + 2, int(right_pixel) - 2):
        blue_rows = np.flatnonzero(blue_mask[60:426, column_pixel]) + 60
        if len(blue_rows):
            column_tops.append(int(blue_rows[0]))
    values, frequencies = np.unique(column_tops, return_counts=True)
    top_pixels.append(int(values[np.argmax(frequencies)]))

densities = np.polyval(y_calibration, top_pixels)
nominal_edges_db = np.linspace(-17, 4, 11)
nominal_width_db = 2.1
bins = []
for index, density in enumerate(densities):
    bins.append({
        "bin_index": index + 1,
        "left_pixel": left_edges_pixels[index],
        "right_pixel": right_edges_pixels[index],
        "top_pixel": top_pixels[index],
        "left_readout_db": float(np.polyval(x_calibration, left_edges_pixels[index])),
        "right_readout_db": float(np.polyval(x_calibration, right_edges_pixels[index])),
        "nominal_left_db": round(float(nominal_edges_db[index]), 1),
        "nominal_right_db": round(float(nominal_edges_db[index + 1]), 1),
        "density_per_db": float(density),
        "nominal_probability_mass": float(density * nominal_width_db),
        "edge_note": "Boundary at 1.9 dB inferred by equal-width subdivision of a flat two-bin plateau." if index in (8, 9) else "Visible step boundary or end of blue fill.",
    })

count_candidates = []
for sample_count in range(150, 201):
    candidate_counts = np.rint(densities * nominal_width_db * sample_count).astype(int)
    errors = np.abs(candidate_counts / (sample_count * nominal_width_db) - densities)
    if int(candidate_counts.sum()) == sample_count and float(errors.max()) < 0.0005:
        count_candidates.append({
            "sample_count": sample_count,
            "bin_counts": candidate_counts.tolist(),
            "maximum_density_residual": float(errors.max()),
        })

extraction = {
    "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
    "source": {
        "url": "https://arxiv.org/pdf/2209.08989v1",
        "abstract_url": "https://arxiv.org/abs/2209.08989",
        "version": "v1; submitted 2022-09-19",
        "pdf_sha256": hashlib.sha256(PDF_PATH.read_bytes()).hexdigest(),
        "pdf_page": 4,
        "figure": 4,
        "embedded_image_size_pixels": list(figure_image.size),
        "independence": "Extracted from source paper only before examining any WSPRadar output, archive selection, fixture, or demo.",
    },
    "reported_statistics": {
        "mean_db": -6.8,
        "sigma_db": 3.5,
        "status": "Exact transcription of rounded one-decimal figure annotations.",
        "sigma_meaning": "Page 5 identifies sigma as estimated sample standard deviation; ddof is not specified.",
        "conditional_nearest_rounding_intervals": {"mean_db": [-6.85, -6.75], "sigma_db": [3.45, 3.55]},
        "interval_caveat": "Intervals assume conventional nearest-one-decimal formatting, which the paper does not specify. These are display-precision intervals, not sampling uncertainty or a license to tune selectors.",
    },
    "experiment_a_setup": {
        "source_location": "Section V, page 4; Figure 4 caption; transmitter setup in Section III, pages 2-3.",
        "band_frequency_mhz": 14,
        "conditions": "Daylight, spring",
        "place": "Gotland Island",
        "transmitter_locator_prefix": "JO97",
        "measurement_antenna": "Difona HF-P1 portable vertical; 2.5 m; center loaded; resonant; 4 radials",
        "reference_antenna": "Hy-Gain AV620 Patriot; resonant 5/8 wavelength vertical",
        "transmitters": "Zachtek; paper states equal fixed 200 mW (+23 dBm) output",
        "pairing_rule": "Same receiving station, same 2-minute slot, same frequency band; only joint reception enters the SNR comparison.",
        "difference_sign": "Measured antenna SNR minus reference antenna SNR, in dB (equation 4).",
        "reported_snr_quantization_db": 1,
        "selector_gaps": ["Exact calendar date absent", "Exact start and end times absent", "Experiment A callsigns absent", "Full six-character Experiment A locator absent", "Exact per-transmitter radio frequencies absent", "Exact raw count, exact paired count, exact receiver count absent", "Receiver list and duplicate handling absent", "No published raw measurement table or linked analysis script"],
        "callsign_caution": "Figure 2 shows SK0WE/P and SK0BU, but its caption explicitly identifies Experiment B (7 MHz T2FD versus dipole). These do not establish Experiment A callsigns.",
    },
    "experiment_narrative_counts": {
        "source_location": "Section V, pages 4-5, pooled description applying to each of the two experiments.",
        "raw_report_count_approx": 1000,
        "duration_hours_approx": 1,
        "valid_report_count_range_approx": [150, 200],
        "receiver_count_range_approx": [15, 35],
        "useful_samples_for_error_discussion_approx": 100,
        "mean_standard_deviation_bound_db_stated": 0.5,
        "status": "Rounded qualitative context; not exact Experiment A counts, time selectors, or a distribution-matching tolerance.",
    },
    "geography_context": {
        "source_location": "Section V, page 5, 14 MHz context.",
        "bulk_distance_km": [1500, 2000],
        "azimuth_context": "Receivers are more common in Western Europe; paper says most reports in Sweden are likely from the southwest quadrant and its discussion describes measurements concentrated toward southern to western azimuths.",
        "test_status": "Qualitative diagnostics only. Bulk does not define an exact fraction; likely is not a counted empirical guarantee. Do not use these as selection filters, a hard majority threshold, or an exact geographic reference distribution.",
    },
    "digitization": {
        "coordinate_origin": "Top left of the original embedded 640x480 Figure 4 raster; zero-based pixels.",
        "x_tick_pixels": x_tick_pixels.tolist(),
        "x_tick_values_db": x_tick_values_db.tolist(),
        "y_tick_pixels": y_tick_pixels.tolist(),
        "y_tick_values": y_tick_values.tolist(),
        "x_calibration_db_per_pixel_and_intercept": x_calibration.tolist(),
        "y_calibration_density_per_pixel_and_intercept": y_calibration.tolist(),
        "density_absolute_readout_tolerance_per_db": 0.0005,
        "x_edge_absolute_readout_tolerance_db": 0.10,
        "tolerance_basis": "Conservative roughly 1.5 source pixels: horizontal 15 pixels/dB and vertical 3089 pixels per density unit. Frozen before any archive or app comparison.",
        "nominal_bin_width_db": nominal_width_db,
        "nominal_bin_count": 10,
        "bins": bins,
        "nominal_area": float(sum(densities) * nominal_width_db),
        "normalization_status": "Density inferred from approximate unit area and density-scale orange Gaussian curve; y-axis lacks an explicit normalization label.",
        "axis_limits_readout": {"x_db": np.polyval(x_calibration, [80, 576]).tolist(), "y_density": np.polyval(y_calibration, [427, 58]).tolist()},
        "axes_caveat": "Readout of border positions; exact plot limits are not stated in the paper.",
    },
    "conditional_count_inference": {
        "status": "Inferred only, not an exact published count and not suitable as a hard paper-proven sample-count assertion.",
        "assumptions": ["Ten equal-width bins over -17 through 4 dB", "Density normalization", "An integer sample count between 150 and 200 inclusive", "Per-bin density tolerance 0.0005 per dB"],
        "candidates": count_candidates,
        "caveat": "The paper's 150-200 wording is approximate across both experiments. Multiples or other larger sample counts can fit the same normalized histogram. Equal-height final bins have no visible internal seam.",
    },
    "aggregation_ambiguity": "The Figure 4 caption calls the plotted values Delta S_k, which equation 6 defines as a per-slot average over joint receivers. Section V also describes 150-200 valid signal reports from 15-35 receivers over roughly one hour. The paper does not publish raw data or the processing script, and does not resolve precisely which sample unit is histogrammed. Do not silently equate this to pooled receiver-slot differences or per-receiver means.",
}

output_path = REVIEW_DIRECTORY / "paper_features.json"
output_path.write_text(json.dumps(extraction, indent=2) + "\n", encoding="utf-8")
print(output_path)
print("Figure 4 density area:", extraction["digitization"]["nominal_area"])
print("Conditional count candidates:", count_candidates)
