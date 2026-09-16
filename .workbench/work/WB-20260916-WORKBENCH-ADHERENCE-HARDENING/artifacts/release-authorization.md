# Release authorization

Work item: `WB-20260916-WORKBENCH-ADHERENCE-HARDENING`

The user explicitly requested in the active conversation:

> commit, push, and update the global skills to reflect this newest version

Authorized scope:

- Commit the locally verified Workbench adherence patch, regression fixtures and tests, and this work item's audit trail.
- Push the resulting `main` commit to `origin/main`.
- Ensure the global Workbench installation matches the committed `skills/workbench` directory and validate it.

Excluded scope:

- Closing this Workbench item.
- Publishing or implementing the local runtime issue tickets.
- Accessing or mutating the affected manual-extraction Workbench item.

The conversation transport does not expose the exact source-message timestamp. The authorization records use the receipt-processing timestamp while preserving the exact grant language here; it is not represented as an independently observed source timestamp.
