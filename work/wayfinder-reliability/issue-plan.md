# Approved implementation breakdown

Status: approved and published as seven local implementation issues
Basis: [specification revision 2](spec.md) and [shared contract design](design.md)

Vince approved these seven slices and their dependency graph on 2026-10-20. Individual implementation issues are linked below and own their live states. This document retains the approved breakdown and shared delivery requirements; the standing planning-only boundary still applies to implementation.

The seven approved slices each deliver observable behavior with their own tests, affected human documentation, and router guidance. The first connects actual producers to the consumer rather than delivering only a schema. Subsequent slices extend that working path.

## Published issues

1. [Local issue handoff](tickets/01-local-issue-handoff.md)
2. [Work selection](tickets/02-work-selection.md)
3. [Planning continuity](tickets/03-planning-continuity.md)
4. [Spec reconciliation](tickets/04-spec-reconciliation.md)
5. [Concurrent implementation](tickets/05-concurrent-implementation.md)
6. [Legacy adoption](tickets/06-legacy-adoption.md)
7. [Remote authority](tickets/07-remote-authority.md)

## 1. Produce and claim a local implementation issue in one stable effort

**Blocked by:** None.

**What it delivers:** A small request can become a current spec and approved implementation issue in a stable effort, and implement can resolve and claim that explicitly named issue.

**Acceptance criteria:**

- The local setup convention and shared contract agree on typed records, identities, lifecycle, readiness, and authority. Participating producers and consumers reference one contract.
- to-spec and to-tickets reuse identified effort context, keep request/outcome/current pointers durable, and create only needed artifacts. Similar titles do not merge unrelated efforts.
- An approved breakdown produces separate implementation issues with current spec basis, explicit dependencies, deterministic order, and durable approval context. Spec readiness does not approve its children.
- Explicit implementation selection validates kind, readiness, active effort where applicable, basis, and completed blockers, then acquires an exclusive claim before beginning. Missing metadata yields a precise explanation.
- The minimum local coordinator reads from one authoritative checkout, serializes acquisition, and persists token ownership. Two competing explicit consumers cannot both start. Unsupported access fails closed.
- A temporary repository fixture runs the producer-to-consumer path and verifies the selected issue and durable records. No map or fabricated decision is required.

**Boundary:** Initial spec publication and an explicit issue path only. Queue selection and whole-spec claims arrive in slice 2; full resume/recovery and implement-spec orchestration arrive in slice 5. Until then, an abandoned claim remains blocking rather than being stolen.

## 2. Select eligible work by queue priority or explicit scope

**Blocked by:** 1.

**What it delivers:** Bare implement finds the first eligible implementation issue; explicit effort, issue, and spec inputs reliably constrain selection.

**Acceptance criteria:**

- Queue order controls cross-effort priority; issue order controls selection within an effort. Blocked or claimed issues do not prevent independent eligible work.
- Explicit references override queue position and membership without bypassing eligibility. An invalid explicit target never falls through to unrelated work.
- Bare selection excludes decisions, history, waiting/terminal efforts, stale bases, and undecomposed specs. Missing readiness, invalid ordering, and unavailable authority have distinct diagnostics.
- An indeterminate higher-priority effort prevents claiming that a lower effort is first eligible. Known ineligibility permits traversal to continue.
- An explicitly selected undecomposed spec and a self-contained issue remain supported. Decomposed spec selection uses its issue graph.
- Whole-spec and child-issue claims conflict. Completed specs cannot authorize repeat execution; completed efforts leave the queue without changing paths.
- Fixtures cover multiple efforts, independent blocked work, explicit overrides, optional inputs, scope conflicts, and no-eligible-work explanations.

## 3. Preserve planning context and Wayfinder session boundaries

**Blocked by:** 1.

**What it delivers:** Wayfinder and grill-with-docs carry durable planning context into the same effort that to-spec and to-tickets already consume.

**Acceptance criteria:**

- Maps and decision tickets live separately from implementation issues and remain authoritative for planning answers. Discovery holds ordinary requirements and findings; glossary and qualifying ADRs remain project-wide.
- Charting records the destination, breadth-first decisions, and fog, then stops with the map link, next decision by name, and next invocation or required input.
- Replies to an unresolved decision continue that decision. One non-research resolution per session and the research exception remain intact.
- Human judgments stay unresolved until answered. Proposed experiments name the destination decision and explain how possible results inform it before becoming prerequisites.
- Invalidated decisions preserve earlier answers, identify replacements, update current references, and trigger dependent review. A session ending never marks the map complete by itself.
- Structural fixtures verify artifact identity and handoff links. Separate synthetic behavioral replays cover continuation, human judgment, legitimate stops, and the Articles scope-drift regression; reports distinguish observed behavior from structural proof.

**Boundary:** Preserve upstream planning behavior. This slice does not authorize automatic multi-decision planning or application implementation.

## 4. Revise specs without leaving obsolete issues actionable

**Blocked by:** 1.

**What it delivers:** A materially changed spec preserves its earlier basis and prevents unfinished issues from starting or completing against unreconciled requirements.

**Acceptance criteria:**

- Material changes increment the revision and retain resolvable previous content. Editorial corrections do not require false material revisions.
- Current spec and effort references agree; publication uses the same coordination boundary as claims. Interrupted publication fails closed and retries preserve retained history.
- All mismatched unfinished issues initially fail currency checks. Unaffected issues advance with explicit no-impact rationale; affected issues update scope and readiness, with renewed approval when the breakdown materially changes.
- Completed issues retain their historical basis. Follow-up requirements become new work rather than retroactively changing completed evidence.
- Active consumers revalidate before publishing results or completing; changed bases pause dependent work without stealing claims or discarding existing work.
- Fixtures cover affected and unaffected siblings, historical lookup, interrupted publication, concurrent publication/acquisition, and completed-work preservation.

