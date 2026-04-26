# WSPRadar.org
## HAM RADIO STATION & ANTENNA BENCHMARKING

WSPRadar is an experimental, data-driven antenna and station benchmarking tool built on public WSPR spot data. It helps turn a large, crowd-sourced observation network into structured evidence about your station. It is not a calibrated antenna range, and it does not replace controlled RF measurements, but it can make real-world WSPR evidence far more auditable than anecdotal reports or casual A/B switching.

---

### Table of Contents
* [1. What can I answer with WSPRadar?](#1-what-can-i-answer-with-wspradar)
* [2. Quick Start: first useful result](#2-quick-start-first-useful-result)
* [3. Choose your test](#3-choose-your-test)
* [4. How to read the results](#4-how-to-read-the-results)
* [5. Core concepts: Absolute vs. Compare](#5-core-concepts-absolute-vs-compare)
* [6. Comparative methods](#6-comparative-methods)
* [7. Scientific method and assumptions](#7-scientific-method-and-assumptions)
* [8. Experiment design appendix](#8-experiment-design-appendix)
* [9. Configuration reference](#9-configuration-reference)
* [10. Limitations, disclaimer and license](#10-limitations-disclaimer-and-license)
* [Appendix A: Parallel operation of multiple WSJT-X instances](#appendix-a-parallel-operation-of-multiple-wsjt-x-instances)
* [References](#references)

### 1. What can I answer with WSPRadar?

WSPRadar is designed around concrete amateur-radio questions:

* **Where is my transmitted signal heard?** Use `TX Absolute` to map receiving stations that decoded your callsign.
* **Who can my station hear?** Use `RX Absolute` to map transmitters decoded by your receiver.
* **Am I typical for my local WSPR neighborhood?** Use `Local Median Neighborhood`. This is the default local benchmark.
* **Can I match the best active local peer?** Use `Local Best Station`. This is a stricter best-peer envelope, not a neighborhood average.
* **How do I compare with a specific nearby station or radio friend?** Use `Specific Reference Station`.
* **Did antenna A beat antenna B at my own location?** Use `Hardware A/B Test`, with simultaneous RX or fixed-schedule sequential TX.
* **Are my distance patterns consistent with NVIS or DX behavior?** Inspect near and far distance rings. Treat this as propagation-pattern evidence, not a direct take-off-angle measurement.
* **Am I an alligator: heard well but hearing poorly?** Compare TX and RX results against the same reference concept and look for asymmetric transmit/receive behavior.

### 2. Quick Start: first useful result

1. Open the configuration panel.
2. Click `Load Demo Config`.
3. Run `TX` or `RX`.
4. Read the map first: color shows the median segment value, dots show individual station categories, and the footer bars show decode yield.
5. Click one map segment in the Segment Inspector.
6. Open one Station Insights row to inspect the Drill-Down data.
7. Export the table as CSV when you want to reproduce or externally audit a result.

The current demo data is configured mainly for the local neighborhood comparison and may be sparse. More comprehensive demo datasets can be added later without changing the method.

### 3. Choose your test

| Question | WSPRadar mode | Valid when | Be careful when | Primary output |
|---|---|---|---|---|
| Where am I heard? | `TX Absolute` | Your callsign transmits WSPR with a correct locator and reported power. | Reported dBm may not equal feedpoint power; closed bands do not count as weak spots because WSPR logs successful decodes only. | Map segments, normalized SNR, receiver list. |
| Who do I hear? | `RX Absolute` | Your receiver uploads WSPR spots reliably. | RX results reflect the full receive chain: antenna, receiver, audio chain, local noise and upload behavior. | Map segments, normalized remote-transmitter SNR, transmitter list. |
| Am I typical for nearby active WSPR stations? | `Local Median Neighborhood` | Several local stations are active inside the selected radius in the same WSPR cycles. | The neighborhood is not a calibrated reference array; it is the median of active peers visible in the data. | Delta SNR vs neighborhood median, yield bars, expanded reference Drill-Down. |
| Can I match the strongest local station? | `Local Best Station` | You want a strict stress test against the best active local peer per cycle/path. | It is intentionally harsh: the reference may change cycle by cycle and can become a moving best-peer envelope. | Delta SNR vs best local station, best-reference Drill-Down. |
| Is my station better than a specific reference? | `Specific Reference Station` | Both callsigns are active and share enough same-cycle remote peers. | Local geography, antenna type, power accuracy and local noise may differ. | Joint spots, exclusive decodes, station-level Delta SNR. |
| Did RX setup A beat RX setup B? | `RX A/B Test` | Two independent receivers decode the same remote WSPR transmissions at the same time and report distinguishable callsigns/suffixes. | Duplicate filtering and shared audio paths can invalidate the comparison. | Same-cycle paired Delta SNR and decode yield. |
| Did TX setup A beat TX setup B? | `TX A/B Test` | One callsign is transmitted on fixed, deterministic time slots for A and B over a long enough window. | Sequential TX is time-binned, not simultaneous. Multi-day runs average down many propagation effects, but fixed timing cannot prove every time-correlated effect disappeared. | Time-bin paired Delta SNR, joint bins, yield. |

### 4. How to read the results

#### 4.1 Map elements

* **Heatmap segments:** Absolute modes show normalized SNR in dB. Compare modes show median Delta SNR against the selected benchmark.
* **Compare color scale:** Positive values indicate that your station/setup is stronger than the benchmark in that segment; negative values indicate weaker performance. WSPRadar uses the common amateur-radio convention `1 S-unit = 6 dB` for the comparison color scale.
* **Distance rings:** Near rings can be consistent with shorter-skip or NVIS behavior; far rings can be consistent with lower-angle DX behavior. Distance is not a direct elevation-angle measurement because ionospheric mode, band, time, season and solar state also matter.
* **Scatter dots:** Individual stations are plotted as dots. Green means joint same-cycle decodes. Yellow-orange means both sides decoded the station asynchronously. Purple means only your station/setup decoded it. White means only the reference decoded it.
* **Pole markers:** The geographic North Pole and South Pole are marked to help interpret paths that cross polar regions.
* **Map footer and 1D-Venn bars:** The `SPOTS` bar shows raw decode-volume distribution. The `STATIONS` bar checks whether the footprint is broad or driven by only a few active stations. These bars are essential because SNR deltas alone can hide decode/no-decode behavior.
* **High-resolution export:** The toolbar above each map can render a 300 DPI version for publication-quality screenshots without blocking the normal interactive workflow.

#### 4.2 Segment Inspector, Station Insights and Drill-Down

The Segment Inspector is the audit layer below the maps. Select a distance ring and compass direction to inspect the raw evidence behind one segment.

1. **Absolute modes:** The histogram shows normalized SNR values for contributing stations. The x-axis is based on station medians. The red dashed line marks the final segment median.
2. **Compare modes:** The histogram shows Delta SNR values. It reveals whether a segment median comes from consistent superiority or from a broad, unstable distribution.
3. **Station Insights:** The table lists contributing remote stations. For compare modes, it separates joint decodes from exclusive decodes and shows the station-level median Delta SNR.
4. **Drill-Down:** Clicking a Station Insights row opens the cycle-level evidence. In normal compare modes, every joint WSPR cycle shows the paired SNR values and the resulting Delta SNR.
5. **Local Median Neighborhood Drill-Down:** For the median-neighborhood method, the Drill-Down expands the reference pool. Instead of showing a generic `Ref Pool` row only, it lists the individual local reference stations that contributed in that cycle, their locator, distance, normalized reference SNR, the cycle's aggregated neighborhood median, your SNR and the resulting Delta SNR. This lets you reconcile the median directly.
6. **Sequential TX A/B Drill-Down:** For TX A/B, the Drill-Down shows time windows rather than same-cycle pairs. It exposes `Micro-Med A`, `Micro-Med B` and the resulting bin Delta. Opposing micro-medians are hidden in single-setup rows so that missing paired data is not mistaken for zero.
7. **Raw Spots Toggle and Async Both:** `Show Non-Joint` reveals isolated decodes. Missing SNR is shown as `None`, not `0.0`. If both setups hear a station but never in the same WSPR cycle, the yield chart can show `Async Both`.
8. **Filtering and export:** Multi-select, dynamic filters and CSV export turn the Segment Inspector into a reproducible raw-data audit surface.

### 5. Core concepts: Absolute vs. Compare

#### 5.1 Absolute analyses

Absolute analyses answer: **is there an open path?**

* **TX Absolute:** isolates spots where your callsign is the transmitter. The map plots receiving stations that decoded you. This measures real-world transmit reach and skip zones, normalized to 1 W where reported power is available.
* **RX Absolute:** isolates spots where your callsign is the receiver. The map plots transmitters your station decoded. This measures real-world receive reach and sensitivity, normalized for the remote transmitter's reported power.

Absolute maps are excellent for coverage and propagation questions. They are not, by themselves, fair hardware comparisons because propagation, transmitter powers, receiver noise floors and station activity are not controlled.

#### 5.2 Comparative and benchmark analyses

Comparative analyses answer: **how did my station/setup perform relative to a benchmark under matching conditions?**

The core idea is pairing. For TX comparisons, two transmit signals are evaluated by the same remote receiver where possible. This strongly reduces the influence of that receiver's noise floor and antenna. For RX comparisons, two receivers evaluate the same remote transmitter where possible. This strongly reduces the influence of remote transmitter power and shared propagation.

This is powerful, but the correct scientific wording is **confounder reduction**, not perfect elimination. WSPR remains a crowd-sourced observational dataset.

#### 5.3 The bivariate evaluation model

A pure median Delta SNR analysis can suffer from survivorship bias. A better antenna may decode very weak signals that a worse antenna misses. Those extra marginal spots can lower the better antenna's median SNR if everything is pooled naively.

WSPRadar therefore separates two signals:

1. **System Sensitivity / Decode Yield:** counts exclusive vs joint decodes. This captures reach at the edge of decodability.
2. **Hardware Linearity / Delta SNR:** uses only paired joint spots or paired time bins. This estimates the conditional gain/SNR difference when both setups produced comparable evidence.

Read both together. A setup can have better yield but lower conditional SNR if it decodes many marginal signals. Conversely, a setup can show a strong positive Delta SNR on joint spots but poor yield if it misses many weak paths.

### 6. Comparative methods

#### 6.1 Local Median Neighborhood

This is the default local benchmark and the recommended first answer to: **am I doing okay for my area?**

WSPRadar collects active WSPR stations within the selected neighborhood radius, up to the configured maximum. For every WSPR cycle and every matching remote path, it computes the median normalized SNR of all active local reference stations in the radius. Your station is then compared against that cycle-level neighborhood median.

Scientific interpretation:

* It estimates the central performance of your active local WSPR environment.
* It is robust against one unusually strong or weak local station.
* It does not invent numeric values for missing spots. If a neighbor did not decode or was not decoded in that cycle, that missing observation is not treated as `0 dB`.
* With an even number of local reference stations, the midpoint median is used.
* The reference pool may change by cycle because WSPR activity changes by cycle.

Best use:

* General self-assessment.
* RX/TX neighborhood benchmarking.
* Detecting whether you are consistently above or below the local central tendency.

#### 6.2 Local Best Station

This is the strict version of the local benchmark. For every cycle and remote path, WSPRadar compares you against the strongest active local station in the selected radius.

Scientific interpretation:

* It is a best-local-peer envelope.
* The identity of the reference station can change from cycle to cycle.
* It answers: **if the best active local station reached or heard this path, how did I compare?**
* It is intentionally harder to beat than the median neighborhood.

Best use:

* Stress-testing your station against strong local performers.
* Finding distance/azimuth regions where your station underperforms the local best case.
* Avoiding the mistaken conclusion that "local benchmark" means "local average".

#### 6.3 Specific Reference Station (Buddy Test)

The Buddy Test is a one-to-one comparison against a known station. You define a different reference callsign, for example a radio friend 10 km away. WSPRadar isolates cases where both signals are decoded by the same remote receiver in the same 2-minute WSPR cycle, or where both receivers decode the same remote transmitter in the same cycle.

This is strong when both stations are active at the same time and share enough remote peers. It remains a station-vs-station comparison, so differences can include antenna, receiver, transmitter, local noise, feedline, siting, polarization and local terrain.

#### 6.4 Hardware A/B Test

The Hardware A/B Test is for your own equipment at your own location. It is valid only when every non-tested variable is held as constant as practical: band, time window, power, feedline losses, receiver chain, audio chain, decoding software and locator reporting.

**RX A/B Test (simultaneous):**

Two parallel receivers decode the same remote WSPR transmissions simultaneously. To prevent the reporting network from treating the streams as duplicate reports, the two receivers must report distinguishable callsigns or suffixes, for example your primary callsign for Setup A and a suffix for Setup B. The two audio/storage paths must be physically separated. Appendix A gives a WSJT-X instance-separation workflow.

**TX A/B Test (fixed-schedule sequential):**

Setup A and Setup B cannot transmit at the same time on the same callsign. WSPRadar therefore uses deterministic time slicing. A transmitter or controller assigns one setup to a fixed slot pattern and the other setup to the opposite slot pattern. The tool groups the data into time bins, computes a micro-median for each setup inside a bin, and then calculates the bin Delta.

This is a practical engineering compromise. It is defensible when the run is long enough, ideally multiple days and complete daily cycles, because many short-term propagation effects average down. However, because the assignment is fixed rather than randomized, time-correlated effects cannot be claimed to be mathematically eliminated. The correct claim is: **fixed-schedule multi-day TX A/B reduces time-confounding substantially and provides evidence from paired time bins.**

Hardware note: such a test requires deterministic scheduling. A QMX transceiver, for example, can be programmed with fixed timing such as `frame=10` and `start=2`. Standard WSJT-X random transmission behavior is not suitable for fixed-schedule TX A/B without additional scheduling control.

Why avoid multi-cycle WSPR suffixes for single-transmitter TX A/B? Compound callsigns can force multi-message behavior and reduce decode yield because not all receivers decode every required message type equally well. Artificial suffixes such as `/1` or `/2` may also be jurisdiction-specific or invalid. `/P` should only be used when it is legally appropriate for the actual operation. For TX A/B, WSPRadar therefore prefers fixed timing with the normal callsign.

### 7. Scientific method and assumptions

#### 7.1 Data provenance

WSPRadar reads historical WSPR spots through wspr.live. The wspr.live documentation states that the data is raw data as reported and published by WSPRnet, and warns that duplicates, false spots and other errors may exist. It also states that the volunteer-run infrastructure gives no guarantees on correctness, availability or stability.

Implication: WSPRadar can make the analysis auditable and internally consistent, but it cannot make the upstream data calibrated or error-free.

The wspr.live database query interface is GET-only for direct database access; POST requests are not allowed. Long-query risk must therefore be handled by bounded time windows, band/time filters, query shortening and chunking where needed, not by switching this endpoint to POST.

#### 7.2 WSPR protocol, SNR and reported power

WSPR is designed for probing potential propagation paths with low-power beacon-like transmissions. WSPR messages carry a callsign, locator and power level in dBm. WSPR-2 transmissions last about 110.6 seconds and start two seconds into even UTC minutes. The ARRL WSPR documentation describes the minimum S/N on the WSJT scale using a 2500 Hz reference bandwidth.

For WSPRadar interpretation:

* SNR is a reported decoder value in dB on the WSPR/WSJT scale, referenced to 2500 Hz.
* Reported transmit power is part of the WSPR message. It is not independently verified by WSPRadar.
* User-entered dBm may differ from transmitter output, feedpoint power or EIRP because of calibration error, foldback, feedline loss, tuner loss and antenna mismatch.

#### 7.3 Power normalization

To compare spots reported with different transmit powers, WSPRadar normalizes SNR to a 1 W / 30 dBm reference:

$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$

This is essential for absolute TX/RX maps and local TX comparisons. It removes the reported-power term from the comparison, but only as well as the reported power is correct. It does not correct antenna gain, feedline loss, calibration error or EIRP differences.

#### 7.4 Geographic rastering and projection

Spatial data is rendered in an Azimuthal Equidistant projection centered on the user's Maidenhead locator. The map engine uses an internal spherical Earth radius of 6371 km so that table distances and plotted map positions are consistent with the same geometry.

The map uses:

* concentric radial bins of 2500 km, approximating useful propagation-distance bands;
* azimuth wedges such as 22.5 degree compass sectors;
* unique segment identifiers for aggregation and inspection.

The projection is internally consistent for WSPRadar's visual analysis. It should not be described as geodetic truth at survey precision.

#### 7.5 Median aggregation hierarchy

WSPRadar uses medians to reduce the influence of outliers and unequal station activity.

* **Cycle-level median:** in Local Median Neighborhood, the reference for one WSPR cycle/path is the median of active local reference stations in that cycle.
* **Station-level median:** for a given remote station, WSPRadar computes the median of the qualifying spot or bin values.
* **Segment-level median:** the final map segment value is the median of station-level medians.

This "median of medians" structure reduces receiver-density bias. A dense receiver cluster should not drown out a sparse region merely because it generated more rows.

#### 7.6 Temporal synchronization and heartbeat filter

WSPRadar validates comparative cycles only when your setup was demonstrably alive.

* In TX mode, your signal must have been decoded by at least one station worldwide during the relevant cycle/slot.
* In RX mode, your receiver must have decoded at least one station during the relevant cycle.

This heartbeat filter reduces offline bias. If you shut the station down overnight, reference spots collected during that offline period are not counted as defeats for your hardware. It does not make every comparison perfectly fair; it specifically guards against penalizing missing data caused by your station being offline.

#### 7.7 Statistical confidence and Wilcoxon filtering

WSPRadar can use a Wilcoxon signed-rank test as an optional compare-map filter. SciPy documents this as a test for related paired samples and specifically frames it around the distribution of paired differences.

Correct interpretation:

* The test is useful as a robustness screen for paired Delta SNR values.
* A p-value is not an effect size.
* Segment-level p-values create multiple-comparison risk across the map.
* WSPR SNR values are quantized and often temporally autocorrelated; this weakens ideal textbook assumptions.
* Zero differences and ties require care, which SciPy also documents.

Therefore, Wilcoxon filtering should be documented as statistical evidence, not proof. A scientifically stronger future version could add bootstrap confidence intervals and false-discovery-rate correction across map segments.

#### 7.8 Evidence strength and reproducibility

Suggested evidence language:

* **Weak evidence:** very few joint cycles, very few stations, or a result driven by one outlier station.
* **Usable evidence:** multiple stations per segment, several joint cycles or bins per station, consistent Delta SNR direction and coherent yield behavior.
* **Strong evidence:** repeated across multiple days or separate runs, stable across adjacent segments or bands where expected, not dominated by one station, and supported by exported raw data.

Reproducibility checklist:

* WSPRadar version or Git commit.
* UTC start/end time.
* Band.
* TX/RX direction.
* Benchmark mode and local benchmark method.
* Neighborhood radius or reference callsign.
* Target/reference locators.
* Min spots/station and min stations/segment.
* Solar-state filter.
* Excluded prefixes and moving-station filter.
* Wilcoxon setting.
* Exported CSV and screenshots of map and Segment Inspector.

### 8. Experiment design appendix

**Local Median Neighborhood:**

Use this first for a practical local baseline. Start with a radius that gives enough active peers without mixing very different propagation environments. In dense regions, a smaller radius may be more representative. In sparse regions, a larger radius may be necessary but less local.

**Local Best Station:**

Use this when you intentionally want a hard target. Do not describe it as average local performance. It is the best active local peer for each path/cycle.

**Buddy Test:**

Pick a reference station whose location, power, antenna and operating schedule you understand. Use the same band and overlapping time windows. Interpret differences as station-system differences, not pure antenna gain.

**RX A/B Test:**

Use two genuinely independent receive chains. Avoid feeding both decoders from the same audio file or same virtual audio path. Use distinct reporting identities so both streams appear in the WSPR database. Confirm that both receivers are time synchronized.

**TX A/B Test:**

Use deterministic fixed timing. Keep power, feedline, tuner settings and band identical except for the tested variable. Run long enough to include day/night changes if those are relevant. Multi-day runs are preferable because fixed-slot time effects average down better over complete daily cycles. Still, avoid claiming perfect time-confound elimination.

**Minimum samples:**

There is no universal magic number. For exploratory work, inspect all visible results but label them as exploratory. For serious claims, require enough joint spots or bins to inspect the distribution, not only the final median. For publication-style claims, include the exported data and repeat the experiment.

### 9. Configuration reference

**Core parameters:**

* **Target Callsign:** primary station under evaluation.
* **QTH Locator:** mathematical center of the map projection. Use a valid 4- or 6-character Maidenhead locator.
* **Band and timeframe:** define the WSPR data window. Time is handled in UTC.

**Comparison parameters:**

* **Benchmark Mode:** `Local Neighborhood Benchmark`, `Reference Station (Buddy Test)` or `Hardware A/B-Test`.
* **Local Benchmark Method:** `Local Median Neighborhood` by default, or `Local Best Station` for a strict best-peer envelope.
* **Neighborhood Radius:** geographic boundary for local reference stations.
* **Reference Callsign:** external counterpart for Buddy Test.
* **A/B-Test Setup:** simultaneous `RX Test` or fixed-schedule `TX Test`.
* **Target/Reference Locator:** 6-character locators used to separate simultaneous RX streams.
* **Target/Reference Time Slot:** fixed slot assignment for sequential TX tests.
* **Time Window (Bins):** bin size for sequential TX A/B pairing.

**Advanced settings:**

* **Local QTH Solar State:** filters by calculated solar elevation at your QTH: daylight, nighttime or greyline.
* **Exclude Prefixes:** comma-separated list of callsign prefixes or callsigns to exclude, for example telemetry balloons or known unwanted sources.
* **Exclude Moving Stations:** removes stations that change their 4-character locator during the analysis window, such as balloons, mobile or maritime stations.
* **Map Scope:** visual map radius.
* **Min. Spots/Station:** filters one-hit wonders and adapts to the selected comparison mode.
* **Min. Stations/Segment:** minimum station count for rendering a segment.
* **Compare Map Statistical Confidence:** optional Wilcoxon-based filtering.

### 10. Limitations, disclaimer and license

**Limitations:**

* **Crowd-sourced data:** WSPR spots can contain duplicates, false spots, wrong power, wrong locator or receiver-side errors.
* **Successful decodes only:** WSPR logs decodes, not all failed reception attempts. Dead bands do not lower the absolute median; they reduce the existence of spots.
* **Reported power caveat:** normalization assumes reported dBm is correct.
* **Sequential TX caveat:** fixed-schedule TX A/B reduces but does not perfectly eliminate time confounding.
* **Distance is not angle:** distance-ring patterns can suggest propagation behavior but do not directly measure radiation take-off angle.
* **Polarization and local environment:** WSPRadar measures real-world station-system performance, including antenna, receiver/transmitter, feedline, terrain, polarization effects, local QRM and software behavior.
* **Performance limits and latency:** query windows are capped to protect database resources, and fresh spots can take roughly 15 to 30 minutes to appear.

**Disclaimer:**

WSPRadar is an experimental open-source project provided "as is" without warranties. The source code and mathematical model can be audited, but the developer cannot guarantee accuracy, completeness, availability or suitability for any particular purpose. Do not make major financial decisions, such as buying or selling expensive antennas or radio hardware, based solely on WSPRadar output.

**License:**

WSPRadar is free software under the GNU Affero General Public License (AGPLv3). The license ensures that the source code, including network-service modifications, remains available to the amateur-radio community.

### Appendix A: Parallel operation of multiple WSJT-X instances

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

### References

* ARRL, WSPR technical overview: https://www.arrl.org/wspr
* wspr.live documentation and database disclaimer: https://wspr.live/
* SciPy Wilcoxon signed-rank documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html
* WSJT-X User Guide, WSPR and SNR reference bandwidth: https://wsjt.sourceforge.io/wsjtx-doc/wsjtx-main-3.0.0.html
