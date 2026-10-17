### Ein erneuter Blick auf die veröffentlichte Abbildung 3

Kann WSPRadar die Ergebnisse des ursprünglichen Experiments von 2017 reproduzieren?

Der Vergleich führt **die veröffentlichte Abbildung 3, eine Rekonstruktion aus historischen WSPR-Meldungen und WSPRadars eigenes chronologisches Diagramm** zusammen. Alle zeigen die allgemeine Zunahme des SNR-Vorteils von G3ZIL während der ersten Aprilhälfte.

Die Rekonstruktion macht auch die Unterschiede zwischen den Darstellungen sichtbar. Die ursprüngliche Abbildung enthält Beobachtungen der Bodenfeuchte, während WSPRadar Empfangsmeldungen analysiert. Die Diagramme verwenden unterschiedliche zeitliche Aggregationen und vertikale Skalen; es ist daher nicht zu erwarten, dass sie identisch aussehen.

[**Die ursprüngliche Abbildung 3, die Rekonstruktion und den Vergleich mit WSPRadar erkunden (PDF) ↗**](https://wspradar.streamlit.app/~/+/app/static/reference_figures/griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3.pdf)

**Für Fortgeschrittene: Warum stimmen nicht alle Beobachtungen überein?**

Einige WSPR-Sendezyklen enthalten mehrere Empfangsmeldungen für dieselbe Station. WSPRadar behält an jeder Empfangsstation das höchste SNR bei, das die Auswahlkriterien erfüllt, und erstellt einen gepaarten Vergleich pro Sender und Zyklus.

Ein alternativer Ansatz, der alle Kombinationen der Meldungen berücksichtigt, kann bestimmte Merkmale des veröffentlichten Diagramms reproduzieren — darunter einen Ausläufer mit negativen SNR-Werten am 16. April —, die von WSPRadars Ergebnissen abweichen. Das genaue Verfahren der ursprünglichen Autoren zum Umgang mit Mehrfachmeldungen ist nicht dokumentiert. Dies ist daher eine plausible Erklärung für die Unterschiede, kein Nachweis ihrer Berechnungsmethode.

[**Paarbildung und Mehrfachmeldungen einschließlich eines durchgearbeiteten Beispiels erkunden (PDF) ↗**](https://wspradar.streamlit.app/~/+/app/static/reference_figures/griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3_diagnostic.pdf)
