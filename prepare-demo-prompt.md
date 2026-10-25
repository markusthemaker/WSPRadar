# Reusable prompt: WSPRadar guided demos

Prepare, refine or review a **WSPRadar guided demo** using the supplied material. Follow the task mode specified below. Write for a **ham radio operator using WSPRadar for the first time**. The reader understands antennas, propagation and basic radio terminology, but needs help with WSPRadar’s controls, evidence categories and interpretation.

The goal is a practical, engaging story: understand the experiment, run the analysis, read the results, discover a few useful insights, and learn how to investigate their own station. Use **“guided demo”**, not “demo walkthrough.”

## Material for this demo

- **Experiment and practical question:** [insert]
- **Task:** [create a new demo / refine the attached existing demo / review only / implement approved changes]
- **Current demo, if any:** [attach]
- **Current export, configuration, figures and results-page reference:** [attach]
- **Approved editorial reference:** Demo #1 in its latest approved form, supplied separately. Use it to judge tone, depth and pacing. A supplied refined Zander guide can be an additional example.
- **Paper or supporting reference, if relevant:** [attach or link]
- **Dedicated technical-comparison PDF, if available:** [link]
- **Specific settings, decisions or content to preserve:** [insert]
- **Approved changes, if implementing a previous review:** [paste the approved change table or exact wording]

Treat examples from other demos as editorial references. Do not transfer their findings, thresholds or settings to this experiment. Use current case evidence for factual claims. Check that figures, settings and text describe the same run; flag material conflicts or missing evidence rather than inventing details.

## Preserve the right amount of detail

If refining an existing demo, **use the supplied version as the baseline**. Preserve its structure, useful explanations, figures, evidence tables, worked examples, navigation, links and technical markup. Make targeted edits where they improve understanding. Do not broadly rewrite, halve the length or remove useful material merely to make it shorter. Identify any substantive removal in the change log.

For **implement approved changes**, use the approved wording exactly at the agreed locations. Preserve everything outside those passages, including formatting, punctuation and integration syntax. If you notice a material issue outside that scope, flag it separately without changing the text. Ordinary creation or refinement does not require an additional approval stage when the task already authorizes it.

Compress repeated numerical narration: arithmetic already evident from a table, several counts making the same point, or a third example adding no new lesson. Retain numbers that establish the result, explain a setting, reveal a meaningful contrast or show how much evidence supports a conclusion. After a table, explain the pattern or practical implication rather than repeating its category totals. Preserve complementary examples that teach different relationships between SNR and decoding; two contrasting cases are not automatically redundant.

Use the approved reference to judge depth. Do not impose a blanket word-count target. Some sections need only a short interpretation; median weighting or a material limitation may need more explanation.

## Walk through the actual results page

Follow the current results-page structure and exact control labels. In an existing demo, preserve its section order and integration markers; flag any mismatch with the current UI instead of silently rearranging it.

Cover every relevant analysis view: setup and settings, overview cards, both geographic maps, Decodes & Stations by SNR, Benchmark Statistics, both temporal views, Station Insights, selected-station views, Drill-Down and saving the evidence. Use the order appropriate to the supplied page. Explain unavailable panels when relevant; do not invent controls or results.

State the relevant scope, station selection, filters and time aggregation before examples that depend on them. Verify Inspector and selected-station settings separately; do not assume their controls share a setting or that changing one changes the other. Distinguish chronological time bins from UTC-hour panels that combine the same hour across dates.

For each results section, naturally answer:

1. **Where do I go?** Give the navigation or action needed.
2. **What should I look at?** Explain the essential axis, color, grouping or evidence distinction.
3. **What is the main pattern?** State the finding before supporting detail.
4. **What does it mean for a ham operator?** Connect it to signal margin, reception, coverage, consistency or experiment design.
5. **What should I check next?** Add a useful action or limitation when it changes the interpretation.

Use this as an editorial checklist, not five repeated subheadings. Keep the prose connected and avoid explaining every chart feature equally.

## Make the interpretation useful

- **Maps:** describe geographic patterns and meaningful contrasts. Connect ΔSNR with observed decode differences where supported. Do not force agreement between the maps or narrate every sector’s counts.
- **Decodes & Stations by SNR:** explain what paired reports, one-sided reports and distinct-station reach add to the story. Where supported, connect additional weak-signal reports with the possible practical benefit of extra signal margin. Avoid a census of every panel endpoint.
- **Statistics:** explain what the distributions and summaries reveal. Distinguish station-balanced and observation-weighted results when applicable. Keep representative examples that teach the difference, and explain why agreement or disagreement between summaries matters.
- **Time views:** ask whether the pattern persists, whether apparent changes have enough support, and whether reporting periods are comparable. Use time aggregation as a practical inspection tool when available.
- **Station Insights:** choose a station with a clear teaching purpose and briefly explain the choice. Its example should reveal something useful about the summaries, time grouping, variation or signal margin versus decode counts.
- **Drill-Down:** connect a summary to actual observations. Retain useful existing examples; for a new demo, use enough rows to teach a point without creating a data audit. Check each example against the exact table or file readers are told to use. If it comes from a different export or linked source records, say where to find it. A row in an export does not establish its visibility in the current UI; do not invent a filter or toggle to explain the difference.

