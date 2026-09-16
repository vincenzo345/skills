# Source behavior comparison fixtures

These synthetic fixtures preserve behaviors that the Workbench migration must keep or improve. They contain no client or production data.

| Fixture | Behavior under comparison |
|---|---|
| `evidence-intake/` | Verbatim token preservation is necessary but insufficient; speaker attribution and source lineage must also be checked. |
| `process-model/` | Process reconstruction must account for triggers, actors, branches, waits, manual work, systems, data, measures, and unresolved holes. |
| `uncertainty-map/` | Fog becomes a question and ready evidence work; evidence unlocks decisions and obligations; invalidation reopens dependencies without erasing history. |
| `informed-decision/` | Confusion cannot confirm a consequential decision; a later consequence receipt can. |
| `coverage-and-proof/` | Requirements cannot disappear during ticketing, and empty or lower-level evidence cannot satisfy a stronger claim. |
| `workbench-adherence/` | Workbench composes mandatory methods, resolves its store before mutation, preserves decision and authorization sources, and does not promote unsupported claims or post-start overrides. |

These are comparison oracles, not complete route scenarios. Route fixtures live under `tests/scenarios/`.

## Completion rule

A replacement behavior passes comparison only when its produced structured artifacts satisfy every `expected.json` assertion for the fixture. Matching prose is not a pass.
