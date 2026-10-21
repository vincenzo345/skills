# Domain documentation

This repository uses a single-context domain layout: the existing [root glossary](../../GLOSSARY.md) and [project ADRs](../adr/). Existing repository/tooling decisions also remain in [.agents/adr/](../../.agents/adr/).

Before exploring domain behavior or proposing changes, read the glossary and the ADRs relevant to that work. Use the glossary's established terms in issues, specifications, and tests. Surface a conflict with an accepted ADR explicitly rather than silently replacing its decision.

For effort workspace changes, read the [stable workspace ADR](../adr/0001-stable-effort-workspaces.md). Effort records link to project-wide vocabulary and decisions; they do not create competing glossary or ADR stores.

Keep ordinary requirements, findings, and open questions in the effort's discovery record or current decision ticket. Use domain-modeling for qualifying vocabulary and ADR changes when needed. Missing domain records are created only as actual terms or decisions are resolved, not as setup scaffolding.

This setup preserves the existing glossary, ADRs, and their locations.
