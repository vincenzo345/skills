# Evidence-guard local verification

Passed on 2026-09-16:

- `python -m pytest tests/runtime -q` — 96 passed.
- Focused typed-finding, hook, and adherence tests — 16 passed.
- `python -B scripts/validate-workbench.py` — foundation validation passed (schemas, records, scenarios, negative contracts, and comparison fixtures).
- Skill Creator `quick_validate.py skills/workbench` — valid.
- `python -m json.tool` — packaged handoff schema and Claude user settings parse.
- `git diff --check` — clean.
- Global Workbench `SKILL.md` SHA-256 equals the repository copy through the existing junction; the global hook script path exists.
- Claude user settings contain one `PreToolUse` matcher for `Read|Grep|Glob|Bash|Task|WebFetch|WebSearch` pointing to the global Workbench hook.

Non-vacuity: the runtime test accepts a mixed handoff and inspects the persisted map statuses; it also proves an unsourced fact is rejected atomically. Hook tests execute the script as a subprocess against synthetic Claude transcript JSONL and observe deny/allow output. The two new comparison cases are structural behavior oracles, not an executed model evaluation.

Residual risk: a producer can still misclassify a claim as a fact and cite a source that does not semantically support it. The runtime verifies source identity and resolution, not entailment. The new hook guarantees skill invocation at the covered seam, not that every diagnosis conclusion is correct.

The predecessor hardening item remains revision 12 and awaiting acceptance. No commit, push, deployment, publication, or closure was performed.
