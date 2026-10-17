# Calibration walkthrough sources

The supplied English draft and the previous English/German walkthroughs are
retained unchanged as editorial history. Active copy belongs in the two
`walkthrough.*.md` files in the parent directory.

`figure1-source.svg` preserves the reviewed original appearance of Figure 1
from Vanhamel et al. (2022), DOI 10.1155/2022/4809313. Its raster equipment
images were decoded from the PDF color space to a lossless RGB PNG so browsers
render the source colors correctly. The unchanged embedded CMYK JPEG and the
decoded PNG are retained beside it.

The reviewed dark adaptation, its complete provenance (source URL, PDF hash,
crop coordinates, transformations and validation), and the native dark
Benchmark Evidence rendering are in `../resources/`. Only files explicitly
listed in that resource manifest are published by the website build. These
source archives are not automatically copied into the built website.

The native calibration plot can be reproduced in the private application using
`scripts/internal/render_vanhamel_calibration_walkthrough.py`. No private
application code is included in this public source archive.
