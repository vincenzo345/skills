# Standards profile for adherence hardening

- **Skill authoring:** keep the entry skill concise; add only guidance that changes decisions; avoid copying diagnosis or research procedures into Workbench.
- **Agent writing:** place always-needed coordination rules in `SKILL.md`; preserve one source of truth and phrase positive target behavior.
- **Regression seam:** conformance cases observe the required agent response to a user message and current state. Runtime tests continue to use only the public CLI and file-backed records.
- **TDD:** add the conformance contract and its failing validator expectations before implementing fixture validation; use independent expected outcomes rather than matching skill wording.
- **Issue boundary:** local Markdown tickets specify runtime changes and tests, but this work item does not change runtime schemas or behavior.
- **Safety:** leave the manual-extraction repository and its Workbench store untouched; preserve existing unrelated repository state.
