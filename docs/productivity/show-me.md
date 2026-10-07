## What it does

`show-me` turns the current discussion into the smallest visual that exposes its important relationships. It can use a diagram, call or file tree, diff sketch, short session timeline, or focused HTML artifact. It shows what is known and labels assumptions; the picture does not become new evidence.

## When to reach for it

You invoke this by typing `/show-me`, and the agent won't reach for it on its own. Use it when a decision or handoff would be easier to inspect than to describe. For the body of a pull request, use [pr](https://aihero.dev/skills-pr), which includes a visual of the change plus review evidence.

## The smallest view

The useful visual is the one that answers the question in front of you. A call tree can reveal ownership of a runtime path; a Mermaid diagram can show a workflow; a timeline can show what this [session](https://www.aihero.dev/ai-coding-dictionary/session) established and what remains open. A focused HTML artifact earns its cost only when layout or interaction is the point.

## Common questions

**Can it show where we are in the session?**

Yes. Ask for a decision map or timeline showing what was established, what changed, what remains open, and the next handoff. It should point back to the underlying issue or document when that detail matters.

## It's working if

- You can see the relationship or decision you asked about without reconstructing it from a long explanation.
- Assumptions and unknowns remain visible rather than becoming settled facts in the diagram.

## Where it fits

`show-me` is a **reach-for-it-anytime standalone** across discovery, design, implementation and release. It explains the current state; it does not advance a workflow stage or replace [grill-with-docs](https://aihero.dev/skills-grill-with-docs), a spec, or review. [guide-me](../engineering/guide-me.md) maps the rest of the skills and their handoffs.
