# Automating a Claude Code–Codex parity loop

Research date: 2026-09-16. This note uses only first-party product documentation and official project sources. No model calls, authentication checks, or configuration changes were made.

## What can be automated today

| Surface | Claude Code | Codex CLI | Benchmark implication |
| --- | --- | --- | --- |
| Scripted execution | `claude -p`; Anthropic recommends `--bare` for scripts and SDK calls | `codex exec`, including `--ephemeral` | Give each attempt a fresh workspace and a noninteractive process with a hard timeout. |
| Machine-readable trace | `--output-format json`; `stream-json --verbose` emits JSON events and ends with a result containing response, cost, and session metadata | `--json` emits JSONL events for turns, items, commands, file changes, tools, plans, errors, and usage | Normalize both streams into one run record, while retaining the raw vendor event log. |
| Final structured response | `--json-schema` with JSON output | `--output-schema`, plus `--output-last-message` | Use schemas only for the agent's completion claim; executable acceptance tests remain authoritative. |
| Per-run prompt injection | `--append-system-prompt-file` preserves Claude Code's defaults; `--system-prompt-file` replaces them | Per-run config overrides include `developer_instructions`; Codex also loads `AGENTS.md` files | Hash and record every instruction source. Prefer additions over replacing vendor defaults for the primary comparison. |
| Local-config isolation | `--bare` ignores normal local settings, hooks, MCP, plugins, and OAuth/keychain state; explicit flags can add selected settings back | `--ignore-user-config` skips `config.toml`, and `--ignore-rules` separately skips exec-policy rules, but neither is documented as suppressing `AGENTS.md` discovery | Use a dedicated benchmark home plus controlled workspace files; do not assume a single ignore flag creates a clean baseline. |
| Completion gates | A `Stop` hook can block stopping and return a reason; Claude forces termination after eight consecutive blocks | No equivalent completion-blocking lifecycle hook was established from the cited Codex CLI pages | Put the final gate in the vendor-neutral outer controller. Test Claude's Stop hook as a separate treatment, not as part of the baseline. |

Sources: Anthropic's [programmatic/headless guide](https://code.claude.com/docs/en/headless), [CLI reference](https://code.claude.com/docs/en/cli-usage), and [hooks reference](https://code.claude.com/docs/en/hooks); official OpenAI documentation for [Codex non-interactive mode](https://developers.openai.com/codex/noninteractive), the [CLI reference](https://developers.openai.com/codex/cli/reference), [AGENTS.md discovery](https://developers.openai.com/codex/guides/agents-md), and the [configuration reference](https://developers.openai.com/codex/config-reference).

## Authentication and licensing caveat

Claude Code explicitly supports login with a Claude for Teams or Enterprise account. Anthropic documents Claude Console as a separate, API-billed setup and separately describes Console roles that can create API keys. In addition, `--bare` skips OAuth and keychain reads and requires `ANTHROPIC_API_KEY` or an `apiKeyHelper` supplied through explicit settings. Therefore:

- An Enterprise seat is sufficient evidence that an invited user can log into Claude Code, but the cited documentation does **not** establish that the seat grants general Anthropic API access or API credits.
- An Enterprise-authenticated `claude -p` trial may be possible without bare mode, but it can inherit local state. A reproducible `--bare` trial needs separately provisioned key/helper authentication.
- Before unattended or high-volume trials, the organization administrator should confirm that automated benchmark use is permitted and choose the supported billing/authentication path.

These distinctions come from Anthropic's [authentication guide](https://code.claude.com/docs/en/team) and [programmatic guide](https://code.claude.com/docs/en/headless). The conclusion about API entitlement is deliberately stated as an inference from separate documented login and Console/API paths, not as a contractual licensing determination.

