## What it does

`diagnosing-bugs` investigates a reported defect with a **tight** feedback loop. Each experiment distinguishes a plausible cause or collects missing evidence. Code inspection can guide reproduction; a hypothesis becomes a diagnosed cause only when evidence supports it.

It reuses existing reproductions and results. An unchanged run that adds no information is a reason to change the investigation, not repeat it indefinitely.

## When to reach for it

Type `/diagnosing-bugs`, or the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) reaches for it when a task fits: a difficult bug, intermittent failure or performance regression.

| Situation | Approach |
| --- | --- |
| Understood defect | Focused failing regression and minimal fix |
| Intermittent failure | Compare retained contexts and probe a specific uncertainty |
| Performance regression | Measure the relevant baseline before changing code |
| Planned new behavior | [tdd](tdd.md) |
| General architecture assessment | [code-review](code-review.md) for a concrete diff, or [design](design.md) for structural choices |

## A loop worth running

The useful boundary is the cheapest one that preserves the failure mechanism. A real database or application-flow reproduction may take minutes and still be the right test. A fast substitute that removes the relevant interaction gives false confidence.

Narrow a reproduction until it is practical to diagnose and retain as regression coverage. Stress, fuzzing and repeated trials are conditional tools with an information goal and stopping condition, not required milestones.

When evidence supports a fix, the agent establishes a failing regression, applies the smallest correction and verifies the original scenario. Required repository checks still apply. Test output and failed evidence retain their relevant code and environment basis; disposable probes follow repository cleanup rules.

## Common questions

**Does it have to reproduce the failure before it can inspect code or suggest causes?**

No. Inspection and tentative explanations help choose a useful reproduction. The agent distinguishes those explanations from proven causes and does not claim a fix from conjecture.

**What happens when the failure will not reproduce?**

It reports what remains unknown and the next decisive observation. Targeted investigation and independent authorized work can continue. Missing access may need your input; unchanged reruns without an information goal stop.

**Do later passing tests explain an earlier failure?**

No. Even a passing test of an injected fault establishes only coverage of that mechanism. The original failure needs its own causal evidence.

**Will it rerun work already done during triage?**

Only when the evidence is insufficient or invalidated. Existing reports, reproductions and applicable results are inputs to diagnosis.

**How are sensitive logs handled?**

Commands and artifacts are redacted, credentials remain in environment variables, and only relevant diagnostic output is shared. Useful failed evidence is retained without exposing secrets or personal data.

## It's working if

- It explains what the next experiment will distinguish.
- The reproduction preserves the failure you reported.
- It stops repeating unchanged trials that add no information.
- A fix has a failing regression followed by relevant passing verification.
- Its report separates diagnosed causes from unresolved historical failures.
- Temporary instrumentation is removed and useful evidence remains available.

## Where it fits

This is a standalone investigation skill. [Triaging](triage.md) can supply the initial evidence; [tdd](tdd.md) supplies behavioral test guidance. After a fix, you can invoke [retro](retro.md) to improve the environment using the observed failure. [guide-me](guide-me.md) routes you to the appropriate workflow.
