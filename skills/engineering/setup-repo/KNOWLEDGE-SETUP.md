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

The index points to accepted current knowledge and identifies material proposals or implementation gaps in plain prose. Preserve useful unaccepted reasoning in its effort. Accepted knowledge belongs in the maintained document with a link to its effort evidence, without turning the index into a second tracker. Setup records locations; it does not invent design decisions or copy the specification into routine instructions.

Use the conditional index pointer in the shared instruction source. Follow only the entries relevant to the task; an ordinary edit without design context needs no index read. Check references and Git visibility before reporting setup complete.
