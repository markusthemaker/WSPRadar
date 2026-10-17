<!-- section: hero -->
# Kurze Portabel-Vertikalantenne gegen größere Vertikalantenne

### Wie viel Signal kostet dich eine kleinere Antenne?

Zwei Sendeantennen, dieselben entfernten Empfänger: Vergleiche mit WSPRadar ihre Signale, erkenne, wo sich der Unterschied verändert, und prüfe die Beobachtungen hinter dem Ergebnis.

<!-- section: setup -->
## Was wollten die Funkamateure untersuchen?

**Kann eine kurze Portabel-Vertikalantenne auf denselben Funkwegen mit einer größeren Antenne mithalten?**

Im Experiment von Prof. Jens Zander wurden zwei Sendeantennen auf Gotland in Schweden verglichen. Jede Antenne war an einen WSPR-Sender mit 200 mW angeschlossen. Beide Baken waren so konfiguriert, dass sie auf 20 m während derselben zweiminütigen Zyklen sendeten.

**SK0WE/P — Target:** eine **Difona HF-P1**, eine 2,5 m lange Portabel-Vertikalantenne mit mittiger Verlängerungsspule und vier Radials.

**SK0WE/1 — Referenz:** eine **Hy-Gain AV620**, die größere Vertikalantenne für den Vergleich.

Diesmal **senden** die Antennen. Die Stationen, die ihre Signale melden, sind die weltweit verteilten entfernten Empfänger.

WSPRadar sucht nach Situationen, in denen **dieselbe Empfangsstation beide Sender im selben zweiminütigen WSPR-Zyklus meldet**. Jeder dieser gepaarten Vergleiche ist ein **Joint Spot**. Durch den Vergleich beim selben Empfänger zur selben Zeit werden Reports aus unterschiedlichen Empfangsaufbauten oder verschiedenen Tageszeiten nicht vermischt.

Verglichen wird das Signal-Rausch-Verhältnis, kurz SNR: Es beschreibt, wie stark sich ein Signal vom Rauschen abhebt. Ein höheres SNR ist besser. Für diese Demo gilt:

**ΔSNR = SNR von SK0WE/P − SNR von SK0WE/1**

Positive Werte fallen zugunsten der kurzen Difona-Vertikalantenne aus, negative zugunsten der größeren Hy-Gain-Vertikalantenne. Null bedeutet, dass beide Signale in diesem Vergleich dasselbe SNR haben.

**Unsere Frage lautet: Wie groß war der von den Empfängern beobachtete Unterschied, und war er auf jedem Funkweg gleich?**

<!-- section: step-1 -->
## Die Demo laden und ihre Einstellungen prüfen

Wähle oben **In WSPRadar App starten**, um die vorbereitete Demo **Kurze Portabel-Vertikalantenne gegen größere Vertikalantenne** zu öffnen.

Du musst das Experiment nicht von Hand eingeben. Prüfe die Einstellungen, um zu verstehen, was die Analyse umfasst:

| Einstellung | Wert in dieser Demo | Bedeutung |
|---|---|---|
| Analyse | TX-Benchmark | Vergleichen, wie zwei Sendeaufbauten gehört wurden. |
| Target | SK0WE/P, QTH JO97 | Die untersuchte kurze Portabel-Vertikalantenne. |
| Referenz | SK0WE/1, QTH JO97 | Die größere Vertikalantenne für den Vergleich. |
| Benchmark-Design | Referenzaufbau/-station | Gleichzeitige Aussendungen dieser beiden Aufbauten vergleichen. |
| Band | 20 m | Empfangsreports dieses Bands verwenden. |
| UTC-Zeitfenster | 21. Mai 2022, 09:45 → 10:30 | Das vorbereitete Zeitfenster von 45 Minuten untersuchen. |
| Referenzseitige SNR-Korrektur | Keine; 0,0 dB | Es wird kein zusätzlicher Referenzversatz angewendet. |

