# UI Prototype

Build a clickable slice to answer the stated interaction or visual question. If the broader interface is still undefined, load the `design` skill through the available skill mechanism (or read its installed SKILL.md) and use its UI branch for the design conversation first. **Start with the end in mind and work backward**: first define what the user has accomplished and sees, then the actions, navigation, information, and backend capabilities needed to get there. The result should let someone judge both whether the experience works and whether it looks right.

Use the workflows the user has already settled as input. Do not reopen them merely because the UI has not been designed. If the request concerns only one visual choice on an established screen, keep the slice to that screen; if it concerns navigation across a workflow, include the connected screens.

## Work backward from the outcome

1. Use the provided goal, accepted design decisions, and visible success state. State the remaining design question this prototype must answer. Keep the slice narrow enough to review in one sitting.
2. Trace the path backward from success to entry. For each step, identify what the user needs to know, the decision or action they take, where they go next, and how they recover from a likely mistake or empty result. Sketch the screen map and the route back before drawing individual screens.
3. Map each screen to the information and actions it requires. For each action, record the implied read, write, permission, validation, or state transition. Compare these needs with the existing backend where there is one. Mark gaps as proposed contracts or open questions, not as working integrations. Use representative fixtures or in-memory state to make the journey runnable.
4. Apply the visual direction chosen with the user to the product, audience, existing brand, and density of real content. Decide typography, spacing, color, and component treatment together. Use existing design tokens and components when they fit. If one visual or structural choice remains unsettled, build alternatives for that disputed part while holding the rest constant; otherwise build one coherent direction.

The mapping can be a short note beside the prototype. It should be concrete enough that a reviewer can point to a screen and say what backend capability it assumes, without turning the prototype into an implementation spec.

## Build the slice

Put the prototype in the relevant app context whenever possible: the real shell, navigation, content density, and routing conventions reveal problems that an isolated mockup hides. Use a clearly named throwaway route or component when no existing screen can host it. Keep the project runnable with one familiar command.

Make the important transitions clickable from entry to success and back. Show realistic content and the states needed to judge the journey: normal, empty, loading or pending, validation or failure, and completed, as relevant to the question. Simulate writes in memory. A control should either do something meaningful in the prototype or be visibly outside the slice.

When comparing alternatives, hold the task and data constant. Vary navigation, layout, hierarchy, or primary affordance, not just color. Make alternatives easy to switch and share, for example with a `?variant=` parameter when the framework makes that simple. Keep comparison controls visually separate from the proposed product UI.

Return observations to the design conversation. Apply requested experiment revisions to the affected part of the prototype. Keep accepted workflow rules and layout choices fixed unless the human reopens them. State what changed between iterations so reviewers can compare the same decision.

## Inspect and hand over

Run the journey in a browser, including a narrow viewport. Inspect the rendered screens and revise anything that obscures the next action, breaks the path back, hides important state, or weakens the visual hierarchy. Check legibility, keyboard access, focus, contrast, and whether the look fits the product. The point is to judge the actual experience, so a code-only review is insufficient when a browser is available.

Hand over the entry URL or file, the goal to try, any variant keys, the settled choices used, the one open question, and a short list of findings: what navigation and visual choices worked, what felt awkward, and which backend capabilities the UI assumes. Separate observed behavior from proposed backend changes. Report any departure from the app-context or branch rules in [SKILL.md](SKILL.md). Capture the validated decision and prototype as that file describes once the human has judged the question.
