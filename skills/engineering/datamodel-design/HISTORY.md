# History and provenance

First identify the exact question a future reader must answer: the current value, what was presented at a point in time, what was believed then, or why a result changed. These needs imply different representations.

| Need | Candidate representation | Decision to make |
|---|---|---|
| Only the current value matters | Mutable record | Whether any operational audit is separately required |
| Preserve selected milestones | Snapshot or retained revision | Which fields and dependencies must be frozen |
| Explain changes | Audit history | Actor, cause, before/after data, and retention needed |
| Reconstruct state from events | Event history with replay rules | Ordering, corrections, schema evolution, and replay cost |

Snapshots and references require an explicit policy for their inputs. Referencing a mutable record's ID does not freeze its values. Choose immutable input revisions, retained copied values, or another verifiable representation according to the requirement. State which transformations or configuration must also be identified to reproduce a derived result.

Distinguish a fact's effective time from when it was recorded when late information or retroactive corrections matter. Use a temporal model only if a real question requires it.

Walk one correction through the model. For a presented analysis, determine whether correction creates new evidence, invalidates future use, or changes the historical display. Keep the original presentation's meaning intact according to the agreed requirement; do not choose the policy silently. For a simple editable contact record with no history requirement, a mutable representation may be sufficient.

Record deletion and retention consequences too: historical records may hold copied personal data or depend on sources scheduled for deletion. Raise actual conflicts with the human rather than inventing a retention period.
