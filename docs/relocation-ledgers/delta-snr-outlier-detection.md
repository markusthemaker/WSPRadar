# Delta-SNR outlier detection documentation restructures

## Scope and accepted source

This completed bilingual integration adds the optional Delta-SNR outlier
detector to the operator and scientific manuals and adjusts the authorized Part
II structure. The user-supplied English source was
`C:/Users/marku/Downloads/doc_en_outlier_detection.py`, SHA-256
`551FAB1D6DC566FCE49313CE210FB10F22DED4C8AD60032E6F1199FC3B7E494F`.

The supplied source was validated against detector version
`native-residual-episode-v7`, the saved-configuration contract, localized UI
labels and export behavior before integration. Corrections applied in both
languages include simultaneous Joint Spot and complete Scheduled Pair support,
the pilot-baseline stage, inclusive grouping thresholds, strong-anchor trimming,
cross-path timing/context, exact defaults and ranges, and the manual Run
lifecycle.

## Initial integration: relocated material

Former Chapter 5, **Troubleshooting and Data Quality**, moved intact in meaning
to Section 4.7 under **Controls, Configuration, and Troubleshooting**. Its former
sections 5.1–5.6 are now Sections 4.7.1–4.7.6. English and German headings,
Table-of-Contents entries and visible cross-reference numbers were updated.

The established compatibility anchors `sec-6`, `sec-6-1`, `sec-6-2`,
`sec-6-3`, `sec-6-4`, `sec-6-5` and `sec-6-6` remain in their authoritative
relocated positions. The new hierarchy adds `sec-5-7`; no duplicate heading or
second source of the troubleshooting guidance was created.

Classification: unique, correct and useful operator guidance relocated without
semantic removal. No original troubleshooting passage was dropped or rendered
obsolete, so there is no unretained passage requiring verbatim quotation.

## Initial integration: authoritative homes

- Section 4.6 owns the exact optional toggle, three control labels, defaults,
  ranges, saved/manual-run behavior and practical selectivity consequences.
- Chapter 5 owns expert operator use, a non-formal method explanation,
  descriptive event classes, cross-path context, interpretation and diagnosis.
- Section 7.11 owns the complete scientific construction, notation and formulas.
- Sections 8.3 and 8.4 own outlier-specific reproducibility and export limits.
- `docs/architecture.md` owns implementation boundaries, v7 anchor trimming and
  the disabled compatibility boundary.

This ownership split follows the manual's complex multi-stage-method rule:
operator action and interpretation remain in Part II, while formulas and the
exact scientific method remain in Chapter 7 and are cross-linked rather than
copied.

## Initial integration: preservation and compatibility audit

- All useful pre-existing English and German manual guidance was preserved.
- No source reference was added, removed or renumbered.
- Existing `sec-6*` inbound links continue to resolve.
- New English and German outlier anchors are structurally parallel.
- `README.md` is regenerated from the authoritative English manual; it is not
  edited independently.

## 2026-08-15 approved accessibility restructure

The user subsequently approved a second bilingual restructure to separate
practical expert use from the formal detector construction. This is a
documentation-only change: detector version `native-residual-episode-v7`, its
configuration, report model, output and runtime behavior remain unchanged.
Mathematical-symbol changes are confined to Section 7.11; symbols outside that
section retain their established meaning and spelling.

The authoritative destinations are now:

| Previous home | Classification and disposition | New authoritative home |
| --- | --- | --- |
| Chapter 5 introduction and practical purpose, report-reading, event-shape, cross-path-context, interpretation and investigation guidance | Unique useful expert guidance, simplified for operator accessibility without changing its evidence or claim boundaries | Part I, Section 2.5, explicitly introduced as an optional expert diagnostic tool rather than routine guidance |
| Chapter 5 detailed baseline, robust-scale, cadence-aware grouping, qualification, core rescue and boundary-trimming construction | Scientifically useful detail duplicated by, or required to complete, the formal method; consolidated rather than discarded | Section 7.11, the sole home of exact detector notation, formulas and construction |
| Section 4.7, **Troubleshooting and Data Quality**, including its six subsections | Unique useful general diagnostic guidance; restored intact in meaning to a standalone chapter | Part II, Chapter 5, **Troubleshooting and Data Quality** |
| Section 4.6 detector controls | Already in the correct operating-reference layer; retained | Section 4.6, the sole home of the exact toggle, three controls, defaults, ranges and Run lifecycle |

Part II is consequently **Controls and Troubleshooting**. Section 2.5 links to
Section 4.6 for exact controls and to Section 7.11 for the formal method rather
than repeating either. Chapter 5 remains general troubleshooting and is not a
second home for the outlier algorithm.

Compatibility-anchor disposition is explicit:

- `sec-outlier` and the established `sec-outlier-*` inbound aliases remain with
  the corresponding relocated practical or formal outlier meaning;
- `sec-6`, `sec-6-1` through `sec-6-6`, and `sec-5-7` remain with the restored
  troubleshooting content;
- the pre-existing `sec-2-5` Reference-design compatibility anchor is not
  repurposed for the new visible Section 2.5;
- every retained anchor resolves once and no compatibility alias creates a
  second visible heading.

The English and German manuals use the same authoritative destinations and
claim boundaries. German prose is adapted naturally for radio-amateur readers;
formulas, thresholds, signs and units remain scientifically equivalent. No
source reference is removed or renumbered by this restructure, and no useful
operator or scientific guidance is left solely in the superseded Chapter 5 or
Section 4.7 locations.
