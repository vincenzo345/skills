---
name: feature-planner
description: Create or review repository-grounded implementation plans for features. Use when a request needs acceptance criteria, affected interfaces, data or schema changes, rollout considerations, or an implementation-ready plan before coding.
---

# Feature Planner

Produce a plan another engineer or coding agent can execute without rediscovering material behavior or making hidden product decisions.

## Plan from evidence

1. Resolve the active repository and inspect the smallest relevant source, tests, schemas, configuration, and local instructions. Keep planning inspection read-only.
2. Establish the desired behavior, users, success evidence, scope, exclusions, constraints, and important tradeoffs. Ask only about choices that materially change the plan and cannot be discovered; record safe defaults as assumptions.
3. Trace the change through affected components, public interfaces, data flow, state ownership, persistence, failure paths, accessibility, compatibility, migration, rollout, observability, and operations where applicable.
4. Name concrete files, modules, or seams when that prevents ambiguity. Preserve existing conventions and separate established facts from inferences.
5. Review the draft against the readiness gate. Repair every failed item, then make one adversarial pass for hidden choices and missing proof. Finish only when no material implementation decision remains unresolved.

## Readiness gate

A ready plan has:

- an explicit outcome and observable success criteria;
- clear in-scope and out-of-scope boundaries;
- concrete behavior and affected subsystem changes;
- interface, type, configuration, schema, and persistence changes, or an explicit no-change disposition;
- data flow, ownership, edge cases, and failure handling where relevant;
- user-experience and accessibility effects where relevant;
- proportional unit, integration, end-to-end, and manual verification;
- compatibility, migration, rollout, monitoring, and operational treatment where relevant; and
- labeled assumptions with no unresolved decision disguised as an implementation detail.

## Handoff

Return one concise implementation-ready Markdown plan containing:

- title and outcome;
- implementation changes grouped by behavior or subsystem;
- interface and data implications;
- verification scenarios;
- rollout or migration obligations; and
- assumptions, exclusions, and genuine blockers.

When Workbench owns the effort, return this plan as evidence for its current phase handoff. Do not create competing lifecycle state or treat planning completion as implementation authorization.
