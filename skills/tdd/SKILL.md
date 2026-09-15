---
name: tdd
description: Test-driven development at public seams. Use when building or fixing behavior test-first, applying red-green-refactor, or defining reliable integration evidence.
---

# Test-Driven Development

Work one vertical `red -> green -> refactor` slice at a time. Tests specify behavior through public interfaces and survive internal refactoring.

Read the project's glossary, ADRs, source criteria, and approved test seams. Existing seams already accepted by the source artifact do not need to be reconfirmed. Leave a consequential unresolved seam decision with its options and effects instead of guessing; do not interrupt for routine mechanical choices.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidance.

## Proof contract first

Before a criterion's first red test, know:

- the public journey or seam;
- the independent source of expected results;
- the named fixture identities or nonzero minimum population;
- the environment and proof level the test can actually establish.

A unit or mocked test normally establishes local behavior, not deployment or outcome verification. Apply the proof rules below to the completion claim.

## A valid red state

The test must fail because the required behavior is absent or wrong. A syntax error, missing dependency, broken harness, inaccessible environment, or unrelated failure is not red; repair or report that blocker before continuing.

## A valid green state

- Implement only enough behavior to satisfy the current criterion.
- Expected values come from a worked example, accepted specification, independently verified golden, or other source that can disagree with the implementation.
- Never generate expected output with the same logic being tested.
- Establish expected population before calculating pass rates or completeness. Empty or unexpectedly reduced populations fail the evidence check.
- Mocks may prove a local contract at a genuine external seam. They do not prove the real integration, target environment, or end-to-end journey.
- Skipped, disabled, or non-executed tests are not green evidence.

## Refactor

Once green, improve structure without changing observable behavior. Keep the same test green. Avoid speculative abstractions that the next slice does not require.

## Repeat and verify

Add the next smallest behavior at the same or next approved seam. Run focused checks during each cycle and the complete relevant suite at the end. Record criterion-specific evidence without turning a generic suite pass into proof of every requirement.
