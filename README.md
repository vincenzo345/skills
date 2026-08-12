# Skills

My agent skills — the ones I actually use. Written for Claude Code and Codex.

The pack is one pipeline: **a meeting becomes a scope tree a build can run against**, without
acceptance ever being won by exhausting the person who does the work. Every skill here is one I
wrote and understand. The set is small on purpose and grows one finished skill at a time.

## Install

**Any agent (Claude Code, Codex, and others):**

```bash
npx skills@latest add vincenzo345/skills
```

Pick the skills you want and which agents to install them on.

**Claude Code, as a managed plugin:**

```bash
claude plugin marketplace add vincenzo345/skills
claude plugin install vince-skills@vincenzo345
```

Updates arrive when I push.

## Skills

### User-invoked

Two skills, one pipeline, run in that order. A raw meeting export becomes a normalised
transcript; the transcript becomes a scope tree the expert has corrected and signed.

- [`to-record`](./skills/to-record/SKILL.md) — turn a raw meeting export into a normalised transcript whose every word is preserved and whose defects are flagged: turns reconstructed from crosstalk, a script that checks the word multiset survived, and six flags about the record rather than questions about the domain.
- [`to-scope`](./skills/to-scope/SKILL.md) — turn that transcript into a signed-off scope tree a build can run against: a story map drafted from what was said, a coverage pass that walks the record for what the tree missed, a conflict pass with no drafting job, the builder grilled so the expert sits through fewer questions, and a review session where the expert corrects a paraphrase instead of composing an answer.

**`to-scope` resumes.** Five passes over a record do not fit in one sitting, and the expert is
rarely free on drafting day. Re-invoke it and it reads the tree, works out which pass never
finished, and starts there — re-drafting nothing, renumbering nothing, and re-asking nobody.

## Working on this repo

Clone it, then link every skill into your local agent directories as junctions, so edits are live:

```powershell
.\scripts\link-skills.ps1
```

Conventions for adding a skill live in [CLAUDE.md](./CLAUDE.md).

## Credit

The shape of this repo — buckets of skills, a plugin manifest, a link script, the user-invoked vs model-invoked split — is modelled on [mattpocock/skills](https://github.com/mattpocock/skills), which is worth reading. No text from it ships here.

## Licence

MIT
