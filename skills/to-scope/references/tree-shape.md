# The tree, and how it is written down

Everything the draft phase needs: the three tiers and their boundaries, the criterion shape,
the slice marks, the story ids, the folder layout, and a worked rendering of all of it.

The node states and the signature block are not here. They are reached later, at sign-off, in
`sign-off.md`.

The worked rendering at the end uses **invented names**. It is a real workflow with every
person and every business detail replaced.

---

## 1. The three tiers

The scope tree **is** the workflow diagram viewed as an outline. The backbone runs in process
order and the build slice cuts horizontally across it. This is Jeff Patton's story map, adopted
by name.

**Epic - one end-to-end workflow. One per external trigger.**
Bounded at the front by a trigger the actor does not control, and at the back by a terminal
state where the actor stops caring or hands off for good.

**Feature - a contiguous run of steps owned by one actor.**
Bounded by a **handoff** (the work moves to somebody else) or a **wait** (the work stops until
something outside arrives). The actor is a property of the feature and is **never restated on
a story**; restating it would give the handoff test two sources of truth.

**The bound is handoff-or-wait. "One actor" describes what a run bounded that way normally
looks like; it is not a second test.** A step delegated to somebody who answers and hands
straight back - the carrier saying what it needs, the owner signing the form you sent them -
does not open a new feature. It is inside the run. A **handoff** is where the work leaves and
does not come back to you as the next thing that happens.

So a feature header may legitimately name a chain: *Actor: Tony Stark, then the carrier, then
the policy owner*. What it may not do is span a point where the process genuinely stops and
somebody else picks it up.

**Story - one step.**

`task` is not a tier. Nothing below the story.

### Every boundary is causal, and this is deliberate

Every published size test - a sprint, a two-week iteration, a twelve-week program increment -
is denominated in a unit this skill does not have. So each one is replaced by a boundary drawn
from the process itself. The names are conventional; the definitions are not.

The payoff is that the boundaries appear unprompted in raw speech. An expert who cannot describe
their workflow in general still says *"one I got today was a banker emailed my partner"* (an
external trigger) and *"then it depends on how fast they sign"* (a wait). You are not imposing
a structure. You are reading one back.

### The one structural test

**A story that belongs to two features is a defect.** It means the handoff boundary landed in
the wrong place. Move the boundary; do not duplicate the story and do not ask the expert. This
test costs nothing, runs by reading, and it is the second job the feature tier does. The first
is being the batching unit for sign-off.

### Non-process scope needs no tier

It either attaches at the step that consumes it, or it is non-functional and belongs to a
standing Definition of Done that attaches to the increment. **Do not re-elicit non-functional
criteria per story.** That is exhaustion by construction.

---

## 2. The criterion shape

Criteria attach at **story level only.** The epic shows the whole workflow with out-of-build
parts marked, and carries no criteria of its own.

Two blocks. A plain trigger and a response. No Given/When/Then, no Gherkin, no test syntax.

```markdown
**Works**
- The carrier needs an authorization → the insured or the policy owner signs it, and it
  reaches the carrier. `inferred`
  - from: *"they need a signed auth before they'll tell you anything"*

**Goes wrong**
- A trust owns the policy → you need the EIN of the trust and the signature of the trustee.
  `confirmed`
  - from: *"if it's in a trust you need the EIN and the trustee"*
```

The test the wording has to pass: **it can be read aloud to the expert**, who is not reading it
as a technical document. Anything
that cannot be is at the wrong altitude.

### The blocks and the marker are independent axes

**The block says which path. The `?` says whether it is answered.** They are not the same
question, and conflating them costs you the happy-path unknown, which has nowhere else to live.

- `Works` - the path where things go right.
- `Goes wrong` - the failure class. **An empty one is written on the page as `(empty)`**, never
  omitted. Omissions live in this block, and silence there is indistinguishable from
  completeness.
- A `?` line may appear in **either** block.
- A `Goes wrong` slot holding **only** `?` lines is a **known-unknown**: visibly different from
  a populated slot and from an empty one. Recorded ignorance is not fake completeness and the
  page has to show the difference.

### Checkability, at this altitude

> Could the expert say yes or no, looking at the finished thing?

That is the whole test. Not *is it testable*, which is a builder's question one rung down.

