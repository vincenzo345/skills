---
name: workbench
description: Coordinate explicitly requested or already-active durable Workbench items from persisted state. Use when the user names Workbench, supplies a Workbench ID, or asks to resume or advance existing .workbench work.
---

# Workbench

Coordinate durable work while keeping the human able to inspect and redirect it. Workbench owns identity, routing, uncertainty, lifecycle, decisions, and accepted handoffs; focused methods supply domain reasoning.

## Priorities and boundary

Apply in order: achieve the recorded outcome; minimize aggregate tokens without weakening proof; use the simplest sufficient route; finish in one session or leave an exact durable frontier. A specialist method normally runs in the current agent. Delegate only bounded independent work whose value exceeds its coordination cost. One canonical artifact may satisfy several included activities when it contains their evidence and decisions.

Start a new work item only when the user explicitly names Workbench or requests durable coordination. Complexity alone does not invoke it. Resume when the user supplies an ID or asks to continue active `.workbench` work. Audits are read-only unless mutation is requested. Never duplicate resumable work by default. If the user explicitly says to ignore, replace, or start separately from existing work, create a new item without relitigating that choice; prior artifacts remain evidence, not the active lifecycle.

## Start or resume

For new work, use the compact helper; do not inspect schemas or helper implementation during an ordinary start.

For a reported slowdown or performance regression, read [references/performance-investigation.md](references/performance-investigation.md) before repository inspection and follow its evidence bounds and claim vocabulary. This bundled method is authoritative for the investigation; do not require a harness-provided diagnosis skill.

Create compact helper inputs inside the target repository (prefer `.workbench/tmp/` or `.wb-tmp/`), never in an operating-system temp directory or another checkout. In `authorization_boundary.granted_actions`, use only governed capabilities: `decision-delegation`, `repository-mutation`, `tracker-publication`, `implementation`, `commit`, `deployment`, and `closure`. Ordinary source reads and Workbench artifact recording are execution-boundary details, not granted capabilities. Build the execution card from the prepared routing receipt so its granted and withheld actions match persisted state.

1. Resolve the repository, `.workbench` store, and related resumable work before mutation.
2. Treat the user's natural description as valid intake and preserve it verbatim, including named references.
3. Inspect the current repository and every accessible reference needed to understand the request before asking questions. Separate explicit, inferred, discoverable, and decision-required information.
4. Select and expose `planning_posture`: use `collaborative` for “help me plan/work through/figure out,” fuzzy targets, or unresolved material choices; use `delegated` only for an explicit request to draft, propose, recommend, or choose within recorded bounds. When cues conflict, choose collaborative.
5. Route intent faithfully: explore/options normally stop at `proposal`; planning a buildable system normally stops at `implementation-plan`; specification-only stops at `specification`; build/fix/implement targets `locally-verified-implementation`; release requires an explicit release destination.
6. Choose the narrowest supported destination and route. Put the verbatim request in the compact input's `request` field and invoke:

   ```text
   python -B "<workbench-skill-dir>/scripts/prepare-routing.py" --repo "<repo>" --work-id "<id>" --input "<compact.json>" --output "<prepared.json>" --capture-and-start
   ```

   This captures intake and uses the validated receipt to start atomically with `route-and-start`. Do not call the underlying `capture-intake` or `route-and-start` commands.
7. Show one compact execution card: environment, posture, outcome, intent, destination, lane, checkpoints, assumptions, exclusions, and granted versus withheld actions. For a performance investigation, begin the card with `Environment:` before words such as ranking or recommendation.

Compact routing input is semantic JSON: `request`, title, desired outcome, solution context, lane, business basis, intent, destination, `planning_posture`, rationale, sourced facts, assumptions, constraints, acceptance evidence, unresolved questions, recommendation, optional stage recommendations, and granted actions. The helper canonicalizes these documented aliases and rejects unknown or conflicting semantic fields. Use `unresolved_questions` with `blocks_start: true` only when routing cannot start. Nonblocking questions become durable phase decision/evidence nodes, never assumptions. If material human answers remain, consult [references/intake.md](references/intake.md), ask one compact batch, and record a superseding revision.

Choose one uppercase ID matching `WB-[A-Z0-9][A-Z0-9._-]{1,63}`; do not probe alternatives. Existing software or document-processing systems are `brownfield`; reserve `process-only` for a non-software operating process. A request to implement or fix authorizes ordinary in-scope repository mutation after gates pass, but not commit, deployment, external publication, or closure.

Use the fast lane only when behavior, blast radius, acceptance oracle, and proof are already clear; no material product, domain, architecture, scope, risk, migration, external-coordination, or multi-ticket choice remains; and the work fits one session. Otherwise use the full route and the collaborative-delivery method.

For existing work, read [references/state-management.md](references/state-management.md), run `resume`, and trust the validated projection over conversation memory. Read only records needed for the ready frontier.

## Operating loop

