# Workflow reliability evaluation

## Basis and bounded method

Current acceptance basis: specification revision 6. Revision 5 was retained exactly before the user's approved Codex-only scope reduction. Issue 01's active claim acknowledged revision 6 after integration of record commit `7a44c6204a3e98e82e1d424d8721e79eb3bcd355`. Its implementation is `c828e53`, scope correction `06ceb02`, and repeat-setup safety correction `acb74b32d0184d88079475029280f2419bc11506`. Completion requires the controller's integration receipt, not this worker report.

Accepted housekeeping basis H: `b86774500cdcc5cca98de791573cd6106b6eeeb2`, from preserved draft PR #7. Independent Standards and Spec reviews found zero actionable findings. Ancestry on `feat/agent-workflow-reliability` returned 0 before readiness/claims and again in the worker. Applicable prior evidence is [housekeeping validation](../agent-housekeeping/validation.md), including exact-head passing CI run 40013022186. Parent reran 60 repository tests, 27 preservation tests, package/version/strict-plugin/whitespace checks successfully on H. Service/recovery behavior is unchanged; no Docker demonstration was added. Prior seeded-interruption, unavailable exact model revision/runtime-outage and two empty fixture-shell limitations remain qualifications of that earlier evidence.

Windows PowerShell, Python 3.12.8, Codex CLI 0.164.0. Actual Codex actor invocations used the existing configured `gpt-6.1-sol` model and high reasoning setting without a model override. That is an available configured identity, not an immutable model revision. The observer and actors had separate contexts. Fixtures, actor prompts, invocation records, UTF-8 JSONL, stderr and exit/elapsed records were kept under `E:/tmpdir/agent-workflow-eval/` for controller inspection. They are evaluation artifacts, not a new shipped helper or evaluation platform.

The common invocation for the decisive discovery and matched-edit runs was:

```text
node <existing @openai/codex/bin/codex.js> exec --ephemeral --json -s danger-full-access -c approval_policy="never" -C <fixture> -
```

The task was supplied on stdin. No global configuration, install, development activation or other live repository setup occurred. The same `runtime_metrics` under-development warning appeared in each matched actor transcript; it did not prevent execution and was not suppressed by changing configuration.

## T1: Fresh and existing/repeated setup

Before configuration, a fresh Codex actor observed no repository instructions or knowledge index in an empty fixture. The candidate setup then ran in two isolated repositories, using the actual `/setup-repo` instruction source, not evaluator-written expected output:

| Fixture | Supplied setup task and approved choices | Observed result |
| --- | --- | --- |
| `01-fresh` | Configure only this disposable fixture; local Markdown tracking, default labels, single-context domain docs, reuse existing instructions/locations, one knowledge index and dedicated temporary subtree. Show the concrete draft, then apply under the task's advance approval; preserve content and unrelated ignores. | Preserved the existing spelling instruction in `CLAUDE.md`; added one Codex `AGENTS.md` pointer. Published the index and configured references, established `.scratch/agent-tmp/`, and left design records uncreated until useful content exists. |
| `01-custom` | Finish this existing fixture using authoritative choices/paths. Approve the smallest additive draft and exact permanent-document Git-visibility exceptions; preserve user edits, scopes, tracker authority and unrelated protected/generated content. | Kept `manual/INDEX.md`, `manual/policy/cleanup.md`, `.local/run/`, `manual/language.md`, existing decisions and `planning/efforts/`. A GitHub code remote did not replace local tracking. Filled missing guidance/labels and added an exact policy-file allowlist under the existing broad `manual/*` ignore. |
| `01-custom`, separate repeat | Run the current setup skill again; preserve configured authorities, custom locations, content/user edits and ignores, apply only missing content, Codex-only runtime scope. | Added only one missing inline sentence verifying ownership/resolved boundaries and protecting shared resources. No regenerated configuration, duplicate sections or second policy source. |

The first two runs started against the earlier approved runtime scope. Their resulting Codex connections and preserved existing shared source remain applicable to revision 6; they introduced no new second-runtime bridge. An authentication failure was observed before the scope reduction. It supplies no support claim and was not retried after the user excluded that runtime.

**Observed defect and correction:** initial custom setup kept ownership in the conditional reference but omitted explicit inline resolved-boundary/shared-resource protection. Parent review identified this. `acb74b3` makes reruns compare baseline obligations, reuse equivalent user text, and fill only missing inline obligations. The actual separate repeat inserted the missing sentence while preserving the existing block and user edit. Its nested read-only Codex probe was execution-policy blocked; that is an incomplete probe, not a discovery pass. The independent default-configuration runs below supply the successful observations.

Both decisive fresh Codex sessions received exactly:

> Explain the purpose of this repository and where a maintainer would find its current design information. Make no changes.

The prompt neither supplied policy nor requested a named instruction-file read. In `01-fresh`, Codex's first shell read the shared `CLAUDE.md` source reached from loaded `AGENTS.md`; it then read the current-knowledge index and relevant references. Its answer distinguished chosen future homes from nonexistent design records. In `01-custom`, Codex likewise reached the existing shared source, followed the existing index and relevant design/domain/schema documents, and distinguished accepted current knowledge from effort proposals. The observer inspected actual commands and output, not only actor claims. Discovery used three shell calls fresh and two custom, with zero file changes.

Independent worker and parent inspection established:

