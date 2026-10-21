# Wayfinder workflow reliability

Status: discovery record, superseded as the current synthesis by the [implementation specification](../../work/wayfinder-reliability/spec.md). Skill implementation is not authorized by this document. The user accepted the recommended stable effort-folder design and confirmed cross-skill handoff testing on 2026-10-20.

Current effort: [Wayfinder workflow reliability](../../work/wayfinder-reliability/README.md). Proposed alternatives and earlier open questions below are retained as discussion history; the current spec and [workspace ADR](../adr/0001-stable-effort-workspaces.md) take precedence.

## Confirmed destination

Improve Wayfinder and its direct dependencies using the Articles session as an observed regression case. Record unrelated discoveries separately. Vince confirmed this focused scope and requested an agreed change plan and decision documents before implementation.

Vince subsequently directed that the intended functionality of Matt Pocock's upstream Wayfinder be replicated. Upstream parity is the reference for continuation; this is not a request to redesign it as an autonomous multi-decision loop.

## Upstream reference

Compared local files with upstream commit `5beb35b040e3de97e54fa9e386d7e42d15c295c2` on 2026-10-20: [upstream skill](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/wayfinder/SKILL.md) and [human documentation](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/docs/engineering/wayfinder.md).

The delegated comparison found Wayfinder runtime differs only in the local setup skill name. Grilling, grill-with-docs, research, domain-modeling, and the local tracker seed have no line differences. Wayfinder human docs adapt setup/router links. Prototype has intentional local design-integration and artifact-handling changes; do not revert them wholesale. The non-code prototype mismatch exists upstream too.

Upstream charts a destination and decision map, then works one non-research decision per session with human judgment where required. Research may proceed in parallel. Charting stops after producing the map. Completion means the decisions are settled; the normal subsequent steps synthesize a spec and implementation issues. Replicating that behavior means preserving its deliberate boundaries while making the current state and next invocation clear.

The documentation itself records execution-scope and prototype-choice failures. Distinguish inherited limitations, fork differences, and agent noncompliance before changing runtime text.

## Observed failure

The user requested investigation and conditional planning of a blog-writing application. The session gathered useful framework facts, but shifted into producing another article and made author comparison a prerequisite for the application decision. Product discovery remained incomplete. Repeated summaries left continuation unclear, and the project was initially difficult to find.

The source of this account is the current user-agent conversation in the Articles workspace. Supporting artifacts include its `.scratch/blog-writing-app/map.md` and `content/reviews/ai-activity-systems/wayfinder-quality-test/run.md`. These are local evidence, not a publicly available regression fixture. Any committed fixture should use a minimal synthetic scenario.

## Existing contracts and candidate changes

| Finding | Current source | Proposed repair, not yet agreed |
| --- | --- | --- |
| Scope drift despite an explicit planning boundary | [Wayfinder](../../skills/engineering/wayfinder/SKILL.md) requires destination-first, breadth-first discovery and decision questions. | Before treating research or a prototype as blocking, state the destination decision and how plausible outcomes change it. Test execution against that contract. |
| Continuation is undefined across turns | Wayfinder limits non-research resolutions per session and stops after charting; [phase guidance](../../skills/engineering/guide-me/PHASE-BOUNDARIES.md) supports continuation within context. | Settle the meaning of session/invocation and continuation, with the next decision and required human input made explicit. |
| Local maps are hard to discover | [Local tracker](../../skills/engineering/setup-repo/issue-tracker-local.md) places maps in `.scratch/`; Wayfinder both requests setup and specifies a fallback. | Choose one fallback rule and require a visible pointer to the canonical map, without duplicating state. |
| Prototype composition disagrees | Wayfinder permits outlines and rough prose; [prototype](../../skills/engineering/prototype/SKILL.md) supports runnable logic/UI code. | Decide how bounded non-code evidence should be handled without adding a new skill. |
| Ordinary interview decisions are not durable | [grill-with-docs documentation](../engineering/grill-with-docs.md) explicitly leaves most decisions only in conversation. | Decide whether the wrapper should record ordinary decisions in the current issue/plan while preserving narrow glossary and ADR purposes. |
| Replaced decisions lack a defined history | Wayfinder allows changing invalidated issues but does not define supersession of a resolved answer. | Link the replacement, preserve history, update the current index, and reconsider dependencies. |

The original scope drift was substantially an agent execution failure. These proposals should clarify the minimal missing contracts, not duplicate existing instructions or claim that every failure requires more prose.

## Reuse before adding machinery

[Workflow gap log](../workflow-gap-log.md) already records an indexed work record, outcome/evidence/questions/next-action handoffs, and the rule that unknowns block dependent work only (R-02, R-03, R-11). Reuse these concepts.

