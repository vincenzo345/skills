# Outcome frame

## Problem

Claude Code sometimes treats implementation as completion: it can make a plausible change, run an insufficient check, and report success while the requested behavior is still wrong.

## Desired behavior

For every task, Claude Code should establish the observable outcome, gather enough evidence to understand the affected seam, make the smallest coherent change, try to falsify its own solution, and claim completion only to the extent supported by verification.

## Completion condition

The deliverable is complete when a concise global instruction document:

- is ready to place at `~/.claude/CLAUDE.md` and stays below 200 lines;
- distinguishes answering, diagnosing, and changing work;
- establishes an explicit orient, act, falsify, and close loop;
- requires end-to-end impact tracing, proportionate focused checks, diff review, and honest disclosure of unrun or failing checks;
- preserves user scope and existing changes;
- continues until the requested outcome is achieved or a precise external blocker remains; and
- explains that instructions guide behavior while tests, hooks, permissions, and CI enforce critical invariants.

## Proof boundary

This work can prove that the instruction contract is concrete, internally consistent, correctly placed, and covers the reported failure mode. It cannot prove a behavioral improvement across Claude models without running a comparative task suite, which is outside the current authorization boundary.
