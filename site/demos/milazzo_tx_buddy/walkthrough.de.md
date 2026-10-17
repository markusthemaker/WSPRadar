<!-- section: hero -->
# #7 Dr. Milazzo neu betrachtet: Erweiterung einer frühen mehrteiligen WSPR-Antennenstudie um zyklusgleiche Evidenz

<!-- section: setup -->
## Diesen Aufbau nachvollziehen

Wähle ‚In WSPRadar App starten‘, um diese Demo zu laden und ihre Analyse zu starten.

<!-- section: step-1 -->
## Mit dem installierten RX-Rundgang beginnen

Die installierte Demo startet in **RX Benchmark** mit **KP4MD als Target** und **WB6RQN als Referenz**. Ihr Hauptrundgang greift Abbildung 6 auf und untersucht empfangene Aussendungen von VE6PDQ. Lies den ausdrücklichen Hinweis zur Richtungskorrektur im Vergleich: Archivierte Endpunktidentitäten widersprechen der in der Originalabbildung gedruckten Richtung. Halte den RX-Rundgang vom optionalen TX-Anschlussbeispiel zu Abbildung 7 getrennt.

Ein **Joint Spot** entsteht, wenn beide Empfänger denselben Sender im selben zweiminütigen WSPR-Zyklus melden, sodass wir ihre SNR-Werte zur selben Zeit vergleichen können.

<!-- section: step-2 -->
## Die vollständigen Locatoridentitäten getrennt halten

Untersuche in **Station Insights** die vorausgewählte Identität **VE6PDQ (DO34IR)** mit drei Joint Spots. Wähle anschließend **VE6PDQ (DO34)** für die beiden weiteren aus. Das gemeinsame Rufzeichen führt diese gemeldeten Identitäten nicht zusammen. Berichte aus demselben Zyklus mit unterschiedlichen vollständigen Senderlocatoren bilden keinen Joint Spot; eine visuelle Zusammenfassung würde diese Evidenzregel verdecken.

<!-- section: step-3 -->
## Ein Paar durch die Panels verfolgen

Nutze das Beispiel vom **19. Dezember, 14:46 UTC**, um ursprüngliche Berichtswerte, Rekonstruktion und gepaarte Differenz zu verbinden. Aus **+2 dB** bei KP4MD und **−6 dB** bei WB6RQN, jeweils bei 5 W, werden auf der gemeinsamen 1-W-Skala **−5 dB** und **−13 dB**. Die Differenz bleibt **+8 dB**. Die blassen Hilfslinien verbinden zulässige Endpunkte desselben Zyklus mit vollständiger Locatorübereinstimmung; sie sind keine interpolierten Beobachtungen.

<!-- section: step-4 -->
## Mit dem optionalen TX-Vergleich fortfahren

Wechsle für Abbildung 7 die **Analyserichtung** zu **TX** und behalte Stationen, Datum, Band und Entfernungsgrenze bei. Der Empfänger VE6PDQ bildet nun den ausgewählten entfernten Funkweg. Dort bleibt nur ein Joint Spot erhalten, während die breitere TX-Konfiguration 45 Joint-Beobachtungen über 30 Empfänger enthält. Lies vor der Deutung dieser gepaarten Differenz das Beispiel zur Leistungsnormalisierung vom **20. Dezember, 00:22 UTC**, in der ursprünglichen Beschreibung.

<!-- section: step-5 -->
## Grafische Übereinstimmung von gepaarter Evidenz trennen

Die zahlreichen rekonstruierten Publikationsmarkierungen und die deutlich kleinere Teilmenge der zyklusgleichen Paare beantworten unterschiedliche Validierungsfragen. Ungleiche Sendezeitpläne und das **Target-Active Gate** beeinflussen außerdem die nicht gemeinsamen Beobachtungszahlen. Verfolge Originalbild, Rekonstruktion und native Evidenz, um zu sehen, welche Beobachtungen die jeweiligen Regeln erfüllen. Dieses Beispiel eignet sich besonders für eine manuelle Evidenzprüfung; wenige Paare und Stationsunterschiede begrenzen weitergehende Antennenschlüsse.
