# Precedent-evidence validation

Implementation basis: [specification revision 1](spec.md), authorized by the user after the [design refinement](discovery.md#short-refinement-pass). Initial implementation commit: `7a97aca`; review compares against `c15d4804cbd9f164e1dc74d96d0a7b7fa8b583b1`.

## Existing checks

- `python scripts/validate_v2_skills.py`: passed, including a repeat after review wording fixes.
- `python -m unittest discover -s scripts -p 'test_*.py'`: 60 passed in 221.441 seconds. Includes work-record, revision, selection, remote-contract, installer and package-validator coverage.
- `python skills/engineering/to-record/scripts/test_verify_preservation.py`: 27 passed.
- `npm run check-plugin-version`: passed, version 2.1.0 remains synchronized. A patch changeset records the new behavior; release/version publication was not run.
- `git diff --check`: passed. No prose-assertion tests or runtime enforcement were added.

The review corrections clarify an empty-search sentence, explicitly invalidate precedent evidence on relevant source/guarantee changes, and reconcile the historical overview with current authorization. They change no executable code or test environment. Existing test evidence remains applicable; package/reference checks cover the final prose.

## Neutral fresh-session discovery

Three separate ephemeral `codex exec` sessions ran in disposable fixtures with a read-only child sandbox and the same neutral task:

> Assess whether adding retries to deliver_once is ready to implement. Identify missing evidence and the next step. Do not edit files or make network requests.

The prompt named no policy, index, source or instruction file. Each fixture supplied an AGENTS.md consumer pointer to the actual updated TICKET-SIZING.md content, a minimal delivery function, and a requirement to avoid duplicate remote deliveries after timeout. Configured fixtures used a custom `engineering/context.md` index and a read-only synthetic example marked reviewed but supported only by a synthetic happy-path test. The legacy fixture used the previous design-only index trigger; the custom fixture used the expanded trigger. The unconfigured fixture had no index or source. These exercise the pointer chain in controlled fixtures, not the complete interactive setup-repo generation or production application flow.

| Fixture | Observed file reads and decision | Result |
| --- | --- | --- |
| Custom index | Read `workflow/TICKET-SIZING.md`, `engineering/context.md`, local code/README and `references/retry.md`. Said the reviewed label and synthetic test did not establish remote idempotency. Requested provider/version contract before readiness. | Discovery and evidence distinction observed |
| Legacy trigger | Read the sizing reference and custom index despite the older design-only pointer, then the exact example. Distinguished a bounded retry loop from duplicate-effect protection and kept the scope unready. | Legacy discovery observed |
| Unconfigured | Read sizing guidance and local code/README. Explicitly observed no configured index/source and requested the provider contract without requiring setup, Cookbook repair or a guessed checkout. | Fallback observed |

All three processes exited 0. Observed commands read fixture files; no source service, source acquisition, external recipe execution or application edits occurred. The run logs contained a harmless CLI stdin notice. Both configured runs loaded the index together with the sizing reference before separately reading implementation files: these runs establish discovery, not strict lazy-read ordering or minimized context load. Sufficient-local-evidence stopping is covered by instruction review below, not a claimed runtime efficiency result.

The temporary fixtures copied the policy from `7a97aca` before the two subsequent editorial clarifications; those clarifications do not change the discovery branch exercised. Raw disposable traces are summarized here and removed after all processes finish. No actual Cookbook service or application was run or modified.

## Scenario review against the completed workflow

Manual instruction walkthroughs are separate from the observed fresh-session checks.

| Scenario from the design | Governing behavior in the completed edits |
| --- | --- |
| Local filter and relevant tests match | Precedent evidence stops discovery at sufficient local support; no optional source lookup is required. |
| Confident unfamiliar API usage | Confidence is not evidence; inspect applicable versioned documentation or maintained upstream code/tests. |
| Familiar retry example claimed to prove exactly-once effects | Inspect required guarantee, assumptions and evidence origin; retain the gap. Also exercised by the configured runtime fixtures. |
| No code example, straightforward official contract | Conditional routes permit normal implementation/verification; no automatic experiment or human gate. |
| Unknown crash behavior | Use the cheapest decisive evidence and a bounded experiment only for the remaining observable consequential fact. |
| Cookbook unavailable, sufficient local evidence | Local stopping rule applies; no source repair obligation. |
| Missing indispensable evidence | Name the unresolved fact; affected work remains unready and independent ready work can continue under existing sizing rules. |
| Reviewed recipe, synthetic evidence only | Source assertions, reports and synthetic tests remain distinct from independent reproduction. Observed in both configured fixtures. |
| Old/conflicting version or assumptions | Resolve the difference; age alone neither validates nor disqualifies. Stale retrieval uses verified canonical content or stays unknown. |
| Integrated work changes a future assumption | Existing impact checks re-estimate affected work; final verification guidance explicitly includes relevant source revisions, warnings, assumptions and guarantees. |
| Direct specification | Existing implement entry pointer applies the same shared readiness gate to the entire scope. |
| Required full suite | Mandatory checks and acceptance verification remain intact regardless of precedent. |
| Setup rerun, custom paths or absent source | Reuse existing index/section/pointer and user access convention; omit unselected sources, preserve unavailable configured locators and review only missing additions. |

## Review and completion

The code-review skill's independent Standards and Spec passes reviewed `c15d480...7a97aca`. Spec found no missing requirements or scope creep. Standards found stale effort overview wording and an ambiguous empty-search sentence; both were corrected. Final follow-up review results and packaging closeout are recorded with effort completion.

## Limits

This is skill/reference/documentation behavior, not a runtime guarantee. Controlled discovery was observed; interactive setup generation/rerun behavior is statically reviewed, and no broad claim of reliable lazy loading follows from these samples. The pilot has not run. No reduction in errors, rework or overhead is claimed. Cookbook remains unconfigured for this checkout, and unrelated working files are preserved. No push is authorized or performed.
