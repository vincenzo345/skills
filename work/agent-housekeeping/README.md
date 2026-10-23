---
schema: 1
kind: effort
id: work/agent-housekeeping
state: active
stage: implementation
current_spec:
  ref: work/agent-housekeeping/spec.md
  revision: 1
current_map: null
next_action: Implement the approved chain on feat/agent-housekeeping; retain a draft
  PR for human review and do not merge main.
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
