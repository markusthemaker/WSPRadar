# Chapter 7: readable scientific explanations

## Authorization and source model

The user approved the Chapter 7 rewrite on 2026-10-05: retain useful equations for normalization, correction and Delta SNR; replace abstract bookkeeping notation with precise prose, tables and examples; preserve scientific meaning; require neither a displayed formula for each method nor a formal appendix. Benchmark comes first and Performance receives equal care.

Source-led update: English is the content master; German is translated from the reviewed final English revision. Baseline commit: `11ec2bc`. The section-level disposition and parity records below are completed during integration. No runtime/scientific calculation is changed.

## Baseline provenance

- `docs/doc_en.py` Git-blob SHA-256: `a5fcb12db0a0fb261c58c525253a489c9f6034d75da80d7cebc84f1eebb13473`


## EN: verbatim baseline passages

The complete original sections are retained below. This includes all superseded prose and mathematical representations, so removed or consolidated wording remains traceable without adding a formal specification to the end-user manual. Each section is accounted for by the disposition review.


### 7. Scientific Methods

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7"></a>
### 7. Scientific Methods

Benchmark compares the SNR of Joint Spots: how did recorded Target and Reference SNR differ for the same qualifying peer-cycle? Performance counts confirmed opportunities: how often did the Target succeed when the required activity was observable? Both questions depend on which peers and cycles enter the calculation.

This chapter defines that scientific contract. WSPRadar starts from reported observations, constructs eligible evidence units, derives quantities such as normalized SNR and paired ΔSNR, and then calculates descriptive summaries. Those summaries are exact for the retained evidence under the selected rules. They become estimates of a broader or future population only if an additional sampling and dependence model is supplied; WSPRadar does not make that inferential step automatically.

It is useful to distinguish five levels:

1. **Reported observations:** uploaded WSPR spots with callsigns, locators, power, time and SNR.
2. **Constructed evidence units:** qualifying opportunities, peer-cycles, Joint units formed by WSPRadar’s eligibility and matching rules.
3. **Derived quantities:** normalized SNR, Decode Outcomes and Target-minus-Reference ΔSNR for an individual evidence unit.
4. **Descriptive summaries:** rates, medians, reach, evidence shares and temporal or geographic summaries calculated from the retained evidence.
5. **Interpretation beyond the run:** statements about future behavior, a wider population or a physical cause. Such generalization requires additional assumptions and experimental control; the calculation alone is not sufficient.

**Method orientation**

| Design | Lowest comparison unit | Conditioning / eligibility | Principal summary | Primary boundary |
|---|---|---|---|---|
| RX Reference Setup/Station | one remote-transmitter peer-cycle | Target active; both receivers report the same transmitter-cycle for ΔSNR | station median ΔSNR, then median across stations | complete receive paths unless chains are controlled |
| TX Reference Setup/Station | one remote-receiver peer-cycle | Target active; same receiver-cycle for paired ΔSNR | station median ΔSNR, then median across stations | power, chain and joint-decode selection |
| Reference Neighborhood (Local Median) | one Target/local-Reference peer-cycle | Target active; one contribution per active local identity | local median Reference, then station/segment Delta medians | changing uncalibrated membership |
| RX Performance | one remote-transmitter peer-cycle | Target RX active; peer TX decoded by Target RX or another eligible RX | peer Decode Rate, then equal-peer mean; pooled opportunity rate retained | conditional observability, not calibrated sensitivity |
| TX Performance | one remote-receiver peer-cycle | Target TX active; peer RX decodes Target TX or another qualifying same-band TX | peer Decode Rate, then equal-peer mean; pooled opportunity rate retained | conditional observability, not all attempted transmissions |

The hierarchy can be read from left to right: WSPRadar first decides which evidence units belong to the analysis, then calculates a peer- or path-level quantity, and only then forms the displayed station-balanced summary. The formulas below make those steps auditable; the text following each formula explains the same operation in ordinary station terms.

**Notation used below**

| Symbol | Meaning |
|---|---|
| $i$ | one peer <strong class="defined-term">identity</strong>, defined as exact `callsign + reported locator` |
| $c$ | one eligible WSPR <strong class="defined-term">cycle</strong> |
| $g$ | one retained <strong class="defined-term">geographic</strong> scope or segment |
| $b$ | one distance or time <strong class="defined-term">bin</strong> |
| $S_{i,c}$ | Target <strong class="defined-term">success</strong> indicator within an eligible Performance opportunity |
| $O_{i,c}$ | Performance <strong class="defined-term">opportunity</strong> indicator after activity, identity and population rules |
| $D_{i,c}$ | paired Target-minus-Reference <strong class="defined-term">Delta</strong> SNR where both sides are observed |
| $T_{i,b},J_{i,b},R_{i,b}$ | Only <strong class="defined-term">Target</strong>, <strong class="defined-term">Joint</strong> and Only <strong class="defined-term">Reference</strong> counts in Benchmark scope $b$ |

An indicator is `1` when its condition is met and `0` otherwise. The notation makes denominators and weighting explicit; the text after each formula explains the same calculation in ordinary station terms.

The subscripts identify whose evidence is being counted and where it belongs. A sum adds retained units; a median is the middle ordered value, or the mean of the two middle values for an even count. These are operations on the selected evidence, not assumptions that the observations are independent.

This chapter uses **summary** or **descriptive statistic** for the rates, medians, shares and distributions calculated from the retained evidence. The distinction matters because a value can be calculated exactly for the retained rows while still describing a narrow or selected population.
````

</details>


### 7.1 Data source, observation units and time model

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-1"></a>
#### 7.1 Data source, observation units and time model

WSPRadar reads public WSPR reports from one selected database through read-only queries for each completed run. Reports are observational records produced by heterogeneous transmitters, receivers, decoders and reporting systems. A completed run does not combine data sources; the selected database belongs to the run provenance.

A **spot** is one reported successful decode row. A **WSPR cycle** is the two-minute interval aligned to an even UTC minute. Same-cycle analyses consolidate qualifying rows by side, peer identity and cycle before classification. The effective UTC boundaries shown in the controls define the analysis window.

WSPR-2 names the two-minute transmission mode; Type 1, Type 2 and Type 3 describe message contents. Extended WSPR can convey a compound callsign and precise six-character locator across two complementary transmissions. A Type 2 message carries the compound callsign and power but no locator; the matching Type 3 message carries a 15-bit hash of that callsign, the six-character locator and power. The two transmissions are separate WSPR cycles, not two fields of one database row <a href="#ref-12">[Ref-12]</a>.

WSPRadar does not classify a row as Type 1, Type 2 or Type 3 and does not join complementary extended-WSPR transmissions across cycles. Each database row belongs to its reported cycle.

WSPRadar does not require both complementary message phases before admitting a same-cycle unit; it requires the identities needed for that particular comparison to be resolved in the database. In same-cycle TX Benchmark, the resolved Target and Reference rows must occur in the same cycle at the same remote receiver identity. Matching message types are not an eligibility requirement: the recorded rows must satisfy the applicable identity, cycle and filtering rules. WSPRadar never pairs reports from different WSPR cycles.

