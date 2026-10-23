---
schema: 1
kind: effort
id: work/agent-housekeeping
state: completed
stage: implementation
current_spec:
  ref: work/agent-housekeeping/spec.md
  revision: 1
current_map: null
next_action: 'Review draft PR #7; no merge or auto-merge authorized. See validation.md
  for measured overhead and two policy-blocked empty fixture directories.'
---

# Agent housekeeping and resource cleanup

## Original request

Research skills and repositories addressing Codex agents leaving unnecessary test scripts and Docker resources, then interview the user to plan a cleanup component or skill.

## Desired outcome

An evidence-backed agreed design for preventing unnecessary artifacts and cleaning up owned temporary resources without deleting durable work or other sessions resources.

[Discovery](discovery.md) holds ordinary requirements and open questions.

[Research](research/cleanup-patterns.md) compares existing skills and resource lifecycle mechanisms.

[Current specification](spec.md) is revision 1; the behavioral testing seam is confirmed.

[Approved issue breakdown](issue-plan.md) links the three published implementation issues.

## Completion evidence

Implemented specification revision1 and published draft PR https://github.com/vincenzo345/skills/pull/7 for human review. Three issues accepted in dependency order; standards/spec review complete and relevant checks passed. Main and unrelated work preserved. No new helper, hook or cleanup skill. See validation.md for measurements and the explicitly unresolved empty fixture-directory cleanup limitation. Human review and any later merge are separate; PR must remain draft for this delivery.
