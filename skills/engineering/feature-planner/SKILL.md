---
name: feature-planner
description: Implementation-focused feature planning skill for creating, evaluating, and iterating repo-aware plans before coding. Use when Codex needs to plan a new feature, feature design, implementation spec, acceptance criteria, data/API/schema changes, rollout or migration strategy, or review and revise a proposed feature plan until it is implementation-ready.
---

# Feature Planner

## Workflow

1. Ground in the available artifacts.
   - Identify the active project root, app, or module before deep searches. When a workspace contains backups, mirrors, generated folders, or multiple app copies, inspect the top-level layout and choose the most relevant candidate first.
   - Use targeted searches in likely source, test, schema, and config paths. Start with high-signal feature terms, cap or sample large result sets, and narrow noisy searches by path, glob, or exact phrase before reading deeply. Avoid whole-worktree sweeps through backups, dependency caches, build artifacts, or large generated outputs unless they are clearly necessary.
   - Inspect files, configs, schemas, types, docs, tests, and existing feature patterns before asking questions when local context exists.
   - If the request is conceptual or no local artifacts are available, state that assumption and plan from the provided context.
   - Keep discovery non-mutating while planning.

2. Clarify intent.
   - Establish the goal, users or audience, success criteria, in scope, out of scope, constraints, and important tradeoffs.
   - Ask targeted questions only when the answer materially changes the plan and cannot be discovered from the environment.
   - If a low-risk default is reasonable, proceed with it and list it as an assumption.

3. Draft the implementation approach.
   - Define the behavior changes, affected subsystems, public APIs, types, schemas, configs, data flow, state ownership, edge cases, failure modes, UX/accessibility impacts, and rollout or migration concerns.
   - Follow existing repo conventions and name specific files, modules, or symbols only when that prevents ambiguity.
   - Make the plan decision-complete for another engineer or agent. Do not leave unresolved implementation choices.

4. Evaluate and iterate.
   - Evaluate the draft against the Plan Evaluation Gate.
   - Revise every failed area, then evaluate again.
   - After the gate passes, run one adversarial review pass for hidden assumptions, missing implementation details, edge cases, testing gaps, UX/accessibility issues, data/API risks, and rollout risks.
   - If the adversarial pass finds a material issue, revise and repeat the gate plus adversarial pass.
   - Finalize only after the gate passes and the adversarial pass finds no material issue worth changing.

## Plan Evaluation Gate

Fail the plan unless every item is satisfied:

- Goal and success criteria are explicit.
- Users, audience, and user-facing behavior are clear when relevant.
- In-scope and out-of-scope boundaries are clear enough to prevent extra work.
- Implementation approach describes concrete behavior changes and affected subsystems.
- Public API, schema, type, config, or interface changes are stated, or explicitly marked as none.
- Data flow and state ownership are clear when data moves or persists.
- Edge cases and failure modes are covered.
- UX and accessibility impacts are covered for user-facing changes.
- Test plan covers the right level of unit, integration, end-to-end, or manual checks for the risk.
- Migration, compatibility, rollout, monitoring, or operational risks are covered when relevant, or explicitly marked as none.
- Assumptions and defaults are explicit.
- No unresolved decisions remain.

## Question Rules

- Ask after discovery unless the prompt itself has contradictory goals or missing product intent.
- Ask only questions that materially change the plan.
- Prefer one to three concise questions. Use any available user-input tool when it is present; otherwise ask directly.
- If user input is unavailable and a safe default exists, proceed with the default and record it.
- If no safe default exists, stop before the final plan and ask the blocking question.

## Final Plan Format

When the plan is ready, output one complete `<proposed_plan>` block. Include:

- A clear title.
- `Summary` with the goal and intended outcome.
- `Implementation Changes` with behavior, interfaces, data flow, and rollout notes.
- `Test Plan` with concrete verification scenarios.
- `Assumptions` with defaults and explicitly deferred items, if any.

Keep the plan concise but implementation-ready. Do not expose internal rubric notes unless the user asks for a rating, critique, or iteration history.
