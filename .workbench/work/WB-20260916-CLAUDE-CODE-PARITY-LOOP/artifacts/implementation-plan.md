# Automated Claude Code parity loop — implementation plan

## Summary

Build a harness-neutral, resumable champion–challenger controller on top of the existing 20-task evaluator. It will compare pinned Claude Code and Codex conditions, improve Claude's explicit instruction/gate configuration against development and sealed validation evidence, and stop at pre-registered operational parity or a bounded plateau. Codex improvement is a separate secondary campaign after the Claude target is frozen.

No real model invocation is part of implementation verification. Credentialed execution remains locked behind an explicit campaign authorization containing exact models, permitted auth modes, and hard usage limits.

## Implementation changes

### 1. Define contracts and fake the vendors first

- Add `claude_harness_eval/experiment/` with typed dataclasses or equivalent immutable value objects for `CampaignConfig`, `Candidate`, `RunCell`, `RunResult`, `PromotionDecision`, `Budget`, and `TerminalDisposition`.
- Add a versioned TOML input contract and JSON Schemas for normalized manifest, run result, promotion decision, and summary report. Unknown input fields fail validation; output readers tolerate additive vendor event fields.
- Add `AgentAdapter` and `IsolationBackend` protocols. Ship deterministic fake adapters and a fake isolation backend used by all controller tests.
- Extend `__main__.py` with `doctor` and `experiment init/run/resume/report/stop`; preserve all current commands and exit codes.
- Exit `0` for successful command completion, `1` for a completed experiment with a non-parity disposition when requested by CI, and `2` for invalid input/preflight. Provider and infrastructure failures use a distinct documented nonzero code.

### 2. Implement immutable storage and resume

- Implement the directory model in `architecture-and-data.md`, canonical JSON encoding, SHA-256 integrity, append-only event writes, and atomic `state.json` replacement.
- Make run scheduling idempotent by stable run ID. Persist the schedule before launching a child process.
- On resume, validate the frozen manifest and all referenced hashes; reconcile orphaned attempts without counting them as model outcomes; never rerun a completed cell.
- Add total and per-agent ledgers for calls, reported tokens, reported cost, wall time, valid statistical repetitions, and infrastructure retries. The outer total limit always wins over adapter-specific caps.
- A durable stop record is checked before every launch and while runs are active.

### 3. Add the execution and isolation seam

- Build subprocess argv arrays without shell interpolation. Capture stdout/stderr separately with byte limits and concurrently drain both streams.
- Sanitize inherited environment variables through an allowlist. Prefer OS-protected login state or a local credential broker that injects provider authorization only into the CLI's outbound request path. If a provider supports only an environment key, use a dedicated revocable evaluation key and prove with a child-process canary that generated commands cannot read it; otherwise block live runs rather than trusting convention.
- Enforce wall time, idle time, process count, disk, and output limits and terminate the full process tree on breach.
- Implement agent and verifier isolation as distinct backend operations. Default `run` refuses a backend that has not passed the current campaign's secret, path, write, network, and process-cleanup canaries.
- Initialize each staged task as a fresh local Git repository with a baseline commit so both adapters receive the same diffable workspace without remotes.

### 4. Add Claude and Codex adapters

- Claude adapter: pin `claude --version`; use print mode and `stream-json`; pass the candidate instruction explicitly by file; select exact model and effort; disable session persistence; load only the declared settings/hooks/tools; capture hook events. Keep vendor-default, installed-global-prompt, prompt-only, gate-only, and prompt-plus-gate as distinct treatments. Do not use `--bare` with enterprise OAuth unless a supported key/helper is separately configured.
- Codex adapter: pin `codex --version`; use `codex exec --json --ephemeral --sandbox workspace-write -C <workspace>`; pass exact model and controlled developer instructions; isolate user configuration/rules where supported; record any unavoidable `AGENTS.md` discovery in the manifest.
- Parse both streams into a small normalized event vocabulary while retaining redacted raw JSONL. Unknown events do not crash the run.
- Extract completion claims only for false-complete scoring. File state and evaluator output remain authoritative.

### 5. Score and compare

- Run the existing `verify` seam only in the verifier environment; add protected-file and allowed-change checks before executing candidate code.
- Normalize outcomes into accepted, failed, invalid-infrastructure, aborted, scope-violation, and false-complete flags.
- Implement randomized paired schedules with a recorded seed and balanced execution order.
- Implement pass-rate differences, category summaries, false-complete/scope differences, infrastructure rate, and deterministic task-cluster bootstrap intervals. Unit-test all calculations on fixed fixtures.
- Reports must name model/CLI/prompt/task/environment hashes, repetitions, excluded invalid runs, margins, budget consumed, and limitations. Never translate “not statistically different” into parity.

### 6. Implement promotion and optimization

- Start with a deterministic candidate queue: vendor baseline, installed prompt, prompt-only edits, completion-gate-only, and prompt-plus-gate. Each candidate changes one declared factor or carries explicit parent lineage.
- Development runs may emit task-level diagnostics. Validation promotion receives only aggregate category metrics and bounded failure summaries; holdout emits no optimization feedback.
- Repeated validation use is treated as model selection, not final proof. Record every validation exposure, cap promotion rounds, and retire the validation set after the campaign; only the untouched holdout supports the terminal comparison.
- A challenger replaces the champion only when it improves validation utility by at least 2 percentage points or one whole validation task and does not regress any primary guardrail beyond its fixed margin.
- Implement parity, plateau, budget, round, invalid-environment, and operator-stop conditions exactly as recorded in `discovery-and-loop.md`.
- Add `GepaCandidateProposer` only after fake and hand-authored loops pass end to end. Wrap GEPA `optimize_anything`: the candidate artifact is instruction text; the evaluator launches the external CLI and returns score plus concise feedback. Give GEPA its own proposal-model budget and never expose sealed tasks or raw holdout failures.

