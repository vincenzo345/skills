# Reliable planning and implementation workspaces

Status: ready-for-agent
Kind: spec
Revision: 2
Date: 2026-10-20

## Problem Statement

Planning work is difficult to locate and resume across skills and conversations. Decisions, research, specifications, and implementation issues can be scattered or confused with historical material. The current local convention puts Wayfinder decision tickets and implementation issues in the same namespace. Implement has no defined no-argument selection rule.

In the observed Articles session, an application investigation drifted into another article-writing exercise. Valid session boundaries were poorly explained, and the user had to ask where the work was stored. The goal is to preserve Wayfinder's intended planning behavior while giving the related skills a shared, discoverable work record.

## Solution

Use one stable, request-named folder per effort across conversations and skills. The user accepted the recommended stable-folder design after comparing five alternatives. Completed efforts remain at their original locations and leave the active queue; superseded documents are kept separately from current work.

The default local layout is:

```text
work/
  queue.md
  <request-derived-slug>/
    README.md
    discovery.md
    map.md
    decisions/
    spec.md
    tickets/
    research/
    history/
```

Create only the artifacts an effort needs. A small change can go directly to a spec or implementation issue without manufacturing a Wayfinder map. An explicit user-provided issue or spec remains a valid implementation entry point.

The effort overview explains the original request, purpose, desired outcome, stage, current artifacts, and next action. It links to authoritative records rather than copying their decisions or issue states. The ordered queue defines cross-effort priority. Effort and issue records determine eligibility.

Wayfinder still charts first, stops after charting, and resolves one non-research decision per session, with the research exception. Each valid stop explains what finished, what remains, and how to start the next decision. Replies while a decision is unresolved continue that decision.

## User Stories

1. As a maintainer, I want an effort folder named after my request, so that I can recognize the work in the file explorer.
2. As an author of a request, I want its purpose and intended outcome recorded, so that a later session understands why the work exists.
3. As a returning user, I want a later conversation to resume the same effort, so that it does not create competing current folders.
4. As a user with similar requests, I want distinct identities when they concern different efforts, so that a matching title does not merge unrelated work.
5. As a Wayfinder user, I want the map and its decision tickets linked from the effort, so that I can inspect the route and resolved decisions.
6. As a grill-with-docs user, I want ordinary findings, requirements, and open questions saved in the effort, so that they survive the conversation.
7. As a maintainer, I want project vocabulary and qualifying ADRs to remain shared, so that effort folders do not create competing domain models.
8. As a to-spec user, I want the current specification saved with the effort, so that subsequent skills find the agreed scope.
9. As a to-tickets user, I want implementation issues separated from decision tickets, so that an agent cannot confuse planning questions with build work.
10. As a maintainer, I want implementation issues to identify their specification basis, so that changed requirements cannot silently leave obsolete work ready.
11. As a user, I want to order efforts, so that a bare implement invocation follows my priorities.
12. As a user, I want an explicitly named effort, spec, or issue to override queue selection, so that I can direct the next work.
13. As an implementation agent, I want only eligible work selected, so that I do not act on historical, canceled, superseded, or unapproved material.
14. As an implementation agent, I want uncompleted blockers and existing claims respected, so that I avoid premature or duplicate work.
15. As a user, I want an independent ready issue considered when another issue is blocked, so that a blocked item does not stall unrelated work.
16. As a user, I want a clear explanation when no work is eligible, so that I know which input or dependency is missing.
17. As a maintainer, I want completed efforts preserved at stable paths, so that historical links continue to work.
18. As a returning user, I want superseded specifications and decisions clearly identified, so that I can inspect history without mistaking it for current direction.
19. As a remote-tracker user, I want tracker state to remain authoritative, so that a stale local overview cannot create conflicting work.
20. As a Wayfinder user, I want each session ending to name the current map and next decision, so that I can distinguish a completed session from a completed effort.
21. As a planning user, I want experiments tied to a specific unresolved decision, so that planning does not drift into unrelated deliverables.
22. As a human decision maker, I want unresolved human choices left open, so that the agent does not simulate my judgment.
23. As a maintainer of existing work, I want legacy records handled without silent movement or renumbering, so that adoption does not destroy references.
24. As a maintainer, I want repeatable checks of the cross-skill handoff, so that these failures can be detected before release.

