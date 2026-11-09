
---

<a id="sec-1"></a>
<a id="part-0"></a>

## Teil 0: Warum WSPRadar

Du veränderst eine Antenne, eine Speiseleitung, einen Empfänger oder eine Stationseinstellung. **Hat es geholfen — und wo, wann und um wie viel?** Ein Empfangsbericht mit höherem SNR oder ein zusätzlicher WSPR-Spot ist eine nützliche Beobachtung. Doch auch die Ausbreitung, die Aktivität der Gegenstationen und der lokale Rauschpegel können sich verändert haben.

WSPRadar hilft dir, dieser Frage über viele Funkstrecken nachzugehen. Es analysiert WSPR-Empfangsberichte und zeigt, wo Signale empfangen werden, wie sie sich unterscheiden und wie regelmäßig sie im Zeitverlauf dekodiert werden. Ein Muster auf der Karte kannst du bis zu den beteiligten Stationen und einzelnen Empfangsberichten zurückverfolgen.

Wiederholte oder gleichzeitige Vergleiche bieten eine stärkere Grundlage als nicht zusammengehörige Empfangsberichte, die Stunden auseinanderliegen. Veröffentlichte WSPR-Versuche zeigen den Wert vergleichbarer Betriebsbedingungen <a href="#ref-1">[Ref-1]</a> <a href="#ref-2">[Ref-2]</a> <a href="#ref-3">[Ref-3]</a> <a href="#ref-4">[Ref-4]</a> <a href="#ref-5">[Ref-5]</a>.

**WSPRadar beschreibt vollständige Stationen und dokumentierte Signalwege unter realen Betriebsbedingungen.** Es misst weder Antennengewinn noch Wirkungsgrad oder Empfängerempfindlichkeit direkt. Um einen Unterschied einem einzelnen Bauteil zuzuordnen, musst du die übrigen Unterschiede kontrollieren und den Vergleich wiederholen.

<a id="sec-1-1"></a>

### 0.1 WSPR in 2 Minuten

<strong class="defined-term">WSPR</strong> steht für **Weak Signal Propagation Reporter**. Stationen senden mit geringer Leistung zeitlich festgelegte digitale Signale, die andere Stationen dekodieren und melden. Ein <strong class="defined-term">WSPR-Zyklus</strong> ist ein zweiminütiges Intervall, das zu einer geraden UTC-Minute beginnt <a href="#ref-6">[Ref-6]</a> <a href="#ref-8">[Ref-8]</a>.

Ein <strong class="defined-term">Spot</strong> ist ein hochgeladener Empfangsbericht über eine erfolgreiche Dekodierung. Er enthält Rufzeichen und Standorte von Sender und Empfänger, Zeitpunkt, Band, gemeldete Sendeleistung und <strong class="defined-term">SNR</strong> — den Signal-Rausch-Abstand in dB. Ein höheres SNR bedeutet ein stärkeres Signal im Verhältnis zum Rauschen; ein negativer Wert bedeutet nicht, dass die Dekodierung fehlgeschlagen ist.

**WSPRadar analysiert hochgeladene Empfangsberichte; es empfängt und dekodiert selbst keine Funksignale.** WSPRnet zeigt Empfangsberichte an. WSPRadar liest normalerweise **wspr.live**, mit **WSPRDaemon WD2** und **WD1** als Alternativen; jeder Analyselauf verwendet eine einzige Datenbank, ohne Quellen zu kombinieren. Siehe [Datenverfügbarkeit und Quellenauswahl](#sec-6-6) <a href="#ref-10">[Ref-10]</a> <a href="#ref-11">[Ref-11]</a>.

Empfangsberichte zeigen erfolgreiche Dekodierungen, nicht jeden Sendeversuch oder jeden zuhörenden Empfänger. **Ein fehlender Spot allein beweist keinen fehlgeschlagenen Empfang.** Wie WSPRadar mit dieser Unsicherheit umgeht, hängt von der gewählten Analyse ab.

<a id="sec-1-0"></a>
<a id="sec-1-2"></a>

### 0.2 Was WSPRadar zeigen kann

Das <strong class="defined-term">Target</strong> ist die untersuchte Station beziehungsweise der untersuchte Signalweg. Eine <strong class="defined-term">Gegenstation</strong> ist bei RX ein entfernter Sender, bei TX ein entfernter Empfänger. Ihre Funkstrecke zum Target trägt zur Analyse bei.

<strong class="defined-term">Performance</strong> untersucht das Target für sich. <strong class="defined-term">Benchmark</strong> vergleicht es mit einer <strong class="defined-term">Referenz</strong> — einem anderen kontrollierten Signalweg oder einer bekannten Station.

| Deine Fragestellung | Wähle | Was untersucht wird |
|---|---|---|
| Was kann diese Station empfangen, und wie regelmäßig? | <strong class="defined-term">RX Performance</strong> | Welche Sender das Target hört und wie regelmäßig. Nicht dekodierte Aussendungen zählen mit, wenn die nötige Aktivität der Stationen durch Empfangsberichte belegt ist. |
| Wo wird diese Station gehört, und wie regelmäßig? | <strong class="defined-term">TX Performance</strong> | Welche Empfänger das Target hören und wie regelmäßig. Nicht dekodierte Aussendungen zählen mit, wenn die nötige Aktivität der Stationen durch Empfangsberichte belegt ist. |
| Wie unterscheiden sich zwei Empfangsaufbauten? | <strong class="defined-term">RX Benchmark</strong> | Target und Referenz empfangen dieselben entfernten Sender in denselben WSPR-Zyklen. |
| Wie unterscheiden sich zwei Sendeaufbauten? | <strong class="defined-term">TX Benchmark</strong> | Dieselben entfernten Empfänger hören Target und Referenz in denselben WSPR-Zyklen. |

Mit Performance kannst du einen Ausgangszustand der Station erfassen oder geografische und zeitliche Muster untersuchen. Benchmark eignet sich zum Vergleich von Antennen, Speiseleitungen, Empfängern, Filtern, Vorverstärkern oder vollständigen Aufbauten. Eine unabhängige Referenz vergleicht vollständige installierte Stationen einschließlich ihrer Standorte und Rauschumgebungen; sie ist nicht automatisch ein kalibrierter Standard.

<a id="sec-1-3"></a>

### 0.3 Was ein Analyselauf liefert

Ein <strong class="defined-term">Analyselauf</strong> wertet Empfangsberichte für die gewählte Analyse, das Band, den UTC-Zeitraum und deine Einstellungen aus. Er liefert Karten, Zusammenfassungen nach Entfernung und Zeit, Stationstabellen und einzelne Beobachtungen, die du prüfen kannst.

Der physische <strong class="defined-term">Versuch</strong> umfasst den Aufbau und den Funkbetrieb, aus denen diese Empfangsberichte entstanden sind. Wenn du die Darstellung eines abgeschlossenen Analyselaufs änderst, entsteht dadurch kein neuer Versuch.

Prüfe anhand der Ergebnisse, ob ein Muster breit auftritt oder auf wenige Stationen begrenzt ist, ob es über die Zeit bestehen bleibt und wie umfangreich die Datengrundlage dafür ist. Ergebnisse und Einstellungen lassen sich zur späteren Prüfung herunterladen; deine eigenen Aufbaunotizen vervollständigen die Dokumentation.

<a id="sec-1-4"></a>

### 0.4 Dein erster sinnvoller Analyselauf

Beginne mit **Demo laden**. Wähle eines der gepflegten Beispiele, lies seine Versuchsnotizen und behalte beim ersten Analyselauf die vorbereiteten Einstellungen bei. Beide Eingabeansichten bieten zwei Wege:

- **Laden und Einstellungen schrittweise prüfen** behält deine gewählte Eingabeansicht bei. **Geführt** führt schrittweise durch die Einstellungen; **Kompakt** öffnet den vollständigen Editor beim ersten Einstellungsbereich.
- **Laden und vor dem Start prüfen** öffnet direkt die Prüfung in deiner gewählten Ansicht **Geführt** oder **Kompakt**. Dorthin führen auch Demolinks von der Website und geteilte Demo-URLs. Eine neue Sitzung beginnt standardmäßig mit **Geführt**.

Das Laden allein startet noch keine Analyse. Prüfe die Einstellungen und wähle dann je nach Analyserichtung **RX-Analyse starten** oder **TX-Analyse starten**.

Verfolge ein Merkmal von der Karte bis zu den Stationen und Empfangsberichten dahinter. Unter **So liest du die Ergebnisse** findest du die Erklärung von Kennzahl, Legende und Interpretation. Eine Demo vermittelt die Methode; sie beschreibt nicht deine Station. Bereite anschließend mit [Kapitel 1](#sec-2) deinen eigenen Analyselauf vor.

<a id="documentation-toc"></a>

### Inhaltsverzeichnis

**[Teil 0: Warum WSPRadar](#part-0)**

* [0.1 WSPR in 2 Minuten](#sec-1-1)
* [0.2 Was WSPRadar zeigen kann](#sec-1-0)
* [0.3 Was ein Analyselauf liefert](#sec-1-3)
* [0.4 Dein erster sinnvoller Analyselauf](#sec-1-4)

**Teil I: Leitfaden für den Funkbetrieb**

* [1. Analyse auswählen und vorbereiten](#sec-2)
    * [1.1 Station und Empfangsberichte vorbereiten](#sec-2-1)
    * [1.2 Analyse konfigurieren](#sec-2-2)
    * [1.3 Die Ergebnisse erkunden](#sec-2-3-overview)
* [2. Analyse durchführen und auswerten](#sec-3)
    * [2.1 RX Benchmark](#sec-3-rx-benchmark)
        * [2.1.1 Referenzaufbau oder Referenzstation](#sec-3-rx-benchmark-hardware)
    * [2.2 TX Benchmark](#sec-3-tx-benchmark)
        * [2.2.1 Referenzaufbau oder Referenzstation](#sec-3-tx-benchmark-simultaneous)
    * [2.3 RX Performance](#sec-3-rx-performance)
    * [2.4 TX Performance](#sec-3-tx-performance)
    * [2.5 Vorübergehende ΔSNR-Abweichungen finden und prüfen](#sec-outlier)
        * [2.5.1 Wann diese Expertendiagnose sinnvoll ist](#sec-outlier-1)
        * [2.5.2 Wie die Erkennung praktisch arbeitet](#sec-outlier-2)
        * [2.5.3 Ein gemeldetes Ereignis lesen und untersuchen](#sec-outlier-4)
        * [2.5.4 Selektivität anpassen und Ergebnis sichern](#sec-outlier-7)
* [3. Ergebnis absichern und kommunizieren](#sec-4)
    * [3.1 Breite, Übereinstimmung und Wiederholbarkeit beurteilen](#sec-4-1)
    * [3.2 Ergebnis durch Wiederholung und Kontrolle absichern](#sec-4-2)
    * [3.3 Eine der Datengrundlage angemessene Schlussfolgerung formulieren](#sec-4-3)
    * [3.4 Analyselauf und Kontext sichern](#sec-4-4)


**Teil II: Praktische Anleitung zum Stationsaufbau**

* [4. Parallele WSJT-X-Instanzen für simultanen Empfang](#sec-a)
    * [4.1 Target- und Referenzinstanz anlegen](#sec-a-1)
    * [4.2 Ausgangskonfiguration bei Bedarf kopieren](#sec-a-2)
    * [4.3 Alle Datenpfade trennen](#sec-a-3)
    * [4.4 Grenzen von WSJT-X für simultanes Senden](#sec-a-4)
* [5. Referenzaufbau für simultanes Senden](#sec-simultaneous-tx-setup)
    * [5.1 Rufzeichen auswählen](#sec-simultaneous-tx-setup-1)
        * [5.1.1 Zwei verschiedene Rufzeichen](#sec-tx-two-distinct-callsigns)
        * [5.1.2 Ein Rufzeichen mit zwei Suffixen](#sec-tx-one-callsign-two-suffixes)
    * [5.2 Zeitplan abgleichen und Signale trennen](#sec-simultaneous-tx-setup-2)
    * [5.3 Leistung und Signalqualität im simultanen Betrieb prüfen](#sec-simultaneous-tx-setup-3)
    * [5.4 WSPRnet und die ausgewählte Datenbank prüfen](#sec-simultaneous-tx-setup-4)
    * [5.5 Gerätespezifische Einrichtung](#sec-simultaneous-tx-setup-5)
        * [5.5.1 QMX und QMX+ Virtual U3S sowie Ultimate3S](#sec-simultaneous-tx-setup-5-1)
            * [5.5.1.1 Zwei verschiedene Rufzeichen](#sec-qrp-two-distinct-callsigns)
            * [5.5.1.2 Ein Rufzeichen mit zwei Suffixen](#sec-qrp-one-callsign-two-suffixes)
            * [5.5.1.3 Gemeinsame Schritte für Leistung, Frequenz und Prüfung](#sec-qrp-common-setup)
        * [5.5.2 ZachTek-Firmware 2.19](#sec-simultaneous-tx-setup-5-3)
            * [5.5.2.1 Zwei verschiedene Rufzeichen](#sec-zachtek-two-ordinary-callsigns)
            * [5.5.2.2 Ein Rufzeichen mit zwei Suffixen](#sec-simultaneous-tx-setup-5-3-2)
            * [5.5.2.3 Gemeinsame Zeitsteuerung, zufällige Frequenzwahl und Prüfung](#sec-simultaneous-tx-setup-5-3-1)
    * [5.6 Durch Tausch oder Kreuztausch bestätigen](#sec-simultaneous-tx-setup-6)
* [6. Kalibrierung des Referenz-SNR](#sec-reference-snr-calibration)

**Teil III: Wissenschaftliche Grundlagen, Methoden und Aussagen**

* [7. Literatur, Vorarbeiten und Einordnung](#sec-d)
    * [7.1 Vom Meldenetz zum Versuchsdatensatz](#sec-d-1)
        * [7.1.1 Joe Taylor, K1JT, und Bruce Walker, W1BW: eine gemeinsame Ressource für Experimente.](#sec-d-taylor-walker)
        * [7.1.2 Nathaniel Frissell und Mitautoren: Amateurfunkbeobachtungen in der Weltraumforschung.](#sec-d-frissell)
    * [7.2 WSPR-Beobachtungsdaten interpretierbar machen](#sec-d-2)
        * [7.2.1 Lo und Mitautoren, 2022: vor der Interpretation ausbleibender Empfangsberichte die Aktivität belegen.](#sec-d-lo)
        * [7.2.2 Gwyn Griffiths, G3ZIL, Rob Robinett, AI6VN, und Glenn Elmore, N6GN, 2019–2020: den Rauschpegel parallel zum Empfang messen.](#sec-d-griffiths-robinett-elmore)
    * [7.3 Entwicklungslinie von Antennen- und Stationsvergleichen](#sec-d-3)
        * [7.3.1 Patrick Destrem, F6IRF, 2008: automatisierte Umschaltung und geografischer Vergleich.](#sec-d-destrem)
        * [7.3.2 Charles Preston, KL7OA, später K7TAA, 2009 und 2017: simultaner Vergleich.](#sec-d-preston)
        * [7.3.3 Sivan Toledo, 2010: ein nützliches negatives Ergebnis zur zeitlichen Versuchsplanung.](#sec-d-toledo)
        * [7.3.4 Carol F. Milazzo, KP4MD, 2011: vollständige Stationen in beiden Richtungen vergleichen.](#sec-d-milazzo)
        * [7.3.5 Gwyn Griffiths, G3ZIL, und Nigel Squibb, G4HZX, 2017: vergleichen, untersuchen und erneut prüfen.](#sec-d-griffiths-squibb)
        * [7.3.6 Vanhamel, Machiels und Lamy, 2022: die Empfangszweige charakterisieren.](#sec-d-vanhamel)
        * [7.3.7 Jens Zander, 2022: Vergleichsmodell und Annahmen angeben.](#sec-d-zander)
        * [7.3.8 Thomas Rietdorf, DL2OAH, 2026: ein synchronisierter Stationsvergleich auf mehreren Bändern.](#sec-d-rietdorf)
        * [7.3.9 Dale Ostergaard, N3HXZ, 2026: praktische sequenzielle Antennenvergleiche.](#sec-d-ostergaard)
    * [7.4 Analyseinfrastruktur und verwandte Werkzeuge](#sec-d-4)
        * [7.4.1 Gwyn Griffiths und Rob Robinett, 2020: wiederverwendbare Datenbankanalyse.](#sec-d-griffiths-robinett)
        * [7.4.2 Arne und das Projekt wspr.live, mit Rechenressourcen von HB9VQQ.](#sec-d-wspr-live)
        * [7.4.3 Rob Robinett, AI6VN, und die WSPRdaemon-Gemeinschaft.](#sec-d-wsprdaemon)
        * [7.4.4 Tim, K5OHY — FarField Lab: praxisnahe Antennenvergleiche mit Umschaltung.](#sec-d-farfield-lab)
        * [7.4.5 Phil, VK7JJ — WSPR.Rocks](#sec-d-wspr-rocks)
        * [7.4.6 Richard Newstead und SOTABEAMS — WSPRlite/DXplorer](#sec-d-wsprlite-dxplorer)
        * [7.4.7 Walter Machiels, ON4AWM — WSPR-Station-Compare](#sec-d-wspr-station-compare)
        * [7.4.8 Fred, W6BSD — Antenna Performance Analysis](#sec-d-antenna-performance-analysis)
        * [7.4.9 Colin Murray, GM4EAU — WATT](#sec-d-watt)
    * [7.5 Was WSPRadar übernimmt, integriert und ergänzt](#sec-d-5)
* [8. Wissenschaftliche Methoden](#sec-7)
    * [8.1 Gemeinsame Grundlagen der Datenauswertung](#sec-7-foundations)
        * [8.1.1 Spots, Identitäten und Zyklen](#sec-7-spots-identities-cycles)
        * [8.1.2 Leistungsnormierung und Zusammenfassung](#sec-7-normalization-consolidation)
        * [8.1.3 Betriebsbedingungen und Zulässigkeit](#sec-7-activity-eligibility)
    * [8.2 Benchmark: Unterschiede und gemeinsame Datengrundlage](#sec-7-benchmark)
        * [8.2.1 Dekodierergebnisse und fehlende Beobachtungen](#sec-7-benchmark-outcomes)
        * [8.2.2 Delta SNR und Referenzkorrektur](#sec-7-benchmark-delta)
        * [8.2.3 Aggregation nach Station und Karte](#sec-7-benchmark-aggregation)
        * [8.2.4 Zeitliche Dekodierabdeckung](#sec-7-benchmark-coverage)
        * [8.2.5 Kontrollierter Betrieb und eingestellte Designs](#sec-7-neighborhood)
    * [8.3 Performance: Empfangsgelegenheiten und Dekodiererfolg](#sec-7-performance)
        * [8.3.1 Was zählt als Empfangsgelegenheit?](#sec-7-performance-opportunities)
        * [8.3.2 Dekodierquoten und Gewichtung](#sec-7-performance-rates)
        * [8.3.3 Mindestens einmal erfasste Gegenstationen](#sec-7-performance-reach)
        * [8.3.4 Target-SNR erfolgreicher Dekodierungen](#sec-7-performance-snr)
    * [8.4 Bereich und Zusammenfassungen über Raum und Zeit](#sec-7-views)
        * [8.4.1 Bereich, Geografie und Filter](#sec-7-view-scope)
        * [8.4.2 Geografische Zusammenfassungen](#sec-7-view-geography)
        * [8.4.3 Chronologische Beobachtungsdaten](#sec-7-view-time)
        * [8.4.4 Tage nach UTC oder wahrer Ortszeit zusammenfassen](#sec-7-view-folding)
        * [8.4.5 Beobachtungsdaten einer ausgewählten Station](#sec-7-view-station)
        * [8.4.6 Streuung und Darstellungsskalen](#sec-7-view-spread)
    * [8.5 Wie weit trägt die Schlussfolgerung?](#sec-7-claims)
        * [8.5.1 Abhängigkeit und Verzerrung](#sec-7-dependence-bias)
        * [8.5.2 Wiederholbarkeit und experimentelle Kontrolle](#sec-7-repeatability-control)
        * [8.5.3 Umfang der Validierung](#sec-7-validation)
    * [8.6 Experimentelle Analyse von ΔSNR-Ereignissen](#sec-7-outliers)
        * [8.6.1 Abweichung vom lokalen Vergleichsniveau](#sec-7-outlier-departure)
        * [8.6.2 Vergleichsniveau und benachbarte Schwankungen](#sec-7-outlier-baseline)
        * [8.6.3 Qualifikation eines Kandidaten](#sec-7-outlier-qualification)
        * [8.6.4 Grenzen und Ereignisklassen](#sec-7-outlier-boundaries)
        * [8.6.5 Kontext und Grenzen](#sec-7-outlier-context)
* [9. Durch die Datengrundlage getragene Aussagen und Reproduzierbarkeit](#sec-8)
    * [9.1 Aussageklassen und passende Formulierungen](#sec-8-1)
    * [9.2 Interpretationsgrenzen](#sec-8-2)
    * [9.3 Checkliste für Berichterstattung und Reproduzierbarkeit](#sec-8-3)
    * [9.4 Exportpaket der Analyse](#sec-8-4)

**Teil IV: Bedienelemente und Fehlersuche**

* [10. Bedienelemente und Konfiguration](#sec-5)
    * [10.1 Bedienelemente für den Ablauf](#sec-5-1)
    * [10.2 Fragestellung, Target und Messzeitraum](#sec-5-2)
    * [10.3 Einstellungen für den Benchmark-Vergleich](#sec-5-3)
    * [10.4 Filter und Anforderungen an die Datengrundlage](#sec-5-4)
    * [10.5 Bedienelemente für Karte, Segmentdetails und Export](#sec-5-5)
    * [10.6 Bedienelemente für die Ausreißererkennung in Benchmark](#sec-5-6)
* [11. Fehlersuche und Datenqualität](#sec-6)
    * [11.1 Zuerst die Definition des Analyselaufs prüfen](#sec-6-1)
    * [11.2 Diagnose anhand des Symptoms](#sec-6-2)
    * [11.3 Rufzeichen und Locator prüfen](#sec-6-3)
    * [11.4 Ersatzabfrage für historische Dekodiercodes](#sec-6-4)
    * [11.5 Betriebsbedingungen und Aktivitätsbelege](#sec-6-5)
    * [11.6 Mit Daten aus den Quellen arbeiten](#sec-6-6)

**Teil V: Literatur und Quellen**

* [Teil V: Literatur und Quellen](#sec-ref)

**Experimentelle Nutzung & Haftungsausschluss**

---

<a id="part-i"></a>

## Teil I: Leitfaden für den Funkbetrieb

[Kapitel 1](#sec-2) hilft dir, die Analyse vorzubereiten. [Kapitel 2](#sec-3) erklärt die Ergebnisse der vier Analysearten; [Kapitel 3](#sec-4) zeigt, wie du eine Schlussfolgerung prüfst und dokumentierst. Ausführliche Diagrammerklärungen findest du unter **So liest du die Ergebnisse** neben dem jeweiligen Ergebnis, Bedienelemente und Fehlersuche in [Teil IV](#part-ii), Berechnungen und wissenschaftliche Grenzen in [Teil III](#part-iii).

---

<a id="sec-2"></a>

### 1. Analyse auswählen und vorbereiten

Beginne mit einer Frage zu deiner Station. Halte fest, was du verändert hast oder untersuchen möchtest und welche Beobachtung bei der Antwort helfen würde.

<a id="sec-2-1"></a>

#### 1.1 Station und Empfangsberichte vorbereiten

1. **Verwertbare Empfangsberichte erzeugen.** Richte für RX einen WSPR-fähigen Empfänger und Decoder wie WSJT-X mit korrektem Empfangsrufzeichen, Locator, Band, Audioeingang und synchronisierter Uhr ein. Aktiviere die Uploads: Eine lokale Dekodierung, die nie hochgeladen wurde, steht WSPRadar nicht zur Verfügung. Konfiguriere für TX Rufzeichen, Locator, Band, Zeitsteuerung und eine zutreffende Angabe der Sendeleistung; die Gegenstationen auf der Empfangsseite liefern die Spots. Die [WSJT-X-Referenz](#ref-12) beschreibt die grundlegende Einrichtung.
2. **Rufzeichen und Locator in der Datenbank prüfen.** Prüfe RX-Melderufzeichen beziehungsweise TX-Rufzeichen, gemeldeten Locator und UTC-Zeiten zuerst in WSPRnet und dann in der von WSPRadar verwendeten Datenbank. Übernimm das Rufzeichen genau wie erfasst, einschließlich vorhandener Zusätze. Wähle einen abgeschlossenen Zeitraum und warte ab, bis die Empfangsberichte eintreffen; eine feste Wartezeit garantiert keine Vollständigkeit. Siehe [Fehlersuche bei Datenproblemen](#sec-6-6).
3. **Den Aufbau nachvollziehbar halten.** Dokumentiere Antenne, Speiseleitung, Funkgerät, Decoder, Verstärkungs- oder Leistungseinstellungen, Software, Zeitplan und bewusste Änderungen. Halte die übrigen Variablen stabil und die Uhren synchron. Bereite bei Benchmark beide Aufbauten anhand der [RX-Hinweise](#sec-3-rx-benchmark-hardware) beziehungsweise [TX-Hinweise](#sec-3-tx-benchmark-simultaneous) vor, bevor du die Vergleichsdaten sammelst.

<a id="sec-2-2"></a>

#### 1.2 Analyse konfigurieren

Wähle die Analyse anhand von [Abschnitt 0.2](#sec-1-0). <strong class="defined-term">Geführt</strong> leitet dich durch die Einstellungen; <strong class="defined-term">Kompakt</strong> bietet dieselben Analyseeinstellungen in kürzerer Form.

Gib das exakte **Target-Rufzeichen**, ein **Band** und einen abgeschlossenen **Messzeitraum (UTC)** ein. Gib unter **Target-Locator (optional)** einen Maidenhead-Locator mit vier oder sechs Zeichen ein oder lass das Feld leer, um den Standort nach **Analyse starten** zu ermitteln. Ein einzelner gemeldeter Locator wird automatisch gewählt; bei mehreren wählst du selbst. Dabei bleiben alle vier oder sechs Zeichen erhalten. Die ersten vier Zeichen wählen die Empfangsberichte aus, während der vollständig eingegebene oder ermittelte Locator den Bezugspunkt für Karte, Entfernungen und Richtungen festlegt. Längere Zeitfenster liefern mehr Beobachtungsdaten, können aber unterschiedliche Betriebs- und Ausbreitungsbedingungen vermischen.

<a id="sec-2-5"></a>

**Bei Benchmark** übernimmst du das Referenz-Rufzeichen genau wie gemeldet; es muss sich vom Target unterscheiden. Lass **Referenz-Locator (optional)** leer, um den Standort nach **Analyse starten** aus Berichten zu ermitteln, oder gib den unabhängig bekannten vierstelligen Locator ein. Werden mehrere Standorte gefunden, wähle einen. Ein Standort allein belegt weder den Betrieb noch einen gemeinsamen physischen Aufstellungsort.

Bestätige die Betriebsbedingungen anhand unabhängiger Informationen:

- **RX Benchmark:** Beide Empfänger haben während des gesamten Zeitraums auf dem gewählten Band empfangen, und ihre Uploads waren funktionsfähig. Dafür ist keine Dekodierung in jedem Zyklus erforderlich.
- **TX Benchmark:** Beide Sender haben in denselben WSPR-Zyklen gesendet, mit aufeinander abgestimmten Zeitplänen und Nachrichtenfolgen.

Bewahre die zugehörigen Betriebsaufzeichnungen auf. Erfolgreiche Empfangsberichte allein belegen keinen durchgehenden Betrieb. Setze vor dem Start eines Benchmarks in der Prüfung unter **ANALYSE STARTEN** das Häkchen bei **Ich habe den gemeinsamen Betrieb bestätigt oder akzeptiere die Einschränkungen, wenn er nicht verifiziert ist.** Das gilt auch für das gepflegte Milazzo-Beispiel und andere historische Empfangsberichte ohne unabhängig verifizierten gemeinsamen Betrieb. Die Bestätigung hält nicht fest, welche Alternative zutrifft, und ist selbst kein Betriebsnachweis; siehe [Abschnitt 10.3](#sec-5-3).

Belasse die **SNR-Korrektur der Referenz (dB)** bei **Keine Korrektur (0,0 dB)**, sofern dir kein unabhängig bestimmter, für diesen Aufbau gültiger Versatz vorliegt. Siehe [Kalibrierungshinweise](#sec-reference-snr-calibration).

Prüfe beim ersten Analyselauf die angezeigten Filter und Mindestanforderungen an die Datengrundlage, ohne die Schwellen nur deshalb zu senken, um mehr farbige Kartenbereiche zu erhalten. **Maximale Entfernung der Gegenstationen vom Target (km)** verändert, welche Gegenstationen in die Analyse eingehen, nicht nur den Kartenausschnitt; wähle den Wert passend zu deiner Fragestellung. Siehe [Einstellungen für Auswertungsbereich und Datengrundlage](#sec-5-4). Prüfe die abschließende Zusammenfassung und wähle dann **RX-Analyse starten** oder **TX-Analyse starten**. Die genauen Bedienelemente stehen in [Kapitel 10](#sec-5); unerwartete Lücken behandelt [Kapitel 11](#sec-6).

<a id="sec-2-3-overview"></a>

#### 1.3 Die Ergebnisse erkunden

Verfolge ein Muster durch die Ergebnisse. Öffne **So liest du die Ergebnisse** neben einer Ansicht, wenn du ihre Legende, Zählweise oder Interpretation nachlesen möchtest.

Bei Performance fasst **Auf einen Blick** oberhalb der **Gesamtübersicht** die gesamte abgeschlossene Analyse zusammen: Dekodierhäufigkeit, Anteil der Stationen mit mindestens einem erfolgreichen Empfang, mittlere Dekodierquote der Stationen und Entfernungen der dekodierten Signale. [Abschnitt 8.4.2](#sec-7-view-geography) erklärt, welche Stationen einbezogen und wie Quoten und Entfernungen gewichtet werden.

<a id="sec-3-4"></a>
<a id="sec-3-5"></a>

**1.** <strong class="defined-term">Gesamtübersicht</strong> **— wo liegt das Muster?** Ein <strong class="defined-term">Kartensegment</strong> umfasst Richtungen und Entfernungen vom Target aus. Lies Zahlenskala und zugrunde liegende Anzahlen. Graue diagonale Schraffur (**Not qualifying**, Anforderungen nicht erfüllt) bedeutet: Beobachtungen liegen vor, aber die Einfärbungsanforderungen sind nicht erfüllt. Ein ungefülltes Segment (**No observations**, keine berücksichtigten Beobachtungen) enthält keine für diese Karte verbleibenden Beobachtungen. Performance verwendet Stationen, die seine Stationsanforderungen erfüllen; Benchmark alle beobachteten Stationen im gewählten Bereich nach den Filtern. Ein Nullwert bleibt bei erfüllten Anforderungen farbig. Schraffur und ungefüllte Bereiche bedeuten keine gemessene Dekodierquote von null.

<a id="sec-3-6"></a>
<a id="sec-3-6a"></a>
<a id="sec-3-6b"></a>

**2.** <strong class="defined-term">Segmentdetails</strong> **— wie breit und wie beständig ist das Muster?** Wähle Richtungen und Entfernungen. Dieser <strong class="defined-term">aktive Auswertungsbereich</strong> bestimmt die Stationen und Beobachtungen in Dekodierungen und Stationen, den Gesamtanzahlen, Segmentstatistiken und Zeitdiagrammen. Dekodierungen und Stationen folgt der Zusammenfassung der aktuellen Auswahl; die Anzahlkarten stehen vor der Benchmark-Statistik. Vergleiche Stations- und Beobachtungszahlen. Prüfe einzelne Tage, bevor du ein zusammengefasstes Tageszeitmuster als wiederkehrend bezeichnest. Vergleiche in der <strong class="defined-term">Benchmark-Statistik</strong> die ΔSNR-Verteilungen der Spot-Paare, Stationsmittelwerte und Stationsmediane. Häufig beobachtete Stationen liefern mehr Spot-Paare; zu den Stationsverteilungen trägt jede berücksichtigte Station genau einen Mittelwert oder Median bei.

<a id="sec-3-7"></a>
<a id="sec-3-7a"></a>
<a id="sec-3-7b"></a>

**3.** <strong class="defined-term">Stationsauswertung</strong> → <strong class="defined-term">Datengrundlage der ausgewählten Station</strong> **— welche Stationen erklären das Muster?** Wähle eine typische Station, eine ungewöhnliche oder eine mit vielen Berichten. Performance und Benchmark listen standardmäßig die gesamte abgeschlossene Analyse auf. **Nach ausgewähltem Segment und Entfernung filtern** schränkt die Liste ein; Stationskennzahlen und Diagramme gelten weiterhin für den vollständigen Analyselauf, auch wenn der Filter die ausgewählte Station ausblendet. Der Listenfilter gilt nur für die Sitzung. Mit **Einseitige Beobachtungen einbeziehen** zeigt Benchmark auch Stationen ohne Spot-Paare und einseitige Beobachtungen in den Detaildaten.

<a id="sec-3-8"></a>

**4.** <strong class="defined-term">Detaildaten</strong> **— was geschah in den einzelnen Zyklen?** Prüfe genaue Rufzeichen und Locator, UTC-Zeiten, SNR und Dekodierergebnisse. Grenze das Zeitfenster ein, um einen Zeitraum genauer zu untersuchen. Diese Beobachtungen sind bereits zugeordnet und gefiltert; sie entsprechen keinem unveränderten Datenbankdownload.

**Die statistischen Zusammenfassungen lesen.** In den Diagrammen begegnen dir folgende Begriffe:

| Begriff | Bedeutung |
|---|---|
| <strong class="defined-term">Arithmetischer Mittelwert</strong> | Summe der Werte geteilt durch ihre Anzahl. In kurzen Bedienelementen heißt er **Mittelwert**, in den englischen Abbildungen **Mean**. |
| <strong class="defined-term">Median</strong> | Der mittlere Wert nach dem Sortieren; bei gerader Anzahl der Mittelwert der beiden mittleren Werte. Mittelwert und Median fassen dieselben Beobachtungen zusammen, reagieren aber unterschiedlich auf extreme Werte. |
| <strong class="defined-term">Konfidenzintervall (KI)</strong> | Beschreibt die Unsicherheit eines geschätzten Mittelwerts unter dem angegebenen Stichprobenmodell. |
| <strong class="defined-term">Stichprobenstandardabweichung (SD)</strong> | Beschreibt, wie stark die beobachteten Werte streuen. |
| <strong class="defined-term">Standardfehler</strong> | Beschreibt die modellabhängige Unsicherheit des Mittelwerts. Bei unabhängigen Beobachtungen ist er die Stichprobenstandardabweichung geteilt durch die Quadratwurzel der Beobachtungszahl. |
| <strong class="defined-term">Interquartilsabstand (IQR)</strong> | Q3 minus Q1. Das dargestellte Q1–Q3-Intervall umfasst die mittleren 50 % der Werte. Es zeigt ihre Streuung, nicht die Unsicherheit des Mittelwerts. |

Ein <strong class="defined-term">Zeitintervall (Bin)</strong> fasst Beobachtungen in einem dargestellten Zeitabschnitt zusammen. Das <strong class="defined-term">punktweise Konfidenzintervall</strong> mit der Legende <strong class="defined-term">Bin 95% CI</strong> gilt für dessen Mittelwert, nicht gleichzeitig für die gesamte Kurve. Der Prozentsatz folgt dem gewählten Konfidenzniveau. Dieses beschreibt das Verfahren bei wiederholten Stichproben, keine Wahrscheinlichkeit für das einzelne angezeigte Intervall. [Abschnitt 8.5.1](#sec-7-dependence-bias) erklärt Berechnung und Unabhängigkeitsannahmen.

<a id="sec-3"></a>

### 2. Analyse durchführen und auswerten

Lies den Abschnitt für die gewählte Analyse. Die folgenden Grundlagen erklären, was das Ergebnis bedeutet; **So liest du die Ergebnisse** neben jedem Ergebnis erläutert dessen Diagramme und Bedienelemente im Detail.

**Wie Stationen und Beobachtungen gezählt werden.** WSPRadar zählt jede Kombination aus genauem Rufzeichen und vollständigem gemeldetem Locator als eine <strong class="defined-term">Stationsidentität</strong>, im Leitfaden meist kurz Station genannt. Ein Rufzeichen an zwei Locatoren zählt zweimal; dahinter müssen keine unabhängigen physischen Stationen stehen. Mehrere beibehaltene Empfangsberichte für denselben Aufbau, dieselbe Gegenstation und denselben WSPR-Zyklus zählen als eine Beobachtung.

**Benchmark vergleicht Signalqualität und Dekodierung.** Ein <strong class="defined-term">Spot-Paar</strong> verbindet Target- und Referenzberichte zur selben Gegenstation im selben WSPR-Zyklus: bei RX zu einem Sender, bei TX von einem Empfänger. <strong class="defined-term">„Both observed“</strong> bedeutet, dass die Gegenstation im Zeitraum bei beiden Seiten erfasst wurde, möglicherweise in unterschiedlichen Zyklen. Daraus allein ergibt sich kein Spot-Paar.

- <strong class="defined-term">ΔSNR</strong> (Delta SNR) ist das Target-SNR minus dem korrigierten Referenz-SNR eines Spot-Paars. Ein positiver Wert spricht für das Target, ein negativer für die Referenz; **0 dB** bedeutet gleiches SNR. Beispielsweise bedeutet **+3 dB** in diesem Vergleich ein um 3 dB höheres Target-SNR. Ein Signal, das nur auf einer Seite dekodiert wurde, lässt sich damit nicht beschreiben.
- <strong class="defined-term">ΔDecode</strong> vergleicht die Gesamtzahlen beobachteter Dekodierungen einschließlich einseitiger Empfangsberichte. Die Verhältnislegende der Karte lässt sich direkt lesen: **2× auf der Target-Seite** bedeutet die doppelte Dekodierzahl der Referenz; **1×** bedeutet gleiche Gesamtzahlen; <strong class="defined-term">„Exclusive“</strong> bedeutet, dass nur eine Seite Dekodierungen aufweist. Signale, die beide Aufbauten nicht dekodiert haben, bleiben unbekannt; deshalb ist ΔDecode keine Erfolgsquote über alle Aussendungen. Siehe [die genaue Berechnung](#sec-7-benchmark-aggregation).

Die ΔSNR-Karte berechnet den <strong class="defined-term">arithmetischen Mittelwert</strong> der verwendbaren gepaarten ΔSNR-Werte von Stationen mit beibehaltenen Paaren im gefilterten Analyselauf. Jedes Paar zählt gleich viel. Für eine Einfärbung müssen Stationsmindestzahl und Präzisionsanforderung an das Konfidenzintervall über die Paare erfüllt sein. ΔDecode addiert alle beibehaltenen Dekodierungen zu <strong class="defined-term">Gesamtzahlen</strong>. Die beiden Größen können unterschiedliche Aufbauten begünstigen. Auch die zeitlichen ΔSNR-Diagramme von Benchmark fassen verwendbare Paare je Zeitintervall zusammen. Häufig beobachtete Stationen tragen deshalb stärker zu den Dekodierzahlen bei und können mehr Paare zu Karte und Zeitdiagrammen beitragen.

**Performance zählt bestätigte Empfangsgelegenheiten.** Eine <strong class="defined-term">bestätigte Empfangsgelegenheit</strong> betrifft eine Gegenstation und einen WSPR-Zyklus. Erfolgreicher Empfang durch das Target (RX) oder eines Target-Signals (TX) bestätigt sie direkt. Andernfalls müssen Berichte die Aktivität beider Stationen belegen, bevor eine nicht dekodierte Gelegenheit zählt. Die <strong class="defined-term">Dekodierquote</strong> ist der erfolgreiche Anteil in Prozent: erfolgreiche Dekodierungen geteilt durch erfolgreiche plus bestätigt nicht dekodierte Gelegenheiten. Unbekannte Aktivität bleibt ausgeschlossen. Die RX- und TX-Abschnitte erklären, wer wen gehört haben muss.

**Welche Stationen gehen in ein Ergebnis ein?** Eine <strong class="defined-term">qualifizierte Station</strong> hat beibehaltene Spot-Paare für ΔSNR oder erfüllt bei Performance die Mindestzahl an Empfangsgelegenheiten und gegebenenfalls die Bestätigung durch weitere Empfänger. Jedes Kartensegment muss zusätzlich seine Einfärbungsanforderungen erfüllen. Bei ΔSNR muss das Konfidenzintervall die gewählte Präzisionsgrenze einhalten. [Abschnitt 8.5.1](#sec-7-dependence-bias) erklärt die statistischen Annahmen und genauen Einfärbungsbedingungen.

**Die SNR-Bezugsgröße prüfen.** RX Performance und Benchmark rechnen das SNR erfolgreicher Dekodierungen auf eine gemeinsame **gemeldete Sendeleistung von 1 W (30 dBm)** um. Neue TX-Performance-Analysen verwenden standardmäßig das ursprünglich gemeldete Empfangs-SNR; **TX-SNR-Normierung auf 30 dBm** schaltet dieselbe Umrechnung ein. Bei älteren TX-Einstellungen ohne dieses Feld bleibt die Normierung eingeschaltet. Sie verändert den SNR-Vergleich, nicht die beobachteten Dekodierzahlen, und kann falsche Leistungsangaben nicht berichtigen.

Die kumulativen Benchmark-Diagramme „Decodes & Stations“ in den Segmentdetails verwenden das <strong class="defined-term">ursprünglich gemeldete SNR</strong>, ohne Leistungsnormierung oder Referenzkorrektur. Performance verwendet die SNR-Bezugsgröße des abgeschlossenen Laufs. Siehe [Abschnitt 8.1.2](#sec-7-normalization-consolidation).

<a id="sec-3-3"></a>
<a id="sec-3-rx-benchmark"></a>

#### 2.1 RX Benchmark

**Fragestellung:** Wie unterschieden sich zwei Empfangsaufbauten bei denselben Sendern und Zyklen?

Für einen kontrollierten RX Benchmark müssen beide Empfänger während des gesamten gewählten Zeitraums empfangen und Empfangsberichte hochgeladen haben. Benchmark berücksichtigt Berichte beider Seiten auch in Zyklen ohne Target-Empfangsbericht. Die Interpretation setzt deshalb die Betriebsbedingungen aus [Abschnitt 1.2](#sec-2-2) voraus; Benchmark prüft die Target-Aktivität nicht gesondert in jedem Zyklus.

**Erste Prüfungen:**

1. Vergleiche die Karten **ΔSNR** und **ΔDecode**: Geht ein höheres SNR bei den gemeinsam dekodierten Signalen mit mehr Dekodierungen insgesamt einher?
2. Unterscheide anhand der kumulativen SNR-Diagramme zwischen zusätzlichen Dekodierungen und zusätzlichen unterschiedlichen Sendern. Eine einseitige Dekodierung muss keine neue Station hinzufügen.
3. Prüfe in den Segmentdetails, ob der Unterschied über mehrere Sender und Zeitpunkte bestehen bleibt. Untersuche einen repräsentativen Funkpfad in der Stationsauswertung und den Detaildaten.

Für ΔSNR braucht eine Station Spot-Paare; zu ΔDecode zählen weiterhin alle ihre beobachteten Dekodierungen. Die beiden Karten haben unterschiedliche Anforderungen. Auch wenige Beobachtungen können einen großen Wert ergeben. Lies deshalb neben den Farben auch die Anzahlen. Siehe [Mindestanforderungen an die Datengrundlage](#sec-5-4).

<a id="sec-2-3"></a>
<a id="sec-3-rx-benchmark-hardware"></a>

##### 2.1.1 Referenzaufbau oder Referenzstation

**Kontrollierter lokaler Aufbau.** Betreibe für die zu vergleichenden Antennen, Speiseleitungen, Filter, Vorverstärker oder Empfänger gleichzeitig arbeitende, getrennt gekennzeichnete Empfangszweige. Prüfe ihre genauen Melderufzeichen und Standorte in der Datenbank. Ein gemeinsamer vierstelliger Locator belegt weder die Aufstellung am selben physischen Ort noch identische Signalwege.

Halte die nicht untersuchten Teile der Empfangsketten gleich oder miss ihre Unterschiede: Empfänger, Verstärkung, Filterung, Audio, Decoder und Uploads können das Ergebnis beeinflussen. Eine Kalibrierung mit gemeinsamem Eingang oder ein Tausch von Bauteilen zwischen den Empfangsketten hilft zu prüfen, ob ein beobachteter Unterschied dem untersuchten Bauteil folgt. Komponenten, die gemeinsam genutzt werden sollen, müssen tatsächlich gemeinsam genutzt werden. Siehe [parallele WSJT-X-Instanzen](#sec-a) und [Referenzkalibrierung](#sec-reference-snr-calibration).

RX-Melderufzeichen wie `CALL` und `CALL/P` können Empfangszweige unterscheiden, sofern Software und Datenbank sie unverändert übernehmen. Sie verändern nicht das Nachrichtenformat des entfernten Senders.

Die <strong class="defined-term">Referenzkorrektur</strong> wendet vor der Subtraktion einen unabhängig bestimmten Versatz auf das Referenz-SNR an. Eine positive Korrektur erhöht das Referenz-SNR und verringert den angezeigten Target-Vorteil. Sie stellt keine ausgebliebenen Dekodierungen wieder her und verändert ΔDecode nicht. Eine räumlich getrennte Referenz kann für dieses Stationspaar eine wiederholbare Vergleichsbasis bieten, aber keine absolute Kalibrierung.

<a id="sec-3-rx-benchmark-buddy"></a>

**Unabhängige Station.** Wähle eine Referenz, deren Rufzeichen, Standort, Aufbau und Zeitplan du kennst. Der Vergleich umfasst Antennen, Ausrüstung, Rauschen und Ausbreitungspfade beider Stationen. Wiederhole ihn mit derselben stabilen Referenz und beschreibe Unterschiede der vollständigen Stationen. Die Zuordnung zu einer einzelnen Antenne oder einem Empfänger erfordert zusätzliche Kontrolle. Die gepflegte Griffiths/Squibb-Demo liefert ein Beispiel.

<a id="sec-3-tx-benchmark"></a>

#### 2.2 TX Benchmark

**Fragestellung:** Wie unterschieden sich zwei Sendeaufbauten an denselben entfernten Empfängern in denselben Zyklen?

Jedes Spot-Paar vergleicht Berichte desselben Empfängers aus demselben Zyklus. RX-Paare beobachten einen Sender, TX-Paare vergleichen zwei Aussendungen. Für normiertes ΔSNR sind deshalb korrekte Angaben der Sendeleistung entscheidend. Tatsächliche Leistungsunterschiede können weiterhin die Dekodierzahlen beeinflussen; diese werden nicht auf gleiche Leistung normiert.

**Erste Prüfungen:** Vergleiche die beiden Karten, prüfe die Empfänger- und Spot-Paar-Anzahlen und verfolge dann repräsentative Empfänger durch die zeitlichen Ansichten und die Detaildaten. Prüfe, ob ein Ergebnis von wenigen Empfängern, einem einzelnen Intervall oder einer bestimmten Zuordnung der Audiofrequenzen abhängt. Ein besseres SNR der gepaarten Spots garantiert keine höhere Gesamtzahl an Dekodierungen.

Einseitige Beobachtungen bleiben ohne gesonderte Prüfung der Target-Aktivität enthalten. Wenn ein Sender nicht gesendet hat oder die Übermittlung von Empfangsberichten unterbrochen war, kann ΔDecode ungleiche Betriebsgelegenheiten widerspiegeln. Stelle den gemeinsamen Betrieb sicher, bevor du dies als Unterschied zwischen Sendezweigen interpretierst.

<a id="sec-2-4"></a>
<a id="sec-2-4-simultaneous"></a>
<a id="sec-3-tx-benchmark-simultaneous"></a>

##### 2.2.1 Referenzaufbau oder Referenzstation

**Kontrollierter lokaler Aufbau.** Verwende zwei getrennt identifizierbare Sendeketten mit unterschiedlichen gültigen Rufzeichen, synchronisierten WSPR-Zyklen, freien getrennten Frequenzen, gemessener und wahrheitsgemäß gemeldeter Leistung sowie ausreichender HF-Entkopplung. Ein einzelner Sender, der zwischen Antennen wechselt, kann keine gleichzeitigen Spot-Paare liefern.

**Bevorzuge zwei unterschiedliche gültige reguläre Rufzeichen.** Wähle Rufzeichen, die jeweils in das WSPR-Format für eine einzelne Aussendung passen, in der Rufzeichen, Locator und Leistung gemeinsam übertragen werden.

Falls <strong class="defined-term">zusammengesetzte Rufzeichen</strong> — Rufzeichen mit zusätzlichem Präfix oder Suffix — erforderlich sind, können auch zwei unterschiedliche gültige zusammengesetzte Rufzeichen funktionieren. Verwende für diesen kontrollierten Vergleich übereinstimmende, überprüfte Nachrichtenfolgen und stimme die jeweils zusammengehörenden Aussendungen zeitlich aufeinander ab. [Abschnitt 5.1](#sec-simultaneous-tx-setup-1) erklärt die Rufzeichenwahl und die daraus entstehenden Nachrichtenformate.

Prüfe vor dem Sammeln der Empfangsberichte die Firmwareeinstellungen, tatsächlichen Zeitpläne sowie Rufzeichen und Locator beider Sender in der Datenbank. WSPRadar vergleicht einzelne zweiminütige Zyklen. Unterschiedliche Zeitpläne können einseitige Empfangsberichte erzeugen, ohne dass die Ausrüstung einen Vorteil hat. Folge der [Aufbauanleitung und Datenbankprüfung in Kapitel 5](#sec-simultaneous-tx-setup).

Das Ergebnis vergleicht vollständige Sendezweige. Einflüsse von Frequenzgang, QRM, Kopplung und Leistungsfehlern können bestehen bleiben; tausche die Frequenzpositionen und, soweit praktisch möglich, die untersuchten Antennen oder Bauteile zwischen den Sendeketten. Verwende nur eine dokumentierte **SNR-Korrektur der Referenz (dB)**, die für diesen Vergleich gültig ist; sie beeinflusst ΔSNR, nicht die Dekodierzahlen. Siehe [Kalibrierungshinweise](#sec-reference-snr-calibration).

<a id="sec-3-tx-benchmark-buddy"></a>

**Unabhängige Station.** Wähle einen bekannten Referenzsender, dessen Rufzeichen, QTH, Leistung, Ausrüstung und Zeitplan du kennst. Die Berichte können vom selben Empfänger aus demselben Zyklus stammen, obwohl sich Sendestandorte und Ausbreitungspfade unterscheiden. Gleiche vierstellige Locator belegen keine Aufstellung am selben Ort. Beschreibe das Ergebnis als Vergleich vollständiger installierter Stationen.

Beide Anordnungen verwenden **Referenzaufbau oder Referenzstation**. Für ΔSNR sind Spot-Paare erforderlich, doch einseitige Beobachtungen können auch dann zu ΔDecode beitragen, wenn keine Spot-Paare vorliegen. Welche Schlussfolgerung möglich ist, bestimmt die physische Anordnung, nicht ein gemeinsames Basisrufzeichen.

<a id="sec-3-1"></a>
<a id="sec-3-2"></a>
<a id="sec-3-rx-performance"></a>

#### 2.3 RX Performance

**Fragestellung:** Welche Sender hat das Target gehört, aus welchen Richtungen und Entfernungen und wie regelmäßig?

Gib das Rufzeichen des untersuchten Empfängers genau wie gemeldet und seinen QTH-Locator an oder lass das optionale Locatorfeld für die Standortsuche nach **Analyse starten** leer. Wähle ein Band und einen Zeitraum mit hochgeladenen Target-Dekodierungen. Halte die Empfangskette stabil; eine Referenz ist nicht erforderlich.

**Was zählt:** Jede Target-Dekodierung bestätigt eine erfolgreiche Empfangsgelegenheit, auch wenn kein anderer Empfänger diesen Sender gemeldet hat. Fehlt die Dekodierung, zählt dies nur dann als nicht dekodierte Gelegenheit, wenn ein anderer Empfänger diesen Sender gemeldet und das Target einen anderen Sender dekodiert hat — beides auf **demselben Band im selben WSPR-Zyklus**. Andernfalls bleibt der Fall unbekannt und geht nicht in die Quote ein.

Die Anzahlen und Quoten beziehen sich auf Stationen, die die Filter und Stationsanforderungen erfüllen. Dazu gehören auch Sender, die das Target nie dekodiert hat. Lies drei einander ergänzende Größen:

- <strong class="defined-term">Anteil mindestens einmal gehörter Sender</strong> (**Station Reach**): der Prozentsatz dieser Sender, die das Target mindestens einmal gehört hat. Eine erfolgreiche Dekodierung bedeutet noch keinen regelmäßigen Empfang.
- <strong class="defined-term">Mittelwert der Stationsdekodierquoten</strong>: Zuerst wird die Dekodierquote jedes Senders berechnet, dann werden diese Prozentsätze gemittelt. Jede Station zählt gleich viel, auch mit 0 %. Die Karte verwendet diesen Mittelwert. Die <strong class="defined-term">Dekodierquote über alle Empfangsgelegenheiten</strong> teilt dagegen die Summe aller erfolgreichen Dekodierungen durch die Summe aller bestätigten Empfangsgelegenheiten. Stationen mit mehr Gelegenheiten tragen zu dieser zweiten Quote stärker bei.
- <strong class="defined-term">SNR erfolgreicher Dekodierungen</strong>: der Signal-Rausch-Abstand dekodierter Signale, auf die gemeinsame gemeldete Sendeleistung umgerechnet. Für nicht dekodierte Signale liegt kein gemessenes Target-SNR vor.

Zwei Stationen mit **90 erfolgreichen Dekodierungen bei 100 Empfangsgelegenheiten** und **5 bei 10** ergeben beispielsweise einen Mittelwert der Stationsdekodierquoten von **70 %**, aber eine Dekodierquote über alle Empfangsgelegenheiten von **86,4 %** (95 bei 110). Die beiden Quoten beantworten unterschiedliche Fragen; keine ersetzt die andere.

Suche ein Muster auf der Karte und vergleiche in **Spot- und Stationsdekodierungen** den Anteil gehörter Sender und beide Quoten, einschließlich der Entfernungszeilen in den Karten für Spots und Stationen. Die Zeitdiagramme zeigen das SNR erfolgreicher Dekodierungen, die Dekodierquote und ihre Empfangsgelegenheiten; eine Heatmap zeigt die Dekodierquote über alle Empfangsgelegenheiten nach Entfernung und Zeit. Für einen ausgewählten Sender zeigen zwei Diagramme das absolute normierte SNR erfolgreicher Dekodierungen sowie Dekodierquote mit den zugehörigen Anzahlen über den vollständigen Lauf, ohne Entfernungs-Heatmap oder Abweichungsansicht. **So liest du die Ergebnisse** erklärt Gewichtung und Diagrammdetails.

Die **Expertenansicht** zeigt, wie das SNR jeder Station von ihrem eigenen Mittelwert oder Median über den Analyselauf abweicht. Öffne sie, um Änderungen gegenüber dem für diese Station üblichen SNR zu untersuchen; [Abschnitt 8.4.3](#sec-7-view-time) erklärt die Berechnung.

Sinkt die Dekodierquote, während das SNR erfolgreicher Dekodierungen steigt, werden möglicherweise schwache Signale nicht mehr dekodiert. Stärkere verbleibende Empfangsberichte allein zeigen keine Verbesserung. Wiederhole die Beobachtungen auf den betroffenen Funkstrecken zu den relevanten Zeiten. Um eine Änderung einem einzelnen Bauteil zuzuordnen, brauchst du einen kontrollierten Vergleich oder Kreuztausch: Performance hängt auch von lokalem Rauschen, anderer Ausrüstung und der Ausbreitung ab.

<a id="sec-3-tx-performance"></a>

#### 2.4 TX Performance

**Fragestellung:** Welche Empfänger haben das Target gehört, aus welchen Richtungen und Entfernungen und wie regelmäßig?

Gib das Rufzeichen des untersuchten Senders genau wie gemeldet und seinen QTH-Locator an oder lass das optionale Locatorfeld für die Standortsuche nach **Analyse starten** leer. Wähle ein Band und einen Zeitraum mit gemeldeten Target-Aussendungen. Halte HF-Signalweg, Zeitplan und tatsächliche Leistung stabil und melde die Leistung korrekt; eine Referenz ist nicht erforderlich.

**Was zählt:** Der Empfangsbericht eines Empfängers zum Target bestätigt eine erfolgreiche Empfangsgelegenheit, auch wenn er keinen anderen Sender meldet. Fehlt die Target-Dekodierung, zählt dies nur dann als nicht dekodierte Gelegenheit, wenn **dieser Empfänger** einen anderen Sender meldet und ein Bericht von anderer Stelle die Target-Aussendung bestätigt — beides auf **demselben Band im selben WSPR-Zyklus**. Dass ein anderer Empfänger das Target hört, belegt nicht, dass ein stiller Empfänger zugehört hat. Jeder Erfolg zählt einmal; Fälle mit unbekannter Aktivität bleiben ausgeschlossen.

Die Anzahlen und Quoten umfassen Empfänger, die die Filter und Stationsanforderungen erfüllen, auch ohne Target-Dekodierung. Der **Anteil der Empfänger mit mindestens einer Target-Dekodierung** (**Station Reach**) zeigt, welcher Prozentsatz das Target mindestens einmal gehört hat. Lies ihn zusammen mit Dekodierquote und SNR erfolgreicher Dekodierungen. Der **Mittelwert der Stationsdekodierquoten** gewichtet die Empfängerquoten gleich, einschließlich null; die Karte verwendet diesen Mittelwert. Die **Dekodierquote über alle Empfangsgelegenheiten** teilt die Summe der Erfolge durch die Summe der Gelegenheiten. Gemeint sind bestätigte Empfangsgelegenheiten, nicht jede geplante Aussendung oder alle möglichen Empfänger.

Suche ein Muster in **Spot- und Stationsdekodierungen** und den Zeitdiagrammen und untersuche anschließend repräsentative Empfänger. Die Diagramme zeigen das SNR erfolgreicher Dekodierungen auf der gewählten Bezugsgröße, die Dekodierquote mit ihren Empfangsgelegenheiten sowie die gemeinsame Quote nach Entfernung und Zeit. Für einen ausgewählten Empfänger zeigen zwei Diagramme das absolute SNR erfolgreicher Dekodierungen und die Dekodierquote mit den zugehörigen Anzahlen über den vollständigen Analyselauf; eine Entfernungs-Heatmap oder Abweichungsansicht gibt es hier nicht. Prüfe einzelne Tage, bevor du ein wiederkehrendes Tagesmuster beschreibst.

Die **Expertenansicht** vergleicht das SNR jedes Empfängers mit seinem eigenen Mittelwert oder Median über den Analyselauf; siehe [Abschnitt 8.4.3](#sec-7-view-time).

Eine breite geografische Verteilung mit niedrigen Dekodierquoten kann zeitweiligen Empfang bedeuten; eine hohe Quote bei wenigen Empfängern belegt keine breite Abdeckung. Die Ergebnisse hängen von tatsächlicher Sendeleistung, Antenne und Speiseleitung, Gelände, Ausbreitung und Empfangsbedingungen der Gegenstationen ab. Sie messen weder abgestrahlte Leistung noch Antennengewinn oder Wirkungsgrad. Verwende **TX Benchmark**, um Sendezweige zu vergleichen, und wiederhole aufschlussreiche Beobachtungen unter vergleichbaren Bedingungen.

<a id="sec-outlier"></a>

#### 2.5 Vorübergehende ΔSNR-Abweichungen finden und prüfen

Diese optionale Expertendiagnose sucht für jede Gegenstation getrennt nach vorübergehenden Änderungen des gepaarten ΔSNR. Im Bericht zählt jede Kombination aus genauem Rufzeichen und vollständigem gemeldetem Locator als ein <strong class="defined-term">Funkpfad</strong>. Schließe zuerst die reguläre Benchmark-Auswertung ab. Ein möglicher Ausreißer ist ein Anlass zur Untersuchung, kein identifiziertes physisches Ereignis.

<a id="sec-outlier-1"></a>

##### 2.5.1 Wann diese Expertendiagnose sinnvoll ist

Verwende sie, wenn eine vorübergehende Änderung für deine Fragestellung relevant ist und davor, währenddessen und danach genügend Spot-Paare vorliegen. Einseitige Empfangsberichte liefern Kontext, aber kein fehlendes ΔSNR. Ein leerer Bericht kann auf unzureichende Beobachtungsdaten im Umfeld hindeuten, nicht auf einen unveränderten Funkpfad.

Aktiviere **Mögliche ΔSNR-Ausreißer erkennen**, prüfe die [drei Experteneinstellungen](#sec-5-6) und starte dann die Analyse. Änderungen an den Einstellungen erfordern einen weiteren ausdrücklich gestarteten Analyselauf.

<a id="sec-outlier-2"></a>
<a id="sec-outlier-3"></a>

##### 2.5.2 Wie die Erkennung praktisch arbeitet

Das <strong class="defined-term">lokale Vergleichsniveau</strong> schätzt das übliche ΔSNR der Funkstrecke aus ausreichend gestützten Beobachtungen vor und nach einem möglichen Ausreißer. Die Beobachtungen des möglichen Ausreißers selbst bleiben dabei ausgeschlossen. Eine <strong class="defined-term">Abweichung</strong> ist das beobachtete ΔSNR minus diesem Vergleichsniveau. Somit ergibt **+1 dB ΔSNR bei einem Vergleichsniveau von +8 dB eine Abweichung von −7 dB**: Das Target hat weiterhin das höhere SNR, doch sein Vorteil ist gesunken.

Die Erkennung prüft die Größe der Abweichung und einen <strong class="defined-term">robusten z-Score</strong>, der sie mit den zeitlich benachbarten Schwankungen vergleicht. Dazu kommen die Übereinstimmung der Vergleichsmediane vor und nach dem möglichen Ausreißer sowie die Vorzeichen innerhalb dieses Zeitraums. Sie nutzt die einzelnen Zyklusbeobachtungen vor der Zusammenfassung für die Darstellung; eine andere Zeitintervallbreite im Diagramm ändert daher keine Erkennung. Ereignisklassen und Gruppierungen über mehrere Funkstrecken belegen weder unterschiedliche Sicherheit noch eine gemeinsame Ursache. Siehe [die Methode](#sec-7-outliers).

<a id="sec-outlier-4"></a>
<a id="sec-outlier-5"></a>
<a id="sec-outlier-6"></a>

##### 2.5.3 Ein gemeldetes Ereignis lesen und untersuchen

Vergleiche **Erwartetes lokales ΔSNR** mit **Beobachteter ΔSNR-Median**. Prüfe dann Spot-Paar-Anzahl, zeitliche Lücken und einzelne Beobachtungen. **↓ In der Stationsauswertung anzeigen** öffnet den größeren zeitlichen Zusammenhang der Funkstrecke; **↓ Detaildaten anzeigen** öffnet die Detailansicht. Beide bereiten **Möglicher Ausreißer im Detail** mit den umgebenden Beobachtungen zum Vergleichsniveau vor.

Nutze **So liest du die Ergebnisse** in **Bericht zu möglichen Ausreißern** und **Möglicher Ausreißer im Detail**, um Ereignisklassen, Sterne, Schattierung und Hilfslinien der Erkennung nachzulesen. Das hervorgehobene Intervall beschreibt die beibehaltenen Beobachtungen, nicht die Dauer eines unbeobachteten physischen Ereignisses.

Prüfe Target-SNR und korrigiertes Referenz-SNR getrennt: Eine Änderung kann von einer oder beiden Seiten ausgehen. Vergleiche zeitlich benachbarte einseitige Empfangsberichte, andere Funkpfade, Stationsaufzeichnungen, Schaltvorgänge, Leistungs- oder Verstärkungsänderungen und unabhängige Messungen, bevor du eine Ursache zuordnest.

<a id="sec-outlier-7"></a>

##### 2.5.4 Selektivität anpassen und Ergebnis sichern

Höhere Mindestwerte für die Abweichung oder den robusten z-Score machen die Auswahl der gemeldeten Ereignisse strenger. Eine kleinere zulässige Differenz der Vergleichsniveaus vor und nach dem Ereignis verlangt eine engere Übereinstimmung dieser Mediane, keine geringeren Hintergrundschwankungen. Für alle Ereignisdauern gelten dieselben Anforderungen; [Abschnitt 10.6](#sec-5-6) führt die Bedienelemente auf.

Dokumentiere Änderungen, die du beim Erkunden ausprobierst. Lege für eine Bestätigung die Einstellungen und die zu untersuchenden Funkstrecken fest, bevor du einen neuen Analyselauf betrachtest. Berichte Funkstrecke, Zeitraum, Abweichung, stützende Spot-Paare und Einstellungen der Erkennung. Die Erkennung liefert weder einen p-Wert noch eine Korrektur für die Zahl durchsuchter Funkstrecken und Ereignisse.

Speichere den Analyseexport, um die bei aktivierter Ausreißererkennung gefundenen Ergebnisse und ihre beitragenden Spot-Paare zu erhalten. Dateiinhalte und Verfügbarkeit sind in [Abschnitt 9.4](#sec-8-4) festgelegt.

<a id="sec-3-9"></a>

---

<a id="sec-4"></a>

### 3. Ergebnis absichern und kommunizieren

Nutze das Ergebnis für die nächste Entscheidung zu deiner Station. Beschreibe, was die Beobachtungen tragen und was du noch prüfen musst.

<a id="sec-4-1"></a>

#### 3.1 Breite, Übereinstimmung und Wiederholbarkeit beurteilen

Prüfe drei Dinge, bevor du eine Schlussfolgerung ziehst:

- <strong class="defined-term">Breite:</strong> Wie viele Stationen, Beobachtungen, Richtungen und Zeiträume stützen die Aussage? Viele Berichte einer Station bieten nicht dieselbe Breite wie mehrere Funkstrecken. Verschiedene Rufzeichen-Locator-Kombinationen stehen nicht zwangsläufig für unabhängige physische Stationen.
- <strong class="defined-term">Übereinstimmung innerhalb eines Analyselaufs:</strong> Zeigen Karte, Zeitdiagramme und Stationsansichten ein ähnliches Bild? Unterscheiden sich Ergebnisse mit gleicher Stationsgewichtung von Ergebnissen über alle Beobachtungen, prüfe die Stationen mit den meisten Berichten. Lies gepaartes ΔSNR zusammen mit einseitigen Dekodierungen beziehungsweise Performance-SNR zusammen mit der Dekodierquote.
- <strong class="defined-term">Wiederholbarkeit:</strong> Tritt das Muster in einem gesonderten Analyselauf unter vergleichbaren, dokumentierten Bedingungen erneut auf? Die Übereinstimmung verschiedener Ansichten derselben Daten belegt dies nicht.

Ein großer Wert oder eine erfüllte Mindestanforderung allein belegt weder einen Ausrüstungsvorteil noch statistische Sicherheit. Beschreibe die Beobachtung und prüfe mögliche Erklärungen wie Rauschen, Ausbreitung oder Hardwareänderungen durch kontrollierte Änderungen, Kreuztauschversuche oder unabhängige Messungen. [Abschnitt 8.5](#sec-7-claims) erklärt Abhängigkeit und Verzerrung.

<a id="sec-4-2"></a>

#### 3.2 Ergebnis durch Wiederholung und Kontrolle absichern

Ein <strong class="defined-term">explorativer Analyselauf</strong> hilft dir, ein mögliches Muster zu finden. Lege vor einem <strong class="defined-term">bestätigenden Analyselauf</strong> Fragestellung, RX/TX-Richtung, Band, gegebenenfalls Referenz, Einstellungen, Schwellen, Zeitplan und den vorrangig untersuchten geografischen oder zeitlichen Bereich fest. Dazu gehört **Maximale Entfernung der Gegenstationen vom Target (km)**. Bewahre andere Bereichsauswahlen als gesonderte Prüfungen auf und berichte sie, statt nur das günstigste Ergebnis auszuwählen.

Wiederhole den Versuch an einem anderen Tag oder in einer anderen Ausbreitungsphase und halte dabei die nicht untersuchten Variablen stabil. Wähle ein Zeitfenster, das lang genug ist, um die in deiner Schlussfolgerung genannten Bedingungen abzudecken; Aussagen über Tagesmuster benötigen Beobachtungsdaten über mehrere Tage, die chronologisch geprüft wurden. Halte Notizen fest, damit sich der physische Aufbau reproduzieren lässt.

RX untersucht entfernte Sender, TX entfernte Empfänger; dafür gelten unterschiedliche Regeln für Empfangsgelegenheiten. Stimme beim Vergleich deiner RX- und TX-Ergebnisse Band, Zeitraum, geografischen Bereich und Konfiguration ab. Interpretiere beide getrennt: Gleiche Prozentsätze bedeuten keine gleiche Empfangs- und Sendefähigkeit.

<a id="sec-4-3"></a>

#### 3.3 Eine der Datengrundlage angemessene Schlussfolgerung formulieren

Nenne Target, Analyseart, Band, UTC-Zeitraum und geografischen Bereich. Gib dann das Ergebnis **mit seiner Gewichtung und den stützenden Anzahlen** an. Nenne bei Benchmark außerdem die Referenz und ihre angewandte SNR-Korrektur, einschließlich null. Beschreibe, wie der gemeinsame Betrieb bestätigt wurde, oder benenne die Einschränkung historischer Empfangsberichte ohne diese Bestätigung.

**Vorlage für Performance**

> Für [Target, Band, UTC-Zeitfenster und Auswertungsbereich] betrug der Mittelwert der Stationsdekodierquoten [x%] über [n berücksichtigte Stationen]. Die Dekodierquote über alle Empfangsgelegenheiten betrug [y%] über [m bestätigte Empfangsgelegenheiten]. Das beobachtete Muster war [breit, richtungsabhängig, zeitweise auftretend oder auf den angegebenen Zeitraum beschränkt].

**Vorlage für Benchmark — Zusammenfassung der Stationsmediane**

> Für [Target und Referenz, Band, UTC-Zeitfenster und Auswertungsbereich] lag der Median der Stationsmediane von ΔSNR um [x dB] zugunsten von [Aufbau], gestützt auf [n Stationen mit Paaren und m Spot-Paare]. Die zusammengefassten Dekodierzahlen betrugen [Target-Gesamtzahl] und [Referenz-Gesamtzahl], mit [Anzahlen gepaart, nur Target und nur Referenz]. Der Vergleich verwendete [kontrollierte Signalwege, unabhängige Stationen oder eine Auswertung historischer Empfangsberichte].

Für ein **Segment der ΔSNR-Karte** nennst du stattdessen den **Mittelwert über alle gepaarten ΔSNR-Werte und sein Konfidenzintervall**, das Segment sowie seine Stations- und Spot-Paar-Anzahlen. [Abschnitt 8.2.3](#sec-7-benchmark-aggregation) erklärt die unterschiedliche Gewichtung.

Ergänze die Anzahl beziehungsweise den Anteil mindestens einmal gehörter Sender (RX) oder der Empfänger, die das Target gehört haben (TX), und relevante zeitliche Muster, soweit sie die Aussage stützen. Vergleiche zwischen Karten die Zahlenwerte der Legenden. Ein Unterschied zwischen vollständigen Stationen belegt für sich keinen Antennengewinn, Wirkungsgrad, keine kalibrierte Empfindlichkeit und keine physische Ursache, die der Versuch nicht gemessen hat. [Kapitel 9](#sec-8) enthält die vollständige Berichtscheckliste und Beispiele.

<a id="sec-4-4"></a>

#### 3.4 Analyselauf und Kontext sichern

Wähle den Bereich in den Segmentdetails, die Station und ein gegebenenfalls zu sicherndes Fokusintervall. Wähle **Alle Ergebnisse zum Herunterladen vorbereiten** und anschließend **Vorbereitete Ergebnisse herunterladen**. Das Vorbereiten allein speichert die Datei nicht; bereite sie nach einer Änderung dieser Auswahlen erneut vor.

Die ZIP-Datei enthält Konfiguration, Metadaten, verarbeitete Beobachtungen und die zugehörigen Tabellen und Abbildungen. Die verarbeiteten Beobachtungen umfassen den abgeschlossenen Analyselauf; einzelne Tabellen und Abbildungen beziehen sich auf ihre jeweils ausgewählten Bereiche oder Stationen. **Konfiguration speichern** oder ein Analyselink bewahrt die Einstellungen, nicht die ursprünglichen Beobachtungen. Eine spätere Abfrage oder erneute Analyse kann andere Ergebnisse liefern.

Bewahre zusammen mit der ZIP-Datei kurze Stationsnotizen auf: Antennen und Speiseleitungen, Anordnung der Signalzweige oder Verteiler, Hardware und Software, Verstärkung und Leistung, Zeitpläne, Kalibrierung sowie bewusste Änderungen oder Fehler. WSPRadar kann diese physischen Einzelheiten nicht erschließen. Siehe [Dokumentationscheckliste](#sec-8-3) und [Exportinhalte](#sec-8-4).

<div style="page-break-before: always;"></div>

<a id="part-iv"></a>

## Teil II: Praktische Anleitung zum Stationsaufbau

Richte zwei Empfangszweige ein, bereite einen simultanen Sendevergleich vor oder bestimme eine RX-Korrektur. Wähle das passende Vorgehen für deinen Versuch und schließe die zugehörigen Prüfungen ab, bevor du die Messdaten aufzeichnest.

| Ziel | Vorgehen | Bereit, wenn |
|---|---|---|
| **Simultaner Empfang unter Windows** | [Kapitel 4](#sec-a): Lege die beiden WSJT-X-Instanzen an, kopiere bei Bedarf die Ausgangskonfiguration und prüfe anschließend beide Signalwege. Fahre mit [Kapitel 6](#sec-reference-snr-calibration) fort, wenn eine Kalibrierung erforderlich ist. | Beide Empfänger laden unter den vorgesehenen Rufzeichen und Locatoren Empfangsberichte hoch. Audio- und Datenpfade sind korrekt und die Uhren synchronisiert. |
| **Kontrolliertes simultanes Senden** | [Kapitel 5](#sec-simultaneous-tx-setup): Plane den Aufbau, folge der [Geräteanleitung](#sec-simultaneous-tx-setup-5) und prüfe anschließend [Zeitsteuerung und Signale](#sec-simultaneous-tx-setup-2), [Leistung](#sec-simultaneous-tx-setup-3) und [Datenbankberichte](#sec-simultaneous-tx-setup-4). [5.6](#sec-simultaneous-tx-setup-6) dient der Bestätigung des Ergebnisses. | Gemeinsame Empfänger melden beide sauberen, korrekt platzierten Signale in den vorgesehenen Zyklen unter den erwarteten Rufzeichen und Locatoren. |
| **Dokumentierte RX-SNR-Korrektur** | [Kapitel 6](#sec-reference-snr-calibration): Messung mit gemeinsamem Eingangssignal, Konsistenzprüfungen, vorzeichenrichtige Korrektur und unabhängige Validierung. | Der Offset ist unter den dokumentierten Bedingungen stabil und wird durch separate Validierungsdaten gestützt. |

Verwende die Anleitungen für die genaue Hardware und Firmware; das ZachTek-Verfahren nutzt die standardmäßige Zeitsteuerung und zufällige Frequenzwahl. Kehre nach Abschluss zu [Abschnitt 1.2](#sec-2-2) zurück. Belasse die Einstellung bei **Keine Korrektur**, solange kein Offset begründet ist.



<a id="sec-a"></a>
### 4. Parallele WSJT-X-Instanzen für simultanen Empfang

**Ziel:** Betreibe zwei Empfangszweige gleichzeitig, mit getrennten Audioströmen, Meldekennungen, Einstellungen und Dateien. Dieses Windows-Verfahren nutzt die dokumentierte WSJT-X-Option `--rig-name`; eine zweite Installation von WSJT-X ist nicht erforderlich <a href="#ref-12">[Ref-12]</a>.

Lege zwei benannte Instanzen an: **WSJT-X Target** und **WSJT-X Reference**. Kopiere bei Bedarf eine funktionierende Ausgangskonfiguration und prüfe anschließend beide Signalwege, bevor du Messdaten sammelst. Diese Namen kennzeichnen die lokalen Softwareinstanzen; sie legen nicht die Rufzeichen fest, die an die Datenbank übermittelt werden.

Für ein Experiment mit simultanem Senden verwende [Kapitel 5](#sec-simultaneous-tx-setup). [Abschnitt 4.4](#sec-a-4) erläutert, warum zwei gleiche WSJT-X-Einstellungen für `Tx Pct` noch keinen gemeinsamen Zeitplan für das Senden in ausgewählten Zyklen ergeben.



<a id="sec-a-1"></a>
#### 4.1 Target- und Referenzinstanz anlegen

1. Erstelle zwei Desktop-Verknüpfungen zur installierten `wsjtx.exe`. Benenne sie **WSJT-X Target** und **WSJT-X Reference**.
2. Öffne jeweils die **Properties** (Eigenschaften) der Verknüpfung. Ergänze im Windows-Feld **Target** (Ziel) den zugehörigen Rig-Namen **nach** dem schließenden Anführungszeichen des Programmpfads. Ersetze den Beispielpfad durch den Pfad deiner Installation:

| Verknüpfung | Windows-Feld **Target** der Verknüpfung |
|---|---|
| **WSJT-X Target** | `"C:\WSJTX\bin\wsjtx.exe" --rig-name=Target` |
| **WSJT-X Reference** | `"C:\WSJTX\bin\wsjtx.exe" --rig-name=Reference` |

3. Starte jede Verknüpfung einmal und schließe die Instanz anschließend, damit ihre Dateien initialisiert werden.

Unter Windows werden folgende Speicherorte verwendet:

| Datei oder Ordner | WSJT-X Target | WSJT-X Reference |
|---|---|---|
| Einstellungen | `%LOCALAPPDATA%\WSJT-X - Target\WSJT-X - Target.ini` | `%LOCALAPPDATA%\WSJT-X - Reference\WSJT-X - Reference.ini` |
| Protokolle und beschreibbare Dateien | `%LOCALAPPDATA%\WSJT-X - Target\` | `%LOCALAPPDATA%\WSJT-X - Reference\` |
| Standardordner für gespeicherte Audiodateien | `%LOCALAPPDATA%\WSJT-X - Target\save\` | `%LOCALAPPDATA%\WSJT-X - Reference\save\` |

**Diese Ordner im Datei-Explorer öffnen:** Drücke **Windows+E** und anschließend **Ctrl+L**, um die Adressleiste auszuwählen. Gib `%LOCALAPPDATA%` ein und drücke **Enter**, um den lokalen Anwendungsdatenordner deines Benutzerkontos zu öffnen. Öffne `WSJT-X - Target` oder `WSJT-X - Reference`. Du kannst auch einen vollständigen Ordnerpfad aus der Tabelle in die Adressleiste einfügen. Die Anzeige **Hidden items** musst du dafür nicht aktivieren.

Starte die beiden Instanzen immer über ihre benannten Verknüpfungen. Ein anderer Rig-Name erzeugt einen anderen Satz von Speicherorten. Falls deine WSJT-X-Version andere Menüs oder Pfade verwendet, prüfe das zugehörige Benutzerhandbuch <a href="#ref-12">[Ref-12]</a>.



<a id="sec-a-2"></a>
#### 4.2 Ausgangskonfiguration bei Bedarf kopieren

**Optional:** Konfiguriere zunächst **WSJT-X Target** nach [4.3](#sec-a-3) und kopiere dann dessen Konfiguration, damit **WSJT-X Reference** mit denselben Einstellungen beginnt. Andernfalls konfiguriere beide Instanzen direkt in 4.3.

1. Schließe **alle** WSJT-X-Instanzen und bewahre eine Sicherung aller Einstellungen auf, die du ersetzen möchtest.
2. Kopiere die Target-Einstellungsdatei `%LOCALAPPDATA%\WSJT-X - Target\WSJT-X - Target.ini` in den Reference-Ordner `%LOCALAPPDATA%\WSJT-X - Reference\`.
3. Benenne die Kopie in `WSJT-X - Reference.ini` um. Ersetze die gerade initialisierte Reference-Datei nur, wenn dies beabsichtigt ist.

Die resultierende Reference-Einstellungsdatei muss `%LOCALAPPDATA%\WSJT-X - Reference\WSJT-X - Reference.ini` heißen. Beim Kopieren werden auch Hardware-, Verzeichnis- und Stationseinstellungen übernommen; führe deshalb vor Beginn des Empfangs jede zutreffende Prüfung unten an **beiden** Instanzen durch.

**Vorhandene Konfiguration weiterverwenden:** Du kannst **WSJT-X Target** zunächst mit den bereits verwendeten Einstellungen einrichten. Gehe dabei ebenso vor: schließen, sichern, kopieren und umbenennen. Bei einer vorhandenen Standardkonfiguration ist die Quelldatei `%LOCALAPPDATA%\WSJT-X\WSJT-X.ini`; kopiere sie in den Target-Ordner und benenne sie `WSJT-X - Target.ini`. Anschließend kannst du Target wie oben beschrieben nach Reference kopieren.



<a id="sec-a-3"></a>
#### 4.3 Alle Datenpfade trennen

Öffne **WSJT-X Target** und **WSJT-X Reference** nacheinander und prüfe die folgenden Einstellungen für ihre jeweiligen physischen Signalwege. Eine kopierte Konfiguration kann in der Reference-Instanz weiterhin den Audioeingang oder das Funkgerät des Targets auswählen.

| Prüfung | Was einzustellen oder zu prüfen ist |
|---|---|
| **Audioeingang** | Wähle unter **File > Settings > Audio** den **Input** des vorgesehenen Empfängers. Wenn unabhängige Signalwege eine Stereo-Audioschnittstelle gemeinsam nutzen, wähle für jede Instanz den richtigen Kanal. |
| **Audioformat** | Konfiguriere das Windows-Audiogerät gemäß WSJT-X-Handbuch auf **48 000 Hz, 16 Bit**. Deaktiviere die Windows-Audioverbesserungen für diese Geräte. |
| **Funkgerätesteuerung** | Verwende unter **File > Settings > Radio** das vorgesehene Funkgerät und die zugehörige Steuerverbindung. Wähle **None**, wenn dieser reine Audioaufbau keine CAT-Steuerung benötigt, und stimme den Empfänger oder SDR manuell auf die passende WSPR-USB-Einstellfrequenz ab. |
| **Gespeicherte Audiodateien** | Setze **Save Directory** für Target auf `%LOCALAPPDATA%\WSJT-X - Target\save\` und für Reference auf `%LOCALAPPDATA%\WSJT-X - Reference\save\`. |
| **AzEl-Ausgabe, falls verwendet** | Weise **AzEl Directory** einen eigenen Speicherort zu: `%LOCALAPPDATA%\WSJT-X - Target\` für Target und `%LOCALAPPDATA%\WSJT-X - Reference\` für Reference. Diese Ausgabe wird von der Funktion Astronomical Data verwendet; für die WSPR-Analyse ist sie nicht erforderlich. |
| **Meldekennung** | Trage unter **File > Settings > General** in **My Call** die exakte Meldekennung der jeweiligen Instanz und in **My Grid** den tatsächlichen Locator dieses Empfangsaufbaus ein. Wähle unten die Variante mit zwei Rufzeichen oder einem Rufzeichen; die Identitäten müssen in der Datenbank unterscheidbar bleiben. |
| **WSPR-Betrieb** | Wähle **Mode > WSPR** und das vorgesehene Band, aktiviere **Monitor**, prüfe Audiopegel und Dekodereinstellungen, lasse **Enable Tx** für dieses RX-Experiment ausgeschaltet und aktiviere das Hochladen von Spots. |
| **Zeit** | Prüfe, dass die Computeruhr mit einer Abweichung von höchstens ±1 Sekunde auf UTC synchronisiert ist. Instanzen auf demselben PC verwenden dessen gemeinsame Uhr; getrennte PCs benötigen jeweils eine Synchronisation. |

Diese Einstellungen und die instanzspezifischen Pfade folgen dem WSJT-X-Handbuch <a href="#ref-12">[Ref-12]</a>.

<a id="sec-rx-reporting-identities"></a>
<blockquote class="setup-important">
<p class="setup-important-lead"><strong>RX-Meldekennungen auswählen.</strong> Wenn zwei geeignete Rufzeichen verfügbar sind, verwende eines für jeden Empfangszweig. Bei einem Basisrufzeichen verwende zwei verschiedene Meldesuffixe, beispielsweise <code>CALL/1</code> für Target und <code>CALL/2</code> für die Referenz. Ersetze <code>CALL</code> durch dein tatsächliches Basisrufzeichen und bestätige, dass der Meldedienst beide exakten Identitäten annimmt und beibehält. Trage den tatsächlichen Locator jedes Empfängers ein; Aufbauten am selben Standort teilen ihn normalerweise, während Empfänger an unterschiedlichen Standorten ihre eigenen Ortsangaben behalten.</p>
<p>WSJT-X übermittelt mit jedem hochgeladenen Spot die <strong>Meldekennung des Empfängers über das Internet</strong>. Ein Suffix an dieser Stelle verändert die WSPR-Nachricht des entfernten Senders nicht und erfordert keine zusätzlichen Funkaussendungen. Lasse <strong>Enable Tx</strong> für diesen RX-Aufbau ausgeschaltet. Für ein zusammengesetztes Rufzeichen im Sendebetrieb verwende das TX-Verfahren in <a href="#sec-tx-one-callsign-two-suffixes">Abschnitt 5.1.2</a>; die Annahme einer RX-Meldekennung belegt nicht ihre Zulässigkeit für Aussendungen <a href="#ref-12">[Ref-12]</a>.</p>
</blockquote>

**Bereit für einen RX-Test:** Beide Instanzen empfangen die vorgesehenen unabhängigen Datenströme und laden unter den richtigen Identitäten auf dem ausgewählten Band Empfangsberichte hoch. Bestätige die Hardwarezuordnung durch eine praktische Prüfung; getrennte Ordner allein belegen keine getrennten HF-Signalwege. Prüfe, dass die Empfangsberichte die in WSPRadar ausgewählte Datenbank erreichen, und berücksichtige dabei die [Verzögerung beim vorgelagerten Datendienst](#sec-6-6).

Wenn der Vergleich eine gemessene Empfangskettenkorrektur erfordert, fahre mit [Kapitel 6](#sec-reference-snr-calibration) fort. Verwende andernfalls das [RX-Benchmark-Verfahren](#sec-3-rx-benchmark) mit dem dokumentierten Aufbau.



<a id="sec-a-4"></a>
#### 4.4 Grenzen von WSJT-X für simultanes Senden

**Gleiche Uhrzeit bedeutet noch keinen gemeinsamen Sendezeitplan.** Im gewöhnlichen WSPR-Betrieb wählt WSJT-X die Sendeperioden entsprechend **Tx Pct** zufällig aus. Zwei Instanzen mit demselben Wert unter `100%` können zufällig im selben Zyklus senden. Die Einstellung garantiert jedoch keinen gemeinsamen A/B-Zeitplan für das Senden in ausgewählten Zyklen <a href="#ref-12">[Ref-12]</a>.

Bei aktiviertem Sendebetrieb versucht mit `Tx Pct = 100%` jede Instanz, in jedem Zyklus zu senden. Eine WSPR-2-Nachricht dauert etwa **110,6 Sekunden** des 120-Sekunden-Zyklus. Daraus ergibt sich eine <strong class="defined-term">HF-Einschaltdauer</strong> von ungefähr **92%** — der Zeitanteil, in dem der Sender tatsächlich HF abgibt <a href="#ref-8">[Ref-8]</a>.

WSPRadar empfiehlt, für dieses Experiment etwa **5–20% der verfügbaren Zyklen** zu verwenden; auf stark belegten Bändern oder bei längeren Versuchen ist das untere Ende vorzuziehen. Dies ist eine Betriebsempfehlung, keine Grenze des WSPR-Protokolls. Der Anteil ausgewählter Zyklen und die HF-Einschaltdauer sind unterschiedliche Größen.

Wenn beide Sender nur in ausgewählten Zyklen gleichzeitig senden sollen, verwende Hardware mit einem festen Zeitplan und prüfe die tatsächlichen Sendestarts. [Kapitel 5](#sec-simultaneous-tx-setup) beschreibt Verfahren für QMX/QMX+ Virtual U3S, Ultimate3S sowie ein modellspezifisches ZachTek-Konfigurationsverfahren mit Standardfirmware.



<div style="page-break-before: always;"></div>

<a id="sec-simultaneous-tx-setup"></a>
### 5. Referenzaufbau für simultanes Senden

**Ziel:** Sende zwei unterscheidbare Signale über den Target- und den Referenzsignalweg in denselben WSPR-Zyklen, entweder mit zwei Aufbauten an einer Station oder mit zwei koordinierten Stationen. Entfernte Empfänger können dann beide Signale im selben Zyklus melden und damit einen TX Benchmark ermöglichen. Das Ergebnis vergleicht die vollständigen dokumentierten Signalwege einschließlich aller nicht kontrollierten Geräteunterschiede.

Gehe in dieser Reihenfolge vor:

| Schritt | Handlung |
|---|---|
| **1. Planen** | Wähle in [5.1](#sec-simultaneous-tx-setup-1) gültige Sendekennungen und ein übereinstimmendes Nachrichtenmuster. Dokumentiere, welche Identität zu welchem physischen Signalweg gehört. |
| **2. Konfigurieren** | Befolge die Anleitung für deine Hardware in [5.5](#sec-simultaneous-tx-setup-5). Beginne bei QRP Labs mit einem aktivierten Eintrag für die gewählte Rufzeichenvariante. Das ZachTek-Verfahren verwendet die modellspezifische Standardkonfiguration vor den Prüfungen am Messplatz. |
| **3. Am Messplatz prüfen** | Prüfe Zeitsteuerung und Signalplatzierung in [5.2](#sec-simultaneous-tx-setup-2), anschließend die tatsächliche Leistung und die Signalqualität im simultanen Betrieb in [5.3](#sec-simultaneous-tx-setup-3). |
| **4. Empfangsberichte prüfen** | Schließe eine kurze Vorabprüfung im Sendebetrieb und in der Datenbank nach [5.4](#sec-simultaneous-tx-setup-4) ab und beginne danach den Messzeitraum. |
| **5. Befund bestätigen** | Wiederhole den Versuch mit vertauschten Frequenzpositionen oder Hardwarezuordnungen, wie in [5.6](#sec-simultaneous-tx-setup-6) beschrieben. |

Verwende Rufzeichen und Betriebsbedingungen, die für deine Station und Zulassung gültig sind. Führe vor dem Anschließen der Antennen die zur Hardware passenden Prüfungen der HF-Sicherheit, Filterung und Entkopplung durch.



<a id="sec-simultaneous-tx-setup-1"></a>
#### 5.1 Rufzeichen auswählen

Wähle das Verfahren passend zu den für das Experiment verfügbaren Rufzeichen. Target und Referenz können zwei Aufbauten an einer Station oder zwei koordinierte Stationen sein. Behalte während des gesamten Experiments die Zuordnung jedes vollständigen Rufzeichens zu seinem dokumentierten physischen Signalweg bei.

**Rufzeichen werden bei RX anders übermittelt als bei TX.** Ein [RX-Meldesuffix](#sec-rx-reporting-identities) wird über das Internet übermittelt. Beim Senden muss das Rufzeichen in der ausgestrahlten WSPR-Nachricht codiert sein; deshalb bestimmt ein gewöhnliches oder zusammengesetztes Rufzeichen die benötigte Nachrichtenfolge <a href="#ref-12">[Ref-12]</a>.

<a id="sec-tx-two-distinct-callsigns"></a>
##### 5.1.1 Zwei verschiedene Rufzeichen

Verwende dieses Verfahren, wenn zwei verschiedene Rufzeichen für den vorgesehenen Betrieb gültig sind und **beide in das gewöhnliche WSPR-Format <strong class="defined-term">Type 1</strong> passen**. Jede Aussendung enthält das Rufzeichen, einen Locator mit vier Zeichen (<strong class="defined-term">grid-4</strong>) und die gemeldete Leistung gemeinsam.

| Anordnung | Rufzeichen und Standorte |
|---|---|
| **Zwei Aufbauten an einer Station** | Weise Target ein gültiges Rufzeichen und der Referenz das andere zu. Melde das gemeinsame tatsächliche QTH wahrheitsgemäß. |
| **Zwei Stationen** | Jede Station verwendet ihr eigenes gültiges Rufzeichen und tatsächliches QTH. Stimme Band, ausgewählte Zyklen und Nachrichtenmuster aufeinander ab; das Ergebnis schließt die unterschiedlichen Standorte und Funkpfade ein. |

Deaktiviere auf beiden Geräten die erweiterten Nachrichten für das Verfahren mit einer Nachricht. Wähle in der zitierten ZachTek-Firmware ausdrücklich **no prefix/suffix** und verwende `LocationPrecision = 4`. Ein normales Basisrufzeichen allein deaktiviert keine bereits gewählte Suffixoption, und die Genauigkeit `6` fügt auch nach einer gewöhnlichen Type-1-Nachricht eine zweite Aussendung hinzu. Gleiche das **tatsächlich gesendete Muster** ab, nicht nur das Rufzeichenformat.

Öffne die [QMX/QMX+- oder Ultimate3S-Anleitung](#sec-simultaneous-tx-setup-5-1) oder die [ZachTek-Anleitung](#sec-simultaneous-tx-setup-5-3), führe deren gemeinsame Vorbereitung durch und wähle anschließend **Zwei verschiedene Rufzeichen**.

<a id="sec-tx-one-callsign-two-suffixes"></a>
##### 5.1.2 Ein Rufzeichen mit zwei Suffixen

Verwende dieses Verfahren, wenn du ein Basisrufzeichen hast und zwei Sendeaufbauten mit zwei gültigen zusammengesetzten Rufzeichen unterscheiden musst. `CALL/1` und `CALL/2` veranschaulichen das Muster; ersetze `CALL` durch dein tatsächliches Basisrufzeichen. Verwende nur Suffixe, die für Operator, Station und Betrieb zulässig sind und von der ausgewählten Firmware unterstützt werden. Erfinde kein Sendesuffix lediglich als Hardwarekennzeichnung.

Die Firmware erzeugt die erweiterte Folge automatisch:

| Nachricht | Übertragene Information |
|---|---|
| <strong class="defined-term">Type 2</strong> | Das vollständige zusammengesetzte Rufzeichen und die gemeldete Leistung, ohne Locator. |
| <strong class="defined-term">Type 3</strong> | Der Locator mit sechs Zeichen (<strong class="defined-term">grid-6</strong>) und die gemeldete Leistung sowie ein kompakter Rufzeichencode (ein <strong class="defined-term">Hash</strong>), den der Empfänger dem vollständigen Rufzeichen zuordnen muss. |

Reserviere für jede vollständige Folge **zwei aufeinanderfolgende zweiminütige Zeitschlitze**. Richte die Type-2-Phasen beider Sender aufeinander aus und ebenso ihre Type-3-Phasen. WSPRadar vergleicht weiterhin die Empfangsberichte jedes einzelnen zweiminütigen Zyklus; es fasst die Folge nicht zu einer vierminütigen Beobachtung zusammen.

Öffne die [QMX/QMX+- oder Ultimate3S-Anleitung](#sec-simultaneous-tx-setup-5-1) oder die [ZachTek-Anleitung](#sec-simultaneous-tx-setup-5-3), führe deren gemeinsame Vorbereitung durch und wähle anschließend **Ein Rufzeichen mit zwei Suffixen**.

**Für beide Verfahren:** Trage den tatsächlichen Locator jedes Aufbaus ein. Signalwege am selben Standort teilen normalerweise einen Locator; getrennte Stationen müssen ihre eigenen Ortsangaben beibehalten. Kombiniere kein Muster mit einem Zyklus auf einem Signalweg mit einem anders geplanten Muster aus zwei Zyklen auf dem anderen: Die zusätzliche Phase kann allein durch den Aufbau einseitige Beobachtungen erzeugen. Prüfe vor der Verwendung von erweitertem WSPR die [Identitätsregeln](#sec-7-spots-identities-cycles) und [Grenzen der Hash-Zuordnung](#sec-7-benchmark-outcomes) <a href="#ref-12">[Ref-12]</a> <a href="#ref-29">[Ref-29]</a>.




<a id="sec-simultaneous-tx-setup-2"></a>
#### 5.2 Zeitplan abgleichen und Signale trennen

Prüfe nach der Umsetzung der [Hardwareanleitung](#sec-simultaneous-tx-setup-5) beide Geräte gemeinsam:

1. **Zeit und Band:** Synchronisiere beide Sender auf genaue UTC, vorzugsweise mit Satellitenzeit wie GPS, und wähle dasselbe Band.
2. **Ausgewählte Zyklen:** Stelle denselben festen Wiederholungsrhythmus ein und prüfe, dass beide Sender zu denselben geraden UTC-Minuten starten. Beide Signalwege müssen in jedem vorgesehenen Vergleichszyklus vollständige Nachrichten senden.
3. **Phasen der Nachrichtenfolge:** Wenn erweitertes WSPR aktiviert ist, prüfe, dass die entsprechenden Phasen gemeinsam stattfinden, auch nach einem Neustart. Nur die erste Phase abzugleichen reicht nicht aus.
4. **Frequenzabstand:** Platziere in den QRP-Labs-Beispielen mit festen Frequenzen die Signalmitten nominal **100 Hz auseinander**, wobei beide vollständigen Signale mit ausreichendem Rand innerhalb des 200 Hz breiten WSPR-Sendeunterbands liegen müssen. Das ZachTek-Verfahren verwendet stattdessen die standardmäßige zufällige Frequenzwahl aus [5.5.2](#sec-simultaneous-tx-setup-5-3); sie garantiert keinen Mindestabstand.

Verwende die ausgearbeiteten 40-m- oder 20-m-Einstellungen in [5.5.1](#sec-simultaneous-tx-setup-5-1). Diese Einstellungen geben **abgestrahlte HF-Frequenzen** an, nicht die USB-Einstellfrequenzen eines Empfängers. Die zitierten QRP-Labs-Handbücher definieren die WSPR-Einstellung als Signalmitte; die zitierte ZachTek-Firmware verwendet den niedrigsten Ton, also <strong class="defined-term">Ton 0</strong>. Verwende die Konvention deiner genauen Firmware <a href="#ref-12">[Ref-12]</a> <a href="#ref-29">[Ref-29]</a>.

Prüfe die einzelnen Frequenzen mit geeigneten Messgeräten und untersuche anschließend beide Signale gemeinsam in einer Wasserfall- oder Spektrumanzeige eines Empfängers. Bestätige bei Aufbauten mit festen Frequenzen den vorgesehenen Abstand; untersuche bei der standardmäßigen zufälligen Frequenzwahl von ZachTek die Frequenzplatzierung über mehrere Folgen und gehe dauerhaft identischen Frequenzwahlen nach. Prüfe in beiden Fällen die Randabstände der vollständigen Signale. Ein größerer Abstand zwischen festen Frequenzen verringert diese Randabstände. Wiederhole die Zeit- und Frequenzprüfungen nach einem Neustart, Firmwareupdate oder einer Konfigurationsänderung.



<a id="sec-simultaneous-tx-setup-3"></a>
#### 5.3 Leistung und Signalqualität im simultanen Betrieb prüfen

**Miss zuerst die tatsächliche Leistung; stelle danach ihren gemeldeten Wert ein.** Das WSPR-dBm-Feld beschreibt die Leistung. Die Eingabe eines anderen Werts stellt die HF-Ausgangsleistung des Senders nicht selbst ein.

1. **Messpunkt wählen.** Entscheide, ob der Vergleich Verluste der Speiseleitung oder andere Verluste im Signalweg einschließt, und dokumentiere, wo die Leistung gemessen wird. Verwende für beide Signalwege dieselbe Grundlage.
2. **Jeden Sender einzeln einstellen und messen.** Verwende eine geeignete Kunstantenne oder einen sicher gedämpften Messpfad. Stelle die tatsächliche Ausgangsleistung mit der vom Gerät unterstützten Methode oder mit geeigneter externer Dämpfung ein. WSPRadar empfiehlt für diesen Versuch etwa **100 mW–1 W (20–30 dBm)**; verwende nicht mehr als erforderlich. Bewahre die Messung der tatsächlichen Leistung im Versuchsprotokoll auf.
3. **Wahrheitsgemäße gemeldete Leistung eingeben.** Verwende den nächstgelegenen gültigen WSPR-codierten Wert. In diesem Bereich sind **20, 23, 27 und 30 dBm** verfügbar, entsprechend ungefähr **100 mW, 200 mW, 500 mW und 1 W**. Verwende keine falschen Leistungswerte als A/B-Kennzeichnungen. Nutze im zitierten ZachTek-Build die Leistungsmeldung **Normal** statt der Höhenkodierung <a href="#ref-12">[Ref-12]</a> <a href="#ref-29">[Ref-29]</a>.
4. **Simultanen Betrieb prüfen.** Betreibe zwei Sender am selben Standort beide an Lasten und untersuche ihre gemeinsamen Signale über geeignete gedämpfte und entkoppelte Messabgriffe. Prüfe Frequenzen, belegte Bandbreite, Oberwellen, unerwünschte Aussendungen und Intermodulationsprodukte. Bei Sendern an getrennten Stationen führe die Einzelprüfungen am Messplatz an jedem Standort durch und untersuche während der Vorabprüfung im Sendebetrieb den simultanen Empfang an einem gemeinsamen Empfänger.

**Bereit für die Vorabprüfung im Sendebetrieb:** Die tatsächlichen Leistungen und ihre Meldegrundlage sind dokumentiert, die Signale belegen die vorgesehenen Positionen, und im simultanen Betrieb wurde kein Fehler festgestellt, der den Vergleich ungültig macht. Ein sauberes Einzelsignal jedes Senders belegt nicht die Qualität des gleichzeitig sendenden Paars.



<a id="sec-simultaneous-tx-setup-4"></a>
#### 5.4 WSPRnet und die ausgewählte Datenbank prüfen

Sende eine kurze Testfolge und prüfe, ob die erwarteten Empfangsberichte in WSPRadar ankommen.

1. Sende mehrere vollständige synchronisierte Folgen mit den endgültigen Einstellungen für Rufzeichen, QTH, Leistung, Zeitplan und Frequenz.
2. Suche in der [WSPRnet Spot Query](https://www.wsprnet.org/drupal/wsprnet/spotquery) nach **jedem exakten Rufzeichen**. Prüfe Empfangsberichte und nicht nur die Karte, die einen zuletzt bekannten Locator anzeigen kann.
3. Prüfe das vorgesehene grid-4, die gemeldete Leistung, die Zeitstempel und die getrennten Frequenzen. Suche Zyklen, in denen **derselbe entfernte Empfänger beide Rufzeichen gemeldet hat**.
4. Führe einen kurzen **TX Benchmark** mit diesen Identitäten, diesem Band und diesem UTC-Zeitfenster durch. Warte, bis die Empfangsberichte in der ausgewählten Datenbank verfügbar sind. wspr.live beschreibt Verzögerungen von einigen Minuten; einzelne Uploads und die Verfügbarkeit des Dienstes können länger dauern. Richte dich nach der tatsächlichen Datenverfügbarkeit statt nach einer festen Wartezeit; siehe [Abschnitt 11.6](#sec-6-6).
5. Prüfe die Anzahlen gepaarter (**Paired**) und einseitiger Dekodierungen, ΔSNR und das aus den gemeinsamen Dekodierzahlen berechnete ΔDecode. Untersuche unerwartete Häufungen von Only Target oder Only Reference, bevor du sie als Performance-Unterschied wertest.

**Prüfe bei einer erweiterten Folge jede Phase getrennt.** Ordne die Positionen in der Folge anhand ihrer Zeitstempel und deines dokumentierten Zeitplans zu, mit exportierten Beobachtungsdaten oder einem externen Dekoderprotokoll. Vergleiche die Anzahlen gepaarter und einseitiger Beobachtungen, ΔSNR und ΔDecode zwischen diesen Positionen. Anhaltende Unterschiede können Anlass geben, Rufzeichen-Hash-Auflösung, Frequenzplatzierung, Erwärmung und Leistungsabfall zu prüfen. Die Datenbank muss Type 2 oder Type 3 nicht kennzeichnen, und WSPRadar stellt weder Kennzeichnungen der Nachrichtenphase noch einen Phasenfilter bereit.

**Bereit zum Messen:** Beide exakten Identitäten erscheinen beständig an ihren tatsächlichen Standorten, gemeinsame Empfänger melden beide Signale in den vorgesehenen Zyklen, und ungeklärte Effekte der Nachrichtenphase oder Frequenzposition wurden untersucht. Beginne nach diesen Prüfungen einen neuen Messzeitraum. Eine erfolgreiche Vorabprüfung belegt den Datenfluss für die geprüfte Hardware, Firmware, Dekoder und Datenquelle; sie allein belegt keinen Antennenvorteil.



<a id="sec-simultaneous-tx-setup-5"></a>
#### 5.5 Gerätespezifische Einrichtung

Wähle unten die Anleitung für deine Geräte und schließe anschließend die gemeinsamen Leistungs- und Signalprüfungen in [5.3](#sec-simultaneous-tx-setup-3) sowie die Datenbankprüfung in [5.4](#sec-simultaneous-tx-setup-4) ab. Dokumentiere die Firmware und Einstellungen, mit denen die Prüfungen bestanden wurden. Wiederhole diese Prüfungen nach Änderungen an Firmware, Zeitsteuerung, Frequenz, Leistung oder Nachrichtenformat.



<a id="sec-simultaneous-tx-setup-5-1"></a>
<a id="sec-simultaneous-tx-setup-5-2"></a>
##### 5.5.1 QMX und QMX+ Virtual U3S sowie Ultimate3S

Verwende ein Gerät für Target und eines für die Referenz. Beide Produkte unterstützen bis zu 16 Einträge; **beginne jedoch mit einem WSPR-Eintrag auf jedem Gerät**. Dieser Eintrag sendet je nach unten gewählter Rufzeichenvariante entweder eine Type-1-Nachricht oder automatisch ein Type-2-/Type-3-Paar. Ihre HF-Hardware unterscheidet sich; Unterschiede bei Oszillator, Filterung und Endstufe bleiben deshalb Teil der verglichenen Signalwege <a href="#ref-12">[Ref-12]</a>.

Prüfe zunächst Hardware und Firmware wie unten beschrieben. Wähle anschließend [zwei verschiedene Rufzeichen](#sec-qrp-two-distinct-callsigns) oder [ein Rufzeichen mit zwei Suffixen](#sec-qrp-one-callsign-two-suffixes). Beide Verfahren verwenden danach die [gemeinsamen Schritte für Leistung, Frequenz und Prüfung](#sec-qrp-common-setup).

**1. Hardware und Firmware prüfen.**

Mit dem physischen Ultimate3S ist hier der Bausatz mit dem Si5351A-Synthesizer gemeint. Der ursprüngliche Ultimate3 mit AD9850 sendet die erweiterten WSPR-Nachrichten abwechselnd in getrennten Sendezyklen statt unmittelbar aufeinanderfolgend und ist deshalb kein idealer Kandidat für die unten beschriebene Anleitung mit erweiterten Nachrichten.

Verwende ein Band, das beide Geräte unterstützen. Prüfe beim QMX die Hardwarevariante und Bandkonfiguration; bestücke einen physischen Ultimate3S mit dem richtigen Ausgangstiefpassfilter bzw. wähle diesen aus.

Für QMX/QMX+ kennzeichnet die [offizielle Firmwarehistorie](https://www.qrp-labs.com/qmx.html) mit Stand **25. Oktober 2026** `1_04_010` als stabile Version; später aufgeführte Versionen sind Betaversionen. Die erste Version `1_04_000` war ausschließlich für QMX+ vorgesehen. Version `1_04_009` korrigierte WSPR-Aussendungen **250 Hz unterhalb der vorgesehenen Frequenz**, und `1_04_010` enthält weitere Korrekturen für Virtual U3S. Verwende eine unterstützte Version mit diesen Korrekturen und prüfe beim Aktualisieren die Versionshistorie.

Diese Anleitung bezieht sich auf das Virtual-U3S-Handbuch für Firmware `1_04_008` (Dokumentrevision `1_04_008a`) und das Ultimate3S-Handbuch für Firmware `v3.12a` (Datei `operation3.12a2.pdf`). Beim physischen U3S führte Firmware `v3.12` die aufeinanderfolgende Aussendung erweiterter Nachrichten ein; setze bei älterer Firmware nicht dasselbe Verhalten voraus <a href="#ref-12">[Ref-12]</a>.

<a id="sec-qrp-two-distinct-callsigns"></a>
###### 5.5.1.1 Zwei verschiedene Rufzeichen

Verwende dieses Verfahren für zwei gültige gewöhnliche Rufzeichen, unabhängig davon, ob sie zwei Aufbauten an einer Station oder zwei getrennte Stationen kennzeichnen, wie in [Abschnitt 5.1.1](#sec-tx-two-distinct-callsigns) beschrieben.

1. Trage unter **Callsign** das eigene vollständige gewöhnliche Rufzeichen jedes Geräts ein.
2. Trage für jeden Aufbau seinen tatsächlichen **Locator mit sechs Zeichen** ein. Type 1 überträgt dessen erste vier Zeichen.
3. Setze bei Virtual U3S **`Extended WSPR = DISABLED`**. Setze beim Ultimate3S **`XW = 0`**.
4. Verwende **nur Eintrag `0`**, Mode **`WSPR`**, **`Frame = 20` Minuten** und **`Start = 04`** und führe anschließend die gemeinsamen Schritte unten aus.

Mit dem einzelnen Type-1-Eintrag werden Starts zu **`:04`, `:24` und `:44` in jeder Stunde** erwartet. Bei jedem Start sollten beide Signale vorhanden sein. Dies nutzt **3 der 30 zweiminütigen Zyklen pro Stunde: 10% Zyklusbelegung**.

<a id="sec-qrp-one-callsign-two-suffixes"></a>
###### 5.5.1.2 Ein Rufzeichen mit zwei Suffixen

Verwende dieses Verfahren für zwei Aufbauten, die durch ein Basisrufzeichen und zwei gültige Suffixe gekennzeichnet werden, wie in [Abschnitt 5.1.2](#sec-tx-one-callsign-two-suffixes) beschrieben.

1. Trage in der Einstellung **Callsign** jedes Geräts das **vollständige Rufzeichen mit Suffix** ein, beispielsweise `CALL/1` für Target und `CALL/2` für die Referenz. Ersetze `CALL` durch dein tatsächliches Basisrufzeichen und verwende nur gültige Sendesuffixe, die von der Firmware unterstützt werden.
2. Trage für jeden Aufbau seinen tatsächlichen **Locator mit sechs Zeichen** ein. Type 3 überträgt alle sechs Zeichen.
3. Setze bei Virtual U3S **`Extended WSPR = ENABLED`**. Setze beim Ultimate3S auf beiden Geräten **`XW = 1`**.
4. Verwende **nur Eintrag `0`**, Mode **`WSPR`**, **`Frame = 20` Minuten** und **`Start = 04`** und führe anschließend die gemeinsamen Schritte unten aus. Lege keine getrennten Einträge für Type 2 und Type 3 an: Unterstützte Firmware erzeugt beide automatisch.

Plane **vier Minuten pro Eintrag** ein. Für den einzelnen Eintrag wird folgender Zeitplan erwartet:

| Position in der Folge | Erwartete UTC-Minuten auf beiden Geräten |
|---|---|
| Type 2: vollständiges zusammengesetztes Rufzeichen und Leistung | `04, 24, 44` |
| Type 3: Identität als Hash, grid-6 und Leistung | `06, 26, 46` |

Wenn diese Wiederholung eingehalten wird, verwendet jeder Sender **6 der 30 zweiminütigen Zyklen pro Stunde: 20% Zyklusbelegung**. Die 10% des Type-1-Verfahrens gelten hier nicht. Halte beide Geräte in den entsprechenden Nachrichtenphasen und lasse das vollständige Paar auf einer Frequenz, bevor du die Frequenz änderst. Prüfe vor der Messung die vollständige erweiterte Folge und die daraus entstehenden Datenbankidentitäten <a href="#ref-12">[Ref-12]</a>.

<a id="sec-qrp-common-setup"></a>
###### 5.5.1.3 Gemeinsame Schritte für Leistung, Frequenz und Prüfung

**Tatsächliche Leistung und einen Sendeeintrag einstellen.**

Bearbeite die TX-Spalte `0` in der Virtual-U3S-Zeitplantabelle oder den Mode-Bildschirm `0` am physischen Ultimate3S.

Trage das Rufzeichen und den tatsächlichen Locator mit sechs Zeichen für das gewählte Verfahren ein. Behalte während des gesamten Experiments die Zuordnung jedes Rufzeichens zu seinem Target- oder Referenzsignalweg bei.

Bei Virtual U3S steuert `PA Voltage` die tatsächliche HF-Ausgangsleistung: `6.0 V` ist bei einem für 12 V aufgebauten QMX ein ungefährer Ausgangspunkt für 1 W; andere Aufbauten und Bänder weichen ab. Miss das Ergebnis. Verwende für deutlich geringere Leistung geeignete externe Dämpfung und miss dahinter; das QMX-Haupthandbuch rät davon ab, allein durch Spannungsabsenkung weniger als etwa 1 W erzielen zu wollen. Stelle die Ausgangsleistung des physischen Ultimate3S mit seiner dokumentierten Hardwarekonfiguration oder externer Dämpfung ein.

Trage anschließend den nächstgelegenen gültigen codierten dBm-Wert ein: `20`, `23`, `27` und `30 dBm` entsprechen ungefähr `100`, `200`, `500 mW` und `1 W`. Das Feld `Power/Speed` von Virtual U3S und das WSPR-Leistungsfeld des Ultimate3S **melden die Leistung in der Nachricht; ihre Änderung stellt die HF-Ausgangsleistung nicht ein**. Wähle den Messpunkt wie in [5.3](#sec-simultaneous-tx-setup-3) beschrieben <a href="#ref-12">[Ref-12]</a>.

| Einstellung | Ausgangswert auf beiden Geräten |
| --- | --- |
| Aktivierte Einträge | Nur Eintrag `0`; deaktiviere alle anderen Einträge |
| Mode | `WSPR` |
| Erweiterte Nachrichten | Verwende die oben genannte Einstellung für die gewählte Rufzeichenvariante |
| `Frame` | `20` Minuten |
| `Start` | `04` Minuten |
| UTC | Korrekt und gegen die Zeitreferenz geprüft |

Beide Produkte behandeln `Start = 00` als unbenutzt. Trage deshalb eine andere gerade Startminute ein, beispielsweise `04`.

Wähle unten **ein** Band. Lege Target zunächst auf die untere Frequenz und die Referenz auf die obere. Behalte jede Frequenz während der vollständigen Nachricht oder des erweiterten Paars bei. Diese Einstellungen sind **HF-Signalmittenfrequenzen**, keine USB-Einstellfrequenzen und nicht der niedrigste WSPR-Ton.

| Band | Untere Signalmitte | Obere Signalmitte |
| --- | ---: | ---: |
| 40 m | `7.040050 MHz` | `7.040150 MHz` |
| 20 m | `14.097050 MHz` | `14.097150 MHz` |

Die Signalmitten liegen 100 Hz auseinander; jede liegt 50 Hz vom näheren Rand des 200 Hz breiten WSPR-Unterbands entfernt. Bestätige, dass die vollständigen abgestrahlten Signale darin bleiben <a href="#ref-12">[Ref-12]</a>.

Beim QMX geht die Uhrzeit bei `Real time clock = Software` verloren, wenn die Stromversorgung getrennt wird; übernimm UTC nach dem Einschalten erneut vom GPS oder stelle die Uhrzeit manuell ein. Damit die Uhr im ausgeschalteten QMX+ weiterläuft, sind `Real time clock = QMX+ Internal` und eine eingesetzte CR2032-Batterie erforderlich. Diese Auswahl der Uhrenquelle ist unabhängig von `GPS source`; die Auswahl des internen GPS allein sorgt nicht dafür, dass die Uhr im ausgeschalteten Zustand weiterläuft.

**Starten, eine Stunde beobachten, dann den Vergleich aufzeichnen.**

Prüfe vor dem Start UTC. Setze bei Virtual U3S die Haupteinstellung `Enable` auf `ENABLED` und verlasse das Menü; verwende beim Ultimate3S die Start-Aktion der rechten Taste, um in den Run-Modus zu wechseln. Beobachte den oben beschriebenen Zeitplan für das gewählte Verfahren; beide Geräte müssen die entsprechenden Phasen gemeinsam senden.

Wenn du GPS-Frequenzkalibrierung verwendest, stelle sicher, dass sie vor dem nächsten erwarteten Start beendet ist.

Setze bei einem internen QLG3 im QMX+ `GPS source = QMX+ Internal`. Wähle für ein externes GPS am QMX `GPS source = Paddle port` und verbinde gemäß der Anschlussanleitung des Herstellers das 1-PPS-Signal mit der Spitze des Klinkensteckers und die seriellen NMEA-Daten mit 9600 Baud mit dessen Ring. Versorge das GPS-Modul separat mit Strom; der QMX stellt über diesen Anschluss keine Stromversorgung dafür bereit.

Beim physischen U3S erfordert die Kalibrierung einen `Cal Step` ungleich null und eine Leerlaufpause, die länger als `Cal Time + 4 seconds` ist; eine GPS-Verbindung allein belegt keine erfolgreiche Kalibrierung. Schließe sowohl die seriellen NMEA-Daten als auch 1 PPS an, damit UTC und Locator automatisch eingestellt werden und die Frequenz kalibriert werden kann. Verwende unter `GPS {Mode Baud}` die Einstellung `Mode = 2` für einen Empfänger, dessen Zeitreferenz die steigende PPS-Flanke ist, und passe `Baud` an dessen serielle Ausgabe an, üblicherweise `009,600`. PPS allein liefert weder UTC noch den Locator.

Beobachte die Sendefrequenzen und Starts, auch nach einem Neustart. Schließe die Prüfungen der einzelnen Geräte, der simultanen Signale und der Datenbank in [5.3–5.4](#sec-simultaneous-tx-setup-3) ab. Beginne den Messzeitraum erst, wenn beide exakten Identitäten in den vorgesehenen Zyklen und an den vorgesehenen Standorten erscheinen. Wiederhole den Versuch anschließend mit **vertauschten Frequenzzuordnungen** nach [5.6](#sec-simultaneous-tx-setup-6), damit das Ergebnis nicht an eine dauerhafte Zuordnung unten/oben gebunden ist.

**Optional: Frequenztausch mit zwei Einträgen für das Verfahren mit zwei gewöhnlichen Rufzeichen.**

Behalte dieselben Rufzeichen, dasselbe Band und dieselbe gemessene Leistung bei und aktiviere zwei WSPR-Einträge pro Gerät:

| Eintrag | Target-Signalmitte | Referenz-Signalmitte |
| --- | --- | --- |
| `0` | Unten | Oben |
| `1` | Oben | Unten |

Verwende `Frame = 20`, `Start = 04` als **Ausgangskonfiguration am Messplatz**. Zeichne vor der Verwendung eine volle Stunde lang die tatsächliche Eintragsreihenfolge und die UTC-Starts beider Geräte auf. Der vorgesehene Ablauf ist Eintrag 0 zu `:04/:24/:44` und Eintrag 1 zu `:06/:26/:46`. **Nur wenn dieser Ablauf beobachtet wird**, liefert der Aufbau benachbarte Paare und 6 von 30 Zyklen, also `20%` Belegung. Die Handbücher geben diesen genauen Ablauf mit zwei Einträgen nicht für jede installierte Version an; wenn Eintrag 1 auf einen späteren Frame wartet, erfolgt auch der Frequenztausch später. Kläre diese Zeitsteuerung oder kehre zur Anleitung mit einem Eintrag zurück.

Vergleiche beide Frequenzpositionen getrennt. Ihre ausgeglichene Nutzung hilft, einen festen Vorteil einer Frequenzposition durch QRM oder die Geräte aufzudecken oder zu verringern; sie belegt jedoch nicht, dass sämtliche Frequenzeffekte verschwunden sind.

Verwende für das Verfahren mit einem Rufzeichen und zwei Suffixen den Frequenztausch zwischen Analyseläufen in [5.6](#sec-simultaneous-tx-setup-6). Ein erweiterter Eintrag verwendet bereits zwei Zyklen; ein zweiter erweiterter Eintrag verändert die Länge der Folge und die Belegung. Der Ablauf des gewöhnlichen Verfahrens und die obige 20%-Berechnung gelten deshalb nicht. Bewahre das vollständige Type-2-/Type-3-Paar, bevor du die Frequenz änderst.



<a id="sec-simultaneous-tx-setup-5-3"></a>
##### 5.5.2 ZachTek-Firmware 2.19

Dieser Aufbau nutzt die integrierte Zeitsteuerung und die standardmäßige zufällige Frequenzwahl von ZachTek; **eine angepasste Firmware mit getrennten Frequenzfenstern ist nicht erforderlich**. Das ausgearbeitete Beispiel verwendet die auf eine bestimmte Revision festgelegte ESP8285-Firmware in [Ref-29](#ref-29), Revision `1657468ea27052167191a7deda2440a535567ecd`, die **WSPR-TX XP Plus, `Product_Model = 1048`** auswählt. Andere Modelle erfordern eine gesondert geprüfte Anleitung. In dieser Datei ist der Sleep-Aufruf für lange Pausen bei Mini/Pico deaktiviert, und beim Pico erzwingt der Start die Höhenmeldung; die folgenden Pausen- und Leistungsanweisungen gelten daher für den ausgewählten 1048-Build.

Verwende die Konfigurationssoftware für deine genaue Hardware und installierte Firmware. Die folgenden Parameternamen entsprechen dem zitierten Quellcode; sie sind keine Aufforderung, Firmware zu bearbeiten oder zu kompilieren. **WSPRadar hat diese Anleitung nicht an ZachTek-Hardware validiert.** Die Erläuterung des Herstellers stützt die Nutzung der vorhandenen Zeitsteuerung und zufälligen Frequenzwahl; sie ist keine Validierung sämtlicher nachfolgender modellspezifischer Einstellungen.

Wähle das Verfahren passend zu den **Sendekennungen im Funkbetrieb**, die du verwenden wirst:

| Verfahren | Identitäten und Nachrichtenmuster |
|---|---|
| [**1. Zwei verschiedene Rufzeichen**](#sec-zachtek-two-ordinary-callsigns) | Zwei verschiedene gültige Type-1-Rufzeichen, verwendet von zwei Aufbauten an einer Station oder von zwei Stationen. Jede geplante Folge enthält eine Aussendung pro Aufbau. |
| [**2. Ein Basisrufzeichen mit zwei Suffixen**](#sec-simultaneous-tx-setup-5-3-2) | Ein Basisrufzeichen mit zwei verschiedenen zulässigen Suffixen aus jeweils einem Zeichen. Jede geplante Folge enthält ein Type-2-/Type-3-Paar pro Aufbau. |

**Beide Verfahren erfordern dieselbe Vorbereitung:** Aktiviere nur das ausgewählte Versuchsband, setze **`PowerOption = Normal`** und verwende das tatsächliche QTH jedes Senders. Beide Geräte benötigen gültige GPS-Zeit **und GPS-Position**, auch wenn der gesendete Locator manuell eingegeben wird. Die normale Leistungsmeldung verwendet den eingestellten dBm-Wert als Nachrichtendaten; sie stellt nicht die HF-Ausgangsleistung ein. Der Höhenmodus ersetzt diesen Wert durch Telemetrie. Miss vor dem Sendebetrieb die tatsächliche Leistung und wähle ihren codierten Wert wie in [Abschnitt 5.3](#sec-simultaneous-tx-setup-3) beschrieben.

Zwei Aufbauten am selben Standort sollten ihr gemeinsames tatsächliches QTH melden. Bei zwei unterschiedlichen Stationen meldet jeder Sender sein eigenes QTH; das Ergebnis vergleicht die vollständigen installierten Stationen und ihre unterschiedlichen Funkpfade. Halte im Versuchsprotokoll fest, welches vollständige Rufzeichen und welcher Locator zu welchem Signalweg gehören.

Schließe nach der Konfiguration einer der beiden folgenden Varianten das gemeinsame Verfahren **Zeitsteuerung → Messplatz → Sendebetrieb** in [Abschnitt 5.5.2.3](#sec-simultaneous-tx-setup-5-3-1) ab. Behalte auf beiden Geräten die standardmäßige zufällige Frequenzwahl bei; eine Zuordnung zu einem unteren und oberen Frequenzfenster ist nicht erforderlich.

<a id="sec-zachtek-two-ordinary-callsigns"></a>
###### 5.5.2.1 Zwei verschiedene Rufzeichen

Verwende dieses Verfahren, wenn Target und Referenz jeweils ein anderes gültiges Rufzeichen haben, das in das gewöhnliche Type-1-WSPR-Format passt. Die Rufzeichen können zwei zulässige Aufbauten an einer Station oder zwei getrennte Stationen kennzeichnen; sie benötigen keine Suffixe, um unterscheidbar zu sein.

**Beide Geräte konfigurieren:**

1. Trage das gewöhnliche Target-Rufzeichen in das Basisrufzeichenfeld des Target-Geräts und das andere gewöhnliche Referenz-Rufzeichen in das entsprechende Feld des Referenzgeräts ein.
2. Wähle ausdrücklich **no prefix/suffix** (`SuPreFixOption = None` im zitierten Quellcode). Tue dies auch, wenn das angezeigte Basisrufzeichen bereits gewöhnlich ist: Nur diesen Text zu ändern deaktiviert kein zuvor ausgewähltes Suffix oder Präfix. Gespeicherte Suffixzeichen können unbenutzt erhalten bleiben; der Auswahlschalter entscheidet über Type 1.
3. Setze auf beiden Geräten **`LocationPrecision = 4`**. Die Genauigkeit `6` würde auch bei einem gewöhnlichen Rufzeichen eine Type-3-Aussendung hinzufügen.
4. Aktiviere dasselbe einzelne Versuchsband, verwende **`PowerOption = Normal`**, behalte das tatsächliche QTH jedes Geräts bei und setze auf beiden **`TimeSlotCode = 7`** sowie **`TXPause = 480` Sekunden**.
5. Behalte auf beiden Geräten die standardmäßige zufällige Frequenzwahl bei und fahre mit [Abschnitt 5.5.2.3](#sec-simultaneous-tx-setup-5-3-1) fort. Behalte die Zuordnung der Rufzeichen zu ihren dokumentierten physischen Signalwegen bei.

Der vorgesehene Zeitplan wiederholt sich alle zwanzig Minuten:

| UTC-Minute in jeder Stunde | Target | Referenz |
|---|---|---|
| `04, 24, 44` | Type 1: eigenes Rufzeichen, grid-4 und Leistung | Type 1: eigenes Rufzeichen, grid-4 und Leistung |
| `06, 26, 46` | Keine zusätzliche Phase bei diesem Verfahren | Keine zusätzliche Phase bei diesem Verfahren |

Wenn diese Wiederholung eingehalten wird, verwendet jeder Sender **3 von 30 WSPR-Zyklen pro Stunde: 10%** der verfügbaren Zyklen. `TXPause` beginnt nach jeder Type-1-Aussendung; es plant keine zusätzlichen Aussendungen im Abstand von acht Minuten. Bestätige die tatsächlichen Starts und führe anschließend die gemeinsamen Messplatz- und Datenbankprüfungen durch, bevor du den Messzeitraum beginnst. <a href="#ref-29">[Ref-29]</a>

<a id="sec-simultaneous-tx-setup-5-3-2"></a>
###### 5.5.2.2 Ein Rufzeichen mit zwei Suffixen

Verwende dieses Verfahren, wenn zwei Sendeaufbauten ein Basisrufzeichen mit zwei verschiedenen gültigen Suffixen verwenden. `CALL/1` und `CALL/2` veranschaulichen das Identitätsmuster; ersetze `CALL` durch dein tatsächliches Rufzeichen und verwende nur Suffixe, die für Operator, Station und Betrieb zulässig sind. Verwende in dieser festgelegten Firmware **Suffixe aus einer einzelnen Ziffer oder einem einzelnen Buchstaben**.

**Beide Geräte konfigurieren:**

1. Trage in das Basisrufzeichenfeld jedes Geräts dasselbe Basisrufzeichen ein, ohne Schrägstrich oder Suffix.
2. Wähle auf beiden Geräten die **Suffixoption** (`SuPreFixOption = Sufix` im Quellcode). Trage in das separate Suffixfeld jedes Geräts ein anderes zulässiges Suffix aus einem Zeichen ein. Dokumentiere, welche vollständige Sendekennung zu Target und welche zur Referenz gehört.
3. Setze auf beiden Geräten **`LocationPrecision = 6`**. Damit wird Type 3 automatisch nach Type 2 hinzugefügt; die Genauigkeit `4` würde nur Type 2 senden. Du schaltest die Nachrichtentypen nicht von Hand um.
4. Aktiviere dasselbe einzelne Versuchsband, verwende **`PowerOption = Normal`**, behalte das tatsächliche QTH jedes Geräts bei und setze auf beiden **`TimeSlotCode = 7`** sowie **`TXPause = 480` Sekunden**.
5. Behalte auf beiden Geräten die standardmäßige zufällige Frequenzwahl bei und fahre mit [Abschnitt 5.5.2.3](#sec-simultaneous-tx-setup-5-3-1) fort. Behalte die Zuordnung der vollständigen Rufzeichen mit Suffix zu ihren dokumentierten physischen Signalwegen bei.

Der vorgesehene Zeitplan wiederholt sich alle zwanzig Minuten:

| UTC-Minute in jeder Stunde | Target | Referenz |
|---|---|---|
| `04, 24, 44` | Type 2: eigenes vollständiges Rufzeichen mit Suffix und Leistung | Type 2: eigenes vollständiges Rufzeichen mit Suffix und Leistung |
| `06, 26, 46` | Type 3: eigene Identität als Hash, grid-6 und Leistung | Type 3: eigene Identität als Hash, grid-6 und Leistung |

Wenn diese Wiederholung eingehalten wird, verwendet jeder Sender **6 von 30 WSPR-Zyklen pro Stunde: 20%** der verfügbaren Zyklen. Beide Phasen verwenden innerhalb dieser Folge dieselbe ausgewählte Frequenz. Die zweite Nachricht folgt nach einer festen Pause von neun Sekunden auf das Ende der ersten; ihr Start wird nicht gesondert gegen den GPS-Zeitschlitz geprüft. Die konfigurierte `TXPause` folgt auf das vollständige Paar und ist nicht die Lücke zwischen dessen beiden Phasen.

**Behalte die Grenzen des Quellcodes im Blick.** Die Type-3-Hash-Bildung für zweistellige Ziffernsuffixe ist deaktiviert. Der präfixbasierte Type-3-Codepfad baut zudem seine Rufzeichenzeichenfolge neu auf, ohne vor dem Hashen die abschließende Null zu schreiben; deshalb ist er in dieser Revision kein zuverlässiges Verfahren. Die obige Variante mit einem Suffix aus einem Zeichen verwendet den implementierten Bildungspfad. <a href="#ref-29">[Ref-29]</a>

Beobachte, dass die entsprechenden Type-2- und Type-3-Phasen gemeinsam stattfinden, auch nach einem Neustart. Prüfe nach [Abschnitt 5.4](#sec-simultaneous-tx-setup-4) beide vollständigen Identitäten in den Empfänger- bzw. Datenbankbeobachtungen für beide Phasen. Übereinstimmende Konfigurationswerte allein belegen weder korrekte Hash-Auflösung noch vollständige synchronisierte Aussendungen.

<a id="sec-simultaneous-tx-setup-5-3-1"></a>
###### 5.5.2.3 Gemeinsame Zeitsteuerung, zufällige Frequenzwahl und Prüfung

**Zeitplan und Pause aufeinander abstimmen.** Beide ausgearbeiteten Verfahren verwenden Code `7`. Wenn du einen anderen festen Start wählst, gleiche `TimeSlotCode` auf beiden Geräten ab und verwende die folgenden Regeln:

| `TimeSlotCode` | Zeitplan der ersten Nachricht, sobald das Gerät bereit ist |
|---|---|
| `0–4` | Wiederholung alle 10 Minuten. Code `0`: `00, 10, 20, 30, 40, 50`; Code `1`: `02, 12, 22, 32, 42, 52`; bis Code `4`: `08, 18, 28, 38, 48, 58`. |
| `5–14` | Wiederholung alle 20 Minuten. Code `5`: `00, 20, 40`; Code `6`: `02, 22, 42`; Code `7`: `04, 24, 44`; bis Code `14`: `18, 38, 58`. |

`TXPause` ist eine Wartezeit in **Sekunden nach dem Durchlauf der aktivierten Bänder**, kein Zeitraum von Start zu Start. Bei einem aktivierten Band folgt sie auf jede vollständige Folge aus einer oder zwei Nachrichten. Lasse genügend Zeit, um die Folge zu beenden, die Pause einzuhalten und vor dem nächsten geplanten Start wieder bereit zu sein. Eine Pause von acht Minuten nach einer Folge aus zwei Nachrichten kann den nächsten Zehn-Minuten-Start auslassen; die ausgearbeiteten Zwanzig-Minuten-Zeitpläne lassen Raum für ihre Nachrichten und diese Pause.

Verwende für diese Anleitungen die obigen festen Codes. Code `16` erlaubt den nächsten verfügbaren Start in einer geraden Minute; Code `17` reagiert auf eine geänderte Position oder den Beginn einer Stunde. Keiner von beiden stellt die hier verwendete ausgewählte feste Wiederholung her. Die zufällige Frequenzwahl wählt nicht die Zeitschlitze aus; prüfe deshalb bei der Vorabprüfung die tatsächlichen Starts beider Sender. <a href="#ref-29">[Ref-29]</a>

**Die standardmäßige zufällige Frequenzwahl verwenden.** Die Originalfirmware zieht einen ganzzahligen Versatz von **−100 bis einschließlich +99 Hz** um die nominale Frequenz des Bands. Behalte dieses Standardverhalten auf beiden Geräten bei, statt getrennte Frequenzfenster zuzuweisen. <a href="#ref-29">[Ref-29]</a>

Nach Auskunft von **Harry Zachrisson (ZachTek, persönliche Mitteilung)** initialisiert jedes Gerät beim Einschalten seinen Zufallszahlengenerator mit **thermischem Rauschen, das der eingebaute Analog-Digital-Wandler (ADC) erfasst**. Der Startwert stammt aus Rauschen, nicht aus einer Temperaturmessung. Dadurch sollen die Sender auch bei gleichzeitigem Einschalten unterschiedliche Folgen von Sendefrequenzen verwenden; ein übereinstimmender Sendezeitplan erzwingt keine übereinstimmende Frequenzwahl.

**Gelegentliche Überlappungen bleiben möglich.** Unterschiedliche Startwerte garantieren nicht, dass in jeder Folge verschiedene Frequenzen gewählt werden. Unter der Annahme unabhängiger, gleichverteilter Ziehungen aus den 200 Ein-Hertz-Versätzen dieses Quellcodes beträgt die Wahrscheinlichkeit für **genau denselben Versatz 0,5% je neuer Ziehung**; Versätze mit **höchstens 5 Hz Abstand treten mit ungefähr 5,4% Wahrscheinlichkeit** auf. Diese berechneten Beispiele beschreiben die Frequenznähe zwischen den beiden Versuchssendern, keine gemessene Störungsrate, keinen sicheren Mindestabstand und keine Schätzung des SNR-Fehlers. Unabhängige zufällige Frequenzwahl macht dauerhaft identische Frequenzfolgen unwahrscheinlich, garantiert aber keinen Mindestabstand.

Die Versätze beziehen sich auf die **Mitte** des 200 Hz breiten WSPR-Sendeunterbands: beispielsweise `7.040100 MHz` auf 40 m oder `14.097100 MHz` auf 20 m. Bestätige, dass beide Geräte dieselbe korrekte nominale Frequenz verwenden. In dieser Firmware ist `freq` **Ton 0**, die niedrigste der vier gesendeten Tonfrequenzen, und verwendet **Einheiten von 0,01 Hz**. Oszillatorfehler, Drift und tatsächliche spektrale Breite erfordern weiterhin Messungen. <a href="#ref-29">[Ref-29]</a>

Jede neue Folge zieht erneut eine Frequenzposition; aufeinanderfolgende Ziehungen **können denselben Wert ergeben**. Wenn die Genauigkeit `6` Type 3 hinzufügt, verwendet dieser Partner **dieselbe ausgewählte Frequenz** wie die vorhergehende Type-1- oder Type-2-Nachricht. Die nächste Ziehung erfolgt nach dem nächsten `NextFreq()`; die Versätze addieren sich nicht auf. <a href="#ref-29">[Ref-29]</a>

**Die Konfiguration dokumentieren.** Prüfe das genaue Hardwaremodell und die Revision, die werkseitige Oszillatorkalibrierung und die installierte Filterkonfiguration. Dokumentiere die installierte Firmwareversion und sämtliche Einstellungen des Experiments. Der zitierte Quellcode wählt Modell `1048`; installiere diesen Build nicht auf einem anderen Modell, nur um dieses Beispiel nachzustellen. Behalte die für deine Hardware vorgesehene Herstellerfirmware bei.

**Am Messplatz prüfen, dann im Sendebetrieb.** Prüfe nach der Konfiguration jedes Gerät einzeln an geeigneten Lasten oder mit einer sicher gedämpften Messanordnung; bei Geräten am selben Standort prüfe außerdem beide gemeinsam. Prüfe tatsächliche Frequenzplatzierung, vollständigen zeitlichen Nachrichtenablauf, Ausgangsleistung, Filterung und spektrale Reinheit, bevor du Antennen anschließt. Untersuche bei Geräten an getrennten Stationen den simultanen Empfang während der anschließenden Vorabprüfung im Sendebetrieb an einem gemeinsamen Empfänger. Verwende dieselben Bedingungen für die PC-Steuerung, die für den Versuch geplant sind; Steuerbefehle können in dieser Firmware eine Aussendung unterbrechen.

Schließe die [Datenbank-Vorabprüfung aus Abschnitt 5.4](#sec-simultaneous-tx-setup-4) mit der vorgesehenen niedrigen Sendeleistung ab. Bestätige, dass beide Identitäten das vorgesehene Band verwenden, sich die Frequenzpositionen über mehrere Folgen hinweg verändern und gemeinsame Empfänger in den vorgesehenen Zyklen Spot-Paare liefern. Wiederhole die Start- und Frequenzprüfungen nach einem Neustart. Untersuche dauerhaft identische Frequenzwahlen oder unerwartete zeitliche Abläufe, bevor du den Messzeitraum beginnst.

**Durch Wiederholung oder Hardware-Kreuztausch bestätigen.** Beide Geräte verwenden denselben Bereich für die zufällige Frequenzwahl; es gibt deshalb keine festen unteren und oberen Frequenzzuordnungen zu vertauschen. Verwende einen neuen Messzeitraum und tausche, soweit praktikabel, die untersuchten Antennen oder Bauteile zwischen den Sendeketten. Dokumentiere dabei, welche gemeldete Station zu welchem Bauteil gehört. Verwende [Abschnitt 5.6](#sec-simultaneous-tx-setup-6), um den wiederholten Aufbau oder Kreuztausch zu dokumentieren.



<a id="sec-simultaneous-tx-setup-6"></a>
#### 5.6 Durch Tausch oder Kreuztausch bestätigen

Nutze den ersten Analyselauf, um ein Muster zu erkennen, das bestätigt werden sollte. Verwende für den nächsten physischen Versuch einen **neuen UTC-Zeitraum** mit vergleichbarer Dauer und Abdeckung der Tageszeiten. Behalte das vorgesehene Band, den Zeitplan, die Leistungen, Filter und den primären Auswertungsumfang bei und dokumentiere unvermeidbare Änderungen.

| Kontrolle | Was zu ändern ist | Was sich damit besser unterscheiden lässt |
|---|---|---|
| **Frequenztausch** | Vertausche bei Aufbauten mit steuerbarer Frequenzzuordnung die unteren und oberen festen Positionen, während du die dokumentierten physischen Signalwege beibehältst. | Ein Effekt, der der Frequenzposition folgt, etwa durch schmalbandige Störungen, die Durchlasskurve des Empfängers oder frequenzabhängiges Senderverhalten. |
| **Hardware-Kreuztausch, soweit praktikabel** | Tausche die Antennen oder untersuchten Bauteile zwischen den Sendeketten. Dokumentiere für jeden Lauf die Zuordnung der Identitäten zu den Bauteilen. | Ein Effekt, der dem untersuchten Bauteil folgt, gegenüber einem Effekt, der der Sendekette folgt. |

Bei einem QRP-Labs-Aufbau, der bereits einen überprüften Frequenztausch innerhalb des Laufs verwendet, behalte die Prüfung je Frequenzposition bei und nutze zur Bestätigung eine separate Wiederholung oder einen Hardware-Kreuztausch. Nutze beim ZachTek-Verfahren mit standardmäßiger zufälliger Frequenzwahl eine separate Wiederholung oder einen Hardware-Kreuztausch; es gibt keine festen Frequenzfensterzuordnungen zu vertauschen.

Bewahre die Ergebnisse des ursprünglichen Laufs, des Frequenztauschs und des Hardware-Kreuztauschs getrennt auf. Fasse sie nur zusammen, wenn Target-/Referenzrollen, Korrekturvorzeichen und Analyseumfänge aufeinander abgestimmt wurden. Bewahre die in [Abschnitt 9.3](#sec-8-3) beschriebenen Aufbau- und Betriebsaufzeichnungen auf.

Übereinstimmung in einem neuen kontrollierten Lauf stützt die Wiederholbarkeit des Experiments. Übereinstimmung zwischen zwei Nachrichtenphasen innerhalb eines Laufs ist Übereinstimmung innerhalb eines Analyselaufs. Die Ausbreitung kann sich zwischen den Läufen weiterhin unterscheiden; interpretiere die Bestätigung im Rahmen dessen, was kontrolliert wurde.



<div style="page-break-before: always;"></div>

<a id="sec-b"></a>
<a id="sec-reference-snr-calibration"></a>
### 6. Kalibrierung des Referenz-SNR

**Ziel:** Bestimme einen stabilen Offset des gemeldeten SNR zwischen **zwei Empfangsketten mit gemeinsamem Eingangssignal** und validiere ihn anschließend unabhängig. Entscheide, was das Experiment korrigieren soll: Beim Antennenvergleich können ungleiche nachgeschaltete Empfangsketten eine Korrektur erfordern; wenn die Empfänger selbst untersucht werden, könnte das Subtrahieren dieses Unterschieds hingegen das zu messende Ergebnis entfernen. Ein Beispiel mit gemeinsam genutzter Antenne findet sich in <a href="#ref-2">[Ref-2]</a>.

Dieses Verfahren mit Empfängern und Verteiler begründet keine TX-Korrektur. TX benötigt eine unabhängig bestimmte Grundlage, die zu seinen Sendezweigen und wahrheitsgemäßen Leistungsmeldungen passt; siehe [Abschnitt 8.2.2](#sec-7-benchmark-delta).

1. **Kalibrierungsgrenze festlegen.** Dokumentiere die <strong class="defined-term">Referenzebene</strong>: den entsprechenden Anschlusspunkt in jeder Kette, an dem das gemeinsame Eingangssignal eingespeist wird. Liste die nachgeschalteten Kabel, Filter, Verstärker sowie Empfänger- und Dekodereinstellungen auf. Behalte die Zuordnung jeder exakten Target- oder Referenz-Meldekennung zu ihrer dokumentierten physischen Kette bei.
2. **Gemeinsames Eingangssignal bereitstellen.** Speise beide Ketten gleichzeitig aus einer stabilen Antenne über einen geeigneten Verteiler und kontrollierte Kabel. Charakterisiere die Pegelunsymmetrie der Ausgänge und die Kabelunterschiede und dokumentiere die Zuordnung der Verteilerzweige. Die nominale Verteilerdämpfung allein ist keine SNR-Korrektur.
3. **Unkorrigierte Beobachtungsdaten sammeln.** Wähle in RX Benchmark **SNR-Korrektur der Referenz → Keine Korrektur**; damit werden **0.0 dB** angewendet. Prüfe simultanen Empfang und Uploads und sammle dann Spot-Paare auf dem vorgesehenen Band über die relevanten Signalpegel, bei unveränderten Einstellungen für Verstärkung, Filterung und Dekoder. Zeichne, soweit praktikabel, außerdem einen Kontrolllauf mit vertauschten Verteilerzweigen auf, wobei die Identitäten ihren Empfangsketten zugeordnet bleiben.
4. **Kennzahl und Gewichtung festhalten.** Verwende die ΔSNR-Zusammenfassungen in **Benchmark-Statistik** für den dokumentierten Kalibrierungszeitraum, die Filter und den Analyseumfang. Dokumentiere sowohl die statistische Kennzahl als auch die Gewichtung: Beim **Median der Stationsmediane von ΔSNR** und beim **Mittelwert der Stationsmittelwerte von ΔSNR** zählt jede berücksichtigte Station gleich viel. Bei einem **Median oder arithmetischen Mittelwert aller zusammengefassten qualifizierten Spot-Paare** zählt dagegen jedes berücksichtigte Paar gleich viel. Dokumentiere Stations- und Paarzahlen und verwende bei der anschließenden unabhängigen Prüfung dieselbe Kennzahl und Gewichtung. WSPRadar bestimmt die Korrektur nicht automatisch.
5. **Prüfen, ob eine Konstante gerechtfertigt ist.** Untersuche die Unterschiede nach Station, Zeit und SNR sowie über die Frequenzen und Einstellungen, unter denen die Korrektur verwendet werden soll. Untersuche einen Unterschied, der dem Verteilerzweig folgt. Eine Konstante ist nicht vertretbar, wenn sie sich mit Pegel, Frequenz, AGC, Gerätezustand oder Zeit wesentlich verändert. Behebe Unsymmetrie der Messanordnung, Übersteuerung, instabile Verstärkung oder zeitweilige Fehler der Signalzuordnung und prüfe nach Änderungen am kalibrierten Aufbau erneut.
6. **Vorzeichen anwenden.** Wähle **Dokumentierte Korrektur verwenden** und gib den Wert unter **SNR-Korrektur der Referenz (dB)** ein. Bei einem unkorrigierten Offset Target minus Referenz von **+1.6 dB** gib **+1.6 dB** ein: Das Referenz-SNR steigt und ΔSNR sinkt um 1,6 dB. Gib einen negativen Offset mit seinem negativen Vorzeichen ein. Dokumentierte **0.0 dB** bleiben von **Keine Korrektur** verschieden. Die Korrektur verändert ΔSNR, nicht die Dekodierzahlen, ΔDecode oder die kumulativen SNR-Kurven der Rohdaten.
7. **Mit neuen Beobachtungsdaten validieren.** Halte die Korrektur fest und zeichne einen separaten Zeitraum mit gemeinsamem Eingangssignal und denselben Kettendefinitionen und Einstellungen auf. Prüfe, ob die korrigierte Kennzahl plausibel nahe null liegt und über Stationen, Zeit und SNR übereinstimmt. Dokumentiere den verbleibenden Offset und die Streuung. Eine Null, die aus denselben Beobachtungen entsteht, mit denen der Offset bestimmt wurde, ist keine unabhängige Validierung. Behalte beim Tausch der Verteilerzweige die Identitäten an ihren Ketten. Wenn nur die Rollen Target und Referenz derselben kalibrierten Ketten vertauscht werden, kehre das Vorzeichen der Korrektur um und aktualisiere die Identitätszuordnung.

**Bereit zum Fortfahren:** Die Prüfungen der Messanordnung stützen den Vergleich, der Offset ist unter den vorgesehenen Bedingungen stabil, und eine separate Validierung stützt seine Verwendung. Schließe die Versuchseingänge wieder an den dokumentierten Referenzebenen an, erhalte die kalibrierten Ketten und Einstellungen und kehre dann zu [Abschnitt 1.2](#sec-2-2) zurück.

**Kalibrierungsprotokoll:** Bewahre exakte Identitäten und die Zuordnung zu physischen Ketten auf; Band, Referenzebene, Einstellungen und Zuordnungen der Verteilerzweige/Kabel; Kalibrierungszeiträume, Filter und Analyseumfang; statistische Kennzahl, Gewichtung und Stations-/Paarzahlen; bestimmten Offset, angewendeten Wert mit Vorzeichen und verbleibende Abweichungen der unabhängigen Validierung. Speichere die unkorrigierten Läufe, optionale Kontrollläufe mit vertauschten Verteilerzweigen und Validierungsläufe getrennt. [Abschnitt 9.3](#sec-8-3) beschreibt das vollständige Versuchsprotokoll.

Wiederholbarkeit stützt einen additiven Offset innerhalb der geprüften Anordnung, keine rückführbare Laborgenauigkeit. Verteilerdämpfung, Fehlanpassung, Kopplung, Kabeleinflüsse und Instabilität der Quelle können verbleiben. Eine geografisch getrennte Referenz kann eine wiederholbare Vergleichsgrundlage für dieses Paar, dieses Band und diesen Aufbau liefern, aber weder diese Kalibrierung mit gemeinsamem Eingangssignal noch eine absolute Kalibrierung.

<div style="page-break-before: always;"></div>

<a id="part-iii"></a>
## Teil III: Wissenschaftliche Grundlagen, Methoden und Aussagen

Teil III erklärt, wie WSPRadar Empfangsberichte auswertet und welche Schlussfolgerungen sich daraus ziehen lassen. Er richtet sich an Funkamateure, die die Berechnungen verstehen möchten; Formeln und durchgerechnete Beispiele helfen dabei, sie nachzuvollziehen.

Beginne für die Berechnungen mit [Kapitel 8](#sec-7): Was zählt als Beobachtung, welche Beobachtungen erfüllen die Anforderungen und was erhält in der jeweiligen Zusammenfassung gleiches Gewicht? [Kapitel 7](#sec-d) stellt den Bezug zu früheren Arbeiten aus Amateurfunk und Wissenschaft her. [Kapitel 9](#sec-8) erklärt, wie du ein Ergebnis formulierst und dokumentierst. Dieselben Einzelheiten unterstützen auch HamSCI-Mitwirkende und Gutachter.


<a id="sec-d"></a>
### 7. Literatur, Vorarbeiten und Einordnung

WSPR-Experimente beruhen auf Beiträgen von Funkamateuren, Forschern, Softwareentwicklern und den Freiwilligen, die das Meldenetz betreiben. Frühere Arbeiten haben praktische Verfahren etabliert, um Anlagen zu vergleichen, Empfangsprobleme zu untersuchen und die Ausbreitung zu erforschen.

Dieses Kapitel würdigt ausgewählte Mitwirkende für ihre Methoden und Ergebnisse. Die Abschnitte **Anwendung in WSPRadar** erläutern, welche Ansätze wir aus diesen Arbeiten aufgreifen; sie geben unsere Interpretation wieder und bedeuten keine Befürwortung durch die zitierten Autoren. Ein technischer Bericht, ein kontrolliertes Experiment und ein Softwaredienst liefern unterschiedliche Arten von Erkenntnissen und Datengrundlagen.

Drei Erkenntnisse kehren wieder: unter gemeinsamen Bedingungen vergleichen, vor der Interpretation ausbleibender Empfangsberichte die Aktivität belegen und die vollständige Station untersuchen, bevor ein Unterschied ihrer Antenne zugeschrieben wird.


<a id="sec-d-1"></a>
#### 7.1 Vom Meldenetz zum Versuchsdatensatz

<a id="sec-d-taylor-walker"></a>
##### 7.1.1 Joe Taylor, K1JT, und Bruce Walker, W1BW: eine gemeinsame Ressource für Experimente.

Taylor führte WSPR 2008 ein; Walker entwickelte WSPRnet, um Empfangsberichte zu sammeln und bereitzustellen. Ihr Artikel von 2010 zeigte, wie diese Berichte Ausbreitungsversuche unterstützen konnten. Ein Beispiel fasste drei Wochen von Beobachtungen auf 30 m in 15-Minuten-UTC-Intervallen zusammen: Die Mittelwertbildung machte wiederkehrende Empfangsmuster sichtbar, die sich anhand einzelner Aussendungen nur schwer beurteilen ließen. Die Stationsbetreiber lieferten die räumlich verteilten Beobachtungen; Protokoll, Software und Meldedienst machten sie zugänglich. Die Berichte blieben jedoch von der beteiligten Ausrüstung, den Standorten und den Betriebszeitplänen geprägt. <a href="#ref-6">[Ref-6]</a>

> **Anwendung in WSPRadar:** diesen Zusammenhang zwischen gemeldeten Beobachtungen und Fragestellung bewahren. Geografische und zeitliche Zusammenfassungen ordnen die Datengrundlage; der gewählte Zeitraum und die beteiligten Stationen bleiben Bestandteil ihrer Bedeutung.

<a id="sec-d-frissell"></a>
##### 7.1.2 Nathaniel Frissell und Mitautoren: Amateurfunkbeobachtungen in der Weltraumforschung.

Ihre Studie von 2019 verglich Berichte aus Amateurfunknetzen während der Sonnenaktivität im September 2017 mit einem Vergleichsverlauf aus einer ruhigen Periode. Sie erkannte mit Sonneneruptionen verbundene Kurzwellen-Funkausfälle sowie Veränderungen während geomagnetischer Störungen und nutzte den Vergleichsverlauf, um Reaktionen auf diese Ereignisse von gewöhnlichen Schwankungen zu unterscheiden. <a href="#ref-13">[Ref-13]</a>

Ihre Studie von 2022 verwendete Beobachtungen aus WSPRnet, dem Reverse Beacon Network und PSKReporter vom 3. November 2017. Schwankungen der Funkentfernung mit einer Dauer von ungefähr 2,5 Stunden stimmten mit SuperDARN-Radar und satellitennavigationsgestützten Messungen des ionosphärischen Elektronengehalts überein. Dies stützte die Interpretation als großräumige wandernde ionosphärische Störungen. Die unabhängigen Messungen waren Teil der Grundlage für diese physikalische Erklärung. <a href="#ref-14">[Ref-14]</a>

Ihr Übersichtsartikel von 2023 ordnet diese Amateurfunknetze neben zweckgebundenen wissenschaftlichen Instrumenten ein und empfiehlt eine Kreuzkalibrierung zwischen den Netzen. Er erkennt den wissenschaftlichen Wert angesammelter Beobachtungen an, ohne jeden beitragenden Empfänger als kalibriertes Instrument zu behandeln. <a href="#ref-7">[Ref-7]</a>

> **Anwendung in WSPRadar:** geografische und zeitliche Strukturen in ihrem Kontext untersuchen und anschließend eine physikalische Erklärung mit unabhängigen Beobachtungen oder einem kontrollierten Experiment prüfen. Die Diagramme von WSPRadar helfen, solche Fragen zu formulieren und zu untersuchen; sie identifizieren selbst keine ionosphärische Ursache.


<a id="sec-d-2"></a>
#### 7.2 WSPR-Beobachtungsdaten interpretierbar machen

<a id="sec-d-lo"></a>
##### 7.2.1 Lo und Mitautoren, 2022: vor der Interpretation ausbleibender Empfangsberichte die Aktivität belegen.

Ihre Studie verwendete ein vollständiges Jahr von Beobachtungen aus 2017 auf 7 MHz zwischen Europa und Australasien. Aktivitätsprüfungen in halbstündigen Intervallen untersuchten, ob ein Sender anderswo empfangen wurde und ob ein Empfänger andere Stationen empfing. Empfang aus dem Vereinigten Königreich nach Neuseeland trat um Sonnenaufgang und Sonnenuntergang im Vereinigten Königreich auf; in Gegenrichtung konzentrierte sich der Empfang auf den dortigen Sonnenaufgang, während Empfang um den dortigen Sonnenuntergang besonders im Sommer selten war. Die Autoren schlugen einen höheren europäischen Störpegel am Abend als mögliche Erklärung vor, statt die Asymmetrie allein als Ausbreitungsbefund zu behandeln. <a href="#ref-9">[Ref-9]</a>

> **Anwendung in WSPRadar:** das Prinzip der Aktivitätsprüfung bei der Definition von Empfangsgelegenheiten für Performance anwenden. WSPRadars eigene Regeln für denselben Zyklus legen fest, für welche Endpunkte Aktivitätsnachweise vorliegen; sie sind eine eigenständige Entwurfsentscheidung und unterscheiden sich von den halbstündigen Prüfungen der Studie. Fehlende Empfangsberichte ohne die erforderlichen Nachweise bleiben unbekannte Ergebnisse.

<a id="sec-d-griffiths-robinett-elmore"></a>
##### 7.2.2 Gwyn Griffiths, G3ZIL, Rob Robinett, AI6VN, und Glenn Elmore, N6GN, 2019–2020: den Rauschpegel parallel zum Empfang messen.

Ihr Bericht von 2019 verglich Rauschpegelschätzungen aus den Pausen zwischen WSPR-Aussendungen mit Schätzungen im Frequenzbereich während des Empfangs und untersuchte die Kalibrierung auf den Antenneneingang des Empfängers. Bei KPH zeigte die Rauschaufzeichnung auf 40 m ein tägliches Minimum um den lokalen Mittag sowie stärkere Schwankungen am Abend und in der Nacht. Diese Messungen lieferten Informationen, die gewöhnliche SNR-Berichte nicht bieten konnten. Die Arbeit wurde anschließend in QEX, September/Oktober 2020, veröffentlicht. <a href="#ref-15">[Ref-15]</a> <a href="#ref-16">[Ref-16]</a>

> **Anwendung in WSPRadar:** eine SNR-Änderung als Änderung des Verhältnisses zwischen Signal und Rauschen interpretieren. WSPRadar misst den Rauschpegel nicht unabhängig; um stärkere Signale von geringerem Rauschen zu unterscheiden, sind zusätzliche Messungen oder kontrollierte Stationsversuche nötig.


<a id="sec-d-3"></a>
#### 7.3 Entwicklungslinie von Antennen- und Stationsvergleichen

<a id="sec-d-destrem"></a>
##### 7.3.1 Patrick Destrem, F6IRF, 2008: automatisierte Umschaltung und geografischer Vergleich.

Destrem wechselte alle zehn Minuten zwischen einer Vertikalantenne und einer Inverted-V für 30 m und korrigierte die Empfangsberichte auf eine gemeinsame Sendeleistung. Dies waren <strong class="defined-term">zeitlich verschachtelte Messungen</strong>: Die Antennen wurden in abwechselnden Zeitabschnitten geprüft. Er untersuchte einzelne Empfänger und Entfernungsgruppen. Der berichtete mittlere Vorteil der Vertikalantenne betrug auf einem etwa 14 000 km langen Funkpfad ungefähr 4 dB; auf einem 2 000-km-Funkpfad waren die Antennen etwa gleichwertig. Das Ergebnis hing vom Funkpfad und der Anlage ab; aufeinanderfolgende Messungen blieben wechselnder Ausbreitung ausgesetzt. Folgeuntersuchungen erweiterten die Untersuchung auf Empfang und Stationsvergleiche. <a href="#ref-17">[Ref-17]</a>

> **Anwendung in WSPRadar:** die frühe Verbindung von Leistungskorrektur und geografischer Untersuchung würdigen. Richtungen und Entfernungen ausdrücklich vergleichen, dabei für ΔSNR zeitgleiche Spot-Paare verwenden und einseitige Empfangsberichte als eigene Datengrundlage erhalten.

<a id="sec-d-preston"></a>
##### 7.3.2 Charles Preston, KL7OA, später K7TAA, 2009 und 2017: simultaner Vergleich.

Prestons vorläufiger Versuch vom März 2009 verwendete zwei am selben Standort aufgestellte 2-W-Sender, eine Buddipole und eine horizontale Schleifenantenne auf 30 m. Gemeinsame entfernte Empfänger lieferten gleichzeitige Empfangsberichte. Im kurzen Versuch war das Gesamtverhalten ähnlich; die Buddipole stand jedoch innerhalb der Schleife, und die gegenseitige Beeinflussung der Antennen begrenzte die Schlussfolgerung. Jede Aussendung konnte auch allein gemeldet werden; schwacher Empfang und frequenzabhängige Störungen waren mögliche Erklärungen. Sein Bericht unterschied empfangenes SNR von Signalstärke. Später veröffentlichte er *Antenna Comparisons Using Simultaneous WSPR Measurements* in QEX, Juli/August 2017; die Aktualisierung des vorläufigen Berichts vom Juni 2017 verweist auf diese Veröffentlichung. <a href="#ref-18">[Ref-18]</a> <a href="#ref-19">[Ref-19]</a>

> **Anwendung in WSPRadar:** Aussendungen vergleichen, die derselbe Empfänger im selben Zyklus beobachtet hat. Gepaarte ΔSNR-Werte und einseitige Dekodierungen getrennt halten und die räumliche Anordnung dokumentieren, die den Vergleich begrenzt.

<a id="sec-d-toledo"></a>
##### 7.3.3 Sivan Toledo, 2010: ein nützliches negatives Ergebnis zur zeitlichen Versuchsplanung.

Toledo verglich drei Schleifenantennen in aufeinanderfolgenden Blöcken von ungefähr einer Stunde. Die Empfangsberichte änderten sich erheblich, während er noch dieselbe Antenne verwendete: Ein Funkpfad schwankte in vierzig Minuten um etwa 10 dB, und ein weiterer Empfänger zeigte ähnliche Schwankungen. Die scheinbaren Antennenunterschiede waren mit dieser Hintergrundschwankung vergleichbar; der Versuch konnte deshalb Antennenverhalten und wechselnde Bedingungen nicht trennen. Sein Bericht erörterte automatisierte Umschaltung und Prestons simultanen Ansatz als Verbesserungen des Versuchsdesigns. Dies war eine Grenze des Versuchs und kein Befund, dass WSPR-Vergleiche unmöglich seien. <a href="#ref-3">[Ref-3]</a>

> **Anwendung in WSPRadar:** den gemeinsamen Betriebszeitraum zum Bestandteil des Vergleichs machen, zeitliche Änderungen untersuchen und kontrollierte Versuche wiederholen. Mehr Empfangsberichte allein beseitigen keine Unterschiede zwischen den verglichenen Bedingungen.

<a id="sec-d-milazzo"></a>
##### 7.3.4 Carol F. Milazzo, KP4MD, 2011: vollständige Stationen in beiden Richtungen vergleichen.

Milazzos im Januar 2011 veröffentlichte Studie verwendete Messungen vom Dezember 2010 und verglich 29 km voneinander entfernte Stationen über einen gemeinsamen Empfänger in etwa 1 750 km Entfernung. Sie korrigierte Unterschiede der Sendeleistung und betrachtete die Ergebnisse zusammen mit VOACAP-Schätzungen. Auf 40 m erzeugte die Station mit horizontaler Schleifenantenne im Allgemeinen höhere gemeldete SNR-Werte bei der Aussendung; die Station mit Vertikalantenne empfing dagegen die gemeinsame entfernte Station mit besserem SNR. Unterschiedliche Standorte, Funkgeräte und Bandzeitpläne blieben Bestandteil des Vergleichs, und die ausgewählte entfernte Station begrenzte dessen geografischen Umfang. <a href="#ref-4">[Ref-4]</a>

> **Anwendung in WSPRadar:** TX und RX getrennt auswerten, die Leistungsbezugsgröße ausdrücklich angeben und gemeinsamen Betrieb prüfen. Ein stärkerer Empfangsbericht einer Aussendung belegt keinen besseren Empfang; jedes Ergebnis ist als Befund zu den vollständigen geprüften Anlagen und Funkpfaden zu interpretieren.
>
> **In WSPRadar erkunden:** Die [Auswertung historischer Empfangsberichte von Milazzo](https://wspradar.org/de/demos/milazzo_tx_buddy/) untersucht die Abbildungen 6 und 7 erneut in RX und TX. Sie zeigt, wie trotz größerer Gesamtzahlen von Empfangsberichten durch exakte Zuordnung nach Zyklus und Locator sowie Normierung auf die gemeldete Sendeleistung nur sehr wenige nutzbare Spot-Paare verbleiben können und warum ungeprüfte Zeitpläne Vergleiche dieser Gesamtzahlen begrenzen. Das vorbereitete Profil beginnt mit RX; die Anleitung stellt auch die TX-Konfiguration bereit.

<a id="sec-d-griffiths-squibb"></a>
##### 7.3.5 Gwyn Griffiths, G3ZIL, und Nigel Squibb, G4HZX, 2017: vergleichen, untersuchen und erneut prüfen.

In *Improving HF Band SNR* paarten sie den Empfang desselben Senders zur selben Zeit und untersuchten Unterschiede nach Zeit, Entfernung, Bodenfeuchte und Stationsänderungen. Nachdem bei G4HZX drei Bodenradials ergänzt worden waren, fehlte der frühere Zusammenhang mit der Feuchtigkeit im folgenden Testzeitraum. Austausch und Versetzen eines nahe gelegenen Computers fielen außerdem mit einer SNR-Verbesserung von ungefähr 5 dB zusammen. Der genaue Störmechanismus blieb ungeklärt, und beide Beobachtungen betrafen vollständige Empfangsanlagen. Die dokumentierten Änderungen machten die Vergleiche für die Diagnose nützlich, ohne einen universellen Antenneneffekt zu beweisen. <a href="#ref-5">[Ref-5]</a>

> **Anwendung in WSPRadar:** gepaarte Empfängervergleiche sowie Zeit- oder Entfernungsansichten gemeinsam mit dem Stationsprotokoll des Betreibers nutzen. Ein Muster als Anlass für einen gezielten Eingriff und eine wiederholte Messung behandeln; kausale Aussagen müssen dem Umfang der Kontrollen entsprechen.
>
> **In WSPRadar erkunden:** Drei vorbereitete Konfigurationen untersuchen diese historischen Empfangsberichte erneut:
>
> - [**Abbildung 3: RX Benchmark**](https://wspradar.org/de/demos/griffiths_squibb_fig3/) verfolgt den G3ZIL/G4HZX-Vergleich vom April 2017 durch Karten, zeitliche Zusammenfassungen und einzelne Funkpfade. Sie zeigt, wie sich ein Vorteil im gepaarten SNR und zusätzliche Dekodierungen ergänzen und zugleich mit Richtung und Zeit variieren.
> - **Abbildung 6: Vergleich nach UTC-Stunde** begrenzt dieselben Empfänger auf den 5.–7. April. Die separate Konfiguration zeigt einen Vorteil der Vertikalantenne in den frühen Stunden, der tagsüber und abends in einen Vorteil des Dipols übergeht; der Vergleich der nach UTC-Stunde zusammengefassten und der chronologischen Ansichten prüft, wie übereinstimmend das Muster auftritt. Die Anleitung zu Abbildung 3 erläutert auch diese Rekonstruktion.
> - [**RX Performance**](https://wspradar.org/de/demos/griffiths_squibb_rx_performance/) untersucht G3ZIL allein. Verfolge HB0QRP, um mindestens einmal erfasste Gegenstationen, die Dekodierquote innerhalb bestätigter Empfangsgelegenheiten und das SNR erfolgreicher Dekodierungen voneinander zu unterscheiden. Dies ist WSPRadars zusätzliche Analyse der historischen Empfangsberichte ohne Referenzempfänger.

<a id="sec-d-vanhamel"></a>
##### 7.3.6 Vanhamel, Machiels und Lamy, 2022: die Empfangszweige charakterisieren.

Bei ihrem 160-m-Versuch verbanden sie zunächst zwei Empfangszweige mit einer Antenne. Zwei siebentägige Kalibrierungszeiträume ergaben jeweils einen mittleren Versatz von etwa 1,2 dB, den sie vor dem simultanen Antennenvergleich berücksichtigten. Mit identischen, rechtwinklig zueinander ausgerichteten Antennen beobachteten sie in dieser Anlage eine SNR-Differenz von ungefähr 3 dB. Polarisation und ionosphärische Effekte wurden als mögliche Erklärungen erörtert; das Ergebnis zur Ausrichtung belegte keine einzelne physikalische Ursache. Die Kalibrierung machte außerdem einen Beitrag der Ausrüstung sichtbar, bevor der Antennenvergleich interpretiert wurde. <a href="#ref-2">[Ref-2]</a>

> **Anwendung in WSPRadar:** einen unabhängig gemessenen Versatz der Empfangszweige über die vorzeichenbehaftete Referenzkorrektur berücksichtigen können und das Messverfahren dokumentieren. Den korrigierten SNR-Vergleich von Aussagen über die Antenne oder den Polarisationsmechanismus trennen, der ihn verursacht hat.
>
> **In WSPRadar erkunden:** Zwei vorbereitete Vergleiche trennen die Kalibrierung vom anschließenden Antennenversuch:
>
> - [**Empfängerkalibrierung**](https://wspradar.org/de/demos/vanhamel_rx_calibration/) lässt den Versatz der Empfangszweige an derselben Antenne ohne Korrektur sichtbar. Sie zeigt, warum arithmetischer Mittelwert, Median über Spot-Paare und Median bei gleicher Stationsgewichtung voneinander abweichen können und warum eine Korrektur eine dokumentierte Messgrundlage benötigt.
> - [**Antennendrehung**](https://wspradar.org/de/demos/vanhamel_rx_buddy/) verfolgt M7AEO, während sich der Referenzdipol um 90° dreht und der Target-Langdraht fest bleibt. Der Sprung von ungefähr 3 dB begünstigt den festen Langdraht gegenüber dem Dipol. Er zeigt, warum die chronologischen Beobachtungsdaten eines Funkpfads einen Übergang aufdecken können, den dessen Median über den gesamten Zeitraum verdeckt. Die Anleitung dokumentiert die separate Kalibrierungsschätzung dieser Konfiguration.

<a id="sec-d-zander"></a>
##### 7.3.7 Jens Zander, 2022: Vergleichsmodell und Annahmen angeben.

Zanders Preprint modelliert zwei lokale Antennen, die gleichzeitig zu gemeinsamen entfernten Empfängern senden. Eine SNR-Differenz innerhalb desselben Empfängers hebt unter den Modellannahmen gemeinsame Ausbreitungsdämpfung und Empfängerrauschen auf; für jede Differenz innerhalb eines Empfängers ist keine Kreuzkalibrierung zwischen diesen entfernten Empfängern nötig. Seine vorläufigen gepaarten Messungen hatten eine Stichproben-Standardabweichung von etwa 3 dB. Die Analyse berücksichtigt Störungen, fehlgeschlagene Dekodierungen, Quantisierung und den Präzisionsgewinn durch Mittelwertbildung sowie Richtwirkung, geografische Stichprobe und unbekannte Elevationswinkel. Gleiche oder korrigierte Leistungen und Unterschiede zwischen den Sendezweigen bleiben relevant. <a href="#ref-1">[Ref-1]</a>

> **Anwendung in WSPRadar:** die Differenzbildung im selben Zyklus und den Bezug auf die gemeldete Sendeleistung ausdrücklich angeben. WSPRadar definiert eigene Qualifikations- und Aggregationsregeln; das Unsicherheitsmodell des Preprints ist nicht automatisch deren Unsicherheitsmodell, und beobachtetes ΔSNR misst nicht direkt den absoluten Antennenwirkungsgrad.
>
> **In WSPRadar erkunden:** [Zanders TX-Vergleich](https://wspradar.org/de/demos/zander_tx_buddy/) untersucht Experiment A / Abbildung 4 erneut und vergleicht eine kurze portable Vertikalantenne mit der größeren Hy-Gain AV620. Er zeigt, warum Zusammenfassungen bei gleicher Stationsgewichtung von Zusammenfassungen über sämtliche Spot-Paare abweichen, wie das Ergebnis mit der Richtung variiert und warum ungleiche Meldezeiträume vor der Interpretation von Dekodierzahlen geprüft werden müssen. Das kurze vorbereitete Zeitfenster trägt den beobachteten Vergleich dieses Versuchs, aber kein Tagesmuster und keinen universellen Nachteil portabler Antennen.

<a id="sec-d-rietdorf"></a>
##### 7.3.8 Thomas Rietdorf, DL2OAH, 2026: ein synchronisierter Stationsvergleich auf mehreren Bändern.

Sein DARC-Vortrag vom 17. Januar 2026 berichtet über Messungen vom 12.–21. Januar 2025. Synchronisierte Transceiver verglichen eine horizontale OCF/IC-7610-Anlage mit einer vertikalen FT-991A-Anlage in getrennten RX- und TX-Durchläufen auf 40, 20, 15 und 10 m. Zugeordnete Zweiminutenberichte ermöglichten zusammen mit einseitigen Empfangsberichten Vergleiche nach Zeit und Richtung. Der Vortrag berichtet je nach Band einen SNR-Vorteil von 2,5–7 dB für die horizontale Anlage, während die maximalen Entfernungen ungefähr gleich waren. Unterschiedliche Funkgeräte und die Verteilung der Gegenstationen begrenzen die Zuordnung allein zu den Antennen. <a href="#ref-20">[Ref-20]</a>

> **Anwendung in WSPRadar:** synchronisierte Vergleiche mit mehreren Ansichten der Datengrundlage verbinden. Gepaarte SNR-Werte, einseitige Dekodierungen sowie geografische oder zeitliche Muster gemeinsam lesen und dabei die Interpretation als vollständige Anlage und die tatsächlichen Messdaten beibehalten.

<a id="sec-d-ostergaard"></a>
##### 7.3.9 Dale Ostergaard, N3HXZ, 2026: praktische sequenzielle Antennenvergleiche.

Ostergaard hat Antennentests mit WSPR für den Portabelbetrieb und den Einsatz im Feld vorangebracht und einen wiederholbaren Ansatz mit einem Sender und einem Antennenumschalter dokumentiert. Sein *QEX*-Artikel vom März/April 2026, *Using WSPR to Predict Relative Antenna Gain of Directional Antennas*, beschreibt den Wechsel zwischen Antennenkonfigurationen, üblicherweise in Blöcken von 30 Minuten, und die Schätzung der relativen Signalstärke an gemeinsamen Empfangsstationen. Gemeldete SNR-Werte werden vor der Mittelwertbildung von dB in lineare Leistungsverhältnisse umgerechnet; er empfiehlt mindestens 40 Empfangsberichte je Antenne an jeder Empfangsstation. Seine veröffentlichten Fallstudien umfassen Vergleiche zwischen erhöht aufgestellten und bodennah montierten Vertikalantennen. Damit werden quantitative Vergleiche im Feld mit überschaubarem Geräteaufwand zugänglich; wechselnde Ausbreitungsbedingungen zwischen den Blöcken und die fehlende Erfassung nicht dekodierter Signale bleiben jedoch wichtige Einschränkungen. <a href="#ref-34">[Ref-34]</a>

> **Anwendung in WSPRadar:** die praktische sequenzielle Methode, ausdrücklich angegebene Umschaltpläne und Anforderungen an die Datengrundlage je Empfänger würdigen. Sequenzielle Schätzungen des relativen Gewinns ergänzen synchronisierte gepaarte ΔSNR-Werte, sind aber nicht direkt mit ihnen austauschbar.


<a id="sec-d-4"></a>
#### 7.4 Analyseinfrastruktur und verwandte Werkzeuge

> **Anwendung in WSPRadar:** **wspr.live ist die primäre Datenbank, mit WD2 und WD1 von WSPRdaemon als Alternativen**. Jeder Analyselauf nutzt eine Quelle. Entwickler, Stationsbetreiber, Anbieter von Rechenressourcen und ehrenamtliche Betreuer ermöglichen diese Analyse; die Verfügbarkeit der Dienste und die Qualität hochgeladener Datensätze bleiben Teil des Kontexts der Datengrundlage.
>
> **Unser herzlicher Dank gilt allen, die diese Dienste aufrechterhalten und Empfangsberichte, Rechenressourcen und ehrenamtliche Zeit beitragen.** Eure Arbeit gibt der Amateurfunkgemeinschaft eine gemeinsame Grundlage für Lernen, Experimente und bessere Stationsaufbauten.

<a id="sec-d-griffiths-robinett"></a>
##### 7.4.1 Gwyn Griffiths und Rob Robinett, 2020: wiederverwendbare Datenbankanalyse.

Ihre Arbeit mit WSPRdaemon TimescaleDB und Grafana verknüpfte Empfangsberichte desselben Senders zur selben Zeit auf demselben Band und stellte anschließend SNR-Differenzen mit Medianen, Quartilen, Zeit, Entfernung und Azimut dar. Ein Beispiel unterschied nächtliche Unterschiede westwärts nach Nordamerika von Unterschieden am Tag mit näheren Stationen. Rauschmessungen und Exporte gaben Betreibern weitere Möglichkeiten zur Untersuchung dieser Muster. Der Beitrag umfasste sowohl die Vergleichsmethode als auch einen wiederverwendbaren Weg von gespeicherten Beobachtungen zu interpretierbaren Darstellungen. <a href="#ref-21">[Ref-21]</a>

> **Anwendung in WSPRadar:** die Untersuchung von Differenzen beim Empfang desselben Signals nach Zeit und Geografie fortführen und den Rückweg zu den beitragenden Beobachtungen ermöglichen. WSPRadars eigene Gruppierungs- und Gewichtungsregeln sind in [Kapitel 8](#sec-7) festgelegt.

<a id="sec-d-wspr-live"></a>
##### 7.4.2 Arne und das Projekt wspr.live, mit Rechenressourcen von HB9VQQ.

Arnes Arbeit an der ClickHouse-Datenbank ermöglicht öffentliche Abfragen historischer und aktueller WSPR-Empfangsberichte; Dashboards und Exporte machen diese Datensätze für Betreiber und andere Anwendungen nutzbar. Die offizielle Dokumentation des Dienstes würdigt **HB9VQQ für die Rechenressourcen**. Auch Phil VK7JJs Dokumentation würdigt Arnes Datenbankbeitrag ausdrücklich. <a href="#ref-10">[Ref-10]</a> <a href="#ref-22">[Ref-22]</a>

<a id="sec-d-wsprdaemon"></a>
##### 7.4.3 Rob Robinett, AI6VN, und die WSPRdaemon-Gemeinschaft.

Empfang, Erfassung mit mehreren Empfängern, Übermittlung von Empfangsberichten, Datenbankhosting und fortlaufender ehrenamtlicher Betrieb tragen diese Dienste. WSPRdaemons Dokumentation würdigt Arnes Datenbankentwicklung und die Zusammenarbeit beim Hosting. Die frühere TimescaleDB-Arbeit und die späteren ClickHouse-Dienste sind eigenständige Beiträge. <a href="#ref-11">[Ref-11]</a>

<a id="sec-d-farfield-lab"></a>
##### 7.4.4 Tim, K5OHY — FarField Lab: praxisnahe Antennenvergleiche mit Umschaltung.

[FarField Lab](https://farfieldlab.streamlit.app/) ist eine kostenlose Open-Source-Anwendung, die Funkamateuren praktische WSPR-Antennenvergleiche mit **nur einem Sender oder Transceiver und einem Antennenumschalter** ermöglicht. Sie unterstützt einen schnellen Antennenwechsel zwischen den Aussendungen nach den Mustern **ABAB und ABBA**, längere sequenzielle Blockvergleiche mit bearbeitbaren Umschaltplänen sowie die Auswertung von Daten des Reverse Beacon Network. Bei kurzen Tests werden Beobachtungen benachbarter Aussendungen paarweise zugeordnet, was den Einfluss wechselnder Ausbreitungsbedingungen begrenzt. Ausbalancierte ABBA-Folgen können unter geeigneten Bedingungen zusätzlich eine annähernd lineare zeitliche Drift ausgleichen. Wiederholte Messungen und Mittelwertbildung helfen, zufällige Schwankungen zu verringern, während Vergleiche längerer Blöcke stärker durch Änderungen der Ausbreitungsbedingungen beeinflusst bleiben. FarField Lab wertet relative SNR-Unterschiede bei Stationen aus, die beide Antennen empfangen haben. Es zeigt außerdem, welche Stationen in welchen Richtungen und Entfernungen erreicht wurden. Dazu gehören Prüfungen der Empfängeraktivität, Mindestanforderungen an die Datengrundlage, Unsicherheitsschätzungen und statistische Validierung. Die Auswertung langer Blöcke reproduziert veröffentlichte Ergebnisse von Dale Ostergaard, N3HXZ. **FarField Lab bietet eine echte, praxistaugliche Alternative zu WSPRadar**, insbesondere für Funkamateure ohne Hardware für zwei synchronisierte Stationen. Der sequenzielle Ansatz ergänzt WSPRadars simultanes RX/TX-Benchmarking mit Spot-Paaren aus demselben WSPR-Zyklus. Damit stehen Funkamateuren unterschiedliche, aber gleichermaßen wertvolle Möglichkeiten zur Verfügung, die Leistungsfähigkeit von Antennen und Stationen anhand öffentlicher WSPR-Daten zu untersuchen. [Ref-35](https://github.com/K5OHY/FarField-Lab) [Ref-34](https://www.n3hxz.net/wspr-methodology)

> **Anwendung in WSPRadar:** FarField Lab als ergänzendes Werkzeug für sequenzielle Antennenanalysen würdigen und Funkamateuren helfen, den Versuchsansatz zu wählen, der am besten zu ihrer Ausrüstung und ihren Zielen passt.

Weitere Werkzeuge machen ergänzende Bereiche des Experimentierens zugänglich:

<a id="sec-d-wspr-rocks"></a>
##### 7.4.5 Phil, VK7JJ — WSPR.Rocks

Interaktive Abfragen, Karten, Diagramme, Untersuchung von Duplikaten und Empfangsdurchlassbereichen sowie Head2Head-Vergleiche von Empfängern, Sendern oder Softwareversionen. SpotQ liefert eine heuristische Rangfolge aus Entfernung, gemeldeter Sendeleistung und SNR. Dies sind nützliche Wege zur Untersuchung von Empfangsberichten; ihre Kennzahlen haben eigene Definitionen. <a href="#ref-22">[Ref-22]</a>

<a id="sec-d-wsprlite-dxplorer"></a>
##### 7.4.6 Richard Newstead und SOTABEAMS — WSPRlite/DXplorer

Eigenständige Kleinleistungsbaken und leicht zugängliche Vergleiche, darunter der Entfernungsindikator DX10. In Newsteads Innen-/Außentest von 2017 sendeten zwei Schleifenantennen gleichzeitig mit 200 mW; 133 Spot-Paare desselben Empfängers zur selben Zeit ergaben einen mittleren Nachteil der Innenantenne von 6,8 dB.

> **Anwendung in WSPRadar:** den praktischen gepaarten Versuchsaufbau würdigen und den Wert zugleich als Ergebnis für diese Anlage und diesen Betriebszeitraum behandeln.

<a href="#ref-23">[Ref-23]</a> <a href="#ref-24">[Ref-24]</a>

<a id="sec-d-wspr-station-compare"></a>
##### 7.4.7 Walter Machiels, ON4AWM — WSPR-Station-Compare

Ein Ablauf für RX-Vergleiche mit Korrektur eines gemessenen Empfängerversatzes, Mindestzahlen von Beobachtungen, Rufzeichenfilter und Azimutauswahl. Er macht Entscheidungen für kontrollierte Vergleiche in einer Bediensoftware verfügbar. <a href="#ref-25">[Ref-25]</a>

<a id="sec-d-antenna-performance-analysis"></a>
##### 7.4.8 Fred, W6BSD — Antenna Performance Analysis

Berichte, die über Zeiträume und Frequenzbänder hinweg ordnen, wo und wann ausgesendete WSPR-Signale empfangen wurden. Damit wird die beobachtete Abdeckung einer Anlage ohne eigens geschriebene Analyse zugänglich. <a href="#ref-26">[Ref-26]</a>

<a id="sec-d-watt"></a>
##### 7.4.9 Colin Murray, GM4EAU — WATT

Ein bearbeitbarer Excel/VBA-Ablauf für Abfragen, Filter, Berechnungen, Diagramme und Kartenwiedergabe über aufeinanderfolgende Zeitintervalle, mit dem Betreiber wechselnde Ausbreitungsmuster untersuchen können. <a href="#ref-27">[Ref-27]</a>

Diese Werkzeuge überschneiden sich in ihrem Zweck; ihre Filter, Vergleichseinheiten und Zusammenfassungen unterscheiden sich jedoch. Prüfe die Größe hinter einer Abbildung, bevor du ihren Wert mit einem WSPRadar-Ergebnis vergleichst.


<a id="sec-d-5"></a>
#### 7.5 Was WSPRadar übernimmt, integriert und ergänzt

WSPRadar überführt diese experimentellen Erkenntnisse in einen dokumentierten RX- und TX-Ablauf. Dabei trifft es bewusst folgende Entscheidungen:

* **Den Vergleich definieren.** Ein kontrollierter Benchmark vergleicht ein Target mit einem Referenzaufbau oder einer Referenzstation bei unabhängig bekanntem gemeinsamem Betrieb. Bei der Auswertung historischer Empfangsberichte bleiben die Betriebsbedingungen ausdrücklich ungeprüft.
* **Ergänzende Ergebnisse sichtbar halten.** Spot-Paare desselben Zyklus liefern ΔSNR; gepaarte und einseitige Dekodierergebnisse ermöglichen den Dekodiervergleich. Eine Station, die auf einer Seite selten gehört wird, liefert möglicherweise nur wenige Spot-Paare. Gepaarte SNR-Werte allein können deshalb ein unvollständiges Bild ergeben.
* **Anpassungen offenlegen.** Normierung auf die gemeldete Sendeleistung und optionale vorzeichenbehaftete Referenzkorrektur machen die numerische Grundlage prüfbar.
* **Empfangsgelegenheiten definieren.** Performance setzt erfolgreiche Dekodierungen zu bestätigten Empfangsgelegenheiten ins Verhältnis. Eine fehlende Dekodierung zählt nur dann als nicht dekodierte Gelegenheit, wenn die erforderlichen Empfangsberichte die Aktivität von Sender und Empfänger belegen.
* **Gewichtungen unterscheiden.** Jede Station gleich zu gewichten beantwortet eine andere Frage, als jede einzelne Beobachtung gleich zu gewichten.
* **Ergebnisse nachvollziehbar machen.** Karten-, Stations- und Einzelbeobachtungsansichten, gespeicherte Einstellungen und Exporte verbinden eine Schlussfolgerung mit ihren Daten und Entscheidungen.

Diese Definitionen bestimmen, welche Beobachtungen die Anforderungen erfüllen, wie sie gezählt werden und wie sie eine Zusammenfassung beeinflussen. Sie ermöglichen reproduzierbare Vergleiche unter den Bedingungen der verfügbaren Empfangsberichte und Betriebsverhältnisse; sie belegen nicht direkt eine unbedingte Empfangswahrscheinlichkeit oder einen kalibrierten Antennenwirkungsgrad. [Kapitel 8](#sec-7) legt die Berechnungen fest, und [Kapitel 9](#sec-8) erklärt, wie sich durch die Datengrundlage getragene Aussagen berichten lassen.


<a id="sec-7"></a>
### 8. Wissenschaftliche Methoden

**Benchmark** vergleicht Target und Referenz für dieselben Gegenstationen und WSPR-Zyklen. Gepaarte und einseitige Dekodierergebnisse bleiben erhalten. Ein Spot-Paar mit nutzbarem SNR auf beiden Seiten liefert außerdem ΔSNR. **Performance** misst den Dekodiererfolg des Targets innerhalb bestätigter Empfangsgelegenheiten, ohne Referenz. Die folgenden Zählregeln unterscheiden Stationen anhand von gemeldetem Rufzeichen und Locator.

Verfolge bei der Berechnung drei Fragen:

| Frage | Was die Methode klären muss |
|---|---|
| **Was zählt einmal?** | Eine Gegenstation in einem WSPR-Zyklus, nachdem Empfangsberichte nach den folgenden Regeln zugeordnet und zusammengefasst wurden. Mehrere Berichte zählen nicht automatisch als mehrere Beobachtungen. |
| **Welche Beobachtungen gehen in das Ergebnis ein?** | Analyse und Filter bestimmen, welche Beobachtungen berücksichtigt werden. Jede Kennzahl stellt außerdem Anforderungen an die Daten je Station oder Segment. Unbekannte Aktivität und nicht erfüllte Anforderungen unterscheiden sich von einer gemessenen Null. |
| **Was erhält gleiches Gewicht?** | Je nach Zusammenfassung eine Station, ein Spot-Paar, eine bestätigte Empfangsgelegenheit oder der Beitrag einer Station innerhalb eines Zeitintervalls. Mehr Empfangsberichte bedeuten nicht immer mehr Gewicht. |

Ein Datenbank-Spot dokumentiert eine erfolgreiche Dekodierung. WSPRadar bildet daraus nach den folgenden Regeln Spot-Paare und bestätigte Empfangsgelegenheiten. Mediane, Quoten und andere Zusammenfassungen beschreiben die so berücksichtigten Beobachtungen.

Lies zunächst die gemeinsamen Grundlagen in [Abschnitt 8.1](#sec-7-foundations), danach [Benchmark](#sec-7-benchmark) oder [Performance](#sec-7-performance). [Abschnitt 8.4](#sec-7-views) erklärt geografische und zeitliche Zusammenfassungen, [Abschnitt 8.5](#sec-7-claims) die Tragweite von Schlussfolgerungen und [Abschnitt 8.6](#sec-7-outliers) die optionale Ereigniserkennung. Eine Berechnung kann für die beibehaltene Datengrundlage korrekt sein, während ihre physikalische Erklärung ungewiss bleibt; [Kapitel 9](#sec-8) gibt Hinweise zur Berichterstattung.


<a id="sec-7-foundations"></a>
#### 8.1 Gemeinsame Grundlagen der Datenauswertung

<a id="sec-7-spots-identities-cycles"></a>
<a id="sec-7-1"></a>
<a id="sec-7-2"></a>
##### 8.1.1 Spots, Identitäten und Zyklen

Jeder abgeschlossene Analyselauf verwendet eine WSPR-Datenbank; er kombiniert keine Datensätze verschiedener Quellen. Dokumentiere diese Quelle mit dem Ergebnis, denn die Empfangsberichte stammen von unterschiedlichen Sendern, Empfängern, Dekodern und Meldesystemen.

Ein **Spot** ist ein hochgeladener Empfangsbericht nach erfolgreicher Dekodierung. Ein **WSPR-Zyklus** ist das zweiminütige Intervall, das zu einer geraden UTC-Minute beginnt. WSPRadar zählt Beobachtungen für eine Gegenstation in einem von der Analyse berücksichtigten Zyklus auf dem gewählten Band: einen Sender bei RX oder einen Empfänger bei TX. Vor dem Zählen werden geeignete Berichte zu einer Beobachtung je Aufbau, Station und Zyklus zusammengefasst. [Abschnitt 8.1.2](#sec-7-normalization-consolidation) erklärt, welcher Bericht erhalten bleibt.

Ein **Spot-Paar** erfordert nutzbare Berichte für Target und Referenz zur selben Gegenstation im selben Zyklus. RX vergleicht zwei Empfänger, die denselben Sender hören; TX vergleicht zwei Sender, die derselbe Empfänger hört. Berichte aus verschiedenen Zyklen werden niemals gepaart. Die Zuordnung erfordert weder identische HF-Frequenzen noch belegt sie identische physikalische Ausbreitungswege; gleichzeitige TX-Signale benötigen normalerweise deutlich getrennte Frequenzen.

**Die Identität hängt von der Rolle der Station ab:**

| Rolle | Datenbankidentität |
|---|---|
| **Target** | Exaktes Empfangsrufzeichen in RX oder Senderufzeichen in TX, dazu die ersten vier Locatorzeichen des Target-QTH. |
| **Referenzaufbau oder Referenzstation** | Exaktes Referenz-Rufzeichen zusammen mit seinem vierstelligen Locator, aus Empfangsberichten ermittelt oder unabhängig angegeben. |
| **Gegenstation** | Exaktes Rufzeichen zusammen mit dem **vollständigen gemeldeten Locator**: der Sender in RX oder der Empfänger in TX. |

**Eine Gegenstation bezeichnet im Folgenden eine exakte Kombination aus Rufzeichen und vollständigem gemeldetem Locator.** Auch bei einem sechsstelligen Target-QTH wählen die ersten vier Zeichen die Target-Berichte aus. Der vollständig konfigurierte Locator dient als Bezugspunkt für Entfernungs-, Azimut- und Sonnenstandsberechnungen. Dasselbe Gegenstationsrufzeichen mit zwei vollständigen Locatoren zählt als zwei Stationen, auch innerhalb desselben vierstelligen Locatorfelds. Übereinstimmende vierstellige Locatoren belegen keine Aufstellung am selben physischen Standort.

Target und Referenz benötigen unterschiedliche exakte Rufzeichen; ein Basisrufzeichen und ein Rufzeichen mit Suffix bleiben verschieden. Jeder berücksichtigte Bericht muss die für die Zuordnung benötigten Rufzeichen- und Locatorfelder enthalten. WSPRadar rekonstruiert zusammengesetzte Rufzeichen nicht aus Hashes und übernimmt keinen fehlenden Locator aus einem benachbarten Zyklus. Falsche oder wechselnde Locatoren können eine physische Station als mehrere Stationen erscheinen lassen, ihre Kartenposition verschieben oder den Ausschluss beweglicher Stationen auslösen.

**Auch erweitertes WSPR liefert getrennte Zweiminutenbeobachtungen.** WSPR-2 bezeichnet die Übertragungsart; die folgenden Nachrichtentypen beschreiben ihren Inhalt:

| Nachrichtentyp | Inhalt |
|---|---|
| <strong class="defined-term">Typ 1</strong> | Ein gewöhnliches Rufzeichen, ein vierstelliger Locator und die Leistung in einer Aussendung. |
| <strong class="defined-term">Typ 2</strong> | Ein zusammengesetztes Rufzeichen und die Leistung, ohne Locator. |
| <strong class="defined-term">Typ 3</strong> | Die ergänzende Nachricht mit einem kompakten 15-Bit-Rufzeichencode (einem <strong class="defined-term">Hash</strong>), einem sechsstelligen Locator und der Leistung. Der Empfänger muss den Code dem Rufzeichen zuordnen. |

Diese Nachrichtenformate sind in der WSJT-X-Referenz dokumentiert <a href="#ref-12">[Ref-12]</a>. WSPRadar klassifiziert sie nicht, rekonstruiert keine fehlenden Phasen und kombiniert sie nicht zu einer Vierminutenbeobachtung. Einer oder beide Zyklen können Spot-Paare liefern, wenn die erforderlichen Identitäten in der Datenbank aufgelöst sind; ein Spot-Paar in einem Zyklus erfordert kein weiteres im nächsten. Übereinstimmende TX-Nachrichtenmuster und Zeitpläne sind eine Empfehlung für den Versuch, keine Zulässigkeitsprüfung nach Nachrichtentyp; siehe [Abschnitt 2.2.1](#sec-3-tx-benchmark-simultaneous) und [Kapitel 5](#sec-simultaneous-tx-setup).

Das konfigurierte UTC-Zeitfenster definiert den Analyselauf. Bei vollständig vor 2022 liegenden Zeiträumen kann eine leere strikte Abfrage den Fallback für historische Dekodiercodes auslösen: keine Target-Quelldaten in Performance beziehungsweise keine Quelldaten von irgendeinem der beiden Aufbauten in Benchmark. [Abschnitt 11.4](#sec-6-4) nennt den exakten Stichtag und die Unsicherheit der Übertragungsart; [Abschnitt 11.6](#sec-6-6) behandelt Datenbankverfügbarkeit und Quellenauswahl.


<a id="sec-7-normalization-consolidation"></a>
##### 8.1.2 Leistungsnormierung und Zusammenfassung

**RX Performance und Benchmark verwenden einen gemeinsamen Bezug auf die gemeldete Sendeleistung; TX Performance kann gemeldetes Empfangs-SNR beibehalten oder normieren.** WSPR meldet das SNR in dB bezogen auf eine **Referenzbandbreite von 2 500 Hz** und die Sendeleistung in dBm <a href="#ref-8">[Ref-8]</a>. Bei eingeschalteter TX-Normierung sowie für RX Performance und Benchmark rechnet WSPRadar das SNR erfolgreicher Dekodierungen auf **30 dBm (1 W)** um:

$$SNR_{\mathrm{norm}}=SNR_{\mathrm{reported}}-P_{\mathrm{reported}}+30$$

Die SNR-Werte stehen in dB, die Leistungswerte in dBm. Ein gemeldetes SNR von **−15 dB** bei **20 dBm** wird beim Vergleichswert von 30 dBm beispielsweise zu **−5 dB**: Die gemeldete Leistung liegt 10 dB darunter, daher werden 10 dB zum SNR addiert.

Dies entfernt den **Unterschied der gemeldeten Sendeleistung** aus dem Vergleich. Es rekonstruiert weder die Dekodierungen, die bei 1 W erfolgt wären, noch korrigiert es Antennengewinn, Strahlungswirkungsgrad, Speiseleitungsverlust, EIRP, Empfängerkalibrierung oder lokalen Störpegel. Dekodierergebnisse und Performance-Empfangsgelegenheiten bleiben die tatsächlich beobachteten.

Das WSPR-Sendeleistungsfeld enthält den in der Sendesoftware eingestellten und gemeldeten Wert. Es enthält keine fortlaufenden Messungen der tatsächlichen HF-Ausgangsleistung. Wenn derselbe gemeldete Sendeleistungswert für alle zusammengefassten Beobachtungen gilt und die Datenauswahl unverändert bleibt, addiert die Normierung einen konstanten Versatz: Absolute Mittelwerte, Mediane und KI-Grenzen verschieben sich; stationsbezogene Abweichungen und KI-Breiten bleiben unverändert.

Tatsächliche Leistungsschwankungen, die dieses gemeldete Feld nicht abbildet, bleiben in beiden Darstellungen enthalten. Ein Betreiber kann das konfigurierte Feld während des Laufs ändern; dann kann der Versatz von Beobachtung zu Beobachtung verschieden sein, und die Aussage über einen konstanten Versatz gilt nicht mehr. Weder aus ursprünglichem noch aus normiertem SNR allein lässt sich erkennen, ob Sendeleistung, Ausbreitung oder Empfangsbedingungen eine Änderung verursacht haben.

**Mehrere Empfangsberichte zählen weiterhin als eine Beobachtung je Aufbau, Gegenstation und Zyklus.** TX Performance behält das höchste geeignete SNR auf der gewählten Bezugsgröße des abgeschlossenen Laufs: das gemeldete Empfangs-SNR bei ausgeschalteter oder das normierte SNR bei eingeschalteter Normierung. RX Performance und beide Seiten von Benchmark behalten jeweils das höchste geeignete normierte SNR. Aufeinanderfolgende Zyklen werden niemals zusammengefasst. Bei unterschiedlichen gemeldeten Leistungen können ursprüngliches und normiertes Maximum aus verschiedenen Berichten stammen. Die Auswahl erfolgt während der Datenerfassung. Ein bereits normiertes Maximum lässt sich im Allgemeinen nicht in den ursprünglichen Bericht mit dem höchsten SNR zurückrechnen.

Die <strong class="defined-term">Regel des stärksten Empfangsberichts</strong> beschreibt den stärksten gemeldeten Empfang statt eines mittleren Werts der verfügbaren Berichte. Schwächere Mehrfachmeldungen, sekundäre Dekodierungen oder unerwünschte Signalrepliken können dieses Maximum nicht senken. Umgekehrt kann ein fehlerhaft hoher Bericht zum beibehaltenen Wert werden. Ein Aufbau mit mehr beitragenden Empfängern oder Berichten hat mehr Gelegenheiten, einen hohen Wert zu liefern. Auch WsprDaemon dokumentiert die Auswahl des besten SNR beim Zusammenführen von Empfängern für WSPRnet <a href="#ref-11">[Ref-11]</a>.

Dieses Vorbild belegt nicht, dass das Maximum das beabsichtigte Signal ist oder beide Aufbauten dieselbe Spektralkomponente ausgewählt haben. Arithmetische Mittelwerte und Mediane würden andere Eigenschaften der verfügbaren Empfangsberichte beschreiben; keine dieser statistischen Größen identifiziert für sich allein die beabsichtigte Komponente. Spätere Mediane fassen die beibehaltenen Werte zusammen und können diese frühere Auswahl nicht rückgängig machen.

**Die Benchmark-Diagramme zu Dekodierungen und Stationen verwenden eine andere SNR-Bezugsgröße.** <strong class="defined-term">Dekodierungen und Stationen: Von starken Signalen zum Schwachsignalempfang</strong> behält für jeden Aufbau je Gegenstation und Zyklus das höchste **ursprünglich gemeldete SNR** bei. Weder die Normierung auf 30 dBm noch die Referenzkorrektur wird angewandt. Die Kurven zählen beobachtete Spots und Stationen ab bestimmten SNR-Untergrenzen; sie ersetzen das normierte gepaarte ΔSNR nicht. Sie verwenden die berücksichtigten Stationen und Beobachtungen in den gewählten Entfernungen und Richtungen der Segmentdetails, einschließlich aller gepaarten und einseitigen Beobachtungen. Eine andere Auswahl aktualisiert Kurven und Anzahlen, während die SNR-Bezugsgröße gleich bleibt. Ihre Rolle im Vergleich erläutern [RX Benchmark](#sec-3-rx-benchmark) und [TX Benchmark](#sec-3-tx-benchmark).

Wie schneiden die beiden Aufbauten ab, wenn Signale im Verhältnis zum Rauschen schwächer werden und sich den Grenzen der WSPR-Dekodierung nähern? Diese Kurven beziehen schrittweise Empfangsberichte mit niedrigerem SNR ein und zeigen, wie die Zahl dekodierter Spots und unterschiedlicher Stationen wächst. Sie enthalten auch **einseitige Dekodierungen**: Empfang, der nur für einen Aufbau aufgezeichnet wurde und den das gepaarte ΔSNR nicht erfassen kann.

Die oberen Panels heißen **„Paired spots“**, **„One-sided spots“** und **„All decoded spots“**. Die unteren Panels heißen **„Stations with paired spots“**, **„Exclusive stations“** und **„All observed stations“**. **„Exclusive stations“** bezeichnet Stationen, zu denen innerhalb der gesamten Auswahl Berichte für nur einen Aufbau vorliegen. Stationen mit Berichten für beide Aufbauten, aber ohne Spot-Paar, erscheinen getrennt in der Angabe **„Both observed, no pairs: +n stations“**; sie sind in **„All observed stations“** enthalten, nicht in den Kurven der exklusiven Stationen.

Bei **„≥ −20 dB“** liest du die Anzahl der Empfangsberichte mit einem gemeldeten SNR von −20 dB oder höher ab. Die Stationspanels zählen Stationen mit mindestens einem berücksichtigten Empfangsbericht, der diesen Grenzwert erreicht. Nach rechts sinkt der Grenzwert, und schwächere Empfangsberichte kommen hinzu. Jeder Endpunkt umfasst sämtliche Beobachtungen, die im ausgewählten Bereich zum jeweiligen Panel gehören. Beispielsweise umfasst **≥ −20 dB** Empfangsberichte bei −20 dB und allen höheren SNR-Werten, etwa −15 oder −10 dB; Empfangsberichte bei −21 oder −25 dB sind ausgeschlossen. **Dies ist ein Zählfilter für bereits dekodierte Empfangsberichte, keine Einstellung der Empfängerempfindlichkeit.** Alle drei Panels einer Zeile verwenden identische, bei null beginnende Y-Achsengrenzen, Teilstriche und Zähleinheiten; Spot- und Stationszeile haben getrennte Skalen.

Jede Kurve verwendet das ursprünglich gemeldete SNR des jeweiligen Aufbaus, ohne Leistungsnormierung oder SNR-Korrektur der Referenz. Die rechten Endpunkte zeigen die Summen des jeweiligen Panels. In **„All decoded spots“** und **„All observed stations“** gilt: Spots = gepaart + einseitig; Stationen = Stationen mit Spot-Paaren + beidseitig beobachtete Stationen ohne Spot-Paare + ausschließlich von diesem Aufbau beobachtete Stationen. Die drei Stationskategorien zerlegen nicht die Spot-Anzahlen. Ihre Summenbeziehung am Endpunkt muss bei früheren Grenzwerten nicht gelten: Der stärkste einseitige Bericht einer Station kann stärker sein als ihr stärkster gepaarter Bericht.

Ein Anstieg zwischen benachbarten Grenzwerten zählt die Empfangsberichte – oder neu hinzukommenden Stationen – in diesem SNR-Intervall. Der horizontale Abstand zwischen den Kurven gepaarter Spots ist nicht die Verteilung des gepaarten ΔSNR. Das SNR der Seite ohne Empfangsbericht ist unbekannt.


<a id="sec-7-activity-eligibility"></a>
<a id="sec-7-3"></a>
##### 8.1.3 Betriebsbedingungen und Zulässigkeit

**Ein kontrollierter Benchmark beruht auf unabhängig bekanntem gemeinsamem Betrieb.** In RX müssen beide Empfänger während des gesamten Vergleichszeitraums auf dem gewählten Band mit funktionierender Übermittlung der Empfangsberichte empfangen haben. Bei simultanem TX müssen beide Sender in denselben WSPR-Zyklen gesendet haben. Die gemeinsame Benchmark-Bestätigung dokumentiert, dass der gemeinsame Betrieb bestätigt oder seine Einschränkungen akzeptiert wurden; erfolgreiche Datenbank-Empfangsberichte können den Betrieb nicht unabhängig überprüfen.

**Wenn der gemeinsame Betrieb nicht verifiziert ist, ist die Interpretation eingeschränkt.** Historische Empfangsberichte können beobachtete Unterschiede beschreiben, ohne einen kontrollierten Versuch zu belegen. Dieselben Berechnungen der beobachteten Ergebnisse und des gepaarten ΔSNR gelten; einseitige Anzahlen können jedoch auch Zeitpläne, Ausfälle oder Unterbrechungen der Berichtsübermittlung widerspiegeln. Jeder Benchmark verwendet [dasselbe Bestätigungsfeld](#sec-5-3); siehe auch [historische und eingestellte Designs](#sec-7-neighborhood).

Benchmark verwendet für beide Aufbauten dieselben Regeln zum Zusammenfassen der Berichte je Gegenstation und Zyklus sowie dieselben Stationsfilter. Eine fehlende Target-Dekodierung schließt Berichte nur der Referenz nicht aus, selbst wenn zum Target in diesem Zyklus oder im gesamten Zeitraum nirgendwo Berichte vorliegen. Dasselbe gilt umgekehrt für Berichte nur des Targets. Fehlt auf beiden Seiten ein Bericht, gibt es kein beobachtetes Ergebnis; WSPRadar ergänzt keine künstliche Zeile „beide nicht dekodiert“.

**Performance wertet einen Zyklus nur aus, wenn Empfangsberichte die Aktivität des Targets auf dem gewählten Band belegen.** Diese Auswahl heißt <strong class="defined-term">Konditionierung auf Target-Aktivität</strong>.

| Richtung | Was belegt die Target-Aktivität in diesem Zyklus? |
|---|---|
| **RX** | Der Target-Empfänger hat mindestens eine geeignete Dekodierung hochgeladen. |
| **TX** | Mindestens ein geeigneter Empfangsbericht einer Target-Aussendung liegt irgendwo vor. |

Die Target-Aktivität wird vor der geografischen Filterung geprüft. Der dafür verwendete Bericht kann von außerhalb der Entfernungsgrenze der Analyse oder des gerade untersuchten Bereichs stammen. Er kann auch eine Station betreffen, die später wegen eines besonderen Rufzeichens oder wechselnden Standorts ausgeschlossen wird. Ein solcher Bericht belegt Aktivität, ohne die ausgeschlossene Station wieder aufzunehmen oder ihre Beobachtung zum ausgewählten Bereich hinzuzuzählen. Für die exportierten Dateien gelten weiterhin die in [Abschnitt 9.4](#sec-8-4) beschriebenen Bereiche.

Ein Zyklus ohne Bericht, der die Aktivität belegt, wird ausgeschlossen. WSPRadar kann einen Ausfall nicht von Betrieb unterscheiden, der keine gemeldete Dekodierung erzeugt hat. Performance beschreibt deshalb Zyklen mit nachweisbarer Target-Aktivität und nicht die gesamte verstrichene Zeit oder alle geplanten Aussendungen.

Target-Aktivität allein macht eine fehlende Meldung einer Gegenstation noch nicht zu einer verpassten Empfangsgelegenheit. Berichte müssen auch die Aktivität des betreffenden Senders oder Empfängers belegen, wie in [Abschnitt 8.3.1](#sec-7-performance-opportunities) beschrieben.


<a id="sec-7-benchmark"></a>
#### 8.2 Benchmark: Unterschiede und gemeinsame Datengrundlage

Benchmark beschreibt zwei Aspekte desselben Vergleichs: **die SNR-Differenz, wenn für beide Aufbauten nutzbare Empfangsberichte vorliegen**, und **die Dekodierergebnisse über alle beibehaltenen Beobachtungen**. Der erste benötigt ein Spot-Paar; der zweite umfasst auch Empfangsberichte nur einer Seite. Halte diese Populationen bei der Interpretation eines Ergebnisses auseinander.


<a id="sec-7-benchmark-outcomes"></a>
<a id="sec-7-6"></a>
##### 8.2.1 Dekodierergebnisse und fehlende Beobachtungen

**Klassifiziere zunächst jede Gegenstation und jeden WSPR-Zyklus.** Nach Zusammenfassung und Filterung gibt es drei Ergebnisse:

| Ergebnis | Beobachtungsdaten dieser Station in diesem Zyklus |
|---|---|
| <strong class="defined-term">Only Target</strong> | Ein Empfangsbericht auf der Target-Seite, ohne Empfangsbericht auf der Referenzseite. |
| <strong class="defined-term">Paired</strong> | Empfangsberichte für beide Aufbauten zur selben Gegenstation im selben Zyklus. Nutzbares SNR auf beiden Seiten liefert ΔSNR. |
| <strong class="defined-term">Only Reference</strong> | Ein Empfangsbericht auf der Referenzseite, ohne Empfangsbericht auf der Target-Seite. |

Dies sind Ergebnisse auf <strong class="defined-term">ursprünglicher Zyklusebene</strong>: zugeordnete, zusammengefasste und wissenschaftlich gefilterte Beobachtungen auf Ebene der ursprünglichen WSPR-Zyklen, vor der Zusammenfassung für die Darstellung.

Es gibt kein viertes Ergebnis „beide nicht dekodiert“: Hat keine Seite die Station gemeldet, liefert die Datenbank kein beobachtetes Ereignis. Benchmark behält einseitige Beobachtungsdaten symmetrisch bei, ohne separaten Nachweis der Target-Aktivität. Ein Spot-Paar liefert auch dann ΔSNR, wenn sein Kartensegment die Stationsanzahl- oder KI-Präzisionsanforderung nicht erfüllt.

**Klassifiziere anschließend jede Station über den gefilterten Vergleichszeitraum.** Eine Station kann in verschiedenen Zyklen unterschiedliche Ergebnisse auf ursprünglicher Zyklusebene haben. Die ΔSNR-Karte fasst diesen Verlauf in vier sich gegenseitig ausschließenden Stationsklassen zusammen:

| Stationsklasse | Bedeutung über den Vergleichszeitraum |
|---|---|
| <strong class="defined-term">Paired (qualifying)</strong> | Beibehaltene gepaarte Beobachtungen; kräftig grün dargestellt. |
| <strong class="defined-term">Both observed, no pairs</strong> | Zur Station liegen Berichte für beide Aufbauten vor, jedoch immer aus unterschiedlichen Zyklen. |
| **Only Target** | Alle berücksichtigten Berichte zu dieser Station betreffen nur das Target. |
| **Only Reference** | Alle berücksichtigten Berichte zu dieser Station betreffen nur die Referenz. |

Die Klasse einer Station ändert ihre einzelnen Beobachtungen nicht. Eine Station mit Spot-Paaren kann auch Ereignisse nur des Targets oder nur der Referenz beitragen. **Both observed, no pairs** ist eine Stationsklasse, niemals ein viertes Spot-Ergebnis. Die ΔDecode-Karte verwendet eine grüne Kategorie für gepaarte Stationen; alle vier Stationsklassen gehören weiterhin zu den beobachteten Stationen.

Unter Dekodierungen und Stationen steht die Karte **Spots** links und die Karte **Stationen** rechts; beide beschreiben alle beibehaltenen beobachteten Daten derselben aktuellen Auswahl. Jede Karte erläutert ihre Zähleinheit und zeigt danach die Gesamtzahl der <strong class="defined-term">Vereinigungsmenge</strong>: Beobachtungen von **mindestens einem** Aufbau, wobei gemeinsame Beobachtungen nur einmal zählen. Der farbige Aufteilungsbalken und seine Legende zerlegen diese Vereinigungsmenge in sich gegenseitig ausschließende Gruppen. Grün bezeichnet gepaarte Beobachtungen, Bernsteinfarben beidseitig beobachtete Stationen ohne Spot-Paare, Magenta Beobachtungen nur des Targets und Cyan Beobachtungen nur der Referenz.

Die Tabellen enthalten die Spalten **Aufschlüsselung**, **Target** und **Referenz** mit den tatsächlichen Rufzeichen sowie **Vereinigungsmenge**. Unter **Spots** stehen die Zeilen **Gepaarte Spots**, **Einseitig · Target dekodiert**, **Einseitig · Referenz dekodiert** und **Alle dekodierten Spots**. Ein Spot-Paar trägt eins zu jeder Aufbausumme, aber nur eins zur Vereinigungsmenge bei. Daher gilt: **Vereinigungsmenge = Target-Gesamtzahl + Referenz-Gesamtzahl − Spot-Paare**. Einseitige Spots bleiben in ihrer ursprünglichen Ergebniszeile, auch wenn ihre Station an anderer Stelle gepaarte Beobachtungen hat.

Unter **Stationen** gehört jede exakte Kombination aus Rufzeichen und vollständigem Locator zu einer von vier Gruppen: **Stationen mit gepaarten Spots**, **beidseitig beobachtet, keine Spot-Paare**, **Ausschließlich Target** oder **Ausschließlich Referenz**. Die abschließende Zeile **Alle beobachteten Stationen** addiert diese Gruppen. Eine Station mit Berichten für beide Aufbauten zählt einmal in jeder Aufbausumme und einmal in der Vereinigungsmenge, unabhängig davon, ob ein Spot-Paar desselben Zyklus vorliegt. Daher gilt: **Vereinigungsmenge = Target-Gesamtzahl + Referenz-Gesamtzahl − Stationen mit Spot-Paaren − beidseitig beobachtete Stationen ohne Spot-Paare**. Die ausgerichtete Spots-Zeile für **beidseitig beobachtet, keine Spot-Paare** bleibt bewusst leer, weil dies eine Stationsklasse über den Beobachtungszeitraum und kein viertes Spot-Ergebnis ist. Diese Tabellen beobachteter Anzahlen behalten alle gepaarten und einseitigen Beobachtungen bei; ΔSNR verwendet die gepaarten Beobachtungen.

Die nachfolgenden Karten der **Benchmark-Statistik** enthalten Median, Mittelwert, das jeweils verfügbare Konfidenzintervall und ΔDecode. Die Karte **Stationen** mittelt die Stationsmittelwerte der für ΔSNR berücksichtigten Stationen und zeigt das Konfidenzintervall dieses Mittelwerts. Die Karte **Spots** fasst deren Paare zusammen und zeigt den Mittelwert über diese Paare mit seinem eigenen Konfidenzintervall.

Die Unterüberschriften der Statistik geben die jeweilige Datengrundlage an: Stationen und Empfängerdekodierungen für ΔDecode, qualifizierende Spot-Paare für dessen ΔSNR-Histogramm und dieselben qualifizierten Stationen für die Histogramme der Stationsmittelwerte und Stationsmediane. Die Detaildaten behalten die drei ursprünglichen Ergebnisse bei. Die zeitliche Abdeckung zählt Stationen und Ereignisse je Station und Zyklus getrennt, wie in [Abschnitt 8.2.4](#sec-7-benchmark-coverage) erläutert.

**Fehlende Empfangsberichte haben kein gemessenes SNR.** WSPRadar rekonstruiert weder das SNR der fehlenden Seite noch weist es ein künstliches ΔSNR zu. Tatsächliche Sendeleistung, Ausbreitung, Störungen und Dekoderverhalten beeinflussen, welche Signale dekodiert werden. Eine falsche gemeldete Sendeleistung kann das normierte ΔSNR verzerren; die Leistungsnormierung ändert die bereits beobachteten Dekodierergebnisse nicht. Die Voraussetzung, dass beide Seiten dekodieren, kann Schwachsignalbedingungen unterrepräsentieren. Fehlende Spot-Paare sollten deshalb nicht als zufällige Auslassungen behandelt werden.

Interpretiere einseitige Beobachtungsdaten bei einem kontrollierten Benchmark unter dem unabhängig festgestellten gemeinsamen Betrieb aus [Abschnitt 8.1.3](#sec-7-activity-eligibility). Bei der Auswertung historischer Empfangsberichte bleibt diese Betriebsvoraussetzung ungeprüft.

**Identitätsfehler bei erweitertem WSPR sind ein eigenständiges Datenqualitätsproblem.** Typ 3 verwendet einen 15-Bit-Rufzeichenhash. Ein nicht aufgelöster oder kollidierender Hash kann eine Dekodierung ohne Identität lassen oder einem falschen Rufzeichen, Locator oder Leistungswert zuordnen, wie von QRP Labs dokumentiert <a href="#ref-28">[Ref-28]</a>. WSPRadar kann die gespeicherte Identität zuordnen, aber nicht jede vorgelagerte Zuordnung als korrekt belegen. Gehäufte oder ungleich verteilte Fehler können Stationszahlen, einseitige Ergebnisse und SNR-Zusammenfassungen verändern; ein großer Datensatz oder ein Median garantiert keinen Schutz. Verwende für zusammengesetzte Rufzeichen die Datenbank-Vorprüfung und die phasenspezifische Prüfung in [Kapitel 5](#sec-simultaneous-tx-setup).


<a id="sec-7-benchmark-delta"></a>
<a id="sec-7-5"></a>
##### 8.2.2 Delta SNR und Referenzkorrektur

Die **Referenzkorrektur** bildet einen unabhängig festgestellten additiven Versatz ab. Sie wird zum normierten Referenz-SNR addiert:

$$SNR_{\mathrm{Reference,corr}}=SNR_{\mathrm{Reference,norm}}+C_{\mathrm{Reference}}$$

Dabei ist `C_Reference` die vorzeichenbehaftete Korrektur in dB. Gib einen gemessenen Kalibrierversatz mit dem Vorzeichen `target - reference` ein. Der Versatz muss über das betreffende Band, die Signalpegel, den Gerätezustand und die Zeit annähernd stabil sein. [Abschnitt 10.3](#sec-5-3) beschreibt das Bedienelement und [Kapitel 6](#sec-reference-snr-calibration) das Kalibrierverfahren.

Ziehe für jedes Spot-Paar das korrigierte Referenz-SNR vom normierten Target-SNR ab:

$$\Delta SNR=SNR_{\mathrm{Target,norm}}-SNR_{\mathrm{Reference,corr}}$$

| ΔSNR | Bedeutung für dieses Spot-Paar |
|---|---|
| **Positiv** | Das Target-SNR ist höher. |
| **Null** | Target-SNR und korrigiertes Referenz-SNR sind gleich. |
| **Negativ** | Das Referenz-SNR ist höher. |

**Vorzeichenprüfung.** Auf normierter Grundlage ergibt Target `−10 dB` minus Referenz `−12 dB` **+2 dB**. Eine Referenzkorrektur von `+1.5 dB` hebt die Referenz auf `−10.5 dB` an; es bleiben **+0,5 dB**. Eine positive Korrektur verringert den berichteten Target-Vorteil; sie verändert die Target-Beobachtung nicht.

In RX beobachten beide Empfänger denselben Sender. Seine Terme der gemeldeten Sendeleistung heben sich auf, **wenn beide beibehaltenen Empfangsberichte denselben Leistungswert enthalten**. TX vergleicht unterschiedliche Aussendungen; die normierte Differenz hängt deshalb direkt von deren gemeldeten Leistungen ab. Unkorrigierte Geräteunterschiede bleiben in beiden Vergleichen enthalten. ΔSNR beschreibt die dokumentierten vollständigen Aufbauten; die Zuordnung zu einer Antenne oder einem anderen Bauteil erfordert die Kontrollen aus [Kapitel 2](#sec-3).


<a id="sec-7-benchmark-aggregation"></a>
<a id="sec-7-7"></a>
##### 8.2.3 Aggregation nach Station und Karte

**Was erfüllt die Anforderungen für ΔSNR?**

Eine Gegenstation **erfüllt die Anforderungen für ΔSNR**, wenn nach den Stations-, UTC-, Sonnenstands- und geografischen Filtern des Analyselaufs gepaarte Beobachtungen verbleiben. Jede Station wird anhand von exaktem Rufzeichen und vollständigem gemeldetem Locator gezählt, wie in [Abschnitt 8.1.1](#sec-7-spots-identities-cycles) definiert. Die Prüfung gilt für den vollständigen gefilterten Vergleichszeitraum; sie wird nicht für jedes Zeitintervall, jede Stationsauswahl oder jeden Zoom wiederholt. Diese Stationen liefern die Daten für ΔSNR-Karte, Histogramme, zeitliche Zusammenfassungen und Ausreißeranalyse.

Alle Spot-Paare und einseitigen Beobachtungen bleiben in Abdeckung, Stationsauswertung, Detaildaten und Exporten erhalten. Für die einseitige Anzahl einer Station gibt es keine eigene Mindestanforderung. Beispielsweise liefern sowohl `100 Paired / 8 Only Target / 4 Only Reference` als auch `4 / 100 / 100` gepaartes ΔSNR. Die beobachteten Anzahlen bleiben in beiden Fällen unverändert. Die Anforderung gepaarter Beobachtungen für ΔSNR ändert weder ΔDecode noch das Verhältnis der Stationszahlen.

**Wie die ΔSNR-Karte qualifizierte Paare zusammenfasst**

1. Bestimme die berücksichtigten Spot-Paare jeder Station über den vollständigen gefilterten Vergleichszeitraum: nach den wissenschaftlichen Filtern und vor der Auswahl von Kartensegmenten oder Zeitbereichen für die Anzeige.
2. Fasse innerhalb des Kartensegments die geeigneten gepaarten ΔSNR-Werte dieser Stationen zusammen. Jedes ursprüngliche Paar zählt einmal; einseitige Beobachtungen liefern kein gepaartes ΔSNR.
3. Berechne den <strong class="defined-term">arithmetischen Mittelwert der zusammengefassten gepaarten Differenzen</strong> mit **gleichem Gewicht je Paar**. Eine Station mit mehr qualifizierten Paaren trägt stärker zu diesem Kartenwert bei.
4. Berechne aus denselben gepaarten Differenzen das nominelle zweiseitige <strong class="defined-term">IID-Student-t-Konfidenzintervall</strong> anhand ihrer Stichprobenstandardabweichung, der Paaranzahl N und des gemeinsamen Konfidenzniveaus.
5. Zähle die Stationen, die die ΔSNR-Anforderungen erfüllen und mindestens ein geeignetes Paar zu diesem Segment beitragen. Färbe das Segment nur, wenn ihre Anzahl die eingestellte Mindestzahl erreicht und das Konfidenzintervall verfügbar und nicht entartet ist, mit einer **ungerundeten Halbbreite höchstens gleich dem gewählten KI-±-Grenzwert**.

Dieser Kartenschätzer entspricht dem Mittelwert und Konfidenzintervall der Karte **Spots** im separaten Abschnitt **Benchmark-Statistik**, wenn der gewählte Bereich genau dieselben qualifizierten Paare, SNR-Anpassungen und dasselbe Konfidenzniveau umfasst. Er unterscheidet sich vom gleich gewichteten **Mittelwert der Stationsmittelwerte** in der Karte **Stationen** und im Histogramm der Stationsmittelwerte.

Der Kartenmittelwert beschreibt die durchschnittliche berücksichtigte Paardifferenz im Segment. Jedes Paar zählt gleich viel. Eine Station mit mehr Paaren beeinflusst das Ergebnis deshalb stärker. Ob eine Station berücksichtigt wird, entscheidet sich über den vollständigen gefilterten Zeitraum. Die separate Zusammenfassung **Stationen** gibt dagegen jeder berücksichtigten Station dasselbe Gewicht. Die Karte gewichtet weder Stationsmittelwerte noch Stationsmediane gleich und mittelt keine Konfidenzintervalle einzelner Stationen oder Segmente. Ihr Konfidenzintervall verwendet die Stichprobenstandardabweichung aller beitragenden Paardifferenzen, einschließlich der Streuung innerhalb und zwischen Stationen. Diese Streuung zu berücksichtigen, korrigiert den Standardfehler nicht für Abhängigkeiten zwischen Beobachtungen.

Der <strong class="defined-term">Median über Spot-Paare</strong> verwendet dieselben berücksichtigten Paare wie der Kartenmittelwert. Er ist der mittlere Wert nach dem Sortieren oder bei gerader Anzahl der Mittelwert der beiden mittleren Werte. Mittelwert und Median geben jedem Paar gleiches Gewicht. Die separate Zusammenfassung der Stationsmediane gibt jeder berücksichtigten Station einen Beitrag. Auch wenn für jede Station gepaarte Beobachtungen vorliegen, können die Zusammenfassungen voneinander abweichen:

| Station | ΔSNR-Werte (dB) | Stationsmedian |
|---|---|---:|
| A | +6, +6, +6, +6, +6, +6 | +6 dB |
| B | −2, −2 | −2 dB |
| C | −1, −1 | −1 dB |

Der **Median der Stationsmediane beträgt −1 dB**, der **Median über sämtliche Spot-Paare dagegen +6 dB**. Der arithmetische Mittelwert der drei Stationsmediane beträgt **+1 dB**; der arithmetische Mittelwert über sämtliche Spot-Paare beträgt **+3 dB**. Jede Berechnung ist korrekt, gibt Stationen oder Extremwerten jedoch anderes Gewicht. Das Panel unten rechts zeigt die Stationsmediane und markiert ausschließlich ihren Median, den **Median der Stationsmediane**. Das separate Panel oben rechts zeigt die Stationsmittelwerte und markiert den **Mittelwert der Stationsmittelwerte**. In diesem Beispiel sind die Werte innerhalb jeder Station konstant; deshalb entspricht jeder Stationsmittelwert seinem Stationsmedian, und der Mittelwert der Stationsmittelwerte beträgt ebenfalls **+1 dB**. Dieses Segment mit drei Stationen kann die Stationsanforderung nur erfüllen, wenn deren Mindestzahl höchstens drei beträgt; den Standardwert drei erreicht es. Für die Karte erhält jedes der zehn Paare gleiches Gewicht. Daraus ergibt sich der zusammengefasste Mittelwert **+3 dB**, nicht der Mittelwert **+1 dB** bei gleicher Stationsgewichtung. Vor einer Färbung muss auch sein Konfidenzintervall über alle Paare die gewählte Halbbreitenanforderung erfüllen. Alle Stations- und Paarzusammenfassungen im separaten Abschnitt **Benchmark-Statistik** behalten ihre bestehenden Definitionen.

**Vier unterschiedliche ΔSNR-Zusammenfassungen**

Die Tabelle **Stationen** berichtet zwei Zusammenfassungen mit gleicher Stationsgewichtung. **Mittelwert ΔSNR ± 95% KI** mittelt die einzelnen Stationsmittelwerte und zeigt die Halbbreite seines Konfidenzintervalls, soweit verfügbar. Das Label verwendet standardmäßig 95%; die Prozentangabe folgt dem gemeinsamen Konfidenzniveau. **Median ΔSNR** ist der Median der einzelnen Stationsmediane, ohne Konfidenzintervall für den Median. Beide verwenden dieselben Stationen, die die ΔSNR-Anforderungen erfüllen, und gewichten jede Station gleich. Die Tabelle **Spots** berichtet Mittelwert und Median aller zusammengefassten Paardifferenzen dieser Stationen; jedes Paar zählt gleich viel. Alle Mittelwerte sind arithmetische Mittel der bereits gebildeten Target-minus-Referenz-Differenzen in dB nach der bestehenden Verarbeitung und Korrektur.

In der Zusammenfassungskarte **Spots** zeigt **Mittelwert ΔSNR ± 95% KI** den Mittelwert und die Halbbreite seines Konfidenzintervalls gemeinsam in einer Zeile, beispielsweise **+1.21 ± 0.04 dB**; die Prozentangabe im Label folgt dem eingestellten Konfidenzniveau. Eine doppelte Trennlinie trennt **ΔDecode** in beiden Karten von den ΔSNR-Zusammenfassungen.

Ungleiche Paaranzahlen und asymmetrische Werte innerhalb einer Station machen den Unterschied sichtbar. Beide folgenden Stationen haben beibehaltene gepaarte Beobachtungen:

| Qualifizierte Station | Gepaarte ΔSNR-Werte (dB) | Paare | Stationsmittelwert | Stationsmedian |
|---|---|---:|---:|---:|
| A | 0, 0, +12 | 3 | +4 dB | 0 dB |
| B | +8, +8 | 2 | +8 dB | +8 dB |

Der **Mittelwert der Stationsmittelwerte beträgt +6 dB**: `(4 + 8) / 2`. Der **Mittelwert über alle Spot-Paare beträgt +5,6 dB**: `(0 + 0 + 12 + 8 + 8) / 5`. Der **Mittelwert der Stationsmediane beträgt +4 dB** und der **Median der Stationsmediane ebenfalls +4 dB**; diese Übereinstimmung macht sie nicht zu derselben Definition. Alle Berechnungen verwenden dieselben fünf Paare; kein Wert wurde ausgeschlossen.

Die Abbildung **Benchmark-Statistik** ordnet die Verteilungen in vier Panels an:

| Position | Englischer Paneltitel | Gleich gewichtete Einheit oder Gewicht |
|---|---|---|
| Oben links | **ΔSNR ± 95% CI - Qualifying spot pairs** | Ein ΔSNR-Wert je qualifiziertem Spot-Paar. |
| Unten links | **ΔDecode - Spot Decodes** | Target- plus Referenzdekodierzahl je Station. |
| Oben rechts | **ΔSNR ± 95% CI - Qualifying station means** | Ein arithmetischer Mittelwert je qualifizierter Station. |
| Unten rechts | **ΔSNR - Qualifying station medians** | Ein Median je derselben qualifizierten Stationen. |

Die Zusammenfassungstabellen folgen derselben Gruppierung: Spots links, Stationen rechts. Die rechten Panels zeigen dieselbe Stationsanzahl, gewichten jede Station gleich und verwenden gemeinsame Klassengrenzen und Achsenbereiche. Ihre einzigen Referenzlinien und Zahlenangaben in der Legende sind oben **„Mean of station means“** und unten **„Median of station medians“**. Sie entsprechen der Tabelle **Stationen**. Der Mittelwert der Stationsmediane bleibt in den Metadaten separat benannt.

Das Spot-Paar-Panel nennt Mittelwert und Median oberhalb des Diagramms. Auch zusammenfallende Markierungen behalten ihre tatsächlichen Positionen und beide Legendeneinträge. Die Prozentangabe in beiden Paneltiteln mit Mittelwert-Konfidenzintervall folgt dem gemeinsamen Niveau (standardmäßig 95%). Die Legende **„Mean of station means“** zeigt denselben Schätzwert und dieselbe aggregierte Halbbreite wie die Karte **Stationen**; dieses Intervall verwendet die Streuung zwischen den Stationsmittelwerten. Ein Intervall der Breite null wird ausdrücklich als entartet gekennzeichnet; ein nicht verfügbares Intervall wird als solches ausgewiesen und nicht durch null ersetzt.

Im Spot-Paar-Panel verbindet der Legendeneintrag **„Mean“** den Mittelwert über alle Paare mit der verfügbaren KI-Halbbreite als **Mittelwert ± Halbbreite** in dB. Dieses Konfidenzintervall beschreibt die Unsicherheit des Mittelwerts über alle Paare unter dem angegebenen Modell. Es beschreibt weder die Histogrammstreuung noch die Unsicherheit des Medians. Der Legendeneintrag **„Median“** bleibt separat.

Beide Stationshistogramme verwenden eine gemeinsame adaptive Klassenbreite: Aus den für beide Verteilungen getrennt berechneten positiven Kandidaten nach Freedman–Diaconis und Sturges wird die feinste Breite gewählt, auf eine 1/2/5-Stufe aufgerundet und bei Bedarf so vergrößert, dass der gesamte gemeinsame Wertebereich höchstens 40 Balken umfasst. Die Klasseneinteilung des Spot-Paar-Histogramms bleibt unverändert. Negative Klassen verwenden Referenz-Cyan, positive Klassen Target-Magenta; die Klasse, die null enthält, ist neutral grau. Eine neutrale Klasse kann auch von null verschiedene Werte enthalten.

Die Tabellen **Stationen** und **Spots** sowie alle vier Histogramme beschreiben die gewählte Analyse und den Bereich der Segmentdetails. Die Auswahl **Median / Mittelwert** für zeitliche Ansichten ändert sie nicht. Das <strong class="defined-term">Konfidenzintervall des Mittelwerts der Stationsmittelwerte</strong> wird unmittelbar aus den berücksichtigten Stationsmittelwerten berechnet. Dazu gehören auch Beiträge aus schraffierten Kartensegmenten. Jeder Stationsmittelwert verwendet die geeigneten Paare dieser Station innerhalb der Auswahl; jede Station zählt gleich viel. Die Zusammenfassung **Spots** fasst die geeigneten Paare zusammen und liefert ihren eigenen Mittelwert mit Konfidenzintervall.

Bei genau denselben Paaren eines Segments, SNR-Anpassungen und demselben Konfidenzniveau stimmen Kartenmittelwert und -intervall mit dem zusammengefassten Spots-Ergebnis überein. Um Segmente zusammenzufassen, werden ihre geeigneten Paare zusammengeführt, statt ihre Mittelwerte oder Konfidenzintervalle zu mitteln. Eine Änderung allein des Grenzwerts für die Kartenhalbbreite ändert, welche Segmente eine Farbe erhalten; berücksichtigte Beobachtungen und Zusammenfassungen in den Segmentdetails bleiben gleich. Ein anderes gemeinsames Konfidenzniveau verändert die Mittelwertintervalle und möglicherweise die Kartenfärbung. Die Mittelwerte und beitragenden Beobachtungen bleiben dabei gleich.

Die Karte verwendet standardmäßig **drei qualifizierte Stationen je Segment**. Das Bedienelement für die Stationsmindestzahl akzeptiert **1–50**. Ein Rufzeichen bei `JO31AA` und dasselbe Rufzeichen bei `JO31AB` zählen getrennt, wenn beide qualifiziert sind und ein geeignetes Paar zum Segment beitragen. Dies sind gemeldete Identitäten, keine nachweislich unabhängigen physischen Standorte.

Tragen die beiden Identitäten beispielsweise jeweils ein Paar mit `+2` beziehungsweise `+4 dB` bei, beträgt der zusammengefasste Kartenmittelwert `+3 dB`, die Paaranzahl N **2** und die stützende Stationsanzahl **2**. Bei ungleichen Paaranzahlen folgt die Karte der Paargewichtung statt einer gleichen Stationsgewichtung. Stationsmindestzahl und Konfidenzintervallanforderung gelten gemeinsam. Ein Segment mit einer Station kann eine konfigurierte Stationsmindestzahl von eins erfüllen. Für eine Färbung benötigt es außerdem mindestens zwei beitragende Paare, eine beobachtete Paarvarianz größer null und ein verfügbares Konfidenzintervall, dessen ungerundete Halbbreite den gewählten Grenzwert einhält.

**Wogegen Mediane schützen**

Mediane verringern den Einfluss einzelner Extremwerte, ohne Beobachtungen zu löschen. Innerhalb einer Station hat `0, 0, 0, +2, +3 dB` den Median **0 dB** und den arithmetischen Mittelwert **+1 dB**. Über die Stationsmediane `+2, +3, +3, +4, −30 dB` beträgt der Median **+3 dB** und der arithmetische Mittelwert **−3,6 dB**. Der Extremwert verändert den arithmetischen Mittelwert wesentlich stärker; der Median belegt nicht, dass dieser Wert ein Fehler ist.

Bei einem Wert ist der Median dieser Wert; bei zweien ist er ihr arithmetischer Mittelwert. Eine dünne Datengrundlage bietet wenig Schutz. Mediane beseitigen keine systematischen Fehler, machen Beobachtungen nicht unabhängig und isolieren keinen Antenneneffekt. Wähle eine statistische Größe nach der Frage, die sie beantwortet, und nicht danach, welchen Aufbau sie begünstigt. [Abschnitt 8.5](#sec-7-claims) behandelt Inferenz und Wiederholbarkeit.

**Wie ΔDecode Beobachtungsdaten zählt**

Für das Segment bezeichne `J` gepaarte Ereignisse, `T` Ereignisse nur des Targets und `R` Ereignisse nur der Referenz. Die Dekodierzahl des Targets ist `A = J + T`, die der Referenz `B = J + R`. Fasse alle beibehaltenen Ereignisse zusammen, einschließlich Stationen ohne qualifizierendes ΔSNR:

$$r=\frac{A}{B}=\frac{J+T}{J+R}$$

Jedes gepaarte Ereignis trägt **eine Dekodierung zu jeder Seite** bei, zählt in der Vereinigungsmenge beobachteter Ereignisse `E = J + T + R` jedoch **einmal**. Die Nettozahl zusätzlicher Target-Dekodierungen ist `A − B = T − R`.

Für **70 gepaarte Ereignisse, 20 nur des Targets und 10 nur der Referenz**:

| Größe | Ergebnis |
|---|---:|
| Beobachtete Ereignisse, `E` | 100 |
| Dekodierzahlen Target / Referenz | 90 / 80 |
| Nettozahl zusätzlicher Target-Dekodierungen | 10 |
| ΔDecode, Verhältnis Target zu Referenz `90 / 80` | 1,125× |

**Lies ΔDecode als Verhältnisfaktor.** Ein Verhältnis Target zu Referenz von **2×** bedeutet doppelt so viele Target-Dekodierungen; **0,5×** bedeutet doppelt so viele Referenzdekodierungen. Gleiche von null verschiedene Anzahlen ergeben **1×**. Karten und vorzeichenbehaftete Diagrammachsen zeigen den Faktor der größeren gegenüber der kleineren Anzahl auf der Seite des begünstigten Aufbaus: **2× auf der Referenzseite** bezeichnet daher denselben Vergleich wie ein Verhältnis Target zu Referenz von **0,5×**. Hat nur eine Seite Dekodierungen, ist das Ergebnis **Exclusive**; ohne beobachtete Ereignisse ist es undefiniert.

Sind beide Anzahlen von null verschieden, ist der dargestellte Vorteilsfaktor die größere geteilt durch die kleinere Anzahl. Im Tabellenverhältnis Target zu Referenz ergeben Beobachtungsdaten nur des Targets **∞×** und Beobachtungsdaten nur der Referenz **0×**; dies sind die beiden exklusiven Fälle, keine endlichen Verhältnisfaktoren.

Bei unveränderten beibehaltenen Ereignissen und unverändertem Bereich kehrt ein Tausch von Target und Referenz die begünstigte Seite um und bildet den Kehrwert des endlichen Verhältnisses Target zu Referenz. Ein neuer Lauf mit einem anderen Target kann auch die auf das Target bezogene Geografie oder Sonnenstandsfilterung ändern und muss daher nicht dieselben Ereignisse beibehalten.

ΔDecode wird **über alle Ereignisse zusammen** berechnet und ist kein Mittelwert der ΔDecode-Werte einzelner Stationen. Häufig beobachtete Stationen tragen mehr Dekodierungen bei. Jedes beibehaltene Ereignis zählt, einschließlich einseitiger Ereignisse von Stationen, die auch Spot-Paare haben, sowie von Stationen, die die beiden Aufbauten in verschiedenen Zyklen beobachtet haben. Anzahlen unterschiedlicher Stationen allein können diese Kennzahl nicht reproduzieren.

**Wie das ΔDecode-Histogramm diesen Umfang darstellt**

Für jede Station seien `A_i` und `B_i` ihre beibehaltenen Target- und Referenzdekodierzahlen. Ordne ihren Vorteil auf der symmetrischen Verhältnisachse ein und gewichte ihn mit `A_i + B_i`. Die vertikale Achse **Share of receiver decodes (%)** zählt deshalb jedes gepaarte Ereignis doppelt. Dieser Prozentsatz beschreibt den Anteil an den Beobachtungsdaten, nicht die Größe des Dekodiervorteils. Die rote Linie markiert ΔDecode aus den zusammengefassten Target- und Referenzdekodierzahlen, **keinen Median, keinen arithmetischen Mittelwert von Stationsverhältnissen und keinen Mittelwert von Klassenmitten**. Die Verhältnisachse ist nicht linear.

Alle berücksichtigten Stationen im aktiven Bereich der Segmentdetails gehen ohne zusätzliche Mindestanforderung ein. Separate **Exclusive**-Balken an den Endpunkten enthalten Dekodierungen von Stationen, die ausschließlich auf einer Seite beobachtet wurden. Sie enthalten nicht alle einseitigen Ereignisse gemeinsam beobachteter Stationen. Die drei ΔSNR-Histogramme behalten ihre eigenen Qualifikationsregeln für Spot-Paare und Stationen; die Panels der Stationsmittelwerte und Stationsmediane verwenden genau dieselben berücksichtigten Stationen.

**Wann die Datengrundlage eines ΔDecode-Segments für eine Färbung ausreicht**

Beide Mindestanforderungen an die ΔDecode-Datengrundlage müssen erfüllt sein. Die **Mindestzahl beobachteter Stationen je Segment für ΔDecode** beträgt standardmäßig **3**, einstellbar von **1 bis 50**. Jede Station mit mindestens einem berücksichtigten Ereignis im Segment zählt einmal, einschließlich Stationen nur des Targets und nur der Referenz. Die Zähleinheit bleibt **Rufzeichen + vollständiger gemeldeter Locator**. Gepaarte Beobachtungen oder eine Qualifikation für ΔSNR sind nicht erforderlich.

Der Standard-Mindestanteil beträgt **1 % der beobachteten Ereignisse des vollständigen gefilterten Analyselaufs**, einstellbar von **0 % bis 5 %** in Schritten von **0,5 %**. Ein Segment muss zusätzlich mindestens folgende Anzahl enthalten:

$$N_{\min}=\left\lceil\frac{p}{100}\,E_{\mathrm{run}}\right\rceil$$

Dabei ist `p` der gewählte Prozentsatz, `E_run` zählt jedes beibehaltene Ereignis je Station und Zyklus einmal, und `ceil` bedeutet Aufrunden auf eine ganze Ereigniszahl. Die Gesamtzahl des Analyselaufs steht vor der Segmentqualifikation fest. Kartenausschnitt, Auswahl in den Segmentdetails und Farben unterhalb der Schwelle ändern sie nicht. Bei **0 %** erfüllt jedes nicht leere Segment die Anforderung an den Ereignisanteil; die Stationsmindestzahl gilt weiterhin. Die Stationsanforderung legt die Breite über beobachtete Stationen fest; die Anforderung an den Ereignisanteil begrenzt die Färbung bei geringer Datengrundlage relativ zum Lauf. Keine davon ist ein Konfidenzniveau oder eine Garantie unabhängiger Funkpfade, und eine häufig beobachtete Station kann die zusammengefassten Summen weiterhin dominieren. Beide Anforderungen steuern nur die Färbung: Alle beibehaltenen Ereignisse bleiben in der zusammengefassten ΔDecode-Berechnung und den Statistiken der Segmentdetails enthalten.

Beide Karten behalten die Marker beobachteter Stationen bei. Liegen Beobachtungen vor, aber die Anforderungen der jeweiligen Kennzahl sind nicht erfüllt, erhält das Segment **graue diagonale Schraffur (Not qualifying — Anforderungen nicht erfüllt)**. Ein ungefülltes Segment zeigt **No observations — Keine berücksichtigten Beobachtungen**, weil innerhalb des gewählten Bereichs nach den Filtern keine Beobachtungen für diese Karte verbleiben. Das belegt nicht, dass physisch kein Empfang stattfand. Null ΔSNR und **1× ΔDecode** sind gültige Ergebnisse und bleiben bei erfüllten Anforderungen farbig. Die Anforderungen für ΔSNR und ΔDecode gelten unabhängig voneinander. Ihre Farbskalen und die ΔDecode-Verhältnislegende erklärt [Abschnitt 8.4.6](#sec-7-view-spread).

Bei ΔSNR kann eine <strong class="defined-term">graue Schraffur</strong> zu wenige Stationen mit erfüllten ΔSNR-Anforderungen, ein nicht verfügbares oder entartetes Konfidenzintervall über die Paare oder eine Halbbreite oberhalb des gewählten Grenzwerts bedeuten. Wähle zur Prüfung die exakte Entfernung und Richtung des Segments in **Segmentdetails**. Lies anschließend den Mittelwert und **± Halbbreite** in der Karte **Spots** des separaten Abschnitts **Benchmark-Statistik** und prüfe die beitragenden Stations- und Paaranzahlen. Die Karte selbst zeigt kein numerisches Konfidenzintervall. Den genauen Grund mit voller Genauigkeit und den Intervallstatus findest du in `benchmark/map_segments.parquet` im Analysedownload; der Status in der Karte **Stationen** betrifft deren anderes Konfidenzintervall bei gleicher Gewichtung der Stationsmittelwerte.

Ohne beitragende Paare sind Kartenmittelwert und Konfidenzintervall nicht verfügbar. Bei einem Paar ist der Mittelwert definiert; Stichprobenstandardabweichung, Standardfehler und Konfidenzintervall sind jedoch nicht verfügbar. Bei **mindestens zwei beitragenden Paaren** ergeben identische gepaarte ΔSNR-Werte eine ungerundete Stichprobenstandardabweichung von genau null: Der Export behält die berechneten Intervallgrenzen der Breite null mit dem Status **degenerate** bei, und das Segment bleibt schraffiert. Ein Intervall der Breite null belegt keine physische Unsicherheit von null.

Identische **Stationsmittelwerte** allein machen das Konfidenzintervall über alle Paare nicht entartet: Die Differenzen innerhalb der Stationen können weiterhin streuen. Kleine positive Halbbreiten behalten genügend angezeigte Stellen, um sie von null zu unterscheiden. Die Qualifikation verwendet die ungerundete Halbbreite und verlangt nicht, dass das Konfidenzintervall null ausschließt; ein Mittelwert von null kann bei erfüllten Anforderungen qualifizieren. Die Schraffur entfernt keine geeigneten Paare oder Stationen aus den Statistiken der Segmentdetails. Untersuche die beitragenden Funkpfade und datierten Beobachtungen, bevor du die Anforderungen änderst: Eine größere zulässige Halbbreite oder niedrigere Stationsmindestzahl ändert die Annahmeregel, nicht die Qualität oder Unabhängigkeit der Beobachtungen.

**Interpretiere beide Karten gemeinsam.** ΔSNR beschreibt die gepaarte Signalqualität; ΔDecode beschreibt das Verhältnis der insgesamt beobachteten Dekodierungen. Sie können unterschiedliche Aufbauten begünstigen. Gleiche Dekodierzahlen können überwiegend aus gepaarten Ereignissen bestehen oder aus erheblichen einseitigen Beobachtungsdaten, die sich gegenseitig ausgleichen. Von beiden Seiten verpasste Ereignisse fehlen; ΔDecode ist deshalb weder eine unbedingte Dekodierwahrscheinlichkeit noch eine Gewinnquote des Targets. Nachweise gemeinsamen Betriebs, tatsächliche Leistung, Zeitpläne und die beobachtete Stationspopulation bleiben wesentlicher Kontext.


<a id="sec-7-benchmark-coverage"></a>
<a id="sec-7-8-2"></a>
##### 8.2.4 Zeitliche Dekodierabdeckung

**<strong class="defined-term">ΔDecode over Time</strong> trennt die Anzahl erfasster Gegenstationen vom Umfang der Dekodierungen.** Beide Zeilen verwenden alle beibehaltenen Ergebnisse unabhängig von der ΔSNR-Qualifikation.

| Zeile | Was die Balken je Zeitintervall zählen | Was die Linie vergleicht |
|---|---|---|
| <strong class="defined-term">Station-level</strong> | Jede Gegenstation einmal: **Both observed**, **Only Target** oder **Only Reference**. | <strong class="defined-term">Station Reach Advantage</strong>, aus den Anzahlen unterschiedlicher Stationen beider Aufbauten. |
| <strong class="defined-term">Spot-level</strong> | Jedes ursprüngliche Ereignis je Station und Zyklus einmal: **Paired**, **Only Target** oder **Only Reference**. | **ΔDecode**, aus den zusammengefassten Dekodierzahlen. |

**Beidseitig beobachtet bedeutet nicht zwingend gepaart.** Liegt für eine Station in einem Zyklus ein Bericht zum Target und in einem anderen ein Bericht zur Referenz vor, gehört sie innerhalb dieses Zeitintervalls zu **Both observed**. Ihre beiden Ereignisse bleiben trotzdem einseitig. **Paired** erfordert dieselbe Station im selben Zyklus. Bei RX sind die Gegenstationen Sender, bei TX Empfänger.

Für die Stationsabdeckung bezeichne `C` beidseitig beobachtete Stationen, `T_s` Stationen nur des Targets und `R_s` Stationen nur der Referenz. Die Stationszahl des Targets ist `A_s = C + T_s`, die der Referenz `B_s = C + R_s`:

$$r_{\mathrm{stations}}=\frac{A_s}{B_s}$$

Die Gesamtzahl des oberen Balkens ist die Vereinigungsmenge der Stationen `C + T_s + R_s`. Wiederholte Dekodierungen können sie nicht erhöhen. Eine zusätzliche Station bedeutet zusätzlich gegenüber dem anderen Aufbau in diesem Zeitintervall, nicht einen erstmaligen Kontakt oder eine kumulierte Entdeckung. Gleiche Stationszahlen müssen keine identischen Stationsmengen bedeuten.

Die untere Zeile vergleicht `(J + T) / (J + R)` gemäß [Abschnitt 8.2.3](#sec-7-benchmark-aggregation). Alle gepaarten Ereignisse verwenden eine grüne Kategorie, unabhängig von der ΔSNR-Qualifikation. Doppelte Empfangsberichte, die bereits zu einer Beobachtung je Station und Zyklus zusammengefasst wurden, erhöhen die Anzahlen nicht.

**Beide Sekundärachsen verwenden vorzeichenbehaftete Verhältnislabels.** Oberhalb des mittigen **1×** wird das Target begünstigt, unterhalb die Referenz. In der oberen Zeile bedeutet **2×** doppelt so viele Stationen, in der unteren doppelt so viele Dekodierungen. Lies den Faktor auf der Seite des begünstigten Aufbaus; dies sind keine linearen Verhältnisachsen. Exklusive Beobachtungen haben einen ausdrücklichen Endpunkt; Zeitintervalle ohne Datengrundlage bleiben Lücken. Die Abdeckung einer ausgewählten Station verwendet deren zusammengefasstes ΔDecode, nicht das Verhältnis der Stationszahlen.

<strong class="defined-term">Chronologische Ansichten</strong> erhalten die zeitliche Reihenfolge. Ansichten nach Tageszeit kombinieren Kalendertage gemäß [Abschnitt 8.4.4](#sec-7-view-folding), wobei die Stationszugehörigkeit für jeden Kalendertag und jede Stunde getrennt bestimmt wird. Der historische **Joint Evidence Share**, `J / (J + T + R)`, misst die gepaarte Überlappung und ist nicht mehr die zeitliche Linie. Keine der aktuellen Linien überprüft die Betriebsverfügbarkeit, zählt von beiden Seiten verpasste Ereignisse oder belegt einen kausalen Antennenvorteil.


<a id="sec-2-6"></a>
<a id="sec-3-rx-benchmark-local-median"></a>
<a id="sec-3-tx-benchmark-local-median"></a>
<a id="sec-7-neighborhood"></a>
##### 8.2.5 Kontrollierter Betrieb und eingestellte Designs

Ein kontrollierter Benchmark benötigt zwei eindeutig bezeichnete Aufbauten mit unabhängig festgestelltem gemeinsamem Betrieb. Ein wechselnder Nachbarschaftsmedian liefert diese feste Referenz nicht. **Reference Neighborhood wurde eingestellt**; frühere Konfigurationen, die es verwenden, werden abgewiesen. Wähle eine ausdrückliche Referenz und prüfe die Betriebsbedingungen für einen neuen kontrollierten Vergleich. Eingestellt wurde dieses Vergleichsverfahren; ein Median bleibt eine gültige Beschreibung der darin berücksichtigten Beobachtungen.

Das **historische Milazzo-Beispiel** bleibt als ausdrücklich gekennzeichnete Auswertung historischer Empfangsberichte verfügbar. Es erlaubt eine reproduzierbare Untersuchung gepaarter und einseitiger Berichte. Diese allein belegen weder synchronisierte Sendezeitpläne noch durchgängigen Betrieb. Ungleiche Zeitpläne können zu einseitigen Anzahlen beitragen. Beschreibe die Rekonstruktion daher anhand der beobachteten Ergebnisse, sofern nicht externe Betriebsaufzeichnungen die für einen kontrollierten Dekodiervergleich erforderlichen Bedingungen belegen.


<a id="sec-7-performance"></a>
<a id="sec-7-4"></a>
#### 8.3 Performance: Empfangsgelegenheiten und Dekodiererfolg

Performance zeigt, wo und wie regelmäßig Signale während bestätigter Empfangsgelegenheiten dekodiert wurden. Eine erfolgreiche Dekodierung durch das Target bei RX oder des Targets bei TX bestätigt die Empfangsgelegenheit bereits selbst. Als nicht dekodiert zählt WSPRadar eine Gelegenheit nur, wenn Empfangsberichte die Aktivität des Targets und der betreffenden Gegenstation auf demselben Band im selben WSPR-Zyklus belegen. Ein Zyklus ohne Empfangsbericht reicht dafür nicht aus.


<a id="sec-7-performance-opportunities"></a>
##### 8.3.1 Was zählt als Empfangsgelegenheit?

Jede Empfangsgelegenheit betrifft eine Gegenstation und einen WSPR-Zyklus auf dem gewählten Band, nach Anwendung der Stations- und geografischen Filter. **Station** steht hier für das exakte Rufzeichen und den vollständigen gemeldeten Locator; unterschiedliche Kombinationen werden getrennt gezählt. Wie die Target-Aktivität festgestellt wird, beschreibt [Abschnitt 8.1.3](#sec-7-activity-eligibility). Wer wen gemeldet haben muss, hängt von der Analyserichtung ab:

- **RX:** Das Target oder ein anderer zulässiger Empfänger hat den entfernten Sender dekodiert. Fehlt die Dekodierung beim Target, zählt dies nur dann als nicht dekodierte Gelegenheit, wenn ein anderer Empfänger diesen Sender gemeldet und das Target einen anderen Sender dekodiert hat — jeweils auf demselben Band im selben Zyklus.
- **TX:** Der entfernte Empfänger hat das Target oder einen anderen berücksichtigten Sender dekodiert. Fehlt seine Target-Dekodierung, zählt dies nur dann als nicht dekodierte Gelegenheit, wenn dieser Empfänger einen anderen Sender gemeldet hat und ein geeigneter Empfangsbericht die Aussendung des Targets auf demselben Band im selben Zyklus belegt.

Eine erfolgreiche Dekodierung bedeutet bei RX Empfang **durch das Target**, bei TX Empfang **des Targets durch diesen Empfänger**. Ist die Target-Aktivität festgestellt, zählt jede Kombination aus Station und Zyklus nur einmal:

| Dekodiert? | Belegen weitere Berichte die Aktivität der Gegenstation? | Ergebnis | Als Empfangsgelegenheit zählen? |
|---|---|---|---|
| Ja | Nein | Die erfolgreiche Dekodierung bestätigt ihre Empfangsgelegenheit selbst. | **Ja — einmal.** |
| Ja | Ja | Erfolgreiche Dekodierung mit zusätzlichen Aktivitätsbelegen. | **Ja — einmal.** |
| Nein | Ja | Bestätigte nicht dekodierte Gelegenheit: Beide Stationen waren aktiv, aber eine erfolgreiche Target-Dekodierung wurde nicht gemeldet. | **Ja — einmal.** |
| Nein | Nein | Unbekannt: Die Aktivität der Gegenstation wurde nicht festgestellt. | **Nein.** |

Erfolge ohne zusätzliche Aktivitätsbelege bleiben innerhalb der erfolgreichen Dekodierungen erkennbar. Zusätzliche Empfangsberichte zählen denselben Erfolg nicht erneut. Bei TX belegt der Bericht eines anderen Empfängers nicht, dass gerade dieser Empfänger zugehört hat. Bei RX kann ein anderer Empfänger die Aktivität des Senders bestätigen, aber nicht die Aktivität des Targets. Unbekannte Fälle bleiben ausgeschlossen und erhalten keinen erfundenen SNR-Wert.


**Zusätzliche Bestätigung bei wenigen Empfangsgelegenheiten.** Standardmäßig prüft ein serverseitig konfigurierter Filter Stationen mit **einer oder zwei bestätigten Empfangsgelegenheiten**. Gezählt wird nach den Stations-, Sonnenstands- und geografischen Filtern, aber **vor Anwendung der Anforderungen für die Aufnahme einer Station**. Zähleinheit bleibt das normalisierte Rufzeichen mit vollständigem gemeldetem Locator. Mindestens **einer** der betreffenden WSPR-Zyklen muss die folgende Bedingung erfüllen:

- **RX Performance:** Mindestens **drei unterschiedliche Empfängerrufzeichen außer Target** müssen denselben Sender mit demselben Rufzeichen und vollständigem Locator auf demselben Band im selben WSPR-Zyklus melden.
- **TX Performance:** Der überprüfte Empfänger muss in einem seiner Gelegenheitszyklen selbst eine Aussendung melden. Mindestens **drei weitere Empfängerrufzeichen**, ohne diesen Empfänger und ohne Target, müssen denselben Sender mit demselben Rufzeichen und vollständigem Locator auf demselben Band im selben Zyklus melden. Dies kann eine Target-Aussendung oder eine andere Aussendung sein, deren Empfang die Aktivität des überprüften Empfängers belegt. Berichte verschiedener Aussendungen dürfen nicht zusammengezählt werden, um die Anforderung zu erfüllen.

Jedes normalisierte Empfängerrufzeichen zählt je passender Aussendung und Zyklus einmal, unabhängig von doppelten Berichten oder unterschiedlichen Empfänger-Locatoren. Die Prüfung verwendet die zugrunde liegenden Empfangsberichte, bevor daraus die Aktivitätsmerkmale gebildet werden.

Die eingestellte **Mindestzahl bestätigter Empfangsgelegenheiten je Station** gilt weiterhin. Mit der standardmäßigen Obergrenze zwei kann die Zusatzprüfung bei Mindestzahlen von eins oder zwei wirken; ab drei hat sie keine zusätzliche Wirkung. Für Stationen mit mindestens drei Empfangsgelegenheiten gilt die bisherige Aufnahmeregel. Die Serverkonfiguration kann die Zusatzprüfung ausschalten oder ihre Obergrenze ändern; **drei weitere meldende Empfänger** sind stets erforderlich, wenn sie greift.

Die Prüfung entscheidet, ob eine Station in die Auswertung eingeht; sie entfernt keine einzelnen Zyklen. Für eine aufgenommene Station bleiben alle ursprünglichen Empfangsgelegenheiten, Erfolge, bestätigten Nichtdekodierungen und SNR-Beobachtungen erhalten. Eine ausgeschlossene Station ist **durch weitere Empfänger unzureichend bestätigt**, aber keine nachgewiesene Fehldekodierung. Verschiedene Empfängerrufzeichen belegen außerdem nicht, dass die Berichte von unabhängigen physischen Empfängern stammen. Der Analyseexport enthält die wirksame Regel des abgeschlossenen Laufs und die Angaben zur zusätzlichen Bestätigung.


<a id="sec-7-performance-rates"></a>
##### 8.3.2 Dekodierquoten und Gewichtung

Für jede berücksichtigte Station $i$ bezeichne $S_i$ erfolgreiche Empfangsgelegenheiten, $M_i$ bestätigte nicht dekodierte Gelegenheiten und $O_i=S_i+M_i$ alle bestätigten Empfangsgelegenheiten. Ihre Dekodierquote beträgt:

$$p_i=100\times\frac{S_i}{O_i}$$

Dabei ist $p_i$ ein Prozentsatz. Eine Station geht nur dann in die Berechnung ein, wenn $O_i$ die **Mindestzahl bestätigter Empfangsgelegenheiten je Station** erreicht und die zusätzliche Bestätigung vorliegt, sofern diese Prüfung greift. Das sind die qualifizierten Stationen. Dieselben $N$ Stationen gehen in beide Zusammenfassungen ein:

| Zusammenfassung | Berechnung | Was erhält gleiches Gewicht? |
|---|---|---|
| **Mittelwert der Stationsdekodierquoten** | $\frac{1}{N}\sum_{i=1}^{N}p_i$ | Jede berücksichtigte Station trägt eine Quote bei. |
| **Dekodierquote über alle Empfangsgelegenheiten** | $100\times\frac{\sum_{i=1}^{N}S_i}{\sum_{i=1}^{N}O_i}$ | Jede bestätigte Empfangsgelegenheit geht einmal in die zusammengefassten Anzahlen ein. |

Die mittlere Dekodierquote der Stationen beschreibt den Empfang über die Stationen hinweg: Jede Station zählt gleich viel, auch mit 0 % Erfolg. Die Quote über alle Empfangsgelegenheiten beschreibt dagegen, welcher Anteil dieser Gelegenheiten erfolgreich war. Erfüllt keine Station die Anforderungen, ist keine der Quoten definiert. Wird der **Median der Stationsdekodierquoten** gewählt, verwendet WSPRadar den Median der einzelnen Stationsquoten einschließlich null; siehe [Abschnitt 8.4.2](#sec-7-view-geography).

**Beispiel.** Zwei Stationen haben **90 Erfolge bei 100 Empfangsgelegenheiten** und **5 bei 10**. Ihre Quoten sind 90 % und 50 %, daher beträgt der Mittelwert der Stationsdekodierquoten **70 %**. Die gemeinsame Zählung ergibt **95 / 110 = 86,4 %**: 95 Erfolge und 15 nicht dekodierte Gelegenheiten, jeweils einmal gezählt. Die gemeinsame Quote ist höher, weil die erfolgreichere Station mehr Empfangsgelegenheiten beigetragen hat. Die beiden Werte beantworten unterschiedliche Fragen zur Gewichtung.


<a id="sec-7-performance-reach"></a>
##### 8.3.3 Mindestens einmal erfasste Gegenstationen

**At-least-once Peer Reach** ist der Prozentanteil berücksichtigter Stationen mit mindestens einer erfolgreichen Dekodierung. Bei RX sind das Sender, die das Target gehört hat; bei TX Empfänger, die das Target gehört haben. Sei $N$ die Anzahl berücksichtigter Stationen und $H$ die Anzahl davon mit mindestens einem Erfolg:

$$\text{Reach (\%)}=100\times\frac{H}{N}$$

$H$ ist die Anzahl; **Reach** gibt ihren Anteil an $N$ in Prozent an. Eine Station mit einem Erfolg und eine Station mit vielen Erfolgen tragen jeweils eins zu $H$ bei. Beide Stationen im Beispiel oben waren erfolgreich; ihre Reach beträgt daher **100 %**, trotz unterschiedlicher Dekodierquoten. Ohne berücksichtigte Stationen ist der Reach-Prozentsatz nicht definiert.

Bei einer festen Gruppe von Stationen können zusätzliche Beobachtungen einen früheren Erfolg nicht rückgängig machen. Welche Stationen die Anforderungen erfüllen, kann sich zwischen Analyseläufen jedoch ändern. Ein längerer Messzeitraum muss deshalb keinen höheren Reach-Prozentsatz ergeben.


<a id="sec-7-performance-snr"></a>
##### 8.3.4 Target-SNR erfolgreicher Dekodierungen

Das Target-SNR erfolgreicher Dekodierungen beschreibt beibehaltene erfolgreiche Dekodierungen, wobei die Zusammenfassung nach dem stärksten Empfangsbericht auf der gewählten SNR-Bezugsgröße des abgeschlossenen Laufs erfolgt, wie in [Abschnitt 8.1.2](#sec-7-normalization-consolidation) beschrieben. Nicht dekodierte Gelegenheiten haben kein gemessenes Target-SNR. Zusätzliche Dekodierungen nahe der Empfangsgrenze können eine Zusammenfassungsgröße des erfolgreichen SNR senken, selbst wenn sich Empfang und Anzahl erfasster Gegenstationen verbessern. Lies SNR deshalb zusammen mit Dekodierquote und Anzahlen.

Die Zeitdiagramme zeigen das SNR erfolgreicher Dekodierungen, die Dekodierquote und die zugehörigen Anzahlen, die Dekodierquote nach Entfernung und Zeit sowie die SNR-Abweichungen jeder Station von ihrem eigenen Mittelwert oder Median über den Lauf. Für eine ausgewählte Station erscheinen die ersten beiden Ansichten mit absolutem SNR auf der gewählten Bezugsgröße. [Abschnitt 8.4.3](#sec-7-view-time) erklärt die Zeitdiagramme, [Abschnitt 8.4.5](#sec-7-view-station) die Einzelstationsansicht. Die Ergebnisse beschreiben die im Meldenetz bestätigten Empfangsgelegenheiten. Sie messen weder die allgemeine Empfängerempfindlichkeit noch den Erfolg über sämtliche versuchten Aussendungen oder den absoluten Stationswirkungsgrad.

Öffne die **Expertenansicht**, um SNR-Abweichungen vom Mittelwert oder Median der jeweiligen Station über den Lauf zu untersuchen. [Abschnitt 8.4.3](#sec-7-view-time) erklärt diese optionale Ansicht und ihre Berechnung.


<a id="sec-7-views"></a>
<a id="sec-7-8"></a>
#### 8.4 Bereich und Zusammenfassungen über Raum und Zeit

Dieselben Daten können unterschiedliche Fragen beantworten, je nachdem, was gleiches Gewicht erhält. In der Performance-Karte zählt jede Station gleich viel; in der Benchmark-ΔSNR-Karte und der Verteilung über Spot-Paare zählt jedes Paar gleich viel. Eine Ansicht nach Tageszeit kann mehrere Kalendertage zusammenfassen. Dieser Abschnitt erklärt, welche Beobachtungen die einzelnen Ansichten verwenden und wie sie daraus ihre Ergebnisse berechnen.

<a id="sec-7-view-scope"></a>
<a id="sec-7-9"></a>
##### 8.4.1 Bereich, Geografie und Filter

Entfernung und Azimut werden aus dem Target-QTH und den gemeldeten Gegenstationslocatoren berechnet, mit einer kugelförmigen Erde von **6 371 km** Radius. Die azimutale äquidistante Karte ist auf das Target-QTH zentriert. Ihre Entfernungsgrenzen liegen bei **2 500**, **5 000**, **10 000**, **15 000** und ungefähr **20 015 km**, die Richtungssektoren sind **22,5 Grad** breit. Locatoren bezeichnen Rasterzellen, keine vermessenen Antennenstandorte. Die Berechnungen liefern daher weder vermessungstechnisch genaue Positionen noch gemessene Abstrahlwinkel.

**Maximale Entfernung der Gegenstationen vom Target** schließt Stationen **an oder jenseits** der gewählten numerischen Grenze aus, bevor Kennzahlen berechnet und verarbeitete Beobachtungen exportiert werden. **Weltweit (≈20 015 km)** umfasst jeden geografischen Standort; alle übrigen Filter und Anforderungen gelten weiterhin. Die Auswahl in den Segmentdetails begrenzt den dargestellten Bereich **innerhalb der bereits berücksichtigten Stationen**. Sie löscht weder Daten des abgeschlossenen Laufs noch nimmt sie ausgeschlossene Stationen wieder auf.

Die größte Entfernung entlang des kürzesten Weges beträgt in diesem Kugelmodell ungefähr **20 015,087 km**, am Punkt gegenüber dem Target. Dort endet die weltweite Karte mit der äußeren Beschriftung **≈20 015 km** und ohne leeren äußeren Ring. Die letzte Entfernungsklasse reicht von **15 000 km** bis zu diesem Maximum; jenseits von 20 000 km gibt es keine eigene Klasse. Die Beschriftung rundet die Obergrenze, die Zuordnung der Stationen verwendet die ungerundete Entfernung.

Vorhandene Konfigurationen und geteilte Links mit einer Grenze von **20 000 km** behalten diesen exakten Grenzwert. Eine gespeicherte Grenze von **22 000 km** öffnet **Weltweit** mit derselben globalen Abdeckung. Auch eine ausdrücklich gespeicherte ältere Entfernungsbereichsauswahl behält ihr ursprüngliches Intervall; sie wird nicht auf die neue letzte Klasse erweitert.

Bei Performance wird die Target-Aktivität aus weltweiten Berichten festgestellt, bevor geografisch gefiltert wird. Der Filter für bewegliche Stationen prüft ebenso zunächst Rufzeichen mit wechselndem Standort in den ansonsten zulässigen weltweiten Berichten und wendet danach die Entfernungsgrenze an.

Der Sonnenstandsfilter verwendet die Sonnenhöhe am **Target-QTH zum Zeitstempel des WSPR-Zyklus**. Dies beschreibt die Bedingungen am Target, nicht entlang der gesamten Funkstrecke oder an jeder Gegenstation. [Abschnitt 11.6](#sec-6-6) erklärt Abrufgrenzen der Datenbank und die Auswahl der berücksichtigten Quellberichte.


<a id="sec-7-view-geography"></a>
<a id="sec-7-8-1"></a>
##### 8.4.2 Geografische Zusammenfassungen

**Kartenfarben, Schraffur und ungefüllte Segmente.** Performance und Benchmark verwenden dieselbe graue diagonale Schraffur und die englischen Legendeneinträge **Not qualifying** und **No observations**. Schraffur bedeutet **Anforderungen nicht erfüllt**: Für die Karte liegen Beobachtungen im Segment vor, aber die Kennzahl erfüllt die Bedingungen zur Einfärbung nicht. Ein ungefülltes Segment bedeutet **Keine berücksichtigten Beobachtungen** für diese Karte; es belegt nicht, dass kein Empfang stattgefunden hat. Die Fußzeile **Map shading:** nennt die Anforderungen.

Performance verwendet für Stationsmarker und Flächendarstellung dieselben Stationen. Jede Station muss zunächst die Anforderungen je Station erfüllen. Für das Kartensegment gilt anschließend:

| Stationen im Segment, die die Anforderungen je Station erfüllen | Darstellung |
|---|---|
| Mindestens die eingestellte Segmentmindestzahl | Farbe nach dem Mittelwert der Stationsdekodierquoten, einschließlich **0%**. |
| Mindestens eine, aber weniger als die Segmentmindestzahl | Grau schraffiert: **Not qualifying**. |
| Keine | Ungefüllt: **No observations**. |

Enthält ein Segment nur Stationen, die die Anforderungen je Station nicht erfüllen, bleibt es ungefüllt, auch wenn ausgeschlossene Beobachtungen vorliegen. Eine gültige **Dekodierquote von 0%** bedeutet: Bestätigte Empfangsgelegenheiten lagen vor, aber keine Target-Dekodierung gelang. Schraffur ändert weder die in den Quoten berücksichtigten Stationen noch die Stationsauswahl der Segmentdetails und Statistiken.

Benchmark behält alle beobachteten Stationen innerhalb des gewählten Bereichs und der Filter bei. Für die Einfärbung gelten getrennte Anforderungen: Stationszahl und KI für ΔSNR; beobachtete Stationen und Ereignisanteil für ΔDecode.

Die **Benchmark**-Segmentanzahlen umfassen alle beobachteten Stationen im gewählten geografischen Bereich. ΔSNR verwendet nur Stationen, die die Anforderungen an gepaarte Beobachtungen erfüllen. Sortieren oder Filtern der Stationstabelle und die Auswahl einer Zeile ändern diese Segmentauswahl nicht. Die ΔSNR-Karte bildet den arithmetischen Mittelwert der berücksichtigten gepaarten Differenzen; jedes Paar zählt gleich viel. Dieser Mittelwert erhält eine Farbe, wenn sein KI über alle Paare und die Stationszahl die Anforderungen erfüllen. Die ΔDecode-Karte verwendet den Vorteil aus den zusammengefassten Dekodierzahlen. [Abschnitt 8.2.3](#sec-7-benchmark-aggregation) erklärt diese Kennzahlen und die separate Verteilung über Spot-Paare.

**Auf einen Blick** fasst bei Performance die gesamte abgeschlossene Analyse zusammen und berücksichtigt die eingestellte **Mindestzahl bestätigter Empfangsgelegenheiten je Station**.

| Karte | Was sie zusammenfasst |
|---|---|
| **Spot-Dekodierquote** | Erfolgreiche Dekodierungen als Anteil aller bestätigten Spot-Empfangsgelegenheiten, mit beiden Gesamtzahlen. |
| **Erfasste Gegenstationen** | Stationen mit mindestens einer erfolgreichen Dekodierung als Anteil aller berücksichtigten Stationen, mit beiden Stationszahlen. Eine Station ist eine Kombination aus Rufzeichen und vollständigem gemeldetem Locator. |
| **Stationsdekodierquote** | Mittelwert der einzelnen Stationsquoten über den gesamten Lauf. Jede Station zählt gleich viel, auch mit 0 %; die Karte nennt die Anzahl der beitragenden Stationen. |
| **Funkpfadentfernungen der Spots** | Maximum, Median und arithmetischer Mittelwert der Entfernung in Kilometern vom Target-QTH zum Gegenstationslocator. Jeder erfolgreiche Spot trägt seine Entfernung einmal bei. Stationen mit mehr Dekodierungen haben dadurch mehr Gewicht im Median und Mittelwert. Ohne erfolgreiche Dekodierungen erscheinen Striche. |

Die Quote einer Station ist die Anzahl ihrer erfolgreichen Dekodierungen geteilt durch ihre bestätigten Empfangsgelegenheiten. Die Auswahl in den Segmentdetails und die Mindestzahl qualifizierter Stationen je Kartensegment ändern diese Zusammenfassungen des gesamten Laufs nicht.

Bei Performance enthält <strong class="defined-term">Spot- und Stationsdekodierungen</strong> in den Segmentdetails die Karten für Spots und Stationen sowie die Abbildung nach SNR-Klassen. Unter den Tabellen leitet die blaue Überschrift **Spot- und Stationsdekodierungen: Vom Empfang schwacher bis zum Empfang starker Signale** die Abbildung ein. **So liest du die Ergebnisse** daneben öffnet die zugehörige Lesehilfe.

Die Karten verwenden dieselbe Anordnung wie Benchmark und fassen den gewählten geografischen Bereich zusammen:

| Karte | Anzahlen und Prozentwert | Bedeutung der Spalte **Gelegenheiten** |
|---|---|---|
| **Spots**, links | Erfolgreiche Dekodierungen / bestätigte Empfangsgelegenheiten und **Spot-Dekodierquote**. | Bestätigte Spot-Empfangsgelegenheiten. |
| **Stationen**, rechts | Stationen mit Erfolg / alle berücksichtigten Stationen und der Anteil **erfasster Gegenstationen**. | Berücksichtigte Stationen, gezählt nach exaktem Rufzeichen und vollständigem gemeldetem Locator. |

Für beide Karten und die Abbildung gelten die gewählten Entfernungen und Richtungen, die Mindestzahl bestätigter Empfangsgelegenheiten und die gegebenenfalls erforderliche zusätzliche Bestätigung. Eine Filterung der Stationstabelle ändert die hier berücksichtigten Stationen nicht.

Die Karte **Stationen** zeigt links die Anzahlen, in der Mitte den **Anteil erfasster Gegenstationen** und rechts in Grün den **Mittelwert der Stationsdekodierquoten** oder den **Median der Stationsdekodierquoten**. Dieselbe ausgewählte Quote steht in der grünen letzten Tabellenspalte, mit dezenter Hintergrundfarbe für jeden Entfernungsbereich und **Alle Entfernungen**. Das Sternchen verweist auf die Erklärung von Mittelwert oder Median am Kartenende. Die Anzeige verwendet eine Nachkommastelle; berechnet wird mit ungerundeten Werten.

**Zusammenfassende Statistik** wählt **Mittelwert** (Standard) oder **Median** der einzelnen Stationsquoten über die vollständige Auswahl. Jede Station zählt gleich viel, auch ohne erfolgreiche Dekodierung. Dies unterscheidet die Kennzahl von der gemeinsamen Spot-Dekodierquote. **Alle Entfernungen** fasst die einzelnen Stationsquoten direkt zusammen, statt die Kennwerte der Entfernungsbereiche zu mitteln. Der Anteil erfasster Gegenstationen und die Ergebnisbalken behalten ihre Bedeutung.

Der Ergebnisbalken für die vollständige aktuelle Auswahl (100,0 %) teilt alle Empfangsgelegenheiten in Erfolge und bestätigte Nichtdekodierungen oder alle berücksichtigten Stationen in solche mit und ohne Erfolg. Die Karten behalten vier Entfernungsbereiche: **0–2 500**, **2 500–5 000**, **5 000–10 000** und **10 000–≈20 015 km**. Eine gemeinsame Grenze gehört zum dort beginnenden Bereich; die exakte weltweite Obergrenze gehört zum letzten Bereich.

Jede Tabelle zeigt diese Bereiche und die Gesamtzeile **Alle Entfernungen**. Bei Spots sind dies Erfolge, Nichtdekodierungen, Gelegenheiten und **Dekodierquote**; bei Stationen die erfassten, nie erfassten und qualifizierten Anzahlen sowie der **Anteil**. Jeder Entfernungsbereich verwendet seinen eigenen Nenner: bestätigte Empfangsgelegenheiten für die Dekodierquote und qualifizierte Stationen für den Anteil. Die Gesamtquoten verwenden die zusammengefassten Anzahlen der vollständigen Auswahl. In der Quote über alle Empfangsgelegenheiten haben häufig beobachtete Stationen mehr Gewicht. Bei leerem Nenner ist kein Prozentsatz definiert. Die SNR-Abbildung darunter fasst alle gewählten Entfernungen zusammen.

Bei RX ist ein nur anderswo gehörter Spot eine bestätigte Empfangsgelegenheit, die andere Empfänger dekodiert haben, ohne Target-Dekodierung oder gemessenes Target-SNR. Bei TX hat der betrachtete Empfänger das Target während einer bestätigten Empfangsgelegenheit nicht dekodiert; er muss dabei selbst einen anderen Sender gemeldet haben. Die Target-Aktivität muss weiterhin durch einen geeigneten Bericht auf demselben Band im selben Zyklus belegt sein, wie in [Abschnitt 8.3.1](#sec-7-performance-opportunities) beschrieben.

Eine Station mit Erfolg ist bei RX ein vom Target gehörter Sender, bei TX ein Empfänger, der das Target gehört hat. Die Karten und die separaten Zusammenfassungen **„All SNR“** enthalten alle erfolgreichen Dekodierungen und diese Stationen, auch Erfolge ohne nutzbares SNR. Aus den SNR-Klassenbalken bleiben Erfolge ohne nutzbares SNR ausgeschlossen. Mindestens einmaliger Empfang hängt vom Beobachtungszeitraum und der verfügbaren Aktivität ab; ein einzelner Erfolg belegt keine hohe Dekodierquote.

Die Abbildung **„Spot & Station Decodes by SNR Band for CALLSIGN (RX/TX)“** nennt Target und Analyserichtung. Sie folgt der Auswahl von Entfernungen und Richtungen sowie der **Mindestzahl bestätigter Empfangsgelegenheiten je Station**. RX verwendet erfolgreiches Target-SNR, normiert auf **30 dBm Sendeleistung**, mit der Achsenbeschriftung **„Successful Target SNR (dB, normalized to 30 dBm TX)“**. TX verwendet das gemeldete oder normierte Empfangs-SNR des abgeschlossenen Laufs, wie auf den Achsen angegeben. Die Abbildung besteht aus drei Zeilen und zwei Spalten.

Fünf Diagramme gruppieren erfolgreiche Dekodierungen in **5 dB breite SNR-Klassen**, von schwachen Signalen links zu starken Signalen rechts. Jede Klasse schließt ihre untere Grenze ein und ihre obere aus: **[−20, −15) dB** enthält −20 dB, aber nicht −15 dB. Ein exaktes Vielfaches von 5 dB gehört zur dort beginnenden Klasse. Die Klassen fassen alle gewählten Entfernungen und Richtungen der Segmentdetails zusammen; getrennte Entfernungsreihen werden nicht gezeigt.

Welche Stationen eingehen, bestimmen die Mindestzahl bestätigter Empfangsgelegenheiten und die gegebenenfalls erforderliche zusätzliche Bestätigung. Jede Kombination aus Rufzeichen und vollständigem gemeldetem Locator zählt als eine Station. Das untere linke Diagramm gruppiert die Stationsdekodierquoten statt des SNR. Die blauen Balken **„All SNR“** in den fünf SNR-Diagrammen fassen die vollständige Auswahl zusammen; sie sind keine zusätzlichen SNR-Klassen. Die Zusammenfassung unten links heißt **„All“** und teilt alle berücksichtigten Stationen in dekodiert und nicht dekodiert auf.

**Oben links — „Successful Spot Decodes“.** Jeder erfolgreiche Spot mit nutzbarem SNR zählt einmal in seiner SNR-Klasse. Die Y-Achse verwendet eine **log₁₀**-Skala; null Anzahlen hinterlassen Lücken. Der Balken **„All SNR“** zählt sämtliche erfolgreichen Dekodierungen, auch ohne nutzbares SNR.

**Oben rechts — „Stations with Successful Decodes“.** Die Anzahlenskala ist linear. Jede Station zählt einmal in jeder Klasse, in der sie eine erfolgreiche Dekodierung hat. Der einfarbige Teil zeigt ihre schwächste erfolgreiche SNR-Klasse (**„Weakest successful SNR band“**). Der schraffierte Teil kennzeichnet Stationen, die bereits in einer schwächeren Klasse vorkommen (**„Also heard at weaker SNR“**). Eine Station kann deshalb zu mehreren Klassengesamtzahlen beitragen. Addiere nur die einfarbigen Teile, um unterschiedliche Stationen mit nutzbarem SNR zu zählen. Der separate Balken **„All SNR“** zählt alle unterschiedlichen Stationen mit Erfolg, auch ohne nutzbares SNR.

**Mitte links — „Spot Decode Rate“.** Die erfolgreichen Dekodierungen jeder SNR-Klasse werden durch **alle bestätigten Spot-Empfangsgelegenheiten** der Auswahl geteilt, einschließlich bestätigter Nichtdekodierungen. Der Nenner bleibt für alle Klassen gleich. Jeder Balken trägt daher zur Dekodierquote der vollständigen Auswahl bei. Er beschreibt nicht die Dekodierwahrscheinlichkeit bei diesem SNR, denn für Nichtdekodierungen gibt es keinen gemessenen SNR-Wert einer erfolgreichen Dekodierung.

**Mitte rechts — „Station Reach“.** Die Stationen mit Erfolg in jeder Klasse werden durch **alle berücksichtigten Stationen** geteilt, auch solche ohne Erfolg. Einfarbiger und schraffierter Teil entsprechen der Unterscheidung oben rechts. Auch dieser Nenner bleibt gleich; Stationen können aber in mehreren Klassen vorkommen, weshalb sich die Prozentwerte nicht addieren lassen. Die blauen Balken **„All SNR“** zeigen die Spot-Dekodierquote und den Anteil unterschiedlicher Stationen mit Erfolg über die vollständige Auswahl.

**Unten links — „Station Decode Frequency“.** Jede Station gehört mit ihrer **Dekodierquote** über die vollständige Auswahl — erfolgreiche Dekodierungen / bestätigte Empfangsgelegenheiten — zu genau einer Kategorie: **0%**, **>0–10%**, **>10–25%**, **>25–50%**, **>50–75%** oder **>75–100%**. Maßgeblich sind ungerundete Quoten. Positive Kategorien schließen die untere Grenze aus und die obere ein; genau 10%, 25%, 50% und 75% gehören zur dort endenden Kategorie.

Die Y-Achse zeigt den Anteil aller berücksichtigten Stationen, auch der Stationen ohne Erfolg. Die X-Achse heißt **„Station Decode Rate (%)“** und zeigt kein SNR. Bei mindestens einer Station ergeben die sechs Kategorien zusammen 100%. Die fünf positiven Kategorien entsprechen zusammen dem Anteil erfasster Gegenstationen. Über dem Prozentsatz der Kategorie **0%** steht **„Not Decoded“**.

Der separate Balken **„All“** ergibt ebenfalls 100%: Grau **„Not Decoded“** steht für Stationen ohne Erfolg, Blau **„Decoded“** für Stationen mit mindestens einem Erfolg. Dieser schmale Balken hat dieselbe sichtbare Breite und horizontale Mitte wie die Zusammenfassungsbalken darüber. Die Verteilung enthält auch Erfolge ohne nutzbares SNR und bleibt bei einem Wechsel zwischen Mittelwert und Median unverändert.

**Unten rechts — „Station-averaged Decode Rate“ oder „Median Station Decode Rate“.** Für jede Station werden ihre Erfolge in einer SNR-Klasse durch **alle ihre bestätigten Empfangsgelegenheiten** der Auswahl geteilt. Anschließend wird der gewählte **Mittelwert** oder **Median** dieser Prozentwerte gebildet. Jede Station zählt gleich viel, auch ohne Erfolg in dieser Klasse. Die berücksichtigten Stationen und der Nenner jeder Station bleiben fest.

Der blaue Balken **„All SNR“** wird separat aus der Quote jeder Station über die vollständige Auswahl berechnet, einschließlich Erfolgen ohne nutzbares SNR. Er ist kein Mittelwert der Klassenkennwerte. Sein **Mittelwert** entspricht dem Kartenwert für dieselben Stationen. Um Mittelwerte mehrerer Kartensektoren zusammenzufassen, müssen sie nach der jeweiligen Zahl berücksichtigter Stationen gewichtet werden.

Die Mittelwertbeiträge der SNR-Klassen ergeben zusammen den Mittelwert der vollständigen Auswahl, wenn alle Erfolge ein nutzbares SNR haben. **Mediane sind nicht additiv**: Alle Klassenmediane können 0% sein, obwohl der separat berechnete Gesamtmedian positiv ist. Ein Median von null ist ein gültiges Ergebnis und kein fehlender Wert.

**Zusammenfassende Statistik** wählt **Mittelwert** (Standard) oder **Median**, unabhängig von den zeitlichen Einstellungen. Die Auswahl steuert auch die roten gestrichelten vertikalen SNR-Markierungen in den fünf SNR-Diagrammen. Die Legenden zeigen den gewählten SNR-Wert in dB mit einer Nachkommastelle.

| Markierung | Zusammengefasste Werte | Beschriftung in der Abbildung |
|---|---|---|
| Beide SNR-Diagramme links | Einzelne SNR-Werte erfolgreicher Spots. | **„Mean spot SNR“** / **„Median spot SNR“** |
| Oben rechts und Mitte rechts | Schwächstes erfolgreiches SNR je Station mit mindestens einem nutzbaren SNR-Wert. | **„Mean weakest station SNR“** / **„Median weakest station SNR“** |
| Unten rechts | Zunächst das erfolgreiche SNR je Station zusammenfassen, dann diese Stationswerte mit gleichem Gewicht kombinieren. | **„Mean of station mean SNR“** / **„Median of station median SNR“** |

Nur Stationen mit nutzbarem SNR erfolgreicher Dekodierungen tragen zu diesen Markierungen bei. Stationen ohne Erfolg bleiben mit null in den Quoten enthalten, haben aber keinen SNR-Wert. Die Markierungen bezeichnen zusammengefasste SNR-Werte; sie sind weder Unsicherheitsintervalle noch Mittelwerte oder Mediane der Balkenhöhen. Die Auswahl ändert diese Markierungen und die mittleren oder medianen Stationsquoten in der Abbildung und der Karte Stationen. Anzahlen, Überschneidungen zwischen Stationen, Spot-Dekodierquote, Anteil erfasster Gegenstationen und Häufigkeitskategorien bleiben gleich.

**Erfolge ohne nutzbares SNR** bleiben in den Karten, den Zusammenfassungen **„All SNR“** und den Kategorien von „Station Decode Frequency“ enthalten. Zu den fünf SNR-Klassenverteilungen und ihren Markierungen tragen sie nicht bei. Daher können die Klassenanzahlen und addierbaren Mittelwertbeiträge unter den Gesamtzusammenfassungen liegen. Bei leerem Nenner ist kein Prozentsatz definiert.

Die Prozentwerte von **„Station Reach“** beschreiben Erfolge innerhalb der jeweiligen SNR-Klasse. Der Balken **„All SNR“** und die Karte **Stationen** zählen jede Station mit Erfolg über die vollständige Auswahl nur einmal.

**Beibehaltene entfernungsabhängige Zusammenfassungen.** Historische Entfernungsprofile der Dekodierquote gruppierten Stationen nach ihrer berechneten Entfernung vom Target-QTH. Ihre feineren Entfernungsklassen waren unabhängig von den vier breiten Bereichen der Kartentabellen. Die Klassenbreite folgte der maximalen Gegenstationsentfernung:

| Maximale Gegenstationsentfernung | Breite der Entfernungsklasse |
|---|---|
| 2 500 km | 250 km |
| 5 000 km | 500 km |
| 10 000 km | 1 000 km |
| 15 000 km | 1 500 km |
| Weltweit oder 20 000 km aus einer vorhandenen Konfiguration oder einem geteilten Link | 2 500 km |

Eine Änderung des ausgewählten Entfernungsbereichs behielt diese Breite bei. Die Klassengrenzen lagen bei ganzzahligen Vielfachen ab **0 km**; die letzte Klasse wurde an das konfigurierte Maximum oder die physikalische globale Obergrenze angepasst. In der weltweiten Ansicht reicht die letzte Klasse von **17 500 km** bis ungefähr **20 015 km**. Sie verbindet die frühere Klasse von 17 500–20 000 km mit dem kleinen möglichen Bereich jenseits von 20 000 km. Die letzte ausgewählte Obergrenze ist **unter den bereits berücksichtigten Gegenstationen** eingeschlossen; der Ausschluss an der maximalen Analyseentfernung gilt weiterhin. Lücken zwischen getrennten ausgewählten Bereichen bleiben Lücken und werden nicht zu Klassen ohne Beobachtungen.

Für jede Entfernungsklasse unterscheiden diese Zusammenfassungen den Mittelwert der einzelnen Stationsquoten von der Quote aus allen erfolgreichen Dekodierungen und bestätigten Empfangsgelegenheiten zusammen.


<a id="sec-7-view-time"></a>
<a id="sec-7-8-3"></a>
##### 8.4.3 Chronologische Beobachtungsdaten

**Chronologische Ansichten erhalten die Reihenfolge des Laufs.** Die Zeitintervalle beginnen am gewählten UTC-Start und verwenden die eingestellte Breite; das letzte Intervall kann kürzer sein. Die **Zeitbasis** ändert die angezeigten Uhrzeiten und Datumsangaben, nicht die Intervallgrenzen, enthaltenen Beobachtungen oder Kennzahlen. Leere Intervalle bleiben leer; **0-dB**- oder **0-%**-Beobachtungen werden nicht ergänzt. Angebotene Breiten und Standardwerte hängen von der vollständigen Laufdauer ab, nicht von der Zeitspanne vorhandener Berichte. Eine gültige gespeicherte Breite kann außerhalb der üblichen Auswahl erhalten bleiben; siehe [Abschnitt 10.5](#sec-5-5).

**Benchmark-ΔSNR** fasst innerhalb jedes Zeitintervalls die beibehaltenen Spot-Paare qualifizierter Stationen zusammen. **ΔSNR-Statistik: Median / Mittelwert** wählt Median mit IQR oder arithmetischen Mittelwert mit punktweisem KI zum eingestellten Konfidenzniveau. Dichteverteilung, zugelassene Paare, Intervallzuordnung und gleiches Gewicht je Paar bleiben unverändert. Stationen mit mehr Paaren tragen mehr Werte bei.

Neue Analysen verwenden unabhängig für Segment- und Einzelstationsdiagramme den Mittelwert. Fehlt in einer aktuellen Konfiguration die gespeicherte Statistik, gilt auf dieser Ebene ebenfalls Mittelwert; ausdrücklich gespeicherte Werte werden beachtet. Die Milazzo-Demo startet auf beiden Ebenen mit Median. Die Abdeckungsansicht behält separat alle zulässigen gepaarten und einseitigen Ergebnisse sowie die Beteiligung unterschiedlicher Stationen bei. Sie verwendet die beiden Vorteilskennzahlen aus [Abschnitt 8.2.4](#sec-7-benchmark-coverage). Gepaarte Beobachtungen unterhalb der ΔSNR-Anforderungen und einseitige Beobachtungen können dort erscheinen, auch wenn die ΔSNR-Ansicht leer ist.

**1. SNR erfolgreicher Dekodierungen im Zeitverlauf und nach Uhrzeit**

**SNR-Bezugsgröße bei TX Performance:** **TX-SNR-Normierung auf 30 dBm**, rechts neben **Band**, ist bei neuen Analysen ausgeschaltet. Erfolgreiche Dekodierungen verwenden dann das vom entfernten Empfänger gemeldete Empfangs-SNR. Eingeschaltet gilt `gemeldetes SNR + 30 − gemeldete TX-Leistung (dBm)`; das Ergebnis wird als auf 30 dBm (1 W) normiert gekennzeichnet. RX Performance und Benchmark-ΔSNR bleiben normiert. Auch die Benchmark-Ansichten für Dekodierungen und erfasste Stationen über dem ursprünglichen SNR bleiben unverändert.

Die gewählte SNR-Bezugsgröße gilt für Stationsmediane, die SNR-Klassen-Abbildung, zeitliche Mittelwerte oder Mediane und ihre Intervalle, Vergleichsniveaus und Abweichungen in der Segmentansicht, die ausgewählte Station und ihre fokussierten Daten sowie Exporte. Erfolgs- und Nichtdekodierungsanzahlen und Dekodierquoten bleiben gleich. Ein Wechsel erfordert einen neuen Analyselauf; zuvor normierte Daten lassen sich nicht durch einen reinen Darstellungswechsel ersetzen.

Die beiden Dichtediagramme zeigen erfolgreiches Target-SNR auf der gewählten Bezugsgröße des abgeschlossenen Laufs: das ursprünglich gemeldete Empfangs-SNR bei TX Performance mit ausgeschalteter Normierung, sonst die **gemeldete Leistungsbasis von 1 W (30 dBm)**. Die Achse nennt die Bezugsgröße; **„Normalized Target SNR (dB @ 30 dBm)“** gilt nur für die normierte Ansicht. Absolutes SNR bedeutet, dass kein Stationsvergleichsniveau abgezogen wurde.

**Mittelwert** ergänzt den arithmetischen Mittelwert und sein punktweises KI zum eingestellten Konfidenzniveau. **Median** ergänzt Median und IQR, der die mittlere Hälfte derselben Beobachtungen beschreibt. Der Wechsel lässt die absolute SNR-Dichte unverändert. Diese Abbildung erfordert nicht die drei Erfolge, die zur Berechnung eines Stationsvergleichsniveaus nötig sind. Sie kann deshalb Stationen enthalten, die in der Abweichungsabbildung fehlen. Eine andere Mischung dekodierter Stationen kann das absolute SNR ändern, auch wenn sich keine einzelne Funkstrecke verändert hat.

**2. Dekodierquote und zugehörige Anzahlen im Zeitverlauf**

Die Zeile **„TX Stations“** bei RX beziehungsweise **„RX Stations“** bei TX zeigt die Stationsbeteiligung. In jedem chronologischen Intervall trägt jede Station eine Einheit zum Stationsbalken bei, aufgeteilt nach ihrer eigenen Dekodierquote. Eine Quote von 40% ergibt **0,4** Erfolgsanteil und **0,6** Nichtdekodierungsanteil. Bei RX heißen diese Teile **„Heard by Target“** und **„Heard by others only“**, bei TX **„Target heard“** und **„Other signals heard only“**.

Diese Bruchteile zählen nicht die mindestens einmal gehörten Stationen. Ihr Erfolgsanteil beschreibt die bestehende Kennzahl mit gleichem Stationsgewicht. **Beide eingezeichneten Quotenlinien verwenden dagegen alle bestätigten Empfangsgelegenheiten zusammen**, H geteilt durch H + M. Die Gelegenheitszeile zählt jeden bestätigten Erfolg und jede Nichtdekodierung direkt. Bei nur einer ausgewählten Station stimmen Stationsanteil und gemeinsame Quote in einem belegten Intervall überein; Stationsbalken und Gelegenheitsbalken beschreiben weiterhin unterschiedliche Anzahlen.

Beide Zeilen enthalten Stationen, die die Anforderungen an Empfangsgelegenheiten erfüllen, auch mit zu wenigen Erfolgen für ein SNR-Vergleichsniveau. In der Tageszeitansicht zeigen die Balken mittlere Stationsbeteiligung oder Empfangsgelegenheiten je vertretenem Tag. Die Quotenlinien verwenden dagegen die über Tage zusammengefassten Erfolge und Gelegenheiten. [Abschnitt 8.4.4](#sec-7-view-folding) erklärt den Nenner aus Tagen und Stunden, die Aufteilung des Stationsbalkens und ein Zahlenbeispiel.


**3. Dekodierquote nach Entfernung im Zeitverlauf und nach Uhrzeit**

Jede Zelle zeigt **„Decode rate (%)“** als `100 × H / (H + M)`. H zählt die berücksichtigten Target-Erfolge, M bestätigte Gelegenheiten ohne Target-Dekodierung. Tageszeitzellen summieren diese Anzahlen für dieselbe Uhrzeitstunde über die Tage und berechnen daraus die Quote. Sie mitteln weder Stationsprozentsätze noch Tagesprozentsätze oder Prozentsätze chronologischer Zellen.

Beide Diagramme verwenden denselben Farbbereich: **0% bis zur höchsten beobachteten Dekodierquote mit gültigem Zahlenwert** in den chronologischen und sichtbaren Tageszeitzellen der aktuellen Auswahl, Zeitintervallbreite und Zeitbasis. Ein nicht verfügbares Tageszeitdiagramm trägt kein verborgenes Maximum bei. Die Werte bleiben tatsächliche Prozentsätze: Liegt das Maximum bei 20%, bedeutet auch die stärkste Farbe 20% und keinen relativen Wert von 100%. Weil sich die Farbgrenzen mit Auswahl, Zeitintervallen oder Zeitbasis ändern können, lies vor dem Vergleich verschiedener Abbildungen die numerische Legende.

Sind alle verfügbaren Quoten null oder liegt kein gültiger Zahlenwert vor, wird ein **Ersatzbereich von 0–1%** ausdrücklich gekennzeichnet, damit die Legende sichtbar bleibt. Dadurch entsteht kein beobachteter Wert von 1%. Eine Zelle mit 20 Erfolgen bei 100 Gelegenheiten bleibt bei 20%, auch als höchster Wert im Diagramm. Ohne Empfangsgelegenheiten fehlt die Datengrundlage; null Erfolge bei positivem Nenner sind dagegen eine gültige 0%-Zelle.

Die vertikale Achse zeigt die berechnete Entfernung, von null unten ansteigend. Beide Diagramme verwenden die Performance-Entfernungsklassen und den gewählten geografischen Bereich. Die bisherige Regel für Punkte zur Kennzeichnung der Datengrundlage bleibt erhalten. **Zeitliche Zusammenfassung** bestimmt die chronologische Intervallbreite; Tageszeitintervalle bleiben eine Stunde in der gewählten **Zeitbasis**.

Bei einer einzelnen ausgewählten Station, bestimmt durch exaktes Rufzeichen und vollständigen Locator, entfällt die Entfernungs-Heatmap. Ihre einzige Entfernungsklasse würde die zeitliche Dekodierquote wiederholen. Die berechnete Entfernung vom Target steht nach dem Locator im Untertitel jeder Einzelstationsabbildung. Ansichten mehrerer Stationen behalten die Entfernungs-Heatmap.

In den SNR-Dichtediagrammen bedeutet **„Relative spot density (% of panel maximum)“**: `100 × Beobachtungsanzahl der Zelle / größte Beobachtungsanzahl einer Zelle in diesem Panel`. Jedes chronologische und jedes Tageszeitdiagramm verwendet sein eigenes Maximum über alle Zeit-/Stunden- und SNR-Zellen; die Spalten werden nicht einzeln normiert. 100 bezeichnet somit die am stärksten belegte Zelle und nicht 100% aller Beobachtungen. Eine gemeinsame Farbskala macht die absoluten Anzahlen verschiedener Diagramme nicht vergleichbar; verwende dafür die zugehörigen Anzahlen. Geringe Dichte ist blau, hohe Dichte orange/rot. Die vertikale Lage zeigt absolutes SNR beziehungsweise in der vierten Segmentabbildung die SNR-Abweichung.

Die zeitlichen Segmentansichten zeigen erfolgreiches SNR als Abbildung 1, Dekodierquote und zugehörige Anzahlen als Abbildung 2, Dekodierquote nach Entfernung/Zeit als Abbildung 3 sowie Stationsabweichungen als Abbildung 4. Für eine ausgewählte Station gibt es nur Abbildungen 1–2. Diese zeitlichen Gewichtungen ändern die bestehenden Definitionen der eigenständigen Karten- und Entfernungsstatistiken mit gleichem Stationsgewicht beziehungsweise über alle Empfangsgelegenheiten nicht.

Die **Expertenansicht** enthält Abbildung 4 und ist zunächst eingeklappt; die ersten drei Segmentabbildungen sind direkt sichtbar. Ihre Beschriftung lautet im Mittelwertmodus **Expertenansicht — SNR-Abweichung vom Mittelwert der jeweiligen Station über den Analyselauf**, im Medianmodus **Expertenansicht — SNR-Abweichung vom Median der jeweiligen Station über den Analyselauf**. Das Öffnen ändert weder Daten noch Berechnungen. Alle vier Segmentabbildungen bleiben im Ergebnispaket enthalten, auch bei eingeklapptem Bereich. Einzelstationsergebnisse enthalten zwei Abbildungen, ohne Entfernungs-Heatmap oder Abweichungsansicht.

**SNR-Abweichungen in Performance** vergleichen jede Station mit ihrem eigenen Vergleichsniveau über den Lauf. Bei RX sind die Gegenstationen Sender, bei TX Empfänger. Eine Station benötigt mindestens **drei erfolgreiche Beobachtungen mit gültigem numerischem SNR auf der gewählten SNR-Bezugsgröße** im vollständigen berücksichtigten Zeitfenster. **Mittelwert** zieht deren arithmetischen Mittelwert ab, **Median** deren Median. Jedes exakte Rufzeichen mit vollständigem gemeldetem Locator erhält sein eigenes Vergleichsniveau.

**−7 dB** gegenüber einem Vergleichsniveau von **−10 dB** ergibt beispielsweise eine **Abweichung von +3 dB**. Null entspricht diesem Vergleichsniveau, nicht der Gleichheit von Target und Referenz. Änderungen der Zeitintervalle, der dargestellten Zeitbasis oder der Segmentauswahl berechnen das Vergleichsniveau des Laufs nicht neu.

Jede erfolgreiche Target-Beobachtung mit gültigem numerischem SNR trägt einen Wert auf der gewählten Bezugsgröße des abgeschlossenen Laufs bei. Eine Beobachtung ist eine berücksichtigte Empfangsgelegenheit nach Zusammenfassung doppelter Berichte; doppelte Datenbankberichte erzeugen also keine zusätzlichen Werte. Chronologische Intervalle fassen diese Einzelbeobachtungen zusammen, Tageszeitintervalle die Beobachtungen gleicher Stunden über die vertretenen Tage. Vorher werden weder Stationen noch Kombinationen aus Station, Tag und Stunde oder Tagesergebnisse gemittelt. Stationen und Tage mit mehr Beobachtungen erhalten daher mehr Gewicht.

Eine bestätigte Gelegenheit ohne Target-Dekodierung zählt im Nenner der Dekodierquote, liefert aber keinen Target-SNR-Wert. Weder null noch ein erfundenes schwaches SNR wird eingesetzt.

Auch die Abweichungsansicht fasst einzelne SNR-Abweichungen direkt innerhalb der Zeitintervalle oder gleicher Uhrzeitstunden zusammen. Dichte, Mittelwert/KI und Median/IQR werden aus diesen Abweichungen berechnet, nicht aus vorherigen Zusammenfassungen je Station und Intervall oder je Tag. Die Stationsidentität bestimmt das Vergleichsniveau, gibt den Stationen aber kein gleiches Gewicht. Ein Wechsel zwischen Mittelwert und Median kann sowohl die Abweichungen als auch ihre Zusammenfassungen verändern. Die KI-Berechnung behandelt die beobachteten Vergleichsniveaus als fest und berücksichtigt ihre Schätzunsicherheit nicht zusätzlich. Einzelstationsansichten lassen diese vierte Abbildung weg und zeigen weiterhin absolutes SNR auf der gewählten Bezugsgröße.

<a id="sec-7-view-folding"></a>
##### 8.4.4 Tage nach UTC oder wahrer Ortszeit zusammenfassen

Bei **Zeitbasis: UTC** kombiniert die <strong class="defined-term">Zusammenfassung nach UTC-Stunde</strong> Beobachtungen derselben Uhrzeitstunde über mehrere Tage. Sie zeigt Tageszeitmuster, entfernt aber die Reihenfolge der einzelnen Tage. Das unterscheidet sie von chronologischen Intervallen: Bei einem Start um **12:17 UTC** reicht ein chronologisches **1h**-Intervall von **12:17 bis 13:17**. Die Tageszeitansicht gruppiert dagegen nach Uhrzeitstunden wie **12:00 bis 13:00** und berücksichtigt nur den Teil innerhalb des gewählten Zeitfensters.

**Zeitliche Zusammenfassung** steuert nur die chronologischen Diagramme; die bisherigen Intervallgrößen bleiben erhalten. Die danebenliegende **Zeitbasis** wählt **UTC** oder **Wahre Ortszeit** für die chronologischen und nach Tageszeit zusammengefassten SNR-, Dekodier- und Abdeckungsansichten dieser Ebene. Segment- und Einzelstationsdiagramme speichern die Zeitbasis unabhängig; fokussierte Diagramme folgen der ausgewählten Station. Tageszeitdiagramme verwenden immer einstündige Intervalle. Neue Analysen starten auf beiden Ebenen mit UTC; ausdrücklich gespeicherte Werte werden beachtet. Die Milazzo-Demo verwendet auf beiden Ebenen wahre Ortszeit und Median, die anderen Benchmark-Demos UTC und Mittelwert.

Bei Benchmark steht **ΔSNR-Statistik: Median / Mittelwert** neben **Zeitbasis**. Die Auswahl gilt für beide ΔSNR-Zeitansichten dieser Ebene. Segment- und Einzelstationsstatistik sind unabhängig wählbar; neue Analysen starten jeweils mit Mittelwert. Geändert werden die statistische Größe und ihr Intervall innerhalb der bestehenden Zeitintervalle, nicht Paarbildung, Kalibrierung, Qualifikation oder Gewichtung. **Median** zeigt IQR, **Mittelwert** das KI für den Mittelwert derselben zusammengefassten Paare. Die Benchmark-Statistik bleibt auf die gewählte Analyse und den gewählten Bereich bezogen.

In Performance sind **Zeitliche Zusammenfassung**, **Zeitbasis** und **SNR-Statistik: Median / Mittelwert** wie bei Benchmark angeordnet. Segment- und Einzelstationsansicht können diese drei Einstellungen unabhängig wählen; das Konfidenzniveau ist gemeinsam. Neue Analysen starten mit **Mittelwert**, **UTC** und **95%** Konfidenzniveau. Ausdrücklich gespeicherte Werte werden beachtet.

Die Statistik gilt für beide SNR-Zeitansichten ihrer Ebene und verwendet die Daten des abgeschlossenen Laufs ohne neue Datenbankabfrage. Sie ändert die Zusammenfassungslinie und das Intervall; bei Segmentabweichungen auch das Vergleichsniveau und die Dichte der Abweichungen.

Unverändert bleiben die Beobachtungen der absoluten SNR-Dichte, Gelegenheitsanzahlen, Dekodierquoten, Kartenqualifikation, die SNR-Klassen-Zusammenfassung und der feste Median in der Stationstabelle. Ein anderes Konfidenzniveau aktualisiert die punktweisen Mittelwertintervalle, ohne den abgeschlossenen Lauf ungültig zu machen.

Ein Wechsel der **Zeitbasis** ändert Uhrzeiten und Datumsangaben der chronologischen Ansicht, nicht deren Intervalle oder Kennzahlen. In der Tageszeitansicht werden Beobachtungen dagegen neu gruppiert; dadurch können sich ihre Stundenwerte ändern. **Wahre Ortszeit** richtet sich nach der Sonne am Target-QTH, mit Sonnenhöchststand um 12:00. Sie ist weder gesetzliche Uhrzeit noch Sommerzeit. Die Zeitstempel der Quelldaten bleiben UTC.

Der Sonnenbezug gilt für das Target, nicht für jede Gegenstation oder die gesamte Funkstrecke.

**Wahre Ortszeit** ist die örtliche scheinbare Sonnenzeit. Der Target-Locator liefert die Korrektur für den Längengrad. Die datumsabhängige Zeitgleichung wird täglich über den Lauf einschließlich seiner Grenzen berechnet und auf die einzelnen WSPR-Zykluszeiten interpoliert. Der Zeitversatz ist daher nicht über den gesamten Lauf konstant.

Die Beobachtungen werden vor der stündlichen Zusammenfassung neu gruppiert. Bereits berechnete Mediane werden nicht verschoben; Paarbildung, Filter, Qualifikation, Rohdaten und Gesamtstatistik bleiben gleich. Der Wechsel nutzt vorhandene Daten ohne neue Datenbankabfrage. Tageszuordnung, vertretene Tage und Nenner der stündlichen Abdeckung folgen der gewählten Zeitbasis, einschließlich des Datumswechsels nach Sonnenzeit. [US Naval Observatory: The Equation of Time](https://aa.usno.navy.mil/faq/eqtime).

Die einzelnen Ansichten kombinieren ihre Daten auf unterschiedliche Weise:

| Ansicht | Was zu einer Stunde der gewählten Zeitbasis beiträgt | Wie daraus die Zusammenfassung entsteht |
|---|---|---|
| **Benchmark-ΔSNR** | Beibehaltene Spot-Paare qualifizierter Stationen über die vertretenen Tage. | Median mit IQR oder Mittelwert mit punktweisem KI derselben Paare. Häufig beobachtete Funkstrecken tragen mehr Werte bei. |
| **Absolutes Performance-SNR** | Jede erfolgreiche Target-Beobachtung mit gültigem numerischem SNR auf der gewählten Bezugsgröße, aus derselben Uhrzeitstunde über die Tage. | Mittelwert mit punktweisem KI oder Median mit IQR der Einzelbeobachtungen. Keine vorherige Zusammenfassung je Station oder Tag und kein Abzug eines Vergleichsniveaus. |
| **Performance-SNR-Abweichung** | Jede erfolgreiche Beobachtung abzüglich des Mittelwerts oder Medians ihrer Rufzeichen-Locator-Kombination über den Lauf. Das Vergleichsniveau erfordert mindestens drei erfolgreiche Dekodierungen mit gültigem numerischem SNR. | Einzelne Abweichungen der Uhrzeitstunde zusammenfassen und daraus Mittelwert/KI oder Median/IQR berechnen. Die Anzahl der Beobachtungen bestimmt das Gewicht; Stationen und Tage erhalten kein erzwungenes gleiches Gesamtgewicht. |
| **Beteiligte Performance-Stationen nach Tageszeit** | Vorkommen je Station, Tag und Stunde sowie die je Station über Tage zusammengefassten Erfolge und Gelegenheiten dieser Stunde. | Mittlere Stationsbeteiligung je Tag, anteilig in dekodiert/nicht dekodiert aufgeteilt anhand gleich gewichteter Stationsquoten. Diese Aufteilung liefert Kontext und entspricht nicht der gemeinsamen Quotenlinie. |
| **Zeitliche Performance-Dekodierquote** | Alle beibehaltenen Erfolge und bestätigten Empfangsgelegenheiten der gewählten Stunde über die Tage. | Gesamte Erfolge durch gesamte bestätigte Gelegenheiten teilen. Beide zeitlichen Quotenlinien und die Entfernungs-/Zeitzellen verwenden diese Quote. Der Stationsbalken liefert Kontext, nicht ihren Nenner. |

Erfolgreiches SNR verwendet die Einzelbeobachtungen aus [Abschnitt 8.4.3](#sec-7-view-time): Doppelte Berichte liefern keine zusätzlichen Werte. Stationen und Tage mit mehr erfolgreichen Dekodierungen erhalten beim Zusammenfassen entsprechend mehr Gewicht.

Bestätigte Nichtdekodierungen gehen in die Dekodierquote ein, liefern aber keinen SNR-Wert. Weder null noch ein erfundenes schwaches SNR wird ergänzt.

**Tageszeitansichten benötigen mindestens zwei vertretene Kalendertage.** Bei Performance hat ein vertretener Tag mindestens eine qualifizierende bestätigte Empfangsgelegenheit irgendwo im gewählten Bereich und Zeitfenster. Diese Tage ermöglichen sowohl die Diagramme mit Anzahlen als auch die SNR-Diagramme, selbst wenn nutzbares SNR an weniger Tagen vorliegt.

Benchmark-Abdeckung verwendet Tage mit beliebigen beibehaltenen Ergebnissen. Ihre ΔSNR-Ansicht benötigt separat Tage mit endlichem gepaartem ΔSNR qualifizierter Stationen. Ein Tag mit Spot-Paaren und ein zweiter nur mit einseitigen Ergebnissen können deshalb die Tageszeit-Abdeckung ermöglichen, ohne Tageszeit-ΔSNR zu ermöglichen.

**Tageszeitbalken mitteln über berücksichtigte Kombinationen aus Tag und Stunde.** Eine Uhrzeitstunde eines vertretenen Tages zählt im Nenner mit, sobald sie das gewählte Zeitfenster überlappt, auch wenn in dieser Stunde keine Beobachtungen vorliegen. Stunden außerhalb des Fensters zählen nicht. Eine nur teilweise überlappende Randstunde zählt als **eine vollständige Einheit**, ohne Gewichtung nach Minuten; das kann den Mittelwert senken.

Die Balken enthalten Stationen, die die Anforderungen an Empfangsgelegenheiten erfüllen, auch ohne die drei Erfolge für ein SNR-Vergleichsniveau. Sie zeigen die mittlere Stationsbeteiligung oder Gelegenheitsanzahl dieser Uhrzeitstunde über die vertretenen Tage. Beispielsweise ergeben sechs und null Empfangsgelegenheiten in derselben berücksichtigten Stunde an zwei vertretenen Tagen einen Mittelwert von drei. Zusätzliche Nichtdekodierungen werden dadurch nicht erfunden.

Für die Aufteilung des Stationsbalkens werden zunächst je Station die Erfolge und Gelegenheiten dieser Uhrzeitstunde über die Tage zusammengezählt und daraus die Quote berechnet. Der Mittelwert dieser gleich gewichteten Stationsquoten bestimmt den Erfolgs- und Nichtdekodierungsanteil. Die Quotenlinien fassen dagegen H und M über alle Stationen und Tage zusammen. Ihre Prozentsätze entstehen unabhängig von der Stationsbalkenaufteilung und vom Tagesmittel der Balkenhöhen.

**Benchmark-Abdeckung ordnet Stationen für jeden Tag getrennt ein.** Zähle je Tag und Uhrzeitstunde der gewählten Zeitbasis **Both observed**, **Only Target** und **Only Reference**. Summiere die täglichen Anzahlen und teile sie für die oberen Balken durch die Zahl vertretener Kombinationen aus Tag und Stunde. Eine Station, die am Montag nur auf der Target-Seite und am Dienstag nur auf der Referenzseite beobachtet wurde, ist an keinem der Tage „Both observed“. Die Linie „Station Reach Advantage“ verwendet die Summen der täglichen Target- und Referenzstationszahlen, keinen Mittelwert täglicher Verhältnisse.

Die unteren Balken teilen ebenso die zusammengefassten ursprünglichen Ergebnisanzahlen durch die Zahl vertretener Kombinationen aus Tag und Stunde. Ihre ΔDecode-Linie verwendet die über Tage zusammengefassten Dekodierzahlen. Keine der Linien vereinigt Stationszugehörigkeiten über den gesamten Zeitraum oder mittelt tägliche Vorteilswerte.

Prüfe die chronologische Ansicht, bevor du ein Tageszeitmuster als wiederkehrend beschreibst. Die Tageszeitansicht zeigt nicht, dass es an jedem Tag auftrat.

Die Tageszeitansicht ändert die Gruppierung für die Darstellung. Datierte UTC-Zeitstempel und Stationsidentitäten bleiben in den Daten erhalten. Die IID-Berechnung setzt voraus, dass die in einem Intervall zusammengefassten Paare unabhängig sind, auch wenn sie von verschiedenen Stationen oder Tagen stammen. Weder die Tageszeit-Zusammenfassung noch ein verfügbares KI je Station belegt diese Annahme.


<a id="sec-7-view-station"></a>
<a id="sec-7-8-4"></a>
##### 8.4.5 Beobachtungsdaten einer ausgewählten Station

Die Einzelstationsansicht folgt normalerweise **einer Station, bestimmt durch exaktes Rufzeichen und vollständigen gemeldeten Locator**. Bei **Benchmark und Performance** verwendet sie die vollständigen Daten dieser Station aus dem abgeschlossenen Lauf, unabhängig von der geografischen Auswahl der Segmentdetails und dem optionalen Stationslistenfilter. Eine in der Liste ausgeblendete Station bleibt ausgewählt und behält ihre Kennzahlen über den gesamten Lauf. Die Auswahl ändert weder die vorherige Zuordnung noch die Aufnahmebedingungen. Ein ausdrücklicher Detaildaten-Fokus kann das dargestellte Zeitintervall eingrenzen.

In der Benchmark-**Stationsauswertung** verwenden **Median ΔSNR** und **Mittelwert ΔSNR** dieselben beibehaltenen gepaarten Differenzen des ausgewählten Rufzeichens mit vollständigem Locator. Die benachbarte KI-Spalte, bei englischer Beschriftung und Standardniveau **„ΔSNR 95% CI (dB)“**, zeigt die symmetrische **± Halbbreite** für den Stationsmittelwert zum eingestellten Konfidenzniveau.

Nach den Stationskennungen folgen standardmäßig Median ΔSNR, Mittelwert ΔSNR, ΔSNR-KI, ΔDecode, gepaarte Spots und einseitige Anzahlen. Die KI-Überschrift nennt den Prozentsatz. Paaranzahl sowie getrennte Anzahlen nur für Target und nur für Referenz bleiben sichtbar. Die **Stichprobenstandardabweichung des gepaarten ΔSNR** ist als optionale Spalte oder im Export verfügbar und standardmäßig ausgeblendet. Vollständige KI-Grenzen und numerische Angaben bleiben im Export enthalten. Aufnahmebedingungen, Stationslistenfilter und der Bezug der Kennzahlen auf die vollständige Analyse bleiben unverändert.

| Analyse | Zusammenfassungen der ausgewählten Station |
|---|---|
| **Benchmark** | Chronologische und Tageszeit-ΔSNR-Ansichten verwenden die beibehaltenen Paare über den gesamten gefilterten Zeitraum. Die Abdeckung behält separat „Only Target“, alle gepaarten Beobachtungen in einer grünen Kategorie und „Only Reference“ bei. Die Kurve zeigt das gemeinsame ΔDecode dieser Station mit derselben vorzeichenbehafteten Verhältnisachse wie die Zeile „Spot-level“ des Segments. |
| **Performance** | Zwei Abbildungen: absolutes SNR erfolgreicher Target-Dekodierungen auf der gewählten Bezugsgröße und Dekodierquote mit zugehörigen Anzahlen im Zeitverlauf. Die Entfernung vom Target steht jeweils nach dem Locator im Untertitel; die sich wiederholende Einzelstations-Entfernungs-Heatmap entfällt. Chronologische und Tageszeitansichten berechnen Mittelwert/KI oder Median/IQR unmittelbar aus einzelnen erfolgreichen Beobachtungen. Kein Vergleichsniveau wird abgezogen, keine Abweichungsabbildung erscheint. Erfolgs-/Nichtdekodierungsanzahlen und gemeinsame Quote beschreiben dieselbe Station über den gesamten Lauf. Bei einer Station stimmen Stationsanteil und gemeinsame Quote in belegten Intervallen überein; Stationsbeteiligung und Gelegenheitsanzahl bleiben verschiedene Maße. |

Bei aktivierter Ausreißerberichterstattung kann Benchmark auch **mehrere Stationen** auswählen und ihre qualifizierenden Spot-Paare für ΔSNR zusammenfassen. Jedes Paar zählt gleich viel; Stationen erhalten kein gleiches Gewicht. **„ΔDecode over Time“** ist nur bei **einer ausgewählten Station** verfügbar. Stationsauswahl, Listenfilter und Zoom berechnen die Qualifikation nicht neu und starten die Erkennung nicht erneut.

**Fokussierte Detaildaten zeigen einzelne beibehaltene Beobachtungen zur tatsächlichen WSPR-Zykluszeit:** einen zusammengefassten gepaarten ΔSNR-Wert bei Benchmark oder ein erfolgreiches Target-SNR auf der gewählten Bezugsgröße des abgeschlossenen Laufs bei Performance. Dies sind verarbeitete Beobachtungen, weder unveränderte Datenbankzeilen noch Mittelwerte, Mediane oder Dichten über Zeitintervalle. Für das fokussierte Benchmark-ΔSNR-Diagramm werden die beibehaltenen Paare verwendet; einseitige Beobachtungen liefern kein gepaartes ΔSNR.

Fokussierte Diagramme verwenden die gewählte **Zeitbasis**, auch für Ereignismarkierungen und Vergleichszeiträume. Die Detaildatentabelle und die Zeiteingaben zur Fokussierung behalten UTC bei, damit jede Beobachtung ihrem ursprünglichen Zyklus zugeordnet werden kann.

**Möglicher Ausreißer im Detail** kann einen Kandidaten mit seinen vollständigen, durch Beobachtungen gestützten Vergleichszeiträumen davor und danach zeigen, auch außerhalb eines gewöhnlichen Fokusintervalls. Verwendet wird das abgeschlossene Erkennungsergebnis; der Detektor wird nicht erneut an die ausgewählten Daten angepasst. Die lokalen Vergleichsniveaus und Abweichungslinien beschreiben diesen Kandidaten. Sie sind weder Konfidenzintervalle noch unabhängige Qualifikationsprüfungen. Fokus und Darstellungsintervalle ändern die Ansicht, nicht das abgeschlossene Ergebnis.


<a id="sec-7-view-spread"></a>
<a id="sec-7-8-5"></a>
##### 8.4.6 Streuung und Darstellungsskalen

**Streuung ist keine Konfidenz.** Ein Q1–Q3-Band umfasst die mittlere Hälfte der beitragenden Werte; ein Min–Max-Intervall umfasst ihren gesamten Wertebereich. Keines ist ein Konfidenzintervall.

In zeitlichen Medianansichten, einschließlich Benchmark mit **ΔSNR-Statistik: Median**, genügt **ein** Wert für eine Medianmarkierung. Benachbarte Mediane werden nur verbunden, wenn **jedes Intervall mindestens drei** Werte enthält. Ein IQR-Band verbindet benachbarte Intervalle erst ab **mindestens fünf Werten je Intervall**. Einzelne ausreichend gestützte Intervalle erhalten kein Band; unzureichend gestützte Intervalle unterbrechen die Verbindungen. Je nach Ansicht sind die Werte Spot-Paare, einzelne erfolgreiche Target-Beobachtungen oder einzelne SNR-Abweichungen vom Stationsvergleichsniveau.

Die roten gestrichelten Mittelwert-/Medianmarkierungen in **Spot- und Stationsdekodierungen** fassen dagegen erfolgreiches SNR wie in [Abschnitt 8.4.2](#sec-7-view-geography) beschrieben zusammen. Sie zeigen weder IQR noch Konfidenzintervalle.

**Mittelwertintervalle beschreiben die Unsicherheit eines Mittelwerts.** Benchmark verwendet im Modus Mittelwert das eingestellte KI je Zeitintervall mit seinen ungerundeten unteren und oberen Grenzen. Die Legende lautet standardmäßig **„Bin 95% CI“** und folgt dem gewählten Konfidenzniveau. Es sind punktweise Intervalle für einzelne Zeitintervalle, kein gleichzeitiges Konfidenzband der gesamten Kurve. Ist der Mittelwert definiert, sein KI aber nicht verfügbar, bleibt er ohne Band sichtbar. Ein IQR wird nicht ersatzweise eingezeichnet.

Eine Mittelwertmarkierung kann ab **einem Paar** erscheinen. Benachbarte Markierungen werden nur bei **mindestens drei Paaren je Intervall** verbunden. Ein verfügbares KI benötigt mindestens **zwei Paare** und reicht über die tatsächlichen Intervallgrenzen, auch bei einem isolierten Intervall. Diese Regeln bestimmen die mathematische Verfügbarkeit, nicht die statistische Abdeckung.

Im Modus Median verwenden die rote globale Referenzlinie und das Zentrum der nichtlinearen ΔSNR-Achse den Median aller beibehaltenen qualifizierten Paare des dargestellten Bereichs. Im Modus Mittelwert verwenden die goldene Referenzlinie und das Achsenzentrum den Mittelwert derselben Paare. Chronologische und Tageszeitansicht teilen diese Referenz. Weder andere Zeitintervalle noch die Tageszeit-Zusammenfassung bilden dafür Mittelwerte aus Stations- oder Intervallmittelwerten. Die Achse zeigt weiterhin die einzelnen gepaarten ΔSNR-Werte; die gewählte Statistik beschreibt die darübergelegte Zusammenfassung je Intervall.

**Performance verwendet dasselbe Student-t-Verfahren für Einzelbeobachtungen.** Absolute Segment- und Einzelstations-KIs verwenden die erfolgreichen SNR-Werte auf der gewählten Bezugsgröße; KIs der Segmentabweichungen die entsprechenden Einzelabweichungen. Chronologische und Tageszeitintervalle ersetzen diese nicht durch Stations- oder Tagesmittelwerte. Das Konfidenzniveau ändert die Intervallgrenzen, nicht den Mittelwert oder die enthaltenen Beobachtungen. Die dB-Achsen von Performance bleiben linear.

**KI-Fortsetzung außerhalb des dargestellten Bereichs.** Jede zeitliche SNR- oder ΔSNR-Abbildung verwendet denselben vertikalen Bereich für ihre chronologische und ihre Tageszeitansicht. Er wird aus allen beitragenden Beobachtungen und den Klassengrenzen der Dichteverteilung bestimmt, mit zusätzlichem Darstellungsrand. Benchmark behält den absoluten Wert 0 dB und seine um die gewählte Statistik zentrierte Skala bei. KIs vergrößern diesen Bereich nicht. Eine alleinige Änderung der zeitlichen Zusammenfassung lässt ihn gleich, solange die beitragenden Werte unverändert sind.

Ein ungefülltes △ am oberen Rand eines Zeitintervalls bedeutet, dass dessen obere KI-Grenze darüber hinausreicht. Ein ungefülltes ▽ am unteren Rand bedeutet, dass die untere KI-Grenze darunterliegt. Reichen beide Grenzen hinaus, erscheinen beide Zeichen. Sobald ein Intervall außerhalb der Skala fortgesetzt wird, steht in der Fußzeile **△ ▽ CI extends beyond displayed range**. Nur das gezeichnete Band wird abgeschnitten; die numerischen Grenzen bleiben gleich. Der Diagrammrand ist kein Intervallendpunkt.

Ein KI kann insbesondere bei wenigen Beobachtungen über den beobachteten Wertebereich hinausreichen. Nicht verfügbare KIs erhalten keine Fortsetzungsmarkierung. Diese Zeichen gelten für KIs im Mittelwertmodus, nicht für IQR-Bänder im Medianmodus. Vorschau, vergrößerte Abbildungen und Exporte verwenden dieselbe Darstellung.

Mittelwertintervalle setzen unabhängige beitragende Beobachtungen voraus. Das Zusammenfassen über Stationen oder Tage belegt diese Unabhängigkeit nicht. Für Segmentabbildung 4 werden die beobachteten Vergleichsniveaus als fest behandelt; ihre Schätzunsicherheit wird nicht zusätzlich berücksichtigt. Ein berechenbares, enges oder nullbreites KI belegt daher weder Unabhängigkeit noch das Fehlen jeglicher Unsicherheit, eine Hardwarewirkung als Ursache oder eine gleichzeitige Abdeckung aller Intervalle. Das KI beschreibt die Unsicherheit des Mittelwerts unter diesem Modell; IQR beschreibt die beobachtete Streuung.

**±h bedeutet Halbbreite.** Die Tabelle **Spots** und die **Stationsauswertung** zeigen das KI neben dem Mittelwert als **± Halbbreite**. **+3,20 dB** und **±0,49 dB** entsprechen beispielsweise **[+2,71; +3,69] dB**. Die Halbbreite ist weder die volle Intervallbreite noch Standardabweichung oder Standardfehler. Ohne danebenstehenden Mittelwert werden beide Angaben gezeigt, zum Beispiel **Mean ΔSNR +3.20 dB; 95% CI ±0.49 dB** in der englischen Darstellung beim Standardniveau. Überschriften und Erläuterungen folgen `ci_alpha`.

Ein fehlendes KI ist nicht verfügbar, niemals **±0,00**. Sehr kleine positive Halbbreiten erhalten zusätzliche Stellen, damit sie nicht als null erscheinen. Numerische Exporte behalten Grenzen und Halbbreite in voller Genauigkeit.

Die symmetrische ±-Angabe gilt nur für symmetrische Grenzen um den Schätzwert. Eine künftige asymmetrische Methode muss das vollständige Intervall oder getrennte untere und obere Abstände zeigen. Sie darf die Grenzen weder umzentrieren noch durch einen mittleren Abstand ersetzen.

**<strong class="defined-term">Dichtefarben</strong> sind innerhalb jedes Diagramms relativ.** Die am stärksten belegte Zelle erhält **100**, die übrigen werden nach ihrer Anzahl proportional skaliert. Diese Zelle enthält damit nicht 100 % aller Beobachtungen. Vergleiche die zugehörigen Anzahlen, wenn du den Datenumfang verschiedener Diagramme beurteilst.

**Farben der ΔSNR-Karte** zeigen den <strong class="defined-term">Mittelwert des gepaarten ΔSNR über alle Paare</strong>. Die symmetrischen Farbgrenzen passen sich den Segmentmittelwerten an, die die Anforderungen erfüllen. Vergleiche deshalb zwischen Läufen die numerischen Legenden. Eine Farbe erfordert die Mindeststationszahl und ein verfügbares, nicht entartetes KI über alle Paare innerhalb der gewählten Halbbreitengrenze. Das Konfidenzniveau verändert das KI, nicht den Mittelwert, und kann so beeinflussen, welche Segmente eine Farbe erhalten. Die Abdeckung gilt <strong class="defined-term">nominell für jedes Segment einzeln</strong>, nicht gleichzeitig für die ganze Karte. Die Präzisionsgrenze ist kein Signifikanztest. Ein Intervall kann die Anforderungen erfüllen und trotzdem null einschließen.

**ΔSNR-Klasseneinteilung und Achsen.** Das Spot-Paar-Histogramm verwendet normalerweise **1-dB**-Klassen, bei einem klaren HalbdB-Raster **0,5 dB**, und bei breiten Wertebereichen größere Klassen. Die beiden Stationshistogramme verwenden die gemeinsame adaptive Einteilung aus [Abschnitt 8.2.3](#sec-7-benchmark-aggregation). Zeitliche Dichtezellen bleiben **1 dB** hoch und verschieben sich mit der Referenzkorrektur. Bei denselben beibehaltenen Beobachtungen bewegen sich Zellen und Werte gemeinsam, ohne Zellanzahlen oder relative Farben zu ändern. Die Darstellung rundet weder Beobachtungen noch ändert sie deren Kennzahlen; Werte mit Bruchteilen von dB müssen nicht in Zellmitten liegen.

Zeitliche Benchmark-ΔSNR-Achsen stauchen die Randbereiche um die gewählte Statistik des dargestellten Bereichs: den Median aller Paare im Medianmodus oder den Mittelwert aller Paare im Mittelwertmodus. Histogrammachsen behalten ihre jeweiligen Zentren. Absolut **0 dB** bleibt sichtbar. Lies die beschrifteten dB-Koordinaten, statt Unterschiede aus den Abständen abzuschätzen. Im Histogramm gibt die **Balkenlänge entlang der Prozentachse**, nicht die gezeichnete Fläche, den Anteil an. Diese Darstellung verändert weder Werte noch Anzahlen, Mittelwerte, Mediane, Quartile oder KI-Grenzen. Die Achsen des erfolgreichen Performance-SNR bleiben in dB linear.

**ΔDecode-Verhältnislegende.** **2×** auf der Target-Seite bedeutet doppelt so viele Target- wie Referenzdekodierungen; **2×** auf der Referenzseite kehrt diesen Vergleich um. Blau begünstigt die Referenz, warme Farben das Target. Die Mitte **1×** markiert exakte Gleichheit; ihr mittleres Farbband enthält jedoch auch nahezu gleiche Verhältnisse unterhalb der ersten Grenze auf beiden Seiten. Dieses Band belegt keine statistische Äquivalenz.

Die Legende wählt die feinste Voreinstellung, die den größten endlichen Vorteil unter den **sichtbaren, ausreichend gestützten Segmenten** abdeckt, berechnet als größere durch kleinere Dekodierzahl der Aufbauten. Exklusiver Empfang verwendet Voreinstellung C. Die Wahl der Voreinstellung ändert nur die Darstellung, nicht die Dekodierzahlen, ihr Verhältnis oder die Qualifikation.

| Voreinstellung | Verhältnisgrenzen auf jeder Seite von 1× | Deckt größtes endliches Verhältnis ab bis |
|---|---|---:|
| AA | 1,05×, 1,10×, 1,15×, 1,20×, 1,25× | 1,25× |
| A | 1,25×, 1,5×, 1,75×, 2×, 2,5×, 3× | 3× |
| B | 1,25×, 1,5×, 2×, 3×, 5×, 10× | 10× |
| C | 1,25×, 2×, 3×, 5×, 10×, ≥20× | Größere Verhältnisse und exklusiver Empfang |

Bei Voreinstellung C umfasst **≥20×** große endliche Verhältnisse. **Exclusive** bedeutet, dass der andere Aufbau null Dekodierungen hat; es ist kein endliches Verhältnis von 20. Grenzen beschreiben Farbintervalle — beispielsweise ist **1,5×–1,75×** ein Band. Gleich breite Farbfelder sind Kategorien, keine lineare Verhältnisskala. Lies beim Vergleich von Läufen die numerischen Grenzen: Gleiche Farbintensitäten unter verschiedenen Voreinstellungen müssen keine gleichen Vorteile darstellen.


<a id="sec-7-claims"></a>
<a id="sec-7-10"></a>
#### 8.5 Wie weit trägt die Schlussfolgerung?

<strong class="defined-term">Deskriptive Statistik</strong> beschreibt die in einem Analyselauf berücksichtigten Beobachtungen. <strong class="defined-term">Statistische Inferenz</strong> nutzt diese Beobachtungen und begründete Annahmen, um über die aufgezeichneten Daten hinausgehende Aussagen abzuleiten, häufig mit einem Unsicherheitsmaß. Eine korrekte Zusammenfassung belegt allein nicht, wie eine Station in einem anderen Zeitraum abschneiden wird oder was einen Unterschied verursacht hat. Prüfe Datengrundlage und Versuchsaufbau, bevor du die Aussage erweiterst; [Kapitel 9](#sec-8) liefert Formulierungsbeispiele.


<a id="sec-7-dependence-bias"></a>
##### 8.5.1 Abhängigkeit und Verzerrung

**Warum WSPRadar Konfidenzintervalle für den Mittelwert von ΔSNR angibt**

Jedes berücksichtigte Spot-Paar liefert eine SNR-Differenz zwischen Target und Referenz für dieselbe Gegenstation, dasselbe Band und denselben WSPR-Zyklus. Damit wird der Zeitpunkt des Vergleichs kontrolliert, und Ausbreitungsschwankungen, die beide Aufbauten gemeinsam betreffen, können sich in ihrer SNR-Differenz aufheben. Die resultierenden gepaarten Differenzen bieten eine praktische Grundlage zur Schätzung eines mittleren relativen Vorteils — ein Messansatz, der durch etablierte Methoden für gepaarte Beobachtungen und Modelle für Antennenvergleiche mit WSPR gestützt wird. <a href="#ref-31">[Ref-31]</a>, <a href="#ref-1">[Ref-1]</a>

Die Mittelwertbildung kann den Einfluss zufälliger Schwankungen verringern, sodass sich der Mittelwert präziser schätzen lässt als eine einzelne Beobachtung. Bei ausreichend vielen unabhängigen, identisch verteilten Beobachtungen mit endlicher Varianz nähert sich die Stichprobenverteilung des Mittelwerts einer Normalverteilung an, selbst wenn die einzelnen ΔSNR-Werte nicht normalverteilt sind. Ein Konfidenzintervall beschreibt die Präzision dieses geschätzten Mittelwerts unter dem statistischen Modell, nicht die Streuung einzelner Spot-Paare. <a href="#ref-31">[Ref-31]</a>, <a href="#ref-32">[Ref-32]</a>

WSPRadar verwendet ein **nominelles Student-t-Konfidenzintervall**, das aus der beobachteten Streuung in der Stichprobe und der Anzahl beitragender Beobachtungen berechnet wird. Die Berechnung berücksichtigt, dass die Varianz aus den Daten geschätzt wird, und ist für unabhängige Beobachtungen aus derselben Normalverteilung exakt. Bei Ergebnissen einzelner Stationen und Ergebnissen über alle zusammengefassten Paare sind die beitragenden Beobachtungen gepaarte ΔSNR-Werte. Beim Mittelwert der Stationsmittelwerte sind es die einzelnen Stationsmittelwerte. <a href="#ref-31">[Ref-31]</a>, <a href="#ref-32">[Ref-32]</a>

**Unabhängigkeit bleibt eine Annahme.** Die Paarbildung garantiert nicht, dass wiederholte Beobachtungen auf einem Funkpfad oder Stationsmittelwerte bei gemeinsamen Ausbreitungs- und Betriebsbedingungen unabhängig sind. Die Berechnung verwendet die beobachtete Anzahl beitragender Beobachtungen ohne Korrektur für Abhängigkeiten; ihr angegebenes Konfidenzniveau gilt daher nur unter diesem Arbeitsmodell. Das KI bezieht sich auf die Population der ausgewählten gepaarten Beobachtungen, berücksichtigt keine systematische Kalibrierungsunsicherheit und liefert keinen Nachweis eines kalibrierten Antennengewinns. <a href="#ref-1">[Ref-1]</a>, <a href="#ref-32">[Ref-32]</a>, <a href="#ref-33">[Ref-33]</a>

**1 000 Spots sind keine 1 000 unabhängigen Experimente.** Wiederholte Zyklen teilen Ausrüstung und Ausbreitung; nahe Stationen teilen Bedingungen; benachbarte Zeitintervalle hängen zusammen; ein Störereignis oder ionosphärisches Ereignis kann viele Beobachtungen beeinflussen. Die beiden Phasen einer Sequenz mit erweitertem WSPR ergänzen Beobachtungen innerhalb eines Laufs, keine unabhängigen Versuchswiederholungen.

Gleiche Stationsgewichtung verringert den Einfluss häufig meldender Stationen. Mediane verringern den Einfluss einzelner Extremwerte. Beides beseitigt weder systematische Kalibrierfehler noch Unterschiede der Berichtsübermittlung oder Verzerrungen durch Ausbreitung; es macht die Beobachtungen auch nicht unabhängig.

**Ein deskriptiver arithmetischer Mittelwert oder eine Standardabweichung erfordert keine gaußverteilten Daten.** Ein arithmetischer Mittelwert beschreibt das rechnerische Mittel; die Standardabweichung beschreibt die Streuung um diesen Mittelwert. Beide können einen endlichen beobachteten Datensatz zusammenfassen, ohne eine glockenförmige Normalverteilung vorauszusetzen. Ihr Nutzen hängt von der zusammengefassten Größe und den Verteilungsrändern beziehungsweise Extremwerten ab. Ein Median beschreibt den mittleren Wert, und der IQR misst die Breite der mittleren Hälfte; diese beantworten andere Fragen und sind gegenüber der Größe von Extremwerten weniger empfindlich. Wähle die statistische Größe nach der beabsichtigten Messgröße, statt eine nicht normale Verteilung als Grund anzusehen, warum ein arithmetischer Mittelwert ungültig sei <a href="#ref-30">[Ref-30]</a>.

Aussagen über die Unsicherheit jenseits der berücksichtigten Beobachtungen erfordern ein begründetes Modell für Stichprobe und Abhängigkeiten. Fehlende Normalverteilung allein macht solche Aussagen nicht unmöglich. WSPRadar bietet ein <strong class="defined-term">IID-Student-t-Basismodell</strong>; IID bedeutet unabhängig und identisch verteilte Beobachtungen. Es gilt für einzelne Stationsmittelwerte, Mittelwerte über berücksichtigte Spot-Paare, Mittelwerte zeitlicher und nach Tageszeit zusammengefasster Intervalle, Kartenmittelwerte über Spot-Paare sowie gleich gewichtete Mittelwerte der berücksichtigten Stationsmittelwerte. Paarbildung allein belegt die Unabhängigkeitsannahme nicht. WSPRadar liefert keine p-Werte, statistische Teststärke, automatischen Signifikanzkennzeichen oder Schätzungen kausaler Effekte. Wer positiv abhängige Berichte als unabhängig behandelt, kann die Unsicherheit über zukünftige Ergebnisse oder eine größere Population unterschätzen.

**Berechnung des Basismodells.** Für beibehaltene endliche gepaarte Differenzen $d_1,\ldots,d_n$ im exakt dargestellten Bereich sei $\bar d$ ihr arithmetischer Mittelwert und $s$ die Stichprobenstandardabweichung mit dem Nenner $n-1$. Der Standardfehler ist $s/\sqrt n$. Das zweiseitige Intervall lautet:

$$\bar d \pm t_{1-\alpha/2,\,n-1}\frac{s}{\sqrt n}$$

Intern ist `ci_alpha` die gesamte zweiseitige Randwahrscheinlichkeit, kein p-Wert, und muss strikt zwischen 0 und 1 liegen. Das Konfidenzniveau ist `100 × (1 − ci_alpha)%`: `0.05` ergibt **95%**, `0.10` ergibt **90%**. Gespeicherte Konfigurationen benennen die Methode als `evidence_confidence_interval_method = iid_student_t`; der aktuelle Standard für Version 1, `evidence_confidence_level_percent = 95`, entspricht intern `ci_alpha = 0.05`. `n` ist die beobachtete Paaranzahl, keine geschätzte effektive Anzahl unabhängiger Beobachtungen. Siehe [NIST: Konfidenzgrenzen für den Mittelwert](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm) und [NIST: Streuungsmaße und Stichprobenstandardabweichung](https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm).

Ohne Beobachtungen sind Mittelwert und Intervall nicht verfügbar. Bei genau einem Paar ist der Mittelwert definiert; Stichprobenstandardabweichung, Standardfehler und Konfidenzintervall sind jedoch nicht verfügbar. Die bestehenden Anforderungen entscheiden weiterhin, ob dieser Mittelwert angezeigt wird. Eine Varianz von null ergibt ein entartetes Intervall der Breite null und keinen Nachweis eines exakt bekannten physikalischen Versatzes. Die Mindestanforderungen beschreiben die Datengrundlage, garantieren aber keine statistische Abdeckung.

Für den aggregierten <strong class="defined-term">Mittelwert der Stationsmittelwerte</strong> in der Zusammenfassung **Stationen** ist das Konfidenzintervall bei weniger als zwei beitragenden Stationen nicht verfügbar; ein definierter Mittelwert bleibt erhalten. Bei mindestens zwei Stationsmittelwerten ergibt eine ungerundete Standardabweichung von null zwischen den Stationen ein entartetes Intervall der Breite null mit ausdrücklichem Status. Die Karte verwendet ein anderes Intervall: Sie zählt die berücksichtigten Paare und berechnet die Standardabweichung über deren Differenzen. Ein entartetes Intervall der Stationsmittelwerte bestimmt daher nicht für sich allein den Status des Kartenintervalls über alle Paare.

**Annahmen und Grenzen des Intervalls.** Bei unabhängigen Beobachtungen aus derselben Normalverteilung erreicht das Student-t-Intervall die exakte Abdeckung seines Konfidenzniveaus; andernfalls ist es unter geeigneten Bedingungen eine Näherung. Ein annähernd normal aussehendes Histogramm oder ein nicht signifikanter diagnostischer Test, etwa ein Normalitätstest, belegt keine Unabhängigkeit. Das Intervall bezieht sich auf den Mittelwert des Prozesses, den die berücksichtigten Paare im ausgewählten Bereich abbilden. Es ist kein Vorhersageintervall für einen einzelnen Spot, enthält keine systematischen Kalibrierungsfehler und beseitigt nicht die Auswahl durch die Voraussetzung beidseitiger Dekodierung. Ein schmales Intervall belegt keinen stabilen Vorteil in jedem Zyklus.

Dieses Basismodell ist **nicht allgemein für WSPR validiert**. Bevor eine solche Aussage getroffen wird, müssen repräsentative beibehaltene gepaarte Datensätze auf chronologisches Verhalten, Lücken, Abhängigkeit, Verteilungsform, kleine Stichproben, wechselnde Stationszusammensetzung und die Auswahl bei schwachen Signalen untersucht werden. Dazu gehören Vergleiche der Intervallbreiten und der simulierten Abdeckung bei bekannten Effekten mit mindestens einem für die Zeitstruktur geeigneten Verfahren. Es gibt keine allgemeingültige „n ≥ 30“-Garantie; Bootstrap-Berechnungen gehören nicht zum automatischen Standardpfad.

<strong class="defined-term">Konfidenzintervall für den gleich gewichteten Mittelwert der Stationsmittelwerte.</strong> Sei `m_i` der mittlere gepaarte ΔSNR-Wert jeder qualifizierten Station im gewählten Bereich. `M` zählt die Stationen, die dort mindestens ein geeignetes Paar beitragen. Für M ≥ 2 gilt:

$$\bar m=\frac{1}{M}\sum_{i=1}^{M}m_i,\qquad s_m^2=\frac{\sum_{i=1}^{M}(m_i-\bar m)^2}{M-1}$$

$$h=t_{1-\alpha/2,\,M-1}\frac{s_m}{\sqrt M},\qquad KI=[\bar m-h,\bar m+h]$$

`M` zählt Stationsmittelwerte, nicht Spot-Paare. Das Konfidenzniveau ist `1 − α`; bei 95% gilt `α = 0.05`. Die Standardabweichung beschreibt die beobachtete Streuung zwischen den Stationsmittelwerten, und `s_m / √M` ist ihr <strong class="defined-term">Standardfehler</strong> unter dem angegebenen Modell. Bei einer beitragenden Station bleibt deren Mittelwert definiert, das aggregierte Konfidenzintervall ist jedoch nicht verfügbar.

Dieses modellbasierte Intervall beruht auf Annahmen über die Unabhängigkeit der Stationen und die Stichprobe. Die Student-t-Berechnung ist exakt, wenn die Stationsmittelwerte unabhängige Beobachtungen aus derselben Normalverteilung sind; andernfalls ist sie eine Näherung. Gleiche Gewichtung allein belegt diese Annahmen nicht, insbesondere bei wenigen Stationen oder ungleichen Paaranzahlen je Station. Unterschiedliche Rufzeichen und Locator belegen keine Unabhängigkeit, und zwei Stationen belegen keine Robustheit.

Die Streuung zwischen den Stationsmittelwerten enthält sowohl Unterschiede zwischen Funkstrecken als auch Unsicherheit in den geschätzten Stationsmittelwerten. Die Berechnung berücksichtigt weder Standardfehler einzelner Stationen noch Korrelationen durch eine separate Fehlerfortpflanzung. Sie verwendet keine Präzisionsgewichte und mittelt keine Stationskonfidenzintervalle. Korrelierte Funkstrecken, gemeinsame Ausbreitung, unterschiedliche Anzahlen oder Zeitpunkte der Beobachtungen je Funkstrecke und die Auswahl beidseitig dekodierter Signale können die Interpretation begrenzen. Das Intervall bei gleicher Stationsgewichtung verwendet die Stationsmittelwerte aus dem gewählten Bereich der Segmentdetails. Die Karte verwendet ihr eigenes Intervall über alle Paare mit Paaranzahl N und Standardabweichung der Paardifferenzen; sie übernimmt nicht das Intervall der Stationsmittelwerte.

Das Ergebnis **Stationen** für den gewählten Bereich wird unmittelbar aus den geeigneten Stationsmittelwerten neu berechnet. Die Anzahlen- und Präzisionsanforderungen der Karte steuern die Färbung und entfernen keine beitragenden Stationen aus schraffierten Segmenten aus diesem Schätzwert. Das gemeinsame Konfidenzniveau verändert dieses Intervall und das Kartenintervall über die Paare; die Halbbreitengrenze der Karte filtert jedoch weder die Zusammenfassung **Stationen** noch **Spots**.

<strong class="defined-term">Kartenmittelwert und Konfidenzintervall über alle Paare.</strong> Beispielsweise beschreibt **+3,20 ± 0,49 dB** die Grenzen **[+2,71; +3,69] dB** beim angegebenen Konfidenzniveau. Die Halbbreite erfüllt eine Präzisionsgrenze von **0,5 dB**; eine Färbung erfordert weiterhin die Stationsmindestzahl und ein verfügbares, nicht entartetes Konfidenzintervall. Seien `d_1,...,d_N` innerhalb eines Kartensegments die geeigneten <strong class="defined-term">gepaarten ΔSNR-Werte</strong> der für ΔSNR berücksichtigten Stationen nach der bestehenden Paarbildung, den Korrekturen und wissenschaftlichen Filtern. N zählt jedes beitragende Paar einmal, nicht dekodierte Empfangsberichte oder Stationen. Für N ≥ 2 gilt:

$$\bar d=\frac{1}{N}\sum_{i=1}^{N}d_i,\qquad s_d^2=\frac{\sum_{i=1}^{N}(d_i-\bar d)^2}{N-1}$$

$$SE=\frac{s_d}{\sqrt N},\qquad h=t_{1-\alpha/2,N-1}SE,\qquad KI=[\bar d-h,\bar d+h]$$

Das Konfidenzniveau ist `1 − α`; beim Standardwert 95% gilt `α = 0.05`. Ohne beitragende Paare sind Mittelwert und Konfidenzintervall nicht verfügbar. Bei einem Paar ist der Mittelwert definiert; Stichprobenstandardabweichung, Standardfehler und Konfidenzintervall sind jedoch nicht verfügbar. Eine Station mit einem verwendbaren Paar kann dieses Paar zur zusammengefassten Berechnung beitragen, auch wenn ihr individuelles Stationskonfidenzintervall nicht verfügbar ist.

Die <strong class="defined-term">Stichprobenstandardabweichung</strong> über alle Paare enthält die Streuung innerhalb und zwischen Stationen. Sie ist weder die Standardabweichung der Stationsmittelwerte noch ein Mittelwert von Stationsstandardabweichungen oder einzelnen Konfidenzintervallen. Ein Segment erhält nur dann eine Farbe, wenn alle folgenden Bedingungen erfüllt sind:

- Die eingestellte Mindestzahl qualifizierter Stationen ist erreicht. Es zählen nur Stationen, die die ΔSNR-Anforderungen erfüllen und mindestens ein verwendbares Paar zum Segment beitragen.
- N beträgt mindestens zwei, und die Intervallberechnung ist endlich und verfügbar.
- Die beobachtete Standardabweichung der Paardifferenzen ist positiv.
- Die **ungerundete** KI-Halbbreite ist positiv und höchstens so groß wie das eingestellte Maximum.

Bei N ≥ 2 bleibt ein berechenbares entartetes Intervall der Breite null numerisch erhalten und wird im Export als entartet gekennzeichnet; das Segment wird schraffiert. Eine Paarvarianz von genau null unterscheidet sich von positiver Varianz, auch wenn eine positive Intervallbreite bei der Anzeige auf null gerundet würde.

Mittelwert und Konfidenzintervall müssen dieselbe vollständige Population qualifizierter Paare beschreiben. Fehlen erforderliche Varianzinformationen, ist das Konfidenzintervall nicht verfügbar; betroffene Gruppen stillschweigend auszulassen und ein Intervall für eine Teilpopulation zu berechnen, ist nicht zulässig.

Dies ist ein <strong class="defined-term">nominelles IID-Student-t-Basismodell</strong>: exakt bei unabhängigen, identisch normalverteilten Paardifferenzen und ansonsten näherungsweise. Wiederholte Beobachtungen eines Funkpfads, benachbarte WSPR-Zyklen und gemeinsame Ausbreitung können abhängig sein. N ist die beobachtete Paaranzahl; die Berechnung korrigiert sie nicht um eine effektive Stichprobengröße für Abhängigkeiten. Das Intervall berücksichtigt keine systematischen Kalibrierungsfehler und entfernt nicht die Auswahl durch gepaarte Dekodierung. Ein schmales Intervall belegt weder Unabhängigkeit noch repräsentative Stichproben oder eine physische Ursache. Die Abdeckung gilt nominell für jedes Segment einzeln, nicht gleichzeitig über die gesamte Karte. Die Präzisionsanforderung ist kein Signifikanztest: Das Intervall darf null enthalten, und ein Mittelwert von null kann qualifizieren.

Bei identischen qualifizierten Paaren, Anpassungen und demselben Konfidenzniveau entspricht diese Berechnung dem bestehenden Mittelwert und Konfidenzintervall der zusammengefassten **Spots** im separaten Abschnitt **Benchmark-Statistik**. Dessen Aggregat **Stationen** mit gleicher Stationsgewichtung und Konfidenzintervall über die Stationsmittelwerte bleibt unverändert.


<a id="sec-7-repeatability-control"></a>
##### 8.5.2 Wiederholbarkeit und experimentelle Kontrolle

Beurteile die Datengrundlage auf mehreren Ebenen:

| Prüfung | Was du untersuchen solltest |
|---|---|
| <strong class="defined-term">Datentiefe</strong> | Bestätigte Empfangsgelegenheiten oder Spot-Paare je beitragender Station. |
| **Breite** | Anzahl und geografische Vielfalt der Stationen und Funkstrecken. |
| **Übereinstimmung innerhalb des Analyselaufs** | Ob verschiedene Gewichtungen, geografische Auswahlen und Zeitansichten ein miteinander vereinbares Bild ergeben. |
| **Wiederholbarkeit** | Ob das Muster in einem neuen Lauf unter vergleichbaren, dokumentierten Bedingungen auftritt. |
| <strong class="defined-term">Experimentelle Kontrolle</strong> | Kalibrierung, Kreuztausch oder vertauschte Zuordnungen, Umkehr des Zeitplans sowie unabhängige Messungen, die alternative Erklärungen prüfen. |

Passen verschiedene Ansichten derselben Beobachtungen zusammen, zeigt das Übereinstimmung innerhalb des Analyselaufs. Es ersetzt keine Wiederholung des Versuchs. [Kapitel 9](#sec-8) erklärt, wie du deine Schlussfolgerung passend zur Datengrundlage formulierst.


<a id="sec-7-validation"></a>
##### 8.5.3 Umfang der Validierung

Auch statistische Angaben zur Softwarevalidierung benötigen Kontext. Nenne Datensatz, Testdatum, WSPRadar-Version oder Quellrevision und Berechnungsmethode. Eine datierte Prüfung belegt, was für diesen Test beurteilt wurde; sie ist keine allgemeine Garantie für jede Station, jeden Zeitraum oder jeden Datensatz.


<a id="sec-7-outliers"></a>
<a id="sec-7-11"></a>
#### 8.6 Experimentelle Analyse von ΔSNR-Ereignissen

**Diese experimentelle, optionale Erkennung findet vorübergehende Abweichungen vom üblichen lokalen ΔSNR einer Gegenstation.** Sie ist eine Diagnose für erfahrene Nutzer, kein erforderlicher Analyseschritt. [Abschnitt 2.5](#sec-outlier) erklärt die Anwendung und [Abschnitt 10.6](#sec-5-6) nennt die Bedienelemente. Im Folgenden geht es um die wissenschaftliche Interpretation und die wichtigsten Prüfungen, nicht um jede Einzelheit des Algorithmus.

<a id="sec-7-outlier-departure"></a>
##### 8.6.1 Abweichung vom lokalen Vergleichsniveau

Die Erkennung untersucht jede Station getrennt anhand ihrer Spot-Paare zu den ursprünglichen WSPR-Zykluszeiten. Eine Station wird durch exaktes Rufzeichen und vollständigen gemeldeten Locator unterschieden und muss die Anforderungen für gepaarte ΔSNR-Zusammenfassungen erfüllen. Zuordnung, Zusammenfassung und wissenschaftliche Filterung sind bereits erfolgt. Die Erkennung arbeitet vor der Zusammenfassung für die Anzeige; eine andere Zeitintervallbreite im Diagramm ändert deshalb die Ereignisse nicht. Bei ausgeschalteter Berichterstattung läuft die Erkennung nicht.

**Die Abweichung ist ΔSNR minus seinem lokalen Vergleichsniveau.** Gegenüber einem Vergleichsniveau von **+8 dB** hat ein Spot-Paar mit **+1 dB** die Abweichung **+1 − (+8) = −7 dB**. Das Target hat weiterhin das höhere SNR, sein Vorteil liegt jedoch 7 dB unter dem lokalen Vergleichsniveau. Eine Änderung des Targets, der Referenz oder beider kann diese Abweichung erzeugen.

Die Gruppierung der Kandidaten folgt dem Vorzeichen der Abweichung, nicht dem Vorzeichen von ΔSNR gegenüber null.


<a id="sec-7-outlier-baseline"></a>
##### 8.6.2 Vergleichsniveau und benachbarte Schwankungen

Eine <strong class="defined-term">Flanke</strong> bezeichnet hier die Beobachtungen vor oder nach einem Kandidaten, aus denen das Vergleichsniveau bestimmt wird. WSPRadar berechnet den Median des ΔSNR in **an UTC ausgerichteten 10-Minuten-Zellen**, die Beobachtungen enthalten. Es verwendet Daten bis zu **sechs Stunden vor und nach** dem Kandidaten. Der Kandidat selbst und ein umgebendes Schutzintervall bleiben bei der Berechnung des Vergleichsniveaus ausgeschlossen.

Jede Flanke benötigt **mindestens vier besetzte Zellen**. Ihr Vergleichsniveau ist der Median ihrer Zellmediane. Das erwartete lokale ΔSNR ist der **arithmetische Mittelwert dieser beiden Vergleichsniveaus**; die Zeiträume vor und nach dem Kandidaten zählen also gleich viel. Fehlende Zellen werden nicht aufgefüllt. Fehlen auf einer der beiden Seiten genügend Daten, bleibt der Kandidat unklassifiziert.

Für die Schwankungen im Umfeld wird das Vergleichsniveau jeder Flanke von ihren Zellmedianen abgezogen. Die verbleibenden Abweichungen heißen <strong class="defined-term">Residuen</strong> und werden aus beiden Flanken zusammengefasst. Ihre <strong class="defined-term">mediane absolute Abweichung (MAD)</strong> ist der Median der absoluten Abstände vom Median dieser zusammengefassten Residuen.

Das <strong class="defined-term">robuste Streuungsmaß</strong> wird wie folgt gewählt:

| Bedingung | Verwendetes Streuungsmaß |
|---|---|
| MAD ist größer als null | MAD |
| MAD ist null, aber IQR ist größer als null | Die Hälfte des IQR |
| MAD und IQR sind beide null | **0,5 dB** |

Auch der IQR wird hier aus den zusammengefassten Residuen berechnet. Der Ersatzwert 0,5 dB ist **kein allgemeiner Mindestwert**.

Der dimensionslose robuste z-Score ist **0,6745 × Abweichung / robustes Streuungsmaß**. Eine Abweichung von **−7 dB** bei einem Streuungsmaß von **1 dB** ergibt etwa **−4,72**. Er beschreibt die Abweichung relativ zu benachbarten Schwankungen und ist weder eine Wahrscheinlichkeit noch ein statistisches Signifikanzniveau.


<a id="sec-7-outlier-qualification"></a>
##### 8.6.3 Qualifikation eines Kandidaten

Nahe beieinanderliegende Abweichungen mit gleichem Vorzeichen bilden vorläufige Kandidaten. Die Gruppierung richtet sich nach den zeitlichen Abständen der berücksichtigten Beobachtungen dieser Station. Für die endgültige Prüfung wird das lokale Vergleichsniveau unter **Ausschluss des vollständigen Kandidaten** bestimmt.

Die **mediane Abweichung** des Ereignisses ist der Median seiner Spot-Paar-ΔSNR-Werte nach Abzug dieses lokalen Vergleichsniveaus. Sie ist nicht der Betrag des beobachteten medianen ΔSNR. Alle vier folgenden Prüfungen müssen bestanden werden:

| Erforderliche Prüfung | Bedingung zum Bestehen |
|---|---|
| <strong class="defined-term">Absolute Abweichung</strong> | Der Betrag der medianen Abweichung des Ereignisses erreicht **Mindestbetrag der ΔSNR-Abweichung (dB)**, mit einer Toleranz von **0,01 dB**. |
| <strong class="defined-term">Relative Abweichung</strong> | Der Betrag seines robusten z-Scores erreicht **Mindestwert des robusten z-Scores**, ohne Toleranz. |
| <strong class="defined-term">Übereinstimmung der Vergleichsniveaus</strong> | Die Flankenmediane davor und danach unterscheiden sich um höchstens **Maximale Differenz der Vergleichsniveaus vor und nach dem Ereignis (dB)** plus **0,01 dB**. |
| <strong class="defined-term">Vorzeichenübereinstimmung</strong> | Bei mindestens **zwei Dritteln der beibehaltenen ursprünglichen Spot-Paare des Kandidaten mit endlichem ΔSNR** hat die Abweichung vom lokalen Vergleichsniveau dasselbe Vorzeichen wie die mediane Abweichung. Der Nenner enthält alle diese Paare innerhalb des Kandidaten, einschließlich der dazwischenliegenden Paare. |

Hier wird geprüft, wie gut die beiden Mediane vor und nach dem Kandidaten übereinstimmen, nicht wie gering die Schwankungen im Hintergrund sind. Die dB-Toleranz betrifft nur die Vergleiche; gespeicherte Beobachtungen und statistische Werte bleiben unverändert. Für jede Ereignisdauer gelten dieselben Schwellen. Ein einzelner großer Wert ersetzt die Prüfungen anhand des Ereignismedians nicht.

**Einseitige Zeitstempel haben eine begrenzte Rolle.** Für das Zeitraster werden alle berücksichtigten gepaarten und einseitigen Zeitstempel einer für ΔSNR berücksichtigten Station verwendet. Sie belegen nicht den tatsächlichen Betriebszeitplan. Bleiben nach einer Änderung der wissenschaftlichen Auswahl zusätzliche einseitige Beobachtungen erhalten, können sich das geschätzte Zeitraster, die zulässigen Lücken zwischen Kandidatenbeobachtungen und die Schutzintervalle ändern. Damit können sich auch Gruppierung, Datengrundlage des Vergleichsniveaus und Erkennungsergebnis ändern, obwohl alle gepaarten ΔSNR-Werte gleich bleiben.

Einseitige Beobachtungen liefern weder ΔSNR für die Erkennung noch eine Stimme bei der Vorzeichenübereinstimmung. Reine Änderungen der Sichtbarkeit in der Darstellung ändern die beibehaltenen Zeitstempel nicht und führen die Erkennung nicht erneut aus.


<a id="sec-7-outlier-boundaries"></a>
##### 8.6.4 Grenzen und Ereignisklassen

Am gemeldeten Beginn und Ende müssen Spot-Paare stehen, deren Abweichungen dasselbe Vorzeichen haben und jeweils **beide** Abweichungsschwellen erreichen. Das Intervall wird auf diese Endpunkte begrenzt und erneut gegen die Anforderungen für das gesamte Ereignis geprüft. Schwächere Beobachtungen dazwischen dürfen verbleiben. Bleibt nur ein kleinerer Kern mit geeigneten Endpunkten übrig, behält er Vergleichsniveau, Streuungsmaß und Datengrundlage des vollständigen Kandidaten. Für diesen Kern wird kein günstigeres Vergleichsniveau neu bestimmt. Erfüllt kein solches Intervall die Anforderungen, wird kein Ereignis gemeldet.

| Ereignisklasse | Beibehaltene Spot-Paare |
|---|---|
| <strong class="defined-term">Spot impulse</strong> | Ein Spot-Paar. |
| <strong class="defined-term">Sustained excursion</strong> | Mindestens drei Spot-Paare über mindestens **30 Minuten**. |
| <strong class="defined-term">Short burst</strong> | Jedes andere Ereignis mit zwei oder mehr Spot-Paaren. |

Alle Klassen bestehen dieselben Prüfungen. Die Zeitspanne zwischen erster und letzter Beobachtung beschreibt beibehaltene Beobachtungsdaten, kein ununterbrochenes Verhalten zwischen den Beobachtungen und keine Dauer eines unbeobachteten physischen Ereignisses.


<a id="sec-7-outlier-context"></a>
##### 8.6.5 Kontext und Grenzen

Das Ereignis jeder Station muss die Prüfungen einzeln bestehen. Nahe Ereignisse mit gleichem Vorzeichen über mehrere Stationen hinweg zu gruppieren, liefert Kontext für die Untersuchung. Die Gruppe kann auf eine Funkstrecke begrenzt sein, in der Richtung übereinstimmen, bereichsweit sein oder mehrere Funkstrecken umfassen. **Bereichsweit** bedeutet, dass die Gruppe nicht benachbarte Richtungssektoren umfasst. Die Gruppierung erhöht weder die Signifikanz noch die Aussagekraft der einzelnen Prüfung.

Nach bestandener Prüfung helfen getrennte Ansichten von Target- und Referenz-SNR sowie die Anzahlen benachbarter einseitiger Beobachtungen, einen Kandidaten zu untersuchen. Diese Angaben werden **nach der Qualifikation** ergänzt. Sie können den Kandidaten weder nachträglich zulässig machen noch verlängern oder seine Einstufung stärken. Davon zu unterscheiden ist die frühere Verwendung einseitiger Zeitstempel für das Zeitraster, die [Abschnitt 8.6.3](#sec-7-outlier-qualification) erklärt.

Die Erkennung ist deterministisch und deskriptiv. Sie liefert keine Signifikanzkorrektur für mehrere Ereignisse, und Ereignisanzahlen sind keine unabhängigen Stichproben. Die Zuordnung einer Ursache erfordert weiterhin die experimentellen Kontrollen aus [Kapitel 2](#sec-3), [Kapitel 3](#sec-4) und [Kapitel 9](#sec-8).


<a id="sec-8"></a>
### 9. Durch die Datengrundlage getragene Aussagen und Reproduzierbarkeit

Ein nützlicher Bericht nennt, was beobachtet wurde, wie es zusammengefasst wurde und was der Vergleich belegen kann. Nenne die einbezogenen Stationen, das Band, das UTC-Zeitfenster, den geografischen Bereich, die Gewichtung und die stützenden Anzahlen. Unterscheide anschließend das beobachtete Ergebnis von jeder vorgeschlagenen Erklärung. Dieses Kapitel liefert Formulierungsbeispiele und nennt die Aufzeichnungen, die zur Bewahrung des Ergebnisses nötig sind.


<a id="sec-8-1"></a>
#### 9.1 Aussageklassen und passende Formulierungen

Unterschiedliche Aussagen benötigen unterschiedliche Datengrundlagen:

| Aussageklasse | Was die Aussage bedeutet | Benötigte Datengrundlage |
|---|---|---|
| **Deskriptiv** | Was in den beibehaltenen Beobachtungen auftrat. | Population, Bereich, Kennzahl, Gewichtung und stützende Anzahlen benennen. |
| <strong class="defined-term">Vergleichend</strong> | Wie sich Target und Referenz unterschieden. | Die Referenz und die beobachteten gepaarten und einseitigen Daten beschreiben. Angeben, ob gemeinsamer Betrieb unabhängig festgestellt wurde oder der Lauf eine Auswertung historischer Empfangsberichte war. |
| <strong class="defined-term">Bauteilzuordnung</strong> | Der Unterschied folgt einer bestimmten Antenne, Speiseleitung, einem Empfänger oder einem anderen geprüften Bauteil. | Eine kontrollierte Anordnung, geeignete Kalibrierung und vorzugsweise Kreuztausch oder Umkehr der Zuordnungen. |
| <strong class="defined-term">Kausal</strong> | Die geprüfte Änderung hat den Effekt verursacht. | Ein Design, das plausible alternative Erklärungen kontrolliert; WSPRadar-Zusammenfassungen allein reichen nicht aus. |
| **Inferenzstatistisch** | Das Ergebnis ist über diese Beobachtungen hinaus verallgemeinerbar, mit angegebener Konfidenz oder Signifikanz. | Ein begründetes Modell für Stichprobe und Abhängigkeiten sowie eine für diese weitergehende Aussage geeignete Analyse. Die nominelle KI-Berechnung von WSPRadar allein liefert diese umfassendere Analyse nicht. |

Passe die Aussage an die Größe an:

- **Performance** beschreibt den Dekodiererfolg des Targets innerhalb bestätigter Empfangsgelegenheiten und seine mindestens einmal erfassten Gegenstationen während des gewählten Zeitfensters.
- **Benchmark-ΔSNR** beschreibt Target-SNR minus Referenz-SNR innerhalb beibehaltener Spot-Paare. Nur auf einer Seite dekodierte Signale haben keine gepaarte SNR-Differenz.
- **Dekodierergebnisse** beschreiben gepaarte und einseitige Beobachtungsdaten. Das **Verhältnis der Stationszahlen** vergleicht die Anzahlen unterschiedlicher Stationen; **ΔDecode** vergleicht die zusammengefassten Dekodierzahlen. Keiner der beiden Vorteile ist eine Gewinnquote des Targets oder eine absolute Dekodierwahrscheinlichkeit.
- **Richtungs- und Entfernungsmuster** beschreiben die beobachteten Funkpfade, ohne Abstrahlwinkel oder Gewinnmuster einer Antenne direkt zu messen.

Ein kontrollierter Benchmark beruht auf unabhängig bekanntem gemeinsamem Betrieb. Eine **Auswertung historischer Empfangsberichte** kann die berichteten Unterschiede beschreiben; ungeprüfte Zeitpläne, Betriebsverfügbarkeit oder Uploads können jedoch einseitige Anzahlen erklären. Stelle diese Auswertung nicht als kontrollierten Vergleich des Dekodiererfolgs dar.

| Vermeiden | Durch die Datengrundlage getragene Formulierung |
|---|---|
| „Antenne A hat 3 dB mehr Gewinn als B.“ | „Für dieses Band, UTC-Zeitfenster und Segment betrug der Mittelwert des gepaarten ΔSNR über alle Paare [Mittelwert] dB mit einem [Konfidenzniveau]%-Konfidenzintervall von ±[Halbbreite] dB für Signalweg A gegenüber B, gestützt auf [n] Stationen mit erfüllten ΔSNR-Anforderungen und [m] Spot-Paare.“ |
| „Meine Empfängerempfindlichkeit beträgt 72 %.“ | „Der Mittelwert der Stationsdekodierquoten des Targets betrug während des angegebenen Zeitfensters über [n] berücksichtigte Stationen 72 %. Jede Station wurde gleich gewichtet; ihre Quote beruht auf bestätigten Empfangsgelegenheiten.“ |
| „Performance sollte nahe 100 % liegen.“ | „Die Dekodierquote beschreibt den Erfolg innerhalb bestätigter Empfangsgelegenheiten; 100 % ist kein zu erwartender Ausgangswert.“ |
| „A ist statistisch signifikant besser.“ | „Der deskriptive Median des ΔSNR begünstigte A innerhalb der ausgewählten Spot-Paare; es wurde kein Signifikanztest durchgeführt.“ |
| „Die Antenne hat einen flacheren Abstrahlwinkel.“ | „Der beobachtete Vorteil konzentrierte sich auf die angegebenen Segmente mit größeren Entfernungen; der Abstrahlwinkel wurde nicht gemessen.“ |
| „A ist effizienter, weil es mehr exklusive Dekodierungen hatte.“ | „A lieferte unter den dokumentierten Leistungs-, Zeitplan- und Netzwerkbedingungen mehr einseitige Dekodierbeobachtungen; der Wirkungsgrad wurde nicht isoliert.“ |

Aus einer SNR-Differenz zwischen vollständigen Aufbauten geht allein nicht hervor, welches Bauteil oder welcher Umwelteinfluss sie verursacht hat. Unterscheide zwischen übereinstimmenden Ansichten desselben Analyselaufs und einem wiederholten Ergebnis in einem neuen, geeignet kontrollierten Lauf. Dokumentiere die zutreffende Betriebserklärung beziehungsweise die Grenzen der historischen Auswertung, die angewandte Referenzkorrektur und die Datenanzahlen anhand der Checkliste in [Abschnitt 9.3](#sec-8-3).


<a id="sec-8-2"></a>
#### 9.2 Interpretationsgrenzen

Die Berechnungen beschreiben die durch den Lauf ausgewählten Beobachtungsdaten. Ihre Grenzen ergeben sich aus den Empfangsberichten, den Auswahlregeln und dem physischen Vergleich:

| Grenze | Folge für die Interpretation |
|---|---|
| **Gemeldete Daten** | Rufzeichen, Locatoren und Leistungen können falsch sein. Datenbanken enthalten erfolgreiche Dekodierungen, nicht jeden Sendeversuch oder ein vollständiges Fehlerprotokoll. Datensätze und Verfügbarkeit können sich nach dem Lauf ändern. |
| **Auswahl von Empfangsgelegenheiten und SNR** | Performance ist auf beobachtbare Target-Aktivität und bestätigte Empfangsgelegenheiten bedingt. Sein erfolgreiches SNR enthält nur dekodierte Signale. Benchmark-ΔSNR erfordert nutzbares SNR auf beiden Seiten; einseitige Beobachtungen haben kein SNR der fehlenden Seite, das rekonstruiert werden könnte. |
| **Betriebsbedingungen** | Ein kontrollierter Benchmark erfordert unabhängig bekannten gemeinsamen Betrieb und behält zulässige einseitige Beobachtungsdaten symmetrisch bei. Die Auswertung historischer Empfangsberichte lässt diese Betriebsvoraussetzung ungeprüft. Weder beobachtete Abdeckung noch ein Bestätigungskästchen beweist unabhängig die Betriebsverfügbarkeit oder gleiche Zeitpläne. |
| **Physikalische Ursachen** | Hardware, Software, Gelände, lokaler Störpegel, Polarisation und Ausbreitung bleiben miteinander verbunden, sofern der Versuch sie nicht trennt. Simultanes TX kann weiterhin Unterschiede von Leistung, Frequenzgang, Isolation und Kopplung enthalten. |
| **Abhängigkeit und Verallgemeinerung** | Empfangsberichte teilen Stationen, Zeiträume, Geografie und Ausbreitung. Eine Zeilenzahl belegt keine unabhängige Stichprobengröße. Konfidenzintervalle für Mittelwerte verwenden ein ausdrücklich benanntes Modell mit Unabhängigkeitsannahme und sind nicht allgemein für WSPR validiert. WSPRadar liefert keine automatischen Signifikanztests oder kausalen Schlussfolgerungen. |

WSPRadar misst Antennengewinn gegenüber einem isotropen Strahler (**dBi**), Strahlungswirkungsgrad, Abstrahlwinkel, Ausbreitungsart, kalibrierte Empfängerempfindlichkeit oder absolute Feldstärke nicht direkt. Eine Gewinn*differenz* wird in **dB** ausgedrückt; beobachtetes ΔSNR ist jedoch nicht automatisch eine Messung dieser Differenz.

Eine breite Datengrundlage, übereinstimmende Ergebnisse und Wiederholung unter dokumentierten Kontrollen können eine praktische Stationsentscheidung stützen. Begrenze die Aussage auf das, was der Versuch gemessen hat; [Abschnitt 8.5](#sec-7-claims) erklärt Abhängigkeit und experimentelle Kontrolle.


<a id="sec-8-3"></a>
#### 9.3 Checkliste für Berichterstattung und Reproduzierbarkeit

Bewahre drei Ebenen auf, wenn du Ergebnisse vergleichst, veröffentlichst oder daraus Maßnahmen ableitest. Der Export liefert einen großen Teil der Analysedefinition und Beobachtungsdaten; bewahre Messungen am physischen Aufbau und Betriebsaufzeichnungen separat auf.

**1. Analysedefinition**

- WSPRadar-Anwendungsversion und, soweit verfügbar, Quellrevision;
- Datenbankquelle und ursprüngliches Exportdatum;
- RX-/TX-Richtung, Ergebnistyp und Benchmark-Design;
- exakte Rufzeichen und Locatoren von Target und Referenz;
- Band und wirksame UTC-Grenzen;
- geografischer Bereich, Sonnenstand, Ausschlüsse und Mindestanforderungen an die Datengrundlage;
- Zweck der Referenzkorrektur, vorzeichenbehafteter Wert und Kalibriergrundlage;
- zutreffende Erklärung gemeinsamen Betriebs oder Bestätigung der Auswertung historischer Empfangsberichte samt Einschränkungen;
- vor der Ergebnisbetrachtung gewählter primärer Bereich sowie alle geprüften alternativen Einstellungen oder Bereiche; und
- ob der Lauf explorativ oder bestätigend war.

Trägt ein möglicher Ausreißer zur Schlussfolgerung bei, dokumentiere außerdem die aktivierte Berichterstattung, die drei Erkennungsschwellen, die Detektorversion, den exakten Funkpfad, das UTC-Intervall, die Ereignisklasse sowie ob der Befund explorativ war oder unter einem zuvor festgelegten bestätigenden Aufbau bewertet wurde.

**2. Datengrundlage der Schlussfolgerung**

- Berichtete Kennzahl und ihre Gewichtung;
- berücksichtigte Stationen und bestätigte Empfangsgelegenheiten für Performance;
- Stationen mit gepaarten Beobachtungen und Anzahlen von Spot-Paaren für Benchmark;
- Zusammenfassungen auf Stations- und Beobachtungsebene;

- Bei einem berichteten Konfidenzintervall: zugehöriger Mittelwert und Schätzer, Konfidenzniveau, Methode, beitragende Einheit und Anzahl, Halbbreite oder vollständige Grenzen, Verfügbarkeitsstatus und Unabhängigkeitsannahme;
- beim Aggregat **Stationen** zusätzlich: Stationsanzahl und Standardabweichung beziehungsweise Standardfehler zwischen Stationsmittelwerten;
- beim Kartenmittelwert über alle Paare zusätzlich: qualifizierte Paaranzahl N, Standardabweichung beziehungsweise Standardfehler der Paardifferenzen, qualifizierte Stationsanzahl, tatsächlich verwendete Stationsmindestzahl, maximale Halbbreite und Qualifikationsgrund;
- Verhältnis der Stationszahlen, zusammengefasstes ΔDecode und relevante Anzahlen gepaarter Ereignisse, Ereignisse nur des Targets und nur der Referenz;
- geografischer und zeitlicher Bereich, einschließlich einzelner Stationen oder kurzer Intervalle mit starkem Einfluss auf das Ergebnis; und
- Übereinstimmung innerhalb des Analyselaufs und etwaige Wiederholung in einem separaten Lauf.

**3. Externe Versuchsaufzeichnung**

- Antennen, Speiseleitungen und Anordnung der HF-Signalwege;
- Umschalter-/Splitterverbindungen und Zuordnung der Meldeidentitäten zu physischen Signalwegen;
- Sender-, Empfänger-, Dekoder- und Softwareversionen;
- tatsächliche Sendeleistung und ihre Grundlage in der WSPR-Leistungsangabe;
- Kalibriermessungen und Bezugsebene;
- tatsächliche Zeitpläne, Aufzeichnungen zur Stützung der Benchmark-Betriebserklärung, Unterbrechungen, Kreuztausch und vertauschte Zuordnungen; und
- Fehler, Störungen, Wetter oder beabsichtigte Änderungen, die für die Interpretation relevant sind.

Bewahre das ursprüngliche Exportpaket zusammen mit diesen Notizen auf. Ein späterer Abruf kann Datenbankkorrekturen oder eine neuere WSPRadar-Version widerspiegeln.


<a id="sec-8-4"></a>
#### 9.4 Exportpaket der Analyse

Wähle den geografischen Bereich, die Stationsdaten und ein etwaiges Fokusintervall, die du bewahren möchtest. **Alle Ergebnisse zum Herunterladen vorbereiten** erstellt die ZIP-Datei; **Vorbereitete Ergebnisse herunterladen** speichert sie. Bereite das Paket nach Änderungen dieser Auswahlen erneut vor.

Die ZIP-Datei enthält `config/` und je nach Analyse entweder `benchmark/` oder `performance/`. Die verfügbaren Abbildungen hängen von den beibehaltenen Beobachtungsdaten und den aktuellen Auswahlen ab. Jede verfügbare Abbildung wird als hochauflösende helle und dunkle PNG-Datei mit denselben Beobachtungsdaten bereitgestellt. Die helle Datei verwendet ihren Dateinamen `figure_*.png`; die dunkle Datei ergänzt im selben Ordner `_dark` vor `.png`.

| Artefakt | Inhalt, Umfang und Verfügbarkeit |
|---|---|
| <strong class="defined-term">Haftungsausschluss</strong> | `disclaimer.txt` enthält den vollständigen Abschnitt [Experimentelle Nutzung & Haftungsausschluss](#sec-disclaimer) in englischer Sprache. Er liegt jedem Paket bei. |
| **Konfiguration** | `wspradar_config.config` stellt Analyseeinstellungen und unterstützte Ansichtsauswahlen für einen weiteren Lauf wieder her. Sie enthält nicht die ursprünglichen Beobachtungen. |
| <strong class="defined-term">Metadaten des Analyselaufs</strong> | `run_metadata.json` dokumentiert Softwareversion, Datenbank, tatsächliche Datenauswahl, Analyseeinstellungen, Korrekturen, Untersuchungsbereich und aktivierte Ausreißereinstellungen. Benchmark dokumentiert außerdem die Bestätigung seiner Bedingungen, die Methodenversion, die ausgewählten zeitlichen Statistiken für Segment und Station, CI-Alpha und -Methode sowie die Definitionen der Stations- und Spot-Aggregation. Die Bestätigung unterscheidet nicht zwischen bestätigtem gemeinsamem Betrieb und akzeptierten Einschränkungen und ist kein unabhängiger Betriebsnachweis. TX Performance erhält die wissenschaftliche Auswahl `tx_snr_normalization_to_30dbm` und dokumentiert die wirksame Bezugsgröße unter `performance_snr`: `value_basis`, `normalization_to_30dbm`, die angewandte Formel und `decode_outcomes_changed: false`. Die Formel lautet bei ausgeschalteter Normierung `reported_snr` beziehungsweise bei eingeschalteter Normierung `reported_snr - reported_tx_power_dbm + 30`. Jeder Performance-Ergebnisblock dokumentiert außerdem `performance_corroboration` mit Einschaltzustand, Obergrenze der Gelegenheitszahl, fester Anforderung von drei weiteren meldenden Empfängern, Ausschlüssen, Erhebungsstatus und Bedeutung für die Stationsqualifikation. |
| <strong class="defined-term">Verarbeitete Beobachtungsdaten</strong> | `analysis_cache.parquet` enthält die beibehaltenen Beobachtungsdaten über den gesamten geografischen Bereich der abgeschlossenen Analyse nach wissenschaftlicher Filterung. Die Datei ist nicht auf das ausgewählte Segment beschränkt und kein unveränderter Datenbankdownload. Performance-`target_snr` wird auf der gewählten Bezugsgröße des abgeschlossenen Laufs gespeichert; dieselbe Spalte ist nicht zugleich ursprünglich und normiert. Das zusätzliche Merkmal `corroborated_cycle` ist 1, wenn mindestens eine passende Aussendung in dieser Kombination aus Identität und Zyklus die feste Anforderung von drei weiteren meldenden Empfängern erfüllt, andernfalls 0. Lies sie zusammen mit den Laufmetadaten: `evidence_acquired: false` bedeutet, dass die zusätzliche Bestätigung nicht erhoben wurde, weil der Filter ausgeschaltet war oder die gewählte Gelegenheitsmindestzahl seine Obergrenze überschritt; ein Nullwert ist dann kein gemessener Mangel an Bestätigung. |
| <strong class="defined-term">Benchmark-Kartensegmentergebnisse</strong> | `benchmark/map_segments.parquet` dokumentiert den Kartenmittelwert über alle qualifizierten Paare, Paaranzahl N, Stichprobenstandardabweichung und Standardfehler der Paardifferenzen, Intervallgrenzen und Halbbreite, Konfidenzniveau beziehungsweise Alpha und Methode, KI-Status, qualifizierte Stationsanzahl und Stationsmindestzahl, maximale KI-Halbbreite sowie Qualifikationsgrund. Bestehende Segmentfelder und deskriptive Zusammenfassungen behalten ihre eigenen Schätzernamen. Schraffierte Segmente behalten einen berechenbaren Mittelwert und numerisches Intervall beziehungsweise Status. |
| <strong class="defined-term">Stationsauswertungs-CSV</strong> | `table_station_insights.csv` folgt bei Performance und Benchmark der vollständigen oder optional durch die Segmentdetails gefilterten Stationsliste. Beide berücksichtigen außerdem die Sichtbarkeit von Stationen ohne Target-Dekodierungen beziehungsweise einseitigen Beobachtungen sowie die Spaltenfilter; Bereich und Filter stehen in den Metadaten. Stationskennzahlen behalten ihre Werte über den vollständigen Lauf. Leere Tabellen behalten ihre Kopfzeilen. Die separate `table_drilldown_all_stations_current_segment.csv` folgt weiterhin dem aktiven Bereich der Segmentdetails. |
| <strong class="defined-term">Detaildaten-CSV-Dateien</strong> | Beobachtungsdaten auf Zeilenebene für ausgewählte Stationen oder alle Stationen im aktiven Segment. Die Tabelle der ausgewählten Stationen kann Fokus und Tabellenfiltern folgen. Beide Dateien behalten bei leerem Ergebnis ihre Kopfzeilen. |
| <strong class="defined-term">Ausreißer-CSV-Dateien</strong> | `table_delta_snr_outlier_event_paths.csv` fasst qualifizierende Funkpfadereignisse zusammen; `table_delta_snr_outlier_paired_evidence.csv` enthält ihre chronologischen Spot-Paare einschließlich korrigierten Referenz-SNR. Beide decken das aktive Segment ab und werden über IDs verknüpft, die nur innerhalb dieses Pakets gültig sind. Berichterstattung aus: Dateien fehlen. Berichterstattung an, ohne Befunde: nur Kopfzeilen. Befunde bleiben Kandidaten, keine bestätigten physischen Ereignisse. |
| **Zusammenfassung von Spots und Stationen** | `figure_spots_stations.png` bewahrt die vollständigen Zusammenfassungen von Spots und Stationen für den aktuellen Bereich der Segmentdetails in einer Abbildung unter `benchmark/` oder `performance/`; `figure_spots_stations_dark.png` enthält die dunkle Variante. |
| <strong class="defined-term">Karten-, Segment- und zeitliche Abbildungen</strong> | Die Karte deckt die abgeschlossene Analyse ab. Segment- und zeitliche Abbildungen folgen dem aktiven Segment, einschließlich der jeweils verfügbaren chronologischen Ansichten und Ansichten nach Tageszeit. |
| <strong class="defined-term">Abbildungen ausgewählter Stationen</strong> | Benchmark und Performance verwenden die vollständigen Daten der ausgewählten Station aus dem Analyselauf, unabhängig vom Stationslistenfilter. Bei aktivierter Ausreißerberichterstattung kann Benchmark stattdessen zusammengefasstes ΔSNR mehrerer ausgewählter Funkpfade zeigen. Performance enthält zwei zeitliche Einzelstationsabbildungen: absolutes SNR und Dekodierquote mit zeitlicher Datengrundlage; die redundante Entfernungs-Heatmap und die ausschließlich segmentbezogene Abweichungsabbildung entfallen. Jeder Untertitel nennt die berechnete Entfernung vom Target nach dem Locator. |
| <strong class="defined-term">Fokusabbildungen der Detaildaten</strong> | Zusätzliche Abbildungen für genau eine ausgewählte Station und ihr aktives Fokusintervall. Sie bewahren einzelne Beobachtungen und den chronologischen Kontext neben den gewöhnlichen Abbildungen ausgewählter Stationen. Kandidatenhilfslinien gelten für die fokussierte Episode. |

| Zeitliche Abbildung | Datei im Performance-Paket |
|---|---|
| Segment 1: absolutes SNR erfolgreicher Dekodierungen | `performance/figure_segment_temporal_snr_absolute.png` |
| Segment 2: zeitliche Datengrundlage und zusammengefasste Dekodierquote | `performance/figure_segment_temporal_evidence.png` |
| Segment 3: Dekodierquote nach Entfernung/Zeit | `performance/figure_segment_temporal_decode_distance.png` |
| Segment 4: SNR-Abweichungen vom Mittelwert oder Median der jeweiligen Station im Analyselauf | `performance/figure_segment_temporal_snr_deviation.png` |
| Ausgewählte Station 1: absolutes SNR erfolgreicher Dekodierungen | `performance/figure_selected_station_snr_evidence.png` |
| Ausgewählte Station 2: zeitliche Datengrundlage und zusammengefasste Dekodierquote | `performance/figure_selected_station_temporal_evidence.png` |

Die Datei `config/run_metadata.json` im Paket erhält `performance_temporal_statistics`. `segment` behält seine Rolle für Segmentabweichungsmetadaten; `segment_absolute` beschreibt die absolute Ansicht, `selected_station` bleibt absolut, und `segment_decode_distance` beschreibt Entfernungszellen. Diese Metadaten unterscheiden die Gewichte einzelner Beobachtungen, Zusammenfassung nach Tageszeit, Dichte relativ zum Maximum jedes Panels, tatsächliche zusammengefasste Prozentsätze, den gemeinsamen dargestellten Quotenbereich samt Ersatzbereichsstatus, Intervallverfügbarkeit und Behandlung festgehaltener Vergleichsniveaus. Die obigen Abbildungspfade liegen unterhalb des Paketwurzelverzeichnisses.

Alle vier zeitlichen Segmentabbildungen sind im Ergebnispaket enthalten, auch wenn die Expertenansicht eingeklappt ist. Das Einzelstationspaket enthält zwei zeitliche Abbildungen; es enthält weder die redundante Entfernungs-Heatmap noch eine Abweichungsabbildung.

Die Performance-Abbildung nach SNR-Klasse folgt der aktuellen Auswahl in den Segmentdetails. Wenn die Abbildung verfügbar ist, enthält das Paket `performance/figure_decodes_stations_by_snr.png` und `performance/figure_decodes_stations_by_snr_dark.png`. Der Eintrag `performance_snr_reach` in `config/run_metadata.json` dokumentiert Auswahl, Statistik der Markierungen, SNR-Bezugsgröße, Zählregeln und feste Nenner.

Lies die wirksame Mindestzahl meldender Empfänger aus dem Zahlenfeld `performance_corroboration.minimum_other_reporters` ab. Der aktuelle Export schreibt weiterhin `mode_specific_five_other_reporter_requirement_met` in das Textfeld `evidence_definition`. Die implementierte Mindestzahl beträgt drei.

TX-Performance-Exporte erhalten `tx_snr_normalization_to_30dbm` und die wirksame SNR-Bezugsgröße. Die beibehaltenen `target_snr`-Werte und alle daraus abgeleiteten SNR-Tabellen, Abbildungen, Vergleichsniveaus und Intervalle verwenden diese eine Bezugsgröße des abgeschlossenen Laufs. Ursprüngliche und normierte Ergebnisse dürfen keine irreführende gemeinsame 30-dBm-Beschriftung tragen.

Numerische Benchmark-Statistikexporte behalten Mittelwert, Stichprobenstandardabweichung, Standardfehler, untere und obere Intervallgrenze, Halbbreite, Alpha, Methode, beitragende Anzahl sowie Verfügbarkeit und Status mit voller Genauigkeit. Diese Anzahl bezeichnet gepaarte Beobachtungen bei Konfidenzintervallen einzelner Stationen und zusammengefasster Paare, dagegen Stationsmittelwerte bei aggregierten Stationskonfidenzintervallen. Die Tabellenanzeige **± Halbbreite** ersetzt diese Werte nicht. **Mittelwert der Stationsmittelwerte**, **Median der Stationsmediane** und **Mittelwert der Stationsmediane** werden getrennt benannt; der erste erhält sein eigenes Konfidenzintervall, berechnet über diese Stationsmittelwerte. Diese Definitionen von **Stationen** bleiben unverändert. Kartensegmentexporte beschreiben dagegen den Mittelwert über alle qualifizierten Paare und dessen eigenes Konfidenzintervall, einschließlich Paaranzahl N, Standardabweichung und Standardfehler der Paardifferenzen, qualifizierter Stationsanzahl, Stationsmindestzahl, maximaler KI-Halbbreite und Qualifikationsgrund. Entartete Intervalle behalten numerische Grenzen der Breite null zusammen mit ihrem ausdrücklichen Status. Beibehaltene datierte UTC-Beobachtungen und vollständige Stationsidentitäten bleiben für spätere abhängigkeitsbewusste Auswertungen verfügbar.

Die maschinenlesbaren Felder des Konfidenzintervallergebnisses umfassen `n`, `mean`, `sample_sd`, `standard_error`, `lower`, `upper`, `half_width`, `alpha`, `method`, `available` und `status`. Zeitliche Profile bewahren vollständige Intervallgrenzen in `ci_lower` und `ci_upper` und die beobachtete Anzahl beitragender Paare in `ci_n`, einschließlich null bei leeren Intervallen. Die übergeordnete Angabe `statistics_availability` und `spots.distribution_status` unterscheiden eine nicht verfügbare zugrunde liegende Verteilung von verfügbaren zwischengespeicherten Statistiken oder Konfidenzintervallen.

Das Aggregat mit gleicher Stationsgewichtung für den ausgewählten Bereich bleibt in `benchmark_mean_statistics.stations.mean_ci` dokumentiert; das zusammengefasste Spots-Ergebnis bleibt getrennt. `benchmark_maps.delta_snr` benennt den Kartenschätzer über alle qualifizierten Paare, die gleiche Paargewichtung, Konfidenzintervallmethode und beitragende Einheit, Anzahlen- und Präzisionsanforderungen sowie die Segmentergebnisdatei. Ein Bereich der Segmentdetails kann mehrere Segmente enthalten und darf nicht mit einem einzelnen Kartensegment verwechselt werden. Wenn die Segmentdetails genau die qualifizierten Paare eines Segments, dessen Anpassungen und Konfidenzniveau auswählen, stimmen Karten- und zusammengefasstes Spots-Ergebnis überein.

Bewahre Metadaten zusammen mit den Beobachtungsdaten auf: Die Konfiguration allein kann nicht jede Auswahl rekonstruieren. Fehlende Metadaten zur Datenauswahl bleiben unbekannt; sie belegen nicht, dass der Standardfilter verwendet wurde. Siehe [Abschnitt 11.4](#sec-6-4). Der Bereich der Segmentdetails, der Stationslistenbereich und der Bereich ausgewählter Stationen beziehungsweise des Fokus sind verschieden; eine Benchmark-Stationsabbildung darf nicht als auf Richtung und Entfernung der Segmentdetails begrenzt gelesen werden.

Die Dateinamen der Benchmark-Abbildungen benennen ihre Größen:

- `figure_map_delta_snr.png` und `figure_map_delta_decode.png`;
- `figure_decodes_over_snr.png` und `figure_segment_statistics.png`;
- `figure_segment_temporal_delta_snr.png` und `figure_segment_temporal_delta_decode.png`;
- `figure_selected_station_temporal_delta_snr.png` und `figure_selected_station_temporal_delta_decode.png`; und
- `figure_drilldown_zoom_delta_snr.png` und `figure_drilldown_zoom_delta_decode.png`.

Diese Dateien sind enthalten, wenn die nötigen Beobachtungsdaten und Auswahlen verfügbar sind. Der Archivname bleibt `WSPRadar_export_YYYY_MM_DD__HH_MM.zip`. Bewahre das ursprüngliche Paket zusammen mit den externen Aufzeichnungen aus [Abschnitt 9.3](#sec-8-3) auf; eine spätere Abfrage oder ein erneuter Lauf kann andere Datensätze oder Ergebnisse liefern.


<div style="page-break-before: always;"></div>

<a id="part-ii"></a>

## Teil IV: Bedienelemente und Fehlersuche

Hier kannst du Einstellungen nachschlagen und Problemen nachgehen. [Teil I](#part-i) erklärt, wie du WSPRadar verwendest; **So liest du die Ergebnisse** neben dem jeweiligen Ergebnis erläutert die Diagramme; [Teil III](#part-iii) definiert die Berechnungen und ihre Grenzen.

<a id="sec-5"></a>

### 10. Bedienelemente und Konfiguration

Wenn du die Analyseart, Rufzeichen oder Locator der Stationen, das Band, den UTC-Messzeitraum, die SNR-Korrektur der Referenz, Filter oder Anforderungen an die Datengrundlage änderst, wird das abgeschlossene Ergebnis gelöscht. Du musst die **Analyse erneut starten**. Änderungen an der Auswahl in den Segmentdetails, an Filtern der Stationsliste, an der zeitlichen Zusammenfassung, an der Zeitbasis oder an der Ansicht der Detaildaten starten keine neue Analyse. Bei Performance aktualisiert **Gemeinsames Konfidenzniveau** die zeitlichen Mittelwertintervalle im abgeschlossenen Ergebnis. Bei Benchmark erfordert diese Einstellung einen neuen Analyselauf.

<a id="sec-5-1"></a>

#### 10.1 Bedienelemente für den Ablauf

| Bedienelement | Das solltest du wissen |
|---|---|
| **Eingabeansicht** | Geführt und Kompakt verwenden dieselben Analyseeinstellungen. Deine gewählte Eingabeansicht bleibt für die Sitzung ausgewählt und wird nicht in gespeicherten Konfigurationen hinterlegt. |
| **Demo laden** | Lädt Einstellungen, ohne die Analyse zu starten, und behält deine gewählte Ansicht **Geführt** oder **Kompakt** bei. **Laden und Einstellungen schrittweise prüfen** öffnet die geführten Schritte nacheinander oder den vollständigen kompakten Editor beim ersten Einstellungsbereich; **Laden und vor dem Start prüfen** öffnet direkt die Prüfung der gewählten Ansicht. In der geführten Ansicht enthält der eingeklappte Bereich **Demo mit Anleitung** weiterhin die Versuchsnotizen und die Navigationsaktionen **Schritt für Schritt durch den Aufbau** / **Direkt zur Prüfung**. Erst **RX-Analyse starten** oder **TX-Analyse starten** startet die Analyse. |
| **Neu beginnen** | Löscht Einstellungen und Ergebnisse und stellt die Standardwerte einschließlich des UTC-Messzeitraums wieder her. Sprache und Eingabeansicht bleiben unverändert. |
| **Konfiguration laden / Konfiguration speichern** | Lädt oder speichert die zutreffenden Analyseeinstellungen und unterstützten Ansichtsoptionen. Gespeicherte Datumsangaben sind feste UTC-Grenzen, kein mitlaufender Zeitraum. Eine Konfiguration enthält weder Ergebnisdaten noch Stationsnotizen. |
| **RX-Analyse starten / TX-Analyse starten** | Startet die gewählte Analyse nach der Prüfung der Eingaben. Korrigiere zuerst markierte Felder und wähle gegebenenfalls den Standort der Referenz. Eine Karte kann bereits erscheinen, bevor die übrigen Ansichten bereitstehen; warte auf **Abgeschlossen**. |
| **Alle Ergebnisse zum Herunterladen vorbereiten** | Erstellt den Export für die aktuelle Auswahl. Wähle anschließend **Vorbereitete Ergebnisse herunterladen**. Bereite den Export erneut vor, wenn du die Auswahl geändert hast. Siehe [Inhalt des Exports](#sec-8-4). |

Wenn eine Änderung nach dem Analyselauf das abgeschlossene Ergebnis löscht, öffnet sich der eingeklappte Bereich **Prüfung** in **Geführt** oder **Kompakt** wieder, sobald die Einstellungen gültig sind. Unter **ANALYSE STARTEN** findest du **Konfiguration speichern** und die Startschaltfläche für die gewählte Analyserichtung. Bei Benchmark stehen die Erläuterung der Betriebsbedingungen und das Bestätigungsfeld direkt über diesen Schaltflächen. Du kannst die Prüfung auch ohne Häkchen öffnen und ansonsten gültige Einstellungen speichern. Zum Start eines Benchmarks musst du das Häkchen setzen.

**Tastatur:** Mit `Tab` und `Shift+Tab` wechselst du zwischen den Bedienelementen. In der geführten Ansicht prüft ein vorwärts gerichteter `Tab` über das Ende eines Einstellungsbereichs hinaus die Eingaben und öffnet den nächsten Schritt, genau wie **Weiter**. Bei Fehlern springt der Fokus zum ersten ungültigen Feld zurück. Das Erreichen der Prüfung startet die Analyse nicht. Die separaten Hilfesymbole `?` erfordern ein Zeigegerät.

Das Laden oder Speichern einer Konfiguration startet keine Analyse. Nicht unterstützte alte Formate werden abgewiesen. Eine Kompatibilitätsausnahme akzeptiert ein vollständiges, gültiges Paar der früheren ΔDecode-Schwellenwerte für absolute Anzahlen und ersetzt sie mit einem Hinweis durch den **Standardwert von 1 % Ereignisanteil**; Anzahlen werden dabei nicht in Prozentwerte umgerechnet. Prüfe geladene Einstellungen vor dem Start.

<a id="sec-5-2"></a>

#### 10.2 Fragestellung, Target und Messzeitraum

| Bedienelement | Standardwert und wesentliche Regeln |
|---|---|
| **Fragestellung** | Erforderlich: Wähle RX Performance, TX Performance, RX Benchmark oder TX Benchmark. Nur Benchmark benötigt eine Referenz. |
| **Target-Rufzeichen** | Erforderlich. Verwende bei RX **Target-Rufzeichen (untersuchter Empfänger)** und bei TX **Target-Rufzeichen (untersuchter Sender)**. Gib das Rufzeichen genau so ein, wie es gemeldet wird, einschließlich Präfix oder Suffix. `CALL`, `CALL/P` und `CALL-1` sind unterschiedliche gemeldete Rufzeichen. |
| **Target-Locator (optional)** | Lass das Feld für die Standortsuche nach **Analyse starten** leer oder gib einen gültigen Maidenhead-Locator mit vier oder sechs Zeichen ein. Im leeren Feld steht `>auto-discover<`. Die ersten vier Locatorzeichen bestimmen die Auswahl der Target-Empfangsberichte; der vollständig eingegebene oder ermittelte Locator legt den Ausgangspunkt für Karte, Entfernung, Richtung und Sonnenstandsberechnung fest. |
| **Band** | Standardwert **20m**. Wähle ein Band. |
| **TX-SNR-Normierung auf 30 dBm** | Nur TX Performance, rechts neben Band. Bei einer neuen Analyse aus: Empfangs-SNR wie gemeldet. Ein: anhand gemeldeter Sendeleistung auf 30 dBm (1 W) normieren. Dies ist eine wissenschaftliche Einstellung und erfordert einen neuen Analyselauf. Ältere Einstellungen ohne das Feld behalten Ein. RX Performance und Benchmark bleiben normiert. |
| **Startdatum / Enddatum und Startzeit / Endzeit (UTC)** | Standardwert: 24 Stunden bis zur aktuellen UTC-Minute. Datumsangaben sind ab 2008 möglich; ein Analyselauf darf höchstens **31 verstrichene Tage** umfassen. Zeitangaben behalten Minutengenauigkeit. |

Neue TX-Performance-Analysen verwenden standardmäßig das ursprünglich gemeldete SNR. Gespeicherte TX-Performance-Konfigurationen und Links erhalten den booleschen Wert `tx_snr_normalization_to_30dbm` ausdrücklich: In Konfigurationen steht er unter `core_parameters.tx_snr_normalization_to_30dbm`; der URL-Parameter trägt denselben Feldnamen.

Fehlt das Feld in einer älteren Konfiguration, einem Link oder einem Datensatz eines abgeschlossenen Laufs, bleibt die Normierung eingeschaltet und die frühere Interpretation erhalten. Ausdrückliche true-/false-Auswahlen bleiben beim Speichern, Teilen, Laden und Wiederherstellen abgeschlossener Läufe erhalten.

Die Einstellung ist nur bei TX Performance aktiv; sie ändert RX Performance und Benchmark nicht. Ein Wechsel der wissenschaftlichen Bezugsgröße erfordert einen neuen Analyselauf mit getrennt gekennzeichneten Beobachtungsdaten und Zwischenspeichern für die jeweilige Bezugsgröße. Ein geladener älterer Lauf wird nicht stillschweigend als ursprüngliches SNR neu interpretiert.

Ein vierstelliger <strong class="defined-term">Maidenhead-Locator</strong> (Grid-4) bezeichnet ein Feld des Locatorrasters; sechs Zeichen bezeichnen ein kleineres Unterfeld.

In der geführten und der kompakten Eingabe beginnt die automatische Standortsuche erst nach **Analyse starten**. Sie verwendet das gewählte Rufzeichen, die RX-/TX-Richtung, das Band und den UTC-Messzeitraum. Performance ermittelt den Target-Standort; Benchmark fragt Target und Referenz gemeinsam ab, wenn einer der erforderlichen Standorte fehlt. Ein einzelner gültiger Target-Locator wird automatisch gewählt. Bei mehreren vollständigen Target-Locatoren wählst du selbst, auch bei unterschiedlichen Locatoren mit sechs Zeichen innerhalb desselben Grid-4; ein gewählter Locator mit sechs Zeichen wird nicht gekürzt. Für die Referenz werden Grid-4-Felder zur Auswahl angeboten und die vollständig gemeldeten Varianten angezeigt. Nach der Standortauswahl wird mit den vorhandenen Suchergebnissen fortgefahren, ohne die Standortsuche zu wiederholen. Wird kein gültiger Standort gefunden, gib einen unabhängig bekannten Locator ein oder passe die Einstellungen an. Manuell eingegebene Locatoren bleiben maßgeblich; sind alle erforderlichen Locatoren angegeben, entfällt die Standortsuche. Ein gemeldeter Locator bezeichnet eine Rasterzelle, keine verifizierte Antennenposition.

<a id="sec-5-3"></a>

#### 10.3 Einstellungen für den Benchmark-Vergleich

| Bedienelement | Deine Eingabe |
|---|---|
| **Referenz-Rufzeichen** | Gib das Referenz-Rufzeichen genau so ein, wie es gemeldet wird. Es muss sich vom Target-Rufzeichen unterscheiden. Reference Neighborhood wird nicht mehr unterstützt. |
| **Referenz-Locator (optional)** | Lass das Feld leer, um den Standort nach **Analyse starten** aus Empfangsberichten zu ermitteln, oder gib einen unabhängig bekannten Grid-4-Locator ein. Im leeren Feld steht `>auto-discover<`. Wird genau ein Locatorfeld gefunden, wird es automatisch übernommen; bei mehreren musst du wählen. Ein bekannter Standort belegt keinen Betrieb. |
| **SNR-Korrektur der Referenz** | Der Standardwert **Keine Korrektur** verwendet **0.0 dB**. Wähle **Dokumentierte Korrektur verwenden** nur für einen bestimmten Offset, der für diesen Aufbau gültig ist. Das Feld mit Vorzeichen akzeptiert **−99.9 bis +99.9 dB**; ein leeres Feld bedeutet **0.0**. Verwende einen Dezimalpunkt. Ein dokumentierter Nullwert bleibt etwas anderes als eine nicht bestimmte Korrektur. |

**Benchmark-Bestätigung:** Der Start jedes Benchmarks erfordert **Ich habe den gemeinsamen Betrieb bestätigt oder akzeptiere die Einschränkungen, wenn er nicht verifiziert ist.** Prüfe den gemeinsamen Betrieb wie in [Abschnitt 1.2](#sec-2-2) beschrieben; wenn er nicht verifiziert ist, interpretiere die Beobachtungen innerhalb der genannten Einschränkungen. Änderungen an Stationsidentitäten, Analyserichtung oder Band löschen die Bestätigung. Eine Änderung des Zeitraums löscht sie ebenfalls, außer bei einem geeigneten, an WSPR-Zyklen ausgerichteten Teilzeitraum des abgeschlossenen Laufs mit unveränderten Abrufeinstellungen. In diesem Fall bleiben der gewählte Referenzstandort und die bestehende Bestätigung erhalten. Ein neuer Analyselauf ist weiterhin erforderlich. Das Laden einer eigenen Konfiguration oder eines gewöhnlichen Analyselinks erfordert eine neue Bestätigung; eine gespeicherte Bestätigung belegt keinen Betrieb.

Dieselbe Bestätigung gilt für **historische Beobachtungen**, einschließlich Milazzo; es gibt keinen separaten historischen Modus. Gewöhnliche Analyselinks erfordern eine neue Bestätigung, auch bei dem wirkungslosen Parameter `run=1`. Das Öffnen eines Links startet niemals eine Analyse. Integrierte Demos wählen diese Bestätigung vor; ihre Versuchsnotizen erläutern bekannte Betriebsbedingungen und Unsicherheiten. Ein Link, der eine installierte Demo auswählt, öffnet mit dieser Demo direkt die Prüfung und behält deine gewählte Ansicht **Geführt** oder **Kompakt** bei; eine neue Sitzung beginnt standardmäßig mit **Geführt**. In der geführten Ansicht bleiben ihre Versuchsnotizen im eingeklappten Bereich **00 Demo mit Anleitung** verfügbar. Diese Abkürzung gilt nicht für gewöhnliche URLs mit geteilten Einstellungen, die weiterhin eine neue Benchmark-Bestätigung erfordern. Das bloße Laden einer Demo startet weiterhin keine Analyse.

##### Vorzeichen der SNR-Korrektur auf der Referenzseite

Eine **positive Korrektur erhöht das Referenz-SNR und verringert ΔSNR**. Hat eine Kalibrierung mit gemeinsamem Eingangssignal für Target minus Referenz **+1.6 dB** ergeben, gib **+1.6 dB** ein. Die Korrektur verändert weder Dekodierzahlen noch die kumulativen Kurven des unveränderten gemeldeten SNR. Verwende **Keine Korrektur**, wenn du eine Vergleichsbasis bestimmen möchtest; WSPRadar ermittelt keinen Offset automatisch. [Kapitel 6](#sec-reference-snr-calibration) beschreibt die Kalibrierung und ihre Grenzen.

<a id="sec-5-4"></a>

#### 10.4 Filter und Anforderungen an die Datengrundlage

Die unter **Optionale Filter, Analyseumfang und Datengrundlage** angezeigten Werte gelten auch dann, wenn du diesen Bereich nicht anfasst. Die Tabelle nennt die Standardwerte für einen neuen Aufbau; Demos und geladene Konfigurationen verwenden ihre gespeicherten Werte. Lege vor einem Versuch zur Bestätigung eines Ergebnisses fest, welche Stationen und Mindestanforderungen gelten sollen.

Für ΔDecode ist ein <strong class="defined-term">beobachtetes Ereignis</strong> eine Gegenstation in einem WSPR-Zyklus mit mindestens einem berücksichtigten Empfangsbericht für Target oder Referenz. Dabei unterscheidet WSPRadar weiterhin nach Rufzeichen und vollständigem gemeldetem Locator. Ein Ereignis mit Spot-Paar zählt für die Anforderung an die Datengrundlage **einmal**.

| Bedienelement | Standardwert / Bereich | Wirkung |
|---|---|---|
| **Rufzeichen mit Q, 0 oder 1 am Anfang ausschließen** | Performance **ein**; Benchmark **aus** | Schließt Gegenstationsrufzeichen aus, die mit `Q`, `0` oder `1` beginnen: Sender bei RX, Empfänger bei TX. Target und Referenz sind ausgenommen. Ein Präfix allein kennzeichnet keine Telemetrie. |
| **Bewegliche Stationen ausschließen** | Performance **ein**; Benchmark **aus** | Schließt Gegenstationsrufzeichen aus, die in den ansonsten zulässigen weltweiten Empfangsberichten in mehr als einem Grid-4 gemeldet wurden, **vor der Entfernungsfilterung**. Das kann auf Bewegung oder fehlerhafte Metadaten zurückgehen. |
| **Sonnenstand am Target-QTH** | **Alle Tageszeiten** | Berücksichtigt alle Zyklen, Tageslicht oberhalb von **+6°**, Nacht unterhalb von **−6°** oder Greyline zwischen diesen Sonnenhöhen am Target. |
| **Maximale Entfernung der Gegenstationen vom Target (km)** | **Weltweit (≈20 015 km)**; Auswahl 2 500 / 5 000 / 10 000 / 15 000 km / Weltweit | Numerische Grenzen entfernen Gegenstationen **an oder jenseits** der Grenze aus der analysierten Population und den Exporten; Weltweit behält alle geografischen Standorte bei. Das verändert die Analyse, nicht nur die Kartenansicht. Eine geladene Grenze von 20 000 km bleibt verfügbar, solange sie ausgewählt ist, und behält ihre ursprüngliche Bedeutung. |
| **Mindestzahl bestätigter Empfangsgelegenheiten je Station** | **1**; 1–50 | Performance: Jede Station benötigt mindestens diese Anzahl erfolgreicher Dekodierungen plus bestätigter nicht dekodierter Gelegenheiten. Niedrigere Werte ergeben gröber abgestufte Quoten auf Grundlage weniger Beobachtungen. Für Stationen mit wenigen Empfangsgelegenheiten gilt zusätzlich der serverseitig konfigurierte Filter zur Bestätigung durch weitere Empfänger; siehe [Abschnitt 8.3.1](#sec-7-performance-opportunities). |
| **Mindestzahl qualifizierter Stationen je Kartensegment** | **5**; 1–25 | Performance: Ab dieser Mindestzahl zeigt ein Segment die Farbe seiner Dekodierquote, auch bei 0 %. Ein Segment mit mindestens einer qualifizierten Station unterhalb der Mindestzahl ist grau schraffiert. Ein Segment ohne qualifizierte Stationen bleibt ungefärbt. |
| **Mindestzahl qualifizierter Stationen je Segment für ΔSNR** | **3**; 1–50 | Mindestzahl der Stationen, die nach Anwendung der geltenden Anforderungen mindestens ein nutzbares Spot-Paar zum Segment beitragen. Zusätzlich benötigt ein Segment ein verfügbares, nicht entartetes Konfidenzintervall über alle Paare innerhalb der maximalen Halbbreite. |
| **Gemeinsames Konfidenzniveau** | **95%**; 70%, 80%, 90%, 95%, 99% | Bei Benchmark steuert eine gemeinsame Einstellung die Mittelwertintervalle der Karte und der Segmentdetails: zusammengefasste Kartenpaare, einzelne Stationen, zusammengefasste Spots, zeitliche Intervalle und Tageszeitintervalle sowie das bestehende Aggregat mit gleicher Stationsgewichtung. Ein höheres Konfidenzniveau verbreitert bei denselben Daten das Intervall, sofern die beitragenden Werte streuen, und kann die Kartenqualifikation ändern; es ändert weder beitragende Beobachtungen noch Mittelwerte. Bei Performance steuert es chronologische und nach Tageszeit zusammengefasste SNR-Mittelwert-KIs auf Segment- und Einzelstationsebene, ohne Kartenqualifikation, Anzahlen, Mittelwerte oder die Median-/IQR-Ansicht zu ändern. Gültige benutzerdefinierte importierte Niveaus bleiben erhalten. |
| **Maximales ΔSNR-Karten-KI (± dB)** | **0,5**; endlicher positiver Wert | Editierbare numerische Karteneinstellung: 0,5 bedeutet ein Intervall höchstens **Mittelwert ±0,5 dB**. Für eine Färbung darf die ungerundete Halbbreite des Konfidenzintervalls über alle Paare diesen Wert nicht überschreiten. Die Stationsanzahlanforderung gilt weiterhin. |
| **Mindestzahl beobachteter Stationen je Segment für ΔDecode** | **3**; 1–50 | Zählt unterschiedliche Identitäten aus Rufzeichen und vollständigem gemeldetem Locator mit mindestens einem beibehaltenen Ereignis im Segment, einschließlich einseitiger Identitäten. Die Anforderung an den Anteil beobachteter Ereignisse muss ebenfalls erfüllt sein. |
| **Mindestanteil beobachteter Ereignisse je Segment für ΔDecode (%)** | **1 %**; 0–5 %, Schritte von 0.5 % | Benchmark: Verlangt diesen Anteil der beobachteten Ereignisse des gesamten gefilterten Analyselaufs, aufgerundet auf ein ganzes Ereignis. Bei **0 %** erfüllt jedes nicht leere Segment diese Anforderung; die Mindestzahl beobachteter Stationen gilt weiterhin. |

**Für die Benchmark-ΔSNR-Karte** beträgt die Mindestzahl standardmäßig **drei Stationen**, mit Bereich **1–50**. Eine Färbung erfordert zusätzlich ein verfügbares, nicht entartetes Konfidenzintervall über alle Paare beim gemeinsamen Konfidenzniveau, standardmäßig **95%**, mit ungerundeter Halbbreite von standardmäßig höchstens **0,5 dB**. Eine Halbbreite von **0,5004 dB überschreitet eine Grenze von 0,5 dB**, auch wenn eine Anzeige auf 0,50 rundet. Die Halbbreiteneinstellung ändert nur Kartenqualifikation und Schattierung; das Konfidenzniveau steuert auch die bestehenden Mittelwertintervalle. Keine der beiden Einstellungen entfernt geeignete Beobachtungen aus den Segmentdetails. Die kompakte Zusammenfassung lautet bei den Standardwerten **KI ± 0.5 dB** und **Gemeinsames Konfidenzniveau: 95%**; beide Werte folgen den aktuellen Einstellungen.

Der Nenner für die ΔDecode-Anforderung bezieht sich weiterhin auf den gesamten Analyselauf, wenn du einen Ausschnitt oder ein Segment auswählst. ΔDecode hat keine zusätzliche Ereignismindestzahl je Station und verwendet nicht die Stationsqualifikation für ΔSNR. Die Mindestzahl beobachteter Stationen und die Anforderung an den Ereignisanteil gelten gemeinsam. Diese Anforderungen sichern eine Mindestzahl verschiedener Stationen und Beobachtungen; sie sind kein Maß für statistische Sicherheit.

Die **ΔSNR-Mindestanforderungen an die Datengrundlage** und **ΔDecode-Mindestanforderungen an die Datengrundlage** stehen bei ausreichender Bildschirmbreite nebeneinander; jeder Abschnitt beginnt mit seiner Stationsmindestzahl. Auf schmalen Bildschirmen stehen sie untereinander. **Experteneinstellungen** folgt diesen Anforderungen und enthält **Mögliche ΔSNR-Ausreißer erkennen** sowie die zugehörigen optionalen Bedienelemente.

Benchmark-Segmente mit beobachteten Daten unterhalb des jeweiligen Schwellenwerts werden grau schraffiert; die berücksichtigten Stationsbeobachtungen bleiben verfügbar. Die Anforderung gepaarter Beobachtungen für ΔSNR entfernt keine Dekodierungen aus ΔDecode. Bei Performance können Beobachtungen außerhalb der Entfernungsgrenze weiterhin die Aktivität des Targets belegen, ohne diese Gegenstationen zur analysierten Population hinzuzufügen.

Sobald du einen der beiden Ausschlussfilter manuell änderst, bleibt diese Auswahl bei einem Wechsel der Fragestellung erhalten. Gespeicherte Konfigurationen, Demos und Analyselinks behalten ebenfalls ihre ausdrücklich festgelegten Ausschlüsse bei.

<a id="sec-5-5"></a>

#### 10.5 Bedienelemente für Karte, Segmentdetails und Export

Mit diesen Bedienelementen untersuchst du die abgeschlossene Analyse. Welche Beobachtungen zählen, bleibt dabei unverändert:

| Bedienelement | Geltungsbereich und Speicherung |
|---|---|
| **Segmententfernung und -richtung** | Ändert die Statistiken und Zeitansichten der Segmentdetails. Die Stationsauswertung folgt diesem Ausschnitt nur bei aktiviertem optionalem Segment- und Entfernungsfilter; Stationskennzahlen und ausgewählte Beobachtungsdaten behalten den vollständigen Lauf bei. Wird für Performance und Benchmark getrennt gespeichert. |
| **Nach ausgewähltem Segment und Entfernung filtern** | Beschränkt auf Wunsch die Performance- oder Benchmark-Stationsliste; andernfalls umfasst sie alle Richtungen und Entfernungen. Die Daten ausgewählter Stationen beziehen sich weiterhin auf den gesamten Analyselauf. Er steht links neben dem Schalter für Stationen ohne Target-Dekodierungen beziehungsweise einseitige Beobachtungen. Er gilt nur für die Sitzung und wird nicht in Konfigurationen oder geteilten Links gespeichert. |
| **Stationsauswertung → Filter** | Beschränkt die Stationsliste und die exportierte Tabelle, nicht die Karten oder Statistiken der Segmentdetails. Spaltenfilter werden gespeichert; eine Station muss jede aktive Bedingung erfüllen. Innerhalb eines Rufzeichen- oder Locatorfilters genügt dagegen die Übereinstimmung mit einem der ausgewählten Werte. |
| **Nur von anderen Stationen dekodiert. / Nur andere Signale dekodiert.** | Zeigt Performance-Stationen mit bestätigten Empfangsgelegenheiten, aber ohne erfolgreiche Dekodierung. Diese Sichtbarkeitsoption wird gespeichert. |
| **Einseitige Beobachtungen einbeziehen** | Zeigt Benchmark-Stationen ohne Spot-Paare und einseitige Beobachtungen in den Detaildaten. Diese gespeicherte Sichtbarkeitsoption verändert weder die Gesamtzahlen der Abdeckung noch die Qualifikation. |
| **Ausgewählte Stationszeile** | Speichert die exakte Auswahl aus Rufzeichen und Locator: normalerweise eine je Ergebnistyp; bei aktiviertem Ausreißerbericht werden mehrere Benchmark-Identitäten unterstützt. |
| **Zeitliche Zusammenfassung** | Ändert die Zeitintervalle der chronologischen Darstellung; die Auswahl für die Segmentdetails und für ausgewählte Stationen wird getrennt gespeichert. Paarbildung, Empfangsgelegenheiten und feste einstündige Tageszeitprofile bleiben unverändert. |
| **Zeitbasis** | Wählt UTC oder wahre Ortszeit unabhängig für Segment- und Einzelstationsdiagramme; neue Analysen verwenden auf beiden Ebenen standardmäßig UTC. Jede Auswahl gilt für die chronologischen und nach Tageszeit zusammengefassten SNR-, Dekodier- und Abdeckungsansichten dieser Ebene; fokussierte Diagramme folgen der Einzelstationsauswahl. Beide Einstellungen werden in Konfigurationen, geteilten Analyselinks und Exportmetadaten gespeichert. Der Wechsel ändert die dargestellte chronologische Zeit; UTC-Intervalle und ihre statistischen Werte bleiben erhalten. Für die Tageszeitprofile werden Beobachtungen vor der stündlichen Zusammenfassung neu gruppiert. Statistiken des gesamten Laufs bleiben unverändert. |
| **ΔSNR-Statistik: Median / Mittelwert** | Ändert ausschließlich die statistische Größe und das zugehörige Intervall zeitlicher Benchmark-ΔSNR-Ansichten. **Mittelwert** ist der Standard für neue Analysen. Segment- und Einzelstationsdiagramme speichern die Auswahl unabhängig voneinander. Wenn eine aktuelle Konfiguration eine Statistik nicht angibt, verwendet diese Ebene standardmäßig Mittelwert; ausdrücklich gespeicherte Werte werden beachtet. Die Milazzo-Demo startet auf beiden Ebenen mit Median. Median zeigt den Median mit Bin IQR; Mittelwert zeigt das arithmetische Mittel mit verfügbarem punktweisem Konfidenzintervall zum eingestellten Konfidenzniveau. Beide Modi erhalten zulässige Beobachtungen, Intervalle und Paargewichtung. Beide Einstellungen werden in Konfigurationen, geteilten Analyselinks und Exportmetadaten gespeichert. Feste Benchmark-Statistik, Karten, ΔDecode und Anzahlen der Datengrundlage bleiben unverändert. |
| **Beibehaltene Einstellung für Performance-SNR-Markierungen** | Das optionale, nur für Performance geltende `results_view.performance_snr_statistic` akzeptiert weiterhin `mean` oder `median` und verwendet ohne Angabe `mean`. Konfigurationen und geteilte Links erhalten diese Kompatibilitätseinstellung. Diese Einstellung wurde für das frühere Histogramm des SNR erfolgreicher Dekodierungen verwendet. Die aktuelle Auswahl in **Spot- und Stationsdekodierungen** verwendet die unabhängige Einstellung darunter. |
| **Spot- und Stationsdekodierungen → Zusammenfassende Statistik (Performance)** | Wählt **Mittelwert** oder **Median** für die fünf SNR-Markierungen und die Mittelwerte oder Mediane der Stationsdekodierquoten unten rechts, je Klasse und über „All SNR“, sowie die entsprechenden Kennwerte in der Karte Stationen. Häufigkeitskategorien, Anzahlen, Spot-Dekodierquote und Anteil erfasster Gegenstationen bleiben fest. Das optionale, nur für Performance geltende `results_view.performance_snr_reach_statistic` akzeptiert `mean` oder `median`, unabhängig von den zeitlichen Einstellungen. Ohne Angabe gilt `mean`. Konfigurationen, geteilte Links, wiederhergestellte abgeschlossene Läufe und Exporte erhalten die Auswahl. |
| **SNR-Statistik: Median / Mittelwert** | Zeitliche Performance-SNR-Ansichten auf beiden unabhängig einstellbaren Ebenen, standardmäßig Mittelwert. Chronologische und Tageszeitansichten fassen einzelne erfolgreiche Beobachtungen unmittelbar zusammen. Absolutes SNR behält diese Werte; Segmentabweichungen ziehen den gewählten Laufmittelwert oder Laufmedian jeder Station ab, bevor einzelne Abweichungen zusammengefasst werden. Mittelwert zeigt sein eingestelltes punktweises Konfidenzintervall (KI); Median zeigt IQR. Die absolute Dichte bleibt beim Wechsel unverändert; die Abweichungsdichte kann sich mit ihrem Vergleichsniveau ändern. Gespeicherte Konfigurationen, geteilte Links, wiederhergestellte abgeschlossene Läufe und Exporte erhalten die Auswahl. Dekodierquoten, Anzahlen, Kartenqualifikation, die SNR-Klassen-Zusammenfassung und feste Mediane der Stationstabelle bleiben unverändert. |
| **Zoom-Zeitfenster / <strong class="defined-term">Möglicher Ausreißer im Detail</strong>** | Beschränkt die Detaildaten für genau eine ausgewählte Station auf ein Zeitintervall. **Tabelle filtern** grenzt anschließend die angezeigten Zeilen und die exportierte Detailtabelle der Auswahl ein. Die Detaildiagramme verwenden das gesamte Zoom-Zeitfenster. Die Fokussierung und Tabellenfilter der Detaildaten werden weder in Konfigurationen noch in Analyselinks gespeichert. |

**Gespeicherte Konfidenzeinstellungen.** Die folgenden Felder sind hilfreich, wenn du Konfigurationen, geteilte Links oder Exporte prüfst.

Diese Einstellungen werden unter `advanced_parameters` gespeichert und in geteilten Analyselinks sowie Exportmetadaten erhalten. Die unabhängigen Einstellungen `segment_temporal_statistic` und `station_temporal_statistic` bleiben unter `results_view`. `evidence_confidence_level_percent` ist standardmäßig `95` und muss strikt zwischen 0 und 100 liegen. Das zugehörige interne `ci_alpha = 1 − evidence_confidence_level_percent / 100` bezeichnet die gesamte zweiseitige Randwahrscheinlichkeit und muss strikt zwischen 0 und 1 liegen; das Konfidenzniveau ist `100 × (1 − ci_alpha)%`. `evidence_confidence_interval_method` ist standardmäßig `iid_student_t`. Bei Benchmark steuert dieselbe Konfidenzkonfiguration einzelne Stationsmittelwerte, Mittelwerte über zusammengefasste qualifizierte Paare, zeitliche Intervalle und Tageszeitintervalle, Mittelwerte über Kartenpaare und das bestehende Aggregat mit gleicher Stationsgewichtung für den gewählten Bereich der Segmentdetails. Jedes Intervall verwendet seine eigene beitragende Einheit und Stichprobenstandardabweichung: Paare für die Karte und zusammengefasste Spots, Stationsmittelwerte für das Aggregat Stationen. Die berechneten statistischen Größen und die einbezogenen Beobachtungen der Benchmark-Statistik bleiben unverändert. Die Karte hat zusätzlich eine eigene maximale KI-Halbbreite; diese Grenze filtert die Bereichsstatistiken der Segmentdetails nicht. Berechnung und Annahmen stehen in [Abschnitt 8.5.1](#sec-7-dependence-bias).

Bei Performance steuern dieselben gespeicherten Konfidenzfelder die oben beschriebenen absoluten zeitlichen Mittelwerte und Segmentabweichungsmittelwerte; jede Ansicht verwendet einzelne beitragende erfolgreiche Beobachtungen oder Abweichungen. Eine nicht angegebene zeitliche Statistik verwendet auf jeder Ebene unabhängig Mittelwert; fehlende Konfidenzfelder verwenden 95% und `iid_student_t`. Ausdrücklich angegebene gültige Werte werden beachtet. Diese Einstellungen ändern die Zusammenfassungen und deren Darstellung. Die Abfrage der Quelldaten und die Auswahl der einbezogenen Beobachtungen bleiben gleich. Performance erhält keine Benchmark-Kartenanforderung an die KI-Halbbreite.

Gespeicherte Konfigurationen verwenden für die gemeinsame Konfidenzeinstellung `advanced_parameters.evidence_confidence_level_percent` und `advanced_parameters.evidence_confidence_interval_method`; das interne `ci_alpha` bleibt die zugehörige gesamte zweiseitige Randwahrscheinlichkeit. Die KI-Grenze der Karte steht unter `advanced_parameters.evidence_max_segment_ci_half_width_db`. Gespeicherte Konfigurationen erhalten die wirksamen Stationsmindestzahlen, das gemeinsame Konfidenzniveau und die KI-Grenze der Karte. Eine nicht angegebene Halbbreite verwendet den Standardwert **0,5 dB**; ein ausdrücklich angegebener Wert muss endlich und strikt positiv sein. Ungültige Werte müssen korrigiert werden und werden nicht stillschweigend ersetzt.

**ΔDecode-Konfiguration:** Benchmark-Konfigurationsdokumente verlangen ausdrücklich `settings.advanced_parameters.evidence_min_decode_stations_per_segment` neben `settings.advanced_parameters.evidence_min_decode_event_share_percent`. Die Stationsmindestzahl ist eine ganze Zahl von **1 bis 50**; neue Analysen verwenden standardmäßig **3**. Die vorhandenen installierten Benchmark-Demos verwenden ausdrücklich **1**, um ihre geprüfte Färbung zu erhalten. Ältere Benchmark-Konfigurationsdokumente ohne das Pflichtfeld werden abgewiesen, statt ihnen stillschweigend eine neue Kartenanforderung zuzuweisen. Geteilte Links verwenden `min_decode_stations_per_segment` für diese gesonderte ΔDecode-Einstellung.

Geteilte Links schreiben die wirksame Benchmark-Stationsmindestzahl ausdrücklich mit. Ein Link mit nicht auflösbaren, ausgemusterten oder ungültigen optionalen Parametern stellt seine erkannten gültigen Einstellungen wieder her und nennt die Parameternamen, die vor dem Start manuell ausgewählt werden müssen. Ausgemusterte Namen sind keine Aliasse und werden nicht stillschweigend migriert. Ungültige oder mehrdeutige erforderliche Identitäts-, Vergleichsdesign- oder Zeiteinstellungen verhindern das Laden. Links laden nur Einstellungen; sie erteilen keine Freigabe für einen neuen Analyselauf.

Die verfügbaren chronologischen Zeitintervalle hängen von der **Dauer des gesamten Analyselaufs** ab. Eine gültige gespeicherte Auswahl hat Vorrang vor dem Standardwert und bleibt auch dann verfügbar, wenn sie nicht zu den unten genannten üblichen Optionen gehört:

| Dauer des Analyselaufs | Übliche Zeitintervalle | Standardwert |
|---|---|---|
| Bis zu 6 Stunden | 2m, 10m, 30m, 1h, 2h, 3h, 6h | **10m** |
| Mehr als 6 bis einschließlich 24 Stunden | 2m, 10m, 30m, 1h, 2h, 3h, 6h | **30m** |
| Mehr als 24 Stunden bis einschließlich 7 Tage | 30m, 1h, 2h, 3h, 6h, 12h, 24h | **12h** |
| Mehr als 7 Tage | 1h, 2h, 3h, 6h, 12h, 24h | **12h** |

Der manuelle Zoom bietet **Aus** sowie die Zeitfenster **1h**, **3h**, **6h**, **12h** oder **24h**, soweit sie in den abgeschlossenen Analyselauf passen. Wähle einen UTC-Mittelpunkt oder verschiebe ihn mit **Früher / Später**. Die Detailansicht eines möglichen Ausreißers umfasst das Ereignis und die umgebenden Daten für das lokale Vergleichsniveau und kann über 24 Stunden hinausgehen. Der Export kann separate Abbildungen dieses Ausschnitts enthalten; [Abschnitt 9.4](#sec-8-4) definiert deren Umfang.

<a id="sec-5-6"></a>

#### 10.6 Bedienelemente für die Ausreißererkennung in Benchmark

Unter **Experteneinstellungen** ist **Mögliche ΔSNR-Ausreißer erkennen** standardmäßig ausgeschaltet. Aktiviere die Option nur, wenn du vorübergehende Abweichungen in den gepaarten Beobachtungen untersuchst; siehe [Abschnitt 2.5](#sec-outlier).

| Bedienelement | Standardwert / Bereich | Wirkung |
|---|---|---|
| **Mindestbetrag der ΔSNR-Abweichung (dB)** | **6.0**; 0.1–100.0 dB | Verlangt eine ausreichend große Änderung gegenüber dem lokalen Vergleichsniveau des Funkpfads. |
| **Mindestwert des robusten z-Scores** | **3.0**; 0.1–100.0 | Verlangt zusätzlich, dass die Änderung gegenüber den Schwankungen in der zeitlichen Umgebung groß ist; verwendet wird der Betrag des robusten Scores. Dieser Score ist keine Wahrscheinlichkeit. |
| **Maximale Differenz der Vergleichsniveaus vor und nach dem Ereignis (dB)** | **3.0**; 0.1–100.0 dB | Verlangt, dass die Mediane des Vergleichsniveaus vor und nach dem möglichen Ausreißer höchstens um diesen Betrag voneinander abweichen. Eine geringe Streuung des Hintergrunds ist damit nicht gefordert. |

Alle drei Anforderungen und die Prüfungen des Detektors auf eine ausreichende Datengrundlage gelten für jede Ereignisdauer. Wenn du einen Mindestwert senkst oder die zulässige Differenz der Vergleichsniveaus erhöhst, werden mehr Fälle für den Bericht zugelassen. Änderungen der Detektoreinstellungen erfordern einen neuen **Analyselauf**; die Erkennung ist unabhängig von der Breite der dargestellten Zeitintervalle und verändert die gewöhnlichen Benchmark-Karten nicht. [Abschnitt 8.6](#sec-7-outliers) beschreibt das Verfahren und seine Grenzen im Einzelnen.

<a id="sec-6"></a>
<a id="sec-5-7"></a>

### 11. Fehlersuche und Datenqualität

Beginne bei den Analyseeinstellungen. Niedrigere Schwellenwerte können ein falsches Rufzeichen oder einen falschen Locator, ein falsches Band, einen falschen Messzeitraum oder einen ungeeigneten Sendezeitplan nicht ausgleichen.

<a id="sec-6-1"></a>

#### 11.1 Zuerst die Definition des Analyselaufs prüfen

Prüfe das genaue **Target-Rufzeichen und das QTH**, das **Band** und den **UTC-Messzeitraum**, anschließend den tatsächlichen Betrieb und die hochgeladenen Empfangsberichte. Prüfe bei Benchmark außerdem die Referenzidentität, gemeinsame Betriebszeiten, synchronisierte Uhren und bei TX die [Sendezeitpläne und den Frequenzabstand](#sec-simultaneous-tx-setup-2). Überprüfe die Signalführung sowie tatsächliche und gemeldete Leistung, bevor du einen unerwarteten Unterschied interpretierst.

<a id="sec-6-2"></a>

#### 11.2 Diagnose anhand des Symptoms

Beziehe Hinweise auf die Einstellungen des **abgeschlossenen Analyselaufs**. Eine beobachtete Anzahl ist etwas anderes als eine geforderte Mindestzahl: Drei beobachtete Empfangsgelegenheiten erfüllen keine Anforderung von fünf Empfangsgelegenheiten.

| Symptom | Was du prüfen oder tun solltest |
|---|---|
| **Keine Target-Daten beziehungsweise keine Daten aus der Quelle zurückgegeben** | Prüfe Identität, Locator, Band, UTC-Messzeitraum und hochgeladene Empfangsberichte in der ausgewählten Datenbank. Sieh dir die [historische Modusfilterung](#sec-6-4) an. Niedrigere Anforderungen an die Datengrundlage können keine Empfangsberichte in der Quelle erzeugen. |
| **Empfangsberichte wurden zurückgegeben, aber keiner bleibt übrig** | Prüfe Stationsausschlüsse, Sonnenstand und maximale Entfernung der Gegenstationen. Diese können die abgerufene Population vollständig entfernen. |
| **Keine Station erfüllt die Performance-Anforderungen** | Vergleiche die bestätigten Empfangsgelegenheiten jeder Station mit der geforderten Mindestzahl. Prüfe die Filter sowie die Empfangsberichte, mit denen die Aktivität von Sender und Empfänger festgestellt wird. Unbekannte Aktivität zählt nicht als bestätigte nicht dekodierte Gelegenheit. |
| **Performance-Stationen vorhanden, aber kein Kartensegment ist eingefärbt** | Vergleiche die Zahl berücksichtigter Stationen im Segment mit der geforderten Mindestzahl. Graue Schraffur (**Not qualifying**, Anforderungen nicht erfüllt) bedeutet: Mindestens eine Station erfüllt die Stationsanforderungen, aber für eine Färbung sind es zu wenige. Ein ungefülltes Segment (**No observations**, keine berücksichtigten Beobachtungen) enthält nach diesen Anforderungen keine Station für die Karte. Eine gültige Dekodierquote von 0 % wird farbig dargestellt. Schraffur und ungefüllte Segmente belegen nicht, dass kein Empfang stattfand. |
| **Benchmark-ΔSNR fehlt oder ist schraffiert** | Prüfe, ob dieselben Gegenstationsidentitäten in denselben Zyklen vorliegen, sowie gemeinsamen Betrieb und synchronisierte Sendezeitpläne. Prüfe anschließend die Stationsqualifikation anhand der Spot-Paare und die Anzahl beitragender Stationen im Segment. Wähle das exakte Segment in **Segmentdetails** und vergleiche den zusammengefassten **Spots**-Mittelwert mit ± Halbbreite im separaten Abschnitt **Benchmark-Statistik** mit dem gewählten KI-±-Grenzwert. Der Intervallstatus mit voller Genauigkeit und der Qualifikationsgrund stehen in `benchmark/map_segments.parquet`. Ein Konfidenzintervall kann nicht verfügbar, entartet oder breiter als die gewählte Grenze sein. Bei mindestens zwei beitragenden Paaren ergibt eine Varianz von genau null über deren Differenzen ein entartetes Intervall, und das Segment bleibt schraffiert; gleiche Stationsmittelwerte allein bedeuten keine Paarvarianz von null. Prüfe Funkpfade und datierte Beobachtungen, bevor du die Anforderungen änderst. Einseitige Beobachtungen können weiterhin ΔDecode stützen, und geeignete Beobachtungen in schraffierten Segmenten bleiben in den Bereichsstatistiken der Segmentdetails erhalten. |
| **ΔDecode ist trotz beobachteter Empfangsberichte schraffiert** | Prüfe die Mindestzahl beobachteter Stationen und vergleiche die Ereignisanzahl des Segments mit dem erforderlichen Ereignisanteil am gesamten Analyselauf. Beide Anforderungen müssen erfüllt sein. Ein kleinerer ausgewählter Bereich senkt die Anforderung an den Ereignisanteil nicht. |
| **Stationsliste unerwartet leer** | Lösche die Spaltenfilter der Stationsauswertung und prüfe die Sichtbarkeitsschalter. Prüfe bei Performance und Benchmark außerdem **Nach ausgewähltem Segment und Entfernung filtern**. |
| **Unerwartetes ΔSNR-Vorzeichen** | Prüfe die Zuordnung von Target und Referenz sowie der physischen Signalwege, das Korrekturvorzeichen und die Leistungsangaben. Vollziehe ein einzelnes Spot-Paar in den Detaildaten nach. |
| **Einseitige Empfangsberichte überwiegen oder kein Ausreißer wird gefunden** | Prüfe Betriebsprotokolle und die Datengrundlage aus Spot-Paaren vor, während und nach dem Intervall. Einseitige Empfangsberichte allein liefern kein ΔSNR; siehe [Aktivitätsbelege](#sec-6-5). |
| **Große Tabelle ohne Suche oder direkten CSV-Download** | Oberhalb von **150 000 angezeigten Zeilen** werden schreibgeschützte Tabellen beim Scrollen nachgeladen. Grenze die Detaildaten mit **Tabelle filtern** ein oder verwende die vorbereitete Ergebnis-ZIP-Datei. |
| **Analyselauf überschreitet die Zeilengrenze der Quelle, aktuelle Empfangsberichte fehlen oder eine Quelle fällt aus** | Folge den [Prüfschritten für Quelldaten](#sec-6-6). Eine kleinere Kartenentfernung verringert die Zahl der abgerufenen Zeilen nicht. |

<a id="sec-6-3"></a>

#### 11.3 Rufzeichen und Locator prüfen

Prüfe Identitäten in der **vom Analyselauf verwendeten Datenbank**, nicht nur auf der Karte einer anderen Website. Target und Referenz werden anhand des exakten Rufzeichens und des Grid-4-Locators ausgewählt; ein in `JN37` gemeldetes Target passt nicht zum konfigurierten `JN38`. Ein manuell eingegebener Kartenursprung des Targets wird niemals automatisch an die Empfangsberichte angepasst. Ein leeres Target-Locatorfeld veranlasst dagegen die Standortsuche vor der Analyse; die Genauigkeit des gewählten gemeldeten Locators bleibt erhalten.

Die gemeldeten Rufzeichenkennungen müssen 3–15 Zeichen lang sein; eingegebene Target-Locatoren müssen gültige vier- oder sechsstellige Maidenhead-Locatoren sein. Die Eingabe unter Referenz-Locator verwendet vier Zeichen. Beide Locatorfelder können für die Standortsuche nach **Analyse starten** leer bleiben; der erforderliche Standort muss feststehen, bevor die Analyse fortgesetzt wird. Eine gültige Schreibweise bestätigt weder Standort noch Betrieb. Gegenstationsidentitäten verwenden den **vollständigen gemeldeten Locator**. Verschiedene Locatorangaben können daher dieselbe physische Station in mehrere Identitäten aufteilen.

WSPRadar setzt weder zusammengesetzte Rufzeichen aus getrennten Nachrichten zusammen noch ergänzt es fehlende Locatorfelder in Datenbankberichten. Die automatische Standortsuche verwendet gültige Locatoren, die bereits in Empfangsberichten stehen. Siehe [Abschnitt 5.1](#sec-simultaneous-tx-setup-1), wenn eine TX-Identität fehlt oder unvollständig ist.

<a id="sec-6-4"></a>

#### 11.4 Ersatzabfrage für historische Dekodiercodes

WSPRadar fragt normalerweise <strong class="defined-term">WSPR-2</strong>, den Zweiminutenmodus, mit der Datenbankbedingung `code = 1` ab. Für einen Zeitraum **vollständig vor dem 1. Januar 2022, 00:00 UTC** wiederholt es die Abfrage ohne diese Bedingung, wenn die strenge Abfrage bei Performance keine Target-Daten aus der Quelle oder bei Benchmark für keinen der beiden Aufbauten Daten aus der Quelle findet. Bei einem Zeitraum, der genau an dieser Grenze oder später endet, bleibt der strenge Filter bestehen.

Diese historische <strong class="defined-term">Ersatzabfrage</strong> erweitert die Auswahl, weil ältere Modusangaben unvollständig oder mehrdeutig sein können <a href="#ref-10">[Ref-10]</a>. Der Status des Analyselaufs und das exportierte Feld `decode_filter_mode` zeigen die verwendete Auswahl; sie belegen nicht den tatsächlichen Funkmodus jedes historischen Empfangsberichts. Das Grenzdatum ist eine Kompatibilitätsregel, keine Zusicherung der Datenqualität.

<a id="sec-6-5"></a>

#### 11.5 Betriebsbedingungen und Aktivitätsbelege

**Benchmark** berücksichtigt zulässige gepaarte und einseitige Empfangsberichte, ohne in jedem Zyklus einen separaten Aktivitätsbeleg für das Target zu verlangen. Selbst ein vollständig nur auf einer Seite beobachteter Zeitraum bleibt als beschreibende Datengrundlage für Dekodierungen nutzbar, liefert aber kein ΔSNR. Ein einseitiges Intervall kann durch Empfang, Sendezeitpläne, Ausfälle oder fehlende Uploads entstehen; WSPRadar ermittelt seine Ursache nicht und entfernt es nicht automatisch. Prüfe Betriebsprotokolle und verwende einen dokumentierten gemeinsamen Betriebszeitraum.

**Performance** zählt jede erfolgreiche Dekodierung als ihre eigene bestätigte Empfangsgelegenheit. Eine nicht dekodierte Gelegenheit zählt nur, wenn Empfangsberichte die Aktivität von Sender und Empfänger auf demselben Band im selben Zyklus belegen; andernfalls bleibt das Ergebnis unbekannt. Die richtungsabhängigen Regeln stehen in [Abschnitt 8.3.1](#sec-7-performance-opportunities).

<a id="sec-6-6"></a>

#### 11.6 Mit Daten aus den Quellen arbeiten

Der <strong class="defined-term">Status des Analyselaufs</strong> nennt die verwendete Datenbank und eine etwaige historische Ersatzabfrage. Jeder Analyselauf verwendet eine Quelle; Empfangsberichte aus verschiedenen Datenbanken werden nicht kombiniert. WSPRadar kann für einen neuen Versuch die Quelle wechseln. Die Ermittlung des Referenzstandorts bindet die anschließende Analyse jedoch an diese Quelle. Fällt sie aus, beginne neu und prüfe den neu ermittelten Referenzstandort. Wenn WSPRadar den Referenzstandort für den Lauf ermittelt, stehen unter **Abgeschlossen** die Datenbank und der Filter der Standortsuche, der verwendete Referenzstandort und die dafür gemeldeten Locator.

Warte bei aktuellen Empfangsberichten etwa **fünf Minuten** nach dem letzten Zyklus und prüfe dann Uploads und Verfügbarkeit in der ausgewählten Datenbank. Das ist eine praktische Wartezeitschätzung, keine Zusicherung vollständiger Daten <a href="#ref-10">[Ref-10]</a>. Datenbanken können falsche Identitäten, Locator oder Leistungsangaben, verspätete Empfangsberichte und nachträgliche Korrekturen enthalten. Erneute Demoläufe können bereits abgerufene Daten wiederverwenden; ein erneuter Lauf übernimmt daher nicht zwangsläufig spätere Korrekturen.

Eine Anfrage mit mehr als **1 000 000 vollständigen Zeilen** wird abgewiesen und nicht stillschweigend gekürzt. Verkürze den UTC-Messzeitraum; **Rufzeichen mit Q, 0 oder 1 am Anfang ausschließen** kann die Datenmenge der Quellenabfragen verringern, sofern das zu deiner Fragestellung passt. Die Entfernungsgrenze greift **nach dem Abruf**. Eine kleinere Entfernung umgeht diese Grenze daher nicht.

<a id="sec-ref"></a>
<a id="part-v"></a>

## Teil V: Literatur und Quellen



* <a id="ref-1"></a><a href="https://arxiv.org/abs/2209.08989">[Ref-1]</a> **Preprint.** Zander, J. (2022). *Simple HF antenna efficiency comparisons using the WSPR system*. arXiv:2209.08989v1. doi:10.48550/arXiv.2209.08989. Insbesondere §IV zum Messmodell des gepaarten Vergleichs.

* <a id="ref-2"></a><a href="https://doi.org/10.1155/2022/4809313">[Ref-2]</a> **Wissenschaftlicher Fachartikel mit Peer-Review.** Vanhamel, J.; Machiels, W.; Lamy, H. (2022). *Using the WSPR Mode for Antenna Performance Evaluation and Propagation Assessment on the 160-m Band*. International Journal of Antennas and Propagation, 2022, 4809313. doi:10.1155/2022/4809313.

* <a id="ref-3"></a><a href="https://sivantoledotech.wordpress.com/2010/09/24/failure-to-use-wspr-to-compare-antennas/">[Ref-3]</a> **Technischer Erfahrungsbericht eines Funkamateurs.** Toledo, S. / 4X6IZ (2010). *Failure to Use WSPR to Compare Antennas*.

* <a id="ref-4"></a><a href="https://www.qsl.net/kp4md/wspr.htm">[Ref-4]</a> **Amateurfunk-Fachartikel und Vortrag in einem Amateurfunkclub.** Milazzo, C. F. / KP4MD (2011). *Using the Weak Signal Propagation Reporter Network to Compare Antenna Performance*. Veröffentlicht am 13. Januar 2011; Messungen vom Dezember 2010; vorgestellt am 1. März 2011.

* <a id="ref-5"></a><a href="https://www.researchgate.net/publication/319903566_Improving_HF_Band_SNR_from_analysis_of_WSPR_spots">[Ref-5]</a> **Artikel in einer Amateurfunkzeitschrift.** Griffiths, G.; Squibb, N. J. (2017). *Improving HF Band SNR*. Practical Wireless, Oktober 2017, 23-26. <a href="https://www.wsprnet.org/drupal/sites/wsprnet.org/files/G3ZIL%20G4HZX%20WSPR%20Improving%20HF%20SNR-print.pdf">Vom Autor bereitgestellte Fassung</a>.

* <a id="ref-6"></a><a href="https://www.arrl.org/files/file/History/History%20of%20QST%20Volume%201%20-%20Technology/QS11-2010-Taylor.pdf">[Ref-6]</a> Taylor, J. H.; Walker, B. (2010). *WSPRing Around the World*. QST, 94(11), 30-32.

* <a id="ref-7"></a><a href="https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2023.1184171/full">[Ref-7]</a> **Wissenschaftlicher Übersichtsartikel mit Peer-Review.** Frissell, N. A. et al. (2023). *Heliophysics and amateur radio: citizen science collaborations for atmospheric, ionospheric, and space physics research and operations*. Frontiers in Astronomy and Space Sciences, 10, 1184171. doi:10.3389/fspas.2023.1184171.

* <a id="ref-8"></a><a href="https://www.arrl.org/wspr">[Ref-8]</a> **Offizielle technische Übersicht.** ARRL, *WSPR*: Nachrichtenformat, Codierung, Dauer, zeitlicher Ablauf, belegte Bandbreite und SNR-Bezugsgröße. Abgerufen am 2026-07-12.

* <a id="ref-9"></a><a href="https://www.mdpi.com/2073-4433/13/8/1340">[Ref-9]</a> **Wissenschaftlicher Fachartikel mit Peer-Review.** Lo, S.; Rankov, N.; Mitchell, C.; Witvliet, B. A.; Jayawardena, T. P.; Bust, G.; Liles, W.; Griffiths, G. (2022). *A Systematic Study of 7 MHz Greyline Propagation Using Amateur Radio Beacon Signals*. Atmosphere, 13(8), 1340. doi:10.3390/atmos13081340.

* <a id="ref-10"></a><a href="https://wspr.live/">[Ref-10]</a> **Offizielle Dokumentation des Datendienstes.** WSPR.live, *Welcome to WSPR Live*: Datenbankzugriff, Schema, Zuordnung der Moduscodes, Haftungsausschluss für Rohdaten und Verfügbarkeit sowie Verhalten bei Datenaktualisierungen. Abgerufen am 2026-08-06. Öffentlicher ClickHouse-SQL-Zugriff, Dashboards, Exporte und Würdigung von HB9VQQ für bereitgestellte Rechenressourcen. Abgerufen am 2026-10-06.

* <a id="ref-11"></a><a href="https://www.wsprdaemon.org/">[Ref-11]</a> **Offizielle Projektwebsite.** WSPRDaemon, *WSPR Daemon*: Mehrkanal-Erfassung von Spots, WSPR/FST4W-Dekodierung und Übermittlung von Empfangsberichten, Schätzung des Rauschpegels, Datenbank-/Grafana-Ausgabe und Dienste für Anwendungen Dritter. Abgerufen am 2026-08-06. **Offizielle Betriebsdokumentation.** WsprDaemon, <a href="https://wsprdaemon.readthedocs.io/en/master/FAQ.html#how-does-spot-merging-work-with-multiple-receivers">*FAQ: How does spot merging work with multiple receivers?*</a>: Übermittlung des besten SNR an WSPRnet beim Zusammenführen von Empfangsberichten mehrerer Empfänger. Abgerufen am 2026-09-24. Weitere Projektdokumentation: <a href="https://wsprdaemon.readthedocs.io/en/master/results/wspr.html">*WSPR*</a>, <a href="https://www.wsprdaemon.org/grafana">*Grafana*</a> und <a href="https://wsprdaemon.readthedocs.io/en/master/description/how_it_works.html">*How it works*</a>: Datenbankzugriff, Würdigung der Beiträge zu ClickHouse-Entwicklung und Hosting, Erfassung, Übermittlung von Empfangsberichten sowie Rausch- und Dopplermessungen. Abgerufen am 2026-10-06.

* <a id="ref-12"></a><a href="https://wsjt.sourceforge.io/wsjtx-main_en.html">[Ref-12]</a> **Offizielle Betriebsdokumentation.** WSJT-X 3.0.1 User Guide: Nachrichtenformate WSPR Type 1, Type 2 und Type 3; zufällige Sendeplanung mit `Tx Pct`; getrennte Dateien unter Windows mit `--rig-name`; Audio-Einstellungen und Dateispeicherorte. QRP Labs, <a href="https://qrp-labs.com/qmx">*QMX firmware history and manuals*</a> und <a href="https://www.qrp-labs.com/images/qmx/manuals/operation_1_04_004.pdf">*QMX Operating Manual, firmware 1_04_004*</a> und <a href="https://qrp-labs.com/images/qmx/manuals/VirtualU3S_1_04_008a.pdf">*Virtual U3S Manual, firmware 1_04_008a*</a>: modellspezifische Firmware, Betrieb und Sendeplanung mit Virtual U3S; <a href="https://www.qrp-labs.com/images/ultimate3s/operation3.12a2.pdf">*Ultimate3S Operating Manual, firmware v3.12a2*</a>: WSPR-Frequenzbereich, globales Frame/Start-Verhalten, erweitertes WSPR, aufeinanderfolgende Moduseinträge und `Aux`-Werte je Eintrag; <a href="https://qrp-labs.com/images/appnotes/AN003_A4.pdf">*AN003: Ultimate3/3S relay-switched filters*</a>: gefilterte Ansteuerung von Relais beziehungsweise Treibern und Schaltintervalle bei abgeschalteter HF. Abgerufen am 2026-10-03.

* <a id="ref-13"></a><a href="https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018SW002008">[Ref-13]</a> **Wissenschaftlicher Fachartikel mit Peer-Review.** Frissell, N. A. et al. (2019). *High-Frequency Communications Response to Solar Activity in September 2017 as Observed by Amateur Radio Networks*. Space Weather, 17(1), 118–132. doi:10.1029/2018SW002008.

* <a id="ref-14"></a><a href="https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2022GL097879">[Ref-14]</a> **Wissenschaftlicher Fachartikel mit Peer-Review.** Frissell, N. A. et al. (2022). *First Observations of Large Scale Traveling Ionospheric Disturbances Using Automated Amateur Radio Receiving Networks*. Geophysical Research Letters, 49(5), e2022GL097879. doi:10.1029/2022GL097879.

* <a id="ref-15"></a><a href="https://www.researchgate.net/publication/334612025_Estimating_LF-HF_band_noise_while_acquiring_WSPR_spots">[Ref-15]</a> **Technischer Bericht.** Griffiths, G.; Robinett, R.; Elmore, G. (2019). *Estimating LF–HF band noise while acquiring Weak Signal Propagation Reporter (WSPR) spots*. Version 12, März–November 2019.

* <a id="ref-16"></a><a href="https://www.arrl.org/files/file/QEX_Next_Issue/SeptOct2020/TOFC.pdf">[Ref-16]</a> **Artikel in einer Amateurfunk-Fachzeitschrift; Inhaltsverzeichnis der Ausgabe.** Griffiths, G.; Robinett, R.; Elmore, G. (2020). *Estimating LF-HF Band Noise While Acquiring WSPR Spots*. QEX, September/Oktober 2020, ab S. 25.

* <a id="ref-17"></a><a href="https://f6irf.blogspot.com/2008/04/">[Ref-17]</a> **Technische Berichte eines Funkamateurs.** Destrem, P. / F6IRF (2008). *A statiscal method to evaluate TX antenna performance using WSPR* (24. April), anschließende TX-Analyse, RX-Vergleich auf 160 m und Stationsvergleiche (April 2008).

* <a id="ref-18"></a><a href="https://www.charlespreston.net/antenna/WSPR-Antenna-Prop-Exp-PR.pdf">[Ref-18]</a> **Vorläufiger technischer Bericht.** Preston, C. / KL7OA (später K7TAA) (2009). *WSPR Antenna and Propagation Experiment: Preliminary Results*. Version 1.0, 31. März 2009; die verfügbare Fassung enthält eine Aktualisierung vom 25. Juni 2017.

* <a id="ref-19"></a><a href="https://www.arrl.org/files/file/QEX_Next_Issue/July-August2017/TOFC.pdf">[Ref-19]</a> **Artikel in einer Amateurfunk-Fachzeitschrift; Inhaltsverzeichnis der Ausgabe.** Preston, C. / K7TAA (2017). *Antenna Comparisons Using Simultaneous WSPR Measurements*. QEX, Juli/August 2017, 8–14.

* <a id="ref-20"></a><a href="https://www.darc.de/fileadmin/filemounts/distrikte/g/2026/Talk_in_G/Talk-G_Antennenvergleich_synchr_WSPR_T.Rietdorf_DL2OAH_V2.1_17012025.pdf">[Ref-20]</a> **Technischer Amateurfunkvortrag.** Rietdorf, T. / DL2OAH (2026). *Antennenvergleich mit synchronen WSPR-Daten*. DARC OV R10, 2. Talk in G, TH Köln, 17. Januar 2026, Version 2.1; Messungen vom 12.–21. Januar 2025. Das Vortragsdatum steht auf Folie 1; die Jahreszahl 2025 am Ende des PDF-Dateinamens bezeichnet nicht das Vortragsjahr.

* <a id="ref-21"></a><a href="https://web.tapr.org/meetings/DCC_2020/2020DCC_G3ZIL.pdf">[Ref-21]</a> **Konferenzbeitrag.** Griffiths, G.; Robinett, R. (2020). *Aids to the Presentation and Analysis of WSPR Spots: TimescaleDB database and Grafana*. ARRL/TAPR Digital Communications Conference 2020.

* <a id="ref-22"></a><a href="https://wspr.rocks/help.html">[Ref-22]</a> **Werkzeugdokumentation.** WSPR.Rocks, *Help &amp; Documentation*: SpotQ, SQL-Zugriff, Duplikatanalyse, Karten, Diagramme und Heatmaps. <a href="https://wspr.rocks/head2head/">*Head2Head*</a>: Vergleiche von Empfängern, Sendern und Softwareversionen; die Hilfe beschreibt auch die Untersuchung des Durchlassbereichs.

* <a id="ref-23"></a><a href="https://www.sotabeams.co.uk/wsprlite-classic">[Ref-23]</a> **Produktdokumentation.** SOTABEAMS, *WSPRlite Classic / DXplorer*: WSPR-basierte Analyse der Leistungsfähigkeit von Antennen und DX10-Kennzahl.

* <a id="ref-24"></a><a href="https://www.sotabeams.co.uk/blog/indoor-hf-antennas-does-it-make-much-difference/">[Ref-24]</a> **Experiment eines Funkamateurs und Produktanwendung.** Newstead, R. / SOTABEAMS (2017). *Indoor HF antennas - does it make much difference?*. 5. Mai 2017.

* <a id="ref-25"></a><a href="https://sites.google.com/myuba.be/wspr-station-compare/home">[Ref-25]</a> **Projektdokumentation.** WSPR-Station-Compare, Projektseite mit Bezug auf Vanhamel et al. und Zander. Machiels, W. / ON4AWM, <a href="https://sites.google.com/myuba.be/wspr-station-compare/home/wspr-station-compare-app">*WSPR Station Compare App*</a>: RX-Vergleich, Korrektur eines Empfänger-Offsets, Mindestanforderungen an Beobachtungen, Rufzeichenfilterung und Azimutauswahl.

* <a id="ref-26"></a><a href="https://tools.bsdworld.org/wap">[Ref-26]</a> **Werkzeugdokumentation.** Fred, W6BSD, *Antenna Performance Analysis*: WSPR-Berichtsgenerator zur Darstellung des beobachteten Empfangs nach Zeit, Standort und Band. Die frühere Adresse wspr.bsdworld.org leitet auf die aktuelle Werkzeug-Website weiter.

* <a id="ref-27"></a><a href="https://www.gm4eau.com/home-page/wspr/">[Ref-27]</a> **Werkzeugdokumentation.** GM4EAU, *WATT WSPR Analysis Tool*: Berichte, Karten, Filterung und Zeitverlaufsanimation mit Excel/VBA. <a href="https://rsgb.org/main/blog/tonight-at-eight-archive/2023/12/18/4-december-amateur-radio-construction/">Vortragsankündigung der RSGB</a>: Zuordnung zu Colin Murray, GM4EAU.

* <a id="ref-28"></a><a href="https://qrp-labs.com/qmxp/wsprcorruption.html">[Ref-28]</a> **Technische Untersuchung des Herstellers.** QRP Labs, *WSPR Type 3 callsign corruption*: beobachtete Hash-Kollisionen oder Fehlzuordnungen bei zusammengesetzten Rufzeichen in großen WSPR-Datensätzen und der zugrunde liegende Mechanismus. Abgerufen am 2026-08-25.

* <a id="ref-29"></a><a href="https://github.com/HarrydeBug/WSPR-transmitters/blob/1657468ea27052167191a7deda2440a535567ecd/Standard%20Firmware/Release/Hardware_Version_2_ESP8285/WSPR-TX2.19/WSPR-TX2.19.ino">[Ref-29]</a> **Veröffentlichter Firmware-Quelltext, unveränderliche Revision.** ZachTek-WSPR-TX-Firmware `2.19` für ESP8285-Hardware: Nachrichtenfolge und Frequenzauswahl in `DoWSPR()`, Zeitplanung in `CorrectTimeslot()`, Suffixbeschränkung in `WSPRCallHash()`, Frequenzeinheiten in Centihertz, Auswahl des Produktmodells und Voraussetzungen für den Build. Revision `1657468ea27052167191a7deda2440a535567ecd`. Abgerufen am 2026-08-25; Nachrichtenfolge und zeitlichen Ablauf am 2026-10-25 erneut geprüft.

* <a id="ref-30"></a><a href="https://www.itl.nist.gov/div898/handbook/eda/section3/eda351.htm">[Ref-30]</a> **Statistisches Nachschlagewerk.** NIST/SEMATECH, *e-Handbook of Statistical Methods*: *Measures of Location* (Abschnitt 1.3.5.1) und <a href="https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm">*Measures of Scale* (Abschnitt 1.3.5.6)</a>. Definitionen und Interpretation von arithmetischem Mittelwert, Median, Standardabweichung, medianer absoluter Abweichung und Interquartilsabstand. Abgerufen am 2026-10-25.

* <a id="ref-31"></a><a href="https://www.itl.nist.gov/div898/handbook/prc/section3/prc311.htm">[Ref-31]</a> **Statistisches Nachschlagewerk.** NIST/SEMATECH. *e-Handbook of Statistical Methods*: *Analysis of paired observations*, §7.3.1.1, und <a href="https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm">*Confidence limits for the mean*, §1.3.5.2</a>.

* <a id="ref-32"></a><a href="https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf">[Ref-32]</a> **Metrologischer Leitfaden.** JCGM (2008). *Evaluation of measurement data — Guide to the expression of uncertainty in measurement*. JCGM 100:2008, insbesondere §4.2.7 zu korrelierten Beobachtungen und Anhang G.2–G.3 zur Normalapproximation und Student-t-Verteilung.

* <a id="ref-33"></a><a href="https://www.nist.gov/publications/calculation-uncertainty-mean-autocorrelated-measurements">[Ref-33]</a> **Peer-reviewter Fachartikel.** Zhang, N.-F. (2006). *Calculation of the uncertainty of the mean of autocorrelated measurements*. *Metrologia*, 43, S276–S281. DOI: 10.1088/0026-1394/43/4/S15.

* <a id="ref-34"></a><a href="https://www.arrl.org/files/file/QEX%20Binaries/March%202026/Contents.pdf">[Ref-34]</a> **Technischer Fachzeitschriftenartikel zum Amateurfunk; Inhaltsverzeichnis der Ausgabe.** Ostergaard, D. / N3HXZ (2026). *Using WSPR to Predict Relative Antenna Gain of Directional Antennas*. *QEX*, März/April 2026, ab S. 19. Weitere Primärdokumentation: [Whispering Antenna — WSPR Methodology](https://www.n3hxz.net/wspr-methodology) und [Case Studies](https://www.n3hxz.net/case-studies): sequenzielle Antennenumschaltung, Mittelwertbildung linearer Leistungsverhältnisse, Anforderungen an die Datengrundlage je Empfänger und praktische Antennenvergleiche.

* <a id="ref-35"></a><a href="https://github.com/K5OHY/FarField-Lab">[Ref-35]</a> **Open-Source-Anwendung und technische Dokumentation.** Tim / K5OHY (2026). *FarField Lab*: Software für Antennenvergleiche mit WSPR und RBN, die sequenzielle ABAB/ABBA-Experimente, Analysen alternierender Blöcke, Schätzungen des relativen Gewinns je Empfänger und statistische Validierung unterstützt. [Live-Anwendung](https://farfieldlab.streamlit.app/); [technische Methodik](https://github.com/K5OHY/FarField-Lab/blob/main/docs/METHODOLOGY.md); [Validierung anhand einer veröffentlichten Studie](https://github.com/K5OHY/FarField-Lab/blob/main/tests/test_dale_study.py). Abgerufen am 2026-11-08.

<div style="page-break-before: always;"></div>

<a id="sec-8-5"></a>
<a id="sec-disclaimer"></a>

## Experimentelle Nutzung und Haftungsausschluss

WSPRadar ist ein kostenloses, nicht kommerzielles Hobbyprojekt für Experimente im Amateurfunk, Bildung und wissenschaftliche Erkundung.

WSPRadar analysiert Beobachtungsdaten aus öffentlich zugänglichen Datenbanken mit WSPR-Empfangsberichten. Sowohl die Quelldaten als auch die daraus gewonnenen Analysen können Fehler, Auslassungen, Verzerrungen durch die Berichterstattung oder Ungenauigkeiten enthalten. Statistische Annahmen, nicht kontrollierte Ausbreitungsbedingungen und Softwarefehler können die Zuverlässigkeit und Interpretation der Ergebnisse zusätzlich beeinflussen.

WSPRadar ist kein kalibriertes Messinstrument. Seine Ergebnisse liefern Anhaltspunkte und sollten unabhängig überprüft werden. Sie dürfen nicht als alleinige Grundlage für bedeutende persönliche, finanzielle, sicherheitsbezogene, technische, rechtliche oder andere folgenreiche Entscheidungen dienen. **WSPRadar ist nicht für sicherheitskritische Anwendungen, Entscheidungen in Notfällen oder den Nachweis der Einhaltung gesetzlicher oder behördlicher Anforderungen vorgesehen.**

Software, Dienst und Ergebnisse werden **„as is“ und „as available“ — im vorliegenden Zustand und nach Verfügbarkeit —** bereitgestellt. Es wird keine zusätzliche vertragliche Garantie für Richtigkeit, Vollständigkeit, Zuverlässigkeit, Eignung für einen bestimmten Zweck oder fortlaufende Verfügbarkeit gegeben. Diese Erklärung schließt gesetzliche Rechte weder aus noch schränkt sie ein.

Die Nutzung und Interpretation der Ergebnisse liegen in der Verantwortung des Nutzers. Dazu gehört, ihre Eignung unabhängig zu beurteilen, bevor auf ihrer Grundlage gehandelt wird. Zwingende gesetzliche Rechte bleiben unberührt.
