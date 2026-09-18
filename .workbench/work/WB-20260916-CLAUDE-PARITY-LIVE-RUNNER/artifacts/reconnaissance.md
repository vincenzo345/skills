# Live-runner brownfield reconnaissance

## Current state

- `experiment/controller.py` owns campaign initialization, scheduling, immutable run results, crash reconciliation, and the sole live-mode rejection.
- `experiment/config.py` accepts a human-entered `isolation_qualified` boolean but cannot bind it to evidence, runtime identity, image identity, or policy.
- `experiment/store.py` already provides canonical digests, immutable writes, atomic writes, and append-only events.
- `experiment/adapters.py` builds vendor command arguments but does not launch them.
- `__main__.py` is the stable public CLI seam; current runtime tests invoke it in subprocesses.
- The task staging and verifier boundary is independent of agent launching and should remain unchanged.
- Docker Desktop 28.3.2 is reachable and `python:3.12-slim` exists locally.

## Smallest change surface

1. Add `experiment/isolation.py` for an immutable policy, bounded Docker execution, executable canaries, qualification artifact creation, and artifact verification.
2. Add an `isolation qualify` CLI command with machine-readable output.
3. Replace the ungrounded live-mode assertion with a qualification artifact reference/digest and validate it before any future provider launch.
4. Preserve the existing fake campaign path and vendor argv builders.
5. Add public tests for qualification/execution behavior and a gated real-Docker integration journey.

## Risks and controls

- Shell injection: construct argv arrays only; never invoke a shell.
- Host disclosure: mount only the staged workspace; never mount the repository, evaluator, Docker socket, home directory, or credential directories.
- Container breakout surface: read-only root, non-root UID/GID, all capabilities dropped, no-new-privileges, no network, capped CPU/memory/PIDs, bounded tmpfs.
- Hangs/orphans: unique names, host timeout, forced removal on timeout/error, and a cleanup canary.
- Output exhaustion: drain concurrently but retain only configured byte limits; mark overflow as failure.
- Stale evidence: bind qualification to schema, Docker server identity/version, immutable image ID, and canonical policy digest; protect the record with a sibling SHA-256.

## Compatibility

No database, external Python dependency, evaluator contract, or fake-campaign result format needs to change. Live provider authentication and egress are deliberately outside this item.
