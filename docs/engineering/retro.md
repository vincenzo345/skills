## What it does

`retro` looks back over a coding [session](https://www.aihero.dev/ai-coding-dictionary/session) and suggests improvements to the agent's **[environment](https://www.aihero.dev/ai-coding-dictionary/environment)**, so the next run goes better. It reads the session's own record (the current one by default, or one you point it at in the session logs). It finds the moments where the agent struggled, and gives you a list of candidate fixes, most severe first.

It examines the environment rather than fixing the application. The bug the agent shipped, a file that took twenty [tool calls](https://www.aihero.dev/ai-coding-dictionary/tool-call) to find, or repeated bookkeeping can each reveal a different cause. It separates required complexity, agent mistakes and workflow overhead, then proposes the smallest effective change. Normally you select a candidate first; an explicit request to refine the skills authorizes targeted edits.

## When to reach for it

You invoke this by typing `/retro`, and the agent won't reach for it on its own.

Reach for it at the end of a session that was harder than it should have been. For example, the agent searched too long for something, made a mistake a tool could have caught, or needed information it could not get. A smooth session has little to teach, and the findings come from the difficult ones. If you want a verdict on the code the session produced, use [code-review](https://aihero.dev/skills-code-review) instead.

## Where the findings land

Each candidate belongs to one category, and the category decides where the fix goes:

| What went wrong in the session | Fix it with |
| --- | --- |
| The agent took a long time to find a file or fact | A **navigation pointer** from a file it already reads |
| An important repeatable mistake is mechanical | Reuse or repair an existing **[automated check](https://www.aihero.dev/ai-coding-dictionary/automated-check)** first; add one when its prevention value justifies the cost |
| The reviewer missed a judgement-call mistake | A rule in `CODING_STANDARDS.md` for the reviewer agent |
| `AGENTS.md` or `CLAUDE.md` is large | Move its steering out, into standards or checks |
| A tool call was expensive for what it returned | Streamline the tool, or replace it |
| A steering file is full of lines that change nothing | Delete the **no-ops** |
| The agent needed information it couldn't reach | Widen its access: tee the dev server log to a file, give read-only access to a service |

Implementation needs the constraints that make the change correct. Review checks the diff and surrounding design, including unnecessary complexity. Detailed judgement guidance belongs where it is used; [AGENTS.md](https://www.aihero.dev/ai-coding-dictionary/agents-md) should mainly carry pointers rather than a checklist loaded into every [context window](https://www.aihero.dev/ai-coding-dictionary/context-window).

Before proposing a rule, `retro` checks what already exists and what the extra work would cost. Worthwhile mechanical checks belong in tooling; design tradeoffs need judgement. A missing guardrail can be a finding, while a one-off mistake may need only a local fix. Removing a misleading instruction can be more useful than another gate.

## Common questions

**Does it write the lint rule itself, or wait for a yes? Can I wire it to run after every session?**

It proposes unless you authorize changes. One user reported being "burned by auto-hooks that blocked good changes"; a retrospective is no reason to install a gate automatically. Keep permanent enforcement [human-in-the-loop](https://www.aihero.dev/ai-coding-dictionary/human-in-the-loop), and try a proposed check against the repo before it blocks merges. A smooth session may need no change.

**Won't this pile up lint rules forever? Does it ever suggest removing one?**

The first options are removing, clarifying or reusing existing instructions and checks. Each addition needs an observed failure and enough prevention value to justify its run and maintenance cost. The session provides evidence for pruning; a full audit of unrelated hooks and jobs is outside its scope.

**Won't it just invent generic advice to fill its categories?**

This is the strongest criticism of it. One user found that "once the job is finished, the AI tends to forget the struggles from the middle of the session and invents generic advice to satisfy the retro categories." Every candidate must come from the session's own record, so the advice is specific to that session. This has a cost as well as a benefit. It rarely invents something irrelevant, but it can give too much weight to whatever this one session was about. Discard any candidate you can't trace to a specific moment. Treat the severity order as a first draft too, because a quiet, expensive mistake can rank below a loud, cheap one.

**My session is long. Run it now, or start fresh?**

By default it reviews the current session. That is the best case, because the struggles are still in the context window. If the session has already moved out of the [smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone), [clear](https://www.aihero.dev/ai-coding-dictionary/clearing) it, and point a fresh `/retro` at the previous session in the session logs.

**The agent keeps making the same mistake. Should I add a line to `CLAUDE.md`?**

Usually start with the instruction or check already responsible. Worthwhile mechanical failures can use existing tooling; judgement calls can improve review guidance. A navigation pointer keeps `AGENTS.md` small. `retro` is not a [memory system](https://www.aihero.dev/ai-coding-dictionary/memory-system), and another instruction cannot guarantee that the mistake never recurs.

**My setup mentions `CODING_STANDARDS.md` and I don't have one. Where does it come from?**

No skill ships the file. The first time a session finds a judgement-call rule for the reviewer, `retro` proposes to create it. After you accept, [code-review](https://aihero.dev/skills-code-review) reads it. Any other standards doc you already keep, such as `CONTRIBUTING.md`, works the same way.

**How is it different from `improve-codebase-architecture`?**

The input is different. [improve-codebase-architecture](https://aihero.dev/skills-improve-codebase-architecture) needs only the code, and looks for structural improvements to it. `retro` needs a session history, and improves the environment the agent works in, not the code. You use both; neither replaces the other.

## It's working if

- Every candidate points back to a specific moment in the session, not a generic best practice.
- Repeat mistakes turn into failing checks, and your `AGENTS.md` gets shorter over time, not longer.
- If a check already existed but was not connected, the finding is to connect it, not a proposal to build a new one.
- The next session on the same kind of task finds what it needs faster.

## Where it fits

`retro` is the last step of the main chain, where you review how the chain went:

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

Run it after a build worth learning from, in the same session or pointed at that session's log. You can skip it after a smooth build.

- [code-review](https://aihero.dev/skills-code-review) is the reviewer agent that `retro` most often tunes. New coding standards go where its Standards axis reads them.
- [writing-for-agents](https://aihero.dev/skills-writing-for-agents) sets the writing style for every steering file and skill that `retro` proposes, and `retro` loads it before it starts.

[guide-me](guide-me.md) routes across the whole set when you are unsure which skill the situation needs.
