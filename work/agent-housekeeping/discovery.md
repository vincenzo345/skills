# Discovery

## Request and authorization boundary

The user reports Codex agents creating unnecessary test scripts and Docker resources and leaving them behind. They requested research into existing skills/repositories and an interview to plan a cleanup component or skill. No implementation or retrospective deletion has been authorized.

## Repository findings

- Existing guidance is scattered: /wizard describes deleting one-run scripts, /prototype uses throwaway resources, and /to-record distinguishes scratch output. No shared resource-ownership and cleanup contract was found in the engineering skill Markdown searched.
- Existing stable effort workspaces and accepted ADR 0001 require retaining planning records at stable paths. These records are durable work, not cleanup targets.
- Initial git status included untracked .playwright-cli/, output/, research/, and a Word document. These predate this effort; their names and untracked status do not establish ownership or authorize deletion. No Docker inventory was taken.
- Skill tool is unavailable in this session. /grilling and /domain-modeling were read directly; /research delegates primary-source investigation to a background agent.

## Initial design hypothesis, not approved

Combine a small preventive housekeeping contract with explicit ownership of temporary resources, targeted teardown, and a way to report or recover leftovers after interruption. Reuse existing verification commands before creating ad hoc tests or infrastructure. Retain useful regression tests and requested research artifacts. A clean Git status alone cannot prove container or process cleanup.

## Round 1: open human decisions

1. Should the deliverable be reusable across repositories, with this repo supplying the skill/component, rather than a cleanup procedure only for this checkout? Recommendation: reusable, with per-repo configuration.
2. Should first-version scope cover both preventing unnecessary temporary resources and closing resources created during authorized work? Recommendation: both; leave retrospective removal of unowned historical clutter to a separately reviewed audit.
3. Should implementation planning consider a small deterministic resource helper alongside skill instructions, instead of requiring a prompt-only solution? Recommendation: yes, subject to source research and later design review; runtime-specific hooks remain optional adapters until compatibility is verified.

These are recommendations awaiting actual user answers. No design choices have been accepted yet.

## Later branches

After the first answers: define resource kinds and retention, ownership under concurrent agents, interruption recovery and deletion authority, platform/runtime support, invocation/integration, and acceptance evidence. No glossary additions or ADRs are warranted before terms or consequential choices are resolved.

## Research completed, 2026-10-23

See [primary-source research and proposed synthesis](research/cleanup-patterns.md). Testcontainers supplies a directly relevant agent skill, fixture teardown, and Ryuk ownership/reaping patterns. Superpowers integrates worktree cleanup but has a reported directory-inference leak. A general cleanup skill exists, but its name-based classification is insufficient deletion authority. These examples solve narrower problems or document policies; none establishes a comprehensive solved Codex housekeeping system.

Official OpenAI documentation supports persistent guidance and lifecycle hooks, with execution-surface and timeout limits. A completion-only hook cannot promise recovery after every interruption. No packages, skills, containers, tests, or runtime hooks were installed or launched during research.

The first round remains unanswered. Resume /grill-with-docs with this effort and the three questions above; later carry this effort and research into /to-spec only after the interview is resolved and the user confirms shared understanding.

## Reassessment and interview restart, 2026-10-23

User instruction: "re evaluate. see if this is the best direction forward. then start the grilling session over"

The initial Round 1 is superseded as the active interview. It received no answers and none of its recommendations constitutes an accepted decision. Keep the same effort and research; restart from desired behavior before choosing packaging or machinery.

### Revised assessment, pending human judgment

The previous recommendation selected a custom lifecycle helper too early. Source review establishes useful narrow mechanisms, not that a general helper is needed. A helper that merely registers resources can be bypassed and can miss failures between creation and registration. Reliable acquisition tracking requires owning or intercepting creation, which expands scope substantially. Neither a registry nor a final checklist alone guarantees cleanup after abrupt termination.

Prefer evaluating a concise shared housekeeping contract, existing fixture/process/container teardown, and explicit completion evidence first. Add a helper or hook only for a demonstrated failure those cannot address. Rules remain advisory and must be evaluated in real agent behavior; this is a staged hypothesis, not a reliability claim or accepted design.

