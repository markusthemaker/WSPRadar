# docs/doc_de.py

"""Maßgebliches deutschsprachiges Anwender- und Wissenschaftshandbuch für WSPRadar."""

DOC_DE = r"""
---

<a id="sec-1"></a>

### 0. Warum WSPRadar?

Funkamateure verändern und optimieren ihre Stationen fortlaufend. Eine neue Antenne wird aufgebaut, ihre Höhe oder Ausrichtung verändert, eine Speiseleitung ersetzt, eine Mantelwellensperre überarbeitet oder ein Empfänger, Filter beziehungsweise Vorverstärker ergänzt. Fast zwangsläufig folgt dieselbe Frage: **Hat die Änderung die Station tatsächlich verbessert – und wenn ja, wo, wann und um wie viel?**

Im praktischen Funkbetrieb scheint sich das zunächst leicht beantworten zu lassen. Es gelingen mehr QSOs, eine Gegenstation gibt einen besseren Rapport, ein WebSDR zeigt ein stärkeres Signal oder WSPR liefert mehr Spots. Solche Beobachtungen sind wertvoll, messen aber nicht allein das geänderte Bauteil. Das Ergebnis entsteht immer aus dem Zusammenwirken der vollständigen Station mit dem Funkweg: Antenne, Speiseleitung, Funkgerät, Sendeleistung, Empfänger, lokaler Stör- und Rauschpegel, Gelände, Ionosphäre, Gegenstation und Zeitpunkt wirken gleichzeitig zusammen.

Genau darin liegt das grundlegende Messproblem. Ein besserer Rapport kann auf einer günstigen Ausbreitungsphase beruhen. Ein zusätzliches QSO kann eine andere Gegenstation betreffen. Eine höhere Spotzahl kann durch veränderte Netzaktivität oder bessere Bedingungen entstehen. Selbst vollkommen korrekte Beobachtungen zeigen daher nicht automatisch, wodurch der Unterschied verursacht wurde.

Erfahrene Funkamateure begegnen diesem Problem mit zunehmend kontrollierten Verfahren: wiederholten Vergleichen, Bakenaussendungen, WebSDRs, Daten des Reverse Beacon Network, WSPR und insbesondere einer schnellen A/B-Umschaltung im laufenden Betrieb. Ein schneller A/B-Test ist wesentlich aussagekräftiger als zwei zeitlich weit auseinanderliegende QSOs, weil Sender, Leistung, Frequenz, Gegenstation und ein großer Teil des Funkwegs ähnlich bleiben. Etablierte WSPR-Vergleichsversuche zeigen ebenfalls, dass gemeinsame Bedingungen und möglichst kurze – oder simultane – Vergleiche belastbarer sind als lange getrennte Messblöcke <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a> <a href="#ref-3">[Ref-3]</a> <a href="#ref-4">[Ref-4]</a> <a href="#ref-5">[Ref-5]</a>.

Doch selbst ein sorgfältiger schneller A/B-Vergleich beobachtet normalerweise nur einen Funkweg in einem kurzen Zeitfenster. QSB, Mehrwegeausbreitung, QRM und lokaler Störpegel können sich schon während der Umschaltung verändern. AGC, S-Meter-Auflösung, unterschiedliche Signalwege und subjektive Rapporte bringen zusätzliche Unsicherheit ein. Ein beobachteter Vorteil kann real sein, gilt zunächst aber nur für diese Gegenstation, Richtung, Zeit und Ausbreitungslage.

Die eigentliche Herausforderung besteht deshalb nicht nur darin, einen Unterschied zu sehen. Entscheidend ist, **ob sich dieser Unterschied unter vielen vergleichbaren Bedingungen wiederholt, wie groß er typischerweise ist, auf welchen Funkwegen er auftritt, wann er wiederkehrt und wie viel Evidenz ihn stützt.**

Hier bietet WSPR eine ungewöhnlich leistungsfähige Grundlage. Seine wiederholten, zeitgestempelten und maschinell decodierten Aussendungen mit kleiner Leistung erzeugen in einem weltweiten, ehrenamtlich betriebenen Netz Beobachtungen über viele Stationen, Entfernungen, Richtungen und Ausbreitungszustände <a href="#ref-6">[Ref-6]</a> <a href="#ref-7">[Ref-7]</a> <a href="#ref-8">[Ref-8]</a>. Je nach Bandbelegung und Beobachtungsdauer können über Stunden oder Tage Hunderte bis Tausende Meldungen zusammenkommen.

WSPRadar macht aus diesem Strom von Meldungen ein experimentelles Evidenzsystem. Es führt vergleichbare Beobachtungen zusammen, prüft, ob die relevanten Stationen nachweislich aktiv waren, berücksichtigt gegebenenfalls die gemeldete Sendeleistung, verhindert, dass wenige besonders aktive Stationen stationsgleichgewichtete Zusammenfassungen unbemerkt dominieren, und hält jedes Ergebnis bis zu den beitragenden Stationen und Beobachtungen prüfbar. Die Aktivitätsprüfung folgt einem wichtigen Grundsatz für Beobachtungsdaten: Funkstille sollte erst dann zu Gegen-Evidenz werden, wenn der Betrieb unabhängig erkennbar ist <a href="#ref-9">[Ref-9]</a>.

Das Ergebnis ist mehr als eine Spotzahl und mehr als eine einzelne Gewinner-Verlierer-Kennzahl. WSPRadar kann zeigen, ob ein Muster breit oder funkwegabhängig ist, wie es sich mit Entfernung, Richtung und Zeit verändert, ob viele Stationen übereinstimmen und wie viel Evidenz aus beidseitig oder nur einseitig decodierten Signalen stammt. Damit wird aus **„Das sah einmal besser aus“** zunehmend **„Dieser Unterschied trat hier, unter diesen Bedingungen, wiederholt und mit dieser Evidenz auf.“**

WSPRadar ist kein kalibriertes Antennenmessgelände und macht aus öffentlichen WSPR-Meldungen keine Labormessung. Es schlägt eine praktische Brücke zwischen alltäglicher Stationsoptimierung und Amateurwissenschaft: semiquantitative, geografisch reichhaltige, zeitbezogene und prüfbare Evidenz über vollständige Stationen und kontrollierte Signalwege unter realen Betriebsbedingungen.

So eingesetzt wird WSPR auch für die gesamte Amateurfunkgemeinschaft wertvoller. Korrekte Rufzeichen, Locator und Leistungsangaben, stabiler Betrieb und dokumentierte Änderungen machen aus gewöhnlichem Bakenbetrieb Evidenz, die später erneut untersucht, verglichen und genutzt werden kann, statt nur auf einer Karte vorbeizuziehen.

<a id="sec-1-1"></a>

#### 0.0 WSPR in 2 Minuten

<strong class="defined-term">WSPR</strong> steht für **Weak Signal Propagation Reporter**. Joe Taylor, K1JT, und Bruce Walker, W1BW, beschrieben WSPR als weltweites Netz von QRP-Stationen, die mit bakenartigen Aussendungen Ausbreitungswege untersuchen. WSPR arbeitet in synchronisierten Zwei-Minuten-Zyklen. Eine WSPR-2-Aussendung dauert etwa 111 Sekunden und belegt etwa 6 Hz. Eine normale Typ-1-Nachricht enthält Rufzeichen, vierstelligen Maidenhead-Locator und gemeldete Sendeleistung in dBm. Das Decoder-SNR bezieht sich auf 2500 Hz Bandbreite; erfolgreiche Decodes um `-28 dB` veranschaulichen den Empfang weit unter dem Rauschen und sind keine garantierte Empfangsschwelle <a href="#ref-6">[Ref-6]</a> <a href="#ref-8">[Ref-8]</a>.

Eine Empfangsstation mit aktiviertem Reporting lädt jeden erfolgreichen Decode als <strong class="defined-term">Spot</strong> hoch. Diese Datenbankmeldung verknüpft Sender- und Empfängerkennung samt Standort mit Zeit, Band, gemeldeter Sendeleistung und SNR. **WSPRnet** sammelt Empfangsmeldungen und zeigt sie an; Dienste wie **wspr.live** und **WSPRDaemon** stellen große Bestände dieser Beobachtungen für Analysen bereit <a href="#ref-10">[Ref-10]</a> <a href="#ref-11">[Ref-11]</a>.

**WSPRadar analysiert diese Datenbankmeldungen; es empfängt und decodiert selbst keine Funksignale.** Bei RX untersucht es die von deiner Station empfangenen Signale. Bei TX untersucht es, wie entfernte Empfänger deine Aussendungen hören. **Benchmark** vergleicht deine Station oder deinen Aufbau mit einer Referenz; **Performance** beschreibt die beobachteten Ergebnisse deiner eigenen Station.

Normale Typ-1-Nachrichten sind der einfachste Einstieg, wenn dein Senderufzeichen in dieses Format passt. Erweitertes WSPR kann ein zusammengesetztes Rufzeichen und einen sechsstelligen Locator auf getrennte Aussendungen verteilen. Die Meldekennungen der Empfänger werden unabhängig davon konfiguriert und bestimmen nicht das Nachrichtenformat der empfangenen entfernten Aussendungen. WSPRadar verwendet die tatsächlich in der Datenbank erfassten Kennungen und rekonstruiert keine fehlenden Nachrichtenphasen <a href="#ref-12">[Ref-12]</a>.

Die grundlegende WSPR-Einrichtung beschreibt [Abschnitt 1.1](#sec-2-1). Zur Vorbereitung eines Vergleichs siehe den [RX-Benchmark-Aufbau in Abschnitt 2.1.1](#sec-3-rx-benchmark-hardware) oder den [TX-Benchmark-Aufbau in Abschnitt 2.2.1](#sec-3-tx-benchmark-simultaneous). Diese Abschnitte erklären, welche Kennungen und Betriebsbedingungen für einen aussagekräftigen Vergleich nötig sind.

**Datenquellen.** WSPRadar verwendet normalerweise **wspr.live**, mit **WSPRDaemon WD2** und **WD1** als Alternativen. Jeder abgeschlossene Lauf verwendet genau eine Datenbank; Meldungen verschiedener Quellen werden niemals kombiniert. [Abschnitt 5.6](#sec-6-6) erklärt Verfügbarkeit und Quellenwahl. Das Projekt dankt den Menschen, die diese öffentliche Infrastruktur bereitstellen und betreiben.

Die zentrale Grenze ist einfach: Eine Datenbank enthält erfolgreiche Decodes, aber kein vollständiges Protokoll aller Sendeversuche oder empfangsbereiten Stationen. **Ein fehlender Spot allein beweist keinen verpassten Empfang.** Bei Performance prüft WSPRadar Aktivitätsnachweise der beteiligten Stationen, bevor es eine bestätigte Gelegenheit zählt. Ohne ausreichenden Nachweis bleibt Funkstille unbekannt. Die praktischen Anleitungen zu [RX Performance in Abschnitt 2.3](#sec-3-rx-performance) und [TX Performance in Abschnitt 2.4](#sec-3-tx-performance) erklären die Interpretation dieser Ergebnisse.

<a id="sec-1-0"></a>
<a id="sec-1-2"></a>

#### 0.1 Was WSPRadar zeigen kann

WSPRadar wertet ein <strong class="defined-term">Target</strong> aus: die zu untersuchende Station, normalerweise deine Station. Das kann eine vollständig aufgebaute Station oder ein dokumentierter Empfangs- beziehungsweise Sendepfad sein. Ein <strong class="defined-term">Peer</strong> ist eine entfernte Station, deren Funkweg beiträgt: bei RX ein Sender, bei TX ein Empfänger. Wähle zwischen zwei Fragen:

* <strong class="defined-term">Benchmark</strong> fragt, wie das Target gegenüber einer <strong class="defined-term">Referenz</strong> abschneidet: einem kontrollierten lokalen Pfad, einer bekannten Station oder den beobachteten Stationen in der Umgebung. Er zeigt relative Signalpegel, einseitig und beidseitig decodierte Signale sowie Ort und Zeit der Unterschiede. Die zentrale Größe ist **ΔSNR (Delta SNR)**: Target-SNR minus Referenz-SNR für gemeinsam decodierte Signale, einschließlich der zutreffenden Leistungsnormierung und Referenzkorrektur.
* <strong class="defined-term">Performance</strong> fragt ohne Referenz, wo, wann und wie beständig das Target gehört wurde oder andere Stationen empfing. Sie verbindet Mindestens-einmal-Reichweite, erfolgreiche Signalpegel und **Dekodierrate**: den Erfolgsprozentsatz innerhalb bestätigter Gelegenheiten. Stationsgleichgewichtete Zusammenfassungen und Zusammenfassungen auf Gelegenheitsebene beantworten ergänzende Fragen; [Kapitel 2](#sec-3) erläutert sie.

Gehe von deiner Frage zur Station aus und wähle anhand der Beispiele die passende Analyse.

| Deine Frage | Praktische Beispiele | Passende Analyse |
|---|---|---|
| Welche meiner Antennen empfängt besser? | Vergleiche zwei Antennen mit gleichzeitig arbeitenden Empfänger-/Decoderketten und unterschiedlichen Melderufzeichen oder prüfe Empfänger, Speiseleitungen, Filter, Vorverstärker oder Mantelwellensperren. Nutze für eine gemeinsame Antenne einen Verteiler mit bekannten Eigenschaften. Halte die übrigen Bedingungen gleich oder bestätige das Ergebnis durch einen Kreuztausch, bevor du Unterschiede den Antennen zuschreibst. | <span class="analysis-choice"><span class="analysis-family">RX Benchmark</span><br><strong class="analysis-variant">Referenzaufbau/-station</strong></span> |
| Welche meiner Antennen wird besser gehört? | Vergleiche Antennen, Speiseleitungen, Anpassnetzwerke oder Filter mit zwei gleichzeitig sendenden Geräten: unterschiedliche Kennungen, synchronisierte Zyklen, geprüfte tatsächliche und gemeldete Leistung, freie, ausreichend voneinander getrennte Frequenzen und ausreichende HF-Entkopplung. Halte die übrigen Bedingungen gleich, bevor du Unterschiede den Antennen zuschreibst. | <span class="analysis-choice"><span class="analysis-family">TX Benchmark</span><br><strong class="analysis-variant">Referenzaufbau/-station</strong></span> |
| Wie schneidet meine Station gegenüber einer bekannten Station ab? | Vergleiche den Empfang derselben Sender oder wie dieselben Empfänger beide Stationen hören, jeweils innerhalb derselben Zyklen. Wiederhole den Vergleich vor und nach Arbeiten an der Station. Das Ergebnis vergleicht vollständige Stationen; deine Referenz ist kein absolut kalibrierter Standard. | <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Referenzaufbau/-station</strong></span> |
| Wie schneidet meine Station gegenüber WSPR-Stationen in der Umgebung ab? | Nutze den Median der SNR-Werte beobachteter Stationen im gewählten Radius, die die Auswahlkriterien erfüllen, wenn keine geeignete einzelne Referenz verfügbar ist. Suche Unterschiede nach Richtung, Entfernung oder Zeit. Diese wechselnde Vergleichsbasis für Gesamtstationen isoliert weder Antennengewinn noch ergibt sie eine Rangliste aller Stationen in der Umgebung. | <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Referenznachbarschaft (Lokaler Median)</strong></span> |
| Was höre ich mit meiner Antenne und meinem Empfänger, und wie beständig? | Erfasse nach Aufbau, Reparatur oder Gerätewechsel den Empfang nach Richtung, Entfernung und Zeit. Prüfe die Dekodierrate innerhalb bestätigter Gelegenheiten mit nachgewiesener Stationsaktivität statt über die gesamte verstrichene Zeit; untersuche wiederkehrende Lücken oder mögliche lokale Störungen. | <strong class="analysis-choice-single">RX Performance</strong> |
| Wo wird meine Station gehört, und wie beständig? | Erfasse, wo deine QRP-Bake oder neue Antenne gehört wird und wann aktive Empfänger sie besonders beständig decodieren. Nutze bestätigte Gelegenheiten mit nachgewiesener Stationsaktivität statt der gesamten verstrichenen Zeit und vergleiche Wiederholungsläufe nach Aufbau, Reparatur oder Standortwechsel. | <strong class="analysis-choice-single">TX Performance</strong> |

Die Referenz ist Bestandteil der wissenschaftlichen Fragestellung und nicht nur eine Darstellungsoption. Ein <strong class="defined-term">Vergleich im kontrollierten Aufbau</strong> bietet die stärkste Grundlage, einen beobachteten Unterschied lokalen Pfaden oder Bauteilen zuzuordnen – allerdings nur in dem Maß, in dem die übrigen Ketten kontrolliert sind. Ein <strong class="defined-term">Vergleich mit einer unabhängigen Referenzstation</strong> vergleicht zwei vollständig aufgebaute Stationen einschließlich QTH, Geräten, Gelände sowie lokaler Stör- und Rauschumgebung. Eine Referenznachbarschaft beschreibt das Target relativ zu einer wechselnden lokalen Population, nicht eine isolierte Antenne oder einen festen kalibrierten Standard.

Diese Perspektiven machen WSPRadar für weit mehr als formale Antennenvergleiche nützlich. Performance kann eine Ausgangsbasis für die Station schaffen, zeigen, wo sie zuverlässig gehört wird, richtungs- oder entfernungsabhängiges Verhalten sichtbar machen, wiederkehrende Tagesmuster erkennen und eingrenzen, wann eine intermittierende Veränderung aufgetreten ist. Benchmark kann Antennen, Speiseleitungen, Filter, Vorverstärker, Empfänger oder vollständige Pfade vergleichen, zwei Gesamtstationen gegenüberstellen oder eine Station in den Kontext ihrer aktiven lokalen Nachbarschaft einordnen.

WSPRadar kann **Form, Umfang und zeitliche Lage** einer Beobachtung bestimmen. Es kann zeigen, ob ein Unterschied breit, konzentriert, intermittierend, wiederkehrend oder nur durch eine schmale Stationsgruppe gestützt ist. Allein daraus folgt jedoch nicht, dass die Ursache Antennengewinn, Strahlungswirkungsgrad, Abstrahlwinkel, kalibrierte Empfängerempfindlichkeit, lokaler Störpegel oder ein bestimmtes Bauteil war. Keine nachträgliche Statistik kann eine Variable beseitigen, die der physische Versuch nicht kontrolliert hat.

<a id="sec-1-3"></a>

#### 0.2 Was ein Lauf liefert

Ein Lauf beantwortet eine klar begrenzte Stationsfrage und liefert das gewählte Benchmark- oder Performance-Ergebnis.

**Benchmark** verbindet ΔSNR mit Decode Outcomes und Evidenzabdeckung: Ein günstiger Signalpegelunterschied ist gemeinsam mit den nur einseitig decodierten Signalen zu beurteilen. **Performance** verbindet Reichweite, beide Gewichtungen der Dekodierrate und erfolgreiches Target-SNR. Beide zeigen Entfernung, Richtung, Zeit und beitragende Stationen.

Der zusammenhängende Evidenzpfad ist eine zentrale Stärke von WSPRadar. Beginne damit, **wo ein Muster auf der Karte auftritt**, wähle im **Segment-Inspektor** den geografischen Bereich und untersuche dann, **wie groß oder beständig es ist, wann es auftritt und welche Stationen es stützen**. Stationsansichten und Drill-Down verbinden die Zusammenfassungen mit einzelnen Beobachtungen. [Abschnitt 1.3](#sec-2-3-overview) führt in diesen Pfad ein; [Kapitel 2](#sec-3) erklärt die Interpretation jeder Analyse.

Übereinstimmung zwischen Geografie, Zeit, Stationen und einzelnen Beobachtungen innerhalb eines Laufs stärkt eine begrenzte Beschreibung. Experimentelle Wiederholbarkeit prüft erst ein weiterer, geeignet kontrollierter Lauf. UTC-Stunden-Ansichten fassen Beobachtungen verschiedener Tage zusammen; ob ein Tagesmuster tatsächlich wiederkehrte, muss in der chronologischen Ansicht geprüft werden.

Analysedefinition, verarbeitete Evidenz, Tabellen, Abbildungen und Metadaten lassen sich zur späteren Prüfung oder Weitergabe herunterladen. Bewahre die physischen Stationsnotizen dazu auf: WSPRadar kann den vollständigen Versuchsaufbau nicht erschließen. [Kapitel 8](#sec-8) erklärt die Grenzen für Berichterstattung und Reproduktion.

<a id="sec-1-4"></a>

#### 0.3 Der erste sinnvolle Lauf

Beginne mit einer gepflegten Demo. Ihre vorbereiteten Einstellungen und Versuchsnotizen lassen dich eine vollständige historische Benchmark- oder Performance-Analyse erkunden, bevor du die eigene Station einrichtest. [Abschnitt 1.1](#sec-2-1) erklärt den Einstieg.

Verfolge ein Merkmal von der Karte über die geografische und zeitliche Evidenz zu den beitragenden Stationen und zum Drill-Down. Prüfe, ob es bei vielen oder wenigen Stationen auftritt, ob es sich an einzelnen Tagen wiederholt und wie viel Benchmark-Evidenz auf gemeinsam decodierten Signalen beruht. Die Demo ist ein durchgearbeitetes Beispiel der Methode und keine Evidenz über deine Station.

Wähle für die eigene Station einen Vergleich mit einem kontrollierten Pfad, einer bekannten Station oder der lokalen Nachbarschaft, oder ermittle eine RX-/TX-Performance-Basislinie. Die kompakte Anleitung in [Abschnitt 1.1](#sec-2-1) beginnt beim WSPR-Betrieb und der Datenbankprüfung. Ziel ist ein Ergebnis, das du verstehen, hinterfragen, wiederholen und für eine Stationsentscheidung nutzen kannst.

<a id="documentation-toc"></a>

### Inhaltsverzeichnis

**Teil 0: Vorwort**

* [0. Warum WSPRadar?](#sec-1)
    * [0.0 WSPR in 2 Minuten](#sec-1-1)
    * [0.1 Was WSPRadar zeigen kann](#sec-1-0)
    * [0.2 Was ein Lauf liefert](#sec-1-3)
    * [0.3 Der erste sinnvolle Lauf](#sec-1-4)

**Teil I: Leitfaden für den Funkbetrieb**

* [1. Analyse auswählen und vorbereiten](#sec-2)
    * [1.1 Solide Versuchsgrundlage schaffen](#sec-2-1)
    * [1.2 Die zur Fragestellung passende Analyse wählen](#sec-2-2)
    * [1.3 Dem Evidenzpfad folgen](#sec-2-3-overview)
* [2. Analyse durchführen und auswerten](#sec-3)
    * [2.1 RX Benchmark](#sec-3-rx-benchmark)
        * [2.1.1 Referenzaufbau/-station](#sec-3-rx-benchmark-hardware)
        * [2.1.2 Referenznachbarschaft](#sec-3-rx-benchmark-local-median)
    * [2.2 TX Benchmark](#sec-3-tx-benchmark)
        * [2.2.1 Referenzaufbau/-station](#sec-3-tx-benchmark-simultaneous)
        * [2.2.2 Referenznachbarschaft](#sec-3-tx-benchmark-local-median)
    * [2.3 RX Performance](#sec-3-rx-performance)
    * [2.4 TX Performance](#sec-3-tx-performance)
    * [2.5 Vorübergehende ΔSNR-Abweichungen finden und prüfen](#sec-outlier)
        * [2.5.1 Wann dieses Diagnosewerkzeug sinnvoll ist](#sec-outlier-1)
        * [2.5.2 Wie die Erkennung praktisch arbeitet](#sec-outlier-2)
        * [2.5.3 Ein berichtetes Ereignis lesen und untersuchen](#sec-outlier-4)
        * [2.5.4 Selektivität anpassen und Ergebnis sichern](#sec-outlier-7)
* [3. Ergebnis absichern und kommunizieren](#sec-4)
    * [3.1 Breite, Konsistenz und Wiederholbarkeit beurteilen](#sec-4-1)
    * [3.2 Ergebnis durch Wiederholung und Kontrolle absichern](#sec-4-2)
    * [3.3 Evidenzgerechte Schlussfolgerung formulieren](#sec-4-3)
    * [3.4 Lauf und Kontext sichern](#sec-4-4)

**Teil II: Bedienelemente und Fehlersuche**

* [4. Bedienelemente und Konfiguration](#sec-5)
    * [4.1 Ablaufsteuerung](#sec-5-1)
    * [4.2 Frage, Target und Messzeitraum](#sec-5-2)
    * [4.3 Benchmark-Design und -Einstellungen](#sec-5-3)
    * [4.4 Filter und Evidenzschwellen](#sec-5-4)
    * [4.5 Karten-, Inspektor- und Exporteinstellungen](#sec-5-5)
    * [4.6 Bedienelemente der Benchmark-Ausreißererkennung](#sec-5-6)
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
    * [6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen](#sec-d-3)
    * [6.4 Analyseinfrastruktur und verwandte Werkzeuge](#sec-d-4)
    * [6.5 Was WSPRadar übernimmt, integriert und ergänzt](#sec-d-5)
* [7. Wissenschaftliche Methoden](#sec-7)
    * [7.1 Gemeinsame Datengrundlage](#sec-7-foundations)
        * [7.1.1 Spots, Identitäten und Zyklen](#sec-7-spots-identities-cycles)
        * [7.1.2 Leistungsnormierung und Zusammenfassung](#sec-7-normalization-consolidation)
        * [7.1.3 Target-Aktivität und Zulässigkeit](#sec-7-activity-eligibility)
    * [7.2 Benchmark: Unterschiede und gemeinsame Evidenz](#sec-7-benchmark)
        * [7.2.1 Decode Outcomes und fehlende Beobachtungen](#sec-7-benchmark-outcomes)
        * [7.2.2 Delta SNR und Referenzkorrektur](#sec-7-benchmark-delta)
        * [7.2.3 Stations- und Kartenaggregation](#sec-7-benchmark-aggregation)
        * [7.2.4 Joint-Evidenzanteil](#sec-7-benchmark-coverage)
        * [7.2.5 Referenznachbarschaft](#sec-7-neighborhood)
    * [7.3 Performance: Gelegenheiten und Erfolg](#sec-7-performance)
        * [7.3.1 Was zählt als Gelegenheit?](#sec-7-performance-opportunities)
        * [7.3.2 Dekodierraten und Gewichtung](#sec-7-performance-rates)
        * [7.3.3 Mindestens-einmal-Reichweite](#sec-7-performance-reach)
        * [7.3.4 Erfolgreiches Target-SNR](#sec-7-performance-snr)
    * [7.4 Bereich und Zusammenfassungen über Ort und Zeit](#sec-7-views)
        * [7.4.1 Bereich, Geografie und Filter](#sec-7-view-scope)
        * [7.4.2 Geografische Zusammenfassungen](#sec-7-view-geography)
        * [7.4.3 Chronologische Evidenz](#sec-7-view-time)
        * [7.4.4 Tage nach UTC-Stunde zusammenfassen](#sec-7-view-folding)
        * [7.4.5 Evidenz der ausgewählten Station](#sec-7-view-station)
        * [7.4.6 Streuung und Darstellungsskalen](#sec-7-view-spread)
    * [7.5 Wie belastbar ist die Schlussfolgerung?](#sec-7-claims)
        * [7.5.1 Abhängigkeit und Verzerrung](#sec-7-dependence-bias)
        * [7.5.2 Wiederholbarkeit und experimentelle Kontrolle](#sec-7-repeatability-control)
        * [7.5.3 Validierungsumfang](#sec-7-validation)
    * [7.6 Experimentelle ΔSNR-Ereignisanalyse](#sec-7-outliers)
        * [7.6.1 Abweichung von der lokalen Basislinie](#sec-7-outlier-departure)
        * [7.6.2 Basislinie und lokale Streuung](#sec-7-outlier-baseline)
        * [7.6.3 Qualifikation eines Kandidaten](#sec-7-outlier-qualification)
        * [7.6.4 Grenzen und Ereignisklassen](#sec-7-outlier-boundaries)
        * [7.6.5 Kontext und Grenzen](#sec-7-outlier-context)
* [8. Evidenzgerechte Aussagen und Reproduzierbarkeit](#sec-8)
    * [8.1 Aussageklassen und evidenzgerechte Formulierungen](#sec-8-1)
    * [8.2 Interpretationsgrenzen](#sec-8-2)
    * [8.3 Checkliste für Berichterstattung und Reproduzierbarkeit](#sec-8-3)
    * [8.4 Exportpaket der Analyse](#sec-8-4)
    * [8.5 Haftungsausschluss](#sec-8-5)
* [Literatur und Quellen](#sec-ref)

**Teil IV: Praktische Ergänzungen**

* [Anhang A: Parallele WSJT-X-Instanzen für simultanes RX](#sec-a)
    * [A.1 Zweite Instanz anlegen](#sec-a-1)
    * [A.2 Ausgangskonfiguration bei Bedarf kopieren](#sec-a-2)
    * [A.3 Alle Datenpfade trennen](#sec-a-3)
    * [A.4 Grenzen von WSJT-X für simultanes TX](#sec-a-4)
* [Anhang B: Simultanes TX Referenzaufbau/-station praktisch einrichten](#sec-simultaneous-tx-setup)
    * [B.1 Rufzeichen auswählen](#sec-simultaneous-tx-setup-1)
    * [B.2 Zeitplan angleichen und Signale trennen](#sec-simultaneous-tx-setup-2)
    * [B.3 Leistung und simultane Signalqualität prüfen](#sec-simultaneous-tx-setup-3)
    * [B.4 WSPRnet und ausgewählte Datenquelle prüfen](#sec-simultaneous-tx-setup-4)
    * [B.5 Gerätespezifische Einrichtung](#sec-simultaneous-tx-setup-5)
        * [B.5.1–B.5.2 QMX und QMX+ Virtual U3S sowie Ultimate3S](#sec-simultaneous-tx-setup-5-1)
        * [B.5.3 ZachTek-Firmware 2.19: Zufallswahl in getrennten Frequenzfenstern](#sec-simultaneous-tx-setup-5-3)
    * [B.6 Durch Tausch oder Kreuztausch bestätigen](#sec-simultaneous-tx-setup-6)
* [Anhang C: Referenz-SNR-Kalibrierung](#sec-reference-snr-calibration)
* [Lizenz](#sec-license)

---
<a id="part-i"></a>

## Teil I: Leitfaden für den Funkbetrieb

Dieser Teil führt von einer Stationsfrage zu einem Ergebnis, das du einordnen und berichten kannst. [Kapitel 1](#sec-2) bereitet den WSPR-Betrieb vor, hilft bei der Wahl von RX oder TX sowie Benchmark oder Performance und führt den gemeinsamen Evidenzpfad ein. [Kapitel 2](#sec-3) wendet ihn auf jede Analyse an und enthält ein optionales Diagnosewerkzeug für erfahrene Anwender zur Prüfung vorübergehender ΔSNR-Abweichungen. [Kapitel 3](#sec-4) hilft bei der nächsten Prüfung und beim Sichern des Ergebnisses. Exakte Bedienelemente und Fehlersuche stehen in Teil II, Berechnungen und wissenschaftliche Grenzen in Teil III.

In diesem Handbuch bezeichnet der **Versuch** den tatsächlichen Funkbetrieb und die physische Stationskonfiguration. Ein **Lauf** oder eine **Analyse** ist die in WSPRadar konfigurierte Verarbeitung der daraus entstandenen Beobachtungen. Ein **Ergebnis** ist die Performance- oder Benchmark-Evidenz, die dieser Lauf erzeugt.

---

<a id="sec-2"></a>

### 1. Analyse auswählen und vorbereiten

Beginne mit der Stationsfrage und dem physischen Versuch. Die Auswahl in der Benutzeroberfläche ergibt sich daraus; sie definiert die Fragestellung nicht.

<a id="sec-2-1"></a>

#### 1.1 Solide Versuchsgrundlage schaffen

Beginne mit einem Satz, der festhält, was geprüft wird und welche Beobachtung als Unterstützung gelten würde. Ein explorativer Lauf sucht nach einem möglichen Muster; ein bestätigender Lauf prüft ein bereits erkanntes Muster.

**Beginne mit einer Demo, wenn WSPRadar neu für dich ist.** Öffne `Demo laden`, wähle ein Profil und anschließend `Ausgewaehlte Demo starten`. Belasse für den ersten Lauf die vorbereiteten Einstellungen und lies die Versuchsnotizen. Folge dann dem passenden Leitfaden in [Kapitel 2](#sec-3).

**Vom WSPR-Betrieb zur ersten eigenen Analyse:**

1. **Verwertbare WSPR-Meldungen erzeugen.** Richte für RX einen WSPR-fähigen Empfänger und Decoder wie WSJT-X mit korrektem Empfangsrufzeichen, Locator, Band, Audioeingang und synchronisierter Uhr ein. Starte den Empfang und aktiviere den Spot-Upload; ein nur lokal gespeicherter Decode ist für WSPRadar nicht verfügbar. Konfiguriere für TX einen WSPR-Sender mit korrektem Rufzeichen, Locator, Band, synchronisierter Zeitsteuerung und zutreffender Leistungsangabe; entfernte Empfangsstationen liefern seine Spots. Das WSJT-X-Handbuch erklärt Funkgeräte-/Audioeinrichtung und WSPR-Bedienung <a href="#ref-12">[Ref-12]</a>.
2. **Vor der Analyse die Datenbank prüfen.** Kontrolliere erfolgreiche Meldungen unter dem exakten Empfangsrufzeichen bei RX beziehungsweise Senderufzeichen bei TX in WSPRnet und anschließend ihre Verfügbarkeit in der von WSPRadar verwendeten Datenbank. Prüfe gemeldeten Locator und UTC-Zeiten. Warte die Uploads ab und wähle ein abgeschlossenes Zeitfenster mit dem vorgesehenen Betrieb; eine feste Wartezeit garantiert keine Vollständigkeit. Eine schrittweise TX-Vorabprüfung findest du in [Anhang B.4](#sec-simultaneous-tx-setup-4). [Abschnitt 5.6](#sec-6-6) behandelt verzögerte Daten und Quellenstatus.
3. **Falls erforderlich den Vergleich vorbereiten.** Benchmark benötigt geeignete Beobachtungen von Target und Referenz in denselben WSPR-Zyklen. Prüfe den Referenzbetrieb unabhängig; beobachtete Target-Aktivität beweist keine Betriebsbereitschaft der Referenz. [Kapitel 2](#sec-3) hilft bei der Referenzwahl, [Anhang A](#sec-a) beim parallelen RX und [Anhang B](#sec-simultaneous-tx-setup) beim simultanen TX. Performance benötigt keine Referenz.
4. **Eine klare Analyse eingeben.** Wähle in Guided oder Classic RX/TX und Benchmark/Performance, das exakt hochgeladene Target-Rufzeichen, Target-QTH, ein Band und das UTC-Zeitfenster. Ergänze bei Benchmark das Referenzdesign und die erforderliche Kennung beziehungsweise den Radius. Prüfe Zusammenfassung und eine etwaige Referenzkorrektur und wähle dann `RX-Analyse starten` oder `TX-Analyse starten`. [Kapitel 4](#sec-5) erklärt die Bedienelemente. Ein Lauf liefert nur das gewählte Ergebnis.
5. **Ergebnis prüfen und sichern.** Folge dem passenden Leitfaden in [Kapitel 2](#sec-3) von der Karte zu einzelnen Stationen. Prüfe bei fehlender oder unerwartet dünner Evidenz zuerst [Kapitel 5](#sec-6), bevor du Schwellen lockerst. Sichere Export und Versuchsnotizen nach [Abschnitt 3.4](#sec-4-4).

**Den physischen Versuch nachvollziehbar halten.** Dokumentiere Antenne, Speiseleitung, Funkgerät, Tuner, Verstärkungs- oder Leistungseinstellungen, Decoder, Softwareversion, Zeitplan und beabsichtigte Änderungen. Halte Variablen außerhalb der Fragestellung so stabil wie praktisch möglich: bei TX tatsächliche und gemeldete Leistung, bei RX Verstärkung, Filterung, Audioführung, Decoder-Einstellungen und Upload-Verhalten. Halte die Uhren während des gesamten Versuchs synchron.

Lege vor einer bestätigenden Wiederholung Richtung, Band, gegebenenfalls Referenzdesign, Filter, Schwellen, Zeitplan und primären geografischen oder zeitlichen Bereich fest. Bewahre alternative Radien, Zeitfenster oder Bereiche als Sensitivitätsanalysen auf, statt nur das günstige Ergebnis auszuwählen.

<a id="sec-2-2"></a>

#### 1.2 Die zur Fragestellung passende Analyse wählen

| Betriebliche Fragestellung | Analyse |
|---|---|
| Wie unterscheiden sich zwei lokale Empfangspfade, zwei vollständige Empfangsstationen oder mein Empfänger und eine lokale Nachbarschaftsreferenz? | **RX Benchmark** |
| Wie unterscheiden sich zwei lokale Sendepfade, zwei vollständige Sendestationen oder mein Sender und eine lokale Nachbarschaftsreferenz? | **TX Benchmark** |
| Welche Signale decodiert mein Empfänger innerhalb bestätigter Gelegenheiten, wo, wann und wie beständig? | **RX Performance** |
| Wo und wie beständig wird mein Sender von Empfängern decodiert, deren Aktivität nachgewiesen ist? | **TX Performance** |

Wähle **Benchmark**, wenn die Frage ausdrücklich relativ zu einer Referenz gestellt wird. Die Referenz bestimmt die Bedeutung des Ergebnisses:

<a id="sec-2-5"></a>

* **Referenzaufbau/-station** vergleicht das Target mit einer exakten Referenzidentität in denselben WSPR-Zyklen. Ein kontrollierter lokaler Aufbau ist die stärkste Anordnung für eine Frage zu einem Bauteil oder Signalpfad, isoliert dieses Bauteil jedoch nur in dem Maß, in dem die übrigen Pfade kontrolliert sind. Eine unabhängige Referenz vergleicht vollständige installierte Stationen und ihre Betriebsumgebungen. Beide Anordnungen verwenden denselben Paarbildungsalgorithmus.

<a id="sec-2-6"></a>

* **Referenznachbarschaft (Lokaler Median)** vergleicht deine vollständige Empfangs- oder Sendestation mit einer wechselnden Referenz aus qualifizierenden WSPR-Beobachtungen der Umgebung innerhalb des ausgewählten Radius. Die Referenz wird für jede entfernte Station und jeden WSPR-Zyklus getrennt berechnet.

Untersuche damit, wo die beobachtete Leistung deiner Station über, nahe oder unter derjenigen der beitragenden lokalen Peers liegt, wenn keine geeignete feste Referenzstation verfügbar ist. Das Ergebnis beschreibt deine Station in ihrem beobachteten lokalen Umfeld; es isoliert weder Antennengewinn noch begründet es eine Rangliste aller Stationen in der Umgebung.

Verwende das engste Referenzdesign, das die beabsichtigte Aussage trägt. Aus einem Benchmark vollständiger Stationen oder einer Nachbarschaft lässt sich durch spätere Filterung oder Mittelung kein isolierter Antennengewinn ableiten.

Wähle **Performance**, wenn das Target selbst Gegenstand der Frage ist und keine Referenz benötigt wird. Sie verbindet Mindestens-einmal-Reichweite, Dekodierrate, erfolgreiches Target-SNR, Geografie, Zeit und stützende Evidenz für die vollständige Target-Station unter den ausgewählten Bedingungen.

<a id="sec-2-3-overview"></a>

#### 1.3 Dem Evidenzpfad folgen

Jedes abgeschlossene Ergebnis folgt demselben betrieblichen Pfad:

> <strong class="defined-term">Karte → Segment-Inspektor → Performance-/Benchmark-Evidenz → Zeitliche Evidenz → Station Insights → Evidenz der ausgewählten Station → Drill-Down</strong>

<a id="sec-3-4"></a>
<a id="sec-3-5"></a>

**Karte.** Lokalisiere das grobe Muster nach Entfernung und Richtung. Lies die Sektorfarbe zusammen mit der Anzahl beitragender Stationen und den zutreffenden Anzahlen von Gelegenheiten oder Joint Spots (den in [Kapitel 2](#sec-3) definierten Benchmark-Vergleichseinheiten). Ein eingefärbter Sektor ist eine Aufforderung zur näheren Prüfung und noch keine Schlussfolgerung.

<a id="sec-3-6"></a>
<a id="sec-3-6a"></a>
<a id="sec-3-6b"></a>

**Segment-Inspektor.** Wähle den zur Fragestellung passenden geografischen Bereich. Alle folgenden Evidenzansichten verwenden diesen aktiven Bereich. Dadurch lässt sich ein breites Kartenmuster in entfernungs- und richtungsabhängiges Verhalten aufteilen.

**Performance- oder Benchmark-Evidenz.** Verbinde bei Performance Reichweite, beide Gewichtungen der Dekodierrate und erfolgreiches Target-SNR. Verbinde bei Benchmark stationsgleichgewichtetes und beobachtungsbezogenes ΔSNR, Decode Outcomes und Joint-Evidenzanteil. Diese Größen beantworten unterschiedliche Fragen und sollten nicht zu einer einzigen Kennzahl verdichtet werden.

**Zeitliche Evidenz.** Nutze die chronologische Ansicht, um Veränderungen während des Laufs zu erkennen. Die UTC-Stunden-Ansicht fasst dieselben Stunden verschiedener Tage zusammen; prüfe die einzelnen Tage, bevor du ein Muster als wiederkehrend bezeichnest. Lies Signalpegel zusammen mit den stützenden Stations-, Gelegenheits- oder Joint-Spot-Anzahlen.

<a id="sec-3-7"></a>
<a id="sec-3-7a"></a>
<a id="sec-3-7b"></a>

**Station Insights.** Prüfe, ob viele Identitäten aus `Rufzeichen + Locator` das Muster stützen oder ob es sich auf wenige Funkwege konzentriert. Lies jeden stationsbezogenen Wert zusammen mit seinen Evidenzanzahlen.

**Evidenz der ausgewählten Station.** Untersuche einen repräsentativen, überraschenden oder besonders einflussreichen Funkweg. So wird sichtbar, ob die Segmentzusammenfassung auch diesen Pfad beschreibt, ob er intermittierend ist und ob sein zeitliches Muster vom breiteren Bereich abweicht.

<a id="sec-3-8"></a>

**Drill-Down.** Prüfe die beibehaltenen Gelegenheiten oder Joint Spots hinter dem Ergebnis. Kontrolliere in den Zeilen exakte Kennungen, Locatorwechsel, Zeitsteuerung, einseitige Evidenz und einzelne Ausreißer. Joint Spots und ihre ΔSNR-Werte werden in [Kapitel 2](#sec-3) eingeführt.

Der übrige Teil von Teil I wendet diesen gemeinsamen Pfad auf jede Analysefrage an, ohne sämtliche Titel, Achsen oder Layoutdetails aufzulisten.

---

<a id="sec-3"></a>

### 2. Analyse durchführen und auswerten

Verwende den Abschnitt für die gewählte Richtung und Ergebnisart. Exakte Bedienbezeichnungen, Standardwerte und Bereiche stehen in [Kapitel 4](#sec-5); die Regeln für Datenauswahl, Zuordnung, Gewichtung und Zusammenfassung in [Kapitel 7](#sec-7).

**Joint Spots beim Benchmark.** WSPRadar bildet einen Joint Spot, wenn für dieselbe entfernte Station und denselben WSPR-Zyklus nutzbare Target- und Referenz-SNR-Werte vorliegen: bei RX vom selben Sender, bei TX am selben Empfänger. Bei einer Referenznachbarschaft wird der Referenz-Wert aus den geeigneten lokalen Stationen berechnet. Als Station zählt hier eine exakte Kombination aus Rufzeichen und vollständig gemeldetem Locator; sie muss keine eigenständige physische Station bezeichnen. Joint Spots liefern **ΔSNR (Delta SNR)**; nur auf einer Seite gemeldete Signale liefern keinen solchen Wert. Performance verwendet stattdessen bestätigte Gelegenheiten, die in den zugehörigen Abschnitten erklärt werden.

<a id="sec-3-3"></a>
<a id="sec-3-rx-benchmark"></a>

#### 2.1 RX Benchmark

**Fragestellung.** Wie unterschied sich der Empfang des Targets von der gewählten Referenz bei denselben entfernten Sendern und WSPR-Zyklen?

**Die zentrale Größe: ΔSNR.** Jeder Joint Spot liefert Target-SNR minus Referenz-SNR, unter Berücksichtigung einer gegebenenfalls eingestellten Referenz-Korrektur. Positive Werte sprechen für das Target, negative für die Referenz; 0 dB bedeutet Gleichheit. Beispielsweise liegt bei +3 dB das Target-SNR um 3 dB über dem im Vergleich verwendeten Referenz-Wert. Ein entsprechender Antennengewinn ist damit nicht nachgewiesen.

**So liest du die Ergebnisse.**

**1. Kartenansicht: wo unterscheidet sich der Empfang?** Die Segmentfarbe zeigt den Median der ΔSNR-Mediane der berücksichtigten Sender; jeder Sender hat dasselbe Gewicht. Lies die dB-Skala zusammen mit der Stationszahl. Ungefärbte Segmente haben kein Ergebnis, das die Mindestanforderungen erfüllt. Stationsmarker unterscheiden Joint- von einseitigem Empfang. Im **Segment-Inspektor** wählst du Richtungen und Entfernungen für die folgenden Ergebnisse aus.

**2. Benchmark-Evidenz: wie groß und wie verbreitet ist der Unterschied?**

| Darstellung | Ablesen und einordnen |
|---|---|
| **Stationsmediane (Δ SNR)** | Jeder Sender geht mit einem ΔSNR-Median aus seinen Joint Spots ein. Die Balken zeigen den Stationsanteil je dB-Bereich. Überwiegend positive Mediane sprechen auf den meisten dieser Funkwege für das Target. Werte auf beiden Seiten von null zeigen Unterschiede zwischen den Funkwegen. |
| **Joint-Spot Δ SNR** | Jeder Joint Spot geht mit einem ΔSNR-Wert ein. Die Balken zeigen den Anteil der Joint Spots je dB-Bereich. So wird die Streuung über Stationen und Zeit sichtbar; häufig beobachtete Sender tragen mehr Werte bei. Vergleiche Lage und Streuung mit den Stationsmedianen. |

Beginne mit den Medianen; die Mittelwerte sind arithmetische Durchschnitte. Weichen die Verteilungen deutlich voneinander ab, prüfe die Stationen mit den meisten Joint Spots. [Abschnitt 7.2.3](#sec-7-benchmark-aggregation) veranschaulicht, warum die Ergebnisse unterschiedlich ausfallen können.

**3. Zeitliche Evidenz: wann tritt der Unterschied auf?** Verfolge in **Δ SNR im Zeitverlauf** die Intervallmediane im Vergleich zum gestrichelten Gesamtmedian: bleibt der Unterschied bestehen, kehrt er sich um oder tritt er nur kurz auf? Lies die beschrifteten dB-Werte an der nichtlinearen senkrechten Achse ab. Das Q1–Q3-Band umfasst, sofern angezeigt, die mittleren 50 % der ΔSNR-Werte aus Joint Spots; es ist kein Konfidenzintervall. Die Farbe zeigt die Konzentration der Joint Spots; leere Intervalle enthalten keine.

**Δ SNR nach UTC-Stunde** fasst dieselben Stunden mehrerer Tage zusammen. Suche nach Tagesmustern und prüfe anschließend die einzelnen Tage, bevor du von einem wiederkehrenden Muster sprichst.

**Datengrundlage prüfen.** Prüfe in Decode Outcomes sowohl die Stationsanteile als auch die Spot-Anteile. Die Anzahlen der Joint-Stationen und Joint Spots sowie **Decode Outcomes** und die **zeitliche Evidenzabdeckung des Benchmarks** zeigen, wie viele Stationen und Joint Spots den Vergleich tragen und wo die Abdeckung dünn ist. Der Joint-Evidenzanteil beschreibt den Anteil der Beobachtungen, für den Joint Spots vorliegen; er ist keine Erfolgsquote des Targets. Einseitiger Empfang kann Unterschiede nahe der Dekodierschwelle zeigen, liefert aber kein ΔSNR. Wenn viele einseitige Meldungen vorliegen, nenne sie auch in deiner Schlussfolgerung: ΔSNR beschreibt nur die Joint Spots. Da nur Zyklen mit beobachteter Target-Aktivität eingehen, sind einseitige Anzahlen keine symmetrischen Gewinne und Verluste. [Abschnitt 7.2.1](#sec-7-benchmark-outcomes) erklärt die Kategorien einschließlich asynchroner Beobachtungen.

**4. Station Insights: welche Funkwege erklären das Ergebnis?** Vergleiche die Sendermediane mit den Anzahlen der Joint Spots und der einseitigen Beobachtungen. Wähle nacheinander typische und auffällige Funkwege aus. Die **Evidenz der ausgewählten Station** zeigt, ob sie dem zeitlichen Gesamtmuster folgen oder nur zeitweise auftreten. Im **Drill-Down** kannst du einzelne Zyklen, Rufzeichen-/Locator-Kennungen und Korrekturvorzeichen prüfen.

**Nächster Schritt.** Wiederhole aussichtsreiche Vergleiche in einem weiteren Lauf. Ein Ergebnis über mehrere Sender, Zeiten und benachbarte Kartensegmente beschreibt mehr Funkwege und Bedingungen als wenige einzelne Beobachtungen. Beschränke richtungs- oder zeitabhängige Aussagen auf die betreffenden Bedingungen. Der Vergleich im selben Zyklus kontrolliert Sender und Zeitpunkt; Antennen, Empfangsketten, lokaler Störpegel und QTH-Bedingungen gehen weiterhin ein. Prüfe die Verfügbarkeit der Referenz unabhängig und nutze die folgenden Aufbauhinweise, um den Vergleich abzusichern.

<a id="sec-2-3"></a>
<a id="sec-3-rx-benchmark-hardware"></a>

##### 2.1.1 Referenzaufbau/-station

**Kontrollierter lokaler Aufbau.**

Vergleiche zwei lokale Antennen, Speiseleitungen, Filter, Vorverstärker, Empfänger oder vollständige Empfangsketten gleichzeitig am selben physischen Test-QTH. Prüfe vor dem Lauf unterschiedliche exakte Melderufzeichen und die Übereinstimmung des aufgelösten Referenzstandorts mit dem tatsächlichen Versuch. Der beabsichtigte Unterschied ist das untersuchte Bauteil oder der untersuchte Pfad; halte andere Bedingungen gleich oder charakterisiere ihre Unterschiede. Gemeinsam vorgesehene Komponenten müssen physisch gemeinsam genutzt werden; gleiches Grid-4 beweist weder Ko-Lokation noch gleiche Pfade.

Konfiguriere die Meldekennung jedes Empfangspfads getrennt in seiner Empfänger- oder Decodersoftware und prüfe, ob seine Spots unter genau dieser Kennung in der Datenbank erscheinen. Beispielsweise können `CALL` und `CALL/P` zwei Empfangspfade unterscheiden, wenn Meldesoftware und Datenbank diese Kennungen unverändert übernehmen. Ein so verwendeter Rufzeichenzusatz kennzeichnet den Empfangspfad in der hochgeladenen Meldung; er verändert nicht das WSPR-Nachrichtenformat des entfernten Senders. Die Empfehlung, bei kontrollierten TX-Benchmarks übereinstimmende Nachrichtenfolgen auszusenden, gilt deshalb nicht für diese RX-Meldekennungen.

Dies ist das stärkste RX-Design für die Zuordnung zu einem lokalen Pfad. Es vergleicht weiterhin vollständige dokumentierte Empfangspfade, solange Unterschiede bei Empfänger, Audio, Verstärkung, Decoder und Signalführung nicht charakterisiert sind. Eine breite, wiederkehrende ΔSNR-Verschiebung mit passender einseitiger Evidenz stützt ein besseres Abschneiden eines Pfads unter den geprüften Bedingungen. Nutze zur Bestätigung eine Kalibrierung mit gemeinsamem Eingang, einen Tausch der Verteilerausgänge oder einen Hardware-Kreuztausch; damit lassen sich Prüfobjekt und dauerhafter Kettenoffset möglicherweise unterscheiden. [Anhang C](#sec-reference-snr-calibration) erklärt die Referenz-SNR-Kalibrierung; [Anhang A](#sec-a) beschreibt getrennte WSJT-X-Instanzen.

<blockquote class="evidence-conclusion"><p>Unter dem dokumentierten simultanen RX-kontrollierten Aufbau beschrieben ΔSNR und Decode Outcomes den beobachteten Unterschied zwischen Target- und Referenzempfangspfad für die gemeinsamen Sender, Zyklen und den ausgewählten geografischen Bereich.</p></blockquote>

<a id="sec-3-rx-benchmark-buddy"></a>

**Unabhängige Station.**

Wähle eine identifizierbare vollständige Referenz-Empfangsstation mit bekanntem QTH, Rufzeichen, Geräten, Betriebsplan und lokaler Umgebung. Bei einem RX-Joint-Spot melden Target und Referenz denselben Sender im selben Zyklus; Target und Referenz bleiben eigenständige vollständige Empfangsstationen mit ihren eigenen Antennen, Geräten, Signalwegen und lokalen Störumgebungen. WSPRadar ermittelt das gemeldete Referenz-Grid-4 aus Datenbankmeldungen im ausgewählten Zeitfenster. Es darf dem Target-Grid-4 entsprechen, beweist aber keine Ko-Lokation.

Dies vergleicht vollständige installierte Empfangsstationen: relative Stärke nach Richtung, Entfernung und Zeit sowie Unterschiede der einseitigen Reichweite. Empfängerempfindlichkeit, Antennengewinn oder lokaler Störpegel lassen sich damit nicht als Ursache isolieren. Wiederhole den Vergleich mit derselben gut verstandenen Referenz und stabilen Betriebsbedingungen. Ein praktisches Beispiel bietet die gepflegte Griffiths/Squibb-Demo zum RX-Vergleich (#1); folge dort der Anleitung zur zeitlichen Evidenz und zum ausgewählten Funkweg.

<blockquote class="evidence-conclusion"><p>Für die gemeinsamen Senderpfade und Zyklen dieses Laufs beschrieben ΔSNR und Decode Outcomes, wie sich die beiden vollständigen Empfangsstationen unter ihren jeweiligen Umgebungsbedingungen verglichen.</p></blockquote>

<a id="sec-3-rx-benchmark-local-median"></a>

##### 2.1.2 Referenznachbarschaft

Die Referenz ist der zyklus- und funkwegspezifische Median aus je einem Beitrag jeder aktiven lokalen Empfängeridentität innerhalb des ausgewählten Radius. Die Zusammensetzung kann sich von Zyklus zu Zyklus ändern; das Ergebnis ist daher eine kontextbezogene lokale Basislinie und kein Vergleich mit einer festen Station.

Beitragende lokale Empfänger sind hier diejenigen mit qualifizierenden Meldungen desselben entfernten Senders im selben WSPR-Zyklus. Die Referenz repräsentiert daher die auf diesem Senderpfad und in diesem Zyklus beobachteten Empfänger und nicht jeden Empfänger innerhalb des Radius. ΔSNR erfordert zusätzlich eine qualifizierende Target-Meldung für denselben Sender und Zyklus.

Prüfe die beitragenden lokalen Identitäten, den Joint-Evidenzanteil und die Radiusabhängigkeit. Eine Veränderung kann vom Target, von einer veränderten Zusammensetzung der Nachbarschaft oder von beidem ausgehen. Wähle den primären Radius vor der Interpretation anhand lokaler Geografie und Stationsdichte; verwende weitere begründbare Radien als Sensitivitätsanalysen.

Interpretiere den Vergleich als Evidenz über vollständig aufgebaute Empfangsstationen. Antennen, Speiseleitungen, Empfänger, Decoder- und SNR-Meldeverhalten, lokales Rauschen und Störungen, Gelände und Ausbreitung können zum beobachteten Unterschied beitragen. Derselbe entfernte Sender und Zyklus beseitigen die Unterschiede zwischen den Empfangsstandorten nicht. Besteht die Nachbarschaft aus nur einem beitragenden Empfänger, ist dessen Wert ihr Median; dies liefert keine Evidenz für Übereinstimmung zwischen mehreren Stationen in der Umgebung.

<blockquote class="evidence-conclusion"><p>Für das ausgewählte Band und Zeitfenster sowie die ausgewählten Senderpfade und Zyklen zeigte die vollständige Empfangsstation des Targets das berichtete ΔSNR und die berichteten Decode Outcomes relativ zur beitragenden lokalen Empfängernachbarschaft. Dies belegt keinen entsprechenden Gewinnvorteil ihrer Antenne.</p></blockquote>

<a id="sec-3-tx-benchmark"></a>

#### 2.2 TX Benchmark

**Fragestellung.** Wie unterschied sich der Target-Sender von der gewählten Referenz bei denselben entfernten Empfängern in denselben WSPR-Zyklen?

**Die zentrale Größe: ΔSNR.** Jeder Joint Spot vergleicht Target- und Referenz-SNR bei einem Empfänger. WSPRadar normiert die SNR-Werte zunächst anhand der gemeldeten Sendeleistungen auf eine einheitliche Leistungsbasis von 30 dBm (1 W) und berücksichtigt anschließend eine gegebenenfalls eingestellte Referenz-Korrektur. Positives ΔSNR spricht für das Target, negatives für die Referenz; 0 dB bedeutet Gleichheit. Korrekte Leistungsangaben sind entscheidend: Der Vergleich kann weder eine falsche Leistungsangabe ausgleichen noch Antennengewinn nachweisen.

**So liest du die Ergebnisse.**

**1. Kartenansicht: wo ist das Target stärker oder schwächer?** Die Segmentfarbe zeigt den Median der ΔSNR-Mediane der berücksichtigten Empfänger; jeder Empfänger hat dasselbe Gewicht. Lies die dB-Skala zusammen mit den Empfänger- und Joint-Spot-Anzahlen. Ungefärbte Segmente haben kein Ergebnis, das die Mindestanforderungen erfüllt. Stationsmarker unterscheiden Joint- von einseitigen Meldungen. Im **Segment-Inspektor** wählst du Richtungen und Entfernungen für die folgenden Ergebnisse aus.

**2. Benchmark-Evidenz: wie groß und wie verbreitet ist der Unterschied?**

| Darstellung | Ablesen und einordnen |
|---|---|
| **Stationsmediane (Δ SNR)** | Jeder Empfänger geht mit einem ΔSNR-Median aus seinen Joint Spots ein. Die Balken zeigen den Empfängeranteil je dB-Bereich. Überwiegend positive Mediane sprechen auf den meisten dieser Funkwege für das Target. Werte auf beiden Seiten von null zeigen, dass das Ergebnis vom Funkweg abhängt. |
| **Joint-Spot Δ SNR** | Jeder Joint Spot geht mit einem ΔSNR-Wert ein. Die Balken zeigen den Anteil der Joint Spots je dB-Bereich. Häufig meldende Empfänger tragen mehr Werte bei. Vergleiche Lage und Streuung mit den Stationsmedianen: Zeigen einzelne Beobachtungen und Stationszusammenfassungen ein ähnliches Bild? |

Beginne mit den Medianen; die Mittelwerte sind arithmetische Durchschnitte. Weichen die Verteilungen deutlich voneinander ab, prüfe die Empfänger mit den meisten Joint Spots. [Abschnitt 7.2.3](#sec-7-benchmark-aggregation) erklärt die unterschiedliche Gewichtung.

**3. Zeitliche Evidenz: wann tritt der Unterschied auf?** Verfolge in **Δ SNR im Zeitverlauf** die Intervallmediane im Vergleich zum gestrichelten Gesamtmedian. Bleibt eine Verschiebung bestehen oder beschränkt sie sich auf einen kurzen Abschnitt? Lies die beschrifteten dB-Werte an der nichtlinearen senkrechten Achse ab. Das Q1–Q3-Band umfasst, sofern angezeigt, die mittleren 50 % der ΔSNR-Werte aus Joint Spots; es ist kein Konfidenzintervall. Die Farbe zeigt die Konzentration der Joint Spots; leere Intervalle enthalten keine.

**Δ SNR nach UTC-Stunde** fasst dieselben Stunden mehrerer Tage zusammen. Prüfe den chronologischen Verlauf an den einzelnen Tagen, bevor du ein Tagesmuster als wiederkehrend bezeichnest.

**Datengrundlage prüfen.** Prüfe in Decode Outcomes sowohl die Stationsanteile als auch die Spot-Anteile. Lies Empfänger- und Joint-Spot-Anzahlen zusammen mit **Decode Outcomes** und der **zeitlichen Evidenzabdeckung des Benchmarks**. Der Joint-Evidenzanteil beschreibt den Anteil der Beobachtungen, für den Joint Spots vorliegen; er ist keine Erfolgsquote des Targets. Einseitige Meldungen können Unterschiede in der Reichweite nahe der Dekodierschwelle zeigen, erlauben aber keinen leistungsnormierten Target-Referenz-SNR-Vergleich. Wenn viele einseitige Meldungen vorliegen, nenne sie auch in deiner Schlussfolgerung: ΔSNR beschreibt nur die Joint Spots. Da nur Zyklen mit beobachteter Target-Aktivität eingehen, sind einseitige Anzahlen keine symmetrischen Gewinne und Verluste. Die Kategorien erklärt [Abschnitt 7.2.1](#sec-7-benchmark-outcomes).

**4. Station Insights: welche Empfänger erklären das Ergebnis?** Vergleiche Empfängermediane mit den Anzahlen der Joint Spots und der einseitigen Beobachtungen. Wähle nacheinander typische und auffällige Empfänger aus. Die **Evidenz der ausgewählten Station** zeigt, ob sie dem zeitlichen Gesamtmuster folgen. Prüfe, ob ein scheinbarer Vorteil von einem bestimmten Empfänger oder der verwendeten NF-Frequenz abhängt. Im **Drill-Down** kannst du Empfängerkennung, WSPR-Zyklus, gemeldete Leistungen und Korrekturvorzeichen prüfen.

**Nächster Schritt.** Wiederhole einen Vergleich, den mehrere Empfänger stützen, mit genau gemessenen und korrekt gemeldeten Leistungen. Auch ein Unterschied in nur einer Richtung, einem Entfernungsbereich oder Zeitabschnitt kann nützlich sein; gib diese Bedingungen an. Der Vergleich umfasst vollständige Sendepfade einschließlich Verhalten der Senderkette, Frequenzgang, HF-Entkopplung und gegenseitiger Kopplung. Beachte die folgenden Aufbauhinweise, bevor du den Unterschied einem einzelnen Bauteil zuschreibst.

<a id="sec-2-4"></a>
<a id="sec-2-4-simultaneous"></a>
<a id="sec-3-tx-benchmark-simultaneous"></a>

##### 2.2.1 Referenzaufbau/-station

**Kontrollierter lokaler Aufbau.**

Verwende am selben physischen Test-QTH zwei unterscheidbare vollständige Sendeketten mit verschiedenen zulässigen exakten Rufzeichen, synchronisierten WSPR-Zyklen, freien getrennten Frequenzen, bestimmter tatsächlicher und gemeldeter Leistung sowie ausreichender HF-Entkopplung.

Verwende für kontrollierte simultane TX-Benchmarks zwei unterschiedliche Stationskennungen mit derselben überprüften Nachrichtenfolge und einem synchronisierten Sendezeitplan. Empfohlen werden folgende Anordnungen:

* **Zwei reguläre Rufzeichen, die jeweils Typ-1-Nachrichten aussenden.** Dies ist die einfachste Anordnung.
* **Zwei zusammengesetzte Rufzeichen, die jeweils eine Typ-2-/Typ-3-Folge aussenden.** Beide können dasselbe Basisrufzeichen mit unterschiedlichen Suffixen verwenden, beispielsweise `CALL/1` und `CALL/2`. Gib bei demselben Basisrufzeichen beiden Sendern unterschiedliche Suffixe. Prüfe, welche Suffixe in deinem Land für dein Rufzeichen und deinen Betrieb zulässig sind.

Richte bei der erweiterten Anordnung die Folgen so aus, dass Typ 2 gleichzeitig mit Typ 2 und Typ 3 gleichzeitig mit Typ 3 gesendet wird. Jeder der beiden Zyklen kann Joint Spots beitragen, wenn derselbe entfernte Empfänger in diesem Zyklus beide Kennungen meldet. WSPRadar wertet die Zwei-Minuten-Zyklen getrennt aus; es fasst die Folge nicht zu einer vierminütigen Beobachtung zusammen.

Prüfe die Senderkonfiguration und den tatsächlichen Sendezeitplan. Aus den Rufzeichen allein geht nicht hervor, welche Nachrichtenfolge die Firmware sendet oder ob beide Sender synchronisiert sind.

**Warum der Zeitplan wichtig ist.** Sendet ein Sender, während der andere laut Zeitplan schweigt, können die beibehaltenen Meldungen die einseitigen Decode Outcomes erhöhen und den Joint-Evidenzanteil verringern. Diese Kennzahlen spiegeln dann teilweise ungleiche Sendemöglichkeiten wider. Prüfe, ob beide Sender die entsprechenden Nachrichtentypen in denselben Zwei-Minuten-Zyklen aussenden, bevor du einseitige Meldungen als Hinweis auf einen Unterschied zwischen den Sendepfaden interpretierst. Übereinstimmende Zeitpläne verbessern die Vergleichbarkeit, beseitigen aber keine Lücken bei Decodierung, Identitätsauflösung oder Meldung.

Prüfe vor dem Versuch beide exakten Datenbankkennungen und ihre wahrheitsgemäß gemeldeten Grid-4-Werte. [Anhang B](#sec-simultaneous-tx-setup) beschreibt die praktische Einrichtung und Vorabprüfung. [Abschnitt 7.1.1](#sec-7-spots-identities-cycles) erklärt den Unterschied zwischen dieser empfohlenen Betriebsanordnung und den WSPRadar-Regeln für die Zuordnung innerhalb desselben Zyklus.

ΔSNR am selben Empfänger und im selben Zyklus vermeidet einen Vergleich zwischen verschiedenen Zyklen und ist das stärkste TX-Design, wenn beide Sendeketten kontrolliert werden können. Verglichen werden dennoch die vollständigen dokumentierten Sendepfade. Frequenzselektives QRM, Kettenfrequenzgang, Kopplung und Leistungsfehler können bestehen bleiben. Tausche die Frequenzpositionen und führe nach Möglichkeit einen Kreuztausch der geprüften Antennen oder Bauteile zwischen den Ketten durch.

<blockquote class="evidence-conclusion"><p>Unter dem dokumentierten simultanen kontrollierten Aufbau mit zwei Sendern beschrieben ΔSNR am selben Empfänger und im selben Zyklus sowie Decode Outcomes den beobachteten Unterschied zwischen Target- und Referenzsendepfad für die ausgewählten Empfänger und den geografischen Bereich.</p></blockquote>

<a id="sec-3-tx-benchmark-buddy"></a>

**Unabhängige Station.**

Verwende eine bekannte, separat identifizierbare vollständige Referenz-Sendestation, deren QTH, Rufzeichen, tatsächliche und gemeldete Leistung, Ausrüstung und Betriebsplan bekannt und nachvollziehbar sind. Bei einem TX-Joint-Spot meldet derselbe entfernte Empfänger beide Seiten in einem Zyklus; Target und Referenz bleiben jedoch eigenständige vollständige Sendestationen mit jeweils eigenen Sendern, Antennen, Speiseleitungen und Stationsumgebungen. WSPRadar ermittelt das gemeldete Referenz-Grid-4 aus dem ausgewählten Datenbankzeitfenster. Es darf dem Target-Grid-4 entsprechen; gleiches Grid-4 beweist keine physische Ko-Lokation.

Ein kontrollierter lokaler Aufbau und eine unabhängige Station verwenden dieselbe Analyse Referenzaufbau/-station. Die physische Anordnung bestimmt die Interpretation, nicht die Verwandtschaft der Rufzeichen. Beide benötigen zwei verschiedene gültige exakte Meldeidentitäten und Joint Spots; ein einzelner umgeschalteter Sender kann diesen Vergleich nicht liefern.

Interpretiere das Ergebnis als Benchmark vollständiger installierter Sendestationen. Der Vergleich von Joint Spots kontrolliert den Empfangsendpunkt, nicht die beiden Sendestandorte oder Funkwege. Die Genauigkeit der Leistungsangaben ist besonders wichtig. Wiederhole den Lauf mit derselben gut bekannten Referenz und stabilen Konfigurationen, statt die Referenzstation als absolut kalibrierten Standard zu behandeln.

<blockquote class="evidence-conclusion"><p>Für die gemeinsamen Empfangsstationen und Zyklen dieses Laufs beschrieben ΔSNR und Decode Outcomes, wie sich die beiden vollständigen Sendestationen unter ihren jeweiligen Betriebsumgebungen verglichen.</p></blockquote>

<a id="sec-3-tx-benchmark-local-median"></a>

##### 2.2.2 Referenznachbarschaft

Die Referenz ist der zyklus- und empfängerpfadspezifische Median aus je einem Beitrag jeder aktiven lokalen Senderidentität innerhalb des ausgewählten Radius. Sie ist eine wechselnde lokale Basislinie und keine feste Station. Das Ergebnis hängt von der aktiven Zusammensetzung und von der Genauigkeit der gemeldeten Leistungen ab.

Beitragende lokale Sender sind diejenigen, die derselbe entfernte Empfänger während desselben WSPR-Zyklus meldet. ΔSNR erfordert zusätzlich, dass dieser Empfänger in diesem Zyklus das Target meldet. Die Referenz repräsentiert daher die qualifizierenden lokalen Aussendungen, die an diesem Empfänger beobachtet wurden, und nicht jeden Sender in der Umgebung oder jeden Sendeversuch.

Prüfe die lokalen Beitragenden, den Joint-Evidenzanteil und die Radiusabhängigkeit. Berichte, ob das Target bei bestimmten Empfängern, Richtungen oder Zeiten eher über, nahe oder unter der aktiven lokalen Basislinie liegt. Eine Veränderung kann vom Target, vom lokalen Pool oder von beidem ausgehen.

Die Normierung auf Basis der gemeldeten Leistung entfernt den gemeldeten Sendeleistungsunterschied aus den SNR-Werten der Joint Spots. Sie überprüft weder die tatsächliche Senderleistung noch misst sie die abgestrahlte Leistung oder korrigiert unbekannte Speiseleitungsverluste. Derselbe entfernte Empfänger und Zyklus kontrollieren Empfangsendpunkt und Zeitpunkt; Sender in der Umgebung können dennoch unterschiedliche Installationen, Gelände- und Ausbreitungsbedingungen haben. Besteht die Nachbarschaft aus nur einem beitragenden Sender, ist dessen Wert ihr Median.

Wähle den primären Radius vor der Interpretation des Ergebnisses und berichte weitere begründbare Radien als Sensitivitätsanalysen. Lege für einen bestätigenden Lauf Band, Filter, Schwellen und primären Auswertungsbereich vorab fest und prüfe, ob sich die beitragende Nachbarschaft geändert hat.

<blockquote class="evidence-conclusion"><p>Für das ausgewählte Band und Zeitfenster sowie die ausgewählten Empfängerpfade und Zyklen zeigte die vollständige Sendestation des Targets das berichtete leistungsnormierte ΔSNR und die berichteten Decode Outcomes relativ zur beitragenden lokalen Sendernachbarschaft. Dies belegt nicht, dass ihre Antenne um die angezeigte Zahl von Dezibel besser ist.</p></blockquote>

<a id="sec-3-1"></a>
<a id="sec-3-2"></a>
<a id="sec-3-rx-performance"></a>

#### 2.3 RX Performance

**Beantwortete Frage.** Welche Sender empfing das Target, wie regelmäßig und mit welchem SNR bei erfolgreicher Dekodierung? Wie hing der Empfang von Richtung, Entfernung und Zeit ab?

**Die zentrale Kennzahl: Dekodierrate.** Sie gibt an, welchen Prozentsatz der bestätigten Gelegenheiten das Target dekodierte. Eine bestätigte RX-Gelegenheit betrifft eine exakte Senderidentität auf dem gewählten Band in einem WSPR-Zyklus: Das Target dekodiert deren Aussendung, oder ein anderer geeigneter Empfänger meldet sie, während zugleich die Target-Aktivität nachgewiesen ist. Ein erfolgreicher Target-Decode bestätigt beide Endpunkte und zählt auch ohne Meldung eines weiteren Empfängers. Dessen Meldung allein belegt nicht, dass das Target zugehört hat. [Abschnitt 7.3](#sec-7-performance) definiert die Einordnung.

**Voraussetzungen.** Verwende das exakte Melderufzeichen und QTH des Targets, ein Band und ein Zeitfenster mit nachweisbarer Aktivität des Target-Empfängers. Halte die Empfangskette stabil. Performance betrachtet die vollständige Empfangsstation ohne Referenz; ein einzelnes Bauteil wird damit nicht isoliert.

**Dem Evidenzpfad folgen.**

**1. Kartenansicht: Wo ist der Empfang breit oder regelmäßig?** Die Sektorfarbe zeigt die **Stationsgleichgewichtete Dekodierrate**: den Mittelwert der einzelnen Raten qualifizierender Sender, mit gleichem Gewicht je Identität. Marker und Anzahlen am Kartenfuß unterscheiden mindestens einmal gehörte Sender von solchen, die nur andernorts gehört wurden. Lies Prozentskala und Stationsanzahlen zusammen, um Richtungsmuster zu erkennen; die Kartenfarbe misst keine Empfängerempfindlichkeit. Im **Segment-Inspektor** wählst du Richtungen und Entfernungen für alle nachfolgenden Ergebnisse.

**2. Performance-Evidenz: Wie passen Reichweite, Regelmäßigkeit und Signalstärke zusammen?**

| Darstellung | Ablesen und einordnen |
|---|---|
| **Vom Target mindestens einmal gehörte TX-Stationen nach Entfernung** | Der Prozentsatz qualifizierender Sender, die in jedem Entfernungsbereich mindestens einmal gehört wurden. Das beschreibt die Breite des Empfangs, nicht dessen Regelmäßigkeit. Lies die Darstellung zusammen mit der Dekodierrate. Mehr Zeit bietet mehr Gelegenheiten, jede Station zu hören; ändert sich die qualifizierende Population, kann der Prozentsatz dennoch steigen oder fallen. |
| **RX Dekodierrate nach Entfernung der TX-Station** | Die **Stationsgleichgewichtete Dekodierrate** gewichtet die Rate jedes Senders gleich. Die **Dekodierrate auf Gelegenheitsebene** teilt alle erfolgreichen Decodes durch alle bestätigten Gelegenheiten; häufig beobachtete Sender haben dadurch mehr Einfluss. Weichen die Linien voneinander ab, prüfe diese Sender und ihre Anzahlen, bevor du die gesamte Population beschreibst. |
| **Erfolgreiches Target-SNR nach Entfernung der TX-Station** | Der Median der senderspezifischen Mediane des erfolgreichen SNR je Entfernungsbereich, anhand der gemeldeten Leistung auf einheitlich **30 dBm (1 W)** Sendeleistung normiert. Weniger negative Werte bedeuten bei erfolgreichen Decodes ein stärkeres Signal gegenüber dem Rauschen. Für verpasste Signale liegt hier kein Target-SNR vor; vergleiche die Darstellung mit der Dekodierrate, bevor du auf besseren Empfang schließt. |

**Evidenzumfang prüfen.** Vergleiche die Anzahl qualifizierender Stationen mit der Anzahl bestätigter Gelegenheiten. Viele Gelegenheiten von wenigen Sendern liefern wiederholte Beobachtungen weniger Funkwege; Übereinstimmung über mehr Sender ist breiter abgestützt. In der SNR-Darstellung umfasst Min-Max bei zwei beitragenden Stationen deren beide Mediane; bei drei oder mehr umfasst der IQR die mittleren 50 % der Stationsmediane. Dies beschreibt die Streuung, nicht die Sicherheit einer Aussage über eine größere Population.

**3. Zeitliche Evidenz: Wann ändert sich der Empfang?** **Abweichung des erfolgreichen RX-SNR im Zeitverlauf** vergleicht erfolgreiche Decodes jedes Senderpfads mit dessen eigenem Median des erfolgreichen SNR über den Lauf. Werte über **0 dB** bedeuten stärkeres SNR als für erfolgreiche Decodes auf diesem Funkweg üblich, darunter schwächeres. Verfolge den Median und lies **Evidenz im Zeitverlauf** dazu: Stations- und Gelegenheitsbalken zeigen den Evidenzumfang; die beiden Dekodierraten zeigen, ob sich zugleich die Dekodierbarkeit änderte. Farbe zeigt die Häufung von Beobachtungen, nicht stärkeren Empfang; ein dargestelltes Q1–Q3-Band beschreibt Streuung und ist kein Konfidenzintervall.

**Abweichung des erfolgreichen RX-SNR nach UTC-Stunde** und **Evidenz nach UTC-Stunde (1-h-Bins)** fassen gleiche Stunden verschiedener Tage zusammen. Suche nach einem möglichen Tagesmuster und prüfe anschließend die einzelnen Tage, bevor du es als wiederkehrend bezeichnest. Ein fehlender SNR-Wert bedeutet nicht Signalstärke null.

**4. Station Insights: Welche Funkwege erklären das Ergebnis?** Lies die Dekodierrate jedes Senders zusammen mit den Anzahlen **Vom Target gehört** und **Nur von anderen gehört**. Wähle einen typischen, einen auffälligen und jeden Funkweg mit besonders vielen Gelegenheiten. Die **Evidenz der ausgewählten Station** zeigt dessen erfolgreiches SNR auf einheitlicher 1-W-Basis und den Verlauf seiner Gelegenheiten statt der im Segment dargestellten Abweichungen vom üblichen Pegel jedes Funkwegs. Prüfe, ob die Veränderungen zum übergreifenden Muster passen. **Drill-Down** prüft einzelne Zyklen: **Nur von anderen gehört** bezeichnet einen verpassten Decode, den ein anderer Empfänger bei nachgewiesener Target-Aktivität stützt. Außerdem werden extern bestätigte Erfolge von Erfolgen unterschieden, die nur das Target meldete; Letztere sind bereits genau einmal in Erfolgen und Gelegenheiten enthalten.

**Nächster Schritt.** Breite Reichweite bei hoher Dekodierrate bedeutet, dass viele Funkwege regelmäßig empfangen wurden; bei niedrigeren Raten war der Empfang wechselhaft. Begrenzte Reichweite bei hohen Raten bedeutet, dass weniger Funkwege gehört wurden, diese aber vergleichsweise regelmäßig. Bleibt das erfolgreiche SNR stabil oder steigt es bei fallender Dekodierrate, können schwächere Signale unter die Dekodierschwelle gefallen sein. Prüfe die betreffenden Funkwege und wiederhole aufschlussreiche richtungs-, entfernungs- oder UTC-abhängige Muster in einem weiteren geeigneten Zeitfenster.

RX Performance umfasst Antenne, Speiseleitung, Empfänger, Verstärkung, Filterung, Decoder, lokalen Rausch- und Störpegel sowie Ausbreitung. Sie misst weder Empfängerempfindlichkeit, Antennengewinn, absoluten Rauschpegel noch Ausbreitungsart direkt. Für eine Aussage über eine einzelne Hardwareänderung verwende einen kontrollierten RX Benchmark oder einen Kreuztausch statt nur zeitlich getrennter Vorher-Nachher-Performance-Läufe.

<p class="evidence-conclusion-label"><strong>Evidenzgerechte Schlussfolgerung.</strong></p>

<blockquote class="evidence-conclusion"><p>Für diesen Target-Empfänger, dieses Band, dieses UTC-Zeitfenster und die ausgewählte Senderpopulation beschreibt RX Performance die Mindestens-einmal-Reichweite, die Dekodierrate innerhalb bestätigter Senderzyklen, das SNR erfolgreicher Decodes sowie den geografischen und zeitlichen Umfang dieser Beobachtungen. Nenne die verwendete Gewichtung, die Unterstützung durch Stationen und Gelegenheiten und ob das Muster breit, intermittierend, richtungsabhängig, entfernungsabhängig oder wiederkehrend war.</p></blockquote>

<a id="sec-3-tx-performance"></a>

#### 2.4 TX Performance

**Beantwortete Frage.** Welche aktiven Empfänger hörten das Target, wie regelmäßig und mit welchem SNR bei erfolgreicher Dekodierung? Wie hing das Ergebnis von Richtung, Entfernung und Zeit ab?

**Die zentrale Kennzahl: Dekodierrate.** Sie gibt an, bei welchem Prozentsatz der bestätigten Empfängergelegenheiten das Target dekodiert wurde. Eine bestätigte TX-Gelegenheit betrifft eine exakte Empfängeridentität auf dem gewählten Band in einem WSPR-Zyklus: Dieser Empfänger dekodiert das Target oder einen anderen qualifizierenden Sender, während zugleich die Target-Aktivität nachgewiesen ist. Eine erfolgreiche Target-Meldung bestätigt beide Endpunkte und zählt auch dann, wenn dieser Empfänger keinen anderen Sender meldet. Wird das Target andernorts gehört, belegt dies die Target-Aktivität, aber nicht, dass dieser bestimmte stille Empfänger zugehört hat. [Abschnitt 7.3](#sec-7-performance) definiert den Nenner.

**Voraussetzungen.** Verwende das exakte Target-Rufzeichen und QTH, ein Band und ein Zeitfenster, in dem das Target in Betrieb war. Halte HF-Pfad, Sendeplan und tatsächliche Leistung stabil und melde die Leistung korrekt. Performance betrachtet die vollständige Sendestation, kein isoliertes Bauteil.

**Dem Evidenzpfad folgen.**

**1. Kartenansicht: Wo wird das Target gehört?** Die Sektorfarbe zeigt die **Stationsgleichgewichtete Dekodierrate**: den Mittelwert der einzelnen Raten qualifizierender Empfänger, mit gleichem Gewicht je Identität. Marker und Anzahlen am Kartenfuß unterscheiden Empfänger, die das Target mindestens einmal hörten, von solchen, die nur andere qualifizierende Signale hörten. Lies Prozentskala und Empfängeranzahlen zusammen, um den beobachteten Sendebereich und Richtungsmuster zu erkennen. Im **Segment-Inspektor** wählst du Richtungen und Entfernungen für alle nachfolgenden Ergebnisse.

**2. Performance-Evidenz: Wie passen Reichweite, Regelmäßigkeit und Signalstärke zusammen?**

| Darstellung | Ablesen und einordnen |
|---|---|
| **RX-Stationen, die das Target mindestens einmal hörten, nach Entfernung** | Der Prozentsatz qualifizierender aktiver Empfänger, die das Target in jedem Entfernungsbereich mindestens einmal hörten. Das beschreibt Reichweite, nicht regelmäßigen Empfang. Lies die Darstellung zusammen mit der Dekodierrate und beachte, dass Beobachtungsfenster und verfügbare Empfänger diese Reichweite beeinflussen. |
| **TX Dekodierrate nach Entfernung der RX-Station** | Die **Stationsgleichgewichtete Dekodierrate** gewichtet die Rate jedes Empfängers gleich. Die **Dekodierrate auf Gelegenheitsebene** teilt alle erfolgreichen Target-Meldungen durch alle bestätigten Gelegenheiten; häufig beobachtete Empfänger haben dadurch mehr Einfluss. Weichen die Linien voneinander ab, prüfe diese Empfänger und ihre Anzahlen, bevor du die gesamte Population beschreibst. |
| **Erfolgreiches Target-SNR nach Entfernung der RX-Station** | Der Median der empfängerspezifischen Mediane des erfolgreichen Target-SNR je Entfernungsbereich, anhand der gemeldeten Target-Leistung auf einheitlich **30 dBm (1 W)** normiert. Weniger negative Werte bedeuten stärkere erfolgreiche Meldungen gegenüber dem Empfängerrauschen. Für verpasste Target-Signale liegt hier kein SNR vor; vergleiche die Darstellung mit der Dekodierrate, bevor du auf bessere Performance schließt. |

**Evidenzumfang prüfen.** Vergleiche die Anzahl qualifizierender Empfänger mit der Anzahl bestätigter Gelegenheiten. Viele Gelegenheiten von wenigen Empfängern beschreiben diese Funkwege wiederholt; Übereinstimmung über mehr Empfänger ist breiter abgestützt. In der SNR-Darstellung umfasst Min-Max bei zwei beitragenden Empfängern deren beide Mediane; bei drei oder mehr umfasst der IQR die mittleren 50 % der Empfängermediane. Dies beschreibt die Streuung, nicht die Sicherheit einer Aussage über eine größere Population.

**3. Zeitliche Evidenz: Wann ändert sich das Sendeergebnis?** **Abweichung des erfolgreichen TX-SNR im Zeitverlauf** vergleicht erfolgreiche Target-Meldungen jedes Empfängers mit dem Median des erfolgreichen SNR auf diesem Funkweg über den Lauf. Werte über **0 dB** bedeuten stärkeres SNR als für erfolgreiche Meldungen auf diesem Funkweg üblich, darunter schwächeres. Verfolge den Median und lies **Evidenz im Zeitverlauf** dazu: Empfänger- und Gelegenheitsbalken zeigen den Evidenzumfang; die beiden Dekodierraten zeigen, ob sich zugleich die Dekodierbarkeit änderte. Farbe zeigt die Häufung von Beobachtungen, nicht stärkere Meldungen; ein dargestelltes Q1–Q3-Band beschreibt Streuung und ist kein Konfidenzintervall.

**Abweichung des erfolgreichen TX-SNR nach UTC-Stunde** und **Evidenz nach UTC-Stunde (1-h-Bins)** fassen gleiche Stunden verschiedener Tage zusammen. Suche nach einem möglichen Tagesmuster und prüfe anschließend die einzelnen Tage, bevor du es als wiederkehrend bezeichnest. Ein fehlender SNR-Wert bedeutet nicht Signalstärke null.

**4. Station Insights: Welche Empfänger erklären das Ergebnis?** Lies die Dekodierrate jedes Empfängers zusammen mit den Anzahlen **Target gehört** und **Nur andere Signale gehört**. Wähle typische und auffällige Funkwege sowie Empfänger mit besonders vielen Gelegenheiten. Die **Evidenz der ausgewählten Station** zeigt das erfolgreiche Target-SNR dieses Empfängers auf einheitlicher 1-W-Basis und den Verlauf seiner Gelegenheiten statt der im Segment dargestellten Abweichungen vom üblichen Pegel jedes Funkwegs. Prüfe, ob dies zum übergreifenden Muster passt oder einen funkwegspezifischen Effekt zeigt. **Drill-Down** prüft Target-Meldungen und Empfängeraktivität: **Nur andere Signale gehört** bezeichnet einen verpassten Target-Decode, bei dem derselbe Empfänger ein anderes qualifizierendes Signal hörte, während das Target nachweislich aktiv war. Target-Erfolge ohne weiteres qualifizierendes Signal an diesem Empfänger sind bereits genau einmal in Erfolgen und Gelegenheiten enthalten; ihre gesonderte Herkunftsangabe ist keine zusätzliche Gesamtzahl.

**Nächster Schritt.** Breite Reichweite bei hoher Dekodierrate bedeutet, dass viele aktive Empfänger das Target regelmäßig hörten; bei niedrigeren Raten war der Sendebereich groß, der Empfang aber wechselhaft. Ein beständiges Richtungs- oder Entfernungsmuster kann mit dem installierten Antennensystem und Gelände vereinbar sein; eine kurze Verbesserung kann Ausbreitung oder Empfängerverfügbarkeit widerspiegeln. Stabiles erfolgreiches SNR bei fallender Dekodierrate kann bedeuten, dass nur stärkere Meldungen verbleiben. Prüfe die betreffenden Funkwege und wiederhole aufschlussreiche Muster in einem weiteren geeigneten Zeitfenster.

TX Performance umfasst Sender, tatsächliche Leistung, Speiseleitung, Anpassung, Antenne, Gelände, entfernte Empfangssysteme, Rausch- und Störpegel sowie Ausbreitung. Eine Normierung anhand der gemeldeten Leistung kann weder eine falsche Leistungsangabe noch einen ungemessenen Speiseleitungsverlust korrigieren. Sie misst EIRP, Wirkungsgrad, Antennengewinn oder Abstrahlwinkel nicht direkt. Verwende TX Benchmark, wenn die Frage lautet, ob sich ein Sendepfad von einem anderen unterscheidet.

<p class="evidence-conclusion-label"><strong>Evidenzgerechte Schlussfolgerung.</strong></p>

<blockquote class="evidence-conclusion"><p>Für diesen Target-Sender, dieses Band, dieses UTC-Zeitfenster und die ausgewählte Population aktiver Empfänger beschreibt TX Performance die Mindestens-einmal-Reichweite, die Dekodierrate innerhalb bestätigter Empfängerzyklen, das erfolgreich gemeldete SNR sowie den geografischen und zeitlichen Umfang dieser Beobachtungen. Nenne Gewichtung, Unterstützung durch Empfänger und Gelegenheiten, die Grundlage der gemeldeten Leistung und ob das Muster breit, intermittierend, richtungsabhängig, entfernungsabhängig oder wiederkehrend war.</p></blockquote>

<a id="sec-outlier"></a>

#### 2.5 Vorübergehende ΔSNR-Abweichungen finden und prüfen

**Beantwortete Frage.** Hat sich ein exakter Funkweg `Rufzeichen + Locator` vorübergehend so weit über oder unter sein stabiles erwartetes lokales ΔSNR verschoben, dass die konfigurierten Anforderungen an Abweichung, robusten z-Wert und Baseline-Stabilität erfüllt sind?

**Dies ist ein optionales Diagnosewerkzeug für erfahrene Anwender und nicht für den routinemäßigen Einsatz in jeder Benchmark-Analyse gedacht.** Beginne mit dem gewöhnlichen Evidenzpfad des Benchmarks. Aktiviere den Ausreißerbericht, wenn ein kontrollierter Benchmark genügend Joint Spots um den interessierenden Zeitraum aufweist und die vorübergehende Änderung der Fragestellung dient. Der Detektor liefert Intervalle zur fachkundigen Prüfung; er erstellt weder eine Rangfolge der größten rohen ΔSNR-Werte noch erklärt er deren physische Ursache.

<a id="sec-outlier-1"></a>

##### 2.5.1 Wann dieses Diagnosewerkzeug sinnvoll ist

Nutze den Detektor ausschließlich mit Benchmark-Evidenz. Seine native Evidenzeinheit ist ein simultaner **Joint Spot** mit Target-SNR und korrigiertem Referenz-SNR und damit einem ΔSNR-Wert. Outcomes `Only Target` und `Only Reference` bleiben nützlicher Diagnosekontext, können ein Ereignis aber nicht selbst qualifizieren.

Achte auf wiederholte Joint Spots vor, während und nach der vermuteten Änderung. Der Detektor enthält sich, wenn sich nicht auf beiden Seiten eine belastbare lokale Baseline stützen lässt. Ein leerer Bericht kann bedeuten, dass die beibehaltenen Joint Spots die konfigurierten Anforderungen nicht erfüllten oder die lokale Evidenz unzureichend beziehungsweise instabil war. Er belegt nicht, dass der Funkweg unverändert blieb.

Aktiviere **`ΔSNR-Ausreißerkandidaten melden`**, lege die drei Experteneinstellungen aus [Abschnitt 4.6](#sec-5-6) fest und starte die Analyse anschließend manuell. Eine Änderung des Schalters oder einer Schwelle kennzeichnet die Analysedefinition als geändert, startet aber nicht automatisch einen neuen Lauf.

<a id="sec-outlier-2"></a>
<a id="sec-outlier-3"></a>

##### 2.5.2 Wie die Erkennung praktisch arbeitet

Für jeden exakten Funkweg behält WSPRadar die Joint Spots zu ihren nativen WSPR-Zykluszeiten bei und:

1. schätzt das erwartete lokale ΔSNR aus robusten Zusammenfassungen vor und nach einer möglichen Abweichung, wobei der Kandidat selbst ausgeschlossen bleibt;
2. verlangt genügend belegte Evidenz auf beiden Seiten der Baseline und Übereinstimmung innerhalb des konfigurierten Höchstunterschieds;
3. gruppiert zeitlich nahe Abweichungen von dieser Baseline mit gleichem Vorzeichen anhand der beobachteten Evidenzkadenz des Funkwegs;
4. wendet unabhängig von der Dauer dieselben Regeln für absolute Abweichung, robusten z-Wert und Vorzeichenübereinstimmung an und
5. entfernt schwache führende und nachlaufende Joint Spots, sodass beide Endpunkte die Schwellen für Abweichung und robusten z-Wert jeweils einzeln erfüllen.

Schwächere Joint Spots dürfen stärkere innerhalb eines Intervalls verbinden, aber seine äußeren Grenzen nicht verlängern. Ein gescheiterter breiter Kandidat kann an einer gestützten Rückkehr zur Baseline geteilt werden: Ein starker innerer Abschnitt wird dann geprüft, ohne eine neue, günstigere Baseline auszuwählen.

Die Erkennung endet vor der Darstellungsaggregation der **Zeitlichen Evidenz**. Ein anderes Darstellungs-Bin wie `1h` oder `6h` kann kein Ereignis erzeugen, zusammenführen, teilen oder entfernen. Nachdem sich Funkwegereignisse einzeln qualifiziert haben, können zeitgleiche Ereignisse mit demselben Abweichungsvorzeichen in einer gemeinsamen Prüfkarte erscheinen:

| Funkwegübergreifender Kontext | Bedeutung |
|---|---|
| **Funkwegspezifisch** | Ein Funkweg. |
| **Richtungskohärent** | Mehrere Funkwege in benachbarten Kompasssektoren. |
| **Bereichsweit** | Mehrere getrennte Richtungen. |
| **Mehrere Funkwege** | Mehrere Funkwege, wobei für mindestens einen Beitragenden keine Richtung verfügbar ist. |

Dieser Kontext verändert nicht, ob ein einzelner Funkweg qualifiziert wird. [Abschnitt 7.6](#sec-7-outliers) erklärt den experimentellen Detektor, seine Evidenz und die wesentlichen Qualifikationsprüfungen.

<a id="sec-outlier-4"></a>
<a id="sec-outlier-5"></a>
<a id="sec-outlier-6"></a>

##### 2.5.3 Ein berichtetes Ereignis lesen und untersuchen

Lies die Ereigniskarte vom Intervall bis zu den Joint Spots, die es stützen:

| Berichtsangabe | Bedeutung und nächster Prüfschritt |
|---|---|
| **Spot-Impuls**, **Kurzer Ausbruch**, **Anhaltende Auslenkung** | Zeitliche Form nach der Grenzkürzung. Die Klassen verwenden dieselben Qualifikationsschwellen und drücken keine unterschiedliche Gewissheit aus. |
| Exakter Funkweg und Richtung | Jede Funkwegzeile nennt `Rufzeichen + Locator` und Richtung; untersuche genau diesen Funkweg und Zeitraum. |
| **Erwartetes lokales ΔSNR** | Die zweiseitige Baseline, bei deren Berechnung der Kandidat ausgeschlossen bleibt. |
| **Beobachteter ΔSNR-Median** | Der Median der beibehaltenen Joint Spots im berichteten Intervall. |
| **Größte Einzelzyklusabweichung** | Die betragsmäßig größte Abweichung von der Baseline unter den beibehaltenen Joint Spots, mit ihrem Vorzeichen. Diese Berichts-/Exportgröße unterscheidet sich vom `*` im Zeitplot aller Funkwege. |
| **Chronologische WSPR-Zyklusevidenz** | Bei mehreren Joint Spots führt die Tabelle UTC-Zeit, Funkweg, Richtung, lokale Baseline, ΔSNR und Abweichung von der Baseline (Residuum) auf. Ein Spot-Impuls aus nur einem Joint Spot benötigt keine doppelte Evidenztabelle. |

Im Zeitplot aller Funkwege wählt ein `*` je Prüfereignis den Joint Spot mit betragsmäßig größtem Residuum **unter den einzeln qualifizierenden Joint Spots** aus. Eine ungestützte oder nicht qualifizierende Episodenspitze kann diesen Marker nicht liefern, auch wenn sie die berichtete **Größte Einzelzyklusabweichung** liefert.

**Als Nächstes den Funkweg prüfen.** Für jeden exakten Funkwegzeitraum stehen zwei Aktionen bereit. Beide wählen den Funkweg aus, laden den Drill-Down vor und öffnen den **`Ausreißerfokus`**:

| Aktion | Ziel |
|---|---|
| **`↓ In Station Insights anzeigen`** | Station Insights für die breitere Laufhistorie des Funkwegs. |
| **`↓ Drill-Down-Details anzeigen`** | Direkt zum Drill-Down für die Detailprüfung. |

Der Fokus umfasst die vollständige gestützte Baseline-Flanke vor dem Ereignis, die geschützte vorläufige Episode und die Baseline-Flanke danach. Er wird nur am abgeschlossenen Analysefenster begrenzt und darf länger als 24 Stunden sein. Die fokussierte ΔSNR-Abbildung zeigt jeden beibehaltenen Joint Spot zu seiner nativen Zeit statt eines Binmedians, IQR oder einer Dichteschicht.

**Fokusmarker und Hilfslinien gemeinsam lesen.** Identische `*`-Marker kennzeichnen jeden Joint Spot im aktuellen Fenster, der als Teil eines berichteten Kandidaten einzeln sowohl die konfigurierte Abweichungsschwelle als auch das robuste-z-Kriterium erfüllt; dies umfasst jeden solchen Joint Spot eines Ausbruchs oder einer Episode. Anders als hier zeigt der Zeitplot aller Funkwege nur einen repräsentativen Stern je Prüfereignis.

Ein dezentes Band **Fokussierte Episode** kennzeichnet die ausgewählte berichtete Episode. Es umspannt deren beibehaltene Joint Spots, wird an beiden Enden um eine halbe Breite der nativen Evidenzeinheit erweitert und am Fokusfenster abgeschnitten, damit ein Impuls aus einem Joint Spot sichtbar bleibt. Das Band ist weder ein Konfidenzintervall noch eine Messung der Dauer eines physischen Ereignisses.

Die Overlays zeigen das erwartete lokale ΔSNR, die Baselines davor und danach über ihre tatsächlichen Stützintervalle, symmetrische robuste-z-Hilfslinien bei 1, 2 und 3 sowie an der konfigurierten Qualifikationsschwelle und die konfigurierte Grenze der absoluten Abweichung. Alle diese Hilfslinien gehören **ausschließlich zur fokussierten Episode**: Andere mit Stern markierte Joint Spots können gegen andere Baselines und robuste Streuungen geprüft worden sein. Die Linien sind Detektorhilfen und keine Konfidenzintervalle; das Überschreiten einer einzelnen Linie kann keinen Kandidaten allein qualifizieren.

**Vor einer Ursachenzuordnung prüfen, was sich geändert hat.** Vergleiche Target-SNR, korrigiertes Referenz-SNR und nahe einseitige Outcomes: Ging die ΔSNR-Bewegung hauptsächlich von einer Seite aus, näherte sich eines der Signale der Decode-Grenze und änderte sich die Paarbarkeit in der Umgebung? Vergleiche den Zeitraum mit zeitgleichen Funkwegen, Stationslogs, Schaltplänen, Änderungen an Verstärkung oder Leistung, beobachteten Störungen und unabhängigen Messungen. Die angezeigte Spanne vom ersten bis zum letzten Joint Spot umfasst beibehaltene Joint Spots; sie belegt kein ununterbrochenes Verhalten dazwischen.

<a id="sec-outlier-7"></a>

##### 2.5.4 Selektivität anpassen und Ergebnis sichern

Verwende die drei Einstellungen entsprechend ihrer wörtlichen Bedeutung; die genaue Bedienreferenz steht in [Abschnitt 4.6](#sec-5-6).

| Änderung | Wirkung auf den Bericht |
|---|---|
| **`Minimale absolute ΔSNR-Abweichung (dB)`** erhöhen | Verlangt eine größere Abweichung von der lokalen Baseline. |
| **`Minimaler robuster z-Wert`** erhöhen | Verlangt eine größere Abweichung im Verhältnis zur robusten Streuung in der Umgebung. |
| **`Maximaler Unterschied zwischen Baseline davor/danach (dB)`** verringern | Verlangt eine stabilere zweiseitige Baseline. |

Die jeweils umgekehrte Änderung macht den Bericht weniger selektiv. Für Spot-Impulse, kurze Ausbrüche und anhaltende Auslenkungen gelten dieselben drei Werte; die Dauer senkt keine Schwelle.

Nutze Kandidaten bei explorativer Arbeit, um prüfenswerte Intervalle zu finden, und dokumentiere Schwellenänderungen. Lege für eine bestätigende Untersuchung Schwellen, Benchmark-Design, Korrektur, Funkwegpopulation, Band und UTC-Bereich **vor** Sichtung des Ergebnisses fest und sichere sie. Prüfe anschließend, ob eine vergleichbare Abweichung in einem getrennten, geeignet kontrollierten Lauf erneut auftritt.

Berichte eine **vorübergehende lokale ΔSNR-Abweichung in den beibehaltenen Joint Spots**, mit exaktem Funkweg, Intervall, Vorzeichen, stützenden Joint Spots und Detektoreinstellungen. Der Detektor ist deskriptiv: Er berechnet keinen p-Wert, korrigiert nicht für die Zahl der durchsuchten Funkwege oder Ereignisse und bestimmt keine physische Ursache.

Ist die Ausreißermeldung aktiviert, sichere die Befunde des aktiven Bereichs mit dem Analyseexport. Er ergänzt eine Zusammenfassung der Funkwegereignisse und eine chronologische CSV-Datei der beitragenden Joint Spots, verknüpft über paketinterne Ereignis- und Funkwegereignis-IDs. Die Evidenztabelle wiederholt Funkweg, Richtung und Ereignisklasse des Funkwegs, damit sie eigenständig verständlich bleibt. [Abschnitt 8.4](#sec-8-4) definiert beide Dateien und ihre bedingte Aufnahme.

<a id="sec-3-9"></a>

---

<a id="sec-4"></a>

### 3. Ergebnis absichern und kommunizieren

Ein belastbares WSPRadar-Ergebnis verbindet einen klaren Versuch, breite Evidenz und eine Formulierung, die genau zur tatsächlichen Beobachtung passt.

<a id="sec-4-1"></a>

#### 3.1 Breite, Konsistenz und Wiederholbarkeit beurteilen

Beurteile das Ergebnis anhand des vollständigen Evidenzbildes:

* Identitäten der beteiligten Stationen;
* Anzahl bestätigter Gelegenheiten bei Performance beziehungsweise Joint Spots bei Benchmark;
* Übereinstimmung zwischen Stationen;
* stationsgleichgewichtete und beobachtungsbezogene Zusammenfassungen;
* benachbarte geografische Segmente;
* zeitliche Ansichten;
* Decode Outcomes;
* Qualität von Identitäten und Locator-Angaben;
* Kontrolle und Wiederholung des Versuchs.

Evidenz ist **breiter**, wenn mehrere Identitäten und benachbarte Segmente übereinstimmen. Sie ist **innerhalb des Laufs konsistenter**, wenn stationsgleichgewichtete, beobachtungsbezogene und zeitliche Ansichten ein vereinbares Bild ergeben. Sie ist **besser kontrolliert**, wenn die betrieblichen Anforderungen des gewählten Leitfadens eingehalten und dokumentiert wurden.

**Konsistenz innerhalb eines Laufs und experimentelle Wiederholbarkeit sind verschieden.** Die Übereinstimmung von stationsgleichgewichteten, beobachtungsbezogenen, geografischen und zeitlichen Ansichten beschreibt die Evidenz innerhalb eines Laufs. Eine Wiederholung des Versuchs in einem weiteren geeigneten Zeitfenster prüft, ob das beobachtete Muster unter neuen Betriebs- und Ausbreitungsbedingungen Bestand hat.

Konzentriert sich ein Muster auf eine Station oder einen kurzen Zeitraum, prüfe diesen Beitrag, bevor du eine breite Schlussfolgerung ziehst. Weichen stationsgleichgewichtete und beobachtungsbezogene Zusammenfassungen voneinander ab, prüfe, welche Stationen die meisten Beobachtungen beitragen. Das spricht für eine engere Aussage oder weitere Untersuchung und nicht automatisch gegen den gesamten Lauf. WSPRadar fasst Evidenzbreite, Konsistenz und Versuchskontrolle nicht zu einer einzigen Beweisstufe zusammen; für die Beurteilung bleiben Anzahlen, Verteilungen und einzelne Zeilen verfügbar.

Das beobachtete zeitliche, entfernungs- oder richtungsabhängige Muster der Dekodierrate, des erfolgreichen SNR oder des ΔSNR ist die Evidenz. Eine Erklärung wie Antennenrichtwirkung, veränderter lokaler Störpegel, Ausbreitungsart, Übersteuerung oder ein intermittierendes Bauteil ist eine Interpretation. Formuliere zuerst passend zur Beobachtung und prüfe die Erklärung anschließend durch eine kontrollierte Änderung, einen Kreuztausch, eine unabhängige Messung oder Wiederholung.

<a id="sec-4-2"></a>

#### 3.2 Ergebnis durch Wiederholung und Kontrolle absichern

Nutze einen ersten explorativen Lauf, um ein mögliches Muster zu erkennen. Lege vor einer bestätigenden Wiederholung Richtung, Band, Benchmark, Filter, Evidenzschwellen, Zeitplan und den primären geografischen oder zeitlichen Auswertungsbereich einschließlich `Maximale Peer-Entfernung vom Target (km)` gemäß [Abschnitt 4.4](#sec-5-4) fest. Führe alternative Maximalentfernungen als getrennt bewahrte Sensitivitätsanalysen aus, statt nach Betrachtung des Ergebnisses nur den günstigsten Bereich auszuwählen.

Wenn das Ergebnis eine wichtige Stationsentscheidung stützen soll:

* dehne das Beobachtungsfenster über die Ausbreitungszustände aus, die in der Schlussfolgerung genannt werden;
* bevorzuge für Aussagen über vollständige Tageszyklen mehrtägige Evidenz;
* wiederhole den Versuch an einem anderen Tag oder während einer anderen Ausbreitungsphase;
* halte nicht untersuchte Variablen zwischen den Wiederholungen stabil;
* vergleiche Läufe mit derselben Richtung, demselben Band, Benchmark, denselben Filtern und Evidenzschwellen;
* untersuche jede Identität, jeden Locator oder kurzen Zeitraum, der einen großen Anteil der Evidenz liefert;
* bewahre Aufbaunotizen auf, damit ein späterer Lauf die Stationskonfiguration reproduzieren kann.

Kleine beobachtete Unterschiede werden nützlicher, wenn sie über Stationen, Zeiträume, benachbarte Segmente und kontrollierte Wiederholungen erneut auftreten.

TX und RX verwenden unterschiedliche Peer-Populationen und Gelegenheitsdefinitionen. Gleiche bei einer Prüfung der Stationsbalance oder eines „Alligator“-Musters Band, Zeitraum, geografischen Bereich und physischen Aufbau soweit praktisch möglich an und untersuche beide Richtungen getrennt. Gleiche Prozentsätze bedeuten keine gleiche Sende- und Empfangsfähigkeit; ein Unterschied der Prozentsätze allein erklärt seine Ursache nicht.

<a id="sec-4-3"></a>

#### 3.3 Evidenzgerechte Schlussfolgerung formulieren

Eine minimale betriebliche Aussage nennt das Target und bei Benchmark gegebenenfalls die feste Referenz oder die lokale Benchmark-Definition. Außerdem nennt sie TX- oder RX-Richtung, Band, UTC-Zeitfenster, geografischen Bereich, Ergebnistyp, angezeigten Wert und die stützende Stations- beziehungsweise Evidenzanzahl.

Verwende für einen technischen Bericht die vollständige Checkliste in [Abschnitt 8.3](#sec-8-3): Bewahre Gewichtung und Evidenzanzahlen, Benchmark-Decode-Outcomes, Versuchsbedingungen und Korrektur, Filter und Schwellen sowie Angaben zu Wiederholung und Sensitivitätsanalysen auf.

**Formulierung für Performance**

> Berichte für dieses Target, Band, UTC-Zeitfenster und die ausgewählte Peer-Population die angezeigte Dekodierrate und nenne ihre Gewichtung. Die stationsgleichgewichtete Dekodierrate ist der Mittelwert der individuellen Raten der qualifizierenden Stationen; die Dekodierrate auf Gelegenheitsebene ist der Erfolgsanteil über alle ihre bestätigten Gelegenheiten. Bei RX bedeutet Erfolg, dass das Target den entfernten Sender decodiert hat; bei TX hat ein entfernter Empfänger das Target decodiert. Nenne die Anzahl qualifizierender Stationen und bestätigter Gelegenheiten, den geografischen Bereich und das relevante zeitliche Muster.

Eine vollständige Performance-Aussage kann zusätzlich nennen, ob die Mindestens-einmal-Reichweite breit oder begrenzt war, ob die Beteiligung beständig oder intermittierend war, wo Entfernungs- oder Richtungsmuster auftraten, ob sich ein UTC-Stunden-Muster wiederholte und wie sich das in RX und TX anhand der gemeldeten Sendeleistung normierte erfolgreiche Target-SNR verhielt. Beschreibe dies als beobachtetes WSPR-Verhalten der vollständigen Station unter den ausgewählten Bedingungen und nicht als isolierten Gewinn, Empfindlichkeit oder Wirkungsgrad.

**Formulierung für Benchmark**

> Für dieses Target, diese Referenz, dieses Band, dieses UTC-Zeitfenster und das ausgewählte Segment sprach das stationsgleichgewichtete mediane ΔSNR innerhalb der Joint Spots um den angezeigten Betrag für Target/Referenz. Berichte dazu das ΔSNR auf Beobachtungsebene, Joint-Stations- und Joint-Spot-Anzahlen, Joint-Evidenzanteil und Decode Outcomes, damit gemeinsame und einseitige Evidenz sichtbar bleiben.

Nenne bei einem Ergebnis eines kontrollierten Aufbaus die vollständigen verglichenen Pfade und jeden Kreuztausch oder jede Kalibrierung. Stelle bei einem Vergleich mit einer unabhängigen Referenzstation klar, dass vollständig aufgebaute Stationen und ihre Umgebungen gebenchmarkt wurden. Nenne bei einer Referenznachbarschaft den Radius und die wechselnde Referenzdefinition des lokalen Nachbarschafts-Medians.

Verwende den Designnamen passend zur beschriebenen Größe:

* Ein **Vergleich im kontrollierten Aufbau** vergleicht die dokumentierten lokalen Pfade.
* Ein **Vergleich mit einer unabhängigen Station** vergleicht vollständig aufgebaute Stationen und ihre Umgebungen.
* **Referenznachbarschaft (Lokaler Median)** vergleicht die vollständige Target-Station mit dem Median der beitragenden Peers in der Umgebung innerhalb des ausgewählten Radius unter den beobachteten Bedingungen.
* Ein richtungsabhängiges Ergebnis beschreibt die beobachteten WSPR-Funkwege und beteiligten Stationen, nicht ein absolutes Strahlungsdiagramm.
* Benchmark-Karten verwenden eine laufabhängige symmetrische dB-Farbskala: Blau spricht für die Referenz, Rot für das Target und `0 dB` bedeutet Gleichheit. Vergleiche Karten verschiedener Läufe anhand der numerischen Farbskalenwerte.

Verwende Formulierungen wie „beobachteter Unterschied“, „in der ausgewählten Evidenz begünstigt“, „bedingte Reichweite“ und „Vergleich vollständig aufgebauter Stationen“. Aussagen über isolierten Antennengewinn, Wirkungsgrad, Empfängerempfindlichkeit, Kausalität oder statistische Signifikanz sind Versuchen vorbehalten, die diese Größen tatsächlich messen oder prüfen.

Die vollständige Referenz für gestützte und nicht gestützte Formulierungen steht in [Kapitel 8](#sec-8).

<a id="sec-4-4"></a>

#### 3.4 Lauf und Kontext sichern

Wähle den geografischen Bereich und die Stationsevidenz, die deine Schlussfolgerung stützen. Wähle dann `Alle Ergebnisse zum Download vorbereiten` und anschließend `Vorbereitete Ergebnisse herunterladen`. Die ZIP-Datei enthält Konfiguration und Metadaten des abgeschlossenen Laufs, verarbeitete Evidenz, zutreffende Tabellen und hochauflösende Abbildungen. Die Vorbereitung allein speichert das Paket noch nicht auf deinem Computer. Eine gespeicherte Konfiguration oder ein geteilter Analyselink bewahrt Einstellungen, nicht die ursprüngliche Evidenz.

Bewahre knappe Stationsnotizen mit der ZIP-Datei auf: Antennen- und Speiseleitungsaufbau, Umschalter-/Splittertopologie, Hardware und Software, gemessene/gemeldete Leistung, Zeitplan und Pfadzuordnung, Kalibrierung, Wetter, Störungen und beabsichtigte Änderungen. Die vollständige Checkliste steht in [Abschnitt 8.3](#sec-8-3).

WSPRadar kann die konfigurierte Analyse und die verarbeitete Evidenz sichern, aber nicht jedes physische Detail der Station erschließen. Das Exportpaket zusammen mit knappen Stationsnotizen macht Vergleich und Reproduktion deutlich belastbarer. [Kapitel 8](#sec-8) dokumentiert den genauen Exportinhalt und die verbleibenden Grenzen der Reproduzierbarkeit.

<div style="page-break-before: always;"></div>

<a id="part-ii"></a>

## Teil II: Bedienelemente und Fehlersuche

Nutze diesen Teil als Nachschlagewerk beim Einrichten, Wiederholen oder Diagnostizieren einer Analyse. Er dokumentiert die exakten Bedienelemente, Standardwerte, gespeicherten Einstellungen und wissenschaftlichen Auswirkungen, die für den Funkbetrieb relevant sind.

Die optionale fachkundige Nutzung der ΔSNR-Ausreißererkennung für Benchmark wird in [Abschnitt 2.5](#sec-outlier) eingeführt. [Abschnitt 4.6](#sec-5-6) enthält ihre Bedienelemente; die wissenschaftliche Übersicht steht in [Abschnitt 7.6](#sec-7-outliers).

<a id="sec-5"></a>

### 4. Bedienelemente und Konfiguration

WSPRadar unterscheidet Bedienelemente, welche die beibehaltene wissenschaftliche Evidenz verändern, von solchen, die nur die Inspektion bereits abgeschlossener Evidenz beeinflussen.

| Klasse | Wirkung | Gespeichert? | Neuer Lauf erforderlich? |
|---|---|---|---|
| **Wissenschaftliche Bedienelemente** | Verändern Identität, Band, Zeit, Referenzdesign, Zulässigkeit, Normierung, Filter, Schwellen oder geografische Population. | Soweit anwendbar | Ja; das vorherige Ergebnis wird verworfen |
| **Ansichtsbedienelemente** | Verändern den aktiven Inspektionsbereich, die ausgewählte Station, die Sichtbarkeit von Evidenz oder die Darstellungsaggregation, ohne beibehaltene Evidenz neu zu klassifizieren. | Nur ausdrücklich unterstützte dauerhafte Einstellungen | Nein |
| **Temporäre Ansichtsoptionen** | Verändern nur die aktuelle Bildschirmdarstellung, temporäre Tabellenfilter, die Sichtbarkeit der Dokumentation oder einen vorbereiteten Download. | Nein | Nein |

Versionierte Konfigurationen speichern die zutreffenden wissenschaftlichen Einstellungen und die unterstützten dauerhaften Ansichtsoptionen. Die exakten Berechnungen stehen in [Kapitel 7](#sec-7); [Abschnitt 8.4](#sec-8-4) erklärt, wie der Export Einstellungen und Evidenz bewahrt. Für den vollständigen Feldvertrag gespeicherter Konfigurationen ist das formale JSON-Schema maßgeblich.

<a id="sec-5-1"></a>

#### 4.1 Ablaufsteuerung

| Bedienelement | Funktion | Wichtiges Verhalten |
|---|---|---|
| **`EN` / `DE`** | Ändert die Anzeigesprache. | Ein abgeschlossenes Ergebnis wird aus seiner aufbewahrten Evidenz ohne erneute Analyse neu dargestellt. Ohne abgeschlossenes Ergebnis startet ein Sprachwechsel die Analyse nicht automatisch neu; starte sie ausdrücklich erneut. Fehlende oder abgelaufene Evidenz erfordert ebenfalls einen ausdrücklich neu gestarteten Lauf. |
| **`Eingabeansicht`** | Wechselt zwischen `Geführt` und `Klassisch`. | Beide Ansichten bearbeiten dieselbe wissenschaftliche Konfiguration. Die gewählte Eingabeansicht wird nicht gespeichert. |
| **`Demo laden`** | Lädt ein gepflegtes historisches Profil. | Das Laden startet keine Analyse. Änderungen an Filtern, Evidenzschwellen und Ergebnisansicht behalten den Demo-Kontext; eine Änderung der Versuchsdefinition löst die Konfiguration von der Demo. |
| **`Konfig laden`** | Lädt eine versionierte JSON-`.config`. | Ungültige Identitäten, Datumswerte, Auswahlwerte, Wertebereiche, doppelte Felder und nicht unterstützte Schemaversionen werden abgelehnt und nicht erraten. |
| **`Konfig speichern`** | Speichert in der geführten und klassischen Eingabe die zutreffenden wissenschaftlichen Eingaben und unterstützten dauerhaften Ansichtseinstellungen aus dem abschließenden Prüfbereich. | Die Datei enthält absolute UTC-Grenzen, aber keine Ergebniszeilen, externen Versuchsnotizen oder flüchtigen Tabellenfilter. Das Speichern bleibt unverfügbar, bis die Frage und bei einem Benchmark zusätzlich das Benchmark-Design vollständig sind. |
| **`RX-Analyse starten` / `TX-Analyse starten`** | Führt in der geführten und klassischen Eingabe das ausgewählte Performance- oder Benchmark-Ergebnis aus dem abschließenden Prüfbereich aus. | In der geführten Eingabe erscheint die Startaktion erst, wenn die zutreffenden Einrichtungsschritte gültig sind und der abschließende Prüfbereich verfügbar ist. In der klassischen Eingabe bleibt Starten verfügbar, um unvollständige oder ungültige Felder mit direkter Korrekturhilfe anzuzeigen. In beiden Ansichten beginnt die Analyse erst nach Klärung aller erforderlichen Eingaben und einer gegebenenfalls nötigen Referenzstandortwahl. Eine Änderung eines wissenschaftlichen Bedienelements nach dem Lauf verwirft das Ergebnis und verlangt einen neuen Lauf. |
| **`Alle Ergebnisse zum Download vorbereiten`** | Erstellt das aktuelle Exportpaket. | Verwendet die abgeschlossene Evidenz und die aktuellen Inspektor-Auswahlen. |
| **`Vollständige Dokumentation laden` / `Vollständige Dokumentation ausblenden`** | Zeigt oder verbirgt das vollständige Webhandbuch. | Reiner Darstellungszustand. |
| **`PDF vorbereiten`** | Erstellt das Handbuch in der gewählten Sprache als PDF. | Das vollständige Webhandbuch muss dazu nicht zuerst geöffnet werden. |

In der geführten Eingabe prüft `Weiter` den aktuellen Einrichtungsbereich und öffnet den nächsten, sobald seine erforderlichen Eingaben gültig sind. Die Korrektur eines Feldes entfernt dessen Fehlermeldung; sind alle Fehler in diesem Bereich korrigiert, verschwindet auch seine zusammenfassende Fehlermeldung. Ein früherer erfolgloser Versuch löst keine Fehleranzeigen in späteren, noch nicht geprüften Bereichen aus. Die abschließende Startaktion prüft vor Beginn der Analyse nochmals die vollständige Konfiguration.

**Tastaturbedienung.** In der geführten und klassischen Eingabe wechselst du mit `Tab` vorwärts durch die nativen Eingabefelder und Aktionen, mit `Umschalt+Tab` rückwärts. Die separaten `?`-Hilfesymbole sind ausschließlich mit der Maus bedienbar und werden niemals zum Tab-Stopp; der Fokus auf einem Eingabefeld öffnet keine überlagernde Hilfe. In der geführten Eingabe übernimmt ein vorwärts gerichtetes `Tab` am Ende des aktiven Einrichtungsbereichs die aktuelle Eingabe und prüft diesen Bereich wie `Weiter`. Sind die Eingaben gültig, öffnet sich der nächste Bereich und sein erstes Eingabefeld erhält den Fokus; andernfalls bleibt der aktuelle Bereich offen und sein erstes ungültiges Feld erhält den Fokus. Das native Tastaturverhalten innerhalb der Bedienelemente und die Rückwärtsnavigation mit `Umschalt+Tab` bleiben unverändert. Nach abgeschlossener Einrichtung erhält die Überschrift des Prüfbereichs den Fokus, mit dem nächsten `Tab` dann die Startaktion; dieser Tastaturwechsel startet keine Analyse automatisch. Meldet `Weiter` oder die Startaktion ungültige Eingaben, erhält das erste ungültige Feld den Fokus, damit du es direkt korrigieren kannst.

Beide Eingabeansichten enden mit derselben abschließenden Konfigurationsübersicht. Im Zustand **`Prüfung — startbereit ✓`** liegen `RX-Analyse starten` / `TX-Analyse starten` und `Konfig speichern` erst nach gültiger Konfiguration innerhalb dieses Bereichs. Der Prüfbereich bleibt beim Start des Laufs und nach seinem Abschluss geöffnet; auch der Laufstatus bleibt bei **`Complete`** geöffnet. In der klassischen Eingabe wird beim Start einer gewöhnlichen Analyse oder einer Demo kein Konfigurationsbereich automatisch geschlossen; einzelne Bereiche lassen sich weiterhin manuell schließen und wieder öffnen. Die geführte Eingabe darf frühere abgeschlossene Schritte weiterhin kompakt darstellen, ihr abschließender Prüfbereich bleibt jedoch geöffnet.

Nach dem Laden einer Demo in der geführten Eingabe öffnet `Einstellungen Schritt für Schritt durchgehen` die Einrichtungsschritte zur Prüfung. `Direkt zu Prüfen und starten` öffnet den abschließenden Prüfbereich und startet die Analyse sofort mit den aktuellen gültigen Einstellungen; ein zweiter Klick auf `RX-Analyse starten` / `TX-Analyse starten` ist nicht erforderlich. Die Abkürzung bleibt unverfügbar, solange erforderliche Einstellungen unvollständig sind oder bereits eine Analyse läuft. Das Laden der Demo selbst startet weiterhin keine Analyse.

Nach dem angenommenen Start einer Analyse springt die Seite zum Laufstatus unterhalb der Prüfung. Sobald das erste Kartenbild bereitsteht, springt sie zu diesem Ergebnis, während Segment-Inspektor und Drill-Down-Daten automatisch weiter vorbereitet werden. Der Status erreicht **`Complete`** erst, wenn alle Ergebnisansichten bereitstehen. Jeder automatische Sprung erfolgt einmal pro Startauftrag; wer während der Wartezeit selbst scrollt oder an eine andere Stelle navigiert, verhindert den Sprung zur Karte. Interaktionen mit den Ergebnisansichten und die erneute Anzeige eines abgeschlossenen Laufs lösen diese automatischen Sprünge nicht erneut aus.

**Aktuelles Konfigurationsformat.** Akzeptiert werden ausschließlich das aktuelle Schema gespeicherter Konfigurationen und der aktuelle öffentliche URL-Vertrag; aufgegebene Aliasnamen, Felder und frühere Eingabeformate werden ohne Migration abgelehnt. Gespeicherte Dateien bewahren die Eingaben und dauerhaften Ansichtsoptionen, die für die ausgewählte Analyse gelten. Ungültige oder nicht unterstützte Dateien werden abgelehnt, statt stillschweigend neu interpretiert zu werden. Das formale JSON-Schema (`config/wspradar-config.schema.json`) ist der maßgebliche vollständige Vertrag gespeicherter Konfigurationen; [Abschnitt 8.4](#sec-8-4) beschreibt die exportierten Konfigurations- und Evidenzdateien. Das Laden oder Speichern einer Konfiguration erzeugt kein zusätzliches Ergebnis; ausgeführt wird nur die ausgewählte Performance- oder Benchmark-Analyse.

**Lebenszyklus des Demo-Kontexts.** Eine geladene Demo behält ihren sichtbaren Kontext, wenn nur Populationsfilter, Evidenzschwellen, Inspektor-Bereich oder andere Bedienelemente der Ergebnisansicht geändert werden. Eine angepasste Ansicht lässt sich dadurch weiterhin vor dem Hintergrund des ursprünglichen Beispiels deuten. Änderungen an Frage oder Richtung, Target-Rufzeichen oder -QTH, Band, Messzeitraum, Benchmark-Design oder -Identität, Nachbarschaftsradius sowie Absicht oder Wert der Korrektur entfernen Demo-Metadaten und Profilidentität aus später gespeicherten Konfigurationen, weil der Aufbau nicht mehr dem dokumentierten Versuch entspricht. Jede wissenschaftliche Änderung beendet außerdem die exakte Demo-Cache-Identität, auch wenn der erklärende Demo-Kontext sichtbar bleibt. Eine wissenschaftliche Änderung der Population oder Evidenz löscht jede vorausgewählte Performance- und Benchmark-Identität in Station Insights, da der Funkweg im neuen Ergebnis fehlen kann. Reine Bedienelemente der Ergebnisansicht löschen diese Auswahl nicht.

**Wiederverwendung von Demo-Daten.** Beim Ausführen einer unveränderten Demo werden fehlende Datenbank-Abfrageergebnisse abgerufen und validierte Zeilen auf dem Datenträger des App-Servers gespeichert. Spätere Läufe verwenden passende Einträge ohne automatischen Ablauf erneut, auch über Sitzungen und App-Neustarts hinweg, solange dieser Datenträger erhalten bleibt. Eine geänderte Abfrage, ein inkompatibles Cache-Format oder fehlende beziehungsweise beschädigte Dateien erfordern einen erneuten Abruf. Weder beim App-Start noch beim Laden einer Demo werden deren Daten vorab abgerufen. Die Wiederverwendung bewahrt die abgerufenen Daten, statt spätere Datenbankkorrekturen automatisch zu übernehmen; jeder Lauf führt die Analyse weiterhin mit dem aktuellen Anwendungscode aus.

<a id="sec-5-2"></a>

#### 4.2 Frage, Target und Messzeitraum

Die Klassische Eingabe ordnet die wissenschaftliche Konfiguration nach der Fragestellung. Im ersten Bereich **`Frage`** muss eine von vier vollständigen Analysen gewählt werden: `RX Performance`, `TX Performance`, `RX-Benchmark` oder `TX-Benchmark`. Diese eine Auswahl legt sowohl die RX-/TX-Richtung als auch fest, ob der Lauf eigenständige Performance-Evidenz oder einen Target–Referenz-Benchmark erzeugt. Der zweite Bereich **`Target und Messzeitraum`** erfasst anschließend wie bisher Target-Identität, QTH, Band und absoluten UTC-Zeitraum. Bei einem Benchmark folgt **`Benchmark-Design`**. Beide Ergebnistypen zeigen danach **`Optionale Filter, Analyseumfang und Evidenz`** und abschließend den Prüfbereich; Performance besitzt damit vier und Benchmark fünf klassische Bereiche.

| UI-Bezeichnung | Standard | Funktion |
|---|---|---|
| **Frage** | keine; erforderlich | Eine Auswahl aus `RX Performance`, `TX Performance`, `RX-Benchmark` oder `TX-Benchmark`; legt Richtung und Ergebnistyp gemeinsam fest. |
| **Target-Rufzeichen (Empfänger im Test)** / **Target-Rufzeichen (Sender im Test)** | leer | Exakte Meldeidentität in der Datenbank. Standardrufzeichen, gültige Varianten mit `/`, reine Buchstabenkennungen und ein optionales abschließendes alphanumerisches Bindestrich-Suffix sind zulässig. |
| **Target-QTH (4 oder 6 Zeichen)** | leer | Target-Zuordnung über Grid-4, Kartenmittelpunkt, Geometrie und Ursprung des lokalen Radius. |
| **Frequenzband** | `20m` | Genau eines aus `LF`, `MF`, `160m`, `80m`, `60m`, `40m`, `30m`, `22m`, `20m`, `17m`, `15m`, `12m`, `10m`, `8m`, `6m`, `4m`, `2m`, `70cm` oder `23cm`. |
| **UTC-Messzeitraum** | festes 24-Stunden-Fenster bis zur aktuellen UTC-Minute | Das absolute Evidenzintervall des Laufs. |
| **Startdatum/-zeit (UTC)** und **Enddatum/-zeit (UTC)** | das wirksame Standardfenster | Datumswerte beginnen im Jahr 2008; ein Lauf ist auf 31 verstrichene Tage begrenzt. Eingegebene Zeiten bleiben mit Minutengenauigkeit erhalten, ohne Rundung auf 15-Minuten-Grenzen. |

Verwende das Rufzeichen oder die Meldekennung exakt so, wie es beziehungsweise sie hochgeladen wurde. Nur als schematische Platzhalter stehen `CALL`, `CALL/1`, `CALL/2`, `CALL/P`, `CALL/QRP` und `CALL-1` für verschiedene exakte Datenbankidentitäten. WSPRadar führt sie weder anhand des Basisrufzeichens zusammen noch wendet es eine verdeckte Präfix- oder Suffixzuordnung an. Die Beispiele zeigen lediglich die Zuordnungssyntax; sie begründen weder die Zuteilung noch die Berechtigung, eine dieser Identitäten zu senden. Verwende nur ein vollständiges Rufzeichen, das für den Bediener und die Betriebsumstände zulässig ist.

Ein vierstelliger Maidenhead-Locator bezeichnet ein größeres Locator-Feld, sechs Zeichen ein kleineres Unterfeld darin. WSPRadar verwendet das konfigurierte QTH als Kartenmittelpunkt und Ursprung des lokalen Radius. Performance und Benchmark wählen Target-Zeilen in der Datenbank anhand des exakten Rufzeichens plus der ersten vier Zeichen des Target-QTHs. Das vollständige QTH verankert weiterhin Karte, Entfernung, Azimut, Sonnenstand und lokale Nachbarschaftsgeometrie.

<a id="sec-5-3"></a>

#### 4.3 Benchmark-Design und -Einstellungen

Für `RX-Benchmark` und `TX-Benchmark` zeigt die Klassische Eingabe einen dritten Bereich namens **`Benchmark-Design`** mit folgenden Optionen:

- `Referenzaufbau/-station`
- `Referenznachbarschaft`

Die geführte Eingabe bietet zu jeder Referenzoption eine kurze Hilfe und getrennte Hilfen zu den Feldern für Referenz-Rufzeichen und Nachbarschaftsradius. Diese erklären, was einzugeben ist und was das jeweilige Feld steuert. In der klassischen Eingabe erklärt die Hilfe neben **Benchmark-Design** beide Referenzoptionen unabhängig von der aktuellen Auswahl. Die Felder für Referenz-Rufzeichen und Nachbarschaftsradius haben eigene Hilfen zur Eingabe. Die Referenznachbarschaft verwendet den in der Auswahlhilfe beschriebenen lokalen Median; den geografischen Umfang legst du mit dem Nachbarschaftsradius fest.

Wird RX- oder TX-Benchmark ohne bestehendes Design gewählt, ist in der geführten und klassischen Eingabe **Referenzaufbau/-station** vorausgewählt. Eine bestehende Auswahl von Referenzaufbau/-station oder Referenznachbarschaft bleibt erhalten.

Bei `RX Performance` und `TX Performance` entfällt der Bereich **`Benchmark-Design`** vollständig, weil Performance keine Referenz verwendet. Der abschließende Prüfbereich erscheint nach dem gemeinsamen Bereich **`Optionale Filter, Analyseumfang und Evidenz`**. Beim Start werden ungültige oder unvollständige Felder direkt mit roter Rückmeldung und konkreter Korrekturhilfe markiert; die Korrektur eines Feldes entfernt dessen Hinweis. Fehler beim Datenbankzugriff werden von einem ungültigen Rufzeichen oder einem leeren Meldezeitfenster getrennt ausgewiesen. Performance und Benchmark sind sich gegenseitig ausschließende Ergebnistypen: Ein Lauf erzeugt nur das ausgewählte Ergebnis. [Abschnitt 8.4](#sec-8-4) beschreibt die im Export enthaltenen Einstellungen, Evidenz und Abbildungen.

| UI-Bezeichnung | Standard / Wertebereich | Gilt für | Wissenschaftliche Wirkung |
|---|---|---|---|
| **Gibt es einen ermittelten Target–Referenz-<br>Offset?** | `Kein ermittelter Offset — 0,0 dB verwenden` | Geführtes Referenzaufbau/<br>-station | Unterscheidet keinen ermittelten Offset, die Verwendung einer ermittelten Korrektur und einen gezielten Offset-Ermittlungslauf. |
| **Referenzseitige SNR-Korrektur (dB)** | leer = `0.0`; `-99.9` bis `+99.9 dB` | Benchmark | Wird zum Referenz-SNR addiert, bevor ΔSNR Target minus Referenz berechnet wird. Dezimalwerte werden mit Punkt eingegeben, beispielsweise `1.2`. |
| **Referenz-<br>Rufzeichen** | leer | Referenzaufbau/<br>-station | Exakte Meldeidentität der Referenz. |
| **Referenzstandort** | aus der ausgewählten Datenbank ermittelt | Referenzaufbau/<br>-station | Ein beobachtetes Grid-4 wird automatisch aufgelöst; bei mehreren gemeldeten Grid-4 ist eine ausdrückliche Auswahl nötig. Ein zusätzlicher manueller Referenz-Locator ist nicht erforderlich. |
| **Nachbarschafts-<br>radius (km)** | `100`; 10–250 km in 10-km-Schritten | Referenz-<br>nachbarschaft | Definiert den lokalen Referenzpool um das Target-QTH. |


Beim Wechsel der Frage oder des Benchmark-Designs werden nicht zutreffende Bedienelemente ausgeblendet. Gespeicherte Konfigurationen enthalten nur die Eingaben, die für die ausgewählte Analyse gelten. Werte, deren wissenschaftliche Bedeutung sich im neuen Design ändern würde, werden gelöscht statt umgedeutet.

Gib nur das exakte Referenzrufzeichen ein. Das Target-QTH bleibt der einzige manuell eingegebene Analyse-Locator und der Ursprung für Karte, Entfernung, Azimut, Sonnenstand und Nachbarschaftsgeometrie. Die Referenzstandortsuche gilt für die ausgewählte Rolle, das Band, das effektive UTC-Zeitfenster und die Datenbank. Ein beobachtetes Grid-4 wird automatisch aufgelöst; bei mehreren Kandidaten ist deine Auswahl erforderlich. Angezeigt werden die vollständigen Locatorvarianten, Meldungszahlen sowie erste und letzte Meldezeit. Eine erfolgreiche Suche ohne passende Meldungen ist von einem Datenquellenfehler getrennt. Dieselbe Datenbank liefert die anschließende Analyse; das aufgelöste Grid-4 bleibt in der gespeicherten Analysedefinition erhalten.

Beim TX-Benchmark mit Referenzaufbau/-station erscheint ein Hinweis zur Prüfung der Nachrichtenfolgen, wenn ein Rufzeichen einen Schrägstrich enthält und das andere nicht. Der Hinweis verhindert den Start nicht und gilt auch bei unterschiedlichen Basisrufzeichen. Die Eingabeprüfung kann weder Firmwareeinstellungen noch Sendezeitpläne überprüfen; beachte die Hinweise zum kontrollierten TX-Aufbau in [Abschnitt 2.2.1](#sec-3-tx-benchmark-simultaneous). Für RX-Meldekennungen, Performance und Referenznachbarschaft gilt dieser Hinweis nicht.

Ein Grid-4 beweist keinen einzelnen physischen Standort. Unterschiedliche Feinlocator darin bleiben als gemeldete Varianten sichtbar; eine Kombination aus grobem und feinem Locator kann geografisch vereinbar sein, ohne einen einzigen Sender oder Empfänger zu beweisen. Die Suche führt die entfernten Peer-Identitäten für die Paarbildung nicht zusammen.

Unterschiedliche gemeldete Felder können getrennte Standorte oder falsche Datenbankmetadaten bedeuten; die gemeldeten Locator beweisen keine der beiden Erklärungen. Passen keine geeigneten Target-Meldungen zum eingegebenen Target-QTH, prüfe die Eingaben; der Analyseursprung wird niemals automatisch geändert.

##### Vorzeichen der referenzseitigen SNR-Korrektur

Eine positive Korrektur erhöht das korrigierte Referenz-SNR und verringert dadurch ΔSNR Target minus Referenz. Gib einen gemessenen Kalibrierversatz `target - reference` mit demselben Vorzeichen ein. Ergibt eine Kalibrierung mit gemeinsamem Eingang beispielsweise `+1.6 dB`, wird `+1.6 dB` eingetragen. [Abschnitt 7.2.2](#sec-7-benchmark-delta) definiert die Gleichungen.

Die Korrektur gilt für den ausgewählten Referenz-Empfangs- beziehungsweise Sendepfad oder jeden lokalen Beitrag vor Bildung des lokalen Nachbarschafts-Medians.

| Geführte Auswahl | Bedeutung | Erforderlicher Wert |
|---|---|---|
| **Kein ermittelter Offset** | Es wurde keine belastbare Korrektur bestimmt. | `0.0 dB` |
| **Ermittelte Korrektur verwenden** | Ein dokumentierter, vorzeichenbehafteter additiver Offset gilt für diesen Aufbau. | Ermittelte Korrektur eingeben |
| **Offset-Ermittlungslauf einrichten** | Evidenz sammeln, aus der ein Offset abgeleitet werden kann; WSPRadar berechnet oder verwendet diesen Offset nicht automatisch. | Während des Ermittlungslaufs `0.0 dB` |

Eine konstante Korrektur kann Übersteuerung, instabile AGC, intermittierende Signalführung, frequenzabhängigen Amplitudengang oder falsche Leistungsangaben nicht beheben. Kalibrierung eines kontrollierten Aufbaus sollte ein gemeinsames Eingangssignal oder eine kalibrierte Bezugsebene verwenden. Eine geografisch getrennte Referenzstation kann nur eine wiederholbare Basislinie für genau dieses Paar, Band und diesen Aufbau stützen – keine absolute Kalibrierung. [Anhang C](#sec-reference-snr-calibration) beschreibt das praktische Verfahren.

Verwende beim lokalen Nachbarschafts-Median `0.0 dB`, wenn keine unabhängig begründete Korrektur ermittelt wurde. Eine Korrektur ungleich null erfordert eine dokumentierte Begründung, warum derselbe additive Offset unter den ausgewählten Bedingungen für die beitragende Referenzpopulation gilt. Die Korrektur so lange anzupassen, bis die Nachbarschaft zum Target passt, begründet keine Kalibrierung. Ein gemeinsamer Offset kann unterschiedliche unbekannte Fehler einzelner Nachbarstationen nicht korrigieren.

<a id="sec-5-4"></a>

#### 4.4 Filter und Evidenzschwellen

Geführte und klassische Eingabe verwenden für diese Einstellungen denselben Bereichsnamen **`Optionale Filter, Analyseumfang und Evidenz`**. Das Anpassen dieser Einstellungen ist optional; ihre angezeigten Werte gelten weiterhin. Innerhalb dieses Schritts zeigt die geführte Eingabe stets die zutreffenden Felder; eine getrennte vorgeschaltete Auswahl entfällt. Unveränderte Konfigurationen initialisieren die sichtbaren Felder mit den nachstehenden ergebnisspezifischen Standardwerten; geladene Konfigurationen und Demos tragen ihre gespeicherten Werte in dieselben sichtbaren Felder ein. Das bloße Anzeigen dieser Werte bearbeitet sie nicht und löst den Demo-Kontext nicht. Die angezeigten Einstellungen für Filter, Analyseumfang und Evidenz gelten auch dann, wenn du diesen Bereich unverändert lässt.

Wähle Filter und Schwellen vor einem bestätigenden Lauf aus der beabsichtigten Population und der gewünschten Evidenzuntergrenze. Eine nachträgliche Änderung nach Betrachtung des Ergebnisses erzeugt eine andere Analyse und sollte getrennt aufbewahrt werden.

| Bedienelement | Standard | Gilt für | Wirkung und Verwendung |
|---|---|---|---|
| **Spezial-Rufzeichen Q, 0, 1 ausschließen** | bei Performance ein; bei Benchmark aus | alle Ergebnisse | Schließt entfernte Peer-Rufzeichen aus, die mit `Q`, `0` oder `1` beginnen: sendende Peers in RX-Analysen und empfangende Peers in TX-Analysen. Target- und Referenzstationen einschließlich der Stationen, die zur Referenz der lokalen Nachbarschaft beitragen, bleiben von diesem Filter unberührt. Die Präfixregel stellt nicht fest, ob eine Station Telemetrie überträgt. Behalte baken- oder telemetrieartige Identitäten, wenn sie zur Fragestellung gehören; schließe sie aus, wenn reguläre Amateurfunkaktivität untersucht werden soll. |
| **Bewegliche Stationen filtern** | bei Performance ein; bei Benchmark aus | kartierte Peers | Schließt Rufzeichen aus, die in der ansonsten qualifizierenden globalen Population mehr als ein Grid-4 melden. Nutze Drill-Down, um Bewegung von fehlerhaften Locator-Angaben zu unterscheiden. |
| **Sonnenstand am Target-QTH** | `Ganze 24h` | alle Ergebnisse | Behält je nach Sonnenhöhe am Target-QTH `Tag (Elev > +6°)`, `Nacht (Elev < -6°)`, `Greyline (-6° bis +6°)` oder alle Zyklen bei. |
| **Maximale Peer-Entfernung vom Target (km)** | `22000`; Auswahl `2500`, `5000`, `10000`, `15000`, `20000`, `22000` | alle Ergebnisse | Entfernt Peers ab der ausgewählten Entfernung aus Analyse, verarbeiteten Artefakten und Exporten. Das Target-Active Gate darf Evidenz außerhalb des Bereichs weiterhin ausschließlich dazu verwenden, Target-Betrieb nachzuweisen. |
| **Minimale Joint-Evidenz pro Station** | `1`; Bereich 1–50 | simultaner Benchmark | Verlangt mindestens die gewählte Anzahl von Joint Spots, bevor eine exakte Stationsidentität ihr medianes ΔSNR beiträgt. Derselbe Zahlenwert gilt getrennt als Untergrenze für Only Target und Only Reference; einseitige Beobachtungen erfüllen die Joint-Anforderung nicht. |
| **Minimale bestätigte Gelegenheiten pro Station** | `5`; Bereich 1–100 | Performance | Verlangt mindestens die gewählte Anzahl bestätigter Gelegenheiten je exakter Peer-Identität: erfolgreiche Target-Decodes oder bestätigte Gelegenheiten ohne Target-Decode (Misses). Niedrige Werte erhöhen die Abdeckung, machen die Raten aber grob und schwach gestützt. |
| **Minimale qualifizierte Stationen pro Kartensegment** | `1`; Bereich 1–10 | alle Karten | Verlangt breitere Identitätsunterstützung, bevor ein Segment gezeichnet wird. |

Die beiden Ausschluss-Standardwerte gelten nur für unveränderte interaktive Konfigurationen. Eine Performance-Konfiguration startet mit beiden Ausschlüssen; eine Benchmark-Konfiguration ohne beide. Sobald der Bediener einen der Ausschlüsse manuell ändert, bleibt dieser ausdrückliche Wert über Wechsel der Frage hinweg erhalten und wird nicht mehr durch einen Ergebnistyp-Standard ersetzt. Geladene Konfigurationen, Demos und Analyse-URLs behalten ihre ausdrücklich gespeicherten Einstellungen ebenfalls bei.

`Maximale Peer-Entfernung vom Target (km)` begrenzt die ausgewertete Population erst, nachdem die Datenbankzeilen abgerufen wurden. Eine Verringerung umgeht deshalb nicht die Zeilengrenze der Datenbank. Ein kleinerer lokaler Nachbarschaftsradius und `Spezial-Rufzeichen Q, 0, 1 ausschließen` können bei bestimmten Analysen die abgerufene Population verkleinern; [Abschnitt 5.6](#sec-6-6) behandelt zu große Abrufe.

<a id="sec-5-5"></a>

#### 4.5 Karten-, Inspektor- und Exporteinstellungen

| Bedienelement | Wirkung | Gespeichert? | Neuer Lauf? |
|---|---|---|---|
| Entfernung und Richtung des Segments | Aktiver geografischer Inspektionsbereich | getrennt für Performance und Benchmark | Nein |
| `Nur von anderen Stationen gehört.` / `Nur andere Signale gehört.` | Sichtbarkeit von Performance-Peers mit ausschließlich Gegen-Evidenz | Ja | Nein |
| `Ungepaarte Evidenz einbeziehen` | Sichtbarkeit von Benchmark-Identitäten, die nur exklusive oder asynchrone Evidenz besitzen | Ja | Nein |
| Ausgewählte Stationszeile | Evidenz der ausgewählten Station und ausgewählte Drill-Down-Identität | exakte Identitäten aus `Rufzeichen + Locator`: normalerweise höchstens eine je Ergebnistyp; mehrere Benchmark-Identitäten bei eingeschalteter Ausreißererkennung | Nein |
| Zeitaggregation des Segments | Chronologische zeitliche Ansicht des Segment-Inspektors; die Auswahl passt sich an die Laufdauer an | Ja | Nein |
| Zeitaggregation der ausgewählten Station | Chronologische Ansicht des ausgewählten Funkwegs; die Auswahl passt sich an die Laufdauer an | Ja | Nein |
| **`Zoom-Zeitfenster`**, **`Datum der Fenstermitte (UTC)`**, **`Uhrzeit der Fenstermitte (UTC)`**, **`← Früher`**, **`Später →`**, **`Ausreißerfokus`** und **`Tabelle filtern`** | Optionale Drill-Down-Abbildungen in nativer Zeitauflösung und zentriertes Tabellenintervall für genau eine ausgewählte Station; die Tabellenfilterung betrifft nur angezeigte Zeilen | Nein | Nein |
| `Alle Ergebnisse zum Download vorbereiten` | Exportpaket und aktuelle Inspektor-Auswahlen | nicht zutreffend | Nein |

Evidenztabellen ohne Zeilenauswahl laden bei mehr als 150.000 angezeigten Zeilen weitere Zeilen beim Scrollen nach. In diesem Modus sind die eingebaute Suche der Browsertabelle und ihr direkter CSV-Download nicht verfügbar. Verwende **`Tabelle filtern`**, um die angezeigten Drill-Down-Zeilen einzugrenzen, und **`Alle Ergebnisse zum Download vorbereiten`**, um das Reproduzierbarkeitspaket zu erhalten. In **Station Insights** bleibt die Zeilenauswahl verfügbar, damit du die Evidenz einer Station öffnen kannst.

Für chronologische Ansichten werden folgende Bins angeboten; der Standard gilt, wenn keine ausdrückliche kompatible Auswahl geladen wurde:

| Vollständige Laufdauer | Angebotene Bins | Standard |
|---|---|---|
| Bis einschließlich 6 Stunden | `2m`, `10m`, `30m`, `1h`, `2h`, `3h`, `6h` | `10m` |
| Mehr als 6 bis einschließlich 24 Stunden | `2m`, `10m`, `30m`, `1h`, `2h`, `3h`, `6h` | `30m` |
| Mehr als 24 Stunden bis einschließlich 7 Tage | `30m`, `1h`, `2h`, `3h`, `6h`, `12h`, `24h` | `12h` |
| Mehr als 7 Tage | `1h`, `2h`, `3h`, `6h`, `12h`, `24h` | `12h` |

Damit steht `2h` bei jeder Laufdauer zur Verfügung. Die chronologische Aggregation verändert weder die Klassifikation von Gelegenheiten noch die Benchmark-Paarbildung oder die festen einstündigen UTC-Profile. Leere Performance-Zeit- oder Entfernungs-Bins bleiben fehlende Evidenz und werden nicht zu künstlichen Beobachtungen mit einer Rate von null.

**Fokusfenster wählen.** Der Drill-Down-Zoom ist flüchtig und nur für genau eine ausgewählte Station verfügbar. Wähle **`Aus`** oder ein vollständiges Intervall von `1h`, `3h`, `6h`, `12h` beziehungsweise `24h`. **`Datum der Fenstermitte (UTC)`** und **`Uhrzeit der Fenstermitte (UTC)`** wählen die Mitte dieses Intervalls; WSPRadar leitet daraus exakten Start und exaktes Ende ab, verschiebt das vollständige Intervall an einer Laufgrenze, statt es zu kürzen, und lässt es mit **`← Früher`** beziehungsweise **`Später →`** um ein vollständiges ausgewähltes Fenster versetzen. Die aufgelösten Grenzen erscheinen in einer Zeile als **`Ausgewähltes Zeitfenster: {start} bis {end} UTC`**. Der Zoom begrenzt die fokussierten Abbildungen und die Drill-Down-Tabelle; **`Tabelle filtern`** verändert anschließend nur die angezeigte Tabelle und niemals die fokussierten Abbildungen oder die abgeschlossene Analyse.

**Einzelbeobachtungen ablesen.** Die Messwertabbildung ist bewusst kein Zwei-Minuten-Aggregat: Der simultane Benchmark zeigt einen tatsächlichen ΔSNR-Punkt je beibehaltenem Joint Spot zu seiner kanonischen Zykluszeit; Performance zeigt das tatsächliche normierte Target-SNR jeder erfolgreichen bestätigten Gelegenheit zu ihrer kanonischen Zykluszeit. Dies sind einzelne beibehaltene wissenschaftliche Evidenzeinheiten nach Zusammenführung, Zuordnung und Filtern durch WSPRadar und keine unveränderten Provider-Zeilen. In der fokussierten Messwertansicht entfallen Binmedian, IQR, Dichtehintergrund, Farbskala, Median des vollständigen Laufs und nach UTC-Stunde gefaltetes Messwertpanel. Die ergänzende Performance-Outcome- beziehungsweise Benchmark-Abdeckungsansicht darf ihre chronologische Aggregation beibehalten; Segmentansicht und Evidenz der ausgewählten Station über das vollständige Fenster bleiben dichtebasierte aggregierte Ansichten.

**Ausreißerfokus öffnen.** Eine Ausreißeraktion lädt den **`Ausreißerfokus`** über die vollständige gestützte Baseline-Flanke vor dem Ereignis, die geschützte vorläufige Episode und die Flanke danach vor; begrenzt wird dieses Intervall nur durch das abgeschlossene Analysefenster, und es darf länger als 24 Stunden sein. Die Kandidatenprovenienz bleibt erhalten, wenn der Bediener zu einem manuellen festen Fenster wechselt.

**Marker und Episodenband einordnen.** In einer fokussierten Benchmark-Abbildung kennzeichnen identische `*`-Marker jeden Joint Spot im aktuellen Fenster, der innerhalb eines gemeldeten Kandidaten einzeln sowohl das konfigurierte Abweichungs- als auch das robuste-z-Kriterium erfüllt; ein dezentes Band **Fokussierte Episode** unterscheidet die ausgewählte berichtete Episode. Das Band umfasst deren berichtetes Intervall der beibehaltenen Evidenz mit einer halben Breite der nativen Evidenzeinheit als Erweiterung an jedem Ende und wird am Fokusfenster abgeschnitten, damit ein Impuls sichtbar bleibt. Es ist ein Auswahlhinweis und kein Konfidenzintervall oder Maß der physischen Dauer.

**Detektorhilfen einordnen.** Erwartetes lokales ΔSNR, zeitlich begrenzte Baselines der Flanken davor und danach, robuste-z-Hilfslinien bei 1, 2 und 3 sowie an der konfigurierten Qualifikationsschwelle und die konfigurierte Grenze der absoluten Abweichung gehören ausschließlich zur fokussierten Episode; andere markierte Kandidaten können andere Baselines und robuste Streuungen besitzen. Robuste-z- und Abweichungslinien sind Detektorhilfen und keine Konfidenzintervalle; das Überschreiten einer einzelnen Linie erfüllt nicht die getrennten Anforderungen des Detektors an Stützung, Stabilität, Ereignis und Vorzeichenübereinstimmung.

**Evidenz sichern.** Manueller und ausreißerverknüpfter Fokus gehören weder zur Analysedefinition noch zur gespeicherten Konfiguration oder öffentlichen URL. Bei aktivem Fokus kann der Export getrennte Fokusabbildungen ergänzen, ohne die normalen Abbildungen der ausgewählten Station über den vollständigen Lauf zu ersetzen. Die Exportinhalte stehen in [Abschnitt 8.4](#sec-8-4).

<a id="sec-5-6"></a>

#### 4.6 Bedienelemente der Benchmark-Ausreißererkennung

Die ΔSNR-Ausreißererkennung für Benchmark ist eine optionale fachkundige Analyse der beibehaltenen **Joint Spots** zu ihren nativen WSPR-Zykluszeiten. Die Erkennung läuft getrennt für jeden exakten Peer-Funkweg `Rufzeichen + Locator` und unabhängig vom ausgewählten Darstellungs-Bin der **Zeitlichen Evidenz**. Einseitige Evidenz kann ein fehlendes ΔSNR nicht ersetzen. [Abschnitt 2.5](#sec-outlier) erklärt Bedienung und Interpretation; [Abschnitt 7.6](#sec-7-outliers) erklärt die experimentelle Methode und ihre Grenzen.

| Bedienelement | Standard / Wertebereich | Methodensymbol | Wissenschaftliche Wirkung |
|---|---|---|---|
| **`ΔSNR-Ausreißerkandidaten melden`** | aus | — | Aktiviert den optionalen Detektor und Ausreißerbericht ausschließlich für Benchmark. Ist die Einstellung aus, fügt WSPRadar dem Ergebnis weder Ausreißererkennung, -felder, -markierungen oder -begriffe noch Ausreißer-Exportmetadaten hinzu. |
| **`Minimale absolute ΔSNR-Abweichung (dB)`** | `6.0`; einschließlich `0.1`–`100.0 dB` | $D_{\min}$ | Verlangt, dass das mediane Residuum des Ereignisses und jeder berichtete Grenzanker mindestens um diesen Betrag von der lokalen Baseline abweichen. |
| **`Minimaler robuster z-Wert`** | `3.0`; einschließlich `0.1`–`100.0` | $Z_{\min}$ | Verlangt, dass sowohl der Ereignismedian als auch jeder berichtete Grenzanker diesen absoluten robusten lokalen Streuungswert erreichen. Der Wert ist deskriptiv und weder eine kalibrierte Wahrscheinlichkeit noch ein konventionelles gaußsches Signifikanzniveau. |
| **`Maximaler Unterschied zwischen Baseline davor/danach (dB)`** | `3.0`; einschließlich `0.1`–`100.0 dB` | $H_{\max}$ | Verwirft einen Kandidaten, wenn sich die Flankenmediane vor und nach dem Ereignis um mehr als diesen Betrag unterscheiden, damit eine instabile oder verschobene Baseline nicht als vorübergehende Auslenkung berichtet wird. |

Die Vergleiche für Abweichung und Baseline-Unterschied verwenden eine feste Toleranz von `0.01 dB`, wie in [Abschnitt 7.6.3](#sec-7-outlier-qualification) erklärt; die konfigurierten Schwellen und internen Evidenzwerte bleiben ungerundet. Für den Vergleich des robusten z-Werts gilt keine solche Toleranz.

Die Standardkombination priorisiert große absolute Auslenkungen: Die 6-dB-Schwelle setzt die nominelle Untergrenze, während der robuste z-Wert weiterhin verlangt, dass die Auslenkung auch im Verhältnis zur lokalen robusten Streuung des Funkwegs groß ist.

Der Schalter und die drei Schwellen werden gespeichert, soweit sie für die Analyse gelten. Ihre Änderung kennzeichnet die Konfiguration als geändert, startet aber nicht automatisch eine Analyse; berechne ein neues Ergebnis mit der normalen richtungsabhängigen Aktion **`RX-Analyse starten`** / **`TX-Analyse starten`**. Alle drei Schwellen gelten unverändert für Spot-Impulse, kurze Ausbrüche und anhaltende Auslenkungen. Für längere Ereignisse gibt es weder einen Dauerbonus noch eine schwächere Schwelle. Ein kleineres $D_{\min}$ oder $Z_{\min}$ beziehungsweise ein größeres $H_{\max}$ macht die Berichterstattung großzügiger; die jeweils umgekehrte Änderung macht sie selektiver. Lege die Schwellen für eine bestätigende Untersuchung vor Sichtung der Kandidaten fest und sichere sie, statt sie so lange anzupassen, bis ein gewünschtes Ereignis erscheint.

<a id="sec-6"></a>
<a id="sec-5-7"></a>

### 5. Fehlersuche und Datenqualität

Prüfe die Laufdefinition, bevor du Filter oder Schwellen veränderst. Ein weiterer Bereich kann mehr Evidenz erhalten, aber keine falsche Identität, kein falsches Band, Zeitfenster oder physisches Zeitplanschema reparieren.

<a id="sec-6-1"></a>

#### 5.1 Zuerst die Laufdefinition prüfen

1. **Target-Identität:** exaktes Rufzeichen beziehungsweise exakte Meldekennung einschließlich Suffix.
2. **QTH:** konfigurierter Locator und die tatsächlich hochgeladenen ersten vier Zeichen.
3. **Band:** exakt ausgewähltes Band und tatsächlich verwendetes Betriebsband.
4. **UTC-Evidenzfenster:** genaue wirksame Start- und Endzeit in den Bedienelementen.
5. **Tatsächlicher Betrieb:** Target-Sende- beziehungsweise Empfangsbetrieb und Spot-Upload.
6. **Referenzbetrieb:** exakte Referenzidentität und überlappende Betriebszeit bei Benchmark.
7. **Versuchsmechanik:** Uhrensynchronisation, Frequenzanordnung für simultanes TX, Signalführung sowie tatsächliche und gemeldete Leistung.

Erst nach diesen Prüfungen sollten Evidenzschwellen, Ausschlüsse, Sonnenstand oder geografischer Bereich geändert werden.

<a id="sec-6-2"></a>

#### 5.2 Fehler nach Symptom eingrenzen

Ein Hinweis auf ein leeres Ergebnis nennt Umfang und Evidenzparameter aus dem abgeschlossenen Lauf und nicht aus später bearbeiteten Bedienelementen. Er trennt eine beobachtete Diagnose von ihrer konfigurierten Anforderung, beispielsweise „höchster beobachteter Wert: `3` bestätigte Gelegenheiten“ und „erforderlich: mindestens `5` pro Station“. Ein konfiguriertes Minimum wird nie als beobachtete Anzahl ausgegeben; ein beobachtetes Maximum erscheint nur, wenn WSPRadar es tatsächlich berechnet und aufbewahrt hat. Bei Performance sind Target-only-Erfolge bestätigte Gelegenheiten und zählen für die Stationsschwellen; ihre Herkunftsanzahl ist eine Teilmenge der Erfolge und keine zusätzliche Gesamtsumme.

| Symptom | Nächste Prüfungen |
|---|---|
| **Keine exakte Target-/Quellenevidenz wurde geliefert** | Prüfe genaue Identität, QTH, Band, Zeitfenster und tatsächlichen Betrieb sowie den gemeldeten Status der strengen Abfrage mit `code = 1`, des historischen Fallbacks und der Upstream-Verfügbarkeit. Dieser Zustand betrifft Eingabe beziehungsweise Quellenevidenz und belegt nicht, dass die konfigurierten Filter zu eng waren. |
| **Quellenevidenz wurde geliefert, aber Filter oder Umfang behielten nichts bei** | Prüfe die angezeigten Stationsausschlüsse, den Sonnenstand und die maximale Peer-Entfernung zusammen mit dem Zeitraum des abgeschlossenen Laufs. Der Hinweis sagt nur, dass angewandte Filter und Umfang keine Evidenz beibehielten; geringe Betriebsaktivität oder Abdeckung können ebenfalls beitragen. |
| **Performance-Identitäten bleiben erhalten, aber keine Station erfüllt die Anforderung an bestätigte Gelegenheiten** | Vergleiche die angezeigte beobachtete Stationsanzahl und die höchste Anzahl bestätigter Gelegenheiten mit dem konfigurierten Minimum bestätigter Gelegenheiten pro Station. Leere Karten, Inspektoren und Tabellen entfallen, statt als Nullergebnisse angezeigt zu werden. |
| **Performance-Stationen qualifizieren sich, aber kein Kartensegment erfüllt seine Stationsanforderung** | Behalte und untersuche die verfügbare Evidenz auf Stationsebene. Nur segmentabhängige Ausgaben fehlen; vergleiche deren Stationsunterstützung mit der konfigurierten Mindestanzahl qualifizierter Stationen pro Kartensegment. |
| **Kein qualifizierendes Benchmark-Ergebnis bleibt erhalten** | Prüfe die konfigurierte Anforderung an Joint-Evidenz, die Mindestanzahl qualifizierter Stationen pro Kartensegment, Filter und Umfang. WSPRadar nennt diese angewandten Anforderungen, erfindet jedoch keine beobachteten Benchmark-Maxima, die die Pipeline nicht berechnet hat. |
| **Benchmark enthält kein ΔSNR** | Prüfe gemeinsame entfernte Peers in überlappenden Zyklen, Referenzbetriebszeit, Uhren, Zeitplanzuordnung, Joint-Schwelle, Filter und Bereich. |
| **Benchmark enthält ΔSNR, aber wenig paarbare Evidenz** | Lies Joint-Evidenzanteil und Decode Outcomes; prüfe Referenzbetriebszeit, Leistung, Schwellen und Bereich. Untersuche, welche Stationen und Zeiten zu Joint Spots beziehungsweise einseitigen Outcomes beitragen, und beschränke die ΔSNR-Interpretation auf die Joint-Teilmenge. |
| **Performance enthält nur sehr wenige Peers** | Prüfe unabhängige Netzaktivität, minimale bestätigte Gelegenheiten, Ausschlüsse, Sonnenstand, Zeitfenster und maximale Peer-Entfernung. |
| **Viele Performance-Erfolge ohne externe Bestätigung** | Ein gültiger Target-Decode bestätigt selbst beide Endpunkte. Diese Target-only-Erfolge gehen einmal in die Dekodierrate ein; ihre separate Herkunftsanzahl wird nicht nochmals addiert. Ohne Target-Decode und ohne den erforderlichen externen Aktivitätsnachweis bleibt der Peer-Zyklus unbekannt und ausgeschlossen. |
| **`Only Reference = 0`** | Prüfe die Konditionierung auf Target-Aktivität, Schwellen und aktiven Bereich; null kann korrekt sein. |
| **Unerwartetes Vorzeichen des ΔSNR bei Referenzaufbau/-station** | Prüfe physische A/B-Zuordnung, Reihenfolge von Target und Referenz, Korrekturvorzeichen, tatsächliche und gemeldete Leistung sowie Kalibrierung. Gleiche einen Funkweg im Drill-Down ab. |
| **Lokales Ergebnis verändert sich mit dem Radius** | Untersuche die lokalen Beitragenden und berichte die Radiusabhängigkeit, statt nur den günstigsten Radius auszuwählen. |
| **Der Lauf wird wegen zu großer Quellmenge beendet** | Verkürze das UTC-Zeitfenster. `Spezial-Rufzeichen Q, 0, 1 ausschließen` oder ein kleinerer lokaler Nachbarschaftsradius können zutreffende Quellabfragen verkleinern; die maximale Peer-Entfernung nicht, weil sie erst nach dem Abruf angewandt wird. |
| **Aktuelle Spots erscheinen unvollständig** | Warte nach dem letzten Zyklus ungefähr fünf Minuten und prüfe danach Upload und Upstream-Status. |

Ein Problem mit Upstream-Daten verändert, was die Quelle geliefert hat. Ein Problem des Versuchsdesigns verändert, ob die beibehaltene Evidenz die beabsichtigte Frage beantwortet. Diagnostiziere und dokumentiere beides getrennt.

<a id="sec-6-3"></a>

#### 5.3 Rufzeichen und Locator prüfen

Performance und jedes Benchmark-Design ordnen Target-Zeilen anhand des exakten Rufzeichens plus des Grid-4 des Target-QTHs zu. Ein Target, das `JN37` meldet, während `JN38` konfiguriert ist, wird nicht zugeordnet.

Referenzaufbau/-station verwendet das exakte Referenzrufzeichen zusammen mit dem aus der ausgewählten Datenbank für den gewählten Zeitraum aufgelösten Grid-4. Die Suche berücksichtigt Referenzrolle (RX oder TX), Band, effektives UTC-Zeitfenster und Datenquelle. Ein gemeldetes Grid-4 wird automatisch aufgelöst; mehrere erfordern eine ausdrückliche Auswahl. Vollständige gemeldete Locatorvarianten, Meldungszahlen sowie erste und letzte Meldezeit unterstützen die Auswahl. Der Standort dient als Auswahlkriterium für Datenbankzeilen und ist kein bestätigter physischer Standort. Die Referenznachbarschaft wählt ihre Beiträge geografisch aus.

Rufzeichen müssen die dokumentierte Regel für Meldekennungen mit 3 bis 15 Zeichen erfüllen. Locator müssen vier oder sechs gültige Maidenhead-Zeichen besitzen. Eine syntaktische Prüfung belegt weder rechtmäßige Zuteilung, physischen Standort noch tatsächlichen Betrieb. Die Peer-Identität ist das exakte `Rufzeichen + vollständig gemeldeter Locator`; veraltete oder wechselnde Locator können eine physische Station aufteilen oder verschieben.

**Simultanes TX mit zusammengesetzten Rufzeichen.** WSPRadar rekonstruiert Typ-2- und Typ-3-Nachrichten nicht und leitet einen fehlenden Sender-Locator nicht aus einer benachbarten Aussendung ab. Prüfe vor dem Sammeln von Evidenz mehrere Upstream-Spots und bestätige, dass die für den WSPRadar-Lauf ausgewählte Datenquelle beide exakten Identitäten im gemeinsamen Target-Grid-4 meldet. Wird eine Identität ohne verwendbaren Locator oder mit einem anderen Grid-4 bereitgestellt, erfüllen diese Zeilen die Identitätszuordnung von Referenzaufbau/-station nicht. Eine korrekte Anzeige in einer anderen Datenbank oder auf einer Karte ersetzt diese Prüfung nicht.

<a id="sec-6-4"></a>

#### 5.4 Fallback für historische Decode-Codes

WSPRadar fragt WSPR-2-Zeilen zunächst mit `code = 1` ab. Liefert diese strenge Abfrage keine Target-seitige Evidenz und liegt der gesamte gewählte Zeitraum vor dem 1. Januar 2022 um 00:00 UTC, wird sie aus Gründen der historischen Kompatibilität ohne dieses Prädikat wiederholt; der Laufstatus meldet den Fallback. Zeiträume, die genau an dieser Grenze enden, sie überschreiten oder danach liegen, behalten durchgehend den strengen Filter. Der Fallback erweitert die Auswahl und kann für Performance und Benchmark unterschiedlich ausfallen.

WSPR-2 ist der Standard-WSPR-Modus mit zweiminütigen Sendezyklen; `code` enthält die in der Datenbank gespeicherte Modusangabe. Bei älteren Datenbankmeldungen können Modusangaben fehlen oder mehrdeutig sein, und die historische Kompatibilitätsabfrage kann Beobachtungen einschließen, deren physikalische Übertragungsart nicht festgestellt werden kann. Der Stichtag ist eine Kompatibilitätsregel und kein belegtes Datum, ab dem sämtliche Modusangaben in der Datenbank zuverlässig wurden. Auch historisches `code = 1` kann mehrdeutig sein <a href="#ref-10">[Ref-10]</a>. Laufstatus und exportiertes `decode_filter_mode` dokumentieren die Abfrageauswahl, ohne zu belegen, dass jede ausgewählte Beobachtung WSPR-2 ist. Ist ein Zeitraum nicht für den Fallback zulässig und liefert die strenge Abfrage keine Target-seitige Evidenz, erläutert WSPRadar den WSPR-2-Filter und den historischen Stichtag; dies belegt nicht, dass das Target einen anderen Modus verwendet hat.

<a id="sec-6-5"></a>

#### 5.5 Wie das Target-Active Gate die Evidenz prägt

Das Target-Active Gate behält simultane Zyklen nur dann bei, wenn eine Beteiligung des Targets beobachtbar ist. Referenzmeldungen aus Zeiten, in denen das Target offline war, werden deshalb nicht automatisch als Misserfolge des Targets gezählt.

Das Gate ist bewusst Target-zentriert. Die Betriebsbereitschaft der Referenz bleibt Teil des Versuchs, und ein Tausch von Target und Referenz kann die einseitigen Decode Outcomes und die zulässige Population verändern. [Abschnitt 7.1.3](#sec-7-activity-eligibility) definiert diese Konditionierung formal.

<a id="sec-6-6"></a>

#### 5.6 Umgang mit Upstream-Daten

Öffentliche WSPR-Datenbanken können Duplikate, falsche Spots, fehlerhafte Locator oder Leistungsangaben, verspätete Uploads und spätere Korrekturen enthalten. wspr.live beschreibt aktuelle Daten als um einige Minuten verzögert. Etwa **fünf Minuten** nach dem letzten Zyklus zu warten ist eine praktische Schätzung und keine Vollständigkeitsgarantie <a href="#ref-10">[Ref-10]</a>.

**Datenquelle und Meldungen prüfen.** Im **System Audit Status** steht, welche Datenbank der abgeschlossene Lauf verwendet hat. Wenn aktuelle Daten unvollständig erscheinen, prüfe zuerst die Uploads und ihre Identitäten und danach, ob diese Zeilen in der verwendeten Datenbank verfügbar sind. Eine Wartezeit allein belegt keine Vollständigkeit.

**Datenbankauswahl und erneuter Versuch.** Bei gleichzeitiger Last kann WSPRadar einen vollständigen neuen Lauf je nach verfügbarer Kapazität von der primären Quelle **wspr.live** an **WSPRDaemon WD2** und danach **WD1** weiterleiten. Dieser geordnete Kapazitätsausgleich unterscheidet sich von einem Quellenwechsel nach einem Ausfall. Fällt eine Quelle aus, bevor der Lauf auf sie festgelegt ist, verwirft WSPRadar den noch nicht veröffentlichten Versuch und kann den vollständigen Lauf mit der nächsten verfügbaren Quelle neu starten. Die Referenzstandortsuche bindet die anschließende Analyse mit Referenzaufbau/-station an dieselbe Datenbank. Fällt diese festgelegte Quelle aus, wird der Versuch beendet und die fehlgeschlagene Standortsuche zurückgesetzt; starte erneut und prüfe den neu ermittelten Referenzstandort. Jeder abgeschlossene Lauf verwendet genau eine Datenbank; Datensätze aus verschiedenen Quellen werden niemals zusammengeführt.

WSPRadar verringert die Empfindlichkeit gegenüber einzelnen fehlerhaften Zeilen durch Identitätskonsolidierung, Mediane, Evidenzschwellen und Drill-Down. Wiederholt auftretende plausible Fehler können dennoch bestehen bleiben. Korrekte Berechnungen können eine falsche Leistungsangabe, einen falschen Locator oder eine falsche Betriebsidentität nicht reparieren.

Der **System Audit Status** dokumentiert die für die Auswertung notwendige Herkunft des Laufs:

| Statuselement | Bedeutung |
|---|---|
| **Datenquelle** | Die eine Upstream-Datenbank, die für den abgeschlossenen Lauf verwendet wurde. Evidenz verschiedener Datenbanken wird innerhalb eines Laufs nicht vermischt. |
| **Historischer Fallback** | Ob die Auswahl ohne die strenge Bedingung für den WSPR-2-Decode-Code wiederholt wurde. |

Diese Angaben zeigen, aus welcher Quelle die Evidenz stammt und ob der historische Kompatibilitäts-Fallback verwendet wurde; sie definieren keine andere wissenschaftliche Methode.

Ein Datenbankabruf mit mehr als 1.000.000 vollständigen Zeilen wird vor der Analyse abgelehnt und nicht stillschweigend abgeschnitten. Verkürze das Zeitfenster oder verwende einen passenden datenbankseitigen Populationsfilter wie in [Abschnitt 5.2](#sec-6-2) beschrieben.


<div style="page-break-before: always;"></div>

<a id="part-iii"></a>
## Teil III: Wissenschaftliche Grundlagen, Methoden und Aussagen

Teil III erklärt, warum die Vergleiche sinnvoll sind, wie die Kennzahlen entstehen und welche Aussagen sie tragen. Er richtet sich an technisch interessierte Funkamateure, HamSCI-Mitwirkende und Gutachter. [Kapitel 6](#sec-d) stellt den Bezug zu früheren Arbeiten her; [Kapitel 7](#sec-7) folgt den Daten von gemeldeten Spots bis zum Ergebnis; [Kapitel 8](#sec-8) behandelt belastbare Aussagen und Reproduzierbarkeit. Die wissenschaftlichen Details erklären, welche Beobachtungen zählen, was fehlt, wie Stationen gewichtet werden, welche Beobachtungen voneinander abhängen und wie Werte umgerechnet werden. Verständliche Erläuterungen und Rechenbeispiele begleiten die Berechnungen.

<a id="sec-d"></a>
### 6. Literatur, Vorarbeiten und Einordnung

Die WSPR-Forschung hat sich durch Beiträge von Funkamateuren, akademischen Forschern, Softwareentwicklern und Instrumentenbauern entwickelt. Ihre Arbeiten haben Verfahren etabliert, um mithilfe eines weltweiten Meldenetzes Antennen zu vergleichen, Stationsprobleme zu untersuchen und die Funkausbreitung zu erforschen.

Dieses Kapitel würdigt ausgewählte Beiträge und erläutert ihre Bedeutung für WSPRadar. Es ist eine gezielte methodische Übersicht, keine umfassende Geschichte. Veröffentlichte Forschungsarbeiten, Preprints, technische Amateurfunkberichte und Softwaredokumentation liefern unterschiedliche Arten von Belegen. Jeder Beitrag verdient Anerkennung für das, was er zeigt.

Drei praktische Erkenntnisse verbinden viele dieser Arbeiten: unter gemeinsamen Bedingungen vergleichen, vor der Deutung fehlender Meldungen die Aktivität belegen und die vollständige Station untersuchen, bevor ein Unterschied einer Antenne zugeschrieben wird.

<a id="sec-d-1"></a>
#### 6.1 Vom Meldenetz zum Versuchsdatensatz

**Joe Taylor, K1JT, und Bruce Walker, W1BW: eine gemeinsame Grundlage für Experimente schaffen.** Taylors WSPR-Protokoll und -Software machten automatisierte Schwachsignalmessungen für gewöhnliche Amateurfunkstationen zugänglich; Walker entwickelte WSPRnet, um ihre Meldungen zu sammeln und bereitzustellen. Ihr Artikel von 2010 benannte ausdrücklich den Wert der Datenbank für die Ausbreitungsforschung. Ein Beispiel fasste Beobachtungen aus mehreren Wochen nach Tageszeit zusammen und zeigte, wie gesammelte Meldungen Muster sichtbar machen können, die über einen einzelnen Funkkontakt oder Betriebszeitraum hinausgehen. Die Gemeinschaft der Stationsbetreiber und Mitwirkenden, die den Betrieb aufrechterhalten, liefert die Beobachtungen, die dies ermöglichen. <a href="#ref-6">[Ref-6]</a>

**Nathaniel Frissell und Mitautoren: Amateurfunkbeobachtungen mit der Weltraumforschung verbinden.** Ihre Studie von 2019 nutzte Beobachtungen aus WSPRNet und dem Reverse Beacon Network, um Veränderungen der Kurzwellenkommunikation während der Sonnenaktivität im September 2017 zu untersuchen. Ein definierter Vergleichsverlauf aus einer ruhigen Periode half, durch Sonneneruptionen verursachte Funkausfälle und die Auswirkungen geomagnetischer Stürme von gewöhnlichen Schwankungen der gemeldeten Aktivität zu unterscheiden. <a href="#ref-13">[Ref-13]</a>

Ihre Arbeit von 2022 zeigte, dass Veränderungen der von WSPRNet, dem Reverse Beacon Network und PSKReporter erfassten Funkentfernungen großräumige wandernde ionosphärische Störungen sichtbar machen konnten. Vergleiche mit SuperDARN-Radar und satellitennavigationsgestützten Messungen des ionosphärischen Elektronengehalts stützten die Interpretation. Diese Studien zeigen, wie Amateurfunkmeldungen zur physikalischen Forschung beitragen können, wenn Stichprobe, Hintergrundbedingungen und unabhängige Beobachtungen gemeinsam berücksichtigt werden. <a href="#ref-14">[Ref-14]</a>

Frissell et al. ordnen WSPRNet zusammen mit dem Reverse Beacon Network und PSKReporter als etablierte Amateurfunk-Beobachtungsnetze ein, die langfristige Beobachtungen der Unterseite der Ionosphäre (Bottomside) liefern. Sie unterscheiden diese Netze von zweckgebundenen wissenschaftlichen Instrumenten und empfehlen eine Kreuzkalibrierung zwischen Instrumentennetzen. Die Übersicht stützt die wissenschaftliche Nutzung von Amateurfunkbeobachtungen; sie macht nicht jeden beitragenden Empfänger zu einem kalibrierten Sensor. <a href="#ref-7">[Ref-7]</a>

Die WSPR-Datenbank ist damit eine wertvolle Quelle von Beobachtungsdaten, deren Interpretation vom jeweiligen Experiment abhängt. Ausrüstung, lokaler Störpegel und Betriebspläne unterscheiden sich; Rufzeichen, Locatoren und Leistungen werden von den Betreibern angegeben; und gewöhnliche Spot-Datensätze enthalten erfolgreiche Decodes. Eine fehlende Meldung benötigt zusätzlichen Kontext.

<a id="sec-d-2"></a>
#### 6.2 WSPR-Beobachtungsdaten interpretierbar machen

<a id="sec-d-lo"></a>
**Lo und Mitautoren: vor der Deutung fehlender Meldungen die Aktivität belegen.** Ihre Studie von 2022 zur Greyline-Ausbreitung auf 7 MHz prüfte, ob Sender andernorts gehört worden waren und ob Empfänger andere Stationen gehört hatten, bevor sie fehlenden Empfang interpretierte. Außerdem berücksichtigte sie die Stationsidentität, den Standort und Beobachtungen von mehreren Standorten. Damit wird die praktische Frage — „War die Ausrüstung überhaupt in Betrieb?“ — zum Bestandteil der wissenschaftlichen Methode.

Ihr Beitrag ging über Aktivitätsprüfungen hinaus. Anhand eines vollständigen Jahres von Beobachtungen zwischen Europa und Australasien untersuchten sie tageszeitliche und jahreszeitliche Empfangsmuster und fanden Unterschiede zwischen den beiden Senderichtungen. Als mögliche Erklärung für fehlenden Empfang bei Sonnenuntergang schlugen sie einen erhöhten Störpegel an europäischen Sommerabenden vor. Die Studie verbindet Ausbreitungsforschung mit Stationsdiagnose: Empfang hängt sowohl von der Empfangsumgebung als auch von der Ausbreitung zwischen den Stationen ab. <a href="#ref-9">[Ref-9]</a>

**Gwyn Griffiths, G3ZIL, Rob Robinett, AI6VN, und Glenn Elmore, N6GN, 2019–2020: den Rauschpegel parallel zum WSPR-Empfang messen.** Ihr technischer Bericht entwickelte Rauschpegelschätzungen aus denselben Empfängeraufzeichnungen, die zur WSPR-Decodierung verwendet wurden. Sie verglichen Messungen in den Pausen zwischen Aussendungen mit Schätzungen im Frequenzbereich, die auch während des Empfangs möglich waren, und untersuchten eine Kalibrierung bezogen auf den Antenneneingang des Empfängers.

Der besondere Beitrag besteht in zusätzlichen Messdaten, mit denen sich SNR-Veränderungen erklären lassen: Sowohl stärkere Signale als auch ein niedrigerer Rauschpegel können den Empfang verbessern. Gewöhnliche WSPR-Spot-Datensätze allein können diese Ursachen nicht trennen. Diese Arbeit unterstützte die erweiterten Messungen von WSPRdaemon und wurde anschließend in QEX, September/Oktober 2020, veröffentlicht. <a href="#ref-15">[Ref-15]</a> <a href="#ref-16">[Ref-16]</a>

Zusammen zeigen diese Ansätze, warum eine Empfangsanalyse Belege für Stationsaktivität und Informationen über die Bedingungen benötigt, unter denen das SNR gemessen wurde.

<a id="sec-d-3"></a>
#### 6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen

**Patrick Destrem, F6IRF, 2008: automatisierte Umschaltung und Vergleiche nach Richtung und Entfernung.** Destrem dokumentierte eine computergesteuerte Antennenumschaltung im Zehnminutentakt, die Korrektur von Meldungen auf eine gemeinsame Sendeleistung und die Auswertung nach Empfangsstation und geografischer Gruppierung. Dies waren zeitlich verschachtelte Messungen: Die Antennen wurden in abwechselnden Zeitabschnitten getestet.

Seine Folgeuntersuchung zeigte, warum sich ein Gesamtergebnis von einem Ergebnis unterscheiden konnte, das nur weit entfernte Empfänger einbezog. Er erweiterte den Ansatz auf Empfangsantennen für 160 m und auf Stationsvergleiche über gemeinsame entfernte Empfänger. Diese Berichte liefern frühe praktische Beispiele dafür, WSPR als experimentelles Messsystem zu verwenden und dabei die gegenseitige Beeinflussung der Antennen, den lokalen Störpegel und eine begrenzte Zahl von Beobachtungen zu berücksichtigen. Ihr besonderer Wert liegt darin, den Vergleich auf die Richtungen, Entfernungen und Betriebsbedingungen zu beziehen, unter denen eine Anlage gut funktioniert. <a href="#ref-17">[Ref-17]</a>

**Charles Preston, damals KL7OA und später K7TAA, 2009: simultaner Vergleich unter gemeinsamen Bedingungen.** Preston beschrieb den Betrieb zweier Antennen mit getrennten Sendern oder Empfängern am selben Standort und den Vergleich gleichzeitiger Meldungen. Bei TX-Vergleichen beobachtet derselbe entfernte Empfänger beide Aussendungen. Dadurch werden Unterschiede infolge wechselnder Ausbreitungs- und Empfangsbedingungen verringert. Seine praktische Frage lautete, welche der verfügbaren Antennen am eigenen Standort besser funktioniert.

Sein vorläufiger Bericht unterschied das empfangene SNR von der Signalstärke und berücksichtigte die gegenseitige Beeinflussung benachbarter Antennen. Er untersuchte auch einseitige Meldungen: Ein fehlendes Gegenstück konnte auf ein schwaches Signal oder auf Störungen auf einer der Sendefrequenzen hinweisen. Damit wurde früh erkannt, dass Meldungen nur einer Seite nützliche Informationen enthalten, aber interpretiert werden müssen. Der kleine erste Versuch demonstrierte die Methode; seine Aussagen zu den Antennen blieben vorläufig. <a href="#ref-18">[Ref-18]</a>

Preston veröffentlichte anschließend *Antenna Comparisons Using Simultaneous WSPR Measurements* in QEX, Juli/August 2017. <a href="#ref-19">[Ref-19]</a>

<a id="sec-d-toledo"></a>
**Sivan Toledo, 2010: ein nützliches negatives Ergebnis zur zeitlichen Versuchsplanung.** Toledo testete Antennen in etwa einstündigen Blöcken und stellte fest, dass die ausbreitungsbedingten SNR-Schwankungen mit den scheinbaren Antennenunterschieden vergleichbar waren. Er prüfte die Beobachtungen eines weiteren Empfängers, um zu untersuchen, ob die Schwankungen von seiner eigenen Station ausgingen; dort traten ähnliche Veränderungen auf.

Der Versuch zeigte, warum dieser Messaufbau die Einflüsse nicht zuverlässig trennen konnte. In seiner Diskussion stellte er den Zusammenhang mit der automatisierten Umschaltung und den gleichzeitigen Aussendungen anderer Funkamateure her. Die praktische Erkenntnis: Mehr Meldungen retten einen Vergleich nicht, wenn die Antennen unter wesentlich unterschiedlichen Bedingungen getestet wurden. <a href="#ref-3">[Ref-3]</a>

<a id="sec-d-milazzo"></a>
**Carol Milazzo, KP4MD, 2011: vollständige Stationen vergleichen und beide Richtungen untersuchen.** Milazzo verglich 29 km voneinander entfernte Stationen über einen gemeinsamen Empfänger in etwa 1.750 km Entfernung, korrigierte das SNR um Unterschiede der Sendeleistung und verglich das beobachtete Verhalten mit VOACAP. Sie untersuchte auch den Empfang in Gegenrichtung: Auf 40 m fiel der Sendevergleich zugunsten der einen und der Empfangsvergleich zugunsten der anderen Station aus.

Dies macht die Studie besonders hilfreich für das Verständnis der Rolle von Ausrüstung und lokalem Störpegel. Eine Station, die beim Senden stärkere Meldungen erzeugt, kann dennoch schlechter empfangen. Unterschiedliche Sendeanteile, verschiedene Standorte und der ausgewählte gemeinsame Empfänger begrenzen die Übertragbarkeit der konkreten Ergebnisse. <a href="#ref-4">[Ref-4]</a>

<a id="sec-d-griffiths-squibb"></a>
**Gwyn Griffiths, G3ZIL, und Nigel Squibb, G4HZX, 2017: Vergleiche desselben Signals zur Stationsdiagnose nutzen.** Sie wählten Meldungen desselben Senders zur selben Zeit aus und untersuchten SNR-Differenzen in Bezug auf Zeit, Entfernung, Bodenfeuchte und Änderungen an den Stationen.

Ihre Arbeit ging über die Beschreibung von Mustern hinaus. Sie untersuchten Niederschlag und zogen einen weiteren Referenzempfänger heran, um die Erklärung durch Bodenfeuchte zu prüfen. Nachdem bei G4HZX drei Bodenradials ergänzt worden waren, war der zuvor beobachtete Zusammenhang mit der Bodenfeuchte im anschließenden Testzeitraum nicht mehr vorhanden. Sie dokumentierten außerdem ein verbessertes SNR nach einer Änderung des Computerstandorts und der Audioanbindung.

Der besondere Beitrag ist ein praktischer Ablauf aus Beobachtung, Hypothese und Eingriff. Wiederholte Vergleiche, Umweltinformationen und dokumentierte Stationsänderungen machten die Diagnose aussagekräftiger als reine Spotzahlen. Die Beobachtungen betreffen vollständige Empfangsanlagen; die vorgeschlagenen physikalischen Mechanismen bleiben Interpretationen, die durch die begleitenden Prüfungen unterschiedlich stark gestützt werden. <a href="#ref-5">[Ref-5]</a>

<a id="sec-d-vanhamel"></a>
**Vanhamel, Machiels und Lamy, 2022: die Empfangsausrüstung vor dem Antennenvergleich charakterisieren.** Ihr begutachteter 160-m-Versuch verband zwei Empfangsketten mit einer gemeinsamen Antenne, um deren Versatz zu messen, bevor simultane Antennenvergleiche durchgeführt wurden. Zwei siebentägige Kalibrierungszeiträume ergaben jeweils einen mittleren Versatz von etwa 1,2 dB, den sie beim Vergleich berücksichtigten.

Sie untersuchten außerdem den Empfang mit identischen Antennen, die rechtwinklig zueinander ausgerichtet waren. Das gemessene, von der Ausrichtung abhängige SNR führte zur Diskussion von Polarisation und ionosphärischen Effekten als möglichen Erklärungen. Der praktische Beitrag besteht darin, die Empfangsapparatur selbst prüfbar zu machen, bevor Antennenunterschiede interpretiert werden, und dabei beobachtetes Verhalten von den vorgeschlagenen Ursachen zu trennen. <a href="#ref-2">[Ref-2]</a>

<a id="sec-d-zander"></a>
**Jens Zander, 2022: Annahmen und Präzision des simultanen TX-Vergleichs erklären.** Zanders Preprint entwickelt eine mathematische Beschreibung zweier lokaler Antennen, die unter getrennten Rufzeichen gleichzeitig zu gemeinsamen entfernten Empfängern senden. Ein Empfänger trägt zum SNR-Vergleich bei, wenn er beide Aussendungen im selben WSPR-Zyklus meldet. Unter den Modellannahmen heben sich gemeinsame Ausbreitungsdämpfung und Empfängerrauschen in jeder SNR-Differenz auf.

Gleiche oder korrigierte Sendeleistungen bleiben wesentlich; Störungen, fehlgeschlagene Decodes, Quantisierung und Unterschiede zwischen den Sendeketten spielen weiterhin eine Rolle. Eine Differenz, die innerhalb eines entfernten Empfängers gebildet wird, erfordert keine Kalibrierung gegenüber anderen Empfängern.

Seine Vorversuche behielten von etwa 1.000 Meldungen ungefähr 150–200 gepaarte Beobachtungen aus 15–35 Empfängern bei, mit einer Stichproben-Standardabweichung nahe 3 dB. Die Analyse erklärt, wie Mittelwertbildung die Präzision verbessern kann, und erörtert geografische Stichprobe, Antennenrichtwirkung und unbekannte Elevationswinkel. Sein besonderer Beitrag ist die mathematische Behandlung der Aufhebung gemeinsamer Einflüsse, von Störungen und von Verzerrungen durch die räumliche Stichprobe. <a href="#ref-1">[Ref-1]</a>

**Thomas Rietdorf, DL2OAH, 2026: synchronisierte Vergleiche in einem praktischen Mehrbandablauf zusammenführen.** Sein DARC-Vortrag beruht auf Messungen vom Januar 2025 und vergleicht horizontale und vertikale Anlagen mit synchronisierten Transceivern in getrennten RX- und TX-Durchläufen auf vier Bändern.

Er unterscheidet Joint Spots von einseitigen Meldungen und untersucht SNR-Differenzen nach Zeit und Richtung. Der zugehörige R-Arbeitsablauf, mit Programmierhilfe durch KI-Werkzeuge entwickelt, zeigt, wie ein Funkamateur von heruntergeladenen Meldungen zu einer strukturierten Untersuchung gelangen kann.

Unterschiedliche Transceivermodelle bleiben Bestandteil der verglichenen Anlagen; die Ergebnisse sind deshalb als Stationsvergleiche zu lesen, unter Beachtung der Hinweise des Autors zu Ausbreitung und Verteilung der entfernten Stationen. Der Beitrag ist ein praktisches Beispiel, das synchronisierte Messungen, statistische Analyse und mehrere einander ergänzende Sichtweisen auf den Antenneneinsatz an einem Standort verbindet. <a href="#ref-20">[Ref-20]</a>

<a id="sec-d-4"></a>
#### 6.4 Analyseinfrastruktur und verwandte Werkzeuge

**Griffiths und Robinett, 2020: umfangreichere Datenbankanalysen wiederverwendbar machen.** Ihre WSPRdaemon-TimescaleDB-Datenbank und Grafana-Beispiele führten Meldungen für denselben Sender, dieselbe Zeit und dasselbe Band zusammen und stellten anschließend SNR-Differenzen, Mediane, Quartile, zeitliche Muster, Entfernung und Azimut dar. Sie bezogen außerdem Rauschmessungen neben den Spot-Daten ein und unterstützten Exporte.

Der Beitrag bestand in einem zugänglichen Analyseablauf: Betreiber konnten Stationen und Zeiträume auswählen, zeitliche und geografische Strukturen untersuchen und Unterschiede erkennen, die reine Spotzahlen verdeckten. <a href="#ref-21">[Ref-21]</a>

**Arne und wspr.live: öffentlicher Zugang zur WSPR-Analyse in großem Maßstab.** Das Projekt wspr.live nutzt ClickHouse, um große Bestände historischer und aktueller WSPR-Meldungen direkt abfragbar zu machen. Die dokumentierte SQL-Schnittstelle, Dashboards und Exportfunktionen ermöglichen Forschern, Beobachtungen für ihre eigenen Fragestellungen auszuwählen und auszuwerten.

Der technische Beitrag verbindet Datenerfassung, Datenbankorganisation und öffentlichen Abfragezugang zu einem Dienst, den andere Anwendungen nutzen können. Damit wird unabhängige Forschung möglich, ohne dass jedes Projekt selbst eine historische Datenbank aufbauen und pflegen muss. Das Projekt würdigt außerdem HB9VQQ für die Bereitstellung von Rechenressourcen. <a href="#ref-10">[Ref-10]</a>

**Rob Robinett, AI6VN, und die WSPRdaemon-Gemeinschaft: Erfassung, Hosting und laufender Betrieb.** WSPRdaemon trägt zuverlässigen Empfang und die Übermittlung von Meldungen, Datenbankhosting und öffentliche Analysedienste bei. Die Dokumentation würdigt Arnes ClickHouse-Datenbankarbeit und das Hosting durch WSPRdaemon und macht so die Zusammenarbeit hinter dieser Infrastruktur deutlich. Die frühere TimescaleDB-Arbeit und die ClickHouse-Dienste sind unterschiedliche Teile dieser Entwicklung. <a href="#ref-11">[Ref-11]</a>

WSPRadar ist unmittelbar auf diese öffentlichen Dienste angewiesen: **wspr.live ist seine primäre Datenbank, mit WD2 und WD1 von WSPRdaemon als Alternativen**. Entwicklung, Rechenressourcen, Hosting und laufende ehrenamtliche Pflege sind wesentliche Beiträge zu WSPRadar und zur gesamten Forschungsgemeinschaft.

Weitere Werkzeuge erleichtern ergänzende Bereiche des Experimentierens mit WSPR:

| Mitwirkende oder Projekt | Besonderer praktischer Beitrag |
|---|---|
| **Arne — wspr.live** | Die oben beschriebene öffentliche Datenbank- und Abfragegrundlage mit Dashboards und Downloads für Forschung und externe Anwendungen. <a href="#ref-10">[Ref-10]</a> |
| **Phil, VK7JJ — WSPR.Rocks** | Interaktive Abfragen, Karten, Tabellen und Diagramme, einschließlich der Untersuchung von Duplikaten und Empfangsdurchlassbereichen. Head2Head vergleicht Empfänger, Sender oder Softwareversionen anhand auswählbarer Kennzahlen. SpotQ bietet eine heuristische Rangfolge auf Grundlage von Entfernung, gemeldeter Leistung und SNR. <a href="#ref-22">[Ref-22]</a> |
| **Rob Robinett, AI6VN, und Mitwirkende — WSPRdaemon** | Erfassung mit mehreren Empfängern, zeitgesteuerte Bandwahl, zwischengespeicherte Meldungen und Wiederaufnahme nach Ausfällen. Zusätzliche Rausch- und Dopplerinformationen unterstützen Untersuchungen, die über herkömmliche Spot-Datensätze hinausgehen. <a href="#ref-11">[Ref-11]</a> |
| **Richard Newstead und SOTABEAMS — WSPRlite/DXplorer** | Eigenständige Kleinleistungsbaken in Verbindung mit zugänglichen Antennen- und Standortvergleichen, einschließlich des Reichweitenindikators DX10. Newsteads Innen-/Außenversuch von 2017 verglich ausdrücklich SNR-Meldungen, die von derselben Station zur selben Zeit empfangen wurden. <a href="#ref-23">[Ref-23]</a> <a href="#ref-24">[Ref-24]</a> |
| **Walter Machiels, ON4AWM — WSPR-Station-Compare** | Ein spezieller RX-Vergleichsablauf mit Korrektur eines gemessenen Empfänger-Offsets, Mindestzahl von Beobachtungen je Station, Rufzeichenfilterung und Azimutauswahl. Diese Bedienelemente übertragen experimentelle Methoden in wiederverwendbare Software für den Stationsbetrieb. <a href="#ref-25">[Ref-25]</a> |
| **Fred, W6BSD — Antenna Performance Analysis Tool** | Ein Berichtsgenerator, der Empfangsbelege nach Zeit, Band und Empfangsstandort ordnet. Dadurch lässt sich die beobachtete Stationsabdeckung leichter untersuchen, ohne eine eigene Auswertung programmieren zu müssen. <a href="#ref-26">[Ref-26]</a> |
| **Colin Murray, GM4EAU — WATT** | Ein bearbeitbarer Excel/VBA-Arbeitsablauf für Abfragen, Filterung, weitere Berechnungen und die Wiedergabe auf der Karte über aufeinanderfolgende Zeitintervalle. Die Animation hilft Betreibern, sich verändernde Ausbreitungsmuster zu untersuchen. <a href="#ref-27">[Ref-27]</a> |

Diese Werkzeuge behandeln sich überschneidende Fragestellungen, unterscheiden sich aber in ihren Filtern, Vergleichseinheiten und Zusammenfassungen. Ähnlich aussehende Abbildungen beruhen daher nicht zwangsläufig auf identischen Berechnungen.

<a id="sec-d-5"></a>
#### 6.5 Was WSPRadar übernimmt, integriert und ergänzt

WSPRadar baut auf der Arbeit dieser Gemeinschaft auf: gesammelte Meldungen, Aktivitätsprüfungen, Sendeleistungskorrektur, Vergleiche unter gemeinsamen Bedingungen, Kalibrierung von Empfangsketten, Datenbankanalyse und geografische Interpretation.

Es führt diese Ideen in einem einheitlichen RX- und TX-Arbeitsablauf zusammen:

* **Benchmark** vergleicht ein Target mit einem Referenzaufbau beziehungsweise einer Referenzstation oder einer dynamischen Referenznachbarschaft.
* **Joint Spots aus demselben WSPR-Zyklus** liefern ΔSNR, während einseitige Decode Outcomes zusätzliche Empfangsbelege beschreiben.
* Normierung anhand gemeldeter Leistung und optionale referenzseitige Korrektur machen die angewandten Anpassungen ausdrücklich sichtbar.
* **Performance** misst erfolgreiche Decodes innerhalb bestätigter Gelegenheiten.
* Stationsgleichgewichtete und beobachtungsbezogene Zusammenfassungen unterscheiden den gleichen Einfluss jeder Station vom Einfluss des Meldungsvolumens.
* Ansichten von Karte, Segment, Station und einzelnen Beobachtungen bieten einen Rückweg zu den zugrunde liegenden Belegen.
* Gespeicherte Konfigurationen, verarbeitete Evidenz und Exporte unterstützen die Reproduzierbarkeit.

Die ΔSNR aus Joint Spots beschreibt nur Vergleiche mit qualifizierenden Target- und Referenzmeldungen für dieselbe entfernte Station und denselben WSPR-Zyklus. Funkwege, für die auf einer Seite nur selten Empfangsmeldungen vorliegen, können deshalb unterrepräsentiert sein; einseitige Decode Outcomes liefern ergänzende Belege. Die Dekodierrate in Performance beschreibt den Erfolg des Targets innerhalb bestätigter Gelegenheiten, die durch erfolgreiche Target-Decodes oder qualifizierende Aktivitätsbelege festgestellt werden. Die Aussage dieser Ergebnisse ist auf die verfügbaren Meldungen und die gewählten Betriebsbedingungen beschränkt; aus ihnen lassen sich weder unmittelbar eine unbedingte Empfangswahrscheinlichkeit noch kalibrierte Werte für den Antennenwirkungsgrad ableiten.

Bezogen auf die ausgewertete Literatur liegt WSPRadars methodischer Beitrag in der konkreten Kombination und den ausdrücklichen Definitionen: welche Beobachtungen zugelassen werden, wie die Target-Aktivität die Analyse bedingt, wie Gelegenheiten und Ergebnisse gezählt werden, wie lokale Referenzen gebildet werden und wie stationsbezogene und geografische Zusammenfassungen gewichtet werden. Diese Regeln verbinden die experimentelle Frage mit einem nachvollziehbaren Ergebnis und werden in [Kapitel 7](#sec-7) erläutert.

<a id="sec-7"></a>
### 7. Wissenschaftliche Methoden

**Benchmark** untersucht, wie sich Target und Referenz unterscheiden, wenn in demselben WSPR-Zyklus für dieselbe entfernte Station Meldungen auf beiden Seiten vorliegen. **Performance** untersucht ohne Referenz, wie oft das Target innerhalb bestätigter Gelegenheiten erfolgreich ist. Dieses Kapitel erklärt genau, welche Beobachtungen zählen und wie ihre Ergebnisse zusammengefasst werden.

Die Berechnung folgt einer einfachen Abfolge: **gemeldete Spots → zulässige Beobachtungen je Station und Zyklus → SNR-Differenzen oder Decode Outcomes → Zusammenfassungen**. Diese Stufen sind voneinander zu unterscheiden. Ein Datenbank-Spot ist ein gemeldeter Decode; ein Joint Spot oder eine bestätigte Gelegenheit ist eine nach den folgenden Regeln aus Meldungen gebildete Beobachtungseinheit. Ein Median oder Prozentsatz fasst anschließend diese beibehaltenen Einheiten zusammen. Er ist keine zusätzliche Funkmessung.

Beginne mit der gemeinsamen Datengrundlage in [Abschnitt 7.1](#sec-7-foundations) und lies anschließend [Benchmark in Abschnitt 7.2](#sec-7-benchmark) oder [Performance in Abschnitt 7.3](#sec-7-performance). [Abschnitt 7.4](#sec-7-views) erklärt Bereich und Darstellung, [Abschnitt 7.5](#sec-7-claims) die Belastbarkeit von Schlussfolgerungen und [Abschnitt 7.6](#sec-7-outliers) die optionale experimentelle Ereigniserkennung.

Dies sind deskriptive Berechnungen für die ausgewählte Evidenz. Ein Ergebnis kann für die beibehaltenen Beobachtungen exakt sein, ohne eine physische Ursache, künftige Performance oder einen Wert für alle Stationen zu belegen. [Abschnitt 7.5](#sec-7-claims) und [Kapitel 8](#sec-8) erklären diese Interpretationsgrenzen.

<a id="sec-7-foundations"></a>
#### 7.1 Gemeinsame Datengrundlage

<a id="sec-7-spots-identities-cycles"></a>
<a id="sec-7-1"></a>
<a id="sec-7-2"></a>
##### 7.1.1 Spots, Identitäten und Zyklen

Jeder abgeschlossene Lauf liest genau eine ausgewählte WSPR-Datenbank und mischt keine Quellen. Ihre Meldungen stammen von unterschiedlichen Sendern, Empfängern, Decodern und Meldesystemen; die verwendete Datenbank gehört zur Herkunftsdokumentation des Laufs.

Ein **Spot** ist ein gemeldeter erfolgreicher Decode. Ein **WSPR-Zyklus** ist das zweiminütige Intervall, das an einer geraden UTC-Minute beginnt. Die grundlegende Beobachtung betrifft eine exakte entfernte Stationsidentität in einem zulässigen Zyklus auf dem ausgewählten Band. Die entfernte Station ist bei RX ein Sender und bei TX ein Empfänger. Mehrere qualifizierende Meldungen werden gemäß [Abschnitt 7.1.2](#sec-7-normalization-consolidation) zusammengefasst, bevor die Outcomes gezählt werden.

Benchmark bildet einen Joint Spot, wenn beide Seiten für dieselbe entfernte Identität im selben Zyklus qualifizierende Evidenz liefern. RX vergleicht zwei Empfänger, die denselben Sender beobachten; TX vergleicht zwei Sender, die derselbe Empfänger beobachtet. Die Referenznachbarschaft bildet zunächst aus qualifizierenden lokalen Stationen ihre Referenz für diese entfernte Station und diesen Zyklus. WSPRadar verbindet niemals Meldungen aus verschiedenen Zyklen zu einem Paar. Die Zuordnung verlangt keine identischen HF-Frequenzen und belegt keine identischen physischen Ausbreitungswege; simultane TX-Signale benötigen normalerweise freie, getrennte Frequenzen.

**Eine Identität besteht aus dem exakten Rufzeichen und dem für die jeweilige Rolle erforderlichen Locator.** Würden unterschiedliche gemeldete Standorte gleichgesetzt, könnte ein Vergleich zwischen verschiedenen Stationen oder Funkwegen entstehen.

| Station oder Rolle | Identifizierung durch WSPRadar |
|---|---|
| **Target — alle Analysen** | Exaktes Empfangsrufzeichen bei RX oder Senderufzeichen bei TX zusammen mit dem vierstelligen Locator des Target-QTH. |
| **Referenz — Referenzaufbau/-station** | Exaktes Referenzrufzeichen zusammen mit seinem aus der Datenbank aufgelösten vierstelligen Locator. |
| **Entfernte Station — alle Analysen** | Exaktes Rufzeichen zusammen mit dem vollständigen gemeldeten Locator: der entfernte Sender bei RX oder der entfernte Empfänger bei TX. |
| **Lokale Beiträge — Referenznachbarschaft** | Lokale Empfängeridentitäten bei RX oder lokale Senderidentitäten bei TX innerhalb des gewählten Radius, unterschieden anhand des exakten Rufzeichens und vollständigen gemeldeten Locators. |

Die Target-Auswahl verwendet Grid-4, auch wenn ein sechsstelliges QTH konfiguriert ist. Das vollständige konfigurierte QTH bleibt der Ursprung für Entfernung, Azimut, Sonnenhöhe und Nachbarschaftsgeometrie. Ein gemeinsames Grid-4 beweist keine physische Ko-Lokation. Dasselbe entfernte Rufzeichen an zwei vollständigen Locatorn bildet weiterhin zwei getrennte Identitäten, auch wenn beide Locator im selben Grid-4 liegen.

Die Datenbank muss die benötigten Identitätsfelder liefern. WSPRadar rekonstruiert keine zusammengesetzten Rufzeichen aus Hashes und übernimmt keine Locator aus benachbarten Typ-2-/Typ-3-Zyklen. Ein fehlendes oder anders dargestelltes Rufzeichen beziehungsweise ein solcher Locator wird nicht durch Schlussfolgerung zulässig. Der lokale Referenzpool schließt das exakte Target-Rufzeichen aus; ein Basisrufzeichen und eine Form mit Suffix bleiben verschieden. Falsche, veraltete oder wechselnde Locator können eine physische Station aufteilen, geografisch verschieben oder den Ausschluss beweglicher Stationen auslösen.

**Auch erweitertes WSPR liefert getrennte Zwei-Minuten-Beobachtungen.** WSPR-2 bezeichnet den Sendemodus; Typ 1, Typ 2 und Typ 3 beschreiben Nachrichteninhalte. Eine Typ-2-Nachricht enthält ein zusammengesetztes Rufzeichen und die Leistung, aber keinen Locator. Ihre ergänzende Typ-3-Nachricht enthält einen 15-Bit-Rufzeichen-Hash, einen sechsstelligen Locator und die Leistung <a href="#ref-12">[Ref-12]</a>. WSPRadar klassifiziert diese Nachrichtentypen nicht, rekonstruiert keine fehlenden Phasen und fasst sie nicht zu einer vierminütigen Beobachtung zusammen.

Einer oder beide Zyklen können Joint Spots liefern, wenn die benötigten Identitäten in der Datenbank aufgelöst sind. Ein Joint Spot in einem Zyklus setzt keinen weiteren im nächsten voraus. Übereinstimmende Nachrichtenfolgen und Zeitpläne sind die Empfehlung für kontrolliertes TX in [Abschnitt 2.2.1](#sec-3-tx-benchmark-simultaneous), keine von WSPRadar durchgeführte Zulässigkeitsprüfung anhand des Nachrichtentyps. [Anhang B](#sec-simultaneous-tx-setup) beschreibt die praktische Einrichtung und die Datenbank-Vorabprüfung.

Das ausgewählte effektive UTC-Fenster definiert den Lauf. Für Zeiträume, die vollständig vor 2022 liegen und bei der strengen Abfrage keine Target-Evidenz liefern, kann der historische Fallback die Bedingung `code = 1` lockern; [Abschnitt 5.4](#sec-6-4) nennt die genaue Grenze und die Unsicherheit der Modusangaben. Datenbankverfügbarkeit, Verzögerungen und Quellenwahl erklärt [Abschnitt 5.6](#sec-6-6).

<a id="sec-7-normalization-consolidation"></a>
##### 7.1.2 Leistungsnormierung und Zusammenfassung

**WSPRadar bezieht erfolgreiche SNR-Beobachtungen bei Benchmark und Performance auf eine gemeinsame gemeldete Sendeleistung.** WSPR meldet das SNR in dB bezogen auf eine Referenzbandbreite von 2500 Hz und die Sendeleistung in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar bezieht erfolgreiche SNR-Beobachtungen sowohl bei RX als auch bei TX auf eine gemeinsame gemeldete Leistung von **30 dBm (1 W)**:

$$SNR_{\mathrm{norm}}=SNR_{\mathrm{reported}}-P_{\mathrm{reported}}+30$$

Die SNR-Werte stehen hier in dB, die gemeldete Leistung in dBm. Ein Signal mit gemeldetem SNR von `-15 dB` bei `20 dBm` Sendeleistung wird auf dem Vergleichsniveau von 30 dBm zu `-5 dB`: Die 10 dB geringere Leistung wird rechnerisch ausgeglichen. Dies entfernt nur den **gemeldeten Leistungsunterschied**. Es stellt weder die Decodes her, die bei 1 W entstanden wären, noch korrigiert es Antennengewinn, Strahlungswirkungsgrad, Speiseleitungsverlust, EIRP, Empfängerkalibrierung oder lokalen Störpegel. Decode Outcomes und Performance-Gelegenheiten bleiben die tatsächlich beobachteten.

**Mehrere Meldungen zählen weiterhin als eine Beobachtung für diese Seite, entfernte Station und diesen Zyklus.** WSPRadar behält das stärkste qualifizierende normierte SNR bei: für Performance, für jede Seite von Referenzaufbau/-station und für die Target-Seite der Referenznachbarschaft. Lokale Referenzbeiträge verwenden stattdessen einen Median innerhalb jeder Identität, bevor der Nachbarschafts-Median gebildet wird; [Abschnitt 7.2.5](#sec-7-neighborhood) erklärt diese zweistufige Berechnung. Die Zusammenfassung verbindet niemals aufeinanderfolgende Zyklen.

Die Auswahl der stärksten Meldung steht für den **besten beobachteten Empfang**, nicht für einen Zentralwert eines physischen Empfängers. Schwächere duplikatähnliche Meldungen, Zweit-Decodes oder unerwünschte Signalrepliken können den beibehaltenen Wert nicht absenken. Ihr Mittelwert oder Median lässt sich nicht begründet als SNR des beabsichtigten Hauptsignals interpretieren. WsprDaemon dokumentiert ebenfalls, dass beim Zusammenführen mehrerer Empfänger das beste SNR an WSPRnet gemeldet wird <a href="#ref-11">[Ref-11]</a>.

Diese bestehende Praxis beweist nicht, dass eine gespeicherte Meldung zum beabsichtigten Signal gehört oder beide Seiten dieselbe Spektralkomponente ausgewählt haben. Unterschiedliche Mehrfachempfänger- oder Meldeanordnungen können Asymmetrien erzeugen. Später berechnete Mediane fassen die beibehaltenen Beobachtungen zusammen; sie machen die Auswahl des SNR je Zyklus nicht rückgängig.

<a id="sec-7-activity-eligibility"></a>
<a id="sec-7-3"></a>
##### 7.1.3 Target-Aktivität und Zulässigkeit

**Eine fehlende Meldung sollte nur dann gegen das Target zählen, wenn dessen Betrieb nachgewiesen ist.** Benchmark und Performance behalten deshalb Zyklen mit beobachtbarer Target-Beteiligung bei. Dies heißt **Konditionierung auf Target-Aktivität**.

| Richtung | Was belegt Target-Aktivität in einem Zyklus? |
|---|---|
| **RX** | Der Target-Empfänger hat mindestens einen qualifizierenden Decode hochgeladen. |
| **TX** | Irgendwo liegt mindestens eine qualifizierende Meldung einer Target-Aussendung vor. |

Der Aktivitätsnachweis kann von außerhalb des ausgewählten geografischen Bereichs stammen. Ein Nachweis außerhalb des Bereichs belegt Aktivität, geht aber nicht selbst in dessen Outcomes, Zusammenfassungen oder Exporte ein. Ein Zyklus ohne Nachweis wird ausgeschlossen; WSPRadar kann Ausfallzeit nicht von Betrieb ohne gemeldeten Decode unterscheiden. Ergebnisse beschreiben deshalb beobachtbare Target-aktive Zyklen, nicht die gesamte verstrichene Zeit oder sämtliche geplanten Aussendungen.

Diese Regel ist **asymmetrisch**. Die Betriebszeit der Referenz bildet keine zweite Zulässigkeitsbedingung und muss außerhalb der Anwendung kontrolliert oder dokumentiert werden. Ein Tausch von Target und Referenz kann beibehaltene Zyklen und einseitige Decode Outcomes verändern. Jeder Joint Spot belegt bereits Target-Beteiligung; diese Bedingung verändert deshalb nicht sein ΔSNR, sondern die einseitige beziehungsweise asynchrone Evidenz und den Gelegenheitsnenner bei Performance.

**Stationsausschlüsse wirken unterschiedlich auf den Aktivitätsnachweis.** Bei Performance kann eine Target-Meldung mit einem Peer, der später wegen eines speziellen Rufzeichens oder wechselnden Standorts ausgeschlossen wird, weiterhin Aktivität belegen. Bei Benchmark greifen diese Ausschlüsse zuerst: Der Nachweis muss einen danach noch zulässigen Peer betreffen. Der geografische Bereich wird bei beiden Analysen erst anschließend angewendet. Ein Zyklus, dessen Target-Aktivität ausschließlich ein ausgeschlossener Peer belegt, kann deshalb eine Performance-Gelegenheit für einen anderen zulässigen Peer behalten, aber kein Benchmark-Outcome. Der ausgeschlossene Peer selbst trägt zu keiner Ergebnispopulation bei.

Target-Aktivität allein macht nicht jede stille entfernte Station zu einem verpassten Decode. Performance benötigt zusätzlich die in [Abschnitt 7.3.1](#sec-7-performance-opportunities) definierte Evidenz für die beteiligten Endpunkte.

<a id="sec-7-benchmark"></a>
#### 7.2 Benchmark: Unterschiede und gemeinsame Evidenz

<a id="sec-7-benchmark-outcomes"></a>
<a id="sec-7-6"></a>
##### 7.2.1 Decode Outcomes und fehlende Beobachtungen

**Delta SNR und Decode Outcomes beantworten unterschiedliche Fragen.** ΔSNR beschreibt den Signalunterschied innerhalb der Joint Spots. Decode Outcomes zeigen, wie viel beibehaltene Evidenz auf beiden Seiten oder nur auf einer Seite vorlag.

| Outcome | Bedeutung |
|---|---|
| **Only Target** | Für diese entfernte Identität und diesen Zyklus liegt Target-Evidenz vor, aber keine Referenzevidenz. |
| **Joint** | Beide Seiten haben qualifizierende Evidenz für dieselbe entfernte Identität und denselben Zyklus; ΔSNR ist möglich. |
| **Only Reference** | Für diese entfernte Identität und diesen Zyklus liegt Referenzevidenz vor, aber keine Target-Evidenz. Der Zyklus bleibt erhalten, weil Target-Aktivität anderweitig belegt wurde. |
| **Both (Async)** | Auf Stationsebene liegt beibehaltene Evidenz beider Seiten vor, aber kein qualifizierendes Paar desselben Zyklus für die betreffende Stationskategorie. Daraus entsteht kein ΔSNR. |

Joint Spots setzen erfolgreiche Beobachtungen auf beiden Seiten voraus. Schwache Signale, Kollisionen, QRM, Decoderverhalten, Leistungsunterschiede und Ausbreitung können beeinflussen, ob ein Paar entsteht. Bedingungen nahe der Decodierschwelle einer Seite können deshalb in der Joint-Evidenz unterrepräsentiert sein; fehlende Paare dürfen nicht als zufällige Ausfälle angenommen werden.

Bei einseitigen Meldungen lässt sich kein SNR der fehlenden Seite rekonstruieren. Sie erhalten kein künstliches ΔSNR und lassen sich nicht als SNR-Paar normieren. Bei TX können ungleiche tatsächliche oder gemeldete Leistungen einseitige Outcomes beeinflussen, obwohl das Joint-ΔSNR normiert ist. Auch die Konditionierung auf Target-Aktivität macht die beiden einseitigen Kategorien asymmetrisch; sie sind keine symmetrischen Siege und Niederlagen.

**Identitätsfehler bei erweitertem WSPR erfordern eine gesonderte Prüfung.** Typ 3 verwendet einen 15-Bit-Rufzeichen-Hash. Ein unaufgelöster oder kollidierender Hash kann einen Decode ohne Identifikation lassen oder einem falschen Rufzeichen, Locator oder Leistungswert zuordnen; QRP Labs hat dies dokumentiert <a href="#ref-28">[Ref-28]</a>. Vereinzelte betroffene Zeilen können einen Median nahezu unverändert lassen. Gehäufte oder zwischen Target und Referenz ungleiche Effekte können jedoch Abdeckung, einseitige Outcomes sowie Stations- oder Segmentergebnisse verändern. Eine große Datenmenge allein schützt nicht davor.

WSPRadar kann das konfigurierte Rufzeichen und den Locator in der Datenbank prüfen, aber nicht jede Upstream-Hash-Zuordnung als korrekt bestätigen. Führe bei zusammengesetzten Rufzeichen die Datenbank-Vorabprüfung und phasenbezogene Prüfung aus [Anhang B](#sec-simultaneous-tx-setup) durch und berücksichtige dabei Nachrichtenposition, Empfänger, Seite und Zeit.

Die Auswahl erfolgreicher SNR-Beobachtungen bei Performance und die Auswahl nach Joint-Decode bei Benchmark sind unterschiedliche Einschränkungen. Lies ihre SNR-Zusammenfassungen gemeinsam mit den jeweiligen Gelegenheiten, Decode Outcomes und der Evidenzabdeckung.

<a id="sec-7-benchmark-delta"></a>
<a id="sec-7-5"></a>
##### 7.2.2 Delta SNR und Referenzkorrektur

Die **Referenzkorrektur** berücksichtigt einen unabhängig bestimmten additiven Offset. Er wird zum normierten Referenz-SNR addiert, niemals zum Target:

$$SNR_{\mathrm{Reference,corr}}=SNR_{\mathrm{Reference,norm}}+C_{\mathrm{Reference}}$$

Die Korrektur muss über das relevante Band, die Signalpegel, den Gerätezustand und die Zeit ungefähr stabil sein. Trage einen gemessenen Kalibrierversatz mit dem Vorzeichen `target - reference` ein. [Abschnitt 4.3](#sec-5-3) erklärt die Bedienelemente und [Anhang C](#sec-reference-snr-calibration) das Kalibrierverfahren.

**Delta SNR vergleicht einen Joint Spot.** Ziehe den korrigierten Referenzwert vom normierten Target-Wert ab:

$$\Delta SNR=SNR_{\mathrm{Target,norm}}-SNR_{\mathrm{Reference,corr}}$$

| Ergebnis | Bedeutung für diesen Joint Spot |
|---|---|
| **Positives ΔSNR** | Das Target-SNR ist höher. |
| **ΔSNR gleich null** | Target-SNR und korrigiertes Referenz-SNR sind gleich. |
| **Negatives ΔSNR** | Das Referenz-SNR ist höher. |

**Vorzeichenprüfung.** Target `-10 dB` minus Referenz `-12 dB` ergibt **+2 dB**. Eine Referenzkorrektur von `+1.5 dB` erhöht die Referenz auf `-10.5 dB`; damit wird ΔSNR zu **+0.5 dB**. Eine positive Korrektur verringert also den ausgewiesenen Target-Vorteil; die Target-Beobachtung selbst bleibt unverändert.

Bei RX-Joint-Spots beobachten beide Empfänger denselben Sender, sodass sich dessen gemeinsamer gemeldeter Leistungsanteil herauskürzt. TX-Joint-Spots vergleichen unterschiedliche Sendesignale und hängen unmittelbar von korrekten Leistungsangaben sowie unkorrigierten Unterschieden der Sendeausrüstung ab. Das resultierende ΔSNR ist ein beobachteter Unterschied zwischen den vollständigen dokumentierten Aufbauten; die Zuordnung zu einer Antenne oder einem Bauteil erfordert weiterhin die in [Kapitel 2](#sec-3) beschriebenen physischen Kontrollen.

<a id="sec-7-benchmark-aggregation"></a>
<a id="sec-7-7"></a>
##### 7.2.3 Stations- und Kartenaggregation

**Stationsgleichgewichtung verhindert, dass eine Station allein durch ihre größere Beobachtungszahl das Ergebnis dominiert.** Sie macht aus wiederholten Meldungen keine unabhängigen Experimente.

Bei **Referenzaufbau/-station** bildet WSPRadar zunächst Joint Spots desselben Zyklus. Anschließend gilt die Mindestzahl an Joint-Evidenz getrennt für jede exakte entfernte Identität aus Rufzeichen und vollständigem Locator. WSPRadar berechnet deren medianes ΔSNR und danach den Median dieser Stationsmediane für ein Kartensegment. Der Median ist der mittlere sortierte Wert oder bei gerader Anzahl das Mittel der beiden mittleren Werte.

Der **Median der Joint Spots** fasst stattdessen alle beibehaltenen Joint-Werte zusammen. Jeder Joint Spot hat dasselbe Gewicht; Stationen mit mehr Joint Spots erhalten dadurch mehr Einfluss. Die beiden Zusammenfassungen können voneinander abweichen, ohne dass eine Berechnung falsch ist:

| Qualifizierende Station | Beibehaltene ΔSNR-Werte (dB) | Stationsmedian |
|---|---|---:|
| A | +6, +6, +6, +6, +6, +6 | +6 dB |
| B | -2, -2 | -2 dB |
| C | -1, -1 | -1 dB |

Der stationsgleichgewichtete Median beträgt **-1 dB**: Das ist der mittlere Wert in `-2, -1, +6`. Der Median der Joint Spots beträgt **+6 dB**, weil die beiden mittleren Werte unter allen zehn Beobachtungen jeweils `+6` sind. Prüfe bei solchen Abweichungen die beitragenden Stationen; keine Zusammenfassung allein belegt einen Antennenvorteil.

Bei jedem Benchmark-Design zählen genau die Identitäten mit einem qualifizierenden Stationsmedian für die Mindestanzahl an Stationen je Kartensegment. Rein einseitige Identitäten liefern keine ΔSNR-Unterstützung. Ein Rufzeichen an `JO31AA` und dasselbe Rufzeichen an `JO31AB` zählen getrennt, sofern beide qualifizieren. Mediane von `+2` und `+4 dB` ergeben einen Segmentmedian von `+3 dB` bei einer Stationszahl von **2**: Ein Minimum von zwei Stationen ist erfüllt, ein Minimum von drei nicht. Dies zählt gemeldete Identitäten, keine nachweislich unabhängigen physischen Standorte.

<a id="sec-7-benchmark-coverage"></a>
<a id="sec-7-8-2"></a>
##### 7.2.4 Joint-Evidenzanteil

**Der Joint-Evidenzanteil misst, wie viel beibehaltene Evidenz ΔSNR liefern kann.** Für eine Station und ein Zeitintervall lautet sein Nenner **Only Target + Joint + Only Reference**. Er umfasst weder alle geplanten Zyklen noch ausschließlich gemeinsam decodierte Beobachtungen.

| Zusammenfassung | Berechnung in Worten |
|---|---|
| **Stationsgleichgewichteter Joint-Evidenzanteil** | Für jede Station die Joint-Anzahl durch ihre gesamten beibehaltenen Outcomes teilen. Diese Anteile mitteln und als Prozentsatz ausdrücken. |
| **Joint-Evidenzanteil auf Outcome-Ebene** | Die Outcomes aller beitragenden Stationen zusammenzählen. Die gesamte Joint-Anzahl durch alle beibehaltenen Outcomes teilen und als Prozentsatz ausdrücken. |

Eine Station trägt bei, wenn sie im Intervall mindestens ein beibehaltenes Outcome hat, auch bei **null Joint Spots**. Eine Station ohne Outcome trägt keinen Anteil bei. In den Balken zur Stationsunterstützung liefert jede Station insgesamt einen Zählwert, aufgeteilt nach ihren Anteilen Only Target, Joint und Only Reference. Balken zur Outcome-Unterstützung zählen dagegen jedes beibehaltene Outcome.

Beispielsweise trägt eine Station mit 80 Joint-Outcomes von 100 einen Anteil von 80% bei; eine andere mit 1 von 10 einen Anteil von 10%. Ihr stationsgleichgewichteter Anteil beträgt **45%**, zusammengezählt ergibt sich dagegen `81 / 110 = 73.6%`. Die erste Berechnung gewichtet Stationen gleich, die zweite Outcomes. Keine ist eine Target-Siegquote. Die Asymmetrie durch Target-Aktivität aus [Abschnitt 7.1.3](#sec-7-activity-eligibility) gilt weiterhin.

<a id="sec-7-neighborhood"></a>
##### 7.2.5 Referenznachbarschaft

**Die Referenznachbarschaft bildet vor derselben Stations- und Segmentaggregation eine lokale Referenz.** Für jede entfernte Identität und jeden Zyklus:

1. Qualifizierende Meldungen normieren und die Referenzkorrektur auf die lokalen Referenzwerte anwenden.
2. Mehrere Meldungen derselben lokalen Identität aus Rufzeichen und vollständigem Locator auf einen Median innerhalb dieser Identität reduzieren.
3. Den Median über diese lokalen Identitätswerte bilden; jede beitragende Identität liefert einen Wert.
4. Diese Referenz vom stärksten qualifizierenden normierten Target-SNR abziehen und anschließend wie oben die ΔSNR-Mediane für entfernte Stationen und Segmente bilden.

Abwesende lokale Identitäten werden weggelassen, niemals mit null angesetzt. Es gibt keine eigene Mindestzahl lokaler Beiträge je Zyklus: Ein Beitrag wird zur Referenz; ohne Beitrag gibt es weder Referenz-SNR noch Joint-ΔSNR. Die übrigen Schwellen für Joint-Evidenz und Kartenunterstützung legen keine Mindestgröße der Nachbarschaft fest. Mehrere lokale Identitäten können Geräte oder Standort teilen; gleiche Identitätsgewichtung bedeutet daher nicht zwangsläufig gleiche Gewichtung physischer Standorte.

**Schon eine andere Zusammensetzung kann das Ergebnis verschieben.** Korrigierte lokale SNR-Werte von `-18, -12, -6 dB` ergeben eine Referenz von `-12 dB`. Bei Target-SNR `-10 dB` ist ΔSNR `+2 dB`. Fällt der Beitrag `-6 dB` weg, wird die Referenz zu `-15 dB` und ΔSNR zu **+5 dB**, ohne Target-Änderung. Die lokale Referenz gilt für die beobachteten Beiträge, die entfernte Station und den jeweiligen Zyklus.

<a id="sec-7-performance"></a>
<a id="sec-7-4"></a>
#### 7.3 Performance: Gelegenheiten und Erfolg

**Performance fragt, wo und wie beständig deine Station erfolgreich ist, wenn sich eine Empfangsgelegenheit nachweisen lässt.** Nicht jeder stille Zwei-Minuten-Zyklus zählt als Misserfolg. Ein erfolgreicher Target-Decode belegt seine eigene Gelegenheit; andernfalls erfordert ein Miss den Nachweis, dass die relevante entfernte Station aktiv war, während auch das Target nachweislich in Betrieb war.

<a id="sec-7-performance-opportunities"></a>
##### 7.3.1 Was zählt als Gelegenheit?

Jede Gelegenheit betrifft eine exakte entfernte Stationsidentität in einem Target-aktiven WSPR-Zyklus auf dem ausgewählten Band, nach Anwendung der geltenden Populations- und geografischen Filter. Die erforderliche Evidenz hängt von der Richtung ab:

* **RX:** Der entfernte Sender wird vom Target oder von einem anderen zulässigen Empfänger decodiert. Die Meldung eines anderen Empfängers bestätigt, dass der Sender auf Sendung war. Ohne Target-Decode stützt sie einen Miss nur dann, wenn im selben Zyklus auch die Aktivität des Target-Empfängers belegt ist.
* **TX:** Der entfernte Empfänger decodiert das Target oder einen anderen qualifizierenden Sender. Seine Meldung eines anderen Senders bestätigt, dass dieser Empfänger in Betrieb war. Ohne Target-Meldung dort stützt sie einen Miss nur dann, wenn im selben Zyklus auch die Aktivität des Target-Senders belegt ist.

Ein Target-seitiger Erfolg bedeutet bei RX, dass der Target-Empfänger den entfernten Sender decodiert hat, oder bei TX, dass der entfernte Empfänger den Target-Sender decodiert hat. Bei nachgewiesener Target-Aktivität gilt:

| Target-seitiger Erfolg? | Bestätigen Meldungen anderer Stationen die entfernte Aktivität? | Klassifikation | Als Gelegenheit zählen? |
|---|---|---|---|
| **Ja** | **Nein** | Erfolg, den der Target-Decode selbst belegt. | **Ja — einmal.** |
| **Ja** | **Ja** | Erfolg mit zusätzlicher externer Bestätigung. | **Ja — einmal.** |
| **Nein** | **Ja** | Miss: Die erforderliche Aktivität ist bestätigt, aber kein Target-seitiger Erfolg wurde gemeldet. | **Ja — einmal.** |
| **Nein** | **Nein** | Unbekannt: Die Aktivität der beteiligten Endpunkte ist nicht ausreichend belegt. | **Nein.** |

Erfolge ohne externe Bestätigung bleiben als Teilmenge der Erfolge erkennbar; sie werden nicht nochmals zu den Gesamtsummen addiert. Auch eine zusätzliche externe Bestätigung eines Erfolgs erzeugt keine zweite Gelegenheit. Eine Meldung einer anderen Empfangsstation belegt nicht, dass der für diese Gelegenheit benötigte Empfänger empfangsbereit war. Unbekannte Beobachtungen bleiben ausgeschlossen und erhalten kein erfundenes SNR.

<a id="sec-7-performance-rates"></a>
##### 7.3.2 Dekodierraten und Gewichtung

Die **Dekodierrate** ist der Prozentsatz bestätigter Gelegenheiten, die erfolgreich waren:

$$\text{Dekodierrate (\%)}=\frac{\text{erfolgreiche Gelegenheiten}}{\text{bestätigte Gelegenheiten}}\times100$$

Bestätigte Gelegenheiten bestehen aus **Erfolgen plus Misses**. WSPRadar berechnet für jede qualifizierende entfernte Station eine Rate; eine Station qualifiziert sich nur, wenn ihre Gelegenheitszahl das konfigurierte Minimum erreicht. Anschließend stehen zwei ergänzende Zusammenfassungen zur Verfügung:

| Zusammenfassung | Berechnung | Beantwortete Frage |
|---|---|---|
| **Stationsgleichgewichtete Dekodierrate** | Die einzelnen Dekodierraten der qualifizierenden Stationen mitteln; jede Station erhält dasselbe Gewicht. | Wie beständig war das Target über die qualifizierenden Stationen hinweg erfolgreich, wenn jede gleich gewichtet wird? |
| **Dekodierrate auf Gelegenheitsebene** | Erfolge und bestätigte Gelegenheiten dieser Stationen zusammenzählen; Gesamterfolge durch Gesamtgelegenheiten teilen. | Welcher Anteil aller beibehaltenen Gelegenheiten war erfolgreich? |

**Beispiel.** Zwei qualifizierende Stationen haben `90 Erfolge / 100 Gelegenheiten = 90%` und `5 / 10 = 50%`. Gleiche Stationsgewichtung ergibt **70%**. Zusammengezählt ergibt sich `95 / 110 = 86.4%`: 95 Erfolge und 15 Misses, jeweils einmal gezählt. Die höhere Gesamtrate entsteht durch die größere Gelegenheitszahl bei der erfolgreicheren Station; keine Gewichtung ist die einzig „wahre“ Rate.

<a id="sec-7-performance-reach"></a>
##### 7.3.3 Mindestens-einmal-Reichweite

**Mindestens-einmal-Peer-Reichweite** misst die Breite: den Prozentsatz qualifizierender entfernter Identitäten mit mindestens einem Target-Erfolg. Ein Erfolg und viele Erfolge zählen für die Reichweite jeweils einmal. Beide Stationen im Beispiel waren erfolgreich; ihre Reichweite beträgt deshalb **100%**, trotz unterschiedlicher Dekodierraten. Bei einer festen Peer-Population können zusätzliche Beobachtungen einen früheren Erfolg nicht aufheben. Die qualifizierende Population kann sich jedoch zwischen Läufen ändern; die ausgewiesene Reichweite muss deshalb mit längerer Laufzeit nicht steigen.

<a id="sec-7-performance-snr"></a>
##### 7.3.4 Erfolgreiches Target-SNR

**Erfolgreiches Target-SNR** beschreibt nur beibehaltene erfolgreiche Decodes nach Normierung und Auswahl der stärksten Meldung. Misses haben kein Target-SNR. Die folgenden Abschnitte erklären, wie diese Werte für Mediane, Streuung und Extremwerte gruppiert werden. Lies SNR und Dekodierrate gemeinsam: Zusätzliche grenzwertige Decodes können SNR-Zusammenfassungen absenken und zugleich Empfang und Reichweite verbessern.

Performance beschreibt die bedingte Beteiligung im beobachteten Netz. Sie ist weder unbedingte Empfängerempfindlichkeit noch Erfolgswahrscheinlichkeit aller versuchten Aussendungen oder absoluter Stationswirkungsgrad.

<a id="sec-7-views"></a>
<a id="sec-7-8"></a>
#### 7.4 Bereich und Zusammenfassungen über Ort und Zeit

Dieselbe Evidenz kann je nach Gewichtung unterschiedliche Fragen beantworten. Eine Karte vergleicht meist Stationen, eine Joint-Spot-Verteilung Beobachtungen; eine nach UTC-Stunden zusammengefasste Ansicht kann mehrere Tage verbinden. Die folgenden Regeln definieren diese Unterschiede.

<a id="sec-7-view-scope"></a>
<a id="sec-7-9"></a>
##### 7.4.1 Bereich, Geografie und Filter

Entfernung und Azimut werden aus dem konfigurierten Target-QTH und den gemeldeten Peer-Locatorn auf einer Kugelerde mit Radius **6371 km** berechnet. Die Karte ist azimutal-äquidistant und auf das Target-QTH zentriert, mit Entfernungsgrenzen bei `2500`, `5000`, `10000`, `15000`, `20000` und `22000 km` sowie **22,5 Grad** breiten Richtungssektoren. Locator beschreiben Rasterzellen, keine vermessenen Antennenpositionen; daraus entstehen weder vermessungsgenaue Positionen noch Messungen des Abstrahlwinkels.

**Maximale Peer-Entfernung vom Target** schließt Stationen an oder jenseits der gewählten Entfernung vor wissenschaftlicher Aggregation und Export der verarbeiteten Evidenz aus. Inspector-Auswahlen können die beibehaltene Population eingrenzen, aber keine ausgeschlossenen Stationen zurückholen. Target-Aktivität wird global vor der geografischen Filterung festgestellt. Der Ausschluss beweglicher Stationen erkennt Rufzeichen mit wechselndem Standort ebenfalls in der ansonsten zulässigen globalen Population, bevor der Entfernungsbereich angewendet wird.

Die Sonnenstandsklassifikation verwendet die Sonnenhöhe am **Target-QTH zum Zeitstempel des WSPR-Zyklus**. Sie beschreibt die Bedingungen am Target, nicht die Beleuchtung des vollständigen Ausbreitungswegs oder aller entfernten Endpunkte. Datenbank-Abrufgrenzen und Bedienelemente zur Eingrenzung der Quellpopulation erklärt [Abschnitt 5.6](#sec-6-6).

<a id="sec-7-view-geography"></a>
<a id="sec-7-8-1"></a>
##### 7.4.2 Geografische Zusammenfassungen

Segmentzusammenfassungen verwenden die vollständige qualifizierende Population im aktiven geografischen Bereich. Das Sortieren einer Tabelle oder Auswählen einer Zeile definiert diese Population nicht neu. Benchmark-Karten verwenden den in [Abschnitt 7.2.3](#sec-7-benchmark-aggregation) beschriebenen Median qualifizierender Stationsmediane; die Joint-Spot-Verteilung bleibt getrennt verfügbar.

Performance-Entfernungsprofile gruppieren Stationen anhand ihrer berechneten Entfernung vom Target-QTH. Intervallbreiten von `125`, `250`, `500` oder `1000 km` werden deterministisch aus der aktiven Entfernungsspanne gewählt. Die Grenzen liegen bei ganzzahligen Vielfachen ab `0 km`; die letzte ausgewählte Obergrenze ist eingeschlossen. Getrennte ausgewählte Bereiche behalten ihre Lücken, statt sie mit Nullevidenz aufzufüllen.

Jedes Entfernungsintervall zeigt Reichweite, beide Gewichtungen der Dekodierrate und erfolgreiches Target-SNR. Für das SNR liefert jede Station zunächst ihren Median der erfolgreichen Werte; das Profil fasst diese Stationsmediane zusammen. Ab drei Medianen ist ein IQR verfügbar, bei zwei ein Min–Max-Intervall und bei einem ein Einzelwert. Stationen mit ausschließlich Misses erhalten kein künstliches SNR.

<a id="sec-7-view-time"></a>
<a id="sec-7-8-3"></a>
##### 7.4.3 Chronologische Evidenz

**Chronologische Ansichten bewahren die zeitliche Abfolge des Laufs.** Die Intervalle beginnen am ausgewählten UTC-Start und verwenden die gewählte Breite; das letzte Intervall kann kürzer sein. Leere Intervalle bleiben ohne Wert, nicht bei 0 dB. Die angebotenen Breiten richten sich nach der gesamten Laufdauer, nicht nach der beobachteten Evidenzspanne; [Abschnitt 4.5](#sec-5-5) nennt Auswahl und Standardwerte.

**Benchmark-ΔSNR** fasst beibehaltene Joint Spots innerhalb jedes chronologischen Intervalls zusammen. Die Abdeckung umfasst getrennt davon alle beibehaltenen einseitigen und Joint-Outcomes mit den beiden in [Abschnitt 7.2.4](#sec-7-benchmark-coverage) definierten Anteilen. Einer leeren ΔSNR-Ebene kann deshalb weiterhin einseitige Evidenz gegenüberstehen; sie belegt nicht, dass die Datenbank keine Meldungen geliefert hat.

**Die Abweichung des erfolgreichen SNR bei Performance** fragt, ob jede Station stärker oder schwächer als ihr eigener üblicher erfolgreicher Pegel war. Eine Station benötigt mindestens drei erfolgreiche normierte Beobachtungen im vollständigen Lauffenster. Deren Median ist ihre Basislinie; diese wird von jedem erfolgreichen Wert abgezogen. Ein Funkweg, der gewöhnlich bei `-10 dB` liegt, liefert bei beobachteten `-7 dB` somit eine Abweichung von `+3 dB`. Null bedeutet den üblichen erfolgreichen Pegel dieses Funkwegs, nicht Gleichheit von Target und Referenz.

Chronologisch trägt jede Station höchstens eine mediane Abweichung pro Intervall bei.

Die Performance-Unterstützung verwendet alle bestätigten Gelegenheiten ihrer qualifizierenden Stationen, auch solcher mit zu wenigen Erfolgen für die SNR-Abweichungsebene. In einem chronologischen Intervall wird der Beitrag jeder Station entsprechend ihrer Dekodierrate auf Erfolg und Miss aufgeteilt. Die gesamte Stationsunterstützung zählt damit beitragende Stationen; die zusammengefasste Gelegenheitsunterstützung zählt bestätigte Gelegenheiten. Die zugehörigen Anteile ergeben die stationsgleichgewichtete Dekodierrate beziehungsweise die Rate auf Gelegenheitsebene.

<a id="sec-7-view-folding"></a>
##### 7.4.4 Tage nach UTC-Stunde zusammenfassen

Benchmark-ΔSNR führt beibehaltene Joint Spots über die vertretenen Tage nach UTC-Stunde zusammen. Für die Abweichung des erfolgreichen SNR bei Performance liefert jede Station zunächst einen Median je Datum und Stunde. Weitere Zeilen innerhalb dieser Stations-Datums-Stunde erhöhen das Gewicht nicht. Stationen, die an mehr Tagen vertreten sind, und Tage mit mehr Stationen tragen jedoch weiterhin mehr Werte bei. Stationen oder Tage werden also nicht über den gesamten Lauf gleich gewichtet.

**Die Zusammenfassung nach UTC-Stunden verbindet Tage und erfordert mindestens zwei Tage mit der jeweils relevanten Evidenz.** Für die Performance-Unterstützung ist ein Datum vertreten, wenn irgendwo im aktiven Bereich und ausgewählten Fenster mindestens eine qualifizierende bestätigte Gelegenheit vorliegt. Die Benchmark-Abdeckung verwendet Tage mit beliebigen beibehaltenen Outcomes; ihre ΔSNR-Ebene benötigt dagegen Tage mit beibehaltenem endlichem Joint-ΔSNR. Ein Tag mit Joint-Evidenz und ein zweiter mit ausschließlich einseitigen Outcomes können deshalb die Stundenabdeckung ermöglichen, ohne eine ΔSNR-Stundenansicht zu ermöglichen. Eine vertretene Datums-Stunde, die das ausgewählte Fenster überlappt, geht auch dann in den Nenner der gemittelten Unterstützung ein, wenn sie keine Evidenz enthält. Stunden außerhalb des Fensters bleiben ausgeschlossen. Eine nur teilweise überlappende Randstunde zählt als vollständiger Slot, ohne Gewichtung nach Beobachtungsdauer; ihr Mittel kann dadurch niedriger ausfallen.

Für Performance-Raten nach UTC-Stunde werden zunächst die Erfolge und Gelegenheiten jeder Station in dieser Stunde über die vertretenen Tage zusammengezählt; anschließend werden die einzelnen Stationsraten gleich gewichtet gemittelt. Die Stunden-Stationsunterstützung ist die Anzahl der Stationspräsenzen je Datum und Stunde geteilt durch die Anzahl vertretener Datums-Stunden. Die Stunden-Gelegenheitsunterstützung ist die zusammengezählte Outcome-Anzahl geteilt durch denselben Nenner. Die Benchmark-Stundenabdeckung drückt das Outcome-Volumen ebenfalls je vertretener Datums-Stunde aus und behält dabei ihre stationsgleichgewichteten und zusammengezählten Joint-Anteile bei.

Eine Stundenansicht kann einen Zusammenhang mit der Tageszeit zeigen, beweist aber keine Wiederholung an jedem Datum. Prüfe die chronologische Ansicht, bevor du ein Muster als wiederkehrend bezeichnest.

<a id="sec-7-view-station"></a>
<a id="sec-7-8-4"></a>
##### 7.4.5 Evidenz der ausgewählten Station

Die Evidenz der ausgewählten Station begrenzt den aktiven beibehaltenen Bereich auf eine exakte entfernte Identität. Sie verändert weder die vorgelagerte Zuordnung noch die Zulässigkeit.

* **Benchmark:** Chronologische und stundenweise Zusammenfassungen verwenden das Joint-Spot-ΔSNR dieser Station; die getrennte Abdeckung umfasst Only Target, Joint und Only Reference.
* **Performance:** Chronologische Zusammenfassungen verwenden das tatsächliche normierte erfolgreiche Target-SNR. Das SNR-Stundenprofil verwendet einen Datums-Stunden-Median je vertretenem Datum. Erfolgs-/Miss-Anzahlen und Dekodierrate beschreiben denselben Funkweg. Bei einer Station sind beide Gewichtungen der Dekodierrate innerhalb eines belegten Intervalls gleich; Stationspräsenz und Gelegenheitsvolumen bleiben jedoch unterschiedliche Unterstützungszahlen.

Der fokussierte Drill-Down zeigt native beibehaltene Beobachtungen: konsolidiertes Joint-Spot-ΔSNR bei Benchmark oder erfolgreiches normiertes Target-SNR bei Performance, jeweils zu den tatsächlichen WSPR-Zykluszeiten. „Nativ“ bedeutet nach Zuordnung, Zusammenfassung und wissenschaftlicher Filterung, nicht unveränderte Datenbankzeilen. Diese Punkte unterscheiden sich von Zeitintervallmedianen oder Dichtezusammenfassungen.

Der Ausreißerfokus kann den Kandidaten mit seinen vollständigen Basislinienflanken umfassen, auch wenn dies über das gewöhnliche Fokusintervall hinausgeht. Er verwendet das abgeschlossene Detektorergebnis, statt einen neuen Detektor an den fokussierten Ausschnitt anzupassen. Lokale Basislinien und Abweichungshilfslinien gelten für diesen Kandidaten; sie sind Detektorkoordinaten, keine Konfidenzintervalle oder eigenständigen Qualifikationsprüfungen. Änderungen an Fokus oder Anzeigeintervallen verändern die Ansicht, nicht das abgeschlossene wissenschaftliche Ergebnis.

<a id="sec-7-view-spread"></a>
<a id="sec-7-8-5"></a>
##### 7.4.6 Streuung und Darstellungsskalen

**Der IQR beschreibt die mittlere Hälfte der beitragenden Werte; Min–Max beschreibt ihren gesamten Wertebereich.** Beides sind keine Konfidenzintervalle. Zeitliche IQR-Bänder erfordern mindestens fünf beitragende Werte; ein Median bleibt bei weniger Werten verfügbar. Je nach Ansicht sind diese Werte Joint Spots, erfolgreiche Target-Beobachtungen, Stations-Intervallmediane oder Stations-Datums-Stunden-Mediane. Für Performance-Entfernungsprofile gilt die gesonderte Drei-Stationen-Regel aus [Abschnitt 7.4.2](#sec-7-view-geography).

**Die Dichtefarbe ist innerhalb jeder Abbildung relativ.** Die am stärksten belegte Zelle erhält `100`; andere Zellen werden proportional zu ihrer Anzahl skaliert. Dies bedeutet nicht 100% der gesamten Evidenz. Vergleiche absolute Datenmengen zwischen Abbildungen anhand der Unterstützungszahlen.

Benchmark-Histogramme verwenden normalerweise 1-dB-Intervalle, bei einem eindeutigen 0,5-dB-Raster 0,5 dB und bei breiten Wertebereichen gröbere Intervalle. Zeitliche Dichtezellen bleiben 1 dB hoch und verschieben sich mit der Referenzkorrektur. Bei derselben beibehaltenen Population bewegen sich Zellen und Beobachtungen gemeinsam, während Zellanzahlen und relative Farben unverändert bleiben. Die Gruppierung für die Anzeige rundet weder die beibehaltenen Beobachtungen noch ihre Kennzahlen; gebrochene Werte müssen nicht in der Zellmitte liegen.

Benchmark-Zeit- und Histogrammachsen können die Randbereiche um den Bereichsmedian komprimieren und dabei absolute `0 dB` sichtbar halten. Lies die beschrifteten dB-Koordinaten, statt Unterschiede aus den optischen Abständen zu schätzen. In Histogrammen codiert die **Balkenlänge an der Prozentachse**, nicht die dargestellte Fläche, die Größe. Diese Transformationen verändern weder Werte noch Anzahlen, Mediane oder Quartile. Die Achsen des erfolgreichen SNR bei Performance bleiben in dB linear.

<a id="sec-7-claims"></a>
<a id="sec-7-10"></a>
#### 7.5 Wie belastbar ist die Schlussfolgerung?

<a id="sec-7-dependence-bias"></a>
##### 7.5.1 Abhängigkeit und Verzerrung

**1.000 Spots sind nicht 1.000 unabhängige Experimente.** Wiederholte Zyklen teilen Stationsausrüstung und Ausbreitung; nahe Stationen teilen Bedingungen; benachbarte Zeitintervalle hängen zusammen; ein Stör- oder Ionosphärenereignis kann viele Beobachtungen beeinflussen. Auch die beiden Phasen einer erweiterten WSPR-Folge ergänzen Beobachtungen innerhalb eines Laufs, keine unabhängigen experimentellen Wiederholungen.

Stationsgleichgewichtung verringert die Dominanz besonders meldestarker Stationen; Mediane verringern den Einfluss einzelner Extremwerte. Beides beseitigt weder systematische Kalibrierfehler, Meldeunterschiede noch Ausbreitungsverzerrungen und erzeugt keine Unabhängigkeit. WSPRadar liefert deskriptive Zusammenfassungen, nicht automatisch Standardfehler, Konfidenzintervalle, p-Werte, Teststärke oder kausale Effekte. Würde jede Meldung als unabhängig behandelt, würde die Unsicherheit über einen künftigen Lauf oder eine breitere Population im Allgemeinen unterschätzt.

<a id="sec-7-repeatability-control"></a>
##### 7.5.2 Wiederholbarkeit und experimentelle Kontrolle

Beurteile die Unterstützung auf mehreren Ebenen: **Tiefe** der Gelegenheiten oder Joint Spots; **Breite** und geografische Vielfalt der Stationsidentitäten; **interne Konsistenz** über Gewichtung, Geografie und Zeit hinweg; **Wiederholbarkeit** in einem neuen kontrollierten Lauf; und **experimentelle Kontrolle**, etwa Kalibrierung, Kreuztausch, vertauschter Zeitplan oder unabhängige Messung. Übereinstimmung zwischen Ansichten derselben Beobachtungen ist interne Konsistenz, keine Replikation. [Kapitel 8](#sec-8) erklärt, wie daraus abgeleitete Aussagen zu begrenzen sind.

<a id="sec-7-validation"></a>
##### 7.5.3 Validierungsumfang

Auch Software-Validierungskennzahlen benötigen Kontext: Nenne Datensatz, Datum, WSPRadar-Version oder Quellrevision und Berechnungsmethode. Eine datierte Prüfung ist Evidenz für diesen Test, keine zeitlose Garantie für jede Station oder jeden Datensatz.

<a id="sec-7-outliers"></a>
<a id="sec-7-11"></a>
#### 7.6 Experimentelle ΔSNR-Ereignisanalyse

**Dieser experimentelle, optionale Detektor erkennt vorübergehende Abweichungen vom üblichen lokalen ΔSNR eines Funkwegs.** Er dient der fachkundigen Diagnose und ist kein notwendiger Analyseschritt. [Abschnitt 2.5](#sec-outlier) erklärt den Einsatz, [Abschnitt 4.6](#sec-5-6) nennt die Bedienelemente. Diese Übersicht erklärt die wissenschaftliche Interpretation und die wesentlichen Prüfungen, nicht jede algorithmische Verfeinerung.

<a id="sec-7-outlier-departure"></a>
##### 7.6.1 Abweichung von der lokalen Basislinie

Nur native Joint Spots liefern Detektor-ΔSNR, getrennt für jede exakte entfernte Identität aus Rufzeichen und Locator. Nativ bedeutet nach Zuordnung, Zusammenfassung und wissenschaftlicher Filterung. Die Erkennung verwendet die tatsächlichen Zykluszeiten vor der Darstellungsaggregation; andere Intervalle der Zeitlichen Evidenz können Ereignisse nicht verändern. Ist die Meldung ausgeschaltet, läuft der Detektor nicht.

**Ein positives ΔSNR kann eine negative Abweichung sein.** Bei einer lokalen Basislinie von **+8 dB** hat ein Joint Spot mit **+1 dB** die Abweichung `+1 - (+8) = -7 dB`. Das Target bleibt stärker, sein Vorteil liegt aber 7 dB unter der lokalen Basislinie. Die Änderung kann vom Target, von der Referenz oder von beiden stammen. Die Gruppierung folgt dem Vorzeichen der Abweichung, nicht dem Vorzeichen von ΔSNR gegenüber null.

<a id="sec-7-outlier-baseline"></a>
##### 7.6.2 Basislinie und lokale Streuung

Die Basislinie verwendet Mediane besetzter, **an UTC ausgerichteter 10-Minuten-Zellen** bis zu **sechs Stunden vor und nach** einem Kandidaten. Der Kandidat und ein umgebender Schutzabstand bleiben ausgeschlossen. Jede Flanke benötigt **mindestens vier besetzte Zellen**. Das erwartete lokale ΔSNR ist der Mittelwert der beiden Flankenmediane; beide Seiten erhalten gleiches Gewicht. Fehlende Zellen werden nicht aufgefüllt. Reicht die Unterstützung auf einer Seite nicht aus, bleibt der Kandidat unklassifiziert.

Die lokale Streuung wird aus den zusammengeführten Zellabweichungen bestimmt, nachdem jede Flanke auf ihren eigenen Median zentriert wurde. Das robuste Streuungsmaß verwendet deren **mediane absolute Abweichung (MAD)**; ist sie null, die Hälfte des IQR; nur wenn beide null sind, **0.5 dB**. Dieser Ersatzwert ist kein allgemeiner Mindestwert. Der dimensionslose robuste z-Wert ist `0.6745 × Abweichung / robustes Streuungsmaß`: Bei `1 dB` Streuungsmaß ergibt das Beispiel etwa **-4.72**. Das beschreibt eine relative Abweichung, keine Wahrscheinlichkeit oder statistische Signifikanz.

<a id="sec-7-outlier-qualification"></a>
##### 7.6.3 Qualifikation eines Kandidaten

Nahe gleichgerichtete Abweichungen bilden vorläufige Kandidaten unter Berücksichtigung des beobachteten Betriebsrhythmus des Funkwegs. Für die endgültige Qualifikation wird die Basislinie unter Ausschluss des vollständigen Kandidaten bestimmt. Alle vier Prüfungen müssen gemeinsam bestanden werden:

| Erforderliche Prüfung | Bedingung |
|---|---|
| **Absolute Abweichung** | Der Betrag des Ereignismedians erreicht **Minimale absolute ΔSNR-Abweichung (dB)** unter Berücksichtigung von `0.01 dB` Toleranz. |
| **Relative Abweichung** | Sein absoluter robuster z-Wert erreicht **Minimaler robuster z-Wert**, ohne Toleranz. |
| **Baseline-Übereinstimmung** | Die Mediane davor und danach unterscheiden sich um höchstens **Maximaler Unterschied zwischen Baseline davor/danach (dB)** plus `0.01 dB`. |
| **Vorzeichenübereinstimmung** | Mindestens **zwei Drittel aller beibehaltenen nativen Beobachtungen**, einschließlich einer etwaigen neutralen Brücke, haben das Vorzeichen der medianen Abweichung. |

Die Baseline-Übereinstimmung betrifft ähnliche Flankenmediane, keine zusätzliche Forderung nach geringer Streuung. Die dB-Toleranz verändert Vergleiche, nicht gespeicherte Beobachtungen oder Kennzahlen. Eine längere Dauer senkt keine Schwelle; ein großer Einzelwert ersetzt nicht die Prüfungen des Ereignismedians.

<a id="sec-7-outlier-boundaries"></a>
##### 7.6.4 Grenzen und Ereignisklassen

Gemeldete Grenzen müssen gleichgerichtete Beobachtungen sein, die beide Abweichungsschwellen einzeln bestehen. Das Intervall wird auf diese starken Anker begrenzt und erneut gegen die Anforderungen auf Ereignisebene geprüft. Schwächere innere Beobachtungen können verbleiben. Ein nachträglich qualifizierter starker Kern behält Basislinie, Streuungsmaß und Unterstützung des vollständigen Kandidaten; er darf keine günstigere Basislinie wählen. Ohne qualifizierendes Ankerintervall wird kein Ereignis gemeldet.

Ein **Spot-Impuls** enthält einen Joint Spot. Eine **Anhaltende Auslenkung** enthält mindestens drei über mindestens 30 Minuten. Jedes andere Ereignis mit mehreren Spots ist ein **Kurzer Ausbruch**. Alle Klassen bestehen dieselben Prüfungen. Die Spanne vom ersten bis zum letzten Punkt beschreibt beobachtete Evidenz, kein ununterbrochenes Verhalten zwischen den Beobachtungen.

<a id="sec-7-outlier-context"></a>
##### 7.6.5 Kontext und Grenzen

Jeder Funkweg wird getrennt auf Qualifikation geprüft. Die Gruppierung naher gleichgerichteter Ereignisse über mehrere Funkwege liefert Prüfungskontext: Funkwegspezifisch, Richtungskohärent, Bereichsweit oder Mehrere Funkwege. Sie erhöht weder Signifikanz noch Qualifikation.

Die Zerlegung in Target und Referenz sowie nahe einseitige Outcomes helfen bei der Untersuchung; sie können einen Kandidaten weder qualifizieren noch verlängern oder stärken. Der deterministische deskriptive Detektor nimmt keine Signifikanzkorrektur für mehrere Ereignisse vor und macht aus Ereigniszahlen keine unabhängigen Stichproben. Die Zuordnung zu einer Ursache erfordert weiterhin die Kontrollen aus [Kapitel 2](#sec-3), [Kapitel 3](#sec-4) und [Kapitel 8](#sec-8).

<a id="sec-8"></a>
### 8. Evidenzgerechte Aussagen und Reproduzierbarkeit

Beginne mit der Beobachtung und gib dann an, wie weit sie eine Erklärung stützt. WSPRadar beschreibt beibehaltene Meldungen und die daraus gebildeten Vergleiche. Ein Bericht sollte die einbezogenen Stationen und Zyklen, Zusammenfassungsgröße und Gewichtung, Evidenzanzahlen, Versuchsdesign und die weiterhin unbekannten oder unkontrollierten Variablen nennen.

<a id="sec-8-1"></a>
#### 8.1 Aussageklassen und evidenzgerechte Formulierungen

| Aussageklasse | Zu prüfende Aussage | Benötigte Evidenz und Grenze |
|---|---|---|
| **Deskriptiv** | Reichweite, Dekodierrate, erfolgreiches SNR, ΔSNR, Decode Outcomes und wo sie in der ausgewählten Evidenz auftraten. | Population, Gewichtung, Bereich und Unterstützung angeben. |
| **Vergleichend** | Unterschied Target gegenüber Referenz unter dem gewählten Benchmark-Design. | Angeben, was die Referenz darstellt und welche Joint Spots das ΔSNR-Ergebnis stützen. |
| **Bauteilzuordnung** | Ein mit einem lokalen Pfad oder Bauteil verbundener Unterschied. | Kontrollierter Aufbau, Kalibrierung und möglichst Kreuztausch beziehungsweise Rollentausch. |
| **Kausal** | Die geprüfte Änderung verursachte den beobachteten Effekt. | Ein Design, das plausible Alternativerklärungen kontrolliert; WSPRadar-Zusammenfassungen allein reichen nicht aus. |
| **Inferenzstatistisch** | Konfidenz, Signifikanz oder ein auf eine Population verallgemeinerbarer Effekt. | Ein begründetes Abhängigkeitsmodell und eine inferenzstatistische Analyse, die WSPRadar derzeit nicht liefert. |

Verwende den Ergebnistyp, der zur Aussage passt:

* **Performance** stützt das konditionale Verhalten des Targets innerhalb bestätigter Gelegenheiten und seine Mindestens-einmal-Reichweite während des ausgewählten Zeitfensters.
* **Benchmark-ΔSNR** beschreibt Target-SNR minus Referenz-SNR für die beibehaltenen Joint Spots; es beschreibt keine nur einseitig decodierten Signale.
* **Decode Outcomes** stützen Aussagen über Paarbarkeit und einseitige Evidenz.
* **Entfernungs- oder Richtungsstruktur** stützt Aussagen über beobachtete Funkwegsegmente und nicht über einen direkten Abstrahlwinkel oder ein Gewinnmuster.
* **Referenznachbarschaft** stützt Beschreibungen, wie die vollständige Target-Station unter den ausgewählten Bedingungen gegenüber den beitragenden Peers in der Umgebung abschnitt. Die Referenz ändert sich mit den qualifizierenden Beobachtungen, dem Radius, dem entfernten Funkweg und dem Zyklus. Sie ist weder eine dauerhafte Stationsrangliste noch ein kalibrierter Antennenvergleich.

Ein positives oder negatives ΔSNR beziffert den nach dieser Konstruktion beobachteten SNR-Unterschied innerhalb der Joint Spots. Es bestimmt nicht, welches Bauteil oder welcher Umgebungsunterschied ihn verursacht hat. Der Joint-Evidenzanteil beschreibt Paarbarkeit oder Abdeckung der beibehaltenen Evidenz; er ist keine Gewinnrate des Targets.

Berichte Richtung, Band, UTC-Zeitfenster, Nachbarschaftsradius, geografischen Bereich, angewandte Korrektur und stützende Evidenz. Unterscheide Konsistenz innerhalb eines Laufs von der Reproduktion in einem getrennten, geeignet kontrollierten Lauf.

| Vermeiden | Evidenzgerechte Formulierung |
|---|---|
| „Antenne A hat 3 dBi mehr Gewinn.“ | „Pfad A ergab gegenüber B ein stationsgleichgewichtetes medianes ΔSNR von +3,0 dB innerhalb der Joint Spots in diesem Band, Zeitfenster und Segment.“ |
| „Die Empfindlichkeit meines Empfängers beträgt 72 %.“ | „Die qualifizierenden entfernten Stationen hatten am Target-Empfänger eine mittlere individuelle Dekodierrate von 72 %, auf Grundlage bestätigter Gelegenheiten mit Target-Decodes oder externen Aktivitätsnachweisen.“ |
| „Performance sollte nahe 100 % liegen.“ | „Die Dekodierrate ist durch bestätigte Gelegenheiten bedingt; 100 % ist kein zu erwartender Ausgangswert.“ |
| „A ist statistisch signifikant besser.“ | „Das deskriptive mediane ΔSNR sprach innerhalb der ausgewählten Joint Spots für A; ein Signifikanztest wurde nicht durchgeführt.“ |
| „Die Antenne hat einen flacheren Abstrahlwinkel.“ | „Der beobachtete Vorteil konzentrierte sich auf die angegebenen größeren Entfernungssegmente; der Abstrahlwinkel wurde nicht gemessen.“ |
| „A ist effizienter, weil es mehr exklusive Decodes hatte.“ | „A erzeugte unter den dokumentierten Leistungs-, Zeitplan- und Netzwerkbedingungen mehr einseitige Decode-Evidenz; der Wirkungsgrad wurde nicht isoliert.“ |
| „Der lokale Median ist die durchschnittliche lokale Station.“ | „Die Referenz war der Zyklus-/Funkwegmedian aus je einem Beitrag jeder aktiven lokalen Identität aus Rufzeichen plus Locator.“ |
| „Meine Antenne ist X dB besser als benachbarte Antennen.“ | „Für das angegebene Band, Zeitfenster, den Radius und Bereich betrug das stationsgleichgewichtete mediane ΔSNR meiner vollständigen Station X dB relativ zur beobachteten lokalen Nachbarschaftsreferenz. Dies beschreibt die beibehaltene Joint-Evidenz und isoliert keinen Antennengewinn.“ |

<a id="sec-8-2"></a>
#### 8.2 Interpretationsgrenzen

WSPRadar misst nicht direkt:

* Antennengewinn in dBi oder Strahlungswirkungsgrad;
* Abstrahlwinkel oder Ausbreitungsart;
* kalibrierte Empfängerempfindlichkeit oder absolute Feldstärke;
* jeden Sendeversuch oder ein vollständiges Fehlerprotokoll;
* unabhängige Stichprobengröße, Konfidenzintervalle oder statistische Signifikanz; oder
* Kausalität.

Wichtige Daten- und Designgrenzen sind:

* von Nutzern gemeldete Rufzeichen, Locator und Leistungen können falsch sein;
* Datenbanken enthalten erfolgreiche Decodes und keine vollständigen Versuchsprotokolle;
* Performance ist auf beobachtbare Gelegenheiten konditioniert;
* nur Zyklen mit beobachteter Target-Aktivität qualifizieren; Target und Referenz werden damit nicht symmetrisch behandelt;
* erfolgreiches Target-SNR enthält nur decodierte Signale; für fehlende Decodes gibt es keinen gemessenen SNR-Wert;
* Benchmark-ΔSNR verwendet nur Joint Spots mit nutzbarem SNR auf beiden Seiten;
* einseitige Evidenz besitzt kein SNR der fehlenden Seite;
* simultanes TX behält Unterschiede zwischen den Ketten bei Leistung, Frequenzgang, Entkopplung und Kopplung bei;
* Stationshardware, Software, Gelände, lokaler Störpegel, Polarisation und Ausbreitung bleiben gekoppelt, sofern der Versuch sie nicht kontrolliert;
* wiederholte Beobachtungen teilen Stationen, Zeiträume, Geografie und Ausbreitungsbedingungen; die Zeilenzahl ist keine unabhängige Stichprobengröße; und
* Upstream-Datensätze und Verfügbarkeit können sich nach dem ursprünglichen Lauf verändern.

Diese Grenzen definieren, was die Zusammenfassungen beschreiben; sie machen die Beobachtungen nicht wertlos. Breite, innerhalb eines Laufs konsistente und experimentell wiederholbare Evidenz kann betrieblich überzeugend sein und dennoch deskriptiv bleiben.

<a id="sec-8-3"></a>
#### 8.3 Checkliste für Berichterstattung und Reproduzierbarkeit

Bewahre für ein Ergebnis, das du vergleichen, veröffentlichen oder für eine Stationsänderung nutzen möchtest, die folgenden drei Ebenen auf. Der Export sichert einen großen Teil der Analysedefinition und verarbeiteten Evidenz; für den physischen Versuch sind externe Notizen erforderlich. Nenne neben den Analyseeinstellungen auch die Datenbankquelle.

**1. Analysedefinition**

* WSPRadar-Anwendungsversion und, soweit verfügbar, Quellrevision;
* Datenbankquelle und ursprüngliches Exportdatum;
* RX-/TX-Richtung, Ergebnistyp und Benchmark-Design;
* exakte Target- und Referenzidentitäten und Locator;
* Band und wirksame UTC-Grenzen;
* geografischer Bereich, Sonnenstand, Ausschlüsse und Evidenzschwellen;
* Zweck der Referenzkorrektur, vorzeichenbehafteter Wert und Kalibriergrundlage;
* primärer vorab festgelegter Auswertungsbereich und alle Sensitivitätsanalysen; und
* ob der Lauf explorativ oder bestätigend war.

Trägt ein Delta-SNR-Ausreißerkandidat zur Schlussfolgerung bei, dokumentiere zusätzlich, dass die Berichterstattung aktiviert war, die drei Detektorschwellen, die Detektorversion, den exakten Funkweg, das UTC-Intervall, die deskriptive Ereignisklasse sowie, ob das Ereignis explorativ gefunden oder unter einer vorab festgelegten bestätigenden Konfiguration bewertet wurde.

**2. Evidenz hinter der Schlussfolgerung**

* berichtete Zusammenfassung und Gewichtungsebene;
* qualifizierende Peers und Gelegenheiten bei Performance;
* Joint-Stationen und Joint Spots bei Benchmark;
* stations- und beobachtungsbezogene Zusammenfassungen;
* Joint-Evidenzanteil und relevante einseitige Decode Outcomes;
* geografischer/zeitlicher Bereich sowie jede einflussreiche Identität oder kurze Zeitspanne; und
* Konsistenz innerhalb des Laufs im Unterschied zur Wiederholung in einem getrennten Lauf.

**3. Externe Versuchsaufzeichnung**

* physische Anordnung von Antenne, Speiseleitung und HF-Pfaden;
* Umschalter-/Splittertopologie und Zuordnung von Identitäten zu Pfaden;
* Sender-, Empfänger-, Decoder- und Softwareversionen;
* tatsächliche Sendeleistung und Grundlage der WSPR-Leistungsangabe;
* Kalibriermessungen und Bezugsebene;
* tatsächlicher Zeitplan, Unterbrechungen, Kreuztausch und vertauschte Zuordnungen; und
* Störungen, Fehler, Wetter oder beabsichtigte Änderungen, die für die Interpretation relevant sind.

Bewahre das ursprüngliche Exportpaket als Evidenznachweis dieses Laufs auf. Ein späterer Abruf kann Korrekturen in der Quelldatenbank oder eine neuere WSPRadar-Version widerspiegeln.

<a id="sec-8-4"></a>
#### 8.4 Exportpaket der Analyse

Wähle vor der Exportvorbereitung den geografischen Bereich, die Stationen und ein etwaiges Fokusintervall für deine Schlussfolgerung. `Alle Ergebnisse zum Download vorbereiten` erstellt die ZIP-Datei; `Vorbereitete Ergebnisse herunterladen` speichert sie. Bereite das Paket nach Änderungen dieser Auswahl erneut vor.

Innerhalb der ZIP-Datei steht `config/` zusammen mit entweder `benchmark/` oder `performance/`, entsprechend der gewählten Analyse. Welche Abbildungen enthalten sind, hängt von der verfügbaren Evidenz und der Inspektor-Auswahl ab.

| Artefakt | Inhalt und Verwendung |
|---|---|
| Konfiguration | `wspradar_config.config` stellt die Analyseeinstellungen und unterstützten Ansichtsoptionen für einen weiteren Lauf wieder her, nicht die ursprünglichen Beobachtungen. |
| Metadaten des Laufs | `run_metadata.json` dokumentiert Softwareversion, Datenbank, tatsächliche Datenauswahl, Analyseeinstellungen, Korrekturen und Inspektor-Bereich einschließlich aktivierter Ausreißereinstellungen. Bewahre die Datei mit der Evidenz auf: Die Konfiguration allein kann nicht jede Auswahl rekonstruieren. Fehlen Angaben zur Datenauswahl, bleibt sie unbekannt; das belegt nicht, dass der Standardfilter verwendet wurde. Siehe [Abschnitt 5.4](#sec-6-4). |
| Verarbeitete Evidenz | `analysis_cache.parquet` enthält die nach den wissenschaftlichen Filtern beibehaltene Evidenz für den gesamten geografischen Bereich der abgeschlossenen Analyse. Sie ist weder auf das ausgewählte Segment beschränkt noch ein unveränderter Datenbankdownload. |
| Station-Insights-CSV | `table_station_insights_current_segment.csv` enthält Zusammenfassungen je Peer für den aktiven Bereich des Segment-Inspektors. Qualifizieren keine Zeilen, bleiben die Kopfzeilen erhalten. |
| Drill-Down-CSV-Dateien | Evidenz auf Zeilenebene für ausgewählte Stationen oder alle Stationen im aktiven Segment. Die Tabelle der ausgewählten Stationen kann Fokus und Tabellenfilter berücksichtigen. Beide Dateien behalten bei leerem Ergebnis ihre Kopfzeilen. |
| Ausreißer-CSV-Dateien | `table_delta_snr_outlier_event_paths.csv` fasst qualifizierte Funkwegereignisse zusammen; `table_delta_snr_outlier_paired_evidence.csv` enthält deren chronologische Joint Spots einschließlich des korrigierten Referenz-SNR. Beide beziehen sich auf das aktive Segment und sind über IDs verknüpft, die nur innerhalb dieses Pakets gelten. Meldung ausgeschaltet: Dateien fehlen. Meldung eingeschaltet, aber keine Befunde: nur Kopfzeilen. Es handelt sich um Kandidatenbefunde, nicht um bestätigte physische Ereignisse. |
| Karten-, Segment- und zeitliche Abbildungen | PNGs zur Darstellung des Ergebnisses: Die Karte zeigt die abgeschlossene Analyse; Segment- und zeitliche Abbildungen fassen das aktive Segment zusammen, einschließlich chronologischer und nach UTC-Stunde zusammengefasster Ansichten. |
| Abbildungen ausgewählter Stationen | Evidenz für genau eine ausgewählte Peer-Identität. Bei aktivierter Ausreißermeldung kann Benchmark stattdessen Delta SNR mehrerer ausgewählter Funkwege gemeinsam darstellen. |
| Drill-Down-Fokusabbildungen | Zusätzliche Abbildungen für eine ausgewählte Station und ihr aktives Fokusintervall mit einzelnen Beobachtungen und deren zeitlichem Zusammenhang. Sie ergänzen die Abbildungen der ausgewählten Station über den vollständigen Lauf; Kandidatenhilfslinien beziehen sich auf die fokussierte Episode. |

Bewahre das ursprüngliche Paket als Evidenznachweis des Laufs auf. Messungen am physischen Aufbau und externe Betriebsprotokolle müssen getrennt erhalten bleiben, wie in [Abschnitt 8.3](#sec-8-3) beschrieben. Eine spätere Datenbankabfrage oder ein erneuter Lauf kann andere Datensätze oder Ergebnisse liefern.

<a id="sec-8-5"></a>
#### 8.5 Haftungsausschluss

WSPRadar ist experimentelle Open-Source-Software und wird in der vorliegenden Form („as is“) ohne Gewährleistung bereitgestellt. Quellcode und Methoden können geprüft werden; Genauigkeit, Vollständigkeit, Verfügbarkeit und Eignung werden jedoch nicht garantiert. Triff keine wesentlichen finanziellen oder sicherheitsrelevanten Entscheidungen allein auf Grundlage von WSPRadar.

<a id="sec-ref"></a>
### Literatur und Quellen

* <a id="ref-1"></a><a href="https://arxiv.org/abs/2209.08989">[Ref-1]</a> **Preprint.** Zander, J. (2022). *Simple HF antenna efficiency comparisons using the WSPR system*. arXiv:2209.08989v1. doi:10.48550/arXiv.2209.08989.

* <a id="ref-2"></a><a href="https://doi.org/10.1155/2022/4809313">[Ref-2]</a> **Begutachteter Fachartikel.** Vanhamel, J.; Machiels, W.; Lamy, H. (2022). *Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band*. International Journal of Antennas and Propagation, 2022, 4809313. doi:10.1155/2022/4809313.

* <a id="ref-3"></a><a href="https://sivantoledotech.wordpress.com/2010/09/24/failure-to-use-wspr-to-compare-antennas/">[Ref-3]</a> **Technischer Erfahrungsbericht eines Funkamateurs.** Toledo, S. / 4X6IZ (2010). *Failure to Use WSPR to Compare Antennas*.

* <a id="ref-4"></a><a href="https://www.qsl.net/kp4md/wspr.htm">[Ref-4]</a> **Amateurfunk-Fachartikel und Clubvortrag.** Milazzo, C. F. / KP4MD (2011). *Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*.

* <a id="ref-5"></a><a href="https://www.researchgate.net/publication/319903566_Improving_HF_Band_SNR_from_analysis_of_WSPR_spots">[Ref-5]</a> **Amateurfunk-Zeitschriftenartikel.** Griffiths, G.; Squibb, N. J. (2017). *Improving HF Band SNR from analysis of WSPR spots*. Practical Wireless, October 2017, 23-26. <a href="https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf">Vom Autor bereitgestellte Fassung</a>.

* <a id="ref-6"></a><a href="https://www.arrl.org/files/file/History/History%20of%20QST%20Volume%201%20-%20Technology/QS11-2010-Taylor.pdf">[Ref-6]</a> Taylor, J. H.; Walker, B. (2010). *WSPRing Around the World*. QST, 94(11), 30-32.

* <a id="ref-7"></a><a href="https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2023.1184171/full">[Ref-7]</a> **Begutachteter Übersichtsartikel.** Frissell, N. A. et al. (2023). *Heliophysics and amateur radio: citizen science collaborations for atmospheric, ionospheric, and space physics research and operations*. Frontiers in Astronomy and Space Sciences, 10, 1184171. doi:10.3389/fspas.2023.1184171.

* <a id="ref-8"></a><a href="https://www.arrl.org/wspr">[Ref-8]</a> **Offizieller technischer Überblick.** ARRL, *WSPR*: Nachrichtenformat, Codierung, Dauer, Zeitsteuerung, belegte Bandbreite und SNR-Bezugsgröße. Abgerufen am 2026-07-12.

* <a id="ref-9"></a><a href="https://www.mdpi.com/2073-4433/13/8/1340">[Ref-9]</a> **Begutachteter Fachartikel.** Lo, S.; Rankov, N.; Mitchell, C.; Witvliet, B. A.; Jayawardena, T. P.; Bust, G.; Liles, W.; Griffiths, G. (2022). *A Systematic Study of 7 MHz Greyline Propagation Using Amateur Radio Beacon Signals*. Atmosphere, 13(8), 1340. doi:10.3390/atmos13081340.

* <a id="ref-10"></a><a href="https://wspr.live/">[Ref-10]</a> **Offizielle Dokumentation des Datendienstes.** WSPR.live, *Welcome to WSPR Live*: Datenbankzugriff, Schema, Zuordnung der Mode-Codes, Hinweise zu Rohdaten und Verfügbarkeit sowie Verhalten bei Datenaktualisierungen. Abgerufen am 2026-08-06. Öffentlicher ClickHouse-SQL-Zugriff, Dashboards, Exporte und Würdigung der von HB9VQQ bereitgestellten Rechenressourcen. Abgerufen am 2026-10-06.

* <a id="ref-11"></a><a href="https://www.wsprdaemon.org/">[Ref-11]</a> **Offizielle Projektwebsite.** WSPRDaemon, *WSPR Daemon*: mehrkanalige Spot-Erfassung, Decodierung und Reporting von WSPR/FST4W, Rauschschätzung, Datenbank-/Grafana-Ausgabe sowie Datendienste für Drittanwendungen. Abgerufen am 2026-08-06. **Offizielle Betriebsdokumentation.** WsprDaemon, <a href="https://wsprdaemon.readthedocs.io/en/master/FAQ.html#how-does-spot-merging-work-with-multiple-receivers">*FAQ: How does spot merging work with multiple receivers?*</a>: Meldung des besten SNR an WSPRnet beim Zusammenführen von Empfängermeldungen. Abgerufen am 2026-09-24. Ergänzende Projektdokumentation: <a href="https://wsprdaemon.readthedocs.io/en/master/results/wspr.html">*WSPR*</a>, <a href="https://www.wsprdaemon.org/grafana">*Grafana*</a> und <a href="https://wsprdaemon.readthedocs.io/en/master/description/how_it_works.html">*How it works*</a>: Datenbankzugriff, Würdigung der Beiträge zu ClickHouse-Entwicklung und Hosting sowie Erfassung, Meldungsübermittlung, Rausch- und Dopplermessungen. Abgerufen am 2026-10-06.

* <a id="ref-12"></a><a href="https://wsjt.sourceforge.io/wsjtx-main_en.html">[Ref-12]</a> **Offizielle Betriebsdokumentation.** WSJT-X 3.0.1 User Guide: WSPR-Nachrichtenformate Typ 1, Typ 2 und Typ 3; zufällige Zeitplanung über `Tx Pct`; Dateitrennung unter Windows mit `--rig-name`; Audioeinstellungen und Dateispeicherorte. QRP Labs, <a href="https://qrp-labs.com/qmx">*QMX firmware history and manuals*</a> und <a href="https://www.qrp-labs.com/images/qmx/manuals/operation_1_04_004.pdf">*QMX Operating Manual, firmware 1_04_004*</a> und <a href="https://qrp-labs.com/images/qmx/manuals/VirtualU3S_1_04_008a.pdf">*Virtual U3S Manual, firmware 1_04_008a*</a>: modellspezifische Firmware sowie Betrieb und Zeitplanung mit Virtual U3S; <a href="https://www.qrp-labs.com/images/ultimate3s/operation3.12a2.pdf">*Ultimate3S Operating Manual, firmware v3.12a2*</a>: WSPR-Frequenzbereich, globales Frame-/Start-Verhalten, erweitertes WSPR, sequenzielle Mode-Einträge und `Aux`-Werte je Eintrag; <a href="https://qrp-labs.com/images/appnotes/AN003_A4.pdf">*AN003: Ultimate3/3S relay-switched filters*</a>: gefilterte Relais-/Treiberansteuerung und Schaltintervalle ohne HF. Abgerufen am 2026-10-03.

* <a id="ref-13"></a><a href="https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018SW002008">[Ref-13]</a> **Begutachteter Fachartikel.** Frissell, N. A. et al. (2019). *High-Frequency Communications Response to Solar Activity in September 2017 as Observed by Amateur Radio Networks*. Space Weather, 17(1), 118–132. doi:10.1029/2018SW002008.

* <a id="ref-14"></a><a href="https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2022GL097879">[Ref-14]</a> **Begutachteter Fachartikel.** Frissell, N. A. et al. (2022). *First Observations of Large Scale Traveling Ionospheric Disturbances Using Automated Amateur Radio Receiving Networks*. Geophysical Research Letters, 49(5), e2022GL097879. doi:10.1029/2022GL097879.

* <a id="ref-15"></a><a href="https://www.researchgate.net/publication/334612025_Estimating_LF-HF_band_noise_while_acquiring_WSPR_spots">[Ref-15]</a> **Technischer Bericht.** Griffiths, G.; Robinett, R.; Elmore, G. (2019). *Estimating LF–HF band noise while acquiring Weak Signal Propagation Reporter (WSPR) spots*. Version 12, März–November 2019.

* <a id="ref-16"></a><a href="https://www.arrl.org/files/file/QEX_Next_Issue/SeptOct2020/TOFC.pdf">[Ref-16]</a> **Amateurfunk-Fachartikel; Inhaltsverzeichnis der Ausgabe.** Griffiths, G.; Robinett, R.; Elmore, G. (2020). *Estimating LF-HF Band Noise While Acquiring WSPR Spots*. QEX, September/Oktober 2020, ab S. 25.

* <a id="ref-17"></a><a href="https://f6irf.blogspot.com/2008/04/">[Ref-17]</a> **Technische Erfahrungsberichte eines Funkamateurs.** Destrem, P. / F6IRF (2008). *A statiscal method to evaluate TX antenna performance using WSPR* (24. April), anschließende TX-Auswertung, RX-Vergleich auf 160 m und Stationsvergleiche (April 2008).

* <a id="ref-18"></a><a href="https://www.charlespreston.net/antenna/WSPR-Antenna-Prop-Exp-PR.pdf">[Ref-18]</a> **Vorläufiger technischer Bericht.** Preston, C. / KL7OA (später K7TAA) (2009). *WSPR Antenna and Propagation Experiment: Preliminary Results*. Version 1.0, 31. März 2009; die verfügbare Fassung enthält eine Aktualisierung vom 25. Juni 2017.

* <a id="ref-19"></a><a href="https://www.arrl.org/files/file/QEX_Next_Issue/July-August2017/TOFC.pdf">[Ref-19]</a> **Amateurfunk-Fachartikel; Inhaltsverzeichnis der Ausgabe.** Preston, C. / K7TAA (2017). *Antenna Comparisons Using Simultaneous WSPR Measurements*. QEX, Juli/August 2017, 8–14.

* <a id="ref-20"></a><a href="https://www.darc.de/fileadmin/filemounts/distrikte/g/2026/Talk_in_G/Talk-G_Antennenvergleich_synchr_WSPR_T.Rietdorf_DL2OAH_V2.1_17012025.pdf">[Ref-20]</a> **Technischer Amateurfunkvortrag.** Rietdorf, T. / DL2OAH (2026). *Antennenvergleich mit synchronen WSPR-Daten*. DARC OV R10, 2. Talk in G, TH Köln, 17. Januar 2026, Version 2.1; Messungen vom Januar 2025.

* <a id="ref-21"></a><a href="https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf">[Ref-21]</a> **Konferenzbeitrag.** Griffiths, G.; Robinett, R. (2020). *Aids to the Presentation and Analysis of WSPR Spots: TimescaleDB database and Grafana*. ARRL/TAPR Digital Communications Conference 2020.

* <a id="ref-22"></a><a href="https://wspr.rocks/help.html">[Ref-22]</a> **Werkzeugdokumentation.** WSPR.Rocks, *Help &amp; Documentation*: SpotQ, SQL-Zugriff, Duplikatanalyse, Karten, Diagramme und Heatmaps. <a href="https://wspr.rocks/head2head/">*Head2Head*</a>: Vergleiche von Empfängern, Sendern und Softwareversionen; die Hilfe beschreibt auch die Untersuchung von Empfangsdurchlassbereichen.

* <a id="ref-23"></a><a href="https://www.sotabeams.co.uk/wsprlite-classic">[Ref-23]</a> **Produktdokumentation.** SOTABEAMS, *WSPRlite Classic / DXplorer*: WSPR-basierte Analyse der Antennenleistung und DX10-Metrik.

* <a id="ref-24"></a><a href="https://www.sotabeams.co.uk/blog/indoor-hf-antennas-does-it-make-much-difference/">[Ref-24]</a> **Amateurfunkversuch und Produktanwendung.** Newstead, R. / SOTABEAMS (2017). *Indoor HF antennas - does it make much difference?*. 5. Mai 2017.

* <a id="ref-25"></a><a href="https://sites.google.com/myuba.be/wspr-station-compare/home">[Ref-25]</a> **Projektdokumentation.** WSPR-Station-Compare, Projektseite mit Verweisen auf Vanhamel et al. und Zander. Machiels, W. / ON4AWM, <a href="https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-station-compare-app">*WSPR Station Compare App*</a>: RX-Vergleich, Empfängerversatzkorrektur, Mindestzahl von Beobachtungen, Rufzeichenfilter und Azimutauswahl.

* <a id="ref-26"></a><a href="https://wspr.bsdworld.org/">[Ref-26]</a> **Werkzeugdokumentation.** Antenna Performance Analysis Tool, WSPR-basierter Generator für Antennenberichte.

* <a id="ref-27"></a><a href="https://www.gm4eau.com/home-page/wspr/">[Ref-27]</a> **Werkzeugdokumentation.** GM4EAU, *WATT WSPR Analysis Tool*: Berichte, Karten, Filter und Zeitachsenanimation in Excel/VBA.

* <a id="ref-28"></a><a href="https://qrp-labs.com/qmxp/wsprcorruption.html">[Ref-28]</a> **Technische Untersuchung des Herstellers.** QRP Labs, *WSPR Type 3 callsign corruption*: beobachtete Hash-Kollisionen oder Fehlzuordnungen zusammengesetzter Rufzeichen in großen WSPR-Datensätzen und ihr Mechanismus. Abgerufen am 2026-08-25.

* <a id="ref-29"></a><a href="https://github.com/HarrydeBug/WSPR-transmitters/blob/1657468ea27052167191a7deda2440a535567ecd/Standard%20Firmware/Release/Hardware_Version_2_ESP8285/WSPR-TX2.19/WSPR-TX2.19.ino">[Ref-29]</a> **Veröffentlichter Firmware-Quellcode, unveränderliche Revision.** ZachTek WSPR-TX-Firmware `2.19` für ESP8285-Hardware: Frequenzauswahl in `DoWSPR()`, Frequenzeinheit Hundertstel Hertz, Produktmodellauswahl und Build-Voraussetzungen. Revision `1657468ea27052167191a7deda2440a535567ecd`. Abgerufen am 2026-08-25.

<div style="page-break-before: always;"></div>

<a id="part-iv"></a>
## Teil IV: Praktische Ergänzungen

Dieser Teil bündelt die Einrichtung paralleler WSJT-X-Instanzen für simultane Empfangspfade, die Grenze von WSJT-X bei sparsamen synchronen Sendetests, praktische Verfahren für einen simultanen TX-Referenzaufbau, die Kalibrierung der Referenzseite und die Projektlizenz. Verwende die Abschnitte, die für deine Station und deinen Versuch relevant sind.

<a id="sec-a"></a>
### Anhang A: Parallele WSJT-X-Instanzen für simultanes RX

Mit diesem Verfahren wird unter Windows eine zweite isolierte WSJT-X-Instanz für einen simultanen RX-Vergleich im kontrollierten Aufbau eingerichtet. Das aktuelle WSJT-X-Handbuch nennt `--rig-name` als unterstützten Weg, die Einstellungen und beschreibbaren Dateien jeder Instanz zu trennen. Da sich WSJT-X-Versionen und Installationspfade ändern können, sollte bei abweichenden Menüs das aktuelle Handbuch geprüft werden. Parallele WSJT-X-Instanzen lösen dagegen nicht die Zeitplanung eines sparsamen simultanen TX-Hardware-A/B-Laufs; diese Grenze beschreibt [Abschnitt A.4](#sec-a-4). <a href="#ref-12">[Ref-12]</a>

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
5. **File > Settings > General** öffnen und dort exakt das Referenz-Rufzeichen und den Referenz-Locator eintragen, die für Meldungen verwendet werden.
6. Zum WSPR-Hauptfenster zurückkehren, das vorgesehene Band und den Audiopegel prüfen, bei Bedarf den Spot-Upload aktivieren und kontrollieren, dass hochgeladene Zeilen die Referenzidentität verwenden.
7. Die Zeitsynchronisation beider Instanzen prüfen.

Getrennte Verzeichnisse belegen noch keine Unabhängigkeit der HF-Pfade. Prüfe praktisch, ob beide Datenströme tatsächlich die vorgesehene Hardware verwenden.

<a id="sec-a-4"></a>
#### A.4 Grenzen von WSJT-X für simultanes TX

Parallele, voneinander getrennte WSJT-X-Instanzen sind für simultanes RX nützlich. Der normale WSPR-Sendebetrieb liefert jedoch keinen sparsamen deterministischen Zeitplan für A/B-Aussendungen im selben Zyklus. WSJT-X wählt die aktivierten zweiminütigen Sendeperioden entsprechend `Tx Pct` zufällig. Bei jedem Wert unter `100%` bleiben die beiden Instanzen deshalb unsynchronisiert; `Tx Pct = 100%` wäre erforderlich, damit beide in jedem Zyklus zu senden versuchen <a href="#ref-12">[Ref-12]</a>.

Diese Einstellung wird für den Versuch nicht empfohlen. Eine WSPR-2-Aussendung belegt etwa 110,6 Sekunden eines 120-Sekunden-Zyklus; der Betrieb in jedem Zyklus nähert sich daher einer HF-Einschaltdauer von 92 % und belegt das WSPR-Unterband in jedem Slot. Als praktische Betriebsempfehlung und nicht als Protokollregel empfiehlt WSPRadar, nur etwa `5–20%` der verfügbaren Zyklen auszuwählen; auf stark belegten Bändern oder bei längeren Versuchen ist das untere Ende vorzuziehen. Bei diesen Prozentsätzen bleibt die WSJT-X-Zeitplanung zufällig statt deterministisch.

Verwende für einen sparsamen synchronen TX-Benchmark stattdessen deterministische Bakenhardware: zwei QMX oder QMX+ mit Virtual U3S, zwei Ultimate3S oder kompatible Virtual-U3S-Implementierungen oder zwei ZachTek-Sender mit geprüfter angepasster Firmware für randomisierte getrennte Frequenzfenster. [Anhang B](#sec-simultaneous-tx-setup) beschreibt die praktische Einrichtung.

<div style="page-break-before: always;"></div>

<a id="sec-simultaneous-tx-setup"></a>
### Anhang B: Simultanes TX Referenzaufbau/-station praktisch einrichten

Dieser Anhang führt Schritt für Schritt durch einen simultanen TX-kontrollierten Aufbau mit zwei lokal kontrollierten Sendepfaden. Er eignet sich für Vergleiche von Antennen, Speiseleitungen, Filtern, Anpassnetzwerken oder vollständigen Sendeketten. Beginne an geeigneten Kunstantennen oder über einen sicher ausgelegten Testpfad mit geringer Leistung und gehe erst nach der vollständigen Vorabprüfung auf Sendung.

<a id="sec-simultaneous-tx-setup-1"></a>
#### B.1 Rufzeichen auswählen

Am einfachsten ist der Aufbau mit zwei verschiedenen regulären Rufzeichen, die jeweils in das normale WSPR-Format mit einer Aussendung passen. Dann enthält jede Aussendung das vollständige Rufzeichen, Grid-4 und die gemeldete Leistung. Das vermeidet die ergänzende Typ-2-/Typ-3-Folge und deren in [Abschnitt 7.2.1](#sec-7-benchmark-outcomes) beschriebene Grenze der Hash-Auflösung.

Alternativ können zwei zusammengesetzte Rufzeichen verwendet werden, die jeweils dieselbe überprüfte Typ-2-/Typ-3-Folge aussenden. Gib bei einem gemeinsamen Basisrufzeichen beiden Sendern unterschiedliche Suffixe, beispielsweise `CALL/1` und `CALL/2`. Prüfe, welche Suffixe in deinem Land für dein Rufzeichen und deinen Betrieb zulässig sind. Verwende einen Rufzeichenzusatz nur, wenn diese Kennung für den Funkbetrieb des Operators und der Station zulässig ist; eine von der Datenbank akzeptierte Schreibweise allein berechtigt nicht zur Verwendung. Richte die Folgen so aus, dass ihre Typ-2-Phasen und ihre Typ-3-Phasen jeweils zusammenfallen.

Kombiniere keine reguläre Folge mit nur einer Aussendung auf einem Pfad mit einer anders geplanten zweizykligen Folge eines zusammengesetzten Rufzeichens auf dem anderen Pfad. Eine zusätzliche oder fehlende Folgenposition kann durch das Versuchsdesign selbst einseitige Evidenz erzeugen. Erfinde keinen Rufzeichenzusatz als bloßes Hardware-Etikett. Dieser Vergleich desselben Zyklus erfordert zwei unterschiedliche gültige exakte Meldeidentitäten. Konfiguriere beide Pfade für dasselbe wahrheitsgemäße physische Test-QTH; prüfe, ob die gemeldeten Standorte beider Identitäten zum tatsächlichen Test-QTH passen.

<a id="sec-simultaneous-tx-setup-2"></a>
#### B.2 Zeitplan angleichen und Signale trennen

1. Synchronisiere beide Sender auf genaue UTC, vorzugsweise über GNSS, und wähle dasselbe Band.
2. Konfiguriere dieselbe deterministische Wiederholung und denselben beobachteten Start in einer geraden Minute. Beide Pfade müssen in denselben Zyklen vollständige WSPR-Nachrichten senden.
3. Wird erweitertes WSPR verwendet, prüfe nach jedem Neustart, dass beide Geräte dieselbe Typ-2-Phase gemeinsam beginnen und anschließend dieselbe Typ-3-Phase gemeinsam beginnen.
4. Platziere bei QMX, Virtual U3S oder Ultimate3S die beiden direkt programmierten HF-Signale nominal `100 Hz` auseinander und halte beide vollständigen Signale mit ausreichendem Rand innerhalb des 200 Hz breiten WSPR-Sendeunterbands. Ein größerer Abstand ist nicht automatisch besser, weil er den Randabstand verringert. Verwende und prüfe bei angepassten ZachTek-Builds mit randomisierten getrennten Frequenzfenstern stattdessen die in [Abschnitt B.5.3](#sec-simultaneous-tx-setup-5-3) beschriebenen unteren und oberen Fenster, ohne einen festen Abstand zu erwarten.

Praktische Festfrequenz-Ausgangspaare für QMX, Virtual U3S und Ultimate3S sind:

| Band | Unteres Signal | Oberes Signal |
|---|---:|---:|
| 40 m | `7.040050 MHz` | `7.040150 MHz` |
| 20 m | `14.097050 MHz` | `14.097150 MHz` |

Dies sind tatsächlich abgestrahlte HF-Frequenzen und nicht die USB-Einstellfrequenz eines Empfängers. Je nach Modell und Firmware kann ein Gerät seine programmierte WSPR-Frequenz als Signalmitte oder als Ton 0 bezeichnen. Folge dem Handbuch der installierten Version, beobachte anschließend beide Sender gemeinsam auf einem Empfänger, Frequenzzähler oder Spektrumsdisplay und prüfe die erwartete Platzierung: den tatsächlichen Abstand von 100 Hz bei einem festen Paar oder die vorgesehenen unteren und oberen Bereiche bei randomisierten getrennten Frequenzfenstern. Wiederhole die Zeit- und Frequenzprüfung nach einem Neustart oder einer Firmwareänderung <a href="#ref-12">[Ref-12]</a>.

<a id="sec-simultaneous-tx-setup-3"></a>
#### B.3 Leistung und simultane Signalqualität prüfen

1. Prüfe jeden Sender einzeln an einer geeigneten Kunstantenne oder über einen sicher gedämpften Messpfad.
2. Miss die tatsächliche HF-Leistung an der für die Fragestellung maßgeblichen Vergleichsebene. Melde den nächstgelegenen gültigen WSPR-kodierten dBm-Wert. WSPRadar empfiehlt für diesen Versuch den praktischen Bereich von `20–30 dBm`; darin stehen die kodierbaren Werte `20`, `23`, `27` und `30 dBm` zur Verfügung. Kennzeichne A und B nicht durch falsche dBm-Werte. `20–30 dBm` entsprechen ungefähr `100 mW–1 W`. Verwende keine unnötig hohe Leistung, sondern nur so viel, wie der Versuch benötigt <a href="#ref-12">[Ref-12]</a>.
3. Betreibe beide Sender gemeinsam an Kunstantennen und prüfe Frequenzen, belegte Bandbreite, Oberwellen, unerwünschte Aussendungen und Intermodulationsprodukte.

Das Ergebnis mit zwei Sendern schließt jeden nicht kontrollierten Unterschied zwischen diesen vollständigen Pfaden ein. Ein sauberes Einzelsignal genügt nicht; geprüft werden muss der gleichzeitige Betrieb.

<a id="sec-simultaneous-tx-setup-4"></a>
#### B.4 WSPRnet und ausgewählte Datenquelle prüfen

Führe mit den endgültigen Einstellungen eine kurze Vorabprüfung durch:

1. Sende mehrere vollständige synchronisierte Folgen.
2. Suche in der [WSPRnet-Spotabfrage](https://www.wsprnet.org/drupal/wsprnet/spotquery) nach jedem exakten Rufzeichen. Verlasse dich nicht nur auf die Karte; sie kann einen zuletzt bekannten Locator anzeigen.
3. Prüfe das vorgesehene Grid-4, die gemeldete Leistung, die Zeitstempel und die getrennten Frequenzen.
4. Suche Zyklen, in denen derselbe entfernte Empfänger beide Rufzeichen gemeldet hat, und prüfe übereinstimmende Zeitstempel.
5. Prüfe bei einer Folge aus zwei Aussendungen anhand des bekannten Zeitplans beide Positionen; die Datenbank kennzeichnet sie nicht zwingend als Typ 2 beziehungsweise Typ 3.
6. Führe eine kurze WSPRadar-Vorabprüfung durch und warte, bis die Testspots dort tatsächlich abfragbar sind. wspr.live beschreibt eine Verzögerung von einigen Minuten; einzelne Uploads oder die Bereitstellung in der Datenbank können länger dauern. Entscheidend ist, dass die Daten tatsächlich vorliegen, nicht eine feste Wartezeit; siehe [Abschnitt 5.6](#sec-6-6).
7. Untersuche nach der Bereitstellung unerwartete Häufungen von Only Target oder Only Reference und vergleiche Joint-Anteil, einseitige Outcomes sowie das ΔSNR der Joint Spots zwischen den beiden Folgenpositionen. Ein beständiger Phasenunterschied kann auf Hash-Auflösung, Frequenzplatzierung, Erwärmung des Senders oder Leistungsabfall hinweisen. Ordne die Folgenpositionen anhand der Zeitstempel und des bekannten Sendezeitplans zu, beispielsweise mit exportierter Evidenz oder einem externen Decoderprotokoll; WSPRadar kennzeichnet keine Nachrichtenphasen und bietet keinen Nachrichtenphasenfilter.

Beginne das eigentliche Messfenster erst, wenn beide exakten Rufzeichen im gemeinsamen Grid-4 beständig erscheinen und gemeinsame Empfänger beide Signale in den vorgesehenen Zyklen melden. Eine erfolgreiche Vorabprüfung gilt nur für die geprüfte Kombination aus Sendern, Firmware, Decodern und Datenquelle.

<a id="sec-simultaneous-tx-setup-5"></a>
#### B.5 Gerätespezifische Einrichtung

Die folgenden Beispiele sind Ausgangsverfahren und kein Ersatz für das Handbuch der installierten Firmware. Wiederhole die vollständige Vorabprüfung von Zeit, Frequenz und Leistung sowie der Datenbankmeldungen nach jeder Firmware- oder Konfigurationsänderung.

<a id="sec-simultaneous-tx-setup-5-1"></a>
<a id="sec-simultaneous-tx-setup-5-2"></a>
##### B.5.1–B.5.2 QMX und QMX+ Virtual U3S sowie Ultimate3S

Der physische Ultimate3S bietet eine Folge aus bis zu 16 programmierbaren Mode-Einträgen mit einer eigenen Frequenz für jeden Eintrag. Virtual U3S für QMX und QMX+ ist als Nachbildung der vollständigen U3S-Architektur beschrieben. Das gemeinsame Zeitplanverfahren gilt für QMX oder QMX+ daher nur, soweit die exakt installierte Virtual-U3S-Version die betreffenden Einträge bereitstellt und sich entsprechend verhält; prüfe dies am Gerät. Die HF-Hardware ist ebenfalls nicht gleich: Unterschiede bei Firmware, Oszillator, Filterung und Endstufe bleiben Teil der verglichenen vollständigen Pfade <a href="#ref-12">[Ref-12]</a>.

1. Installiere beim QMX oder QMX+ die aktuelle, exakt für das jeweilige Modell freigegebene Firmware, und folge deren versionspassender Virtual-U3S-Anleitung. Verwende die erste Version `1_04_000` nicht als allgemeines QMX-Rezept; QRP Labs kennzeichnet sie als QMX+-spezifisch, und spätere Versionen enthalten Korrekturen für Virtual U3S. Bestücke einen physischen Ultimate3S mit dem richtigen Ausgangsfilter für das ausgewählte Band.
2. Trage die beiden exakten Rufzeichen, denselben wahrheitsgemäßen Locator und die gemessene Leistung jedes Geräts als nächstgelegenen gültigen WSPR-kodierten dBm-Wert ein. Reguläre Typ-1-Rufzeichen sind vorzuziehen. Werden zusammengesetzte Rufzeichen verwendet, konfiguriere auf beiden Geräten dieselbe erweiterte WSPR-Folge und prüfe, dass die Typ-2- und Typ-3-Phasen ausgerichtet bleiben.
3. Versorge beide Geräte über GNSS oder eine andere dokumentierte Zeitreferenz mit genauer UTC. Verwende denselben deterministischen globalen `Frame` und denselben beobachteten Start in einer geraden Minute. Deaktiviere nicht benötigte Einträge, damit kein Pfad eine zusätzliche Aussendung einfügt. Beim physischen Ultimate3S hat `Start = 00` die besondere Bedeutung „not used“; prüfe deshalb die angezeigten und beobachteten Starts.
4. Programmiere vollständige HF-Frequenzen nominal 100 Hz auseinander und halte beide vollständigen Signale mit ausreichendem Rand innerhalb des 200-Hz-WSPR-Unterbands. Geeignete Ausgangspaare sind `7.040050 MHz` und `7.040150 MHz` auf 40 m oder `14.097050 MHz` und `14.097150 MHz` auf 20 m. Dies sind tatsächliche HF-Frequenzen und nicht die USB-Einstellfrequenzen eines Empfängers. Beachte die Tonkonvention der installierten Firmware und prüfe die abgestrahlten Signale, statt allein den angezeigten Werten zu vertrauen.
5. Prüfe jedes Gerät einzeln, beide gemeinsam an Kunstantennen und zuletzt mit der vorgesehenen niedrigen Leistung auf Sendung. Schließe die obigen Prüfungen von Leistung, simultaner Signalqualität und Datenbankmeldungen ab, bevor du den Versuch aufzeichnest.

**Verwende einen festen Zeitplan für den Frequenztausch.** Ordne nicht dauerhaft das Target der unteren und die Referenz der oberen Frequenz zu. Schmalbandiges QRM, ein anderes WSPR-Signal, der Frequenzgang eines Empfängers oder ein frequenzabhängiges Senderverhalten könnten dann einen Pfad begünstigen. Programmiere stattdessen komplementäre Eintragsfolgen, sodass die Pfade zwischen aufeinanderfolgenden Beobachtungen desselben Zyklus ihre Frequenzpositionen tauschen, während ihre Rufzeichen weiterhin Target und Referenz identifizieren.

Für reguläre Typ-1-Rufzeichen verwendet ein beim physischen Ultimate3S bestätigter praktischer sparsamer Ausgangszeitplan zwei aktivierte WSPR-Einträge je Gerät, einen gemeinsamen `Frame = 20` und denselben beobachteten Start in einer geraden Minute, zum Beispiel `Start = 04`. Verwende dieses Beispiel bei QMX oder QMX+ nur, wenn die exakt installierte Virtual-U3S-Version dasselbe Verhalten bereitstellt, und bestätige es am Gerät. Programmiere die Target-Einträge in der Reihenfolge unten, dann oben, und die Referenz-Einträge in der Reihenfolge oben, dann unten. Jede Folge aus zwei Einträgen erzeugt zwei unmittelbar aufeinanderfolgende, jeweils zyklusgleiche A/B-Paare und pausiert anschließend bis zum nächsten 20-Minuten-Frame. Jeder Sender verwendet damit zwei von zehn WSPR-Zyklen, also `20%` der verfügbaren Zyklen. Bestätige dieses Verhalten mit der installierten Firmware, bevor du auf Sendung gehst.

| Beobachtung desselben Zyklus | HF-Position Target | HF-Position Referenz |
|---:|---:|---:|
| 1 | unten (`+50 Hz`) | oben (`+150 Hz`) |
| 2 | oben (`+150 Hz`) | unten (`+50 Hz`) |
| 3 | unten (`+50 Hz`) | oben (`+150 Hz`) |
| 4 | oben (`+150 Hz`) | unten (`+50 Hz`) |

`+50 Hz` und `+150 Hz` sind hier Abstände von der unteren Grenze des ausgewählten 200-Hz-WSPR-Unterbands; die exakten vollständigen HF-Werte hängen vom Band ab. Die Paare 1–2 bilden eine Folge aus zwei Einträgen, die Paare 3–4 die nächste. Jede A/B-Beobachtung teilt weiterhin denselben WSPR-Zyklus und dasselbe Ausbreitungsintervall. Die gleichmäßige Nutzung beider Frequenzpositionen balanciert über aufeinanderfolgende Messungen die Empfindlichkeit gegenüber festen Einflüssen der Frequenzposition. Sie verringert diese Störgröße, belegt aber nicht, dass Frequenzeinflüsse beseitigt wurden. Prüfe bei der Vorabprüfung beide Folgenpositionen getrennt. Werden zusammengesetzte Rufzeichen verwendet, übernimm dieses Typ-1-Beispiel nicht ungeprüft: Erstelle und prüfe einen zur installierten Version passenden Zeitplan, der die vollständige Typ-2-/Typ-3-Folge auf beiden Pfaden bewahrt.

<a id="sec-simultaneous-tx-setup-5-3"></a>
##### B.5.3 ZachTek-Firmware 2.19: Zufallswahl in getrennten Frequenzfenstern

Die unveränderte ZachTek-Firmware `2.19` des veröffentlichten ESP8285-Quellcodes wählt bei jeder Auswahl einen neuen zufälligen Versatz von ungefähr `-100 Hz` bis `+99 Hz` um die nominale WSPR-Frequenz. Zwei unveränderte Geräte behalten deshalb keine getrennten A/B-Frequenzbereiche und können gelegentlich nahe beieinander senden. Erstelle für ein kontrolliertes simultanes Paar zwei getrennt beschriftete angepasste Firmware-Builds aus dem Quellcode, der exakt zum jeweiligen Sender passt <a href="#ref-29">[Ref-29]</a>.

Stelle bei beiden ZachTek-Geräten dieselbe nominale Frequenz in der Mitte des ausgewählten 200-Hz-WSPR-Sendeunterbands ein. Die nachfolgenden angepassten Versätze teilen diese gemeinsame Mitte dann in einen unteren und einen oberen Frequenzbereich; nur mit dieser gemeinsamen Mitteneinstellung gelten die beschriebenen Randabstände wie vorgesehen.

In `DoWSPR()` enthält der veröffentlichte Quellcode diese Anweisung zweimal: einmal nach dem ersten `NextFreq()` und erneut nach dem späteren `NextFreq()` des Bandzyklus:

```cpp
freq = freq + (100ULL * random (-100, 100));
```

Ersetze **beide** Vorkommen in der Quellkopie für Sender A durch:

```cpp
freq = freq - (100ULL * random(31, 91));
// zufälliges unteres Fenster: -90 bis -31 Hz
```

Ersetze **beide** Vorkommen in der Quellkopie für Sender B durch:

```cpp
freq = freq + (100ULL * random(30, 90));
// zufälliges oberes Fenster: +30 bis +89 Hz
```

`freq` verwendet Einheiten von `0,01 Hz`. Das untere und das obere Frequenzfenster überschneiden sich deshalb nicht; zwischen ihren programmierten Ton-0-Positionen bleiben mindestens `61 Hz` Abstand, während jeder Sender seine Frequenz weiterhin von einer WSPR-Folge zur nächsten ändert. Die vier nominalen WSPR-Tonfrequenzen überspannen nur etwa `4,4 Hz`, sodass die nächstgelegenen programmierten Tonmitten der beiden Signale selbst an den engsten Fensterpositionen ungefähr `57 Hz` oder weiter auseinander bleiben. Die Endpunkte der Ton-0-Fenster lassen außerdem etwa `10 Hz` Abstand zu jedem äußeren Rand des ungefähr ±100-Hz-Bereichs der unveränderten Zufallsauswahl. Beim oberen Fenster liegt der höchste WSPR-Ton wegen der Tonspanne jedoch nur ungefähr `6,6 Hz` unter dem oberen `+100-Hz`-Rand. Prüfe deshalb die tatsächlichen HF-Signale und ihre Lage im Unterband.

Randomisierte getrennte Frequenzfenster haben gegenüber festen A/B-Frequenzen einen Vorteil: Ein beständiger schmalbandiger Störer oder eine lokale frequenzabhängige Decoderauffälligkeit wirkt mit geringerer Wahrscheinlichkeit auf jede Beobachtung bei exakt derselben Frequenz. Das Design beseitigt jedoch keinen systematischen Einfluss der unteren gegenüber der oberen Empfänger-Durchlasskurve, weil Sender A immer eine Seite und Sender B immer die andere Seite belegt. Vertausche deshalb für eine bestätigende Wiederholung die Frequenzfenster:

```text
Lauf 1: A = unteres zufälliges Frequenzfenster, B = oberes zufälliges Frequenzfenster
Lauf 2: A = oberes zufälliges Frequenzfenster, B = unteres zufälliges Frequenzfenster
```

Ein beobachteter Vorteil, der nach diesem Tausch der physischen Antenne oder dem Sendepfad folgt, ist stärkere Evidenz als ein Vorteil, der dem Frequenzfenster folgt.

Nur ein Vorkommen der Quellcodeanweisung zu ändern reicht nicht aus, weil ein späterer Bandzyklus zur unveränderten Zufallsplatzierung zurückkehren könnte. Eine nachfolgende Typ-3-Aussendung verwendet **dieselbe gewählte Frequenz** wie ihr vorausgehender Typ-2-Partner; erst für das nächste Band oder die nächste Folge wählt die Firmware eine neue zufällige Position im Frequenzfenster. Dies ist eine Quellcodeänderung und keine Option im ZachTek-Konfigurationsprogramm.

Prüfe vor dem Kompilieren, dass der Quellcode und sein `Product_Model` exakt zur Hardware passen. Die verlinkte veröffentlichte Datei wählt Modell `1048`; ein falsches Modell kann ein falsches Relais- oder Filterverhalten auswählen. Befolge die im Quellkopf genannten Build-Voraussetzungen für ESP8285 und NeoGPS, bewahre ein wieder einspielbares Abbild der unveränderten Firmware und einen Konfigurationsnachweis auf und dokumentiere Quellrevision, Patch und Prüfsumme der Binärdatei.

Prüfe nach dem Flashen jeden Sender einzeln und anschließend beide gemeinsam an Kunstantennen oder über einen sicher gedämpften Messpfad. Prüfe tatsächliche HF-Frequenz, Zeitplanung, Ausgangsleistung, Filterung und spektrale Reinheit, bevor du Antennen anschließt. Bestätige bei einer kurzen Vorabprüfung auf Sendung außerdem, dass die beobachteten Frequenzen innerhalb des vorgesehenen unteren beziehungsweise oberen Fensters bleiben und beide Identitäten ausreichend Joint Spots in denselben Zyklen erzeugen, bevor du den Messlauf beginnst.

<a id="sec-simultaneous-tx-setup-6"></a>
#### B.6 Durch Tausch oder Kreuztausch bestätigen

Bewahre den ersten Lauf als vollständigen eigenen Versuch auf. Führe danach, soweit praktikabel, folgende Kontrollen durch:

1. Tausche die beiden Frequenzzuordnungen, ohne die physischen Pfade zu verändern.
2. Wiederhole denselben Zeitplan als getrennten Lauf.
3. Tausche die geprüften Antennen oder Bauteile zwischen den Sendeketten.
4. Bewahre jede Konfiguration mit ihrer tatsächlichen Target-/Referenzzuordnung als eigenen Lauf auf.

Ein Unterschied, der nach Frequenztausch und Hardware-Kreuztausch der physischen Antenne oder dem geprüften Bauteil folgt, ist überzeugender als ein Unterschied, der an einem Sender, einer Frequenzposition oder einer Folgenphase haften bleibt. Bewahre die Läufe getrennt auf und führe sie nur zusammen, wenn Rollen, Korrekturen und Analyseumfang bewusst angeglichen wurden. Übereinstimmung über diese kontrollierten Läufe ist experimentelle Wiederholbarkeit; Übereinstimmung zwischen Typ-2- und Typ-3-Phasen innerhalb eines Laufs ist nur Konsistenz innerhalb des Laufs.

<div style="page-break-before: always;"></div>

<a id="sec-b"></a>
<a id="sec-reference-snr-calibration"></a>
### Anhang C: Referenz-SNR-Kalibrierung

Dieses Verfahren ermittelt einen stabilen additiven Offset zwischen Empfangsketten oder Pfaden auf der Referenzseite.

1. **Gemeinsames Eingangssignal:** Beide Empfangsketten über einen geeigneten Verteiler und charakterisierte Kabel aus einer stabilen Antenne speisen.
2. **Verteiler charakterisieren:** Pegelunterschiede zwischen den Ausgängen und Kabeldifferenzen berücksichtigen; wenn praktikabel, die Ausgänge in einem Kontrolllauf vertauschen.
3. **Joint Spots sammeln:** Für den Offset-Ermittlungslauf die referenzseitige SNR-Korrektur auf `0.0 dB` setzen. Beide Ketten gleichzeitig über den vorgesehenen Signalpegelbereich betreiben, ohne Verstärkung oder Decoder-Einstellungen zu verändern.
4. **Offset ableiten:** Die ΔSNR-Werte der Joint Spots verwenden und angeben, ob der berichtete Wert aus stationsgleichgewichteten Zusammenfassungen oder aus zusammengefassten Joint Spots berechnet ist.
5. **Konsistenz prüfen:** Nach Station, Zeit und SNR untersuchen. Ein konstanter Wert ist nicht vertretbar, wenn sich der Offset mit Pegel, Frequenz, AGC oder Zeit ändert.
6. **Vorzeichen anwenden:** Den beobachteten Offset `target - reference` mit demselben Vorzeichen eingeben.
7. **Validieren:** Messung wiederholen oder Pfade tauschen und prüfen, ob das korrigierte ΔSNR des gemeinsamen Eingangssignals plausibel nahe null liegt.

Konsistenz über Stations-, Zeit- und SNR-Ansichten stützt die Verwendung eines additiven Offsets innerhalb des geprüften Aufbaus; sie weist keine rückführbare Laborgenauigkeit nach. Verteilerverlust, Fehlanpassung, Kopplung und Instabilität der Quelle können bestehen bleiben.

<a id="sec-license"></a>
### Lizenz

WSPRadar ist unter der GNU Affero General Public License Version 3 (AGPLv3) lizenziert. Maßgeblich ist die Datei `LICENSE` im Repository. Die mitgelieferten Schriftdateien für Rajdhani und Space Mono bleiben separat unter der SIL Open Font License 1.1 lizenziert; Urheberrechtshinweise und Lizenztexte stehen unter `static/fonts/`.

"""
