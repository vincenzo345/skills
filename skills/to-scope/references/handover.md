# The handover

Reached at sign-off. Below this file, `/grill-with-docs`, `/to-spec`, `/to-tickets` and
`/implement` run unforked and untouched.

---

## The gate

**Only a feature with zero open `?` crosses.**

Nothing unresolved reaches a skill that will resolve it silently. `/to-spec` is contractually
forbidden to interview - *"Do NOT interview the user - just synthesize what you already know"* -
so an open question that crosses is not asked, it is answered by synthesis, with the client's
signature already on the page.

There are exactly two exits, and they are the ones a `?` already had:

1. **Answer it.**
2. **Mark that story `out-of-build`**, reason `unanswered`. Which prints on the epic index and
   gets counted.

Aging out is not an exit. A guess is not an exit.

## Why the feature is the unit

The story is the **content** that crosses; the feature is the **batch**.

A per-story handover was the original design and it was wrong: a story is one step, and
`/to-spec` is built around *a long list of user stories*, so handing it one step at a time
starves it. The tier is picked by `/to-spec`'s own one-seam rule - an epic crosses many seams; a
feature ends at a handoff and so is exactly one.

---

## The transform: copy, then subtract

**The handover file is a copy of the feature file.** It is not generated from it, not
regenerated, not re-rendered. Every step at which the wording the client signed could be
reworded is removed by making the operation a file copy.

Then subtract, and **only** subtract, so the transform can be verified by reading the two files
side by side:

**Remove:**

- the `` `inferred` `` / `` `confirmed` `` mark from the end of every criterion;
- the `- from:` lines under every criterion;
- the "cannot cross" banner, which no longer applies.

**Keep, character for character:**

- the story ids and their order in the file;
- the goal line of every story;
- the `**Works**` and `**Goes wrong**` blocks and every bullet in them, including `(empty)`;
- the slice mark and its reason on every story;
- the signature block.

**Add:**

- the frozen header and the do-not-edit line;
- the epic name and the trigger;
- the two handoff edges;
- the `/to-tickets` section and the seam checklist.

**Change nothing else. Reword nothing.** Not the criteria, not the goals, not the slice notes.
If a criterion reads awkwardly out of context, that is the price of the client having signed
those exact words.

### Why the marks are left behind

`inferred` / `confirmed` **does not cross.**

The signature makes every criterion in the file equal - that is what a signature is. Carrying
the marks across would hand a builder who was not in the room a measurement he cannot use,
against a negotiation he cannot reopen. It is the refused transcript citation in another form:
provenance that looks authoritative exactly where it can no longer be checked.

The `from:` lines go for the same reason. They did their job upstream, where two statements
under one criterion made a flattening visible. Downstream they would be read as authority the
tree deliberately never claimed.

### The two handoff edges

The payload is the feature **plus its two edges, each marked in-build or out-of-build.**

```
Incoming edge: the trigger - **out of build**. The email arrives by hand.
Outgoing edge: F2, get authority - **in build**.
```

This is not decoration. An out-of-build neighbour means the input still arrives by hand: the
same feature, with a completely different build, and the difference is **invisible in the code
and unguessable from the criteria.** A build that assumes its input arrives from software when
a person types it in has been built wrong, and nothing else in the payload says which it is.

### Freezing

Write to `scope/<epic-slug>/handover/F<n>-<date>.md`.

**It is a snapshot.** The tree keeps moving after handover and the signature must not. A new
signature makes a **new** file; the superseded one stays on disk, marked not current. Nothing
is overwritten and nothing is deleted.

---

## Story tokens across the seam

Inside the tree, a story is `2.1` - epic-local. **Once it crosses, it is qualified:
`<epic-slug>/2.1`.** A tracker serves the whole repo and epic-local numbering has to survive
that.

State the allocate-once rule in the file, because the reader downstream does not have the tree's
conventions: **numbers are allocated once and never reassigned. Process order comes from
position in the file, never from the number.**

## The instruction to `/to-tickets`

**Every ticket names the stories it serves.**

Derivation was rejected. *Which tickets serve 2.1* is a judgement, and the measured behaviour is
a model reaching that judgement and **not telling you 97.5% of the time** - at the one moment
the answer has to be right. Storing it on the coach side was also rejected: it would mean
writing a build-layer fact into a file that exists in order to **stop changing** once signed.

