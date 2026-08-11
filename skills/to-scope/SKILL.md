---
name: to-scope
description: Turn a normalised transcript into a signed-off scope tree a build can run against, one feature at a time.
disable-model-invocation: true
---

# to-scope

Two seats, and this skill needs both filled.

- **The expert** does the work and owns the process. They cannot describe it.
- **The builder** owns the slice - the part that gets built. They do not own the process.

Whether the two share an employer decides nothing here. A client and an agency developer fill
these seats; so do a claims lead and the staff engineer down the hall.

The builder comes away from a call knowing less than the build needs. The call this skill was
designed against ends with the builder saying so, on the record:

> "So, it sounds like we need to figure out what all those different workflows are, those
> paths."

The expert is not withholding anything. Asked whether the workflow varies by case, they answer
*"yeah and no"* and narrate one anecdote instead of describing the class. **An expert cannot
describe their own work.** No amount of asking gets a general answer out of a cooperative one,
and asking harder makes it worse: sign-off given to stop the questions is worthless while still
looking exactly like approval.

This skill drafts the workflow as a tree, finds where the record contradicts itself, spends the
builder's patience before the expert's, and takes what survives back to the expert to be
corrected rather than composed. It runs in **five ordered phases: draft, coverage pass, conflict
pass, grill the builder, review with the expert.** Sign-off and the handover close it.

## The binding constraint

**Acceptance must never be won by exhaustion.** Two forms, both forbidden:

- **By asking.** An expert who signs off to stop the questions has given worthless approval that
  still reads as approval.
- **By volume.** Over-generation reads as completeness. A hundred generated stories exhaust an
  expert without ever interrogating them.

When a judgement call in this skill is genuinely ambiguous, **resolve it toward fewer questions
put to the expert.** That is not a preference. It is the rule every other rule here was derived
from, and it is why the review session asks *less* when a feature comes back with zero
corrections.

## The standing rules

Five rules hold for every phase. Nothing below overrides them.

**1. Paraphrase-back, not extraction.** You restate the workflow and the expert corrects it.
This converts their job from **generating** to **recognising**, which is the only lever that
exists against exhaustion. It also means the artifact is always provisional until corrected, and
the expert's word always wins over your wording.

**2. You own the hole.** The detector is your own inability to restate the workflow without a
gap. When a restatement will not close, that is your problem to record, never the expert's to
fix by being asked more questions.

**3. Two authorities, and you are neither.** The expert owns the process. The builder owns the
slice. You generate, you get things recognised, and you **never arbitrate**. The offence is
*"which of these is right?"* and the naming of parties - not the subject. So you may ask the
conflict; you may never ask the contest.

**4. Every device here leaves a mark.** Unmerged source statements under a criterion make
flattening a visible deletion. `inferred` / `confirmed` makes *zero corrections* countable. The
`unanswered` out-of-build count makes acceptance-by-evasion countable. `(empty)` makes silence
different from completeness. *not chosen* keeps the losing view of a closed conflict. The
off-tree count makes a silent omission countable. The seam checklist makes a signed story
nothing builds detectable. **A mark goes only when the thing it records is fixed, never because
the page looks cleaner without it.** The clean page is the failure.

**5. Zero corrections on a feature is a failure signal, not success.** Drafting for the person
you are eliciting from and handing them the draft is a named defect in the literature, and this
skill does it anyway, because the objection assumes someone who can co-author and the expert
seat is defined by the opposite. It is not free. What it costs is this rule: a feature that
comes back untouched means the wrong artifact was presented, and the answer is a better
presentation, **never more questions**.

## Step 0 - check the input

`/to-scope` reads a **normalised transcript**, never a raw export. A normalised file carries
front matter with `provenance:` and `labels:`, a flag list, and one speaker per turn.

