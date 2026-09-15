---
name: research
description: Investigate a question against high-trust primary sources. Use when the user needs documented facts, API or specification research, or evidence for a blocked decision.
---

# Research

Investigate the question against primary sources: official documentation, specifications, source code, first-party APIs, and repository evidence. Follow each important claim back to the source that owns it and cite it precisely.

Delegate the reading to a background agent when capacity and tools allow; otherwise research in the current session. Delegation is an execution optimization, not a precondition for answering.

Honor the request's mutation scope:

- For analysis, review, or other read-only requests, report findings inline and do not create a repository artifact.
- When writes are authorized, save one cited Markdown artifact using the repository's configured research or evidence convention. If none exists, choose a narrow sensible location and report it.

Distinguish sourced facts, inferences, unresolved conflicts, and recommendations. Return evidence-blocked questions as blockers instead of manufacturing certainty.