**A criterion that fails it converts to a `?`.** It is never rejected. This is why the skill
needs no separate rejection step and never writes a criterion it cannot check.

### What a criterion may not do

- **Name a UI location.** No screens, no buttons, no menus. Criteria have to survive the build
  choosing a different interface, and this skill stays out of design.
- **Hide a story.** A `Goes wrong` line that **hands off to a different actor** or that
  **waits** is not a criterion. It is a step, and it gets extracted as a story. This is the
  handoff-or-wait boundary rule doing a second job; no new rule is needed to catch hidden
  stories.

### `from:` lines - the unmerged statements

Every criterion carries the statements it was drafted from, **unmerged**, directly beneath it.

- **The quoted words only. No speaker. No timestamp.** Both would be authoritative-looking and
  wrong. A timestamp locates into a raw export that merges crosstalk, so it points into
  corrupted attribution. A speaker fails for a subtler reason: in the designed-against sample
  the *builder's* recap of a prior call carried full domain authority, so even an accurate
  label does not tell you whose requirement a sentence is.
- **Two statements under one criterion is a prompt to check, not an automatic split.** Apply
  the same test phase 2 uses: **would they produce different criteria?**
  - **Different criteria - split.** You flattened two things into one, and leaving them
    stacked is the deletion the `from:` lines exist to make visible.
  - **The same criterion - keep both.** They corroborate. *"the name was on it"* and *"the
    policy number was there too"* are one fact said twice, and splitting them manufactures a
    second criterion nobody needs. Volume is the second form of exhaustion.
  - **They cannot both be true - leave them.** Phase 2 will find it.
- **No `from:` lines means you proposed it.** Write `- from: (none)`. Nothing needs storing;
  the page already shows it. There is no `agent-proposed` state for the same reason.

This is a statement, not a citation. The distinction is load-bearing: a transcript-line
citation was refused three times in the design, always because a structureless transcript
corrupts exactly the attribution such a citation would claim.

### `inferred` / `confirmed`

Every criterion carries one of these two words. **A closed two-value set, no free text.**

- `inferred` - you wrote it. Nobody has looked at it.
- `confirmed` - the expert corrected it or agreed to it, in a session.

This exists to make one number countable: a feature signed with every criterion still
`inferred` is a review that visibly did not happen. Roughly 27% of what a model extracts from a
transcript is not a requirement at all - two thirds of that being current manual work misread
as a request to automate it - and without this mark, none of it is visible on the page.

### How many

**Three to five per story is an agent-side drafting smell and is never enforced on the expert.**
It is one published count and it is worth listening to when you are drafting. It is not a cap,
because a cap creates pressure to under-record, which is the same failure from the other side.

The real control is **the rejection test**: would the expert reject the finished thing if
this were not true? A criterion that fails it is **marked out-of-build, not deleted.** Nothing
silently leaves the record.

**At most one worked example per rule.** A rule needing two examples is a wrong rule - split
it. Per-rule examples are how volume gets back in through the back door, and volume is the
second form of exhaustion.

### The goal line

Every story states its goal, or points up to the feature's with `↑`.

**A step whose goal cannot be stated even by pointing up is a suspect node.** Flag it. This is a
documentation rule doing a second job as a hole-finder: if you cannot say why a step exists,
you have either misread the process or found a step nobody could justify.

---

## 3. The slice

One axis, two values, on the **story**: `in-build` or `out-of-build`.

**Out-of-build carries a required reason, from a closed set of two:**

- `manual by nature` - a person does this and will keep doing it. A signature on paper, a
  conversation.
- `unanswered` - it is out of the build because nobody answered the question.

The two are not interchangeable and must never be rendered the same way, because **the count of
`unanswered` prints on the epic index.** Read that number. If it grows, the tree bought
acceptance by pushing hard steps out of the slice instead of asking about them - the binding
constraint failing in a new and almost silent form.

*Stays manual* is the wrong axis. It names who works. The question the build needs answered is
whether the build covers the step.

---

## 4. Story ids: allocate once

**A number is assigned once and never reassigned or reused.** An inserted story takes the next
free number in its feature, so `2.9` may sit between `2.1` and `2.2`.

**Process order comes from position in the file, never from the number.**

