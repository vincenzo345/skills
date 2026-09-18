# Claude harness optimization loop — implementation and verification

## Outcome

Implemented a durable champion-challenger controller that can start fresh Claude sessions, send a pinned scenario prompt, grade the resulting transcript and Workbench state, ask Codex for one bounded prompt improvement, retest it, and promote only a non-regressing challenger. The complete loop is executable in deterministic fake mode without provider calls; live mode is present but remains operator-triggered and fail-closed.

## Implementation

- `claude_harness_eval/experiment/optimization.py`
  - strict TOML configuration and frozen JSON rubric validation;
  - immutable candidate prompts, run observations, evaluations, and round decisions with SHA-256 sidecars;
  - append-only idempotent events and atomic resumable state;
  - champion-challenger comparison that rejects hard-gate failures and any dimension regression;
  - target, maximum-round, no-progress, session-budget, provider-error, timeout, and manual-stop terminals;
  - deterministic fake runner, evaluator, and improver;
  - live Claude runner using streamed JSON, hook events, no session persistence, pinned model/effort, session prompt, explicit settings, and optional session-only plugin;
  - fresh copied workspace per attempt from a schema-v1 secret-scrubbed fixture;
  - captured and hash-bound resulting workspace and Workbench state;
  - blinded, read-only, ephemeral Codex structured evaluator and prompt-only improver;
  - bounded transcript packets and 0–5 rubric score validation; and
  - reporting plus artifact and runtime-input integrity checks on every resume, including completed campaigns.
- `claude_harness_eval/__main__.py` exposes `optimize init|run|resume|report|stop`.
- `claude_harness_eval/experiment/__init__.py` exports the optimization API.
- `tests/comparison/claude-codex-investigation/rubric.json` freezes the initial comparison dimensions, weights, hard gates, and efficiency thresholds.
- `docs/examples/claude-optimization-*` supplies a zero-cost campaign, baseline prompt, and deployed-environment scenario.
- `docs/claude-harness-evals.md` documents dry-run, live prerequisites, integrity, isolation, promotion, and deployment boundaries.
- `tests/runtime/test_claude_harness_optimization.py` covers the public state machine and live command boundary.

## Durable model and safety disposition

The loop adds filesystem persistence only; it does not change a database. Campaign manifests bind the configuration plus scenario, rubric, settings, plugin, workspace marker, and pristine workspace-template hashes. Candidate prompts, run results, evaluations, and decisions are immutable evidenced records. `state.json` is an atomic projection and `events.jsonl` is append-only with deterministic event IDs, so retries do not duplicate events.

Live configuration requires explicit authorization, per-run budget, an explicit settings file, and a fixture marker declaring `secret_scrubbed: true`. Each Claude attempt uses a fresh fixture copy. Codex evaluator/improver calls run from an empty temporary directory under a read-only sandbox and receive only explicit structured input. The improver may change prompt text but cannot generate or execute hook source. The controller never installs a candidate globally.

## Verification

- `python -m pytest -q` → **186 passed** in 161.90 seconds.
- `python scripts/validate-skills.py` → **12 skills validated**; metadata, invocation policies, references, links, catalog, manifest, and portability passed.
- `git diff --check` → passed with no whitespace errors.
- `python -m py_compile claude_harness_eval/experiment/optimization.py` → passed.
- Zero-cost public CLI journey:
  - `optimize init` initialized `claude-brownfield-dry-run-9e8834752590`;
  - `optimize run` evaluated the baseline and two challengers across six simulated sessions;
  - `CAND-001` and `CAND-002` were promoted without dimension regressions;
  - the loop stopped at `target-met` with `CAND-002`;
  - `optimize resume` returned the same terminal state without new work; and
  - `optimize report` reported baseline score 2.0, challenger scores 3.0 and 4.0, and decreasing fake token/time metrics.
- Focused contracts additionally prove higher-total dimension regressions are rejected, budget exhaustion blocks without promotion, completed resumes detect changed frozen rubrics, result tampering is detected, decision reconciliation does not duplicate events, live commands include the bounded session flags, fresh fixture copies preserve the original, and resulting Workbench state is captured.

## Proof boundary

Verified: controller behavior, persistence, integrity, fake multi-round orchestration, CLI behavior, candidate comparison, failure handling, and live command construction.

Not yet verified: an actual Claude or Codex provider invocation, the qualitative rubric's agreement with human grading, Claude performance parity with Codex, the deployed global harness, or the real brownfield fixture. Those require a separately authorized live campaign and are not implied by local verification.

No commit, global installation, deployment, or paid model run was performed.