Repository integration matters: /wizard already describes deleting one-run scripts; /prototype intentionally preserves the experiment as a source on a throwaway branch; /implement-spec explicitly cleans implementer worktrees after integration; /tdd describes durable behavioral tests. The prior broad statement about no shared contract remains accurate, but these local rules must be reconciled rather than displaced by generic deletion instructions.

### Restarted Round 1: desired behavior

1. Unnecessary creation: If an agent cleaned up perfectly but still wrote redundant test scripts or launched an unnecessary database, would that remain a failure? Recommendation: yes; require a concrete verification gap before creating extra tooling, while keeping useful regression tests part of normal engineering.
2. Coverage: Should housekeeping apply automatically during ordinary coding and debugging, including tasks where no named skill is invoked? Recommendation: yes; a manually invoked cleanup skill would only be a supplementary recovery entry point.
3. Interruption target: Is cleanup on normal completion plus safe recovery at the next session sufficient for the first version? Recommendation: yes; if automatic cleanup while Codex is closed is required, that is a distinct runtime requirement that must drive the architecture now.

All three questions are unanswered. Decisions about package shape, helper necessity, resource categories, cleanup authority, retention, platform coverage, and validation remain open. No spec, implementation, glossary term, or ADR has been approved.

## Restarted Round 1 answers

User answer: "yes to your recommendation"

In the context of the immediately preceding reassessment and three questions, the user accepted:

- Preventing unnecessary creation is part of success even if cleanup would be perfect. Additional verification tooling needs a concrete gap; useful regression tests remain welcome.
- Housekeeping should apply automatically during ordinary coding and debugging, without requiring a named skill invocation.
- Version one targets cleanup before normal completion and safe recovery at the next session. Automatic cleanup while Codex is closed is not a version-one requirement.
- Start with shared policy and existing lifecycle mechanisms. Add a custom helper only if a demonstrated gap justifies it.

These answers resolve the restarted Round 1 only. The superseded original Round 1 remains unaccepted. This is design agreement, not implementation authorization. Existing research remains linked above. No domain-specific term or qualifying architectural decision requires a glossary entry or ADR yet.

## Round 2: open behavioral and adoption decisions

Q4. Verification threshold: May agents create an extra script or service without an additional permission question when they can name the behavior or failure being checked, explain why existing checks are insufficient, and define cleanup? Recommendation: yes within existing task/environment authorization. Reuse existing checks first; a small change does not by itself justify new tests or infrastructure. Useful permanent regression tests belong in the existing test suite.

Q5. Cleanup authority: May agents automatically remove disposable resources they can establish were created for their task and are no longer needed? Recommendation: yes; do not ask again for routine cleanup. Preserve pre-existing/shared resources and other active agents' work. Recovery requires evidence that the prior owner is inactive; unknown ownership is reported, not inferred from filenames or age.

Q6. Failure evidence retention: When a test fails, should the default be to stop disposable services, keep only the minimum useful diagnostic evidence, and remove disposable repro scripts once the issue is resolved? Recommendation: yes. Keep a live environment only when continued debugging or user review requires it, with its purpose and location reported. Durable regression tests and requested deliverables remain.

Q7. Adoption boundary: Should the policy be reusable but enabled per repository, allowing each repo to specify its test commands and temporary locations? Recommendation: yes. This would be the proposed distribution model, not authorization to install it now. A global default across every repo remains an alternative.

All four Round 2 questions await human answers. Later branches include precise resource coverage, scratch and recovery records, concurrent ownership evidence, platform/tool integration, completion reporting and acceptance evaluation. Their details depend on this round; do not assume those choices are settled.

## Round 2 answers and verification lifetime requirement

User answer: "yes to all recommendations. things that are used to test long term like linting can be appended and single one off validation tests that wont be reused need to be cleaned up. the agent should know the Difference in plan accordingly"

Accepted Q4-Q7: agents may create justified additional verification resources within existing authorization without repeated permission questions; automatically clean owned disposable resources; retain minimum useful failure evidence and live environments only while needed; provide a reusable policy configured per repository.

