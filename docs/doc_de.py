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
  * [4.0 Begriffe und Vergleichslogik](#sec-4-0)
  * [4.1 TX/RX-Erfolgsrate](#sec-4-1)
  * [4.2 Lokaler Nachbarschafts-Benchmark](#sec-4-2)
  * [4.3 Spezifische Referenzstation / Buddy-Test](#sec-4-3)
  * [4.4 Hardware A/B-Test](#sec-4-4)
  * [4.5 Decode Yield in Vergleichsmodi](#sec-4-5)
* [5. Ergebnisbegriffe und Oberfl&auml;che lesen](#sec-5)
  * [5.1 Karte](#sec-5-1)
  * [5.2 Segment Insight - TX/RX-Erfolg](#sec-5-2)
  * [5.3 Segment Insight - Vergleichsmodi](#sec-5-3)
  * [5.4 Station Insights und ausgew&auml;hlte Stations-Evidenz](#sec-5-4)
  * [5.5 Export- und Download-Reproduzierbarkeitspaket](#sec-5-5)
* [6. Wissenschaftliche Methodik und Annahmen](#sec-6)
  * [6.1 Datenherkunft und Robustheit](#sec-6-1)
  * [6.2 WSPR-SNR und gemeldete Leistung](#sec-6-2)
  * [6.3 Leistungsnormalisierung](#sec-6-3)
  * [6.4 Zeitliche Paarbildung und Heartbeat-Filter](#sec-6-4)
  * [6.5 Median-Aggregationshierarchie](#sec-6-5)
  * [6.6 Bivariates Auswertungsmodell](#sec-6-6)
  * [6.7 Geografisches Rastering und Projektion](#sec-6-7)
  * [6.8 Evidenzst&auml;rke und Mindest-Schwellen](#sec-6-8)
* [7. Einschr&auml;nkungen](#sec-7)
* [8. Konfigurationsreferenz](#sec-8)
* [9. Bestehende Literatur und Stand der Technik](#sec-9)
* [10. Haftungsausschluss & Lizenz](#sec-10)
* [Anhang A: Paralleler Betrieb mehrerer WSJT-X Instanzen](#sec-a)
* [Anhang B: Single-TX A/B-Umschaltung mit USB-Relay](#sec-b)
* [Anhang C: Referenz-SNR-Kalibrierung](#sec-c)
* [Quellen](#sec-ref)

<a id="sec-2"></a>
### 2. Schnellstart

1. Konfigurationsbereich &ouml;ffnen.
2. `Load Demo` anklicken.
3. Entweder die gew&auml;hlte Demo-Konfiguration laden und pr&uuml;fen, oder die gew&auml;hlte Demo direkt starten.
4. `TX` oder `RX` starten.
5. Zuerst die Karte lesen: Farbe = medianer Segmentwert, Punkte = Stationskategorien, Fu&szlig;balken = **Decode Yield**, also die Decode/No-Decode-Seite der Analyse.
6. Im Segment-Inspektor ein Distanz-/Azimut-Kartensegment ausw&auml;hlen.
7. Eine Station-Insights-Zeile &ouml;ffnen und die Drill-Down-Daten pr&uuml;fen.
8. `Prepare All Results for Download` nutzen, wenn ein vollst&auml;ndiges Reproduzierbarkeitspaket mit Konfiguration, Metadaten, hochaufl&ouml;senden Abbildungen, CSV-Tabellen und kompaktem parquet-Analysecache ben&ouml;tigt wird.

<a id="sec-3"></a>
### 3. Welche Fragen beantwortet WSPRadar?

WSPRadar ist um konkrete Amateurfunk-Fragen herum aufgebaut:

* **Wo wird mein Sendesignal geh&ouml;rt?** `TX Success`.
* **Wen kann meine Station h&ouml;ren?** `RX Success`.
* **Liege ich im Rahmen meiner lokalen WSPR-Nachbarschaft?** `Lokaler Nachbarschafts-Median`, der Standard-Benchmark.
* **Kann ich mit der besten aktiven lokalen Station mithalten?** `Beste lokale Station`, der strenge lokale Stresstest.
* **Wie schneide ich gegen eine bestimmte Station oder einen Funkfreund ab?** `Spezifische Referenzstation`.
* **Hat Antenne A Antenne B am eigenen Standort geschlagen?** `Hardware A/B-Test`, entweder simultan im RX oder mit festem Zeitplan im TX.
* **Sind meine Distanzmuster konsistent mit NVIS- oder DX-Verhalten?** Nahe und weite Distanzringe pr&uuml;fen, aber Distanz nicht als direkte Abstrahlwinkelmessung interpretieren.
* **Bin ich ein Alligator: werde gut geh&ouml;rt, h&ouml;re aber schlecht?** TX- und RX-Ergebnisse gegen dasselbe Referenzkonzept vergleichen und nach Asymmetrien suchen.

<a id="sec-4"></a>
### 4. Analysemodi und valides Experimentdesign

Dieses Kapitel b&uuml;ndelt Nutzerfrage, Analysekonzept und Experimentdesign. Gemeinsame Mathematik und Annahmen werden einmal in [Wissenschaftliche Methodik und Annahmen](#sec-6) erkl&auml;rt.

<a id="sec-4-0"></a>
#### 4.0 Begriffe und Vergleichslogik

* **Ziel / Target** meint die Station oder das Setup unter Test: normalerweise das eigene Rufzeichen, Setup A oder die Station, die bewertet werden soll.
* **Referenz** meint die Vergleichsbasis: ein Buddy-Rufzeichen, die lokale Nachbarschaft, die beste lokale Station oder Setup B.
* Ein **WSPR-Spot** ist ein gemeldeter erfolgreicher Decode: Zeit, Band, Sender, Empf&auml;nger, Locator, gemeldete Leistung und SNR.
* Ein **WSPR-Zyklus** ist eine zweimin&uuml;tige WSPR-Sende-/Empfangsgelegenheit, ausgerichtet an geraden UTC-Minuten.
* Ein **target-aktiver WSPR-Zyklus** ist ein WSPR-Zyklus, in dem die Zielstation bzw. das Ziel-Setup nachweislich aktiv war. In der TX-Analyse muss das Zielsignal weltweit von mindestens einer Station decodiert worden sein. In der RX-Analyse muss der Ziel-Empf&auml;nger in diesem Zyklus mindestens einen Decode hochgeladen haben.
* Ein **Maidenhead-Locator** ist der von WSPR genutzte Grid-Square-Standortcode; WSPRadar nutzt den eigenen QTH-Locator als Kartenzentrum.
* Ein **Median** ist der mittlere Wert einer sortierten Stichprobe. WSPRadar nutzt Mediane, weil sie robuster gegen Ausrei&szlig;er und wechselnde Ausbreitungszust&auml;nde sind als einfache Mittelwerte.
* **Joint / Synced** Evidenz bedeutet, dass Ziel und Referenz vergleichbare Evidenz f&uuml;r dieselbe Remote-Station und denselben Ausbreitungspfad im selben WSPR-Zyklus haben oder, bei sequenziellem TX A/B, im selben validen Zeit-Bin.
* **Delta SNR** bedeutet SNR des Ziels minus SNR der Referenz. In Vergleichskarten spricht positives Delta SNR f&uuml;r das Ziel; negatives Delta SNR spricht f&uuml;r die Referenz.
* **Decode Yield** ist die Decode/No-Decode-Seite des Vergleichs: gemeinsame Evidenz, Nur-Ziel-Evidenz, Nur-Referenz-Evidenz und Async-Evidenz innerhalb der relevanten heartbeat-gefilterten Vergleichszyklen.
* Der **Heartbeat-Filter** sch&uuml;tzt Decode Yield gegen Offline-Bias: WSPRadar z&auml;hlt nur **target-aktive Zyklen**, also WSPR-Zyklen, in denen das Ziel nachweislich aktiv war. [Abschnitt 6.4](#sec-6-4) definiert das pr&auml;zise f&uuml;r TX und RX.
* **System Sensitivity** ist die UI-Bezeichnung f&uuml;r Decode Yield. Das ist keine kalibrierte Empf&auml;ngerempfindlichkeitsmessung.
* **Station Medians (Delta SNR)** ist die UI-Bezeichnung f&uuml;r die stationsbalancierte gepaarte Delta-SNR-Verteilung. Das ist keine RF-Verst&auml;rkerlinearit&auml;t.

**Standardempfehlungen f&uuml;r alle Modi**

* Korrektes Rufzeichen und korrekten Maidenhead-Locator verwenden.
* Ein Zeitfenster w&auml;hlen, das die relevanten Ausbreitungszust&auml;nde abdeckt; mehrt&auml;gige Zeitfenster sind st&auml;rker, wenn die Aussage vollst&auml;ndige t&auml;gliche ionosph&auml;rische Zyklen betreffen soll.
* Stationskonfiguration im Analysefenster stabil halten, au&szlig;er bei der bewusst getesteten Variable.
* Bei TX-Analysen Sender, Antennen-/Speiseleitungs-/Tunerpfad, Leistungsregelung, Zeitplan und gemeldete Leistung stabil halten, sofern sie nicht die getestete Variable sind; einen realistischen Leistungswert melden.
* Bei RX-Analysen Empf&auml;nger, Antennen-/Speiseleitungspfad, Audiopfad, Decoder-Einstellungen und Upload-Verhalten stabil halten, sofern sie nicht die getestete Variable sind.

<a id="sec-4-1"></a>
#### 4.1 TX/RX-Erfolgsrate

**Antwortet auf**

* `RX Success` / **RX-Erfolgsrate:** Wie oft hat mein Empf&auml;nger, das Target, in target-aktiven WSPR-Zyklen ein WSPR-Signal empfangen und decodiert, das unabh&auml;ngig von einem anderen Empf&auml;nger irgendwo anders auf der Welt best&auml;tigt wurde?
* `TX Success` / **TX-Erfolgsrate:** Wie oft haben RX-Stationen in target-aktiven WSPR-Zyklen meinen Sender, das Target, decodiert, wenn diese RX-Stationen durch eigene Nicht-Target-WSPR-Decodes auf demselben Band aktiv nachgewiesen waren?
* Das sind bedingte, opportunity-basierte Raten. Sie reduzieren den Aktivit&auml;ts-, Ausbreitungs- und Successful-Decode-Bias, der rohe Coverage- oder SNR-Karten schwer interpretierbar machte.

**Funktionsweise**

WSPRadar verwendet exakte zweimin&uuml;tige UTC-WSPR-Zyklen und beh&auml;lt nur Zyklen, in denen die konfigurierte Zielstation nachweislich aktiv war. Ein Peer ist eine exakte Identit&auml;t aus `Rufzeichen + gemeldetem Locator`.

F&uuml;r jeden target-aktiven Zyklus und Peer:

* **Target (`T`)**: Die Zielstation bzw. das Ziel-Setup hat den relevanten Peer im target-aktiven Zyklus best&auml;tigt.
* **Elsewhere (`E`, RX Success)**: Dieselbe sendende Remote-Station wurde im selben Zyklus irgendwo anders im RX-Netzwerk geh&ouml;rt, aber nicht vom Target-Empf&auml;nger.
* **Other Signals (`OS`, TX Success)**: Eine aktive RX-Station hat in diesem target-aktiven Zyklus andere WSPR-Decodes auf demselben Band hochgeladen, aber den Target-Sender nicht decodiert.
* **Target-only**: Das Target hat die Station ohne unabh&auml;ngige Gegen-Evidenz beobachtet. Diese Zeilen bleiben Audit-Evidenz, gehen aber nicht in `Target`, `Elsewhere`, `Other Signals` oder den Erfolgsraten-Nenner ein.
* **Erfolgsrate:** RX nutzt `Target/(Target+Elsewhere)`. TX nutzt `Target/(Target+Other Signals)`.

Die Richtung der Evidenz h&auml;ngt vom Modus ab:

* Bei **RX Success** ist der Peer eine sendende Station. Der Kartentitel lautet `Target {Rufzeichen} vs. Same Signals Heard Elsewhere`: Hat der Target-Empf&auml;nger Signale geh&ouml;rt, deren Existenz das Netzwerk anderswo belegt?
* Bei **TX Success** ist der Peer eine empfangende Station. Der Kartentitel lautet `Target {Rufzeichen} vs. Other Signals at Active RX Stations`: Hat ein aktiver Empf&auml;nger, der WSPR-Verkehr h&ouml;rte, den Target-Sender geh&ouml;rt oder nur andere Signale?

In `RX Success` kann eine sendende Station in die Kandidatenmenge gelangen, wenn dasselbe Signal im selben target-aktiven WSPR-Zyklus anderswo decodiert wurde. Bei einem ausreichend langen RX-Lauf kann diese Kandidatenmenge gegen alle weltweit aktiven Sender auf diesem Band wachsen, w&auml;hrend der Ziel-Empf&auml;nger aktiv war, einschlie&szlig;lich Sendern, die der Ziel-Empf&auml;nger nie decodiert hat.

In `TX Success` kann ein Empf&auml;nger in die Kandidatenmenge gelangen, wenn er in einem target-aktiven WSPR-Zyklus irgendeinen WSPR-Decode auf demselben Band hochgeladen hat. Bei einem ausreichend langen TX-Lauf kann diese Kandidatenmenge gegen alle weltweit aktiven WSPR-Empf&auml;nger auf diesem Band w&auml;hrend deiner Sendezyklen wachsen, einschlie&szlig;lich Empf&auml;ngern, die dich nie decodiert haben.

Raten werden zuerst pro Stationsidentit&auml;t berechnet. Eine Station tr&auml;gt erst dann zu Karte, Segment-Zusammenfassung und Station Insights bei, wenn sie die konfigurierte Mindestzahl best&auml;tigter Gegen-Evidenz erreicht: `Target+Elsewhere` in RX Success oder `Target+Other Signals` in TX Success. Ein Kartensegment zeigt das arithmetische Mittel der beitragenden Stations-Erfolgsraten, sodass jede qualifizierte Station gleich gewichtet wird. Segment Insight zeigt zus&auml;tzlich die Beobachtungsebene `sum(Target) / sum(Target+Gegen-Evidenz)`, die jede best&auml;tigte Beobachtung gleich gewichtet und daher von volumenstarken Stationen dominiert werden kann.

**Vorsicht bei**

* Die Rate ist auf extern best&auml;tigte Peer-Aktivit&auml;t bedingt; sie ist nicht die Wahrscheinlichkeit, jede m&ouml;glicherweise erfolgte Aussendung zu decodieren.
* Externe Evidenz best&auml;tigt Endpunkt-Aktivit&auml;t, nicht dass der Ausbreitungspfad zwischen Ziel und Peer offen war. Das Ergebnis enth&auml;lt bewusst Ausbreitung, Pfadgeometrie und Stationssystem-Performance.
* WSPR liefert kein autoritatives Sendelog. Bei TX Success ist eine Ziel-Aussendung, die niemand decodiert, nicht beobachtbar und kann deshalb kein Other-Signals-Fall werden.
* Target-only-Evidenz bleibt in den internen Auditdaten erhalten, wird aber in prim&auml;rer Karte, Zusammenfassung und Station Insights ausgeblendet, weil sie weder `Target` noch Gegen-Evidenz ist. Ihre Aufnahme in den Nenner w&uuml;rde die Metrik vom eigenen Erfolg abh&auml;ngig machen.
* TX/RX-Success-Analysen ben&ouml;tigen genau ein Band. `Band = All` wird bewusst abgelehnt, weil Zyklen und Beobachtbarkeit bandspezifisch sind.
* Die Zielidentit&auml;t wird &uuml;ber exaktes Rufzeichen und den 4-stelligen Locator des konfigurierten QTH abgeglichen. Falsche oder wechselnde Locator-Uploads k&ouml;nnen daher g&uuml;ltige Zyklen entfernen oder Stationsidentit&auml;ten vermischen.
* Die Query verwendet g&uuml;ltige WSPR-Spots mit `code = 1`. Bei &auml;lteren historischen Daten kann die Vollst&auml;ndigkeit dieses Felds abweichen; langfristige historische Vergleiche deshalb vorsichtig interpretieren.
* RX-Ergebnisse beschreiben weiterhin das gesamte Empfangssystem, TX-Ergebnisse den gesamten Sende-/Netzwerkpfad. Keine der Raten ist eine Labor-Antennengewinnmessung.


<a id="sec-4-2"></a>
#### 4.2 Lokaler Nachbarschafts-Benchmark

Der lokale Nachbarschafts-Benchmark fragt, wie die eigene Station gegen aktive WSPR-Stationen innerhalb eines gew&auml;hlten geografischen Radius abschneidet. Der Radius gilt f&uuml;r beide lokalen Methoden.

Alle lokalen Nachbarschaftsvergleiche bleiben target-aktive Vergleiche. WSPRadar begrenzt die Analyse zuerst auf WSPR-Zyklen, in denen die eigene Station/das eigene Setup nachweislich aktiv war; [Zeitliche Paarbildung und Heartbeat-Filter](#sec-6-4) definiert das pr&auml;zise f&uuml;r TX und RX. Lokale Referenz-Evidenz au&szlig;erhalb dieser target-aktiven Zyklen wird bewusst ignoriert. Deshalb ist der lokale Benchmark-Yield keine rohe Z&auml;hlung aller Nachbarschaftsaktivit&auml;t im Zeitfenster.

**Lokaler Nachbarschafts-Median: Standard-Baseline**

F&uuml;r jeden WSPR-Zyklus und passenden Remote-Pfad berechnet WSPRadar den Median des normierten SNR aller aktiven lokalen Referenzstationen innerhalb des Radius. Die eigene Station wird gegen diesen zyklusbezogenen Nachbarschaftsmedian verglichen.

* Beste erste Antwort auf: **Bin ich f&uuml;r meine Region im Rahmen?**
* Robust gegen eine einzelne ungew&ouml;hnlich starke oder schwache lokale Station.
* Erfindet keine Werte f&uuml;r fehlende Spots. Wenn ein Nachbar in einem Zyklus nicht decodiert hat oder nicht decodiert wurde, wird das nicht als `0 dB` gez&auml;hlt.
* Bei gerader Anzahl lokaler Referenzstationen wird der Mittelpunkt-Median verwendet.
* Der Referenzpool kann sich zyklusweise &auml;ndern, weil WSPR-Aktivit&auml;t zyklusweise schwankt.
* Yield-Kategorien werden nur innerhalb target-aktiver WSPR-Zyklen bewertet. `Nur Referenz` bedeutet daher: Die lokale Referenzseite hatte in einem Zyklus, in dem die eigene Station/das eigene Setup irgendwo aktiv war, Evidenz f&uuml;r diesen Peer/Pfad, aber nicht gemeinsam auf genau diesem Peer/Pfad.

**Beste lokale Station: strenger Stresstest**

F&uuml;r jeden WSPR-Zyklus und passenden Remote-Pfad vergleicht WSPRadar gegen die st&auml;rkste aktive lokale Station im Radius.

* Beste Antwort auf: **Kann ich mit dem st&auml;rksten aktiven lokalen Peer mithalten?**
* Dies ist eine Best-Local-Peer-H&uuml;llkurve, kein Nachbarschaftsdurchschnitt.
* Die Identit&auml;t der Referenzstation kann von Zyklus zu Zyklus wechseln.
* Der Benchmark ist absichtlich schwerer zu schlagen als der Nachbarschaftsmedian.
* Yield-Kategorien werden nur innerhalb target-aktiver WSPR-Zyklen bewertet. `Nur Referenz` bedeutet daher: Die beste lokale Referenzseite hatte in einem Zyklus, in dem die eigene Station/das eigene Setup irgendwo aktiv war, Evidenz f&uuml;r diesen Peer/Pfad, aber nicht gemeinsam auf genau diesem Peer/Pfad.

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
* Yield im Buddy-Test ist ebenfalls heartbeat-gefiltert. Er vergleicht nicht alle Spots beider Rufzeichen &uuml;ber das gesamte Zeitfenster. Er vergleicht Joint-, Target-only-, Reference-only- und Async-Evidenz innerhalb von Zyklen, in denen das Zielrufzeichen/das Zielsetup nachweislich aktiv war.

**Valides Design**

* Eine Referenzstation w&auml;hlen, deren Standort, Antenne, Leistung und Betriebsplan bekannt sind.
* Gleiches Band und &uuml;berlappende Zeitfenster verwenden.
* Sicherstellen, dass beide Rufzeichen gen&uuml;gend gleiche Remote-Peers im selben Zyklus teilen.

**Vorsicht bei**

* Ein Buddy-Test ist ein Stationssystem-Vergleich, keine reine Antennengewinnmessung.
* Unterschiede k&ouml;nnen Antenne, Sender, Empf&auml;nger, Speiseleitung, Gel&auml;nde, Polarisation, lokales QRM und Genauigkeit der gemeldeten Leistung enthalten.
* Das Tauschen von Ziel- und Referenzrufzeichen kann die Yield-Zahlen ver&auml;ndern. Das Active-Cycle-Gate folgt dem Zielrufzeichen, deshalb m&uuml;ssen A gegen B und B gegen A nicht symmetrisch sein. Delta-SNR-Vorzeichen sollten sich auf gemeinsamer Joint-Evidenz umkehren, Yield-Kategorien aber nicht zwingend.

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

Setup A und Setup B k&ouml;nnen mit demselben Rufzeichen nicht gleichzeitig senden. WSPRadar nutzt daher deterministisches UTC-WSPR-Frame-Time-Slicing. Ein Sender, Controller oder RF-Umschaltsystem weist ein Setup oder einen RF-Pfad WSPR-2-Frames mit UTC-Startminute 00, 04, 08, ... und das andere Setup oder den anderen RF-Pfad Frames mit UTC-Startminute 02, 06, 10, ... zu. Das Tool gruppiert Daten in Zeit-Bins, berechnet je Setup oder RF-Pfad einen Mikro-Median im Bin und daraus den Bin-Delta.

Das kontrollierteste TX-A/B-Design nutzt meist einen einzelnen Sender und schaltet nur den RF-Pfad zwischen zwei Antennen um. In diesem Design bleiben Sender, Rufzeichen, WSPR-Software, Frequenz, Leistungseinstellung und Uhr gemeinsam. Die beabsichtigten experimentellen Variablen sind dann die geschalteten Speiseleitungs-/Antennenpfade, nicht zwei getrennte Sendeketten. Das ist sicherer und wissenschaftlich sauberer als der Vergleich zweier unabh&auml;ngiger Sender, weil Senderkalibrierung, Frequenzstabilit&auml;t, Audioansteuerung, Leistungsangabe und Timing-Verhalten als wesentliche Konfounder entfernt werden.

WSPRadar enth&auml;lt daf&uuml;r das plattform&uuml;bergreifende Hilfswerkzeug `tools/Timed-AB-Relay-Switch`. Es schaltet ein unterst&uuml;tztes USB-HID-Relay im selben UTC-WSPR-Frame-Takt, den auch die App nutzt, und verwendet den Python-HID-Stack unter Windows, Linux und macOS. Das USB-Relay kann wiederum einen geeigneten RF-Antennenschalter steuern, zum Beispiel einen 1-zu-2-RF-Schalter wie den QRO.cz 1-to-2 RF Switch, sofern Relay-Ausgang, RF-Schalter-Steuereingang, Steuerspannung, Strombelastbarkeit, Polarit&auml;t und Stations-Interlock elektrisch geeignet ausgelegt sind.

* Ausgangsleistung, Speiseleitung, Tuner-Einstellungen, Band und Zeitplan konstant halten, au&szlig;er bei der getesteten Variable.
* Einen Single-Transmitter-RF-Pfadschalter bevorzugen, wenn das Ziel ein Antennen-/Speiseleitungs-A/B-Test ist.
* Relay-zu-RF-Schalter-Polarit&auml;t vor RF-Betrieb verifizieren: Target-WSPR-Frames m&uuml;ssen die beabsichtigte Testantenne / den Testpfad w&auml;hlen, Reference-WSPR-Frames die beabsichtigte Referenzantenne / den Referenzpfad.
* Ein QMX-Transceiver oder externer Relay-Controller l&auml;sst sich beispielsweise mit deterministischem Timing wie UTC-Startminutenfolge 00/04/08 f&uuml;r Setup A/Pfad A und 02/06/10 f&uuml;r Setup B/Pfad B programmieren.
* Hardware nur zwischen vollst&auml;ndigen WSPR-2-Sendeframes umschalten; nicht w&auml;hrend einer zweimin&uuml;tigen WSPR-Sendung.
* Standard-WSJT-X mit zuf&auml;lligem Sendemuster ist ohne Zusatzsteuerung nicht f&uuml;r fixed-schedule TX A/B geeignet.

**Vorsicht bei TX-Suffixen**

Warum keine Multi-Cycle-WSPR-Suffixe f&uuml;r Single-TX A/B? Compound-Rufzeichen k&ouml;nnen Multi-Message-Verhalten erzwingen und den Decode Yield senken, weil nicht alle Empf&auml;nger alle ben&ouml;tigten Nachrichtentypen gleich zuverl&auml;ssig decodieren. K&uuml;nstliche Suffixe wie `/1` oder `/2` k&ouml;nnen je nach Land unzul&auml;ssig sein. `/P` sollte nur verwendet werden, wenn es f&uuml;r den tats&auml;chlichen Betrieb rechtlich passt. F&uuml;r TX A/B bevorzugt WSPRadar deshalb feste WSPR-Frame-Startminuten mit normalem Rufzeichen.

**Wissenschaftliche Vorsicht**

Sequenzieller TX ist zeitgebinnt, nicht simultan. Mehrt&auml;giges fixes Timing reduziert Zeitkonfundierung deutlich, beweist aber nicht, dass jeder zeitkorrelierte Effekt verschwunden ist.

<a id="sec-4-5"></a>
#### 4.5 Decode Yield in Vergleichsmodi

**Decode Yield** ist eine unterst&uuml;tzende Metrik in Vergleichsmodi, kein eigener Analysemodus. Er fasst zusammen, was innerhalb heartbeat-gefilterter, target-aktiver Vergleichszyklen passiert ist.

**Funktionsweise**

* `Joint` / `Beide (Sync)`: Ziel und Referenz haben Evidenz f&uuml;r denselben Peer/Pfad im selben WSPR-Zyklus. Das ist valide gepaarte Evidenz f&uuml;r Delta SNR.
* `Nur Zielstation`: innerhalb eines target-aktiven Zyklus hatte die Zielseite Evidenz f&uuml;r diesen Peer/Pfad, die Referenzseite nicht.
* `Nur Referenz`: innerhalb eines target-aktiven Zyklus hatte die Referenzseite Evidenz f&uuml;r diesen Peer/Pfad, die Zielseite nicht.
* `Beide (Async)`: im ausgew&auml;hlten Segment/Stationssatz haben beide Seiten Evidenz, aber nicht im selben WSPR-Zyklus. Das ist n&uuml;tzlicher Yield-Kontext, aber keine gepaarte Delta-SNR-Evidenz.
* `Nur Referenz = 0` kann ein korrektes Ergebnis sein. Es bedeutet, dass innerhalb der target-aktiven Vergleichszyklen und gew&auml;hlten Filter keine Nur-Referenz-Evidenz &uuml;brig blieb, nicht dass die Referenzstation im gesamten Zeitfenster keine WSPR-Aktivit&auml;t hatte.
* Das Tauschen von Ziel und Referenz kann Yield-Zahlen ver&auml;ndern, weil das Active-Cycle-Gate dem Ziel folgt. A gegen B und B gegen A m&uuml;ssen daher im Yield nicht symmetrisch sein, selbst wenn gemeinsames Joint-Delta-SNR erwartungsgem&auml;&szlig; das Vorzeichen wechselt.

**Interpretation**

* Decode Yield hilft, Decode/No-Decode-Verhalten an der Reichweitengrenze zu verstehen.
* Delta SNR bleibt das wichtigste gepaarte Performance-Signal, wenn gen&uuml;gend Joint-Evidenz existiert.
* Yield ist heartbeat-gefilterte operative Reichweite, keine normalisierte Antenneneffizienz und keine kalibrierte Empf&auml;ngerempfindlichkeit.
* `SPOTS` als Decode-Volumenverteilung und `STATIONS` als Footprint-Breite lesen. Diese Balken sind wichtig, weil Delta SNR allein Decode/No-Decode-Verhalten verbergen kann.

<a id="sec-5"></a>
### 5. Ergebnisbegriffe und Oberfl&auml;che lesen

<a id="sec-5-1"></a>
#### 5.1 Karte

**Heatmap-Segmente**

TX/RX-Success-Modi zeigen pro Segment die mittlere Stations-Erfolgsrate: RX nutzt `Target/(Target+Elsewhere)`, TX nutzt `Target/(Target+Other Signals)`. Karte und zeitliche Ratenpanels verwenden dieselbe feste nichtlineare Skala mit semantischen Low-End-Bins: schwarze Kartenfelder bedeuten keine Target/Gegen-Evidenz, Lila bedeutet exakt `0%`, die erste Nicht-Null-Farbe bedeutet `>0%`, danach l&auml;uft die Skala mit `1, 2, 5, 10, 20, 40, 60, 80, 100%` weiter. Dadurch bleiben niedrige Raten differenzierbar und Farben verschiedener Success-Analysen direkt vergleichbar. Vergleichsmodi zeigen medianen Delta SNR gegen den gew&auml;hlten Benchmark. Positive Delta-SNR-Werte bedeuten, dass die eigene Station/das eigene Setup im Segment st&auml;rker als die Benchmark ist; negative Werte zeigen schw&auml;chere Performance. WSPRadar nutzt die g&auml;ngige Amateurfunk-Konvention `1 S-Stufe = 6 dB`.

**Distanzringe**

Nahe Ringe k&ouml;nnen mit Short-Skip oder NVIS konsistent sein; weite Ringe k&ouml;nnen mit flacherem DX-Verhalten konsistent sein. Distanz ist keine direkte Elevationswinkelmessung, weil ionosph&auml;rischer Modus, Band, Zeit, Saison und Sonnenzustand mitwirken.

**Punkte**

In TX/RX-Success-Modi werden nur Stationen dargestellt, die den Mindestwert best&auml;tigter Target/Gegen-Evidenz erreichen. `T (Target)`-Stationen besitzen mindestens eine Target-Beobachtung und werden mit steigender Target-Zahl heller gr&uuml;n dargestellt. RX-Zero-Target-Stationen werden als `E (Elsewhere)` gelabelt; TX-Zero-Target-Stationen als `OS (Other Signals)`. Beide werden hellgrau dargestellt. Stationen unterhalb der Evidenzschwelle und Target-only-Beobachtungen erscheinen nicht auf der Karte. In Vergleichsmodi gilt: Gr&uuml;n = Joint Decodes im selben Zyklus, gelb-orange = beide Seiten haben die Station geh&ouml;rt, aber asynchron, violett = nur eigene Station/eigenes Setup, wei&szlig; = nur Referenz.

Die Punktkategorien der Vergleichsmodi verwenden die heartbeat-gefilterten Evidenzklassen aus [Decode Yield in Vergleichsmodi](#sec-4-5).

**Footer und 1D-Venn-Balken**

In TX/RX-Success-Modi nennt der Footer die modus-spezifische Mindestzahl best&auml;tigter Beobachtungen pro Station, die Zahl qualifizierter Stationen und ob die Segmentfarben die mittlere Stationsrate `Target/(Target+Elsewhere)` f&uuml;r RX oder `Target/(Target+Other Signals)` f&uuml;r TX darstellen. In Vergleichsmodi zeigen `SPOTS` und `STATIONS` Decode-Volumenverteilung und Footprint-Breite; diese Balken sind wichtig, weil Delta SNR allein Decode/No-Decode-Verhalten verbergen kann.

Die Footer-Balken visualisieren die Decode-Yield-Kategorien aus [Decode Yield in Vergleichsmodi](#sec-4-5). In Vergleichsmodi sind sie heartbeat-gefiltert und keine Rohz&auml;hler der gesamten Aktivit&auml;t im Zeitfenster.

<a id="sec-5-2"></a>
#### 5.2 Segment Insight - TX/RX-Erfolg

**Segment-Inspektor**

Der Segment-Inspektor ist die Auditschicht unterhalb der Karten. Ein oder mehrere Distanzbereiche und Himmelsrichtungen lassen sich ausw&auml;hlen, um die Evidenz hinter diesem Kartenausschnitt zu pr&uuml;fen.

In TX/RX-Success-Modi fasst der **Segment Insight** Block das ausgew&auml;hlte Segment als Target und modus-spezifische Gegen-Evidenz zusammen. RX nutzt `Elsewhere`; TX nutzt `Other Signals`. Danach folgen zwei klar benannte Erfolgsraten: **Stationsmittel**, der Mittelwert der einzelnen Stationsraten, und **Beobachtungsebene**, `sum(Target) / sum(Target+Gegen-Evidenz)`.

**Erfolgsraten-Panels**

* Das obere Panel zeigt Stationen mit mindestens einer Target-Beobachtung gegen ihre best&auml;tigte Target/Gegen-Evidenz auf einer log2-x-Achse. Die Tick-Beschriftung zeigt die echten Evidenzzahlen statt Zweierpotenzen. Zero-Target-Stationen werden hier ausgeblendet, weil sie immer bei 0 Prozent liegen und gegen&uuml;ber den Gegen-Evidenz-Zahlen und Zeitpanels wenig Zusatzinformation liefern.
* Das untere linke Zeitpanel zeigt die **Mittlere Stations-Erfolgsrate** jeder Distanz-/Zeitzelle. Zuerst wird `Target/(Target+Gegen-Evidenz)` pro beitragender Station berechnet, danach werden diese Stationsraten gemittelt.
* Das untere rechte Zeitpanel zeigt die **Erfolgsrate auf Beobachtungsebene** derselben Zelle: `sum(Target) / sum(Target+Gegen-Evidenz)`. Eine Differenz zwischen beiden Panels zeigt, dass volumenstarke Stationen das beobachtungsgewichtete Ergebnis vom gleichgewichteten Stationsmittel wegziehen.
* Beide Zeitpanels verwenden dieselbe feste nichtlineare Erfolgsratenskala wie die Karte, eine gemeinsame Farbskala und identische Distanz-/Zeitachsen. Die Distanz wird an den Ring&uuml;berg&auml;ngen `2500`, `5000`, `10000`, `15000` und `20000 km` beschriftet, statt lange Bereichslabels zu verwenden. Zeitbins sind l&uuml;ckenlos, am exakt gew&auml;hlten Analysebeginn verankert und reichen bis zum Analyseende; leere Bins bleiben leer sichtbar, statt zu verschwinden. Die Tick-Labels verwenden ein f&uuml;r die angezeigte Dauer gew&auml;hltes regelm&auml;&szlig;iges, uhrzeitstabiles Intervall, zum Beispiel alle 6 oder 12 Stunden, statt die Labels nach den zuf&auml;llig mit Daten gef&uuml;llten Bins zu verteilen.

<a id="sec-5-3"></a>
#### 5.3 Segment Insight - Vergleichsmodi

Vergleichsmodi sch&auml;tzen Delta SNR gegen ein Referenzkonzept, nicht eine Target/Gegen-Evidenz-Erfolgsrate. Ihr Segment Insight beh&auml;lt deshalb die bivariate Vergleichsansicht bei: Decode Yield / System Sensitivity, stationsbalancierte Delta-SNR-Mediane und rohe Spot-/Bin-Delta-SNR-Evidenz.

* Das linke Panel, **System Sensitivity**, fasst heartbeat-gefilterten Decode Yield zusammen: Joint-Evidenz, Target-only-Evidenz, Reference-only-Evidenz und Async-Evidenz innerhalb target-aktiver Vergleichszyklen.
* Das mittlere Panel, **Station Medians (Delta SNR)**, zeigt die stationsbalancierte Verteilung. Jede beitragende Station hat &uuml;ber ihren Stationsmedian gleiches Gewicht.
* Das rechte Panel zeigt die rohe gepaarte Evidenzverteilung: `Joint-Spot Delta SNR` in Same-Cycle-Vergleichsmodi oder `Paired Spot Bin Delta SNR` im sequenziellen TX-A/B.
* Positives Delta SNR spricht f&uuml;r das Target. Negatives Delta SNR spricht f&uuml;r die Referenz. Die rote gestrichelte Medianlinie und das 90%-Stabilit&auml;tsintervall fassen das ausgew&auml;hlte Segment zusammen.
* Vergleichsmodus-Verteilungspanels nutzen Prozent-Histogramme f&uuml;r Delta SNR. Dadurch bleibt quantisierte WSPR-SNR-Evidenz sichtbar, ohne sie zu einer kontinuierlichen Dichteform zu gl&auml;tten.
* SNR-Histogramm-Bins sind pro Panel global fest und decken den vollen sichtbaren Bereich mit h&ouml;chstens 40 Balken ab. WSPRadar nutzt standardm&auml;&szlig;ig 1,0-dB-Bins, wechselt nur bei klarer HalbdB-Struktur der Werte auf 0,5-dB-Bins und aggregiert breite Bereiche bei Bedarf auf 1, 2, 3, 6 oder 10 dB.
* WSPRadar zeigt ein `90% Stability`-Intervall f&uuml;r stationsbezogene Mediane und ausgew&auml;hlte Evidenz. Das ist ein Bootstrap-/Resampling-Stabilit&auml;tsintervall um den Median, kein formaler Signifikanznachweis. In den oberen Segmentplots wird die rote gestrichelte Medianlinie durch den echten 90%-Stabilit&auml;tsbereich hinterlegt; Intervalle mit nahezu Nullbreite werden als Linie dargestellt und nicht k&uuml;nstlich zu einem Band verbreitert. SNR- und Delta-SNR-Panels nutzen mindestens 3 dB sichtbare y-Achsen-Spanne, damit winzige numerische Variation nicht visuell vergr&ouml;&szlig;ert wird.

<a id="sec-5-4"></a>
#### 5.4 Station Insights und ausgew&auml;hlte Stations-Evidenz

**Station-Insights-Tabelle**

Die Station-Insights-Tabelle listet die Stationen, die zum ausgew&auml;hlten Segment beitragen, und erlaubt die Auswahl der Evidenz f&uuml;r die tiefere Pr&uuml;fung.

* In TX/RX-Success-Modi listen Station Insights schwellenqualifizierte Stationsidentit&auml;ten mit Distanz, Azimut, `Target`, modus-spezifischer Gegen-Evidenz, Erfolgsrate und medianem Target-SNR. RX nutzt `Elsewhere`; TX nutzt `Other Signals`. Zero-Target-Stationen sind standardm&auml;&szlig;ig ausgeblendet und k&ouml;nnen mit `Zero-Target-Stationen zeigen` eingeblendet werden. Sortiert wird absteigend nach `Target`, danach Gegen-Evidenz und Erfolgsrate.
* In Vergleichsmodi listet Station Insights beteiligte Remote-Stationen, trennt Joint Decodes von exklusiven Decodes und zeigt den stationsbezogenen medianen Delta SNR. `Show Non-Joint` zeigt isolierte Decodes. Fehlendes SNR wird als `None`, nicht als `0.0`, angezeigt. Wenn beide Setups eine Station h&ouml;ren, aber nie im selben WSPR-Zyklus, kann der Yield-Chart `Beide (Async)` zeigen.
* Wenn keine Station-Insights-Zeile ausgew&auml;hlt ist, &ouml;ffnet WSPRadar standardm&auml;&szlig;ig die evidenzst&auml;rkste Zeile: in Vergleichsmodi die Zeile mit den meisten Joint Spots oder Joint Bins, in TX/RX-Success-Modi die erste nach `Target`, Gegen-Evidenz und Erfolgsrate sortierte Zeile.

**Ausgew&auml;hlte Stations-Evidenz**

Die Auswahl einer oder mehrerer Station-Insights-Zeilen f&uuml;gt oberhalb der Drill-Down-Tabelle einen zweiteiligen Evidenzblock ein.

* In TX/RX-Success-Modi verwendet die Evidenzgrafik der ausgew&auml;hlten Stationen zwei vergr&ouml;&szlig;erte Panels: gestapelte Target-/Gegen-Evidenz-Zahlen mit der Erfolgsrate &uuml;ber der Zeit sowie Target-SNR. Target und Gegen-Evidenz werden nach der beobachtungsbezogenen Great-Circle-Pfadbeleuchtung aufgeteilt: night, greyline/mixed und daylight. Das Target-SNR-Histogramm verwendet dieselben Beleuchtungsklassen f&uuml;r erfolgreiche Target-Beobachtungen. Die Erfolgsraten-Achse reicht bis 10 Prozent oberhalb des gr&ouml;&szlig;ten sichtbaren Werts, begrenzt auf 100 Prozent, statt immer den gesamten Bereich von 0 bis 100 Prozent zu reservieren. Die Zeitreihe verwendet l&uuml;ckenlose, am exakten Analysebeginn verankerte Bins.
* In Vergleichsmodi zeigt der ausgew&auml;hlte Evidenzblock ein horizontales Prozent-Histogramm der ausgew&auml;hlten Evidenz und eine Zeit-Heatmap. Das Histogramm h&auml;lt die SNR- oder Delta-SNR-Achse mit der Heatmap ausgerichtet. Die Heatmap aggregiert alle ausgew&auml;hlten Zeilen in ganzzahlige SNR- oder Delta-SNR-Dichtezellen, legt Medianmarker dar&uuml;ber und verbindet benachbarte Mediane nur, wenn beide benachbarten Bins mindestens drei Punkte enthalten. Das Verteilungspanel bleibt roh, damit die vollst&auml;ndige ausgew&auml;hlte Evidenzpopulation sichtbar bleibt.
* Die Zeitbin-Auswahl wirkt nur auf das ausgew&auml;hlte Zeitpanel. Die verf&uuml;gbaren UTC-Binbreiten passen sich an die Dauer der ausgew&auml;hlten Evidenz an: kurze Fenster verwenden Minuten-Bins, lange Fenster verwenden Stunden-Bins. Bei TX/RX-Success-Target/Gegen-Evidenz-Zeitreihen richten sich die Optionen nach dem vollst&auml;ndigen Analyseintervall, damit d&uuml;nn besetzte Stationen nicht versehentlich Tausende winziger leerer Bins erzeugen. Die Standardauswahl f&uuml;r lange Fenster ist `1h`, `3h`, `6h`, `12h` und `24h`, und WSPRadar startet mit der zweitfeinsten verf&uuml;gbaren Binbreite.

**Drill-Down-Tabelle**

Die Drill-Down-Tabelle ist die zeilenbasierte Auditschicht f&uuml;r alle Modi. Sie zeigt Beobachtungen, Paare oder Zeit-Bins hinter einer Station-Insights-Zeile, damit Segment- und Stationsmediane gegen die zugrunde liegende Evidenz gepr&uuml;ft werden k&ouml;nnen.

In TX/RX-Success-Modi bleibt jede Drill-Down-Zeile intern eine target-aktive Stations-Zyklus-Beobachtung, klassifiziert als Target, Gegen-Evidenz oder Target-only, mit den zugeh&ouml;rigen Audit-Flags und Target-SNR, sofern vorhanden. In normalen Same-Cycle-Vergleichsmodi zeigt der Drill-Down die gepaarten Spot-Level-Vergleiche, die in den Stationsmedian eingehen.

F&uuml;r die Median-Nachbarschaftsmethode wird der Referenzpool expandiert. Statt nur eine generische `Ref Pool`-Zeile zu zeigen, listet die Tabelle die einzelnen lokalen Referenzstationen dieses Zyklus, ihren Locator, ihre Distanz, ihr normiertes Referenz-SNR, den aggregierten Nachbarschaftsmedian des Zyklus, das eigene SNR und den resultierenden Delta SNR. So l&auml;sst sich der Median direkt nachvollziehen.

F&uuml;r TX A/B zeigt der Drill-Down Zeitfenster statt Same-Cycle-Paare. Sichtbar sind `Micro-Med A`, `Micro-Med B` und der resultierende Bin-Delta. Gegenseitige Mikromediane werden in Single-Setup-Zeilen ausgeblendet, damit fehlende Paare nicht als Nullwerte missverstanden werden.

<a id="sec-5-5"></a>
#### 5.5 Export- und Download-Reproduzierbarkeitspaket

Multi-Select, dynamische Filter und CSV-Export machen den Segment-Inspektor zur reproduzierbaren Rohdaten-Auditfl&auml;che. `Prepare All Results for Download` erzeugt das Exportpaket erst auf Anfrage, damit hochaufl&ouml;sende Abbildungen nicht w&auml;hrend der normalen Interaktion gerendert werden. Das ZIP enth&auml;lt die aktive Konfiguration, Run-Metadaten, helle/papierfreundliche hochaufl&ouml;sende PNG-Abbildungen, Station-Insights-CSV-Tabellen, Drill-Down-CSV-Tabellen f&uuml;r die ausgew&auml;hlten Stationen, vollst&auml;ndige Drill-Down-CSV-Tabellen f&uuml;r das aktuelle Segment und den kompakten parquet-Analysecache f&uuml;r Regression-Fixtures.

<a id="sec-6"></a>
### 6. Wissenschaftliche Methodik und Annahmen

<a id="sec-6-1"></a>
#### 6.1 Datenherkunft und Robustheit

WSPRadar liest historische WSPR-Spots &uuml;ber wspr.live. Die wspr.live-Dokumentation beschreibt die Daten als Rohdaten, wie sie von WSPRnet gemeldet und ver&ouml;ffentlicht werden, und warnt vor Duplikaten, falschen Spots und anderen Fehlern. Au&szlig;erdem gibt es f&uuml;r die ehrenamtlich betriebene Infrastruktur keine Garantie f&uuml;r Korrektheit, Verf&uuml;gbarkeit oder Stabilit&auml;t. <a href="#ref-1">[Ref-1]</a>

WSPRadar mindert viele vorgelagerte Datenprobleme durch mehrschichtige Aggregation und Filter: Same-Cycle-Paarbildung, Stationsmediane, Segmentmediane, Mindest-Sample-Schwellen, Moving-Station-Filter und optionale Pr&auml;fix-Ausschl&uuml;sse. Diese Ma&szlig;nahmen reduzieren den Einfluss isolierter Duplikate, sporadischer falscher Spots, One-Hit-Decodes und Receiver-Density-Bias erheblich. Sie machen den vorgelagerten Datensatz nicht kalibriert oder fehlerfrei, und ein plausibler wiederholter Fehler kann weiterhin durchrutschen; der Anspruch ist Robustheit, nicht Immunit&auml;t.

<a id="sec-6-2"></a>
#### 6.2 WSPR-SNR und gemeldete Leistung

WSPR ist f&uuml;r die Untersuchung potenzieller Ausbreitungspfade mit Low-Power-Baken gedacht. WSPR-Nachrichten enthalten Rufzeichen, Locator und Leistung in dBm. WSPR-2-Sendungen dauern etwa 110,6 Sekunden und starten zwei Sekunden nach einer geraden UTC-Minute. Die ARRL-WSPR-Dokumentation beschreibt den Mindest-S/N auf der WSJT-Skala mit 2500-Hz-Referenzbandbreite. <a href="#ref-2">[Ref-2]</a>

F&uuml;r WSPRadar bedeutet das:

* SNR ist ein Decoderwert in dB auf der WSPR/WSJT-Skala, referenziert auf 2500 Hz.
* Die gemeldete Sendeleistung ist Teil der WSPR-Nachricht und wird von WSPRadar nicht unabh&auml;ngig verifiziert.
* Eingetragene dBm k&ouml;nnen von Senderausgangsleistung, Speisepunktleistung oder EIRP abweichen, etwa durch Kalibrierfehler, Foldback, Speiseleitungsverlust, Tuner-Verlust oder Fehlanpassung.

<a id="sec-6-3"></a>
#### 6.3 Leistungsnormalisierung

Um Spots mit unterschiedlichen gemeldeten Sendeleistungen vergleichen zu k&ouml;nnen, normalisiert WSPRadar das SNR auf 1 W / 30 dBm:

$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$

Das ist f&uuml;r TX/RX-Success-Karten und lokale TX-Vergleiche zentral. Es entfernt den gemeldeten Leistungsanteil aus dem Vergleich, aber nur so gut, wie die gemeldete Leistung stimmt. Antennengewinn, Speiseleitungsverlust, Kalibrierfehler oder EIRP-Unterschiede werden dadurch nicht automatisch korrigiert.

Leistungsnormalisierung ist trotzdem eine wesentliche Mitigation. RX-Vergleiche reduzieren die Abh&auml;ngigkeit von Leistungsfehlern oft, weil beide lokalen Empf&auml;nger denselben Remote-Sender bewerten. Same-Callsign TX A/B vermeidet den Vergleich unterschiedlicher selbstgemeldeter Leistungen. Lokale TX-Vergleiche und TX-Success-Karten bleiben am empfindlichsten gegen&uuml;ber falsch gemeldeten dBm.

<a id="sec-6-4"></a>
#### 6.4 Zeitliche Paarbildung und Heartbeat-Filter

Zeitliche Synchronisation ist eine der st&auml;rksten Kontrollen von WSPRadar. Same-Cycle-Paarbildung reduziert schnelle QSB-/Fading-Effekte deutlich, weil beide Seiten in derselben zweimin&uuml;tigen WSPR-Gelegenheit bewertet werden. Bei TX-Vergleichen reduziert derselbe Remote-Empf&auml;nger empfangsseitiges QRM, Noise-Floor- und Antenneneffekte. Bei RX-Vergleichen reduziert derselbe Remote-Sender Sendeleistungs- und gemeinsame Pfadvariation.

Der Heartbeat-Filter ist der Gatekeeper f&uuml;r Vergleichs-Yield. WSPRadar validiert Vergleichszyklen nur, wenn die Zielstation/das Zielsetup nachweislich aktiv war:

* Im TX-Modus muss das Zielsignal im relevanten Zyklus/Slot von mindestens einer Station weltweit decodiert worden sein. Praktisch bedeutet das: WSPRadar bewertet nur TX-Vergleichszyklen, in denen die Zielstation tats&auml;chlich gesendet und mindestens einen gemeldeten Decode irgendwo erzeugt hat.
* Im RX-Modus muss der Zielempf&auml;nger im relevanten Zyklus mindestens eine Station decodiert haben. Praktisch bedeutet das: WSPRadar bewertet nur RX-Vergleichszyklen, in denen der Zielempf&auml;nger tats&auml;chlich empfangen/hochgeladen und mindestens einen gemeldeten Decode erzeugt hat.

Referenz-Evidenz au&szlig;erhalb dieser target-aktiven Zyklen wird bewusst ausgeschlossen. Das sch&uuml;tzt die Analyse davor, Ziel-Downtime als Hardwareversagen zu interpretieren, und bindet den Vergleich an tats&auml;chliche WSPR-Gelegenheiten, in denen die Zielstation/das Zielsetup teilgenommen hat. Die Folge ist eine beabsichtigte target-zentrierte Asymmetrie: Das Tauschen von Ziel und Referenz kann die g&uuml;ltigen Zyklen und damit die Yield-Zahlen ver&auml;ndern.

Wenn die Station nachts ausgeschaltet ist, werden Referenzspots in diesem Offline-Zeitraum nicht als Niederlagen f&uuml;r die eigene Hardware gez&auml;hlt. Das macht nicht jeden Vergleich perfekt fair. Es reduziert dominante Timing-, Fading- und Offline-Bias-Konfounder in synchronen Modi und erh&auml;lt zugleich das zentrale WSPRadar-Prinzip: nur innerhalb g&uuml;ltiger WSPR-Gelegenheiten vergleichen. Sequenzieller TX A/B bleibt der Sonderfall: Time-Binning und mehrt&auml;gige fixe Zeitpl&auml;ne reduzieren Makro-Fading/Zeitdrift, sind aber nicht gleichwertig zu simultaner Same-Cycle-Paarbildung.

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

1. **System Sensitivity / Decode Yield:** z&auml;hlt exklusive und gemeinsame Decodes innerhalb heartbeat-gefilterter Vergleichszyklen. Das erfasst reale operative Reichweite an der Decodiergrenze, ohne Zeitr&auml;ume zu z&auml;hlen, in denen die Zielstation/das Zielsetup nicht nachweislich aktiv war.
2. **Station Medians / Delta SNR:** nutzt nur gepaarte Joint Spots oder gepaarte Spot-Bins. Das sch&auml;tzt den bedingten Gain/SNR-Unterschied, wenn beide Setups vergleichbare Evidenz erzeugt haben.

Beides muss zusammen gelesen werden. Ein Setup kann besseren Yield, aber niedrigeren bedingten SNR haben, wenn es viele Grenzfallsignale decodiert. Umgekehrt kann ein Setup auf Joint Spots starken positiven Delta SNR zeigen, aber schlechten Yield haben, wenn es viele schwache Pfade verpasst.

**Wichtige Interpretation des TX-Yield**

In der TX-Analyse wird Yield bewusst als **heartbeat-gefilterter operativer Yield** ausgegeben. Er beantwortet die praktische On-Air-Frage:

**Wer wurde innerhalb der Zyklen, in denen mein Zielsender nachweislich aktiv war, unter den tats&auml;chlich gemeldeten Betriebsbedingungen h&auml;ufiger decodiert?**

Das ist nützlich, aber keine leistungsnormalisierte Fairness-Metrik. Wenn eine Station mit 100 W und eine andere mit 100 mW sendet, hat die stärkere Station normalerweise einen Decode-Yield-Vorteil. WSPRadar normalisiert SNR für gemeinsame TX-Spots, bei denen beide Stationen decodiert wurden und ein SNR-Vergleich möglich ist. Bei exklusiven TX-Spots fehlt jedoch auf der nicht gehörten Seite ein SNR-Wert. WSPRadar kann daher nicht zuverlässig rekonstruieren, welches SNR die fehlende Station bei anderer Sendeleistung gehabt hätte.

Daraus folgt:

* TX Delta SNR auf Joint Spots ist das wichtigste faire Vergleichssignal.
* TX Yield sollte als heartbeat-gefilterte operative Reichweite gelesen werden, nicht als normalisierte Antenneneffizienz.
* Reference-only- oder Target-only-TX-Decodes können Antennenleistung, Sendeleistung, Ausbreitung, Empfängerverteilung, Timing, Kollisionen, Genauigkeit der gemeldeten Leistung oder eine Kombination dieser Faktoren widerspiegeln.
* Ungleiche gemeldete Sendeleistungen sollten bei der Interpretation von TX-Yield-Asymmetrien ausdrücklich erwähnt werden.

Praktisch bedeutet starker TX Yield: Eine Station wurde unter ihren tatsächlichen Betriebsbedingungen von mehr Empfangsstationen gehört. Das beweist für sich genommen nicht, dass die Antenne besser war. Für faireres TX-Benchmarking sollte das größte Gewicht auf Same-Cycle, leistungsnormalisiertem Delta SNR liegen; heartbeat-gefilterter Yield dient als unterstützender Kontext.

<a id="sec-6-7"></a>
#### 6.7 Geografisches Rastering und Projektion

R&auml;umliche Daten werden in einer mittabstandstreuen Azimutalprojektion dargestellt, zentriert auf dem Maidenhead-Locator des Nutzers. Die Kartenengine nutzt intern eine sph&auml;rische Erde mit 6371 km Radius, damit Tabellendistanzen und geplottete Kartenpositionen derselben Geometrie folgen.

Die Karte nutzt:

* konzentrische Distanzb&auml;nder von 2500 km;
* Azimut-Wedges, z. B. 22,5-Grad-Kompasssektoren;
* eindeutige Segment-IDs f&uuml;r Aggregation und Inspektion.

Die Projektion ist f&uuml;r WSPRadars visuelle Analyse intern konsistent. Sie sollte nicht als geod&auml;tische Vermessung mit Survey-Pr&auml;zision beschrieben werden.

<a id="sec-6-8"></a>
#### 6.8 Evidenzst&auml;rke und Mindest-Schwellen

WSPRadar nutzt praktische Evidenz-Schwellen statt formaler statistischer Signifikanzfilter. Das ist bewusst so. WSPR-Daten sind beobachtend, quantisiert, crowd-sourced und zeitlich strukturiert; ein einfacher p-Wert kann leicht pr&auml;ziser wirken, als die zugrunde liegende Evidenz tats&auml;chlich ist.

F&uuml;r die Interpretation von Vergleichskarten dienen die Joint-Evidenz-Schwellen als Heuristik:

| Evidenz | Mindestbedingung |
|---|---|
| Low | &ge;1 Station pro Segment und &ge;3 Joint Spots pro Station |
| Medium | &ge;3 Stationen pro Segment und &ge;10 Joint Spots pro Station |
| Strong | &ge;5 Stationen pro Segment und &ge;20 Joint Spots pro Station |

Bei sequenziellem TX A/B bedeutet "Joint Spots" sinngem&auml;&szlig; "Paired Spot Bins", weil die gepaarte Evidenzeinheit der valide Zeit-Bin mit Spots ist und nicht der Same-Cycle-Spot.

Diese Schwellen sind keine Beweisstufen. Sie sind praktische Leitplanken zum Lesen der WSPRadar-Ausgabe. St&auml;rkere Evidenz bedeutet zus&auml;tzlich konsistente Delta-SNR-Richtung, plausibles Decode-Yield-Verhalten, keine erkennbare Dominanz durch eine fehlerhafte Station/Grid-Identit&auml;t und Stabilit&auml;t &uuml;ber benachbarte Segmente, B&auml;nder oder wiederholte Runs, sofern das zu erwarten ist.

Das `90% Stability`-Intervall ist ein deskriptives Bootstrap-Stabilit&auml;tsintervall um einen Median. WSPRadar zieht die beitragenden Werte 500-mal mit Zur&uuml;cklegen neu, berechnet f&uuml;r jede Stichprobe den Median und berichtet den zentralen 90%-Bereich dieser Bootstrap-Mediane. Dadurch wird Medianstabilit&auml;t sichtbar, ohne einen formalen p-Wert oder ein kontrolliertes Labor-Konfidenzintervall zu behaupten. Ein schmales Intervall bedeutet, dass der berichtete Median gegen&uuml;ber Resampling der vorhandenen Evidenz stabil ist; es beweist nicht, dass der WSPR-Datensatz selbst unverzerrt ist.

<a id="sec-7"></a>
### 7. Einschr&auml;nkungen

* **Crowd-sourced Daten:** WSPR-Spots k&ouml;nnen Duplikate, falsche Spots, falsche Leistung, falschen Locator oder empfangsseitige Fehler enthalten. WSPRadar reduziert die Empfindlichkeit gegen&uuml;ber vielen dieser Probleme, kann upstream Daten aber nicht kalibriert oder fehlerfrei machen.
* **Nur erfolgreiche Decodes:** WSPR protokolliert Decodes, nicht alle fehlgeschlagenen Empfangsversuche. Geschlossene B&auml;nder reduzieren die Existenz von Spots, statt einen Durchschnitt zu senken.
* **Bedingte Erfolgsraten:** TX/RX-Success-Raten sind auf unabh&auml;ngig best&auml;tigte Aktivit&auml;t bedingt. RX nutzt `Target/(Target+Elsewhere)`, TX nutzt `Target/(Target+Other Signals)`. Gegen-Evidenz beweist nicht, dass der Pfad zwischen Target und Station offen war; die Raten enthalten daher Ausbreitung und schaetzen weder eine unbedingte Empfaengerempfindlichkeit noch den Anteil aller geplanten Aussendungen, die decodiert wurden.
* **Nicht beobachtbare TX-Stille:** Ohne autoritatives Sendelog ist ein Ziel-TX-Zyklus, den niemand decodiert, nicht von keiner Aussendung unterscheidbar und kann daher nicht in `Other Signals` eingehen.
* **Historische Spot-Gueltigkeit:** TX/RX-Success-Queries nutzen `code = 1`, um die Analyse auf gueltige WSPR-Spots zu begrenzen. Code-Abdeckung und Upstream-Verarbeitung koennen in aelteren Archivzeitraeumen abweichen.
* **Gemeldete Leistung:** Normalisierung mindert Unterschiede in gemeldeter Leistung, und mehrere Vergleichsmodi reduzieren dieses Problem zus&auml;tzlich durch Paarbildung gegen denselben Sender oder dasselbe Rufzeichen. Jede Analyse, die auf gemeldeten dBm basiert, setzt aber weiterhin voraus, dass der gemeldete Wert ungef&auml;hr stimmt.
* **Target-zentrierter Yield:** Yield in Vergleichsmodi wird durch target-aktive Zyklen begrenzt. Das ist ein bewusster Schutz gegen Offline-Bias, bedeutet aber, dass Yield beim Tausch von Ziel und Referenz nicht symmetrisch sein muss. A gegen B und B gegen A k&ouml;nnen trotz gleicher Kernparameter unterschiedliche `Nur Referenz`- und `Nur Zielstation`-Zahlen haben.
* **Sequenzieller TX:** Fixed-schedule TX A/B reduziert Zeitkonfundierung, eliminiert sie aber nicht perfekt.
* **Distanz ist kein Winkel:** Distanzringe k&ouml;nnen Ausbreitungsverhalten nahelegen, messen aber keinen Abstrahlwinkel direkt.
* **Polarisation und lokale Umgebung:** WSPRadar misst reale Stationssystem-Performance, einschlie&szlig;lich Antenne, Sender/Empf&auml;nger, Speiseleitung, Gel&auml;nde, Polarisation, lokalem QRM und Softwareverhalten.
* **Performance-Limits und Latenz:** Query-Fenster sind zum Schutz der Datenbank begrenzt; neue Spots k&ouml;nnen etwa 15 bis 30 Minuten brauchen, bis sie sichtbar werden.

F&uuml;r ernsthafte Aussagen sollte gen&uuml;gend Kontext erhalten bleiben, um das Ergebnis zu reproduzieren: WSPRadar-Version oder Git-Commit, UTC-Fenster, Band, Modus, Filter, lokale Benchmark-Methode oder Referenzrufzeichen, Screenshots und exportierte CSV.

<a id="sec-8"></a>
### 8. Konfigurationsreferenz

**Workflow-Bedienelemente**

* **Load Demo:** &ouml;ffnet die Liste gepflegter Demo-Profile. `Load Selected Demo Configuration` f&uuml;llt die Oberfl&auml;che, damit die Parameter gepr&uuml;ft oder ge&auml;ndert werden k&ouml;nnen; `Run Selected Demo` f&uuml;llt die Oberfl&auml;che und startet sofort die konfigurierte TX- oder RX-Analyse.
* **Load Config:** l&auml;dt eine zuvor gespeicherte WSPRadar-`.config`-Datei. Fehlende zuk&uuml;nftige Felder fallen auf Defaults zur&uuml;ck; geladene Rufzeichen und Locators werden vor der Nutzung validiert und normalisiert.
* **Save Config:** l&auml;dt die aktuelle UI-Konfiguration als editierbare JSON-basierte `.config`-Datei herunter. Das ist n&uuml;tzlich, um ein Setup zu teilen, einen Run zu archivieren oder einen Vergleich sp&auml;ter zu wiederholen.
* **Prepare All Results for Download:** erscheint, sobald Analyseergebnisse vorhanden sind. Es rendert die aktuelle Ergebnisauswahl in ein ZIP-Paket mit Konfiguration, Run-Metadaten, hochaufl&ouml;senden Light-Theme-Abbildungen, aktuellen Station-Insights-Tabellen, Drill-Down-Tabellen f&uuml;r ausgew&auml;hlte Stationen, vollst&auml;ndigen Drill-Down-Tabellen f&uuml;r das aktuelle Segment und Analyse-Parquet-Daten.

**Core-Parameter**

* **Zielrufzeichen:** prim&auml;re Station unter Auswertung.
* **QTH Locator:** mathematisches Zentrum der Kartenprojektion. G&uuml;ltigen 4- oder 6-Zeichen-Maidenhead-Locator verwenden.
* **Band und Zeitfenster:** definieren das WSPR-Datenfenster. Zeit wird in UTC behandelt.
* **Min. Target+Gegen-Evidenz pro Station:** Evidenzschwelle nur f&uuml;r Success-Modi. Eine Station benoetigt mindestens diese Zahl bestaetigter Beobachtungen, bevor ihre Erfolgsrate zu Karte, Segment-Zusammenfassung, Zeitpanels oder Station Insights beitraegt. RX zaehlt `Target+Elsewhere`; TX zaehlt `Target+Other Signals`. Standard ist `5`; niedrigere Werte erhoehen die Abdeckung, erzeugen aber auch mehr diskrete Kleinstichproben-Raten wie `0%`, `50%` oder `100%`.

**Vergleichsparameter**

* **Benchmark Mode:** `Lokaler Nachbarschafts-Benchmark`, `Fremdes Rufzeichen (Buddy-Test)` oder `Hardware A/B-Test`.
* **Referenz-SNR-Korrektur (dB):** nutzerdefinierte Korrektur, die vor der Delta-SNR-Berechnung zum Referenzseiten-SNR addiert wird. Sie gilt nur f&uuml;r Vergleichsmodi und ist f&uuml;r bekannte referenzseitige D&auml;mpfung oder Kalibrierartefakte gedacht, die WSPRadar nicht aus WSPR-Daten ableiten kann. Da WSPRadar `Delta SNR = Ziel - Referenz` nutzt, macht eine positive Korrektur das korrigierte Referenz-SNR vor der Subtraktion gr&ouml;&szlig;er. Anhang C beschreibt, wie ein Kalibrierwert bestimmt wird.
  * **Geltungsbereich:** Buddy-Test gilt f&uuml;r das Referenzrufzeichen. Beste lokale Station gilt f&uuml;r das SNR der ausgew&auml;hlten besten lokalen Referenz. Lokaler Nachbarschafts-Median gilt f&uuml;r alle Nachbarschafts-Referenz-SNRs vor der Median-Aggregation. Hardware A/B-Test gilt f&uuml;r die Referenzseite, also Setup B / Referenz-WSPR-Frame.
  * **Formel:** `korrigiertes Referenz-SNR = Referenz-SNR + Referenz-SNR-Korrektur`; `Delta SNR = Ziel-SNR - korrigiertes Referenz-SNR`.
  * **Beispiel f&uuml;r positive Korrektur:** Ein Kalibrierlauf ergibt `Ziel - Referenz = +1,6 dB`. Dann `+1,6 dB` eintragen. Ein Referenzseiten-SNR von `-24,0 dB` wird wie `-22,4 dB` behandelt; der korrigierte Delta SNR sinkt dadurch um `1,6 dB`.
  * **Beispiel f&uuml;r negative Korrektur:** Ein Kalibrierlauf ergibt `Ziel - Referenz = -1,6 dB`. Dann `-1,6 dB` eintragen. Ein Referenzseiten-SNR von `-24,0 dB` wird wie `-25,6 dB` behandelt; der korrigierte Delta SNR steigt dadurch um `1,6 dB`.
* **Lokale Benchmark-Methode:** standardm&auml;&szlig;ig `Lokaler Nachbarschafts-Median`, optional `Beste lokale Station` als strenge Best-Peer-H&uuml;llkurve.
* **Nachbarschaftsradius:** geografische Grenze f&uuml;r lokale Referenzstationen.
* **Referenzrufzeichen:** externer Gegenpart f&uuml;r Buddy-Test.
* **A/B-Test Setup:** simultaner `RX Test` oder fixed-schedule `TX Test`.
* **Target/Reference Locator:** 6-Zeichen-Locators zur Trennung simultaner RX-Streams.
* **Target/Reference WSPR Frame:** feste UTC-Startminuten-Frame-Zuweisung f&uuml;r sequenzielle TX-Tests; 00, 04, 08, ... und 02, 06, 10, ... sind die zwei unterst&uuml;tzten Frame-Sequenzen.
* **Time Window (Bins):** Bin-Gr&ouml;&szlig;e f&uuml;r sequenzielle TX-A/B-Paarbildung.

**Erweiterte Einstellungen**

* **Exclude Special Callsigns:** entfernt bekannte Sonderformat-WSPR-Rufzeichen aus der Analyse anhand des eingebauten WSPRadar-Präfixfilters. Der aktuelle Filter schließt Rufzeichen aus, die mit `Q`, `0` oder `1` beginnen. Diese Präfixe sind häufig mit speziellen WSPR-Anwendungsfällen wie telemetrieartigen oder nicht-standardmäßigen Beacon-Kennungen verbunden (z.B. Pico-Ballon), nicht mit normalen Amateurfunk-Rufzeichen.
* **Exclude Moving Stations:** entfernt Stationen, die während des Analysefensters ihren 4-stelligen Locator ändern, zum Beispiel Ballons, mobile oder maritime Stationen.
* **Local QTH Solar State:** filtert nach berechneter Sonnenhöhe am eigenen QTH: Tageslicht, Nacht oder Greyline.
* **Map Scope:** visueller Kartenradius.
* **Min. Joint Spots/Station:** Schwelle nur f&uuml;r Vergleichsmodi. Sie erfordert mindestens X Joint Spots pro Remote-Station, bevor diese Station zu einem Delta SNR beitr&auml;gt. In sequenziellem TX A/B wird dies als Min. Joint Bins angezeigt.
* **Min. Target+Gegen-Evidenz pro Station:** Success-Modus-Schwelle aus den Core-Parametern. Sie ersetzt die fruehere Interpretation als rohe Spots pro Station.
* **Min. qualifizierte Stationen/Segment:** erfordert mindestens X qualifizierende Stationen, bevor ein Segment gezeichnet wird. In Vergleichsmodi zaehlt sie Stationen mit qualifizierender Joint-Evidenz; in TX/RX-Success-Modi z&auml;hlt sie Stationen, die den modus-spezifischen best&auml;tigten Target/Gegen-Evidenz-Schwellenwert erreichen.

**Hinweis zum Sonderrufzeichen-Filter**

Der Sonderrufzeichen-Filter ist besonders nützlich, wenn nicht-standardmäßige Beacon- oder telemetrieartige Stationen die normale Station-zu-Station-Interpretation verzerren würden. Er sollte jedoch nicht automatisch für jede Analyse aktiviert werden.

Für RX-Vergleiche gibt es oft einen guten Grund, diese Rufzeichen **nicht** auszuschließen. Viele spezielle WSPR-Kennungen verhalten sich wie Low-Power-Baken. Wenn dieselbe schwache Bake im selben WSPR-Zyklus sowohl von der eigenen Station als auch von der Referenzstation decodiert wird, ist das wertvolle gepaarte RX-Evidenz. In diesem Fall ist die absolute Identität der Bake weniger wichtig als die Tatsache, dass beide Empfänger denselben schwachen Sender zur selben Zeit bewertet haben.

Empfohlene Interpretation:

* Bei **TX-Analysen** kann das Ausschließen von Sonderrufzeichen helfen, die Empfänger-/Referenzpopulation näher an normalen Amateurfunkstationen zu halten.
* Bei **RX-Vergleichen** kann das Beibehalten von Sonderrufzeichen nützlich sein, weil sie schwache, stabile Same-Cycle-Testsignale liefern können.
* Bei **RX-Success-Coverage** hängt die Wahl von der Fragestellung ab: einschließen, wenn Beacon-Sensitivität interessant ist; ausschließen, wenn nur normale Amateurfunkaktivität betrachtet werden soll.
* Für **Veröffentlichungen oder ernsthafte Vergleiche** sollte dokumentiert werden, ob der Sonderrufzeichen-Filter aktiviert war.

<a id="sec-9"></a>
### 9. Bestehende Literatur und Stand der Technik

WSPRadar steht nicht isoliert. Es baut auf drei bereits etablierten Linien auf: Erstens auf WSPR als globalem, durch Funkamateure betriebenem Beobachtungsnetz; zweitens auf wissenschaftlichen Arbeiten, die WSPR-Daten f&uuml;r Ausbreitungs- und Antennenfragen verwenden; drittens auf praktischen Werkzeugen, die WSPR-Spots visualisieren, abfragen oder f&uuml;r Antennenvergleiche auswerten.

Dieses Kapitel ordnet WSPRadar in diesen Kontext ein und grenzt den eigenen Anspruch bewusst ab: WSPRadar ist kein kalibrierter Antennenmessplatz und kein Ersatz f&uuml;r kontrollierte Feldst&auml;rkemessungen. Es ist ein Werkzeug zur robusten, auditierbaren Realwelt-Bewertung von Stationssystemen auf Basis &ouml;ffentlicher WSPR-Spots.

<a id="sec-9-1"></a>
#### 9.1 WSPR als globales Beobachtungsnetz

WSPR wurde f&uuml;r die Untersuchung potenzieller Ausbreitungspfade mit niedriger Sendeleistung entwickelt. Die ARRL beschreibt WSPR als schmalbandiges digitales Protokoll f&uuml;r HF- und MF-Ausbreitungstests. Eine typische WSPR-Nachricht enth&auml;lt Rufzeichen, 4-stelligen Maidenhead-Locator und Sendeleistung in dBm. Die Aussendung dauert etwa 110,6 Sekunden und beginnt zwei Sekunden nach einer geraden UTC-Minute. Die minimale Dekodierbarkeit liegt ungef&auml;hr bei -27 dB auf der WSJT-Skala mit 2500-Hz-Referenzbandbreite. <a href="#ref-2">[Ref-2]</a> <a href="#ref-3">[Ref-3]</a>

Die &ouml;ffentliche WSPR-Infrastruktur ist aber kein Laborinstrument. WSPR.live stellt historische und aktuelle WSPR-Spots in einer ClickHouse-Datenbank bereit und weist ausdr&uuml;cklich darauf hin, dass es sich um Rohdaten handelt, wie sie von WSPRnet gemeldet und ver&ouml;ffentlicht wurden. Duplikate, falsche Spots, fehlerhafte Locator, falsche Leistungen und Infrastrukturausf&auml;lle sind deshalb Teil des realen Datenumfelds. <a href="#ref-1">[Ref-1]</a>

WSPRadar &uuml;bernimmt diese Unsicherheit nicht blind, sondern reduziert ihre Wirkung durch Filter, Mindestschwellen, Mediane, zeitliche Paarbildung, Segmentaggregation und Drill-Down-Pr&uuml;fbarkeit. Der Anspruch ist nicht, aus Crowd-Daten kalibrierte Messdaten zu machen. Der Anspruch ist, aus unvollkommenen, aber sehr zahlreichen Beobachtungen eine nachvollziehbare und vorsichtig interpretierte Evidenzschicht zu erzeugen.

<a id="sec-9-2"></a>
####9.2 WSPR in Radio Science und Ionosph&auml;renforschung

**Lo et al.** untersuchten 7-MHz-Greyline-Ausbreitung anhand von Amateurfunk-Bakensignalen aus der WSPR-Datenbank. Die Arbeit zeigt exemplarisch, dass WSPR nicht nur f&uuml;r individuelle Stationsbeobachtung n&uuml;tzlich ist, sondern auch als wissenschaftlicher Datensatz f&uuml;r globale HF-Ausbreitungsfragen verwendet werden kann. Besonders relevant f&uuml;r WSPRadar ist dabei die Grundidee, dass WSPR-Pfade zeitlich, geografisch und bandbezogen ausgewertet werden k&ouml;nnen, ohne dass die urspr&uuml;ngliche Infrastruktur als kontrolliertes Experiment aufgebaut wurde. <a href="#ref-4">[Ref-4]</a>

**Frissell et al.** ordnen WSPRNet zusammen mit dem Reverse Beacon Network und PSKReporter als etablierte Amateurfunk-Beobachtungsnetzwerke ein, die langfristige Daten &uuml;ber die untere Ionosph&auml;re liefern. Die Arbeit ist wichtig, weil sie die Rolle des Amateurfunks als Citizen-Science-Infrastruktur beschreibt: Viele unabh&auml;ngige Stationen erzeugen gemeinsam ein Beobachtungsnetz, das f&uuml;r Raumwetter-, Ionosph&auml;ren- und HF-Ausbreitungsfragen relevant ist. F&uuml;r WSPRadar ist diese Perspektive zentral: Das Tool verwendet nicht einzelne Rapporte als absolute Wahrheit, sondern nutzt die Masse, Wiederholung und r&auml;umliche Verteilung der Beobachtungen. <a href="#ref-5">[Ref-5]</a>

**Methodische Konsequenz.** WSPR-Daten sind f&uuml;r Radio Science brauchbar, aber sie m&uuml;ssen als Beobachtungsdaten gelesen werden. Sie enthalten reale Ausbreitung, reale Stationsunterschiede und reale Fehlerquellen gleichzeitig. WSPRadar versucht deshalb nicht, diese Faktoren vollst&auml;ndig zu eliminieren, sondern die dominanten St&ouml;rgr&ouml;&szlig;en f&uuml;r konkrete Vergleichsfragen sichtbar zu machen und so weit wie m&ouml;glich zu reduzieren.

<a id="sec-9-3"></a>
#### 9.3 Direkte WSPR-Literatur zu Antennenvergleichen

Die direkte Literatur zu WSPR-basierten Antennenvergleichen ist kleiner als die breitere Literatur zu WSPR-Ausbreitungsanalyse. Das ist wichtiger Kontext: WSPRadar tritt nicht in ein reifes Feld mit vielen standardisierten Messprotokollen ein. Stattdessen baut es auf wenigen starken methodischen Vorl&auml;ufern und einer gr&ouml;&szlig;eren Menge praktischer Amateurfunk-Experimente auf.

**Vanhamel, Machiels und Lamy** liefern den st&auml;rksten peer-reviewten RX-seitigen Vorl&auml;ufer. Ihr 160-m-Experiment nutzte zwei nahezu identische und kalibrierte WSPR-Empfangsketten an fast demselben Standort, um unterschiedliche Antennen zu vergleichen. Dieses Design reduziert Ausbreitungspfad-Variation, weil beide Antennen dieselben Remote-Sender zur selben Zeit beobachten. F&uuml;r WSPRadar st&uuml;tzt das die Logik simultaner RX-A/B-Tests und die Notwendigkeit, Empfangsketten zu kalibrieren oder zumindest zu verstehen, bevor kleine SNR-Unterschiede interpretiert werden. <a href="#ref-6">[Ref-6]</a>

**Zander** liefert den st&auml;rksten TX-seitigen Vorl&auml;ufer. Statt zwei lokale Empf&auml;nger zu verwenden, vergleicht Zander zwei sendende Antennen &uuml;ber das globale WSPR-Empf&auml;ngernetz. Berichte werden nur verwendet, wenn derselbe entfernte Empf&auml;nger beide Antennen im selben Zeitintervall h&ouml;rt. Dadurch werden Ausbreitungsverlust und empfangsseitige Bedingungen weitgehend gemeinsam f&uuml;r beide Beobachtungen. F&uuml;r WSPRadar st&uuml;tzt das Same-Cycle-TX-Pairing, betont aber auch die Grenzen: Empf&auml;ngerverteilung, Antennendirektivit&auml;t, Kollisionen, gemeldete Leistung und unvollst&auml;ndige r&auml;umliche Abdeckung bleiben Teil der Evidenz. <a href="#ref-7">[Ref-7]</a>

**Milazzos** vergleichende Antennenanalyse von 2011 ist wichtige historische Prior Art aus der Amateurfunkpraxis. Sie zeigt, dass WSPR-Spots bereits kurz nach der breiteren Verf&uuml;gbarkeit von WSPR f&uuml;r Antennenvergleiche genutzt wurden. Die Arbeit ist weniger formal als Vanhamel oder Zander, aber n&uuml;tzlich, weil sie zeigt, wie Funkamateure WSPR tats&auml;chlich verwenden: nicht nur zur Beobachtung von Ausbreitung, sondern zum Vergleich realer Antennen unter realen Betriebsbedingungen. <a href="#ref-8">[Ref-8]</a>

**Griffiths und Squibb** erg&auml;nzen eine praktische RX-Performance-Perspektive. Ihr Practical-Wireless-Artikel nutzte aus WSPR abgeleitete Spot- und SNR-Informationen, um HF-Band-SNR in normalen suburbanen Empfangsinstallationen zu verstehen und zu verbessern. Das liegt nahe an WSPRadars RX-Interpretationsphilosophie: Das gemessene Resultat ist nicht nur Antennengewinn, sondern das kombinierte Empfangssystem aus Antenne, lokalem Rauschen, Speiseleitung, Empf&auml;nger und Betriebsumgebung. <a href="#ref-9">[Ref-9]</a>

Diese Arbeiten st&uuml;tzen den Grundgedanken von WSPRadar: WSPR kann f&uuml;r Antennen- und Stationsvergleiche n&uuml;tzlich sein, wenn Vergleichspaare sauber gebildet und St&ouml;rgr&ouml;&szlig;en bewusst behandelt werden. Sie begrenzen aber auch die Sprache, mit der Ergebnisse beschrieben werden sollten. Ein WSPR-basierter Vergleich kann starke Hinweise auf reale Stationsperformance liefern, aber er misst nicht direkt Antennengewinn, Abstrahlwinkel oder Wirkungsgrad im kalibrierten Labor-Sinn.

<a id="sec-9-4"></a>
#### 9.4 Bestehende Werkzeuge und praktische Prior Art

**WSPR.live** ist f&uuml;r WSPRadar die wichtigste Datenquelle. Die Plattform stellt eine &ouml;ffentlich abfragbare ClickHouse-Datenbank mit historischen WSPR-Spots bereit, erg&auml;nzt durch Dokumentation, Grafana-Dashboards und Beispiele zur Datenstruktur. WSPR.live ist damit weniger ein Antennenvergleichswerkzeug als vielmehr die zentrale, schnelle Datengrundlage f&uuml;r eigene Analysen. WSPRadar nutzt diese Infrastruktur, erg&auml;nzt sie aber um stationsbezogene Experimentlogik, Segmentaggregation und interaktive Audit-Ansichten. <a href="#ref-1">[Ref-1]</a>

**WSPR.Rocks** ist ein m&auml;chtiges Analyse- und Visualisierungswerkzeug auf Basis der WSPR.live- und WSPRdaemon-Daten. Es bietet unter anderem SpotQ, SQL-Zugriff, Karten, Tabellen, Duplicate-Spot-Analyse, Passband-Darstellungen und interaktive Auswertungen. Besonders SpotQ ist als praktisches Rankingma&szlig; interessant, weil es Distanz, Leistung und SNR in eine einfache Kennzahl &uuml;berf&uuml;hrt. WSPRadar verfolgt einen anderen Schwerpunkt: Es berechnet keine globale Bestenliste, sondern versucht, konkrete Vergleichsfragen mit kontrollierter Paarbildung, lokalen Referenzpools und segmentbezogener Evidenz zu beantworten. <a href="#ref-10">[Ref-10]</a>

**Griffiths und Robinetts** WSPR/TimescaleDB/Grafana-Arbeit ist wichtige Dateninfrastruktur-Prior-Art. Sie zeigt, dass ernsthafte WSPR-Analyse schnell &uuml;ber einfache Spotlisten hinausgeht und Zeitreihendatenbanken, abgeleitete Felder, Joins, Heatmaps und Dashboards nutzt. Ihre Beispiele enthalten Datenbank-Joins, um SNR desselben Senders zur selben Zeit und auf demselben Band zwischen verschiedenen Reportern zu vergleichen. WSPRadar folgt derselben allgemeinen Richtung, rohe WSPR-Spots in strukturierte Evidenz zu verwandeln, spezialisiert den Workflow aber auf Stationsbenchmarking, lokale Referenzen, Same-Cycle-Vergleich und Map-Segment-Drill-Down. <a href="#ref-11">[Ref-11]</a>

**WSPRdaemon** ist vor allem auf robuste Datenerfassung ausgelegt. Es kann WSPR und FST4W von mehreren SDR-Empf&auml;ngern dekodieren, Spots zuverl&auml;ssig zu WSPRnet hochladen, Band- und Empf&auml;nger-Schedules verwalten, Ausf&auml;lle &uuml;berstehen und zus&auml;tzliche Informationen wie Doppler-Shift und Hintergrundrauschen erfassen. Damit ist WSPRdaemon eher eine professionelle Empfangs- und Reporting-Infrastruktur als ein Endnutzer-Tool f&uuml;r Antennenbenchmarking. F&uuml;r WSPRadar ist es dennoch relevante Prior Art, weil es zeigt, wie wichtig stabile Multi-Receiver-Datenerfassung, Rauschinformation und langfristige Beobachtbarkeit f&uuml;r belastbare WSPR-Auswertung sind. <a href="#ref-12">[Ref-12]</a>

**SOTABEAMS WSPRlite und DXplorer** sind direkte praktische Prior Art f&uuml;r WSPR-basierte Antennen- und Standortvergleiche. WSPRlite ist ein kleiner WSPR-Sender; DXplorer nutzt WSPR-Daten, um Antennen- und Standortleistung unter anderem &uuml;ber den DX10-Wert und Echtzeitgraphen vergleichbar zu machen. Die St&auml;rke dieses Ansatzes liegt in einfacher Bedienung und direktem Praxisnutzen. WSPRadar unterscheidet sich durch einen st&auml;rker auditierbaren, datenanalytischen Ansatz: Es zeigt nicht nur einen Score, sondern Segmentwerte, Joint/Exclusive-Decodes, Station-Insights und Drill-Down-Zeilen, damit ein Ergebnis nachvollzogen und angezweifelt werden kann. <a href="#ref-13">[Ref-13]</a>

**WSPR-Station-Compare** und &auml;hnliche Werkzeuge zeigen, dass der Bedarf an stationsbezogenen WSPR-Vergleichen bereits erkannt wurde. Die WSPR-Station-Compare-Seite verweist ausdr&uuml;cklich auf Vanhamel, Machiels und Lamy sowie auf Zander und beschreibt eine App-Idee zur Darstellung und zum Vergleich eigener WSPRnet-Messungen. Das best&auml;tigt die N&auml;he zwischen wissenschaftlichem Ansatz und Amateurfunkpraxis: Nutzer m&ouml;chten nicht nur sehen, wo Spots auftreten; sie m&ouml;chten wissen, ob eine Station, Antenne oder Hardware&auml;nderung messbar besser oder schlechter ist. <a href="#ref-14">[Ref-14]</a>

**Antenna Performance Analysis Tool** und andere neuere Webdienste zeigen denselben Trend: WSPR-Daten werden zunehmend f&uuml;r verst&auml;ndliche, anwenderorientierte Antennenberichte genutzt. Solche Tools kartieren Empfangsorte, Zeitr&auml;ume und B&auml;nder und helfen Operatoren, die reale Wirkung einer Antenne &uuml;ber Zeit zu beurteilen. WSPRadar sollte deshalb nicht behaupten, als erstes Werkzeug WSPR f&uuml;r Antennenperformance zu nutzen. Die eigene St&auml;rke liegt vielmehr in der Kombination aus Vergleichsdesign, lokalen Benchmarks, Medianlogik, bivariater Yield/SNR-Auswertung und nachvollziehbaren Rohdatenebenen. <a href="#ref-15">[Ref-15]</a>

**WATT WSPR Analysis Tool** ist ein weiteres Beispiel f&uuml;r praktische Prior Art. Es nutzt eine Excel/VBA-Umgebung f&uuml;r Reporting, Mapping, Filterung, Ad-hoc-Analyse und zeitliche Animation von WSPR-Daten. Der Ansatz ist interessant, weil er zeigt, dass WSPR-Auswertung auch als explorativer Arbeitsfluss verstanden werden kann: Nutzer m&ouml;chten Daten nicht nur ansehen, sondern filtern, sortieren, animieren und eigene Fragen stellen. WSPRadar greift diese explorative Idee auf, verlagert sie aber in eine webbasierte, experimentdesign-orientierte Oberfl&auml;che. <a href="#ref-16">[Ref-16]</a>

<a id="sec-9-5"></a>
#### 9.5 Einordnung von WSPRadar

Aus dieser Literatur und Prior Art ergibt sich eine klare Einordnung:

* WSPRadar &uuml;bernimmt von WSPR und WSPR.live die Idee eines globalen, historischen, crowd-sourced Beobachtungsdatensatzes. <a href="#ref-2">[Ref-2]</a> <a href="#ref-1">[Ref-1]</a>
* WSPRadar &uuml;bernimmt von wissenschaftlichen Arbeiten wie Vanhamel et al. und Zander die Einsicht, dass faire Vergleiche zeitliche und r&auml;umliche Konfounder reduzieren m&uuml;ssen. <a href="#ref-6">[Ref-6]</a> <a href="#ref-7">[Ref-7]</a>
* WSPRadar &uuml;bernimmt von praktischen Tools wie WSPR.Rocks, DXplorer, WSPRdaemon und WATT die Erkenntnis, dass WSPR-Daten nur dann n&uuml;tzlich sind, wenn sie schnell, filterbar, visualisierbar und reproduzierbar zug&auml;nglich sind. <a href="#ref-10">[Ref-10]</a> <a href="#ref-13">[Ref-13]</a> <a href="#ref-12">[Ref-12]</a> <a href="#ref-16">[Ref-16]</a>
* WSPRadar erg&auml;nzt diese Ans&auml;tze durch einen eigenen Schwerpunkt: experimentelles Stationsbenchmarking mit Same-Cycle-Paarbildung, lokalen Nachbarschaftsreferenzen, Hardware-A/B-Workflows, Median-von-Medianen-Aggregation, Decode-Yield-Auswertung und Drill-Down-Audit.

WSPRadar sollte daher nicht als Ersatz f&uuml;r WSPR.live, WSPR.Rocks, WSPRdaemon oder DXplorer beschrieben werden. Es sitzt eine Ebene dar&uuml;ber: Es nutzt historische WSPR-Spots, um konkrete Stationsfragen methodisch vorsichtiger zu beantworten. Die Kernfrage lautet nicht nur: "Wo gibt es Spots?" Die Kernfrage lautet: "Welche Spots sind f&uuml;r diese Vergleichsfrage g&uuml;ltig, welche St&ouml;rgr&ouml;&szlig;en wurden reduziert, wie stabil ist der Median, wie sieht der Decode Yield aus, und kann ich das Ergebnis bis auf die zugrunde liegenden Zeilen zur&uuml;ckverfolgen?"

<a id="sec-9-6"></a>
#### 9.6 Methodische Konsequenzen f&uuml;r die Interpretation

Die vorhandene Literatur st&uuml;tzt den Grundansatz von WSPRadar, aber sie begrenzt auch die Sprache, mit der Ergebnisse beschrieben werden sollten. WSPR-basierte Auswertungen k&ouml;nnen starke Hinweise auf reale Stationsperformance liefern, aber sie messen nicht direkt Antennengewinn, Abstrahlwinkel oder Effizienz im kalibrierten Labor-Sinn. Reported Power, Locator-Genauigkeit, Empf&auml;ngerverteilung, lokale St&ouml;rungen, Polarisation, Ausbreitungsmodus, Bandaktivit&auml;t und Decode-Survivorship bleiben Teil der Daten.

Deshalb sollte WSPRadar-Ergebnistext konsequent zwischen folgenden Ebenen unterscheiden:

* **Spot-Ebene:** einzelne WSPR-Decodes mit SNR, Zeit, Band, Sender, Empf&auml;nger und gemeldeter Leistung.
* **Paar-Ebene:** g&uuml;ltige Same-Cycle-Vergleiche oder g&uuml;ltige Zeit-Bins, bei denen wichtige St&ouml;rgr&ouml;&szlig;en reduziert wurden.
* **Stations-Ebene:** Median &uuml;ber mehrere g&uuml;ltige Beobachtungen einer Remote-Station.
* **Segment-Ebene:** Median &uuml;ber mehrere Stationsmediane in einem Distanz-/Azimutsegment.
* **Interpretations-Ebene:** vorsichtige Aussage &uuml;ber reale Stationsperformance, nicht &uuml;ber isolierten Antennengewinn.

Diese Schichtung ist eine der wichtigsten Abgrenzungen von WSPRadar gegen&uuml;ber einfacheren Karten- oder Score-Werkzeugen. Sie macht das Ergebnis nicht automatisch "wahr", aber sie macht sichtbar, welche Evidenz hinter einer Aussage steht.

<a id="sec-9-7"></a>
#### 9.7 Kurzfazit

Literatur und Prior Art zeigen, dass die einzelnen Bausteine hinter WSPR-basierter Stationsbewertung bereits existieren: Same-Cycle-Vergleich, Antennenbewertung mit WSPR, lokale Rausch- und SNR-Verbesserung, datenbankgest&uuml;tzte Spot-Analyse, Mapping, Scoring und Visualisierung. WSPRadars Beitrag besteht darin, diese Ideen in ein koh&auml;rentes, nutzerorientiertes Benchmarking-Framework mit explizitem Experimentdesign, heartbeat-gefiltertem Yield, leistungsnormalisiertem Joint-TX-SNR, lokalen Nachbarschafts-Baselines, Segmentmedianen und zeilenbasierter Auditierbarkeit zu integrieren.

Das ist ein sinnvoller Beitrag, weil die meisten praktischen WSPR-Tools eine von zwei Fragen beantworten: wo Spots aufgetreten sind oder wie eine Station nach einem bestimmten Score rangiert. WSPRadar stellt eine strukturiertere Vergleichsfrage: Welche Beobachtungen sind f&uuml;r diesen Benchmark g&uuml;ltig, welche St&ouml;rgr&ouml;&szlig;en wurden reduziert, welche Evidenz ist gepaart, welche Evidenz ist nur operativer Yield, und l&auml;sst sich das Ergebnis bis zu den zugrunde liegenden Spots zur&uuml;ckverfolgen?

Die bestehende Literatur st&uuml;tzt die Nutzung von WSPR-Daten f&uuml;r Ausbreitungsforschung, Antennenvergleich und Citizen Science, macht aber ebenso klar, dass WSPR kein kalibriertes Laborinstrument ist. WSPRadar akzeptiert diese Begrenzung, statt sie zu verstecken. Es behauptet nicht, isolierten Antennengewinn, Abstrahlwinkel oder Effizienz direkt zu messen. Stattdessen verwandelt es crowd-sourced WSPR-Beobachtungen in ein reproduzierbares, vorsichtig interpretiertes Evidenz-Framework f&uuml;r reale TX-, RX-, lokale Peer- und Hardware-A/B-Stationsvergleiche.

In diesem Sinne ist WSPRadar nicht einfach eine weitere WSPR-Karte oder Score-Anzeige. Es ist ein Versuch, WSPR-basiertes Stationsbenchmarking transparenter, reproduzierbarer und wissenschaftlich disziplinierter zu machen, ohne den praktischen Nutzen f&uuml;r den Amateurfunk-Alltag zu verlieren.

<a id="sec-10"></a>
### 10. Haftungsausschluss & Lizenz

**Haftungsausschluss**

WSPRadar ist ein experimentelles Open-Source-Projekt und wird ohne Gew&auml;hrleistung bereitgestellt. Quellcode und mathematisches Modell sind pr&uuml;fbar, aber der Entwickler kann keine Genauigkeit, Vollst&auml;ndigkeit, Verf&uuml;gbarkeit oder Eignung f&uuml;r einen bestimmten Zweck garantieren. Gr&ouml;&szlig;ere finanzielle Entscheidungen, etwa Kauf oder Verkauf teurer Antennen oder Funkhardware, sollten nie ausschlie&szlig;lich auf WSPRadar-Ausgaben basieren.

**Lizenz**

WSPRadar ist freie Software unter der GNU Affero General Public License (AGPLv3). Die Lizenz stellt sicher, dass der Quellcode, einschlie&szlig;lich &Auml;nderungen an Netzwerkdiensten, der Amateurfunk-Community zug&auml;nglich bleibt.


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


<a id="sec-b"></a>
### Anhang B: Single-TX A/B-Umschaltung mit USB-Relay

F&uuml;r sequenzielle TX-A/B-Antennentests ist das bevorzugte Hardwaredesign oft ein einzelner Sender, der &uuml;ber einen gesteuerten RF-Schalter zwei alternative RF-Pfade speist. Dadurch wird vermieden, zwei unabh&auml;ngige Sender miteinander zu vergleichen. PA-Stufe, Frequenzreferenz, WSPR-Audiokette, Leistungseinstellung, Rufzeichen und Software-Timing sind f&uuml;r beide Pfade identisch. Das macht den Vergleich konservativer: Die verbleibenden beabsichtigten Variablen sind die geschalteten Speiseleitungs-/Antennenpfade.

WSPRadar enth&auml;lt ein plattform&uuml;bergreifendes Python-Hilfswerkzeug:

`tools/Timed-AB-Relay-Switch`: https://github.com/markusthemaker/WSPRadar/releases/download/timed-ab-relay-switch-v0.1.0/Timed-AB-Relay-Switch-v0.1.0.zip

Das Werkzeug schaltet ein unterst&uuml;tztes USB-HID-Relay im WSPR-Frame-Takt, den WSPRadar nutzt:

* Target-WSPR-Frames: UTC-Startminuten 00, 04, 08, ...
* Reference-WSPR-Frames: UTC-Startminuten 02, 06, 10, ...
* Das Relay schaltet an der zweimin&uuml;tigen WSPR-Slot-Grenze, optional mit Vorlaufzeit, damit sich der RF-Pfad vor dem n&auml;chsten Sendek&ouml;rper stabilisieren kann.

Das Hilfswerkzeug zielt auf verbreitete ATtiny45/V-USB-HID-Relay-Boards mit USB VID/PID `16c0:05df` und nutzt den Python-HID-Stack unter Windows, Linux und macOS. Beim Setup werden Relay-Ger&auml;t, Relay-Kanal, Relay-Polarit&auml;t, Target-Frame-Phase und Umschaltvorlauf ausgew&auml;hlt. Vor Anschluss von RF-Hardware sollte der Dry-Run-Modus verwendet werden. Plattformspezifische Installationshinweise, einschlie&szlig;lich Linux-HID-Berechtigungen, stehen in der README des Werkzeugs.

Abh&auml;ngigkeit aus dem Werkzeugordner installieren:

```bat
py -3 -m pip install -r requirements-relay.txt
```

oder unter Linux/macOS:

```sh
python3 -m pip install -r requirements-relay.txt
```

Beispiel f&uuml;r Setup unter Windows:

```bat
Start-Timed-AB-Relay-Switch.cmd --setup
```

Beispiel f&uuml;r Setup unter Linux/macOS:

```sh
chmod +x ./Start-Timed-AB-Relay-Switch.sh
./Start-Timed-AB-Relay-Switch.sh --setup
```

Beispiel f&uuml;r Dry Run unter Windows:

```bat
Start-Timed-AB-Relay-Switch.cmd --dry-run
```

Beispiel f&uuml;r Dry Run unter Linux/macOS:

```sh
./Start-Timed-AB-Relay-Switch.sh --dry-run
```

Ein USB-Relay sollte RF normalerweise nicht direkt schalten. Es sollte ein daf&uuml;r ausgelegtes RF-Schalt- oder Relaissystem steuern. Eine Beispielklasse ist ein 1-zu-2-RF-Schalter wie der QRO.cz 1-to-2 RF Switch, der einen gemeinsamen RF-Port zwischen zwei RF-Ports schalten kann oder umgekehrt und eine DC-Steuerschnittstelle bereitstellt. Vor dem Einsatz muss gepr&uuml;ft werden, dass USB-Relay-Kontakte und RF-Schalter-Steuereingang elektrisch kompatibel sind, einschlie&szlig;lich Steuerspannung, Strom, Polarit&auml;t und Fail-Safe-Zustand.

Vor jedem On-Air-Test:

* Relay und RF-Schalter ohne RF-Leistung testen.
* Best&auml;tigen, dass Target-WSPR-Frames die beabsichtigte Target-Antenne / den beabsichtigten Target-Pfad ausw&auml;hlen.
* Best&auml;tigen, dass Reference-WSPR-Frames die beabsichtigte Referenzantenne / den beabsichtigten Referenzpfad ausw&auml;hlen.
* Best&auml;tigen, dass kein Relay-Umschaltvorgang w&auml;hrend des WSPR-Sendek&ouml;rpers stattfindet.
* Vor Normalbetrieb mit Dummy Load oder Low-Power-Durchgangs-/SWR-Test pr&uuml;fen.
* Gen&uuml;gend Metadaten f&uuml;r Reproduzierbarkeit sichern: Relay-Konfiguration, Frame-Zuweisung, Umschaltvorlauf, Antennen-/Speiseleitungszuordnung, WSPRadar-Konfiguration und UTC-Laufzeitfenster.

Diese Umschaltmethode verbessert die experimentelle Kontrolle, macht das Ergebnis aber nicht zu einer Labor-Antennengewinnmessung. RF-Schalter-Verlust, Isolation, Steckverbinder-Wiederholbarkeit, Speiseleitungsunterschiede und Ver&auml;nderungen der lokalen Antennenumgebung k&ouml;nnen weiterhin beitragen. F&uuml;r einen strengeren Nur-Antennen-Vergleich sollten, soweit praktisch m&ouml;glich, gleiche Speiseleitungsl&auml;ngen und -typen verwendet, der RF-Pfad dokumentiert und ein Kontrolllauf mit zwischen den Pfaden getauschten Antennen erwogen werden.

<a id="sec-c"></a>
### Anhang C: Referenz-SNR-Kalibrierung

Dieses Verfahren sch&auml;tzt eine konstante Korrektur zwischen zwei Empfangsketten, Referenzstationen oder Referenzseiten-Pfaden vor dem eigentlichen Vergleichslauf. Es ist besonders n&uuml;tzlich, wenn bekannt ist, dass die Referenzseite einen stabilen Hardware-, Empfangsketten- oder Kalibrierunterschied hat, den WSPRadar nicht aus WSPR-Spots allein ableiten kann.

1. **Baseline-Messung:** Eine einzelne Antenne &uuml;ber einen 3-dB-Splitter gleichzeitig auf beide RX-Ketten f&uuml;hren.
2. **Datensammlung:** Dieses Setup mehrere Tage laufen lassen, um eine gro&szlig;e gepaarte Stichprobe &uuml;ber wechselnde Ausbreitungszust&auml;nde zu erhalten.
3. **Berechnung:** WSPRadar Buddy-Test oder Hardware A/B-Test verwenden, um den Delta SNR zwischen beiden Ketten zu bestimmen. Den Kalibrierwert aus den Abbildungen oberhalb der Station-Insights-Tabelle ablesen. Es muss bewusst entschieden werden, ob der relevante Wert der Station-Median-Delta-SNR oder der Joint-Spot-Delta-SNR-Mittelwert/Median ist; verwende den Wert, der zur Evidenzebene passt, die korrigiert werden soll. Mit gen&uuml;gend gepaarten Samples kann der numerische Mittelwert sehr stabil werden; ein Ziel wie `0,05 dB` beschreibt Stichprobenpr&auml;zision, nicht absolute Laborkalibrierungsgenauigkeit.
4. **Anwendung:** Diesen Kalibrierwert im eigentlichen Vergleichslauf als konstante Referenz-SNR-Korrektur f&uuml;r die zweite Station, Referenzstation oder Referenzseite verwenden.

<a id="sec-ref"></a>
### Quellen / Referenzen

* <a id="ref-1"></a><a href="#ref-1">[Ref-1]</a> WSPR.live, **Welcome to WSPR Live**, Dokumentation, Datenbankbeschreibung und Disclaimer zu Rohdaten, Duplikaten, falschen Spots und Verf&uuml;gbarkeit.
  https://wspr.live/

* <a id="ref-2"></a><a href="#ref-2">[Ref-2]</a> ARRL, **WSPR**, technische &Uuml;bersicht zu MEPT_JT/WSPR, Nachrichtenformat, Dauer, belegter Bandbreite und SNR-Referenz.
  https://www.arrl.org/wspr

* <a id="ref-3"></a><a href="#ref-3">[Ref-3]</a> Taylor, J. H.; Walker, B. (2010). **WSPRing Around the World**. *QST*, 94(11), pp. 30-32.
  https://www.arrl.org/files/file/History/History%20of%20QST%20Volume%201%20-%20Technology/QS11-2010-Taylor.pdf

* <a id="ref-4"></a><a href="#ref-4">[Ref-4]</a> Lo, S.; Rankov, N.; Mitchell, C.; Witvliet, B. A.; Jayawardena, T. P.; Bust, G.; Liles, W.; Griffiths, G. (2022). **A Systematic Study of 7 MHz Greyline Propagation Using Amateur Radio Beacon Signals**. *Atmosphere*, 13(8), 1340. doi:10.3390/atmos13081340.
  https://www.mdpi.com/2073-4433/13/8/1340

* <a id="ref-5"></a><a href="#ref-5">[Ref-5]</a> Frissell, N. A. et al. (2023). **Heliophysics and amateur radio: citizen science collaborations for atmospheric, ionospheric, and space physics research and operations**. *Frontiers in Astronomy and Space Sciences*, 10, Article 1184171. doi:10.3389/fspas.2023.1184171.
  https://www.frontiersin.org/articles/10.3389/fspas.2023.1184171/full

* <a id="ref-6"></a><a href="#ref-6">[Ref-6]</a> Vanhamel, J.; Machiels, W.; Lamy, H. (2022). **Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band**. *International Journal of Antennas and Propagation*, 2022, Article 4809313. doi:10.1155/2022/4809313.
  https://research.tudelft.nl/en/publications/using-the-wspr-mode-for-antenna-performance-evaluation-and-propag/

* <a id="ref-7"></a><a href="#ref-7">[Ref-7]</a> Zander, J. (2022). **Simple HF antenna efficiency comparisons using the WSPR system**. arXiv:2209.08989. doi:10.48550/arXiv.2209.08989.
  https://arxiv.org/abs/2209.08989

* <a id="ref-8"></a><a href="#ref-8">[Ref-8]</a> Milazzo, C. F. / KP4MD (2011). **Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance**.
  https://www.qsl.net/kp4md/wspr.htm

* <a id="ref-9"></a><a href="#ref-9">[Ref-9]</a> Griffiths, G.; Squibb, N. J. (2017). **Improving HF Band SNR from analysis of WSPR spots**. *Practical Wireless*, October 2017, pp. 23-26.
  https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf

* <a id="ref-10"></a><a href="#ref-10">[Ref-10]</a> WSPR.Rocks, **Help & Documentation**, SpotQ, SQL-Zugriff, Duplicate-Spot-Analyse, Karten, Charts und Heatmaps.
  https://wspr.rocks/help.html

* <a id="ref-11"></a><a href="#ref-11">[Ref-11]</a> Griffiths, G.; Robinett, R. (2020). **Aids to the Presentation and Analysis of WSPR Spots: TimescaleDB database and Grafana**. ARRL/TAPR Digital Communications Conference, 2020.
  https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf

* <a id="ref-12"></a><a href="#ref-12">[Ref-12]</a> WSPRdaemon, **How wsprdaemon Works**, Dokumentation f&uuml;r Multi-Receiver-WSPR/FST4W-Dekodierung, Reporting, Scheduling, Noise- und Doppler-Metadaten.
  https://wsprdaemon.readthedocs.io/en/stable/description/how_it_works.html

* <a id="ref-13"></a><a href="#ref-13">[Ref-13]</a> SOTABEAMS, **WSPRlite Classic / DXplorer**, WSPR-basierte Antennenleistungsanalyse und DX10-Metrik.
  https://www.sotabeams.co.uk/wsprlite-classic

* <a id="ref-14"></a><a href="#ref-14">[Ref-14]</a> WSPR-Station-Compare, **WSPR-Station-compare**, Projektseite mit Verweis auf Vanhamel et al. und Zander.
  https://sites.google.com/myuba.be/wspr-station-compare/home

* <a id="ref-15"></a><a href="#ref-15">[Ref-15]</a> Antenna Performance Analysis Tool, **WSPR-based antenna report generator**.
  https://wspr.bsdworld.org/

* <a id="ref-16"></a><a href="#ref-16">[Ref-16]</a> GM4EAU, **WATT WSPR Analysis Tool**, Excel/VBA-basiertes Werkzeug f&uuml;r WSPR-Reporting, Mapping, Filterung und Timeline-Animation.
  https://www.gm4eau.com/home-page/wspr/

"""
