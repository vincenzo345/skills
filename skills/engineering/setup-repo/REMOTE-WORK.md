# Remote work-record adapter contract

Read this with [WORK-RECORDS.md](WORK-RECORDS.md) whenever GitHub or GitLab owns the tracker. The provider owns maps, decisions, implementation issues, lifecycle, readiness, ordering, dependencies, current spec pointers and revisions. Local effort folders hold assets and links only. A local coordinator or stale checkout cannot authorize remote work.

## Map facts once

Record the configured provider host and issue repository/project explicitly. Resolve every ID to its fully qualified issue URL; a bare number is insufficient across repositories or projects. Keep one authoritative effort record with current map/spec links and ordered issue references. Native parent links group records but do not establish order or dependencies.

| Fact | Remote representation |
| --- | --- |
| Kind and identity | Stable issue URL; declared `effort`, `spec`, `implementation`, `map`, or `decision` kind in a Work record section of its body. Existing Wayfinder labels identify map/decision kinds. |
| Readiness | Exactly one configured triage readiness label on each implementation issue; spec readiness is independent. |
| Basis | Work record section on the issue: fully qualified spec URL and positive integer revision, or explicit null for self-contained work whose own body supplies sufficient criteria and authority. The spec owns its current revision and immutable retained revision links. |
| Stage, effort lifecycle, current pointers, order | Effort body owns stage/lifecycle/current map/current spec and ordered issue links; queue priority comes from the configured ordered remote effort list. Missing or duplicate order is indeterminate. |
| Dependencies | All native blocking links, fully paginated and individually resolved; body `Blocked by` references only where native blocking is unavailable and that fallback is explicitly configured. |
| Completion | Native closure plus the outcome mapping below and acceptance/integration evidence. Closure alone is insufficient for implementation blockers. |
| Operational ownership | Existing assignees are blocking evidence. Exclusive token ownership requires a proven provider operation or an established shared controller, as below. |

Specs can link content assets in Git, but declare whether the remote body or an immutable repository commit/path owns content. Publish a material revision by retaining exact prior content, gating unfinished old-basis issues, and updating the remote current pointer. If multi-write publication is interrupted, leave a remote publication-pending marker that stops consumers until reconciled. Completed issues retain their original basis. Remote notes hold human answers and decisions; local research/prototypes link back to that decision and the decision links to those assets.

## Selection through completion

1. Resolve the explicit issue/spec/effort, or query the complete ordered remote queue. Fetch current records, labels, current spec revision, blockers and ownership directly from the provider. Validate pagination and access to every required record. Authentication, permission, rate-limit, missing-record and incomplete-page failures mean unavailable information, never an empty queue or a local fallback.
2. Apply the shared selection precedence and eligibility rules. Decision/map kinds never become implementation issues. Skip known blocked work for independent eligible issues; stop on indeterminate authority. Implementation blockers satisfy only with completed outcomes. Canceled or superseded blockers require explicit dependency reconciliation. Explicit invalid targets stay confined to that scope.
3. Acquire through a verified path below before work. Retain owner token, acquired basis and workspace. Refresh authority before resuming, publishing results and recording completion; changed basis requires explicit impact review and worker acknowledgment. If a claim or read fails, preserve work and explain the precise gate.
4. After verified integration and acceptance, record completion evidence remotely and read it back. For implement-spec, include integration branch and accepted commit, verify ancestry, then close the issue with the correct outcome. Only then expose dependents. Finalize a decomposed spec after every required issue is integrated and no overlapping claim remains. A local status update never completes remote work.

## Capability boundary

The shipped GitHub and GitLab adapters **do not support automatic concurrent claiming**. Their assignment updates have not been established as conditional exclusive acquisition. Assignment then read-back, an ETag read, a local worktree lock, or a comment containing a token does not prove exclusivity. Return `unsupported automatic concurrent claiming` before starting autonomous workers.

