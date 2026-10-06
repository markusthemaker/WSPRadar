# Section 8.4: concise analysis export guide

## Authorization and accepted source model

On 2026-10-06 the user approved reducing Section 8.4 to one artifact/content table, a short introduction and a closing reproducibility note. The approved proposal removes the directory tree, repeated filename and field inventories, and the second technical-contract table, while preserving practical scope, provenance and conditional-file distinctions. It also updates inbound references to the removed table. No runtime or export contract changes are authorized or made.

This is a parallel bilingual edit of the working-tree manuals on base commit `8683fdd9d0349300584e887d62b1f0291aa97034`. The working tree already contains the approved Section 1.1 Appendix B.4 link and TX-only contributor guidance; both are preserved.

Starting file SHA-256: EN `56bacae75a48416b10ec983f31206a72b3fc4bbb4b38a8e2740040179364e5a6`; DE `73e20d9bf3b743858b1c85407d846f5f8f589c09aad98b8b09f9cacfdf693ff2`.

## Disposition and authoritative destinations

| Original material | Classification and disposition | Authoritative destination |
| --- | --- | --- |
| Preparation/download workflow and selection-dependent contents | Useful operator guidance; retain once in the short opening and table. | Section 8.4 introduction and artifact rows. |
| Directory tree and repeated filenames | Duplicated inventory; remove from the reading path. Keep core artifact filenames and alternative result-folder explanation. | Section 8.4 artifact rows; complete filename contracts remain in `ui/results_export.py` and export regression tests. |
| Configuration, provenance, processed evidence, selected-scope tables and figures | Useful scientific/operational distinctions; condense without changing scope. | Section 8.4 artifact rows. |
| Actual decode-filter selection, absent metadata, historical fallback dates and physical-mode caveat | Preserve actual-selection and unknown-metadata consequences in the metadata row; reference existing detailed historical explanation. | Section 5.4; `docs/architecture.md`, export metadata discussion; `ui/results_export.py` and export metadata regression tests. |
| Focused figures and exact zoom fields, recipes and guide metadata | Keep native observations, one selected station, supplementary nature and episode-specific guides. Remove field-by-field repetition from the manual. | Section 8.4 focus row; Section 4.5; `docs/architecture.md`, active Drill-Down focus export discussion. |
| Outlier row meanings, package-local joins, empty/absent files and corrected Reference SNR | Useful interpretation boundaries retained compactly. Full scientific candidate interpretation remains linked from existing Sections 2.5 and 7.6. | Section 8.4 outlier row; Sections 2.5 and 7.6. |
| Outlier field inventory, data formatting, schema and recipe signatures | Engineering detail removed from operator reading path, with original wording archived below. | `docs/architecture.md` export discussion; `ui/inspector/outlier_export.py`; runtime export tests. |
| Public configuration/URL/export name table | Exhaustive-looking duplicate of formal contracts; remove from manual. Retain schema location in Section 4.1 and core filenames in artifact table. | `config/wspradar-config.schema.json`; configuration/URL/export sections in `docs/architecture.md`; `ui/url_state.py`; `ui/results_export.py`. |
| Inbound Section 4 references to the removed contract table | Update descriptions to current settings/evidence/export contents; retain links to Section 8.4 and schema authority. | Chapter 4 introduction and Sections 4.1, 4.3. |
| Original-package preservation and external experiment record | Useful reproducibility guidance; retain concise closing with Section 8.3 link. | Sections 8.3 and 8.4. |

No new formal appendix or user-facing data dictionary is introduced. Original text is archived verbatim below so omitted engineering detail remains auditable without burdening the manual. This record does not change the existing engineering or exported-data contracts.

## Verification

- Independent bilingual content review and implementation-scope review passed. The English and German sections preserve the same operator meanings; the three incoming Chapter 4 descriptions now match the artifact guide. No scientific or export-data behavior changed.
- Section 8.4 fell from approximately 1,269 to 420 English words and 1,206 to 437 German words (whitespace counts including table markup). One two-column, nine-artifact table replaces the duplicated lists and detailed field inventories.
- Final English source SHA-256: `2786ef7ee09057325c2fd2e160082f2d7161bcd75e9e0501916021d06509582b`; German: `fe2ad777a956d76fc9c5cfb4a86760f7391a310f5b3f04106ffb5395d8ecfb50`.
- A source comparison confirms that, relative to the starting working tree, all text outside Section 8.4 and exactly three incoming reference descriptions per language is unchanged. The earlier Section 1.1 Appendix B.4 link remains intact.
- The two documentation regression modules passed: **140 passed in 16.56 seconds**. Tests now protect operator scope and provenance instead of requiring the removed field catalog. Real export-contract tests are unchanged.
- Full English and German PDFs generated successfully (72 and 81 pages). Poppler-rendered Section 8.4 pages were visually reviewed: English 62–63, German 69–71. The table gives 26% to short labels and 74% to descriptions, preserves filenames intact and repeats its header across pages. A final PDF-only break prevents the long German focus label from crossing into the description column.
- README synchronization, complete Python compilation and patch whitespace checks passed. After the full run, both language cases of the final PDF width/filename/label-wrap test passed (**2 passed in 3.71 seconds**), and complete compilation passed again.
- Complete regression verification used the checked-in foreground Windows runner: **3,510 passed, 3 failed, 3 xfailed, 1 existing warning in 657.16 seconds**. The full run is not green. All three failure diagnostics match the previous Chapter 7 verification record:
  - `test_guided_input_integration.py::test_reference_intro_avoids_repeated_metric_definitions_preserved_in_results[en/de]` expects the same SNR definition marker absent from existing result-guidance copy.
  - `test_idle_import_boundary.py::test_idle_browser_component_payloads_preserve_json_transport` expects navigation JSON without the existing `panelKey: null` field.
