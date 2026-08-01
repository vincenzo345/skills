# The harness pattern — why each piece exists

This is the reasoning behind the scaffold, so that when you adapt it you know what's load-bearing and
what's incidental. It's the long-running-agents pattern: a build loop that stays coherent and honest
over hours, where a single model context would drift, over-approve its own work, or run out of room.

## The three failures it defends against

**Context limits.** A single context window is finite and degrades ("context rot"); near the end a
model rushes ("context anxiety"). The harness keeps each role in its own fresh context and puts durable
state on disk (`.harness/`), so no run depends on one window holding everything.

**Weak planning.** Models over-specify or one-shot. The Planner deliberately stays high-level — sprints,
not schemas — because an early over-specified mistake cascades and magnifies across every later sprint.

**Bad self-judgment.** This is the big one. A model grading its own output is generous: it calls a
half-built feature done. So the Evaluator is a *separate* agent with its own context and a harsh brief.
The insight that makes this work: tuning a standalone critic to be demanding is tractable; tuning a
builder to be self-critical is not. You exploit the gap between an LLM's ability to critique and to
generate — the same reason it's easier to judge a meal than to cook one.

## The roles

- **Planner** — one-shot, high-level direction and sprint order. Not in the loop; its only job is to set
  the outer lines so downstream errors don't cascade.
- **Generator** — the builder. Implements one sprint, writes tests, commits when green. Never grades
  itself or declares "passed."
- **Evaluator** — the adversary. Independently builds, tests, and *exercises* the artifact (drives the
  browser, runs the CLI, hits the API — not just reading diffs), then grades against the contract and
  rubric. Defaults to failing.

## The mechanisms

**The contract.** Before building, Generator and Evaluator negotiate concrete, testable criteria for the
sprint (files on disk, back and forth until agreed). This converts vague intent into checks a lazy
implementation can't pass, *without* forcing the Planner to over-specify up front. It's the piece a
plain "build then check" loop lacks.

**Tests vs. exercise.** Anything with a mechanism becomes a test (fast, deterministic). Anything that is
taste becomes evidence the Evaluator captures (a screenshot, an output sample) and grades against the
rubric. That division is what lets fuzzy goals ("feels responsive," "reads as locked") run under an
automated loop at all.

**The rubric + calibration references.** Subjective quality is gradable if you write down a strong
opinion. The rubric weights the axes of "good"; the reference examples in `.harness/references/` anchor
the Evaluator's taste to yours — the single highest-leverage quality lever, because it turns "make it
good" into "make it like this."

**File-system state.** Plan, progress, contract, verdict, and a `journal.jsonl` breadcrumb log live on
disk (JSON preferred — models overwrite Markdown too eagerly). This is the shared memory that lets fresh
contexts pick up mid-build and lets you stop and resume anytime.

**Verdicts, including restart.** `pass` / `revise` / `restart`. The `restart` path (reset to the sprint
tag, rebuild from scratch) matters: a separate Evaluator will happily throw away ten patched attempts
for a clean rebuild — a move a self-grading builder, attached to its own work, essentially never makes.

## Adapting it over time

The harness fills the model's current gaps; as models get stronger you strip scaffolding out — raise the
loop caps, drop sprint decomposition, eventually merge roles. The lesson from the pattern's own evolution:
a harness that was right for one model generation becomes overhead for the next, so periodically try the
simpler version. And you tune a run by editing the rubric and role prompts and re-reading the traces,
not by inserting yourself into the loop — that reading-and-tuning *is* the engineering work here.