Additional explicit requirement: the agent must distinguish maintained verification from one-off validation and plan the appropriate lifetime before creating it. Reusable lint checks, configuration and regression tests may be added to or extend established project tooling. Single-use validation scripts/tests that will not be reused must be cleaned up. The distinction is based on intended future use, not filename, whether a check passed, or merely the possibility that it could someday be useful.

Operational interpretation for the next design review: name the future behavior or repeatable command that a maintained check supports and integrate it into the existing tooling. One-off validation answers a bounded current question; specify its cleanup before creation. Reassess classification if debugging reveals a real reusable regression case. A reusable checker and its generated output have separate lifetimes: keeping the linter does not justify keeping every lint report, test database or test container. This interpretation does not authorize unrelated tooling installations.

These are ordinary verification-policy distinctions, so keep them in this effort rather than adding general testing terms to the project glossary. No ADR is needed for these reversible choices.

## Round 3: open operational boundaries

Q8. Resource scope: Should version one cover disposable files/reports, temporary local processes, and task-created Docker containers plus their disposable networks/volumes? Recommendation: yes; apply existing worktree-specific rules separately, preserve shared caches and installed project tooling, and leave cloud resources and general machine cleanup out of this first version.

Q9. Temporary workspace and recovery: Should one-off files use the repo's established temporary location, isolated by task, with a single small recovery note only when resources or retained evidence can survive interruption? Recommendation: yes. Reuse existing conventions; choose a configured fallback if absent. The note identifies owned paths/resource IDs, purpose and cleanup action; do not create a report for each command. Remove disposable task state once reconciled. A note establishes creation provenance, not proof that an owner has stopped; require independent inactivity evidence before recovery deletion.

Q10. Verification before adoption: Should the first version be evaluated on representative tasks before expanding it with a helper? Recommendation: yes. Check that unnecessary infrastructure is avoided, reusable lint/regression checks remain, one-off scripts are removed, failed/interrupted tasks are recoverable, and another agent's resources survive. Completion should briefly report checks and any intentional leftovers; avoid generating a permanent housekeeping report for every task.

Q8-Q10 are recommendations awaiting answers. Integration/packaging and final shared-understanding review remain after these boundaries are settled. No implementation has begun.

## Round 3 answers and setup integration requirement

User answer: "Yes to all. If there is no temporary workspace established yet, then this needs to be something that's part of the repo setup skill."

Accepted Q8-Q10: version one covers disposable files/reports, local processes, and task-created Docker containers with their disposable networks/volumes; preserve maintained tooling and shared caches, retain existing worktree-specific rules, and exclude general machine/cloud cleanup. Use task-isolated temporary storage and minimal recovery information for resources that can survive interruption. Evaluate representative task behavior before adding a custom helper, including preservation of useful checks and other agents' resources.

Additional explicit requirement: /setup-repo must establish a temporary workspace when the repository has none. Reuse established conventions when present. This is a design requirement for the setup skill, not an instruction to execute setup or implement changes during this interview.

### Integration findings and proposed defaults

/setup-repo currently configures tracker, triage labels and domain docs, writes a short block to the existing agent instruction file, and uses an explore/review/write workflow. Housekeeping can extend this existing configuration path. The accepted project ADR on setup dependencies distinguishes mandatory setup from gracefully degrading optional guidance; making all ordinary work depend on setup would introduce a broader dependency than required.

Proposed routine defaults for specification: when no suitable existing workspace exists, configure .scratch/agent-tmp/ with unique task subdirectories and ignore only this new subtree, never all of .scratch/ because it may contain existing durable tracker records. Preserve current contents and create task folders lazily. Configure the path and lifecycle policy in the repo's agent docs, separate from stable work/ effort records. Ignore rules do not confer cleanup authority. Paths must remain within the configured boundary and cleanup must avoid following links into unrelated locations. These are proposed implementation defaults, not newly approved user decisions.

## Round 4: remaining integration choices

Q11. Packaging: Should version one extend /setup-repo and shared repository instructions, with relevant existing skills following the same policy, instead of introducing a separate cleanup skill immediately? Recommendation: yes. Setup supplies a concise always-loaded baseline plus the configured housekeeping reference. A separate recovery command or helper can be added only if evaluation exposes a useful missing capability. Existing prototype retention and worktree ownership rules must remain coherent with this policy.

