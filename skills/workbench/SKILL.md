---
name: workbench
description: Coordinate explicitly requested or already-active durable Workbench items from persisted state. Use when the user names Workbench, supplies a Workbench ID, or asks to resume or advance existing .workbench work.
---

# Workbench

Coordinate durable work while keeping the human able to inspect and redirect it. Workbench owns identity, routing, uncertainty, lifecycle, decisions, and accepted handoffs; focused methods supply domain reasoning.

## Priorities and boundary

Apply in order: achieve the recorded outcome; minimize aggregate tokens without weakening proof; use the simplest sufficient route; finish in one session or leave an exact durable frontier. A specialist method normally runs in the current agent. Delegate only bounded independent work whose value exceeds its coordination cost. One canonical artifact may satisfy several included activities when it contains their evidence and decisions.

Start a new work item only when the user explicitly names Workbench or requests durable coordination. Complexity alone does not invoke it. Resume when the user supplies an ID or asks to continue active `.workbench` work. Audits are read-only unless mutation is requested. Never duplicate resumable work.

## Start or resume

For new work, use the compact helper; do not inspect schemas or helper implementation during an ordinary start.

1. Resolve the repository, `.workbench` store, and related resumable work before mutation.
2. Treat the user's natural description as valid intake and preserve it verbatim, including named references.
3. Inspect the current repository and every accessible reference needed to understand the request before asking questions. Separate explicit, inferred, discoverable, and decision-required information.
4. Choose the narrowest supported destination and route. Put the verbatim request in the compact input's `request` field and invoke:

   ```text
   python -B "<workbench-skill-dir>/scripts/prepare-routing.py" --repo "<repo>" --work-id "<id>" --input "<compact.json>" --output "<prepared.json>" --capture-and-start
   ```

   This captures intake and uses the validated receipt to start atomically with `route-and-start`. Do not call the underlying `capture-intake` or `route-and-start` commands.
5. Show one compact execution card: outcome, destination, lane, checkpoints, assumptions, exclusions, and granted versus withheld actions.

Compact routing input is semantic JSON: `request`, title, desired outcome, solution context, lane, business basis, intent, destination, rationale, sourced facts, assumptions, constraints, acceptance evidence, unresolved questions, recommendation, optional stage recommendations, and granted actions. Use `unresolved_questions` only for answers required before start and set `blocks_start: true`; conditional unknowns belong in phase uncertainties. If material human answers remain, consult [references/intake.md](references/intake.md), ask one compact batch, and record a superseding revision.

Choose one uppercase ID matching `WB-[A-Z0-9][A-Z0-9._-]{1,63}`; do not probe alternatives. Existing software or document-processing systems are `brownfield`; reserve `process-only` for a non-software operating process. A request to implement or fix authorizes ordinary in-scope repository mutation after gates pass, but not commit, deployment, external publication, or closure.

For existing work, read [references/state-management.md](references/state-management.md), run `resume`, and trust the validated projection over conversation memory. Read only records needed for the ready frontier.

## Operating loop

1. **Orient once.** Use the latest mutation or resume projection. Refresh only when state may have changed. Make visible: current position, evidence, decisions and rejected options, why the next action is ready, and remaining uncertainty.
2. **Act on the ready frontier.** Do agent-owned work with satisfied dependencies and authorization; continue independent work while dependent work waits.
3. **Use methods proportionally.** Activity labels identify concerns, not mandatory documents, skills, stages, or subagents. Use a method only when it creates evidence, resolves uncertainty, supports a decision, or proves a claim.
4. **Accept one meaningful phase handoff.** Review one consolidated artifact, then use `prepare-handoff.py --accept-and-advance`; its findings and uncertainties become the durable frontier.
5. **Stop at the destination.** Its gate yields authorized completion or `awaiting-acceptance`. Never close, implement, deploy, publish, or commit without the corresponding authority.

## Compact handoff contract

For ordinary artifact-backed results, invoke:

```text
python -B "<workbench-skill-dir>/scripts/prepare-handoff.py" --repo "<repo>" --work-id "<id>" --input "<phase.json>" --output "<bundle.json>" --accept-and-advance
```

Do not call `--help`, reconstruct envelopes, or call underlying accept/advance commands. Compact phase JSON contains `handoff_id`, specialist, `artifact` (`artifact_id`, repository-relative path, title, kind), findings, and uncertainties. Findings may use `sources` strings; uncertainties may use `description` or `question`. For destination proof, add `proof` with `proof_id` beginning `PRF-`, `requirement_id` beginning `REQ-`, claim, acceptance criteria, and non-vacuity check. The helper owns stage, node, lineage, fingerprints, normalization, registration, and advancement.

Review content before the helper snapshots it. Terminal acceptance requires:

```json
"review": {
  "provenance_reconciled": true,
  "measurements_bounded": true,
  "conditional_ordering": true,
  "durable_artifact_final": true
}
```

Set these only after reviewing the final source artifact. The emitted `DIAGNOSIS_PROPOSAL_REVIEW_V2` marker records completion for the Claude guard. The helper snapshots external source documents and versions reused artifact IDs. Edit the source, never an accepted snapshot. Repair a named field directly; inspect lower-level schemas only after the same field repair fails twice or the helper reports an unsupported governed record.

## Control rules

- A recommendation is not a decision. Evidence establishes facts; it does not grant authority.
- Ask one decision dimension per question. Silence and non-selection decide nothing.
- Preserve decisions, overrides, rejected alternatives, changed assumptions, blockers, and residual obligations.
- Unspecified authorization is withheld. Mutation, implementation, publication, commit, deployment, closure, and delegated decisions are separate capabilities.
- Advance only a schema-valid accepted handoff satisfying its gate. A filename or completed task is not proof.
- Classify findings as fact, measurement, hypothesis, or inference. Only sourced facts and measurements are established evidence.
- Required and achieved proof must match environment, seam, and journey. An isolated harness cannot prove a stronger application journey.
- On validation failure, leave state unchanged and report the exact record, gate, owner, and smallest repair.

## Conditional references

The bundled runtime schemas are authoritative. Read one reference only when the compact contract or field-level error is insufficient:

- Intake revision: [references/intake.md](references/intake.md)
- Route or destination: [references/routing.md](references/routing.md)
- Investigation: [references/discovery.md](references/discovery.md)
- Persisted-data design or audit: [references/data-modeling.md](references/data-modeling.md) or [references/data-model-auditing.md](references/data-model-auditing.md)
- Handoffs, proof, decisions, or gates: [references/stage-gates.md](references/stage-gates.md)
- Resume and recovery: [references/state-management.md](references/state-management.md)
