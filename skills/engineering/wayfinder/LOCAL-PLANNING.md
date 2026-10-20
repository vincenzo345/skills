# Local planning operations

Read the repository tracker convention and [shared contract](../setup-repo/WORK-RECORDS.md) first. Use its declared authority and stable effort; these operations do not configure a second tracker or migrate historical records. Explicit legacy records remain at their original references.

The packaged `../setup-repo/scripts/work_planning.py` extends the shared producer with planning operations. It uses the same checkout authority, OS lock, and token claim store as implementation. Run it with Python and PyYAML from its installed location, always passing the target checkout:

```text
python <setup-repo>/scripts/work_planning.py --repo <checkout> <operation> --request-file <request.json>
```

The JSON file holds the operation's named arguments. The public Python interface is `PlanningRecords(checkout)`. It also exposes the shared `create_effort`, `publish_spec`, `publish_issue`, `read`, and `release` operations. Use the shared helper for those CLI operations.

| Operation | Request fields | Observable result |
| --- | --- | --- |
| `chart` | `effort`, `title`, `destination`, `fog`, optional `notes` | Creates the open map and updates the effort's current map. Existing maps require resumption, not overwrite. |
| `record-discovery` | `effort`, `finding` | Appends a durable finding and links discovery from the overview. Include open questions and source context in the finding. |
| `add-decision` | `effort`, `slug`, `title`, `question`, `decision_type`, optional `blocked_by` | Creates a typed ordered decision under `decisions/`; type is grilling, prototype, research, or task. Create blockers before dependents. |
| `claim-decision` | `target`, `owner` | Validates the current decision and resolved blockers, then returns an exclusive token. |
| `resolve-decision` | `target`, `token`, `answer`, optional `human_answer` | Records the authoritative answer, links it from the still-open map, and releases the claim. Grilling/prototype require supplied human evidence. For HITL tasks, the caller must also supply actual human confirmation. |
| `supersede-decision` | `target`, `replacement`, `reason` | Retains the old answer, links its open replacement, rewires direct dependencies, and gates affected dependent decisions for review. Release any old claim first. |
| `review-decision` | `target`, `rationale` | Clears the dependent-review gate after actual impact review; records why the question or answer still applies. If an answer no longer applies, supersede it instead. |

Example `add-decision` request:

```json
{"effort":"work/note-search","slug":"scope","title":"Search scope","question":"Search titles or full text?","decision_type":"grilling","blocked_by":[]}
```

The optional `review_required: [<invalidated-decision-ID>]` metadata records a dependent-review gate separately from decision lifecycle; it is never an implementation readiness label.

Frontier reads use authoritative decision records ordered by `order`: open, no `review_required`, all blockers resolved with answers and no pending review, and no existing claim. The atomic claim operation rechecks those gates. Preserve the token across replies; do not reacquire or switch decisions because the human sends another message. Release with the shared helper when deferring; elapsed time never grants takeover. Claims cannot authenticate human evidence, evaluate experiment relevance, or enforce conversational session boundaries; those remain agent obligations and require behavioral replay.

For charting and continuation, update the overview's next action to the named decision and required input, and keep a named map link in its body. Use the coordinator lock for map prose/fog, next-action, cancellation, or explicit map completion edits not exposed by a dedicated command: acquire `records.locked()`, establish `records._authority()`, read the current records, and use `records._write(...)` only within that block. Preserve other sessions' changes. These are low-level maintenance writes, not an alternate claim mechanism. A map remains open at a session stop; completion requires every decision settled and no in-scope fog. Cancel out-of-scope decisions with a reason and an Out of scope link, not a resolved answer.

Supersession gates dependents before publishing the replacement pointer. If interrupted, inspect the prior record and affected dependencies under the lock, finish the same operation, and retain every answer. Do not clear review gates merely to restore eligibility. A resolved dependent with pending review cannot satisfy a later decision's blocker.
