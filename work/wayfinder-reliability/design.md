# Shared work-record contract

Status: design complete for issue planning; not implemented
Date: 2026-10-20
Basis: [specification revision 1](history/spec-r1.md)
Current scope: [specification revision 2](spec.md)

## Outcome and decision authority

Use a small typed record envelope in Markdown, explicit references, and a shared selection/claim protocol. Store lifecycle and readiness separately. Derive eligibility at selection time; never store an `eligible` flag.

The [accepted ADR](../../docs/adr/0001-stable-effort-workspaces.md) settles stable effort folders, separated history, and remote tracker authority. The [discovery record](../../docs/plans/wayfinder-reliability.md) supplies the failure case and upstream comparison. Their accepted decisions remain unchanged. The metadata, state names, revision format, and protocols below are technical design recommendations selected for this handoff, not claims of earlier user approval.

This design defines future behavior. Existing documents in this effort retain their current format until adoption. No skill, tracker, installer, or queue consumer is changed here. Approval of an implementation breakdown remains a subsequent to-tickets activity.

## One source for each fact

| Record | Owns | Does not own |
| --- | --- | --- |
| `work/queue.md` | Ordered effort links | Readiness, claims, issue state, permission to implement |
| Effort `README.md` | Identity, request, outcome, lifecycle, stage, current artifact references, next action | Copies of issue statuses or decision answers |
| Discovery | Requirements, ordinary findings, open questions | Alternative glossary or ADR system |
| Map and decision tickets | Planning frontier and authoritative decision answers | Implementation readiness |
| Current spec and retained revisions | Scope, acceptance criteria, revision, spec readiness | Automatic readiness of children |
| Implementation issue | Deliverable, readiness, basis, dependencies, progress, approval/reconciliation evidence | Effort priority |
| Claim authority | Exclusive work ownership and resume token | Completion or scope approval |

For remote tracking, the configured tracker owns issue/map/spec records and native dependencies where supported. Local files are linked assets and history, not a second mutable tracker. A remote spec can link a repo-held content asset, but the adapter must declare which copy owns its content and revision; two independently editable current specs are invalid.

The effort record still owns the effort lifecycle and current artifact pointers. Remote mappings must preserve these logical facts without inventing competing local issue state. An overview may contain a dated summary, but selectors ignore it in favor of authoritative records.

## Identity and representation

Use UTF-8 Markdown with YAML front matter for new local typed records. The title and body remain readable prose. One metadata spelling per field; do not retain competing `Status:` lines. A future single shared contract reference will define the schema and selection rules for all participating skills. Tracker adapters map to that contract rather than copy its policy.

- `schema: 1` identifies the envelope version, not a spec revision. Unknown versions fail with an unsupported-schema explanation.
- `kind` is `effort`, `map`, `decision`, `spec`, or `implementation`. Discovery, research, and ordinary assets need no envelope unless a consumer must select them.
- The local effort ID is its repository-relative stable directory, such as `work/search-workflow`. It is independent of the display title. Do not rename that directory when the title changes. On a slug collision, create a distinct suffix such as `search-workflow-2`; never merge by title.
- Local child IDs are their stable repository-relative paths. Remote IDs are fully qualified tracker references including tracker instance/repository. Bare numbers resolve only inside a known tracker scope.
- Relationships carry these IDs, not titles. Paths in metadata are repository-relative; prose links are relative to the containing Markdown file. No implicit current-directory resolution.
- Resolve explicit effort context first, then an unambiguous existing conversation reference. A similar title alone is insufficient to resume. Ask only when identity is ambiguous.

Each effort has zero or one current spec and zero or one current map; it can have many decisions, implementation issues, and assets. Each child belongs to exactly one effort when managed by this convention. A directly supplied standalone spec or implementation issue can omit effort membership; it is never discovered by the effort queue.

### Required and conditional fields

| Kind | Fields in addition to `schema`, `kind` | Body requirements |
| --- | --- | --- |
| Effort | `id`, `state`, `stage`, `current_spec`, `current_map`, `next_action` | Title, original request, purpose/outcome, relevant artifact links |
| Spec | `id`, `effort` when managed, `revision`, `state`, `readiness` | Scope and acceptance criteria; readiness rationale; revision notes when revised |
| Implementation | `id`, `effort` when managed, `state`, `readiness`, `basis`, `blocked_by`, `order` when queue-managed | Deliverable, acceptance criteria, breakdown approval or explicit task authority; reconciliation notes when basis changes |
| Map | `id`, `effort`, `state` | Existing Wayfinder Destination / Notes / Decisions so far / Not yet specified / Out of scope |
| Decision | `id`, `effort`, `map`, `type`, `state`, `blocked_by`, `order` | Existing question and authoritative answer on resolution |

