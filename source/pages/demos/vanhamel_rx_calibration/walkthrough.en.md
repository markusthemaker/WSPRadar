<!-- section: hero -->
# One Antenna, Two Receivers — Why Calibration Matters

### Calibrate your receivers before comparing antennas

Two receivers connected to one antenna should tell a similar story. Use WSPRadar to find the difference introduced by the receiving equipment—before mistaking it for an antenna advantage.

**What you will take away:** a **+1.2 dB receiving-chain offset**, supported by **1 143 spot pairs from ten station entries**, and how to enter it as the **Reference correction in the next antenna benchmark**. This value belongs to the receiver pair in this demo; your own pair needs its own calibration.

<!-- section: setup -->
## Setup: how were the receiving chains compared?

Before comparing two antennas, Jurgen Vanhamel, Walter Machiels and Hervé Lamy checked the receiving equipment itself. Their paper describes **two receiving chains connected to the same long-wire antenna through a splitter**, using matching processing settings. This demo compares the database reports from **ON4AWM0** and **ON4AWM1**.

Each receiving chain includes more than the receiver: cables, filters and signal-processing settings also belong to the setup. With both chains fed by the same antenna, a persistent SNR difference provides a baseline for the equipment rather than a comparison between antennas.

**Our question is: how large is that difference, and is there enough evidence to use it as a calibration baseline?**

SNR is the signal-to-noise ratio: how strongly a signal stands out relative to noise. Higher SNR is better. WSPRadar finds <strong class="defined-term">spot pairs</strong>: occasions when both receivers report the same transmitter with the same reported locator in the same two-minute WSPR cycle. This lets us compare their SNR for the same transmission. Signals decoded by only one receiver cannot provide this paired difference.

A spot pair consists of one retained Target observation and one retained Reference observation matched on band, WSPR cycle, and the remote station’s callsign and full reported locator. Each pair supplies one ΔSNR observation.

When several reports exist for one setup, remote station, and cycle, WSPRadar consolidates them using its existing SNR-selection rules before forming the comparison.

For this demo, no correction is applied:

**ΔSNR = ON4AWM0 SNR − ON4AWM1 SNR**

Positive values mean ON4AWM0 reported the higher SNR; negative values mean ON4AWM1 did. Zero means equal reported SNR.


<!-- section: step-1 -->
## Load the demo and check its settings

Select **Run in WSPRadar App** above to open the prepared receiver-calibration demo. The settings load for you:

| Setting | Value in this demo | What it means |
|---|---|---|
| Analysis | RX Benchmark | Compare reception by the two receiving chains. |
| Target | ON4AWM0, QTH JO20OT | The chain being evaluated. |
| Reference | ON4AWM1, reported grid JO20 | The chain used for comparison; retain its reported locator precision. |
| Benchmark design | Reference Setup/Station | Compare against this particular Reference. |
| Operating Band | 160 m | Use reports from this band. |
| UTC window | 6 February 2021, 06:00 → 13 February 2021, 06:00 | Examine one week of observations. |
| Maximum peer distance from Target (km) | 2 500 km | Include transmitting stations within this distance of the Target. |
| Reference-side SNR correction (dB) | **0.0 dB; establish the offset** | Leave the original equipment difference visible. |
| Minimum spot pairs per station | **50** | A station entry needs at least 50 spot pairs during the week to contribute to the calibration SNR summaries. |

If the results have not opened automatically, select **Run Analysis**. Go directly to **Segment Inspector → Benchmark Statistics** and keep **Full Range \| All Directions** selected. For this question, we do not need to work through every results view.

<!-- section: step-2 -->
## Read the result and check its support

### What is the typical difference?

Start with the **middle and right SNR panels**.

**ΔSNR — Qualifying spot pairs:** the median is **+1.0 dB**. This panel includes every matched comparison from the stations that meet the 50-spot-pair minimum. Frequently heard transmitters therefore have more influence.

**ΔSNR — Qualifying Stations:** the median is also **+1.0 dB**. WSPRadar first finds each transmitter's median difference, then takes the middle value across those station medians. Each contributing station entry has equal weight, regardless of how often it was heard.

A median is the middle value when the values are placed in order; with an even number of values, it is the average of the two middle values. Here, both summaries give the same answer: **ON4AWM0 typically reports an SNR about 1 dB higher than ON4AWM1.**

