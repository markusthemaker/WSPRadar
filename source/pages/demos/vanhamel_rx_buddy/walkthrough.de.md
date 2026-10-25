<!-- section: hero -->
# Eine Antennendrehung um 90°, ein Unterschied von 3 dB

### So verändert die Antennenausrichtung den Empfang

Lass eine Antenne unverändert, drehe die andere und verfolge den Unterschied.

<!-- section: setup -->
## Was wollten die Funkamateure untersuchen?

**Lässt sich in WSPR-Ergebnissen erkennen, wenn eine Empfangsantenne um 90° gedreht wird?**

Jurgen Vanhamel, Walter Machiels und Hervé Lamy verglichen zwei Empfangsaufbauten auf 160 m:

**ON4AWM0 — Target:** eine Langdrahtantenne ITA LWA II, deren Ausrichtung während des gesamten Experiments unverändert blieb.

**ON4AWM1 — Referenz:** ein modifizierter kurzgeschlossener Dipol, zunächst parallel zur Langdrahtantenne aufgestellt und dann **nach der ersten Woche in der horizontalen Ebene um 90° gedreht**.

Beide Empfänger meldeten während des Vergleichs WSPR-Signale. WSPRadar ordnet Empfangsreports **desselben Senders mit demselben gemeldeten Locator aus demselben zweiminütigen WSPR-Zyklus** einander zu. Ein **Joint Spot** entsteht, wenn beide Empfänger denselben Sender im selben zweiminütigen WSPR-Zyklus melden, sodass wir ihre SNR-Werte zur selben Zeit vergleichen können.

SNR bezeichnet das Signal-Rausch-Verhältnis: Es beschreibt, wie stark sich ein Signal vom Rauschen abhebt. Ein höheres SNR ist besser. Unser Vergleich lautet:

**ΔSNR = SNR von ON4AWM0 − (SNR von ON4AWM1 + SNR-Korrektur)**

Positive Werte fallen zugunsten des Empfangsaufbaus mit Langdrahtantenne aus, negative zugunsten des Aufbaus mit Dipol. **Gedreht wird der Dipol, nicht die Langdrahtantenne.**

Die ergänzende Demo [**Eine Antenne, zwei Empfänger — warum die Kalibrierung zählt**](/de/demos/vanhamel_rx_calibration/) erklärt, wie sich zunächst die Empfangstechnik prüfen lässt. Hier lädt die vorbereitete Demo bereits eine Empfängerkorrektur, damit wir uns auf den Antennenvergleich konzentrieren können.

**Unsere Frage lautet: Wo, wann und um wie viel hat sich der relative Empfang verändert?**

<!-- section: step-1 -->
## Die Demo laden und ihre Einstellungen prüfen

Wähle oben **In WSPRadar App starten**, um die vorbereitete Demo zur Antennendrehung zu öffnen.

| Einstellung | Wert in dieser Demo | Bedeutung |
|---|---|---|
| Analyse | RX-Benchmark | Den Empfang der beiden Antennenaufbauten vergleichen. |
| Target | ON4AWM0, QTH JO20OT | Der unveränderte Aufbau mit Langdrahtantenne und der Kartenmittelpunkt. |
| Referenz | ON4AWM1, gemeldeter Locator JO20 | Der Aufbau mit dem gedrehten Dipol. |
| Benchmark-Design | Referenzaufbau/-station | Mit genau dieser Referenz vergleichen. |
| Band | 160 m | Empfangsreports dieses Bands verwenden. |
| UTC-Zeitfenster | 1. Mai 2021, 17:15 → 15. Mai 2021, 07:00 | Beide Antennenausrichtungen erfassen. |
| Referenzseitige SNR-Korrektur | +1,6 dB; ermittelter Versatz\* | Den Unterschied zwischen den Empfangsketten berücksichtigen. |

Die Übersicht umfasst Sender im Umkreis von **5 000 km**. Die Diagramme zum Zeitverlauf verwenden **12-Stunden-Intervalle**. Für die Betrachtung einer einzelnen Station ist **M7AEO mit Locator IO82** vorausgewählt.

Beginne mit der Auswahl **Gesamter Bereich | Alle Richtungen**.

<!-- section: step-2 -->
## Die Karte lesen: Zeigt sich in jeder Richtung dasselbe Bild?

Der Mittelpunkt der Azimutkarte ist ON4AWM0. Die Sektoren stehen für die Richtungen vom Target aus; die Ringe unterteilen die Entfernung.

