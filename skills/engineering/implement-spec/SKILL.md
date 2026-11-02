---
name: implement-spec
description: "Implement the result of /to-spec and /to-tickets in code."
disable-model-invocation: true
---

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

The issue tracker should have been provided to you. If not, tell the user to run `/setup-repo`.

For disposable validation or interrupted work, read the housekeeping reference named by repository instructions, or the [shared fallback](../setup-repo/housekeeping.md#without-repository-configuration) if none is configured.

The goal is the entire spec implemented on a single **integration branch**, with every ticket resolved the way the issue tracker closes work.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

**Implementer subagents** should be run in the background where possible for maximum concurrency.

For remote trackers, read [the remote adapter contract](../setup-repo/REMOTE-WORK.md) before dispatch. Automatic concurrent claiming is unsupported without an established exclusive controller or verified provider path. Refresh remote state before selection and completion.

## Steps

1. Read the configured tracker and [shared work-record contract](../setup-repo/WORK-RECORDS.md), then the current spec, linked design, and approved issues. Verify completed issues against their evidence and integration availability; work only on the remaining eligible frontier. Never infer completion from a worker report or a stale worktree. If no issues exist, use explicit direct-spec implementation through `implement` instead.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Establish the integration branch and its base explicitly. Preserve existing work when resuming; do not reset a dirty worktree. For local tracking, declare one authoritative checkout and the shared Git coordinator before dispatch. If the issue tracker closes work through PRs, or the user asks for one, open a draft PR after the first merge in step 5 (a branch with no commits ahead of main can't open one), marked as closing the spec and tickets.

4. Before each dispatch, apply [ticket sizing and readiness](../setup-repo/TICKET-SIZING.md). Refine the next eligible outcomes; provisional work remains ineligible. Use **implementer subagents** to implement ready tickets, each in its own worktree on its own branch, within available worker capacity. Each implementer subagent:
   - receives an individual issue claim acquired atomically through the shared authority, its ownership token, and the current integration basis; never acquire a whole-spec claim over child workers;
   - confirms its worktree is based on the integration branch before starting; reconcile a different base without discarding work;
   - resumes only with its matching token after current readiness, basis and dependencies are revalidated; a lost token requires explicit recovery with confirmed worker stoppage and preserved work pointer;
   - pauses when its acquired basis changes; retain work, reconcile the issue, and acknowledge the reviewed new basis before publishing results;
   - calls the Skill tool with `tdd` to build the ticket;
   - reports scope-changing discoveries immediately and follows the shared reference's recovery and re-estimation rules, preserving work while independent ready work continues;
   - merges the integration branch tip into its own branch before reporting results, with the shared reference's handoff and explicit pending integration action.

5. Once a worker reports verified results, revalidate its claim and merge its work with a **merger subagent**. Resolve discrepancies and run relevant integration checks. Only then record issue completion in the authority. For local records, use `complete` with the ownership token, acceptance evidence, `--integration-ref <branch>`, and `--commit <accepted-commit>`; the helper verifies ancestry and retains the receipt. Unmerged work remains in-progress and blocks dependents. Do not merge stale worker tracker files over live authority.

6. After each integration, apply the shared reference's discovery impact check to remaining work. Update affected assumptions, scope, dependencies, estimates and verification before dispatch; preserve completed evidence and requirement coverage. Routine refinement uses existing authority; consequential changes return to the user as a concrete proposal. Refresh authoritative state and claims, then dispatch the eligible **frontier** within available capacity. Observe worker results through the actual controller tools and retain pending handoffs in existing tracker notes; Markdown alone does not schedule workers or integrate their branches. If no work is ready, identify whether refinement, a user decision, or pending integration is next rather than treating provisional outcomes as complete.

7. Once every required outcome is covered by accepted integrated work, call the Skill tool with `code-review` on the integration branch. Refine review fixes through the same sizing gate before dispatching them.

8. Verify the whole spec acceptance criteria and required repository checks after review fixes, following the shared reference's verification and evidence-reuse rules at this and earlier integration boundaries. For a local decomposed spec, `complete-spec` requires the expected revision, overall acceptance evidence, integrated child receipts and no conflicting claims. Complete the effort only when its remaining planning/outcome obligations are satisfied. Remote completion follows the adapter contract; never substitute local status for remote authority. If a draft PR exists, mark it ready for review. Report the integration branch, evidence and remaining limitations.

9. Clean up all **implementer subagent** worktrees.