- The two failing test modules and their relevant production sources (`i18n.py`, `ui/page_navigation.py`) are unchanged from the starting commit. No unrelated UI or navigation repair was included.

## Original English Section 8.4 (verbatim)

````markdown
<a id="sec-8-4"></a>
#### 8.4 Analysis export package

`Prepare All Results for Download` builds a ZIP from the completed run and current inspection selections; `Download Prepared Results` saves it. Before preparing it, select the geographic scope, station or stations, and any focus interval needed to support your conclusion. If those selections change, prepare and download the updated package.

The following layout lists the available files **inside the named ZIP root folder**. `config/` accompanies the selected result; `benchmark/` and `performance/` are alternative result folders, not two analyses produced by one run:

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

Optional figures depend on the available result, station selection and focus state. The three ordinary CSV tables are written for the result even when a selection supplies no rows. Outlier CSV files appear only when their reporting is enabled, as described below.

| Artifact | Scientific content and scope |
|---|---|
| `wspradar_config.config` | Versioned runnable definition and durable result-view settings. |
| `run_metadata.json` | Application/export provenance, database source, Direction, band, time selection, Benchmark/correction definition, filters, thresholds and inspection selections. |
| `analysis_cache.parquet` | Processed retained evidence for the completed run after its scientific filters and configured geographic scope; not only the active Segment Inspector selection and not an untouched database download. |
| `table_station_insights_current_segment.csv` | Per-peer summaries for the active Segment Inspector scope. |
| Drill-Down CSV files | Row-level retained evidence for selected or active-scope identities. |
| Delta-SNR outlier CSV files | When optional outlier reporting is enabled, qualified path-event summaries and their chronological native paired evidence for the active Segment Inspector scope. |
| Map and segment figures | Geographic and segment-level descriptive summaries for the completed result. |
| Temporal figures | Chronological and UTC-folded summaries for the active segment. |
| Selected-station figures | One exact selected peer identity in normal use; while optional ΔSNR outlier reporting enables an ordered multi-path selection, Benchmark can instead export the corresponding pooled multi-path ΔSNR view. |
| Drill-Down focus figures | Optional native-time metric and chronological companion figures for the exact selected station and active manual or candidate-linked focus interval; they supplement rather than replace the full-run selected-station figures. |

