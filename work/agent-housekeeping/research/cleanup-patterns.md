# Agent housekeeping research

Researched 2026-10-23. Scope: primary-source examples of agent cleanup skills and resource lifecycle mechanisms. Sources were searched and opened; nothing was installed, tested, or started. This is source review, not proof that any skill reliably prevents agent litter across harnesses.

## Existing skills worth examining

### Testcontainers' own agent skills

The first-party [`testcontainers-go` skill](https://github.com/testcontainers/claude-skills/blob/main/plugins/testcontainers/skills/testcontainers-go/SKILL.md) requires registering `CleanupContainer` immediately after creation and before checking startup errors. It also shows `CleanupNetwork` and explains Ryuk as a second cleanup layer. This directly addresses a failure path where partial startup creates resources but an assertion exits before teardown registration.

Useful pattern: creation and cleanup registration are one operation from the agent's perspective. Limitation: this is a Go integration-testing skill, not a general repo housekeeping policy. It assumes containers are needed; it does not prevent unnecessary infrastructure creation. Its examples and versions still need project-specific review.

### General session cleanup skill

[`Guanff/claude-code-cleanup`](https://github.com/Guanff/claude-code-cleanup/blob/master/SKILL.md) catalogs temporary files, asks before deletion, then checks Git status and project integrity. Its scan categories include one-off dependencies, generated documents, test output, empty scaffolding, and temporary environments.

Useful pattern: show candidates and reasons before removing unknown leftovers. Limitations: filename and directory heuristics do not establish ownership; names like `test` or `output` can be legitimate deliverables. Its rule protecting all ignored paths also leaves many real temporary artifacts untouched. It focuses on filesystem cleanup, not Docker lifecycle. No behavioral evidence was verified. Treat as a survey example, not a recommended drop-in.

### Superpowers branch finishing

[`finishing-a-development-branch`](https://github.com/obra/superpowers/blob/main/skills/finishing-a-development-branch/SKILL.md) puts cleanup in the completion flow, preserves worktrees for ongoing PR review, and refuses to force worktree removal when modified or untracked files remain. It distinguishes externally managed workspaces.

Useful pattern: completion has explicit retention and cleanup outcomes, and untracked work is protected. Limitation: ownership is inferred from directory patterns. The project's [open issue #2397](https://github.com/obra/superpowers/issues/2397) reports that worktrees created in user-configured directories are misclassified as externally owned and leak. This is concrete evidence of a cleanup failure mode, not evidence the problem is resolved. Prefer recorded creation provenance over path-based ownership guesses.

## Mechanisms that solve narrower lifecycle problems

### Session ownership plus an external reaper

[Testcontainers .NET Resource Reaper documentation](https://dotnet.testcontainers.org/api/resource_reaper/) describes automatically assigning a session ID to Docker resources, grouping resources by session, and removing remaining resources after tests whether successful or unsuccessful. It currently documents Linux-container support. Keep the reaper enabled unless the environment already supplies cleanup.

[Moby Ryuk's README](https://github.com/testcontainers/moby-ryuk/blob/main/README.md) describes filtered removal of containers, networks, volumes, and images. Its protocol accepts label filters, and cleanup follows the last client connection closing after a configurable reconnection period. This moves cleanup outside the test process, so ordinary in-process teardown is not the sole mechanism.

Inference: a general agent component can reuse the architecture of explicit session ownership and a supervisor-owned cleanup path. It should not introduce a reaper container merely to clean up trivial scripts. An external reaper also depends on the Docker daemon and reaper remaining available; it is not a universal guarantee against every host failure.

### Framework-owned files and teardown

[pytest temporary-path documentation](https://pytest.org/en/latest/how-to/tmp_path.html) supplies a unique directory per test, and documents bounded retention of recent runs. This isolates outputs from source folders; it does not mean everything is deleted immediately.

[pytest fixture documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html#safe-teardowns) recommends pairing individual state-changing actions with their teardown. It warns that setup exceptions can leave state behind and explains finalizer registration. Useful pattern: cleanup is attached to acquired state as soon as applicable, rather than appended to a large setup sequence. Framework fixtures should be reused before adding bespoke cleanup scripts. Process termination remains outside ordinary fixture guarantees.

### Compose scope and teardown semantics

[Compose's application model](https://docs.docker.com/compose/intro/compose-application-model/) groups and isolates resources by project name and uses `com.docker.compose.project` labels. Distinct names allow independent deployments of the same definition.

[`docker compose down`](https://docs.docker.com/reference/cli/docker/compose/down/) removes service containers and networks by default. Anonymous volumes are not removed by default; `--volumes` removes declared named volumes and attached anonymous volumes. External networks and volumes are never removed. Therefore, a successful `down` alone cannot substantiate a claim of zero leftovers. Cleanup must explicitly distinguish disposable session data from persistent or external data.

## Proposed synthesis for the interview

These recommendations are design proposals, not observed behavior of a single existing tool:

1. Prevent unnecessary creation: prefer the project's existing checks, fixtures, services, and temporary directories. Require a concrete verification gap before introducing a new script or service. Useful durable regression tests remain project code.
2. Declare lifetime before creating resources: deliverable, disposable task resource, or retained diagnostic evidence. Record why a new resource is needed and who owns it.
3. Couple creation to cleanup: use native fixtures/context managers and project-scoped container lifecycle commands. Record exact resource IDs and ownership, with unique session grouping where supported.
4. Reconcile at normal completion and failure: remove owned disposable resources, preserve user/pre-existing/shared state, and report retained evidence with a reason and location.
5. Plan recovery separately: interrupted agents need a surviving ownership record and a later recovery path. Age or a filename alone is insufficient authority to delete another session's resources.
6. Keep unknown legacy cleanup reviewable: inventory and classify existing litter without automatic deletion until ownership and intent are established. Never substitute global Docker prune, broad Git clean, or filename matching for provenance.

The likely useful product is an always-loaded housekeeping contract plus a small lifecycle helper, with an explicit cleanup skill for inventory and recovery. A standalone end-of-task skill alone cannot ensure cleanup after the process vanishes, and it cannot prevent litter if it is never invoked.

## Codex integration evidence

The [official AGENTS.md documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md) says Codex reads repository guidance before work. That supports a preventive contract being loaded through existing guidance rather than depending only on voluntary end-of-task invocation.

The [official hooks reference](https://learn.chatgpt.com/docs/hooks) documents Stop, Interrupt, SubagentStop, and SessionEnd. SessionEnd applies to the main thread, may occur later than a completed turn, and has a maximum three-second command timeout. Interrupt is also time-limited. Hook handler support differs with orchestration mode; local command hooks are not supported under cloud orchestration. Consequently, a universal cleanup guarantee cannot rest on SessionEnd. Proposed use: hooks trigger short reconciliation or record pending recovery, while native teardown and recoverable ownership handle resource lifetime. Installed versions and execution surfaces must be checked before selecting adapters. These are design inferences, not a verified integration in this repo.

## Reassessment after user requested a fresh interview

The earlier helper recommendation is provisional and now superseded by a staged evaluation. No source establishes that a generic helper is the smallest sufficient solution for this user's incidents. First establish prevention requirements, coverage across ordinary tasks, and the required interruption behavior.

[Docker run documentation](https://docs.docker.com/reference/cli/docker/container/run/#clean-up---rm) specifies that `--rm` removes a container and associated anonymous volumes when the container exits. It does not remove named volumes or make a still-running detached container exit when the agent disappears. [pytest's safe fixture structure](https://docs.pytest.org/en/stable/how-to/fixtures.html#safe-fixture-structure) couples individual state-changing actions with teardown. These support reusing native lifecycle mechanisms with explicit limits.

Engineering inference: a custom registry adds adoption requirements, persistent state, concurrency and recovery concerns. Registering after creation can leave an unrecorded resource if interrupted in between. A helper becomes compelling only if it closes a concrete gap, ideally by owning acquisition and cleanup together. A prompt-only contract cannot guarantee compliance either; compare behavior on ordinary completion, failed setup, interrupted work, concurrent sessions and intentional retention before expanding machinery.

The revised recommendation is a shared preventive contract plus native lifecycle handling first, with targeted automation contingent on the user's required reliability and evidence of remaining failures. This is not a user-approved decision.
