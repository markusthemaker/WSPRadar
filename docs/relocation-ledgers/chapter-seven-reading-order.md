# Chapter 7: reader-first progression and compact experimental detector

## Authorization and accepted source model

The user approved the six-part subsection plan and its implementation on 2026-10-05, adding: "keep 7.6 shorter than in the current version. This is a experimental feature and does not deserve that much space; we should cover what it does, but at a much reduced volume".

This is a parallel bilingual restructure of the accepted, already improved manuals, not a new scientific method. The English and German starting files have SHA-256 hashes `DC508F5B17C1659730BC7E509DD4CB8E57008A219E35F6FAAB40DE734ABBC6FD` and `6AD9DAEDD5342AD6851D2D4655A76BC4A59A40BDA4F94BB75F9515F9D66ADE58`. These are the working-tree documents accepted after the preceding Chapter 7 readability update, rather than the older committed manuals. The agreed content plan is the common semantic specification.

The approved scope is reorganization and cross-reference repair, with substantial editorial condensation of the optional experimental detector. Runtime analysis, classification, data, controls and exported scientific values are unchanged. A formal methods appendix is not required or introduced. The reported iPad Preview navigation difference remains a separate compatibility observation; this change does not claim to fix it.

## Content destinations

| Previous home | Accepted destination | Disposition |
| --- | --- | --- |
| 7.1 data, units and time; 7.2 identity | 7.1.1 Spots, station identities and WSPR cycles | Preserve definitions; retain extended-WSPR and historical qualifications as conditional notes. |
| Normalization from 7.4; consolidation from 7.2 | 7.1.2 Power normalization and report consolidation | Give shared normalization one home for Benchmark and Performance; retain the equation and scientific consequences of consolidation. |
| 7.3 activity and eligibility | 7.1.3 Target activity and eligible evidence | Preserve asymmetric conditioning and direction-/mode-specific eligibility. |
| 7.6 outcomes and missingness | 7.2.1 Joint Spots and Decode Outcomes | Introduce comparison evidence before the derived SNR difference; retain selection and identity-error limits. |
| Correction and Delta SNR from 7.4 | 7.2.2 Delta SNR and Reference correction | Preserve equations, signs and worked examples; link shared normalization. |
| Benchmark aggregation from 7.7 | 7.2.3 From Joint Spots to station and map results | Preserve station/observation weighting and minimum support, including exact-identity examples. |
| 7.8.2 coverage | 7.2.4 Joint Evidence Share and supporting counts | Bring coverage next to Benchmark evidence, preserving denominators and example. |
| Neighborhood construction from 7.7 | 7.2.5 How Reference Neighborhood forms its Reference | Preserve two-stage local medians, membership effects and support limits. |
| 7.5 Performance; Performance reminder in 7.7 | 7.3.1-7.3.4 opportunities, rates, Reach and successful SNR | Keep one continuous Performance explanation with all denominators and selection boundaries. |
| 7.9 scope, geography and filters | 7.4.1 Geographic scope, population filters and solar conditions | Explain the selected population before its geographic summaries. |
| 7.8.1 geographic summaries | 7.4.2 Map segments and distance profiles | Preserve aggregation and profile support rules. |
| 7.8.3 temporal summaries and folding | 7.4.3-7.4.4 chronological time and UTC-hour folding | Separate the reading questions while preserving represented-date denominators and weighting. |
| 7.8.4 selected paths | 7.4.5 Selected Station Evidence and Drill-Down | Preserve exact identity, native retained evidence and existing-result focus behavior. |
| 7.8.5 spread and transforms | 7.4.6 Spread, density and axis scales | Preserve scientific interpretation of spread, density, binning and transformed axes. |
| 7.10 dependence and validation | 7.5.1-7.5.3 evidence strength, repeatability and validation | Preserve scientific limits, keeping metric-specific caveats beside the affected metric. |
| 7.11 detector | 7.6.1-7.6.5 compact experimental overview | User-authorized condensation: retain purpose, evidence, baseline/support, principal qualification conditions, boundaries/classes and interpretation limits; remove exhaustive procedural specification from the reading path. Exact behavior remains in the existing implementation and regression tests. |

Existing numeric anchors retain their original semantic destination as compatibility aliases. New section links use descriptive anchors, and visible section numbering is updated in both languages and the generated README. The contributor instructions now require this reader-first structure, clickable section references and a proportionate experimental-detector overview.

## Verification and semantic review

- Final English SHA-256: `650A21CD71A2A2D52A7D2078ACF0F4CD167E8A3E48FAC661BF83FDC6B7A22634`.
- Final German SHA-256: `E9B100D3F331A8A56C0C043BC71657753193B68FAEE902545DCF55D679A27646`.
- Complete independent scientific-preservation and bilingual review passed; a separate full German reverse-outline review also passed. The review records are preserved below. No unresolved semantic divergence remains.
- All original anchors are retained exactly once. Every internal link resolves; explicit section/chapter/appendix references are clickable; Chapter 7 link numbering matches its target headings. Four useful equations remain.
- English Chapter 7 is approximately 5,700 words versus 6,580; its experimental section is approximately 650 versus 1,550 (about 58% shorter). German follows the same reduced scope. Counts include headings and vary slightly with markup handling.
- Focused documentation verification: **137 passed in 15.60 seconds**. Two initial failures were obsolete assertions demanding former detector prose; the tests now check the preserved meaning in its current authoritative home. No runtime behavior changed to satisfy a test.
- Complete Python compilation and patch whitespace checks passed; generated README equals `build_readme_text(DOC_EN)`.
- Final PDFs generated from the recorded hashes: English **75 pages**, German **84 pages**. Poppler-rendered Chapter 7 and transition pages (EN 46-59; DE 52-66), plus each Chapter 7 contents page, were visually reviewed. No clipped text, overlapping labels or table collisions were found.
- All **32** Chapter 7 contents destinations in each final PDF were checked against the actual target heading page and vertical coordinate. Each uses an `/XYZ` destination just above the matching heading. A permanent regression test also checks exact heading placement and equality of semantic/compatibility destinations. This does not establish iPad Preview compatibility; that reported viewer-specific issue is unchanged.
- PDF inspection used the bundled independent inspection runtime because the repository environment does not include `pdfplumber`; no dependencies or mixed-runtime paths were installed or configured.
- Complete regression verification used the checked-in foreground Windows runner: **3,507 passed, 3 failed, 3 xfailed, 1 existing warning in 569.25 seconds**. The full run is not green. Its three failures exactly match those already recorded before this restructure:
  - `test_guided_input_integration.py::test_reference_intro_avoids_repeated_metric_definitions_preserved_in_results[en/de]` expects an SNR definition marker absent from the existing result-guidance copy.
  - `test_idle_import_boundary.py::test_idle_browser_component_payloads_preserve_json_transport` expects navigation JSON without the existing `panelKey: null` field.
  The affected test files, `i18n.py`, `ui/page_navigation.py`, `ui/documentation_scroll_trigger.py`, and `ui/url_synchronizer.py` were verified unchanged against HEAD. No new failing test was introduced by this restructure. The existing Matplotlib pending-deprecation warning remains.
- No live provider run, deployment or iPad Preview test was performed. Runtime scientific calculations and analysis behavior were not changed.
- Temporary baseline copies, PDFs, rendered pages and inspection scripts are removed after verification. Their unique editorial source passages and independent review findings are preserved in this ledger. Temporary paths quoted in the historical review records identify those task-local copies, not required runtime or reproduction inputs.

## Source passages condensed or replaced

The verbatim starting passages not retained literally in the integrated manual are recorded below after final integration. Core passages are relocated or rephrased without scientific loss; detector passages are condensed under the explicit authorization above. This ledger preserves editorial history and is not a new end-user formal appendix.

<!-- preserved-source-record -->

### Experimental detector: exact previous passages and disposition

# Chapter 7 detector disposition

Source: .tmp/chapter-seven-progression/doc_en_before.py and doc_de_before.py. The approved experimental overview replaces an exhaustive procedural specification. Exact runtime behavior remains in code/tests; no formal appendix is added.

## Disposition

Retained or compactly summarized: optional expert scope; native Joint-only exact-path evidence; display independence and disabled state; signed +8/+1/−7 example and causal boundary; two supported candidate-excluded local flanks and equal-flank baseline; robust-scale fallback and descriptive score; four conjunctive qualification gates; comparison tolerance; strong boundaries and retesting; same-baseline core rescue; event classes; cross-path context and inferential limits.

Omitted procedural micro-details: cadence estimation interval selection and fallback; 1.5-times cadence gap bounds; initial guard width; provisional departure floor; exact neutral-bridge stopping rule; final guard width; shoulder threshold and three refinement passes; exact rescue segmentation; exact cross-path grouping gap; all-path marker selection versus report peak. These are not moved to a new appendix. Practical investigation remains in Section 2.5, controls in Section 4.6, and exact behavior in code/tests.

Core sections outside the detector are reordered with integration/cross-reference edits. No unique core eligibility, denominator, weight or interpretation rule is intentionally removed.

## EN original detector block 1