Q12. Missing setup during ordinary work: If an agent encounters a repo without housekeeping configuration, should it continue using a uniquely owned operating-system temporary directory, clean up its own resources, and mention /setup-repo once to establish the lasting convention? Recommendation: yes. Do not scatter temporary files in the repo, silently install project configuration, or block otherwise authorized work solely on absent housekeeping setup. If the verification actually requires repo-local files, use an already established safe location or request the necessary setup choice; do not invent a durable convention without it. Existing environment permissions still apply.

Q11-Q12 remain unanswered. Once settled, present the consolidated design for the user's final shared-understanding confirmation, then hand off the same effort and research references to /to-spec. No implementation or breakdown has been approved.

## Round 4 answers

User answer: "yes to all"

Accepted Q11-Q12: extend /setup-repo, persistent repository instructions and relevant existing skills for version one; add a separate cleanup skill/helper only if evaluation reveals a worthwhile gap. In an unconfigured repo, continue within existing authorization using a uniquely owned OS temporary directory and suggest /setup-repo once. Resolve the workspace choice if verification specifically needs repo-local files. No silent setup installation is authorized by this fallback.

All twelve restarted interview questions now have supplied human answers. Earlier questions marked unanswered above are historical rounds; this section and their subsequent answer sections establish the current position. The first, superseded interview's assumptions were not accepted by these replies.

## Consolidated design for final shared-understanding review

1. Deliver the first version through /setup-repo, persistent housekeeping guidance, and integration with existing skills. It applies during ordinary agent work without a manual cleanup invocation. Prefer native teardown and avoid a custom registry, helper or hook until evaluation demonstrates a gap.
2. Before creating verification artifacts, decide whether they are maintained checks or one-off validation. Reuse existing checks first. Retain and integrate justified reusable lint rules/configuration and regression tests into established tooling. Give disposable scripts, test data and services an explicit cleanup plan before creation. Classify generated outputs independently from the checker that produced them.
3. Setup discovers and preserves an established temporary workspace or configures a dedicated one with task isolation and narrow ignore rules. Keep durable work/ records and requested deliverables separate. The suggested .scratch/agent-tmp/ fallback is a routine specification proposal, not a path explicitly chosen by the user; inspect collisions and existing conventions before adopting it.
4. Agents may autonomously create justified verification resources and remove their own no-longer-needed disposable resources within existing task/environment authorization. Clean temporary files, local processes and task-created Docker containers with their disposable networks/volumes. Preserve shared resources, maintained project tooling, caches, other active agents' work, and the established prototype/worktree retention rules. Unknown ownership is reported rather than inferred from names, ignored status or age.
5. Use normal completion/failure teardown and next-session recovery. Keep a single small recovery note when resources or retained evidence can survive interruption, with exact identity, purpose and cleanup action. Remove disposable bookkeeping after reconciliation. A recovery note proves neither inactivity nor exclusive use; independently establish that cleanup will not disrupt ongoing work. Keep minimal useful failure evidence and explain any intentionally retained live resource.
6. Before setup, use an owned OS temporary directory and suggest setup once; avoid blocking ordinary authorized work merely on missing housekeeping configuration. Recovery discoverability for fallback locations and partial resource creation must be addressed in the specification and evaluated, not assumed from a note alone. Do not claim guaranteed automatic cleanup while Codex is closed.
7. Evaluate agent behavior on unnecessary creation, maintained lint/regression additions, successful one-off validation, partial startup and failed tests, interruption/recovery, concurrent agents, and intentional retention. Verify actual resource outcomes, including resources outside Git. If policy/native lifecycle handling fails an agreed criterion, narrow the claim or add a targeted mechanism before claiming the criterion is met. Report checks and intentional leftovers concisely; avoid permanent per-task housekeeping reports.

### Handoff boundary