Die Übersicht umfasst Empfänger im Umkreis von **10 000 km** und verlangt **mindestens einen Joint Spot pro beitragender Station**. Einige Funkwege haben deshalb nur wenige Vergleiche; wir prüfen ihre Anzahl im weiteren Verlauf.

Beginne mit der Auswahl **Gesamter Bereich | Alle Richtungen**.

<!-- section: step-2 -->
## Die Karte lesen: Ist der Unterschied überall gleich?

Der Mittelpunkt der Azimutkarte ist das Target SK0WE/P. Die Sektoren stehen für Richtungen von der sendenden Station aus; die Ringe unterteilen die Entfernung. **Die Stationsmarkierungen sind entfernte Empfänger.**

Jeder beitragende Empfänger liefert seinen eigenen Median der SNR-Differenz. Anschließend bildet WSPRadar den Median dieser Empfängermediane. Ein Empfänger, der häufiger Reports liefert, dominiert den Sektor daher nicht allein deshalb, weil er mehr Beobachtungen beiträgt.

Lies die Zahlenwerte der Farbskala ab. Negative Werte fallen zugunsten der größeren Referenz-Vertikalantenne aus. Hier ist jeder gefärbte Sektor negativ – die Größe des Unterschieds variiert jedoch.

Vergleiche mit dem **Segment-Inspektor** diese Beispiele:

| Geografischer Bereich | Stationsgleichgewichteter Median ΔSNR | Empfangende Stationseinträge | Joint Spots |
|---|---:|---:|---:|
| 0–2 500 km, SSW | −10,0 dB | 7 | 41 |
| 0–2 500 km, WSW | −4,0 dB | 14 | 74 |
| 5 000–10 000 km, WNW | −4,0 dB | 3 | 10 |

Der Nachteil der kurzen Vertikalantenne ist auf den erfassten südsüdwestlichen europäischen Funkwegen größer als in Richtung westsüdwestliches Europa oder Nordamerika. Der nordamerikanische Vergleich beruht außerdem auf weniger Empfängern und Beobachtungen.

**Einen weit entfernten Empfänger zu erreichen, ist nicht dasselbe, wie das SNR der anderen Antenne zu erreichen.** Die kurze Vertikalantenne erreichte Nordamerika, doch die gepaarten Reports fallen auf diesen Funkwegen insgesamt weiterhin zugunsten der größeren Vertikalantenne aus.

Ungefärbte Sektoren haben keinen Vergleich, der die Anforderungen erfüllt, d. h. eine Empfangsstation, die sowohl SK0WE/P als auch SK0WE/1 im selben WSPR-Zyklus gehört hat. Sie belegen nicht, dass eine der Antennen in diesen Richtungen nichts abstrahlt.

Kehre im Segment-Inspektor zu **Gesamter Bereich | Alle Richtungen** zurück, bevor du fortfährst.

<!-- section: step-3 -->
## Benchmark-Evidenz lesen: Wie groß ist der Unterschied?

### Welche Signale lieferten einen Vergleich?

In **Decode Outcomes** beziehen sich die schraffierten Balken auf Stationseinträge, die gefüllten Balken auf Beobachtungen.

**37 von 85 empfangenden Stationseinträgen – etwa 44 % – lieferten Joint Spots.** Zusammen trugen sie **166 gepaarte Vergleiche** bei, ungefähr **36 % der berücksichtigten Beobachtungen**. Auf diesen Vergleichen beruhen die SNR-Ergebnisse.

Weitere **47 Einträge meldeten nur die größere Vertikalantenne**, während **ein Eintrag nur die kurze Vertikalantenne meldete**. Ein Stationseintrag bezeichnet ein Rufzeichen zusammen mit seinem gemeldeten Locator.

