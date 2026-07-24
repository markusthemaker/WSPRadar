# Stability removal and evidence-control labels

## Scope

This change removes the discontinued branded 90% bootstrap Stability feature
from the active English and German manuals. It preserves the useful guidance
about breadth, internal consistency, controlled repetition, distributions and
calibration limits without describing an interval the application no longer
calculates or displays.

The same change renames `Show Non-Joint` to `Include Unpaired Evidence` and
`Ungepaarte Evidenz einbeziehen`, clarifies that the control includes exclusive
or asynchronous evidence, and names the adaptive Segment Compare control
`Time aggregation bin size:` / `Zeitliche Aggregationsbreite:`.

## Removed Stability passages

### Section 0.0 — feature framing

Original English sentence not retained:

> Its descriptive <strong class="defined-term">Stability</strong> check describes a displayed median's sensitivity to resampling the evidence available in one run.

Original German sentence not retained:

> Seine deskriptive <strong class="defined-term">Stability</strong>-Prüfung beschreibt die Empfindlichkeit eines angezeigten Medians gegenüber erneutem Ziehen aus der in einem Lauf verfügbaren Evidenz.

Disposition: obsolete feature framing removed. The surrounding scientific
lineage and current WSPRadar capabilities remain unchanged.

### Section 0.3 — strong-result framing

Original English passage replaced:

> A strong result is one in which the run definition, station breadth, observation volume, geographic and time pattern, descriptive Stability and underlying rows are mutually consistent and support the same bounded interpretation. Repeating the same design across another suitable window can show whether that interpretation persists.

Original German passage replaced:

> Ein belastbares Ergebnis liegt vor, wenn Laufdefinition, Breite der Stationsbasis, Beobachtungsumfang, räumliches und zeitliches Muster, deskriptive Stability und die zugrunde liegenden Datenzeilen miteinander vereinbar sind und dieselbe klar begrenzte Interpretation stützen. Die Wiederholung desselben Designs in einem weiteren geeigneten Zeitfenster kann zeigen, ob diese Interpretation Bestand hat.

Disposition: the obsolete Stability dimension was removed. Breadth, time and
geographic patterns, row-level consistency, bounded interpretation and
repetition remain.

### Section 3.1 — bootstrap explanation

Original English heading not retained:

> #### 3.1 Judge breadth, Stability and repeatability

Original German heading not retained:

> #### 3.1 Breite, Stability und Wiederholbarkeit beurteilen

Original English passages not retained:

> <strong class="defined-term">90% Stability</strong> is a descriptive bootstrap interval around a median. A narrow interval means the displayed median changes little when the available values are resampled. Use it to describe sensitivity to the observed sample. It is not a confidence interval or statistical significance test, and it does not establish independence or eliminate data bias.
>
> **Sample Stability and experimental repeatability are different.** The Stability interval resamples evidence already present in this run. Repeating the experiment in another suitable window tests whether the observed pattern persists under new operating and propagation conditions.

Original German passages not retained:

> <strong class="defined-term">90% Stability</strong> ist ein deskriptives Bootstrap-Intervall um einen Median. Ein schmales Intervall bedeutet, dass sich der angezeigte Median beim wiederholten Ziehen aus den verfügbaren Werten nur wenig ändert. Nutze es, um die Empfindlichkeit gegenüber der beobachteten Stichprobe zu beschreiben. Es ist weder ein Konfidenzintervall noch ein Test auf statistische Signifikanz und weist weder Unabhängigkeit nach noch beseitigt es Datenverzerrungen.
>
> **Stability der Stichprobe und experimentelle Wiederholbarkeit sind verschieden.** Das Stability-Intervall zieht erneut aus der Evidenz, die bereits in diesem Lauf vorhanden ist. Eine Wiederholung des Versuchs in einem weiteren geeigneten Zeitfenster prüft, ob das beobachtete Muster unter neuen Betriebs- und Ausbreitungsbedingungen Bestand hat.

