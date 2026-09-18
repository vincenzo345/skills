# Claude Code instruction optimization: pre/post results

Date: 2026-09-16/17
Primary model: Claude Opus 5 through Claude Code 2.1.274
Reference model: `gpt-5.6-sol` through Codex CLI 0.154.0

## Outcome

The installed global Claude Code harness reached the pre-registered parity threshold on the frozen holdout:

| Condition | Executable passes | Total | Rate |
|---|---:|---:|---:|
| Claude, installed global prompt + completion guard | 12 | 12 | 100% |
| Codex 5.6 Sol reference | 12 | 12 | 100% |

The four holdout tasks were authored only after the Claude candidate was frozen. Each task was run in three fresh sessions per agent. The tasks covered resource cleanup, retry/error boundaries, atomic state updates, and one-shot iteration. Every untouched seed failed and every reference implementation passed in two author-validation repetitions before model scoring.

## Before

Claude's clean `--safe-mode` baseline passed 19 of the original 20 tasks. It failed `error-contract`: Claude introduced a `TypeError` path for `None`, although the existing implementation had treated `TypeError` and `ValueError` together as expected invalid input and the required public error was `ConfigError`.

The previously installed global rigor prompt also failed the same task in a fresh session. Its final answer explicitly classified non-string input as a programmer error and asked the user to choose, while the executable oracle failed.

## Iteration history

| Candidate | Change | `error-contract` result | Disposition |
|---|---|---:|---|
| Clean baseline | Claude `--safe-mode` | 0/1 | Baseline failure |
| Prior installed prompt | Existing rigor contract | 0/1 | Failed |
| v2 | Added input-partition and public-error guidance | 0/1 | Rejected |
| v3 | Clarified validation errors versus unexpected internal errors | 1/2 | Rejected as nondeterministic |
| v4 | Anchored fixes to the existing expected-invalid input set | 1/3 | Rejected as unreliable |
| v5/v6 | Added a one-shot Stop hook; first protocol versions were not credited because debug logs did not prove blocking | 4/4 | Supporting model evidence only |
| v7 | JSON-only Stop-hook protocol, explicit hook evidence | 3/3 | Promoted to regression/holdout |

The important mechanism change was not another longer prompt. The global Stop hook blocks the first attempted completion after edits, supplies a skeptical contract/diff review checklist, and honors `stop_hook_active` so it cannot loop. Claude's debug logs record the hook's `decision:block` and the additional review turn.

## Post-change validation

- Target failure: v7 passed `error-contract` 3/3; hook activation was recorded on every run.
- Regression set: 5/5 passed (`backward-compatible-api`, `atomic-settings-write`, `two-cause-regression`, `preserve-dirty-file`, `concurrent-memoization`).
- Frozen holdout: Claude 12/12 and Codex 12/12 across four tasks and three repetitions.
- Deployed global smoke: `inclusive-range-partition` passed in a fresh Claude session without an explicit `--settings` argument; the debug log proves automatic discovery of the installed Stop hook and one blocked completion.
- Harness-focused repository checks: 36/36 passed.
- Full repository suite: 167/167 passed.
- Full catalog: 24 synthetic coding tasks. The four new holdouts independently demonstrate red seed and green reference behavior.

## Installed state

- `C:\Users\vince\.claude\CLAUDE.md`
  - SHA-256: `4F3B9B078DDBF5E083CB58EDFFCD5D103C0FD4389D2DD80C045D64E2873DBFA8`
  - Preserves the original Graphify instructions.
  - Adds contract partitioning and expected-invalid-input preservation rules.
- `C:\Users\vince\.claude\settings.json`
  - SHA-256: `9605302A998A70A25ABACB7FEC0036967975E5698952FFC0AFE8069670FA9ED2`
  - Registers the global completion-review Stop hook.
- `C:\Users\vince\.claude\hooks\completion_guard.py`
  - SHA-256: `D2AC7024CBB2E47B29F03ED63E50FE721A2BB043CFFE6D9B710C699BBAD9C567`
  - Matches the repository-tested implementation.

Backups:

- `C:\Users\vince\.claude\CLAUDE.md.backup-rigor-v1-20260916`
- `C:\Users\vince\.claude\settings.json.backup-before-completion-guard-20260916`
- `C:\Users\vince\.claude\CLAUDE.md.backup-before-codex-rigor-20260916`

## Boundaries and caveats

- This establishes parity on the defined synthetic task distribution, model versions, and run policies; it is not a universal claim that Claude and Codex have identical capabilities.
- Claude was denied shell/network tools during scored tasks and relied on file read/edit/search tools; executable acceptance tests ran externally. Codex used `danger-full-access` inside disposable synthetic workspaces because its Windows `workspace-write` sandbox rejected even read-only shell commands. The prompt restricted Codex to the workspace, and evaluator-owned oracles determined results.
- Claude CLI's `total_cost_usd` field reported list-price-equivalent accounting even though the authenticated account used a subscription. This report makes no claim about cash charges.
- Two Codex trials blocked by the Windows sandbox were infrastructure-invalid and excluded from scoring.
- The Stop hook adds one review turn after edits. That latency/cost is the measured tradeoff for the reliability gain.

## Stopping decision

The satisfactory threshold is met: on a frozen holdout repeated three times, Claude is not more than one task behind Codex and has no observed scope or false-completion regression. Both agents scored 12/12. Further prompt changes would risk overfitting without a new, harder evaluation distribution, so this optimization loop stops with v7 installed.
