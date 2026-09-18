# Brownfield reconnaissance

The existing standard-library package has four files and an argparse CLI. Its public seam is `python -m claude_harness_eval`; the established tests invoke both Python APIs and subprocess CLI behavior. The controller will extend this seam with `doctor` and `experiment` subcommands while preserving `list`, `stage`, `verify`, `apply-reference`, and `validate`. New implementation lives under `claude_harness_eval/experiment/`; new public-seam tests live in `tests/runtime/test_claude_harness_experiment.py`. Existing unrelated dirty files are outside scope.
