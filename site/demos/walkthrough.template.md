<!-- section: hero -->
# Demo title

Introduce the experiment and the question it answers.

<!-- section: setup -->
## Experiment and interpretation

Start the setup directly after the hero without a separate introductory block.
Present it unboxed like the evidence sections. The default layout omits an
At a glance card section; retain any underlying metric data in configuration.

Describe the complete experimental setup, its source, the compared station
identities, and the observation period. Preserve configuration values and the
qualifications needed to interpret the comparison.

Explain the sign and weighting of the reported measure. Link the original
publication and reviewed resources where they support the explanation.

<!-- section: step-1 -->
## Read the first result

Explain what the reader should inspect, what the available evidence shows, and
what it does not establish. Keep figures in the layout configuration's explicit
media assignments. The layout places text beside the figure and then across
the full width below it. Keep this heading unnumbered; the layout supplies
the step number. For a table-only or intentionally text-only step, set
`layout: "full"` in the configuration so no figure placeholder is shown.

Use the shared Run in WSPRadar App action and the demo's explicit `launch_url`
in `site/demo_walkthroughs.json`. Keep the reviewed full version-1 configuration
URL at wspradar.org, including `run=1` and the results fragment, to load these
settings and request the analysis. Do not add a separate configuration-download
action.
