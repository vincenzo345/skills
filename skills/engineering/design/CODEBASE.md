# Codebase and module design

Use the existing `codebase-design` skill as the single source of module vocabulary and principles. Load it through the available skill mechanism; if no invocation tool exists, locate and read its installed SKILL.md from the skill catalog. Keep it independently reachable for existing callers. Do not copy its glossary or principles into this branch.

Apply the design conversation to the specific module question:

1. Trace representative callers, dependencies, invariants, errors, and tests. Describe the complexity callers currently carry and the behavior the module must support.
2. Use `codebase-design` to propose the interface and seam, showing concrete usage and the complexity hidden in the implementation. Reach its deepening or alternative-interface references only when their stated conditions apply.
3. Compare viable choices on depth, locality, testability, compatibility, and the actual need for adapters. Recommend a choice. Involve the human when behavior, compatibility, ownership, or a significant tradeoff remains open; resolve routine structure from evidence and established conventions.
4. Exercise the proposed interface with a normal caller, an error case, and a likely change. Use a runnable experiment only for a question examples and inspection cannot settle.

Hand off the interface, invariants, seam and dependency decisions, representative usage, migration impact, and verification approach. Keep internal module choices within the architecture's established responsibilities; return a system-level conflict to the architecture branch instead of silently redesigning the system.
