# docs/doc_de.py

"""
Deutsches Handbuch f?r WSPRadar.
Wird im Web-UI und f?r den PDF-Export verwendet.
"""

DOC_DE = r"""
---

### Inhaltsverzeichnis
* [1. Welche Fragen beantwortet WSPRadar?](#sec-1)
* [2. Schnellstart: erstes nutzbares Ergebnis](#sec-2)
* [3. Den richtigen Test w?hlen](#sec-3)
* [4. Ergebnisse lesen](#sec-4)
  * [4.1 Kartenelemente](#sec-4-1)
  * [4.2 Segment-Inspektor, Station Insights und Drill-Down](#sec-4-2)
* [5. Kernkonzepte: Absolut vs. Vergleich](#sec-5)
  * [5.1 Absolute Analysen](#sec-5-1)
  * [5.2 Vergleichs- und Benchmark-Analysen](#sec-5-2)
  * [5.3 Das bivariate Auswertungsmodell](#sec-5-3)
* [6. Vergleichsmethoden](#sec-6)
  * [6.1 Lokaler Nachbarschafts-Median](#sec-6-1)
  * [6.2 Beste lokale Station](#sec-6-2)
  * [6.3 Spezifische Referenzstation (Buddy-Test)](#sec-6-3)
  * [6.4 Hardware A/B-Test](#sec-6-4)
* [7. Wissenschaftliche Methodik und Annahmen](#sec-7)
  * [7.1 Datenherkunft](#sec-7-1)
  * [7.2 WSPR-Protokoll, SNR und gemeldete Leistung](#sec-7-2)
  * [7.3 Leistungsnormalisierung](#sec-7-3)
  * [7.4 Geografisches Rastering und Projektion](#sec-7-4)
  * [7.5 Median-Aggregationshierarchie](#sec-7-5)
  * [7.6 Zeitliche Synchronisation und Heartbeat-Filter](#sec-7-6)
  * [7.7 Statistische Konfidenz und Wilcoxon-Filter](#sec-7-7)
* [8. Evidenzst?rke und Reproduzierbarkeit](#sec-8)
* [9. Konfigurationsreferenz](#sec-9)
* [10. Limitationen, Haftungsausschluss und Lizenz](#sec-10)
* [Anhang A: Paralleler Betrieb mehrerer WSJT-X Instanzen](#sec-a)
* [Quellen](#sec-ref)

<a id="sec-1"></a>
### 1. Welche Fragen beantwortet WSPRadar?

WSPRadar ist ein experimentelles, datengest?tztes Werkzeug zum Benchmarking von Antennen und Amateurfunkstationen auf Basis ?ffentlicher WSPR-Spots. Es macht aus einem gro?en, crowdsourcing-basierten Beobachtungsnetz strukturierte Evidenz ?ber die eigene Station. WSPRadar ist kein kalibrierter Antennenmessplatz und ersetzt keine kontrollierte HF-Messung. Es kann reale WSPR-Daten aber deutlich besser pr?fbar machen als anekdotische Rapporte oder lockeres A/B-Umschalten.

Das Tool ist um konkrete Amateurfunk-Fragen herum aufgebaut:

* **Wo wird mein Sendesignal geh?rt?** `TX Absolut` kartiert Empf?nger, die mein Rufzeichen decodiert haben.
* **Wen kann meine Station h?ren?** `RX Absolut` kartiert Sender, die mein Empf?nger decodiert hat.
* **Liege ich im Rahmen meiner lokalen WSPR-Nachbarschaft?** `Lokaler Nachbarschafts-Median` ist der Standard-Benchmark.
* **Kann ich mit der besten aktiven lokalen Station mithalten?** `Beste lokale Station` ist ein strenger Best-Peer-Benchmark, kein lokaler Durchschnitt.
* **Wie schneide ich gegen eine bestimmte Station oder einen Funkfreund ab?** `Spezifische Referenzstation`.
* **Hat Antenne A Antenne B am eigenen Standort geschlagen?** `Hardware A/B-Test`, entweder simultan im RX oder mit festem Zeitplan im TX.
* **Sind meine Distanzmuster konsistent mit NVIS- oder DX-Verhalten?** Nahe und weite Distanzringe geben Hinweise, sind aber keine direkte Abstrahlwinkelmessung.
* **Bin ich ein Alligator: werde gut geh?rt, h?re aber schlecht?** TX- und RX-Ergebnisse gegen dasselbe Referenzkonzept vergleichen und nach Asymmetrien suchen.

<a id="sec-2"></a>
### 2. Schnellstart: erstes nutzbares Ergebnis

1. Konfigurationsbereich ?ffnen.
2. `Load Demo Config` anklicken.
3. `TX` oder `RX` starten.
4. Zuerst die Karte lesen: Farbe = medianer Segmentwert, Punkte = Stationskategorien, Fu?balken = Decode Yield.
5. Im Segment-Inspektor ein Kartensegment ausw?hlen.
6. Eine Station-Insights-Zeile ?ffnen und die Drill-Down-Daten pr?fen.
7. CSV exportieren, wenn das Ergebnis reproduziert oder extern gepr?ft werden soll.

Die aktuellen Demo-Daten sind vor allem f?r den lokalen Nachbarschaftsvergleich ausgelegt und k?nnen sp?rlich sein. Umfangreichere Demo-Datens?tze k?nnen sp?ter erg?nzt werden, ohne die Methodik zu ?ndern.

<a id="sec-3"></a>
### 3. Den richtigen Test w?hlen

#### 3.1 Wo werde ich geh?rt? (`TX Absolut`)

* **Experimentdesign:** WSPR mit normalem Rufzeichen, korrektem Locator und realistischer gemeldeter Leistung senden. Ein Zeitfenster w?hlen, das die relevanten Ausbreitungszust?nde abdeckt.
* **Valide wenn:** Die Station im ausgew?hlten Fenster gesendet hat und WSPR-Empf?nger Spots zuverl?ssig hochgeladen haben.
* **Vorsicht bei:** Gemeldete dBm sind nicht zwingend Speisepunktleistung. Geschlossene B?nder erzeugen keine schwachen Spots, sondern keine Spots.
* **Wichtigste Ausgabe:** Kartensegmente, normiertes SNR, Empf?ngerliste und Distanz-/Azimut-Footprint.

#### 3.2 Wen h?re ich? (`RX Absolut`)

* **Experimentdesign:** Empf?nger kontinuierlich betreiben und WSPR-Spots hochladen. Empf?nger, Antenne und Softwareeinstellungen im Zeitfenster stabil halten.
* **Valide wenn:** Der Empf?nger online war und normal decodiert hat.
* **Vorsicht bei:** RX-Ergebnisse enthalten die gesamte Empfangskette: Antenne, Empf?nger, Audiopfad, lokales Rauschen, Decoderverhalten und Upload-Zuverl?ssigkeit.
* **Wichtigste Ausgabe:** Kartensegmente, normiertes Remote-Sender-SNR und Senderliste.

#### 3.3 Bin ich typisch f?r aktive lokale WSPR-Stationen? (`Lokaler Nachbarschafts-Median`)

* **Experimentdesign:** Diesen Benchmark zuerst f?r lokale Selbsteinsch?tzung nutzen. Einen Radius w?hlen, der gen?gend aktive Peers liefert, ohne sehr unterschiedliche Ausbreitungsumgebungen zu mischen. In dichten Regionen kann ein kleinerer Radius reichen; in d?nnen Regionen kann ein gr??erer Radius n?tig sein.
* **Valide wenn:** Mehrere lokale Stationen im gew?hlten Radius in denselben WSPR-Zyklen und auf vergleichbaren Pfaden aktiv sind.
* **Vorsicht bei:** Die Nachbarschaft ist kein kalibriertes Referenzarray. Sie ist der Median der aktiven Peers in den Daten, und der Peer-Satz kann sich zyklusweise ?ndern.
* **Wichtigste Ausgabe:** Delta SNR gegen Nachbarschafts-Median, Yield-Balken, Station Insights und erweiterter Referenz-Drill-Down.

#### 3.4 Kann ich mit der st?rksten lokalen Station mithalten? (`Beste lokale Station`)

* **Experimentdesign:** Nur verwenden, wenn bewusst ein strenges Ziel gesucht wird. Verglichen wird gegen den st?rksten aktiven lokalen Peer pro Pfad/Zyklus.
* **Valide wenn:** Das Ziel ein Best-Local-Peer-Stresstest ist, nicht eine zentrale Nachbarschafts-Baseline.
* **Vorsicht bei:** Das ist keine lokale Durchschnittsleistung. Die Referenz kann zyklusweise wechseln und zu einer beweglichen Best-Peer-H?llkurve werden.
* **Wichtigste Ausgabe:** Delta SNR gegen beste lokale Station, Yield-Balken und Best-Reference-Drill-Down.

#### 3.5 Bin ich besser als eine spezifische Referenzstation? (`Spezifische Referenzstation`)

* **Experimentdesign:** Eine Referenzstation w?hlen, deren Standort, Leistung, Antenne und Betriebsplan bekannt sind. Gleiches Band und ?berlappende Zeitfenster verwenden.
* **Valide wenn:** Beide Rufzeichen aktiv sind und gen?gend gleiche Remote-Peers im selben Zyklus teilen.
* **Vorsicht bei:** Unterschiede sind Stationssystem-Unterschiede, kein reiner Antennengewinn. Standort, Antenne, Leistung, Speiseleitung, Empfangskette, Polarisation und lokales Rauschen k?nnen alle relevant sein.
* **Wichtigste Ausgabe:** Joint Spots, exklusive Decodes, stationsbezogener Delta SNR und Drill-Down-Zeilen.

#### 3.6 Hat RX-Setup A RX-Setup B geschlagen? (`RX A/B-Test`)

* **Experimentdesign:** Zwei wirklich unabh?ngige Empfangsketten verwenden. Nicht beide Decoder aus derselben Audiodatei oder demselben virtuellen Audiopfad speisen. Unterschiedliche Reporting-Identit?ten nutzen, damit beide Streams in der WSPR-Datenbank erscheinen, und Zeitsynchronisation pr?fen.
* **Valide wenn:** Beide Empf?nger dieselben Remote-WSPR-Sendungen gleichzeitig decodieren und unterscheidbare Rufzeichen/Suffixe melden.
* **Vorsicht bei:** Duplicate-Filter, gemeinsame Audiopfade, unterschiedliche AGC-/Audioeinstellungen oder unsynchronisierte Uhren k?nnen den Vergleich ung?ltig machen.
* **Wichtigste Ausgabe:** Same-cycle Delta SNR, gemeinsamer/exklusiver Decode Yield und stationsbezogener Drill-Down.

#### 3.7 Hat TX-Setup A TX-Setup B geschlagen? (`TX A/B-Test`)

* **Experimentdesign:** Deterministisches fixes Timing verwenden. Leistung, Speiseleitung, Tuner-Einstellungen und Band konstant halten, au?er bei der getesteten Variable. Lange genug laufen lassen, um die relevanten Ausbreitungszust?nde abzudecken; mehrt?gige L?ufe sind vorzuziehen, weil fixe Slot-Effekte ?ber vollst?ndige Tageszyklen besser ausmitteln.
* **Valide wenn:** Ein Rufzeichen mit festem, deterministischem Zeitplan f?r A und B ?ber ein ausreichend langes Fenster sendet.
* **Vorsicht bei:** TX ist zeitgebinnt, nicht simultan. Mehrt?giges fixes Timing reduziert Zeitkonfundierung deutlich, beweist aber nicht, dass jeder zeitkorrelierte Effekt verschwunden ist.
* **Wichtigste Ausgabe:** Time-bin Delta SNR, Joint Bins, Decode Yield und Bin-Level-Drill-Down.

<a id="sec-4"></a>
### 4. Ergebnisse lesen

<a id="sec-4-1"></a>
#### 4.1 Kartenelemente

* **Heatmap-Segmente:** Absolute Modi zeigen normiertes SNR in dB. Vergleichsmodi zeigen medianen Delta SNR gegen den gew?hlten Benchmark.
* **Vergleichsfarbskala:** Positive Werte bedeuten, dass die eigene Station/das eigene Setup im Segment st?rker als die Benchmark ist; negative Werte zeigen schw?chere Performance. WSPRadar nutzt die g?ngige Amateurfunk-Konvention `1 S-Stufe = 6 dB`.
* **Distanzringe:** Nahe Ringe k?nnen mit Short-Skip oder NVIS konsistent sein; weite Ringe k?nnen mit flacherem DX-Verhalten konsistent sein. Distanz ist keine direkte Elevationswinkelmessung, weil ionosph?rischer Modus, Band, Zeit, Saison und Sonnenzustand mitwirken.
* **Punkte:** Einzelne Stationen werden als Punkte gezeichnet. Gr?n = Joint Decodes im selben Zyklus. Gelb-orange = beide Seiten haben die Station geh?rt, aber asynchron. Violett = nur eigene Station/eigenes Setup. Wei? = nur Referenz.
* **Polmarkierungen:** Nord- und S?dpol helfen bei der Interpretation polarer Ausbreitungspfade.
* **Footer und 1D-Venn-Balken:** `SPOTS` zeigt das Rohdatenvolumen. `STATIONS` pr?ft, ob der Footprint breit ist oder nur von wenigen aktiven Stationen getragen wird. Diese Balken sind wichtig, weil SNR-Deltas allein Decode/No-Decode-Verhalten verbergen k?nnen.
* **High-Resolution Export:** Die Toolbar oberhalb jeder Karte kann eine 300-DPI-Version f?r Publikationen rendern, ohne die interaktive Oberfl?che dauerhaft zu blockieren.

<a id="sec-4-2"></a>
#### 4.2 Segment-Inspektor, Station Insights und Drill-Down

Der Segment-Inspektor ist die Auditschicht unterhalb der Karten. Distanzring und Himmelsrichtung ausw?hlen, um die Evidenz hinter einem Segment zu pr?fen.

1. **Absolute Modi:** Das Histogramm zeigt normierte SNR-Werte der beteiligten Stationen. Die x-Achse basiert auf Stationsmedianen. Die rote gestrichelte Linie markiert den finalen Segmentmedian.
2. **Vergleichsmodi:** Das Histogramm zeigt Delta-SNR-Werte. Es zeigt, ob ein Segmentmedian aus konsistenter ?berlegenheit oder aus breiter, instabiler Streuung entsteht.
3. **Station Insights:** Die Tabelle listet beteiligte Remote-Stationen. In Vergleichsmodi trennt sie Joint Decodes von exklusiven Decodes und zeigt den stationsbezogenen medianen Delta SNR.
4. **Drill-Down:** Ein Klick auf eine Station-Insights-Zeile ?ffnet die zyklusgenaue Evidenz. In normalen Vergleichsmodi zeigt jeder Joint-WSPR-Zyklus die gepaarten SNR-Werte und den Delta SNR.
5. **Drill-Down beim lokalen Nachbarschafts-Median:** Der Referenzpool wird expandiert. Statt nur `Ref Pool` zu zeigen, listet die Tabelle alle lokalen Referenzstationen dieses Zyklus mit Locator, Distanz, normiertem Referenz-SNR, aggregiertem Nachbarschaftsmedian des Zyklus, eigenem SNR und Delta SNR. So l?sst sich der Median direkt nachvollziehen.
6. **Drill-Down beim sequenziellen TX A/B:** Statt Same-Cycle-Paaren werden Zeitfenster gezeigt. Sichtbar sind `Micro-Med A`, `Micro-Med B` und der resultierende Bin-Delta. Gegenseitige Mikromediane werden in Single-Setup-Zeilen ausgeblendet, damit fehlende Paare nicht als Nullwerte missverstanden werden.
7. **Raw Spots Toggle und Async Both:** `Show Non-Joint` zeigt isolierte Decodes. Fehlendes SNR wird als `None`, nicht als `0.0`, angezeigt. Wenn beide Setups eine Station h?ren, aber nie im selben Zyklus, kann der Yield-Chart `Async Both` zeigen.
8. **Filter und Export:** Multi-Select, dynamische Filter und CSV-Export machen den Segment-Inspektor zur reproduzierbaren Rohdaten-Auditfl?che.

<a id="sec-5"></a>
### 5. Kernkonzepte: Absolut vs. Vergleich

<a id="sec-5-1"></a>
#### 5.1 Absolute Analysen

Absolute Analysen beantworten: **Gibt es einen offenen Pfad?**

* **TX Absolut:** isoliert Spots, in denen das eigene Rufzeichen sendet. Die Karte zeigt Empf?nger, die das Signal decodiert haben. Das misst reale Sendereichweite und Skip-Zonen, normiert auf 1 W, sofern gemeldete Leistung verf?gbar ist.
* **RX Absolut:** isoliert Spots, in denen das eigene Rufzeichen empf?ngt. Die Karte zeigt Sender, die der Empf?nger decodiert hat. Das misst reale Empfangsreichweite und -empfindlichkeit, normiert auf die gemeldete Leistung des Remote-Senders.

Absolute Karten sind sehr gut f?r Coverage- und Ausbreitungsfragen. Allein sind sie keine fairen Hardwarevergleiche, weil Ausbreitung, Sendeleistungen, Empf?ngerrauschen und Stationsaktivit?t nicht kontrolliert sind.

<a id="sec-5-2"></a>
#### 5.2 Vergleichs- und Benchmark-Analysen

Vergleichsanalysen beantworten: **Wie hat meine Station/mein Setup relativ zu einer Benchmark unter m?glichst passenden Bedingungen abgeschnitten?**

Der Kern ist Paarbildung. Bei TX-Vergleichen werden zwei Sendesignale m?glichst vom selben Remote-Empf?nger bewertet. Das reduziert den Einfluss von dessen Rauschpegel und Antenne stark. Bei RX-Vergleichen bewerten zwei Empf?nger m?glichst denselben Remote-Sender. Das reduziert den Einfluss von Remote-Sendeleistung und gemeinsamem Ausbreitungspfad stark.

Das ist leistungsf?hig, aber wissenschaftlich korrekt ist **Konfounder-Reduktion**, nicht perfekte Eliminierung. WSPR bleibt ein crowdsourcing-basierter Beobachtungsdatensatz.

<a id="sec-5-3"></a>
#### 5.3 Das bivariate Auswertungsmodell

Eine reine Median-Delta-SNR-Analyse kann unter Survivorship Bias leiden. Eine bessere Antenne decodiert oft sehr schwache Signale, die eine schlechtere Antenne verpasst. Diese zus?tzlichen Grenzfall-Spots k?nnen den Median der besseren Antenne senken, wenn alles naiv zusammengeworfen wird.

WSPRadar trennt deshalb zwei Signale:

1. **System Sensitivity / Decode Yield:** z?hlt exklusive und gemeinsame Decodes. Das erfasst Reichweite an der Decodiergrenze.
2. **Hardware Linearity / Delta SNR:** nutzt nur gepaarte Joint Spots oder gepaarte Zeit-Bins. Das sch?tzt den bedingten Gain/SNR-Unterschied, wenn beide Setups vergleichbare Evidenz erzeugt haben.

Beides muss zusammen gelesen werden. Ein Setup kann besseren Yield, aber niedrigeren bedingten SNR haben, wenn es viele Grenzfallsignale decodiert. Umgekehrt kann ein Setup auf Joint Spots starken positiven Delta SNR zeigen, aber schlechten Yield haben, wenn es viele schwache Pfade verpasst.

<a id="sec-6"></a>
### 6. Vergleichsmethoden

<a id="sec-6-1"></a>
#### 6.1 Lokaler Nachbarschafts-Median

Dies ist der Standard-Benchmark und die empfohlene erste Antwort auf: **Bin ich f?r meine Region im Rahmen?**

WSPRadar sammelt aktive WSPR-Stationen innerhalb des gew?hlten Nachbarschaftsradius. F?r jeden WSPR-Zyklus und jeden passenden Remote-Pfad berechnet es den Median des normierten SNR aller aktiven lokalen Referenzstationen im Radius. Die eigene Station wird gegen diesen zyklusbezogenen Nachbarschaftsmedian verglichen.

Wissenschaftliche Interpretation:

* Sch?tzt die zentrale Performance der aktiven lokalen WSPR-Umgebung.
* Robust gegen eine einzelne ungew?hnlich starke oder schwache lokale Station.
* Fehlende Spots werden nicht als numerische Werte erfunden. Wenn ein Nachbar in diesem Zyklus nicht decodiert hat oder nicht decodiert wurde, wird das nicht als `0 dB` gez?hlt.
* Bei gerader Anzahl lokaler Referenzstationen wird der Mittelpunkt-Median verwendet.
* Der Referenzpool kann sich zyklusweise ?ndern, weil WSPR-Aktivit?t zyklusweise schwankt.

Beste Verwendung:

* Allgemeine Selbsteinsch?tzung.
* RX/TX-Benchmarking gegen die lokale Nachbarschaft.
* Erkennen, ob die eigene Station konsistent ?ber oder unter der lokalen zentralen Tendenz liegt.

<a id="sec-6-2"></a>
#### 6.2 Beste lokale Station

Dies ist die strenge Variante des lokalen Benchmarks. F?r jeden Zyklus und Remote-Pfad vergleicht WSPRadar gegen die st?rkste aktive lokale Station im gew?hlten Radius.

Wissenschaftliche Interpretation:

* Es ist eine Best-Local-Peer-H?llkurve.
* Die Identit?t der Referenzstation kann von Zyklus zu Zyklus wechseln.
* Die Frage lautet: **Wenn die beste aktive lokale Station diesen Pfad erreicht oder geh?rt hat, wie war ich im Vergleich?**
* Dieser Benchmark ist absichtlich schwerer zu schlagen als der Nachbarschaftsmedian.

Beste Verwendung:

* Stress-Test gegen starke lokale Performer.
* Finden von Distanz-/Azimutbereichen, in denen die eigene Station gegen den lokalen Best Case abf?llt.
* Vermeiden der Fehlannahme, "lokaler Benchmark" bedeute "lokaler Durchschnitt".

<a id="sec-6-3"></a>
#### 6.3 Spezifische Referenzstation (Buddy-Test)

Der Buddy-Test ist ein 1:1-Vergleich mit einer bekannten Station. Man definiert ein anderes Referenzrufzeichen, zum Beispiel einen Funkfreund 10 km entfernt. WSPRadar isoliert F?lle, in denen beide Signale vom selben Remote-Empf?nger im selben 2-Minuten-WSPR-Zyklus decodiert werden, oder in denen beide Empf?nger denselben Remote-Sender im selben Zyklus decodieren.

Das ist stark, wenn beide Stationen gleichzeitig aktiv sind und gen?gend Remote-Peers teilen. Es bleibt aber ein Stationssystem-Vergleich: Unterschiede k?nnen Antenne, Empf?nger, Sender, lokales Rauschen, Speiseleitung, Aufbauort, Polarisation und Gel?nde enthalten.

<a id="sec-6-4"></a>
#### 6.4 Hardware A/B-Test

Der Hardware A/B-Test ist f?r eigene Ausr?stung am eigenen Standort gedacht. Er ist nur valide, wenn jede nicht getestete Variable so konstant wie praktikabel gehalten wird: Band, Zeitfenster, Leistung, Speiseleitungsverluste, Empfangskette, Audiokette, Decodiersoftware und Locator-Meldung.

**RX A/B-Test (simultan):**

Zwei parallele Empf?nger decodieren dieselben Remote-WSPR-Sendungen gleichzeitig. Damit das Reporting-Netz die Streams nicht als Duplikate behandelt, m?ssen die Empf?nger unterscheidbare Rufzeichen oder Suffixe melden, z. B. Hauptrufzeichen f?r Setup A und Suffix f?r Setup B. Audio- und Speicherpfade m?ssen physisch getrennt sein. Anhang A beschreibt eine WSJT-X-Instanztrennung.

**TX A/B-Test (sequenziell mit festem Zeitplan):**

Setup A und Setup B k?nnen mit demselben Rufzeichen nicht gleichzeitig senden. WSPRadar nutzt daher deterministisches Time-Slicing. Ein Sender oder Controller weist ein Setup einem festen Slotmuster zu und das andere dem Gegenmuster. Das Tool gruppiert die Daten in Zeit-Bins, berechnet je Setup einen Mikro-Median im Bin und daraus den Bin-Delta.

Das ist ein praktischer Engineering-Kompromiss. Er ist vertretbar, wenn der Lauf lang genug ist, idealerweise mehrere Tage und vollst?ndige Tageszyklen, weil viele kurzzeitige Ausbreitungseffekte ausmitteln. Da die Zuordnung aber fix und nicht randomisiert ist, d?rfen zeitkorrelierte Effekte nicht als mathematisch eliminiert beschrieben werden. Korrekt ist: **Fixed-schedule Multi-Day TX A/B reduziert Zeitkonfundierung deutlich und liefert Evidenz aus gepaarten Zeit-Bins.**

Hardware-Hinweis: Ein solcher Test erfordert deterministische Zeitsteuerung. Ein QMX-Transceiver l?sst sich beispielsweise mit festen Parametern wie `frame=10` und `start=2` programmieren. Standard-WSJT-X mit zuf?lligem Sendemuster ist ohne Zusatzsteuerung nicht f?r festen TX A/B geeignet.

Warum keine Multi-Cycle-WSPR-Suffixe f?r Single-TX A/B? Compound-Rufzeichen k?nnen Multi-Message-Verhalten erzwingen und den Decode Yield senken, weil nicht alle Empf?nger alle ben?tigten Nachrichtentypen gleich zuverl?ssig decodieren. K?nstliche Suffixe wie `/1` oder `/2` k?nnen au?erdem je nach Land unzul?ssig sein. `/P` sollte nur genutzt werden, wenn es f?r den tats?chlichen Betrieb rechtlich passt. F?r TX A/B bevorzugt WSPRadar deshalb feste Zeitschlitze mit normalem Rufzeichen.

<a id="sec-7"></a>
### 7. Wissenschaftliche Methodik und Annahmen

<a id="sec-7-1"></a>
#### 7.1 Datenherkunft

WSPRadar liest historische WSPR-Spots ?ber wspr.live. Die wspr.live-Dokumentation beschreibt die Daten als Rohdaten, wie sie von WSPRnet gemeldet und ver?ffentlicht werden, und warnt vor Duplikaten, falschen Spots und anderen Fehlern. Au?erdem gibt es f?r die ehrenamtlich betriebene Infrastruktur keine Garantie f?r Korrektheit, Verf?gbarkeit oder Stabilit?t.

WSPRadar mindert viele vorgelagerte Datenprobleme durch mehrschichtige Aggregation und Filter: Same-Cycle-Paarbildung, Stationsmediane, Segmentmediane, Mindest-Sample-Schwellen, Moving-Station-Filter und optionale Pr?fix-Ausschl?sse. Diese Ma?nahmen reduzieren den Einfluss isolierter Duplikate, sporadischer falscher Spots, One-Hit-Decodes und Receiver-Density-Bias erheblich. Sie machen den vorgelagerten Datensatz nicht kalibriert oder fehlerfrei, und ein plausibler wiederholter Fehler kann weiterhin durchrutschen; der Anspruch ist Robustheit, nicht Immunit?t.

<a id="sec-7-2"></a>
#### 7.2 WSPR-Protokoll, SNR und gemeldete Leistung

WSPR ist f?r die Untersuchung potenzieller Ausbreitungspfade mit Low-Power-Baken gedacht. WSPR-Nachrichten enthalten Rufzeichen, Locator und Leistung in dBm. WSPR-2-Sendungen dauern etwa 110,6 Sekunden und starten zwei Sekunden nach einer geraden UTC-Minute. Die ARRL-WSPR-Dokumentation beschreibt den Mindest-S/N auf der WSJT-Skala mit 2500-Hz-Referenzbandbreite.

F?r WSPRadar bedeutet das:

* SNR ist ein Decoderwert in dB auf der WSPR/WSJT-Skala, referenziert auf 2500 Hz.
* Die gemeldete Sendeleistung ist Teil der WSPR-Nachricht und wird von WSPRadar nicht unabh?ngig verifiziert.
* Eingetragene dBm k?nnen von Senderausgangsleistung, Speisepunktleistung oder EIRP abweichen, etwa durch Kalibrierfehler, Foldback, Speiseleitungsverlust, Tuner-Verlust oder Fehlanpassung.

<a id="sec-7-3"></a>
#### 7.3 Leistungsnormalisierung

Um Spots mit unterschiedlichen gemeldeten Sendeleistungen vergleichen zu k?nnen, normalisiert WSPRadar das SNR auf 1 W / 30 dBm:

$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$

Das ist f?r absolute TX/RX-Karten und lokale TX-Vergleiche zentral. Es entfernt den gemeldeten Leistungsanteil aus dem Vergleich, aber nur so gut, wie die gemeldete Leistung stimmt. Antennengewinn, Speiseleitungsverlust, Kalibrierfehler oder EIRP-Unterschiede werden dadurch nicht automatisch korrigiert.

<a id="sec-7-4"></a>
#### 7.4 Geografisches Rastering und Projektion

R?umliche Daten werden in einer mittabstandstreuen Azimutalprojektion dargestellt, zentriert auf dem Maidenhead-Locator des Nutzers. Die Kartenengine nutzt intern eine sph?rische Erde mit 6371 km Radius, damit Tabellendistanzen und geplottete Kartenpositionen derselben Geometrie folgen.

Die Karte nutzt:

* konzentrische Distanzb?nder von 2500 km;
* Azimut-Wedges, z. B. 22,5-Grad-Kompasssektoren;
* eindeutige Segment-IDs f?r Aggregation und Inspektion.

Die Projektion ist f?r WSPRadars visuelle Analyse intern konsistent. Sie sollte nicht als geod?tische Vermessung mit Survey-Pr?zision beschrieben werden.

<a id="sec-7-5"></a>
#### 7.5 Median-Aggregationshierarchie

WSPRadar nutzt Mediane, um Ausrei?er und ungleiche Stationsaktivit?t zu d?mpfen.

* **Zyklusmedian:** Im lokalen Nachbarschafts-Median ist die Referenz f?r einen WSPR-Zyklus/Pfad der Median aktiver lokaler Referenzstationen in diesem Zyklus.
* **Stationsmedian:** F?r eine Remote-Station berechnet WSPRadar den Median der qualifizierenden Spot- oder Bin-Werte.
* **Segmentmedian:** Der finale Kartenwert ist der Median der Stationsmediane.

Diese "Median des Medians"-Struktur reduziert Receiver-Density-Bias. Ein dichter Empf?ngercluster soll eine d?nn besetzte Region nicht nur deshalb dominieren, weil er mehr Zeilen erzeugt.

<a id="sec-7-6"></a>
#### 7.6 Zeitliche Synchronisation und Heartbeat-Filter

WSPRadar validiert Vergleichszyklen nur, wenn das eigene Setup nachweislich aktiv war.

* Im TX-Modus muss das eigene Signal im relevanten Zyklus/Slot von mindestens einer Station weltweit decodiert worden sein.
* Im RX-Modus muss der eigene Empf?nger im relevanten Zyklus mindestens eine Station decodiert haben.

Zeitliche Synchronisation ist eine der st?rksten Kontrollen von WSPRadar. Same-Cycle-Paarbildung reduziert schnelle QSB-/Fading-Effekte deutlich, weil beide Seiten in derselben zweimin?tigen WSPR-Gelegenheit bewertet werden. Bei TX-Vergleichen reduziert derselbe Remote-Empf?nger empfangsseitiges QRM, Noise-Floor- und Antenneneffekte. Bei RX-Vergleichen reduziert derselbe Remote-Sender Sendeleistungs- und gemeinsame Pfadvariation. Der Heartbeat-Filter erg?nzt einen separaten Schutz: Wenn die Station nachts ausgeschaltet ist, werden Referenzspots in diesem Offline-Zeitraum nicht als Niederlagen f?r die eigene Hardware gez?hlt.

Das macht nicht jeden Vergleich perfekt fair. Es reduziert die dominanten Timing-, Fading- und Offline-Bias-Konfounder in synchronen Modi. Sequenzieller TX A/B bleibt der Sonderfall: Time-Binning und mehrt?gige fixe Zeitpl?ne reduzieren Makro-Fading/Zeitdrift, sind aber nicht gleichwertig zu simultaner Same-Cycle-Paarbildung.

<a id="sec-7-7"></a>
#### 7.7 Statistische Konfidenz und Wilcoxon-Filter

WSPRadar kann optional einen Wilcoxon-Vorzeichen-Rang-Test als Compare-Map-Filter verwenden. SciPy dokumentiert diesen Test f?r verbundene gepaarte Stichproben und beschreibt ihn ausdr?cklich ?ber die Verteilung gepaarter Differenzen.

Korrekte Interpretation:

* Der Test ist ein n?tzlicher Robustheitsfilter f?r gepaarte Delta-SNR-Werte.
* Ein p-Wert ist keine Effektgr??e.
* Segmentweise p-Werte erzeugen ein Multiple-Comparison-Risiko ?ber die Karte.
* WSPR-SNR-Werte sind quantisiert und oft zeitlich autokorreliert; das schw?cht ideale Lehrbuchannahmen.
* Null-Differenzen und Ties m?ssen vorsichtig behandelt werden; auch das dokumentiert SciPy.

Wilcoxon-Filterung sollte deshalb als statistische Evidenz, nicht als Beweis, beschrieben werden. Eine wissenschaftlich st?rkere sp?tere Version k?nnte Bootstrap-Konfidenzintervalle und False-Discovery-Rate-Korrektur ?ber Kartensegmente erg?nzen.

<a id="sec-8"></a>
### 8. Evidenzst?rke und Reproduzierbarkeit

Empfohlene Evidenzsprache:

* **Schwache Evidenz:** sehr wenige Joint-Zyklen, sehr wenige Stationen oder ein Ergebnis, das von einem Ausrei?er getragen wird.
* **Nutzbare Evidenz:** mehrere Stationen pro Segment, mehrere Joint-Zyklen oder Bins pro Station, konsistente Delta-SNR-Richtung und plausibles Yield-Verhalten.
* **Starke Evidenz:** ?ber mehrere Tage oder getrennte Runs wiederholt, ?ber benachbarte Segmente oder B?nder plausibel stabil, nicht von einer Station dominiert und durch exportierte Rohdaten belegbar.

Reproduzierbarkeits-Checkliste:

* WSPRadar-Version oder Git-Commit.
* UTC-Start- und Endzeit.
* Band.
* TX/RX-Richtung.
* Benchmark-Modus und lokale Benchmark-Methode.
* Nachbarschaftsradius oder Referenzrufzeichen.
* Ziel-/Referenz-Locator.
* Min Spots/Station und Min Stations/Segment.
* Solar-State-Filter.
* Ausgeschlossene Pr?fixe und Moving-Station-Filter.
* Wilcoxon-Einstellung.
* Exportierte CSV und Screenshots von Karte und Segment-Inspektor.

**Mindestdaten:**

Es gibt keine universelle magische Zahl. Explorative Ergebnisse d?rfen sichtbar bleiben, sollten aber so bezeichnet werden. F?r ernsthafte Aussagen braucht es gen?gend Joint Spots oder Bins, um die Verteilung zu pr?fen, nicht nur den finalen Median. F?r publikationsnahe Aussagen sollten Rohdaten exportiert und Experimente wiederholt werden.

<a id="sec-9"></a>
### 9. Konfigurationsreferenz

**Core-Parameter:**

* **Zielrufzeichen:** prim?re Station unter Auswertung.
* **QTH Locator:** mathematisches Zentrum der Kartenprojektion. G?ltigen 4- oder 6-Zeichen-Maidenhead-Locator verwenden.
* **Band und Zeitfenster:** definieren das WSPR-Datenfenster. Zeit wird in UTC behandelt.

**Vergleichsparameter:**

* **Benchmark Mode:** `Lokaler Nachbarschafts-Benchmark`, `Fremdes Rufzeichen (Buddy-Test)` oder `Hardware A/B-Test`.
* **Lokale Benchmark-Methode:** standardm??ig `Lokaler Nachbarschafts-Median`, optional `Beste lokale Station` als strenge Best-Peer-H?llkurve.
* **Nachbarschaftsradius:** geografische Grenze f?r lokale Referenzstationen.
* **Referenzrufzeichen:** externer Gegenpart f?r Buddy-Test.
* **A/B-Test Setup:** simultaner `RX Test` oder fixed-schedule `TX Test`.
* **Target/Reference Locator:** 6-Zeichen-Locators zur Trennung simultaner RX-Streams.
* **Target/Reference Time Slot:** feste Slotzuweisung f?r sequenzielle TX-Tests.
* **Time Window (Bins):** Bin-Gr??e f?r sequenzielle TX-A/B-Paarbildung.

**Advanced Settings:**

* **Lokaler QTH Sonnenstand:** filtert nach berechneter Sonnenh?he am eigenen QTH: Daylight, Nighttime oder Greyline.
* **Exclude Prefixes:** kommagetrennte Liste von Rufzeichenpr?fixen oder Rufzeichen, z. B. Telemetrieballons oder bekannte unerw?nschte Quellen.
* **Exclude Moving Stations:** entfernt Stationen, die w?hrend des Analysefensters ihren 4-Zeichen-Locator ?ndern, z. B. Ballons, mobile oder maritime Stationen.
* **Map Scope:** visueller Kartenradius.
* **Min. Spots/Station:** filtert One-Hit-Wonders und passt sich dem Vergleichsmodus an.
* **Min. Stations/Segment:** Mindeststationszahl f?r die Darstellung eines Segments.
* **Compare Map Statistical Confidence:** optionale Wilcoxon-basierte Filterung.

<a id="sec-10"></a>
### 10. Limitationen, Haftungsausschluss und Lizenz

**Limitationen:**

* **Crowd-sourced Daten:** WSPR-Spots k?nnen Duplikate, falsche Spots, falsche Leistung, falschen Locator oder empfangsseitige Fehler enthalten.
* **Nur erfolgreiche Decodes:** WSPR protokolliert Decodes, nicht alle fehlgeschlagenen Empfangsversuche. Tote B?nder senken nicht den absoluten Median; sie verringern die Existenz von Spots.
* **Gemeldete Leistung:** Normalisierung mindert Unterschiede in gemeldeter Leistung, und mehrere Vergleichsmodi reduzieren dieses Problem zus?tzlich durch Paarbildung gegen denselben Sender oder dasselbe Rufzeichen. Jede Analyse, die auf gemeldeten dBm basiert, setzt aber weiterhin voraus, dass der gemeldete Wert ungef?hr stimmt.
* **Sequenzieller TX:** Fixed-schedule TX A/B reduziert Zeitkonfundierung, eliminiert sie aber nicht perfekt.
* **Distanz ist kein Winkel:** Distanzringe k?nnen Ausbreitungsverhalten nahelegen, messen aber keinen Abstrahlwinkel direkt.
* **Polarisation und lokale Umgebung:** WSPRadar misst reale Stationssystem-Performance, einschlie?lich Antenne, Sender/Empf?nger, Speiseleitung, Gel?nde, Polarisation, lokalem QRM und Softwareverhalten.
* **Performance-Limits und Latenz:** Query-Fenster sind zum Schutz der Datenbank begrenzt; neue Spots k?nnen etwa 15 bis 30 Minuten brauchen, bis sie sichtbar werden.

**Haftungsausschluss:**

WSPRadar ist ein experimentelles Open-Source-Projekt und wird ohne Gew?hrleistung bereitgestellt. Quellcode und mathematisches Modell sind pr?fbar, aber der Entwickler kann keine Genauigkeit, Vollst?ndigkeit, Verf?gbarkeit oder Eignung f?r einen bestimmten Zweck garantieren. Gr??ere finanzielle Entscheidungen, etwa Kauf oder Verkauf teurer Antennen oder Funkhardware, sollten nie ausschlie?lich auf WSPRadar-Ausgaben basieren.

**Lizenz:**

WSPRadar ist freie Software unter der GNU Affero General Public License (AGPLv3). Die Lizenz stellt sicher, dass der Quellcode, einschlie?lich ?nderungen an Netzwerkdiensten, der Amateurfunk-Community zug?nglich bleibt.

<a id="sec-a"></a>
### Anhang A: Paralleler Betrieb mehrerer WSJT-X Instanzen

Diese Anleitung beschreibt die Erzeugung einer zweiten OS-isolierten WSJT-X-Umgebung, z. B. f?r einen SDR, inklusive Konfigurationsmigration und zwingender Pfadtrennung.

#### 1. Instanziierung (OS-Level-Isolation)

Standardm??ig verhindert das WSJT-X-Lockfile Mehrfachstarts. Die Trennung erfolgt mit einem Command-Line-Parameter, der eine neue Sandbox im Windows-`AppData`-Verzeichnis erzwingt.

1. Desktop-Verkn?pfung f?r `wsjtx.exe` erstellen.
2. Eigenschaften der Verkn?pfung ?ffnen.
3. Das Feld `Ziel` nach diesem Muster ?ndern, Parameter au?erhalb der Anf?hrungszeichen:
   `"C:\Program Files\wsjtx\bin\wsjtx.exe" --rig-name=SDR`
4. Diese Verkn?pfung einmal starten und sofort wieder schlie?en. Dadurch wird `%LOCALAPPDATA%\WSJT-X - SDR` initialisiert.

#### 2. Konfigurationsmigration (Klonen)

WSJT-X bietet keinen internen Export f?r Instanzen. Der Klon muss auf Dateisystemebene erfolgen.

1. In den prim?ren Konfigurationsordner navigieren: `%LOCALAPPDATA%\WSJT-X`
2. `WSJT-X.ini` kopieren.
3. In den neuen Ordner navigieren: `%LOCALAPPDATA%\WSJT-X - SDR`
4. Datei einf?gen und die beim Erststart erzeugte `.ini` ?berschreiben.
5. Die eingef?gte Datei exakt passend zur neuen Instanz umbenennen: `WSJT-X - SDR.ini`

#### 3. Zwingende Pfadtrennung (Audio und Speicherorte)

Da die Konfiguration geklont wurde, zeigen beide Instanzen m?glicherweise noch auf dieselben Hardwareeing?nge und tempor?ren Speicherorte. F?r WSPR kann das zu identischen Decodes f?hren, weil dieselbe `.wav` analysiert wird, und File-Lock-Fehler erzeugen.

Neue SDR-Instanz ?ffnen und `File > Settings > Audio` aufrufen. Anpassen:

* **Soundcard > Input:** Audio-Interface auf die zweite Empf?ngerquelle setzen, z. B. ein dediziertes Virtual Audio Cable.
* **Save Directory:** Pfad in die isolierte Umgebung ?ndern, z. B.:
  `C:\Users\[User]\AppData\Local\WSJT-X - SDR\save`
* **AzEl Directory:** auch diesen Pfad ?ndern, z. B.:
  `C:\Users\[User]\AppData\Local\WSJT-X - SDR`

Nach dem Neustart sind Datenstr?me, Hardwarezugriffe und tempor?re WSPR-Dateien von der Prim?rinstanz getrennt.

<a id="sec-ref"></a>
### Quellen

* ARRL, WSPR technical overview: https://www.arrl.org/wspr
* wspr.live Dokumentation und Datenbank-Disclaimer: https://wspr.live/
* SciPy Wilcoxon signed-rank documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html
* WSJT-X User Guide, WSPR and SNR reference bandwidth: https://wsjt.sourceforge.io/wsjtx-doc/wsjtx-main-3.0.0.html
"""
