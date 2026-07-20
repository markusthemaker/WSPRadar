# docs/doc_de.py

"""Maßgebliches deutschsprachiges Anwender- und Wissenschaftshandbuch für WSPRadar."""

DOC_DE = r"""
---

<a id="sec-1"></a>

### 0. Warum WSPRadar?

Funkamateure verändern und optimieren ihre Stationen fortlaufend. Eine neue Antenne wird aufgebaut, die Masthöhe verändert, eine Speiseleitung ersetzt, ein Balun überarbeitet oder ein Vorverstärker ergänzt. Danach stellt sich fast zwangsläufig dieselbe Frage: **Hat die Änderung die Station tatsächlich verbessert – und wenn ja, wo, wann und um wie viel?**

Im praktischen Funkbetrieb scheint sich diese Frage zunächst leicht beantworten zu lassen. Mit der neuen Antenne gelingen mehr QSOs, eine Gegenstation gibt einen besseren Rapport, ein WebSDR zeigt ein stärkeres Signal oder WSPR liefert mehr Spots. Solche Beobachtungen sind wertvoll, messen jedoch nicht die Antenne oder das geänderte Bauteil allein. Das beobachtete Ergebnis entsteht immer aus dem Zusammenwirken der vollständigen Station mit dem jeweiligen Funkweg: Antenne, Speiseleitung, Funkgerät, Sendeleistung, Empfänger, lokaler Rauschpegel, QRM, Gelände, Ionosphäre, Gegenstation und Zeitpunkt wirken gleichzeitig zusammen.

Genau darin liegt das grundlegende Messproblem. Zwei unterschiedliche Ergebnisse müssen nicht durch die getestete Hardware verursacht worden sein. Ein besserer Rapport kann auf einer günstigeren Ausbreitungsphase beruhen, ein zusätzliches QSO auf einer anderen Gegenstation und eine höhere Spotzahl auf veränderter Stationsaktivität oder besseren Bedingungen. Auch vollkommen korrekte Beobachtungen erlauben daher nicht automatisch eine eindeutige Aussage über die Ursache.

Erfahrene Funkamateure begegnen diesem Problem mit zunehmend kontrollierten Verfahren: wiederholten Vergleichen, Bakenaussendungen, WebSDRs, Auswertungen des Reverse Beacon Network (RBN) oder von WSPR und insbesondere einer schnellen A/B-Umschaltung im laufenden Betrieb. Ein solcher Live-A/B-Test ist wesentlich aussagekräftiger als zwei zeitlich getrennte QSOs. Sender, Sendeleistung, Frequenz, Gegenstation und ein großer Teil des Funkwegs bleiben dabei weitgehend gleich. Dass gemeinsame Bedingungen und möglichst kurze oder simultane Vergleiche belastbarer sind als lange getrennte Messblöcke, zeigen auch etablierte WSPR-Vergleichsversuche <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a> <a href="#ref-3">[Ref-3]</a> <a href="#ref-4">[Ref-4]</a> <a href="#ref-5">[Ref-5]</a>.

Dennoch bleibt auch ein sorgfältiger schneller A/B-Vergleich gewöhnlich eine nacheinander durchgeführte Messung auf einem einzelnen Funkweg und innerhalb eines kurzen Zeitfensters. QSB, Mehrwegeausbreitung, QRM und der lokale Rauschpegel können sich bereits während der Umschaltung verändern. AGC, S-Meter-Auflösung und subjektive Rapporte begrenzen zusätzlich die erkennbare Differenz. Ein beobachteter Vorteil kann real sein, gilt zunächst aber nur für diese Gegenstation, diese Richtung, diesen Zeitpunkt und diesen Ausbreitungszustand.

Die eigentliche Herausforderung besteht deshalb nicht darin, überhaupt einen Unterschied zu beobachten. Sie besteht darin, zu prüfen, **ob sich der Unterschied unter vielen vergleichbaren Bedingungen wiederholt, wie groß er typischerweise ist, auf welchen Funkwegen er auftritt und wie viel Evidenz ihn stützt.**

Genau hierfür bietet WSPR eine ungewöhnlich geeignete Grundlage. Seine wiederholten, zeitgestempelten und maschinell decodierten QRP-Aussendungen erzeugen in einem weltweiten Netz freiwillig betriebener Stationen Beobachtungen über viele Stationen, Entfernungen, Richtungen und Ausbreitungszustände <a href="#ref-6">[Ref-6]</a> <a href="#ref-7">[Ref-7]</a> <a href="#ref-8">[Ref-8]</a>. WSPRadar macht daraus kein kalibriertes Antennenmesslabor. Es ordnet die Beobachtungen jedoch zu einem kontrollierteren, semiquantitativen und nachvollziehbaren Stationsversuch: Vergleichbare Bedingungen werden zusammengeführt, Stationsaktivität wird geprüft, Unterschiede der gemeldeten Sendeleistung werden berücksichtigt, und das Ergebnis bleibt bis zu den beitragenden Stationen und Spots überprüfbar.

Je nach Band, Stationsaktivität und gewähltem Zeitfenster können dabei über Stunden oder Tage Hunderte bis Tausende Beobachtungen zusammenkommen. Diese Wiederholung über viele Funkwege und Ausbreitungszustände hilft, zufällige Einzelereignisse von wiederkehrenden Mustern zu unterscheiden und semiquantitative Aussagen über Größe, räumliche Verteilung und zeitliche Beständigkeit eines beobachteten Effekts abzuleiten. So entsteht keine kalibrierte Labormessung, wohl aber eine solide technisch-wissenschaftliche Evidenzbasis für die Bewertung der vollständigen Station unter realen Betriebsbedingungen.

So eingesetzt wird WSPR auch für die gesamte Amateurfunkgemeinschaft wertvoller. Korrekte Rufzeichen, Locator und Leistungsangaben, stabiler Betrieb und dokumentierte Änderungen machen aus gewöhnlichem WSPR-Bakenbetrieb Evidenz, die sich wiederverwenden lässt, statt lediglich auf der Karte betrachtet zu werden.

<a id="sec-1-0"></a>

#### 0.0 Was WSPRadar zeigen kann

WSPRadar wertet ein <strong class="defined-term">Target</strong> innerhalb eines klar definierten Versuchsdesigns aus. Das Target kann eine vollständig aufgebaute Station oder ein kontrollierter Signalweg sein. Es kann für sich allein oder gegenüber einer aussagekräftigen <strong class="defined-term">Referenz</strong> ausgewertet werden. Je nach Fragestellung kann die Referenz Setup B an derselben Station, eine bekannte externe Station, die aktive lokale WSPR-Nachbarschaft oder deren stärkstes aktives Mitglied sein.

Die Referenz ist Teil der wissenschaftlichen Fragestellung und nicht nur eine Darstellungsoption. Ein <strong class="defined-term">Hardware A/B-Test</strong> kann den Vergleich auf zwei lokale Antennen, Speiseleitungen, Empfänger oder vollständige Empfangsketten eingrenzen, wenn die übrigen Variablen stabil gehalten werden. Ein <strong class="defined-term">Referenzstations-/Buddy-Test</strong> vergleicht zwei vollständige Stationen einschließlich ihrer QTHs, Geräte, des Geländes sowie der lokalen Stör- und Rauschumgebungen. Ein lokaler Nachbarschafts-Benchmark fragt, wie das Target gegenüber einer wechselnden Population aktiver WSPR-Stationen in der Umgebung abschneidet. Ohne Benchmark fragt WSPRadar, wo das Target unter unabhängig bestätigten Opportunities <strong class="defined-term">qualifizierende Evidenz</strong> geliefert hat – also Evidenz, die nach Anwendung der Regeln des Laufs erhalten bleibt.

Diese Designs sind nicht austauschbar. Ein Buddy- oder Nachbarschaftsergebnis kann den Antennengewinn nicht isolieren, weil Stationsstandort, Hardware und Rauschen Teil des Vergleichs bleiben. Ein Hardware-A/B-Ergebnis grenzt die Ursache nur so weit ein, wie der Versuch den übrigen Signalweg tatsächlich kontrolliert. Keine nachträgliche Statistik kann eine Variable herausrechnen, die das Betriebsdesign nie kontrolliert hat.

Die Methode baut auf etablierten WSPR-Vergleichsansätzen auf: TX-Differenzen am selben Empfänger unter gemeinsamen Ausbreitungsbedingungen, simultane RX-Vergleiche unter kontrollierten Bedingungen, unabhängige Aktivitätsprüfungen bei unbekannten Betriebszeiten sowie die praktische Erkenntnis, dass langsames Umschalten durch veränderliche Ausbreitung verfälscht werden kann <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a> <a href="#ref-9">[Ref-9]</a> <a href="#ref-3">[Ref-3]</a>. WSPRadar integriert und erweitert diese Grundlage um die Qualifizierung der Target-Aktivität, zweckgebundene Benchmark-Designs, Zuordnung innerhalb desselben Zyklus oder nach deterministischem Zeitplan, Normierung auf die gemeldete Sendeleistung, getrennte Auswertungen für Success, Delta SNR und Decode Outcomes, stationsgleichgewichtete geografische Zusammenfassungen und den Drill-Down bis zur beitragenden Evidenz. Seine deskriptive <strong class="defined-term">Stability</strong>-Prüfung beschreibt die Empfindlichkeit eines angezeigten Medians gegenüber erneutem Ziehen aus der in einem Lauf verfügbaren Evidenz. [Kapitel 6](#sec-d) dokumentiert diese wissenschaftliche Entwicklungslinie, die Ergänzungen durch WSPRadar und ihre Grenzen.

Die angestrebte Schlussfolgerung ist daher klar begrenzt, aber für den Funkbetrieb nützlich: **Wie hat das Target auf diesem Band, in diesem UTC-Zeitfenster, innerhalb dieser Stationspopulation und unter diesem Versuchsdesign abgeschnitten? Gegenüber welcher Referenz zeigte sich wo und wann welcher Unterschied, und wie viel Evidenz stützt ihn?** WSPRadar kann einen beobachteten relativen Vorteil sowie dessen räumlichen oder zeitlichen Umfang zeigen. Es misst weder isolierten Gewinn in dBi noch Strahlungswirkungsgrad, Abstrahlwinkel oder Empfängerempfindlichkeit direkt; dafür sind separate kalibrierte Messungen erforderlich.

<a id="sec-1-1"></a>

#### 0.1 WSPR in zwei Minuten

<strong class="defined-term">WSPR</strong> steht für **Weak Signal Propagation Reporter**. Joe Taylor, K1JT, und Bruce Walker, W1BW, beschrieben WSPR als weltweites Netz von QRP-Stationen, die bakenartige Aussendungen austauschen, um mögliche Ausbreitungswege zu untersuchen. Eine WSPR-2-Aussendung dauert knapp zwei Minuten und belegt etwa 6 Hz. Die Nachricht enthält üblicherweise ein Rufzeichen, einen vierstelligen Maidenhead-Locator und die gemeldete Leistung in dBm; `30 dBm` entsprechen `1 W`. Decodes sind bis etwa `-28 dB` Signal-Rausch-Verhältnis (SNR) bezogen auf eine Referenzbandbreite von 2500 Hz möglich <a href="#ref-6">[Ref-6]</a> <a href="#ref-8">[Ref-8]</a>. Ein weniger negativer SNR-Wert bedeutet ein stärkeres Signal gegenüber dem Rauschen.

Ist das Reporting aktiviert, lädt ein Empfänger jeden erfolgreichen Decode als <strong class="defined-term">Spot</strong> hoch. Ein Spot enthält die Identität von Sender und Empfänger, den gemeldeten Standort, Zeit, Band, Leistung und den vom Decoder gemeldeten SNR. WSPRadar nutzt wspr.live als primäre WSPR-Datenquelle <a href="#ref-10">[Ref-10]</a>; WSPRDaemon WD2 und WD1 dienen als Ausweichquellen <a href="#ref-11">[Ref-11]</a>. wspr.live ist eine öffentliche ClickHouse-Datenbank, die von WSPRnet gemeldete Spots speichert und alle paar Minuten nach neuen Meldungen sucht. Eine tägliche Synchronisierung ergänzt Meldungen, die zunächst fehlten oder verspätet hochgeladen wurden.

Eine Einschränkung ist für jede Analyse entscheidend: Das Archiv enthält erfolgreiche Decodes, aber kein vollständiges Protokoll aller Sendeversuche. WSPRadar konstruiert deshalb eine <strong class="defined-term">Opportunity</strong>: einen zweiminütigen Zyklus mit nachweislich aktivem Target und unabhängiger Evidenz dafür, dass der betreffende entfernte Sender oder Empfänger aktiv war. Bei RX muss ein anderer Empfänger denselben Sender decodiert haben; bei TX muss der entfernte Empfänger ein anderes Signal auf demselben Band decodiert haben. Ohne diesen Aktivitätsnachweis wird ein fehlender Spot nicht automatisch als funktechnischer Misserfolg gewertet.

<a id="sec-1-2"></a>

#### 0.2 Die passende Fragestellung wählen

Beginne mit der betrieblichen Fragestellung, nicht mit einer Karte oder Kennzahl. Die Frage bestimmt Analyserichtung, Benchmark-Design und die Evidenz, die eine Antwort stützen kann:

| Deine Frage | Auswahl |
|---|---|
| Wo wird mein Sender von Empfängern decodiert, deren Aktivität unabhängig nachgewiesen ist? | TX-Analyse mit `Kein Benchmark (nur Success)` |
| Welche andernorts unabhängig bestätigten Signale decodiert auch mein Empfänger? | RX-Analyse mit `Kein Benchmark (nur Success)` |
| Unterscheidet sich der kontrollierte lokale Antennen-, Speiseleitungs- oder Hardwarepfad A von Pfad B? | Hardware A/B-Test |
| Wie schneidet meine vollständige Station gegenüber einer bekannten Station ab? | Referenzstations-/Buddy-Test |
| Ist meine Station im Großen und Ganzen typisch für nahegelegene aktive WSPR-Stationen? | Lokaler Nachbarschafts-Benchmark mit lokalem Nachbarschafts-Median |
| Wie schneide ich auf jedem Funkweg und in jedem Zyklus gegenüber dem stärksten aktiven lokalen Peer ab? | Lokaler Nachbarschafts-Benchmark mit bester lokaler Station |

Wähle die <strong class="defined-term">TX-Analyse</strong>, wenn das Target-Rufzeichen sendet. Die entfernten Empfangsstationen, die Evidenz liefern, werden als <strong class="defined-term">Peers</strong> auf der Karte dargestellt.

Wähle die <strong class="defined-term">RX-Analyse</strong>, wenn das Target-Rufzeichen empfängt. Die entfernten Sendestationen, die Evidenz liefern, werden als Peers auf der Karte dargestellt. Das konfigurierte <strong class="defined-term">QTH</strong> ist der Standort der Target-Station und dient als Kartenmittelpunkt sowie als Ausgangspunkt für den lokalen Radius.

Wähle das am engsten gefasste Design, das die beabsichtigte Aussage tatsächlich trägt. Eine Frage nach einer Hardwareursache erfordert einen kontrollierten Hardware A/B-Test. Ein Buddy- oder Nachbarschaftsergebnis bleibt Evidenz für die Gesamtstation, weil QTH, Geräte und Rauschen Teil des Vergleichs sind. Keine spätere Aggregation kann aus einem unkontrollierten Stationsvergleich isolierten Antennengewinn machen. [Kapitel 1](#sec-2) enthält den Versuchsleitfaden für jede Auswahl.

<a id="sec-1-3"></a>

#### 0.3 Was ein Lauf liefert

Jeder Lauf legt eine <strong class="defined-term">Analyserichtung</strong>, genau ein Band, eine Target-Identität und ein aufgelöstes UTC-Zeitfenster fest. Sein <strong class="defined-term">Benchmark-Design</strong> bestimmt die Ergebnisblöcke. Ein Lauf erzeugt ein Evidenzpaket für diese klar definierte Fragestellung und keine universelle Kennzahl für die Station.

* <strong class="defined-term">Success</strong> ist das nicht vergleichende Target-Ergebnis. Die bedingte Success Rate zeigt, wie oft das Target unter unabhängig bestätigten Opportunities qualifizierende Evidenz lieferte.
* <strong class="defined-term">Compare</strong> kommt hinzu, sobald ein Benchmark ausgewählt ist. Das Ergebnis enthält gepaartes **Delta SNR** und **Decode Outcomes**. Delta SNR ist das SNR der Target-Seite minus das SNR der Referenzseite nach einer gegebenenfalls konfigurierten Referenzkorrektur. Positive Werte sprechen für das Target, negative für die Referenz. Decode Outcomes weisen sowohl gepaarte Evidenz als auch Fälle aus, in denen nur eine Seite decodiert wurde.

Success, Delta SNR und Decode Outcomes beantworten unterschiedliche Fragen. WSPRadar hält sie getrennt, damit eine einzelne eingängige Zahl eine geringe Opportunity-Abdeckung, einseitige Decodes oder eine gepaarte Teilmenge, die nur einen Teil der Evidenz repräsentiert, nicht verdeckt.

Die Ergebnisse öffnen sich auf einer Karte und lassen sich entlang eines durchgängigen Evidenzpfads prüfen:

**Laufidentität -> Karte -> Stationen und Spots -> Segment-Inspektor -> Station Insights -> Drill-Down**

Die Karte lokalisiert das beobachtete Muster; sie ist der Ausgangspunkt der Analyse, nicht die Schlussfolgerung. Der Segment-Inspektor zeigt die Evidenz für eine gewählte Entfernung und Richtung. Station Insights zeigt, welche Identitäten beitragen. Drill-Down legt die Beobachtungen, Paare desselben Zyklus oder geplanten TX-A/B-Paare hinter den Zusammenfassungen offen.

Ein belastbares Ergebnis liegt vor, wenn Laufdefinition, Breite der Stationsbasis, Beobachtungsumfang, räumliches und zeitliches Muster, deskriptive Stability und die zugrunde liegenden Datenzeilen ein konsistentes Bild ergeben. Die Wiederholung desselben Designs in einem weiteren geeigneten Zeitfenster kann zeigen, ob dieses Bild Bestand hat.

Das Ziel ist eine klare betriebliche Aussage: **Was unterschied sich wo und wann gegenüber welcher Referenz, um wie viel und mit wie viel stützender Evidenz?**

<a id="documentation-toc"></a>

### Inhaltsverzeichnis

**Teil 0: Vorwort**

* [0. Warum WSPRadar?](#sec-1)
    * [0.0 Was WSPRadar zeigen kann](#sec-1-0)
    * [0.1 WSPR in zwei Minuten](#sec-1-1)
    * [0.2 Die passende Fragestellung wählen](#sec-1-2)
    * [0.3 Was ein Lauf liefert](#sec-1-3)

**Teil I: Leitfaden für den Funkbetrieb**

* [1. Versuchsleitfäden](#sec-2)
    * [1.1 Solide Grundlagen für jeden Versuch](#sec-2-1)
    * [1.2 Nur Success: die Target-Reichweite untersuchen](#sec-2-2)
    * [1.3 RX Hardware A/B: simultane Empfangspfade vergleichen](#sec-2-3)
    * [1.4 TX Hardware A/B: abwechselnde Sendepfade vergleichen](#sec-2-4)
    * [1.5 Referenzstations-/Buddy-Test](#sec-2-5)
    * [1.6 Lokaler Nachbarschafts-Median](#sec-2-6)
    * [1.7 Beste lokale Station](#sec-2-7)
* [2. Ergebnisse auswerten](#sec-3)
    * [2.1 Ein Success-Ergebnis auswerten](#sec-3-2)
    * [2.2 Ein Compare-Ergebnis auswerten](#sec-3-3)
    * [2.3 Das beobachtete Muster auf der Karte lokalisieren](#sec-3-4)
    * [2.4 Stationen und Spots prüfen](#sec-3-5)
    * [2.5a Ein geografisches Segment untersuchen (Success-Modus)](#sec-3-6a)
    * [2.5b Ein geografisches Segment untersuchen (Compare-Modus)](#sec-3-6b)
    * [2.6a Die beitragenden Stationen untersuchen (Success-Modus)](#sec-3-7a)
    * [2.6b Die beitragenden Stationen untersuchen (Compare-Modus)](#sec-3-7b)
    * [2.7 Die zugrunde liegende Evidenz prüfen](#sec-3-8)
    * [2.8 Durchgerechnetes Compare-Beispiel](#sec-3-9)
* [3. Ergebnisse absichern und kommunizieren](#sec-4)
    * [3.1 Breite, Stability und Wiederholbarkeit beurteilen](#sec-4-1)
    * [3.2 Ein Ergebnis durch Wiederholung und Kontrolle absichern](#sec-4-2)
    * [3.3 Eine evidenzgerechte Schlussfolgerung formulieren](#sec-4-3)
    * [3.4 Lauf und Kontext sichern](#sec-4-4)

**Teil II: Bedienelemente und Fehlersuche**

* [4. Bedienelemente und Konfiguration](#sec-5)
    * [4.1 Ablaufsteuerung](#sec-5-1)
    * [4.2 Kernparameter](#sec-5-2)
    * [4.3 Benchmark-Einstellungen](#sec-5-3)
    * [4.4 Filter und Evidenzschwellen](#sec-5-4)
    * [4.5 Karten-, Inspektor- und Exporteinstellungen](#sec-5-5)
* [5. Fehlersuche und Datenqualität](#sec-6)
    * [5.1 Zuerst die Laufdefinition prüfen](#sec-6-1)
    * [5.2 Fehler nach Symptom eingrenzen](#sec-6-2)
    * [5.3 Rufzeichen und Locator prüfen](#sec-6-3)
    * [5.4 Fallback für historische Decode-Codes](#sec-6-4)
    * [5.5 Wie das Target-Active Gate die Evidenz prägt](#sec-6-5)
    * [5.6 Umgang mit Upstream-Daten](#sec-6-6)

**Teil III: Wissenschaftliche Grundlagen, Methoden und Aussagen**

* [6. Literatur, Vorarbeiten und Einordnung](#sec-d)
    * [6.1 Vom Meldenetz zum Versuchsdatensatz](#sec-d-1)
    * [6.2 WSPR-Beobachtungsdaten interpretierbar machen](#sec-d-2)
    * [6.3 Wissenschaftliche Vorarbeiten zu Antennen- und Stationsvergleichen](#sec-d-3)
    * [6.4 Analyseinfrastruktur und Werkzeuge für Funkamateure](#sec-d-4)
    * [6.5 Was WSPRadar übernimmt, integriert und ergänzt](#sec-d-5)
* [7. Wissenschaftliche Methoden](#sec-7)
    * [7.1 Datenquelle, Decode-Auswahl und Zeitmodell](#sec-7-1)
    * [7.2 Identitäts- und Zuordnungsregeln](#sec-7-2)
    * [7.3 Target-Active Gate](#sec-7-3)
    * [7.4 Success-Klassifikation und Formeln](#sec-7-4)
    * [7.5 Leistungsnormierung, Korrektur und Delta SNR](#sec-7-5)
    * [7.6 Gepaarte Evidenz und Decode Outcomes](#sec-7-6)
    * [7.7 Aggregationshierarchie](#sec-7-7)
    * [7.8 Stabilität, Verteilungen und Gewichtung in der Inspektionsansicht](#sec-7-8)
    * [7.9 Geografie und Sonnenstandsklassifikation](#sec-7-9)
* [8. Evidenzgerechte Aussagen und Reproduzierbarkeit](#sec-8)
    * [8.1 Aussagen, die von der Evidenz gestützt werden](#sec-8-1)
    * [8.2 Interpretationsgrenzen: Was gekoppelt oder unbeobachtet bleibt](#sec-8-2)
    * [8.3 Checkliste für die Ergebnisdokumentation](#sec-8-3)
    * [8.4 Exportpaket der Analyse](#sec-8-4)
    * [8.5 Haftungsausschluss](#sec-8-5)
* [Literatur und Quellen](#sec-ref)

**Teil IV: Praktische Ergänzungen**

* [Anhang A: Parallele WSJT-X-Instanzen](#sec-a)
    * [A.1 Zweite Instanz anlegen](#sec-a-1)
    * [A.2 Ausgangskonfiguration bei Bedarf kopieren](#sec-a-2)
    * [A.3 Alle Datenpfade trennen](#sec-a-3)
* [Anhang B: Sequenzielle TX-A/B-Zeitplanung und Umschaltung](#sec-b)
    * [B.1 Anforderungen an einen gültigen zeitgesteuerten Versuch](#sec-b-1)
    * [B.2 Zeitgesteuerter WSPRadar-A/B-Relaisumschalter](#sec-b-2)
    * [B.3 Zeitplanbeispiel für Ultimate3S](#sec-b-3)
    * [B.4 Zeitplanbeispiele für QMX](#sec-b-4)
    * [B.5 Zuordnung prüfen und Versuch dokumentieren](#sec-b-5)
* [Anhang C: Referenz-SNR-Kalibrierung](#sec-c)
* [Lizenz](#sec-license)

---

<a id="part-i"></a>

## Teil I: Leitfaden für den Funkbetrieb

Dieser Teil führt von der betrieblichen Fragestellung zu einem gut belegten Ergebnis. Nutze Kapitel 1, um den Versuch auszuwählen und durchzuführen, Kapitel 2 zur Prüfung der Evidenz und Kapitel 3, um die Schlussfolgerung abzusichern, zu dokumentieren und zu bewahren. Die genauen Bedienelemente, Verarbeitungsmethoden und Angaben zur Reproduzierbarkeit sind in den Teilen II und III zusammengefasst.

In diesem Handbuch bezeichnet der **Versuch** den tatsächlichen Funkbetrieb und die physische Stationskonfiguration. Ein **Lauf** oder eine **Analyse** ist die in WSPRadar konfigurierte Verarbeitung der daraus entstandenen Beobachtungen. Ein **Ergebnis** ist die Success- oder Compare-Evidenz, die dieser Lauf erzeugt.

---

<a id="sec-2"></a>

### 1. Versuchsleitfäden

Wähle den Leitfaden, der zu deiner Frage aus [Abschnitt 0.2](#sec-1-2) passt. Jeder Leitfaden beschreibt den minimal erforderlichen Versuchsaufbau, das daraus entstehende Ergebnis und die wichtigste Interpretationsgrenze des Designs. Die exakten Bedienelemente stehen in Teil II; Zuordnung, Normierung und Aggregation werden einmal in den [Wissenschaftlichen Methoden](#sec-7) definiert.

<a id="sec-2-1"></a>

#### 1.1 Solide Grundlagen für jeden Versuch

Eine klare Fragestellung und ein stabiler physischer Aufbau erleichtern die Interpretation des Ergebnisses.

**Versuch und Lauf definieren**

* Formuliere die Fragestellung und die zu untersuchende Variable in einem Satz.
* Lege fest, ob es sich um einen explorativen Lauf oder um die bestätigende Wiederholung eines zuvor beobachteten Musters handelt.
* Wähle TX- oder RX-Analyse, genau ein Band und das Benchmark-Design.
* Gib Rufzeichen exakt so ein, wie sie hochgeladen wurden, einschließlich eines gültigen Suffixes wie `/P`, `/1` oder `/QRP`.
* Prüfe das Target-QTH. Success identifiziert das Target anhand des exakten Rufzeichens in Verbindung mit den ersten vier Zeichen des Locators.
* Wähle ein UTC-Zeitfenster, in dem das Target tatsächlich in Betrieb war. Das Fenster muss lang genug sein, um die Ausbreitungszustände abzudecken, auf die sich die beabsichtigte Aussage bezieht; für Aussagen über vollständige Tageszyklen sind mehrtägige Läufe vorzuziehen.
* Protokolliere Antennen, Speiseleitungen, Tuner, Sender oder Empfänger, Decoder, Softwareversion, Leistung, Zeitplan und beabsichtigte Änderungen.

Jeder Lauf verwendet genau ein Band. Eine Zusammenfassung mehrerer Bänder würde unterschiedliche Ausbreitung, Aktivität, Stationspopulationen und Beobachtbarkeit vermischen.

**Den physischen Versuchsaufbau stabil halten**

* Halte alle nicht untersuchten Variablen so stabil wie praktisch möglich.
* Synchronisiere die Stationsuhren.
* Halte bei TX die tatsächliche und die gemeldete Leistung synchron und stabil, sofern nicht die Leistung selbst untersucht wird. WSPR wird üblicherweise mit kleiner Leistung betrieben; `20-30 dBm` entsprechen etwa `0.1-1 W`.
* Halte bei RX Verstärkung, Filterung, Audioführung, Decoder-Einstellungen und Upload-Verhalten stabil, sofern nicht einer dieser Punkte untersucht wird.
* Prüfe, ob beide Seiten des Benchmarks wie vorgesehen in Betrieb sind. Das <strong class="defined-term">Target-Active Gate</strong> verhindert, dass Zeiträume ohne beobachtbare Target-Aktivität als Misserfolg gewertet werden, weist aber keine Betriebsbereitschaft der Referenz nach.

Nutze bei einem explorativen Lauf die Evidenzkette aus [Kapitel 2](#sec-3), um ein mögliches Muster zu erkennen. Lege vor einer bestätigenden Wiederholung den primären geografischen und zeitlichen Auswertungsbereich fest und halte Richtung, Band, Benchmark, Filter, Schwellen und Zeitplan konstant, sofern nicht gerade deren Änderung Teil des erklärten Versuchs ist.

<a id="sec-2-2"></a>

#### 1.2 Nur Success: die Target-Reichweite untersuchen

**Beantwortete Frage**

Wo, wann und wie regelmäßig liefert das Target qualifizierende Evidenz bei entfernten Stationen oder Signalen, deren Aktivität unabhängig nachgewiesen wurde, und welcher SNR wird für erfolgreiche Target-Decodes beobachtet?

**Was WSPRadar zeigt**

Für diesen Leitfaden bezeichnet <strong class="defined-term">qualifizierende Evidenz</strong> die Target- und unabhängige Aktivitätsevidenz, die nach Anwendung der Identitäts-, Band-, Zeit-, Target-Aktivitäts-, Filter- und Schwellenregeln des Laufs erhalten bleibt.

* **RX Success** vergleicht die Decodes des Target-Empfängers mit unabhängig bestätigten Zyklen entfernter Sender.
* **TX Success** vergleicht die Decodes des Target-Senders mit Zyklen entfernter Empfänger, in denen andere Aktivitäten auf demselben Band nachgewiesen wurden.

Es gibt weder eine Referenzstation noch ein Setup B. Die Success Rate beschreibt bedingte Erreichbarkeit; der SNR erfolgreicher Target-Decodes ist eine getrennte Signalstärkezusammenfassung. [Abschnitt 2.1](#sec-3-2) erläutert die sichtbaren Klassifikationen und Gewichtungen, [Abschnitt 7.4](#sec-7-4) definiert den exakten Nenner.

**Die Analyse einrichten**

Wähle `RX-Analyse` oder `TX-Analyse`, gib das exakte Target-Rufzeichen und QTH ein, wähle ein Band und ein aktives UTC-Zeitfenster und anschließend `Kein Benchmark (nur Success)`.

**Die Evidenz stärken**

Verwende ein Betriebsfenster mit beobachtbarer Target-Aktivität und genügend unabhängiger WSPR-Aktivität. Prüfe geografischen Umfang, Stationen, Spots und Zeitansichten. Wenn nur wenige Peers übrig bleiben, verlängere das Beobachtungsfenster oder begrenze den geografischen beziehungsweise zeitlichen Umfang der Schlussfolgerung. Verändere Filter oder Schwellen nur aus einem klar genannten Versuchsgrund und dokumentiere die geänderte Konfiguration als separaten Lauf.

**Evidenzgerechte Schlussfolgerung**

> Für dieses Target, Band, UTC-Zeitfenster und die ausgewählte Peer-Population fasst die angezeigte Success Rate den Anteil der unabhängig bestätigten Opportunities im weltweiten WSPR-Netz zusammen, in denen auch das Target qualifizierende Evidenz lieferte. Die Rate wird zunächst je Peer berechnet und anschließend gleichgewichtet über alle qualifizierenden Peers gemittelt.

In der Stationspraxis bedeutet das: Von den weltweiten WSPR-Aktivitäten, die dieser Lauf unabhängig bestätigen und damit belastbar prüfen konnte, zeigt das Ergebnis, wie regelmäßig deine Station ebenfalls die erwartete TX- oder RX-Evidenz lieferte. Die SNR-Ansicht der erfolgreichen Decodes zeigt davon getrennt die Signalstärken der tatsächlich decodierten Target-Evidenz.

<a id="sec-2-3"></a>

#### 1.3 RX Hardware A/B: simultane Empfangspfade vergleichen

**Beantwortete Frage**

Unterschieden sich zwei lokale Empfangspfade bei der Beobachtung derselben entfernten WSPR-Aussendungen?

Für Funkamateure kann das bedeuten: zwei Antennen zu vergleichen, die jeweils eine eigene, unabhängig meldende Empfänger-/Decoderkette speisen; zwei Empfänger über einen charakterisierten Verteiler aus derselben Antenne zu versorgen; Vorverstärker, Filter oder Speiseleitungen zu vergleichen; oder zwei vollständige parallele Empfangsketten gegeneinander zu testen.

**Was WSPRadar zeigt**

Beim simultanen RX Hardware A/B-Test werden zwei lokale Empfangspfade an derselben Station verglichen. Setup A und Setup B beobachten dieselben entfernten Senderidentitäten in denselben WSPR-Zyklen. Dieses Design kommt in WSPRadar einem kontrollierten Hardwarevergleich mit demselben Signal am nächsten.

Solange Unterschiede zwischen Empfänger, Audiopfad und Decoder nicht charakterisiert wurden, vergleicht das Ergebnis die vollständigen Empfangspfade und nicht die Antennen allein.

**Den Versuch einrichten**

Wähle in der Benutzeroberfläche `Hardware A/B-Test (Eigenes Setup)` und betreibe zwei Empfänger gleichzeitig mit unterschiedlichen exakten Melderufzeichen:

* Setup A verwendet das Target-Rufzeichen.
* Setup B verwendet das `Setup B Callsign`.

Halte Uhren, Antennenführung, Verstärkung, Audiopfade, Decoder-Einstellungen und Uploads unter Kontrolle. Komponenten, die gemeinsam sein sollen, müssen physisch gemeinsam genutzt werden; unvermeidliche Unterschiede zwischen den beiden Ketten sind zu messen oder zu dokumentieren.

Der Lauf erzeugt ein RX-Hardware-Compare-Ergebnis sowie ein separates RX-Success-Ergebnis für das Target.

**Die Evidenz stärken**

Dokumentiere die Pegelgleichheit der Verteilerausgänge, Unterschiede der Speiseleitungen, Empfängerverstärkung, Verhalten der automatischen Verstärkungsregelung (AGC), Übersteuerung, Decoder-Konfiguration und Upload-Verhalten. Eine gemessene Referenz-SNR-Korrektur kann einen stabilen Offset ausgleichen, jedoch kein nichtlineares oder zeitabhängiges Verhalten.

[Anhang A](#sec-a) beschreibt parallele WSJT-X-Instanzen. [Anhang C](#sec-c) erläutert die Referenz-SNR-Kalibrierung.

**Evidenzgerechte Schlussfolgerung**

> Unter dem dokumentierten simultanen RX-Aufbau zeigte das gepaarte Delta SNR den beobachteten Unterschied zwischen den Empfangspfaden A und B für die gemeinsamen Sender, Zyklen und den untersuchten geografischen Bereich.

In der Stationspraxis bedeutet das: Für entfernte Signale, die beide Pfade gleichzeitig beobachteten, zeigt das Ergebnis, welcher Empfangspfad tendenziell stärkere Decodes lieferte, wo der Unterschied auftrat und wie viel gemeinsame Evidenz ihn stützte.

<a id="sec-2-4"></a>

#### 1.4 TX Hardware A/B: abwechselnde Sendepfade vergleichen

**Beantwortete Frage**

Unterschieden sich zwei lokale Antennen, Speiseleitungen oder geschaltete HF-Pfade, wenn sie von derselben Stationsausrüstung gespeist wurden?

<a id="sec-2-4-why"></a>

**Warum deterministisches Abwechseln verwendet wird**

Senden zwei nahe beieinanderstehende Antennen im selben WSPR-Zyklus und Frequenzkanal dieselbe WSPR-Aussendung mit demselben Rufzeichen, empfängt eine entfernte Station die Überlagerung beider Felder. Ihr Spot lässt nicht erkennen, welcher Anteil von Antenne A oder B stammt. Unterscheidbare simultane Signale erfordern normalerweise getrennte Rufzeichen und Sendeketten; dadurch kommen zusätzliche Unterschiede bei Leistung, Kalibrierung, Zeit und Frequenz hinzu.

Ein deterministischer Wechsel behält dagegen ein Rufzeichen und vorzugsweise eine gemeinsame Sendekette bei, während beide Pfade wiederholt wechselnden Ausbreitungs- und Empfangsbedingungen ausgesetzt werden. Der Vergleich bleibt sequenziell: Ein kürzerer Abstand verringert die Zeit, in der sich die Bedingungen ändern können, macht die Beobachtungen aber nicht simultan.

**Was WSPRadar zeigt**

Beim sequenziellen TX Hardware A/B-Test werden vollständige WSPR-Aussendungen anhand eines zeitlich festgelegten Sendeplans Setup A und Setup B zugeordnet. WSPRadar bildet anschließend für jede entfernte Empfängeridentität deterministische Eins-zu-eins-Paare und meldet das Delta SNR der geplanten Paare sowie einseitige Decode Outcomes.

**Den Versuch einrichten**

Verwende für beide Pfade das reguläre, gültige Rufzeichen der Station. Die Pfadidentität ergibt sich aus dem deterministischen UTC-Zeitplan, nicht aus Suffixen wie `/1` und `/2` oder unterschiedlichen gemeldeten Leistungen.

Trage im `TX-A/B-Zeitplan` für jeden physischen Pfad seine **tatsächliche Wiederholung und UTC-Phase** ein. Leite diese Werte nicht allein aus der `Frame`-Bezeichnung eines Senders ab. Verwende einen deterministischen Zeitgeber oder Controller; der zufällige Sendebetrieb über die prozentuale TX-Einstellung von WSJT-X erzeugt keine gültige feste A/B-Folge. Die exakten Bedienelemente und zulässigen Phasen stehen in [Abschnitt 4.3](#sec-5-3), gerätespezifische Zeitpläne und Umschaltverfahren in [Anhang B](#sec-b). <a href="#ref-12">[Ref-12]</a>

WSPRadar bildet die geplanten Paare automatisch. Die exakte Paarzuordnung, die Behandlung der Zeitfenstergrenzen und die Aggregation zu Mikro-Medianen sind in den [Abschnitten 7.1](#sec-7-1) und [7.7](#sec-7-7) definiert.

Melde die tatsächliche Sendeleistung. Kennzeichne die Pfade nicht durch falsche Leistungsangaben: Die TX-Normierung würde aus einer erfundenen Leistungsdifferenz einen künstlichen Vergleichsoffset erzeugen. [Abschnitt 7.5](#sec-7-5) definiert die Berechnung, [Anhang C](#sec-c) beschreibt eine belastbare Kalibrierung der Referenzseite.

Prüfe die physische Zuordnung von Zeitplan und Pfad vor dem Start ohne HF. Eine vertauschte Zuordnung beschriftet die Pfade falsch und kehrt die praktische Interpretation des Delta-SNR-Vorzeichens um.

Der Lauf erzeugt ein sequenzielles TX-Hardware-Compare-Ergebnis und ein separates TX-Success-Ergebnis. Success ist auf den konfigurierten Target-Zeitplan begrenzt und beschreibt daher Setup A.

**Die Evidenz stärken**

Kontrolliere Schaltverluste, Unterschiede der Speiseleitungen, Antennenkopplung, Ganggenauigkeit der Uhr, Zuordnung des Zeitplans zu den Pfaden sowie den Schaltzeitpunkt. Verwende den kürzesten praktikablen Abstand und dehne den Lauf über die für die Fragestellung relevanten Ausbreitungszeiten aus.

In einem ausgewogenen Lauf können sich zufällige kurzfristige Schwankungen teilweise ausmitteln, weil beide Pfade wiederholt wechselnden Bedingungen ausgesetzt sind. Systematische Effekte des Zeitplans, des Umschalters oder der Position im Zyklus mitteln sich dagegen nicht zwangsläufig aus. Wenn ein kleiner Unterschied entscheidend ist, wiederhole den Versuch mit vertauschter A/B-Zeitplanzuordnung und vergleiche gleichartig konfigurierte Läufe, wie in [Abschnitt 3.2](#sec-4-2) beschrieben.

[Abschnitt 6.3](#sec-d-toledo) erläutert die experimentellen Vorarbeiten und warum kurze Wechsel langen Blöcken vorzuziehen sind <a href="#ref-3">[Ref-3]</a>.

**Evidenzgerechte Schlussfolgerung**

> Unter dem dokumentierten, zeitlich festgelegten Sendeplan zeigte das Delta SNR der geplanten Paare den beobachteten Unterschied zwischen den geschalteten Pfaden A und B für die ausgewählten Empfänger, Zeiträume und den untersuchten geografischen Bereich.

In der Stationspraxis bedeutet das: Nach wiederholtem Wechsel der beiden HF-Pfade zeigt das Ergebnis, ob Pfad A oder B für die im Lauf vertretenen Empfänger und Ausbreitungszeiten tendenziell stärkere Meldungen erzeugte; der Vergleich bleibt dabei sequenziell und nicht simultan.

<a id="sec-2-5"></a>

#### 1.5 Referenzstations-/Buddy-Test

**Beantwortete Frage**

Wie schnitt die Target-Station während zeitgleichen Betriebs gegenüber einer bekannten externen Station ab?

**Was WSPRadar zeigt**

Ein Buddy-Test vergleicht zwei vollständig aufgebaute Stationssysteme. Der Vergleich umfasst ihre Standorte, Antennen, Speiseleitungen, Sender oder Empfänger, das lokale Rauschen, Gelände, Software und Betriebsumfeld.

* Bei TX werden Target und Referenz an demselben entfernten Empfänger verglichen, wenn beide im selben Zyklus decodiert wurden.
* Bei RX werden Target- und Referenzempfänger anhand derselben entfernten Senderidentität im selben Zyklus verglichen.

TX-Paare desselben Zyklus teilen damit einen entfernten Empfänger, RX-Paare einen entfernten Sender. Dadurch wird ein Endpunkt des Vergleichs kontrolliert; Unterschiede bei QTH, Funkweg, Stationshardware, Gelände und lokalem Rauschen bleiben bestehen.

**Die Analyse einrichten**

Wähle `Fremdes Rufzeichen (Buddy-Test)`. Gib ein exaktes Target-Rufzeichen und ein davon verschiedenes exaktes `Referenz-Rufzeichen` ein. Wähle als Referenz eine Station, deren Standort, Hardware, gemeldete Leistung und Betriebsplan du kennst.

Beide Stationen müssen zeitgleich auf demselben Band in Betrieb sein. Prüfe die Betriebsbereitschaft der Referenz unabhängig. Verwende eine Referenz-SNR-Korrektur nur, wenn sie auf einer belastbaren Kalibrierung beruht.

Der Lauf erzeugt ein TX- oder RX-Compare-Ergebnis gegenüber dem Buddy und ein separates nicht vergleichendes Target-Success-Ergebnis.

**Die Evidenz stärken**

Dokumentiere für beide Stationen Gelände, lokales Rauschen, Antennen, Polarisation, Speiseleitungsverlust, Sender- oder Empfängerkalibrierung, gemeldete Leistung und Betriebspläne. Prüfe die Locator-Identität und sammle genügend gemeinsame entfernte Peers.

Das Target-Active Gate ist asymmetrisch. Ein Tausch von Target und Referenz kann deshalb einseitige Decode Outcomes verändern, selbst wenn sich das Vorzeichen des gemeinsamen gepaarten Delta SNR erwartungsgemäß umkehrt.

Eine bekannte Referenzstation ist ein sinnvoller Vergleichspartner, aber nicht automatisch ein kalibrierter Referenzstandard.

**Evidenzgerechte Schlussfolgerung**

> Für die gemeinsamen Pfade und Zyklen dieses Laufs zeigten gepaartes Delta SNR und Decode Outcomes, wie sich die beiden vollständig aufgebauten Stationen unter ihren jeweiligen Betriebsbedingungen verglichen.

In der Stationspraxis bedeutet das: Das Ergebnis zeigt, wie deine vollständige Funkstation auf gemeinsamen Pfaden gegenüber der vollständigen Station deines Buddys abschnitt; es ordnet den beobachteten Unterschied nicht von selbst einer einzelnen Antenne, einem Empfänger oder einem Standort zu.

<a id="sec-2-6"></a>

#### 1.6 Lokaler Nachbarschafts-Median

**Beantwortete Frage**

Wie schneidet das Target gegenüber der typischen aktiven WSPR-Evidenz von Stationen in der Umgebung seines konfigurierten QTHs ab?

**Was WSPRadar zeigt**

Der lokale Nachbarschafts-Median bildet aus aktiven Stationsidentitäten innerhalb des ausgewählten Radius eine dynamische Referenz. Für jeden qualifizierenden Zyklus und Pfad repräsentiert der Nachbarschafts-Median die aktive lokale Gruppe, ohne dass eine Identität mit besonders vielen Beobachtungen dominiert.

Die Referenz kann sich von Zyklus zu Zyklus ändern. Sie ist ein lokaler Aktivitätsbenchmark und keine einzelne feste oder kalibrierte Station.

**Die Analyse einrichten**
Wähle `Lokaler Nachbarschafts-Benchmark`, einen Radius von 10 bis 250 km und unter `Lokale Benchmark-Methode` die Option `Lokaler Nachbarschafts-Median`.

Prüfe Target-Rufzeichen und QTH, weil sie den Ausschluss des Targets aus dem lokalen Pool und den Ursprung des Radius bestimmen. Wähle den primären Radius vor der Interpretation anhand der lokalen Geografie und der zu erwartenden Stationsdichte. Er sollte eine klare lokale Bedeutung besitzen und genügend aktive Identitäten enthalten.

Der Lauf erzeugt ein lokales Compare-Ergebnis und ein separates nicht vergleichendes Success-Ergebnis für das Target.

**Die Evidenz stärken**

Prüfe, welche lokalen Identitäten beitragen und wie viele Evidenzeinheiten sie liefern. Weitere wissenschaftlich begründbare Radien können als Sensitivitätsanalyse dokumentiert werden: Ein kleinerer Radius kann eine ähnlichere lokale Umgebung beschreiben, aber einen fragilen Pool hinterlassen; ein größerer Radius kann mehr Beitragende liefern, dabei jedoch unterschiedliches Gelände, Rauschen und Stationsbedingungen vermischen. Bewahre nicht nur den Radius auf, der das günstigste Ergebnis erzeugt.

Lokale Stationen können sich in Antenne, Hardware, Betriebsplan und Genauigkeit der gemeldeten Leistung unterscheiden. Gib den primären Radius, die Methode, die Beitragenden, Evidenzanzahlen und alle Sensitivitätsläufe zusammen mit dem Ergebnis an.

**Evidenzgerechte Schlussfolgerung**

> Gegenüber dem aktiven Nachbarschafts-Median innerhalb des ausgewählten Radius zeigte das Target für die beobachteten Pfade und Zyklen das angezeigte gepaarte Delta SNR und die angezeigten Decode Outcomes.

In der Stationspraxis bedeutet das: Das Ergebnis zeigt, ob deine Station für die Pfade und Zeiträume, in denen beide Seiten vergleichbar waren, tendenziell oberhalb, nahe oder unterhalb der typischen aktiven WSPR-Gruppe in der Umgebung lag.

<a id="sec-2-7"></a>

#### 1.7 Beste lokale Station

**Beantwortete Frage**

Wie schneidet das Target gegenüber der stärksten aktiven lokalen Referenz ab, die für jeden qualifizierenden Pfad und Zyklus verfügbar ist?

**Was WSPRadar zeigt**

Die Methode „Beste lokale Station“ bildet aus aktiven Stationsidentitäten innerhalb des gewählten Radius eine wechselnde Hüllkurve des jeweils stärksten Peers. Sie ist bewusst strenger als der Nachbarschafts-Median und stellt keinen lokalen Durchschnitt dar.

**Die Analyse einrichten**

Wähle `Lokaler Nachbarschafts-Benchmark`, einen Radius von 10 bis 250 km und unter `Lokale Benchmark-Methode` die Option `Beste lokale Station`.

Prüfe Target-Rufzeichen und QTH. Wähle den primären Radius vor der Interpretation anhand der lokalen Geografie und der zu erwartenden Stationsdichte; er muss einen aussagekräftigen und ausreichend besetzten lokalen Pool erhalten.

Der Lauf erzeugt ein lokales Compare-Ergebnis und ein separates nicht vergleichendes Success-Ergebnis für das Target.

**Die Evidenz stärken**

Prüfe die wechselnden lokalen Referenzstationen. Weitere wissenschaftlich begründbare Radien können als Sensitivitätsanalyse dokumentiert werden, wenn die Schlussfolgerung stark von der Zusammensetzung des Pools abhängt; bewahre nicht nur den Radius mit dem günstigsten Vergleich auf.

Die lokalen Beitragenden können sich in Gelände, Ausstattung, Rauschen, Betriebsplan und Genauigkeit der gemeldeten Leistung unterscheiden. Beschreibe die wechselnde Definition des stärksten Peers, statt das Ergebnis als Vergleich mit einer einzelnen festen Station darzustellen.

**Evidenzgerechte Schlussfolgerung**

> Gegenüber der jeweils stärksten aktiven lokalen Referenz, die innerhalb des angegebenen Radius für jeden qualifizierenden Pfad und Zyklus ausgewählt wurde, zeigte das Target das angezeigte gepaarte Delta SNR und die angezeigten Decode Outcomes.

In der Stationspraxis bedeutet das: Das Ergebnis zeigt, wie deine Station gegenüber der stärksten qualifizierenden Station in der Nähe abschnitt, die auf dem jeweiligen Pfad und in dem jeweiligen Zyklus verfügbar war – nicht gegenüber einer dauerhaft festgelegten Vergleichsstation.

Die genauen Regeln für die Zusammensetzung und Aggregation des lokalen Pools stehen in den [Abschnitten 7.2](#sec-7-2) und [7.7](#sec-7-7).

<a id="sec-3"></a>

### 2. Ergebnisse auswerten

Prüfe jeden Lauf entlang derselben Evidenzkette:

**Karte -> Stationen und Spots -> Segment-Inspektor -> Station Insights -> Drill-Down**

* Bestätige das Ergebnis und die Laufdefinition.
* Lokalisiere das beobachtete Muster auf der Karte.
* Wähle im Segment-Inspektor die relevante Entfernung und Richtung für die weitere Untersuchung.
* Prüfe die Evidenz auf Stationsebene in Station Insights.
* Gehe im Drill-Down bis zur Evidenz auf Beobachtungsebene.

Die genauen Formeln, Zuordnungsregeln und die Verarbeitungshierarchie stehen in den [Wissenschaftlichen Methoden](#sec-7).

<a id="sec-3-1"></a>

<a id="sec-3-2"></a>

#### 2.1 Ein Success-Ergebnis auswerten

Success ist das nicht vergleichende Target-Ergebnis. Verstehe die Success Rate als <strong class="defined-term">bedingte Erreichbarkeit</strong> unter unabhängig bestätigten Opportunities:

* **RX Success:** Wie viele der Zyklen entfernter Sender, die ein anderer Empfänger unabhängig bestätigte, decodierte auch der Target-Empfänger?
* **TX Success:** Wie viele der aktiven Zyklen entfernter Empfänger, die durch andere Decodes auf demselben Band bestätigt wurden, enthielten auch einen Decode des Target-Senders?

WSPRadar verwendet vier sichtbare Klassifikationen:

* <strong class="defined-term">Target:</strong> Das Target war erfolgreich, und die erforderliche unabhängige Bestätigung liegt ebenfalls vor.
* <strong class="defined-term">Elsewhere:</strong> Bei RX decodierte ein anderer Empfänger den Sender, das Target jedoch nicht.
* <strong class="defined-term">Other Signals:</strong> Bei TX decodierte der Empfänger andere Signale auf demselben Band, aber nicht das Target.
* <strong class="defined-term">Target-only:</strong> Das Target wurde ohne die für den Nenner erforderliche unabhängige Bestätigung decodiert. Diese Evidenz bleibt für Prüfzwecke verfügbar, geht aber nicht in die Success Rate ein.

Wurde beispielsweise ein entfernter Sender in acht qualifizierenden Zyklen unabhängig bestätigt und in drei davon auch vom Target-Empfänger decodiert, beträgt die RX Success Rate dieses Peers `3 von 8 = 37,5 %`. Erzeugte ein aktiver Empfänger zehn qualifizierende Zyklen und decodierte den Target-Sender in vier davon, beträgt seine TX Success Rate `4 von 10 = 40 %`.

Die Kandidatenpopulation wird weltweit gebildet:

* Bei RX kann sie bis zu allen weltweit aktiven Sendern auf dem Band in den Zyklen anwachsen, in denen der Target-Empfänger aktiv war.
* Bei TX kann sie bis zu allen weltweit aktiven Empfängern auf dem Band während der Target-Sendezyklen anwachsen.

Es tragen nur Peers bei, die das gewählte Zeitfenster, Band, die Filter und Evidenzschwellen erfüllen. Der angezeigte Kartenbereich kann einen geografischen Ausschnitt darstellen.

Zunächst wird die Rate jedes Peers berechnet. In einem Success-Kartensegment erhält anschließend jede qualifizierende Peer-Identität genau eine gleich große Stimme; angezeigt wird das arithmetische Mittel dieser Stationsraten. Das ist der <strong class="defined-term">stationsgleichgewichtete</strong> Wert. Der Segment-Inspektor zeigt zusätzlich die gepoolte Rate auf <strong class="defined-term">Beobachtungsebene</strong>, bei der jede qualifizierende Beobachtung gleich gewichtet wird.

Die Success Rate wird nicht auf die Sendeleistung normiert. Der daneben angezeigte SNR erfolgreicher Target-Decodes wird dagegen auf die gemeldete Leistung von 1 W normiert.

Angezeigte `100%` bedeuten, dass das Target bei jeder qualifizierenden Opportunity der Station oder des ausgewählten Bereichs erfolgreich war. Sie bedeuten nicht, dass jede mögliche oder geplante Aussendung decodiert wurde. Da Success eine anspruchsvolle, weltweit gebildete Opportunity-Population misst, ergibt sich die praktische Aussage aus Geografie, Stationen, Spots, Zeitverlauf und Wiederholung – nicht allein aus der Nähe zu `100%`.

<a id="sec-3-3"></a>

#### 2.2 Ein Compare-Ergebnis auswerten

Compare hält zwei Evidenzfragen getrennt.

**Delta SNR**

Delta SNR beantwortet die Frage: Wenn Target und Referenz beide vergleichbare Evidenz lieferten, welche Seite hatte den stärkeren SNR und um wie viel?

Aus Anwendersicht ist Delta SNR das SNR der Target-Seite minus das korrigierte SNR der Referenzseite. Die genaue Gleichung und die Vorzeichenkonvention der Korrektur stehen in [Abschnitt 7.5](#sec-7-5). Positive Werte sprechen für das Target, negative für die Referenz.

Das gepaarte Delta SNR ist normalerweise der wichtigste quantitative Vergleich, weil für beide Seiten die am besten vergleichbaren verfügbaren Bedingungen gelten:

* Beim simultanen RX Compare messen Target- und Referenzempfänger denselben entfernten Sender. Dadurch werden Unterschiede bei Sendeleistung, Signalform und gemeinsamem Pfad innerhalb des Paars verringert.
* Bei TX Compare im selben Zyklus, beispielsweise bei passenden Buddy- oder lokalen Nachbarschaftsvergleichen, misst derselbe entfernte Empfänger Target und Referenz. Dadurch werden Unterschiede bei Empfängerhardware, Empfangsantenne, lokalem Rauschen und Reporting innerhalb des Paars verringert.
* Sequenzielles TX Hardware A/B verwendet deterministisch geplante Paare statt Evidenz aus demselben Zyklus.

**Decode Outcomes**

Decode Outcomes zeigen gemeinsame und einseitige Evidenz innerhalb und außerhalb der gepaarten Teilmenge:

* <strong class="defined-term">Joint / Joint Spots / Joint Pairs:</strong> Es liegt qualifizierende gepaarte Evidenz vor.
* <strong class="defined-term">Only Target:</strong> In der jeweiligen Vergleichseinheit liegt Target-Evidenz ohne Referenz-Evidenz vor.
* <strong class="defined-term">Only Reference:</strong> Es liegt Referenz-Evidenz ohne Target-Evidenz vor.
* <strong class="defined-term">Both (Async):</strong> Für die Peer-Identität liegt Evidenz beider Seiten vor, aber in dieser Kategorie bleibt keine qualifizierende Joint-Einheit erhalten.

Beschreibe mit Delta SNR den gepaarten Signalstärkeunterschied und mit Decode Outcomes die gemeinsame und einseitige Decode-Evidenz. Ein Ergebnis kann einen klaren gepaarten Median und zugleich umfangreiche einseitige Evidenz enthalten; beides gehört in die Schlussfolgerung.

Decode Outcomes rekonstruieren kein SNR der fehlenden Seite und normieren es auch nicht auf die Sendeleistung. Interpretiere einseitige Outcomes bei TX deshalb zusammen mit der tatsächlichen und gemeldeten Sendeleistung. [Abschnitt 7.6](#sec-7-6) definiert diese Grenze.

Die Paarbildung im selben Zyklus reduziert gemeinsame Störgrößen, macht räumlich getrennte Stationen oder verschiedene Hardwareketten aber nicht physikalisch identisch. Bei Vergleichen im selben Zyklus verhindert das Target-Active Gate, dass Ausfallzeiten des Targets als Misserfolg gezählt werden; die Betriebsbereitschaft der Referenz muss weiterhin unabhängig bestätigt werden.

<a id="sec-3-4"></a>

#### 2.3 Das beobachtete Muster auf der Karte lokalisieren

Die Karte liefert den geografischen Überblick. Nutze Farben, Kategorien und Marker, um Entfernung und Richtung für die nächste Untersuchung auszuwählen.

**Kartenzusammenfassung**

Der <strong class="defined-term">Median</strong> ist nach dem Sortieren der mittlere Wert beziehungsweise bei gerader Anzahl der Mittelwert der beiden mittleren Werte. Ein einzelner ungewöhnlich hoher oder niedriger Wert verschiebt ihn weniger stark als das arithmetische Mittel.

* Compare-Segmente zeigen den Median der qualifizierenden Stationsmediane des Delta SNR. Positive Werte sprechen für das Target, negative für die Referenz.
* Success-Segmente zeigen das arithmetische Mittel der qualifizierenden Success Rates, nachdem jeder qualifizierende Peer genau eine gleich große Stimme erhalten hat.

Die Compare-Skala verwendet die im Amateurfunk übliche Anzeigekonvention `1 S-Stufe = 6 dB`. Das ist eine Skalenangabe und keine Behauptung, jedes S-Meter sei kalibriert.

**Stationskategorien**

Lies neben der Farbe immer auch die Kategorie:

* Success: Target-Evidenz wird mit grünen `T`-Markern dargestellt. Qualifizierende Peers ohne Target-Evidenz erscheinen grau als `E` für Elsewhere oder `OS` für Other Signals.
* Compare: Joint ist grün, Both (Async) gelborange, Only Target violett und Only Reference weiß.

**Entfernungsringe**

Nahe Entfernungsringe können mit kurzen Sprungdistanzen oder NVIS-Ausbreitung (Near Vertical Incidence Skywave) vereinbar sein; weit entfernte Ringe können auf DX-Ausbreitung hindeuten. Die Ringe beschreiben die Pfaddistanz und sind keine unmittelbare Messung des Abstrahlwinkels.

Die Kartenfarbe lokalisiert das beobachtete Muster. Die folgenden Evidenzebenen zeigen, wie breit und gut es belegt ist.

<a id="sec-3-5"></a>

#### 2.4 Stationen und Spots prüfen

* <strong class="defined-term">STATIONS</strong> beschreibt die Breite der Abdeckung über unterschiedliche qualifizierende Identitäten `callsign + locator`.
* <strong class="defined-term">SPOTS</strong> beschreibt den Umfang der qualifizierenden Beobachtungen.

Bei Compare werden beide Zeilen in Only Target, Joint, Both (Async) und Only Reference unterteilt. Die Stationskategorien ordnen jede Identität genau einer Hauptkategorie zu. Die Spot-Kategorien zählen den Evidenzumfang einschließlich exklusiver Beobachtungen von Identitäten, die zugleich Joint-Evidenz besitzen.

Bei Success unterteilt `SPOTS` die Nennerevidenz bei RX in Target und Elsewhere beziehungsweise bei TX in Target und Other Signals. `STATIONS` unterteilt die qualifizierenden Identitäten in Peers mit mindestens einer Target-Beobachtung und Peers ausschließlich mit Gegen-Evidenz. Target-only und nicht qualifizierende Evidenz werden ausgeschlossen, weil sie nicht in die Success Rate eingehen.

Die Zähler am Kartenfuß beziehen sich auf den sichtbaren Kartenbereich. Viele Spots von nur wenigen Stationen bedeuten wiederholte Evidenz aus einer schmalen Identitätsbasis. Viele Stationen zeigen eine breitere Beteiligung unterschiedlicher Identitäten und geografischer Räume.

Eine Identität `callsign + locator` ist eine Analyseidentität und kein Beweis für genau eine physische Station. Suffixe, veraltete Locator und Locatorwechsel können eine physische Station in der Evidenz aufteilen oder verschieben.

<a id="sec-3-6"></a>
<a id="sec-3-6a"></a>

#### 2.5a Ein geografisches Segment untersuchen (Success-Modus)

Wähle im `Segment-Inspektor` einen oder mehrere Entfernungsbereiche und Himmelsrichtungen aus. Dadurch öffnet sich die Evidenz hinter dem entsprechenden Kartenausschnitt.

**Target und Gegen-Evidenz.** Die Anzahlen für Target und Elsewhere/Other Signals zeigen die Beobachtungen, die in den Success-Nenner des ausgewählten Segments eingehen.

**Stationsmittel** gibt jedem qualifizierenden Peer genau eine gleich große Stimme und entspricht dem Kartenwert. **Beobachtungsebene** fasst alle qualifizierenden Beobachtungen zusammen. Weichen beide Werte voneinander ab, beeinflussen Peers mit hohem Beobachtungsumfang das gepoolte Ergebnis anders als der typische Peer.

**Station Success Rate by Evidence Count** stellt jede Station mit Target-Evidenz als einen Punkt dar. Seine vertikale Position ist die Success Rate; die horizontale logarithmische Achse zur Basis 2 zeigt die Anzahl `Target + Gegen-Evidenz`. Punkte oben rechts stehen für eine hohe Rate bei wiederholter Evidenz. Punkte auf der linken Seite zeigen, wo relativ wenig Evidenz zu einem extremen Prozentwert führen kann.

Stationen ohne Target-Evidenz fehlen in diesem Streudiagramm, weil sie alle bei `0%` lägen. Sie bleiben in den Kartenzählern, der zeitlichen Evidenz und – bei aktivierter Option `Zero-Target-Stationen zeigen` – in Station Insights enthalten.

**Success im Zeitverlauf** zeigt ein stationsgleichgewichtetes Panel und ein Panel auf Beobachtungsebene. Ähnliche Muster sprechen dafür, dass der Beobachtungsumfang die Aussage nicht wesentlich verändert. Abweichungen zeigen, wo besonders aktive Peers oder Zeitintervalle die gepoolte Rate beeinflussen. Leere Zellen bedeuten fehlende qualifizierende Evidenz und nicht gemessene `0 %`.

<a id="sec-3-6b"></a>

#### 2.5b Ein geografisches Segment untersuchen (Compare-Modus)

**Decode Outcomes** zeigen die Breite der Stationen in den Kategorien Joint, Only Target, Both (Async) und Only Reference. So lässt sich erkennen, ob das gepaarte Delta SNR einen großen Teil der geografischen Abdeckung oder nur eine schmalere Joint-Teilmenge beschreibt.

**Station Medians (Delta SNR)** weist jeder beitragenden Station genau einen Wert zu: ihren Median des gepaarten Delta SNR. Die Stationen werden somit gleich gewichtet. Eine überwiegend oberhalb oder unterhalb von null liegende Verteilung zeigt, dass die verfügbaren Pfade konsistent das Target beziehungsweise die Referenz begünstigen. Eine breite oder geteilte Verteilung zeigt, dass der beobachtete Unterschied vom Pfad abhängt.

**Joint-Spot Δ SNR** beziehungsweise **Geplantes Paar Δ SNR** zeigt jedes konsolidierte Paar desselben Zyklus beziehungsweise jedes gültige geplante Paar beim sequenziellen TX A/B. Diese Ansicht macht Streuung, Quantisierung und Ausreißer sichtbar, wobei aktive Stationen mehrere Werte beitragen können. Eine Verschiebung gegenüber der Verteilung der Stationsmediane zeigt, wie sich der Beobachtungsumfang auf das stationsgleichgewichtete Bild auswirkt.

**Delta SNR im Zeitverlauf für Joint Spots oder geplante Paare** verwendet genau dieselben Evidenzzeilen auf Beobachtungsebene und denselben ausgewählten Entfernungs- und Richtungsbereich wie das Histogramm für Joint Spots beziehungsweise geplante Paare. Die Zeilenauswahl in Station Insights verändert diese Segmentansicht nicht. Das linke Panel behält das tatsächliche UTC-Datum und die UTC-Uhrzeit jeder Zeile bei; das rechte faltet dieselbe Evidenz aus allen beitragenden Tagen auf eine gemeinsame 24-Stunden-Achse nach UTC-Stunde.

Sequenzielles TX A/B meldet geplante Paare anstelle von Joint Spots.

Der UI-Begriff `Joint Spot` bezeichnet eine konsolidierte Vergleichseinheit desselben Zyklus und nicht zwangsläufig eine unveränderte einzelne Datenbankzeile. Die genaue Aggregation auf Stations- und Segmentebene ist in [Abschnitt 7.7](#sec-7-7) definiert.

<a id="sec-3-7"></a>
<a id="sec-3-7a"></a>

#### 2.6a Die beitragenden Stationen untersuchen (Success-Modus)

`Station Insights` listet die Identitäten `callsign + locator` auf, die zum ausgewählten Segment beitragen. Success-Zeilen zeigen Target- und Elsewhere- beziehungsweise Other-Signals-Evidenz, Success Rate und den Median des erfolgreichen Target-SNR, normiert auf 1 W. Lies jede Rate zusammen mit ihren Anzahlen für Target und Gegen-Evidenz; mit `Zero-Target-Stationen zeigen` lassen sich qualifizierende Stationen ohne Target-Evidenz wieder einblenden.

Wähle eine oder mehrere Stationen aus, um die Evidenzansicht für diese Auswahl zu öffnen. Unter `Station Insights` zeigt das chronologische Panel Success Rate sowie Target-/Gegen-Evidenz im Zeitverlauf für die Pfadklassen Nacht, Greyline/gemischt und Tageslicht; daneben erscheint die Verteilung des erfolgreichen Target-SNR. Bei Auswahl mehrerer Stationen wird ihre aggregierte Evidenz gemeinsam dargestellt.

<a id="sec-3-7b"></a>

#### 2.6b Die beitragenden Stationen untersuchen (Compare-Modus)

Wähle eine oder mehrere Stationen aus, um die Evidenzansicht für diese Auswahl zu öffnen. `Station Insights` listet die Identitäten `callsign + locator` auf, die zum ausgewählten Segment beitragen. Compare-Zeilen zeigen Joint- und exklusive Evidenz sowie das stationsbezogene mediane Delta SNR; `Show Non-Joint` schließt Identitäten ohne qualifizierende gepaarte Evidenz ein. Unter der Stationstabelle erscheint ein Delta-SNR-Histogramm neben einem der beiden Zeitdiagramme: `Chronologisch` oder dem nach Datum gefalteten Diagramm `UTC-Stunde`. Diese Diagramme verwenden die ausgewählten Joint Spots oder geplanten Paare; die Ansicht `UTC-Stunde` erfordert Evidenz von mindestens zwei verschiedenen UTC-Tagen. Bei Auswahl mehrerer Stationen wird ihre aggregierte Evidenz gemeinsam dargestellt. Das Histogramm und das aktive Zeitdiagramm verwenden den Median der ausgewählten Evidenz, nicht den darüber angezeigten Segmentmedian.

<a id="sec-3-8"></a>

#### 2.7 Die zugrunde liegende Evidenz prüfen

`Drill-Down` ist die Prüfoberfläche auf Zeilenebene:

* Success zeigt die Klassifikationen Target-aktiver Peer-Zyklen einschließlich Target-only.
* Compare im selben Zyklus zeigt Target-/Referenz-Evidenz und Delta SNR aus dem gemeinsamen Zyklus.
* Der lokale Nachbarschafts-Median schlüsselt die lokalen Referenzidentitäten hinter dem Zyklusmedian auf.
* Sequenzielles TX A/B zeigt das geplante UTC-Paar, `Micro-Med A`, `Micro-Med B` und `Paar Δ`.

Nutze diese Zeilen, um einen überraschenden Stations- oder Segmentwert nachzuvollziehen, Locatorwechsel oder einzelne Ausreißer zu erkennen und zu bestätigen, welche Beobachtungen gepaart oder ausgeschlossen wurden. Drill-Down ist der Prüfpfad hinter den Zusammenfassungen und keine eigene Leistungskennzahl.

<a id="sec-3-9"></a>

#### 2.8 Durchgerechnetes Compare-Beispiel

Die folgenden Werte sind neutral und hypothetisch.

1. **Den Lauf bestätigen:** Der Titel bezeichnet ein RX-Compare-Ergebnis mit dem erwarteten Target, der erwarteten Referenz, dem Band, UTC-Zeitfenster und der Referenzkorrektur.
2. **Karte:** Das Nordostsegment `2500-5000 km` ist leicht zugunsten des Targets eingefärbt. Damit ist der zu untersuchende Bereich lokalisiert.
3. **Stationen und Spots:** Der Kartenfuß zeigt Joint-Evidenz über mehrere Identitäten sowie etwas Evidenz in den Kategorien Only Target und Only Reference.
4. **Segment-Inspektor:** Das ausgewählte Segment meldet ein stationsgleichgewichtetes medianes Delta SNR von `+1.2 dB`, basierend auf `6 joint stations | 47 joint spots`. Die Verteilung auf Beobachtungsebene hat einen Median von `+0.8 dB`; wiederholte Beobachtungen gewichten die Roh-Evidenz also etwas anders als die Zusammenfassung mit gleicher Stationsgewichtung.
5. **Station Insights:** Vier Stationsmediane sind positiv, zwei liegen nahe null. Keine einzelne Identität liefert den Großteil der 47 Joint Spots, und die Decode Outcomes bleiben gemischt.
6. **Drill-Down:** Die Zeilen bestätigen Paare aus Target und Referenz im selben Zyklus mit den erwarteten Rufzeichen- und Locator-Identitäten. Die Delta-SNR-Werte auf Zeilenebene berücksichtigen die konfigurierte Referenzkorrektur, und keine einzelne Ausreißerzeile erklärt den Segmentmedian.
7. **Schlussfolgerung:** „Für dieses Target, diese Referenz, dieses Band, dieses UTC-Zeitfenster und das ausgewählte Nordostsegment `2500-5000 km` begünstigte das stationsgleichgewichtete Delta SNR das Target um `+1.2 dB`, gestützt durch 6 Joint-Stationsidentitäten und 47 Joint Spots. Der Median auf Beobachtungsebene betrug `+0.8 dB`; die Decode Outcomes blieben gemischt.“

Diese Schlussfolgerung nennt Laufdefinition, geografischen Bereich, beide Gewichtungsebenen, die Anzahl gepaarter Evidenzeinheiten und die einseitige Evidenz. Sie beschreibt das ausgewählte Datenmaterial und macht aus dem Vergleich weder einen Signifikanztest noch eine isolierte Messung des Antennengewinns.

---

<a id="sec-4"></a>
### 3. Ergebnisse absichern und kommunizieren

Ein aussagekräftiges WSPRadar-Ergebnis verbindet einen klaren Versuchsaufbau, breite Evidenz und eine Formulierung, die genau zur tatsächlichen Beobachtung passt.

<a id="sec-4-1"></a>

#### 3.1 Breite, Stability und Wiederholbarkeit beurteilen

Beurteile das Ergebnis anhand des vollständigen Evidenzbildes:

* Identitäten der beteiligten Stationen;
* Umfang der qualifizierenden Spots oder geplanten Paare;
* Übereinstimmung zwischen Stationen;
* stationsgleichgewichtete Zusammenfassungen und Zusammenfassungen auf Beobachtungsebene;
* benachbarte geografische Segmente;
* Zeitansichten und Ansichten der Pfadbeleuchtung;
* Decode Outcomes;
* Qualität von Identitäten und Locator-Angaben;
* Kontrolle und Wiederholung des Versuchs.

Evidenz ist **breiter**, wenn mehrere Identitäten und benachbarte Segmente übereinstimmen. Sie ist **intern konsistenter**, wenn stationsgleichgewichtete Ansichten, Ansichten auf Beobachtungsebene und Zeitansichten dasselbe begrenzte Bild stützen. Sie ist **besser kontrolliert**, wenn die betrieblichen Anforderungen des gewählten Versuchsleitfadens eingehalten und dokumentiert wurden.

<strong class="defined-term">90% Stability</strong> ist ein deskriptives Bootstrap-Intervall um einen Median. Ein schmales Intervall bedeutet, dass sich der angezeigte Median beim wiederholten Ziehen aus den verfügbaren Werten nur wenig ändert. Nutze es, um die Empfindlichkeit gegenüber der beobachteten Stichprobe zu beschreiben. Es ist weder ein Konfidenzintervall noch ein Test auf statistische Signifikanz und weist weder Unabhängigkeit nach noch beseitigt es Datenverzerrungen.

**Stability der Stichprobe und experimentelle Wiederholbarkeit sind verschieden.** Das Stability-Intervall zieht erneut aus der Evidenz, die bereits in diesem Lauf vorhanden ist. Eine Wiederholung des Versuchs in einem weiteren geeigneten Zeitfenster prüft, ob das beobachtete Muster unter neuen Betriebs- und Ausbreitungsbedingungen Bestand hat.

WSPRadar verdichtet diese Dimensionen bewusst nicht zu einer einzigen Beweisstufe. Die sichtbaren Anzahlen, Verteilungen und zugrunde liegenden Zeilen erlauben eine Beurteilung im Kontext des tatsächlich durchgeführten Versuchs.

<a id="sec-4-2"></a>

#### 3.2 Ein Ergebnis durch Wiederholung und Kontrolle absichern

Nutze einen ersten explorativen Lauf, um ein mögliches Muster zu erkennen. Lege vor einer bestätigenden Wiederholung Richtung, Band, Benchmark, Filter, Evidenzschwellen, Zeitplan sowie den primären geografischen oder zeitlichen Auswertungsbereich fest. Dokumentiere alternative Radien oder Bereiche als Sensitivitätsanalysen, statt nur die günstigste Ansicht beizubehalten.

Wenn das Ergebnis eine wichtige Stationsentscheidung stützen soll:

* dehne das Beobachtungsfenster über die Ausbreitungszustände aus, die in der Schlussfolgerung genannt werden;
* bevorzuge für Aussagen über vollständige Tageszyklen mehrtägige Evidenz;
* wiederhole den Versuch an einem anderen Tag oder in einem anderen Ausbreitungszeitraum;
* vertausche bei sequenziellem TX Hardware A/B die A/B-Zeitplanzuordnungen;
* halte nicht untersuchte Variablen zwischen den Wiederholungen stabil;
* vergleiche Läufe mit derselben Richtung, demselben Band, Benchmark, denselben Filtern und Evidenzschwellen;
* untersuche jede Identität, jeden Locator oder kurzen Zeitraum, der einen großen Anteil der Evidenz liefert;
* bewahre Aufbaunotizen auf, damit ein späterer Lauf die Stationskonfiguration reproduzieren kann.

Kleine beobachtete Unterschiede werden nützlicher, wenn sie über Stationen, Zeiträume, benachbarte Segmente und kontrollierte Wiederholungen erneut auftreten. Eine vertauschte Zuordnung bei sequenziellem TX ist besonders aussagekräftig, weil sie Zeitplan-, Schaltpfad- oder Zykluspositionseffekte sichtbar machen kann, die bei einer gewöhnlichen Wiederholung in derselben Rolle verbleiben.

TX und RX verwenden unterschiedliche Peer-Populationen und Opportunity-Definitionen. Vergleiche gleichartige TX- und RX-Läufe, wenn du die Stationsbalance oder ein „Alligator“-Muster untersuchst.

<a id="sec-4-3"></a>

#### 3.3 Eine evidenzgerechte Schlussfolgerung formulieren

Eine kurze betriebliche Aussage nennt das Target und bei Compare gegebenenfalls die feste Referenz, Setup B oder die lokale Benchmark-Definition. Außerdem nennt sie TX- oder RX-Richtung, Band, UTC-Zeitfenster, geografischen Bereich, Ergebnistyp, angezeigten Wert und die stützende Stations- beziehungsweise Evidenzanzahl.

Ein vollständiger technischer Bericht nennt zusätzlich:

* stationsgleichgewichtete Werte und Werte auf Beobachtungsebene, sofern beide gelten;
* Stationen und Spots beziehungsweise die Anzahl von Joint-Stationen und Joint-Spots/-Paaren;
* Decode Outcomes bei Compare;
* Versuchsbedingungen und eine etwaige Referenzkorrektur;
* Filter und Evidenzschwellen;
* ob sich das Muster über Zeit, Stationen oder Läufe wiederholte;
* jeden alternativen Radius oder Bereich, der als Sensitivitätsanalyse verwendet wurde.

**Formulierung für Success**

> Für dieses Target, Band, UTC-Zeitfenster und die ausgewählte Peer-Population beschreibt die angezeigte Success Rate den Anteil der unabhängig bestätigten Opportunities, in denen auch das Target qualifizierende Evidenz lieferte. Stationen, Spots, geografischer Bereich und Zeitansichten beschreiben Breite und Wiederholung der stützenden Evidenz.

**Formulierung für Compare**

> Für dieses Target, diese Referenz, dieses Band, dieses UTC-Zeitfenster und das ausgewählte Segment begünstigte das stationsgleichgewichtete Delta SNR Target/Referenz um den angezeigten Betrag. Delta SNR auf Beobachtungsebene, die Anzahlen der Joint-Stationen und Joint-Spots/-Paare sowie die Decode Outcomes beschreiben die stützende gepaarte und einseitige Evidenz.

Verwende den Namen des Designs passend zur beschriebenen Größe:

* Ein **Hardware A/B-Test** vergleicht die dokumentierten lokalen Pfade.
* Ein **Buddy-Test** vergleicht vollständig aufgebaute Stationen und ihre Betriebsumgebungen.
* Der **Lokale Nachbarschafts-Median** vergleicht das Target mit der aktiven Median-Nachbarschaftsdefinition innerhalb des gewählten Radius.
* Die **Beste lokale Station** vergleicht das Target mit einer wechselnden Hüllkurve des stärksten Peers.
* Ein richtungsabhängiges Ergebnis beschreibt die beobachteten WSPR-Pfade und beteiligten Stationen, nicht ein absolutes Strahlungsdiagramm.
* Die Angabe `1 S-Stufe = 6 dB` beschreibt die Kartenskala und nicht die Kalibrierung der beteiligten Empfänger.

Verwende Formulierungen wie „beobachteter Unterschied“, „in der ausgewählten Evidenz begünstigt“, „bedingte Erreichbarkeit“ und „Vergleich vollständig aufgebauter Stationen“. Aussagen über isolierten Antennengewinn, Wirkungsgrad, Empfängerempfindlichkeit, Kausalität oder statistische Signifikanz sind Versuchen vorbehalten, die diese Größen tatsächlich messen oder prüfen.

Die vollständige Referenz für gestützte und nicht gestützte Aussagen steht in [Kapitel 8](#sec-8).

<a id="sec-4-4"></a>

#### 3.4 Lauf und Kontext sichern

Mit `Alle Ergebnisse zum Download vorbereiten` erstellst du das Exportpaket der aktuellen Analyse. Es enthält die aktuelle Konfiguration, Laufmetadaten, verarbeitete Evidenz, Tabellen und hochauflösende Abbildungen.

Bewahre zusammen mit diesem Paket externe Notizen auf zu:

* physischem Aufbau von Antenne und Speiseleitung;
* Umschalter- oder Splittertopologie;
* Sender- oder Empfängerhardware;
* Leistungsmessungen und Bezugsgrundlage der Leistungsangaben;
* Decoder- und Softwareversionen;
* Betriebsplan, physischer Zuordnung des Zeitplans zu den Pfaden und jeder vertauschten Zuordnung;
* Kalibrierverfahren;
* Wetter, Störungen oder beabsichtigten Änderungen, die für den Lauf relevant waren.

WSPRadar kann die konfigurierte Analyse und die verarbeitete Evidenz sichern, aber nicht jedes physische Detail der Station erschließen. Das Exportpaket zusammen mit knappen Stationsnotizen macht Vergleiche und Reproduktionen deutlich belastbarer. [Kapitel 8](#sec-8) dokumentiert den genauen Exportinhalt und die verbleibenden Grenzen der Reproduzierbarkeit.

<div style="page-break-before: always;"></div>

<a id="part-ii"></a>

## Teil II: Bedienelemente und Fehlersuche

Nutze diesen Teil als Nachschlagewerk beim Einrichten, Wiederholen oder Diagnostizieren einer Analyse. Die Versuchsleitfäden erläutern, welches Design zur jeweiligen Fragestellung passt; dieser Teil beschreibt die genauen Bedienelemente, Standardwerte, Wertebereiche und das Verhalten von Konfigurationen.

<a id="sec-5"></a>

### 4. Bedienelemente und Konfiguration

WSPRadar trennt Bedienelemente, welche die wissenschaftliche Analyse verändern, von solchen, die nur die Darstellung bereits abgeschlossener Evidenz beeinflussen. Wer den Unterschied kennt, kann eine Ansicht gezielt anpassen, ohne versehentlich den Versuch zu verändern.

| Klasse | Was sie verändert | Konfiguration und Reproduzierbarkeit |
|---|---|---|
| **Wissenschaftliche Bedienelemente** | Abfragepopulation, Paarbildung, Klassifikation, Normierung, Qualifizierung oder Aggregation. Dazu gehören Richtung, Identität, Band, Zeit, Benchmark, Korrektur, Sonnenstandsfilter, Ausschlussfilter und Evidenzschwellen. | Werden gespeichert, sofern sie gelten, und im Exportpaket festgehalten. Eine Änderung verwirft das abgeschlossene Ergebnis, damit die Analyse mit der neuen Definition erneut ausgeführt werden kann. |
| **Ansichtsbedienelemente** | Welche abgeschlossene Evidenz dargestellt oder untersucht wird, ohne die vorgelagerte Abfrage erneut auszuführen. Dazu gehören Kartenbereich, ausgewähltes Segment, ausgewählte Stationen, Sichtbarkeit von Non-Joint- beziehungsweise Zero-Target-Evidenz, Zeitansicht und Zeit-Bin der Evidenz. | Kartenbereich, Bereich/Richtung im Segment Inspector und die jeweils anwendbaren dauerhaften Compare-/Success-Ansichten werden gespeichert. Tabellenfilter und weitere beiläufige Interaktionen bleiben flüchtig. |
| **Flüchtiger UI-Zustand** | Auf- und Zuklappen von Bereichen, Tabellen- und Drill-Down-Filter, Sichtbarkeit der Dokumentation, vorbereitete Download-Bytes und weitere beiläufige Interaktionszustände der Sitzung. | Gehört nicht zur wissenschaftlichen Konfiguration und wird normalerweise nicht serialisiert. |
| **Zur Reproduzierbarkeit gespeicherte Konfigurationsfelder** | Der jeweils anwendbare wissenschaftliche Zweig sowie ausdrücklich unterstützte dauerhafte Ansichtseinstellungen. | Werden in der versionierten `.config` gespeichert. Inaktive ausgeblendete Zweige werden weggelassen, statt als ruhende Werte erhalten zu bleiben. |

Die exakten Formeln und Verarbeitungsregeln stehen weiterhin in den [Wissenschaftlichen Methoden](#sec-7).

<a id="sec-5-1"></a>

#### 4.1 Ablaufsteuerung

**`Demo laden`** öffnet gepflegte historische Profile. Ein Profil kann zur Prüfung geladen oder sofort ausgeführt werden. Ein unverändert geladenes Profil bleibt auch beim anschließenden Start über die normale Analyse-Schaltfläche eine geführte Demo und behält damit die Demo-Cache-Richtlinie. Wird ein wissenschaftliches Bedienelement geändert, gilt die bearbeitete Konfiguration als normale Analyse.

**`Konfig laden`** validiert eine versionierte JSON-`.config` streng und lädt sie anschließend. Ungültige Identitäten, Datumswerte, Auswahlwerte, Wertebereiche, doppelte Felder und nicht unterstützte Schemaversionen werden abgelehnt.

**`Konfig speichern`** öffnet ein kompaktes Profilformular. Gib einen Titel und eine optionale Beschreibung ein; eine optionale stabile ID kann angegeben oder automatisch erzeugt werden. Die entstehende Datei `<profil-id>.config` speichert alle anwendbaren Eingaben und dauerhaften Compare-/Success-Ansichten. Ist `Letzte X Stunden` konfiguriert, fragt der Speichervorgang außerdem, ob dieses gleitende relative Fenster beibehalten oder durch die aufgelösten absoluten UTC-Start-/Endzeitpunkte des aktiven Laufs ersetzt werden soll. Wähle die absolute Form, wenn ein späterer Lauf dieselben Datumswerte verwenden soll. Eine gespeicherte Konfiguration enthält weder Ergebniszeilen noch externe Versuchsnotizen oder flüchtige Tabellenfilter.

**`RX-Analyse starten` / `TX-Analyse starten`** ist eine richtungsabhängige Schaltfläche. Sie führt Success und – sofern ein Benchmark gewählt ist – Compare für die unter den Kernparametern gewählte RX- oder TX-Analyse aus. Nach dem Absenden bleibt die Schaltfläche deaktiviert, solange die unveränderte Analyse dieser Sitzung wartet oder ausgeführt wird. Wird ein wissenschaftliches Bedienelement geändert, entsteht ein anderer Auftrag und die Analyse-Schaltfläche wird für die geänderte Konfiguration wieder verfügbar. Beim Warten auf Kapazität zeigt der Status nur die aktuelle Position der eigenen Analyse und keine Warteschlangensummen anderer Nutzer.

**`Alle Ergebnisse zum Download vorbereiten`** erstellt das Exportpaket der aktuellen Analyse bei Bedarf.

**`Vollständige Dokumentation laden` / `Vollständige Dokumentation ausblenden`** lädt beziehungsweise verbirgt ausdrücklich das vollständige Webhandbuch.

**`PDF vorbereiten`** erstellt das vollständige Handbuch in der ausgewählten Sprache bei Bedarf als PDF. Das vollständige Webhandbuch muss dafür nicht zuerst geöffnet werden.

<a id="sec-5-2"></a>

#### 4.2 Kernparameter

Diese Bedienelemente definieren Target, Betriebsrichtung, Band und Evidenzfenster.

| UI-Bezeichnung | Werkseinstellung | Funktion |
|---|---|---|
| **RX-Analyse / TX-Analyse** | keine; erforderlich | RX wertet das Target als empfangende WSPR-Station aus, TX als sendende WSPR-Station. `RX-Analyse starten` / `TX-Analyse starten` und `Konfig speichern` bleiben deaktiviert, bis eine Option gewählt wurde. |
| **Dein Rufzeichen (Empfänger im Test)** / **Dein Rufzeichen (Sender im Test)** | leer | Exakte Target-Identität für die gewählte Richtung. Zulässig sind 3 bis 15 Zeichen aus `A-Z`, `0-9` und `/`. |
| **QTH Locator (4-6 Chars)** | leer | Kartenmittelpunkt und Ursprung des lokalen Radius. Success verwendet außerdem die ersten vier Zeichen zur Zuordnung der Target-Identität. |
| **Frequenzband** | `20m` | Genau eines aus `LF`, `MF`, `160m`, `80m`, `60m`, `40m`, `30m`, `22m`, `20m`, `17m`, `15m`, `12m`, `10m`, `8m`, `6m`, `4m`, `2m`, `70cm` oder `23cm`. |
| **Zeitraum-Auswahl** | `Letzte X Stunden` | Wählt aktuelle oder benutzerdefinierte Evidenz in UTC. Der Modus `Letzte X Stunden` erlaubt 1 bis 168 Stunden und verwendet standardmäßig 24. |
| **Stunden zurück (DB Update alle 15 Min)** | `24` | Erscheint für `Letzte X Stunden` und akzeptiert 1 bis 168 Stunden. Die absoluten Endpunkte werden beim Start aufgelöst und für diesen aktiven Lauf festgehalten. Beim Speichern wählst du, ob die Datei `Letzte X Stunden` beibehält oder diese aufgelösten UTC-Endpunkte festschreibt. |
| **Startdatum**, **Enddatum**, **Startzeit (UTC)**, **Endzeit (UTC)** | Vortag `00:00` bis aktueller Tag `23:59` | Erscheinen für `Datum/Uhrzeit manuell`. Datumswerte beginnen im Jahr 2008; ein einzelnes Fenster ist auf 31 Tage begrenzt. Die aufgelösten Endpunkte werden auf 15-Minuten-Grenzen abgerundet. Success und Compare unterscheiden sich derzeit an der exakten Endgrenze, wie im [Zeitmodell](#sec-7-1) beschrieben. |

Verwende das Rufzeichen exakt so, wie es hochgeladen wurde. `DL1MKS`, `DL1MKS/P`, `DL1MKS/1` und `DL1MKS/QRP` sind eigenständige Identitäten; WSPRadar führt keine verdeckte Präfixzuordnung durch.

Ein Maidenhead-Locator ist eine kompakte Ortsangabe im Gitternetz. Vier Zeichen bezeichnen ein größeres Gebiet, sechs Zeichen ein kleineres Gebiet darin. WSPRadar verwendet das konfigurierte QTH als Kartenmittelpunkt und Ursprung des lokalen Radius. Für das Target-Matching in Success werden die ersten vier Locator-Zeichen herangezogen.

<a id="sec-5-3"></a>

#### 4.3 Benchmark-Einstellungen

**`Benchmark-Design`** hat die Werkseinstellung `Kein Benchmark (nur Success)`. Zur Auswahl stehen:

- `Kein Benchmark (nur Success)`
- `Hardware A/B-Test (Eigenes Setup)`
- `Fremdes Rufzeichen (Buddy-Test)`
- `Lokaler Nachbarschafts-Benchmark`

Nur Success überspringt Compare. Die übrigen Optionen ergänzen das eigenständige Success-Ergebnis um Compare.

| UI-Bezeichnung | Standard und Wertebereich | Wann sie erscheint und was sie steuert |
|---|---|---|
| **Referenz-SNR-Korrektur (dB)** | `0.0`; `-99.9` bis `+99.9` in Schritten von `0.1 dB` | Erscheint für Compare und ist bei `Kein Benchmark (nur Success)` ausgeblendet. Der Wert wird zum SNR der Referenzseite addiert, bevor Delta SNR berechnet wird. |
| **Referenz-Rufzeichen** | Beispiel `DL2XYZ` | `Fremdes Rufzeichen (Buddy-Test)`. Ersetze das Beispiel durch ein exaktes Rufzeichen, das sich vom Target unterscheidet. |
| **Lokale Benchmark-Methode** | `Lokaler Nachbarschafts-Median` | Lokaler Nachbarschafts-Benchmark. Wählt `Lokaler Nachbarschafts-Median` oder die strenge Methode `Beste lokale Station`. |
| **Nachbarschaftsradius (km)** | `100`; 10 bis 250 km in Schritten von 10 km | Lokaler Nachbarschafts-Benchmark. Bezieht lokale Referenzkoordinaten rund um das konfigurierte QTH ein. |
| **Setup B Callsign** | leer | RX Hardware A/B-Test. Gib ein exaktes Rufzeichen ein, das sich von Setup A unterscheidet. |
| **Wiederholintervall** | `10 min`; `4, 6, 10, 12, 20, 30, 60 min` | TX Hardware A/B-Test. Gemeinsames Wiederholintervall jedes physischen Signalpfads. Alle Werte sind gerade, WSPR-kompatible Teiler einer UTC-Stunde. |
| **Target-Start** | `00 UTC`; gerade Phasen unterhalb des Wiederholintervalls | TX Hardware A/B-Test. Definiert die UTC-Startphase des Targets / Setups A. |
| **Referenz-Start** | `02 UTC`; gerade Phasen unterhalb des Wiederholintervalls | TX Hardware A/B-Test. Definiert die UTC-Startphase der Referenz / des Setups B und wird so gewählt, dass sie sich nicht mit dem Target-Start überschneidet. |

Der Hardware A/B-Test folgt der gewählten Option **RX-Analyse / TX-Analyse**. RX zeigt für den Aufbau mit zwei Empfängern das Rufzeichen von Setup B. TX zeigt das gemeinsame Wiederholintervall, zwei Startphasen ohne Überschneidung, eine Tauschfunktion und die daraus entstehende Zeitplanvorschau für eine Stunde. Die Paarbildung folgt diesem Zeitplan automatisch.

Bei TX Hardware A/B bezeichnet das `Wiederholintervall` die tatsächliche Wiederkehr jedes physischen Pfads. Es entspricht nicht zwangsläufig der `Frame`-Bezeichnung eines Senders, der einen Ausgang abwechselnd auf zwei Pfade schaltet. Vergleiche die Vorschau mit den beobachteten Startzeiten auf Sendung und der physischen Schaltzuordnung. Gerätespezifische Beispiele stehen in [Anhang B](#sec-b), die exakte Paarbildung in den [Abschnitten 7.1](#sec-7-1) und [7.7](#sec-7-7).

Beim Wechsel der Richtung oder des Benchmark-Modus wird der nicht anwendbare Zweig ausgeblendet. Seine bisherigen Widget-Werte werden weder gespeichert noch wiederhergestellt. Eine Konfiguration mit `Kein Benchmark (nur Success)` enthält deshalb keine ruhenden Compare-Parameter.

##### Vorzeichen der Referenz-SNR-Korrektur

Eine positive Korrektur erhöht den korrigierten Referenz-SNR-Wert und verringert dadurch das Delta SNR Target minus Referenz. Gib einen gemessenen Kalibrierversatz `target - reference` mit demselben Vorzeichen ein. Ergibt beispielsweise eine Kalibrierung mit gemeinsamem Eingang `+1.6 dB`, wird `+1.6 dB` eingetragen. Die exakten Gleichungen stehen in der [Delta-SNR-Methode](#sec-7-5).

Die Korrektur gilt für:

- Setup B oder den Referenzzeitplan im `Hardware A/B-Test`;
- das Referenz-Rufzeichen bei `Fremdes Rufzeichen (Buddy-Test)`;
- den ausgewählten lokalen Wert bei `Beste lokale Station`; und
- jeden lokalen Beitrag vor der Aggregation zum `Lokalen Nachbarschafts-Median`.

Eine konstante Korrektur eignet sich für einen belastbar bestimmten konstanten Versatz. Übersteuerung, instabile AGC, zeitweilig fehlerhafte Signalführung, frequenzabhängiger Amplitudengang und falsche Leistungsangaben müssen dagegen im Versuchsaufbau oder in der Hardware behoben werden. [Anhang C](#sec-c) beschreibt die Kalibrierung.

<a id="sec-5-4"></a>

#### 4.4 Filter und Evidenzschwellen

Mit diesen Bedienelementen bestimmst du die Peer-Population, den Beleuchtungszeitraum und die für eine Darstellung erforderliche Mindestevidenz. Leite sie aus der beabsichtigten Population und Evidenzuntergrenze ab. Lockere Filter oder Schwellen nach der Ergebnisbetrachtung nicht allein, um eine dichtere oder günstigere Karte zu erhalten; dokumentiere eine geänderte Analyse als separate Konfiguration.

**`Spezial-Rufzeichen Q, 0, 1 ausschließen`**

- **Standard:** aus
- **Gilt für:** alle Ergebnisse
- **Wirkung:** schließt qualifizierende Peer-Identitäten aus, die mit `Q`, `0` oder `1` beginnen.
- **Ändern, wenn:** die vorgesehene Peer-Population keine ballon- oder telemetrieähnlichen Identitäten mit diesen Präfixen enthalten soll. Dokumentiere die Auswahl im Bericht.

Setze dieses Bedienelement passend zur Fragestellung ein:

- In RX Compare können baken- oder telemetrieähnliche Sender wertvolle schwache Signale im selben Zyklus liefern, die beide Empfänger decodieren.
- In RX Success bleiben sie eingeschlossen, wenn Bakenempfang zur Fragestellung gehört; schließe sie aus, wenn die beabsichtigte Population aus regulären Amateurfunkstationen besteht.
- In TX-Analysen wirkt der Filter auf die empfängerseitigen Peer-Identitäten. Nutze ihn, wenn diese Identitäten die beabsichtigte Empfängerpopulation verzerren.

**`Bewegliche Stationen filtern`**

- **Standard:** aus
- **Gilt für:** kartierte Peers
- **Wirkung:** entfernt ein Peer-Rufzeichen, wenn es nach Anwendung der übrigen Filter mehr als einen vierstelligen Locator meldet.
- **Ändern, wenn:** mobile Identitäten oder wechselnde Locator-Angaben sonst mehrere Orte unter einem Rufzeichen vermischen würden. Prüfe im Drill-Down, ob wahrscheinlich Bewegung oder ein fehlerhafter Locator vorliegt.

**`Lokaler QTH Sonnenstand`**

- **Standard:** `Ganze 24h`
- **Auswahl:** `Ganze 24h`, `Tag (Elev > +6°)`, `Nacht (Elev < -6°)`, `Greyline (-6° bis +6°)`
- **Gilt für:** alle Ergebnisse
- **Wirkung:** behält Zyklen bei, die anhand der Sonnenhöhe am Target-QTH klassifiziert wurden.
- **Ändern, wenn:** die wissenschaftliche Fragestellung gezielt einen lokalen Beleuchtungszustand betrifft. Dies unterscheidet sich von den in der Success-Evidenz gezeigten Beleuchtungsklassen des Ausbreitungspfads.

**`Kartenbereich (Max. Distanz km)`**

- **Standard:** `22000`
- **Auswahl:** `2500`, `5000`, `10000`, `15000`, `20000`, `22000`
- **Gilt für:** Karten- und Inspektionsansichten
- **Wirkung:** legt den sichtbaren und inspizierbaren radialen Bereich fest; die vorgelagerte Abfrage wird dadurch nicht eingeengt.
- **Ändern, wenn:** eine regionale Ansicht sinnvoll ist. Der Kartenbereich ist ein reproduzierbarkeitsrelevantes Ansichtsbedienelement und kein vorgelagerter Datenfilter.

**`Min. Joint Spots pro Station`**

- **Standard:** `1`
- **Wertebereich:** 1 bis 50
- **Gilt für:** simultanes Compare
- **Wirkung:** verlangt diese Anzahl von Joint-Peer-Zyklen, bevor eine Station gepaartes Delta SNR beiträgt.
- **Ändern, wenn:** du mehr wiederholte gepaarte Evidenz pro Station verlangst und dafür eine geringere geografische Abdeckung in Kauf nimmst.

**`Min. Joint-Paare`**

- **Standard:** `1`
- **Wertebereich:** 1 bis 50
- **Gilt für:** sequenzielles TX Hardware A/B
- **Wirkung:** verlangt diese Anzahl von Joint-Paaren, bevor eine Station gepaartes Delta SNR beiträgt.
- **Ändern, wenn:** du mehr wiederholte geplante Paare pro Station verlangst und dafür eine geringere geografische Abdeckung in Kauf nimmst.

Die Joint-Schwelle für Compare unterdrückt außerdem exklusive Kategorien, deren eigene Anzahl unter demselben Zahlenwert liegt. Bei sequenziellem TX Hardware A/B wird die Qualifizierung für gepaarte Evidenz in geplanten Paaren gezählt; exklusive Evidenz wird in einseitigen geplanten Paaren gezählt und mit demselben Zahlenwert verglichen.

**`Min. Target+Gegen-Evidenz pro Station`**

- **Standard:** `5`
- **Wertebereich:** 1 bis 100
- **Gilt für:** Success
- **Wirkung:** verlangt diese Anzahl von Target+Elsewhere-Beobachtungen bei RX beziehungsweise Target+Other-Signals-Beobachtungen bei TX, bevor ein Peer beiträgt.
- **Ändern, wenn:** du eine andere Evidenzuntergrenze benötigst.

Eine niedrigere Schwelle erhöht die Kartenabdeckung. Stationsraten werden jedoch gröber gestuft, wenn sie nur auf einer oder zwei qualifizierenden Opportunities beruhen. Werte wie `0 %`, `50 %` oder `100 %` können dann sehr wenig Evidenz repräsentieren. Lies die Anzahl neben der Rate und erweitere eine kleine Stichprobe durch einen längeren oder wiederholten Lauf.

**`Min. qualifizierte Stationen pro Karten-Segment`**

- **Standard:** `1`
- **Wertebereich:** 1 bis 10
- **Gilt für:** alle Karten
- **Wirkung:** verlangt diese Anzahl qualifizierender Identitäten, bevor ein Segment gezeichnet wird.
- **Ändern, wenn:** eine Kartenfarbe breitere Unterstützung durch mehrere Identitäten erfordern soll und du dafür mehr leere Segmente akzeptierst.

<a id="sec-5-5"></a>

#### 4.5 Karten-, Inspektor- und Exporteinstellungen

Diese Bedienelemente wirken auf abgeschlossene Evidenz und führen die vorgelagerte Abfrage nicht erneut aus, sofern nicht ausdrücklich anders angegeben.

- Auswahl von Segmentbereich und Richtung verändert den inspizierten Bereich. Beide Auswahlen werden für Compare und Success getrennt gespeichert.
- `Zero-Target-Stationen zeigen` stellt qualifizierende Success-Identitäten mit null Target-Bestätigungen wieder dar. Die Einstellung wird für Success gespeichert.
- `Show Non-Joint` stellt Compare-Identitäten wieder dar, die ausschließlich durch exklusive oder asynchrone Evidenz vertreten sind. Der dauerhafte Wert wird gespeichert, wenn ein Compare-Ergebnis vorhanden ist.
- Die Stationsauswahl verändert die Abbildungen der ausgewählten Stationen und den gewählten Drill-Down. Compare- und Success-Auswahl werden getrennt als exakte Identitäten aus `Rufzeichen + Locator` gespeichert. Werden alle Stationen ausgewählt, speichert die Konfiguration diese Absicht, statt jede aktuelle Tabellenzeile einzeln aufzuführen; bei einem gleitenden Fenster `Letzte X Stunden` kann sich die rekonstruierte Stationsmenge daher mit der Evidenz ändern. Fehlt eine explizit gespeicherte Identität im aktuellen Segmentbereich, bleibt sie mit einem Hinweis unausgewählt und wird nicht ersetzt; ihre gespeicherte Identität bleibt bis zu einer neuen Tabellenauswahl erhalten, sodass sie nach Wahl des passenden Segmentbereichs wieder verfügbar werden kann.
- Das Bedienelement für das Zeit-Bin der ausgewählten Station verändert nur deren chronologische Zeitachse. Die jeweils geltenden Werte für Compare sowie Success/absolut werden gespeichert.
- Die Ansichtsgruppe der ausgewählten Compare-Ansicht wählt `Chronologisch` oder `UTC-Stunde`. `UTC-Stunde` verwendet feste einstündige Zeitfenster und verändert oder überschreibt das gespeicherte chronologische Bin nicht. Die gewählte Ansicht wird in `.config` gespeichert.
- Die Zeit-Bin-Schaltflächen für Segment Compare verändern nur das linke Zeitpanel auf Segmentebene. Das nach UTC-Stunden gefaltete Panel, die Zeitachse der ausgewählten Stationen, Paarbildung und Analyse bleiben unverändert; das gewählte Bin wird unabhängig in `.config` gespeichert.
- Leere Success-Zeit-Bins bleiben leer; sie werden nicht zu Evidenz mit einer Rate von null umgedeutet.
- `Alle Ergebnisse zum Download vorbereiten` exportiert das aktuelle Ergebnis und die aktuellen Inspektor-Auswahlen. Der Paketinhalt steht im Abschnitt [Export und Reproduzierbarkeit](#sec-8-4).

<a id="sec-6"></a>

### 5. Fehlersuche und Datenqualität

Die Ursache leerer oder unerwarteter Ergebnisse lässt sich meist effizient finden, wenn du zuerst die Laufdefinition prüfst und anschließend den symptombezogenen Schritten folgst. So verhinderst du, dass eine geänderte Schwelle einen Fehler bei Rufzeichen, Band, Zeit oder Betriebsplan lediglich verdeckt.

<a id="sec-6-1"></a>

#### 5.1 Zuerst die Laufdefinition prüfen

Arbeite diese Prüfungen der Reihe nach ab:

1. **Target-Identität:** Prüfe das exakte Rufzeichen einschließlich eines etwaigen Suffixes sowie die in WSJT-X konfigurierte Identität.
2. **QTH:** Vergleiche den konfigurierten Locator und dessen erste vier Zeichen mit dem tatsächlich hochgeladenen Locator.
3. **Band:** Prüfe das exakt gewählte Band und das Band, auf dem die Station tatsächlich in Betrieb war.
4. **UTC-Evidenzfenster:** Prüfe die aufgelösten Start- und Endzeitstempel, nicht nur die relative Auswahl `Letzte X Stunden`.
5. **Tatsächlicher Betrieb:** Stelle sicher, dass das Target wie vorgesehen sendete oder empfing und dass der WSPR-Upload aktiviert war.
6. **Benchmark-Betrieb:** Prüfe für Compare die exakte Identität der Referenz oder von Setup B sowie den Betrieb der Gegenstelle während der vorgesehenen Überlappung.
7. **Technische Umsetzung:** Prüfe gegebenenfalls Uhrensynchronisation, Zuordnung des TX-Zeitplans zu den Signalpfaden, Schaltfolge, Signalführung und gemeldete Leistung.

Erst danach folgen Evidenzschwellen, Ausschlussfilter, Sonnenstandsauswahl und Kartenbereich. Ein weniger strenger Filter kann mehr qualifizierende Evidenz sichtbar machen, aber keinen Lauf reparieren, der auf die falsche Identität, das falsche Band oder den falschen Zeitraum zielt.

<a id="sec-6-2"></a>

#### 5.2 Fehler nach Symptom eingrenzen

Folge nach den gemeinsamen Prüfungen aus Abschnitt 5.1 dem Zweig, der zum Ergebnis passt:

| Symptom | Nächste Prüfungen |
|---|---|
| **Kein Ergebnis oder keine Target-Evidenz** | Prüfe den gemeldeten Status der strengen Abfrage mit `code = 1` beziehungsweise des historischen Fallbacks sowie die aktuelle Verfügbarkeit der Upstream-Daten. |
| **Compare enthält kein Delta SNR** | Prüfe gemeinsame entfernte Peers in überlappenden Zyklen oder geplanten Paaren; danach Uhren, Zuordnung des TX-A/B-Zeitplans zu den Signalpfaden, Schaltfolge, Joint-Schwelle, Filter und Bereich. |
| **Success enthält nur sehr wenige Peers** | Prüfe die unabhängige Netzaktivität; danach `Min. Target+Gegen-Evidenz pro Station`, Ausschluss- und Sonnenstandsfilter, Zeitraum und Kartenbereich. Ein längeres Fenster kann Evidenz hinzufügen, ohne die beabsichtigte Population zu verändern. |

<div style="page-break-before: always;"></div>

Wenn Evidenz vorhanden ist, aber unerwartet aussieht, fahre mit diesen Zweigen fort:

| Symptom | Nächste Prüfungen |
|---|---|
| **Viele Target-only-Success-Zeilen** | Target-Evidenz ist vorhanden, aber nicht die für den Nenner erforderliche unabhängige Bestätigung. Die Zeilen bleiben prüfbar, gehen jedoch nicht in die Success Rate ein. |
| **`Only Reference = 0`** | Prüfe das Target-Active Gate, die Evidenzschwellen und den ausgewählten Bereich; nach Anwendung dieser Regeln kann null korrekt sein. |
| **Unerwartetes Vorzeichen des Delta SNR bei Hardware A/B** | Prüfe die physische A/B-Zuordnung, Reihenfolge von Target und Referenz, Zeitplanphasen, Vorzeichen der Korrektur, tatsächliche und gemeldete Leistung sowie Kalibriernotizen. Gleiche eine Station im Drill-Down ab. |
| **Lokales Ergebnis ändert sich mit dem Radius** | Prüfe QTH und Radius und untersuche anschließend die beitragenden lokalen `callsign + locator`-Identitäten. Dokumentiere eine aussagekräftige Radiusabhängigkeit, statt nur den günstigsten Lauf auszuwählen. |
| **Alte Konfiguration mit `band=All` wird abgelehnt** | Wähle genau ein Band; eine automatische Konvertierung würde die wissenschaftliche Fragestellung verändern. |
| **Aktuelle Spots erscheinen unvollständig** | Warte nach dem letzten Zyklus ungefähr fünf Minuten und prüfe anschließend Upload und Upstream-Status wie in Abschnitt 5.6 beschrieben. |

Ein Problem mit Upstream-Daten verändert, was die ausgewählte Quelle liefert. Ein Problem des Versuchsdesigns verändert, ob die beibehaltenen Zeilen die beabsichtigte Frage beantworten. Diagnostiziere und dokumentiere beides getrennt.

<a id="sec-6-3"></a>

#### 5.3 Rufzeichen und Locator prüfen

Rufzeichen werden in Compare exakt zugeordnet. Das Target-Matching in Success ist strenger: exaktes Rufzeichen plus die ersten vier Zeichen des konfigurierten QTHs. Lädt ein Target `JN37` hoch, während die Konfiguration `JN38` enthält, erfüllt es die Target-Bedingung von Success nicht.

Peer-Identitäten bestehen aus dem exakten Rufzeichen plus der vollständig gemeldeten Locator-Zeichenfolge. Falsche, veraltete oder wechselnde Locator-Angaben können eine physische Station aufteilen, in das falsche Segment verschieben oder den Filter für bewegliche Stationen auslösen.

<a id="sec-6-4"></a>

#### 5.4 Fallback für historische Decode-Codes

WSPRadar fragt für WSPR-2-Evidenz zunächst Zeilen mit `code = 1` ab. Liefert die strenge Abfrage keine Target-seitige Evidenz, wird sie aus Gründen der historischen Kompatibilität ohne dieses Prädikat wiederholt; der Fallback wird im Laufstatus gemeldet.

Der Fallback erweitert die Auswahl. Das aktuelle Exportpaket hält weder den effektiv verwendeten Decode-Filter noch den Fallback-Zustand fest. Bewahre deshalb den gemeldeten Laufstatus in den Versuchsnotizen auf – insbesondere, weil Compare und Success unterschiedliche Wege nehmen können.

<a id="sec-6-5"></a>

#### 5.5 Wie das Target-Active Gate die Evidenz prägt

Das Target-Active Gate beschränkt simultane Vergleiche auf Zyklen, in denen eine Beteiligung des Targets beobachtbar ist. Referenz-Evidenz außerhalb dieser Zyklen wird ausgeschlossen, damit bekannte Ausfallzeiten des Targets nicht automatisch als Misserfolg gewertet werden.

Ist die Target-Station beispielsweise über Nacht abgeschaltet, werden Referenz-Spots aus diesen Offline-Stunden nicht als Misserfolge der Target-Seite gezählt. Innerhalb der beibehaltenen Zyklen müssen die Verfügbarkeit der Referenz und die Verfügbarkeit des Funkwegs weiterhin anhand des Versuchskontexts belegt werden.

Da das Gate bewusst Target-zentriert ist, kann ein Tausch von Target und Referenz die qualifizierenden Zyklen und Decode Outcomes verändern. Sequenzielles TX Hardware A/B verwendet anstelle desselben simultanen Gates seine deterministische Methode geplanter Paare.

Die genauen Zulässigkeitsregeln und die Target-zentrierte Asymmetrie sind in [Abschnitt 7.3](#sec-7-3) definiert.

<a id="sec-6-6"></a>

#### 5.6 Umgang mit Upstream-Daten

wspr.live weist darauf hin, dass seine Daten von WSPRnet gemeldete Rohdaten sind und Duplikate, falsche Spots sowie andere Fehler enthalten können. Die ehrenamtlich betriebene Infrastruktur bietet keine Gewähr für Richtigkeit, Verfügbarkeit oder Stabilität. <a href="#ref-10">[Ref-10]</a>

Nach Angaben von wspr.live stehen Echtzeitdaten mit einigen Minuten Verzögerung bereit; der Scraper prüft alle paar Minuten auf neue Spots. Als praktische Faustregel solltest du nach dem letzten WSPR-Zyklus ungefähr **fünf Minuten** warten, bevor du erwartest, dass ein aktuelles Analysefenster hinreichend gefüllt ist.

Fünf Minuten sind keine Vollständigkeitsgarantie. Verzögerte Uploads, Unterbrechungen der Datenübernahme und spätere Korrekturen können erst danach erscheinen. <a href="#ref-10">[Ref-10]</a>

WSPRadar verwendet Paarbildung, Gruppierung nach Identitäten, Mediane, Schwellen und Drill-Down, um die Empfindlichkeit gegenüber einzelnen fehlerhaften Zeilen zu verringern und deren Prüfung zu erleichtern. Wiederholt auftretende, plausibel wirkende Fehler können trotz dieser Maßnahmen erhalten bleiben.

Gemeldete Leistung und Locator-Angaben stammen von den Nutzern. Auch mathematisch korrekte Berechnungen bleiben physikalisch falsch, wenn Leistung oder Locator falsch angegeben wurden.

**System Audit Status lesen**

Der System Audit Status nennt die Datenbankquelle einmal für den vollständigen Lauf. Als Grund erscheint `primary`, wenn die Quelle mit der höchsten Priorität ausgewählt wurde, `cache affinity`, wenn eine geführte Demo vor der normalen netzwerkgestützten Provider-Auswahl ein vollständiges frisches Bündel einer Quelle mit niedrigerer Priorität auswählte, `capacity spillover`, wenn eine betriebsbereite Quelle mit niedrigerer Priorität den vollständigen Anfrageblock aufnehmen konnte, die Anfragekapazität höher priorisierter Quellen jedoch nicht, `failure fallback`, wenn dieser Lauf nach einem providerbezogenen Fehler neu begann oder eine höher priorisierte Quelle bereits wegen Provider-Cooldown oder Recovery-Probe nicht verfügbar war, oder `committed source`, wenn ein erneutes Rendern die bereits festgelegte Quelle des Laufs beibehielt.

Anschließend werden `database request`, `RAM cache` oder `disk cache` samt Dauer getrennt für jede strenge Abfrage und den optionalen historischen Fallback gemeldet. Diese Bereitstellungsangaben beschreiben, wie die Zeilen zur Analyse gelangten; sie bezeichnen weder unterschiedliche Datenbanken noch ändern sie den Grund der Quellenauswahl.

Auf derselben Bereitstellung kann eine geführte Demo rohe Abfragezeilen des Providers bis zu 24 Stunden nach dem ursprünglichen Abruf wiederverwenden. Vor einer neuen Demo-Abfrage bevorzugt WSPRadar die erste konfigurierte Quelle, für die das gesamte benötigte Demo-Bündel bereits im Cache liegt. Die zwischengespeicherten Zeilen behalten ihre tatsächliche Provider-Herkunft und werden niemals mit Zeilen anderer Provider kombiniert. Cache-Treffer verlängern diese Frist nicht. Ein Prozessneustart verwirft die RAM-Stufe, die Disk-Stufe bleibt bei erhaltenem lokalen Speicher jedoch wiederverwendbar; eine Speicherbereinigung kann sie früher entfernen.

<div style="page-break-before: always;"></div>

<a id="part-iii"></a>
## Teil III: Wissenschaftliche Grundlagen, Methoden und Aussagen

Dieser Teil ordnet WSPRadar in seine wissenschaftliche und amateurfunktechnische Entwicklungslinie ein und legt anschließend exakt fest, wie die Anwendung Evidenz aufbaut, zusammenfasst, interpretiert und sichert. Er unterstützt Methodenprüfung, Audit und belastbare Berichterstattung; für die praktische Arbeit mit der Anwendung bleiben die Versuchsleitfäden und Kapitel zur Ergebnisinterpretation der direkte Einstieg.

<a id="sec-d"></a>
### 6. Literatur, Vorarbeiten und Einordnung

Dieses Kapitel erläutert, welche Ideen WSPRadar übernimmt, integriert und weiterentwickelt. Es stellt den nützlichen Beitrag jeder Quelle ebenso heraus wie die Grenzen dessen, was die jeweilige Quelle belegt. Es behauptet nicht, dass die Literatur jede Kennzahl oder Implementierungsentscheidung von WSPRadar validiert.

<a id="sec-d-1"></a>
#### 6.1 Vom Meldenetz zum Versuchsdatensatz

Taylor und Walker stellten WSPRnet nicht nur als Live-Karte, sondern auch als Archiv vor: „The WSPRnet database represents a rich source of experimental data for propagation studies.“ Ihr Beispiel gruppiert Beobachtungen über mehrere Wochen nach Tageszeit. Es zeigt sowohl den Wert gesammelter Meldungen als auch die Notwendigkeit, sie als Beobachtungsdaten zu interpretieren. <a href="#ref-6">[Ref-6]</a>

Frissell et al. ordnen WSPRNet zusammen mit dem Reverse Beacon Network und PSKReporter als etablierte Amateurfunk-Beobachtungsnetze ein, die „rich, ever-growing, long-term data of bottomside ionospheric observations“ liefern. Sie unterscheiden diese etablierten Netze von neueren, gezielt für Citizen Science aufgebauten Netzen und empfehlen eine Kreuzkalibrierung zwischen Instrumentennetzen. Der Übersichtsartikel stützt den wissenschaftlichen Wert von Amateurfunkbeobachtungen; er macht jedoch nicht jeden einzelnen Empfänger zu einem kalibrierten Messgerät. <a href="#ref-7">[Ref-7]</a>

Das öffentliche WSPR-Archiv ist daher außerordentlich leistungsfähig, bleibt aber eine von unterschiedlich ausgestatteten, ehrenamtlich betriebenen Stationen erzeugte Aufzeichnung erfolgreicher Decodes. Historische Tiefe und geografische Reichweite beseitigen weder Auswahleffekte und Identitätsfehler noch wechselnde Ausrüstung oder unbekannte Betriebspläne.

<a id="sec-d-2"></a>
#### 6.2 WSPR-Beobachtungsdaten interpretierbar machen

<a id="sec-d-lo"></a>
Lo et al. untersuchten mit WSPR-Beobachtungen auf 7 MHz die Greyline-Ausbreitung und warnten ausdrücklich: „There is no official recording of the operating schedules for WSPR equipment.“ Bevor sie fehlende Verbindungen als Ausbreitungsverhalten interpretierten, prüften sie, ob ein Sender irgendwo gehört worden war beziehungsweise ob ein Empfänger irgendeine Station gehört hatte. Außerdem betonten sie die Konsistenz von Rufzeichen und Standort sowie die Nutzung mehrerer Standorte. <a href="#ref-9">[Ref-9]</a>

Dieses Aktivitätsprinzip ist eine direkte methodische Vorarbeit für das Target-Active Gate von WSPRadar: Funkstille sollte erst dann zu Gegen-Evidenz werden, wenn der Betrieb beobachtbar ist. Lo et al. definieren jedoch weder das exakte asymmetrische Gate von WSPRadar noch dessen Success-Nenner oder Decode Outcomes. Diese bleiben WSPRadar-Designentscheidungen für eine andere Zielgröße.

<a id="sec-d-3"></a>
#### 6.3 Wissenschaftliche Vorarbeiten zu Antennen- und Stationsvergleichen

<a id="sec-d-toledo"></a>
**Toledo (2010): Warum langsames Abwechseln scheitert.** Sivan Toledo erprobte ungefähr eine Stunde lang eine Antenne und anschließend eine andere. Dabei änderte sich das SNR des Ausbreitungswegs in derselben Größenordnung wie die scheinbaren Antennenunterschiede. Sein Fazit war unmissverständlich: „Clearly, you can't compare antennas using WSPR using the naive technique that I was using.“ Als belastbarere Versuchsdesigns nannte er die Umschaltung in jedem Zyklus und simultane Aussendungen mit getrennter Hardware. Aus diesem praktischen Grund verwendet WSPRadar deterministische, abwechselnde TX-A/B-Zeitpläne statt langer Blöcke und bevorzugt den kürzesten praktikablen zeitlichen Abstand. Ein kurzer Abstand verringert zeitliche Konfundierung, kann sie aber nicht vollständig beseitigen. <a href="#ref-3">[Ref-3]</a>

<a id="sec-d-milazzo"></a>
**Milazzo (2011): Ein früher, von einer Funkamateurin durchgeführter End-to-End-Vergleich.** Carol Milazzo verglich zwei 29 km voneinander entfernte Stationen über einen gemeinsamen Empfänger in 1.750 km Entfernung. Sie korrigierte die gemeldeten SNR-Werte um Unterschiede der Sendeleistung, verglich den Verlauf mit VOACAP, berücksichtigte unterschiedliche Tastgrade und untersuchte auch reziproke RX-Meldungen. Ihre erste Schlussfolgerung lautete: „The WSPR network data permitted a comparison of signals from two antennas to a distant destination.“ Dies ist eine ungewöhnlich vollständige frühe Amateurfunk-Fallstudie und der früheste ausführliche Vergleich, der in diesem Handbuch berücksichtigt wird. Ein Anspruch, die erste Arbeit gewesen zu sein, ist damit nicht verbunden: Milazzo selbst verweist auf mehrere frühere WSPR-Antennenversuche. Unterschiedliche QTHs, Hardware und lokale Störpegel, nur ein ausgewählter entfernter Empfänger sowie das Fehlen einer formalen Unsicherheitsanalyse begrenzen die kausale Aussage. <a href="#ref-4">[Ref-4]</a>

<a id="sec-d-griffiths-squibb"></a>
**Griffiths und Squibb (2017): RX-Vergleich desselben Signals als Stationsdiagnose.** Für zwei Empfänger an getrennten QTHs behielten sie „only those reports of the same station at the same time selected for analysis“ bei und untersuchten den SNR-Unterschied in Abhängigkeit von Bodenfeuchte, Zeit, Entfernung und Änderungen an der Station. Die Arbeit zeigt, wie gepaarte WSPR-Daten das gesamte Empfangssystem diagnostizieren und Effekte sichtbar machen können, die reine Spot-Anzahlen verdecken. Da sich Antennen, QTHs, Störpegel und Ausrüstung unterschieden, stützt sie vergleichende Stationsevidenz, nicht jedoch kalibrierten Antennengewinn oder eine einzelne kausale Erklärung. <a href="#ref-5">[Ref-5]</a>

<a id="sec-d-vanhamel"></a>
**Vanhamel, Machiels und Lamy (2022): Konditioniertes simultanes RX.** In ihrer begutachteten Studie heißt es, dass „two identical 160-m band WSPR receiver stations are conditioned to compare the performance of different 160-m band antennas.“ Anschließend vergleicht ein kalibrierter Zweiempfängeraufbau gemeinsame entfernte Aussendungen simultan. Innerhalb dieser Quellenauswahl ist dies die stärkste direkte Vorarbeit für den RX Hardware A/B-Test und für die Charakterisierung von Unterschieden zwischen Empfangsketten vor einem Antennenvergleich. Ihr Ausbreitungsversuch zeigt außerdem, dass Polarisation und ionosphärische Effekte das gemeldete SNR verändern können. Selbst ein sorgfältig konditionierter Aufbau ergibt deshalb keine einzelne, kontextfreie Antennenkennzahl. <a href="#ref-2">[Ref-2]</a>

<a id="sec-d-zander"></a>
**Zander (2022): Ein mathematisches Modell für simultanen TX-Vergleich.** Zander untersucht zwei lokale Antennen, die im selben WSPR-Zyklus von getrennten, nominell leistungsgleichen Sendern mit unterschiedlichen Rufzeichen gespeist werden. Ein Empfänger wird nur berücksichtigt, wenn beide Signale „reported by the same station in the same time interval“ sind. Unter den Modellannahmen zeitgleicher Aussendungen, eines gemeinsamen Ausbreitungswegs und gleicher Sendeleistung heben sich gemeinsame Pfaddämpfung und Empfängerrauschen in der SNR-Differenz auf; getrennte schmalbandige Störungen, fehlgeschlagene Decodes und die ganzzahlige SNR-Quantisierung bleiben bestehen. Da jede Differenz innerhalb desselben entfernten Empfängers gebildet wird, gilt: „the method does not require any receiver calibration“. Gleiche beziehungsweise korrigierte Leistungen der beiden Sender bleiben dennoch erforderlich. <a href="#ref-1">[Ref-1]</a>

In jedem Vorversuch sammelte Zander ungefähr 1.000 Meldungen in rund einer Stunde und behielt davon 150–200 Joint-Meldungen aus 15–35 Empfangsstationen bei. Die beobachtete Stichproben-Standardabweichung lag nahe 3 dB; für ungefähr 100 nutzbare Einzelbeobachtungen schätzt die Arbeit die Standardabweichung des arithmetischen Mittels auf unter 0,5 dB. Anschließend nennt sie eine „accuracy of less than a dB“ innerhalb weniger Stunden. Wissenschaftlich belegt diese Rechnung Wiederholbarkeit beziehungsweise Präzision unter den Annahmen des Modells, nicht eine metrologisch rückführbare Gesamtgenauigkeit: Die Arbeit benennt gesondert Verzerrungen durch die geografische Verteilung der Empfänger, Richtwirkung und unbekannte Elevationswinkel. Lange Läufe verringern zufällige Belegungs- und Kollisionseffekte, nicht aber diese systematischen Einflüsse. Die Studie stützt simultanes Delta SNR innerhalb desselben Empfängers deutlich; sie validiert weder das sequenzielle Ein-Sender-TX-A/B von WSPRadar noch stationsgleichgewichtete Mediane, Decode Outcomes oder andere Benchmark-Designs.

<a id="sec-d-4"></a>
#### 6.4 Analyseinfrastruktur und Werkzeuge für Funkamateure

Griffiths und Robinett zeigten, wie eine relationale Zeitreihendatenbank einen Self-Join für den „same sender at the same time in the same band for two different reporters“ ermöglicht. Ihre Grafana-Beispiele kombinieren Scatterplots der SNR-Differenz, Mediane, Quartile, Zeit-Heatmaps, Entfernungs- und Azimutansichten sowie Datenexport. Dies ist eine wichtige Vorarbeit für prüfbare Vergleichsinfrastruktur, nicht jedoch für die exakten Qualifizierungsregeln, Nenner oder Schätzer von WSPRadar. <a href="#ref-13">[Ref-13]</a>

WSPR.Rocks ermöglicht die schnelle Erkundung von WSPR-Daten mit SQL-Zugriff, Karten, Tabellen, SpotQ und weiteren Analysen. WSPRadar unterscheidet sich dadurch, dass der Arbeitsablauf auf ausdrücklichen Versuchsdesigns, Paarbildung und einem Audit bis auf Zeilenebene statt auf einer Rangliste beruht. <a href="#ref-14">[Ref-14]</a>

WSPRdaemon konzentriert sich auf robuste Erfassung mit mehreren Empfängern, Zeitplanung und zusätzliche Rausch-/Doppler-Metadaten. Dies verdeutlicht, weshalb Erfassungsstabilität und Rauschkontext für RX-Analysen wichtig sind. <a href="#ref-11">[Ref-11]</a>

SOTABEAMS WSPRlite und DXplorer bieten leicht zugängliche WSPR-basierte Antennen-/Standortvergleiche sowie die Kennzahl DX10. <a href="#ref-15">[Ref-15]</a>

WSPR-Station-Compare stellt ausdrücklich einen Bezug zwischen Software für Stationsvergleiche und den Methoden von Vanhamel und Zander her. <a href="#ref-16">[Ref-16]</a>

Das Antenna Performance Analysis Tool ist ein weiterer nutzerorientierter Dienst zur Auswertung von WSPR-Antennenmeldungen. Schon seine Existenz schließt die Behauptung aus, WSPRadar sei das erste Werkzeug zur WSPR-Antennenanalyse. <a href="#ref-17">[Ref-17]</a>

WATT bietet Berichte, Kartendarstellung, Filter und Zeitleistenanalyse mit Excel/VBA und unterstreicht damit den praktischen Wert prüfbarer Daten gegenüber einer einzelnen starren Kennzahl. <a href="#ref-18">[Ref-18]</a>

Diese Werkzeuge belegen umfangreiche Vorarbeiten bei Erfassung, Datenexploration, Rangbildung, Visualisierung und Antennenberichten. Sie sind Teil der Entwicklungslinie von WSPRadar und keine Schwäche seiner Einordnung.

<a id="sec-d-5"></a>
#### 6.5 Was WSPRadar übernimmt, integriert und ergänzt

WSPRadar übernimmt wichtige Ideen, statt die Erfindung des WSPR-Vergleichs für sich zu beanspruchen: Für gesammelte Beobachtungen, Aktivitätsprüfungen, Korrektur anhand der gemeldeten Sendeleistung, Paarbildung unter gemeinsamen Bedingungen, kalibrierte Empfangsketten, geografische und zeitliche Ansichten sowie Datenbank-Joins gibt es jeweils klare Vorarbeiten.

WSPRadar führt diese Ideen in einem Arbeitsablauf für Funkamateure zusammen. Dieser umfasst:

* TX- und RX-Analyse mit den Designs `Kein Benchmark (nur Success)`, `Hardware A/B-Test (Eigenes Setup)`, `Fremdes Rufzeichen (Buddy-Test)` und `Lokaler Nachbarschafts-Benchmark`;
* Prüfungen der Target-Aktivität, Vergleiche im selben Zyklus oder anhand deterministischer geplanter Paare, SNR-Normierung anhand der gemeldeten Sendeleistung sowie eine optionale Referenz-SNR-Korrektur;
* bedingte Success-Evidenz, gepaartes Delta SNR und kategorische Decode Outcomes als getrennte Evidenzfragen;
* Karten, Segment-Inspektor, Station Insights, Zeit-/Sonnenstandsansichten und Drill-Down bis auf Zeilenebene;
* Evidenzschwellen, vergleichende Diagnosen auf Stations- und Beobachtungsebene sowie deskriptive Stability-Prüfungen;
* geführte Demos, versionierte Konfigurationen, Laufmetadaten, verarbeitete Evidenz, Tabellen, Abbildungen und praktische Ergänzungen.

Innerhalb der hier geprüften Literatur und Werkzeuge sind die deutlichsten WSPRadar-spezifischen Ergänzungen:

* das bedingte Success-Opportunity-Modell mit ausdrücklich definierter Gegen-Evidenz im Nenner;
* die ausdrückliche Trennung des gepaarten Delta SNR von den Decode Outcomes `Joint`, `Only Target`, `Only Reference` und `Both (Async)`;
* der dynamische Aufbau der Benchmarks Lokaler Nachbarschafts-Median und Beste lokale Station;
* die hierarchische, stationsgleichgewichtete geografische Aggregation, einschließlich genau eines Beitrags je lokaler Station, bevor ein Lokaler Nachbarschafts-Median gebildet wird;
* die parallele Zusammensetzung nach `STATIONS` und `SPOTS` auf jeder Compare-Karte;
* ein integrierter Prüfpfad von der Karte über Segment und Station bis zur einzelnen Zeile;
* ein Reproduzierbarkeitspaket, das an den abgeschlossenen Lauf und die aktuellen Inspektor-Auswahlen gebunden ist.

Dies ist eine begrenzte Einordnung, kein globaler Prioritätsanspruch. Die Medianaggregation selbst ist nicht neu; der Beitrag liegt in ihrer stationsgleichgewichteten Anwendung innerhalb des vollständigen Versuchs- und Inspektionsablaufs. Der besondere Wert von WSPRadar ist die durchgängige Integration und Zugänglichkeit für WSPR-Anwender im Amateurfunk – nicht die Behauptung, das erste Vergleichswerkzeug zu sein oder kalibrierte Antennenmessungen zu liefern.

WSPRadar sollte nicht als Ersatz für wspr.live, WSPR.Rocks, WSPRdaemon, DXplorer oder kontrollierte HF-Messtechnik beschrieben werden. Methodisch arbeitet es eine Ebene oberhalb eines Spot-Browsers: **Welche Beobachtungen sind für diesen Versuch qualifizierend, welcher gepaarte Unterschied wurde beobachtet, welche einseitige Evidenz bleibt bestehen und lässt sich die Schlussfolgerung prüfen?**

<a id="sec-7"></a>
### 7. Wissenschaftliche Methoden

WSPRadar überführt öffentliche WSPR-Decodes in klar definierte Vergleichseinheiten und fasst diese anschließend so zusammen, dass eine einzelne sehr aktive Station das stationsgleichgewichtete Ergebnis nicht dominieren kann. Dieses Kapitel ist die maßgebliche Stelle für Formeln, Zuordnungsregeln, Zulässigkeitsbedingungen und Aggregation.

**Methodischer Überblick**

| Analysedesign | Target-Rolle | Referenz oder Gegen-Evidenz | Kleinste Beobachtungs-/Vergleichseinheit | Aktivitätsbedingung | Zeitlicher Bezug | Leistungsnormierung | Aggregation auf Stationsebene | Aggregation auf Segmentebene | Wichtigste Interpretationsgrenze |
|---|---|---|---|---|---|---|---|---|---|
| Kein Benchmark (nur Success), RX oder TX | Target-Empfänger oder -Sender | RX: derselbe Sender andernorts decodiert; TX: anderes Signal im selben Band vom Peer-Empfänger decodiert | ein Target-aktiver Peer-Zyklus | beobachtbare Target-Beteiligung | derselbe zweiminütige Zyklus | Rate: keine; Anzeige des erfolgreichen Target-SNR: auf gemeldete 1 W normiert | eine Success Rate pro Peer | arithmetisches Mittel der Peer-Raten; gepoolte Rate bleibt erhalten | bedingte Reichweite im Netzwerk, keine unbedingte Decode-Wahrscheinlichkeit |
| Hardware A/B-Test, RX | Empfänger von Setup A | simultaner Empfänger von Setup B | ein konsolidierter Peer-Zyklus des entfernten Senders | Target-Active Gate | derselbe Sender und Zyklus | gemeinsame TX-Leistung fällt heraus; Korrektur gilt für Setup B | Median des Delta SNR | Median der Stationsmediane | kontrollierte lokale Empfangspfade nur in dem Maß, in dem die übrigen Ketten kontrolliert sind |
| Hardware A/B-Test, TX | geplante Starts von Setup A | geplante Starts von Setup B | eine Peer-Identität in einem geplanten Target-/Referenzpaar | deterministische, überschneidungsfreie Zeitpläne; kein simultanes Gate | nächstgelegene Eins-zu-eins-Paarung der Starts innerhalb eines gemeinsamen Wiederholintervalls | beide Seiten auf gemeldete 1 W normiert; Korrektur gilt für Setup B | Median des Delta SNR der geplanten Paare | Median der Stationsmediane | sequenziell, nicht simultan; Zeitplan- und Schalteffekte bleiben bestehen |
| Fremdes Rufzeichen (Buddy-Test), RX | Target-Empfänger | externer Referenzempfänger | ein konsolidierter Peer-Zyklus des entfernten Senders | Target-Active Gate; Referenz-Betriebszeit extern kontrolliert | derselbe Sender und Zyklus | gemeinsame TX-Leistung fällt heraus; Korrektur gilt für die Referenz | Median des Delta SNR | Median der Stationsmediane | vollständig aufgebaute Stationen und Umgebungen, nicht isolierte Empfängerempfindlichkeit |
| Fremdes Rufzeichen (Buddy-Test), TX | Target-Sender | externer Referenzsender | ein konsolidierter Peer-Zyklus des entfernten Empfängers | Target-Active Gate; Referenz-Betriebszeit extern kontrolliert | derselbe Empfänger und Zyklus | beide Seiten auf gemeldete 1 W normiert; Korrektur gilt für die Referenz | Median des Delta SNR | Median der Stationsmediane | vollständig aufgebaute Stationen; abhängig von der Genauigkeit der gemeldeten Leistung |
| Lokaler Nachbarschafts-Median | Target RX oder TX | Zyklus-/Pfadmedian aus je einem Beitrag pro aktivem lokalem `callsign + locator` | ein Peer-Zyklus aus Target und lokaler Referenz | Target-Active Gate | derselbe Peer-Pfad und Zyklus | TX-Werte auf gemeldete 1 W normiert; Korrektur vor Bildung des lokalen Medians | Median des Delta SNR | Median der Stationsmediane | dynamischer, unkalibrierter Pool; Ergebnis hängt von Radius und aktiver Zusammensetzung ab |
| Beste lokale Station | Target RX oder TX | stärkste qualifizierende lokale Station für diesen Zyklus/Pfad | ein Peer-Zyklus aus Target und bester Referenz | Target-Active Gate | derselbe Peer-Pfad und Zyklus | TX-Werte auf gemeldete 1 W normiert; Korrektur vor Auswahl der besten Station | Median des Delta SNR | Median der Stationsmediane | wechselnde Hüllkurve des besten Peers, weder lokaler Durchschnitt noch feste Referenz |

Die Matrix dient der Orientierung. Maßgeblich sind die nachfolgenden Definitionen, Formeln und Verarbeitungsschritte.

<a id="sec-7-1"></a>
#### 7.1 Datenquelle, Decode-Auswahl und Zeitmodell

WSPRadar liest die öffentliche Tabelle `wspr.rx` über die ausgewählte schreibgeschützte ClickHouse-HTTP-Schnittstelle. Spots sind Beobachtungsdatensätze unabhängig betriebener Sender, Empfänger, Software und Netzwerke. Sie sind keine randomisierte oder kalibrierte Stichprobe möglicher Funkwege. Decode-Auswahl, historischer Fallback und das Verhalten bei vorgelagerten Datenproblemen sind einmalig in den [Abschnitten 5.4-5.6](#sec-6-4) dokumentiert.

Die gewählten UTC-Endpunkte werden beim Start des Laufs aufgelöst und anschließend zur Wiederverwendung der Abfrage beide auf 15-Minuten-Grenzen abgerundet. Success verwendet ein halboffenes Intervall, `start <= time < end`: Eine Beobachtung genau am quantisierten Start ist zulässig, eine Beobachtung genau am quantisierten Ende dagegen ausgeschlossen. Compare verwendet derzeit in der Datenbank `BETWEEN` und kann daher eine Beobachtung exakt am quantisierten Start wie auch am quantisierten Ende einschließen. Eine Beobachtung auf der Intervallgrenze kann folglich in Compare, nicht aber in Success erscheinen; benachbarte Compare-Fenster können sich außerdem den exakten Endpunkt teilen.

Ein **WSPR-Zyklus** ist das zweiminütige Intervall, das an einer geraden UTC-Minute beginnt. WSPRadar leitet simultane Zyklen aus den Spot-Zeitstempeln ab. Beim sequenziellen TX-A/B bleiben die Zeitstempel dagegen erhalten; zugelassen werden nur Starts, die dem konfigurierten Modulo-Zeitplan des jeweiligen Pfades entsprechen, und jedem Spot werden die geplanten Target- und Referenz-Starts seines nächstgelegenen Eins-zu-eins-Startpaares zugeordnet. Ein geplantes Paar ist nur zulässig, wenn beide geplanten Starts innerhalb des gewählten Vergleichsfensters liegen.

<a id="sec-7-2"></a>
#### 7.2 Identitäts- und Zuordnungsregeln

WSPRadar behält die gemeldete Identität als Bestandteil der Evidenz bei. Rufzeichenvarianten und gemeldete Locator sind deshalb wissenschaftlich relevante Eingaben und keine bloßen Beschriftungen.

| Analyse | Target-Zuordnung | Peer-/Referenzidentität | Kleinste Ergebniseinheit |
|---|---|---|---|
| RX Success | exaktes RX-Rufzeichen plus Grid-4 des Target-QTH | TX-Rufzeichen + gemeldeter TX-Locator | ein Target-aktiver Peer-Zyklus |
| TX Success | exaktes TX-Rufzeichen plus Grid-4 des Target-QTH | RX-Rufzeichen + gemeldeter RX-Locator | ein Target-aktiver Peer-Zyklus |
| Simultanes Compare | exakte Target- und Referenzrufzeichen | entferntes Rufzeichen + gemeldeter Locator | ein konsolidierter Peer-Zyklus |
| Sequenzielles TX-A/B | exaktes Target-Rufzeichen, aufgeteilt nach konfiguriertem UTC-Zeitplan | RX-Rufzeichen + gemeldeter Locator | ein geplantes Target-/Referenzpaar |
| Lokaler Referenzpool | exaktes lokales Rufzeichen + Locator innerhalb des Radius | entfernter Peer wie oben | ein Beitrag je lokaler Identität pro Zyklus/Pfad |

Rufzeichen werden in Compare exakt abgeglichen. Die Target-Zuordnung in Success ist strenger: Sie verwendet das exakte Rufzeichen zusammen mit den ersten vier Zeichen des Locators des konfigurierten QTH. Sendet ein Target `JN37`, während die Konfiguration `JN38` vorgibt, erfüllt es die Target-Bedingung von Success nicht.

Peer-Identitäten bestehen aus dem exakten Rufzeichen und der vollständig gemeldeten Locator-Zeichenfolge. Falsche, veraltete oder wechselnde Locator können eine physische Station auf mehrere Identitäten aufteilen, sie einem falschen Segment zuordnen oder den Filter für bewegliche Stationen auslösen.

Mehrere qualifizierende Zeilen für eine Seite eines normalen simultanen Peer-Zyklus werden konsolidiert; das höchste normierte SNR repräsentiert diese Seite. Beim lokalen Nachbarschafts-Median wird stattdessen zunächst innerhalb jeder lokalen Identität der Median und anschließend über die lokalen Identitäten hinweg erneut der Median gebildet.

Der lokale Pool schließt das Target anhand des exakten Rufzeichens aus. Ein Basisrufzeichen und ein Rufzeichen mit Suffix sind daher unterschiedliche Identitäten, sofern nicht die exakte Target-Form übereinstimmt. Jeder lokale Beitrag behält seinen gemeldeten Locator als Bestandteil der Identität bei.

<a id="sec-7-3"></a>
#### 7.3 Target-Active Gate

Das Target-Active Gate verankert Success und simultanes Compare in Zyklen, in denen eine Beteiligung des Targets beobachtbar ist:

* **TX:** Im Zyklus existiert irgendwo mindestens ein qualifizierender Spot einer Target-Aussendung.
* **RX:** Im Zyklus existiert mindestens ein qualifizierender Decode, den der Target-Empfänger hochgeladen hat.

Das Gate verhindert, dass bekannte Ausfallzeiten des Targets automatisch als Misserfolg gewertet werden. Referenz-Spots aus Stunden, in denen die Target-Station ausgeschaltet war, zählen beispielsweise nicht als Niederlagen.

Die Asymmetrie ist beabsichtigt: Ohne maßgebliche Betriebspläne definiert WSPRadar Success und simultanes Compare ausgehend vom festgelegten Target und lässt nur Zyklen mit beobachtbarer Target-Beteiligung zu. Bei Compare bildet die Betriebszeit der Referenz kein zweites Gate und muss daher von der experimentierenden Person kontrolliert werden.

Da jede Joint-Beobachtung bereits eine Target-Beteiligung belegt, beeinflusst die Asymmetrie des Gates ausschließlich einseitige oder asynchrone Decode Outcomes sowie die Gegen-Evidenz im Nenner der Success Rate; das Gate selbst verändert reine Joint-Zusammenfassungen des Delta SNR nicht.

Ein Tausch von Target und Referenz kann deshalb die zulässigen Zyklen und Decode Outcomes verändern. Sequenzielles TX-A/B verwendet statt dieses simultanen Gates eine deterministische Zeitplanzuordnung und geplante Paare. Die rollenunabhängige Gleichstandsregel beim halben Intervall erhält beim Tausch von A/B dieselben physischen Paare.

<a id="sec-7-4"></a>
#### 7.4 Success-Klassifikation und Formeln

Success misst die bedingte Reichweite des Targets unter Opportunities, für die unabhängige Evidenz einer Netzaktivität vorliegt.

WSPRadar erfasst für jeden Target-aktiven Peer-Zyklus Target-Evidenz und unabhängige externe Evidenz:

* **Externe RX-Evidenz:** Ein anderer Empfänger meldete im selben Zyklus dieselbe Senderidentität.
* **Externe TX-Evidenz:** Der Peer-Empfänger meldete im selben Zyklus einen anderen Sender im selben Band als das Target.

`Target` bezeichnet den Fall, dass sowohl Target- als auch externe Evidenz vorliegt. `Elsewhere` / `Other Signals` bezeichnet externe Evidenz ohne Target. `Target-only` bezeichnet Target-Evidenz ohne externe Evidenz und bleibt vom Nenner ausgeschlossen.

$$\text{Success Rate}_{RX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Elsewhere}}$$

$$\text{Success Rate}_{TX} = 100\% \times \frac{\text{Target}}{\text{Target} + \text{Other Signals}}$$

Die zulässige Peer-Population wird nach Anwendung von Band, Zeit, Gate, Filtern und Schwellen aus dem globalen Netz gewonnen. Die Success Rate ist damit durch beobachtbare Netzaktivität und Ausbreitungsbedingungen bedingt. Sie ist weder eine Schätzung aller Sendeversuche noch eine kalibrierte Detektionswahrscheinlichkeit des Empfängers.

Die Klassifikation der Success Rate selbst wird nicht leistungsnormiert. Das daneben angezeigte SNR erfolgreicher Target-Evidenz wird auf die gemeldete Leistung von 1 W normiert.

<a id="sec-7-5"></a>
#### 7.5 Leistungsnormierung, Korrektur und Delta SNR

Die Leistungsnormierung bringt erfolgreiche TX-Evidenz auf eine gemeinsame Basis der gemeldeten Leistung. Das WSPR-SNR wird vom Decoder in dB auf der WSJT-Skala gemeldet, bezogen auf eine Bandbreite von 2500 Hz. WSPR-Nachrichten enthalten die gemeldete Sendeleistung in dBm. <a href="#ref-8">[Ref-8]</a>

WSPRadar normiert erfolgreiches SNR auf die gemeldete Referenzleistung von 1 W / 30 dBm:

$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$

Damit wird der **gemeldete** Leistungsanteil herausgerechnet. Nicht korrigiert werden Antennengewinn, Wirkungsgrad, Speiseleitungsverlust, äquivalente isotrope Strahlungsleistung (EIRP), Empfängerkalibrierung oder lokales Rauschen.

Die Referenz-SNR-Korrektur wird zur Referenzseite addiert:

$$SNR_{reference,corrected} = SNR_{reference} + Correction$$

Die allgemeine Vergleichsdefinition lautet:

$$\Delta SNR = SNR_{target} - SNR_{reference,corrected}$$

Eine positive Korrektur macht die Referenz vor der Subtraktion stärker und senkt damit Delta SNR. Eine negative Korrektur erhöht Delta SNR. Die betroffenen Zweige, das Vorzeichen bei der Eingabe und Hinweise zur Kalibrierung stehen in [Abschnitt 4.3](#sec-5-3) und [Anhang C](#sec-c).

TX-Vergleiche verwenden normiertes SNR, weil unterschiedliche Sendeleistungen beteiligt sein können. Bei RX-Paaren desselben Senders fällt der gemeinsame Leistungsterm heraus. TX-Vergleiche zwischen verschiedenen Rufzeichen hängen unmittelbar von der Genauigkeit der gemeldeten Leistung ab.

<a id="sec-7-6"></a>
#### 7.6 Gepaarte Evidenz und Decode Outcomes

Compare stellt zwei einander ergänzende Sichtweisen auf das Vergleichsergebnis getrennt dar.

1. **Gepaartes Delta SNR:** der bedingte Wert Target minus Referenz, wenn beide Seiten vergleichbare Evidenz erzeugt haben.
2. **Decode Outcomes:** Evidenz der Kategorien Joint, Only Target, Only Reference und Both (Async) außerhalb oder im Umfeld dieser gepaarten Teilmenge.

Diese Trennung ist wichtig, weil eine ausschließlich gepaarte Delta-SNR-Analyse einer Selektionsverzerrung durch die Beschränkung auf erfolgreiche Paare (Survivorship Bias) unterliegt: Beide Seiten müssen vergleichbare Evidenz erzeugen. Ein Aufbau, der viele zusätzliche schwache Signale decodiert, kann gerade deshalb einen niedrigeren gepoolten SNR-Median aufweisen, weil er schwächere Signale erreicht.

Decode Outcomes werden nicht leistungsnormiert. Bei einer exklusiven TX-Beobachtung fehlt das SNR der anderen Seite und lässt sich nicht rekonstruieren. Ungleiche Sendeleistungen können daher exklusive TX-Evidenz dominieren, selbst wenn das gemeinsame Delta SNR normiert ist.

Auf Compare-Karten ordnen die Kategorien unter `STATIONS` Identitäten zu; die Kategorien unter `SPOTS` zählen das Evidenzvolumen. Die Balken auf Success-Karten verwenden dieselben beiden Ebenen, richten sie jedoch am Success-Nenner aus. Ein `Joint Spot` ist eine konsolidierte Vergleichseinheit desselben Zyklus und nicht zwingend eine einzelne unveränderte Datenbankzeile.

<a id="sec-7-7"></a>
#### 7.7 Aggregationshierarchie

WSPRadar berechnet zunächst einen Wert auf Peer-Ebene und daraus anschließend den Wert des geografischen Segments. In stationsgleichgewichteten Zusammenfassungen erhält dadurch jeder qualifizierende Peer dasselbe Gewicht; eine Station mit hohem Datenvolumen kann das Ergebnis nicht allein deshalb dominieren, weil sie mehr Beobachtungen hochgeladen hat.

Mediane verringern die Empfindlichkeit gegenüber einzelnen Extremwerten, duplikatähnlichen Häufungen und Ausreißern des quantisierten SNR. Systematische Kalibrierfehler, Ausbreitungsverzerrungen oder zeitliche und räumliche Korrelationen zwischen Stationen beseitigen sie nicht.

**Success**

1. Jeden Target-aktiven Peer-Zyklus klassifizieren.
2. Target, Gegen-Evidenz und Target-only nach Peer-`callsign + locator` summieren.
3. Den konfigurierten Schwellenwert für `Target+Gegen-Evidenz` verlangen.
4. Für jeden qualifizierenden Peer eine Success Rate berechnen.
5. Für das Segment das arithmetische Mittel der Peer-Raten berechnen.
6. Die gepoolte Rate auf Beobachtungsebene als Diagnosewert beibehalten.

Der stationsgleichgewichtete Wert und der gepoolte Wert auf Beobachtungsebene beantworten unterschiedliche Fragen. Der erste beschreibt die typische qualifizierende Identität bei gleichem Peer-Gewicht; beim zweiten hat jede qualifizierende Beobachtung dasselbe Gewicht.

**Simultanes Compare**

1. Target- und Referenzevidenz nach Zyklus und Peer-Identität konsolidieren.
2. Für Joint-Zyklen Delta SNR berechnen.
3. Für jeden Peer die konfigurierte Mindestanzahl an Joint-Evidenz verlangen.
4. Für jede Station einen Median des Delta SNR berechnen.
5. Für das Segment den Median über die Stationsmediane berechnen.

**Sequenzielles TX-A/B**

1. Spots des exakten Rufzeichens nur dann behalten, wenn ihr UTC-Start dem konfigurierten Target- oder Referenzzeitplan entspricht.
2. Geplante Target- und Referenz-Starts anhand des kleinsten zyklischen Abstands eins zu eins zuordnen und verlangen, dass beide geplanten Starts innerhalb des Vergleichsfensters liegen.
3. Jede Seite nach geplantem Paar und Peer-`callsign + locator` gruppieren.
4. Für jede Seite und jedes Paar einen Mikro-Median berechnen.
5. Das Paar-Delta berechnen, wenn beide Mikro-Mediane vorhanden sind; ein einseitiges Paar als Only Target oder Only Reference beibehalten.
6. Die konfigurierte Mindestanzahl gemeinsamer Paare verlangen.
7. Stations- und Segmentmediane berechnen.

Die beiden Seiten bleiben zeitlich nacheinander. Ein kurzer Abstand und ein ausgewogener Betrieb verringern die Zeitdifferenz gegenüber langen Blöcken, doch Einflüsse von Zeitplan und Umschaltung können bestehen bleiben.

**Lokale Referenz als Nachbarschafts-Median**

1. Jede lokale Referenz mit `callsign + locator` innerhalb eines Zyklus und entfernten Peers gruppieren.
2. Den Median des normierten SNR dieser lokalen Identität berechnen.
3. Dieser Identität unabhängig von der Zahl ihrer wiederholten Zeilen genau einen Beitrag geben.
4. Eine Identität ohne qualifizierende Beobachtung für diesen Zyklus/Pfad auslassen; niemals einen Beitrag von `0 dB` erfinden.
5. Über die beitragenden lokalen Identitäten den exakten Median bilden.
6. Target mit dieser Referenz auf Zyklusebene vergleichen.

Bei einem lokalen Pool mit gerader Anzahl wird der Mittelwert der beiden mittleren Werte verwendet. Die Zusammensetzung des Pools kann sich in jedem Zyklus ändern.

**Lokale Referenz als beste Station**

Für jeden Zyklus und Pfad verwendet Beste lokale Station die stärkste qualifizierende lokale Station als Referenz. Die Referenzkorrektur wird vor der Auswahl der besten Station angewendet. Das Ergebnis ist daher eine wechselnde Hüllkurve des besten Peers und weder ein lokaler Durchschnitt noch eine feste Referenz.

<a id="sec-7-8"></a>
#### 7.8 Stabilität, Verteilungen und Gewichtung in der Inspektionsansicht

WSPRadar verwendet ein deterministisches Perzentil-Bootstrap mit 500 Stichprobenziehungen mit Zurücklegen und gibt das zentrale 90-%-Intervall um den Median an. Intervalle auf Stationsebene ziehen neue Stichproben aus den Stationsmedianen. Intervalle aus den Rohpaaren ziehen neue Stichproben aus den Delta-Werten der Peer-Zyklen oder geplanten Paare.

Die Berechnung behandelt die Werte als austauschbar, obwohl WSPR-Beobachtungen nach Station, Zeit und Geografie korreliert sein können. Es handelt sich um ein deskriptives **Stability**-Intervall, nicht um ein Konfidenzintervall oder einen Signifikanztest.

Compare-Histogramme des Delta SNR verwenden innerhalb eines Panels feste Klassen. Normalerweise sind die Klassen 1 dB breit; 0,5 dB werden nur bei einem deutlichen Halb-dB-Raster verwendet. Große Wertebereiche werden zu Klassen von 1, 2, 3, 6 oder 10 dB zusammengefasst, damit ein Panel höchstens 40 Balken enthält. Ein sichtbarer Mindestbereich von 3 dB verhindert, dass geringe Streuung optisch überhöht wird.

Compare-Zeit-Heatmaps zählen zunächst die Evidenz in Zellen, die aus UTC-Zeit- bzw. gefalteten UTC-Stundenklassen und auf ganzzahlige dB gerundeten Delta-SNR-Klassen gebildet werden. Jedes Panel wird unabhängig skaliert:

$$D_{relative} = 100 \times \frac{n_{cell}}{\max(n_{cell,panel})}$$

Die am dichtesten belegte Zelle erhält damit den Wert `100`, proportional belegte Zellen liegen zwischen `0` und `100`, und leere Zellen bleiben leer. Der Wert ist ein Prozentsatz der maximalen Zellbelegung dieses Panels und kein Anteil an der gesamten Evidenz. Werte und Farben ermöglichen deshalb keinen Vergleich absoluter Evidenzmengen zwischen getrennt normierten Panels. Compare-Zeitverläufe auf Segmentebene und für ausgewählte Stationen verwenden diese Regel; Success-Zeitverläufe behalten ihre dokumentierte Semantik für Success Rate und Anzahlen.

Die vier Compare-Verteilungs- und Zeitpanels verwenden ausschließlich für die Darstellung eine medianzentrierte, nichtlineare Delta-SNR-Skala. Die beiden Zeitpanels des Segments teilen sich den Median aller gepaarten Beobachtungen im ausgewählten Segment. Die Verteilung der ausgewählten Stationen und ihr aktives Zeitpanel teilen sich dagegen den gepoolten Median der aktuell ausgewählten Station bzw. Stationen. Jeder aus zwei Panels bestehende Evidenzbereich hat somit ein gemeinsames Zentrum, während absolute Beschriftungen die Interpretation zwischen den Bereichen erhalten.

Die weißen verbundenen Marker bleiben eine eigene Statistik: Sie zeigen den Median innerhalb jeder belegten Zeitklasse.

`M` sei der exakte Evidenzmedian dieses Bereichs. Bei einem großen Wertebereich liegen äquidistante visuelle Anker bei `M`, `M +/- 3`, `M +/- 6`, `M +/- 10`, `M +/- 20` und `M +/- 30 dB`; ein unbeschrifteter Randanker setzt sich bei `M +/- 60 dB` fort und wird bei Bedarf weiter extrapoliert. Beträgt jede erforderliche Abweichung von `M` höchstens `10 dB`, lauten die engeren sichtbaren Anker `M`, `M +/- 1`, `M +/- 3`, `M +/- 6` und `M +/- 10 dB`; unbeschriftete Anker bei `M +/- 20` und `M +/- 40 dB` definieren die komprimierte Fortsetzung außerhalb dieses sichtbaren Bereichs. Zur erforderlichen Abweichung zählen die Grenzen des Rohhistogramms und der gerundeten Heatmap-Klassen, eine Mindesthalbspanne von 3 dB sowie der absolute Wert `0 dB`, damit Ausläufer und die 0-dB-Referenz Target = Referenz nicht unbemerkt abgeschnitten werden.

Die Skalenbeschriftungen zeigen das resultierende **absolute Delta SNR** und nicht den Abstand von `M`. Beispielsweise ergeben sich für `M = +6 dB` die Beschriftungen der breiten Skala `-24, -14, -4, 0, +3, +6 M, +9, +12, +16, +26, +36 dB`.

Die Transformation verändert weder wissenschaftliche Werte noch Gruppierungen. Anzahlen und Klassengrenzen der Histogramme bleiben in untransformierten dB-Werten, die Zeitzellen bleiben auf ganzzahlige dB gerundete Klassen, Mediane und Stability-Intervalle bleiben Statistiken aus untransformierten dB-Werten, und die Farben der relativen Dichte behalten die oben angegebene Berechnung bei. Weil die nichtlineare vertikale Streckung gleich breiten Roh-dB-Klassen im Histogramm unterschiedliche dargestellte Höhen gibt, ist die **Balkenlänge** auf der Achse `Share (%)` abzulesen; die dargestellte Balkenfläche ist keine Wahrscheinlichkeit. Success-SNR-Diagramme bleiben linear.

Die Diagramme ausgewählter Stationen verwenden die in [Abschnitt 2.6](#sec-3-7) beschriebenen Gewichtungs- und Darstellungsregeln auf Beobachtungsebene; diese Ansichtsoptionen verändern weder Kartenaggregation noch Opportunity-Klassifikation oder Paarbildung.

<a id="sec-7-9"></a>
#### 7.9 Geografie und Sonnenstandsklassifikation

WSPRadar berechnet Entfernung und Azimut mit einem sphärischen Erdradius von 6371 km und stellt die Karte in einer azimutal äquidistanten Projektion mit dem Target-QTH als Mittelpunkt dar. Die radialen Grenzen liegen bei 2500, 5000, 10000, 15000, 20000 und 22000 km; die Azimutsektoren sind 22,5 Grad breit.

Die Kartengeometrie ist in sich konsistent, erreicht aber keine vermessungstechnische Genauigkeit; gemeldete Locator repräsentieren Positionen von Locator-Feldern und keine vermessenen Antennenkoordinaten.

`Lokaler QTH Sonnenstand` verwendet die Sonnenhöhe am Target-QTH. Bei regulärer Evidenz aus demselben Zyklus wird dessen Zeitstempel verwendet. Beim automatischen geplanten TX-A/B wird die Mitte zwischen den beiden geplanten Starts verwendet, damit Target und Referenz eines Paares nicht unterschiedlichen solaren Klassen zugeordnet werden können. Success-Evidenzdiagramme klassifizieren die an Stützpunkten ausgewertete Beleuchtung des Großkreispfads separat als Nacht, Greyline/gemischt oder Tageslicht. Diese Klassifikationen beantworten unterschiedliche Fragen.

<div style="page-break-before: always;"></div>

<a id="sec-8"></a>
### 8. Evidenzgerechte Aussagen und Reproduzierbarkeit

WSPRadar erlaubt präzise Aussagen über bedingte Erreichbarkeit, gepaarte Unterschiede, einseitige Evidenz und die Bereiche, in denen diese beobachteten Muster auftraten. Eine belastbare Berichterstattung beschreibt die tatsächlich erzeugte Evidenz, bewahrt die Laufdefinition und trennt Laborgrößen von den Beobachtungsgrößen des Netzes.

<a id="sec-8-1"></a>
#### 8.1 Aussagen, die von der Evidenz gestützt werden

Verwende den Ergebnistyp, der zur Aussage passt:

* **Success** stützt eine Aussage über die bedingte Reichweite des Targets unter unabhängig bestätigten Opportunities. Für Aussagen zur Empfängerempfindlichkeit und zu einer erwarteten Rate von 100 % sind die entsprechenden Zeilen unten zusammen mit dem Nenner aus [Abschnitt 7.4](#sec-7-4) heranzuziehen.
* **Compare Delta SNR** stützt eine Aussage über gepaarte Evidenz Target minus Referenz. Für Aussagen zu Gewinn und Signifikanz sind die entsprechenden Zeilen zusammen mit den [Abschnitten 7.5](#sec-7-5) und [7.6](#sec-7-6) heranzuziehen.
* **Decode Outcomes** stützen eine Aussage über Joint- und einseitige Evidenz. Für exklusive Decodes ist die entsprechende Zeile zu verwenden und die gepaarte Teilmenge getrennt auszuweisen.
* **Entfernungsabhängige Muster** stützen eine Aussage über die beobachteten Entfernungssegmente. Für Aussagen zum Abstrahlwinkel ist die entsprechende Zeile zu verwenden, da die Entfernung beobachtet, der Abstrahlwinkel jedoch nicht gemessen wird.
* **Lokaler Nachbarschafts-Benchmark** stützt eine Aussage über die gewählte dynamische Definition der Nachbarschaft. Für Aussagen zum lokalen Median ist die entsprechende Zeile zu verwenden; Radius, Methode und aktive beitragende Stationen sind anzugeben.

| Vermeiden | Evidenzgerechte Formulierung |
|---|---|
| "Antenne A hat 3 dBi mehr Gewinn." | "Pfad A ergab gegenüber B ein medianes normiertes Delta SNR von +3,0 dB für die gepaarte Evidenz in diesem Band, Zeitfenster und Segment." |
| "Die Empfindlichkeit meines Empfängers beträgt 72 %." | "Die Success Rate des Target-Empfängers betrug 72 % unter qualifizierenden Peer-Zyklen, die andernorts unabhängig bestätigt wurden." |
| "Success sollte nahe 100 % liegen." | "Success ist ein bedingtes Maß für die Reichweite im globalen Netzwerk; 100 % ist nicht der zu erwartende Ausgangswert." |
| "A ist statistisch signifikant besser." | "Der gepaarte Median begünstigte A; das deskriptive 90-%-Stability-Intervall betrug [Bereich]. Ein Signifikanztest wurde nicht durchgeführt." |
| "Die Antenne hat einen flacheren Abstrahlwinkel." | "Der beobachtete Vorteil konzentrierte sich auf die angegebenen größeren Entfernungssegmente; der Abstrahlwinkel wurde nicht gemessen." |
| "A ist effizienter, weil es mehr exklusive Decodes hatte." | "A erzeugte unter den dokumentierten Leistungs-, Zeitplan- und Netzwerkbedingungen mehr exklusive Decode-Evidenz; der Wirkungsgrad wurde nicht isoliert." |
| "Der lokale Median ist der Durchschnitt der lokalen Stationen." | "Die Referenz war der Zyklus-/Pfadmedian aus je einem Beitrag pro aktiver lokaler callsign+locator-Identität." |

<a id="sec-8-2"></a>
#### 8.2 Interpretationsgrenzen: Was gekoppelt oder unbeobachtet bleibt

WSPRadar-Ergebnisse beschreiben Stationssysteme im tatsächlichen Betrieb unter den gewählten Netzwerk- und Ausbreitungsbedingungen. Sie können Vergleichsmuster aufgebauter Stationskonfigurationen sichtbar machen; die folgenden Laborgrößen werden jedoch nicht direkt gemessen:

* Antennengewinn in dBi;
* Strahlungswirkungsgrad;
* Abstrahlwinkel;
* kalibrierte Empfängerempfindlichkeit;
* absolute Feldstärke;
* jede versuchte oder geplante Aussendung;
* formale statistische Signifikanz oder Kausalität.

Bei der Interpretation der Evidenz sind außerdem folgende Eigenschaften der Daten und des Versuchsdesigns zu berücksichtigen:

* aus der Community stammende Rufzeichen, Locator, Leistungsangaben und Spots können falsch sein;
* das Archiv enthält erfolgreiche Decodes und keine vollständigen Protokolle aller Versuche und Fehlschläge;
* die Success Rate ist durch global erfasste, beobachtbare Opportunities bedingt;
* ein TX-Zyklus, der nirgends decodiert wurde, ist ohne externes Log nicht von einer ausgebliebenen Aussendung zu unterscheiden;
* das Target-Active Gate ist asymmetrisch;
* sequenzielles TX-A/B bleibt zeitlich getrennt;
* die Normierung auf die gemeldete Leistung ist nur so genau wie das gemeldete Feld;
* Stationshardware, Software, Gelände, Rauschen, Polarisation und Ausbreitung bleiben miteinander gekoppelt;
* die Netzdichte variiert nach Geografie, Band und Zeit;
* Entfernung weist weder Abstrahlwinkel noch Ausbreitungsart nach;
* Verfügbarkeit und Korrekturen des vorgelagerten Archivs bleiben externe Faktoren.

Diese Grenzen verhindern keine nützlichen Stationsvergleiche. Sie bestimmen, welche Größe das Ergebnis repräsentiert und wie präzise darüber berichtet werden kann.

<a id="sec-8-3"></a>
#### 8.3 Checkliste für die Ergebnisdokumentation

Für ein belastbares Ergebnis bewahre folgende Angaben auf und dokumentiere sie:

* die gespeicherte `.config`; sie und `run_metadata.json` erfassen die WSPRadar-Anwendungsversion. Halte jedoch den exakten Git-Commit und den Status des Arbeitsbaums separat fest, da das Exportpaket beides nicht erfasst;
* konfigurierte UTC-Auswahl und, sofern aus den Laufnotizen verfügbar, die aufgelösten 15-Minuten-Abfragegrenzen; gib an, ob es sich um Success- oder Compare-Evidenz handelt, da sich die Behandlung des exakten Endpunkts unterscheidet;
* exaktes Band und TX-/RX-Richtung;
* Target-Rufzeichen und konfiguriertes QTH;
* Benchmark-Design und bei Compare gegebenenfalls die feste Referenz- oder Setup-B-Identität beziehungsweise den lokalen Radius und die Benchmark-Methode;
* gegebenenfalls den TX-A/B-Zeitplan;
* Referenz-SNR-Korrektur und deren Kalibriergrundlage;
* Filter für spezielle und bewegte Stationen sowie solare Filter;
* alle Evidenzschwellen;
* Anzahl der Joint-Stationen und Joint-Spots bzw. -Paare;
* Median des Delta SNR auf Stationsebene und 90-%-Stability-Intervall;
* Decode Outcomes sowie Verteilungen unter `STATIONS` / `SPOTS`;
* Success Rate mit ihrem Nenner und der Gewichtungsebene;
* Geräte, Leistung, Zeitplan und bekannte Einschränkungen;
* Exportpaket zusammen mit externen Versuchsnotizen.

Eine Wiederholung, ein Tausch der Pfade oder eine unabhängige Kalibrierung kann einen kleinen beobachteten Unterschied erhärten, bevor daraus eine kostspielige Entscheidung abgeleitet wird.

<a id="sec-8-4"></a>
#### 8.4 Exportpaket der Analyse

`Alle Ergebnisse zum Download vorbereiten` erstellt aus dem abgeschlossenen Lauf und den aktuellen Auswahlen in der Inspektionsansicht ein Paket. Eine typische ZIP-Datei enthält:

```text
config/
  wspradar_config.config
  run_metadata.json
compare/                         # sofern ein Benchmark-Ergebnis vorliegt
  figure_map_highres.png
  figure_segment_insight.png
  figure_segment_temporal_evidence.png
  figure_selected_station_evidence.png
  table_station_insights_current_segment.csv
  table_drilldown_selected_stations.csv
  table_drilldown_all_stations_current_segment.csv
  analysis_cache.parquet
success/                         # sofern ein Success-Ergebnis vorliegt
  ...gleiches Muster für Abbildungen/Tabellen...
  analysis_cache.parquet
```

Die Abbildungen verwenden eine hochauflösende Darstellung auf hellem, druckgeeignetem Hintergrund. Dateien ohne anwendbares Exportrezept oder ohne ausgewählte Evidenz können fehlen. CSV-Dateien spiegeln die aktuelle Segment- und Stationsauswahl wider. Parquet-Dateien enthalten verarbeitete Evidenz nach Anwendung der Filter und keine unveränderten Upstream-Dumps.

Bei Compare reproduziert `figure_selected_station_evidence.png` die für die ausgewählten Stationen aktive Zeitansicht zum Zeitpunkt der Exportvorbereitung. Der Modus `Chronologisch` verwendet die gewählte Compare-Zeitklasse; `UTC-Stunde` verwendet feste einstündige Zeitfenster und dieselben ausgewählten Evidenzzeilen. Der Modus wird in der gespeicherten `.config` und in `run_metadata.json` festgehalten.

Die gespeicherte Konfiguration enthält die zutreffenden ausführbaren Einstellungen. `run_metadata.json` erfasst Anwendungsname und -version, Exportzeit, Sprache, Richtung, Band, Benchmark-Auswahl, konfigurierte Zeitauswahl, Korrektur, Filter, Schwellen, Ergebnisblöcke und Auswahlen in der Inspektionsansicht.

Der effektive Zustand `code = 1` bzw. des historischen Fallbacks wird während des Laufs angezeigt, aber nicht im Paket gespeichert. Das Paket enthält außerdem weder einen Git-Commit noch die exakten aufgelösten Endpunkte vor der Quantisierung, eine stabile ausdrückliche Intervallkonvention oder einen Fingerabdruck der Abfrage bzw. Abfrageparameter. Quantisierte Kartengrenzen können innerhalb der nicht transparenten Exportsignatur vorkommen; dieser interne Wert ist jedoch keine versionierte Festlegung der Zeitgrenzen und darf nicht als solche behandelt werden.

Das Paket unterstützt Audit und Reproduzierbarkeit, ist jedoch kein vollständiger Rechen-Snapshot. Derzeit fehlen:

* Git-Commit oder Nachweis eines unveränderten Arbeitsbaums;
* ausdrückliche aufgelöste und quantisierte UTC-Endpunktfelder mit der jeweils geltenden Intervallkonvention;
* der effektive Zustand des strikten `code = 1` gegenüber dem historischen Fallback je Ergebnisblock;
* das exakte SQL, ein stabiler Fingerabdruck der Abfrage bzw. Abfrageparameter oder unveränderte vorgelagerte Antworten;
* ein Abhängigkeits-Lockfile oder eine Beschreibung des Betriebssystems;
* maßgebliche Betriebsprotokolle der Sender und Empfänger, Kalibrierdatensätze oder externe Versuchsnotizen.

Bewahre die ZIP-Datei zusammen mit Stationsnotizen, Umschaltzeitplan, Leistungsmessungen und Kalibrierdaten auf.

<a id="sec-8-5"></a>
#### 8.5 Haftungsausschluss

WSPRadar ist experimentelle Open-Source-Software und wird in der vorliegenden Form („as is“) ohne Gewährleistung bereitgestellt. Quellcode und Methoden können geprüft werden; Genauigkeit, Vollständigkeit, Verfügbarkeit und Eignung werden jedoch nicht garantiert. Triff keine wesentlichen finanziellen oder sicherheitsrelevanten Entscheidungen allein auf Grundlage von WSPRadar.

<div style="page-break-before: always;"></div>

<a id="sec-ref"></a>
### Literatur und Quellen

* <a id="ref-1"></a><a href="https://arxiv.org/abs/2209.08989">[Ref-1]</a> **Preprint.** Zander, J. (2022). *Simple HF antenna efficiency comparisons using the WSPR system*. arXiv:2209.08989v1. doi:10.48550/arXiv.2209.08989.

* <a id="ref-2"></a><a href="https://doi.org/10.1155/2022/4809313">[Ref-2]</a> **Begutachteter Fachartikel.** Vanhamel, J.; Machiels, W.; Lamy, H. (2022). *Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band*. International Journal of Antennas and Propagation, 2022, 4809313. doi:10.1155/2022/4809313.

* <a id="ref-3"></a><a href="https://sivantoledotech.wordpress.com/2010/09/24/failure-to-use-wspr-to-compare-antennas/">[Ref-3]</a> **Technischer Erfahrungsbericht eines Funkamateurs.** Toledo, S. / 4X6IZ (2010). *Failure to Use WSPR to Compare Antennas*.

* <a id="ref-4"></a><a href="https://www.qsl.net/kp4md/wspr.htm">[Ref-4]</a> **Amateurfunk-Fachartikel und Clubvortrag.** Milazzo, C. F. / KP4MD (2011). *Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*.

* <a id="ref-5"></a><a href="https://www.researchgate.net/publication/319903566_Improving_HF_Band_SNR_from_analysis_of_WSPR_spots">[Ref-5]</a> **Amateurfunk-Zeitschriftenartikel.** Griffiths, G.; Squibb, N. J. (2017). *Improving HF Band SNR from analysis of WSPR spots*. Practical Wireless, October 2017, 23-26.

* <a id="ref-6"></a><a href="https://www.arrl.org/files/file/History/History%20of%20QST%20Volume%201%20-%20Technology/QS11-2010-Taylor.pdf">[Ref-6]</a> Taylor, J. H.; Walker, B. (2010). *WSPRing Around the World*. QST, 94(11), 30-32.

* <a id="ref-7"></a><a href="https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2023.1184171/full">[Ref-7]</a> **Begutachteter Übersichtsartikel.** Frissell, N. A. et al. (2023). *Heliophysics and amateur radio: citizen science collaborations for atmospheric, ionospheric, and space physics research and operations*. Frontiers in Astronomy and Space Sciences, 10, 1184171. doi:10.3389/fspas.2023.1184171.

* <a id="ref-8"></a><a href="https://www.arrl.org/wspr">[Ref-8]</a> **Offizieller technischer Überblick.** ARRL, *WSPR*: Nachrichtenformat, Codierung, Dauer, Zeitsteuerung, belegte Bandbreite und SNR-Bezugsgröße. Abgerufen am 2026-07-12.

* <a id="ref-9"></a><a href="https://www.mdpi.com/2073-4433/13/8/1340">[Ref-9]</a> **Begutachteter Fachartikel.** Lo, S.; Rankov, N.; Mitchell, C.; Witvliet, B. A.; Jayawardena, T. P.; Bust, G.; Liles, W.; Griffiths, G. (2022). *A Systematic Study of 7 MHz Greyline Propagation Using Amateur Radio Beacon Signals*. Atmosphere, 13(8), 1340. doi:10.3390/atmos13081340.

* <a id="ref-10"></a><a href="https://wspr.live/">[Ref-10]</a> **Offizielle Dokumentation des Datendienstes.** WSPR.live, *Welcome to WSPR Live* und <a href="https://wspr.live/wspr_downloader.php">*WSPR Exporter*</a>: Datenbankbeschreibung, Schema, Zuordnung der Mode-Codes, Haftungsausschluss zu Rohdaten und Verfügbarkeit sowie Echtzeitverzögerung. Abgerufen am 2026-07-15.

* <a id="ref-11"></a><a href="https://wsprdaemon.readthedocs.io/en/stable/description/how_it_works.html">[Ref-11]</a> **Werkzeugdokumentation.** WSPRdaemon, *How wsprdaemon Works*: Decodierung mit mehreren Empfängern, Reporting, Zeitplanung sowie Rausch- und Doppler-Metadaten.

* <a id="ref-12"></a><a href="https://wsjt.sourceforge.io/wsjtx-main_en.html">[Ref-12]</a> **Offizielle Betriebsdokumentation.** WSJT-X 3.0.1 User Guide: WSPR-Nachrichtenformate und Decoderleistung; Dateitrennung unter Windows mit `--rig-name`; Audioeinstellungen und Dateispeicherorte. QRP Labs, <a href="https://www.qrp-labs.com/images/qmx/manuals/operation_1_03_000.pdf">*QMX Operating Manual, firmware 1_03_000*</a>: Beacon-Zeitplanung mit `Frame` und `Start` sowie Empfehlungen zur WSPR-Wiederholung; <a href="https://qrp-labs.com/images/ultimate3s/operation3.12a.pdf">*Ultimate3S Operating Manual, firmware v3.12a*</a>: globales Frame-/Start-Verhalten, sequenzielle Mode-Einträge und `Aux`-Werte je Eintrag; <a href="https://qrp-labs.com/images/appnotes/AN003_A4.pdf">*AN003: Ultimate3/3S relay-switched filters*</a>: Ansteuerung von Relais/Treibern für geschaltete Filter und Schaltintervalle ohne HF. Abgerufen am 2026-07-15.

* <a id="ref-13"></a><a href="https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf">[Ref-13]</a> **Konferenzbeitrag.** Griffiths, G.; Robinett, R. (2020). *Aids to the Presentation and Analysis of WSPR Spots: TimescaleDB database and Grafana*. ARRL/TAPR Digital Communications Conference 2020.

* <a id="ref-14"></a><a href="https://wspr.rocks/help.html">[Ref-14]</a> **Werkzeugdokumentation.** WSPR.Rocks, *Help &amp; Documentation*: SpotQ, SQL-Zugriff, Duplikatanalyse, Karten, Diagramme und Heatmaps.

* <a id="ref-15"></a><a href="https://www.sotabeams.co.uk/wsprlite-classic">[Ref-15]</a> **Produktdokumentation.** SOTABEAMS, *WSPRlite Classic / DXplorer*: WSPR-basierte Analyse der Antennenleistung und DX10-Metrik.

* <a id="ref-16"></a><a href="https://sites.google.com/myuba.be/wspr-station-compare/home">[Ref-16]</a> **Projektdokumentation.** WSPR-Station-Compare, Projektseite mit Verweisen auf Vanhamel et al. und Zander.

* <a id="ref-17"></a><a href="https://wspr.bsdworld.org/">[Ref-17]</a> **Werkzeugdokumentation.** Antenna Performance Analysis Tool, WSPR-basierter Generator für Antennenberichte.

* <a id="ref-18"></a><a href="https://www.gm4eau.com/home-page/wspr/">[Ref-18]</a> **Werkzeugdokumentation.** GM4EAU, *WATT WSPR Analysis Tool*: Berichte, Karten, Filter und Zeitachsenanimation in Excel/VBA.

<div style="page-break-before: always;"></div>

<a id="part-iv"></a>
## Teil IV: Praktische Ergänzungen

Dieser Teil bündelt optionale Einrichtungsverfahren, Hinweise zur sequenziellen TX-A/B-Zeitplanung und Umschaltung, die Kalibrierung der Referenzseite und die Projektlizenz. Verwende die Abschnitte, die für deine Station und deinen Versuch relevant sind.

<a id="sec-a"></a>
### Anhang A: Parallele WSJT-X-Instanzen

Mit diesem Verfahren wird unter Windows eine zweite isolierte WSJT-X-Instanz eingerichtet, beispielsweise für einen simultanen RX Hardware A/B-Test. Das aktuelle WSJT-X-Handbuch nennt `--rig-name` als unterstützten Weg, die Einstellungen und beschreibbaren Dateien jeder Instanz zu trennen. Da sich WSJT-X-Versionen und Installationspfade ändern können, sollte bei abweichenden Menüs das aktuelle Handbuch geprüft werden. <a href="#ref-12">[Ref-12]</a>

<a id="sec-a-1"></a>
#### A.1 Zweite Instanz anlegen

1. Eine Desktop-Verknüpfung zu `wsjtx.exe` erstellen.
2. Die Eigenschaften der Verknüpfung öffnen.
3. Im Feld **Ziel** der Verknüpfung außerhalb der Anführungszeichen des Programmpfads einen eindeutigen Rig-Namen ergänzen. Den tatsächlichen Programmpfad der eigenen Installation verwenden, zum Beispiel:
   `"C:\WSJTX\bin\wsjtx.exe" --rig-name=SDR`
4. Die Verknüpfung einmal starten und die Instanz wieder schließen. Für `--rig-name=SDR` legt Windows folgende getrennte Speicherorte an:
    * Einstellungen: `%LOCALAPPDATA%\WSJT-X - SDR\WSJT-X - SDR.ini`
    * Log-/Schreibverzeichnis: `%LOCALAPPDATA%\WSJT-X - SDR\`
    * Standardverzeichnis für gespeicherte Audiodateien: `%LOCALAPPDATA%\WSJT-X - SDR\save\`

<a id="sec-a-2"></a>
#### A.2 Ausgangskonfiguration bei Bedarf kopieren

1. Alle WSJT-X-Instanzen schließen.
2. `%LOCALAPPDATA%\WSJT-X\WSJT-X.ini` kopieren.
3. Die Datei in `%LOCALAPPDATA%\WSJT-X - SDR\` einfügen.
4. Die Kopie in `%LOCALAPPDATA%\WSJT-X - SDR\WSJT-X - SDR.ini` umbenennen und dabei, falls beabsichtigt, die neu initialisierte Instanzdatei ersetzen.

<a id="sec-a-3"></a>
#### A.3 Alle Datenpfade trennen

Eine kopierte Konfiguration kann weiterhin beide Instanzen auf denselben Audioeingang oder Speicherpfad verweisen lassen. Dadurch kann derselbe Audiostrom doppelt decodiert werden oder es können Dateikonflikte entstehen. In der zweiten Instanz Folgendes prüfen:

1. **File > Settings > Audio** öffnen.
2. Unter **Soundcard** für **Input** den vorgesehenen unabhängigen Empfänger bzw. das vorgesehene unabhängige Audiogerät einstellen. Das WSJT-X-Handbuch nennt eine Audiogerätekonfiguration mit 48.000 Hz und 16 Bit.
3. **Save Directory** auf einen instanzspezifischen Pfad setzen, normalerweise `%LOCALAPPDATA%\WSJT-X - SDR\save\`.
4. **AzEl Directory** auf einen instanzspezifischen Pfad setzen, zum Beispiel `%LOCALAPPDATA%\WSJT-X - SDR\`.
5. **File > Settings > General** öffnen und dort exakt das Rufzeichen und den Locator von Setup B eintragen, die für Meldungen verwendet werden.
6. Zum WSPR-Hauptfenster zurückkehren, das vorgesehene Band und den Audiopegel prüfen, bei Bedarf den Spot-Upload aktivieren und kontrollieren, dass hochgeladene Zeilen die Identität von Setup B verwenden.
7. Die Zeitsynchronisation beider Instanzen prüfen.

Getrennte Verzeichnisse belegen noch keine Unabhängigkeit der HF-Pfade. Prüfe praktisch, ob beide Datenströme tatsächlich die vorgesehene Hardware verwenden.

<div style="page-break-before: always;"></div>

<a id="sec-b"></a>
### Anhang B: Sequenzielle TX-A/B-Zeitplanung und Umschaltung

Dieser Anhang bündelt die praktischen Hinweise zu Zeitplan und Umschaltung hinter dem TX-Hardware-A/B-Leitfaden. Die exakten UI-Bedienelemente stehen in [Abschnitt 4.3](#sec-5-3), die genaue Bildung geplanter Paare in den [Abschnitten 7.1](#sec-7-1) und [7.7](#sec-7-7).

<a id="sec-b-1"></a>
#### B.1 Anforderungen an einen gültigen zeitgesteuerten Versuch

Für sequenzielle TX-A/B-Antennentests ist ein Sender, der über einen kontrollierten Umschalter zwei HF-Pfade speist, normalerweise zwei unabhängigen Sendern vorzuziehen. Sender, Frequenzreferenz, WSPR-Kette, Rufzeichen, Leistungseinstellung und Zeitsteuerung bleiben damit gemeinsam.

Verwende für beide Pfade ein reguläres, gültiges Rufzeichen und unterscheide sie durch verschiedene deterministische UTC-Phasen. Trage die Aussendungen ein, die tatsächlich über den jeweiligen HF-Pfad erfolgen:

* Das `Wiederholintervall` ist die tatsächliche Wiederkehr jedes Pfads und entspricht nicht zwangsläufig dem angezeigten `Frame`-Wert eines Senders.
* `Target-Start` und `Referenz-Start` sind unterschiedliche gerade UTC-Phasen unterhalb dieses Intervalls.
* Verwende den kürzesten praktikablen Abstand, der einen zuverlässigen Betrieb und einen vertretbaren Tastgrad erlaubt.
* Melde die tatsächliche Leistung; kennzeichne den Pfad nicht durch falsche dBm-Werte.
* Prüfe vor dem Senden die Zeitsynchronisation und die physische Zuordnung von Zeitplan und Pfad.

Ein deterministischer Zeitgeber oder Controller ist erforderlich. Der zufällige Sendebetrieb über die prozentuale TX-Einstellung von WSJT-X erzeugt keine feste A/B-Folge.

<a id="sec-b-2"></a>
#### B.2 Zeitgesteuerter WSPRadar-A/B-Relaisumschalter

WSPRadar enthält:

`tools/Timed-AB-Relay-Switch`

Derzeit veröffentlichtes Release-Paket der Version 0.1:

[Release-Paket des zeitgesteuerten A/B-Relaisumschalters herunterladen](https://github.com/markusthemaker/WSPRadar/releases/download/timed-ab-relay-switch-v0.1.0/Timed-AB-Relay-Switch-v0.1.0.zip)

Das Hilfsprogramm im Repository verwendet dieselben Begriffe und Bedingungen für den Zeitplan wie WSPRadar:

* `Wiederholintervall` gilt gemeinsam für Target und Referenz; zulässig sind `4, 6, 10, 12, 20, 30` oder `60 min`.
* `Target-Start` und `Referenz-Start` sind unterschiedliche gerade UTC-Phasen unterhalb dieses Intervalls.
* Die Voreinstellung lautet `Wiederholintervall = 10`, `Target-Start = 00`, `Referenz-Start = 02`.

Das Relais wählt jeden Pfad vor dessen konfiguriertem Start und hält während nicht belegter Lücken den zuletzt gewählten Pfad. An ungenutzten zweiminütigen WSPR-Grenzen wird nicht geschaltet. Hilfsprogramm und WSPRadar müssen anhand der Aussendungen, die tatsächlich über den jeweiligen HF-Pfad erfolgen, identisch konfiguriert werden. Ist die physische Polarität umgekehrt, ändere, ob Relais ON dem Target entspricht, oder tausche die beiden Startzuordnungen.

Eine optionale Vorlaufzeit lässt den HF-Pfad vor jedem geplanten Start einschwingen. Die manuelle physische Relaissteuerung ON/OFF bleibt unabhängig vom automatischen Zeitplan verfügbar. Bestehende Modulo-4-Konfigurationen der Version 0.1 behalten beim Laden ihr bisheriges Verhalten als `4 / 00 / 02` oder `4 / 02 / 00`. Das Hilfsprogramm ist für verbreitete ATtiny45/V-USB-HID-Relaisplatinen mit USB-VID/PID `16c0:05df` ausgelegt und verwendet unter Windows, Linux und macOS den Python-HID-Stack. Aktuelle Hinweise zu Installation, Berechtigungen und Optionen stehen in seiner README-Datei.

Das verlinkte Paket der Version 0.1 enthält noch den früheren festen Modulo-4-Zeitplaner. Bis ein neueres Paket veröffentlicht ist, ist für den hier beschriebenen konfigurierbaren Zeitplan die Version aus dem Repository zu verwenden.

Installation aus dem Werkzeugverzeichnis:

```bat
py -3 -m pip install -r requirements-relay.txt
```

oder unter Linux/macOS:

```sh
python3 -m pip install -r requirements-relay.txt
```

Einrichtung und Testlauf unter Windows:

```bat
Start-Timed-AB-Relay-Switch.cmd --setup
Start-Timed-AB-Relay-Switch.cmd --dry-run
```

Einrichtung und Testlauf unter Linux/macOS:

```sh
chmod +x ./Start-Timed-AB-Relay-Switch.sh
./Start-Timed-AB-Relay-Switch.sh --setup
./Start-Timed-AB-Relay-Switch.sh --dry-run
```

Ein kleines USB-Relais sollte die HF normalerweise nicht direkt schalten. Es sollte ein für die Aufgabe ausreichend dimensioniertes HF-Schaltsystem oder -Relais ansteuern. Prüfe Spannung, Strom, Polarität, ausfallsicheren Zustand, HF-Leistung, Isolation und Verriegelungen.

<a id="sec-b-3"></a>
#### B.3 Zeitplanbeispiel für Ultimate3S

Der QRP Labs Ultimate3S kann eine Folge von WSPR-Einträgen abarbeiten und pro Eintrag einen `Aux`-Ausgang für externe Umschalthardware setzen. Beginnt eine Folge aus zwei Einträgen um `00`, kann ein globaler 10-Minuten-Frame das Target um `00` und die Referenz um `02` senden und anschließend bis zum nächsten Sequenzstart um `10` pausieren; in WSPRadar entspricht das `Wiederholintervall = 10`, `Target-Start = 00`, `Referenz-Start = 02`. Dieselbe Anordnung mit einem globalen 20-Minuten-Frame ergibt für jeden Pfad eine Wiederholung alle 20 Minuten bei weiterhin zwei Minuten A/B-Abstand.

Laut Ultimate3S-Handbuch hat `Start = 00` die besondere Bedeutung „not used“. Prüfe deshalb die angezeigte und tatsächlich beobachtete UTC-Folge und trage deren wirkliche Phasen ein, statt eine wörtliche Zuordnung von Einstellung zu Uhrzeit anzunehmen. Die `Aux`-Leitungen werden gemeinsam mit Displaysignalen genutzt; verwende den dokumentierten gefilterten Treiber oder eine geeignete Relaisschnittstelle und schalte ausschließlich in der sendefreien Zeit <a href="#ref-12">[Ref-12]</a>.

<a id="sec-b-4"></a>
#### B.4 Zeitplanbeispiele für QMX

Ein QMX mit `Frame = 10`, `Start = 0` sendet um `00, 10, 20, 30, 40, 50`. Schaltet ein externer Umschalter diese Aussendungen abwechselnd auf zwei Pfade, liegt das Target bei `00, 20, 40` und die Referenz bei `10, 30, 50`; jeder Pfad wiederholt sich alle 20 Minuten. Trage deshalb `Wiederholintervall = 20`, `Target-Start = 00`, `Referenz-Start = 10` ein; verwende nicht `10 / 00 / 02`.

Mit diesem Bakenscheduler kann ein einzelner QMX kein benachbartes Paar `00/02` mit anschließender achtminütiger Pause erzeugen. Zwischen den beiden Pfaden in benachbarten Zwei-Minuten-Slots könnte ein einzelner QMX nur wechseln, indem er alle zwei Minuten sendet, wovon das QMX-Handbuch wegen der unangemessen hohen Netzbelegung abrät. Zwei unabhängig geplante QMX mit `Frame = 10` und den Starts `00` beziehungsweise `02` setzen hingegen den WSPRadar-Zeitplan `10 / 00 / 02` um; ihre Sendeketten und tatsächlichen Leistungen müssen dann jedoch als getrennte Hardware kontrolliert werden <a href="#ref-12">[Ref-12]</a>.

<a id="sec-b-5"></a>
#### B.5 Zuordnung prüfen und Versuch dokumentieren

Vor dem Senden:

* ohne HF-Leistung testen;
* Polarität des Target- und Referenzpfads prüfen;
* sicherstellen, dass während einer WSPR-Aussendung nicht umgeschaltet wird;
* eine Kunstantenne (Dummy Load) oder einen Durchgangs-/SWR-Test mit geringer Leistung verwenden;
* Relaiskanal, Polarität, Vorlaufzeit, tatsächlichen Sendeplan, Zeitplanzuordnung und Pfadbelegung dokumentieren.

Schaltverlust, Isolation, Steckverbinder, Unterschiede der Speiseleitungen und das Antennenumfeld bleiben Bestandteil des Ergebnisses. Ein Tausch der Antennen zwischen den Schaltpfaden kann helfen, Antenneneffekte von Pfadeffekten zu trennen. Eine Wiederholung mit vertauschten Zeitplanzuordnungen kann Zeit- oder rollenspezifische Effekte sichtbar machen.

<div style="page-break-before: always;"></div>

<a id="sec-c"></a>
### Anhang C: Referenz-SNR-Kalibrierung

Dieses Verfahren schätzt einen stabilen additiven Offset zwischen Empfangsketten oder Pfaden auf der Referenzseite.

1. **Gemeinsames Eingangssignal:** Beide Empfangsketten über einen geeigneten Verteiler und charakterisierte Kabel aus einer stabilen Antenne speisen.
2. **Verteiler charakterisieren:** Pegelunterschiede zwischen den Ausgängen und Kabeldifferenzen berücksichtigen; wenn praktikabel, die Ausgänge in einem Kontrolllauf vertauschen.
3. **Gepaarte Evidenz sammeln:** Beide Ketten gleichzeitig über den vorgesehenen Signalpegelbereich betreiben, ohne Verstärkung oder Decoder-Einstellungen zu verändern.
4. **Offset schätzen:** Gepaarte Delta-SNR-Evidenz verwenden und angeben, ob der Schätzer stationsgleichgewichtet oder aus den Rohpaaren berechnet ist.
5. **Stabilität prüfen:** Nach Station, Zeit und SNR untersuchen. Ein konstanter Wert ist nicht vertretbar, wenn sich der Offset mit Pegel, Frequenz, AGC oder Zeit ändert.
6. **Vorzeichen anwenden:** Den beobachteten Offset `target - reference` mit demselben Vorzeichen eingeben.
7. **Validieren:** Messung wiederholen oder Pfade tauschen und prüfen, ob das korrigierte Delta des gemeinsamen Eingangssignals plausibel nahe null liegt.

Ein schmales Stability-Intervall zeigt die Wiederholbarkeit der verfügbaren Stichprobe und keine rückführbare Laborgenauigkeit. Verteilerverlust, Fehlanpassung, Kopplung und Instabilität der Quelle können bestehen bleiben.

<a id="sec-license"></a>
### Lizenz

WSPRadar ist unter der GNU Affero General Public License Version 3 (AGPLv3) lizenziert. Maßgeblich ist die Datei `LICENSE` im Repository.

"""