1. **Orient once.** Use the latest mutation or resume projection. Refresh only when state may have changed. Make visible: current position, evidence, decisions and rejected options, why the next action is ready, and remaining uncertainty.
2. **Establish shared understanding.** For collaborative or unsettled full routes, read [references/collaborative-delivery.md](references/collaborative-delivery.md). Investigate facts, surface the material decision frontier, gather proportional evidence, and obtain confirmation of a ready shared-understanding artifact before specification.
3. **Act on the ready frontier.** Do agent-owned work with satisfied dependencies and authorization; continue independent work while dependent work waits.
4. **Use methods proportionally.** Activity labels identify concerns, not mandatory documents, skills, stages, or subagents. Research, domain models, mockups, prototypes, POCs, and measurements are evidence tasks for named uncertainties, not decorations.
5. **Accept meaningful handoffs.** Use `--accept-and-advance` for a completed phase. During implementation, use `--accept-only` for ticket-scoped results so one ticket cannot complete the whole stage.
6. **Execute approved tickets.** Claim dependency-ready deliverables atomically, complete them with review and proof, and continue through the recomputed frontier until every required ticket is terminal.
7. **Stop at the destination.** Its gate yields authorized completion or `awaiting-acceptance`. Never close, implement, deploy, publish, or commit without the corresponding authority.

## Compact handoff contract

For ordinary artifact-backed results, invoke:

```text
python -B "<workbench-skill-dir>/scripts/prepare-handoff.py" --repo "<repo>" --work-id "<id>" --input "<phase.json>" --output "<bundle.json>" --accept-and-advance
```

For an exact two-stage investigation ending in a proposal, replace `--accept-and-advance` with `--accept-to-proposal`. Supply only the final reviewed proposal JSON; do not serialize a duplicate framing result.

Do not call `--help`, reconstruct envelopes, or call underlying accept/advance commands. Compact phase JSON contains `handoff_id`, specialist, `artifact` or `artifacts` (`artifact_id`, repository-relative path, title, kind, readiness), findings, uncertainties, decisions, optional node additions/dependencies, and node updates. Findings may use `statement`, `summary`, `claim`, or `finding`; classification may use `basis`, `classification`, or `finding_type`; sources may be strings. Decisions preserve authority, options, confirmation, provenance, and consequences. For destination or ticket proof, add `proof` with `proof_id` beginning `PRF-`, `requirement_id` beginning `REQ-`, claim, acceptance criteria, and non-vacuity check. The helper owns stage, lineage, fingerprints, normalization, and registration.

Use `--accept-only` for intermediate ticket handoffs. Before implementation, invoke `workbench.py claim-node --work-id <id> --node-id <ticket> --expected-revision <n> --idempotency-key <key>`. Dependency-blocked tickets do not appear in `frontier.agent_ready`.

The compact phase JSON is an index, not a second proposal. Record at most six decision-relevant findings and consolidate uncertainties that share the same proof action. Keep option detail in the artifact; do not duplicate every option's prose in the handoff or final response.

Review content before the helper snapshots it. Terminal acceptance requires:

```json
"review": {
  "provenance_reconciled": true,
  "measurements_bounded": true,
  "conditional_ordering": true,
  "durable_artifact_final": true
}
```

Set these only after completing the global skeptical review of the final source artifact; they attest that review, not a later check. For performance work, explicitly check milestone scope, prerequisite timing, measurement resolution, and every exclusive or causal label before setting them. The emitted `DIAGNOSIS_PROPOSAL_REVIEW_V2` marker records it in the lifecycle result. After the helper succeeds, do not reopen discovery or modify the accepted artifact: report the accepted result. The helper snapshots external source documents and versions reused artifact IDs. Edit the source, never an accepted snapshot. Repair a named field directly; inspect lower-level schemas only after the same field repair fails twice or the helper reports an unsupported governed record.

## Control rules

- A recommendation is not a decision. Evidence establishes facts; it does not grant authority.
- Ask one decision dimension per question. Silence and non-selection decide nothing.
- Preserve decisions, overrides, rejected alternatives, changed assumptions, blockers, and residual obligations.
- Unspecified authorization is withheld. Mutation, implementation, publication, commit, deployment, closure, and delegated decisions are separate capabilities.
- Advance only a schema-valid accepted handoff satisfying its gate. A filename or completed task is not proof.
- Classify findings as fact, measurement, hypothesis, or inference. Only sourced facts and measurements are established evidence.
- Required and achieved proof must match environment, seam, and journey. An isolated harness cannot prove a stronger application journey.
- Read-only is defined by effects, not HTTP method or normal-user behavior. Do not exercise a deployed application when a request can populate caches or other durable state; use passive telemetry or obtain explicit authority.
- On validation failure, leave state unchanged and report the exact record, gate, owner, and smallest repair.

## Conditional references

The bundled runtime schemas are authoritative. Read one reference only when the compact contract or field-level error is insufficient:

- Intake revision: [references/intake.md](references/intake.md)
- Route or destination: [references/routing.md](references/routing.md)
- Collaborative alignment, evidence routing, specification, tickets, and implementation frontier: [references/collaborative-delivery.md](references/collaborative-delivery.md)
- Investigation: [references/discovery.md](references/discovery.md)
- Performance investigation: [references/performance-investigation.md](references/performance-investigation.md)
- Persisted-data design or audit: [references/data-modeling.md](references/data-modeling.md) or [references/data-model-auditing.md](references/data-model-auditing.md)
- Handoffs, proof, decisions, or gates: [references/stage-gates.md](references/stage-gates.md)
- Resume and recovery: [references/state-management.md](references/state-management.md)
