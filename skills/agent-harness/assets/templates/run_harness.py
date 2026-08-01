#!/usr/bin/env python3
"""
Long-running build harness — headless driver (project-agnostic).

Spawns EACH role as a separate `claude -p` (Claude Code headless) invocation, so every role
gets its own fresh context window and they coordinate only through files in .harness/ —
the separate-context, adversarial-pressure pattern. It is deliberately simple; read it and
tune the caps / prompts to taste.

Prereqs:
  - Claude Code CLI on PATH (`claude`). Verify flags with `claude --help`.
  - Run from the PROJECT ROOT (the dir with CLAUDE.md), not from orchestrator/.
  - ci/build.sh and ci/test.sh wired to your stack (the skill generated thin wrappers).

Usage (on Windows use `python` — `python3` is usually not on PATH there):
  python3 orchestrator/run_harness.py                # current sprint -> done
  python3 orchestrator/run_harness.py --start 5      # jump to sprint 5
  python3 orchestrator/run_harness.py --only 3       # run just sprint 3, then stop
  python3 orchestrator/run_harness.py --replan       # regenerate plan.json first
  python3 orchestrator/run_harness.py --dry-run      # print the calls, spend nothing
"""
import argparse, json, subprocess, sys, datetime, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
H = ROOT / ".harness"
AGENTS = ROOT / ".claude" / "agents"

MAX_CONTRACT_ROUNDS = 4
MAX_BUILD_ROUNDS = 8
AGENT_TIMEOUT_S = 2 * 60 * 60  # kill a hung `claude -p` call rather than hang the loop forever

def now(): return datetime.datetime.now().isoformat(timespec="seconds")

def load(p, default=None):
    p = H / p
    if not p.exists(): return default
    txt = p.read_text(encoding="utf-8")
    return json.loads(txt) if p.suffix == ".json" else txt

def save_json(name, obj):
    (H / name).write_text(json.dumps(obj, indent=2), encoding="utf-8")

def journal(**kw):
    kw.setdefault("ts", now())
    with (H / "journal.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(kw) + "\n")

def role_prompt(role):
    """Same prompt whether run interactively (subagents) or headless (here)."""
    body = (AGENTS / f"{role}.md").read_text(encoding="utf-8")
    return re.sub(r"^---.*?---\s*", "", body, count=1, flags=re.S).strip()  # strip frontmatter

def role_model(role):
    """Honor each agent's `model:` frontmatter in headless mode too."""
    body = (AGENTS / f"{role}.md").read_text(encoding="utf-8")
    m = re.search(r"^model:\s*(\S+)", body, flags=re.M)
    return m.group(1) if m else None

def run_agent(role, task, dry=False):
    cmd = [
        "claude", "-p", task,
        "--append-system-prompt", role_prompt(role),
        "--permission-mode", "acceptEdits",
        "--output-format", "json",
    ]
    model = role_model(role)
    if model:
        cmd += ["--model", model]
    if dry:
        print(f"\n[DRY] {role} ({model or 'default model'}): {task}\n"
              f"  $ claude -p ... --append-system-prompt <{role}.md>")
        return ""
    print(f"\n=== {role} :: {task[:70]} ===")

    def attempt_once():
        try:
            return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                                  timeout=AGENT_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            print(f"{role} timed out after {AGENT_TIMEOUT_S}s")
            return None

    # One transient API/CLI error should not kill an hours-long unattended run: retry once.
    res = attempt_once()
    if res is None or res.returncode != 0:
        if res is not None:
            print(f"claude CLI error (exit {res.returncode}):")
            print("stderr:", res.stderr[-2000:] or "<empty>")
            print("stdout tail:", res.stdout[-1000:] or "<empty>")
        print("retrying once with a fresh session...")
        res = attempt_once()
    if res is None:
        sys.exit(1)
    if res.returncode != 0:
        print(f"claude CLI failed twice (exit {res.returncode}):")
        print("stderr:", res.stderr[-2000:] or "<empty>")
        sys.exit(1)
    try:
        out = json.loads(res.stdout).get("result", res.stdout)
    except json.JSONDecodeError:
        out = res.stdout
    # Persist the transcript — "read the traces, tune the prompts" needs traces on disk.
    tdir = H / "traces"
    tdir.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    (tdir / f"{stamp}-{role}.md").write_text(f"# {role} :: {task}\n\n{out}\n", encoding="utf-8")
    return out

def git(*args):
    subprocess.run(["git", *args], cwd=ROOT, check=False)

def negotiate_contract(n, dry):
    for r in range(1, MAX_CONTRACT_ROUNDS + 1):
        run_agent("generator", f"Propose a contract for sprint {n}. Write .harness/contract.json.", dry)
        run_agent("evaluator", "Review the proposed contract. Write .harness/contract_review.json.", dry)
        if dry: return True
        review = load("contract_review.json", {})
        journal(sprint=n, role="orchestrator", round=r, action="contract-negotiation",
                verdict=("agreed" if review.get("agreed") else "revise"))
        if review.get("agreed"):
            return True
    print(f"Contract for sprint {n} did not converge in {MAX_CONTRACT_ROUNDS} rounds. Stopping for human review.")
    return False

def build_eval(n, dry):
    if not dry:  # --dry-run must not touch the repo
        git("tag", f"sprint-{n}-start")
    for r in range(1, MAX_BUILD_ROUNDS + 1):
        run_agent("generator", f"Build sprint {n} against the agreed contract. Run tests, commit when green.", dry)
        run_agent("evaluator", "Evaluate the current build. Write .harness/verdict.json.", dry)
        if dry: return True
        v = load("verdict.json", {})
        verdict, score = v.get("verdict"), v.get("weighted")
        journal(sprint=n, role="orchestrator", round=r, action="graded", verdict=verdict, weighted=score,
                note=(v.get("critique", "")[:200]))
        print(f"  sprint {n} round {r}: {verdict} (weighted {score})")
        if verdict == "pass":
            return True
        if verdict == "restart":
            print(f"  restart -> git reset --hard sprint-{n}-start")
            git("reset", "--hard", f"sprint-{n}-start")
    print(f"Sprint {n} hit the {MAX_BUILD_ROUNDS}-round cap without passing. Stopping for human review.")
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int)
    ap.add_argument("--only", type=int, help="run just this one sprint, then stop")
    ap.add_argument("--replan", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    dry = a.dry_run

    if a.replan or not (H / "plan.json").exists():
        run_agent("planner", "Produce .harness/plan.json for this project.", dry)

    plan = load("plan.json"); progress = load("progress.json")
    ids = [s["id"] for s in plan["sprints"]]
    start = a.start or next((i for i in ids if progress["sprints"].get(str(i)) != "passed"), None)
    if start is None:
        print("All sprints already passed. Nothing to do."); return

    targets = [a.only] if a.only else [i for i in ids if i >= start]
    for n in targets:
        if progress["sprints"].get(str(n)) == "passed":
            continue
        print(f"\n########## SPRINT {n} ##########")
        if not negotiate_contract(n, dry): break
        if not build_eval(n, dry): break
        if dry:
            print(f"[DRY] would mark sprint {n} passed (no state written)")
            continue
        progress["sprints"][str(n)] = "passed"; progress["current"] = n + 1
        save_json("progress.json", progress)
        git("commit", "-am", f"sprint {n}: passed")
        print(f"########## SPRINT {n} PASSED ##########")

    print("\nDone (or stopped). Read .harness/journal.jsonl for the trail.")

if __name__ == "__main__":
    main()
