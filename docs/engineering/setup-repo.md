## What it does

`/setup-repo` configures the repo conventions the engineering skills consume: issue tracking, triage labels, domain docs, and housekeeping. It records the answers as markdown files under `docs/agents/`. For GitHub, it records the issue repository explicitly, which may differ from the code repository.

Those files are the only thing that varies between repos. The skills themselves are identical everywhere. They read `docs/agents/issue-tracker.md` at run time and do what it says. That is why the set is not tied to GitHub, and why you never edit a skill file to point it at another tracker. Invoking it with "link the skills to a custom issue tracker" works with anything you can connect to programmatically, with no changes to the skills.

It is a prompt-driven skill, not a deterministic script. It reads your `git remote`, `CLAUDE.md` and `GLOSSARY.md`, proposes what it found, and waits for you to confirm before it writes anything.

Local tracking uses stable effort folders and separate implementation issues and Wayfinder decisions. A shared coordinator reads one declared checkout across worktrees and validates ownership. Existing repository conventions and historical paths are preserved. Explicit legacy records can be read without relocation. Optional migration produces a classification and reference plan for review, preserves original IDs through forwarding references, and checks unchanged inputs before applying. Participating tools must adopt the shared resolver before moving records; ordinary setup never moves historical work. See the [legacy adoption procedure](../../skills/engineering/setup-repo/WORK-RECORDS.md#explicit-legacy-inputs-and-reviewed-adoption).

Remote GitHub and GitLab records remain authoritative. Assignment shows intent but does not prove exclusive ownership. Automatic concurrent claiming is unavailable unless an exclusive provider path or one shared controller has been established and verified; unavailable remote information stops work instead of falling back to local status.

## When to reach for it

You invoke this by typing `/setup-repo`; the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) won't reach for it on its own. Its metadata marks it non-invokable on purpose, so no other skill can fire it for you.

