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

Local decisions may carry `review_required: [<invalidated-decision-ID>]` after an upstream answer is superseded. This is a dependent-review gate, not lifecycle or implementation readiness. Planning claims and blocker satisfaction require that gate to be cleared through recorded impact review. Use [local planning operations](../wayfinder/LOCAL-PLANNING.md) to retain answers, supersede decisions, and review affected dependents.

## Authority and implementation ownership

Use `scripts/work_records.py` beside this reference with Python and PyYAML. Pass `--repo <target-checkout>` even when the helper is installed elsewhere. `--help` and each subcommand's `--help` describe arguments. The public Python interface is `WorkRecords(checkout)`; its producer and consumer methods are also CLI operations.

1. `configure --authority <checkout-root>` declares the single live record checkout under the shared Git common directory. All participating worktrees use that declaration. A Git discovery/access failure blocks work. Existing authority cannot silently change. Independent clones/machines and unverified network filesystem locking are outside this local concurrency guarantee.
2. `create-effort` records the request/outcome; `--effort` resumes a known identity. `publish-spec --body-file ...` publishes initial revision 1 and updates the overview. It creates no child issues. Read existing context before synthesis; publication is not an interview.
3. After breakdown approval, `publish-issue --body-file ... --approval ...` creates one issue at a time, blockers first. Repeat `--blocked-by` for dependencies. The body must be self-contained: purpose, scope, observable criteria, delivery requirements, spec/design links and approval context. Source references are allowed even though implementation file paths should be avoided. The helper records current basis and deterministic order.
4. `read <ref>` reads authoritative metadata/body. `claim <issue-ref> --owner <session>` validates kind, lifecycle, readiness, current spec, effort, dependencies and existing ownership together under one process-safe lock. Preserve the returned opaque token and worktree pointer. Claim before work; implementation runs outside the lock. Every record writer must share this coordinator; hand editing live state during acquisition is unsupported.
5. `release <ref> --token ...` returns unfinished in-progress work to open. `complete <ref> --token ... --evidence ...` revalidates eligibility and records completion only after acceptance and integration have been verified. The helper cannot independently prove a prose evidence claim. Never mark unmerged worker work completed. A wrong token cannot mutate ownership. Abandoned claims stay blocking until explicit recovery; elapsed time never grants takeover.

The coordinator uses OS file locking and atomic replacement with flushed files. Claim persistence precedes in-progress publication; interruption can leave a blocking claim requiring recovery, never authorize a second consumer. Spec publication journals its intended content before changing the spec or overview pointer; interruption fails closed until recovery. All extensions preserve the same authority and short-lock boundary.

## Revisions and selection contract

Material scope/criteria changes increment a positive spec revision. Retain exact prior content in `history/spec-rN.md`, then update current spec and effort pointer consistently under the coordinator lock. Mismatched unfinished issue bases are ineligible until impact review: unaffected issues need a no-impact rationale; affected issues need updated scope/readiness and changed-breakdown approval. Completed issues retain their original bases. Active workers revalidate before publishing results; revision changes retain their claims and work for reconciliation.

Explicit input confines selection to that issue, effort, or spec, overriding queue order but never gates. Historical inputs are rejected with a current pointer when known. Bare implementation traverses ordered unique effort references in `work/queue.md`, then positive unique issue order. Skip known blocked, claimed, terminal, waiting, stale, or unready work and consider independent issues. Missing/unreadable authority, malformed ordering, unsupported schema, and unknown dependency outcomes make a scope indeterminate, not empty. Bare implementation never executes decisions or undecomposed specs. Explicit undecomposed specs use whole-spec ownership; decomposed specs use the issue graph. Whole-spec and child-issue claims must conflict.

Preserve explicit legacy IDs and references. Normalize recognized fields only when unambiguous; report missing kind, readiness, basis, or dependency information. Migration is separately opt-in, with reviewed classification and reference mapping; never relocate historical work automatically. Remote adapters must verify exclusive acquisition or establish one shared controller; native assignment alone is not proof.


## Revision publication operations

Use `revise-spec --effort ... --body-file ... --expected-revision N --rationale ...` for an existing current spec. Material changes retain exact revision N content before publishing N+1; `--editorial` retains N and records the correction rationale. Treat uncertain impact as material. Readiness is explicit; changing a spec does not grant child readiness or rewrite completed evidence.

Publication holds the same coordinator lock as acquisition. Its durable journal blocks selection and issue publication until both current spec and overview agree. After interruption, `resume-publication --effort ...` reapplies only unchanged or already-applied writes. Conflicting retained history or externally changed files require explicit reconciliation; retry never overwrites prior history. `read-revision <spec-ref> <N>` resolves the stable identity and requested revision to retained content rather than today's requirements. Retained content is exact, so resolve historical relative links against the original spec directory.

