# Delta-SNR outlier detection and Part II restructure

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

## Relocated material

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

## Added authoritative homes

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

## Preservation and compatibility audit

- All useful pre-existing English and German manual guidance was preserved.
- No source reference was added, removed or renumbered.
- Existing `sec-6*` inbound links continue to resolve.
- New English and German outlier anchors are structurally parallel.
- `README.md` is regenerated from the authoritative English manual; it is not
  edited independently.

