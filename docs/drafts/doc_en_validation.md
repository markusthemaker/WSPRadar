# English Manual Integration Validation

- Source branch: `agent/stronger-english-preface`
- Integrated English commit: `03f7633e670faa2546124fb9e44fa017e94a0068`
- Validation runtime: Python 3.12.13
- Candidate compilation and execution: passed
- Standalone final manual compilation: passed
- Authoritative `docs/doc_en.py` integration: passed
- `README.md` synchronization: passed
- Internal anchor and link validation: passed
- English PDF rendering smoke test: passed
- Documentation `git diff --check`: passed

## Regression comparison

The full branch suite completed with `6 failed, 530 passed, 3 skipped`. The same `main` baseline completed with three pre-existing demo-configuration failures. The English-only integration adds three expected documentation-contract failures:

1. one test still requires the former exact `Qualifying evidence` wording;
2. one test still requires the former exact `simultaneous TX Compare` wording;
3. the English/German anchor-parity test detects the new Appendix B subsections, which are not yet present in `docs/doc_de.py`.

These failures do not indicate a broken English manual, but they correctly prevent this draft PR from being merge-ready. Before merging, update the German manual with equivalent structure and claims, revise the exact English documentation assertions to the approved wording, regenerate `README.md`, and rerun the suite.

Full branch regression output is retained in `docs/drafts/doc_en_validation_pytest.log`.