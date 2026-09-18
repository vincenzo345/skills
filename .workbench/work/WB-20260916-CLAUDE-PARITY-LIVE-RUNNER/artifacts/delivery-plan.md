# Isolated runner delivery plan

## Confirmed seams

Tests observe only the public CLI, durable artifact files, and public isolation-runner qualification/execution results. The Docker CLI is an external boundary and may be substituted in focused tests; one real-Docker journey validates the actual boundary.

## Vertical red-green slices

1. **Policy-to-command:** a public runner invocation exposes a deterministic, shell-free Docker argv containing every security/resource/mount control; implement only command construction and identity inspection needed to pass.
2. **Bounded execution:** timeout and excess-output tests fail first; implement concurrent bounded drains, deadline handling, and forced name-based cleanup.
3. **Executable qualification:** a CLI/public API test expects a qualified record only when all canaries pass; implement workspace, root, identity/capability, network, secret/evaluator absence, resource, timeout, and cleanup canaries.
4. **Evidence integrity and drift:** tamper, policy drift, server drift, and image drift tests fail first; implement canonical digest verification and current-environment rebinding.
5. **Qualified fake execution:** a CLI/public API test runs a deterministic Python fake agent through validated evidence and observes bounded result fields; implement the qualified run path.
6. **Campaign fail-closed wiring:** live-config tests require a qualification reference/digest and prove invalid evidence blocks before adapter launch; preserve the intentional provider-execution stop after valid isolation.
7. **Real Docker journey:** qualify `python:3.12-slim`, execute a fake workspace mutation, trigger timeout cleanup, validate evidence, and prove no container remains.
8. **Regression and documentation:** run focused tests, evaluator validation, full runtime suite, compile checks, and update operator documentation with exact proof limits.

## Obligations

- Never use `shell=True` or interpolate an agent command into a shell string.
- Never mount the repository root, Docker socket, home directory, or credential locations.
- Never persist the random host-secret value.
- Treat every failed/missing canary and every evidence mismatch as unqualified.
- Keep paid model use and provider credential injection disabled.
- Record real-Docker proof separately from mocked boundary tests.

## Completion evidence

Feature-focused tests cover success and adversarial failure paths, a real local Docker journey passes, the existing evaluator and runtime suite remain green, and docs distinguish isolation qualification from live-provider or parity proof.
