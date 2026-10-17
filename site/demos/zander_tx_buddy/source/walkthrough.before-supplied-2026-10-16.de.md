<!-- section: hero -->
# #6 Prof. Zander et al. TX-Antennenvergleich: kurze Portabel-Vertikalantenne gegen 5/8-λ-Vertikalantenne

<!-- section: setup -->
## Diesen Aufbau nachvollziehen

Wähle ‚In WSPRadar App starten‘, um diese Demo zu laden und ihre Analyse zu starten.

<!-- section: step-1 -->
## Die beiden Sendeaufbauten bestimmen

Das Target ist **SK0WE/P mit der kurzen Difona-Vertikalantenne**, die Referenz **SK0WE/1 mit der Hy-Gain AV620**. Beide befinden sich in JO97. Behalte für den Vergleich mit der Publikation das installierte Zeitfenster **21. Mai 2022, 09:45–10:30 UTC** bei. Ein Joint Spot erfordert Berichte über beide Sender vom selben entfernten Empfänger und Locator im selben zweiminütigen Zyklus.

<!-- section: step-2 -->
## Histogramme mit derselben Beobachtungseinheit vergleichen

Lasse im **Segment-Inspektor → Benchmark-Evidenz** alle Richtungen und Entfernungen ausgewählt und verwende das Histogramm **Joint-Spot Δ SNR**. Sein Mittelwert beträgt über **166 gemeinsame Empfängerzyklen −6,78 dB** und spricht für die Referenz. Im Histogramm **Stationsmediane (Δ SNR)** erhält stattdessen jeder Empfänger einen Median. Nutze es für eine andere Gewichtung, nicht als gleichartigen Ersatz für die Joint-Spot-Verteilung der Publikation.

<!-- section: step-3 -->
## Unterschiedliche Balkenhöhen verstehen

Die Publikation und das native WSPRadar-Histogramm verwenden unterschiedliche Klassenbreiten und Einheiten der vertikalen Achse. Das Rekonstruktionspanel verbindet die gröbere, dichtebasierte Publikationsdarstellung mit WSPRadars **1-dB-Klassen** und Prozentanteilen gepaarter Beobachtungen. Vergleiche Klassengrenzen und Achsenbeschriftungen, bevor du Balkenhöhen gegenüberstellst. Die feinere native Darstellung bedeutet nicht, dass andere gepaarte Beobachtungen verwendet werden.

<!-- section: step-4 -->
## Räumliche Unterschiede des relativen Vorteils untersuchen

Vergleiche in der **Kartenansicht** die erfassten nordamerikanischen Funkwege mit europäischen Richtungen und untersuche diese anschließend im **Segment-Inspektor**. Kartensektoren fassen die medianen ΔSNR-Werte der Empfänger mit gleichem Empfängergewicht zusammen; sie zeigen nicht den Mittelwert aller Joint Spots. Wähle einzelne Empfänger in **Station Insights**, um die beitragenden Funkwege zu prüfen. Ungefärbte Sektoren besitzen keine gestützte Schätzung und weisen keine Antennennullstellen nach.
