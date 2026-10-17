<!-- section: hero -->
# #2 Prof. Griffiths (G3ZIL) et al. RX-Vergleich: Umkehr des SNR-Vorteils zwischen Tag und Nacht: Niedrig aufgehängter Dipol gegen Vertikalantenne

Ein **Joint Spot** entsteht, wenn beide Empfänger denselben Sender im selben zweiminütigen WSPR-Zyklus melden, sodass wir ihre SNR-Werte zur selben Zeit vergleichen können.

<!-- section: setup -->
## Diesen Aufbau nachvollziehen

Wähle ‚In WSPRadar App starten‘, um diese Demo zu laden und ihre Analyse zu starten.

<!-- section: step-1 -->
## Die Vergleichsrichtung beibehalten

Dieses Beispiel verwendet wie Demo #1 die Differenz **G3ZIL − G4HZX**, begrenzt die Beobachtungen jedoch auf den **5.–7. April 2017**. Positive Werte sprechen für die Empfangsstation mit dem niedrig aufgehängten Dipol, negative für die Station mit der Vertikalantenne. Lasse zunächst alle Richtungen und Entfernungen ausgewählt, damit die erste Ansicht zur übergreifenden Frage der Demo passt.

<!-- section: step-2 -->
## Das Tagesmuster nach UTC-Stunde lesen

Öffne **Segment-Inspektor → Zeitliche Evidenz → Δ SNR nach UTC-Stunde (1-h-Bins)**. Jedes Stundenintervall fasst Beobachtungen aus dieser Stunde an allen drei Tagen zusammen. Folge den Stundenmedianen über die Nulllinie: Auf den Vorteil von G4HZX in den frühen Stunden folgt später am Tag ein Vorteil von G3ZIL. Die Farben beschreiben Konzentrationen von Beobachtungen, das schattierte Band deren mittlere 50 %. Beides bedeutet nicht, dass jede Aussendung dem Median folgt.

<!-- section: step-3 -->
## UTC-Stunden und zeitlichen Verlauf vergleichen

Untersuche nun **Δ SNR im Zeitverlauf**. Das Zusammenfassen nach UTC-Stunde macht ein wiederkehrendes Tagesmuster sichtbar, verdeckt aber, von welchem Datum eine Beobachtung stammt. Die chronologische Darstellung zeigt diese Unterscheidung wieder. Vergleiche die drei Tage, bevor du annimmst, dass die zusammengefasste Form jeden Tag gleichermaßen beschreibt. Prüfe anschließend in **Station Insights**, ob ein ausgewählter Sender diesem Muster folgt.

<!-- section: step-4 -->
## Die Vergleichspanels mit ihren Grenzen lesen

Vergleiche die Originalpublikation mit der Rekonstruktion und der nativen WSPRadar-Ansicht. Ihre Dichtedarstellungen sind keine identischen statistischen Darstellungen. Lies Anmerkungen, beschriftete Achsen und Farbskalen jedes Panels, statt Übereinstimmung allein anhand der Farben zu beurteilen. Das Beispiel ermöglicht die Untersuchung einer Tag-Nacht-Umkehr im relativen Empfang; es isoliert weder Antenne noch Störpegel oder Ausbreitung als Ursache.
