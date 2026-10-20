# Shared work-record contract

Read this reference before creating, resuming, selecting, claiming, revising, or completing tracked planning and implementation work. Repository tracker configuration selects the authority and locations. Remote tracker state stays remote; this local helper is only for a configured local tracker.

## Identity and artifacts

Use a stable `work/<effort>/` directory across sessions. Resume an explicit effort reference; similar titles are insufficient identity. Allocate a distinct slug suffix for a new request. Create only needed artifacts: `README.md` owns request, desired outcome, lifecycle, stage, current spec/map pointers and next action; `discovery.md` holds ordinary findings; `map.md` and `decisions/` hold Wayfinder planning; `spec.md` holds the current specification; `tickets/` holds implementation issues; `history/` retains replaced content. Project glossary and ADRs retain their existing scope. Completed folders remain in place.

Use UTF-8 Markdown with YAML front matter: `schema: 1`, `kind`, and stable repository-relative `id`. Kinds are `effort`, `map`, `decision`, `spec`, and `implementation`. Child records name `effort`; directly supplied standalone specs/issues may omit membership. Metadata references resolve from the repository root; body links resolve from their document. Missing, contradictory, duplicate, and unknown fields required for selection need a diagnostic, never a guessed default.

| Kind | Additional metadata | Body |
| --- | --- | --- |
| Effort | `state`, `stage`, `current_spec: {ref, revision}` or null, `current_map` or null, `next_action` | Original request, desired outcome, artifact links |
| Spec | `revision`, `state`, `readiness` | Scope, acceptance criteria, readiness rationale |
| Implementation | `state`, `readiness`, `basis: {ref, revision}` or explicit null, `blocked_by: []`, positive `order` within its effort | Deliverable, observable criteria, approval or explicit task authority, reconciliation/completion evidence |
| Map | `state` | Destination, Notes, Decisions so far, Not yet specified, Out of scope |
| Decision | `map`, `type`, `state`, `blocked_by`, `order` | Question; authoritative answer on resolution |

## Lifecycle, readiness, and dependencies

Effort states: active, waiting, completed, canceled, superseded. Stages: discovery, decisions, specification, implementation. Spec states: current, completed, superseded, canceled. Implementation states: open, in-progress, waiting, completed, canceled, superseded. Map states: open, completed, canceled, superseded. Decision states: open, resolved, canceled, superseded. Waiting/canceled records explain why; waiting names the missing condition. Superseded records link their replacement. Terminal records require explicit reopening intent and a recorded reason.

Readiness uses the configured triage vocabulary: needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix. Only ready-for-agent passes automatic implementation gates. Stage, queue membership, and spec readiness never approve children or invoke implementation. Record the user's breakdown approval before publishing ready issues. Human decisions remain open until the human supplies judgment.

Implementation blockers reference implementation IDs, never decision tickets. Validate cycles, self references, unresolved IDs, and kinds. Only completed blockers satisfy dependencies; cancellation/supersession requires explicit reconciliation. During implement-spec, completed means accepted work is available on the integration branch. A required open human decision keeps the affected issue at needs-info. Keep Wayfinder's separate resolved-decision frontier semantics.

## Authority and implementation ownership

Use `scripts/work_records.py` beside this reference with Python and PyYAML. Pass `--repo <target-checkout>` even when the helper is installed elsewhere. `--help` and each subcommand's `--help` describe arguments. The public Python interface is `WorkRecords(checkout)`; its producer and consumer methods are also CLI operations.

1. `configure --authority <checkout-root>` declares the single live record checkout under the shared Git common directory. All participating worktrees use that declaration. A Git discovery/access failure blocks work. Existing authority cannot silently change. Independent clones/machines and unverified network filesystem locking are outside this local concurrency guarantee.
2. `create-effort` records the request/outcome; `--effort` resumes a known identity. `publish-spec --body-file ...` publishes initial revision 1 and updates the overview. It creates no child issues. Read existing context before synthesis; publication is not an interview.
3. After breakdown approval, `publish-issue --body-file ... --approval ...` creates one issue at a time, blockers first. Repeat `--blocked-by` for dependencies. The body must be self-contained: purpose, scope, observable criteria, delivery requirements, spec/design links and approval context. Source references are allowed even though implementation file paths should be avoided. The helper records current basis and deterministic order.
4. `read <ref>` reads authoritative metadata/body. `claim <issue-ref> --owner <session>` validates kind, lifecycle, readiness, current spec, effort, dependencies and existing ownership together under one process-safe lock. Preserve the returned opaque token and worktree pointer. Claim before work; implementation runs outside the lock. Every record writer must share this coordinator; hand editing live state during acquisition is unsupported.
5. `release <ref> --token ...` returns unfinished in-progress work to open. `complete <ref> --token ... --evidence ...` revalidates eligibility and records completion only after acceptance and integration have been verified. The helper cannot independently prove a prose evidence claim. Never mark unmerged worker work completed. A wrong token cannot mutate ownership. Abandoned claims stay blocking until explicit recovery; elapsed time never grants takeover.

The coordinator uses OS file locking and atomic replacement with flushed files. Claim persistence precedes in-progress publication; interruption can leave a blocking claim requiring recovery, never authorize a second consumer. Initial spec publication writes content before the overview pointer; an interrupted mismatch fails closed. Supported local operations are explicit issue acquisition, initial production, release, and completion. Selection/revision/recovery extensions must preserve the same authority and short-lock boundary.

## Revisions and selection contract

Material scope/criteria changes increment a positive spec revision. Retain exact prior content in `history/spec-rN.md`, then update current spec and effort pointer consistently under the coordinator lock. Mismatched unfinished issue bases are ineligible until impact review: unaffected issues need a no-impact rationale; affected issues need updated scope/readiness and changed-breakdown approval. Completed issues retain their original bases. Active workers revalidate before publishing results; revision changes retain their claims and work for reconciliation.

Explicit input confines selection to that issue, effort, or spec, overriding queue order but never gates. Historical inputs are rejected with a current pointer when known. Bare implementation traverses ordered unique effort references in `work/queue.md`, then positive unique issue order. Skip known blocked, claimed, terminal, waiting, stale, or unready work and consider independent issues. Missing/unreadable authority, malformed ordering, unsupported schema, and unknown dependency outcomes make a scope indeterminate, not empty. Bare implementation never executes decisions or undecomposed specs. Explicit undecomposed specs use whole-spec ownership; decomposed specs use the issue graph. Whole-spec and child-issue claims must conflict.

Preserve explicit legacy IDs and references. Normalize recognized fields only when unambiguous; report missing kind, readiness, basis, or dependency information. Migration is separately opt-in, with reviewed classification and reference mapping; never relocate historical work automatically. Remote adapters must verify exclusive acquisition or establish one shared controller; native assignment alone is not proof.
