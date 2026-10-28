---
name: setup-repo
description: "Configure repository workflows, discoverable agent guidance, durable knowledge locations, and housekeeping."
disable-model-invocation: true
---

# Setup Repo

Scaffold the per-repo configuration that the engineering skills assume:

- **Issue tracker**: where issues live (GitHub by default; local markdown is also supported out of the box)
- **Triage labels**: the strings used for the two category roles and five state roles
- **Domain docs**: where `GLOSSARY.md` and ADRs live, and the consumer rules for reading them
- **Current knowledge**: one short index to architecture, module, data-model and decision knowledge, reusing suitable locations
- **Housekeeping**: a temporary workspace and a short policy for maintained checks, disposable validation and ownership

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write.

For local tracking, read [the shared work-record contract](WORK-RECORDS.md) before configuring authority or artifact locations. Use the accepted repository convention when present. New local setups use stable `work/<effort>/` folders, separate `tickets/` and `decisions/`, and the shared coordinator. Preserve existing labels, domain docs and historical paths. Explicit legacy references normalize in place; relocation requires the separately reviewed adoption procedure in the shared contract, never an automatic setup migration.

## Process

### 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config`: is this a GitHub repo? Which one?
- Instruction entry points used by Codex, including applicable overrides, pointers and nested scope. Preserve existing instruction files and trace how Codex reaches repository-wide guidance instead of choosing by filename.
- `GLOSSARY.md` and `GLOSSARY-MAP.md` at the repo root
- `docs/adr/` and any `src/*/docs/adr/` directories
- Prior setup output, including custom paths linked from instructions; do not assume `docs/agents/` is its authority
- Existing documentation indexes, architecture/module/data-model records, decisions, editable diagrams and maintained synthetic fixtures
- `work/`: a sign that a local-markdown issue tracker convention is already in use
- Existing temporary-workspace conventions, ignore rules and project verification commands
- Is the `triage` skill installed? (a `triage` skill folder alongside this one, or `triage` in your available skills.) This decides whether Section B runs at all.
- Monorepo signals: a `pnpm-workspace.yaml`, a `workspaces` field in `package.json`, or a populated `packages/*` with its own `src/`. These are present only in a genuinely large multi-package repo; their absence means single-context, which is almost every repo.

### 2. Present findings and ask

Summarise what's present and what's missing. Then take the sections in order. One section, one answer, then the next.

An existing configured authority takes precedence over defaults and the code remote. Preserve its paths, content and user edits, including edits inside generated sections. Present only missing additions or a precise proposed diff. Reuse equivalent guidance; conflicting policies need explicit reconciliation rather than replacement or a second policy. A prior approved choice needs no new question.

Lead each section with the recommended answer so the user can accept it in a word. Give a one-line explainer only when the choice genuinely branches; skip the section entirely when exploration already settled it (Section B when `triage` isn't installed, Section C when there's no monorepo).

**Section A: Issue tracker.**

> Explainer: The "issue tracker" is where issues live for this repo. Skills like `to-tickets`, `triage`, and `to-spec` read from and write to it. They need to know whether to call `gh issue create`, write a markdown file under `work/`, or follow some other workflow you describe. Pick the place you actually track work for this repo.

For new or missing tracker configuration, use the code remote as a suggested default: propose GitHub for a GitHub remote or GitLab for a GitLab remote (`gitlab.com` or a self-hosted host). Otherwise (or if the user prefers), offer:

- **GitHub**: issues live in the repo's GitHub Issues (uses the `gh` CLI)
- **GitLab**: issues live in the repo's GitLab Issues (uses the [`glab`](https://gitlab.com/gitlab-org/cli) CLI)
- **Local markdown**: issues live as files under `work/<effort>/` in this repo (good for solo projects or repos without a remote)
- **Other** (Jira, Linear, etc.): ask the user to describe the workflow in one paragraph; the skill will record it as freeform prose

Record approved changes in the existing tracker reference; use `docs/agents/issue-tracker.md` for new configuration without a chosen path. New GitHub and GitLab configurations keep the templates' "PRs as a request surface" flag **off**. Users can enable it later; preserve its existing value on reruns.

For GitHub or GitLab, read [REMOTE-WORK.md](REMOTE-WORK.md) and preserve its remote authority and unsupported automatic-concurrency boundary in the generated configuration. Record the GitLab host/project explicitly too.

For GitHub, record the selected issue repository as an explicit `owner/repo`, even when it matches the git remote. A project can keep its issues in a different repository, for example a private issues repository for a public app. Make the generated `gh` commands and API paths target that issue repository. PR discovery, if enabled later, remains scoped to the code repository.

**Section B: Triage label vocabulary.** Skip this section entirely if the `triage` skill isn't installed (exploration told you), since an uninstalled skill needs no labels.

For a new or missing label mapping, ask exactly one question:

> Do you want to keep the default triage labels? (recommended: **yes**)

The defaults are the two category roles (`bug`, `enhancement`) and five state roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), each mapped to an identical label string. On **yes**, write them as-is. Only if the user says no, usually because their tracker already uses other names (e.g. `bug:triage` for `needs-triage`), collect the overrides so `triage` applies existing labels instead of creating duplicates.

