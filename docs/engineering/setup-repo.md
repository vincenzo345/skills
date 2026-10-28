## What it does

`/setup-repo` configures issue tracking, triage labels, domain docs, current-knowledge locations and housekeeping. It reuses existing authorities and user edits, including custom documentation paths, rather than replacing them with defaults. New configuration normally lives under `docs/agents/`.

Those references vary between repos; the skills themselves are identical everywhere. They follow the configured tracker authority at run time. That is why the set is not tied to GitHub, and why you never edit a skill file to point it at another tracker. Invoking it with "link the skills to a custom issue tracker" works with anything you can connect to programmatically, with no changes to the skills.

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
| One short current-knowledge index | an existing suitable index, or `docs/README.md` |
| An `## Agent skills` block, concise survival/ownership baseline and conditional knowledge pointer | one shared instruction source, connected to the entry points used by Codex and Claude |

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
| **Current knowledge** | reuse an index and suitable architecture/module/data-model/decision locations | review missing content and the conditional pointer, creating documents only when useful content exists |
| **Instruction discovery** | the smallest compatible connections to one shared source | review missing connections; verify fresh discovery independently in each available runtime |

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

Setup records one temporary root with task-isolated directories and narrowly scoped ignore rules. Existing scratch notes and durable effort records remain where they are. Shared services and persistent data remain protected.

| Work | Guidance |
| --- | --- |
| Ordinary edit | Use the short persistent baseline. |
| Temporary validation | Load the fuller reference when needed. |
| Process or Docker work | Load the service branch, use native teardown, and record exact ownership for interrupted work. |
| Interrupted task | Find one recovery note through the configured root or repository-specific OS temporary namespace. Verify prior-owner inactivity and current ownership before cleanup; preserve and report unknown or active resources. |
| Unconfigured repository | Use an owned OS temporary directory and suggest setup once. |

Setup adds a lasting convention without becoming a prerequisite for every edit.

## Current knowledge without another tracker

The short index helps a contributor find only the design context needed for a task. It distinguishes the roles of current documentation while preserving existing locations:

| Role | What belongs there |
| --- | --- |
| Architecture | System responsibilities and runtime boundaries |
| Module design | Interfaces, dependencies, invariants and testing seams |
| Data-model design | Identity, relationships, integrity and lifecycle intent, linked to schemas and migrations |
| Decisions and domain | Existing ADRs own consequential choices; the glossary owns business meaning |

Plans, proposals, research and evidence stay in their stable effort. Accepted current knowledge links back to that evidence. Setup creates no empty design taxonomy and does not invent accepted decisions. Editable diagrams stay beside their document; reusable synthetic data stays with maintained fixtures.

Repeated setup preserves the index, tracker authority, existing instruction scope and user edits inside generated blocks. Permanent documents must be visible to Git. An ignore conflict is corrected only for the reviewed paths while unrelated private/generated content stays protected.

## Common questions

**Do I have to use GitHub?**

No. GitHub, GitLab and local markdown under `work/` all ship as ready-made templates, and anything else works through the "other" path. This is the most-repeated question, in roughly these words: *"hard locked to github"*, *"can I use GitLab / Jira"*, *"what about Azure DevOps"*. The answer is always the same: setup chooses the tracker, not the skill.

**Do I need to re-run it after updating the skills?**

Re-run it to add a missing configuration section or refresh a changed convention. Setup preserves existing choices and user edits, rather than appending another copy. The temporary workspace and narrow ignore rule are included in the same review as the other configuration.

**It wrote to `CLAUDE.md`, but I'm on Codex.**

Setup preserves one shared source and connects the entry points each runtime actually loads:

| Condition | Setup behavior |
| --- | --- |
| `CLAUDE.md` owns shared guidance | Keep it and connect Codex's loaded entry point to it. |
| `AGENTS.md` owns shared guidance | Keep it and connect Claude through a brief import in its loaded `CLAUDE.md`. |
| Both carry independent instructions | Preserve their content and scope; add only the missing connection. |
| Neither exists | Review a shared `AGENTS.md` with a brief `CLAUDE.md` import. |
| Existing override or pointer already connects them | Verify it and reuse it without another block. |

