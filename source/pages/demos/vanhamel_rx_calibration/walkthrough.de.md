<!-- section: hero -->
# Eine Antenne, zwei Empfänger — warum die Kalibrierung zählt

### Erst die Empfänger kalibrieren, dann die Antennen vergleichen

Zwei Empfänger an derselben Antenne sollten ähnliche Ergebnisse liefern. Mit WSPRadar lässt sich erkennen, welchen Unterschied die Empfangstechnik selbst verursacht – bevor er als Vorteil einer Antenne ausgelegt wird.

<!-- section: setup -->
## Was wollten die Funkamateure untersuchen?

Bevor sie zwei Antennen verglichen, prüften Jurgen Vanhamel, Walter Machiels und Hervé Lamy zunächst die Empfangstechnik. Ihre [Publikation](https://doi.org/10.1155/2022/4809313) beschreibt **zwei Empfangsketten, die über einen Leistungsteiler an derselben Langdrahtantenne angeschlossen waren**. Beide verwendeten dieselben Einstellungen für die Signalverarbeitung. Diese Demo vergleicht die archivierten Empfangsreports von **ON4AWM0 und ON4AWM1**.

Zur Empfangskette gehört mehr als der Empfänger: Auch Kabel, Filter und die Einstellungen der Signalverarbeitung sind Teil des Aufbaus. Werden beide Empfangsketten aus derselben Antenne gespeist, liefert eine anhaltende SNR-Differenz eine Vergleichsbasis für die Empfangstechnik, keinen Antennenvergleich.

**Unsere Frage lautet: Wie groß ist dieser Unterschied, und reichen die Beobachtungen aus, um ihn als Grundlage für eine Kalibrierung zu verwenden?**

SNR bezeichnet das Signal-Rausch-Verhältnis: Es beschreibt, wie stark sich ein Signal vom Rauschen abhebt. Ein höheres SNR ist besser. WSPRadar sucht nach Fällen, in denen beide Empfänger **dieselbe sendende Station mit demselben gemeldeten Locator im selben zweiminütigen WSPR-Zyklus** gemeldet haben. Ein **Joint Spot** entsteht, wenn beide Empfänger denselben Sender im selben zweiminütigen WSPR-Zyklus melden, sodass wir ihre SNR-Werte zur selben Zeit vergleichen können. Signale, die nur ein Empfänger decodiert hat, liefern keine solche gepaarte Differenz.

In dieser Demo wird keine Korrektur angewendet:

**ΔSNR = SNR von ON4AWM0 − SNR von ON4AWM1**

Positive Werte bedeuten, dass ON4AWM0 das höhere SNR gemeldet hat; bei negativen Werten war es ON4AWM1. Null bedeutet gleiches gemeldetes SNR.

<!-- section: step-1 -->
## Die Demo laden und ihre Einstellungen prüfen

Wähle oben **In WSPRadar App starten**, um die vorbereitete Demo zur Empfängerkalibrierung zu öffnen. Die Einstellungen werden automatisch geladen:

| Einstellung | Wert in dieser Demo | Bedeutung |
|---|---|---|
| Analyse | RX-Benchmark | Den Empfang der beiden Empfangsketten vergleichen. |
| Target | ON4AWM0, QTH JO20OT | Die zu untersuchende Empfangskette. |
| Referenz | ON4AWM1, gemeldeter Locator JO20 | Die Empfangskette für den Vergleich; die gemeldete Locatorauflösung bleibt erhalten. |
| Benchmark-Design | Referenzaufbau/-station | Mit genau dieser Referenz vergleichen. |
| Frequenzband | 160 m | Empfangsreports dieses Bands verwenden. |
| UTC-Zeitraum | 6. Februar 2021, 06:00 → 13. Februar 2021, 06:00 | Eine Woche mit Beobachtungen untersuchen. |
| Maximale Peer-Entfernung vom Target (km) | 2 500 km | Sendende Stationen bis zu dieser Entfernung vom Target berücksichtigen. |
| Referenzseitige SNR-Korrektur (dB) | 0,0 dB; Offset-Ermittlungslauf einrichten | Den ursprünglichen Unterschied der Empfangstechnik sichtbar lassen. |
| Minimale Joint-Evidenz pro Station | 50 | Jeder berücksichtigte Stationseintrag muss in der gewählten Woche mindestens 50 gepaarte Beobachtungen beitragen. |

Öffne direkt **Segment-Inspektor → Benchmark-Evidenz** und lasse **Gesamter Bereich \| Alle Richtungen** ausgewählt. Für diese Fragestellung müssen wir nicht alle Ergebnisansichten durchgehen.

<!-- section: step-2 -->
## Benchmark-Evidenz lesen: Stimmen die Empfänger überein?

**Benchmark-Evidenz: ein kleiner Unterschied, der sich bei mehreren Sendern wiederholt**

*Beide angezeigten Mediane liegen bei +1,0 dB. Das arithmetische Mittel über alle gepaarten Beobachtungen beträgt +1,2 dB.*

### Wie groß ist der typische Unterschied?

Beginne mit den beiden SNR-Diagrammen.

**Stationsmediane (Δ SNR): +1,0 dB.** WSPRadar bestimmt zunächst für jeden Sender den Median der Differenzen und anschließend den Median dieser Stationsmediane. Jeder beteiligte Stationseintrag erhält dasselbe Gewicht, unabhängig davon, wie oft er empfangen wurde.

**Joint-Spot Δ SNR: +1,0 dB.** In dieses Diagramm geht jeder gepaarte Vergleich ein. Häufig empfangene Sender haben deshalb einen größeren Einfluss.

Der Median ist der mittlere Wert, wenn die Werte der Größe nach geordnet werden; bei einer geraden Anzahl ist es der Durchschnitt der beiden mittleren Werte. Hier liefern beide Zusammenfassungen dasselbe Ergebnis: **ON4AWM0 meldet typischerweise ein etwa 1 dB höheres SNR als ON4AWM1**.

Das Joint-Spot-Diagramm zeigt außerdem **Arithmetisches Mittel: +1,2 dB** – den Durchschnitt über alle gepaarten Beobachtungen. Mittelwert und Median beschreiben die Verteilung auf unterschiedliche Weise; hier weisen beide auf denselben kleinen, positiven Empfängeroffset hin. Der Mittelwert liefert den Kalibrierwert für diesen Lauf.\*

### Wie gut ist das Ergebnis durch Beobachtungen gestützt?

**Decode Outcomes** zeigt, welche Signale einen Vergleich ermöglichten. Die schraffierten Balken stehen für Stationseinträge, die ausgefüllten für Beobachtungen.

Hier liefern **zehn Stationseinträge insgesamt 1 143 Joint Spots**. Das sind rund **91 % der 1 257 berücksichtigten Beobachtungen**. Ein Stationseintrag besteht aus dem Rufzeichen und dem vollständigen gemeldeten Locator. Die übrigen **114 Beobachtungen** liefern kein ΔSNR-Paar aus demselben WSPR-Zyklus.

Jeder beteiligte Stationseintrag trägt **52 bis 344 gepaarte Beobachtungen** bei, und **alle zehn Stationsmediane liegen bei +1,0 dB**. Das Ergebnis wiederholt sich also bei verschiedenen Sendern und beruht weder auf einem einzelnen Signal noch auf wenigen Reports.

Der **schraffierte Stationsbalken mit 100 %** steht für Joint-Evidenz und ergibt sich aus der Auswahl: Stationen mit zu wenigen gepaarten Beobachtungen wurden bereits ausgeschlossen. Er bedeutet nicht, dass beide Empfänger jede Aussendung decodiert haben.

**Aussagekräftig ist die Übereinstimmung:** Die Stationswerte, die einzelnen Vergleiche und die zugehörigen Anzahlen sprechen unter der Annahme einer gemeinsamen Antenne für einen kleinen Unterschied der Empfangstechnik. Die Anzahlen beschreiben die ausgewählten Beobachtungen; sie liefern weder ein Unsicherheitsintervall noch einen Nachweis des damaligen Geräteaufbaus.

<!-- section: step-3 -->
## Das Ergebnis festhalten und den Antennenvergleich vorbereiten

> **In der gewählten Archivwoche meldete ON4AWM0 ein im Mittel um 1,2 dB höheres SNR als ON4AWM1. Das Ergebnis stützt sich auf 1 143 Vergleiche aus demselben WSPR-Zyklus von zehn sendenden Stationseinträgen. Sind beide Empfangsketten an derselben Antenne angeschlossen, bildet ein solcher Offset die Vergleichsbasis der Empfangstechnik und keinen Antennenvorteil; die Archivdaten allein belegen diesen Anschluss nicht für die gesamte Woche.**

Um diesen Offset zu berücksichtigen, würde eine **SNR-Korrektur der Referenz von +1,2 dB** das SNR von ON4AWM1 vor der Subtraktion anheben und die mittlere Differenz damit nahe null bringen. Die vorbereitete Kalibrierungsdemo belässt die Korrektur bei null, damit der ursprüngliche Offset sichtbar bleibt.

Speichere das Ergebnispaket und halte Band, Anschlüsse und Empfängereinstellungen fest. Die Korrektur gilt für den geprüften Aufbau; nach Änderungen an Geräten oder Einstellungen sollte sie nicht ungeprüft weiterverwendet werden.

Du hast nun nachvollzogen, wie sich der Beitrag der Empfangstechnik bestimmen lässt. Als Nächstes zeigt ein korrigierter Vergleich, was sich beim Drehen einer Empfangsantenne ändert.

[**Weiter zu: 90° gedreht, 3 dB Unterschied →**](/de/demos/vanhamel_rx_buddy/)

Demo #5 verwendet für ihre Rekonstruktion von Abbildung 6 eine gesonderte **SNR-Korrektur der Referenz von +1,6 dB**. Die zugehörige Anleitung erläutert diese Wahl; ersetze einen Kalibrierwert nicht stillschweigend durch den anderen.

---

\* Der Mittelwert von +1,2 dB stimmt bei der angezeigten Genauigkeit mit der von Vanhamel und Kollegen beschriebenen Kalibrierung an einer gemeinsamen Antenne überein. Aus dem gerundeten Mittelwert der Publikation gehen weder die genaue Gewichtung noch die Zuordnung des Vorzeichens zu den Empfängern oder die gewählten Archivdaten hervor. Die Publikation verlangt mehr als 50 Empfangsbeobachtungen je Station; die Demo verwendet mindestens 50 Joint Spots. In dieser festgehaltenen Rekonstruktion hat kein Stationseintrag genau 50. Deshalb wählen die Schwellen > 50 und ≥ 50 hier dieselben Einträge aus. [Originalpublikation ↗](https://doi.org/10.1155/2022/4809313)