## Implementation Decisions

### Agreed direction

1. Preserve Matt Pocock's intended Wayfinder lifecycle. The inspected upstream revision is `5beb35b040e3de97e54fa9e386d7e42d15c295c2`; local runtime differences were limited to the setup skill name. This is a reliability and integration change, not an autonomous planning-loop redesign.
2. Use stable effort folders, a readable overview, an ordered queue, and separate historical artifacts. Treat the user's acceptance of the recommendation as choosing this option over physical active/archive movement.
3. Carry the same effort through Wayfinder, grill-with-docs, to-spec, to-tickets, and implement. Keep optional entry paths intact.
4. Separate decision tickets from implementation issues. They have distinct purposes and eligibility rules even where both are represented as Markdown.
5. Preserve source-of-truth boundaries: queue for priority, effort record for effort lifecycle/current artifact references, issue for issue state and blockers, and configured remote tracker for remote state.
6. Preserve explicit selection precedence. Automatic selection uses queue priority and eligibility, not newest files, alphabetical order, or directory presence.
7. Preserve upstream human decision boundaries. An experiment must identify the decision its results inform before it becomes a blocking prerequisite.
8. This session produces the spec and decisions. It does not implement skill changes, install global skills, publish a release, or begin application work.

### Required behavior to implement

1. Define one shared work-record contract and reference it from participating skills. Avoid independent copies of the rules.
2. Store a concise request/description, stable identity, current stage, current spec reference, next action, and relevant artifact links in the effort record. Keep individual issue state in the issue itself.
3. Let grill-with-docs record ordinary requirements and decisions in an effort's discovery record or the current decision ticket. Keep glossary and ADR scope unchanged.
4. Make to-spec write the current spec in the identified effort and preserve an earlier materially different version. Spec readiness alone must not imply all child issues are ready.
5. Make to-tickets create separate implementation issues linked to the current basis, with explicit dependencies and existing user approval of the breakdown.
6. Make implement resolve explicit inputs first, otherwise select from the queue. Check issue kind, readiness, spec currency, blockers, and claims before work. A direct spec remains supported when explicitly selected and sufficiently ready.
7. When the current spec changes materially, identify affected unfinished issues and require reconciliation before their implementation. Preserve completed work and earlier decisions as history.
8. Keep completed, canceled, waiting, and superseded states distinguishable. Remove terminal efforts from active selection without moving their folder.
9. Where a remote tracker is configured, query its authoritative state and dependencies. Local files hold assets and links; do not create a second mutable tracker.
10. Keep claim handling compatible with concurrent implementation sessions and implement-spec. A stale worktree copy must not authorize duplicate work.
11. At a Wayfinder boundary, provide the map link, resolved work, next decision by name, and the next invocation or required input. Do not mark the map complete merely because a session ended.
12. Reconcile the local tracker convention and setup guidance with the new default. Retain explicit legacy references; provide an opt-in migration path with a classification report, preserved IDs, and reference checks.
13. Update participating human documentation and router guidance together. Add an appropriate release note and run existing package validation. Installation follows the repository's established release procedure after implementation.

### Shared contract design outcome

The [shared work-record design](design.md) defines the contract for implementation planning. These are technical choices made during design, not retroactive claims of user approval. [Revision 1](history/spec-r1.md) is retained as the prior specification basis.

1. Use versioned YAML front matter in local Markdown, typed record kinds, stable repository-relative identities, and fully qualified remote references. Keep readable bodies and one authoritative value per fact.
2. Separate lifecycle from stage, triage readiness, and operational claims. Derive eligibility from current authority rather than storing it. Waiting, completed, canceled, and superseded records remain distinguishable.
3. Number material spec revisions with increasing integers. Retain prior content, gate all mismatched unfinished issues until impact review, and advance unaffected issues only with a recorded no-impact rationale. Preserve completed issues on their original basis.
4. Use explicit dependency references and deterministic within-effort order. Only completed implementation blockers satisfy dependencies; canceled or superseded blockers require reconciliation. Preserve Wayfinder's separate decision-frontier behavior.
5. Resolve explicit issue, spec, or effort inputs before the queue without bypassing eligibility. Bare implement selects implementation issues only. A direct spec is an explicit path for undecomposed scope; a decomposed spec uses its issue graph.
6. Share authoritative reads and atomic claims across local worktrees. Claims have owner tokens, explicit release/recovery, and no automatic time-based expiry. Direct-spec and child-issue claims conflict; implement-spec uses the same individual issue claims.
7. Bound local concurrency to one declared authoritative checkout and shared coordinator. Remote adapters must prove exclusive claiming or establish a shared single controller; unavailable authority and unsupported concurrency are explicit errors, not local fallback.
8. Preserve explicit legacy references through normalization. Opt-in migration uses a classification plan followed by reviewed application, preserves IDs, and checks references. Exact command spelling is left to implementation.

