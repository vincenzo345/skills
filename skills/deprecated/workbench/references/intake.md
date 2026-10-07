# Free-form intake

Use this reference when the user starts complex work in ordinary language rather than supplying a prepared brief.

## Preserve before interpreting

Run `capture-intake` before turning the request into a route or structured plan:

```text
python -B "<workbench-skill-dir>/scripts/workbench.py" capture-intake --repo "<current-repo>" --work-id "WB-..." --request "<exact user request>" --reference "<exact named source>" --idempotency-key "<stable operation key>" [--owner "user:..."]
```

Pass the request without rewriting, summarizing, correcting spelling, or expanding shorthand. Repeat `--reference` in the order sources appeared. A captured record intentionally has no route or planning destination. Its next action belongs to the agent because inspection and synthesis normally do not require a human decision.

If capture reports a conflict, do not overwrite the prior request or invent a new ID solely to bypass it. Resume the existing work or explain why the two requests need separate identities.

## Inspect before asking

Build a four-part intake inventory:

- **Explicit:** behavior, problems, constraints, examples, locations, and intent stated by the user.
- **Inferred:** plausible interpretations that remain labeled as assumptions.
- **Discoverable:** repository structure, current behavior, data flow, tests, standards, and readable reference behavior the agent can inspect.
- **Decision-required:** product, business, risk, or authorization choices that evidence cannot settle.

Inspect discoverable items before questioning the user. Start with the named paths and the smallest relevant code surface, then trace the affected behavior, tests, data boundaries, and applicable local instructions. Do not perform repository mutations during intake inspection.

Ask only when an unresolved answer would materially change at least one of these:

- observable behavior or acceptance evidence;
- affected users, records, systems, or compatibility promises;
- destructive, privacy, security, financial, or operational risk;
- route, planning destination, or whether the work is a prototype versus production change;
- authorization for an action now at the frontier.

Ask the smallest coherent batch, usually one to three questions. Include what was inspected and why the remaining answer is not discoverable. Do not ask the user to select internal identifiers when Workbench can recommend them in plain language.

## Synthesize the execution contract

Before routing, show a compact draft with:

1. the problem and desired outcome;
2. the observable behavior and acceptance evidence;
3. affected surfaces and constraints found during inspection;
4. explicit facts versus labeled assumptions;
5. business basis, solution context, engagement intent, planning destination, execution lane, and why;
6. what the request authorizes now and what remains outside that boundary;
7. remaining decisions or blockers.

The draft need not repeat the raw request because `intake.json` preserves it. It must be understandable to the user without internal jargon. If the route is clear and no material user choice remains, state the recommendation and proceed under the explicit request. If a consequential choice remains, pause only the dependent work.

Write those fields to a temporary JSON routing-input file using the field contract in [schemas/workbench-routing-receipt.schema.json](schemas/workbench-routing-receipt.schema.json), omitting the runtime-owned identity, intake binding, compiled plan, owner, timestamp, idempotency, and fingerprint fields. The preferred path compiles and starts the work atomically:

```json
{
  "title": "Short human-readable title",
  "desired_outcome": "Observable outcome, not the artifact used to plan it.",
  "business_basis": "hypothesis | operating-process | supplied-requirements | technical-only",
  "solution_context": "greenfield | brownfield | process-only | undetermined",
  "engagement_intent": "explore | plan | implement | release",
  "planning_destination": "one lifecycle destination ID",
  "execution_lane": "fast | full",
  "planning_posture": "collaborative | delegated",
  "runtime_route": "one matching legacy route ID or null",
  "rationale": "Why this profile fits the evidence.",
  "evidence_references": ["path, URL, or captured-intake"],
  "facts": [{"statement": "Explicit or inspected fact.", "source_references": ["source"]}],
  "constraints": ["Known constraint."],
  "acceptance_evidence": ["Observable evidence that would support completion."],
  "assumptions": ["Labeled assumption and its practical boundary."],
  "unresolved_questions": [{"question": "Material question?", "why_material": "What it changes.", "owner": {"actor_id": "human:...", "kind": "human"}}],
  "phase_questions": [{"question": "Downstream choice or evidence question?", "why_material": "What later artifact it changes.", "owner": {"actor_id": "human:... | agent:...", "kind": "human | agent"}}],
  "stage_recommendations": [{"stage_id": "canonical-stage-id", "applicability": "applicable | not-applicable | undetermined", "reason": "Why.", "evidence_references": ["source"]}],
  "authorization_boundary": {"granted_actions": []},
  "recommendation": {"choice": "Bounded recommendation.", "rationale": "Why.", "assumptions": [], "tradeoffs": ["What this makes harder."], "confidence": "low | medium | high"}
}
```

```text
python -B "<workbench-skill-dir>/scripts/workbench.py" route-and-start --repo "<current-repo>" --work-id "WB-..." --routing-input "<routing-input.json>" --idempotency-key "..." [--owner "user:..."]
```

`route-and-start` fills every unlisted capability action into `withheld_actions`, rejects overlap, compiles applicable activities into no more than one checkpoint per active phase, truncates the plan at the selected destination, then writes routing and lifecycle state in one transaction. A `null` `runtime_route` is valid for profile-compiled work, including greenfield; do not invent a brownfield route merely to proceed. Unresolved material questions or an undetermined activity blocks start.

If the work must pause with material questions, use `finalize-intake` so those questions are durable. When the user answers, retain the exact answer source, remove only the questions now resolved, add `revision_reason` and matching `resolved_questions`, and submit the complete updated profile with `revise-routing --expected-routing-revision N`. Continue under the same work ID; do not ask to create a successor item. Then use `start --from-routing` with only the work ID, idempotency key, and optional owner. The start event cites and binds the exact `intake.json` and latest routing-revision bytes. A later integrity mismatch is a blocker, not permission to reconstruct the request from chat.

## Example contract

For a request such as “Workbench, I want to implement a new feature. There is an issue with manual validation. Make it like the test-validation HTML at a named path, with column separators and a row selector, and append data from multiple pages into one table”:

- capture the sentence and named path first;
- treat this as a candidate brownfield feature aimed at a locally verified implementation;
- inspect the reference HTML, current manual-validation implementation, pagination/data-loading path, existing tests, and repository instructions;
- derive selector appearance and table behavior from accessible evidence instead of asking the user to restate them;
- keep “manual validation” as the feature's domain term; do not confuse it with Workbench's process-validation stage;
- ask only about behavior that remains materially ambiguous after inspection, such as whether selection persists across loaded pages or what ends pagination;
- state that local repository changes may be in scope when the request is directed at the agent, while commit, deployment, and external mutation remain unauthorized unless separately requested.

Success is not a perfectly filled template. Success is a faithful raw record, an evidence-grounded execution contract the user can understand, and no unanswered material decision hidden behind agent confidence.
