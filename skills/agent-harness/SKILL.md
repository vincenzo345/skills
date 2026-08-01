---
name: agent-harness
description: >-
  Scaffold a reusable, stack-agnostic long-running build harness into any project — the
  Planner→Generator→Evaluator loop where three agents with separate context windows coordinate
  through files on disk and an adversarial Evaluator verifies every sprint instead of the builder
  grading itself. Use whenever the user wants to set up an autonomous or long-running build loop, a
  generator/evaluator (adversarial) harness, contract-negotiated sprints, a self-verifying agent
  scaffold, or wants to ADD a feature to a project that already has this harness. Triggers on requests
  like "set up the harness", "scaffold a generator-evaluator loop", "make my project build and
  self-verify itself", "give me the long-running agent infrastructure", "add a feature via the
  harness", or "reuse that harness on a new project" — even if they don't name the pattern exactly.
  Reach for it any time the goal is durable build infrastructure Claude runs for hours per sprint.
---

# Agent Harness

This skill scaffolds a **Planner → Generator → Evaluator** build harness into a project and lets you
extend it later. The harness is the reusable asset: the same infrastructure drops into any project
(web app, game, CLI, data pipeline, library) because only two things are project-specific — the
build/test commands and how the Evaluator *exercises* the finished artifact. Everything else is
identical every time.

Read `references/pattern.md` if you want the full "why" behind the design before scaffolding; it's
short and explains what each piece defends against. You don't need it to run the skill.

## Two modes

- **init** — stand up a fresh harness in a new (or existing) project directory.
- **enhance** — add new sprints to a project that already has the harness (feature work / iteration).

Figure out which the user wants from context. "Set it up / scaffold it / new project" → init.
"Add X to the app / next feature / another sprint" in a harnessed repo → enhance.

## Mode: init

### 1. Interview (do this before writing anything)

The whole loop's quality rides on these answers, so gather them first. Ask in one batch; infer sensible
defaults from the repo (read `package.json`, build files, README) and only ask what you can't infer.