The repository has [package validation](../../scripts/validate_v2_skills.py), validator/installer tests, and [CI](../../.github/workflows/validate-v2.yml). CI currently targets `v2`; this checkout's `.git/HEAD` names `main`. Git status is unavailable because Git rejects repository ownership. No Git configuration was changed.

Package checks are not behavioral proof. Extend deterministic checks only for mechanically enforceable contracts. Add a small behavioral scenario set for planning relevance, continuation, artifact discovery, and changed decisions. Existing runtime/comparison directories contain cache remnants; a runnable scenario harness has not yet been established.

## Interview state

- Confirmed: focused workflow improvement.
- Confirmed: agreed plan and decision documents are this session's outcome; implementation comes later.
- Confirmed direction: investigate upstream intended behavior and replicate it, preserving its one-decision session boundary rather than selecting a new automatic-loop policy.
- Latest user steering: design shared, request-named folders for Wayfinder, grill-with-docs, to-spec, and to-tickets so implement can locate actionable work and distinguish history. Include a description of what the effort/conversation concerns. This makes cross-skill storage/discovery part of the focused improvement.
- Current decisions: folder identity across sessions, visible root location, queue/selection policy.
- Later decisions: readiness and spec revisions, history handling, configured remote tracker authority, migration, and regression acceptance.

## Shared work-folder proposal

Status: proposal for discussion, not an accepted schema or an implemented skill behavior.

The user requests human-discoverable folders named after the request, a description/context record, and reliable selection of the next spec and tickets for implementation.

Current sources expose a concrete collision: Wayfinder's local decision tickets and to-tickets' implementation issues both use `.scratch/<slug>/issues/`. Implement expects a supplied reference and has no documented no-argument queue resolver. The folder design must distinguish the kinds of work and define selection, not merely rename `.scratch`.

Propose one stable folder per effort, spanning multiple sessions and skills. A session may update an existing effort; it should not automatically create another similarly named copy. Use a readable request-derived slug, with disambiguation only when needed.

Illustrative layout:

```text
work/
  README.md                         # Ordered queue and links; not a second decision store
  improve-blog-writing/
    README.md                       # Purpose, state, current artifact links, next action
    discovery.md                    # Interview context and ordinary decisions
    map.md                          # Optional Wayfinder map
    decisions/                      # Wayfinder decision tickets
    spec.md                         # Current spec
    tickets/                        # Implementation issues
    research/
    history/                        # Superseded artifacts and session records
```

Create only needed files. Glossary and qualifying ADRs remain in their established project-wide locations, linked from the effort; do not fork the domain model into each effort. Existing decision tickets remain authoritative for their answers; discovery and overview records link rather than duplicate them.

Suggested overview content: title, original request, concise purpose, intended outcome, current stage, approved/current spec reference, next action, and links to relevant evidence. Separate facts, user decisions, and proposals.

Suggested implement selection: an explicit effort/ticket reference wins; otherwise use the agreed ordered queue. An effort is eligible only when its implementation inputs are ready and current. Within that effort, select an unclaimed implementation issue with completed blockers. Never interpret a decision ticket, superseded spec, or historical file as ready implementation work. Resolve ambiguous eligibility rather than choosing the newest file.

Open design choices:

- Root path and whether one effort persists across sessions.
- Explicit queue ordering versus prompting whenever multiple efforts are ready.
- Whether completed effort folders stay in place with archived state or move to an archive tree; stable locations avoid link churn.
- Readiness and invalidation when discovery changes the spec after tickets were generated.
- How local artifacts relate to a configured remote issue tracker; avoid two competing authorities.
- Migration of existing `.scratch` efforts without mixing decision and implementation issue IDs.

The requested storage behavior is a deliberate local integration improvement beyond literal upstream text parity. Preserve upstream's planning/decision boundaries while designing it.

## Folder alternatives

Status: design comparison requested by Vince; no layout selected. Assess against human discoverability, reliable next-work selection, continuity across skills/sessions, historical isolation, and maintenance. These are design judgments, not measured performance results.

| Alternative | Shape | Main benefit | Main cost | Assessment |
| --- | --- | --- | --- | --- |
| Stable effort folders | `work/<request-slug>/` plus ordered queue | One permanent home throughout discovery and implementation; stable links | Active/history distinction depends on explicit metadata and queue filtering | Recommended first |
| Active and archived effort folders | `work/active/<request-slug>/`, `work/archive/<request-slug>/`, plus active queue | Closed work is physically outside the normal discovery path | Archiving moves paths; references and retained identities require care | Recommended second |
| Stage folders | `work/discovery/`, `work/specs/`, `work/tickets/`, grouped by effort within each | Easy to inspect all work at a particular stage | Splits each effort across locations; cross-stage handoff and history are harder | Reject for this workflow |
| Session folders | `work/<date>-<request>/` per conversation | Easy chronological browsing and conversation capture | Several folders compete to describe the same effort; difficult to identify current spec | Keep sessions as subordinate records only |
| Tracker-ID asset folders | `work/W-0042-<slug>/` with authoritative remote tracker links | Strong identity and alignment with remote issue state | More tracker interaction and indirection; less useful as a standalone local work queue | Useful adapter when remote tracking is central |