### 7. Add sealed sets and run gates

- Keep the current 20 tasks as development material. Author 12 sealed validation and 20 sealed holdout tasks with the existing red-seed/green-reference authoring gate and balanced categories.
- Store sealed assets outside the agent and proposer readable roots. The repository may contain only opaque task-set IDs, hashes, and public metadata if true secrecy cannot be maintained here.
- `doctor` must fail credentialed mode unless organization permission, auth mode, exact model IDs, total usage cap, per-run time/cost limits, concurrency, isolation backend, task-set revisions, repetitions, and random seed are supplied.
- Recommended first campaign ceilings: 12 Claude optimization rounds, at most two concurrent model runs, three valid repetitions for final holdout, and a user-selected total quota/spend cap. There is deliberately no default dollar amount.

### 8. Run the secondary Codex branch

- Freeze the Claude champion, terminal disposition, and original Codex baseline.
- Create a new linked experiment ID for Codex instruction optimization; do not rewrite the Claude comparison.
- Reuse the same development/validation machinery. A fresh or retired holdout is required for a new generalization claim.
- Report baseline Codex, optimized Claude, and optimized Codex as three distinct conditions. Improvement to Codex is never used retroactively to deny or grant the original parity result.

## Test plan

### Unit tests

- Manifest validation, canonical hashes, stable IDs, state transitions, atomic writes, budget arithmetic, redaction, event normalization, retry classification, promotion rules, plateau rules, and bootstrap calculations.
- Golden vendor-event fixtures for known, unknown, partial, malformed, and over-limit streams.
- Exact argv tests prove prompts are passed as files/arguments without shell expansion and that prohibited flags cannot be selected.

### Integration tests with no model calls

- Fake Claude and Codex executables exercise success, functional failure, false completion, rate limit, timeout, hung child process, output flood, interrupted write, malformed JSONL, and unknown event types.
- Crash after every durable transition, then resume; assert no completed cell reruns and no interrupted attempt becomes a statistical repetition.
- Stage a task, initialize Git, apply fake edits, snapshot, verify in the separate backend, and prove the oracle was never visible to the agent process.
- Drive champion → challenger → validation promotion → parity and champion → three rejected rounds → plateau as deterministic end-to-end scenarios.

### Security and isolation qualification

- Canary attempts to read the evaluator, parent repository, home credentials, and planted secret; write outside the workspace; connect to a disallowed host; spawn a surviving child; and exceed disk/output/process limits. Every attempt must fail closed and leave no surviving process.
- Scan persisted artifacts for planted credentials and verify raw logs are redacted before commit to the store.
- Prove verifier execution has no provider credentials or network.

### Campaign acceptance

- Re-run existing suite author validation and repository tests.
- Run a zero-cost dry campaign with fake adapters across all 20 current tasks and verify deterministic report reproduction from the same store.
- With separate user authorization, run a two-task, one-repetition live smoke below a small explicit cap; inspect artifacts before expanding.
- Run baselines, optimization, validation, and the holdout only after each prior gate is accepted. The final report must independently reproduce every aggregate from immutable run records.

## Rollout and operations

Land the controller disabled by default. Phase 1 supports fake/dry runs only; phase 2 qualifies isolation; phase 3 permits a bounded live smoke; phase 4 permits a capped Claude campaign; phase 5 optionally enables GEPA; phase 6 optionally starts a separate Codex campaign. Each expansion is reversible by disabling the corresponding manifest capability. No migration or backfill is required because every campaign has a schema version and immutable root; incompatible changes create a new experiment.

Monitor valid/invalid run rate, spend/quota consumption, wall time, provider errors, redaction hits, sandbox failures, and pass/false-complete/scope metrics. Any integrity, credential, or isolation alert stops launches immediately.

## Assumptions and deferred execution choices

- Exact model IDs and auth mechanisms are not safely inferable from installed CLIs or an Enterprise seat; `doctor` requires them at run time.
- The user chooses the total quota/spend cap after seeing baseline smoke cost. No model is invoked without it.
- True sealed sets cannot live in a directory readable by the optimizer. Their storage location is deployment configuration, while their opaque interface is fixed here.
- UX/accessibility impact is none for the first machine-oriented CLI; reports remain plain Markdown and JSON.
- No database, external service, deployment, or backwards data migration is required for the first implementation.

## Delivery order

1. Contracts, fake adapters, CLI skeleton, and backward-compatibility tests.
2. Immutable store, budget ledger, stop/resume, and crash testing.
3. Execution seam, separate verifier, isolation backend, and security canaries.
4. Claude/Codex adapters and golden event fixtures.
5. Scoring, statistics, reporting, and deterministic replay.
6. Candidate lineage, promotion, parity/plateau logic, and manual queue.
7. Sealed validation/holdout authoring and access boundary.
8. Authorized two-task smoke, then capped baseline campaign.
9. Optional GEPA proposer after controller qualification.
10. Optional linked Codex-improvement campaign after Claude freezes.
