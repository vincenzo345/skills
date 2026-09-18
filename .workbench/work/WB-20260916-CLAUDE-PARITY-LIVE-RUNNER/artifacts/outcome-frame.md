# Isolated live-runner outcome

## Destination claim

This item ends when the repository contains a locally verified Docker isolation boundary with auditable qualification evidence and a deterministic, bounded subprocess runner. It does not end with—and cannot claim—Claude/Codex parity, provider credential safety, provider network allowlisting, or production readiness.

## Observable completion

- A public CLI command qualifies a specific local Docker server, immutable image, and isolation policy using executable canaries.
- Qualification proves a writable staged workspace, read-only root filesystem, absent evaluator and host-secret material, disabled network, dropped privileges, resource caps, and timeout cleanup.
- Qualification is persisted as an integrity-protected artifact and invalidated by tampering or runtime/policy/image drift.
- A deterministic fake agent executes through the same runner boundary with bounded output, time, and cleanup behavior.
- Existing fake campaign behavior remains compatible and live provider execution remains fail-closed.

## Authority and exclusions

Repository mutation, Docker canaries, and local implementation are authorized. Model invocation, credential copying, quota consumption, global prompt/hook promotion, commit, deployment, publication, and closure are excluded.

## Confirmed public seams

The tests observe the public CLI, campaign artifact store, and the isolation runner's qualification/execution results. Docker itself is treated as an external system boundary.