**Eine mögliche Erklärung ist, dass das Signal der kurzen Vertikalantenne an einigen Empfängern zu schwach für eine erfolgreiche WSPR-Dekodierung war**, während das Signal der größeren Vertikalantenne in denselben Zyklen dekodiert wurde. Dadurch käme an diesen Empfängern kein Joint Spot zustande. Die fehlenden Reports allein können diese Erklärung nicht bestätigen; auch Störungen oder Lücken beim Empfang und bei der Übermittlung von Reports könnten dazu beitragen.

Der Beobachtungsbalken **Beide (Async)** enthält ungepaarte Reports von Empfängern, die zu anderen Zeiten Joint Spots lieferten. Ein Empfänger kann deshalb in der Stationskategorie Joint erscheinen, ohne dass jeder seiner Reports ein Paar bildet. Die Bezeichnung weist nicht zwangsläufig auf ein Problem mit der Uhrzeitsynchronisation hin.

Für die Auswertung heißt das: **SNR-Differenzen beschreiben die gepaarten Signale, nicht alle Empfangsreports.**

### Was sagt uns der Unterschied zwischen den Medianen?

**Die beiden Zusammenfassungen stimmen darin überein, welche Antenne vorn lag, beschreiben aber einen unterschiedlich großen typischen Vorteil.** Hier entspricht der Median der Empfängerergebnisse einem Vorteil von **5 dB** für die größere Vertikalantenne, während der Median der einzelnen Vergleiche einem Vorteil von **7 dB** entspricht. Dies sind zwei Sichtweisen auf dasselbe Experiment – kein Unsicherheitsbereich, innerhalb dessen der „wahre“ Vorteil liegen muss.

Um den Unterschied zu untersuchen, öffne **Station Insights** und vergleiche **Joint Spots** mit **Median ΔSNR**. Zum Beispiel trägt **ON5KQ 11 gepaarte Beobachtungen mit einem Median von −7 dB** bei, während **SWLEI1763 nur eine beiträgt, mit −1 dB**. Beide tragen einen Wert zu den Stationsmedianen bei, zum Joint-Spot-Panel jedoch elf Beobachtungen gegenüber einer.

Ein stärker negativer Joint-Spot-Median **kann auftreten, wenn wiederholt beobachtete Funkwege einen größeren Nachteil zeigen**. Allerdings spielt auch die Streuung der Beobachtungen innerhalb jedes Empfängers eine Rolle: Der Abstand allein beweist nicht, dass die Empfänger mit den meisten Reports ihn verursacht haben.

### Welches Ergebnis sollte ich verwenden?

Nutze **Stationsmediane** für die Frage: **„Wie schnitten die Antennen über die Empfangsstationen hinweg ab, wenn jede Station gleich gewichtet wird?“** Nutze **Joint-Spot ΔSNR** für: **„Wie groß war der typische Unterschied über alle gepaarten Beobachtungen hinweg?“**

Keines der beiden Ergebnisse ist automatisch genauer. Die Gleichgewichtung der Stationen verhindert, dass häufig meldende Empfänger dominieren; aber auch ein Empfänger mit nur einem Vergleich trägt einen Stationsmedian bei. Prüfe die Anzahlen zusammen mit dem Ergebnis.

Nutze für deine eigenen Vergleiche diese Lesehilfe:

| Wenn die Mediane … | So lassen sie sich interpretieren |
|---|---|
| **Nahe beieinanderliegen und denselben Aufbau bevorzugen** | Die Zusammenfassungen auf Stations- und Beobachtungsebene erzählen eine ähnliche Geschichte. Prüfe dennoch die Abdeckung und die Unterschiede zwischen den Funkwegen. |
| **Sich unterscheiden, aber denselben Aufbau bevorzugen** | Beide Zusammenfassungen zeigen denselben Spitzenreiter, aber der typische Vorteil hängt davon ab, wie die Evidenz zusammengefasst wird. Untersuche Report-Anzahlen, Richtungen und Zeiträume. |
| **Unterschiedliche Aufbauten bevorzugen** | Die übergreifende Schlussfolgerung hängt von der gewählten Zusammenfassung ab. Untersuche, welche Funkwege und Zeiträume jeweils für welchen Aufbau sprechen, bevor du einen Gesamtsieger benennst. |

