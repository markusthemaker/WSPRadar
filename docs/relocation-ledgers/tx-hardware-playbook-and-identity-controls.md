# TX Hardware playbook and identity-control cleanup

## Scope

This change strengthens the simultaneous TX explanation, clarifies that
sequential TX can use one shared transmitter or two non-overlapping transmitter
chains, adds calibration guidance based on the variable under test, and shortens
the Core and Benchmark control descriptions. English and German were changed in
parallel.

The former `sec-2-4-why` compatibility anchor remains at the start of the
sequential playbook even though its visible heading and duplicated rationale
were removed.

## Removed or replaced passages

### Section 1.4 — comparison-method table

Original English passages replaced:

> | **Simultaneous TX** | Each joint Delta SNR compares the Target and Reference at the same remote receiver in the same UTC cycle, strongly reducing temporal path variation within that pair. | Requires two distinguishable transmitter chains, exact power/correction control, separate callsigns and separated frequencies. Coupling, intermodulation, near/far effects and chain differences can bias the result. It compares the documented complete transmit paths, not automatically the antennas alone. |
>
> | **Sequential TX** | Can retain one transmitter, waveform, callsign and frequency reference while a controlled switch alternates the two RF paths; simultaneous-transmitter coupling is avoided. | The two observations are time-separated. Short, balanced alternation reduces but cannot eliminate propagation, interference, schedule and switching differences. |

Disposition: replaced with a more precise same-receiver, same-cycle explanation
and its frequency-selective-QRM limitation. `Waveform` was removed, and the
sequential row now states the supported hardware distinction: one transmitter
switched between two RF paths or two transmitter chains on non-overlapping
schedules. An A/B comparison still always has two RF paths.

Original German passages replaced:

> | **Simultanes TX** | Jedes gemeinsame Delta SNR vergleicht Target und Referenz am selben entfernten Empfänger im selben UTC-Zyklus. Dadurch wird die zeitliche Funkwegvariation innerhalb dieses Paars stark reduziert. | Erfordert zwei unterscheidbare Sendeketten, genaue Kontrolle von Leistung und Korrektur, getrennte Rufzeichen sowie getrennte Frequenzen. Kopplung, Intermodulation, Nah-/Fern-Effekte und Kettenunterschiede können das Ergebnis verzerren. Verglichen werden die dokumentierten vollständigen Sendepfade, nicht automatisch nur die Antennen. |
>
> | **Sequenzielles TX** | Ein Sender, eine Signalform, ein Rufzeichen und eine Frequenzreferenz können gemeinsam bleiben, während ein kontrollierter Umschalter zwischen den beiden HF-Pfaden wechselt; eine Kopplung zwischen gleichzeitig aktiven Sendern wird vermieden. | Die beiden Beobachtungen sind zeitlich getrennt. Kurzes, ausgewogenes Abwechseln verringert Unterschiede durch Ausbreitung, Störungen, Zeitplan und Umschaltung, kann sie aber nicht beseitigen. |

Disposition: German parity with the English replacement.

### Section 1.4.1 — former two-chain control paragraph

Original English passage not retained verbatim:

> Measure or defensibly correct the power difference between the complete Target and Reference paths. Also control antenna coupling, transmitter isolation, harmonics/intermodulation, clock alignment and uploaded identities. A 100 Hz audio/RF separation is negligible as a propagation-frequency difference on an HF band, but receiver passband shape, local interference and frequency-specific transmitter response can still create a systematic offset. For a small claimed difference, repeat with the Target/Reference frequency assignments exchanged, or otherwise characterize that offset.

Disposition: replaced at the user's request with guidance that places TX-power
and feedline calibration at the comparison point appropriate to the variable
under test. Coupling, isolation, intermodulation and identity controls remain in
the method table, the surrounding simultaneous-TX setup, and Appendix A. The
scientific limitation from frequency-selective interference remains in Sections
1.4, 6.3 and 7.7.

Original German passage not retained verbatim:

> Miss den Leistungsunterschied zwischen den vollständigen Target- und Referenzpfaden oder korrigiere ihn auf belastbare Weise. Kontrolliere außerdem Antennenkopplung, Senderisolation, Oberwellen und Intermodulation, Uhrensynchronisation sowie die hochgeladenen Identitäten. Ein Abstand von 100 Hz im Audio- beziehungsweise HF-Signal ist auf einem HF-Band als Ausbreitungsfrequenzunterschied vernachlässigbar; Form des Empfängerdurchlassbereichs, lokale Störungen und der frequenzabhängige Sendergang können dennoch einen systematischen Versatz verursachen. Ist ein kleiner beobachteter Unterschied entscheidend, wiederhole den Versuch mit vertauschten Target-/Referenz-Frequenzzuordnungen oder charakterisiere diesen Versatz auf andere Weise.

