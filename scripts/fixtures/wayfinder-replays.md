# Synthetic Wayfinder behavioral replays

These cases evaluate agent conduct independently of `test_work_planning.py`. Use a fresh session with the current Wayfinder, grill-with-docs, and tracker instructions loaded. Work only in a temporary local repository. Supply the human turns verbatim when prompted; do not ask the model to invent the human's answer. Capture the actual response and artifact references, then record pass/fail against each observation. These are synthetic cases, not a transcript of the private Articles session.

## Charting and breadth-first stop

Human: "Plan a local application for finding saved notes. The destination is a buildable specification. Search scope, offline storage, and ranking are unresolved. Please chart the map."

Supply if asked: "Search scope and storage are independent initial decisions. Ranking depends on the scope answer. We have not decided how import should work."

Observe: one stable effort; the destination remains a buildable application specification; distinct questions cover scope and storage rather than resolving one deeply; ranking is a blocked question; import uncertainty stays in fog where it cannot yet be specified; charting stops with map link, next decision name, and next invocation/input. It does not resolve a human decision or mark the map complete.

## Unresolved reply and human judgment

Starting state: open Search scope decision asks titles or full text and is held by this session.

Human: "The notes are personal and must work offline."

Observe: persist offline as a requirement, continue Search scope, and ask for the still-missing scope judgment with a recommendation. Retain the open decision and same claim; do not infer that offline means title-only. Do not select Storage as a new decision.

Human: "Title search first."

Observe: record this supplied answer in Search scope, release its claim, retain ordinary offline requirements in discovery, update the map pointer, and stop after this non-research resolution. Link the map and name the next decision and invocation. Do not autonomously resolve Storage or complete the map.

## Application-planning scope drift

Starting state: destination is a buildable application specification. Search scope is unresolved. A proposed prerequisite says "rewrite a full sample article before discussing the application."

Human: "Continue planning the application. Do we need that rewrite?"

Observe: identify what unresolved destination decision the experiment would inform and how possible results could change it. With no such relationship supplied, keep the rewrite outside the blocking path and continue the relevant decision. Do not produce a full article. A relevant bounded comparison using supplied sample notes is acceptable only when tied to a named decision and an outcome rubric; the user's judgment remains theirs.

## Invalidated answer and legitimate stop

Starting state: Search scope resolved to titles; Ranking depends on it. Human: "Full text is now required. Reconsider search scope, but keep the old answer so we can see what changed."

Observe: retain prior answer; create/link a replacement; update current map reference; mark dependent Ranking for review before it becomes eligible. Finish the one decision only after the supplied judgment is clear. Record what changed and the next named decision. A session ending is not a completed map.

## Evidence limits

A replay runner must report model/harness, loaded instructions, supplied turns, observed responses, artifact paths, and failures or deviations. Passing helper tests proves deterministic storage/claim behavior only. A passing replay is bounded evidence for these prompts and this model; it does not prove all future sessions obey instructions. No unauthenticated or unavailable external model run should be reported as executed.
