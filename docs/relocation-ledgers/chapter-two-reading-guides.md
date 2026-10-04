# Chapter 2: practical reading guides and Benchmark-first order

## Accepted scope and source model

User-approved integration of the RX Benchmark pilot pattern throughout Chapter 2.
Parallel/co-authored English and German update from the recorded working-tree
manuals at HEAD `2e42701cbc89b0d89da281e1a3c15094d947320b`, including the earlier
approved setup and scientific-example pilot. The common specification is:
operating question; established terms; figure meaning, interpretation and next
check; Benchmark first with equal Performance depth; content-fitted guide tables;
natural technical German for radio amateurs. Earlier experimental English-only
drafts informed presentation but are not an independent scientific source.

- EN baseline SHA-256: `7278aef429d40d48ea67346bb75cd5b4e1faedf4989aee47ec2fff98a10c42eb`.
- DE baseline SHA-256: `cf9cc8b97454c30e482a9bb1cff462a429b7eab941aee2e9b61ea1232d78cb67`.

## Destinations and preservation

| Previous location | Authoritative destination | Disposition |
|---|---|---|
| 2.3 RX Benchmark, including 2.3.1-2 | 2.1, including 2.1.1-2 | Move with all compatibility anchors; shared guide adopts approved pilot; setup and neighborhood keep their facts with canonical terminology. |
| 2.4 TX Benchmark, including 2.4.1-2 | 2.2, including 2.2.1-2 | Corresponding TX guide; normalization, same-receiver cycles, RF controls and neighborhood conditions retained. |
| 2.1 RX Performance | 2.3 | Reach, both rate weightings, successful SNR, temporal and station interpretation retained and explained by figure. |
| 2.2 TX Performance | 2.4 | Same structure adapted to active receivers; power, denominator and attribution boundaries retained. |
| 2.5 diagnostics | 2.5, existing subsections | Local restructuring into report/action/control tables; detector criteria, focus, boundaries, timing and export facts retained. |
| Repeated paired/matched vocabulary | Chapter 2 introduction and the relevant guide | Define Joint Spots once; use ΔSNR for values and retain direction-specific construction. |
| Full Joint/one-sided/async taxonomy in shared introductions | 7.6, with short support check and link in 2.1/2.2 | Existing formal definitions remain; operator guide concentrates on figures and what can be concluded. |

No scientific formulas or Chapters 3-8 were changed by this integration.
Conclusion templates remain with their design; Benchmark ΔSNR wording is
standardized without strengthening claims. A folded UTC-hour profile is a
possible pattern to check across dates, not proof of recurrence. Performance
selected-path SNR is identified as reported-power-normalized; extra observation
time provides more opportunities but does not guarantee an increasing reach
percentage when the qualifying population changes.

EN/DE pre-edit and post-edit reviews cover each section, table row, condition,
weighting, missingness boundary, numerical value, UI label and conclusion.
Independent review checklists are retained in the task working record. German
uses the actual localized UI titles and idiomatic RF/station vocabulary; no
intentional difference in scientific meaning is introduced.

## Original passages replaced locally or moved

The following verbatim source passages account for text not retained literally.
Unless a destination above states otherwise, each is rewritten in its mapped
Chapter 2 section with its useful meaning retained. They are recorded separately
from the normative manual so editorial provenance does not burden the reader.
Headings below include mechanical renumbering; replaced paragraphs include
terminology changes as well as paragraph/table restructuring.

### EN original passages

<details><summary>Source unit 1</summary>

````text
#### 2.1 RX Performance
````

</details>

<details><summary>Source unit 2</summary>

````text
**Question answered.** Which confirmed peer TX cycles did the Target RX decode; how consistently did it do so; what successful SNR did it observe; and where and when did that behavior occur?
````

</details>

<details><summary>Source unit 3</summary>

````text
**Minimum valid setup.** Use the exact Target reporting callsign and QTH, one band and a window with observable Target receiver activity. Keep the receive chain stable. Performance does not introduce a Reference and does not isolate one component of the receive system.
````

</details>

<details><summary>Source unit 4</summary>

````text
**What WSPRadar evaluates.** Within the selected band, exact peer identity and Target-active cycle, a confirmed RX opportunity exists when the Target RX decodes the peer TX or another eligible RX decodes that same peer TX. `Heard by Target` is a success whether or not another RX also reports the peer TX: the Target RX report directly confirms both the transmitting peer TX and the receiving Target RX. `Heard by others only` is a Miss when another eligible RX confirms the peer TX transmission but the active Target RX does not decode it. A Target-only success is retained as provenance within successes and opportunities, never added a second time. If the Target RX has no activity evidence, another receiver's report does not prove that the Target RX was listening. The exact classification is in [Section 7.4](#sec-7-4).
````

</details>

<details><summary>Source unit 5</summary>

````text
**Read the evidence path.** On the **Map**, sector color shows the Station-balanced Decode Rate of qualifying remote transmitters in each distance-and-direction segment. Station markers and the footer distinguish paths heard by the Target at least once from paths heard only elsewhere. Use this first to locate broad RX footprint and directional structure, not to judge receiver sensitivity from color alone.
````

</details>

<details><summary>Source unit 6</summary>

````text
In **Segment Inspector**, first compare station breadth with confirmed-opportunity depth. Many opportunities from only a few transmitters are deep but narrow evidence; agreement across many transmitters is broader. Then read the three Performance views together:
````

</details>

<details><summary>Source unit 7</summary>

````text
* **At-least-once reach** asks which qualifying transmitters were heard at least once during the window. It measures breadth and normally increases with a longer run.
* **Decode Rate** asks how consistently the Target decoded confirmed opportunities. The Station-balanced rate gives each transmitter one vote; the Opportunity-level rate gives each confirmed cycle one vote. A difference between them shows that high-volume transmitters behave differently from the wider station population.
* **Successful Target SNR** describes only successful decodes. It helps show whether the successful signals themselves differ with distance, but misses have no Target SNR and cannot appear there.
````

</details>

<details><summary>Source unit 8</summary>

````text
In **Temporal Evidence**, successful-SNR deviation compares each transmitter path with its own usual successful level during the run. Values above `0 dB` mean successful decodes were stronger than usual for their respective paths; values below `0 dB` mean weaker. The accompanying station and opportunity evidence shows whether a signal-level change coincided with changed Decode Rate and whether the pattern was broadly supported. The chronological view identifies changes during the run; the folded UTC-hour view identifies recurring daily behavior.
````

</details>

<details><summary>Source unit 9</summary>

````text
In **Station Insights**, read each transmitter's Decode Rate together with `Heard by Target` and `Heard by others only` counts. Select a typical path, an outlier and any path contributing unusually large evidence. **Selected Station Evidence** then shows the actual successful SNR and opportunity history of one transmitter path rather than the station-relative summary across the segment. **Drill-Down** verifies the contributing cycles and distinguishes externally supported successes from the Target-only provenance subset, which is already included in successes and opportunities.
````

</details>

<details><summary>Source unit 10</summary>

````text
**Common interpretation patterns.** Broad reach with high Decode Rate means many paths opened and were decoded consistently. Broad reach with lower Decode Rate means many paths opened at least once but were intermittent. Limited reach with high Decode Rate means fewer qualifying paths opened, but those that did were comparatively consistent. If successful SNR remains steady or rises while Decode Rate falls, weaker signals may have disappeared below the decoder threshold, leaving only stronger successful decodes. A pattern confined to one azimuth, distance range or UTC period can be operationally useful, but it describes the installed receiver under those paths and conditions rather than a context-free sensitivity number.
````

</details>

<details><summary>Source unit 11</summary>

````text
**Boundary and confirmation.** RX Performance combines antenna, feedline, receiver, gain, filtering, decoder, local noise, interference and propagation. It does not directly measure receiver sensitivity, antenna gain, absolute noise or propagation mode. Repeat a suspected pattern in another suitable window. When the intended conclusion is about one hardware change, use a controlled RX Benchmark or a crossover rather than relying only on separated before-and-after Performance runs.
````

</details>

<details><summary>Source unit 12</summary>

````text
#### 2.2 TX Performance
````

</details>

<details><summary>Source unit 13</summary>

````text
**Question answered.** Which peer RX stations shown to be active decoded the Target TX; how consistently did they do so; what successful SNR did they report; and where and when did that behavior occur?
````

</details>

<details><summary>Source unit 14</summary>

````text
**Minimum valid setup.** Use the exact Target callsign and QTH, one band and a window in which the Target transmitter was operating. Keep the RF path, schedule and actual power stable, and report power accurately. Performance evaluates the complete transmitted station rather than one isolated component.
````

</details>

<details><summary>Source unit 15</summary>