Disposition: obsolete bootstrap mechanics removed. The useful distinction is
retained in neutral form: agreement among views describes internal consistency
within one run, while a new controlled window tests experimental
repeatability. The section and Table of Contents now name breadth, consistency
and repeatability.

### Section 6.5 — feature inventory

Original English list item not retained:

> * evidence thresholds, station-versus-observation diagnostics and descriptive Stability checks;

Original German list item not retained:

> * Evidenzschwellen, vergleichende Diagnosen auf Stations- und Beobachtungsebene sowie deskriptive Stability-Prüfungen;

Disposition: the discontinued feature was removed from the inventory.
Evidence thresholds and station-versus-observation diagnostics remain.

### Section 7.8 — bootstrap method

Original English heading and passages not retained:

> #### 7.8 Stability, distributions and inspection-layer weighting
>
> WSPRadar uses a deterministic 500-resample percentile bootstrap with replacement and reports the central 90% interval around the median. Station-level intervals resample station medians. Raw paired intervals resample peer-cycle or scheduled-pair Delta values.
>
> The calculation treats values as exchangeable even though WSPR observations can remain correlated by station, time and geography. It is a descriptive **Stability** interval, not a confidence interval or significance test.

Original German heading and passages not retained:

> #### 7.8 Stabilität, Verteilungen und Gewichtung in der Inspektionsansicht
>
> WSPRadar verwendet ein deterministisches Perzentil-Bootstrap mit 500 Stichprobenziehungen mit Zurücklegen und gibt das zentrale 90-%-Intervall um den Median an. Intervalle auf Stationsebene ziehen neue Stichproben aus den Stationsmedianen. Intervalle aus den Rohpaaren ziehen neue Stichproben aus den Delta-Werten der Peer-Zyklen oder geplanten Paare.
>
> Die Berechnung behandelt die Werte als austauschbar, obwohl WSPR-Beobachtungen nach Station, Zeit und Geografie korreliert sein können. Es handelt sich um ein deskriptives **Stability**-Intervall, nicht um ein Konfidenzintervall oder einen Signifikanztest.

Disposition: obsolete scientific mechanics removed. Section 7.8 remains the
authoritative home for distributions and inspection-layer weighting.

Original English raw-dB passage replaced:

> The transform does not change scientific values or grouping. Histogram counts and bin edges remain in raw dB, temporal cells remain rounded integer-dB bins, medians and Stability intervals remain raw-dB statistics, and relative-density colors retain the calculation above. Because nonlinear vertical stretching gives equal raw-dB histogram bins unequal displayed heights, read histogram **bar length** against `Share (%)`; displayed bar area is not probability. Success SNR figures remain linear.

Original German raw-dB passage replaced:

> Die Transformation verändert weder wissenschaftliche Werte noch Gruppierungen. Anzahlen und Klassengrenzen der Histogramme bleiben in untransformierten dB-Werten, die Zeitzellen bleiben auf ganzzahlige dB gerundete Klassen, Mediane und Stability-Intervalle bleiben Statistiken aus untransformierten dB-Werten, und die Farben der relativen Dichte behalten die oben angegebene Berechnung bei. Weil die nichtlineare vertikale Streckung gleich breiten Roh-dB-Klassen im Histogramm unterschiedliche dargestellte Höhen gibt, ist die **Balkenlänge** auf der Achse `Share (%)` abzulesen; die dargestellte Balkenfläche ist keine Wahrscheinlichkeit. Success-SNR-Diagramme bleiben linear.

Disposition: only the obsolete interval reference was removed. The raw-dB,
nonlinear-axis and density-color interpretation remains.

### Sections 8.1 and 8.3 — claim and reporting language

Original English claim example not retained:

> | "A is statistically significantly better." | "The paired median favored A and its descriptive 90% Stability interval was [range]; no significance test was performed." |

Original German claim example not retained:

> | "A ist statistisch signifikant besser." | "Der gepaarte Median begünstigte A; das deskriptive 90-%-Stability-Intervall betrug [Bereich]. Ein Signifikanztest wurde nicht durchgeführt." |

