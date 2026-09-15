# Workbench Artifact Contracts

**Version:** 0.3.0  
**Status:** Proportional orchestration contract, validated and globally installed

## Purpose

This document defines how Workbench identifies, registers, relates, hands off, and validates artifacts. It is the semantic source of truth for artifact behavior. The JSON Schemas are the structural source of truth for fields and types; specialists reference those schemas instead of copying their field lists.

The contract applies to every route, including proposal-only work and the small-change fast lane.

## Contract boundaries

| Concern | Canonical source |
|---|---|
| Raw request before route selection | `schemas/workbench-intake.schema.json` |
| Intake synthesis, routing profile, and initial authorization boundary | `schemas/workbench-routing-receipt.schema.json` |
| Work-item structure and stage records | `schemas/workbench-state.schema.json` |
| Append-only changes | `schemas/workbench-event.schema.json` |
| Uncertainty nodes and obligations | `schemas/workbench-map.schema.json` |
| Artifact registry entries and lineage | `schemas/workbench-artifact.schema.json` |
| Decisions | `schemas/workbench-decision.schema.json` and `DECISION-POLICY.md` |
| Claims and proof | `schemas/workbench-proof.schema.json` |
| Execution authority | `schemas/workbench-authorization.schema.json` |
| Specialist handoffs | `schemas/workbench-handoff.schema.json` |

This document defines meanings and invariants. A schema defines their serialized representation. When the two disagree, stop the operation and resolve the version mismatch; do not guess which interpretation was intended.

## Stable identity

`work_id` and `artifact_id` are opaque, immutable identifiers:

- Work IDs use `WB-<opaque-token>`.
- Artifact IDs use `ART-<opaque-token>`.
- The kernel's generation policy determines the token and uniqueness mechanism. This contract does not require a sequence, UUID, ULID, timestamp, or other encoding.
- An ID is assigned once and is never renamed, renumbered, or reused, including after deletion, cancellation, import, or tracker publication.
- Titles, paths, stages, tracker numbers, and timestamps are descriptive metadata and never identity.

Examples:

```text
WB-2026-001
ART-012
```

Every Workbench record that refers to an artifact uses its `artifact_id`. A path may accompany the ID for convenience but cannot replace it.

## Canonical artifact registry

Each work item has one canonical record store indexed by `state.json`:

```text
.workbench/work/<work_id>/records/<artifact_id>.json
```

The record store contains artifact metadata and pointers, not copies of artifact content. `state.json.artifact_ids` is the authoritative index and `workbench-artifact.schema.json` defines each entry. `accept-handoff` updates the index, record files, event journal, stage outputs, and accepted handoff atomically.

The v0.3 source runtime accepts `current` and `superseded` artifacts only when their bytes are locally verifiable as a repository-relative `workspace-path` or exact `embedded` value. URI and tracker retrieval rules below define the longer-term contract but are not yet an implemented acceptance path. Unsupported locations block registration rather than degrading to an unchecked external reference.

The registry is authoritative for:

- identity and owning work item;
- artifact type, producing stage, and owner;
- location and content integrity;
- lifecycle status;
- direct inputs and replacement lineage;
- named downstream consumers;
- related proof and obligation pointers.

Artifacts may live anywhere the work item is authorized to reference. A generated status page, tracker issue, artifact index, or specialist document is a view or external projection; none is a second registry.

### Artifact lifecycle

The `artifact_status` enum is deliberately small:

| Status | Meaning |
|---|---|
| `draft` | The producer may still revise the content. It is not eligible to satisfy a stage gate. |
| `current` | The registered revision passed applicable validation and may be consumed. Its content is immutable. |
| `superseded` | A newer artifact explicitly replaces this revision. It remains available for history and lineage. |
| `withdrawn` | The artifact must no longer be consumed and has no replacement claimed. The reason remains recorded. |

Changing the meaning or content of a `current` artifact creates a new `artifact_id`. The old revision becomes `superseded` and points to its replacement. Metadata corrections that do not change interpretation may be evented without creating a new artifact revision.