The spot-pair panel also shows a **Mean of +1.2 dB**—the arithmetic average across the qualifying matched observations. Most differences lie at +1 or +2 dB, which helps explain why the mean is slightly higher than the median. Mean and median summarize the distribution differently; here, both point to the same small, positive receiver offset. **The mean provides the calibration estimate for this run.**<sup><a href="/en/demos/vanhamel_rx_calibration/#calibration-paper-note">1</a></sup>

### Is there enough evidence behind it?

**Ten station entries contribute 1 143 qualifying spot pairs.** A station entry means a callsign together with its full reported locator. Each contributor supplies **52 to 344 spot pairs**, and **all ten station medians are +1.0 dB**. The result is therefore repeated across different transmitters, rather than resting on a single signal or a handful of reports.

The left **ΔDecode — Decode Volume** panel answers a separate question: which chain recorded more decodes? It includes **all 59 observed station entries**, including those below the calibration's spot-pair minimum. Its **3 231 decodes** are the two receivers' counts added together; a shared transmission contributes one decode to each receiver. This broader decoding population should not be confused with the ten stations used to estimate the SNR offset.

The useful finding is the agreement: the station summaries, the individual comparisons and the supporting counts all point to a small equipment difference under the shared-antenna interpretation. The counts describe the selected evidence; they do not establish an uncertainty interval or validate the historical hardware arrangement.

<!-- section: temporal-snr -->
## Does the offset persist through the week?

Next, open **ΔSNR Temporal Coverage** in the Segment Inspector. Select **12 h** bins to match this figure.

In the twelve-hour view, **13 of the 14 median points remain at +1 dB**. The +2 dB point on **10 February, 06:00–18:00 UTC**, comes from only **ten spot pairs**. The result is consistent with a small, repeated offset through the observed week.

The hourly view is also centered at +1 dB apart from the **16:00 UTC hour**, which contains only **three pairs**. The blank interval from **10:00 to 16:00 UTC** contains no qualifying paired observations; it does not indicate a zero offset. For your own calibration, investigate a sustained shift before adopting one correction for the whole run.

<!-- section: decoding-check -->
## Does correcting SNR also equalize decoding?

For a final check, open **Global View → Decodes & Stations by SNR**. Follow the curves from stronger signals on the left toward weaker signals on the right. These are cumulative counts: a steep rise means many decodes fall within a narrow reported-SNR range.

The top-middle panel shows **316 ON4AWM0-only decodes** and **15 ON4AWM1-only decodes**, concentrated near the weak end of the scale, around −30 dB. The top-left **Paired spots** panel represents **1 450 spot pairs**, with **1 450 retained observations from each receiver**, including pairs from stations with fewer than 50 spot pairs; only **1 143** meet the calibration’s station requirement.

