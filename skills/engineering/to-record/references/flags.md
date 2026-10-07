# The six flags

A flag is a defect **of the record**. It is never a question about the domain.

The set is closed. Six types, no seventh. A defect that fits none of them is written out in
plain words under the flag list and named as unclassified, so that the closed set stays
closed and the gap stays visible.

Every flag carries: the type, a timestamp or other locator, the words it is about, and a
state - `resolved`, `unresolved` or `unresolvable`. `unresolved` is correct and expected
when the builder was not in the room.

Examples below use invented names in the format the skill was designed against.

---

## `suspect-term`

**Catches:** domain vocabulary the transcription mangled.

This is the class to design for, because it is load-bearing exactly where it is wrong. A
platform name, a product, a document type, an acronym - the words that will end up in the
glossary and in the tickets. The transcriber has never heard them and will render them as
whatever they sound like.

```
2:56  (Ada Wong) they all run on Windflex so eventually we integrate with that
```

`suspect-term` 2:56 - "Windflex" is probably **WinFlex**. unresolved

**How to spot one:** a word that carries weight in the sentence, is not ordinary English in
context, and is either capitalised oddly or spelled as it sounds. Near-misses of the same
term across the file are strong evidence: *ILS* in one place and *PILS* in another means at
least one of them is wrong.

**Pass 2 asks:** `"Windflex at 2:56 - WinFlex?"` A fact question, legal, cheap.

**Resolution goes in the flag, not in the body.** The body still says *Windflex*. The
correction is data about the record, and rewriting the body would break the preservation
contract for the one word most worth preserving.

---

## `merged-crosstalk`

**Catches:** two speakers on one line; a clause whose owner is uncertain.

The defect that makes this skill necessary. An export with no turn structure merges an
interjection into the middle of somebody else's sentence, and the sentence continues after
it - so the second half of a question can sit four lines below the first, inside the other
speaker's reply.

```
0:16  (Ada Wong) ever - (Ben Choi) Yeah, sometimes. (Ada Wong) vary?
```

Restructuring stitches *"Does that ever vary?"* back into one turn and lifts *"Yeah,
sometimes."* out as an interjection. Where the stitch is **not** certain, flag it:

`merged-crosstalk` 0:16 - who says "vary"? unresolved

**How to spot one:** a fragment that is not a sentence; a verb with no subject; a turn that
answers a question that has not finished being asked; a speaker marker appearing twice in
one line.

**Pass 2 asks:** `"Two speakers merged at 0:16 - who said 'vary'?"`

---

## `unlabelled-speaker`

**Catches:** a turn whose speaker the export did not name.

Assign a positional id - `Speaker A`, `Speaker B` - in first-appearance order, and use it
consistently. **Never infer identity from content.** Inferred attribution is fabricated
attribution, and it is undetectable afterwards, which is what makes it worse than a gap.

`unlabelled-speaker` 8:04 - three turns from an unnamed voice, id'd as Speaker C.
unresolved

**Where a mapping is obvious, propose it. Never apply it.**

> "Speaker C at 8:04 answers for the finance side and is called Priya twice by Ada - is
> Speaker C Priya?"

Proposing is a recognise move: the builder confirms or corrects, and confirmation is
cheap. Applying silently converts a guess into a fact in the record.

**Header state.** `labels: unverified` stays until the builder confirms them, for every
label in the file and not only the assigned ones. Wrong labels from the export are
undetectable from the export.

---

## `thread-abandoned`

**Catches:** a topic raised and closed without an answer.

```
14:40  (Ada Wong) what do we do about the tables that come in as images?
14:48  (Ben Choi) Yeah, I haven't had a chance to look at that.
```

`thread-abandoned` 14:40 - image tables raised, closed with "I haven't had a chance to
look". unresolved

**This is the one flag that touches the domain, and the line is precise.** The skill records
**that a thread stopped**. It does not ask what the answer would have been, does not mark it
important, and does not carry it forward as a question. `/to-scope` decides whether it
matters. Recording the stop is a fact about the record; asking what was missed is
elicitation.

**How to spot one:** an explicit deferral (*"I'll get back to you"*, *"let me check"*), a
subject change immediately after a question, or a question that receives an
acknowledgement rather than an answer.

---

## `hard-stop`

**Catches:** the call running out of clock.

```
23:10  (Ben Choi) I got about six minutes left, sorry.
```

`hard-stop` 23:10 - six minutes called; content after this point is compressed. unresolved

Everything after a hard stop is **deferred rather than finished**, and it reads exactly like
agreement: short answers, fewer questions, no pushback. Marking it means `/to-scope` can
tell a settled point from one that ran out of time, and the review session can revisit it
rather than treat it as signed.

One flag per call, normally at the point the clock is named - not one per turn after it.

---

## `prior-context`

**Catches:** any passage that refers to agreement, decisions or artifacts reached **outside
this transcript**.

```
0:00  (Ada Wong) remember we talked about the three buckets
```

`prior-context` 0:00 - "the three buckets" settled in an earlier call. unresolved

**First-class, and the reason is a mistake made live.** In the session that designed these
flags, the agent read exactly this passage as the *builder* proposing structure - a
builder's requirement misread into the expert's mouth, which is the single most common
extraction error there is. The builder, who was in the room, corrected it: the passage was
a recap of agreement reached in a prior call. It carries **full domain authority** despite
the builder's mouth saying it.

The finding is the flag:

> **A speaker label does not tell you whose claim a sentence carries.** Authority is a
> pass-2 fact, never a parse-time inference.

A passage flagged `prior-context` is the densest domain content in the file and the least
verifiable from it. Reading one transcript cannot tell you it was settled elsewhere - only
that it points somewhere else.

**How to spot one:** *"remember we talked about"*, *"as we discussed"*, *"the thing I sent
you"*, *"like we said last time"*, *"per the doc"*. Any deictic pointing outside the file.

**Pass 2 asks:** was this settled, with whom, and is there a record? If no provenance can be
given, mark the passage as resting on an unavailable source - `unresolvable`, not
`resolved`. An unavailable source is a real state and the record should say so.
