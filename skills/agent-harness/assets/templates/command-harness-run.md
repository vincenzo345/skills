---
description: Run the {{PROJECT_NAME}} Planner->Generator->Evaluator loop from the current sprint until it stalls or finishes.
---

You are the **orchestrator** for the {{PROJECT_NAME}} harness. Follow `CLAUDE.md` exactly. Do NOT
write project code yourself — dispatch to the subagents.

Arguments (optional): `$ARGUMENTS` may name a sprint to start from or "replan".

Steps:
1. Read `.harness/progress.json` and `.harness/plan.json`. If `plan.json` is missing or
   `$ARGUMENTS` == "replan", dispatch the **planner** subagent, then stop and show the plan for
   confirmation.
2. Determine the current sprint (first not `passed`, or the one named in `$ARGUMENTS`).
3. **Contract negotiation:** dispatch **generator** ("propose a contract for sprint N"), then
   **evaluator** ("review the proposed contract"). Repeat until `.harness/contract_review.json` has
   `agreed: true` (max 4 rounds — if it won't converge, stop and surface the disagreement).
4. Tag the sprint start: `git tag sprint-N-start`.
5. **Build/eval loop** (max 8 rounds):
   - Dispatch **generator** ("build sprint N against the agreed contract").
   - Dispatch **evaluator** ("evaluate the current build").
   - Read `.harness/verdict.json`. On `pass`: set the sprint `passed` in `progress.json`, commit, go
     to step 2 for the next sprint. On `revise`: loop. On `restart`: `git reset --hard sprint-N-start`,
     then loop.
6. Stop when all sprints are `passed`, when a loop hits its round cap, or when a subagent reports a
   blocker. Summarize what passed, what stalled, and the last verdict. Do not silently spin.

Keep the main context lean: rely on the subagents' separate context windows and the files on disk.
Append a journal line at each transition.
