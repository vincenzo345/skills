# Workbench Decision Policy

**Version:** 0.1.0  
**Status:** Initial kernel policy

## Purpose

This policy keeps evidence, recommendations, choices, and authority distinct so the human remains the informed orchestrator. It is the semantic source of truth for decisions across every Workbench route. Specialists cite this policy version and return decision references; they do not restate its rules.

`schemas/workbench-decision.schema.json` defines the decision record, `schemas/workbench-authorization.schema.json` defines permission to act, and `schemas/workbench-event.schema.json` records transitions. This document defines what those records mean.

## Facts are not decisions

A **factual question** asks what is, was, or happened. Evidence can answer it at a stated confidence and scope. Examples include measured cycle time, current system behavior, a contractual requirement, and whether a test passes.

A **consequential decision** selects what should happen. It changes commitments, behavior, scope, cost, risk, architecture, policy, or an external system. Evidence informs the choice but cannot authorize it.

Use this test:

| Question | Record as |
|---|---|
| Can observation, inspection, calculation, or a source establish the answer? | Evidence, finding, or proof |
| Does answering select among futures or accept a consequence? | Decision |
| Are both present? | Record the factual basis and consequential choice separately, then link them |

Conflicting or insufficient facts create an evidence task. Confidence is not consent, and a recommendation is not a decision.

A material factual question may use the decision schema as a **determination record** so its evidence blockers and supersession remain visible. Its authority is `factual`, and confirmation means evidence-backed within the recorded scope—not human approval. This structural reuse never converts a fact into consent.

## Materiality

A choice is material when a reasonable alternative would change at least one of:

- the desired outcome, planning destination, or committed scope;
- user, customer, employee, or business behavior;
- security, privacy, safety, legal, data-retention, or access risk;
- architecture boundaries, external contracts, migrations, operational ownership, or reversibility;
- meaningful cost, schedule, staffing, vendor, or infrastructure commitments;
- proof required to make a completion or outcome claim; or
- authority to mutate a repository, publish externally, implement, commit, deploy, or close work.

Materiality depends on consequence, not technical size. A one-line access-control change may be material; choosing an internal variable name usually is not.

Non-material choices may use documented defaults within the specialist's remit. Record the selected default in the artifact or handoff without opening a decision record. When uncertainty about materiality could conceal a meaningful consequence, treat the choice as material until its bounds are clear.

## Authority and decision state

Authority and resolution are independent. Every material question receives both when it is registered.

The `decision_authority` enum is:

| Authority | Meaning |
|---|---|
| `user-owned` | Only the user or named accountable human may settle a consequential choice. |
| `delegable` | A named delegate may settle the choice under a separate authorization with explicit bounds. Until then, the user remains the owner. |
| `factual` | Evidence, rather than preference or consent, settles the question at a stated scope and confidence. |

The `decision_state` enum is:

| State | Meaning |
|---|---|
| `proposed` | The question is identified and may be settled when its authority and prerequisites permit. |
| `evidence-blocked` | A responsible resolution cannot yet be made; linked evidence work, owner, and reconsideration condition are required. |
| `confirmed` | A permitted actor made an explicit consequential choice, or evidence supports a factual determination. The applicable receipt is recorded. |
| `superseded` | A later confirmed record replaces this resolution without erasing it. |
| `withdrawn` | The question no longer applies and the reason is recorded. |

`user-owned` and `delegable` describe who may decide; `evidence-blocked` describes why the question cannot currently resolve. There is no generic `open`, `resolved`, or `approved` state.

Legal state transitions are:

```text
proposed         -> confirmed | evidence-blocked | withdrawn
evidence-blocked -> proposed | withdrawn
confirmed        -> superseded
```

Authority may change while a record is unresolved through an event with its basis. New evidence never edits a `confirmed` record in place. It may trigger a linked replacement and supersession.

## Ownership and delegation

The user owns material business, product, experience, architecture, risk, scope, and tradeoff decisions unless an accountable owner is explicitly named or the user delegates the specific choice.

A decision with `delegable` authority is not already delegated. Before an agent or other specialist settles it, the authorization record must identify:

- the decision or bounded class of decisions;
- the permitted actor;
- constraints, defaults, and escalation thresholds;
- duration or terminating condition; and
- actions the delegation does not authorize.

Delegation to choose does not authorize implementation, publication, commit, deployment, or closure. A delegate escalates when the evidence, options, or consequences fall outside the recorded bounds.

An agent may make non-material method choices inside an authorized task and report them in its handoff. It must not fragment a material decision into small defaults to avoid human ownership.

## Consequence-first decision process

For each material choice:

1. State one decision question and why it matters now.
2. Confirm its state, owner, dependencies, and decision deadline or triggering condition.
3. Present no more than three meaningful options by default. Include “defer” or “gather evidence” when either is responsible.
4. Explain each option's likely benefits, costs, risks, reversibility, and what it makes harder later.
5. Separate established facts, assumptions, inferences, and unknowns. Link the evidence and proof records used.
6. Give a recommendation after the options, with rationale and confidence.
7. Show a concise consequence receipt and ask for an explicit choice only when the user demonstrates understanding.
8. Record the choice, actor, authority, receipt, and downstream effects before dependent work advances.

For a factual determination, replace the choice steps with an evidence assessment and record its scope, confidence, and limitations. The completion criterion is a valid `confirmed`, `evidence-blocked`, or `withdrawn` record—not the end of a conversation.

## Consequence receipt

A consequence receipt is the short, human-readable view of a material decision. The decision schema owns its serialization. The receipt must make these meanings apparent on one screen:

- the decision ID, question, owner, and chosen option;
- the immediate consequence and important longer-term tradeoffs;
- alternatives considered and why they were not selected;
- facts, assumptions, uncertainties, and confidence behind the choice;
- reversibility, revisit trigger, and known falsifiers;
- resulting artifacts, route changes, risks, and obligations; and
- who decided, under what delegation or authority, and when.

The receipt links to detail instead of reproducing research or specialist documents. A user confirmation applies to the displayed receipt version; material changes require a new decision or supersession.

## Confusion is not consent

Consent is valid only when the user makes an affirmative choice that maps unambiguously to a presented option or clearly states a different choice.

Silence, lack of objection, politeness, an exhausted “fine,” approval of a document's wording, or agreement to continue is not consent to the material choice inside it. Neither is a response that reveals a mistaken understanding of the principal consequence.

When understanding is unclear:

1. Identify the specific mismatch in plain language.
2. Re-explain the consequence from a different angle with a concrete example where useful.
3. Ask the user to choose or restate the consequence in their own words; do not ask them merely to confirm the agent's summary.
4. If clear understanding is still absent after two materially different explanations, stop seeking a final choice in that review session. Set the state to `evidence-blocked` when information can resolve it; otherwise keep it `proposed` with `user-owned` authority and a named next step such as involving another accountable person.

Independent ready work may continue. Only dependent work is blocked.

## Evidence-blocked decisions

Use `evidence-blocked` when more questioning would solicit preference without a sufficient factual basis.

The decision must point to at least one evidence task with:

- the question or uncertainty it will reduce;
- an owner and next action;
- the evidence quality or threshold needed to reconsider the decision; and
- a falsifier or stopping condition where applicable.

When the evidence condition is met, return the state to `proposed`. A consequential record keeps or explicitly changes its `user-owned` or `delegable` authority and does not become `confirmed` automatically. A factual record may become `confirmed` only when the stated evidence threshold is met. When evidence cannot reasonably be obtained, present that limitation and let the authorized owner explicitly accept, defer, or avoid the uncertainty.

## Overrides

The user may override a recommendation, default, stage sequence, method, or permitted gate. Workbench records the selected alternative without continuing to argue the settled point.

An override records what was overridden, the user's stated reason when offered, the consequences shown, accepted residual risk, affected artifacts or stages, and resulting proof gaps or obligations. If no prior decision was settled, the override is the decision. If it changes a settled choice, create a replacement decision and supersede the prior record.

An override cannot:

- change a factual result without new evidence;
- turn missing proof into achieved proof;
- erase history, blockers, or residual risk;
- grant an action beyond the user's authority; or
- silently authorize implementation or another state-changing action.

When an external rule or platform control cannot be overridden, record the constraint and route to an available alternative.

## Supersession and correction

Decisions and factual determinations are append-only after they become `confirmed`.

To change one:

1. Create a new decision linked to the prior record.
2. Explain the new evidence, assumption failure, changed constraint, or user override.
3. Record a new consequence receipt and authority basis.
4. Mark the prior decision `superseded` only after the replacement is valid.
5. Re-evaluate dependent artifacts, proof, obligations, route stages, and tracker projections. Create explicit updates rather than assuming they remain valid.

A clerical correction that cannot change interpretation may be evented as metadata. If a reasonable consumer could act differently after the edit, use supersession.

## Fatigue limits

Human control fails when agreement is obtained through volume. Apply these defaults:

- Ask the highest-value blocking question first. Questions whose answers do not affect each other may be grouped.
- Present at most three material decisions in one review batch. Then summarize what settled, what remains, and offer a pause before another batch.
- Reuse settled decisions. Ask again only when a recorded assumption, scope boundary, or falsifier changed.
- Use a one-screen receipt and progressive links. Document length, scroll completion, and “reviewed all sections” never count as understanding.
- After two unsuccessful, materially different explanations of one decision, apply the confusion rule instead of increasing pressure or repetition.
- If the user signals fatigue, pause consequential review, preserve state, and continue only independent agent-ready work.

The user may explicitly request a larger batch, but every material choice still requires its own unambiguous receipt and response.

## Authorization boundaries

A decision selects a course; an authorization permits an action. Keep them as separate linked records.

The minimum `authorization_scope` values are:

- `decision-delegation`
- `repository-mutation`
- `tracker-publication`
- `implementation`
- `commit`
- `deployment`
- `closure`

Authorization for one scope never implies another. In particular:

- approval of a proposal, design, architecture, specification, or ticket plan does not authorize implementation;
- implementation does not authorize commit, tracker publication, deployment, or closure;
- deployment approval applies only to the named artifact, target environment, and bounds;
- decision delegation does not grant any execution scope; and
- closure requires honest proof and cannot be inferred from successful implementation or deployment.

The initiating user request may itself supply authorization when it explicitly asks for the action and identifies a sufficient scope. Record that basis; do not interrupt for duplicate permission. Material expansion, a new target, or a more irreversible action requires new authorization.

Read-only investigation within the supplied work scope may proceed unless restricted by confidentiality, access policy, or the environment. External communication, purchases, credential changes, destructive data operations, and other consequential actions still require their applicable explicit authority even when they are not represented by a kernel scope value.

## Policy completion criteria

A material decision is ready for dependent work only when:

- it is classified as factual or consequential and materiality is explicit;
- its authority, owner, and current state are valid;
- facts and assumptions point to their evidence rather than masquerading as consent;
- a deciding actor had authority and made an unambiguous choice;
- the consequence receipt is complete and understandable;
- overrides, supersession, proof gaps, and obligations remain visible; and
- every resulting state-changing action has its own applicable authorization.
