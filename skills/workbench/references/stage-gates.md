# Phase checkpoints and gates

Use this reference before invoking a specialist, accepting a handoff, advancing a checkpoint, or claiming a planning destination. Read the current phase, checkpoint activity, included activities, and destination from persisted state and `schemas/workbench-lifecycle.schema.json`; its registry is the only lifecycle vocabulary.

## Evaluate a checkpoint

For the active phase checkpoint:

1. Use the latest complete projection and confirm work ID, profile, destination, phase, checkpoint activity, included activities, status, revision, and frontier. Refresh with `status` only if the projection may be stale.
2. Read the compiled plan's activity dispositions. Do not run a not-applicable activity and do not create an extra transition for each applicable lens.
3. Evaluate the checkpoint activity's registered entry gate against exact record references. Missing inputs block entry; narrative confidence does not satisfy it.
4. Dispatch only ready tasks whose recorded owner is an agent. Give each method bounded inputs, a completion condition, and one phase handoff contract sized for the 150,000–250,000-token per-agent envelope. Keep related methods in the current agent; use a subagent only for independent work, valuable parallelism, context containment, or an independence-sensitive review with material expected value.
5. Accept the bundle with `accept-handoff`. The runtime validates structure, identity, input resolution, local artifact SHA-256 integrity, proof semantics, lifecycle meaning, decision authority, and idempotency before registering any proposed change.
6. Evaluate the registered exit gate using the accepted records. A completed specialist task or a filename citation is not automatically a completed checkpoint.
7. Before advancing, make the human-control answers visible and preserve every decision, blocker, override, and downstream obligation.

Do not manually reinterpret a handler ID. If the installed runtime does not implement it, report that gate as unsupported and leave the stage unchanged.

## Accepted handoff path

The normal v0.5 path is one structured handoff bundle followed by a derived advance:

```text
python -B "<workbench-skill-dir>/scripts/workbench.py" accept-handoff --repo "<current-repo>" --work-id "WB-DEMO-001" --handoff-bundle "<bundle.json>" --idempotency-key "..." --expected-revision 1 --actor "agent:workbench"
python -B "<workbench-skill-dir>/scripts/workbench.py" advance-stage --repo "<current-repo>" --work-id "WB-DEMO-001" --accepted-handoff "HO-DEMO-001" --idempotency-key "..." --expected-revision 2 --actor "agent:workbench"
```

The bundle contains one `handoff` valid against `workbench-handoff.schema.json` and a `records` array containing its artifact, decision, proof, and authorization outputs. The handoff's `input_fingerprint` is the canonical SHA-256 digest of its `inputs_used` and `policy_versions`. Every workspace artifact must exist beneath the target repository and match its recorded digest. Workbench registers the records, updates state pointers and checkpoint outputs, and appends one event atomically. An exact retry is idempotent; a conflicting retry or any invalid record changes nothing.

For a v0.5 handoff, set `schema_version` and `policy_versions.workbench` to the installed runtime version. Accepted findings become evidence nodes, uncertainties become durable fog, and supplied decision records become decision nodes, so `resume` exposes the reasoning frontier without rereading the artifact. Use `node_updates` for existing nodes; do not duplicate the automatically projected records.

`advance-stage --accepted-handoff` derives the gate evidence from that registered handoff and its outputs. It cannot make a weak handoff stronger: the checkpoint still requires the record types named by its gate, and destination, implementation, deployment, and closure rules still apply.

## Manual gate-receipt compatibility

The manual receipt path exists only for legacy journals and recovery cases that cannot use accepted handoffs. Read [legacy-gates.md](legacy-gates.md) only when that branch is actually required.

## Execution economy

Assign one primary producer for the phase and one consolidated handoff. A shared artifact may cover several included activities; require separate artifacts only when they have distinct consumers, owners, lifecycles, or proof requirements.

Every delegated session ends with its assigned outcome achieved or a resumable handoff that identifies the outcome and inputs, evidence, decisions and assumptions, artifacts, verification, remaining uncertainty or blocker, and exact next action. Accept the handoff only when these are represented by its registered records; do not invent schema fields. The coordinator synthesizes accepted handoffs and reopens their source material only when a material claim needs verification.