The design walks the agreed handoff and failure scenarios. Those walkthroughs are analytical evidence, not executed behavioral replays. Local locking/crash recovery, remote adapter capabilities, and migration safety still require implementation tests. No new product-policy question blocks issue planning; any provider limitation requiring a changed authority or concurrency promise must be raised specifically.

## Testing Decisions

Vince confirmed the primary seam: the complete cross-skill work-folder handoff. Test observable selection and durable artifacts, not whether instructions contain certain phrases.

Use temporary repository fixtures with multiple efforts. Exercise creation/resumption, discovery, spec production, issue production, and implementation selection. Checks should establish:

1. Reusing an identified effort does not create a competing current record.
2. A new effort with a similar title remains distinct.
3. An explicit reference wins over queue order.
4. Bare implement selects the first eligible effort and a ready, unclaimed, unblocked implementation issue within it.
5. Decision tickets, historical documents, terminal efforts, and stale-basis issues are never implicitly selected.
6. A blocked first issue does not prevent selection of an independent eligible issue.
7. Missing or ambiguous readiness produces a specific explanation rather than a guess.
8. A changed spec preserves history and prevents affected unreconciled issues from being selected.
9. An unavailable remote tracker or Git ownership error is reported as unavailable information, not absence of work.
10. Concurrent consumers cannot claim the same issue from stale local copies.
11. Local artifact links remain valid after completion or opt-in migration.

Also exercise the design's scope-conflicting spec/issue claims, token-based resume and abandoned-claim recovery, interrupted revision publication, canceled blockers, and indeterminate higher-priority authority. Verify that explicit invalid inputs never fall through to unrelated queue work and that implement-spec exposes completed blockers only after integration.

Keep behavioral replay cases separate from deterministic artifact checks: destination preservation, breadth-first charting, legitimate stop with next invocation, unresolved-ticket continuation, human judgment retained, and experiment relevance. Use a minimal synthetic version of the Articles failure, not a public dump of the private conversation. Report replay outcomes and limitations; passing structural checks does not prove model compliance.

Prior art is the existing Python package validator, its mutation-style unit tests, installer safety tests, and meeting-record preservation checks. Extend these mechanisms where appropriate. Cache-only runtime/comparison directories are not evidence of an available executable harness. A small replay fixture set is sufficient; no evaluation platform is required.

Existing CI targets the v2 branch while this checkout's HEAD names main. Confirm the intended integration branch and ensure the relevant checks run there as part of delivery; do not silently broaden release behavior.

## Out of Scope

- Building the blog-writing application or continuing its article experiment.
- Replacing Wayfinder with automatic resolution of multiple human decisions.
- Adding a new skill, general workflow engine, or evaluation service.
- Broad changes to unrelated skills or the editorial skill collection.
- Requiring every effort to have a map, ADR, glossary, or decomposed issue set.
- Changing all repositories' trackers or migrating existing records automatically.
- Duplicating remote tracker state in a local status system.
- Implementing, committing, installing, or releasing changes during this specification step.

## Further Notes

Next work: use the shared record/selection design with to-tickets to propose and approve vertical implementation slices. Suggested sequence is an end-to-end local handoff first, history/reconciliation and legacy compatibility next, and remote/concurrent integration with its own acceptance evidence.

The first slice must demonstrate more than creating directories: a newly produced ready issue must be discoverable by the implementation consumer. This list is a work outline, not a published or approved implementation issue set.

The earlier discovery document is retained as background. This spec is the current synthesis. The stable folder decision is recorded separately as an ADR.

Revision 2 records the completed contract design and additional acceptance cases. No implementation issues existed when it was published, so there are no child issue bases to reconcile. The current design, this spec, and the overview remain planning artifacts, not an implementation authorization.
