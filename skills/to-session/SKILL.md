---
name: to-session
description: Run the review session against a scope tree that already exists, then sign off and hand over.
disable-model-invocation: true
---

# to-session

Reached with a scope tree already on disk and **the expert in the room.**

`/to-scope` drafts the tree, walks the record, finds the conflicts and grills the builder. It
stops there. **The expert being unreachable on drafting day is the normal case, not the
exception**, so the session is a separate run against a tree that already exists. This skill is
that run, and it is the **only** path to `confirmed`, to a state above `provisional`, and to a
signature.

**One entry point, run as many times as it takes.** A session ends at a feature; six features
is more than one call; signing may land a week after the call; a re-opened `?` comes back
months later. All four are the same re-entry, and none of them re-drafts anything.

## Why this is not a phase of `/to-scope`

The same argument the coverage pass and the conflict pass are run on. **A context holding the
drafting instructions drafts.** A resume path built as a branch of the drafting skill would
carry the tier definitions, the criterion shape and the record itself into the room with the
expert - and the failure would look like a helpful improvement to the tree.

Split this way, two rules stop being trusted and start being structural:

- **The skill that drafts cannot write `confirmed`.** It has no instruction that produces one.
- **The skill that runs the session cannot draft.** It never opens the record.

## The binding constraint

**Acceptance must never be won by exhaustion.** Two forms, both forbidden: by asking, and by
volume. An expert who signs off to stop the questions has given worthless approval that still
reads as approval. **When a judgement call here is genuinely ambiguous, resolve it toward fewer
questions put to the expert.**

Re-entry is a new way to break this rule. A second session is a second chance to ask everything
again, and the budget below is what stops it: **the paraphrase is spent per feature, not per
session.**

## Two rules that decide every mark in this skill

**Every device leaves a mark, and a mark goes only when the thing it records is fixed.** The
clean page is the failure. `inferred` / `confirmed` makes *zero corrections* countable. The
`unanswered` count makes acceptance-by-evasion countable. A deferral's quoted words make a
non-event different from assent. The review block, below, makes *a session happened* countable.

**Zero corrections on a feature is a failure signal, not success.** A feature that comes back
untouched means the wrong artifact was presented. The answer is a **better paraphrase, or
none** - never more questions. `references/session.md` holds the evidence and what to say at
sign-off.

## Step 0 - read the tree

**The feature files are the store.** Everything this skill needs to resume is already written
in them. There is no session file, no agenda and no position marker, and this skill will not
write one: a resume path with its own state is a second store that can disagree with the first.

1. **Find the tree** at `scope/` in the target project. No tree - **stop. Tell the user to run
   `/to-scope`.** Do not draft one.
   Read `scope/README.md`, the tree index, and check the **pass log** before anything else.
   **A tree whose grilling pass is not logged does not get a session**, and neither does one
   holding open `?` marked `new since grilling`. Stop and say so: every `?` the builder can
   close is a question the expert never sits through, and putting one to the expert that the
   builder could have answered is the binding constraint failing before the call starts. The
   same holds for an unlogged coverage pass - it is the only thing that would have found the
   workflow the tree missed, and the expert should not be the one who finds it.
2. **Read every feature file.** State line, `Confirmed: n of m`, every criterion and its mark,
   every open `?`, every review block and every signature.
3. **Re-derive the three views** - slice, circle-back, holes - by scanning the feature files.
   **Compare them with what the epic `README.md` says before you overwrite it.** A disagreement
   means a derived view was hand-edited, or the tree moved without re-derivation. Say so, then
   re-derive. Off-tree is the one store; leave it alone.
4. **Check the marks, before anything else happens.** These are the checks a later reader would
   run, and running them at the start of every session is what makes the marks worth having:
   - Every `confirmed` criterion sits on a feature carrying a **review block**. One that does
     not is a review that cannot be shown to have happened.
   - Every feature above `provisional` carries the block that earns it: a review block for
     `reviewed`, a signature for `signed`.
   - Every `Confirmed: n of m` header matches the body. Recount it.
   - Every deferral carries the expert's words.
   - Every deferred `?` is still open.

   **Report a defect. Do not repair it by guessing.** A `confirmed` with no review block is
   settled by asking **the builder** whether a session was held - which costs the expert
   nothing. If it was not, the mark comes off and the feature returns to `provisional`.