- No normalised transcript present, or the file is a raw export - **stop. Tell the user to run
  `/to-record`, then re-run this.** `/to-record` is user-invoked, so you cannot reach it, and it
  opens by asking the user a question you cannot answer for them. Do not elicit over a raw
  export: its crosstalk is merged and its attribution is corrupt, which is exactly what you
  would be building the tree out of.
- More than one normalised transcript - read them all.
- A project doc, brief or proposal may be read too, **as background only.** It never acquires
  equal weight with what was actually said in a room. When the doc and the transcript
  disagree, the transcript is the record and the doc is a claim about it.

Read the flag list before the body. Flags marked `resolved` carry corrections that belong in
the tree - a `suspect-term` resolved to **WinFlex** means the tree says WinFlex, even though
the body still says *Windflex*, because the body is the record. Flags marked `unresolved` are
known defects of the input; carry them, and **do not convert one into a question for the
expert.** A `hard-stop` flag matters most: everything after it is deferred rather than
finished, and it reads exactly like agreement.

### Then name the seats

Say who holds each seat on this run, in one line, and have it confirmed before you draft.

**The expert seat is held by whoever does the work, never by whoever reports on it.** A manager
describing their team's process is a builder with unusually good exposure. So is anyone whose
account of the work is second-hand, however senior, and however certain.

- **No expert reachable** - draft the tree and say so. Every criterion stays `inferred`, no
  feature goes past `provisional`, and phase 5 does not run. A tree nobody corrected is a
  legitimate output; a tree nobody corrected wearing `confirmed` marks is not.
- **One person in both seats** - the same rule decides it, story by story. They hold the expert
  seat for work they do themselves, and the builder seat everywhere else. Their word on the
  slice never earns `confirmed`.
- **Several experts** - ordinary. Phase 3 applies no cross-speaker filter, so disagreement
  between them surfaces as a conflict like any other.

## Phase 1 - draft the tree

Read `references/tree-shape.md` before you write anything. It holds the tier boundaries, the
criterion shape, the slice marks, the story ids, the folder layout and a full worked rendering.
The short version, so the shape is in view:

- **Epic** - one end-to-end workflow, one per external trigger. Bounded by a trigger the actor
  does not control, and a terminal state where they stop caring or hand off.
- **Feature** - a contiguous run of steps owned by **one** actor, bounded by a handoff or a
  wait.
- **Story** - one step.

Every boundary is causal; `tree-shape.md` holds why. `task` is not a tier.

The tree **is** the workflow diagram viewed as an outline: you project the process the expert
already described, in the order it happens.

Write to `scope/<epic-slug>/` in the target project: `README.md` for the epic, one file per
feature, `handover/` created at sign-off.

Then, per story: criteria in the two-block shape, each carrying its marks.

**Steps that stay manual stay on the tree**, marked out-of-build. This is what makes an epic
sign-off two claims rather than one: *this is my process*, and *this is the part you are
touching*. A manual step deleted from the tree takes the second claim with it.

**A story that belongs to two features is a structural defect.** Report it and move the
boundary. It means the handoff landed in the wrong place, and you found it by reading - it
costs the expert nothing.

Phase 1 is done when every story carries all five marks and **you cannot find another hole by
reading**:

- a goal line, or `↑`
- a `Goes wrong` block, populated or `(empty)`
- a `from:` line under every criterion, or `(none)`
- `inferred` or `confirmed` on every criterion
- `in-build`, or `out-of-build` with a reason

Not when the questions are answered. Questions are recorded as `?` and stay open.

**This test reads the tree, so it can only find holes inside what you drew.** Every one of the
five marks sits on a node that exists, and a workflow nobody drafted carries no marks - so no
mark can be missing from it. Phase 2 is the test that reads the other direction.

## Phase 2 - the coverage pass

Run this AFK, as a **separate pass with no drafting job at all**, for the same reason phase 3
is run that way. A model drafting a tree will not stop to list what it declined to draft, and
an omission it never wrote down is one it will report as completeness.