Disposition: rewritten to report the paired median for the documented evidence
and scope while retaining the explicit warning that no significance test was
performed.

Original English reporting item not retained:

> * for Compare, joint-station and joint-spot or pair counts, station-level median Delta SNR and its 90% Stability interval;

Original German reporting item not retained:

> * bei Compare die Anzahl der Joint-Stationen und Joint-Spots beziehungsweise -Paare, den Median des Delta SNR auf Stationsebene und sein 90-%-Stability-Intervall;

Disposition: the interval requirement was removed. Counts and the
station-level median remain required reporting evidence.

### Appendix C — calibration consistency

Original English passages replaced:

> 5. **Check stability:** inspect by station, time and SNR. One constant is not defensible if offset changes with level, frequency, AGC or time.
>
> A narrow Stability interval indicates repeatability of the available sample, not traceable laboratory accuracy. Splitter loss, mismatch, coupling and source instability can remain.

Original German passages replaced:

> 5. **Stabilität prüfen:** Nach Station, Zeit und SNR untersuchen. Ein konstanter Wert ist nicht vertretbar, wenn sich der Offset mit Pegel, Frequenz, AGC oder Zeit ändert.
>
> Ein schmales Stability-Intervall zeigt die Wiederholbarkeit der verfügbaren Stichprobe und keine rückführbare Laborgenauigkeit. Verteilerverlust, Fehlanpassung, Kopplung und Instabilität der Quelle können bestehen bleiben.

Disposition: the procedure now asks the operator to check consistency across
station, time and SNR views. It retains the constant-offset limitation and the
warning that this does not establish traceable laboratory accuracy.

## Renamed evidence controls

### `Show Non-Joint`

Original English control passages replaced:

> Simultaneous TX Hardware A/B compares two deliberately synchronized, distinguishable WSPR signals at each remote receiver. Delta SNR is calculated only when that receiver decodes both the Target and Reference in the same UTC cycle. The standard Decode Outcomes also retain Target-only, Reference-only and asynchronous evidence; `Show Non-Joint` controls whether stations without qualifying joint evidence are included in the inspection view. One UTC cycle can therefore be joint at one receiver and one-sided at another.
>
> Select one or multiple stations to open the selected station evidence view. `Station Insights` lists the `callsign + locator` identities contributing to the selected segment; Compare rows show joint and exclusive evidence plus station-level median Delta SNR, and `Show Non-Joint` includes identities without qualifying paired evidence. Below the station table, a Delta SNR histogram appears next to either a `Chronological` time plot or the date-folded `UTC-Hour` plot. These plots use the selected joint spots or scheduled pairs; the `UTC-Hour` view requires evidence from at least two distinct UTC dates. If multiple stations are selected, their aggregated evidence is visualized together. The histogram and active time plot use the median of the selected evidence, not the segment median above.
>
> - `Show Non-Joint` restores Compare identities represented only by exclusive or asynchronous evidence. Its durable value is saved when Compare applies.

Original German control passages replaced:

