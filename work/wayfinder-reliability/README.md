---
schema: 1
kind: effort
id: work/wayfinder-reliability
state: active
stage: implementation
current_spec:
  ref: work/wayfinder-reliability/spec.md
  revision: 2
current_map: null
next_action: Finish legacy and remote validation, review integrated changes, and install.
---

# Wayfinder workflow reliability

## Purpose

Make planning and implementation work easy to find, resume, and select across conversations while preserving upstream Wayfinder behavior.

Original request: improve the skills repository after an application-planning session drifted into article writing. The request expanded to shared, request-named folders for planning, specs, and implementation issues, with current work clearly distinguished from history.

## Current state

- Stage: implementation in progress on `integration/wayfinder-reliability`.
- Current specification: [Reliable planning and implementation workspaces](spec.md), revision 2, `ready-for-agent`.
- Contract design: [Shared work-record contract](design.md), including metadata, lifecycle, revisions, readiness, dependencies, claims, selection, and handoff walkthroughs.
- Implementation issues: [Seven published slices](issue-plan.md#published-issues), each with its own authoritative record.
- Approved breakdown: [Seven vertical implementation slices](issue-plan.md), including dependencies, acceptance criteria, and approval evidence.
- Next action: finish legacy and remote validation, review the integrated changes, and follow the Windows installation procedure.
- Implementation authorization: the user explicitly invoked implement-spec for the approved tickets, integrated validation/review, and Windows installation. Earlier planning-only statements record the previous session boundary.

The queue lists this effort for navigation and priority. The current implement-spec invocation supplies implementation authorization; the queue itself does not. Implementation and replay evidence is recorded in [validation](validation.md).

## Decisions and evidence

- [Stable effort workspace decision](../../docs/adr/0001-stable-effort-workspaces.md).
- [Discovery, upstream comparison, and alternatives](../../docs/plans/wayfinder-reliability.md).
- [Shared domain language](../../GLOSSARY.md).
- [Previous specification, revision 1](history/spec-r1.md).

The design preserves the settled workspace and Wayfinder decisions. Its technical choices are recorded as design outcomes rather than earlier user approvals. No consequential product-policy question remains open for issue planning. Implementation must validate local claim coordination, remote capabilities, migration safety, and the intended integration branch/CI coverage. Scenario walkthroughs are recorded; executable checks and behavioral replays remain implementation work.

The existing discovery document remains at its original location to preserve references. New artifacts for this effort belong here unless they are project-wide domain records.
