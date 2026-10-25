<!-- section: hero -->

# #1 Niedriger Dipol gegen Vertikalantenne ohne Radials

Ein niedriger Dipol im Vergleich mit einer Vertikalantenne auf 40 m — ein Praxisvergleich mit WSPR-Daten.

<!-- section: setup -->

## Was untersuchten die Funkamateure?

In *Improving HF Band SNR*, veröffentlicht im Oktober 2017 in *Practical Wireless*, untersuchten Gwyn Griffiths, G3ZIL, und Nigel Squibb, G4HZX, Möglichkeiten zur Verbesserung des Empfangs auf 40 Metern. Beide verwendeten im Wesentlichen denselben Entwurf eines selbstgebauten Direktmischempfängers, allerdings an unterschiedlichen Standorten und mit unterschiedlichen Antennen. [Originalpublikation](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf)

**G3ZIL — IO90HW:** Ein niedrig aufgehängter horizontaler Dipol, dessen Mitte sich in etwa 4 Metern Höhe und dessen Enden sich in 1,5 Metern Höhe befanden. Der Empfänger war in einen Gartenschuppen verlegt worden.

**G4HZX — IO91:** Eine Hustler-5-BTV-Vertikalantenne, die am hinteren Ende des Gartens ohne Radiale an einen Erdspieß angeschlossen war.

Der Artikel dokumentiert außerdem eine erneute Abstimmung des Dipols von G3ZIL am **8. April**. Untersucht wurden tatsächlich installierte Stationen, kein unveränderter Laboraufbau.

**Unsere Frage lautet: Wie schnitten diese beiden Empfangsstationen im April 2017 im Vergleich ab?**

Jede Station lud Meldungen zu den von ihr dekodierten WSPR-Signalen hoch. WSPRadar ermittelt die Fälle, in denen beide Stationen **denselben Sender im selben zweiminütigen WSPR-Zyklus** meldeten. Ein **Joint Spot** entsteht, wenn beide Empfänger denselben Sender im selben zweiminütigen WSPR-Zyklus melden, sodass wir ihre SNR-Werte zur selben Zeit vergleichen können. Durch den Vergleich derselben Aussendung wird vermieden, den Empfang der einen Station an einem günstigen Nachmittag mit dem Empfang der anderen Station zu einer anderen Zeit oder sogar an einem anderen Tag zu vergleichen.

Die verglichene Größe ist das **Signal-Rausch-Verhältnis, kurz SNR**: wie stark sich das Signal gegenüber dem Rauschen abhebt. Ein höheres SNR ist besser. Für diese Demo gilt:

**ΔSNR = SNR von G3ZIL − SNR von G4HZX**

Eine positive Differenz spricht für G3ZIL, eine negative Differenz für G4HZX. Null bedeutet in diesem Vergleich ein gleiches SNR.

<!-- section: load -->

## Laden Sie die Demo und prüfen Sie ihre Einstellungen

Wählen Sie **In WSPRadar App starten** (oben), um **Demo #1: Low Dipole vs Radial-Free Vertical** mit den vorbereiteten Einstellungen zu öffnen und die RX-Analyse automatisch zu starten.

Sie müssen nichts manuell eingeben. Die Einstellungen erläutern, was in die Analyse eingeht:

| Einstellung | Wert in dieser Demo | Bedeutung |
|---|---|---|
| Analyse | **RX Benchmark** | Vergleich des Empfangs statt der Aussendung oder einer eigenständigen Performance-Analyse. |
| Zielstation | **G3ZIL**, QTH **IO90HW** | Die untersuchte Station und der Mittelpunkt der Karte. |
| Referenzstation | **G4HZX**, gemeldeter Locator **IO91** | Die zum Vergleich verwendete Empfangsstation. |
| Benchmark-Design | **Reference Setup/Station** | Vergleich mit dieser bestimmten Station, nicht mit einer Referenz aus der Nachbarschaft. |
| Band | **40 m** | Meldungen aus diesem Band verwenden. |
| UTC-Zeitfenster | **1. April 2017, 00:00 → 1. Mai 2017, 00:00** | Untersuchung der Beobachtungen aus dem April. |