**In dieser Demo kehrt die Wahl der Zusammenfassung die Schlussfolgerung nicht um:** Beide Mediane fallen zugunsten der größeren Vertikalantenne aus, und alle 37 Empfängermediane sind negativ. Stelle den **stationsgleichgewichteten Vorteil von 5 dB** in den Vordergrund und behalte den **Vorteil von 7 dB auf Beobachtungsebene** als ergänzende Information bei.

<!-- section: step-3-publication -->
## WSPRadar anhand veröffentlichter Forschung überprüfen

Eine Möglichkeit, WSPRadar zu prüfen, besteht darin, ein veröffentlichtes Experiment erneut zu betrachten und dessen Ergebnisse aus historischen WSPR-Beobachtungen zu rekonstruieren.

Hier zeigen **die ursprüngliche Abbildung 4, die Rekonstruktion und das Joint-Spot-Histogramm von WSPRadar dieselbe Verteilung in ihren Grundzügen**. Die 166 gepaarten Vergleiche ergeben eine **mittlere Differenz von −6,8 dB** und eine **Standardabweichung von 3,5 dB**. Damit stimmen sie mit der veröffentlichten Abbildung in der dort angegebenen Genauigkeit überein. Die Standardabweichung beschreibt die Streuung der einzelnen Vergleiche.\*

[**Die ursprüngliche Abbildung 4, die Rekonstruktion und den WSPRadar-Vergleich ansehen (PDF) ↗**](app/static/reference_figures/zander_fig4_paper_v1/WSPRadar_Demo_Zander_Figure4.pdf)

<!-- section: step-4 -->
## Zeitliche Evidenz lesen: Blieb der Vorteil bestehen?

### Linkes Panel: den Beobachtungen im Zeitverlauf folgen

In **Δ SNR im Zeitverlauf** zeigt jede kreisförmige Markierung den Median der Differenz für ein **10-Minuten-Intervall**.

Die vier Intervalle mit Beobachtungen haben Mediane von **−8, −6, −8 und −4 dB**. Die Referenz-Vertikalantenne liegt in all diesen Intervallzusammenfassungen vorn, nicht nur an einem einzigen Punkt des Tests.

Das Ergebnis variiert dennoch. Bevor du den weniger negativen letzten Punkt als Verbesserung der kurzen Antenne wertest, prüfe, wie viele Beobachtungen ihn stützen.

Die gestrichelte Linie zeigt den **Gesamtmedian der Joint Spots von −7 dB**. Das schattierte Band umfasst die mittleren 50 % der Beobachtungen jedes Intervalls: Es zeigt die Streuung, kein Konfidenzintervall. Die Hintergrundfarben zeigen, wo sich Beobachtungen konzentrieren, nicht welche Antenne besser ist. Lies die beschrifteten dB-Werte ab – die senkrechte Skala ist nichtlinear.

### Rechtes Panel: Warum gibt es kein UTC-Stundenprofil?

Im Panel steht **„UTC-Stundenmuster nicht verfügbar.“** Dieser Lauf enthält Beobachtungen von nur einem Datum; WSPRadar benötigt für diese Ansicht Evidenz von mindestens zwei UTC-Daten.

Das ist für dieses Beispiel angemessen: Ein kurzer Test an einem einzigen Vormittag kann kein wiederkehrendes Tagesmuster belegen. Fahre mit der chronologischen Evidenz fort.

<!-- section: step-5 -->
## Die zeitliche Evidenzabdeckung prüfen: Worauf beruht das Muster?

Das SNR-Diagramm zeigt die Differenzen. Die **Zeitliche Evidenzabdeckung** zeigt, welche Beobachtungen sie stützen.

Das obere Panel betrifft Empfangsstationen, das untere **Empfängerzyklen** – einen Empfänger in einem WSPR-Zyklus. Grün steht für Joint-Evidenz, Violett für Beobachtungen nur beim Target und die ungefüllten Anteile für Beobachtungen nur bei der Referenz.

