# Outcome frame

## Observable outcome

The repository contains a locally runnable, harness-neutral evaluation suite of exactly 20 original coding tasks. A public CLI copies only an agent-visible fixture and its instruction into an isolated workspace, while a separate verification command runs evaluator-owned black-box acceptance tests and emits deterministic JSON.

## Completion conditions

1. Every task has a unique ID, concise instruction, metadata, agent-visible seed fixture, evaluator-only acceptance test, and evaluator-only reference solution.
2. The untouched seed for every task fails verification for the intended defect.
3. The reference solution for every task passes the same public verifier.
4. The task set covers algorithmic edges, integration contracts, robustness, state/persistence, and agent work discipline rather than twenty variants of one bug class.
5. Staging excludes verifier and reference-solution content, preserves any task-defined dirty-work sentinel, and never requires network access, containers, credentials, or third-party packages.
6. Results distinguish functional acceptance from optional transcript/tool-use evidence; the functional headline never relies on the agent's self-report.
7. Focused tests exercise task discovery, staging, path isolation, baseline failure, reference success, JSON result shape, and repeatability.

## Proof boundary

Local proof establishes the fixture catalog and runner behavior on this machine. It does not establish comparative Claude behavior, cross-platform CI success, human-solvability review, or prompt improvement until separate model trials and platform runs occur.

## Scope boundary

In scope: repository code, original synthetic fixtures, executable acceptance tests, documentation, and local verification. Out of scope: invoking paid models, optimizing a prompt, changing global Claude settings, publishing benchmark content, committing, deploying, or closing the Workbench item.

## Confirmed decision

The user confirmed the CLI seam: isolate and stage an agent-visible workspace, verify final repository state with hidden black-box oracles, and keep transcript/tool-use scoring separate and optional.
