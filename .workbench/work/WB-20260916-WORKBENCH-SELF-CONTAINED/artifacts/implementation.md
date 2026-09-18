# Implementation

- Added deployable `feature-planner` and `openai-docs` skill packages with Claude/Codex-compatible metadata and capability-based instructions.
- Retained the existing bundled `research` method.
- Updated Workbench discovery and routing so repository-bundled companions are the portable baseline, separately installed skills are optional extensions, and an absent optional skill is not itself a blocker.
- Added both skills to the plugin manifest and README, bumped the plugin to 1.2.0, and extended repository validation plus regression tests to enforce the contract.

No Workbench runtime or persistence schema was changed by this item.
