# Workbench v0.5 wayfinding and data-model audit correction

The implementation corrects the behavior exposed by the pathway data-model audit:

- proposal destinations now consolidate every applicable design lens, including data-model design;
- data-model audits evaluate both requirements fitness and intrinsic health, with evidence-bounded table dispositions;
- a compact destination challenge stress-tests consequential routes without burdening bounded work;
- accepted v0.5 handoffs project findings, uncertainties, and decision records into the canonical map;
- `resume` exposes those learned facts and decisions without rereading the source artifact;
- stale Workbench policy provenance is rejected;
- a passed destination can become `awaiting-acceptance`, with explicit authorized closure through `close`; and
- material audit follow-ups are preserved as versioned artifacts instead of remaining only in chat.

Verification:

- `python -m pytest -q`: 115 passed.
- `python scripts/validate-workbench.py`: passed.
- `python scripts/validate-skills.py`: passed.
- Skill Creator `quick_validate.py skills/workbench`: passed.
- Root and bundled schema copies have matching SHA-256 hashes.
- Global Codex, Claude, and shared-agent Workbench paths are junctions to this repository skill.

Claim boundary: this is local implementation and packaging proof. It does not claim deployment or a measured business outcome.
