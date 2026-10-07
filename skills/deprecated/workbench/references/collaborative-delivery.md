# Collaborative delivery

Use this method when `planning_posture` is `collaborative`, or when a full implementation route still contains material unsettled decisions. It is the behavioral bridge from discovery to specification, tickets, implementation, and proof.

## Working agreement

The agent owns fact-finding. The user owns consequential product, domain, scope, risk, and hard-to-reverse choices unless an explicit `decision-delegation` authorization covers them. Evidence may narrow a choice; it never transfers authority.

Maintain a dependency-aware design tree. Its frontier contains only questions or evidence tasks whose prerequisites are satisfied. For each round:

1. Inspect the repository and named sources before asking anything discoverable.
2. Classify each open item as factual, human-owned, delegable, or evidence-blocked.
3. Complete safe, agent-owned evidence work while independent human choices wait.
4. Ask one to three independent material questions, or one at a time when the user or repository prefers that style.
5. Explain why each answer matters, viable options and consequences, uncertainty, reversibility, and a conditional recommendation.
6. Record the answer, explicit delegation, rejected alternatives, and downstream effect as a decision record.
7. Recompute the frontier. Do not impose a fixed number of interview rounds.

Never answer the human side of the conversation, disguise a material choice as an assumption, or generate a long final plan while the target remains unsettled.

## Evidence router

Create evidence work only for a named uncertainty and decision it can unlock. Every evidence task records:

- question and decision unlocked;
- method and why it is proportional;
- completion condition and falsifier;
- authority and cost/time boundary;
- environment, seam, population, or journey exercised;
- what the result cannot prove.

Choose the method by uncertainty:

| Uncertainty | Method and output |
|---|---|
| Current code, behavior, data flow, tests, or policy | Repository reconnaissance with cited paths and observed behavior |
| External API, platform, regulation, or established practice | Primary-source research with dated citations |
| Vocabulary, lifecycle, ownership, or bounded-context ambiguity | Domain model or ADR with terms, states, responsibilities, and invariants |
| Visual hierarchy or interaction choice | Mockup for human reaction; record the choice it tests |
| State or behavioral choice discussion cannot settle | Throwaway prototype at the disputed public seam |
| Technical feasibility or integration risk | Bounded design POC with success/failure criteria |
| Performance, reliability, volume, or operational claim | Measurement or simulation with population and resolution |

Read-only inspection and research may proceed automatically. Obtain the relevant authority before mutating prototypes or POCs, external publication, live-system effects, sensitive-data access, or material cost. A local prototype or POC proves only the exercised seam and environment.

## Shared-understanding gate

Before collaborative work leaves outcome framing, create one current `shared-understanding` artifact marked `ready`. It contains:

- desired outcome and affected actors;
- current problem and evidence;
- canonical domain terms and responsibility boundaries;
- target journey, workflow, or state model;
- in-scope and out-of-scope behavior;
- constraints and invariants;
- confirmed and explicitly delegated decisions with provenance;
- rejected alternatives and accepted consequences;
- remaining uncertainty, blockers, and owned evidence work;
- observable success and intended proof.

Show the artifact as a compact synthesis, invite correction, and wait for confirmation. Record confirmation as a `confirmed`, `user-owned` decision whose `artifact_inputs` cites that artifact. A correction supersedes the artifact; it does not reject the work item.

Delegated posture may omit confirmation only when all consequential choices are covered by explicit decision-delegation authority. Otherwise switch to collaborative posture or leave the artifact blocked.

## Ready specification

Synthesize the confirmed understanding and accepted evidence; do not restart the interview. A specification marked `ready` uses stable IDs:

- `OUT-*` outcomes and observable success;
- `US-*` user or operational stories;
- `INV-*` invariants;
- `AC-*` criteria with proof level, environment, public seam or journey, independent oracle, expected nonzero population, terminal state, procedure, and evidence location;
- `DEC-*` settled decisions and provenance;
- `DEP-*` external dependencies;
- `OBL-*` surviving obligations, owner, and discharge condition.

Also define interfaces, state ownership, failures, compatibility, rollout, recovery, and exclusions. Preserve bidirectional traceability. Mark the artifact `draft` or `blocked` when a behavior-changing decision or orphan ID remains; the specification gate accepts only `ready` plus passed artifact-validity proof.

## Executable tickets

Turn a ready specification into tracer-bullet vertical slices. Each implementation ticket:

- fits one fresh implementation session;
- delivers a complete user-visible or operational increment across required layers;
- cites unchanged source IDs and criteria;
- separates blockers-to-start from later verification dependencies;
- names obligations it discharges;
- specifies a public test seam, independent oracle, proof evidence location, and done condition;
- is marked `ready` only when an implementer need not invent behavior.

Persist one ready `delivery-plan` with the coverage matrix, one ready `implementation-ticket` per slice, and one agent-owned `deliverable` map node per ticket. Put source IDs on the node, cite the ticket artifact in `evidence`, and express blocking order through `depends_on`. Add an outcome-verification ticket when implementation slices cannot prove the destination.

Show the user ticket titles, delivered behavior, blockers, source coverage, and proof levels. Require confirmation only when the breakdown changes scope, sequencing, ownership, or evidence materially. Local ticket records need no tracker authority; publishing them does.

## Ticket execution

After ticket approval and implementation authorization:

1. Read `next`; choose an agent-ready ticket whose dependencies are terminal.
2. Atomically claim it with `claim-node --expected-revision`.
3. Implement test-first at the agreed public seam, preserving pre-existing work.
4. Review the actual delta from the pinned starting state.
5. Accept a ticket-scoped handoff with `prepare-handoff.py --accept-only`; include implementation/review artifacts, passed proof, and a node update to `completed`.
6. Re-read the returned frontier and continue with newly ready tickets.

Do not complete a ticket with failed or missing proof, an unresolved blocking review, or weakened source criteria. Do not advance the implementation stage until every required deliverable is completed or explicitly excluded/superseded by an authorized upstream change. Pause only for a user-owned decision, failed assumption, unavailable evidence, external prerequisite, concurrent-state conflict, or action outside authorization.

## Bounded fast lane

Use the fast lane only when all are evidenced:

- observable behavior is already clear;
- no material product, domain, architecture, scope, risk, or proof choice remains;
- blast radius is bounded;
- acceptance criteria and an independent oracle are obvious;
- work fits one session;
- no migration, external coordination, or multi-ticket dependency graph is needed.

Record a compact execution contract with stable acceptance and obligation IDs, then implement and verify. If any condition fails, stop dependent work and use the supported route-correction path; never continue under stale assumptions or create a duplicate merely to bypass the route.
