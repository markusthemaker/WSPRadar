"""
Deutsches Handbuch für WSPRadar.
Wird im Web-UI und für den PDF-Export verwendet.
"""

DOC_DE = r"""
---

### 1. Einleitung & Zielsetzung

Im Amateurfunk stützt sich die Bewertung der Antennenleistung traditionell auf anekdotische Signalrapporte oder lokales A/B-Umschalten. Diese herkömmlichen Methoden unterliegen jedoch erheblichen Störvariablen: schnelles ionosphärisches Fading (QSB), inkonsistente Sendeleistungen der Gegenstationen und lokale Störpegel (QRM). Diese unberechenbaren Faktoren machen es extrem schwierig, die tatsächliche Leistung einer Antenne im täglichen Betrieb objektiv zu messen.

Hier ändert das **Weak Signal Propagation Reporter (WSPR)** Protokoll die Spielregeln. WSPR ist eine digitale Betriebsart, die speziell dafür entwickelt wurde, potenzielle Ausbreitungswege mithilfe von zweiminütigen Low-Power-Baken zu untersuchen. Jeden Tag senden und empfangen Tausende von Stationen weltweit völlig autonom diese Baken und protokollieren dabei Millionen von hochpräzisen Signal-Rausch-Verhältnis (SNR) Messwerten in einer öffentlichen Datenbank. Wer an WSPR teilnimmt, verwandelt seine Station effektiv in eine kalibrierte globale Sonde, die kontinuierlich harte Daten darüber sammelt, wo das eigene Signal landet und wen man hören kann.

Das Ziel von **WSPRadar** ist es, diesen riesigen, durch Crowdsourcing entstandenen Datensatz zu nutzen, um ein systematisches, semi-quantitatives Framework zur Bewertung von Sende- (TX) und Empfangsantennen (RX) bereitzustellen. Durch die Extraktion historischer WSPR-Spot-Daten aus der wspr.live-Datenbank wendet dieses Tool eine strikte räumliche und zeitliche Normalisierung an. Es rechnet atmosphärische Volatilität und ungleiche Sendeleistungen mathematisch heraus, um die einzige Metrik zu isolieren, die wirklich zählt: die reine Hardwareeffizienz und Abstrahlcharakteristik deines Antennensystems.

### 2. Key Use Cases & Capabilities (Anwendungsfälle)

WSPRadar wurde entwickelt, um spezifische, häufige Fragestellungen im Amateurfunk präzise zu beantworten:
* **Path Viability & Skip Zones (Gibt es eine Öffnung?):** Erreicht mein Signal heute Ozeanien? Wo liegen meine toten Winkel? *(Gelöst durch Absolute Analysen für TX und RX).*
* **The "Am I doing okay?" Test (Lokales Benchmarking):** Ist meine Station im Vergleich zu anderen Funkern in meiner Region gut oder schlecht? *(Gelöst durch den Referenz-Radius-Benchmark).*
* **Buddy-Testing (Station vs. Station):** Mein Freund funkt 10 km weiter mit einer Yagi, ich mit einem Dipol. Wer ist heute besser? *(Gelöst durch den Vergleich gegen eine Spezifische Referenzstation mit synchroner Auswertung).*
* **The Hardware Laboratory (Echte A/B-Tests):** Ich brauche ein isoliertes Labor-Setup für Antenne A vs. B, RX vs. RX oder TX vs. TX am eigenen Standort. *(Gelöst durch den Hardware A/B-Test Modus).*
* **DX vs. NVIS Profiling (Take-Off Angle beurteilen):** Ist meine Antenne ein Flachstrahler (DX) oder ein Steilstrahler (NVIS)? *(Ablesbar an der Performance in den nahen vs. weiten Distanzringen der Karte).*
* **Uncovering Local QRM (Der "Alligator-Test"):** Werde ich weltweit gehört, höre aber selbst nichts? *(Beweisbar durch die Kombination eines TX- und RX-Vergleichslaufs gegen dieselbe Referenz).*
* **Statistical Proof vs. Guesswork:** Ist ein gemessener Vorteil von 2 dB physikalisch echt oder nur Zufall? *(Gelöst durch den integrierten Wilcoxon-Test zur Signifikanzprüfung).*

**💡 Quick Start:** Klicken Sie in der Konfiguration auf `✨ Load Demo Config` und anschließend auf `Run TX` oder `Run RX`, um das Tool direkt mit Beispieldaten zu testen. *(Hinweis: Die aktuellen Demo-Daten sind vorerst nur für den Radius-Benchmark ausgelegt und noch etwas spärlich. Umfassendere Demo-Datensätze folgen in Kürze).*

### 3. Kern-Konzepte: Absolut vs. Vergleich

Um aus WSPR-Daten verlässliche Schlüsse zu ziehen, trennt WSPRadar die Analyse streng in zwei Betrachtungsweisen:

#### Absolute Analysen (Die reine Ausbreitung):
Hierbei geht es um die Beantwortung der Frage "Gibt es einen offenen Ausbreitungsweg?". Da Ausbreitungsbedingungen oft asymmetrisch sind, generiert WSPRadar hierfür zwei strikt getrennte Betrachtungen:
* **TX Absolut:** *Wo wird mein gesendetes Signal gehört?* Isoliert alle Instanzen, in denen Sie senden, und plottet alle weltweiten **Empfangsstationen** auf der Karte. Misst die reine Sendefähigkeit und zeigt Ihre Skip-Zonen (normiert auf 1 Watt).
* **RX Absolut:** *Wen kann meine Station hören?* Isoliert alle Instanzen, in denen Sie empfangen, und plottet alle weltweiten **Sendestationen** auf der Karte. Misst die reine Empfangsempfindlichkeit und visualisiert offene Pfade zu Ihrem Standort (normiert basierend auf der gemeldeten Leistung des Senders).
  Beide Karten zeigen Ihre globalen toten Winkel. Wenn Sie wissen wollen, ob Ihr Signal heute Ozeanien erreicht (oder ob Sie Ozeanien hören können), betrachten Sie die Absolute Maps.
  
#### Vergleichende Benchmark Analysen (Die Hardware-Differenz):
Hier wird die Frage "Bin ich besser als Setup B?" beantwortet. In der Compare-Map werden das lokale Störrauschen an der Gegenstation sowie das schnelle ionosphärische Fading (QSB) mathematisch *vollständig eliminiert*. Übrig bleibt ausschließlich die reine Differenz ($\Delta$ SNR) zwischen den zwei getesteten Hardware-Setups, aufgeschlüsselt nach geografischen Segmenten. Dies ist das ultimative Werkzeug für Leistungs-Benchmarking. 
* **Bei TX Vergleichen:** Beide Sendesignale werden durch denselben Remote-Empfänger bewertet. Dadurch werden lokales QRM des Remote-Empfängers und dessen Antennengewinn funktional herausgekürzt. Berechnung: $\Delta SNR_{TX} = SNR_{norm,target} - SNR_{norm,benchmark}$
* **Bei RX Vergleichen:** Beide lokalen Empfänger bewerten dasselbe ferne Sendesignal simultan. Dadurch sind die Leistung des fernen Senders und der grundlegende Ausbreitungsweg identisch. Jegliche Differenz ist strikt auf die eigene Empfangsantenne und das eigene lokale QRM zurückzuführen. Berechnung: $\Delta SNR_{RX} = SNR_{measured,target} - SNR_{measured,benchmark}$

#### Das Bivariate Auswertungsmodell (Vermeidung von Survivorship Bias)
Verlässt man sich beim Vergleich zweier Setups ausschließlich auf die mediane SNR-Differenz ($\Delta$ SNR), führt dies unweigerlich zu einem statistischen Fehler namens 'Survivorship Bias'. Eine überlegene Antenne decodiert extrem schwache Signale an der Rauschgrenze, die ein schlechteres Setup völlig verpasst. Diese zusätzlichen, grenzwertigen Spots senken mathematisch den SNR-Median des besseren Setups und lassen es fälschlicherweise schlechter aussehen, wenn alles vermischt wird. WSPRadar löst dies durch ein striktes bivariates Modell:
1. **System Sensitivity (Yield / Ausbeute):** Analysiert die absolute Anzahl exklusiver vs. gemeinsamer (Joint) Decodes, um die tatsächliche Empfindlichkeit und Reichweite an der Rauschgrenze zu beweisen.
2. **Hardware Linearity ($\Delta$ SNR):** Wird *ausschließlich* für Joint Spots (Signale, die von beiden Setups zeitgleich im selben 2-Minuten-Fenster decodiert wurden) berechnet, um den reinen physikalischen Gain-Unterschied unter absolut identischen Ausbreitungsbedingungen zu beweisen.

### 4. Methodik für vergleichende Analysen

WSPRadar bietet drei fundamentale Säulen für vergleichende Hardware-Tests, je nachdem, was Sie beweisen möchten. Ein A/B-Test ist physikalisch nur valide, wenn *alle* anderen Variablen identisch bleiben (z.B. Testen Sie Antenne A vs. B bei gleichem Sender, oder Sender A vs. B bei gleicher Antenne).

#### Säule 1: Lokales Umfeld (Radius-Benchmark)
* **Ziel:** Messung Ihrer Leistungsfähigkeit gegen den Durchschnitt Ihrer Nachbarschaft.
* **Methodik:** WSPRadar aggregiert alle lokalen WSPR-Stationen innerhalb eines definierten Radius (z.B. 50 km). Da angenommen wird, dass alle diese Stationen denselben Makro-Ausbreitungsbedingungen unterliegen, liefert Ihnen dies eine harte statistische Einordnung, ob Ihr QTH (Standort) oder Ihre Antenne über- oder unterdurchschnittlich abschneidet. Es wird die *Spot-by-Spot (Synchronous)* Mathematik angewandt.

#### Säule 2: Fremde Referenzstation (Buddy-Test)
* **Ziel:** Ein 1-zu-1 Vergleich mit einem bekannten Funkamateur (Standort vs. Standort, Antenne vs. Antenne, oder einfach Station vs. Station).
* **Methodik:** Sie definieren ein abweichendes Referenz-Rufzeichen (z.B. einen Funk-Freund in 10 km Entfernung). Da Sie beide unter unterschiedlichen Rufzeichen in der Luft sind, sammelt die Datenbank problemlos alle Spots. WSPRadar isoliert Instanzen, in denen beide Signale vom exakt selben Empfänger im exakt selben 2-Minuten-WSPR-Zyklus decodiert wurden. Auch hier eliminiert die *Spot-by-Spot (Synchronous)* Mathematik das Fading vollständig auf Bitebene.

#### Säule 3: Echter Hardware A/B-Test (Das eigene Setup)
* **Ziel:** Ein präziser Labor-Test der eigenen Hardware am eigenen Standort mit dem eigenen Rufzeichen. Dies geht weit über den klassischen Vergleich hinaus: Solange alle anderen Parameter identisch bleiben, können Sie hier jede beliebige Variable isoliert testen. Vergleichen Sie Empfänger gegen Empfänger (RX vs. RX), Transceiver gegen Transceiver (TX vs. TX), unterschiedliche Baluns/Speiseleitungen oder evaluieren Sie die exakte Aufbaustelle einer Antenne innerhalb desselben Grundstücks (Standort A vs. Standort B). WSPRadar spaltet sich hierfür je nach Test-Richtung in zwei spezielle Rechenpfade auf:
* **Der RX A/B-Test (Simultan):** Zwei parallel laufende Empfänger (SDRs) werten gleichzeitig WSPR-Signale aus. **Der Trick:** Damit das WSPR-Netzwerk die synchronen Spots Ihrer Empfänger nicht als Duplikate löscht, müssen Sie in Ihrer Empfangssoftware (z.B. WSPRdaemon) unterschiedliche Rufzeichen-Suffixe angeben. 
  * **Setup A:** Meldet unter Ihrem Hauptrufzeichen (z. B. `DL1MKS`).
  * **Setup B:** Meldet mit einem spezifischen Suffix (z. B. `DL1MKS/P`).
  In WSPRadar geben Sie im Self-Test Modus diese beiden Rufzeichen an. Das Tool generiert dann via *Spot-by-Spot (Synchronous)* Mathematik exakte Joint-Spots für den ultimativen Hardware-Vergleich.
* **Der TX A/B-Test (Sequenziell / Time-Slicing):** Sie verwenden einen Transceiver, der periodisch zwischen Setup A und B umschaltet. Da Setup A und B *niemals* im selben Slot senden, nutzt WSPRadar die **Asynchronous Math (Time-Averaging)**: Es spaltet Ihre Daten anhand der Startminuten (Gerade: 00, 04, 08 / Ungerade: 02, 06, 10) auf und bildet Langzeit-Mediane, bevor das $\Delta$ SNR berechnet wird. 
  * *Hinweis zur TX-Hardware:* Ein solcher Test erfordert Hardware, die deterministisch nach Zeitplan sendet. Ein QMX-Transceiver lässt sich beispielsweise exakt programmieren (`frame=10` sendet alle 10 Minuten, `start=2` beginnt exakt in Minute 2). Die Standard-Software WSJT-X sendet "out-of-the-box" zufällig (random) und ist ohne spezielle Zusatztools für zeitlich fixierte A/B-Tests nicht geeignet.
  * *Warum kein Multi-Cycle WSPR (Rufzeichen-Zusätze wie /1 oder /P)?* WSPR-Nachrichten mit Suffixen zwingen das Protokoll dazu, zyklusübergreifend zu senden (Typ 1 und Typ 3 Nachrichten). Da viele weltweite Empfangsstationen Typ 3 Nachrichten nicht sauber aus dem Rauschen decodieren können, sinkt die absolute Anzahl an weltweit geloggten Spots für Compound-Rufzeichen drastisch. Zudem sind künstliche Zusätze wie `/1` oder `/2` funkrechtlich keine zugelassenen Rufzeichenstrukturen, und die Nutzung von `/P` ist strikt nur bei tatsächlichem Portabel-Betrieb gestattet. Daher setzt WSPRadar beim eigenen TX A/B-Test exklusiv auf Time-Slicing mit dem *identischen* Standard-Rufzeichen und trennt die Signale mathematisch anhand der ungeraden/geraden Minuten auf, um 100 % der Dekodierleistung des globalen Netzwerks zu erhalten.

### 5. Allgemeine Daten-Methodik

#### 5.1 Leistungs-Normalisierung
Um einen direkten Vergleich zwischen Stationen mit unterschiedlichen Hardware-Setups zu ermöglichen, werden alle absoluten Signal-Rausch-Verhältnis (SNR) Daten auf eine Standardreferenz von 1 Watt (30 dBm) normalisiert. 
$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$
Diese Normalisierung wird auf alle TX- und RX-Absolutanalysen angewendet, wodurch die Sendeleistung als unabhängige Variable eliminiert und die intrinsische Effizienz sowie der Abstrahlwinkel des Antennensystems isoliert werden.

#### 5.2 Geografisches Rastering und Projektion
Räumliche Daten werden mithilfe einer mittabstandstreuen Azimutalprojektion (Azimuthal Equidistant) abgebildet, zentriert auf den Maidenhead-Locator des Benutzers. Die Render-Engine ist explizit auf eine perfekte mathematische Kugel (Radius = 6371 km) fixiert. Dies garantiert eine 100%ige geometrische Konsistenz zwischen den errechneten Distanzen der Datentabellen und der visuellen Platzierung auf der Karte (Vermeidung von WGS84-Ellipsoid-Verzerrungen).
* Die Karte ist in ein dynamisches Zonenmodell unterteilt, das konzentrische radiale Bänder von 2.500 km nutzt (was ungefähr einem typischen F2-Schicht-Hop entspricht).
* Azimutale Segmente werden in diskrete Kompass-Richtungen (z. B. 22.5° für N, NNE, NE) unterteilt, um der räumlichen Dichte Rechnung zu tragen.
* Jedes resultierende geografische Segment erhält einen eindeutigen Koordinaten-Identifikator für die Datenaggregation.

#### 5.3 Räumliche Normalisierung (Median-Aggregation)
Um räumliche Verzerrungen durch eine unverhältnismäßige Empfängerdichte in bestimmten Regionen abzuschwächen, verwendet das Tool eine zweistufige "Median des Medians"-Aggregation:
1. **Aggregationsstufe Station:** Der Median-SNR aller Spots wird für jede eindeutige Remote-Station berechnet.
2. **Aggregationsstufe Segment:** Der Median dieser Stationswerte wird berechnet, um den finalen Wert für das geografische Segment zu bestimmen. 
Diese Methode verhindert den "Receiver Density Bias" – bei dem dichte Empfänger-Cluster (z. B. in Europa oder Nordamerika) spärlich besiedelte Regionen (z. B. Asien oder Afrika) im globalen Durchschnitt statistisch übertönen. Jedes geografische Segment erhält eine faire, isolierte Bewertung, wodurch sichergestellt wird, dass eine einzelne, hochaktive Station eine Region nicht statistisch dominiert.

### 6. Visuelle Interpretation & Segment-Inspektor

#### 6.1 Visuelle Lesehilfe (Karten-Elemente)
* **Heatmaps:** Absolute Modi werden in rohen dB gerendert. Vergleichende Modi (Compare) bilden das Δ SNR auf einer standardisierten S-Stufen-Skala ab (1 S-Stufe = 6 dB). Positive Werte (rot) zeigen eine Überlegenheit gegenüber der Benchmark an; negative Werte (blau) deuten auf eine systemische Schwäche hin.
* **Distanzringe (Take-Off Angle):** Beachten Sie bei der Analyse die Distanz: Die Überlegenheit in nahen Ringen (z.B. < 2500 km) deutet auf gute NVIS-Eigenschaften (Steilstrahler) hin, während eine Dominanz in weiten Ringen (> 10000 km) einen flachen Abstrahlwinkel (DX-Flachstrahler) beweist.
* **Scatter Plots:** Einzelne Stationen werden als Punkte dargestellt. Grüne Punkte zeigen gemeinsam (im exakt selben 2-Minuten-Zyklus) decodierte Stationen an. Gelb-orange Punkte stehen für Stationen, die von beiden gehört wurden, jedoch asynchron. Violette Punkte stehen für exklusive Decodierungen der eigenen Station ("Only [Target]"), während weiße Punkte Stationen anzeigen, die nur von der Referenzstation gehört wurden ("Only Reference").
* **Pol-Markierungen:** Zur besseren räumlichen Orientierung – insbesondere bei Ausbreitungswegen, die buchstäblich über die Pole hinweg verlaufen – sind der geografische Nordpol (N-POL) und Südpol (S-POL) mit neongrünen Kreuzen exakt auf der Karte markiert.
* **Map Footer & 1D-Venn Diagrams** Die Hauptkarte enthält am unteren Rand auf 100% skalierte, horizontale gestapelte Balkendiagramme. Diese 1D-Venn-Diagramme visualisieren sofort die relative Systemempfindlichkeit ohne Survivorship Bias. 
  * Der **SPOTS**-Balken zeigt die Verteilung des reinen Datenvolumens. 
  * Der **STATIONS**-Balken validiert den echten geografischen Fußabdruck (um sicherzustellen, dass eine hohe exklusive Spot-Anzahl nicht nur von einer einzigen, sehr lauten Station generiert wurde). 
Die Balken sind farblich exakt auf die Markierungen der Karte abgestimmt: Violett (Nur Setup A), Grün (Joint) und Weiß (Nur Setup B). Die absoluten Zahlenwerte stehen direkt in den Blöcken.
* **High-Res Export:** Oberhalb jeder Karte befindet sich eine dezente Toolbar ("⚙️ Render High-Res Map"). Hiermit lässt sich bedarfsgesteuert eine verlustfreie, druckfähige 300-DPI-Version der aktuellen Karte berechnen und herunterladen, ohne die interaktive Benutzeroberfläche durch Ladezeiten zu blockieren.

#### 6.2 Detaillierte Auswertung: Segment-Inspektor (Histogramm & Tabellen)
Direkt unter den Karten befindet sich der Segment-Inspektor mit zwei kaskadierenden Dropdowns. Hier können Sie gezielt eine Distanz und anschließend eine Himmelsrichtung (z.B. NNE) auswählen, um die zugrundeliegende Datenverteilung dieses Segments im Detail zu analysieren.
1. **Absolute Modi:** Zeigt die Verteilung der normierten SNR-Werte aller Stationen in diesem Segment in Form eines diskreten Säulendiagramms. Die X-Achse zeigt dabei die individuellen *Station Medians*. Die rote gestrichelte Linie markiert den finalen *Segment Median*, der aus all diesen Werten gebildet wird.
2. **Compare Modi:** Zeigt die Verteilung der Δ SNR-Werte. Dies ist entscheidend, um zu beurteilen, ob ein knapper Medianwert durch eine konsistente Überlegenheit (enge Glockenkurve) oder durch extrem wilde Streuung zustande kam. Die X-Achse repräsentiert die individuellen *Station Medians* (die erste Aggregationsstufe). Die rote gestrichelte Linie markiert den final aggregierten *Segment Median* (den "Median des Medians" über alle Stationen dieses Segments).
3. **Station Insights Tabelle:** Unterhalb des Histogramms listet eine interaktive Datentabelle die exakten beteiligten Remote-Stationen für das ausgewählte Segment auf. Die Spalte "Median Δ SNR" zeigt hier den zusammengeführten Wert für exakt diese eine Station. In vergleichenden Modi schlüsselt die Tabelle zudem auf, wie viele gemeinsame Decodierungen (`Joint Spots`) diesen Wert bilden und wie viele exklusive Decodierungen (`Nur Referenz` oder `Nur eigenes Rufzeichen`) vorliegen.
4. **Drill-Down Data (Rohdaten & Export):** Durch Anklicken einer Zeile in der "Station Insights" Tabelle öffnet sich die detaillierte Ansicht für diese spezifische Station. Hier wird jeder einzelne 2-Minuten-Zyklus (Spot) offengelegt. Im Compare-Modus sehen Sie hier die rohen Δ SNR-Werte der einzelnen "Joint Spots", deren Median exakt den "Station Median" aus der übergeordneten Tabelle bildet. 
Dank der Multi-Select-Funktion lassen sich per Shift-Klick mehrere Stationen gleichzeitig markieren, oder über die Checkbox im Tabellenkopf direkt *alle* Stationen des Segments auswählen. So generieren Sie im Handumdrehen ein vollständiges Raw-Data-Audit. Die interaktive Master-Tabelle bietet native Werkzeuge oben rechts: Sie können die Daten **durchsuchen**, gezielt **filtern**, zusätzliche **Spalten ein- oder ausblenden** und den gesamten Datensatz mit einem Klick als **CSV-Datei herunterladen** zur weiteren Analyse in Excel.

### 7. Konfiguration & Parameter-Referenz

#### 7.1 Core Parameters
* **Ziel-Rufzeichen & QTH Locator:** Identifiziert die primäre Station und setzt das mathematische Zentrum für die Kartenprojektion.
* **Frequenzband & Zeitrahmen:** Definiert das Band und das zeitliche Fenster zur Extraktion der Spot-Daten.

#### 7.2 Comparison against References and A/B Testing
* **Vergleichsmodus:** Wählt die grundlegende Art des Benchmarks aus (Referenz-Radius, Fremdes Rufzeichen oder Eigenes Setup).
* **Referenz-Suchradius (km):** Definiert die Distanzschranke zur Aggregation lokaler WSPR-Stationen beim Radius-Benchmark.
* **Referenz-Rufzeichen:** Das spezifische Rufzeichen der externen Gegenstation beim Buddy-Test.
* **Test-Setup (nur bei Hardware A/B-Test):** Schaltet zwischen `RX A/B-Test (2 Empfänger, Simultan)` und `TX A/B-Test (1 Sender, Time-Slicing)` um.
* **Target Locator & Referenz Locator:** Die exakten 6-stelligen Maidenhead-Locators (z.B. JN37AA vs. JN37AB) zur Trennung der Datenströme bei simultanen RX-Tests.
* **Target Zeit-Slot & Referenz Zeit-Slot:** Die Zuweisung der Sendezyklen (`Gerade Min` vs. `Ungerade Min`) bei sequenziellen TX-Tests.

#### 7.3 Advanced Config & Expert Settings
* **Lokaler QTH Sonnenstand:** Um tageszeitabhängigen Veränderungen der Ionosphäre Rechnung zu tragen (z. B. D-Schicht Dämpfung am Tag vs. F2-Schicht Öffnung bei Nacht), nutzt WSPRadar die astronomische Bibliothek `ephem`. Der exakte Sonnen-Höhenwinkel wird für jeden WSPR-Spot passend zum QTH berechnet. Nutzer können die Daten gezielt nach `Daylight` (> +6°), `Nighttime` (< -6°) oder der magischen `Greyline` (Dämmerung zwischen -6° und +6°) filtern.
* **Kartenbereich (Max. Distanz):** Legt den visuellen Zoom-Faktor der Kartendarstellung (in Kilometern) vom Zentrum fest. Hilfreich, um regionale Ausbreitungen besser zu untersuchen.
* **Min. Spots pro Station:** Qualifiziert die Validität eines Ausbreitungsweges. Eine Remote-Station muss die Übertragung mindestens so oft decodiert haben, um in die Aggregation aufgenommen zu werden. Dies filtert flüchtige Ausbreitungsanomalien wie Meteor- oder Flugzeug-Scatter effektiv heraus.
* **Globaler Filter: Min. Spots / Station:** Dieser globale Filter verhindert, dass einzelne Zufallsempfänge das Bild verfälschen. Wenn Setup A und Setup B eine Gegenstation zeitgleich decodieren, zählt dies physikalisch korrekt als *ein* offener Ausbreitungszyklus. Nur Stationen, deren Gesamtsumme an einzigartigen, offenen Zyklen den eingestellten Schwellenwert erreicht, passieren den Filter. Dies eliminiert rigoros transiente Ausbreitungsanomalien (wie Meteorscatter oder falsche Decodes) über alle Diagramme, Histogramme und Tabellen hinweg.
* **Compare Map Statistische Signifikanz (Wilcoxon Test):** Anstatt sich blind auf den Median der Δ SNR zu verlassen, erlaubt WSPRadar die Prüfung echter statistischer Signifikanz bei Vergleichskarten (Compare). Wird der Wilcoxon-Test aktiviert, überschreibt das Tool den Basiswert der "Min. Stationen" für Vergleichskarten bei Bedarf dynamisch nach oben (auf bis zu 8 Stationen), um die mathematischen Mindestanforderungen des Tests für das gewählte Konfidenzniveau zu erfüllen. Segmente, die den p-Wert Test nicht bestehen, werden rigoros verworfen.

### 8. Diskussion, Limitationen & Haftungsausschluss

#### Diskussion:
WSPRadar überführt anekdotische Amateurfunk-Rapporte in einen rein datengestützten, quantitativen Ansatz. Durch die strikte zeitliche und räumliche Synchronisation der Spots (insbesondere im Compare-Modus) gelingt es dem Tool, die unberechenbaren Einflüsse der Ionosphäre (QSB) und unterschiedliche lokale Rauschpegel (QRM) herauszukürzen. Dies ermöglicht eine objektive Leistungsbewertung der Antennen-Hardware im realen Betrieb, die sonst nur mit extrem teurem, kalibrierten Messequipment oder Drohnenflügen möglich wäre.

#### Limitationen:
* **Performance Limits & Data Latency:** Um Server-Ressourcen zu schonen, ist der abfragbare Zeitraum auf 7 Tage begrenzt und Zeitabfragen werden zur Optimierung des globalen Cachings auf 15-Minuten-Intervalle quantisiert. Zudem hat die globale wspr.live Datenbank eine natürliche Aggregations-Latenz von ca. 15 bis 30 Minuten, bis brandneue Spots nach dem Senden im Tool sichtbar werden.
* **Verfügbarkeit vs. Uptime:** WSPR protokolliert systembedingt nur erfolgreiche Decodierungen. Der absolute Median-SNR spiegelt daher die Signalstärke *während eines offenen Ausbreitungsweges* wider. Geschlossene Bänder (Dead Bands) senken den Durchschnitt nicht.
* **Die TX-Power-Kalibrierungsfalle:** WSPRadar ist anfällig für fehlerhaft gemeldete Sendeleistungen ("Garbage In, Garbage Out"). Die Normalisierungsformel geht davon aus, dass die im WSPR-Paket gemeldete Leistung exakt der am Speisepunkt abgestrahlten Leistung entspricht. Wenn ein Transceiver bei schlechtem SWR automatisch die Leistung drosselt oder hohe Verluste im Speisekabel auftreten, sinkt das berechnete $SNR_{norm}$. Betreiber, die strenge A/B-Tests durchführen, müssen ihre reale Ausgangsleistung physisch mit einem Wattmeter kalibrieren.
* **Polarisation:** WSPRadar misst nicht den isolierten Freiraumgewinn einer Antenne, sondern die reale Systemeffizienz. Diese beinhaltet auch das Polarisations-Matching unter echten Ausbreitungsbedingungen, da die Ionosphäre die Signale durch die Faraday-Rotation beeinflusst.

#### Haftungsausschluss (Disclaimer):
WSPRadar ist ein experimentelles Open-Source-Projekt (Beta) und wird "wie besehen" (as is) ohne jegliche Gewährleistung bereitgestellt. Der Quellcode und die mathematischen Modelle sind öffentlich einsehbar und überprüfbar. Dennoch übernimmt der Entwickler **keinerlei Garantie oder Haftung** für die Richtigkeit, Vollständigkeit oder Zuverlässigkeit der generierten Daten und Grafiken.
Die Ergebnisse basieren auf Nutzerdaten einer Drittanbieter-Schnittstelle (wspr.live), welche durch fehlerhafte Kalibrierung (z. B. falsch gemeldete TX-Leistungen) verfälscht sein können. **Nutzer sollten niemals finanzielle Entscheidungen (wie den Kauf oder Verkauf von teurer Funk- oder Antennen-Hardware) ausschließlich auf Basis dieses Tools treffen.** Die Nutzung erfolgt vollständig auf eigene Gefahr.

#### Lizenz (Open Source):
WSPRadar ist freie Software: Sie können sie unter den Bedingungen der GNU Affero General Public License (AGPLv3), wie von der Free Software Foundation veröffentlicht, weitergeben und/oder modifizieren. Diese Lizenz garantiert, dass der Quellcode – auch bei Netzwerk-Nutzung (SaaS) und nach Modifikationen – für die Amateurfunk-Community immer frei und offen verfügbar bleiben muss.
"""