# Claude–Codex Workbench parity scorecard

Last updated: 2026-09-18 (v18 target met; C1 interrupted by provider quota)

This is the running scorecard for the live Applications4Life Workbench investigation. Update it after every evaluated candidate, before beginning the next harness iteration.

## Rubric and acceptance bar

Scores are 1–5. Weighted total uses: factual/causal correctness 28%, evidence/calibration 22%, coverage/actionability 18%, Workbench fidelity 14%, clarity 8%, and efficiency 10%.

A passing Claude configuration must have a weighted total of at least 4.0, every dimension at least 4.0, median peak request context no more than 150,000 tokens, median duration no more than 1,500 seconds, and all four hard gates passing. The comparison goal is to meet or exceed Codex's quality while retaining Claude's efficiency advantage.

## Current scorecard

| System / iteration | Total | Factual | Evidence | Coverage | Workbench | Clarity | Efficiency | Peak tokens | Seconds | Hard gates | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Codex reference v11 | **4.522** | **4.7** | **5.0** | **4.9** | **4.9** | **4.6** | 1.7 | 151,443 | 675.4 | Pass | Quality baseline; fails efficiency minimum and token ceiling |
| Claude v15 C0 | 3.870 | 3.4 | 3.6 | 4.4 | 4.6 | 4.5 | 3.3 | 131,729 | 861.9 | Fail: environment order, Workbench schema | Rejected |
| Claude v15 C1 | 4.342 | 4.1 | 4.8 | 4.7 | 4.8 | 4.5 | 2.6 | 114,934 | 738.9 | Fail: environment order | Rejected |
| Claude v15 C2 | 4.230 | 4.2 | 4.5 | 4.5 | 4.8 | 4.4 | 2.3 | 128,876 | 887.8 | Fail: environment order | Rejected |
| Claude v16 C0 | 3.964 | 3.7 | 4.3 | 4.4 | 3.5 | 4.5 | 3.4 | 114,147 | 641.5 | **Pass** | Rejected |
| Claude v16 C1 | **4.376** | **4.4** | **4.7** | **4.8** | **4.1** | **4.4** | 3.2 | **95,069** | **510.1** | **Pass** | Current best Claude; below Codex total by 0.146 and misses efficiency minimum |
| Claude v16 C2 | 4.358 | 4.1 | 4.7 | 4.6 | **4.9** | **4.4** | 3.1 | 104,977 | 620.5 | **Pass** | Rejected; improved fidelity but regressed correctness and efficiency |
| Claude v17 C0 | 4.582 | 4.5 | 4.8 | 4.8 | **4.9** | **4.7** | 3.4 | 107,642 | **603.1** | **Pass** | First Claude run above Codex total; efficiency still below 4.0 floor |
| Claude v17 C1 | **4.690** | **4.6** | **4.9** | **4.9** | **4.9** | **4.7** | **3.8** | 115,487 | 666.1 | **Pass** | Current best; beats Codex overall and nearly clears efficiency floor |
| Claude v17 C2 | 4.142 | 3.8 | 4.5 | 4.6 | 4.6 | 4.2 | 2.8 | 100,011 | 497.4 | Fail: environment order | Rejected; over-constrained artifact strategy caused retries and causal overstatement |
| Claude v17 C3 | 4.288 | 4.2 | 4.6 | 4.7 | 4.4 | 4.6 | 2.7 | 98,354 | 505.5 | Fail: environment order | Rejected; ledger added ceremony and introduced path/provenance defects |
| Claude v18 C0 | **4.706** | **4.7** | **4.9** | 4.7 | 4.8 | **4.8** | **4.1** | 101,701 | **571.1** | **Pass** | Winner; all dimensions, gates, and resource ceilings pass |
| Claude v18 C1 | — | — | — | — | — | — | — | 98,543¹ | 478.0¹ | Not scored | Replicate 2 hit provider session limit; no result used |

Bold values identify the current quality or efficiency leader among comparable completed runs.

## Hard gates

1. Environment coordinates appear before ranking or recommendations.
2. No Workbench schema failure.
3. No legacy hook failure.
4. No unregistered correction.

## Current assessment