Jeder beitragende Sender liefert zunächst seinen eigenen Median der SNR-Differenz. Anschließend bildet WSPRadar den Median dieser Stationsmediane. Häufig empfangene Sender dominieren einen Sektor daher nicht allein deshalb, weil sie mehr Reports liefern.

Lies die Zahlenwerte der Farbskala: Positive Werte fallen zugunsten der Langdrahtantenne aus, negative zugunsten des Dipols. Ungefärbte Sektoren haben keinen Vergleich, der die Anforderungen erfüllt; sie stehen nicht für eine gemessene Differenz von null.

Das Ergebnis hängt von der Richtung ab. Einige Beispiele:

| Geografischer Bereich | Stationsgleichgewichteter Median ΔSNR | Beitragende Stationseinträge |
|---|---:|---:|
| 0–2 500 km, ENE | +4,4 dB | 4 |
| 0–2 500 km, WNW | +0,4 dB | 17 |
| 0–2 500 km, SSE | −3,6 dB | 4 |

In einigen der erfassten Richtungen liegt der Aufbau mit Langdrahtantenne vorn, in anderen der Aufbau mit Dipol. **Kein einzelner Empfangsvorteil beschreibt alle Funkwege.**

Untersuche mit dem **Segment-Inspektor** einen Sektor und prüfe, wie viele Stationen und Joint Spots sein Ergebnis stützen. In dieser Demo dürfen Stationen schon mit einem einzigen Joint Spot beitragen. Eine kräftige Farbe bedeutet daher nicht zwangsläufig, dass viele Beobachtungen dahinterstehen.

Denke daran, dass diese Karte beide Wochen zusammenfasst. Um die mit der Drehung verbundene Veränderung zu erkennen, brauchen wir zusätzlich den Zeitverlauf.

Kehre zu **Gesamter Bereich | Alle Richtungen** zurück, bevor du fortfährst.

<!-- section: step-3 -->
## Benchmark-Evidenz lesen: Wie groß ist der Unterschied insgesamt?

### Welche Signale lieferten einen Vergleich?

In **Decode Outcomes** beziehen sich die schraffierten Balken auf Stationseinträge, die gefüllten Balken auf Beobachtungen.

**60 von 75 Stationseinträgen – 80 % – lieferten Joint Spots.** Zusammen trugen sie **5 379 gepaarte Vergleiche** bei, etwa **75 % der berücksichtigten Beobachtungen**. Auf diesen Vergleichen beruhen die SNR-Ergebnisse.

Weitere 13 Stationseinträge erschienen nur bei ON4AWM0, zwei nur bei ON4AWM1. Ein Stationseintrag bezeichnet hier ein Rufzeichen zusammen mit seinem gemeldeten Locator.

Auf Beobachtungsebene enthält die Kategorie **Beide (Async)** ungepaarte Reports von Sendern, die beide Empfänger gehört haben. Ein Sender kann zu manchen Zeiten Joint Spots liefern und zu anderen ungepaarte Reports.

Für die Auswertung heißt das: **SNR-Differenzen beschreiben die gepaarten Signale, nicht alle Signale, die einer der beiden Empfänger gehört hat.**

### Wie groß ist der typische Vorteil?

**Stationsmediane: +1,4 dB.** Jeder Sender trägt genau einen Median der Differenz bei, unabhängig davon, wie oft er gehört wurde.

**Joint-Spot Δ SNR: +2,4 dB.** Jeder gepaarte Vergleich trägt bei; häufig gehörte Sender erhalten dadurch mehr Gewicht.

Ein Median ist der mittlere Wert, wenn die Werte der Größe nach geordnet werden. Beide Zusammenfassungen fallen insgesamt zugunsten des Aufbaus mit Langdrahtantenne aus. Die Werte müssen nicht identisch sein, weil sie die Beobachtungen unterschiedlich gewichten.

#### Was sagt uns der Unterschied zwischen den Medianen?

**Die beiden Zusammenfassungen stimmen darin überein, welcher Aufbau vorn liegt, beschreiben aber einen unterschiedlich großen typischen Vorteil.** Wenn jeder Sender gleich gewichtet wird, ergeben sich +1,4 dB; wenn jede gepaarte Beobachtung eingeht, ergeben sich +2,4 dB. Dies sind einander ergänzende Ergebnisse – kein Unsicherheitsbereich, in dem der „wahre“ Vorteil liegen muss.

Ein stärker positiver Joint-Spot-Median kann entstehen, wenn Funkwege oder Zeiträume mit größeren Vorteilen mehr Beobachtungen beitragen. Allerdings spielt auch die Streuung der Differenzen innerhalb der Meldungen jedes Senders eine Rolle: **Der Abstand allein verrät nicht, welche Stationen oder Zeiträume ihn verursacht haben.**

