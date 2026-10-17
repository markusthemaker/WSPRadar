<!-- section: hero -->
# One Antenna, Two Receivers — Why Calibration Matters

### Calibrate your receivers before comparing antennas

Two receivers connected to one antenna should tell a similar story. Use WSPRadar to find the difference introduced by the receiving equipment—before mistaking it for an antenna advantage.

<!-- section: setup -->
## What were the operators testing?

Before comparing two antennas, Jurgen Vanhamel, Walter Machiels and Hervé Lamy checked the receiving equipment itself. Their [paper](https://doi.org/10.1155/2022/4809313) describes **two receiving chains connected to the same long-wire antenna through a splitter**, using matching processing settings. This demo compares the archive reports from **ON4AWM0 and ON4AWM1**.

Each receiving chain includes more than the receiver: cables, filters and signal-processing settings also belong to the setup. With both chains fed by the same antenna, a persistent SNR difference provides a baseline for the equipment rather than a comparison between antennas.

**Our question is: how large is that difference, and is there enough evidence to use it as a calibration baseline?**

SNR is the signal-to-noise ratio: how strongly a signal stands out relative to noise. Higher SNR is better. WSPRadar finds occasions when both receivers reported the **same transmitter and reported locator in the same two-minute WSPR cycle**. A **Joint Spot** occurs when both receivers report the same transmitter in the same two-minute WSPR cycle, allowing us to compare their SNR at the same time. Signals decoded by only one receiver cannot provide this paired difference.

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
| Reference-side SNR correction (dB) | 0.0 dB; Set up an offset-establishment run | Leave the original equipment difference visible. |
| Minimum joint evidence per station | 50 | Each retained station entry must supply at least 50 matched observations during the selected week. |

Go directly to **Segment Inspector → Benchmark Evidence** and keep **Full Range \| All Directions** selected. For this question, we do not need to work through every results view.

<!-- section: step-2 -->
## Read Benchmark Evidence: do the receivers agree?

**Benchmark Evidence: a small difference, repeated across transmitters**

*Both median summaries are +1.0 dB. The mean across all matched observations is +1.2 dB.*

### What is the typical difference?

Start with the two SNR panels.

**Station Medians (Δ SNR): +1.0 dB.** WSPRadar first finds each transmitter's median difference, then takes the middle value across those station medians. Each contributing station entry has equal weight, regardless of how often it was heard.

**Joint-Spot Δ SNR: +1.0 dB.** This panel includes every matched comparison. Frequently heard transmitters therefore have more influence.

A median is the middle value when the values are placed in order; with an even number of values, it is the average of the two middle values. Here, both summaries give the same answer: **ON4AWM0 typically reports an SNR about 1 dB higher than ON4AWM1**.

The Joint-Spot panel also shows a **Mean of +1.2 dB**—the arithmetic average across all matched observations. Mean and median summarize the distribution differently; here, both point to the same small, positive receiver offset. The mean provides the calibration estimate for this run.\*

### Is there enough evidence behind it?

**Decode Outcomes** shows which signals supplied a comparison. The striped bars represent station entries; the solid bars represent observations.

Here, **ten station entries contribute 1 143 Joint Spots**, approximately **91% of the 1 257 retained observations**. A station entry means a callsign together with its full reported locator. The remaining **114 observations** do not supply a same-cycle ΔSNR pair.

Each contributor supplies **52 to 344 matched observations**, and **all ten station medians are +1.0 dB**. The result is therefore repeated across different transmitters, rather than resting on a single signal or a handful of reports.

The **100% Joint station bar** reflects the selection: stations without enough paired observations have already been excluded. It does not mean that both receivers decoded every transmission.

**The useful finding is the agreement:** the station summaries, the individual comparisons and the supporting counts all point to a small equipment difference under the shared-antenna interpretation. The counts describe the selected evidence; they do not establish an uncertainty interval or validate the historical hardware arrangement.

<!-- section: step-3 -->
## State the result—and prepare the antenna comparison

> **In the selected archive week, ON4AWM0 reported an average SNR 1.2 dB higher than ON4AWM1. The result is supported by 1 143 same-cycle comparisons from ten transmitting-station entries. With both receiving chains connected to the same antenna, such an offset is a receiver-chain baseline, not an antenna advantage; the archive alone does not verify that connection for the entire week.**

To account for this offset, a **+1.2 dB Reference SNR Correction** would raise ON4AWM1's SNR before subtraction, bringing the average difference close to zero. The prepared calibration demo leaves the correction at zero so the original offset remains visible.

Save the results package and record the band, connections and receiver settings. The correction belongs to the tested arrangement; it should not automatically be reused after changing the equipment or its settings.

You have now examined how to establish what the receiving equipment contributes. Next, see how a corrected comparison reveals a change in antenna orientation.

[**Continue to A 90° Turn, a 3 dB Difference →**](/en/demos/vanhamel_rx_buddy/)

Demo #5 uses a separate **+1.6 dB Reference SNR Correction** for its Figure 6 reconstruction. Its walkthrough explains that choice; do not silently substitute one calibration value for the other.

---

\* The +1.2 dB average agrees, at the displayed precision, with the shared-antenna calibration reported by Vanhamel and colleagues. The paper's rounded average does not establish its exact weighting, the signed receiver mapping, or the selected archive dates. The paper uses “more than 50” receptions per station; the demo uses at least 50 Joint Spots. No station entry in this frozen reconstruction has exactly 50, so the strict and inclusive cutoffs select the same entries here. [Original paper ↗](https://doi.org/10.1155/2022/4809313)
