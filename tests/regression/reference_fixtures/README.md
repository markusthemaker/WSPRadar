# Publication reconstructions and independent reference evidence

The comparison figures exercise WSPRadar's scientific pipeline against frozen
source reports. They are visual integration checks, accompanied by numerical
regressions. They do not become independent validation merely by resembling a
publication: the paper-derived features and separately calculated reference
expectations remain the independent checking side of the comparison.

## Current maintenance command locations

Specialist builders, scientific verification tools, PDF helpers and the PDF
publisher now live in `scripts/internal/`. The complete current command index is
[scripts/README.md](../../../scripts/README.md). For a fixture instruction that
names `scripts/build_*.py` or `scripts/verify_*.py`, use the same filename under
`scripts/internal/`; its documented arguments and scientific inputs are unchanged.
`scripts/sync_reference_figure_pdfs.py` likewise moved under `scripts/internal/`.

Individual frozen fixture READMEs can be covered by their manifests' file hashes.
Those READMEs, provenance paths and historical builder hashes are preserved as
part of the original evidence package. This index supplies the current command
locations without rewriting that frozen record. The routine regression runner
and README synchronizer remain directly under `scripts/`.

## Required reconstruction path

```text
Frozen source reports + saved scientific configuration
  -> WSPRadar configuration validation and analysis/query construction
  -> generated scientific SQL executed against those reports
  -> production post-fetch filtering and evidence preparation
  -> production map/station aggregation and Inspector selection
  -> production paired observations and statistical/figure recipes
  -> publication-style reconstruction and WSPRadar export view

Independent paper features and expected results -> assertions only
```

Builders must obtain plotted SNR, Delta SNR, eligibility and selection from the
production stages that own those quantities. Do not read an `expected_*` table
as reconstructed observations, inject captured SQL-result rows in place of SQL
execution, or copy WSPRadar's scientific formulas into a presentation script.
Expected files may be read after calculation to check its result, without
replacing or correcting any production value. A mismatch must stop generation
or be handled by an already explicit, reviewed discrepancy policy; never refresh
the expected files merely to make a new result pass.

Where the application already supplies the required time bins, quartiles,
histogram or density preparation, use that production implementation. Additional
paper-style smoothing, bin edges, axes and units are permitted presentation
steps on the production observations. Record them separately from scientific
processing. The reconstruction and app-view panels must use the same retained
evidence population unless a difference is explicitly described.

## Deliberate review transformations

| Figure | Production evidence | Additional review or presentation step |
| --- | --- | --- |
| Griffiths Figure 3 comparison | Retained same-cycle paired Delta SNR; production 1-hour and 12-hour temporal recipes and white export | Linear-dB grayscale hourly density matching the paper's axes, with every original pair shown using fixed larger black markers; the colorbar describes the density background only; no smoothing or per-hour normalization |
| Griffiths Figure 3 tail diagnostic | Strongest-report paired differences from the production pipeline | Separate all-report Cartesian join illustrates weaker duplicate combinations; these are not WSPRadar-retained observations |
| Griffiths Figure 6 comparison | Retained paired differences and production folded-hour density/statistics | Fixed, documented smoothing and contour presentation for comparison with the paper |
| Zander Figure 4 comparison | Production paired differences and fine histogram recipe | Rebinning to the paper's coarse bins, converting counts to density, and a supplemental sample standard deviation of the production pairs for the paper comparison |
| Vanhamel Figure 6 comparison | Selected-station production pairs, corrected endpoint SNR, and 12-hour temporal export | Reception-number axis and common endpoint power-scale conversion for the paper view; unchanged native UTC density projected onto exact reception spans in an added explanatory panel; Delta SNR unchanged |
| Milazzo Figures 6 and 7 | Production post-fetch retention and paired evidence | Pre-gate SQL endpoint reports remain visible as an explicitly separate archive review; common 37 dBm display scale and paper-pixel readout calibration |

The original publication panels and their independently read coordinates are
external evidence. Their pixel calibration and matching tolerances must not be
fitted to force a production result to agree. Unresolved publication differences
remain visible and separately documented.

## Execution boundary and regression protection

The offline SQL adapter executes the generated scientific query expressions
against the frozen population, with bounded equivalents for the required
ClickHouse functions. It removes the output serialization clause. This tests
the SQL and downstream WSPRadar methods without a live provider request; it does
not certify native ClickHouse type/optimizer behavior or exact geographic
distance, HTTP transport, caches, admission control, or Streamlit callbacks.
Those infrastructure contracts have their own tests. Frozen captures also limit
claims about activity outside the captured population.

Tests must demonstrate both numerical agreement and the origin of the plotted
values. Evidence preparation must work with expected-output reads forbidden;
controlled source or production-output mutations must affect the reconstruction
or fail its independent assertions. Matching an expected table to itself is not
a scientific regression.

Rebuild figures with their checked-in presentation builders. Review the PNG and
rendered PDF, then update only presentation entries in the relevant fixture
manifest. Preserve the source reports, publication annotations, scientific
configuration and independent numerical expectations. Keep native generated
plots and text as vectors; original publication raster panels stay raster.

Finally run `python scripts/internal/sync_reference_figure_pdfs.py` to refresh the copies
served by demo links, and `python scripts/internal/sync_reference_figure_pdfs.py --check`
to verify that all published copies match the reviewed fixture PDFs. This
publication step does not depend on the retained PNG companions.