`current_spec` is either `{ref, revision}` or explicit `null`; `current_map` is a reference or `null`. `basis` is `{ref, revision}` or explicit `null` for a self-contained implementation issue. `blocked_by: []` means no dependencies; absence means unknown, not none. No timestamps, UUIDs, event log, or copied issue list are mandatory.

`order` is a positive integer unique among current implementation issues in an effort, and separately among current decisions in a map. to-tickets assigns increasing numbers in approved breakdown order, with blockers first where possible. These numbers express within-effort preference, not execution steps. Later issues receive unused numbers; existing IDs are never renumbered. The same field can map to an existing authoritative remote ordering mechanism.

Optional `superseded_by` points at a replacement. It is required when a record is marked superseded. Waiting and canceled records require a body explanation; waiting also names the input or condition that would permit resumption. Missing, duplicate, or contradictory required fields make the affected selection scope invalid.

```yaml
---
schema: 1
kind: effort
id: work/search-workflow
state: active
stage: implementation
current_spec:
  ref: work/search-workflow/spec.md
  revision: 2
current_map: null
next_action: Implement the next eligible search slice.
---
```

```yaml
---
schema: 1
kind: implementation
id: work/search-workflow/tickets/02-filter.md
effort: work/search-workflow
order: 2
state: open
readiness: ready-for-agent
basis:
  ref: work/search-workflow/spec.md
  revision: 2
blocked_by:
  - work/search-workflow/tickets/01-search.md
---
```

The examples are illustrative future records, not work created or approved by this design.

## Lifecycle and readiness

| Record | States | Transition rules |
| --- | --- | --- |
| Effort | `active`, `waiting`, `completed`, `canceled`, `superseded` | Active and waiting may alternate with a reason. Terminal states require an explicit recorded outcome; superseded links a replacement. Terminal efforts leave the queue and retain their directories. |
| Spec | `current`, `completed`, `superseded`, `canceled` | One current revision per spec. A material revision supersedes the previous one. Complete after direct execution or the full issue graph satisfies acceptance and integration requirements. Completed or canceled scope cannot authorize another implementation run. |
| Implementation | `open`, `in-progress`, `waiting`, `completed`, `canceled`, `superseded` | Claim an eligible open issue before entering in-progress. Release back to open for unfinished resumable work, or waiting for missing input. Complete only after acceptance and the tracker-defined integration/closure step. |
| Map | `open`, `completed`, `canceled`, `superseded` | Completing charting or a session does not complete the map. Completion requires no remaining in-scope decisions or fog. |
| Decision | `open`, `resolved`, `canceled`, `superseded` | Claim while open; resolved requires the answer. Canceled/out-of-scope is distinct from an answer and stays out of Decisions so far. |

Effort `stage` is `discovery`, `decisions`, `specification`, or `implementation`. It describes the next substantive activity, can move backward after new findings, and never grants execution permission. `state` describes lifecycle independently of stage.

The effort's current-spec pointer identifies the latest authoritative revision even after its completion; it need not point to a spec whose lifecycle is still `current`. Finishing the spec does not automatically complete the effort if its requested outcome includes other unfinished work.

Use the existing triage vocabulary for spec and implementation `readiness`: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. Only `ready-for-agent` passes autonomous implementation selection. Readiness describes sufficient, authorized inputs; it does not encode dependency completion or claim ownership. A ready issue may still be blocked. Decisions and maps never receive implementation triage readiness.

to-spec may mark its synthesis ready under its existing contract when the inputs and agreed testing seam are sufficient. This neither approves an issue breakdown nor starts implementation. to-tickets records the approved breakdown context in issue bodies before marking published issues ready; pending human choices remain unresolved. Record a durable concise account of the approval and its scope, not a claim that the whole project was approved.

No terminal record reopens merely because it was named explicitly. Reopening existing work requires an explicit intent and recorded reason, followed by readiness/basis validation; a changed destination is a new effort under Wayfinder's existing scope rule. Completed work remains evidence even when follow-up work is needed.

## Spec revisions and reconciliation

Use positive integers, starting at 1 and increasing for material changes. Identity stays stable while revision changes. A material change alters scope, behavior, acceptance criteria, constraints, or required decisions. Typographical corrections and repaired links can retain the revision with a brief correction note. If impact is uncertain, treat the change as material.

