# WSPRadar support

WSPRadar uses GitHub as the durable support and engineering record. Public social-media comments and private messages may be useful for discovery, but actionable defects and changes should be recorded here so they remain searchable, reproducible, and linked to the eventual code change.

## Choose the correct channel

| Need | Channel |
|---|---|
| Reproducible incorrect behavior, error, or regression | **Bug report** issue form |
| New capability or material workflow improvement | **Feature request** issue form |
| Concern about methodology, statistics, data handling, interpretation, or scientific claim wording | **Scientific or methodological concern** issue form |
| Usage question, experiment-design discussion, result interpretation, or early idea | **GitHub Discussions** |
| Documentation and maintained demos | **WSPRadar.org** |

Do not use a scientific-concern issue merely because WSPR data has known observational limitations. Use it when a specific WSPRadar assumption, calculation, implementation, or claim may be defective, biased, incomplete, or insufficiently qualified.

## Information that makes support effective

For analysis-related reports, provide as much of the following as applies:

- WSPRadar version or Git commit
- analysis mode
- exact target and reference callsigns
- QTH locator and band
- complete UTC analysis interval
- non-default filters, thresholds, and correction values
- saved `.config` file
- screenshots or exact numerical outputs
- prepared reproducibility package
- browser, operating system, and local Python environment where relevant

Use the smallest dataset and shortest procedure that still reproduces the problem.

## Public-data and security caution

WSPR callsigns and spots are public, but local paths, configuration files, logs, and deployment details may contain information you did not intend to publish. Remove passwords, tokens, cookies, private URLs, credentials, and unrelated personal data before attaching files.

Do not publish exploit details or credentials in a normal issue. Use GitHub private vulnerability reporting when it is enabled for the repository.

## Triage and response

The project is maintained on a best-effort basis. Submission does not imply acceptance or a fixed response time. Issues may be closed when they are duplicates, cannot be reproduced, are outside the project scope, conflict with the documented methodology, or do not provide enough information after a reasonable request for clarification.

Accepted engineering work proceeds through the manual workflow described in [CONTRIBUTING.md](CONTRIBUTING.md).
