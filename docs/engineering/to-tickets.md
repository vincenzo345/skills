## What it does

`to-tickets` takes a plan, a [spec](https://www.aihero.dev/ai-coding-dictionary/spec), or the conversation you are in, and breaks it into a set of **[tickets](https://www.aihero.dev/ai-coding-dictionary/ticket)** on your issue tracker. Each ticket declares its **blocking edges**: the other tickets that have to finish before it can start.

It maps the whole outcome and requirement coverage, but fully refines only the next eligible work. A ready ticket is a **tracer bullet**: a narrow complete path through the layers needed for an independently verifiable outcome. Later outcomes stay explicitly provisional. The [shared sizing reference](../../skills/engineering/setup-repo/TICKET-SIZING.md) covers the estimate, readiness evidence and refinement rules.

Local issues belong to the identified effort and reference the current spec revision. Approval is recorded with each published issue; dependencies and observable acceptance criteria let a fresh implementation session validate and claim the work.

Refinement uses applicable precedent evidence in the existing sizing note. Sufficient local implementation and verification end discovery; a gap or needed alternative can trigger a source configured through [setup-repo](setup-repo.md). Evidence must support the required behavior, including relevant failure conditions. A familiar example does not make an uncertain outcome ready.

The approach is simplified before it is sized. Several small tickets can still build an unnecessarily complex system. New maintained mechanisms need a concrete requirement that the simpler existing path cannot meet; material choices stay visible in the existing design or sizing note. Prefactoring earns its place by reducing total delivery work.

On GitHub or GitLab, approved issues retain explicit specification revisions and native blocking links. Readiness does not bypass a stale basis, unfinished blockers, or the remote ownership capability boundary.

## When to reach for it

You invoke this by typing `/to-tickets`. The [agent](https://www.aihero.dev/ai-coding-dictionary/agent) won't reach for it on its own.

| Where you are | What to run |
| --- | --- |
| You have a spec issue and the build spans several sessions | `/to-tickets`, or `/to-tickets #<spec_issue>` |
| The plan is only in the conversation, never written up | `/to-tickets` reads the thread directly, no spec needed |
| The whole change meets the shared sizing/readiness gate | [implement](implement.md), skip the tickets |
| Integration evidence changes future work | Revise the existing breakdown, preserving accepted evidence and requirement coverage |
| Nothing is decided yet | [grill-with-docs](https://aihero.dev/skills-grill-with-docs), then [to-spec](https://aihero.dev/skills-to-spec) |
| A [wayfinder](https://aihero.dev/skills-wayfinder) map has cleared | [to-spec](https://aihero.dev/skills-to-spec) first, to collapse the map, then `/to-tickets` |

Only approved, refined work is agent-ready. Provisional outcomes return here for refinement; [triage](triage.md) is for incoming work from someone else.

## Prerequisites

`to-tickets` publishes into a tracker, so [setup-repo](setup-repo.md) must have configured one for this repo, along with the triage-label vocabulary. Either kind works: a real tracker like GitHub or Linear, or local markdown files under `work/`, which work with no extra setup.

## Tracer bullets, not layers

A **horizontal** slice ships one layer of the change. Nothing works until every layer has landed, and each ticket's acceptance criteria have to reach into work that another ticket owns. A **vertical** slice (the tracer bullet) ships one thin path through all the layers at once, so it is verifiable alone and owns everything it grades.

This is the rule people break most often. One team ran a 26-ticket stack sliced by layer (corpus, producer, aggregator, selector) and got roughly twenty agent runs per closed ticket, about three quarters of them rework. Their own post-mortem traced every failure class back to the horizontal slicing rather than to the implementations.

The initial breakdown comes back for approval with ready slices distinguished from provisional coverage. During authorized implementation, routine refinement records existing authority rather than repeating the approval ceremony. Changes to accepted behavior, guarantees or architecture need a concrete proposal for your decision.

## Blocking edges

The edges are the point of the artifact. They work in two ways, depending on the tracker:

| Tracker | Where the edges live | How you work them |
| --- | --- | --- |
| Local markdown | Authoritative blocking references in each issue under `work/<effort>/tickets/` | Claim refined ready work whose blockers are integrated through the shared consumer |
| A real tracker (GitHub, Linear) | Native blocking links where available; parent links group the work | Select the ready **frontier** through the configured ownership path |

The edges live in the ticket either way. The tracker only decides whether anything can act on them in parallel. `to-tickets` produces the artifact; running it (one session at a time, or a fleet) is your job, not the skill's.

## The wide-refactor exception

One shape breaks the tracer-bullet rule. A **wide refactor** is a single mechanical change (rename a column, retype a shared symbol) whose **blast radius** covers the whole codebase. One edit breaks thousands of call sites, so no vertical slice can land green.

`to-tickets` sequences that as **expand–contract** instead:

- **Expand**: add the new form beside the old, so nothing breaks.
- **Migrate**: move call sites over in batches sized by blast radius (per package, per directory), one ticket per batch, each blocked by the expand. CI stays green because the old form still exists.
- **Contract**: delete the old form once no caller remains, in a ticket blocked by every migrate batch.

Each batch must meet the same sizing gate and demonstrate compatibility independently. If that is not possible, refine the compatibility boundary before dispatch; a final integration ticket cannot absorb all earlier verification obligations.

## Common questions

**It produced twelve tickets for a three-line change.**
Over-decomposition loses the independently useful outcome. Ask for the smallest coherent outcome that includes its verification and integration, not one ticket per file or layer. If the whole change meets the shared sizing/readiness gate, go straight to [implement](implement.md).

**The tickets came out one per layer: all the schema in one, all the API in another.**
This is the failure the vertical-slice rule is written against, and the skill still produces it sometimes. Catch it at the quiz step by asking one question per ticket: what can I demo when this is done? A ticket with no answer is a horizontal slice. Some people add a "demo path" line to each ticket for this reason, and report that it pushes the model toward vertical slices.

**On GitHub the tickets weren't created as sub-issues of the spec issue.**
This was reported across a dozen runs and several models, [most fully in issue #554](https://github.com/mattpocock/skills/issues/554). Fixed: `to-tickets` now makes each ticket a sub-issue of its source issue, and the GitHub tracker template gives the command (`gh issue create --parent <n>`, `gh` 2.94+). Re-run [setup-repo](setup-repo.md) to refresh an older `docs/agents/issue-tracker.md`.

**"Blocked by" was written into the issue body instead of a real blocking link.**
This is the same kind of problem, [reported in issue #513](https://github.com/mattpocock/skills/issues/513), where the agent even stated that GitHub has no native blocking relationship at all. It does: `gh issue create --blocked-by 12,15`. Because the skill publishes blockers first, their numbers are always available at creation time. The body text is meant to be the fallback for trackers with no native edge, not the default. The ticket template now omits `## Blocked by` when the edges are native.

**Where do the local tickets go? The v1.1 notes said a root-level `tickets.md`.**
They did, and that was a bug. A single shared file also caused race conditions when parallel agents wrote to it. Local mode now writes one file per ticket under `work/<effort>/tickets/<NN>-<slug>.md`, in dependency order, matching the layout the local tracker template already described. A bare number resolves only with known effort and record-kind context; otherwise use the full issue reference.

**It kept truncating when it tried to read my spec.**
A very large spec can outgrow what a tracker issue serves back cleanly. There is no local copy to fall back on, so the agent spends [tool calls](https://www.aihero.dev/ai-coding-dictionary/tool-call) fetching chunks again and never reaches the end. Don't [clear](https://www.aihero.dev/ai-coding-dictionary/clearing) or [compact](https://www.aihero.dev/ai-coding-dictionary/compaction) between `/to-spec` and `/to-tickets`. Run them in the same context window and the agent never has to fetch the spec back.

**The acceptance criteria graded nothing: some passed before any work was done.**
The template asks for criteria and says nothing about whether they can fail, so this happens. Three shapes recur: a criterion already true at the base commit, a criterion that only work in another ticket can satisfy, and one that restates the request rather than deriving from the artifact. Vertical slicing prevents most of it, because a slice that delivers new behaviour fails at the base commit by construction. The check is still worth doing by hand. For each criterion, name the observation that would show it false, and confirm it fails at the commit the implementer starts from.

**The tickets are published. How do I actually run them?**
The skill stops at the artifact. Use [implement](implement.md) for one refined slice or [implement-spec](implement-spec.md) to manage the ready frontier through available worker tools. Readiness, ownership and integration evidence still gate work. Provisional future coverage is not dispatchable just because its blockers have finished.

## It's working if

- Every ticket has an answer to "what can I demo when this is done?", and the answer is behaviour, not a layer.
- The list comes back to you numbered, with a "Blocked by" line on each, before anything is published.
- The next ready slice has sizing evidence, and provisional outcomes name what still needs refinement.
- Each issue links its spec/design basis while avoiding brittle implementation paths and line numbers.
- Every requirement maps to accepted evidence, a refined slice or an explicitly provisional outcome.
- Necessary prefactoring enables a concrete outcome; a separate ticket has its own useful compatibility result.

## Where it fits

`to-tickets` is a step in the main build chain:

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

Upstream is [to-spec](https://aihero.dev/skills-to-spec), which hands it a settled spec to slice against. Keep both in one context window, with no clear between them. Downstream is [implement](https://aihero.dev/skills-implement), which builds one ticket per fresh session, driving [tdd](https://aihero.dev/skills-tdd) for the tests and closing with [code-review](https://aihero.dev/skills-code-review). [implement-spec](https://aihero.dev/skills-implement-spec) is the other way down. It reads the same blocking edges as a task graph and builds every ready ticket in parallel on one integration branch. When you're unsure which skill or flow fits, [guide-me](guide-me.md) routes you.
