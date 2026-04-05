"""
English manual for WSPRadar.
Used in the Web UI and for PDF export.
"""

DOC_EN = r"""
---

### 1. Introduction & Objective

In amateur radio, evaluating antenna performance has traditionally relied on anecdotal signal reports or manual A/B switching. However, these methods are subject to significant confounding variables: rapid ionospheric fading (QSB), inconsistent remote transmitter power levels, and localized noise floors (QRM). These unpredictable factors make it incredibly difficult to objectively measure how well an antenna is truly performing on a day-to-day basis.

This is where the **Weak Signal Propagation Reporter (WSPR)** protocol changes the game. WSPR is a digital mode designed for probing potential propagation paths using low-power, two-minute beacon transmissions. Every day, thousands of stations worldwide autonomously transmit and receive these beacons, logging millions of highly precise Signal-to-Noise Ratio (SNR) reports into a public database. By participating in WSPR, you effectively turn your station into a calibrated global probe, continuously gathering hard data on exactly where your signal lands and who you can hear. 

The objective of **WSPRadar** is to harness this massive, crowdsourced dataset to provide a systematic, semi-quantitative framework for evaluating your transmit (TX) and receive (RX) antennas. By extracting historical WSPR spot data from the wspr.live repository, this tool applies strict spatial and temporal normalization. It mathematically strips away atmospheric volatility and unequal power levels to isolate the one metric that actually matters: your antenna system's raw hardware efficiency and radiation pattern.

### 2. Key Use Cases & Capabilities

WSPRadar was developed to precisely answer specific, common questions in amateur radio:
* **Path Viability & Skip Zones (Is there an opening?):** Does my signal reach Oceania today? Where are my blind spots? *(Solved via Absolute Analyses for TX and RX).*
* **The "Am I doing okay?" Test (Local Benchmarking):** Is my station performing above or below average compared to others in my region? *(Solved via the Radius Benchmark).*
* **Buddy-Testing (Station vs. Station):** My friend 10 km away uses a Yagi, I use a dipole. Who is better today? *(Solved via the Specific Reference Station test with synchronous evaluation).*
* **The Hardware Laboratory (True A/B Tests):** I need an isolated lab setup for Antenna A vs. B, RX vs. RX, or TX vs. TX at my own location. *(Solved via the Hardware A/B-Test mode).*
* **DX vs. NVIS Profiling (Assessing Take-Off Angle):** Is my antenna a low-angle radiator (DX) or high-angle (NVIS)? *(Readable by analyzing performance in near vs. far distance rings on the map).*
* **Uncovering Local QRM (The "Alligator Test"):** Am I heard worldwide but hear nothing myself? *(Provable by combining a TX and RX compare run against the exact same reference).*
* **Statistical Proof vs. Guesswork:** Is a measured 2 dB advantage physically real or just random noise? *(Solved by the integrated Wilcoxon Test for statistical significance).*

**💡 Quick Start:** Click `✨ Load Demo Config` in the configuration panel, then `Run TX` or `Run RX` to instantly test the tool with sample data. *(Note: The current demo data is configured for the Reference Radius comparison only and is a bit sparse; more comprehensive demo datasets will follow soon).*

### 3. Core Concepts: Absolute vs. Compare

To draw reliable conclusions from WSPR data, WSPRadar strictly separates its analysis into two distinct perspectives:

#### Absolute Analyses (Pure Propagation): 
These answer the question "Is there an open path?". Because propagation conditions can be highly asymmetrical, WSPRadar generates two strictly separate views for this:
* **TX Absolute:** *Where is my transmitted signal heard?* Isolates all instances where your callsign is the transmitter. The map plots all worldwide **receiving stations** that successfully decoded your signal. Measures your pure transmit capability and shows your skip zones (normalized to 1 Watt).
* **RX Absolute:** *Who can my station hear?* Isolates all instances where your callsign is the receiver. The map plots all worldwide **transmitting stations** that your station successfully heard. Measures your pure receive sensitivity and visualizes open paths to your location (normalized based on the remote transmitter's power).
  Both maps show your global blind spots. If you want to know if your signal reaches Oceania today (or if you can hear Oceania), you look at the Absolute Maps.
  
#### Comparative & Benchmark Analyses (The Hardware Difference):
These answer the question "Am I better than Setup B?". In the Compare map, the local noise floor (QRM) at the remote station and rapid ionospheric fading (QSB) are mathematically *completely eliminated*. What remains is exclusively the pure difference ($\Delta$ SNR) between the two tested hardware setups, broken down by geographic segments. This is the ultimate tool for performance benchmarking.
* **For TX Comparisons:** Both transmitting signals are evaluated by the identical remote receiver simultaneously. Thus, the remote receiver's local noise floor (QRM) and antenna gain are functionally canceled out. Calculation: $\Delta SNR_{TX} = SNR_{norm,target} - SNR_{norm,benchmark}$
* **For RX Comparisons:** Both local receivers evaluate the identical remote transmission simultaneously. Thus, the remote transmitter's power and the baseline propagation path are identical. Any difference in SNR is strictly due to your receiving antenna's efficiency and your local QRM. Calculation: $\Delta SNR_{RX} = SNR_{measured,target} - SNR_{measured,benchmark}$

### 4. Methods for Comparative Analysis

WSPRadar offers three fundamental pillars for comparative hardware testing, depending on what you want to prove. An A/B test is physically only valid if *all* other variables remain identical (e.g. testing Antenna A vs. B using the same transmitter).

#### Pillar 1: Local Average (Radius Benchmark)
* **Objective:** Measuring your performance against the average of your neighborhood.
* **Methodology:** WSPRadar aggregates all local WSPR stations within a defined radius (e.g. 50 km). Since it is assumed that all these stations are subject to the same macro-propagation conditions, this gives you a hard statistical classification of whether your QTH (location) or antenna performs above or below average. The *Spot-by-Spot (Synchronous)* mathematics is applied.

#### Pillar 2: Specific Reference Station (Buddy Test)
* **Objective:** A 1-to-1 comparison with a known ham radio operator (location vs. location, antenna vs. antenna, or simply station vs. station).
* **Methodology:** You define a different reference callsign (e.g. a radio buddy 10 km away). Because you are both on the air under different callsigns, the database seamlessly collects all spots. WSPRadar isolates instances where both signals were decoded by the *exact same remote receiver* during the *exact same 2-minute WSPR cycle*. The *Spot-by-Spot (Synchronous)* mathematics eliminates fading completely on a bit-level.

#### Pillar 3: True Hardware A/B Test (Self-Test)
* **Objective:** A precise laboratory test of your own hardware at your own location using your own callsign. This goes far beyond the classic comparison: As long as all other parameters remain identical, you can isolate and test any variable here. Compare receiver vs. receiver (RX vs. RX), transceiver vs. transceiver (TX vs. TX), different baluns/feedlines, or evaluate the exact mounting position of an antenna within the same property (Location A vs. Location B). WSPRadar splits into two special computational paths depending on the test direction:
* **The RX A/B Test (Simultaneous):** Two parallel receivers (SDRs) evaluate WSPR signals simultaneously. **The Trick:** So that the WSPR network doesn't delete the synchronous spots of your receivers as duplicates, you must specify different callsign suffixes in your receiving software (e.g. WSPRdaemon). 
  * **Setup A:** Reports using your primary callsign (e.g., `DL1MKS`).
  * **Setup B:** Reports using a distinct suffix (e.g., `DL1MKS/P`).
  In WSPRadar's Self-Test mode, you enter these two callsigns. The tool then generates perfect joint-spots via *Spot-by-Spot (Synchronous)* mathematics for the ultimate receive setup comparison.
* **The TX A/B Test (Sequential / Time-Slicing):** You use a transceiver that periodically switches between transmitting Setup A and B. Since Setup A and B *never* transmit in the same slot, WSPRadar uses **Asynchronous Math (Time-Averaging)**: It splits your data based on the start minutes (Even: 00, 04, 08 / Odd: 02, 06, 10) and forms long-term medians before calculating the $\Delta$ SNR.
  * *Note on TX Hardware:* Such a test requires hardware capable of deterministic scheduling. A QMX transceiver, for example, can be programmed exactly (`frame=10` transmits every 10 minutes, `start=2` begins exactly at minute 2). The standard WSJT-X software transmits randomly out-of-the-box and is not suitable for fixed-schedule A/B tests without special add-on tools.
  * *Why avoid Multi-Cycle WSPR (callsign suffixes like /1 or /P) for TX?* WSPR messages with compound suffixes force the protocol to transmit across multiple cycles (Type 1 and Type 3 messages). Because many global receiving stations fail to reliably decode Type 3 messages from the noise, the absolute number of logged spots for compound callsigns drops drastically. Furthermore, artificial suffixes like `/1` or `/2` are not officially approved callsign structures, and using `/P` is strictly only permitted when actually operating portable. Therefore, WSPRadar's TX A/B test relies exclusively on time-slicing using your *identical* standard callsign, mathematically separating the signals based on even/odd minutes to retain 100% of the global network's decoding performance.

### 5. General Data Methodology

#### 5.1 Power Normalization
To enable direct comparison between stations operating with different hardware configurations, all absolute signal-to-noise ratio (SNR) data is normalized to a standard 1-Watt (30 dBm) reference. 
$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$
This normalization is applied to both TX and RX absolute analyses, eliminating transmitter power as an independent variable and isolating the antenna system's intrinsic efficiency and take-off angle.

#### 5.2 Geographic Rastering and Projection
Spatial data is mapped using an Azimuthal Equidistant Projection centered on the user's defined Maidenhead locator. The map rendering engine is explicitly locked to a perfect mathematical sphere (Radius = 6371 km) to guarantee 100% geometric consistency between the calculated data tables and the visual map plotting, avoiding standard WGS84 ellipsoid distortions.
* The map is divided into a dynamic zone model, utilizing concentric radial bins of 2,500 km (approximating a typical F2-layer hop).
* Azimuthal wedges are divided into discrete degrees (e.g., 22.5°) to account for spatial density.
* Each resulting geographic segment is assigned a unique coordinate identifier for data aggregation.

#### 5.3 Spatial Normalization (Median Aggregation)
To mitigate spatial bias caused by disproportionate receiver density in specific regions, the tool employs a two-step "Median of Medians" aggregation:
1. **Station-Level Aggregation:** The median SNR of all spots is calculated for each unique remote station.
2. **Segment-Level Aggregation:** The median of these station-level values is calculated to determine the final value for the geographic segment. 
This method prevents "Receiver Density Bias"—where dense receiver clusters (e.g., in Europe or North America) statistically drown out sparse regions (e.g., in Asia or Africa) in global averages. Every geographic wedge gets a fair, isolated evaluation, ensuring that a single highly active station does not statistically overpower a region.

### 6. Visual Interpretation & Segment Inspector

#### 6.1 Visual Guide (Map Elements)
* **Heatmaps:** Absolute modes render in raw dB. Comparative modes (Compare) map the Δ SNR using a standardized S-Unit scale (1 S-Unit = 6 dB). Positive values (red) indicate superiority over the benchmark; negative values (blue) indicate a systemic weakness.
* **Distance Rings (Take-Off Angle):** When analyzing the map, note the distances: Superiority in inner rings (e.g., < 2500 km) indicates good NVIS capabilities (high take-off angle), whereas dominance in outer rings (> 10000 km) proves a low take-off angle suitable for DX.
* **Scatter Plots:** Individual stations are plotted as dots. Green dots indicate jointly decoded stations (in the exact same 2-minute cycle). Yellow-orange dots represent stations heard by both, but asynchronously. Purple dots represent exclusive decodes by your own station ("Only [Target]"), while white dots indicate stations decoded only by the reference station ("Only Reference").
* **Pole Markers:** To aid in spatial orientation, the exact geographic North Pole (N-POL) and South Pole (S-POL) are marked with neon-green crosses.
* **High-Res Export:** Located above each map is a discreet toolbar ("⚙️ Render High-Res Map"). This allows for the on-demand rendering and downloading of a lossless, print-ready 300 DPI version of the current map without blocking the interactive user interface with loading times.

#### 6.2 Detailed Evaluation: Segment Inspector (Histogram & Tables)
Directly below the maps, you will find a Segment Inspector with two cascading dropdown menus. This allows you to select a specific distance and then a compass direction (e.g., NNE) to analyze its underlying data distribution in detail.
1. **Absolute Modes:** Displays the distribution of normalized SNR values for all stations within that segment using a discrete bar chart. The X-axis displays the individual *Station Medians*. The red dashed line marks the final aggregated *Segment Median* calculated from all these underlying values.
2. **Compare Modes:** Displays the distribution of Δ SNR values. This is crucial for determining whether a close median value is the result of consistent superiority (a tight bell curve) or extreme variance. The X-axis displays the individual *Station Medians* (the first-order aggregation). The red dashed line explicitly marks the final aggregated *Segment Median* (the "median of medians" across all stations in this segment).
3. **Station Insights Table:** Below the histogram, an interactive data table lists the exact contributing remote stations for the selected segment. The "Median Δ SNR" column here displays the merged value for that specific station. For comparative modes, the table explicitly breaks down how many `Joint Spots` form this value, and how many unmatched decodes (`Only Reference` or `Only [Target]`) were logged.
4. **Drill-Down Data (Raw Data & Export):** Clicking on any row within the "Station Insights" table reveals the detailed drill-down view for that specific station, exposing every single 2-minute cycle (spot). In Compare mode, this view exposes the raw Δ SNR of each individual joint spot, whose median perfectly forms the "Station Median" shown in the table above.
Utilizing the multi-select feature, you can use Shift-Click to highlight multiple stations, or use the checkbox in the table header to select *all* stations in the segment at once, instantly generating a full raw data audit. This interactive master table includes powerful native tools in the top right corner: you can **search** the data, apply **filters**, **show or hide columns**, and **download** the entire compiled dataset as a **CSV file** for further analysis in Excel.

### 7. Configuration & Parameter Reference

#### 7.1 Core Parameters
* **Target Callsign & QTH Locator:** Identifies the primary station under evaluation and establishes the mathematical center (Maidenhead grid) for the Azimuthal Equidistant map projection.
* **Operating Band & Timeframe:** Specifies the frequency band and the temporal window (in hours or absolute dates) to extract the relevant spot data from the database.

#### 7.2 Comparison against References and A/B Testing
* **Benchmark Mode:** Selects the fundamental type of comparison (Reference Radius, Specific Reference Station, or Hardware A/B-Test).
* **Reference Search Radius (km):** Defines the geographic boundary to aggregate local benchmark stations when using the radius mode.
* **Reference Callsign:** The exact callsign of the external counterpart for the buddy test.
* **Test Setup (Hardware A/B-Test only):** Toggles between `RX Test (2 Receivers, Simultaneous)` and `TX Test (1 Transmitter, Time-Slicing)`.
* **Target Locator & Reference Locator:** The exact 6-character Maidenhead locators (e.g., JN37AA vs. JN37AB) used to separate data streams during simultaneous RX tests.
* **Target Time-Slot & Reference Time-Slot:** Assigns the transmission cycles (`Even Minutes` vs. `Odd Minutes`) for sequential TX tests.

#### 7.3 Advanced Config & Expert Settings
* **Local QTH Solar State:** To account for diurnal shifts in the ionosphere (e.g., D-layer absorption during the day vs. F2-layer propagation at night), the tool uses the `ephem` astronomical library. It calculates the exact solar elevation at your QTH for every single WSPR spot. You can filter data strictly for `Daylight` (> +6°), `Nighttime` (< -6°), or `Greyline` (between -6° and +6°).
* **Map Scope (Max Distance km):** Sets the visual zoom factor of the map projection (in kilometers) from the center. Useful for better analyzing regional propagation.
* **Min. Spots per Station:** Qualifies the validity of a propagation path. A remote station must decode the transmission at least this many times to be included in the aggregation. This effectively filters out one-off, transient propagation anomalies such as meteor or airplane scatter.
* **Min. Stations per Map Segment:** Acts as the **baseline filter** for all maps. This filter prevents random decodes from skewing the picture by completely hiding segments with too few stations. It is highly critical for mitigating the "WSPR Collision Problem", ensuring that rendered segments possess genuine statistical significance.
* **Compare Map Statistical Confidence (Wilcoxon Test):** Instead of blindly relying on the median Δ SNR, WSPRadar allows you to enforce strict statistical rigor on Compare maps. When activated, the Wilcoxon test dynamically overrides the base value of "Min. Stations" upwards (up to 8 minimum stations) for Compare maps to meet the mathematical constraints of the chosen confidence level. Segments failing the p-value test are strictly discarded.

### 8. Discussion, Limitations & Disclaimer

#### Discussion:
WSPRadar transforms anecdotal amateur radio reports into a purely data-driven, quantitative approach. By enforcing strict temporal and spatial synchronization (especially in Compare mode), the tool successfully cancels out the unpredictable volatility of the ionosphere (QSB) and varying local receiver noise floors (QRM). This enables an objective performance evaluation of antenna hardware during real-world operation that would otherwise only be possible with extremely expensive calibrated measurement equipment or drone flights.

#### Limitations:
* **Performance Limits & Data Latency:** To preserve server resources, the maximum queryable timeframe is capped at 7 days, and time queries are quantized to 15-minute intervals to optimize global caching. Additionally, the global wspr.live database has a natural aggregation latency of about 15 to 30 minutes before brand new spots appear in the tool after transmitting.
* **Path Viability vs. Uptime:** WSPR inherently logs only successful decodes. Therefore, the absolute median SNR reflects the signal strength *during an open propagation path*. Dead bands do not lower the average.
* **The TX Power Calibration Trap:** WSPRadar is vulnerable to a "Garbage In, Garbage Out" scenario regarding transmit power. The normalization formula assumes the $P_{TX}$ reported in the WSPR packet is the exact power radiated at the feedpoint. If a transceiver automatically folds back power due to a high SWR, or if there is severe feedline loss, the mathematically derived $SNR_{norm}$ will drop. Operators conducting strict A/B tests must physically calibrate their output power with a wattmeter to ensure a reported weakness is attributed to the antenna geometry and not the feedline or transmitter.
* **Polarization:** WSPRadar does not measure isolated free-space antenna gain; it measures real-world system efficiency. This includes polarization matching under real propagation conditions, as the ionosphere heavily influences signals through Faraday rotation.

#### Disclaimer:
WSPRadar is an experimental open-source project (Beta) provided "as is" without any warranties of any kind. While the source code and mathematical models are publicly accessible and verifiable, the developer assumes **no liability or responsibility** for the accuracy, completeness, or reliability of the generated data or charts.
Results rely on crowd-sourced WSPR data via a third-party API (wspr.live), which may be skewed by user errors (e.g., misreported TX power levels). **Users should never make financial decisions (such as purchasing or selling expensive radio or antenna equipment) based solely on the output of this tool.** Use entirely at your own risk.

#### License (Open Source):
WSPRadar is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License (AGPLv3) as published by the Free Software Foundation. This license ensures that the source code—even when used over a network (SaaS) and after modifications—must always remain free and open for the amateur radio community.
"""