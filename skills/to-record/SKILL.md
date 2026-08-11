---
name: to-record
description: Turn a raw meeting export into a normalised transcript whose every word is preserved and whose defects are flagged.
disable-model-invocation: true
---

# to-record

A raw meeting export is not a record you can build on. The one this skill was designed
against has no turn structure at all: a timestamp every eight seconds, speaker names in
parentheses, crosstalk merged into a single line, and one speaker's verb landing four lines
later inside the other speaker's reply. The export does not corrupt words. It corrupts
**attribution**.

This skill restructures that export into a normalised transcript and flags what is wrong
with the record. It runs in four ordered steps: **ask provenance, normalise, verify,
resolve flags.**

## The preservation contract

**Every word between speaker markers is carried across unchanged.** Fillers, hedges,
mis-transcriptions, profanity, a *"yeah and no"* that answers nothing: all of them survive
verbatim. You may move words between lines and between turns. You may not add one, drop one
or change one.

Normalisation is **restructuring, never rewriting**. Tidying grammar, dropping filler, or
resolving a vague answer into a clean one is a synthesis step wearing a parse's clothing,
and it is the failure this skill exists to prevent. A model that tidies here produces a
record that reads better and says something the room did not say.

**Emit no question about the domain.** Not one. This skill reports that a sentence stopped;
it never asks what the answer would have been. A hole in the workflow is only findable by
attempting to restate the workflow, and that move belongs to `/to-scope`, one step later.
If you find yourself wanting to ask what a step means, you have left this skill's job.

**Flag and continue. Never refuse.** A refusal rule would reject every real transcript.

## Step 1 - provenance

Ask exactly one question, and ask it first:

> Were you in the room?

The answer routes the whole run and nothing else is configurable.

- **In the room.** The transcript is a memory aid. Every flag is answerable from your
  memory, for free, without spending a second of the client's patience. **Step 4 runs.**
- **Absent.** The transcript is evidence about people who are not here. Nobody present can
  answer. **Step 4 does not run.** Flags ride forward into `/to-scope` as known defects of
  the input, and the only legal move later is to raise them when the stakeholder is next
  available.

Do not guess the answer from the file. Ask.

## Step 2 - normalise

Read the export whole. A realistic meeting is about 19K tokens per hour, so a two-hour
workshop is about 40K: no chunking, no summarising, no splitting. If a file ever genuinely
exceeds the window, say so rather than silently summarising.

Do not write a parser. Formats are endless - VTT, Otter JSON, Fathom, Granola, a caption
dump, raw notes - and the one you meet next week has no parser. Read the format, work out
its marker convention, and restructure by hand under the contract above.

What restructuring means, concretely:

1. **One speaker per turn.** Split the text at speaker markers.
2. **Stitch fragments.** Consecutive fragments from the same speaker, cut apart only by a
   timestamp, are one turn. This is what rejoins the verb with its own question.
3. **Lift the backchannel lane out.** Many exports run short interjections inline while the
   primary speaker's sentence continues around them - in the designed-against format, after
   a ` - ` separator. Those become their own interjection turns, and the sentence they
   interrupted is stitched back together.
4. **Assign positional ids where labels are missing** - `Speaker A`, `Speaker B`. Never
   infer identity from content. Inferred attribution is fabricated attribution.

**Flag as you go.** Six types, a closed set: `suspect-term`, `merged-crosstalk`,
`unlabelled-speaker`, `thread-abandoned`, `hard-stop`, `prior-context`. Read
`references/flags.md` for what each one catches and how each resolves. There is no seventh; a
defect that fits none of the six is described in plain words under the flag list and named as
unclassified.

Write the output to `.scratch/`, beside its source, gitignored, never committed. It
inherits the confidentiality of the material it restructures.

### The output format

The verifier depends on this shape, so match it exactly.

```markdown
---
source: <path to the raw export>
provenance: in-the-room | absent
labels: unverified
---

# Flags

- `suspect-term` 2:56 - "Windflex" is probably WinFlex. unresolved
- `merged-crosstalk` 3:20 - who says "achieve"? unresolved

---

[0:00] **Ada Wong:** Right, so a request comes in, and we open a case against whoever
sent it. Does that ever vary?
> **Ben Choi:** Mhm.
> **Ben Choi:** Yeah, sometimes.
```

- Front matter, then the flag list, then a `---` line, then the body.
- **The body contains no `---` line.** The verifier finds the body by taking everything
  after the last `---`, so one inside the body would silently cut the file in half.
- `labels: unverified` stays until you confirm the labels in step 4. A speaker label
  **locates a line and carries no authority** - see the flag reference.
- Timestamps are optional in the body and carry no meaning beyond locating a turn back in
  the raw export.

## Step 3 - verify

The model cannot check its own preservation; it is the checker and the checked. A script
does it:

```bash
python <skill-dir>/scripts/verify_preservation.py <raw> <normalised>
```

On macOS and Linux use `python3`. Run it every time, before step 4.

It compares the body word count and the sorted body word multiset of the two files and
exits non-zero on divergence, printing what went missing and what appeared from nowhere.
Reordering is legal, because restructuring moves words. Run
`python <skill-dir>/scripts/verify_preservation.py --rules` to see the body-extraction rule
it applies; the rule is stated in full at the top of the script.

**A failure rejects the normalisation.** Redo it. Do not warn and continue, do not patch
the two or three words the script named and call it done, and never edit the raw export to
make the check pass. Show the user which words diverged.

**On a second consecutive failure, stop and hand both word lists to the user.** A
body-extraction rule may not fit this export's format, and that is a rule to fix rather than a
normalisation to retry.

## Step 4 - resolve the flags

Only if the answer to step 1 was *in the room*. Otherwise skip to termination with every
flag carried forward unresolved.

This pass is short, addressed to **the developer only**, and asks nothing about the domain.
Fact questions, of the record:

> "Windflex at 2:56 - WinFlex?"
> "Two speakers merged at 3:20 - who said 'achieve'?"

Where a speaker mapping is obvious, **propose** it for correction. Never apply it silently.
The client is never asked about transcription noise: their patience is the scarcest thing
in this whole pack and spending it on the recording tool's mistakes is its cheapest failure.

Record each answer against its flag, and mark each flag `resolved`, `unresolved` or
`unresolvable`. Corrections to a suspect term go **in the flag list, not in the body** -
the body still says *Windflex*, because the body is the record. `/to-scope` and
`/domain-modeling` read the correction from the flag.

Set `labels: confirmed` only once the developer has confirmed them.

## Termination

Done means both of these, and nothing softer:

1. The verifier exits 0.
2. Every flag is `resolved`, `unresolved` (absent from the room) or `unresolvable`.

Report the flag counts and hand the path to the normalised file to the user. `/to-scope`
reads that file and never the raw export.