Lies das untere Panel zusammen mit dem SNR-Diagramm:

| UTC-Intervall | Joint Spots | Median ΔSNR |
|---|---:|---:|
| 09:45–09:55 | 8 | −8 dB |
| 09:55–10:05 | 70 | −6 dB |
| 10:05–10:15 | 76 | −8 dB |
| 10:15–10:25 | 12 | −4 dB |

Die beiden mittleren Intervalle liefern **146 der 166 Vergleiche**. Der letzte Punkt bei −4 dB beruht auf **12 Vergleichen, alle aus dem Zyklus um 10:16 UTC**. Er belegt nicht, dass die kurze Antenne dieses Ergebnis zehn Minuten lang aufrechterhielt.

Die Linien zum **Joint-Evidenzanteil** zeigen, welcher Anteil der berücksichtigten Evidenz verwertbare Paare bildet. Die stationsgleichgewichtete Linie gewichtet Empfänger gleich, die Linie auf Outcome-Ebene Empfängerzyklen. **Keine der beiden Linien zeigt eine Sendeerfolgsrate oder einen „Anteil gewonnener Vergleiche“.**

Beachte auch den Hinweis unter der Abbildung: Zyklen ohne Beleg dafür, dass SK0WE/P in Betrieb war, werden ausgeschlossen. Die Betriebszeit des Referenzsenders wird durch diese Regel nicht unabhängig festgestellt. Die einseitigen Empfangsergebnisse liefern deshalb Kontext, sind aber keine symmetrische Erfolgsbilanz.

**Prüfe die Anzahl der Beobachtungen hinter einem auffälligen Wert – nicht nur seine Höhe oder seinen Prozentanteil.**

<!-- section: step-6 -->
## Station Insights öffnen: Was beobachtete ein einzelner Empfänger?

Mit der Tabelle **Station Insights** gelangst du vom übergreifenden Vergleich zu einer einzelnen Empfangsstation.

Wähle **ON5KQ mit Locator JO10os**, den Empfänger in den folgenden Abbildungen. Er liegt etwa **1 267 km** vom Target entfernt, bei einem Azimut von **241°**.

Seine **11 Joint Spots** ergeben einen Median ΔSNR von **−7 dB**. Alle elf Vergleiche fallen zugunsten der größeren Vertikalantenne aus; die Differenzen reichen von **−12 bis −6 dB**.

### Warum zeigt das Diagramm nur eine Medianmarkierung?

Die Ansicht der ausgewählten Station verwendet **Ein-Stunden-Intervalle**, die länger sind als dieses gesamte Testfenster. Die einzelne Markierung fasst deshalb alle elf gepaarten Beobachtungen zusammen. Sie bedeutet **nicht**, dass die SNR-Differenz während des gesamten Tests konstant blieb.

Diese Unterscheidung ist hilfreich: Die Anzahl der Markierungen hängt von der zeitlichen Gruppierung ab, während die Beobachtungsanzahl zeigt, wie viele Daten jede Markierung zusammenfasst.


<!-- section: step-6-coverage -->
## Evidenzabdeckung des ausgewählten Funkwegs: ON5KQ

Der **Joint-Evidenzanteil beträgt ungefähr 85 %**. Hier bedeutet das, dass 11 der 13 berücksichtigten Empfängerzyklen ein Paar lieferten – nicht, dass eine der Antennen in 85 % der Fälle „gewonnen“ hätte.

Die beiden Beobachtungen nur beim Target widersprechen den negativen gepaarten SNR-Differenzen nicht. Sie entstanden, als nur das Signal der kurzen Antenne gemeldet wurde. Für diese Zyklen lässt sich deshalb keine gepaarte Differenz berechnen.

<!-- section: step-7 -->
## Drill-Down nutzen: einen einzelnen Vergleich prüfen

