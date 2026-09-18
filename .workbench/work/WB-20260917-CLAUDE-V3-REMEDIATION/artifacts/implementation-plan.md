# Claude v3 harness remediation plan

## Outcome

Make Claude's performance on the brownfield Workbench investigation comparable to Codex—and preferably better—under the grading criteria already used for the prior transcript assessment. The primary mechanism is the Claude harness: its canonical operating prompt, early/late hooks, and installation hygiene. Workbench core changes are supporting work only and do not lead the implementation.

Success requires both quality and economy. A run does not pass merely because its final answer is eventually correct after retractions: its durable Workbench state, evidence provenance, question ordering, and investigation cost must also pass.

## Frozen comparison contract

Before changing the harness, capture the existing assessment rubric and the Codex and Claude v3 scores in a versioned comparison fixture under `tests/comparison/claude-codex-investigation/`. Preserve the existing dimensions and weights rather than tuning the rubric to the proposed fix. At minimum, the fixture must retain the dimensions already used in the assessment:

- factual and causal correctness;
- evidence quality and claim calibration;
- coverage, option quality, and actionability;
- Workbench activation, lifecycle, and durable-state fidelity;
- clarity and user-facing usefulness; and
- efficiency: tokens, elapsed time, tool calls, redundant reads, and schema failures.

Use two evaluation cases:

1. **Ambiguous-environment adherence case.** Reuse the original prompt. The expected behavior is one early prerequisite question if the affected environment cannot be discovered; Claude must not rank options or pass a proposal first.
2. **Controlled head-to-head case.** Use the same task and repository snapshot for both agents, state the deployed environment and affected manual-extraction surface in the prompt, and hold model, permissions, fixture access, and stopping conditions constant. This isolates investigation quality and efficiency from a missing user fact.

The existing Codex transcript remains the initial reference. If a new controlled Codex run is needed because the prompt or repository snapshot differs, score it before seeing the remediated Claude result.

## 1. Make the Claude operating prompt decision-aware and economical

Canonical source: `skills/claude-rigor/agents/rigorous-engineer.md`. The installed default agent should be the only full copy of the operating contract. Keep `~/.claude/CLAUDE.md` for user-specific instructions such as Graphify; do not duplicate the full rigor contract there.

Add a compact diagnosis contract near the beginning of the agent instructions, before general repository exploration:

- Identify the user's affected **environment, deployed version, user journey/seam, fixture, and cache/warm state** before deep investigation or option ranking.
- Separate discoverable facts from user-only facts. Inspect discoverable facts; if a missing user-only fact can reorder the options, capture/finalize intake and ask that prerequisite question by itself.
- Do not ask a downstream option-selection question in the same batch as a prerequisite whose answer changes the options.
- A proposal cannot pass while an unresolved fact can materially change its recommendation. Conditional branches are allowed; selecting one branch is not.
- Claims about “current,” “default,” or “deployed” behavior must come from the active worktree or identified deployed revision. Sibling worktrees and in-flight changes may be reported only as prospective alternatives.
- Stop exploring when additional evidence cannot change the ranking, recommendation, or material uncertainty. Prefer one representative fixture matrix and one discriminating intervention over broad codebase and cloud-log sweeps.
- For Workbench records, use the runtime's compact examples and field-level validation error. Never dump whole schemas to repair one rejected field.

Keep the existing causal vocabulary—measurement, contributor, hypothesis, established cause—but move the environment/seam gate ahead of it. Preserve the strong v3 behavior that the Stop review induced: aggregate Lambda data stays service-scoped, authorization failures are not successful endpoint traces, and root-cause language requires a discriminating intervention.

Update `skills/claude-rigor/SKILL.md` and the installer documentation to identify the default agent file as the canonical contract and explicitly prohibit a second full copy in global `CLAUDE.md`.

## 2. Move the decisive review to the start, while retaining one final challenge

