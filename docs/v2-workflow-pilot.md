# V2 workflow pilot

This is branch `v2` of `vincenzo345/skills`. It retains this repository's `main` ancestry and imports the exact tree of Matt Pocock's `main` at `f3fc5632f401156837ee3872f14fe33ccf1024ea`, fetched on 2026-10-07. Matt's repository is a read-only source for this experiment; changes and pushes belong to `vincenzo345/skills`. The prior uncommitted `main` work was saved in a local stash before switching this checkout to `v2`.

## Route to test

1. Establish a shared problem and vocabulary with `grill-with-docs`. Use `wayfinder` only when the decision route cannot fit one session. A wayfinder ticket resolves a question, not a build slice.
2. Gather requirements. For an expert/builder meeting export, use `to-record` to preserve the source and `to-scope` to produce expert-corrected scope. Both are promoted in this branch. For other sources, use the relevant discovery method. Keep the high-level problem statement distinct from transcript evidence and confirmed scope.
3. Design the smallest solution, using prototypes and domain/module design when they answer a real uncertainty. Bootstrap or audit the project's GitHub, local checks, CI, deployment and observability before the first feature PR.
4. Use `to-spec` and `to-tickets` only for a build that needs them; implement bounded slices with TDD, review the diff, require deterministic CI and verify the released revision.
5. Use `show-me` when a visual helps the user inspect a decision or handoff. Use `retro` after a meaningful run to propose one evidence-backed improvement to checks, instructions or tooling.

Incoming app tickets have a separate on-ramp: backend validation and GitHub issue creation, triage, an authorized agent-ready trigger, isolated agent PR, required CI/review, rollout and user-ticket update. The app connector and agent worker are future pilot slices, not capabilities this branch currently provides.

## Installed v2 package

The package promotes 29 skills. `show-me`, `to-record`, and `to-scope` were added to Matt's baseline; `wait-what` was removed. The older Workbench implementation is archived at `skills/deprecated/workbench` and is not installed. Codex uses junctions to this checkout. Claude Code uses the `skillsrepo-v2@skillsrepo-v2` plugin from a clean snapshot of this branch. The old official Matt plugin and global Workbench entry points were removed from this machine.

The deterministic package check is `scripts/validate_v2_skills.py`, run by `.github/workflows/validate-v2.yml` on v2 pushes and PRs. It checks promoted manifest membership, skill identity, dual-host invocation policy, README links and docs-page presence. The workflow also runs the `to-record` preservation tests and Windows installer safety tests. `v2` requires both CI jobs and a PR. [A deliberately broken PR](https://github.com/vincenzo345/skills/pull/1) failed the skill-package job and GitHub marked it blocked; the PR was closed without merging. These checks validate packaging, not skill outcomes or a target application's behavior.

## Next proof before expansion

Choose one bounded application task with frozen requirements and an independent acceptance check. Run the v2 route and record correctness, rework, elapsed time, token use and human interruptions. Add application-specific CI before relying on agent PRs, and add only the specialist skill that a task exposes as missing. Automated issue-to-PR execution remains a future integration after those proofs.
