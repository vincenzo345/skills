---
name: prototype
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered — from the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a tiny interactive terminal app that pushes the state machine through cases that are hard to reason about on paper.
- **"What should this look like?"** → [UI.md](UI.md). Generate several radically different variations in a production-excluded preview surface with a local comparison control.

The two branches produce very different artifacts — getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## Rules that apply to both

1. **Throwaway and production-excluded from day one.** Use the repository's approved prototype/scratch convention. If none exists, choose a clearly named isolated location that production builds, routes, packages, and deploys do not consume. Do not edit an existing production route or module merely to host a prototype.
2. **One command to run.** Prefer a direct command or existing prototype hook. Do not modify a shared production task runner, manifest, route registry, or deployment configuration unless the repository already has an explicitly production-excluded prototype convention or the user authorizes that integration.
3. **Synthetic, disposable state by default.** State lives in memory and example data is synthetic. If the question explicitly concerns persistence or real data, use a scratch database/file and the minimum authorized data, with an obvious "PROTOTYPE — wipe me" marker. Never infer permission to use production data, credentials, or mutations.
4. **Skip the polish.** No tests, no error handling beyond what makes the prototype _runnable_, no abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), print or render the full relevant state so the user can see what changed.
6. **Capture the answer, not accidental production code.** A prototype is evidence for a decision, not implementation proof. Record the question, verdict, limitations, and context pointer using the repository's conventions. Create a branch or commit only when the request or repository workflow authorizes it. Production adoption returns through the repository's normal specification, implementation, and verification flow; rewrite or deliberately adopt the idea there under production standards.

Repository security and data-handling policy governs what data, credentials, services, and environments a prototype may use. If those rules or the production-exclusion boundary are unknown, use synthetic disposable local data in an isolated path and report the limitation.
