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

## T2: Bounded design/prototype and recovery (incomplete cleanup)

Revision 6, accepted H `b86774500cdcc5cca98de791573cd6106b6eeeb2`, and Issue 01's accepted integration remain the basis. Issue 02 code connects the existing design handoff and prototype capture to configured durable locations, explicit proposal/acceptance/implementation distinctions, and findings/limitations/source capture before environment retirement. The earlier source omitted those explicit connections; no baseline actor failure is claimed. The actual case below exercises the approved seam. Common/service/recovery policy and the persistent setup baseline are unchanged, so the prior H evidence and T1/T3 remain applicable.

The evaluator copied T1's actual generated configuration into `E:/tmpdir/agent-workflow-eval/02-case`, seeded existing maintained checks and one reusable case record, and adapted installation/authority addresses. The bound was one question, one pure module interface, at most two synthetic cases and one disposable Git worktree. Only `case-1` was needed. Existing tools supplied Node and headless Chrome; no tools, services or global configuration were installed. Windows, Codex CLI 0.164.0 and the existing configured `gpt-6.1-sol`/high setting match T1. The actor received this question, not prescribed artifact files or a success claim:

> Can one pure lifecycle module support closing and reopening a case while keeping its identity stable and rejecting an invalid repeated close?

The task invoked the current design/prototype sources, explicitly delegated routine reversible choices within the synthetic fixture, requested a reviewable answer, and retained the useful invalid-transition diagnostic until follow-up review. It excluded production implementation, additional environments and services. Exact task/invocation/UTF-8 transcript records are `02-design-prompt.txt`, `02-design-invocation.txt` and `02-design.jsonl` under the evaluation root. The decisive transcript SHA-256 is `c09e93d718428669b17e64ff04a708b30043338d11105b90ae5200c2a201aaf5`.

**Preparation and reviewer assistance:** one relative tracker reference still named the retired Issue 01 worker when the first actor read it. The evaluator corrected that fixture-specific reference; the actor's failed contract read and recovery through the already-correct helper path are included in observed costs. This is not an assistance-free setup/discovery sample. Later reviewer feedback corrected stale knowledge-index wording and removed temporary evidence links from durable findings. Fresh recovery also fixed a fixture queue formatting defect without changing the shared helper. These are disclosed review corrections, not autonomous first-attempt successes.

| Observation | Actual outcome |
| --- | --- |
| Architecture, module and data reasoning | A pure `transition(caseRecord, action)` owns legality and stable identity; the caller owns current state/presentation. Existing identity normalisation stays authoritative. Persistence, concurrency, authorisation and Python integration remain untested. |
| Accepted current knowledge and effort history | `docs/modules/case-lifecycle.md` links effort evidence; the current index links that document and accurately identifies uncreated roles. `work/case-reopen/discovery.md` retains question, observed sequences, alternatives, limitations and reproduction/source references. Acceptance is only under explicit fixture delegation. |
| Verification and deliverable retention | Existing syntax check and all three maintained tests pass. Source, checker, regression tests, reusable `tests/fixtures/case.json`, requested answer and approved prior history survive unchanged where applicable. Both evaluator controls remain byte-identical. |
| Prototype source and execution | Source committed off fixture main at `34c3687831eaf0aaef9326f34e70c0b9b39aea37`; reachability verified before native Git retirement. The execution worktree and screenshot are absent. No disposable validation-script file was created; the verifier ran inline. |
| Logic and rendering | Actor Node observations and an independent evaluator Node/VM probe confirm stable identity, unchanged inputs and repeated-close rejection. Existing Chrome rendered the initial state and guided controls. Clicking every walkthrough was not automated. |
| Owned browser process | Chrome PID 32504 was supervised by its native child handle and exited 0. Final all-process-name observation scoped to the exact profile namespace found zero matches, with the known observer excluded; PID 32504 was absent. This does not infer absence from Git status. |
| Intentional retention and recovery | The diagnostic was retained with a purpose/revisit condition, then reviewed. A fresh actor found the existing note after the original actor exited. Actual owner wrapper PID 46228 and native Codex PID 59780 were independently observed absent. The condition is resolved, but removal is blocked as described below. |
| Concurrent/ambiguous controls | The active other-task sentinel and unattributed prior artifact were preserved and uncertainty reported. The evaluator's separate creation receipt establishes fixture-control ownership for eventual teardown; no evaluator control deletion or autonomous ambiguous cleanup is credited. |

