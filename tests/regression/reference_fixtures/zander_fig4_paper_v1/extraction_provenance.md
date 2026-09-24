# Independent source-only extraction

Source: Jens Zander, *Simple HF antenna efficiency comparisons using the WSPR system*, arXiv:2209.08989v1, submitted 19 September 2022. The live arXiv abstract and PDF text were read; the local source PDF was copied from the previously downloaded source-only location. No WSPRadar configuration, demo, fixture, archive measurement, or computed result was inspected.

The preserved PDF is `2209.08989v1.pdf`; SHA256 is `c03e9cd189da2b0c07abda459064cfebf07c2d515bf6eeb1b7d5610066cfaa8d`. The Figure 4 embedded image is 640 by 480 pixels. The PDF contains an embedded raster for this figure, not numerical vector bar paths. The PDF pages and embedded image were visually inspected. Figure 2 was also inspected to distinguish its explicitly Experiment B callsigns from the missing Experiment A callsigns.

`digitize_figure4.py` reproduces the source-only numerical extraction and creates `paper_features.json` and `figure4_embedded.png`. The JSON timestamp marks its independent freeze. The earlier `figure4_source_only.json` is an intermediate subset, superseded by `paper_features.json`.

## Confidence classes

- **Exact transcription of published rounded numbers:** Figure 4 title has mean -6.8 dB and sigma 3.5 dB. Page 5 calls sigma the estimated sample standard deviation. No degrees-of-freedom convention is published. Assuming ordinary nearest-one-decimal formatting gives display-precision bands of -6.85 to -6.75 dB and 3.45 to 3.55 dB; these are not confidence intervals.
- **Raster readout:** Bar heights and visible boundaries are calibrated against labelled ticks. Density tolerance is +/-0.0005 per dB and boundary tolerance +/-0.10 dB, each approximately 1.5 original-image pixels. These tolerances were selected from image resolution before any application/archive comparison.
- **Inferred rendering:** Ten equal-width bins over -17 through +4 dB, with width 2.1 dB. The final two equal-height bins merge visually; their interior boundary at 1.9 dB is inferred. Approximate unit histogram area (1.00082) supports density normalization, which the y-axis does not name explicitly. Exact plotting-library options are unavailable.
- **Conditional integer inference:** Using those ten bins and the approximate paper narrative range 150-200 as an assumed inclusive count range leaves one integer candidate at the frozen density tolerance: 166 samples, counts 2,8,16,27,33,31,34,11,2,2. This is an inferred reconstruction, not an exact published count. The approximate narrative range is not a proof that other sample counts are impossible.
- **Qualitative context:** About 1000 reports in roughly one hour; 150-200 valid reports; 15-35 receivers; bulk 14 MHz distances 1500-2000 km; likely southwest concentration. None defines an exact Experiment A acquisition selector or numerical geographic pass/fail bound.

## Important limit on a regression oracle

Equation 6 defines Delta S_k as an average over the receivers jointly reporting in one slot. The Figure 4 caption identifies the histogram as measured Delta S_k. The experimental narrative instead discusses valid signal reports from multiple receivers, and does not publish the aggregation code. Thus the paper alone does not settle whether the figure uses individual receiver-slot differences, time-slot receiver averages, or another intermediate sample definition. Do not silently rewrite this inconsistency in the test specification.

A comparison can freeze the published mean/spread display bands, histogram bins and readout uncertainty, sign convention, nominal band, and the limited setup facts. It cannot claim exact reconstruction of Experiment A from this paper alone: date/time and A callsigns are missing. Histogram agreement is evidence of consistency, not proof that an archive slice is the exact published experiment. Do not search selectors or change pairing/aggregation until the image agrees and then present that agreement as an independent validation.

For an eventual implementation, retain separate assertions for (1) provenance and selectors supplied independently of app results, (2) correctly selected same-receiver same-slot pairs and subtraction direction, (3) the selected aggregation rule with its publication ambiguity explicit, and (4) rounded mean, spread, and approximate distribution shape. Treat the inferred count candidate and geographic prose as diagnostics, not hard exact paper facts. The paper's standard-error discussion should not be used to widen a deterministic reproduction tolerance.
