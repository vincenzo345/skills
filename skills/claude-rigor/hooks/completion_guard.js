#!/usr/bin/env node
"use strict";

// Request one skeptical completion review after Claude edits code. Malformed
// input fails open, and stop_hook_active limits the review to once per turn.

const fs = require("fs");
const path = require("path");

const EDIT_TOOLS = new Set(["edit", "multiedit", "notebookedit", "write"]);
const REVIEW =
  "Before finishing, challenge the implementation once as a skeptical reviewer. " +
  "Re-read the request and inspect the final changes. Build explicit input partitions " +
  "for valid, boundary, malformed, wrong-type, and failure cases; compare every partition " +
  "with the required public contract and existing behavior. Resolve any stated judgment calls " +
  "from repository evidence instead of narrowing the contract or asking the user. Check for " +
  "missed callers, unintended files, weakened tests, silent fallbacks, and error-path regressions. " +
  "Run the narrowest meaningful verification available, fix any discovered gap, then report only " +
  "claims supported by executed evidence.";

function readEntries(value) {
  if (typeof value !== "string" || value.length === 0) return [];
  try {
    return fs
      .readFileSync(value, "utf8")
      .split(/\r?\n/)
      .filter((line) => line.trim())
      .map((line) => JSON.parse(line))
      .filter((item) => item && typeof item === "object" && !Array.isArray(item));
  } catch (_) {
    return [];
  }
}

function isHumanRequest(entry) {
  if (entry.type !== "user" || entry.isMeta) return false;
  const content = entry.message && entry.message.content;
  return !(
    Array.isArray(content) &&
    content.some((item) => item && typeof item === "object" && item.type === "tool_result")
  );
}

function editedSinceLatestRequest(entries) {
  let start = 0;
  entries.forEach((entry, index) => {
    if (isHumanRequest(entry)) start = index + 1;
  });
  return entries.slice(start).some((entry) => {
    if (entry.type !== "assistant") return false;
    const content = entry.message && entry.message.content;
    if (!Array.isArray(content)) return false;
    return content.some((item) => {
      if (!item || typeof item !== "object" || item.type !== "tool_use") return false;
      const tool = String(item.name || "").split(".").pop().toLowerCase();
      return EDIT_TOOLS.has(tool);
    });
  });
}

function isTaskWorkspace(value) {
  if (typeof value !== "string" || value.length === 0) return false;
  try {
    return fs.statSync(path.join(value, "TASK.md")).isFile();
  } catch (_) {
    return false;
  }
}

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
  input += chunk;
});
process.stdin.on("end", () => {
  try {
    const payload = JSON.parse(input);
    if (!payload || typeof payload !== "object" || payload.hook_event_name !== "Stop") return;
    if (payload.stop_hook_active === true) return;
    const edited = editedSinceLatestRequest(readEntries(payload.transcript_path));
    if (!edited && !isTaskWorkspace(payload.cwd)) return;
    process.stdout.write(JSON.stringify({ decision: "block", reason: REVIEW }));
  } catch (_) {
    // Hooks must not prevent completion when their own input is malformed.
  }
});