**Phase 1 walked the tree. This pass walks the record.** That inversion is the whole of it.

**Its only output is: this stretch of the record names work, and here is where it went.**

Three destinations, and there is no fourth:

- **a node** - cite the epic and the story id
- **a named hole** - written into the `Holes` section of an epic index, with what it would take
  to close it
- **an off-tree note** - written into an epic index with the reason it is not on a tree

How the walk is run:

- **No seat filter. Walk every speaker.** The seat rule decides who can *confirm* a criterion.
  It never decides whose words get read. Material from the builder is routed like anything else
  and lands `inferred`, which is what it would have been anyway. Reading the expert's turns as
  the process and everyone else's as framing is the failure this pass exists to catch.
- **A trigger with no epic is the finding this pass is for.** An epic is one per external
  trigger, so read the record for triggers the actor does not control and check each one has an
  epic. A workflow the expert names in six words is still a workflow.
- **A `prior-context` flag is not a defect to route around.** It marks material carrying
  authority from a call you do not hold. It goes to one of the three places like everything
  else. So does anything after a `hard-stop`.
- **Off-tree is a decision, not a deletion.** *It is not a workflow - no trigger anywhere in the
  record* is a legal reason. *The expert did not say it* is not, and neither is *it did not fit
  the shape*.
- **No cap**, and for the reason phase 3 gives. Thirty orphans tells you the draft read one
  anecdote as the whole process. Truncating to five hides that.

**Print the three counts on every epic index**, beside the `unanswered` count. This pass detects
silence, so its own output has to be countable or it reproduces the defect.

What closes: a named candidate epic is drafted by **re-entering phase 1 for that epic alone.**
Where the record is too thin to draft one without inventing it, it stays a named hole and says
so. Phase 3 runs once nothing in the record is unrouted.

## Phase 3 - the conflict pass

Run this AFK, as a **separate pass with no drafting job at all.** That is the whole point of
it. Models detect a conflict reliably and then commit to one side without telling you
somewhere around 97.5% of the time, silently favouring whichever speaker sounded more formal -
and that is a *generation* failure. A pass with nothing to produce gives suppression nowhere to
hide.

**Its only output is: these two statements are on this node and they disagree.**

- A conflict is **two statements attaching to the same node that cannot both be true of it.**
  The tree supplies the pairwise structure; walk the nodes, not the transcript.
- **Self-contradiction and two-party disagreement go through the same channel.** No
  cross-speaker filter. One person contradicting themselves across twenty minutes is the common
  case in real material, and a filter defending the multi-party framing would discard it.
- **Two statements conflict only if they would produce different criteria.** This one test
  keeps restatement drift, refinement and ordinary temporal change out of the list.
- **No recency rule.** *The later statement supersedes* is resolution-by-preference wearing a
  process's clothing. The one exception is a speaker marking their own correction, which is
  one statement and not two.
- **No cap.** Forty conflicts tells you the draft is wrong. Truncating to five tells you
  nothing and hides the same fact.
- **A conflict is written as a `?` holding two views**, not as a new record type. It inherits
  blocking, the circle-back view, and the two exits that already exist. Name no party.
- **Never fork a criterion into two.** A fork carries no `?`, so it would cross the zero-`?`
  seam intact and be resolved silently downstream with the expert's signature already on it.
  The contested criterion converts to a `?`; the uncontested criteria on the same node are
  left alone, so the step does not vanish from the expert's view while one aspect is disputed.

Closure keeps the loser. When a conflict closes, the losing statement stays on the node marked
*not chosen*, so a signature never erases which view lost months before anyone learns the
choice was wrong.

## Phase 4 - grill the builder

Invoke `/grilling`, **unforked**, and point it at **the builder**.

Every hole the builder can close is a question the expert never sits through. That makes this
phase an anti-exhaustion device, and it is why it runs before the expert sees anything.