Before publishing revision N+1, preserve the exact prior content in `history/spec-rN.md`, or retain an immutable remote revision/snapshot with a resolvable reference. History filenames identify their revisions; an unchanged snapshot may still say `current` inside because it records what was true then. Currentness is determined by the effort pointer and live authoritative spec, never by scanning snapshot headers. Relative links in a moved snapshot may need rebasing; record that mechanical correction without changing its historical meaning.

The publication operation must:

1. Retain revision N and record why the scope changes.
2. Make the current spec and effort pointer agree on N+1.
3. Enumerate unfinished issues based on the old spec and record their impact disposition. Until reviewed, all mismatched issues fail currency checks, even if their readiness still says ready.
4. For each unaffected issue, record an explicit no-impact rationale and advance its basis. For each affected issue, update its scope/criteria and readiness, then advance its basis only after reconciliation. If the approved breakdown changes materially, obtain approval for those changed slices before marking them ready.
5. Keep completed issues on their original basis. Create follow-up work for newly required behavior; do not rewrite what completed work meant.

Revision mismatch is a computed gate, not another lifecycle state. Reconciliation never silently bulk-updates basis numbers. Historical lookup resolves `(spec ID, revision)` to the retained content, not today's `spec.md`.

Publication and claim acquisition share a short coordination lock. An active worker must revalidate the basis before publishing results or reporting completion. If the basis changed, it pauses dependent work and reconciles; work already done is retained for review. Publication does not steal its claim.

Local multi-file publication need not pretend to be a filesystem transaction: selectors share the lock, and an interrupted update leaves mismatched pointers or an incomplete-publication marker that fails closed until recovery. Remote publication similarly withholds ready/current availability until linked records agree. A retry must detect an already retained revision and must not overwrite its historical content.

## Dependencies

`blocked_by` is a set of authoritative implementation issue references; cross-effort dependencies are allowed. Reject self-dependencies, cycles, unresolved IDs, and decision tickets used as implementation blockers. A decision that must precede an implementation issue keeps that issue at `needs-info` with a link and explanation until settled. It is not an implementation task.

An implementation blocker is satisfied only by `completed` under the tracker adapter's completion semantics. Canceled, superseded, closed-as-not-planned, unknown, or inaccessible is not completed. Reconcile a dependency explicitly if its work was replaced or no longer needed. Do not follow `superseded_by` automatically as though the replacement had completed.

Keep Wayfinder's separate decision-frontier semantics: local blockers resolve with decision answers; remote adapters preserve upstream closure behavior. An invalidated decision requires dependent decision review before selection. The implementation rules do not redefine the existing Wayfinder frontier.

For implement-spec, completion must represent availability on its integration branch before dependent workers start. Finished work on an unmerged worker branch remains in-progress. Every next worker receives the integration basis through the existing implement-spec orchestration.

## Claims and authoritative reads

Claims are operational records, not readiness labels or copied front-matter flags. The minimum claim contains `target`, opaque unique `token`, `owner` (session/worker identity), `workspace` (checkout/worktree pointer), and `acquired_at`. It persists until completion, release, or explicit recovery. Time alone never expires a claim.

Acquisition means one indivisible operation: read authoritative eligibility, check conflicting claims, create ownership, and return its token. Only the matching token may update or release that ownership. A read followed by an ordinary assignment write is insufficient evidence of exclusivity.

For local tracking, recommend one declared authoritative checkout for the live work records and one coordinator under the repository's shared Git administrative directory. All worktrees read live queue, effort, spec, and issue records through that checkout and use the same coordinator. Worktree copies are implementation inputs, never claim or readiness authority. Git discovery/ownership errors stop this access path with a diagnostic; never substitute the current stale tree.

The future helper must provide process-safe locking on supported local filesystems, durable claim records, serialized record publication, and compare-by-token release. Selection plus claim acquisition happens under the same short lock; implementation runs outside it. Record edits from worker branches must be reconciled through the authority rather than blindly merged over live status. Independent clones or machines without a shared coordinator are outside this local guarantee and must not be advertised as concurrent consumers of the same local tracker.

Claims have two scopes:

- An issue claim excludes another claim on that issue but permits independent issues.
- A direct-spec claim excludes every issue claim based on that spec, and vice versa. A standalone issue without a spec is claimed by its own identity.

implement-spec claims individual frontier issues using this same protocol; it does not take a conflicting whole-spec claim. An explicit spec with decomposed issues uses the issue graph; direct-spec execution is only for a spec without current implementation children. Do not run the same scope once as a spec and again as its children.

