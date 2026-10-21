# Installed-source verification, 2026-10-21

This follow-up verifies the delivered implementation without changing skills, completed issues, or accepted requirements. The production checkout remains on `integration/wayfinder-reliability`, starting at `46a6bd3`. See [provenance](provenance.json) for installed-source comparisons.

## Runtime and method

All 32 promoted skills, comprising 111 files, match source `00ff5b94ebab4fdd7d6fea9681e79957fcedbc57` in both installed locations. Codex junction contents match with CRLF normalization; Claude cache contents match Git archive bytes exactly. No skill, test, or CI source changed between that commit and the inspected head.

Behavioral execution used fresh Codex subagents with `fork_turns=none`, inheriting the controller's model. The harness does not expose a separately pinned model identifier. Actors read installed skill files and executed installed helpers against isolated temporary Git repositories. No Skill invocation tool was available, so this verifies application of installed instructions, not automatic slash-command discovery. Actors did not read production test assertions, the replay rubric, or previous validation outcomes. Synthetic human turns were supplied by the controller; actors did not invent their own human answers.

Claude Code returned `loggedIn: false`, `authMethod: none`, exit 1 from `claude auth status`. No authenticated Claude behavioral run is claimed. Authentication failure did not prevent local plugin inventory and file verification.

## Planning replay

Temporary repository: `E:/tmpdir/wayfinder-installed-replay-vd7yjutt/fixture`.

The [transcript](planning/transcript.json) records supplied turns and actor responses. Per-turn snapshot JSON files retain each artifact's original path, text, and byte hash. [Execution notes](planning/execution-notes.md) disclose the actor's operations and capture limitations. [Observed artifact checks](planning/observations.json) were made after execution, separate from the actor's behavior.

| Turn | Supplied input | Observation |
| --- | --- | --- |
| 1 | Chart a saved-notes application; scope/storage independent, ranking dependent on scope, import unclear. | One effort and open map, three open decisions, import fog. Stopped with the map, named next decision, and invocation. |
| 2 | Start Search scope. | Acquired ownership and asked about supported formats and searchable fields. |
| 3 | Notes are personal and must work offline. | Persisted requirements; Search scope remained open, with the unanswered choices requested again. |
| 4 | Plain-text/Markdown notes; title search first. | Resolved only scope, released its claim, kept the map open. Import became a concrete decision. |
| 5 | Full text now required; preserve the old answer. | Created a replacement, retained the original answer, rewired dependent ranking and recorded an impact review without inventing a ranking answer. |
| 6 | Revert first release to titles; preserve both earlier answers. | Updated the current map pointer from an anchored old answer to its replacement. Both old answers remain traceable; the prior-answer link retains `#resolution`. |
| 7 | Is a full article rewrite needed before offline storage? | Rejected the unrelated prerequisite, created no article or implementation, and asked the still-open storage question. |

Before turn 6, the controller changed the valid current-answer link to include `#resolution`. The exact [precondition](planning/anchor-precondition.json) and snapshot were captured before the next prompt. This deliberately exercises the previously problematic anchor; it is not a repair after a failed result. No failed artifact was manually repaired to produce a pass. Ordinary map gist updates by the actor are disclosed in its execution notes; the turn-6 helper output remained intact.

Ranking's `review_required` gate was cleared through recorded impact review while its human decision stayed open. The replay therefore demonstrates review before subsequent eligibility, not a gate left permanently set. Snapshots omit `.git`, so they do not independently prove the earlier claim token remained identical across turns; that continuity is actor-reported. The final storage claim is retained only in the isolated fixture. Earlier transcript Unicode capture had substitutions; execution notes disclose the limited correction to a turn-2 response before delivery. Treat transcript typography as less exact than artifact snapshots.

The original scope-drift challenge, continuation, human-choice boundary, answer history, and anchored-pointer behavior passed these bounded observations. This does not establish universal compliance.

## Separate planning-to-implementation handoff

Temporary repository: `E:/tmpdir/installed-handoff-e3k78jmn/repo`.

A second fresh actor received settled requirements for a small offline note-title command and an explicitly approved external test seam. This intentionally exercises the supported small-effort path without manufacturing a Wayfinder map. It is not a claim that the still-open application map from the first replay reached implementation.

1. Applied installed grill-with-docs and to-spec instructions. Saved discovery and published ready-for-agent spec revision 1 in the same effort. Stopped with no implementation issues.
2. Applied installed to-tickets instructions. Proposed one vertical slice with acceptance criteria and empty blockers, then stopped before publication.
3. Received the controller-supplied approval and published a self-contained issue with current spec basis and explicit empty blockers. Stopped before implementation.
4. A fresh consumer received only the fixture path and an explicit spec reference, with permission to select and claim but stop before coding. It selected the published child issue, reported revision 1, empty blockers, configured authority and ownership receipt, and stopped before coding. A separate installed-helper contender then exited 2 with `already claimed by installed-handoff-consumer`. That contender is a deterministic probe, not a second live behavioral actor. Cleanup releases the unfinished claim without completing the issue.

See the [producer capture](handoff-producer/capture-manifest.json), including the [initial response](handoff-producer/turn-01-assistant-final.txt.json) and [spec-publication output](handoff-producer/helper-outputs.json). Consumer evidence is retained separately under `handoff-consumer/`.

This replay exposed the two discrepancies below. Later successful publication does not erase the earlier stage or response failure.

## Newly observed discrepancies, not fixed

**V-01: publishing a spec can leave the effort's stage stale.** After discovery followed by successful `publish-spec`, the overview retained `stage: discovery` while `current_spec` named a current ready-for-agent revision and `next_action` requested slice approval. This conflicts with the spec's current-stage requirement. The installed publication path updates current_spec and next_action but does not update stage (`work_records.py`, `_publish_revision`, around line 307). An effort created directly at specification stage can mask this omission. Publishing the later issue set stage to implementation; the earlier failing snapshot remains evidence. Impact is misleading resumption context, not demonstrated unsafe claiming. Existing 60-test coverage passes despite this case.

**V-02: the actor's handoff named an unavailable skill.** The spec-publication response recommended `spec-to-issues`; the installed inventory contains `to-tickets`, and the inspected to-spec/router instructions do not supply that old name. This is an observed agent handoff error, not evidence that the helper routes to a wrong command. The next supplied human turn explicitly named to-tickets and succeeded, so that continuation does not validate the erroneous suggestion. Impact is a confusing or unusable next invocation.

These findings are separate from the previously resolved implementation review. Completed production issue states and spec acceptance were preserved as requested. Neither finding was fixed or converted into an approved new implementation issue during verification. Resolve or explicitly disposition them before recommending merge readiness.

## Deterministic checks and boundaries

The existing full script suite passed again: **60 tests in 123.480 seconds**, Windows Python 3.12.8 and pinned PyYAML 6.0.3. See [captured output](deterministic-tests.txt). PowerShell wrapped unittest's stderr progress as `NativeCommandError` text; the process exited 0 and unittest reported OK. This was shell presentation, not a failing case.

The 27 preservation tests, promoted-package validator, plugin version check (2.1.0), and strict Claude plugin validation also passed. These checks were rerun without adding tests or changing runtime sources. The new behavioral findings illustrate why these passes are not a blanket behavior guarantee.

Hosted Windows/Linux jobs remain pending publication approval. Remote-provider concurrency was not exercised live and remains unsupported without the documented exclusive path or established controller. No production historical work was migrated; no application implementation, push, PR, merge, release, or reinstall occurred during verification.

For the concrete target and approval boundary, see the [publication plan](../publication-plan.md) and [PR body](../pr-body.md).