Use one fixed review set derived from the actual change, its risks, and the destination. Prefer a single review pass across related axes. Parallel independent review is justified when independence materially improves the oracle or when the axes can be evaluated without duplicating repository discovery. After a finding is corrected, re-review the finding and affected seams; reopen settled axes only when the correction changes them.

Verification begins with the smallest focused checks that exercise changed behavior and realistic failure paths. Add integration journeys, full-suite checks, security or architecture review, and repository-wide governance only when applicable policy, blast radius, or the selected destination requires them. Record pre-existing repository failures separately from feature-focused results.

## Human-control checkpoint

Every stage result must make these answers apparent without rereading the conversation:

1. Where are we?
2. What did we learn?
3. What did we decide, and which alternatives were rejected?
4. Why is the proposed action next?
5. What remains uncertain?

Link to evidence and detail rather than pasting full specialist artifacts. If any answer depends on hidden reasoning, fix the records or handoff before advancing.

## Decisions and pauses

Separate factual findings from consequential choices. Facts can be established by evidence at a bounded scope and confidence. A material selection among futures stays human-owned unless a valid decision-delegation authorization names the decision or bounded class, delegate, defaults, escalation thresholds, excluded actions, and terminating condition.

For a consequential choice, present no more than three meaningful options by default, including defer or gather evidence when responsible. Show benefits, costs, risks, reversibility, assumptions, uncertainties, recommendation, and what each choice makes harder later. Ask for an unambiguous choice only after showing the consequence receipt.

Confusion, silence, fatigue, acceptance of a document, or permission to continue is not consent. Keep dependent work paused. A delegated decision never grants implementation, mutation, publication, commit, deployment, or closure.

## Authorization gate

Before a consequential action, find a current authorization record whose action, target, constraints, authority, and validity cover exactly that operation. Treat these as separate capabilities:

- repository or other durable content mutation;
- implementation;
- tracker publication;
- commit;
- deployment;
- closure;
- decision delegation.

The user's initiating request can be the grant basis when it explicitly asks for the action at sufficient scope, but the grant must still be recorded. One capability does not imply another. Never infer authority from a recommendation, selected route, accepted proposal, approved specification, successful test, or prior grant.

## Proof and completion

Read the selected destination entry in the lifecycle registry for its completion stage, work status, and required proof kind. Then validate the corresponding proof record. Structural validity, feature-focused behavior, integration journeys, repository health, user acceptance, deployment readiness, deployed behavior, and business outcome are different claims.

For every v0.3 proof, record `verification_scope`. Each required and achieved result also names its exact verification target—environment, seam, and journey—and the targets must match. If the required authenticated application journey cannot run, record that integration scope as `blocked`; do not pass it with an isolated component harness. A feature-focused pass can coexist with blocked integration proof and failing pre-existing repository health without collapsing those dispositions into one ambiguous status.

Use `paused` for a coherent item waiting on a user or external event; use `blocked` when an applicable stage cannot meet its exit; use a terminal stop only for its recorded reason. Passing the destination gate without closure authorization produces `awaiting-acceptance`: the requested result is ready for review while administrative closure remains a separate human action. `close` requires destination-specific authorization and records the terminal claim. A completed proposal may support a proceed, hold, or reject decision without proving feasibility, authorizing implementation, or achieving the business outcome.

## Handoff acceptance

A specialist proposes changes; Workbench accepts them atomically or not at all. A valid handoff must:

- identify the exact work, node, canonical stage, specialist, owner, operation key, and input fingerprint;
- point to the records actually consumed and the policy versions applied;
- distinguish findings from recommendations and decisions;
- register current outputs with stable identity, lineage, integrity, consumers, and proof pointers;
- leave every open blocker, decision, and obligation with an owner and next action; and
- propose node or routing changes without rewriting canonical state directly.

An exact retry returns the accepted result. Reusing an operation key with different inputs is a conflict. On any failure, register no partial transition and report the smallest record-level correction needed. A generic external reference proves only that a string was recorded; it is not a substitute for a registered, integrity-checked artifact or semantically valid proof.