For each result block, `run_metadata.json` records the actual query selection in `result_blocks[].decode_filter_mode`: `strict_code_1` means the query retained the `code = 1` predicate; `legacy_no_code` means the historical fallback omitted that restriction after the strict query returned no Target-side evidence. New fallback executions require the entire selected period to end before 1 January 2022 at 00:00 UTC, as described in [Section 5.4](#sec-6-4); the provenance meaning of earlier exports remains unchanged. The saved configuration alone cannot reconstruct this implicit choice, so retain the metadata when comparing evidence populations. A `null` value means the selection was not recorded and must not be inferred as strict. This field documents the query selection; it does not independently verify that every observation belongs to the same physical transmission mode.

When a Drill-Down focus is active at preparation time, Performance can add `figure_drilldown_zoom_snr_evidence.png` and `figure_drilldown_zoom_temporal_evidence.png`; Benchmark can add `figure_drilldown_zoom_delta_snr_evidence.png` and `figure_drilldown_zoom_coverage.png`. The metric figure preserves the same individual retained native points as the browser focus rather than substituting temporal medians; the companion figure preserves the applicable chronological outcome or coverage recipe. `run_metadata.json` records one `drilldown_zoom` block with its schema version, callsign, locator, exact `start_utc` and `end_utc`, selected focus option, `manual` or `outlier_focus` origin and render contract. When a candidate overlay is present, its registered recipe and signature preserve the focused episode and every individually qualifying candidate unit in the window, the muted focused-episode band, local and pre/post baseline values, robust spread and method, robust-z threshold and absolute-departure threshold used by the exported guides. The guide coordinates remain specific to the focused episode even when another starred candidate in the exported window was assessed against another baseline or spread. No focus block or focus figure is included while focus is off or the one-station requirement is not met.

When ΔSNR outlier reporting is enabled, `table_delta_snr_outlier_event_paths.csv` contains one row per qualified path event. It records the combined review-event class and observed UTC bounds, cross-path context and departure direction, then identifies the exact path, direction, path-event class, paired-evidence timing and count, expected and observed ΔSNR, largest departure, robust score, pre/post baseline diagnostics and nearby Decode Outcome diagnostics. One exact path can occur in more than one row of the same combined review event when it contributes more than one qualifying timeframe. The qualifying-path count remains the number of distinct `callsign + locator` identities.

`table_delta_snr_outlier_paired_evidence.csv` contains one row per retained native paired unit inside those path events, in chronological order. Event ID and Path event ID link it to the summary. For stand-alone readability it repeats the observed event bounds, path, direction and path-event class; the combined event class remains only in the summary because it can differ from an individual path's class. The table includes Target SNR, already-corrected Reference SNR, ΔSNR, expected local ΔSNR, departure from that baseline, per-unit robust score, strong-anchor status and reported-boundary role. Timestamps use ISO UTC and numeric fields remain numeric rather than embedding signs or units in the cells.

The IDs are deterministic joins within one prepared package, not persistent identities across separately prepared analyses and not assertions that a physical event occurred. If reporting is enabled but no path event qualifies, both CSVs remain present with their headers and no invented finding row. `run_metadata.json` records the enabled state, detector version, three-threshold policy, export-schema version, result status, table filenames and event, path and evidence counts once. Applicable exported Benchmark figures retain the same candidate-marker recipe metadata. When reporting is disabled, both CSVs, all outlier metadata and all marker recipes are omitted entirely.

**Selected public machine-readable contract names.** This concise table identifies supported external names useful to operators and downstream consumers; it is not an exhaustive saved-configuration field, URL-parameter or export-metadata catalog. The formal JSON Schema (`config/wspradar-config.schema.json`) is authoritative for saved-configuration fields, while the supported public URL contract is versioned separately. Private implementation identifiers are deliberately omitted. These names are not vocabulary for explaining the scientific method.

| Contract surface | Exact names | Meaning |
|---|---|---|
| Configuration format | schema version `1` | Current pre-production `.config` contract; invalid or unsupported files are rejected rather than silently reinterpreted. |
| Result-type values | `performance`, `benchmark` | Values emitted by new analysis URLs, configurations and exports. |
| Durable result-view blocks | `results_view.performance`, `results_view.benchmark` | Saved inspection preferences. Their presence does not create or run an additional result. |
| Result folders | `performance/`, `benchmark/` | Top-level result folders in the export package. |
| Outlier tables | `table_delta_snr_outlier_event_paths.csv`, `table_delta_snr_outlier_paired_evidence.csv` | Enabled-only Benchmark tables linked by package-local Event ID and Path event ID; absent when Delta-SNR outlier reporting is disabled. |
| Figure metadata | `selected_evidence_figures`, `benchmark_evidence_figures`, `benchmark_evidence_recipes`, `drilldown_zoom` | Stable mappings and exact transient zoom identity/bounds for applicable exported figures and Benchmark recipes. |
| Correction metadata | `benchmark_snr_correction_mode`, `benchmark_snr_correction_db` | The semantic correction choice and its numeric dB value. |

Use the PNG figures to present the result, the Station Insights CSV to review station summaries, and Drill-Down CSVs to inspect the supporting rows. The Parquet file preserves processed evidence for further analysis; the `.config` file restores supported settings for another run, not the original reports.

The package preserves the processed evidence and provenance recorded by WSPRadar. It does not contain authoritative external operating logs, physical setup measurements or unchanged database responses. Keep those separately as described in [Section 8.3](#sec-8-3); a later database query need not reproduce the original records exactly.

````

## Original German Section 8.4 (verbatim)

````markdown
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

````

## Original inbound reference descriptions (verbatim)

These six descriptions are replaced by references to the retained export contents; the surrounding control guidance is unchanged.

### EN

> [Section 8.4](#sec-8-4) summarizes selected public machine-readable configuration, URL and export names.

> The formal JSON Schema is the authoritative exhaustive saved-configuration contract; [Section 8.4](#sec-8-4) gives a concise operator-facing summary of selected public identifiers.

> [Section 8.4](#sec-8-4) summarizes selected public machine-readable configuration, URL and export names; it is not an exhaustive field or parameter catalog.


### DE

> [Abschnitt 8.4](#sec-8-4) fasst ausgewählte öffentliche maschinenlesbare Bezeichnungen für Konfiguration, URL und Export zusammen.

> Das formale JSON-Schema ist der maßgebliche vollständige Vertrag gespeicherter Konfigurationen; [Abschnitt 8.4](#sec-8-4) bietet eine knappe, betriebsbezogene Zusammenfassung ausgewählter öffentlicher Bezeichnungen.

> [Abschnitt 8.4](#sec-8-4) fasst ausgewählte öffentliche maschinenlesbare Bezeichnungen für Konfiguration, URL und Export zusammen; er ist kein vollständiger Feld- oder Parameterkatalog.

