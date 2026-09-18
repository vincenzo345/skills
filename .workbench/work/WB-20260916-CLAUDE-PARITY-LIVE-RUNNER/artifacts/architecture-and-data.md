# Docker isolation architecture and qualification model

## Module boundary

`experiment.isolation` owns four public concepts:

- `IsolationPolicy`: immutable security/resource/output/time limits with a canonical dictionary and digest.
- `DockerIsolationRunner`: inspects runtime/image identity, constructs shell-free `docker` argv, executes with bounded output/time, and force-removes named containers on exceptional paths.
- `qualify(...)`: runs executable canaries and writes integrity-protected evidence.
- `run_qualified(...)`: revalidates evidence against current runtime/image/policy, then executes an argv command in a staged workspace.

The CLI exposes those last two operations. The campaign controller consumes qualification validation but does not own Docker details. Vendor adapters remain launch-agnostic.

## Enforced container policy

- exact locally present image resolved to immutable image ID;
- `--network none`, `--read-only`, `--cap-drop ALL`, `no-new-privileges`;
- numeric non-root `65534:65534`;
- CPU, memory, and PID limits;
- one bind mount: caller-selected staged workspace at `/workspace`;
- bounded, non-executable tmpfs at `/tmp`;
- no Docker socket, evaluator repository, home, credential, SSH, or provider-config mount;
- unique container name, host deadline, bounded retained stdout/stderr, forced cleanup.

## Durable qualification record

Stable identity is the qualification ID derived from canonical runtime, image, policy, and canary results. The JSON record contains:

- schema/version/status/timestamp;
- Docker server ID, version, OS type, and architecture;
- requested image plus immutable image ID and available repository digests;
- complete canonical policy and `policy_sha256`;
- named boolean/details for workspace write, read-only root, non-root UID, zero effective capabilities, no-new-privileges, no network route, absent planted host secret, absent evaluator path, resource ceilings, timeout, and cleanup canaries;
- bounded execution metadata, never host secrets or provider credentials.

`qualification.json` is canonical JSON and `qualification.sha256` is its byte digest. Creation is immutable/idempotent for identical bytes. Consumption verifies both files, schema/status, every required canary, policy digest/equality, current Docker server identity, and current immutable image ID.

## Lifecycle and consistency

Qualification is created only after all canaries pass. It has no partial or mutable qualified state. Runtime, image, policy, file-integrity, or canary mismatch invalidates it; requalification creates evidence in a new empty destination. There is no database migration or concurrent writer protocol beyond the existing immutable/atomic file helpers. Campaign manifests copy the evidence reference and digest; they do not convert it into truth.

## Sensitive-data boundary

The planted secret is random, remains outside the mounted workspace, is not passed in argv/environment, and only its non-sensitive digest/presence result may be recorded. Provider credentials are excluded from this destination. Qualification artifacts are internal and contain environment identity, not credentials.

## Rejected alternatives

- A config boolean was rejected because it is unauditable and cannot detect drift.
- Host-process sandboxing was rejected because Claude's Windows sandbox reports unsupported and host execution exposes broader filesystem/process state.
- Mounting the repository read-only was rejected because hidden evaluator material and unrelated user files would become observable.
- Mutable “latest qualification” records were rejected because they weaken lineage and tamper detection.
