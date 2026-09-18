# Claude harness coding evaluations

This suite measures whether a coding-agent run achieved a requested repository outcome. It contains 24 dependency-free Python tasks with evaluator-owned black-box acceptance programs and known-good reference overlays: the original 20-task development set plus four frozen holdout tasks added for the live Claude/Codex parity campaign.

The live parity campaign and its pre/post evidence are recorded in [the Workbench result](../.workbench/work/WB-20260916-CLAUDE-INSTRUCTION-OPTIMIZATION/artifacts/pre-post-results.md). The promoted Claude harness combines contract-oriented instructions with a one-shot completion-review Stop hook. The distributable GitHub package lives under `skills/claude-rigor/`; it is both an Agent Skill and a self-contained Claude Code skills-directory plugin. The original evaluated Python hook remains at `claude_harness_eval/hooks/completion_guard.py`, while the packaged Node implementation is exercised by the same executable hook contract tests.

Functional acceptance is separate from transcript behavior. A task passes only when its executable oracle passes; an agent's completion claim is never used as proof.

## Commands

List the catalog:

```powershell
python -m claude_harness_eval list
python -m claude_harness_eval list --json
```

Stage one task into a new or empty workspace:

```powershell
python -m claude_harness_eval stage config-precedence E:\tmp\config-precedence --json
```

The workspace receives only `TASK.md`, public metadata, and seed files. Run the agent with that directory as its working directory. Do not give it access to this evaluator repository.

Verify the final workspace:

```powershell
python -m claude_harness_eval verify config-precedence E:\tmp\config-precedence --json
```

The verification process exits `0` for acceptance, `1` for a failed or timed-out oracle, and `2` for invalid input. Its JSON includes captured output, duration, exit status, and timeout state.

## Validate the suite itself

The author gate proves that every untouched seed is red and every reference overlay is green:

```powershell
python -m claude_harness_eval validate --repeat 2 --json
```

Validate selected tasks by putting their IDs before the options:

```powershell
python -m claude_harness_eval validate pagination-cursor sqlite-transaction --repeat 3 --json
```

`apply-reference` is an evaluator-authoring command. Never run it inside a model trial:

```powershell
python -m claude_harness_eval apply-reference pagination-cursor E:\tmp\pagination-cursor
```

## Evaluation protocol

For comparisons between global prompts or harness variants:

1. Use the same model, model settings, permissions, time limit, and task revision.
2. Stage a fresh workspace for every attempt.
3. Restrict network access and credentials through the agent harness or operating environment.
4. Run at least three attempts per task and condition.
5. Retain prompt hash, model identifier, suite revision, transcript, commands, final diff, verification JSON, duration, and token/cost data when available.
6. Report task pass rate as the primary result. Report transcript evidence, claim calibration, efficiency, and categories separately.

Suggested prompt-development split:

- 12 development tasks;
- 4 validation tasks;
- 4 private holdout tasks.

Rotate tasks that leak into prompts, transcripts, or public material.

## Safety boundary

The CLI prevents normal staging from copying reference or verifier content into the agent workspace. Verification executes candidate code, so verifier execution is still trusted-host activity. Agent execution now has a separately qualified Docker boundary; do not treat that as proof that provider authentication or network egress is safe.

Qualify the local Docker engine and an already-present immutable image without invoking either model:

```powershell
python -m claude_harness_eval isolation qualify --root .harness-runs/isolation --image python:3.12-slim --json
```

Qualification enforces and probes a read-only root, numeric non-root user, dropped capabilities, no-new-privileges, no network, CPU/memory/PID ceilings, bounded tmpfs/output/time, one staged-workspace mount, host-secret and evaluator absence, and forced timeout cleanup. The resulting `qualification.json` and `qualification.sha256` bind the Docker server, immutable image, complete policy, and canary results.

Exercise the same validated boundary with a non-provider fake command:

```powershell
python -m claude_harness_eval isolation run --qualification .harness-runs/isolation --workspace E:\tmp\staged-task --json -- python -c "print('fake agent')"
```

The runner rejects workspaces containing control-plane roots such as `.git`, `.workbench`, `.claude`, or `.codex`, as well as links. Never mount the evaluator repository, home directory, credential directories, or Docker socket.

## Current proof boundary

Repository tests and `validate` establish local catalog integrity, no-op failure, reference success, and runner behavior on the current machine. They do not establish:

- Claude or Codex comparative performance;
- Windows/Linux parity until CI runs both;
- human solvability or independent instruction-to-assertion review;
- safety against hostile generated code;
- provider credential or egress safety, because qualified agent containers currently have networking disabled and receive no provider credentials;
- improvement caused by the global Claude instruction.

The benchmark-design evidence and provenance are recorded in [the research note](./research/claude-harness-eval-benchmarks.md).

## Zero-cost experiment controller

The experiment commands orchestrate reproducible campaigns without relying on an agent's completion claim. The checked-in example is intentionally fake: its Claude condition applies evaluator reference overlays and its Codex condition makes no changes. That makes controller behavior deterministic and spends no model quota.

```powershell
python -m claude_harness_eval doctor --config docs/examples/claude-harness-campaign.toml --json
python -m claude_harness_eval experiment init --config docs/examples/claude-harness-campaign.toml --root .harness-runs/dry-run --json
python -m claude_harness_eval experiment run --root .harness-runs/dry-run --json
python -m claude_harness_eval experiment report --root .harness-runs/dry-run --json
```

`experiment resume` is an alias for the idempotent run operation. Completed, identity-matching run artifacts are reconciled after an interrupted state write and are never rerun. `experiment stop --reason <text>` durably prevents additional launches.

Each campaign stores a normalized immutable manifest, append-only events, atomic state projection, per-run identity manifest, verifier result, result digest, and JSON/Markdown reports. Reusing a root with different configuration is rejected.

Live configuration is fail-closed. It requires explicit organization permission, live authorization, an exact qualification artifact path and SHA-256, and a positive total cost cap. `doctor` and `experiment run` revalidate artifact integrity plus current Docker server, image, and policy identity. Provider execution remains disabled until credential injection and restricted provider egress receive separate authorization and proof. These commands do not invoke a model or modify global Claude/Codex prompts or hooks.

A live configuration uses these fields rather than a self-asserted boolean:

```toml
live_authorized = true
organization_permission_confirmed = true
qualification_file = ".harness-runs/isolation"
qualification_sha256 = "<sha256 of qualification.json>"
max_total_cost_usd = 1.0
```

## Resumable harness optimization

The optimization controller adds a champion-challenger loop around fresh Claude sessions. It
stores every candidate prompt, session result, rubric evaluation, and promotion decision with a
SHA-256 sidecar. A challenger is promoted only when every hard gate passes, no scored dimension
regresses, and weighted quality or efficiency improves by the configured minimum. The loop stops
on its frozen target, maximum rounds, repeated lack of progress, a provider failure, or its session
budget.

Run the checked-in zero-cost campaign:

```powershell
python -m claude_harness_eval optimize init `
  --config docs/examples/claude-optimization-loop.toml `
  --root .harness-runs/optimization-dry-run --json
python -m claude_harness_eval optimize run `
  --root .harness-runs/optimization-dry-run --json
python -m claude_harness_eval optimize report `
  --root .harness-runs/optimization-dry-run --json
```

`optimize resume` is the same idempotent operation as `optimize run`. It reuses evidenced session
and evaluation records and refuses any candidate, result, evaluation, or decision whose digest no
longer matches. `optimize stop --reason <text>` durably prevents further work.

Fake mode uses deterministic local runner, evaluator, and improver implementations. It proves the
controller without invoking Claude or Codex. Live mode instead launches Claude with streamed JSON,
hook events, a fresh persisted session so transcript-aware hooks execute, a pinned model and effort,
a candidate prompt file, and an
optional session-only plugin. Codex receives only the bounded transcript packet and frozen rubric
in a read-only ephemeral structured-output invocation; it cannot browse the campaign directory.

Live mode is deliberately operator-triggered. Its config must include:

- `live_authorized = true`;
- a positive `max_budget_usd_per_run`;
- an existing disposable `workspace` containing `.harness-scenario.json`;
- an explicit `settings_file` defining the permitted tools for that disposable workspace; and
- real Claude, evaluator, and improver model identifiers.

Initialization binds the workspace marker, scenario prompt, rubric, settings, and plugin bytes.
Changing any of them blocks later runs. Use a secret-scrubbed disposable workspace; never point the
loop at the source repository or a home directory. The loop never installs a winning candidate into
global Claude configuration. Promotion means only that the candidate becomes the campaign's next
champion; deployment remains a separate reviewed operation.