- Hand it the conflict `?`s **alongside the ordinary ones, procedurally indistinguishable.**
  The cheapest surfacing path has to be the default one, or it will not be taken.
- Challenge the builder on **the slice** and never on the domain. **Exposure is not authority.**
  A builder who sits beside the work still answers a domain question from belief, and a belief
  answered under pressure enters the tree looking exactly like the expert's account of it.
  Grilling does not extract that answer, it manufactures it.
- The full contest belongs here. This is the one place where *these two views disagree, which
  is it?* is a legal question, because the builder is not the party being exhausted.

Update the tree with what closes. What does not close stays a `?` and goes to the expert as a
neutral fact question, never as a contest.

## Phase 5 - the review session

Read `references/session.md`. It is reached only here and holds the script, the stopping rules
and the evidence behind them.

Per feature, **two moves in order** - the open `?` first, then the feature said back as a short
narrative with *what is wrong with it?* The criteria are **never read out.** No boundary question
is ever put to the expert.

Budget is **one paraphrase per feature plus that feature's open `?`**, so the cost does not grow
with the size of the draft. That is what phase 1 was drafting for: a thorough tree costs the
expert nothing extra.

**The artifact is the residue of a session, never a substitute for one.** A run that produces a
beautiful tree and no session has failed, however good the tree is.

## Sign-off

Read `references/sign-off.md`. It holds the states, the four fields of a signature, why a
deferral needs the words, and the re-opening rule.

Sign-off is **decoupled from the session.** The session produces a *signable state*; signing
may land inside the call or after it.

- **An open `?` blocks sign-off of that story alone**, never its siblings.
- **A `?` closes two ways only:** an answer, or marking the node out-of-build with the reason
  `unanswered`. Never by aging out, never by a guess.
- **A signed feature is a file that stops changing.** The signature is protected structurally,
  not by discipline.

## The handover

Read `references/handover.md` at sign-off. It holds the copy transform, the two handoff edges
and the seam checklist.

Only a feature with **zero open `?`** crosses. The handover file is a **copy** of the feature
file, transformed subtractively so the transform can be verified by reading it, and frozen. It
is read by both the spec step and the ticketing step, so the criteria travel by reference and
every copy that could reword what the expert signed is removed.

Below the seam the build layer runs **unforked and untouched.**

## The glossary

Use `/domain-modeling` throughout, with **code cross-reference off and ADRs off.** This skill
holds no codebase model, deliberately - repo exploration belongs below the seam.

Invert its *propose a canonical term* move. **Upstream, the expert's word wins:** *job*, not
*work order*, with your alias noted beside it. The expert's vocabulary is the most expensive
thing this skill buys, and it is what makes what they agreed to still recallable tomorrow.
Named things survive; propositions evaporate.

The glossary **is** the repo's `CONTEXT.md`. There is no second glossary and no mapping for
anyone to keep level. Downstream is free to add terms and never to rename one; a forced rename
costs an ADR recording both words and the reason.

## Termination

Unlike `/to-record`, this skill does not end on a checkable test. It ends on a judgement, and
these are the things that make the judgement honestly:

1. Every feature reached in the session carries a state, and every deferral carries the words.
2. Every `?` is open, answered, or closed as out-of-build with `unanswered` recorded.
3. The three derived views in the epic `README.md` agree with the feature files, because they
   were re-derived and not edited.
4. The `unanswered` count is printed on the epic index and you have read it out loud. If it
   grew, the tree bought acceptance by pushing hard steps out of the slice.
5. Any feature that came back with zero corrections is named as such, marked `inferred`, and
   said at sign-off: *"you changed nothing here, so this is our reading, not yours."*
6. Nothing in the record is unrouted, and the off-tree count is printed with its reasons. A
   scope tree that reads as complete over a record it does not cover is the one failure here
   that nobody downstream can detect.

Report the feature states, the open `?` count, the `unanswered` count, and the off-tree count.
Hand back the path to `scope/<epic-slug>/`.
