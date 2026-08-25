# Simultaneous TX Benchmark setup and appendix restructure

## Accepted source model

This is a parallel/co-authored English and German documentation update. The
accepted baseline is `docs/doc_en.py` and `docs/doc_de.py` at Git revision
`3e984165c0092b576f7ebad749044566d71529ff`. The approved semantic specification
is the user's accepted simultaneous-TX documentation proposal together with the
subsequent minor changes requesting:

- a concise Section 2.4.1 that recommends avoiding compound callsigns unless
  they are necessary;
- an Appendix A limitation explaining why independent WSJT-X `Tx Pct` operation
  is unsuitable for sparse synchronized TX;
- a practical simultaneous-TX Appendix B covering QMX/Virtual U3S,
  Ultimate3S and randomized split-lane custom ZachTek firmware;
- the existing sequential procedure moved to Appendix C;
- Reference SNR calibration moved to Appendix D; and
- equivalent, natural operator-oriented English and German guidance.

The user subsequently authorized a focused practical revision inside Appendix
B: simplify B.3 and B.4, combine the QMX/Virtual U3S and Ultimate3S procedures,
and add a four-position frequency-swap schedule that reduces frequency-position
bias without claiming to cancel it.

Neither language is a secondary source of scientific meaning. The accepted
specification governs both manuals, with established WSPRadar terms and native
German amateur-radio wording preserved.

## Appendix ownership after the change

| Destination | Authoritative content | Canonical anchor | Retained compatibility anchors |
| --- | --- | --- | --- |
| Appendix A | Parallel WSJT-X instances and the limitation of independent `Tx Pct` scheduling for simultaneous TX | `sec-a` | `sec-a-1` through `sec-a-4` remain in place |
| Appendix B | Practical simultaneous TX Hardware A/B setup | `sec-simultaneous-tx-setup` | none; this is a new appendix |
| Appendix C | Sequential TX A/B scheduling and switching | `sec-sequential-tx-setup` | `sec-b` and `sec-b-1` through `sec-b-5` remain attached to their relocated meanings |
| Appendix D | Reference SNR calibration | `sec-reference-snr-calibration` | `sec-c` remains attached to calibration |

`sec-d` is not reused for Appendix D because it already identifies Chapter 6,
Literature, Prior Art and Positioning. Each sequential or calibration
compatibility anchor is placed immediately before its corresponding new
canonical anchor and does not create a duplicate visible heading.

## Original English A.4 and disposition

The following baseline passage is not retained verbatim at A.4:

````markdown
<a id="sec-a-4"></a>
#### A.4 Configure distinguishable simultaneous TX

For simultaneous TX Hardware A/B, isolation of settings is only the software foundation. Before radiating, verify the complete two-transmitter arrangement into suitable loads or through a safely engineered low-power test path:

1. Assign the exact Target callsign and QTH to one instance and the different exact Reference callsign to the other. Configure the Reference instance to report from the same test QTH; WSPRadar displays disabled Target and Reference Locator fields derived from the first four Target-QTH characters and matches both uploaded identities within that shared grid-4.
2. Route each instance to its intended radio, control interface and audio output. A copied configuration must not key or feed the wrong transmitter.
3. Use the normal WSPR dial frequency on both radios if appropriate, but assign separated audio TX offsets such as `1450 Hz` and `1550 Hz`. Inspect the waterfall and choose clear, non-overlapping positions rather than assuming those illustrative values are free.
4. Configure deliberate same-cycle starts. Independent randomized `Tx Pct` settings do not define a synchronized comparison schedule.
5. Verify frequency, actual RF power, spectral cleanliness, clock alignment and uploaded callsign/QTH/power for both paths before collecting evidence.
6. Confirm adequate isolation between active transmitters and antennas. Coupled power can desensitize or damage equipment and can create intermodulation or misleading spots; use appropriate filtering, spacing, power levels and RF engineering for the station.

For a small observed difference, repeat with exchanged audio-frequency assignments and perform a hardware crossover where practical. Preserve both runs separately; do not pool them until the role, correction and analysis scope are aligned.
````

Disposition:

- The `sec-a-4` decision point remains in Appendix A, but now owns only the
  WSJT-X scheduling limitation and a link to the practical simultaneous-TX
  appendix.
- Callsign and shared-QTH guidance moves to B.1.
- Same-cycle scheduling and separated in-window frequencies move to B.2.
- Actual power, simultaneous spectral quality and safe bench checks move to
  B.3. The initially relocated detailed coupled-power/desensitization and
  record-inventory paragraphs were later removed by explicit authorization, as
  recorded below.
