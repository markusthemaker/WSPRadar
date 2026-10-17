# Landing-page assets

`source/` preserves all 55 files supplied in `WSPRadar_landing_assets.zip` without modification, including every SVG and PNG icon, both logo concepts, artwork, sample diagram, contact sheet, and the asset pack's original README and manifest. The previous separately supplied header is retained as `source/hero/WSPRadar-Global-Signal-Insights.png` (2172 × 724 pixels). The original file was named `WSPRadar_ Global Signal Insights.png`.

The active public-website header is the later supplied `WSPR Insights Across Earth.png`, preserved byte-for-byte as `source/hero/WSPR-Insights-Across-Earth.png` (2172 × 724 pixels; 2,352,260 bytes). The preparation script now reads this image while retaining the earlier header and all other supplied artwork. This asset change does not replace the application's header or publish the website.

The supplied ZIP's SHA-256 is `b81a3a1de62b07dc3a0d411f08309b79ba30ed0c7a4e0c991269492af998aae4`. Archive entries were checked for traversal, absolute paths, and symbolic links before extraction; each extracted file was compared byte-for-byte with the archive. Instructions in the supplied README describe the asset pack and do not override the website task or repository instructions.

`web/` contains separately encoded browser derivatives and unchanged copies of the neon SVG icons. `manifest.json` records source and derivative hashes, dimensions, encoding settings, and an explicit `publish_files` list. The static builder should copy only that list, rather than publishing the complete retained source collection. Original scientific figures belong to the imported content bundle and are not processed by this tool.

The hero keeps its supplied English wording in both website languages. It is illustrative artwork, not a measured WSPR result. Provide the meaningful heading and description in accessible semantic HTML; small raster text must not be the only source of essential information on a phone. The full-page mockup is a visual reference and is not embedded in the website.

The standalone radar emblem is used for the navigation logo, with a live HTML wordmark. The separate logo-lockup concept is retained for future work; its original wordmark transparency has visible rough edges, so it is not the production navigation asset.

## Reproduction

Use Python with Pillow and WebP support (initially verified with Pillow 12.2.0):

```powershell
python scripts/prepare_landing_assets.py
python scripts/prepare_landing_assets.py --check
```

The script reads only the retained sources, uses Lanczos resampling directly from each original, refuses upscaling, and deterministically encodes each derivative. `--check` compares rebuilt bytes and the manifest with the saved files. Pillow/libwebp changes can change encoded bytes, so rerender and review when changing the image toolchain.

The handwritten callout uses the locally served Caveat font, obtained with its OFL license from the official Google Fonts repository. Original font files, metadata, and provenance are retained in `source/fonts/`. Font preparation additionally requires FontTools (verified with 4.63.0); the script creates a static 400-weight Latin/Latin Extended/punctuation TTF and includes that file and its license in `publish_files`. Font timestamps remain fixed for byte-for-byte reproduction. The original variable font remains intact, and no system font is redistributed. Review font output again when changing FontTools.

For the previous header, WebP quality 94, WebP quality 90, and lossless WebP were compared at each output size. Quality 94 was selected after inspection of embedded text, thin signal paths, and map detail at 1280 pixels and full size. At 1280 pixels it was 174,978 bytes versus 680,890 bytes for lossless WebP; at 2172 pixels it was 389,122 bytes versus 1,694,462 bytes for lossless WebP and 2,226,720 bytes for the supplied PNG. The supplied original remains intact. Small logo derivatives use lossless WebP to retain their transparency and edges. PNG fallbacks are also included.

## Active header encoding review

The current `WSPR-Insights-Across-Earth.png` was compared at 1280 pixels and full size, including AVIF supported by Pillow 12.2.0. All WebP variants use method 6; AVIF candidates use speed 6, 4:4:4 chroma, and one encoder thread. Quality values are encoder-specific and are not equivalent across formats.

| Dimensions | WebP quality 94 | WebP quality 90 | Lossless WebP | AVIF quality 90 | AVIF quality 80 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1280 × 427 | 199,548 bytes | 156,686 bytes | 731,298 bytes | 200,511 bytes | 140,273 bytes |
| 2172 × 724 | 446,566 bytes | 350,064 bytes | 1,820,090 bytes | 459,326 bytes | 314,237 bytes |

WebP quality 94 remains the active encoding after visual review of embedded headings, small handwriting, thin signal paths, and map detail. It retains the existing WebP/PNG browser contract; the reviewed AVIF quality-90 candidates provided no bandwidth saving, while AVIF quality 80 trades a lower encoder setting for smaller files. The full-size selected WebP is about 81% smaller than the supplied PNG. The manifest records the selected responsive widths, exact dimensions, sizes, and hashes. AVIF comparison files are review-only and are not published or required to reproduce the selected browser assets.