**Drill-Down** legt die Beobachtungen hinter den Zusammenfassungen offen. Wähle ON5KQ aus und prüfe die Uhrzeit sowie die beiden SNR-Spalten.

Die exportierten Zeilen enthalten zum Beispiel:

| UTC-Zeit am 21. Mai | SNR von SK0WE/P | SNR von SK0WE/1 | ΔSNR |
|---|---:|---:|---:|
| 09:54 | −13 dB | −1 dB | −12 dB |
| 09:56 | −13 dB | −6 dB | −7 dB |
| 10:02 | −11 dB | −5 dB | −6 dB |
| 10:10 | −14 dB | −4 dB | −10 dB |
| 10:12 | −5 dB | +1 dB | −6 dB |

Um 09:54 gilt: **−13 − (−1) = −12 dB**. Das Signal der größeren Vertikalantenne hatte bei ON5KQ das höhere SNR, aber **beide Signale wurden dekodiert**. Ein negatives ΔSNR bedeutet einen relativen Nachteil, keinen fehlgeschlagenen Empfang.

Die Differenzen ändern sich von einem Zyklus zum nächsten, obwohl das Diagramm der ausgewählten Station sie mit einer einzigen Medianmarkierung zusammenfasst.

Dies sind die von WSPRadar exportierten SNR-Werte. Die Spalte ΔSNR zieht den Referenzwert vom Target-Wert ab; in diesem Lauf wird keine zusätzliche Referenzkorrektur angewendet.

Du musst nicht jede Zeile durchsehen. Nutze Drill-Down, um die Rechnung zu überprüfen, eine ungewöhnliche Beobachtung zu verstehen oder die Beiträge zu einer Zusammenfassung nachzuvollziehen.

<!-- section: step-8 -->
## Das Ergebnis festhalten und sichern

> **In diesem Experiment auf 20 m übertraf die größere Hy-Gain AV620 die kurze Difona-Vertikalantenne auf den gepaart verglichenen Empfangswegen. Die 166 Vergleiche aus jeweils demselben WSPR-Zyklus von 37 empfangenden Stationseinträgen ergeben einen stationsgleichgewichteten Median ΔSNR von −5 dB und einen Joint-Spot-Median von −7 dB. Jeder beitragende Empfänger hat einen negativen Median, doch die Größe des Unterschieds variiert mit der Richtung und von einem Vergleich zum nächsten.**

Die kurze Vertikalantenne erreichte dennoch weit entfernte Empfänger, auch in Nordamerika. **Gehört zu werden und das SNR einer größeren Antenne zu erreichen, sind unterschiedliche Fragen – und mit WSPRadar kannst du beide untersuchen.**

Dieses Ergebnis beschreibt diese installierten Sendeaufbauten während des ausgewählten Tests. Es ist weder ein fester Nachteil jeder Portabel-Vertikalantenne noch eine Messung des Antennengewinns in jeder Richtung.

Speichere das Ergebnispaket, um die Einstellungen, Abbildungen und verarbeiteten Beobachtungen zu sichern. Halte bei eigenen Experimenten die Antennen, die Sendeleistung und die Installationsdetails zusammen mit den Ergebnissen fest.

Du hast nun entfernte WSPR-Empfänger genutzt, um zwei Sendeantennen zu vergleichen – von der Karte und dem Gesamtunterschied über den Zeitverlauf und eine einzelne Empfangsstation bis zu einem einzelnen Report-Paar.

---

\* **Hinweis zur Abbildung:** Die ursprüngliche Abbildung verwendet gröbere Histogrammklassen und eine Wahrscheinlichkeitsdichteskala; WSPRadar verwendet feinere 1-dB-Klassen und Prozentanteile. Das Vergleichs-PDF erläutert die unterschiedlichen Darstellungen. Der rekonstruierte Mittelwert und die Stichprobenstandardabweichung betragen −6,78 dB und 3,51 dB. Gerundet ergeben sie die veröffentlichten Werte −6,8 dB und 3,5 dB.
