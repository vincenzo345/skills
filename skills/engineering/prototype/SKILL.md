---
name: prototype
description: Build a throwaway runnable experiment to answer a bounded design question about logic, state, interaction, or visual choices. Use design when the broader direction needs collaborative exploration first.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered, using the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a single shareable HTML file (free-play buttons plus tabbed guided walkthroughs) that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"How does this interaction or visual choice work in practice?"** ? [UI.md](UI.md). Build a clickable experiment using accepted workflow and interface decisions. For broader UI exploration, load `design` through the available skill mechanism, or read its installed SKILL.md when no invocation tool exists, and use its UI branch first.

The two branches produce very different artifacts, so getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious, but name it so a casual reader can see it's a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
2. **Trivial to run.** A UI prototype starts from one command in the project's task runner: `pnpm <name>`, `python <path>`, `bun <path>`, etc. A logic demo is a single HTML file the user double-clicks. Either way, no thinking required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE, wipe me" name.
4. **Polish what is under examination.** A UI prototype needs enough visual craft and interaction detail to judge the experience. Skip production hardening, abstractions, and tests unless they answer the question.
5. **Make change visible.** After each meaningful action, show the resulting user-visible state. A logic demo also exposes its full relevant model state.
6. **Capture it when done.** Record the validated decision and the question it settled in the implementation issue or another durable project record. Capture the prototype as a **primary source** on a throwaway branch out of main, with a pointer from that record. Fold the decision into production code when implementation is in scope; keep the throwaway code off main.