**Boundary:** This slice implements the shared publication and validation operations. Other consumers, including implement-spec and remote adapters, must reuse them rather than invent revision policy.

## 5. Resume claims and integrate concurrent implement-spec workers safely

**Blocked by:** 2, 4.

**What it delivers:** Multiple local implementation sessions and implement-spec workers share live authority, safely resume work, and expose dependencies only after integration.

**Acceptance criteria:**

- Worktrees share the authoritative record source and claim coordinator; stale worktree metadata cannot grant ownership or overwrite live status.
- Resume validates the ownership token, current scope, basis, and dependencies. Same user/branch and elapsed time never substitute for ownership.
- Explicit recovery establishes that the old worker has stopped, preserves its work pointer, invalidates its token, and grants replacement ownership atomically. If stoppage cannot be established, the claim remains blocking.
- implement-spec claims individual frontier issues through the same protocol. Independent issues can proceed concurrently; a dependent issue waits until blocker work is available on the integration branch.
- Process/crash and stale-copy fixtures establish exclusive acquisition, token-safe release, interrupted-operation behavior, scope conflicts, and integrated dependency readiness on supported local platforms.
- Unsupported independent-clone or multi-machine local concurrency is reported clearly. Git ownership errors remain access failures, not empty frontiers.

## 6. Adopt legacy records without breaking references

**Blocked by:** 2, 4.

**What it delivers:** Explicit legacy inputs remain usable, and an opt-in migration can bring classified records into the stable effort layout without losing identities or historical bases.

**Acceptance criteria:**

- Explicit legacy references normalize recognized kinds, readiness, parents, and dependencies without changing their originals. Ambiguous records remain blocked with precise missing-information explanations.
- A read-only migration plan classifies records and reports identity collisions, ambiguous types, input fingerprints, and inbound references.
- Applying a reviewed plan checks for changed inputs, preserves IDs and history, maintains forwarding references where needed, and leaves one writable authority.
- Adoption sequencing prevents old readers from mutating forwarding copies. Interrupted application is resumable or leaves an explicit recovery state.
- Fixtures demonstrate resumption from a legacy reference, decision/implementation separation, preserved dependency IDs, valid inbound links, and rejection of stale or ambiguous plans.

**Boundary:** No automatic migration, renumbering, or moving remote issues. The implementation fixture is not permission to migrate unrelated user repositories.

## 7. Respect remote authority and bound remote concurrency

**Blocked by:** 3, 5.

**What it delivers:** The configured remote tracker participates in the same planning-to-implementation handoff while keeping remote state authoritative and enforcing the documented concurrency boundary.

**Acceptance criteria:**

- Existing supported remote adapter guidance maps the shared record facts, current spec basis, readiness, native dependencies, ordering, and completion semantics without creating a mutable local status mirror.
- The complete handoff preserves remote map/decision authority and local asset links. Implementation queries current remote state before selection and before completion.
- For each supported claim path, document and verify conditional exclusive acquisition or one established shared controller. A two-contender test is required before claiming concurrent support.
- If a provider lacks the required capability, automatic concurrent claiming reports unsupported behavior. Assignment alone and per-worktree claims are not accepted as proof of exclusivity.
- Unavailable remote records, incomplete dependency queries, stale revisions, canceled blockers, and conflicting existing claims fail with specific explanations.
- Adapter contract fixtures cover authority and failure behavior. Any actual provider verification is reported separately from mocks; unavailable credentials or unverified capabilities remain explicit delivery limitations.

**Boundary:** Use existing configured mainstream trackers. Do not add a distributed lock service, new tracker, or new authority to work around provider limitations without returning the consequential choice to the user.

## Dependency rationale

Slices 2, 3, and 4 independently extend the local path from slice 1. Slice 5 needs scoped claims from 2 and revision coordination from 4. Slice 6 needs the resolver from 2 and revision/history handling from 4. Slice 7 needs planning handoff behavior from 3 and the completed consumer protocol from 5. Migration is not a dependency of remote support.

## Delivery requirements shared by every slice

- Keep changed skill instructions, human documentation, setup guidance, and router relationships synchronized in the slice that changes behavior.
- Add observable artifact/selection tests at the agreed handoff seam, and behavioral replays where agent conduct matters. Do not replace either with phrase-presence tests.
- Run relevant package and regression checks. The final combined delivery reruns the handoff matrix and records remaining platform/provider limitations.
- Maintain an appropriate release note and follow established validation, installation, and release procedures only during subsequently authorized implementation/delivery.
- Confirm the integration branch before implementation delivery: this checkout is on `main`, while the current validation workflow targets `v2`. Ensure checks cover the chosen target without silently broadening release behavior.

The individual issues are published in this effort's implementation-issue area, following the accepted design rather than the old skill's conflicting scratch-folder default. Publication adopts the designed envelope for these new records only; existing effort/spec formats and skill behavior remain unchanged.

## Approval and publication

On 2026-10-20, Vince replied "sounds good" to the request to approve the seven-slice granularity and dependency graph. That approval covers this breakdown and publication of the individual issues. It does not authorize implementation, installation, commits, or release.

All seven issues were published with specification revision 2 as their basis, explicit dependency references, and `ready-for-agent` readiness. Their own records govern subsequent state. The spec itself is unchanged; no work was claimed or started during publication.
