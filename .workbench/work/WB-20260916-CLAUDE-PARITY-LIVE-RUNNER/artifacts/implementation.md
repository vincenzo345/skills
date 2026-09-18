# Docker isolation runner implementation

## Implemented surface

- `claude_harness_eval/experiment/isolation.py`: immutable policy, shell-free Docker command construction, staged-workspace guards, bounded concurrent output drains, timeout/forced cleanup, runtime and immutable-image inspection, executable canaries, immutable qualification records, drift/tamper validation, and qualified execution.
- `claude_harness_eval/__main__.py`: `isolation qualify` and `isolation run` public commands; live `doctor` revalidates exact qualification evidence.
- `claude_harness_eval/experiment/config.py`: live campaigns now require `qualification_file` and `qualification_sha256`; the unauditable `isolation_qualified` boolean is removed.
- `claude_harness_eval/experiment/controller.py`: live campaign preflight binds the configured digest and current runtime/image/policy evidence before stopping at the separately gated provider boundary.
- `tests/runtime/test_claude_harness_isolation.py` and `test_claude_harness_experiment.py`: public-seam success and adversarial tests, including a real local Docker journey.
- `docs/claude-harness-evals.md`: operator commands, guarantees, exclusions, and live-config contract.

## Enforced boundary

The runner mounts exactly one staged workspace, rejects control-plane roots and links, disables network, uses a read-only root and non-root user, drops all capabilities, enables no-new-privileges, caps memory/CPU/PIDs/tmpfs/output/time, and force-removes timed-out containers. Qualification binds all canaries to Docker server and image identity plus a canonical policy digest and sibling artifact digest.

## TDD record

Each slice began red at a confirmed public seam: policy command, output/timeout handling, canary qualification, tamper/drift validation, qualified execution, real CLI/Docker flow, live campaign binding, broad-workspace rejection, and unavailable-Docker diagnostics. Focused tests ended 22/22 green.

## Deliberate stop

No Claude or Codex model was invoked. No provider credential was read or copied. Provider egress, container images containing vendor CLIs, credential injection, spend enforcement against provider-reported usage, comparative campaigns, optimizer updates, and global prompt/hook promotion remain later work.
