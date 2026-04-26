# docs/doc_en.py

"""
English manual for WSPRadar.
Used in the Web UI and for PDF export.
"""

DOC_EN = r"""
---

<a id="sec-1"></a>
### 1. Introduction and Objective

In amateur radio, evaluating antenna performance has traditionally relied on anecdotal signal reports or manual A/B switching. However, these methods are subject to significant confounding variables: rapid ionospheric fading (QSB), inconsistent remote transmitter power levels, localized noise floors (QRM), uneven receiver density and changing station activity. These factors make it difficult to objectively measure how well an antenna or station is performing in day-to-day operation.

This is where the **Weak Signal Propagation Reporter (WSPR)** protocol changes the game. WSPR is a digital mode designed for probing potential propagation paths using low-power, two-minute beacon transmissions. Every day, thousands of stations worldwide autonomously transmit and receive these beacons, logging large volumes of time-stamped Signal-to-Noise Ratio (SNR) reports into public databases. WSPR is not calibrated laboratory instrumentation, but it is an unusually powerful global observation network: it continuously records where signals land, who can hear whom, and under which band/time conditions those decodes occurred.

The objective of **WSPRadar** is to harness this massive, crowd-sourced dataset and turn it into a systematic, semi-quantitative framework for evaluating transmit (TX) and receive (RX) station performance. By extracting historical WSPR spot data from wspr.live, WSPRadar applies temporal pairing, reported-power normalization, geographic aggregation, median-based robustness filters and interactive drill-down tables. The result is not a calibrated antenna test site or controlled station measurement setup. It is a practical real-world evidence engine for answering: where am I heard, who do I hear, how do I compare to my local peers, and did a hardware change produce a measurable signal?

### Table of Contents
* [1. Introduction and Objective](#sec-1)
* [2. Quick Start](#sec-2)
* [3. What WSPRadar Can Answer](#sec-3)
* [4. Analysis Modes and Valid Experiment Design](#sec-4)
  * [4.1 Absolute TX/RX](#sec-4-1)
  * [4.2 Local Neighborhood Benchmark](#sec-4-2)
  * [4.3 Specific Reference Station / Buddy Test](#sec-4-3)
  * [4.4 Hardware A/B Test](#sec-4-4)
* [5. How to Read Results](#sec-5)
* [6. Scientific Method and Assumptions](#sec-6)
  * [6.1 Data provenance and robustness](#sec-6-1)
  * [6.2 WSPR SNR and reported power](#sec-6-2)
  * [6.3 Power normalization](#sec-6-3)
  * [6.4 Temporal pairing and heartbeat filtering](#sec-6-4)
  * [6.5 Median aggregation hierarchy](#sec-6-5)
  * [6.6 Bivariate evaluation model](#sec-6-6)
  * [6.7 Geographic rastering and projection](#sec-6-7)
  * [6.8 Statistical confidence and Wilcoxon filtering](#sec-6-8)
* [7. Limitations and Interpretation Rules](#sec-7)
* [8. Configuration Reference](#sec-8)
* [Appendix A: Parallel Operation of Multiple WSJT-X Instances](#sec-a)
* [References](#sec-ref)

<a id="sec-2"></a>
### 2. Quick Start

1. Open the configuration panel.
2. Click `Load Demo Config`.
3. Select the desired comparison mode.
4. Run `TX` or `RX`.
5. Read the map first: color shows the median segment value, dots show individual station categories, and the footer bars show decode yield.
6. Click one distance/azimuth segment in the Segment Inspector.
7. Open one Station Insights row to inspect the Drill-Down data.
8. Export the table as CSV when you want to reproduce or externally audit a result.

<a id="sec-3"></a>
### 3. What WSPRadar Can Answer

WSPRadar is designed around concrete amateur-radio questions:

* **Where is my transmitted signal heard?** Use `TX Absolute`.
* **Who can my station hear?** Use `RX Absolute`.
* **Am I typical for my local WSPR neighborhood?** Use `Local Median Neighborhood`, the default local benchmark.
* **Can I match the best active local peer?** Use `Local Best Station`, the strict local stress test.
* **How do I compare with a specific nearby station or radio friend?** Use `Specific Reference Station`.
* **Did antenna A beat antenna B at my own location?** Use `Hardware A/B Test`, either simultaneous RX or fixed-schedule sequential TX.
* **Are my distance patterns consistent with NVIS or DX behavior?** Inspect near and far distance rings, while remembering that distance is not a direct take-off-angle measurement.
* **Am I an alligator: heard well but hearing poorly?** Compare TX and RX results against the same reference concept and look for asymmetric transmit/receive behavior.

<a id="sec-4"></a>
### 4. Analysis Modes and Valid Experiment Design

This chapter combines the user choice, the analysis concept and the experiment-design rules. Shared mathematics and assumptions are explained once in [Scientific Method and Assumptions](#sec-6).

**Standard recommendations for all modes**

* Use a correct callsign and Maidenhead locator.
* Use a time window that covers the propagation states you care about; multi-day windows are stronger when the claim spans full daily ionospheric cycles.
* Keep the station configuration stable during the analysis window except for the variable intentionally under test.
* For TX analysis, keep transmitter, antenna/feedline/tuner path, power control, scheduling and reported power stable unless they are the tested variable; use a realistic reported power value.
* For RX analysis, keep receiver, antenna/feedline path, audio path, decoder settings and upload behavior stable unless they are the tested variable.

<a id="sec-4-1"></a>
#### 4.1 Absolute TX/RX

**Answers**

* `TX Absolute`: where is my transmitted signal heard?
* `RX Absolute`: who can my station hear?
* Both modes answer path-viability and footprint questions before any benchmark is introduced.

**How it works**

* `TX Absolute` isolates spots where your callsign is the transmitter and maps receiving stations that decoded you.
* `RX Absolute` isolates spots where your callsign is the receiver and maps transmitters decoded by your station.
* SNR is normalized to 1 W where a remote transmit power is involved:  
  $$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$
* Absolute maps are excellent for coverage, skip zones and band-opening analysis. They are not fair hardware comparisons by themselves because propagation, station activity, transmitter power and receiver noise are not controlled.

**Careful with**

* WSPR logs successful decodes, not failed receive attempts. Dead bands do not lower the median; they reduce the existence of spots.
* Reported dBm may not equal feedpoint power or EIRP.
* RX results include the whole receive chain: antenna, receiver, audio path, local noise, decoder behavior and upload reliability.

<a id="sec-4-2"></a>
#### 4.2 Local Neighborhood Benchmark

The local neighborhood benchmark asks how your station performs against active WSPR stations inside a chosen geographic radius. The radius applies to both local methods.

**Local Median Neighborhood: default baseline**

For every WSPR cycle and matching remote path, WSPRadar computes the median normalized SNR of all active local reference stations inside the selected radius. Your station is compared against this cycle-level neighborhood median.

* Best first answer to: **am I doing okay for my area?**
* Robust against one unusually strong or weak local station.
* Does not invent values for missing spots. If a neighbor did not decode or was not decoded in a cycle, that missing observation is not treated as `0 dB`.
* With an even number of local reference stations, the midpoint median is used.
* The reference pool can change by cycle because WSPR activity changes by cycle.

**Local Best Station: strict stress test**

For every WSPR cycle and matching remote path, WSPRadar compares you against the strongest active local station inside the radius.

* Best answer to: **can I match the strongest active local peer?**
* This is a best-local-peer envelope, not a neighborhood average.
* The identity of the reference station can change from cycle to cycle.
* It is intentionally harder to beat than the median neighborhood.

**Valid design**

* Choose a radius that gives enough active peers without mixing very different local environments.
* Dense regions can often use a smaller radius; sparse regions may need a larger radius.
* Interpret the result as a comparison against active WSPR peers, not against calibrated reference stations.

**Careful with**

* Local peers differ in antenna type, terrain, receiver/transmitter quality, local noise and reported power accuracy.
* A very large neighborhood may stop being truly local.
* `Local Best Station` should never be described as local average performance.

<a id="sec-4-3"></a>
#### 4.3 Specific Reference Station / Buddy Test

The Buddy Test is a one-to-one comparison against a known station. You define a different reference callsign, for example a radio friend 10 km away.

**How it works**

* In TX comparison, both signals are evaluated by the same remote receiver in the same 2-minute WSPR cycle where possible:  
  $$\Delta SNR_{TX} = SNR_{norm,target} - SNR_{norm,reference}$$
* In RX comparison, both local receivers evaluate the same remote transmitter in the same 2-minute WSPR cycle where possible:  
  $$\Delta SNR_{RX} = SNR_{target} - SNR_{reference}$$
* This same-cycle pairing strongly reduces shared fading, path and receiver/transmitter confounders, depending on TX or RX direction.

**Valid design**

* Pick a reference station whose location, antenna, power and operating schedule you understand.
* Use the same band and overlapping time windows.
* Make sure both callsigns have enough shared same-cycle remote peers.

**Careful with**

* A Buddy Test is a station-system comparison, not a pure antenna-gain measurement.
* Differences may include antenna, transmitter, receiver, feedline, terrain, polarization, local QRM and reported-power accuracy.

<a id="sec-4-4"></a>
#### 4.4 Hardware A/B Test

The Hardware A/B Test is for your own equipment at your own location. It is valid only when every non-tested variable is held as constant as practical: band, time window, power, feedline losses, receiver chain, audio chain, decoding software and locator reporting.

* Use two genuinely independent receive and/or transmit chains where those chains are part of the test; shared components must be intentional, stable and outside the tested variable.

**RX A/B Test: simultaneous**

Two parallel receivers decode the same remote WSPR transmissions at the same time.

* Use distinguishable reporting identities, for example the main callsign for Setup A and a suffix for Setup B, so both streams appear in the WSPR database.
* Keep clocks synchronized.
* Appendix A describes how to separate parallel WSJT-X instances so both decoders do not share the same audio file, virtual audio path, save directory or temporary WSPR files.

**TX A/B Test: fixed-schedule sequential**

Setup A and Setup B cannot transmit at the same time on the same callsign. WSPRadar therefore uses deterministic time slicing. A transmitter or controller assigns one setup to a fixed slot pattern and the other setup to the opposite slot pattern. The tool groups data into time bins, computes a micro-median for each setup inside a bin, and calculates the bin Delta.

* Keep output power, feedline, tuner settings, band and schedule stable except for the tested variable.
* A QMX transceiver, for example, can be programmed with deterministic timing such as `frame=0` for Setup A and `frame=2` for Setup B.
* Standard WSJT-X random transmission behavior is not suitable for fixed-schedule TX A/B without additional scheduling control.

**Careful with TX suffixes**

Why avoid multi-cycle WSPR suffixes for single-transmitter TX A/B? Compound callsigns can force multi-message behavior and reduce decode yield because not all receivers decode every required message type equally well. Artificial suffixes such as `/1` or `/2` may also be jurisdiction-specific or invalid. `/P` should only be used when it is legally appropriate for the actual operation. For TX A/B, WSPRadar therefore prefers fixed timing with the normal callsign.

**Scientific caution**

Sequential TX is time-binned, not simultaneous. Multi-day fixed timing reduces time-confounding substantially, but it does not prove that every time-correlated effect disappeared.

<a id="sec-5"></a>
### 5. How to Read Results

**Heatmap segments**

Absolute modes show normalized SNR in dB. Compare modes show median Delta SNR against the selected benchmark. Positive values indicate that your station/setup is stronger than the benchmark in that segment; negative values indicate weaker performance. WSPRadar uses the common amateur-radio convention `1 S-unit = 6 dB` for the comparison color scale.

**Distance rings**

Near rings can be consistent with shorter-skip or NVIS behavior; far rings can be consistent with lower-angle DX behavior. Distance is not a direct elevation-angle measurement because ionospheric mode, band, time, season and solar state also matter.

**Scatter dots**

Individual stations are plotted as dots. Green means joint same-cycle decodes. Yellow-orange means both sides decoded the station asynchronously. Purple means only your station/setup decoded it. White means only the reference decoded it.

**Map footer and 1D-Venn bars**

The `SPOTS` bar shows raw decode-volume distribution. The `STATIONS` bar checks whether the footprint is broad or driven by only a few active stations. These bars are essential because Delta SNR alone can hide decode/no-decode behavior.

**Segment Inspector**

The Segment Inspector is the audit layer below the maps. Select a distance ring and compass direction to inspect the evidence behind one segment.

* In absolute modes, the histogram shows normalized SNR values for contributing stations. The x-axis is based on station medians. The red dashed line marks the final segment median.
* In compare modes, the histogram shows Delta SNR values. It reveals whether a segment median comes from consistent superiority or from a broad, unstable distribution.
* The Station Insights table lists contributing remote stations, separates joint decodes from exclusive decodes and shows the station-level median Delta SNR.
* Clicking a Station Insights row opens the Drill-Down table.
* `Show Non-Joint` reveals isolated decodes. Missing SNR is shown as `None`, not `0.0`. If both setups hear a station but never in the same WSPR cycle, the yield chart can show `Async Both`.

**Drill-Down Table**

The Drill-Down table is the row-level audit layer across all modes. It shows the observations, pairs or time bins behind a Station Insights row so the segment and station medians can be reconciled against the underlying evidence.

For absolute modes and normal same-cycle compare modes, the Drill-Down exposes the contributing spot-level observations and paired same-cycle comparisons used for the station-level median.

For the median-neighborhood method, the Drill-Down expands the reference pool. Instead of showing only a generic `Ref Pool` row, it lists the individual local reference stations that contributed in that cycle, their locator, distance, normalized reference SNR, the cycle's aggregated neighborhood median, your SNR and the resulting Delta SNR. This lets you reconcile the median directly.

For TX A/B, the Drill-Down shows time windows rather than same-cycle pairs. It exposes `Micro-Med A`, `Micro-Med B` and the resulting bin Delta. Opposing micro-medians are hidden in single-setup rows so missing paired data is not mistaken for zero.

**Filtering, export and high-resolution maps**

Multi-select, dynamic filters and CSV export turn the Segment Inspector into a reproducible raw-data audit surface. The map toolbar can render a 300 DPI version for publication-quality screenshots without blocking the normal interactive workflow.

<a id="sec-6"></a>
### 6. Scientific Method and Assumptions

<a id="sec-6-1"></a>
#### 6.1 Data provenance and robustness

WSPRadar reads historical WSPR spots through wspr.live. The wspr.live documentation states that the data is raw data as reported and published by WSPRnet, and warns that duplicates, false spots and other errors may exist. It also states that the volunteer-run infrastructure gives no guarantees on correctness, availability or stability.

WSPRadar mitigates many upstream data issues by using multi-layer aggregation and filters: same-cycle pairing, station-level medians, segment-level medians, minimum-sample thresholds, moving-station filtering and optional prefix exclusions. These measures substantially reduce the influence of isolated duplicates, sporadic false spots, one-hit decodes and receiver-density bias. They do not make the upstream dataset calibrated or error-free, and a plausible repeated bad report can still survive; the claim is robustness, not immunity.

<a id="sec-6-2"></a>
#### 6.2 WSPR SNR and reported power

WSPR is designed for probing potential propagation paths with low-power beacon-like transmissions. WSPR messages carry a callsign, locator and power level in dBm. WSPR-2 transmissions last about 110.6 seconds and start two seconds into even UTC minutes. The ARRL WSPR documentation describes the minimum S/N on the WSJT scale using a 2500 Hz reference bandwidth.

For WSPRadar interpretation:

* SNR is a reported decoder value in dB on the WSPR/WSJT scale, referenced to 2500 Hz.
* Reported transmit power is part of the WSPR message. It is not independently verified by WSPRadar.
* User-entered dBm may differ from transmitter output, feedpoint power or EIRP because of calibration error, foldback, feedline loss, tuner loss and antenna mismatch.

<a id="sec-6-3"></a>
#### 6.3 Power normalization

To compare spots reported with different transmit powers, WSPRadar normalizes SNR to a 1 W / 30 dBm reference:

$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$

This is essential for absolute TX/RX maps and local TX comparisons. It removes the reported-power term from the comparison, but only as well as the reported power is correct. It does not correct antenna gain, feedline loss, calibration error or EIRP differences.

Power normalization is still a meaningful mitigation. RX comparisons often reduce exposure to reported-power errors because both local receivers evaluate the same remote transmitter. Same-callsign TX A/B avoids comparing different self-reported powers. Local TX comparisons and absolute TX maps remain the most sensitive to incorrect reported dBm.

<a id="sec-6-4"></a>
#### 6.4 Temporal pairing and heartbeat filtering

Temporal synchronization is one of WSPRadar's strongest controls. Same-cycle pairing strongly reduces fast QSB/fading effects because both sides are evaluated in the same two-minute WSPR opportunity. In TX comparisons, using the same remote receiver reduces receiver-side QRM, noise-floor and antenna effects. In RX comparisons, decoding the same remote transmitter reduces transmitter-power and shared-path variation.

The heartbeat filter adds a separate protection. WSPRadar validates comparative cycles only when your setup was demonstrably alive:

* In TX mode, your signal must have been decoded by at least one station worldwide during the relevant cycle/slot.
* In RX mode, your receiver must have decoded at least one station during the relevant cycle.

If you shut the station down overnight, reference spots collected during that offline period are not counted as defeats for your hardware. This does not make every comparison perfectly fair. It reduces the dominant timing, fading and offline-bias confounders in synchronous modes. Sequential TX A/B remains the special case: time-binning and multi-day fixed schedules reduce macro-fading/time drift, but are not equivalent to simultaneous same-cycle pairing.

<a id="sec-6-5"></a>
#### 6.5 Median aggregation hierarchy

Medians are a core WSPRadar concept, not just an outlier clean-up tool. They provide robust aggregation across:

* short-term QSB and fading;
* changing ionospheric states within the selected time window;
* uneven WSPR activity by cycle and station;
* receiver-density bias in highly active regions;
* occasional erroneous or duplicate spots;
* repeated observations from very active stations;
* local-neighborhood reference pools that change from cycle to cycle.

The aggregation hierarchy is:

* **Cycle-level median:** in Local Median Neighborhood, the reference for one WSPR cycle/path is the median of active local reference stations in that cycle.
* **Station-level median:** for a given remote station, WSPRadar computes the median of the qualifying spot or bin values.
* **Segment-level median:** the final map segment value is the median of station-level medians.

This "median of medians" structure helps keep a dense receiver cluster from drowning out a sparse region merely because it generated more rows. It also keeps a single very active station from statistically overpowering an entire segment.

<a id="sec-6-6"></a>
#### 6.6 Bivariate evaluation model

A pure median Delta SNR analysis can suffer from survivorship bias. A better antenna may decode very weak signals that a worse antenna misses. Those extra marginal spots can lower the better antenna's median SNR if everything is pooled naively.

WSPRadar therefore separates two signals:

1. **System Sensitivity / Decode Yield:** counts exclusive vs joint decodes. This captures reach at the edge of decodability.
2. **Hardware Linearity / Delta SNR:** uses only paired joint spots or paired time bins. This estimates the conditional gain/SNR difference when both setups produced comparable evidence.

Read both together. A setup can have better yield but lower conditional SNR if it decodes many marginal signals. Conversely, a setup can show a strong positive Delta SNR on joint spots but poor yield if it misses many weak paths.

<a id="sec-6-7"></a>
#### 6.7 Geographic rastering and projection

Spatial data is rendered in an Azimuthal Equidistant projection centered on the user's Maidenhead locator. The map engine uses an internal spherical Earth radius of 6371 km so that table distances and plotted map positions are consistent with the same geometry.

The map uses:

* concentric radial bins of 2500 km, approximating useful propagation-distance bands;
* azimuth wedges such as 22.5 degree compass sectors;
* unique segment identifiers for aggregation and inspection.

The projection is internally consistent for WSPRadar's visual analysis. It should not be described as geodetic truth at survey precision.

<a id="sec-6-8"></a>
#### 6.8 Statistical confidence and Wilcoxon filtering

WSPRadar can use a Wilcoxon signed-rank test as an optional compare-map filter. SciPy documents this as a test for related paired samples and specifically frames it around the distribution of paired differences.

Correct interpretation:

* The test is useful as a robustness screen for paired Delta SNR values.
* A p-value is not an effect size.
* Segment-level p-values create multiple-comparison risk across the map.
* WSPR SNR values are quantized and often temporally autocorrelated; this weakens ideal textbook assumptions.
* Zero differences and ties require care, which SciPy also documents.

Therefore, Wilcoxon filtering should be documented as statistical evidence, not proof. A scientifically stronger future version could add bootstrap confidence intervals and false-discovery-rate correction across map segments.

<a id="sec-7"></a>
### 7. Limitations and Interpretation Rules

**Core limitations**

* **Crowd-sourced data:** WSPR spots can contain duplicates, false spots, wrong power, wrong locator or receiver-side errors. WSPRadar reduces sensitivity to many of these problems but cannot make upstream data calibrated or error-free.
* **Successful decodes only:** WSPR logs decodes, not all failed reception attempts. Closed bands reduce the existence of spots rather than lowering an average.
* **Reported power caveat:** normalization mitigates reported-power differences, and several compare modes reduce exposure to this problem by pairing against the same transmitter or the same callsign. However, any analysis that depends on user-reported dBm still assumes that the reported value is reasonably close to reality.
* **Sequential TX caveat:** fixed-schedule TX A/B reduces but does not perfectly eliminate time confounding.
* **Distance is not angle:** distance-ring patterns can suggest propagation behavior but do not directly measure radiation take-off angle.
* **Polarization and local environment:** WSPRadar measures real-world station-system performance, including antenna, receiver/transmitter, feedline, terrain, polarization effects, local QRM and software behavior.
* **Performance limits and latency:** query windows are capped to protect database resources, and fresh spots can take roughly 15 to 30 minutes to appear.

**Evidence language**

* **Weak evidence:** very few joint cycles, very few stations, or a result driven by one outlier station.
* **Usable evidence:** multiple stations per segment, several joint cycles or bins per station, consistent Delta SNR direction and coherent yield behavior.
* **Strong evidence:** repeated across multiple days or separate runs, stable across adjacent segments or bands where expected, not dominated by one station, and supported by exported raw data.

For serious claims, preserve enough context to reproduce the result: WSPRadar version or Git commit, UTC window, band, mode, filters, local benchmark method or reference callsign, screenshots and exported CSV.

**Disclaimer**

WSPRadar is an experimental open-source project provided "as is" without warranties. The source code and mathematical model can be audited, but the developer cannot guarantee accuracy, completeness, availability or suitability for any particular purpose. Do not make major financial decisions, such as buying or selling expensive antennas or radio hardware, based solely on WSPRadar output.

**License**

WSPRadar is free software under the GNU Affero General Public License (AGPLv3). The license ensures that the source code, including network-service modifications, remains available to the amateur-radio community.

<a id="sec-8"></a>
### 8. Configuration Reference

**Core parameters**

* **Target Callsign:** primary station under evaluation.
* **QTH Locator:** mathematical center of the map projection. Use a valid 4- or 6-character Maidenhead locator.
* **Band and timeframe:** define the WSPR data window. Time is handled in UTC.

**Comparison parameters**

* **Benchmark Mode:** `Local Neighborhood Benchmark`, `Reference Station (Buddy Test)` or `Hardware A/B-Test`.
* **Local Benchmark Method:** `Local Median Neighborhood` by default, or `Local Best Station` for a strict best-peer envelope.
* **Neighborhood Radius:** geographic boundary for local reference stations.
* **Reference Callsign:** external counterpart for Buddy Test.
* **A/B-Test Setup:** simultaneous `RX Test` or fixed-schedule `TX Test`.
* **Target/Reference Locator:** 6-character locators used to separate simultaneous RX streams.
* **Target/Reference Time Slot:** fixed slot assignment for sequential TX tests.
* **Time Window (Bins):** bin size for sequential TX A/B pairing.

**Advanced settings**

* **Local QTH Solar State:** filters by calculated solar elevation at your QTH: daylight, nighttime or greyline.
* **Exclude Prefixes:** comma-separated list of callsign prefixes or callsigns to exclude, for example telemetry balloons or known unwanted sources.
* **Exclude Moving Stations:** removes stations that change their 4-character locator during the analysis window, such as balloons, mobile or maritime stations.
* **Map Scope:** visual map radius.
* **Min. Joint Spots/Station:** in compare modes, requires at least X joint spots per remote station before that station contributes a Delta SNR. In sequential TX A/B, this is shown as Min. Joint Bins. In absolute modes, the same control acts as a raw spots-per-station filter.
* **Min. Joint Stations/Segment:** in compare modes, requires at least X remote stations with qualifying joint evidence before a segment is drawn. In absolute modes, the same control acts as a raw stations-per-segment filter.
* **Compare Map Statistical Confidence:** optional Wilcoxon-based filtering.

<a id="sec-a"></a>
### Appendix A: Parallel Operation of Multiple WSJT-X Instances

This guide describes the creation of a second OS-isolated WSJT-X environment, for example for an SDR, including configuration migration and mandatory path separation.

#### 1. Instantiation (OS-level isolation)

By default, the WSJT-X lock file prevents multiple executions. Separation is achieved with a command-line parameter that forces a new sandbox in the Windows `AppData` directory.

1. Create a desktop shortcut for `wsjtx.exe`.
2. Open the shortcut properties.
3. Modify the `Target` field according to this syntax pattern, with the parameter outside the quotation marks:
   `"C:\Program Files\wsjtx\bin\wsjtx.exe" --rig-name=SDR`
4. Start this shortcut once and immediately close the program again. This initializes the new directory structure: `%LOCALAPPDATA%\WSJT-X - SDR`.

#### 2. Configuration migration (cloning)

WSJT-X does not provide an internal export for instances, so the clone must be done at file-system level.

1. Navigate to the primary configuration folder: `%LOCALAPPDATA%\WSJT-X`
2. Copy `WSJT-X.ini`.
3. Navigate to the new folder: `%LOCALAPPDATA%\WSJT-X - SDR`
4. Paste the file and overwrite the `.ini` file created by the first start.
5. Rename the pasted file to match the new instance exactly: `WSJT-X - SDR.ini`

#### 3. Mandatory path separation (audio and storage)

Because the configuration was cloned, both instances may still point to the same hardware inputs and temporary storage directories. For WSPR, that can lead to identical decodes because the same `.wav` file is analyzed, and it can cause file-lock errors.

Open the new SDR instance and go to `File > Settings > Audio`. Adjust:

* **Soundcard > Input:** set the audio interface to the second receiver source, for example a dedicated Virtual Audio Cable.
* **Save Directory:** change the path to the isolated environment, for example:
  `C:\Users\[User]\AppData\Local\WSJT-X - SDR\save`
* **AzEl Directory:** change this path too, for example:
  `C:\Users\[User]\AppData\Local\WSJT-X - SDR`

After restarting the instance, data streams, hardware access and temporary WSPR files are separated from the primary instance.

<a id="sec-ref"></a>
### References

* ARRL, WSPR technical overview: https://www.arrl.org/wspr
* wspr.live documentation and database disclaimer: https://wspr.live/
* SciPy Wilcoxon signed-rank documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html
* WSJT-X User Guide, WSPR and SNR reference bandwidth: https://wsjt.sourceforge.io/wsjtx-doc/wsjtx-main-3.0.0.html
"""
