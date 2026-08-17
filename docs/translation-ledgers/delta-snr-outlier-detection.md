# English–German Delta-SNR outlier documentation parity

## Source model

This is a source-led English-to-German integration. The user-supplied content
source is `C:/Users/marku/Downloads/doc_en_outlier_detection.py`, SHA-256
`551FAB1D6DC566FCE49313CE210FB10F22DED4C8AD60032E6F1199FC3B7E494F`.
The integrated English text is the translation source after factual correction
against detector version `native-residual-episode-v7`, configuration/schema
contracts, `i18n.py`, and export behavior. The German manual is translated from
that corrected English meaning, not from `README.md` or an earlier German draft.

The pre-restructure integrated source hashes recorded after the initial parity
review were:

- `docs/doc_en.py`: `9932DAE2E344D0044F84D485B8C641A0A2E92160D0CB6D7A16331163EC3D0F4C`;
- `docs/doc_de.py`: `DA04A03BCCA5D667A29FD5B344779A2C90BCF6BD5E505060A89A100DE652D776`.

## Initial integration parity checklist

| Scope | Required semantic units | English/German status |
| --- | --- | --- |
| Part II and TOC | Authorized Part II name; Chapter 4/5 hierarchy; retained `sec-6*` compatibility anchors | Matched |
| Section 4.6 | Toggle; three exact controls; defaults; ranges; applicability; persistence; explicit Run lifecycle; selectivity direction | Matched |
| Chapter 5 introduction and 5.1 | Time-local path question; native paired unit; Joint Spot and complete Scheduled Pair; one-sided exclusion; display-bin independence; non-causal boundary | Matched |
| Section 5.2 | 10-minute cells; six-hour flanks; four cells per side; no imputation; stability gate; equal-side baseline; MAD/IQR/0.5 dB scale | Matched |
| Section 5.3 | Cadence and outage rule; pilot guard; inclusive grouping floor; neutral bridge; final candidate exclusion/guard/refinement | Matched |
| Section 5.4 | Same three gates for all durations; two-thirds sign agreement; failed-group core rescue; no child baseline refit; strong anchors; boundary trimming and requalification | Matched |
| Section 5.5 | Spot impulse, Short burst and Sustained excursion as descriptive classes; observed-span boundary | Matched |
| Section 5.6 | Same-sign temporal grouping tolerance; path-specific, directionally coherent, scope-wide and unavailable-direction multiple-path context; no qualification/significance effect | Matched |
| Section 5.7 | Rejection/abstention reasons; diagnostic workflow; exploratory versus confirmatory use; bounded claim language | Matched |
| Section 7.11 | Analysis target; all twelve method stages; formulas, symbols, numbers, signs and units; descriptive robust-z limitation; no causal or inferential claim | Matched |
| Sections 8.3–8.4 | Outlier reproducibility record; enabled export metadata/markers; no dedicated report table; disabled omission | Matched |

## Localization choices

Exact visible German labels follow `i18n.py`, including:

- `ΔSNR-Ausreißerkandidaten melden`;
- `Minimale absolute ΔSNR-Abweichung (dB)`;
- `Minimaler robuster z-Wert`;
- `Maximaler Unterschied zwischen Baseline davor/danach (dB)`;
- `Spot-Impuls`, `Kurzer Ausbruch` and `Anhaltende Auslenkung`.

Established product terms Target, Reference, Benchmark, Joint Spot, Station
Insights and Drill-Down remain unchanged. Narrative terminology uses natural
amateur-radio German such as **Funkweg**, **gepaarte Evidenzeinheit**,
**Residuum**, **lokale Basislinie**, **Stützflanke** and **Evidenzkadenz**.
Decimal points are retained in literal control values and formulas.

## Semantic and structural audit

Independent reverse outlines were compared over Sections 4.6–5.7, 7.11 and the
new 8.3/8.4 passages. Every heading, paragraph, table row, list item, formula,
threshold, qualifier, warning, cross-reference and claim boundary has a
counterpart. Chapter 7 formulas are byte-identical between languages. The only
intentional divergences are ordinary German syntax and the approved localized
UI labels above; no scientific or operational meaning differs. No unresolved
source-only, target-only or conflicting unit remains.