<!-- section: map -->

## Lesen Sie die Karte: Ist der Vorteil weit verbreitet?

Die Karte ist auf die Zielstation G3ZIL zentriert. Die Kompasssektoren stellen die Richtungen von dieser Station aus dar; die Ringe trennen Entfernungsbereiche. Dies wird als [Azimutalkarte](https://en.wikipedia.org/wiki/Azimuthal_equidistant_projection) bezeichnet und ist im Amateurfunk weit verbreitet.

Die **Sektorfarben zeigen den stationsbalancierten Median von ΔSNR** in dB. Jeder beitragende Sender liefert seinen eigenen Median der Differenz; anschließend nimmt WSPRadar den mittleren Wert dieser Stationsmediane. Ein häufig gehörter Sender dominiert die Karte deshalb nicht allein dadurch, dass er mehr Meldungen liefert.

Lesen Sie die numerische Farbskala: Positive Werte sprechen für G3ZIL, negative Werte für G4HZX. Ungefärbte Sektoren enthalten keinen Vergleich, der die Auswahlkriterien erfüllt; sie stehen nicht für eine gemessene Differenz von null.

**Der erste sichtbare Befund ist, dass der Vorteil von G3ZIL geografisch nicht gleichmäßig verteilt ist.** Viele nähere europäische Sektoren sprechen deutlich für G3ZIL, während der entfernte westnordwestliche Sektor mit vielen nordamerikanischen Stationen wesentlich näher an einem Gleichstand liegt.

Verwenden Sie den **Segment Inspector**, um genauer hinzusehen. Die exportierten Stationseinträge ergeben beispielsweise:

| Geografischer Bereich | Stationsbalancierter Median von ΔSNR | Beitragende Stationseinträge |
|---|---:|---:|
| **0–2 500 km, E** | **+8,0 dB** | **172** |
| **5 000–10 000 km, WNW** | **0,0 dB** | **113** |



**Das ist bereits ein nützliches Ergebnis:** Ein Gesamtvorteil würde nicht bedeuten, dass G3ZIL jede Richtung besser hörte. Die Karte hilft, einen Vorteil auf bestimmten Ausbreitungswegen von einem Vorteil im gesamten beobachteten Gebiet zu unterscheiden.

Die Stationsmarkierungen vermitteln eine andere Information als die Sektorfarben: Sie zeigen, ob ein Sender gemeinsam oder nur in anderen Empfangskategorien gemeldet wurde. Diese Kategorien untersuchen wir als Nächstes.

Stellen Sie den Segment Inspector vor dem Fortfahren wieder auf **Full Range | All Directions**, damit die nachfolgenden Zahlen übereinstimmen.

<!-- section: difference -->

## Lesen Sie Benchmark Evidence: Wie groß ist der Unterschied?

Dieser Abschnitt betrachtet das Segment, das Sie untersuchen möchten, hier Full Range | All Directions. Er verbindet **die Frage, welche Signale dekodiert wurden**, mit **der SNR-Differenz in den Fällen, in denen beide Empfänger sie dekodierten**.

#### Welche Signale lieferten einen Vergleich?

In **Decode Outcomes** zählen die gestreiften Balken Stationseinträge; die ausgefüllten Balken zählen Beobachtungen.

In diesem Lauf lieferten **792 Stationseinträge — etwa 70 % — mindestens einen Joint Spot**. Zusammen lieferten sie **57 767 gepaarte Vergleiche**, ungefähr **46 % der berücksichtigten Beobachtungen**. Auf diesen Vergleichen beruhen die ΔSNR-Ergebnisse.

Die übrigen Stationskategorien ergänzen den Kontext: **258 Einträge erschienen nur bei G3ZIL**, **47 nur bei G4HZX** und **33 bei beiden, jedoch ohne ein Paar aus demselben Zyklus**. Ein Stationseintrag bezeichnet hier ein Rufzeichen zusammen mit dem gemeldeten Locator.

Eine Bezeichnung erfordert besondere Aufmerksamkeit: **Both (Async)**. Bei den Stationsbalken bedeutet sie, dass beide Empfänger diesen Sender meldeten, jedoch nie gemeinsam in einem Zyklus, der die Auswahlkriterien erfüllt. Bei den Beobachtungsbalken umfasst sie außerdem ungepaarte Meldungen von Sendern, die zu anderen Zeiten Joint Spots lieferten. Sie bedeutet **nicht**, dass die Uhren der Empfänger zwangsläufig falsch gingen. Die [exportierten Beobachtungen](/assets/demos/griffiths_squibb_fig3/export/benchmark/table_drilldown_all_stations_current_segment.csv) und die Aggregationsregeln unterscheiden diese beiden Ebenen.

Die praktische Aussage ist einfach: **SNR-Differenzen beschreiben die gepaarten Signale, nicht alles, was eine der beiden Stationen hörte.** Betrachten Sie die Empfangsergebnisse zusammen mit dem SNR-Ergebnis.

#### Wie groß ist der typische SNR-Vorteil?

Die beiden anderen Teilgrafiken fassen die gepaarten Beobachtungen auf unterschiedliche Weise zusammen:

**Station Medians: +6,5 dB.** Jeder Sender trägt einen Median der Differenz bei, unabhängig davon, wie oft er gehört wurde. Die meisten Stationsmediane sind positiv, einige sprechen jedoch für G4HZX.

**Joint-Spot ΔSNR: +7,0 dB.** Jeder gepaarte Vergleich geht ein. Häufiger gehörte Sender haben daher einen größeren Einfluss.

Ein *Median* ist der mittlere Wert, wenn die Werte der Größe nach geordnet werden. Hier liegen die beiden Mediane nahe beieinander und sind beide klar positiv: Das typische Stationsergebnis und der typische Einzelvergleich ergeben ein miteinander vereinbares Bild.

**Unsere erste Gesamtaussage: G3ZIL hatte in den gepaarten Beobachtungen aus dem April einen deutlichen SNR-Vorteil.** Die Karte hat bereits gezeigt, wo diese Aussage eingeschränkt werden muss. Prüfen Sie als Nächstes, ob der Vorteil während des gesamten Monats gleich blieb.

<!-- section: time -->

## Lesen Sie Temporal Evidence: Hat sich der Unterschied verändert?

#### Linke Teilgrafik: Verfolgen Sie den Monatsverlauf

In **Δ SNR over Time** stellt jede kreisförmige Markierung den Median eines Tages dar.

Das Ergebnis verändert sich erheblich: Der Tagesmedian steigt von **+2 dB am 1. April** auf **+9 dB am 15. April**, mit Schwankungen während dieses Zeitraums. Im späteren Monatsverlauf liegt er überwiegend zwischen **+6 und +8 dB**.

**Der Vorteil war nicht lediglich ein fester Versatz zwischen zwei Empfängern.** Seine Größe änderte sich im Beobachtungszeitraum — etwas, das der einzelne Monatsmedian nicht zeigen kann.

Die Autoren schlugen trocknenden Boden als Erklärung für den Trend in der ersten Monatshälfte vor. Der Export enthält keine Bodenfeuchtemessungen; diese Anleitung zeigt daher die Veränderung der SNR-Differenz und stellt keine Prüfung dieser Erklärung dar. [Originalpublikation ↗](https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf)

**Weltraumwetter-Kontext:** Interessanterweise fallen die spärlichen ΔSNR-Beobachtungen am **20. April 2017** mit einem dokumentierten **geomagnetischen Sturm der Stufe G2 (mäßig)** zusammen. NOAA meldete G2-Bedingungen um **04:33 UTC**, verursacht durch einen schnellen Sonnenwindstrom aus einem koronalen Loch. Solche Störungen können die Kurzwellenausbreitung beeinflussen und könnten zu der geringeren Datengrundlage beigetragen haben. Dieses zeitliche Zusammentreffen belegt jedoch keinen ursächlichen Zusammenhang, insbesondere da am 22.–23. April noch stärkere tägliche geomagnetische Störungen auftraten.

[**NOAAs ursprünglichen Sturmbericht vom 20. April 2017 lesen ↗**](https://www.spaceweather.gov/news/g2-moderate-geomagnetic-storm-conditions-met)

Einige Darstellungsdetails helfen, das Diagramm korrekt zu lesen. Die gestrichelte Linie ist der übergreifende **Joint-Spot-Median von +7 dB**. Das schattierte Band enthält die mittleren 50 % der Beobachtungen in jedem Zeitintervall; es zeigt die Streuung, kein Konfidenzintervall. Die Hintergrundfarben zeigen, wo sich Beobachtungen konzentrieren, nicht welcher Empfänger besser ist. Lesen Sie die beschrifteten dB-Werte — die vertikale Skala ist nichtlinear.

#### Rechte Teilgrafik: Vergleichen Sie die Tagesstunden

**Δ SNR by UTC Hour** fasst Beobachtungen aus derselben UTC-Stunde über den gesamten April zusammen.

Der SNR-Vorteil von G3ZIL nimmt in der ersten Aprilhälfte zu und variiert stark mit der Tageszeit. Die Ansicht nach UTC-Stunde zeigt ungefähr **+7 bis +8 dB tagsüber**, nach Mitternacht sinkt der Vorteil auf **+1 bis +2 dB**. Dies ist mit wechselnden Ausbreitungsbedingungen auf 40 m vereinbar: Der niedrige Dipol begünstigt europäische Funkwege mit höheren Einfallswinkeln, während die Vertikalantenne besser für flachere Einfallswinkel und nächtlichen Fernempfang geeignet ist — wie auch in der Originalstudie beobachtet (Abbildung 6).

<!-- section: published-figure3 -->

## WSPRadar anhand veröffentlichter Forschung überprüfen

**Wie überprüfen wir die Ergebnisse von WSPRadar?** Ein Ansatz besteht darin, veröffentlichte WSPR-Experimente erneut zu untersuchen, ihre Abbildungen aus historischen Beobachtungen zu rekonstruieren und die Ergebnisse zu vergleichen. So können wir unsere Berechnungen validieren, Abweichungen untersuchen und Funkamateuren dieselben leistungsfähigen Analysemöglichkeiten zugänglich machen.

Hier vergleichen wir **die ursprüngliche Abbildung 3 von Griffiths und Squibb**, unsere Rekonstruktion und **die zeitliche Analyse von WSPRadar**. Das ursprüngliche Punktdiagramm enthält viele überlappende Beobachtungen. Unsere Rekonstruktion ergänzt eine Dichtedarstellung, um sichtbar zu machen, wo sich Beobachtungen konzentrieren, während WSPRadar die Entwicklung der medianen SNR-Differenz und ihrer Variabilität hervorhebt. Alle drei Darstellungen zeigen den zunehmenden Vorteil von G3ZIL während der ersten Aprilhälfte.

Einige Details unterscheiden sich, weil mehrere Meldungen aus demselben Sendezyklus unterschiedlich kombiniert werden können. Wir dokumentieren und untersuchen diese Abweichungen, statt eine exakte Übereinstimmung zu erzwingen.

[**Ursprüngliche Abbildung 3, Rekonstruktion und WSPRadar-Vergleich (PDF, Seite 1) ↗**](/assets/demos/griffiths_fig3_paper_v1/WSPRadar_Demo_Griffiths_Figure3.pdf)

<!-- section: coverage -->

## Prüfen Sie Temporal Evidence Coverage: Welche Daten stützen das Muster?

Das SNR-Diagramm zeigt die Unterschiede. **Temporal Evidence Coverage** zeigt die Beobachtungen, auf denen sie beruhen.

Die oberen Teilgrafiken betreffen Sendestationen, die unteren deren Sender-Zyklen. Grün steht für gemeinsame Beobachtungen (Joint), Violett für Beobachtungen nur an der Zielstation (Target-only), und die ungefüllten Bereiche stehen für Beobachtungen nur an der Referenzstation (Reference-only).

**An jedem Tag dieses Laufs liegen gepaarte Beobachtungen von 70 bis 172 TX-Stationseinträgen vor**, jedoch nicht gleich viele: Die Tagessumme reicht von **860 Joint Spots am 20. April** bis zu **2 903 am 11. April**. Die geringere Datengrundlage am 20. April ist neben dem SNR-Ergebnis dieses Tages sichtbar.

**Weltraumwetter-Kontext:** Die geringe Zahl gemeinsamer Beobachtungen am **20. April 2017** fällt ebenfalls mit dem bereits erwähnten dokumentierten **geomagnetischen Sturm der Stufe G2 (mäßig)** zusammen.

Auch die Teilgrafiken nach UTC-Stunde zeigen, dass in den frühen Stunden weniger gepaarte Beobachtungen vorliegen als am späten Nachmittag und am Abend.

Die Linien **Joint Evidence Share** beschreiben, welcher Anteil der berücksichtigten Beobachtungen nutzbare Paare bildet. Die stationsbalancierte Linie gewichtet Stationen gleich; die Linie auf Ergebnisebene gewichtet Beobachtungen gleich. **Keine von beiden ist eine Erfolgsquote eines Empfängers oder ein „gewonnener Prozentsatz“.**

Beachten Sie außerdem: Zyklen ohne einen Beleg dafür, dass G3ZIL in Betrieb war, werden ausgeschlossen. Die Betriebszeit von G4HZX wird nicht unabhängig festgestellt, da WSPRadar nach der Aktivität des Targets filtert. Die einseitigen Empfangsergebnisse liefern deshalb nützlichen Kontext, stellen aber keine symmetrische Vergleichswertung dar.

Konzentrieren Sie sich beim ersten Lesen auf eine Gewohnheit: **Prüfen Sie, ob ein auffälliges SNR-Merkmal von vielen Vergleichen oder nur von wenigen gestützt wird.**

<!-- section: stations -->

## Öffnen Sie Station Insights: Stimmen einzelne Ausbreitungswege überein?

Die Tabelle **Station Insights** ermöglicht den Wechsel von einer breiten Zusammenfassung zu einem bestimmten Sender.

Wählen Sie **DJ0ABR bei JN68nt**, das in der Demo bereits vorbereitet ist. Die Station liegt etwa **1 064 km** von G3ZIL entfernt, bei einem Azimut von ungefähr **97°**.







**Selected Station Evidence** verfolgt nun einen einzelnen Ausbreitungsweg von einem Sender, statt Sender aus vielen Standorten zusammenzufassen.

Sein Gesamtmedian beträgt **+5 dB**, basierend auf **2 334 Joint Spots**. Die 12-Stunden-Mediane schwanken in Teilen der ersten Tage um null oder darunter und werden anschließend überwiegend positiver. Die grundlegende Veränderung vom früheren zum späteren Zeitraum zeigt sich daher sowohl auf diesem einzelnen Ausbreitungsweg als auch in der Ansicht aller Stationen.

Das Stundenprofil unterscheidet sich vom Profil aller Stationen. Das ist aufschlussreich: Eine Zusammenfassung vieler Ausbreitungswege muss nicht den Tagesverlauf jedes einzelnen Weges beschreiben.

#### Untersuchen Sie die auffällige Spitze

Am **20. April** gibt es einen Punkt bei **+25 dB**. Wurde die Station plötzlich für einen halben Tag erheblich besser?

Prüfen Sie die Datengrundlage des ausgewählten Ausbreitungswegs, bevor Sie diesen Schluss ziehen.







Im Zeitraum **20. April, 12:00–24:00 UTC** gibt es nur **einen Joint Spot**. Sein ΔSNR beträgt +25 dB und ist damit zugleich der Median dieses Zeitintervalls. Wie zuvor erläutert, meldete NOAA am selben Tag einen **geomagnetischen Sturm der Stufe G2 (mäßig)**, der die Kurzwellenausbreitung beeinflusst haben könnte.

Über den gesamten Monat weist dieser Ausbreitungsweg **2 334 Joint Spots**, **247 Beobachtungen ausschließlich bei G3ZIL** und **6 Beobachtungen ausschließlich bei G4HZX** auf. Insgesamt ist die gepaarte Datengrundlage umfangreich, auch wenn einzelne Zeitintervalle nur wenige Beobachtungen enthalten können.

<!-- section: drilldown -->

## Verwenden Sie Drill-Down: Prüfen Sie einen einzelnen Vergleich

**Drill-Down** legt die Beobachtungen hinter den Zusammenfassungen offen. Prüfen Sie bei ausgewähltem DJ0ABR die Zeit und die beiden SNR-Spalten.

Die exportierten Zeilen enthalten beispielsweise:

| UTC-Zeit | SNR von G3ZIL | SNR von G4HZX | ΔSNR |
|---|---:|---:|---:|
| **1. April, 06:14** | +1 dB | +6 dB | **−5 dB** |
| **1. April, 10:40** | −22 dB | −29 dB | **+7 dB** |
| **4. April, 11:58** | −16 dB | −16 dB | **0 dB** |
| **8. April, 11:48** | −13 dB | −25 dB | **+12 dB** |
| **12. April, 11:58** | −8 dB | −8 dB | **0 dB** |
| **16. April, 11:58** | −13 dB | −18 dB | **+5 dB** |
| **19. April, 12:00** | −5 dB | −20 dB | **+15 dB** |
| **20. April, 17:56** | −7 dB | −32 dB | **+25 dB** |
| **24. April, 11:58** | −23 dB | −23 dB | **0 dB** |
| **28. April, 11:58** | −10 dB | −14 dB | **+4 dB** |

Der erste Vergleich spricht für G4HZX. Der zweite spricht für G3ZIL: **−22 dB ist höher als −29 dB**.

Die Beobachtung vom **20. April, 17:56 UTC** fällt mit **+25 dB** auf: der Export weist −7 dB für G3ZIL und −32 dB für G4HZX aus. Sie ist die einzige gepaarte Beobachtung hinter dem auffälligen Punkt vom 20. April.

Diese SNR-Spalten verwenden WSPRadars gemeinsame **Bezugsbasis von 1 W gemeldeter Sendeleistung**, statt zwangsläufig das ursprünglich gemeldete SNR unverändert wiederzugeben. Die Spalte ΔSNR subtrahiert den Referenzwert vom Zielwert.

Sie müssen nicht Tausende von Zeilen untersuchen. Verwenden Sie Drill-Down, wenn Sie ein Beispiel überprüfen, einen überraschenden Punkt verstehen oder genau prüfen möchten, was in eine Zusammenfassung eingegangen ist.

<!-- section: takeaways -->

## Formulieren Sie das Ergebnis — und bewahren Sie es auf

Wir können die ursprüngliche Frage zu den Stationen nun mit mehr als einer einzelnen Zahl beantworten:

> **Im April 2017 zeigte die Empfangsstation G3ZIL auf 40 m gegenüber G4HZX einen gesamten stationsbalancierten medianen SNR-Vorteil von +6,5 dB, basierend auf 57 767 Vergleichen aus demselben Zyklus von 792 Sendestationseinträgen innerhalb von 10 000 km. Der Vorteil war auf vielen näheren europäischen Ausbreitungswegen deutlicher als auf entfernten westnordwestlichen Wegen und nahm während der ersten Aprilhälfte zu. Auch der Ausbreitungsweg von DJ0ABR sprach insgesamt für G3ZIL, zeigte dabei jedoch erhebliche zeitliche Schwankungen.**

**Dies sind aussagekräftige Belege für den Vergleich der beiden installierten Empfangsstationen.** Es handelt sich nicht um eine Messung des allgemeinen Gewinnunterschieds zwischen Dipolen und Vertikalantennen. Ihre Standorte, ihr lokales Rauschen und ihre vollständigen Empfangsanordnungen bleiben Bestandteil des Ergebnisses.

Speichern Sie das Ergebnispaket, um die Konfiguration, Abbildungen und verarbeiteten Beobachtungen aufzubewahren. Führen Sie für Ihre eigenen Experimente ergänzende Stationsnotizen, damit ein späterer Vergleich auch berücksichtigt, was physisch angeschlossen war und was sich verändert hat.

Sie haben nun ein Ergebnis **von der Karte zum Gesamtvergleich, über den Zeitverlauf und einzelne Stationen bis hin zu einer tatsächlichen WSPR-Beobachtung** verfolgt.

