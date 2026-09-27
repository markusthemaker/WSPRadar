# Engineering-guide verification-history relocation

Approved housekeeping on 2026-09-27 separates current engineering instructions
from dated evidence. Scope: `AGENT_README.md` and `docs/verification-history.md`;
this does not restructure the English/German end-user scientific manuals.

Every relocated passage is classified as unique historical verification or
evidence-retention material. Its authoritative destination is the linked history
section; the guide retains a cross-reference at the original decision point.
No historical paragraph, number, path or command is paraphrased or dropped.

The table records original one-based line ranges and SHA-256 hashes of the exact
UTF-8 block strings, including their original line endings. Two ranges begin
partway through the first line, at `Focused verification on` (Zander) and
`On 2026-09-24` (Milazzo overlay), retaining the preceding operating description
in the guide. The original working-tree guide had SHA-256:

`a682c148d38154d352491e08f833b1fa78fa89fcbf511f54c5e91ee7cb931da3`

| Original lines | Destination and scope | SHA-256 of preserved block |
| --- | --- | --- |
| 106-113 | [Installation verification, 2026-07-11](../verification-history.md#installation-2026-07-11) | `283f01502e6b427828ce0c71005a401bcc2ce2b3fbf25a2d377e8167c24cf132` |
| 339-341 | [Startup verification, 2026-07-11](../verification-history.md#startup-2026-07-11) | `52f9d928e625947743c0d49472f51fad7dd5bf30c56180f9b6294677cfef0306` |
| 373-386 | [Scratch evidence archive, 2026-09-27](../verification-history.md#scratch-archive-2026-09-27) | `bd3d653f7cdbe7cc414747660f2823319c2e66c371b01036e4a845b36ebd93fa` |
| 545-555 | [Performance endpoint-participation verification, 2026-09-25](../verification-history.md#performance-method-2026-09-25) | `014222239e72274c31ef5d71c618c4a76d023d79218349499b15be9b7d9f0c0d` |
| 621-640 | [Milazzo human-review and provider verification, 2026-09-26](../verification-history.md#milazzo-human-review-2026-09-26) | `0bdc2f7f2d44c5a287a1f480934308ca8c4f4ddf221b5827f4af0092467c4af3` |
| 643-752 | [Runtime verification records, 2026-09-26 and 2026-09-27](../verification-history.md#recent-runtime-checks-2026-09-26-27) | `97b7d6e0e18b02e747ad6b0050e1747aa1d001c63420024ab91bfeeadff022b2` |
| 822-1369 | [Regression and performance records, 2026-08-17 through 2026-09-25](../verification-history.md#regression-and-performance-records-2026-08-17-to-09-25) | `075e581e7ba18508ca29c9cf5fb9214a539cff2b20cd4b8fb1e1cb6f5292fb4d` |
| 1382-1383 | [Source-compilation and whitespace record, 2026-07-11](../verification-history.md#source-and-whitespace-2026-07-11) | `9bd653cb57c9da1b0c514d4094e1a07c497038ffcf9075e334b12973ddb0f42a` |
| 1468-1475 | [Griffiths publication-reference verification, 2026-09-24](../verification-history.md#griffiths-paper-reference-2026-09-24) | `1853249508d816264b63ab3579ec50428a418fb0f00d2664dfb15bb1b8fd50b3` |
| 1505-1512 | [Zander reference verification, 2026-09-24](../verification-history.md#zander-reference-2026-09-24) | `8aa436ca6e918bb5568d1205e2252a3a5ad8c7f2cddb2ce858b707417ad47ceb` |
| 1542-1551 | [Vanhamel calibration verification, 2026-09-24](../verification-history.md#vanhamel-calibration-2026-09-24) | `5543da8354182013c2f94c2df4fbdd4374461a5bbdf329f5d6a106c3d12c48d5` |
| 1582-1595 | [Vanhamel rotation verification, 2026-09-24](../verification-history.md#vanhamel-rotation-2026-09-24) | `a058de822f9359b7587eadb2b770b1476bf2d76d2cb5addb6a2000a1378d3559` |
| 1627-1645 | [Milazzo TX reference verification, 2026-09-24](../verification-history.md#milazzo-tx-reference-2026-09-24) | `03c3fc443cb51806c18cfd72dc32a757bd3d55ea8cf5e8dcbac82f18c6a3d671` |
| 1673-1681 | [Milazzo RX reference verification, 2026-09-24](../verification-history.md#milazzo-rx-reference-2026-09-24) | `dbd5a215ca917747e7f8eb92db645a1f3b2759ec1fda0e6e1dde348cd4b09d2c` |
| 1699-1704 | [Milazzo overlay artifact verification, 2026-09-24](../verification-history.md#milazzo-overlay-artifact-2026-09-24) | `b67939078a6467b1a100d002854b865c9295847749aaaca5bddefa52866001e5` |
| 1723-1729 | [Milazzo overlay regression integration, 2026-09-24](../verification-history.md#milazzo-overlay-integration-2026-09-24) | `f9a27171393f03d4812302562db8581dabfa1189bb0f20ceef5d5b3c17683a06` |

## Current-state corrections

The former present-tense prepared-export limitation below is retained here as
obsolete text for auditability and replaced in the guide by the committed
Milazzo snapshot's availability/provenance contract and the scope of independent
offline SQL reference tests. The historical `.gitkeep`/skipped-fixture statement
is preserved unchanged in the regression-history block and explicitly dated by
the history preamble.

```text
- A prepared-export regression package is still absent, so its package-integrity
  test is skipped. The separate G3ZIL/G4HZX scientific reference fixture is
  mandatory and exercises the numerical path after SQL aggregation; frozen-row
  SQL execution and broader independent reference coverage remain outstanding.
```

Current operative `scripts/` paths were updated to `scripts/internal/` for the approved specialist tools; the historical record retains the old commands and a location mapping. No runtime, scientific expectations, deployment settings or fixture bytes were changed.

Preservation was checked during relocation by exact ordinal substring comparison for all 16 blocks. No application tests, compilation, provider requests or local load checks were run for this document move.

## Subsequently approved security configuration update

During this cleanup the user separately approved enabling both Streamlit CORS and XSRF protection. The guide now documents the enabled settings and the VS Code command without disabling overrides; Codespaces and Community Cloud browser/upload/reconnection verification remains pending. The former current-state wording is preserved below as superseded text, not as operating guidance.

```text
The application uses port 8501 by default. A repository VS Code task runs the
same entry point with CORS and XSRF protection disabled, matching the committed
Streamlit server configuration.

- Streamlit CORS and XSRF protection are disabled in committed configuration.
  This should be revisited for a public deployment and changed only after testing
  the deployment path that required it.
```

## Historical-status qualifications

Three present-tense statements embedded in older scientific-development descriptions contradicted later records already present in the same guide. They now explicitly identify their original implementation stage and link to those existing later records. No new scientific review, approval, or verification claim was introduced. The former wording is retained verbatim below.

### Milazzo card review status

```text
the affected cards must be regenerated and reviewed in the ongoing review task.
```

### Initial Griffiths fixture SQL coverage

```text
and runtime calculations remain unchanged; SQL execution is still not tested.
```

### Initial Milazzo reconciliation demo direction

```text
image swap. The installed demo remains TX with unchanged scientific settings,
and its description now explains the RX publication reconciliation.
```