Öffne zur Untersuchung **Station Insights** und vergleiche **Joint Spots** mit **Median Δ SNR**. Ein Sender mit Hunderten gepaarten Beobachtungen trägt einen Median zu den Stationsmedianen bei, aber Hunderte Beobachtungen zum Joint-Spot-Panel. Prüfe auch die Anzahlen: Gleiches Stationsgewicht bedeutet nicht, dass die Ergebnisse aller Stationen gleich gut belegt sind.

#### Welches Ergebnis sollte ich verwenden?

Nutze **Stationsmediane**, um zu beantworten: **„Wie schnitten die Empfangsaufbauten über die Sender hinweg ab, wenn jeder Sender gleich gewichtet wird?“** Nutze **Joint-Spot Δ SNR**, um zu beantworten: **„Wie groß war die typische Differenz über alle gepaarten Beobachtungen hinweg?“**

Hier fallen beide Ergebnisse zugunsten der Langdrahtantenne aus. Ihr Unterschied zeigt, dass die Größe des Gesamtvorteils davon abhängt, wie die Evidenz zusammengefasst wird – nicht, dass eines der Ergebnisse falsch ist.

Diese Ergebnisse gelten für den **gesamten Zeitraum von zwei Wochen** und fassen beide Dipolausrichtungen zusammen. **Keiner der beiden Gesamtmediane – und auch nicht der Abstand von 1 dB zwischen ihnen – misst den Effekt der Drehung.** Sie zeigen noch nicht, um wie viel sich der Empfang bei der Drehung des Dipols verändert hat. Verfolge dafür die Ergebnisse im Zeitverlauf.

<!-- section: step-4 -->
## Zeitliche Evidenz lesen: Wann hat sich der Unterschied verändert?

### Linkes Panel: dem Experiment im Zeitverlauf folgen

In **Δ SNR im Zeitverlauf** zeigt jede kreisförmige Markierung den Median der Differenz für ein 12-Stunden-Intervall.

Suche den Anstieg um den **8. Mai**. Mehrere frühe Intervalle mit vielen Beobachtungen liegen bei etwa **−0,6 dB**; spätere Intervalle liegen häufig zwischen **+2,4 und +4,4 dB**. Der relative Empfang hat sich zugunsten des unveränderten Aufbaus mit Langdrahtantenne verschoben.

Die Differenz war während des Experiments also nicht konstant. Ein einziger Gesamtmedian würde diese Veränderung verdecken.

Die gestrichelte Linie zeigt den **Gesamtmedian der Joint Spots von +2,4 dB**. Das schattierte Band umfasst die mittleren 50 % der Beobachtungen jedes Intervalls: Es zeigt die Streuung, kein Konfidenzintervall. Die Hintergrundfarben zeigen, wo sich Beobachtungen konzentrieren. Lies die beschrifteten dB-Werte ab – die senkrechte Skala ist nichtlinear.

Diese Ansicht fasst die Beobachtungen aller Sender zusammen. Häufig gehörte Stationen tragen dadurch mehr bei. Gleich prüfen wir, ob sich die Veränderung auch auf einem einzelnen Funkweg zeigt.

### Rechtes Panel: die Tagesstunden vergleichen

**Δ SNR nach UTC-Stunde** fasst die Beobachtungen derselben UTC-Stunde über den gesamten Lauf zusammen.

Die meisten gepaarten Beobachtungen stammen aus den Abend-, Nacht- und frühen Morgenstunden. Für die Tagesstunden gibt es nur sehr wenige Beobachtungen; einzelne Punkte verdienen deshalb einen genaueren Blick. Das passt zu den starken Veränderungen der Ausbreitungsbedingungen zwischen Tag und Nacht, die durch das Verhalten der Ionosphäre der Erde entstehen.

Auch dieses Stundenprofil fasst beide Antennenausrichtungen zusammen. Nutze es, um das Tagesmuster zu untersuchen. Für den Verlauf des Drehexperiments ist die chronologische Ansicht maßgeblich.

<!-- section: step-5 -->
## Die zeitliche Evidenzabdeckung prüfen: Worauf beruht das Muster?

Das SNR-Diagramm zeigt die Differenzen. Die **Zeitliche Evidenzabdeckung** zeigt, welche Beobachtungen sie stützen.

