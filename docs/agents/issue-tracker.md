# Issue tracker: Local Markdown

This repository uses local Markdown in stable `work/<effort>/` folders. This is the user's explicit repository convention and takes precedence over skill defaults that publish to `.scratch/<feature>/issues/` or a remote tracker. The Git remote is for code hosting; it does not select the issue tracker.

## Locations and authority

All paths below are repository-relative:

| Record | Location |
| --- | --- |
| Ordered effort queue | `work/queue.md` |
| Effort overview and current artifact pointers | `work/<effort>/README.md` |
| Current specification | `work/<effort>/spec.md` |
| Implementation issues | `work/<effort>/tickets/<NN>-<slug>.md` |
| Wayfinder map | `work/<effort>/map.md` |
| Wayfinder decision tickets | `work/<effort>/decisions/<NN>-<slug>.md` |
| Ordinary discovery findings | `work/<effort>/discovery.md` |
| Supporting research and retained revisions | `work/<effort>/research/` and `work/<effort>/history/` |

Create only needed artifacts. Resume an identified effort at its existing path; similar titles alone do not establish identity. Keep completed effort folders stable. The queue owns priority, the overview owns effort context/current pointers, and individual issues own their state and dependencies.

## Current effort

For Wayfinder workflow reliability, use the [existing overview](../../work/wayfinder-reliability/README.md), [current spec](../../work/wayfinder-reliability/spec.md), and [published implementation issues](../../work/wayfinder-reliability/issue-plan.md#published-issues).

Its implementation issues are in `work/wayfinder-reliability/tickets/`. Any Wayfinder decision tickets belong in `work/wayfinder-reliability/decisions/`, with the map at `work/wayfinder-reliability/map.md`. Create those planning artifacts only if needed; none is required to use the published implementation issues.

## Publish, fetch, and update

- When a skill says to publish a spec, use the identified effort's current spec location. Preserve materially different earlier revisions according to the [shared contract design](../../work/wayfinder-reliability/design.md).
- When to-tickets publishes an approved breakdown, write one implementation issue per file in `tickets/`, with its specification basis and explicit blocking references. Keep existing IDs and numbering stable.
- When fetching a record, resolve its explicit path first. A bare number needs effort and record-kind context; ask if it could refer to both an implementation issue and a decision ticket.
- The new implementation issues use YAML front matter for kind, identity, lifecycle, readiness, spec basis, order, and dependencies. Read and update those fields rather than adding a conflicting `Status:` line. Use the unchanged [triage label vocabulary](triage-labels.md) for readiness.
- Existing spec/overview formats remain valid explicit inputs. Read their current fields as written; this setup does not convert them. For missing or ambiguous eligibility information, report the gap instead of guessing.
- Append comments and conversation notes under `## Comments` when needed. Keep issue state in the issue and link to it from overviews.

Read the shared contract design for lifecycle, revisions, dependency satisfaction, selection precedence, and claim semantics. It defines the intended shared behavior; this configuration supplies locations and instructions, not an executable selector or claim coordinator. Explicit inputs take precedence over queue order, but readiness, blockers, and ownership still require validation. Queue membership alone does not authorize implementation.

## Wayfinding operations

Use the separate map and `decisions/` paths above for Wayfinder's map, child records, and frontier queries. Decision tickets hold questions and their authoritative answers; they are never implementation issues and never receive implementation readiness merely because they are unblocked.

For new typed planning records, use the map/decision envelopes in the shared contract design: decision type, lifecycle, blocking references, and order. Resolve local decision blockers through their recorded answers, preserve superseded answers, and append a named context pointer to the map on resolution. Keep upstream charting, human-decision, and session boundaries intact.

Record ownership before working on a decision. An existing legacy `claimed` status remains a claim to respect. Typed-record claims follow the shared contract; a status edit alone does not establish atomic exclusivity across sessions. If the required shared claim mechanism is unavailable, report that limitation rather than asserting concurrent ownership.

## Existing work and adoption

Historical `.scratch` records and explicitly referenced legacy records remain at their existing locations with their original identities and formats. Fetch them in place when requested. Do not move, renumber, rewrite, or copy them into a second current record as part of setup.

This configuration does not migrate history, change skill defaults globally, install tooling, or authorize implementation. Follow the current effort's recorded authorization boundary. Any later migration is a separate opt-in action.