The only remaining human input is confirmation that this consolidated design captures the intended outcome. /grilling requires shared-understanding confirmation before acting on the interview. After that confirmation, the next invocation is /to-spec for work/agent-housekeeping, carrying README.md, this discovery record, and research/cleanup-patterns.md. Specification must preserve the accepted behavior and resolve technical details such as recovery discoverability, per-platform process identity, configuration placement and validation fixtures. None of these records approves an implementation breakdown or starts implementation.

## Final confirmation and token-efficiency constraint

User answer: "yes, my only concern is that I'll bog down the agent with more context or things in general. i want to keep it token efficient. what are your thoughts on this?"

The user confirmed shared understanding of the consolidated design and added token efficiency as an explicit requirement. Treat this as refinement of the accepted design, not permission to implement or a reason to reopen settled questions.

Recommended specification constraints:

- Keep the always-loaded housekeeping baseline small and self-contained: reuse existing checks, distinguish maintained verification from disposable validation, name the configured temporary root, clean owned disposable resources, protect shared work, and trigger detailed recovery guidance only when needed. Aim for roughly 150-250 tokens for the baseline including path/reference; this is a proposed design target, not a measured count or a user-selected hard limit.
- Keep setup discovery and configuration in /setup-repo. Do not repeat workspace discovery during every ordinary task or require the setup skill to be reread at task completion.
- Keep Docker-specific details, recovery procedures and exceptional retention cases in short references loaded only on their trigger. Give explicit triggers so deferred guidance is actually found. Do not put core cleanup or ownership obligations behind an optional reference.
- Maintain one source for policy. Existing skills should have only necessary integration pointers or local exceptions, rather than duplicate the full contract.
- Ordinary edits that create no disposable resources incur no new housekeeping inventory tool calls, ledger files, mandated narration or cleanup reports. Resource-producing work incurs only the ownership/recovery information and scoped verification needed for the actual resources. Reuse results from normal checks where sufficient.
- Evaluate instruction size and incremental tool calls alongside correctness. Use ordinary edits, one-off validation, container testing and recovery cases. Do not claim net token savings without measurement; shorter prose is not a success if it causes failures and rework.
- Research and this interview history are design inputs for /to-spec, not runtime housekeeping context to inject into every task.

The [official skills documentation](https://learn.chatgpt.com/docs/build-skills) confirms that skill metadata is loaded first and full instructions are loaded on use. This supports the general pattern of loading detailed guidance on demand; it does not automatically defer arbitrary Markdown linked from repository instructions. Explicit read triggers are part of the proposed design.

Interview status: shared understanding confirmed, with token efficiency included. Next invocation remains /to-spec for work/agent-housekeeping, carrying the current overview, discovery and research. No further human choice is needed merely to adopt the efficiency constraint. Detailed token targets and reference organization can be resolved in the specification without another approval round.

## Specification testing seam confirmation

The user requested /to-spec for this existing effort, preserving the confirmed requirements and token-efficiency constraint, and explicitly limited the task to specification publication.

Proposed seam: setup produces repository guidance; an agent performs or resumes a task; observe resulting files, processes, containers, maintained checks, and context/tool-call overhead. Cases cover normal cleanup, partial setup failure, interruption, and concurrent agents. Existing package validation remains supporting evidence.

User answer through the question tool: "Confirm this testing seam".

This confirms the single end-to-end behavioral seam. It does not approve implementation, tickets, or executing the behavioral evaluation during specification work. Prior art is the existing Wayfinder temporary-repository replays and package/installer checks. Model replay results and deterministic checks must remain distinct evidence.

## Implementation authorization

User explicitly approved the three-ticket breakdown and dependency chain 1 -> 2 -> 3 in issue-plan.md, based on specification revision 1, and authorized implementation on feat/agent-housekeeping with a draft PR targeting main. Keep the PR draft; no merge or auto-merge.

Integration base: origin/main at a3dc1bb8acda362a6d8078f36d83c2e517468407. Integration worktree: E:/tmpdir/agent-housekeeping-integration. The original checkout remains on main and is the existing shared work-record authority. Record snapshots are copied to the integration branch explicitly; worker snapshots never overwrite authority. Docker server 28.3.2 and GitHub authentication are available. Installed skills continue to source main until review/merge.
