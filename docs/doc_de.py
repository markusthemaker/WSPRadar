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
    * [7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell](#sec-7-1)
    * [7.2 Identität, Zuordnung und Zeilenkonsolidierung](#sec-7-2)
    * [7.3 Konditionierung auf Target-Aktivität und Zulässigkeit](#sec-7-3)
    * [7.4 Performance-Analyseziel, Klassifikation und Zusammenfassungsgrößen](#sec-7-4)
    * [7.5 Leistungsnormierung, Korrektur und Benchmark-ΔSNR](#sec-7-5)
    * [7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen](#sec-7-6)
    * [7.7 Aggregationshierarchie und Gewichtung](#sec-7-7)
    * [7.8 Geografische, zeitliche und funkwegbezogene Zusammenfassungen](#sec-7-8)
        * [7.8.1 Geografische Zusammenfassungen](#sec-7-8-1)
        * [7.8.2 Abdeckung der Benchmark-Evidenz](#sec-7-8-2)
        * [7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung](#sec-7-8-3)
        * [7.8.4 Zusammenfassungen für den ausgewählten Funkweg](#sec-7-8-4)
        * [7.8.5 Deskriptive Streuung und Visualisierungstransformationen](#sec-7-8-5)
    * [7.9 Geografie, Sonnenstandsklassifikation und Populationsfilter](#sec-7-9)
    * [7.10 Abhängigkeit, Unsicherheit und Geltungsbereich der Validierung](#sec-7-10)
    * [7.11 Robuste ΔSNR-Ereigniserkennung mit lokaler Basislinie](#sec-7-11)
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

Dieser Teil führt von einer Stationsfrage zu einem Ergebnis, das du einordnen und berichten kannst. Kapitel 1 bereitet den WSPR-Betrieb vor, hilft bei der Wahl von RX oder TX sowie Benchmark oder Performance und führt den gemeinsamen Evidenzpfad ein. Kapitel 2 wendet ihn auf jede Analyse an und enthält ein optionales Diagnosewerkzeug für erfahrene Anwender zur Prüfung vorübergehender ΔSNR-Abweichungen. Kapitel 3 hilft bei der nächsten Prüfung und beim Sichern des Ergebnisses. Exakte Bedienelemente und Fehlersuche stehen in Teil II, Berechnungen und wissenschaftliche Grenzen in Teil III.

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
2. **Vor der Analyse die Datenbank prüfen.** Kontrolliere erfolgreiche Meldungen unter dem exakten Empfangsrufzeichen bei RX beziehungsweise Senderufzeichen bei TX in WSPRnet und anschließend ihre Verfügbarkeit in der von WSPRadar verwendeten Datenbank. Prüfe gemeldeten Locator und UTC-Zeiten. Warte die Uploads ab und wähle ein abgeschlossenes Zeitfenster mit dem vorgesehenen Betrieb; eine feste Wartezeit garantiert keine Vollständigkeit. [Abschnitt 5.6](#sec-6-6) behandelt verzögerte Daten und Quellenstatus.
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

Beginne mit den Medianen; die Mittelwerte sind arithmetische Durchschnitte. Weichen die Verteilungen deutlich voneinander ab, prüfe die Stationen mit den meisten Joint Spots. [Abschnitt 7.7](#sec-7-7) veranschaulicht, warum die Ergebnisse unterschiedlich ausfallen können.

**3. Zeitliche Evidenz: wann tritt der Unterschied auf?** Verfolge in **Δ SNR im Zeitverlauf** die Intervallmediane im Vergleich zum gestrichelten Gesamtmedian: bleibt der Unterschied bestehen, kehrt er sich um oder tritt er nur kurz auf? Lies die beschrifteten dB-Werte an der nichtlinearen senkrechten Achse ab. Das Q1–Q3-Band umfasst, sofern angezeigt, die mittleren 50 % der ΔSNR-Werte aus Joint Spots; es ist kein Konfidenzintervall. Die Farbe zeigt die Konzentration der Joint Spots; leere Intervalle enthalten keine.

**Δ SNR nach UTC-Stunde** fasst dieselben Stunden mehrerer Tage zusammen. Suche nach Tagesmustern und prüfe anschließend die einzelnen Tage, bevor du von einem wiederkehrenden Muster sprichst.

**Datengrundlage prüfen.** Prüfe in Decode Outcomes sowohl die Stationsanteile als auch die Spot-Anteile. Die Anzahlen der Joint-Stationen und Joint Spots sowie **Decode Outcomes** und die **zeitliche Evidenzabdeckung des Benchmarks** zeigen, wie viele Stationen und Joint Spots den Vergleich tragen und wo die Abdeckung dünn ist. Der Joint-Evidenzanteil beschreibt den Anteil der Beobachtungen, für den Joint Spots vorliegen; er ist keine Erfolgsquote des Targets. Einseitiger Empfang kann Unterschiede nahe der Dekodierschwelle zeigen, liefert aber kein ΔSNR. Wenn viele einseitige Meldungen vorliegen, nenne sie auch in deiner Schlussfolgerung: ΔSNR beschreibt nur die Joint Spots. Da nur Zyklen mit beobachteter Target-Aktivität eingehen, sind einseitige Anzahlen keine symmetrischen Gewinne und Verluste. [Abschnitt 7.6](#sec-7-6) erklärt die Kategorien einschließlich asynchroner Beobachtungen.

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

Beginne mit den Medianen; die Mittelwerte sind arithmetische Durchschnitte. Weichen die Verteilungen deutlich voneinander ab, prüfe die Empfänger mit den meisten Joint Spots. [Abschnitt 7.7](#sec-7-7) erklärt die unterschiedliche Gewichtung.

**3. Zeitliche Evidenz: wann tritt der Unterschied auf?** Verfolge in **Δ SNR im Zeitverlauf** die Intervallmediane im Vergleich zum gestrichelten Gesamtmedian. Bleibt eine Verschiebung bestehen oder beschränkt sie sich auf einen kurzen Abschnitt? Lies die beschrifteten dB-Werte an der nichtlinearen senkrechten Achse ab. Das Q1–Q3-Band umfasst, sofern angezeigt, die mittleren 50 % der ΔSNR-Werte aus Joint Spots; es ist kein Konfidenzintervall. Die Farbe zeigt die Konzentration der Joint Spots; leere Intervalle enthalten keine.

**Δ SNR nach UTC-Stunde** fasst dieselben Stunden mehrerer Tage zusammen. Prüfe den chronologischen Verlauf an den einzelnen Tagen, bevor du ein Tagesmuster als wiederkehrend bezeichnest.

**Datengrundlage prüfen.** Prüfe in Decode Outcomes sowohl die Stationsanteile als auch die Spot-Anteile. Lies Empfänger- und Joint-Spot-Anzahlen zusammen mit **Decode Outcomes** und der **zeitlichen Evidenzabdeckung des Benchmarks**. Der Joint-Evidenzanteil beschreibt den Anteil der Beobachtungen, für den Joint Spots vorliegen; er ist keine Erfolgsquote des Targets. Einseitige Meldungen können Unterschiede in der Reichweite nahe der Dekodierschwelle zeigen, erlauben aber keinen leistungsnormierten Target-Referenz-SNR-Vergleich. Wenn viele einseitige Meldungen vorliegen, nenne sie auch in deiner Schlussfolgerung: ΔSNR beschreibt nur die Joint Spots. Da nur Zyklen mit beobachteter Target-Aktivität eingehen, sind einseitige Anzahlen keine symmetrischen Gewinne und Verluste. Die Kategorien erklärt [Abschnitt 7.6](#sec-7-6).

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

Prüfe vor dem Versuch beide exakten Datenbankkennungen und ihre wahrheitsgemäß gemeldeten Grid-4-Werte. [Anhang B](#sec-simultaneous-tx-setup) beschreibt die praktische Einrichtung und Vorabprüfung. Die [Abschnitte 7.1–7.2](#sec-7-1) erklären den Unterschied zwischen dieser empfohlenen Betriebsanordnung und den WSPRadar-Regeln für die Zuordnung innerhalb desselben Zyklus.

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

**Die zentrale Kennzahl: Dekodierrate.** Sie gibt an, welchen Prozentsatz der bestätigten Gelegenheiten das Target dekodierte. Eine bestätigte RX-Gelegenheit betrifft eine exakte Senderidentität auf dem gewählten Band in einem WSPR-Zyklus: Das Target dekodiert deren Aussendung, oder ein anderer geeigneter Empfänger meldet sie, während zugleich die Target-Aktivität nachgewiesen ist. Ein erfolgreicher Target-Decode bestätigt beide Endpunkte und zählt auch ohne Meldung eines weiteren Empfängers. Dessen Meldung allein belegt nicht, dass das Target zugehört hat. [Abschnitt 7.4](#sec-7-4) definiert die Einordnung.

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

**Die zentrale Kennzahl: Dekodierrate.** Sie gibt an, bei welchem Prozentsatz der bestätigten Empfängergelegenheiten das Target dekodiert wurde. Eine bestätigte TX-Gelegenheit betrifft eine exakte Empfängeridentität auf dem gewählten Band in einem WSPR-Zyklus: Dieser Empfänger dekodiert das Target oder einen anderen qualifizierenden Sender, während zugleich die Target-Aktivität nachgewiesen ist. Eine erfolgreiche Target-Meldung bestätigt beide Endpunkte und zählt auch dann, wenn dieser Empfänger keinen anderen Sender meldet. Wird das Target andernorts gehört, belegt dies die Target-Aktivität, aber nicht, dass dieser bestimmte stille Empfänger zugehört hat. [Abschnitt 7.4](#sec-7-4) definiert den Nenner.

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

Dieser Kontext verändert nicht, ob ein einzelner Funkweg qualifiziert wird. [Abschnitt 7.11](#sec-7-11) definiert die vollständige Konstruktion, Stützzahlen, Zeitregeln und Formeln.

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

Die optionale fachkundige Nutzung der ΔSNR-Ausreißererkennung für Benchmark wird in [Abschnitt 2.5](#sec-outlier) eingeführt. [Abschnitt 4.6](#sec-5-6) enthält ihre Bedienelemente; die formale wissenschaftliche Definition steht in [Abschnitt 7.11](#sec-7-11).

<a id="sec-5"></a>

### 4. Bedienelemente und Konfiguration

WSPRadar unterscheidet Bedienelemente, welche die beibehaltene wissenschaftliche Evidenz verändern, von solchen, die nur die Inspektion bereits abgeschlossener Evidenz beeinflussen.

| Klasse | Wirkung | Gespeichert? | Neuer Lauf erforderlich? |
|---|---|---|---|
| **Wissenschaftliche Bedienelemente** | Verändern Identität, Band, Zeit, Referenzdesign, Zulässigkeit, Normierung, Filter, Schwellen oder geografische Population. | Soweit anwendbar | Ja; das vorherige Ergebnis wird verworfen |
| **Ansichtsbedienelemente** | Verändern den aktiven Inspektionsbereich, die ausgewählte Station, die Sichtbarkeit von Evidenz oder die Darstellungsaggregation, ohne beibehaltene Evidenz neu zu klassifizieren. | Nur ausdrücklich unterstützte dauerhafte Einstellungen | Nein |
| **Temporäre Ansichtsoptionen** | Verändern nur die aktuelle Bildschirmdarstellung, temporäre Tabellenfilter, die Sichtbarkeit der Dokumentation oder einen vorbereiteten Download. | Nein | Nein |

Versionierte Konfigurationen speichern die zutreffenden wissenschaftlichen Einstellungen und die unterstützten dauerhaften Ansichtsoptionen. Die exakten Berechnungen stehen in [Kapitel 7](#sec-7); [Abschnitt 8.4](#sec-8-4) fasst ausgewählte öffentliche maschinenlesbare Bezeichnungen für Konfiguration, URL und Export zusammen. Für den vollständigen Feldvertrag gespeicherter Konfigurationen ist das formale JSON-Schema maßgeblich.

<a id="sec-5-1"></a>

#### 4.1 Ablaufsteuerung

| Bedienelement | Funktion | Wichtiges Verhalten |
|---|---|---|
| **`EN` / `DE`** | Ändert die Anzeigesprache. | Ein abgeschlossenes Ergebnis wird aus seiner aufbewahrten Evidenz ohne erneute Analyse neu dargestellt. Ohne abgeschlossenes Ergebnis startet ein Sprachwechsel die Analyse nicht automatisch neu; starte sie ausdrücklich erneut. Fehlende oder abgelaufene Evidenz erfordert ebenfalls einen ausdrücklich neu gestarteten Lauf. |
| **`Eingabeansicht`** | Wechselt zwischen `Geführt` und `Klassisch`. | Beide Ansichten bearbeiten dieselbe wissenschaftliche Konfiguration. Die gewählte Eingabeansicht wird nicht gespeichert. |
| **`Demo laden`** | Lädt ein gepflegtes historisches Profil. | Das Laden startet keine Analyse. Änderungen an Filtern, Evidenzschwellen und Ergebnisansicht behalten den Demo-Kontext; eine Änderung der Versuchsdefinition löst die Konfiguration von der Demo. |
| **`Konfig laden`** | Lädt eine versionierte JSON-`.config`. | Ungültige Identitäten, Datumswerte, Auswahlwerte, Wertebereiche, doppelte Felder und nicht unterstützte Schemaversionen werden abgelehnt und nicht erraten. |
| **`Konfig speichern`** | Speichert in der geführten und klassischen Eingabe die zutreffenden wissenschaftlichen Eingaben und unterstützten dauerhaften Ansichtseinstellungen aus dem abschließenden Prüfbereich. | Die Datei enthält absolute UTC-Grenzen, aber keine Ergebniszeilen, externen Versuchsnotizen oder flüchtigen Tabellenfilter. Das Speichern bleibt unverfügbar, bis die Frage und bei einem Benchmark zusätzlich das Benchmark-Design vollständig sind. |
| **`RX-Analyse starten` / `TX-Analyse starten`** | Führt in der geführten und klassischen Eingabe das ausgewählte Performance- oder Benchmark-Ergebnis aus dem abschließenden Prüfbereich aus. | Starten bleibt verfügbar, um unvollständige oder ungültige Felder mit direkter Korrekturhilfe anzuzeigen; die Analyse beginnt erst nach Klärung aller erforderlichen Eingaben und einer gegebenenfalls nötigen Referenzstandortwahl. Eine Änderung eines wissenschaftlichen Bedienelements nach dem Lauf verwirft das Ergebnis und verlangt einen neuen Lauf. |
| **`Alle Ergebnisse zum Download vorbereiten`** | Erstellt das aktuelle Exportpaket. | Verwendet die abgeschlossene Evidenz und die aktuellen Inspektor-Auswahlen. |
| **`Vollständige Dokumentation laden` / `Vollständige Dokumentation ausblenden`** | Zeigt oder verbirgt das vollständige Webhandbuch. | Reiner Darstellungszustand. |
| **`PDF vorbereiten`** | Erstellt das Handbuch in der gewählten Sprache als PDF. | Das vollständige Webhandbuch muss dazu nicht zuerst geöffnet werden. |

Beide Eingabeansichten enden mit derselben abschließenden Konfigurationsübersicht. Im Zustand **`Prüfung — startbereit ✓`** liegen `RX-Analyse starten` / `TX-Analyse starten` und `Konfig speichern` erst nach gültiger Konfiguration innerhalb dieses Bereichs. Der Prüfbereich bleibt beim Start des Laufs und nach seinem Abschluss geöffnet; auch der Laufstatus bleibt bei **`Complete`** geöffnet. In der klassischen Eingabe wird beim Start einer gewöhnlichen Analyse oder einer Demo kein Konfigurationsbereich automatisch geschlossen; einzelne Bereiche lassen sich weiterhin manuell schließen und wieder öffnen. Die geführte Eingabe darf frühere abgeschlossene Schritte weiterhin kompakt darstellen, ihr abschließender Prüfbereich bleibt jedoch geöffnet.

Nach dem Laden einer Demo in der geführten Eingabe öffnet `Einstellungen Schritt für Schritt durchgehen` die Einrichtungsschritte zur Prüfung. `Direkt zu Prüfen und starten` öffnet den abschließenden Prüfbereich und startet die Analyse sofort mit den aktuellen gültigen Einstellungen; ein zweiter Klick auf `RX-Analyse starten` / `TX-Analyse starten` ist nicht erforderlich. Die Abkürzung bleibt unverfügbar, solange erforderliche Einstellungen unvollständig sind oder bereits eine Analyse läuft. Das Laden der Demo selbst startet weiterhin keine Analyse.

Nach dem angenommenen Start einer Analyse springt die Seite zum Laufstatus unterhalb der Prüfung. Sobald das erste Kartenbild bereitsteht, springt sie zu diesem Ergebnis, während Segment-Inspektor und Drill-Down-Daten automatisch weiter vorbereitet werden. Der Status erreicht **`Complete`** erst, wenn alle Ergebnisansichten bereitstehen. Jeder automatische Sprung erfolgt einmal pro Startauftrag; wer während der Wartezeit selbst scrollt oder an eine andere Stelle navigiert, verhindert den Sprung zur Karte. Interaktionen mit den Ergebnisansichten und die erneute Anzeige eines abgeschlossenen Laufs lösen diese automatischen Sprünge nicht erneut aus.

**Aktuelles Konfigurationsformat.** Akzeptiert werden ausschließlich das aktuelle Schema gespeicherter Konfigurationen und der aktuelle öffentliche URL-Vertrag; aufgegebene Aliasnamen, Felder und frühere Eingabeformate werden ohne Migration abgelehnt. Gespeicherte Dateien bewahren die Eingaben und dauerhaften Ansichtsoptionen, die für die ausgewählte Analyse gelten. Ungültige oder nicht unterstützte Dateien werden abgelehnt, statt stillschweigend neu interpretiert zu werden. Das formale JSON-Schema ist der maßgebliche vollständige Vertrag gespeicherter Konfigurationen; [Abschnitt 8.4](#sec-8-4) bietet eine knappe, betriebsbezogene Zusammenfassung ausgewählter öffentlicher Bezeichnungen. Das Laden oder Speichern einer Konfiguration erzeugt kein zusätzliches Ergebnis; ausgeführt wird nur die ausgewählte Performance- oder Benchmark-Analyse.

**Lebenszyklus des Demo-Kontexts.** Eine geladene Demo behält ihren sichtbaren Kontext, wenn nur Populationsfilter, Evidenzschwellen, Inspektor-Bereich oder andere Bedienelemente der Ergebnisansicht geändert werden. Eine angepasste Ansicht lässt sich dadurch weiterhin vor dem Hintergrund des ursprünglichen Beispiels deuten. Änderungen an Frage oder Richtung, Target-Rufzeichen oder -QTH, Band, Messzeitraum, Benchmark-Design oder -Identität, Nachbarschaftsradius sowie Absicht oder Wert der Korrektur entfernen Demo-Metadaten und Profilidentität aus später gespeicherten Konfigurationen, weil der Aufbau nicht mehr dem dokumentierten Versuch entspricht. Jede wissenschaftliche Änderung beendet außerdem die exakte Demo-Cache-Identität, auch wenn der erklärende Demo-Kontext sichtbar bleibt. Eine wissenschaftliche Änderung der Population oder Evidenz löscht jede vorausgewählte Performance- und Benchmark-Identität in Station Insights, da der Funkweg im neuen Ergebnis fehlen kann. Reine Bedienelemente der Ergebnisansicht löschen diese Auswahl nicht.

**Wiederverwendung von Demo-Daten.** Beim Ausführen einer unveränderten Demo werden fehlende Datenbank-Abfrageergebnisse abgerufen und validierte Zeilen auf dem Datenträger des App-Servers gespeichert. Spätere Läufe verwenden passende Einträge ohne automatischen Ablauf erneut, auch über Sitzungen und App-Neustarts hinweg, solange dieser Datenträger erhalten bleibt. Eine geänderte Abfrage, ein inkompatibles Cache-Format oder fehlende beziehungsweise beschädigte Dateien erfordern einen erneuten Abruf. Weder beim App-Start noch beim Laden einer Demo werden deren Daten vorab abgerufen. Die Wiederverwendung bewahrt die abgerufenen Daten, statt spätere Datenbankkorrekturen automatisch zu übernehmen; jeder Lauf führt die Analyse weiterhin mit dem aktuellen Anwendungscode aus.

<a id="sec-5-2"></a>

#### 4.2 Frage, Target und Messzeitraum

Die Klassische Eingabe ordnet die wissenschaftliche Konfiguration nach der Fragestellung. Im ersten Bereich **`Frage`** muss eine von vier vollständigen Analysen gewählt werden: `RX Performance`, `TX Performance`, `RX-Benchmark` oder `TX-Benchmark`. Diese eine Auswahl legt sowohl die RX-/TX-Richtung als auch fest, ob der Lauf eigenständige Performance-Evidenz oder einen Target–Referenz-Benchmark erzeugt. Der zweite Bereich **`Target und Messzeitraum`** erfasst anschließend wie bisher Target-Identität, QTH, Band und absoluten UTC-Zeitraum. Bei einem Benchmark folgt **`Benchmark-Design`**. Beide Ergebnistypen zeigen danach **`Filter, Analyseumfang und Evidenz`** und abschließend den Prüfbereich; Performance besitzt damit vier und Benchmark fünf klassische Bereiche.

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

Bei `RX Performance` und `TX Performance` entfällt der Bereich **`Benchmark-Design`** vollständig, weil Performance keine Referenz verwendet. Der abschließende Prüfbereich erscheint nach dem gemeinsamen Bereich für Filter, Umfang und Evidenz. Beim Start werden ungültige oder unvollständige Felder direkt mit roter Rückmeldung und konkreter Korrekturhilfe markiert; die Korrektur eines Feldes entfernt dessen Hinweis. Fehler beim Datenbankzugriff werden von einem ungültigen Rufzeichen oder einem leeren Meldezeitfenster getrennt ausgewiesen. Performance und Benchmark sind sich gegenseitig ausschließende Ergebnistypen: Ein Lauf erzeugt nur das ausgewählte Ergebnis. [Abschnitt 8.4](#sec-8-4) fasst ausgewählte öffentliche maschinenlesbare Bezeichnungen für Konfiguration, URL und Export zusammen; er ist kein vollständiger Feld- oder Parameterkatalog.

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

Eine positive Korrektur erhöht das korrigierte Referenz-SNR und verringert dadurch ΔSNR Target minus Referenz. Gib einen gemessenen Kalibrierversatz `target - reference` mit demselben Vorzeichen ein. Ergibt eine Kalibrierung mit gemeinsamem Eingang beispielsweise `+1.6 dB`, wird `+1.6 dB` eingetragen. [Abschnitt 7.5](#sec-7-5) definiert die Gleichungen.

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

Geführte und klassische Eingabe verwenden für diese Einstellungen denselben Bereichsnamen **`Filter, Analyseumfang und Evidenz`**. Innerhalb dieses Schritts zeigt die geführte Eingabe stets die zutreffenden Felder; eine getrennte vorgeschaltete Auswahl entfällt. Unveränderte Konfigurationen initialisieren die sichtbaren Felder mit den nachstehenden ergebnisspezifischen Standardwerten; geladene Konfigurationen und Demos tragen ihre gespeicherten Werte in dieselben sichtbaren Felder ein. Das bloße Anzeigen dieser Werte bearbeitet sie nicht und löst den Demo-Kontext nicht. Die angezeigten Einstellungen für Filter, Analyseumfang und Evidenz gelten auch dann, wenn du diesen Bereich unverändert lässt.

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

Die ΔSNR-Ausreißererkennung für Benchmark ist eine optionale fachkundige Analyse der beibehaltenen **Joint Spots** zu ihren nativen WSPR-Zykluszeiten. Die Erkennung läuft getrennt für jeden exakten Peer-Funkweg `Rufzeichen + Locator` und unabhängig vom ausgewählten Darstellungs-Bin der **Zeitlichen Evidenz**. Einseitige Evidenz kann ein fehlendes ΔSNR nicht ersetzen. [Abschnitt 2.5](#sec-outlier) erklärt Bedienung und Interpretation; [Abschnitt 7.11](#sec-7-11) definiert die Methode formal.

| Bedienelement | Standard / Wertebereich | Methodensymbol | Wissenschaftliche Wirkung |
|---|---|---|---|
| **`ΔSNR-Ausreißerkandidaten melden`** | aus | — | Aktiviert den optionalen Detektor und Ausreißerbericht ausschließlich für Benchmark. Ist die Einstellung aus, fügt WSPRadar dem Ergebnis weder Ausreißererkennung, -felder, -markierungen oder -begriffe noch Ausreißer-Exportmetadaten hinzu. |
| **`Minimale absolute ΔSNR-Abweichung (dB)`** | `6.0`; einschließlich `0.1`–`100.0 dB` | $D_{\min}$ | Verlangt, dass das mediane Residuum des Ereignisses und jeder berichtete Grenzanker mindestens um diesen Betrag von der lokalen Baseline abweichen. |
| **`Minimaler robuster z-Wert`** | `3.0`; einschließlich `0.1`–`100.0` | $Z_{\min}$ | Verlangt, dass sowohl der Ereignismedian als auch jeder berichtete Grenzanker diesen absoluten robusten lokalen Streuungswert erreichen. Der Wert ist deskriptiv und weder eine kalibrierte Wahrscheinlichkeit noch ein konventionelles gaußsches Signifikanzniveau. |
| **`Maximaler Unterschied zwischen Baseline davor/danach (dB)`** | `3.0`; einschließlich `0.1`–`100.0 dB` | $H_{\max}$ | Verwirft einen Kandidaten, wenn sich die Flankenmediane vor und nach dem Ereignis um mehr als diesen Betrag unterscheiden, damit eine instabile oder verschobene Baseline nicht als vorübergehende Auslenkung berichtet wird. |

Die Vergleiche für Abweichung und Baseline-Unterschied verwenden eine feste Toleranz von `0.01 dB`, wie in [Abschnitt 7.11](#sec-7-11) definiert; die konfigurierten Schwellen und internen Evidenzwerte bleiben ungerundet. Für den Vergleich des robusten z-Werts gilt keine solche Toleranz.

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

Das Gate ist bewusst Target-zentriert. Die Betriebsbereitschaft der Referenz bleibt Teil des Versuchs, und ein Tausch von Target und Referenz kann die einseitigen Decode Outcomes und die zulässige Population verändern. [Abschnitt 7.3](#sec-7-3) definiert diese Konditionierung formal.

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

Teil III erklärt, warum die Vergleiche sinnvoll sind, wie die Kennzahlen entstehen und welche Aussagen sie tragen. Er richtet sich an technisch interessierte Funkamateure, HamSCI-Mitwirkende und Gutachter. Kapitel 6 stellt den Bezug zu früheren Arbeiten her; Kapitel 7 folgt den Daten von gemeldeten Spots bis zum Ergebnis; Kapitel 8 behandelt belastbare Aussagen und Reproduzierbarkeit. Die wissenschaftlichen Details erklären, welche Beobachtungen zählen, was fehlt, wie Stationen gewichtet werden, welche Beobachtungen voneinander abhängen und wie Werte umgerechnet werden. Die praktische Bedeutung steht vor der formalen Notation.

<a id="sec-d"></a>
### 6. Literatur, Vorarbeiten und Einordnung

**Wozu dieses Kapitel?** Frühere Versuche erklären drei praktische Entscheidungen: unter gemeinsamen Bedingungen vergleichen, vor der Deutung fehlender Meldungen die Aktivität prüfen und vollständige Signalketten kontrollieren, bevor ein Unterschied einer Antenne zugeschrieben wird. Dies ist eine gezielte methodische Übersicht, keine systematische oder erschöpfende Literaturrecherche. Begutachtete Fachartikel, Preprints, technische Amateurfunkberichte und Softwaredokumentation liefern unterschiedliche Arten von Belegen. Ihre Beiträge werden im Folgenden unterschieden; sie bestätigen nicht jede WSPRadar-Kennzahl oder methodische Entscheidung.

<a id="sec-d-1"></a>
#### 6.1 Vom Meldenetz zum Versuchsdatensatz

Taylor und Walker beschrieben die WSPRnet-Datenbank als Grundlage für Experimente: „The WSPRnet database represents a rich source of experimental data for propagation studies.“ Ihr Beispiel gruppiert Beobachtungen über mehrere Wochen nach Tageszeit. Es zeigt sowohl den Wert angesammelter Meldungen als auch die Notwendigkeit, sie als Beobachtungsdaten und nicht als kontrollierte Labordaten zu interpretieren. <a href="#ref-6">[Ref-6]</a>

Frissell et al. ordnen WSPRNet zusammen mit dem Reverse Beacon Network und PSKReporter als etablierte Amateurfunk-Beobachtungsnetze ein, die langfristige Beobachtungen der Unterseite der Ionosphäre (Bottomside) liefern. Sie unterscheiden diese Netze von zweckgebundenen wissenschaftlichen Instrumenten und empfehlen eine Kreuzkalibrierung zwischen Instrumentennetzen. Die Übersicht stützt die wissenschaftliche Nutzung von Amateurfunkbeobachtungen; sie macht nicht jeden beitragenden Empfänger zu einem kalibrierten Sensor. <a href="#ref-7">[Ref-7]</a>

Die WSPR-Datenbank enthält Beobachtungen über lange Zeiträume und viele Standorte. Die Stationen unterscheiden sich jedoch, Ausrüstung ändert sich, Kennungen und Leistungen werden von den Betreibern angegeben, und Betriebspläne sind meist unbekannt. Gemeldet werden nur erfolgreiche Decodes. WSPRadar muss daher festlegen, welche Beobachtungen zählen und wann fehlende Meldungen aussagekräftig sind; ein fehlender Spot allein reicht nicht.

<a id="sec-d-2"></a>
#### 6.2 WSPR-Beobachtungsdaten interpretierbar machen

<a id="sec-d-lo"></a>
Lo et al. untersuchten mit WSPR-Meldungen auf 7 MHz die Greyline-Ausbreitung und warnten davor, dass für WSPR-Geräte keine maßgeblichen Betriebspläne existieren. Bevor sie einen fehlenden Funkweg interpretierten, prüften sie, ob der Sender andernorts gehört worden war oder ob der Empfänger eine andere Station gehört hatte. Außerdem betonten sie die Konsistenz von Rufzeichen und Standort sowie die Verwendung mehrerer Standorte. <a href="#ref-9">[Ref-9]</a>

Diese Aktivitätsprüfung ist eine direkte Vorarbeit für das Target-Active Gate und die bestätigten Gelegenheiten von WSPRadar: erst den Betrieb belegen, dann eine fehlende Meldung bewerten. Lo et al. definieren weder die asymmetrische Target-Konditionierung von WSPRadar noch dessen Performance-Analyseziel, Stationsgewichtung, Decode Outcomes oder lokale Referenzen. Diese eigenständigen WSPRadar-Entscheidungen sind in [Kapitel 7](#sec-7) definiert.

<a id="sec-d-3"></a>
#### 6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen

<a id="sec-d-toledo"></a>
**Toledo (2010): Warum langsames Abwechseln scheitert.** Sivan Toledo erprobte ungefähr eine Stunde lang eine Antenne und anschließend eine andere. Dabei änderte sich das SNR des Funkwegs in derselben Größenordnung wie der scheinbare Antennenunterschied. Er folgerte, dass dieser Aufbau die Antennen nicht isolieren konnte, und besprach Versuche anderer Funkamateure mit zyklusweiser Umschaltung oder gleichzeitigen Aussendungen über getrennte Hardware. WSPRadar unterstützt simultane Vergleiche innerhalb desselben WSPR-Zyklus; die Analyse paart keine unterschiedlichen Sendezyklen. <a href="#ref-3">[Ref-3]</a>

<a id="sec-d-milazzo"></a>
**Milazzo (2011): Vollständige Stationen über denselben Empfänger vergleichen.** Carol Milazzo verglich zwei 29 km voneinander entfernte Stationen über einen gemeinsamen Empfänger in 1.750 km Entfernung, korrigierte die gemeldeten SNR-Werte um Unterschiede der Sendeleistung, verglich den Verlauf mit VOACAP, berücksichtigte unterschiedliche Sendeanteile und untersuchte reziproke RX-Meldungen. Die Fallstudie zeigt den praktischen Wert eines WSPR-Vergleichs über denselben Empfänger, macht aber zugleich die Grenzen durch unterschiedliche QTHs, Hardware, lokalen Störpegel, nur einen ausgewählten Empfänger und eine fehlende formale Unsicherheitsanalyse sichtbar. <a href="#ref-4">[Ref-4]</a>

<a id="sec-d-griffiths-squibb"></a>
**Griffiths und Squibb (2017): RX-Vergleich desselben Signals als Stationsdiagnose.** Für zwei Empfänger an getrennten QTHs behielten sie Meldungen desselben Senders zur selben Zeit bei und setzten die SNR-Differenz in Beziehung zu Bodenfeuchte, Zeit, Entfernung und Änderungen an der Station. Die Arbeit zeigt, wie gepaarte WSPR-Beobachtungen vollständige Empfangssysteme diagnostizieren und Strukturen sichtbar machen können, die reine Spotzahlen verdecken. Da sich Antennen, QTHs, Störpegel und Ausrüstung unterschieden, stützt sie vergleichende Stationsevidenz und keinen isolierten, kalibrierten Antennengewinn. <a href="#ref-5">[Ref-5]</a>

<a id="sec-d-vanhamel"></a>
**Vanhamel, Machiels und Lamy (2022): Zuerst die Empfangsketten prüfen.** Ihr begutachteter 160-m-Versuch prüfte den Versatz zweier nominell identischer Empfangsketten an einer gemeinsamen Antenne. Anschließend wurden Antennen verglichen, indem beide Ketten dieselben entfernten Aussendungen gleichzeitig empfingen. Innerhalb der betrachteten Quellen ist dies die stärkste direkte Vorarbeit für kontrollierte RX-Vergleiche und die Prüfung von Empfangsketten-Offsets vor der Deutung von Antennenunterschieden. Die Ausbreitungsergebnisse zeigen außerdem, dass Polarisation und ionosphärische Effekte mit dem gemeldeten SNR gekoppelt bleiben. <a href="#ref-2">[Ref-2]</a>

<a id="sec-d-zander"></a>
**Zander (2022): Simultaner TX-Vergleich am selben Empfänger.** Zander modelliert zwei lokale Antennen, die im selben WSPR-Zyklus von getrennten, nominell leistungsgleichen Sendern mit unterschiedlichen Rufzeichen gespeist werden. Ein entfernter Empfänger trägt nur dann bei, wenn er beide Signale im selben Intervall meldet. Unter den Annahmen gleicher Zeit, eines gemeinsamen Funkwegs und gleicher Leistung heben sich gemeinsame Pfaddämpfung und Empfängerrauschen in der SNR-Differenz auf; frequenzselektive Störungen, fehlgeschlagene Decodes, Quantisierung und Unterschiede der Sendeketten bleiben bestehen. Da jede Differenz innerhalb desselben entfernten Empfängers gebildet wird, ist für dieses Paar keine Empfängerkalibrierung erforderlich; Gleichheit oder Korrektur der beiden Sendeleistungen bleibt jedoch wesentlich. <a href="#ref-1">[Ref-1]</a>

Zander berichtet je Vorversuch ungefähr 1.000 Beobachtungen, von denen etwa 150–200 gemeinsame Meldungen aus 15–35 Empfängern beibehalten wurden; die Stichproben-Standardabweichung lag nahe 3 dB. Zander beansprucht eine Genauigkeit unter 1 dB. Wir lesen die rechnerische Begründung enger: Sie schätzt die Präzision eines arithmetischen Mittels unter den Modell- und Stichprobenannahmen, ohne eine rückführbare Gesamtgenauigkeit nachzuweisen. Geografische Stichprobe, Antennenrichtwirkung und unbekannte Elevationswinkel bleiben systematische Grenzen. Die Studie stützt simultanes Delta SNR am selben Empfänger, nicht jedoch stationsgleichgewichtete Mediane, Decode Outcomes oder Nachbarschaftsreferenzen.

<a id="sec-d-4"></a>
#### 6.4 Analyseinfrastruktur und verwandte Werkzeuge

Griffiths und Robinett zeigten, wie eine Datenbank die Meldungen zweier Empfänger für denselben Sender, dieselbe Zeit und dasselbe Band zusammenführen kann. Ihre Werkzeuge boten Diagramme der SNR-Differenz, Mediane, Quartile, Zeit-Heatmaps, Entfernungs-/Azimutansichten und Export. Damit entstand eine Grundlage für nachvollziehbare Vergleiche, nicht für die besonderen WSPRadar-Regeln zur Datenauswahl, Konditionierung und Zusammenfassung. <a href="#ref-13">[Ref-13]</a>

WSPR.Rocks ermöglicht eine schnelle SQL-basierte Erkundung von WSPR-Daten mit Karten, Tabellen, SpotQ und Heatmaps. WSPRdaemon legt den Schwerpunkt auf robuste Erfassung mit mehreren Empfängern, Zeitplanung und zusätzliche Rausch-/Doppler-Metadaten. SOTABEAMS WSPRlite/DXplorer, WSPR-Station-Compare, das Antenna Performance Analysis Tool und WATT bieten weitere Arbeitsabläufe für Vergleich, Berichterstattung und Visualisierung <a href="#ref-14">[Ref-14]</a> <a href="#ref-15">[Ref-15]</a> <a href="#ref-16">[Ref-16]</a> <a href="#ref-17">[Ref-17]</a> <a href="#ref-18">[Ref-18]</a>.

Diese Systeme belegen umfangreiche Vorarbeiten bei Datenerfassung, Erkundung, Rangbildung, Vergleich, Kartendarstellung und Berichterstattung. WSPRadar verbindet klare Versuchsdefinitionen, Regeln für die Aufnahme von Beobachtungen, aufeinander aufbauende Stations- und geografische Zusammenfassungen, Joint Spots und einseitigen Empfang sowie den Rückweg zu den zugrunde liegenden Beobachtungen. Es beansprucht nicht, das erste WSPR-Analysewerkzeug zu sein.

<a id="sec-d-5"></a>
#### 6.5 Was WSPRadar übernimmt, integriert und ergänzt

WSPRadar übernimmt gesammelte WSPR-Beobachtungen, Aktivitätsprüfungen, Korrektur anhand gemeldeter Leistung, Paarbildung unter gemeinsamen Bedingungen, den Vergleich kalibrierter Empfangsketten, Datenbank-Joins sowie geografische und zeitliche Inspektion. Es führt diese Elemente in einem TX-/RX-Arbeitsablauf zusammen mit:

* Benchmark mit Referenzaufbau/-station oder dynamischer Referenznachbarschaft;
* Joint Spots aus demselben Zyklus und deren ΔSNR, getrennt von einseitigen Decode Outcomes;
* Normierung anhand gemeldeter Leistung und optionaler referenzseitiger Korrektur;
* Performance auf Grundlage bestätigter Gelegenheiten;
* stationsgleichgewichteten und beobachtungsbezogenen Zusammenfassungen;
* einem Auditpfad von Karte über Segment und Station bis zur Zeile; und
* versionierter Konfiguration, verarbeiteter Evidenz und Reproduzierbarkeitsexport.

Innerhalb der geprüften Quellen sind die deutlichsten spezifischen Ergänzungen von WSPRadar der ausdrücklich definierte konditionale Performance-Nenner, die Trennung gepaarter von einseitiger Evidenz, dynamische Referenzen des lokalen Nachbarschafts-Medians, hierarchische stationsgleichgewichtete geografische Aggregation und ein integrierter Auditpfad über alle unterstützten Designs.

Dies ist eine begrenzte Aussage über Integration und Methode und kein globaler Prioritätsanspruch. Medianaggregation an sich ist nicht neu. WSPRadar sollte als strukturierte Versuchs- und Auditschicht oberhalb eines Spot-Browsers beschrieben werden und nicht als Ersatz für die Quelldatenbanken, andere Analysewerkzeuge oder kalibrierte HF-Messtechnik.

<a id="sec-7"></a>
### 7. Wissenschaftliche Methoden

Benchmark vergleicht das SNR von Joint Spots: Wie unterschieden sich das gemeldete Target- und Referenz-SNR für denselben qualifizierenden Peer-Zyklus? Performance zählt bestätigte Gelegenheiten: Wie oft war das Target erfolgreich, wenn die erforderliche Aktivität beobachtbar war? Beide Fragen hängen davon ab, welche Peers und Zyklen in die Rechnung eingehen.

Dieses Kapitel definiert diese wissenschaftlichen Regeln. WSPRadar beginnt mit gemeldeten Beobachtungen, bildet daraus zulässige Evidenzeinheiten, leitet Größen wie normiertes SNR und gepaartes ΔSNR ab und berechnet anschließend deskriptive Zusammenfassungen. Diese Werte sind für die Evidenz exakt, die nach den ausgewählten Regeln beibehalten wurde. Sie sind nicht automatisch Aussagen über alle möglichen Stationen, künftige Betriebsbedingungen oder eine isolierte physikalische Eigenschaft der Station.

Die Übertragung auf eine breitere oder künftige Population erfordert ein zusätzliches Modell für Stichprobenauswahl und Abhängigkeiten; WSPRadar nimmt diesen Inferenzschritt nicht automatisch vor.

Hilfreich ist die Unterscheidung von fünf Ebenen:

1. **Gemeldete Beobachtungen:** hochgeladene WSPR-Spots mit Rufzeichen, Locator, Leistung, Zeit und SNR.
2. **Gebildete Evidenzeinheiten:** qualifizierende Gelegenheiten, Peer-Zyklen, Joint-Einheiten, die nach den Zulässigkeits- und Zuordnungsregeln von WSPRadar entstehen.
3. **Abgeleitete Größen:** normiertes SNR, Decode Outcomes und Target-minus-Referenz-ΔSNR einer einzelnen Evidenzeinheit.
4. **Deskriptive Zusammenfassungen:** Raten, Mediane, Reichweite, Evidenzanteile sowie zeitliche und geografische Zusammenfassungen der beibehaltenen Evidenz.
5. **Interpretation über den Lauf hinaus:** Aussagen über künftiges Verhalten, eine breitere Population oder eine physische Ursache. Solche Verallgemeinerungen benötigen zusätzliche Annahmen und experimentelle Kontrolle; die reine Berechnung genügt dafür nicht.

**Methodischer Überblick**

| Design | Kleinste Vergleichseinheit | Konditionierung / Zulässigkeit | Hauptzusammenfassung | Wichtigste Grenze |
|---|---|---|---|---|
| RX Referenzaufbau/-station | ein Peer-Zyklus eines entfernten Senders | Target aktiv; beide Empfänger melden denselben Sender-Zyklus für ΔSNR | Stationsmedian des ΔSNR, danach Median über Stationen | vollständige Empfangspfade, sofern Ketten nicht kontrolliert sind |
| TX Referenzaufbau/-station | ein Peer-Zyklus eines entfernten Empfängers | Target aktiv; derselbe Empfänger-Zyklus für gepaartes ΔSNR | Stationsmedian des ΔSNR, danach Median über Stationen | Leistung, Kettenunterschiede und Auswahl nach Joint-Decode |
| Referenznachbarschaft (Lokaler Median) | ein Target-/lokaler-Referenz-Peer-Zyklus | Target aktiv; ein Beitrag je aktiver lokaler Identität | lokaler Median als Referenz, danach Stations- und Segmentmediane des ΔSNR | wechselnde, unkalibrierte Zusammensetzung |
| RX Performance | ein Peer-Zyklus eines entfernten Senders | Target-RX aktiv; Peer-TX vom Target-RX oder einem anderen geeigneten RX decodiert | Peer-Dekodierrate, danach Mittel mit gleicher Peer-Gewichtung; gepoolte Gelegenheitsrate bleibt erhalten | bedingte Beobachtbarkeit, keine kalibrierte Empfindlichkeit |
| TX Performance | ein Peer-Zyklus eines entfernten Empfängers | Target-TX aktiv; Peer-RX decodiert Target-TX oder einen anderen qualifizierenden TX auf demselben Band | Peer-Dekodierrate, danach Mittel mit gleicher Peer-Gewichtung; gepoolte Gelegenheitsrate bleibt erhalten | bedingte Beobachtbarkeit, nicht alle Sendeversuche |

Die Hierarchie lässt sich von links nach rechts lesen: WSPRadar entscheidet zuerst, welche Evidenzeinheiten zur Analyse gehören, berechnet danach eine Größe auf Peer- oder Funkwegebene und bildet erst dann die angezeigte stationsgleichgewichtete Zusammenfassung. Die folgenden Formeln machen diese Schritte prüfbar; der Text nach jeder Formel erklärt dieselbe Berechnung in Funkpraxis-Sprache.

**Verwendete Notation**

| Symbol | Bedeutung |
|---|---|
| $i$ | eine Peer-<strong class="defined-term">Identität</strong>, definiert als exaktes `Rufzeichen + gemeldeter Locator` |
| $c$ | ein zulässiger WSPR-<strong class="defined-term">Zyklus</strong> |
| $g$ | ein beibehaltener <strong class="defined-term">geografischer</strong> Bereich oder ein Segment |
| $b$ | ein Entfernungs- oder Zeit-<strong class="defined-term">Bin</strong> |
| $S_{i,c}$ | Target-<strong class="defined-term">Erfolgs</strong>indikator innerhalb einer zulässigen Performance-Gelegenheit |
| $O_{i,c}$ | Performance-<strong class="defined-term">Gelegenheits</strong>indikator nach Aktivitäts-, Identitäts- und Populationsregeln |
| $D_{i,c}$ | gepaartes Target-minus-Referenz-<strong class="defined-term">Delta</strong>-SNR, wenn beide Seiten beobachtet wurden |
| $T_{i,b},J_{i,b},R_{i,b}$ | Anzahlen Only <strong class="defined-term">Target</strong>, <strong class="defined-term">Joint</strong> und Only <strong class="defined-term">Reference</strong> im Benchmark-Bereich $b$ |

Ein Indikator ist `1`, wenn seine Bedingung erfüllt ist, und sonst `0`. Die Notation macht Nenner und Gewichtung eindeutig; der Text nach jeder Formel erklärt dieselbe Berechnung in Funkpraxis-Sprache.

Die Indizes kennzeichnen, wessen Evidenz gezählt wird und zu welchem Bereich sie gehört. Eine Summe zählt beibehaltene Einheiten zusammen; der Median ist der mittlere sortierte Wert, bei gerader Anzahl das Mittel der beiden mittleren Werte. Diese Rechenschritte setzen nicht voraus, dass die Beobachtungen unabhängig sind.

Dieses Kapitel verwendet **Zusammenfassung** oder **deskriptive Kennzahl** für die Raten, Mediane, Anteile und Verteilungen der beibehaltenen Evidenz. Die Unterscheidung ist wichtig, weil ein Wert für die beibehaltenen Zeilen exakt berechnet sein und dennoch nur eine enge oder ausgewählte Population beschreiben kann.

<a id="sec-7-1"></a>
#### 7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell

WSPRadar liest öffentliche WSPR-Meldungen für jeden abgeschlossenen Lauf aus genau einer ausgewählten Datenbank über schreibgeschützte Abfragen. Die Meldungen sind Beobachtungsdaten heterogener Sender, Empfänger, Decoder und Meldesysteme. Ein abgeschlossener Lauf mischt keine Datenquellen; die ausgewählte Datenbank gehört zur Provenienz des Laufs.

Ein **Spot** ist eine gemeldete Zeile eines erfolgreichen Decodes. Ein **WSPR-Zyklus** ist das zweiminütige Intervall, das an einer geraden UTC-Minute beginnt. Analysen im selben Zyklus konsolidieren qualifizierende Zeilen zunächst nach Seite, Peer-Identität und Zyklus und klassifizieren sie erst danach. Die in den Bedienelementen angezeigten effektiven UTC-Grenzen definieren das Analysefenster.

WSPR-2 bezeichnet den zweiminütigen Sendemodus; Typ 1, Typ 2 und Typ 3 beschreiben die Nachrichteninhalte. Erweitertes WSPR kann ein zusammengesetztes Rufzeichen und einen präzisen sechsstelligen Locator über zwei sich ergänzende Aussendungen übertragen. Eine Typ-2-Nachricht überträgt das zusammengesetzte Rufzeichen und die Leistung, jedoch keinen Locator; die zugehörige Typ-3-Nachricht überträgt einen 15-Bit-Hash dieses Rufzeichens, den sechsstelligen Locator und die Leistung. Die beiden Aussendungen liegen in getrennten WSPR-Zyklen; sie sind nicht zwei Felder einer einzigen Datenbankzeile <a href="#ref-12">[Ref-12]</a>.

WSPRadar klassifiziert eine Zeile nicht als Typ 1, Typ 2 oder Typ 3 und verbindet keine sich ergänzenden erweiterten WSPR-Aussendungen über Zyklusgrenzen hinweg. Jede Datenbankzeile gehört zu ihrem gemeldeten Zyklus.

WSPRadar verlangt nicht beide sich ergänzenden Nachrichtenphasen, bevor es eine Einheit desselben Zyklus zulässt; die für den jeweiligen Vergleich benötigten Identitäten müssen in der Datenbank aufgelöst sein. Beim TX-Benchmark müssen die aufgelösten Target- und Referenzzeilen im selben Zyklus von derselben entfernten Empfängeridentität stammen. Übereinstimmende Nachrichtentypen sind keine Zulässigkeitsbedingung: Die gespeicherten Zeilen müssen die geltenden Identitäts-, Zyklus- und Filterregeln erfüllen. WSPRadar verbindet niemals Meldungen aus verschiedenen WSPR-Zyklen zu einem Paar.

Eine erweiterte Folge kann deshalb in einem oder beiden Zyklen Joint Spots beitragen. Ein qualifizierender Joint Spot in einem Zyklus setzt keinen Joint Spot im anderen voraus. Die Empfehlung, bei einem kontrollierten TX-Versuch Nachrichtentypen und Sendezeitpläne aufeinander abzustimmen, verbessert die Vergleichbarkeit der Beobachtungen; sie ist eine Betriebsempfehlung und keine von WSPRadar durchgeführte Nachrichtentypprüfung. [Abschnitt 2.2.1](#sec-3-tx-benchmark-simultaneous) erklärt den praktischen Aufbau.

Die kleinste Evidenzeinheit hängt vom Design ab:

* Performance und Benchmark verwenden eine Peer-Identität in einem zulässigen WSPR-Zyklus.
* Die Referenznachbarschaft bildet zusätzlich zunächst für jeden Zyklus und Funkweg eine Referenz aus qualifizierenden lokalen Identitäten, bevor Target-minus-Referenz-Evidenz entsteht.

Die Zuordnung desselben Zyklus bedeutet denselben zweiminütigen gemeldeten UTC-Slot und dasselbe entfernte Rufzeichen mit vollständigem gemeldeten Locator im selben Band. Sie verlangt keine identischen HF-Frequenzen und beweist keine gleichen physischen Ausbreitungswege; simultane TX-Signale benötigen normalerweise getrennte freie Frequenzen. Nur Joint Spots liefern ΔSNR. Einseitige Evidenz und Both (Async) auf Stationsebene bleiben ohne erfundenes SNR der fehlenden Seite erhalten.

Diese Einheiten werden aus gemeldeten Spots gebildet; sie sind keine zusätzlichen Funkmessungen. Ihr Zweck ist, eindeutig festzulegen, unter welchen Bedingungen ein Erfolg, ein verpasster Decode oder eine gepaarte Differenz gezählt wird.

Der historische Fallback ohne `code = 1` verändert die Auswahl der Quellzeilen nur, wenn die strenge Abfrage keine Target-seitige Evidenz liefert und der gesamte gewählte Zeitraum vor dem 1. Januar 2022 um 00:00 UTC endet. Der Laufstatus dokumentiert den verwendeten Abfrageweg. Die Zulässigkeitsgrenze und die Unsicherheit historischer Modusangaben stehen in [Abschnitt 5.4](#sec-6-4). Verzögerungen und Datenqualitätsgrenzen der Upstream-Quellen stehen in [Abschnitt 5.6](#sec-6-6).

<a id="sec-7-2"></a>
#### 7.2 Identität, Zuordnung und Zeilenkonsolidierung

WSPRadar behandelt gemeldete Identitäten als wissenschaftliche Daten und nicht als bloße Beschriftung.

**Die grundlegende Beobachtung betrifft eine entfernte Station in einem zweiminütigen WSPR-Zyklus.** Die entfernte Station ist bei RX ein Sender und bei TX ein Empfänger. Benchmark vergleicht die Target- und Referenzevidenz für diese entfernte Station innerhalb desselben Zyklus.

Performance und Benchmark behalten nur Zyklen mit beobachtbarer Target-Aktivität bei. Diese Aktivität muss nicht auf jedem einzelnen Funkweg zur entfernten Station beobachtet werden: Evidenz auf einem anderen Funkweg kann belegen, dass das Target im Zyklus aktiv war. [Abschnitt 7.3](#sec-7-3) definiert die Aktivitätsprüfungen und ihre Unterschiede zwischen den Analysen.

Stationsidentitäten werden wie folgt ausgewählt:

| Station oder Rolle | Identifizierung durch WSPRadar |
|---|---|
| **Target — alle Analysen** | Exaktes Empfangsrufzeichen bei RX oder Senderufzeichen bei TX zusammen mit dem vierstelligen Locator des Target-QTH. |
| **Referenz — Referenzaufbau/-station** | Exaktes Referenzrufzeichen zusammen mit seinem aus der Datenbank aufgelösten vierstelligen Locator. |
| **Entfernte Station — alle Analysen** | Exaktes Rufzeichen zusammen mit dem vollständigen gemeldeten Locator: der entfernte Sender bei RX oder der entfernte Empfänger bei TX. |
| **Lokale Beiträge — Referenznachbarschaft** | Lokale Empfängeridentitäten bei RX oder lokale Senderidentitäten bei TX innerhalb des gewählten Radius, unterschieden anhand des exakten Rufzeichens und vollständigen gemeldeten Locators. |

Performance wertet die Beobachtungen und bestätigten Gelegenheiten des Targets für jede entfernte Station und jeden Zyklus aus. Referenzaufbau/-station vergleicht das Target mit einer identifizierten Referenz. Die Referenznachbarschaft bildet ihre Referenz für jede entfernte Station und jeden Zyklus getrennt aus den qualifizierenden lokalen Beiträgen.

Mehrere qualifizierende Meldungen für dieselbe Seite, entfernte Station und denselben Zyklus werden vor der Ergebnisbildung zusammengefasst. So bleibt für diese Seite in diesem Zyklus ein Wert erhalten; Meldungen aufeinanderfolgender Zyklen werden dabei nicht verbunden. Die Regeln zur stärksten Meldung und zum Nachbarschafts-Median werden nachfolgend erklärt.

Für die Auswahl der Target-Zeilen in der Datenbank verwendet WSPRadar Grid-4, auch wenn ein sechsstelliges QTH konfiguriert ist. Das vollständige QTH bleibt für Entfernung, Azimut, Sonnenhöhe und die Geometrie des lokalen Radius relevant. Ein gemeinsames Grid-4 belegt keine physische Ko-Lokation.

Diese Zuordnung verwendet die exakten Rufzeichen- und Locatorfelder der ausgewählten Datenbank. WSPRadar rekonstruiert weder ein zusammengesetztes Rufzeichen aus seinem Hash noch übernimmt es einen Locator aus einem benachbarten Typ-2- oder Typ-3-Zyklus. Eine simultane erweiterte WSPR-Folge kann deshalb in jedem zulässigen Zyklus eine Vergleichseinheit desselben Zyklus je entfernter Empfängeridentität beitragen, wenn beide Seiten in der Datenbank konsistent aufgelöst sind. Ein fehlendes oder anders dargestelltes Rufzeichen beziehungsweise Grid-4 wird nicht durch Schlussfolgerung zulässig.

Wenn mehrere qualifizierende, nicht identische Zeilen dieselbe logische Kombination aus Seite, Peer und Zyklus darstellen, behält WSPRadar den stärksten qualifizierenden normierten SNR als besten beobachteten Wert dieser logischen Identität. Dadurch können exakte Wiederholungen oder schwächere Zweit-Decodes den beibehaltenen Seitenwert nicht absenken. Der Wert ist jedoch kein Zentralwert eines einzelnen physischen Empfängers. Unterschiedliches Mehrfach-Empfänger- oder Meldeverhalten auf beiden Seiten kann deshalb eine Asymmetrie erzeugen. Beim lokalen Nachbarschafts-Median wird stattdessen zunächst innerhalb jeder lokalen Identität ein Median und erst danach über die Identitäten hinweg aggregiert.

**Warum wird die stärkste Meldung beibehalten?** Mehrere Meldungen für dieselbe Station, denselben Peer und denselben WSPR-Zyklus stellen nicht zwangsläufig unabhängige Beobachtungen dar. Entstehen schwächere Meldungen durch sender- oder empfängerseitige Signalrepliken, unerwünschte Spektralkomponenten oder Zweit-Decodes, lässt sich ihr Mittelwert oder Median nicht begründet als SNR des Hauptsignals interpretieren. Das stärkste qualifizierende normierte SNR steht für den besten beobachteten Empfang und verhindert, dass schwächere zusätzliche Meldungen diesen Wert absenken. Diese Meldungen tragen weiterhin nur ein Detektionsergebnis oder eine gepaarte Beobachtung für den jeweiligen Zyklus und Funkweg bei.

Diese Interpretation als bester gemeldeter Empfang entspricht dem dokumentierten Zusammenführen mehrerer Empfänger in WsprDaemon: Liefern mehrere Empfänger Meldungen für dieselbe Aussendung, meldet es das beste SNR an WSPRnet. Dies ist ein Beispiel einer bestehenden Meldepraxis und kein Beleg dafür, dass eine bestimmte gespeicherte Meldung das beabsichtigte Signal darstellt oder beide Vergleichsseiten dieselbe Spektralkomponente ausgewählt haben. <a href="#ref-11">[Ref-11]</a>

Die Auswahl der stärksten Meldung gilt für die SNR-Werte bei Performance, beide Seiten eines simultanen Benchmarks mit fester Referenz und die Target-Seite des lokalen Nachbarschafts-Medians. Bei lokalen Referenzbeiträgen bleiben die Mediane innerhalb jeder Identität und der anschließende Median über die Identitäten erhalten. Diese unterschiedlichen Konstruktionen sind in [Abschnitt 7.7](#sec-7-7) definiert. Mediane und IQR über beibehaltene Beobachtungen bleiben Zusammenfassungen der daraus entstehenden Evidenz und sind von der Auswahl eines SNR-Werts innerhalb eines Zyklus und Funkwegs zu unterscheiden.

Der lokale Pool schließt das Target anhand des exakten Rufzeichens aus. Basisrufzeichen und Rufzeichen mit Suffix sind verschieden, sofern nicht die exakte Target-Form übereinstimmt. Falsche, veraltete oder wechselnde Locator können eine physische Station aufteilen, geografisch verschieben oder den Ausschluss beweglicher Stationen auslösen.

<a id="sec-7-3"></a>
#### 7.3 Konditionierung auf Target-Aktivität und Zulässigkeit

Ein stiller Zyklus ist mehrdeutig: Das Target kann außer Betrieb gewesen sein, oder seine Beteiligung hat keinen gemeldeten Decode erzeugt. WSPRadar zählt Gegen-Evidenz nur in Zyklen mit beobachtbarer Target-Beteiligung. Diese Einschränkung heißt **Konditionierung auf Target-Aktivität**.

Sei $A_c$ der Indikator für beobachtbare Target-Beteiligung im Zyklus $c$:

* TX: Im Zyklus existiert irgendwo mindestens eine qualifizierende Meldung einer Target-Aussendung.
* RX: Der Target-Empfänger hat im Zyklus mindestens einen qualifizierenden Decode hochgeladen.

Performance und simultaner Benchmark konditionieren auf $A_c=1$. Dadurch werden Zeiten ohne beobachtbare Target-Aktivität nicht automatisch zu Gegen-Evidenz, ohne zwischen Ausfallzeit und unbeobachteter Beteiligung zu unterscheiden. Zugleich verändert diese Regel die Analysepopulation: Das Ergebnis beschreibt Zyklen mit beobachtbarer Target-Beteiligung und nicht die gesamte Uhrzeit oder sämtliche geplanten Versuche.

Die Konditionierung ist asymmetrisch. Die Betriebszeit der Referenz bildet kein zweites Gate und muss extern kontrolliert oder dokumentiert werden. Ein Tausch von Target und Referenz kann deshalb zulässige Zyklen und einseitige Decode Outcomes verändern, selbst wenn sich das Vorzeichen des reinen Joint-ΔSNR erwartungsgemäß umkehrt.

Jede Joint-Beobachtung belegt bereits eine Target-Beteiligung. Das Gate verändert daher nicht die ΔSNR-Werte der Joint-Beobachtungen. Es verändert die Population einseitiger oder asynchroner Outcomes und bei Performance den Gelegenheitsnenner.

Target-Aktivität darf global nachgewiesen werden, auch wenn der Peer, der sie belegt, außerhalb des ausgewählten geografischen Analysebereichs liegt. Dieser Peer setzt lediglich $A_c$; er geht nicht in die begrenzten Outcomes, Zusammenfassungen oder Exporte ein.

**Welche Meldungen können Aktivität belegen?** Bei Performance kann eine Target-Meldung mit einem Peer, der später wegen eines speziellen Rufzeichens oder wechselnden Standorts ausgeschlossen wird, weiterhin Aktivität belegen. Bei Benchmark gelten diese Peer-Ausschlüsse bereits vor dem Aktivitätsnachweis; das Target benötigt deshalb eine Meldung mit einem danach noch zulässigen Peer. Der geografische Bereich wird bei beiden Designs erst anschließend angewendet. Belegt nur ein ausgeschlossener Peer die Target-Aktivität eines Zyklus, kann daher eine Performance-Gelegenheit für einen anderen zulässigen Peer erhalten bleiben, aber kein Benchmark-Outcome. Der ausgeschlossene Peer selbst trägt zu keiner der beiden Ergebnispopulationen bei.

<a id="sec-7-4"></a>
#### 7.4 Performance-Analyseziel, Klassifikation und Zusammenfassungsgrößen

Performance beschreibt die Beteiligung des Targets innerhalb beobachtbarer Gelegenheiten der beibehaltenen Peer-Population. Die Größe ist bewusst bedingt: Gefragt wird, was das Target tat, wenn ein erfolgreicher Target-seitiger Decode oder externe Evidenz die erforderliche Endpunktaktivität belegte.

Der Nenner umfasst Erfolge und extern gestützte Misses; er besteht weder aus sämtlichen Uhrzeitzyklen noch ausschließlich aus extern bestätigten Zyklen.

Für Peer $i$ und Target-aktiven Zyklus $c$ sei $T_{i,c}=1$, wenn ein gültiger Target-seitiger Decode vorliegt, und $E_{i,c}=1$, wenn qualifizierende externe Evidenz die Aktivität des Peer-Endpunkts bestätigt. Die gewählten Band-, exakten Peer-Identitäts-, Filter- und geografischen Bereichsregeln gelten, bevor ein Peer-Zyklus eingeht. Erfolg $S_{i,c}$, Gelegenheit $O_{i,c}$ und Miss $M_{i,c}$ sind definiert durch:

$$S_{i,c}=T_{i,c},\qquad O_{i,c}=T_{i,c}\lor E_{i,c},\qquad M_{i,c}=E_{i,c}\land\neg T_{i,c}$$

Jeder gültige Erfolg liefert damit seine eigene Gelegenheit, mit $S_{i,c}\le O_{i,c}$ und $O_{i,c}=S_{i,c}+M_{i,c}$. Die Methodenkennung lautet `opportunity-v3`.

In der Formel bedeutet $\lor$ „oder“, $\land$ „und“ und $\neg$ „nicht“: Eine Gelegenheit benötigt einen Target-Decode oder externe Bestätigung; ein Miss benötigt externe Bestätigung ohne Target-Decode.

* RX-Rollen: Der **Target-RX** empfängt den **Peer-TX**. Die Meldung Peer-TX → Target-RX bestätigt beide Endpunkte und ist ein Erfolg. Eine Meldung Peer-TX → anderer geeigneter RX bestätigt die Sendeaktivität dieses Peer-TX; sie stützt einen Miss nur dann, wenn auch der Target-RX im selben Zyklus nachweislich aktiv ist.
* TX-Rollen: Der **Target-TX** sendet zum **Peer-RX**. Die Meldung Target-TX → Peer-RX bestätigt beide Endpunkte und ist ein Erfolg. Eine Meldung anderer qualifizierender TX → derselbe Peer-RX bestätigt die Empfangsaktivität dieses Peer-RX; sie stützt einen Miss nur dann, wenn auch der Target-TX im selben Zyklus nachweislich aktiv ist.

Ein Target-only-Erfolg hat $T_{i,c}=1$ und $E_{i,c}=0$. Seine Herkunft bleibt als Teilmenge der Erfolge nachvollziehbar; er ist bereits genau einmal in Erfolgs- und Gelegenheitsanzahl enthalten. Externe Bestätigung zusätzlich zu einem Erfolg erzeugt keine weitere Gelegenheit. Sind beide Flags null, reicht die Endpunktaktivität nicht aus: Der Peer-Zyklus bleibt unbekannt und ausgeschlossen. Das Target-Active Gate bleibt unverändert. Aktivität andernorts belegt nicht, dass ein bestimmter stiller Target-RX oder Peer-RX zugehört hat.

| Target-Decode | Externe Evidenz | Erfolg | Gelegenheit | Miss | Deutung |
| :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | 0 | 1 | 1 | 0 | Target-only; Teilmenge der Erfolge |
| 1 | 1 | 1 | 1 | 0 | Extern gestützter Erfolg |
| 0 | 1 | 0 | 1 | 1 | Extern gestützter Miss in einem Target-aktiven Zyklus |
| 0 | 0 | 0 | 0 | 0 | Aktivität unbekannt; ausgeschlossen |

Für einen qualifizierenden Peer werden Gelegenheiten und Target-Erfolge über die beibehaltenen Zyklen gezählt; anschließend werden Erfolge durch Gelegenheiten geteilt:

$$n_i=\sum_c O_{i,c},\qquad h_i=\sum_c S_{i,c}$$

$$r_i=100\%\times\frac{h_i}{n_i}$$

Dabei ist $n_i$ die Zahl bestätigter Gelegenheiten dieses Peers, $h_i$ die Zahl der Target-Erfolge und $r_i$ seine Dekodierrate. Ein Peer trägt nur bei, wenn $n_i$ den konfigurierten Mindestwert erreicht.

Für den geografischen Bereich $g$ mit der qualifizierenden Peer-Menge $I_g$ bezeichnet $|I_g|$ die Zahl qualifizierender Peers. Ihre einzelnen Raten werden addiert und durch diese Peer-Anzahl geteilt; daraus ergibt sich die stationsgleichgewichtete Dekodierrate:

$$R_{station}(g)=\frac{1}{|I_g|}\sum_{i\in I_g} r_i$$

Dies ist das exakte arithmetische Mittel der beibehaltenen Peer-Raten: Jeder qualifizierende Peer erhält unabhängig von seiner Gelegenheitsanzahl eine gleich große Stimme.

Die Dekodierrate auf Gelegenheitsebene lautet:

$$R_{opportunity}(g)=100\%\times\frac{\sum_{i\in I_g}h_i}{\sum_{i\in I_g}n_i}$$

Dies ist der exakte Anteil erfolgreicher Target-Outcomes über alle beibehaltenen Gelegenheiten: Jede Gelegenheit erhält eine gleich große Stimme. Beide Raten sind ergänzende Zusammenfassungen und keine zwei Näherungen an eine einzige „wahre“ Rate. Sie beantworten unterschiedliche Gewichtungsfragen; ihre Abweichung ist aufschlussreich, wenn sich das Evidenzvolumen zwischen den Peers stark unterscheidet.

**Beispiel: ein Ergebnis, zwei Gewichtungsfragen.** Zwei Peers erfüllen bereits die konfigurierte Mindestanzahl an Gelegenheiten. Peer A hat `90 Erfolge / 100 Gelegenheiten = 90%`, Peer B `5 / 10 = 50%`. Bei gleicher Peer-Gewichtung ergeben sich **70 %**. Über alle Gelegenheiten gepoolt sind es `95 / 110`, also **86,4 %**. Der gepoolte Nenner enthält 95 Erfolge und 15 Misses; jede Gelegenheit zählt einmal. Der größere Wert entsteht durch das höhere Evidenzvolumen des erfolgreicheren Funkwegs und macht die Rechnung mit gleicher Peer-Gewichtung nicht falsch.

Die Mindestens-einmal-Reichweite lautet:

$$Reach(g)=100\%\times\frac{|\{i\in I_g:h_i\ge1\}|}{|I_g|}$$

In Funkpraxis-Sprache ist dies der Prozentsatz qualifizierender Peers, bei denen das Target in mindestens einer qualifizierenden Gelegenheit erfolgreich war.

Im Nenner stehen alle qualifizierenden Peers des Bereichs. Ein Peer mit einem Erfolg und ein Peer mit vielen Erfolgen zählen im Zähler jeweils einmal. Die Reichweite beschreibt Breite. Bei einer festen zulässigen Peer-Menge kann zusätzliche Evidenz keinen früheren Erfolg aufheben, solange die bisherige Evidenz erhalten bleibt. Zwischen Läufen kann sich jedoch die qualifizierende Peer-Population ändern; der angezeigte Reichweitenanteil muss deshalb mit längerer Laufdauer nicht steigen. Wie beständig die Funkwege funktionierten, beantwortet die Dekodierrate. Im obigen Beispiel mit zwei Peers beträgt die Reichweite 100 %, obwohl deren Dekodierraten verschieden sind.

Erfolgreiches Target-SNR ist nur definiert, wenn das Target decodiert oder gemeldet wurde, einschließlich Target-only-Erfolgen. Es ist damit eine auf erfolgreiche Decodes bedingte Verteilung. Zugrunde liegen alle beibehaltenen Erfolge nach Zusammenfassung auf die stärkste Meldung und Normierung; die späteren Abschnitte definieren, wie jede Ansicht diese Werte für Mediane, IQR und Extremwerte gruppiert und gewichtet. Dieselbe Klassifikation gilt für Stationsschwellen, beide Gewichtungen der Dekodierrate, Karten, Mindestens-einmal-Reichweite, chronologische und gefaltete Profile, Station Insights, Evidenz der ausgewählten Station, Drill-Down und Exporte. Verpasste Gelegenheiten besitzen kein Target-SNR und erhalten keinen künstlichen Wert. Dekodierrate und erfolgreiches SNR müssen gemeinsam gelesen werden: Ein System, das zusätzliche schwache Signale decodiert, kann die praktische Reichweite verbessern und zugleich den Median der erfolgreichen SNR-Werte absenken.

Das Performance-Analyseziel ist somit die bedingte Beteiligung des Targets unter beobachtbaren Gelegenheiten in der beibehaltenen Population und unter der gewählten Gewichtung. Es ist weder unbedingte Empfängerempfindlichkeit noch die Erfolgswahrscheinlichkeit sämtlicher Sendeversuche oder der absolute Wirkungsgrad der Station.

<a id="sec-7-5"></a>
#### 7.5 Leistungsnormierung, Korrektur und Benchmark-ΔSNR

WSPR meldet SNR auf der WSJT-Skala in dB bezogen auf eine Referenzbandbreite von 2500 Hz und überträgt die gemeldete Sendeleistung in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar bezieht erfolgreiche SNR-Beobachtungen sowohl in RX- als auch in TX-Analysen auf eine gemeinsame gemeldete Sendeleistung von 30 dBm (1 W). So lassen sich gespeicherte Signalpegel nach Herausrechnen des gemeldeten Leistungsunterschieds vergleichen; die Rechnung rekonstruiert keine Decodes, die bei dieser Leistung stattgefunden hätten:

$$SNR_{norm}=SNR_{measured}-P_{TX(dBm)}+30$$

Praktisch wird ein Signal mit 10 dB geringerer gemeldeter Sendeleistung für diesen Vergleich um 10 dB angehoben. Ein mit `-15 dB` gemeldetes SNR bei `20 dBm` wird beispielsweise auf `-5 dB` bei `30 dBm` normiert. Die Rechnung entfernt ausschließlich den **gemeldeten** Leistungsanteil.

Dabei sind $SNR_{measured}$ und $SNR_{norm}$ SNR-Werte in dB; $P_{TX(dBm)}$ ist die für diese Beobachtung gemeldete Sendeleistung. Decode Outcomes und der Gelegenheitsnenner bei Performance bleiben unverändert die tatsächlich beobachteten. Die Normierung korrigiert weder Antennengewinn, Strahlungswirkungsgrad, Speiseleitungsverlust, EIRP, Empfängerkalibrierung noch lokalen Stör- oder Rauschpegel.

Die referenzseitige Korrektur wird addiert:

$$SNR_{R,corr}=SNR_R+C_R$$

Für einen Joint Spot wird das korrigierte Referenz-SNR vom normierten Target-SNR abgezogen:

$$D_{i,c}=\Delta SNR_{i,c}=SNR_{T,i,c}-SNR_{R,corr,i,c}$$

Dabei ist $C_R$ die vorzeichenbehaftete additive referenzseitige Korrektur. In der ersten Gleichung bezeichnen $SNR_R$ und $SNR_{R,corr}$ das Referenz-SNR vor und nach der Korrektur. In der Gleichung für das Paar kennzeichnen die Indizes $i,c$ den Peer und die zugeordnete Evidenzeinheit; $SNR_{T,i,c}$ ist das zugehörige normierte Target-SNR und $SNR_{R,corr,i,c}$ das korrigierte Referenz-SNR. Die konfigurierte Korrektur gehört zur Referenzseite und wird nicht zum Target addiert. Positives $D_{i,c}$ spricht für das Target, negatives für die Referenz. Eine positive Korrektur macht die Referenz vor der Subtraktion stärker und senkt deshalb ΔSNR. Der eingegebene Kalibrierversatz verwendet dasselbe Vorzeichen `target - reference`.

**Vorzeichenprüfung.** Bei normiertem Target-SNR `-10 dB` und Referenz-SNR `-12 dB` beträgt ΔSNR `+2 dB`. Eine Referenzkorrektur von `+1.5 dB` setzt die Referenz auf `-10.5 dB`; ΔSNR beträgt dann `+0.5 dB`. Die Target-Beobachtungen sind unverändert; der Vergleich berücksichtigt den eingegebenen Referenzversatz.

Der Wert $D_{i,c}$ ist eine beobachtete gepaarte Differenz für genau eine beibehaltene Vergleichseinheit. Er wird exakt aus den beiden beibehaltenen SNR-Werten und der gegebenenfalls konfigurierten Korrektur berechnet. Seine Interpretation hängt dennoch davon ab, wofür beide Seiten stehen und wie gut der physische Versuch die übrigen Ketten kontrolliert hat.

Bei RX-Paaren desselben Senders fällt der gemeinsame gemeldete TX-Leistungsanteil heraus. TX-Paare verschiedener Signale hängen unmittelbar von der Richtigkeit der gemeldeten Leistung und von unkorrigierten Unterschieden der Sender- oder Speiseleitungsketten ab. Eine Referenzkorrektur ist nur dann wissenschaftlich vertretbar, wenn der Offset über das relevante Band, den Pegelbereich, den Hardwarezustand und die Zeit näherungsweise additiv und stabil ist.

<a id="sec-7-6"></a>
#### 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen

Benchmark besitzt zwei miteinander verknüpfte Analyseziele:

1. die Verteilung des Target-minus-Referenz-ΔSNR unter **Joint**-Vergleichseinheiten und
2. die Zusammensetzung der beibehaltenen Evidenz aus **Only Target**, **Joint**, **Only Reference** sowie auf Identitätsebene **Both (Async)**.

ΔSNR existiert nur, wenn beide Seiten vergleichbare Evidenz erzeugen. Die Joint-Teilmenge wird daher durch den erfolgreichen Decode beider Seiten ausgewählt. In statistischer Sprache sind die fehlenden Paare normalerweise nicht „zufällig fehlend“: Schwache Signale, Kollisionen, QRM, Decoderverhalten, Leistungsunterschiede und Funkwegbedingungen können alle beeinflussen, ob ein Paar entsteht. In Stationssprache heißt das: Die überlebenden Paare müssen nicht jede Gelegenheit nahe der Decode-Schwelle gleich gut repräsentieren.

Einseitige Evidenz besitzt kein SNR der fehlenden Seite, das rekonstruiert werden könnte. Ihr darf kein künstliches ΔSNR zugewiesen werden, und sie wird nicht als Paar leistungsnormiert. Bei TX Benchmark können unterschiedliche tatsächliche oder gemeldete Leistungen einseitige Outcomes stark beeinflussen, selbst wenn das Joint-ΔSNR normiert ist.

`Both (Async)` bedeutet, dass für eine Identität beibehaltene Evidenz beider Seiten existiert, aber für die betreffende Stationskategorie keine qualifizierende Einheit desselben Zyklus erhalten bleibt. Die Kategorie zeigt eine breitere Beteiligung beider Seiten, trägt jedoch kein gepaartes ΔSNR bei.

Werden Folgen mit zusammengesetzten Rufzeichen verwendet, hängt die Upstream-Identität von Typ 3 von der Auflösung eines 15-Bit-Rufzeichen-Hashs ab. Ein Hash kann unaufgelöst bleiben oder mit einem anderen bekannten Rufzeichen kollidieren. Dadurch kann ein physischer Decode fehlen, falsch identifiziert oder einem falschen Locator beziehungsweise Leistungswert zugeordnet werden. QRP Labs dokumentiert ein beobachtetes Beispiel und den Mechanismus <a href="#ref-19">[Ref-19]</a>.

Findet eine Prüfung nur wenige vereinzelte Fehlzuordnungen unter Zehntausenden von Beobachtungen und keine Häufung nach Target- oder Referenzseite, Folgenphase, Empfänger oder Zeit, können die Medianwerte unverändert oder nahezu unverändert bleiben; dies muss jedoch in der betroffenen Population geprüft werden. Diese Robustheit darf nicht allein aus der Datenmenge abgeleitet werden: Systematische, gehäufte oder asymmetrische Fehlzuordnungen können die Joint-Zulässigkeit, einseitige Decode Outcomes und Stationsmediane verändern, auch innerhalb eines kleinen Segments. WSPRadar kann nur prüfen, ob das konfigurierte exakte Rufzeichen und Grid-4 in der ausgewählten Datenbank vorliegen; es kann nicht beweisen, dass jede Upstream-Hash-Zuordnung physisch korrekt war.

Bei zusammengesetzten Rufzeichen sind deshalb die Datenbank-Vorprüfung und die phasenbezogene Prüfung aus [Anhang B](#sec-simultaneous-tx-setup) erforderlich.

Die Zensierung auf erfolgreiches SNR bei Performance und die Auswahl nach gemeinsamem Decode bei Benchmark sind verschiedene Selektionsprozesse. WSPRadar zeigt Decode Outcomes und Joint-Evidenzanteil, damit die gepaarten ΔSNR-Zusammenfassungen im Verhältnis zur breiteren beibehaltenen Evidenz gelesen und nicht mit der vollständigen Stationspopulation gleichgesetzt werden.

<a id="sec-7-7"></a>
#### 7.7 Aggregationshierarchie und Gewichtung

WSPRadar verwendet eine hierarchische Aggregation: Zuerst wird die Evidenz innerhalb jeder Peer-Identität zusammengefasst, danach über die Peers hinweg. Dadurch kann ein Peer mit hohem Datenvolumen ein stationsgleichgewichtiges Ergebnis nicht allein deshalb dominieren, weil er mehr Beobachtungen gemeldet hat. Zugleich beantworten stationsgleichgewichtete und beobachtungsbezogene Zusammenfassungen bewusst unterschiedliche Fragen.

**Performance**

1. Jeden zulässigen Peer-Zyklus klassifizieren.
2. Alle qualifizierenden Target-Erfolge und extern gestützten Misses nach Peer-Identität zusammenfassen. Target-only-Herkunft als Teilmenge der Erfolge bewahren, ohne sie nochmals zu den Gesamtsummen zu addieren.
3. Die Mindestanzahl an Gelegenheiten anwenden.
4. Für jeden Peer eine Dekodierrate $r_i$ berechnen.
5. Das gleichgewichtete Peer-Mittel $R_{station}$ berechnen.
6. $R_{opportunity}$ als ergänzende, nach Gelegenheiten gewichtete Zusammenfassung beibehalten.

Das erste Ergebnis beschreibt den typischen qualifizierenden Peer bei gleicher Peer-Gewichtung; das zweite die gepoolte beibehaltene Gelegenheits-Population.

<p style="page-break-after: avoid; -pdf-keep-with-next: true;"><strong>Simultaner Benchmark</strong></p>

Zeigt sich die Verschiebung über mehrere Peers oder prägen wenige Funkwege mit vielen Meldungen das Ergebnis? Lies die folgenden Kennzahlen zusammen mit Stationsverteilungen und Anzahlen.

1. Target- und Referenzevidenz nach Peer und Zyklus konsolidieren.
2. Für Joint-Zyklen $D_{i,c}$ berechnen.
3. Die Mindestanzahl an Joint-Evidenz je Peer anwenden.
4. Den Peer-Median berechnen:

    $$m_i=\operatorname{median}_{c}(D_{i,c})$$

5. Für den Bereich $g$ die stationsgleichgewichtete Segmentzusammenfassung berechnen:

    $$M_g=\operatorname{median}_{i\in I_g}(m_i)$$

Dabei ist $m_i$ die typische gepaarte Differenz eines Peers und $M_g$ der Median dieser Peer-Mediane. Jeder qualifizierende Peer trägt somit genau einen Wert zum Segmentergebnis bei. Der Median aller $D_{i,c}$ auf Beobachtungsebene bleibt getrennt erhalten; in dieser Zusammenfassung erhalten Peers mit mehr Joint-Beobachtungen ein größeres Gewicht.

**Veranschaulichendes Beispiel: warum die Ergebnisse abweichen können.** Diese drei Peer-Identitäten erfüllen nach Zuordnung, Korrektur und Filterung bereits die Anforderungen in einem Segment. Jeder Eintrag ist ein eigener beibehaltener Joint-Peer-Zyklus.

| Peer-Identität | Beibehaltene ΔSNR-Werte (dB) | Peer-Median (dB) |
|---|---|---:|
| A | +6, +6, +6, +6, +6, +6 | +6 |
| B | -2, -2 | -2 |
| C | -1, -1 | -1 |

Der stationsgleichgewichtete Median beträgt **-1 dB**: der mittlere Peer-Median in `-2, -1, +6`. Der Median auf Beobachtungsebene beträgt **+6 dB**: Der fünfte und sechste aller zehn sortierten Werte sind jeweils `+6`. Peer A liefert sechs Beobachtungen, aber nur einen Peer-Median. Beide Ergebnisse beschreiben dieselbe Joint-Evidenz mit unterschiedlicher Gewichtung: Prüfe bei Abweichungen die beitragenden Funkwege. Keine der Gewichtungen allein belegt einen Antennenvorteil oder macht aus den Beobachtungen unabhängige experimentelle Wiederholungen.

Bei jedem Benchmark-Design gilt für Gewichtung und Segmentunterstützung dieselbe Stationsidentität: das exakte `Rufzeichen + vollständig gemeldeter Locator`. Jede Identität muss für sich die konfigurierte Mindestzahl an Joint-Evidenz erfüllen. Genau die Identitäten, die jeweils einen Peer-Median beitragen, zählen auch für die Mindestanzahl qualifizierender Stationen pro Kartensegment. Identitäten mit ausschließlich einseitiger Evidenz tragen nicht zu dieser ΔSNR-Unterstützungszahl bei. Dasselbe Rufzeichen mit unterschiedlichen vollständigen Locatorn zählt getrennt, auch wenn beide Locator im selben Grid-4 liegen. Gezählt werden gemeldete Funkwegidentitäten; daraus folgen keine unabhängigen physischen Stationen oder Standorte.

Beispielsweise ergeben zwei qualifizierende Identitäten mit demselben Rufzeichen und den Locatorn `JO31AA` und `JO31AB` bei Peer-Medianen von `+2 dB` und `+4 dB` einen Segmentmedian von `+3 dB` und eine Unterstützungszahl von `2`. Bei einer Mindestanzahl von zwei qualifizierenden Stationen bleibt dieses Segment erhalten; bei einer Mindestanzahl von drei nicht.

<p style="page-break-after: avoid; -pdf-keep-with-next: true;"><strong>Referenznachbarschaft (Lokaler Median)</strong></p>

Für jeden entfernten Peer-Zyklus berechnet WSPRadar zunächst je aktiver lokaler Identität aus `Rufzeichen + Locator` genau einen normierten SNR-Beitrag und danach den exakten Median über die beitragenden lokalen Identitäten. Eine nicht beobachtete lokale Identität wird weggelassen und nicht mit null angesetzt. Die Referenzkorrektur wird vor der Aggregation des lokalen Pools angewendet. Anschließend wird das Target mit diesem zyklus- und funkwegspezifischen Median verglichen; daraus entstehen Peer- und Segmentmediane des ΔSNR.

Gehören mehrere qualifizierende Meldungen zu derselben lokalen Referenzidentität, demselben entfernten Peer und demselben Zyklus, bilden ihre normierten SNR-Werte zunächst einen Median innerhalb dieser Identität. Jede beitragende lokale Identität liefert danach genau einen Wert für den Nachbarschafts-Median. Die bestehende Zusammenführung auf der Target-Seite behält das stärkste qualifizierende normierte SNR; die Nachbarschaftsmethode führt Meldungen auf beiden Seiten daher nicht nach derselben Regel zusammen.

Eine lokale Identität besteht aus Rufzeichen und vollständig gemeldetem Locator. Die gleiche Gewichtung dieser Identitäten garantiert keine gleiche Gewichtung unabhängiger physischer Standorte: Mehrere Meldeidentitäten können Geräte oder einen Standort teilen.

Es gibt keine gesonderte Mindestzahl lokaler Beitragender pro Peer-Zyklus. Bei einem Beitrag entspricht die Referenz dessen Wert. Ohne Beitragende steht weder ein Referenz-SNR noch gepaartes ΔSNR zur Verfügung. Die an anderer Stelle geltenden Anforderungen an die Mindestmenge gemeinsamer Evidenz und stützender Stationen legen keine Mindestgröße der Nachbarschaft fest.

**Eine andere Zusammensetzung kann den Vergleich verändern.** Drei lokale Identitäten liefern beispielsweise korrigierte SNR-Werte von `-18, -12, -6 dB`; ihr Referenzmedian beträgt `-12 dB`. Bei unverändertem Target-SNR von `-10 dB` ergibt sich ΔSNR `+2 dB`. Fehlt in einem anderen Zyklus der Beitrag von `-6 dB`, während die übrigen Werte gleich bleiben, beträgt der Referenzmedian `-15 dB` und ΔSNR `+5 dB`. Diese Verschiebung erfordert keine Änderung am Target, sondern entsteht aus der veränderten lokalen Population.

Der Nachbarschafts-Median beschreibt qualifizierende gemeldete Beobachtungen. Fehlende Meldungen sind keine Messungen von null SNR, und die beitragende Gruppe kann sich je nach entferntem Peer und Zyklus ändern. Mehr Beobachtungen beseitigen für sich genommen weder systematische Meldeunterschiede noch Selektionseffekte oder Abhängigkeiten zwischen Beobachtungen.

Mediane verringern die Empfindlichkeit gegenüber einzelnen Extremwerten, quantisierten SNR-Ausreißern und duplikatähnlichen Häufungen. Sie beseitigen weder systematische Kalibrierfehler noch Ausbreitungsverzerrungen oder Abhängigkeiten zwischen Zyklen und Stationen.

<a id="sec-7-8"></a>
#### 7.8 Geografische, zeitliche und funkwegbezogene Zusammenfassungen

<a id="sec-7-8-1"></a>
##### 7.8.1 Geografische Zusammenfassungen

Der Segment-Inspektor beginnt mit der vollständigen qualifizierenden Peer-Population im aktiven beibehaltenen Bereich. Tabellensortierung, Zeilenauswahl und Sichtbarkeitsbedienelemente verändern diese Zusammenfassungen nicht.

Performance-Entfernungsprofile gruppieren Peers nach der exakt berechneten Entfernung vom Target-QTH. Abhängig von der aktiven Entfernungsspanne wird deterministisch eine Breite von `125`, `250`, `500` oder `1.000 km` gewählt. Die Grenzen sind an ganzzahligen Vielfachen ab `0 km` verankert; die letzte ausgewählte Obergrenze ist eingeschlossen. Getrennte ausgewählte Bereiche behalten fehlende Lücken, statt sie als Null-Evidenz zu behandeln.

Für jedes Entfernungs-Bin berechnet WSPRadar:

* die Mindestens-einmal-Reichweite;
* die stationsgleichgewichtete Dekodierrate;
* die Dekodierrate auf Gelegenheitsebene und
* das erfolgreiche Target-SNR, zunächst auf einen Median je Peer reduziert und danach über diese Peer-Mediane zusammengefasst.

Für die Streuung des erfolgreichen SNR liefern mindestens drei Peer-Mediane einen Interquartilsabstand, zwei ein Min-Max-Intervall und einer einen einzelnen Punkt. Peers mit ausschließlicher Gegen-Evidenz erhalten kein künstliches SNR. Die Entfernung übernimmt die Genauigkeit des gemeldeten Maidenhead-Locators und ist keine vermessungsgenaue Position.

Geografische Benchmark-Zusammenfassungen verwenden je qualifizierender Identität genau einen Peer-Median des ΔSNR und danach den Segmentmedian dieser Peer-Mediane. Das ΔSNR auf Beobachtungsebene bleibt als getrennt gewichtete Verteilung verfügbar. Die erste Sicht beantwortet „Was zeigte der typische qualifizierende Peer?“, die zweite „Was zeigten die beibehaltenen gepaarten Beobachtungen, wenn jedes Paar zählt?“.

<a id="sec-7-8-2"></a>
##### 7.8.2 Abdeckung der Benchmark-Evidenz

Der Joint-Evidenzanteil beantwortet, welcher Anteil der beibehaltenen Benchmark-Evidenz einen SNR-Vergleich beider Seiten ermöglicht. Sein Nenner umfasst alle drei Outcomes, nicht nur Joint Spots und nicht sämtliche geplanten Zyklen.

Für Station $i$ im Bin $b$ seien die Anzahlen Only Target, Joint und Only Reference $T_{i,b}$, $J_{i,b}$ und $R_{i,b}$ mit:

$$N_{i,b}=T_{i,b}+J_{i,b}+R_{i,b}$$

Eine beitragende Station liefert eine aufgeteilte Stützungsstimme:

$$v_{T,i,b}=\frac{T_{i,b}}{N_{i,b}},\qquad v_{J,i,b}=\frac{J_{i,b}}{N_{i,b}},\qquad v_{R,i,b}=\frac{R_{i,b}}{N_{i,b}}$$

Praktisch erhält jeder Peer insgesamt eine Stationsstimme, die entsprechend seiner Mischung aus Only Target, Joint und Only Reference in diesem Bin aufgeteilt wird.

Der stationsgleichgewichtete Joint-Evidenzanteil lautet:

$$JES_{station}(b)=100\%\times\operatorname{mean}_{i}\left(\frac{J_{i,b}}{N_{i,b}}\right)$$

Der Joint-Evidenzanteil auf Outcome-Ebene lautet:

$$JES_{outcome}(b)=100\%\times\frac{\sum_iJ_{i,b}}{\sum_iN_{i,b}}$$

Die erste Größe gibt jedem beitragenden Peer dasselbe Gewicht, die zweite jeder beibehaltenen Vergleichseinheit.

Bei der ersten werden also zunächst die Joint-Anteile der einzelnen Peers berechnet und anschließend gemittelt; bei der zweiten werden zuerst alle Outcomes zusammengezählt und dann der Joint-Anteil gebildet.

Es tragen nur Peers mit mindestens einem beibehaltenen Outcome in diesem Bin bei; ein Peer ohne Evidenz liefert keinen Anteil. Die drei Anteile eines Peers ergeben zusammen eine Stützungsstimme. Der Joint-Evidenzanteil misst die Paarbarkeit – also welcher Anteil der beibehaltenen Evidenz zu ΔSNR beitragen kann. Er ist keine Gewinnquote des Targets.

Unter dem Target-Active Gate sind Only Target und Only Reference gerichtet und asymmetrisch. Einseitige Evidenz besitzt weiterhin kein ΔSNR.

<a id="sec-7-8-3"></a>
##### 7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung

Chronologische Ansichten bewahren die tatsächliche Reihenfolge des Laufs über das vollständige ausgewählte UTC-Zeitfenster mit der gewählten Zeit-Bin-Breite. Die Bins beginnen am ausgewählten Startzeitpunkt; das abschließende Intervall kann kürzer sein, und Zeitabschnitte ohne Evidenz bleiben leer, statt zu 0 dB zu werden. UTC-Stunden-Ansichten **falten** die Evidenz, indem Beobachtungen verschiedener Tage auf dieselbe 24-Stunden-UTC-Uhr ausgerichtet werden. Die chronologische Sicht fragt damit „Was änderte sich während dieses Laufs?“, die gefaltete Sicht „Kehrte ein Muster zu einer bestimmten UTC-Stunde an mehreren berücksichtigten Tagen wieder?“.

Die angebotenen chronologischen Breiten richten sich nach der vollständigen Laufdauer und nicht nach der beobachteten Evidenzspanne: Läufe bis 6 Stunden verwenden standardmäßig `10m`, längere Läufe bis 24 Stunden `30m` und Läufe über 24 Stunden `12h`. [Abschnitt 4.5](#sec-5-5) führt die vollständigen Angebote einschließlich `2h` in jeder Dauerstufe auf.

Die Abweichung des erfolgreichen Performance-SNR vergleicht jeden Funkweg mit seinem eigenen üblichen erfolgreichen Pegel in diesem Lauf; dauerhaft starke Funkwege bestimmen deshalb nicht den Nullpunkt schwächerer Funkwege. Ein Peer geht nur dann in die Anomaliepopulation ein, wenn er im vollständigen Laufzeitfenster mindestens drei erfolgreiche normierte Target-SNR-Beobachtungen besitzt. Seine Basislinie ist der Median dieser Erfolge. Jede erfolgreiche Beobachtung trägt bei:

$$A_{i,c}=SNR_{i,c}-\operatorname{median}_{c'}(SNR_{i,c'})$$

Dabei kennzeichnet $c$ die aktuelle erfolgreiche Beobachtung; $c'$ durchläuft alle erfolgreichen Beobachtungen des Peers $i$ im vollständigen Laufzeitfenster, aus denen seine Basislinie entsteht. `0 dB` bedeutet damit „auf dem für diesen Funkweg üblichen erfolgreichen Pegel“ und nicht Target–Referenz-Gleichheit. Ein positiver Wert bedeutet, dass dieser erfolgreiche Decode stärker als der für diesen Peer übliche erfolgreiche Pegel im Lauf war; ein negativer Wert bedeutet schwächer. Es handelt sich um eine Abweichung innerhalb eines Funkwegs und nicht um Target-minus-Referenz-ΔSNR.

Chronologisch trägt jeder Peer je ausgewähltem Bin höchstens einen Median der Abweichung bei. In der UTC-gefalteten Sicht trägt jeder Peer zunächst je Datum und UTC-Stunde einen Median bei; erst danach werden diese Peer-Datum-Stunden-Werte über die gefaltete Population zusammengefasst. Innerhalb einer Kombination aus Peer, Datum und Stunde erhöhen zusätzliche Zeilen das Gewicht nach dieser Medianbildung nicht. Peers an mehr Tagen und Tage mit mehr Peers liefern aber weiterhin mehr Werte für die gefaltete Population; es handelt sich nicht um eine über den vollständigen Lauf gleiche Gewichtung der Peers oder Tage.

Die zeitliche Performance-Stützung verwendet dieselben qualifizierenden Peers, behält aber alle bestätigten Gelegenheiten einschließlich der Peers, die aus der erfolgreichen SNR-Anomalieebene ausgeschlossen sind. In einem chronologischen Bin liefert jeder Peer eine nach seiner Dekodierrate im Bin aufgeteilte Stimme. Die gesamte Stationsstützung entspricht damit der Zahl beitragender Peers; das Teilungsverhältnis reproduziert die stationsgleichgewichtete Rate. Die Gelegenheitsstützung ist die rohe Zahl bestätigter Gelegenheiten; ihr Teilungsverhältnis reproduziert die Dekodierrate auf Gelegenheitsebene.

Für jede gefaltete UTC-Stunde ist die Stationsstützung die durchschnittliche Zahl unterschiedlicher Peer-Datum-Stunden-Präsenzen über die berücksichtigten Tage, deren Stundenslot das Analysefenster überlappt. Die gefaltete stationsgleichgewichtete Rate entsteht, indem die Outcomes jedes Peers zu dieser UTC-Stunde über die berücksichtigten Tage gepoolt, daraus je Peer eine Rate berechnet und anschließend jeder Peer gleich gewichtet wird. Gefaltete Gelegenheitsanzahlen sind gepoolte Outcome-Summen geteilt durch den zugehörigen Nenner berücksichtigter Tage.

Bei Performance ist ein **berücksichtigter UTC-Tag** ein Datum, an dem im aktiven Bereich und ausgewählten Fenster mindestens eine qualifizierende bestätigte Gelegenheit existiert. Eine im Fenster liegende Datum-Stunde ohne Evidenz trägt für einen berücksichtigten Tag null bei; eine Datum-Stunde außerhalb des Fensters wird ausgeschlossen. Eine nur teilweise überlappende erste oder letzte Stunde zählt als ein vollständiger berücksichtigter Slot und wird nicht nach Expositionsanteil gewichtet. Dadurch können Mittelwerte an Randstunden niedriger ausfallen. Die UTC-Stunden-Faltung erfordert mindestens zwei berücksichtigte Tage.

Das zeitliche Benchmark-ΔSNR verwendet beibehaltene Joint-Beobachtungen. Wenn keine gepaarten Werte verbleiben, zeigt das ΔSNR-Panel weiterhin das vollständige ausgewählte UTC-Zeitfenster und weist auf die fehlende gepaarte Evidenz für Δ SNR hin. Das bedeutet, dass im dargestellten Bereich keine beibehaltene Joint-Beobachtung verbleibt; daraus folgt nicht, dass die Datenquelle keine Beobachtungen lieferte, und die zeitliche Abdeckung kann weiterhin einseitige Outcomes zeigen. Chronologische Bins fassen gepaarte Werte in tatsächlicher Zeit zusammen; UTC-Stunden-Bins fassen dieselbe gepaarte Population nach Stunde über die Tage zusammen, die in der beibehaltenen Benchmark-Evidenz vertreten sind. Die zeitliche Benchmark-Abdeckung verwendet alle beibehaltenen Einheiten Only Target, Joint und Only Reference sowie die beiden oben definierten Zusammenfassungen des Joint-Evidenzanteils. Auch die Benchmark-Faltung erfordert mindestens zwei Tage mit Evidenz.

<a id="sec-7-8-4"></a>
##### 7.8.4 Zusammenfassungen für den ausgewählten Funkweg

Die Evidenz der ausgewählten Station filtert den aktiven beibehaltenen Bereich auf genau eine Peer-Identität, ohne die vorgelagerte Analysepopulation zu verändern.

Bei Performance zeigt der ausgewählte Funkweg:

* das tatsächliche normierte erfolgreiche Target-SNR in chronologischen Bins;
* je berücksichtigtem Datum und UTC-Stunde einen Median im gefalteten SNR-Profil;
* Anzahlen erfolgreicher und Gegen-Gelegenheiten sowie
* die Dekodierrate im Zeitverlauf.

Bei genau einem Peer sind die stationsgleichgewichtete Dekodierrate und die Dekodierrate auf Gelegenheitsebene innerhalb eines belegten Bins numerisch identisch, weil beide dieselben Erfolge und Gelegenheiten dieses einen Peers verwenden. Die getrennten Stützzahlen unterscheiden dennoch Funkwegpräsenz von Evidenzvolumen.

Bei Benchmark zeigt der ausgewählte Funkweg das ΔSNR jeder Joint-Einheit auf Beobachtungsebene und getrennt die Abdeckung durch Only Target, Joint und Only Reference. Ein Wechsel des ausgewählten Funkwegs oder Darstellungs-Bins verändert nur die Ansicht der beibehaltenen Evidenz, nicht die vorgelagerte Zuordnung, Zulässigkeit oder Aggregation.

Der Drill-Down kann dieselbe Evidenz des ausgewählten Funkwegs vor Anwendung gewöhnlicher Tabellenfilter vorübergehend auf ein zentriertes Intervall von `1h`, `3h`, `6h`, `12h` oder `24h` begrenzen. Sein fokussiertes Messwertrezept behält je nativer Koordinate eine wissenschaftliche Einheit: beim simultanen Benchmark einen zusammengeführten Joint Spot mit tatsächlichem ΔSNR zur kanonischen Zykluszeit, bei Performance eine erfolgreiche bestätigte Gelegenheit mit tatsächlichem normiertem Target-SNR zur kanonischen Zykluszeit. „Nativ“ bezeichnet damit verarbeitete beibehaltene Evidenz nach Zusammenführung, Zuordnung und wissenschaftlichen Filtern und keine unveränderten Provider-Zeilen. Das fokussierte Messwertrezept enthält weder Mediane oder Quartile zeitlicher Bins noch Dichtegitter, Farbskala, Median des vollständigen Laufs oder gefaltetes Profil. Ergänzende Outcome- beziehungsweise Abdeckungspanels dürfen ihre chronologische Aggregation beibehalten; Segment- und ausgewählte Funkwegrezepte über das vollständige Fenster bleiben unveränderte Dichtezusammenfassungen.

Der kandidatenverknüpfte **`Ausreißerfokus`** verwendet die vollständige beibehaltene Flanke vor dem Ereignis, die geschützte vorläufige Episode und die Flanke danach und darf länger als 24 Stunden sein. Das Benchmark-Overlay verwendet das bereits abgeschlossene Detektormodell, statt auf der fokussierten Teilmenge erneut zu erkennen.

Für jeden gemeldeten Kandidaten, der das Fokusfenster schneidet, markiert es mit demselben `*` jede native Einheit, die gegen die endgültige Baseline und robuste Streuung dieses Kandidaten einzeln sowohl $D_{\min}$ als auch $Z_{\min}$ erfüllt; schwächere gruppierte Einheiten, die zwischen starken Ankern beibehalten werden, bleiben normale Punkte.

Ein dezentes Band **Fokussierte Episode** unterscheidet das berichtete Intervall der beibehaltenen Evidenz des ausgewählten Kandidaten. Der Renderer erweitert jedes Ende um eine halbe Breite der nativen Evidenzeinheit und schneidet das Band am Fokusfenster ab; dadurch bleibt ein Impuls aus einer Einheit sichtbar, ohne eine unbeobachtete physische Dauer oder ein Konfidenzintervall darzustellen.

Erwartetes lokales ΔSNR über den Fokus, die Mediane der Flanken davor und danach über deren jeweilige Stützintervalle, symmetrische Hilfsgrenzen für robuste z-Beträge 1, 2, 3 und $Z_{\min}$ sowie die Grenze der absoluten Abweichung $D_{\min}$ gehören ausschließlich zu dieser fokussierten Episode; ein anderer markierter Kandidat kann eine andere Baseline und robuste Streuung besitzen. Aus der Detektordefinition in [Abschnitt 7.11](#sec-7-11) folgt: Eine Hilfsgrenze des Betrags `k` liegt bei der lokalen Baseline plus oder minus `k × robuste Streuung / 0,6745`. Diese Linien visualisieren Detektorkoordinaten; sie sind weder Standardabweichungen oder Konfidenzintervalle noch eigenständige Qualifikationstests, und das Überschreiten einer einzelnen Hilfslinie reicht nicht zur Qualifikation eines Kandidaten.

Fokusauswahl und Kandidatenprovenienz sind ausschließlich Darstellungszustand; sie verändern weder den abgeschlossenen Analysekontext, die Zuordnung, Zulässigkeit oder Detektorergebnisse oder Provider-Abfrage noch gespeicherte Konfiguration oder öffentliche URL.

<a id="sec-7-8-5"></a>
##### 7.8.5 Deskriptive Streuung und Visualisierungstransformationen

Der IQR zeigt die mittlere Hälfte der beitragenden Werte; Min-Max zeigt deren vollständige Spannweite. Dies sind deskriptive Streuungsmaße und keine Konfidenzintervalle. Zeitliche IQR-Bänder erfordern mindestens fünf beitragende Werte im jeweiligen Bin; der Median bleibt auch bei weniger Werten sichtbar. Leere Bins bleiben fehlend und werden nicht zu künstlichen Nullbeobachtungen.

Was als beitragender Wert zählt, hängt von der Ansicht ab: ein Joint Spot, eine einzelne erfolgreiche normierte Target-SNR-Beobachtung, ein Peer-Median je Bin oder ein Peer-Median je Datum und Stunde gemäß den obigen Definitionen. Für Performance-Entfernungsprofile gilt die gesonderte Drei-Peer-Regel aus [Abschnitt 7.8.1](#sec-7-8-1).

**Dichte und Achsenabstände lesen.** Dichtefarben zeigen, wo sich Werte innerhalb eines Panels häufen; Stützzahlen geben das Evidenzvolumen an. Benchmark-Achsen können die Randbereiche stauchen: Lies deshalb die beschrifteten dB-Koordinaten, statt eine Differenz aus ihrer Bildhöhe abzuleiten. Die folgenden exakten Transformationen verändern die Darstellung, nicht die beibehaltenen Beobachtungen oder deren Mediane und Quartile.

**Dichtezellen und Korrektur.**

Benchmark-Histogramme verwenden normalerweise 1-dB-Klassen, 0,5 dB nur bei einem klaren Halb-dB-Raster und gröbere Klassen bei großen Wertebereichen, damit die Bin-Anzahl begrenzt bleibt. Zeitliche Benchmark-Dichtezellen bleiben 1 dB hoch und folgen der angewandten Referenz-SNR-Korrektur. Für das korrigierte ΔSNR `d` und die numerische Korrektur `c` lautet die ideale Zuordnungsregel in der unkorrigierten Vergleichskoordinate `k = floor(d + c + 0.5)`; die folgende numerische Konvention wertet diese Koordinate mit 0,1 dB Auflösung aus. Zelle `k` ist bei `k - c` zentriert und umfasst das halboffene Intervall `[k - 0.5 - c, k + 0.5 - c)`: Die untere Grenze gehört zur Zelle, die obere zur nächsten Zelle, auch bei negativen Werten. Die Addition von `c` zur Bestimmung der Zugehörigkeit ist ausschließlich eine Koordinatentransformation; sie wendet die Korrektur nicht erneut auf die gespeicherten Beobachtungen, Mediane oder Quartile an. Bei derselben beibehaltenen Population verschiebt eine Änderung von `c` das Dichtegitter gemeinsam mit den korrigierten Beobachtungen; Belegungszahlen der Zellen und Farben der relativen Dichte bleiben erhalten. Nicht ganzzahlige Beobachtungen, einschließlich Vergleichen mit dem lokalen Median, müssen nicht in den Zellzentren liegen.

**Numerische Zellzuordnung.** Ausschließlich für die Zellzuordnung wird `d + c` vor Bestimmung der ganzzahligen Zell-ID auf das nächste Zehntel Dezibel gerundet; bei einem exakten halben Zehntel wird das gerade Zehntel gewählt. Ein ausschließlich an diesen Rundungsmittelpunkten wirksamer Float64-Rundungsfehlerbereich verhindert, dass Korrekturrauschen unterschiedliche Zehntel auswählt. Damit ist die Auflösung der Zuordnung ausdrücklich auf 0,1 dB begrenzt; numerisches Rauschen wie `-0.7000000000000028` bei einem korrigierten Wert, der bei `-0,7 dB` erwartet wird, wird aufgefangen. Unterschiede unterhalb dieser Zuordnungsauflösung können derselben Zelle zugewiesen werden. Exakte Halb-dB-Koordinaten bei dieser Auflösung gehören zur oberen Zelle, auch bei negativen Werten. Die ursprünglichen korrigierten Beobachtungen und ihre Statistiken werden durch diese Gitterkonvention nicht gerundet. Eine nicht ganzzahlige Beobachtung mit voller Präzision kann deshalb bis zu 0,05 dB außerhalb der zugewiesenen Zellgrenze liegen; der Achsenbereich umfasst weiterhin die Beobachtung selbst. Diese zeitliche Darstellungskonvention ersetzt die Ganzzahlrundung zur nächsten geraden Zahl bei Gleichstand; deshalb können sich Zuordnungen exakt auf Halb-dB-Grenzen auch ohne Korrektur ändern. Gewöhnliche Histogramme, Performance-Ansichten und Drill-Down-Abbildungen mit nativen Einzelpunkten bleiben unverändert. Jedes Dichtepanel wird unabhängig normiert:

$$D_{relative}=100\times\frac{n_{cell}}{\max(n_{cell,panel})}$$

Dabei ist $n_{cell}$ die Evidenzanzahl in einer Dichtezelle. Die Division durch die am stärksten belegte Zelle wandelt das Panel in eine Darstellung der relativen Dichte um, ohne die zugrunde liegenden Anzahlen zu verändern.

`100` bezeichnet damit die am stärksten belegte Zelle dieses Panels und nicht 100 % der gesamten Evidenz. Dichtefarben erlauben keinen Vergleich des absoluten Evidenzvolumens zwischen unabhängig normierten Panels; dafür sind die Stützzahlen maßgeblich.

**Achse um den Median.** Zeitliche Benchmark-Ansichten und Histogramme verwenden eine rein darstellungsbezogene monotone Skala, die um den Bereichsmedian $M$ zentriert ist. Bei großer Spannweite liegen gleichmäßige visuelle Schritte bei $M$, $M\pm3$, $M\pm6$, $M\pm10$, $M\pm20$ und $M\pm30$ dB; ein Randanker liegt bei $M\pm60$ dB und wird bei Bedarf fortgesetzt. Wenn jede erforderliche Abweichung höchstens `10 dB` beträgt, lauten die engeren Anker $M$, $M\pm1$, $M\pm3$, $M\pm6$ und $M\pm10$ dB; Fortsetzungsanker liegen bei $M\pm20$ und $M\pm40$ dB. Der erforderliche Bereich umfasst die zutreffenden Rohgrenzen des Histogramms beziehungsweise die durch die Korrektur verschobenen zeitlichen Zellgrenzen, eine Mindesthalbspanne von `3 dB` und den absoluten Wert `0 dB`, damit Target-Referenz-Gleichheit sichtbar bleibt. Die Ankerabbildung verändert ausschließlich die dargestellten Abstände: Rohe ΔSNR-Werte, Bin-Zuordnung, Anzahlen, Mediane und Quartile bleiben unverändert. Wegen der nichtlinearen vertikalen Abbildung ist die **Balkenlänge** entlang der Prozentachse – nicht die dargestellte Fläche – die quantitative Kodierung.

Performance-Ansichten des erfolgreichen SNR bleiben auf einer linearen dB-Achse.

<a id="sec-7-9"></a>
#### 7.9 Geografie, Sonnenstandsklassifikation und Populationsfilter

Entfernung und Azimut werden aus dem konfigurierten Target-QTH und den gemeldeten Peer-Locators mit einem kugelförmigen Erdradius von 6371 km berechnet. Die Karte verwendet eine azimutal äquidistante Projektion mit Target-QTH als Mittelpunkt, radialen Grenzen bei 2500, 5000, 10000, 15000, 20000 und 22000 km sowie 22,5-Grad-Azimutsektoren.

Gemeldete Locator repräsentieren Locator-Felder und keine vermessenen Antennenkoordinaten. Geografische Zusammenfassungen sind mit diesen Eingaben intern konsistent, dürfen aber nicht als vermessungsgenaue Position oder direkte Messung des Abstrahlwinkels interpretiert werden.

`Maximale Peer-Entfernung vom Target (km)` entfernt Peers an oder jenseits der gewählten Entfernung vor der wissenschaftlichen Aggregation und dem Export verarbeiteter Evidenz. Kartensegmente, Stützzahlen, Segment-Inspektor und Exporte verwenden damit dieselbe beibehaltene Peer-Population. Inspektor-Auswahlen können diese Population eingrenzen, aber keine ausgeschlossenen Zeilen wiederherstellen.

Zwei Regeln liegen vor diesem geografischen Bereich:

* Die Konditionierung auf Target-Aktivität bleibt global. Ein Peer außerhalb des Bereichs kann den Betrieb des Targets belegen, ohne selbst zu einem begrenzten Outcome zu werden.
* Ist der Ausschluss beweglicher Stationen aktiviert, werden Rufzeichen mit wechselndem Standort in der ansonsten zulässigen globalen Population erkannt, bevor der Entfernungsbereich angewendet wird.

Die Sonnenstandsklassifikation verwendet die Sonnenhöhe am Target-QTH. Evidenz desselben Zyklus verwendet den Zykluszeitstempel.

Sie bezeichnet die Bedingungen am Target, nicht die Beleuchtung des gesamten Ausbreitungswegs oder jedes entfernten Endpunkts.

Die Zeilengrenze der Datenbank und die Bedienelemente, mit denen sich die abgerufene Population verkleinern lässt, sind betriebliche Fragen aus [Abschnitt 5.6](#sec-6-6). Sie verändern die wissenschaftlichen Zusammenfassungen nicht, nachdem die beibehaltene Population gebildet wurde.

<a id="sec-7-10"></a>
#### 7.10 Abhängigkeit, Unsicherheit und Geltungsbereich der Validierung

Die Formeln dieses Kapitels berechnen exakte deskriptive Zusammenfassungen der beibehaltenen Evidenz. Unsicherheit entsteht, wenn daraus Aussagen über nicht beobachtete Bedingungen, künftige Läufe, eine breitere Stationspopulation oder eine physische Ursache abgeleitet werden.

WSPRadar-Beobachtungen sind geclustert und nicht unabhängig. In gewöhnlicher Stationssprache sind 1.000 Spots nicht dasselbe wie 1.000 voneinander unabhängige Experimente. Wiederholte Zyklen eines Peers teilen Hardware- und Funkwegeigenschaften; Stationen in benachbarten Regionen teilen Ausbreitungsbedingungen; Zeit-Bins sind autokorreliert; und ein einzelnes ionosphärisches Ereignis oder eine Störung kann viele Beobachtungen gleichzeitig beeinflussen. Eine große Zeilenzahl ist daher keine unabhängige Stichprobengröße.

Entsprechende Typ-2- und Typ-3-Positionen innerhalb einer Folge können die Evidenztiefe erhöhen, weil jede eine native Vergleichseinheit desselben Zyklus bleibt. Sie liegen jedoch zeitlich eng beieinander, sind voneinander abhängig und dürfen nicht als unabhängige Wiederholungen oder experimentelle Wiederholbarkeit bezeichnet werden. Wiederholbarkeit erfordert einen getrennten, geeignet kontrollierten Lauf.

Stationsgleichgewichtung verringert die Dominanz besonders aktiver Peers, und Mediane verringern die Empfindlichkeit gegenüber einzelnen Ausreißern. Beides erzeugt weder Unabhängigkeit noch beseitigt es systematische Verzerrungen oder liefert eine Stichprobenverteilung. IQRs beschreiben die Streuung innerhalb des Laufs und sind keine Unsicherheitsintervalle.

WSPRadar berichtet derzeit deskriptive Zusammenfassungen. Es passt nicht automatisch ein Stichproben- oder Abhängigkeitsmodell an und berechnet weder Standardfehler, Konfidenzintervalle, p-Werte, Teststärke noch kausale Effekte. Naive Inferenzrechnungen, die jeden Spot oder jedes Paar als unabhängig behandeln, würden die Unsicherheit im Allgemeinen unterschätzen.

Wissenschaftliche Unterstützung sollte deshalb auf mehreren Ebenen beschrieben werden:

* **Evidenztiefe:** Zahl der Gelegenheiten, Joint-Einheiten;
* **Evidenzbreite:** Zahl und geografische Vielfalt der Peer-Identitäten;
* **Konsistenz innerhalb eines Laufs:** Übereinstimmung der stationsgleichgewichteten, beobachtungsbezogenen, geografischen und zeitlichen Zusammenfassungen;
* **experimentelle Wiederholbarkeit:** erneutes Auftreten in einem neuen, geeignet kontrollierten Lauf und
* **experimentelle Kontrolle:** zur Aussage passende Kalibrierung, Kreuztausch, vertauschter Zeitplan oder unabhängige Messung.

Diese Ebenen machen aus den beibehaltenen Zusammenfassungen keine kalibrierten Vorhersagen. Sie zeigen, wie viel Evidenz eine begrenzte deskriptive oder vergleichende Aussage stützt und wie gut der physische Versuch eine Zuordnung zur vermuteten Ursache trägt.

Übereinstimmung mehrerer Ansichten desselben Laufs ist nützliche interne Konsistenz, aber keine unabhängige Wiederholung. Für stärkere Aussagen bleiben ein gesonderter kontrollierter Lauf und der Versuchsaufbau entscheidend; [Kapitel 8](#sec-8) enthält passende Berichtsformulierungen.

Empirische Prüfungen der Softwarevalidierung sind keine zeitlosen Methodendefinitionen. Jede angeführte Validierungskennzahl muss Datensätze, Datum, WSPRadar-Version oder Quellrevision und Berechnungsmethode nennen. Ohne diese Provenienz sollte sie aus dem normativen Handbuch entfernt oder ausdrücklich als datierte Validierungsprüfung gekennzeichnet werden.

<a id="sec-7-11"></a>
#### 7.11 Robuste ΔSNR-Ereigniserkennung mit lokaler Basislinie

Das Analyseziel des Detektors ist eine vorübergehende gleichgerichtete Abweichung des gepaarten ΔSNR eines Funkwegs von einem stabilen lokalen Erwartungswert. Er erstellt weder eine Rangfolge der größten Rohwerte noch schätzt er eine Ereigniswahrscheinlichkeit. [Abschnitt 2.5](#sec-outlier) erklärt, wann und wie dieses Diagnosewerkzeug fachkundig eingesetzt werden sollte; dieser Abschnitt definiert die exakte wissenschaftliche Konstruktion.

Die Konstruktion erfüllt drei Aufgaben: den üblichen lokalen Unterschied vor und nach einem Kandidaten bestimmen, eine vorübergehende Abweichung finden, ohne dass diese ihre eigene Basislinie verschiebt, und nur ein Intervall melden, das sämtliche Evidenzprüfungen besteht. **Residuum** bedeutet Abweichung von dieser lokalen Basislinie; **robuste Skala** beschreibt die Streuung in ihrer Umgebung; der **robuste z-Wert** setzt die Abweichung zu dieser Streuung ins Verhältnis. Ein großes rohes ΔSNR kann für einen Funkweg völlig üblich sein, während ein Wert nahe null eine erhebliche lokale Änderung darstellt.

Die Notation gilt nur für diesen Abschnitt, abgesehen von den drei bereits in [Abschnitt 4.6](#sec-5-6) eingeführten Symbolen der Bedienelemente: $D_{\min}$ bezeichnet **`Minimale absolute ΔSNR-Abweichung (dB)`**, $Z_{\min}$ bezeichnet **`Minimaler robuster z-Wert`** und $H_{\max}$ bezeichnet **`Maximaler Unterschied zwischen Baseline davor/danach (dB)`**. Keine andere Notation aus Kapitel 7 wird neu definiert.

| Symbol | Englischer Merkbezug und Bedeutung in diesem Abschnitt |
|---|---|
| $i$ | ein exakter Peer-Funkweg mit der Identität `Rufzeichen + Locator` |
| $u$ | eine native gepaarte Einheit: ein Joint Spot aus demselben Zyklus |
| $k$ | Index einer UTC-ausgerichteten 10-Minuten-Baseline-Zelle |
| $D_{i,u}$ | korrigiertes gepaartes ΔSNR Target minus Referenz der Einheit $u$ gemäß Abschnitt 7.5 |
| $\widetilde D_{i,k}$ | ΔSNR-Median in der belegten Baseline-Zelle $k$ |
| $\mathcal{B}_{\mathrm{pre}},\mathcal{B}_{\mathrm{post}}$ | beibehaltene Baseline-Evidenzwerte vor und nach dem Ereignis |
| $B_{\mathrm{pre}},B_{\mathrm{post}},B$ | Baseline vor dem Ereignis, nach dem Ereignis und abschließende lokale Baseline |
| $B^P_{i,k}$ | `B` = Baseline, `P` = Pilot: Pilot-Baseline für Funkweg $i$ und Zelle $k$ |
| $r^P_{i,u},r_{i,u}$ | `r` = residual: Pilot- und abschließendes Residuum der nativen Einheit $u$ |
| $\mathcal{V},S_{\mathrm{robust}}$ | `V` = variability, `S` = scale: zentrierte Stichprobe der Flankenvariabilität und robuste lokale Skala |
| $z_{i,u}$ | robuster z-Wert einer nativen gepaarten Einheit |
| $C_i,G_i,F$ | `C` = cadence, `G` = gap, `F` = floor: typische Funkwegkadenz, größte interne Lücke und vorläufige Gruppierungsuntergrenze |
| $W_i^P,W_i^B$ | `W` = width: Ausschlussbreiten der Pilot- und abschließenden Baseline |
| $E,m_E,z_E,\operatorname{agree}(E)$ | `E` = event, `m` = median, `agree` = agreement: Ereigniskandidat, medianes Residuum, robuster Ereignis-z-Wert und Anteil der Vorzeichenübereinstimmung |
| $\varepsilon$ | feste Vergleichstoleranz von `0.01 dB` für die Mindestabweichung und den maximalen Baseline-Unterschied |

Der Detektor verwendet $\varepsilon=0.01\ \mathrm{dB}$ ausschließlich beim Vergleich einer absoluten Abweichung mit $D_{\min}$ oder eines Baseline-Unterschieds davor/danach mit $H_{\max}$. Interne Evidenzwerte und konfigurierte Schwellen werden dabei nicht gerundet. Dieselbe Toleranz gilt für die Ereignisqualifikation, starke Grenzanker und einzeln qualifizierende native Einheiten. Robuste z-Werte, die MAD/IQR-Skalenschätzung und die Regeln zur Vorzeichenübereinstimmung bleiben unverändert; für den Vergleich des robusten z-Werts gilt keine Toleranz.

**1. Evidenz und Auflösung.** Nur native gepaarte Einheiten liefern ΔSNR-Werte für den Detektor. Einseitige Outcomes besitzen keinen gepaarten Wert und können kein Ereignis qualifizieren; ihre Zeitpunkte tragen jedoch zur Kadenzschätzung bei, und die Outcomes bleiben Diagnosekontext. Die Erkennung läuft für jeden Funkweg $i$ getrennt und vor der Darstellungsaggregation der **Zeitlichen Evidenz**. Ein anderes Darstellungs-Bin kann deshalb kein Ereignis erzeugen, zusammenführen, teilen oder entfernen. Ist **`ΔSNR-Ausreißerkandidaten melden`** ausgeschaltet, wird der Detektor nicht ausgeführt, und dem Ergebnis werden keine Ausreißerbegriffe hinzugefügt.

Für die Schätzung von Baseline und robuster Skala werden die nativen Werte zu $\widetilde D_{i,k}$ reduziert. Kandidatengruppierung und berichtete Grenzen behalten die Zeitpunkte der nativen gepaarten Einheiten.

**2. Stabile lokale Baseline und robuste Variabilität.** Für den geprüften Kandidaten untersucht der Detektor belegte 10-Minuten-Zellen bis zu sechs Stunden davor und sechs Stunden danach. Der Kandidat und seine Ausschlussbreite werden ausgelassen. Jede Flanke muss mindestens vier belegte Zellen enthalten; fehlende Zellen werden niemals ergänzt. Die beibehaltenen Zellenwerte bilden $\mathcal{B}_{\mathrm{pre}}$ und $\mathcal{B}_{\mathrm{post}}$:

$$
B_{\mathrm{pre}}=\operatorname{median}(\mathcal{B}_{\mathrm{pre}}),\qquad
B_{\mathrm{post}}=\operatorname{median}(\mathcal{B}_{\mathrm{post}})
$$

Das abschließende erwartete lokale ΔSNR gewichtet beide Flanken gleich, während das Stabilitätskriterium ihre Abweichung begrenzt:

$$
B=\frac{B_{\mathrm{pre}}+B_{\mathrm{post}}}{2},\qquad
\left|B_{\mathrm{pre}}-B_{\mathrm{post}}\right|\leq H_{\max}+\varepsilon
$$

Die gleiche Gewichtung verhindert, dass die Flanke mit mehr belegten Zellen dominiert. Fehlt einer Flanke die erforderliche Stützung oder scheitert das Stabilitätskriterium, bleibt der Funkweg für diesen Kandidaten unklassifiziert, und es wird kein Ereignis berichtet.

Damit eine Verschiebung der Baseline nicht als Rauschen behandelt wird, wird jede Flanke zur Messung der nahen Variabilität um ihre eigene Baseline zentriert. Geschweifte Klammern und Vereinigung bedeuten hier zusammengeführte Evidenzstichproben mit beibehaltenen Wiederholungen: Jedes beibehaltene Zellenresiduum trägt bei, auch wenn eine andere Zelle denselben Wert hat:

$$
\mathcal{V}=\left\{x-B_{\mathrm{pre}}:x\in\mathcal{B}_{\mathrm{pre}}\right\}
\cup\left\{x-B_{\mathrm{post}}:x\in\mathcal{B}_{\mathrm{post}}\right\}
$$

Die Skala beschreibt die typische absolute Streuung der zentrierten Flankenwerte in dB. Zunächst verwendet der Detektor deren mediane absolute Abweichung (MAD); bei null den halben Interquartilsabstand (IQR), und nur wenn beide null sind einen festen Ersatzwert:

$$
S_{\mathrm{robust}}=
\begin{cases}
\operatorname{MAD}(\mathcal{V}), & \operatorname{MAD}(\mathcal{V})>0,\\
\frac{1}{2}\operatorname{IQR}(\mathcal{V}), & \operatorname{MAD}(\mathcal{V})=0\ \land\ \operatorname{IQR}(\mathcal{V})>0,\\
0.5\ \mathrm{dB}, & \operatorname{MAD}(\mathcal{V})=0\ \land\ \operatorname{IQR}(\mathcal{V})=0.
\end{cases}
$$

MAD ist der Median der absoluten Abstände vom Stichprobenmedian; IQR ist der Abstand zwischen dem 25. und 75. Perzentil. Der Ersatzwert `0.5 dB` verhindert eine Division durch null, wenn beide Maße verschwinden; positive MAD- oder Halb-IQR-Werte unter `0.5 dB` bleiben erhalten. Das Abziehen der Baseline liefert ein Residuum in dB; die Division durch die robuste Skala und der konventionelle Faktor ergeben einen dimensionslosen Wert:

$$
r_{i,u}=D_{i,u}-B,\qquad
z_{i,u}=0.6745\frac{r_{i,u}}{S_{\mathrm{robust}}}
$$

Ein positives Residuum liegt über dem erwarteten lokalen ΔSNR Target minus Referenz, ein negatives darunter. Gruppierung und Qualifikation richten sich nach diesem Vorzeichen und nicht nach dem Vorzeichen des Rohwerts $D_{i,u}$ relativ zu `0 dB`. Der Faktor `0.6745` liefert die konventionelle Skalierung des modifizierten Werts, wenn MAD aktiv ist. Der Wert bleibt deskriptiv und ist weder eine kalibrierte Wahrscheinlichkeit noch ein p-Wert oder ein gaußsches Signifikanzniveau.

**Beispiel: positives ΔSNR, negative Abweichung.** Liegt die stabile lokale Baseline bei `+8 dB` und ein Joint Spot bei `+1 dB`, beträgt sein Residuum `-7 dB`. Das Target ist in diesem Spot weiterhin stärker als die Referenz, aber deutlich weniger als auf diesem Funkweg üblich. Bei einer robusten Skala von `1 dB` beträgt der robuste z-Wert ungefähr `-4,72`. Diese Rechnung allein erzeugt noch kein gemeldetes Ereignis: Flankenstützung, Baseline-Stabilität, Kriterien auf Ereignisebene, Vorzeichenübereinstimmung und beibehaltene Grenzanker müssen ebenfalls passen.

**3. Kadenzabhängige Pilotgruppierung.** Die typische Funkwegkadenz $C_i$ wird in Minuten aus eindeutigen Zeitpunkten zulässiger gepaarter und einseitiger Outcomes geschätzt. Positive Intervalle bis einschließlich 45 Minuten werden beibehalten; wenn mindestens zwei verbleiben, definiert ihr Median die Kadenz. Andernfalls liefert die konfigurierte Kadenz gepaarter Einheiten den Wert $C_i$. Die größte interne Lücke ist:

$$G_i=\min\left(45,\max\left(15,1.5C_i\right)\right)\ \mathrm{minutes}$$

Damit erhalten dünn belegte Funkwege einen kadenzabhängigen Gruppierungsspielraum; kein Ereignis kann jedoch mehr als 45 Minuten überbrücken, und keine geschätzte Kadenz verkleinert den Spielraum auf weniger als 15 Minuten.

Um Kandidaten zu bilden, ohne dass der geprüfte Punkt seinen eigenen Erwartungswert bestimmt, erhält jede unterstützte Zelle eine Pilot-Baseline $B^P_{i,k}$. Deren Ausschlussbreite und die bewusst niedrige Gruppierungsuntergrenze sind:

$$
W_i^P=\max(60,2C_i)\ \mathrm{minutes},\qquad
F=\min(1\ \mathrm{dB},D_{\min}-\varepsilon)
$$

Der Term `1 dB` bleibt exakt: Die Toleranz geht nur über die tolerierte Mindestabweichung in diese frühe Gruppierungsregel ein, damit die Gruppierung keine strengere Abweichungsanforderung als die abschließende Qualifikation stellt. Sie wird weder vom festen Term `1 dB` noch vom unten beschriebenen `1-dB`-Kriterium zur Erweiterung der Ereignisränder abgezogen.

Die Pilot-Anpassung verwendet dieselbe Flankenreichweite von sechs Stunden, mindestens vier belegte Zellen auf jeder Seite und das Stabilitätskriterium $H_{\max}$. Eine native Einheit $u$ in Zelle $k(u)$ erhält nur dann ein Pilot-Residuum, wenn diese Zelle gestützte Flanken besitzt:

$$r^P_{i,u}=D_{i,u}-B^P_{i,k(u)}$$

Nahe Pilot-Residuen desselben Vorzeichens und mit einem Betrag von mindestens $F$ bilden ein vorläufiges Ereignis. Die Gruppierung endet bei einer Lücke größer als $G_i$, einer Einheit mit entgegengesetztem Vorzeichen oder einer gestützten Rückkehr zur Baseline. Eine einzelne gestützte neutrale Einheit darf die Evidenz überbrücken, wenn sich die gleichgerichtete Abweichung fortsetzt; eine zweite aufeinanderfolgende gestützte neutrale Einheit beendet das Ereignis. Nicht gestützte Einheiten bleiben unklassifiziert und werden nicht ergänzt. Die niedrige Gruppierungsuntergrenze findet Kontinuität; sie lockert die abschließende Qualifikation nicht.

**4. Kandidatenausschließende abschließende Baseline.** Das vollständige vorläufige Ereignis wird mit folgender Breite aus der abschließenden Baseline-Anpassung ausgeschlossen:

$$W_i^B=\max(10,C_i)\ \mathrm{minutes}$$

Die abschließende Anpassung verwendet die Baseline- und robuste Skalenkonstruktion aus Schritt 2. Gegenüber dieser gemeinsamen abschließenden Baseline dürfen gleichgerichtete Ränder mit einem Residuumbetrag von mindestens `1 dB` das Ereignis in bis zu drei Durchgängen erweitern. Das vollständige erweiterte Intervall bleibt bei jeder erneuten Anpassung ausgeschlossen, damit der Kandidat seinen eigenen Erwartungswert nicht in Richtung der Auslenkung zieht.

**5. Qualifikation, Prüfung eines starken Kerns und berichtete Grenzen.** Für einen verfeinerten Ereigniskandidaten $E$ sind sein medianes Residuum, sein robuster Ereignis-z-Wert und der Anteil der Vorzeichenübereinstimmung definiert als:

$$
m_E=\operatorname{median}_{u\in E}(r_{i,u}),\qquad
z_E=0.6745\frac{m_E}{S_{\mathrm{robust}}}
$$

$$
\operatorname{agree}(E)=
\frac{\left|\left\{u\in E:\operatorname{sign}(r_{i,u})=\operatorname{sign}(m_E)\right\}\right|}{|E|}
$$

Der Ereignismedian beschreibt die typische Abweichung und nicht den größten Einzelpunkt. Der Nenner der Vorzeichenübereinstimmung umfasst alle beibehaltenen nativen Einheiten dieses Kandidaten einschließlich neutraler Brücken. Mindestens zwei Drittel müssen dasselbe Vorzeichen wie das mediane Residuum besitzen. Zur Qualifikation müssen alle vier Bedingungen gemeinsam gelten: genügend Abweichung in dB, genügend Abweichung relativ zur lokalen Streuung, vereinbare Baselines davor und danach sowie ausreichende Vorzeichenübereinstimmung:

$$
|m_E|\geq D_{\min}-\varepsilon,\qquad
|z_E|\geq Z_{\min},\qquad
\left|B_{\mathrm{pre}}-B_{\mathrm{post}}\right|\leq H_{\max}+\varepsilon,\qquad
\operatorname{agree}(E)\geq\frac{2}{3}
$$

Für jede Dauer und jede spätere Klasse gelten dieselben Kriterien. Es gibt weder einen Dauerbonus noch eine Absenkung der Schwellen aufgrund angesammelter Evidenz oder eine schwächere Schwelle für ein anhaltendes Ereignis.

Kann das vollständige verfeinerte Ereignis kein qualifiziertes, stark verankertes Intervall liefern, wird es an Rückkehrpunkten zur abschließenden Baseline in zusammenhängende gleichgerichtete Abschnitte ohne neutrale Überbrückung geteilt. Jeder Abschnitt wird anhand derselben Kriterien geprüft; dabei werden die abschließende Baseline, die robuste Skala und die Flankenstützung des vollständigen Kandidaten wiederverwendet. So kann ein durch schwache umgebende Evidenz verdeckter starker Kern erhalten bleiben, ohne dass der kleinere Abschnitt eine günstigere Referenz auswählen kann.

Nach der Qualifikation ist eine native Einheit nur dann ein starker Grenzanker, wenn:

$$
\operatorname{sign}(r_{i,u})=\operatorname{sign}(m_E),\qquad
|r_{i,u}|\geq D_{\min}-\varepsilon,\qquad
|z_{i,u}|\geq Z_{\min}
$$

Das berichtete Intervall wird auf den ersten und letzten starken Anker gekürzt. Bereits dazwischen gruppierte Einheiten bleiben interne Evidenz, auch wenn sie einzeln eine Anker-Schwelle verfehlen. Das gekürzte Intervall wird mit derselben abschließenden Baseline, robusten Skala und Flankenstützung neu aufgebaut und nochmals gegen alle Kriterien auf Ereignisebene geprüft. Schwache führende und nachlaufende Einheiten entfallen; schwächere interne Brücken können bestehen bleiben. Ein verbleibender Anker wird zum Spot-Impuls. Besteht kein stark verankertes Intervall die Prüfung, wird kein Ereignis berichtet. Die niedrige Gruppierungsuntergrenze und die höheren Anforderungen an die Grenzen erzeugen somit hysteretische Ereignisgrenzen.

Praktisch dürfen schwache Punkte den Zusammenhang innerhalb eines Ereignisses erhalten; dessen berichteten Anfang und Schluss dürfen jedoch nur einzeln starke Punkte festlegen.

Der Marker im Zeitplot aller Funkwege wird nur aus diesen starken Ankern ausgewählt: Innerhalb jedes funkwegübergreifenden Prüfereignisses liefert die einzeln qualifizierende native Einheit mit dem betragsmäßig größten Residuum das `*`. Eine ungestützte oder nicht qualifizierende Episodenspitze kann nicht zu diesem Plot-Repräsentanten werden. Die Markerauswahl ist von der Berichtsgröße **Größte Einzelzyklusabweichung** getrennt; diese bleibt für Bericht und Export das tatsächliche betragsmäßig größte beibehaltene Residuum jedes Funkwegereignisses.

**6. Deskriptive Klasse und funkwegübergreifender Kontext.** Die Klassifikation erfolgt nach der Kürzung:

* **Spot-Impuls:** eine beibehaltene native gepaarte Einheit;
* **Anhaltende Auslenkung:** mindestens drei beibehaltene native gepaarte Einheiten über eine Spanne von mindestens 30 Minuten und
* **Kurzer Ausbruch:** jedes andere beibehaltene Ereignis aus mehreren Einheiten.

Die Klassen beschreiben die zeitliche Form der Evidenz und verändern die Qualifikation nicht. Das angezeigte Intervall von der ersten bis zur letzten Einheit umspannt beobachtete beibehaltene Einheiten; es weist kein ununterbrochenes Verhalten zwischen ihnen nach.

Funkwegereignisse qualifizieren sich unabhängig. Gleichgerichtete Ereignisse erscheinen in einer gemeinsamen Prüfkarte, wenn sie sich überschneiden oder höchstens um den größeren Wert aus 10 Minuten und der halben konfigurierten Kadenz gepaarter Einheiten getrennt sind. Der Kontext lautet bei einem Funkweg funkwegspezifisch, bei mehreren Funkwegen in benachbarten Kompasssektoren richtungskohärent, bei mehreren getrennten Richtungen bereichsweit oder mehrere Funkwege, wenn für mindestens einen Beitragenden keine Richtung verfügbar ist. Der funkwegübergreifende Kontext verändert die Qualifikation eines Funkwegs nicht und ist keine Berechnung von Unabhängigkeit oder Signifikanz.

Die Zerlegung in Target und Referenz sowie nahe einseitige Outcomes bleiben interne Diagnoseangaben und lassen sich über die gepaarte Evidenz und den Drill-Down untersuchen. Sie qualifizieren, verlängern oder verstärken ein Ereignis nicht. Der Detektor ist somit ein deterministischer deskriptiver Klassifikator der beibehaltenen gepaarten Evidenz. Seine Ereigniszahl ist keine unabhängige Stichprobengröße; er nimmt keine Signifikanzkorrektur für mehrere Ereignisse vor, und eine kausale Zuordnung erfordert weiterhin die in den Kapiteln 2, 3 und 8 beschriebene Versuchskontrolle.

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

`Alle Ergebnisse zum Download vorbereiten` erstellt aus dem abgeschlossenen Lauf und den aktuellen Inspektor-Auswahlen eine ZIP-Datei; `Vorbereitete Ergebnisse herunterladen` speichert sie. Wähle vor der Vorbereitung den geografischen Bereich, die Station oder Stationsgruppe und ein etwaiges Fokusintervall, die deine Schlussfolgerung stützen. Ändern sich diese Auswahlen, bereite das aktualisierte Paket vor und lade es herunter.

Die folgende Übersicht zeigt die verfügbaren Dateien **innerhalb des benannten ZIP-Hauptordners**. `config/` begleitet das gewählte Ergebnis; `benchmark/` und `performance/` sind alternative Ergebnisordner und keine zwei Analysen aus einem Lauf:

```text
config/
  wspradar_config.config
  run_metadata.json
benchmark/
  figure_map_highres.png
  figure_segment_insight.png
  figure_segment_temporal_evidence.png
  figure_segment_temporal_coverage.png
  figure_selected_station_evidence.png
  figure_selected_station_coverage.png
  figure_drilldown_zoom_delta_snr_evidence.png
  figure_drilldown_zoom_coverage.png
  table_station_insights_current_segment.csv
  table_drilldown_selected_stations.csv
  table_drilldown_all_stations_current_segment.csv
  table_delta_snr_outlier_event_paths.csv
  table_delta_snr_outlier_paired_evidence.csv
  analysis_cache.parquet
performance/
  figure_map_highres.png
  figure_segment_insight.png
  figure_segment_temporal_snr_deviation.png
  figure_segment_temporal_evidence.png
  figure_selected_station_snr_evidence.png
  figure_selected_station_temporal_evidence.png
  figure_drilldown_zoom_snr_evidence.png
  figure_drilldown_zoom_temporal_evidence.png
  table_station_insights_current_segment.csv
  table_drilldown_selected_stations.csv
  table_drilldown_all_stations_current_segment.csv
  analysis_cache.parquet
```

Optionale Abbildungen hängen vom verfügbaren Ergebnis, der Stationsauswahl und dem Fokuszustand ab. Die drei regulären CSV-Tabellen werden für das Ergebnis geschrieben, auch wenn eine Auswahl keine Zeilen liefert. Ausreißer-CSV-Dateien erscheinen nur bei aktivierter Meldung, wie unten beschrieben.

| Artefakt | Wissenschaftlicher Inhalt und Bereich |
|---|---|
| `wspradar_config.config` | Versionierte ausführbare Definition und dauerhafte Einstellungen der Ergebnisansicht. |
| `run_metadata.json` | Provenienz von Anwendung und Export, Datenbankquelle, Richtung, Band, Zeitauswahl, Benchmark-/Korrekturdefinition, Filter, Schwellen und Inspektor-Auswahlen. |
| `analysis_cache.parquet` | Verarbeitete beibehaltene Evidenz des abgeschlossenen Laufs nach dessen wissenschaftlichen Filtern und konfiguriertem geografischem Bereich; nicht nur die aktive Auswahl im Segment-Inspektor und kein unveränderter Datenbankdownload. |
| `table_station_insights_current_segment.csv` | Zusammenfassungen je Peer für den aktiven Bereich des Segment-Inspektors. |
| Drill-Down-CSV-Dateien | Beibehaltene Evidenz auf Zeilenebene für ausgewählte Identitäten oder Identitäten im aktiven Bereich. |
| Delta-SNR-Ausreißer-CSV-Dateien | Bei aktivierter optionaler Ausreißermeldung Zusammenfassungen qualifizierter Funkwegereignisse und deren chronologische native gepaarte Evidenz für den aktiven Bereich des Segment-Inspektors. |
| Karten- und Segmentabbildungen | Geografische und segmentbezogene deskriptive Zusammenfassungen des abgeschlossenen Ergebnisses. |
| Zeitliche Abbildungen | Chronologische und nach UTC-Stunde gefaltete Zusammenfassungen für das aktive Segment. |
| Abbildungen der ausgewählten Station | Im Normalfall genau eine ausgewählte Peer-Identität; solange die optionale Delta-SNR-Ausreißererkennung eine geordnete Mehrfachauswahl von Funkwegen ermöglicht, kann Benchmark stattdessen die zugehörige zusammengefasste Mehrwegeansicht des ΔSNR exportieren. |
| Drill-Down-Fokusabbildungen | Optionale Messwertabbildungen in nativer Zeitauflösung und chronologische Ergänzungsabbildungen für die exakte ausgewählte Station und das aktive manuelle oder kandidatenverknüpfte Fokusintervall; sie ergänzen die Abbildungen der ausgewählten Station über den vollständigen Lauf, statt sie zu ersetzen. |

Für jeden Ergebnisblock hält `run_metadata.json` die tatsächlich verwendete Abfrageauswahl in `result_blocks[].decode_filter_mode` fest: `strict_code_1` bedeutet, dass die Abfrage das Prädikat `code = 1` beibehielt; `legacy_no_code` bedeutet, dass der historische Fallback diese Einschränkung wegließ, nachdem die strenge Abfrage keine Target-seitige Evidenz geliefert hatte. Neue Fallback-Ausführungen setzen voraus, dass der gesamte gewählte Zeitraum vor dem 1. Januar 2022 um 00:00 UTC endet, wie in [Abschnitt 5.4](#sec-6-4) beschrieben; die Provenienzbedeutung früherer Exporte bleibt unverändert. Die gespeicherte Konfiguration allein kann diese implizite Entscheidung nicht rekonstruieren; bewahre deshalb beim Vergleich von Evidenzpopulationen auch die Metadaten auf. Ein Wert `null` bedeutet, dass die Auswahl nicht dokumentiert wurde und nicht als strenge Auswahl angenommen werden darf. Dieses Feld dokumentiert die Abfrageauswahl; es bestätigt nicht unabhängig, dass jede Beobachtung derselben physikalischen Übertragungsart angehört.

Ist bei der Vorbereitung ein Drill-Down-Fokus aktiv, kann Performance `figure_drilldown_zoom_snr_evidence.png` und `figure_drilldown_zoom_temporal_evidence.png` ergänzen; Benchmark kann `figure_drilldown_zoom_delta_snr_evidence.png` und `figure_drilldown_zoom_coverage.png` ergänzen. Die Messwertabbildung bewahrt dieselben einzelnen beibehaltenen nativen Punkte wie der Browserfokus, statt Zeitmediane einzusetzen; die Ergänzungsabbildung bewahrt das zutreffende chronologische Outcome- oder Abdeckungsrezept. `run_metadata.json` enthält einen Block `drilldown_zoom` mit Schemaversion, Rufzeichen, Locator, exaktem `start_utc` und `end_utc`, gewählter Fokusoption, Ursprung `manual` oder `outlier_focus` und Rendervertrag. Ist ein Kandidaten-Overlay vorhanden, bewahren dessen registriertes Rezept und Signatur die fokussierte Episode und jede einzeln qualifizierende Kandidateneinheit im Fenster, das dezente Band der fokussierten Episode, lokale Baseline und Baselines davor/danach, robuste Streuung und Methode, robuste-z-Schwelle sowie absolute Abweichungsschwelle der exportierten Hilfslinien. Die Koordinaten der Hilfslinien bleiben auf die fokussierte Episode beschränkt, selbst wenn ein anderer markierter Kandidat im exportierten Fenster gegen eine andere Baseline oder Streuung bewertet wurde. Bei ausgeschaltetem Fokus oder nicht erfüllter Ein-Stations-Bedingung fehlen Fokusblock und Fokusabbildungen.

Bei aktivierter Delta-SNR-Ausreißermeldung enthält `table_delta_snr_outlier_event_paths.csv` je qualifiziertem Funkwegereignis eine Zeile. Sie erfasst die zusammengefasste Klasse und die beobachteten UTC-Grenzen des Prüfereignisses, den funkwegübergreifenden Zusammenhang und die Abweichungsrichtung sowie exakten Funkweg, Richtung, Ereignisklasse des Funkwegs, Zeitlage und Anzahl gepaarter Evidenzeinheiten, erwartetes und beobachtetes ΔSNR, größte Abweichung, robusten z-Wert, Baseline-Diagnostik davor/danach und nahe Decode Outcomes. Derselbe exakte Funkweg kann im selben zusammengefassten Prüfereignis in mehreren Zeilen erscheinen, wenn er mehr als einen qualifizierenden Zeitraum beiträgt. Die Anzahl qualifizierender Funkwege zählt weiterhin die unterschiedlichen Identitäten aus `Rufzeichen + Locator`.

`table_delta_snr_outlier_paired_evidence.csv` enthält für jede beibehaltene native gepaarte Einheit innerhalb dieser Funkwegereignisse eine chronologisch geordnete Zeile. Ereignis-ID und Funkwegereignis-ID verknüpfen sie mit der Zusammenfassung. Damit sie eigenständig lesbar bleibt, wiederholt sie die beobachteten Ereignisgrenzen, Funkweg, Richtung und Ereignisklasse des Funkwegs; die zusammengefasste Ereignisklasse steht nur in der Zusammenfassung, weil sie von der Klasse eines einzelnen Funkwegs abweichen kann. Die Tabelle enthält Target-SNR, bereits korrigiertes Referenz-SNR, ΔSNR, erwartetes lokales ΔSNR, Abweichung von dieser Baseline, robusten z-Wert der einzelnen Einheit, Status der starken Ankerkriterien und Rolle als berichtete Grenze. Zeitstempel verwenden ISO-UTC; numerische Felder bleiben numerisch, statt Vorzeichen oder Einheiten in die Zellen einzubetten.

Die IDs sind deterministische Verknüpfungen innerhalb eines vorbereiteten Pakets. Sie sind weder dauerhafte Identitäten über getrennt vorbereitete Analysen hinweg noch eine Aussage darüber, dass ein physisches Ereignis stattgefunden hat. Ist die Meldung aktiviert, aber kein Funkwegereignis qualifiziert, bleiben beide CSV-Dateien mit ihren Kopfzeilen und ohne erfundene Befundzeile vorhanden. `run_metadata.json` erfasst aktivierte Einstellung, Detektorversion, Konfiguration der drei Schwellen, Export-Schemaversion, Ergebnisstatus, Tabellennamen sowie Anzahlen von Ereignissen, Funkwegereignissen und Evidenzzeilen einmalig. Zutreffende exportierte Benchmark-Abbildungen behalten die Rezeptmetadaten derselben Kandidatenmarker. Ist die Meldung ausgeschaltet, fehlen beide CSV-Dateien, sämtliche Ausreißermetadaten und alle Ausreißer-Markierungsrezepte vollständig.

**Ausgewählte öffentliche maschinenlesbare Vertragsbezeichnungen.** Diese knappe Tabelle nennt unterstützte externe Bezeichnungen, die für den Funkbetrieb und nachgelagerte Auswertungen nützlich sind; sie ist kein vollständiger Katalog der Felder gespeicherter Konfigurationen, URL-Parameter oder Exportmetadaten. Für Felder gespeicherter Konfigurationen ist das formale JSON-Schema (`config/wspradar-config.schema.json`) maßgeblich; der unterstützte öffentliche URL-Vertrag ist separat versioniert. Private Implementierungsbezeichnungen sind bewusst ausgelassen. Diese Namen sind keine Begriffe zur Erklärung der wissenschaftlichen Methode.

| Vertragsbereich | Exakte Bezeichnungen | Bedeutung |
|---|---|---|
| Konfigurationsformat | Schemaversion `1` | Aktueller `.config`-Vorproduktionsvertrag; ungültige oder nicht unterstützte Dateien werden abgelehnt und nicht stillschweigend umgedeutet. |
| Werte des Ergebnistyps | `performance`, `benchmark` | Werte, die neue Analyse-URLs, Konfigurationen und Exporte ausgeben. |
| Dauerhafte Blöcke der Ergebnisansicht | `results_view.performance`, `results_view.benchmark` | Gespeicherte Inspektionsoptionen. Ihr Vorhandensein erzeugt oder startet kein zusätzliches Ergebnis. |
| Ergebnisordner | `performance/`, `benchmark/` | Oberste Ergebnisordner im Exportpaket. |
| Ausreißertabellen | `table_delta_snr_outlier_event_paths.csv`, `table_delta_snr_outlier_paired_evidence.csv` | Nur bei aktivierter Delta-SNR-Ausreißermeldung vorhandene Benchmark-Tabellen, verknüpft über paketinterne Ereignis-ID und Funkwegereignis-ID; bei deaktivierter Meldung fehlen sie. |
| Abbildungsmetadaten | `selected_evidence_figures`, `benchmark_evidence_figures`, `benchmark_evidence_recipes`, `drilldown_zoom` | Stabile Zuordnungen und exakte Identität/Grenzen des flüchtigen Zooms für zutreffende exportierte Abbildungen und Benchmark-Rezepte. |
| Korrekturmetadaten | `benchmark_snr_correction_mode`, `benchmark_snr_correction_db` | Semantische Auswahl der Korrektur und ihr numerischer dB-Wert. |

Verwende PNG-Abbildungen zur Darstellung des Ergebnisses, die Station-Insights-CSV zur Prüfung der Stationszusammenfassungen und Drill-Down-CSVs für die stützenden Zeilen. Die Parquet-Datei bewahrt verarbeitete Evidenz für weitere Auswertungen; die `.config`-Datei stellt unterstützte Einstellungen für einen weiteren Lauf wieder her, nicht die ursprünglichen Meldungen.

Das Paket bewahrt die verarbeitete Evidenz und die von WSPRadar erfasste Provenienz. Es enthält keine maßgeblichen externen Betriebsprotokolle, physischen Aufbaumessungen oder unveränderten Datenbankantworten. Bewahre diese wie in [Abschnitt 8.3](#sec-8-3) beschrieben getrennt auf; eine spätere Datenbankabfrage muss nicht exakt dieselben Datensätze liefern.

<a id="sec-8-5"></a>
#### 8.5 Haftungsausschluss

WSPRadar ist experimentelle Open-Source-Software und wird in der vorliegenden Form („as is“) ohne Gewährleistung bereitgestellt. Quellcode und Methoden können geprüft werden; Genauigkeit, Vollständigkeit, Verfügbarkeit und Eignung werden jedoch nicht garantiert. Triff keine wesentlichen finanziellen oder sicherheitsrelevanten Entscheidungen allein auf Grundlage von WSPRadar.

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

* <a id="ref-10"></a><a href="https://wspr.live/">[Ref-10]</a> **Offizielle Dokumentation des Datendienstes.** WSPR.live, *Welcome to WSPR Live*: Datenbankzugriff, Schema, Zuordnung der Mode-Codes, Hinweise zu Rohdaten und Verfügbarkeit sowie Verhalten bei Datenaktualisierungen. Abgerufen am 2026-08-06.

* <a id="ref-11"></a><a href="https://www.wsprdaemon.org/">[Ref-11]</a> **Offizielle Projektwebsite.** WSPRDaemon, *WSPR Daemon*: mehrkanalige Spot-Erfassung, Decodierung und Reporting von WSPR/FST4W, Rauschschätzung, Datenbank-/Grafana-Ausgabe sowie Datendienste für Drittanwendungen. Abgerufen am 2026-08-06. **Offizielle Betriebsdokumentation.** WsprDaemon, <a href="https://wsprdaemon.readthedocs.io/en/master/FAQ.html#how-does-spot-merging-work-with-multiple-receivers">*FAQ: How does spot merging work with multiple receivers?*</a>: Meldung des besten SNR an WSPRnet beim Zusammenführen von Empfängermeldungen. Abgerufen am 2026-09-24.

* <a id="ref-12"></a><a href="https://wsjt.sourceforge.io/wsjtx-main_en.html">[Ref-12]</a> **Offizielle Betriebsdokumentation.** WSJT-X 3.0.1 User Guide: WSPR-Nachrichtenformate Typ 1, Typ 2 und Typ 3; zufällige Zeitplanung über `Tx Pct`; Dateitrennung unter Windows mit `--rig-name`; Audioeinstellungen und Dateispeicherorte. QRP Labs, <a href="https://qrp-labs.com/qmx">*QMX firmware history and manuals*</a> und <a href="https://www.qrp-labs.com/images/qmx/manuals/operation_1_04_004.pdf">*QMX Operating Manual, firmware 1_04_004*</a> und <a href="https://qrp-labs.com/images/qmx/manuals/VirtualU3S_1_04_008a.pdf">*Virtual U3S Manual, firmware 1_04_008a*</a>: modellspezifische Firmware sowie Betrieb und Zeitplanung mit Virtual U3S; <a href="https://www.qrp-labs.com/images/ultimate3s/operation3.12a2.pdf">*Ultimate3S Operating Manual, firmware v3.12a2*</a>: WSPR-Frequenzbereich, globales Frame-/Start-Verhalten, erweitertes WSPR, sequenzielle Mode-Einträge und `Aux`-Werte je Eintrag; <a href="https://qrp-labs.com/images/appnotes/AN003_A4.pdf">*AN003: Ultimate3/3S relay-switched filters*</a>: gefilterte Relais-/Treiberansteuerung und Schaltintervalle ohne HF. Abgerufen am 2026-10-03.

* <a id="ref-13"></a><a href="https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf">[Ref-13]</a> **Konferenzbeitrag.** Griffiths, G.; Robinett, R. (2020). *Aids to the Presentation and Analysis of WSPR Spots: TimescaleDB database and Grafana*. ARRL/TAPR Digital Communications Conference 2020.

* <a id="ref-14"></a><a href="https://wspr.rocks/help.html">[Ref-14]</a> **Werkzeugdokumentation.** WSPR.Rocks, *Help &amp; Documentation*: SpotQ, SQL-Zugriff, Duplikatanalyse, Karten, Diagramme und Heatmaps.

* <a id="ref-15"></a><a href="https://www.sotabeams.co.uk/wsprlite-classic">[Ref-15]</a> **Produktdokumentation.** SOTABEAMS, *WSPRlite Classic / DXplorer*: WSPR-basierte Analyse der Antennenleistung und DX10-Metrik.

* <a id="ref-16"></a><a href="https://sites.google.com/myuba.be/wspr-station-compare/home">[Ref-16]</a> **Projektdokumentation.** WSPR-Station-Compare, Projektseite mit Verweisen auf Vanhamel et al. und Zander.

* <a id="ref-17"></a><a href="https://wspr.bsdworld.org/">[Ref-17]</a> **Werkzeugdokumentation.** Antenna Performance Analysis Tool, WSPR-basierter Generator für Antennenberichte.

* <a id="ref-18"></a><a href="https://www.gm4eau.com/home-page/wspr/">[Ref-18]</a> **Werkzeugdokumentation.** GM4EAU, *WATT WSPR Analysis Tool*: Berichte, Karten, Filter und Zeitachsenanimation in Excel/VBA.

* <a id="ref-19"></a><a href="https://qrp-labs.com/qmxp/wsprcorruption.html">[Ref-19]</a> **Technische Untersuchung des Herstellers.** QRP Labs, *WSPR Type 3 callsign corruption*: beobachtete Hash-Kollisionen oder Fehlzuordnungen zusammengesetzter Rufzeichen in großen WSPR-Datensätzen und ihr Mechanismus. Abgerufen am 2026-08-25.

* <a id="ref-20"></a><a href="https://github.com/HarrydeBug/WSPR-transmitters/blob/1657468ea27052167191a7deda2440a535567ecd/Standard%20Firmware/Release/Hardware_Version_2_ESP8285/WSPR-TX2.19/WSPR-TX2.19.ino">[Ref-20]</a> **Veröffentlichter Firmware-Quellcode, unveränderliche Revision.** ZachTek WSPR-TX-Firmware `2.19` für ESP8285-Hardware: Frequenzauswahl in `DoWSPR()`, Frequenzeinheit Hundertstel Hertz, Produktmodellauswahl und Build-Voraussetzungen. Revision `1657468ea27052167191a7deda2440a535567ecd`. Abgerufen am 2026-08-25.

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

Am einfachsten ist der Aufbau mit zwei verschiedenen regulären Rufzeichen, die jeweils in das normale WSPR-Format mit einer Aussendung passen. Dann enthält jede Aussendung das vollständige Rufzeichen, Grid-4 und die gemeldete Leistung. Das vermeidet die ergänzende Typ-2-/Typ-3-Folge und deren in [Abschnitt 7.6](#sec-7-6) beschriebene Grenze der Hash-Auflösung.

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

Die unveränderte ZachTek-Firmware `2.19` des veröffentlichten ESP8285-Quellcodes wählt bei jeder Auswahl einen neuen zufälligen Versatz von ungefähr `-100 Hz` bis `+99 Hz` um die nominale WSPR-Frequenz. Zwei unveränderte Geräte behalten deshalb keine getrennten A/B-Frequenzbereiche und können gelegentlich nahe beieinander senden. Erstelle für ein kontrolliertes simultanes Paar zwei getrennt beschriftete angepasste Firmware-Builds aus dem Quellcode, der exakt zum jeweiligen Sender passt <a href="#ref-20">[Ref-20]</a>.

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