5. **Take the position from the files**, in backbone order:
   - `signed` - closed. The file has stopped changing.
   - `reviewed` - **the paraphrase is spent.** Its open `?` are not: they are live and they are
     asked in move 1, with no second paraphrase.
   - `provisional` - the next one in backbone order gets both moves.
6. **Snapshot the story ids** you found, per feature, and the next free number in each. You
   check this again at termination.

## Step 1 - name the seats, again

Say who holds each seat **on this run**, in one line, and have it confirmed before you start.
The holder can change between the draft and the session, and between one session and the next.

**The expert seat is held by whoever does the work, never by whoever reports on it.** A manager
describing their team's process is a builder with unusually good exposure. So is anyone whose
account of the work is second-hand, however senior, and however certain.

**No expert in the room means there is no session today.** You may still sign a feature already
`reviewed`, and you may still take builder corrections - written `inferred`, spending no
paraphrase. Nothing else in this skill runs.

## The session

Read `references/session.md`. It holds the script, the budget, the stopping rules and the
evidence behind them. Per feature, **two moves in order**: that feature's open `?` first, then
the feature said back as a short narrative with *what is wrong with it?* The criteria are
**never read out.** No boundary question is ever put to the expert.

Three things it does not say, because they only arise on re-entry:

- **The budget is one paraphrase per feature, over the life of the tree** - not one per
  session. A feature carrying a review block does not get a second paraphrase because a new
  session started.
- **The five-questions-per-pass limit is per session**, and a later session gets its own five.
  Rank by Impact x Uncertainty as before. This is the one thing re-entry legitimately renews,
  and it is renewed by the calendar rather than by wanting to ask more.
- **A re-paraphrase deferred to "the end of the session" that never happened is still owed.**
  It is the first thing in the next session, and it writes a second review block.

Write a review block on every feature that got both moves, in the shape `sign-off.md` gives.

**Where a correction changes the tree, the shape is on the page.** This skill carries no tier
definitions and no criterion template, deliberately - it holds the ones it is editing. A
criterion the expert corrects keeps its blocks, its `from:` lines and its slice mark and changes
only what they said; a story the expert adds is written to match its neighbours in the file it
lands in, takes the next free number in that feature, and is marked `confirmed` because it came
from the expert in the room. Anything that cannot be written by matching the file in front of
you is drafting, and drafting is `/to-scope`.

## Sign-off

Read `references/sign-off.md`. It holds the three states, the **review block**, the four fields
of a signature, why a deferral needs the words, and the re-opening rule.

**Sign-off is decoupled from the session.** The session produces a *signable state*; signing may
land inside the call or a week after it. A run of this skill that holds no session at all and
only signs features already `reviewed` is an ordinary run.

- **An open `?` blocks sign-off of that story alone**, never its siblings.
- **A `?` closes two ways only:** an answer, or marking the node out-of-build with the reason
  `unanswered`. Never by aging out, never by a guess, and never by a session ending.
- **A signed feature is a file that stops changing.**

## The handover

Read `references/handover.md` at sign-off. It holds the zero-`?` gate, the copy transform, the
two handoff edges, the freeze and the seam checklist.

Below the seam the build layer runs **unforked and untouched.**

## What this skill refuses, and how each refusal is caught

A document prevents nothing. What every rule below has instead is the property the whole pack
runs on: **breaking it leaves something countable on the page**, and step 0 of the next run
counts it. A tree picked up twice is a tree whose marks were audited twice.

**1. The record is not opened.** No transcript, raw or normalised, is read here. The tree
carries every quote it needs on its `from:` lines.
*Caught by:* a story added in a session carries `from:` lines quoting **the expert in the room**,
on a feature whose review block is dated that day. A story carrying transcript quotes, on a
feature with no review block, was drafted.

