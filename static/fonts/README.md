# Browser fonts

These unmodified WOFF2 files replace the former Google Fonts CSS import.
Rajdhani 600/700 normal and Space Mono 400/700 normal plus 400 italic retain
all character subsets returned by the original request. The browser downloads
only faces and Unicode ranges used by rendered text. The font definitions remain
in `ui/css.py`, including `font-display: swap`.

Files are served at `app/static/fonts/` with Streamlit static serving enabled.
Names include the upstream release version. Replace the versioned filenames and
CSS together when updating; do not overwrite an older version with new bytes.

Material Symbols Rounded is provided by Streamlit's own frontend. WSPRadar
retains the matching CSS class without downloading a second copy or referencing
Streamlit's private hashed asset filename. PDF generation continues to use its
separate embedded DejaVu fonts.

## Licenses and sources

Retrieved on 2026-09-14 from Google's public font service. The original font
files are distributed under the SIL Open Font License 1.1; the complete
copyright notices and licenses are in `Rajdhani-OFL.txt` and `SpaceMono-OFL.txt`.
No font files were modified or subsetted by WSPRadar.

- [Rajdhani source and license](https://github.com/google/fonts/tree/main/ofl/rajdhani)
- [Space Mono source and license](https://github.com/google/fonts/tree/main/ofl/spacemono)

| Bundled file | Original source |
| --- | --- |
| `rajdhani-v17-600-normal-devanagari.woff2` | [Google Fonts](https://fonts.gstatic.com/s/rajdhani/v17/LDI2apCSOBg7S-QT7pbYF_Oqeef2kg.woff2) |
| `rajdhani-v17-600-normal-latin-ext.woff2` | [Google Fonts](https://fonts.gstatic.com/s/rajdhani/v17/LDI2apCSOBg7S-QT7pbYF_Oleef2kg.woff2) |
| `rajdhani-v17-600-normal-latin.woff2` | [Google Fonts](https://fonts.gstatic.com/s/rajdhani/v17/LDI2apCSOBg7S-QT7pbYF_Oreec.woff2) |
| `rajdhani-v17-700-normal-devanagari.woff2` | [Google Fonts](https://fonts.gstatic.com/s/rajdhani/v17/LDI2apCSOBg7S-QT7pa8FvOqeef2kg.woff2) |
| `rajdhani-v17-700-normal-latin-ext.woff2` | [Google Fonts](https://fonts.gstatic.com/s/rajdhani/v17/LDI2apCSOBg7S-QT7pa8FvOleef2kg.woff2) |
| `rajdhani-v17-700-normal-latin.woff2` | [Google Fonts](https://fonts.gstatic.com/s/rajdhani/v17/LDI2apCSOBg7S-QT7pa8FvOreec.woff2) |
| `space-mono-v17-400-italic-vietnamese.woff2` | [Google Fonts](https://fonts.gstatic.com/s/spacemono/v17/i7dNIFZifjKcF5UAWdDRYERMSHK_IwU.woff2) |
| `space-mono-v17-400-italic-latin-ext.woff2` | [Google Fonts](https://fonts.gstatic.com/s/spacemono/v17/i7dNIFZifjKcF5UAWdDRYERMSXK_IwU.woff2) |
| `space-mono-v17-400-italic-latin.woff2` | [Google Fonts](https://fonts.gstatic.com/s/spacemono/v17/i7dNIFZifjKcF5UAWdDRYERMR3K_.woff2) |
| `space-mono-v17-400-normal-vietnamese.woff2` | [Google Fonts](https://fonts.gstatic.com/s/spacemono/v17/i7dPIFZifjKcF5UAWdDRYE58RWq7.woff2) |
| `space-mono-v17-400-normal-latin-ext.woff2` | [Google Fonts](https://fonts.gstatic.com/s/spacemono/v17/i7dPIFZifjKcF5UAWdDRYE98RWq7.woff2) |
| `space-mono-v17-400-normal-latin.woff2` | [Google Fonts](https://fonts.gstatic.com/s/spacemono/v17/i7dPIFZifjKcF5UAWdDRYEF8RQ.woff2) |
| `space-mono-v17-700-normal-vietnamese.woff2` | [Google Fonts](https://fonts.gstatic.com/s/spacemono/v17/i7dMIFZifjKcF5UAWdDRaPpZUFqaHjyV.woff2) |
| `space-mono-v17-700-normal-latin-ext.woff2` | [Google Fonts](https://fonts.gstatic.com/s/spacemono/v17/i7dMIFZifjKcF5UAWdDRaPpZUFuaHjyV.woff2) |
| `space-mono-v17-700-normal-latin.woff2` | [Google Fonts](https://fonts.gstatic.com/s/spacemono/v17/i7dMIFZifjKcF5UAWdDRaPpZUFWaHg.woff2) |
