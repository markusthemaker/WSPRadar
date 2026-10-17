<!-- section: hero -->
# #2 Prof. Griffiths (G3ZIL) et al. RX Comparison: Day/Night SNR Reversal: Low Dipole vs Vertical

A **Joint Spot** occurs when both receivers report the same transmitter in the same two-minute WSPR cycle, allowing us to compare their SNR at the same time.

<!-- section: setup -->
## Reproduce this setup

Select ‘Run in WSPRadar App’ to load this demo and start its analysis.

<!-- section: step-1 -->
## Keep the comparison direction fixed

This example uses the same **G3ZIL − G4HZX** difference as demo #1, but restricts the observations to **5–7 April 2017**. Positive values favor the low-dipole receiving station; negative values favor the vertical receiving station. Begin with all directions and distances selected so that the first view matches the overall question posed by the demo.

<!-- section: step-2 -->
## Read the daily pattern by UTC hour

Open **Segment Inspector → Temporal Evidence → Δ SNR by UTC Hour (1 h bins)**. Each hourly interval combines observations from that hour on all three dates. Follow the hourly medians through zero: the early-hour advantage of G4HZX gives way to an advantage of G3ZIL later in the day. The colors describe concentrations of observations; the shaded band describes their middle 50%. Neither means every transmission followed the median.

<!-- section: step-3 -->
## Compare folding with chronological time

Now inspect **Δ SNR over Time**. Folding is useful for seeing a recurring daily pattern, but it hides which date supplied an observation. The chronological chart restores that distinction. Compare the three dates before treating the folded shape as a pattern shared equally by every day, then use **Station Insights** to ask whether a selected transmitter follows it.

<!-- section: step-4 -->
## Read the comparison panels with their limits

Compare the original publication with the reconstruction and the native WSPRadar view. Their density presentations are not identical statistical renderings. Read the annotations, labeled axes, and color scales for each panel rather than judging agreement by color alone. The case supports examination of a day/night reversal in relative reception; it does not isolate antenna, noise, or propagation as its cause.
