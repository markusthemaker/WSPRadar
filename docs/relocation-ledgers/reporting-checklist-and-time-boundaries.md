# Reporting checklist and time-boundary cleanup

## Scope

This change rewrites Section 8.3 around three operator-controlled records: the
saved WSPRadar configuration, the retained evidence package, and external
experiment context. It also removes the automatic half-open interval convention
from the English and German end-user manuals. Exact boundary semantics remain an
implementation and engineering-architecture contract.

English and German were changed in parallel. The German passages had the same
disposition as their English counterparts.

## Removed or replaced passages

### Section 4.2 — boundary convention in the control table

Original English passage not retained:

> Success and Compare both use the half-open interval described in [the time model](#sec-7-1).

Disposition: implementation-only detail removed. The operator-relevant
15-minute endpoint quantization remains documented.

Original German passage not retained:

> Success und Compare verwenden beide das im [Zeitmodell](#sec-7-1) beschriebene halboffene Intervall.

Disposition: German parity with the English removal.

### Section 5.4 — fallback reporting burden

Original English passage not retained:

> The current export package does not preserve the effective decode-filter or fallback state. Retain the reported run status in the experiment notes, especially because Compare and Success can take different paths.

Disposition: removed as a non-actionable reproducibility burden. The section
still explains that fallback broadens selection, may differ between result
blocks, is applied automatically, and is shown for diagnosis.

Original German passage not retained:

> Das aktuelle Exportpaket hält weder den effektiv verwendeten Decode-Filter noch den Fallback-Zustand fest. Bewahre deshalb den gemeldeten Laufstatus in den Versuchsnotizen auf – insbesondere, weil Compare und Success unterschiedliche Wege nehmen können.

Disposition: German parity with the English removal.

### Sections 7.1 and 7.7 — exact interval-boundary mechanics

Original English passages not retained:

> Success and Compare use the same half-open interval, `start <= time < end`: an observation exactly at the quantized start is eligible, while one exactly at the quantized end is excluded. Adjacent analysis windows therefore do not share an endpoint observation.

> A scheduled pair is eligible only when both planned starts satisfy `start <= planned start < end`.

> Pair scheduled Target and Reference starts one-to-one by nearest cyclic separation and require both planned starts to satisfy `start <= planned start < end`.

Disposition: automatic implementation details removed from the end-user manual.
The manual retains the operator-relevant facts that Success and Compare use the
same resolved window and that both planned TX A/B starts must fall within it.

Original German passages not retained:

> Success und Compare verwenden dasselbe halboffene Intervall, `start <= time < end`: Eine Beobachtung genau am quantisierten Start ist zulässig, eine Beobachtung genau am quantisierten Ende ausgeschlossen. Benachbarte Analysefenster teilen sich daher keine Beobachtung am Endpunkt.

> Ein geplantes Paar ist nur zulässig, wenn beide geplanten Starts `start <= geplanter Start < end` erfüllen.

> Geplante Target- und Referenz-Starts anhand des kleinsten zyklischen Abstands eins zu eins zuordnen und verlangen, dass beide geplanten Starts `start <= geplanter Start < end` erfüllen.

Disposition: German parity with the English removal.

### Section 8.3 — former flat reporting checklist

Original English passage replaced in full:

> For a serious result, preserve and report:
>
> * preserve the saved `.config`; it and `run_metadata.json` record the WSPRadar application version, but separately record the exact Git commit and clean-worktree state because the export package does not capture them;
> * configured UTC selection and, when available from the run notes, the resolved 15-minute query bounds, interpreted as the common half-open interval `[start, end)`;
> * exact band and TX/RX direction;
> * Target callsign and configured QTH;
> * Benchmark Design and, for Compare where applicable, the fixed Reference or Setup B identity or the local radius and benchmark method;
> * Hardware schedule design where applicable;
> * Reference SNR Correction and calibration basis;
> * special, moving-station and solar filters;
> * all evidence thresholds;
> * joint station and joint spot/pair counts;
> * station-level median Delta SNR and 90% Stability interval;
> * Decode Outcomes and `STATIONS` / `SPOTS` distributions;
> * Success Rate with its denominator and weighting level;
> * equipment, power, schedule and known limitations;
> * export package plus external experiment notes.

Disposition: rewritten in place. Applicable configuration fields, reported
evidence, and external experiment context are retained and organized by owner.
Application version remains automatically described in Section 8.4. Git state,
internal query-boundary mechanics, and manual fallback-state recording were
removed as implementation-oriented or non-actionable operator requirements.
The German checklist was the native counterpart of this passage and received
the same complete restructuring. Its original passage was:

> Für ein belastbares Ergebnis bewahre folgende Angaben auf und dokumentiere sie:
>
> * die gespeicherte `.config`; sie und `run_metadata.json` erfassen die WSPRadar-Anwendungsversion. Halte jedoch den exakten Git-Commit und den Status des Arbeitsbaums separat fest, da das Exportpaket beides nicht erfasst;
> * konfigurierte UTC-Auswahl und, sofern aus den Laufnotizen verfügbar, die aufgelösten 15-Minuten-Abfragegrenzen, interpretiert als gemeinsames halboffenes Intervall `[start, end)`;
> * exaktes Band und TX-/RX-Richtung;
> * Target-Rufzeichen und konfiguriertes QTH;
> * Benchmark-Design und bei Compare gegebenenfalls die feste Referenz- oder Setup-B-Identität beziehungsweise den lokalen Radius und die Benchmark-Methode;
> * gegebenenfalls den TX-A/B-Zeitplan;
> * Referenz-SNR-Korrektur und deren Kalibriergrundlage;
> * Filter für spezielle und bewegte Stationen sowie solare Filter;
> * alle Evidenzschwellen;
> * Anzahl der Joint-Stationen und Joint-Spots bzw. -Paare;
> * Median des Delta SNR auf Stationsebene und 90-%-Stability-Intervall;
> * Decode Outcomes sowie Verteilungen unter `STATIONS` / `SPOTS`;
> * Success Rate mit ihrem Nenner und der Gewichtungsebene;
> * Geräte, Leistung, Zeitplan und bekannte Einschränkungen;
> * Exportpaket zusammen mit externen Versuchsnotizen.

### Section 8.4 — implementation-level export omissions

Original English passages not retained:

> The effective `code = 1` or historical-fallback state is reported while the run executes but is not stored in the package. The package also does not provide a Git commit, exact resolved pre-quantization endpoints, an explicit field recording the half-open interval convention, or a query/query-parameter fingerprint. Quantized map bounds can occur inside the opaque export signature, but that internal value is not a versioned endpoint contract and should not be treated as one.
>
> The package supports audit and reproducibility but is not a complete computational snapshot. It does not currently include:
>
> * a Git commit or clean-worktree record;
> * explicit resolved and quantized UTC endpoint fields and a machine-readable half-open-interval marker;
> * effective strict `code = 1` versus historical-fallback state for each result block;
> * exact SQL, a stable query/query-parameter fingerprint or untouched upstream responses;
> * a dependency lock or operating-system description;
> * authoritative transmitter/receiver operating logs, calibration records or external experiment notes.

Disposition: implementation-level inventory removed. Section 8.4 now states
the user-relevant boundary directly: the package contains processed evidence,
not untouched upstream responses or authoritative external operating and
calibration records.

Original German passages not retained:

> Der effektive Zustand `code = 1` bzw. des historischen Fallbacks wird während des Laufs angezeigt, aber nicht im Paket gespeichert. Das Paket enthält außerdem weder einen Git-Commit noch die exakten aufgelösten Endpunkte vor der Quantisierung, ein ausdrückliches Feld, das die halboffene Intervallkonvention festhält, oder einen Fingerabdruck der Abfrage bzw. Abfrageparameter. Quantisierte Kartengrenzen können innerhalb der nicht transparenten Exportsignatur vorkommen; dieser interne Wert ist jedoch keine versionierte Festlegung der Zeitgrenzen und darf nicht als solche behandelt werden.
>
> Das Paket unterstützt Audit und Reproduzierbarkeit, ist jedoch kein vollständiger Rechen-Snapshot. Derzeit fehlen:
>
> * Git-Commit oder Nachweis eines unveränderten Arbeitsbaums;
> * ausdrückliche aufgelöste und quantisierte UTC-Endpunktfelder sowie eine maschinenlesbare Kennzeichnung des halboffenen Intervalls;
> * der effektive Zustand des strikten `code = 1` gegenüber dem historischen Fallback je Ergebnisblock;
> * das exakte SQL, ein stabiler Fingerabdruck der Abfrage bzw. Abfrageparameter oder unveränderte vorgelagerte Antworten;
> * ein Abhängigkeits-Lockfile oder eine Beschreibung des Betriebssystems;
> * maßgebliche Betriebsprotokolle der Sender und Empfänger, Kalibrierdatensätze oder externe Versuchsnotizen.

Disposition: German parity with the English removal.
