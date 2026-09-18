# Standards profile

- TDD uses the three agreed public seams: `accept-handoff`/map projection, hook stdin/stdout with a synthetic transcript, and the adherence fixture catalog.
- Work in vertical slices: typed finding test and implementation; hook test and implementation; then fixture cases.
- The hook is a dependency-free Python script, silent on allow, narrowly scoped to Workbench diagnosis prompts, and actionable on deny.
- The skill entrypoint gains only the finding-classification invariant; detailed mechanics remain enforced by schema/runtime rather than duplicated as prose.
- Legacy handoff strings remain readable but lose automatic evidence status. Existing stored records are not migrated.
- Focused tests precede full runtime/schema/skill validation. No commit, push, deployment, or closure is authorized.
