---
name: retro
description: "Conduct a retrospective on a coding session."
disable-model-invocation: true
---

The user has asked for a **retrospective**. You are suggesting improvements to the coding agent's **environment** to improve future runs.

## Steps

1. Call the Skill tool with `writing-for-agents` for the writing style guide.

2. Read primary sources for the specified session, or the current one by default: the conversation, relevant changes, instructions and failed or expensive checks. Separate required complexity, agent mistakes and workflow overhead. Link observed behavior to its cause; an unhappy outcome alone does not prove another rule was missing.

3. Look for candidates for improvement in these categories.

- **Navigation**: how easy was it for the agent to find the right files? Are there hidden dependencies between files? Would a **navigation pointer** make it easier? _Use when_ the session took a long time to find a piece of information.
- **Automated checks**: read the existing lint/typecheck/test commands and CI wiring first. Prefer wiring, fixing or running a relevant existing check earlier. Propose a new deterministic check for an important repeatable failure only when its prevention value justifies its maintenance and run cost. A one-off mistake can need a local fix rather than a permanent gate.
- **Coding standards**: classify the problem. Mechanical patterns belong in existing tooling when worth enforcing; design and complexity tradeoffs belong in review. Revise or remove a misleading rule before adding another. A complexity finding should identify concrete harm and a simpler adequate alternative.
- **Global AGENTS.md**: are there any steering instructions that should be moved to coding standards (or automated checks) instead? _Use when_ the AGENTS.md file is particularly large - in the repo OR the user's global scope.
- **Tool economy**: identify repeated reads, tests, approvals, handoffs or bookkeeping that delayed the outcome. Reuse valid evidence and existing tracker/test output; consolidate or remove redundant work before proposing custom tooling. Preserve required checks and ownership boundaries.
- **No-ops**: look for instructions in steering files that don't modify the agent's behavior. _Use when_ the steering files are large and unwieldy.
- **Information access**: look for opportunities to increase the agent's access to information. Teeing dev server logs, readonly access to third-party services. _Use when_ a crucial piece of information was not available to the agent.

4. Present the highest-value candidates in severity order. For each, give the observed failure, its cause and the smallest effective change, including what existing work it replaces. Prefer a few targeted edits to a new workflow. Apply changes when authorized; otherwise leave concrete proposals for selection. Keep remaining uncertainty and verification limits explicit.

## Reference

### Implementation vs Review

Give implementers the constraints needed to build correctly. Reviewers inspect the diff and relevant surrounding design for correctness, standards and unnecessary complexity. Use tooling for worthwhile mechanical checks; detailed review guidance need not become an implementation checklist.

### Files

You have access to several files in the repo:

- `CLAUDE.md`/`AGENTS.md`: these files are pushed to the context window of any agent working in this repo. They should be used incredibly sparingly, usually only for **navigation pointers** to other files.
- `CODING_STANDARDS.md`: keep judgement-based review guidance here; point to essential implementation constraints where needed. Disclose topic-specific detail through navigation pointers as the file grows.
- Docs: use docs as references files, pointed to by other files. Look for existing docs before writing new ones.
- Skills: use skills for docs (since their description goes into the agent's context window), or for user-invoked commands. Follow the advice in the `writing-for-agents` skill.