- Callsign/QTH/power and provider verification moves to B.4.
- Device routing and version-specific scheduling move to B.5.
- Frequency exchange, hardware crossover and separate-run preservation move to
  B.6.
- The illustrative `1450 Hz` / `1550 Hz` pair is replaced by device-appropriate
  nominal 100 Hz separation, edge-margin guidance and verification of actual RF
  frequencies.

## Original German A.4 and disposition

The following baseline passage is not retained verbatim at A.4:

````markdown
<a id="sec-a-4"></a>
#### A.4 Unterscheidbares simultanes TX konfigurieren

Für simultanes TX Hardware A/B ist die Trennung der Einstellungen nur die softwareseitige Grundlage. Prüfe den vollständigen Aufbau mit zwei Sendern vor dem Senden an geeigneten Abschlüssen oder über einen sicher ausgelegten Testpfad mit geringer Leistung:

1. Weise einer Instanz das exakte Target-Rufzeichen und Target-QTH und der anderen das davon verschiedene exakte Referenz-Rufzeichen zu. Konfiguriere die Referenzinstanz für Meldungen vom selben Test-QTH; WSPRadar zeigt deaktivierte Target- und Referenz-Locator-Felder an, die beide aus den ersten vier Zeichen des Target-QTHs abgeleitet werden, und ordnet beide hochgeladenen Identitäten diesem gemeinsamen Grid-4 zu.
2. Führe jede Instanz zum vorgesehenen Funkgerät, zur richtigen Steuerschnittstelle und zum richtigen Audioausgang. Eine kopierte Konfiguration darf nicht den falschen Sender tasten oder ansteuern.
3. Verwende bei Bedarf auf beiden Funkgeräten die normale WSPR-Abstimmfrequenz, aber getrennte Audio-Sendeversätze wie `1450 Hz` und `1550 Hz`. Prüfe den Wasserfall und wähle freie, nicht überlappende Positionen, statt anzunehmen, dass diese Beispielwerte unbelegt sind.
4. Konfiguriere bewusst gleichzeitige Starts im selben Zyklus. Unabhängige Zufallseinstellungen für `Tx Pct` definieren keinen synchronisierten Vergleichszeitplan.
5. Prüfe vor dem Sammeln von Evidenz für beide Pfade Frequenz, tatsächliche HF-Leistung, spektrale Reinheit, Uhrensynchronisation und hochgeladene Angaben zu Rufzeichen, QTH und Leistung.
6. Stelle ausreichende Isolation zwischen den aktiven Sendern und Antennen sicher. Eingekoppelte Leistung kann Geräte desensibilisieren oder beschädigen sowie Intermodulation oder irreführende Spots erzeugen; verwende eine für die Station geeignete Filterung, räumliche Trennung, Leistung und HF-technische Auslegung.

Ist ein kleiner beobachteter Unterschied entscheidend, wiederhole den Versuch mit vertauschten Audiofrequenz-Zuordnungen und führe nach Möglichkeit einen Hardware-Kreuztausch durch. Bewahre beide Läufe getrennt auf; führe sie erst zusammen, wenn Rollen, Korrektur und Analyseumfang übereinstimmen.
````

Disposition: German semantic parity with the English relocation. Appendix A
retains a concise limitation at the original decision point; the practical
identity, timing, frequency, power, isolation, provider-check, device and
crossover guidance moves to the corresponding B.1 through B.6 destinations.

## Authorized Appendix B refinements

### English passages removed by authorization

The following B.3 items from the first integrated draft are intentionally not
retained or relocated:

````markdown
4. Confirm that coupled power cannot damage or desensitize either transmitter. Use suitable antenna spacing, filtering, isolators or reduced power according to the station design.
5. Record transmitter, firmware, oscillator or GNSS source, antenna, feedline, filter, measured power, frequency assignment and test arrangement for each path.
````

The following B.4 item is also intentionally removed:

````markdown
2. Preserve a useful local decoder record or spectrum screenshot.
````

### German passages removed by authorization

The corresponding German B.3 items from the first integrated draft are
intentionally not retained or relocated:

````markdown
5. Sorge für geeignete Filterung, Antennenabstand und HF-Entkopplung. Eingekoppelte Sendeleistung kann Geräte beschädigen oder desensibilisieren und irreführende Spots erzeugen.
6. Notiere vor dem Messlauf für beide Pfade Sender, Firmware, Antenne, Speiseleitung, tatsächliche und gemeldete Leistung, Frequenz und Zeitplan.
````

The corresponding German B.4 item is also intentionally removed:

````markdown
2. Bewahre eine aussagekräftige Ausgabe des lokalen Decoders oder einen Screenshot des Spektrums auf.
````

Disposition: these are user-authorized removals rather than silent compression.
B.3 retains the simultaneous two-transmitter spectrum, spurious-product and
intermodulation check. Its power guidance now prohibits false dBm identity
encoding, requires the nearest valid WSPR-encoded dBm value, presents
`20–30 dBm` as WSPRadar's recommendation for this test rather than a universal
legal or manufacturer limit, and warns against excessive power. B.4 no longer
requests a local decoder record or spectrum screenshot; provider queryability,
the possible `15 minutes or more` delay and the short WSPRadar preflight are
one operator step.

### Combined QMX, Virtual U3S and Ultimate3S procedure

The separately headed B.5.1 QMX/QMX+ Virtual U3S and B.5.2 Ultimate3S
procedures are combined into one visible B.5.1–B.5.2 procedure. Both existing
canonical anchors remain, immediately adjacent before the combined heading, so
either deep link reaches the complete shared procedure. The ZachTek procedure
and `sec-simultaneous-tx-setup-5-3` remain B.5.3.

The combined procedure retains exact-model QMX firmware selection, the
`1_04_000` caveat, accurate timing, truthful identities and power, actual RF
frequency verification, Ultimate3S-specific `Start = 00` behavior and the
ordinary-versus-extended-message alignment boundary. It attributes the
up-to-16-entry capability to the physical Ultimate3S evidence; Virtual U3S is
described as modeled on that architecture and must be confirmed against the
installed QMX/QMX+ firmware rather than assumed identical in every build. It
additionally documents:

- a deterministic sparse schedule whose two transmitters remain paired in the
  same cycles;
- a four-position alternating schedule using `+50 Hz` and `+150 Hz`; and
- the bounded interpretation that alternating positions balances or reduces
  frequency-position bias but does not guarantee cancellation.

### ZachTek fixed-position text replaced by authorization

The following English fixed-position passage from the first integrated B.5.3 is
not retained:

````markdown
##### B.5.3 ZachTek firmware 2.19 fixed-frequency builds

Replace **both** occurrences in transmitter A's source copy with:

```cpp
freq = freq - 5000ULL;  // fixed -50 Hz; freq uses 0.01 Hz units
```

Replace **both** occurrences in transmitter B's source copy with:

```cpp
freq = freq + 5000ULL;  // fixed +50 Hz; freq uses 0.01 Hz units
```

The two builds are then nominally `100 Hz` apart. Changing only one occurrence is insufficient because a later band cycle could return to random placement. A following Type 3 transmission uses the same selected frequency as its Type 2 partner. This is a source-code modification, not an option in the ZachTek configuration program.
````

The corresponding German fixed-position passage is not retained:

````markdown
##### B.5.3 ZachTek-Firmware 2.19: Festfrequenz-Builds

Ersetze **beide** Vorkommen in der Quellkopie für Sender A durch:

```cpp
freq = freq - 5000ULL;  // fest -50 Hz; freq verwendet Einheiten von 0,01 Hz
```

Ersetze **beide** Vorkommen in der Quellkopie für Sender B durch:

```cpp
freq = freq + 5000ULL;  // fest +50 Hz; freq verwendet Einheiten von 0,01 Hz
```

Die beiden Builds liegen damit nominal `100 Hz` auseinander. Nur ein Vorkommen zu ändern reicht nicht aus, weil ein späterer Bandzyklus zur zufälligen Platzierung zurückkehren könnte. Eine nachfolgende Typ-3-Aussendung verwendet dieselbe gewählte Frequenz wie ihr Typ-2-Partner. Dies ist eine Quellcodeänderung und keine Option im ZachTek-Konfigurationsprogramm.
````

Disposition: B.5.3 remains the ZachTek source-modification procedure, but its
authoritative design is now randomized split-lane operation. Both occurrences
of the stock random-offset expression are replaced in each build with:

```cpp
freq = freq - (100ULL * random(31, 91));
freq = freq + (100ULL * random(30, 90));
```

The documented lower lane is `-90` through `-31 Hz`; the upper lane is `+30`
through `+89 Hz`. Because `freq` is in centihertz, the closest commanded
tone-zero positions are at least `61 Hz` apart. Accounting for the approximately
`4.4 Hz` WSPR tone span leaves roughly `57 Hz` between the closest commanded
tone centers. The approximately `10 Hz` edge margin applies specifically to the
tone-zero lane endpoints, not the complete upper signal; actual radiated
positions also depend on oscillator and synthesizer error. Randomization reduces
repeated use of one exact frequency but leaves lower-versus-upper lane assignment
as a residual confound. Run 1 and Run 2 therefore reverse the lanes.

