# Proposed publication

Status: publication approved by the user on 2026-10-21; execution results will be recorded after hosted checks.

Repository: `vincenzo345/skills`, remote `origin` (`https://github.com/vincenzo345/skills.git`).

Title: **Keep Wayfinder planning and implementation in reliable shared workspaces**

Head: `integration/wayfinder-reliability`.

Recommended base: `main` at `0467dbee1b9d5bc5c1b2114dd88bf6f8f33e9496`, the remote default and implementation starting point. Remote refs were queried on 2026-10-21. The head is 68 commits ahead and zero behind before verification-document commits. Targeting `v2` would additionally include unrelated changes already on main. No existing open PR was found.

[Prepared PR body](pr-body.md), including repository URLs suitable for GitHub. The proposed PR is a draft: [installed-source verification](replay-2026-10-21/README.md) found two unresolved discrepancies that require resolution or explicit disposition before merge readiness.

## Approval scope

1. Commit only the effort's retrospective and verification/publication evidence, including the overview and validation updates. Preserve unrelated untracked research and the ontology document.
2. Recheck remote main and the final branch diff. If the base has changed materially, reassess integration before publishing.
3. Push this integration branch to origin without force.
4. Open a draft PR against main using the prepared title/body and the verified final results. Keep both replay findings visible; do not mark the PR ready merely because CI passes.
5. Monitor the existing Validate v2 skills jobs for the pushed SHA. Record hosted Linux and Windows results and any failures. Report newly discovered defects; do not silently expand scope into optional improvements.

The user approved this plan on 2026-10-21 with "do it". Approval covers branch and draft PR publication and monitoring checks, not merging or releasing.

## CI and release boundaries

[Validation CI](../../.github/workflows/validate-v2.yml) runs on pushes to `v2` and `integration/wayfinder-reliability`, and PRs targeting those branches. Therefore the proposed head push triggers both existing jobs; a PR targeting main does not independently trigger this workflow. The successful head check is not evidence for a separately synthesized merge commit. At inspection, main is an ancestor, so there is no competing base change to integrate.

[Release CI](../../.github/workflows/release.yml) runs on pushes to main and invokes Changesets. Publishing the head and opening a PR do not trigger it. No CI or release configuration was changed during verification. Any future decision to add main PR validation is separate from this publication plan.
