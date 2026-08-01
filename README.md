# Skills

My agent skills — the ones I actually use. Written for Claude Code and Codex.

Every skill here is one I wrote and understand. The set is small on purpose and grows one finished skill at a time.

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

### Model-invoked

- [`agent-harness`](./skills/agent-harness/SKILL.md) — scaffold a stack-agnostic long-running build harness into any project: the Planner/Generator/Evaluator loop where three agents with separate context windows coordinate through files on disk, and an adversarial Evaluator verifies every sprint instead of the builder grading itself.

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