`current` means eligible for its named consumers. It does not mean implemented, deployed, accepted by users, or proven to achieve the business outcome.

## Lineage and consumers

Lineage records direct relationships; Workbench derives the transitive graph.

- Every produced artifact names the artifacts it actually used, including raw evidence and prior decisions represented as registered artifacts or record pointers.
- A revision names the artifact it supersedes. Replacement history is linear unless an explicit merge artifact names every branch as an input.
- Lineage is append-only and acyclic. Superseding or withdrawing an artifact never erases its inputs.
- Each non-terminal artifact names at least one downstream consumer. A consumer is a stage, map node, or explicitly named external handoff—not “future work.”
- A terminal artifact names the authorized stopping point or outcome it serves.
- Consumers reference exact artifact IDs. “Latest,” a filename alone, or a tracker URL is not a reproducible input.

The content of every `current` or `superseded` artifact must remain recoverable at the registered location or immutable version reference, and its digest must still match. A dangling pointer or digest mismatch invalidates dependent handoffs.

`content_integrity` is SHA-256 over the exact bytes consumed by downstream work. Workspace and URI locations hash the retrieved byte stream without newline or encoding normalization. Embedded text hashes the exact UTF-8 bytes of the registered value. Tracker content is first exported to an immutable byte snapshot; the tracker page itself is not a stable digest target. An adapter records retrieval or serialization metadata beside the artifact when reproducing those bytes requires it.

## Stage records and handoff outcomes

Applicability, stage lifecycle, and specialist outcome are separate concepts.

The `stage_applicability` enum is:

- `undetermined`
- `applicable`
- `not-applicable`

The `stage_status` enum is:

| Status | Meaning |
|---|---|
| `pending` | The stage is on the route but has not begun. |
| `active` | At least one stage action is in progress or ready. |
| `blocked` | The stage cannot currently reach its exit criteria; blocker pointers and an owner are present. |
| `complete` | Applicable exit criteria are supported by registered artifacts and proof. |
| `skipped` | The stage was bypassed because it was not applicable or because an authorized override accepted the consequences. |

An `undetermined` stage remains `pending`. A `not-applicable` stage is `skipped`. An `applicable` stage may be `pending`, `active`, `blocked`, or `complete`; it may be `skipped` only through an authorized override with recorded consequences.

`decision-required` is not a stage status. It is a handoff outcome that creates or updates a decision node while the stage remains `active` or becomes `blocked`, as determined by the remaining ready work.

The `handoff_status` enum is:

- `completed` — the specialist completed its contracted task and returned valid outputs;
- `blocked` — a named external or evidence blocker prevents completion;
- `decision-required` — a consequential choice must be settled before dependent work proceeds.

`completed` describes the specialist task, not the lifecycle stage or business outcome.

Every applicability or status change is recorded through `workbench-event.schema.json`, including actor, cause, prior value, new value, and relevant pointers. A current-state file is a projection of those accepted transitions.

## Specialist handoff envelope

A specialist returns one envelope conforming to `workbench-handoff.schema.json`, packaged with the artifact, decision, proof, and authorization records it produced. The envelope carries these semantic groups:

- context: work, node, stage, and policy versions;
- consumed inputs: exact artifact and decision references;
- applicability: methods applied, skipped, or unresolved and why;
- result: findings, bounded options, recommendation, assumptions, and confidence when relevant;
- control requests: decisions, evidence blockers, obligations, and authorization needs;
- produced outputs: artifact registrations and proposed map or stage updates;
- routing advice: suggested next action and plain-language rationale;
- idempotency: the operation key and input fingerprint.

The envelope proposes state changes. `accept-handoff` validates local artifact existence and SHA-256 integrity, reference resolution, record identity, proof semantics, and idempotency before committing the records and event atomically. `advance-stage --accepted-handoff` can then derive the mechanical gate envelope from that registered result. A specialist does not directly rewrite canonical route, registry, decision, or proof state.