Resume requires the recorded token plus revalidation of current authority, basis, and dependencies. Same username, branch, or apparent inactivity is not proof of ownership. A lost token or abandoned worker requires explicit recovery: establish that the previous worker has stopped, preserve its work pointer, invalidate its token, and issue a new claim under the lock. If that cannot be established, report the claim as blocking. No automatic timeout takeover.

For remote tracking, fetch current authoritative records/dependencies and respect existing assignees/claims. A remote adapter must demonstrate conditional exclusive acquisition or use one declared coordinator shared by all participating consumers. Existing native assignment semantics, including Wayfinder's assignment behavior, are not by themselves a proven atomic implementation claim. No guarantee is made about a particular provider in this design.

If a provider cannot satisfy that contract, concurrent automatic claiming remains unsupported there. Report the missing capability and use a separately established single-controller arrangement only when its exclusivity is known. Never emulate remote authority with per-worktree local claims. Provider verification and a two-contender test are implementation acceptance requirements, not an invitation to add a general distributed lock service.

## Selection precedence and eligibility

An implement invocation authorizes selection within its requested scope, subject to any standing planning-only constraint. Merely preparing ready records or putting an effort in the queue does not invoke implementation.

1. Resolve explicit input first. An issue selects that issue only. A spec selects its current issue graph, or the direct-spec path if it has no current implementation children. An effort selects only that effort's implementation issues. Multiple incompatible or ambiguous explicit references require clarification.
2. Explicit selection bypasses queue position and membership, never lifecycle, kind, readiness, currency, dependencies, or claims. An ineligible explicit target returns its reason; it does not fall through to unrelated queue work.
3. Without explicit input, traverse the queue's unique effort links in listed order. Only active efforts qualify. Waiting and terminal efforts are skipped with reasons even if stale queue links remain.
4. Within an active effort, enumerate current implementation issues from the authoritative tracker, ordered by `order`. Select the first open, ready-for-agent issue whose basis is current, whose blockers are complete, and which has no conflicting claim. A spec-based issue also requires a current ready-for-agent spec. A self-contained issue with explicit `basis: null` requires sufficient criteria and authority in its own body.
5. Skip a known blocked, claimed, waiting, terminal, stale-basis, or unready issue and consider independent issues. If none qualify, continue to the next effort. Bare implement never chooses a direct spec or a decision ticket.
6. Recheck and acquire atomically before starting. Losing a claim race restarts selection within the same permitted scope. Explicit single-issue selection reports the competing claim instead.
7. Report the chosen title, effort, basis, and authority. If nothing qualifies, report the relevant reasons and next input/action. Never turn missing information into “no work.”

Malformed ordering, duplicate identities, unreadable authority, unknown dependency outcomes, or unsupported schema make the affected scope indeterminate. Do not silently skip an indeterminate higher-priority effort to claim that a lower one is first eligible. An unrelated explicitly selected valid scope can still proceed. Known ineligibility and unavailable information have different outcomes.

Historical path inputs are rejected for execution with a pointer to the current record, when known. Explicit legacy inputs remain supported through normalization below; being explicit does not make ambiguous readiness acceptable.

## Legacy and adoption boundary

No migration happens in this design session. Keep explicitly referenced `.scratch` and tracker records usable at their original IDs. Normalize recognized `Status:` values, explicit kinds/labels, blockers, and parent references in memory. Missing kind, readiness, or basis is not inferred from an `issues/` directory or a file title. Explain the precise gap and resolve it before implementation.

Recommend a future explicit two-step migration interface: `plan(source, destination)` produces a classification/reference report; `apply(report)` applies the reviewed mapping after checking that inputs have not changed. The eventual command spelling is incidental. The report identifies maps, decision tickets, implementation issues, specs, ambiguous records, collisions, and inbound links.

Preserve legacy record IDs and original references; migration records their old-ID-to-new-location mapping. Because new IDs normally equal stable creation paths, this is an explicit compatibility exception: moved legacy IDs are resolved through the mapping, never reassigned to new records. Keep forwarding references at old local locations when moved, and exactly one authoritative writable record. Do not move remote issues.

Apply only classified, reviewed mappings. Retain source snapshots, verify links and dependency identities, and make interrupted application resumable. Old readers must not continue mutating forwarding copies; adoption requires participating readers to use the new resolver before relocating records. An unsuccessful conversion leaves the original authority usable or selection blocked with a recovery report, never two current copies. Automatic migration and wholesale renumbering are rejected.

## Walkthrough against the agreed handoffs

These are design trace results, not executed skill replays. Future deterministic fixtures assert records and selection results; behavioral replays evaluate agent conduct separately.

