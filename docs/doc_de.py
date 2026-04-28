# docs/doc_de.py

"""
Deutsches Handbuch f&uuml;r WSPRadar.
Wird im Web-UI und f&uuml;r den PDF-Export verwendet.
"""

DOC_DE = r"""
---

<a id="sec-1"></a>
### 1. Einleitung und Zielsetzung

Im Amateurfunk st&uuml;tzt sich die Bewertung der Antennenleistung traditionell auf anekdotische Signalrapporte oder manuelles A/B-Umschalten. Diese Methoden unterliegen jedoch erheblichen St&ouml;rvariablen: schnellem ionosph&auml;rischem Fading (QSB), inkonsistenten Sendeleistungen der Gegenstationen, lokalen St&ouml;rpegeln (QRM), ungleich verteilter Empf&auml;ngerdichte und wechselnder Stationsaktivit&auml;t. Diese Faktoren machen es schwierig, objektiv zu messen, wie gut eine Antenne oder Station im t&auml;glichen Betrieb tats&auml;chlich arbeitet.

Hier &auml;ndert das **Weak Signal Propagation Reporter (WSPR)** Protokoll die Spielregeln. WSPR ist eine digitale Betriebsart, die potenzielle Ausbreitungswege mithilfe zweimin&uuml;tiger Low-Power-Baken untersucht. Jeden Tag senden und empfangen Tausende Stationen weltweit autonom diese Baken und protokollieren gro&szlig;e Mengen zeitgestempelter Signal-Rausch-Verh&auml;ltnis-Berichte (SNR) in &ouml;ffentlichen Datenbanken. WSPR ist kein kalibriertes Laborinstrument, aber ein au&szlig;ergew&ouml;hnlich starkes globales Beobachtungsnetz: Es zeichnet kontinuierlich auf, wo Signale landen, wer wen h&ouml;ren kann und unter welchen Band-/Zeitbedingungen diese Decodes aufgetreten sind.

Das Ziel von **WSPRadar** ist es, diesen riesigen, durch Crowdsourcing entstandenen Datensatz in ein systematisches, semi-quantitatives Framework zur Bewertung von Sende- (TX) und Empfangsleistung (RX) zu verwandeln. Durch die Extraktion historischer WSPR-Spot-Daten aus wspr.live nutzt WSPRadar zeitliche Paarbildung, Leistungsnormalisierung anhand gemeldeter dBm, geografische Aggregation, medianbasierte Robustheitsfilter und interaktive Drill-Down-Tabellen. Das Ergebnis ist kein kalibrierter Antennentestplatz und kein kontrollierter Stationsmessplatz. Es ist eine praktische Realwelt-Evidenzmaschine f&uuml;r die Fragen: Wo werde ich geh&ouml;rt, wen h&ouml;re ich, wie schneide ich gegen lokale Peers ab, und hat eine Hardware&auml;nderung ein messbares Signal erzeugt?

### Inhaltsverzeichnis
* [1. Einleitung und Zielsetzung](#sec-1)
* [2. Schnellstart](#sec-2)
* [3. Welche Fragen beantwortet WSPRadar?](#sec-3)
* [4. Analysemodi und valides Experimentdesign](#sec-4)
  * [4.1 Absolut TX/RX](#sec-4-1)
  * [4.2 Lokaler Nachbarschafts-Benchmark](#sec-4-2)
  * [4.3 Spezifische Referenzstation / Buddy-Test](#sec-4-3)
  * [4.4 Hardware A/B-Test](#sec-4-4)
* [5. Ergebnisse lesen](#sec-5)
* [6. Wissenschaftliche Methodik und Annahmen](#sec-6)
  * [6.1 Datenherkunft und Robustheit](#sec-6-1)
  * [6.2 WSPR-SNR und gemeldete Leistung](#sec-6-2)
  * [6.3 Leistungsnormalisierung](#sec-6-3)
  * [6.4 Zeitliche Paarbildung und Heartbeat-Filter](#sec-6-4)
  * [6.5 Median-Aggregationshierarchie](#sec-6-5)
  * [6.6 Bivariates Auswertungsmodell](#sec-6-6)
  * [6.7 Geografisches Rastering und Projektion](#sec-6-7)
  * [6.8 Statistische Konfidenz und Wilcoxon-Filter](#sec-6-8)
* [7. Limitationen und Interpretationsregeln](#sec-7)
* [8. Konfigurationsreferenz](#sec-8)
* [9. Bestehende Literatur und Stand der Technik](#sec-9)
* [Anhang A: Paralleler Betrieb mehrerer WSJT-X Instanzen](#sec-a)
* [Quellen](#sec-ref)

<a id="sec-2"></a>
### 2. Schnellstart

1. Konfigurationsbereich &ouml;ffnen.
2. `Load Demo Config` anklicken.
3. Gew&uuml;nschten Vergleichsmodus w&auml;hlen.
4. `TX` oder `RX` starten.
5. Zuerst die Karte lesen: Farbe = medianer Segmentwert, Punkte = Stationskategorien, Fu&szlig;balken = Decode Yield.
6. Im Segment-Inspektor ein Distanz-/Azimutsegment ausw&auml;hlen.
7. Eine Station-Insights-Zeile &ouml;ffnen und die Drill-Down-Daten pr&uuml;fen.
8. CSV exportieren, wenn das Ergebnis reproduziert oder extern gepr&uuml;ft werden soll.

<a id="sec-3"></a>
### 3. Welche Fragen beantwortet WSPRadar?

WSPRadar ist um konkrete Amateurfunk-Fragen herum aufgebaut:

* **Wo wird mein Sendesignal geh&ouml;rt?** `TX Absolut`.
* **Wen kann meine Station h&ouml;ren?** `RX Absolut`.
* **Liege ich im Rahmen meiner lokalen WSPR-Nachbarschaft?** `Lokaler Nachbarschafts-Median`, der Standard-Benchmark.
* **Kann ich mit der besten aktiven lokalen Station mithalten?** `Beste lokale Station`, der strenge lokale Stresstest.
* **Wie schneide ich gegen eine bestimmte Station oder einen Funkfreund ab?** `Spezifische Referenzstation`.
* **Hat Antenne A Antenne B am eigenen Standort geschlagen?** `Hardware A/B-Test`, entweder simultan im RX oder mit festem Zeitplan im TX.
* **Sind meine Distanzmuster konsistent mit NVIS- oder DX-Verhalten?** Nahe und weite Distanzringe pr&uuml;fen, aber Distanz nicht als direkte Abstrahlwinkelmessung interpretieren.
* **Bin ich ein Alligator: werde gut geh&ouml;rt, h&ouml;re aber schlecht?** TX- und RX-Ergebnisse gegen dasselbe Referenzkonzept vergleichen und nach Asymmetrien suchen.

<a id="sec-4"></a>
### 4. Analysemodi und valides Experimentdesign

Dieses Kapitel b&uuml;ndelt Nutzerfrage, Analysekonzept und Experimentdesign. Gemeinsame Mathematik und Annahmen werden einmal in [Wissenschaftliche Methodik und Annahmen](#sec-6) erkl&auml;rt.

**Standardempfehlungen f&uuml;r alle Modi**

* Korrektes Rufzeichen und korrekten Maidenhead-Locator verwenden.
* Ein Zeitfenster w&auml;hlen, das die relevanten Ausbreitungszust&auml;nde abdeckt; mehrt&auml;gige Zeitfenster sind st&auml;rker, wenn die Aussage vollst&auml;ndige t&auml;gliche ionosph&auml;rische Zyklen betreffen soll.
* Stationskonfiguration im Analysefenster stabil halten, au&szlig;er bei der bewusst getesteten Variable.
* Bei TX-Analysen Sender, Antennen-/Speiseleitungs-/Tunerpfad, Leistungsregelung, Zeitplan und gemeldete Leistung stabil halten, sofern sie nicht die getestete Variable sind; einen realistischen Leistungswert melden.
* Bei RX-Analysen Empf&auml;nger, Antennen-/Speiseleitungspfad, Audiopfad, Decoder-Einstellungen und Upload-Verhalten stabil halten, sofern sie nicht die getestete Variable sind.

<a id="sec-4-1"></a>
#### 4.1 Absolut TX/RX

**Antwortet auf**

* `TX Absolut`: Wo wird mein Sendesignal geh&ouml;rt?
* `RX Absolut`: Wen kann meine Station h&ouml;ren?
* Beide Modi beantworten Pfad-, Footprint- und Band&ouml;ffnungsfragen, bevor eine Benchmark eingef&uuml;hrt wird.

**Funktionsweise**

* `TX Absolut` isoliert Spots, in denen das eigene Rufzeichen Sender ist, und kartiert Empf&auml;nger, die das Signal decodiert haben.
* `RX Absolut` isoliert Spots, in denen das eigene Rufzeichen Empf&auml;nger ist, und kartiert Sender, die die eigene Station decodiert hat.
* SNR wird auf 1 W normiert, wenn eine Remote-Sendeleistung relevant ist:  
  $$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$
* Absolute Karten sind sehr gut f&uuml;r Coverage, Skip-Zonen und Band&ouml;ffnungen. Allein sind sie keine fairen Hardwarevergleiche, weil Ausbreitung, Stationsaktivit&auml;t, Sendeleistung und Empf&auml;ngerrauschen nicht kontrolliert sind.

**Vorsicht bei**

* WSPR protokolliert erfolgreiche Decodes, nicht fehlgeschlagene Empfangsversuche. Tote B&auml;nder senken nicht den Median; sie reduzieren die Existenz von Spots.
* Gemeldete dBm sind nicht zwingend Speisepunktleistung oder EIRP.
* RX-Ergebnisse enthalten die gesamte Empfangskette: Antenne, Empf&auml;nger, Audiopfad, lokales Rauschen, Decoderverhalten und Upload-Zuverl&auml;ssigkeit.

<a id="sec-4-2"></a>
#### 4.2 Lokaler Nachbarschafts-Benchmark

Der lokale Nachbarschafts-Benchmark fragt, wie die eigene Station gegen aktive WSPR-Stationen innerhalb eines gew&auml;hlten geografischen Radius abschneidet. Der Radius gilt f&uuml;r beide lokalen Methoden.

**Lokaler Nachbarschafts-Median: Standard-Baseline**

F&uuml;r jeden WSPR-Zyklus und passenden Remote-Pfad berechnet WSPRadar den Median des normierten SNR aller aktiven lokalen Referenzstationen innerhalb des Radius. Die eigene Station wird gegen diesen zyklusbezogenen Nachbarschaftsmedian verglichen.

* Beste erste Antwort auf: **Bin ich f&uuml;r meine Region im Rahmen?**
* Robust gegen eine einzelne ungew&ouml;hnlich starke oder schwache lokale Station.
* Erfindet keine Werte f&uuml;r fehlende Spots. Wenn ein Nachbar in einem Zyklus nicht decodiert hat oder nicht decodiert wurde, wird das nicht als `0 dB` gez&auml;hlt.
* Bei gerader Anzahl lokaler Referenzstationen wird der Mittelpunkt-Median verwendet.
* Der Referenzpool kann sich zyklusweise &auml;ndern, weil WSPR-Aktivit&auml;t zyklusweise schwankt.

**Beste lokale Station: strenger Stresstest**

F&uuml;r jeden WSPR-Zyklus und passenden Remote-Pfad vergleicht WSPRadar gegen die st&auml;rkste aktive lokale Station im Radius.

* Beste Antwort auf: **Kann ich mit dem st&auml;rksten aktiven lokalen Peer mithalten?**
* Dies ist eine Best-Local-Peer-H&uuml;llkurve, kein Nachbarschaftsdurchschnitt.
* Die Identit&auml;t der Referenzstation kann von Zyklus zu Zyklus wechseln.
* Der Benchmark ist absichtlich schwerer zu schlagen als der Nachbarschaftsmedian.

**Valides Design**

* Einen Radius w&auml;hlen, der gen&uuml;gend aktive Peers liefert, ohne sehr unterschiedliche lokale Umgebungen zu mischen.
* In dichten Regionen kann ein kleinerer Radius reichen; in d&uuml;nn besetzten Regionen kann ein gr&ouml;&szlig;erer Radius n&ouml;tig sein.
* Ergebnis als Vergleich gegen aktive WSPR-Peers interpretieren, nicht gegen kalibrierte Referenzstationen.

**Vorsicht bei**

* Lokale Peers unterscheiden sich in Antennentyp, Gel&auml;nde, Sender-/Empf&auml;ngerqualit&auml;t, lokalem Rauschen und Genauigkeit der gemeldeten Leistung.
* Eine sehr gro&szlig;e Nachbarschaft kann aufh&ouml;ren, wirklich lokal zu sein.
* `Beste lokale Station` sollte nie als lokale Durchschnittsleistung beschrieben werden.

<a id="sec-4-3"></a>
#### 4.3 Spezifische Referenzstation / Buddy-Test

Der Buddy-Test ist ein 1:1-Vergleich mit einer bekannten Station. Man definiert ein anderes Referenzrufzeichen, zum Beispiel einen Funkfreund 10 km entfernt.

**Funktionsweise**

* Im TX-Vergleich werden beide Sendesignale m&ouml;glichst vom selben Remote-Empf&auml;nger im selben 2-Minuten-WSPR-Zyklus bewertet:  
  $$\Delta SNR_{TX} = SNR_{norm,target} - SNR_{norm,reference}$$
* Im RX-Vergleich bewerten beide lokalen Empf&auml;nger m&ouml;glichst denselben Remote-Sender im selben 2-Minuten-WSPR-Zyklus:  
  $$\Delta SNR_{RX} = SNR_{target} - SNR_{reference}$$
* Diese Same-Cycle-Paarbildung reduziert gemeinsame Fading-, Pfad- und Empf&auml;nger-/Sender-Konfounder je nach TX- oder RX-Richtung deutlich.

**Valides Design**

* Eine Referenzstation w&auml;hlen, deren Standort, Antenne, Leistung und Betriebsplan bekannt sind.
* Gleiches Band und &uuml;berlappende Zeitfenster verwenden.
* Sicherstellen, dass beide Rufzeichen gen&uuml;gend gleiche Remote-Peers im selben Zyklus teilen.

**Vorsicht bei**

* Ein Buddy-Test ist ein Stationssystem-Vergleich, keine reine Antennengewinnmessung.
* Unterschiede k&ouml;nnen Antenne, Sender, Empf&auml;nger, Speiseleitung, Gel&auml;nde, Polarisation, lokales QRM und Genauigkeit der gemeldeten Leistung enthalten.

<a id="sec-4-4"></a>
#### 4.4 Hardware A/B-Test

Der Hardware A/B-Test ist f&uuml;r eigene Ausr&uuml;stung am eigenen Standort gedacht. Er ist nur valide, wenn jede nicht getestete Variable so konstant wie praktikabel gehalten wird: Band, Zeitfenster, Leistung, Speiseleitungsverluste, Empfangskette, Audiokette, Decodiersoftware und Locator-Meldung.

* Zwei wirklich unabh&auml;ngige Empfangs- und/oder Sendeketten verwenden, wenn diese Ketten Teil des Tests sind; gemeinsam genutzte Komponenten m&uuml;ssen bewusst gew&auml;hlt, stabil gehalten und au&szlig;erhalb der getesteten Variable liegen.

**RX A/B-Test: simultan**

Zwei parallele Empf&auml;nger decodieren dieselben Remote-WSPR-Sendungen zur selben Zeit.

* Unterscheidbare Reporting-Identit&auml;ten verwenden, zum Beispiel Hauptrufzeichen f&uuml;r Setup A und Suffix f&uuml;r Setup B, damit beide Streams in der WSPR-Datenbank erscheinen.
* Uhren synchron halten.
* Anhang A beschreibt die Trennung paralleler WSJT-X-Instanzen, damit beide Decoder nicht dieselbe Audiodatei, denselben virtuellen Audiopfad, dasselbe Save Directory oder dieselben tempor&auml;ren WSPR-Dateien teilen.

**TX A/B-Test: sequenziell mit festem Zeitplan**

Setup A und Setup B k&ouml;nnen mit demselben Rufzeichen nicht gleichzeitig senden. WSPRadar nutzt daher deterministisches Time-Slicing. Ein Sender oder Controller weist ein Setup einem festen Slotmuster zu und das andere Setup dem Gegenmuster. Das Tool gruppiert Daten in Zeit-Bins, berechnet je Setup einen Mikro-Median im Bin und daraus den Bin-Delta.

* Ausgangsleistung, Speiseleitung, Tuner-Einstellungen, Band und Zeitplan konstant halten, au&szlig;er bei der getesteten Variable.
* Ein QMX-Transceiver l&auml;sst sich beispielsweise mit deterministischem Timing wie `frame=0` f&uuml;r Setup A und `frame=2` f&uuml;r Setup B programmieren.
* Standard-WSJT-X mit zuf&auml;lligem Sendemuster ist ohne Zusatzsteuerung nicht f&uuml;r fixed-schedule TX A/B geeignet.

**Vorsicht bei TX-Suffixen**

Warum keine Multi-Cycle-WSPR-Suffixe f&uuml;r Single-TX A/B? Compound-Rufzeichen k&ouml;nnen Multi-Message-Verhalten erzwingen und den Decode Yield senken, weil nicht alle Empf&auml;nger alle ben&ouml;tigten Nachrichtentypen gleich zuverl&auml;ssig decodieren. K&uuml;nstliche Suffixe wie `/1` oder `/2` k&ouml;nnen je nach Land unzul&auml;ssig sein. `/P` sollte nur verwendet werden, wenn es f&uuml;r den tats&auml;chlichen Betrieb rechtlich passt. F&uuml;r TX A/B bevorzugt WSPRadar deshalb feste Zeitschlitze mit normalem Rufzeichen.

**Wissenschaftliche Vorsicht**

Sequenzieller TX ist zeitgebinnt, nicht simultan. Mehrt&auml;giges fixes Timing reduziert Zeitkonfundierung deutlich, beweist aber nicht, dass jeder zeitkorrelierte Effekt verschwunden ist.

<a id="sec-5"></a>
### 5. Ergebnisse lesen

**Heatmap-Segmente**

Absolute Modi zeigen normiertes SNR in dB. Vergleichsmodi zeigen medianen Delta SNR gegen den gew&auml;hlten Benchmark. Positive Werte bedeuten, dass die eigene Station/das eigene Setup im Segment st&auml;rker als die Benchmark ist; negative Werte zeigen schw&auml;chere Performance. WSPRadar nutzt die g&auml;ngige Amateurfunk-Konvention `1 S-Stufe = 6 dB`.

**Distanzringe**

Nahe Ringe k&ouml;nnen mit Short-Skip oder NVIS konsistent sein; weite Ringe k&ouml;nnen mit flacherem DX-Verhalten konsistent sein. Distanz ist keine direkte Elevationswinkelmessung, weil ionosph&auml;rischer Modus, Band, Zeit, Saison und Sonnenzustand mitwirken.

**Punkte**

Einzelne Stationen werden als Punkte gezeichnet. Gr&uuml;n = Joint Decodes im selben Zyklus. Gelb-orange = beide Seiten haben die Station geh&ouml;rt, aber asynchron. Violett = nur eigene Station/eigenes Setup. Wei&szlig; = nur Referenz.

**Footer und 1D-Venn-Balken**

`SPOTS` zeigt das Rohdatenvolumen. `STATIONS` pr&uuml;ft, ob der Footprint breit ist oder nur von wenigen aktiven Stationen getragen wird. Diese Balken sind wichtig, weil Delta SNR allein Decode/No-Decode-Verhalten verbergen kann.

**Segment-Inspektor**

Der Segment-Inspektor ist die Auditschicht unterhalb der Karten. Distanzring und Himmelsrichtung ausw&auml;hlen, um die Evidenz hinter einem Segment zu pr&uuml;fen.

* In absoluten Modi zeigt das Histogramm normierte SNR-Werte der beteiligten Stationen. Die x-Achse basiert auf Stationsmedianen. Die rote gestrichelte Linie markiert den finalen Segmentmedian.
* In Vergleichsmodi zeigt das Histogramm Delta-SNR-Werte. Es zeigt, ob ein Segmentmedian aus konsistenter &Uuml;berlegenheit oder aus breiter, instabiler Streuung entsteht.
* Die Station-Insights-Tabelle listet beteiligte Remote-Stationen, trennt Joint Decodes von exklusiven Decodes und zeigt den stationsbezogenen medianen Delta SNR.
* Ein Klick auf eine Station-Insights-Zeile &ouml;ffnet die Drill-Down-Tabelle.
* `Show Non-Joint` zeigt isolierte Decodes. Fehlendes SNR wird als `None`, nicht als `0.0`, angezeigt. Wenn beide Setups eine Station h&ouml;ren, aber nie im selben WSPR-Zyklus, kann der Yield-Chart `Async Both` zeigen.

**Drill-Down-Tabelle**

Die Drill-Down-Tabelle ist die zeilenbasierte Auditschicht f&uuml;r alle Modi. Sie zeigt Beobachtungen, Paare oder Zeit-Bins hinter einer Station-Insights-Zeile, damit Segment- und Stationsmediane gegen die zugrunde liegende Evidenz gepr&uuml;ft werden k&ouml;nnen.

In absoluten Modi und normalen Same-Cycle-Vergleichsmodi zeigt der Drill-Down die beteiligten Spot-Level-Beobachtungen und gepaarten Same-Cycle-Vergleiche, die in den Stationsmedian eingehen.

F&uuml;r die Median-Nachbarschaftsmethode wird der Referenzpool expandiert. Statt nur eine generische `Ref Pool`-Zeile zu zeigen, listet die Tabelle die einzelnen lokalen Referenzstationen dieses Zyklus, ihren Locator, ihre Distanz, ihr normiertes Referenz-SNR, den aggregierten Nachbarschaftsmedian des Zyklus, das eigene SNR und den resultierenden Delta SNR. So l&auml;sst sich der Median direkt nachvollziehen.

F&uuml;r TX A/B zeigt der Drill-Down Zeitfenster statt Same-Cycle-Paare. Sichtbar sind `Micro-Med A`, `Micro-Med B` und der resultierende Bin-Delta. Gegenseitige Mikromediane werden in Single-Setup-Zeilen ausgeblendet, damit fehlende Paare nicht als Nullwerte missverstanden werden.

**Filter, Export und High-Resolution Maps**

Multi-Select, dynamische Filter und CSV-Export machen den Segment-Inspektor zur reproduzierbaren Rohdaten-Auditfl&auml;che. Die Karten-Toolbar kann eine 300-DPI-Version f&uuml;r publikationsf&auml;hige Screenshots rendern, ohne die normale interaktive Oberfl&auml;che zu blockieren.

<a id="sec-6"></a>
### 6. Wissenschaftliche Methodik und Annahmen

<a id="sec-6-1"></a>
#### 6.1 Datenherkunft und Robustheit

WSPRadar liest historische WSPR-Spots &uuml;ber wspr.live. Die wspr.live-Dokumentation beschreibt die Daten als Rohdaten, wie sie von WSPRnet gemeldet und ver&ouml;ffentlicht werden, und warnt vor Duplikaten, falschen Spots und anderen Fehlern. Au&szlig;erdem gibt es f&uuml;r die ehrenamtlich betriebene Infrastruktur keine Garantie f&uuml;r Korrektheit, Verf&uuml;gbarkeit oder Stabilit&auml;t.

WSPRadar mindert viele vorgelagerte Datenprobleme durch mehrschichtige Aggregation und Filter: Same-Cycle-Paarbildung, Stationsmediane, Segmentmediane, Mindest-Sample-Schwellen, Moving-Station-Filter und optionale Pr&auml;fix-Ausschl&uuml;sse. Diese Ma&szlig;nahmen reduzieren den Einfluss isolierter Duplikate, sporadischer falscher Spots, One-Hit-Decodes und Receiver-Density-Bias erheblich. Sie machen den vorgelagerten Datensatz nicht kalibriert oder fehlerfrei, und ein plausibler wiederholter Fehler kann weiterhin durchrutschen; der Anspruch ist Robustheit, nicht Immunit&auml;t.

<a id="sec-6-2"></a>
#### 6.2 WSPR-SNR und gemeldete Leistung

WSPR ist f&uuml;r die Untersuchung potenzieller Ausbreitungspfade mit Low-Power-Baken gedacht. WSPR-Nachrichten enthalten Rufzeichen, Locator und Leistung in dBm. WSPR-2-Sendungen dauern etwa 110,6 Sekunden und starten zwei Sekunden nach einer geraden UTC-Minute. Die ARRL-WSPR-Dokumentation beschreibt den Mindest-S/N auf der WSJT-Skala mit 2500-Hz-Referenzbandbreite.

F&uuml;r WSPRadar bedeutet das:

* SNR ist ein Decoderwert in dB auf der WSPR/WSJT-Skala, referenziert auf 2500 Hz.
* Die gemeldete Sendeleistung ist Teil der WSPR-Nachricht und wird von WSPRadar nicht unabh&auml;ngig verifiziert.
* Eingetragene dBm k&ouml;nnen von Senderausgangsleistung, Speisepunktleistung oder EIRP abweichen, etwa durch Kalibrierfehler, Foldback, Speiseleitungsverlust, Tuner-Verlust oder Fehlanpassung.

<a id="sec-6-3"></a>
#### 6.3 Leistungsnormalisierung

Um Spots mit unterschiedlichen gemeldeten Sendeleistungen vergleichen zu k&ouml;nnen, normalisiert WSPRadar das SNR auf 1 W / 30 dBm:

$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$

Das ist f&uuml;r absolute TX/RX-Karten und lokale TX-Vergleiche zentral. Es entfernt den gemeldeten Leistungsanteil aus dem Vergleich, aber nur so gut, wie die gemeldete Leistung stimmt. Antennengewinn, Speiseleitungsverlust, Kalibrierfehler oder EIRP-Unterschiede werden dadurch nicht automatisch korrigiert.

Leistungsnormalisierung ist trotzdem eine wesentliche Mitigation. RX-Vergleiche reduzieren die Abh&auml;ngigkeit von Leistungsfehlern oft, weil beide lokalen Empf&auml;nger denselben Remote-Sender bewerten. Same-Callsign TX A/B vermeidet den Vergleich unterschiedlicher selbstgemeldeter Leistungen. Lokale TX-Vergleiche und absolute TX-Karten bleiben am empfindlichsten gegen&uuml;ber falsch gemeldeten dBm.

<a id="sec-6-4"></a>
#### 6.4 Zeitliche Paarbildung und Heartbeat-Filter

Zeitliche Synchronisation ist eine der st&auml;rksten Kontrollen von WSPRadar. Same-Cycle-Paarbildung reduziert schnelle QSB-/Fading-Effekte deutlich, weil beide Seiten in derselben zweimin&uuml;tigen WSPR-Gelegenheit bewertet werden. Bei TX-Vergleichen reduziert derselbe Remote-Empf&auml;nger empfangsseitiges QRM, Noise-Floor- und Antenneneffekte. Bei RX-Vergleichen reduziert derselbe Remote-Sender Sendeleistungs- und gemeinsame Pfadvariation.

Der Heartbeat-Filter erg&auml;nzt einen separaten Schutz. WSPRadar validiert Vergleichszyklen nur, wenn das eigene Setup nachweislich aktiv war:

* Im TX-Modus muss das eigene Signal im relevanten Zyklus/Slot von mindestens einer Station weltweit decodiert worden sein.
* Im RX-Modus muss der eigene Empf&auml;nger im relevanten Zyklus mindestens eine Station decodiert haben.

Wenn die Station nachts ausgeschaltet ist, werden Referenzspots in diesem Offline-Zeitraum nicht als Niederlagen f&uuml;r die eigene Hardware gez&auml;hlt. Das macht nicht jeden Vergleich perfekt fair. Es reduziert die dominanten Timing-, Fading- und Offline-Bias-Konfounder in synchronen Modi. Sequenzieller TX A/B bleibt der Sonderfall: Time-Binning und mehrt&auml;gige fixe Zeitpl&auml;ne reduzieren Makro-Fading/Zeitdrift, sind aber nicht gleichwertig zu simultaner Same-Cycle-Paarbildung.

<a id="sec-6-5"></a>
#### 6.5 Median-Aggregationshierarchie

Mediane sind ein Kernkonzept von WSPRadar, nicht nur ein Ausrei&szlig;erfilter. Sie aggregieren robust &uuml;ber:

* kurzfristiges QSB und Fading;
* wechselnde ionosph&auml;rische Zust&auml;nde im gew&auml;hlten Zeitfenster;
* ungleiche WSPR-Aktivit&auml;t nach Zyklus und Station;
* Receiver-Density-Bias in sehr aktiven Regionen;
* gelegentliche fehlerhafte oder doppelte Spots;
* wiederholte Beobachtungen sehr aktiver Stationen;
* lokale Nachbarschafts-Referenzpools, die sich von Zyklus zu Zyklus &auml;ndern.

Die Aggregationshierarchie lautet:

* **Zyklusmedian:** Im lokalen Nachbarschafts-Median ist die Referenz f&uuml;r einen WSPR-Zyklus/Pfad der Median aktiver lokaler Referenzstationen in diesem Zyklus.
* **Stationsmedian:** F&uuml;r eine Remote-Station berechnet WSPRadar den Median der qualifizierenden Spot- oder Bin-Werte.
* **Segmentmedian:** Der finale Kartenwert ist der Median der Stationsmediane.

Diese "Median des Medians"-Struktur hilft zu verhindern, dass ein dichter Empf&auml;ngercluster eine d&uuml;nn besetzte Region nur deshalb dominiert, weil er mehr Zeilen erzeugt. Sie verhindert au&szlig;erdem, dass eine einzelne sehr aktive Station ein ganzes Segment statistisch &uuml;berm&auml;chtig pr&auml;gt.

<a id="sec-6-6"></a>
#### 6.6 Bivariates Auswertungsmodell

Eine reine Median-Delta-SNR-Analyse kann unter Survivorship Bias leiden. Eine bessere Antenne decodiert oft sehr schwache Signale, die eine schlechtere Antenne verpasst. Diese zusätzlichen Grenzfall-Spots können den Median der besseren Antenne senken, wenn alles naiv zusammengeworfen wird.

WSPRadar trennt deshalb zwei Signale:

1. **System Sensitivity / Decode Yield:** zählt exklusive und gemeinsame Decodes. Das erfasst reale operative Reichweite an der Decodiergrenze.
2. **Hardware Linearity / Delta SNR:** nutzt nur gepaarte Joint Spots oder gepaarte Zeit-Bins. Das schätzt den bedingten Gain/SNR-Unterschied, wenn beide Setups vergleichbare Evidenz erzeugt haben.

Beides muss zusammen gelesen werden. Ein Setup kann besseren Yield, aber niedrigeren bedingten SNR haben, wenn es viele Grenzfallsignale decodiert. Umgekehrt kann ein Setup auf Joint Spots starken positiven Delta SNR zeigen, aber schlechten Yield haben, wenn es viele schwache Pfade verpasst.

**Wichtige Interpretation des TX-Yield**

In der TX-Analyse wird Yield bewusst als **roher operativer Yield** ausgegeben. Er beantwortet die praktische On-Air-Frage:

**Wer wurde unter den tatsächlich gemeldeten Betriebsbedingungen häufiger decodiert?**

Das ist nützlich, aber keine leistungsnormalisierte Fairness-Metrik. Wenn eine Station mit 100 W und eine andere mit 100 mW sendet, hat die stärkere Station normalerweise einen Decode-Yield-Vorteil. WSPRadar normalisiert SNR für gemeinsame TX-Spots, bei denen beide Stationen decodiert wurden und ein SNR-Vergleich möglich ist. Bei exklusiven TX-Spots fehlt jedoch auf der nicht gehörten Seite ein SNR-Wert. WSPRadar kann daher nicht zuverlässig rekonstruieren, welches SNR die fehlende Station bei anderer Sendeleistung gehabt hätte.

Daraus folgt:

* TX Delta SNR auf Joint Spots ist das wichtigste faire Vergleichssignal.
* TX Yield sollte als rohe operative Reichweite gelesen werden, nicht als normalisierte Antenneneffizienz.
* Reference-only- oder Target-only-TX-Decodes können Antennenleistung, Sendeleistung, Ausbreitung, Empfängerverteilung, Timing, Kollisionen, Genauigkeit der gemeldeten Leistung oder eine Kombination dieser Faktoren widerspiegeln.
* Ungleiche gemeldete Sendeleistungen sollten bei der Interpretation von TX-Yield-Asymmetrien ausdrücklich erwähnt werden.

Praktisch bedeutet starker TX Yield: Eine Station wurde unter ihren tatsächlichen Betriebsbedingungen von mehr Empfangsstationen gehört. Das beweist für sich genommen nicht, dass die Antenne besser war. Für faireres TX-Benchmarking sollte das größte Gewicht auf Same-Cycle, leistungsnormalisiertem Delta SNR liegen; roher Yield dient als unterstützender Kontext.

<a id="sec-6-7"></a>
#### 6.7 Geografisches Rastering und Projektion

R&auml;umliche Daten werden in einer mittabstandstreuen Azimutalprojektion dargestellt, zentriert auf dem Maidenhead-Locator des Nutzers. Die Kartenengine nutzt intern eine sph&auml;rische Erde mit 6371 km Radius, damit Tabellendistanzen und geplottete Kartenpositionen derselben Geometrie folgen.

Die Karte nutzt:

* konzentrische Distanzb&auml;nder von 2500 km;
* Azimut-Wedges, z. B. 22,5-Grad-Kompasssektoren;
* eindeutige Segment-IDs f&uuml;r Aggregation und Inspektion.

Die Projektion ist f&uuml;r WSPRadars visuelle Analyse intern konsistent. Sie sollte nicht als geod&auml;tische Vermessung mit Survey-Pr&auml;zision beschrieben werden.

<a id="sec-6-8"></a>
#### 6.8 Statistische Konfidenz und Wilcoxon-Filter

WSPRadar kann optional einen Wilcoxon-Vorzeichen-Rang-Test als Compare-Map-Filter verwenden. SciPy dokumentiert diesen Test f&uuml;r verbundene gepaarte Stichproben und beschreibt ihn ausdr&uuml;cklich &uuml;ber die Verteilung gepaarter Differenzen.

Korrekte Interpretation:

* Der Test ist ein n&uuml;tzlicher Robustheitsfilter f&uuml;r gepaarte Delta-SNR-Werte.
* Ein p-Wert ist keine Effektgr&ouml;&szlig;e.
* Segmentweise p-Werte erzeugen ein Multiple-Comparison-Risiko &uuml;ber die Karte.
* WSPR-SNR-Werte sind quantisiert und oft zeitlich autokorreliert; das schw&auml;cht ideale Lehrbuchannahmen.
* Null-Differenzen und Ties m&uuml;ssen vorsichtig behandelt werden; auch das dokumentiert SciPy.

Wilcoxon-Filterung sollte deshalb als statistische Evidenz, nicht als Beweis, beschrieben werden. Eine wissenschaftlich st&auml;rkere sp&auml;tere Version k&ouml;nnte Bootstrap-Konfidenzintervalle und False-Discovery-Rate-Korrektur &uuml;ber Kartensegmente erg&auml;nzen.

<a id="sec-7"></a>
### 7. Limitationen und Interpretationsregeln

**Kernlimitationen**

* **Crowd-sourced Daten:** WSPR-Spots k&ouml;nnen Duplikate, falsche Spots, falsche Leistung, falschen Locator oder empfangsseitige Fehler enthalten. WSPRadar reduziert die Empfindlichkeit gegen&uuml;ber vielen dieser Probleme, kann upstream Daten aber nicht kalibriert oder fehlerfrei machen.
* **Nur erfolgreiche Decodes:** WSPR protokolliert Decodes, nicht alle fehlgeschlagenen Empfangsversuche. Geschlossene B&auml;nder reduzieren die Existenz von Spots, statt einen Durchschnitt zu senken.
* **Gemeldete Leistung:** Normalisierung mindert Unterschiede in gemeldeter Leistung, und mehrere Vergleichsmodi reduzieren dieses Problem zus&auml;tzlich durch Paarbildung gegen denselben Sender oder dasselbe Rufzeichen. Jede Analyse, die auf gemeldeten dBm basiert, setzt aber weiterhin voraus, dass der gemeldete Wert ungef&auml;hr stimmt.
* **Sequenzieller TX:** Fixed-schedule TX A/B reduziert Zeitkonfundierung, eliminiert sie aber nicht perfekt.
* **Distanz ist kein Winkel:** Distanzringe k&ouml;nnen Ausbreitungsverhalten nahelegen, messen aber keinen Abstrahlwinkel direkt.
* **Polarisation und lokale Umgebung:** WSPRadar misst reale Stationssystem-Performance, einschlie&szlig;lich Antenne, Sender/Empf&auml;nger, Speiseleitung, Gel&auml;nde, Polarisation, lokalem QRM und Softwareverhalten.
* **Performance-Limits und Latenz:** Query-Fenster sind zum Schutz der Datenbank begrenzt; neue Spots k&ouml;nnen etwa 15 bis 30 Minuten brauchen, bis sie sichtbar werden.

**Evidenzsprache**

* **Schwache Evidenz:** sehr wenige Joint-Zyklen, sehr wenige Stationen oder ein Ergebnis, das von einem Ausrei&szlig;er getragen wird.
* **Nutzbare Evidenz:** mehrere Stationen pro Segment, mehrere Joint-Zyklen oder Bins pro Station, konsistente Delta-SNR-Richtung und plausibles Yield-Verhalten.
* **Starke Evidenz:** &uuml;ber mehrere Tage oder getrennte Runs wiederholt, &uuml;ber benachbarte Segmente oder B&auml;nder plausibel stabil, nicht von einer Station dominiert und durch exportierte Rohdaten belegbar.

F&uuml;r ernsthafte Aussagen sollte gen&uuml;gend Kontext erhalten bleiben, um das Ergebnis zu reproduzieren: WSPRadar-Version oder Git-Commit, UTC-Fenster, Band, Modus, Filter, lokale Benchmark-Methode oder Referenzrufzeichen, Screenshots und exportierte CSV.

**Haftungsausschluss**

WSPRadar ist ein experimentelles Open-Source-Projekt und wird ohne Gew&auml;hrleistung bereitgestellt. Quellcode und mathematisches Modell sind pr&uuml;fbar, aber der Entwickler kann keine Genauigkeit, Vollst&auml;ndigkeit, Verf&uuml;gbarkeit oder Eignung f&uuml;r einen bestimmten Zweck garantieren. Gr&ouml;&szlig;ere finanzielle Entscheidungen, etwa Kauf oder Verkauf teurer Antennen oder Funkhardware, sollten nie ausschlie&szlig;lich auf WSPRadar-Ausgaben basieren.

**Lizenz**

WSPRadar ist freie Software unter der GNU Affero General Public License (AGPLv3). Die Lizenz stellt sicher, dass der Quellcode, einschlie&szlig;lich &Auml;nderungen an Netzwerkdiensten, der Amateurfunk-Community zug&auml;nglich bleibt.

<a id="sec-8"></a>
### 8. Konfigurationsreferenz

**Core-Parameter**

* **Zielrufzeichen:** prim&auml;re Station unter Auswertung.
* **QTH Locator:** mathematisches Zentrum der Kartenprojektion. G&uuml;ltigen 4- oder 6-Zeichen-Maidenhead-Locator verwenden.
* **Band und Zeitfenster:** definieren das WSPR-Datenfenster. Zeit wird in UTC behandelt.

**Vergleichsparameter**

* **Benchmark Mode:** `Lokaler Nachbarschafts-Benchmark`, `Fremdes Rufzeichen (Buddy-Test)` oder `Hardware A/B-Test`.
* **Lokale Benchmark-Methode:** standardm&auml;&szlig;ig `Lokaler Nachbarschafts-Median`, optional `Beste lokale Station` als strenge Best-Peer-H&uuml;llkurve.
* **Nachbarschaftsradius:** geografische Grenze f&uuml;r lokale Referenzstationen.
* **Referenzrufzeichen:** externer Gegenpart f&uuml;r Buddy-Test.
* **A/B-Test Setup:** simultaner `RX Test` oder fixed-schedule `TX Test`.
* **Target/Reference Locator:** 6-Zeichen-Locators zur Trennung simultaner RX-Streams.
* **Target/Reference Time Slot:** feste Slotzuweisung f&uuml;r sequenzielle TX-Tests.
* **Time Window (Bins):** Bin-Gr&ouml;&szlig;e f&uuml;r sequenzielle TX-A/B-Paarbildung.

**Erweiterte Einstellungen**

* **Exclude Special Callsigns:** entfernt bekannte Sonderformat-WSPR-Rufzeichen aus der Analyse anhand des eingebauten WSPRadar-Präfixfilters. Der aktuelle Filter schließt Rufzeichen aus, die mit `Q`, `0` oder `1` beginnen. Diese Präfixe sind häufig mit speziellen WSPR-Anwendungsfällen wie telemetrieartigen oder nicht-standardmäßigen Beacon-Kennungen verbunden (z.B. Pico-Ballon), nicht mit normalen Amateurfunk-Rufzeichen.
* **Exclude Moving Stations:** entfernt Stationen, die während des Analysefensters ihren 4-stelligen Locator ändern, zum Beispiel Ballons, mobile oder maritime Stationen.
* **Local QTH Solar State:** filtert nach berechneter Sonnenhöhe am eigenen QTH: Tageslicht, Nacht oder Greyline.
* **Map Scope:** visueller Kartenradius.
* **Min. Joint Spots/Station:** erfordert in Vergleichsmodi mindestens X Joint Spots pro Remote-Station, bevor diese Station zu einem Delta SNR beiträgt. In sequenziellem TX A/B wird dies als Min. Joint Bins angezeigt. In absoluten Modi wirkt derselbe Regler als Roh-Spots-pro-Station-Filter.
* **Min. Joint Stations/Segment:** erfordert in Vergleichsmodi mindestens X Remote-Stationen mit qualifizierender Joint-Evidenz, bevor ein Segment gezeichnet wird. In absoluten Modi wirkt derselbe Regler als Roh-Stationen-pro-Segment-Filter.
* **Compare Map Statistical Confidence:** optionaler Wilcoxon-basierter Filter.

**Hinweis zum Sonderrufzeichen-Filter**

Der Sonderrufzeichen-Filter ist besonders nützlich, wenn nicht-standardmäßige Beacon- oder telemetrieartige Stationen die normale Station-zu-Station-Interpretation verzerren würden. Er sollte jedoch nicht automatisch für jede Analyse aktiviert werden.

Für RX-Vergleiche gibt es oft einen guten Grund, diese Rufzeichen **nicht** auszuschließen. Viele spezielle WSPR-Kennungen verhalten sich wie Low-Power-Baken. Wenn dieselbe schwache Bake im selben WSPR-Zyklus sowohl von der eigenen Station als auch von der Referenzstation decodiert wird, ist das wertvolle gepaarte RX-Evidenz. In diesem Fall ist die absolute Identität der Bake weniger wichtig als die Tatsache, dass beide Empfänger denselben schwachen Sender zur selben Zeit bewertet haben.

Empfohlene Interpretation:

* Bei **TX-Analysen** kann das Ausschließen von Sonderrufzeichen helfen, die Empfänger-/Referenzpopulation näher an normalen Amateurfunkstationen zu halten.
* Bei **RX-Vergleichen** kann das Beibehalten von Sonderrufzeichen nützlich sein, weil sie schwache, stabile Same-Cycle-Testsignale liefern können.
* Bei **absoluter RX-Coverage** hängt die Wahl von der Fragestellung ab: einschließen, wenn Beacon-Sensitivität interessant ist; ausschließen, wenn nur normale Amateurfunkaktivität betrachtet werden soll.
* Für **Veröffentlichungen oder ernsthafte Vergleiche** sollte dokumentiert werden, ob der Sonderrufzeichen-Filter aktiviert war.

* [9. Bestehende Literatur und Stand der Technik](#sec-9)

<a id="sec-9"></a>
### 9. Bestehende Literatur und Stand der Technik

WSPRadar steht nicht isoliert. Es baut auf drei bereits etablierten Linien auf: Erstens auf WSPR als globalem, durch Funkamateure betriebenem Beobachtungsnetz; zweitens auf wissenschaftlichen Arbeiten, die WSPR-Daten für Ausbreitungs- und Antennenfragen verwenden; drittens auf praktischen Werkzeugen, die WSPR-Spots visualisieren, abfragen oder für Antennenvergleiche auswerten.

Dieses Kapitel ordnet WSPRadar in diesen Kontext ein und grenzt den eigenen Anspruch bewusst ab: WSPRadar ist kein kalibrierter Antennenmessplatz und kein Ersatz für kontrollierte Feldstärkemessungen. Es ist ein Werkzeug zur robusten, auditierbaren Realwelt-Bewertung von Stationssystemen auf Basis öffentlicher WSPR-Spots.

<a id="sec-9-1"></a>
#### 9.1 WSPR als globales Beobachtungsnetz

WSPR wurde für die Untersuchung potenzieller Ausbreitungspfade mit niedriger Sendeleistung entwickelt. Die ARRL beschreibt WSPR als schmalbandiges digitales Protokoll für HF- und MF-Ausbreitungstests. Eine typische WSPR-Nachricht enthält Rufzeichen, 4-stelligen Maidenhead-Locator und Sendeleistung in dBm. Die Aussendung dauert etwa 110,6 Sekunden und beginnt zwei Sekunden nach einer geraden UTC-Minute. Die minimale Dekodierbarkeit liegt ungefähr bei -27 dB auf der WSJT-Skala mit 2500-Hz-Referenzbandbreite. [9-1]

Die öffentliche WSPR-Infrastruktur ist aber kein Laborinstrument. WSPR.live stellt historische und aktuelle WSPR-Spots in einer ClickHouse-Datenbank bereit und weist ausdrücklich darauf hin, dass es sich um Rohdaten handelt, wie sie von WSPRnet gemeldet und veröffentlicht wurden. Duplikate, falsche Spots, fehlerhafte Locator, falsche Leistungen und Infrastrukturausfälle sind deshalb Teil des realen Datenumfelds. [9-2]

WSPRadar übernimmt diese Unsicherheit nicht blind, sondern reduziert ihre Wirkung durch Filter, Mindestschwellen, Mediane, zeitliche Paarbildung, Segmentaggregation und Drill-Down-Prüfbarkeit. Der Anspruch ist nicht, aus Crowd-Daten kalibrierte Messdaten zu machen. Der Anspruch ist, aus unvollkommenen, aber sehr zahlreichen Beobachtungen eine nachvollziehbare und vorsichtig interpretierte Evidenzschicht zu erzeugen.

<a id="sec-9-2"></a>
#### 9.2 WSPR in Radio Science und Ionosphärenforschung

Lo et al. untersuchten 7-MHz-Greyline-Ausbreitung anhand von Amateurfunk-Bakensignalen aus der WSPR-Datenbank. Die Arbeit zeigt exemplarisch, dass WSPR nicht nur für individuelle Stationsbeobachtung nützlich ist, sondern auch als wissenschaftlicher Datensatz für globale HF-Ausbreitungsfragen verwendet werden kann. Besonders relevant für WSPRadar ist dabei die Grundidee, dass WSPR-Pfade zeitlich, geografisch und bandbezogen ausgewertet werden können, ohne dass die ursprüngliche Infrastruktur als kontrolliertes Experiment aufgebaut wurde. [9-3]

Frissell et al. ordnen WSPRNet zusammen mit dem Reverse Beacon Network und PSKReporter als etablierte Amateurfunk-Beobachtungsnetzwerke ein, die langfristige Daten über die untere Ionosphäre liefern. Die Arbeit ist wichtig, weil sie die Rolle des Amateurfunks als Citizen-Science-Infrastruktur beschreibt: Viele unabhängige Stationen erzeugen gemeinsam ein Beobachtungsnetz, das für Raumwetter-, Ionosphären- und HF-Ausbreitungsfragen relevant ist. Für WSPRadar ist diese Perspektive zentral: Das Tool verwendet nicht einzelne Rapporte als absolute Wahrheit, sondern nutzt die Masse, Wiederholung und räumliche Verteilung der Beobachtungen. [9-4]

Aus diesen Arbeiten folgt eine wichtige methodische Konsequenz: WSPR-Daten sind für Radio Science brauchbar, aber sie müssen als Beobachtungsdaten gelesen werden. Sie enthalten reale Ausbreitung, reale Stationsunterschiede und reale Fehlerquellen gleichzeitig. WSPRadar versucht deshalb nicht, diese Faktoren vollständig zu eliminieren, sondern die dominanten Störgrößen für konkrete Vergleichsfragen sichtbar zu machen und so weit wie möglich zu reduzieren.

<a id="sec-9-3"></a>
#### 9.3 WSPR für Antennen- und Stationsvergleiche

Vanhamel, Machiels und Lamy verwendeten WSPR auf dem 160-m-Band zur Antennenbewertung und Ausbreitungsanalyse. Ihr Aufbau nutzte zwei nahezu identische WSPR-Empfangsketten an ähnlichem Standort, um unterschiedliche 160-m-Antennen zu vergleichen. Die Arbeit ist für WSPRadar besonders wichtig, weil sie denselben Kernkonflikt behandelt: WSPR-SNR enthält sowohl Antennen-/Stationsleistung als auch Ausbreitung, Rauschen, Polarisation und zeitliche Variabilität. Die Studie reduziert diese Störgrößen durch nahe beieinander liegende, vergleichbare Empfangssysteme und zeigt damit einen methodischen Vorläufer für simultane RX-A/B-Vergleiche. [9-5]

Zander schlug eine einfache Methode vor, um HF-Antennen relativ zu einer Referenzantenne mit Hilfe des globalen WSPR-Empfängernetzes zu vergleichen. Dabei senden zwei Antennen, und nur Berichte derselben entfernten Empfangsstation im gleichen Zeitintervall werden als Vergleich herangezogen. Damit werden Ausbreitungsverlust und Empfängerrauschen weitgehend gemeinsam gemacht; übrig bleibt näherungsweise die Differenz zwischen den beiden sendenden Antennensystemen. Diese Idee ist sehr nah an WSPRadars Same-Cycle-Logik für TX-Vergleiche. Zugleich diskutiert Zander Einschränkungen wie Empfängerverteilung, Richtdiagramm-Bias, Interferenz, WSPR-Kollisionen und die Tatsache, dass relative Effizienz nicht automatisch ein vollständiges Antennendiagramm ergibt. [9-6]

Diese Arbeiten stützen den Grundgedanken von WSPRadar: WSPR kann für Antennen- und Stationsvergleiche nützlich sein, wenn Vergleichspaare sauber gebildet und Störgrößen bewusst behandelt werden. Sie begrenzen aber auch die Sprache, mit der Ergebnisse beschrieben werden sollten. Ein WSPR-basierter Vergleich kann starke Hinweise auf reale Stationsperformance liefern, aber er misst nicht direkt Antennengewinn, Abstrahlwinkel oder Wirkungsgrad im kalibrierten Labor-Sinn.

<a id="sec-9-4"></a>
#### 9.4 Bestehende Werkzeuge und praktische Prior Art

**WSPR.live** ist für WSPRadar die wichtigste Datenquelle. Die Plattform stellt eine öffentlich abfragbare ClickHouse-Datenbank mit historischen WSPR-Spots bereit, ergänzt durch Dokumentation, Grafana-Dashboards und Beispiele zur Datenstruktur. WSPR.live ist damit weniger ein Antennenvergleichswerkzeug als vielmehr die zentrale, schnelle Datengrundlage für eigene Analysen. WSPRadar nutzt diese Infrastruktur, ergänzt sie aber um stationsbezogene Experimentlogik, Segmentaggregation und interaktive Audit-Ansichten. [9-2]

**WSPR.Rocks** ist ein mächtiges Analyse- und Visualisierungswerkzeug auf Basis der WSPR.live- und WSPRdaemon-Daten. Es bietet unter anderem SpotQ, SQL-Zugriff, Karten, Tabellen, Duplicate-Spot-Analyse, Passband-Darstellungen und interaktive Auswertungen. Besonders SpotQ ist als praktisches Rankingmaß interessant, weil es Distanz, Leistung und SNR in eine einfache Kennzahl überführt. WSPRadar verfolgt einen anderen Schwerpunkt: Es berechnet keine globale Bestenliste, sondern versucht, konkrete Vergleichsfragen mit kontrollierter Paarbildung, lokalen Referenzpools und segmentbezogener Evidenz zu beantworten. [9-7]

**WSPRdaemon** ist vor allem auf robuste Datenerfassung ausgelegt. Es kann WSPR und FST4W von mehreren SDR-Empfängern dekodieren, Spots zuverlässig zu WSPRnet hochladen, Band- und Empfänger-Schedules verwalten, Ausfälle überstehen und zusätzliche Informationen wie Doppler-Shift und Hintergrundrauschen erfassen. Damit ist WSPRdaemon eher eine professionelle Empfangs- und Reporting-Infrastruktur als ein Endnutzer-Tool für Antennenbenchmarking. Für WSPRadar ist es dennoch relevante Prior Art, weil es zeigt, wie wichtig stabile Multi-Receiver-Datenerfassung, Rauschinformation und langfristige Beobachtbarkeit für belastbare WSPR-Auswertung sind. [9-8]

**SOTABEAMS WSPRlite und DXplorer** sind direkte praktische Prior Art für WSPR-basierte Antennen- und Standortvergleiche. WSPRlite ist ein kleiner WSPR-Sender; DXplorer nutzt WSPR-Daten, um Antennen- und Standortleistung unter anderem über den DX10-Wert und Echtzeitgraphen vergleichbar zu machen. Die Stärke dieses Ansatzes liegt in einfacher Bedienung und direktem Praxisnutzen. WSPRadar unterscheidet sich durch einen stärker auditierbaren, datenanalytischen Ansatz: Es zeigt nicht nur einen Score, sondern Segmentwerte, Joint/Exclusive-Decodes, Station-Insights und Drill-Down-Zeilen, damit ein Ergebnis nachvollzogen und angezweifelt werden kann. [9-9]

**WSPR-Station-Compare** und ähnliche Werkzeuge zeigen, dass der Bedarf an stationsbezogenen WSPR-Vergleichen bereits erkannt wurde. Die WSPR-Station-Compare-Seite verweist ausdrücklich auf Vanhamel, Machiels und Lamy sowie auf Zander und beschreibt eine App-Idee zur Darstellung und zum Vergleich eigener WSPRnet-Messungen. Das bestätigt die Nähe zwischen wissenschaftlichem Ansatz und Amateurfunkpraxis: Nutzer möchten nicht nur sehen, wo Spots auftreten, sondern wissen, ob eine Station, Antenne oder Änderung messbar besser oder schlechter ist. [9-10]

**Antenna Performance Analysis Tool** und andere neuere Webdienste zeigen denselben Trend: WSPR-Daten werden zunehmend für verständliche, anwenderorientierte Antennenberichte genutzt. Solche Tools kartieren Empfangsorte, Zeiträume und Bänder und helfen Operatoren, die reale Wirkung einer Antenne über Zeit zu beurteilen. WSPRadar sollte deshalb nicht behaupten, als erstes Werkzeug WSPR für Antennenperformance zu nutzen. Die eigene Stärke liegt vielmehr in der Kombination aus Vergleichsdesign, lokalen Benchmarks, Medianlogik, bivariater Yield/SNR-Auswertung und nachvollziehbaren Rohdatenebenen. [9-11]

**WATT WSPR Analysis Tool** ist ein weiteres Beispiel für praktische Prior Art. Es nutzt eine Excel/VBA-Umgebung für Reporting, Mapping, Filterung, Ad-hoc-Analyse und zeitliche Animation von WSPR-Daten. Der Ansatz ist interessant, weil er zeigt, dass WSPR-Auswertung auch als explorativer Arbeitsfluss verstanden werden kann: Nutzer möchten Daten nicht nur ansehen, sondern filtern, sortieren, animieren und eigene Fragen stellen. WSPRadar greift diese explorative Idee auf, verlagert sie aber in eine webbasierte, experimentdesign-orientierte Oberfläche. [9-12]

<a id="sec-9-5"></a>
#### 9.5 Einordnung von WSPRadar

Aus dieser Literatur und Prior Art ergibt sich eine klare Einordnung:

* WSPRadar übernimmt von WSPR und WSPR.live die Idee eines globalen, historischen, crowd-sourced Beobachtungsdatensatzes.
* WSPRadar übernimmt von wissenschaftlichen Arbeiten wie Vanhamel et al. und Zander die Einsicht, dass faire Vergleiche zeitliche und räumliche Konfounder reduzieren müssen.
* WSPRadar übernimmt von praktischen Tools wie WSPR.Rocks, DXplorer, WSPRdaemon und WATT die Erkenntnis, dass WSPR-Daten nur dann nützlich sind, wenn sie schnell, filterbar, visualisierbar und reproduzierbar zugänglich sind.
* WSPRadar ergänzt diese Ansätze durch einen eigenen Schwerpunkt: experimentelles Stationsbenchmarking mit Same-Cycle-Paarbildung, lokalen Nachbarschaftsreferenzen, Hardware-A/B-Workflows, Median-von-Medianen-Aggregation, Decode-Yield-Auswertung und Drill-Down-Audit.

WSPRadar sollte daher nicht als Ersatz für WSPR.live, WSPR.Rocks, WSPRdaemon oder DXplorer beschrieben werden. Es sitzt eine Ebene darüber: Es nutzt historische WSPR-Spots, um konkrete Stationsfragen methodisch vorsichtiger zu beantworten. Die Kernfrage lautet nicht nur: „Wo gibt es Spots?“, sondern: „Welche Spots sind für diese Vergleichsfrage gültig, welche Störgrößen wurden reduziert, wie stabil ist der Median, wie sieht der Decode Yield aus, und kann ich das Ergebnis bis auf die zugrunde liegenden Zeilen zurückverfolgen?“

<a id="sec-9-6"></a>
#### 9.6 Methodische Konsequenzen für die Interpretation

Die vorhandene Literatur stützt den Grundansatz von WSPRadar, aber sie begrenzt auch die Sprache, mit der Ergebnisse beschrieben werden sollten. WSPR-basierte Auswertungen können starke Hinweise auf reale Stationsperformance liefern, aber sie messen nicht direkt Antennengewinn, Abstrahlwinkel oder Effizienz im kalibrierten Labor-Sinn. Reported Power, Locator-Genauigkeit, Empfängerverteilung, lokale Störungen, Polarisation, Ausbreitungsmodus, Bandaktivität und Decode-Survivorship bleiben Teil der Daten.

Deshalb sollte WSPRadar-Ergebnistext konsequent zwischen folgenden Ebenen unterscheiden:

* **Spot-Ebene:** einzelne WSPR-Decodes mit SNR, Zeit, Band, Sender, Empfänger und gemeldeter Leistung.
* **Paar-Ebene:** gültige Same-Cycle-Vergleiche oder gültige Zeit-Bins, bei denen wichtige Störgrößen reduziert wurden.
* **Stations-Ebene:** Median über mehrere gültige Beobachtungen einer Remote-Station.
* **Segment-Ebene:** Median über mehrere Stationsmediane in einem Distanz-/Azimutsegment.
* **Interpretations-Ebene:** vorsichtige Aussage über reale Stationsperformance, nicht über isolierten Antennengewinn.

Diese Schichtung ist eine der wichtigsten Abgrenzungen von WSPRadar gegenüber einfacheren Karten- oder Score-Werkzeugen. Sie macht das Ergebnis nicht automatisch „wahr“, aber sie macht sichtbar, welche Evidenz hinter einer Aussage steht.

<a id="sec-9-7"></a>
#### 9.7 Kurzfazit

Die bestehende Literatur zeigt, dass WSPR-Daten für Ausbreitungsforschung, Antennenvergleich und Citizen Science ernsthaft nutzbar sind. Die praktische Prior Art zeigt, dass viele Funkamateure bereits Werkzeuge für Karten, Scores, Datenbankabfragen und Antennenberichte verwenden. WSPRadar positioniert sich zwischen diesen Welten: Es ist praxisnah genug für den täglichen Stationsvergleich, aber methodisch explizit genug, um die wichtigsten Konfounder offenzulegen.

Der Beitrag von WSPRadar liegt nicht darin, WSPR-Spots neu zu erfinden. Der Beitrag liegt darin, diese Spots in ein reproduzierbares, vorsichtig interpretiertes Benchmarking-Framework für TX-, RX-, lokale Peer- und Hardware-A/B-Fragen zu überführen.
  
<a id="sec-a"></a>
### Anhang A: Paralleler Betrieb mehrerer WSJT-X Instanzen

Diese Anleitung beschreibt die Erzeugung einer zweiten OS-isolierten WSJT-X-Umgebung, z. B. f&uuml;r einen SDR, inklusive Konfigurationsmigration und zwingender Pfadtrennung.

#### 1. Instanziierung (OS-Level-Isolation)

Standardm&auml;&szlig;ig verhindert das WSJT-X-Lockfile Mehrfachstarts. Die Trennung erfolgt mit einem Command-Line-Parameter, der eine neue Sandbox im Windows-`AppData`-Verzeichnis erzwingt.

1. Desktop-Verkn&uuml;pfung f&uuml;r `wsjtx.exe` erstellen.
2. Eigenschaften der Verkn&uuml;pfung &ouml;ffnen.
3. Das Feld `Ziel` nach diesem Muster &auml;ndern, Parameter au&szlig;erhalb der Anf&uuml;hrungszeichen:
   `"C:\Program Files\wsjtx\bin\wsjtx.exe" --rig-name=SDR`
4. Diese Verkn&uuml;pfung einmal starten und sofort wieder schlie&szlig;en. Dadurch wird `%LOCALAPPDATA%\WSJT-X - SDR` initialisiert.

#### 2. Konfigurationsmigration (Klonen)

WSJT-X bietet keinen internen Export f&uuml;r Instanzen. Der Klon muss auf Dateisystemebene erfolgen.

1. In den prim&auml;ren Konfigurationsordner navigieren: `%LOCALAPPDATA%\WSJT-X`
2. `WSJT-X.ini` kopieren.
3. In den neuen Ordner navigieren: `%LOCALAPPDATA%\WSJT-X - SDR`
4. Datei einf&uuml;gen und die beim Erststart erzeugte `.ini` &uuml;berschreiben.
5. Die eingef&uuml;gte Datei exakt passend zur neuen Instanz umbenennen: `WSJT-X - SDR.ini`

#### 3. Zwingende Pfadtrennung (Audio und Speicherorte)

Da die Konfiguration geklont wurde, zeigen beide Instanzen m&ouml;glicherweise noch auf dieselben Hardwareeing&auml;nge und tempor&auml;ren Speicherorte. F&uuml;r WSPR kann das zu identischen Decodes f&uuml;hren, weil dieselbe `.wav` analysiert wird, und File-Lock-Fehler erzeugen.

Neue SDR-Instanz &ouml;ffnen und `File > Settings > Audio` aufrufen. Anpassen:

* **Soundcard > Input:** Audio-Interface auf die zweite Empf&auml;ngerquelle setzen, z. B. ein dediziertes Virtual Audio Cable.
* **Save Directory:** Pfad in die isolierte Umgebung &auml;ndern, z. B.:
  `C:\Users\[User]\AppData\Local\WSJT-X - SDR\save`
* **AzEl Directory:** auch diesen Pfad &auml;ndern, z. B.:
  `C:\Users\[User]\AppData\Local\WSJT-X - SDR`

Nach dem Neustart sind Datenstr&ouml;me, Hardwarezugriffe und tempor&auml;re WSPR-Dateien von der Prim&auml;rinstanz getrennt.

<a id="sec-ref"></a>
### Quellen / Referenzen

* [9-1] ARRL, **WSPR**, technische Übersicht zu MEPT_JT/WSPR, Nachrichtenformat, Dauer, Bandbreite und SNR-Referenz.  
  https://www.arrl.org/wspr

* [9-2] WSPR.live, **Welcome to WSPR Live**, Dokumentation, Datenbankbeschreibung und Disclaimer zu Rohdaten, Duplikaten, falschen Spots und Verfügbarkeit.  
  https://wspr.live/

* [9-3] Lo, S.; Rankov, N.; Mitchell, C.; Witvliet, B. A.; Jayawardena, T. P.; Bust, G.; Liles, W.; Griffiths, G. (2022). **A Systematic Study of 7 MHz Greyline Propagation Using Amateur Radio Beacon Signals**. *Atmosphere*, 13(8), 1340. doi:10.3390/atmos13081340.  
  https://www.mdpi.com/2073-4433/13/8/1340

* [9-4] Frissell, N. A. et al. (2023). **Heliophysics and amateur radio: citizen science collaborations for atmospheric, ionospheric, and space physics research and operations**. *Frontiers in Astronomy and Space Sciences*, 10, Article 1184171. doi:10.3389/fspas.2023.1184171.  
  https://www.frontiersin.org/articles/10.3389/fspas.2023.1184171/full

* [9-5] Vanhamel, J.; Machiels, W.; Lamy, H. (2022). **Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band**. *International Journal of Antennas and Propagation*, 2022, Article 4809313. doi:10.1155/2022/4809313.  
  https://research.tudelft.nl/en/publications/using-the-wspr-mode-for-antenna-performance-evaluation-and-propag/

* [9-6] Zander, J. (2022). **Simple HF antenna efficiency comparisons using the WSPR system**. arXiv:2209.08989. doi:10.48550/arXiv.2209.08989.  
  https://arxiv.org/abs/2209.08989

* [9-7] WSPR.Rocks, **Help & Documentation**, SpotQ, SQL-Zugriff, Duplicate-Spot-Analyse, Karten, Charts und Heatmaps.  
  https://wspr.rocks/help.html

* [9-8] WSPRdaemon, **How wsprdaemon Works**, Dokumentation für Multi-Receiver-WSPR/FST4W-Dekodierung, Reporting, Scheduling, Noise- und Doppler-Metadaten.  
  https://wsprdaemon.readthedocs.io/en/stable/description/how_it_works.html

* [9-9] SOTABEAMS, **WSPRlite Classic / DXplorer**, WSPR-basierte Antennenleistungsanalyse und DX10-Metrik.  
  https://www.sotabeams.co.uk/wsprlite-classic

* [9-10] WSPR-Station-Compare, **WSPR-Station-compare**, Projektseite mit Verweis auf Vanhamel et al. und Zander.  
  https://sites.google.com/myuba.be/wspr-station-compare/home

* [9-11] Antenna Performance Analysis Tool, **WSPR-based antenna report generator**.  
  https://wspr.bsdworld.org/

* [9-12] GM4EAU, **WATT WSPR Analysis Tool**, Excel/VBA-basiertes Werkzeug für WSPR-Reporting, Mapping, Filterung und Timeline-Animation.  
  https://www.gm4eau.com/home-page/wspr/
"""
