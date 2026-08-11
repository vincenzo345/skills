# Node states and the signature

Reached at sign-off. The states a feature moves through, the four fields of a signature, why a
deferral is not one of them, and what happens when a signed feature re-opens.

Dates and names below are invented.

---

## Three states, and they sit on the feature, not the story

- `provisional` - drafted, not yet reviewed with the customer.
- `reviewed` - the session happened. Not yet signed.
- `signed` - the signature block is present, and **the file stops changing.**

Plus the **non-state** `deferred`. It is not a fourth state. It records that the customer
declined to agree, and it is never treated as one.

There is no `architected` and no `ticketed`. The tree stops at the handover file, and **a state
the tree cannot honestly maintain is worse than no state at all.**

**A story has no state.** It holds three things: its criteria, its `?`s, and its slice mark.

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
will not recall tomorrow what he deferred on.

---

## Re-opening

The old signature stays. The superseded snapshot stays. The new state is written below it and
dated. The record of what was agreed is not erased by what came after - the same principle that
keeps a losing statement on a closed conflict.