## 2026-08-15 parallel restructure source model

The accepted English and German starting revision for the accessibility
restructure is repository commit
`e8cf74755d0573f891cd0a1680c0625847d4c0e8`. Both manuals are maintained in
parallel against the user-approved specification from 2026-08-15; neither
language is treated as an unrecorded sole master for this change.

Final authoritative manual hashes after the accessibility restructure and
native-language parity review are:

- `docs/doc_en.py`: `84EDD5BE4E6AFA80BD88BA1EA13295798F1188477ABF2ED3F29B357EAAA34CAC`;
- `docs/doc_de.py`: `D7AEC4F224B8912D9F0D244E637EB2F79ADF643637B4CCD28A7AE2E6907EF635`.

The approved specification relocates practical outlier use to Part I Section
2.5, restores **Troubleshooting and Data Quality** as Part II Chapter 5, retains
the exact controls in Section 4.6, and consolidates the exact detector method in
Section 7.11. Section 2.5 must identify the feature as an optional expert
diagnostic tool rather than routine guidance. The restructure changes no
runtime behavior. It introduces no new physical or causal claim.

## Accessibility-restructure parity checklist

| Scope | Required semantic units | English/German status |
| --- | --- | --- |
| Part I Section 2.5 | Explicit expert-diagnostic scope; when to use the option; plain-language detection flow; report reading; selectivity controls by cross-reference; investigation workflow; evidence and claim limits | Matched |
| Section 4.6 | Exact toggle and three control labels, defaults, ranges, saved configuration and explicit Run lifecycle retained without algorithm duplication | Matched |
| Part II Chapter 5 | General Troubleshooting and Data Quality plus all six former Section 4.7 diagnostic topics restored intact in meaning | Matched |
| Section 7.11 structure | Radio/analysis question first; evidence and notation; stable local baseline and robust variability; cadence-aware pilot grouping; candidate-excluded final baseline; qualification, strong-core rescue and boundary trimming; descriptive classes and cross-path context | Matched |
| Section 7.11 notation | Mnemonic `B^P`, `B`, `r^P`, `r`, `S_robust`, `C`, `G`, `F`, `W^P`, `W^B`, `E`, `m_E`, `z_E` and `agree(E)`; established `D_min`, `Z_min` and `H_max` retained | Matched |
| Symbol scope | Formula and symbol changes confined to Section 7.11; every symbol and formula outside Section 7.11 unchanged | Matched |
| Compatibility anchors | `sec-outlier` and `sec-outlier-*` follow corresponding outlier meaning; `sec-6*` and `sec-5-7` follow troubleshooting; legacy `sec-2-5` is not repurposed; each anchor resolves once | Matched |
| Cross-references and ownership | Section 2.5 points to Section 4.6 and Section 7.11; Chapter 5 is not a duplicate outlier-method home; TOC hierarchy and section numbers agree | Matched |

The English version uses concise practical language in Section 2.5 and layered
HamSCI-level explanation in Section 7.11. The German version preserves the same
semantic units, qualifications, emphasis and claim boundaries in natural
technical amateur-radio German rather than mirroring English syntax. Equations,
thresholds, signs, units and detector logic remain equivalent. Established
English product terms and exact localized German UI labels remain intentional
localizations. There is no intentional semantic divergence.

## 2026-08-15 additive export parity note

The initial integration checklist records the export behavior that existed at
that historical review point. Its statement that no dedicated report table was
present is superseded by the current additive export contract. Sections 2.5.4
and 8.4 now describe, with matched English/German meaning, the enabled-only
`table_delta_snr_outlier_event_paths.csv` path-event summary and
`table_delta_snr_outlier_paired_evidence.csv` chronological native paired-unit
evidence table. Both languages preserve the same package-local ID boundary,
deliberate path/direction duplication, combined-versus-path class distinction,
header-only enabled-empty behavior, and complete disabled omission. No formula,
detector threshold, event qualification rule, manual anchor or TOC structure
changed in this additive update.

