#!/usr/bin/env node
"use strict";

// Request one skeptical review after a material code change. Read-only work and
// Workbench/scratch artifacts stay unblocked. Malformed input fails open, and
// stop_hook_active limits the review to once per turn.

const fs = require("fs");
const path = require("path");

const EDIT_TOOLS = new Set(["edit", "multiedit", "notebookedit", "write"]);
const TERMINAL_REVIEW_MARKER = "DIAGNOSIS_PROPOSAL_REVIEW_V2";
const REVIEW =
  "Before finishing, challenge the implementation once as a skeptical reviewer. " +
  "Re-read the request and inspect the final diff. Check the affected public contract, callers, " +
  "boundary and failure cases, unintended files, weakened tests, silent fallbacks, and error-path regressions. " +
  "Run the narrowest meaningful verification, inspect its actual output, fix any discovered gap, " +
  "then report only claims supported by the evidence.";

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

function latestHumanRequestIndex(entries) {
  let latest = -1;
  entries.forEach((entry, index) => {
    if (isHumanRequest(entry)) latest = index;
  });
  return latest;
}

function isNonSourceArtifact(filePath, cwd) {
  if (typeof filePath !== "string" || filePath.length === 0) return false;
  const normalized = filePath.replace(/\\/g, "/").toLowerCase();
  if (
    normalized.startsWith(".workbench/") ||
    normalized.includes("/.workbench/") ||
    normalized.startsWith(".scratch/") ||
    normalized.includes("/.scratch/")
  ) return true;

  // Agents commonly place one-off probes and command output under <cwd>/tmp.
  // Those files support an investigation; they are not product-source edits.
  if (typeof cwd !== "string" || cwd.length === 0) return false;
  try {
    const resolved = path.resolve(cwd, filePath);
    const tempRoot = path.resolve(cwd, "tmp");
    return resolved === tempRoot || resolved.startsWith(tempRoot + path.sep);
  } catch (_) {
    return false;
  }
}

function hasMaterialEdit(entries, start, cwd) {
  for (const entry of entries.slice(start)) {
    if (entry.type !== "assistant") continue;
    const content = entry.message && entry.message.content;
    if (!Array.isArray(content)) continue;
    for (const item of content) {
      if (!item || typeof item !== "object" || item.type !== "tool_use") continue;
      const tool = String(item.name || "").split(".").pop().toLowerCase();
      if (!EDIT_TOOLS.has(tool)) continue;
      const input = item.input && typeof item.input === "object" ? item.input : {};
      const filePath = input.file_path || input.path || input.notebook_path;
      if (!isNonSourceArtifact(filePath, cwd)) return true;
    }
  }
  return false;
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
    const entries = readEntries(payload.transcript_path);
    const start = latestHumanRequestIndex(entries) + 1;
    if (entries.slice(start).some((entry) => JSON.stringify(entry).includes(TERMINAL_REVIEW_MARKER))) return;
    if (!hasMaterialEdit(entries, start, payload.cwd) && !isTaskWorkspace(payload.cwd)) return;
    process.stdout.write(JSON.stringify({ decision: "block", reason: REVIEW }));
  } catch (_) {
    // A guard that cannot understand its own input must not prevent completion.
  }
});
