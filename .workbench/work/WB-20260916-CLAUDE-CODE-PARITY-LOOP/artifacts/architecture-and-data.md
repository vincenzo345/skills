# Architecture and durable data design

## Component boundaries

Extend `claude_harness_eval` with these deep seams:

- `experiment/config.py`: parse and validate a versioned TOML campaign manifest; reject credentialed mode when required limits or exact model IDs are absent.
- `experiment/controller.py`: own the state machine, randomized schedule, idempotency, budget ledger, stop conditions, and resume behavior.
- `experiment/adapters/base.py`: define `AgentAdapter.prepare()`, `command()`, `parse_event()`, `usage()`, and `completion_claim()` without embedding scoring policy.
- `experiment/adapters/claude.py`: invoke `claude -p --output-format stream-json` with explicit prompt/config files and a controlled customization mode.
- `experiment/adapters/codex.py`: invoke `codex exec --json --ephemeral --sandbox workspace-write` with explicit working root and developer instructions.
- `experiment/executor.py`: launch argv without a shell, sanitize the environment, enforce timeout/output/process-tree limits, and capture raw bytes.
- `experiment/scoring.py`: join executable verifier results with normalized claims and scope checks; vendor events are diagnostic inputs only.
- `experiment/statistics.py`: paired summaries and task-cluster bootstrap with fixed seed and testable pure functions.
- `experiment/optimizer.py`: champion–challenger interface with deterministic/manual candidates first and an optional GEPA implementation later.
- `experiment/store.py`: atomic immutable artifacts, append-only events, content hashes, and resumable state projection.
- `experiment/report.py`: render a machine-readable summary and Markdown report with limitations and terminal disposition.

Add CLI commands under the existing module:

```text
python -m claude_harness_eval doctor --config campaign.toml
python -m claude_harness_eval experiment init --config campaign.toml
python -m claude_harness_eval experiment run <experiment-id> [--dry-run]
python -m claude_harness_eval experiment resume <experiment-id>
python -m claude_harness_eval experiment report <experiment-id>
python -m claude_harness_eval experiment stop <experiment-id> --reason <text>
```

`doctor` and `--dry-run` never invoke a model. `run` refuses local-host execution unless the manifest explicitly selects a qualified isolation backend; an escape hatch, if implemented, must be named `--unsafe-local` and cannot be the default or usable in unattended mode.

## Isolation and credential boundary

Use two disposable environments per attempt:

1. **Agent environment:** contains only the staged synthetic workspace, provider connectivity, revocable evaluation credentials, and explicit CLI configuration. It has no evaluator source, personal home, unrelated repository, SSH/cloud credentials, or general outbound network.
2. **Verifier environment:** receives the final workspace snapshot and hidden oracle, has no provider credentials or network, and is destroyed after verification.

The campaign cannot leave preflight until canaries prove that the agent cannot read the evaluator, parent workspace, or a planted secret; cannot write outside its task root; and cannot use disallowed network destinations. Claude sandbox configuration must fail closed if unavailable. Codex uses `workspace-write`; neither agent may use a full-access bypass without a separate external sandbox.

Credential values never enter manifests or event logs. The launcher supplies them at process scope, the child shell/test environment removes them, and the redactor scans raw and normalized outputs before persistence. Synthetic tasks avoid employer or production data even when enterprise auth is used.

## Durable model

The store root is `.harness-runs/<experiment-id>/` (gitignored):

```text
manifest.json                    frozen normalized configuration
state.json                       atomic replaceable projection
events.jsonl                     append-only controller events
candidates/<candidate-id>/       instruction bytes, metadata, lineage, hashes
runs/<run-id>/manifest.json      immutable run identity and environment
runs/<run-id>/vendor.jsonl       redacted raw vendor events
runs/<run-id>/stdout.bin
runs/<run-id>/stderr.bin
runs/<run-id>/diff.patch
runs/<run-id>/verification.json
runs/<run-id>/result.json
decisions/<sequence>.json        promotion, stop, invalidation records
reports/summary.json
reports/report.md
```

Stable identities:

- `experiment_id`: caller label plus manifest SHA-256.
- `candidate_id`: SHA-256 of exact instruction/config bytes and parent candidate.
- `run_id`: SHA-256 of experiment, agent, candidate, task revision, and attempt.
- `decision_id`: monotonic sequence plus digest of compared evidence.

Run states are `queued → running → agent-finished|agent-failed → verifying → completed|invalid|aborted`. Only the controller mutates `state.json`, using temp-file, fsync, and atomic replace. Events and terminal run artifacts are never overwritten. Resume derives completed run IDs from valid hashed artifacts, marks orphaned `running` attempts interrupted, and schedules only missing cells. Reusing an ID with different bytes is a hard conflict.

Retention defaults to manifests, normalized events, diffs, verification, decisions, and reports. Raw stdout/stderr may be deleted only by an explicit retention operation after their hashes and redacted normalized events are durable. Sealed oracles live outside this tree and are referenced by opaque revision/hash.

## Failure behavior

- Unknown vendor event types are retained and ignored by the normalizer, not fatal.
- Rate limits and provider outages become retryable infrastructure outcomes and never task failures.
- Authentication, sandbox-canary, budget-ledger, manifest-integrity, or sealed-set failures stop the campaign.
- Per-run retry uses the same cell identity with an incremented infrastructure-attempt field; it cannot silently create extra statistical repetitions.
- Controller crash, Ctrl+C, or kill-switch observation terminates process trees, records an interruption, and leaves a resumable state.
- A model completion claim never bypasses `verify`.