> Beim simultanen TX Hardware A/B-Test werden an jedem entfernten Empfänger zwei bewusst synchronisierte und unterscheidbare WSPR-Signale verglichen. Delta SNR wird nur berechnet, wenn dieser Empfänger Target und Referenz im selben UTC-Zyklus decodiert. Die regulären Decode Outcomes erhalten außerdem Target-only-, Reference-only- und asynchrone Evidenz; `Show Non-Joint` steuert, ob Stationen ohne qualifizierende gemeinsame Evidenz in die Inspektionsansicht einbezogen werden. Derselbe UTC-Zyklus kann daher an einem Empfänger joint und an einem anderen einseitig sein.
>
> Wähle eine oder mehrere Stationen aus, um die Evidenzansicht für diese Auswahl zu öffnen. `Station Insights` listet die Identitäten `callsign + locator` auf, die zum ausgewählten Segment beitragen. Compare-Zeilen zeigen Joint- und exklusive Evidenz sowie das stationsbezogene mediane Delta SNR; `Show Non-Joint` schließt Identitäten ohne qualifizierende gepaarte Evidenz ein. Unter der Stationstabelle erscheint ein Delta-SNR-Histogramm neben einem der beiden Zeitdiagramme: `Chronologisch` oder dem nach Datum gefalteten Diagramm `UTC-Stunde`. Diese Diagramme verwenden die ausgewählten Joint Spots oder geplanten Paare; die Ansicht `UTC-Stunde` erfordert Evidenz von mindestens zwei verschiedenen UTC-Tagen. Bei Auswahl mehrerer Stationen wird ihre aggregierte Evidenz gemeinsam dargestellt. Das Histogramm und das aktive Zeitdiagramm verwenden den Median der ausgewählten Evidenz, nicht den darüber angezeigten Segmentmedian.
>
> - `Show Non-Joint` stellt Compare-Identitäten wieder dar, die ausschließlich durch exklusive oder asynchrone Evidenz vertreten sind. Der dauerhafte Wert wird gespeichert, wenn ein Compare-Ergebnis vorhanden ist.

Disposition: UI wording updated in place. All existing interpretation,
selection and persistence guidance remains, and the replacement wording now
states explicitly that unpaired evidence includes exclusive or asynchronous
evidence.

Original English generic view-control passages replaced:

> | **View controls** | Which completed evidence is displayed or inspected, without changing the retained analysis population. These include selected Inspector segment, selected stations, non-joint or zero-Target visibility, temporal view and evidence time bin. | Segment Inspector range/direction and the applicable durable Compare/Success result-view choices are saved. Inspector choices can narrow the completed geographic scope but cannot override it. Table filters and other incidental interactions remain transient. |
>
> * **durable result-view settings:** selected ranges and directions, selected stations, evidence time bins and temporal view, and visibility of non-joint or zero-Target evidence.

Original German generic view-control passages replaced:

> | **Ansichtsbedienelemente** | Welche abgeschlossene Evidenz dargestellt oder untersucht wird, ohne die beibehaltene Analysepopulation zu verändern. Dazu gehören ausgewähltes Inspector-Segment, ausgewählte Stationen, Sichtbarkeit von Non-Joint- beziehungsweise Zero-Target-Evidenz, Zeitansicht und Zeit-Bin der Evidenz. | Bereich/Richtung im Segment Inspector und die jeweils anwendbaren dauerhaften Compare-/Success-Ansichten werden gespeichert. Inspector-Auswahlen können den abgeschlossenen geografischen Umfang eingrenzen, ihn aber nicht überschreiben. Tabellenfilter und weitere beiläufige Interaktionen bleiben flüchtig. |
>
> * **dauerhafte Einstellungen der Ergebnisansicht:** ausgewählte Entfernungs- und Richtungsbereiche, ausgewählte Stationen, Evidenz-Zeitklassen und Zeitansicht sowie die Sichtbarkeit nicht gemeinsamer Evidenz oder von Evidenz ohne Target-Beobachtung.

Disposition: only the generic terminology changed from non-joint to unpaired.
The view-versus-scientific boundary and saved-state behavior are unchanged.

### Segment Compare time-bin control

Original English control passage replaced:

> - The Segment Compare time-bin buttons change only the left segment-level temporal panel. The control does not change the dates-folded UTC-hour panel, the selected-station timeline, pairing or analysis; its selected bin is stored independently in `.config`.

Original German control passage replaced:

> - Die Zeit-Bin-Schaltflächen für Segment Compare verändern nur das linke Zeitpanel auf Segmentebene. Das nach UTC-Stunden gefaltete Panel, die Zeitachse der ausgewählten Stationen, Paarbildung und Analyse bleiben unverändert; das gewählte Bin wird unabhängig in `.config` gespeichert.

Disposition: the existing scope and persistence semantics remain. The
replacement adds the exact control label, its location under Temporal Evidence,
and the fact that available minute/hour choices adapt to the run duration.
