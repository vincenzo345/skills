#!/usr/bin/env node
"use strict";

// Put explicit Workbench routing in context before Claude chooses its first
// tool. The PreToolUse guard remains a backstop, not the primary teacher.

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => { input += chunk; });
process.stdin.on("end", () => {
  try {
    const payload = JSON.parse(input);
    if (!payload || payload.hook_event_name !== "UserPromptSubmit") return;
    const prompt = String(payload.prompt || payload.user_prompt || "");
    const workbench = /(?:^|[\s/])workbench\b/i.test(prompt);
    const startNew = /(?:\b(?:start|create)\s+(?:a\s+)?new\b|\bignore\b[^.\n]{0,100}\bactive\s+work)/i.test(prompt);
    if (!workbench || !startNew) return;
    const performance = /\b(?:slow|slowness|latency|performance|regression)\b/i.test(prompt);
    const performanceContext = performance
      ? " This is a bounded performance investigation. Begin the first substantive update with Environment, Deployed revision, Journey, Fixture, and Cache state before any ranking. " +
        "Use one batched pass over the end-to-end seam and at most one decision-changing benchmark; inspect each target once and stop when another check cannot change the conditional order. " +
        "Source topology, absent configuration, library internals, sequential or concurrent calls, and cache-writer searches do not prove the deployed network path, execution-environment reuse, CPU boundedness, cache emptiness, or a dominant option. " +
        "Separate independent mechanisms. Before terminal handoff, compare every option against the same user-visible milestone and branch; reject any statement that makes an option both inert and helpful in the same branch, or calls an option largest, only, guaranteed, excluded, or counterproductive without a discriminating measurement. " +
        "Preserve source-versus-deployed qualifiers in the final. Batch independent searches and adjacent reads."
      : "";
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "UserPromptSubmit",
        additionalContext:
          "WORKBENCH_START_NEW_ROUTER_V1: This request explicitly invokes Workbench and requires a new item. " +
          "Your first tool call must be Skill(workbench). Do not inspect the repository or old Workbench state first. " +
          "After loading it, create the compact routing input and call prepare-routing.py --capture-and-start exactly as documented." +
          performanceContext,
      },
    }));
  } catch (_) {
    // Malformed input fails open.
  }
});
