# Approved implementation breakdown

## Current execution basis

Current delivery: Issue01 accepted; Issue02 code integrated for draft PR8, but waiting/needs-info because policy-blocked T2 cleanup and diagnostic reconciliation remain incomplete. Spec/effort are unfinished; no accepted completion is inferred from code availability.

The user authorized isolated implementation through a reviewed draft PR, then explicitly directed "skip anything claude related". [Revision 6](spec.md) removes new Claude-specific setup/bridges/validation and preserves existing instructions. Exact [revision 5](history/spec-r5.md) is retained. Existing Issues were reconciled through the shared coordinator: Issue 01 affected with approval, Issue 02 no impact. Codex T1, all other acceptance, identities and 01 -> 02 remain. Accepted H is b86774500cdcc5cca98de791573cd6106b6eeeb2, verified ancestor of feat/agent-workflow-reliability before readiness. See the overview and each Issue for current lifecycle/claims; older needs-info and planning-only statements below are publication history.

**Published 2026-10-28 through the configured local work-record producer. Specification basis: [revision 5](spec.md), verified current and unchanged. The user approved both slices and the genuine 1 -> 2 edge. Both Issues remain needs-info; publication grants no implementation eligibility.**

## Original approved breakdown (historical revision 5)

The publication state and authorization snapshots below describe the original publication. Current basis and authorization are recorded above and in the live Issues.

## Improvements and their authoritative homes

| Improvement | Benefit | Authoritative instruction location |
| --- | --- | --- |
| Verify Codex and Claude discovery after setup | Guidance reaches either agent | Setup's discovery/write/verification flow; minimal runtime entry-point references |
| Reuse knowledge locations and one short index | Current design is easy to find without loading all docs | Reviewed repo configuration and current documentation index |
| Keep core rules short with precise creation, retention and recovery triggers | Detailed policy loads only for relevant work | One baseline and the existing common/service/recovery references |
| Connect design/prototype findings to cleanup | Decisions survive disposable execution | Existing design handoff and prototype capture steps, pointing to configured records and shared housekeeping |
| Preserve valuable work using existing ownership and teardown | Maintained checks, unique reasoning and other tasks stay safe | Existing housekeeping policy; no per-file register |
| Require bounded, comparable behavioral evidence | Completion and overhead claims are reviewable | Implementation acceptance criteria and one evaluation summary; hooks remain deferred |

## Housekeeping prerequisite H