The desired style is: **“Here is the pattern, here is the evidence that matters, and here is what you can learn from it.”** Keep tables that make comparisons easier, then interpret them without repeating every cell in prose.

## Keep the science precise

- Identify Target, Reference and the remote stations correctly for the analysis mode. TX and RX comparisons give them different roles. Introduce these roles and the station-entry identity used in the export, such as callsign plus reported locator, in the setup.
- Check the ΔSNR sign and decode-ratio orientation. Explain which setup a value favors and distinguish signal strength, report counts and distinct stations.
- Explain experiment-specific thresholds in the settings section, including any sparse-data compromise. Distinguish per-station and per-segment requirements, and keep ΔSNR qualification separate from decode support rules. A minimum count does not establish statistical confidence.
- Distinguish paired observations from one-sided reports. A station can contribute both in different cycles. An absent report supplies no SNR to subtract; an observed count ratio is not an absolute decoding-success probability.
- Check how cumulative counts combine. Verify whether categories such as **Both (Async)** or exclusive stations are plotted, separately annotated or already included in totals; do not add them twice. Verify how stations enter each curve: reconciling final endpoints does not mean the panels add at every intermediate SNR cutoff. Keep observed-event unions distinct from combined decode totals, where a Joint event may contribute once to each setup’s total. Explain these mechanics only where they affect the reader’s interpretation.
- Verify whether figures and tables use raw, corrected or power-normalized SNR. Explain material differences so readers can compare views correctly.
- Check common operation and reporting spans before attributing count differences to antenna performance. Missing reports do not establish transmitter shutdown or its cause.
- Describe medians, spreads and shaded bands according to what they actually represent. Do not call a spread band a confidence interval or treat two differently weighted medians as an uncertainty range.
- Separate observation from explanation. A weak-signal pattern may be consistent with extra margin helping reception; it does not establish a universal decoding threshold or prove why the other signal was absent.
- Keep conclusions specific to the sampled paths, installations and test period. Do not turn an observed difference into a universal antenna-gain claim.

Keep these checks in the reasoning. Include caveats in the reader-facing text where they materially affect interpretation; avoid repeating a disclaimer in every paragraph.

## Paper comparison and conclusion

If a publication is relevant, briefly explain where the findings agree, what WSPRadar adds and any material limits to the comparison. Link the dedicated comparison PDF for reconstruction details. Keep that technical reconstruction outside the guided demo unless explicitly requested.

Finish with a concise, evidence-based conclusion answering the original practical question. Explain what the operator learned and how to preserve or repeat the analysis using the controls actually available. Be encouraging without hype.

## Style and deliverables

Use plain English, short paragraphs, active verbs and the app’s exact labels. Define WSPRadar-specific terms on first use. Use bold sparingly for actions and key insights. Keep the tone technically credible, approachable and suitable for a first-time user. Do not assign a demo number unless requested.

Identify chart elements by their labels, positions or meaning when colors vary between light and dark themes. Keep useful color explanations that match the supplied figures. Explain observable behavior in plain language rather than using implementation terms such as “gate,” unless that term appears in the UI and needs explanation.

For **create**, **refine** or **implement approved changes**, return:

1. **The complete, publishable Markdown file**, preserving existing section markers, placeholders, asset references, links and other integration syntax.
2. **A brief change log in chat:** what changed, why, what important material was preserved, and any unresolved factual issue. For a new demo, summarize the main editorial choices instead.

For **review only**, leave the file unchanged and return a concise table with the precise location, suggested change, reason and exact proposed text. State whether each proposal is an addition or replacement, and distinguish necessary corrections from optional refinements. If the guide already works well, say so; do not invent changes to fill a quota.

Before delivering, verify quoted numbers and interpretations against the supplied evidence; check full results-page coverage, navigation and links; and remove avoidable repetition. Preserve enough detail for the reader to follow and understand the analysis, while making the important patterns easy to find.

Keep all verification and cleanup within the selected task mode. For approved edits, check the final diff against the agreed changes and confirm that everything else remains unchanged. Report material checks that remain unresolved, such as live UI behavior or link availability; an inaccessible link is not automatically a broken link.