A separately established single controller can serialize all participating consumers only when the operator has established its exclusive authority over dispatch and lifecycle mutations. Record its identity, participating sessions, ownership protocol, restart/recovery method and scope conflicts in the remote effort. The controller must retain tokens across restarts, reject other owners, arbitrate whole-spec/child conflicts, and verify stopped workers before takeover. Assignment remains a visible signal after ownership. This is a deployment precondition, not an implemented controller service or a default assumption. If exclusivity cannot be established, stop and report the missing capability. Do not silently create a new distributed service or local status mirror.

Before advertising any future concurrent path, run two independent contenders against that actual provider/controller: exactly one may own the same issue; the loser cannot publish completion; stale views, whole-spec/child overlap, restart and explicit recovery retain exclusion. Fixture passes cannot substitute for that proof. No live claim path was verified in this delivery, and no remote writes were performed.

## Native outcomes and planning

GitHub implementation blockers require `state: closed` and `state_reason: completed`. `not_planned` maps to canceled; `duplicate` to superseded; null/unknown reasons remain indeterminate. GitLab issue closure lacks an equivalent completion reason in the issue update contract, so require a remote Work record `completion_outcome: completed|canceled|superseded`, with evidence, before closure. Missing or conflicting outcomes remain indeterminate. These are implementation semantics.

Keep Wayfinder's separate upstream remote frontier: open unclaimed children whose decision blockers are closed, in map order. Read the answer and any invalidation/review marker; a superseded answer gates dependents until reviewed. A canceled out-of-scope decision belongs in Out of scope, not Decisions-so-far. Record a human choice only from supplied human evidence, append a named answer link, and retain old answers on supersession. Session stops never close an unfinished map. Remote assignment expresses the planning convention; simultaneous planning consumers still need established exclusive dispatch.

## Executable contract fixtures and limits

`scripts/work_remote.py` in this skill is a read-only conformance interface, not a provider client. `RemoteContract(provider, fetch).inspect(target, token=None)` calls `fetch` afresh for the issue, current spec when present, and every blocker. For continuation, also pass `acquired_basis` with the previously pinned value, including explicit `None` for self-contained work; omitting the argument performs no acquired-basis comparison. The callback must return current normalized facts from the provider; it must not use local status snapshots. Successful inspection is a preview and does not acquire ownership. `claim` deliberately reports unsupported for both shipped providers.

The normalized issue supplies `kind`, `state`, `effort_state`, `readiness`, `basis`, `blocked_by`, `dependencies_complete`, and `claim` (null when current ownership is known absent). Explicit `effort_state: null` means no containing effort; explicit `basis: null` means self-contained work with sufficient criteria and authority in its own body. Missing either field is unavailable information, not a standalone issue. For a non-null basis, the fetched spec supplies `kind`, `state`, `revision`, and independent `readiness`; both issue and current spec must be `ready-for-agent`. A blocker supplies `kind`, `native_state`, and `state_reason` (GitHub) or `completion_outcome` (GitLab). Optional asset links pass through unchanged. Controller tokens are only normalized observations, not proof that a controller exists. The evaluator covers individual issue inspection; skills retain responsibility for complete queue/order queries, planning continuity, publication and provider writes.

The fixture suite checks fresh authority between selection and completion inspection, retained asset links, stale/acquired basis, canceled and missing blockers, incomplete dependency queries, missing readiness, conflicting ownership and two rejected claim contenders. It is deterministic adapter-contract evidence, not an authenticated provider round trip or successful concurrency proof.

Provider documentation checked 2026-10-20: [GitHub issue state and assignment](https://docs.github.com/en/rest/issues/issues#update-an-issue), [GitHub dependency listing](https://docs.github.com/en/rest/issues/issue-dependencies#list-dependencies-an-issue-is-blocked-by), [GitLab issue update](https://docs.gitlab.com/api/issues/#update-an-issue), and [GitLab link direction](https://docs.gitlab.com/api/issue_links/). The lack of demonstrated exclusive claim support is this adapter's conservative capability assessment, not a claim that every possible provider integration lacks such a mechanism.
