# Configure current knowledge

Read during /setup-repo. Reuse a suitable existing documentation index and locations before proposing another structure. Keep one short index of current knowledge, with relative links to existing useful documents. If no index exists, propose `docs/README.md`; create no empty documentation taxonomy or placeholder design records.

Record the chosen homes in the index, creating each document only when there is useful content:

| Role | Content and authority |
| --- | --- |
| Architecture | System responsibilities and runtime boundaries |
| Module design | Interfaces, dependencies, invariants and testing seams |
| Data-model design | Identity, relationships, integrity and lifecycle intent; link authoritative schemas/migrations rather than copying them |
| Decisions | Consequential accepted choices, rationale and supersession, using the existing ADR convention |
| Domain | Existing glossary/domain records own business meaning; link them rather than creating competing definitions |

Keep editable diagrams beside their document and reusable synthetic data with maintained fixtures. Reuse the configured tracker for effort plans, proposals, research and evidence. Keep stable effort paths and retained revisions; remove completed efforts from the active queue instead of relocating them.

When the user requests a reference source, or existing configuration/narrow discovery identifies one, propose a short **Reference sources** entry in the configured index. Reuse an equivalent existing section or link. Record its name, scope, locator and entry point; preserve user paths and access conventions on reruns. A local path is machine-specific, not a requirement for other checkouts. Keep sources read-only during lookup. Include the addition in the existing setup review; do not install a reader, create a separate source catalog, or ask another question when the choice is settled. If no source is selected, omit the section. A useful source entry alone can justify the existing default index without placeholder design documents.

For example: `Cookbook: engineering recipes and provenance; location: <user-selected path or URL>; entry point: <existing README or index>.` Replace placeholders only with confirmed source details, never a bundled machine-specific default. The index identifies the source; [ticket sizing](TICKET-SIZING.md#precedent-evidence) owns evidence assessment and routing. A source's presence or editorial review is not an endorsement of its claims.

The index points to accepted current knowledge and identifies material proposals or implementation gaps in plain prose. Preserve useful unaccepted reasoning in its effort. Accepted knowledge belongs in the maintained document with a link to its effort evidence, without turning the index into a second tracker. Setup records locations; it does not invent design decisions or copy the specification into routine instructions.

Use the conditional index pointer in the shared instruction source for design context and gaps in implementation evidence. Follow only relevant entries; ordinary edits with sufficient local evidence need no index read. Check references and Git visibility before reporting setup complete. Verify the selected source locator and entry point when accessible; report an unavailable optional source without inventing a replacement or repairing it. Preserve its configured location on reruns.
