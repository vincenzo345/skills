# Docker isolation runner local verification

## Passed evidence

- `python -m pytest tests/runtime -q`: **129 passed** in 142.35 seconds.
- Focused isolation and experiment-controller suite: **22 passed**, including the real Docker CLI qualification/doctor/fake-agent journey.
- `python -m claude_harness_eval validate --repeat 2 --json`: passed; across 20 tasks and two repetitions, all 40 untouched baselines failed and all 40 reference overlays passed.
- Real qualification `37553f0ad0134a50778e117d` revalidated against Docker server 28.3.2 and immutable image `sha256:7026274c107626d7e940e0e5d6730481a4600ae95d5ca7eb532dd4180313fea9`; all 13 canaries are true.
- `docker ps -a --filter name=harness-`: no remaining harness containers.
- Python compilation, `git diff --check`, Workbench replay (11 events at the time of the check), and the repository skill validator passed.

## Adversarial coverage

Tests establish fail-closed behavior for missing Docker, malformed commands, broad/control-plane workspaces, links, output overflow, timeout, failed canaries, missing artifacts, byte tampering, policy drift, runtime drift, image drift, config digest mismatch, and provider-launch attempts beyond the qualified boundary.

## Non-vacuity

The real-Docker journey launched the local image under the enforced flags, observed all kernel/cgroup canaries, force-stopped a deliberate sleeper, found no remaining container, then ran a separate deterministic fake agent that wrote `agent.txt` only in its mounted staged workspace. The benchmark self-check independently preserves red baselines and green references.

## Exact proof boundary

This proves local implementation of the Docker isolation/qualification boundary on the current Windows + Docker Desktop Linux engine and preserves the prior evaluator behavior. It does not prove that arbitrary hostile generated code cannot exploit Docker/kernel defects. It does not prove provider credential safety, restricted provider egress, Claude/Codex CLI availability inside the image, provider cost accounting, model parity, prompt improvement, global configuration promotion, deployment readiness, or business outcome.
