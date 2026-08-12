# English–German Delta-SNR outlier documentation parity

## Source model

This is a source-led English-to-German integration. The user-supplied content
source is `C:/Users/marku/Downloads/doc_en_outlier_detection.py`, SHA-256
`551FAB1D6DC566FCE49313CE210FB10F22DED4C8AD60032E6F1199FC3B7E494F`.
The integrated English text is the translation source after factual correction
against detector version `native-residual-episode-v7`, configuration/schema
contracts, `i18n.py`, and export behavior. The German manual is translated from
that corrected English meaning, not from `README.md` or an earlier German draft.

Final integrated source hashes after the parity review are:

- `docs/doc_en.py`: `9932DAE2E344D0044F84D485B8C641A0A2E92160D0CB6D7A16331163EC3D0F4C`;
- `docs/doc_de.py`: `DA04A03BCCA5D667A29FD5B344779A2C90BCF6BD5E505060A89A100DE652D776`.

## Section-level parity checklist

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
