# Evidence and execution loop

## Instruction surface

Claude Code documents `~/.claude/CLAUDE.md` as the personal instruction file loaded for every project. It is injected as context after the built-in system prompt, so it guides behavior but does not enforce it. Claude recommends concise, concrete instructions and a file below roughly 200 lines. Project and local instructions are additive and may be more specific. Critical mechanical guarantees belong in hooks, permissions, tests, and CI.

## Failure model

The reported failure is a broken completion boundary:

1. Claude recognizes a plausible implementation.
2. It edits the apparent location.
3. It runs a convenient or narrow check.
4. It interprets the check as proof of the requested outcome.
5. It reports completion before tracing adjacent behavior, realistic failure paths, or the final diff.

Generic reminders such as “be thorough” do not define where to spend effort or when work is done. The instruction must install explicit gates.

## Four-gate loop

### 1. Orient

Before changing anything:

- classify the request as answer, diagnose, review, or change;
- state the observable outcome and the evidence that would demonstrate it;
- read applicable instructions and inspect the smallest relevant implementation, callers, tests, configuration, and current repository state;
- distinguish explicit facts, evidence-backed facts, assumptions, and decisions that only the user can make; and
- ask only when a remaining material decision changes behavior, risk, or authorization.

The gate passes when the affected seam, constraints, and completion condition are concrete enough to act without guessing materially.

### 2. Act

For a requested change:

- make the smallest coherent change that addresses the root behavior rather than its most visible symptom;
- preserve unrelated work and follow established repository patterns;
- update all affected paths whose contract actually changes, including tests or documentation when needed; and
- keep investigation read-only when the user requested explanation, review, or diagnosis only.

The gate passes when the implementation is internally coherent and ready to be challenged, not when editing stops.

### 3. Falsify

Try to prove the solution wrong:

- run the narrowest meaningful check at the public seam, including a regression or realistic failure case when appropriate;
- add broader checks in proportion to blast radius and risk;
- inspect actual outputs and state instead of treating a zero exit code as sufficient;
- review the final diff as a skeptical reviewer for missed callers, invalid assumptions, unintended changes, weak tests, and error-path regressions; and
- verify the user-visible journey when an isolated component check cannot establish the requested behavior.

The gate passes only when the required evidence matches the claimed environment, seam, and journey, or an exact blocker is recorded.

### 4. Close

Before reporting success:

- reconcile the result against every part of the request and the completion condition;
- separate verified, inferred, unverified, blocked, and pre-existing failures;
- continue working while a safe, relevant next action can still close a gap; and
- report the outcome first, then the material changes, verification performed, and residual risk.

The gate passes only when the requested outcome is achieved with proportionate evidence or progress is impossible without a specific user decision or external state change.

## Proportionality

Correctness is the priority; ceremony is not. A one-line local change may need one focused check and diff review. Cross-cutting state, security, persistence, concurrency, or integration changes require broader tracing and realistic verification. Use the least work that proves the outcome, not the least work that produces an edit.
