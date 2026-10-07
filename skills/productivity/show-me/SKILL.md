---
name: show-me
description: Show the current topic as the smallest useful visual.
disable-model-invocation: true
metadata:
  credits:
    skill: show-me
    author: Dex Horthy
    organisation: HumanLayer
    url: "https://github.com/humanlayer/skills/blob/ca7c8088db69e315a8b2deea43820270457f8f3c/plugins/show-me/skills/show-me/SKILL.md"
---

# Show me

Answer the user's current question with a visual that exposes the important relationships, order, ownership, or change. Use the smallest form that makes the point clear:

- Pseudocode for logic; a call tree for runtime flow; a component or file tree for structure.
- Mermaid for interactions, states, data flow, or phase handoffs.
- A short timeline or decision map for the session: what was established, what changed, what remains open, and the next handoff.
- A short diff sketch for before/after; a focused HTML artifact when layout or interaction cannot be explained well in text.

Use names from the actual conversation or repository. Label assumptions and unknowns in the visual. Keep only the detail needed to answer this question, with a brief explanation beside it. If you create an HTML artifact, link the file so the user can open it; open it in a browser when a browser tool is available and the visual needs inspection.

This skill adapts the visual-selection approach of [HumanLayer's `show-me`](https://github.com/humanlayer/skills/blob/ca7c8088db69e315a8b2deea43820270457f8f3c/plugins/show-me/skills/show-me/SKILL.md). It is a conversation aid, not a mandatory gate in the build workflow.