**The optional detector looks for a temporary departure from a path's usual local ΔSNR, not simply the largest raw values.** It works separately for every exact remote callsign-plus-locator identity. [Section 2.5](#sec-outlier) explains expert use; [Section 4.6](#sec-5-6) lists the three controls. The steps below define which candidates qualify.

## EN original detector block 2

**Example: a positive value can be a negative departure.** Suppose the local baseline is **+8 dB**, but a Joint Spot is **+1 dB**. Its departure is `+1 - (+8) = -7 dB`. The Target is still stronger than the Reference in that observation, but its advantage is 7 dB smaller than usual. The change can come from the Target, the Reference or both; inspect their individual SNR values before assigning a cause. Grouping uses this departure's sign, not the sign of ΔSNR relative to zero.

## EN original detector block 3

The detector calls the departure a **residual** and compares it with nearby variability, its **robust scale**. A residual divided by that scale and multiplied by `0.6745` gives the **robust z-score**. With a scale of `1 dB`, the example scores about **-4.72**. This is a descriptive score, not a probability, p-value or Gaussian significance level. That one calculation is insufficient: support, baseline agreement, event-level conditions and boundary checks must also pass.

## EN original detector block 4

**1. Keep the observations and baseline resolution distinct.** Only native Joint Spots provide detector ΔSNR. One-sided outcomes cannot supply a missing value, but their timestamps help estimate the path's operating cadence and their outcomes remain diagnostic context. Native here means the retained observations after consolidation, matching and scientific filtering.

## EN original detector block 5

Baseline and variability estimation use median ΔSNR values in populated **UTC-aligned 10-minute cells**. Event grouping and reported boundaries use the actual native Joint-Spot times. Detection precedes Temporal Evidence display aggregation: changing a display bin cannot create, merge, split or remove an event. With **Report ΔSNR outlier candidates** off, the detector is not run.

## EN original detector block 6

**2. Establish the expected local value on both sides of the candidate.** The detector looks up to **six hours before and six hours after** the candidate, excluding the candidate and a surrounding guard interval. Each side needs **at least four populated 10-minute cells**. Missing cells are not filled in.

## EN original detector block 7

| Baseline quantity | Calculation |
|---|---|
| **Before-event baseline** | Median of the retained cell values before the excluded interval. |
| **After-event baseline** | Median of the retained cell values after the excluded interval. |
| **Expected local ΔSNR** | Average of those two medians, giving the two sides equal weight. |
| **Baseline agreement** | Their absolute difference must not exceed **Maximum pre/post baseline difference (dB)** plus the `0.01 dB` comparison tolerance. |

## EN original detector block 8

Equal weight prevents the side with more populated cells from dominating the baseline. “Stable” here means adequate support and sufficiently similar flank medians, not an additional low-variability requirement. Without both supported flanks and acceptable agreement, the candidate remains unclassified and no event is reported.

## EN original detector block 9

**3. Measure nearby variability without treating the baseline difference as noise.** Subtract each flank's own median from its cell values, then pool the resulting residuals. Retain repeated values: two cells with the same residual are still two contributions. Determine the robust scale in this order:

## EN original detector block 10

1. Use the **median absolute deviation (MAD)**: the median absolute distance from the pooled sample's median.
2. If MAD is zero, use **half the IQR**, where IQR is the difference between the 75th and 25th percentiles.
3. Only when both are zero, use **0.5 dB** to avoid division by zero.

## EN original detector block 11

A positive MAD or half-IQR below 0.5 dB is retained; 0.5 dB is a fallback, not a universal minimum. The scale is in dB. Subtracting the expected local ΔSNR gives each Joint Spot's final residual; `0.6745 × residual / robust scale` gives its dimensionless score. The factor provides conventional modified-score scaling when MAD is used.

## EN original detector block 12

**4. Find provisional departures using the path's cadence.** Cadence is estimated from unique eligible outcome times, including Joint and one-sided observations. Retain positive intervals no longer than **45 minutes**; if at least two remain, their median is the typical cadence. Otherwise use the configured native paired-unit cadence.

## EN original detector block 13

The allowed internal gap is **1.5 times that cadence**, limited to a minimum of **15 minutes** and a maximum of **45 minutes**. Sparse observations receive a larger allowance, but no event can bridge a gap above 45 minutes.

## EN original detector block 14

For initial grouping, each supported cell receives a provisional local baseline using the same six-hour flanks, four-cell minimum per flank and baseline-agreement requirement. Exclude the cell and a guard width equal to the greater of **60 minutes** and **twice the cadence**. This prevents the point being tested from defining its own expected value.

## EN original detector block 15

Group nearby native residuals that have the same sign and reach a permissive departure floor: the smaller of **1 dB** and **Minimum absolute ΔSNR departure minus 0.01 dB**. The tolerance does not reduce the fixed 1 dB term. The low floor identifies continuity; it does not relax final qualification.

## EN original detector block 16

An excessive gap, opposite-sign member or supported return to baseline ends grouping. One supported neutral observation can bridge a departure if the same-sign departure resumes; two consecutive supported neutral observations end it. Unsupported observations remain unclassified and are never imputed.

## EN original detector block 17

**5. Refit while excluding the complete candidate.** The final baseline excludes the full provisional interval and a guard width equal to the greater of **10 minutes** and the typical cadence. Against that shared baseline, same-sign shoulders with residual magnitude at least **1 dB** can expand the candidate for up to **three passes**. The entire expanded interval stays excluded at each refit, so the candidate cannot pull its own expected value toward the excursion. The 1 dB shoulder requirement receives no tolerance adjustment.

## EN original detector block 18

**6. Require all qualification conditions together.** Calculate the candidate's median residual and its robust z-score using the final baseline and scale. The median describes the typical departure, not merely the single largest point.

## EN original detector block 19

| Required check | Passing condition |
|---|---|
| **Absolute departure** | The event median's magnitude reaches **Minimum absolute ΔSNR departure (dB)**, allowing the fixed `0.01 dB` comparison tolerance. |
| **Departure relative to variability** | The event median's absolute robust z-score reaches **Minimum robust z-score**, with no tolerance adjustment. |
| **Baseline agreement** | The supported before/after medians remain within **Maximum pre/post baseline difference (dB)** plus `0.01 dB`. |
| **Sign agreement** | At least **two thirds of all retained native observations** share the median residual's sign. The denominator includes any neutral bridge. |

## EN original detector block 20

The tolerance means a minimum dB requirement is compared at the configured value minus 0.01 dB, and a maximum baseline difference at the configured value plus 0.01 dB. It does not round observations, thresholds, medians, MAD/IQR or scores. It applies to the dB checks for event qualification, strong boundary anchors and individually qualifying observations; robust-z and sign checks remain unchanged. A long event receives no duration bonus or weaker threshold.

## EN original detector block 21

**7. Keep strong boundaries without discarding every weaker interior point.** If the complete refined candidate cannot produce a qualifying interval with strong boundaries, split it at returns to the final baseline into contiguous same-sign sections, without neutral bridging. Test each section against the same requirements while reusing the complete candidate's final baseline, robust scale and flank support. This can rescue a strong core without selecting a more favorable baseline for the smaller section.

## EN original detector block 22

An individual observation can anchor a reported boundary only if it shares the event median's sign and separately passes both the absolute-departure and robust-z thresholds. Trim the interval to its first and last such anchors, then retest the trimmed interval against every event-level requirement using the same baseline, scale and flank support. Weaker leading and trailing points disappear; already grouped weaker points between the anchors can remain. No passing anchored interval means no reported event.

## EN original detector block 23

Weak observations can therefore preserve continuity inside an event, while individually strong observations define its reported start and end. One surviving anchor can qualify as a single-spot impulse.

## EN original detector block 24

**8. Describe the surviving evidence, then add cross-path context.** Classification occurs after trimming and does not change the thresholds:

## EN original detector block 25

| Class | Retained evidence |
|---|---|
| **Spot impulse** | One native Joint Spot. |
| **Sustained excursion** | At least three native Joint Spots spanning at least 30 minutes. |
| **Short burst** | Every other multi-spot event. |

## EN original detector block 26

The first-to-last span describes observed evidence, not uninterrupted behavior between observations. Each path qualifies independently. Same-sign path events share a review card when they overlap or are separated by no more than the greater of **10 minutes** and **half the configured native paired-unit cadence**. Context is path-specific for one path, directionally coherent across adjacent compass sectors, scope-wide across separated directions, or multiple paths when at least one direction is unavailable. These labels add review context, not significance or stronger qualification.

## EN original detector block 27

The all-path temporal marker represents the individually qualifying strong anchor with the largest absolute residual in that cross-path review event. **Largest single-cycle departure** in the report/export instead remains the greatest absolute retained residual for each path event; a plot representative and a reported peak need not be the same observation.

## EN original detector block 28

Target/Reference decomposition and nearby one-sided outcomes are diagnostic context only. They cannot qualify, extend or strengthen an event. The detector is a deterministic descriptive classifier, performs no multiple-event significance correction, and does not turn event counts into independent samples. Causal attribution still requires the experimental controls in Chapters 2, 3 and 8.

## DE original detector block 1

