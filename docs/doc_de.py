# docs/doc_de.py

"""Maßgebliches deutschsprachiges Anwender- und Wissenschaftshandbuch für WSPRadar."""

DOC_DE = r"""
---

<a id="sec-1"></a>

### 0. Warum WSPRadar?

Funkamateure verändern und optimieren ihre Stationen fortlaufend. Eine neue Antenne wird aufgebaut, ihre Höhe oder Ausrichtung verändert, eine Speiseleitung ersetzt, eine Mantelwellensperre überarbeitet oder ein Empfänger, Filter beziehungsweise Vorverstärker ergänzt. Fast zwangsläufig folgt dieselbe Frage: **Hat die Änderung die Station tatsächlich verbessert – und wenn ja, wo, wann und um wie viel?**

Im praktischen Funkbetrieb scheint sich das zunächst leicht beantworten zu lassen. Es gelingen mehr QSOs, eine Gegenstation gibt einen besseren Rapport, ein WebSDR zeigt ein stärkeres Signal oder WSPR liefert mehr Spots. Solche Beobachtungen sind wertvoll, messen aber nicht allein das geänderte Bauteil. Das Ergebnis entsteht immer aus dem Zusammenwirken der vollständigen Station mit dem Funkweg: Antenne, Speiseleitung, Funkgerät, Sendeleistung, Empfänger, lokaler Stör- und Rauschpegel, Gelände, Ionosphäre, Gegenstation und Zeitpunkt wirken gleichzeitig zusammen.

Genau darin liegt das grundlegende Messproblem. Ein besserer Rapport kann auf einer günstigen Ausbreitungsphase beruhen. Ein zusätzliches QSO kann eine andere Gegenstation betreffen. Eine höhere Spotzahl kann durch veränderte Netzaktivität oder bessere Bedingungen entstehen. Selbst vollkommen korrekte Beobachtungen zeigen daher nicht automatisch, wodurch der Unterschied verursacht wurde.

Erfahrene Funkamateure begegnen diesem Problem mit zunehmend kontrollierten Verfahren: wiederholten Vergleichen, Bakenaussendungen, WebSDRs, Daten des Reverse Beacon Network, WSPR und insbesondere einer schnellen A/B-Umschaltung im laufenden Betrieb. Ein schneller A/B-Test ist wesentlich aussagekräftiger als zwei Stunden auseinanderliegende QSOs, weil Sender, Leistung, Frequenz, Gegenstation und ein großer Teil des Funkwegs ähnlich bleiben. Etablierte WSPR-Vergleichsversuche zeigen ebenfalls, dass gemeinsame Bedingungen und möglichst kurze – oder simultane – Vergleiche belastbarer sind als lange getrennte Messblöcke <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a> <a href="#ref-3">[Ref-3]</a> <a href="#ref-4">[Ref-4]</a> <a href="#ref-5">[Ref-5]</a>.

Doch selbst ein sorgfältiger schneller A/B-Vergleich beobachtet normalerweise nur einen Funkweg in einem kurzen Zeitfenster. QSB, Mehrwegeausbreitung, QRM und lokaler Störpegel können sich schon während der Umschaltung verändern. AGC, S-Meter-Auflösung, unterschiedliche Signalwege und subjektive Rapporte bringen zusätzliche Unsicherheit ein. Ein beobachteter Vorteil kann real sein, gilt zunächst aber nur für diese Gegenstation, Richtung, Zeit und Ausbreitungslage.

Die eigentliche Herausforderung besteht deshalb nicht nur darin, einen Unterschied zu sehen. Entscheidend ist, **ob sich dieser Unterschied unter vielen vergleichbaren Bedingungen wiederholt, wie groß er typischerweise ist, auf welchen Funkwegen er auftritt, wann er wiederkehrt und wie viel Evidenz ihn stützt.**

Hier bietet WSPR eine ungewöhnlich leistungsfähige Grundlage. Seine wiederholten, zeitgestempelten und maschinell decodierten Aussendungen mit kleiner Leistung erzeugen in einem weltweiten, ehrenamtlich betriebenen Netz Beobachtungen über viele Stationen, Entfernungen, Richtungen und Ausbreitungszustände <a href="#ref-6">[Ref-6]</a> <a href="#ref-7">[Ref-7]</a> <a href="#ref-8">[Ref-8]</a>. Je nach Bandbelegung und Beobachtungsdauer können über Stunden oder Tage Hunderte bis Tausende Meldungen zusammenkommen.

WSPRadar macht aus diesem Strom von Meldungen ein experimentelles Evidenzsystem. Es führt vergleichbare Beobachtungen zusammen, prüft, ob die relevanten Stationen nachweislich aktiv waren, berücksichtigt gegebenenfalls die gemeldete Sendeleistung, verhindert, dass wenige besonders aktive Stationen stationsgleichgewichtete Zusammenfassungen unbemerkt dominieren, und hält jedes Ergebnis bis zu den beitragenden Stationen und Beobachtungen prüfbar. Die Aktivitätsprüfung folgt einem wichtigen Grundsatz für Beobachtungsdaten: Funkstille sollte erst dann zu Gegen-Evidenz werden, wenn der Betrieb unabhängig erkennbar ist <a href="#ref-9">[Ref-9]</a>.

Das Ergebnis ist mehr als eine Spotzahl und mehr als eine einzelne Gewinner-Verlierer-Kennzahl. WSPRadar kann zeigen, ob ein Muster breit oder funkwegabhängig ist, ob es mit Entfernung oder Richtung zusammenhängt, ob es nur einmal auftritt oder zu bestimmten Tageszeiten wiederkehrt, ob viele Stationen übereinstimmen und ob die gepaarte Evidenz das breitere Ergebnis tatsächlich repräsentiert. Damit wird aus **„Das sah einmal besser aus“** zunehmend **„Dieser Unterschied trat hier, unter diesen Bedingungen, wiederholt und mit dieser Evidenz auf.“**

WSPRadar ist kein kalibriertes Antennenmessgelände und macht aus öffentlichen WSPR-Meldungen keine Labormessung. Es schlägt eine praktische Brücke zwischen alltäglicher Stationsoptimierung und Amateurwissenschaft: semiquantitative, geografisch reichhaltige, zeitbezogene und prüfbare Evidenz über vollständige Stationen und kontrollierte Signalwege unter realen Betriebsbedingungen.

So eingesetzt wird WSPR auch für die gesamte Amateurfunkgemeinschaft wertvoller. Korrekte Rufzeichen, Locator und Leistungsangaben, stabiler Betrieb und dokumentierte Änderungen machen aus gewöhnlichem Bakenbetrieb Evidenz, die später erneut untersucht, verglichen und genutzt werden kann, statt nur auf einer Karte vorbeizuziehen.

<a id="sec-1-1"></a>

#### 0.0 WSPR in 2 Minuten

<strong class="defined-term">WSPR</strong> steht für **Weak Signal Propagation Reporter**. Joe Taylor, K1JT, und Bruce Walker, W1BW, beschrieben WSPR als weltweites Netz von QRP-Stationen, die bakenartige Aussendungen austauschen, um mögliche Ausbreitungswege zu untersuchen. Eine WSPR-2-Aussendung dauert knapp zwei Minuten und belegt nur etwa 6 Hz. Die Nachricht enthält normalerweise ein Rufzeichen, einen vierstelligen Maidenhead-Locator und die gemeldete Sendeleistung in dBm. Das vom Decoder gemeldete Signal-Rausch-Verhältnis (SNR) bezieht sich auf eine Bandbreite von 2500 Hz; Decodes sind bis ungefähr `-28 dB` möglich. Ein weniger negativer SNR-Wert bedeutet ein stärkeres Signal relativ zum Empfängerrauschen <a href="#ref-6">[Ref-6]</a> <a href="#ref-8">[Ref-8]</a>.

Ist das Reporting aktiviert, lädt ein Empfänger jeden erfolgreichen Decode als <strong class="defined-term">Spot</strong> hoch. Ein Spot enthält die Identität von Sender und Empfänger, deren gemeldete Standorte, Zeit, Band, Sendeleistung und den vom Decoder gemeldeten SNR. Öffentliche <strong class="defined-term">Archive</strong> enthalten dadurch eine große und fortlaufend wachsende Sammlung erfolgreicher Funkbeobachtungen, die von unabhängig betriebenen Stationen in aller Welt beigetragen werden. Dienste wie wspr.live und WSPRDaemon bewahren diese Beobachtungsdaten auf und stellen sie für Analysen bereit <a href="#ref-10">[Ref-10]</a> <a href="#ref-11">[Ref-11]</a>.

**Datenquellen.** WSPRadar verwendet **wspr.live** als primäre Datenquelle. Das WSPRadar-Projekt dankt den Menschen hinter wspr.live und WSPRDaemon, die diese öffentlich zugängliche Datenbankinfrastruktur bereitstellen und betreiben.

Bei gleichzeitiger Last kann WSPRadar einen vollständigen neuen Lauf je nach verfügbarer Kapazität an **WSPRDaemon WD2** und danach **WD1** weiterleiten. Dieser geordnete Kapazitätsausgleich unterscheidet sich von einem Quellenwechsel nach einem Ausfall: Fällt eine ausgewählte Quelle aus, verwirft WSPRadar den noch nicht veröffentlichten Versuch und startet den vollständigen Lauf mit der nächsten Quelle neu. Jeder abgeschlossene Lauf bleibt an genau ein Archiv gebunden; Datensätze aus verschiedenen Quellen werden niemals zusammengeführt.

Eine Einschränkung ist für jede Analyse zentral: Das Archiv erfasst erfolgreiche Decodes, aber kein vollständiges Protokoll aller Sendeversuche oder aller aktiven Empfänger. WSPRadar bildet deshalb nur dann eine <strong class="defined-term">Gelegenheit</strong>, wenn unabhängige Evidenz zeigt, dass der betreffende entfernte Sender beziehungsweise Empfänger aktiv war. Bei RX muss ein anderer geeigneter Empfänger denselben Sender decodiert haben. Bei TX muss der entfernte Empfänger ein anderes Signal auf demselben Band decodiert haben. Ohne diesen Aktivitätsnachweis wird ein fehlender Target-Spot nicht automatisch als funktechnischer Misserfolg gewertet.

Durch diese Unterscheidung wird aus einer Sammlung erfolgreicher Spots Evidenz, die Fragen nach praktischer Reichweite, Beständigkeit und relativer Performance stützen kann, ohne so zu tun, als sei jede fehlende Meldung ein gescheiterter Funkweg.

<a id="sec-1-0"></a>
<a id="sec-1-2"></a>

#### 0.1 Was WSPRadar zeigen kann

WSPRadar ist ein WSPR-basiertes System zur Analyse und zum Benchmarking der Performance von Antennen und Stationen. Es wertet ein <strong class="defined-term">Target</strong> aus: die zu untersuchende Station, normalerweise deine Station, dargestellt entweder als vollständig aufgebaute Station oder als kontrollierter Sende- beziehungsweise Empfangspfad. Ein <strong class="defined-term">Peer</strong> ist eine entfernte Gegenstation, deren Funkweg zur Analyse beiträgt. Die <strong class="defined-term">Dekodierrate</strong> ist der Prozentsatz unabhängig bestätigter Gelegenheiten mit einem erfolgreichen Decode auf der Target-Seite: Bei RX decodiert das Target den Peer, bei TX decodiert der Peer das Target. Dabei beantwortet WSPRadar eine von zwei grundlegenden Fragen.

* <strong class="defined-term">Performance</strong> fragt, wie sich das Target innerhalb unabhängig bestätigter WSPR-Gelegenheiten verhalten hat. Sie kann die praktische Funkabdeckung, Mindestens-einmal-Reichweite, Dekodierrate, erfolgreiche Signalpegel, Distanz- und Richtungsstruktur, zeitliches Verhalten sowie Breite und Tiefe der stützenden Evidenz sichtbar machen.
* <strong class="defined-term">Benchmark</strong> fragt, wie sich das Target unter zugeordneten Bedingungen relativ zu einer aussagekräftigen <strong class="defined-term">Referenz</strong> verhalten hat. Er kann gepaartes Delta SNR Target minus Referenz, gemeinsame und einseitige Decode Outcomes, den Anteil paarbarer Evidenz sowie Ort und Zeit des relativen Unterschieds zeigen.

Die Fragestellung bestimmt das passende Evidenzdesign:

| Analyse | Fragestellung | Praktische Beispiele |
|---|---|---|
| <strong class="analysis-choice-single">RX Performance</strong> | Wie breit und wie beständig decodiert mein Empfänger Signale, die andernorts unabhängig bestätigt wurden? | Empfangsbereich einer neu aufgebauten Antenne oder Station erfassen; unterscheiden, ob der Empfang breit, aber wechselhaft oder schmaler und beständig ist; wiederkehrende Richtungs-, Entfernungs- oder UTC-Stunden-Muster erkennen – einschließlich Zeiträume, die eine separate Prüfung auf lokalen Störpegel oder intermittierende Hardware nahelegen. |
| <strong class="analysis-choice-single">TX Performance</strong> | Wo, wann und wie beständig wird mein Sender von Empfängern decodiert, deren Aktivität unabhängig nachgewiesen ist? | Abbilden, wo eine QRP-Bake oder neu installierte Antenne gehört wird; erkennen, zu welchen Zeiten und in welchen Richtungen nachweislich aktive Empfänger die Station besonders beständig decodieren; nach Inbetriebnahme, Reparatur oder Standortänderung eine Ausgangsbasis schaffen und mit vergleichbaren Wiederholungsläufen prüfen, ob sich das beobachtete Verhalten später verändert. |
| <span class="analysis-choice"><span class="analysis-family">RX Benchmark</span><br><strong class="analysis-variant">Hardware A/B</strong></span> | Unterschieden sich zwei lokale Empfangspfade beim gleichzeitigen Beobachten derselben entfernten Aussendungen? | Zwei Antennen vergleichen, die jeweils eine eigene simultane Empfänger- und Decoderkette speisen, wobei das Ergebnis zunächst die vollständigen Empfangspfade beschreibt; einen Unterschied nur dann gezielt den Antennen zuschreiben, wenn die übrigen Ketten abgeglichen, charakterisiert oder durch einen Kreuztausch bestätigt wurden; eine Antenne über einen charakterisierten Verteiler an zwei Empfänger führen, um Empfänger oder Decoderpfade zu vergleichen; Vorverstärker, Filter, Speiseleitung oder Mantelwellensperre nur in einen ansonsten kontrollierten Pfad einfügen und die beiden dokumentierten vollständigen Empfangspfade benchmarken. |
| <span class="analysis-choice"><span class="analysis-family">TX Benchmark</span><br><strong class="analysis-variant">Hardware A/B</strong></span> | Unterschieden sich zwei lokale Sendepfade bei simultanem oder eng getaktetem Betrieb? | Zwei Antennen über getrennte, kalibrierte Sendeketten speisen und mit synchronisierten Zyklen, unterscheidbaren Signalen und ausreichender Entkopplung gleichzeitig senden; einen Sender über einen kontrollierten HF-Umschalter nach festem UTC-Zeitplan abwechselnd auf zwei Antennen schalten; zwei Speiseleitungen, Anpassnetzwerke, Filter oder vollständige Sendepfade vergleichen und dabei tatsächliche Leistung, Zeitsteuerung und die übrige Kette kontrollieren. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Referenzstation / Buddy-Test</strong></span> | Wie schneidet meine vollständige Station gegenüber einer bekannten Station ab? | <strong>RX:</strong> den eigenen Empfänger mit dem bekannten Empfänger eines Funkfreunds vergleichen, während beide in denselben Zyklen dieselben entfernten Sender beobachten; <strong>TX:</strong> den eigenen Sender mit dem Sender eines Funkfreunds an denselben entfernten Empfängern und in denselben Zyklen vergleichen; ein stabiles, gut verstandenes Buddy-Design vor und nach dokumentierten Stationsarbeiten als relative Basislinie für die Gesamtstation wiederholen, ohne die Buddy-Station als absolut kalibrierten Standard zu behandeln. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Lokaler Nachbarschafts-Median</strong></span> | Wie schneidet meine Station gegenüber der typischen aktiven WSPR-Gruppe in der Umgebung ab? | Prüfen, ob die eigene Empfangs- oder Sendestation insgesamt über, nahe oder unter dem zyklus- und funkwegspezifischen Median der aktiven lokalen Peers im gewählten Radius liegt; eine Station in Betrieb nehmen, wenn keine einzelne geeignete Buddy-Referenz verfügbar ist; Richtungen, Entfernungen oder UTC-Zeiträume erkennen, in denen die Station von dieser kontextbezogenen lokalen Basislinie abweicht, und dabei Zusammensetzung der Nachbarschaft sowie Radiusabhängigkeit prüfen. |
| <span class="analysis-choice"><span class="analysis-family">RX/TX Benchmark</span><br><strong class="analysis-variant">Beste lokale Station</strong></span> | Wie schneidet meine Station gegenüber dem stärksten aktiven Peer in der Umgebung ab, der auf dem jeweiligen Funkweg und in dem jeweiligen Zyklus verfügbar ist? | Die eigene Station mit der stärksten qualifizierenden Station in der Umgebung vergleichen, die auf jedem Funkweg und in jedem Zyklus verfügbar ist; Richtungen oder Entfernungsbereiche finden, in denen sich die eigene Station der wechselnden lokalen Bestmarke nähert oder hinter ihr zurückbleibt; in vergleichbaren Wiederholungsläufen verfolgen, ob sich der beobachtete Abstand verkleinert oder vergrößert, während Radius und Poolzusammensetzung geprüft werden – ohne das Ergebnis als Rangliste gegen einen festen Konkurrenten oder als stabile kalibrierte Basislinie zu behandeln. |

Die Referenz ist Bestandteil der wissenschaftlichen Fragestellung und nicht nur eine Darstellungsoption. Ein kontrollierter <strong class="defined-term">Hardware-A/B-Test</strong> bietet die stärkste Grundlage, einen beobachteten Unterschied lokalen Pfaden oder Bauteilen zuzuordnen – allerdings nur in dem Maß, in dem die übrigen Ketten kontrolliert sind. Ein <strong class="defined-term">Referenzstations-/Buddy-Test</strong> vergleicht zwei vollständig aufgebaute Stationen einschließlich QTH, Geräten, Gelände sowie lokaler Stör- und Rauschumgebung. Nachbarschafts-Benchmarks liefern wechselnde kontextbezogene Basislinien und keine festen oder kalibrierten Standards.

Diese Perspektiven machen WSPRadar für weit mehr als formale Antennenvergleiche nützlich. Performance kann eine Ausgangsbasis für die Station schaffen, zeigen, wo sie zuverlässig gehört wird, richtungs- oder entfernungsabhängiges Verhalten sichtbar machen, wiederkehrende Tagesmuster erkennen und eingrenzen, wann eine intermittierende Veränderung aufgetreten ist. Benchmark kann Antennen, Speiseleitungen, Filter, Vorverstärker, Empfänger oder vollständige Pfade vergleichen, zwei Gesamtstationen gegenüberstellen oder eine Station in den Kontext ihrer aktiven lokalen Nachbarschaft einordnen.

WSPRadar kann **Form, Umfang und zeitliche Lage** einer Beobachtung bestimmen. Es kann zeigen, ob ein Unterschied breit, konzentriert, intermittierend, wiederkehrend oder nur durch eine schmale Stationsgruppe gestützt ist. Allein daraus folgt jedoch nicht, dass die Ursache Antennengewinn, Strahlungswirkungsgrad, Abstrahlwinkel, kalibrierte Empfängerempfindlichkeit, lokaler Störpegel oder ein bestimmtes Bauteil war. Keine nachträgliche Statistik kann eine Variable beseitigen, die der physische Versuch nicht kontrolliert hat.

<a id="sec-1-3"></a>

#### 0.2 Was ein Lauf liefert

Ein WSPRadar-Lauf erzeugt ein zusammenhängendes Evidenzpaket für eine klar begrenzte Stationsfrage – keine universelle Kennzahl und keine Rangliste.

Ein Performance-Lauf verbindet praktische Reichweite, zwei ergänzende Gewichtungen der Dekodierrate, erfolgreiches Target-SNR, Distanz- und Richtungsstruktur, zeitliche Veränderungen, wiederkehrendes Verhalten nach UTC-Stunde, beitragende Stationen und die zugrunde liegenden Gelegenheiten. Ein Benchmark-Lauf verbindet gepaartes Delta SNR mit Decode Outcomes und Evidenzabdeckung, sodass ein günstiger gepaarter Median weder umfangreiche einseitige Evidenz noch eine schmale paarbare Teilmenge verdecken kann.

Jedes Ergebnis folgt demselben Evidenzpfad:

> <strong class="defined-term">Karte → Segment-Inspektor → Performance-/Benchmark-Evidenz → Zeitliche Evidenz → Station Insights → Evidenz der ausgewählten Station → Drill-Down</strong>

Die Karte liefert den geografischen Überblick. Evidenz auf Segmentebene zeigt, wie sich die Beobachtung nach Entfernung und Richtung verändert und wie viel Unterstützung dahintersteht. Performance- beziehungsweise Benchmark-Evidenz trennt das Hauptergebnis von seiner ergänzenden Evidenz. Zeitliche Evidenz zeigt, ob sich das Muster während des Laufs veränderte oder zu bestimmten UTC-Stunden wiederkehrte. Station Insights legt offen, welche Stationsidentitäten beitragen. Die Evidenz der ausgewählten Station verfolgt einen exakten Funkweg; Drill-Down zeigt die Beobachtungen, Vergleiche desselben Zyklus oder geplanten A/B-Paare hinter den Zusammenfassungen.

Diese abgestufte Struktur ist eine der zentralen Stärken von WSPRadar: Das übergeordnete Muster bleibt mit seiner Evidenz verbunden. Der Operator kann von **wo der Effekt auftritt** über **wie beständig er ist und wie gut er gestützt wird** bis zu **den einzelnen Beobachtungen, aus denen die Schlussfolgerung entstanden ist**, hinabsteigen.

Ein belastbares Ergebnis ist deshalb nicht einfach der größte Wert auf dem Bildschirm. Versuchsdesign, geografisches Muster, zeitliches Verhalten, Stationsbreite, Evidenztiefe und Prüfung auf Zeilenebene müssen dieselbe begrenzte Interpretation stützen. Eine Wiederholung des Designs in einem weiteren geeigneten Betriebsfenster kann anschließend prüfen, ob die Beobachtung experimentell wiederholbar ist und nicht nur innerhalb eines Laufs konsistent erscheint.

Der vollständige Lauf lässt sich außerdem als Reproduzierbarkeitspaket mit Analysedefinition, verarbeiteter Evidenz, Tabellen, Abbildungen und Metadaten sichern. Zusammen mit den physischen Stationsnotizen, die WSPRadar nicht selbst erschließen kann, kann er später erneut geprüft oder mit anderen Funkamateuren geteilt werden.

<a id="sec-1-4"></a>

#### 0.3 Der erste sinnvolle Lauf

Am schnellsten erschließt sich WSPRadar mit einer gepflegten Demo. Eine Demo zeigt eine vollständige historische Performance- oder Benchmark-Analyse mit vorbereitetem Versuchskontext. So lässt sich der Evidenzpfad erkunden, bevor die eigene Station beteiligt ist.

Der Nutzen der Demo wird im Zusammenhang ihrer Ebenen sichtbar: geografischer Überblick, Entfernung und Richtung, einmaliges oder wiederkehrendes zeitliches Verhalten, Anzahl und Vielfalt der stützenden Stationen, Paarbarkeit der Benchmark-Evidenz sowie die ausgewählten Funkwege und Beobachtungen auf Zeilenebene hinter der Zusammenfassung.

Eine Demo ist ein durchgearbeitetes Beispiel für die Methode von WSPRadar und keine Evidenz über die eigene Station. Sobald der Evidenzpfad vertraut ist, beginnt die erste sinnvolle Analyse der eigenen Station mit einer klaren Frage: eine RX- oder TX-Performance-Basislinie bestimmen, zwei kontrollierte lokale Pfade vergleichen, gegen eine bekannte Station benchmarken oder die Station in ihren lokalen WSPR-Kontext einordnen.

Ziel ist keine schmeichelhafte Zahl. Ziel ist ein Ergebnis, das sich verstehen, hinterfragen, wiederholen und für eine fundiertere Stationsentscheidung nutzen lässt.

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
    * [2.1 RX Performance](#sec-3-rx-performance)
    * [2.2 TX Performance](#sec-3-tx-performance)
    * [2.3 RX Benchmark](#sec-3-rx-benchmark)
        * [2.3.1 Hardware A/B: simultane Empfangspfade](#sec-3-rx-benchmark-hardware)
        * [2.3.2 Referenzstation / Buddy-Test](#sec-3-rx-benchmark-buddy)
        * [2.3.3 Lokaler Nachbarschafts-Median](#sec-3-rx-benchmark-local-median)
        * [2.3.4 Beste lokale Station](#sec-3-rx-benchmark-local-best)
    * [2.4 TX Benchmark](#sec-3-tx-benchmark)
        * [2.4.1 Hardware A/B: simultane Sendepfade](#sec-3-tx-benchmark-simultaneous)
        * [2.4.2 Hardware A/B: sequenzielle Sendepfade](#sec-3-tx-benchmark-sequential)
        * [2.4.3 Referenzstation / Buddy-Test](#sec-3-tx-benchmark-buddy)
        * [2.4.4 Lokaler Nachbarschafts-Median](#sec-3-tx-benchmark-local-median)
        * [2.4.5 Beste lokale Station](#sec-3-tx-benchmark-local-best)
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
    * [7.5 Leistungsnormierung, Korrektur und Benchmark-Delta-SNR](#sec-7-5)
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
* [8. Evidenzgerechte Aussagen und Reproduzierbarkeit](#sec-8)
    * [8.1 Aussageklassen und evidenzgerechte Formulierungen](#sec-8-1)
    * [8.2 Interpretationsgrenzen](#sec-8-2)
    * [8.3 Checkliste für Berichterstattung und Reproduzierbarkeit](#sec-8-3)
    * [8.4 Exportpaket der Analyse](#sec-8-4)
    * [8.5 Haftungsausschluss](#sec-8-5)
* [Literatur und Quellen](#sec-ref)

**Teil IV: Praktische Ergänzungen**

* [Anhang A: Parallele WSJT-X-Instanzen](#sec-a)
    * [A.1 Zweite Instanz anlegen](#sec-a-1)
    * [A.2 Ausgangskonfiguration bei Bedarf kopieren](#sec-a-2)
    * [A.3 Alle Datenpfade trennen](#sec-a-3)
    * [A.4 Unterscheidbares simultanes TX konfigurieren](#sec-a-4)
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

Dieser Teil führt von der betrieblichen Fragestellung zu einer evidenzgerechten Schlussfolgerung. Kapitel 1 schafft die gemeinsame Versuchsgrundlage, wählt RX oder TX sowie Performance oder Benchmark und führt den gemeinsamen Evidenzpfad ein. Kapitel 2 folgt diesem Pfad anschließend innerhalb der konkreten Analysefamilie und des jeweiligen Referenzdesigns. Kapitel 3 erläutert, wie ein Ergebnis abgesichert, berichtet und bewahrt wird. Die exakten Bedienelemente stehen in Teil II; genaue Berechnungen und wissenschaftliche Randfälle in Teil III.

In diesem Handbuch bezeichnet der **Versuch** den tatsächlichen Funkbetrieb und die physische Stationskonfiguration. Ein **Lauf** oder eine **Analyse** ist die in WSPRadar konfigurierte Verarbeitung der daraus entstandenen Beobachtungen. Ein **Ergebnis** ist die Performance- oder Benchmark-Evidenz, die dieser Lauf erzeugt.

---

<a id="sec-2"></a>

### 1. Analyse auswählen und vorbereiten

Beginne mit der Stationsfrage und dem physischen Versuch. Die Auswahl in der Benutzeroberfläche ergibt sich daraus; sie definiert die Fragestellung nicht.

<a id="sec-2-1"></a>

#### 1.1 Solide Versuchsgrundlage schaffen

Ein nützliches WSPRadar-Ergebnis beginnt mit einem Satz, der festhält, was geprüft wird und welche Beobachtung als Unterstützung gelten würde. Lege fest, ob der Lauf explorativ ist – also ein mögliches Muster aufspüren soll – oder ob er ein bereits erkanntes Muster bestätigend prüfen soll.

Verwende genau ein Band und ein UTC-Zeitfenster, in dem das Target tatsächlich in Betrieb war. Gib Rufzeichen exakt so ein, wie sie hochgeladen wurden, und prüfe das Target-QTH. Dokumentiere Antenne, Speiseleitung, Funkgerät, Tuner, Verstärkungs- oder Leistungseinstellungen, Decoder, Softwareversion, Zeitplan und jede beabsichtigte Änderung. Halte alle Variablen außerhalb der Fragestellung so stabil wie praktisch möglich.

Halte bei TX die tatsächliche und die gemeldete Sendeleistung korrekt und stabil, sofern nicht gerade die Leistung untersucht wird. Halte bei RX Verstärkung, Filterung, Audioführung, Decoder-Einstellungen und Upload-Verhalten stabil, sofern nicht einer dieser Punkte Gegenstand des Tests ist. Synchronisiere die Uhren. Prüfe bei Benchmark, ob die Referenz wie vorgesehen in Betrieb war: Das Target-Active Gate belegt eine beobachtbare Beteiligung des Targets, aber nicht die Betriebsbereitschaft der Referenz.

Lege vor einer bestätigenden Wiederholung Richtung, Band, Referenzdesign, Filter, Schwellen, Zeitplan und den primären geografischen oder zeitlichen Auswertungsbereich fest. Behandle alternative Radien, Zeitfenster oder Bereiche als getrennte Sensitivitätsanalysen, statt nur die günstigste Variante auszuwählen.

<a id="sec-2-2"></a>

#### 1.2 Die zur Fragestellung passende Analyse wählen

| Betriebliche Fragestellung | Analyse |
|---|---|
| Welche unabhängig bestätigten Signale decodiert mein Empfänger, wo, wann und wie beständig? | **RX Performance** |
| Wo und wie beständig wird mein Sender von Empfängern decodiert, deren Aktivität unabhängig nachgewiesen ist? | **TX Performance** |
| Wie unterscheiden sich zwei lokale Empfangspfade, zwei vollständige Empfangsstationen oder mein Empfänger und eine lokale Nachbarschaftsreferenz? | **RX Benchmark** |
| Wie unterscheiden sich zwei lokale Sendepfade, zwei vollständige Sendestationen oder mein Sender und eine lokale Nachbarschaftsreferenz? | **TX Benchmark** |

Wähle **Performance**, wenn das Target selbst Gegenstand der Frage ist und keine Referenz benötigt wird. Performance verbindet Mindestens-einmal-Reichweite, Dekodierrate, erfolgreiches Target-SNR, Geografie, Zeit und Evidenzunterstützung. Sie beschreibt die vollständige Target-Station unter den ausgewählten realen Betriebsbedingungen.

Wähle **Benchmark**, wenn die Frage ausdrücklich relativ zu einer Referenz gestellt wird. Die Referenz bestimmt die Bedeutung des Ergebnisses:

<a id="sec-2-5"></a>

* **Hardware A/B** ist das stärkste Design für eine Frage zu einem lokalen Bauteil oder Signalpfad. Es isoliert dieses Bauteil jedoch nur in dem Maß, in dem die übrigen Pfade kontrolliert sind.
* **Referenzstation / Buddy-Test** vergleicht vollständig aufgebaute Stationen und ihre Betriebsumgebungen.

<a id="sec-2-6"></a>

* **Lokaler Nachbarschafts-Median** vergleicht das Target mit einer wechselnden typischen lokalen Basislinie innerhalb des ausgewählten Radius.

<a id="sec-2-7"></a>

* **Beste lokale Station** vergleicht das Target auf jedem qualifizierenden Funkweg und in jedem Zyklus mit einem wechselnden stärksten lokalen Peer.

Verwende das engste Referenzdesign, das die beabsichtigte Aussage trägt. Aus einem Benchmark vollständiger Stationen oder einer Nachbarschaft lässt sich durch spätere Filterung oder Mittelung kein isolierter Antennengewinn ableiten.

<a id="sec-2-3-overview"></a>

#### 1.3 Dem Evidenzpfad folgen

Jedes abgeschlossene Ergebnis folgt demselben betrieblichen Pfad:

> <strong class="defined-term">Karte → Segment-Inspektor → Performance-/Benchmark-Evidenz → Zeitliche Evidenz → Station Insights → Evidenz der ausgewählten Station → Drill-Down</strong>

<a id="sec-3-4"></a>
<a id="sec-3-5"></a>

**Karte.** Lokalisiere das grobe Muster nach Entfernung und Richtung. Lies die Sektorfarbe stets zusammen mit der Unterstützung durch Stationen und Gelegenheiten, Spots beziehungsweise Paare. Ein eingefärbter Sektor ist eine Aufforderung zur näheren Prüfung und noch keine Schlussfolgerung.

<a id="sec-3-6"></a>
<a id="sec-3-6a"></a>
<a id="sec-3-6b"></a>

**Segment-Inspektor.** Wähle den zur Fragestellung passenden geografischen Bereich. Alle folgenden Evidenzansichten verwenden diesen aktiven Bereich. Dadurch lässt sich ein breites Kartenmuster in entfernungs- und richtungsabhängiges Verhalten aufteilen.

**Performance- oder Benchmark-Evidenz.** Verbinde bei Performance Reichweite, beide Gewichtungen der Dekodierrate und erfolgreiches Target-SNR. Verbinde bei Benchmark stationsgleichgewichtetes und beobachtungsbezogenes Delta SNR, Decode Outcomes und Joint-Evidenzanteil. Diese Größen beantworten unterschiedliche Fragen und sollten nicht zu einer einzigen Kennzahl verdichtet werden.

**Zeitliche Evidenz.** Nutze die chronologische Ansicht, um Veränderungen während des Laufs zu erkennen, und die UTC-Stunden-Ansicht, um wiederkehrende Tageszeitmuster über mehrere Tage zu sehen. Lies Signalpegel stets gemeinsam mit der Unterstützung durch Stationen, Gelegenheiten oder Paare.

<a id="sec-3-7"></a>
<a id="sec-3-7a"></a>
<a id="sec-3-7b"></a>

**Station Insights.** Prüfe, ob viele Identitäten aus `Rufzeichen + Locator` das Muster stützen oder ob es sich auf wenige Funkwege konzentriert. Lies jeden stationsbezogenen Wert zusammen mit seinen Evidenzanzahlen.

**Evidenz der ausgewählten Station.** Untersuche einen repräsentativen, überraschenden oder besonders einflussreichen Funkweg. So wird sichtbar, ob die Segmentzusammenfassung auch diesen Pfad beschreibt, ob er intermittierend ist und ob sein zeitliches Muster vom breiteren Bereich abweicht.

<a id="sec-3-8"></a>

**Drill-Down.** Prüfe die beibehaltenen Gelegenheiten, Vergleiche desselben Zyklus oder geplanten Paare hinter dem Ergebnis. Nutze Drill-Down, um Identitäten, Locatorwechsel, Zeitsteuerung, einseitige Evidenz und einzelne Ausreißer nachzuvollziehen.

Der übrige Teil von Teil I wendet diesen gemeinsamen Pfad auf jede Analysefrage an, ohne sämtliche Titel, Achsen oder Layoutdetails aufzulisten.

---

<a id="sec-3"></a>

### 2. Analyse durchführen und auswerten

Verwende den Abschnitt, der zur gewählten Richtung und zum Ergebnistyp passt. Exakte Bedienelemente, Standardwerte und Wertebereiche stehen in [Kapitel 4](#sec-5); genaue Zulässigkeit, Zuordnung, Gewichtung und Aggregation in [Kapitel 7](#sec-7).

<a id="sec-3-1"></a>
<a id="sec-3-2"></a>
<a id="sec-3-rx-performance"></a>

#### 2.1 RX Performance

**Beantwortete Frage.** Welche Zyklen entfernter Sender, die von einem anderen geeigneten Empfänger unabhängig bestätigt wurden, decodierte auch der Target-Empfänger; wie beständig gelang dies; welchen erfolgreichen SNR beobachtete er; und wo und wann trat dieses Verhalten auf?

**Minimal gültiger Aufbau.** Verwende das exakte Melderufzeichen und QTH des Targets, ein Band und ein Zeitfenster mit beobachtbarer Aktivität des Target-Empfängers. Halte die Empfangskette stabil. Performance führt keine Referenz ein und isoliert kein einzelnes Bauteil des Empfangssystems.

**Was WSPRadar auswertet.** Eine bestätigte RX-Gelegenheit liegt vor, wenn ein anderer geeigneter Empfänger denselben entfernten Sender im selben Target-aktiven Zyklus decodiert hat. `Vom Target gehört` bedeutet, dass auch das Target ihn decodiert hat; `Nur von anderen gehört` bedeutet, dass der unabhängige Empfänger ihn decodierte, das Target jedoch nicht. Evidenz ohne unabhängige Bestätigung bleibt prüfbar, geht aber nicht in die Dekodierrate ein. Die genaue Klassifikation steht in [Abschnitt 7.4](#sec-7-4).

**Dem Evidenzpfad folgen.** Auf der **Karte** zeigt die Sektorfarbe die stationsgleichgewichtete Dekodierrate der qualifizierenden entfernten Sender in jedem Entfernungs- und Richtungssegment. Stationsmarker und Kartenfuß unterscheiden Funkwege, die das Target mindestens einmal hörte, von Funkwegen, die nur andernorts gehört wurden. Nutze dies zunächst, um den groben RX-Empfangsbereich und Richtungsstrukturen zu lokalisieren – nicht, um allein aus der Farbe auf Empfängerempfindlichkeit zu schließen.

Vergleiche im **Segment-Inspektor** zunächst die Breite der Stationsbasis mit der Tiefe bestätigter Gelegenheiten. Viele Gelegenheiten von nur wenigen Sendern sind tiefe, aber schmale Evidenz; Übereinstimmung über viele Sender ist breiter abgestützt. Lies anschließend die drei Performance-Ansichten gemeinsam:

* **Mindestens-einmal-Reichweite** fragt, welche qualifizierenden Sender während des Zeitfensters mindestens einmal gehört wurden. Sie misst Breite und nimmt bei längeren Läufen normalerweise zu.
* **Dekodierrate** fragt, wie beständig das Target bestätigte Gelegenheiten decodierte. Die stationsgleichgewichtete Rate gibt jedem Sender eine Stimme; die Rate auf Gelegenheitsebene gibt jedem bestätigten Zyklus eine Stimme. Ein Unterschied zwischen beiden zeigt, dass Sender mit hohem Evidenzvolumen anders abschneiden als die breitere Stationspopulation.
* **Erfolgreiches Target-SNR** beschreibt nur erfolgreiche Decodes. Es hilft zu erkennen, ob sich die erfolgreich empfangenen Signalpegel mit der Entfernung verändern. Verpasste Gelegenheiten besitzen jedoch kein Target-SNR und können dort nicht erscheinen.

In der **Zeitlichen Evidenz** vergleicht die Abweichung des erfolgreichen SNR jeden Senderpfad mit seinem eigenen typischen erfolgreichen Pegel während des Laufs. Werte über `0 dB` bedeuten, dass erfolgreiche Decodes auf dem jeweiligen Pfad stärker als üblich waren; Werte unter `0 dB` bedeuten schwächere erfolgreiche Decodes. Die zugehörige Stations- und Gelegenheits-Evidenz zeigt, ob sich gleichzeitig die Dekodierrate änderte und wie breit das Muster gestützt ist. Die chronologische Ansicht erkennt Veränderungen im Lauf; die gefaltete UTC-Stunden-Ansicht wiederkehrendes Tagesverhalten.

Lies in **Station Insights** die Dekodierrate jedes Senders zusammen mit den Anzahlen `Vom Target gehört` und `Nur von anderen gehört`. Wähle einen typischen Funkweg, einen Ausreißer und jeden Pfad mit ungewöhnlich viel Evidenz. Die **Evidenz der ausgewählten Station** zeigt anschließend das tatsächliche erfolgreiche SNR und die Gelegenheitshistorie eines einzelnen Senderpfads statt der stationsbezogenen Zusammenfassung des Segments. **Drill-Down** prüft die beitragenden Zyklen und unterscheidet bestätigte Gelegenheiten von Target-Evidenz ohne unabhängige Bestätigung.

**Typische Interpretationsmuster.** Breite Reichweite bei hoher Dekodierrate bedeutet, dass viele Funkwege offen waren und beständig decodiert wurden. Breite Reichweite bei niedrigerer Dekodierrate bedeutet, dass viele Wege mindestens einmal offen, aber wechselhaft waren. Begrenzte Reichweite bei hoher Dekodierrate bedeutet, dass weniger qualifizierende Wege offen waren, diese jedoch vergleichsweise zuverlässig funktionierten. Bleibt das erfolgreiche SNR stabil oder steigt, während die Dekodierrate fällt, können schwächere Signale unter die Decode-Schwelle gefallen sein, sodass nur stärkere erfolgreiche Decodes übrig bleiben. Ein Muster, das auf einen Azimut, Entfernungsbereich oder UTC-Zeitraum begrenzt ist, kann betrieblich nützlich sein, beschreibt aber den installierten Empfänger unter diesen Funkwegen und Bedingungen und keine kontextfreie Empfindlichkeitskennzahl.

**Grenze und Bestätigung.** RX Performance umfasst Antenne, Speiseleitung, Empfänger, Verstärkung, Filterung, Decoder, lokalen Stör- und Rauschpegel sowie Ausbreitung. Sie misst weder Empfängerempfindlichkeit, Antennengewinn, absoluten Rauschpegel noch Ausbreitungsart direkt. Wiederhole ein vermutetes Muster in einem weiteren geeigneten Zeitfenster. Soll gezielt eine Hardwareänderung beurteilt werden, verwende einen kontrollierten RX Benchmark oder einen Kreuztausch statt nur zeitlich getrennter Vorher-Nachher-Performance-Läufe.

<p class="evidence-conclusion-label"><strong>Evidenzgerechte Schlussfolgerung.</strong></p>

<blockquote class="evidence-conclusion"><p>Für diesen Target-Empfänger, dieses Band, dieses UTC-Zeitfenster und die ausgewählte Senderpopulation beschreibt RX Performance die Mindestens-einmal-Reichweite, die Dekodierrate innerhalb unabhängig bestätigter Senderzyklen, das SNR erfolgreicher Decodes sowie den geografischen und zeitlichen Umfang dieser Beobachtungen. Nenne die verwendete Gewichtung, die Unterstützung durch Stationen und Gelegenheiten und ob das Muster breit, intermittierend, richtungsabhängig, entfernungsabhängig oder wiederkehrend war.</p></blockquote>

<a id="sec-3-tx-performance"></a>

#### 2.2 TX Performance

**Beantwortete Frage.** Welche entfernten Empfänger, deren Aktivität unabhängig nachgewiesen ist, decodierten den Target-Sender; wie beständig taten sie dies; welchen erfolgreichen SNR meldeten sie; und wo und wann trat dieses Verhalten auf?

**Minimal gültiger Aufbau.** Verwende das exakte Target-Rufzeichen und QTH, ein Band und ein Zeitfenster, in dem der Target-Sender in Betrieb war. Halte HF-Pfad, Zeitplan und tatsächliche Leistung stabil und melde die Leistung korrekt. Performance wertet die vollständige Sendestation aus und nicht ein isoliertes Bauteil.

**Was WSPRadar auswertet.** Eine bestätigte TX-Gelegenheit liegt vor, wenn der entfernte Empfänger während eines Target-Sendezyklus aktiv war, nachgewiesen durch einen anderen qualifizierenden Decode auf demselben Band. `Target gehört` bedeutet, dass dieser Empfänger auch das Target decodierte; `Nur andere Signale gehört` bedeutet, dass er qualifizierende Aktivität auf demselben Band, aber nicht das Target decodierte. Eine Target-Meldung ohne unabhängige Bestätigung der Empfängeraktivität bleibt prüfbar, geht jedoch nicht in die Dekodierrate ein. Der genaue Nenner steht in [Abschnitt 7.4](#sec-7-4).

**Dem Evidenzpfad folgen.** Auf der **Karte** zeigt die Sektorfarbe die stationsgleichgewichtete Dekodierrate qualifizierender aktiver Empfänger in jedem Entfernungs- und Richtungssegment. Marker und Anzahlen am Kartenfuß unterscheiden Empfänger, die das Target mindestens einmal hörten, von Empfängern, die nur andere qualifizierende Signale hörten. Nutze die Karte, um den praktischen Sendefußabdruck und Richtungsstrukturen zu lokalisieren.

Vergleiche im **Segment-Inspektor** die Breite der Empfängerbasis mit der Tiefe bestätigter Gelegenheiten und lies anschließend die drei Performance-Ansichten gemeinsam:

* **Mindestens-einmal-Reichweite** fragt, welche qualifizierenden aktiven Empfänger das Target während des Zeitfensters mindestens einmal hörten.
* **Dekodierrate** fragt, wie beständig das Target innerhalb bestätigter Empfängergelegenheiten gemeldet wurde. Die stationsgleichgewichtete und die gelegenheitsbezogene Rate zeigen, ob häufig meldende Empfänger anders abschneiden als die breitere Empfängerpopulation.
* **Erfolgreiches Target-SNR** zeigt das auf die gemeldete Leistung normierte SNR erfolgreicher Target-Meldungen. Es ist an einen erfolgreichen Decode gebunden und hängt von der Richtigkeit der gemeldeten Sendeleistung ab.

In der **Zeitlichen Evidenz** zeigt die Abweichung des erfolgreichen SNR, wann erfolgreiche Meldungen stärker oder schwächer waren als der jeweils typische erfolgreiche Pegel des Empfängerpfads. Die zugehörigen Stations- und Gelegenheitsstapel zeigen, ob eine Veränderung des erfolgreichen SNR mit einer Veränderung der praktischen Decodierbarkeit einherging und wie viel Evidenz jedes Zeit-Bin stützt. Unterscheide Veränderungen im chronologischen Verlauf von wiederkehrendem Verhalten nach UTC-Stunde.

Lies in **Station Insights** die Rate jedes Empfängers zusammen mit seinen Anzahlen `Target gehört` und `Nur andere Signale gehört`. Die **Evidenz der ausgewählten Station** legt für einen Empfängerpfad das tatsächliche erfolgreiche SNR und die Gelegenheitshistorie offen. So wird sichtbar, ob die Segmentzusammenfassung viele Empfänger beschreibt oder einen funkwegspezifischen Effekt verdeckt. **Drill-Down** prüft Target-Meldungen, unabhängige Empfängeraktivität und Target-Meldungen ohne unabhängigen Nachweis der Empfängeraktivität.

**Typische Interpretationsmuster.** Breite Reichweite und hohe Dekodierrate bedeuten, dass viele qualifizierende aktive Empfänger das Target beständig hörten. Breite Reichweite bei niedrigerer Dekodierrate beschreibt einen großen, aber wechselhaften Fußabdruck. Ein anhaltender Vorteil in einem Azimut oder Entfernungsbereich kann mit dem installierten Antennensystem und Gelände vereinbar sein; eine kurze isolierte Verbesserung kann dagegen durch Ausbreitung oder Empfängerverfügbarkeit verursacht sein. Ein stabiles erfolgreiches SNR bei fallender Dekodierrate kann bedeuten, dass nur stärkere überlebende Meldungen verbleiben. Unterschiede zwischen stationsgleichgewichteter und gelegenheitsbezogener Rate zeigen, ob wenige Empfänger mit hohem Evidenzvolumen die gepoolte Sicht prägen.

**Grenze und Bestätigung.** TX Performance umfasst Sender, tatsächliche Leistung, Speiseleitung, Anpassung, Antenne, Gelände, entfernte Empfangssysteme, lokalen Störpegel und Ausbreitung. Eine Normierung anhand der gemeldeten Leistung kann weder eine falsche Leistungsangabe noch einen ungemessenen Speiseleitungsverlust korrigieren. Das Ergebnis misst EIRP, Wirkungsgrad, Antennengewinn oder Abstrahlwinkel nicht direkt. Wiederhole das Muster in einem weiteren geeigneten Zeitfenster; verwende TX Benchmark, wenn die konkrete Frage lautet, ob sich ein Sendepfad von einem anderen unterscheidet.

<p class="evidence-conclusion-label"><strong>Evidenzgerechte Schlussfolgerung.</strong></p>

<blockquote class="evidence-conclusion"><p>Für diesen Target-Sender, dieses Band, dieses UTC-Zeitfenster und die ausgewählte Population aktiver Empfänger beschreibt TX Performance die Mindestens-einmal-Reichweite, die Dekodierrate innerhalb unabhängig bestätigter Empfängerzyklen, das erfolgreich gemeldete SNR sowie den geografischen und zeitlichen Umfang dieser Beobachtungen. Nenne Gewichtung, Unterstützung durch Empfänger und Gelegenheiten, die Grundlage der gemeldeten Leistung und ob das Muster breit, intermittierend, richtungsabhängig, entfernungsabhängig oder wiederkehrend war.</p></blockquote>

<a id="sec-3-3"></a>
<a id="sec-3-rx-benchmark"></a>

#### 2.3 RX Benchmark

**Beantwortete Frage.** Wie unterschied sich die Target-Empfangsseite von der ausgewählten Referenz, während beide dieselben entfernten Senderidentitäten in denselben WSPR-Zyklen beobachteten?

**Gemeinsame RX-Benchmark-Evidenz.** Gepaarte Delta-SNR-Werte entstehen nur dort, wo Target und Referenz vergleichbare Evidenz für denselben Sender im selben Zyklus lieferten. Positives Delta SNR spricht für das Target, negatives für die Referenz. Decode Outcomes bewahren Joint, Only Target, Only Reference und asynchrone Evidenz um diese gepaarte Teilmenge. Der Joint-Evidenzanteil beschreibt, wie viel der beibehaltenen Evidenz paarbar war; er ist keine Gewinnquote. Die Betriebsbereitschaft der Referenz muss unabhängig bekannt sein, und das Target-Active Gate macht die einseitigen Kategorien bewusst asymmetrisch.

**Dem Evidenzpfad folgen.** Auf der **Karte** fasst die Sektorfarbe den stationsgleichgewichteten Median des Delta SNR der entfernten Sender in jedem Entfernungs- und Richtungssegment zusammen. Markerkategorien zeigen, ob eine Senderidentität Joint- oder einseitige Evidenz beitrug. Lies die Farbe zusammen mit Stations- und Spotanzahlen: Ein auffälliger Sektor, der nur von wenigen Sendern gestützt wird, ist schmalere Evidenz als ein ähnliches Ergebnis über viele Funkwege.

Im **Segment-Inspektor** zeigen Decode Outcomes zwei ergänzende Zusammensetzungen: die Breite über Stationen und das Beobachtungsvolumen. Stationsmediane geben jedem entfernten Sender genau einen Delta-SNR-Wert und damit dasselbe Gewicht. Die Verteilung der Joint Spots zeigt jede gepaarte Beobachtung und kann von Sendern mit vielen Meldungen geprägt werden. Stimmen beide überein, spricht das für eine breite Verschiebung; weichen sie ab, erzählen Beobachtungsvolumen und Stationsbreite unterschiedliche Geschichten.

Die **Zeitliche Evidenz** zeigt, ob sich das gepaarte Delta SNR während des Laufs veränderte oder nach UTC-Stunde wiederkehrte. Lies sie zusammen mit der Abdeckung der Benchmark-Evidenz: Ein Delta-SNR-Muster mit breiter Joint-Abdeckung ist etwas anderes als ein Muster, das nur in einer dünnen gepaarten Teilmenge sichtbar ist. Einseitige Evidenz kann praktische Unterschiede nahe der Decode-Schwelle aufdecken, die gepaartes Delta SNR allein nicht beschreibt; sie liefert jedoch kein SNR der fehlenden Seite.

Prüfe in **Station Insights** für jeden Sender die Joint- und einseitigen Anzahlen zusammen mit seinem medianen Delta SNR. Die **Evidenz der ausgewählten Station** zeigt für einen Senderpfad gepaartes Delta SNR und Evidenzabdeckung im Zeitverlauf. So lässt sich ein repräsentativer Funkweg von einem Ausreißer oder intermittierenden Pfad unterscheiden. **Drill-Down** prüft, ob Target- und Referenzzeilen den beabsichtigten Sender, Zyklus sowie die richtigen Rufzeichen- und Locatoridentitäten treffen und ob die konfigurierte Korrektur das erwartete Vorzeichen besitzt.

**Typische Interpretationsmuster.** Eine Verteilung der Stationsmediane überwiegend auf einer Seite von null, breite Joint-Abdeckung und Wiederkehr über Zeit oder benachbarte Segmente stützen einen beständigen Unterschied der vollständigen Pfade. Eine Verschiebung der gepoolten Joint Spots ohne entsprechende Verschiebung der Stationsmediane kann durch wenige besonders aktive Sender verursacht sein. Ein klarer gepaarter Median zusammen mit vielen Only-Target- oder Only-Reference-Outcomes bedeutet, dass der gepaarte Signalstärkeunterschied nur einen Teil der praktischen Decode-Evidenz beschreibt. Ein Unterschied, der auf eine Richtung oder UTC-Zeit begrenzt ist, kann real und nützlich sein, bleibt aber funkweg- oder bedingungsabhängig.

**Grenze und Bestätigung.** Die gepaarte Analyse ist darauf konditioniert, dass beide Seiten vergleichbare Evidenz erzeugen, und kann daher nicht sämtliche verpassten Signale beschreiben. Die Zuordnung im selben Zyklus kontrolliert den entfernten Sender und die Zeit, beseitigt aber Unterschiede von lokaler Empfängerkette, Antenne, Störumgebung oder QTH nicht. Stärke das Ergebnis durch ausreichend viele Joint-Stationen, unabhängig bekannte Referenzbetriebszeiten, Wiederholung und die nachfolgend beschriebene designspezifische Kontrolle.

<a id="sec-2-3"></a>
<a id="sec-3-rx-benchmark-hardware"></a>

##### 2.3.1 Hardware A/B: simultane Empfangspfade

Verwende dieses Design für zwei lokale Antennen, Speiseleitungen, Filter, Vorverstärker, Empfänger oder vollständige Empfangsketten, die gleichzeitig am selben physischen Test-QTH betrieben werden. Target und Referenz benötigen unterschiedliche exakte Melderufzeichen und dasselbe Target-Grid-4. Komponenten, die gemeinsam sein sollen, müssen physisch gemeinsam genutzt werden; die Zuordnung zum selben Grid-4 beweist weder Ko-Lokation noch Gleichheit der Pfade.

Dies ist das stärkste RX-Design, um einen Unterschied einem lokalen Pfad zuzuordnen. Sofern Unterschiede bei Empfänger, Audio, Verstärkung, Decoder und Signalführung nicht charakterisiert wurden, vergleicht das Ergebnis weiterhin die vollständigen dokumentierten Empfangspfade. Eine breite, wiederkehrende Delta-SNR-Verschiebung zusammen mit dazu passender einseitiger Evidenz stützt die Aussage, dass ein Pfad unter den geprüften Bedingungen besser abschnitt. Eine Kalibrierung mit gemeinsamem Eingang, ein Tausch der Verteilerausgänge oder ein Hardware-Kreuztausch ist die nützlichste Bestätigung, weil dadurch das Prüfobjekt von einem dauerhaften Kettenoffset getrennt werden kann. [Anhang C](#sec-c) beschreibt die Referenz-SNR-Kalibrierung.

<blockquote class="evidence-conclusion"><p>Unter dem dokumentierten simultanen RX-Hardware-A/B-Aufbau beschrieben gepaartes Delta SNR und Decode Outcomes den beobachteten Unterschied zwischen Target- und Referenzempfangspfad für die gemeinsamen Sender, Zyklen und den ausgewählten geografischen Bereich.</p></blockquote>

<a id="sec-3-rx-benchmark-buddy"></a>

##### 2.3.2 Referenzstation / Buddy-Test

Verwende einen bekannten externen Empfänger, dessen QTH, Identität, Ausrüstung, Betriebsplan und lokale Umgebung verstanden sind. RX-Paare teilen denselben entfernten Sender und Zyklus; die beiden Empfangsstationen bleiben jedoch an unterschiedlichen QTHs mit verschiedenen Antennen, Gelände-, Geräte- und Störbedingungen.

Interpretiere dies als Benchmark vollständiger installierter Empfangsstationen. Er kann zeigen, wo eine Station relativ stärker war, wie sich das Verhältnis nach Richtung, Entfernung oder Zeit veränderte und ob sich die einseitige Reichweite unterschied. Er kann nicht isolieren, ob Empfängerempfindlichkeit, Antennengewinn oder lokaler Störpegel die Ursache war. Eine Wiederholung mit demselben gut verstandenen Buddy und stabilen Betriebsbedingungen ist die nützlichste Bestätigung.

<blockquote class="evidence-conclusion"><p>Für die gemeinsamen Senderpfade und Zyklen dieses Laufs beschrieben gepaartes Delta SNR und Decode Outcomes, wie sich die beiden vollständigen Empfangsstationen unter ihren jeweiligen Umgebungsbedingungen verglichen.</p></blockquote>

<a id="sec-3-rx-benchmark-local-median"></a>

##### 2.3.3 Lokaler Nachbarschafts-Median

Die Referenz ist der zyklus- und funkwegspezifische Median aus je einem Beitrag jeder aktiven lokalen Empfängeridentität innerhalb des ausgewählten Radius. Die Zusammensetzung kann sich von Zyklus zu Zyklus ändern; das Ergebnis ist daher eine kontextbezogene lokale Basislinie und kein Vergleich mit einer festen Station.

Prüfe die beitragenden lokalen Identitäten, den Joint-Evidenzanteil und die Radiusabhängigkeit. Eine Veränderung kann vom Target, von einer veränderten Zusammensetzung der Nachbarschaft oder von beidem ausgehen. Wähle den primären Radius vor der Interpretation anhand lokaler Geografie und Stationsdichte; verwende weitere begründbare Radien als Sensitivitätsanalysen.

<blockquote class="evidence-conclusion"><p>Relativ zum aktiven medianen Empfangsumfeld innerhalb des ausgewählten Radius zeigte das Target für die beobachteten Senderpfade und Zyklen das berichtete gepaarte Delta SNR und die berichteten Decode Outcomes.</p></blockquote>

<a id="sec-3-rx-benchmark-local-best"></a>

##### 2.3.4 Beste lokale Station

Die Referenz ist die stärkste qualifizierende lokale Empfangsevidenz, die für jeden entfernten Senderpfad und Zyklus verfügbar ist. Die gewinnende lokale Identität kann fortlaufend wechseln. Dadurch entsteht eine anspruchsvolle Best-Peer-Hüllkurve statt eines lokalen Durchschnitts oder eines festen Konkurrenten.

Prüfe, welche lokale Station die Referenz liefert und ob der beobachtete Abstand breit auftritt oder sich auf wenige Gewinner konzentriert. Radius und Poolzusammensetzung bleiben Bestandteil des Ergebnisses. Berichte es als Abstand des Targets zum wechselnden stärksten lokalen Empfänger und nicht als Rangliste gegenüber einer festen Station.

<blockquote class="evidence-conclusion"><p>Relativ zum stärksten qualifizierenden lokalen Empfänger, der innerhalb des angegebenen Radius für jeden Funkweg und Zyklus ausgewählt wurde, zeigte das Target das berichtete gepaarte Delta SNR und die berichteten Decode Outcomes.</p></blockquote>

<a id="sec-3-tx-benchmark"></a>

#### 2.4 TX Benchmark

**Beantwortete Frage.** Wie unterschied sich der Target-Sender beziehungsweise der geplante Target-Pfad von der ausgewählten Referenz an gemeinsamen entfernten Empfängern?

**Gemeinsame TX-Benchmark-Evidenz.** Ein TX-Benchmark im selben Zyklus vergleicht Target und Referenz am selben entfernten Empfänger im selben WSPR-Zyklus. Sequenzielles Hardware A/B verwendet stattdessen deterministische geplante Paare am selben Empfänger. Erfolgreiches TX-SNR wird vor der Bildung des Delta SNR auf die gemeldete Leistung normiert; das Ergebnis hängt daher unmittelbar von korrekten Leistungsangaben ab. Decode Outcomes bewahren Joint- und einseitige Evidenz. Eine exklusive Beobachtung besitzt jedoch kein SNR der fehlenden Seite und wird nicht als Paar leistungsnormiert.

**Dem Evidenzpfad folgen.** Auf der **Karte** fasst die Sektorfarbe das stationsgleichgewichtete mediane Delta SNR über entfernte Empfänger zusammen. Marker- und Kartenfußkategorien zeigen Joint- und einseitige Empfängerevidenz. Lies jeden Sektor zusammen mit der Breite über Empfänger sowie der Tiefe durch Spots oder geplante Paare.

Vergleiche im **Segment-Inspektor** die stationsbezogenen Decode Outcomes mit der Zusammensetzung auf Beobachtungs- beziehungsweise Paarebene. Stationsmediane geben jedem entfernten Empfänger eine gleich große Stimme; die Delta-SNR-Verteilung der Joint Spots oder geplanten Paare zeigt die vollständige gepaarte Beobachtungspopulation. Eine Verschiebung über viele Empfänger ist andere Evidenz als ein Ergebnis, das von wenigen Empfängern mit hohem Datenvolumen dominiert wird.

Die **Zeitliche Evidenz** zeigt, ob sich Delta SNR im Verlauf des Laufs veränderte oder nach UTC-Stunde wiederkehrte. Die Abdeckung der Benchmark-Evidenz zeigt, ob die gepaarte Evidenz während dieser Zeiten breit blieb. Prüfe beim sequenziellen TX, ob das Ergebnis an eine Zeitplanphase oder Schaltperiode gebunden ist; prüfe beim simultanen TX, ob es vor allem an einem Empfänger, einer Audiofrequenzzuordnung oder einem kurzen Zeitraum auftritt.

Lies in **Station Insights** das mediane Delta SNR jedes Empfängers zusammen mit seinen Joint- und einseitigen Anzahlen. Die **Evidenz der ausgewählten Station** legt das gepaarte Ergebnis und die Evidenzabdeckung an einem Empfängerpfad offen. **Drill-Down** prüft Empfängeridentität, gemeldete Leistungen, Paarbildung im selben Zyklus oder Zuordnung geplanter Paare sowie das Vorzeichen der Korrektur.

**Typische Interpretationsmuster.** Eine beständige Verschiebung der Stationsmediane über viele Empfänger, Richtungen und Zeiten stützt einen breiten Unterschied der vollständigen Sendepfade. Eine auf einen Azimut oder Entfernungsbereich begrenzte Verschiebung kann nützliches installiertes Richtverhalten anzeigen, ohne zu einem kontextfreien Gewinnwert zu werden. Starkes gepaartes Delta SNR bei umfangreicher einseitiger Evidenz bedeutet, dass sowohl der Signalstärkeunterschied als auch die praktische Reichweite nahe der Schwelle berichtet werden müssen. Weicht der Median der Rohpaare von der Stationsmedian-Ansicht ab, gewichten Empfänger mit hohem Datenvolumen die Beobachtungsevidenz anders.

**Grenze und Bestätigung.** TX Benchmark bleibt auf paarbare Evidenz und korrekte Leistungsangaben konditioniert. Simultane Designs behalten Unterschiede der Sendeketten bei Leistung, Frequenzgang, Entkopplung und Kopplung bei. Sequenzielle Designs bleiben zeitlich getrennt. Einseitige Evidenz im selben Zyklus wird außerdem vom Target-Active Gate beeinflusst. Stärke das Ergebnis durch breite Empfängerunterstützung, genaue Leistungsmessung, Wiederholung und die nachfolgend beschriebenen methodenspezifischen Kontrollen.

<a id="sec-2-4"></a>
<a id="sec-2-4-simultaneous"></a>
<a id="sec-3-tx-benchmark-simultaneous"></a>

##### 2.4.1 Hardware A/B: simultane Sendepfade

Verwende zwei unterscheidbare Sendeketten und Rufzeichen am selben physischen Test-QTH, die bewusst in denselben WSPR-Zyklen synchronisiert und auf freien, nicht überlappenden Frequenzen innerhalb des WSPR-Durchlassbereichs platziert werden. Miss oder bestimme die tatsächliche Leistung an dem für die Fragestellung relevanten Vergleichspunkt und sorge für ausreichende Entkopplung zwischen den aktiven Sendern und Antennen.

Delta SNR am selben Empfänger und im selben Zyklus beseitigt den zeitlichen Abstand des sequenziellen Designs und ist das stärkste TX-Design, wenn sich beide Sendeketten kontrollieren lassen. Es vergleicht dennoch die vollständigen dokumentierten Sendepfade. Frequenzselektives QRM, Kettenfrequenzgang, Kopplung und Leistungsfehler können bestehen bleiben. Tausche die Audiofrequenzzuordnungen und führe nach Möglichkeit einen Kreuztausch der geprüften Antennen oder Bauteile zwischen den Ketten durch. [Anhang A](#sec-a) behandelt den parallelen WSJT-X-Betrieb.

<blockquote class="evidence-conclusion"><p>Unter dem dokumentierten simultanen Hardware-A/B-Aufbau mit zwei Sendern beschrieben Delta SNR am selben Empfänger und im selben Zyklus sowie Decode Outcomes den beobachteten Unterschied zwischen Target- und Referenzsendepfad für die ausgewählten Empfänger und den geografischen Bereich.</p></blockquote>

<a id="sec-2-4-sequential"></a>
<a id="sec-2-4-why"></a>
<a id="sec-3-tx-benchmark-sequential"></a>

##### 2.4.2 Hardware A/B: sequenzielle Sendepfade

Verwende einen deterministischen Zeitplan, der vollständige WSPR-Aussendungen Target- und Referenzphasen zuordnet. Ein Sender, der zwischen zwei HF-Pfaden umgeschaltet wird, ist normalerweise der stärkste Aufbau, weil Rufzeichen, Frequenzreferenz und Sender gemeinsam bleiben. Trage die tatsächliche Wiederkehr und UTC-Phase jedes Pfads ein, prüfe die physische Zuordnung des Zeitplans zu den Pfaden ohne HF und melde die tatsächliche Leistung. Gerätespezifische Hinweise zu Zeitplanung und Umschaltung stehen in [Anhang B](#sec-b).

WSPRadar bildet automatisch eindeutige geplante A/B-Paare. Das Paar-Delta bleibt sequenziell: Kurzes, ausgewogenes Abwechseln verringert Unterschiede durch Ausbreitung, Störungen, Zeitplanposition und Umschaltung, beseitigt sie aber nicht. Prüfe unvollständige Paare und den chronologischen Verlauf zusammen mit dem gepaarten Median. Vertausche in einem bestätigenden Lauf die Target- und Referenzzeitplanphasen; bleibt der Vorteil des physischen Pfads nach dem Rollentausch bestehen, ist dies wesentlich überzeugender als eine Wiederholung mit derselben Phasenzuordnung.

<blockquote class="evidence-conclusion"><p>Unter dem dokumentierten deterministischen Zeitplan beschrieben das Delta SNR geplanter Paare und die einseitigen Paar-Outcomes den beobachteten Unterschied zwischen den geschalteten Target- und Referenzpfaden für die ausgewählten Empfänger, Zeiten und den geografischen Bereich.</p></blockquote>

<a id="sec-3-tx-benchmark-buddy"></a>

##### 2.4.3 Referenzstation / Buddy-Test

Verwende einen bekannten externen Sender, dessen QTH, Identität, tatsächliche und gemeldete Leistung, Ausrüstung und Betriebsplan verstanden sind. TX-Paare teilen denselben entfernten Empfänger und Zyklus; Target und Referenz bleiben jedoch vollständige Stationen an unterschiedlichen QTHs mit verschiedenen Antennen, Speiseleitungen, Gelände- und Funkwegen.

Interpretiere das Ergebnis als Benchmark vollständiger installierter Sendestationen. Die Paarbildung am selben Empfänger kontrolliert den Empfangsendpunkt, nicht die beiden Sendestandorte oder Funkwege. Die Genauigkeit der Leistungsangaben ist besonders wichtig. Wiederhole den Lauf mit demselben gut verstandenen Buddy und stabilen Konfigurationen, statt die Buddy-Station als absolut kalibrierten Standard zu behandeln.

<blockquote class="evidence-conclusion"><p>Für die gemeinsamen Empfangsstationen und Zyklen dieses Laufs beschrieben gepaartes Delta SNR und Decode Outcomes, wie sich die beiden vollständigen Sendestationen unter ihren jeweiligen Betriebsumgebungen verglichen.</p></blockquote>

<a id="sec-3-tx-benchmark-local-median"></a>

##### 2.4.4 Lokaler Nachbarschafts-Median

Die Referenz ist der zyklus- und empfängerpfadspezifische Median aus je einem Beitrag jeder aktiven lokalen Senderidentität innerhalb des ausgewählten Radius. Sie ist eine wechselnde lokale Basislinie und keine feste Station. Das Ergebnis hängt von der aktiven Zusammensetzung und von der Genauigkeit der gemeldeten Leistungen ab.

Prüfe die lokalen Beitragenden, den Joint-Evidenzanteil und die Radiusabhängigkeit. Berichte, ob das Target bei bestimmten Empfängern, Richtungen oder Zeiten eher über, nahe oder unter der aktiven lokalen Basislinie liegt. Eine Veränderung kann vom Target, vom lokalen Pool oder von beidem ausgehen.

<blockquote class="evidence-conclusion"><p>Relativ zum aktiven medianen Sendeumfeld innerhalb des ausgewählten Radius zeigte das Target für die beobachteten Empfängerpfade und Zyklen das berichtete gepaarte Delta SNR und die berichteten Decode Outcomes.</p></blockquote>

<a id="sec-3-tx-benchmark-local-best"></a>

##### 2.4.5 Beste lokale Station

Die Referenz ist die stärkste qualifizierende lokale Sendeevidenz, die nach Anwendung der zutreffenden Korrektur an jedem entfernten Empfänger und in jedem Zyklus verfügbar ist. Die gewinnende lokale Identität kann fortlaufend wechseln. Dadurch entsteht eine Best-Peer-Hüllkurve statt eines lokalen Durchschnitts oder eines festen Konkurrenten.

Prüfe, welche Station die Referenz liefert, welche Leistung sie meldet und ob der Abstand des Targets über Empfänger, Entfernung, Richtung und Zeit bestehen bleibt. Berichte das Ergebnis als Vergleich mit einem wechselnden stärksten lokalen Sender innerhalb des angegebenen Radius.

<blockquote class="evidence-conclusion"><p>Relativ zum stärksten qualifizierenden lokalen Sender, der innerhalb des angegebenen Radius für jeden Empfängerpfad und Zyklus ausgewählt wurde, zeigte das Target das berichtete gepaarte Delta SNR und die berichteten Decode Outcomes.</p></blockquote>

<a id="sec-3-9"></a>

---

<a id="sec-4"></a>

### 3. Ergebnis absichern und kommunizieren

Ein belastbares WSPRadar-Ergebnis verbindet einen klaren Versuch, breite Evidenz und eine Formulierung, die genau zur tatsächlichen Beobachtung passt.

<a id="sec-4-1"></a>

#### 3.1 Breite, Konsistenz und Wiederholbarkeit beurteilen

Beurteile das Ergebnis anhand des vollständigen Evidenzbildes:

* Identitäten der beteiligten Stationen;
* Umfang der qualifizierenden bestätigten Gelegenheiten, Spots oder geplanten Paare;
* Übereinstimmung zwischen Stationen;
* stationsgleichgewichtete und beobachtungsbezogene Zusammenfassungen;
* benachbarte geografische Segmente;
* zeitliche Ansichten;
* Decode Outcomes;
* Qualität von Identitäten und Locator-Angaben;
* Kontrolle und Wiederholung des Versuchs.

Evidenz ist **breiter**, wenn mehrere Identitäten und benachbarte Segmente übereinstimmen. Sie ist **innerhalb des Laufs konsistenter**, wenn stationsgleichgewichtete, beobachtungsbezogene und zeitliche Ansichten ein vereinbares Bild ergeben. Sie ist **besser kontrolliert**, wenn die betrieblichen Anforderungen des gewählten Leitfadens eingehalten und dokumentiert wurden.

**Konsistenz innerhalb eines Laufs und experimentelle Wiederholbarkeit sind verschieden.** Die Übereinstimmung von stationsgleichgewichteten, beobachtungsbezogenen, geografischen und zeitlichen Ansichten beschreibt die Evidenz innerhalb eines Laufs. Eine Wiederholung des Versuchs in einem weiteren geeigneten Zeitfenster prüft, ob das beobachtete Muster unter neuen Betriebs- und Ausbreitungsbedingungen Bestand hat.

WSPRadar verdichtet diese Dimensionen bewusst nicht zu einer einzigen Beweisstufe. Die sichtbaren Anzahlen, Verteilungen und zugrunde liegenden Zeilen ermöglichen eine Beurteilung im Kontext des tatsächlich durchgeführten Versuchs.

Das beobachtete zeitliche, entfernungs- oder richtungsabhängige Muster der Dekodierrate, des erfolgreichen SNR oder des Delta SNR ist die Evidenz. Eine Erklärung wie Antennenrichtwirkung, veränderter lokaler Störpegel, Ausbreitungsart, Übersteuerung oder ein intermittierendes Bauteil ist eine Interpretation. Formuliere zuerst passend zur Beobachtung und prüfe die Erklärung anschließend durch eine kontrollierte Änderung, einen Kreuztausch, eine unabhängige Messung oder Wiederholung.

<a id="sec-4-2"></a>

#### 3.2 Ergebnis durch Wiederholung und Kontrolle absichern

Nutze einen ersten explorativen Lauf, um ein mögliches Muster zu erkennen. Lege vor einer bestätigenden Wiederholung Richtung, Band, Benchmark, Filter, Evidenzschwellen, Zeitplan und den primären geografischen oder zeitlichen Auswertungsbereich einschließlich `Maximale Peer-Entfernung vom Target (km)` gemäß [Abschnitt 4.4](#sec-5-4) fest. Führe alternative Maximalentfernungen als getrennt bewahrte Sensitivitätsanalysen aus, statt nach Betrachtung des Ergebnisses nur den günstigsten Bereich auszuwählen.

Wenn das Ergebnis eine wichtige Stationsentscheidung stützen soll:

* dehne das Beobachtungsfenster über die Ausbreitungszustände aus, die in der Schlussfolgerung genannt werden;
* bevorzuge für Aussagen über vollständige Tageszyklen mehrtägige Evidenz;
* wiederhole den Versuch an einem anderen Tag oder während einer anderen Ausbreitungsphase;
* vertausche bei sequenziellem TX Hardware A/B die Target- und Referenzzeitplanphasen;
* halte nicht untersuchte Variablen zwischen den Wiederholungen stabil;
* vergleiche Läufe mit derselben Richtung, demselben Band, Benchmark, denselben Filtern und Evidenzschwellen;
* untersuche jede Identität, jeden Locator oder kurzen Zeitraum, der einen großen Anteil der Evidenz liefert;
* bewahre Aufbaunotizen auf, damit ein späterer Lauf die Stationskonfiguration reproduzieren kann.

Kleine beobachtete Unterschiede werden nützlicher, wenn sie über Stationen, Zeiträume, benachbarte Segmente und kontrollierte Wiederholungen erneut auftreten. Eine vertauschte Zuordnung bei sequenziellem TX ist besonders aufschlussreich, weil sie Zeitplan-, Schaltpfad- oder Zykluspositionseffekte sichtbar machen kann, die bei einer gewöhnlichen Wiederholung in derselben Rolle verbleiben.

TX und RX verwenden unterschiedliche Peer-Populationen und Gelegenheitsdefinitionen. Vergleiche gleichartige TX- und RX-Läufe, wenn du die Stationsbalance oder ein „Alligator“-Muster untersuchst.

<a id="sec-4-3"></a>

#### 3.3 Evidenzgerechte Schlussfolgerung formulieren

Eine minimale betriebliche Aussage nennt das Target und bei Benchmark gegebenenfalls die feste Referenz oder die lokale Benchmark-Definition. Außerdem nennt sie TX- oder RX-Richtung, Band, UTC-Zeitfenster, geografischen Bereich, Ergebnistyp, angezeigten Wert und die stützende Stations- beziehungsweise Evidenzanzahl.

Ein vollständiger technischer Bericht nennt zusätzlich:

* die zutreffenden Gewichtungsebenen: stationsgleichgewichtete Dekodierrate und Dekodierrate auf Gelegenheitsebene bei Performance beziehungsweise Delta SNR auf Stations- und Beobachtungsebene bei Benchmark;
* bei Performance die Anzahl qualifizierender Stationen und bestätigter Gelegenheiten, bei Benchmark die Anzahl der Joint-Stationen und Joint-Spots beziehungsweise -Paare;
* Decode Outcomes bei Benchmark;
* Versuchsbedingungen und eine etwaige Referenzkorrektur;
* Filter und Evidenzschwellen;
* ob sich das Muster über Zeit, Stationen oder Läufe wiederholte;
* jeden alternativen Radius oder Bereich, der als Sensitivitätsanalyse verwendet wurde.

**Formulierung für Performance**

> Für dieses Target, dieses Band, dieses UTC-Zeitfenster und die ausgewählte Peer-Population beschreibt die angezeigte Dekodierrate den Anteil der unabhängig bestätigten Gelegenheiten, in denen auch das Target qualifizierende Evidenz lieferte. Gib an, ob die stationsgleichgewichtete Dekodierrate oder die Dekodierrate auf Gelegenheitsebene berichtet wird. Qualifizierende Stationen, bestätigte Gelegenheiten, geografischer Bereich und zeitliche Ansichten beschreiben Breite, Tiefe und Wiederkehr der stützenden Evidenz.

Eine vollständige Performance-Aussage kann zusätzlich nennen, ob die Mindestens-einmal-Reichweite breit oder begrenzt war, ob die Beteiligung beständig oder intermittierend war, wo Entfernungs- oder Richtungsmuster auftraten, ob sich ein UTC-Stunden-Muster wiederholte und wie sich das erfolgreiche Target-SNR verhielt. Beschreibe dies als beobachtetes WSPR-Verhalten der vollständigen Station unter den ausgewählten Bedingungen und nicht als isolierten Gewinn, Empfindlichkeit oder Wirkungsgrad.

**Formulierung für Benchmark**

> Für dieses Target, diese Referenz, dieses Band, dieses UTC-Zeitfenster und das ausgewählte Segment begünstigte das stationsgleichgewichtete Delta SNR Target/Referenz um den angezeigten Betrag. Das Delta SNR auf Beobachtungsebene, die Anzahlen der Joint-Stationen und Joint-Spots/-Paare, der Joint-Evidenzanteil und die Decode Outcomes beschreiben die stützende gepaarte und einseitige Evidenz.

Nenne bei einem kontrollierten Hardware-A/B-Ergebnis die vollständigen verglichenen Pfade und jeden Kreuztausch oder jede Kalibrierung. Stelle bei einem Referenzstations-/Buddy-Test klar, dass vollständig aufgebaute Stationen und ihre Umgebungen gebenchmarkt wurden. Nenne bei einem lokalen Nachbarschafts-Benchmark Radius, Methode und wechselnde Referenzdefinition.

Verwende den Designnamen passend zur beschriebenen Größe:

* Ein **Hardware-A/B-Test** vergleicht die dokumentierten lokalen Pfade.
* Ein **Buddy-Test** vergleicht vollständig aufgebaute Stationen und ihre Umgebungen.
* **Lokaler Nachbarschafts-Median** vergleicht das Target mit der aktiven Median-Nachbarschaftsdefinition innerhalb des ausgewählten Radius.
* **Beste lokale Station** vergleicht das Target mit einer wechselnden Best-Peer-Hüllkurve.
* Ein richtungsabhängiges Ergebnis beschreibt die beobachteten WSPR-Funkwege und beteiligten Stationen, nicht ein absolutes Strahlungsdiagramm.
* Benchmark-Karten verwenden eine laufabhängige symmetrische dB-Farbskala: Blau spricht für die Referenz, Rot für das Target und `0 dB` bedeutet Gleichheit. Vergleiche Karten verschiedener Läufe anhand der numerischen Farbskalenwerte.

Verwende Formulierungen wie „beobachteter Unterschied“, „in der ausgewählten Evidenz begünstigt“, „bedingte Reichweite“ und „Vergleich vollständig aufgebauter Stationen“. Aussagen über isolierten Antennengewinn, Wirkungsgrad, Empfängerempfindlichkeit, Kausalität oder statistische Signifikanz sind Versuchen vorbehalten, die diese Größen tatsächlich messen oder prüfen.

Die vollständige Referenz für gestützte und nicht gestützte Formulierungen steht in [Kapitel 8](#sec-8).

<a id="sec-4-4"></a>

#### 3.4 Lauf und Kontext sichern

Mit `Alle Ergebnisse zum Download vorbereiten` erstellst du das Exportpaket der aktuellen Analyse. Es enthält die aktuelle Konfiguration, Laufmetadaten, verarbeitete Evidenz, Tabellen und hochauflösende Abbildungen.

Bewahre zusammen mit diesem Paket externe Notizen auf zu:

* physischem Aufbau von Antenne und Speiseleitung;
* Umschalter- oder Splittertopologie;
* Sender- oder Empfängerhardware;
* Leistungsmessungen und Grundlage der Leistungsangaben;
* Decoder- und Softwareversionen;
* Betriebsplan, physischer Zuordnung des Zeitplans zu den Pfaden und jeder vertauschten Zuordnung;
* Kalibrierverfahren;
* Wetter, Störungen oder beabsichtigten Änderungen, die für den Lauf relevant waren.

WSPRadar kann die konfigurierte Analyse und die verarbeitete Evidenz sichern, aber nicht jedes physische Detail der Station erschließen. Das Exportpaket zusammen mit knappen Stationsnotizen macht Vergleich und Reproduktion deutlich belastbarer. [Kapitel 8](#sec-8) dokumentiert den genauen Exportinhalt und die verbleibenden Grenzen der Reproduzierbarkeit.

<div style="page-break-before: always;"></div>

<a id="part-ii"></a>

## Teil II: Bedienelemente und Fehlersuche

Nutze diesen Teil als Nachschlagewerk beim Einrichten, Wiederholen oder Diagnostizieren einer Analyse. Er dokumentiert die exakten Bedienelemente, Standardwerte, gespeicherten Einstellungen und wissenschaftlichen Auswirkungen, die für den Funkbetrieb relevant sind.

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
| **`Eingabeansicht`** | Wechselt zwischen `Geführt` und `Klassisch`. | Beide Ansichten bearbeiten dieselbe wissenschaftliche Konfiguration. Die gewählte Eingabeansicht wird nicht gespeichert. |
| **`Demo laden`** | Lädt ein gepflegtes historisches Profil. | Das Laden startet keine Analyse. Ein unverändertes Profil bleibt eine Demo; das Bearbeiten eines wissenschaftlichen Bedienelements macht daraus eine gewöhnliche Analyse. |
| **`Konfig laden`** | Lädt eine versionierte JSON-`.config`. | Ungültige Identitäten, Datumswerte, Auswahlwerte, Wertebereiche, doppelte Felder und nicht unterstützte Schemaversionen werden abgelehnt und nicht erraten. |
| **`Konfig speichern`** | Speichert die zutreffenden wissenschaftlichen Eingaben und unterstützten dauerhaften Ansichtseinstellungen. | Die Datei enthält absolute UTC-Grenzen, aber keine Ergebniszeilen, externen Versuchsnotizen oder flüchtigen Tabellenfilter. In der Klassischen Eingabe bleibt das Speichern unverfügbar, bis die Frage und bei einem Benchmark zusätzlich das Benchmark-Design vollständig sind. |
| **`RX-Analyse starten` / `TX-Analyse starten`** | Führt das ausgewählte Performance- oder Benchmark-Ergebnis aus. | In der Klassischen Eingabe bleibt das Starten unverfügbar, bis die Frage und bei einem Benchmark zusätzlich das Benchmark-Design vollständig sind. Eine Änderung eines wissenschaftlichen Bedienelements nach dem Lauf verwirft das Ergebnis und verlangt einen neuen Lauf. |
| **`Alle Ergebnisse zum Download vorbereiten`** | Erstellt das aktuelle Exportpaket. | Verwendet die abgeschlossene Evidenz und die aktuellen Inspektor-Auswahlen. |
| **`Vollständige Dokumentation laden` / `Vollständige Dokumentation ausblenden`** | Zeigt oder verbirgt das vollständige Webhandbuch. | Reiner Darstellungszustand. |
| **`PDF vorbereiten`** | Erstellt das Handbuch in der gewählten Sprache als PDF. | Das vollständige Webhandbuch muss dazu nicht zuerst geöffnet werden. |

**Konfigurationskompatibilität.** Gespeicherte Dateien bewahren die Eingaben und dauerhaften Ansichtsoptionen, die für die ausgewählte Analyse gelten. Ungültige oder nicht unterstützte Dateien werden abgelehnt, statt stillschweigend neu interpretiert zu werden. Das formale JSON-Schema ist der maßgebliche vollständige Vertrag gespeicherter Konfigurationen; [Abschnitt 8.4](#sec-8-4) bietet eine knappe, betriebsbezogene Zusammenfassung ausgewählter öffentlicher Bezeichnungen. Das Laden oder Speichern einer Konfiguration erzeugt kein zusätzliches Ergebnis; ausgeführt wird nur die ausgewählte Performance- oder Benchmark-Analyse.

<a id="sec-5-2"></a>

#### 4.2 Frage, Target und Messzeitraum

Die Klassische Eingabe ordnet die wissenschaftliche Konfiguration nach der Fragestellung. Im ersten Bereich **`Frage`** muss eine von vier vollständigen Analysen gewählt werden: `RX Performance`, `TX Performance`, `RX-Benchmark` oder `TX-Benchmark`. Diese eine Auswahl legt sowohl die RX-/TX-Richtung als auch fest, ob der Lauf eigenständige Performance-Evidenz oder einen Target–Referenz-Benchmark erzeugt. Der zweite Bereich **`Target und Messzeitraum`** erfasst anschließend wie bisher Target-Identität, QTH, Band und absoluten UTC-Zeitraum.

| UI-Bezeichnung | Standard | Funktion |
|---|---|---|
| **Frage** | keine; erforderlich | Eine Auswahl aus `RX Performance`, `TX Performance`, `RX-Benchmark` oder `TX-Benchmark`; legt Richtung und Ergebnistyp gemeinsam fest. |
| **Target-Rufzeichen (Empfänger im Test)** / **Target-Rufzeichen (Sender im Test)** | leer | Exakte Meldeidentität im Archiv. Standardrufzeichen, gültige Varianten mit `/`, reine Buchstabenkennungen und ein optionales abschließendes alphanumerisches Bindestrich-Suffix sind zulässig. |
| **Target-QTH (4 oder 6 Zeichen)** | leer | Target-Zuordnung über Grid-4, Kartenmittelpunkt, Geometrie und Ursprung des lokalen Radius. |
| **Frequenzband** | `20m` | Genau eines aus `LF`, `MF`, `160m`, `80m`, `60m`, `40m`, `30m`, `22m`, `20m`, `17m`, `15m`, `12m`, `10m`, `8m`, `6m`, `4m`, `2m`, `70cm` oder `23cm`. |
| **UTC-Messzeitraum** | festes 24-Stunden-Fenster bis zur aktuellen 15-Minuten-UTC-Grenze | Das absolute Evidenzintervall des Laufs. |
| **Startdatum/-zeit (UTC)** und **Enddatum/-zeit (UTC)** | das wirksame Standardfenster | Datumswerte beginnen im Jahr 2008; ein Lauf ist auf 31 verstrichene Tage begrenzt. Bearbeitete Werte werden auf wirksame 15-Minuten-Grenzen abgerundet und in den Bedienelementen angezeigt. |

Verwende das Rufzeichen oder die Meldekennung exakt so, wie es beziehungsweise sie hochgeladen wurde. `KFS`, `KFS/SE`, `DL1MKS`, `DL1MKS/P`, `DL1MKS/1`, `DL1MKS/QRP` und `DL1MKS-1` sind eigenständige Identitäten; WSPRadar führt keine verdeckte Präfix- oder Suffixzuordnung durch.

Ein vierstelliger Maidenhead-Locator bezeichnet ein größeres Locator-Feld, sechs Zeichen ein kleineres Unterfeld darin. WSPRadar verwendet das konfigurierte QTH als Kartenmittelpunkt und Ursprung des lokalen Radius. Performance und Benchmark wählen Target-Zeilen im Archiv anhand des exakten Rufzeichens plus der ersten vier Zeichen des Target-QTHs. Das vollständige QTH verankert weiterhin Karte, Entfernung, Azimut, Sonnenstand und lokale Nachbarschaftsgeometrie.

<a id="sec-5-3"></a>

#### 4.3 Benchmark-Design und -Einstellungen

Für `RX-Benchmark` und `TX-Benchmark` zeigt die Klassische Eingabe einen dritten Bereich namens **`Benchmark-Design`** und verlangt eine der folgenden Auswahlen:

- `Hardware A/B`
- `Bekannte Referenzstation`
- `Lokale Nachbarschaft`

Bei `RX Performance` und `TX Performance` entfällt der Bereich **`Benchmark-Design`** vollständig, weil Performance keine Referenz verwendet. Die richtungsabhängige Aktion `RX-Analyse starten` / `TX-Analyse starten` und `Konfig speichern` bleiben unverfügbar, solange die Frage unvollständig ist oder für eine Benchmark-Frage kein vollständiges Benchmark-Design vorliegt. Performance und Benchmark sind sich gegenseitig ausschließende Ergebnistypen: Ein Lauf erzeugt nur das ausgewählte Ergebnis. [Abschnitt 8.4](#sec-8-4) fasst ausgewählte öffentliche maschinenlesbare Bezeichnungen für Konfiguration, URL und Export zusammen; er ist kein vollständiger Feld- oder Parameterkatalog.

| UI-Bezeichnung | Standard / Wertebereich | Gilt für | Wissenschaftliche Wirkung |
|---|---|---|---|
| **Gibt es einen ermittelten Target–Referenz-Offset?** | `Kein ermittelter Offset — 0,0 dB verwenden` | Geführtes Hardware A/B und bekannte Referenzstation | Unterscheidet keinen ermittelten Offset, die Verwendung einer ermittelten Korrektur und einen gezielten Offset-Ermittlungslauf. |
| **Referenzseitige SNR-Korrektur (dB)** | leer = `0.0`; `-99.9` bis `+99.9 dB` | Benchmark | Wird zum Referenz-SNR addiert, bevor Delta SNR Target minus Referenz berechnet wird. Dezimalwerte werden mit Punkt eingegeben, beispielsweise `1.2`. |
| **Referenz-Rufzeichen** | leer | Hardware A/B und Referenzstation | Exakte Meldeidentität der Referenz. |
| **Referenz-Locator** | unabhängiges Grid-4 bei Referenzstation; abgeleitetes Target-Grid-4 bei Hardware A/B | Benchmark | Steuert die Zuordnung der Referenzzeilen im Archiv. |
| **Lokale Benchmark-Methode** | `Lokaler Nachbarschafts-Median` | Lokaler Nachbarschafts-Benchmark | Wählt den medianen lokalen Referenzwert oder die strengere wechselnde `Beste lokale Station`. |
| **Nachbarschaftsradius (km)** | `100`; 10–250 km in 10-km-Schritten | Lokaler Nachbarschafts-Benchmark | Definiert den lokalen Referenzpool um das Target-QTH. |
| **TX-A/B-Methode** | `Simultanes TX` | TX Hardware A/B | Wählt Paarbildung zweier Sender im selben Zyklus oder deterministische sequenzielle Paarung. |
| **Wiederholintervall** | `10 min`; `4, 6, 10, 12, 20, 30, 60 min` | Sequenzielles TX A/B | Tatsächliche Wiederkehr jedes physischen Pfads. |
| **Target-Start / Referenz-Start** | `00 UTC` / `02 UTC`; verschiedene gerade Phasen unterhalb des Wiederholintervalls | Sequenzielles TX A/B | Ordnet Aussendungen den Target- und Referenzphasen des Zeitplans zu. |

Bei TX Hardware A/B bezeichnet das `Wiederholintervall` die tatsächliche Wiederkehr jedes Pfads und nicht zwangsläufig den angezeigten `Frame`-Wert eines Senders. Vergleiche die Stunden-Vorschau mit den beobachteten Startzeiten auf Sendung und der physischen Schaltzuordnung. Gerätebeispiele stehen in [Anhang B](#sec-b); die Paarbildung in den [Abschnitten 7.1](#sec-7-1) und [7.7](#sec-7-7) <a href="#ref-12">[Ref-12]</a>.

Beim Wechsel der Frage oder des Benchmark-Designs werden nicht zutreffende Bedienelemente ausgeblendet. Gespeicherte Konfigurationen enthalten nur die Eingaben, die für die ausgewählte Analyse gelten. Werte, deren wissenschaftliche Bedeutung sich im neuen Design ändern würde, werden gelöscht statt umgedeutet.

##### Vorzeichen der referenzseitigen SNR-Korrektur

Eine positive Korrektur erhöht das korrigierte Referenz-SNR und verringert dadurch Delta SNR Target minus Referenz. Gib einen gemessenen Kalibrierversatz `target - reference` mit demselben Vorzeichen ein. Ergibt eine Kalibrierung mit gemeinsamem Eingang beispielsweise `+1.6 dB`, wird `+1.6 dB` eingetragen. [Abschnitt 7.5](#sec-7-5) definiert die Gleichungen.

Die Korrektur gilt für den Referenz-Empfangs- beziehungsweise Sendepfad oder -Zeitplan bei Hardware A/B, die bekannte Referenzstation, den ausgewählten Wert der besten lokalen Station oder jeden lokalen Beitrag vor Bildung des lokalen Nachbarschafts-Medians.

| Geführte Auswahl | Bedeutung | Erforderlicher Wert |
|---|---|---|
| **Kein ermittelter Offset** | Es wurde keine belastbare Korrektur bestimmt. | `0.0 dB` |
| **Ermittelte Korrektur verwenden** | Ein dokumentierter, vorzeichenbehafteter additiver Offset gilt für diesen Aufbau. | Ermittelte Korrektur eingeben |
| **Offset-Ermittlungslauf einrichten** | Evidenz sammeln, aus der ein Offset abgeleitet werden kann; WSPRadar berechnet oder verwendet diesen Offset nicht automatisch. | Während des Ermittlungslaufs `0.0 dB` |

Eine konstante Korrektur kann Übersteuerung, instabile AGC, intermittierende Signalführung, frequenzabhängigen Amplitudengang oder falsche Leistungsangaben nicht beheben. Hardware-A/B-Kalibrierung sollte ein gemeinsames Eingangssignal oder eine kalibrierte Bezugsebene verwenden. Eine geografisch getrennte Referenzstation kann nur eine wiederholbare Basislinie für genau dieses Paar, Band und diesen Aufbau stützen – keine absolute Kalibrierung. [Anhang C](#sec-c) beschreibt das praktische Verfahren.

<a id="sec-5-4"></a>

#### 4.4 Filter und Evidenzschwellen

Wähle Filter und Schwellen vor einem bestätigenden Lauf aus der beabsichtigten Population und der gewünschten Evidenzuntergrenze. Eine nachträgliche Änderung nach Betrachtung des Ergebnisses erzeugt eine andere Analyse und sollte getrennt aufbewahrt werden.

| Bedienelement | Standard | Gilt für | Wirkung und Verwendung |
|---|---|---|---|
| **Spezial-Rufzeichen Q, 0, 1 ausschließen** | bei Performance ein; bei Benchmark aus | alle Ergebnisse | Schließt Peer-Identitäten aus, die mit `Q`, `0` oder `1` beginnen. Behalte baken- oder telemetrieartige Identitäten, wenn sie zur Fragestellung gehören; schließe sie aus, wenn reguläre Amateurfunkaktivität untersucht werden soll. |
| **Bewegliche Stationen filtern** | bei Performance ein; bei Benchmark aus | kartierte Peers | Schließt Rufzeichen aus, die in der ansonsten qualifizierenden globalen Population mehr als ein Grid-4 melden. Nutze Drill-Down, um Bewegung von fehlerhaften Locator-Angaben zu unterscheiden. |
| **Sonnenstand am Target-QTH** | `Ganze 24h` | alle Ergebnisse | Behält je nach Sonnenhöhe am Target-QTH `Tag (Elev > +6°)`, `Nacht (Elev < -6°)`, `Greyline (-6° bis +6°)` oder alle Zyklen bei. |
| **Maximale Peer-Entfernung vom Target (km)** | `22000`; Auswahl `2500`, `5000`, `10000`, `15000`, `20000`, `22000` | alle Ergebnisse | Entfernt Peers ab der ausgewählten Entfernung aus Analyse, verarbeiteten Artefakten und Exporten. Das Target-Active Gate darf Evidenz außerhalb des Bereichs weiterhin ausschließlich dazu verwenden, Target-Betrieb nachzuweisen. |
| **Minimale Joint-Evidenz pro Station** | `1`; Bereich 1–50 | simultaner Benchmark | Verlangt wiederholte Joint-Peer-Zyklen, bevor eine Station gepaartes Delta SNR beiträgt; derselbe Zahlenwert gilt auch als Untergrenze für exklusive Kategorien. |
| **Minimale geplante Paare pro Station** | `1`; Bereich 1–50 | sequenzielles TX A/B | Verlangt wiederholte vollständige geplante Paare, bevor eine Station ein Paar-Delta beiträgt; einseitige Paarkategorien verwenden denselben Zahlenwert. |
| **Minimale bestätigte Gelegenheiten pro Station** | `5`; Bereich 1–100 | Performance | Verlangt ausreichend Target- plus Gegen-Gelegenheiten, bevor ein Peer beiträgt. Niedrige Werte erhöhen die Abdeckung, machen die Raten aber grob und schwach gestützt. |
| **Minimale qualifizierte Stationen pro Kartensegment** | `1`; Bereich 1–10 | alle Karten | Verlangt breitere Identitätsunterstützung, bevor ein Segment gezeichnet wird. |

Die beiden Ausschluss-Standardwerte gelten nur für unveränderte interaktive Konfigurationen. Eine Performance-Konfiguration startet mit beiden Ausschlüssen; eine Benchmark-Konfiguration ohne beide. Sobald der Bediener einen der Ausschlüsse manuell ändert, bleibt dieser ausdrückliche Wert über Wechsel der Frage hinweg erhalten und wird nicht mehr durch einen Ergebnistyp-Standard ersetzt. Geladene Konfigurationen, Demos und Analyse-URLs behalten ihre ausdrücklich gespeicherten Einstellungen ebenfalls bei.

`Maximale Peer-Entfernung vom Target (km)` begrenzt die ausgewertete Population erst, nachdem die Archivzeilen abgerufen wurden. Eine Verringerung umgeht deshalb nicht die Zeilengrenze des Archivs. Ein kleinerer lokaler Nachbarschaftsradius und `Spezial-Rufzeichen Q, 0, 1 ausschließen` können bei bestimmten Analysen die abgerufene Population verkleinern; [Abschnitt 5.6](#sec-6-6) behandelt zu große Abrufe.

<a id="sec-5-5"></a>

#### 4.5 Karten-, Inspektor- und Exporteinstellungen

| Bedienelement | Wirkung | Gespeichert? | Neuer Lauf? |
|---|---|---|---|
| Entfernung und Richtung des Segments | Aktiver geografischer Inspektionsbereich | getrennt für Performance und Benchmark | Nein |
| `Nur von anderen Stationen gehört.` / `Nur andere Signale gehört.` | Sichtbarkeit von Performance-Peers mit ausschließlich Gegen-Evidenz | Ja | Nein |
| `Ungepaarte Evidenz einbeziehen` | Sichtbarkeit von Benchmark-Identitäten, die nur exklusive oder asynchrone Evidenz besitzen | Ja | Nein |
| Ausgewählte Stationszeile | Evidenz der ausgewählten Station und ausgewählte Drill-Down-Identität | genau ein `Rufzeichen + Locator` je Ergebnistyp | Nein |
| Zeitaggregation des Segments | Chronologische zeitliche Ansicht des Segment-Inspektors | Ja | Nein |
| Zeitaggregation der ausgewählten Station | Chronologische Ansicht des ausgewählten Funkwegs | Ja | Nein |
| `Alle Ergebnisse zum Download vorbereiten` | Exportpaket und aktuelle Inspektor-Auswahlen | nicht zutreffend | Nein |

Die chronologische Aggregation verändert weder die Klassifikation von Gelegenheiten noch die Benchmark-Paarbildung oder die festen einstündigen UTC-Profile. Leere Performance-Zeit- oder Entfernungs-Bins bleiben fehlende Evidenz und werden nicht zu künstlichen Beobachtungen mit einer Rate von null. Die Exportinhalte stehen in [Abschnitt 8.4](#sec-8-4).

<a id="sec-6"></a>

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
7. **Versuchsmechanik:** Uhrensynchronisation, Zuordnung des TX-Zeitplans zu den Pfaden, Umschaltung, Signalführung sowie tatsächliche und gemeldete Leistung.

Erst nach diesen Prüfungen sollten Evidenzschwellen, Ausschlüsse, Sonnenstand oder geografischer Bereich geändert werden.

<a id="sec-6-2"></a>

#### 5.2 Fehler nach Symptom eingrenzen

| Symptom | Nächste Prüfungen |
|---|---|
| **Kein Ergebnis oder keine Target-Evidenz** | Prüfe genaue Identität, QTH, Band, Zeitfenster und tatsächlichen Betrieb sowie den gemeldeten Status der strengen Abfrage mit `code = 1`, des historischen Fallbacks und der Upstream-Verfügbarkeit. |
| **Benchmark enthält kein Delta SNR** | Prüfe gemeinsame entfernte Peers in überlappenden Zyklen oder geplanten Paaren, Referenzbetriebszeit, Uhren, Zeitplanzuordnung, Joint-Schwelle, Filter und Bereich. |
| **Benchmark enthält Delta SNR, aber wenig paarbare Evidenz** | Lies Joint-Evidenzanteil und Decode Outcomes; prüfe Referenzbetriebszeit, Leistung, Schwellen, Bereich und ob die gepaarte Teilmenge die breitere Stationspopulation repräsentiert. |
| **Performance enthält nur sehr wenige Peers** | Prüfe unabhängige Netzaktivität, minimale bestätigte Gelegenheiten, Ausschlüsse, Sonnenstand, Zeitfenster und maximale Peer-Entfernung. |
| **Viele Performance-Zeilen ohne unabhängige Bestätigung** | Die Target-Beobachtungen bleiben prüfbar, gehen aber ohne den erforderlichen unabhängigen Aktivitätsnachweis nicht in die Dekodierrate ein. |
| **`Only Reference = 0`** | Prüfe die Konditionierung auf Target-Aktivität, Schwellen und aktiven Bereich; null kann korrekt sein. |
| **Unerwartetes Vorzeichen des Delta SNR bei Hardware A/B** | Prüfe physische A/B-Zuordnung, Reihenfolge von Target und Referenz, Korrekturvorzeichen, Zeitplanphasen, tatsächliche und gemeldete Leistung sowie Kalibrierung. Gleiche einen Funkweg im Drill-Down ab. |
| **Lokales Ergebnis verändert sich mit dem Radius** | Untersuche die lokalen Beitragenden und berichte die Radiusabhängigkeit, statt nur den günstigsten Radius auszuwählen. |
| **Der Lauf wird wegen zu großer Quellmenge beendet** | Verkürze das UTC-Zeitfenster. `Spezial-Rufzeichen Q, 0, 1 ausschließen` oder ein kleinerer lokaler Nachbarschaftsradius können zutreffende Quellabfragen verkleinern; die maximale Peer-Entfernung nicht, weil sie erst nach dem Abruf angewandt wird. |
| **Aktuelle Spots erscheinen unvollständig** | Warte nach dem letzten Zyklus ungefähr fünf Minuten und prüfe danach Upload und Upstream-Status. |

Ein Problem mit Upstream-Daten verändert, was die Quelle geliefert hat. Ein Problem des Versuchsdesigns verändert, ob die beibehaltene Evidenz die beabsichtigte Frage beantwortet. Diagnostiziere und dokumentiere beides getrennt.

<a id="sec-6-3"></a>

#### 5.3 Rufzeichen und Locator prüfen

Performance und jedes Benchmark-Design ordnen Target-Zeilen anhand des exakten Rufzeichens plus des Grid-4 des Target-QTHs zu. Ein Target, das `JN37` meldet, während `JN38` konfiguriert ist, wird nicht zugeordnet.

Eine Referenzstation verwendet das exakte Referenz-Rufzeichen plus einen unabhängigen vierstelligen Referenz-Locator. RX und simultanes TX Hardware A/B leiten das Referenz-Grid-4 aus dem Target-QTH ab; sequenzielles TX Hardware A/B verwendet die gemeinsame Target-Identität und unterscheidet die Pfade über den Zeitplan. Lokale Referenzen werden geografisch gewählt.

Rufzeichen müssen die dokumentierte Regel für Meldekennungen mit 3 bis 15 Zeichen erfüllen. Locator müssen vier oder sechs gültige Maidenhead-Zeichen besitzen. Eine syntaktische Prüfung belegt weder rechtmäßige Zuteilung, physischen Standort noch tatsächlichen Betrieb. Die Peer-Identität ist das exakte `Rufzeichen + vollständig gemeldeter Locator`; veraltete oder wechselnde Locator können eine physische Station aufteilen oder verschieben.

<a id="sec-6-4"></a>

#### 5.4 Fallback für historische Decode-Codes

WSPRadar fragt WSPR-2-Zeilen zunächst mit `code = 1` ab. Liefert diese strenge Abfrage keine Target-seitige Evidenz, wird sie aus Gründen der historischen Kompatibilität ohne dieses Prädikat wiederholt; der Laufstatus meldet den Fallback. Der Fallback erweitert die Auswahl und kann für Performance und Benchmark unterschiedlich ausfallen.

<a id="sec-6-5"></a>

#### 5.5 Wie das Target-Active Gate die Evidenz prägt

Das Target-Active Gate behält simultane Zyklen nur dann bei, wenn eine Beteiligung des Targets beobachtbar ist. Referenzmeldungen aus Zeiten, in denen das Target offline war, werden deshalb nicht automatisch als Misserfolge des Targets gezählt.

Das Gate ist bewusst Target-zentriert. Die Betriebsbereitschaft der Referenz bleibt Teil des Versuchs, und ein Tausch von Target und Referenz kann die einseitigen Decode Outcomes und die zulässige Population verändern. Sequenzielles TX Hardware A/B verwendet stattdessen deterministische geplante Paare. [Abschnitt 7.3](#sec-7-3) definiert diese Konditionierung formal.

<a id="sec-6-6"></a>

#### 5.6 Umgang mit Upstream-Daten

Öffentliche WSPR-Archive können Duplikate, falsche Spots, fehlerhafte Locator oder Leistungsangaben, verspätete Uploads und spätere Korrekturen enthalten. wspr.live beschreibt aktuelle Daten als um einige Minuten verzögert. Etwa **fünf Minuten** nach dem letzten Zyklus zu warten ist eine praktische Schätzung und keine Vollständigkeitsgarantie <a href="#ref-10">[Ref-10]</a>.

WSPRadar verringert die Empfindlichkeit gegenüber einzelnen fehlerhaften Zeilen durch Identitätskonsolidierung, Mediane, Evidenzschwellen und Drill-Down. Wiederholt auftretende plausible Fehler können dennoch bestehen bleiben. Korrekte Berechnungen können eine falsche Leistungsangabe, einen falschen Locator oder eine falsche Betriebsidentität nicht reparieren.

Der **System Audit Status** dokumentiert die für die Auswertung notwendige Herkunft des Laufs:

| Statuselement | Bedeutung |
|---|---|
| **Datenquelle** | Das eine Upstream-Archiv, das für den abgeschlossenen Lauf verwendet wurde. Evidenz verschiedener Archive wird innerhalb eines Laufs nicht vermischt. |
| **Historischer Fallback** | Ob die Auswahl ohne die strenge Bedingung für den WSPR-2-Decode-Code wiederholt wurde. |

Diese Angaben zeigen, aus welcher Quelle die Evidenz stammt und ob der historische Kompatibilitäts-Fallback verwendet wurde; sie definieren keine andere wissenschaftliche Methode.

Ein Archivabruf mit mehr als 1.000.000 vollständigen Zeilen wird vor der Analyse abgelehnt und nicht stillschweigend abgeschnitten. Verkürze das Zeitfenster oder verwende einen passenden archivseitigen Populationsfilter wie in [Abschnitt 5.2](#sec-6-2) beschrieben.

<div style="page-break-before: always;"></div>

<a id="part-iii"></a>
## Teil III: Wissenschaftliche Grundlagen, Methoden und Aussagen

Teil III ist die wissenschaftliche Methodenreferenz für technisch kritisch arbeitende Funkamateure, HamSCI-Mitwirkende und Gutachter. Er definiert Beobachtungsdaten, gebildete Evidenzeinheiten, Analyseziele, deskriptive Zusammenfassungen, Konditionierung, fehlende Beobachtungen, Gewichtung, Abhängigkeiten, Transformationen und Reproduzierbarkeitsgrenzen von WSPRadar. Dieser Teil ist bewusst formaler als der Leitfaden für den Funkbetrieb, erklärt die Formeln aber zusätzlich in verständlicher Stationssprache.

<a id="sec-d"></a>
### 6. Literatur, Vorarbeiten und Einordnung

Dieses Kapitel ist eine fokussierte methodische Übersicht und keine systematische oder erschöpfende Literaturrecherche. Begutachtete Fachartikel, Preprints, technische Erfahrungsberichte aus dem Amateurfunk und Softwaredokumentation stützen unterschiedliche Arten von Aussagen; jede Quelle wird nur für den Beitrag verwendet, den sie tatsächlich belegt. Die Übersicht bedeutet nicht, dass die Vorarbeiten jede WSPRadar-Kennzahl oder methodische Entscheidung validieren.

<a id="sec-d-1"></a>
#### 6.1 Vom Meldenetz zum Versuchsdatensatz

Taylor und Walker stellten WSPRnet nicht nur als Live-Karte, sondern auch als Archiv vor: „The WSPRnet database represents a rich source of experimental data for propagation studies.“ Ihr Beispiel gruppiert Beobachtungen über mehrere Wochen nach Tageszeit. Es zeigt sowohl den Wert angesammelter Meldungen als auch die Notwendigkeit, sie als Beobachtungsdaten und nicht als kontrollierte Labordaten zu interpretieren. <a href="#ref-6">[Ref-6]</a>

Frissell et al. ordnen WSPRNet zusammen mit dem Reverse Beacon Network und PSKReporter als etablierte Amateurfunk-Beobachtungsnetze ein, die langfristige Beobachtungen der unteren Ionosphäre liefern. Sie unterscheiden diese Netze von zweckgebundenen wissenschaftlichen Instrumenten und empfehlen eine Kreuzkalibrierung zwischen Instrumentennetzen. Die Übersicht stützt die wissenschaftliche Nutzung von Amateurfunkbeobachtungen; sie macht nicht jeden beitragenden Empfänger zu einem kalibrierten Sensor. <a href="#ref-7">[Ref-7]</a>

Das WSPR-Archiv verbindet damit eine ungewöhnliche zeitliche Tiefe und geografische Reichweite mit heterogenen Stationen, einer Auswahl erfolgreicher Decodes, von Nutzern gemeldeten Identitäten und Leistungen, wechselnder Ausrüstung und meist unbekannten Betriebsplänen. Diese Eigenschaften erfordern ausdrücklich definierte Zulässigkeit und Konditionierung, statt das Ausbleiben eines Spots unmittelbar zu interpretieren.

<a id="sec-d-2"></a>
#### 6.2 WSPR-Beobachtungsdaten interpretierbar machen

<a id="sec-d-lo"></a>
Lo et al. untersuchten mit WSPR-Meldungen auf 7 MHz die Greyline-Ausbreitung und warnten davor, dass für WSPR-Geräte keine maßgeblichen Betriebspläne existieren. Bevor sie einen fehlenden Funkweg interpretierten, prüften sie, ob der Sender andernorts gehört worden war oder ob der Empfänger eine andere Station gehört hatte. Außerdem betonten sie die Konsistenz von Rufzeichen und Standort sowie die Verwendung mehrerer Standorte. <a href="#ref-9">[Ref-9]</a>

Dieses Prinzip der Aktivitätsprüfung ist eine direkte methodische Vorarbeit für das Target-Active Gate und die unabhängig bestätigten Gelegenheiten von WSPRadar: Funkstille sollte erst dann zu Gegen-Evidenz werden, wenn der relevante Betrieb beobachtbar ist. Lo et al. definieren jedoch weder die asymmetrische Target-Konditionierung von WSPRadar noch dessen Performance-Analyseziel, Stationsgewichtung, Decode Outcomes oder lokale Referenzen; diese bleiben WSPRadar-Designentscheidungen für andere Analysefragen.

<a id="sec-d-3"></a>
#### 6.3 Wissenschaftliche Entwicklungslinie von Antennen- und Stationsvergleichen

<a id="sec-d-toledo"></a>
**Toledo (2010): Warum langsames Abwechseln scheitert.** Sivan Toledo erprobte ungefähr eine Stunde lang eine Antenne und anschließend eine andere. Dabei änderte sich das SNR des Funkwegs in derselben Größenordnung wie der scheinbare Antennenunterschied. Er folgerte, dass dieser naive Aufbau die Antennen nicht isolieren konnte, und schlug eine Umschaltung in jedem Zyklus oder simultane Aussendungen mit getrennter Hardware vor. Der deterministische alternierende TX-A/B-Zeitplan von WSPRadar folgt derselben praktischen Logik: Ein kurzer zeitlicher Abstand verringert zeitliche Konfundierung, beseitigt sie aber nicht. <a href="#ref-3">[Ref-3]</a>

<a id="sec-d-milazzo"></a>
**Milazzo (2011): Vom Funkamateur durchgeführter End-to-End-Vergleich.** Carol Milazzo verglich zwei 29 km voneinander entfernte Stationen über einen gemeinsamen Empfänger in 1.750 km Entfernung, korrigierte die gemeldeten SNR-Werte um Unterschiede der Sendeleistung, verglich den Verlauf mit VOACAP, berücksichtigte unterschiedliche Tastgrade und untersuchte reziproke RX-Meldungen. Die Fallstudie zeigt den praktischen Wert eines WSPR-Vergleichs über denselben Empfänger, macht aber zugleich die Grenzen durch unterschiedliche QTHs, Hardware, lokalen Störpegel, nur einen ausgewählten Empfänger und eine fehlende formale Unsicherheitsanalyse sichtbar. <a href="#ref-4">[Ref-4]</a>

<a id="sec-d-griffiths-squibb"></a>
**Griffiths und Squibb (2017): RX-Vergleich desselben Signals als Stationsdiagnose.** Für zwei Empfänger an getrennten QTHs behielten sie Meldungen desselben Senders zur selben Zeit bei und setzten die SNR-Differenz in Beziehung zu Bodenfeuchte, Zeit, Entfernung und Änderungen an der Station. Die Arbeit zeigt, wie gepaarte WSPR-Beobachtungen vollständige Empfangssysteme diagnostizieren und Strukturen sichtbar machen können, die reine Spotzahlen verdecken. Da sich Antennen, QTHs, Störpegel und Ausrüstung unterschieden, stützt sie vergleichende Stationsevidenz und keinen isolierten, kalibrierten Antennengewinn. <a href="#ref-5">[Ref-5]</a>

<a id="sec-d-vanhamel"></a>
**Vanhamel, Machiels und Lamy (2022): Konditioniertes simultanes RX.** Ihr begutachteter Versuch konditionierte zwei nominell identische 160-m-WSPR-Empfangsstationen und verglich gemeinsame entfernte Aussendungen simultan. Innerhalb der hier betrachteten Quellen ist dies die stärkste direkte Vorarbeit für RX Hardware A/B und für die Charakterisierung von Offsets zwischen Empfangsketten vor der Interpretation von Antennenunterschieden. Die Ausbreitungsergebnisse zeigen außerdem, dass Polarisation und ionosphärische Effekte mit dem gemeldeten SNR gekoppelt bleiben. <a href="#ref-2">[Ref-2]</a>

<a id="sec-d-zander"></a>
**Zander (2022): Simultaner TX-Vergleich am selben Empfänger.** Zander modelliert zwei lokale Antennen, die im selben WSPR-Zyklus von getrennten, nominell leistungsgleichen Sendern mit unterschiedlichen Rufzeichen gespeist werden. Ein entfernter Empfänger trägt nur dann bei, wenn er beide Signale im selben Intervall meldet. Unter den Annahmen gleicher Zeit, eines gemeinsamen Funkwegs und gleicher Leistung heben sich gemeinsame Pfaddämpfung und Empfängerrauschen in der SNR-Differenz auf; frequenzselektive Störungen, fehlgeschlagene Decodes, Quantisierung und Unterschiede der Sendeketten bleiben bestehen. Da jede Differenz innerhalb desselben entfernten Empfängers gebildet wird, ist für dieses Paar keine Empfängerkalibrierung erforderlich; Gleichheit oder Korrektur der beiden Sendeleistungen bleibt jedoch wesentlich. <a href="#ref-1">[Ref-1]</a>

Zander berichtet je Vorversuch ungefähr 1.000 Beobachtungen, von denen etwa 150–200 gemeinsame Meldungen aus 15–35 Empfängern beibehalten wurden; die Stichproben-Standardabweichung lag nahe 3 dB. Die Aussage der Arbeit im Sub-dB-Bereich betrifft die Präzision eines arithmetischen Mittels unter den Modell- und Stichprobenannahmen und keine rückführbare Gesamtgenauigkeit. Geografische Stichprobe, Antennenrichtwirkung und unbekannte Elevationswinkel bleiben systematische Grenzen. Die Studie stützt simultanes Delta SNR am selben Empfänger, nicht jedoch das sequenzielle Ein-Sender-Design von WSPRadar, stationsgleichgewichtete Mediane, Decode Outcomes oder Nachbarschaftsreferenzen.

<a id="sec-d-4"></a>
#### 6.4 Analyseinfrastruktur und verwandte Werkzeuge

Griffiths und Robinett demonstrierten einen relationalen Zeitreihen-Self-Join für denselben Sender, dieselbe Zeit und dasselbe Band, gemeldet von zwei Empfängern, zusammen mit Diagrammen der SNR-Differenz, Medianen, Quartilen, Zeit-Heatmaps, Entfernungs-/Azimutansichten und Export. Dies ist eine wichtige Vorarbeit für prüfbare Vergleichsinfrastruktur, nicht jedoch für die exakten Zulässigkeits-, Konditionierungs- oder Zusammenfassungsdefinitionen von WSPRadar. <a href="#ref-13">[Ref-13]</a>

WSPR.Rocks ermöglicht eine schnelle SQL-basierte Erkundung von WSPR-Daten mit Karten, Tabellen, SpotQ und Heatmaps. WSPRdaemon legt den Schwerpunkt auf robuste Erfassung mit mehreren Empfängern, Zeitplanung und zusätzliche Rausch-/Doppler-Metadaten. SOTABEAMS WSPRlite/DXplorer, WSPR-Station-Compare, das Antenna Performance Analysis Tool und WATT bieten weitere Arbeitsabläufe für Vergleich, Berichterstattung und Visualisierung <a href="#ref-14">[Ref-14]</a> <a href="#ref-15">[Ref-15]</a> <a href="#ref-16">[Ref-16]</a> <a href="#ref-17">[Ref-17]</a> <a href="#ref-18">[Ref-18]</a>.

Diese Systeme belegen umfangreiche Vorarbeiten bei Datenerfassung, Exploration, Rangbildung, Vergleich, Kartendarstellung und Berichterstattung. Die Einordnung von WSPRadar beruht daher auf integrierten Versuchsdefinitionen, konditionierten Populationen, hierarchischer Gewichtung, ergänzender gepaarter und einseitiger Evidenz sowie dem Auditpfad – nicht auf der Behauptung, das erste WSPR-Analysewerkzeug zu sein.

<a id="sec-d-5"></a>
#### 6.5 Was WSPRadar übernimmt, integriert und ergänzt

WSPRadar übernimmt gesammelte WSPR-Beobachtungen, Aktivitätsprüfungen, Korrektur anhand gemeldeter Leistung, Paarbildung unter gemeinsamen Bedingungen, den Vergleich kalibrierter Empfangsketten, Datenbank-Joins sowie geografische und zeitliche Inspektion. Es führt diese Elemente in einem TX-/RX-Arbeitsablauf zusammen mit:

* Performance auf Grundlage unabhängig bestätigter Gelegenheiten;
* Hardware A/B, Referenzstation und dynamischen lokalen Nachbarschafts-Benchmarks;
* Zuordnung im selben Zyklus oder über deterministische geplante Paare;
* Normierung anhand gemeldeter Leistung und optionaler referenzseitiger Korrektur;
* gepaartem Delta SNR, getrennt von einseitigen Decode Outcomes;
* stationsgleichgewichteten und beobachtungsbezogenen Zusammenfassungen;
* einem Auditpfad von Karte über Segment und Station bis zur Zeile; und
* versionierter Konfiguration, verarbeiteter Evidenz und Reproduzierbarkeitsexport.

Innerhalb der geprüften Quellen sind die deutlichsten spezifischen Ergänzungen von WSPRadar der ausdrücklich definierte konditionale Performance-Nenner, die Trennung gepaarter von einseitiger Evidenz, dynamische lokale Median- und Best-Peer-Referenzen, hierarchische stationsgleichgewichtete geografische Aggregation und ein integrierter Auditpfad über alle unterstützten Designs.

Dies ist eine begrenzte Aussage über Integration und Methode und kein globaler Prioritätsanspruch. Medianaggregation an sich ist nicht neu. WSPRadar sollte als strukturierte Versuchs- und Auditschicht oberhalb eines Spot-Browsers beschrieben werden und nicht als Ersatz für Upstream-Archive, andere Analysewerkzeuge oder kalibrierte HF-Messtechnik.

<a id="sec-7"></a>
### 7. Wissenschaftliche Methoden

Dieses Kapitel definiert den wissenschaftlichen Vertrag eines WSPRadar-Laufs. WSPRadar beginnt mit gemeldeten Beobachtungen, bildet daraus zulässige Evidenzeinheiten, leitet Größen wie normiertes SNR und gepaartes Delta SNR ab und berechnet anschließend deskriptive Zusammenfassungen. Diese Werte sind für die Evidenz exakt, die nach den ausgewählten Regeln beibehalten wurde. Sie sind nicht automatisch Aussagen über alle möglichen Stationen, künftige Betriebsbedingungen oder eine isolierte physikalische Eigenschaft der Station.

Hilfreich ist die Unterscheidung von fünf Ebenen:

1. **Gemeldete Beobachtungen:** hochgeladene WSPR-Spots mit Rufzeichen, Locator, Leistung, Zeit und SNR.
2. **Gebildete Evidenzeinheiten:** qualifizierende Gelegenheiten, Peer-Zyklen, Joint-Einheiten und geplante A/B-Paare, die nach den Zulässigkeits- und Zuordnungsregeln von WSPRadar entstehen.
3. **Abgeleitete Größen:** normiertes SNR, Decode Outcomes und Target-minus-Referenz-Delta-SNR einer einzelnen Evidenzeinheit.
4. **Deskriptive Zusammenfassungen:** Raten, Mediane, Reichweite, Evidenzanteile sowie zeitliche und geografische Zusammenfassungen der beibehaltenen Evidenz.
5. **Interpretation über den Lauf hinaus:** Aussagen über künftiges Verhalten, eine breitere Population oder eine physische Ursache. Solche Verallgemeinerungen benötigen zusätzliche Annahmen und experimentelle Kontrolle; die reine Berechnung genügt dafür nicht.

**Verwendete Notation**

| Symbol | Bedeutung |
|---|---|
| $i$ | eine Peer-<strong class="defined-term">Identität</strong>, definiert als exaktes `Rufzeichen + gemeldeter Locator` |
| $c$ | ein zulässiger WSPR-<strong class="defined-term">Zyklus</strong> oder beim sequenziellen TX A/B ein geplantes Paar |
| $g$ | ein beibehaltener <strong class="defined-term">geografischer</strong> Bereich oder ein Segment |
| $b$ | ein Entfernungs- oder Zeit-<strong class="defined-term">Bin</strong> |
| $S_{i,c}$ | Target-<strong class="defined-term">Erfolgs</strong>indikator innerhalb einer zulässigen Performance-Gelegenheit |
| $O_{i,c}$ | Performance-<strong class="defined-term">Gelegenheits</strong>indikator nach Aktivitäts-, Identitäts- und Populationsregeln |
| $D_{i,c}$ | gepaartes Target-minus-Referenz-<strong class="defined-term">Delta</strong>-SNR, wenn beide Seiten beobachtet wurden |
| $T_{i,b},J_{i,b},R_{i,b}$ | Anzahlen Only <strong class="defined-term">Target</strong>, <strong class="defined-term">Joint</strong> und Only <strong class="defined-term">Reference</strong> im Benchmark-Bereich $b$ |

Ein Indikator ist `1`, wenn seine Bedingung erfüllt ist, und sonst `0`. Die Notation macht Nenner und Gewichtung eindeutig; der Text nach jeder Formel erklärt dieselbe Berechnung in Funkpraxis-Sprache.

Dieses Kapitel verwendet **Zusammenfassung** oder **deskriptive Kennzahl** für die Raten, Mediane, Anteile und Verteilungen der beibehaltenen Evidenz. Die Unterscheidung ist wichtig, weil ein Wert für die beibehaltenen Zeilen exakt berechnet sein und dennoch nur eine enge oder ausgewählte Population beschreiben kann.

**Methodischer Überblick**

| Design | Kleinste Vergleichseinheit | Konditionierung / Zulässigkeit | Hauptzusammenfassung | Wichtigste Grenze |
|---|---|---|---|---|
| RX Performance | ein Peer-Zyklus eines entfernten Senders | Target-Empfänger aktiv; derselbe Sender andernorts unabhängig decodiert | Peer-Dekodierrate, danach Mittel mit gleicher Peer-Gewichtung; gepoolte Gelegenheitsrate bleibt erhalten | bedingte Beobachtbarkeit, keine kalibrierte Empfindlichkeit |
| TX Performance | ein Peer-Zyklus eines entfernten Empfängers | Target-Sender aktiv; Peer-Empfänger auf dem Band unabhängig aktiv | Peer-Dekodierrate, danach Mittel mit gleicher Peer-Gewichtung; gepoolte Gelegenheitsrate bleibt erhalten | bedingte Beobachtbarkeit, nicht alle Sendeversuche |
| RX Hardware A/B / Buddy | ein Peer-Zyklus eines entfernten Senders | Target aktiv; beide Empfänger melden denselben Sender-Zyklus für Delta SNR | Stationsmedian des Delta SNR, danach Median über Stationen | vollständige Empfangspfade, sofern Ketten nicht kontrolliert sind |
| Simultanes TX Hardware A/B / zutreffender Buddy- oder lokaler Benchmark | ein Peer-Zyklus eines entfernten Empfängers | Target aktiv; derselbe Empfänger-Zyklus für gepaartes Delta SNR | Stationsmedian des Delta SNR, danach Median über Stationen | Leistung, Kettenunterschiede und Auswahl nach Joint-Decode |
| Sequenzielles TX Hardware A/B | ein entfernter Empfänger in einem geplanten Target-/Referenzpaar | deterministischer, überschneidungsfreier Zeitplan und vollständiges Paar im Zeitfenster | Stationsmedian des Paar-Deltas, danach Median über Stationen | zeitliche Trennung sowie Umschalt- und Zeitplaneffekte |
| Lokaler Nachbarschafts-Median | ein Target-/lokaler-Referenz-Peer-Zyklus | Target aktiv; ein Beitrag je aktiver lokaler Identität | lokaler Median als Referenz, danach Stations- und Segmentmediane des Delta SNR | wechselnde, unkalibrierte Zusammensetzung |
| Beste lokale Station | ein Target-/beste-lokale-Station-Peer-Zyklus | Target aktiv; stärkste qualifizierende lokale Identität | beste lokale Referenz, danach Stations- und Segmentmediane des Delta SNR | wechselnde Hüllkurve, kein fester Konkurrent |

Die Hierarchie lässt sich von links nach rechts lesen: WSPRadar entscheidet zuerst, welche Evidenzeinheiten zur Analyse gehören, berechnet danach eine Größe auf Peer- oder Funkwegebene und bildet erst dann die angezeigte stationsgleichgewichtete Zusammenfassung. Die folgenden Formeln machen diese Schritte prüfbar; der Text nach jeder Formel erklärt dieselbe Berechnung in Funkpraxis-Sprache.

<a id="sec-7-1"></a>
#### 7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell

WSPRadar liest öffentliche WSPR-Meldungen für jeden abgeschlossenen Lauf aus genau einem ausgewählten, schreibgeschützten Archiv. Die Meldungen sind Beobachtungsdaten heterogener Sender, Empfänger, Decoder und Meldesysteme. Ein abgeschlossener Lauf mischt keine Datenquellen; das ausgewählte Archiv gehört zur Provenienz des Laufs.

Ein **Spot** ist eine gemeldete Zeile eines erfolgreichen Decodes. Ein **WSPR-Zyklus** ist das zweiminütige Intervall, das an einer geraden UTC-Minute beginnt. Analysen im selben Zyklus konsolidieren qualifizierende Zeilen zunächst nach Seite, Peer-Identität und Zyklus und klassifizieren sie erst danach. Die in den Bedienelementen angezeigten effektiven UTC-Grenzen definieren das Analysefenster.

Die kleinste Evidenzeinheit hängt vom Design ab:

* Performance und simultaner Benchmark verwenden eine Peer-Identität in einem zulässigen WSPR-Zyklus.
* Sequenzielles TX A/B behält die exakten geplanten Startzeiten, ordnet sie anhand des konfigurierten Modulo-Zeitplans Target oder Referenz zu und bildet für jeden Peer deterministische Eins-zu-eins-Paare. Beide geplanten Starts müssen im Laufzeitfenster liegen.
* Ein lokaler Nachbarschafts-Benchmark bildet zusätzlich zunächst für jeden Zyklus und Funkweg eine Referenz aus qualifizierenden lokalen Identitäten, bevor Target-minus-Referenz-Evidenz entsteht.

Diese Einheiten werden aus gemeldeten Spots gebildet; sie sind keine zusätzlichen Funkmessungen. Ihr Zweck ist, eindeutig festzulegen, unter welchen Bedingungen ein Erfolg, ein verpasster Decode oder eine gepaarte Differenz gezählt wird.

Der historische Fallback ohne `code = 1` verändert die Auswahl der Quellzeilen nur, wenn die strenge Abfrage keine Target-seitige Evidenz liefert. Der Laufstatus dokumentiert den verwendeten Abfrageweg. Verzögerungen und Datenqualitätsgrenzen der Upstream-Quellen stehen in [Abschnitt 5.6](#sec-6-6).

<a id="sec-7-2"></a>
#### 7.2 Identität, Zuordnung und Zeilenkonsolidierung

WSPRadar behandelt gemeldete Identitäten als wissenschaftliche Daten und nicht als bloße Beschriftung.

| Analyse | Target-Zuordnung | Referenz-/Peer-Identität | Kleinste Ergebniseinheit |
|---|---|---|---|
| RX Performance | exaktes RX-Rufzeichen + Grid-4 des Target-QTH | TX-Rufzeichen + vollständig gemeldeter TX-Locator | Target-aktiver Peer-Zyklus |
| TX Performance | exaktes TX-Rufzeichen + Grid-4 des Target-QTH | RX-Rufzeichen + vollständig gemeldeter RX-Locator | Target-aktiver Peer-Zyklus |
| Referenzstation / Buddy | exaktes Target-Rufzeichen + Target-Grid-4 | exaktes Referenzrufzeichen + unabhängiges Referenz-Grid-4; entfernte Peer-Identität | konsolidierter Peer-Zyklus |
| RX Hardware A/B | exaktes Target-Rufzeichen + Target-Grid-4 | exaktes Referenzrufzeichen + dasselbe abgeleitete Target-Grid-4; entfernte TX-Identität | konsolidierter Peer-Zyklus |
| Simultanes TX Hardware A/B | exaktes Target-Rufzeichen + Target-Grid-4 | exaktes Referenzrufzeichen + dasselbe abgeleitete Target-Grid-4; entfernte RX-Identität | konsolidierter Peer-Zyklus |
| Sequenzielles TX Hardware A/B | gemeinsames exaktes Target-Rufzeichen + Target-Grid-4, nach Zeitplan getrennt | dasselbe Rufzeichen/Grid-4 im Referenzzeitplan; entfernte RX-Identität | geplantes Target-/Referenzpaar |
| Lokaler Nachbarschafts-Benchmark | exaktes Target-Rufzeichen + Target-Grid-4 | lokale Identität innerhalb des Radius; entfernte Peer-Identität | Target-/lokale-Referenz-Peer-Zyklus |

Für die Auswahl der Target-Zeilen im Archiv verwendet WSPRadar Grid-4, auch wenn ein sechsstelliges QTH konfiguriert ist. Das vollständige QTH bleibt für Entfernung, Azimut, Sonnenhöhe und die Geometrie des lokalen Radius relevant. Ein gemeinsames Hardware-A/B-Grid-4 belegt keine physische Ko-Lokation.

Wenn mehrere qualifizierende, nicht identische Zeilen dieselbe logische Kombination aus Seite, Peer und Zyklus darstellen, behält WSPRadar den stärksten qualifizierenden normierten SNR als besten beobachteten Wert dieser logischen Identität. Dadurch können exakte Wiederholungen oder schwächere Zweit-Decodes den beibehaltenen Seitenwert nicht absenken. Der Wert ist jedoch kein Zentralwert eines einzelnen physischen Empfängers. Unterschiedliches Mehrfach-Empfänger- oder Meldeverhalten auf beiden Seiten kann deshalb eine Asymmetrie erzeugen. Beim lokalen Nachbarschafts-Median wird stattdessen zunächst innerhalb jeder lokalen Identität ein Median und erst danach über die Identitäten hinweg aggregiert.

Der lokale Pool schließt das Target anhand des exakten Rufzeichens aus. Basisrufzeichen und Rufzeichen mit Suffix sind verschieden, sofern nicht die exakte Target-Form übereinstimmt. Falsche, veraltete oder wechselnde Locator können eine physische Station aufteilen, geografisch verschieben oder den Ausschluss beweglicher Stationen auslösen.

<a id="sec-7-3"></a>
#### 7.3 Konditionierung auf Target-Aktivität und Zulässigkeit

Sei $A_c$ der Indikator für beobachtbare Target-Beteiligung im Zyklus $c$:

* TX: Im Zyklus existiert irgendwo mindestens eine qualifizierende Meldung einer Target-Aussendung.
* RX: Der Target-Empfänger hat im Zyklus mindestens einen qualifizierenden Decode hochgeladen.

Performance und simultaner Benchmark konditionieren auf $A_c=1$. Dadurch werden bekannte Target-Ausfallzeiten nicht automatisch zu Gegen-Evidenz. Zugleich verändert diese Regel die Analysepopulation: Das Ergebnis beschreibt Zyklen mit beobachtbarer Target-Beteiligung und nicht die gesamte Uhrzeit oder sämtliche geplanten Versuche.

Die Konditionierung ist asymmetrisch. Die Betriebszeit der Referenz bildet kein zweites Gate und muss extern kontrolliert oder dokumentiert werden. Ein Tausch von Target und Referenz kann deshalb zulässige Zyklen und einseitige Decode Outcomes verändern, selbst wenn sich das Vorzeichen des reinen Joint-Delta-SNR erwartungsgemäß umkehrt.

Jede Joint-Beobachtung belegt bereits eine Target-Beteiligung. Das Gate verändert daher nicht die Delta-SNR-Werte der Joint-Beobachtungen. Es verändert die Population einseitiger oder asynchroner Outcomes und bei Performance den Gelegenheitsnenner. Sequenzielles TX A/B verwendet statt des simultanen Target-Active Gates eine deterministische Zeitplanzulässigkeit.

Target-Aktivität darf global nachgewiesen werden, auch wenn der Peer, der sie belegt, außerhalb des ausgewählten geografischen Analysebereichs liegt. Dieser Peer setzt lediglich $A_c$; er geht nicht in die begrenzten Outcomes, Zusammenfassungen oder Exporte ein.

<a id="sec-7-4"></a>
#### 7.4 Performance-Analyseziel, Klassifikation und Zusammenfassungsgrößen

Performance beschreibt die Beteiligung des Targets innerhalb unabhängig beobachtbarer Gelegenheiten der beibehaltenen Peer-Population. Die Größe ist bewusst bedingt: Gefragt wird, was das Target tat, wenn WSPRadar unabhängig belegen konnte, dass die betreffende entfernte Station oder das Signal beobachtbar war.

Für Peer $i$ und Target-aktiven Zyklus $c$ sei $O_{i,c}=1$, wenn unabhängige Aktivitätsevidenz diesen Peer-Zyklus nach Anwendung der gewählten Band-, Identitäts-, Filter- und Bereichsregeln zu einer qualifizierenden Gelegenheit macht. Sei $S_{i,c}=1$, wenn das Target in dieser Gelegenheit ebenfalls die erforderliche Evidenz erzeugt, mit $S_{i,c}\le O_{i,c}$.

* Unabhängige RX-Aktivität: Ein anderer geeigneter Empfänger meldet im selben Zyklus dieselbe Senderidentität.
* Unabhängige TX-Aktivität: Der Peer-Empfänger meldet im selben Zyklus einen anderen Sender auf demselben Band.

Target-Evidenz ohne die für $O_{i,c}=1$ erforderliche unabhängige Aktivität bleibt prüfbar, geht aber nicht in die Dekodierrate ein. Innerhalb qualifizierender RX-Gelegenheiten unterscheidet WSPRadar zwischen Zyklen, die das Target hörte, und Zyklen, die nur andere geeignete Empfänger hörten. Bei TX unterscheidet es zwischen Zyklen, in denen der Peer-Empfänger das Target hörte, und Zyklen, in denen er nur andere qualifizierende Signale im selben Band hörte.

Für einen qualifizierenden Peer gilt:

$$n_i=\sum_c O_{i,c},\qquad h_i=\sum_c S_{i,c}$$

$$r_i=100\%\times\frac{h_i}{n_i}$$

Dabei ist $n_i$ die Zahl bestätigter Gelegenheiten dieses Peers, $h_i$ die Zahl der Target-Erfolge und $r_i$ seine Dekodierrate. Ein Peer trägt nur bei, wenn $n_i$ den konfigurierten Mindestwert erreicht.

Für den geografischen Bereich $g$ mit der qualifizierenden Peer-Menge $I_g$ lautet die stationsgleichgewichtete Dekodierrate:

$$R_{station}(g)=\frac{1}{|I_g|}\sum_{i\in I_g} r_i$$

Dies ist das exakte arithmetische Mittel der beibehaltenen Peer-Raten: Jeder qualifizierende Peer erhält unabhängig von seiner Gelegenheitsanzahl eine gleich große Stimme.

Die Dekodierrate auf Gelegenheitsebene lautet:

$$R_{opportunity}(g)=100\%\times\frac{\sum_{i\in I_g}h_i}{\sum_{i\in I_g}n_i}$$

Dies ist der exakte Anteil erfolgreicher Target-Outcomes über alle beibehaltenen Gelegenheiten: Jede Gelegenheit erhält eine gleich große Stimme. Beide Raten sind ergänzende Zusammenfassungen und keine zwei Näherungen an eine einzige „wahre“ Rate. Sie beantworten unterschiedliche Gewichtungsfragen; ihre Abweichung ist aufschlussreich, wenn sich das Evidenzvolumen zwischen den Peers stark unterscheidet.

Die Mindestens-einmal-Reichweite lautet:

$$Reach(g)=100\%\times\frac{|\{i\in I_g:h_i\ge1\}|}{|I_g|}$$

In Funkpraxis-Sprache ist dies der Prozentsatz qualifizierender Peers, bei denen das Target in mindestens einer qualifizierenden Gelegenheit erfolgreich war. Die Reichweite beschreibt Breite und nimmt mit der Beobachtungsdauer normalerweise zu; sie sagt nicht, wie beständig diese Funkwege funktionierten.

Erfolgreiches Target-SNR ist nur definiert, wenn das Target decodiert oder gemeldet wurde. Es ist damit eine auf erfolgreiche Decodes bedingte Verteilung. Verpasste Gelegenheiten besitzen kein Target-SNR und erhalten keinen künstlichen Wert. Dekodierrate und erfolgreiches SNR müssen gemeinsam gelesen werden: Ein System, das zusätzliche schwache Signale decodiert, kann die praktische Reichweite verbessern und zugleich den Median der erfolgreichen SNR-Werte absenken.

Das Performance-Analyseziel ist somit die bedingte Beteiligung des Targets unter unabhängig beobachtbaren Gelegenheiten in der beibehaltenen Population und unter der gewählten Gewichtung. Es ist weder unbedingte Empfängerempfindlichkeit noch die Erfolgswahrscheinlichkeit sämtlicher Sendeversuche oder der absolute Wirkungsgrad der Station.

<a id="sec-7-5"></a>
#### 7.5 Leistungsnormierung, Korrektur und Benchmark-Delta-SNR

WSPR meldet SNR auf der WSJT-Skala in dB bezogen auf eine Referenzbandbreite von 2500 Hz und überträgt die gemeldete Sendeleistung in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar normiert erfolgreiches TX-seitiges SNR auf gemeldete 30 dBm:

$$SNR_{norm}=SNR_{measured}-P_{TX(dBm)}+30$$

Praktisch wird ein Signal mit 10 dB geringerer gemeldeter Sendeleistung für diesen Vergleich um 10 dB angehoben. Ein mit `-15 dB` gemeldetes SNR bei `20 dBm` wird beispielsweise auf `-5 dB` bei `30 dBm` normiert. Die Rechnung entfernt ausschließlich den **gemeldeten** Leistungsanteil. Sie korrigiert weder Antennengewinn, Strahlungswirkungsgrad, Speiseleitungsverlust, EIRP, Empfängerkalibrierung noch lokalen Stör- oder Rauschpegel.

Die referenzseitige Korrektur wird addiert:

$$SNR_{R,corr}=SNR_R+C_R$$

Für eine gepaarte Beobachtung gilt:

$$D_{i,c}=\Delta SNR_{i,c}=SNR_{T,i,c}-SNR_{R,corr,i,c}$$

Dabei ist $C_R$ die vorzeichenbehaftete additive referenzseitige Korrektur. In der ersten Gleichung bezeichnen $SNR_R$ und $SNR_{R,corr}$ das Referenz-SNR vor und nach der Korrektur. In der Gleichung für das Paar kennzeichnen die Indizes $i,c$ den Peer und die zugeordnete Evidenzeinheit; $SNR_{T,i,c}$ ist das zugehörige normierte Target-SNR und $SNR_{R,corr,i,c}$ das korrigierte Referenz-SNR. Positives $D_{i,c}$ spricht für das Target, negatives für die Referenz. Eine positive Korrektur macht die Referenz vor der Subtraktion stärker und senkt deshalb Delta SNR. Der eingegebene Kalibrierversatz verwendet dasselbe Vorzeichen `target - reference`.

Der Wert $D_{i,c}$ ist eine beobachtete gepaarte Differenz für genau eine beibehaltene Vergleichseinheit. Er wird exakt aus den beiden beibehaltenen SNR-Werten und der gegebenenfalls konfigurierten Korrektur berechnet. Seine Interpretation hängt dennoch davon ab, wofür beide Seiten stehen und wie gut der physische Versuch die übrigen Ketten kontrolliert hat.

Bei RX-Paaren desselben Senders fällt der gemeinsame gemeldete TX-Leistungsanteil heraus. TX-Paare verschiedener Signale hängen unmittelbar von der Richtigkeit der gemeldeten Leistung und von unkorrigierten Unterschieden der Sender- oder Speiseleitungsketten ab. Eine Referenzkorrektur ist nur dann wissenschaftlich vertretbar, wenn der Offset über das relevante Band, den Pegelbereich, den Hardwarezustand und die Zeit näherungsweise additiv und stabil ist.

<a id="sec-7-6"></a>
#### 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen

Benchmark besitzt zwei miteinander verknüpfte Analyseziele:

1. die Verteilung des Target-minus-Referenz-Delta-SNR unter **Joint**-Vergleichseinheiten und
2. die Zusammensetzung der beibehaltenen Evidenz aus **Only Target**, **Joint**, **Only Reference** sowie auf Identitätsebene **Both (Async)**.

Delta SNR existiert nur, wenn beide Seiten vergleichbare Evidenz erzeugen. Die Joint-Teilmenge wird daher durch den erfolgreichen Decode beider Seiten ausgewählt. In statistischer Sprache sind die fehlenden Paare normalerweise nicht „zufällig fehlend“: Schwache Signale, Kollisionen, QRM, Decoderverhalten, Leistungsunterschiede und Funkwegbedingungen können alle beeinflussen, ob ein Paar entsteht. In Stationssprache heißt das: Die überlebenden Paare müssen nicht jede Gelegenheit nahe der Decode-Schwelle gleich gut repräsentieren.

Einseitige Evidenz besitzt kein SNR der fehlenden Seite, das rekonstruiert werden könnte. Ihr darf kein künstliches Delta SNR zugewiesen werden, und sie wird nicht als Paar leistungsnormiert. Bei TX Benchmark können unterschiedliche tatsächliche oder gemeldete Leistungen einseitige Outcomes stark beeinflussen, selbst wenn das Joint-Delta-SNR normiert ist.

`Both (Async)` bedeutet, dass für eine Identität beibehaltene Evidenz beider Seiten existiert, aber für die betreffende Stationskategorie keine qualifizierende Einheit desselben Zyklus oder kein geplantes Paar erhalten bleibt. Die Kategorie zeigt eine breitere Beteiligung beider Seiten, trägt jedoch kein gepaartes Delta SNR bei.

Die Zensierung auf erfolgreiches SNR bei Performance und die Auswahl nach gemeinsamem Decode bei Benchmark sind verschiedene Selektionsprozesse. WSPRadar zeigt Decode Outcomes und Joint-Evidenzanteil, damit die gepaarten Delta-SNR-Zusammenfassungen im Verhältnis zur breiteren beibehaltenen Evidenz gelesen und nicht mit der vollständigen Stationspopulation gleichgesetzt werden.

<a id="sec-7-7"></a>
#### 7.7 Aggregationshierarchie und Gewichtung

WSPRadar verwendet eine hierarchische Aggregation: Zuerst wird die Evidenz innerhalb jeder Peer-Identität zusammengefasst, danach über die Peers hinweg. Dadurch kann ein Peer mit hohem Datenvolumen ein stationsgleichgewichtiges Ergebnis nicht allein deshalb dominieren, weil er mehr Beobachtungen gemeldet hat. Zugleich beantworten stationsgleichgewichtete und beobachtungsbezogene Zusammenfassungen bewusst unterschiedliche Fragen.

**Performance**

1. Jeden zulässigen Peer-Zyklus klassifizieren.
2. Qualifizierende Target-Erfolge und Gegen-Evidenz nach Peer-Identität zusammenfassen; Target-Beobachtungen ohne unabhängige Bestätigung getrennt für die Prüfung bewahren.
3. Die Mindestanzahl an Gelegenheiten anwenden.
4. Für jeden Peer eine Dekodierrate $r_i$ berechnen.
5. Das gleichgewichtete Peer-Mittel $R_{station}$ berechnen.
6. $R_{opportunity}$ als ergänzende, nach Gelegenheiten gewichtete Zusammenfassung beibehalten.

Das erste Ergebnis beschreibt den typischen qualifizierenden Peer bei gleicher Peer-Gewichtung; das zweite die gepoolte beibehaltene Gelegenheits-Population.

**Simultaner Benchmark**

1. Target- und Referenzevidenz nach Peer und Zyklus konsolidieren.
2. Für Joint-Zyklen $D_{i,c}$ berechnen.
3. Die Mindestanzahl an Joint-Evidenz je Peer anwenden.
4. Den Peer-Median berechnen:

    $$m_i=\operatorname{median}_{c}(D_{i,c})$$

5. Für den Bereich $g$ die stationsgleichgewichtete Segmentzusammenfassung berechnen:

    $$M_g=\operatorname{median}_{i\in I_g}(m_i)$$

Dabei ist $m_i$ die typische gepaarte Differenz eines Peers und $M_g$ der Median dieser Peer-Mediane. Jeder qualifizierende Peer trägt somit genau einen Wert zum Segmentergebnis bei. Der Median aller $D_{i,c}$ auf Beobachtungsebene bleibt getrennt erhalten; in dieser Zusammenfassung erhalten Peers mit mehr Joint-Beobachtungen ein größeres Gewicht.

**Sequenzielles TX A/B**

1. Meldungen der exakten Identität behalten, deren Startzeit zur Target- oder Referenzphase passt.
2. Geplante Starts unter dem gemeinsamen Wiederholintervall anhand des kleinsten zyklischen Abstands eins zu eins paaren.
3. Verlangen, dass beide geplanten Starts im Laufzeitfenster liegen.
4. Innerhalb jedes Peers und geplanten Paars für jede Seite einen Mikro-Median berechnen.
5. Das Paar-Delta berechnen, wenn beide Mikro-Mediane existieren; andernfalls das Paar als einseitige Evidenz behalten.
6. Die Mindestanzahl vollständiger Paare je Peer anwenden.
7. Peer- und Segmentmediane wie oben berechnen.

Der Mikro-Median schützt eine geplante Seite vor duplikatähnlichen Wiederholungszeilen, macht die beiden nacheinander gesendeten Aussendungen aber nicht simultan.

**Lokaler Nachbarschafts-Median**

Für jeden entfernten Peer-Zyklus berechnet WSPRadar zunächst je aktiver lokaler Identität aus `Rufzeichen + Locator` genau einen normierten SNR-Beitrag und danach den exakten Median über die beitragenden lokalen Identitäten. Eine nicht beobachtete lokale Identität wird weggelassen und nicht mit null angesetzt. Die Referenzkorrektur wird vor der Aggregation des lokalen Pools angewendet. Anschließend wird das Target mit diesem zyklus- und funkwegspezifischen Median verglichen; daraus entstehen Peer- und Segmentmediane des Delta SNR.

**Beste lokale Station**

Für jeden entfernten Peer-Zyklus wählt WSPRadar den stärksten qualifizierenden, korrigierten lokalen Beitrag als Referenz. Die resultierende Referenz ist eine wechselnde obere Hüllkurve. Sie ist weder ein lokales Mittel noch ein Vergleich mit einer festen Station.

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

Geografische Benchmark-Zusammenfassungen verwenden je qualifizierender Identität genau einen Peer-Median des Delta SNR und danach den Segmentmedian dieser Peer-Mediane. Das Delta SNR auf Beobachtungsebene bleibt als getrennt gewichtete Verteilung verfügbar. Die erste Sicht beantwortet „Was zeigte der typische qualifizierende Peer?“, die zweite „Was zeigten die beibehaltenen gepaarten Beobachtungen, wenn jedes Paar zählt?“.

<a id="sec-7-8-2"></a>
##### 7.8.2 Abdeckung der Benchmark-Evidenz

Für Station $i$ im Bin $b$ seien die Anzahlen Only Target, Joint und Only Reference $T_{i,b}$, $J_{i,b}$ und $R_{i,b}$ mit:

$$N_{i,b}=T_{i,b}+J_{i,b}+R_{i,b}$$

Eine beitragende Station liefert eine aufgeteilte Stützungsstimme:

$$v_{T,i,b}=\frac{T_{i,b}}{N_{i,b}},\qquad v_{J,i,b}=\frac{J_{i,b}}{N_{i,b}},\qquad v_{R,i,b}=\frac{R_{i,b}}{N_{i,b}}$$

Praktisch erhält jeder Peer insgesamt eine Stationsstimme, die entsprechend seiner Mischung aus Only Target, Joint und Only Reference in diesem Bin aufgeteilt wird.

Der stationsgleichgewichtete Joint-Evidenzanteil lautet:

$$JES_{station}(b)=100\%\times\operatorname{mean}_{i}\left(\frac{J_{i,b}}{N_{i,b}}\right)$$

Der Joint-Evidenzanteil auf Outcome-Ebene lautet:

$$JES_{outcome}(b)=100\%\times\frac{\sum_iJ_{i,b}}{\sum_iN_{i,b}}$$

Die erste Größe gibt jedem beitragenden Peer dasselbe Gewicht, die zweite jeder beibehaltenen Vergleichseinheit. Der Joint-Evidenzanteil misst die Paarbarkeit – also welcher Anteil der beibehaltenen Evidenz zu Delta SNR beitragen kann. Er ist keine Gewinnquote des Targets.

Unter dem Target-Active Gate sind Only Target und Only Reference gerichtet und asymmetrisch. Sequenzielles TX A/B verwendet stattdessen deterministische vollständige oder einseitige geplante Paare; auch ein einseitiges Paar besitzt jedoch kein Paar-Delta.

<a id="sec-7-8-3"></a>
##### 7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung

Chronologische Ansichten bewahren die tatsächliche Reihenfolge des Laufs über das vollständige ausgewählte UTC-Zeitfenster mit der gewählten Zeit-Bin-Breite. Die Bins beginnen am ausgewählten Startzeitpunkt; das abschließende Intervall kann kürzer sein, und Zeitabschnitte ohne Evidenz bleiben leer, statt zu 0 dB zu werden. UTC-Stunden-Ansichten **falten** die Evidenz, indem Beobachtungen verschiedener Tage auf dieselbe 24-Stunden-UTC-Uhr ausgerichtet werden. Die chronologische Sicht fragt damit „Was änderte sich während dieses Laufs?“, die gefaltete Sicht „Kehrte ein Muster zu einer bestimmten UTC-Stunde an mehreren berücksichtigten Tagen wieder?“.

Für die Abweichung des erfolgreichen Performance-SNR geht ein Peer nur dann in die Anomaliepopulation ein, wenn er im vollständigen Laufzeitfenster mindestens drei erfolgreiche normierte Target-SNR-Beobachtungen besitzt. Seine Basislinie ist der Median dieser Erfolge. Jede erfolgreiche Beobachtung trägt bei:

$$A_{i,c}=SNR_{i,c}-\operatorname{median}_{c'}(SNR_{i,c'})$$

Dabei kennzeichnet $c$ die aktuelle erfolgreiche Beobachtung; $c'$ durchläuft alle erfolgreichen Beobachtungen des Peers $i$ im vollständigen Laufzeitfenster, aus denen seine Basislinie entsteht. `0 dB` bedeutet damit „auf dem für diesen Funkweg üblichen erfolgreichen Pegel“ und nicht Target–Referenz-Gleichheit. Ein positiver Wert bedeutet, dass dieser erfolgreiche Decode stärker als der für diesen Peer übliche erfolgreiche Pegel im Lauf war; ein negativer Wert bedeutet schwächer. Es handelt sich um eine Abweichung innerhalb eines Funkwegs und nicht um Target-minus-Referenz-Delta-SNR.

Chronologisch trägt jeder Peer je ausgewähltem Bin höchstens einen Median der Abweichung bei. In der UTC-gefalteten Sicht trägt jeder Peer zunächst je Datum und UTC-Stunde einen Median bei; erst danach werden diese Peer-Datum-Stunden-Werte über die gefaltete Population zusammengefasst. Dadurch dominieren besonders häufig meldende Peers oder Tage nicht allein durch ihre Rohzeilenzahl.

Die zeitliche Performance-Stützung verwendet dieselben qualifizierenden Peers, behält aber alle bestätigten Gelegenheiten einschließlich der Peers, die aus der erfolgreichen SNR-Anomalieebene ausgeschlossen sind. In einem chronologischen Bin liefert jeder Peer eine nach seiner Dekodierrate im Bin aufgeteilte Stimme. Die gesamte Stationsstützung entspricht damit der Zahl beitragender Peers; das Teilungsverhältnis reproduziert die stationsgleichgewichtete Rate. Die Gelegenheitsstützung ist die rohe Zahl bestätigter Gelegenheiten; ihr Teilungsverhältnis reproduziert die Dekodierrate auf Gelegenheitsebene.

Für jede gefaltete UTC-Stunde ist die Stationsstützung die durchschnittliche Zahl unterschiedlicher Peer-Datum-Stunden-Präsenzen über die berücksichtigten Tage, deren Stundenslot das Analysefenster überlappt. Die gefaltete stationsgleichgewichtete Rate entsteht, indem die Outcomes jedes Peers zu dieser UTC-Stunde über die berücksichtigten Tage gepoolt, daraus je Peer eine Rate berechnet und anschließend jeder Peer gleich gewichtet wird. Gefaltete Gelegenheitsanzahlen sind gepoolte Outcome-Summen geteilt durch den zugehörigen Nenner berücksichtigter Tage.

Bei Performance ist ein **berücksichtigter UTC-Tag** ein Datum, an dem im aktiven Bereich und ausgewählten Fenster mindestens eine qualifizierende bestätigte Gelegenheit existiert. Eine im Fenster liegende Datum-Stunde ohne Evidenz trägt für einen berücksichtigten Tag null bei; eine Datum-Stunde außerhalb des Fensters wird ausgeschlossen. Eine nur teilweise überlappende erste oder letzte Stunde zählt als ein vollständiger berücksichtigter Slot und wird nicht nach Expositionsanteil gewichtet. Dadurch können Mittelwerte an Randstunden niedriger ausfallen. Die UTC-Stunden-Faltung erfordert mindestens zwei berücksichtigte Tage.

Das zeitliche Benchmark-Delta-SNR verwendet beibehaltene Joint-Beobachtungen oder vollständige geplante Paare. Wenn keine gepaarten Werte verbleiben, zeigt das Delta-SNR-Panel weiterhin das vollständige ausgewählte UTC-Zeitfenster und weist auf die fehlende gepaarte Evidenz für Δ SNR hin. Das bedeutet, dass im dargestellten Bereich keine beibehaltene Joint-Beobachtung beziehungsweise kein vollständiges geplantes Paar verbleibt; daraus folgt nicht, dass die Datenquelle keine Beobachtungen lieferte, und die zeitliche Abdeckung kann weiterhin einseitige Outcomes zeigen. Chronologische Bins fassen gepaarte Werte in tatsächlicher Zeit zusammen; UTC-Stunden-Bins fassen dieselbe gepaarte Population nach Stunde über die Tage zusammen, die in der beibehaltenen Benchmark-Evidenz vertreten sind. Die zeitliche Benchmark-Abdeckung verwendet alle beibehaltenen Einheiten Only Target, Joint und Only Reference sowie die beiden oben definierten Zusammenfassungen des Joint-Evidenzanteils. Auch die Benchmark-Faltung erfordert mindestens zwei Tage mit Evidenz.

<a id="sec-7-8-4"></a>
##### 7.8.4 Zusammenfassungen für den ausgewählten Funkweg

Die Evidenz der ausgewählten Station filtert den aktiven beibehaltenen Bereich auf genau eine Peer-Identität, ohne die vorgelagerte Analysepopulation zu verändern.

Bei Performance zeigt der ausgewählte Funkweg:

* das tatsächliche normierte erfolgreiche Target-SNR in chronologischen Bins;
* je berücksichtigtem Datum und UTC-Stunde einen Median im gefalteten SNR-Profil;
* Anzahlen erfolgreicher und Gegen-Gelegenheiten sowie
* die Dekodierrate im Zeitverlauf.

Bei genau einem Peer sind die stationsgleichgewichtete Dekodierrate und die Dekodierrate auf Gelegenheitsebene innerhalb eines belegten Bins numerisch identisch, weil beide dieselben Erfolge und Gelegenheiten dieses einen Peers verwenden. Die getrennten Stützzahlen unterscheiden dennoch Funkwegpräsenz von Evidenzvolumen.

Bei Benchmark zeigt der ausgewählte Funkweg das Delta SNR jeder Joint-Einheit oder jedes vollständigen geplanten Paars auf Beobachtungsebene und getrennt die Abdeckung durch Only Target, Joint und Only Reference. Ein Wechsel des ausgewählten Funkwegs oder Darstellungs-Bins verändert nur die Ansicht der beibehaltenen Evidenz, nicht die vorgelagerte Zuordnung, Zulässigkeit oder Aggregation.

<a id="sec-7-8-5"></a>
##### 7.8.5 Deskriptive Streuung und Visualisierungstransformationen

IQR- und Min-Max-Darstellungen sind deskriptive Streuungsmaße und keine Konfidenzintervalle. Ein IQR-Band wird nur gezeichnet, wenn mindestens fünf Werte zum jeweiligen Bin beitragen; der Median bleibt auch bei weniger Werten sichtbar. Leere Bins bleiben fehlend und werden nicht zu künstlichen Nullbeobachtungen.

Benchmark-Histogramme verwenden normalerweise 1-dB-Klassen, 0,5 dB nur bei einem klaren Halb-dB-Raster und gröbere Klassen bei großen Wertebereichen, damit die Bin-Anzahl begrenzt bleibt. Zeitliche Dichtezellen verwenden ganzzahlige dB-Klassen. Jedes Dichtepanel wird unabhängig normiert:

$$D_{relative}=100\times\frac{n_{cell}}{\max(n_{cell,panel})}$$

Dabei ist $n_{cell}$ die Evidenzanzahl in einer Dichtezelle. Die Division durch die am stärksten belegte Zelle wandelt das Panel in eine Darstellung der relativen Dichte um, ohne die zugrunde liegenden Anzahlen zu verändern.

`100` bezeichnet damit die am stärksten belegte Zelle dieses Panels und nicht 100 % der gesamten Evidenz. Dichtefarben erlauben keinen Vergleich des absoluten Evidenzvolumens zwischen unabhängig normierten Panels; dafür sind die Stützzahlen maßgeblich.

Zeitliche Benchmark-Ansichten und Histogramme verwenden eine rein darstellungsbezogene monotone Skala, die um den Bereichsmedian $M$ zentriert ist. Bei großer Spannweite liegen gleichmäßige visuelle Schritte bei $M$, $M\pm3$, $M\pm6$, $M\pm10$, $M\pm20$ und $M\pm30$ dB; ein Randanker liegt bei $M\pm60$ dB und wird bei Bedarf fortgesetzt. Wenn jede erforderliche Abweichung höchstens `10 dB` beträgt, lauten die engeren Anker $M$, $M\pm1$, $M\pm3$, $M\pm6$ und $M\pm10$ dB; Fortsetzungsanker liegen bei $M\pm20$ und $M\pm40$ dB. Der erforderliche Bereich umfasst die zutreffenden Rohgrenzen des Histogramms beziehungsweise die gerundeten Heatmap-Klassengrenzen, eine Mindesthalbspanne von `3 dB` und den absoluten Wert `0 dB`, damit Target-Referenz-Gleichheit sichtbar bleibt. Die Ankerabbildung verändert ausschließlich die dargestellten Abstände: Rohe Delta-SNR-Werte, Bin-Zuordnung, Anzahlen, Mediane und Quartile bleiben unverändert. Wegen der nichtlinearen vertikalen Abbildung ist die **Balkenlänge** entlang der Prozentachse – nicht die dargestellte Fläche – die quantitative Kodierung.

Performance-Ansichten des erfolgreichen SNR bleiben auf einer linearen dB-Achse.

<a id="sec-7-9"></a>
#### 7.9 Geografie, Sonnenstandsklassifikation und Populationsfilter

Entfernung und Azimut werden aus dem konfigurierten Target-QTH und den gemeldeten Peer-Locators mit einem kugelförmigen Erdradius von 6371 km berechnet. Die Karte verwendet eine azimutal äquidistante Projektion mit Target-QTH als Mittelpunkt, radialen Grenzen bei 2500, 5000, 10000, 15000, 20000 und 22000 km sowie 22,5-Grad-Azimutsektoren.

Gemeldete Locator repräsentieren Locator-Felder und keine vermessenen Antennenkoordinaten. Geografische Zusammenfassungen sind mit diesen Eingaben intern konsistent, dürfen aber nicht als vermessungsgenaue Position oder direkte Messung des Abstrahlwinkels interpretiert werden.

`Maximale Peer-Entfernung vom Target (km)` entfernt Peers an oder jenseits der gewählten Entfernung vor der wissenschaftlichen Aggregation und dem Export verarbeiteter Evidenz. Kartensegmente, Stützzahlen, Segment-Inspektor und Exporte verwenden damit dieselbe beibehaltene Peer-Population. Inspektor-Auswahlen können diese Population eingrenzen, aber keine ausgeschlossenen Zeilen wiederherstellen.

Zwei Regeln liegen vor diesem geografischen Bereich:

* Die Konditionierung auf Target-Aktivität bleibt global. Ein Peer außerhalb des Bereichs kann den Betrieb des Targets belegen, ohne selbst zu einem begrenzten Outcome zu werden.
* Ist der Ausschluss beweglicher Stationen aktiviert, werden Rufzeichen mit wechselndem Standort in der ansonsten zulässigen globalen Population erkannt, bevor der Entfernungsbereich angewendet wird.

Die Sonnenstandsklassifikation verwendet die Sonnenhöhe am Target-QTH. Evidenz desselben Zyklus verwendet den Zykluszeitstempel. Beim geplanten TX A/B wird die Mitte zwischen den geplanten Target- und Referenzstarts verwendet, damit ein Paar nicht auf zwei Sonnenklassen verteilt werden kann.

Die Zeilengrenze des Archivs und die Bedienelemente, mit denen sich die abgerufene Population verkleinern lässt, sind betriebliche Fragen aus [Abschnitt 5.6](#sec-6-6). Sie verändern die wissenschaftlichen Zusammenfassungen nicht, nachdem die beibehaltene Population gebildet wurde.

<a id="sec-7-10"></a>
#### 7.10 Abhängigkeit, Unsicherheit und Geltungsbereich der Validierung

Die Formeln dieses Kapitels berechnen exakte deskriptive Zusammenfassungen der beibehaltenen Evidenz. Unsicherheit entsteht, wenn daraus Aussagen über nicht beobachtete Bedingungen, künftige Läufe, eine breitere Stationspopulation oder eine physische Ursache abgeleitet werden.

WSPRadar-Beobachtungen sind geclustert und nicht unabhängig. In gewöhnlicher Stationssprache sind 1.000 Spots nicht dasselbe wie 1.000 voneinander unabhängige Experimente. Wiederholte Zyklen eines Peers teilen Hardware- und Funkwegeigenschaften; Stationen in benachbarten Regionen teilen Ausbreitungsbedingungen; Zeit-Bins sind autokorreliert; und ein einzelnes ionosphärisches Ereignis oder eine Störung kann viele Beobachtungen gleichzeitig beeinflussen. Eine große Zeilenzahl ist daher keine unabhängige Stichprobengröße.

Stationsgleichgewichtung verringert die Dominanz besonders aktiver Peers, und Mediane verringern die Empfindlichkeit gegenüber einzelnen Ausreißern. Beides erzeugt weder Unabhängigkeit noch beseitigt es systematische Verzerrungen oder liefert eine Stichprobenverteilung. IQRs beschreiben die Streuung innerhalb des Laufs und sind keine Unsicherheitsintervalle.

WSPRadar berichtet derzeit deskriptive Zusammenfassungen. Es passt nicht automatisch ein Stichproben- oder Abhängigkeitsmodell an und berechnet weder Standardfehler, Konfidenzintervalle, p-Werte, Teststärke noch kausale Effekte. Naive Inferenzrechnungen, die jeden Spot oder jedes Paar als unabhängig behandeln, würden die Unsicherheit im Allgemeinen unterschätzen.

Wissenschaftliche Unterstützung sollte deshalb auf mehreren Ebenen beschrieben werden:

* **Evidenztiefe:** Zahl der Gelegenheiten, Joint-Einheiten oder geplanten Paare;
* **Evidenzbreite:** Zahl und geografische Vielfalt der Peer-Identitäten;
* **Konsistenz innerhalb eines Laufs:** Übereinstimmung der stationsgleichgewichteten, beobachtungsbezogenen, geografischen und zeitlichen Zusammenfassungen;
* **experimentelle Wiederholbarkeit:** erneutes Auftreten in einem neuen, geeignet kontrollierten Lauf und
* **experimentelle Kontrolle:** zur Aussage passende Kalibrierung, Kreuztausch, vertauschter Zeitplan oder unabhängige Messung.

Diese Ebenen machen aus den beibehaltenen Zusammenfassungen keine kalibrierten Vorhersagen. Sie zeigen, wie viel Evidenz eine begrenzte deskriptive oder vergleichende Aussage stützt und wie gut der physische Versuch eine Zuordnung zur vermuteten Ursache trägt.

Empirische Prüfungen der Softwarevalidierung sind keine zeitlosen Methodendefinitionen. Jede angeführte Validierungskennzahl muss Datensätze, Datum, WSPRadar-Version oder Quellrevision und Berechnungsmethode nennen. Ohne diese Provenienz sollte sie aus dem normativen Handbuch entfernt oder ausdrücklich als datierte Validierungsprüfung gekennzeichnet werden.

<a id="sec-8"></a>
### 8. Evidenzgerechte Aussagen und Reproduzierbarkeit

WSPRadar stützt begrenzte deskriptive und vergleichende Aussagen über beibehaltene Beobachtungsevidenz. Eine belastbare Berichterstattung nennt die konditionierte Population, die berichtete Zusammenfassung und Gewichtung, die Unterstützung, das Versuchsdesign und die verbleibenden unbeobachteten oder unkontrollierten Variablen.

<a id="sec-8-1"></a>
#### 8.1 Aussageklassen und evidenzgerechte Formulierungen

| Aussageklasse | Was WSPRadar stützen kann | Zusätzliche Voraussetzung für eine stärkere Aussage |
|---|---|---|
| **Deskriptiv** | Reichweite, Dekodierrate, erfolgreiches SNR, Delta SNR, Decode Outcomes und wo sie in der ausgewählten Evidenz auftraten. | Population, Gewichtung, Bereich und Unterstützung angeben. |
| **Vergleichend** | Unterschied Target gegenüber Referenz unter dem gewählten Benchmark-Design. | Angeben, was die Referenz darstellt und welche zugeordnete Teilmenge verwendet wurde. |
| **Bauteilzuordnung** | Ein mit einem lokalen Pfad oder Bauteil verbundener Unterschied. | Kontrolliertes Hardware A/B, Kalibrierung und möglichst Kreuztausch beziehungsweise Rollentausch. |
| **Kausal** | Die geprüfte Änderung verursachte den beobachteten Effekt. | Ein Design, das plausible Alternativerklärungen kontrolliert; WSPRadar-Zusammenfassungen allein reichen nicht aus. |
| **Inferenzstatistisch** | Konfidenz, Signifikanz oder ein auf eine Population verallgemeinerbarer Effekt. | Ein begründetes Abhängigkeitsmodell und eine inferenzstatistische Analyse, die WSPRadar derzeit nicht liefert. |

Verwende den Ergebnistyp, der zur Aussage passt:

* **Performance** stützt das konditionale Verhalten des Targets innerhalb unabhängig bestätigter Gelegenheiten und seine Mindestens-einmal-Reichweite während des ausgewählten Zeitfensters.
* **Benchmark-Delta-SNR** stützt die gepaarte Beschreibung Target minus Referenz innerhalb der Joint-Teilmenge.
* **Decode Outcomes** stützen Aussagen über Paarbarkeit und einseitige Evidenz.
* **Entfernungs- oder Richtungsstruktur** stützt Aussagen über beobachtete Funkwegsegmente und nicht über einen direkten Abstrahlwinkel oder ein Gewinnmuster.
* **Lokaler Nachbarschafts-Benchmark** stützt Aussagen relativ zur gewählten dynamischen lokalen Definition und keine dauerhafte Stationsrangliste.

| Vermeiden | Evidenzgerechte Formulierung |
|---|---|
| „Antenne A hat 3 dBi mehr Gewinn.“ | „Pfad A ergab gegenüber B ein stationsgleichgewichtetes medianes Delta SNR von +3,0 dB für die gepaarte Evidenz in diesem Band, Zeitfenster und Segment.“ |
| „Die Empfindlichkeit meines Empfängers beträgt 72 %.“ | „Die stationsgleichgewichtete Dekodierrate des Target-Empfängers betrug 72 % unter qualifizierenden Peer-Zyklen, die andernorts unabhängig bestätigt wurden.“ |
| „Performance sollte nahe 100 % liegen.“ | „Die Dekodierrate ist durch unabhängig bestätigte Gelegenheiten bedingt; 100 % ist kein zu erwartender Ausgangswert.“ |
| „A ist statistisch signifikant besser.“ | „Der deskriptive gepaarte Median begünstigte A in der ausgewählten Evidenz; ein Signifikanztest wurde nicht durchgeführt.“ |
| „Die Antenne hat einen flacheren Abstrahlwinkel.“ | „Der beobachtete Vorteil konzentrierte sich auf die angegebenen größeren Entfernungssegmente; der Abstrahlwinkel wurde nicht gemessen.“ |
| „A ist effizienter, weil es mehr exklusive Decodes hatte.“ | „A erzeugte unter den dokumentierten Leistungs-, Zeitplan- und Netzwerkbedingungen mehr einseitige Decode-Evidenz; der Wirkungsgrad wurde nicht isoliert.“ |
| „Der lokale Median ist die durchschnittliche lokale Station.“ | „Die Referenz war der Zyklus-/Funkwegmedian aus je einem Beitrag jeder aktiven lokalen Identität aus Rufzeichen plus Locator.“ |

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
* Archive enthalten erfolgreiche Decodes und keine vollständigen Versuchsprotokolle;
* Performance ist auf unabhängig beobachtbare Gelegenheiten konditioniert;
* die Konditionierung auf Target-Aktivität ist asymmetrisch;
* erfolgreiches Target-SNR ist auf erfolgreiche Decodes zensiert;
* Benchmark-Delta-SNR wird durch die gemeinsame Beobachtung beider Seiten ausgewählt;
* einseitige Evidenz besitzt kein SNR der fehlenden Seite;
* simultanes TX behält Unterschiede zwischen den Ketten bei Leistung, Frequenzgang, Entkopplung und Kopplung bei;
* sequenzielles TX bleibt zeitlich getrennt;
* Stationshardware, Software, Gelände, lokaler Störpegel, Polarisation und Ausbreitung bleiben gekoppelt, sofern der Versuch sie nicht kontrolliert;
* Beobachtungen sind über Station, Zeit, Geografie und Ausbreitung geclustert; und
* Upstream-Datensätze und Verfügbarkeit können sich nach dem ursprünglichen Lauf verändern.

Diese Grenzen definieren, was die Zusammenfassungen beschreiben; sie machen die Beobachtungen nicht wertlos. Breite, innerhalb eines Laufs konsistente und experimentell wiederholbare Evidenz kann betrieblich überzeugend sein und dennoch deskriptiv bleiben.

<a id="sec-8-3"></a>
#### 8.3 Checkliste für Berichterstattung und Reproduzierbarkeit

Bewahre für eine ernsthafte Analyse drei Ebenen auf.

**1. Analysedefinition**

* WSPRadar-Anwendungsversion und, soweit verfügbar, Quellrevision;
* RX-/TX-Richtung, Ergebnistyp und Benchmark-Design;
* exakte Target- und Referenzidentitäten und Locator;
* Band und wirksame UTC-Grenzen;
* geografischer Bereich, Sonnenstand, Ausschlüsse und Evidenzschwellen;
* Zweck der Referenzkorrektur, vorzeichenbehafteter Wert und Kalibriergrundlage;
* primärer vorab festgelegter Auswertungsbereich und alle Sensitivitätsanalysen; und
* ob der Lauf explorativ oder bestätigend war.

**2. Evidenz hinter der Schlussfolgerung**

* berichtete Zusammenfassung und Gewichtungsebene;
* qualifizierende Peers und Gelegenheiten bei Performance;
* Joint-Peers und Joint-Spots/-Paare bei Benchmark;
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

Bewahre das ursprüngliche Exportpaket als Evidenznachweis dieses Laufs auf. Ein späterer Abruf kann Korrekturen im Upstream-Archiv oder eine neuere WSPRadar-Version widerspiegeln.

<a id="sec-8-4"></a>
#### 8.4 Exportpaket der Analyse

`Alle Ergebnisse zum Download vorbereiten` erstellt aus dem abgeschlossenen Lauf und den aktuellen Inspektor-Auswahlen ein Paket. Ein typisches Paket enthält:

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
  table_station_insights_current_segment.csv
  table_drilldown_selected_stations.csv
  table_drilldown_all_stations_current_segment.csv
  analysis_cache.parquet
performance/
  figure_map_highres.png
  figure_segment_insight.png
  figure_segment_temporal_snr_deviation.png
  figure_segment_temporal_evidence.png
  figure_selected_station_snr_evidence.png
  figure_selected_station_temporal_evidence.png
  table_station_insights_current_segment.csv
  table_drilldown_selected_stations.csv
  table_drilldown_all_stations_current_segment.csv
  analysis_cache.parquet
```

Dateien ohne anwendbares Ergebnis oder ohne ausgewählte Station können fehlen.

| Artefakt | Wissenschaftlicher Inhalt und Bereich |
|---|---|
| `wspradar_config.config` | Versionierte ausführbare Definition und dauerhafte Einstellungen der Ergebnisansicht. |
| `run_metadata.json` | Provenienz von Anwendung und Export, Richtung, Band, Zeitauswahl, Benchmark-/Korrekturdefinition, Filter, Schwellen und Inspektor-Auswahlen. |
| `analysis_cache.parquet` | Verarbeitete beibehaltene Evidenz nach wissenschaftlichen Filtern und geografischem Bereich; kein unveränderter Upstream-Dump. |
| `table_station_insights_current_segment.csv` | Zusammenfassungen je Peer für den aktiven Bereich des Segment-Inspektors. |
| Drill-Down-CSV-Dateien | Beibehaltene Evidenz auf Zeilenebene für ausgewählte Identitäten oder Identitäten im aktiven Bereich. |
| Karten- und Segmentabbildungen | Geografische und segmentbezogene deskriptive Zusammenfassungen des abgeschlossenen Ergebnisses. |
| Zeitliche Abbildungen | Chronologische und nach UTC-Stunde gefaltete Zusammenfassungen für das aktive Segment. |
| Abbildungen der ausgewählten Station | Genau eine ausgewählte Peer-Identität; mehrere ausgewählte Funkwege werden niemals zusammengefasst. |

**Ausgewählte öffentliche maschinenlesbare Vertragsbezeichnungen.** Diese knappe Tabelle nennt unterstützte externe Bezeichnungen, die für den Funkbetrieb und nachgelagerte Auswertungen nützlich sind; sie ist kein vollständiger Katalog der Felder gespeicherter Konfigurationen, URL-Parameter oder Exportmetadaten. Für Felder gespeicherter Konfigurationen ist das formale JSON-Schema (`config/wspradar-config.schema.json`) maßgeblich; der unterstützte öffentliche URL-Vertrag ist separat versioniert. Private Implementierungsbezeichnungen sind bewusst ausgelassen. Diese Namen sind keine Begriffe zur Erklärung der wissenschaftlichen Methode.

| Vertragsbereich | Exakte Bezeichnungen | Bedeutung |
|---|---|---|
| Konfigurationsformat | Schemaversion `1` | Aktueller `.config`-Vorproduktionsvertrag; ungültige oder nicht unterstützte Dateien werden abgelehnt und nicht stillschweigend umgedeutet. |
| Werte des Ergebnistyps | `performance`, `benchmark` | Werte, die neue Analyse-URLs, Konfigurationen und Exporte ausgeben. |
| Dauerhafte Blöcke der Ergebnisansicht | `results_view.performance`, `results_view.benchmark` | Gespeicherte Inspektionsoptionen. Ihr Vorhandensein erzeugt oder startet kein zusätzliches Ergebnis. |
| Ergebnisordner | `performance/`, `benchmark/` | Oberste Ergebnisordner im Exportpaket. |
| Abbildungsmetadaten | `selected_evidence_figures`, `benchmark_evidence_figures`, `benchmark_evidence_recipes` | Stabile Zuordnungen für zutreffende exportierte Abbildungen und Benchmark-Rezepte. |
| Korrekturmetadaten | `benchmark_snr_correction_mode`, `benchmark_snr_correction_db` | Semantische Auswahl der Korrektur und ihr numerischer dB-Wert. |

Das Exportpaket bewahrt die verarbeitete Evidenz und die von WSPRadar erfasste Provenienz. Es enthält keine maßgeblichen externen Betriebsprotokolle, physischen Aufbaumessungen oder unveränderten Antworten der Upstream-Archive. Bewahre diese wie in [Abschnitt 8.3](#sec-8-3) beschrieben getrennt auf.

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

* <a id="ref-11"></a><a href="https://www.wsprdaemon.org/">[Ref-11]</a> **Offizielle Projektwebsite.** WSPRDaemon, *WSPR Daemon*: mehrkanalige Spot-Erfassung, Decodierung und Reporting von WSPR/FST4W, Rauschschätzung, Datenbank-/Grafana-Ausgabe sowie Datendienste für Drittanwendungen. Abgerufen am 2026-08-06.

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

Dieser Teil bündelt optionale Verfahren für parallele WSJT-X-Instanzen und die Einrichtung simultaner Sender, Hinweise zur sequenziellen TX-A/B-Zeitplanung und Umschaltung, die Kalibrierung der Referenzseite und die Projektlizenz. Verwende die Abschnitte, die für deine Station und deinen Versuch relevant sind.

<a id="sec-a"></a>
### Anhang A: Parallele WSJT-X-Instanzen

Mit diesem Verfahren wird unter Windows eine zweite isolierte WSJT-X-Instanz eingerichtet, beispielsweise für einen simultanen RX- oder TX-Hardware-A/B-Test. Das aktuelle WSJT-X-Handbuch nennt `--rig-name` als unterstützten Weg, die Einstellungen und beschreibbaren Dateien jeder Instanz zu trennen. Da sich WSJT-X-Versionen und Installationspfade ändern können, sollte bei abweichenden Menüs das aktuelle Handbuch geprüft werden. <a href="#ref-12">[Ref-12]</a>

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
#### A.4 Unterscheidbares simultanes TX konfigurieren

Für simultanes TX Hardware A/B ist die Trennung der Einstellungen nur die softwareseitige Grundlage. Prüfe den vollständigen Aufbau mit zwei Sendern vor dem Senden an geeigneten Abschlüssen oder über einen sicher ausgelegten Testpfad mit geringer Leistung:

1. Weise einer Instanz das exakte Target-Rufzeichen und Target-QTH und der anderen das davon verschiedene exakte Referenz-Rufzeichen zu. Konfiguriere die Referenzinstanz für Meldungen vom selben Test-QTH; WSPRadar zeigt deaktivierte Target- und Referenz-Locator-Felder an, die beide aus den ersten vier Zeichen des Target-QTHs abgeleitet werden, und ordnet beide hochgeladenen Identitäten diesem gemeinsamen Grid-4 zu.
2. Führe jede Instanz zum vorgesehenen Funkgerät, zur richtigen Steuerschnittstelle und zum richtigen Audioausgang. Eine kopierte Konfiguration darf nicht den falschen Sender tasten oder ansteuern.
3. Verwende bei Bedarf auf beiden Funkgeräten die normale WSPR-Abstimmfrequenz, aber getrennte Audio-Sendeversätze wie `1450 Hz` und `1550 Hz`. Prüfe den Wasserfall und wähle freie, nicht überlappende Positionen, statt anzunehmen, dass diese Beispielwerte unbelegt sind.
4. Konfiguriere bewusst gleichzeitige Starts im selben Zyklus. Unabhängige Zufallseinstellungen für `Tx Pct` definieren keinen synchronisierten Vergleichszeitplan.
5. Prüfe vor dem Sammeln von Evidenz für beide Pfade Frequenz, tatsächliche HF-Leistung, spektrale Reinheit, Uhrensynchronisation und hochgeladene Angaben zu Rufzeichen, QTH und Leistung.
6. Stelle ausreichende Isolation zwischen den aktiven Sendern und Antennen sicher. Eingekoppelte Leistung kann Geräte desensibilisieren oder beschädigen sowie Intermodulation oder irreführende Spots erzeugen; verwende eine für die Station geeignete Filterung, räumliche Trennung, Leistung und HF-technische Auslegung.

Ist ein kleiner beobachteter Unterschied entscheidend, wiederhole den Versuch mit vertauschten Audiofrequenz-Zuordnungen und führe nach Möglichkeit einen Hardware-Kreuztausch durch. Bewahre beide Läufe getrennt auf; führe sie erst zusammen, wenn Rollen, Korrektur und Analyseumfang übereinstimmen.

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

Dieses Verfahren ermittelt einen stabilen additiven Offset zwischen Empfangsketten oder Pfaden auf der Referenzseite.

1. **Gemeinsames Eingangssignal:** Beide Empfangsketten über einen geeigneten Verteiler und charakterisierte Kabel aus einer stabilen Antenne speisen.
2. **Verteiler charakterisieren:** Pegelunterschiede zwischen den Ausgängen und Kabeldifferenzen berücksichtigen; wenn praktikabel, die Ausgänge in einem Kontrolllauf vertauschen.
3. **Gepaarte Evidenz sammeln:** Beide Ketten gleichzeitig über den vorgesehenen Signalpegelbereich betreiben, ohne Verstärkung oder Decoder-Einstellungen zu verändern.
4. **Offset ableiten:** Gepaarte Delta-SNR-Evidenz verwenden und angeben, ob der berichtete Wert stationsgleichgewichtet oder aus den Rohpaaren berechnet ist.
5. **Konsistenz prüfen:** Nach Station, Zeit und SNR untersuchen. Ein konstanter Wert ist nicht vertretbar, wenn sich der Offset mit Pegel, Frequenz, AGC oder Zeit ändert.
6. **Vorzeichen anwenden:** Den beobachteten Offset `target - reference` mit demselben Vorzeichen eingeben.
7. **Validieren:** Messung wiederholen oder Pfade tauschen und prüfen, ob das korrigierte Delta des gemeinsamen Eingangssignals plausibel nahe null liegt.

Konsistenz über Stations-, Zeit- und SNR-Ansichten stützt die Verwendung eines additiven Offsets innerhalb des geprüften Aufbaus; sie weist keine rückführbare Laborgenauigkeit nach. Verteilerverlust, Fehlanpassung, Kopplung und Instabilität der Quelle können bestehen bleiben.

<a id="sec-license"></a>
### Lizenz

WSPRadar ist unter der GNU Affero General Public License Version 3 (AGPLv3) lizenziert. Maßgeblich ist die Datei `LICENSE` im Repository.

"""
