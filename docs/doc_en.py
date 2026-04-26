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
* [9. Existing Literature and Prior Art](#sec-9)
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

* [9. Existing Literature and Prior Art](#sec-9)

<a id="sec-9"></a>
### 9. Existing Literature and Prior Art

WSPRadar does not exist in isolation. It builds on three already established lines of work: first, WSPR as a global observation network operated by radio amateurs; second, scientific work that uses WSPR data for propagation and antenna questions; and third, practical tools that visualize, query, score or otherwise analyze WSPR spots.

This chapter places WSPRadar in that context and deliberately limits its claim. WSPRadar is not a calibrated antenna range and it is not a replacement for controlled field-strength measurements. It is a tool for robust, auditable real-world evaluation of station systems using public WSPR spot data.

<a id="sec-9-1"></a>
#### 9.1 WSPR as a Global Observation Network

WSPR was developed to probe potential propagation paths using low-power transmissions. The ARRL describes WSPR as a narrowband digital protocol for HF and MF propagation testing. A typical WSPR message contains callsign, 4-character Maidenhead locator and transmit power in dBm. A transmission lasts about 110.6 seconds and starts two seconds into an even UTC minute. The approximate minimum reception threshold is around -27 dB on the WSJT scale, referenced to a 2500 Hz bandwidth. [9-1]

The public WSPR infrastructure, however, is not a laboratory instrument. WSPR.live provides historical and current WSPR spots in a ClickHouse database and explicitly states that the data is raw data as reported, saved and published by WSPRnet. Duplicates, false spots, incorrect locators, incorrect powers and infrastructure outages are therefore part of the real data environment. [9-2]

WSPRadar does not treat this uncertainty as if it disappeared. Instead, it reduces its effect through filters, minimum thresholds, medians, temporal pairing, segment aggregation and drill-down inspection. The claim is not that crowd-sourced WSPR data becomes calibrated measurement data. The claim is that many imperfect but repeated observations can be transformed into a transparent and cautiously interpreted evidence layer.

<a id="sec-9-2"></a>
#### 9.2 WSPR in Radio Science and Ionospheric Research

Lo et al. studied 7 MHz greyline propagation using amateur-radio beacon observations from the WSPR database. The paper shows that WSPR is useful not only for individual station observation, but also as a scientific dataset for global HF propagation questions. For WSPRadar, the important idea is that WSPR paths can be analyzed by time, geography and band even though the original infrastructure was not built as a controlled experiment. [9-3]

Frissell et al. place WSPRNet alongside the Reverse Beacon Network and PSKReporter as established amateur-radio observation networks that provide long-term data on the bottomside ionosphere. This work is important because it describes amateur radio as citizen-science infrastructure: many independent stations together create an observation network that is relevant to space weather, ionospheric and HF-propagation research. For WSPRadar, this perspective is central: the tool does not treat one report as absolute truth, but uses the mass, repetition and geographic distribution of observations. [9-4]

A key methodological consequence follows from this literature: WSPR data can be useful for radio science, but it must be read as observational data. It contains real propagation, real station differences and real error sources at the same time. WSPRadar therefore does not try to eliminate all of these factors. Instead, it makes the dominant confounders visible and reduces them as much as practical for specific comparison questions.

<a id="sec-9-3"></a>
#### 9.3 WSPR for Antenna and Station Comparisons

Vanhamel, Machiels and Lamy used WSPR on the 160 m band for antenna performance evaluation and propagation assessment. Their setup used two nearly identical WSPR receiving stations at a similar location to compare different 160 m antennas. The work is especially relevant to WSPRadar because it addresses the same core problem: WSPR SNR contains antenna and station performance, but also propagation, noise, polarization and time variation. The study reduces these confounders by using closely located, comparable receive systems, making it a methodological precursor to simultaneous RX A/B comparisons. [9-5]

Zander proposed a simple method for comparing HF antenna efficiency relative to a reference antenna using the global WSPR receiver network. In that approach, two antennas transmit, and only reports from the same distant receiving station within the same time interval are used for comparison. This makes path loss and receiver noise largely common to both observations; the remaining difference is then closer to the relative difference between the two transmitting antenna systems. This idea is very close to WSPRadar's same-cycle logic for TX comparisons. Zander also discusses limitations such as receiver distribution, radiation-pattern bias, interference, WSPR collisions and the fact that relative efficiency does not automatically provide a complete antenna pattern. [9-6]

These works support the basic idea behind WSPRadar: WSPR can be useful for antenna and station comparisons when comparison pairs are formed carefully and confounders are handled explicitly. They also limit how WSPRadar results should be described. A WSPR-based comparison can provide strong evidence about real station performance, but it does not directly measure antenna gain, take-off angle or efficiency in the calibrated laboratory sense.

<a id="sec-9-4"></a>
#### 9.4 Existing Tools and Practical Prior Art

**WSPR.live** is the most important data source for WSPRadar. The platform provides a publicly queryable ClickHouse database of historical WSPR spots, together with documentation, Grafana dashboards and examples of the data structure. WSPR.live is therefore less an antenna-comparison tool than a central, fast data foundation for custom analysis. WSPRadar uses this infrastructure but adds station-focused experiment logic, segment aggregation and interactive audit views. [9-2]

**WSPR.Rocks** is a powerful analysis and visualization tool based on WSPR.live and WSPRdaemon data. It provides, among other features, SpotQ, SQL access, maps, tables, duplicate-spot analysis, passband displays and interactive analyses. SpotQ is especially interesting as a practical ranking measure because it combines distance, power and SNR into a simple metric. WSPRadar has a different emphasis: it does not try to produce a global leaderboard, but instead tries to answer concrete comparison questions using controlled pairing, local reference pools and segment-level evidence. [9-7]

**WSPRdaemon** is primarily focused on robust data acquisition. It can decode WSPR and FST4W from multiple SDR receivers, upload spots reliably to WSPRnet, manage band and receiver schedules, recover from outages and record additional information such as Doppler shift and background noise. WSPRdaemon is therefore more of a professional receiving and reporting infrastructure than an end-user antenna-benchmarking tool. It is nevertheless important prior art for WSPRadar because it shows how important stable multi-receiver acquisition, noise information and long-term observability are for serious WSPR analysis. [9-8]

**SOTABEAMS WSPRlite and DXplorer** are direct practical prior art for WSPR-based antenna and location comparisons. WSPRlite is a small WSPR transmitter; DXplorer uses WSPR data to compare antenna and station performance, including the DX10 metric and real-time graphs. The strength of this approach is ease of use and direct practical value. WSPRadar differs by taking a more auditable, data-analytical approach: it does not only show a score, but also segment values, joint and exclusive decodes, station insights and drill-down rows so that a result can be inspected and challenged. [9-9]

**WSPR-Station-Compare** and similar tools show that the need for station-focused WSPR comparison has already been recognized. The WSPR-Station-Compare page explicitly references Vanhamel, Machiels and Lamy as well as Zander, and describes an app concept for displaying and comparing one's own WSPRnet measurements. This confirms the close connection between scientific method and amateur-radio practice: users do not only want to see where spots occurred; they want to know whether a station, antenna or hardware change is measurably better or worse. [9-10]

**Antenna Performance Analysis Tool** and other newer web services show the same trend: WSPR data is increasingly being used for understandable, user-oriented antenna reports. Such tools map receiving locations, time periods and bands and help operators assess the real-world effect of an antenna over time. WSPRadar should therefore not claim to be the first tool that uses WSPR for antenna-performance analysis. Its specific strength is the combination of comparison design, local benchmarks, median logic, bivariate yield/SNR analysis and inspectable raw-data layers. [9-11]

**WATT WSPR Analysis Tool** is another example of practical prior art. It uses an Excel/VBA environment for reporting, mapping, filtering, ad-hoc analysis and timeline animation of WSPR data. The approach is interesting because it shows that WSPR analysis can also be understood as an exploratory workflow: users want not only to view data, but also to filter, sort, animate and ask their own questions. WSPRadar picks up this exploratory idea but moves it into a web-based, experiment-design-oriented interface. [9-12]

<a id="sec-9-5"></a>
#### 9.5 Positioning of WSPRadar

This literature and prior art lead to a clear positioning:

* WSPRadar inherits from WSPR and WSPR.live the idea of a global, historical, crowd-sourced observation dataset.
* WSPRadar inherits from scientific work such as Vanhamel et al. and Zander the insight that fair comparisons must reduce temporal and spatial confounders.
* WSPRadar inherits from practical tools such as WSPR.Rocks, DXplorer, WSPRdaemon and WATT the insight that WSPR data is only useful when it is fast, filterable, visualizable and reproducible.
* WSPRadar adds its own emphasis: experimental station benchmarking with same-cycle pairing, local-neighborhood references, hardware A/B workflows, median-of-medians aggregation, decode-yield analysis and drill-down audit.

WSPRadar should therefore not be described as a replacement for WSPR.live, WSPR.Rocks, WSPRdaemon or DXplorer. It sits one layer above them: it uses historical WSPR spots to answer concrete station questions more carefully. The core question is not only: "Where are the spots?" The core question is: "Which spots are valid for this comparison question, which confounders were reduced, how stable is the median, what does the decode yield look like, and can the result be traced down to the underlying rows?"

<a id="sec-9-6"></a>
#### 9.6 Methodological Consequences for Interpretation

The existing literature supports the basic approach of WSPRadar, but it also limits the language that should be used to describe results. WSPR-based analyses can provide strong evidence about real station performance, but they do not directly measure antenna gain, take-off angle or efficiency in the calibrated laboratory sense. Reported power, locator accuracy, receiver distribution, local noise, polarization, propagation mode, band activity and decode survivorship remain part of the data.

WSPRadar result text should therefore distinguish carefully between the following levels:

* **Spot level:** individual WSPR decodes with SNR, time, band, transmitter, receiver and reported power.
* **Pair level:** valid same-cycle comparisons or valid time bins where important confounders have been reduced.
* **Station level:** median over several valid observations of one remote station.
* **Segment level:** median over several station medians in a distance/azimuth segment.
* **Interpretation level:** cautious statement about real station performance, not isolated antenna gain.

This layering is one of WSPRadar's most important distinctions from simpler map or score tools. It does not automatically make the result "true", but it makes visible which evidence supports a statement.

<a id="sec-9-7"></a>
#### 9.7 Short Conclusion

The existing literature shows that WSPR data can be seriously useful for propagation research, antenna comparison and citizen science. The practical prior art shows that many radio amateurs already use tools for maps, scores, database queries and antenna reports. WSPRadar positions itself between these worlds: it is practical enough for everyday station comparison, but methodologically explicit enough to expose the most important confounders.

WSPRadar's contribution is not that it reinvents WSPR spots. Its contribution is that it turns those spots into a reproducible, cautiously interpreted benchmarking framework for TX, RX, local-peer and hardware A/B questions.

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

* [9-1] ARRL, **WSPR**, technical overview of MEPT_JT/WSPR, message format, transmission duration, occupied bandwidth and SNR reference.  
  https://www.arrl.org/wspr

* [9-2] WSPR.live, **Welcome to WSPR Live**, documentation, database description and disclaimer about raw data, duplicates, false spots and availability.  
  https://wspr.live/

* [9-3] Lo, S.; Rankov, N.; Mitchell, C.; Witvliet, B. A.; Jayawardena, T. P.; Bust, G.; Liles, W.; Griffiths, G. (2022). **A Systematic Study of 7 MHz Greyline Propagation Using Amateur Radio Beacon Signals**. *Atmosphere*, 13(8), 1340. doi:10.3390/atmos13081340.  
  https://www.mdpi.com/2073-4433/13/8/1340

* [9-4] Frissell, N. A. et al. (2023). **Heliophysics and amateur radio: citizen science collaborations for atmospheric, ionospheric, and space physics research and operations**. *Frontiers in Astronomy and Space Sciences*, 10, Article 1184171. doi:10.3389/fspas.2023.1184171.  
  https://www.frontiersin.org/articles/10.3389/fspas.2023.1184171/full

* [9-5] Vanhamel, J.; Machiels, W.; Lamy, H. (2022). **Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band**. *International Journal of Antennas and Propagation*, 2022, Article 4809313. doi:10.1155/2022/4809313.  
  https://research.tudelft.nl/en/publications/using-the-wspr-mode-for-antenna-performance-evaluation-and-propag/

* [9-6] Zander, J. (2022). **Simple HF antenna efficiency comparisons using the WSPR system**. arXiv:2209.08989. doi:10.48550/arXiv.2209.08989.  
  https://arxiv.org/abs/2209.08989

* [9-7] WSPR.Rocks, **Help & Documentation**, SpotQ, SQL access, duplicate-spot analysis, maps, charts and heatmaps.  
  https://wspr.rocks/help.html

* [9-8] WSPRdaemon, **How wsprdaemon Works**, documentation for multi-receiver WSPR/FST4W decoding, reporting, scheduling, noise and Doppler metadata.  
  https://wsprdaemon.readthedocs.io/en/stable/description/how_it_works.html

* [9-9] SOTABEAMS, **WSPRlite Classic / DXplorer**, WSPR-based antenna performance analysis and DX10 metric.  
  https://www.sotabeams.co.uk/wsprlite-classic

* [9-10] WSPR-Station-Compare, **WSPR-Station-compare**, project page referencing Vanhamel et al. and Zander.  
  https://sites.google.com/myuba.be/wspr-station-compare/home

* [9-11] Antenna Performance Analysis Tool, **WSPR-based antenna report generator**.  
  https://wspr.bsdworld.org/

* [9-12] GM4EAU, **WATT WSPR Analysis Tool**, Excel/VBA-based tool for WSPR reporting, mapping, filtering and timeline animation.  
  https://www.gm4eau.com/home-page/wspr/
"""