Read-only verification on 2026-10-28: [housekeeping PR #7](https://github.com/vincenzo345/skills/pull/7) is OPEN and draft, targeting main, with head `b86774500cdcc5cca98de791573cd6106b6eeeb2`, no reviews, no merge commit and no merge date. GitHub PR base and local main are `a3dc1bb8acda362a6d8078f36d83c2e517468407`. Local `merge-base --is-ancestor` returned 1: that housekeeping head is absent from main. The existing housekeeping review branch/worktree and completed effort record do not establish an accepted integrated basis.

**Exact missing prerequisite:** through separately authorized housekeeping review/integration, identify the exact accepted housekeeping commit, name the authorized integration branch (main is the current intended basis), and verify that commit is its ancestor. Record accepted SHA, integration tip, ancestry result and applicable prior evidence; revalidate if the basis changes. No exact accepted integrated housekeeping commit is currently established. H is an external prerequisite, not another implementation Issue or a request to recreate housekeeping.

Both Issues remain **needs-info** despite approved scope. After H is satisfied, review readiness through the shared coordinator and obtain feature-branch implementation and draft-PR authorization. Acquire exclusive shared ownership before implementation on an isolated branch. Preserve unrelated work and the globally linked main checkout. Merge approval is separate. Publication authorizes no merge, global development-worktree activation, installation, implementation branch or PR mutation.

## 1. Configure discoverable guidance and durable knowledge locations

**Delivers:** Setup configures a usable documentation index and temporary workspace, and fresh Codex/Claude sessions find the concise shared repository guidance.

**Objective:** 1 and the setup/overhead portions of 3.

**Blocked by:** H. No proposed Issue blocker.

**Acceptance criteria**

- Fresh setup reuses or establishes appropriate knowledge roles, a short index and a temporary convention; creates no empty documentation taxonomy.
- Codex and Claude fresh-session observations demonstrate discovery without a prompt that explicitly supplies the policy or orders a named instruction-file read.
- One authoritative policy source is reached through appropriate entry points; existing instructions, custom locations, tracker authority and user edits survive repeated setup without duplicate blocks.
- References resolve, permanent docs are Git-visible, and narrow temporary ignore rules preserve unrelated content.
- Conditional pointers expose creation, retention ambiguity, services and recovery without loading all references for ordinary edits.
- T1 passes. T3 shows zero added routine housekeeping actions, specialized reads or bookkeeping in matched baseline/candidate ordinary edits; context and execution differences are reported separately. Missing runtime observations remain unresolved.
- Relevant setup documentation/catalog/router changes and existing package checks ship in this slice.

**Documentation and validation:** Setup consumer documentation and relevant catalog/router entries; T1 and T3 evidence in the effort's compact evaluation summary.

## 2. Preserve design findings through safe cleanup

**Delivers:** An agent answering a bounded design question retains useful knowledge and verification while safely retiring its disposable prototype work through configured housekeeping.

**Objective:** 2 and lifecycle proof in 3.

**Blocked by:** Issue 1, because its configured locations and discovered guidance supply this slice's end-to-end input. H is inherited.

**Acceptance criteria**

- Existing design handoff and prototype capture use configured durable locations, link accepted conclusions to evidence, and distinguish proposed/accepted/implemented intent without duplicating policy.
- T2 uses one question, one lifecycle, one module interface, minimal synthetic data and one disposable environment.
- Findings and necessary source reference survive before execution resources retire. Approved plans/history, maintained linting/regression checks, reusable fixture and requested deliverable remain.
- Owned one-off script/output/environment are absent when no longer needed; justified diagnostic retention is reconciled when its revisit condition is met.
- Another task's sentinel remains unchanged; ambiguous ownership is preserved and reported. Evaluator teardown is identified separately from actor outcomes.
- Existing native cleanup and next-session recovery are reused. Changed service/recovery behavior reruns only affected prior scenarios; unchanged behavior cites its existing basis/evidence.
- Design/prototype human documentation and relevant router/catalog guidance accompany the behavior. Relevant checks pass; repeat T1/T3 only when changes or findings affect their prior result.
- Final scope review excludes extra hooks, helpers and policy layers; remaining mandatory observations and cleanup limitations are explicit.

**Documentation and validation:** Existing design/prototype documentation, necessary shared-reference integration and relevant catalogs/router; T2 evidence and final review in the existing effort records.

## Published Issues

| Order | Issue | Readiness at publication | Blockers |
| --- | --- | --- | --- |
| 01 | [Configure discoverable guidance and durable knowledge locations](tickets/01-configure-discoverable-guidance-and-durable-knowledge-locations.md) | needs-info | H; no Issue blocker |
| 02 | [Preserve design findings through safe cleanup](tickets/02-preserve-design-findings-through-safe-cleanup.md) | needs-info | Issue 01 and H |

Dependency order: 01 -> 02. H is an external integration prerequisite, not a synthetic implementation edge. The producer recorded revision 5, stable IDs, deterministic order, typed blockers and durable approval in each Issue. No pre-existing Issues were found under this effort or elsewhere under work before publication; reuse these published identities.

## Next action and authorization

Resolve H through separately authorized housekeeping review/integration. Record the exact accepted housekeeping commit and prove its ancestry on the authorized integration branch before reviewing readiness and obtaining feature-branch implementation and draft-PR authorization. Then work Issue 01 before Issue 02 under exclusive shared ownership, with relevant validation, review and integration receipts. Preserve unrelated work and globally linked main. Merge approval remains separate.

## Publication boundary

Publication only: no implementation, implementation branch, installation, runtime replay, global development-worktree activation or PR mutation. The specification remains unchanged; its prior planning-only publication restriction is superseded solely by the user's explicit authorization to publish these two Issues. Spec readiness does not bypass H or authorize implementation.
