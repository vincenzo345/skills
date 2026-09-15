# State management

Use this reference to start, resume, inspect, or advance Workbench work, especially in a fresh agent context.

## Keep runtime and project separate

`<workbench-skill-dir>` is the installed directory containing `SKILL.md`. `<current-repo>` is the repository containing the user's work. Invoke the bundled runtime from the former and pass the latter explicitly:

```text
python -B "<workbench-skill-dir>/scripts/workbench.py" --help
python -B "<workbench-skill-dir>/scripts/workbench.py" <command> --repo "<current-repo>" ...
```

The CLI also has narrow wrappers for compatibility: `start-work.py`, `show-status.py`, `select-next-node.py`, and `advance-stage.py`. Prefer `workbench.py` so every command uses the same validation and path rules. Treat `render-map` as deferred unless the installed runtime advertises it.

Never assume the current repository contains the runtime. Never run a development checkout's script merely because it has the same name. Use `--help` for the installed version's exact arguments and supported capability claim.

## Command workflow

- `capture-intake` preserves a new user's ordinary request and named references before route selection. It creates a resumable `intake-draft` whose route and planning destination remain uncommitted. Use it before inspecting and synthesizing a new request:

  ```text
  python -B "<workbench-skill-dir>/scripts/workbench.py" capture-intake --repo "<current-repo>" --work-id "WB-..." --request "<exact request>" --reference "<exact source>" --idempotency-key "..." [--owner "user:..."]
  ```

  Repeat `--reference` as needed. Do not rewrite the request before capture.
- `route-and-start` is the preferred continuation after capture. It consumes the synthesized routing input, defaults every unlisted capability to withheld, compiles applicable activities into proportional phase checkpoints through the destination, persists the immutable receipt, and starts lifecycle state in one transaction:

  ```text
  python -B "<workbench-skill-dir>/scripts/workbench.py" route-and-start --repo "<current-repo>" --work-id "WB-..." --routing-input "<routing-input.json>" --idempotency-key "..." [--owner "user:..."]
  ```

  The receipt separates business basis, solution context, engagement intent, planning destination, and execution lane. Greenfield and brownfield are both compiled directly; `runtime_route` may be null because it is legacy metadata, not the lifecycle source for new work. Undetermined material applicability blocks the entire transaction without leaving a routing receipt or partial lifecycle state.
- `finalize-intake` is the deliberate pause point. It persists the same immutable routing receipt without starting. Use it when a material routing review or external wait is required:

  ```text
  python -B "<workbench-skill-dir>/scripts/workbench.py" finalize-intake --repo "<current-repo>" --work-id "WB-..." --routing-input "<routing-input.json>" --idempotency-key "..." [--owner "user:..."]
  ```

- `revise-routing` records answers or corrected pre-start synthesis without replacing the work item or overwriting a receipt. Supply the complete updated routing input plus `revision_reason` and `resolved_questions`; each resolved item contains the exact previous question, its answer, and source references. The expected revision is mandatory:

  ```text
  python -B "<workbench-skill-dir>/scripts/workbench.py" revise-routing --repo "<current-repo>" --work-id "WB-..." --routing-input "<updated-routing-input.json>" --expected-routing-revision N --idempotency-key "..." [--owner "user:..."]
  ```

  The update file repeats every normal routing field and adds:

  ```json
  {
    "revision_reason": "The user resolved the product-direction questions.",
    "resolved_questions": [
      {
        "question": "Exact question from the prior receipt?",
        "answer": "The user's answer.",
        "source_references": ["user-response:<stable-session-reference>"]
      }
    ]
  }
  ```

  The runtime preserves `routing.json` as revision one and appends later immutable receipts under `routing-revisions/`. It rejects stale updates, missing answer records for removed questions, broken lineage, and every routing revision attempted after lifecycle start. An identical retry is idempotent.

- `start --from-routing` resumes a finalized ready receipt. The runtime derives title, outcome, profile-compiled route, destination, and owner from the receipt; do not repeat them unless checking compatibility with an exact match:

  ```text
  python -B "<workbench-skill-dir>/scripts/workbench.py" start --repo "<current-repo>" --work-id "WB-..." --idempotency-key "..." --from-routing [--owner "user:..."]
  ```

  Direct `start` remains supported for already-structured legacy work with no captured draft. `start --from-intake` remains compatible for a captured v0.1 draft with no routing receipt. A finalized receipt requires `--from-routing`; unresolved routing is rejected without mutation. The receipt's authorization boundary records request interpretation but does not replace the scoped authorization records required by later implementation, deployment, or closure gates.