Die oberen Panels betreffen sendende Stationen, die unteren Senderzyklen. Grün steht für Joint-Evidenz, Violett für Beobachtungen nur beim Target und die ungefüllten Anteile für Beobachtungen nur bei der Referenz. Die Panels nach UTC-Stunde zeigen Mittelwerte über den Lauf.

Die wiederkehrende nächtliche Abdeckung stützt die übergreifende Veränderung. Die Tagesstunden sind deutlich weniger gleichmäßig erfasst.

Zum Beispiel beruht der **Punkt bei +7,4 dB um 13:00 UTC** im SNR-Profil aller Stationen auf **nur einem einzigen Joint Spot im gesamten Lauf**. Das ist eine reale Beobachtung, reicht aber nicht aus, um einen typischen Empfangsvorteil am Tag festzustellen.

Die Linien zum **Joint-Evidenzanteil** zeigen, welcher Anteil der berücksichtigten Evidenz verwertbare Paare bildet. Die stationsgleichgewichtete Linie gewichtet jede Station gleich, die Linie auf Outcome-Ebene jede Beobachtung. **Keine der beiden Linien zeigt eine Erfolgsrate eines Empfängers oder einen „Anteil gewonnener Vergleiche“.**

Beachte auch: Zyklen ohne Beleg dafür, dass ON4AWM0 in Betrieb war, werden ausgeschlossen. Wann ON4AWM1 in Betrieb war, wird nicht unabhängig festgestellt, da WSPRadar nach der Aktivität des Targets filtert. Die einseitigen Empfangsergebnisse liefern deshalb hilfreichen Kontext, sind aber keine symmetrische Erfolgsbilanz.

**Prüfe die Anzahl der Beobachtungen hinter einem auffälligen Wert – nicht nur seine Höhe oder seinen Prozentanteil.**

<!-- section: step-6 -->
## Station Insights öffnen: Zeigt sich die Veränderung auf einem einzelnen Funkweg?

Mit der Tabelle **Station Insights** gelangst du vom übergreifenden Vergleich zu einer einzelnen sendenden Station.

Wähle **M7AEO mit Locator IO82**, das in der Demo bereits vorbereitet ist. Die Station liegt etwa **598 km** von ON4AWM0 entfernt, bei einem Azimut von **291°**. Dieser Funkweg liefert **1 441 Joint Spots**.

Im chronologischen Diagramm liegen die meisten frühen 12-Stunden-Mediane unter null. Nach der Veränderung um den 8. Mai werden die Mediane positiv; viele spätere Intervalle liegen bei etwa **+2,4 dB**.

Der Anstieg zeigt sich damit sowohl auf diesem einzelnen Funkweg als auch in der Übersicht aller Stationen. Eine veränderte Zusammensetzung der Sender in der zusammengefassten Ansicht kann die Veränderung also nicht vollständig erklären.

Behalte das Vorzeichen im Blick: **Der unveränderte Aufbau mit Langdrahtantenne wird relativ zum Aufbau mit gedrehtem Dipol stärker.** Die gedrehte Antenne erzielt hier keine Verbesserung um 3 dB.

<!-- section: step-6-coverage -->
## Evidenzabdeckung des ausgewählten Funkwegs: M7AEO

Über den gesamten Lauf liefert dieser Funkweg **1 441 Joint Spots**, **109 Beobachtungen nur beim Target** und **fünf Beobachtungen nur bei der Referenz**.

Prüfe diese Zahlen zusammen mit dem SNR-Diagramm. Die nächtlichen Intervalle mit vielen Beobachtungen stützen die übergreifende Veränderung, doch nicht jeder Punkt ist gleich gut belegt: Das Intervall **9. Mai, 05:15–17:15 UTC** hat einen **Median von +4,4 dB auf Grundlage eines einzigen Joint Spots**.

<!-- section: step-6-publication -->
## ↳ WSPRadar anhand veröffentlichter Forschung überprüfen

Eine Möglichkeit, WSPRadar zu prüfen, besteht darin, ein veröffentlichtes Experiment erneut zu betrachten und dessen Ergebnisse mit einer Rekonstruktion aus historischen WSPR-Beobachtungen zu vergleichen.

Für M7AEO zeigen **die ursprüngliche Abbildung 6, unsere Rekonstruktion und das chronologische Diagramm von WSPRadar denselben Übergang nach oben**. Die rekonstruierten Mediane vor und nach dem Übergang betragen **−0,6 dB und +2,4 dB – ein Unterschied von 3,0 dB**.†