````text
**What WSPRadar evaluates.** Within the selected band, exact peer identity and Target-active cycle, a confirmed TX opportunity exists when the peer RX decodes the Target TX or that same peer RX decodes another qualifying same-band transmitter. `Target heard` is a success whether or not the peer RX also reports another transmitter: its Target TX report directly confirms both endpoints. `Other signals heard only` is a Miss when that peer RX reports another qualifying transmitter but not the active Target TX. A Target-only success is retained as provenance within successes and opportunities, never added a second time. A report of the Target TX at some other receiver proves Target TX activity, not that this particular silent peer RX was listening. The exact denominator is in [Section 7.4](#sec-7-4).
````

</details>

<details><summary>Source unit 16</summary>

````text
**Read the evidence path.** On the **Map**, sector color shows the Station-balanced Decode Rate of qualifying active receivers in each distance-and-direction segment. Markers and footer counts distinguish receivers that heard the Target at least once from receivers that heard only other qualifying signals. Use the map to locate practical transmitted footprint and directional structure.
````

</details>

<details><summary>Source unit 17</summary>

````text
In **Segment Inspector**, compare receiver breadth with confirmed-opportunity depth, then read the three Performance views together:
````

</details>

<details><summary>Source unit 18</summary>

````text
* **At-least-once reach** asks which qualifying active receivers heard the Target at least once during the window.
* **Decode Rate** asks how consistently the Target was reported within confirmed receiver opportunities. The Station-balanced and Opportunity-level rates reveal whether frequently reporting receivers behave differently from the wider receiver population.
* **Successful Target SNR** shows normalized SNR for successful Target reports. It is conditional on a decode and depends on the accuracy of reported transmit power.
````

</details>

<details><summary>Source unit 19</summary>

````text
In **Temporal Evidence**, successful-SNR deviation shows when successful reports were stronger or weaker than each receiver path's own usual successful level. The accompanying station and opportunity stacks show whether a change in successful SNR was accompanied by a change in practical detectability and how much support each time bin contains. Chronological change and recurring UTC-hour behavior should be distinguished.
````

</details>

<details><summary>Source unit 20</summary>

````text
In **Station Insights**, read each receiver's rate with its `Target heard` and `Other signals heard only` counts. **Selected Station Evidence** exposes one receiver path's actual successful SNR and opportunity history, which helps determine whether the segment summary reflects many receivers or masks a path-specific effect. **Drill-Down** verifies Target TX reports, externally confirmed peer RX activity and the Target-only provenance subset already included in successes and opportunities.
````

</details>

<details><summary>Source unit 21</summary>

````text
**Common interpretation patterns.** Broad reach and high Decode Rate indicate that many qualifying active receivers heard the Target consistently. Broad reach and lower Decode Rate indicate a large but intermittent footprint. A persistent advantage in one azimuth or distance range can be consistent with installed antenna and terrain behavior; a short isolated improvement can instead reflect propagation or receiver availability. Stable successful SNR with falling Decode Rate can indicate that only stronger surviving reports remain. Differences between station-balanced and Opportunity-level rates reveal whether a few high-volume receivers are driving the pooled view.
````

</details>

<details><summary>Source unit 22</summary>

````text
**Boundary and confirmation.** TX Performance combines transmitter, actual power, feedline, matching, antenna, terrain, remote receiver systems, noise and propagation. Reported-power normalization cannot correct an incorrect power report or an unmeasured feedline loss. The result does not directly measure EIRP, efficiency, antenna gain or take-off angle. Repeat the pattern across another suitable window; use TX Benchmark when the question is specifically whether one transmit path differs from another.
````

</details>

<details><summary>Source unit 23</summary>

````text
#### 2.3 RX Benchmark
````

</details>

<details><summary>Source unit 24</summary>

````text
**Question answered.** How did Target reception differ from the selected Reference for the same remote transmitter identities and WSPR cycles?
````

</details>

<details><summary>Source unit 25</summary>

````text
**Shared RX Benchmark evidence.** Paired Delta SNR requires comparable same-transmitter, same-cycle evidence from Target and Reference. Positive values favor the Target; negative values favor the Reference. Decode Outcomes retain Joint, Only Target, Only Reference and asynchronous evidence around that paired subset. Joint Evidence Share shows how much retained evidence is pairable; it is not a Target win rate. Reference uptime needs independent verification; the Target-Active Gate makes one-sided categories asymmetric.
````

</details>

<details><summary>Source unit 26</summary>

````text
**Read the evidence path.** On the **Map**, sector color summarizes the station-balanced median Delta SNR for each distance-and-direction segment. Markers distinguish Joint and one-sided transmitter identities. Read color with station and spot counts: a striking sector supported by few transmitters describes narrower evidence than a similar result across many paths.
````

</details>

<details><summary>Source unit 27</summary>

````text
In **Segment Inspector**, Decode Outcomes show two complementary compositions: station breadth and observation volume. Station Medians give each remote transmitter one Delta-SNR value and equal weight; the Joint-Spot distribution shows every paired observation, giving prolific transmitters more influence. Agreement supports a broad shift; disagreement shows different patterns across stations and observations. [Section 7.7](#sec-7-7) illustrates this weighting difference.
````

</details>

<details><summary>Source unit 28</summary>

````text
**Temporal Evidence** shows change during the run and possible UTC-hour patterns. Check the chronological evidence across individual dates before calling a folded pattern recurring. Read it with Benchmark Evidence Coverage: distinguish broad Joint support from a pattern confined to a small paired subset. One-sided evidence can reveal practical near-threshold differences, but supplies no missing-side SNR.
````

</details>

<details><summary>Source unit 29</summary>

````text
In **Station Insights**, read each transmitter's median Delta SNR with its Joint and one-sided counts. **Selected Station Evidence** shows one path's paired values and coverage over time: is it representative, exceptional or intermittent? **Drill-Down** checks the intended transmitter, cycle, exact callsign and locator identities, and correction sign.
````

</details>

<details><summary>Source unit 30</summary>

````text
**Interpret and act.** Mostly same-sign station medians, broad Joint coverage and recurrence over time or adjacent segments support a consistent complete-path difference; test whether it persists in a new run. A pooled shift without a station-median shift may come from a few prolific transmitters: inspect their counts and paths. A clear paired median with many Only Target or Only Reference outcomes describes only part of the decode evidence: check Reference availability and one-sided coverage before generalising. A direction- or UTC-specific difference can still be useful; bound the conclusion to those conditions and repeat that comparison.
````

</details>

<details><summary>Source unit 31</summary>

````text
**Boundary and confirmation.** Joint-only Delta SNR cannot describe missed signals. Same-cycle matching controls transmitter and timing, but not receiver-chain, antenna, noise or QTH differences. Strengthen the result with enough stations supplying Joint evidence, independently known Reference uptime, repetition and the design-specific checks below.
````

</details>

<details><summary>Source unit 32</summary>

````text
##### 2.3.1 Reference Setup/Station
````

</details>

<details><summary>Source unit 33</summary>

````text
This is the strongest RX design for local-path attribution. It still compares complete documented receive paths unless receiver, audio, gain, decoder and routing differences are characterized. A broad recurring Delta-SNR shift with compatible one-sided evidence supports one path outperforming the other under the tested conditions. Use common-input calibration, a splitter-output swap or hardware crossover for confirmation; these can distinguish the tested component from a persistent chain offset. [Appendix C](#sec-reference-snr-calibration) explains Reference SNR calibration; [Appendix A](#sec-a) covers separate WSJT-X instances.
````

</details>

<details><summary>Source unit 34</summary>

````text
<blockquote class="evidence-conclusion"><p>Under the documented simultaneous controlled RX setup, paired Delta SNR and Decode Outcomes described the observed difference between the Target and Reference receive paths for the shared transmitters, cycles and selected geographic scope.</p></blockquote>
````

</details>

<details><summary>Source unit 35</summary>

````text
Choose an identifiable complete Reference receiver with known QTH, callsign, equipment, operating schedule and local environment. RX pairs share transmitter and cycle; Target and Reference remain distinct complete receiving stations with their own antennas, hardware, signal paths and local noise. WSPRadar resolves the reported Reference grid-4 from database observations in the selected window. Matching Target grid-4 is allowed, but does not prove co-location.
````

</details>

<details><summary>Source unit 36</summary>

````text
<blockquote class="evidence-conclusion"><p>For the shared transmitter paths and cycles in this run, paired Delta SNR and Decode Outcomes described how the two complete receiving stations compared under their respective environments.</p></blockquote>
````

</details>

<details><summary>Source unit 37</summary>

````text
##### 2.3.2 Reference Neighborhood
````

</details>

<details><summary>Source unit 38</summary>

````text
Here, the contributing local receivers are those with qualifying reports of the same remote transmitter in the same WSPR cycle. The Reference therefore represents the receivers observed on that transmitter path and cycle, not every receiver inside the radius. Paired Delta SNR additionally requires a qualifying Target report for that same transmitter and cycle.
````

</details>

<details><summary>Source unit 39</summary>

````text
<blockquote class="evidence-conclusion"><p>For the selected band, window, transmitter paths and cycles, the Target’s complete receiving station showed the reported paired Delta SNR and Decode Outcomes relative to the contributing local receiver neighborhood. This does not establish that its antenna has a corresponding gain advantage.</p></blockquote>
````

</details>

<details><summary>Source unit 40</summary>

````text
#### 2.4 TX Benchmark
````

</details>

<details><summary>Source unit 41</summary>

````text
**Question answered.** How did the Target transmitter differ from the selected Reference at shared remote receivers?
````

</details>

<details><summary>Source unit 42</summary>

````text
**Shared TX Benchmark evidence.** Same-cycle TX Benchmark compares Target and Reference at the same remote receiver in the same WSPR cycle. Successful TX SNR is normalized to reported power before Delta SNR is formed; the result therefore depends directly on accurate power reporting. Decode Outcomes preserve Joint and one-sided evidence, but an exclusive observation has no missing-side SNR and is not power-normalized.
````

</details>

<details><summary>Source unit 43</summary>

````text
**Read the evidence path.** On the **Map**, sector color summarizes station-balanced median Delta SNR across remote receivers. Marker and footer categories show Joint and one-sided receiver evidence. Read each sector with receiver breadth and Joint-Spot depth.
````

</details>

<details><summary>Source unit 44</summary>

````text
In **Segment Inspector**, compare the station-level Decode Outcomes with the observation-level composition. Station Medians give each remote receiver one equal vote, while Joint-Spot Delta SNR shows the full paired observation distribution. A shift shared across many receivers is different from one dominated by a few high-volume receivers.
````

</details>

<details><summary>Source unit 45</summary>

````text
**Temporal Evidence** shows whether Delta SNR changed through the run or recurred by UTC hour. Benchmark Evidence Coverage shows whether paired evidence remained broad through those times. Inspect whether the result is tied to one receiver, audio-frequency assignment or short interval.
````

</details>

<details><summary>Source unit 46</summary>

````text
In **Station Insights**, read each receiver's median Delta SNR with its Joint and one-sided counts. **Selected Station Evidence** reveals the paired result and evidence coverage at one receiver path. **Drill-Down** verifies receiver identity, reported powers, same-cycle pairing, and correction sign.
````

</details>

<details><summary>Source unit 47</summary>

````text
**Common interpretation patterns.** A consistent station-median shift across many receivers, directions and times supports a broad complete-transmit-path difference. A shift limited to one azimuth or distance range can indicate useful installed directional behavior without becoming a context-free gain value. Strong paired Delta SNR with substantial one-sided evidence means the strength difference and practical near-threshold reach must both be reported. A raw-pair median that differs from the station-median view indicates that high-volume receivers weight the observation-level evidence differently.
````

</details>

<details><summary>Source unit 48</summary>

````text
**Boundary and confirmation.** TX Benchmark remains conditional on pairable evidence and accurate reported power. Simultaneous designs retain transmitter-chain, frequency-response, isolation and coupling differences. Same-cycle one-sided evidence is also affected by the Target-Active Gate. Strengthen the result with broad receiver support, accurate power measurement, repeated runs and the method-specific controls below.
````

</details>

<details><summary>Source unit 49</summary>

````text
##### 2.4.1 Reference Setup/Station
````

</details>

<details><summary>Source unit 50</summary>

````text
Use two distinguishable complete transmitter chains at the same physical test QTH, with different valid exact callsigns, synchronized WSPR cycles, separated clear frequencies, established actual and reported power, and adequate RF isolation. Prefer ordinary callsigns that fit one Type 1 transmission and avoid compound callsigns unless they are necessary. If a compound callsign is unavoidable, keep both chains on the same Type 2/Type 3 message pattern and verify both exact archive identities and their truthful reported grid-4 values before the experiment. [Appendix B](#sec-simultaneous-tx-setup) gives the practical setup and preflight.
````

</details>

<details><summary>Source unit 51</summary>

````text
Same-receiver, same-cycle Delta SNR avoids a comparison across different cycles and is the strongest TX design when the two transmitter chains can be controlled. It still compares the complete documented transmit paths. Frequency-selective QRM, chain response, coupling and power error can remain. Swap the frequency positions and, where practical, cross the tested antennas or components between chains.
````

</details>

<details><summary>Source unit 52</summary>

````text
<blockquote class="evidence-conclusion"><p>Under the documented simultaneous controlled two-transmitter setup, same-receiver, same-cycle Delta SNR and Decode Outcomes described the observed difference between the Target and Reference transmit paths for the selected receivers and geographic scope.</p></blockquote>
````

</details>

<details><summary>Source unit 53</summary>

````text
Use a known, separately identifiable complete Reference transmitter whose QTH, callsign, actual and reported power, equipment and operating schedule are understood. TX pairs share the same remote receiver and cycle, but Target and Reference remain distinct complete transmitting stations with their own transmitters, antennas, feedlines and installed environments. WSPRadar resolves the reported Reference grid-4 from the selected archive window. It may equal Target grid-4; equal grid-4 does not prove physical co-location.
````

</details>

<details><summary>Source unit 54</summary>

````text
A controlled local setup and an independent station use the same Reference Setup/Station analysis. The physical arrangement, not whether two callsigns share a base, determines the interpretation. Both require two distinct valid exact reporting identities and same-cycle evidence; a single switched transmitter cannot supply this comparison.
````

</details>

<details><summary>Source unit 55</summary>

````text
Interpret the result as a benchmark of complete installed transmitting stations. Same-receiver pairing controls the receiving endpoint, not the two transmit sites or radio paths. Power-reporting accuracy is especially important. Repeat with the same well-understood Buddy and stable configurations rather than treating the Buddy as an absolute calibrated standard.
````

</details>

<details><summary>Source unit 56</summary>

````text
<blockquote class="evidence-conclusion"><p>For the shared receiving stations and cycles in this run, paired Delta SNR and Decode Outcomes described how the two complete transmitting stations compared under their respective operating environments.</p></blockquote>
````

</details>

<details><summary>Source unit 57</summary>

````text
##### 2.4.2 Reference Neighborhood
````

</details>

<details><summary>Source unit 58</summary>

````text
The contributing local transmitters are those reported by the same remote receiver during the same WSPR cycle. Paired Delta SNR additionally requires that receiver to report the Target in that cycle. The Reference therefore represents the qualifying local transmissions observed at that receiver, not every nearby transmitter or every attempted transmission.
````

</details>

<details><summary>Source unit 59</summary>

````text
Reported-power normalization removes the reported transmit-power difference from paired SNR values. It does not verify actual transmitter power, measure radiated power or correct unknown feedline losses. Sharing a remote receiver and cycle controls the receiving endpoint and timing, but nearby transmitters can still have different installations, terrain and propagation paths. A neighborhood containing only one contributing transmitter provides that transmitter’s value as its median.
````

</details>

<details><summary>Source unit 60</summary>

````text
<blockquote class="evidence-conclusion"><p>For the selected band, window, receiver paths and cycles, the Target’s complete transmitting station showed the reported power-normalized paired Delta SNR and the reported Decode Outcomes relative to the contributing local transmitter neighborhood. This does not establish that its antenna is the displayed number of decibels better.</p></blockquote>
````

</details>

<details><summary>Source unit 61</summary>

````text
**This is an optional expert diagnostic tool, not a routine step intended for every operator or every Benchmark analysis.** Use it when a controlled Benchmark has enough paired evidence around the period of interest and the question specifically concerns a temporary departure from one radio path's usual Target-versus-Reference behavior. Start with the ordinary Benchmark evidence path first; enable outlier reporting only when its additional event-level detail serves the investigation.
````

</details>

<details><summary>Source unit 62</summary>

````text
The detector does not search for the largest raw Delta SNR in the run. It asks whether one exact `callsign + locator` path temporarily moved above or below a stable local expected Delta SNR by enough to pass the configured departure, robust-score and baseline-stability requirements. The result is a set of intervals for expert review, not an automatic explanation of why the observations changed.
````

</details>

<details><summary>Source unit 63</summary>

````text
Use the detector only with Benchmark evidence. Its native evidence unit is a simultaneous **Joint Spot**. Only those units contain both Target and corrected Reference SNR and therefore a paired Delta SNR. Only Target and Only Reference outcomes remain useful diagnostic context but cannot themselves qualify an event.
````

</details>

<details><summary>Source unit 64</summary>

````text
The method is most useful when the selected path has repeated paired observations before, during and after a suspected change. It deliberately abstains when a reliable local baseline cannot be supported on both sides. No reported event can therefore mean either that the retained evidence did not pass the configured gates or that the local evidence was insufficient or unstable; it does not establish that the path was unchanged.
````

</details>

<details><summary>Source unit 65</summary>

````text
Enable **`Report ΔSNR outlier candidates`** and set the three expert controls described in [Section 4.6](#sec-5-6), then run the analysis manually. Changing the toggle or a threshold marks the analysis definition as changed but does not automatically start another run.
````

</details>

<details><summary>Source unit 66</summary>

````text
For each exact path, WSPRadar:
````

</details>

<details><summary>Source unit 67</summary>

````text
1. keeps the paired observations at their native WSPR-cycle times;
2. estimates the path's expected local Delta SNR from robust summaries before and after a possible departure, excluding the candidate itself;
3. requires those two baseline sides to have enough populated evidence and to agree within the configured maximum;
4. groups nearby, same-sign residuals using the path's observed evidence cadence;
5. tests the grouped event against the same absolute-departure, robust-score and sign-agreement rules regardless of its duration; and
6. trims weak leading and trailing evidence so that the reported interval begins and ends on observations that individually meet both user thresholds.
````

</details>

<details><summary>Source unit 68</summary>

````text
Weaker observations can remain inside an interval when they connect stronger observations, but they cannot extend its outer boundaries. A failed broad candidate can be split at a supported return to baseline so that a strong internal section is tested on its own without choosing a new, more favorable baseline.
````

</details>

<details><summary>Source unit 69</summary>

````text
Detection is completed before the Temporal Evidence display is aggregated. Changing a `1h`, `6h` or other display bin therefore cannot create, merge, split or remove an event. After path events qualify independently, contemporaneous same-sign events can be grouped for review: **path-specific** means one path, **directionally coherent** means several paths in adjacent compass sectors, **scope-wide** means several separated directions, and **multiple paths** means several paths with direction unavailable for at least one contributor. That context does not change whether an individual path qualified. The exact construction, support counts, timing rules and formulas are in [Section 7.11](#sec-7-11).
````

</details>

<details><summary>Source unit 70</summary>

````text
Read an event card from the interval down to its source evidence:
````

</details>

<details><summary>Source unit 71</summary>

````text
* **Spot impulse**, **Short burst** and **Sustained excursion** describe the retained temporal shape after boundary trimming. They do not use different qualification thresholds or express different certainty.
* Each path line identifies the exact `callsign + locator` and direction. **Expected local Delta SNR** is the candidate-excluded two-sided baseline; **Observed median Delta SNR** summarizes the retained units in the reported interval; **Largest single-cycle departure** is the most extreme retained residual from that baseline. That report/export metric is independent of the all-path temporal `*`, which selects the greatest-absolute-residual unit only among individually qualifying native units in each review event and never uses an unsupported or nonqualifying episode peak.
* For a multi-unit event, **Chronological WSPR-cycle evidence** lists the contributing UTC time, path, direction, local baseline, Delta SNR and residual. A one-unit Spot impulse needs no duplicate evidence table.
* The green **`↓ Show in Station Insights`** and **`↓ Show Drill-Down Details`** actions sit to the right of their exact path timeframe. The first selects that path, preloads Drill-Down and navigates to Station Insights for the wider run history; the second makes the same selection and preload but navigates directly to Drill-Down. Both open **`Outlier Focus`** over the complete supported pre-event baseline flank, guarded provisional episode and post-event baseline flank, clipped only to the completed analysis window; this detector-support interval may exceed 24 hours. The focused Delta SNR plot shows one actual retained Joint Spot at its native time instead of a bin median, IQR or density layer. Identical `*` markers identify every native unit in the current window that individually meets both configured departure and robust-z gates as part of a reported candidate, including all such units in a multi-unit burst or episode. A muted **Focused episode** band identifies the selected reported episode. It spans that episode's reported retained-evidence interval, padded by half one native evidence-unit width at each end and clipped to the focused window so a one-unit impulse remains visible; it is neither a confidence interval nor a measurement of physical-event duration. Overlays show the expected local Delta SNR, the pre/post flank baselines over their actual support intervals, symmetric robust-z guides at 1, 2 and 3 plus the configured qualifying threshold, and the configured absolute-departure boundary for the focused episode only. Other starred candidate units may have been evaluated against different local baselines and robust spreads. These are detector guides, not confidence intervals, and crossing any one guide cannot qualify a candidate by itself. Use the underlying Target and corrected Reference SNR values and nearby one-sided outcomes to check whether the Delta SNR movement came mainly from one side, whether either signal approached the decode edge, and whether pairability changed nearby.
````

</details>

<details><summary>Source unit 72</summary>

````text
The displayed first-to-last span is the interval between retained observations. It does not assert uninterrupted behavior between them. Compare the interval with contemporaneous paths, station logs, switching schedules, gain or power changes, interference observations and independent measurements before assigning a cause.
````

</details>

<details><summary>Source unit 73</summary>

````text
The three controls always retain their literal meaning:
````

</details>

<details><summary>Source unit 74</summary>

````text
* increasing **`Minimum absolute ΔSNR departure (dB)`** requires a larger departure;
* increasing **`Minimum robust z-score`** requires the departure to be larger relative to nearby robust variability; and
* decreasing **`Maximum pre/post baseline difference (dB)`** requires a more stable two-sided baseline.
````

</details>

<details><summary>Source unit 75</summary>

````text
The opposite changes make reporting more permissive. The same three values apply to Spot impulses, Short bursts and Sustained excursions; duration provides no hidden discount. For exploratory work, use candidates to identify intervals worth auditing and record any threshold changes. For confirmatory work, fix and preserve the thresholds, Benchmark design, correction, path population, band and UTC scope before inspecting the result, then test whether a comparable departure recurs in a separate suitably controlled run.
````

</details>

<details><summary>Source unit 76</summary>

````text
Report the observation as a **temporary local Delta SNR departure in the retained paired evidence**, together with its exact path, interval, sign, supporting units and detector settings. The detector is descriptive: it does not calculate a p-value, correct for the number of searched paths or events, or determine the physical cause.
````

</details>

<details><summary>Source unit 77</summary>

````text
When outlier reporting is enabled, preserve the active-scope findings with the analysis export. It adds a path-event summary and a chronological paired-evidence CSV linked by package-local Event and Path event IDs. The evidence table deliberately repeats the path, direction and path-event class so it remains readable on its own. [Section 8.4](#sec-8-4) defines the two files and their conditional inclusion.
````

</details>


### DE original passages

<details><summary>Source unit 1</summary>

````text
Verwende den Abschnitt, der zur gewählten Richtung und zum Ergebnistyp passt. Exakte Bedienelemente, Standardwerte und Wertebereiche stehen in [Kapitel 4](#sec-5); genaue Zulässigkeit, Zuordnung, Gewichtung und Aggregation in [Kapitel 7](#sec-7).
````

</details>

<details><summary>Source unit 2</summary>

````text
#### 2.1 RX Performance
````

</details>

<details><summary>Source unit 3</summary>

````text
**Beantwortete Frage.** Welche bestätigten Zyklen des Peer-TX decodierte der Target-RX; wie beständig gelang dies; welchen erfolgreichen SNR beobachtete er; und wo und wann trat dieses Verhalten auf?
````

</details>

<details><summary>Source unit 4</summary>

````text
**Minimal gültiger Aufbau.** Verwende das exakte Melderufzeichen und QTH des Targets, ein Band und ein Zeitfenster mit beobachtbarer Aktivität des Target-Empfängers. Halte die Empfangskette stabil. Performance führt keine Referenz ein und isoliert kein einzelnes Bauteil des Empfangssystems.
````

</details>

<details><summary>Source unit 5</summary>

````text
**Was WSPRadar auswertet.** Innerhalb des gewählten Bands, der exakten Peer-Identität und eines Target-aktiven Zyklus liegt eine bestätigte RX-Gelegenheit vor, wenn der Target-RX den Peer-TX decodiert oder ein anderer geeigneter RX denselben Peer-TX decodiert. `Vom Target gehört` ist ein Erfolg, unabhängig davon, ob ein anderer RX den Peer-TX ebenfalls meldet: Die Meldung des Target-RX bestätigt unmittelbar sowohl den sendenden Peer-TX als auch den empfangenden Target-RX. `Nur von anderen gehört` ist ein Miss, wenn ein anderer geeigneter RX die Aussendung des Peer-TX bestätigt, der aktive Target-RX sie aber nicht decodiert. Ein Target-only-Erfolg bleibt als Herkunftsangabe innerhalb der Erfolge und Gelegenheiten erhalten und wird niemals ein zweites Mal addiert. Fehlt ein Aktivitätsnachweis für den Target-RX, belegt die Meldung eines anderen Empfängers nicht, dass der Target-RX zugehört hat. Die genaue Klassifikation steht in [Abschnitt 7.4](#sec-7-4).
````

</details>

<details><summary>Source unit 6</summary>

````text
**Dem Evidenzpfad folgen.** Auf der **Karte** zeigt die Sektorfarbe die stationsgleichgewichtete Dekodierrate der qualifizierenden entfernten Sender in jedem Entfernungs- und Richtungssegment. Stationsmarker und Kartenfuß unterscheiden Funkwege, die das Target mindestens einmal hörte, von Funkwegen, die nur andernorts gehört wurden. Nutze dies zunächst, um den groben RX-Empfangsbereich und Richtungsstrukturen zu lokalisieren – nicht, um allein aus der Farbe auf Empfängerempfindlichkeit zu schließen.
````

</details>

<details><summary>Source unit 7</summary>

````text
Vergleiche im **Segment-Inspektor** zunächst die Breite der Stationsbasis mit der Tiefe bestätigter Gelegenheiten. Viele Gelegenheiten von nur wenigen Sendern sind tiefe, aber schmale Evidenz; Übereinstimmung über viele Sender ist breiter abgestützt. Lies anschließend die drei Performance-Ansichten gemeinsam:
````

</details>

<details><summary>Source unit 8</summary>

````text
* **Mindestens-einmal-Reichweite** fragt, welche qualifizierenden Sender während des Zeitfensters mindestens einmal gehört wurden. Sie misst Breite und nimmt bei längeren Läufen normalerweise zu.
* **Dekodierrate** fragt, wie beständig das Target bestätigte Gelegenheiten decodierte. Die stationsgleichgewichtete Rate gibt jedem Sender eine Stimme; die Rate auf Gelegenheitsebene gibt jedem bestätigten Zyklus eine Stimme. Ein Unterschied zwischen beiden zeigt, dass Sender mit hohem Evidenzvolumen anders abschneiden als die breitere Stationspopulation.
* **Erfolgreiches Target-SNR** beschreibt nur erfolgreiche Decodes. Es hilft zu erkennen, ob sich die erfolgreich empfangenen Signalpegel mit der Entfernung verändern. Verpasste Gelegenheiten besitzen jedoch kein Target-SNR und können dort nicht erscheinen.
````

</details>

<details><summary>Source unit 9</summary>

````text
In der **Zeitlichen Evidenz** vergleicht die Abweichung des erfolgreichen SNR jeden Senderpfad mit seinem eigenen typischen erfolgreichen Pegel während des Laufs. Werte über `0 dB` bedeuten, dass erfolgreiche Decodes auf dem jeweiligen Pfad stärker als üblich waren; Werte unter `0 dB` bedeuten schwächere erfolgreiche Decodes. Die zugehörige Stations- und Gelegenheits-Evidenz zeigt, ob sich gleichzeitig die Dekodierrate änderte und wie breit das Muster gestützt ist. Die chronologische Ansicht erkennt Veränderungen im Lauf; die gefaltete UTC-Stunden-Ansicht wiederkehrendes Tagesverhalten.
````

</details>

<details><summary>Source unit 10</summary>

````text
Lies in **Station Insights** die Dekodierrate jedes Senders zusammen mit den Anzahlen `Vom Target gehört` und `Nur von anderen gehört`. Wähle einen typischen Funkweg, einen Ausreißer und jeden Pfad mit ungewöhnlich viel Evidenz. Die **Evidenz der ausgewählten Station** zeigt anschließend das tatsächliche erfolgreiche SNR und die Gelegenheitshistorie eines einzelnen Senderpfads statt der stationsbezogenen Zusammenfassung des Segments. **Drill-Down** prüft die beitragenden Zyklen und unterscheidet extern gestützte Erfolge von der Target-only-Herkunftsteilmenge, die bereits in Erfolgen und Gelegenheiten enthalten ist.
````

</details>

<details><summary>Source unit 11</summary>

````text
**Typische Interpretationsmuster.** Breite Reichweite bei hoher Dekodierrate bedeutet, dass viele Funkwege offen waren und beständig decodiert wurden. Breite Reichweite bei niedrigerer Dekodierrate bedeutet, dass viele Wege mindestens einmal offen, aber wechselhaft waren. Begrenzte Reichweite bei hoher Dekodierrate bedeutet, dass weniger qualifizierende Wege offen waren, diese jedoch vergleichsweise zuverlässig funktionierten. Bleibt das erfolgreiche SNR stabil oder steigt, während die Dekodierrate fällt, können schwächere Signale unter die Decode-Schwelle gefallen sein, sodass nur stärkere erfolgreiche Decodes übrig bleiben. Ein Muster, das auf einen Azimut, Entfernungsbereich oder UTC-Zeitraum begrenzt ist, kann betrieblich nützlich sein, beschreibt aber den installierten Empfänger unter diesen Funkwegen und Bedingungen und keine kontextfreie Empfindlichkeitskennzahl.
````

</details>

<details><summary>Source unit 12</summary>

````text
**Grenze und Bestätigung.** RX Performance umfasst Antenne, Speiseleitung, Empfänger, Verstärkung, Filterung, Decoder, lokalen Stör- und Rauschpegel sowie Ausbreitung. Sie misst weder Empfängerempfindlichkeit, Antennengewinn, absoluten Rauschpegel noch Ausbreitungsart direkt. Wiederhole ein vermutetes Muster in einem weiteren geeigneten Zeitfenster. Soll gezielt eine Hardwareänderung beurteilt werden, verwende einen kontrollierten RX Benchmark oder einen Kreuztausch statt nur zeitlich getrennter Vorher-Nachher-Performance-Läufe.
````

</details>

<details><summary>Source unit 13</summary>

````text
#### 2.2 TX Performance
````

</details>

<details><summary>Source unit 14</summary>

````text
**Beantwortete Frage.** Welche nachweislich aktiven Peer-RX decodierten den Target-TX; wie beständig taten sie dies; welchen erfolgreichen SNR meldeten sie; und wo und wann trat dieses Verhalten auf?
````

</details>

<details><summary>Source unit 15</summary>

````text
**Minimal gültiger Aufbau.** Verwende das exakte Target-Rufzeichen und QTH, ein Band und ein Zeitfenster, in dem der Target-Sender in Betrieb war. Halte HF-Pfad, Zeitplan und tatsächliche Leistung stabil und melde die Leistung korrekt. Performance wertet die vollständige Sendestation aus und nicht ein isoliertes Bauteil.
````

</details>

<details><summary>Source unit 16</summary>

````text
**Was WSPRadar auswertet.** Innerhalb des gewählten Bands, der exakten Peer-Identität und eines Target-aktiven Zyklus liegt eine bestätigte TX-Gelegenheit vor, wenn der Peer-RX den Target-TX decodiert oder derselbe Peer-RX einen anderen qualifizierenden Sender auf demselben Band decodiert. `Target gehört` ist ein Erfolg, unabhängig davon, ob der Peer-RX einen weiteren Sender meldet: Seine Target-TX-Meldung bestätigt unmittelbar beide Endpunkte. `Nur andere Signale gehört` ist ein Miss, wenn dieser Peer-RX einen anderen qualifizierenden Sender meldet, den aktiven Target-TX aber nicht. Ein Target-only-Erfolg bleibt als Herkunftsangabe innerhalb der Erfolge und Gelegenheiten erhalten und wird niemals ein zweites Mal addiert. Eine Target-TX-Meldung an einem anderen Empfänger belegt die Aktivität des Target-TX, aber nicht, dass dieser bestimmte stille Peer-RX zugehört hat. Der genaue Nenner steht in [Abschnitt 7.4](#sec-7-4).
````

</details>

<details><summary>Source unit 17</summary>

````text
**Dem Evidenzpfad folgen.** Auf der **Karte** zeigt die Sektorfarbe die stationsgleichgewichtete Dekodierrate qualifizierender aktiver Empfänger in jedem Entfernungs- und Richtungssegment. Marker und Anzahlen am Kartenfuß unterscheiden Empfänger, die das Target mindestens einmal hörten, von Empfängern, die nur andere qualifizierende Signale hörten. Nutze die Karte, um den praktischen Sendefußabdruck und Richtungsstrukturen zu lokalisieren.
````

</details>

<details><summary>Source unit 18</summary>

````text
Vergleiche im **Segment-Inspektor** die Breite der Empfängerbasis mit der Tiefe bestätigter Gelegenheiten und lies anschließend die drei Performance-Ansichten gemeinsam:
````

</details>

<details><summary>Source unit 19</summary>

````text
* **Mindestens-einmal-Reichweite** fragt, welche qualifizierenden aktiven Empfänger das Target während des Zeitfensters mindestens einmal hörten.
* **Dekodierrate** fragt, wie beständig das Target innerhalb bestätigter Empfängergelegenheiten gemeldet wurde. Die stationsgleichgewichtete und die gelegenheitsbezogene Rate zeigen, ob häufig meldende Empfänger anders abschneiden als die breitere Empfängerpopulation.
* **Erfolgreiches Target-SNR** zeigt das auf die gemeldete Leistung normierte SNR erfolgreicher Target-Meldungen. Es ist an einen erfolgreichen Decode gebunden und hängt von der Richtigkeit der gemeldeten Sendeleistung ab.
````

</details>

<details><summary>Source unit 20</summary>

````text
In der **Zeitlichen Evidenz** zeigt die Abweichung des erfolgreichen SNR, wann erfolgreiche Meldungen stärker oder schwächer waren als der jeweils typische erfolgreiche Pegel des Empfängerpfads. Die zugehörigen Stations- und Gelegenheitsstapel zeigen, ob eine Veränderung des erfolgreichen SNR mit einer Veränderung der praktischen Decodierbarkeit einherging und wie viel Evidenz jedes Zeit-Bin stützt. Unterscheide Veränderungen im chronologischen Verlauf von wiederkehrendem Verhalten nach UTC-Stunde.
````

</details>

<details><summary>Source unit 21</summary>

````text
Lies in **Station Insights** die Rate jedes Empfängers zusammen mit seinen Anzahlen `Target gehört` und `Nur andere Signale gehört`. Die **Evidenz der ausgewählten Station** legt für einen Empfängerpfad das tatsächliche erfolgreiche SNR und die Gelegenheitshistorie offen. So wird sichtbar, ob die Segmentzusammenfassung viele Empfänger beschreibt oder einen funkwegspezifischen Effekt verdeckt. **Drill-Down** prüft Target-TX-Meldungen, extern bestätigte Peer-RX-Aktivität und die bereits in Erfolgen und Gelegenheiten enthaltene Target-only-Herkunftsteilmenge.
````

</details>

<details><summary>Source unit 22</summary>

````text
**Typische Interpretationsmuster.** Breite Reichweite und hohe Dekodierrate bedeuten, dass viele qualifizierende aktive Empfänger das Target beständig hörten. Breite Reichweite bei niedrigerer Dekodierrate beschreibt einen großen, aber wechselhaften Fußabdruck. Ein anhaltender Vorteil in einem Azimut oder Entfernungsbereich kann mit dem installierten Antennensystem und Gelände vereinbar sein; eine kurze isolierte Verbesserung kann dagegen durch Ausbreitung oder Empfängerverfügbarkeit verursacht sein. Ein stabiles erfolgreiches SNR bei fallender Dekodierrate kann bedeuten, dass nur stärkere überlebende Meldungen verbleiben. Unterschiede zwischen stationsgleichgewichteter und gelegenheitsbezogener Rate zeigen, ob wenige Empfänger mit hohem Evidenzvolumen die gepoolte Sicht prägen.
````

</details>

<details><summary>Source unit 23</summary>

````text
**Grenze und Bestätigung.** TX Performance umfasst Sender, tatsächliche Leistung, Speiseleitung, Anpassung, Antenne, Gelände, entfernte Empfangssysteme, lokalen Störpegel und Ausbreitung. Eine Normierung anhand der gemeldeten Leistung kann weder eine falsche Leistungsangabe noch einen ungemessenen Speiseleitungsverlust korrigieren. Das Ergebnis misst EIRP, Wirkungsgrad, Antennengewinn oder Abstrahlwinkel nicht direkt. Wiederhole das Muster in einem weiteren geeigneten Zeitfenster; verwende TX Benchmark, wenn die konkrete Frage lautet, ob sich ein Sendepfad von einem anderen unterscheidet.
````

</details>

<details><summary>Source unit 24</summary>

````text
#### 2.3 RX Benchmark
````

</details>

<details><summary>Source unit 25</summary>

````text
**Beantwortete Frage.** Wie unterschied sich der Empfang des Targets von der gewählten Referenz für dieselben entfernten Senderidentitäten und WSPR-Zyklen?
````

</details>

<details><summary>Source unit 26</summary>

````text
**Gemeinsame RX-Benchmark-Evidenz.** Gepaarte Delta-SNR-Werte erfordern vergleichbare Evidenz von Target und Referenz für denselben Sender im selben Zyklus. Positive Werte sprechen für das Target, negative für die Referenz. Decode Outcomes erhalten Joint, Only Target, Only Reference und asynchrone Evidenz um diese gepaarte Teilmenge. Der Joint-Evidenzanteil zeigt, wie viel der beibehaltenen Evidenz paarbar ist; er ist keine Gewinnquote des Targets. Die Betriebsbereitschaft der Referenz muss unabhängig geprüft werden; das Target-Active Gate macht die einseitigen Kategorien asymmetrisch.
````

</details>

<details><summary>Source unit 27</summary>

````text
**Dem Evidenzpfad folgen.** Auf der **Karte** zeigt die Sektorfarbe den stationsgleichgewichteten Median des Delta SNR je Entfernungs- und Richtungssegment. Marker unterscheiden Senderidentitäten mit Joint- und einseitiger Evidenz. Lies Farbe, Stations- und Spotanzahlen zusammen: Ein auffälliger Sektor mit wenigen Sendern liefert schmalere Evidenz als ein ähnliches Ergebnis über viele Funkwege.
````

</details>

<details><summary>Source unit 28</summary>

````text
Im **Segment-Inspektor** zeigen Decode Outcomes zwei ergänzende Zusammensetzungen: die Breite über Stationen und das Beobachtungsvolumen. Stationsmediane geben jedem entfernten Sender genau einen Delta-SNR-Wert und gleiches Gewicht; die Verteilung der Joint Spots zeigt jede gepaarte Beobachtung und gewichtet damit Sender mit vielen Meldungen stärker. Übereinstimmung stützt eine breite Verschiebung; Abweichungen zeigen unterschiedliche Muster über Stationen und Beobachtungen. [Abschnitt 7.7](#sec-7-7) veranschaulicht diesen Gewichtungsunterschied.
````

</details>

<details><summary>Source unit 29</summary>

````text
Die **Zeitliche Evidenz** zeigt Veränderungen während des Laufs und mögliche Muster nach UTC-Stunde. Prüfe die chronologische Evidenz über einzelne Tage, bevor du ein gefaltetes Muster als wiederkehrend bezeichnest. Lies sie zusammen mit der Abdeckung der Benchmark-Evidenz: Unterscheide breite Joint-Unterstützung von einem Muster, das auf eine kleine gepaarte Teilmenge begrenzt ist. Einseitige Evidenz kann praktische Unterschiede nahe der Decode-Schwelle zeigen, liefert aber kein SNR der fehlenden Seite.
````

</details>

<details><summary>Source unit 30</summary>

````text
Lies in **Station Insights** den medianen Delta-SNR-Wert jedes Senders zusammen mit seinen Joint- und einseitigen Anzahlen. Die **Evidenz der ausgewählten Station** zeigt gepaarte Werte und Abdeckung eines Funkwegs über die Zeit: Ist er repräsentativ, außergewöhnlich oder intermittierend? **Drill-Down** prüft Sender, Zyklus, exakte Rufzeichen- und Locatoridentitäten sowie das Vorzeichen der Korrektur.
````

</details>

<details><summary>Source unit 31</summary>

````text
**Interpretieren und weiterprüfen.** Stationsmediane überwiegend auf derselben Seite von 0 dB, breite Joint-Abdeckung und Wiederkehr über Zeit oder benachbarte Segmente stützen einen beständigen Unterschied vollständiger Empfangspfade; prüfe ihn in einem neuen Lauf. Eine gepoolte Verschiebung ohne entsprechende Verschiebung der Stationsmediane kann von wenigen Sendern mit vielen Meldungen ausgehen: Prüfe deren Anzahlen und Funkwege. Ein klarer gepaarter Median mit vielen Only-Target- oder Only-Reference-Outcomes beschreibt nur einen Teil der Decode-Evidenz: Prüfe Referenzverfügbarkeit und einseitige Abdeckung, bevor du verallgemeinerst. Ein richtungs- oder UTC-spezifischer Unterschied kann dennoch nützlich sein; begrenze die Aussage auf diese Bedingungen und wiederhole den Vergleich.
````

</details>

<details><summary>Source unit 32</summary>

````text
**Grenze und Bestätigung.** Delta SNR aus Joint-Evidenz beschreibt keine verpassten Signale. Die Zuordnung im selben Zyklus kontrolliert Sender und Zeit, aber keine Unterschiede von Empfängerkette, Antenne, Störumgebung oder QTH. Stärke das Ergebnis durch ausreichend viele Stationen mit Joint-Evidenz, unabhängig bekannte Referenzbetriebszeiten, Wiederholung und die nachfolgenden designspezifischen Prüfungen.
````

</details>

<details><summary>Source unit 33</summary>

````text
##### 2.3.1 Referenzaufbau/-station
````

</details>

<details><summary>Source unit 34</summary>

````text
Dies ist das stärkste RX-Design für die Zuordnung zu einem lokalen Pfad. Es vergleicht weiterhin vollständige dokumentierte Empfangspfade, solange Unterschiede bei Empfänger, Audio, Verstärkung, Decoder und Signalführung nicht charakterisiert sind. Eine breite, wiederkehrende Delta-SNR-Verschiebung mit passender einseitiger Evidenz stützt ein besseres Abschneiden eines Pfads unter den geprüften Bedingungen. Nutze zur Bestätigung eine Kalibrierung mit gemeinsamem Eingang, einen Tausch der Verteilerausgänge oder einen Hardware-Kreuztausch; damit lassen sich Prüfobjekt und dauerhafter Kettenoffset möglicherweise unterscheiden. [Anhang C](#sec-reference-snr-calibration) erklärt die Referenz-SNR-Kalibrierung; [Anhang A](#sec-a) beschreibt getrennte WSJT-X-Instanzen.
````

</details>

<details><summary>Source unit 35</summary>

````text
<blockquote class="evidence-conclusion"><p>Unter dem dokumentierten simultanen RX-kontrollierten Aufbau beschrieben gepaartes Delta SNR und Decode Outcomes den beobachteten Unterschied zwischen Target- und Referenzempfangspfad für die gemeinsamen Sender, Zyklen und den ausgewählten geografischen Bereich.</p></blockquote>
````

</details>

<details><summary>Source unit 36</summary>

````text
Wähle eine identifizierbare vollständige Referenz-Empfangsstation mit bekanntem QTH, Rufzeichen, Geräten, Betriebsplan und lokaler Umgebung. RX-Paare teilen Sender und Zyklus; Target und Referenz bleiben eigenständige vollständige Empfangsstationen mit ihren eigenen Antennen, Geräten, Signalwegen und lokalen Störumgebungen. WSPRadar ermittelt das gemeldete Referenz-Grid-4 aus Datenbankmeldungen im ausgewählten Zeitfenster. Es darf dem Target-Grid-4 entsprechen, beweist aber keine Ko-Lokation.
````

</details>

<details><summary>Source unit 37</summary>

````text
<blockquote class="evidence-conclusion"><p>Für die gemeinsamen Senderpfade und Zyklen dieses Laufs beschrieben gepaartes Delta SNR und Decode Outcomes, wie sich die beiden vollständigen Empfangsstationen unter ihren jeweiligen Umgebungsbedingungen verglichen.</p></blockquote>
````

</details>

<details><summary>Source unit 38</summary>

````text
##### 2.3.2 Referenznachbarschaft
````

</details>

<details><summary>Source unit 39</summary>

````text
Beitragende lokale Empfänger sind hier diejenigen mit qualifizierenden Meldungen desselben entfernten Senders im selben WSPR-Zyklus. Die Referenz repräsentiert daher die auf diesem Senderpfad und in diesem Zyklus beobachteten Empfänger und nicht jeden Empfänger innerhalb des Radius. Gepaartes Delta SNR erfordert zusätzlich eine qualifizierende Target-Meldung für denselben Sender und Zyklus.
````

</details>

<details><summary>Source unit 40</summary>

````text
<blockquote class="evidence-conclusion"><p>Für das ausgewählte Band und Zeitfenster sowie die ausgewählten Senderpfade und Zyklen zeigte die vollständige Empfangsstation des Targets das berichtete gepaarte Delta SNR und die berichteten Decode Outcomes relativ zur beitragenden lokalen Empfängernachbarschaft. Dies belegt keinen entsprechenden Gewinnvorteil ihrer Antenne.</p></blockquote>
````

</details>

<details><summary>Source unit 41</summary>

````text
#### 2.4 TX Benchmark
````

</details>

<details><summary>Source unit 42</summary>

````text
**Beantwortete Frage.** Wie unterschied sich der Target-Sender von der ausgewählten Referenz an gemeinsamen entfernten Empfängern?
````

</details>

<details><summary>Source unit 43</summary>

````text
**Gemeinsame TX-Benchmark-Evidenz.** Ein TX-Benchmark im selben Zyklus vergleicht Target und Referenz am selben entfernten Empfänger im selben WSPR-Zyklus. Erfolgreiches TX-SNR wird vor der Bildung des Delta SNR auf die gemeldete Leistung normiert; das Ergebnis hängt daher unmittelbar von korrekten Leistungsangaben ab. Decode Outcomes bewahren Joint- und einseitige Evidenz. Eine exklusive Beobachtung besitzt jedoch kein SNR der fehlenden Seite und wird nicht als Paar leistungsnormiert.
````

</details>

<details><summary>Source unit 44</summary>

````text
**Dem Evidenzpfad folgen.** Auf der **Karte** fasst die Sektorfarbe das stationsgleichgewichtete mediane Delta SNR über entfernte Empfänger zusammen. Marker- und Kartenfußkategorien zeigen Joint- und einseitige Empfängerevidenz. Lies jeden Sektor zusammen mit der Breite über Empfänger sowie der Tiefe durch Spots.
````

</details>

<details><summary>Source unit 45</summary>

````text
Vergleiche im **Segment-Inspektor** die stationsbezogenen Decode Outcomes mit der Zusammensetzung auf Beobachtungsebene. Stationsmediane geben jedem entfernten Empfänger eine gleich große Stimme; die Delta-SNR-Verteilung der Joint Spots zeigt die vollständige gepaarte Beobachtungspopulation. Eine Verschiebung über viele Empfänger ist andere Evidenz als ein Ergebnis, das von wenigen Empfängern mit hohem Datenvolumen dominiert wird.
````

</details>

<details><summary>Source unit 46</summary>

````text
Die **Zeitliche Evidenz** zeigt, ob sich Delta SNR im Verlauf des Laufs veränderte oder nach UTC-Stunde wiederkehrte. Die Abdeckung der Benchmark-Evidenz zeigt, ob die gepaarte Evidenz während dieser Zeiten breit blieb. Prüfe, ob es vor allem an einem Empfänger, einer Audiofrequenzzuordnung oder einem kurzen Zeitraum auftritt.
````

</details>

<details><summary>Source unit 47</summary>

````text
Lies in **Station Insights** das mediane Delta SNR jedes Empfängers zusammen mit seinen Joint- und einseitigen Anzahlen. Die **Evidenz der ausgewählten Station** legt das gepaarte Ergebnis und die Evidenzabdeckung an einem Empfängerpfad offen. **Drill-Down** prüft Empfängeridentität, gemeldete Leistungen, Paarbildung im selben Zyklus sowie das Vorzeichen der Korrektur.
````

</details>

<details><summary>Source unit 48</summary>

````text
**Typische Interpretationsmuster.** Eine beständige Verschiebung der Stationsmediane über viele Empfänger, Richtungen und Zeiten stützt einen breiten Unterschied der vollständigen Sendepfade. Eine auf einen Azimut oder Entfernungsbereich begrenzte Verschiebung kann nützliches installiertes Richtverhalten anzeigen, ohne zu einem kontextfreien Gewinnwert zu werden. Starkes gepaartes Delta SNR bei umfangreicher einseitiger Evidenz bedeutet, dass sowohl der Signalstärkeunterschied als auch die praktische Reichweite nahe der Schwelle berichtet werden müssen. Weicht der Median der Rohpaare von der Stationsmedian-Ansicht ab, gewichten Empfänger mit hohem Datenvolumen die Beobachtungsevidenz anders.
````

</details>

<details><summary>Source unit 49</summary>

````text
**Grenze und Bestätigung.** TX Benchmark bleibt auf paarbare Evidenz und korrekte Leistungsangaben konditioniert. Simultane Designs behalten Unterschiede der Sendeketten bei Leistung, Frequenzgang, Entkopplung und Kopplung bei. Einseitige Evidenz im selben Zyklus wird außerdem vom Target-Active Gate beeinflusst. Stärke das Ergebnis durch breite Empfängerunterstützung, genaue Leistungsmessung, Wiederholung und die nachfolgend beschriebenen methodenspezifischen Kontrollen.
````

</details>

<details><summary>Source unit 50</summary>

````text
##### 2.4.1 Referenzaufbau/-station
````

</details>

<details><summary>Source unit 51</summary>

````text
Verwende am selben physischen Test-QTH zwei unterscheidbare vollständige Sendeketten mit verschiedenen zulässigen exakten Rufzeichen, synchronisierten WSPR-Zyklen, freien getrennten Frequenzen, bestimmter tatsächlicher und gemeldeter Leistung sowie ausreichender HF-Entkopplung. Bevorzuge reguläre Rufzeichen, die jeweils in eine Typ-1-Aussendung passen, und vermeide zusammengesetzte Rufzeichen, sofern sie nicht erforderlich sind. Ist ein zusammengesetztes Rufzeichen unvermeidbar, verwende für beide Ketten dasselbe Typ-2-/Typ-3-Nachrichtenmuster und prüfe vor dem Versuch beide exakten Archividentitäten mit ihrem gemeinsamen wahrheitsgemäßen Grid-4. [Anhang B](#sec-simultaneous-tx-setup) beschreibt die praktische Einrichtung und Vorabprüfung.
````

</details>

<details><summary>Source unit 52</summary>

````text
Delta SNR am selben Empfänger und im selben Zyklus vermeidet einen Vergleich zwischen verschiedenen Zyklen und ist das stärkste TX-Design, wenn beide Sendeketten kontrolliert werden können. Verglichen werden dennoch die vollständigen dokumentierten Sendepfade. Frequenzselektives QRM, Kettenfrequenzgang, Kopplung und Leistungsfehler können bestehen bleiben. Tausche die Frequenzpositionen und führe nach Möglichkeit einen Kreuztausch der geprüften Antennen oder Bauteile zwischen den Ketten durch.
````

</details>

<details><summary>Source unit 53</summary>

````text
<blockquote class="evidence-conclusion"><p>Unter dem dokumentierten simultanen kontrollierten Aufbau mit zwei Sendern beschrieben Delta SNR am selben Empfänger und im selben Zyklus sowie Decode Outcomes den beobachteten Unterschied zwischen Target- und Referenzsendepfad für die ausgewählten Empfänger und den geografischen Bereich.</p></blockquote>
````

</details>

<details><summary>Source unit 54</summary>

````text
Verwende eine bekannte, separat identifizierbare vollständige Referenz-Sendestation, deren QTH, Rufzeichen, tatsächliche und gemeldete Leistung, Ausrüstung und Betriebsplan bekannt und nachvollziehbar sind. TX-Paare teilen denselben entfernten Empfänger und denselben Zyklus; Target und Referenz bleiben jedoch eigenständige vollständige Sendestationen mit jeweils eigenen Sendern, Antennen, Speiseleitungen und Stationsumgebungen. WSPRadar ermittelt das gemeldete Referenz-Grid-4 aus dem ausgewählten Archivzeitfenster. Es darf dem Target-Grid-4 entsprechen; gleiches Grid-4 beweist keine physische Ko-Lokation.
````

</details>

<details><summary>Source unit 55</summary>

````text
Ein kontrollierter lokaler Aufbau und eine unabhängige Station verwenden dieselbe Analyse Referenzaufbau/-station. Die physische Anordnung bestimmt die Interpretation, nicht die Verwandtschaft der Rufzeichen. Beide benötigen zwei verschiedene gültige exakte Meldeidentitäten und Evidenz desselben Zyklus; ein einzelner umgeschalteter Sender kann diesen Vergleich nicht liefern.
````

</details>

<details><summary>Source unit 56</summary>

````text
Interpretiere das Ergebnis als Benchmark vollständiger installierter Sendestationen. Die Paarbildung am selben Empfänger kontrolliert den Empfangsendpunkt, nicht die beiden Sendestandorte oder Funkwege. Die Genauigkeit der Leistungsangaben ist besonders wichtig. Wiederhole den Lauf mit demselben gut verstandenen Buddy und stabilen Konfigurationen, statt die Buddy-Station als absolut kalibrierten Standard zu behandeln.
````

</details>

<details><summary>Source unit 57</summary>

````text
<blockquote class="evidence-conclusion"><p>Für die gemeinsamen Empfangsstationen und Zyklen dieses Laufs beschrieben gepaartes Delta SNR und Decode Outcomes, wie sich die beiden vollständigen Sendestationen unter ihren jeweiligen Betriebsumgebungen verglichen.</p></blockquote>
````

</details>

<details><summary>Source unit 58</summary>

````text
##### 2.4.2 Referenznachbarschaft
````

</details>

<details><summary>Source unit 59</summary>

````text
Beitragende lokale Sender sind diejenigen, die derselbe entfernte Empfänger während desselben WSPR-Zyklus meldet. Gepaartes Delta SNR erfordert zusätzlich, dass dieser Empfänger in diesem Zyklus das Target meldet. Die Referenz repräsentiert daher die qualifizierenden lokalen Aussendungen, die an diesem Empfänger beobachtet wurden, und nicht jeden Sender in der Umgebung oder jeden Sendeversuch.
````

</details>

<details><summary>Source unit 60</summary>

````text
Die Normierung auf Basis der gemeldeten Leistung entfernt den gemeldeten Sendeleistungsunterschied aus den gepaarten SNR-Werten. Sie überprüft weder die tatsächliche Senderleistung noch misst sie die abgestrahlte Leistung oder korrigiert unbekannte Speiseleitungsverluste. Derselbe entfernte Empfänger und Zyklus kontrollieren Empfangsendpunkt und Zeitpunkt; Sender in der Umgebung können dennoch unterschiedliche Installationen, Gelände- und Ausbreitungsbedingungen haben. Besteht die Nachbarschaft aus nur einem beitragenden Sender, ist dessen Wert ihr Median.
````

</details>

<details><summary>Source unit 61</summary>

````text
<blockquote class="evidence-conclusion"><p>Für das ausgewählte Band und Zeitfenster sowie die ausgewählten Empfängerpfade und Zyklen zeigte die vollständige Sendestation des Targets das berichtete leistungsnormierte gepaarte Delta SNR und die berichteten Decode Outcomes relativ zur beitragenden lokalen Sendernachbarschaft. Dies belegt nicht, dass ihre Antenne um die angezeigte Zahl von Dezibel besser ist.</p></blockquote>
````

</details>

<details><summary>Source unit 62</summary>

````text
**Dies ist ein optionales Diagnosewerkzeug für erfahrene Anwender und nicht für den routinemäßigen Einsatz in jeder Benchmark-Analyse gedacht.** Nutze es, wenn ein kontrollierter Benchmark um den interessierenden Zeitraum herum genügend gepaarte Evidenz besitzt und die Fragestellung ausdrücklich eine vorübergehende Abweichung vom üblichen Target-Referenz-Verhalten eines Funkwegs betrifft. Beginne stets mit dem gewöhnlichen Evidenzpfad des Benchmarks; aktiviere den Ausreißerbericht nur, wenn die zusätzlichen Ereignisdetails der Untersuchung dienen.
````

</details>

<details><summary>Source unit 63</summary>

````text
Der Detektor sucht nicht nach dem größten rohen Delta SNR des Laufs. Er prüft, ob sich ein exakter Funkweg `Rufzeichen + Locator` vorübergehend so weit über oder unter sein stabiles erwartetes lokales Delta SNR verschoben hat, dass die konfigurierten Anforderungen an Abweichung, robusten z-Wert und Baseline-Stabilität erfüllt sind. Das Ergebnis sind Zeitintervalle zur fachkundigen Prüfung und keine automatische Erklärung dafür, warum sich die Beobachtungen verändert haben.
````

</details>

<details><summary>Source unit 64</summary>

````text
Nutze den Detektor ausschließlich mit Benchmark-Evidenz. Seine native Evidenzeinheit ist ein simultaner **Joint Spot**. Nur diese Einheiten enthalten sowohl Target-SNR als auch korrigiertes Referenz-SNR und damit ein gepaartes Delta SNR. Outcomes `Only Target` und `Only Reference` bleiben nützlicher Diagnosekontext, können ein Ereignis aber nicht selbst qualifizieren.
````

</details>

<details><summary>Source unit 65</summary>

````text
Die Methode ist besonders nützlich, wenn der ausgewählte Funkweg vor, während und nach einer vermuteten Änderung wiederholte gepaarte Beobachtungen aufweist. Sie enthält sich bewusst, wenn auf beiden Seiten keine belastbare lokale Baseline gestützt werden kann. Kein berichtetes Ereignis kann daher bedeuten, dass die beibehaltene Evidenz entweder die konfigurierten Bedingungen nicht erfüllte oder lokal nicht ausreichte beziehungsweise instabil war; es belegt nicht, dass der Funkweg unverändert blieb.
````

</details>

<details><summary>Source unit 66</summary>

````text
Aktiviere **`ΔSNR-Ausreißerkandidaten melden`**, lege die drei in [Abschnitt 4.6](#sec-5-6) beschriebenen fachkundigen Einstellungen fest und starte die Analyse anschließend manuell. Eine Änderung des Schalters oder einer Schwelle kennzeichnet die Analysedefinition als geändert, startet aber nicht automatisch einen neuen Lauf.
````

</details>

<details><summary>Source unit 67</summary>

````text
Für jeden exakten Funkweg führt WSPRadar folgende Schritte aus:
````

</details>

<details><summary>Source unit 68</summary>

````text
1. Die gepaarten Beobachtungen bleiben an ihren nativen WSPR-Zykluszeiten erhalten.
2. Das erwartete lokale Delta SNR des Funkwegs wird aus robusten Zusammenfassungen vor und nach einer möglichen Abweichung geschätzt; der Kandidat selbst bleibt dabei ausgeschlossen.
3. Beide Seiten der Baseline müssen genügend belegte Evidenz besitzen und innerhalb des konfigurierten Höchstunterschieds übereinstimmen.
4. Zeitlich nahe Residuen gleichen Vorzeichens werden anhand der beobachteten Evidenzkadenz des Funkwegs gruppiert.
5. Das gruppierte Ereignis wird unabhängig von seiner Dauer gegen dieselben Regeln für absolute Abweichung, robusten z-Wert und Vorzeichenübereinstimmung geprüft.
6. Schwache führende und nachlaufende Evidenz wird abgeschnitten, sodass das berichtete Intervall an Beobachtungen beginnt und endet, die beide Benutzerschwellen jeweils einzeln erfüllen.
````

</details>

<details><summary>Source unit 69</summary>

````text
Schwächere Beobachtungen dürfen innerhalb eines Intervalls erhalten bleiben, wenn sie stärkere Beobachtungen verbinden; seine äußeren Grenzen dürfen sie nicht verlängern. Ein gescheiterter breiter Kandidat kann an einer gestützten Rückkehr zur Baseline geteilt werden, sodass ein starker innerer Abschnitt eigenständig geprüft wird, ohne eine neue, günstigere Baseline auswählen zu können.
````

</details>

<details><summary>Source unit 70</summary>

````text
Die Erkennung ist abgeschlossen, bevor die **Zeitliche Evidenz** zur Darstellung aggregiert wird. Ein anderes Darstellungs-Bin wie `1h` oder `6h` kann daher kein Ereignis erzeugen, zusammenführen, teilen oder entfernen. Nachdem Funkwegereignisse unabhängig qualifiziert wurden, können zeitgleiche Ereignisse gleichen Vorzeichens zur Prüfung gruppiert werden: **funkwegspezifisch** bezeichnet einen Funkweg, **richtungskohärent** mehrere Funkwege in benachbarten Kompasssektoren, **bereichsweit** mehrere getrennte Richtungen und **mehrere Funkwege** mehrere Funkwege, wenn für mindestens einen Beitragenden keine Richtung verfügbar ist. Dieser Kontext verändert nicht, ob ein einzelner Funkweg qualifiziert wurde. Die exakte Konstruktion, Stützzahlen, Zeitregeln und Formeln stehen in [Abschnitt 7.11](#sec-7-11).
````

</details>

<details><summary>Source unit 71</summary>

````text
Lies eine Ereigniskarte vom Intervall bis hinunter zur zugrunde liegenden Evidenz:
````

</details>

<details><summary>Source unit 72</summary>

````text
* **Spot-Impuls**, **Kurzer Ausbruch** und **Anhaltende Auslenkung** beschreiben die nach der Grenzkürzung beibehaltene zeitliche Form. Sie verwenden weder unterschiedliche Qualifikationsschwellen noch drücken sie unterschiedliche Gewissheit aus.
* Jede Funkwegzeile nennt das exakte `Rufzeichen + Locator` und die Richtung. **Erwartetes lokales ΔSNR** ist die zweiseitige, kandidatenbereinigte Baseline; **Beobachteter ΔSNR-Median** fasst die beibehaltenen Einheiten im berichteten Intervall zusammen; **Größte Einzelzyklusabweichung** ist das extremste beibehaltene Residuum von dieser Baseline. Diese Berichts-/Exportgröße ist unabhängig vom `*` im Zeitplot aller Funkwege; dieser wählt je Prüfereignis die Einheit mit betragsmäßig größtem Residuum ausschließlich unter den einzeln qualifizierenden nativen Einheiten aus und verwendet nie eine ungestützte oder nicht qualifizierende Episodenspitze.
* Bei einem Ereignis mit mehreren Einheiten führt die **Chronologische WSPR-Zyklusevidenz** UTC-Zeit, Funkweg, Richtung, lokale Baseline, Delta SNR und Residuum der beitragenden Beobachtungen auf. Ein Spot-Impuls aus nur einer Einheit benötigt keine doppelte Evidenztabelle.
* Die grünen Aktionen **`↓ In Station Insights anzeigen`** und **`↓ Drill-Down-Details anzeigen`** stehen rechts neben ihrem exakten Funkwegzeitraum. Die erste wählt diesen Funkweg aus, lädt den Drill-Down vor und navigiert für die breitere Laufhistorie zu Station Insights; die zweite nimmt dieselbe Auswahl und Vorladung vor, navigiert aber unmittelbar zum Drill-Down. Beide öffnen den **`Ausreißerfokus`** über die vollständige gestützte Baseline-Flanke vor dem Ereignis, die geschützte vorläufige Episode und die Baseline-Flanke danach; begrenzt wird er nur durch das abgeschlossene Analysefenster, und dieses Detektor-Stützintervall darf länger als 24 Stunden sein. Die fokussierte Delta-SNR-Abbildung zeigt jeden tatsächlichen beibehaltenen Joint Spot zu seiner nativen Zeit anstelle eines Binmedians, IQR oder einer Dichteschicht. Identische `*`-Marker kennzeichnen jede native Einheit im aktuellen Fenster, die innerhalb eines gemeldeten Kandidaten einzeln sowohl das konfigurierte Abweichungs- als auch das robuste-z-Kriterium erfüllt; dies schließt alle solchen Einheiten eines mehrteiligen Ausbruchs oder einer Episode ein. Ein dezentes Band **Fokussierte Episode** kennzeichnet die ausgewählte berichtete Episode. Es umfasst deren berichtetes Intervall der beibehaltenen Evidenz, ist an beiden Enden um eine halbe Breite der nativen Evidenzeinheit erweitert und wird am Fokusfenster abgeschnitten, damit ein Impuls aus einer Einheit sichtbar bleibt; es ist weder ein Konfidenzintervall noch eine Messung der Dauer eines physischen Ereignisses. Weitere Overlays zeigen das erwartete lokale Delta SNR, die Baselines davor und danach nur über ihre tatsächlichen Stützintervalle, symmetrische robuste-z-Hilfslinien bei 1, 2 und 3 sowie an der konfigurierten Qualifikationsschwelle und die konfigurierte Grenze der absoluten Abweichung ausschließlich für die fokussierte Episode. Andere mit Stern markierte Kandidateneinheiten können gegen andere lokale Baselines und robuste Streuungen bewertet worden sein. Dies sind Detektorhilfen und keine Konfidenzintervalle; das Überschreiten einer einzelnen Linie kann keinen Kandidaten allein qualifizieren. Prüfe anhand der zugrunde liegenden Werte für Target-SNR und korrigiertes Referenz-SNR sowie naher einseitiger Outcomes, ob die Bewegung des Delta SNR hauptsächlich von einer Seite ausging, ob sich eines der Signale der Decode-Grenze näherte und ob sich die Paarbarkeit in der Umgebung veränderte.
````

</details>

<details><summary>Source unit 73</summary>

````text
Die angezeigte Spanne von der ersten bis zur letzten Einheit ist das Intervall zwischen beibehaltenen Beobachtungen. Sie behauptet kein ununterbrochenes Verhalten dazwischen. Vergleiche den Zeitraum mit zeitgleichen Funkwegen, Stationslogs, Schaltplänen, Änderungen an Verstärkung oder Leistung, beobachteten Störungen und unabhängigen Messungen, bevor du eine Ursache zuschreibst.
````

</details>

<details><summary>Source unit 74</summary>

````text
Die drei Einstellungen behalten stets ihre wörtliche Bedeutung:
````

</details>

<details><summary>Source unit 75</summary>

````text
* Ein höherer Wert für **`Minimale absolute ΔSNR-Abweichung (dB)`** verlangt eine größere Abweichung.
* Ein höherer Wert für **`Minimaler robuster z-Wert`** verlangt eine im Verhältnis zur robusten Streuung in der Umgebung größere Abweichung.
* Ein niedrigerer Wert für **`Maximaler Unterschied zwischen Baseline davor/danach (dB)`** verlangt eine stabilere zweiseitige Baseline.
````

</details>

<details><summary>Source unit 76</summary>

````text
Die jeweils umgekehrte Änderung macht den Bericht weniger selektiv. Für Spot-Impulse, kurze Ausbrüche und anhaltende Auslenkungen gelten dieselben drei Werte; die Dauer gewährt keinen verborgenen Rabatt. Nutze Kandidaten bei explorativer Arbeit, um prüfenswerte Intervalle zu finden, und dokumentiere jede Schwellenänderung. Lege für eine bestätigende Untersuchung Schwellen, Benchmark-Design, Korrektur, Funkwegpopulation, Band und UTC-Bereich vor Sichtung des Ergebnisses fest und sichere sie. Prüfe anschließend, ob eine vergleichbare Abweichung in einem getrennten, geeignet kontrollierten Lauf erneut auftritt.
````

</details>

<details><summary>Source unit 77</summary>

````text
Berichte die Beobachtung als **vorübergehende lokale Delta-SNR-Abweichung in der beibehaltenen gepaarten Evidenz** und nenne exakten Funkweg, Intervall, Vorzeichen, stützende Einheiten und Detektoreinstellungen. Der Detektor ist deskriptiv: Er berechnet keinen p-Wert, korrigiert nicht für die Zahl der durchsuchten Funkwege oder Ereignisse und bestimmt keine physische Ursache.
````

</details>

<details><summary>Source unit 78</summary>

````text
Ist die Ausreißermeldung aktiviert, sichere ihre Befunde für den aktiven Bereich mit dem Analyseexport. Er ergänzt eine Zusammenfassung der Funkwegereignisse und eine chronologische CSV-Datei der gepaarten Evidenz, die über paketinterne Ereignis- und Funkwegereignis-IDs verknüpft sind. Damit die Evidenztabelle auch eigenständig verständlich bleibt, wiederholt sie Funkweg, Richtung und Ereignisklasse des Funkwegs. [Abschnitt 8.4](#sec-8-4) definiert beide Dateien und ihre bedingte Aufnahme.
````

</details>

