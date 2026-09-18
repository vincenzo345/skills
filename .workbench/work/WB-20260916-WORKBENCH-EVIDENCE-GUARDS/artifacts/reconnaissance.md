# Evidence-guard reconnaissance

- `workbench-handoff.schema.json` accepts findings only as strings.
- `accept_handoff` projects every finding as an `evidence-established` map node and attaches every handoff output as supporting evidence, regardless of what the output proves.
- Existing persisted handoffs use strings, so compatibility requires accepting them while treating them as non-established.
- Claude transcripts are JSONL. Human prompts are `type: user` entries; slash-skill expansion appears after the prompt as a meta user entry whose text names the diagnosing-bugs skill/base directory.
- `~/.claude/settings.json` has no Workbench hook. A standard-library Python hook can consume `PreToolUse` JSON on stdin and inspect `transcript_path` without `jq`.
- The conformance catalog currently has six structural behavior oracles and explicitly does not execute a model.

Blast radius is limited to new handoff acceptance/projection, one new hook script and focused tests, two fixture cases, and one additive global Claude hook registration. Existing maps and events are snapshots and are not rewritten.
