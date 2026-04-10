# docs/doc_de.py

"""
Deutsches Handbuch für WSPRadar.
Wird im Web-UI und für den PDF-Export verwendet.
"""

DOC_DE = r"""
---

### Inhaltsverzeichnis
* [1. Einleitung und Zielsetzung](#sec-1)
* [2. Key Use Cases und Capabilities (Anwendungsfaelle)](#sec-2)
* [3. Kern-Konzepte: Absolut vs. Vergleich](#sec-3)
  * [Absolute Analysen (Die reine Ausbreitung)](#sec-3-1)
  * [Vergleichende Benchmark Analysen (Die Hardware-Differenz)](#sec-3-2)
  * [Das Bivariate Auswertungsmodell (Vermeidung von Survivorship Bias)](#sec-3-3)
* [4. Methodik fuer vergleichende Analysen](#sec-4)
  * [Option 1: Lokales Umfeld (Nearest Peers / Radius-Benchmark)](#sec-4-1)
  * [Option 2: Fremde Referenzstation (Buddy-Test)](#sec-4-2)
  * [Option 3: Echter Hardware A/B-Test (Das eigene Setup)](#sec-4-3)
* [5. Allgemeine Daten-Methodik](#sec-5)
  * [5.1 Leistungs-Normalisierung](#sec-5-1)
  * [5.2 Geografisches Rastering und Projektion](#sec-5-2)
  * [5.3 Raeumliche Normalisierung (Median-Aggregation)](#sec-5-3)
  * [5.4 Temporaere Synchronisation (Heartbeat-Filter / Offline-Schutz)](#sec-5-4)
* [6. Visuelle Interpretation und Segment-Inspektor](#sec-6)
  * [6.1 Visuelle Lesehilfe (Karten-Elemente)](#sec-6-1)
  * [6.2 Detaillierte Auswertung: Segment-Inspektor (Histogramm und Tabellen)](#sec-6-2)
* [7. Konfiguration und Parameter-Referenz](#sec-7)
  * [7.1 Core Parameters](#sec-7-1)
  * [7.2 Comparison against References and A/B Testing](#sec-7-2)
  * [7.3 Advanced Config und Expert Settings](#sec-7-3)
* [8. Diskussion, Limitationen und Haftungsausschluss](#sec-8)
* [Anhang A: Setup: Paralleler Betrieb multipler WSJT-X Instanzen](#sec-a)

<a id="sec-1"></a>
### 1. Einleitung und Zielsetzung

Im Amateurfunk stützt sich die Bewertung der Antennenleistung traditionell auf anekdotische Signalrapporte oder lokales A/B-Umschalten. Diese herkömmlichen Methoden unterliegen jedoch erheblichen Störvariablen: schnelles ionosphärisches Fading (QSB), inkonsistente Sendeleistungen der Gegenstationen und lokale Störpegel (QRM). Diese unberechenbaren Faktoren machen es extrem schwierig, die tatsächliche Leistung einer Antenne im täglichen Betrieb objektiv zu messen.

Hier ändert das **Weak Signal Propagation Reporter (WSPR)** Protokoll die Spielregeln. WSPR ist eine digitale Betriebsart, die speziell dafür entwickelt wurde, potenzielle Ausbreitungswege mithilfe von zweiminütigen Low-Power-Baken zu untersuchen. Jeden Tag senden und empfangen Tausende von Stationen weltweit völlig autonom diese Baken und protokollieren dabei Millionen von hochpräzisen Signal-Rausch-Verhältnis (SNR) Messwerten in einer öffentlichen Datenbank. Wer an WSPR teilnimmt, verwandelt seine Station effektiv in eine kalibrierte globale Sonde, die kontinuierlich harte Daten darüber sammelt, wo das eigene Signal landet und wen man hören kann.

Das Ziel von **WSPRadar** ist es, diesen riesigen, durch Crowdsourcing entstandenen Datensatz zu nutzen, um ein systematisches, semi-quantitatives Framework zur Bewertung von Sende- (TX) und Empfangsantennen (RX) bereitzustellen. Durch die Extraktion historischer WSPR-Spot-Daten aus der wspr.live-Datenbank wendet dieses Tool eine strikte räumliche und zeitliche Normalisierung an. Es rechnet atmosphärische Volatilität und ungleiche Sendeleistungen mathematisch heraus, um die einzige Metrik zu isolieren, die wirklich zählt: die reine Hardwareeffizienz und Abstrahlcharakteristik deines Antennensystems.

<a id="sec-2"></a>
### 2. Key Use Cases und Capabilities (Anwendungsfaelle)

WSPRadar wurde entwickelt, um spezifische, häufige Fragestellungen im Amateurfunk präzise zu beantworten:
* **Path Viability & Skip Zones (Gibt es eine Öffnung?):** Erreicht mein Signal heute Ozeanien? Wo liegen meine toten Winkel? *(Gelöst durch Absolute Analysen für TX und RX).*
* **The "Am I doing okay?" Test (Lokales Benchmarking):** Ist meine Station im Vergleich zu anderen Funkern in meiner Region gut oder schlecht? *(Gelöst durch den Referenz-Radius-Benchmark).*
* **Buddy-Testing (Station vs. Station):** Mein Freund funkt 10 km weiter mit einer Yagi, ich mit einem Dipol. Wer ist heute besser? *(Gelöst durch den Vergleich gegen eine Spezifische Referenzstation mit synchroner Auswertung).*
* **The Hardware Laboratory (Echte A/B-Tests):** Ich brauche ein isoliertes Labor-Setup für Antenne A vs. B, RX vs. RX oder TX vs. TX am eigenen Standort. *(Gelöst durch den Hardware A/B-Test Modus).*
* **DX vs. NVIS Profiling (Take-Off Angle beurteilen):** Ist meine Antenne ein Flachstrahler (DX) oder ein Steilstrahler (NVIS)? *(Ablesbar an der Performance in den nahen vs. weiten Distanzringen der Karte).*
* **Uncovering Local QRM (Der "Alligator-Test"):** Werde ich weltweit gehört, höre aber selbst nichts? *(Beweisbar durch die Kombination eines TX- und RX-Vergleichslaufs gegen dieselbe Referenz).*
* **Statistical Proof vs. Guesswork:** Ist ein gemessener Vorteil von 2 dB physikalisch echt oder nur Zufall? *(Gelöst durch den integrierten Wilcoxon-Test zur Signifikanzprüfung).*

**💡 Quick Start:** Klicken Sie in der Konfiguration auf `✨ Load Demo Config` und anschließend auf `Run TX` oder `Run RX`, um das Tool direkt mit Beispieldaten zu testen. *(Hinweis: Die aktuellen Demo-Daten sind vorerst nur für den Radius-Benchmark ausgelegt und noch etwas spärlich. Umfassendere Demo-Datensätze folgen in Kürze).*

<a id="sec-3"></a>
### 3. Kern-Konzepte: Absolut vs. Vergleich

Um aus WSPR-Daten verlässliche Schlüsse zu ziehen, trennt WSPRadar die Analyse streng in zwei Betrachtungsweisen:

<a id="sec-3-1"></a>
#### Absolute Analysen (Die reine Ausbreitung)
Hierbei geht es um die Beantwortung der Frage "Gibt es einen offenen Ausbreitungsweg?". Da Ausbreitungsbedingungen oft asymmetrisch sind, generiert WSPRadar hierfür zwei strikt getrennte Betrachtungen:
* **TX Absolut:** *Wo wird mein gesendetes Signal gehört?* Isoliert alle Instanzen, in denen Sie senden, und plottet alle weltweiten **Empfangsstationen** auf der Karte. Misst die reine Sendefähigkeit und zeigt Ihre Skip-Zonen (normiert auf 1 Watt).
* **RX Absolut:** *Wen kann meine Station hören?* Isoliert alle Instanzen, in denen Sie empfangen, und plottet alle weltweiten **Sendestationen** auf der Karte. Misst die reine Empfangsempfindlichkeit und visualisiert offene Pfade zu Ihrem Standort (normiert basierend auf der gemeldeten Leistung des Senders).
  Beide Karten zeigen Ihre globalen toten Winkel. Wenn Sie wissen wollen, ob Ihr Signal heute Ozeanien erreicht (oder ob Sie Ozeanien hören können), betrachten Sie die Absolute Maps.
  
<a id="sec-3-2"></a>
#### Vergleichende Benchmark Analysen (Die Hardware-Differenz)
Hier wird die Frage "Bin ich besser als Setup B?" beantwortet. In der Compare-Map werden das lokale Störrauschen an der Gegenstation sowie das schnelle ionosphärische Fading (QSB) mathematisch *vollständig eliminiert*. Übrig bleibt ausschließlich die reine Differenz ($\Delta$ SNR) zwischen den zwei getesteten Hardware-Setups, aufgeschlüsselt nach geografischen Segmenten. Dies ist das ultimative Werkzeug für Leistungs-Benchmarking. 
* **Bei TX Vergleichen:** Beide Sendesignale werden durch denselben Remote-Empfänger bewertet. Dadurch werden lokales QRM des Remote-Empfängers und dessen Antennengewinn funktional herausgekürzt. Berechnung: $\Delta SNR_{TX} = SNR_{norm,target} - SNR_{norm,benchmark}$
* **Bei RX Vergleichen:** Beide lokalen Empfänger bewerten dasselbe ferne Sendesignal simultan. Dadurch sind die Leistung des fernen Senders und der grundlegende Ausbreitungsweg identisch. Jegliche Differenz ist strikt auf die eigene Empfangsantenne und das eigene lokale QRM zurückzuführen. Berechnung: $\Delta SNR_{RX} = SNR_{measured,target} - SNR_{measured,benchmark}$

<a id="sec-3-3"></a>
#### Das Bivariate Auswertungsmodell (Vermeidung von Survivorship Bias)
Verlässt man sich beim Vergleich zweier Setups ausschließlich auf die mediane SNR-Differenz ($\Delta$ SNR), führt dies unweigerlich zu einem statistischen Fehler namens 'Survivorship Bias'. Eine überlegene Antenne decodiert extrem schwache Signale an der Rauschgrenze, die ein schlechteres Setup völlig verpasst. Diese zusätzlichen, grenzwertigen Spots senken mathematisch den SNR-Median des besseren Setups und lassen es fälschlicherweise schlechter aussehen, wenn alles vermischt wird. WSPRadar löst dies durch ein striktes bivariates Modell:
1. **System Sensitivity (Yield / Ausbeute):** Analysiert die absolute Anzahl exklusiver vs. gemeinsamer (Joint) Decodes, um die tatsächliche Empfindlichkeit und Reichweite an der Rauschgrenze zu beweisen.
2. **Hardware Linearity ($\Delta$ SNR):** Wird *ausschließlich* für Joint Spots (Signale, die von beiden Setups zeitgleich im selben 2-Minuten-Fenster decodiert wurden) berechnet, um den reinen physikalischen Gain-Unterschied unter absolut identischen Ausbreitungsbedingungen zu beweisen.

<a id="sec-4"></a>
### 4. Methodik fuer vergleichende Analysen

WSPRadar bietet drei fundamentale Säulen für vergleichende Hardware-Tests, je nachdem, was Sie beweisen möchten. Ein A/B-Test ist physikalisch nur valide, wenn *alle* anderen Variablen identisch bleiben (z.B. Testen Sie Antenne A vs. B bei gleichem Sender, oder Sender A vs. B bei gleicher Antenne).

<a id="sec-4-1"></a>
#### Option 1: Lokales Umfeld (Nearest Peers / Radius-Benchmark)
* **Ziel:** Messung Ihrer Leistungsfähigkeit gegen die besten Stationen Ihrer direkten Nachbarschaft.
* **Methodik:** WSPRadar aggregiert die bis zu 25 nächstgelegenen lokalen WSPR-Stationen innerhalb eines definierten Radius (max. 250 km). Da angenommen wird, dass alle diese Stationen denselben Makro-Ausbreitungsbedingungen unterliegen, liefert Ihnen dies eine harte statistische Einordnung, ob Ihr QTH (Standort) oder Ihre Antenne über- oder unterdurchschnittlich abschneidet. Es wird dabei eine strikte *Cycle-by-Cycle (Spot-by-Spot)* Mathematik angewandt: In jedem einzelnen 2-Minuten-WSPR-Zyklus ermittelt die Engine dynamisch die "Best Peer" Referenzstation aus Ihrer lokalen Wolke – also exakt den Nachbarn, der in dieser Minute das beste SNR erzielt hat. Der Benchmark lautet: *"Wenn die beste Station in direkter Nachbarschaft diese DX-Station erreicht/gehört hat, wie gut warst du im direkten Vergleich?"* Dies simuliert eine "virtuelle Makro-Antenne" und ist der härteste und fairste Gradmesser.

<a id="sec-4-2"></a>
#### Option 2: Fremde Referenzstation (Buddy-Test)
* **Ziel:** Ein 1-zu-1 Vergleich mit einem bekannten Funkamateur (Standort vs. Standort, Antenne vs. Antenne, oder einfach Station vs. Station).
* **Methodik:** Sie definieren ein abweichendes Referenz-Rufzeichen (z.B. einen Funk-Freund in 10 km Entfernung). Da Sie beide unter unterschiedlichen Rufzeichen in der Luft sind, sammelt die Datenbank problemlos alle Spots. WSPRadar isoliert Instanzen, in denen beide Signale vom exakt selben Empfänger im exakt selben 2-Minuten-WSPR-Zyklus decodiert wurden. Auch hier eliminiert die *Spot-by-Spot (Synchronous)* Mathematik das Fading vollständig auf Bitebene.

<a id="sec-4-3"></a>
#### Option 3: Echter Hardware A/B-Test (Das eigene Setup)
* **Ziel:** Ein präziser Labor-Test der eigenen Hardware am eigenen Standort mit dem eigenen Rufzeichen. Dies geht weit über den klassischen Vergleich hinaus: Solange alle anderen Parameter identisch bleiben, können Sie hier jede beliebige Variable isoliert testen. Vergleichen Sie Empfänger gegen Empfänger (RX vs. RX), Transceiver gegen Transceiver (TX vs. TX), unterschiedliche Baluns/Speiseleitungen oder evaluieren Sie die exakte Aufbaustelle einer Antenne innerhalb desselben Grundstücks (Standort A vs. Standort B). WSPRadar spaltet sich hierfür je nach Test-Richtung in zwei spezielle Rechenpfade auf:
* **Der RX A/B-Test (Simultan):** Zwei parallel laufende Empfänger (SDRs) werten gleichzeitig WSPR-Signale aus. **Der Trick:** Damit das WSPR-Netzwerk die synchronen Spots Ihrer Empfänger nicht als Duplikate löscht, müssen Sie in Ihrer Empfangssoftware (z.B. WSPRdaemon) unterschiedliche Rufzeichen-Suffixe angeben. *➔ Anleitung zur Einrichtung dualer WSJT-X Instanzen in [Anhang A](#sec-a).*
  * **Setup A:** Meldet unter Ihrem Hauptrufzeichen (z. B. `DL1MKS`).
  * **Setup B:** Meldet mit einem spezifischen Suffix (z. B. `DL1MKS/P`).
  In WSPRadar geben Sie im Self-Test Modus diese beiden Rufzeichen an. Das Tool generiert dann via *Spot-by-Spot (Synchronous)* Mathematik exakte Joint-Spots für den ultimativen Hardware-Vergleich.
* **Der TX A/B-Test (Sequenziell / Time-Slicing):** Sie verwenden zwei identische WSPR-Sender oder einen Transceiver, der zeitgesteuert zwischen Antenne A und Antenne B umschaltet. Da Setup A und B *niemals* im selben Slot senden, nutzt WSPRadar die **Asynchronous Math (Time-Averaging)**: Es spaltet Ihre Daten anhand der Startminuten (Gerade: 00, 04, 08 / Ungerade: 02, 06, 10) auf und bildet Langzeit-Mediane, bevor das $\Delta$ SNR berechnet wird. *(Da Setup A und B niemals im selben Slot senden, kann es physikalisch keine simultanen 'Joint Spots'. Der Segment-Inspektor nutzt hierfür logischerweise die 'Async Both' Metrik für Zyklen-Schnittmengen in der Tabelle.)*
  * *Hinweis zur TX-Hardware:* Ein solcher Test erfordert Hardware, die deterministisch nach Zeitplan sendet. Ein QMX-Transceiver lässt sich beispielsweise exakt programmieren (`frame=10` sendet alle 10 Minuten, `start=2` beginnt exakt in Minute 2). Die Standard-Software WSJT-X sendet "out-of-the-box" zufällig (random) und ist ohne spezielle Zusatztools für zeitlich fixierte A/B-Tests nicht geeignet.
  * *Warum kein Multi-Cycle WSPR mit einem TX (Rufzeichen-Zusätze wie /1 oder /P)?* WSPR-Nachrichten mit Suffixen zwingen das Protokoll dazu, zyklusübergreifend zu senden (Typ 1 und Typ 3 Nachrichten). Da viele weltweite Empfangsstationen Typ 3 Nachrichten nicht sauber aus dem Rauschen decodieren können, sinkt die absolute Anzahl an weltweit geloggten Spots für Compound-Rufzeichen drastisch. Zudem sind künstliche Zusätze wie `/1` oder `/2` funkrechtlich keine zugelassenen Rufzeichenstrukturen, und die Nutzung von `/P` ist strikt nur bei tatsächlichem Portabel-Betrieb gestattet. Daher setzt WSPRadar beim eigenen TX A/B-Test exklusiv auf Time-Slicing mit dem *identischen* Standard-Rufzeichen und trennt die Signale mathematisch anhand der ungeraden/geraden Minuten auf, um 100 % der Dekodierleistung des globalen Netzwerks zu erhalten.

<a id="sec-5"></a>
### 5. Allgemeine Daten-Methodik

<a id="sec-5-1"></a>
#### 5.1 Leistungs-Normalisierung
Um einen direkten Vergleich zwischen Stationen mit unterschiedlichen Hardware-Setups zu ermöglichen, werden alle absoluten Signal-Rausch-Verhältnis (SNR) Daten auf eine Standardreferenz von 1 Watt (30 dBm) normalisiert. 
$$SNR_{norm} = SNR_{measured} - P_{TX(dBm)} + 30$$
Diese Normalisierung wird auf alle TX- und RX-Absolutanalysen angewendet, wodurch die Sendeleistung als unabhängige Variable eliminiert und die intrinsische Effizienz sowie der Abstrahlwinkel des Antennensystems isoliert werden.

<a id="sec-5-2"></a>
#### 5.2 Geografisches Rastering und Projektion
Räumliche Daten werden mithilfe einer mittabstandstreuen Azimutalprojektion (Azimuthal Equidistant) abgebildet, zentriert auf den Maidenhead-Locator des Benutzers. Die Render-Engine ist explizit auf eine perfekte mathematische Kugel (Radius = 6371 km) fixiert. Dies garantiert eine 100%ige geometrische Konsistenz zwischen den errechneten Distanzen der Datentabellen und der visuellen Platzierung auf der Karte (Vermeidung von WGS84-Ellipsoid-Verzerrungen).
* Die Karte ist in ein dynamisches Zonenmodell unterteilt, das konzentrische radiale Bänder von 2.500 km nutzt (was ungefähr einem typischen F2-Schicht-Hop entspricht).
* Azimutale Segmente werden in diskrete Kompass-Richtungen (z. B. 22.5° für N, NNE, NE) unterteilt, um der räumlichen Dichte Rechnung zu tragen.
* Jedes resultierende geografische Segment erhält einen eindeutigen Koordinaten-Identifikator für die Datenaggregation.

<a id="sec-5-3"></a>
#### 5.3 Raeumliche Normalisierung (Median-Aggregation)
Um räumliche Verzerrungen durch eine unverhältnismäßige Empfängerdichte in bestimmten Regionen abzuschwächen, verwendet das Tool eine zweistufige "Median des Medians"-Aggregation:
1. **Aggregationsstufe Station:** Der Median-SNR aller Spots wird für jede eindeutige Remote-Station berechnet.
2. **Aggregationsstufe Segment:** Der Median dieser Stationswerte wird berechnet, um den finalen Wert für das geografische Segment zu bestimmen. 
Diese Methode verhindert den "Receiver Density Bias" – bei dem dichte Empfänger-Cluster (z. B. in Europa oder Nordamerika) spärlich besiedelte Regionen (z. B. Asien oder Afrika) im globalen Durchschnitt statistisch übertönen. Jedes geografische Segment erhält eine faire, isolierte Bewertung, wodurch sichergestellt wird, dass eine einzelne, hochaktive Station eine Region nicht statistisch dominiert.

<a id="sec-5-4"></a>
#### 5.4 Temporaere Synchronisation (Heartbeat-Filter / Offline-Schutz)
Um zu verhindern, dass Ihr Setup unfaire Strafpunkte (Niederlagen) sammelt, während Ihr Funkgerät, die Software oder Ihr PC tatsächlich ausgeschaltet war, wendet WSPRadar in allen vergleichenden Modi einen systemweiten, strikten **Heartbeat-Filter** an. Ein 2-Minuten-Zyklus wird in der Vergleichsanalyse nur dann als gültig gewertet, wenn Ihr Setup in genau dieser Minute nachweislich "am Leben" (online) war. 

* **Im TX-Modus (Senden):** Sie müssen in diesem Zyklus von *mindestens einer* beliebigen Station weltweit gehört worden sein. Dies beweist, dass Ihr Transceiver in diesem Slot tatsächlich gesendet hat.
* **Im RX-Modus (Empfangen):** Ihr Empfänger muss in diesem Zyklus *mindestens eine* beliebige Station (lokal oder weltweit) decodiert haben. Dies beweist, dass Ihre Software lief und die Antenne angeschlossen war.

Dieser Mechanismus eliminiert die sogenannte **Offline-Strafe**. Wenn Sie nachts den Rechner ausschalten, sammelt Ihre Referenz-Wolke zwar weiterhin Tausende Spots, aber WSPRadar wertet diese nicht als Niederlagen für Ihre Antenne. Das garantiert eine hundertprozentig faire, physikalische Win/Loss-Ratio.

<a id="sec-6"></a>
### 6. Visuelle Interpretation und Segment-Inspektor

<a id="sec-6-1"></a>
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

<a id="sec-6-2"></a>
#### 6.2 Detaillierte Auswertung: Segment-Inspektor (Histogramm und Tabellen)
Direkt unter den Karten befindet sich der Segment-Inspektor mit zwei kaskadierenden Dropdowns. Hier können Sie gezielt eine Distanz und anschließend eine Himmelsrichtung (z.B. NNE) auswählen, um die zugrundeliegende Datenverteilung dieses Segments im Detail zu analysieren.
*Hinweis: Der Segment-Inspektor ist die direkte visuelle Umsetzung des bivariaten Auswertungsmodells aus **Kapitel 3**. Der Yield-Balken links zeigt die absolute Ausbeute (System Sensitivity), während das Histogramm rechts die reinen Gain-Differenzen (Hardware Linearity) anhand der Joint-Spots abbildet.*
1. **Absolute Modi:** Zeigt die Verteilung der normierten SNR-Werte (`Norm@1W`) aller Stationen in diesem Segment in Form eines diskreten Säulendiagramms. Die X-Achse zeigt dabei die individuellen *Station Medians*. Die rote gestrichelte Linie markiert den finalen *Segment Median*, der aus all diesen Werten gebildet wird.
2. **Compare Modi:** Zeigt die Verteilung der Δ SNR-Werte. Dies ist entscheidend, um zu beurteilen, ob ein knapper Medianwert durch eine konsistente Überlegenheit (enge Glockenkurve) oder durch extrem wilde Streuung zustande kam. Die X-Achse repräsentiert die individuellen *Station Medians* (die erste Aggregationsstufe). Die rote gestrichelte Linie markiert den final aggregierten *Segment Median* (den "Median des Medians" über alle Stationen dieses Segments).
3. **Station Insights Tabelle:** Unterhalb des Histogramms listet eine interaktive Datentabelle die exakten beteiligten Remote-Stationen für das ausgewählte Segment auf. Im Standardmodus werden hier zur Übersichtlichkeit nur Stationen mit erfolgreichen `Joint Spots` gelistet (Ausnahme: beim sequenziellen TX A/B-Test ist der Schalter für alle Spots standardmäßig aktiv). Die Spalte "Median Δ SNR" zeigt den zusammengeführten Wert für exakt diese eine Station. In vergleichenden Modi schlüsselt die Tabelle zudem auf, wie viele gemeinsame Decodierungen (`Joint Spots`) diesen Wert bilden und wie viele exklusive Decodierungen (`Nur Referenz` oder `Nur eigenes Rufzeichen`) vorliegen.
4. **Drill-Down Data (Rohdaten & Export):** Durch Anklicken einer Zeile in der "Station Insights" Tabelle öffnet sich die detaillierte Ansicht für diese spezifische Station. Hier wird jeder einzelne 2-Minuten-Zyklus (Spot) offengelegt. Im Compare-Modus sehen Sie hier die rohen Δ SNR-Werte der einzelnen Spots, deren Median exakt den "Station Median" aus der übergeordneten Tabelle bildet. In der Radius-Analyse finden Sie zudem die Spalten `Best Ref` und `Ref km`, welche exakt benennen, gegen welchen lokalen Nachbarn Sie in diesem speziellen Zyklus angetreten sind und wie viele Kilometer dieser von Ihnen entfernt war.
5. **Raw Spots Toggle & Async Both:** Über den Schalter "Show Non-Joint" können Sie die "Joint-Schutzwand" fallen lassen und auch komplett isolierte Decodierungen in der Tabelle einblenden. Für Zyklen, in denen Sie oder die Referenz taub blieben, zeigt die SNR-Spalte transparent `None` anstelle einer irreführenden `0.0`. Das System Sensitivity Bar-Chart (Yield) wird hierbei ebenfalls dynamisch erweitert: Gab es Stationen, die zwar von beiden Setups, jedoch niemals im selben 2-Minuten-Zyklus gehört wurden (z.B. aufgrund von Fading), erscheint der zusätzliche Balken `Async Both`.
Dank der Multi-Select-Funktion lassen sich per Shift-Klick mehrere Stationen gleichzeitig markieren, oder über die Checkbox im Tabellenkopf direkt *alle* Stationen des Segments auswählen. So generieren Sie im Handumdrehen ein vollständiges Raw-Data-Audit. Anstelle einfacher nativer Tools verfügen die interaktiven Tabellen über ein maßgeschneidertes, Excel-artiges dynamisches Filtersystem via `Filter` Button (Trichter-Icon). Dies erlaubt es, präzise numerische Slider oder Dropdown-Auswahlen sowohl auf die Master- als auch auf die Drill-Down-Tabelle anzuwenden. Über die native Toolbar (oben rechts bei Hover) können Sie den Datensatz weiterhin durchsuchen oder mit einem Klick als **CSV-Datei herunterladen** zur weiteren Analyse in Excel.

<a id="sec-7"></a>
### 7. Konfiguration und Parameter-Referenz

<a id="sec-7-1"></a>
#### 7.1 Core Parameters
* **Ziel-Rufzeichen & QTH Locator:** Identifies the primary station under evaluation and establishes the mathematical center (Maidenhead grid) for the Azimuthal Equidistant map projection.
* **Frequenzband & Zeitrahmen:** Specifies the frequency band and the temporal window (in hours or absolute dates) to extract the relevant spot data from the database.

<a id="sec-7-2"></a>
#### 7.2 Comparison against References and A/B Testing
* **Vergleichsmodus:** Wählt die grundlegende Art des Benchmarks aus (Referenz-Radius, Fremdes Rufzeichen oder Eigenes Setup).
* **Referenz-Suchradius (km):** Definiert die Distanzschranke zur Aggregation lokaler WSPR-Stationen beim Radius-Benchmark.
* **Referenz-Rufzeichen:** Das spezifische Rufzeichen der externen Gegenstation beim Buddy-Test.
* **Test-Setup (nur bei Hardware A/B-Test):** Schaltet zwischen `RX Test (2 Empfänger, Simultan)` und `TX Test (1 Sender, Time-Slicing)` um.
* **Target Locator & Referenz Locator:** Die exakten 6-stelligen Maidenhead-Locators (z.B. JN37AA vs. JN37AB) zur Trennung der Datenströme bei simultanen RX-Tests.
* **Target Zeit-Slot & Referenz Zeit-Slot:** Die Zuweisung der Sendezyklen (`Gerade Min` vs. `Ungerade Min`) bei sequenziellen TX-Tests.

<a id="sec-7-3"></a>
#### 7.3 Advanced Config und Expert Settings
* **Lokaler QTH Sonnenstand:** Um tageszeitabhängigen Veränderungen der Ionosphäre Rechnung zu tragen (z. B. D-Schicht Dämpfung am Tag vs. F2-Schicht Öffnung bei Nacht), nutzt WSPRadar die astronomische Bibliothek `ephem`. Der exakte Sonnen-Höhenwinkel wird für jeden WSPR-Spot passend zum QTH berechnet. Nutzer können die Daten gezielt nach `Daylight` (> +6°), `Nighttime` (< -6°) oder der magischen `Greyline` (Dämmerung zwischen -6° und +6°) filtern.
* **Exclude Prefixes:** Ein Textfeld für eine kommagetrennte Liste (z.B. "Q, 0, AG6NS"), um bestimmte Rufzeichen oder bekannte Telemetrie-Ballons ("Pico Balloons") kategorisch aus den Analysen auszuschließen.
* **Exclude Moving Stations:** Ein Schalter (standardmäßig inaktiv), der vollautomatisch alle Gegenstationen (Ballons, maritime Stationen `/MM`, mobile Autos `/M`) herausfiltert, die innerhalb des Analysezeitraums ihren 4-stelligen Grid-Locator (Planquadrat) verändern. Dies eliminiert statistisches Rauschen, das durch "Jetstream-Nomaden" bei der Messung von stationären Antennen entstehen.
* **Kartenbereich (Max. Distanz):** Legt den visuellen Zoom-Faktor der Kartendarstellung (in Kilometern) vom Zentrum fest. Hilfreich, um regionale Ausbreitungen besser zu untersuchen.
* **Min. Spots/Station (Datenrobustheit):** Um die Auswertung robust gegen Rauschen und Datenartefakte zu machen, verhindert dieser Filter, dass zufällige Einzeldekodierungen ("One-Hit-Wonders") die Ergebnisse verzerren. Die Filter-Philosophie passt sich automatisch an den gewählten Vergleichsmodus an:
  * **Buddy & A/B-Test Modus (Strenger Symmetrischer Filter):** In direkten 1:1 Vergleichen wirkt der Filter streng und symmetrisch. Eine Station wird nur dann als *'Joint'* (Gemeinsam) gewertet, wenn sie das Spot-Minimum für BEIDE Setups zwingend und unabhängig erfüllt (Simultan: X gemeinsame Zyklen. Sequentiell: X valide Spots pro Setup). Für exklusive Empfänge (Nur Setup A/B) muss das jeweilige Setup mindestens X Spots eigenständig sammeln. Stationen, die diese Schwellenwerte verfehlen, werden kategorisch ausgeschlossen, was die Hardware-Linearitätsberechnung (SNR-Delta) vor Verzerrungen schützt.
  * **Radius Modus (Virtuelle Makro-Antenne):** Beim Vergleich gegen einen geografischen Radius agieren die Referenzstationen kollektiv als eine einzige 'Virtuelle Makro-Antenne'. Der Filter prüft hier, ob die *aggregierte Summe* der Spots aller Referenzstationen in diesem Radius den Schwellenwert für einen Remote-Peer erreicht. Dies validiert das regionale Ausbreitungspotenzial (es beweist, dass ein Pfad offen ist), ohne dass eine einzelne offline gegangene oder schwache Referenzstation einen ansonsten validen Ausbreitungspfad disqualifiziert.
* **Compare Map Statistische Signifikanz (Wilcoxon Test):** Anstatt sich blind auf den Median der Δ SNR zu verlassen, erlaubt WSPRadar die Prüfung echter statistischer Signifikanz bei Vergleichskarten (Compare). Wird der Wilcoxon-Test aktiviert, überschreibt das Tool den Basiswert der "Min. Stationen" für Vergleichskarten bei Bedarf dynamisch nach oben (auf bis zu 8 Stationen), um die mathematischen Mindestanforderungen des Tests für das gewählte Konfidenzniveau zu erfüllen. Segmente, die den p-Wert Test nicht bestehen, werden rigoros verworfen.

<a id="sec-8"></a>
### 8. Diskussion, Limitationen und Haftungsausschluss

#### Diskussion
WSPRadar überführt anekdotische Amateurfunk-Rapporte in einen rein datengestützten, quantitativen Ansatz. Durch die strikte zeitliche und räumliche Synchronisation der Spots (insbesondere im Compare-Modus) gelingt es dem Tool, die unberechenbaren Einflüsse der Ionosphäre (QSB) und unterschiedliche lokale Rauschpegel (QRM) herauszukürzen. Dies ermöglicht eine objektive Leistungsbewertung der Antennen-Hardware im realen Betrieb, die sonst nur mit extrem teurem, kalibrierten Messequipment oder Drohnenflügen möglich wäre.

#### Limitationen
* **Performance Limits & Data Latency:** Um Server-Ressourcen zu schonen, ist der abfragbare Zeitraum auf 7 Tage begrenzt und Zeitabfragen werden zur Optimierung des globalen Cachings auf 15-Minuten-Intervalle quantisiert. Zudem hat die globale wspr.live Datenbank eine natürliche Aggregations-Latenz von ca. 15 bis 30 Minuten, bis brandneue Spots nach dem Senden im Tool sichtbar werden.
* **Verfügbarkeit vs. Uptime:** WSPR protokolliert systembedingt nur erfolgreiche Decodierungen. Der absolute Median-SNR spiegelt daher die Signalstärke *während eines offenen Ausbreitungsweges* wider. Geschlossene Bänder (Dead Bands) senken den Durchschnitt nicht.
* **Die TX-Power-Kalibrierungsfalle:** WSPRadar ist anfällig für fehlerhaft gemeldete Sendeleistungen ("Garbage In, Garbage Out"). Die Normalisierungsformel geht davon aus, dass die im WSPR-Paket gemeldete Leistung exakt der am Speisepunkt abgestrahlten Leistung entspricht. Wenn ein Transceiver bei schlechtem SWR automatisch die Leistung drosselt oder hohe Verluste im Speisekabel auftreten, sinkt das berechnete $SNR_{norm}$. Betreiber, die strenge A/B-Tests durchführen, müssen ihre reale Ausgangsleistung physisch mit einem Wattmeter kalibrieren.
* **Polarisation:** WSPRadar misst nicht den isolierten Freiraumgewinn einer Antenne, sondern die reale Systemeffizienz. Diese beinhaltet auch das Polarisations-Matching unter echten Ausbreitungsbedingungen, da die Ionosphäre die Signale durch die Faraday-Rotation beeinflusst.

#### Haftungsausschluss (Disclaimer)
WSPRadar ist ein experimentelles Open-Source-Projekt (Beta) und wird "wie besehen" (as is) ohne jegliche Gewährleistung bereitgestellt. Der Quellcode und die mathematischen Modelle sind öffentlich einsehbar und überprüfbar. Dennoch übernimmt der Entwickler **keinerlei Garantie oder Haftung** für die Richtigkeit, Vollständigkeit oder Zuverlässigkeit der generierten Daten und Grafiken.
Die Ergebnisse basieren auf Nutzerdaten einer Drittanbieter-Schnittstelle (wspr.live), welche durch fehlerhafte Kalibrierung (z. B. falsch gemeldete TX-Leistungen) verfälscht sein können. **Nutzer sollten niemals finanzielle Entscheidungen (wie den Kauf oder Verkauf von teurer Funk- oder Antennen-Hardware) ausschließlich auf Basis dieses Tools treffen.** Die Nutzung erfolgt vollständig auf eigene Gefahr.

#### Lizenz (Open Source)
WSPRadar ist freie Software: Sie können sie unter den Bedingungen der GNU Affero General Public License (AGPLv3), wie von der Free Software Foundation veröffentlicht, weitergeben und/oder modifizieren. Diese Lizenz garantiert, dass der Quellcode – auch bei Netzwerk-Nutzung (SaaS) und nach Modifikationen – für die Amateurfunk-Community immer frei und offen verfügbar bleiben muss.

<a id="sec-a"></a>
### Anhang A: Setup: Paralleler Betrieb multipler WSJT-X Instanzen

Diese Anleitung beschreibt die Erzeugung einer zweiten OS-isolierten WSJT-X Umgebung (z.B. für einen SDR) inklusive Migration der bestehenden Konfiguration und zwingend erforderlicher Pfad-Trennung.

#### 1. Instanziierung (OS-Level Isolation)
Standardmäßig blockiert das WSJT-X Lock-File mehrfache Ausführungen. Die Trennung erfolgt über einen Command-Line-Parameter, der eine neue Sandbox im Windows `AppData`-Verzeichnis erzwingt.

1. Erstellen Sie eine Desktop-Verknüpfung der `wsjtx.exe`.
2. Öffnen Sie die **Eigenschaften** der Verknüpfung.
3. Modifizieren Sie das Feld **Ziel** exakt nach folgendem Syntax-Muster (Parameter außerhalb der Anführungszeichen):
   `"C:\Program Files\wsjtx\bin\wsjtx.exe" --rig-name=SDR`
4. Start dieses Verknüpfung **einmalig** und schließen Sie das Programm sofort wieder. Dadurch wird die neue Verzeichnisstruktur (`%LOCALAPPDATA%\WSJT-X - SDR`) initialisiert.

#### 2. Konfigurations-Migration (Klonen)
WSJT-X bietet keinen internen Export für Instanzen. Der Klon-Vorgang muss auf Dateisystemebene erfolgen.

1. Navigieren Sie in den primären Konfigurationsordner: `%LOCALAPPDATA%\WSJT-X`
2. Kopieren Sie die Hauptkonfigurationsdatei `WSJT-X.ini`.
3. Navigieren Sie in den neuen Ordner: `%LOCALAPPDATA%\WSJT-X - SDR`
4. Fügen Sie die Datei ein und überschreiben/ersetzen Sie die dort vom Erststart generierte `.ini`-Datei.
5. **Wichtig:** Benennen Sie die eingefügte Datei exakt passend zur neuen Instanz um: `WSJT-X - SDR.ini`

#### 3. Zwingende Pfad-Separation (Audio & Speicherorte)
Da die Konfiguration 1:1 geklont wurde, greifen nun beide Instanzen auf dieselben Hardware-Inputs und temporären Speicherdirectories zu. Dies führt bei WSPR zwingend zu identischen Dekodierungen (da dieselbe `.wav` analysiert wird) und potenziellen File-Lock-Fehlern.

Öffnen Sie die neue SDR-Instanz, navigieren Sie zu **File > Settings > Audio** und passen Sie folgende Parameter an:

* **Soundcard > Input:** Ändern Sie das Audio-Interface auf die spezifische Quelle des zweiten Empfängers (z.B. ein dediziertes Virtual Audio Cable).
* **Save Directory:** Ändern Sie den Pfad zwingend in die isolierte Umgebung, z.B.:
   `C:\Users\[User]\AppData\Local\WSJT-X - SDR\save`
* **AzEl Directory:** Ändern Sie auch diesen Pfad ab, um parallele Schreibzugriffe auf die `azel.dat` zu verhindern, z.B.:
   `C:\Users\[User]\AppData\Local\WSJT-X - SDR`

Nach einem Neustart der Instanz sind Datenströme, Hardwarezugriffe und temporäre WSPR-Dateien (WAV-Files) vollständig physikalisch voneinander getrennt.

"""