| Scenario | Operation and expected observation | Design check |
| --- | --- | --- |
| Create and resume | Chart an application effort, then resume by its overview in another conversation. Resolve the same effort ID and map. | One folder and current map; no title-based duplicate. |
| Similar request | Start a distinct request with the same display title. Allocate a suffixed stable directory and separate queue entry. | No accidental merge of unrelated outcomes. |
| Charting boundary | Wayfinder records breadth-first questions and fog, then stops with map link, next decision name, and invocation. | Map remains open; charting does not manufacture implementation work. |
| Continue unresolved choice | A reply supplies more context for an open decision. Continue it; retain human questions until answered. | No new decision/session boundary inferred from each message. |
| Discovery handoff | grill-with-docs records ordinary requirements in discovery or the current decision ticket. Link project-wide glossary/ADRs only when warranted. | Durable context without duplicated decisions. |
| Spec production | to-spec writes revision 1 and updates the current pointer using the agreed seam. No issues exist yet. | A ready spec is discoverable, but bare implement finds no issue. |
| Approved decomposition | to-tickets presents slices; after approval it writes implementation issues, basis revision 1, ordering, and dependencies. | Decisions stay separate; a newly ready issue is discoverable by implement. |
| Queue and independent work | Queue A before B. A/1 waits on unfinished work, A/2 is independent and ready. | Select A/2. If A has no eligible issues, consider B. |
| Explicit override | Explicit B/1 or effort B while A heads the queue. | Evaluate only B/1 or B. An ineligible explicit target never falls back to A. |
| Direct inputs | Explicit ready undecomposed spec, or a self-contained ready issue without a map/spec. | Claim the spec scope or issue identity; optional planning artifacts stay optional. |
| History and false readiness | Decision ticket, history snapshot, canceled effort, stale basis, or missing readiness appears near current work. | Reject by typed record/currentness/readiness, independent of filename and dates. |
| Changed requirements | Preserve spec r1, publish r2, review unfinished A/1 and A/2. A/1 changes; A/2 is unaffected. | Both initially fail currency. A/2 advances with rationale; A/1 waits for reconciliation/changed-slice approval. Completed issues retain r1. |
| Competing consumers | Two stale worktrees try the same issue, including implement-spec workers. | Shared authority grants one token. Loser skips it or reports a conflict for an explicit target. |
| Scope overlap and resume | Direct-spec worker competes with a child issue worker; later its session disappears. | Overlapping claims conflict. No timeout takeover; token resume or explicit recovery is required. |
| Remote failure | Tracker unavailable, dependency unreadable, or conditional claim capability missing. | Report unavailable/unsupported information. No local-state fallback or invented empty frontier. |
| Ownership failure | Git refuses access to shared authority. | Report the access error; do not change Git trust configuration or use a stale worktree as authority. |
| Completion and migration | Complete an effort; remove its queue entry. Later review an opt-in legacy mapping. | Original effort links stay valid; migration preserves IDs and verifies forwarding links. |
| Articles regression | Application planning proposes an article rewrite as a prerequisite. | Require the unresolved destination decision and how possible results inform it; otherwise keep it outside the blocking path. |
| Decision supersession | A settled answer is invalidated. Retain its answer, create/link its replacement, update the map pointer, review dependents. | Old evidence remains readable; replacement is not silently treated as resolved. |

## Alternatives and limits

- Reject moving completed effort folders, stage/session-based identities, and duplicate remote status stores because the ADR already settles those choices.
- Reject filename/date-based selection, a single overloaded status field, and automatic readiness inheritance because they cannot distinguish the failure cases.
- Reject UUIDs for every local record, event sourcing, automatic claim leases, and a general workflow engine. Stable paths, retained material revisions, and explicit recovery meet this scope with less machinery.
- Use a conservative revision mismatch gate instead of speculative automated impact analysis. A short no-impact reconciliation restores independent work.
- Require shared authoritative reads as well as locks. A lock alone would still allow stale requirements or dependency state to authorize work.

No unresolved product-policy decision blocks this contract. Technical validation remains: supported local locking/crash recovery, concrete remote adapter capabilities, and legacy classification/link preservation. If provider limitations require a new authority or reduced concurrency promise, bring that specific tradeoff back before implementing it.

Next activity: to-tickets proposes vertical slices for the local end-to-end handoff, revisions/history and legacy compatibility, then remote/concurrent integration. The user approves that breakdown before issue publication. Confirm the intended integration branch and CI coverage during delivery. No implementation, installation, commit, or release is authorized by this document.
