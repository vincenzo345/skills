---
name: openai-docs
description: Research current OpenAI product, API, model, and Codex behavior from official documentation. Use for OpenAI setup, capabilities, pricing, model choice or migration, prompting, SDKs, APIs, agents, evals, and product comparisons; skip generic software work that merely mentions OpenAI.
---

# OpenAI Docs

Answer current OpenAI questions from fetched first-party documentation, using whatever search and page-retrieval capabilities the active harness provides.

## Source-first workflow

1. Search the user's exact topic and any explicitly named model or product before inspecting local files, planning changes, or answering from memory.
2. Open the most relevant official page; a search snippet is not evidence. If it does not settle the question, open the next relevant official source.
3. Prefer the source that owns the claim:
   - `developers.openai.com` for Codex and developer guides;
   - `platform.openai.com` for API reference and platform behavior;
   - `learn.chatgpt.com` for ChatGPT work guidance.
4. Preserve explicitly requested model names. Resolve “current,” “latest,” pricing, availability, limits, and defaults only from current official pages.
5. Cite the exact supporting pages near the claims they establish. Mark account-dependent behavior, unavailable facts, conflicts, and inferences explicitly.

Use a local manual or repository copy only when the user asks about that local installation or when current official documentation points to it as the relevant source. State when network or page retrieval is unavailable rather than presenting remembered product behavior as current.

## Scope and execution boundary

Documentation research does not authorize credentials, API calls that incur cost, account mutation, deployment, or changes to a user's OpenAI configuration. For an implementation request, use the documentation findings as inputs to the ordinary repository workflow and obtain any required credentials or consequential authorization at the action boundary.

Keep straightforward factual answers direct. For migration, prompting, or integration work, distinguish the documented baseline from the proposed design and verification plan.

When Workbench owns the effort, return sourced facts, inferences, unresolved questions, and exact citations for its current phase handoff. Do not create competing lifecycle state.