The revised procedure retains the requirement to change both source
occurrences, Type 3 reuse of the selected Type 2 frequency, the source-code—not
configuration-program—boundary, `Product_Model = 1048`, build prerequisites,
recoverable stock firmware and post-flash bench verification. It adds an on-air
lane-bound and Joint-evidence preflight. A.4 and Appendix B no longer describe
the ZachTek design as fixed-frequency.

## Sequential and calibration moves

The former Appendix B sequential procedure is unique useful operator guidance.
It is moved without compression to visible Appendix C and renumbered C.1
through C.5. New semantic anchors identify the canonical destination, while
`sec-b` and `sec-b-1` through `sec-b-5` remain beside the same headings so old
links continue to reach the sequential procedure.

The former Appendix C calibration procedure is unique useful measurement
guidance. It is moved without compression to visible Appendix D. The new
canonical anchor is `sec-reference-snr-calibration`; `sec-c` remains beside it
so old links continue to reach calibration.

All inbound English and German references are relabelled and retargeted to the
new canonical anchors. The old anchors are compatibility destinations, not new
Table of Contents targets.

## Accepted bilingual reverse outlines

### English

1. A.1-A.3 create and isolate parallel WSJT-X instances for independent RX
   paths.
2. A.4 explains that deterministic same-cycle TX would require `Tx Pct = 100%`,
   that lower percentages are random, and that continuous occupation is not
   recommended; it points operators to deterministic beacon hardware.
3. B.1 chooses two valid exact identities, prefers ordinary one-transmission
   callsigns and avoids compound callsigns unless necessary.
4. B.2 aligns UTC timing and message phase. It places directly programmed QMX,
   Virtual-U3S and Ultimate3S pairs nominally 100 Hz apart, while custom ZachTek
   builds use the randomized lower and upper lanes defined in B.5.3 instead of
   a fixed separation.
5. B.3 prohibits false dBm identity encoding, uses the nearest valid
   WSPR-encoded dBm value, presents `20–30 dBm` as WSPRadar's recommendation for
   this test, warns against excessive power and retains the simultaneous
   spectrum/intermodulation check.
6. B.4 verifies exact callsigns, shared grid-4, power, times and frequencies in
   WSPRnet and the provider used by WSPRadar; one combined step waits for
   queryability, allows `15 minutes or more` and runs the WSPRadar preflight.
7. Combined B.5.1–B.5.2 gives practical QMX/QMX+ Virtual U3S and Ultimate3S
   setup, attributes the up-to-16-entry fact to physical Ultimate3S, requires
   version-specific Virtual-U3S confirmation, and includes a deterministic
   sparse same-cycle four-position schedule that alternates `+50 Hz` and
   `+150 Hz` to reduce frequency-position bias.
   B.5.3 uses randomized lower/upper frequency lanes, requires reversal in a
   second run, retains both source changes and the compile/flash boundary, and
   verifies the lanes and Joint evidence on air.
8. B.6 uses frequency reversal and hardware crossover as separate controlled
   runs.
9. C.1-C.5 retain the complete sequential scheduling, switching, QMX,
   Ultimate3S and preservation procedure.
10. D retains the complete Reference SNR calibration procedure.

### German

1. A.1-A.3 richten getrennte parallele WSJT-X-Instanzen für unabhängige
   Empfangspfade ein.
2. A.4 erklärt, dass deterministisches Senden im selben Zyklus `Tx Pct = 100%`
   erfordern würde, niedrigere Werte zufällig arbeiten und eine dauernde
   Bandbelegung nicht empfohlen wird; der Abschnitt verweist auf deterministisch
   planbare Bakensender.
3. B.1 wählt zwei gültige exakte Rufzeichen, bevorzugt reguläre Rufzeichen im
   Einzelaussendungsformat und vermeidet zusammengesetzte Rufzeichen, soweit sie
   nicht erforderlich sind.
4. B.2 gleicht UTC-Zeitsteuerung und Nachrichtenphase ab. Direkt programmierte
   Paare aus QMX, Virtual U3S und Ultimate3S werden nominell 100 Hz voneinander
   entfernt platziert; angepasste ZachTek-Builds verwenden stattdessen die in
   B.5.3 definierten randomisierten unteren und oberen Frequenzfenster ohne
   festen Abstand.