### Preferred: stable effort folders

Keep one effort at `work/<slug>/` for its lifetime. The ordered queue references effort identities/paths and owns priority, not copied ticket state. Each effort has one authoritative overview/status record, and individual tickets own their states and blockers. A human-readable catalog can show active and archived views from those records.

Within an effort, separate decision tickets from implementation tickets. Keep current approved spec links explicit. `history/` contains superseded artifacts and optional session records; an archived effort remains at its stable path but is excluded from default implementation selection.

This fits repeated discovery/spec/revision cycles without moving the effort. It is the least disruptive default for existing relative references and future automation.

### Second: active and archived effort folders

Use the same internal effort layout but place all ongoing efforts under `work/active/` and move terminal efforts to `work/archive/`. Active includes discovery, waiting, and ready work; folder membership alone never means implementation-ready.

Move only at explicit archival, not at every stage change. Preserve a stable effort identity, keep internal links relative, update queue and inbound references, and retain a redirect where necessary. Closed includes completed or canceled work, recorded distinctly in the overview.

This provides the clearest file-explorer view, at the cost of an archive operation with reference maintenance. Prefer it if physical separation of historical work matters more than permanent paths.

### Shared requirements whichever layout wins

- An explicit implement reference wins over queue selection.
- Readiness depends on the current approved basis, ticket state, blockers, and claims, never directory name or file date alone.
- A later chat resumes the same effort when identified; a new effort gets a distinct identity even if its title resembles an old one.
- Configured remote tracker state remains authoritative; local folders hold assets and pointers rather than a second mutable status system.
- Keep decision records, spec revisions, and implementation tickets distinguishable.
- Create artifacts lazily; no forced Wayfinder map or ticket decomposition for work that does not need them.

## Proposed bounded change plan

These are candidate changes, not accepted implementation work.

1. Preserve upstream lifecycle and current glossary meanings. Distinguish finishing charting or one decision from finishing the whole map. At each valid stop, link the canonical map, name the next decision, and state how to start that next session. While a decision remains unresolved, replies continue that decision.
2. Add a brief relevance test before making an investigation a prerequisite: name the destination decision and what alternative results would change. Preserve cheap prototypes where they answer a real decision; avoid converting them into implementation milestones.
3. Make local output discoverable through one pointer in the project's existing entry documentation. Keep the tracker authoritative. Clarify the configured-tracker/local-fallback rule only if a reliability extension is accepted.
4. Define small consistency repairs for replaced decisions and local issue states if accepted. Treat these as extensions, since upstream currently leaves them incomplete.
5. Synchronize changed human docs and router relationships. Keep grill-with-docs' broader output contract unchanged unless a separate observed failure and explicit decision justify changing it. This plan records ordinary decisions because the user expressly requested a plan.
6. Add a small set of before/after behavioral cases. Reuse existing package validation for packaging; add deterministic artifact checks only after agreeing any schema. Do not build a new evaluation platform.

Candidate regression scenarios:

- Charting preserves the requested destination and creates decision questions, with research allowed but no unintended execution.
- A valid charting stop provides the map location and next invocation.
- A reply or "continue" while a ticket is unresolved resumes it rather than restarting or inventing a new workstream.
- A finished decision records resolution and the next decision without implying the map is complete.
- An application-planning prompt does not acquire a mandatory article rewrite without a justified decision dependency.
- A human-in-the-loop choice remains unresolved until the human answers.
- Local map links lead to actual files; an ownership/access error is reported as unavailable information, not absence of a repository.

The initial file scope is Wayfinder runtime/docs and the local tracker adapter where necessary, with guide-me references synchronized. Prototype, grilling, domain-modeling, research, and retro are dependencies to inspect, not blanket rewrite targets.

## Documentation decisions

Existing glossary terms such as Decision ticket, Issue, and Issue tracker fit the discussion. No new term has been settled and no glossary entry is needed yet. No ADR is warranted yet: the primary decision preserves upstream functionality, and proposed prompt repairs are reversible. Record a genuine architectural or scope tradeoff as an ADR if the interview produces one.

Keep recommendations distinct from accepted decisions. Write glossary entries only for terms actually settled; create ADRs only when the existing domain-modeling criteria are met.

## Scope boundaries

No new skill, fixed question cap, global steering expansion, automatic publishing/installing, or broad repository redesign is proposed. Related docs and router references must be synchronized with any eventual behavior change. Installation and release are later implementation concerns.