So the edge is stored on the build side, on the ticket, and `story -> tickets` is that same edge
read backwards. `/to-tickets` has no slot for it and cannot be forked, so the handover file
asks.

## The seam checklist

A request the reader is free to ignore is not a mechanism. This is what makes it verifiable.
The developer runs it **in the session that publishes the tickets** - not before:

- [ ] Every **in-build** story is named by at least one ticket.
- [ ] Every **out-of-build** story is named by **zero** tickets.

The first direction catches a signed story that nothing builds. The second costs nothing - same
query, same moment - and catches the build doing work the client did not buy.

A failure in either direction is a defect **at the seam**: fix the tickets, not the handover
file. The handover file is frozen.

### What the trace does and does not promise

**It under-reports; it never over-reports.** The link is read at exactly one moment - a `?`
re-opening on a signed story - so it does not need to be continuously true, only answerable
then. A ticket that dropped its ids is invisible to the query. A ticket the query returns
genuinely serves that story.

Precision comes from the link. **Safety comes from the feature boundary**: the stop is taken
against the query *within that feature's open tickets*, so a dropped id costs recall inside one
feature rather than correctness across the repo.

---

## When the repo contradicts a signed story

It happens below the seam, and the test is the criterion test this skill already has:

> Does it change what the customer would see?

- **No** - a database, a library, a schema choice. It is settled below the seam. The customer's
  patience is not spent on it.
- **Yes** - it goes back across the seam and becomes **an ordinary re-opened `?`** on that
  story. No new machinery. The spec is kept, and only that story's tickets stop - found by the
  query above, inside that feature.

---

## Worked example

`scope/policy-review/handover/F1-2026-08-04.md`. Invented names.

````markdown
# Handover - F1, Take in the request and start a case

Frozen 2026-08-04 at sign-off. **This is a copy. Do not edit it.**
The tree moves. This file does not.

```
Signed 2026-08-04. Tony Stark. On the call.
"Yeah, that's how it works."
```

Epic: Policy review, from an inbound question about a policy we did not sell.
Trigger: a banker emails one page of a statement and asks what we think.

Actor: Tony Stark
Starts at: the email arrives
Ends at: the wait on carrier contact
Incoming edge: the trigger - **out of build**. The email arrives by hand.
Outgoing edge: F2, get authority - **in build**.

---

## 1.1 Identify who and what the page refers to
Slice: `in-build`

Goal: ↑

**Works**
- A forwarded statement page arrives → the person's name and the policy number are recorded
  against a new case.

**Goes wrong**
- The page carries no name and no policy number → the case is opened against the sender, and
  the missing identifiers are chased.

## 1.2 Put the case on the list
Slice: `in-build`

Goal: ↑

**Works**
- A policy review is identified → it enters the same pipeline as a sale, marked
  unknown-intent.

**Goes wrong**
- (empty)

## 1.3 File the document
Slice: `in-build`

Goal: ↑

**Works**
- A policy document arrives for a policy we are not the agent on → it is stored in the
  document library, not in policy management.

**Goes wrong**
- (empty)

---

The marks `inferred` and `confirmed` are not in this file. Every criterion here is signed.
They are equal. The words are copied from the tree; nothing was reworded.

---

## For `/to-tickets`

Epic slug: `policy-review`. Across this seam a story is named `policy-review/1.1` - epic-local
numbers, qualified once they leave the tree.

**Every ticket names the stories it serves.** Put the qualified tokens in the ticket body. A `?`
that re-opens on a signed story stops exactly the tickets that name it and no others; a ticket
that drops its ids is invisible to that query, so the story it serves cannot be stopped when the
answer changes.

Numbers are allocated once and never reassigned. Process order comes from position in this file,
never from the number - an inserted step takes the next free number in the feature, so `1.9` may
sit between `1.1` and `1.2`.

## Seam checklist

Run this when the tickets are published, not before. Both directions, same query, same moment.

- [ ] Every **in-build** story is named by at least one ticket:
      `policy-review/1.1`, `policy-review/1.2`, `policy-review/1.3`.
- [ ] Every **out-of-build** story is named by **zero** tickets: none in F1.

The second direction costs nothing and catches the build doing work the client did not buy. A
failure in either direction is a defect at the seam: fix the tickets, not this file. This file
is frozen.
````
