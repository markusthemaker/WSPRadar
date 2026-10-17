<!-- section: hero -->
# #5 Dr. Vanhamel et al. RX Antenna Rotation: Reproducing Figure 6’s 3 dB ΔSNR Step

<!-- section: setup -->
## Experiment and interpretation

[Publication: Vanhamel, J., Machiels, W., & Lamy, H. (2022). Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band](https://doi.org/10.1155/2022/4809313)

**What changes when one receiving antenna is turned through 90°?** This demo revisits Figure 6, comparing **ON4AWM0 with an ITA LWA II long-wire antenna** against **ON4AWM1 with an adapted shorted dipole** on **160 m during 1–15 May 2021**. The long-wire antenna stayed fixed; the authors rotated the dipole after the first week.

**M7AEO (IO82) is preselected in Station Insights**, matching the transmitting station in Figure 6. WSPRadar compares signals from that transmitter decoded by both receivers in the same two-minute WSPR cycle. Each matched observation is a **Joint Spot**. The difference is **ΔSNR = ON4AWM0 − corrected ON4AWM1**: positive values favour the long-wire receiving station, and negative values favour the dipole receiving station.

Open **Selected Station Evidence → Δ SNR over Time (12h bins)**. Look for the upward change around **8 May**. Across the **1,441 Joint Spots**, the median is **−0.6 dB for the first 750 observations** and **+2.4 dB for the remaining observations**: a **3 dB shift** consistent with the upward transition in the paper. This is a change in relative reception on the sampled path, not a measurement of antenna gain in every direction.

The markers show the median in each time interval; the shaded band, where shown, covers the middle 50% of observations. The colours show where observations are concentrated. Read the vertical axis by its labelled dB values: its spacing is nonlinear. For the broader pattern across transmitters, use **Segment Inspector → Temporal Evidence** with all ranges and directions selected; this pooled view gives more weight to transmitters with more Joint Spots.

[**Figure 6 comparison (PDF)**](app/static/reference_figures/vanhamel_fig6_rotation_v1/WSPRadar_Demo_Vanhamel_Figure6.pdf): Compare the publication in **Panel A**, individual reconstructed receptions in **Panel B**, the matching density bins behind the black ΔSNR curve in **Panel C**, and WSPRadar’s native UTC view in **Panel D**. Matching bin numbers link Panels C and D: each numbered column spans reception numbers in Panel C and elapsed time in Panel D. Reception numbers count successive observations; they do not measure elapsed time. Seven marked peaks and troughs agree with the publication to within one reception and 0.1 dB, within the graphical readout tolerances.

This demo applies a **+1.6 dB Reference SNR Correction**, rounding the **1.57 dB** calibration documented on the [authors’ website](https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-antenna-comparison-instrument). The paper’s text reports **1.2 dB**, as explored in demo #4. The +1.6 dB reconstruction closely matches Figure 6, without establishing which correction was used to create the published figure. A constant correction moves the entire ΔSNR curve vertically; it does not change the size of the step.

<!-- section: step-1 -->
## Follow the path used in the publication

Keep **M7AEO (IO82)** selected in **Station Insights**. This exact callsign and locator identify the transmitting path used for the comparison. The receivers are ON4AWM0 with the fixed long-wire antenna and ON4AWM1 with the dipole that the authors rotated after the first week. The selected evidence concerns this path; it is not a full antenna radiation pattern.

<!-- section: step-2 -->
## Locate the change around 8 May

Open **Selected Station Evidence → Δ SNR over Time (12h bins)**. Read ΔSNR as ON4AWM0 minus corrected ON4AWM1 and look for the upward transition. The documented first-750/remaining-observations split gives medians of **−0.6 dB** and **+2.4 dB**. That is a **3 dB shift** between these observation groups, not an equal-duration split of the measurement window.

<!-- section: step-3 -->
## Bridge reception number and elapsed time

Read the four comparison panels in order. Panel A preserves the publication; Panel B reconstructs observations in reception order; Panel C maps native density bins onto their reception-number spans; Panel D shows the native UTC view. Matching bin numbers connect Panels C and D. Reception numbers count observations, whereas UTC measures elapsed time: a period with no receptions does not acquire reception-number width.

<!-- section: step-4 -->
## Separate vertical offset from step size

The demo applies a **+1.6 dB Reference SNR Correction**, explained in the original description below alongside the paper's **1.2 dB** value. A constant correction shifts the full difference curve vertically; it does not change the size of the transition. Read native axes by their labeled dB values because their spacing is nonlinear. Use **Segment Inspector → Temporal Evidence** for the broader, pooled transmitter population and keep that population distinct from the selected M7AEO path.