Extend the Claude-specific plugin under `skills/claude-rigor/hooks/` with a portable one-shot `PreToolUse` diagnosis preflight. Fold the current behavior of `skills/workbench/scripts/workbench_diagnosis_hook.py` into this plugin-owned hook so a fresh installation does not depend on a separately edited global settings file.

The preflight hook should:

- trigger only for diagnosis/performance requests when the first investigative tool is attempted;
- recognize explicit Workbench invocation and require both Workbench and diagnosing-bugs to have been loaded when applicable;
- block once with a short checklist requiring environment, seam, fixture, and cache/warm-state disposition before routing or ranking;
- tell Claude to ask the environment question first when it is user-owned and ranking-changing;
- allow the retried tool call after the checklist has been surfaced, avoiding a denial loop; and
- fail open on malformed hook input or unrelated requests.

Keep `skills/claude-rigor/hooks/completion_guard.js` as the sole Stop hook. Tighten its diagnosis review so it also checks active/deployed source provenance and whether a recommendation was selected before a ranking-changing uncertainty was resolved. Do not add another generic final-review hook.

Add black-box tests in `tests/runtime/test_claude_completion_guard.py` and a new/relocated preflight-hook test module for:

- Workbench + diagnosis method composition;
- a single early denial and successful retry;
- dependent question ordering;
- local/deployed uncertainty before proposal ranking;
- active worktree versus sibling-worktree provenance;
- aggregate service metrics versus endpoint evidence;
- one final diagnosis review only; and
- fail-open behavior for malformed input and unrelated work.

## 3. Make installation singular, idempotent, and inspectable

Add an idempotent PowerShell installer/migrator in `scripts/` for the Claude harness. It should install/update `claude-rigor`, preserve unrelated global settings and personal `CLAUDE.md` sections, and report the effective hook inventory.

The migration must:

- remove only the known legacy global `~/.claude/hooks/completion_guard.py` Stop registration;
- remove the separately registered Workbench diagnosis PreToolUse entry after the equivalent plugin hook is active;
- leave unrelated hooks, permissions, status-line settings, plugins, and personal instructions untouched;
- detect and report any additional Stop hook rather than silently deleting an unknown hook;
- verify that the effective configuration contains exactly one diagnosis preflight and one `claude-rigor` Stop review; and
- be safe to run repeatedly with the same result.

Update `README.md` and `tests/runtime/test_claude_rigor_distribution.py` so direct-GitHub and marketplace installation paths produce the same self-contained harness. Add a settings-migration fixture test covering comments/unknown keys where the selected JSON editing approach supports them; otherwise document that Claude settings are strict JSON and preserve all unknown keys structurally.

## 4. Add only the Workbench support needed to cut Claude's ceremony

Do not build a general post-start correction engine in the first tranche. The primary fix is preventing a proposal from starting or passing on an unresolved environment premise.

Make two bounded, harness-neutral Workbench improvements:

1. In `skills/workbench/SKILL.md` and `references/routing.md`, state the dependency rule explicitly: resolve prerequisite facts before dependent choices; a routing assumption cannot replace a user-owned fact when that fact can change the route or ranking.
2. Add a compact handoff-bundle preparation command to `skills/workbench/scripts/workbench.py`. It should accept a small phase summary, artifact paths, findings, uncertainties, and next action, then fill runtime-owned boilerplate, hashes, lineage, phase/activity identifiers, `why_next`, and proof structure. It must emit a bundle for inspection and existing `accept-handoff` validation, not bypass validation.

The helper is justified only if it removes the four schema-repair loops seen in v3. Test it with golden frame, discovery, proposal, and implementation-plan bundles. Keep the underlying schemas unchanged unless a concrete helper test proves a schema change is necessary.

For the rare case where a material premise changes after lifecycle start, the first release should do exactly what Workbench already promises: record the discrepancy and hold dependent advancement. A full append-only route-correction/rewind command is a separate follow-up only if the remediated live run still crosses a gate prematurely or real usage shows that prevention is insufficient.

## 5. Encode the v3 failures as regression cases

Extend `tests/comparison/workbench-adherence/cases.json` and `tests/runtime/test_workbench_adherence_evals.py` with cases for:

- `environment-before-ranking`: deployed/local identity is established or asked before route-and-start and option ranking;
- `dependent-question-order`: environment and “which option” are not asked simultaneously;
- `proposal-material-uncertainty-gate`: a proposal cannot be accepted while an unresolved answer can reorder it;
- `active-source-provenance`: defaults cannot be taken from sibling or uncommitted future work and described as deployed;
- `single-authoritative-hook`: no duplicate generic Stop review competes with the task-aware review; and
- `bounded-schema-repair`: a field-level validation error leads to one focused repair, not schema-catalog exploration.

The active-source fixture should reproduce the v3 DPI discrepancy: the active client default was 110 DPI and another surface mapped 100% zoom to 140 DPI, so an in-flight 180-DPI value must not be reported as the current deployed default.

## 6. Verify locally, then run a controlled Claude–Codex comparison

Local verification:

- run the focused hook, distribution, Workbench adherence, handoff-helper, and migration tests;
- run the full repository validation suite;
- install into a temporary Claude home and inspect the effective prompt and hook inventory;
- run the installer twice and prove byte-equivalent effective settings on the second run; and
- start a fresh Claude session to verify that plugin activation, not the current session cache, supplies the hooks.

Live validation should use a fresh repository copy or worktree with identical starting state for each agent. Capture complete transcripts plus model, prompt, instruction hash, plugin hash, repository commit/status fingerprint, tool calls, token counts, elapsed time, hook activations, Workbench records, and final answer.

Acceptance thresholds:

- Claude meets or exceeds Codex on every substantive grading dimension and on the weighted total; no correctness dimension may be traded for speed.
- Claude has no unsupported dominant/root-cause claim, no deployed/default claim sourced from another worktree, and no endpoint conclusion derived from aggregate service metrics.
- On the ambiguous case, environment is established or asked before deep investigation, routing, or option selection.
- The durable Workbench proposal matches the final recommendation; there is no unregistered corrective addendum and no advancement on a known-stale premise.
- There are zero Workbench schema-validation failures in the live run.
- Exactly one diagnosis preflight and one task-aware Stop review fire; no legacy generic Stop hook or Ralph hook appears.
- Against v3's approximately 211k-token, 39-minute investigation, the remediated run targets at least a 30% token reduction and 35% elapsed-time reduction, with a hard non-inferiority ceiling of 150k tokens and 25 minutes unless provider latency is separately evidenced. Compare tool calls as a diagnostic metric, not a standalone optimization target.
- If Claude beats the Codex quality score, keep the best-quality candidate among those within the efficiency ceiling. If quality ties, prefer the lower-token/lower-time harness.

Run at least two fresh Claude repetitions before promotion. A candidate that passes once and regresses once is not promoted; diagnose the divergent grading dimension and make one targeted harness change rather than broadening the prompt.

## Rollout and rollback

Promote by versioning the canonical agent prompt and hooks in `skills/claude-rigor`, running the idempotent migrator, and starting a new Claude session. Record the installed prompt and hook hashes beside the evaluation result. Keep timestamped backups of the prior global settings and personal `CLAUDE.md`; rollback restores those files and the prior plugin version, then verifies the old hook inventory in a fresh session.

No application code, infrastructure, customer data, or production deployment is part of this remediation.

## Assumptions and exclusions

- The established grading rubric can be recovered from the prior assessment without redefining its weights.
- Claude Code remains the deployment target for harness enforcement; Workbench instructions and comparison cases remain harness-neutral.
- The user's personal Graphify instructions remain unchanged.
- Provider throttling and model-side nondeterminism are recorded separately from harness-caused inefficiency.
- A general Workbench lifecycle correction mechanism, application performance fixes, and changes to the brownfield application are excluded from the first implementation tranche.

There are no unresolved implementation decisions. The implementer should begin with the frozen comparison fixture, then change the canonical prompt and early hook, consolidate installation, add the bounded Workbench helper, and only then run the live comparison.
