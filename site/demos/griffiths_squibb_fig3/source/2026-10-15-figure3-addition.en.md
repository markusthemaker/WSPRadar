### Revisiting the published Figure 3

Can WSPRadar reproduce the findings of the original 2017 experiment?

The comparison brings together **the published Figure 3, a reconstruction from historical WSPR reports, and WSPRadar's own chronological chart**. All reveal the general increase in G3ZIL's SNR advantage during the first half of April.

The reconstruction also makes the differences between the representations visible. The original figure includes soil-moisture observations, whereas WSPRadar analyzes reception reports. The charts use different time aggregations and vertical scales, so they should not be expected to look identical.

[**Explore the original Figure 3, reconstruction and WSPRadar comparison (PDF) ↗**](https://wspradar.streamlit.app/~/+/app/static/reference_figures/griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3.pdf)

**Advanced: Why don't all observations match?**

Some WSPR transmission cycles contain multiple reception reports for the same station. WSPRadar retains the strongest qualifying SNR at each receiving station and creates one matched comparison per transmitter and cycle.

An alternative approach that includes all report combinations can reproduce specific features of the published graph—including a negative-SNR tail on 16 April—that differ from WSPRadar's results. The original authors' exact duplicate-handling procedure is not documented, so this is a plausible reconciliation, not proof of their calculation method.

[**Explore pairing and multiple reports, including a worked example (PDF) ↗**](https://wspradar.streamlit.app/~/+/app/static/reference_figures/griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3_diagnostic.pdf)