Disposition: German parity with the English replacement.

### Section 1.4.2 — former deterministic-alternation rationale

Original English passage removed:

> **Why deterministic alternation is used**
>
> When two nearby antennas radiate the same WSPR waveform and callsign in the same cycle and frequency channel, a remote receiver observes their combined field. Its spot cannot identify how much came from the Target or Reference path. Distinguishable simultaneous signals require separate callsigns and separated frequencies, normally with separate transmitter chains; the simultaneous playbook above states the resulting calibration and isolation requirements.
>
> Deterministic alternation instead retains one callsign and preferably one common transmitter chain while exposing both paths repeatedly to changing propagation and receiver conditions. It remains a sequential comparison: shorter separation reduces the time available for conditions to change, but does not make the observations simultaneous.

Disposition: duplicated explanation removed at the user's request. The
same-frequency collision is still explained in Section 1.4.1, while the
sequential timing boundary remains in Sections 1.4, 1.4.2 and 7.7. The invisible
compatibility anchor was retained.

Original German passage removed:

> **Warum deterministisches Abwechseln verwendet wird**
>
> Senden zwei nahe beieinanderstehende Antennen im selben WSPR-Zyklus und Frequenzkanal dieselbe WSPR-Aussendung mit demselben Rufzeichen, empfängt eine entfernte Station die Überlagerung beider Felder. Ihr Spot lässt nicht erkennen, welcher Anteil vom Target- oder Referenzpfad stammt. Unterscheidbare simultane Signale erfordern getrennte Rufzeichen und getrennte Frequenzen, normalerweise mit getrennten Sendeketten; der Leitfaden für simultanes TX oben nennt die daraus folgenden Anforderungen an Kalibrierung und Isolation.
>
> Ein deterministischer Wechsel behält dagegen ein Rufzeichen und vorzugsweise eine gemeinsame Sendekette bei, während beide Pfade wiederholt wechselnden Ausbreitungs- und Empfangsbedingungen ausgesetzt werden. Der Vergleich bleibt sequenziell: Ein kürzerer Abstand verringert die Zeit, in der sich die Bedingungen ändern können, macht die Beobachtungen aber nicht simultan.

Disposition: German parity with the English removal.

### Section 4.2 — callsign and QTH descriptions

Original English table passages replaced:

> | **Your Callsign (Receiver under Test)** / **Your Callsign (Transmitter under Test)** | blank | Direction-specific exact Target callsign. Accepted syntax is 3 to 15 ASCII characters. `/` may separate non-empty alphanumeric prefix or suffix segments. One optional terminal `-` may introduce a non-empty alphanumeric suffix. At least one segment before the hyphen suffix must contain both a letter and a digit. |
>
> | **QTH Locator (4 or 6 chars)** | blank | Valid four- or six-character Maidenhead locator: two letters `A-R`, two digits, and optionally two subsquare letters `A-X`. The complete value is the map center, local-radius origin and geographic calculation input; its first four characters constrain Target matching in Success and Compare. Reference Station uses a separately entered Reference Grid-4, while Hardware A/B derives both displayed grid-4 fields from this Target QTH. |

Original English paragraph removed:

> Callsign and QTH text is normalized to uppercase. A non-empty malformed Target or Reference value produces a field-specific validation message, and invalid values are rejected when a run or configuration is submitted. Callsign validation establishes plausible archive-token syntax; it cannot verify that a callsign is legally assigned or that the station actually used it.

Disposition: the table now gives the concise operator meanings requested. The
normalization and generic validation narration was removed as self-evident UI
behavior. The non-obvious exact-archive-identity and grid-4 matching guidance
remains immediately below the table and in troubleshooting Section 5.3.

Original German table passages replaced:

> | **Dein Rufzeichen (Empfänger im Test)** / **Dein Rufzeichen (Sender im Test)** | leer | Exaktes Target-Rufzeichen für die gewählte Richtung. Zulässig sind 3 bis 15 ASCII-Zeichen. `/` darf nicht leere alphanumerische Präfix- oder Suffixsegmente trennen. Ein optionales abschließendes `-` darf ein nicht leeres alphanumerisches Suffix einleiten. Mindestens ein Segment vor dem Bindestrich-Suffix muss sowohl einen Buchstaben als auch eine Ziffer enthalten. |
>
> | **QTH-Locator (4 oder 6 Zeichen)** | leer | Gültiger vier- oder sechsstelliger Maidenhead-Locator: zwei Buchstaben `A-R`, zwei Ziffern und optional zwei Unterfeldbuchstaben `A-X`. Der vollständige Wert dient als Kartenmittelpunkt, Ursprung des lokalen Radius und Eingabe geografischer Berechnungen; seine ersten vier Zeichen begrenzen die Target-Zuordnung in Success und Compare. Die Referenzstation verwendet ein separat eingegebenes Referenz-Grid-4, während Hardware A/B beide angezeigten Grid-4-Felder aus diesem Target-QTH ableitet. |

