# docs/doc_en.py

"""
English manual for WSPRadar.
Used in the Web UI and for PDF export.
"""

DOC_EN = r"""
---

### Table of Contents
* [1. Introduction and Objective](#sec-1)
* [2. Key Use Cases and Capabilities](#sec-2)
* [3. Core Concepts: Absolute vs. Compare](#sec-3)
  * [Absolute Analyses (Pure Propagation)](#sec-3-1)
  * [Comparative and Benchmark Analyses (The Hardware Difference)](#sec-3-2)
  * [The Bivariate Evaluation Model (Addressing Survivorship Bias)](#sec-3-3)
* [4. Methods for Comparative Analysis](#sec-4)
  * [Option 1: Local Environment (Nearest Peers / Radius Benchmark)](#sec-4-1)
  * [Option 2: Specific Reference Station (Buddy Test)](#sec-4-2)
  * [Option 3: True Hardware A/B Test (Self-Test)](#sec-4-3)
* [5. General Data Methodology](#sec-5)
  * [5.1 Power Normalization](#sec-5-1)
  * [5.2 Geographic Rastering and Projection](#sec-5-2)
  * [5.3 Spatial Normalization (Median Aggregation)](#sec-5-3)
  * [5.4 Temporal Synchronization (Heartbeat Filter / Offline Penalty Protection)](#sec-5-4)
* [6. Visual Interpretation and Segment Inspector](#sec-6)
  * [6.1 Visual Guide (Map Elements)](#sec-6-1)
  * [6.2 Detailed Evaluation: Segment Inspector (Histogram and Tables)](#sec-6-2)
* [7. Configuration and Parameter Reference](#sec-7)
  * [7.1 Core Parameters](#sec-7-1)
  * [7.2 Comparison against References and A/B Testing](#sec-7-2)
  * [7.3 Advanced Config and Expert Settings](#sec-7-3)
* [8. Discussion, Limitations and Disclaimer](#sec-8)
* [Appendix A: Setup: Parallel Operation of Multiple WSJT-X Instances](#sec-a)

<a id="sec-1"></a>
### 1. Introduction and Objective

In amateur radio, evaluating antenna performance has traditionally relied on anecdotal signal reports or manual A/B switching. However, these methods are subject to significant confounding variables: rapid ionospheric fading (QSB), inconsistent remote transmitter power levels, and localized noise floors (QRM). These unpredictable factors make it incredibly difficult to objectively measure how well an antenna is truly performing on a day-to-day basis.

This is where the **Weak Signal Propagation Reporter (WSPR)** protocol changes the game. WSPR is a digital mode designed for probing potential propagation paths using low-power, two-minute beacon transmissions. Every day, thousands of stations worldwide autonomously transmit and receive these beacons, logging millions of highly precise Signal-to-Noise Ratio (SNR) reports into a public database. By participating in WSPR, you effectively turn your station into a calibrated global probe, continuously gathering hard data on exactly where your signal lands and who you can hear. 

The objective of **WSPRadar** is to harness this massive, crowdsourced dataset to provide a systematic, semi-quantitative framework for evaluating your transmit (TX) and receive (RX) antennas. By extracting historical WSPR spot data from the wspr.live repository, this tool applies strict spatial and temporal normalization. It mathematically strips away atmospheric volatility and unequal power levels to isolate the one metric that actually matters: your antenna system's raw hardware efficiency and radiation pattern.

<a id="sec-2"></a>
### 2. Key Use Cases and Capabilities

WSPRadar was developed to precisely answer specific, common questions in amateur radio:
* **Path Viability & Skip Zones (Is there an opening?):** Does my signal reach Oceania today? Where are my blind spots? *(Solved via Absolute Analyses for TX and RX).*
* **The "Am I doing okay?" Test (Local Benchmarking):** Is my station performing above or below average compared to others in my region? *(Solved via the Radius Benchmark).*
* **Buddy-Testing (Station vs. Station):** My friend 10 km away uses a Yagi, I use a dipole. Who is better today? *(Solved via the Specific Reference Station test with synchronous evaluation).*
* **The Hardware Laboratory (True A/B Tests):** I need an isolated lab setup for Antenna A vs. B, RX vs. RX, or TX vs. TX at my own location. *(Solved via the Hardware A/B-Test mode).*
* **DX vs. NVIS Profiling (Assessing Take-Off Angle):** Is my antenna a low-angle radiator (DX) or high-angle (NVIS)? *(Readable by analyzing performance in near vs. far distance rings on the map).*
* **Uncovering Local QRM (The "Alligator Test"):** Am I heard worldwide but hear nothing myself? *(Provable by combining a TX and RX compare run against the exact same reference).*
* **Statistical Proof vs. Guesswork:** Is a measured 2 dB advantage physically real or just random noise? *(Solved by the integrated Wilcoxon Test for statistical significance).*

**💡 Quick Start:** Click `✨ Load Demo Config` in the configuration panel, then `Run TX` or `Run RX` to instantly test the tool with sample data. *(Note: The current demo data is configured for the Reference Radius comparison only and is a bit sparse; more comprehensive demo datasets will follow soon).*

<a id="sec-3"></a>
### 3. Core Concepts: Absolute vs. Compare

To draw reliable conclusions from WSPR data, WSPRadar strictly separates its analysis into two distinct perspectives:

<a id="sec-3-1"></a>
#### Absolute Analyses (Pure Propagation)
These answer the question "Is there an open path?". Because propagation conditions can be highly asymmetrical, WSPRadar generates two strictly separate views for this:
* **TX Absolute:** *Where is my transmitted signal heard?* Isolates all instances where your callsign is the transmitter. The map plots all worldwide **receiving stations** that successfully decoded your signal. Measures your pure transmit capability and shows your skip zones (normalized to 1 Watt).
* **RX Absolute:** *Who can my station hear?* Isolates all instances where your callsign is the receiver. The map plots all worldwide **transmitting stations** that your station successfully heard. Measures your pure receive sensitivity and visualizes open paths to your location (normalized based on the remote transmitter's power).
  Both maps show your global blind spots. If you want to know if your signal reaches Oceania today (or if you can hear Oceania), you look at the Absolute Maps.
  
<a id="sec-3-2"></a>
#### Comparative and Benchmark Analyses (The Hardware Difference)
These answer the question "Am I better than Setup B?". In the Compare map, the local noise floor (QRM) at the remote station and rapid ionospheric fading (QSB) are mathematically *completely eliminated*. What remains is exclusively the pure difference ($\Delta$ SNR) between the two tested hardware setups, broken down by geographic segments. This is the ultimate tool for performance benchmarking.
* **For TX Comparisons:** Both transmitting signals are evaluated by the identical remote receiver simultaneously. Thus, the remote receiver's local noise floor (QRM) and antenna gain are functionally canceled out. Calculation: $\Delta SNR_{TX} = SNR_{norm,target} - SNR_{norm,benchmark}$
* **For RX Comparisons:** Both local receivers evaluate the identical remote transmission simultaneously. Thus, the remote transmitter's power and the baseline propagation path are identical. Any difference in SNR is strictly due to your receiving antenna's efficiency and your local QRM. Calculation: $\Delta SNR_{RX} = SNR_{measured,target} - SNR_{measured,benchmark}$

<a id="sec-3-3"></a>
#### The Bivariate Evaluation Model (Addressing Survivorship Bias)
When comparing two setups, relying solely on the median SNR difference ($\Delta$ SNR) can lead to a statistical trap known as 'Survivorship Bias'. A superior antenna will decode ultra-weak signals at the extreme noise floor that an inferior setup completely misses. These additional marginal spots lower the median SNR of the superior setup, making it look artificially worse if simply averaged together. To solve this, WSPRadar uses a strict Bivariate Model:
1. **System Sensitivity (Decode Yield):** Analyzes the absolute count of exclusive vs. joint decodes to prove performance and reach at the extreme noise floor.
2. **Hardware Linearity ($\Delta$ SNR):** Calculated *strictly* on Joint Spots (signals decoded by both setups simultaneously in the same 2-minute window, or within the same defined time-bin in a sequential test) to prove physical gain differences under identical propagation conditions.

<a id="sec-4"></a>
### 4. Methods for Comparative Analysis

WSPRadar offers three fundamental pillars for comparative hardware testing, depending on what you want to prove. An A/B test is physically only valid if *all* other variables remain identical (e.g. testing Antenna A vs. B using the same transmitter).

<a id="sec-4-1"></a>
#### Option 1: Local Environment (Nearest Peers / Radius Benchmark)
* **Objective:** Measure your capability against the best stations in your immediate neighborhood.
* **Methodology:** WSPRadar aggregates up to the 25 closest local WSPR stations within a defined radius (max 250 km). Since it's assumed these stations share the same macro-propagation conditions, this provides a hard statistical benchmark of whether your QTH or antenna is performing above or below average. It applies strict *Cycle-by-Cycle (Spot-by-Spot)* mathematics: In every single 2-minute WSPR cycle, the engine dynamically determines the "Best Peer" reference station from your local cloud – the neighbor who achieved the best SNR in that exact minute. The benchmark asks: *"If the best station in your direct vicinity reached/heard this DX station, how did you perform in direct comparison?"* This simulates a "virtual macro antenna" and serves as the toughest and fairest gauge.

<a id="sec-4-2"></a>
#### Option 2: Specific Reference Station (Buddy Test)
* **Objective:** A 1-to-1 comparison with a known ham radio operator (location vs. location, antenna vs. antenna, or simply station vs. station).
* **Methodology:** You define a different reference callsign (e.g. a radio buddy 10 km away). Because you are both on the air under different callsigns, the database seamlessly collects all spots. WSPRadar isolates instances where both signals were decoded by the *exact same remote receiver* during the *exact same 2-minute WSPR cycle*. The *Spot-by-Spot (Synchronous)* mathematics eliminates fading completely on a bit-level.

<a id="sec-4-3"></a>
#### Option 3: True Hardware A/B Test (Self-Test)
* **Objective:** A precise laboratory test of your own hardware at your own location using your own callsign. This goes far beyond the classic comparison: As long as all other parameters remain identical, you can isolate and test any variable here. Compare receiver vs. receiver (RX vs. RX), transceiver vs. transceiver (TX vs. TX), different baluns/feedlines, or evaluate the exact mounting position of an antenna within the same property (Location A vs. Location B). WSPRadar splits into two special computational paths depending on the test direction:
* **The RX A/B Test (Simultaneous):** Two parallel receivers (SDRs) evaluate WSPR signals simultaneously. **The Trick:** So that the WSPR network doesn't delete the synchronous spots of your receivers as duplicates, you must specify different callsign suffixes in your receiving software (e.g. WSPRdaemon). *➔ Guide on setting up dual WSJT-X instances in [Appendix A](#sec-a).*
  * **Setup A:** Reports using your primary callsign (e.g., `DL1MKS`).
  * **Setup B:** Reports using a distinct suffix (e.g., `DL1MKS/P`).
  In WSPRadar's Self-Test mode, you enter these two callsigns. The tool then generates perfect joint-spots via *Spot-by-Spot (Synchronous)* mathematics for the ultimate receive setup comparison.
* **The TX A/B Test (Sequential / Time-Slicing):** You use two identical WSPR transmitters or a transceiver that periodically switches between transmitting to Antenna A and Antenna B based on timing. Since Setup A and B *never* transmit in the same slot, WSPRadar uses a **Time-Binning Architecture (Paired Samples)**: It slices the time axis into fixed blocks (e.g., 8 minutes). Within each block (bin), a micro-median for Setup A (odd minutes) and a micro-median for Setup B (even minutes) is formed before calculating the exact $\Delta$ SNR of that block. This smooths out rapid QSB and completely eliminates long-term macro-fading. *(Because Setup A and B never transmit in the exact same slot, WSPRadar defines a 'Joint Bin' in this mode as a time window in which both setups were successfully decoded.)*
  * *Note on TX Hardware:* Such a test requires hardware capable of deterministic scheduling. A QMX transceiver, for example, can be programmed exactly (`frame=10` transmits every 10 minutes, `start=2` begins exactly at minute 2). The standard WSJT-X software transmits randomly out-of-the-box and is not suitable for fixed-schedule A/B tests without special add-on tools.
  * *Why avoid Multi-Cycle WSPR with a single TX (callsign suffixes like /1 or /P) for TX?* WSPR messages with compound suffixes force the protocol to transmit across multiple cycles (Type 1 and Type 3 messages). Because many global receiving stations fail to reliably decode Type 3 messages from the noise, the absolute number of logged spots for compound callsigns drops drastically. Furthermore, artificial suffixes like `/1` or `/2` are not officially approved callsign structures, and using `/P` is strictly only permitted when actually operating portable. Therefore, WSPRadar's TX A/B test relies exclusively on time-slicing using your *identical* standard callsign, mathematically separating the signals based on even/odd minutes to retain 100% of the global network's decoding performance.

<a id="sec-5"></a>
### 5. General Data Methodology

<a id="sec-5-1"></a>
#### 5.1 Power Normalization
To enable direct comparison between stations operating with different hardware configurations, all absolute signal-to-noise ratio (SNR) data is normalized to a standard 1-Watt (30 dBm) reference. 
$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$
This normalization is applied to both TX and RX absolute analyses, eliminating transmitter power as an independent variable and isolating the antenna system's intrinsic efficiency and take-off angle.

<a id="sec-5-2"></a>
#### 5.2 Geographic Rastering and Projection
Spatial data is mapped using an Azimuthal Equidistant Projection centered on the user's defined Maidenhead locator. The map rendering engine is explicitly locked to a perfect mathematical sphere (Radius = 6371 km) to guarantee 100% geometric consistency between the calculated data tables and the visual map plotting, avoiding standard WGS84 ellipsoid distortions.
* The map is divided into a dynamic zone model, utilizing concentric radial bins of 2,500 km (approximating a typical F2-layer hop).
* Azimuthal wedges are divided into discrete degrees (e.g., 22.5°) to account for spatial density.
* Each resulting geographic segment is assigned a unique coordinate identifier for data aggregation.

<a id="sec-5-3"></a>
#### 5.3 Spatial Normalization (Median Aggregation)
To mitigate spatial bias caused by disproportionate receiver density in specific regions, the tool employs a two-step "Median of Medians" aggregation:
1. **Station-Level Aggregation:** The median SNR of all spots is calculated for each unique remote station.
2. **Segment-Level Aggregation:** The median of these station-level values is calculated to determine the final value for the geographic segment. 
This method prevents "Receiver Density Bias"—where dense receiver clusters (e.g., in Europe or North America) statistically drown out sparse regions (e.g., in Asia or Africa) in global averages. Every geographic wedge gets a fair, isolated evaluation, ensuring that a single highly active station does not statistically overpower a region.

<a id="sec-5-4"></a>
#### 5.4 Temporal Synchronization (Heartbeat Filter / Offline Penalty Protection)
To prevent your setup from accumulating unfair penalties (defeats) while your radio, software, or PC was actually powered off, WSPRadar applies a system-wide, strict **Heartbeat Filter** across all comparative modes. A 2-minute cycle is only validated in the comparative analysis if your setup was demonstrably "alive" (online) during that exact minute.

* **In TX Mode (Transmitting):** Your signal must have been decoded by *at least one* station worldwide during that cycle. This proves that your transceiver actually transmitted in that timeslot.
* **In RX Mode (Receiving):** Your receiver must have decoded *at least one* station (local or worldwide) during that cycle. This proves that your software was running and the antenna was connected.

This mechanism eliminates the so-called **Offline Penalty**. If you shut down your computer at night, your reference cloud will continue to collect thousands of spots, but WSPRadar will not count these as defeats for your antenna. This ensures a 100% fair, physical Win/Loss ratio.

<a id="sec-6"></a>
### 6. Visual Interpretation and Segment Inspector

<a id="sec-6-1"></a>
#### 6.1 Visual Guide (Map Elements)
* **Heatmaps:** Absolute modes render in raw dB. Comparative modes (Compare) map the Δ SNR using a standardized S-Unit scale (1 S-Unit = 6 dB). Positive values (red) indicate superiority over the benchmark; negative values (blue) indicate a systemic weakness.
* **Distance Rings (Take-Off Angle):** When analyzing the map, note the distances: Superiority in inner rings (e.g., < 2500 km) indicates good NVIS capabilities (high take-off angle), whereas dominance in outer rings (> 10000 km) proves a low take-off angle suitable for DX.
* **Scatter Plots:** Individual stations are plotted as dots. Green dots indicate jointly decoded stations (in the exact same 2-minute cycle). Yellow-orange dots represent stations heard by both, but asynchronously. Purple dots represent exclusive decodes by your own station ("Only [Target]"), while white dots indicate stations decoded only by the reference station ("Only Reference").
* **Pole Markers:** To aid in spatial orientation, the exact geographic North Pole (N-POL) and South Pole (S-POL) are marked with neon-green crosses.
* **Map Footer & 1D-Venn Diagrams** The main map features 100%-scaled horizontal stacked bar charts at the bottom. These 1D-Venn diagrams instantly visualize relative system sensitivity without Survivorship Bias. 
  * The **SPOTS** bar shows the raw data volume distribution.
  * The **STATIONS** bar validates the true geographic footprint (ensuring that a high exclusive spot count isnt just generated by a single loud station). 
The bars are color-matched to the map markers: Purple (Setup A Only), Green (Joint), and White (Setup B Only). The absolute counts are printed directly inside the blocks.

* **High-Res Export:** Located above each map is a discreet toolbar ("⚙️ Render High-Res Map"). This allows for the on-demand rendering and downloading of a lossless, print-ready 300 DPI version of the current map without blocking the interactive user interface with loading times.

<a id="sec-6-2"></a>
#### 6.2 Detailed Evaluation: Segment Inspector (Histogram and Tables)
Directly below the maps, you will find a Segment Inspector with two cascading dropdown menus. This allows you to select a specific distance and then a compass direction (e.g., NNE) to analyze its underlying data distribution in detail.
*Note: The Segment Inspector is the direct visual implementation of the Bivariate Evaluation Model from **Chapter 3**. The Yield Bar on the left displays the absolute decode yield (System Sensitivity), while the histogram on the right depicts the pure gain difference (Hardware Linearity) using only the true Joint Spots.*
1. **Absolute Modes:** Displays the distribution of normalized SNR values (`Norm@1W`) for all stations within that segment using a discrete bar chart. The X-axis displays the individual *Station Medians*. The red dashed line marks the final aggregated *Segment Median* calculated from all these underlying values.
2. **Compare Modes:** Displays the distribution of Δ SNR values. This is crucial for determining whether a close median value is the result of consistent superiority (a tight bell curve) or extreme variance. The X-axis displays the individual *Station Medians* (the first-order aggregation). The red dashed line explicitly marks the final aggregated *Segment Median* (the "median of medians" across all stations in this segment).
3. **Station Insights Table:** Below the histogram, an interactive data table lists the exact remote stations involved in the selected segment. By default, for clarity, only stations with successful `Joint Spots` (or `Joint Bins` for sequential TX A/B tests) are listed. The "Median Δ SNR" column shows the merged value for exactly this one station. In comparative modes, the table also details how many joint decodes (`Joint Spots` / `Joint Bins`) form this value and how many exclusive decodes (`Only Ref` or `Only [Callsign]`) exist.
4. **Drill-Down Data (Raw Data & Export):** Clicking a row in the "Station Insights" table opens a detailed view for that specific station, revealing every single 2-minute cycle (spot). In Compare mode, you see the raw Δ SNR values of the individual spots whose median forms the "Station Median" in the parent table. *In the sequential TX A/B test*, this table reveals the aggregated time-windows (Time-Bins) along with their corresponding `Micro-Med A` and `Micro-Med B` values, and the resulting `Bin Delta`. Opposing micro-medians are transparently hidden in single-setup rows. In Radius analysis, you will also find the `Best Ref` and `Ref km` columns, strictly identifying exactly which local neighbor you competed against in that specific cycle and how many kilometers away they were.
5. **Raw Spots Toggle & Async Both:** Using the "Show Non-Joint" toggle, you can drop the "joint-wall" and reveal completely isolated decodes in the table. For cycles where you or the reference remained deaf, the SNR column transparently displays `None` instead of a misleading `0.0`. The System Sensitivity Bar Chart (Yield) dynamically expands in this context: If there were stations decoded by both setups but never in the same 2-minute cycle (e.g., due to fading), an additional `Async Both` bar appears.
Thanks to the multi-select function, multiple stations can be marked simultaneously via Shift-Click, or *all* stations in the segment can be selected directly using the checkbox in the table header. This generates a complete raw data audit in seconds. Instead of basic native tools, the interactive tables feature a custom Excel-style dynamic filter system via the `Filter` button (funnel icon). This allows you to apply precise numerical range sliders or categorical dropdown selections to both the Master Table and the Drill-Down Data. You can still use the native toolbar (top right on hover) to search the data or download the entire dataset as a **CSV file** with one click for further analysis in Excel.

<a id="sec-7"></a>
### 7. Configuration and Parameter Reference

<a id="sec-7-1"></a>
#### 7.1 Core Parameters
* **Target Callsign & QTH Locator:** Identifies the primary station under evaluation and establishes the mathematical center (Maidenhead grid) for the Azimuthal Equidistant map projection.
* **Operating Band & Timeframe:** Specifies the frequency band and the temporal window (in hours or absolute dates) to extract the relevant spot data from the database.

<a id="sec-7-2"></a>
#### 7.2 Comparison against References and A/B Testing
* **Benchmark Mode:** Selects the fundamental type of comparison (Reference Radius, Specific Reference Station, or Hardware A/B-Test).
* **Reference Search Radius (km):** Defines the geographic boundary to aggregate local benchmark stations when using the radius mode.
* **Reference Callsign:** The exact callsign of the external counterpart for the buddy test.
* **Test Setup (Hardware A/B Test only):** Toggles between `RX Test (2 Receivers, Simultaneous)` and `TX Test (1 Transmitter, Time-Slicing)`.
* **Target Locator & Reference Locator:** The exact 6-character Maidenhead locators (e.g., JN37AA vs. JN37AB) used to separate data streams during simultaneous RX tests.
* **Target Time-Slot & Reference Time-Slot:** Assigns the transmission cycles (`Even Minutes` vs. `Odd Minutes`) for sequential TX tests.
* **Time Window (Bins) (TX A/B Test only):** Configuration slider for the time-bin size (4 to 16 minutes) used to form pairs.

<a id="sec-7-3"></a>
#### 7.3 Advanced Config and Expert Settings
* **Local QTH Solar State:** To account for diurnal shifts in the ionosphere (e.g., D-layer absorption during the day vs. F2-layer propagation at night), the tool uses the `ephem` astronomical library. It calculates the exact solar elevation at your QTH for every single WSPR spot. You can filter data strictly for `Daylight` (> +6°), `Nighttime` (< -6°), or `Greyline` (between -6° and +6°).
* **Exclude Prefixes:** A text field for a comma-separated list (e.g., "Q, 0, AG6NS") to categorically exclude specific callsigns or known telemetry balloons ("Pico Balloons") from the analyses.
* **Exclude Moving Stations:** A toggle (inactive by default) that automatically filters out all remote stations (balloons, maritime stations `/MM`, mobile cars `/M`) that change their 4-digit Grid Locator during the analysis timeframe. This eliminates statistical noise caused by "jetstream nomads" when measuring stationary antennas.
* **Map Scope (Max Distance km):** Sets the visual zoom factor of the map projection (in kilometers) from the center. Useful for better analyzing regional propagation.
* **Min. Spots/Station (Data Robustness):** To ensure high data robustness against noise and artifacts, this filter prevents random single decodes ("One-Hit Wonders") from skewing the results. The filter philosophy adapts automatically based on your selected comparison mode:
  * **Buddy & A/B Test Modes (Strict Symmetric Filter):** In direct 1:1 comparisons, the filter applies strictly and symmetrically. A station is only classified as *'Joint'* if it meets the minimum spot requirement for BOTH setups independently (Simultaneous: X shared cycles. Sequential: X valid Joint Bins). For exclusive spots (Only Setup A/B), the respective setup must gather at least X spots independently. Stations failing these thresholds are completely omitted from the respective categories, safeguarding the hardware linearity calculations (SNR Delta) from distortion.
  * **Radius Mode (Virtual Macro-Antenna):** When comparing against a geographic radius, the reference stations act collectively as a single 'Virtual Macro-Antenna'. The filter evaluates if the *aggregate sum* of spots from all reference stations in that radius meets the threshold for a specific remote peer. This validates the regional propagation potential (proving a path is open), without letting a single offline or weak reference station disqualify a valid propagation path.
* **Compare Map Statistical Confidence (Wilcoxon Test):** Instead of blindly relying on the median Δ SNR, WSPRadar allows you to enforce strict statistical rigor on Compare maps. For the sequential TX A/B test, this utilizes the true paired arrays of micro-medians from the time-bins. When activated, the Wilcoxon test dynamically overrides the base value of "Min. Stations" upwards (up to 8 minimum stations) for Compare maps to meet the mathematical constraints of the chosen confidence level. Segments failing the p-value test are strictly discarded.

<a id="sec-8"></a>
### 8. Discussion, Limitations and Disclaimer

#### Discussion
WSPRadar transforms anecdotal amateur radio reports into a purely data-driven, quantitative approach. By enforcing strict temporal and spatial synchronization (especially in Compare mode), the tool successfully cancels out the unpredictable volatility of the ionosphere (QSB) and varying local receiver noise floors (QRM). This enables an objective performance evaluation of antenna hardware during real-world operation that would otherwise only be possible with extremely expensive calibrated measurement equipment or drone flights.

#### Limitations
* **Performance Limits & Data Latency:** To preserve server resources, the maximum queryable timeframe is capped at 7 days, and time queries are quantized to 15-minute intervals to optimize global caching. Additionally, the global wspr.live database has a natural aggregation latency of about 15 to 30 minutes before brand new spots appear in the tool after transmitting.
* **Path Viability vs. Uptime:** WSPR inherently logs only successful decodes. Therefore, the absolute median SNR reflects the signal strength *during an open propagation path*. Dead bands do not lower the average.
* **The TX Power Calibration Trap:** WSPRadar is vulnerable to a "Garbage In, Garbage Out" scenario regarding transmit power. The normalization formula assumes the $P_{TX}$ reported in the WSPR packet is the exact power radiated at the feedpoint. If a transceiver automatically folds back power due to a high SWR, or if there is severe feedline loss, the mathematically derived $SNR_{norm}$ will drop. Operators conducting strict A/B tests must physically calibrate their output power with a wattmeter to ensure a reported weakness is attributed to the antenna geometry and not the feedline or transmitter.
* **Polarization:** WSPRadar does not measure isolated free-space antenna gain; it measures real-world system efficiency. This includes polarization matching under real propagation conditions, as the ionosphere heavily influences signals through Faraday rotation.

#### Disclaimer
WSPRadar is an experimental open-source project (Beta) provided "as is" without any warranties of any kind. While the source code and mathematical models are publicly accessible and verifiable, the developer assumes **no liability or responsibility** for the accuracy, completeness, or reliability of the generated data or charts.
Results rely on crowd-sourced WSPR data via a third-party API (wspr.live), which may be skewed by user errors (e.g., misreported TX power levels). **Users should never make financial decisions (such as purchasing or selling expensive radio or antenna equipment) based solely on the output of this tool.** Use entirely at your own risk.

#### License (Open Source)
WSPRadar is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License (AGPLv3) as published by the Free Software Foundation. This license ensures that the source code—even when used over a network (SaaS) and after modifications—must always remain free and open for the amateur radio community.

<a id="sec-a"></a>
### Appendix A: Setup: Parallel Operation of Multiple WSJT-X Instances

This guide describes the creation of a second OS-isolated WSJT-X environment (e.g., for an SDR), including the migration of the existing configuration and the strictly required path separation.

#### 1. Instantiation (OS-Level Isolation)
By default, the WSJT-X lock file prevents multiple executions. Separation is achieved via a command-line parameter that forces a new sandbox in the Windows `AppData` directory.

1. Create a desktop shortcut for `wsjtx.exe`.
2. Open the **Properties** of the shortcut.
3. Modify the **Target** field exactly according to the following syntax pattern (parameter outside the quotation marks):
   `"C:\Program Files\wsjtx\bin\wsjtx.exe" --rig-name=SDR`
4. Start this shortcut **once** and immediately close the program again. This initializes the new directory structure (`%LOCALAPPDATA%\WSJT-X - SDR`).

#### 2. Configuration Migration (Cloning)
WSJT-X does not offer an internal export for instances. The cloning process must take place at the file system level.

1. Navigate to the primary configuration folder: `%LOCALAPPDATA%\WSJT-X`
2. Copy the main configuration file `WSJT-X.ini`.
3. Navigate to the new folder: `%LOCALAPPDATA%\WSJT-X - SDR`
4. Paste the file and overwrite/replace the `.ini` file generated there by the initial start.
5. **Important:** Rename the pasted file to match the new instance exactly: `WSJT-X - SDR.ini`

#### 3. Mandatory Path Separation (Audio & Storage Locations)
Since the configuration was cloned 1:1, both instances now access the same hardware inputs and temporary storage directories. For WSPR, this inevitably leads to identical decodes (since the same `.wav` is analyzed) and potential file lock errors.

Open the new SDR instance, navigate to **File > Settings > Audio** and adjust the following parameters:

* **Soundcard > Input:** Change the audio interface to the specific source of the second receiver (e.g., a dedicated Virtual Audio Cable).
* **Save Directory:** You must change the path to the isolated environment, e.g.:
   `C:\Users\[User]\AppData\Local\WSJT-X - SDR\save`
* **AzEl Directory:** Change this path as well to prevent parallel write access to the `azel.dat`, e.g.:
   `C:\Users\[User]\AppData\Local\WSJT-X - SDR`

After restarting the instance, data streams, hardware access, and temporary WSPR files (WAV files) are completely physically separated from each other.
"""