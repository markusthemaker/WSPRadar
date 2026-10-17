# WSPRadar support

WSPRadar uses [GitHub Discussions](https://github.com/markusthemaker/WSPRadar/discussions) as the main place for community help, suspected bugs, ideas, and experiments, with GitHub Issues used for engineering work when needed. Public social-media comments and private messages may be useful for discovery, but actionable defects and changes should be recorded here so they remain searchable, reproducible, and linked to their resolution.

A free GitHub account is required to post; no programming knowledge or confirmed diagnosis is needed. Please write all posts and replies in English. Please use one topic per discussion.

## Choose the correct channel

Before asking a usage question, please check the [documentation and demos inside the WSPRadar application](https://wspradar.streamlit.app/). If something remains unclear, your question is welcome in Ask a question.

| Need | Channel |
|---|---|
| Suspected incorrect behavior, error, or regression | **[Report a bug or concern](https://github.com/markusthemaker/WSPRadar/discussions/new?category=report-a-bug-or-concern)** discussion |
| New capability, material workflow improvement, or early idea | **[Ideas and feature requests](https://github.com/markusthemaker/WSPRadar/discussions/new?category=ideas-and-feature-requests)** discussion |
| Concern about methodology, statistics, data handling, interpretation, or scientific claim wording | **[Report a bug or concern](https://github.com/markusthemaker/WSPRadar/discussions/new?category=report-a-bug-or-concern)** discussion |
| Usage question, experiment-design help, or result interpretation | **[Ask a question](https://github.com/markusthemaker/WSPRadar/discussions/new?category=ask-a-question)** Q&A discussion |
| Shared experiment or finding | **[Discuss your experiments](https://github.com/markusthemaker/WSPRadar/discussions/new?category=discuss-your-experiments)** discussion |
| Documentation and maintained demos | **[Documentation and demos inside the WSPRadar application](https://wspradar.streamlit.app/)** |

Do not label a discussion as a scientific concern merely because WSPR data has known observational limitations. Use that description when a specific WSPRadar assumption, calculation, implementation, or claim may be defective, biased, incomplete, or insufficiently qualified. Questions about those limitations are welcome in Ask a question.

## Information that makes support effective

Start with what you tried, what happened, and what you expected. A screenshot or saved configuration can help, but start with what you have. You do not need to decide whether the cause is a software bug.

For analysis-related reports, the following details can help when applicable. They are optional in your first post; the maintainer will request additional information if needed:

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

Do not publish exploit details or credentials in a public discussion or issue. Use GitHub private vulnerability reporting when it is enabled for the repository.

## Triage and response

The project is maintained on a best-effort basis. Submission does not imply acceptance or a fixed response time. Discussions and issues may be closed when they are duplicates, cannot be reproduced, are outside the project scope, conflict with the documented methodology, or do not provide enough information after a reasonable request for clarification.

Accepted application changes are implemented and tested by the maintainer in the private WSPRadarApp repository. The maintainer creates a linked engineering Issue when useful and reports the outcome, including the release containing a fix, back to the original public discussion. The existing issue forms remain available for engineering work; community members can begin with a discussion.
