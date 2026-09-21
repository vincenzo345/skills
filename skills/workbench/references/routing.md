# Routing

Use this reference when compiling a work profile, choosing a planning destination, or turning uncertainty into executable work. The machine-readable lifecycle registry in `schemas/workbench-lifecycle.schema.json` owns phases, activity stages, legacy routes, destinations, applicability handlers, and gate handler IDs.

## Decide whether durable coordination is warranted

Start a new Workbench item only after the user explicitly names Workbench or asks for durable Workbench coordination, and at least one of these is true:

- the destination is clearer than the path and evidence work must chart that path;
- the work crosses business, process, experience, architecture, delivery, or verification concerns;
- a proposal or other planning destination may be a valid stop before implementation;
- a brownfield change needs reconnaissance and a recorded architecture delta;
- decisions, obligations, or state must survive another session or agent;
- the user asks to start or route such an effort.

Resume an existing item when the user names its work ID or asks to continue, inspect, advance, or determine what is next for active `.workbench` work. Do not create a Workbench item for a clear explanation, ordinary coding work, or a bounded one-session task unless the user chooses durable coordination. If ordinary work later reveals a continuity or orchestration need, explain why Workbench may help and let the user choose whether to start it.

## Build a routing profile

Classify six independent questions using evidence available now, and explain each answer:

- **Business basis:** `hypothesis` when value, demand, or process behavior remains unproven; `operating-process` when current business work is the basis; `supplied-requirements` when an accepted requirement set is the basis; `technical-only` when the request originates in software behavior without a separate process claim.
- **Solution context:** `greenfield` for a new software context; `brownfield` when existing code, data, integrations, or deployment behavior will change; `process-only` before software is justified; `undetermined` only while evidence or a human decision genuinely blocks classification.
- **Engagement intent:** `explore`, `plan`, `implement`, or `release`, based on what the user asked Workbench to do now—not what might eventually happen.
- **Planning destination:** choose the narrowest lifecycle destination that satisfies the current request and authority. Proposal is a destination, not an entrance. Reaching it does not establish a later destination or the desired business outcome.
- **Execution lane:** use `fast` only when behavior, blast radius, applicable standards, proof, and execution context are bounded and no material choice or evidence gap is hidden. Otherwise use `full`. A failed preflight expands the same work item.
- **Planning posture:** `collaborative` means the agent discovers facts while the user owns material choices; `delegated` permits reversible defaults only inside explicit bounds. “Help me plan/work through/figure out” and any unsettled consequential choice select collaborative. “Draft/propose/recommend using your judgment” may select delegated.

Intent and destination must agree. Explore and option comparison normally target `proposal`; a buildable plan targets `implementation-plan`; a behavior contract targets `specification`; build, fix, and implement target `locally-verified-implementation`; release targets an explicit release destination. Never allow a semantic helper default to weaken the user's requested destination.

For every `greenfield` or `brownfield` software profile, inspect persistence and include an explicit `data-model-design` stage recommendation. Mark it applicable when a database or durable store is introduced or its semantics may change; mark it not applicable only with evidence that persistence is unaffected; use undetermined when the impact cannot yet be established. Read [data-modeling.md](data-modeling.md) when this branch applies. A no-impact disposition keeps a small change lean while preventing the data layer from disappearing by default.

Persist and start a ready profile with `route-and-start`. When a material human question or external wait prevents start, use `finalize-intake` so the unresolved question is durable before asking it. After answers arrive, use `revise-routing` with the complete updated profile, a revision reason, and an answer for every question removed from `unresolved_questions`. Workbench keeps the same work ID, preserves every immutable receipt, and treats the highest valid contiguous revision as current. Then start it with `start --from-routing`.

New work is `profile-compiled`: the runtime applies the recorded activity recommendations and its deterministic defaults, groups the applicable activities into phases, selects at most one checkpoint per active phase, and stops the plan at the chosen destination. The compiled plan on each routing revision is immutable evidence of what that revision included, excluded, and why.

The eight phases are `frame`, `discover`, `design-decide`, `plan`, `implement`, `verify`, `release`, and `measure`. Activity stages retain the domain vocabulary—such as evidence intake, experience design, architecture, data-model design, standards, specification, and review—but an activity is not automatically a lifecycle checkpoint. Several activities may collaborate within one phase and produce one accepted handoff. `proposal` is the consolidating checkpoint at the end of `design-decide`, so every explicitly applicable design lens can contribute to a proposal destination.

`runtime_route` records the closest historical route when one exists and may be `null`, especially for greenfield. It does not control a profile-compiled plan. The five fixed route IDs remain supported for replay and direct legacy starts only; do not create another fixed route for every combination of context, destination, and depth.

