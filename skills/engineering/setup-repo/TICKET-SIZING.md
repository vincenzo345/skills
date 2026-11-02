# Ticket sizing and adaptive delivery

Use this reference when sizing, refining, dispatching, or re-estimating implementation, including an explicitly selected undecomposed spec or conversation request. [WORK-RECORDS.md](WORK-RECORDS.md) owns identity, publication, ownership and completion; this reference owns sizing and readiness evidence. These are agent instructions, not runtime enforcement or an automatic scheduler.

## Size the accepted outcome

Points compare the total work to implement, verify, review and integrate an independently verifiable outcome in this repository. They are not hours, code-size limits, or a substitute for judgment. Calibrate against accepted work, not typing speed or context-window capacity.

| Points | Implementation | Verification | Review and integration |
| --- | --- | --- | --- |
| 1 | One narrow change on an established path | Existing focused checks demonstrate the outcome; little new setup | Local reasoning, familiar integration, small interaction surface |
| 2 | One outcome across a few understood seams | Focused behavioral coverage plus known interaction checks | Reviewer follows the complete path; dependencies and integration steps are understood |
| 3 | One bounded outcome with several understood interactions | Failure cases and affected integration checks are identified and feasible | Broader but bounded review; integration and recovery obligations are known |

Dispatch only ready work estimated at 1–3 points. Three is the maximum, not a target to assign everything. Anything above three, including every 5+ estimate, must be decomposed before dispatch. A nominal three with consequential uncertainty is unready regardless of its label. An explicit direct-spec invocation has the same gate over the entire requested scope.

## Readiness evidence

Record a short sizing note in the existing ticket or explicit spec, alongside acceptance criteria, rather than creating another planning artifact. It must name:

- The independently observable outcome and requirement references it covers, with scope boundaries.
- Evidence for the implementation path and dependencies, and how acceptance, affected checks, review and integration will be verified.
- The estimate and confidence rationale: what makes the total work fit, what evidence supports confidence, and which ordinary details remain open.

Resolve uncertainty that could change architecture, acceptance criteria or ticket boundaries before marking ready. Ordinary details, such as local helper names or an equivalent implementation within an accepted seam, may remain open. Low confidence in the boundary means further refinement, not a discounted estimate.

Use the cheapest decisive evidence: inspect code, then existing tests, then documentation; use a bounded experiment only when those leave a consequential question unresolved. State the question, stopping condition and how its answer changes the slice. An experiment is evidence gathering, not permission to implement an uncertain feature. Reuse current evidence instead of repeating discovery by ceremony.

## Refine the next frontier

Map the whole outcome and requirement coverage, but fully refine only the next eligible work, including independent work that can proceed now. Keep later outcomes explicitly **provisional**, with requirement links, likely dependencies and the condition for refinement. They are ineligible for implementation until this readiness gate is met. Prefer retaining them in the existing breakdown or effort overview; if published as issues, use `needs-info` and name the missing refinement. Approval of the overall map is not readiness approval for every future outcome.

Decompose by independently verifiable outcomes, not schema/service/tests layers. Each slice includes its own verification and integration obligations. Necessary prefactoring or expand–contract work must have an observable compatibility outcome; sharing an integration branch does not exempt a slice from sizing or verification. Avoid splitting a small coherent outcome merely to increase ticket count.

When revising a breakdown, keep existing identities and completed evidence. Map every requirement to accepted evidence, remaining refined work, or a provisional outcome, and explain moved coverage. Preserve replaced scope and replacement links through the configured tracker. Re-estimate only affected remaining work from the current integration basis; sunk effort neither reduces the remaining estimate nor justifies expanding an active ticket.

## Discoveries and handoffs

After each integration, compare discoveries against remaining assumptions, scope, dependencies, estimates and verification. Record a brief no-impact conclusion or update the affected records before dispatch. Refine newly eligible outcomes using the same gate. Preserve completed historical bases; use the work-record revision and reconciliation paths for unfinished records.

If scope grows beyond three points or consequential uncertainty appears during implementation, report the discovery and preserve the branch, partial work and useful evidence. Pause the affected scope, separate accepted integrated outcomes from unfinished work, and refine the remainder before resuming or redispatching. Continue independent ready work within the authorized scope. Never mark partial or unmerged work complete to clear dependencies.

Routine refinement within accepted behavior, guarantees and architecture remains covered by existing implementation authorization; record that authority when publication or reconciliation asks for approval evidence. For consequential changes to those commitments, bring the user a concrete proposal with evidence, affected requirements, tradeoffs and a revised slice. Keep that work unready pending their decision.

Use existing tracker notes and the available worker controller to make handoffs visible: issue, owner/token reference, branch/worktree, candidate commit, verification evidence and its basis, discoveries/downstream implications, and next integration action. Distinguish working, finished awaiting integration, and accepted integrated work in the handoff without inventing lifecycle states. A finished worker retains its claim and blocks dependents until verified integration. Markdown records intent; the controller must observe worker results and perform dispatch and integration using available tools. If it cannot, name the pending action and capability limit.

## Verification evidence

Run repository-required checks and checks affected by the slice. A required full suite remains mandatory. Run whole-spec acceptance checks at meaningful integration boundaries, including final completion and earlier boundaries where shared behavior changes. Reuse results only while their relevant code, dependencies, configuration and environment remain unchanged; record their commit/environment basis and rerun invalidated checks. Review fixes are changes too. A skipped required check is a limitation, not passing evidence.

## Examples

| Estimate | Evidence and boundary |
| --- | --- |
| 1, high confidence | Correct an existing validation message and its documented example. The validation path and existing focused test are inspected; review checks consistency and the repository docs check covers integration. |
| 2, high confidence | Add one existing list filter through the established query and UI seam. Current tests demonstrate authorization and pagination; extend behavioral coverage for filtered results and run affected integration checks. No new query semantics. |
| 3, moderate confidence | Add retry of one failed import using an already accepted idempotency contract. Inspection and existing failure tests establish storage and worker behavior; verify duplicate delivery, failure recovery and the user-visible result. Review and integrate that complete path. Local helper structure remains open. |
| Rejected “3” | “Add retry” while idempotency, concurrent ownership or retention guarantees are undecided. Those answers change architecture and acceptance, so gather decisive evidence and resolve the commitments first. |
| Rejected “3” | “Implement reset/recovery” bundles reset eligibility, deletion/retention policy, concurrent operations, interruption recovery and UI. A small diff or a familiar endpoint does not make the review and verification small. |

For the oversized reset/recovery example, first establish the intended guarantees and inspect actual behavior; do not presume the existing Applications4Life design is correct. This is a hypothetical sizing example, not authorization to inspect or resume that application. Depending on the accepted contract, independently verifiable outcomes might be: (1) expose an accurate eligibility decision and reasons through the existing read path; (2) execute one bounded reset case with its agreed retention and failure behavior; (3) recover that case after interruption without violating the accepted guarantees. Each includes the layers and checks it needs. Later outcomes remain provisional until earlier evidence establishes their boundaries. If atomicity makes those outcomes inseparable, find a narrower supported case or resolve the architecture first rather than relabeling the bundle three points.

After integrating the eligibility slice, suppose evidence shows an external operation can outlive local ownership. Keep the accepted eligibility evidence, mark the affected reset/recovery outcomes unready, and re-estimate their remaining coordination and verification work. A new cancellation guarantee needs a user proposal; an implementation adjustment within an already accepted guarantee can be routinely refined. Independent ready outcomes can continue.
