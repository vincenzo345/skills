# Service lifecycle

Use this branch only for local processes or Docker resources. Apply the shared ownership, retention and recovery-note rules in [housekeeping](housekeeping.md).

## Acquire with teardown

Identify the concrete verification gap before starting a service. Prefer existing test fixtures, context managers, shell traps or `try/finally` teardown. Scope cleanup alongside acquisition so success, failed checks and partial startup all release acquired resources.

Before acquisition, put the intended unique namespace, cleanup and owner evidence in the task's single recovery note. Capture resulting identities there promptly, including partial acquisitions. Reuse native labels and task context rather than adding per-command logs.

- **Processes:** retain the native process handle where available; record PID, start identity, executable and task-specific command identity. Launch Windows helpers hidden. Before termination, verify current identity matches; a PID alone can name a replacement process. Use native supervised child teardown when available. Report unverified descendants rather than terminating by broad name or port.
- **Docker:** use a unique task/project namespace and ownership labels. Record container and network IDs, volume names plus ownership labels, and the selected Docker context. Distinguish disposable volumes from shared or external data before creating or attaching them. Prefer native removal flags or scoped Compose teardown when the entire project is exclusively task-owned. Inspect exact identities and ownership before removal; remove volumes only when proven disposable. Preserve shared images and caches.

Inspect each owned container's mounts before removing it, including failed or partially started containers. Images can create anonymous volumes without explicit mount flags. Capture those exact identities and disposition in the same note; use native teardown that removes disposable anonymous volumes (for example, `docker rm -v`) and check their absence. Container removal without volume removal loses that ownership link and can leak data.

## Reconcile

Release acquired services when verification finishes, even after failure. Remove owned containers before their disposable networks and volumes; confirm each removal and process exit through scoped native observations. An empty Git diff does not establish service cleanup.

If startup fails before an ID is returned, reconcile only the recorded namespace using native ownership evidence. A matching name alone is insufficient. If the runtime is unavailable, identity differs, ownership is uncertain or cleanup fails, preserve the recovery note and report the unresolved identities and next action. Never count an unavailable observation as absence.

Keep a live environment only for continuing debugging or requested review, recording its purpose and revisit condition. Remove the note and disposable task directory only after every owned resource and retained diagnostic is reconciled. Follow the shared recovery rules before acting on a previous session's resources; provenance alone does not establish inactivity.