An extended sequence can therefore contribute Joint Spots in either or both of its cycles. A qualifying Joint Spot in one cycle does not require a Joint Spot in the other. The recommendation to align message types and transmission schedules in a controlled TX experiment improves comparability of the observations; it is an operating recommendation, not a message-type check performed by WSPRadar. [Section 2.2.1](#sec-3-tx-benchmark-simultaneous) explains the practical setup.

The lowest unit differs by design:

* Performance and Benchmark use one peer identity in one eligible WSPR cycle.
* Reference Neighborhood additionally constructs a cycle/path Reference from qualifying local identities before forming Target-minus-Reference evidence.

Same-cycle matching means the same two-minute UTC reported slot and exact remote callsign plus full reported locator on the same band. It does not require identical RF frequencies or prove equal physical propagation paths; simultaneous TX signals normally need distinct clear frequencies. Only Joint Spots supply ΔSNR. One-sided evidence and station-level Both (Async) remain available without an invented missing-side SNR.

These units are constructed from reported spots; they are not additional radio measurements. Their purpose is to define unambiguously the conditions under which a success, missed decode or paired difference is counted.

The historical fallback relaxes the `code = 1` requirement only when the strict request has no Target-side evidence and the entire selected period ends before 1 January 2022 at 00:00 UTC. Run status records which source path was used. The eligibility boundary and historical mode uncertainty are described in [Section 5.4](#sec-6-4). Upstream delay and data-quality limitations are described in [Section 5.6](#sec-6-6).
````

</details>


### 7.2 Identity, matching and row consolidation

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-2"></a>
#### 7.2 Identity, matching and row consolidation

WSPRadar treats reported identity as scientific data rather than a cosmetic label.

**The basic observation is one remote station in one two-minute WSPR cycle.** The remote station is a transmitter in RX analysis and a receiver in TX analysis. Benchmark compares Target and Reference evidence for that remote station within the same cycle.

Both Performance and Benchmark retain only cycles with observable Target activity. That activity need not be observed on every individual remote-station path: evidence elsewhere can establish that the Target was active in the cycle. [Section 7.3](#sec-7-3) defines the activity checks and their differences between analyses.

Station identities are selected as follows:

| Station or role | How WSPRadar identifies it |
|---|---|
| **Target — all analyses** | Exact receiving callsign in RX, or transmitting callsign in TX, together with the Target QTH's four-character locator. |
| **Reference — Reference Setup/Station** | Exact Reference callsign together with its four-character locator resolved from the database. |
| **Remote station — all analyses** | Exact callsign together with the full reported locator: the remote transmitter in RX, or the remote receiver in TX. |
| **Local contributors — Reference Neighborhood** | Local receiver identities in RX, or local transmitter identities in TX, distinguished by exact callsign and full reported locator within the selected radius. |

Performance evaluates the Target's observations and confirmed opportunities for each remote station and cycle. Reference Setup/Station compares the Target with one identified Reference. Reference Neighborhood constructs its Reference separately for each remote station and cycle from the qualifying local contributors.

Multiple qualifying reports for the same side, remote station and cycle are consolidated before forming the result. This produces one retained value for that side in that cycle; it does not combine reports from successive cycles. The strongest-report and neighborhood-median rules are explained below.

Target selection from the database uses grid-4 even when a six-character QTH is configured. The full QTH remains relevant to distance, azimuth, solar elevation and local-radius geometry. A matching grid-4 does not prove physical co-location.

This matching uses the exact callsign and locator fields supplied by the selected database. WSPRadar neither reconstructs a compound callsign from its hash nor borrows a locator from a neighboring Type 2 or Type 3 cycle. A simultaneous extended-WSPR sequence can therefore contribute one same-cycle comparison unit per remote receiver identity in each eligible cycle when both sides resolve consistently in the database; a missing or differently represented callsign/grid-4 does not become eligible by inference.

If several qualifying non-identical rows represent one logical side/peer/cycle identity, WSPRadar retains the strongest qualifying normalized SNR as the best observed value for that logical identity. This prevents exact repeats or weaker secondary decodes from lowering the retained side value, but it is not a representative central value for one physical receiver. Different multi-receiver/reporting behavior on the two sides can therefore introduce asymmetry. Reference Neighborhood (Local Median) instead forms a median within each local identity before aggregating across identities.

**Why retain the strongest report?** Multiple reports for the same station, peer and WSPR cycle do not necessarily represent independent observations. If weaker reports arise from transmitter or receiver replicas, spurious components or secondary decodes, their mean or median has no established interpretation as the main signal's SNR. Retaining the strongest qualifying normalized SNR represents the best observed reception and prevents weaker secondary reports from lowering that value. These reports still contribute only one detection outcome or paired observation for the relevant cycle/path.

This best-report interpretation is consistent with WsprDaemon's documented multi-receiver merging: when several receivers contribute reports for the same transmission, it reports the best SNR to WSPRnet. This is a reporting precedent, not proof that a particular stored report represents the intended signal or that both comparison endpoints selected the same spectral component. <a href="#ref-11">[Ref-11]</a>

The strongest-report rule applies to Performance SNR values, both endpoints of simultaneous fixed-Reference Benchmark, and the Target side of Reference Neighborhood (Local Median). Local Reference contributors retain their within-identity medians and subsequent median across identities. These distinct constructions are defined in [Section 7.7](#sec-7-7). Medians and IQR across retained observations remain summaries of the resulting evidence, separate from choosing one SNR value within a cycle/path.

The local pool excludes the Target by exact callsign. A base callsign and suffixed callsign are distinct unless the exact Target form matches. Bad, stale or changing locators can split one physical station, move it geographically or trigger the moving-station exclusion.
````

</details>


### 7.3 Target-active conditioning and eligibility

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-3"></a>
#### 7.3 Target-active conditioning and eligibility

A silent cycle is ambiguous: the Target may have been off air, or its participation may simply have produced no reported decode. WSPRadar counts against the Target only in cycles where Target participation is observable. This restriction is called **Target-active conditioning**.

Let $A_c$ indicate observable Target participation in cycle $c$:

* TX: at least one qualifying Target transmission report exists somewhere in the cycle.
* RX: the Target receiver uploaded at least one qualifying decode in the cycle.

Performance and Benchmark condition on $A_c=1$. This prevents periods without observable Target activity from becoming automatic counter-evidence, without distinguishing downtime from unobserved participation. It changes the analysis population: the result describes cycles in which Target participation was observable, not all clock time or all planned attempts.

The conditioning is asymmetric. Reference uptime is not a second gate and must be controlled or documented externally. Swapping Target and Reference can therefore change eligible cycles and one-sided Decode Outcomes even when the sign of Joint-only ΔSNR reverses as expected.

Every Joint observation already implies Target participation, so the gate does not change Joint-only ΔSNR values. It changes the population of one-sided/asynchronous outcomes and, in Performance, the opportunity denominator.

Target-active evidence may be established globally even when the peer that proves activity lies outside the selected geographic analysis scope. That peer establishes $A_c$ only; it does not enter scoped outcomes, summaries or exports.

**Which reports can establish activity?** In Performance, a Target report involving a peer later removed by the special-callsign or moving-station exclusion can still prove activity. In Benchmark, these peer exclusions apply before activity is established, so the Target needs a report involving a peer that survives them. Geographic scope is applied afterward in both designs. Consequently, a cycle with only an excluded peer as its Target-activity witness can retain a Performance opportunity for another eligible peer but no Benchmark outcome. The excluded peer itself contributes to neither result population.
````

</details>


### 7.4 Performance analysis target, classification and summary statistics

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-4"></a>
#### 7.4 Performance analysis target, classification and summary statistics

Performance describes Target participation among confirmed opportunities in the retained peer population. Its denominator includes successes and externally supported Misses; it is neither all clock cycles nor only cycles confirmed by other stations.

For peer $i$ and Target-active cycle $c$, let $T_{i,c}=1$ when a valid Target-side decode is present and $E_{i,c}=1$ when qualifying external evidence confirms the peer endpoint activity. Apply the selected band, exact peer identity, filter and geographic scope rules before including the peer-cycle. Success $S_{i,c}$, opportunity $O_{i,c}$ and Miss $M_{i,c}$ are defined by:

$$S_{i,c}=T_{i,c},\qquad O_{i,c}=T_{i,c}\lor E_{i,c},\qquad M_{i,c}=E_{i,c}\land\neg T_{i,c}$$

Thus every valid success supplies its own opportunity, with $S_{i,c}\le O_{i,c}$ and $O_{i,c}=S_{i,c}+M_{i,c}$. The method identifier is `opportunity-v3`.

In the formula, $\lor$ means “or,” $\land$ means “and,” and $\neg$ means “not”: an opportunity needs a Target decode or external confirmation, while a Miss needs external confirmation without a Target decode.

* RX roles: the **Target RX** receives the **peer TX**. The peer TX → Target RX report confirms both endpoints and is a success. A peer TX → other eligible RX report confirms that peer TX was transmitting; it supports a Miss only when the Target RX is also demonstrably active in that cycle.
* TX roles: the **Target TX** transmits to the **peer RX**. The Target TX → peer RX report confirms both endpoints and is a success. Another qualifying TX → that same peer RX report confirms that peer RX was receiving; it supports a Miss only when the Target TX is also demonstrably active in that cycle.

A Target-only success has $T_{i,c}=1$ and $E_{i,c}=0$. Its provenance is retained as a subset of successes; it is already included once in both the success count and the opportunity count. External confirmation accompanying a success does not create another opportunity. If both flags are zero, endpoint activity is insufficient: the peer-cycle remains unknown and excluded. The Target-Active Gate is unchanged. Activity somewhere else cannot prove that a particular silent Target RX or peer RX was listening.

| Target decode | External evidence | Success | Opportunity | Miss | Meaning |
| :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | 0 | 1 | 1 | 0 | Target-only success; provenance subset |
| 1 | 1 | 1 | 1 | 0 | Externally supported success |
| 0 | 1 | 0 | 1 | 1 | Externally supported Miss in a Target-active cycle |
| 0 | 0 | 0 | 0 | 0 | Unknown endpoint activity; excluded |

For one qualifying peer, add its opportunities and Target successes across the retained cycles, then divide successes by opportunities:

$$n_i=\sum_c O_{i,c},\qquad h_i=\sum_c S_{i,c}$$

$$r_i=100\%\times\frac{h_i}{n_i}$$

Here, $n_i$ is the number of qualifying opportunities retained for peer $i$, $h_i$ is the number of those opportunities in which the Target succeeded, and $r_i$ is that peer's Decode Rate. A peer contributes only when $n_i$ meets the configured minimum.

For geographic scope $g$ with qualifying peer set $I_g$, $|I_g|$ is the number of qualifying peers. Add their individual rates and divide by this peer count to obtain the **Station-balanced Decode Rate**:

$$R_{station}(g)=\frac{1}{|I_g|}\sum_{i\in I_g} r_i$$

The **Opportunity-level Decode Rate** is:

$$R_{opportunity}(g)=100\%\times\frac{\sum_{i\in I_g}h_i}{\sum_{i\in I_g}n_i}$$

In plain terms, the first calculates one rate per peer and then gives every peer one equal vote. The second pools all qualifying opportunities and therefore gives more influence to peers that contributed more opportunities. These are complementary summaries of the retained evidence, not competing estimates of one uniquely defined “true” Decode Rate.

**Example: one result, two weighting questions.** Two peers already meet the configured opportunity minimum. Peer A has `90 successes / 100 opportunities = 90%`; peer B has `5 / 10 = 50%`. Giving each peer equal weight yields **70%**. Pooling the opportunities yields `95 / 110`, or **86.4%**. The pooled denominator contains 95 successes and 15 Misses, with each opportunity counted once. The larger value reflects the greater evidence volume on the more successful path; it does not make the equal-peer calculation wrong.

At-least-once Peer Reach is:

$$Reach(g)=100\%\times\frac{|\{i\in I_g:h_i\ge1\}|}{|I_g|}$$

The numerator counts qualifying peer identities that produced at least one Target success; the denominator counts all qualifying peers in the scope. A peer with one success and a peer with many successes both count once for Reach.

Reach measures breadth. For a fixed eligible peer set, adding observations while retaining the earlier evidence cannot remove an earlier success. Across reruns, however, the qualifying peer population can change, so the reported Reach percentage need not increase with duration. Reach does not describe how consistently those peers were decoded; Decode Rate answers that separate question. In the two-peer example above, Reach is 100% even though the peers have different Decode Rates.

Successful Target SNR is defined only where the Target was decoded/reported, including Target-only successes. It is therefore a success-conditioned distribution. Its underlying evidence comprises all retained successes after strongest-report consolidation and normalization; the later sections define how each view groups and weights these values for medians, IQR and extremes. The same classification supplies station thresholds, both Decode Rate weightings, maps, Peer Reach, chronological and folded profiles, Station Insights, Selected Station Evidence, Drill-Down and exports. Missed opportunities have no Target SNR and no synthetic value. Decode Rate and successful SNR must be interpreted jointly because a system that adds marginal decodes can show lower successful-SNR summaries while improving practical reach.

The Performance analysis target is the Target's conditional participation among observable opportunities in the retained population. It is not unconditional receiver sensitivity, the success probability of every attempted transmission or absolute station efficiency.
````

</details>


### 7.5 Power normalization, correction and Benchmark ΔSNR

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-5"></a>
#### 7.5 Power normalization, correction and Benchmark ΔSNR

WSPR reports SNR on the WSJT scale in dB relative to a 2500 Hz reference bandwidth and carries reported transmit power in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar expresses successful SNR observations in both RX and TX analyses at a common reported transmit power of 30 dBm (1 W). This compares recorded signal levels after removing the reported power difference; it does not recreate the decodes that would have occurred at that power:

$$SNR_{norm}=SNR_{measured}-P_{TX(dBm)}+30$$

In practical terms, a signal with `10 dB` less reported transmit power is raised by `10 dB` for this comparison. For example, an SNR reported as `-15 dB` at `20 dBm` is normalized to `-5 dB` at `30 dBm`. In words, the reported transmit-power difference is removed by expressing every successful SNR observation as though the reported power had been `30 dBm`. This removes only the **reported** power term.

Here $SNR_{measured}$ and $SNR_{norm}$ are SNR values in dB, and $P_{TX(dBm)}$ is the transmit power reported for that observation. Decode Outcomes and the Performance opportunity denominator remain those actually observed. Normalization does not correct antenna gain, radiation efficiency, feedline loss, EIRP, receiver calibration or local noise.

Reference-side correction is additive:

$$SNR_{R,corr}=SNR_R+C_R$$

For one Joint Spot, subtract corrected Reference SNR from normalized Target SNR:

$$D_{i,c}=\Delta SNR_{i,c}=SNR_{T,i,c}-SNR_{R,corr,i,c}$$

Here $C_R$ is the signed additive Reference-side correction. In the first equation, $SNR_R$ and $SNR_{R,corr}$ denote Reference SNR before and after correction. In the paired equation, the indices $i,c$ identify the peer and matched evidence unit; $SNR_{T,i,c}$ is the corresponding normalized Target SNR and $SNR_{R,corr,i,c}$ is the corrected Reference SNR. The configured correction belongs to the Reference side; it is not added to the Target. Positive $D_{i,c}$ favors the Target; negative favors the Reference. A positive correction makes the Reference stronger before subtraction and therefore lowers ΔSNR. The entered calibration offset uses the same `target - reference` sign.

**Sign check.** With normalized Target SNR `-10 dB` and Reference SNR `-12 dB`, ΔSNR is `+2 dB`. A Reference correction of `+1.5 dB` makes the Reference `-10.5 dB`, so ΔSNR becomes `+0.5 dB`. The Target observations have not changed; the comparison accounts for the entered Reference offset.

The value $D_{i,c}$ is an observed paired difference for exactly one retained comparison unit. It is calculated exactly from the two retained SNR values and the configured correction, if any. Its interpretation still depends on what the two sides represent and how well the physical experiment controlled the remaining chains.

In same-transmitter RX pairs, the common reported TX-power term cancels. TX pairs involving different signals depend directly on reported-power accuracy and on any uncorrected transmitter/feedline difference. A Reference correction is scientifically defensible only when the offset is approximately additive and stable over the relevant band, level, hardware state and time.
````

</details>


### 7.6 Paired evidence, Decode Outcomes and missingness

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-6"></a>
#### 7.6 Paired evidence, Decode Outcomes and missingness

Benchmark answers two linked evidence questions:

1. the distribution of Target-minus-Reference ΔSNR among **Joint** comparison units; and
2. the composition of retained evidence into **Only Target**, **Joint**, **Only Reference** and, at identity level, **Both (Async)**.

ΔSNR exists only when both sides produce comparable evidence. The Joint subset is therefore selected on successful observation of both sides. Missing pairs cannot generally be treated as a random sample of all possible pairs: weak signals, collisions, QRM, decoder behavior, power differences and path conditions can affect whether a pair exists.

The surviving Joint Spots can therefore underrepresent conditions close to either side's decode threshold.

Extended-WSPR Type 3 rows identify a compound callsign through a 15-bit hash. QRP Labs documented a mechanism that misassociates reported identities involving this limited hash space <a href="#ref-19">[Ref-19]</a>. An unresolved or colliding hash can leave a decode unidentified or associate it with the wrong callsign, locator or power. A few isolated affected rows among tens of thousands may leave medians unchanged or nearly unchanged, but that must be checked in the affected population, including Target/Reference side, message phase, receiver and time. Dataset size alone is not protection, however: a systematic, clustered or Target/Reference-asymmetric artifact can still change Joint coverage, one-sided outcomes, individual station medians or a narrow segment. WSPRadar can check whether the configured exact callsign and grid-4 are present in the selected database; it cannot prove that every upstream hash association was physically correct. The database preflight and phase-specific audit in [Appendix B](#sec-simultaneous-tx-setup) are therefore required when compound callsigns are used.

One-sided evidence has no missing-side SNR to reconstruct. It cannot be assigned an artificial ΔSNR and is not power-normalized as a pair. In TX Benchmark, unequal actual or reported powers can strongly affect one-sided outcomes even when Joint ΔSNR is normalized.

`Both (Async)` means that an identity has retained evidence from both sides but lacks a qualifying same-cycle pair for the relevant station category. It indicates broader two-sided participation without contributing paired ΔSNR.

Successful-SNR censoring in Performance and Joint-decode selection in Benchmark are distinct selection processes. WSPRadar exposes Decode Outcomes and Joint Evidence Share so the paired ΔSNR summary can be read against the wider retained evidence rather than treated as the complete station population.
````

</details>


### 7.7 Aggregation hierarchy and weighting

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-7"></a>
#### 7.7 Aggregation hierarchy and weighting

WSPRadar aggregates the evidence hierarchically so that one high-volume peer does not dominate station-balanced summaries solely by reporting more observations.

**Performance**

1. Classify each eligible peer-cycle.
2. Aggregate all qualifying Target successes and externally supported Misses by peer identity. Retain Target-only provenance as a subset of successes without adding it again to totals.
3. Apply the minimum opportunity count.
4. Calculate one peer Decode Rate $r_i$.
5. Calculate the equal-peer mean $R_{station}$.
6. Retain $R_{opportunity}$ as the complementary volume-weighted summary.

<p style="page-break-after: avoid; -pdf-keep-with-next: true;"><strong>Simultaneous Benchmark</strong></p>

Does the shift span peers, or mainly reflect prolific paths? Read the following summaries alongside station distributions and counts.

1. Consolidate Target and Reference evidence by peer and cycle.
2. Calculate $D_{i,c}$ for Joint cycles.
3. Apply the minimum Joint count per peer.
4. Calculate the peer median:

    $$m_i=\operatorname{median}_{c}(D_{i,c})$$

5. For scope $g$, calculate the station-balanced segment summary:

    $$M_g=\operatorname{median}_{i\in I_g}(m_i)$$

In words, each peer is first reduced to one typical paired difference, $m_i$, and the segment summary $M_g$ is then the median across those peer values. A peer with many Joint observations therefore cannot dominate the station-balanced segment merely through volume.

The observation-level median of all $D_{i,c}$ is retained separately. It answers a different question because peers with more Joint observations receive more weight.

**Illustrative example: why the summaries can disagree.** These three peer identities already qualify in one segment after matching, correction and filtering. Each entry is a distinct retained Joint peer-cycle.

| Peer identity | Retained ΔSNR values (dB) | Peer median (dB) |
|---|---|---:|
| A | +6, +6, +6, +6, +6, +6 | +6 |
| B | -2, -2 | -2 |
| C | -1, -1 | -1 |

The station-balanced median is **-1 dB**: the middle peer median in `-2, -1, +6`. The observation-level median is **+6 dB**: the fifth and sixth of all ten ordered values are both `+6`. Peer A supplies six observations but only one peer median. Both results describe the same Joint evidence with different weighting: inspect the contributing paths when they disagree. Neither weighting alone establishes an antenna advantage or creates independent experimental repetitions.

For every Benchmark design, a station is one exact `callsign + full reported locator` identity for both weighting and segment support. Each identity must separately meet the configured minimum Joint-evidence count. The identities contributing one peer median each are exactly the identities counted toward the minimum qualifying stations per map segment. Identities with only one-sided evidence do not contribute to this ΔSNR support count. The same callsign at different full locators counts separately, including two locators in the same grid-4. This counts reported path identities; it does not establish independent physical stations or sites.

For example, two qualifying identities with the same callsign and locators `JO31AA` and `JO31AB`, with peer medians of `+2 dB` and `+4 dB`, contribute a segment median of `+3 dB` and support count `2`. A minimum of two qualifying stations retains that segment; a minimum of three does not.

<p style="page-break-after: avoid; -pdf-keep-with-next: true;"><strong>Reference Neighborhood (Local Median)</strong></p>

For each remote peer-cycle, WSPRadar first calculates one normalized SNR contribution per active local `callsign + locator`, then takes the exact median across contributing local identities. An absent local identity is omitted rather than assigned zero. Reference correction is applied before the local pool is aggregated. The Target is compared with this cycle/path median, after which peer and segment ΔSNR medians are calculated.

When several qualifying reports belong to the same local Reference identity, remote peer and cycle, their normalized SNR values first form a within-identity median. Each contributing local identity then supplies one value to the neighborhood median. The existing Target-side consolidation retains the strongest qualifying normalized SNR; the neighborhood method does not apply identical report consolidation to both sides.

A local identity uses its callsign and full reported locator. Equal weighting of these identities does not guarantee equal weighting of independent physical sites: multiple reporting identities may share equipment or a location.

There is no separate minimum number of local contributors per peer-cycle. With one contributor, the Reference equals that contributor’s value. With no contributors, no Reference SNR or paired ΔSNR is available. The minimum joint-evidence and station-support requirements elsewhere in the analysis do not impose a minimum neighborhood size.

**Changing membership can change the comparison.** Suppose three local identities contribute corrected SNR values `-18, -12, -6 dB`; their Reference median is `-12 dB`. With Target SNR fixed at `-10 dB`, ΔSNR is `+2 dB`. If the `-6 dB` contributor is absent in another cycle while the other values stay the same, the Reference median becomes `-15 dB` and ΔSNR `+5 dB`. This shift needs no change at the Target: it arises from the changed local population.

The neighborhood median describes qualifying reported observations. Missing reports are not measurements of zero SNR, and the contributing set can vary by remote peer and cycle. Increasing the number of observations does not by itself remove systematic reporting differences, selection effects or dependence between observations.

Medians reduce sensitivity to isolated extreme values, quantized SNR outliers and duplicate-like bursts. They do not remove systematic calibration error, propagation bias or dependence across cycles and stations.
````

</details>


### 7.8 Geographic, temporal and selected-path summaries

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-8"></a>
#### 7.8 Geographic, temporal and selected-path summaries

<a id="sec-7-8-1"></a>
##### 7.8.1 Geographic summaries

Segment Inspector starts from the complete qualifying peer population in the active retained scope; table sorting, row selection and visibility controls do not change these summaries.

Performance distance profiles group peers by exact calculated distance from Target QTH. A deterministic width of `125`, `250`, `500` or `1,000 km` is selected from the active distance span, with edges anchored at integer multiples from `0 km` and the final selected upper boundary included. Disjoint selected ranges retain missing gaps rather than treating them as zero evidence.

For each distance bin, WSPRadar calculates:

* at-least-once Peer Reach;
* station-balanced Decode Rate;
* Opportunity-level Decode Rate; and
* successful Target SNR, first reduced to one median per peer and then summarized across peer medians.

For successful-SNR spread, three or more peer medians produce an IQR, two produce a min–max interval, and one produces a single point. Counter-only peers receive no synthetic SNR. Distance inherits the precision of the reported Maidenhead locator and is not survey-grade positioning.

Benchmark geographic summaries use one peer median ΔSNR per qualifying identity and then the segment median of those peer medians. Observation-level ΔSNR remains available as a separately weighted distribution.

The geographic station-balanced view asks what the qualifying peers typically showed; the observation-level distribution asks what the retained Joint Spots showed when each pair counts.

<a id="sec-7-8-2"></a>
##### 7.8.2 Benchmark evidence coverage

Joint Evidence Share answers how much retained Benchmark evidence supports an SNR comparison between both sides. Its denominator includes all three outcomes, not just Joint Spots and not every scheduled cycle.

For station $i$ in bin $b$, let Only Target, Joint and Only Reference counts be $T_{i,b}$, $J_{i,b}$ and $R_{i,b}$, with:

$$N_{i,b}=T_{i,b}+J_{i,b}+R_{i,b}$$

A contributing station supplies one split support vote:

$$v_{T,i,b}=\frac{T_{i,b}}{N_{i,b}},\qquad v_{J,i,b}=\frac{J_{i,b}}{N_{i,b}},\qquad v_{R,i,b}=\frac{R_{i,b}}{N_{i,b}}$$

The station-balanced Joint Evidence Share is:

$$JES_{station}(b)=100\%\times\operatorname{mean}_{i}\left(\frac{J_{i,b}}{N_{i,b}}\right)$$

The outcome-level share is:

$$JES_{outcome}(b)=100\%\times\frac{\sum_iJ_{i,b}}{\sum_iN_{i,b}}$$

The station-balanced form first asks what fraction of each peer's retained units were Joint and then averages those fractions. The outcome-level form simply pools all retained units before taking the Joint fraction. The same distinction — equal peer weight versus equal evidence-unit weight — appears elsewhere in WSPRadar.

The first gives every contributing peer equal weight; the second gives every retained comparison unit equal weight.

Only peers with at least one retained outcome in that bin contribute; a peer without evidence contributes no fraction. The three fractions for one peer sum to one support vote. Joint Evidence Share measures pairability — the fraction of retained evidence that can contribute ΔSNR. It is not a Target win rate.

Under the Target-Active Gate, Only Target and Only Reference are directional and asymmetric. One-sided evidence still has no ΔSNR.

<a id="sec-7-8-3"></a>
##### 7.8.3 Temporal summaries and UTC folding

Chronological views preserve the actual sequence of the run across the full selected UTC window using the selected time-bin width. Bins begin at the selected start; the final interval may be shorter, and intervals without evidence remain blank rather than becoming 0 dB. UTC-hour views fold evidence from represented dates onto the same 24-hour UTC clock. Chronological views ask what changed during this run; folded views ask whether a pattern recurred at a particular UTC hour across the represented dates.

Offered chronological widths are governed by the complete run duration, not by the observed evidence span: runs through 6 hours default to `10m`; longer runs through 24 hours default to `30m`; runs longer than 24 hours default to `12h`. The offered sets are listed in [Section 4.5](#sec-5-5), including the `2h` choice in every duration tier.

Performance successful-SNR deviation compares each path with its own usual successful level in this run, so persistently strong paths do not define the zero for weaker paths. A peer enters the anomaly population only when it has at least three successful normalized Target-SNR observations in the complete run window. Its baseline is the median of those successes. Each successful observation contributes:

$$A_{i,c}=SNR_{i,c}-\operatorname{median}_{c'}(SNR_{i,c'})$$

Here $c$ identifies the current successful observation and $c'$ indexes all successful observations for peer $i$ in the complete run window that define its baseline. Thus `0 dB` means “at this path's own usual successful level,” not Target–Reference equality. A positive anomaly is a stronger-than-usual successful decode for that path, and a negative anomaly is weaker than usual.

Chronologically, each peer contributes at most one median anomaly per selected bin. In the UTC-folded view, each peer contributes one median per date and UTC hour before those peer-date-hour values are summarized across the folded population. Within each peer-date-hour, additional rows do not add weight after that median is formed. Peers represented on more dates and dates containing more peers still contribute more values to the folded population; this is not equal weighting of peers or dates over the full run.

Performance temporal support uses the same qualifying peers but retains all confirmed opportunities, including peers omitted from the successful-SNR anomaly layer. In a chronological bin, each peer contributes one split vote according to its within-bin Decode Rate. The station-support total is therefore the number of contributing peers, while the split ratio reproduces the station-balanced rate. The opportunity-support total is the raw confirmed-opportunity count, and its split ratio reproduces the Opportunity-level rate.

For each folded UTC hour, station support is the average number of distinct peer-date-hour presences over represented dates whose hour slot overlaps the analysis window. The folded station-balanced rate is calculated by pooling each peer's outcomes at that UTC hour across represented dates, calculating one rate per peer, and then giving each peer equal weight. Folded opportunity counts are pooled outcome totals divided by the corresponding represented-date denominator.

For Performance, a **represented UTC date** is a date with at least one qualifying confirmed opportunity somewhere in the active scope and selected window. A represented date-hour inside the window contributes zero when it has no evidence; a date-hour outside the window is excluded. A partially overlapping first or last hour counts as one represented slot rather than receiving exposure weighting, so boundary-hour averages can be depressed. UTC-hour folding requires at least two represented dates.

Benchmark temporal ΔSNR uses retained Joint observations. If no paired values remain, the ΔSNR panel still shows the full selected UTC window and states that paired Δ SNR evidence is absent. This means no retained Joint observation remains in the displayed scope; it does not by itself mean that the data source returned no observations, and temporal coverage can still show one-sided outcomes. Chronological bins summarize raw paired values in actual time; UTC-hour bins summarize the same paired population by hour across dates represented by retained Benchmark evidence. Benchmark temporal coverage uses all retained Only Target, Joint and Only Reference units and the two Joint Evidence Share summaries above. Benchmark folding likewise requires at least two represented evidence dates.

<a id="sec-7-8-4"></a>
##### 7.8.4 Selected-path summaries

Selected Station Evidence filters the active retained scope to one exact peer identity without changing the upstream analysis population.

For Performance, the selected path reports:

* actual normalized successful Target SNR in chronological bins;
* one date-hour median per represented date in the folded SNR profile;
* successful/counter opportunity counts; and
* Decode Rate through time.

With one peer, station-balanced and Opportunity-level Decode Rate are numerically identical within a populated bin because both use that peer's same successes and opportunities; the separate support counts still distinguish path presence from evidence volume.

For Benchmark, the selected path reports observation-level ΔSNR for each Joint unit and separately reports Only Target, Joint and Only Reference coverage. Changing the selected path or display bin changes only the retained-evidence view, not matching, eligibility or aggregation upstream.

Drill-Down can temporarily restrict this same selected-path evidence to one centered `1h`, `3h`, `6h`, `12h` or `24h` interval before ordinary table filters run. Its focused metric recipe retains one scientific unit at its native coordinate: one consolidated Joint Spot and actual ΔSNR at canonical cycle UTC for Benchmark; or one successful confirmed opportunity and actual normalized Target SNR at canonical cycle UTC for Performance. Thus “native” describes processed retained evidence after consolidation, matching and scientific filters, not untouched provider rows. The focused metric recipe contains neither temporal-bin medians or quartiles nor a density grid, colorbar, full-run median or folded profile. Companion outcome/coverage panels may retain their chronological aggregation, and the segment and full-window selected-path recipes remain unchanged density summaries.

Candidate-linked **`Outlier Focus`** uses the full retained pre-event flank, guarded provisional episode and post-event flank and may exceed 24 hours. The Benchmark overlay uses the already completed detector model rather than redetecting from the focused subset.

For every reported candidate intersecting the focus window, it marks with the same `*` each native unit that individually meets both $D_{\min}$ and $Z_{\min}$ against that candidate's final baseline and robust spread; weaker grouped units retained between strong anchors remain ordinary dots.

A muted **Focused episode** band distinguishes the selected candidate's reported retained-evidence interval. The renderer pads each end by half one native evidence-unit width and clips the band to the focused window, making a one-unit impulse visible without representing unobserved physical duration or a confidence interval.

Expected local ΔSNR across the focus, the pre/post flank medians over their respective support intervals, symmetric guide boundaries for robust-z magnitudes 1, 2, 3 and $Z_{\min}$, and the absolute-departure boundary $D_{\min}$ all belong only to that focused episode; another starred candidate can have a different baseline and robust spread. From the detector definition in [Section 7.11](#sec-7-11), a guide of magnitude `k` lies at the local baseline plus or minus `k × robust spread / 0.6745`. These guides visualize detector coordinates; they are not standard deviations, confidence intervals or independent qualification tests, and crossing one guide alone is insufficient to qualify a candidate.

Focus selection and candidate provenance are presentation state only; they do not alter the completed analysis context, matching, eligibility or detector results, the provider query, saved configuration or public URL.

<a id="sec-7-8-5"></a>
##### 7.8.5 Descriptive spread and visualization transforms

An IQR shows the middle half of the contributing values; min–max shows their full range. These are descriptive spread summaries, not confidence intervals. Temporal IQR bands require at least five contributing values in the relevant bin; the median remains available with fewer values. Empty bins remain missing rather than becoming synthetic zero observations.

The contributing value depends on the view: it can be a Joint Spot, an individual successful normalized Target-SNR observation, a peer-bin median or a peer-date-hour median as defined above. Performance distance profiles use the separate three-peer rule in [Section 7.8.1](#sec-7-8-1).

**Reading density and axis spacing.** Density color identifies where values accumulate within one panel; support counts give the evidence volume. Benchmark axes may compress the tails, so use the labelled dB coordinates rather than judging a difference from its visual height. The exact transformations below change the display, not the retained observations or their medians and quartiles.

**Density cells and correction.**

Benchmark histograms normally use 1 dB bins, use 0.5 dB only for a clear half-dB lattice, and coarsen broad ranges to keep the number of bins bounded. Benchmark temporal density cells remain 1 dB high and follow the applied Reference SNR correction. For corrected ΔSNR `d` and numerical correction `c`, the ideal membership rule in the uncorrected comparison coordinate is `k = floor(d + c + 0.5)`; the numerical convention below evaluates this coordinate at 0.1 dB resolution. Cell `k` is centered at `k - c` and covers the half-open interval `[k - 0.5 - c, k + 0.5 - c)`: its lower boundary belongs to the cell, its upper boundary to the next cell, also for negative values. Adding `c` for membership is only a coordinate transformation; it does not apply the correction again to the stored observations, medians or quartiles. For the same retained population, changing `c` translates the density grid together with the corrected observations while retaining cell counts and relative-density colors. Fractional observations, including Local Median comparisons, need not lie at cell centers.

**Numerical cell assignment.** For membership only, `d + c` is rounded to the nearest tenth of a decibel before assigning its integer cell ID; exact half-tenth ties choose the even tenth. A float64 roundoff guard only at these rounding midpoints prevents correction noise from choosing opposite tenths. This explicitly limits membership resolution to 0.1 dB and absorbs numerical noise such as `-0.7000000000000028` in a corrected value expected at `-0.7 dB`; distinctions smaller than that membership resolution can share a cell. Exact half-dB coordinates at that resolution enter the upper cell, including negative values. The original corrected observations and their statistics are not rounded by this grid policy. A full-precision fractional observation can consequently lie up to 0.05 dB beyond its assigned cell edge; axis coverage still includes the observation itself. This temporal presentation policy replaces ties-to-even integer rounding, so exact half-dB assignments can change even with zero correction. It does not change ordinary histograms, Performance views or native-point Drill-Down plots. Each density panel is normalized independently:

$$D_{relative}=100\times\frac{n_{cell}}{\max(n_{cell,panel})}$$

Here $n_{cell}$ is the evidence count in one density cell. Dividing by the most populated cell converts the panel to a relative-density display while leaving the underlying counts unchanged.

Thus `100` means the most populated cell in that panel, not 100% of all evidence. Density colors cannot compare absolute evidence volume between independently normalized panels; support counts provide that information.

**Median-centered axis.** Benchmark temporal and histogram views use a presentation-only monotonic scale centered on the scope median $M$. For a broad range, equal visual steps are anchored at $M$, $M\pm3$, $M\pm6$, $M\pm10$, $M\pm20$ and $M\pm30$ dB, with a tail anchor at $M\pm60$ dB and extrapolation when required. When every required deviation is at most `10 dB`, the tighter anchors are $M$, $M\pm1$, $M\pm3$, $M\pm6$ and $M\pm10$ dB, with continuation anchors at $M\pm20$ and $M\pm40$ dB. The required range includes the applicable raw histogram or correction-shifted temporal cell edges, a minimum `3 dB` half-span and absolute `0 dB`, so Target–Reference equality remains visible. The anchor mapping changes displayed spacing only: raw ΔSNR values, bin membership, counts, medians and quartiles remain unchanged. Because the vertical mapping is nonlinear, histogram bar **length** against its percentage axis — not displayed area — is the quantitative encoding.

Performance successful-SNR views remain on a linear dB axis.
````

</details>


### 7.9 Geography, solar classification and population filters

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-9"></a>
#### 7.9 Geography, solar classification and population filters

Distance and azimuth are calculated from the configured Target QTH and reported peer locators using a spherical Earth radius of 6371 km. The map uses an azimuthal equidistant projection centered on Target QTH, with radial boundaries at 2500, 5000, 10000, 15000, 20000 and 22000 km and 22.5-degree azimuth sectors.

Reported locators represent grid cells rather than measured antenna coordinates. Geographic summaries are internally consistent with those inputs but should not be interpreted as survey-grade position or direct take-off-angle measurement.

`Maximum peer distance from Target (km)` removes peers at or beyond the selected distance before scientific aggregation and processed-evidence export. Map segments, support counts, Segment Inspector and exports therefore use one retained peer population. Inspector selections can narrow that population but cannot restore excluded rows.

Two rules precede the geographic scope:

* Target-active conditioning remains global, so an out-of-scope peer can prove Target operation without becoming a scoped outcome.
* When moving-station exclusion is enabled, changing-location callsigns are identified in the otherwise eligible global population before distance scope is applied.

Solar classification uses solar elevation at Target QTH. Same-cycle evidence uses the cycle timestamp.

It labels conditions at the Target, not illumination along the whole propagation path or at every remote endpoint.

The database row limit and the controls that can reduce the retrieved source population are operational matters documented in [Section 5.6](#sec-6-6); they do not change the scientific summaries after the retained population has been formed.
````

</details>


### 7.10 Dependence, uncertainty and validation scope

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-10"></a>
#### 7.10 Dependence, uncertainty and validation scope

The calculations above can be exact for the retained evidence while a future result or physical explanation remains uncertain. This is the distinction between describing this run and generalizing beyond it.

WSPRadar observations are clustered rather than independent. In ordinary station terms, 1,000 spots are not the same as 1,000 unrelated experiments. Repeated cycles from one peer share hardware and path characteristics; stations in nearby regions share propagation; time bins are autocorrelated; and one ionospheric or interference event can affect many observations simultaneously. A large row count is therefore not an independent sample size. Likewise, the aligned Type 2 and Type 3 phases of one extended-WSPR sequence provide additional within-run evidence units, not independent experimental repetitions. Experimental repeatability requires a separate suitably controlled run.

Station balancing reduces domination by prolific peers, and medians reduce sensitivity to isolated outliers. Neither creates independence, removes systematic bias nor supplies a sampling distribution. IQRs describe within-run spread and are not uncertainty intervals.

WSPRadar currently reports descriptive summaries of retained evidence. It does not automatically calculate standard errors, confidence intervals, p-values, statistical power or causal effects. The summaries can be exact for the retained evidence while uncertainty about a wider population or future run remains unresolved. Naive inferential calculations that treat every spot or pair as independent would generally understate that uncertainty.

Scientific support should therefore be described at several levels:

* **evidence depth:** number of opportunities, Joint units;
* **evidence breadth:** number and geographic diversity of peer identities;
* **within-run consistency:** agreement across station-balanced, observation-level, geographic and temporal summaries;
* **experimental repeatability:** recurrence in a new suitably controlled run; and
* **experimental control:** calibration, crossover, reversed schedule or independent measurement appropriate to the claim.

These levels show the support for a bounded description or comparison; they do not turn the summaries into calibrated predictions. Agreement across several views of the same run is useful internal consistency, but it is not independent replication. For stronger claims, the separate controlled run and experiment design remain essential; [Chapter 8](#sec-8) gives reporting language.

Empirical software-validation audits are not timeless method definitions. Any reported validation statistic should identify its datasets, date, WSPRadar version or source revision, and calculation method. Without that provenance it should be removed from the normative manual or labelled explicitly as a dated validation check.
````

</details>


### 7.11 Robust local-baseline ΔSNR event detection

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-11"></a>
#### 7.11 Robust local-baseline ΔSNR event detection

The detector's analysis target is a temporary same-sign departure in one path's paired ΔSNR from a stable local expected value. It is not a ranking of the largest raw values and does not estimate an event probability. [Section 2.5](#sec-outlier) explains when and how an operator should use the diagnostic; this section defines the exact scientific construction.

The construction has three jobs: establish the usual local difference before and after a candidate, find a temporary departure without letting it redefine that baseline, and report only an interval that passes all evidence checks. **Residual** means departure from that local baseline; **robust scale** measures nearby variation; **robust z-score** expresses the departure relative to that variation. A large raw ΔSNR can be entirely usual for a path, while a value close to zero can be a substantial local change.

The notation is local to this section except for the three control symbols already introduced in [Section 4.6](#sec-5-6): $D_{\min}$ is **`Minimum absolute ΔSNR departure (dB)`**, $Z_{\min}$ is **`Minimum robust z-score`**, and $H_{\max}$ is **`Maximum pre/post baseline difference (dB)`**. No notation elsewhere in Chapter 7 is redefined.

| Symbol | English mnemonic and meaning in this section |
|---|---|
| $i$ | one exact peer `callsign + locator` path identity |
| $u$ | one native paired unit: a same-cycle Joint Spot |
| $k$ | one UTC-aligned 10-minute baseline-cell index |
| $D_{i,u}$ | corrected paired Target-minus-Reference ΔSNR for unit $u$, following Section 7.5 |
| $\widetilde D_{i,k}$ | median ΔSNR in populated baseline cell $k$ |
| $\mathcal{B}_{\mathrm{pre}},\mathcal{B}_{\mathrm{post}}$ | retained pre-event and post-event Baseline evidence values |
| $B_{\mathrm{pre}},B_{\mathrm{post}},B$ | pre-event, post-event and final local Baseline |
| $B^P_{i,k}$ | Pilot Baseline for path $i$ and cell $k$ |
| $r^P_{i,u},r_{i,u}$ | Pilot and final Residual for native unit $u$ |
| $\mathcal{V},S_{\mathrm{robust}}$ | centred flank Variability sample and robust local Scale |
| $z_{i,u}$ | robust z-score of one native paired unit |
| $C_i,G_i,F$ | typical path Cadence, maximum internal Gap and provisional grouping Floor |
| $W_i^P,W_i^B$ | Pilot- and final-Baseline exclusion Widths |
| $E,m_E,z_E,\operatorname{agree}(E)$ | candidate Event, its Median residual, event robust z-score and sign-agreement fraction |
| $\varepsilon$ | fixed `0.01 dB` comparison tolerance for the minimum-departure and maximum-baseline-difference gates |

The detector applies $\varepsilon=0.01\ \mathrm{dB}$ only when comparing an absolute departure with $D_{\min}$ or a pre/post baseline difference with $H_{\max}$. It does not round internal evidence values or configured thresholds. The same tolerance applies to event qualification, strong boundary anchors and individually qualifying native units. Robust z-scores, MAD/IQR scale estimation and sign-agreement rules remain unchanged; the robust-z comparison receives no tolerance.

**1. Evidence and resolution.** Only native paired units supply detector ΔSNR. One-sided outcomes have no paired value and cannot qualify an event, although their times contribute to cadence estimation and the outcomes remain diagnostic context. Detection runs independently for each path $i$ before Temporal Evidence display aggregation. Changing a display bin cannot create, merge, split or remove an event. When **`Report ΔSNR outlier candidates`** is off, the detector is not run and no outlier semantics are added to the result.

Native values are reduced to $\widetilde D_{i,k}$ for baseline and robust-scale estimation. Candidate grouping and reported boundaries retain the native paired-unit times.

**2. Stable local baseline and robust variability.** For the candidate under evaluation, the detector examines populated 10-minute cells up to six hours before and six hours after it. The candidate and its exclusion width are omitted. Each flank must contain at least four populated cells; missing cells are never imputed. The retained cell values form $\mathcal{B}_{\mathrm{pre}}$ and $\mathcal{B}_{\mathrm{post}}$:

$$
B_{\mathrm{pre}}=\operatorname{median}(\mathcal{B}_{\mathrm{pre}}),\qquad
B_{\mathrm{post}}=\operatorname{median}(\mathcal{B}_{\mathrm{post}})
$$

The final expected local ΔSNR gives the two flanks equal weight, while the stability gate limits their disagreement:

$$
B=\frac{B_{\mathrm{pre}}+B_{\mathrm{post}}}{2},\qquad
\left|B_{\mathrm{pre}}-B_{\mathrm{post}}\right|\leq H_{\max}+\varepsilon
$$

Equal flank weighting prevents the side with more populated cells from dominating. If either flank lacks support or the stability gate fails, the path remains unclassified for that candidate and no event is reported.

To measure nearby variability without treating a baseline shift as noise, each flank is centred on its own baseline. The braces and union below denote pooled evidence samples with repeated values retained: every retained cell residual contributes, even when another cell has the same value:

$$
\mathcal{V}=\left\{x-B_{\mathrm{pre}}:x\in\mathcal{B}_{\mathrm{pre}}\right\}
\cup\left\{x-B_{\mathrm{post}}:x\in\mathcal{B}_{\mathrm{post}}\right\}
$$

The scale records typical absolute variation in the centred flank values, in dB. The detector first uses their median absolute deviation (MAD); if it is zero, it uses half their interquartile range (IQR), and only if both are zero does it use a fixed replacement:

$$
S_{\mathrm{robust}}=
\begin{cases}
\operatorname{MAD}(\mathcal{V}), & \operatorname{MAD}(\mathcal{V})>0,\\
\frac{1}{2}\operatorname{IQR}(\mathcal{V}), & \operatorname{MAD}(\mathcal{V})=0\ \land\ \operatorname{IQR}(\mathcal{V})>0,\\
0.5\ \mathrm{dB}, & \operatorname{MAD}(\mathcal{V})=0\ \land\ \operatorname{IQR}(\mathcal{V})=0.
\end{cases}
$$

MAD is the median of the absolute distances from the sample median; IQR is the gap between its 25th and 75th percentiles. The `0.5 dB` replacement prevents division by zero when both measures vanish; positive MAD or half-IQR values smaller than `0.5 dB` are retained. Subtracting the baseline gives a residual in dB; dividing by the robust scale and applying the conventional factor gives a dimensionless score:

$$
r_{i,u}=D_{i,u}-B,\qquad
z_{i,u}=0.6745\frac{r_{i,u}}{S_{\mathrm{robust}}}
$$

A positive residual is above the expected local Target-minus-Reference ΔSNR and a negative residual is below it; this residual sign, not the sign of raw $D_{i,u}$ relative to `0 dB`, drives grouping and qualification. The factor `0.6745` supplies conventional modified-score scaling when MAD is active. The score remains descriptive rather than a calibrated probability, p-value or Gaussian significance level.

**Example: positive ΔSNR, negative departure.** If the stable local baseline is `+8 dB` and a Joint Spot has `+1 dB`, its residual is `-7 dB`. The Target is still stronger than the Reference in that spot, but much less so than usual for this path. With robust scale `1 dB`, its robust z-score is about `-4.72`. This calculation alone does not report an event: flank support, baseline stability, event-level gates, sign agreement and retained boundary anchors must also pass.

**3. Cadence-aware pilot grouping.** The typical path cadence $C_i$ is estimated in minutes from unique eligible paired and one-sided outcome times. Positive intervals no longer than 45 minutes are retained, and their median defines the cadence when at least two remain; otherwise the configured paired-unit cadence supplies $C_i$. The maximum internal gap is:

$$G_i=\min\left(45,\max\left(15,1.5C_i\right)\right)\ \mathrm{minutes}$$

Thus sparse paths receive a cadence-aware grouping allowance, but no event can bridge more than 45 minutes and no estimated cadence reduces the allowance below 15 minutes.

To seed candidates without allowing the point under test to define its own expected value, each supported cell receives a Pilot Baseline $B^P_{i,k}$. Its exclusion width and the permissive grouping Floor are:

$$
W_i^P=\max(60,2C_i)\ \mathrm{minutes},\qquad
F=\min(1\ \mathrm{dB},D_{\min}-\varepsilon)
$$

The `1 dB` term remains exact: the tolerance enters this early grouping rule only through the tolerated minimum departure, so grouping cannot impose a stricter departure requirement than final qualification. It is not subtracted from the fixed `1 dB` term or from the `1 dB` shoulder-expansion criterion below.

The pilot fit uses the same six-hour flank reach, four-populated-cell minimum on each side and $H_{\max}$ stability gate. A native unit $u$ in cell $k(u)$ receives a pilot residual only when that cell has supported flanks:

$$r^P_{i,u}=D_{i,u}-B^P_{i,k(u)}$$

Nearby pilot residuals of the same sign and magnitude at least $F$ form a provisional event. Grouping stops at a gap greater than $G_i$, an opposite-sign member or a supported return to baseline. One supported neutral unit may bridge the evidence when the same-sign departure resumes; a second consecutive supported neutral unit ends the event. Unsupported units remain unclassified and are not imputed. The low Floor finds continuity; it does not relax final qualification.

**4. Candidate-excluded final baseline.** The complete provisional event is excluded from the final baseline fit with width:

$$W_i^B=\max(10,C_i)\ \mathrm{minutes}$$

The final fit uses the baseline and robust-scale construction in Step 2. Against that shared final baseline, same-sign shoulders with residual magnitude at least `1 dB` may expand the event for up to three passes. The complete expanded interval remains excluded at every refit, preventing the candidate from pulling its own expected value toward the excursion.

**5. Qualification, strong-core rescue and reported boundaries.** For one refined candidate Event $E$, define its Median residual, event robust z-score and sign-agreement fraction as:

$$
m_E=\operatorname{median}_{u\in E}(r_{i,u}),\qquad
z_E=0.6745\frac{m_E}{S_{\mathrm{robust}}}
$$

$$
\operatorname{agree}(E)=
\frac{\left|\left\{u\in E:\operatorname{sign}(r_{i,u})=\operatorname{sign}(m_E)\right\}\right|}{|E|}
$$

The event median describes its typical departure rather than its single largest point. The sign-agreement denominator is every retained native unit in that candidate, including any neutral bridge. At least two thirds must share the median residual's sign. Qualification then requires all four conditions together: enough departure in dB, enough departure relative to local variation, compatible pre/post baselines, and sufficient sign agreement:

$$
|m_E|\geq D_{\min}-\varepsilon,\qquad
|z_E|\geq Z_{\min},\qquad
\left|B_{\mathrm{pre}}-B_{\mathrm{post}}\right|\leq H_{\max}+\varepsilon,\qquad
\operatorname{agree}(E)\geq\frac{2}{3}
$$

Every duration and eventual class uses these same gates. There is no duration bonus, accumulated-evidence discount or weaker threshold for a sustained event.

If the complete refined event cannot yield a qualifying strongly anchored interval, it is split at final-baseline returns into contiguous same-sign sections without neutral bridging. Each section is tested against the same gates while reusing the complete candidate's final baseline, robust scale and flank support. This can rescue a strong core suppressed by weak surroundings without allowing the smaller section to select a more favorable reference.

After qualification, a native unit is a strong boundary anchor only when:

$$
\operatorname{sign}(r_{i,u})=\operatorname{sign}(m_E),\qquad
|r_{i,u}|\geq D_{\min}-\varepsilon,\qquad
|z_{i,u}|\geq Z_{\min}
$$

The reported interval is trimmed to the first and last strong anchors. Units already grouped between them remain internal evidence even when they individually miss an anchor threshold. The trimmed interval is rebuilt and retested against every event-level gate using the same final baseline, robust scale and flank support. Weak leading and trailing units are removed; weaker internal bridges can remain. One surviving anchor becomes a Spot impulse. If no strongly anchored interval passes, no event is reported. The lower grouping Floor and higher boundary requirements therefore produce hysteretic event boundaries.

In practical terms, weak points may preserve continuity inside an event, but only individually strong points can define its reported start and end.

The all-path temporal marker is selected only from these strong anchors: within each cross-path review event, the individually qualifying native unit with the greatest absolute residual supplies the `*`. An unsupported or nonqualifying episode peak cannot become that plot representative. Marker selection is separate from **Largest single-cycle departure**, which remains the true greatest-absolute retained residual in each path event for the report and export.

**6. Descriptive class and cross-path context.** Classification occurs after trimming:

* **Spot impulse:** one retained native paired unit;
* **Sustained excursion:** at least three retained native paired units spanning at least 30 minutes; and
* **Short burst:** every other retained multi-unit event.

The classes describe temporal evidence shape and do not change qualification. The displayed first-to-last interval spans observed retained units; it does not establish uninterrupted behavior between them.

Path events qualify independently. Same-sign events are placed in one review card when they overlap or lie within the greater of 10 minutes and half the configured paired-unit cadence. Context is path-specific for one path, directionally coherent for several paths in adjacent compass sectors, scope-wide for several separated directions, or multiple paths when direction is unavailable for at least one contributor. Cross-path context does not alter path qualification and is not an independence or significance calculation.

Target/Reference decomposition and nearby one-sided outcomes are retained as internal diagnostics and can be investigated through the paired evidence and Drill-Down. They do not qualify, extend or strengthen an event. The detector is therefore a deterministic descriptive classifier of the retained paired evidence. Its event count is not an independent sample size, it performs no multiple-event significance correction, and causal attribution still requires the experiment control described in Chapters 2, 3 and 8.
````

</details>

- `docs/doc_de.py` Git-blob SHA-256: `2e4f34f4ad927b2dbda7a711e30436772d398139410a13a83b5229ce622b58f6`


## DE: verbatim baseline passages

The complete original sections are retained below. This includes all superseded prose and mathematical representations, so removed or consolidated wording remains traceable without adding a formal specification to the end-user manual. Each section is accounted for by the disposition review.


### 7. Wissenschaftliche Methoden

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7"></a>
### 7. Wissenschaftliche Methoden

Benchmark vergleicht das SNR von Joint Spots: Wie unterschieden sich das gemeldete Target- und Referenz-SNR für denselben qualifizierenden Peer-Zyklus? Performance zählt bestätigte Gelegenheiten: Wie oft war das Target erfolgreich, wenn die erforderliche Aktivität beobachtbar war? Beide Fragen hängen davon ab, welche Peers und Zyklen in die Rechnung eingehen.

Dieses Kapitel definiert diese wissenschaftlichen Regeln. WSPRadar beginnt mit gemeldeten Beobachtungen, bildet daraus zulässige Evidenzeinheiten, leitet Größen wie normiertes SNR und gepaartes ΔSNR ab und berechnet anschließend deskriptive Zusammenfassungen. Diese Werte sind für die Evidenz exakt, die nach den ausgewählten Regeln beibehalten wurde. Sie sind nicht automatisch Aussagen über alle möglichen Stationen, künftige Betriebsbedingungen oder eine isolierte physikalische Eigenschaft der Station.

Die Übertragung auf eine breitere oder künftige Population erfordert ein zusätzliches Modell für Stichprobenauswahl und Abhängigkeiten; WSPRadar nimmt diesen Inferenzschritt nicht automatisch vor.

Hilfreich ist die Unterscheidung von fünf Ebenen:

1. **Gemeldete Beobachtungen:** hochgeladene WSPR-Spots mit Rufzeichen, Locator, Leistung, Zeit und SNR.
2. **Gebildete Evidenzeinheiten:** qualifizierende Gelegenheiten, Peer-Zyklen, Joint-Einheiten, die nach den Zulässigkeits- und Zuordnungsregeln von WSPRadar entstehen.
3. **Abgeleitete Größen:** normiertes SNR, Decode Outcomes und Target-minus-Referenz-ΔSNR einer einzelnen Evidenzeinheit.
4. **Deskriptive Zusammenfassungen:** Raten, Mediane, Reichweite, Evidenzanteile sowie zeitliche und geografische Zusammenfassungen der beibehaltenen Evidenz.
5. **Interpretation über den Lauf hinaus:** Aussagen über künftiges Verhalten, eine breitere Population oder eine physische Ursache. Solche Verallgemeinerungen benötigen zusätzliche Annahmen und experimentelle Kontrolle; die reine Berechnung genügt dafür nicht.

**Methodischer Überblick**

| Design | Kleinste Vergleichseinheit | Konditionierung / Zulässigkeit | Hauptzusammenfassung | Wichtigste Grenze |
|---|---|---|---|---|
| RX Referenzaufbau/-station | ein Peer-Zyklus eines entfernten Senders | Target aktiv; beide Empfänger melden denselben Sender-Zyklus für ΔSNR | Stationsmedian des ΔSNR, danach Median über Stationen | vollständige Empfangspfade, sofern Ketten nicht kontrolliert sind |
| TX Referenzaufbau/-station | ein Peer-Zyklus eines entfernten Empfängers | Target aktiv; derselbe Empfänger-Zyklus für gepaartes ΔSNR | Stationsmedian des ΔSNR, danach Median über Stationen | Leistung, Kettenunterschiede und Auswahl nach Joint-Decode |
| Referenznachbarschaft (Lokaler Median) | ein Target-/lokaler-Referenz-Peer-Zyklus | Target aktiv; ein Beitrag je aktiver lokaler Identität | lokaler Median als Referenz, danach Stations- und Segmentmediane des ΔSNR | wechselnde, unkalibrierte Zusammensetzung |
| RX Performance | ein Peer-Zyklus eines entfernten Senders | Target-RX aktiv; Peer-TX vom Target-RX oder einem anderen geeigneten RX decodiert | Peer-Dekodierrate, danach Mittel mit gleicher Peer-Gewichtung; gepoolte Gelegenheitsrate bleibt erhalten | bedingte Beobachtbarkeit, keine kalibrierte Empfindlichkeit |
| TX Performance | ein Peer-Zyklus eines entfernten Empfängers | Target-TX aktiv; Peer-RX decodiert Target-TX oder einen anderen qualifizierenden TX auf demselben Band | Peer-Dekodierrate, danach Mittel mit gleicher Peer-Gewichtung; gepoolte Gelegenheitsrate bleibt erhalten | bedingte Beobachtbarkeit, nicht alle Sendeversuche |

Die Hierarchie lässt sich von links nach rechts lesen: WSPRadar entscheidet zuerst, welche Evidenzeinheiten zur Analyse gehören, berechnet danach eine Größe auf Peer- oder Funkwegebene und bildet erst dann die angezeigte stationsgleichgewichtete Zusammenfassung. Die folgenden Formeln machen diese Schritte prüfbar; der Text nach jeder Formel erklärt dieselbe Berechnung in Funkpraxis-Sprache.

**Verwendete Notation**

| Symbol | Bedeutung |
|---|---|
| $i$ | eine Peer-<strong class="defined-term">Identität</strong>, definiert als exaktes `Rufzeichen + gemeldeter Locator` |
| $c$ | ein zulässiger WSPR-<strong class="defined-term">Zyklus</strong> |
| $g$ | ein beibehaltener <strong class="defined-term">geografischer</strong> Bereich oder ein Segment |
| $b$ | ein Entfernungs- oder Zeit-<strong class="defined-term">Bin</strong> |
| $S_{i,c}$ | Target-<strong class="defined-term">Erfolgs</strong>indikator innerhalb einer zulässigen Performance-Gelegenheit |
| $O_{i,c}$ | Performance-<strong class="defined-term">Gelegenheits</strong>indikator nach Aktivitäts-, Identitäts- und Populationsregeln |
| $D_{i,c}$ | gepaartes Target-minus-Referenz-<strong class="defined-term">Delta</strong>-SNR, wenn beide Seiten beobachtet wurden |
| $T_{i,b},J_{i,b},R_{i,b}$ | Anzahlen Only <strong class="defined-term">Target</strong>, <strong class="defined-term">Joint</strong> und Only <strong class="defined-term">Reference</strong> im Benchmark-Bereich $b$ |

Ein Indikator ist `1`, wenn seine Bedingung erfüllt ist, und sonst `0`. Die Notation macht Nenner und Gewichtung eindeutig; der Text nach jeder Formel erklärt dieselbe Berechnung in Funkpraxis-Sprache.

Die Indizes kennzeichnen, wessen Evidenz gezählt wird und zu welchem Bereich sie gehört. Eine Summe zählt beibehaltene Einheiten zusammen; der Median ist der mittlere sortierte Wert, bei gerader Anzahl das Mittel der beiden mittleren Werte. Diese Rechenschritte setzen nicht voraus, dass die Beobachtungen unabhängig sind.

Dieses Kapitel verwendet **Zusammenfassung** oder **deskriptive Kennzahl** für die Raten, Mediane, Anteile und Verteilungen der beibehaltenen Evidenz. Die Unterscheidung ist wichtig, weil ein Wert für die beibehaltenen Zeilen exakt berechnet sein und dennoch nur eine enge oder ausgewählte Population beschreiben kann.
````

</details>


### 7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-1"></a>
#### 7.1 Datenquelle, Beobachtungseinheiten und Zeitmodell

WSPRadar liest öffentliche WSPR-Meldungen für jeden abgeschlossenen Lauf aus genau einer ausgewählten Datenbank über schreibgeschützte Abfragen. Die Meldungen sind Beobachtungsdaten heterogener Sender, Empfänger, Decoder und Meldesysteme. Ein abgeschlossener Lauf mischt keine Datenquellen; die ausgewählte Datenbank gehört zur Provenienz des Laufs.

Ein **Spot** ist eine gemeldete Zeile eines erfolgreichen Decodes. Ein **WSPR-Zyklus** ist das zweiminütige Intervall, das an einer geraden UTC-Minute beginnt. Analysen im selben Zyklus konsolidieren qualifizierende Zeilen zunächst nach Seite, Peer-Identität und Zyklus und klassifizieren sie erst danach. Die in den Bedienelementen angezeigten effektiven UTC-Grenzen definieren das Analysefenster.

WSPR-2 bezeichnet den zweiminütigen Sendemodus; Typ 1, Typ 2 und Typ 3 beschreiben die Nachrichteninhalte. Erweitertes WSPR kann ein zusammengesetztes Rufzeichen und einen präzisen sechsstelligen Locator über zwei sich ergänzende Aussendungen übertragen. Eine Typ-2-Nachricht überträgt das zusammengesetzte Rufzeichen und die Leistung, jedoch keinen Locator; die zugehörige Typ-3-Nachricht überträgt einen 15-Bit-Hash dieses Rufzeichens, den sechsstelligen Locator und die Leistung. Die beiden Aussendungen liegen in getrennten WSPR-Zyklen; sie sind nicht zwei Felder einer einzigen Datenbankzeile <a href="#ref-12">[Ref-12]</a>.

WSPRadar klassifiziert eine Zeile nicht als Typ 1, Typ 2 oder Typ 3 und verbindet keine sich ergänzenden erweiterten WSPR-Aussendungen über Zyklusgrenzen hinweg. Jede Datenbankzeile gehört zu ihrem gemeldeten Zyklus.

WSPRadar verlangt nicht beide sich ergänzenden Nachrichtenphasen, bevor es eine Einheit desselben Zyklus zulässt; die für den jeweiligen Vergleich benötigten Identitäten müssen in der Datenbank aufgelöst sein. Beim TX-Benchmark müssen die aufgelösten Target- und Referenzzeilen im selben Zyklus von derselben entfernten Empfängeridentität stammen. Übereinstimmende Nachrichtentypen sind keine Zulässigkeitsbedingung: Die gespeicherten Zeilen müssen die geltenden Identitäts-, Zyklus- und Filterregeln erfüllen. WSPRadar verbindet niemals Meldungen aus verschiedenen WSPR-Zyklen zu einem Paar.

Eine erweiterte Folge kann deshalb in einem oder beiden Zyklen Joint Spots beitragen. Ein qualifizierender Joint Spot in einem Zyklus setzt keinen Joint Spot im anderen voraus. Die Empfehlung, bei einem kontrollierten TX-Versuch Nachrichtentypen und Sendezeitpläne aufeinander abzustimmen, verbessert die Vergleichbarkeit der Beobachtungen; sie ist eine Betriebsempfehlung und keine von WSPRadar durchgeführte Nachrichtentypprüfung. [Abschnitt 2.2.1](#sec-3-tx-benchmark-simultaneous) erklärt den praktischen Aufbau.

Die kleinste Evidenzeinheit hängt vom Design ab:

* Performance und Benchmark verwenden eine Peer-Identität in einem zulässigen WSPR-Zyklus.
* Die Referenznachbarschaft bildet zusätzlich zunächst für jeden Zyklus und Funkweg eine Referenz aus qualifizierenden lokalen Identitäten, bevor Target-minus-Referenz-Evidenz entsteht.

Die Zuordnung desselben Zyklus bedeutet denselben zweiminütigen gemeldeten UTC-Slot und dasselbe entfernte Rufzeichen mit vollständigem gemeldeten Locator im selben Band. Sie verlangt keine identischen HF-Frequenzen und beweist keine gleichen physischen Ausbreitungswege; simultane TX-Signale benötigen normalerweise getrennte freie Frequenzen. Nur Joint Spots liefern ΔSNR. Einseitige Evidenz und Both (Async) auf Stationsebene bleiben ohne erfundenes SNR der fehlenden Seite erhalten.

Diese Einheiten werden aus gemeldeten Spots gebildet; sie sind keine zusätzlichen Funkmessungen. Ihr Zweck ist, eindeutig festzulegen, unter welchen Bedingungen ein Erfolg, ein verpasster Decode oder eine gepaarte Differenz gezählt wird.

Der historische Fallback ohne `code = 1` verändert die Auswahl der Quellzeilen nur, wenn die strenge Abfrage keine Target-seitige Evidenz liefert und der gesamte gewählte Zeitraum vor dem 1. Januar 2022 um 00:00 UTC endet. Der Laufstatus dokumentiert den verwendeten Abfrageweg. Die Zulässigkeitsgrenze und die Unsicherheit historischer Modusangaben stehen in [Abschnitt 5.4](#sec-6-4). Verzögerungen und Datenqualitätsgrenzen der Upstream-Quellen stehen in [Abschnitt 5.6](#sec-6-6).
````

</details>


### 7.2 Identität, Zuordnung und Zeilenkonsolidierung

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-2"></a>
#### 7.2 Identität, Zuordnung und Zeilenkonsolidierung

WSPRadar behandelt gemeldete Identitäten als wissenschaftliche Daten und nicht als bloße Beschriftung.

**Die grundlegende Beobachtung betrifft eine entfernte Station in einem zweiminütigen WSPR-Zyklus.** Die entfernte Station ist bei RX ein Sender und bei TX ein Empfänger. Benchmark vergleicht die Target- und Referenzevidenz für diese entfernte Station innerhalb desselben Zyklus.

Performance und Benchmark behalten nur Zyklen mit beobachtbarer Target-Aktivität bei. Diese Aktivität muss nicht auf jedem einzelnen Funkweg zur entfernten Station beobachtet werden: Evidenz auf einem anderen Funkweg kann belegen, dass das Target im Zyklus aktiv war. [Abschnitt 7.3](#sec-7-3) definiert die Aktivitätsprüfungen und ihre Unterschiede zwischen den Analysen.

Stationsidentitäten werden wie folgt ausgewählt:

| Station oder Rolle | Identifizierung durch WSPRadar |
|---|---|
| **Target — alle Analysen** | Exaktes Empfangsrufzeichen bei RX oder Senderufzeichen bei TX zusammen mit dem vierstelligen Locator des Target-QTH. |
| **Referenz — Referenzaufbau/-station** | Exaktes Referenzrufzeichen zusammen mit seinem aus der Datenbank aufgelösten vierstelligen Locator. |
| **Entfernte Station — alle Analysen** | Exaktes Rufzeichen zusammen mit dem vollständigen gemeldeten Locator: der entfernte Sender bei RX oder der entfernte Empfänger bei TX. |
| **Lokale Beiträge — Referenznachbarschaft** | Lokale Empfängeridentitäten bei RX oder lokale Senderidentitäten bei TX innerhalb des gewählten Radius, unterschieden anhand des exakten Rufzeichens und vollständigen gemeldeten Locators. |

Performance wertet die Beobachtungen und bestätigten Gelegenheiten des Targets für jede entfernte Station und jeden Zyklus aus. Referenzaufbau/-station vergleicht das Target mit einer identifizierten Referenz. Die Referenznachbarschaft bildet ihre Referenz für jede entfernte Station und jeden Zyklus getrennt aus den qualifizierenden lokalen Beiträgen.

Mehrere qualifizierende Meldungen für dieselbe Seite, entfernte Station und denselben Zyklus werden vor der Ergebnisbildung zusammengefasst. So bleibt für diese Seite in diesem Zyklus ein Wert erhalten; Meldungen aufeinanderfolgender Zyklen werden dabei nicht verbunden. Die Regeln zur stärksten Meldung und zum Nachbarschafts-Median werden nachfolgend erklärt.

Für die Auswahl der Target-Zeilen in der Datenbank verwendet WSPRadar Grid-4, auch wenn ein sechsstelliges QTH konfiguriert ist. Das vollständige QTH bleibt für Entfernung, Azimut, Sonnenhöhe und die Geometrie des lokalen Radius relevant. Ein gemeinsames Grid-4 belegt keine physische Ko-Lokation.

Diese Zuordnung verwendet die exakten Rufzeichen- und Locatorfelder der ausgewählten Datenbank. WSPRadar rekonstruiert weder ein zusammengesetztes Rufzeichen aus seinem Hash noch übernimmt es einen Locator aus einem benachbarten Typ-2- oder Typ-3-Zyklus. Eine simultane erweiterte WSPR-Folge kann deshalb in jedem zulässigen Zyklus eine Vergleichseinheit desselben Zyklus je entfernter Empfängeridentität beitragen, wenn beide Seiten in der Datenbank konsistent aufgelöst sind. Ein fehlendes oder anders dargestelltes Rufzeichen beziehungsweise Grid-4 wird nicht durch Schlussfolgerung zulässig.

Wenn mehrere qualifizierende, nicht identische Zeilen dieselbe logische Kombination aus Seite, Peer und Zyklus darstellen, behält WSPRadar den stärksten qualifizierenden normierten SNR als besten beobachteten Wert dieser logischen Identität. Dadurch können exakte Wiederholungen oder schwächere Zweit-Decodes den beibehaltenen Seitenwert nicht absenken. Der Wert ist jedoch kein Zentralwert eines einzelnen physischen Empfängers. Unterschiedliches Mehrfach-Empfänger- oder Meldeverhalten auf beiden Seiten kann deshalb eine Asymmetrie erzeugen. Beim lokalen Nachbarschafts-Median wird stattdessen zunächst innerhalb jeder lokalen Identität ein Median und erst danach über die Identitäten hinweg aggregiert.

**Warum wird die stärkste Meldung beibehalten?** Mehrere Meldungen für dieselbe Station, denselben Peer und denselben WSPR-Zyklus stellen nicht zwangsläufig unabhängige Beobachtungen dar. Entstehen schwächere Meldungen durch sender- oder empfängerseitige Signalrepliken, unerwünschte Spektralkomponenten oder Zweit-Decodes, lässt sich ihr Mittelwert oder Median nicht begründet als SNR des Hauptsignals interpretieren. Das stärkste qualifizierende normierte SNR steht für den besten beobachteten Empfang und verhindert, dass schwächere zusätzliche Meldungen diesen Wert absenken. Diese Meldungen tragen weiterhin nur ein Detektionsergebnis oder eine gepaarte Beobachtung für den jeweiligen Zyklus und Funkweg bei.

Diese Interpretation als bester gemeldeter Empfang entspricht dem dokumentierten Zusammenführen mehrerer Empfänger in WsprDaemon: Liefern mehrere Empfänger Meldungen für dieselbe Aussendung, meldet es das beste SNR an WSPRnet. Dies ist ein Beispiel einer bestehenden Meldepraxis und kein Beleg dafür, dass eine bestimmte gespeicherte Meldung das beabsichtigte Signal darstellt oder beide Vergleichsseiten dieselbe Spektralkomponente ausgewählt haben. <a href="#ref-11">[Ref-11]</a>

Die Auswahl der stärksten Meldung gilt für die SNR-Werte bei Performance, beide Seiten eines simultanen Benchmarks mit fester Referenz und die Target-Seite des lokalen Nachbarschafts-Medians. Bei lokalen Referenzbeiträgen bleiben die Mediane innerhalb jeder Identität und der anschließende Median über die Identitäten erhalten. Diese unterschiedlichen Konstruktionen sind in [Abschnitt 7.7](#sec-7-7) definiert. Mediane und IQR über beibehaltene Beobachtungen bleiben Zusammenfassungen der daraus entstehenden Evidenz und sind von der Auswahl eines SNR-Werts innerhalb eines Zyklus und Funkwegs zu unterscheiden.

Der lokale Pool schließt das Target anhand des exakten Rufzeichens aus. Basisrufzeichen und Rufzeichen mit Suffix sind verschieden, sofern nicht die exakte Target-Form übereinstimmt. Falsche, veraltete oder wechselnde Locator können eine physische Station aufteilen, geografisch verschieben oder den Ausschluss beweglicher Stationen auslösen.
````

</details>


### 7.3 Konditionierung auf Target-Aktivität und Zulässigkeit

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-3"></a>
#### 7.3 Konditionierung auf Target-Aktivität und Zulässigkeit

Ein stiller Zyklus ist mehrdeutig: Das Target kann außer Betrieb gewesen sein, oder seine Beteiligung hat keinen gemeldeten Decode erzeugt. WSPRadar zählt Gegen-Evidenz nur in Zyklen mit beobachtbarer Target-Beteiligung. Diese Einschränkung heißt **Konditionierung auf Target-Aktivität**.

Sei $A_c$ der Indikator für beobachtbare Target-Beteiligung im Zyklus $c$:

* TX: Im Zyklus existiert irgendwo mindestens eine qualifizierende Meldung einer Target-Aussendung.
* RX: Der Target-Empfänger hat im Zyklus mindestens einen qualifizierenden Decode hochgeladen.

Performance und simultaner Benchmark konditionieren auf $A_c=1$. Dadurch werden Zeiten ohne beobachtbare Target-Aktivität nicht automatisch zu Gegen-Evidenz, ohne zwischen Ausfallzeit und unbeobachteter Beteiligung zu unterscheiden. Zugleich verändert diese Regel die Analysepopulation: Das Ergebnis beschreibt Zyklen mit beobachtbarer Target-Beteiligung und nicht die gesamte Uhrzeit oder sämtliche geplanten Versuche.

Die Konditionierung ist asymmetrisch. Die Betriebszeit der Referenz bildet kein zweites Gate und muss extern kontrolliert oder dokumentiert werden. Ein Tausch von Target und Referenz kann deshalb zulässige Zyklen und einseitige Decode Outcomes verändern, selbst wenn sich das Vorzeichen des reinen Joint-ΔSNR erwartungsgemäß umkehrt.

Jede Joint-Beobachtung belegt bereits eine Target-Beteiligung. Das Gate verändert daher nicht die ΔSNR-Werte der Joint-Beobachtungen. Es verändert die Population einseitiger oder asynchroner Outcomes und bei Performance den Gelegenheitsnenner.

Target-Aktivität darf global nachgewiesen werden, auch wenn der Peer, der sie belegt, außerhalb des ausgewählten geografischen Analysebereichs liegt. Dieser Peer setzt lediglich $A_c$; er geht nicht in die begrenzten Outcomes, Zusammenfassungen oder Exporte ein.

**Welche Meldungen können Aktivität belegen?** Bei Performance kann eine Target-Meldung mit einem Peer, der später wegen eines speziellen Rufzeichens oder wechselnden Standorts ausgeschlossen wird, weiterhin Aktivität belegen. Bei Benchmark gelten diese Peer-Ausschlüsse bereits vor dem Aktivitätsnachweis; das Target benötigt deshalb eine Meldung mit einem danach noch zulässigen Peer. Der geografische Bereich wird bei beiden Designs erst anschließend angewendet. Belegt nur ein ausgeschlossener Peer die Target-Aktivität eines Zyklus, kann daher eine Performance-Gelegenheit für einen anderen zulässigen Peer erhalten bleiben, aber kein Benchmark-Outcome. Der ausgeschlossene Peer selbst trägt zu keiner der beiden Ergebnispopulationen bei.
````

</details>


### 7.4 Performance-Analyseziel, Klassifikation und Zusammenfassungsgrößen

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-4"></a>
#### 7.4 Performance-Analyseziel, Klassifikation und Zusammenfassungsgrößen

Performance beschreibt die Beteiligung des Targets innerhalb beobachtbarer Gelegenheiten der beibehaltenen Peer-Population. Die Größe ist bewusst bedingt: Gefragt wird, was das Target tat, wenn ein erfolgreicher Target-seitiger Decode oder externe Evidenz die erforderliche Endpunktaktivität belegte.

Der Nenner umfasst Erfolge und extern gestützte Misses; er besteht weder aus sämtlichen Uhrzeitzyklen noch ausschließlich aus extern bestätigten Zyklen.

Für Peer $i$ und Target-aktiven Zyklus $c$ sei $T_{i,c}=1$, wenn ein gültiger Target-seitiger Decode vorliegt, und $E_{i,c}=1$, wenn qualifizierende externe Evidenz die Aktivität des Peer-Endpunkts bestätigt. Die gewählten Band-, exakten Peer-Identitäts-, Filter- und geografischen Bereichsregeln gelten, bevor ein Peer-Zyklus eingeht. Erfolg $S_{i,c}$, Gelegenheit $O_{i,c}$ und Miss $M_{i,c}$ sind definiert durch:

$$S_{i,c}=T_{i,c},\qquad O_{i,c}=T_{i,c}\lor E_{i,c},\qquad M_{i,c}=E_{i,c}\land\neg T_{i,c}$$

Jeder gültige Erfolg liefert damit seine eigene Gelegenheit, mit $S_{i,c}\le O_{i,c}$ und $O_{i,c}=S_{i,c}+M_{i,c}$. Die Methodenkennung lautet `opportunity-v3`.

In der Formel bedeutet $\lor$ „oder“, $\land$ „und“ und $\neg$ „nicht“: Eine Gelegenheit benötigt einen Target-Decode oder externe Bestätigung; ein Miss benötigt externe Bestätigung ohne Target-Decode.

* RX-Rollen: Der **Target-RX** empfängt den **Peer-TX**. Die Meldung Peer-TX → Target-RX bestätigt beide Endpunkte und ist ein Erfolg. Eine Meldung Peer-TX → anderer geeigneter RX bestätigt die Sendeaktivität dieses Peer-TX; sie stützt einen Miss nur dann, wenn auch der Target-RX im selben Zyklus nachweislich aktiv ist.
* TX-Rollen: Der **Target-TX** sendet zum **Peer-RX**. Die Meldung Target-TX → Peer-RX bestätigt beide Endpunkte und ist ein Erfolg. Eine Meldung anderer qualifizierender TX → derselbe Peer-RX bestätigt die Empfangsaktivität dieses Peer-RX; sie stützt einen Miss nur dann, wenn auch der Target-TX im selben Zyklus nachweislich aktiv ist.

Ein Target-only-Erfolg hat $T_{i,c}=1$ und $E_{i,c}=0$. Seine Herkunft bleibt als Teilmenge der Erfolge nachvollziehbar; er ist bereits genau einmal in Erfolgs- und Gelegenheitsanzahl enthalten. Externe Bestätigung zusätzlich zu einem Erfolg erzeugt keine weitere Gelegenheit. Sind beide Flags null, reicht die Endpunktaktivität nicht aus: Der Peer-Zyklus bleibt unbekannt und ausgeschlossen. Das Target-Active Gate bleibt unverändert. Aktivität andernorts belegt nicht, dass ein bestimmter stiller Target-RX oder Peer-RX zugehört hat.

| Target-Decode | Externe Evidenz | Erfolg | Gelegenheit | Miss | Deutung |
| :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | 0 | 1 | 1 | 0 | Target-only; Teilmenge der Erfolge |
| 1 | 1 | 1 | 1 | 0 | Extern gestützter Erfolg |
| 0 | 1 | 0 | 1 | 1 | Extern gestützter Miss in einem Target-aktiven Zyklus |
| 0 | 0 | 0 | 0 | 0 | Aktivität unbekannt; ausgeschlossen |

Für einen qualifizierenden Peer werden Gelegenheiten und Target-Erfolge über die beibehaltenen Zyklen gezählt; anschließend werden Erfolge durch Gelegenheiten geteilt:

$$n_i=\sum_c O_{i,c},\qquad h_i=\sum_c S_{i,c}$$

$$r_i=100\%\times\frac{h_i}{n_i}$$

Dabei ist $n_i$ die Zahl bestätigter Gelegenheiten dieses Peers, $h_i$ die Zahl der Target-Erfolge und $r_i$ seine Dekodierrate. Ein Peer trägt nur bei, wenn $n_i$ den konfigurierten Mindestwert erreicht.

Für den geografischen Bereich $g$ mit der qualifizierenden Peer-Menge $I_g$ bezeichnet $|I_g|$ die Zahl qualifizierender Peers. Ihre einzelnen Raten werden addiert und durch diese Peer-Anzahl geteilt; daraus ergibt sich die stationsgleichgewichtete Dekodierrate:

$$R_{station}(g)=\frac{1}{|I_g|}\sum_{i\in I_g} r_i$$

Dies ist das exakte arithmetische Mittel der beibehaltenen Peer-Raten: Jeder qualifizierende Peer erhält unabhängig von seiner Gelegenheitsanzahl eine gleich große Stimme.

Die Dekodierrate auf Gelegenheitsebene lautet:

$$R_{opportunity}(g)=100\%\times\frac{\sum_{i\in I_g}h_i}{\sum_{i\in I_g}n_i}$$

Dies ist der exakte Anteil erfolgreicher Target-Outcomes über alle beibehaltenen Gelegenheiten: Jede Gelegenheit erhält eine gleich große Stimme. Beide Raten sind ergänzende Zusammenfassungen und keine zwei Näherungen an eine einzige „wahre“ Rate. Sie beantworten unterschiedliche Gewichtungsfragen; ihre Abweichung ist aufschlussreich, wenn sich das Evidenzvolumen zwischen den Peers stark unterscheidet.

**Beispiel: ein Ergebnis, zwei Gewichtungsfragen.** Zwei Peers erfüllen bereits die konfigurierte Mindestanzahl an Gelegenheiten. Peer A hat `90 Erfolge / 100 Gelegenheiten = 90%`, Peer B `5 / 10 = 50%`. Bei gleicher Peer-Gewichtung ergeben sich **70 %**. Über alle Gelegenheiten gepoolt sind es `95 / 110`, also **86,4 %**. Der gepoolte Nenner enthält 95 Erfolge und 15 Misses; jede Gelegenheit zählt einmal. Der größere Wert entsteht durch das höhere Evidenzvolumen des erfolgreicheren Funkwegs und macht die Rechnung mit gleicher Peer-Gewichtung nicht falsch.

Die Mindestens-einmal-Reichweite lautet:

$$Reach(g)=100\%\times\frac{|\{i\in I_g:h_i\ge1\}|}{|I_g|}$$

In Funkpraxis-Sprache ist dies der Prozentsatz qualifizierender Peers, bei denen das Target in mindestens einer qualifizierenden Gelegenheit erfolgreich war.

Im Nenner stehen alle qualifizierenden Peers des Bereichs. Ein Peer mit einem Erfolg und ein Peer mit vielen Erfolgen zählen im Zähler jeweils einmal. Die Reichweite beschreibt Breite. Bei einer festen zulässigen Peer-Menge kann zusätzliche Evidenz keinen früheren Erfolg aufheben, solange die bisherige Evidenz erhalten bleibt. Zwischen Läufen kann sich jedoch die qualifizierende Peer-Population ändern; der angezeigte Reichweitenanteil muss deshalb mit längerer Laufdauer nicht steigen. Wie beständig die Funkwege funktionierten, beantwortet die Dekodierrate. Im obigen Beispiel mit zwei Peers beträgt die Reichweite 100 %, obwohl deren Dekodierraten verschieden sind.

Erfolgreiches Target-SNR ist nur definiert, wenn das Target decodiert oder gemeldet wurde, einschließlich Target-only-Erfolgen. Es ist damit eine auf erfolgreiche Decodes bedingte Verteilung. Zugrunde liegen alle beibehaltenen Erfolge nach Zusammenfassung auf die stärkste Meldung und Normierung; die späteren Abschnitte definieren, wie jede Ansicht diese Werte für Mediane, IQR und Extremwerte gruppiert und gewichtet. Dieselbe Klassifikation gilt für Stationsschwellen, beide Gewichtungen der Dekodierrate, Karten, Mindestens-einmal-Reichweite, chronologische und gefaltete Profile, Station Insights, Evidenz der ausgewählten Station, Drill-Down und Exporte. Verpasste Gelegenheiten besitzen kein Target-SNR und erhalten keinen künstlichen Wert. Dekodierrate und erfolgreiches SNR müssen gemeinsam gelesen werden: Ein System, das zusätzliche schwache Signale decodiert, kann die praktische Reichweite verbessern und zugleich den Median der erfolgreichen SNR-Werte absenken.

Das Performance-Analyseziel ist somit die bedingte Beteiligung des Targets unter beobachtbaren Gelegenheiten in der beibehaltenen Population und unter der gewählten Gewichtung. Es ist weder unbedingte Empfängerempfindlichkeit noch die Erfolgswahrscheinlichkeit sämtlicher Sendeversuche oder der absolute Wirkungsgrad der Station.
````

</details>


### 7.5 Leistungsnormierung, Korrektur und Benchmark-ΔSNR

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-5"></a>
#### 7.5 Leistungsnormierung, Korrektur und Benchmark-ΔSNR

WSPR meldet SNR auf der WSJT-Skala in dB bezogen auf eine Referenzbandbreite von 2500 Hz und überträgt die gemeldete Sendeleistung in dBm <a href="#ref-8">[Ref-8]</a>. WSPRadar bezieht erfolgreiche SNR-Beobachtungen sowohl in RX- als auch in TX-Analysen auf eine gemeinsame gemeldete Sendeleistung von 30 dBm (1 W). So lassen sich gespeicherte Signalpegel nach Herausrechnen des gemeldeten Leistungsunterschieds vergleichen; die Rechnung rekonstruiert keine Decodes, die bei dieser Leistung stattgefunden hätten:

$$SNR_{norm}=SNR_{measured}-P_{TX(dBm)}+30$$

Praktisch wird ein Signal mit 10 dB geringerer gemeldeter Sendeleistung für diesen Vergleich um 10 dB angehoben. Ein mit `-15 dB` gemeldetes SNR bei `20 dBm` wird beispielsweise auf `-5 dB` bei `30 dBm` normiert. Die Rechnung entfernt ausschließlich den **gemeldeten** Leistungsanteil.

Dabei sind $SNR_{measured}$ und $SNR_{norm}$ SNR-Werte in dB; $P_{TX(dBm)}$ ist die für diese Beobachtung gemeldete Sendeleistung. Decode Outcomes und der Gelegenheitsnenner bei Performance bleiben unverändert die tatsächlich beobachteten. Die Normierung korrigiert weder Antennengewinn, Strahlungswirkungsgrad, Speiseleitungsverlust, EIRP, Empfängerkalibrierung noch lokalen Stör- oder Rauschpegel.

Die referenzseitige Korrektur wird addiert:

$$SNR_{R,corr}=SNR_R+C_R$$

Für einen Joint Spot wird das korrigierte Referenz-SNR vom normierten Target-SNR abgezogen:

$$D_{i,c}=\Delta SNR_{i,c}=SNR_{T,i,c}-SNR_{R,corr,i,c}$$

Dabei ist $C_R$ die vorzeichenbehaftete additive referenzseitige Korrektur. In der ersten Gleichung bezeichnen $SNR_R$ und $SNR_{R,corr}$ das Referenz-SNR vor und nach der Korrektur. In der Gleichung für das Paar kennzeichnen die Indizes $i,c$ den Peer und die zugeordnete Evidenzeinheit; $SNR_{T,i,c}$ ist das zugehörige normierte Target-SNR und $SNR_{R,corr,i,c}$ das korrigierte Referenz-SNR. Die konfigurierte Korrektur gehört zur Referenzseite und wird nicht zum Target addiert. Positives $D_{i,c}$ spricht für das Target, negatives für die Referenz. Eine positive Korrektur macht die Referenz vor der Subtraktion stärker und senkt deshalb ΔSNR. Der eingegebene Kalibrierversatz verwendet dasselbe Vorzeichen `target - reference`.

**Vorzeichenprüfung.** Bei normiertem Target-SNR `-10 dB` und Referenz-SNR `-12 dB` beträgt ΔSNR `+2 dB`. Eine Referenzkorrektur von `+1.5 dB` setzt die Referenz auf `-10.5 dB`; ΔSNR beträgt dann `+0.5 dB`. Die Target-Beobachtungen sind unverändert; der Vergleich berücksichtigt den eingegebenen Referenzversatz.

Der Wert $D_{i,c}$ ist eine beobachtete gepaarte Differenz für genau eine beibehaltene Vergleichseinheit. Er wird exakt aus den beiden beibehaltenen SNR-Werten und der gegebenenfalls konfigurierten Korrektur berechnet. Seine Interpretation hängt dennoch davon ab, wofür beide Seiten stehen und wie gut der physische Versuch die übrigen Ketten kontrolliert hat.

Bei RX-Paaren desselben Senders fällt der gemeinsame gemeldete TX-Leistungsanteil heraus. TX-Paare verschiedener Signale hängen unmittelbar von der Richtigkeit der gemeldeten Leistung und von unkorrigierten Unterschieden der Sender- oder Speiseleitungsketten ab. Eine Referenzkorrektur ist nur dann wissenschaftlich vertretbar, wenn der Offset über das relevante Band, den Pegelbereich, den Hardwarezustand und die Zeit näherungsweise additiv und stabil ist.
````

</details>


### 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-6"></a>
#### 7.6 Gepaarte Evidenz, Decode Outcomes und fehlende Beobachtungen

Benchmark besitzt zwei miteinander verknüpfte Analyseziele:

1. die Verteilung des Target-minus-Referenz-ΔSNR unter **Joint**-Vergleichseinheiten und
2. die Zusammensetzung der beibehaltenen Evidenz aus **Only Target**, **Joint**, **Only Reference** sowie auf Identitätsebene **Both (Async)**.

ΔSNR existiert nur, wenn beide Seiten vergleichbare Evidenz erzeugen. Die Joint-Teilmenge wird daher durch den erfolgreichen Decode beider Seiten ausgewählt. In statistischer Sprache sind die fehlenden Paare normalerweise nicht „zufällig fehlend“: Schwache Signale, Kollisionen, QRM, Decoderverhalten, Leistungsunterschiede und Funkwegbedingungen können alle beeinflussen, ob ein Paar entsteht. In Stationssprache heißt das: Die überlebenden Paare müssen nicht jede Gelegenheit nahe der Decode-Schwelle gleich gut repräsentieren.

Einseitige Evidenz besitzt kein SNR der fehlenden Seite, das rekonstruiert werden könnte. Ihr darf kein künstliches ΔSNR zugewiesen werden, und sie wird nicht als Paar leistungsnormiert. Bei TX Benchmark können unterschiedliche tatsächliche oder gemeldete Leistungen einseitige Outcomes stark beeinflussen, selbst wenn das Joint-ΔSNR normiert ist.

`Both (Async)` bedeutet, dass für eine Identität beibehaltene Evidenz beider Seiten existiert, aber für die betreffende Stationskategorie keine qualifizierende Einheit desselben Zyklus erhalten bleibt. Die Kategorie zeigt eine breitere Beteiligung beider Seiten, trägt jedoch kein gepaartes ΔSNR bei.

Werden Folgen mit zusammengesetzten Rufzeichen verwendet, hängt die Upstream-Identität von Typ 3 von der Auflösung eines 15-Bit-Rufzeichen-Hashs ab. Ein Hash kann unaufgelöst bleiben oder mit einem anderen bekannten Rufzeichen kollidieren. Dadurch kann ein physischer Decode fehlen, falsch identifiziert oder einem falschen Locator beziehungsweise Leistungswert zugeordnet werden. QRP Labs dokumentiert ein beobachtetes Beispiel und den Mechanismus <a href="#ref-19">[Ref-19]</a>.

Findet eine Prüfung nur wenige vereinzelte Fehlzuordnungen unter Zehntausenden von Beobachtungen und keine Häufung nach Target- oder Referenzseite, Folgenphase, Empfänger oder Zeit, können die Medianwerte unverändert oder nahezu unverändert bleiben; dies muss jedoch in der betroffenen Population geprüft werden. Diese Robustheit darf nicht allein aus der Datenmenge abgeleitet werden: Systematische, gehäufte oder asymmetrische Fehlzuordnungen können die Joint-Zulässigkeit, einseitige Decode Outcomes und Stationsmediane verändern, auch innerhalb eines kleinen Segments. WSPRadar kann nur prüfen, ob das konfigurierte exakte Rufzeichen und Grid-4 in der ausgewählten Datenbank vorliegen; es kann nicht beweisen, dass jede Upstream-Hash-Zuordnung physisch korrekt war.

Bei zusammengesetzten Rufzeichen sind deshalb die Datenbank-Vorprüfung und die phasenbezogene Prüfung aus [Anhang B](#sec-simultaneous-tx-setup) erforderlich.

Die Zensierung auf erfolgreiches SNR bei Performance und die Auswahl nach gemeinsamem Decode bei Benchmark sind verschiedene Selektionsprozesse. WSPRadar zeigt Decode Outcomes und Joint-Evidenzanteil, damit die gepaarten ΔSNR-Zusammenfassungen im Verhältnis zur breiteren beibehaltenen Evidenz gelesen und nicht mit der vollständigen Stationspopulation gleichgesetzt werden.
````

</details>


### 7.7 Aggregationshierarchie und Gewichtung

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-7"></a>
#### 7.7 Aggregationshierarchie und Gewichtung

WSPRadar verwendet eine hierarchische Aggregation: Zuerst wird die Evidenz innerhalb jeder Peer-Identität zusammengefasst, danach über die Peers hinweg. Dadurch kann ein Peer mit hohem Datenvolumen ein stationsgleichgewichtiges Ergebnis nicht allein deshalb dominieren, weil er mehr Beobachtungen gemeldet hat. Zugleich beantworten stationsgleichgewichtete und beobachtungsbezogene Zusammenfassungen bewusst unterschiedliche Fragen.

**Performance**

1. Jeden zulässigen Peer-Zyklus klassifizieren.
2. Alle qualifizierenden Target-Erfolge und extern gestützten Misses nach Peer-Identität zusammenfassen. Target-only-Herkunft als Teilmenge der Erfolge bewahren, ohne sie nochmals zu den Gesamtsummen zu addieren.
3. Die Mindestanzahl an Gelegenheiten anwenden.
4. Für jeden Peer eine Dekodierrate $r_i$ berechnen.
5. Das gleichgewichtete Peer-Mittel $R_{station}$ berechnen.
6. $R_{opportunity}$ als ergänzende, nach Gelegenheiten gewichtete Zusammenfassung beibehalten.

Das erste Ergebnis beschreibt den typischen qualifizierenden Peer bei gleicher Peer-Gewichtung; das zweite die gepoolte beibehaltene Gelegenheits-Population.

<p style="page-break-after: avoid; -pdf-keep-with-next: true;"><strong>Simultaner Benchmark</strong></p>

Zeigt sich die Verschiebung über mehrere Peers oder prägen wenige Funkwege mit vielen Meldungen das Ergebnis? Lies die folgenden Kennzahlen zusammen mit Stationsverteilungen und Anzahlen.

1. Target- und Referenzevidenz nach Peer und Zyklus konsolidieren.
2. Für Joint-Zyklen $D_{i,c}$ berechnen.
3. Die Mindestanzahl an Joint-Evidenz je Peer anwenden.
4. Den Peer-Median berechnen:

    $$m_i=\operatorname{median}_{c}(D_{i,c})$$

5. Für den Bereich $g$ die stationsgleichgewichtete Segmentzusammenfassung berechnen:

    $$M_g=\operatorname{median}_{i\in I_g}(m_i)$$

Dabei ist $m_i$ die typische gepaarte Differenz eines Peers und $M_g$ der Median dieser Peer-Mediane. Jeder qualifizierende Peer trägt somit genau einen Wert zum Segmentergebnis bei. Der Median aller $D_{i,c}$ auf Beobachtungsebene bleibt getrennt erhalten; in dieser Zusammenfassung erhalten Peers mit mehr Joint-Beobachtungen ein größeres Gewicht.

**Veranschaulichendes Beispiel: warum die Ergebnisse abweichen können.** Diese drei Peer-Identitäten erfüllen nach Zuordnung, Korrektur und Filterung bereits die Anforderungen in einem Segment. Jeder Eintrag ist ein eigener beibehaltener Joint-Peer-Zyklus.

| Peer-Identität | Beibehaltene ΔSNR-Werte (dB) | Peer-Median (dB) |
|---|---|---:|
| A | +6, +6, +6, +6, +6, +6 | +6 |
| B | -2, -2 | -2 |
| C | -1, -1 | -1 |

Der stationsgleichgewichtete Median beträgt **-1 dB**: der mittlere Peer-Median in `-2, -1, +6`. Der Median auf Beobachtungsebene beträgt **+6 dB**: Der fünfte und sechste aller zehn sortierten Werte sind jeweils `+6`. Peer A liefert sechs Beobachtungen, aber nur einen Peer-Median. Beide Ergebnisse beschreiben dieselbe Joint-Evidenz mit unterschiedlicher Gewichtung: Prüfe bei Abweichungen die beitragenden Funkwege. Keine der Gewichtungen allein belegt einen Antennenvorteil oder macht aus den Beobachtungen unabhängige experimentelle Wiederholungen.

Bei jedem Benchmark-Design gilt für Gewichtung und Segmentunterstützung dieselbe Stationsidentität: das exakte `Rufzeichen + vollständig gemeldeter Locator`. Jede Identität muss für sich die konfigurierte Mindestzahl an Joint-Evidenz erfüllen. Genau die Identitäten, die jeweils einen Peer-Median beitragen, zählen auch für die Mindestanzahl qualifizierender Stationen pro Kartensegment. Identitäten mit ausschließlich einseitiger Evidenz tragen nicht zu dieser ΔSNR-Unterstützungszahl bei. Dasselbe Rufzeichen mit unterschiedlichen vollständigen Locatorn zählt getrennt, auch wenn beide Locator im selben Grid-4 liegen. Gezählt werden gemeldete Funkwegidentitäten; daraus folgen keine unabhängigen physischen Stationen oder Standorte.

Beispielsweise ergeben zwei qualifizierende Identitäten mit demselben Rufzeichen und den Locatorn `JO31AA` und `JO31AB` bei Peer-Medianen von `+2 dB` und `+4 dB` einen Segmentmedian von `+3 dB` und eine Unterstützungszahl von `2`. Bei einer Mindestanzahl von zwei qualifizierenden Stationen bleibt dieses Segment erhalten; bei einer Mindestanzahl von drei nicht.

<p style="page-break-after: avoid; -pdf-keep-with-next: true;"><strong>Referenznachbarschaft (Lokaler Median)</strong></p>

Für jeden entfernten Peer-Zyklus berechnet WSPRadar zunächst je aktiver lokaler Identität aus `Rufzeichen + Locator` genau einen normierten SNR-Beitrag und danach den exakten Median über die beitragenden lokalen Identitäten. Eine nicht beobachtete lokale Identität wird weggelassen und nicht mit null angesetzt. Die Referenzkorrektur wird vor der Aggregation des lokalen Pools angewendet. Anschließend wird das Target mit diesem zyklus- und funkwegspezifischen Median verglichen; daraus entstehen Peer- und Segmentmediane des ΔSNR.

Gehören mehrere qualifizierende Meldungen zu derselben lokalen Referenzidentität, demselben entfernten Peer und demselben Zyklus, bilden ihre normierten SNR-Werte zunächst einen Median innerhalb dieser Identität. Jede beitragende lokale Identität liefert danach genau einen Wert für den Nachbarschafts-Median. Die bestehende Zusammenführung auf der Target-Seite behält das stärkste qualifizierende normierte SNR; die Nachbarschaftsmethode führt Meldungen auf beiden Seiten daher nicht nach derselben Regel zusammen.

Eine lokale Identität besteht aus Rufzeichen und vollständig gemeldetem Locator. Die gleiche Gewichtung dieser Identitäten garantiert keine gleiche Gewichtung unabhängiger physischer Standorte: Mehrere Meldeidentitäten können Geräte oder einen Standort teilen.

Es gibt keine gesonderte Mindestzahl lokaler Beitragender pro Peer-Zyklus. Bei einem Beitrag entspricht die Referenz dessen Wert. Ohne Beitragende steht weder ein Referenz-SNR noch gepaartes ΔSNR zur Verfügung. Die an anderer Stelle geltenden Anforderungen an die Mindestmenge gemeinsamer Evidenz und stützender Stationen legen keine Mindestgröße der Nachbarschaft fest.

**Eine andere Zusammensetzung kann den Vergleich verändern.** Drei lokale Identitäten liefern beispielsweise korrigierte SNR-Werte von `-18, -12, -6 dB`; ihr Referenzmedian beträgt `-12 dB`. Bei unverändertem Target-SNR von `-10 dB` ergibt sich ΔSNR `+2 dB`. Fehlt in einem anderen Zyklus der Beitrag von `-6 dB`, während die übrigen Werte gleich bleiben, beträgt der Referenzmedian `-15 dB` und ΔSNR `+5 dB`. Diese Verschiebung erfordert keine Änderung am Target, sondern entsteht aus der veränderten lokalen Population.

Der Nachbarschafts-Median beschreibt qualifizierende gemeldete Beobachtungen. Fehlende Meldungen sind keine Messungen von null SNR, und die beitragende Gruppe kann sich je nach entferntem Peer und Zyklus ändern. Mehr Beobachtungen beseitigen für sich genommen weder systematische Meldeunterschiede noch Selektionseffekte oder Abhängigkeiten zwischen Beobachtungen.

Mediane verringern die Empfindlichkeit gegenüber einzelnen Extremwerten, quantisierten SNR-Ausreißern und duplikatähnlichen Häufungen. Sie beseitigen weder systematische Kalibrierfehler noch Ausbreitungsverzerrungen oder Abhängigkeiten zwischen Zyklen und Stationen.
````

</details>


### 7.8 Geografische, zeitliche und funkwegbezogene Zusammenfassungen

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-8"></a>
#### 7.8 Geografische, zeitliche und funkwegbezogene Zusammenfassungen

<a id="sec-7-8-1"></a>
##### 7.8.1 Geografische Zusammenfassungen

Der Segment-Inspektor beginnt mit der vollständigen qualifizierenden Peer-Population im aktiven beibehaltenen Bereich. Tabellensortierung, Zeilenauswahl und Sichtbarkeitsbedienelemente verändern diese Zusammenfassungen nicht.

Performance-Entfernungsprofile gruppieren Peers nach der exakt berechneten Entfernung vom Target-QTH. Abhängig von der aktiven Entfernungsspanne wird deterministisch eine Breite von `125`, `250`, `500` oder `1.000 km` gewählt. Die Grenzen sind an ganzzahligen Vielfachen ab `0 km` verankert; die letzte ausgewählte Obergrenze ist eingeschlossen. Getrennte ausgewählte Bereiche behalten fehlende Lücken, statt sie als Null-Evidenz zu behandeln.

Für jedes Entfernungs-Bin berechnet WSPRadar:

* die Mindestens-einmal-Reichweite;
* die stationsgleichgewichtete Dekodierrate;
* die Dekodierrate auf Gelegenheitsebene und
* das erfolgreiche Target-SNR, zunächst auf einen Median je Peer reduziert und danach über diese Peer-Mediane zusammengefasst.

Für die Streuung des erfolgreichen SNR liefern mindestens drei Peer-Mediane einen Interquartilsabstand, zwei ein Min-Max-Intervall und einer einen einzelnen Punkt. Peers mit ausschließlicher Gegen-Evidenz erhalten kein künstliches SNR. Die Entfernung übernimmt die Genauigkeit des gemeldeten Maidenhead-Locators und ist keine vermessungsgenaue Position.

Geografische Benchmark-Zusammenfassungen verwenden je qualifizierender Identität genau einen Peer-Median des ΔSNR und danach den Segmentmedian dieser Peer-Mediane. Das ΔSNR auf Beobachtungsebene bleibt als getrennt gewichtete Verteilung verfügbar. Die erste Sicht beantwortet „Was zeigte der typische qualifizierende Peer?“, die zweite „Was zeigten die beibehaltenen gepaarten Beobachtungen, wenn jedes Paar zählt?“.

<a id="sec-7-8-2"></a>
##### 7.8.2 Abdeckung der Benchmark-Evidenz

Der Joint-Evidenzanteil beantwortet, welcher Anteil der beibehaltenen Benchmark-Evidenz einen SNR-Vergleich beider Seiten ermöglicht. Sein Nenner umfasst alle drei Outcomes, nicht nur Joint Spots und nicht sämtliche geplanten Zyklen.

Für Station $i$ im Bin $b$ seien die Anzahlen Only Target, Joint und Only Reference $T_{i,b}$, $J_{i,b}$ und $R_{i,b}$ mit:

$$N_{i,b}=T_{i,b}+J_{i,b}+R_{i,b}$$

Eine beitragende Station liefert eine aufgeteilte Stützungsstimme:

$$v_{T,i,b}=\frac{T_{i,b}}{N_{i,b}},\qquad v_{J,i,b}=\frac{J_{i,b}}{N_{i,b}},\qquad v_{R,i,b}=\frac{R_{i,b}}{N_{i,b}}$$

Praktisch erhält jeder Peer insgesamt eine Stationsstimme, die entsprechend seiner Mischung aus Only Target, Joint und Only Reference in diesem Bin aufgeteilt wird.

Der stationsgleichgewichtete Joint-Evidenzanteil lautet:

$$JES_{station}(b)=100\%\times\operatorname{mean}_{i}\left(\frac{J_{i,b}}{N_{i,b}}\right)$$

Der Joint-Evidenzanteil auf Outcome-Ebene lautet:

$$JES_{outcome}(b)=100\%\times\frac{\sum_iJ_{i,b}}{\sum_iN_{i,b}}$$

Die erste Größe gibt jedem beitragenden Peer dasselbe Gewicht, die zweite jeder beibehaltenen Vergleichseinheit.

Bei der ersten werden also zunächst die Joint-Anteile der einzelnen Peers berechnet und anschließend gemittelt; bei der zweiten werden zuerst alle Outcomes zusammengezählt und dann der Joint-Anteil gebildet.

Es tragen nur Peers mit mindestens einem beibehaltenen Outcome in diesem Bin bei; ein Peer ohne Evidenz liefert keinen Anteil. Die drei Anteile eines Peers ergeben zusammen eine Stützungsstimme. Der Joint-Evidenzanteil misst die Paarbarkeit – also welcher Anteil der beibehaltenen Evidenz zu ΔSNR beitragen kann. Er ist keine Gewinnquote des Targets.

Unter dem Target-Active Gate sind Only Target und Only Reference gerichtet und asymmetrisch. Einseitige Evidenz besitzt weiterhin kein ΔSNR.

<a id="sec-7-8-3"></a>
##### 7.8.3 Zeitliche Zusammenfassungen und UTC-Faltung

Chronologische Ansichten bewahren die tatsächliche Reihenfolge des Laufs über das vollständige ausgewählte UTC-Zeitfenster mit der gewählten Zeit-Bin-Breite. Die Bins beginnen am ausgewählten Startzeitpunkt; das abschließende Intervall kann kürzer sein, und Zeitabschnitte ohne Evidenz bleiben leer, statt zu 0 dB zu werden. UTC-Stunden-Ansichten **falten** die Evidenz, indem Beobachtungen verschiedener Tage auf dieselbe 24-Stunden-UTC-Uhr ausgerichtet werden. Die chronologische Sicht fragt damit „Was änderte sich während dieses Laufs?“, die gefaltete Sicht „Kehrte ein Muster zu einer bestimmten UTC-Stunde an mehreren berücksichtigten Tagen wieder?“.

Die angebotenen chronologischen Breiten richten sich nach der vollständigen Laufdauer und nicht nach der beobachteten Evidenzspanne: Läufe bis 6 Stunden verwenden standardmäßig `10m`, längere Läufe bis 24 Stunden `30m` und Läufe über 24 Stunden `12h`. [Abschnitt 4.5](#sec-5-5) führt die vollständigen Angebote einschließlich `2h` in jeder Dauerstufe auf.

Die Abweichung des erfolgreichen Performance-SNR vergleicht jeden Funkweg mit seinem eigenen üblichen erfolgreichen Pegel in diesem Lauf; dauerhaft starke Funkwege bestimmen deshalb nicht den Nullpunkt schwächerer Funkwege. Ein Peer geht nur dann in die Anomaliepopulation ein, wenn er im vollständigen Laufzeitfenster mindestens drei erfolgreiche normierte Target-SNR-Beobachtungen besitzt. Seine Basislinie ist der Median dieser Erfolge. Jede erfolgreiche Beobachtung trägt bei:

$$A_{i,c}=SNR_{i,c}-\operatorname{median}_{c'}(SNR_{i,c'})$$

Dabei kennzeichnet $c$ die aktuelle erfolgreiche Beobachtung; $c'$ durchläuft alle erfolgreichen Beobachtungen des Peers $i$ im vollständigen Laufzeitfenster, aus denen seine Basislinie entsteht. `0 dB` bedeutet damit „auf dem für diesen Funkweg üblichen erfolgreichen Pegel“ und nicht Target–Referenz-Gleichheit. Ein positiver Wert bedeutet, dass dieser erfolgreiche Decode stärker als der für diesen Peer übliche erfolgreiche Pegel im Lauf war; ein negativer Wert bedeutet schwächer. Es handelt sich um eine Abweichung innerhalb eines Funkwegs und nicht um Target-minus-Referenz-ΔSNR.

Chronologisch trägt jeder Peer je ausgewähltem Bin höchstens einen Median der Abweichung bei. In der UTC-gefalteten Sicht trägt jeder Peer zunächst je Datum und UTC-Stunde einen Median bei; erst danach werden diese Peer-Datum-Stunden-Werte über die gefaltete Population zusammengefasst. Innerhalb einer Kombination aus Peer, Datum und Stunde erhöhen zusätzliche Zeilen das Gewicht nach dieser Medianbildung nicht. Peers an mehr Tagen und Tage mit mehr Peers liefern aber weiterhin mehr Werte für die gefaltete Population; es handelt sich nicht um eine über den vollständigen Lauf gleiche Gewichtung der Peers oder Tage.

Die zeitliche Performance-Stützung verwendet dieselben qualifizierenden Peers, behält aber alle bestätigten Gelegenheiten einschließlich der Peers, die aus der erfolgreichen SNR-Anomalieebene ausgeschlossen sind. In einem chronologischen Bin liefert jeder Peer eine nach seiner Dekodierrate im Bin aufgeteilte Stimme. Die gesamte Stationsstützung entspricht damit der Zahl beitragender Peers; das Teilungsverhältnis reproduziert die stationsgleichgewichtete Rate. Die Gelegenheitsstützung ist die rohe Zahl bestätigter Gelegenheiten; ihr Teilungsverhältnis reproduziert die Dekodierrate auf Gelegenheitsebene.

Für jede gefaltete UTC-Stunde ist die Stationsstützung die durchschnittliche Zahl unterschiedlicher Peer-Datum-Stunden-Präsenzen über die berücksichtigten Tage, deren Stundenslot das Analysefenster überlappt. Die gefaltete stationsgleichgewichtete Rate entsteht, indem die Outcomes jedes Peers zu dieser UTC-Stunde über die berücksichtigten Tage gepoolt, daraus je Peer eine Rate berechnet und anschließend jeder Peer gleich gewichtet wird. Gefaltete Gelegenheitsanzahlen sind gepoolte Outcome-Summen geteilt durch den zugehörigen Nenner berücksichtigter Tage.

Bei Performance ist ein **berücksichtigter UTC-Tag** ein Datum, an dem im aktiven Bereich und ausgewählten Fenster mindestens eine qualifizierende bestätigte Gelegenheit existiert. Eine im Fenster liegende Datum-Stunde ohne Evidenz trägt für einen berücksichtigten Tag null bei; eine Datum-Stunde außerhalb des Fensters wird ausgeschlossen. Eine nur teilweise überlappende erste oder letzte Stunde zählt als ein vollständiger berücksichtigter Slot und wird nicht nach Expositionsanteil gewichtet. Dadurch können Mittelwerte an Randstunden niedriger ausfallen. Die UTC-Stunden-Faltung erfordert mindestens zwei berücksichtigte Tage.

Das zeitliche Benchmark-ΔSNR verwendet beibehaltene Joint-Beobachtungen. Wenn keine gepaarten Werte verbleiben, zeigt das ΔSNR-Panel weiterhin das vollständige ausgewählte UTC-Zeitfenster und weist auf die fehlende gepaarte Evidenz für Δ SNR hin. Das bedeutet, dass im dargestellten Bereich keine beibehaltene Joint-Beobachtung verbleibt; daraus folgt nicht, dass die Datenquelle keine Beobachtungen lieferte, und die zeitliche Abdeckung kann weiterhin einseitige Outcomes zeigen. Chronologische Bins fassen gepaarte Werte in tatsächlicher Zeit zusammen; UTC-Stunden-Bins fassen dieselbe gepaarte Population nach Stunde über die Tage zusammen, die in der beibehaltenen Benchmark-Evidenz vertreten sind. Die zeitliche Benchmark-Abdeckung verwendet alle beibehaltenen Einheiten Only Target, Joint und Only Reference sowie die beiden oben definierten Zusammenfassungen des Joint-Evidenzanteils. Auch die Benchmark-Faltung erfordert mindestens zwei Tage mit Evidenz.

<a id="sec-7-8-4"></a>
##### 7.8.4 Zusammenfassungen für den ausgewählten Funkweg

Die Evidenz der ausgewählten Station filtert den aktiven beibehaltenen Bereich auf genau eine Peer-Identität, ohne die vorgelagerte Analysepopulation zu verändern.

Bei Performance zeigt der ausgewählte Funkweg:

* das tatsächliche normierte erfolgreiche Target-SNR in chronologischen Bins;
* je berücksichtigtem Datum und UTC-Stunde einen Median im gefalteten SNR-Profil;
* Anzahlen erfolgreicher und Gegen-Gelegenheiten sowie
* die Dekodierrate im Zeitverlauf.

Bei genau einem Peer sind die stationsgleichgewichtete Dekodierrate und die Dekodierrate auf Gelegenheitsebene innerhalb eines belegten Bins numerisch identisch, weil beide dieselben Erfolge und Gelegenheiten dieses einen Peers verwenden. Die getrennten Stützzahlen unterscheiden dennoch Funkwegpräsenz von Evidenzvolumen.

Bei Benchmark zeigt der ausgewählte Funkweg das ΔSNR jeder Joint-Einheit auf Beobachtungsebene und getrennt die Abdeckung durch Only Target, Joint und Only Reference. Ein Wechsel des ausgewählten Funkwegs oder Darstellungs-Bins verändert nur die Ansicht der beibehaltenen Evidenz, nicht die vorgelagerte Zuordnung, Zulässigkeit oder Aggregation.

Der Drill-Down kann dieselbe Evidenz des ausgewählten Funkwegs vor Anwendung gewöhnlicher Tabellenfilter vorübergehend auf ein zentriertes Intervall von `1h`, `3h`, `6h`, `12h` oder `24h` begrenzen. Sein fokussiertes Messwertrezept behält je nativer Koordinate eine wissenschaftliche Einheit: beim simultanen Benchmark einen zusammengeführten Joint Spot mit tatsächlichem ΔSNR zur kanonischen Zykluszeit, bei Performance eine erfolgreiche bestätigte Gelegenheit mit tatsächlichem normiertem Target-SNR zur kanonischen Zykluszeit. „Nativ“ bezeichnet damit verarbeitete beibehaltene Evidenz nach Zusammenführung, Zuordnung und wissenschaftlichen Filtern und keine unveränderten Provider-Zeilen. Das fokussierte Messwertrezept enthält weder Mediane oder Quartile zeitlicher Bins noch Dichtegitter, Farbskala, Median des vollständigen Laufs oder gefaltetes Profil. Ergänzende Outcome- beziehungsweise Abdeckungspanels dürfen ihre chronologische Aggregation beibehalten; Segment- und ausgewählte Funkwegrezepte über das vollständige Fenster bleiben unveränderte Dichtezusammenfassungen.

Der kandidatenverknüpfte **`Ausreißerfokus`** verwendet die vollständige beibehaltene Flanke vor dem Ereignis, die geschützte vorläufige Episode und die Flanke danach und darf länger als 24 Stunden sein. Das Benchmark-Overlay verwendet das bereits abgeschlossene Detektormodell, statt auf der fokussierten Teilmenge erneut zu erkennen.

Für jeden gemeldeten Kandidaten, der das Fokusfenster schneidet, markiert es mit demselben `*` jede native Einheit, die gegen die endgültige Baseline und robuste Streuung dieses Kandidaten einzeln sowohl $D_{\min}$ als auch $Z_{\min}$ erfüllt; schwächere gruppierte Einheiten, die zwischen starken Ankern beibehalten werden, bleiben normale Punkte.

Ein dezentes Band **Fokussierte Episode** unterscheidet das berichtete Intervall der beibehaltenen Evidenz des ausgewählten Kandidaten. Der Renderer erweitert jedes Ende um eine halbe Breite der nativen Evidenzeinheit und schneidet das Band am Fokusfenster ab; dadurch bleibt ein Impuls aus einer Einheit sichtbar, ohne eine unbeobachtete physische Dauer oder ein Konfidenzintervall darzustellen.

Erwartetes lokales ΔSNR über den Fokus, die Mediane der Flanken davor und danach über deren jeweilige Stützintervalle, symmetrische Hilfsgrenzen für robuste z-Beträge 1, 2, 3 und $Z_{\min}$ sowie die Grenze der absoluten Abweichung $D_{\min}$ gehören ausschließlich zu dieser fokussierten Episode; ein anderer markierter Kandidat kann eine andere Baseline und robuste Streuung besitzen. Aus der Detektordefinition in [Abschnitt 7.11](#sec-7-11) folgt: Eine Hilfsgrenze des Betrags `k` liegt bei der lokalen Baseline plus oder minus `k × robuste Streuung / 0,6745`. Diese Linien visualisieren Detektorkoordinaten; sie sind weder Standardabweichungen oder Konfidenzintervalle noch eigenständige Qualifikationstests, und das Überschreiten einer einzelnen Hilfslinie reicht nicht zur Qualifikation eines Kandidaten.

Fokusauswahl und Kandidatenprovenienz sind ausschließlich Darstellungszustand; sie verändern weder den abgeschlossenen Analysekontext, die Zuordnung, Zulässigkeit oder Detektorergebnisse oder Provider-Abfrage noch gespeicherte Konfiguration oder öffentliche URL.

<a id="sec-7-8-5"></a>
##### 7.8.5 Deskriptive Streuung und Visualisierungstransformationen

Der IQR zeigt die mittlere Hälfte der beitragenden Werte; Min-Max zeigt deren vollständige Spannweite. Dies sind deskriptive Streuungsmaße und keine Konfidenzintervalle. Zeitliche IQR-Bänder erfordern mindestens fünf beitragende Werte im jeweiligen Bin; der Median bleibt auch bei weniger Werten sichtbar. Leere Bins bleiben fehlend und werden nicht zu künstlichen Nullbeobachtungen.

Was als beitragender Wert zählt, hängt von der Ansicht ab: ein Joint Spot, eine einzelne erfolgreiche normierte Target-SNR-Beobachtung, ein Peer-Median je Bin oder ein Peer-Median je Datum und Stunde gemäß den obigen Definitionen. Für Performance-Entfernungsprofile gilt die gesonderte Drei-Peer-Regel aus [Abschnitt 7.8.1](#sec-7-8-1).

**Dichte und Achsenabstände lesen.** Dichtefarben zeigen, wo sich Werte innerhalb eines Panels häufen; Stützzahlen geben das Evidenzvolumen an. Benchmark-Achsen können die Randbereiche stauchen: Lies deshalb die beschrifteten dB-Koordinaten, statt eine Differenz aus ihrer Bildhöhe abzuleiten. Die folgenden exakten Transformationen verändern die Darstellung, nicht die beibehaltenen Beobachtungen oder deren Mediane und Quartile.

**Dichtezellen und Korrektur.**

Benchmark-Histogramme verwenden normalerweise 1-dB-Klassen, 0,5 dB nur bei einem klaren Halb-dB-Raster und gröbere Klassen bei großen Wertebereichen, damit die Bin-Anzahl begrenzt bleibt. Zeitliche Benchmark-Dichtezellen bleiben 1 dB hoch und folgen der angewandten Referenz-SNR-Korrektur. Für das korrigierte ΔSNR `d` und die numerische Korrektur `c` lautet die ideale Zuordnungsregel in der unkorrigierten Vergleichskoordinate `k = floor(d + c + 0.5)`; die folgende numerische Konvention wertet diese Koordinate mit 0,1 dB Auflösung aus. Zelle `k` ist bei `k - c` zentriert und umfasst das halboffene Intervall `[k - 0.5 - c, k + 0.5 - c)`: Die untere Grenze gehört zur Zelle, die obere zur nächsten Zelle, auch bei negativen Werten. Die Addition von `c` zur Bestimmung der Zugehörigkeit ist ausschließlich eine Koordinatentransformation; sie wendet die Korrektur nicht erneut auf die gespeicherten Beobachtungen, Mediane oder Quartile an. Bei derselben beibehaltenen Population verschiebt eine Änderung von `c` das Dichtegitter gemeinsam mit den korrigierten Beobachtungen; Belegungszahlen der Zellen und Farben der relativen Dichte bleiben erhalten. Nicht ganzzahlige Beobachtungen, einschließlich Vergleichen mit dem lokalen Median, müssen nicht in den Zellzentren liegen.

**Numerische Zellzuordnung.** Ausschließlich für die Zellzuordnung wird `d + c` vor Bestimmung der ganzzahligen Zell-ID auf das nächste Zehntel Dezibel gerundet; bei einem exakten halben Zehntel wird das gerade Zehntel gewählt. Ein ausschließlich an diesen Rundungsmittelpunkten wirksamer Float64-Rundungsfehlerbereich verhindert, dass Korrekturrauschen unterschiedliche Zehntel auswählt. Damit ist die Auflösung der Zuordnung ausdrücklich auf 0,1 dB begrenzt; numerisches Rauschen wie `-0.7000000000000028` bei einem korrigierten Wert, der bei `-0,7 dB` erwartet wird, wird aufgefangen. Unterschiede unterhalb dieser Zuordnungsauflösung können derselben Zelle zugewiesen werden. Exakte Halb-dB-Koordinaten bei dieser Auflösung gehören zur oberen Zelle, auch bei negativen Werten. Die ursprünglichen korrigierten Beobachtungen und ihre Statistiken werden durch diese Gitterkonvention nicht gerundet. Eine nicht ganzzahlige Beobachtung mit voller Präzision kann deshalb bis zu 0,05 dB außerhalb der zugewiesenen Zellgrenze liegen; der Achsenbereich umfasst weiterhin die Beobachtung selbst. Diese zeitliche Darstellungskonvention ersetzt die Ganzzahlrundung zur nächsten geraden Zahl bei Gleichstand; deshalb können sich Zuordnungen exakt auf Halb-dB-Grenzen auch ohne Korrektur ändern. Gewöhnliche Histogramme, Performance-Ansichten und Drill-Down-Abbildungen mit nativen Einzelpunkten bleiben unverändert. Jedes Dichtepanel wird unabhängig normiert:

$$D_{relative}=100\times\frac{n_{cell}}{\max(n_{cell,panel})}$$

Dabei ist $n_{cell}$ die Evidenzanzahl in einer Dichtezelle. Die Division durch die am stärksten belegte Zelle wandelt das Panel in eine Darstellung der relativen Dichte um, ohne die zugrunde liegenden Anzahlen zu verändern.

`100` bezeichnet damit die am stärksten belegte Zelle dieses Panels und nicht 100 % der gesamten Evidenz. Dichtefarben erlauben keinen Vergleich des absoluten Evidenzvolumens zwischen unabhängig normierten Panels; dafür sind die Stützzahlen maßgeblich.

**Achse um den Median.** Zeitliche Benchmark-Ansichten und Histogramme verwenden eine rein darstellungsbezogene monotone Skala, die um den Bereichsmedian $M$ zentriert ist. Bei großer Spannweite liegen gleichmäßige visuelle Schritte bei $M$, $M\pm3$, $M\pm6$, $M\pm10$, $M\pm20$ und $M\pm30$ dB; ein Randanker liegt bei $M\pm60$ dB und wird bei Bedarf fortgesetzt. Wenn jede erforderliche Abweichung höchstens `10 dB` beträgt, lauten die engeren Anker $M$, $M\pm1$, $M\pm3$, $M\pm6$ und $M\pm10$ dB; Fortsetzungsanker liegen bei $M\pm20$ und $M\pm40$ dB. Der erforderliche Bereich umfasst die zutreffenden Rohgrenzen des Histogramms beziehungsweise die durch die Korrektur verschobenen zeitlichen Zellgrenzen, eine Mindesthalbspanne von `3 dB` und den absoluten Wert `0 dB`, damit Target-Referenz-Gleichheit sichtbar bleibt. Die Ankerabbildung verändert ausschließlich die dargestellten Abstände: Rohe ΔSNR-Werte, Bin-Zuordnung, Anzahlen, Mediane und Quartile bleiben unverändert. Wegen der nichtlinearen vertikalen Abbildung ist die **Balkenlänge** entlang der Prozentachse – nicht die dargestellte Fläche – die quantitative Kodierung.

Performance-Ansichten des erfolgreichen SNR bleiben auf einer linearen dB-Achse.
````

</details>


### 7.9 Geografie, Sonnenstandsklassifikation und Populationsfilter

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-9"></a>
#### 7.9 Geografie, Sonnenstandsklassifikation und Populationsfilter

Entfernung und Azimut werden aus dem konfigurierten Target-QTH und den gemeldeten Peer-Locators mit einem kugelförmigen Erdradius von 6371 km berechnet. Die Karte verwendet eine azimutal äquidistante Projektion mit Target-QTH als Mittelpunkt, radialen Grenzen bei 2500, 5000, 10000, 15000, 20000 und 22000 km sowie 22,5-Grad-Azimutsektoren.

Gemeldete Locator repräsentieren Locator-Felder und keine vermessenen Antennenkoordinaten. Geografische Zusammenfassungen sind mit diesen Eingaben intern konsistent, dürfen aber nicht als vermessungsgenaue Position oder direkte Messung des Abstrahlwinkels interpretiert werden.

`Maximale Peer-Entfernung vom Target (km)` entfernt Peers an oder jenseits der gewählten Entfernung vor der wissenschaftlichen Aggregation und dem Export verarbeiteter Evidenz. Kartensegmente, Stützzahlen, Segment-Inspektor und Exporte verwenden damit dieselbe beibehaltene Peer-Population. Inspektor-Auswahlen können diese Population eingrenzen, aber keine ausgeschlossenen Zeilen wiederherstellen.

Zwei Regeln liegen vor diesem geografischen Bereich:

* Die Konditionierung auf Target-Aktivität bleibt global. Ein Peer außerhalb des Bereichs kann den Betrieb des Targets belegen, ohne selbst zu einem begrenzten Outcome zu werden.
* Ist der Ausschluss beweglicher Stationen aktiviert, werden Rufzeichen mit wechselndem Standort in der ansonsten zulässigen globalen Population erkannt, bevor der Entfernungsbereich angewendet wird.

Die Sonnenstandsklassifikation verwendet die Sonnenhöhe am Target-QTH. Evidenz desselben Zyklus verwendet den Zykluszeitstempel.

Sie bezeichnet die Bedingungen am Target, nicht die Beleuchtung des gesamten Ausbreitungswegs oder jedes entfernten Endpunkts.

Die Zeilengrenze der Datenbank und die Bedienelemente, mit denen sich die abgerufene Population verkleinern lässt, sind betriebliche Fragen aus [Abschnitt 5.6](#sec-6-6). Sie verändern die wissenschaftlichen Zusammenfassungen nicht, nachdem die beibehaltene Population gebildet wurde.
````

</details>


### 7.10 Abhängigkeit, Unsicherheit und Geltungsbereich der Validierung

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-10"></a>
#### 7.10 Abhängigkeit, Unsicherheit und Geltungsbereich der Validierung

Die Formeln dieses Kapitels berechnen exakte deskriptive Zusammenfassungen der beibehaltenen Evidenz. Unsicherheit entsteht, wenn daraus Aussagen über nicht beobachtete Bedingungen, künftige Läufe, eine breitere Stationspopulation oder eine physische Ursache abgeleitet werden.

WSPRadar-Beobachtungen sind geclustert und nicht unabhängig. In gewöhnlicher Stationssprache sind 1.000 Spots nicht dasselbe wie 1.000 voneinander unabhängige Experimente. Wiederholte Zyklen eines Peers teilen Hardware- und Funkwegeigenschaften; Stationen in benachbarten Regionen teilen Ausbreitungsbedingungen; Zeit-Bins sind autokorreliert; und ein einzelnes ionosphärisches Ereignis oder eine Störung kann viele Beobachtungen gleichzeitig beeinflussen. Eine große Zeilenzahl ist daher keine unabhängige Stichprobengröße.

Entsprechende Typ-2- und Typ-3-Positionen innerhalb einer Folge können die Evidenztiefe erhöhen, weil jede eine native Vergleichseinheit desselben Zyklus bleibt. Sie liegen jedoch zeitlich eng beieinander, sind voneinander abhängig und dürfen nicht als unabhängige Wiederholungen oder experimentelle Wiederholbarkeit bezeichnet werden. Wiederholbarkeit erfordert einen getrennten, geeignet kontrollierten Lauf.

Stationsgleichgewichtung verringert die Dominanz besonders aktiver Peers, und Mediane verringern die Empfindlichkeit gegenüber einzelnen Ausreißern. Beides erzeugt weder Unabhängigkeit noch beseitigt es systematische Verzerrungen oder liefert eine Stichprobenverteilung. IQRs beschreiben die Streuung innerhalb des Laufs und sind keine Unsicherheitsintervalle.

WSPRadar berichtet derzeit deskriptive Zusammenfassungen. Es passt nicht automatisch ein Stichproben- oder Abhängigkeitsmodell an und berechnet weder Standardfehler, Konfidenzintervalle, p-Werte, Teststärke noch kausale Effekte. Naive Inferenzrechnungen, die jeden Spot oder jedes Paar als unabhängig behandeln, würden die Unsicherheit im Allgemeinen unterschätzen.

Wissenschaftliche Unterstützung sollte deshalb auf mehreren Ebenen beschrieben werden:

* **Evidenztiefe:** Zahl der Gelegenheiten, Joint-Einheiten;
* **Evidenzbreite:** Zahl und geografische Vielfalt der Peer-Identitäten;
* **Konsistenz innerhalb eines Laufs:** Übereinstimmung der stationsgleichgewichteten, beobachtungsbezogenen, geografischen und zeitlichen Zusammenfassungen;
* **experimentelle Wiederholbarkeit:** erneutes Auftreten in einem neuen, geeignet kontrollierten Lauf und
* **experimentelle Kontrolle:** zur Aussage passende Kalibrierung, Kreuztausch, vertauschter Zeitplan oder unabhängige Messung.

Diese Ebenen machen aus den beibehaltenen Zusammenfassungen keine kalibrierten Vorhersagen. Sie zeigen, wie viel Evidenz eine begrenzte deskriptive oder vergleichende Aussage stützt und wie gut der physische Versuch eine Zuordnung zur vermuteten Ursache trägt.

Übereinstimmung mehrerer Ansichten desselben Laufs ist nützliche interne Konsistenz, aber keine unabhängige Wiederholung. Für stärkere Aussagen bleiben ein gesonderter kontrollierter Lauf und der Versuchsaufbau entscheidend; [Kapitel 8](#sec-8) enthält passende Berichtsformulierungen.

Empirische Prüfungen der Softwarevalidierung sind keine zeitlosen Methodendefinitionen. Jede angeführte Validierungskennzahl muss Datensätze, Datum, WSPRadar-Version oder Quellrevision und Berechnungsmethode nennen. Ohne diese Provenienz sollte sie aus dem normativen Handbuch entfernt oder ausdrücklich als datierte Validierungsprüfung gekennzeichnet werden.
````

</details>


### 7.11 Robuste ΔSNR-Ereigniserkennung mit lokaler Basislinie

<details><summary>Verbatim baseline section</summary>

````text
<a id="sec-7-11"></a>
#### 7.11 Robuste ΔSNR-Ereigniserkennung mit lokaler Basislinie

Das Analyseziel des Detektors ist eine vorübergehende gleichgerichtete Abweichung des gepaarten ΔSNR eines Funkwegs von einem stabilen lokalen Erwartungswert. Er erstellt weder eine Rangfolge der größten Rohwerte noch schätzt er eine Ereigniswahrscheinlichkeit. [Abschnitt 2.5](#sec-outlier) erklärt, wann und wie dieses Diagnosewerkzeug fachkundig eingesetzt werden sollte; dieser Abschnitt definiert die exakte wissenschaftliche Konstruktion.

Die Konstruktion erfüllt drei Aufgaben: den üblichen lokalen Unterschied vor und nach einem Kandidaten bestimmen, eine vorübergehende Abweichung finden, ohne dass diese ihre eigene Basislinie verschiebt, und nur ein Intervall melden, das sämtliche Evidenzprüfungen besteht. **Residuum** bedeutet Abweichung von dieser lokalen Basislinie; **robuste Skala** beschreibt die Streuung in ihrer Umgebung; der **robuste z-Wert** setzt die Abweichung zu dieser Streuung ins Verhältnis. Ein großes rohes ΔSNR kann für einen Funkweg völlig üblich sein, während ein Wert nahe null eine erhebliche lokale Änderung darstellt.

Die Notation gilt nur für diesen Abschnitt, abgesehen von den drei bereits in [Abschnitt 4.6](#sec-5-6) eingeführten Symbolen der Bedienelemente: $D_{\min}$ bezeichnet **`Minimale absolute ΔSNR-Abweichung (dB)`**, $Z_{\min}$ bezeichnet **`Minimaler robuster z-Wert`** und $H_{\max}$ bezeichnet **`Maximaler Unterschied zwischen Baseline davor/danach (dB)`**. Keine andere Notation aus Kapitel 7 wird neu definiert.

| Symbol | Englischer Merkbezug und Bedeutung in diesem Abschnitt |
|---|---|
| $i$ | ein exakter Peer-Funkweg mit der Identität `Rufzeichen + Locator` |
| $u$ | eine native gepaarte Einheit: ein Joint Spot aus demselben Zyklus |
| $k$ | Index einer UTC-ausgerichteten 10-Minuten-Baseline-Zelle |
| $D_{i,u}$ | korrigiertes gepaartes ΔSNR Target minus Referenz der Einheit $u$ gemäß Abschnitt 7.5 |
| $\widetilde D_{i,k}$ | ΔSNR-Median in der belegten Baseline-Zelle $k$ |
| $\mathcal{B}_{\mathrm{pre}},\mathcal{B}_{\mathrm{post}}$ | beibehaltene Baseline-Evidenzwerte vor und nach dem Ereignis |
| $B_{\mathrm{pre}},B_{\mathrm{post}},B$ | Baseline vor dem Ereignis, nach dem Ereignis und abschließende lokale Baseline |
| $B^P_{i,k}$ | `B` = Baseline, `P` = Pilot: Pilot-Baseline für Funkweg $i$ und Zelle $k$ |
| $r^P_{i,u},r_{i,u}$ | `r` = residual: Pilot- und abschließendes Residuum der nativen Einheit $u$ |
| $\mathcal{V},S_{\mathrm{robust}}$ | `V` = variability, `S` = scale: zentrierte Stichprobe der Flankenvariabilität und robuste lokale Skala |
| $z_{i,u}$ | robuster z-Wert einer nativen gepaarten Einheit |
| $C_i,G_i,F$ | `C` = cadence, `G` = gap, `F` = floor: typische Funkwegkadenz, größte interne Lücke und vorläufige Gruppierungsuntergrenze |
| $W_i^P,W_i^B$ | `W` = width: Ausschlussbreiten der Pilot- und abschließenden Baseline |
| $E,m_E,z_E,\operatorname{agree}(E)$ | `E` = event, `m` = median, `agree` = agreement: Ereigniskandidat, medianes Residuum, robuster Ereignis-z-Wert und Anteil der Vorzeichenübereinstimmung |
| $\varepsilon$ | feste Vergleichstoleranz von `0.01 dB` für die Mindestabweichung und den maximalen Baseline-Unterschied |

Der Detektor verwendet $\varepsilon=0.01\ \mathrm{dB}$ ausschließlich beim Vergleich einer absoluten Abweichung mit $D_{\min}$ oder eines Baseline-Unterschieds davor/danach mit $H_{\max}$. Interne Evidenzwerte und konfigurierte Schwellen werden dabei nicht gerundet. Dieselbe Toleranz gilt für die Ereignisqualifikation, starke Grenzanker und einzeln qualifizierende native Einheiten. Robuste z-Werte, die MAD/IQR-Skalenschätzung und die Regeln zur Vorzeichenübereinstimmung bleiben unverändert; für den Vergleich des robusten z-Werts gilt keine Toleranz.

**1. Evidenz und Auflösung.** Nur native gepaarte Einheiten liefern ΔSNR-Werte für den Detektor. Einseitige Outcomes besitzen keinen gepaarten Wert und können kein Ereignis qualifizieren; ihre Zeitpunkte tragen jedoch zur Kadenzschätzung bei, und die Outcomes bleiben Diagnosekontext. Die Erkennung läuft für jeden Funkweg $i$ getrennt und vor der Darstellungsaggregation der **Zeitlichen Evidenz**. Ein anderes Darstellungs-Bin kann deshalb kein Ereignis erzeugen, zusammenführen, teilen oder entfernen. Ist **`ΔSNR-Ausreißerkandidaten melden`** ausgeschaltet, wird der Detektor nicht ausgeführt, und dem Ergebnis werden keine Ausreißerbegriffe hinzugefügt.

Für die Schätzung von Baseline und robuster Skala werden die nativen Werte zu $\widetilde D_{i,k}$ reduziert. Kandidatengruppierung und berichtete Grenzen behalten die Zeitpunkte der nativen gepaarten Einheiten.

**2. Stabile lokale Baseline und robuste Variabilität.** Für den geprüften Kandidaten untersucht der Detektor belegte 10-Minuten-Zellen bis zu sechs Stunden davor und sechs Stunden danach. Der Kandidat und seine Ausschlussbreite werden ausgelassen. Jede Flanke muss mindestens vier belegte Zellen enthalten; fehlende Zellen werden niemals ergänzt. Die beibehaltenen Zellenwerte bilden $\mathcal{B}_{\mathrm{pre}}$ und $\mathcal{B}_{\mathrm{post}}$:

$$
B_{\mathrm{pre}}=\operatorname{median}(\mathcal{B}_{\mathrm{pre}}),\qquad
B_{\mathrm{post}}=\operatorname{median}(\mathcal{B}_{\mathrm{post}})
$$

Das abschließende erwartete lokale ΔSNR gewichtet beide Flanken gleich, während das Stabilitätskriterium ihre Abweichung begrenzt:

$$
B=\frac{B_{\mathrm{pre}}+B_{\mathrm{post}}}{2},\qquad
\left|B_{\mathrm{pre}}-B_{\mathrm{post}}\right|\leq H_{\max}+\varepsilon
$$

Die gleiche Gewichtung verhindert, dass die Flanke mit mehr belegten Zellen dominiert. Fehlt einer Flanke die erforderliche Stützung oder scheitert das Stabilitätskriterium, bleibt der Funkweg für diesen Kandidaten unklassifiziert, und es wird kein Ereignis berichtet.

Damit eine Verschiebung der Baseline nicht als Rauschen behandelt wird, wird jede Flanke zur Messung der nahen Variabilität um ihre eigene Baseline zentriert. Geschweifte Klammern und Vereinigung bedeuten hier zusammengeführte Evidenzstichproben mit beibehaltenen Wiederholungen: Jedes beibehaltene Zellenresiduum trägt bei, auch wenn eine andere Zelle denselben Wert hat:

$$
\mathcal{V}=\left\{x-B_{\mathrm{pre}}:x\in\mathcal{B}_{\mathrm{pre}}\right\}
\cup\left\{x-B_{\mathrm{post}}:x\in\mathcal{B}_{\mathrm{post}}\right\}
$$

Die Skala beschreibt die typische absolute Streuung der zentrierten Flankenwerte in dB. Zunächst verwendet der Detektor deren mediane absolute Abweichung (MAD); bei null den halben Interquartilsabstand (IQR), und nur wenn beide null sind einen festen Ersatzwert:

$$
S_{\mathrm{robust}}=
\begin{cases}
\operatorname{MAD}(\mathcal{V}), & \operatorname{MAD}(\mathcal{V})>0,\\
\frac{1}{2}\operatorname{IQR}(\mathcal{V}), & \operatorname{MAD}(\mathcal{V})=0\ \land\ \operatorname{IQR}(\mathcal{V})>0,\\
0.5\ \mathrm{dB}, & \operatorname{MAD}(\mathcal{V})=0\ \land\ \operatorname{IQR}(\mathcal{V})=0.
\end{cases}
$$

MAD ist der Median der absoluten Abstände vom Stichprobenmedian; IQR ist der Abstand zwischen dem 25. und 75. Perzentil. Der Ersatzwert `0.5 dB` verhindert eine Division durch null, wenn beide Maße verschwinden; positive MAD- oder Halb-IQR-Werte unter `0.5 dB` bleiben erhalten. Das Abziehen der Baseline liefert ein Residuum in dB; die Division durch die robuste Skala und der konventionelle Faktor ergeben einen dimensionslosen Wert:

$$
r_{i,u}=D_{i,u}-B,\qquad
z_{i,u}=0.6745\frac{r_{i,u}}{S_{\mathrm{robust}}}
$$

Ein positives Residuum liegt über dem erwarteten lokalen ΔSNR Target minus Referenz, ein negatives darunter. Gruppierung und Qualifikation richten sich nach diesem Vorzeichen und nicht nach dem Vorzeichen des Rohwerts $D_{i,u}$ relativ zu `0 dB`. Der Faktor `0.6745` liefert die konventionelle Skalierung des modifizierten Werts, wenn MAD aktiv ist. Der Wert bleibt deskriptiv und ist weder eine kalibrierte Wahrscheinlichkeit noch ein p-Wert oder ein gaußsches Signifikanzniveau.

**Beispiel: positives ΔSNR, negative Abweichung.** Liegt die stabile lokale Baseline bei `+8 dB` und ein Joint Spot bei `+1 dB`, beträgt sein Residuum `-7 dB`. Das Target ist in diesem Spot weiterhin stärker als die Referenz, aber deutlich weniger als auf diesem Funkweg üblich. Bei einer robusten Skala von `1 dB` beträgt der robuste z-Wert ungefähr `-4,72`. Diese Rechnung allein erzeugt noch kein gemeldetes Ereignis: Flankenstützung, Baseline-Stabilität, Kriterien auf Ereignisebene, Vorzeichenübereinstimmung und beibehaltene Grenzanker müssen ebenfalls passen.

**3. Kadenzabhängige Pilotgruppierung.** Die typische Funkwegkadenz $C_i$ wird in Minuten aus eindeutigen Zeitpunkten zulässiger gepaarter und einseitiger Outcomes geschätzt. Positive Intervalle bis einschließlich 45 Minuten werden beibehalten; wenn mindestens zwei verbleiben, definiert ihr Median die Kadenz. Andernfalls liefert die konfigurierte Kadenz gepaarter Einheiten den Wert $C_i$. Die größte interne Lücke ist:

$$G_i=\min\left(45,\max\left(15,1.5C_i\right)\right)\ \mathrm{minutes}$$

Damit erhalten dünn belegte Funkwege einen kadenzabhängigen Gruppierungsspielraum; kein Ereignis kann jedoch mehr als 45 Minuten überbrücken, und keine geschätzte Kadenz verkleinert den Spielraum auf weniger als 15 Minuten.

Um Kandidaten zu bilden, ohne dass der geprüfte Punkt seinen eigenen Erwartungswert bestimmt, erhält jede unterstützte Zelle eine Pilot-Baseline $B^P_{i,k}$. Deren Ausschlussbreite und die bewusst niedrige Gruppierungsuntergrenze sind:

$$
W_i^P=\max(60,2C_i)\ \mathrm{minutes},\qquad
F=\min(1\ \mathrm{dB},D_{\min}-\varepsilon)
$$

Der Term `1 dB` bleibt exakt: Die Toleranz geht nur über die tolerierte Mindestabweichung in diese frühe Gruppierungsregel ein, damit die Gruppierung keine strengere Abweichungsanforderung als die abschließende Qualifikation stellt. Sie wird weder vom festen Term `1 dB` noch vom unten beschriebenen `1-dB`-Kriterium zur Erweiterung der Ereignisränder abgezogen.

Die Pilot-Anpassung verwendet dieselbe Flankenreichweite von sechs Stunden, mindestens vier belegte Zellen auf jeder Seite und das Stabilitätskriterium $H_{\max}$. Eine native Einheit $u$ in Zelle $k(u)$ erhält nur dann ein Pilot-Residuum, wenn diese Zelle gestützte Flanken besitzt:

$$r^P_{i,u}=D_{i,u}-B^P_{i,k(u)}$$

Nahe Pilot-Residuen desselben Vorzeichens und mit einem Betrag von mindestens $F$ bilden ein vorläufiges Ereignis. Die Gruppierung endet bei einer Lücke größer als $G_i$, einer Einheit mit entgegengesetztem Vorzeichen oder einer gestützten Rückkehr zur Baseline. Eine einzelne gestützte neutrale Einheit darf die Evidenz überbrücken, wenn sich die gleichgerichtete Abweichung fortsetzt; eine zweite aufeinanderfolgende gestützte neutrale Einheit beendet das Ereignis. Nicht gestützte Einheiten bleiben unklassifiziert und werden nicht ergänzt. Die niedrige Gruppierungsuntergrenze findet Kontinuität; sie lockert die abschließende Qualifikation nicht.

**4. Kandidatenausschließende abschließende Baseline.** Das vollständige vorläufige Ereignis wird mit folgender Breite aus der abschließenden Baseline-Anpassung ausgeschlossen:

$$W_i^B=\max(10,C_i)\ \mathrm{minutes}$$

Die abschließende Anpassung verwendet die Baseline- und robuste Skalenkonstruktion aus Schritt 2. Gegenüber dieser gemeinsamen abschließenden Baseline dürfen gleichgerichtete Ränder mit einem Residuumbetrag von mindestens `1 dB` das Ereignis in bis zu drei Durchgängen erweitern. Das vollständige erweiterte Intervall bleibt bei jeder erneuten Anpassung ausgeschlossen, damit der Kandidat seinen eigenen Erwartungswert nicht in Richtung der Auslenkung zieht.

**5. Qualifikation, Prüfung eines starken Kerns und berichtete Grenzen.** Für einen verfeinerten Ereigniskandidaten $E$ sind sein medianes Residuum, sein robuster Ereignis-z-Wert und der Anteil der Vorzeichenübereinstimmung definiert als:

$$
m_E=\operatorname{median}_{u\in E}(r_{i,u}),\qquad
z_E=0.6745\frac{m_E}{S_{\mathrm{robust}}}
$$

$$
\operatorname{agree}(E)=
\frac{\left|\left\{u\in E:\operatorname{sign}(r_{i,u})=\operatorname{sign}(m_E)\right\}\right|}{|E|}
$$

Der Ereignismedian beschreibt die typische Abweichung und nicht den größten Einzelpunkt. Der Nenner der Vorzeichenübereinstimmung umfasst alle beibehaltenen nativen Einheiten dieses Kandidaten einschließlich neutraler Brücken. Mindestens zwei Drittel müssen dasselbe Vorzeichen wie das mediane Residuum besitzen. Zur Qualifikation müssen alle vier Bedingungen gemeinsam gelten: genügend Abweichung in dB, genügend Abweichung relativ zur lokalen Streuung, vereinbare Baselines davor und danach sowie ausreichende Vorzeichenübereinstimmung:

$$
|m_E|\geq D_{\min}-\varepsilon,\qquad
|z_E|\geq Z_{\min},\qquad
\left|B_{\mathrm{pre}}-B_{\mathrm{post}}\right|\leq H_{\max}+\varepsilon,\qquad
\operatorname{agree}(E)\geq\frac{2}{3}
$$

Für jede Dauer und jede spätere Klasse gelten dieselben Kriterien. Es gibt weder einen Dauerbonus noch eine Absenkung der Schwellen aufgrund angesammelter Evidenz oder eine schwächere Schwelle für ein anhaltendes Ereignis.

Kann das vollständige verfeinerte Ereignis kein qualifiziertes, stark verankertes Intervall liefern, wird es an Rückkehrpunkten zur abschließenden Baseline in zusammenhängende gleichgerichtete Abschnitte ohne neutrale Überbrückung geteilt. Jeder Abschnitt wird anhand derselben Kriterien geprüft; dabei werden die abschließende Baseline, die robuste Skala und die Flankenstützung des vollständigen Kandidaten wiederverwendet. So kann ein durch schwache umgebende Evidenz verdeckter starker Kern erhalten bleiben, ohne dass der kleinere Abschnitt eine günstigere Referenz auswählen kann.

Nach der Qualifikation ist eine native Einheit nur dann ein starker Grenzanker, wenn:

$$
\operatorname{sign}(r_{i,u})=\operatorname{sign}(m_E),\qquad
|r_{i,u}|\geq D_{\min}-\varepsilon,\qquad
|z_{i,u}|\geq Z_{\min}
$$

Das berichtete Intervall wird auf den ersten und letzten starken Anker gekürzt. Bereits dazwischen gruppierte Einheiten bleiben interne Evidenz, auch wenn sie einzeln eine Anker-Schwelle verfehlen. Das gekürzte Intervall wird mit derselben abschließenden Baseline, robusten Skala und Flankenstützung neu aufgebaut und nochmals gegen alle Kriterien auf Ereignisebene geprüft. Schwache führende und nachlaufende Einheiten entfallen; schwächere interne Brücken können bestehen bleiben. Ein verbleibender Anker wird zum Spot-Impuls. Besteht kein stark verankertes Intervall die Prüfung, wird kein Ereignis berichtet. Die niedrige Gruppierungsuntergrenze und die höheren Anforderungen an die Grenzen erzeugen somit hysteretische Ereignisgrenzen.

Praktisch dürfen schwache Punkte den Zusammenhang innerhalb eines Ereignisses erhalten; dessen berichteten Anfang und Schluss dürfen jedoch nur einzeln starke Punkte festlegen.

Der Marker im Zeitplot aller Funkwege wird nur aus diesen starken Ankern ausgewählt: Innerhalb jedes funkwegübergreifenden Prüfereignisses liefert die einzeln qualifizierende native Einheit mit dem betragsmäßig größten Residuum das `*`. Eine ungestützte oder nicht qualifizierende Episodenspitze kann nicht zu diesem Plot-Repräsentanten werden. Die Markerauswahl ist von der Berichtsgröße **Größte Einzelzyklusabweichung** getrennt; diese bleibt für Bericht und Export das tatsächliche betragsmäßig größte beibehaltene Residuum jedes Funkwegereignisses.

**6. Deskriptive Klasse und funkwegübergreifender Kontext.** Die Klassifikation erfolgt nach der Kürzung:

* **Spot-Impuls:** eine beibehaltene native gepaarte Einheit;
* **Anhaltende Auslenkung:** mindestens drei beibehaltene native gepaarte Einheiten über eine Spanne von mindestens 30 Minuten und
* **Kurzer Ausbruch:** jedes andere beibehaltene Ereignis aus mehreren Einheiten.

Die Klassen beschreiben die zeitliche Form der Evidenz und verändern die Qualifikation nicht. Das angezeigte Intervall von der ersten bis zur letzten Einheit umspannt beobachtete beibehaltene Einheiten; es weist kein ununterbrochenes Verhalten zwischen ihnen nach.

Funkwegereignisse qualifizieren sich unabhängig. Gleichgerichtete Ereignisse erscheinen in einer gemeinsamen Prüfkarte, wenn sie sich überschneiden oder höchstens um den größeren Wert aus 10 Minuten und der halben konfigurierten Kadenz gepaarter Einheiten getrennt sind. Der Kontext lautet bei einem Funkweg funkwegspezifisch, bei mehreren Funkwegen in benachbarten Kompasssektoren richtungskohärent, bei mehreren getrennten Richtungen bereichsweit oder mehrere Funkwege, wenn für mindestens einen Beitragenden keine Richtung verfügbar ist. Der funkwegübergreifende Kontext verändert die Qualifikation eines Funkwegs nicht und ist keine Berechnung von Unabhängigkeit oder Signifikanz.

Die Zerlegung in Target und Referenz sowie nahe einseitige Outcomes bleiben interne Diagnoseangaben und lassen sich über die gepaarte Evidenz und den Drill-Down untersuchen. Sie qualifizieren, verlängern oder verstärken ein Ereignis nicht. Der Detektor ist somit ein deterministischer deskriptiver Klassifikator der beibehaltenen gepaarten Evidenz. Seine Ereigniszahl ist keine unabhängige Stichprobengröße; er nimmt keine Signifikanzkorrektur für mehrere Ereignisse vor, und eine kausale Zuordnung erfordert weiterhin die in den Kapiteln 2, 3 und 8 beschriebene Versuchskontrolle.
````

</details>


## Section disposition and bilingual review

The initial reviewed English content master had SHA-256 `de64a2ed752cf506d55295489acd231a56cb4184727f7fd06563c4f031bc9308`. An independent source-and-code review found no substantive calculation error or critical scientific omission. Bilingual review then made the shared Section 7.3 wording explicit: an out-of-scope activity witness establishes activity without entering that scope's outcomes; an in-scope witness is not thereby excluded. The final English source and matching German target hashes are recorded below.

| Original section | Disposition and authoritative destination |
|---|---|
| Chapter 7 introduction | Condensed into the radio questions and the observation-to-summary sequence. Removed the up-front symbol inventory and five-column method matrix; the same units, eligibility and weighting are defined where used in Sections 7.1–7.8. No new appendix. |
| 7.1 | Retained database provenance, two-minute cycle, exact remote identity, same-cycle matching, extended-message limits and historical fallback. Removed duplicated notation and repeated setup guidance; operating guidance remains in Chapters 0/2 and Appendix B. |
| 7.2 | Retained the role-specific identity table, full-locator/grid-4 distinction, geometry, database identity requirements and strongest-report versus neighborhood-median distinction. Consolidated the best-observed-reception justification and its asymmetry limitation. |
| 7.3 | Retained direction-specific Target activity, geographic ordering, mode-specific population-filter ordering and asymmetric Reference treatment. Replaced symbolic conditioning with one compact table and its consequences. |
| 7.4 Performance | Moved to visible Section 7.5, preserving the semantic compatibility anchor `sec-7-4`. Replaced Boolean notation and six statistical equations with direction-specific endpoint evidence, a four-row decision table, one Decode Rate equation and the 90/100 versus 5/10 example. Retained qualification, both weightings, Reach, successful-SNR selection and inference limits. |
| 7.5 normalization and Benchmark | Moved to visible Section 7.4, preserving `sec-7-5`. Retained three useful equations with descriptive subscripts, units, correction sign and worked arithmetic. Retained the reported-power limitation and RX/TX distinction. Updated the TOC and coupled visible cross-references in both manuals. |
| 7.6 | Retained Joint, one-sided and asynchronous categories, non-random Joint selection, no artificial missing-side SNR, Target asymmetry and compound-callsign hash risks. Condensed repeated statements and linked the existing preflight guidance. |
| 7.7 | Retained exact-identity qualification, median-of-station-medians versus pooled Joint Spots, map support, neighborhood construction and changing-membership effects. Preserved the +6/-2/-1, JO31AA/JO31AB and local -18/-12/-6 examples. Replaced indexed aggregation notation with the actual calculation sequence. |
| 7.8.1 | Retained map population, distance bins, non-filled gaps, station-balanced successful SNR and the three/two/one-value spread rules. Removed repeated view-control narration. |
| 7.8.2 | Replaced split-vote symbols and JES equations with exact station and outcome definitions. Added the approved 80/100 versus 1/10 example (45% versus 73.6%). Retained one-sided-only contributors, absent-station treatment, support-bar meaning and Target asymmetry. |
| 7.8.3 | Consolidated chronological and folded definitions, baseline deviations, support and denominators. Preserved unequal station/date weighting, represented-date empty slots, partial-hour treatment and two-date eligibility. Clarified against code that Benchmark coverage can have two dates while its Joint-SNR layer has only one. |
| 7.8.4 | Retained native-versus-aggregated evidence, selected-identity scope and no re-fitting in focused views. Detailed focus-window/marker/guide operation remains in Section 2.5. Engineering state/renderer names remain in `docs/architecture.md` and the implementation. |
| 7.8.5 | Retained IQR support, panel-relative color, histogram/temporal-cell widths, correction invariance, nonlinear-axis interpretation and unchanged scientific statistics. Private 0.1 dB lattice tie-breaking and numerical axis-anchor arrays are omitted from the manual; their exact behavior remains in `docs/architecture.md`, `ui/plots/evidence_figures.py` and corresponding regression tests. |
| 7.9 | Condensed geometry and filtering prose while retaining Earth radius, map boundaries, azimuth width, strict distance exclusion, global moving-station identification and Target-QTH solar scope. |
| 7.10 | Consolidated dependence, descriptive versus inferential meaning, evidence depth/breadth/consistency/repeatability/control and dated validation provenance. Removed repeated warnings without expanding the supported claims. |
| 7.11 | Replaced the symbol glossary and 13 displayed equations with an example, staged explanation and compact definition/qualification tables. Retained baseline support, scale fallback, cadence/grouping, exclusion/refit, qualification/tolerance, strong-core rescue, boundary trimming, class/context rules and marker-versus-peak distinction. Existing engineering descriptions in `docs/architecture.md` already cover detector mechanics. No formal appendix was added. |

The private method tag `opportunity-v3` is removed from the end-user method explanation. The executable identifier remains unchanged in code and supported provenance; the scientific success/opportunity/Miss definition remains in visible Section 7.5. Reference titles, URLs, supported public identifiers, unaffected chapters and runtime behavior are retained.

`AGENTS.md` now requires precise scientific explanation without requiring a displayed formula or a formal appendix. It explicitly preserves useful normalization/correction/Delta-SNR equations, scientific qualifications, bilingual parity and the existing restructuring verification requirements.

### Final bilingual parity and verification

Source model: source-led English master, translated and independently reviewed German target.

- Final English file SHA-256: `dc508f5b17c1659730bc7e509dd4cb8e57008a219e35f6faab40de734abbc6fd`.
- Final German file SHA-256: `6ad9daedd5342ad6851d2d4655a76bc4a59a40bda4f94bb75f9515f9d66ade58`.
- Independent section-by-section scientific and semantic parity review passed. It covered exact endpoint identity, Target activity and filter ordering, self-confirming successes, one-sided outcomes, missing SNR, all weighting/denominators, folded-date populations, neighborhood construction, and detector qualification/boundary rules.
- Source-only omissions, target-only additions and unresolved conflicting scientific statements: none found in Chapter 7. Intentional localization: German narrative and established UI labels; German wording in the Decode Rate equation; the three SNR equations retain shared mathematical symbols. German `1000 km` avoids a comma being read as a decimal separator.
- Both languages retain all original anchors without duplicates. Compatibility anchors `sec-7-5` and `sec-7-4` continue to identify normalization/Benchmark and Performance respectively, despite their visible order changing. Every internal link resolves.
- Approximate Chapter 7 whitespace-delimited source-word counts, excluding its opening anchor: English 9,889 to 6,620; German 9,909 to 6,559. Both reduce 30 displayed equations to four. Word counts are a readability measurement, not a completeness criterion.
- Focused documentation/rendering verification: 130 tests passed. Initial stale prose, obsolete matrix and CSS-punctuation assertions were updated while preserving the scientific and rendering contracts.
- Final manuals generated successfully: English 76 pages, German 86 pages. Chapter 7 pages were visually inspected with Poppler renders (English pages 45–59 and German pages 52–67). Two long German detector-table labels received print-only line breaks, preserving the source prose and English output. The German PDF was regenerated and its affected pages 64 and 66 visually rechecked; no label collision remains.

Full verification used the checked-in foreground Windows runner, `scripts/run_regression.cmd`: **3,500 passed, 3 failed, 3 xfailed**, in 623.26 seconds. The three failures are outside this documentation change:

- `test_guided_input_integration.py::test_reference_intro_avoids_repeated_metric_definitions_preserved_in_results[en/de]` expects a marked SNR definition absent from the existing result-guidance copy.
- `test_idle_import_boundary.py::test_idle_browser_component_payloads_preserve_json_transport` expects a navigation JSON payload without the existing `panelKey: null` field.

The affected test files and their runtime inputs (`i18n.py`, `ui/page_navigation.py`, `ui/documentation_scroll_trigger.py`, `ui/url_synchronizer.py`) were verified unchanged against baseline HEAD with `git diff --exit-code`. No analysis calculation, configuration, provider or scientific export code changed. The existing Matplotlib pending-deprecation warning also remains. The full run is therefore not reported as green.

Full repository Python compilation passed. README matches the output of `build_readme_text(DOC_EN)` exactly; patch whitespace checks passed. After the bounded PDF-only follow-up, both affected Python files compiled and the complete documentation subset passed again: **131 passed in 16.03 seconds**. The full suite was not repeated for that localized presentation follow-up, in line with the proportional verification policy.

No live provider run, deployment or manual browser walkthrough was performed; those runtime behaviors were not changed. Markdown/HTML math rendering, link targets, PDF generation and the affected layout were verified through the focused tests and rendered PDF inspection. Task-specific temporary PDF, PNG and baseline-copy artifacts were removed after review; the original passages and their disposition remain preserved in this ledger.