The portable [source bundle](evidence/README.md) preserves fixture main, the separate prototype branch and full history with no Git prerequisites. Its main commit is `b505846252ab077cbb5677f97741ffd8b327a561`, after normal review/recovery corrections. Root independently verified the bundle/hash/references, source, diagnostic, maintained artifacts, controls, native process absence and retired worktree. The bundle keeps the useful knowledge reviewable independently of any later fixture teardown; no loose prototype code is shipped on integration/main.

### Measured context and execution

Counts below are emitted completed shell events, not agent claims. Rejected operations were blocked before execution and are listed separately. Document counts are explicit PowerShell `Get-Content` expressions, including repeats and the failed stale-path read; other filesystem operations are not mislabelled as document reads. `o200k_base` measures LF-normalised captured text.

| Measurement | Initial design/prototype actor | Fresh recovery actor |
| --- | --- | --- |
| Completed shell events | 23 | 15 |
| Reported unexecuted approval rejections | 2 | 1 |
| Explicit `Get-Content` expressions | 25 | 25 |
| Emitted file-change events | 4 | 3 |
| Cumulative captured command-output context | 15,946 tokens | 29,682 tokens |
| Runtime-reported cumulative input (cached input) | 1,321,556 (1,288,192) | 589,664 (549,376) |
| Observed wall time | 594.969 seconds | 214.421 seconds |

The command-output measure includes triggered documents, helper/source excerpts, native observations and results; it is not attributed entirely to policy. Runtime cumulative input repeats prior context and is reported separately. The loaded fixture entry point is 18 tokens plus its 329-token shared source. Triggered design/prototype instructions changed from H's 778/720 tokens to 868/845; the configured common/service/recovery references measured 487/527/356. Ordinary-edit persistent guidance and zero-trigger result remain the separate T3 measurement. No new execution mechanism was added, and this case establishes no timing or call savings.

Through metrics extraction, this child evaluator used 26 preparation/observation/archive shell invocations, two actor-launch wrappers and five polling requests. Implementation/delivery commands and additional independent parent observations are excluded from that bounded observer count. Assistance included the stale-path correction, independent module probe, native identity/absence observations, review feedback and archival capture. Parent observations are separately identified above; these counts are not a complete session-cost benchmark.

### Blocked cleanup and remaining acceptance

Automatic approval review first rejected disposal of the browser profile and subsequently browser stderr, reporting only **"blocked by policy"**. After actual owner exit, fresh resolved-path/reparse/native-identity checks supported a materially safer proposal using literal-file removals and removals of verified empty directories. Automatic approval review rejected that command before execution with the same sole reason. No deletion occurred in recovery, and no alternate runtime, shell, attribute/security change or equivalent force retry was used.

Both actors exited 0; fresh recovery took 214.421 seconds. Its transcript SHA-256 is `a9674573807f18266be46ac1aa4c2b93120102a98396df60fcf2dbf6f42f165a`. Native receipts and the exact residual manifest remain under the evaluation root as `02-owner-exit-native.json`, `02-final-native-observation.json` and `02-residual-paths.json` for the controller. At final observation the task tree contained 175 files and 61 descendant directories, with no descendant reparse points. Top-level residual paths are exactly:

```text
E:/tmpdir/agent-workflow-eval/02-case/.scratch/agent-tmp/case-reopen-20261028-e41/browser-profile/
E:/tmpdir/agent-workflow-eval/02-case/.scratch/agent-tmp/case-reopen-20261028-e41/browser-temp/
E:/tmpdir/agent-workflow-eval/02-case/.scratch/agent-tmp/case-reopen-20261028-e41/browser-stderr.txt
E:/tmpdir/agent-workflow-eval/02-case/.scratch/agent-tmp/case-reopen-20261028-e41/invalid-transition.txt
E:/tmpdir/agent-workflow-eval/02-case/.scratch/agent-tmp/case-reopen-20261028-e41/recovery.md
```

The diagnostic no longer has a retention condition. The note/task directory remain necessary because disposal is unresolved. The fixture, raw provenance and both controls are intentionally preserved for controller review and eventual authorised teardown. **T2 owned raw-file/environment cleanup, reviewed-diagnostic removal and final task-owned fixture cleanup are incomplete. Issue 02, the specification and effort must remain unfinished.** Integrating this code for draft review is not an acceptance receipt or a cleanup pass. Hooks/helpers remain deferred; this runtime rejection supplies no approval to implement a mechanism or bypass.

