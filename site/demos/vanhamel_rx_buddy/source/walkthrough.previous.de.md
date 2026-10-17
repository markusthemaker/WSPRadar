<!-- section: hero -->
# #5 Dr. Vanhamel et al.: Empfangsantenne drehen – Rekonstruktion des 3-dB-ΔSNR-Sprungs aus Abbildung 6

<!-- section: setup -->
## Experiment und Interpretation

[Publikation: Vanhamel, J., Machiels, W., & Lamy, H. (2022). Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band](https://doi.org/10.1155/2022/4809313)

**Was ändert sich, wenn eine Empfangsantenne um 90° gedreht wird?** Diese Demo greift Abbildung 6 auf und vergleicht **ON4AWM0 mit einer Langdrahtantenne ITA LWA II** mit **ON4AWM1 mit einem modifizierten kurzgeschlossenen Dipol** auf **160 m im Zeitraum vom 1. bis 15. Mai 2021**. Die Langdrahtantenne blieb unverändert ausgerichtet; den Dipol drehten die Autoren nach der ersten Woche.

**M7AEO (IO82) ist in Station Insights vorausgewählt** und entspricht damit der sendenden Station in Abbildung 6. WSPRadar vergleicht Signale dieses Senders, die beide Empfänger im selben zweiminütigen WSPR-Zyklus decodiert haben. Jede so gepaarte Beobachtung ist ein **Joint Spot**. Die Differenz lautet **ΔSNR = ON4AWM0 − korrigiertes ON4AWM1**: Positive Werte fallen zugunsten der Empfangsstation mit Langdrahtantenne aus, negative zugunsten der Empfangsstation mit Dipol.

Öffne **Evidenz der ausgewählten Station → Δ SNR im Zeitverlauf (12h-Intervalle)**. Achte auf den Anstieg um den **8. Mai**. Bei insgesamt **1.441 Joint Spots** beträgt der Median **−0,6 dB für die ersten 750 Beobachtungen** und **+2,4 dB für die übrigen Beobachtungen**: eine **Verschiebung um 3 dB**, die mit dem Anstieg in der Publikation im Einklang steht. Dies beschreibt eine Änderung des relativen Empfangs auf dem durch die Beobachtungen erfassten Funkweg, keine Messung des Antennengewinns in allen Richtungen.

Die Markierungen zeigen den Median jedes Zeitintervalls; das schattierte Band umfasst, sofern dargestellt, die mittleren 50 % der Beobachtungen. Die Farben zeigen, wo sich Beobachtungen konzentrieren. Lies die senkrechte Achse anhand der beschrifteten dB-Werte ab: Ihre Teilung ist nichtlinear. Für das übergreifende Muster über mehrere Sender nutze **Segment-Inspektor → Zeitliche Evidenz** und wähle alle Entfernungsbereiche und Richtungen aus. In dieser zusammengefassten Ansicht erhalten Sender mit mehr Joint Spots ein höheres Gewicht.

[**Vergleich mit Abbildung 6 (PDF)**](app/static/reference_figures/vanhamel_fig6_rotation_v1/WSPRadar_Demo_Vanhamel_Figure6.pdf): Vergleiche die Publikation in **Panel A**, die einzeln rekonstruierten Empfangsbeobachtungen in **Panel B**, die zugehörigen Dichte-Bins hinter der schwarzen ΔSNR-Kurve in **Panel C** und die native UTC-Ansicht von WSPRadar in **Panel D**. Übereinstimmende Bin-Nummern verbinden die Panels C und D: Jede nummerierte Spalte umfasst in Panel C Empfangsnummern und in Panel D verstrichene Zeit. Die Empfangsnummern zählen aufeinanderfolgende Beobachtungen; sie messen keine verstrichene Zeit. Sieben markierte Maxima und Minima weichen um höchstens eine Empfangsbeobachtung und höchstens 0,1 dB von der Publikation ab und liegen damit innerhalb der grafischen Ablesetoleranzen.

Diese Demo wendet eine **SNR-Korrektur der Referenz von +1,6 dB** an. Dies ist der gerundete Wert der Kalibrierung von **1,57 dB**, die auf der [Website der Autoren](https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-antenna-comparison-instrument) dokumentiert ist. Der Text der Publikation nennt **1,2 dB**, wie in Demo #4 untersucht. Die Rekonstruktion mit +1,6 dB stimmt eng mit Abbildung 6 überein, belegt jedoch nicht, welche Korrektur bei der Erstellung der veröffentlichten Abbildung verwendet wurde. Eine konstante Korrektur verschiebt die gesamte ΔSNR-Kurve senkrecht; sie verändert nicht die Höhe des Sprungs.

<!-- section: step-1 -->
## Den Funkweg der Publikation verfolgen

Behalte **M7AEO (IO82)** in **Station Insights** ausgewählt. Das genaue Rufzeichen und der Locator kennzeichnen den Sendefunkweg dieses Vergleichs. Die Empfänger sind ON4AWM0 mit der unveränderten Langdrahtantenne und ON4AWM1 mit dem Dipol, den die Autoren nach der ersten Woche drehten. Die ausgewählte Evidenz betrifft diesen Funkweg; sie ist kein vollständiges Antennen-Strahlungsdiagramm.

<!-- section: step-2 -->
## Die Veränderung um den 8. Mai finden

Öffne **Evidenz der ausgewählten Station → Δ SNR im Zeitverlauf (12h-Bins)**. Lies ΔSNR als ON4AWM0 minus korrigiertes ON4AWM1 und suche den Übergang nach oben. Die dokumentierte Aufteilung in die ersten 750 und die verbleibenden Beobachtungen ergibt Mediane von **−0,6 dB** und **+2,4 dB**. Das ist eine **Verschiebung um 3 dB** zwischen diesen Beobachtungsgruppen, keine Aufteilung des Messzeitraums in gleich lange Hälften.

<!-- section: step-3 -->
## Empfangsnummer und verstrichene Zeit verbinden

Lies die vier Vergleichspanels der Reihe nach. Panel A bewahrt die Publikation; Panel B rekonstruiert die Beobachtungen in Empfangsreihenfolge; Panel C ordnet native Dichte-Bins ihren Bereichen von Empfangsnummern zu; Panel D zeigt die native UTC-Ansicht. Übereinstimmende Bin-Nummern verbinden Panels C und D. Empfangsnummern zählen Beobachtungen, UTC misst dagegen verstrichene Zeit: Ein Zeitraum ohne Empfang erhält keine Breite auf der Empfangsnummernachse.

<!-- section: step-4 -->
## Vertikalen Versatz und Sprunghöhe unterscheiden

Die Demo verwendet eine **Referenz-SNR-Korrektur von +1,6 dB**. Die ursprüngliche Beschreibung unten erläutert sie zusammen mit dem Wert von **1,2 dB** aus der Publikation. Eine konstante Korrektur verschiebt die gesamte Differenzkurve vertikal, verändert aber nicht die Größe des Übergangs. Lies native Achsen anhand ihrer beschrifteten dB-Werte, da ihre Abstände nichtlinear sind. Nutze **Segment-Inspektor → Zeitliche Evidenz** für die breitere, zusammengefasste Senderpopulation und halte sie vom ausgewählten Funkweg M7AEO getrennt.
