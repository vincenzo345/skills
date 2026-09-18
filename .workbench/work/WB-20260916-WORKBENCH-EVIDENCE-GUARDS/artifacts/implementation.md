# Evidence-guard implementation

Implemented the three bounded controls:

- Added a backward-compatible typed finding schema to both canonical and packaged schemas. Facts and measurements require sources; hypotheses, inferences, and legacy strings project as draft evidence work.
- Updated `accept-handoff` to resolve explicit finding sources and to use only those sources when establishing evidence.
- Added `workbench_diagnosis_hook.py` and registered one Claude `PreToolUse` matcher for investigative tools. It blocks only a Workbench bug/performance prompt before `diagnosing-bugs` is loaded and otherwise stays silent.
- Added two adherence cases: code reading remains a hypothesis, and a measured bottleneck needs a discriminating intervention before root-cause status.
- Added black-box runtime/hook tests and structural eval checks.

The global Workbench skill resolves to this repository through the existing junction, and the Claude hook command points through that global path. The frozen predecessor and manual-extraction items were not edited.