Without this, inserting a step at the head of a feature renumbers `2.1`, and every ticket naming
`2.1` now points at a different story. That is *silent redirection*, which is undetectable.
Staleness is detectable; redirection is not, which is why the cost is paid here.

An opaque id was considered and rejected: it buys nothing allocate-once does not, and costs in
every place a human reads the token.

---

## 5. The folder, and the second dimension

```
scope/<epic-slug>/
  README.md              epic header, backbone table, three derived views
  F1-<slug>.md           one file per feature
  F2-<slug>.md
  handover/
    F1-<date>.md         frozen copy, written at sign-off
```

**A folder per epic, a file per feature.** The file unit does three jobs at once: freezing
becomes a file copy with no generator and no chance to reword what was signed; the file unit
matches the signable unit, so a signature is protected by being a file that stops changing; and
it matches a session that ends at a feature.

The cost is that you cannot read the whole process by scrolling one buffer. That is affordable
only because **the expert never reads the tree.** The readers are the builder and the agent,
and the backbone table is the process at low resolution.

### The store is one-dimensional. The second axis is derived.

A story map has two axes and markdown has one. Rendering the grid literally was tried and
failed twice over: markdown tables do not wrap, so six features are already too wide in a
terminal or a PR diff, and the grid holds slice membership that the story files hold too - the
same fact in two places with nothing keeping them level.

So there are **three derived views** in the epic `README.md`: **slice**, **circle-back**,
**holes**. They are written by scanning the feature files. **They are not a store**, so they
cannot disagree with the tree. Re-derive them; never edit them in place.

---

## 6. Worked rendering

Invented names throughout. **`client` below is a person inside the modelled business - the
policyholder.** It is not the expert seat, and nothing stops a business from having its own
`client`, `customer` or `user`. That is why the seats are named by what they own.

### `scope/policy-review/README.md`

````markdown
# Epic - Policy review, from an inbound question about a policy we did not sell

Trigger: a banker emails Bruce Banner one page of a statement and asks *"what do you think
about this?"*
Terminal outcome: the client keeps the policy, replaces it, or we become agent of record.

Epic sign-off makes two claims: **this is the workflow**, and **this is the part we build**.

## Backbone - in process order

| # | Feature | Actor | Ends at | State | Confirmed | `?` |
|---|---|---|---|---|---|---|
| F1 | [Take in the request and start a case](./F1-take-in-request.md) | Tony Stark | wait on carrier contact | **signed** 2026-08-04 | 6/6 | 0 |
| F2 | [Get authority to see the policy](./F2-get-authority.md) | Tony Stark, carrier, owner | wait on a signature | **deferred** 2026-08-04 | 1/6 | 3 |
| F3 | Gather the numbers | Tony Stark | handoff to analysis | provisional | 0/4 | 0 |
| F4 | Analyse and build the comparative | Tony Stark | handoff to presentation | provisional | 0/6 | 2 |
| F5 | Present and decide | Tony Stark, client | client's decision | provisional | 1/4 | 2 |
| F6 | Become agent of record | Tony Stark | client signs | provisional | 1/2 | 0 |

`Confirmed` counts criteria the expert corrected or agreed to. A feature that is signed with
a low count is a review that did not happen.

## Slice - derived from the feature files

**In build:** 1.1, 1.2, 1.3, 2.1, 2.3, 3.1, 3.2, 4.1, 4.2, 5.2.

**Out of build:**

| Node | Reason | Note |
|---|---|---|
| 2.2 | `manual by nature` | The policy owner signs paper. |
| 5.1 | `manual by nature` | A person has the conversation. |
| 6.1 | `manual by nature` | The client signs the AOR paperwork. |

**Out of build for the reason `unanswered`: 0 of 13 stories.**

Read this number. If it grows, the tree removed hard steps from the build instead of asking
about them.

F3 cannot start until 2.2 finishes by hand. The build must know this.

## Circle-back - derived. Every `?` on the tree, in backbone order

