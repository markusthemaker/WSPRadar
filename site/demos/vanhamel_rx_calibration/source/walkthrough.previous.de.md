<!-- section: hero -->
# #4 Dr. Vanhamel et al.: Empfangskette kalibrieren – einen Empfängeroffset von 1,2 dB bestimmen

<!-- section: setup -->
## Experiment und Interpretation

[Publikation: Vanhamel, J., Machiels, W., & Lamy, H. (2022). Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band](https://doi.org/10.1155/2022/4809313)

Bevor du zwei Antennen vergleichst, prüfe zunächst, ob die Empfangstechnik selbst einen Unterschied verursacht. Diese Demo zeigt die **Kalibrierung der Empfangskette**: Dabei wird eine systematische Differenz im gemeldeten Signal-Rausch-Verhältnis (SNR) gemessen, damit sie bei einem anschließenden Antennenvergleich berücksichtigt werden kann. Zur Empfangskette gehören Empfänger, Filter, Kabel und Einstellungen der Signalverarbeitung.

Die Demo rekonstruiert eine siebentägige Vergleichsbasis zur Kalibrierung der Empfangsketten vom 6. bis 13. Februar 2021 ohne SNR-Korrektur. Die Publikation beschreibt eine Kalibrierung, bei der beide Empfangsketten an derselben Antenne angeschlossen waren. WSPRadar vergleicht **ON4AWM0 als Target** mit **ON4AWM1 als Referenz** auf **160 m**. Verwendet werden das Archivfenster vom **6. Februar, 06:00 UTC, bis zum 13. Februar, 06:00 UTC**, und sendende Stationen in bis zu **2.500 km** Entfernung. Bei der in der Publikation beschriebenen Anordnung mit gemeinsamer Antenne zeigt eine anhaltende Differenz einen Offset zwischen den Empfangsketten, der andernfalls den Antennenvergleich beeinflussen würde.

WSPRadar ordnet Reports **derselben sendenden Station mit demselben gemeldeten Locator im selben zweiminütigen WSPR-Zyklus** einander zu, wenn beide Empfänger das Signal decodiert haben. Jede so gepaarte Beobachtung ist ein **Joint Spot**. Die Differenz lautet **ΔSNR = ON4AWM0 − ON4AWM1**: Positive Werte bedeuten, dass ON4AWM0 ein höheres SNR gemeldet hat, negative Werte ein höheres SNR bei ON4AWM1; 0 dB bedeutet gleiches gemeldetes SNR. Reports, die nur ein Empfänger decodiert hat, liefern keine solche gepaarte Differenz.

Öffne **Segment-Inspektor → Benchmark-Evidenz**, lasse alle Entfernungsbereiche und Richtungen ausgewählt und lies den **Mittelwert** für **Joint-Spot Δ SNR** ab. Die 1.143 zyklusgleichen gemeinsamen Reports stammen von zehn Sendern, die den Schwellenwert von ≥50 gemeinsamen Reports erfüllen. Ihr Mittelwert für ON4AWM0 − ON4AWM1 beträgt +1,214 dB, angezeigt als +1,2 dB; der Median jedes einzelnen Senders beträgt +1,0 dB. Der Schwellenwert bedeutet, dass jeder berücksichtigte Sender während der ausgewählten Woche mindestens 50 gepaarte Beobachtungen beitragen muss.

Vergleiche dies mit **Stationsmediane (Δ SNR)**: Dort geht jeder Sender mit genau einem Median ein, hier jeweils **+1,0 dB**. Der **Joint-Spot-Mittelwert von +1,2 dB** mittelt über alle 1.143 gepaarten Beobachtungen und ist der Wert, der mit dem in der Publikation angegebenen Durchschnitt verglichen wird.

Eine Addition von **+1,2 dB** zum SNR des Referenzempfängers ON4AWM1 würde die rekonstruierte mittlere Differenz nahe an **0 dB** bringen. Diese Demo belässt die Korrektur bei **0,0 dB**, damit der ursprüngliche Offset sichtbar bleibt.

<!-- section: step-1 -->
## Vom Aufbau mit gemeinsamer Antenne ausgehen

Die Publikation beschreibt zwei Empfangsketten, die an dieselbe Antenne angeschlossen sind. Die Demo vergleicht **ON4AWM0 als Target** mit **ON4AWM1 als Referenz** in der angegebenen Woche auf 160 m. In diesem Aufbau zeigt eine anhaltende gepaarte SNR-Differenz einen Versatz zwischen den Empfangsketten, der einen späteren Antennenvergleich beeinflussen würde.

<!-- section: step-2 -->
## Den Mittelwert der Joint Spots lesen

Lasse im **Segment-Inspektor → Benchmark-Evidenz** alle Entfernungen und Richtungen ausgewählt. Lies bei **Joint-Spot Δ SNR** den Mittelwert über alle gepaarten Beobachtungen: Der rekonstruierte Wert beträgt **+1,214 dB**, angezeigt als **+1,2 dB**. Jeder Joint Spot trägt eine Differenz bei. Die gewählte Evidenzschwelle verlangt mindestens 50 Joint-Beobachtungen je berücksichtigtem Sender.

<!-- section: step-3 -->
## Eine andere Gewichtung vergleichen

Betrachte nun **Stationsmediane (Δ SNR)**. Jeder Sender trägt einen Median bei, nicht einen Wert pro Joint Spot; hier liegen diese Stationsmediane bei **+1,0 dB**. Das ist kein widersprüchliches Kalibrierergebnis. Der Mittelwert der Joint-Spot-Differenzen und die Zusammenfassung der Stationsmediane verwenden unterschiedliche Beobachtungseinheiten und Gewichte. Benenne daher beim Zitieren eines Werts stets die verwendete Statistik.

<!-- section: step-4 -->
## Das Vorzeichen der Korrektur verstehen

Die angezeigte Differenz lautet **ON4AWM0 − ON4AWM1**. Eine Addition von **+1,2 dB** zum Referenz-SNR würde die rekonstruierte mittlere Differenz nahe null verschieben. Die installierte Demo belässt die Korrektur bewusst bei **0,0 dB**, damit der ursprüngliche Versatz sichtbar bleibt. Demo #5 erläutert eine gesonderte Korrektur von **+1,6 dB** für ihre Rekonstruktion von Abbildung 6; ersetze einen Wert nicht stillschweigend durch den anderen.
