# English Manual Integration Validation

- Source branch: `agent/stronger-english-preface`
- Source commit before integration: `e8e657cffa895a6b85f825d8d2ef1ce265d66f00`
- Python: `Python 3.12.13`
- Candidate compilation and execution: passed
- Standalone final manual compilation: passed
- Authoritative `docs/doc_en.py` integration: passed
- `README.md` synchronization: passed
- Internal anchor and link validation: passed
- English PDF rendering smoke test: passed
- Branch regression exit code: `1`
- Main regression exit code: `1`
- Regression comparison: `additional-branch-failure`
- Documentation `git diff --check` exit code: `0`

The regression comparison treats failures already present on `main` as baseline rather than documentation regressions. Full branch output is retained in `docs/drafts/doc_en_validation_pytest.log`.
