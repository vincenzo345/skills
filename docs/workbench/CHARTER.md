# Workbench Charter

**Status:** Foundation contract for version 1

## Purpose

Workbench helps a human direct work from an uncertain business need to an honestly verified outcome. It coordinates focused specialists, persists state, explains what is ready and why, and validates movement between lifecycle stages.

The governing design rationale is in the [Workbench build plan](../../WORKBENCH-BUILD-PLAN.md). The source-skill strengths and risks that this charter responds to are in the [skill portfolio audit](../../WORKBENCH-SKILL-AUDIT.md).

## Operating promise

Workbench will make the current position, evidence, decisions, uncertainty, and next action understandable without relying on conversation history. It will distinguish a recommendation from a decision, a plan from implementation, local proof from deployed proof, and deployment from an observed business outcome.

## Non-goals

Workbench is not:

- an all-knowing business, product, architecture, UX, or engineering advisor;
- a replacement for specialist methods, executable standards, or domain expertise;
- a tracker, issue graph, or document collection used as hidden workflow state;
- a fixed waterfall that forces every stage onto every work item;
- authority to make consequential decisions or mutate external systems;
- evidence that a process, control, deployment, or outcome works merely because it is documented;
- in version 1, a polished UI, a migration of every source skill, or support for every technology stack.

## Ownership boundaries

### Workbench owns

- The stable work identity, intake-bound routing profile, selected compatibility route, current stage, and transition history.
- Stage applicability, entry and exit evaluation, stopping points, and route corrections.
- The uncertainty graph, ready frontier, and explanation of the recommended next action.
- Shared identities and lineage for artifacts, decisions, evidence, authorizations, and handoffs.
- Validation that a specialist output satisfies its declared handoff contract.

### Specialists own

- The domain method used to investigate or produce a stage result.
- Findings, options, recommendations, limitations, and artifacts within that domain.
- Declaring which inputs they used and which uncertainties or decisions remain.

Specialists consume shared contracts; they do not create competing routers, state stores, decision policies, proof policies, or tracker lifecycles.

### The human owns

- The desired outcome and acceptable planning destination.
- Material business, product, architecture, scope, risk, and tradeoff decisions.
- Delegation of a decision, including its scope, constraints, and expiry.
- Authorization for consequential external actions.
- Acceptance of residual risk and the decision to stop, defer, continue, release, or close.

Evidence can inform a human-owned decision. Confidence, document volume, or repeated questioning cannot convert evidence into authority.

### External systems own

Repositories, trackers, deployment platforms, and operating systems remain systems of execution or publication. Workbench records references to their outputs; none is the canonical Workbench state store.

## Human-control invariant

After every stage, the current-state view must let the human answer:

1. Where are we?
2. What did we learn?
3. What did we decide, and which alternatives were rejected?
4. Why is the proposed action next?
5. What remains uncertain?

A stage has not completed when these answers require forensic rereading or when confusion is treated as consent. The human may override a recommendation; Workbench records the override and its consequences without repeatedly relitigating a settled choice.

## Authorization boundaries

Authorization is capability-specific, scope-bound, and recorded. A direct user request may grant a capability for its stated scope; one capability never silently grants another.

Separate authorization boundaries apply to:

- repository or other durable content mutation;
- implementation of a proposed solution;
- publication or synchronization to an external tracker;
- creating commits or otherwise recording a source-control change;
- release or deployment to an environment;
- closure or a claim that the planning destination or desired outcome was achieved.

Read-only investigation stays within the systems and data placed in scope. Sensitive-data access and onward disclosure remain constrained by the source's authority and confidentiality. When authority is absent, a specialist may prepare a plan, preview, or recommendation and must leave the external action pending.

## Version 1 success

Version 1 succeeds when:

- A fresh agent can start, inspect, advance, and resume each of the five canonical routes from persisted files.
- Stage applicability, skips, stops, and loop-backs are explicit and reproducible.
- The lifecycle route and uncertainty map remain distinct while producing one coherent current-state view.
- Every material artifact and decision has stable identity, input lineage, owner, and named consumer.
- Invalid transitions and incomplete handoffs fail with actionable explanations.
- Authorization boundaries prevent ungranted publication, implementation, commit, deployment, and closure actions.
- The five human-control questions are answerable at every scenario checkpoint.
- One bounded real process completes a pilot through its authorized planning destination, including at least one agent-executable evidence task and one exercised route correction.
- Packaging, contract validity, local behavior, deployment, and business-outcome evidence are reported as separate claims.

Version 1 is not successful merely because its schemas validate or its documentation is complete.
