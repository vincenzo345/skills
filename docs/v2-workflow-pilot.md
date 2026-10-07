# V2 workflow pilot

This branch starts from Matt Pocock's `main` at `f3fc5632f401156837ee3872f14fe33ccf1024ea`, fetched on 2026-10-07. It is an isolated experiment. The existing Skillsrepo and the earlier `workflow-pilot-20261007` worktree remain separate.

## Route to test

1. Establish a shared problem and vocabulary with `grill-with-docs`. Use `wayfinder` only when the decision route cannot fit one session. A wayfinder ticket resolves a question, not a build slice.
2. Gather requirements. For an expert/builder meeting export, use Skillsrepo's `to-record` to preserve the source and `to-scope` to produce expert-corrected scope. For other sources, use the relevant discovery method. Keep the high-level problem statement distinct from transcript evidence and confirmed scope.
3. Design the smallest solution, using prototypes and domain/module design when they answer a real uncertainty. Bootstrap or audit the project's GitHub, local checks, CI, deployment and observability before the first feature PR.
4. Use `to-spec` and `to-tickets` only for a build that needs them; implement bounded slices with TDD, review the diff, require deterministic CI and verify the released revision.
5. Use `show-me` when a visual helps the user inspect a decision or handoff. Use `retro` after a meaningful run to propose one evidence-backed improvement to checks, instructions or tooling.

Incoming app tickets have a separate on-ramp: backend validation and GitHub issue creation, triage, an authorized agent-ready trigger, isolated agent PR, required CI/review, rollout and user-ticket update. The app connector and agent worker are future pilot slices, not capabilities this branch currently provides.

## First thin slice

`show-me` is the first branch-local addition. It is explicitly user-invoked in Claude and Codex metadata, listed in the plugin manifest, router, catalog READMEs and docs. The first trial should ask for a visual of a real decision or session handoff, then check that the view is concise, source-faithful and useful to the user. This trial does not establish that the full development workflow improves outcomes.

## Next proof before expansion

Choose one bounded application task with frozen requirements and an independent acceptance check. Run the Matt v2 route and the current Workbench route against the same task and record correctness, rework, elapsed time, token use and human interruptions. Prove a deliberately failing CI check blocks a PR before adding automated issue-to-PR execution. Add only the specialist skill that a task exposes as missing.