A blocked handoff must identify what is blocked, why, who owns the next action, and the node or obligation tracking it. A decision-required handoff must reference a decision record governed by `DECISION-POLICY.md`. Empty sections are permitted only where the handoff schema marks them optional for that outcome.

## Proof and obligation pointers

Artifacts point to proof records; they do not embed a private proof policy. `workbench-proof.schema.json` owns claims, required evidence, achieved evidence, limitations, and proof status. A v0.3 requirement and achieved result each name an environment, seam, and journey; an achieved result cannot pass a different target. One proof record may hold the complete requirement-to-proof matrix. Ticket annotations and delivery summaries are projections of that record, not parallel proof ledgers.

Obligations are uncertainty-map nodes governed by `workbench-map.schema.json`. An artifact may point to obligations it creates, satisfies, transfers, or leaves open. The map remains authoritative for the obligation's owner, dependencies, next action, and state.

These distinctions are binding:

- an artifact is something produced or preserved;
- a proof record evaluates a claim about it or about an outcome;
- an obligation preserves necessary future work;
- a decision authorizes a choice;
- an authorization permits a state-changing action.

One record may reference another, but none substitutes for another.

## Idempotency and atomicity

Every state-changing Workbench operation carries an idempotency key and an input fingerprint as defined by the applicable event or handoff schema.

- Repeating the same key with the same normalized inputs returns the previously accepted result and IDs without creating duplicate artifacts, events, nodes, or tracker items.
- Repeating the same key with different inputs is a conflict. The operation stops and reports both fingerprints.
- Retrying after a partial filesystem or adapter failure either completes the original atomic operation or rolls it back to the last valid registry state.
- Content equality alone does not merge independently produced artifacts. Deduplication requires an explicit identity or retry relationship.
- Adapter retries use the Workbench operation key as their external idempotency reference when the target supports one.

## Tracker neutrality

Workbench identity and state remain usable with no issue tracker configured.

- Tracker issue IDs, URLs, labels, and workflow states are external references attached to Workbench records.
- Publication occurs only through an authorized adapter after the applicable gate.
- Publishing never changes a Workbench ID and never makes the tracker the source of artifact content or lifecycle truth.
- An artifact may be projected to more than one tracker without acquiring more than one Workbench identity.
- External edits are imported as proposed events or artifacts, validated, and reconciled. They do not silently overwrite canonical state.
- Deleting or closing a tracker item does not withdraw, complete, or close its Workbench record.

## Validation expectations

Workbench validates a handoff in this order:

1. **Version and structure:** every record names supported contract versions and validates against its schema.
2. **Identity and references:** IDs have the required form, belong to the work item where required, resolve exactly once, and point to permitted record kinds.
3. **Integrity and lineage:** content locations exist, digests match, input and supersession edges are acyclic, and immutable revisions were not changed in place.
4. **Lifecycle:** requested transitions are legal; completion and skipping include the required proof or override pointers.
5. **Decision and authority:** consequential choices and state-changing actions have valid decision and authorization references.
6. **Handoff completeness:** the declared outcome supplies the corresponding artifacts, blockers, decisions, owners, and next actions.
7. **Idempotency:** the operation is new or is an exact replay of an accepted operation.

Validation failure is actionable and atomic: report the failing rule and record pointer, register no partial transition, and preserve the specialist outputs as unaccepted diagnostics when useful. Validation layers are reported separately; structural validity cannot stand in for lifecycle, proof, or authorization validity.

## Contract completion criteria

An artifact handoff is accepted only when:

- every consumed and produced artifact resolves through the canonical registry;
- every `current` output is immutable and integrity-checkable;
- direct lineage and named consumers are complete;
- stage, handoff, and artifact statuses use only their own enums;
- every open blocker, decision, proof gap, and downstream obligation has a durable pointer;
- retrying the operation is safe;
- tracker publication is optional and separately authorized; and
- a fresh agent can reconstruct the same handoff result from persisted records without conversation history.
