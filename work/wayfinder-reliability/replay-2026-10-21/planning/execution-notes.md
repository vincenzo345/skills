# Execution notes

Harness: fresh Codex agent, fork_turns=none, same model as controller (controller supplied).

## Installed files loaded

- C:/Users/vince/.codex/skills/wayfinder/SKILL.md
- C:/Users/vince/.codex/skills/wayfinder/LOCAL-PLANNING.md
- C:/Users/vince/.codex/skills/setup-repo/SKILL.md
- C:/Users/vince/.codex/skills/setup-repo/WORK-RECORDS.md
- C:/Users/vince/.codex/skills/setup-repo/issue-tracker-local.md
- C:/Users/vince/.codex/skills/setup-repo/domain.md (copied into fixture configuration)
- C:/Users/vince/.codex/skills/setup-repo/scripts/work_records.py (help, selected implementation portions, Python import)
- C:/Users/vince/.codex/skills/setup-repo/scripts/work_planning.py (selected implementation portions, Python import)
- C:/Users/vince/.codex/skills/grill-with-docs/SKILL.md
- C:/Users/vince/.codex/skills/grilling/SKILL.md
- C:/Users/vince/.codex/skills/domain-modeling/SKILL.md
- C:/Users/vince/.codex/skills/domain-modeling/GLOSSARY-FORMAT.md

Python also imports the installed helpers' dependencies in the usual way. No source-repository tests, rubric, or validation files were read. All replay writes occurred in the temporary fixture/evidence tree.

## Errors and retries

No helper operation reported an exception or failed status. No operation was retried to bypass a failure. PowerShell-to-Python stdin replaced non-ASCII characters with question marks in early transcript text. During turn 2, its response field was corrected using Unicode escapes before delivering the final response; wording of its commentary was normalized to ASCII. The tool trace retains the initial output. Other early transcript entries may still contain encoding substitutions. Later entries use Unicode escapes/ASCII. No artifact snapshots were rewritten.

## Observed behavior and limitations

- Three initial decisions were created, with ranking wired to scope after creation. Import began as fog, then became a decision after scope resolved.
- One scope claim persisted through the insufficient personal/offline response. Only the next actual scope answer resolved it.
- Scope changes used new decisions and installed supersession, preserving prior answers and rewiring ranking. Ranking impact review was performed and recorded before clearing its review gate.
- The controller's turn-6 anchor precondition was accepted. Helper operations succeeded with the anchored current-map pointer, and its prior-answer link kept the anchor. No manual repair was applied.
- Map gist text was edited under the coordinator lock in earlier turns as ordinary map maintenance. The turn-6 helper-produced map text was left intact.
- The final turn rejected the unrelated article rewrite as a prerequisite, claimed Offline storage, and asked for human input without resolving it.
- Snapshots copy the working tree excluding .git; they do not independently capture the Git-common-directory claim store. Claim receipts were stored in active-claim.json when active; the earlier scope receipt was removed after its resolution. Current final receipt is the storage claim.
- There is no implementation or specification, and the map remains open.
- Skills were applied by reading installed files; no Skill invocation tool was available. Installed helper implementation excerpts were read to use their public interface and documented maintenance lock safely.