- All 19 original custom-fixture files remain: 14 byte-identical, five changed by additive/merge edits. Every original tracked line remains in its original order, including user text inside the generated block, handbook ordering, custom authority and the original ignore rules. The two existing service/recovery reference files also remain unchanged.
- All 17 fresh and 22 custom published Markdown references resolve. Intended permanent Markdown is visible to Git. Chosen future homes are explicitly described as locations, not broken published links.
- Instruction/configuration headings are unique, one policy source remains, and custom setup creates no competing default `docs/` tree.
- Disposable children are ignored. Private/generated sentinels, another active task's sentinel and hypothetical unrelated policy secrets remain protected/ignored. Existing content is unchanged. The only ignore additions reopen `manual/policy/` traversal, ignore its other children, and allow six exact permanent policy files.
- Temporary setup probes were removed; fresh setup leaves no task child beneath its usable temporary root. The custom other-task child remains preserved.

Raw transcript names: `01-fresh-setup.jsonl`, `01-custom-setup.jsonl`, `01-custom-repeat.jsonl`, `01-fresh-codex-discovery.jsonl`, `01-custom-codex-discovery.jsonl`. Decisive discovery SHA-256 values are `3f4a0a6aa234b7f9cf64b48624b869d2b95ce5d96a5c01fd4d5adf47b752b87c` and `89b3d90d7022fdfc480bf61a7668468f4ad85f56267b4f77e1caa86f0a1ecebe`. Exact setup prompts/invocations are retained beside those logs for controller review. Top-level setup shell calls were 19 fresh, 15 custom, 13 repeat; these include nested-runtime invocation wrappers, not an exhaustive count of every child process, and are not an ordinary-edit overhead comparison.

## T3: Matched ordinary edit

Both actors received exactly:

> Correct `reccords` to `records` in README.md. Make no other content changes.

The pair used the same fixture path (`01-ordinary`), exact restored initial README bytes, existing runtime/model/configuration, permission arguments and JSONL observation method. The sole intended input difference was original-H housekeeping guidance versus the candidate survival baseline and conditional knowledge pointer. Both versions used the same loaded `AGENTS.md` location; unrelated fixture files were unchanged. The policy/pointer text did not change during revision-6 scope correction, so this observation remains applicable.

| Observation | Baseline | Candidate |
| --- | --- | --- |
| Result | Exact requested typo correction | Same exact correction |
| Shell/tool calls | 2 | 2 |
| Explicit project-document reads | README only | README only |
| Housekeeping calls or specialized-reference reads | 0 | 0 |
| New recovery notes, bookkeeping artifacts or mandatory reports | 0 | 0 |
| Persistent `AGENTS.md`, tiktoken `o200k_base` | 180 tokens | 213 tokens |
| Cumulative triggered specialized context | 0 tokens | 0 tokens |
| Observed wall time | 27.468 seconds | 20.969 seconds |

The baseline used one Python edit and four Git subprocesses; the candidate used PowerShell/.NET file operations and three Git subprocesses. These execution choices are reported separately from housekeeping activity. API-reported total input tokens were 54,441 baseline and 54,552 candidate, which include unrelated runtime context and repeated tool results. A single model run cannot attribute timing or total-context variation to the guidance, and establishes no savings claim. No new execution mechanism was introduced.

An evaluator assertion initially expected LF rather than the fixture's CRLF bytes, preventing restoration and accidentally launching a candidate on already-corrected text. That no-op attempt (`01-ordinary-candidate.jsonl`) is excluded. The valid candidate (`01-ordinary-candidate-valid.jsonl`) restored the original CRLF bytes and uses the exact same task as baseline. Both actual edit results were independently checked. Baseline/candidate-valid transcript SHA-256: `d93bbc34e5ff3ab6c82c2be9b0b5c57cc64c721c370b1b70344b1d93be8d0671` / `20a193df3418c8af523c9cdb03fda01bd7685433df612f6ff6f31c88236f3e85`.

Actual generated fresh instruction text measures 18 tokens for the loaded pointer plus 329 for its shared source; custom measures 29 plus 362 after the missing-obligation correction. These include prior instructions and tracker/domain configuration as well as housekeeping. The proposed 150-250 target is not a hard acceptance limit. Fresh discovery read 1,367 cumulative document tokens: shared source 329, index 260, domain 106, tracker 600, README 10 and queue 62. Those are observed design-context choices, with 1,038 tokens beyond the shared source. Ordinary edits triggered no specialized context. Context is measured from UTF-8 text normalized to LF with named `o200k_base`, separately from execution counts.

## Checks and disposition

Promoted-package validation and `git diff --check` passed on the updated source. Human setup documentation, both catalogs, router and UI description ship with the behavior. No executable helper, hook, new skill or service/recovery policy was added. The accepted H checks above remain applicable to unchanged executable/package infrastructure; parent owns final integration checks and two-axis review.

All setup/discovery/edit actors exited. Evaluation repositories and raw evidence are intentionally retained for parent verification and reuse of generated guidance in T2, with a revisit condition of controller acceptance/capture. They are not claimed cleaned merely because actors exited or Git status is clean. The parent must retire these task-owned fixtures/raw output after the necessary evidence is captured, preserve its unrelated evaluation/control files, and record any cleanup limitation. T2 and final integration/review evidence remain to be supplied by Issue 02 and the integration controller.