- `resume` locates and validates an existing work item, then reports the persisted revision and current position. `resume --work-id` also selects that item in `.workbench/active-work.json`. When more than one item could match, ask the user to select by work ID; do not guess from the conversation.
- `status` validates and projects an `intake-draft`, the latest `routing-ready` or `routing-blocked` revision, or a replayed and snapshot-compared lifecycle checkpoint. A current pre-start projection includes routing lineage and recorded question resolutions; a lifecycle projection includes the profile, current phase, included activities, authorization boundary, ready frontier, next action, and verification scopes. It also rechecks routing lineage and registered workspace artifact digests. It is read-only and does not prove a real-world claim or authorize a transition.
- `next` returns a narrower view of the same frontier. Use it when that focus helps, not mechanically after `status`. The runtime does not yet compute dependency-edge readiness, so verify map dependencies before acting. Its recommendation is not a grant to perform a consequential action.
- `accept-handoff` validates one specialist bundle and atomically registers its artifact, decision, proof, and authorization records, accepted handoff, stage outputs, state revision, and event:

  ```text
  python -B "<workbench-skill-dir>/scripts/workbench.py" accept-handoff --repo "<current-repo>" --work-id "WB-..." --handoff-bundle "<bundle.json>" --idempotency-key "..." --expected-revision N [--actor "agent:..."]
  ```

- `advance-stage` requests a persisted checkpoint transition. Prefer an accepted handoff ID, which lets the runtime derive the mechanical receipt. A manual gate-receipt file remains a compatibility path; provide exactly one:

  ```text
  python -B "<workbench-skill-dir>/scripts/workbench.py" advance-stage --repo "<current-repo>" --work-id "WB-..." --accepted-handoff "HO-..." --idempotency-key "..." --expected-revision N [--actor "agent:..."]
  ```

  Verify which lifecycle, proof, handoff, authorization-consumption, and destination-completion checks the installed version enforces. Report unenforced checks and do not describe the transition as fully validated when they remain outside the runtime.
- `replay` rebuilds or checks the current projection from the append-only event stream. A mismatch blocks mutation until repaired through a supported recovery path.

`resume`, `status`, `next`, and `replay` accept an optional `--work-id`; without it they use `.workbench/active-work.json`. Add `--json` when deterministic structured output is needed.

Successful mutations return the updated projection. Do not immediately rerun `status` or `next` unless another actor or external event may have changed the state. Never repair a failed operation by editing JSON or YAML directly.

## Repository state

Canonical work records live under `.workbench/work/<work-id>/` in the current repository. A new pre-start item contains immutable `intake.json` and, after finalization, immutable `routing.json`. Corrections append under `routing-revisions/<revision>.json`; the highest valid contiguous revision is current, and every revision binds its predecessor's reference and digest. Routed start binds the exact intake and current routing revision into the first event. Lifecycle work additionally persists state, events, the uncertainty map, and accepted records beneath `records/`. `accept-handoff` is the registration path for artifacts, decisions, proofs, authorizations, and handoffs. Map-node creation and dependency mutation remain deferred. Generated status, diagrams, tracker items, and specialist documents are projections or referenced artifacts, not alternate state stores.

Treat the event stream as append-only and current state as its projection. Preserve stable IDs across retries, corrections, route changes, and fresh sessions. Current or superseded artifacts must retain content integrity and exact lineage. Do not rename IDs to match filenames, tracker tickets, or stage labels.

## Fresh-context resume protocol

At the beginning of a new session:

1. Locate the installed Workbench skill directory and current repository.
2. Run `resume` for the explicit work ID, or list/select through the installed CLI if its help advertises that capability.
3. Use the `resume` projection directly. If it reports `intake-draft`, inspect the raw request and sources before routing. If it reports `routing-blocked`, answer or investigate only the named frontier item, append the updated synthesis with `revise-routing`, and use the returned projection. If it reports `routing-ready`, bind-start the latest revision. Otherwise verify work ID, state revision, routing profile, destination, current phase, included activities, work status, verification dispositions, and latest event.
4. Read the human-control fields, then inspect persisted authorization records separately when the proposed action is consequential.
5. Verify map dependencies and inspect only the records needed for the selected frontier item. Run `next` only if a narrower frontier view is useful.
6. State the recommended action and why before invoking a specialist or requesting a human decision.

Conversation summaries can help locate a work ID but cannot override persisted facts. If chat and files disagree, report the discrepancy and treat the validated persisted records as current until an authorized correction is recorded.

## Conflict and recovery behavior

- A stale expected revision, illegal transition, mismatched before-value, invalid gate proof, expired or out-of-scope authorization, or reused operation key with different inputs must stop without partial mutation.
- An identical retry should return the prior accepted result rather than duplicate events or artifacts.
- If replay and current state disagree, stop all mutation, preserve diagnostics, and use only a tested recovery operation advertised by the installed runtime.
- Missing or corrupt state is a blocker, not permission to reconstruct decisions from memory.
- If the installed runtime labels a capability read-only, unproven, deferred, or unsupported, repeat that limitation to the user and do not simulate the missing behavior.
