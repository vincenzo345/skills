---
name: diagnosing-bugs
description: Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow.
---

# Diagnosing Bugs

Diagnose the reported failure with a **tight** feedback loop: a specific signal that distinguishes causes and can verify the fix. Reuse existing reports, reproductions and test results. Scale the investigation to the uncertainty; an understood defect needs a focused regression, not every technique below.

When exploring the codebase, read `GLOSSARY.md` (if it exists) and relevant ADRs. Follow [verification evidence](../setup-repo/TICKET-SIZING.md#verification-evidence) for check boundaries, stopping and reuse.

## Protect evidence

Redact secrets and personal data from commands, outputs and captured artifacts. Keep credentials in environment variables; show only the lines carrying the diagnostic signal. If redacted output is insufficient, identify the missing observation and request only the access or artifact needed.

For disposable validation or interrupted work, read the housekeeping reference named by repository instructions, or the [shared fallback](../setup-repo/housekeeping.md#without-repository-configuration) if none is configured. Preserve useful failed evidence with its code/environment basis; later passing runs do not explain an earlier failure.

## 1. Establish the failure and next observation

Identify the expected behavior, observed symptom, affected input and execution context from the report and retained evidence. Inspect relevant code to form tentative explanations and choose a reproduction or probe. Keep hypotheses distinct from established causes.

Prefer an existing test or invocation that reaches the actual failure. If needed, use a request, CLI fixture, browser interaction, captured-event replay or minimal harness. Choose the cheapest stable boundary that preserves the failure mechanism, following [TDD's seam guidance](../tdd/SKILL.md#seams-where-tests-go). A slower database or application-flow reproduction is appropriate when the interactions are necessary.

Before a new experiment, state briefly what observation would distinguish a plausible cause or supply missing evidence, and when to stop. Keep this in the existing investigation note or update, not a separate plan. Use bounded repetition, stress, fuzzing or bisection only when it answers that question; choose the bound from expected information and execution cost rather than an arbitrary trial count.

## 2. Reproduce and narrow

Run the selected command and retain its relevant output. Confirm it reaches the reported failure, not a nearby defect or setup error. Narrow inputs and setup while the failure remains observable; stop minimising when the scenario is practical to diagnose and suitable for regression coverage.

For intermittent failures, retain failing and passing contexts and target their differences. Record the observed reproduction rate when repetitions are useful. Increasing that rate is a technique, not a prerequisite for investigation.

If the failure cannot be reproduced, continue code inspection or targeted instrumentation only when it can resolve a named uncertainty. When further unchanged runs would add no information, stop those runs, state the unresolved fact and next decisive observation, and continue independent authorized work. Request human input only for missing access, evidence or a consequential decision. An unresolved cause stays unresolved.

## 3. Test explanations

Rank plausible explanations from the evidence. Each experiment needs a prediction: "If X is the cause, changing Y should produce Z." Use only as many hypotheses as the evidence supports. Communicate the leading explanation and uncertainty without adding an approval gate for routine diagnosis.

Use a debugger or targeted boundary logs to distinguish predictions. Change one relevant variable at a time where practical. Tag temporary logs with a unique prefix, such as `[DEBUG-a4f2]`, for removal. For performance defects, measure the relevant baseline and use a profiler, query plan or targeted timing before changing code.

Revise the explanation when results contradict it. A passing test of an injected fault can establish coverage of that mechanism; it does not by itself establish the cause of the original intermittent failure.

## 4. Fix and verify

Once evidence supports a fix, extend existing regression coverage or write a failing test before changing behavior. The test must exercise the real bug pattern and use independently established expected behavior. If no adequate test boundary exists, report that limitation and the smallest viable verification alternative; do not build an architectural subsystem merely to obtain a test seam.

Watch the regression fail for the intended reason. If red is forced by mutating code or a fixture, diff against a pristine copy to prove the mutation landed, and distinguish that evidence from reproduction of the original defect. Apply the smallest supported fix and verify the regression passes. Verify the original scenario too when the focused test does not already cover it; reuse a valid result rather than running the same scenario again at cleanup.

## 5. Close with evidence

Remove temporary instrumentation and clean up task-owned disposable resources under the housekeeping policy. Keep maintained regression tests and useful failure evidence.

Report the diagnosed cause, changed behavior, verification and remaining uncertainty in the existing handoff or PR. Claim resolution only at the proof level actually established. Missing access, a non-reproduced historical failure or an inadequate test boundary remains a limitation, not a pass.
