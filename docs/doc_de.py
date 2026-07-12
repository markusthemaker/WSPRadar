# docs/doc_de.py

"""Autoritatives deutsches Endnutzer- und Wissenschaftshandbuch fuer WSPRadar."""

DOC_DE = r"""
---

<a id="sec-1"></a>
### 1. Warum WSPRadar

<a id="sec-1-0"></a>
#### 1.0 Was WSPRadar besonders macht

WSPR kann zeigen, dass ein Signal geh&ouml;rt wurde. WSPRadar stellt die n&auml;chste, praktisch wichtigere Frage: **Wie hat die getestete Station oder Konfiguration im Vergleich mit einer sinnvollen Referenz unter vergleichbaren Bedingungen abgeschnitten?**

In diesem Handbuch hei&szlig;t die untersuchte Station oder Konfiguration **Target**. WSPRadar kann dieses Target allein untersuchen, zwei lokale Hardwarepfade vergleichen, es einer bekannten Referenzstation gegen&uuml;berstellen oder es mit aktiven Stationen in seiner lokalen WSPR-Nachbarschaft vergleichen.

WSPRadar geht &uuml;ber eine Spot-Karte oder eine Stationsbewertung hinaus. Seine besondere St&auml;rke entsteht durch die Kombination mehrerer Funktionen in einem Arbeitsablauf f&uuml;r Funkamateure:

* **TX- und RX-Analyse:** Untersuchen, wo das eigene Sendesignal decodiert wird und welche unabh&auml;ngig best&auml;tigten Signale der eigene Empf&auml;nger decodiert.
* **Gezielte Experimentdesigns:** Hardware A/B, Referenzstation/Buddy-Test, lokaler Nachbarschafts-Benchmark oder Success ohne Benchmark ausw&auml;hlen.
* **Vergleichbare Evidenz:** Target- und Referenzbeobachtungen im selben WSPR-Zyklus paaren oder bei sequenziellem TX A/B kontrollierte Zeit-Bins verwenden.
* **Zwei Leistungsansichten:** Gepaarte Signalst&auml;rkedifferenz von Decode/No-Decode-Ergebnissen trennen, statt beides in eine einzige Kennzahl zu zwingen.
* **Stations and Spots:** Sowohl die geografische Breite der beteiligten Stationsidentit&auml;ten als auch das Volumen qualifizierender Beobachtungen sehen.
* **Pr&uuml;fbare Evidenz:** Von der Karte zum Segment, zur Station und zu den Zeilen hinter dem Ergebnis wechseln und anschlie&szlig;end das aktuelle Analysepaket exportieren.

Diese Kombination macht aus "Ich hatte mehr Spots" eine belastbarere und n&uuml;tzlichere Aussage dar&uuml;ber, **was passiert ist, wo es passiert ist, gegen welche Referenz verglichen wurde und unter welchen Bedingungen**.

WSPRadar bleibt ein Beobachtungswerkzeug f&uuml;r den realen Funkbetrieb. Es ist weder ein kalibriertes Antennenmessgel&auml;nde noch ein Empf&auml;ngermessplatz und isoliert Antennengewinn, Wirkungsgrad oder Empf&auml;ngerempfindlichkeit nicht vom &uuml;brigen Stationssystem. Sein Wert liegt woanders: WSPR-basierte Stationsexperimente werden wesentlich kontrollierter, transparenter und reproduzierbarer.

<a id="sec-1-1"></a>
#### 1.1 WSPR in zwei Minuten

**WSPR** steht f&uuml;r **Weak Signal Propagation Reporter**. Es ist ein schmalbandiges digitales Protokoll, mit dem Funkamateure Ausbreitungswege durch Sendungen mit geringer Leistung untersuchen. Eine normale WSPR-2-Sendung dauert etwa 110,6 Sekunden, beginnt zwei Sekunden nach einer geraden UTC-Minute und belegt ungef&auml;hr 6 Hz. Die Nachricht enth&auml;lt normalerweise ein Rufzeichen, einen vierstelligen Maidenhead-Locator und die gemeldete Sendeleistung in dBm. Abh&auml;ngig von Decoder und Bedingungen wird Empfang h&auml;ufig mit etwa `-27 bis -31 dB` SNR auf der WSJT-Skala mit 2500 Hz Referenzbandbreite angegeben. <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a>

Eine Empfangsstation decodiert m&ouml;glichst viele WSPR-Signale und l&auml;dt bei aktivierter Meldung jeden erfolgreichen Decode als **Spot** hoch. Ein Spot enth&auml;lt Sender- und Empf&auml;ngeridentit&auml;t, gemeldete Locator, Zeit, Band, gemeldete Leistung und das vom Decoder gemeldete Signal-Rausch-Verh&auml;ltnis (SNR). WSPRadar liest den historischen Spot-Bestand &uuml;ber wspr.live. <a href="#ref-3">[Ref-3]</a>

Eine Einschr&auml;nkung ist sofort wichtig: Die Datenbank enth&auml;lt erfolgreiche Decodes, nicht jeden Sendeversuch und jeden fehlgeschlagenen Empfang. Ein fehlender Spot kann keine Sendung, keinen Decode, keinen Upload, eine falsche Identit&auml;t, einen nicht verf&uuml;gbaren Dienst oder einen geschlossenen Pfad bedeuten. WSPRadar verwendet deshalb ausdr&uuml;ckliche Aktivit&auml;ts- und Vergleichsregeln; es setzt nie jeden fehlenden Spot mit einem Funkfehler gleich.

<a id="sec-1-2"></a>
#### 1.2 Was du &uuml;ber deine Station lernen kannst

WSPRadar ist um praktische Amateurfunkfragen aufgebaut:

* Wo wird mein Sender decodiert, und von welchen aktiven Empf&auml;ngern?
* Welche anderswo best&auml;tigten Signale decodiert auch mein Empf&auml;nger?
* Hat Antenne oder Empfangspfad A besser abgeschnitten als B?
* Wie vergleicht sich meine Station mit einem bekannten Buddy auf demselben Band?
* Bin ich ungef&auml;hr typisch f&uuml;r aktive WSPR-Stationen in der N&auml;he meines QTH?
* Kann ich mit der st&auml;rksten aktiven lokalen Station mithalten?
* Konzentriert sich ein Vorteil auf bestimmte Richtungen, Entfernungen oder Zeiten?
* Bin ich ein "Alligator": werde gut geh&ouml;rt, h&ouml;re aber schlecht?

Die letzte Frage erfordert vergleichbare TX- und RX-L&auml;ufe gegen dasselbe Benchmark-Konzept. Auch dann ist die Differenz als Evidenz f&uuml;r das gesamte Stationssystem zu lesen: TX und RX verwenden unterschiedliche Peer-Populationen und Opportunity-Regeln.

<a id="sec-1-3"></a>
#### 1.3 Was ein WSPRadar-Lauf erzeugt

Vor der Analyse werden gew&auml;hlt:

* **Richtung:** TX, wenn das Target sendet; RX, wenn das Target empf&auml;ngt.
* **Benchmark-Design:** kein Benchmark, lokales Hardware A/B, eine Referenzstation oder eine lokale Nachbarschaft.

Diese Auswahl bestimmt die Ergebnisbl&ouml;cke:

* **Success** ist das Betriebsergebnis nur f&uuml;r das Target. Es meldet eine bedingte Success Rate gegen qualifizierende Aktivit&auml;t im WSPR-Netz. Es ist keine Benchmark-Punktzahl.
* **Compare** kommt hinzu, wenn ein Benchmark gew&auml;hlt wurde. Es zeigt die gepaarte SNR-Differenz zwischen Target und Reference zusammen mit **Decode Outcomes** f&uuml;r gemeinsame und einseitige Evidenz.

Das Vergleichsobjekt des Targets hei&szlig;t **Reference**. Je nach Design ist das Setup B, ein Buddy-Rufzeichen, ein zyklusbezogener lokaler Median oder der st&auml;rkste aktive lokale Peer.

Ein **Peer** ist eine entfernte Stationsidentit&auml;t, die Evidenz liefert. WSPRadar behandelt jedes exakte Paar `Rufzeichen + gemeldeter Locator` als eigene Peer-Identit&auml;t.

Zuerst erscheint eine geografische Karte. Danach untersucht der Segment Inspector einen gew&auml;hlten Entfernungs-/Richtungsbereich, Station Insights listet die beitragenden Identit&auml;ten auf, und Drill-Down zeigt die zugrunde liegenden Beobachtungen, Paare oder Zeit-Bins.

<a id="documentation-toc"></a>
### Inhaltsverzeichnis

* [1. Warum WSPRadar](#sec-1)
* [2. F&uuml;nf-Minuten-Schnellstart](#sec-2)
* [3. Analyse ausw&auml;hlen und planen](#sec-3)
  * [3.1 TX oder RX ausw&auml;hlen](#sec-3-1)
  * [3.2 Kein Benchmark: nur Success](#sec-3-2)
  * [3.3 Hardware A/B](#sec-3-3)
  * [3.4 Referenzstation / Buddy-Test](#sec-3-4)
  * [3.5 Lokaler Nachbarschafts-Benchmark](#sec-3-5)
  * [3.6 Checkliste vor dem Lauf](#sec-3-6)
* [4. Ergebnisse lesen](#sec-4)
* [5. Bedienelemente und Konfiguration](#sec-5)
* [6. Fehlersuche und Datenqualit&auml;t](#sec-6)
* [7. Wissenschaftliche Methodik](#sec-7)
* [8. Grenzen, zul&auml;ssige Aussagen und Reproduzierbarkeit](#sec-8)
* [Anhang A: Parallele WSJT-X-Instanzen](#sec-a)
* [Anhang B: Zeitgesteuerte A/B-Relaisumschaltung](#sec-b)
* [Anhang C: Referenz-SNR-Kalibrierung](#sec-c)
* [Anhang D: Literatur, Stand der Technik und Einordnung](#sec-d)
* [Quellen](#sec-ref)

<a id="sec-2"></a>
### 2. F&uuml;nf-Minuten-Schnellstart

Der sicherste erste Lauf verwendet eine gepflegte historische Demo. So lernst du die Oberfl&auml;che kennen, bevor du ein eigenes Experiment planst.

1. `Demo laden` anklicken.
2. Eine Demo ausw&auml;hlen, deren Titel zu einer gew&uuml;nschten Frage passt.
3. `Ausgewaehlte Demo starten` anklicken.
4. Die Ergebnistitel pr&uuml;fen. Eine Benchmark-Demo erzeugt normalerweise ein **Compare**-Ergebnis und ein separates **Success**-Ergebnis.
5. Die Karte zun&auml;chst im &Uuml;berblick lesen:
   * Die Kartenfarbe zeigt das Segmentergebnis.
   * `STATIONS` zeigt die Verteilung der beteiligten Stationsidentit&auml;ten.
   * `SPOTS` zeigt die Verteilung des qualifizierenden Beobachtungsvolumens.
6. Den `Segment Inspector` &ouml;ffnen und Entfernungsbereich sowie Richtung ausw&auml;hlen.
7. Die Segmentzusammenfassung lesen. Bei Compare meldet sie sachliche Z&auml;hlwerte wie `Selected Segment Evidence: 4 joint stations | 17 joint spots`.
8. Eine Zeile in Station Insights ausw&auml;hlen und die ausgew&auml;hlte Stations-Evidenz sowie die Drill-Down-Zeilen pr&uuml;fen.
9. `Alle Ergebnisse zum Download vorbereiten` verwenden, wenn aktuelle Konfiguration, Metadaten, verarbeitete Evidenz, Tabellen und hochaufl&ouml;sende Abbildungen ben&ouml;tigt werden.

Nicht allein aus der Kartenfarbe schlie&szlig;en, dass eine Antenne "gewonnen" hat. Zuerst Ergebnistyp, Stationsanzahl, Spot-/Bin-Anzahl, Decode Outcomes, Zeitfenster und gew&auml;hlten geografischen Bereich best&auml;tigen.

**Eine vertretbare erste Compare-Aussage**

> F&uuml;r dieses Target, diesen Benchmark, dieses Band, dieses UTC-Fenster und dieses Segment sprach die gepaarte SNR-Differenz der Stationsmediane um den angezeigten Betrag f&uuml;r Target/Reference. Die Anzahl gemeinsamer Stationen und Spots beschreibt die Menge gepaarter Evidenz; Decode Outcomes zeigt die einseitige Evidenz au&szlig;erhalb dieser Teilmenge.

**Eine vertretbare erste Success-Aussage**

> F&uuml;r dieses Target, dieses Band, dieses UTC-Fenster und die gew&auml;hlte Peer-Population beschreibt die angezeigte Success Rate den Anteil unabh&auml;ngig best&auml;tigter Opportunities, in denen auch das Target qualifizierende Evidenz erzeugte. Sie ist ein bedingter Netzindikator, keine unbedingte Decode-Wahrscheinlichkeit und keine Punktzahl, die 100 Prozent erreichen sollte.

Vor einem Lauf mit dem eigenen Rufzeichen das Experiment in [Abschnitt 3](#sec-3) ausw&auml;hlen. Eine korrekte Folge von Mausklicks kann ein unkontrolliertes Experiment nicht reparieren.

<a id="sec-3"></a>
### 3. Analyse ausw&auml;hlen und planen

Dieses Kapitel ist die zentrale Stelle f&uuml;r Analyseauswahl und Experimentdesign. Gemeinsame Berechnungen werden sp&auml;ter unter [Wissenschaftliche Methodik](#sec-7) definiert.

| Deine Frage | Benchmark-Design | Wesentliche Voraussetzung |
|---|---|---|
| Wo werde ich geh&ouml;rt, oder welche best&auml;tigten Signale h&ouml;re ich? | `Kein Benchmark (nur Success)` | Korrekte Target-Identit&auml;t, Band und aktives Zeitfenster. |
| Unterscheidet sich lokales Setup A von Setup B? | `Hardware A/B-Test (Eigenes Setup)` | Jede nicht getestete Variable stabil halten. |
| Wie vergleiche ich mich mit einer bekannten Station? | `Fremdes Rufzeichen (Buddy-Test)` | &Uuml;berlappender Betrieb und gen&uuml;gend gemeinsame entfernte Peers. |
| Bin ich typisch f&uuml;r aktive WSPR-Stationen in der N&auml;he? | `Lokaler Nachbarschafts-Benchmark` mit lokalem Median | Sinnvoller Radius und gen&uuml;gend aktive lokale Stationen. |
| Kann ich mit dem st&auml;rksten aktiven lokalen Peer mithalten? | `Lokaler Nachbarschafts-Benchmark` mit lokaler Beststation | Die Reference als wechselnde Best-Peer-H&uuml;llkurve interpretieren. |

<a id="sec-3-1"></a>
#### 3.1 TX oder RX ausw&auml;hlen

**TX** ausw&auml;hlen, wenn das Target-Rufzeichen die sendende Station oder der Sendepfad von Setup A ist. Entfernte Empfangsstationen werden zu den dargestellten Peers.

**RX** ausw&auml;hlen, wenn das Target-Rufzeichen die Empfangsstation oder Empfangskette von Setup A ist. Entfernte Sendestationen werden zu den dargestellten Peers.

Jeder Lauf ben&ouml;tigt genau ein Band. Eine Kombination mehrerer B&auml;nder w&uuml;rde unterschiedliche Ausbreitung, Stationspopulationen, Aktivit&auml;t und Beobachtbarkeit in einem Ergebnis vermischen.

<a id="sec-3-2"></a>
#### 3.2 Kein Benchmark: nur Success

**Verwenden, wenn:** du die TX- oder RX-Reichweite des Targets verstehen m&ouml;chtest, ohne sie mit einer anderen Station oder Konfiguration zu vergleichen.

**Einrichtung:** Exaktes Target-Rufzeichen, QTH, ein Band und ein Zeitfenster eingeben, in dem das Target in Betrieb war. `Kein Benchmark (nur Success)` ausw&auml;hlen und danach TX oder RX starten.

**Ergebnis:** Ein TX-Success- oder RX-Success-Ergebnis. Reine Vergleichseingaben verschwinden, und es wird keine Compare-Abfrage erstellt.

**Bedeutung:** Success ist ein bedingter, ausbreitungsgewichteter Indikator f&uuml;r die Netzreichweite, der aus qualifizierender globaler WSPR-Aktivit&auml;t gebildet wird. Er ist keine Target-gegen-Reference-Punktzahl. [Abschnitt 4.2](#sec-4-2) erkl&auml;rt die Interpretation des Prozentwerts.

**Beachten:** Hardware nicht anhand des Prozentwerts allein bewerten. Geografischen Bereich, Evidenzz&auml;hler und Konsistenz &uuml;ber die Zeit pr&uuml;fen.

<a id="sec-3-3"></a>
#### 3.3 Hardware A/B

**Verwenden, wenn:** zwei lokale Antennen, Speiseleitungen, Empfangspfade oder andere Stationskonfigurationen getestet werden sollen.

**Einrichtung f&uuml;r simultanes RX:** Zwei Empf&auml;nger gleichzeitig mit unterschiedlichen exakten Melderufzeichen betreiben. Setup A verwendet das Target-Rufzeichen, Setup B das Setup-B-Rufzeichen. Die aktuelle Oberfl&auml;che verwendet bei RX A/B keine getrennten Target-/Reference-Locatorfelder. Uhren, Antennenumschaltung, Verst&auml;rkung, Audiopfade, Decoder-Einstellungen und Uploads kontrollieren.

**Einrichtung f&uuml;r sequenzielles TX:** Ein Rufzeichen verwenden und vollst&auml;ndige WSPR-Sendungen zwischen zwei Pfaden abwechseln:

* Target-Frames: UTC-Startminuten `00, 04, 08, ...`
* Reference-Frames: UTC-Startminuten `02, 06, 10, ...`

WSPRadar gruppiert diese Sendungen in feste Bins von 4, 8, 12, 16 oder 20 Minuten. Ein deterministischer Scheduler oder Controller ist erforderlich; das normale zuf&auml;llige Verhalten des Sendeprozentsatzes ist kein fester A/B-Zeitplan.

F&uuml;r beide Pfade das normale exakte Stationsrufzeichen verwenden. Keine k&uuml;nstlichen Suffixe `/1` und `/2` f&uuml;r Setup A und Setup B erfinden: Die konfigurierte Frame-Folge identifiziert beide Seiten. Zusammengesetzte WSPR-Rufzeichen verwenden andere Nachrichtenformate; je nach Format fehlt der Locator oder das Rufzeichen wird durch einen Hash dargestellt. Dadurch k&ouml;nnen Identit&auml;ts- und Locator-Evidenz zwischen Decodern und Uploads weniger direkt vergleichbar werden. Ein Suffix kann au&szlig;erdem regulatorische Bedeutung haben und sollte nur verwendet werden, wenn es f&uuml;r den tats&auml;chlichen Betrieb zul&auml;ssig ist. <a href="#ref-2">[Ref-2]</a>

**Warum TX A/B sequenziell ist:** Wenn zwei nahe Antennen am selben QTH im selben Zyklus und Frequenzkanal dieselbe WSPR-Wellenform mit demselben Rufzeichen abstrahlen, beobachtet ein entfernter Empf&auml;nger ihr kombiniertes Feld. Sein Spot kann nicht Antenne A oder B zugeordnet werden. Unterscheidbare simultane Signale erfordern normalerweise getrennte Rufzeichen und Sendeketten. Damit kommen Unterschiede bei Senderkalibrierung, Leistung, Timing und Frequenz hinzu; nahe Antennen und Speisesysteme k&ouml;nnen sich zudem gegenseitig koppeln oder HF in die andere Kette einspeisen. Simultanes lokales TX ist daher nicht physikalisch unm&ouml;glich, aber normalerweise das falsche Design f&uuml;r den von WSPRadar beabsichtigten kontrollierten Vergleich eines einzelnen Senders mit umgeschaltetem HF-Pfad.

Der Wechsel vollst&auml;ndiger benachbarter WSPR-Frames h&auml;lt die Beobachtungen von Setup A und B nur zwei Minuten auseinander. Bei einem ausgeglichenen Zeitplan &uuml;ber viele Stunden oder Tage sollten kurzzeitige &Auml;nderungen von Ausbreitung und Empf&auml;nger beide Seiten wiederholt treffen und sich tendenziell ausmitteln, sodass der praktische Nachteil von sequenziellem gegen&uuml;ber simultanem TX klein werden sollte. Er ist nicht exakt null: Systematische Frame-Timing- oder Schalteffekte k&ouml;nnen verbleiben; ein Tausch der Frame-Zuordnung ist eine n&uuml;tzliche Kontrolle.

**Ergebnis:** Ein Hardware-Compare-Ergebnis plus separates Success-Ergebnis des Targets. Bei sequenziellem TX ist Success auf die konfigurierte Target-Frame-Folge begrenzt und beschreibt nur Setup A.

**Bedeutung:** Simultanes RX kommt bei WSPRadar einem kontrollierten Hardwarevergleich desselben Signals am n&auml;chsten. Sequenzielles TX reduziert viele Hardwareunterschiede, wenn ein Sender nur den HF-Pfad umschaltet; beide Seiten werden jedoch zu verschiedenen Zeiten beobachtet.

**Beachten:** Gemeinsame Hardware, Splitter-Ungleichgewicht, Schaltverlust, ungleiche Speiseleitungen, AGC-Verhalten, Clipping, Uhrenfehler, falsche Frame-Polarit&auml;t und jede Konfigurations&auml;nderung au&szlig;erhalb der getesteten Variable.

**Zugeh&ouml;rige Anh&auml;nge:** [Anhang A](#sec-a) f&uuml;r parallele WSJT-X-Instanzen, [Anhang B](#sec-b) f&uuml;r das zeitgesteuerte USB-Relaiswerkzeug von WSPRadar und [Anhang C](#sec-c) f&uuml;r die Reference-SNR-Kalibrierung verwenden.

<a id="sec-3-4"></a>
#### 3.4 Referenzstation / Buddy-Test

**Verwenden, wenn:** das Target mit einer bekannten externen Station verglichen werden soll.

**Einrichtung:** Ein exaktes Target-Rufzeichen und ein davon verschiedenes exaktes Reference-Rufzeichen eingeben. Eine Station w&auml;hlen, deren Standort, Hardware, Leistung und Betriebsplan bekannt sind. Beide Seiten m&uuml;ssen sich im Betrieb auf demselben Band &uuml;berlappen.

**Ergebnis:** Ein TX- oder RX-Compare-Ergebnis gegen den Buddy plus separates Target-Success-Ergebnis.

**Bedeutung:** Bei TX vergleicht derselbe entfernte Empf&auml;nger Target und Reference, wenn beide im selben Zyklus beobachtet wurden. Bei RX vergleichen Target- und Reference-Empf&auml;nger dieselbe entfernte Senderidentit&auml;t im selben Zyklus. Diese Paarung reduziert gemeinsames Fading und Unterschiede am gemeinsamen Endpunkt, macht zwei Stationen aber nicht physikalisch identisch.

**Beachten:** Unterschiedliches Gel&auml;nde, lokales Rauschen, Antennen, Polarisation, Speiseleitungsverlust, Sender- oder Empf&auml;ngerkalibrierung, gemeldete Leistung und Betriebsplan. Das Target-Active Gate ist asymmetrisch; ein Tausch von Target und Reference kann einseitige Decode Outcomes ver&auml;ndern, obwohl sich gemeinsame gepaarte Differenzen im Vorzeichen umkehren.

<a id="sec-3-5"></a>
#### 3.5 Lokaler Nachbarschafts-Benchmark

**Verwenden, wenn:** statt einer handverlesenen Referenz der Kontext aktiver WSPR-Stationen rund um das konfigurierte QTH gew&uuml;nscht ist.

**Einrichtung:** Einen Radius von 10 bis 250 km und eine von zwei Methoden w&auml;hlen:

* **Lokaler Nachbarschafts-Median:** Empfohlener Ausgangspunkt f&uuml;r die Frage "Bin ich f&uuml;r meine Region ungef&auml;hr typisch?"
* **Beste lokale Station:** Strengerer Test gegen die st&auml;rkste aktive lokale Referenz f&uuml;r jeden Zyklus und Pfad.

**Ergebnis:** Ein lokales Compare-Ergebnis plus separates Target-Success-Ergebnis.

**Bedeutung:** Beim lokalen Median erh&auml;lt jede aktive lokale Identit&auml;t `Rufzeichen + Locator` genau einen Referenzbeitrag pro Zyklus/Pfad, bevor der Nachbarschaftsmedian gebildet wird. Eine sehr aktive lokale Station erh&auml;lt dadurch nicht f&uuml;r jede doppelte oder wiederholte Zeile eine Stimme. Fehlt einer lokalen Station eine qualifizierende Beobachtung f&uuml;r diesen Zyklus/Pfad, erfindet WSPRadar keine `0 dB`; die Station tr&auml;gt einfach nichts zu diesem Referenzpool bei. Das Target wird nur anhand des exakten Rufzeichens aus dem lokalen Pool ausgeschlossen, sodass Basisrufzeichen und suffigierte Identit&auml;t getrennt bleiben. Local Best verwendet dagegen eine wechselnde Best-Peer-H&uuml;llkurve und ist kein lokaler Durchschnitt.

**Beachten:** Der Referenzpool &auml;ndert sich, wenn Stationen aktiv oder inaktiv werden. Lokale Stationen sind nicht kalibriert und k&ouml;nnen sich bei Antenne, Gel&auml;nde, Rauschen, Hardware und Genauigkeit der gemeldeten Leistung unterscheiden. Ein zu gro&szlig;er Radius repr&auml;sentiert m&ouml;glicherweise keine gemeinsame lokale Umgebung mehr.

<a id="sec-3-6"></a>
#### 3.6 Checkliste vor dem Lauf

**Vor der Datenerfassung**

* Frage und getestete Variable in einem Satz festhalten.
* TX oder RX, genau ein Band und das Benchmark-Design ausw&auml;hlen.
* Exakte Rufzeichenformen einschlie&szlig;lich Suffixen wie `/P`, `/1` oder `/QRP` pr&uuml;fen.
* Target-QTH pr&uuml;fen. Success gleicht das Target-Rufzeichen gemeinsam mit den ersten vier Locatorzeichen ab.
* Ein UTC-Fenster w&auml;hlen, das lang genug f&uuml;r die von der Aussage abgedeckten Ausbreitungszust&auml;nde ist. F&uuml;r Aussagen &uuml;ber vollst&auml;ndige Tageszyklen sind mehrt&auml;gige L&auml;ufe vorzuziehen.
* Antennen, Speiseleitungen, Tuner, Sender oder Empf&auml;nger, Decoder, Softwareversion, Leistung, Zeitplan und beabsichtigte &Auml;nderungen dokumentieren.

**W&auml;hrend des Experiments**

* Jede nicht getestete Variable so stabil wie praktisch m&ouml;glich halten.
* Uhren synchron halten.
* Bei TX tats&auml;chliche und gemeldete Leistung realistisch und stabil halten, sofern nicht die Leistung getestet wird.
* Bei RX Verst&auml;rkung, Filterung, Audiopfad, Decoder-Einstellungen und Upload-Verhalten stabil halten, sofern sie nicht getestet werden.
* Den beabsichtigten Betrieb beider Benchmark-Seiten best&auml;tigen. Das Target-Active Gate weist keine Reference-Uptime nach.

**Vor der Annahme des Ergebnisses**

* Titel, Target, Reference, Band, UTC-Fenster und Filter best&auml;tigen.
* Sowohl `STATIONS` als auch `SPOTS` pr&uuml;fen, nicht nur die Kartenfarbe.
* Anzahl gemeinsamer Stationen und Spots/Bins im gew&auml;hlten Segment pr&uuml;fen.
* Decode Outcomes zusammen mit der gepaarten SNR-Differenz betrachten.
* Nach einer dominierenden Identit&auml;t, einem Locator oder einem kurzen Zeitintervall suchen.
* Experiment wiederholen oder Pfade tauschen, wenn eine kleine Differenz eine wichtige Entscheidung st&uuml;tzen soll.
* Exportpaket vorbereiten und externe Aufbauhinweise aufbewahren, die WSPRadar nicht ableiten kann.

<a id="sec-4"></a>
### 4. Ergebnisse lesen

Dieses Kapitel ist die zentrale Stelle f&uuml;r die Interpretation der Oberfl&auml;che. Exakte Formeln und Verarbeitungshierarchie stehen unter [Wissenschaftliche Methodik](#sec-7).

<a id="sec-4-1"></a>
#### 4.1 Ergebnisblock identifizieren

Mit dem Titel beginnen:

* **TX Success / RX Success:** Bedingte Target-Reichweite gegen qualifizierende Netzaktivit&auml;t.
* **TX Compare / RX Compare:** Target-gegen-Reference-Evidenz anhand gepaarter SNR-Differenz und Decode Outcomes.
* **Sequential TX A/B Compare:** Spezielles Compare-Ergebnis, dessen gepaarte Einheit ein festes Zeit-Bin statt eines WSPR-Zyklus ist.

Farben unterschiedlicher Ergebnistypen nicht miteinander vergleichen. Zus&auml;tzlich Band, Zeitfenster, Benchmark-Design, Rufzeichen, Filter und Evidenzschwellen best&auml;tigen.

<a id="sec-4-2"></a>
#### 4.2 Success Rate verstehen

Success Rate beantwortet eine praktische, aber bewusst begrenzte Frage:

* **RX Success:** Wie viele der Peer-Senderzyklen, die unabh&auml;ngig von einem anderen Empf&auml;nger best&auml;tigt wurden, decodierte auch der Target-Empf&auml;nger?
* **TX Success:** Wie viele der aktiven Peer-Empf&auml;ngerzyklen, die durch andere Decodes auf demselben Band best&auml;tigt wurden, decodierten auch den Target-Sender?

WSPRadar verwendet vier sichtbare Klassifikationen:

* **Target:** Das Target war erfolgreich, und eine unabh&auml;ngige Best&auml;tigung existiert ebenfalls.
* **Elsewhere:** Bei RX wurde der Sender von einem anderen Empf&auml;nger, aber nicht vom Target geh&ouml;rt.
* **Other Signals:** Bei TX h&ouml;rte der Empf&auml;nger andere Signale auf demselben Band, aber nicht das Target.
* **Target-only:** Das Target war ohne die f&uuml;r den Nenner erforderliche unabh&auml;ngige Best&auml;tigung erfolgreich. Diese Evidenz bleibt f&uuml;r Audits erhalten, geht aber nicht in Success Rate ein.

Beispiel: Wurde ein entfernter Sender in acht qualifizierenden Zyklen anderswo best&auml;tigt und vom eigenen Empf&auml;nger in drei davon geh&ouml;rt, betr&auml;gt seine RX Success Rate `3 von 8 = 37,5%`. Erzeugte ein aktiver Empf&auml;nger zehn qualifizierende Zyklen und h&ouml;rte den eigenen Sender in vier, betr&auml;gt seine TX Success Rate `4 von 10 = 40%`.

**Success Rate ist keine Punktzahl von 100.** Die Kandidatenpopulation stammt aus dem globalen Netz:

* Bei RX kann sie sich den weltweit aktiven Sendern auf diesem Band in Zyklen ann&auml;hern, in denen der Target-Empf&auml;nger aktiv war.
* Bei TX kann sie sich den weltweit aktiven Empf&auml;ngern auf diesem Band w&auml;hrend der Target-Sendezyklen ann&auml;hern.

Nur Peers, die Zeit, Band, Filter und Evidenzschwellen &uuml;berstehen, tragen bei; der angezeigte Kartenbereich kann au&szlig;erdem nur eine geografische Teilmenge zeigen. Trotzdem bleiben viele Pfade schwierig oder nicht verf&uuml;gbar. Ein niedrigerer Prozentwert bedeutet nicht automatisch schlechte Hardware.

Angezeigte `100%` bedeuten, dass das Target in jeder qualifizierenden Opportunity dieser Station oder dieses gew&auml;hlten Bereichs erfolgreich war. Sie bedeuten nicht, dass jede m&ouml;gliche oder geplante Sendung decodiert wurde.

Zuerst wird die Rate jedes Peers berechnet. Ein Success-Kartensegment gewichtet danach jede qualifizierende Peer-Identit&auml;t gleich und zeigt das arithmetische Mittel dieser Stationsraten. Segment Insight zeigt zus&auml;tzlich die gepoolte Rate auf Beobachtungsebene, bei der jede qualifizierende Beobachtung gleich gewichtet wird.

Die Success-Rate-Klassifikation selbst ist nicht leistungsnormalisiert. Das daneben angezeigte erfolgreiche Target-SNR ist auf gemeldete 1 W normalisiert.

<a id="sec-4-3"></a>
#### 4.3 Compare verstehen

Compare trennt zwei Fragen, die eine einzige Kennzahl nicht gut beantworten kann.

Die **gepaarte SNR-Differenz** fragt: Wenn Target und Reference beide vergleichbare Evidenz erzeugten, welche Seite hatte das st&auml;rkere SNR und um wie viel? Die Oberfl&auml;che nennt diese Differenz **Delta SNR**. Positive Werte sprechen f&uuml;r das Target, negative f&uuml;r die Reference. Die Formel erscheint einmal in [Abschnitt 7.5](#sec-7-5).

**Decode Outcomes** fragt: Was geschah au&szlig;erhalb dieser gepaarten Teilmenge?

* **Joint / Joint Spots / Joint Bins:** Qualifizierende gepaarte Evidenz ist vorhanden.
* **Only Target:** Target-Evidenz ohne Reference-Evidenz in der betreffenden Vergleichseinheit.
* **Only Reference:** Reference-Evidenz ohne Target-Evidenz.
* **Both (Async):** Beide Seiten haben Evidenz f&uuml;r die Peer-Identit&auml;t, aber f&uuml;r diese Kategorie bleibt keine qualifizierende gemeinsame Einheit &uuml;brig.

Gepaartes Delta SNR ist normalerweise der prim&auml;re quantitative Vergleich, weil beide Seiten unter besser vergleichbaren Bedingungen beobachtet werden. Decode Outcomes zeigt, ob eine Seite zus&auml;tzlich Signale oder Pfade au&szlig;erhalb der gepaarten Teilmenge erreichte.

Der gemeinsame Endpunkt h&auml;ngt von der Richtung ab. Bei simultanem TX Compare misst derselbe entfernte Empf&auml;nger Target und Reference; dadurch werden Unterschiede bei Empf&auml;ngerhardware, Empfangsantenne, lokalem Rauschen und Meldung innerhalb des Paars reduziert. Bei simultanem RX Compare messen Target- und Reference-Empf&auml;nger denselben entfernten Sender; dadurch werden Unterschiede bei Sendeleistung, Wellenform und gemeinsamem Ausbreitungspfad reduziert. Paarung im selben Zyklus reduziert diese St&ouml;rvariablen, macht getrennte Stationen oder Hardwareketten aber nicht physikalisch identisch.

Bei simultanen Vergleichen verhindert das Target-Active Gate, dass Target-Ausfallzeit als Misserfolg gez&auml;hlt wird; eine symmetrische Reference-Uptime weist es nicht nach. Sequenzielles TX A/B verwendet stattdessen geplante Frames und gepaarte Zeit-Bins.

<a id="sec-4-4"></a>
#### 4.4 Karte lesen

**Median und arithmetisches Mittel**

Ein **Median** ist der mittlere Wert sortierter Werte oder bei gerader Anzahl der Mittelpunkt der beiden zentralen Werte. Anders als das arithmetische Mittel wird er von einem einzelnen ungew&ouml;hnlich hohen oder niedrigen Wert weniger stark verschoben. WSPRadar verwendet Mediane f&uuml;r gepaarte SNR-Differenzen und lokale Referenzwerte, bei denen Robustheit wichtig ist; Success-Kartensegmente verwenden das arithmetische Mittel, nachdem jeder qualifizierende Peer eine gleich gro&szlig;e Stimme erhalten hat. Beide Zusammenfassungen beantworten unterschiedliche Fragen und sind nicht austauschbar.

**Heatmap-Farbe**

* Compare-Segmente zeigen den Median qualifizierender Delta-SNR-Stationsmediane. Positiv spricht f&uuml;r Target, negativ f&uuml;r Reference. Die Vergleichsskala nutzt die Amateurfunk-Anzeigekonvention `1 S-Stufe = 6 dB`; das ist eine Skalenbeschriftung und keine Behauptung, jedes S-Meter sei kalibriert.
* Success-Segmente zeigen das arithmetische Mittel qualifizierender Success Rates der Stationen. Die feste nichtlineare Skala unterscheidet keine Evidenz, exakt `0%`, einen positiven Wert unter `1%` und danach `1, 2, 5, 10, 20, 40, 60, 80, 100%`.

**STATIONS und SPOTS**

Jede aktuelle WSPRadar-Karte verwendet zwei Fu&szlig;zeilen:

* `STATIONS` beschreibt die geografische Breite &uuml;ber unterschiedliche qualifizierende Identit&auml;ten `Rufzeichen + Locator`.
* `SPOTS` beschreibt das Volumen qualifizierender Beobachtungen.

Bei Compare werden beide Zeilen in Only Target, Joint, Both (Async) und Only Reference aufgeteilt. Stationskategorien ordnen jede Identit&auml;t einer Hauptkategorie zu. Spot-Kategorien z&auml;hlen das Evidenzvolumen einschlie&szlig;lich exklusiver Beobachtungen von Identit&auml;ten, die auch gemeinsame Evidenz besitzen.

Bei Success teilt `SPOTS` die qualifizierende Nennerevidenz bei RX in Target und Elsewhere und bei TX in Target und Other Signals. `STATIONS` teilt qualifizierende Identit&auml;ten in Peers mit mindestens einer Target-Beobachtung und Peers nur mit Gegen-Evidenz. Target-only und nicht qualifizierende Evidenz werden ausgeschlossen, weil sie nicht in Success Rate eingehen.

Die Fu&szlig;zeile z&auml;hlt nur Evidenz innerhalb des sichtbaren Kartenbereichs.

**Stationsmarker**

* Success: Gr&uuml;ne `T`-Marker besitzen mindestens eine best&auml;tigte Target-Beobachtung. Graue `E`- oder `OS`-Marker sind qualifizierende Zero-Target-Peers mit Elsewhere- oder Other-Signals-Evidenz.
* Compare: Gr&uuml;n ist Joint, Gelb-Orange Both (Async), Violett Only Target und Wei&szlig; Only Reference.

**Entfernungsringe**

Nahe Ringe k&ouml;nnen mit k&uuml;rzerem Skip oder NVIS-Verhalten vereinbar sein; weite Ringe mit DX-Verhalten. Entfernung ist keine direkte Messung des Abstrahlwinkels.

<a id="sec-4-5"></a>
#### 4.5 Segment Insight

Einen oder mehrere Entfernungsbereiche und Kompassrichtungen ausw&auml;hlen, um die Evidenz hinter diesem Kartenteil zu untersuchen.

**Success Segment Insight**

**Target-/Gegen-Evidenz-Zusammenfassung und Raten.** Die Z&auml;hler f&uuml;r Target und Elsewhere/Other Signals zeigen die Beobachtungen im Success-Nenner des gew&auml;hlten Segments. **Average by Station** gibt jedem qualifizierenden Peer eine gleich gro&szlig;e Stimme und ist der Kartenwert. **Observation-Level** poolt alle Beobachtungen; ein Unterschied zwischen beiden bedeutet daher, dass Peers mit hohem Volumen das gepoolte Ergebnis vom typischen Peer wegziehen. Keine Gewichtung ist allgemein richtig; sie beantworten unterschiedliche Fragen.

**Station Success Rate by Evidence Count.** Jeder Punkt ist eine Station mit Target-Evidenz. Die vertikale Position ist ihre Success Rate; die horizontale logarithmische Achse zur Basis 2 ist ihre Anzahl `Target + Gegen-Evidenz`. Punkte oben rechts verbinden eine hohe Rate mit wiederholter Evidenz, w&auml;hrend Punkte links vorsichtiger zu lesen sind, weil wenig Evidenz extreme Prozentwerte erzeugen kann. Zero-Target-Stationen fehlen, weil alle bei `0%` l&auml;gen; sie bleiben in Kartenz&auml;hlern, Zeitevidenz und bei aktiviertem `Zero-Target-Stationen zeigen` in Station Insights enthalten.

**Success &uuml;ber die Zeit.** Die stationsbalancierten und Observation-Level-Ansichten zeigen, ob Reichweite anh&auml;lt oder sich auf ein kurzes Ausbreitungsfenster konzentriert. &Auml;hnliche Ansichten sprechen daf&uuml;r, dass das Beobachtungsvolumen die Geschichte nicht ver&auml;ndert; Abweichungen weisen auf wenige sehr aktive Peers oder Intervalle hin, die die gepoolte Rate dominieren. Leere Zellen bedeuten keine qualifizierende Evidenz und nicht gemessene `0%`.

**Compare Segment Insight**

**Decode Outcomes.** Die Kategorienansicht zeigt die Breite von Joint-, Only-Target-, Both-(Async)- und Only-Reference-Stationen im gew&auml;hlten Segment. Damit l&auml;sst sich pr&uuml;fen, ob das gepaarte Delta-SNR-Ergebnis den gr&ouml;&szlig;ten Teil der geografischen Abdeckung beschreibt oder nur eine schmale gemeinsame Teilmenge. Ein starker gepaarter Median bei umfangreicher einseitiger Evidenz verlangt weiterhin beide Teile der Geschichte.

**Station Medians (Delta SNR).** Jede beitragende Station liefert genau einen Wert: ihren Median des gepaarten Delta SNR. Die Verteilung gewichtet Stationen daher gleich. Eine oberhalb oder unterhalb von null konzentrierte Verteilung weist auf einen geografisch konsistenten Vorteil von Target oder Reference hin; eine breite oder geteilte Verteilung bedeutet, dass der Effekt stark vom Pfad abh&auml;ngt und der Gesamtmedian diese Variation verdeckt.

**Delta SNR gemeinsamer Spots oder gepaarter Bins.** Diese Verteilung zeigt jedes konsolidierte Paar desselben Zyklus oder bei sequenziellem TX A/B jedes g&uuml;ltige gepaarte Bin. Sie macht rohe Streuung, Quantisierung und Ausrei&szlig;er sichtbar, aber aktive Stationen k&ouml;nnen viele Werte beitragen. Der Vergleich mit Station Medians ist wichtig: Eine gro&szlig;e Verschiebung zwischen beiden zeigt, dass Stationen mit hohem Volumen vom stationsbalancierten Bild abweichen.

**Median, Stabilit&auml;t und Evidenzz&auml;hler.** Der Median fasst Richtung und typische Gr&ouml;&szlig;e zusammen; das 90%-Stabilit&auml;tsintervall zeigt, wie stark dieser Median beim Resampling wandert, nicht statistische Signifikanz. Der sachliche Z&auml;hler beschreibt den Umfang gepaarter Evidenz, zum Beispiel:

`Selected Segment Evidence: 4 joint stations | 17 joint spots`

Sequenzielles TX A/B verwendet `paired spot bins` anstelle von `joint spots`.

Der UI-Begriff `Joint Spot` bezeichnet eine konsolidierte Vergleichseinheit desselben Zyklus und nicht zwingend eine unver&auml;nderte Datenbankzeile.

<a id="sec-4-6"></a>
#### 4.6 Station Insights und Drill-Down

`Station Insights` listet die zum ausgew&auml;hlten Bereich beitragenden Identit&auml;ten auf.

* Success-Zeilen zeigen Target, Elsewhere oder Other Signals, Success Rate und das mediane erfolgreiche Target-SNR, normalisiert auf 1 W. Qualifizierende Zero-Target-Zeilen sind standardm&auml;&szlig;ig verborgen und k&ouml;nnen mit `Zero-Target-Stationen zeigen` eingeblendet werden.
* Compare-Zeilen zeigen gemeinsame und exklusive Evidenz sowie den Delta-SNR-Stationsmedian. `Show Non-Joint` blendet Identit&auml;ten ohne qualifizierende gepaarte Evidenz wieder ein.
* Fehlendes SNR erscheint als `None`, nicht als `0.0 dB`.
* Ohne Zeilenauswahl wird standardm&auml;&szlig;ig die erste nach Evidenz sortierte Zeile gew&auml;hlt.

**Tabelle interpretieren.** Bei Success die Rate zusammen mit dem Target-/Gegen-Evidenz-Z&auml;hler lesen: Eine hohe Rate mit wenig Evidenz ist weniger &uuml;berzeugend als eine &auml;hnliche, vielfach wiederholte Rate. Das normalisierte Target-SNR beschreibt nur erfolgreiche Decodes und geht nicht in die Rate ein. Bei Compare auf &Uuml;bereinstimmung der Delta-SNR-Richtung &uuml;ber mehrere Stationen achten und gemeinsame gegen exklusive Z&auml;hler pr&uuml;fen; ein einzelner Pfad mit hohem Volumen oder ungew&ouml;hnlichem Verhalten sollte die Schlussfolgerung nicht unbemerkt bestimmen.

Die Auswahl einer oder mehrerer Zeilen &ouml;ffnet eine Ansicht der ausgew&auml;hlten Stations-Evidenz:

**Ausgew&auml;hlte Success-Evidenz.** Die Zeitansicht zeigt Success Rate gemeinsam mit Target-/Gegen-Evidenz-Z&auml;hlern, aufgeteilt nach Nacht, Greyline/gemischt und Tageslicht des Pfades. Damit l&auml;sst sich erkennen, ob ein Ergebnis &uuml;ber Beleuchtungszust&auml;nde bestehen bleibt oder aus einer kurzen &Ouml;ffnung stammt. Die Verteilung des erfolgreichen, auf 1 W normalisierten Target-SNR beschreibt die St&auml;rke decodierter Target-Evidenz; sie beschreibt weder verfehlte Opportunities noch isolierten Antennengewinn.

**Ausgew&auml;hlte Compare-Evidenz.** Die Verteilung zeigt Zentrum, Streuung und m&ouml;gliche Gruppen der ausgew&auml;hlten Delta-SNR-Evidenz. Die UTC-Zeit-Heatmap zeigt, ob diese Verteilung stabil bleibt oder sich mit der Zeit verschiebt. Sequenzielles TX A/B verwendet das Delta SNR gepaarter Bins. Medianmarker benachbarter Zeit-Bins werden nur verbunden, wenn beide Bins mindestens drei Werte enthalten; isolierte Marker zeigen daher d&uuml;nne Evidenz und nicht zwingend eine physikalische Diskontinuit&auml;t.

Verf&uuml;gbare Zeit-Bins passen sich an den Datumsbereich an: von Minuten-Bins bei kurzen L&auml;ufen bis zu 24-Stunden-Bins bei langen L&auml;ufen. Dieses Bedienelement &auml;ndert nur die ausgew&auml;hlte Evidenzansicht, nicht Kartenaggregation, Opportunity-Klassifikation oder Paarung.

`Drill-Down` ist die Audit-Ansicht auf Zeilenebene:

* Success zeigt Klassifikationen target-aktiver Peer-Zyklen einschlie&szlig;lich Target-only.
* Simultanes Compare zeigt Target-/Reference-Evidenz desselben Zyklus und Delta SNR.
* Der lokale Median erweitert die lokalen Referenzidentit&auml;ten hinter dem Zyklusmedian.
* Sequenzielles TX A/B zeigt Zeit-Bin, `Micro-Med A`, `Micro-Med B` und Bin-Delta.

**Drill-Down verwenden.** Mit diesen Zeilen lassen sich &uuml;berraschende Stations- oder Segmentwerte nachvollziehen, Locatorwechsel oder einzelne Ausrei&szlig;er finden und tats&auml;chlich gepaarte oder ausgeschlossene Beobachtungen best&auml;tigen. Drill-Down ist der Auditpfad hinter den Zusammenfassungen und keine eigene Leistungskennzahl.

<a id="sec-4-7"></a>
#### 4.7 Stabilit&auml;t und ausreichende Evidenz

`90% Stability` ist ein beschreibendes Bootstrap-Intervall um einen Median. Ein schmales Intervall bedeutet, dass sich der angezeigte Median beim Resampling der vorhandenen Werte wenig &auml;ndert. Es beweist weder Unabh&auml;ngigkeit noch die Abwesenheit von Datenbias oder statistische Signifikanz.

Die Angemessenheit der Evidenz anhand des Gesamtbilds beurteilen:

* Anzahl gemeinsamer Stationen;
* Anzahl gemeinsamer Spots oder gepaarter Bins;
* Konsistenz &uuml;ber Stationen, Zeit und benachbarte geografische Segmente;
* Decode Outcomes;
* Identit&auml;ts- und Datenqualit&auml;t;
* Experimentkontrolle und Wiederholung.

Es gibt bewusst keine automatische Beweisstufe.

<a id="sec-5"></a>
### 5. Bedienelemente und Konfiguration

Dieses Kapitel ist die zentrale Stelle f&uuml;r Standardwerte, Geltungsbereiche und Nebenwirkungen. Wissenschaftliche Formeln werden hier nicht wiederholt.

<a id="sec-5-1"></a>
#### 5.1 Ablaufsteuerung

| Bedienelement | Zweck |
|---|---|
| `Demo laden` | &Ouml;ffnet gepflegte historische Profile. Die Konfiguration kann zur Pr&uuml;fung geladen oder sofort gestartet werden. |
| `Konfig laden` | Validiert und l&auml;dt eine gespeicherte JSON-basierte `.config`-Datei. Ung&uuml;ltige Identit&auml;ten, Daten, Auswahlwerte und Bereiche werden abgelehnt. |
| `Konfig speichern` | L&auml;dt die aktuellen Eingaben herunter. Ergebnisdaten und externe Experimentnotizen sind nicht enthalten. |
| `TX Analyse starten` | Startet TX Success und bei ausgew&auml;hltem Benchmark TX Compare. |
| `RX Analyse starten` | Startet RX Success und bei ausgew&auml;hltem Benchmark RX Compare. |
| `Alle Ergebnisse zum Download vorbereiten` | Erstellt bei Bedarf das Exportpaket der aktuellen Analyse. |
| `Vollst&auml;ndige Dokumentation laden` / `Vollst&auml;ndige Dokumentation ausblenden` | Die Startseite &uuml;bertr&auml;gt zun&auml;chst nur Abschnitt 1. Wenn Abschnitt 1.3 in den sichtbaren Bereich gelangt, werden Inhaltsverzeichnis und restliches Handbuch h&ouml;chstens einmal pro Sitzung automatisch geladen, w&auml;hrend Abschnitt 1.3 gelesen wird; diese Schaltfl&auml;che &uuml;ber die volle Breite bleibt der ausdr&uuml;ckliche Ersatzweg und kann den geladenen Inhalt wieder ausblenden. Der Start einer Analyse unterdr&uuml;ckt das scrollgesteuerte Laden. |
| `PDF vorbereiten` | Erstellt bei Bedarf das vollst&auml;ndige Handbuch der gew&auml;hlten Sprache als prozessweit zwischengespeichertes PDF; das vollst&auml;ndige Web-Handbuch muss daf&uuml;r nicht ge&ouml;ffnet sein. |

<a id="sec-5-2"></a>
#### 5.2 Kernbedienelemente

| UI-Bezeichnung | Werkseinstellung | Wissenschaftliche Wirkung |
|---|---|---|
| **Dein Rufzeichen (Target under Test)** | leer | Exakte Target-Identit&auml;t. Zul&auml;ssig sind 3 bis 15 Zeichen aus `A-Z`, `0-9` und `/`. |
| **QTH Locator (4-6 Chars)** | leer | Kartenzentrum und Ursprung des lokalen Radius. Success verwendet zus&auml;tzlich die ersten vier Zeichen f&uuml;r den Abgleich der Target-Identit&auml;t. |
| **Frequenzband** | `20m` | Genau eines von `LF`, `MF`, `160m`, `80m`, `60m`, `40m`, `30m`, `22m`, `20m`, `17m`, `15m`, `12m`, `10m`, `8m`, `6m`, `4m`, `2m`, `70cm` oder `23cm`. |
| **Zeitraum-Auswahl** | `Letzte X Stunden` | Aktuelle oder benutzerdefinierte UTC-Evidenz. Der aktuelle Modus erlaubt 1 bis 168 Stunden und verwendet standardm&auml;&szlig;ig 24. |
| **Benutzerdefinierte Daten/Zeiten** | Vortag bis aktueller Tag | Benutzerdefinierte Fenster sind auf 31 Tage und Daten ab 2008 begrenzt. Endpunkte werden auf 15-Minuten-Grenzen abgerundet. |

Das Rufzeichen exakt wie hochgeladen verwenden. `DL1MKS`, `DL1MKS/P`, `DL1MKS/1` und `DL1MKS/QRP` sind getrennte Identit&auml;ten; WSPRadar verwendet keinen versteckten Pr&auml;fixabgleich.

Ein Maidenhead-Locator ist ein kompakter Standortcode aus Planquadraten. Vier Zeichen kennzeichnen ein gr&ouml;&szlig;eres Gebiet; sechs Zeichen ein kleineres Gebiet darin. WSPRadar verwendet das konfigurierte QTH als Kartenzentrum und Ursprung des lokalen Radius; Success gleicht das Target anhand der ersten vier Locatorzeichen ab.

<a id="sec-5-3"></a>
#### 5.3 Benchmark-Bedienelemente

| UI-Bezeichnung | Standard | Gilt f&uuml;r | Wirkung |
|---|---|---|---|
| **Benchmark-Design** | `Kein Benchmark (nur Success)` | Zusammenstellung des Laufs | Nur Success &uuml;berspringt Compare. Andere Auswahlwerte f&uuml;gen Compare zu Success hinzu. |
| **Referenz-SNR-Korrektur (dB)** | `0.0` | Compare | Wird vor Delta SNR zum SNR der Reference-Seite addiert. Bei nur Success verborgen. |
| **Referenz-Rufzeichen** | Beispiel `DL2XYZ` | Buddy | Durch ein exaktes, vom Target verschiedenes Rufzeichen ersetzen. |
| **Lokale Benchmark-Methode** | `Lokaler Nachbarschafts-Median` | Lokal | W&auml;hlt Nachbarschaftsmedian oder strenges Local Best. |
| **Nachbarschaftsradius (km)** | `100` | Lokal | Bezieht lokale Reference-Koordinaten in 10 bis 250 km Entfernung vom QTH ein. |
| **A/B-Test Setup** | simultanes RX | Hardware A/B | W&auml;hlt RX mit zwei Empf&auml;ngern oder zeitgeteiltes TX mit einem Sender. |
| **Setup B Callsign** | leer | RX Hardware A/B | Ein exaktes, von Setup A verschiedenes Rufzeichen. |
| **Target WSPR-Frame** | `00, 04, 08, ...` | TX Hardware A/B | Frame-Starts f&uuml;r Target / Setup A. |
| **Referenz WSPR-Frame** | `02, 06, 10, ...` | TX Hardware A/B | Frame-Starts f&uuml;r Reference / Setup B. |
| **Zeitfenster (Bins)** | `8 min` | TX Hardware A/B | Festes Paarungs-Bin von 4 bis 20 Minuten in 4-Minuten-Schritten. |

Vergleichsspezifische Werte bleiben im Sitzungszustand und in gespeicherten Konfigurationen erhalten, wenn nur Success ausgew&auml;hlt wird. Sie erscheinen bei erneuter Benchmark-Auswahl wieder, ver&auml;ndern aber weder Abfrage noch Ergebnis des reinen Success-Laufs.

**Vorzeichen der Referenz-SNR-Korrektur**

Eine positive Korrektur macht das korrigierte Reference-SNR st&auml;rker und verringert dadurch Target-minus-Reference Delta SNR. Einen gemessenen Kalibrieroffset `Target - Reference` mit demselben Vorzeichen eingeben: Ein Common-Input-Ergebnis von `+1,6 dB` wird als `+1,6 dB` eingegeben. Die exakten Gleichungen stehen in [Abschnitt 7.5](#sec-7-5).

Die Korrektur gilt f&uuml;r Setup B / den Reference-Frame bei Hardware A/B, das Buddy-Rufzeichen im Buddy-Test, den gew&auml;hlten lokalen Wert bei Local Best und jeden lokalen Beitrag vor der Local-Median-Aggregation.

Eine konstante Korrektur kann Clipping, instabile AGC, intermittierende Signalwege, frequenzabh&auml;ngigen Gang oder falsche Leistungsangaben nicht reparieren. [Anhang C](#sec-c) beschreibt die Kalibrierung.

<a id="sec-5-4"></a>
#### 5.4 Filter und Schwellen

| UI-Bezeichnung | Standard | Gilt f&uuml;r | Exakte Wirkung |
|---|---|---|---|
| **Spezielle Rufzeichen Q, 0, 1 ausschlie&szlig;en** | aus | alle Ergebnisse | Schlie&szlig;t qualifizierende Peer-Identit&auml;ten aus, die mit `Q`, `0` oder `1` beginnen. |
| **Bewegte Stationen ausschlie&szlig;en** | aus | dargestellte Peers | Entfernt ein Peer-Rufzeichen, das nach anderen Filtern mehr als einen vierstelligen Locator meldet. |
| **Lokaler QTH Sonnenstand** | `Alle 24h` | alle Ergebnisse | Beh&auml;lt am Target-QTH als Tag (`>+6 deg`), Nacht (`<-6 deg`) oder Greyline klassifizierte Zyklen. |
| **Kartenbereich (Max. Distanz km)** | `22000` | Karte/Inspektion | Legt den sichtbaren und inspizierbaren Radius fest; die Upstream-Abfrage wird nicht eingeschr&auml;nkt. |
| **Min. Joint Spots pro Station** | `1` | simultanes Compare | Erfordert so viele gemeinsame Peer-Zyklen, bevor eine Station zu gepaartem Delta SNR beitr&auml;gt. |
| **Min. Joint Bins** | `1` | sequenzielles TX A/B | Erfordert so viele gepaarte Bins, bevor eine Station zu gepaartem Delta SNR beitr&auml;gt. |
| **Min. Target+Gegen-Evidenz pro Station** | `5` | Success | Erfordert so viele Target+Elsewhere-RX- oder Target+Other-Signals-TX-Beobachtungen. |
| **Min. qualifizierte Stationen pro Karten-Segment** | `1` | alle Karten | Erfordert so viele qualifizierende Identit&auml;ten, bevor ein Segment gezeichnet wird. |

Die Compare-Joint-Schwelle unterdr&uuml;ckt auch exklusive Kategorien, deren eigener Z&auml;hler unter demselben Zahlenwert liegt. Bei sequenziellem TX A/B wird gepaarte Eignung in Bins gez&auml;hlt, exklusive Evidenz dagegen in Spots und mit demselben Zahlenwert verglichen.

Eine Verringerung von **Min. Target+Gegen-Evidenz pro Station** erh&ouml;ht die Kartenabdeckung, macht Stationsraten aber diskreter und fragiler. Bei nur einer oder zwei qualifizierenden Opportunities k&ouml;nnen Werte wie `0%`, `50%` oder `100%` sehr wenig Evidenz repr&auml;sentieren. Den Z&auml;hler neben der Rate lesen und vor Entscheidungen auf kleinen Stichproben Wiederholungen bevorzugen.

**Spezielle Rufzeichen Q, 0, 1 ausschlie&szlig;en** entsprechend der Frage verwenden und nicht automatisch aktivieren:

* Bei RX Compare k&ouml;nnen baken- oder telemetrie&auml;hnliche Sender wertvolle schwache Signale desselben Zyklus liefern, die beide Empf&auml;nger sehen.
* Bei RX Success bleiben sie enthalten, wenn Bakenempfang Teil der Frage ist; sie werden ausgeschlossen, wenn die gew&uuml;nschte Population normale Amateurstationen sind.
* Bei TX-Analysen wirkt der Filter auf empf&auml;ngerseitige Peer-Identit&auml;ten. Nur verwenden, wenn diese Identit&auml;ten die beabsichtigte Empf&auml;ngerpopulation verzerren.

Die Auswahl in seri&ouml;sen Berichten angeben.

<a id="sec-5-5"></a>
#### 5.5 Karten-, Inspector- und Exportsteuerung

* Segmentbereichs- und Richtungsauswahl &auml;ndern den inspizierten Bereich, nicht die abgeschlossene Analyse.
* `Zero-Target-Stationen zeigen` blendet qualifizierende Success-Identit&auml;ten ohne Target-Best&auml;tigung wieder ein.
* `Show Non-Joint` blendet Compare-Identit&auml;ten wieder ein, die nur durch exklusive/asynchrone Evidenz vertreten sind.
* Stationsauswahl &auml;ndert die Abbildungen der ausgew&auml;hlten Station und das ausgew&auml;hlte Drill-Down.
* Die Zeit-Bin-Auswahl der Station &auml;ndert nur ihre ausgew&auml;hlte Zeitleiste.
* Leere Success-Zeit-Bins bleiben leer und werden nicht in Evidenz mit Nullrate umgewandelt.
* `Alle Ergebnisse zum Download vorbereiten` exportiert das aktuelle Ergebnis und die Inspector-Auswahl. Der Paketinhalt steht in [Abschnitt 8.4](#sec-8-4).

<a id="sec-6"></a>
### 6. Fehlersuche und Datenqualit&auml;t

<a id="sec-6-1"></a>
#### 6.1 H&auml;ufige Symptome

| Symptom | Zuerst pr&uuml;fen |
|---|---|
| Kein Ergebnis oder keine Target-Evidenz | Exaktes Rufzeichen einschlie&szlig;lich Suffix, Target-QTH Grid-4, Band, UTC-Fenster und tats&auml;chlicher Target-Betrieb. |
| Compare hat kein Delta SNR | Gemeinsame Peer-Identit&auml;ten, &uuml;berlappende Zyklen, Joint-Schwelle, Uhren und Reference-Betrieb. |
| Success-Karte hat wenige Peers | Target+Gegen-Evidenz-Schwelle, kurzes Zeitfenster, Filter und Verf&uuml;gbarkeit unabh&auml;ngiger Best&auml;tigung. |
| Viele Target-only-Success-Zeilen | Unabh&auml;ngige Best&auml;tigung fehlt; diese Zeilen gehen nicht in Success Rate ein. |
| `Only Reference = 0` | Das kann nach Target-Active Gate, Schwellen und Bereichsauswahl korrekt sein. |
| A/B-Ergebnis hat unerwartetes Vorzeichen | Zuordnung von Setup/Pfad, Frame-Polarit&auml;t, Korrekturvorzeichen, tats&auml;chliche Leistung und Reihenfolge Target/Reference. |
| Lokales Ergebnis &auml;ndert sich mit dem Radius | Der aktive lokale Reference-Pool hat sich ge&auml;ndert; Beitr&auml;ger pr&uuml;fen. |
| Alte Konfiguration mit `band=All` wird abgelehnt | Genau ein Band w&auml;hlen; eine automatische Umwandlung w&uuml;rde die wissenschaftliche Frage ver&auml;ndern. |
| Aktuelle Spots wirken unvollst&auml;ndig | Etwa f&uuml;nf Minuten nach dem letzten Zyklus warten, danach Meldung und Upstream-Status pr&uuml;fen; siehe [Abschnitt 6.5](#sec-6-5). |

<a id="sec-6-2"></a>
#### 6.2 Rufzeichen- und Locatorprobleme

Compare-Rufzeichen werden exakt abgeglichen. Der Success-Abgleich des Targets ist strenger: exaktes Rufzeichen plus die ersten vier Zeichen des konfigurierten QTH. L&auml;dt ein Target `JN37` hoch, w&auml;hrend die Konfiguration `JN38` enth&auml;lt, erf&uuml;llt es die Target-Bedingung von Success nicht.

Peer-Identit&auml;ten verwenden exaktes Rufzeichen plus vollst&auml;ndigen gemeldeten Locator-String. Falsche, veraltete oder wechselnde Locator k&ouml;nnen eine physische Station aufteilen, in das falsche Segment verschieben oder den Filter f&uuml;r bewegte Stationen ausl&ouml;sen.

<a id="sec-6-3"></a>
#### 6.3 Historischer Decode-Code-Fallback

WSPRadar fordert Zeilen zun&auml;chst mit wspr.live `code = 1` f&uuml;r WSPR-2-Evidenz an. Liefert diese strenge Abfrage keine Target-seitige Evidenz, wird aus Gr&uuml;nden historischer Kompatibilit&auml;t ohne dieses Pr&auml;dikat erneut versucht und der Fallback im Laufstatus gemeldet.

Der Fallback erweitert die Auswahl. Aktuelle Exportmetadaten speichern nicht, welche Variante verwendet wurde; deshalb die sichtbare Fallback-Meldung dokumentieren, wenn sie relevant ist.

<a id="sec-6-4"></a>
#### 6.4 Warnungen zum Target-Active Gate

Das Gate ist bewusst Target-zentriert. Es best&auml;tigt die Teilnahme des Targets, schlie&szlig;t Reference-Evidenz au&szlig;erhalb dieser Zyklen aus und verhindert, dass bekannte Target-Ausfallzeit automatisch zum Misserfolg wird. Es weist weder Reference-Uptime noch einen offenen Funkpfad nach.

Ist die Target-Station beispielsweise &uuml;ber Nacht ausgeschaltet, werden Reference-Spots aus diesen Offline-Stunden nicht als Niederlagen gez&auml;hlt. Das ist der praktische Grund f&uuml;r das Gate. Es kann trotzdem nicht feststellen, ob die Reference in jedem erhaltenen Target-aktiven Zyklus durchgehend in Betrieb war.

Ein Tausch von Target und Reference kann deshalb zul&auml;ssige Zyklen und Decode Outcomes ver&auml;ndern. Sequenzielles TX A/B verwendet nicht dasselbe simultane Gate.

<a id="sec-6-5"></a>
#### 6.5 Warnungen zu Upstream-Daten

wspr.live erkl&auml;rt, dass seine Daten rohe WSPRnet-Meldungen sind und Duplikate, falsche Spots sowie andere Fehler enthalten k&ouml;nnen. Die freiwillig betriebene Infrastruktur garantiert weder Korrektheit noch Verf&uuml;gbarkeit oder Stabilit&auml;t. <a href="#ref-3">[Ref-3]</a>

wspr.live beschreibt Echtzeitdaten mit einer Verz&ouml;gerung von einigen Minuten und gibt an, alle paar Minuten nach neuen Spots zu suchen. Als praktische Betriebssch&auml;tzung etwa **f&uuml;nf Minuten** nach dem letzten WSPR-Zyklus warten, bevor ein aktuelles Analysefenster als ausreichend gef&uuml;llt erwartet wird. F&uuml;nf Minuten sind keine Vollst&auml;ndigkeitsgarantie: Verz&ouml;gerte Uploads, Ingestionsunterbrechungen und sp&auml;tere Korrekturen k&ouml;nnen danach erscheinen. <a href="#ref-3">[Ref-3]</a>

WSPRadar reduziert durch Paarung, Identit&auml;tsgruppierung, Mediane, Schwellen und Drill-Down die Empfindlichkeit gegen einzelne schlechte Zeilen. Wiederholte plausible Fehler verschwinden dadurch nicht.

Gemeldete Leistung und Locator stammen von Nutzern. Korrekte Mathematik auf einer falschen Leistung oder einem falschen Locator bleibt physikalisch falsch.

<a id="sec-7"></a>
### 7. Wissenschaftliche Methodik

Dieses Kapitel ist die autoritative Stelle f&uuml;r Formeln, Abgleichregeln und Aggregation. Funkamateure k&ouml;nnen die fr&uuml;heren Kapitel nutzen, ohne jedes Implementierungsdetail zu lesen; wissenschaftlich ernsthafte Berichte sollten beide Ebenen verwenden.

<a id="sec-7-1"></a>
#### 7.1 Datenquelle und Zeitmodell

WSPRadar liest die &ouml;ffentliche Tabelle `wspr.rx` &uuml;ber die schreibgesch&uuml;tzte HTTP-Schnittstelle von wspr.live. Spots sind Beobachtungsdaten unabh&auml;ngig betriebener Sender, Empf&auml;nger, Software und Netze. Sie sind keine randomisierte oder kalibrierte Stichprobe m&ouml;glicher Pfade.

Gew&auml;hlte Endpunkte werden zur Wiederverwendung von Abfragen auf 15-Minuten-Grenzen abgerundet. Success-Abfragen verwenden ein halboffenes Intervall `start <= time < end`. Compare-Abfragen verwenden aktuell Datenbank-`BETWEEN` und schlie&szlig;en eine Beobachtung exakt am Endzeitpunkt ein. Ein Grenzzyklus kann deshalb in Compare, aber nicht in Success erscheinen.

Ein **WSPR-Zyklus** ist das an einer geraden UTC-Minute ausgerichtete zweimin&uuml;tige Intervall. WSPRadar leitet simultane Zyklen aus Spot-Zeitstempeln ab. Sequenzielles TX A/B beh&auml;lt stattdessen Zeitstempel und ordnet Frame-Evidenz festen Uhrzeit-Bins zu.

<a id="sec-7-2"></a>
#### 7.2 Identit&auml;ts- und Abgleichregeln

| Analyse | Target-Abgleich | Peer-/Reference-Identit&auml;t | Kleinste Ergebniseinheit |
|---|---|---|---|
| RX Success | Exaktes RX-Rufzeichen plus Target-QTH Grid-4 | TX-Rufzeichen + gemeldeter TX-Locator | Ein Target-aktiver Peer-Zyklus |
| TX Success | Exaktes TX-Rufzeichen plus Target-QTH Grid-4 | RX-Rufzeichen + gemeldeter RX-Locator | Ein Target-aktiver Peer-Zyklus |
| Simultanes Compare | Exakte Target- und Reference-Rufzeichen | Entferntes Rufzeichen + gemeldeter Locator | Ein konsolidierter Peer-Zyklus |
| Sequenzielles TX A/B | Exaktes, nach WSPR-Frame getrenntes Target-Rufzeichen | RX-Rufzeichen + gemeldeter Locator | Ein festes Zeit-Bin |
| Lokaler Reference-Pool | Exaktes lokales Rufzeichen + Locator innerhalb des Radius | Entfernter Peer wie oben | Ein lokaler Identit&auml;tsbeitrag pro Zyklus/Pfad |

Mehrere qualifizierende Zeilen einer Seite in einem normalen simultanen Peer-Zyklus werden konsolidiert; das maximale normalisierte SNR repr&auml;sentiert diese Seite. Local Median bildet stattdessen zuerst einen Median innerhalb jeder lokalen Identit&auml;t und danach einen Median &uuml;ber die lokalen Identit&auml;ten.

<a id="sec-7-3"></a>
#### 7.3 Target-Active Gate

Success und simultanes Compare behalten Evidenz nur in Target-aktiven Zyklen:

* **TX:** Mindestens ein qualifizierender Target-Sendespots existiert irgendwo im Zyklus.
* **RX:** Mindestens ein qualifizierender, vom Target-Empf&auml;nger hochgeladener Decode existiert im Zyklus.

Reference-Evidenz au&szlig;erhalb dieser Zyklen wird ausgeschlossen. Das reduziert Offline-Bias, erzeugt aber eine Target-zentrierte Sch&auml;tzgr&ouml;&szlig;e; ein symmetrisches Reference-Aktivit&auml;ts-Gate gibt es nicht.

Gemeinsames Delta SNR erfordert weiterhin beide Seiten f&uuml;r dieselbe Peer-Identit&auml;t und ist damit strenger als das Zyklus-Gate. Decode Outcomes enth&auml;lt einseitige Evidenz und verlangt eine vorsichtigere Interpretation der Uptime.

Sequenzielles TX A/B verwendet statt dieses simultanen Gates deterministische Frame-Zuordnung und gepaarte Bins.

<a id="sec-7-4"></a>
#### 7.4 Success-Klassifikation und Formeln

F&uuml;r jeden Target-aktiven Peer-Zyklus speichert WSPRadar Target-Evidenz und unabh&auml;ngige externe Evidenz.

* **Externe RX-Evidenz:** Ein anderer Empf&auml;nger meldete dieselbe Senderidentit&auml;t im selben Zyklus.
* **Externe TX-Evidenz:** Der Peer-Empf&auml;nger meldete im selben Zyklus einen Nicht-Target-Sender auf demselben Band.

Target erfordert sowohl Target- als auch externe Evidenz. Elsewhere / Other Signals erfordert externe Evidenz ohne Target. Target-only bedeutet Target-Evidenz ohne externe Evidenz und wird aus dem Nenner ausgeschlossen.

$$\text{Success Rate}_{RX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Elsewhere}}$$

$$\text{Success Rate}_{TX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Other Signals}}$$

Die zul&auml;ssige Peer-Population stammt nach Band, Zeit, Gate, Filtern und Schwellen aus dem globalen Netz. Success Rate ist deshalb von beobachtbarer Netzaktivit&auml;t und Ausbreitung bedingt und keine Sch&auml;tzung jedes Sendeversuchs oder einer kalibrierten Empf&auml;nger-Detektionswahrscheinlichkeit.

<a id="sec-7-5"></a>
#### 7.5 Leistungsnormalisierung, Korrektur und Delta SNR

WSPR-SNR ist ein vom Decoder gemeldeter dB-Wert auf der WSJT-Skala mit 2500 Hz Referenzbandbreite. WSPR-Nachrichten enthalten die gemeldete Sendeleistung in dBm. <a href="#ref-1">[Ref-1]</a>

WSPRadar normalisiert erfolgreiches SNR auf eine gemeldete Referenz von 1 W / 30 dBm:

$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$

Das entfernt den **gemeldeten** Leistungsterm. Antennengewinn, Wirkungsgrad, Speiseleitungsverlust, EIRP, Empf&auml;ngerkalibrierung oder lokales Rauschen werden nicht korrigiert.

Reference SNR Correction wird zur Reference-Seite addiert:

$$SNR_{reference,corrected} = SNR_{reference} + Correction$$

Die allgemeine Vergleichsdefinition lautet:

$$\Delta SNR = SNR_{target} - SNR_{reference,corrected}$$

Eine positive Korrektur st&auml;rkt die Reference vor der Subtraktion und senkt Delta SNR. Eine negative Korrektur erh&ouml;ht Delta SNR.

TX-Vergleiche verwenden normalisiertes SNR, weil unterschiedliche Sendeleistungen beteiligt sein k&ouml;nnen. Bei RX-Paaren desselben Senders hebt sich der gemeinsame Leistungsterm auf. TX-Vergleiche verschiedener Rufzeichen h&auml;ngen direkt von der Genauigkeit gemeldeter Leistungen ab.

<a id="sec-7-6"></a>
#### 7.6 Gepaarte Evidenz und Decode Outcomes

Eine reine SNR-Analyse gepaarter Werte hat Survivorship-Bias: Beide Seiten m&uuml;ssen vergleichbare Evidenz erzeugen. Eine Konfiguration mit vielen zus&auml;tzlichen grenzwertigen Decodes kann einen niedrigeren gepoolten SNR-Median haben, gerade weil sie schw&auml;chere Signale erreicht.

WSPRadar beh&auml;lt deshalb:

1. **Paired Delta SNR:** Bedingte Signalst&auml;rkedifferenz, wenn beide Seiten vergleichbare Evidenz erzeugten.
2. **Decode Outcomes:** Joint-, Only-Target-, Only-Reference- und Both-(Async)-Evidenz au&szlig;erhalb oder rund um diese gepaarte Teilmenge.

Decode Outcomes ist nicht leistungsnormalisiert. Bei einer exklusiven TX-Beobachtung fehlt das SNR der anderen Seite und kann nicht rekonstruiert werden. Ungleiche Sendeleistungen k&ouml;nnen daher exklusive TX-Evidenz dominieren, selbst wenn gemeinsames Delta SNR normalisiert ist.

`STATIONS`-Kategorien einer Compare-Karte ordnen Identit&auml;ten zu; `SPOTS`-Kategorien z&auml;hlen Evidenzvolumen. Success-Kartenbalken verwenden dieselben zwei Ebenen, richten sie aber am Success-Nenner aus.

<a id="sec-7-7"></a>
#### 7.7 Aggregationshierarchie

Mediane verringern die Empfindlichkeit gegen einzelne Extremwerte, duplikat&auml;hnliche Bursts und quantisierte SNR-Ausrei&szlig;er. Sie entfernen jedoch weder systematischen Kalibrierfehler noch Ausbreitungsbias oder Korrelation &uuml;ber Zeit und Stationen. Die Berechnung eines Peer-Werts vor dem Segmentwert ist ebenfalls eine Gewichtungsentscheidung: Jeder qualifizierende Peer tr&auml;gt einmal bei, sodass eine Station mit hohem Volumen nicht allein wegen mehr hochgeladener Beobachtungen dominiert.

**Success**

1. Jeden Target-aktiven Peer-Zyklus klassifizieren.
2. Target, Gegen-Evidenz und Target-only nach Peer `Rufzeichen + Locator` summieren.
3. Konfigurierte Target+Gegen-Evidenz-Schwelle verlangen.
4. Eine Success Rate pro qualifizierendem Peer berechnen.
5. Das arithmetische Segmentmittel der Peer-Raten berechnen.
6. Die gepoolte Rate auf Beobachtungsebene als Diagnose behalten.

**Simultanes Compare**

1. Target- und Reference-Evidenz nach Zyklus und Peer-Identit&auml;t konsolidieren.
2. Delta SNR f&uuml;r gemeinsame Zyklen berechnen.
3. Konfigurierten Joint-Z&auml;hler pro Peer verlangen.
4. Einen Delta-SNR-Stationsmedian berechnen.
5. Segmentmedian &uuml;ber Stationsmediane berechnen.

**Sequenzielles TX A/B**

1. Spots den Target- und Reference-Frame-Folgen zuordnen.
2. Jede Seite nach Zeit-Bin und Peer-Identit&auml;t gruppieren.
3. Einen Mikro-Median pro Seite und Bin berechnen.
4. Bin-Delta berechnen, wenn beide Mikro-Mediane existieren.
5. Konfigurierte Anzahl gepaarter Bins verlangen.
6. Stations- und Segmentmediane berechnen.

**Local Median Reference**

1. Jede lokale Reference `Rufzeichen + Locator` innerhalb von Zyklus und entferntem Peer gruppieren.
2. Das mediane normalisierte SNR dieser lokalen Identit&auml;t berechnen.
3. Den exakten inklusiven Mittelpunktmedian &uuml;ber lokale Identit&auml;ten bilden.
4. Target mit dieser zyklusbezogenen Reference vergleichen.

Bei gerader Gr&ouml;&szlig;e des lokalen Pools wird der Mittelpunkt der beiden zentralen Werte verwendet. Der Pool kann sich in jedem Zyklus &auml;ndern.

<a id="sec-7-8"></a>
#### 7.8 Stabilit&auml;t und Histogrammkonstruktion

WSPRadar verwendet ein deterministisches Perzentil-Bootstrap mit 500 Ziehungen mit Zur&uuml;cklegen und meldet das zentrale 90%-Intervall um den Median. Intervalle auf Stationsebene resamplen Stationsmediane. Rohe gepaarte Intervalle resamplen Delta-Werte von Peer-Zyklen oder gepaarten Bins.

Die Berechnung behandelt Werte als austauschbar, obwohl WSPR-Beobachtungen nach Station, Zeit und Geografie korreliert bleiben k&ouml;nnen. Es ist ein beschreibendes **Stabilit&auml;tsintervall**, kein Konfidenzintervall und kein Signifikanztest.

Compare-Delta-SNR-Histogramme verwenden feste Bins innerhalb eines Panels. Normalerweise sind es 1-dB-Bins; 0,5 dB wird nur bei einem klaren Halb-dB-Raster verwendet. Breite Bereiche werden auf 1, 2, 3, 6 oder 10 dB zusammengefasst, damit ein Panel h&ouml;chstens 40 Balken enth&auml;lt. Eine minimale sichtbare Spanne von 3 dB verhindert die optische &Uuml;bertreibung sehr kleiner Variation.

<a id="sec-7-9"></a>
#### 7.9 Geografie und Sonnenklassifikation

WSPRadar berechnet Entfernung und Azimut mit einem kugelf&ouml;rmigen Erdradius von 6371 km und zeichnet eine azimutal-&auml;quidistante Projektion um das Target-QTH. Radialgrenzen liegen bei 2500, 5000, 10000, 15000, 20000 und 22000 km; Azimutsektoren umfassen 22,5 Grad.

Das ist intern konsistente Kartengeometrie und keine vermessungstechnische Geod&auml;sie. Gemeldete Locator stehen f&uuml;r Positionen in Grid-Zellen, nicht f&uuml;r gemessene Antennenkoordinaten.

`Lokaler QTH Sonnenstand` verwendet die Sonnenh&ouml;he am Target-QTH. Success-Evidenzdiagramme klassifizieren getrennt die abgetastete Beleuchtung des Gro&szlig;kreispfads als Nacht, Greyline/gemischt oder Tageslicht. Beide beantworten unterschiedliche Fragen.

<a id="sec-8"></a>
### 8. Grenzen, zul&auml;ssige Aussagen und Reproduzierbarkeit

<a id="sec-8-1"></a>
#### 8.1 Was WSPRadar nicht isoliert

WSPRadar-Ergebnisse beschreiben arbeitende Stationssysteme unter ausgew&auml;hlten Netz- und Ausbreitungsbedingungen. Sie messen nicht direkt:

* Antennengewinn in dBi;
* Strahlungswirkungsgrad;
* Abstrahlwinkel;
* kalibrierte Empf&auml;ngerempfindlichkeit;
* absolute Feldst&auml;rke;
* jeden versuchten oder geplanten Sendevorgang;
* formale statistische Signifikanz oder Kausalit&auml;t.

Wesentliche Einschr&auml;nkungen:

* Crowd-sourced Rufzeichen, Locator, Leistungen und Spots k&ouml;nnen falsch sein;
* das Archiv enth&auml;lt erfolgreiche Decodes statt vollst&auml;ndiger Versuchs-/Fehlerprotokolle;
* Success Rate ist von global stammenden beobachtbaren Opportunities bedingt;
* ein nirgends decodierter TX-Zyklus ist ohne externes Log nicht von keiner Sendung unterscheidbar;
* Target-Active Gate ist asymmetrisch;
* sequenzielles TX A/B bleibt zeitlich getrennt;
* Normalisierung gemeldeter Leistung ist nur so genau wie das gemeldete Feld;
* Stationshardware, Software, Gel&auml;nde, Rauschen, Polarisation und Ausbreitung bleiben kombiniert;
* Netzdichte variiert nach Geografie, Band und Zeit;
* Entfernung bestimmt weder Abstrahlwinkel noch Ausbreitungsart;
* Upstream-Verf&uuml;gbarkeit und Archivkorrekturen bleiben extern.

<a id="sec-8-2"></a>
#### 8.2 Unterst&uuml;tzte und nicht unterst&uuml;tzte Formulierungen

| Vermeiden | Evidenzgerechte Formulierung |
|---|---|
| "Antenne A hat 3 dBi mehr Gewinn." | "Pfad A erzeugte f&uuml;r die gepaarte Evidenz auf diesem Band, in diesem Fenster und Segment ein medianes normalisiertes Delta SNR von +3,0 dB gegen B." |
| "Meine Empf&auml;ngerempfindlichkeit betr&auml;gt 72%." | "Die Success Rate des Target-Empf&auml;ngers betrug 72% unter qualifizierenden Peer-Zyklen, die unabh&auml;ngig anderswo best&auml;tigt wurden." |
| "Success sollte nahe 100% liegen." | "Success ist ein bedingter globaler Faktor f&uuml;r Netzreichweite; 100% sind nicht der erwartete Ausgangswert." |
| "A ist statistisch signifikant besser." | "Der gepaarte Median sprach f&uuml;r A, und sein beschreibendes 90%-Stabilit&auml;tsintervall betrug [Bereich]; ein Signifikanztest wurde nicht durchgef&uuml;hrt." |
| "Die Antenne hat einen niedrigeren Abstrahlwinkel." | "Der beobachtete Vorteil konzentrierte sich auf die angegebenen Segmente mit gr&ouml;&szlig;erer Entfernung; der Abstrahlwinkel wurde nicht gemessen." |
| "A ist effizienter, weil es mehr exklusive Decodes hatte." | "A erzeugte unter gemeldeter Leistung, Zeitplan und Netzbedingungen mehr exklusive Decode-Evidenz; Wirkungsgrad wurde nicht isoliert." |
| "Der lokale Median ist die durchschnittliche lokale Station." | "Die Reference war der Zyklus-/Pfadmedian aus je einem Beitrag pro aktiver lokaler Identit&auml;t aus Rufzeichen+Locator." |

<a id="sec-8-3"></a>
#### 8.3 Checkliste f&uuml;r Berichte

F&uuml;r ein seri&ouml;ses Ergebnis angeben:

* WSPRadar-Version und vorzugsweise Git-Commit;
* exakter UTC-Start und exaktes UTC-Ende;
* exaktes Band und TX-/RX-Richtung;
* Target-Rufzeichen und konfiguriertes QTH;
* Benchmark-Design, Reference-Identit&auml;t oder lokalen Radius/Methode;
* Hardware-Frame-/Bin-Design, falls anwendbar;
* Reference SNR Correction und Kalibriergrundlage;
* Filter f&uuml;r spezielle, bewegte Stationen und Sonnenstand;
* alle Evidenzschwellen;
* Anzahl gemeinsamer Stationen und Spots/Bins;
* Delta-SNR-Stationsmedian und 90%-Stabilit&auml;tsintervall;
* Decode Outcomes und Verteilungen von `STATIONS` / `SPOTS`;
* Success Rate mit Nenner und Gewichtungsebene;
* Hardware, Leistung, Zeitplan und bekannte Einschr&auml;nkungen;
* Exportpaket plus externe Experimentnotizen.

Vor teuren Entscheidungen aufgrund einer kleinen Differenz Wiederholung, Pfadtausch oder unabh&auml;ngige Kalibrierung einsetzen.

<a id="sec-8-4"></a>
#### 8.4 Analyse-Exportpaket

`Alle Ergebnisse zum Download vorbereiten` erstellt aus dem abgeschlossenen Lauf und den aktuellen Inspector-Auswahlwerten ein Paket. Ein typisches ZIP enth&auml;lt:

```text
config/
  wspradar_config.config
  run_metadata.json
compare/                         # wenn ein Benchmark-Ergebnis existiert
  figure_map_highres.png
  figure_segment_insight.png
  figure_selected_station_evidence.png
  table_station_insights_current_segment.csv
  table_drilldown_selected_stations.csv
  table_drilldown_all_stations_current_segment.csv
  analysis_cache.parquet
success/                         # wenn ein Success-Ergebnis existiert
  ...gleiches Abbildungs-/Tabellenmuster...
  analysis_cache.parquet
```

Abbildungen verwenden eine hochaufl&ouml;sende helle Papierdarstellung. Dateien ohne passende Exportanweisung oder ausgew&auml;hlte Evidenz k&ouml;nnen fehlen. CSV-Dateien spiegeln aktuelle Segment- und Stationsauswahl wider. Parquet-Dateien enthalten verarbeitete Evidenz nach Filtern und keine unver&auml;nderten wspr.live-Dumps.

Konfiguration und Laufmetadaten speichern Anwendungsversion, Exportzeit, Sprache, Richtung, Band, Benchmark-Auswahl, konfigurierte Zeitauswahl, Korrektur, Filter, Schwellen, Ergebnisbl&ouml;cke und Inspector-Auswahl.

Das Paket unterst&uuml;tzt Audit und Reproduzierbarkeit, ist aber kein vollst&auml;ndiger Rechensnapshot. Derzeit fehlen:

* exaktes SQL oder unver&auml;nderte Upstream-Antworten;
* Dependency-Lock oder Beschreibung des Betriebssystems;
* Git-Commit-ID;
* Zustand des strengen gegen&uuml;ber dem Fallback-Decode-Filter;
* eigene exakt aufgel&ouml;ste/quantisierte Endpunkte eines Laufs mit `Letzte X Stunden`.

Das ZIP zusammen mit Stationsnotizen, Schaltzeitplan, Leistungsmessungen und Kalibrierdaten aufbewahren.

<a id="sec-8-5"></a>
#### 8.5 Haftungsausschluss und Lizenz

WSPRadar ist experimentelle Open-Source-Software und wird ohne Gew&auml;hrleistung "wie besehen" bereitgestellt. Quellcode und Methoden sind pr&uuml;fbar, aber Genauigkeit, Vollst&auml;ndigkeit, Verf&uuml;gbarkeit und Eignung werden nicht garantiert. Keine gro&szlig;en finanziellen oder sicherheitsrelevanten Entscheidungen allein auf WSPRadar st&uuml;tzen.

WSPRadar steht unter der GNU Affero General Public License Version 3 (AGPLv3). Ma&szlig;geblich ist die Datei `LICENSE` im Repository.

<a id="sec-a"></a>
### Anhang A: Parallele WSJT-X-Instanzen

Dieses Verfahren erstellt unter Windows eine zweite isolierte WSJT-X-Instanz, zum Beispiel f&uuml;r simultanes RX Hardware A/B. Das aktuelle WSJT-X-Handbuch dokumentiert `--rig-name` als unterst&uuml;tzten Weg, Einstellungen und schreibbare Dateien jeder Instanz zu isolieren. WSJT-X-Versionen und Installationspfade k&ouml;nnen sich &auml;ndern; bei abweichenden Men&uuml;s das aktuelle Handbuch pr&uuml;fen. <a href="#ref-2">[Ref-2]</a>

#### A.1 Zweite Instanz erstellen

1. Eine Desktop-Verkn&uuml;pfung f&uuml;r `wsjtx.exe` erstellen.
2. Eigenschaften der Verkn&uuml;pfung &ouml;ffnen.
3. Im Feld **Target/Ziel** der Verkn&uuml;pfung au&szlig;erhalb der Anf&uuml;hrungszeichen des Programmpfads einen eigenen Rig-Namen erg&auml;nzen. Den tats&auml;chlichen Pfad der Installation verwenden, zum Beispiel:
   `"C:\WSJTX\bin\wsjtx.exe" --rig-name=SDR`
4. Die Verkn&uuml;pfung einmal starten und wieder schlie&szlig;en. F&uuml;r `--rig-name=SDR` erstellt Windows diese isolierten Orte:
   * Einstellungen: `%LOCALAPPDATA%\WSJT-X - SDR\WSJT-X - SDR.ini`
   * Log-/Schreibverzeichnis: `%LOCALAPPDATA%\WSJT-X - SDR\`
   * Standardverzeichnis f&uuml;r gespeicherte Audiodaten: `%LOCALAPPDATA%\WSJT-X - SDR\save\`

#### A.2 Ausgangskonfiguration bei Bedarf klonen

1. Alle WSJT-X-Instanzen schlie&szlig;en.
2. `%LOCALAPPDATA%\WSJT-X\WSJT-X.ini` kopieren.
3. Die Datei in `%LOCALAPPDATA%\WSJT-X - SDR\` einf&uuml;gen.
4. Die Kopie in `%LOCALAPPDATA%\WSJT-X - SDR\WSJT-X - SDR.ini` umbenennen und bei beabsichtigtem Klonen die neu initialisierte Instanzdatei ersetzen.

#### A.3 Jeden Datenpfad trennen

Eine geklonte Konfiguration kann beide Instanzen weiterhin auf denselben Audioeingang oder Speicherpfad verweisen lassen. Dadurch kann derselbe Audiostream doppelt decodiert werden oder es k&ouml;nnen Dateikonflikte entstehen. In der zweiten Instanz pr&uuml;fen:

1. **File > Settings > Audio** &ouml;ffnen.
2. Unter **Soundcard** bei **Input** den vorgesehenen unabh&auml;ngigen Empf&auml;nger oder das Audioger&auml;t w&auml;hlen. Das WSJT-X-Handbuch verlangt eine Audioger&auml;tekonfiguration mit 48.000 Hz und 16 Bit.
3. **Save Directory** auf einen instanzspezifischen Pfad setzen, normalerweise `%LOCALAPPDATA%\WSJT-X - SDR\save\`.
4. **AzEl Directory** auf einen instanzspezifischen Pfad setzen, zum Beispiel `%LOCALAPPDATA%\WSJT-X - SDR\`.
5. **File > Settings > General** &ouml;ffnen und das exakte Setup-B-Rufzeichen sowie den f&uuml;r Meldungen verwendeten Locator einstellen.
6. Zur WSPR-Hauptansicht zur&uuml;ckkehren, Band und Audiopegel best&auml;tigen, bei Bedarf den Spot-Upload aktivieren und pr&uuml;fen, dass hochgeladene Zeilen die Setup-B-Identit&auml;t verwenden.
7. Zeitsynchronisation beider Instanzen best&auml;tigen.

Getrennte Verzeichnisse beweisen keine Unabh&auml;ngigkeit der HF-Pfade. Empirisch best&auml;tigen, dass beide Datenstr&ouml;me die vorgesehene Hardware verwenden.

<a id="sec-b"></a>
### Anhang B: Zeitgesteuerte A/B-Relaisumschaltung

Bei sequenziellen TX-A/B-Antennentests ist ein Sender, der &uuml;ber einen kontrollierten Schalter zwei HF-Pfade speist, normalerweise zwei unabh&auml;ngigen Sendern vorzuziehen. Sender, Frequenzreferenz, WSPR-Kette, Rufzeichen, Leistungseinstellung und Timing bleiben gemeinsam.

WSPRadar enth&auml;lt:

`tools/Timed-AB-Relay-Switch`

Release-Paket:

https://github.com/markusthemaker/WSPRadar/releases/download/timed-ab-relay-switch-v0.1.0/Timed-AB-Relay-Switch-v0.1.0.zip

Das Hilfsprogramm steuert unterst&uuml;tzte USB-HID-Relais auf den beiden WSPR-Frame-Folgen:

* Target-Frames: UTC `00, 04, 08, ...`
* Reference-Frames: UTC `02, 06, 10, ...`

Eine optionale Vorlaufzeit l&auml;sst den HF-Pfad vor der Sendung einschwingen. Das Hilfsprogramm zielt auf verbreitete ATtiny45/V-USB-HID-Relaisplatinen mit USB-VID/PID `16c0:05df` und verwendet den Python-HID-Stack unter Windows, Linux und macOS. Aktuelle Installation, Berechtigungen und Optionen stehen in seinem README.

Installation aus dem Werkzeugverzeichnis:

```bat
py -3 -m pip install -r requirements-relay.txt
```

oder unter Linux/macOS:

```sh
python3 -m pip install -r requirements-relay.txt
```

Windows-Einrichtung und Testlauf:

```bat
Start-Timed-AB-Relay-Switch.cmd --setup
Start-Timed-AB-Relay-Switch.cmd --dry-run
```

Linux/macOS-Einrichtung und Testlauf:

```sh
chmod +x ./Start-Timed-AB-Relay-Switch.sh
./Start-Timed-AB-Relay-Switch.sh --setup
./Start-Timed-AB-Relay-Switch.sh --dry-run
```

Ein kleines USB-Relais sollte normalerweise nicht direkt HF schalten. Es sollte ein passend dimensioniertes HF-Schalt- oder Relaissystem steuern. Spannung, Strom, Polarit&auml;t, ausfallsicheren Zustand, HF-Leistung, Isolation und Verriegelungen pr&uuml;fen.

Vor dem Senden:

* ohne HF-Leistung testen;
* Polarit&auml;t der Target- und Reference-Pfade pr&uuml;fen;
* sicherstellen, dass w&auml;hrend einer WSPR-Sendung nicht umgeschaltet wird;
* Dummy Load oder Durchgangs-/SWR-Test mit geringer Leistung verwenden;
* Relaiskanal, Polarit&auml;t, Vorlaufzeit, Frame-Zuordnung und Pfadzuordnung dokumentieren.

Schaltverlust, Isolation, Steckverbinder, Unterschiede der Speiseleitungen und Antennenumgebung bleiben Teil des Ergebnisses. Ein Tausch der Antennen zwischen Schaltpfaden kann helfen, Antennen- von Pfadeffekten zu trennen.

<a id="sec-c"></a>
### Anhang C: Referenz-SNR-Kalibrierung

Dieses Verfahren sch&auml;tzt einen stabilen additiven Offset zwischen Empfangsketten oder Reference-seitigen Pfaden.

1. **Gemeinsamer Eingang:** Beide Empfangsketten &uuml;ber einen geeigneten Splitter und kontrollierte Kabel aus einer stabilen Antenne speisen.
2. **Splitter charakterisieren:** Ausgangsungleichgewicht und Kabelunterschiede ber&uuml;cksichtigen; Ausg&auml;nge in einem Kontrolllauf tauschen, wenn praktisch m&ouml;glich.
3. **Gepaarte Evidenz erfassen:** Gleichzeitig &uuml;ber die beabsichtigten Signalpegel arbeiten, ohne Verst&auml;rkung oder Decoder-Einstellungen zu &auml;ndern.
4. **Offset sch&auml;tzen:** Gepaarte Delta-SNR-Evidenz verwenden und angeben, ob der Sch&auml;tzer stationsbalanciert oder ein Rohpaar-Sch&auml;tzer ist.
5. **Stabilit&auml;t pr&uuml;fen:** Nach Station, Zeit und SNR untersuchen. Eine Konstante ist nicht vertretbar, wenn sich der Offset mit Pegel, Frequenz, AGC oder Zeit &auml;ndert.
6. **Vorzeichen anwenden:** Beobachteten Offset `Target - Reference` mit demselben Vorzeichen eingeben.
7. **Validieren:** Wiederholen oder Pfade tauschen und best&auml;tigen, dass das korrigierte Common-Input-Delta plausibel nahe null liegt.

Ein schmales Stabilit&auml;tsintervall zeigt Wiederholbarkeit der vorhandenen Stichprobe und keine r&uuml;ckf&uuml;hrbare Laborgenauigkeit. Splitterverlust, Fehlanpassung, Kopplung und Quelleninstabilit&auml;t k&ouml;nnen verbleiben.

<a id="sec-d"></a>
### Anhang D: Literatur, Stand der Technik und Einordnung

Dieser Anhang st&uuml;tzt die Einordnung von WSPRadar, ohne den Arbeitsablauf f&uuml;r Funkamateure zu unterbrechen. Er behauptet nicht, dass die Literatur jede WSPRadar-Kennzahl oder Implementierungsentscheidung validiert.

#### D.1 WSPR als Beobachtungsnetz

Taylor und Walker beschreiben Zweck und praktische weltweite Nutzung von WSPR als Weak Signal Propagation Reporter. <a href="#ref-4">[Ref-4]</a>

Das &ouml;ffentliche Archiv ist kein Laborinstrument. Die Kombination aus breiter geografischer Beteiligung, historischer Tiefe und erfolgreichen Decode-Datens&auml;tzen macht es stark f&uuml;r Beobachtungsanalysen, verlangt aber einen ausdr&uuml;cklichen Umgang mit Stationsaktivit&auml;t, Identit&auml;t und Sampling.

#### D.2 WSPR in der Funkwissenschaft

Lo et al. verwendeten WSPR-Beobachtungen auf 7 MHz zur Untersuchung von Greyline-Ausbreitung. Sie diskutieren inkonsistente Stationsangaben, fehlende offizielle Betriebspl&auml;ne und den Nutzen, Sender- oder Empf&auml;ngeraktivit&auml;t an anderer Stelle im Netz zu pr&uuml;fen. Diese Aktivit&auml;tslogik ist relevantes Vorwissen f&uuml;r das Target-Active Gate von WSPRadar, obwohl sich die Sch&auml;tzgr&ouml;&szlig;en unterscheiden. <a href="#ref-5">[Ref-5]</a>

Frissell et al. beschreiben WSPRNet, Reverse Beacon Network und PSKReporter als wichtige Amateurfunk-Beobachtungsnetze f&uuml;r Heliophysik und Citizen Science. Sie unterscheiden diese breiten Netze von gezielt gebauten, fein kalibrierten Instrumenten. <a href="#ref-6">[Ref-6]</a>

Die Schlussfolgerung ist bewusst begrenzt: WSPR kann systematische funkwissenschaftliche Fragen unterst&uuml;tzen, wenn Aktivit&auml;t, Sampling, Identit&auml;t und St&ouml;rvariablen ausdr&uuml;cklich behandelt werden. Peer-Review macht nicht automatisch jeden Stationsvergleich valide.

#### D.3 Vorarbeiten zu Antennen- und Stationsvergleichen

Vanhamel, Machiels und Lamy verwendeten zwei konditionierte, nahezu identische 160-m-WSPR-Empfangsstationen zum Vergleich von Antennen und Ausbreitung. Ihr simultanes Design mit gemeinsamem Signal st&uuml;tzt RX Hardware A/B und die Notwendigkeit, Offsets der Empfangsketten zu charakterisieren. <a href="#ref-7">[Ref-7]</a>

Zander untersucht den relativen Wirkungsgrad von HF-Antennen &uuml;ber das globale WSPR-Empf&auml;ngernetz und diskutiert Genauigkeit und Grenzen. Das ist relevante TX-seitige Vorarbeit, beweist aber nicht, dass jedes WSPR-Delta-SNR kalibrierter Wirkungsgrad ist. <a href="#ref-8">[Ref-8]</a>

Milazzo liefert fr&uuml;here amateurfunktechnische Vorarbeiten zum WSPR-Antennenvergleich. Sie belegen einen langj&auml;hrigen praktischen Bedarf und kein peer-reviewtes standardisiertes Protokoll. <a href="#ref-9">[Ref-9]</a>

Griffiths und Squibb verwendeten WSPR-Spot- und SNR-Informationen zur Untersuchung praktischer Verbesserungen von HF-Empfangssystemen. Das st&uuml;tzt eine Interpretation des gesamten Stationssystems einschlie&szlig;lich Antenne, Speiseleitung, lokalem Rauschen und Empf&auml;nger. <a href="#ref-10">[Ref-10]</a>

#### D.4 Werkzeuge und praktische Vorarbeiten

WSPR.Rocks bietet schnelle WSPR-Exploration, SQL-Zugriff, Karten, Tabellen, SpotQ und weitere Analysen. WSPRadar unterscheidet sich durch einen Arbeitsablauf rund um ausdr&uuml;ckliche Experimentdesigns, Paarung und Audit auf Zeilenebene statt einer Rangliste. <a href="#ref-11">[Ref-11]</a>

Griffiths und Robinett demonstrieren Datenbank-Joins und Zeitreihenansichten zum Vergleich gemeinsamer WSPR-Sender, Zeiten und B&auml;nder. <a href="#ref-12">[Ref-12]</a>

WSPRdaemon konzentriert sich auf robuste Erfassung mit mehreren Empf&auml;ngern, Zeitplanung und zus&auml;tzliche Rausch-/Doppler-Metadaten. Das zeigt, warum Erfassungsstabilit&auml;t und Rauschkontext f&uuml;r RX-Analysen wichtig sind. <a href="#ref-13">[Ref-13]</a>

SOTABEAMS WSPRlite und DXplorer bieten zug&auml;ngliche WSPR-basierte Antennen-/Standortvergleiche und die DX10-Kennzahl. <a href="#ref-14">[Ref-14]</a>

WSPR-Station-Compare verbindet Stationsvergleichssoftware ausdr&uuml;cklich mit den Methoden von Vanhamel und Zander. <a href="#ref-15">[Ref-15]</a>

Das Antenna Performance Analysis Tool ist ein weiterer nutzerorientierter Dienst f&uuml;r WSPR-Antennenberichte. Seine Existenz bedeutet, dass WSPRadar nicht behaupten sollte, das erste WSPR-Antennenanalysewerkzeug zu sein. <a href="#ref-16">[Ref-16]</a>

WATT bietet Berichte, Karten, Filter und Zeitleistenexploration in Excel/VBA. Das unterstreicht den praktischen Wert pr&uuml;fbarer Daten gegen&uuml;ber einer einzigen festen Punktzahl. <a href="#ref-17">[Ref-17]</a>

#### D.5 Einordnung von WSPRadar

Der Beitrag von WSPRadar ist die Integration von:

* Pr&uuml;fungen der Target-Aktivit&auml;t;
* Vergleichen im selben Zyklus oder in kontrollierten Bins;
* Normalisierung gemeldeter Leistung;
* Hardware-, Buddy- und lokalen Benchmark-Designs;
* bedingter Success-Analyse;
* gepaartem Delta SNR und kategorischen Decode Outcomes;
* stationsbalancierter geografischer Aggregation;
* Zusammensetzung von `STATIONS` und `SPOTS`;
* Drill-Down und exportierbarer verarbeiteter Evidenz.

WSPRadar sollte nicht als Ersatz f&uuml;r wspr.live, WSPR.Rocks, WSPRdaemon, DXplorer oder kontrollierte HF-Messungen beschrieben werden. Es arbeitet eine methodische Ebene &uuml;ber einem Spot-Browser: **Welche Beobachtungen sind f&uuml;r dieses Experiment zul&auml;ssig, welche gepaarte Differenz wurde beobachtet, welche einseitige Evidenz bleibt, und kann die Schlussfolgerung auditiert werden?**

<a id="sec-ref"></a>
### Quellen

* <a id="ref-1"></a><a href="#ref-1">[Ref-1]</a> **Offizielle technische &Uuml;bersicht.** ARRL, *WSPR*: Nachrichtenformat, Codierung, Dauer, Timing, belegte Bandbreite und SNR-Referenz. Abgerufen am 12.07.2026.
  https://www.arrl.org/wspr

* <a id="ref-2"></a><a href="#ref-2">[Ref-2]</a> **Offizielle Softwaredokumentation.** WSJT-X 3.0.1 User Guide: WSPR-Nachrichtenformate und Decoderleistung; Windows-Dateitrennung mit `--rig-name`; Audioeinstellungen und Dateiorte. Abgerufen am 12.07.2026.
  https://wsjt.sourceforge.io/wsjtx-main_en.html

* <a id="ref-3"></a><a href="#ref-3">[Ref-3]</a> **Offizielle Datendienstdokumentation.** WSPR.live, *Welcome to WSPR Live* und *WSPR Exporter*: Datenbankbeschreibung, Schema, Mode-Code-Zuordnung, Rohdaten-/Verf&uuml;gbarkeitshinweis und Echtzeitverz&ouml;gerung. Abgerufen am 12.07.2026.
  https://wspr.live/
  https://wspr.live/wspr_downloader.php

* <a id="ref-4"></a><a href="#ref-4">[Ref-4]</a> Taylor, J. H.; Walker, B. (2010). *WSPRing Around the World*. QST, 94(11), 30-32.
  https://www.arrl.org/files/file/History/History%20of%20QST%20Volume%201%20-%20Technology/QS11-2010-Taylor.pdf

* <a id="ref-5"></a><a href="#ref-5">[Ref-5]</a> **Peer-reviewter Artikel.** Lo, S.; Rankov, N.; Mitchell, C.; Witvliet, B. A.; Jayawardena, T. P.; Bust, G.; Liles, W.; Griffiths, G. (2022). *A Systematic Study of 7 MHz Greyline Propagation Using Amateur Radio Beacon Signals*. Atmosphere, 13(8), 1340. doi:10.3390/atmos13081340.
  https://www.mdpi.com/2073-4433/13/8/1340

* <a id="ref-6"></a><a href="#ref-6">[Ref-6]</a> **Peer-reviewter &Uuml;bersichtsartikel.** Frissell, N. A. et al. (2023). *Heliophysics and amateur radio: citizen science collaborations for atmospheric, ionospheric, and space physics research and operations*. Frontiers in Astronomy and Space Sciences, 10, 1184171. doi:10.3389/fspas.2023.1184171.
  https://www.frontiersin.org/articles/10.3389/fspas.2023.1184171/full

* <a id="ref-7"></a><a href="#ref-7">[Ref-7]</a> **Peer-reviewter Artikel.** Vanhamel, J.; Machiels, W.; Lamy, H. (2022). *Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band*. International Journal of Antennas and Propagation, 2022, 4809313. doi:10.1155/2022/4809313.
  https://research.tudelft.nl/en/publications/using-the-wspr-mode-for-antenna-performance-evaluation-and-propag/

* <a id="ref-8"></a><a href="#ref-8">[Ref-8]</a> **Preprint.** Zander, J. (2022). *Simple HF antenna efficiency comparisons using the WSPR system*. arXiv:2209.08989. doi:10.48550/arXiv.2209.08989.
  https://arxiv.org/abs/2209.08989

* <a id="ref-9"></a><a href="#ref-9">[Ref-9]</a> **Amateurfunk-Fachartikel.** Milazzo, C. F. / KP4MD (2011). *Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*.
  https://www.qsl.net/kp4md/wspr.htm

* <a id="ref-10"></a><a href="#ref-10">[Ref-10]</a> Griffiths, G.; Squibb, N. J. (2017). *Improving HF Band SNR from analysis of WSPR spots*. Practical Wireless, Oktober 2017, 23-26.
  https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf

* <a id="ref-11"></a><a href="#ref-11">[Ref-11]</a> **Werkzeugdokumentation.** WSPR.Rocks, *Help &amp; Documentation*: SpotQ, SQL-Zugriff, Duplikatanalyse, Karten, Diagramme und Heatmaps.
  https://wspr.rocks/help.html

* <a id="ref-12"></a><a href="#ref-12">[Ref-12]</a> Griffiths, G.; Robinett, R. (2020). *Aids to the Presentation and Analysis of WSPR Spots: TimescaleDB database and Grafana*. ARRL/TAPR Digital Communications Conference 2020.
  https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf

* <a id="ref-13"></a><a href="#ref-13">[Ref-13]</a> **Werkzeugdokumentation.** WSPRdaemon, *How wsprdaemon Works*: Multi-Receiver-Decodierung, Meldung, Zeitplanung, Rausch- und Doppler-Metadaten.
  https://wsprdaemon.readthedocs.io/en/stable/description/how_it_works.html

* <a id="ref-14"></a><a href="#ref-14">[Ref-14]</a> **Produktdokumentation.** SOTABEAMS, *WSPRlite Classic / DXplorer*: WSPR-basierte Antennenleistungsanalyse und DX10-Kennzahl.
  https://www.sotabeams.co.uk/wsprlite-classic

* <a id="ref-15"></a><a href="#ref-15">[Ref-15]</a> **Projektdokumentation.** WSPR-Station-Compare, Projektseite mit Verweisen auf Vanhamel et al. und Zander.
  https://sites.google.com/myuba.be/wspr-station-compare/home

* <a id="ref-16"></a><a href="#ref-16">[Ref-16]</a> **Werkzeugdokumentation.** Antenna Performance Analysis Tool, WSPR-basierter Antennenbericht-Generator.
  https://wspr.bsdworld.org/

* <a id="ref-17"></a><a href="#ref-17">[Ref-17]</a> **Werkzeugdokumentation.** GM4EAU, *WATT WSPR Analysis Tool*: Excel/VBA-Berichte, Karten, Filter und Zeitleistenanimation.
  https://www.gm4eau.com/home-page/wspr/
"""
