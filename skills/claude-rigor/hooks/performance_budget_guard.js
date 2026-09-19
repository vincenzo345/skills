#!/usr/bin/env node
"use strict";

// Convert Workbench's performance-investigation tool budget into a backstop.
// Once evidence collection reaches the bound, preserve artifact/handoff tools
// but stop another round of repository discovery.

const fs = require("fs");
const LIMIT = 30;
const PERFORMANCE = /\b(?:slow|slowness|latency|performance|regression)\b/i;
const WORKBENCH = /(?:^|[\s/])workbench\b/i;
const DISCOVERY = new Set(["bash", "read", "grep", "glob", "webfetch", "websearch"]);
const LIFECYCLE = /prepare-(?:routing|handoff)\.py|workbench\.py/i;

function entries(path) {
  try {
    return fs.readFileSync(path, "utf8").split(/\r?\n/).filter(Boolean).map(JSON.parse);
  } catch (_) { return []; }
}

function text(value) {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(text).join("\n");
  if (value && typeof value === "object") return Object.values(value).map(text).join("\n");
  return "";
}

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => { input += chunk; });
process.stdin.on("end", () => {
  try {
    const payload = JSON.parse(input);
    if (!payload || payload.hook_event_name !== "PreToolUse") return;
    const history = entries(payload.transcript_path);
    let requestIndex = -1;
    let request = "";
    for (let index = history.length - 1; index >= 0; index -= 1) {
      const item = history[index];
      if (item.type !== "user" || item.isMeta) continue;
      const content = item.message && item.message.content;
      if (Array.isArray(content) && content.some((part) => part && part.type === "tool_result")) continue;
      requestIndex = index;
      request = text(content);
      break;
    }
    if (requestIndex < 0 || !WORKBENCH.test(request) || !PERFORMANCE.test(request)) return;
    let calls = 0;
    for (const item of history.slice(requestIndex + 1)) {
      if (item.type !== "assistant") continue;
      for (const part of ((item.message || {}).content || [])) {
        if (part && part.type === "tool_use") calls += 1;
      }
    }
    if (calls < LIMIT) return;
    const tool = String(payload.tool_name || "").split(".").pop().toLowerCase();
    const toolInput = text(payload.tool_input || {});
    if (!DISCOVERY.has(tool) || LIFECYCLE.test(toolInput)) return;
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason:
          `PERFORMANCE_EVIDENCE_BUDGET_V1: ${LIMIT} tool calls have already been made for this bounded Workbench performance investigation. ` +
          "Stop repository discovery. Synthesize the existing evidence, write/review the proposal, and use the documented handoff helper. " +
          "Record any unresolved premise as proof-needed instead of running another search.",
      },
    }));
  } catch (_) {
    // Malformed input fails open.
  }
});
