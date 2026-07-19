# English Manual Relocation Ledger

This ledger records useful material moved between documentation layers. A relocation is complete only when the destination text exists in `doc_en_candidate.py` and any necessary point-of-action reminder remains at the source.

| ID | Source | Subject | Authoritative destination | Source reminder | Status |
|---|---|---|---|---|---|
| R-001 | 1.4 | Exact TX A/B schedule choices, defaults and preview behavior | 4.3 Benchmark controls | Yes: enter each physical path's actual recurrence and UTC phase | Completed |
| R-002 | 1.4 | Nearest-pair assignment, half-interval tie rule, micro-medians and edge-window eligibility | 7.1 and 7.7 | Yes: pairing is automatic and deterministic | Completed |
| R-003 | 1.4 | Ultimate3S and QMX schedule examples | Appendix B.3/B.4 | Link only | Completed |
| R-004 | 1.4 | Reported-power normalization equation and artificial-offset mechanism | 7.5 | Yes: never encode path identity through false power reports | Completed |
| R-005 | 1.4 | Reversed A/B assignments and repeated balanced runs | 3.2 | Yes: repeat with reversed assignments when a small result matters | Completed |
| R-006 | 1.4 | Physical schedule-to-path mapping and station notes | 3.4 and Appendix B.5 | Yes: verify mapping without RF | Completed |
| R-007 | 1.2 | Full qualifying-evidence definition | 2.1 and 7.4 | Short operator definition only | Completed |
| R-008 | 1.6/1.7 | Radius alternatives as sensitivity analysis, not result shopping | 3.2, with point-of-action warning in both playbooks | Yes | Completed |
| R-009 | 2.2 | Exact power-normalization boundary for one-sided TX outcomes | 7.5 and 7.6 | Short interpretation warning | Completed |
| R-010 | 3.1 | Formal Stability mechanics | 7.8 | Retain distinction between sample Stability and experimental repeatability | Completed |
| R-011 | 5.2 | Database-origin, provider-reason and cache-delivery explanation | 5.6 Working with upstream data | Symptom tables retain upstream-status links | Completed |

## Status values

- **Planned:** destination and reminder identified.
- **Moved:** destination text added; source not yet simplified.
- **Completed:** destination exists, source is correctly shortened and cross-referenced.
- **Cancelled:** review found relocation unnecessary; reason must be added below.

## Decisions and exceptions

- Published `2.5a/b` and `2.6a/b` numbering and anchors remain unchanged in this candidate. A nested numbering cleanup would create link churn without changing the current operator interpretation.
- The empty legacy `sec-3-1` anchor remains in inherited production content as a compatibility alias.
- Part 0 remains the production baseline except for replacing `effect` with `observed pattern` in Section 0.3.
- No worked Success example is added in this review.
