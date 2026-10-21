# Issue tracker: Local Markdown

Use stable `work/<effort>/` folders. Read the setup-repo skill's `WORK-RECORDS.md` shared contract before producing, selecting, or changing work records, including claims and completion. Configure its helper's authority to the selected live checkout. Explicit repository conventions override these defaults.

## Locations and operations

- Overview: `work/<effort>/README.md`; current spec: `spec.md`.
- Approved implementation issues: one file each in `tickets/<NN>-<slug>.md`.
- Wayfinder map: `map.md`; decision tickets: `decisions/<NN>-<slug>.md`.
- Ordinary findings: `discovery.md`; research: `research/`; retained revisions: `history/`.
- Queue: `work/queue.md`, ordered unique effort links. Completed efforts leave selection and stay at their original paths.

Create only needed artifacts. Resume by explicit identity. Use typed YAML metadata for lifecycle, readiness, basis, ordering and dependencies; keep comments under `## Comments`. The queue owns priority, the overview owns current pointers, and each issue owns state. Producers record user approval before publishing ready children. Consumers acquire exclusive ownership through the shared helper before work and record completion only after acceptance and integration.

Wayfinder decision tickets own questions and answers and have a separate resolved-decision frontier. Keep map completion separate from session completion. Decision tickets never become implementation slices by location or filename. Existing legacy references remain in place; resolve missing eligibility information explicitly and migrate only through a separately reviewed mapping.