5. B.3 verbietet falsche dBm-Werte zur Pfadkennzeichnung, verwendet den
   nächstliegenden gültigen WSPR-kodierbaren dBm-Wert, kennzeichnet `20–30 dBm`
   als WSPRadar-Empfehlung für diesen Test, warnt vor unnötig hoher Leistung und
   bewahrt die gemeinsame Spektrum-/Intermodulationsprüfung.
6. B.4 prüft exakte Rufzeichen, gemeinsames Grid-4, Leistung, Zeiten und
   Frequenzen bei WSPRnet und beim von WSPRadar verwendeten Anbieter; ein
   gemeinsamer Schritt wartet auf die Abfragbarkeit, berücksichtigt `15 Minuten
   oder länger` und startet die WSPRadar-Probeanalyse.
7. Der gemeinsame Abschnitt B.5.1–B.5.2 beschreibt QMX/QMX+ Virtual U3S und
   Ultimate3S, ordnet die Angabe von bis zu 16 Einträgen dem physischen
   Ultimate3S zu, verlangt für Virtual U3S eine versionsbezogene Prüfung und
   verwendet einen deterministischen sparsamen Vier-Positionen-Zeitplan, der
   `+50 Hz` und `+150 Hz` in denselben Zyklen wechselt, um den Einfluss der
   Frequenzposition zu verringern. B.5.3 verwendet randomisierte untere und
   obere Frequenzbereiche, verlangt ihren Tausch in einem zweiten Lauf, bewahrt
   beide Quellcodeänderungen und die Grenze zu Kompilieren und Flashen und prüft
   Frequenzbereiche sowie Joint-Evidenz auf Sendung.
8. B.6 verwendet Frequenztausch und Hardware-Kreuztausch als getrennte
   kontrollierte Läufe.
9. C.1-C.5 bewahren das vollständige sequenzielle Verfahren zu Zeitplanung,
   Umschaltung, QMX, Ultimate3S und Versuchsdokumentation.
10. D bewahrt das vollständige Verfahren zur Referenz-SNR-Kalibrierung.

## Affected-scope bilingual parity checklist

- [x] The accepted English and German outlines carry the same content ownership
  and ordering for Appendices A through D.
- [x] Sections 0.0, 2.4.1, 5.3, 7.1, 7.2, 7.6 and 7.10 carry the same WSPR
  message-format, archive-representation and dependence boundaries.
- [x] Sections 2.3.2 and 2.4.3 carry equivalent complete-station Buddy meanings,
  same-grid-4 qualification and Hardware-A/B routing.
- [x] Section 4.2 uses only generic `CALLSIGN` examples in both languages and
  retains exact archive-identity and authorization boundaries.
- [x] A.4 carries equivalent WSJT-X randomness, `100%`, band-occupancy and
  `5–20%` operating recommendations.
- [x] B.1 carries the same ordinary-versus-compound callsign preference and
  fallback boundary.
- [x] B.2 and B.5 carry equivalent numerical values, frequency units, device
  names, firmware qualifications and verification requirements.
- [x] B.3 carries the same false-dBm prohibition, valid WSPR-encoded reporting
  rule, WSPRadar-specific `20–30 dBm` test recommendation, excessive-power
  warning and simultaneous spectrum/intermodulation check; the authorized
  detailed removals are absent.
- [x] B.4 carries the same WSPRnet URL, provider distinction, combined
  queryability/preflight step and delay warning; the authorized screenshot item
  is absent.
- [x] B.5.1 and B.5.2 remain as adjacent anchors before one combined heading and
  carry the same physical-Ultimate3S capability attribution, version-qualified
  Virtual-U3S guidance, deterministic sparse same-cycle and four-position
  frequency-swap guidance without claiming guaranteed bias cancellation.
- [x] B.5.3 carries the same randomized split-lane expressions, inclusive lane
  bounds, centihertz conversion, commanded tone-position separation,
  tone-zero-endpoint edge margin, actual-frequency qualification, randomization
  benefit, residual lane confound, Run-1/Run-2 reversal, Type-3 frequency reuse,
  source/build/recovery boundary and post-flash/on-air preflight; superseded
  fixed-position wording and expressions are absent.
- [x] B.6 carries the same reversal, crossover and separate-run meaning.
- [x] The complete former sequential and calibration guidance remains present in
  both languages after relocation.
- [x] Canonical and compatibility anchors appear once per manual and in the same
  order; no visible heading is duplicated.
- [x] Reference numbers, URLs, code, commands, callsign placeholders, units and
  supported public identifiers are preserved exactly across the bilingual pair
  except for natural localized prose.
- [x] Material intentional semantic divergences: none.
