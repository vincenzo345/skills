# Housekeeping

Temporary root: `{{TEMP_ROOT}}`

Read for temporary placement, retained evidence or resources that can survive interruption. The persistent baseline covers ordinary work; use only the branch needed here.

For local processes or Docker resources, read [service lifecycle](housekeeping-services.md) before acquisition or reconciliation. File-only work skips that reference.

## Task workspace

Use a fresh task ID beneath the configured root. Keep the same ID while resuming the task. A task directory is disposable, not a deliverable or an effort tracker. Requested artifacts, maintained linting and regression tests belong in their established project locations.

Reuse existing checks before adding verification. A maintained check protects a concrete recurring behavior or provides a repeatable project command. A one-off check answers the current question; choose its cleanup before creation. Treat generated output independently from the checker. Promote a reproduction to the existing suite when it establishes a useful regression case, not merely because it might be reused someday.

## File cleanup and retention

Record ownership through the task directory and known created paths. Before removing a file, resolve its path and confirm it stays within that boundary. Treat symlinks and Windows junctions as links, not directories to traverse. Remove only links or files created by this task; preserve their targets, pre-existing files and other tasks' directories. Use native temporary fixtures and scoped teardown where available. Ignore rules hide disposable output from Git; they do not establish ownership.

After success or failure, remove disposable scripts and outputs once no longer needed. Preserve requested deliverables and intentional prototype evidence under their existing lifecycle rules. For unresolved failures, retain only the useful evidence and note its purpose and revisit condition. Reconcile that evidence when the issue is resolved. A clean Git status alone does not establish cleanup.

If task files or other resources may survive interruption, use one small `recovery.md` inside the task directory. Record canonical repository identity, task ID, owner evidence, created paths/resource identities, intended cleanup and any retention reason. Reuse that note while work continues, and remove it with the disposable task directory after reconciliation. A note records provenance; it does not prove the owner has stopped. Preserve and report resources whose ownership or active use is uncertain.

## Without repository configuration

Continue authorized work in an owned OS temporary namespace. Derive the repository key as the first 16 hexadecimal characters of SHA-256 over the UTF-8 canonical absolute repository-root path, using forward slashes and case-folding on Windows. Use `<OS-temp>/agent-housekeeping/<repo-key>/<task-id>/`. This stable namespace lets the next session locate the task without scanning the machine; keep the canonical root in any recovery note to detect a collision or changed location.

Suggest /setup-repo once to establish the lasting convention. Ordinary work does not require setup first. If verification genuinely requires repo-local files, use an established suitable location or resolve that setup choice before inventing one. Keep useful results in the project only when they are maintained checks or requested deliverables. The placeholder above is setup input, not a configured path in this fallback branch.