**The concentration is striking: 293 of the 316 Target-only decodes—about 93%—fall between −28 and −32 dB raw reported SNR.** Near the decoding limit, a small real SNR improvement can determine whether a WSPR message is decoded at all. When many signals sit in this region, the number of successful decodes can change substantially. WSPR’s decoding threshold represents a transition in decoding probability, rather than a hard boundary applying to every reception. [WSJT-X User Guide](https://wsjt.sourceforge.io/wsjtx-main_en.html) This pattern is consistent with marginal-signal decoding; the measured +1.2 dB reporting offset alone does not prove the cause.

**This is why ΔDecode complements ΔSNR.** ΔSNR compares only transmissions decoded by both receivers. <strong class="defined-term">ΔDecode</strong> compares their total observed decodes—Paired plus each receiver’s own one-sided decodes—and therefore captures reception missing from the paired comparison. Here, **1 766 versus 1 465 decodes gives 1.21× as many observed decodes**, with a net advantage of **316 − 15 = 301**.

The bottom row shows **59 station entries at ON4AWM0 versus 50 at ON4AWM1**. The advantage includes **nine transmitting-station entries absent from the Reference’s log**, as well as additional transmissions from stations both receivers heard.

**An SNR correction adjusts the reported values used in the comparison. It cannot recover a missed decode or establish equal decoding performance.** These curves use each receiver’s raw reported SNR, so the Reference correction does not move them. Interpret one-sided evidence under known common operation and reporting: outages or missing uploads can also produce a difference. The counts do not measure an absolute decoding probability or identify the physical cause of the imbalance.

**Keep this decoding result with your calibration record.** The next antenna benchmark can correct the +1.2 dB SNR offset but may still include differences in decoding performance between the receiving chains. The **1.21× factor describes this run; it is not a correction to apply to later decode counts**.

<!-- section: step-3 -->
## Use the result in the next antenna benchmark

> **Calibration result:** In the selected week of database records, ON4AWM0 reported an average SNR **1.2 dB higher** than ON4AWM1. The result is supported by **1 143 same-cycle comparisons from ten transmitting-station entries**. With both receiving chains connected to the same antenna, such an offset is a receiver-chain baseline, not an antenna advantage; the database alone does not verify that connection for the entire week.

To account for this offset, a **+1.2 dB Reference SNR correction** raises ON4AWM1's SNR before subtraction, bringing the average difference close to zero. **The prepared calibration demo stays at 0.0 dB**, so the original offset remains visible.

### Where to enter the correction

For the next antenna comparison using these same receiving chains:

1. **Save the calibration results package** and record the band, connections and receiver settings.
2. Connect the antenna under test to the **Target receiving chain** and the comparison antenna to the **Reference receiving chain**. Keep the receiving-chain settings and band as calibrated, and have both receivers listening and reporting throughout the new comparison period.
3. Open the next **RX Benchmark** with **Reference Setup/Station**. Keep **ON4AWM0 as Target** and **ON4AWM1 as Reference**, and select the dates of the antenna experiment.
4. In the SNR-correction controls, switch from **establishing an offset** to **using an established correction**. Enter **+1.2** in **Reference-side SNR correction (dB)**, then run the benchmark.

| Next benchmark setting | What to enter for this receiver pair |
|---|---|
| Target | **ON4AWM0** |
| Reference | **ON4AWM1** |
| Correction choice | Apply an established correction |
| Reference-side SNR correction (dB) | **+1.2** |

**Use the positive sign.** WSPRadar adds the value to Reference before calculating Target minus Reference:

**Corrected ΔSNR = Target SNR − (Reference SNR + 1.2 dB)**

For example, a raw **+3.0 dB** antenna-comparison difference would become **+1.8 dB** after this correction. This is a calculation example, not another measured result from the calibration week. The adjustment accounts for the measured receiving-chain baseline before you interpret the antenna comparison.

For the calibration observations themselves, the mean would move close to **0 dB**, while the +1.0 dB medians would move to **−0.2 dB**. That is expected: this correction follows the mean, and the mean and median are different summaries.

**For your own receivers, use the signed offset from your own common-antenna calibration.** The +1.2 dB value belongs to the pair and arrangement in this demo. It is a WSPRadar analysis correction; retain the receiver settings used during calibration. Recheck the calibration after changing the band, receiving equipment, cables, filters or relevant settings. If you simply reverse the Target and Reference assignments of the same calibrated chains, the correction sign reverses too: this example would use **−1.2 dB**.

You have now examined how to establish what the receiving equipment contributes. Next, see how a corrected comparison reveals a change in antenna orientation.

[Continue to A 90° Turn, a 3 dB Difference →](/en/demos/vanhamel_rx_buddy/)

**The antenna-rotation demo uses a separate +1.6 dB Reference SNR correction for its Figure 6 reconstruction.** Its guided demo explains that choice; do not silently substitute one calibration value for the other.<sup><a href="/en/demos/vanhamel_rx_calibration/#calibration-rotation-note">2</a></sup>

---

<span id="calibration-paper-note"></span>

**1.** The +1.2 dB average agrees, at the displayed precision, with the shared-antenna calibration reported by Vanhamel and colleagues. The paper's rounded average does not establish its exact weighting, the signed receiver mapping, or the selected database dates. The paper uses “more than 50” receptions per station; the demo uses at least 50 spot pairs. No station entry in this export has exactly 50 spot pairs, so the strict and inclusive cutoffs select the same entries here. [Original paper ↗](https://doi.org/10.1155/2022/4809313)

<span id="calibration-rotation-note"></span>

**2.** The authors' [instrument and calibration notes](https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-antenna-comparison-instrument) document a separate approximately 1.574 dB estimate, added to ON4AWM1. The following reconstruction uses that estimate rounded to +1.6 dB.
