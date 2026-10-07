# Legacy manual gate receipts

Read this reference only when advancing a legacy journal or a recovery case that cannot use `accept-handoff` followed by `advance-stage --accepted-handoff`.

Build a manual receipt from the latest projection, not from memory. It contains:

- `work_id` and `stage_id` matching current state;
- `state_revision` matching the revision reported by `status`;
- `exit_gate` matching the stage's registered exit-gate handler;
- `result` set to `passed`;
- a nonempty `evidence` array of typed record references;
- `checked_at` as an ISO 8601 timestamp with a timezone, no more than seven days old and no more than five minutes in the future; and
- `checked_by` as an actor ID string or an actor object with `actor_id` and a valid actor kind.

The receipt is a runtime input envelope, not a registered Workbench record. The runtime does not require `schema_version`. For profile-compiled v0.3 work, generic work or external-file references do not satisfy a checkpoint requiring a registered artifact, decision, proof, authorization, or handoff.

Pass the same revision through `--expected-revision`. If another command advances the revision, refresh the projection, re-evaluate the gate, and create a new receipt.

Minimal intake receipt:

```json
{
  "work_id": "WB-DEMO-001",
  "state_revision": 1,
  "stage_id": "intake",
  "exit_gate": "intake-recorded",
  "result": "passed",
  "evidence": [
    {
      "record_type": "work",
      "record_id": "WB-DEMO-001"
    }
  ],
  "checked_at": "2026-09-14T15:30:00-05:00",
  "checked_by": {
    "actor_id": "agent:workbench",
    "kind": "agent"
  }
}
```

`proof_records` and `authorization_records` are optional arrays of complete records valid against their bundled schemas. IDs or shorthand grants are insufficient. Full records are mandatory when:

- the checkpoint completes the destination: include passed destination proof and an unexpired closure authorization scoped to the work and destination;
- advancement enters `implementation`: include an applicable implementation authorization;
- advancement enters `release`: include an applicable deployment authorization; or
- the verification checkpoint requires local-implementation, deployed-behavior, or business-outcome proof.

Run the transition with the checked revision:

```text
python -B "<workbench-skill-dir>/scripts/workbench.py" advance-stage --repo "<current-repo>" --work-id "WB-DEMO-001" --gate-receipt "<receipt.json>" --idempotency-key "..." --expected-revision 1 --actor "agent:workbench"
```

A structurally acceptable receipt proves only what its evidence establishes. Prefer accepted handoffs because they verify local artifact content and preserve registered evidence for later projections.
