---
name: ontology-map
description: Read, draft, and maintain a repository business ontology of domain concepts, attributes, rules, and relationships when application entities or relationships matter to a task.
---

# Ontology map

Use `docs/ontology/graph.json` as the reviewed business map when it exists. It describes domain meaning and relationships, never rows of application data. Read [the format](references/format.md) before creating or changing a map.

## Read for a task

When a task names a business entity or relationship, retrieve matching nodes and their adjacent edges before making domain assumptions. Read only the relevant neighborhood, then expand as new concepts arise. The optional `scripts/ontology_map.py show` command provides a bounded neighborhood. Trace claims to linked scope records, glossary entries, ADRs, and code. If the map disagrees with those sources, report the conflict; do not silently choose an authority. Consult implementation bindings only when the task needs code or data navigation.

## Draft or update

1. Identify business concepts in the project's own language, their meaning, selected business attributes and rules, and relationships from reviewed scope, glossary, accepted decisions, and current behavior. A table, join table, account record, or API model is not a business concept merely because it exists. Never inspect production rows or add personal or protected data.
2. Give every node and edge a concise business description and source paths. Record uncertainty explicitly and mark inferred claims as `proposed`; an expert-confirmed scope statement or accepted ADR may support `confirmed` after the user reviews the graph. Do not turn a storage discriminator into a business `is_a` relationship without domain evidence.
3. Record table mappings and join fields separately in `docs/ontology/implementation-bindings.proposed.json` when they help navigate the code. These bindings are evidence about implementation, not ontology nodes or edges. Record absent constraints and type mismatches there.
4. Write proposed graph changes to `docs/ontology/graph.proposed.json` or present a diff against the accepted graph. Do not replace `graph.json` until the user approves the specific changes. Preserve rejected or unresolved claims in review notes, not as accepted facts.
5. Run `scripts/ontology_map.py validate <proposal> --repo-root <repo> --bindings <bindings>` when bindings exist. Summarize additions, changed meanings, unresolved conflicts, and source evidence for review. On approval, update the accepted graph and bindings through the normal repo change process.

## Scope handoff

During `to-scope`, inspect the relevant graph neighborhood while drafting and reviewing features. Scope statements marked `inferred` can only propose ontology changes. After expert correction, present candidate changes and evidence to the user for approval. Do not rewrite signed scope or let the ontology map overrule the expert's words.