Use `reconcile-issue <issue-ref> --rationale ...` for an unaffected unfinished issue after impact review. For affected work, supply `--affected --body-file ... --readiness ...` with its updated self-contained scope and criteria; ready-for-agent also requires `--approval ...` recording approval of the changed slice. Keep affected work at needs-info while approval is pending. Reconciliation records the old and new basis with rationale. Completed, canceled, and superseded issues remain historical evidence; create new follow-up work instead.

Run `revalidate <target> --token ...` immediately before publishing results; completion performs the same eligibility and acquired-basis check. A revision change retains ownership and the workspace. Pause dependent work and reconcile explicitly. Advancing an issue's basis does not silently advance an active claim's acquired basis; a stale worker must acknowledge the new scope through the claim-resume protocol or release its claim and acquire again after reconciliation. Revalidation is an observation under the lock, not a lock held during external publishing; revalidate again at completion.

## Selection and completion commands

Use `select [target]` only to preview. `select-and-claim [target] --owner SESSION --workspace PATH` resolves and acquires atomically through the declared authority. `claim TARGET --owner SESSION` uses the same explicit-scope operation. The returned target identifies the selected issue when an effort or decomposed spec was supplied. No target traverses ordered relative effort-overview links in `work/queue.md`; bare selection never executes an undecomposed spec.

Known ineligibility is reported separately from indeterminate authority. Missing readiness, bad ordering, unknown blocker outcomes, and inaccessible records stop the affected scope; do not silently choose lower-priority work. A direct-spec claim conflicts with every child claim based on it. Claims retain the acquired basis for later reconciliation checks.

`complete TARGET --token TOKEN --evidence TEXT` completes the claimed issue or direct spec after acceptance and integration verification. A completed spec cannot run again. `complete-effort EFFORT --evidence TEXT` requires terminal issues, completed current spec/map when present, and no outstanding claims. It records the outcome and removes the queue link while preserving every artifact path. Finishing a spec alone never declares the overall effort complete.

## Explicit legacy inputs and reviewed adoption

Use the packaged `scripts/work_legacy.py --repo ROOT normalize REF` to inspect a legacy record without rewriting it. The implementation consumer uses the same normalization for explicit references. Supported Markdown fields are bold `Kind`, `Status`, `State`, `Readiness`, `Basis`, `Blocked by`, `Parent`, `Effort`, `Order`, and `Revision`. Values use YAML scalar/list/object syntax. Kind is explicit, never inferred from a title or directory. A self-contained implementation issue needs `Basis: null` and `Blocked by: []`; spec-based work supplies `{ref: ..., revision: N}`. Missing or conflicting lifecycle, readiness, kind, basis or dependencies require correction before execution. Read-only normalization leaves the source unchanged; an authorized claim or other update writes typed metadata at the existing authority.

Migration is separate from setup and implementation. First save a JSON object mapping original repository-relative record paths to new `work/` Markdown locations. Run `work_legacy.py --repo ROOT plan --mapping mapping.json` and save its JSON output outside the source tree. The plan reports classification, collisions, source fingerprints, and inbound Markdown references. Existing effort folders stay put; map only individual records. Remote records are outside this local migration interface. Source snapshots and original dependency/basis IDs are retained.

Review that exact plan with the user, including unresolved classification and reference problems. Before relocation, update every participating reader/writer to use this resolver and stop old readers: forwarding files are documentation, not an operating-system access control. Release claims and finish pending spec publications. Apply only the reviewed digest with `apply --plan plan.json --review DIGEST --readers-adopted`. The flag attests the adoption prerequisite; it cannot discover old tools. Changed Markdown inputs or references invalidate the plan and require regeneration and renewed review. Setup alone never authorizes this operation.

A versioned `work/legacy-map.json` preserves each old ID and resolves both original and new paths to it. The destination is the only writable record; the original path becomes a forwarding link. Claims always use the original identity. Retained source snapshots live under `work/legacy-history/`. Relative outbound links are checked and adjusted for the new location; inbound links continue through the forwarding file. Commit the mapping, destinations, snapshots and forwarding files together so other checkouts receive the same identity map.

Application journals intended writes before relocation. All normal record access fails closed while that journal exists. `work_legacy.py --repo ROOT resume` accepts unchanged or already-applied files and finishes the same transaction. An externally edited file requires explicit recovery rather than overwriting it. This process preserves one declared local authority; independent clones remain outside the coordinator's concurrency boundary.
