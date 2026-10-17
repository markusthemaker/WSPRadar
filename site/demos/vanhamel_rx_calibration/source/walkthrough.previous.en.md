<!-- section: hero -->
# #4 Dr. Vanhamel et al. RX Chain Calibration: Calibrating a 1.2 dB Receiver Offset

<!-- section: setup -->
## Experiment and interpretation

[Publication: Vanhamel, J., Machiels, W., & Lamy, H. (2022). Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band](https://doi.org/10.1155/2022/4809313)

Before comparing two antennas, first check whether the receiving equipment introduces a difference of its own. This demo explores **receiver-chain calibration**: measuring a systematic difference in reported signal-to-noise ratio (SNR) so that it can be accounted for in a subsequent antenna comparison. The receiver chain includes the receiver, filters, cables and signal-processing settings.

Reconstructs a seven-day receiver-chain calibration baseline for 6–13 February 2021 with no SNR correction applied. The paper describes calibration with both receiver chains connected to the same antenna. WSPRadar compares **ON4AWM0 as Target** with **ON4AWM1 as Reference** on **160 m**, using the archive window from **6 February 06:00 to 13 February 06:00 UTC** and transmitters within **2,500 km**. In the paper’s shared-antenna arrangement, a persistent difference reveals an offset between the receiving chains that would otherwise influence the antenna comparison.

WSPRadar matches reports of the **same transmitting station and reported locator in the same two-minute WSPR cycle**, decoded by both receivers. Each matched observation is a **Joint Spot**. The difference is **ΔSNR = ON4AWM0 − ON4AWM1**: positive values mean that ON4AWM0 reported a higher SNR, negative values mean that ON4AWM1 did, and 0 dB means equal reported SNR. Reports decoded by only one receiver cannot provide this paired difference.

Go to **Segment Inspector → Benchmark Evidence**, keep all distance ranges and directions selected, and read the **Mean** for **Joint-Spot Δ SNR**. The 1,143 same-cycle joint reports from the ten transmitters passing the ≥50-joint-report threshold average +1.214 dB for ON4AWM0 − ON4AWM1, displayed as +1.2 dB; each transmitter has a +1.0 dB median. The threshold means that each included transmitter must contribute at least 50 matched observations during the selected week.

Compare this with **Station Medians (Δ SNR)**, where each transmitter contributes one median, here **+1.0 dB**. The **+1.2 dB Joint-Spot mean** averages all 1,143 matched observations and is the value compared with the paper’s reported average.

Adding **+1.2 dB** to Reference receiver ON4AWM1’s SNR would bring the reconstructed mean difference close to **0 dB**. This demo leaves the correction at **0.0 dB** so that the original offset remains visible.

<!-- section: step-1 -->
## Start with the shared-antenna arrangement

The paper describes both receiving chains connected to the same antenna. The demo compares **ON4AWM0 as Target** with **ON4AWM1 as Reference**, using the stated week on 160 m. In that arrangement, a persistent paired SNR difference reveals a receiving-chain offset that would otherwise affect a later antenna comparison.

<!-- section: step-2 -->
## Read the Joint-Spot mean

Keep all distance ranges and directions selected in **Segment Inspector → Benchmark Evidence**. In **Joint-Spot Δ SNR**, read the mean across all matched observations: the reconstructed value is **+1.214 dB**, displayed as **+1.2 dB**. Each Joint Spot contributes one difference. The selected evidence threshold requires at least 50 Joint observations from each included transmitter.

<!-- section: step-3 -->
## Compare a different weighting

Now read **Station Medians (Δ SNR)**. Each transmitter contributes one median rather than one value per Joint Spot; here those station medians are **+1.0 dB**. This is not a contradictory calibration result. The mean of Joint-Spot differences and the summary of station medians use different observation units and weights. Keep the statistic named whenever quoting a value.

<!-- section: step-4 -->
## Interpret the correction sign

The displayed difference is **ON4AWM0 − ON4AWM1**. Adding **+1.2 dB** to the Reference SNR would move the reconstructed mean difference close to zero. The installed demo deliberately leaves the correction at **0.0 dB**, preserving the visible baseline offset. Demo #5 discusses a separate **+1.6 dB** correction used for its Figure 6 reconstruction; do not silently substitute one value for the other.
