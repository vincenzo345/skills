# Discovery and experiment process

## Current state

The repository already provides 20 dependency-free Python tasks across algorithmic, integration, robustness, and work-discipline categories. `stage` exposes only public instructions and seed files; `verify` runs evaluator-owned acceptance code; `validate` proves each untouched seed is red and each reference overlay is green. The missing layer is campaign orchestration.

Local inspection found Claude Code 2.1.273 and Codex CLI 0.154.0. Both expose non-interactive execution, explicit model selection, machine-readable event streams, and structured-final-output options. Claude additionally exposes system-prompt files, hook events, tool restrictions, worktrees, and an API-only USD cap. Codex exposes explicit sandbox modes, ephemeral runs, configuration overrides, and managed worktrees.

The source-backed product findings, authentication caveat, and DSPy/GEPA fit are in `docs/research/claude-codex-parity-loop.md`.

## Experiment loop

1. **Preflight:** validate config, versions, model identifiers, auth mode, organization approval, total budget, per-run limits, sandbox availability, sealed-set access, and kill switch. This step must not infer API entitlement from a Claude Enterprise seat.
2. **Qualify the controller:** use fake CLIs and reference overlays to prove event parsing, workspace freshness, evaluator separation, redaction, timeouts, process-tree termination, idempotency, and resume.
3. **Freeze baselines:** record vendor-default Claude, the installed Claude instruction as an explicit treatment, and vendor-default Codex. Codex becomes a fixed target for the Claude campaign.
4. **Run development baselines:** randomize paired execution order and repeat the same task/environment cells. Diagnose failures by outcome category rather than by prose style.
5. **Propose one bounded intervention:** instruction change, completion gate, or explicit tool/permission configuration. Keep factors separate until their individual effect is measured.
6. **Screen on development:** reject candidates that violate safety, scope, budget, or primary correctness. Retain full diagnostics only in the durable run store.
7. **Promote on sealed validation:** the proposer receives only aggregate category feedback. A candidate replaces the champion only if it clears the pre-registered utility and regression gates.
8. **Stop search:** stop at operational parity, plateau, a hard usage/time/round limit, operator kill switch, invalidated environment, or repeated infrastructure failure.
9. **Confirm once on sealed holdout:** freeze prompts and configuration before opening the holdout. A failed holdout retires that set; it never becomes another optimization round under the same claim.
10. **Optionally improve Codex:** freeze the Claude conclusion first, then run a separately labeled Codex campaign. Never move the comparison target during Claude optimization.

## Evidence partitions

- **Development:** all 20 current tasks. They may drive diagnosis and prompt changes.
- **Sealed validation:** 12 new tasks balanced across the four categories, stored outside any agent-visible workspace. Only the controller and verifier can resolve their IDs and oracles.
- **Sealed holdout:** 20 new tasks, opened only after the champion and baseline are frozen. Five tasks per category prevent one category from disappearing in the aggregate.

Task count is a cost/precision tradeoff. If the authorized campaign cannot fund this design, the controller reports a pilot result and must not label it parity.

## Metrics and fixed terminal rules

Primary per-run outcomes are acceptance pass, protected-regression pass, forbidden-scope pass, and false-complete (the agent claims success while acceptance fails). Token/usage estimate, wall time, command count, test execution, and diff inspection are secondary diagnostics.

For final comparison, run three paired repetitions per holdout task and bootstrap at the **task** level so repetitions do not masquerade as independent tasks. Operational parity requires all of:

- Claude pass-rate point estimate is no more than 5 percentage points below Codex;
- the one-sided 95% task-cluster bootstrap lower bound is no worse than 10 percentage points below Codex;
- Claude false-complete and scope-violation point estimates are each no more than 5 percentage points worse;
- no task category is more than 15 percentage points behind; and
- neither condition has an infrastructure-invalid rate above 5%.

The two margins distinguish practical target from uncertainty tolerance and must be printed prominently in the report. A campaign may increase repetitions, but never change thresholds after results are visible.

Plateau within scope occurs when either the authorized usage limit is reached or three consecutive completed rounds produce no candidate that improves validation utility by at least 2 percentage points (or one whole validation task) without worsening a primary guardrail, after every observed failure family has received one targeted intervention. A maximum of 12 Claude search rounds is the recommended default ceiling. Budget exhaustion is reported separately from evidence of convergence.

## Remaining execution-time gates

Implementation is decision-complete without selecting paid account details. A real campaign remains disabled until the operator supplies exact Claude and Codex model IDs, confirms permitted auth/billing paths, chooses a total spend or quota cap, and accepts the sealed-task count. Those are run authorizations, not hidden implementation choices.
