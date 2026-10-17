# WSPRadar landing-page asset pack

## Contents
- `icons/neon/*.svg`: 15 original, transparent, standalone, scalable icons for the dark landing page.
- `icons/png-512/*.png`: separate transparent 512×512 px versions of every neon icon.
- `icons/monochrome/*.svg`: matching single-color icons using `currentColor`.
- `diagrams/how-it-works-flow.svg` and `.png`: concise four-stage data-flow diagram.
- `brand/`: previous image-generated neon emblem and wordmark *concept* artwork.
- `hero/`: previous Europe-centred hero illustration and separate transparent globe artwork.
- `icon-contact-sheet.png`: visual index of the production-ready icons.

## Suggested use
- Use native SVG icons through `<img src="assets/icons/neon/tx-station.svg" alt="">` where decorative.
- Prefer live HTML text for all headings, descriptions, navigation and CTAs: do not embed UI wording in a background image.
- The stage names in the flow represent WSPR radio transmission → decoding/upload → public reports → WSPRadar analysis. WSPRadar never directly receives RF.
- For a performant site, use the individual SVGs and load large decorative artwork lazily except the hero.
- Use original repository brand assets as the authority for the official WSPRadar logo; previous image-generated brand images are design references until approved.
- Hero mockups and the icon pack are not evidence of actual propagation paths, data magnitudes or station reach.

## Design tokens
- Background: `#06101f`
- Surface/card: `#0b182d`
- Card border: `#254963`
- Primary accent: `#39ff14`
- Secondary accent: `#40b6ff`
- Primary text: `#f8fbff`
- Muted text: `#a6c8df`

SVG files are text/vector assets that can be edited directly. PNGs have transparent backgrounds.
