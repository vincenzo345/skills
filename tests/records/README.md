# Workbench record fixtures

`proposal-only-checkpoint/` is one coherent persisted checkpoint containing all eight kernel record types. It represents a completed proposal stage while the wider work item is paused for a sponsor decision. This deliberately distinguishes a finished artifact and stage from a finished work item.

`contract-cases/` contains positive examples for a confirmed consequential decision with a consequence receipt and a bounded decision-delegation authorization. The repository validator derives focused negative cases from these records and confirms that missing control fields are rejected.

These fixtures test serialization and selected cross-record invariants. They are not proof that event storage is append-only, digests match real content, authorizations are legitimate, or transitions are legal; those remain runtime responsibilities.
