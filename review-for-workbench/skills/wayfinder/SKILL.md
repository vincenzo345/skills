---
name: wayfinder
description: Plan a huge, foggy effort as a shared map of decision tickets, resolving one informed decision at a time until a traceable handoff to specification is ready.
disable-model-invocation: true
---

# Wayfinder

Use Wayfinder when an effort is too large and uncertain for one session. It charts a shared map on the configured issue tracker and resolves decision tickets until the route to a buildable specification is clear.

Before starting, verify the model-invoked companions `/grilling`, `/domain-modeling`, `/research`, `/prototype`, and `/delivery-proof` are installed. Name missing dependencies and do not pretend their decision or proof gate ran.

## Plan, do not silently build

Wayfinder produces decisions and delivery obligations, not implementation. A `task` ticket may perform work needed to obtain decision evidence, but it does not deliver the product outcome. Execution begins through `/to-spec`, `/to-tickets`, and `/implement` unless the user explicitly defines a different planning destination.

Never resolve more than one non-research ticket per session. Refer to every map and ticket by its linked title, not a bare identifier.

## Two destinations

- **Desired outcome** — the real user or business result that must eventually be true. It does not become true merely because planning is complete.
- **Planning destination** — the artifact Wayfinder will make ready, normally a specification handoff.

Every scope decision must preserve the desired outcome. An item may be out of this map only if the desired outcome remains true without it, or if it is carried forward as an owned obligation.

## The map

The map is the tracker-native map artifact; its decision tickets are the tracker-native children defined by the adapter. The tracker should be documented in `docs/agents/issue-tracker.md`. Use its identity, labels or fields, paths, relationship, claim, and frontier operations. If no tracker has been configured, pause to run `/setup-matt-pocock-skills` instead of inventing a second convention.

The map is an index, not a duplicate store. Detailed resolutions live on their tickets; the map holds linked gists.

```md
# <Map title>

## Desired outcome
<observable real-world result>

## Planning destination
<artifact and readiness condition this map must produce>

## Notes
<constraints, linked evidence, tracker-specific instructions>

## Decisions so far
- [<resolved ticket title>](link) — <gist; state and provenance>

## Delivery obligations
- OBL-1 — <obligation>; owner/next artifact: <...>; discharged when: <...>; status: open

## Not yet specified
<in-scope fog that cannot yet be stated as a precise question>

## Out of scope
<excluded item, consequence, and why the desired outcome remains achievable>
```

## Decision tickets

Each ticket is one precise question sized for one fresh session:

```md
## Question
<the decision or investigation>

## Why it matters
<effect on outcome, scope, proof, or downstream work>

## Decision state
open | evidence-blocked | confirmed | explicitly-delegated | factual-evidence-backed

## Resolution provenance
<decision owner, consequence receipt, or evidence pointer>

## Delivery obligations surfaced
<new or changed OBL-* items, or none>
```

Use the configured adapter to decide whether a child is unclaimed and how to claim it. Prefer native blocking relationships where available and follow the adapter's body convention otherwise. The frontier is the tracker-defined set of open, unblocked, unclaimed children.

## Ticket types

Every ticket is either human-in-the-loop (HITL) or agent-driven (AFK). The agent never answers the human side of a HITL exchange.

- **Research** (AFK) — obtain primary-source facts with `/research`.
- **Prototype** (HITL) — create a cheap artifact with `/prototype` to answer a visual or behavioral question; the artifact is evidence, not implementation.
- **Grilling** (HITL) — resolve a consequential choice using `/grilling` and `/domain-modeling`.
- **Task** (AFK or HITL) — perform bounded work required to obtain evidence or unblock a decision, such as provisioning access. It is resolved when the evidence-producing task is done, not when the desired outcome is delivered.

## Fog of war

Create a ticket when the question can be stated precisely, even if its answer is blocked. Keep an item in **Not yet specified** only while the question itself is still too vague. As decisions clear the fog, graduate newly precise questions to tickets and remove their fog entry.

Evidence-blocked is an open state, not a resolution. Give it an evidence owner and next step. Do not close it because a recommendation sounds plausible.

## Out of scope

Out of scope means beyond this map, not unimportant. Record the consequence of exclusion and why all desired outcomes remain achievable. If the work is still necessary later, carry it as an `OBL-*` item with an owner or create a separate effort; do not let it vanish.

If an existing ticket proves out of scope, close it as excluded, record why, and remove it from the route. It does not become a completed decision.

## Invocation

### Chart the map

1. Use `/grilling` and `/domain-modeling` to name the desired outcome and the planning destination. Confusion cannot confirm either.
2. Explore the repository and tracker for facts, prior decisions, and constraints.
3. Map breadth-first: identify precise frontier questions, blocking edges, delivery dependencies, and the fog beyond them.
4. Create the map, then create tickets before wiring edges so real identifiers are available.
5. Start independent research tickets in parallel when agent capacity exists. Research is read-only unless artifact writes are authorized.
6. Stop. Charting does not resolve a ticket in the same session.

If there is no meaningful fog and the work fits one session, say Wayfinder is unnecessary and route to the appropriate smaller flow.

### Work through the map

1. Load the low-resolution map and the configured tracker operations.
2. Use the named ticket, or claim the first frontier ticket.
3. Load its full context and resolve it with the named supporting skill.
4. For consequential decisions, require the `/grilling` consequence receipt. A user-owned choice may resolve only as `confirmed` or `explicitly-delegated`; evidence may support it but cannot authorize it. Use `factual-evidence-backed` only for research or factual questions. Evidence-blocked tickets remain open.
5. Append or update `OBL-*` items, new tickets, blocking edges, and newly cleared fog.
6. Close only a genuinely resolved ticket and append its linked gist to **Decisions so far**.

Expect concurrent tracker edits; re-read before mutating relationships.

## Handoff gate

When no decision tickets or fog remain, run `/delivery-proof` on the map before declaring the planning destination reached. If that companion skill is not installed, apply this checklist directly; its requirements do not disappear. Require:

- every desired outcome traces to settled decisions and downstream obligations;
- every user-owned consequential resolution is confirmed or explicitly delegated after an understood consequence; factual resolutions are evidence-backed;
- every `OBL-*` item has an owner or next artifact and a discharge condition;
- exclusions do not make the desired outcome false;
- unresolved or evidence-blocked items remain visible rather than being called complete.

Then hand off to `/to-spec`. Wayfinder is complete when its planning destination is proven, not when the desired outcome is implemented.
