# Skills

My focused agent skills for Claude Code and Codex. The set stays small on purpose: durable
Workbench coordination, reusable engineering workflows, and a requirements pipeline that turns
a meeting into a scope tree a build can run against.

## Install

**Any agent (Claude Code, Codex, and others):**

```bash
npx skills@latest add vincenzo345/skills
```

Pick the skills you want and which agents to install them on.

To install the tested correctness-focused Claude Code harness directly from this GitHub
repository, select only `claude-rigor` and install it globally for Claude Code:

```bash
npx skills@latest add vincenzo345/skills --skill claude-rigor --agent claude-code --global --copy -y
```

Start a new Claude Code session after installation. The installed folder is also a
self-contained Claude Code plugin: it activates the rigorous default agent and the
one-shot completion-review hook without changing the user's global `CLAUDE.md` or
`settings.json`. No public Claude marketplace listing is required.

**Claude Code, as a managed plugin from this GitHub repository (optional):**

```bash
claude plugin marketplace add vincenzo345/skills
claude plugin install vince-skills@vincenzo345
```

Updates arrive when I push.

## Skills

### User-invoked

The `claude-rigor` harness is independent of the two-skill requirements pipeline below.
In that pipeline, a raw meeting export becomes a normalised
transcript; the transcript becomes a scope tree the expert has corrected and signed.

- [`claude-rigor`](./skills/claude-rigor/SKILL.md) — install and inspect the direct-GitHub Claude Code harness that applies the validated operating contract and enforces one skeptical review after code edits.
- [`to-record`](./skills/to-record/SKILL.md) — turn a raw meeting export into a normalised transcript whose every word is preserved and whose defects are flagged: turns reconstructed from crosstalk, a script that checks the word multiset survived, and six flags about the record rather than questions about the domain.
- [`to-scope`](./skills/to-scope/SKILL.md) — turn that transcript into a signed-off scope tree a build can run against: a story map drafted from what was said, a coverage pass that walks the record for what the tree missed, a conflict pass with no drafting job, the builder grilled so the expert sits through fewer questions, and a review session where the expert corrects a paraphrase instead of composing an answer.

**`to-scope` resumes.** Five passes over a record do not fit in one sitting, and the expert is
rarely free on drafting day. Re-invoke it and it reads the tree, works out which pass never
finished, and starts there — re-drafting nothing, renumbering nothing, and re-asking nobody.

### Model-invoked

- [`workbench`](./skills/workbench/SKILL.md) — coordinate explicitly requested durable work from persisted state, with proportional routing, proof, resumability, and session closure.
- [`code-review`](./skills/code-review/SKILL.md) — review a branch or worktree against both repository standards and its originating specification.
- [`diagnosing-bugs`](./skills/diagnosing-bugs/SKILL.md) — diagnose difficult bugs and performance regressions with an evidence-driven loop.
- [`prototype`](./skills/prototype/SKILL.md) — build a throwaway prototype to answer a focused design question.
- [`research`](./skills/research/SKILL.md) — resolve a question from high-trust primary sources.
- [`resolving-merge-conflicts`](./skills/resolving-merge-conflicts/SKILL.md) — resolve an active merge or rebase conflict safely.
- [`tdd`](./skills/tdd/SKILL.md) — develop behavior test-first at meaningful public seams.

Nine additional candidates live under [`review-for-workbench`](./review-for-workbench/INVENTORY.md).
They are intentionally excluded from the installable skill tree until their useful behavior is
incorporated or they are retired.

## Working on this repo

Clone it, then link every skill into your local agent directories as junctions, so edits are live:

```powershell
.\scripts\link-skills.ps1
```

Conventions for adding a skill live in [CLAUDE.md](./CLAUDE.md).

## Credit

The repository shape and several retained engineering workflows were adapted from
[mattpocock/skills](https://github.com/mattpocock/skills), then narrowed and made self-contained
for this pack.

## Licence

MIT
