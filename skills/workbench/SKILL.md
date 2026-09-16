---
name: workbench
description: Coordinate explicitly requested or already-active durable Workbench items from persisted state. Use when the user names Workbench, supplies a Workbench ID, or asks to resume or advance existing .workbench work.
---

# Workbench

Coordinate durable work while keeping the human able to see and redirect the path. Workbench owns work identity, routing, uncertainty, lifecycle state, decisions, and accepted handoffs. Focused methods supply domain reasoning.

## Operating priorities

Apply these in order:

1. **Outcome** — Achieve the recorded desired outcome and its completion condition, or establish the exact blocker.
2. **Token economy** — Minimize aggregate token use while reliably achieving and verifying it. Reuse evidence and records; load, inspect, delegate, and explain only what the active branch needs.
3. **Proportionality** — Choose the simplest route that fully addresses uncertainty, risk, and proof. Add methods, artifacts, agents, and reviews only when their value exceeds their coordination cost.
4. **Session closure** — Aim to finish in one session. If that is not responsible within a 150,000–250,000-token per-agent planning envelope, accept a handoff preserving state, evidence, decisions, uncertainty, and the exact ready frontier.

Higher priorities override lower ones. Economy and session sizing never weaken required safety, authorization, or proof.

A specialist method normally runs in the current agent. Delegate bounded independent work when parallelism, independent judgment, or per-agent context containment outweighs prompt, rereading, and synthesis cost. One canonical artifact may satisfy several included activities when it contains their required evidence and decisions.

## Invocation boundary

Start a new work item only when the user explicitly names Workbench or requests durable coordination. Complexity alone does not invoke it; use the ordinary bounded workflow otherwise.

Resume when the user names a work ID or asks to continue, inspect, route, or advance active `.workbench` work. Audits are read-only unless mutation is requested. Never duplicate resumable work.

## Start or resume

For new work, read [references/intake.md](references/intake.md) and [references/routing.md](references/routing.md), then:

1. Before `capture-intake`, resolve the repository, intended `.workbench` store, and related resumable work; ambiguity blocks mutation.
2. Treat the user's natural description as valid intake. Preserve it exactly with `capture-intake`, including every named reference.
3. Inspect the current repository and every accessible reference needed to understand the request before asking questions. Classify information as explicit, inferred, discoverable, or decision-required.
4. Synthesize the narrowest destination and proportional route supported by the evidence. If no material question remains, persist and start atomically with `route-and-start`.
5. If material human answers remain, preserve them with `finalize-intake`, ask one compact batch, then record the answers and complete updated synthesis with `revise-routing`. Revisions supersede rather than overwrite. Start the latest ready receipt with `start --from-routing`; `start --from-intake` is legacy compatibility.
6. Show one compact execution card: outcome, destination, lane, phase checkpoints, assumptions, exclusions, and granted versus withheld actions.

An explicit request to implement, fix, or change the current repository authorizes the ordinary in-scope repository mutation and implementation needed for that request once its gates are satisfied. It does not authorize commit, deployment, tracker publication, external-system mutation, or closure.

For existing work, read [references/state-management.md](references/state-management.md), run `resume`, and use the returned projection as current. Read only the records required for the selected frontier item; conversation memory and parallel planning documents cannot override validated state.

## Operating loop

1. **Orient once.** Use the latest mutation or `resume` projection. Refresh with `status` only when state may have changed; use `next` only for a deliberately narrower frontier view. Make five answers visible: where we are, what we learned, what was decided and rejected, why the proposed action is next, and what remains uncertain.
2. **Act on the ready frontier.** Execute agent-owned work whose dependencies, scope, and authorization are satisfied. Pause dependent work for a human decision or external blocker while continuing independent ready work.
3. **Apply only useful methods.** An activity label identifies a concern, not a mandatory stage, document, skill, or subagent. Workbench coordinates every independently triggered skill; it never makes one optional. Otherwise use a method only when it creates evidence, resolves uncertainty, supports a decision, or proves a claim.
4. **Accept one meaningful phase handoff.** Validate and register the consolidated bundle with `accept-handoff`; its findings, uncertainties, and decisions become the durable reasoning frontier. Then use `advance-stage --accepted-handoff` so the runtime derives mechanical gate evidence. Preserve a material follow-up as a versioned artifact rather than leaving it only in chat.
5. **Stop at the selected destination.** Passing its gate produces either authorized completion or `awaiting-acceptance`; do not make closure ceremony the headline. Report separate dispositions for feature behavior, focused verification, integration journey, repository health, user acceptance, deployment readiness, deployed behavior, and business outcome only when applicable.

## Control rules

- A recommendation is not a decision. Evidence can establish facts but cannot authorize a consequential choice.
- Ask one decision dimension per question. A response decides only what it states; silence and non-selection decide nothing else.
- Preserve user decisions, overrides, rejected alternatives, changed assumptions, blockers, and residual obligations. Do not relitigate a settled choice unless its recorded premise changed.
- Treat unspecified authorization as withheld. Repository mutation, implementation, tracker publication, commit, deployment, closure, and delegated decisions are separate capabilities.
- Before advancing, require a schema-valid accepted handoff whose outputs satisfy the registered gate. A filename or completed specialist task is not proof.
- Required and achieved proof must name the same environment, seam, and journey. An isolated component harness cannot pass an authenticated application-flow requirement; unavailable prerequisites remain blocked.
- If validation fails, leave state unchanged and report the exact record, gate, owner, and smallest repair.

## Runtime and conditional detail

Resolve `<workbench-skill-dir>` to the installed directory containing this file and run its bundled CLI against the user's repository:

```text
python -B "<workbench-skill-dir>/scripts/workbench.py" <command> --repo "<current-repo>" ...
```

Read one relevant reference when its branch fires:

- New request capture and clarification: [references/intake.md](references/intake.md)
- Route, destination, lane, uncertainty, or specialist selection: [references/routing.md](references/routing.md)
- Focused investigation or uncertainty escalation: [references/discovery.md](references/discovery.md)
- Database-backed application or possible persisted-data impact: [references/data-modeling.md](references/data-modeling.md)
- Review or audit of an existing persisted model: [references/data-model-auditing.md](references/data-model-auditing.md)
- Handoff, decision, proof, authorization, or checkpoint movement: [references/stage-gates.md](references/stage-gates.md)
- Commands, resumption, recovery, or persisted files: [references/state-management.md](references/state-management.md)

The bundled lifecycle schema is the source of phase, activity, legacy-route, destination, status, and gate identifiers. Let the runtime validate schemas; do not load or reproduce the full schema catalog unless diagnosing a validation failure.