A fresh session receives a neutral repository task, without supplied policy or a request to read a named instruction file. Each runtime's observed discovery is recorded separately. File inspection and another runtime's success cannot prove it; an unavailable runtime remains unresolved.

**Did it create my triage labels?**

When `triage` is installed and the tracker is GitHub or GitLab, setup creates the configured category and state labels that are missing. `docs/agents/triage-labels.md` records the mapping that later skills read. Setup does not create [wayfinder](https://aihero.dev/skills-wayfinder)'s `wayfinder:map` and `wayfinder:<type>` labels; create those before the first wayfinder run.

**Can I configure the other skills' behaviour here ([grilling](https://www.aihero.dev/ai-coding-dictionary/grilling) cadence, question format, tone)?**

It configures repository workflow and knowledge locations. General tone or interview preferences remain outside its scope. Preferences belong in your existing repository instructions; setup preserves them and verifies the loading connections.

**Can I keep the config in `~/.claude` instead of committing it to every repo?**

Not today. A user who runs the skills across many repos has an open request for this, but no user-level mode exists. Each repo carries its own configuration at the chosen locations.

**Isn't it strange to have a skill that configures the other skills?**

One long-standing complaint says yes, in these words: *"having a skill to set up the other skill does not feel right to me: that means the LLM is configuring its own skills."* The trade-off is real. Without a setup step, every skill that touches issues would need its own copy of the tracker instructions. The output is markdown you can read and edit, and that limits the risk. You can read every file it wrote and change it by hand. Make day-to-day changes that way, not with another run.

## It's working if

- The configured tracker and domain references exist, plus the label mapping if `triage` is installed. New setups normally use `docs/agents/`.
- Fresh Codex and Claude sessions each discover the shared guidance, or the unavailable observation is reported explicitly.
- A short index points to current knowledge at the chosen paths, and all permanent references resolve and are visible to Git.
- Repeated setup preserves custom locations, user edits and unrelated ignores, without duplicate guidance blocks.
- The recorded tracker is the one you selected, which may differ from the git remote, and the label strings match labels that exist in that tracker.
- For GitHub, the tracker reference names the exact issue repository. If it differs from the code repository, issue commands target the recorded repository.
- Afterwards, `/to-tickets` publishes without asking you where issues live, and `/triage` applies labels rather than inventing them.
- Maintained checks remain available, and completed one-off validation leaves no unexplained files in the repo.
- Completed service checks release their owned processes and disposable Docker resources while shared services stay available; failed cleanup remains visible in a scoped recovery note.
- A new session can find an interrupted task's recovery note without lost conversation IDs; unresolved ownership remains visible.
- An ordinary edit does not trigger a housekeeping scan or a separate report.
- Nothing in the skill files themselves changed. If setup edited a `SKILL.md`, something went wrong.

## Where it fits

`setup-repo` is the **run-once setup** for the engineering flow, the precondition everything else assumes rather than a step in the chain. Its neighbours are its readers: [triage](https://aihero.dev/skills-triage), which applies the label vocabulary written here; [to-spec](https://aihero.dev/skills-to-spec) and [to-tickets](https://aihero.dev/skills-to-tickets), which publish into the tracker named here; and [wayfinder](https://aihero.dev/skills-wayfinder), which reads the "Wayfinding operations" section of the same tracker file to learn how to store maps and child [tickets](https://www.aihero.dev/ai-coding-dictionary/ticket). [domain-modeling](https://aihero.dev/skills-domain-modeling) later fills in the domain-doc layout that setup records. It creates `GLOSSARY.md` and ADRs only when you resolve a term or decision, so a repo with no domain docs after setup is normal. For which skill to reach for next, [guide-me](guide-me.md) routes the whole set.