Not-applicable activities remain visible in the current routing receipt's `compiled_plan` but are never entered. Undetermined material applicability blocks start. Work at a proposal destination does not enter implementation, and locally verified work does not carry release stages as pending. Do not simulate a missing transition by editing state.

## Maintain two coordinated views

The lifecycle route answers which broad gate applies. The uncertainty map answers what must be learned, tested, decided, or produced to reach the destination. Neither substitutes for the other.

When the path is unclear:

1. Preserve unresolved fog instead of converting it into confident tasks.
2. Turn actionable fog into outcome-linked questions.
3. Add the smallest evidence task, experiment, decision, obligation, or deliverable needed to resolve a question.
4. Give every open node an owner, dependency set, next action, and completion condition.
5. Attach evidence to the node and decision it informs.
6. Recompute the ready frontier after accepted evidence or a changed dependency. Accepted v0.6 handoffs project findings, uncertainties, decisions, implementation-ticket nodes, and dependency edges into the canonical map. Deliverables with incomplete dependencies stay off `agent_ready`; post-start rerouting remains explicit rather than inferred.

Prefer breadth-first discovery: expose the major questions blocking the destination before deeply pursuing one branch. Admit a node only when it supports the desired outcome, the planning destination, or a surviving obligation.

## Choose what is next

Use the frontier returned by `status`, `resume`, or the latest accepted mutation. Run `next` only when a focused frontier projection helps; do not select from prose alone. Interpret ownership as follows:

- **Agent-owned and ready:** execute the bounded task or invoke the appropriate specialist.
- **Human-owned decision:** prepare a concise consequence receipt and pause dependent work.
- **External or evidence blocker:** record its owner and next action; continue only independent branches.

Prioritize work that unlocks the most blocked nodes, tests the riskiest falsifiable assumption cheaply, or satisfies the current stage gate with the least irreversible commitment. State why the recommendation has priority and what would change it. The user may override it; record the override and consequences.

## Invoke specialists without surrendering control

Use Workbench's embedded contracts for routing, destination challenge, data-model work, handoffs, and proof. The portable repository bundle supplies focused companions for feature planning, official OpenAI documentation, research, prototyping, diagnosis, test-driven implementation, code review, and merge-conflict resolution. Select one only when its method adds evidence or resolves a live uncertainty. Treat harness-native or separately installed skills as optional extensions, never as undeclared route prerequisites.

A specialist is a bounded method and handoff contract, not automatically another agent. Run related methods in the current agent when they share the same evidence and working context. Delegate only independent evidence work or a genuinely independence-sensitive review whose expected value exceeds the prompt, rereading, and synthesis cost. Never create one subagent per activity label.

Treat 150,000–250,000 tokens as a per-agent planning envelope, not a team allowance. Partition ready work when an independently completable task would otherwise push one agent beyond that envelope, or when parallelism or independent judgment has material value. Keep tightly coupled reasoning, shared-file changes, and small tasks together. Judge token economy across the whole team: delegation that merely duplicates discovery fails the routing test.

Each delegated assignment names one bounded outcome, its inputs and exclusive or clearly separated surface, completion condition, expected handoff, and authorization limits. Size it to finish within one agent session. If that is not responsible, require a resumable handoff before the envelope is exhausted. The coordinator consumes the handoff and re-checks only claims material to the route, decision, or gate instead of repeating the scan.

Give each method exact record references, one bounded question, the current phase checkpoint and included activities, expected handoff, applicable policy versions, and authorization limits. Share a compact evidence inventory instead of copying full upstream artifacts into every prompt. Accept only a handoff that identifies inputs used, findings, applicability, remaining decisions or blockers, produced artifacts, proposed node changes, and routing advice. One checkpoint normally accepts one consolidated phase handoff even when several methods contributed. Workbench—not the specialist—decides whether the lifecycle gate passed.

If no focused companion is available, apply the baseline method in Workbench's references and keep the node ready. Record a capability blocker only when the outcome genuinely requires a tool or domain capability absent from the environment; the absence of an optional skill is not itself a blocker. Do not silently collapse several domains into one claim.

## Correct the route when evidence changes

Before lifecycle start, append a routing revision with `revise-routing`. Its `expected-routing-revision` prevents concurrent or stale updates; its `supersedes` link binds the exact prior bytes; and `resolved_questions` makes human answers visible instead of silently rewriting the synthesis. A dropped unresolved question without a recorded answer is rejected. Lifecycle start binds the exact latest revision and freezes pre-start routing.

After lifecycle start, return conceptually to the earliest phase whose conclusion is invalidated. Preserve the work ID and prior events, supersede affected decisions or artifacts rather than rewriting them, and state what remains valid. The v0.6 runtime does not yet expose a post-start route-correction mutation, so keep dependent work blocked rather than editing state or creating a duplicate item. An unproven process that earns a bounded proceed decision should later compile the remaining software phases without restarting completed discovery or becoming universally “proven.”