Original German paragraph removed:

> Rufzeichen- und QTH-Eingaben werden in Großbuchstaben normalisiert. Ein nicht leerer, fehlerhafter Target- oder Referenzwert erzeugt eine feldbezogene Validierungsmeldung; ungültige Werte werden beim Start eines Laufs oder beim Einreichen einer Konfiguration abgelehnt. Die Rufzeichenprüfung bestätigt eine plausible Syntax für ein Archiv-Token, nicht die rechtmäßige Zuteilung des Rufzeichens oder dessen tatsächliche Verwendung durch die Station.

Disposition: German parity with the English replacement and removal.

### Section 4.3 — Reference correction and identity rows

Original English passages replaced:

> | **Reference SNR Correction (dB)** | `0.0`; `-99.9` to `+99.9` in `0.1 dB` steps | Appears for Compare and is hidden for Success-only. The value is added to the Reference-side SNR before Delta SNR is calculated. |
>
> | **Target Callsign** | value from Core Parameters; read-only | Appears in the fixed-reference identity block for Reference Station, RX Hardware A/B and simultaneous TX Hardware A/B. It makes the Target side explicit without creating a second source of Target state. |
>
> | **Target QTH** | value from Core Parameters; read-only | Appears for Reference Station and retains all four or six configured characters because the complete Target QTH also anchors geometry. |
>
> | **Target Grid-4** | first four characters of Target QTH; read-only | Appears for RX and simultaneous TX Hardware A/B beside the equally derived Reference Grid-4. |
>
> | **Reference Callsign** | blank; example placeholder | Reference Station, RX Hardware A/B and simultaneous TX Hardware A/B. Enter the Reference's different exact reporting callsign under the same syntax and exact-identity rules as the Target callsign in [Section 4.2](#sec-5-2). |
>
> | **Reference Grid-4** | blank and editable for Reference Station; derived Target grid-4 and read-only for Hardware A/B | Exactly four Maidenhead characters. Reference Station permits an independently chosen grid-4. Hardware A/B displays the shared value but has no independent Reference-QTH setting or serialized `reference_qth`; the operator must still ensure physical co-location. |

Disposition: shortened to identify each value's scientific role instead of
narrating where the UI displays it. The Reference SNR range remains the factual
signed runtime range, `-99.9` to `+99.9 dB`; negative corrections are supported
by the UI, configuration contract and analysis boundary.

Original German passages replaced:

> | **Referenz-SNR-Korrektur (dB)** | `0.0`; `-99.9` bis `+99.9` in Schritten von `0.1 dB` | Erscheint für Compare und ist bei `Kein Benchmark (nur Success)` ausgeblendet. Der Wert wird zum SNR der Referenzseite addiert, bevor Delta SNR berechnet wird. |
>
> | **Target-Rufzeichen** | Wert aus den Kernparametern; schreibgeschützt | Erscheint im Identitätsblock für feste Referenzen bei Referenzstation, RX Hardware A/B und simultanem TX Hardware A/B. Es macht die Target-Seite sichtbar, ohne eine zweite Quelle für den Target-Zustand zu schaffen. |
>
> | **Target-QTH** | Wert aus den Kernparametern; schreibgeschützt | Erscheint bei der Referenzstation und behält alle vier oder sechs konfigurierten Zeichen, weil das vollständige Target-QTH auch die Geometrie verankert. |
>
> | **Target-Grid-4** | erste vier Zeichen des Target-QTHs; schreibgeschützt | Erscheint bei RX und simultanem TX Hardware A/B neben dem ebenso abgeleiteten Referenz-Grid-4. |
>
> | **Referenz-Rufzeichen** | leer; Beispiel-Platzhalter | Referenzstation, RX Hardware A/B und simultanes TX Hardware A/B. Gib das andere exakte Melderufzeichen der Referenz nach denselben Syntax- und Exaktidentitätsregeln wie das Target-Rufzeichen in [Abschnitt 4.2](#sec-5-2) ein. |
>
> | **Referenz-Grid-4** | leer und editierbar bei Referenzstation; abgeleitetes Target-Grid-4 und schreibgeschützt bei Hardware A/B | Exakt vier Maidenhead-Zeichen. Die Referenzstation erlaubt ein unabhängig gewähltes Grid-4. Hardware A/B zeigt den gemeinsamen Wert an, besitzt jedoch keine unabhängige Referenz-QTH-Einstellung und kein serialisiertes `reference_qth`; die physische Ko-Lokation muss weiterhin vom Anwender sichergestellt werden. |

Disposition: German parity with the English replacements.
