# Node states, the review block and the signature

Reached in the session, and again at sign-off. The states a feature moves through, the block
that records the session, the four fields of a signature, why a deferral is not one of them,
and what happens when a signed feature re-opens.

Dates and names below are invented.

---

## Three states, and they sit on the feature, not the story

- `provisional` - drafted, not yet reviewed with the expert.
- `reviewed` - the session happened, **and the review block says who held it and when.** Not
  yet signed.
- `signed` - the signature block is present, and **the file stops changing.**

Plus the **non-state** `deferred`. It is not a fourth state. It records that the expert
declined to agree, and it is never treated as one.

There is no `architected` and no `ticketed`. The tree stops at the handover file, and **a state
the tree cannot honestly maintain is worse than no state at all.**

**A story has no state.** It holds three things: its criteria, its `?`s, and its slice mark.

---

## The review block - what makes a session countable

Three fields: the date, who held the expert seat, and how the session was held. It goes on the
feature under the state line.

```
Reviewed 2026-08-14. Connor Craig, expert seat. Screen-shared call.
```

**It is written when a feature has had both moves of the session, and nothing else writes it.**

`reviewed` on its own asserts that a session happened and says nothing about who was in it or
when. The draft and the session usually fall on different days, often weeks apart, and a session
held later has no ambient context to fall back on - the marks are the only defence.

**No review block, no `confirmed`.** A criterion marked `confirmed` on a feature carrying no
review block is a review that cannot be shown to have happened, and the next run of
`/to-session` finds it at step 0. This is the failure that has actually been observed: a builder
improving his own draft an hour before the call, three criteria written `confirmed`, the feature
marked `reviewed`, and nothing on the page able to tell the difference.

The seat is named because the holder can change between one session and the next. A second-hand
account is a builder seat however senior, and this is where that stays visible months later.

**Blocks accumulate.** A second session on the same feature - a re-paraphrase owed from last
time, or a re-opened `?` - writes a second block below the first. Nothing is overwritten, for
the reason the re-opening rule gives at the end of this file.

---

## The signature block

Four fields: date, name, how they agreed, and the words if any were said.

```
Signed 2026-08-04. Tony Stark. On the call.
"Yeah, that's how it works."
```

```
Deferred 2026-08-04. Tony Stark. On the call.
"Go with your recommendation."
This is not an agreement. Ask again in the next session.
```

**Words are optional for a signature and necessary for a deferral.** Without them the two are
the same four fields, and a deferral that looks like a signature is the binding constraint
failing in the record itself. A deferral is a non-event that reads as assent, and the subject
will not recall tomorrow what they deferred on.

---

## Re-opening

The old signature stays. The superseded snapshot stays. The new state is written below it and
dated. The record of what was agreed is not erased by what came after - the same principle that
keeps a losing statement on a closed conflict.