Die Publikation stellt aufeinanderfolgende Empfangsbeobachtungen dar, während WSPRadar die Beobachtungen nach UTC-Zeit gruppiert. Die Diagramme sehen deshalb unterschiedlich aus, machen aber dieselbe Veränderung des relativen Empfangs sichtbar.

[**Die ursprüngliche Abbildung 6, die Rekonstruktion und den WSPRadar-Vergleich ansehen (PDF) ↗**](/assets/demos/vanhamel_fig6_rotation_v1/WSPRadar_Demo_Vanhamel_Figure6.pdf)

<!-- section: step-7 -->
## Drill-Down nutzen: einen einzelnen Vergleich prüfen

**Drill-Down** legt die Beobachtungen hinter den Zusammenfassungen offen. Wähle M7AEO aus und prüfe die Uhrzeit sowie die beiden SNR-Spalten.

Die Tabelle enthält zum Beispiel:

| UTC-Zeit | SNR von ON4AWM0 | Korrigiertes SNR von ON4AWM1 | ΔSNR |
|---|---:|---:|---:|
| 1. Mai, 18:24 | −20,0 dB | −19,4 dB | −0,6 dB |
| 7. Mai, 20:04 | −12,0 dB | −12,4 dB | +0,4 dB |
| 8. Mai, 20:16 | −16,0 dB | −20,4 dB | +4,4 dB |
| 14. Mai, 20:04 | −17,0 dB | −20,4 dB | +3,4 dB |

Der erste Vergleich fällt zugunsten des Aufbaus mit Dipol aus. Der Vergleich vom 8. Mai fällt zugunsten des Aufbaus mit Langdrahtantenne aus: **−16,0 − (−20,4) = +4,4 dB**.

Dies sind die von WSPRadar verarbeiteten SNR-Werte. Die Referenzspalte enthält die Korrektur bereits; addiere sie nicht erneut.

Du musst nicht Tausende von Zeilen durchsehen. Nutze Drill-Down, um die Rechnung zu überprüfen, einen überraschenden Punkt zu verstehen oder die Beiträge zu einer Zusammenfassung nachzuvollziehen. Das übergreifende Vorher-nachher-Ergebnis stammt aus den vollständigen Beobachtungsgruppen, nicht aus der Auswahl zweier einzelner Zeilen.

<!-- section: step-8 -->
## Das Ergebnis festhalten und sichern

> **WSPRadar macht eine deutliche Veränderung des relativen Empfangs um den 8. Mai sichtbar. Auf dem Funkweg von M7AEO rekonstruieren 1 441 Vergleiche aus jeweils demselben WSPR-Zyklus einen Anstieg um 3 dB, der mit der Drehung des Referenzdipols verbunden ist. In der umfassenderen Auswahl liefern 5 379 Joint Spots von 60 sendenden Stationseinträgen über den gesamten Zeitraum einen stationsgleichgewichteten Median von +1,4 dB zugunsten des Aufbaus mit Langdrahtantenne. Fasst man alle Joint Spots zusammen, ergibt sich ein Median von +2,4 dB. Stationen mit mehr Beobachtungen haben in dieser zusammengefassten Verteilung mehr Einfluss; bei der stationsgleichgewichteten Berechnung erhält der Median jeder Station das gleiche Gewicht. Die Karten- und Zeitansichten zeigen, warum dieses Gesamtergebnis nicht jeden Funkweg und jeden Zeitraum beschreibt.**

Du hast nun eine Änderung am Antennenaufbau von der Karte über den Gesamtvergleich, den Zeitverlauf und eine einzelne sendende Station bis zu einer einzelnen WSPR-Beobachtung verfolgt.

---

\* **Hinweis zur Kalibrierung:** Dieses Beispiel vom Mai verwendet +1,6 dB, gerundet aus der Kalibrierung von 1,57 dB, die auf der [Website der Autoren](https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-station-compare-app/wspr-station-compare-add-on#h.jj74yhtflcn2) dokumentiert ist. Die [Kalibrierungsdemo für Februar](/de/demos/vanhamel_rx_calibration/) ergibt einen Mittelwert von +1,2 dB und stimmt damit mit dem Text der Publikation überein. Mit +1,2 dB lägen hier alle Differenzen um 0,4 dB höher; der Sprung von 3 dB bliebe jedoch unverändert.

† **Hinweis zur Rekonstruktion:** Die beiden Mediane teilen die rekonstruierten Beobachtungen an der Grenze aus Abbildung 6: die ersten 750 Joint Spots und die verbleibenden 691. Diese Grenze dient der Rekonstruktion; sie ist kein unabhängig protokollierter Zeitpunkt der Antennendrehung.