Reach for it once per repo, before the first use of any other engineering skill. If [triage](https://aihero.dev/skills-triage), [to-spec](https://aihero.dev/skills-to-spec), [to-tickets](https://aihero.dev/skills-to-tickets) or [wayfinder](https://aihero.dev/skills-wayfinder) start guessing where your issues go, or apply labels your tracker doesn't have, this repo has not been set up yet. You can run it in a repo halfway through a project. The skill reads what is already there, so no earlier work is lost.

## Prerequisites

It writes into the repo you run it in:

| It writes | Where |
| --- | --- |
| `issue-tracker.md` | `docs/agents/` |
| `domain.md` | `docs/agents/` |
| `triage-labels.md` | `docs/agents/`, only when the `triage` skill is installed |
| `housekeeping.md` and its conditional service and recovery branches | `docs/agents/`, or the existing authoritative location |
| A narrow temporary-output ignore rule | the existing ignore configuration |
| An `## Agent skills` block and short housekeeping baseline | the existing agent instruction file, with its loading path verified |

You commit all of it as markdown. There is no user-level or global mode. The config lives in the repo, so every repo gets its own copy.

The local work-record helpers require Python with PyYAML and a Git checkout. They use the shared Git administrative directory to coordinate participating worktrees; no remote is required. Tool installation stays in the [repository installation instructions](../../README.md).

## The setup decisions

It starts each section with the recommended answer, and skips any question its exploration already answered. Most runs need only two confirmations.

| Decision | What it proposes | When it asks |
| --- | --- | --- |
| **Issue tracker** | the one matching your `git remote` | when not already selected or configured |
| **Triage labels** | keep two category names (`bug`, `enhancement`) and five state names (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) | only if the `triage` skill is installed |
| **Domain docs** | single-context: one `GLOSSARY.md` plus `docs/adr/` at the root | only if it spots monorepo signals, and then it offers a multi-context `GLOSSARY-MAP.md` |
| **Housekeeping** | reuse a suitable temporary workspace or establish an isolated subtree | present the chosen root, narrow ignore rule and guidance in the setup draft |

The tracker options:

| Option | Where issues live | Needs |
| --- | --- | --- |
| **GitHub** | the repo's GitHub Issues | the `gh` CLI |
| **GitLab** | the repo's GitLab Issues | the `glab` CLI |
| **Local markdown** | files under `work/<effort>/` in this repo | Python, PyYAML, and a Git checkout; no remote |
| **Other** | wherever you say | one paragraph from you describing the workflow |

The first three ship as templates in the skill and work out of the box. Local markdown is a full option, not a fallback. The skill supports a solo project with no remote. Choose one configured issue-tracker authority; hosting code on GitHub does not preclude tracking its work in local Markdown.

"Other" is a full option too. It is how Jira, Linear, Azure DevOps and Beads all work. You describe the workflow, the skill records your prose in `docs/agents/issue-tracker.md`, and the downstream skills follow the prose. Users have already built this: a Jira-over-[MCP](https://www.aihero.dev/ai-coding-dictionary/mcp) variant, a Gitea CLI shaped like `gh`, a hand-built local dashboard.

## Maintained checks and disposable validation

A reusable lint rule or regression test belongs in the maintained project tooling. A one-off script answers the current question and is removed when it is no longer needed. Generated reports and data have their own lifetime even when the checker is permanent.

Setup records one temporary root with task-isolated directories and narrowly scoped ignore rules. Existing scratch notes and durable effort records remain where they are. Ordinary edits use a short persistent baseline; only temporary or resumed work loads the fuller reference. Process and Docker work loads a separate service branch, uses native teardown, and records exact ownership for interrupted work. Interrupted tasks locate one recovery note through the configured root or repository-specific OS temporary namespace. Recovery verifies prior-owner inactivity and current ownership before cleanup; unknown or active resources remain reported and untouched. Shared services and persistent data remain protected. Unconfigured work can use an owned OS temporary directory and suggest setup once. Setup adds a lasting convention without becoming a prerequisite for every edit.

## Common questions

**Do I have to use GitHub?**

No. GitHub, GitLab and local markdown under `work/` all ship as ready-made templates, and anything else works through the "other" path. This is the most-repeated question, in roughly these words: *"hard locked to github"*, *"can I use GitLab / Jira"*, *"what about Azure DevOps"*. The answer is always the same: setup chooses the tracker, not the skill.

**Do I need to re-run it after updating the skills?**

Re-run it to add a missing configuration section or refresh a changed convention. Setup preserves existing choices and user edits, rather than appending another copy. The temporary workspace and narrow ignore rule are included in the same review as the other configuration.

**It wrote to `CLAUDE.md`, but I'm on Codex.**

Setup still prefers an existing `CLAUDE.md`, then `AGENTS.md`. For housekeeping it also checks that the chosen file is actually loaded, directly or through a pointer. When that connection is missing, it includes the smallest pointer correction in the reviewed draft instead of silently duplicating the policy. If neither file exists, it asks which to create.

**Did it create my triage labels?**

When `triage` is installed and the tracker is GitHub or GitLab, setup creates the configured category and state labels that are missing. `docs/agents/triage-labels.md` records the mapping that later skills read. Setup does not create [wayfinder](https://aihero.dev/skills-wayfinder)'s `wayfinder:map` and `wayfinder:<type>` labels; create those before the first wayfinder run.

**Can I configure the other skills' behaviour here ([grilling](https://www.aihero.dev/ai-coding-dictionary/grilling) cadence, question format, tone)?**

It configures tracker, labels, domain-doc layout and housekeeping. General tone or interview preferences remain outside its scope. Users have asked to make it the place for per-user preferences. The answer is that skills stay opinionated and take no per-user config. Preferences belong in your `CLAUDE.md` as plain instructions, which every skill already reads.

**Can I keep the config in `~/.claude` instead of committing it to every repo?**

Not today. A user who runs the skills across many repos has an open request for this, but no user-level mode exists. Every repo carries its own `docs/agents/`.

**Isn't it strange to have a skill that configures the other skills?**

One long-standing complaint says yes, in these words: *"having a skill to set up the other skill does not feel right to me: that means the LLM is configuring its own skills."* The trade-off is real. Without a setup step, every skill that touches issues would need its own copy of the tracker instructions. The output is markdown you can read and edit, and that limits the risk. You can read every file it wrote and change it by hand. Make day-to-day changes that way, not with another run.

## It's working if

- `docs/agents/issue-tracker.md` and `docs/agents/domain.md` exist, plus `triage-labels.md` if `triage` is installed.
- An `## Agent skills` section appears in the instruction file your harness reads, with a one-line summary pointing at each of those files.
- The recorded tracker is the one you selected, which may differ from the git remote, and the label strings match labels that exist in that tracker.
- For GitHub, `docs/agents/issue-tracker.md` names the exact issue repository. If it differs from the code repository, issue commands target the recorded repository.
- Afterwards, `/to-tickets` publishes without asking you where issues live, and `/triage` applies labels rather than inventing them.
- Maintained checks remain available, and completed one-off validation leaves no unexplained files in the repo.
- Completed service checks release their owned processes and disposable Docker resources while shared services stay available; failed cleanup remains visible in a scoped recovery note.
- A new session can find an interrupted task's recovery note without lost conversation IDs; unresolved ownership remains visible.
- An ordinary edit does not trigger a housekeeping scan or a separate report.
- Nothing in the skill files themselves changed. If setup edited a `SKILL.md`, something went wrong.

## Where it fits

`setup-repo` is the **run-once setup** for the engineering flow, the precondition everything else assumes rather than a step in the chain. Its neighbours are its readers: [triage](https://aihero.dev/skills-triage), which applies the label vocabulary written here; [to-spec](https://aihero.dev/skills-to-spec) and [to-tickets](https://aihero.dev/skills-to-tickets), which publish into the tracker named here; and [wayfinder](https://aihero.dev/skills-wayfinder), which reads the "Wayfinding operations" section of the same tracker file to learn how to store maps and child [tickets](https://www.aihero.dev/ai-coding-dictionary/ticket). [domain-modeling](https://aihero.dev/skills-domain-modeling) later fills in the domain-doc layout that setup records. It creates `GLOSSARY.md` and ADRs only when you resolve a term or decision, so a repo with no domain docs after setup is normal. For which skill to reach for next, [guide-me](guide-me.md) routes the whole set.
