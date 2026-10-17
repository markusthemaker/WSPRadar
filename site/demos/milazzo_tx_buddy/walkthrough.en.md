<!-- section: hero -->
# #7 Dr. Milazzo Revisited: Extending an Early Multi-Part WSPR Antenna Study with Same-Cycle Evidence

<!-- section: setup -->
## Reproduce this setup

Select ‘Run in WSPRadar App’ to load this demo and start its analysis.

<!-- section: step-1 -->
## Begin with the installed RX walkthrough

The installed demo starts in **RX Benchmark**, with **KP4MD as Target** and **WB6RQN as Reference**. Its main walkthrough revisits Figure 6, receiving transmissions from VE6PDQ. Read the explicit direction-correction note in the comparison: archived endpoint identities contradict the original figure's printed direction. Keep the RX walkthrough separate from the optional Figure 7 TX follow-up.

A **Joint Spot** occurs when both receivers report the same transmitter in the same two-minute WSPR cycle, allowing us to compare their SNR at the same time.

<!-- section: step-2 -->
## Keep the full locator identities separate

In **Station Insights**, inspect the preselected **VE6PDQ (DO34IR)** identity, which supplies three Joint Spots. Then select **VE6PDQ (DO34)** for the other two. The shared callsign does not merge these reported identities. Same-cycle reports with different full transmitter locators do not form a Joint Spot; combining them visually would conceal the evidence rule.

<!-- section: step-3 -->
## Trace one pair through the panels

Use the **19 December 14:46 UTC** example to connect the original report values, the reconstruction, and the paired difference. KP4MD's **+2 dB** and WB6RQN's **−6 dB**, both at 5 W, become **−5 dB** and **−13 dB** on the common 1 W scale. Their difference remains **+8 dB**. The faint guides link eligible same-cycle, full-locator endpoints; they are not interpolated observations.

<!-- section: step-4 -->
## Continue with the optional TX comparison

For Figure 7, switch **Analysis direction** to **TX**, retaining the same stations, dates, band, and distance limit. The receiver VE6PDQ now provides the selected remote path. Only one Joint Spot survives there, whereas the broader TX configuration contains 45 Joint observations across 30 receivers. Read the **20 December 00:22 UTC** power-normalization example in the original description before interpreting that paired difference.

<!-- section: step-5 -->
## Separate graphical agreement from paired evidence

The many reconstructed publication markers and the much smaller same-cycle paired subset answer different validation questions. Unequal transmitting schedules and the **Target-Active Gate** also affect non-joint counts. Follow the original image, reconstruction, and native evidence panels to see which observations survive each rule. This case is particularly useful for a manual evidence audit; sparse pairs and station differences limit broader antenna conclusions.
