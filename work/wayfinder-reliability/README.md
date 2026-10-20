# Wayfinder workflow reliability

## Purpose

Make planning and implementation work easy to find, resume, and select across conversations while preserving upstream Wayfinder behavior.

Original request: improve the skills repository after an application-planning session drifted into article writing. The request expanded to shared, request-named folders for planning, specs, and implementation issues, with current work clearly distinguished from history.

## Current state

- Stage: implementation breakdown approved and issues published.
- Current specification: [Reliable planning and implementation workspaces](spec.md), revision 2, `ready-for-agent`.
- Contract design: [Shared work-record contract](design.md), including metadata, lifecycle, revisions, readiness, dependencies, claims, selection, and handoff walkthroughs.
- Implementation issues: [Seven published slices](issue-plan.md#published-issues), each with its own authoritative record.
- Approved breakdown: [Seven vertical implementation slices](issue-plan.md), including dependencies, acceptance criteria, and approval evidence.
- Next action: when implementation is requested, begin with [Local issue handoff](tickets/01-local-issue-handoff.md) and confirm the integration branch before delivery.
- Implementation authorization: this session covers planning/specification only.

The queue lists this effort for navigation and priority. It does not authorize bare implement to start, and no new queue-selection behavior is installed yet.

## Decisions and evidence

- [Stable effort workspace decision](../../docs/adr/0001-stable-effort-workspaces.md).
- [Discovery, upstream comparison, and alternatives](../../docs/plans/wayfinder-reliability.md).
- [Shared domain language](../../GLOSSARY.md).
- [Previous specification, revision 1](history/spec-r1.md).

The design preserves the settled workspace and Wayfinder decisions. Its technical choices are recorded as design outcomes rather than earlier user approvals. No consequential product-policy question remains open for issue planning. Implementation must validate local claim coordination, remote capabilities, migration safety, and the intended integration branch/CI coverage. Scenario walkthroughs are recorded; executable checks and behavioral replays remain implementation work.

The existing discovery document remains at its original location to preserve references. New artifacts for this effort belong here unless they are project-wide domain records.
