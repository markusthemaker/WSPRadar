# Caveat handwriting font

Downloaded on October 15, 2026 from the official Google Fonts repository:

- Original variable font: https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/Caveat%5Bwght%5D.ttf
- License: https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/OFL.txt
- Family metadata: https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/METADATA.pb
- Official family directory: https://github.com/google/fonts/tree/main/ofl/caveat

The retained `Caveat-variable.ttf` has SHA-256 `0bdb6b660482d31531b3945849fba5916b3ef8695da7024a9e6b9ee3c4157988`. The official metadata identifies the upstream source as `googlefonts/caveat`, commit `59745e818ef7973e11e70cb1358d0e902b56c5fc`, and the weight range as 400–700. The original font, metadata, and OFL license are retained unchanged here. The original GitHub filename was `Caveat[wght].ttf`.

`scripts/prepare_landing_assets.py` uses FontTools to create a static 400-weight font with Latin, Latin Extended, and general punctuation, retaining contextual glyph substitutions. The smaller browser TTF is served locally as `web/fonts/caveat-hand-latin.ttf`, accompanied by `web/fonts/Caveat-OFL.txt`. The build requires no Google Fonts request or system-font redistribution. The website may use `WSPRadar Hand` as its CSS family alias; the font's internal family remains Caveat.

The font is licensed under the SIL Open Font License 1.1; the complete copyright notice and license are in `Caveat-OFL.txt`. No system handwriting font is copied into the repository.