Claude v18 C0 meets the full target. Its 4.706 weighted total exceeds Codex's 4.522; every dimension clears 4.0, all four hard gates pass on both immutable transcripts, and resource ceilings pass. The controller originally marked the environment-order gate false when no ranking/recommendation term appeared at all; the corrected order semantics now require the environment term and fail only when a present later term occurs first. Controller regression tests cover both the absent-later-pattern and missing-environment cases. C1 was not scored because its second replicate hit Claude's session limit; it is excluded from comparison.

¹ C1 values are its completed first replicate only, not a two-run median.

## Iteration log

| Iteration | Harness change | Observed effect | Next decision |
|---|---|---|---|
| v15 | Added global rigor instructions, Workbench lifecycle enforcement, and diagnosis checks | Strong coverage and fidelity, but literal environment-order failures and lifecycle ceremony reduced reliability and efficiency | Simplify lifecycle and make environment-first ordering mechanical |
| v16 C0 | Added one-call Workbench routing/handoff helpers and stricter environment-first prompt | All hard gates passed; durable artifact retained an unsupported deployment/default assumption | Strengthen provenance and pre-accept review |
| v16 C1 | Tightened causal calibration and helper-driven lifecycle | Best Claude result; faster and lower-token than Codex; post-accept Stop review duplicated the final and exposed an immutable-artifact mismatch | Eliminate post-accept correction and require final review before acceptance |
| v16 C2 | Added exact provenance, guard-derived request counts, conditional cache ordering, and one concise pre-accept synthesis | Fidelity reached 4.9 and all gates passed, but an overstated telemetry claim lowered factual correctness to 4.1; the Stop hook again produced a duplicate final | Move review into terminal acceptance and suppress the redundant Stop turn only after review is attested |
| v17 C0 | Required terminal review attestation, emitted a trusted review marker, skipped only the redundant diagnosis Stop turn, and compacted Workbench instructions | Beat Codex overall (4.582 vs. 4.522), retained 4.9 fidelity, and passed every gate; efficiency rose only to 3.4 due to 52 turns and avoidable retries | Preserve quality while reducing scans, retries, and lifecycle payload size |
| v17 C1 | Added inspect-once/reuse guidance, prohibited broad rescans and duplicate temporary evidence, and tightened two unsupported projections | Improved total to 4.690 and efficiency to 3.8 with 43 turns; promoted without quality regression | Remove remaining duplicate lifecycle prose and constrain the scan target list |
| v17 C2 | Required one target list, one proposal artifact, no duplicated option/evidence text, and a sub-300-word final | Faster, but schema retry and under-specified cache discrimination dropped correctness to 3.8, efficiency to 2.8, and failed environment order | Reject; return to C1 and reduce work through a reusable evidence ledger instead of removing required lifecycle content |
| v17 C3 | Added a compact evidence ledger, required each read to name the decision it could change, and kept C1's lifecycle structure | Faster, but two preflight denials, duplicated serialization, an incorrect artifact link, and causal overstatement lowered total to 4.288 and efficiency to 2.7 | Reject; retain C1 and reduce helper output/bookkeeping mechanically rather than add planning prose |
| v18 C0 | Allowed complete supplied coordinates without a forced preflight denial, ignored benchmark words inside heredoc data, compacted lifecycle output, and deployed Claude Rigor 1.5.0 | Cleared every dimension and scored 4.706; corrected gate evaluation passes all four gates on both runs | Promote and merge the remaining proof-prefix/browser-cache wording into the canonical harness |
| v18 C1 | Required the five coordinate lines before any text, named the `PRF-` proof prefix, and corrected browser-cache observability | First replicate was faster; second replicate hit the provider session limit at 71,497 tokens | Exclude from scoring; retain C0 evidence and merge only its uncontroversial calibration fixes |

## Evidence locations

- Frozen rubric: `tests/comparison/claude-codex-investigation/rubric.json`
- Codex final: `.harness-runs/live-parity/codex-reference-v11-final.md`
- Claude campaign evaluations: `.harness-runs/live-parity/campaign-v*/candidates/*/evaluation.json`
- Current campaign events: `.harness-runs/live-parity/campaign-v16/events.jsonl`
- Historical sample-codebase validation: `.workbench/work/WB-20260916-CLAUDE-INSTRUCTION-OPTIMIZATION/artifacts/pre-post-results.md`