Codex can reuse saved CLI authentication or use a narrowly scoped `CODEX_API_KEY`. Official OpenAI documentation recommends API keys as the default automation path, warns against exposing a key to repository-controlled processes, and treats saved `auth.json` as a password. ChatGPT-managed authentication is an advanced path for trusted runners that need workspace entitlements. See [Codex non-interactive authentication](https://developers.openai.com/codex/noninteractive) and [Codex authentication](https://developers.openai.com/codex/auth).

## Safe execution boundary

The benchmark runs code written by an agent. Treat each attempt as untrusted:

1. Materialize one disposable workspace per task, agent, treatment, and repetition. Never let candidates share a modified worktree.
2. Keep the evaluator and hidden tests outside the agent-writable tree. Give the agent only the task fixture and public instructions.
3. Deny network access except the model-provider connection required by the launcher. Do not mount personal home directories, SSH keys, cloud credentials, or unrelated repositories.
4. Scope provider credentials to the launcher rather than the build/test child environment. Redact credentials and environment values from captured events.
5. Use explicit least-privilege settings. Claude's sandbox should set `failIfUnavailable: true` and disable unsandboxed fallback; Codex coding runs should explicitly use `workspace-write`, never `danger-full-access` unless a second isolation boundary contains the whole process.
6. Enforce wall-clock, process-tree, output-size, model-usage, and concurrency limits in the outer controller, with a durable kill switch.

Claude's sandbox can otherwise warn and fall back to unsandboxed execution when unavailable, and it has a configurable unsandboxed retry escape hatch; the strict settings above close both paths. See Anthropic's [sandbox documentation](https://code.claude.com/docs/en/sandboxing). Codex defaults to read-only in noninteractive mode and documents `workspace-write` for editing tasks and `danger-full-access` only for controlled runners; see [Codex non-interactive mode](https://developers.openai.com/codex/noninteractive).

## Reproducible evaluation design

The following is a proposed experimental design, not a vendor claim.

### Freeze the experimental unit

For every run, record the task revision, fixture hash, acceptance-test hash, agent and CLI version, exact model identifier, reasoning/effort settings, instruction hashes, tool policy, sandbox policy, dependency lock hashes, OS/container image, attempt number, timestamps, timeout, and raw event-log checksum. Pin versions where the products allow it. OpenAI notes that model outputs vary and that behavior can change across snapshots, recommending pinned versions plus evals for consistency ([API compatibility guidance](https://platform.openai.com/docs/api-reference/debugging-requests)).

### Separate development from proof

Partition tasks before optimization:

- **Development:** visible failure feedback drives prompt and gate changes.
- **Validation:** selects among candidate treatments; it is not used to write new candidates.
- **Holdout:** opened only for a promotion decision. A failed holdout does not become another development round without retiring and replacing that holdout.

The existing executable tasks are useful development/validation material, but a credible final parity claim needs untouched holdout tasks that the optimizer and candidate agents cannot read.

### Pair runs and repeat them

Run Claude and Codex on the same task revision, environment image, resource limits, and time window. Randomize execution order and repeat each cell because agent outputs are nondeterministic. Analyze paired task-level differences rather than only aggregate percentages.

Primary outcomes should be deterministic:

- acceptance-test pass/fail;
- regression-test pass/fail;
- forbidden-scope modification pass/fail; and
- **false-complete rate:** the agent claims completion while acceptance tests fail.

Keep tokens, wall time, tool calls, and estimated cost as secondary efficiency outcomes. Behavioral trace metrics such as “ran tests” or “inspected the diff” are diagnostic, not substitutes for correctness.

### Define the two stopping outcomes before running

- **Operational parity:** on the untouched holdout, Claude's task pass rate is non-inferior to the fixed Codex baseline by a predeclared margin, while false-complete and scope-violation rates are no worse. Report paired confidence intervals; do not equate “no significant difference” with parity.
- **Capability plateau:** the authorized run budget is exhausted, or no challenger produces a predeclared minimum validation improvement for a fixed number of consecutive rounds, after allowing each failure family one targeted intervention. Confirm the incumbent once on holdout and stop.

This makes “keep iterating” finite and auditable. A model can also be maxed only **within the tested harness, model version, tasks, and budget**, not universally.

## DSPy and GEPA: where they fit

DSPy optimizers take a DSPy program, a metric, and training inputs, then tune prompt/program parameters to improve that metric. MIPROv2 jointly searches instructions and examples; DSPy's GEPA accepts explicit metric-call budgets, a validation set, and a seed ([DSPy optimizer overview](https://github.com/stanfordnlp/dspy/blob/main/docs/docs/learn/optimization/optimizers.md), [GEPA API](https://github.com/stanfordnlp/dspy/blob/main/docs/docs/diving-deeper/gepa-in-depth.md)). Those APIs are natural when the system under test is a DSPy program, but an external coding CLI with filesystem side effects is not a documented drop-in DSPy predictor.

The better fit is the official GEPA package that DSPy uses. Its `optimize_anything` interface is intended for arbitrary text artifacts with a caller-supplied evaluator, and the official FAQ directs non-DSPy agent optimization to that interface ([GEPA integration guide](https://github.com/gepa-ai/gepa/blob/main/docs/docs/guides/index.md), [GEPA FAQ](https://github.com/gepa-ai/gepa/blob/main/docs/docs/guides/faq.md)). A safe adapter would:

1. Treat the Claude instruction document as the candidate artifact.
2. For each development example, launch the external CLI in a disposable workspace with that candidate supplied explicitly.
3. Run the deterministic verifier outside the agent process.
4. Return a numeric score plus concise failure feedback, while storing full logs separately.
5. Let GEPA propose candidates only from development feedback; use the independent controller for validation and holdout promotion.

GEPA/DSPy still requires a reflection/proposal language model and therefore its own supported authentication and usage budget. It does not turn a Claude Enterprise seat into Anthropic API access. Start with a small hand-authored champion/challenger loop to validate the evaluator; introduce GEPA only after the metrics, isolation, and budget accounting are trustworthy.

## Recommended experiment sequence

1. **Preflight:** confirm organizational permission, authentication mode, model availability, usage caps, and strict sandbox operation without invoking a task.
2. **Harness qualification:** prove fixtures are fresh, secrets are absent, acceptance tests fail before and pass after reference patches, event parsing survives unknown event types, and interrupted runs resume safely.
3. **Baseline:** run unmodified Claude Code and Codex with controlled homes and vendor-default prompts. Then measure the installed Claude global prompt as a separate treatment.
4. **Factorial pilot:** on development tasks, compare prompt only, deterministic completion gate only, and prompt plus gate. Change one factor at a time before testing combinations.
5. **Automated search:** promote candidates development → validation using immutable manifests and a fixed per-round budget. Diagnose failures by task family before proposing the next intervention.
6. **Stop:** apply the predeclared parity or plateau rule, then run the holdout once and publish the full manifest, paired outcomes, confidence intervals, and limitations.
7. **Secondary Codex work:** only after fixing the Claude result, run the same champion/challenger protocol for Codex instructions. Keep Codex improvements out of the moving parity target; compare improved Codex in a separately labeled experiment.

## Limitations

- Product flags, event schemas, model availability, and authentication policies are time-sensitive; re-check the linked official pages and capture CLI `--version`/`--help` output at experiment start.
- Neither vendor's event stream is the ground truth for correctness; executable tests are.
- The proposed parity threshold, repetition count, run budget, and model pairing require an explicit owner decision before paid or quota-consuming runs.
- Results from a 20-task suite estimate performance only on that suite's task distribution. They do not establish universal Claude Code–Codex parity.