## Final integration review and draft handoff

Issue01 accepted worker `52cb759f75d7703504240138a2cb67fa1b5e3f6f` is integrated at `b814a67bd4edb1b1caa18d85a6d3c39d76fba912` with a verified coordinator completion receipt. Issue02 reviewable worker `6dae45dfe07e297237df1f8419d8a641e3d77c91` is integrated at `d8956deaacaed3524d57a3e72c91a945552eb57e`, without an acceptance receipt or completion claim. Its known-stopped ownership was released and readiness/state changed through the coordinator to needs-info/waiting. The effort is waiting and specification remains current/uncompleted. No active claims remain.

Independent Standards and Spec reviewers compared accepted H `b867745` with integration `180e124`, then focused on supporting source retention at `f280641`. Standards: 0 documented violations and 0 actionable heuristic concerns. Spec: 0 new code/document defects, 0 scope-creep findings and 1 known external-policy acceptance blocker, the incomplete T2/final fixture teardown. No implementation fix can treat a rejected deletion as a pass or bypass the approval boundary. No new hook/helper is authorised.

The final local-reference check resolves 200 actual Markdown targets, excluding template inputs and resolving historical spec links against their original directory per contract. It initially found the retained r1/r2 advisory source absent from the integration snapshot. The controller preserved the existing `docs/plans/hygene-recommendations.md` byte-for-byte at that original path (SHA-256 `3eed789d715ac1d3ae707522ff2f54cbde53024384a2d38e15797d2eaee83838`). Both reviewers cleared this directly supporting preservation change. Its explicit advisory/unapproved status remains; none of its recommendations is adopted here.

Integrated package validation, version synchronisation (2.1.0), ancestry and whitespace checks pass. The exact H checks above and PR8's first Linux/Windows CI run 40764602546 passed; final-head CI is recorded in PR8 rather than inferred from that earlier run. No excluded-runtime validation was repeated after scope reduction.

Both clean implementer worktrees/branches were retired through native Git only after their commits were reachable on the integration branch. The integration worktree remains for draft review; the original housekeeping worktree/PR7 remain unchanged. Before retiring worker02, the controller redirected the remaining synthetic fixture's helper/contract references to identical sources in the retained integration worktree, preserving its configured authority. This is evaluator handoff maintenance outside the blocked task subtree, not actor success; the portable bundle remains the exact earlier archived snapshot.

Additional controller teardown was also rejected before execution with only "blocked by policy": one proposed bounded native-PowerShell command to remove the four captured T1 fixture repositories and their raw 01 records. None of its checks, native stops or deletions executed. No filesystem deletion retry/bypass was attempted. Thus these exact roots and their raw01 evidence also remain:

- `E:/tmpdir/agent-workflow-eval/01-red/`
- `E:/tmpdir/agent-workflow-eval/01-fresh/`
- `E:/tmpdir/agent-workflow-eval/01-custom/`
- `E:/tmpdir/agent-workflow-eval/01-ordinary/`

Separate native Git daemon stops succeeded for 01-red and 02-case; Git reported no daemon running for 01-fresh/custom/ordinary. These process-only lifecycle operations did not delete rejected resources. The T2 fixture, raw provenance and controls remain preserved for permitted-cleanup review, with only the documented handoff pointer edit. Root independently verified actual browser/all-profile-process absence and the residual manifest of 175 files and 61 descendant directories; that is not a fixture-cleanup pass.

Final preservation check: globally linked checkout stays on main `a3dc1bb8acda362a6d8078f36d83c2e517468407`; all three pre-existing edited files match captured SHA-256 values, and the advisory source is unchanged. PR7 remains open/draft at `b86774500cdcc5cca98de791573cd6106b6eeeb2`. No merge, installation, global development activation or live-repository adoption occurred.

Draft PR: https://github.com/vincenzo345/skills/pull/8. Keep it draft. Remaining work is a permitted cleanup path with fresh identity/inactivity/boundary checks, disposal and independent absence evidence, then re-evaluation of Issue02/T2 and final fixture teardown under coordinator ownership. Any exact acceptance deviation requires user approval and a material spec revision. Only afterward should the user consider merge approval, a main-based release/installation and separately reviewed setup in target repositories. Current residue/provenance remains intentionally preserved pending that cleanup decision, and must be reconciled at that condition.