1. **What are we building?** One or two sentences — the brief/pitch.
2. **Stack & how artifacts are built** (language, framework, how a runnable build is produced).
3. **Build command** and **test command** (what you'd run by hand). These become `ci/build.sh` / `ci/test.sh`.
4. **How should the Evaluator EXERCISE the result** — the most important question. Not "read the code,"
   but actually use it: drive a browser via the Playwright/Chrome MCP, run the CLI on fixtures, hit the
   API, diff output against a golden file, screenshot the UI. Be concrete; this text goes verbatim into
   the Evaluator's job.
5. **Invariants** — properties that must hold across the whole build (e.g. "all state flows through one
   reducer," "generation is deterministic given a seed," "no PII leaves the process"). These are what
   the Evaluator polices hardest.
6. **Rubric dimensions** — 3–5 weighted axes of "good" for this project, each with a couple of concrete
   criteria. Weight toward what the user will experience most. Include a pass threshold (default 7.5/10).
7. **Sprints** — the high-level sequence. Keep it high-level and prove each core capability ONCE before
   widening (if there's a repeating unit, do one as the template). This is the Planner's job, so you can
   either draft sprints now or leave `sprints` minimal and let the planner subagent expand it on first run.

If the user is vague, propose a draft of 5–8 and let them correct it — don't block on perfect answers.

### 2. Assemble the config and scaffold

Write the answers into a `harness.config.json` (schema below), then run the bundled scaffolder — it's
deterministic and writes the whole tree so you don't hand-author boilerplate:

```bash
python3 <skill-dir>/scripts/scaffold.py init --target <project-dir> --config harness.config.json
```

Config schema:

```json
{
  "project_name": "string",
  "pitch": "one–two sentence brief",
  "stack_notes": "language / framework / how a runnable build is produced",
  "build_cmd": "the shell command that builds",
  "test_cmd": "the shell command that runs tests",
  "exercise": "concrete instructions for how the Evaluator uses the artifact (goes into evaluator.md)",
  "pass_threshold": 7.5,
  "invariants": ["...", "..."],
  "rubric_dimensions": [
    {"name": "Correctness", "weight": 0.4, "criteria": ["concrete check", "concrete check"]}
  ],
  "sprints": [
    {"id": 1, "name": "short name", "goal": "one sentence", "demoable_as": "the observable proof"}
  ]
}
```

### 3. Finish setup and hand off

After scaffolding, do the mechanical finishing so the user can run immediately:

- `cd <project-dir> && git init && git add -A && git commit -m "scaffold harness"` (the loop tags and
  commits per sprint; git must exist).
- Sanity-check that `ci/build.sh` and `ci/test.sh` actually run in this repo; fix the wrapped commands
  if not. **Prove the build once by hand before any real run** — a broken build wrapper makes every
  Evaluator round fail and burns tokens.
- If the Evaluator drives a browser, remind the user to add the browser MCP
  (`claude mcp add playwright -- npx @playwright/mcp@latest`), since the Evaluator can't just read code.
- Tell them to drop 2–6 calibration examples in `.harness/references/` — the highest-leverage quality
  lever.
- Show them how to run: `python3 orchestrator/run_harness.py --dry-run` (preview, spends nothing), then
  `/harness-run 1` interactively (watch one sprint, build trust) before letting the whole thing run —
  either `/harness-run` or, hands-off, `nohup python3 orchestrator/run_harness.py &`.

## Mode: enhance

For a project that already has the harness, adding a feature is just more sprints:

1. Draft the new sprints with the user (same shape: `name`, `goal`, `demoable_as`). Keep them high-level.
2. Write them to a `new-sprints.json` (a JSON array of sprint objects; ids are assigned automatically).
3. Append them and reset the run cursor:
   ```bash
   python3 <skill-dir>/scripts/scaffold.py add-sprints --target <project-dir> --sprints new-sprints.json
   ```
4. If the feature changes what "good" means or adds an invariant, edit `.harness/rubric.md` /
   `.harness/plan.json` invariants accordingly — the Evaluator reads these fresh each round.
5. Run from the first new sprint: `/harness-run <N>` or `python3 orchestrator/run_harness.py --start <N>`.

Passed sprints are skipped, so re-running is safe; the harness picks up exactly where it left off.

## What the scaffolder writes

```
CLAUDE.md                     loop spec + invariants + how-to-build/exercise (every agent reads this)
.claude/agents/{planner,generator,evaluator}.md   the three roles (separate context windows)
.claude/commands/harness-run.md                   /harness-run orchestrator command
.claude/settings.json         tool permission allow/deny (safer than skip-permissions)
.gitattributes                pins *.sh to LF (autocrlf breaks ci scripts on `git reset --hard`)
.harness/plan.json            sprints        .harness/progress.json   pass/pending state
.harness/rubric.md            weighted rubric .harness/contract.json   negotiated per-sprint criteria
.harness/journal.jsonl        breadcrumb log  .harness/references/     calibration examples
.harness/traces/              full per-role transcripts, written by each headless run
ci/build.sh  ci/test.sh       thin wrappers around the project's build/test
orchestrator/run_harness.py   headless driver (spawns `claude -p` per role; separate contexts)
```

If the target already has a `CLAUDE.md` or `.claude/settings.json`, the scaffolder writes
`*.harness-new` files next to them instead of overwriting — merge those by hand (or do it for the
user) before the first run.

## Headless gotchas (check these before the first real run)

Hard-won on real projects; each one silently stalls or corrupts a run if missed:

1. **Trust the project first.** Headless `claude -p` IGNORES the project's `.claude/settings.json`
   until the project is trusted — every agent then stalls on "requires approval". Fix: open `claude`
   interactively in the project once and accept the trust prompt (or set
   `hasTrustDialogAccepted: true` for the project dir in `~/.claude.json`).
2. **Windows: use `python`, not `python3`** — `python3` usually isn't on PATH there. All commands in
   this skill and the orchestrator docstring accept either.
3. **Per-role models work headless.** The orchestrator reads each agent's `model:` frontmatter and
   passes `--model`, so a cheap generator + strong evaluator split actually takes effect in headless
   runs. Set models in `.claude/agents/*.md`, not in the orchestrator.
4. **Run one sprint at a time while calibrating:** `python orchestrator/run_harness.py --only N`
   runs exactly sprint N and stops — the cost-control mode. `--start N` runs from N to the end.
5. **Read the traces.** Every role invocation's full transcript lands in `.harness/traces/`; that is
   what you read to tune the rubric and role prompts between runs.

## Guidance to pass on to the user

The harness fills the model's current gaps; as models improve you delete scaffolding (raise the loop
caps, drop sprint decomposition, merge roles). Steer a run by editing the rubric and role prompts, not
by hand-holding — that "read the traces, tune the prompt" loop is the actual work. And the first run on
any project mostly exposes gaps in *your prompts*, so treat run one as calibration. `references/pattern.md`
has the fuller version of this if they want it.