| Node | Question | State |
|---|---|---|
| [2.1](./F2-get-authority.md#21-ask-the-carrier-what-it-needs) | Is the carrier requirement a fact we hold per carrier? | **deferred** |
| [2.1](./F2-get-authority.md#21-ask-the-carrier-what-it-needs) | Is "carrier requires nothing" a separate path? | open |
| [2.2](./F2-get-authority.md#22-get-the-authorization-signed) | What chases a case that waits on a signature? | **conflict**, 2 views |
| 4.1 | What general check is the Steve Rogers case an example of? | open |
| 4.1 | Is "no sale, good shape" an outcome we record? | open |
| 5.2 | Does a case that comes back stay the same case? | open |
| 5.2 | What holds a case until the next anniversary? | open |

## Holes - derived from the shape. These cost the expert nothing

- 2.3 has an empty `Goes wrong` and an obvious failure: the carrier refuses after
  authorization.
- F2 holds a wait. Nothing chases it.
- F5 has a branch, *client wants nothing*. It does not come back and it does not stop.
- Bruce Banner receives the trigger. They are in no feature.

## Glossary

The glossary is `CONTEXT.md` in the repo root. It is not in this folder.
````

### `scope/policy-review/F2-get-authority.md`

````markdown
# F2 - Get authority to see the policy

Epic: [Policy review](./README.md) · Feature 2 of 6
Actor: Tony Stark, then the carrier, then the policy owner
Starts at: a case exists, with a named person and a policy
Ends at: the wait on a signature - handoff to the policy owner
Confirmed: 1 of 6 criteria

**State: deferred**

```
Deferred 2026-08-04. Tony Stark. On the call.
"Go with your recommendation."
This is not an agreement. Ask again in the next session.
```

**This feature cannot cross to the build.** Story 2.1 holds two open `?`. Story 2.2 holds one.
Story 2.3 is clear. Close every `?` on this feature, or mark that one story out of build.

---

## 2.1 Ask the carrier what it needs
Slice: `in-build`

Goal: establish what this carrier needs before it releases information.

**Works**
- Tony Stark contacts the carrier → the carrier states what it needs to release the policy
  information. `inferred`
  - from: *"depends on my relationship with the carrier internals"*

**Goes wrong**
- **?** Some carriers release with nothing. Is that a separate outcome, or the same path with
  an empty requirement?

**? Is the carrier requirement a fact we hold for each carrier, or can we not know it before?**
> Deferred 2026-08-04. Tony Stark. On the call.
> *"Go with your recommendation."*
> This is not an answer. Ask again.

---

## 2.2 Get the authorization signed
Slice: `out-of-build` - reason: `manual by nature`. The policy owner signs paper.

Goal: ↑

**Works**
- The carrier needs an authorization → the insured or the policy owner signs it, and it
  reaches the carrier. `inferred`
  - from: *"they need a signed auth before they'll tell you anything"*

**Goes wrong**
- A trust owns the policy → you need the EIN of the trust and the signature of the trustee.
  You do not need the signature of the insured. `confirmed`
  - from: *"if it's in a trust you need the EIN and the trustee"*

**? What happens to the case while it waits? Does anything chase it?**
> **Conflict.** Two statements. Both cannot be true of this node.
> - view 1 - nothing chases it: *"depending on which route that goes could delay or not"*
> - view 2 - a weekly follow-up chases it: *"I follow up every week"*
>
> Open. No view is chosen. When this closes, the view that loses stays here, marked
> *not chosen*.

---

## 2.3 Access the policy information
Slice: `in-build`

Goal: ↑

**Works**
- The authorization is in place → Tony Stark can reach the policy information through the
  carrier. `inferred`
  - from: (none)

**Goes wrong**
- (empty)

This story has no source quotes. The agent proposed it. Nobody said it.
The empty `Goes wrong` is a hole: nothing here covers a carrier that refuses after the
authorization is filed.
````

### What to read off that rendering

Five things, and each one is a rule above being visible rather than trusted:

1. **2.3 says on its own page that nobody said it.** `from: (none)` plus the empty `Goes wrong`,
   with the hole named in plain words underneath.
2. **2.2 is out-of-build with a reason**, so the epic index can count `manual by nature`
   separately from `unanswered`.
3. **The conflict on 2.2 is one `?` with two views and no party named.** It is not a new record
   type and it does not fork the criterion.
4. **The deferral on 2.1 carries the words.** Strip them and it reads as a signature.
5. **1 of 6 confirmed, and the feature is deferred.** That is the review visibly not having
   happened, printed at the top of the file and again on the backbone table.