**2. No epic and no feature is drafted here.** A workflow the expert names that is not on the
tree is written into the epic index `Holes` in their own words, with what it would take to close
it. Six words about a workflow produce five inventions, and volume exhausts an expert as surely
as questions do. A **story** added inside an existing feature is different: that is the expert
correcting the step list, which is exactly what the session is for.
*Caught by:* the holes section is on the page and counted. A new feature file with no review
block is visible in the folder.

**3. Nothing is renumbered.** Ids allocate once. An inserted story takes the next free number in
its feature, so `1.9` may sit between `1.1` and `1.2`.
*Caught by:* the step 0 snapshot, checked at termination - no id absent, no id moved to a
different story. Every frozen handover copy holds the ids it crossed with.

**4. A signed file does not change.** A re-opening writes below the old signature, dated. The
superseded snapshot stays.
*Caught by:* the handover copy on disk, which is frozen and was never the same file.

**5. A closed `?` does not re-open by being resumed.** It re-opens one way only: something below
the seam contradicts it, by the test in `handover.md`. A closed conflict keeps its losing view
marked *not chosen*.
*Caught by:* the circle-back view is derived from **open** `?` only, so a closed one cannot walk
back into the question list by being re-derived.

**6. `confirmed` means the expert corrected it or agreed to it, in a session.** A builder
correction is taken and written `inferred`, and it does not spend the feature's paraphrase.
Nothing else earns the mark, because the mark exists to count a review that did not happen.
*Caught by:* the review block. No block, no `confirmed`.

**7. The derived views are never edited in place.** They are re-derived from the feature files.
The **pass log on the tree index belongs to `/to-scope`**: this skill reads it and never writes
a line to it, because it runs none of those passes.
*Caught by:* step 0 re-derives and compares before overwriting, and a pass line dated after the
last draft with no work behind it is visible against the tree it claims to have walked.

**8. The stopping rules are counted, not judged.** Three deferrals in a row stops the pass - not
the question, the pass. At most five questions per pass. Agreement and disengagement sound
identical in the room and identical in a transcript, so by the time it *feels* like the expert
is finished, the record already holds a lot of approval that means nothing.

## If the record changed since the tree was drafted

**Nothing here reads the record, so a changed record cannot move a session.**

The `from:` lines are **statements, not citations** - the tree quotes what was said, and a
re-normalised source does not invalidate a quotation the tree already holds.

New material, or a `/to-record` flag that resolved into a corrected term, is **drafting work**.
It goes back to `/to-scope`, which extends the existing tree on the affected epic alone, without
renumbering and without touching a `confirmed` criterion or a signed file. Run it **before** the
session, never during one.

A wrong term is also caught free in the room: the paraphrase is spoken in the expert's own
vocabulary, and a wrong word is the cheapest correction there is.

## The glossary

Use `/domain-modeling`, with **code cross-reference off and ADRs off**. It ships as
`domain-modeling` standalone and as `mattpocock-skills:domain-modeling` inside that plugin;
either will do. If neither is installed, apply its one inverted rule inline: **the expert's word
wins** - *job*, not *work order*, with your alias beside it. A correction in a session that
renames a thing updates the glossary in the same sitting.

The glossary **is** the repo's `CONTEXT.md`. There is no second glossary.

## Termination

This skill ends on a judgement, and these are the things that make it honestly:

1. Every feature reached in this session carries a state, a review block, and the expert's words
   on every deferral.
2. Every `?` is open, answered, or closed as out-of-build with `unanswered` recorded.
3. No story id changed, and no id from the step 0 snapshot is missing.
4. The three derived views agree with the feature files, because they were re-derived.
5. The `unanswered` count is printed on the epic index and you have read it out loud. If it
   grew, the session bought acceptance by pushing hard steps out of the slice.
6. Any feature that came back with **zero corrections** is named as such, left `inferred`, and
   said at sign-off: *"you changed nothing here, so this is our reading, not yours."*
7. Every `confirmed` written today sits under a review block written today.

Report the feature states, which features are still `provisional`, the confirmed counts, the
open `?` count, the `unanswered` count and the off-tree count. Hand back the path to
`scope/<epic-slug>/`, and say plainly what remains: **a tree with provisional features is a
session that has not finished.**
