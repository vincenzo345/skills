#!/usr/bin/env python3
"""
scaffold.py — materialize (or extend) a Planner->Generator->Evaluator build harness in any project.

Used by the `agent-harness` skill. Two modes:

  init        Write a fresh harness into a target project directory from a config JSON.
  add-sprints Append new sprints to an EXISTING harnessed project (feature enhancement).

The harness itself is stack-agnostic: the only project-specific pieces are ci/build.sh and
ci/test.sh (thin wrappers around your build/test commands) and how the Evaluator "exercises" the
artifact (a prose instruction embedded in the evaluator agent). Everything else is identical across
projects, which is the whole point — reuse the same infrastructure everywhere.

Usage:
  python3 scaffold.py init        --target <project_dir> --config <config.json>
  python3 scaffold.py add-sprints --target <project_dir> --sprints <sprints.json>

See the skill's SKILL.md for the config schema and the interview that produces it.
"""
import argparse, json, pathlib, stat, sys

HERE = pathlib.Path(__file__).resolve().parent
TPL = HERE.parent / "assets" / "templates"


def _read(name):     return (TPL / name).read_text(encoding="utf-8")
def _sub(text, d):
    for k, v in d.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text
def _write(path, text, execable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n": on Windows, write_text would emit CRLF and break the *.sh files in Git Bash
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    if execable:
        path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def render_rubric(cfg):
    dims = cfg["rubric_dimensions"]
    thr = cfg.get("pass_threshold", 7.5)
    formula = " + ".join(f'{d["weight"]}·{d["name"].replace(" ", "")}' for d in dims)
    out = [f'# {cfg["project_name"]} — Evaluation Rubric', ""]
    out += [f"Weighted = {formula}",
            f"PASS a sprint only at weighted ≥ {thr} AND zero contract criteria failing.", ""]
    for d in dims:
        out.append(f'## {d["name"]} ({d["weight"]})')
        for c in d.get("criteria", []):
            out.append(f"- {c}")
        out.append("")
    out += ["## Calibration",
            "Point these criteria at the example files in `.harness/references/` "
            "(GOOD to resemble, `bad-*` to avoid). Concrete references beat adjectives."]
    return "\n".join(out) + "\n"


def render_plan(cfg):
    return json.dumps({
        "title": cfg["project_name"],
        "pitch": cfg["pitch"],
        "invariants": cfg.get("invariants", []),
        "sprints": cfg["sprints"],
    }, indent=2) + "\n"


def render_progress(sprints):
    return json.dumps({
        "current": sprints[0]["id"] if sprints else 1,
        "run_started": None,
        "sprints": {str(s["id"]): "pending" for s in sprints},
    }, indent=2) + "\n"


def cmd_init(args):
    cfg = json.loads(pathlib.Path(args.config).read_text())
    root = pathlib.Path(args.target).resolve()
    for req in ("project_name", "pitch", "build_cmd", "test_cmd", "exercise",
                "rubric_dimensions", "sprints"):
        if req not in cfg:
            sys.exit(f"config missing required field: {req}")

    subs = {
        "PROJECT_NAME": cfg["project_name"],
        "PITCH": cfg["pitch"],
        "STACK_NOTES": cfg.get("stack_notes", "(none specified)"),
        "BUILD_CMD": cfg["build_cmd"],
        "TEST_CMD": cfg["test_cmd"],
        "EXERCISE": cfg["exercise"],
        "INVARIANTS": "\n".join(f"- {i}" for i in cfg.get("invariants", [])) or "- (none specified)",
    }

    # templated text files: template name -> output path
    templated = {
        "CLAUDE.md":               root / "CLAUDE.md",
        "agent-planner.md":        root / ".claude/agents/planner.md",
        "agent-generator.md":      root / ".claude/agents/generator.md",
        "agent-evaluator.md":      root / ".claude/agents/evaluator.md",
        "command-harness-run.md":  root / ".claude/commands/harness-run.md",
        "settings.json":           root / ".claude/settings.json",
        "references-README.md":    root / ".harness/references/README.md",
    }
    for tname, out in templated.items():
        text = _sub(_read(tname), subs)
        # Never clobber a pre-existing CLAUDE.md or settings.json in an existing repo:
        # write alongside and let a human (or Claude) merge.
        if out.name in ("CLAUDE.md", "settings.json") and out.exists():
            alt = out.with_name(out.name + ".harness-new")
            _write(alt, text)
            print(f"MERGE REQUIRED: {out} already exists — wrote {alt} instead; merge by hand.")
        else:
            _write(out, text)

    # executable wrappers
    _write(root / "ci/build.sh", _sub(_read("build.sh"), subs), execable=True)
    _write(root / "ci/test.sh",  _sub(_read("test.sh"),  subs), execable=True)

    # LF pinning — the loop's `git reset --hard` re-checks-out ci/*.sh; with autocrlf on
    # Windows that injects \r and Git Bash chokes. Append to an existing .gitattributes.
    ga = root / ".gitattributes"
    ga_text = _read("gitattributes")
    if ga.exists():
        cur = ga.read_text(encoding="utf-8")
        if "*.sh text eol=lf" not in cur:
            _write(ga, cur.rstrip() + "\n\n" + ga_text)
            print("Appended LF pinning for *.sh to existing .gitattributes")
    else:
        _write(ga, ga_text)

    # verbatim
    _write(root / "orchestrator/run_harness.py", _read("run_harness.py"), execable=True)
    _write(root / "orchestrator/requirements.txt", _read("requirements.txt"))

    # generated state
    _write(root / ".harness/plan.json",     render_plan(cfg))
    _write(root / ".harness/progress.json", render_progress(cfg["sprints"]))
    _write(root / ".harness/rubric.md",     render_rubric(cfg))
    _write(root / ".harness/contract.json",
           json.dumps({"$comment": "filled by the generator when it proposes a contract",
                       "sprint": None, "criteria": []}, indent=2) + "\n")
    _write(root / ".harness/journal.jsonl",
           json.dumps({"ts": "seed", "sprint": 0, "role": "orchestrator", "round": 0,
                       "action": "scaffolded", "verdict": None,
                       "note": "run /harness-run or orchestrator/run_harness.py to begin"}) + "\n")

    print(f"Harness scaffolded into {root}")
    print("Next: git init && git add -A && git commit -m 'scaffold harness'")
    print("      wire ci/build.sh + ci/test.sh to your stack, add references, then /harness-run 1")


def cmd_add_sprints(args):
    root = pathlib.Path(args.target).resolve()
    plan_p = root / ".harness/plan.json"
    prog_p = root / ".harness/progress.json"
    if not plan_p.exists():
        sys.exit(f"no harness found at {root} (missing .harness/plan.json). Run `init` first.")
    plan = json.loads(plan_p.read_text())
    prog = json.loads(prog_p.read_text())
    new = json.loads(pathlib.Path(args.sprints).read_text())
    if isinstance(new, dict) and "sprints" in new:
        new = new["sprints"]

    next_id = max((s["id"] for s in plan["sprints"]), default=0) + 1
    for s in new:
        s["id"] = next_id
        plan["sprints"].append(s)
        prog["sprints"][str(next_id)] = "pending"
        next_id += 1
    prog["current"] = min(int(k) for k, v in prog["sprints"].items() if v != "passed")

    plan_p.write_text(json.dumps(plan, indent=2) + "\n")
    prog_p.write_text(json.dumps(prog, indent=2) + "\n")
    print(f"Appended {len(new)} sprint(s). Run: python3 orchestrator/run_harness.py "
          f"--start {prog['current']}   (or /harness-run {prog['current']})")


def main():
    ap = argparse.ArgumentParser(description="Scaffold or extend a build harness.")
    sub = ap.add_subparsers(dest="mode", required=True)
    pi = sub.add_parser("init"); pi.add_argument("--target", required=True); pi.add_argument("--config", required=True)
    pa = sub.add_parser("add-sprints"); pa.add_argument("--target", required=True); pa.add_argument("--sprints", required=True)
    args = ap.parse_args()
    {"init": cmd_init, "add-sprints": cmd_add_sprints}[args.mode](args)


if __name__ == "__main__":
    main()