**Der optionale Detektor sucht vorübergehende Abweichungen vom üblichen lokalen ΔSNR eines Funkwegs, nicht einfach die größten Rohwerte.** Er arbeitet getrennt für jede exakte entfernte Identität aus Rufzeichen und Locator. [Abschnitt 2.5](#sec-outlier) erklärt den fachkundigen Einsatz; [Abschnitt 4.6](#sec-5-6) nennt die drei Bedienelemente. Die folgenden Schritte definieren, welche Kandidaten qualifizieren.

## DE original detector block 2

**Beispiel: Ein positiver Wert kann eine negative Abweichung sein.** Die lokale Basislinie liege bei **+8 dB**, ein Joint Spot aber bei **+1 dB**. Seine Abweichung beträgt `+1 - (+8) = -7 dB`. Das Target ist in dieser Beobachtung weiterhin stärker als die Referenz, sein Vorteil jedoch 7 dB kleiner als üblich. Die Änderung kann vom Target, von der Referenz oder von beiden stammen; prüfe ihre einzelnen SNR-Werte, bevor du eine Ursache zuordnest. Die Gruppierung verwendet das Vorzeichen dieser Abweichung, nicht das Vorzeichen des ΔSNR gegenüber null.

## DE original detector block 3

Der Detektor nennt die Abweichung **Residuum** und vergleicht sie mit der umgebenden Variabilität, seinem **robusten Streuungsmaß**. Das Residuum geteilt durch dieses Maß und multipliziert mit `0.6745` ergibt den **robusten z-Wert**. Bei einem Streuungsmaß von `1 dB` erreicht das Beispiel etwa **-4.72**. Dies ist eine deskriptive Kennzahl, keine Wahrscheinlichkeit, kein p-Wert und kein gaußsches Signifikanzniveau. Diese Einzelrechnung genügt nicht: Auch Unterstützung, Basislinienübereinstimmung, Ereignisbedingungen und Grenzprüfungen müssen passen.

## DE original detector block 4

**1. Beobachtungen und Basislinienauflösung getrennt halten.** Nur native Joint Spots liefern ΔSNR für den Detektor. Einseitige Outcomes können keinen fehlenden Wert ersetzen; ihre Zeitstempel helfen jedoch, den zeitlichen Rhythmus des Funkwegs zu bestimmen, und ihre Outcomes bleiben diagnostischer Kontext. Nativ bedeutet hier die beibehaltenen Beobachtungen nach Zusammenfassung, Zuordnung und wissenschaftlicher Filterung.

## DE original detector block 5

Basislinie und Variabilität werden aus medianen ΔSNR-Werten belegter **UTC-ausgerichteter 10-Minuten-Zellen** bestimmt. Ereignisgruppierung und gemeldete Grenzen verwenden die tatsächlichen Zeitpunkte der nativen Joint Spots. Die Erkennung erfolgt vor der Anzeigeaggregation der zeitlichen Evidenz: Andere Anzeigeintervalle können kein Ereignis erzeugen, zusammenführen, teilen oder entfernen. Ist **ΔSNR-Ausreißerkandidaten melden** ausgeschaltet, läuft der Detektor nicht.

## DE original detector block 6

**2. Den erwarteten lokalen Wert auf beiden Seiten des Kandidaten bestimmen.** Der Detektor betrachtet bis zu **sechs Stunden davor und sechs Stunden danach**. Den Kandidaten und ein umgebendes Schutzintervall schließt er aus. Jede Seite benötigt **mindestens vier belegte 10-Minuten-Zellen**. Fehlende Zellen werden nicht aufgefüllt.

## DE original detector block 7

| Basisliniengröße | Berechnung |
|---|---|
| **Basislinie vor dem Ereignis** | Median der beibehaltenen Zellwerte vor dem ausgeschlossenen Intervall. |
| **Basislinie nach dem Ereignis** | Median der beibehaltenen Zellwerte nach dem ausgeschlossenen Intervall. |
| **Erwartetes lokales ΔSNR** | Mittel dieser beiden Mediane; beide Seiten erhalten dasselbe Gewicht. |
| **Basislinienübereinstimmung** | Ihr absoluter Unterschied darf **Maximaler Unterschied zwischen Baseline davor/danach (dB)** zuzüglich der Vergleichstoleranz von `0.01 dB` nicht überschreiten. |

## DE original detector block 8

Gleiche Gewichtung verhindert, dass die Seite mit mehr belegten Zellen die Basislinie dominiert. „Stabil“ bedeutet hier ausreichende Unterstützung und hinreichend ähnliche Flankenmediane, keine zusätzliche Forderung nach geringer Variabilität. Fehlt die erforderliche Unterstützung auf einer der beiden Seiten oder die erforderliche Übereinstimmung, bleibt der Kandidat unklassifiziert und es wird kein Ereignis gemeldet.

## DE original detector block 9

**3. Die umgebende Variabilität messen, ohne den Basislinienunterschied als Rauschen zu behandeln.** Ziehe von den Zellwerten jeder Flanke deren eigenen Median ab und führe die resultierenden Residuen zusammen. Wiederholte Werte bleiben erhalten: Zwei Zellen mit demselben Residuum sind weiterhin zwei Beiträge. Bestimme das robuste Streuungsmaß in dieser Reihenfolge:

## DE original detector block 10

1. Verwende die **mediane absolute Abweichung (MAD)**: den Median der absoluten Abstände vom Median der zusammengeführten Stichprobe.
2. Ist MAD null, verwende den **halben IQR**; der IQR ist die Differenz zwischen dem 75. und 25. Perzentil.
3. Nur wenn beide null sind, verwende **0.5 dB**, um eine Division durch null zu vermeiden.

## DE original detector block 11

Ein positiver MAD oder halber IQR unter 0.5 dB bleibt erhalten; 0.5 dB ist ein Ersatzwert, keine allgemeine Untergrenze. Das Streuungsmaß hat die Einheit dB. Das Abziehen des erwarteten lokalen ΔSNR ergibt das endgültige Residuum jedes Joint Spots; `0.6745 × Residuum / robustes Streuungsmaß` ergibt seinen dimensionslosen z-Wert. Der Faktor liefert bei Verwendung von MAD die übliche Skalierung eines modifizierten z-Werts.

## DE original detector block 12

**4. Vorläufige Abweichungen anhand des zeitlichen Rhythmus finden.** Der typische Zeitabstand wird aus eindeutigen zulässigen Outcome-Zeitpunkten bestimmt, einschließlich Joint- und einseitiger Beobachtungen. Positive Abstände von höchstens **45 Minuten** bleiben erhalten. Liegen mindestens zwei vor, ist ihr Median der typische Abstand. Andernfalls gilt der festgelegte Zeitabstand nativer gepaarter Einheiten.

## DE original detector block 13

Die erlaubte interne Lücke beträgt **das 1,5-Fache dieses Abstands**, begrenzt auf mindestens **15 Minuten** und höchstens **45 Minuten**. Bei dünnerer Evidenz wird die erlaubte Lücke größer; kein Ereignis kann jedoch eine Lücke über 45 Minuten überbrücken.

## DE original detector block 14

Für die erste Gruppierung erhält jede unterstützte Zelle eine vorläufige lokale Basislinie mit denselben Sechs-Stunden-Flanken, mindestens vier Zellen je Flanke und derselben Anforderung an die Basislinienübereinstimmung. Die Zelle und ein Schutzintervall werden ausgeschlossen; dessen Breite ist der größere Wert aus **60 Minuten** und **dem doppelten typischen Abstand**. Dadurch bestimmt der geprüfte Punkt nicht seinen eigenen Erwartungswert.

## DE original detector block 15

Nahe native Residuen werden gruppiert, wenn sie dasselbe Vorzeichen haben und eine bewusst niedrige Abweichungsgrenze erreichen: den kleineren Wert aus **1 dB** und **Minimale absolute ΔSNR-Abweichung minus 0.01 dB**. Die Toleranz verringert nicht den festen 1-dB-Anteil. Die niedrige Grenze erkennt den Zusammenhang; sie lockert nicht die endgültige Qualifikation.

## DE original detector block 16

Eine zu große Lücke, ein Mitglied mit entgegengesetztem Vorzeichen oder eine durch Evidenz belegte Rückkehr zur Basislinie beendet die Gruppierung. Eine unterstützte neutrale Beobachtung kann eine Abweichung überbrücken, wenn die gleichgerichtete Abweichung danach weitergeht; zwei aufeinanderfolgende unterstützte neutrale Beobachtungen beenden sie. Nicht unterstützte Beobachtungen bleiben unklassifiziert und werden niemals durch angenommene Werte ersetzt.

## DE original detector block 17

**5. Unter Ausschluss des vollständigen Kandidaten neu anpassen.** Die endgültige Basislinie schließt das gesamte vorläufige Intervall und ein Schutzintervall aus. Dessen Breite ist der größere Wert aus **10 Minuten** und dem typischen Abstand. Gegen diese gemeinsame Basislinie können gleichgerichtete Randbereiche mit einem Residuumsbetrag von mindestens **1 dB** den Kandidaten in bis zu **drei Durchgängen** erweitern. Das gesamte erweiterte Intervall bleibt bei jeder Neuanpassung ausgeschlossen, damit der Kandidat seinen eigenen Erwartungswert nicht zur Auslenkung hin verschiebt. Die 1-dB-Anforderung für die Randerweiterung erhält keine Toleranzkorrektur.

## DE original detector block 18

**6. Alle Qualifikationsbedingungen gemeinsam verlangen.** Berechne das mediane Residuum des Kandidaten und seinen robusten z-Wert mit der endgültigen Basislinie und dem endgültigen Streuungsmaß. Der Median beschreibt die typische Abweichung, nicht nur den einzelnen größten Punkt.

## DE original detector block 19

| Erforderliche Prüfung | Bedingung für das Bestehen |
|---|---|
| **Absolute Abweichung** | Der Betrag des Ereignismedians erreicht **Minimale absolute ΔSNR-Abweichung (dB)** unter Berücksichtigung der festen Vergleichstoleranz von `0.01 dB`. |
| **Abweichung relativ zur Variabilität** | Der absolute robuste z-Wert des Ereignismedians erreicht **Minimaler robuster z-Wert**, ohne Toleranzkorrektur. |
| **Basislinienübereinstimmung** | Die ausreichend unterstützten Mediane davor und danach liegen höchstens um **Maximaler Unterschied zwischen Baseline davor/danach (dB)** zuzüglich `0.01 dB` auseinander. |
| **Vorzeichenübereinstimmung** | Mindestens **zwei Drittel aller beibehaltenen nativen Beobachtungen** haben das Vorzeichen des medianen Residuums. Der Nenner enthält auch eine etwaige neutrale Brücke. |

## DE original detector block 20

Die Toleranz bedeutet, dass eine dB-Mindestanforderung mit dem eingestellten Wert minus 0.01 dB verglichen wird, ein maximaler Basislinienunterschied dagegen mit dem eingestellten Wert plus 0.01 dB. Sie rundet weder Beobachtungen, Schwellen, Mediane, MAD/IQR noch z-Werte. Sie gilt für die dB-Prüfungen der Ereignisqualifikation, starken Grenzanker und einzeln qualifizierenden Beobachtungen; z-Wert- und Vorzeichenprüfungen bleiben unverändert. Ein langes Ereignis erhält keinen Dauerbonus und keine schwächere Schwelle.

## DE original detector block 21

**7. Starke Grenzen bewahren, ohne jeden schwächeren inneren Punkt zu verwerfen.** Liefert der vollständig verfeinerte Kandidat kein qualifizierendes Intervall mit starken Grenzen, wird er an Rückkehrpunkten zur endgültigen Basislinie in zusammenhängende gleichgerichtete Abschnitte geteilt, ohne neutrale Brücken. Prüfe jeden Abschnitt gegen dieselben Anforderungen und verwende dabei weiterhin die endgültige Basislinie, das robuste Streuungsmaß und die Flankenunterstützung des vollständigen Kandidaten. So kann ein starker Kern erhalten bleiben, ohne für den kleineren Abschnitt eine günstigere Basislinie auszuwählen.

## DE original detector block 22

Eine einzelne Beobachtung darf eine gemeldete Grenze nur dann verankern, wenn sie das Vorzeichen des Ereignismedians hat und sowohl die Schwelle der absoluten Abweichung als auch die des robusten z-Werts selbst erfüllt. Begrenze das Intervall auf den ersten und letzten solchen Anker. Prüfe das gekürzte Intervall danach erneut gegen sämtliche Ereignisanforderungen mit derselben Basislinie, demselben Streuungsmaß und derselben Flankenunterstützung. Schwächere führende und nachlaufende Punkte entfallen; bereits gruppierte schwächere Punkte zwischen den Ankern können bleiben. Besteht kein solches verankertes Intervall alle Prüfungen, wird kein Ereignis gemeldet.

## DE original detector block 23

Schwache Beobachtungen können somit den Zusammenhang innerhalb eines Ereignisses bewahren, während einzeln starke Beobachtungen dessen gemeldeten Anfang und Ende bestimmen. Ein einziger verbleibender Anker kann als Spot-Impuls qualifizieren.

## DE original detector block 24

**8. Die verbleibende Evidenz beschreiben und danach den Kontext mehrerer Funkwege ergänzen.** Die Klassifikation erfolgt nach dem Kürzen und ändert die Schwellen nicht:

## DE original detector block 25

| Klasse | Beibehaltene Evidenz |
|---|---|
| **Spot-Impuls** | Ein nativer Joint Spot. |
| **Anhaltende Auslenkung** | Mindestens drei native Joint Spots über eine Spanne von mindestens 30 Minuten. |
| **Kurzer Ausbruch** | Jedes andere Ereignis mit mehreren Spots. |

## DE original detector block 26

Die Spanne vom ersten bis zum letzten Punkt beschreibt beobachtete Evidenz, kein ununterbrochenes Verhalten dazwischen. Jeder Funkweg wird getrennt auf Qualifikation geprüft. Gleichgerichtete Funkwegereignisse werden gemeinsam zur Prüfung gruppiert, wenn sie sich überlappen oder höchstens um den größeren Wert aus **10 Minuten** und **dem halben festgelegten Zeitabstand nativer gepaarter Einheiten** getrennt sind. Der Kontext ist funkwegspezifisch bei einem Funkweg, richtungskohärent bei benachbarten Kompasssektoren, bereichsweit bei getrennten Richtungen oder „Mehrere Funkwege“, wenn mindestens eine Richtung fehlt. Diese Bezeichnungen ergänzen den Prüfungskontext, keine Signifikanz oder stärkere Qualifikation.

## DE original detector block 27

Der Marker im Zeitverlauf aller Funkwege steht für den einzeln qualifizierenden starken Anker mit dem größten absoluten Residuum in diesem funkwegübergreifenden Prüfereignis. **Größte Einzelzyklusabweichung** im Bericht und Export bleibt dagegen das größte absolute beibehaltene Residuum jedes Funkwegereignisses. Ein repräsentativer Diagrammpunkt und ein berichteter Spitzenwert müssen deshalb nicht dieselbe Beobachtung sein.

## DE original detector block 28

Die Zerlegung in Target und Referenz sowie nahe einseitige Outcomes sind ausschließlich diagnostischer Kontext. Sie können ein Ereignis weder qualifizieren noch verlängern oder stärken. Der Detektor ist ein deterministischer deskriptiver Klassifikator, führt keine Signifikanzkorrektur für mehrere Ereignisse durch und macht aus Ereigniszahlen keine unabhängigen Stichproben. Die Zuordnung zu einer Ursache erfordert weiterhin die experimentellen Kontrollen aus den Kapiteln 2, 3 und 8.

## Core integration deduplication

The former final paragraph of §7.7 is integrated into its two owning topics rather than copied as a redundant standalone paragraph. Its Performance minimum-opportunity-before-rate rule is already stated explicitly in §7.3.2 before the weighting table (each station qualifies only after meeting its configured minimum; both table rows use qualifying stations). Its median/bias sentence is merged into §7.5.1, retaining calibration errors, reporting differences, propagation bias and dependence. Original paragraphs:

EN: **Performance** applies its minimum opportunity count per identity before calculating the individual rates and both weightings in Section 7.5. In both analysis families, medians limit isolated extreme values; they do not remove systematic calibration errors, reporting differences, propagation bias or dependence.

DE: **Performance** wendet seine Mindestzahl an Gelegenheiten je Identität an, bevor die einzelnen Raten und beide Gewichtungen aus Abschnitt 7.5 berechnet werden. In beiden Analysefamilien begrenzen Mediane den Einfluss einzelner Extremwerte; sie beseitigen weder systematische Kalibrierfehler, Meldeunterschiede, Ausbreitungsverzerrungen noch Abhängigkeiten.


## EN core passages changed during integration

These passages retain their scientific content in the destinations above. Changes are cross-reference updates, explicit shared normalization, chronological/folded separation, and consolidation of the approved duplicates. Verbatim originals follow.

### EN core source 1: 7. Scientific Methods

```text
Read Sections 7.1–7.3 for the shared data rules, Section 7.4 for Benchmark SNR calculations, and Section 7.5 for Performance. The later sections explain weighting, geographic and temporal summaries, and limitations. Section 7.11 defines the optional expert detector for temporary ΔSNR departures.
```

### EN core source 2: 7. Scientific Methods

```text
These are descriptive calculations for the selected evidence. A result can be exact for the retained observations without establishing a physical cause, future performance or a value for every station. Those interpretation boundaries are addressed in Sections 7.10 and Chapter 8.
```

### EN core source 3: 7.1 Data source, observation units and time model

```text
A **spot** is one reported successful decode. A **WSPR cycle** is the two-minute interval beginning at an even UTC minute. The basic observation concerns one exact remote station identity in one eligible cycle on the selected band. That remote station is a transmitter in RX analysis and a receiver in TX analysis. Multiple qualifying reports are consolidated as described in Section 7.2 before outcomes are counted.
```

### EN core source 4: 7.2 Identity, matching and row consolidation

```text
**Several reports still count as one observation for that side, remote station and cycle.** WSPRadar retains the strongest qualifying normalized SNR for Performance, each side of Reference Setup/Station, and the Target side of Reference Neighborhood. Local Reference contributors instead use a within-identity median before the neighborhood median is formed; Section 7.7 explains that two-stage calculation. Consolidation never combines successive cycles.
```

### EN core source 5: 7.3 Target-active conditioning and eligibility

```text
Target activity alone is not enough to turn every silent remote station into a missed decode. Performance also needs the endpoint evidence defined in Section 7.5.
```

### EN core source 6: 7.4 Power normalization, correction and Benchmark ΔSNR

```text
**A fair SNR comparison must account for reported transmit power before subtracting Target and Reference values.** WSPR reports SNR in dB relative to a 2500 Hz reference bandwidth and transmit power in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar expresses successful SNR observations in both RX and TX analyses at a common reported power of **30 dBm (1 W)**:
```

### EN core source 7: 7.4 Power normalization, correction and Benchmark ΔSNR

```text
The correction must be approximately stable over the relevant band, signal levels, hardware state and time. Enter a measured calibration offset with the `target - reference` sign. Section 4.3 explains the controls and [Appendix C](#sec-reference-snr-calibration) the calibration procedure.
```

### EN core source 8: 7.4 Power normalization, correction and Benchmark ΔSNR

```text
In RX Joint Spots, both receivers observe the same transmitter, so its common reported-power term cancels. TX Joint Spots compare different transmitted signals and depend directly on accurate power reporting and any uncorrected differences in the transmit equipment. The resulting ΔSNR is an observed difference between the complete documented setups; assigning it to one antenna or component still requires the physical controls described in Chapter 2.
```

### EN core source 9: 7.7 Aggregation hierarchy and weighting

```text
**Performance** applies its minimum opportunity count per identity before calculating the individual rates and both weightings in Section 7.5. In both analysis families, medians limit isolated extreme values; they do not remove systematic calibration errors, reporting differences, propagation bias or dependence.
```

### EN core source 10: 7.8.1 Geographic summaries

```text
Segment summaries use the complete qualifying population in the active geographic scope. Sorting a table or selecting a row does not redefine that population. Benchmark maps use the median of qualifying station medians described in Section 7.7; the Joint-Spot distribution remains separately available.
```

### EN core source 11: 7.8.2 Benchmark evidence coverage

```text
For example, a station with 80 Joint outcomes out of 100 contributes 80%; another with 1 out of 10 contributes 10%. Their station-balanced share is **45%**, while pooling gives `81 / 110 = 73.6%`. The first gives stations equal weight; the second gives outcomes equal weight. Neither is a Target win rate. The Target-active asymmetry in Section 7.3 still applies.
```

### EN core source 12: 7.8.3 Temporal summaries and UTC folding

```text
**Benchmark ΔSNR** summarizes retained Joint Spots within each chronological bin, or pools them by UTC hour across represented dates. Coverage separately includes all retained one-sided and Joint outcomes using the two shares above. An empty ΔSNR layer can therefore coexist with one-sided evidence; it does not establish that the database returned no reports.
```

### EN core source 13: 7.8.3 Temporal summaries and UTC folding

```text
Chronologically, each station contributes at most one median deviation per bin. When folding by UTC hour, each station first contributes one median per date and hour. Extra rows within that station-date-hour add no further weight, but stations present on more dates and dates containing more stations still contribute more values. This is not equal weighting of stations or dates over the whole run.
```

### EN core source 14: 7.8.5 Descriptive spread and visualization transforms

```text
**IQR describes the middle half of the contributing values; min–max describes their full range.** Neither is a confidence interval. Temporal IQR bands require at least five contributing values; a median remains available with fewer. Depending on the view, those values are Joint Spots, successful Target observations, station-bin medians or station-date-hour medians. Performance distance profiles use the separate three-station rule above.
```

### EN core source 15: 7.10 Dependence, uncertainty and validation scope

```text
Station balancing reduces domination by prolific reporters, and medians reduce the influence of isolated extremes. Neither removes systematic bias or creates independence. WSPRadar supplies descriptive summaries, not automatic standard errors, confidence intervals, p-values, statistical power or causal effects. Treating every report as independent would generally understate uncertainty about a future run or broader population.
```

## DE core passages changed during integration

These passages retain their scientific content in the destinations above. Changes are cross-reference updates, explicit shared normalization, chronological/folded separation, and consolidation of the approved duplicates. Verbatim originals follow.

### DE core source 1: 7. Wissenschaftliche Methoden

```text
Die Abschnitte 7.1–7.3 erklären die gemeinsamen Datenregeln, Abschnitt 7.4 die SNR-Berechnungen für Benchmark und Abschnitt 7.5 Performance. Danach folgen Gewichtung, geografische und zeitliche Zusammenfassungen sowie deren Grenzen. Abschnitt 7.11 definiert den optionalen Expertendetektor für vorübergehende ΔSNR-Abweichungen.
```

### DE core source 2: 7. Wissenschaftliche Methoden

```text
Dies sind deskriptive Berechnungen für die ausgewählte Evidenz. Ein Ergebnis kann für die beibehaltenen Beobachtungen exakt sein, ohne eine physische Ursache, künftige Performance oder einen Wert für alle Stationen zu belegen. Abschnitt 7.10 und Kapitel 8 behandeln diese Interpretationsgrenzen.
```

### DE core source 3: 7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell

```text
Ein **Spot** ist ein gemeldeter erfolgreicher Decode. Ein **WSPR-Zyklus** ist das zweiminütige Intervall, das an einer geraden UTC-Minute beginnt. Die grundlegende Beobachtung betrifft eine exakte entfernte Stationsidentität in einem zulässigen Zyklus auf dem ausgewählten Band. Die entfernte Station ist bei RX ein Sender und bei TX ein Empfänger. Mehrere qualifizierende Meldungen werden gemäß Abschnitt 7.2 zusammengefasst, bevor die Outcomes gezählt werden.
```

### DE core source 4: 7.2 Identität, Zuordnung und Zeilenkonsolidierung

```text
**Mehrere Meldungen zählen weiterhin als eine Beobachtung für diese Seite, entfernte Station und diesen Zyklus.** WSPRadar behält das stärkste qualifizierende normierte SNR bei: für Performance, für jede Seite von Referenzaufbau/-station und für die Target-Seite der Referenznachbarschaft. Lokale Referenzbeiträge verwenden stattdessen einen Median innerhalb jeder Identität, bevor der Nachbarschafts-Median gebildet wird; Abschnitt 7.7 erklärt diese zweistufige Berechnung. Die Zusammenfassung verbindet niemals aufeinanderfolgende Zyklen.
```

### DE core source 5: 7.3 Konditionierung auf Target-Aktivität und Zulässigkeit

```text
Target-Aktivität allein macht nicht jede stille entfernte Station zu einem verpassten Decode. Performance benötigt zusätzlich die in Abschnitt 7.5 definierte Evidenz für die beteiligten Endpunkte.
```

### DE core source 6: 7.4 Leistungsnormierung, Korrektur und Benchmark-ΔSNR

```text
**Ein fairer SNR-Vergleich muss die gemeldete Sendeleistung berücksichtigen, bevor Target- und Referenzwerte voneinander abgezogen werden.** WSPR meldet das SNR in dB bezogen auf eine Referenzbandbreite von 2500 Hz und die Sendeleistung in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar bezieht erfolgreiche SNR-Beobachtungen sowohl bei RX als auch bei TX auf eine gemeinsame gemeldete Leistung von **30 dBm (1 W)**:
```

### DE core source 7: 7.4 Leistungsnormierung, Korrektur und Benchmark-ΔSNR

```text
Die Korrektur muss über das relevante Band, die Signalpegel, den Gerätezustand und die Zeit ungefähr stabil sein. Trage einen gemessenen Kalibrierversatz mit dem Vorzeichen `target - reference` ein. Abschnitt 4.3 erklärt die Bedienelemente und [Anhang C](#sec-reference-snr-calibration) das Kalibrierverfahren.
```

### DE core source 8: 7.4 Leistungsnormierung, Korrektur und Benchmark-ΔSNR

```text
Bei RX-Joint-Spots beobachten beide Empfänger denselben Sender, sodass sich dessen gemeinsamer gemeldeter Leistungsanteil herauskürzt. TX-Joint-Spots vergleichen unterschiedliche Sendesignale und hängen unmittelbar von korrekten Leistungsangaben sowie unkorrigierten Unterschieden der Sendeausrüstung ab. Das resultierende ΔSNR ist ein beobachteter Unterschied zwischen den vollständigen dokumentierten Aufbauten; die Zuordnung zu einer Antenne oder einem Bauteil erfordert weiterhin die in Kapitel 2 beschriebenen physischen Kontrollen.
```

### DE core source 9: 7.7 Aggregationshierarchie und Gewichtung

```text
**Performance** wendet seine Mindestzahl an Gelegenheiten je Identität an, bevor die einzelnen Raten und beide Gewichtungen aus Abschnitt 7.5 berechnet werden. In beiden Analysefamilien begrenzen Mediane den Einfluss einzelner Extremwerte; sie beseitigen weder systematische Kalibrierfehler, Meldeunterschiede, Ausbreitungsverzerrungen noch Abhängigkeiten.
```

### DE core source 10: 7.8.1 Geografische Zusammenfassungen

```text
Segmentzusammenfassungen verwenden die vollständige qualifizierende Population im aktiven geografischen Bereich. Das Sortieren einer Tabelle oder Auswählen einer Zeile definiert diese Population nicht neu. Benchmark-Karten verwenden den in Abschnitt 7.7 beschriebenen Median qualifizierender Stationsmediane; die Joint-Spot-Verteilung bleibt getrennt verfügbar.
```

### DE core source 11: 7.8.2 Benchmark-Evidenzabdeckung

```text
Beispielsweise trägt eine Station mit 80 Joint-Outcomes von 100 einen Anteil von 80% bei; eine andere mit 1 von 10 einen Anteil von 10%. Ihr stationsgleichgewichteter Anteil beträgt **45%**, zusammengezählt ergibt sich dagegen `81 / 110 = 73.6%`. Die erste Berechnung gewichtet Stationen gleich, die zweite Outcomes. Keine ist eine Target-Siegquote. Die Asymmetrie durch Target-Aktivität aus Abschnitt 7.3 gilt weiterhin.
```

### DE core source 12: 7.8.3 Zeitliche Zusammenfassungen und UTC-Stunden

```text
**Benchmark-ΔSNR** fasst beibehaltene Joint Spots innerhalb jedes chronologischen Intervalls zusammen oder führt sie über die vertretenen Tage nach UTC-Stunde zusammen. Die Abdeckung umfasst getrennt davon alle beibehaltenen einseitigen und Joint-Outcomes mit den beiden oben definierten Anteilen. Einer leeren ΔSNR-Ebene kann deshalb weiterhin einseitige Evidenz gegenüberstehen; sie belegt nicht, dass die Datenbank keine Meldungen geliefert hat.
```

### DE core source 13: 7.8.3 Zeitliche Zusammenfassungen und UTC-Stunden

```text
Chronologisch trägt jede Station höchstens eine mediane Abweichung pro Intervall bei. Bei der Zusammenfassung nach UTC-Stunde liefert jede Station zunächst einen Median je Datum und Stunde. Weitere Zeilen innerhalb dieser Stations-Datums-Stunde erhöhen das Gewicht nicht. Stationen, die an mehr Tagen vertreten sind, und Tage mit mehr Stationen tragen jedoch weiterhin mehr Werte bei. Stationen oder Tage werden also nicht über den gesamten Lauf gleich gewichtet.
```

### DE core source 14: 7.8.5 Deskriptive Streuung und Darstellungstransformationen

```text
**Der IQR beschreibt die mittlere Hälfte der beitragenden Werte; Min–Max beschreibt ihren gesamten Wertebereich.** Beides sind keine Konfidenzintervalle. Zeitliche IQR-Bänder erfordern mindestens fünf beitragende Werte; ein Median bleibt bei weniger Werten verfügbar. Je nach Ansicht sind diese Werte Joint Spots, erfolgreiche Target-Beobachtungen, Stations-Intervallmediane oder Stations-Datums-Stunden-Mediane. Für Performance-Entfernungsprofile gilt die gesonderte Drei-Stationen-Regel oben.
```

### DE core source 15: 7.10 Abhängigkeit, Unsicherheit und Validierungsumfang

```text
Stationsgleichgewichtung verringert die Dominanz besonders meldestarker Stationen; Mediane verringern den Einfluss einzelner Extremwerte. Beides beseitigt keine systematische Verzerrung und erzeugt keine Unabhängigkeit. WSPRadar liefert deskriptive Zusammenfassungen, nicht automatisch Standardfehler, Konfidenzintervalle, p-Werte, Teststärke oder kausale Effekte. Würde jede Meldung als unabhängig behandelt, würde die Unsicherheit über einen künftigen Lauf oder eine breitere Population im Allgemeinen unterschätzt.
```

## Independent scientific and bilingual review record

# Independent Chapter 7 preservation and bilingual parity review

Review scope: the six-part reorganization and approved compact experimental detector overview. Source comparison: `.tmp/chapter-seven-progression/doc_en_before.py` and `doc_de_before.py` versus the current authoritative manuals. No runtime or manual source edits were made by this reviewer. The reviewer owns only `tests/regression/test_documentation_rendering.py` and this report.

Reviewed source hashes:
- English SHA256: 650a21cd71a2a2d52a7d2078acf0f4cd167e8a3e48fac661bf83fdc6b7a22634
- German SHA256: e9b100d3f331a8a56c0c043bc71657753193b68faee902545dcf55d679a27646

Result: PASS. No remaining substantive scientific mismatch or English-German semantic discrepancy found within the approved scope. This conclusion covers content review and targeted comparison with implementation, not a new qualification of live data providers or the complete scientific pipeline.

## Review method

Read the complete reorganized scientific chapter against the previously accepted bilingual chapter. Compared paragraph inventories after stripping headings/anchors and normalizing section-link numbering: 88 substantive blocks per language remain unchanged. Read every changed block in both languages and mapped all nine changed/merged non-detector baseline blocks to their retained homes. This structural comparison supported, rather than replaced, the semantic review below.

Checked units, identity, conditioning, counting, denominators, weighting, examples, selection/censoring, scope, display invariants and claims. The full prior detector specification is intentionally replaced by an overview under the user's explicit approval; preservation does not require restoring omitted engineering microsteps.

## Paired reverse outline

| Current home | English meaning | German counterpart and assessment |
|---|---|---|
| 7 introduction | Two analysis questions; reports become constructed units and summaries; descriptive scope; six-group reading routes. | Same questions, construction hierarchy, descriptive limits and linked routes. Equivalent. |
| 7.1.1 Spots, identities and cycles | One database/run; exact remote identity and even-UTC two-minute cycle; RX/TX roles; same-cycle pairing only; full peer locator versus grid-4 endpoint matching and full-QTH geometry; extended-message and historical-data qualifications. | Same identity matrix, cycle boundary, role distinctions, full-locator geometry limits, hash/non-reconstruction and historical qualification. Equivalent. |
| 7.1.2 Power normalization and consolidation | Successful SNR normalized to reported 30 dBm in both families; actual outcomes unchanged; strongest normalized SNR except Local Reference's identity medians; best-observed reception limits. | Same normalization equation, units, example, limits and Local Median exception. Shared Performance applicability is explicit. Equivalent. |
| 7.1.3 Target activity and eligibility | Global RX/TX activity witnesses; missing witness excluded; Reference not separately gated; asymmetric one-sided populations; special/moving exclusion order differs by analysis; geography follows activity. | Same endpoint witnesses, out-of-scope qualification, asymmetry and filter-order difference. Equivalent. |
| 7.2.1 Outcomes and missingness | Joint/one-sided/Async definitions; paired-decode selection; no invented missing-side SNR; reported-power and hash limitations. | Same outcome table and selection/missingness boundaries. Equivalent. |
| 7.2.2 Delta SNR and correction | Additive Reference-only correction and its stable-offset assumption; Target-minus-corrected-Reference sign; RX common-power cancellation versus TX power sensitivity. | Equations, signs, examples and experiment-control limits match. Equivalent. |
| 7.2.3 Station and map aggregation | Qualifying exact identities; median per peer then median across peers; separate Joint-Spot median; identical identity set for segment support; reported identities are not independent sites. | Same reducers, support thresholds, locator example and -1 dB versus +6 dB counterexample. Equivalent. |
| 7.2.4 Joint Evidence Share | Joint divided by all retained outcomes; mean peer fractions versus pooled counts; zero-Joint peers with outcomes contribute; absent peers do not; no win-rate interpretation. | Same denominator, contributors, split station-support vote and 45% versus 73.6% example. Equivalent. |
| 7.2.5 Neighborhood | Local within-identity medians followed by median across identities; correction before aggregation; Target maximum; no contributor-count minimum; absence omitted; membership can move reference. | Same two-stage construction, asymmetry, singleton/empty cases, physical-site limits and +2 to +5 dB example. Equivalent. |
| 7.3 introduction and 7.3.1 opportunities | Success self-confirms one opportunity; Miss needs specific RX/TX endpoint evidence and same-cycle Target activity; neither observed is unknown; no duplicate opportunity or synthetic SNR. | Correct receiver/transmitter must supply each witness; same classification table and no double counting. Equivalent. |
| 7.3.2 rates | Per-identity minimum opportunities; successes/(successes+Misses); equal-peer mean versus pooled rate; 70% versus 86.4% example. | Same formula, qualifying population and arithmetic. Equivalent. |
| 7.3.3 Reach | Qualifying identities with at least one success; breadth distinct from consistency; monotonic only for fixed peer population with previous evidence retained. | Same denominator and variable-population duration caveat. Equivalent. |
| 7.3.4 successful SNR | Normalized/consolidated successes only; Miss has no SNR; more marginal successes may lower SNR while improving reception; conditional observed-network result. | Same censoring and interpretation restrictions. Equivalent. |
| 7.4.1 scope | Locator-based spherical geometry; maximum-distance exclusion before aggregation/export; global witnesses and moving filter; solar classification is Target-local at cycle time. | Same geometry values, boundaries and population distinction. Equivalent. |
| 7.4.2 geography | Distance bins preserve selected gaps; peer-median SNR; IQR at three peers, min-max at two, point at one; no SNR for Miss-only peers. | Same bins and spread rules, with unambiguous German 1000 km. Equivalent. |
| 7.4.3 chronology | Full-window aligned bins, partial final bin, missing stays missing; Joint-only Delta layer versus all-outcome coverage; Performance deviation from each path's own full-run successful baseline; minimum three successes; one peer-bin median; support includes all opportunities. | Same populations, baseline, bin rules, missingness and support weighting. Equivalent. |
| 7.4.4 folding | Joint values pooled by UTC hour; Performance one peer/date/hour median; unequal numbers of represented dates still affect weight; panel-specific two-date eligibility; represented date-hour denominators and boundary-hour effect; pooled-per-peer/hour rates then equal-peer average; folding alone is not recurrence proof. | All population, weight and denominator distinctions retained, including a Joint-only date versus a one-sided-only second date. Equivalent. |
| 7.4.5 selected paths | One exact identity; own chronology/folded reducers; singleton rates coincide; native focused points are processed units; detector focus uses completed results and candidate-specific guides. | Same identity, aggregation, native-versus-raw distinction, focus and no-redetection semantics. Equivalent. |
| 7.4.6 spread/display | IQR descriptive, temporal minimum five values; contributing unit depends on view; relative density normalized within panel; correction-shifted cells; raw statistics unchanged; nonlinear Benchmark axis and histogram length; linear Performance SNR. | Same display meanings, thresholds, invariants and interpretation limits. Equivalent. |
| 7.5.1 dependence/bias | Many reports are not independent experiments; balancing/medians do not remove systematic calibration, reporting or propagation bias; no automatic inferential or causal results. | Same restrictions. The previous separate aggregation-limit paragraph is merged here without losing its named biases. Equivalent. |
| 7.5.2 repeatability/control | Depth, breadth, consistency, separate-run repeatability and physical control; shared views are not independent replication. | Same support hierarchy and reporting boundary. Equivalent. |
| 7.5.3 validation | Dataset, date, source revision/version and calculation needed for validation claims; dated checks are not timeless guarantees. | Same provenance requirements and bounded interpretation. Equivalent. |
| 7.6 introduction and departure | Explicitly experimental/optional expert overview; native Joint-only path evidence; independent of display bins; +8 to +1 means residual -7 without identifying which side changed. | Same optional scope, evidence, sign example and causal caution. Equivalent. |
| 7.6.2 baseline/scale | Candidate-excluded supported pre/post 10-minute medians within six hours; four cells each; equal flanks; missing not filled; centered pooled residual scale; MAD/half-IQR/zero-zero fallback; score descriptive. | Same support, calculation and fallback boundary; no universal 0.5 dB floor. Equivalent. |
| 7.6.3 qualification | Candidate-excluded baseline; absolute and robust-relative event-median gates, baseline agreement and two-thirds sign agreement all required; dB tolerance not z tolerance; no duration discount. | Same four conditions and distinction between median agreement and low variability. Equivalent. |
| 7.6.4 boundaries/classes | Individually qualifying same-sign anchors; trim and retest; weaker interiors allowed; rescued core keeps original baseline; all classes share gates; first-last span not continuous physical duration. | Same eligibility, retained interval and one/three/30-minute class boundaries. Equivalent. |
| 7.6.5 context/limits | Paths qualify separately; cross-path labels only review context; components/one-sided context do not strengthen events; no multiple-event significance correction or independent-sample claim; causal control needed. | Same diagnostic, statistical and causal limits. Equivalent. |

## Preservation decisions

- Shared reported-power normalization moved to foundations and explicitly names both Benchmark and Performance. Reference correction and Delta SNR remain Benchmark-specific.
- The previous Performance aggregation reminder is covered by 7.3.2. Its general calibration/reporting/propagation/dependence limits are retained explicitly in 7.5.1.
- Chronological and folded paragraphs were split into separate subsection homes; the peer/date/hour weighting and represented-date rules remain intact.
- Four retained display equations and all core numerical examples preserve their values, signs and meanings.
- The prior detector's precise cadence estimator, gap/guard formulas, pilot floor, neutral-bridge sequence rule, repeated shoulder expansion and exact cross-path proximity mechanics are omitted under the approved compact-overview scope. The text explicitly disclaims being an exhaustive algorithm specification. This is not an algorithm change.
- Marker-versus-peak and focused-overlay interpretation retain their detailed practical home in Section 2.5; they need not be repeated in the condensed detector overview.
- Prior numbered anchors remain compatibility aliases at the corresponding semantic homes. Scientific tests no longer infer scope from old alias order.

## Implementation evidence checked

- `config/delta_snr_outlier.py`: authoritative gate defaults, accepted ranges and 0.01 dB comparison tolerance; no robust-z tolerance.
- `ui/inspector/outlier_candidates.py`: constants for 10-minute cells, six-hour flanks and four-cell support; `_supported_baseline` averages supported flank medians after the agreement check; `_robust_flank_spread` uses positive MAD, otherwise half-IQR, otherwise 0.5 dB only when both vanish; event checks require departure, robust-z and two-thirds agreement; `_strong_anchor_trimmed_candidate` enforces and retests strong boundaries; `_classify_episode` defines one-unit impulse and >=3-unit, >=30-minute sustained events.
- Prior targeted review of `core/opportunity_engine.py`, `core/analysis_runner.py`, `core/compare_engine.py` and temporal figure reducers supports the retained identity, gating, denominator, aggregation and folded-date descriptions. No scientific runtime changes were made in this task.

## Corrections and verification boundary

Two German detector wording issues were reported to the source editor and corrected: half-IQR grammar and the wording for absence of multiple-event significance correction. No unresolved content defect remains in the reviewed source hashes.

The rendering test module preserves CRLF, compiles without importing or executing tests, and passes its whitespace diff check. The parent task runs focused/full pytest and PDF validation. This reviewer started no pytest process and makes no independent claim about those runs.

## Independent German review record

# Independent English/German Chapter 7 review

Reviewed 2026-10-05 by operator_review. Scope: the complete Chapter 7 introduction, six major sections, 26 subsections, all nine tables, four displayed equations, examples, qualifiers and outbound references. This is a semantic review of the parallel/co-authored pair against the approved six-part structure and compact experimental-detector scope, not an inference of parity from matching markup.

Accepted source snapshots:

- English `docs/doc_en.py`: SHA256 `650A21CD71A2A2D52A7D2078ACF0F4CD167E8A3E48FAC661BF83FDC6B7A22634`.
- German `docs/doc_de.py`: SHA256 `E9B100D3F331A8A56C0C043BC71657753193B68FAEE902545DCF55D679A27646`.

## Findings and verdict

Pass for scientific meaning, operator-language suitability and bilingual parity. No unresolved source-only, target-only or conflicting scientific unit was found. German retains the same conditioning, exclusions, missingness, weights, denominators, numerical examples, uncertainty and causal boundaries. Exact detector controls/classes were checked against `i18n.py`; the localized names agree. Established product terms remain intentionally untranslated where appropriate.

One stale English reference seen in an earlier intermediate snapshot at line 1219 pointed to Section 7.5 for Performance endpoint evidence. The editor had already corrected it to Section 7.3.1 in the accepted hash above; the correction was independently confirmed. No manual changes were made by this reviewer.

Ordinary German adaptations include decimal punctuation in prose, natural sentence splitting, and `Funkweg` for path. These do not change meaning. The prose is technically idiomatic; no wording change is necessary for correctness. The dense UTC-folding paragraph carries material denominator and boundary-hour rules and should not be shortened further without preserving those distinctions.

## English reverse outline, read independently

- Introduction: distinguishes Benchmark comparison from Performance success; moves from reports through constructed observation units to descriptive summaries; limits generalization.
- 7.1.1: one source per run; exact role-specific identity, same-cycle matching, full-locator remote identities, QTH geometry; extended-WSPR handling and database prerequisites; historical fallback links.
- 7.1.2: both directions/modes normalize successful SNR to reported 30 dBm; strongest-report consolidation, Neighborhood exception; best-observed meaning and calibration/selection limitations.
- 7.1.3: observable Target activity, global witness, Reference asymmetry; different exclusion order between modes; separate Performance endpoint requirement.
- 7.2.1: four outcome categories, Joint selection bias, no synthetic missing SNR; TX power and activity asymmetry; hash-error clustering and phase audit.
- 7.2.2: additive Reference correction, stable independently measured offset, Target-minus-Reference sign, RX cancellation/TX power dependence; whole-setup interpretation.
- 7.2.3: minimum support per exact identity, station medians then map median; pooled Joint median contrast, duplicate callsign/full-locator identities and map support.
- 7.2.4: Joint-share denominator, equal-station versus pooled-outcome weighting, zero-Joint contributors, station/outcome support and numerical contrast.
- 7.2.5: local within-identity then across-identity medians; absent contributor rules, no independent neighborhood-size minimum, membership-change example.
- 7.3.1: direction-specific endpoint evidence; success establishes opportunity; four success/external-evidence cases; unknown exclusion and no double counting.
- 7.3.2: successes divided by successes plus Misses; qualifying station minimum; equal-station and pooled-opportunity rates and example.
- 7.3.3: at-least-once breadth, fixed-population monotonicity versus changing qualifying population.
- 7.3.4: successful-only normalized strongest SNR, no Miss SNR, selection tradeoff and conditional network interpretation.
- 7.4.1: spherical geography, locator uncertainty, strict distance cutoff, global activity/moving-station witnesses, Target-only solar classification.
- 7.4.2: retained geographic population, deterministic distance bins, station-median SNR and three/two/one support rules.
- 7.4.3: chronological bins/missing intervals; Joint versus coverage layers; per-path successful-SNR baseline/deviation; one station-bin value and support-rate relationship.
- 7.4.4: UTC-hour folding, station-date-hour weighting, separate represented-date eligibility, averaging denominator including empty overlapping hours, boundary-hour limitation, recurrence caveat.
- 7.4.5: exact selected identity, direction/mode-specific SNR and support; native consolidated observations; focus does not refit the completed detector.
- 7.4.6: IQR/min-max are spread, five-value temporal versus three-station distance rules; panel-relative density; correction-aware cells and nonlinear display limits.
- 7.5.1: shared conditions and extended-WSPR phases create dependence; medians/balancing do not produce inference or independence.
- 7.5.2: depth, breadth, internal consistency, repeatability and experimental control; agreement of views is not replication.
- 7.5.3: dated, dataset/version-specific software-validation claims.
- 7.6.1: optional experimental native-Joint detector; actual times and sign relative to local baseline, not zero ΔSNR.
- 7.6.2: guarded two-sided cell baseline, minimum support, flank balancing; MAD/IQR/fallback scale and non-probabilistic z-score.
- 7.6.3: cadence-based candidates, candidate-excluded final baseline, four simultaneous checks and tolerance boundaries.
- 7.6.4: strong signed boundary anchors, retesting, retained interior values, fixed-baseline core rescue and common class qualification.
- 7.6.5: independently qualifying paths; contextual grouping/decomposition cannot improve qualification or establish cause/significance.

## German reverse outline, read independently

- Einstieg: Vergleich und Erfolg unterscheiden; aus Datenbankmeldungen gebildete Einheiten erklären; deskriptive Reichweite begrenzen.
- 7.1.1: Datenherkunft, Rufzeichen-/Locatorrollen und Zweiminutenzuordnung; Nachrichtenfolgen nicht rekonstruieren; Datenbankprüfung und historische Ausnahme verlinken.
- 7.1.2: erfolgreiche Werte auf 1 W beziehen; stärkste Meldung beziehungsweise lokale Mediane auswählen; keine nachträglich erzeugten Decodes oder Korrektur aller Anlagenunterschiede.
- 7.1.3: Target-Betrieb nachweisen; räumlich externe Zeugen zulassen, aber nicht mitzählen; Referenz nicht zusätzlich konditionieren; Ausschlussreihenfolge unterscheiden.
- 7.2.1: einseitige, gemeinsame und asynchrone Evidenz trennen; nichtzufälliges Fehlen und Hash-Zuordnungsfehler begrenzen die Aussage.
- 7.2.2: gemessenen Versatz nur zur Referenz addieren; Vorzeichen und Leistungsabhängigkeit prüfen; Ergebnis dem gesamten Aufbau zuordnen.
- 7.2.3: Stationsqualifikation vor Kartenmedian; gleiche Identitätsgewichte von gleichen Joint-Spot-Gewichten unterscheiden; Locator und Stationsminimum beachten.
- 7.2.4: alle beibehaltenen Outcomes im Nenner; Anteile mitteln oder Anzahlen zusammenzählen; Null-Joint-Stationen behalten, leere Stationen auslassen.
- 7.2.5: zweistufige lokale Referenzbildung; fehlende Beiträge auslassen; Mitgliedschaft kann den Wert ohne Target-Änderung verschieben.
- 7.3.1: RX-/TX-Aktivitätsnachweis an den richtigen Endpunkten; Erfolg einmal zählen; bestätigten Miss von Unbekannt trennen.
- 7.3.2: Gelegenheitsnenner und Stationsminimum; stationsgleichgewichtete und zusammengezählte Rate mit unterschiedlichen Fragen verbinden.
- 7.3.3: mindestens einmal erreichte Identitäten; zusätzliche Beobachtungen und wechselnde qualifizierende Population auseinanderhalten.
- 7.3.4: SNR nur erfolgreicher Decodes; schwächere zusätzliche Erfolge können Empfang verbessern und den SNR-Median senken.
- 7.4.1: berechnete Geografie und Filtergrenzen; Locator sind keine Antennenvermessung; Sonnenhöhe nur am Target.
- 7.4.2: vollständige Bereichspopulation; Entfernungsintervalle mit Lücken; Streuungsdarstellung nach Zahl beitragender Stationsmediane.
- 7.4.3: Zeitfolge mit fehlenden Intervallen; gemeinsame und einseitige Evidenz getrennt; Abweichung vom eigenen erfolgreichen Pegel; Unterstützung aus allen Gelegenheiten.
- 7.4.4: Tage nach UTC-Stunde bündeln; Gewichtung und vertretene Tage je Ebene; leere überlappende Stunden und Randstunden im Nenner; keine automatische Wiederholbarkeit.
- 7.4.5: eine exakte Station innerhalb der bestehenden Zulässigkeit; echte konsolidierte Zykluswerte; Fokusdarstellung ändert das Detektorergebnis nicht.
- 7.4.6: Streuung statt Konfidenz; relative Dichtefarben; Anzeigeintervalle und komprimierte Achsen ändern weder Beobachtungen noch Kennzahlen.
- 7.5.1: abhängige Beobachtungen und systematische Verzerrungen trotz Median und Stationsgleichgewichtung.
- 7.5.2: Evidenztiefe, Vielfalt, Konsistenz, Wiederholung und Kontrolle unterscheiden; gleiche Datenansichten sind keine Replikation.
- 7.5.3: Validierung nur mit Datensatz, Datum, Version und Verfahren einordnen.
- 7.6.1: experimentelle optionale Erkennung nativer Joint-Abweichungen; positives ΔSNR kann negative lokale Abweichung bedeuten.
- 7.6.2: beidseitige besetzte Zellen und Schutzabstand; gleiche Flankengewichte; Ersatzstreuung nur im Nullfall, z-Wert ohne Signifikanzbehauptung.
- 7.6.3: Kandidatenbildung nach Betriebsrhythmus; endgültige Basislinie ohne gesamten Kandidaten; alle vier Prüfungen und ihre Toleranzen.
- 7.6.4: starke gleichgerichtete Grenzpunkte, erneute Intervallprüfung, unveränderte Basislinie beim Kern; Ereignisklassen beschreiben beobachtete Zeitspannen.
- 7.6.5: jeder Funkweg qualifiziert separat; Gruppierung, Zerlegung und einseitige Meldungen liefern Kontext, keine zusätzliche Qualifikation oder Ursache.

## High-risk parity checks

Confirmed normalization `-15 dB @ 20 dBm -> -5 dB`; Reference correction `+1.5 dB` changes ΔSNR `+2 -> +0.5 dB`; station median `-1 dB` versus pooled `+6 dB`; JES `45%` versus `73.6%`; Neighborhood membership `+2 -> +5 dB`; Performance `70%` versus `86.4%`, Reach `100%`; SNR deviation `-7 - (-10) = +3 dB`; detector `+1 - (+8) = -7 dB`, robust z approximately `-4.72` at scale `1 dB`. All signs, units and denominators match.

The compact detector retains either-flank insufficiency, conditional 0.5 dB fallback, dB-only tolerance, two-thirds sign share including neutral observations, candidate-excluded baseline, strong anchored interval retesting, fixed-baseline core rescue, equal class requirements, and non-causal/non-significance limits. Its approved omission of microalgorithm implementation detail is not a bilingual loss.

## Structural and PDF-test compatibility checks

A read-only AST/source check found matching ordered anchors and outbound links, zero missing destinations, zero duplicate manual anchors, 26 subsections and four displayed equations per language. The nine table shapes match: identities 2 columns; activity 2; outcomes 2; ΔSNR sign 2; Benchmark weighting 3; Joint shares 2; Performance opportunity cases 4; Performance rates 3; detector qualification 2.

The existing updated `test_documentation_pdf.py` semantic ranges correspond to these actual tables. The Performance three-column rate summary is outside the four-column opportunity range. The detector has exactly one two-column table and its retained sign example satisfies the extraction contract. German `Vorzeichenübereinstimmung` remains covered by the print-only label-wrap test; localized `Baseline-Übereinstimmung` is already hyphenated and does not require the previous `Basislinien...` special case. Compatibility anchors and six semantic major anchors remain available. No PDF test edits were necessary in this review.

No pytest or PDF generation was run. This review establishes source semantics and selector/test compatibility, not final typography, pagination or rendered link coordinates; root owns those checks. External protocol research and algorithm reimplementation were not repeated in this bounded parity review.