**Section C: Domain docs.** Reuse the configured layout. For new or missing configuration, recommend **single-context** (one `GLOSSARY.md` + `docs/adr/` at the repo root) in the setup draft without a separate question.

When choosing a new layout, offer **multi-context** (a root `GLOSSARY-MAP.md` pointing to per-context `GLOSSARY.md` files) only when exploration found monorepo signals. Then confirm which layout they want.

**Section D: Housekeeping.** Read [housekeeping setup](HOUSEKEEPING-SETUP.md). Reuse an established workspace or propose the dedicated fallback. Include the baseline and adapted reference in the same setup review; avoid a separate questionnaire when discovery settles the choice.

**Section E: Current knowledge.** Read [knowledge placement](KNOWLEDGE-SETUP.md). Reuse a suitable index and documentation locations; propose only missing content and the conditional index pointer in the same review.

### 3. Confirm and edit

Show the user a draft of:

- The `## Agent skills` additions and minimal Codex instruction connection (step 4), preserving existing scope
- Missing additions to the configured tracker, domain and label references (default paths below apply only to new configuration)
- The housekeeping baseline, temporary root, narrow ignore rule and `docs/agents/housekeeping.md` reference with its conditional service and recovery branches
- The current-knowledge index, chosen locations, conditional pointer and any targeted Git-visibility correction

Let them edit before writing.

### 4. Write

**Connect the Codex instruction entry point:** Keep one authoritative repository-wide guidance source, normally the existing source. Preserve existing instructions and scope. Include any new connection in the reviewed draft; avoid cycles and duplicate policy blocks.

| Existing structure | Smallest proposed connection |
| --- | --- |
| `CLAUDE.md` owns shared guidance | Keep it authoritative; connect Codex's loaded entry point with an explicit instruction to read that file for shared repository guidance. |
| Codex's loaded entry point owns shared guidance | Keep it authoritative; no extra connection is needed. |
| Both have independent content | Preserve both; add only the missing connection to the chosen shared source, respecting narrower scope. |
| No shared source exists | Recommend `AGENTS.md` as the shared source; confirm this in the setup draft. |
| An override or existing pointer already connects them | Reuse it after checking its scope and discovery; do not append a second connection. |

If an `## Agent skills` block already exists, merge the approved additions in place. Preserve existing user edits inside and outside the block; do not regenerate whole sections from templates. Keep core obligations inline in the shared source and branch details behind conditional pointers.

The block (use the configured paths in place of these defaults):

```markdown
## Agent skills

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Domain docs

[one-line summary of layout: "single-context" or "multi-context"]. See `docs/agents/domain.md`.
```

Add the reviewed housekeeping baseline after this block.

Add a brief current-knowledge pointer using the chosen index path: `For architecture, module, data-model or decision context, follow the relevant entry in [current knowledge](<index-path>).` Ordinary edits need no index read.

For new or missing label configuration, include the `### Triage labels` sub-block and write the configured label reference (default `docs/agents/triage-labels.md`) only when `triage` is installed and Section B ran. Preserve existing configuration on reruns.

When Section B ran on GitHub or GitLab, create each configured label the tracker lacks (`gh label create` / `glab label create`).

For new configuration, use the seed templates as a starting point. Existing authoritative files and custom paths remain in place:

- [issue-tracker-github.md](./issue-tracker-github.md): GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md): GitLab issue tracker
- [issue-tracker-local.md](./issue-tracker-local.md): local-markdown issue tracker
- [triage-labels.md](./triage-labels.md): label mapping (only if `triage` is installed)
- [domain.md](./domain.md): domain doc consumer rules + layout
- [housekeeping.md](./housekeeping.md): temporary placement, lifetime and retention rules with conditional service and recovery branches, adapted through [housekeeping setup](HOUSEKEEPING-SETUP.md)

For a newly configured "other" issue tracker, write its reference from the user's description at the chosen path (default `docs/agents/issue-tracker.md`).

### 5. Verify and report

Verify every published local reference resolves from its document and the intended permanent documents are Git-visible with `git check-ignore` and `git status --untracked-files=all`. Check disposable contents are ignored and unrelated protected/generated paths retain their rules. A broad ignore conflict needs a targeted reviewed exception for the exact permanent paths and necessary parent traversal; never unignore an entire protected tree. On repeated setup, check preserved content and absence of duplicate sections/connections.

After all approved instruction and reference writes are complete, start a fresh Codex session with a neutral repository task that neither supplies the policy nor requests a named instruction-file read. Observe discovery and the source reached; check nested scope where applicable. A filename or a successful explicit read is not fresh-session discovery evidence. If the runtime is unavailable, report discovery as unresolved instead of inferring it from file inspection. Additional runtime setup and validation are outside this flow.

Report the configured locations, Codex discovery outcome and any unresolved observation. Setup is complete only for the outcomes verified. Mention the user can edit the configured references directly; re-running adds missing configuration while preserving their choices. Keep dependency/evaluation controls outside ordinary repository guidance.