## 2026-08-16 default-policy parity note

The English and German control tables now give the same new-analysis defaults:
`6.0 dB` minimum absolute Delta-SNR departure, `3.0` minimum robust z-score, and
`3.0 dB` maximum pre/post baseline difference. Both manuals explain that this
combination prioritizes large absolute movements while retaining an independent
path-relative robust-variability gate. Formulas, symbols, accepted ranges,
duration-class definitions, event qualification mechanics, anchors and TOC
structure are unchanged. Version-1 omitted-value compatibility remains an
engineering contract rather than a different operator-facing default.

## 2026-08-16 Drill-Down context parity note

Section 2.5.3 now gives both per-timeframe actions the same operational meaning
in English and German. **Show in Station Insights** / **In Station Insights
anzeigen** selects the exact path, preloads its detector-derived candidate context
and navigates to Station Insights; **Show Drill-Down Details** /
**Drill-Down-Details anzeigen** makes the same selection and preload but targets
Drill-Down directly. Both manuals state that the interval includes the complete
supported pre-event baseline flank, cadence-guarded provisional episode and
post-event baseline flank, clipped only to the completed analysis window. They
also preserve the same exception to the manual 24-hour zoom limit: detector
context may be longer, while the focused metric figure retains one point per
native evidence unit rather than aggregating those units into time-bin medians. This
addition changes no detector formula, qualification threshold, reported strong-
anchor boundary or causal-claim limitation.

## 2026-08-17 focused Drill-Down terminology parity note

The focused Drill-Down controls now use the approved bilingual phrase matrix:
**Center date (UTC)** / **Datum der Fenstermitte (UTC)**, **Center time (UTC)** /
**Uhrzeit der Fenstermitte (UTC)**, **Outlier Focus** / **Ausreißerfokus**, and
**Filter table** / **Tabelle filtern**. The former visible **Focus date/time**,
**12h Event focus** and **Fit detector context** variants have no active
operator-facing role. One Outlier Focus now means the exact retained detector-
support interval: supported pre-event flank, guarded provisional episode and
supported post-event flank, clipped to the completed analysis window. Both
languages state that table filtering affects only displayed rows, while the
focus interval limits both focused figures and the table. Both also preserve
the same native-unit definitions and the same warning that robust-z and
absolute-departure lines are detector guides rather than confidence intervals
and that crossing one guide alone is insufficient. This is a presentation and
focus-selection simplification; it changes no detector calculation, threshold,
candidate boundary, saved scientific configuration or causal-claim limit.

## 2026-08-17 focused-episode marker and band parity note

The focused Benchmark legend now uses **Qualifying candidate unit** /
**Qualifizierende Kandidateneinheit** for every identical star and **Focused
episode** / **Fokussierte Episode** for the muted selection band. Both languages
state the same evidence rule: a star denotes one native unit belonging to a
reported candidate that individually meets both the configured departure and
robust-z gates; weaker grouped units retained between strong anchors remain
ordinary points. The band denotes only the selected candidate's reported
retained-evidence interval, padded by half one native evidence-unit width at
each end and clipped to the focus window so an impulse remains visible. It does
not claim a physical-event duration or confidence interval. Expected local
Delta SNR, pre/post baselines and detector guides belong only to the focused
episode; another starred candidate can have a different local baseline and
robust spread. This presentation change does not alter detector qualification,
reported candidate bounds, native evidence, saved scientific configuration or
causal-claim limits.

The single marker in the all-path temporal plot follows the same bilingual
eligibility distinction. **Strongest individually qualifying native-unit
residual per review event** / **stärkstes Residuum einer einzeln qualifizierenden
nativen Einheit je Prüfereignis** is the marker rule; an unsupported or
nonqualifying episode peak cannot represent the event. **Largest single-cycle
departure** / **Größte Einzelzyklusabweichung** remains a separate report and
export metric containing the true greatest-absolute retained residual of the
path event. No candidate membership, gate, retained evidence or exported peak
value changes through this marker-selection refinement.
